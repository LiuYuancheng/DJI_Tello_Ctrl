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
# Vertial movement control:
YA_CMD_LIST = ('flip l', 'up', 'flip r', 'cw', 'down', 'ccw')
YA_PNG_LIST = ("".join([dirpath, "\\img\\flip_l.png"]),
               "".join([dirpath, "\\img\\up.png"]),
               "".join([dirpath, "\\img\\flip_r.png"]),
               "".join([dirpath, "\\img\\cw.png"]),
               "".join([dirpath, "\\img\\down.png"]),
               "".join([dirpath, "\\img\\ccw.png"]))
# Function movement control:
IN_CMD_LIST = ('takeoff', 'land', 'streamon', 'streamoff')
IN_PNG_LIST = ("".join([dirpath, "\\img\\takeoff.png"]),
               "".join([dirpath, "\\img\\land.png"]),
               "".join([dirpath, "\\img\\streamon.png"]),
               "".join([dirpath, "\\img\\streamoff.png"]),)
# Horizontal movement control:
XA_CMD_LIST = ('flip f', 'forward', 'flip b', 'left', 'back', 'right')
XA_PNG_LIST = ("".join([dirpath, "\\img\\flip_f.png"]),
               "".join([dirpath, "\\img\\forward.png"]),
               "".join([dirpath, "\\img\\flip_b.png"]),
               "".join([dirpath, "\\img\\left.png"]),
               "".join([dirpath, "\\img\\back.png"]),
               "".join([dirpath, "\\img\\right.png"]))

# Track path record file:
TRACK_PATH = "".join([dirpath, "\\TrackPath.txt"])
# Firmware file path: 
FIRM_FILE_NAME = "".join([dirpath, "\\firmware.hex"])
# PATT check sum record.
CHECKSUM_RCD = "".join([dirpath, "\\checkSumRecord.txt"])

# Communication IP Port setting:
# Send Command & Receive Response: Tello IP: 192.168.10.1  UDP PORT:8889  <<-->>  PC/Mac/Mobile
# Receive Tello State: 192.168.10.1  ->>  PC/Mac/Mobile UDP Server: 0.0.0.0 UDP PORT:8890 
# Receive Tello Video Stream: Tello IP: 192.168.10.1  ->>  PC/Mac/Mobile UDP Server: 0.0.0.0 UDP PORT:11111 
CT_IP = ('192.168.10.1', 8889)  # Drone control IP 
VD_IP = ('0.0.0.0', 11111)      # UDP video stream server IP 
FB_IP = ('', 9000)              # Own Feedback server IP
ST_IP = ('', 8890)              # Drone Feed back server
SE_IP = ('0.0.0.0', 4000)       # Sensor server IP

# parameters used by PATT firmware attestation.
RANDOM_RANGE_MAX = 10000
RANDOM_RANGE_MIN = 1000
FULL_MEMORY_SIZE_NODE_MCU = 64
WORD_SIZE = 16
BOOT_LOADER_OFFSET = 256

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
iCamPanel = None        # Camera display panel
iDetailPanel = None     # Drone detail information panel.
iMainFrame = None       # Main UI frame.
iTrackPanel = None      # Track control panel.
iSensorPanel = None     # Sensor control panel.
iSensorChecker = None   # Sensor firmware attestation. 
iAddressList = []       # Sensor memory address list check.