#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        TelloRun.py
#
# Purpose:     This function is used to create a controller to control the DJI 
#              Tello Drone and connect to the height sensor.
#
# Author:      Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import sys
import time
import socket
import platform
import queue as queue

import wx  # use wx to build the UI.
import cv2
import telloGlobal as gv
import telloPanel as tp
import telloSensor as ts

KEY_CODE = {
    '87': 'up',     # Key 'w'
    '83': 'down',   # key 's'
    '65': 'cw',     # key 'a'
    '68': 'ccw',    # key 'd'
    '315': 'forward', # key 'up'
    '314': 'left',  # key 'left'
    '316': 'right', # key 'right'
    '317': 'back'   # key 'back'
}

PERIODIC = 10  # periodicly call by 10ms

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloFrame(wx.Frame):
    """ DJI tello drone system control hub."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(510, 720))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        self.capture = None         # Video capture.
        self.connectFlag = False    # connection flag. 
        self.cmdQueue = queue.Queue(maxsize=10)
        # Init the UDP server.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(gv.FB_IP)
        # Init the UI.
        self.SetSizer(self._buidUISizer())
        # Tcp server to connect to the sensor.
        gv.iSensorChecker = self.thread1 = ts.telloSensor(1, "Thread-1", 1)
        self.thread1.start()
        # Set the periodic feedback:
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 300 ms
        # Set the key sense event
        self.Bind(wx.EVT_KEY_DOWN, self.keyDown)
        # Add Close event here. 
        self.Bind(wx.EVT_CLOSE, self.OnClose)

#-----------------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI sizer of the frame."""
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        flagsC = wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.VERTICAL)
        mSizer.AddSpacer(5)
        # Row Idx = 0 : Statue diaplay
        mSizer.Add(self._buildStateSizer(), flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # Row Idx = 1 : Camera display
        self.camPanel = tp.PanelCam(self)
        mSizer.Add(self.camPanel, flag=flagsC, border=2)
        mSizer.AddSpacer(5)
        # Row Idx = 2: Drone Control part
        bhox1 = wx.BoxSizer(wx.HORIZONTAL)
        bhox1.AddSpacer(20)
        bhox1.Add(wx.StaticText(
            self, label="Vertical Motion Ctrl".ljust(40)), flag=flagsC, border=2)
        bhox1.Add(wx.StaticText(
            self, label="Takeoff and Cam Ctrl".ljust(40)), flag=flagsC, border=2)
        bhox1.Add(wx.StaticText(
            self, label="Horizontal Motion Ctrl".ljust(40)), flag=flagsC, border=2)
        mSizer.Add(bhox1, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        bhox2 = self._buildCtrlSizer()
        mSizer.Add(bhox2, flag=flagsR, border=2)
        # Split line
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # Row Idx = 3 : Track edition and control.
        gv.iTrackPanel = self.trackPanel = tp.TrackCtrlPanel(self)
        mSizer.Add(self.trackPanel, flag=flagsC, border=2)
        # Split line
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # Row Idx =4 : sensor control
        gv.iSensorPanel = self.sensorPanel = tp.SensorCtrlPanel(self)
        mSizer.Add(self.sensorPanel, flag=flagsC, border=2)
        return mSizer

#-----------------------------------------------------------------------------
    def _buildCtrlSizer(self):
        """ Build the Drone control sizer"""
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        mSizer.AddSpacer(10)
        # Vertical movement control
        gs1 = wx.GridSizer(2, 3, 5, 5)
        for k, item in enumerate(gv.YA_CMD_LIST):
            bmp0 = wx.Bitmap(gv.YA_PNG_LIST[k], wx.BITMAP_TYPE_ANY)
            outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0, size=(
                bmp0.GetWidth()+6, bmp0.GetHeight()+6), name=item)
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs1.Add(outputBt, flag=flagsR, border=2)
        mSizer.Add(gs1, flag=flagsR, border=2)
        # Split line
        mSizer.AddSpacer(15)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 100),
                                 style=wx.LI_VERTICAL), flag=flagsR, border=2)
        mSizer.AddSpacer(15)
        # take off and camera control
        gs2 = wx.GridSizer(2, 2, 5, 5)
        for k, item in enumerate(gv.IN_CMD_LIST):
            bmp0 = wx.Bitmap(gv.IN_PNG_LIST[k], wx.BITMAP_TYPE_ANY)
            outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0, size=(
                bmp0.GetWidth()+6, bmp0.GetHeight()+6), name=item)
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs2.Add(outputBt, flag=flagsR, border=2)
        mSizer.Add(gs2, flag=flagsR, border=2)
        # Split line
        mSizer.AddSpacer(15)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 100),
                                 style=wx.LI_VERTICAL), flag=flagsR, border=2)
        mSizer.AddSpacer(15)
        # Horizontal movement control
        gs3 = wx.GridSizer(2, 3, 5, 5)
        for k, item in enumerate(gv.XA_CMD_LIST):
            bmp0 = wx.Bitmap(gv.XA_PNG_LIST[k], wx.BITMAP_TYPE_ANY)
            outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0, size=(
                bmp0.GetWidth()+6, bmp0.GetHeight()+6), name=item)
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs3.Add(outputBt, flag=flagsR, border=2)
        mSizer.Add(gs3, flag=flagsR, border=2)
        return mSizer

#-----------------------------------------------------------------------------
    def _buildStateSizer(self):
        """ Build the UAV + sensor state display."""
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        mSizer.AddSpacer(5)
        self.connectBt = wx.Button(self, label='UAV_Connect', size=(90, 20))
        self.connectBt.Bind(wx.EVT_BUTTON, self.onConnect)
        mSizer.Add(self.connectBt, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.connectLbD = wx.StaticText(self, label=" UAV_Offline".ljust(15))
        self.connectLbD.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.connectLbD, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.batteryLbD = wx.StaticText(
            self, label=" UAV_Battery:[0%]".ljust(20))
        self.batteryLbD.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.batteryLbD, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.connectLbS = wx.StaticText(self, label=" SEN_Offline".ljust(15))
        self.connectLbS.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.connectLbS, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.batteryLbS = wx.StaticText(
            self, label=" SEN_Battery:[100%]".ljust(20))
        self.batteryLbS.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.batteryLbS, flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        return mSizer

#-----------------------------------------------------------------------------
    def keyDown(self, event):
        print("OnKeyDown event %s" % (event.GetKeyCode()))
        msg = KEY_CODE[str(event.GetKeyCode())]
        print(msg)
        self.queueCmd(msg)

#-----------------------------------------------------------------------------
    def onButton(self, event):
        cmd = event.GetEventObject().GetName()
        print("Add message %s in the cmd Q." % cmd)
        if not cmd in gv.IN_CMD_LIST:
            cmd = cmd + " 30"
        self.queueCmd(cmd)

#-----------------------------------------------------------------------------
    def onConnect(self, event):
        """ Try to connect the drone and control uder SDK cmd mode.
        """
        self.sendMsg('command')
        if self.recvMsg() == 'ok':
            self.connectLbD.SetLabel("UAV_Online".ljust(15))
            self.connectLbD.SetBackgroundColour(wx.Colour('GREEN'))
            self.connectFlag = True

#-----------------------------------------------------------------------------
    def periodic(self, event):
        """ periodic capture the image from camera:
        """
        # update the video
        now = time.time()
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret: 
                self.camPanel.updateCvFrame(frame)
                self.camPanel.periodic(now)
        # Update the active cmd
        if self.connectFlag and now - self.lastPeriodicTime >= 5:
            cmd = gv.iTrackPanel.getAction()
            if not cmd: cmd = 'command'
            self.queueCmd(cmd)
            self.lastPeriodicTime =  now
        
        # check the cmd send
        if not self.cmdQueue.empty():
            msg = self.cmdQueue.get()
            print(msg)
            self.sendMsg(msg)
            data = self.recvMsg() if msg in ['streamon', 'streamoff'] else ''
            if msg == 'streamon' and data == 'ok':
                ip, port = gv.VD_IP
                addr = 'udp://%s:%s' % (str(ip), str(port))
                self.capture = cv2.VideoCapture(addr)
            elif msg == 'streamoff' or data == 'error':
                if self.capture: self.capture.release()
                self.capture = None

#-----------------------------------------------------------------------------
    def queueCmd(self, cmd):
        """ Add the cmd in the cmd Queue."""
        if self.cmdQueue.full():
            print("cmd Queue is full")
            return
        self.cmdQueue.put(cmd)

#-----------------------------------------------------------------------------
    def recvMsg(self):
        """ Receive the feed back message from the drone."""
        data, _ = self.sock.recvfrom(1518)
        return data.decode(encoding="utf-8")

#-----------------------------------------------------------------------------
    def sendMsg(self, msg):
        """ Send the control cmd to the drone directly."""
        self.sock.sendto(msg.encode(encoding="utf-8"), gv.CT_IP)

    #-----------------------------------------------------------------------------
    def OnClose(self, event):
        #self.ser.close()
        self.thread1.stop()
        self.Destroy()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        mainFrame = telloFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
