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

import wx # use wx to build the UI.
import time
import socket
import sys
import time
import platform  

import telloGlobal as gv

IN_CMD_LIST = ['command', 'takeoff', 'land', 'streamon', 'streamoff']
YA_CMD_LIST = ['up', 'down', 'cw', 'ccw']
XA_CMD_LIST = ['forward', 'back', 'left', 'right']

PERIODIC = 10 # periodicly call by 300ms
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
        wx.Panel.__init__(self, parent,  size=(400, 300))
        self.SetSize((400, 300))
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.lastPeriodicTime = time.time()
        #self.bmp = wx.BitmapFromBuffer(width, height, frame)
        self.bmp = wx.Bitmap(400, 300)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.SetDoubleBuffered(True)

    def onPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawRectangle(0, 0, 400, 300)
        dc.DrawBitmap(self.bmp, 0, 0)


    def periodic(self , now):
        if now - self.lastPeriodicTime >= 0.5:
            self.updateDisplay()


    def updateCvFrame(self, cvFrame):
        self.bmp = wx.BitmapFromBuffer(400, 300, cvFrame)

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
        wx.Frame.__init__(self, parent, id, title, size= (500, 700))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))

        host = ''
        port = 9000
        locaddr = (host,port)
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

        
    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.VERTICAL)
        
        self.camPanel = ShowCapture(self)
        hsizer.Add(self.camPanel, flag=flagsR, border=2)

        bhox1 = wx.BoxSizer(wx.HORIZONTAL)
        for item in IN_CMD_LIST:
            outputBt = wx.Button(self, label=item, size=(80, 40))
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            bhox1.Add(outputBt, flag=flagsR, border=2)
        hsizer.Add(bhox1, flag=flagsR, border=2)

        bhox2 = wx.BoxSizer(wx.HORIZONTAL)
        for item in YA_CMD_LIST:
            outputBt = wx.Button(self, label=item, size=(80, 40))
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            bhox2.Add(outputBt, flag=flagsR, border=2)
        hsizer.Add(bhox2, flag=flagsR, border=2)


        bhox3 = wx.BoxSizer(wx.HORIZONTAL)
        for item in XA_CMD_LIST:
            outputBt = wx.Button(self, label=item, size=(80, 40))
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            bhox3.Add(outputBt, flag=flagsR, border=2)
        hsizer.Add(bhox3, flag=flagsR, border=2)
        return hsizer

    def onButton(self, event):
        msg = event.GetEventObject().GetLabel()
        if not msg in IN_CMD_LIST:
            msg = msg +" 30"
        print(msg)
        self.sendMsg(msg)
        data = self.recvMsg() if msg in IN_CMD_LIST else ''
        if data== 'ok' and msg == 'streamon':
            addr = 'udp://' + LOCAL_IP + ':' + str(LOCAL_PORT_VIDEO)
            self.capture = cv2.VideoCapture(addr)
        if data== 'ok' and msg == 'streamoff':
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
        if self.capture is not None and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.camPanel.updateCvFrame(frame)

        now = time.time()
        self.camPanel.periodic(now)
        if now - self.lastPeriodicTime >= 3:
            self.sendMsg('speed?')
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