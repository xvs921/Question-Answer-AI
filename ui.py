import wx
from requestPage import requestHandle
import speech_recognition as sr
import pyttsx3

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,
        pos=wx.DefaultPosition,size=wx.Size(450,100),
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

if __name__ == '__main__':
    app=wx.App(True)
    frame = MyFrame()
    app.MainLoop()
