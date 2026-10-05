import logging
import shutil
import subprocess
import sys
import threading

import pyttsx3
import speech_recognition as sr
import wx

import config
from assistant import request_database, request_handle
from database import SEARCH_LIMIT
from display import format_date, shorten

logger = logging.getLogger(__name__)

NO_ANSWER = "Sorry, I could not find an answer."


class Speaker:
    """Text to speech. On macOS the built-in `say` command runs in its own process, so it does not block."""

    def __init__(self):
        self._process = None
        self._engine = None
        if sys.platform != "darwin" or not shutil.which("say"):
            self._engine = pyttsx3.init()

    def say(self, text):
        if self._engine is not None:
            # pyttsx3 is not reliable outside the main thread, so this blocks while speaking
            self._engine.say(text)
            self._engine.runAndWait()
            return
        self.stop()
        # Pass the text on stdin, so it can never be read as a command line option
        self._process = subprocess.Popen(["say"], stdin=subprocess.PIPE)
        self._process.stdin.write(text.encode("utf-8"))
        self._process.stdin.close()

    def stop(self):
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=wx.Size(600, 680), title="PyAi")
        self.SetMinSize(wx.Size(450, 500))
        self.busy = False
        self.search_items = []
        self.recognizer = sr.Recognizer()
        self.speaker = Speaker()

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(panel, label='Hello I am your digital assistant! How can I help you'),
                  0, wx.ALL, 5)
        ask_row = wx.BoxSizer(wx.HORIZONTAL)
        self.txt = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.ask_btn = wx.Button(panel, label='Ask')
        self.mic_btn = wx.Button(panel, label='Speak')
        ask_row.Add(self.txt, 1, wx.EXPAND | wx.RIGHT, 5)
        ask_row.Add(self.ask_btn, 0, wx.RIGHT, 5)
        ask_row.Add(self.mic_btn, 0)
        sizer.Add(ask_row, 0, wx.EXPAND | wx.ALL, 5)
        self.status = wx.StaticText(panel, label='')
        sizer.Add(self.status, 0, wx.ALL, 5)
        self.answer_txt = wx.TextCtrl(panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add(self.answer_txt, 1, wx.EXPAND | wx.ALL, 5)

        sizer.Add(wx.StaticText(panel, label='What are you finding?'), 0, wx.ALL, 5)
        self.txt2 = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.txt2, 0, wx.EXPAND | wx.ALL, 5)
        self.results = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.results.InsertColumn(0, 'Date', width=130)
        self.results.InsertColumn(1, 'Question', width=180)
        self.results.InsertColumn(2, 'Answer', width=260)
        sizer.Add(self.results, 2, wx.EXPAND | wx.ALL, 5)
        self.detail_txt = wx.TextCtrl(panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add(self.detail_txt, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)

        self.txt.Bind(wx.EVT_TEXT_ENTER, self.on_ask)
        self.ask_btn.Bind(wx.EVT_BUTTON, self.on_ask)
        self.mic_btn.Bind(wx.EVT_BUTTON, self.on_mic)
        self.txt2.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        self.results.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_result_selected)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.txt.SetFocus()
        self.Show()

    # Network and microphone calls run in worker threads so the window does not freeze.
    # Widgets may only be touched from the GUI thread, hence wx.CallAfter.

    @staticmethod
    def _run_in_background(target, *args):
        threading.Thread(target=target, args=args, daemon=True).start()

    def on_ask(self, event):
        question = self.txt.GetValue().strip()
        if not question or self.busy:
            return
        self.speaker.stop()
        self.set_busy(True, 'Searching...')
        self._run_in_background(self._ask_worker, question)

    def on_mic(self, event):
        if self.busy:
            return
        self.speaker.stop()
        self.set_busy(True, 'Listening...')
        self._run_in_background(self._voice_worker)

    def _voice_worker(self):
        question = self._listen()
        if not question:
            wx.CallAfter(self._show_message, 'I could not understand you.')
            return
        wx.CallAfter(self.txt.SetValue, question)
        wx.CallAfter(self.status.SetLabel, 'Searching...')
        self._ask_worker(question)

    def _ask_worker(self, question):
        answer = request_handle(question.lower())
        wx.CallAfter(self._show_answer, question, answer)

    def _listen(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return self.recognizer.recognize_google(audio, language=config.SPEECH_LANG)
        except sr.WaitTimeoutError:
            logger.info("No speech detected")
        except sr.UnknownValueError:
            logger.info("Google speech recognition could not understand audio")
        except sr.RequestError as e:
            logger.error("Could not request results from Google speech recognition service: %s", e)
        except OSError as e:
            logger.error("Microphone is not available: %s", e)
        return None

    def _show_message(self, text):
        self.set_busy(False)
        self.answer_txt.SetValue(text)

    def _show_answer(self, question, answer):
        self.set_busy(False)
        if answer is None:
            self.answer_txt.SetValue(NO_ANSWER)
            self.speaker.say(NO_ANSWER)
            return
        self.answer_txt.SetValue(answer)
        self.speaker.say(f"The question is: {question}. The answer is: {answer}")

    def set_busy(self, busy, status=''):
        self.busy = busy
        for widget in (self.txt, self.ask_btn, self.mic_btn):
            widget.Enable(not busy)
        self.status.SetLabel(status)
        if not busy:
            self.txt.SetFocus()

    def on_search(self, event):
        text = self.txt2.GetValue().strip()
        if not text:
            return
        self.search_items = []
        self.results.DeleteAllItems()
        self.detail_txt.SetValue('Searching...')
        self._run_in_background(self._search_worker, text)

    def _search_worker(self, text):
        try:
            items = request_database('find', text)
        except Exception:
            logger.exception("Database search failed")
            wx.CallAfter(self.detail_txt.SetValue, 'Database search failed, see the log.')
            return
        wx.CallAfter(self._show_results, items)

    def _show_results(self, items):
        self.search_items = items
        self.results.DeleteAllItems()
        for row, item in enumerate(items):
            self.results.InsertItem(row, format_date(item.get('date')))
            self.results.SetItem(row, 1, shorten(item.get('request', ''), 40))
            self.results.SetItem(row, 2, shorten(item.get('response', ''), 60))
        if not items:
            message = 'No matching items.'
        elif len(items) >= SEARCH_LIMIT:
            message = f'Showing the newest {SEARCH_LIMIT} items. Select one to see the details.'
        else:
            message = f'{len(items)} item(s) found. Select one to see the details.'
        self.detail_txt.SetValue(message)

    def on_result_selected(self, event):
        item = self.search_items[event.GetIndex()]
        self.detail_txt.SetValue(
            f"{format_date(item.get('date'))}\n\n"
            f"Q: {item.get('request', '')}\n\n"
            f"A: {item.get('response', '')}"
        )

    def on_close(self, event):
        self.speaker.stop()
        event.Skip()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
