#-----------------------------------------------------------------------------
# Name:        telloGlobal.py
#
# Purpose:     This module is used as the Local config file to set constants, 
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/10/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import os

dirpath = os.getcwd()
print("Current working directory is : %s" %dirpath)
APP_NAME = 'DJI Tello Ctrl'

#------<IMAGES PATH>-------------------------------------------------------------
ICO_PATH = "".join([dirpath, "\\img\\telloIcon.ico"])
# Vertial control
YA_CMD_LIST = ('flip l', 'up', 'flip r', 'cw', 'down', 'ccw')
YA_PNG_LIST = ("".join([dirpath, "\\img\\flip_l.png"]),
               "".join([dirpath, "\\img\\up.png"]),
               "".join([dirpath, "\\img\\flip_r.png"]),
               "".join([dirpath, "\\img\\cw.png"]),
               "".join([dirpath, "\\img\\down.png"]),
               "".join([dirpath, "\\img\\ccw.png"]))
# Function control
IN_CMD_LIST = ('takeoff', 'land', 'streamon', 'streamoff')
IN_PNG_LIST = ("".join([dirpath, "\\img\\takeoff.png"]),
               "".join([dirpath, "\\img\\land.png"]),
               "".join([dirpath, "\\img\\streamon.png"]),
               "".join([dirpath, "\\img\\streamoff.png"]),)
# Horizontal control
XA_CMD_LIST = ('flip f', 'forward', 'flip b', 'left', 'back', 'right')
XA_PNG_LIST = ("".join([dirpath, "\\img\\flip_f.png"]),
               "".join([dirpath, "\\img\\forward.png"]),
               "".join([dirpath, "\\img\\flip_b.png"]),
               "".join([dirpath, "\\img\\left.png"]),
               "".join([dirpath, "\\img\\back.png"]),
               "".join([dirpath, "\\img\\right.png"]))

# Track record file:
TRACK_PATH = "".join([dirpath, "\\TrackPath.txt"])




CT_IP = ('192.168.10.1', 8889)  # Drone control IP 
VD_IP = ('192.168.10.2', 11111) # UDP video stream server IP 
FB_IP = ('', 9000)              # Own Feedback server IP

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
iCamPanel = None
iMainFrame = None
iTrackPanel = None