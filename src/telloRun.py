#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railwayHub.py
#
# Purpose:     This function is used to create a rail control hub to show the 
#              different situation of the cyber-security attack's influence for
#              the railway HMI and PLC system.
#
# Author:      Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import wx  # use wx to build the UI.
import time
import socket
import sys
import time
import platform
import cv2
import telloGlobal as gv

IN_CMD_LIST = ['command', 'takeoff', 'land', 'streamon', 'streamoff', ]
YA_CMD_LIST = ['flip l', 'up', 'flip r', 'cw', 'down',  'ccw']
XA_CMD_LIST = ['', 'forward', '', 'left', 'back',  'right']

KEY_CODE = {
    '87': 'up',     # Key 'w'
    '83': 'down',   # key 's'
    '65': 'cw',     # key 'a'
    '68': 'ccw',    # key 'd'
    '315': 'forward', # key 'up'
    '314': 'left',  # key 'left'
    '316': 'right',  # key 'right'
    '317': 'back'   # key 'back'
}

PERIODIC = 10  # periodicly call by 300ms
LOCAL_IP = '192.168.10.2'
LOCAL_PORT_VIDEO = '11111'


class PanelPlaceHolder(wx.Panel):
    """ Place Holder Panel"""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(400, 300))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        wx.StaticText(self, -1, "Place Holder:", (20, 20))


class ShowCapture(wx.Panel):
    """ Image display panel.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent,  size=(480, 360))
        self.SetSize((400, 300))
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.lastPeriodicTime = time.time()
        #self.bmp = wx.BitmapFromBuffer(width, height, frame)
        self.bmp = wx.Bitmap(480, 360)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.SetDoubleBuffered(True)

    def onPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawRectangle(0, 0, 480, 360)
        dc.DrawBitmap(self.bmp, 0, 0)
        dc.SetPen(wx.Pen('GREEN', width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(240, 0, 240, 180)
        dc.DrawLine(0, 180, 480, 180)
        dc.DrawLine(220, 200, 260, 200)
        dc.DrawLine(225, 220, 255, 220)
        dc.DrawLine(230, 240, 250, 240)


    def scale_bitmap(self, bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

    def periodic(self, now):
        if now - self.lastPeriodicTime >= 0.5:
            self.updateDisplay()

    def updateCvFrame(self, cvFrame):
        #print(cvFrame.shape[:2])
        frame = cv2.cvtColor(cvFrame, cv2.COLOR_BGR2RGB)
        #frame = cv2.cvtColor(cvFrame, cv2.COLOR_BGR2RGB)
        #self.bmp.CopyFromBuffer(frame)
        self.bmp = self.scale_bitmap(
            wx.BitmapFromBuffer(960, 720, frame), 480, 360)

    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(False)
        self.Update()


class telloFrame(wx.Frame):
    """ Railway system control hub."""

    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(500, 560))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))

        host = ''
        port = 9000
        locaddr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(locaddr)

        # Init the image capture part.

        self.capture = None

        self.SetSizer(self.buidUISizer())
        # Set the periodic feedback:
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 300 ms
        self.Bind(wx.EVT_KEY_DOWN, self.keyDown)


    def keyDown(self, event):
        print("OnKeyDown event %s" % (event.GetKeyCode()))
        msg = KEY_CODE[str(event.GetKeyCode())]
        if not msg in IN_CMD_LIST:
            msg = msg + " 30"
        print(msg)
        self.sendMsg(msg)

    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.VERTICAL)

        self.camPanel = ShowCapture(self)
        hsizer.Add(self.camPanel, flag=flagsR, border=2)
        hsizer.AddSpacer(10)

        bhox1 = wx.BoxSizer(wx.HORIZONTAL)
        for item in IN_CMD_LIST:
            outputBt = wx.Button(self, label=item, size=(90, 30))
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            bhox1.Add(outputBt, flag=flagsR, border=5)
        hsizer.Add(bhox1, flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        hsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(480, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        bhox2 = wx.BoxSizer(wx.HORIZONTAL)
        bhox2.AddSpacer(10)
        gs1 = wx.GridSizer(2, 3, 5, 5)
        for item in YA_CMD_LIST:
            outputBt = wx.Button(self, label=item, size=(50, 50))
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs1.Add(outputBt, flag=flagsR, border=2)
        bhox2.Add(gs1, flag=flagsR, border=2)

        bhox2.AddSpacer(120)

        gs2 = wx.GridSizer(2, 3, 5, 5)
        for item in XA_CMD_LIST:
            outputBt = wx.Button(self, label=item, size=(50, 50))
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs2.Add(outputBt, flag=flagsR, border=2)
        bhox2.Add(gs2, flag=flagsR, border=2)

        hsizer.Add(bhox2, flag=flagsR, border=2)
        return hsizer

    def onButton(self, event):
        msg = event.GetEventObject().GetLabel()
        if not msg in IN_CMD_LIST:
            msg = msg + " 30"
        print(msg)
        self.sendMsg(msg)
        data = self.recvMsg() if msg in IN_CMD_LIST else ''
        print(data)
        if data == 'ok' and msg == 'streamon':
            print('q')
            addr = 'udp://' + LOCAL_IP + ':' + str(LOCAL_PORT_VIDEO)
            self.capture = cv2.VideoCapture(addr)
        if data == 'ok' and msg == 'streamoff':
            self.capture.release()
            self.capture = None

    def sendMsg(self, msg):
        tello_address = ('192.168.10.1', 8889)
        self.sock.sendto(msg.encode(encoding="utf-8"), tello_address)

    def recvMsg(self):
        data, server = self.sock.recvfrom(1518)
        return data.decode(encoding="utf-8")

    def periodic(self, event):
        """ periodic capture the image from camera:
        """
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.camPanel.updateCvFrame(frame)

        now = time.time()
        self.camPanel.periodic(now)
        if now - self.lastPeriodicTime >= 3:
            self.sendMsg('command')
            #print('speed: %s' %speed)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        mainFrame = telloFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True


app = MyApp(0)
app.MainLoop()
