#-----------------------------------------------------------------------------
# Name:        globalVal.py
#
# Purpose:     This module is used set the Local config file as global value 
#              which will be used in the other modules.
# Author:      Yuancheng Liu
#
# Created:     2019/05/17
# Copyright:   NUS – Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------
import os

dirpath = os.getcwd()
print("testProute: Current working directory is : %s" %dirpath)

CLFM_FILE = os.path.join(dirpath,  "my_video.h264")
SEFM_FILE = os.path.join(dirpath,  "my_video.h264")


#-------<GLOBAL PARAMTERS>-----------------------------------------------------
SE_IP = ('0.0.0.0', 4000)       # Sensor server IP

# parameters used by PATT firmware attestation.
RANDOM_RANGE_MAX = 10000
RANDOM_RANGE_MIN = 1000
FULL_MEMORY_SIZE_NODE_MCU = 64
WORD_SIZE = 16
BOOT_LOADER_OFFSET = 256

iRouteHandler = None
iSensorThread = None