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
BUFFER_SZ = 4096

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class camClient(object):
    def __init__(self):
        self.server = udpCom.udpServer(None, UDP_PORT)
        #self.cam = cv2.VideoCapture(0)
        self.cam = cv2.VideoCapture('my_video.h264') #play back the presave the video.
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        self.setResolution(640, 480)
        self.data = None # image data.

#-----------------------------------------------------------------------------
    def run(self):
        print("Server thread run() start.")
        self.server.serverStart(handler=self.msgHandler)
        print("Server thread run() end.")

#-----------------------------------------------------------------------------
    def setResolution(self, w, h):
        self.cam.set(3, w)
        self.cam.set(4, h)

#-----------------------------------------------------------------------------
    def msgHandler(self, msg):
        """ The test handler method passed into the UDP server to handle the 
            incoming messages.
        """
        #print("Incomming message: %s" % str(msg))
        if msg == b'new':
            # read a new camera image data.
            _, image = self.cam.read()
            result, frame = cv2.imencode('.jpg', image, self.encode_param)
            self.data = pickle.dumps(frame, 0)
            size = len(self.data)
            msg = str(size)
        else:
            if len(self.data) > BUFFER_SZ:
                msg = self.data[:BUFFER_SZ]
                self.data = self.data[BUFFER_SZ:]
            else:
                msg = self.data
            print(len(msg))
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

