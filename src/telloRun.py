#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        TelloRun.py
#
# Purpose:     This module is used to create a controller to control the DJI 
#              Tello Drone and connect to the Arduino_ESP8266 to get the height
#              sensor data.
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
import cv2  # use cv2 to capture the H264 UDP video stream.
# import local modules.
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

PERIODIC = 100  # main thread periodicly call by 10ms

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloFrame(wx.Frame):
    """ DJI tello drone controler program."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(520, 810))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        self.connFlagD = False      # drone connection flag.
        self.connFlagS = False      # sensor connection flag.
        self.infoWindow = None      # drone detail information window.
        self.stateFbStr = None      # drone feed back data string
        self.cmdQueue = queue.Queue(maxsize=10)
        # Init the cmd/rsp UDP server.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(gv.FB_IP)
        # Init TCP server thread to connect to the sensor.
        gv.iSensorChecker = ts.telloSensor(1, "Arduino_ESP8266", 1)
        gv.iSensorChecker.start()
        # Init UDP server thread the read the drone state.
        self.droneRsp = telloRespSer(2, "DJI_TELLO_STATE", 1)
        self.droneRsp.start()
        # Init UDP server thread to get the H264 video stream.
        self.videoRsp = telloVideopSer(3, "DJI_TELLO_VIDEO", 1)
        self.videoRsp.start()
        # Init the UI.
        self.SetSizer(self._buidUISizer())
        # Set the periodic feedback:
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 100 ms
        # Set the key sense event
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        # Add Close event here.
        self.Bind(wx.EVT_CLOSE, self.onClose)
        print("Program init finished.")

#-----------------------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI sizer of the frame."""
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        flagsC = wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.VERTICAL)
        mSizer.AddSpacer(5)
        # Row Idx = 0 : state diaplay
        mSizer.Add(self._buildStateSizer(), flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # Row Idx = 1 : Camera display panel
        gv.iCamPanel = tp.PanelCam(self)
        mSizer.Add(gv.iCamPanel, flag=flagsC, border=2)
        mSizer.AddSpacer(5)
        # Row Idx = 2: Drone Control part
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(20) # Added the title line.
        hbox.Add(wx.StaticText(
            self, label="Vertical Motion Ctrl".ljust(40)), flag=wx.ALL, border=2)
        hbox.Add(wx.StaticText(
            self, label="Takeoff and Cam Ctrl".ljust(40)), flag=wx.ALL, border=2)
        hbox.Add(wx.StaticText(
            self, label="Horizontal Motion Ctrl".ljust(40)), flag=wx.ALL, border=2)
        mSizer.Add(hbox, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5) # Added the control buttons.
        mSizer.Add(self._buildCtrlSizer(), flag=flagsR, border=2)
        # Split line
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # Row Idx = 3 : Track editing and control.
        gv.iTrackPanel = tp.TrackCtrlPanel(self)
        mSizer.Add(gv.iTrackPanel, flag=flagsC, border=2)
        # Split line
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # Row Idx = 4 : Sensor PATT attestation control.
        gv.iSensorPanel = tp.SensorCtrlPanel(self)
        mSizer.Add(gv.iSensorPanel, flag=flagsC, border=2)
        return mSizer

#-----------------------------------------------------------------------------
    def _buildCtrlSizer(self):
        """ Build the Drone control sizer with all the control buttons."""
        mSizer, flagsR = wx.BoxSizer(wx.HORIZONTAL), wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        mSizer.AddSpacer(10)
        # Control list element: (sizer, cmd list, button bitmap png file list.)
        ctrlList = ((wx.GridSizer(2, 3, 5, 5), gv.YA_CMD_LIST, gv.YA_PNG_LIST),
                    (wx.GridSizer(2, 2, 5, 5), gv.IN_CMD_LIST, gv.IN_PNG_LIST),
                    (wx.GridSizer(2, 3, 5, 5), gv.XA_CMD_LIST, gv.XA_PNG_LIST))
        for i, item in enumerate(ctrlList):
            (gs, cmdList, pngList) = item
            mSizer.AddSpacer(10)
            for k, val in enumerate(cmdList):
                bmp0 = wx.Bitmap(pngList[k], wx.BITMAP_TYPE_ANY)
                outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0, size=(
                    bmp0.GetWidth()+6, bmp0.GetHeight()+6), name=val)
                outputBt.Bind(wx.EVT_BUTTON, self.onButton)
                gs.Add(outputBt, flag=flagsR, border=2)
            mSizer.Add(gs, flag=flagsR, border=2)
            mSizer.AddSpacer(10)
            if i < 2:
                mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 100),
                                         style=wx.LI_VERTICAL), flag=flagsR, border=2)
        return mSizer

#-----------------------------------------------------------------------------
    def _buildStateSizer(self):
        """ Build the UAV + sensor state display sizer."""
        flagsR, dtColor = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, wx.Colour(120, 120, 120)
        mSizer = wx.BoxSizer(wx.HORIZONTAL)
        mSizer.AddSpacer(5)
        self.connectBt = wx.Button(self, label='UAV Connect', size=(90, 20))
        self.connectBt.Bind(wx.EVT_BUTTON, self.onUAVConnect)
        mSizer.Add(self.connectBt, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.connectLbD = wx.StaticText(self, label=" UAV_Offline".ljust(15))
        self.connectLbD.SetBackgroundColour(dtColor)
        mSizer.Add(self.connectLbD, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.batteryLbD = wx.StaticText(self, label=" Battery:[000%]".ljust(20))
        self.batteryLbD.SetBackgroundColour(dtColor)
        mSizer.Add(self.batteryLbD, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.connectLbS = wx.StaticText(self, label=" SEN_Offline".ljust(15))
        self.connectLbS.SetBackgroundColour(dtColor)
        mSizer.Add(self.connectLbS, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.senAttLb = wx.StaticText(self, label=" SEN_Att: None".ljust(20))
        self.senAttLb.SetBackgroundColour(dtColor)
        mSizer.Add(self.senAttLb, flag=flagsR, border=2)
        self.detailBt =  wx.Button(self, label=' >> ', size=(32, 20))
        self.detailBt.Bind(wx.EVT_BUTTON, self.showDetail)
        mSizer.Add(self.detailBt, flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        return mSizer

#--PanelBaseInfo---------------------------------------------------------------
    def infoWinClose(self, event):
        """ Close the pop-up detail information window"""
        if self.infoWindow:
            self.infoWindow.Destroy()
            gv.iDetailPanel = None
            self.infoWindow = None

#-----------------------------------------------------------------------------
    def getHtAndBat(self):
        """ Return the current drone height and battery."""
        h, b = 0, 0
        if self.stateFbStr:
            dataList = self.stateFbStr.split(';')
            h, b = int(dataList[9].split(':')[1]), int(dataList[10].split(':')[1])
        return (h, b)

#-----------------------------------------------------------------------------
    def onButton(self, event):
        """ Add  cmd to the cmd queue when the user press the UI button."""
        cmd = event.GetEventObject().GetName()
        print("Add message %s in the cmd Q." % cmd)
        if not cmd in gv.IN_CMD_LIST: cmd = cmd + " 30"
        self.queueCmd(cmd)

#-----------------------------------------------------------------------------
    def onKeyDown(self, event):
        """ Handle the control when the user press the keyboard."""
        print("OnKeyDown event %s" % (event.GetKeyCode()))
        self.queueCmd(KEY_CODE[str(event.GetKeyCode())])

#-----------------------------------------------------------------------------
    def onUAVConnect(self, event):
        """ Try to connect the drone and switch the control to SDK cmd mode."""
        # Connect to the drone and get the feed back from the cmd channel.
        self.sendMsg('command')
        self.connFlagD = (self.recvMsg() == 'ok')
        # Update the UI
        if self.connFlagD:
            self.connectLbD.SetLabel(" UAV_Online".ljust(15))
            self.connectLbD.SetBackgroundColour(wx.Colour('GREEN'))
        else:
            print('Tello: connect to the drone failed.')

#-----------------------------------------------------------------------------
    def updateBatterSt(self, pct):
        """ Update the UI drone battery state."""
        self.batteryLbD.SetLabel(" Battery:[%s]".ljust(20) % str(pct).zfill(3))
        bgcolor = ('GRAY', 'RED', 'YELLOW', 'GREEN')
        self.batteryLbD.SetBackgroundColour(wx.Colour(min(bgcolor//30, 3)))
        self.batteryLbD.Refresh(True)

#-----------------------------------------------------------------------------
    def updateSenConn(self, state):
        """ Update the UI sensor connection state."""
        if self.connFlagS == state: return # return if the state a same as UI shown
        self.connFlagS = state
        (lbText, bgColor) = (' SEN_Online', wx.Colour('Green')
                             ) if self.connFlagS else ('SEN_Offline', wx.Colour(120, 120, 120))
        self.connectLbS.SetLabel(lbText)
        self.connectLbS.SetBackgroundColour(bgColor)

#-----------------------------------------------------------------------------
    def updateDataStr(self, dataStr):
        """ Update the drone state data feedback string."""
        self.stateFbStr = dataStr

#-----------------------------------------------------------------------------
    def updateSenDis(self, state):
        """ Update the sensor attestation check result."""
        (lbText, bgColor) = (' SEN_Att: Safe', wx.Colour('Green')) if state else (' SEN_Att: Unsafe', wx.Colour('RED'))
        self.senAttLb.SetLabel(lbText)
        self.senAttLb.SetBackgroundColour(bgColor)

#-----------------------------------------------------------------------------
    def periodic(self, event):
        """ Periodic call back to handle all the functions."""
        now = time.time()
        # update the video panel.
        gv.iCamPanel.periodic(now)
        # Update the active cmd ever 2 second.
        if self.connFlagD and now - self.lastPeriodicTime >= 5:
            cmd = gv.iTrackPanel.getAction()
            if not cmd: cmd = 'command'
            self.queueCmd(cmd)
            _, btPct = self.getHtAndBat()
            self.updateBatterSt(btPct)
            self.lastPeriodicTime = now
        # update the detail panel.
        if gv.iDetailPanel:
            gv.iDetailPanel.periodic(now)
        # pop the cmd queue and send the cmd.
        if not self.cmdQueue.empty():
            msg = self.cmdQueue.get()
            print('cmd: %s' %msg)
            self.sendMsg(msg)
            data = self.recvMsg() if msg in ('streamon', 'streamoff') else ''
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

#-----------------------------------------------------------------------------
    def showDetail(self, event):
        """ Pop up the detail window to show all the drone state value."""
        if self.infoWindow is None and gv.iDetailPanel is None:
            posF = gv.iMainFrame.GetPosition()
            self.infoWindow = wx.MiniFrame(gv.iMainFrame, -1,
                                           'UAV Detail', pos=(posF[0]+511, posF[1]),
                                           size=(130, 500),
                                           style=wx.DEFAULT_FRAME_STYLE)
            gv.iDetailPanel = tp.PanelDetail(self.infoWindow)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()

#-----------------------------------------------------------------------------
    def onClose(self, event):
        """ Stop all the thread and close the UI."""
        if gv.iSensorChecker: gv.iSensorChecker.stop()
        self.droneRsp.stop()
        self.videoRsp.stop()
        self.Destroy()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloVideopSer(threading.Thread):
    """ Tello camera UDP H264 video stream reading server thread.""" 
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
            time.sleep(0.006)
        print('Tello video server terminated.')

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
    """ Tello state prameters feedback UDP reading server thread.""" 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False
        self.udpSer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSer.bind(gv.ST_IP)

#-----------------------------------------------------------------------------
    def run(self):
        """ main loop to handle the data feed back."""
        while not self.terminate:
            data, _ = self.udpSer.recvfrom(1518) # YC: Why the API use this buffer size ? 
            if not data: break
            if isinstance(data, bytes):
                data = data.decode(encoding="utf-8")
                gv.iMainFrame.updateDataStr(data)
                if gv.iDetailPanel: gv.iDetailPanel.updateDataStr(data)
        print('Tello state server terminated')

#-----------------------------------------------------------------------------
    def stop(self):
        """ Send back a Null message to terminate the buffer reading waiting part."""
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
