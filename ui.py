import wx
from requestPage import requestHandle, requestDatabase
import speech_recognition as sr
import pyttsx3

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,
        pos=wx.DefaultPosition,size=wx.Size(450,400),
        style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |
        wx.CLOSE_BOX | wx.CLIP_CHILDREN,
        title="PyAi")
        panel=wx.Panel(self)
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(panel,
        label='Hello I am your digital assistant! How can I help you')
        my_sizer.Add(lbl,0,wx.ALL,5)
        self.txt = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(400,30))
        self.txt.SetFocus()
        self.txt.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        my_sizer.Add(self.txt,0,wx.ALL,5)
        lbl2 = wx.StaticText(panel,
        label='What are you finding?')
        my_sizer.Add(lbl2,0,wx.ALL,5)
        self.txt2 = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(400,30))
        my_sizer.Add(self.txt2,0,wx.ALL,5)
        self.txt2.Bind(wx.EVT_TEXT_ENTER, self.OnEnterSearch)
        self.txt3 = wx.TextCtrl(panel, style=wx.TE_READONLY | wx.TE_MULTILINE, size=(400,90))
        my_sizer.Add(self.txt3,0,wx.ALL,5)
        panel.SetSizer(my_sizer)
        self.Show()

    def OnEnter(self, event):
        input = self.txt.GetValue()
        input = input.lower()
        if input == '':
            r = sr.Recognizer()
            with sr.Microphone as source:
                audio = r.listen(source)
            try:
                self.txt.SetValue(r.recognize_google(audio))
            except sr.UnknownValueError:
                print("Google speech recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results for Google speech recognition service: ".format(e))
        engine = pyttsx3.init()
        engine.say('The question is: '.input)
        engine.runAndWait()
        if len(input) > 0:
            answer = requestHandle(input)
            engine.say('The answer is: '.answer)

    def OnEnterSearch(self, event):
        input = self.txt2.GetValue()
        result = requestDatabase('find',input)
        itemsInArray = len(result)-1
        resultText = ''
        for x in range(0, itemsInArray):
            if x == 0:
                resultText += '-----START ITEMS-----\n'
            resultText += result[x]['_id'] + '\n'
            resultText += result[x]['date'] + '\n'
            resultText += result[x]['request'] + '\n'
            resultText += result[x]['response'] + '\n'
            resultText += '\n-----NEW ITEM-----\n'
        self.txt3.SetValue(resultText)

if __name__ == '__main__':
    app=wx.App(True)
    frame = MyFrame()
    app.MainLoop()
