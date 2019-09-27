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

PERIODIC = 500 # periodicly call by 300ms

class telloFrame(wx.Frame):
    """ Railway system control hub."""
    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size= (500, 300))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))

        host = ''
        port = 9000
        locaddr = (host,port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(locaddr)


        self.SetSizer(self.buidUISizer())
        # Set the periodic feedback:
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 300 ms

        
    def buidUISizer(self):
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.VERTICAL)

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

    def sendMsg(self, msg):
        tello_address = ('192.168.10.1', 8889)
        msg = msg.encode(encoding="utf-8")
        self.sock.sendto(msg, tello_address)
        self.recvMsg()

    def recvMsg(self):
        data, server = self.sock.recvfrom(1518)
        print(data.decode(encoding="utf-8"))

    def periodic(self, event):
        pass
        

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        mainFrame = telloFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()