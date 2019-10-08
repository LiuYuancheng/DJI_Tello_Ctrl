#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        railwayHub.py
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

class PanelCam(wx.Panel):
    """ Image display panel.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent,  size=(480, 360))
        self.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.lastPeriodicTime = time.time()
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
        """ resize the bitmap
        """
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

