#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        TelloPanel.py
#
# Purpose:     This module is used to create the control and display panel for
#              the UAV system (drone control and sensor firmware attestation).
#
# Author:      Yuancheng Liu
#
# Version:     v_0.3.1
# Created:     2019/10/01
# Copyright:   Copyright (c) 2019 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
import wx
import time
import cv2
import telloGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelCam(wx.Panel):
    """ Tello drone camera image display panel."""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(480, 360))
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.lastPeriodicTime = time.time()
        self.heigh = 0
        self.bmp = wx.Bitmap(480, 360)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.SetDoubleBuffered(True)

#--PanelCam--------------------------------------------------------------------
    def onPaint(self, evt):
        """ Draw the bitmap and the indicator lines."""
        dc = wx.PaintDC(self)
        _ = dc.DrawBitmap(self.bmp, 0, 0) if self.bmp else dc.DrawRectangle(0, 0, 480, 360)
        dc.SetPen(wx.Pen('GREEN', width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(240, 0, 240, 180)
        dc.DrawLine(0, 180, 480, 180)
        # Draw the horizontal indicator line.
        _ = [dc.DrawLine(220+5*i, 200+20*i, 260-5*i, 200+20*i) for i in range(4)]
        dc.SetTextForeground(wx.Colour('GREEN'))
        dc.DrawText('H: %s' % str(self.heigh), 250, 260)
        #dc.DrawText('Battery: %s' % str(self.battery), 20, 20)

#--PanelCam--------------------------------------------------------------------
    def scale_bitmap(self, bitmap, width, height):
        """ Resize the input bitmap."""
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

#--PanelCam--------------------------------------------------------------------
    def periodic(self, now):
        if now - self.lastPeriodicTime >= 0.05:
            """ Update the camera under 20 fps. """
            self.updateDisplay()
            self.lastPeriodicTime = now

#--PanelCam--------------------------------------------------------------------
    def updateHeight(self, height):
        """ Update the Drone height data """
        self.heigh = height

#--PanelCam--------------------------------------------------------------------
    def updateCvFrame(self, cvFrame):
        """ Convert the openCV frame image to wx bitmap."""
        # print(cvFrame.shape[:2]) # the tello feed back video format is 960*720
        h, w = cvFrame.shape[:2] # will raise error if the size is not match.
        # frame = cv2.cvtColor(cvFrame, cv2.COLOR_BGR2RGB)
        self.bmp = self.scale_bitmap(wx.BitmapFromBuffer(
            w, h, cv2.cvtColor(cvFrame, cv2.COLOR_BGR2RGB)), 480, 360)

#--PanelCam--------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(False)
        self.Update()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelDetail(wx.Panel):
    """ Panel to show the detail information of the drone."""
    def __init__(self, parent, stateList):
        wx.Panel.__init__(self, parent,  size=(130, 500))
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.stateList = stateList  # list to store all state information.
        self.labelList = []         # label list shown on the panel.
        self.lastPeriodicTime = time.time()
        self.SetSizer(self._buidUISizer())

#--PanelDetail-----------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI sizer for the panel."""
        flagsR = wx.RIGHT #| wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.VERTICAL)
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticText(self, label="Detail Info:"),
                   flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        mSizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(130, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        mSizer.AddSpacer(10)
        for val in self.stateList:
            lb = wx.StaticText(self, label=' > %s' % val)
            self.labelList.append(lb)
            mSizer.Add(lb, flag=flagsR, border=2)
            mSizer.AddSpacer(5)
        return mSizer

#--PanelDetail-----------------------------------------------------------------
    def periodic(self, now):
        """ Periodic call back, update every 0.5 sec."""
        if now - self.lastPeriodicTime >= 0.5:
            self.updateDisplay()
            self.lastPeriodicTime = now

#--PanelDetail-----------------------------------------------------------------
    def updateDisplay(self):
        """ Update the information shown on the panel."""
        if len(self.stateList) != len(self.labelList): return # check whether data match.
        for i, val in enumerate(self.stateList):
            self.labelList[i].SetLabel(' >  %s'  %val)
        self.Refresh(False)

#--PanelDetail-----------------------------------------------------------------
    def updateState(self, stateList):
        """ Update the state list."""
        self.stateList = stateList

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class TrackCtrlPanel(wx.Panel):
    """ Panel used to select the track and show the auto-tracking progress."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(510, 70))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.selectTrack = 'None'
        self.trackLbs = []  # Track display label list.
        self.trackDict = {'None': ['-']*15} # track_name: action list dict.
        self.actionIdx = -1 # current executing action's idx in the track.
        self.loadTrack(None)
        self.SetSizer(self._buidUISizer())
        self.Refresh(False)

#--TrackCtrlPanel--------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI sizer for the panel."""
        mSizer = wx.BoxSizer(wx.VERTICAL)
        flagsR = wx.RIGHT #| wx.ALIGN_CENTER_VERTICAL
        flagsC = wx.CENTER #| wx.ALIGN_CENTER_VERTICAL
        # Row Idx 0 : Track control area.
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(
            self, label="Track Control:".ljust(15)), flag=flagsC, border=2)
        hbox.AddSpacer(5)
        self.trackCtrl = wx.ComboBox(
            self, -1, choices=list(self.trackDict.keys()),size=(90, 22), style=wx.CB_READONLY)
        self.trackCtrl.SetSelection(1)
        self.trackCtrl.Bind(wx.EVT_COMBOBOX, self.onTrackSel)
        hbox.Add(self.trackCtrl, flag=flagsR, border=2)
        hbox.AddSpacer(5)
        self.trackAcBt = wx.Button(self, label='ActiveTrack', size=(90, 22))
        self.trackAcBt.Bind(wx.EVT_BUTTON, self.onTrackAct)
        hbox.Add(self.trackAcBt, flag=flagsR, border=2)
        hbox.AddSpacer(5)
        self.trackEdBt = wx.Button(self, label='ReLoadTrack', size=(90, 22))
        self.trackEdBt.Bind(wx.EVT_BUTTON, self.loadTrack)
        hbox.Add(self.trackEdBt, flag=flagsR, border=2)
        hbox.AddSpacer(5)
        self.trackStopBt = wx.Button(self, label='EmergencyStop', size=(90, 22))
        self.trackStopBt.SetBackgroundColour(wx.Colour('YELLOW'))
        self.trackStopBt.Bind(wx.EVT_BUTTON, self.onEmerg)
        hbox.Add(self.trackStopBt, flag=flagsR, border=2)
        mSizer.Add(hbox, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # Row Idx 2: Track display area
        gs = wx.GridSizer(2, 8, 5, 5)
        gs.Add(wx.StaticText(self, label="Track:".ljust(14)),flag=flagsC, border=2)
        for val in self.trackDict[self.selectTrack]:
            tracklb = wx.StaticText(self, label=str(val).ljust(14))
            tracklb.SetBackgroundColour(wx.Colour(200, 200, 200))
            self.trackLbs.append(tracklb)
            gs.Add(tracklb, flag=flagsR, border=2)
        mSizer.Add(gs, flag=flagsR, border=2)
        return mSizer

#--TrackCtrlPanel--------------------------------------------------------------
    def getAction(self):
        """ Return the action drone need to do for the current track."""
        if self.selectTrack == 'None' or self.actionIdx == -1:
            return None
        else:
            cmdList = self.trackDict[self.selectTrack]
            if self.actionIdx == len(cmdList):
                self.trackLbs[self.actionIdx-1].SetBackgroundColour(wx.Colour(200, 200, 200))
                self.Refresh(False)
                self.actionIdx = -1
                return 'land' # send land if 'land' cmd is not in the track.
            else:
                cmd = cmdList[self.actionIdx]
                self.trackLbs[self.actionIdx].SetBackgroundColour(wx.Colour('GREEN'))
                if self.actionIdx > 0: self.trackLbs[self.actionIdx-1].SetBackgroundColour(wx.Colour(200, 200, 200))
                self.Refresh(False)
                self.actionIdx += 1
                return cmd

#--TrackCtrlPanel--------------------------------------------------------------
    def loadTrack(self, event):
        """ Load the track from the track file."""
        self.selectTrack = 'None' # clear the selected track.
        with open(gv.TRACK_PATH, "r") as fh:
            for line in fh.readlines():
                parms = line.rstrip().split(';')
                key, val = parms[0], parms[1:]
                self.trackDict[key] = val
        print("Loaded tracks from file: %s" %str (self.trackDict.keys()))
        if not event is None: 
            self.onTrackSel(None) # load the current selected track back.

#--TrackCtrlPanel--------------------------------------------------------------
    def onEmerg(self, event):
        """ Emergency stop stop all motors immediately."""
        gv.iMainFrame.sendMsg('emergency')

#--TrackCtrlPanel--------------------------------------------------------------
    def onTrackAct(self, event):
        """ Acticve the selected track.(set the track action to idx=0)"""
        self.actionIdx = 0 if self.selectTrack != 'None' else -1
        print("Active track: %s" %self.selectTrack)

#--TrackCtrlPanel--------------------------------------------------------------
    def onTrackSel(self, event):
        """ Handle the track selection. """
        self.selectTrack = self.trackCtrl.GetString(self.trackCtrl.GetSelection())
        self.trackAcBt.Enable(self.selectTrack != 'None')
        # Clear all display first.
        for i, val in enumerate(self.trackDict['None']):
            self.trackLbs[i].SetLabel(str(val).ljust(14))
        # set to selected track
        for i, val in enumerate(self.trackDict[self.selectTrack]):
            self.trackLbs[i].SetLabel(str(val).ljust(14))
        self.Refresh(False)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class SensorCtrlPanel(wx.Panel):
    """ Sensor reading and firmware attestation display panel."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(500, 160))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetSizer(self._buidUISizer())

#--SensorCtrlPanel-------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the main UI sizer for the panel."""
        flagsR = wx.RIGHT #| wx.ALIGN_CENTER_VERTICAL
        mSizer = wx.BoxSizer(wx.VERTICAL)
        # row idx 0 : basic patt setting.
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.StaticText(self, label="Sensor Control: ".ljust(15)), flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        hbox0.Add(wx.StaticText(self, label="Iteration Num: "),flag=flagsR, border=2)
        self.iterN = wx.TextCtrl(self, -1, "1", size=(40, -1), style=wx.TE_PROCESS_ENTER)
        hbox0.Add(self.iterN, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        hbox0.Add(wx.StaticText(self, label="Block Value: "),flag=flagsR, border=2)
        self.blockN = wx.TextCtrl( self, -1, "4", size=(40, -1), style=wx.TE_PROCESS_ENTER)
        hbox0.Add(self.blockN, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        self.pattBt = wx.Button(self, label='StartPatt', size=(90, 25))
        self.pattBt.Bind(wx.EVT_BUTTON, self.onPattCheck)
        hbox0.Add(self.pattBt, flag=flagsR, border=2)
        mSizer.Add(hbox0, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        # row idx 1 : the patt attestation control display
        gs = wx.GridSizer(1, 8, 5, 5)
        fbLbList = ('Iteration:', ' - ','SeedVal:', ' - ', 'Altitude:', ' - ', 'TimeUsed', ' - ')
        self.lbList = [wx.StaticText(self, label=val) for val in fbLbList]
        _ = [gs.Add(fblb, flag=flagsR, border=2) for fblb in self.lbList]
        mSizer.Add(gs, flag=flagsR, border=2)
        hbox0.AddSpacer(5)
        mSizer.Add(wx.StaticText(self, label="Local Firmware Sample CheckSum: "),flag=flagsR, border=2)
        self.chSmTCL = wx.TextCtrl(self, size=(480, 25))#, style=wx.TE_MULTILINE)
        mSizer.Add(self.chSmTCL,flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        self.attesBar = wx.Gauge(self, range=200, size=(480, 17), style=wx.GA_HORIZONTAL)
        mSizer.Add(self.attesBar,flag=flagsR, border=2)
        mSizer.Add(wx.StaticText(self, label="Sensor Final Firmware CheckSum: "),flag=flagsR, border=2)
        self.chSmTCS = wx.TextCtrl(self, size=(480, 25))
        mSizer.Add(self.chSmTCS,flag=flagsR, border=2)
        return mSizer

#--SensorCtrlPanel-------------------------------------------------------------
    def onPattCheck(self, event):
        """ Start firmware Patt attestation when user click the startPatt button."""
        iterN, blockN = int(self.iterN.GetValue()), int(self.blockN.GetValue())
        self.chSmTCL.Clear()
        self.chSmTCS.Clear()
        self.attesBar.SetValue(10)
        print('Patt setting : %s' %str((iterN, blockN)))
        if gv.iSensorChecker:
            gv.iSensorChecker.setPattParameter(iterN, blockN)

#--SensorCtrlPanel-------------------------------------------------------------
    def updateInfo(self, iterN=None, sead=None, alti=None, timeU=None):
        """ Update information in Row Idx = 0 """
        if not iterN is None: self.lbList[1].SetLabel(str(iterN))
        if not sead is None: self.lbList[3].SetLabel(str(sead))
        if not alti is None: self.lbList[5].SetLabel(str(alti))
        if not timeU is None: self.lbList[7].SetLabel(str(timeU))
        self.Refresh(False)

#--SensorCtrlPanel-------------------------------------------------------------
    def updateProgress(self, val, tot):
        """ update the Patt progress bar. """
        self.attesBar.SetValue(val*200//tot)

#--SensorCtrlPanel-------------------------------------------------------------
    def updateChecksum(self, local=None, remote=None):
        """ Update the check sum display. """
        if local: 
            self.chSmTCL.AppendText(local)
            self.attesBar.SetValue(20)  # update the progress bar.
        if remote: self.chSmTCS.AppendText(remote)
