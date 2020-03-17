#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        cameraClient.py
#
# Purpose:     This module will create a camera firmware PATT checking function
#              
# Author:       Yuancheng Liu
#
# Created:     2020/03/16
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import io
import time
import cv2
import socket
import struct
import pickle

import udpCom
UDP_PORT = 5005

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class camClient(object):
    def __init__(self):
        self.server = udpCom.udpServer(None, UDP_PORT)
        self.cam = cv2.VideoCapture(0)
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        self.setResolution(640, 480)

#-----------------------------------------------------------------------------
    def run(self):
        print("Server thread run() start.")
        self.server.serverStart(handler=self.msgHandler)
        print("Server thread run() end.")

#-----------------------------------------------------------------------------
    def setResolution(self, w, h):
        self.cam.set(3, w//2)
        self.cam.set(4, h//2)

#-----------------------------------------------------------------------------
    def msgHandler(self, msg):
        """ The test handler method passed into the UDP server to handle the 
            incoming messages.
        """
        print("Incomming message: %s" % str(msg))
        _, frame = self.cam.read()
        data = pickle.dumps(frame, 0)
        size = len(data)
        print(size)
        msg = struct.pack(">L", size) + data
        return msg

#-----------------------------------------------------------------------------
    def termiate(self):
        self.cam.release()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    cam = camClient()
    cam.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()

