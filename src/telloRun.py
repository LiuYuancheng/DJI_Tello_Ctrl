#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        TelloRun.py
#
# Purpose:     This module is used to create a controller to control the DJI 
#              Tello Drone and connect to the Arduino_ESP8266 height sensor.
#
# Author:      Yuancheng Liu
#
# Created:     2019/10/04
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import sys
import time
import socket
import threading
import queue as queue

import wx   # use wx to build the UI.
import cv2  # use cv2 to capture the UDP video stream.

import telloGlobal as gv
import telloPanel as tp
import telloSensor as ts

# The keyboad key to control the drone.
KEY_CODE = {
    '87'    : 'up',     # Key 'w'
    '83'    : 'down',   # key 's'
    '65'    : 'cw',     # key 'a'
    '68'    : 'ccw',    # key 'd'
    '315'   : 'forward', # key 'up'
    '314'   : 'left',  # key 'left'
    '316'   : 'right', # key 'right'
    '317'   : 'back'   # key 'back'
}

PERIODIC = 100  # periodicly call by 10ms

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloFrame(wx.Frame):
    """ DJI tello drone controler program."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(520, 810))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        
        self.connFlagD = False      # Drone connection flag.
        self.connFlagS = False      # Sensor connection flag.
        self.cmdQueue = queue.Queue(maxsize=10)
        self.infoWindow = None      # drone detail information window.
        # Init the cmd/rsp UDP server.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(gv.FB_IP)
        # Init the UI.
        self.SetSizer(self._buidUISizer())
        # Tcp server to connect to the sensor.
        gv.iSensorChecker = ts.telloSensor(1, "Arduino_ESP8266", 1)
        gv.iSensorChecker.start()

        # UDP server the read the drone state
        self.droneRsp = telloRespSer(2, "DJI_DRONE_STATE", 1)
        self.droneRsp.start()

        self.videoRsp = telloVideopSer(2, "DJI_DRONE_STATE", 1)
        self.videoRsp.start()

        # Set the periodic feedback:
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 300 ms
        # Set the key sense event
        self.Bind(wx.EVT_KEY_DOWN, self.keyDown)
        # Add Close event here.
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        print("Init finished")

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
        gv.iCamPanel = self.camPanel = tp.PanelCam(self)
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
        self.connectBt = wx.Button(self, label='UAV Connect', size=(90, 20))
        self.connectBt.Bind(wx.EVT_BUTTON, self.onConnect)
        mSizer.Add(self.connectBt, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.connectLbD = wx.StaticText(self, label=" UAV_Offline".ljust(15))
        self.connectLbD.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.connectLbD, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.batteryLbD = wx.StaticText(
            self, label=" Battery:[000%]".ljust(20))
        self.batteryLbD.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.batteryLbD, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.connectLbS = wx.StaticText(self, label=" SEN_Offline".ljust(15))
        self.connectLbS.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.connectLbS, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.senAttLb = wx.StaticText(
            self, label=" SEN_Att: None".ljust(20))
        self.senAttLb.SetBackgroundColour(wx.Colour(120, 120, 120))
        mSizer.Add(self.senAttLb, flag=flagsR, border=2)
        self.detailBt =  wx.Button(self, label='>>', size=(30, 20))
        self.detailBt.Bind(wx.EVT_BUTTON, self.showDetail)
        mSizer.Add(self.detailBt, flag=flagsR, border=2)
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
            self.connectLbD.SetLabel(" UAV_Online".ljust(15))
            self.connectLbD.SetBackgroundColour(wx.Colour('GREEN'))
            self.connFlagD = True

    def updateSenConn(self, state):
        """ update the sensor connection state
        """
        if self.connFlagS != state:
            self.connFlagS = state
            (lbText, bgColor) = (' SEN_Online', wx.Colour('Green')
                                 ) if self.connFlagS else ('SEN_Offline', wx.Colour(120, 120, 120))
            self.connectLbS.SetLabel(lbText)
            self.connectLbS.SetBackgroundColour(bgColor)

    def updateSenDis(self, state):
        (lbText, bgColor) = (' SEN_Att: Safe', wx.Colour('Green')) if state else (' SEN_Att: Unsafe', wx.Colour('RED'))
        self.senAttLb.SetLabel(lbText)
        self.senAttLb.SetBackgroundColour(bgColor)

#-----------------------------------------------------------------------------
    def periodic(self, event):
        """ periodic capture the image from camera:
        """
        # update the video
        now = time.time()
 
        self.camPanel.periodic(now)
        # Update the active cmd
        if self.connFlagD and now - self.lastPeriodicTime >= 5:
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
                self.videoRsp.initVideoConn(True)
            elif msg == 'streamoff' or data == 'error':
                self.videoRsp.initVideoConn(False)

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

#--PanelBaseInfo---------------------------------------------------------------
    def showDetail(self, event):
        """ Pop up the detail window to show all the sensor parameters value."""
        if self.infoWindow is None and gv.iDetailPanel is None:
            posF = gv.iMainFrame.GetPosition()
            self.infoWindow = wx.MiniFrame(gv.iMainFrame, -1,
                'UAV Detail', pos=(posF[0]+511, posF[1]),
                size=(130, 500),
                style=wx.DEFAULT_FRAME_STYLE)
            gv.iDetailPanel = tp.PanelDetail(self.infoWindow)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()

#--PanelBaseInfo---------------------------------------------------------------
    def infoWinClose(self, event):
        """ Close the pop-up detail information window"""
        if self.infoWindow:
            self.infoWindow.Destroy()
            gv.iDetailPanel = None
            self.infoWindow = None

#-----------------------------------------------------------------------------
    def OnClose(self, event):
        #self.ser.close()
        if gv.iSensorChecker: gv.iSensorChecker.stop()
        self.droneRsp.stop()
        self.videoRsp.stop()
        self.Destroy()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloVideopSer(threading.Thread):
    """ tello state response UDP reading server thread.""" 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False      
        self.capture = None     # Cv2 video capture handler.

#-----------------------------------------------------------------------------
    def run(self):
        """ main loop to handle the data feed back."""
        while not self.terminate:
            if self.capture and self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret: gv.iCamPanel.updateCvFrame(frame)
            #time.sleep(0.01) # add a sleep time to avoid hang the main UI.
            time.sleep(0.005)
        print('Tello video server terminated')

#-----------------------------------------------------------------------------
    def initVideoConn(self, initFlag=True):
        """ init the video connection. True-Init/reInit, False - Release"""
        if initFlag:
            if self.capture: self.capture.release() # relased the existed connection.
            ip, port = gv.VD_IP
            addr = 'udp://%s:%s' % (str(ip), str(port))
            self.capture = cv2.VideoCapture(addr)
        else:
            if self.capture: self.capture.release()
            self.capture = None
#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True
        self.initVideoConn(False)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloRespSer(threading.Thread):
    """ tello state response UDP reading server thread.""" 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False
        self.udpSer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSer.bind(gv.ST_IP)

#-----------------------------------------------------------------------------
    def run(self):
        """ main loop to handle the data feed back."""
        while not self.terminate:
            data, _ = self.udpSer.recvfrom(1518)
            if isinstance(data, bytes):
                data = data.decode(encoding="utf-8")
            #print (data)
            if not data: break
        print('Tello state server terminated')

#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True
        closeClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        closeClient.sendto(b'', ("127.0.0.1", gv.ST_IP[1]))
        closeClient.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        gv.iMainFrame = telloFrame(None, -1, gv.APP_NAME)
        gv.iMainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
