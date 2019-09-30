# from link: https://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython

import wx
import cv2
LOCAL_IP = '192.168.10.2'
LOCAL_PORT_VIDEO = '11111'


class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=25):
        wx.Panel.__init__(self, parent)

        self.capture = capture
        ret, frame = self.capture.read()

        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.BitmapFromBuffer(width, height, frame)

        self.timer = wx.Timer(self)
        self.timer.Start(15)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)
        self.SetDoubleBuffered(True)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            #if ret:
            #    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #    self.bmp.CopyFromBuffer(frame)
            #    self.Refresh()



addr = 'udp://' + LOCAL_IP + ':' + str(LOCAL_PORT_VIDEO)

#capture = cv2.VideoCapture(0)
capture = cv2.VideoCapture(addr)


#capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
#capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

app = wx.App()
frame = wx.Frame(None)
cap = ShowCapture(frame, capture)
frame.Show()
app.MainLoop()