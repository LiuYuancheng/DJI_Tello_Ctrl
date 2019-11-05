#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        TelloRun.py
#
# Purpose:     This module is used to create a controller for the DJI Tello Drone
#              and connect to the Arduino_ESP8266 to get the height sensor data.
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
    '87'    : 'up 30',      # Key 'w'
    '83'    : 'down 30',    # key 's'
    '65'    : 'cw 30',      # key 'a'
    '68'    : 'ccw 30',     # key 'd'
    '315'   : 'forward 30', # key 'up'
    '314'   : 'left 30',    # key 'left'
    '316'   : 'right 30',   # key 'right'
    '317'   : 'back 30'     # key 'back'
}

PERIODIC = 100  # main thread periodically callback by 10ms.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloFrame(wx.Frame):
    """ DJI tello drone controller program."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(520, 810))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        self.connFlagD = False      # drone connection flag.
        self.connFlagS = False      # sensor connection flag.
        self.infoWindow = None      # drone detail information window.
        self.stateFbStr = None      # drone feed back data string.
        self.lastCmd = None         # last cmd send to the drone which has not get resp.
        self.cmdQueue = queue.Queue(maxsize=10) # drone control cmd q.
        self.droneCtrl = telloCtrlSer(0, "DJI_TELLO_CTRL", 1)
        self.droneCtrl.start()
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
        # Set the periodic callback.
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 100 ms
        # Set the key sense event.
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        # Add Close event here.
        self.Bind(wx.EVT_CLOSE, self.onClose)
        print("Program init finished.")

#--<telloFrame>----------------------------------------------------------------
    def _addSplitLine(self, pSizer, lStyle, length):
        """ Add the split line to the input sizer. 
            pSizer: parent sizer, lStyle: line style, length: pixel length.
        """
        pSizer.AddSpacer(5)
        lSize = (length, -1) if lStyle == wx.LI_HORIZONTAL else (-1, length)
        pSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=lSize,
                                 style=lStyle), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=2)
        pSizer.AddSpacer(5)

#--<telloFrame>----------------------------------------------------------------
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
        hbox.AddSpacer(20)  # Added the title line.
        lbList = ("Vertical Motion Ctrl",
                  "Takeoff and Cam Ctrl",
                  "Horizontal Motion Ctrl")
        _ = [hbox.Add(wx.StaticText(self, label=str(val).ljust(40)),
                      flag=wx.ALL, border=2) for val in lbList]
        mSizer.Add(hbox, flag=flagsR, border=2)
        self._addSplitLine(mSizer, wx.LI_HORIZONTAL, 510)
        # Added the control buttons.
        mSizer.Add(self._buildCtrlSizer(), flag=flagsR, border=2)
        # Split line
        self._addSplitLine(mSizer, wx.LI_HORIZONTAL, 510)
        # Row Idx = 3 : Track editing and control.
        gv.iTrackPanel = tp.TrackCtrlPanel(self)
        mSizer.Add(gv.iTrackPanel, flag=flagsC, border=2)
        self._addSplitLine(mSizer, wx.LI_HORIZONTAL, 510)
        # Row Idx = 4 : Sensor PATT attestation control.
        gv.iSensorPanel = tp.SensorCtrlPanel(self)
        mSizer.Add(gv.iSensorPanel, flag=flagsC, border=2)
        return mSizer

#--<telloFrame>----------------------------------------------------------------
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
                bmp = wx.Bitmap(pngList[k], wx.BITMAP_TYPE_ANY)
                outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size=(
                    bmp.GetWidth()+6, bmp.GetHeight()+6), name=val)
                outputBt.Bind(wx.EVT_BUTTON, self.onButton)
                gs.Add(outputBt, flag=flagsR, border=2)
            mSizer.Add(gs, flag=flagsR, border=2)
            mSizer.AddSpacer(5)
            if i < 2: self._addSplitLine(mSizer, wx.LI_VERTICAL, 100)
        return mSizer

#--<telloFrame>----------------------------------------------------------------
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
        mSizer.AddSpacer(5)
        return mSizer

#--<telloFrame>----------------------------------------------------------------
    def infoWinClose(self, event):
        """ Close the pop-up detail information window and clear paremeters."""
        if self.infoWindow:
            self.infoWindow.Destroy()
            self.infoWindow = gv.iDetailPanel = None

#--<telloFrame>----------------------------------------------------------------
    def getNextRrsp(self):
        """ Get the execution response of the last cmd and clear the last cmd for 
            the next cmd queue pop.
        """
        resp = self.droneCtrl.getRecvMsg()
        if resp:
            if self.lastCmd == 'streamon' and resp == 'ok':
                self.videoRsp.initVideoConn(True)
            elif self.lastCmd == 'streamoff' or  resp == 'error':
                self.videoRsp.initVideoConn(False)
            self.lastCmd = None # clear the last response for cmd queue pop

#--<telloFrame>----------------------------------------------------------------
    def onButton(self, event):
        """ Add a cmd to the cmd queue when user press a control button on UI."""
        cmd = event.GetEventObject().GetName()
        if not cmd in gv.IN_CMD_LIST: cmd = cmd + " 30"
        print("Add message [%s] in the cmd Q." % cmd)
        self.queueCmd(cmd)

#--<telloFrame>----------------------------------------------------------------
    def onClose(self, event):
        """ Stop all the thread and close the UI."""
        if gv.iSensorChecker: gv.iSensorChecker.stop()
        self.droneCtrl.stop()
        self.droneRsp.stop()
        self.videoRsp.stop()
        self.timer.Stop()
        self.Destroy()

#--<telloFrame>----------------------------------------------------------------
    def onKeyDown(self, event):
        """ Handle the control when the user press the keyboard."""
        keyCodeStr = str(event.GetKeyCode())
        print("OnKeyDown event %s" % keyCodeStr)
        if keyCodeStr in KEY_CODE.keys(): self.queueCmd(KEY_CODE[keyCodeStr])

#--<telloFrame>----------------------------------------------------------------
    def onUAVConnect(self, event):
        """ Try to connect the drone and switch the control to SDK cmd mode."""
        # Connect to the drone and get the feed back from the cmd channel.
        self.droneCtrl.sendMsg('command')

#--<telloFrame>----------------------------------------------------------------www
    def periodic(self, event):
        """ Periodic call back to handle all the functions."""
        now = time.time()
        self.updateConnState()
        # Update the video panel.
        gv.iCamPanel.updateHeight(self.droneRsp.getHeight())
        gv.iCamPanel.periodic(now)
        # Update the active cmd ever 2 second.
        if self.connFlagD and now - self.lastPeriodicTime >= 5:
            cmd = gv.iTrackPanel.getAction()
            if not cmd: cmd = 'command' # 'command' use file time cmd to keep drone alive
            self.queueCmd(cmd)
            self.updateBatterSt(self.droneRsp.getBattery())
            self.lastPeriodicTime = now
        # Update the drone detail state panel.
        if gv.iDetailPanel: 
            gv.iDetailPanel.updateState(self.droneRsp.getCrtState())
            gv.iDetailPanel.periodic(now)
        # pop the cmd queue and send the cmd.
        self.popNextCmd()
        # get response from the drone.
        self.getNextRrsp()

#--<telloFrame>----------------------------------------------------------------
    def popNextCmd(self):
        """ Pop the cmd queue and send the cmd, handling the response if needed."""
        if self.lastCmd is None and not self.cmdQueue.empty():
            self.lastCmd = self.cmdQueue.get()
            print('cmd: %s' %self.lastCmd)
            self.droneCtrl.sendMsg(self.lastCmd)

#--<telloFrame>----------------------------------------------------------------
    def queueCmd(self, cmd):
        """ Add the cmd in the cmd Queue."""
        if self.cmdQueue.full():
            print("cmd queue is full.")
            return
        self.cmdQueue.put(cmd)

#--<telloFrame>----------------------------------------------------------------
    def showDetail(self, event):
        """ Pop up the detail window to show all the drone state value."""
        if self.infoWindow is None and gv.iDetailPanel is None:
            posF = gv.iMainFrame.GetPosition()
            self.infoWindow = wx.MiniFrame(gv.iMainFrame, -1,
                                           'UAV Detail', pos=(posF[0]+511, posF[1]),
                                           size=(130, 500),
                                           style=wx.DEFAULT_FRAME_STYLE)
            gv.iDetailPanel = tp.PanelDetail(self.infoWindow, self.droneRsp.getCrtState())
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()

#--<telloFrame>----------------------------------------------------------------
    def updateConnState(self):
        if not self.connFlagD and self.droneCtrl.getRecvMsg():
            self.connFlagD = True
            self.connectLbD.SetLabel(" UAV_Online".ljust(15))
            self.connectLbD.SetBackgroundColour(wx.Colour('GREEN'))

#--<telloFrame>----------------------------------------------------------------
    def updateBatterSt(self, pct):
        """ Update the UI drone battery state. pct: int battery percent"""
        self.batteryLbD.SetLabel(" Battery:[%s]".ljust(20) % str(pct).zfill(3))
        bgcolor = ('GRAY', 'RED', 'YELLOW', 'GREEN')
        self.batteryLbD.SetBackgroundColour(wx.Colour(bgcolor[min(pct//30, 3)]))
        self.batteryLbD.Refresh(True)

#--<telloFrame>----------------------------------------------------------------
    def updateSenConn(self, state, terminate):
        """ Update the UI sensor connection state."""
        if self.connFlagS == state or terminate:
            return  # return if the state a same as UI shown
        self.connFlagS = state
        if self.connFlagS:
            self.connectLbS.SetLabel(' SEN_Online')
            self.connectLbS.SetBackgroundColour(wx.Colour('Green'))
            self.connectLbS.Refresh(False)
        else:
            self.connectLbS.SetLabel('SEN_Offline')
            self.connectLbS.SetBackgroundColour(wx.Colour(120, 120, 120))
            self.connectLbS.Refresh(False)

#--<telloFrame>----------------------------------------------------------------
    def updateSenDis(self, state):
        """ Update the sensor attestation check result."""
        (lbText, bgColor) = (' SEN_Att: Safe', wx.Colour('Green')) if state else (' SEN_Att: Unsafe', wx.Colour('RED'))
        self.senAttLb.SetLabel(lbText)
        self.senAttLb.SetBackgroundColour(bgColor)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloVideopSer(threading.Thread):
    """ Tello camera UDP H264 video stream reading server thread.""" 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False      
        self.capture = None     # Cv2 video capture handler.

#--<telloVideopSer>------------------------------------------------------------
    def run(self):
        """ Main loop to handle the data feed back."""
        while not self.terminate:
            if self.capture and self.capture.isOpened():
                try:
                    ret, frame = self.capture.read()
                    if ret: gv.iCamPanel.updateCvFrame(frame)
                #time.sleep(0.01) # add a sleep time to avoid hang the main UI.
                except:
                    time.sleep(0.01)
            time.sleep(0.006) # main video more smoth
        print('Tello video server terminated.')

#--<telloVideopSer>------------------------------------------------------------
    def initVideoConn(self, initFlag=True):
        """ Init the video connection. True:Init/reInit, False:Release"""
        if initFlag:
            if self.capture: self.capture.release() # relased the existed connection.
            ip, port = gv.VD_IP
            addr = 'udp://%s:%s' % (str(ip), str(port))
            self.capture = cv2.VideoCapture(addr)
        else:
            #if self.capture: self.capture.release()
            self.capture = None

#--<telloVideopSer>------------------------------------------------------------
    def stop(self):
        self.initVideoConn(False)
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloCtrlSer(threading.Thread):
    """ Tello state prameters feedback UDP reading server thread.""" 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False
        # Init the cmd/rsp UDP server.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(gv.FB_IP)
        self.recvMsg = None

    #--telloRespSer----------------------------------------------------------------
    def run(self):
        """ main loop to handle the data feed back."""
        while not self.terminate:
            data, _ = self.sock.recvfrom(1518) # YC: Why the API use this buffer size ? 
            if not data: break
            if isinstance(data, bytes):
                self.recvMsg = data.decode(encoding="utf-8")
        self.sock.close()
        print('Tello control server terminated')

    #--<telloFrame>----------------------------------------------------------------
    def sendMsg(self, msg):
        """ Send the control cmd to the drone directly."""
        self.sock.sendto(msg.encode(encoding="utf-8"), gv.CT_IP)

    #--<telloFrame>----------------------------------------------------------------
    def getRecvMsg(self):
        """ send the last response back and clear the record."""
        data = self.recvMsg
        self.recvMsg = None
        return data

    #--telloRespSer----------------------------------------------------------------
    def stop(self):
        """ Send back a None message to terminate the buffer reading waiting part."""
        self.terminate = True
        closeClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        closeClient.sendto(b'', ("127.0.0.1", gv.FB_IP[1]))
        closeClient.close()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloRespSer(threading.Thread):
    """ Tello state prameters feedback UDP reading server thread.""" 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        # Init drone feed back data list.
        self.stateList = ["pitch: 0", "roll: 0", "yaw: 0", "vgx: 0", "vgy 0",
                          "vgz: 0", "templ: 0", "temph: 0", "tof: 0", "h: 0",
                          "bat: 0", "baro: 0", "time: 0", "agx: 0", "agy: 0",
                          "agz: 0", "-:-"]
        self.terminate = False
        self.udpSer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSer.bind(gv.ST_IP)

#--telloRespSer----------------------------------------------------------------
    def run(self):
        """ main loop to handle the data feed back."""
        while not self.terminate:
            data, _ = self.udpSer.recvfrom(1518) # YC: Why the API use this buffer size ? 
            if not data: break
            if isinstance(data, bytes):
                dataStr = data.decode(encoding="utf-8")
                self.stateList = dataStr.split(';')
        self.udpSer.close()
        print('Tello state server terminated')
        
#--telloRespSer----------------------------------------------------------------
    def getHeight(self):
        """ Return the height value (unit: cm) as a int"""
        return int(self.stateList[9].split(':')[1]) 

#--telloRespSer----------------------------------------------------------------
    def getBattery(self):
        """ Return the battery value (unit: %) as a int"""
        return int(self.stateList[10].split(':')[1])

#--telloRespSer----------------------------------------------------------------
    def getCrtState(self):
        """ Return all the state data."""
        return self.stateList

#--telloRespSer----------------------------------------------------------------
    def stop(self):
        """ Send back a None message to terminate the buffer reading waiting part."""
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
