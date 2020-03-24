#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        cameraClient.py
#
# Purpose:     This module will create a client program running on raspberry PI
#              to capture the camera image and feed the image back to connected
#              camera server.
#              
# Author:       Yuancheng Liu
#
# Created:     2020/03/16
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import io
import time
import socket
import struct
import pickle

import cv2
import udpCom

UDP_PORT = 5005
BUFFER_SZ = udpCom.BUFFER_SZ
TEST_MD = True # Test mode flag

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class camClient(object):
    def __init__(self, videoSrc=0):
        """ Init the UDP server and camera capture handler. Capture the default 
            camera idx=0 if no video src is provided.
            Init example : cam = camClient(videoSrc='VideoFilePath')
        """
        self.server = udpCom.udpServer(None, UDP_PORT)
        print("Capture video from src: %s" % str(videoSrc))
        self.cam = cv2.VideoCapture(videoSrc)
        self.encodeParam = [int(cv2.IMWRITE_JPEG_QUALITY), 90] # image encode parameter
        self.setResolution(640, 480)
        self.data = None # image data.

#-----------------------------------------------------------------------------
    def msgHandler(self, msg):
        """ Encode the image bytes and send to connected camera server.
            The image sending process: When the server asks the client to send 
            a new image, client sends the image size to the server, then cut 
            the image data based on the buffer size to several chunk, then send
            the chunk to the server one by one.
            server -> new image cmd -> client
            server <- image size <- client
            loop:   server -> image request -> client
                    server <- image data <- client
        """
        #print("Incomming message: %s" % str(msg))
        if msg == b'new':
            # read a new camera image data.
            _, image = self.cam.read()
            _, frame = cv2.imencode('.jpg', image, self.encodeParam)
            self.data = pickle.dumps(frame, 0)
            msg = str(len(self.data))   # Image size.
        else:
            if len(self.data) > BUFFER_SZ:
                msg = self.data[:BUFFER_SZ]
                self.data = self.data[BUFFER_SZ:]
            else:
                msg = self.data
        return msg

#-----------------------------------------------------------------------------
    def run(self):
        """ Main incomming message handle loop. """
        print("Camera client run() start.")
        self.server.serverStart(handler=self.msgHandler)
        print("Camera client run() end.")

#-----------------------------------------------------------------------------
    def setResolution(self, w, h):
        """ Set the feed back image resulotion. """
        self.cam.set(3, w)
        self.cam.set(4, h)

#-----------------------------------------------------------------------------
    def termiate(self):
        self.cam.release()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    # play back the pre-saved video if under test mode.
    videoSrc = 'my_video.h264' if TEST_MD else 0 
    cam = camClient(videoSrc=videoSrc)
    cam.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()

