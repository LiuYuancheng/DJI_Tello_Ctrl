#-----------------------------------------------------------------------------
# Name:        telloGlobal.py
#
# Purpose:     This module is used as a Local config file to set constants and
#              global parameters which will be used in the other modules.
#              
# Author:      Yuancheng Liu
#
# Created:     2019/10/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------
import os

print("Current working directory is : %s" %str(os.getcwd()))
dirpath = os.path.dirname(__file__)
print("Current source code location : %s" % dirpath)

APP_NAME = 'DJI Tello Ctrl'

#------<IMAGES PATH>-------------------------------------------------------------
IMG_FD = 'img'
ICO_PATH = os.path.join(dirpath, IMG_FD, "telloIcon.ico")
# Vertial movement control:
YA_CMD_LIST = ('flip l', 'up', 'flip r', 'cw', 'down', 'ccw')
YA_PNG_LIST = (os.path.join(dirpath, IMG_FD, "flip_l.png"),
               os.path.join(dirpath, IMG_FD, "up.png"),
               os.path.join(dirpath, IMG_FD, "flip_r.png"),
               os.path.join(dirpath, IMG_FD, "cw.png"),
               os.path.join(dirpath, IMG_FD, "down.png"),
               os.path.join(dirpath, IMG_FD, "ccw.png"))
# Function movement control:
IN_CMD_LIST = ('takeoff', 'land', 'streamon', 'streamoff')
IN_PNG_LIST = (os.path.join(dirpath, IMG_FD, "takeoff.png"),
               os.path.join(dirpath, IMG_FD, "land.png"),
               os.path.join(dirpath, IMG_FD, "streamon.png"),
               os.path.join(dirpath, IMG_FD, "streamoff.png"))
# Horizontal movement control:
XA_CMD_LIST = ('flip f', 'forward', 'flip b', 'left', 'back', 'right')
XA_PNG_LIST = (os.path.join(dirpath, IMG_FD, "flip_f.png"),
               os.path.join(dirpath, IMG_FD, "forward.png"),
               os.path.join(dirpath, IMG_FD, "flip_b.png"),
               os.path.join(dirpath, IMG_FD, "left.png"),
               os.path.join(dirpath, IMG_FD, "back.png"),
               os.path.join(dirpath, IMG_FD, "right.png"))

# Track path record file:
TRACK_PATH = os.path.join(dirpath, "TrackPath.txt")
# Firmware file path: 
FIRM_FILE = os.path.join(dirpath, "esp_client", "esp_client.ino.generic.bin")
# PATT check sum record.
CHECKSUM_RCD = os.path.join(dirpath, "checkSumRecord.txt")

# Communication IP Port setting:
# Send Command & Receive Response: Tello IP: 192.168.10.1  UDP PORT:8889  <<-->>  PC/Mac/Mobile
# Receive Tello State: 192.168.10.1  ->>  PC/Mac/Mobile UDP Server: 0.0.0.0 UDP PORT:8890 
# Receive Tello Video Stream: Tello IP: 192.168.10.1  ->>  PC/Mac/Mobile UDP Server: 0.0.0.0 UDP PORT:11111 
CT_IP = ('192.168.10.1', 8889)  # Drone control IP 
VD_IP = ('0.0.0.0', 11111)      # UDP video stream server IP 
FB_IP = ('', 9000)              # Own Feedback server IP
ST_IP = ('', 8890)              # Drone Feed back server IP
SE_IP = ('0.0.0.0', 4000)       # Sensor server IP

# parameters used by PATT firmware attestation.
RANDOM_RANGE_MAX = 10000
RANDOM_RANGE_MIN = 1000
FULL_MEMORY_SIZE_NODE_MCU = 64
WORD_SIZE = 16
BOOT_LOADER_OFFSET = 256

#-------<GLOBAL PARAMTERS>-----------------------------------------------------
iCamPanel = None        # Camera display panel,
iDetailPanel = None     # Drone detail information panel.
iMainFrame = None       # Main UI frame.
iTrackPanel = None      # Track path control panel.
iSensorPanel = None     # Sensor control panel.
iSensorChecker = None   # Sensor firmware attestation. 