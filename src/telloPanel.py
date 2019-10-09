#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        TelloPanel.py
#
# Purpose:     This function is used to create the control or display panel for
#              the UAV system.
# Author:      Yuancheng Liu
#
# Created:     2019/10/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
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
        wx.Panel.__init__(self, parent,  size=(480, 360))
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.lastPeriodicTime = time.time()
        self.bmp = wx.Bitmap(480, 360)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.SetDoubleBuffered(True)

#-----------------------------------------------------------------------------
    def onPaint(self, evt):
        """ Draw the bitmap and the lines."""
        dc = wx.PaintDC(self)
        _ = dc.DrawBitmap(self.bmp, 0, 0) if self.bmp else dc.DrawRectangle(0, 0, 480, 360)
        dc.SetPen(wx.Pen('GREEN', width=1, style=wx.PENSTYLE_DOT))
        dc.DrawLine(240, 0, 240, 180)
        dc.DrawLine(0, 180, 480, 180)
        _ = [dc.DrawLine(220+5*i, 200+20*i, 260-5*i, 200+20*i) for i in range(4)] # draw the lvl line.

#-----------------------------------------------------------------------------
    def scale_bitmap(self, bitmap, width, height):
        """ resize the bitmap """
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

#-----------------------------------------------------------------------------
    def periodic(self, now):
        if now - self.lastPeriodicTime >= 0.5:
            self.updateDisplay()

#-----------------------------------------------------------------------------
    def updateCvFrame(self, cvFrame):
        """ Convert the openCV frame image to wx bitmap."""
        # print(cvFrame.shape[:2]) # the tello feed back video format is 960*720
        h, w = cvFrame.shape[:2]
        # frame = cv2.cvtColor(cvFrame, cv2.COLOR_BGR2RGB)
        self.bmp = self.scale_bitmap(wx.BitmapFromBuffer(
            w, h, cv2.cvtColor(cvFrame, cv2.COLOR_BGR2RGB)), 480, 360)

#-----------------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function will 
            set the self update flag.
        """
        self.Refresh(False)
        self.Update()


class TrackCtrlPanel(wx.Panel):
    """ Panel provides three Grids to show/set the all the PLCs' I/O data."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(500, 70))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.selectTrack = 'None'
        self.trackLbs = []
        self.trackDict = {'None': ['-']*15}
        self.loadTrack()
        self.SetSizer(self._buidUISizer())
        self.Refresh(False)

    def _buidUISizer(self):
        mSizer = wx.BoxSizer(wx.VERTICAL)
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        flagsC = wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL
        bhox3 = wx.BoxSizer(wx.HORIZONTAL)
        bhox3.Add(wx.StaticText(
            self, label="Track Control:".ljust(15)), flag=flagsC, border=2)
        bhox3.AddSpacer(5)
        self.trackCtrl = wx.ComboBox(
            self, -1, choices=list(self.trackDict.keys()),size=(90, 22), style=wx.CB_READONLY)
        self.trackCtrl.SetSelection(0)
        self.trackCtrl.Bind(wx.EVT_COMBOBOX, self.onTrackSel)
        bhox3.Add(self.trackCtrl, flag=flagsR, border=2)
        bhox3.AddSpacer(5)
        self.trackAcBt = wx.Button(self, label='ActiveTrack', size=(90, 22))
        bhox3.Add(self.trackAcBt, flag=flagsR, border=2)
        bhox3.AddSpacer(5)
        self.trackAcBt.Bind(wx.EVT_BUTTON, self.onTrackAct)



        self.trackEdBt = wx.Button(self, label='EditTrack', size=(90, 22))
        bhox3.Add(self.trackEdBt, flag=flagsR, border=2)
        bhox3.AddSpacer(5)
        self.trackAnBt = wx.Button(self, label='AddNewTrack', size=(90, 22))
        bhox3.Add(self.trackAnBt, flag=flagsR, border=2)
        mSizer.Add(bhox3, flag=flagsR, border=2)
        mSizer.AddSpacer(5)
        # track display area:
        gs = wx.GridSizer(2, 8, 5, 5)
        gs.Add(wx.StaticText(self, label="Track:".ljust(12)), flag=flagsC, border=2)
        for val in self.trackDict[self.selectTrack]:
            tracklb = wx.StaticText(self, label=str(val).ljust(12))
            tracklb.SetBackgroundColour(wx.Colour(200, 200, 200))
            self.trackLbs.append(tracklb)
            gs.Add(tracklb, flag=flagsR, border=2)
        mSizer.Add(gs, flag=flagsR, border=2)
        return mSizer

    def loadTrack(self):
        """ Load the track from the track file.
        """
        f = open(gv.TRACK_PATH, "r")
        fh = f.readlines()
        for line in fh:
            parms = line.split(';')
            key, val = parms[0], parms[1:]
            self.trackDict[key] = val
        print(self.trackDict.keys())
        f.close()

    def onTrackSel(self, event):
        sel = self.trackCtrl.GetSelection()
        self.selectTrack = self.trackCtrl.GetString(sel)
        self.trackAcBt.Enable(self.selectTrack != 'None')
        # clear all 
        for i, val in enumerate(self.trackDict['None']):
            self.trackLbs[i].SetLabel(str(val).ljust(12))
        # set to selected track
        for i, val in enumerate(self.trackDict[self.selectTrack]):
            self.trackLbs[i].SetLabel(str(val).ljust(12))
        self.Refresh(False)

    def onTrackAct(self, event):
        if 

                
                



    







