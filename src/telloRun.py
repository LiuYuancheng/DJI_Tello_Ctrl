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
import telloPanel as tp


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





class telloFrame(wx.Frame):
    """ Railway system control hub."""

    def __init__(self, parent, id, title):
        """ Init the UI and parameters """
        wx.Frame.__init__(self, parent, id, title, size=(510, 650))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetIcon(wx.Icon(gv.ICO_PATH))
        
        
        
        host = ''
        port = 9000
        locaddr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(locaddr)
        self.connectFlag = False
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
        flagsC = wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer.AddSpacer(5)
        hsizer.Add(self._buildStateSizer(), flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        self.camPanel = tp.PanelCam(self)
        hsizer.Add(self.camPanel, flag=wx.ALIGN_CENTER_HORIZONTAL |
                   wx.ALIGN_CENTER_VERTICAL, border=2)
        hsizer.AddSpacer(5)

        bhox1 = wx.BoxSizer(wx.HORIZONTAL)
        bhox1.AddSpacer(20)
        bhox1.Add(wx.StaticText(self, label="Vertical Motion Ctrl".ljust(40)) ,flag=flagsC, border=2)
        bhox1.Add(wx.StaticText(self, label="Takeoff and Cam Ctrl".ljust(40)) ,flag=flagsC, border=2)
        bhox1.Add(wx.StaticText(self, label="Horizontal Motion Ctrl".ljust(40)) ,flag=flagsC, border=2)
        hsizer.Add(bhox1, flag=flagsR, border=2)

        hsizer.AddSpacer(5)
        hsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        bhox2 = wx.BoxSizer(wx.HORIZONTAL)
        bhox2.AddSpacer(10)



        gs1 = wx.GridSizer(2, 3, 5, 5)
        for k, item in enumerate(gv.YA_CMD_LIST):
            bmp0 = wx.Bitmap(gv.YA_PNG_LIST[k], wx.BITMAP_TYPE_ANY)
            outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0, size=(
                bmp0.GetWidth()+6, bmp0.GetHeight()+6), name=item)
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs1.Add(outputBt, flag=flagsR, border=2)
        bhox2.Add(gs1, flag=flagsR, border=2)

        bhox2.AddSpacer(15)
        bhox2.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 100),style=wx.LI_VERTICAL), flag=flagsR, border=2)
        bhox2.AddSpacer(15)

        gs2 = wx.GridSizer(2, 2, 5, 5)
        for k, item in enumerate(gv.IN_CMD_LIST):
            bmp0 = wx.Bitmap(gv.IN_PNG_LIST[k], wx.BITMAP_TYPE_ANY)
            outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0, size=(
                bmp0.GetWidth()+6, bmp0.GetHeight()+6), name=item)
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs2.Add(outputBt, flag=flagsR, border=2)
        bhox2.Add(gs2, flag=flagsR, border=2)

        bhox2.AddSpacer(15)
        bhox2.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 100),style=wx.LI_VERTICAL), flag=flagsR, border=2)
        bhox2.AddSpacer(15)


        gs3 = wx.GridSizer(2, 3, 5, 5)
        for k, item in enumerate(gv.XA_CMD_LIST):
            bmp0 = wx.Bitmap(gv.XA_PNG_LIST[k], wx.BITMAP_TYPE_ANY)
            outputBt = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp0, size=(
                bmp0.GetWidth()+6, bmp0.GetHeight()+6), name=item)
            outputBt.Bind(wx.EVT_BUTTON, self.onButton)
            gs3.Add(outputBt, flag=flagsR, border=2)
        bhox2.Add(gs3, flag=flagsR, border=2)
        hsizer.Add(bhox2, flag=flagsR, border=2)

        hsizer.AddSpacer(5)
        hsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        hsizer.AddSpacer(5)

        bhox3 = wx.BoxSizer(wx.HORIZONTAL)
        bhox3.AddSpacer(5)
        bhox3.Add(wx.StaticText(self, label="Track Control:".ljust(15)) ,flag=flagsC, border=2)
        bhox3.AddSpacer(5)
        
        self.trackCtrl = wx.ComboBox(self, -1, choices=['Track1', 'Track2'], style=wx.CB_READONLY)
        self.trackCtrl.SetSelection(0)
        bhox3.Add(self.trackCtrl ,flag=flagsC, border=2)

        bhox3.AddSpacer(5)
        self.trackAcBt = wx.Button(self, label='ActiveTrack', size=(90, 22))
        bhox3.Add(self.trackAcBt ,flag=flagsR, border=2)

        bhox3.AddSpacer(5)
        self.trackEdBt = wx.Button(self, label='EditTrack', size=(90, 22))
        bhox3.Add(self.trackEdBt ,flag=flagsR, border=2)

        bhox3.AddSpacer(5)
        self.trackAnBt = wx.Button(self, label='AddNewTrack', size=(90, 22))
        bhox3.Add(self.trackAnBt ,flag=flagsR, border=2)
        
        hsizer.Add(bhox3, flag=flagsR, border=2)

        hsizer.AddSpacer(5)
        hsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(510, -1),
                                 style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        hsizer.AddSpacer(5)


        #bhox4 = wx.BoxSizer(wx.HORIZONTAL)
        #bhox4.AddSpacer(5)
        #bhox4.Add(wx.StaticText(self, label="Sensor Control:".ljust(15)) ,flag=flagsC, border=2)
        #bhox4.AddSpacer(5)

        #bhox4.Add(wx.StaticText(self, label="Iteration Number:") ,flag=flagsC, border=2)
        #self.InheritAttributes = wx.TextCtrl(self, -1, "", size=(100, -1), style=wx.TE_PROCESS_ENTER)





        return hsizer

    def _buildStateSizer(self):
        """ Build the UAV + sensor state display.
        """
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddSpacer(5)
        self.connectBt = wx.Button(self, label='UAV_Connect', size=(90, 20))
        self.connectBt.Bind(wx.EVT_BUTTON, self.onConnect)
        hsizer.Add(self.connectBt,flag=flagsR, border=2)

        hsizer.AddSpacer(5)
        self.connectLbD = wx.StaticText(self, label=" UAV_Offline".ljust(15))
        self.connectLbD.SetBackgroundColour(wx.Colour(120, 120, 120))
        hsizer.Add(self.connectLbD,flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        self.batteryLbD = wx.StaticText(self, label=" UAV_Battery:[0%]".ljust(20))
        self.batteryLbD.SetBackgroundColour(wx.Colour(120, 120, 120))
        hsizer.Add(self.batteryLbD,flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        self.connectLbS = wx.StaticText(self, label=" SEN_Offline".ljust(15))
        self.connectLbS.SetBackgroundColour(wx.Colour(120, 120, 120))
        hsizer.Add(self.connectLbS,flag=flagsR, border=2)
        hsizer.AddSpacer(5)
        self.batteryLbS = wx.StaticText(self, label=" SEN_Battery:[100%]".ljust(20))
        self.batteryLbS.SetBackgroundColour(wx.Colour(120, 120, 120))
        hsizer.Add(self.batteryLbS,flag=flagsR, border=2)
        hsizer.AddSpacer(10)
        return hsizer


    def onConnect(self, event):
        """ Try to connect the drone and control uder SDK cmd mode.
        """
        self.sendMsg('command')
        if self.recvMsg() == 'ok':
            self.connectLbD.SetLabel("UAV_Online".ljust(15))
            self.connectLbD.SetBackgroundColour(wx.Colour('GREEN'))
            self.connectFlag = True

    def onButton(self, event):
        msg = event.GetEventObject().GetName()
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
        if self.connectFlag and now - self.lastPeriodicTime >= 3:
            self.sendMsg('command')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        mainFrame = telloFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True


app = MyApp(0)
app.MainLoop()
