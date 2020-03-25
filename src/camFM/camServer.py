#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        cameraServer.py
#
# Purpose:     This module will create a camera viewer server to connect to the 
#              <camClient> by UDP client, get the camera video and do the motion 
#              detection and simple target tracking.
#              
# Author:       Yuancheng Liu
#
# Created:     2020/03/16
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import sys
import math
import time
import socket
import pickle

import cv2
import numpy as np
import udpCom
# image transfer : https://gist.github.com/kittinan/e7ecefddda5616eab2765fdb2affed1b

UDP_PORT = 5005
BUFFER_SZ = udpCom.BUFFER_SZ
CONFIG_FILE = 'camServerConfig.txt'

TEST_MD = True  # test mode flag
FRAME_RT = 10   # camera frame rate

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class camServer(object):
    def __init__(self, camIP):
        """ Init the image fetch UDP client and motion detection handler.
            Init example : cam = camServer(camIP='172.27.142.65')
        """
        self.client = udpCom.udpClient((camIP, UDP_PORT))
        self.staticBack = None
        self.diffLvl = 30       # Motion changed level which will be detected.(smaller->sensitive)
        self.contourIgnRng = (400, 10000) # contour ingore range. target not in range will be ingnored.
        self.termiate = False   # program terminate flag
        self.showDiff = False   # flag to whether to show the difference frame.
        self.frameRate = 10     

#-----------------------------------------------------------------------------
    def run(self):
        """ main loop to fetch image bytes from the camera client."""
        imgData = b'' # imagedata
        while not self.termiate:
            # get a new image from the camera
            imgData = b''
            result = self.client.sendMsg(b'new', resp=True)
            imgSz = int(result.decode('utf-8'))
            rcvIterN = math.ceil(imgSz/float(BUFFER_SZ)) #iteration time to receive one img.
            print('Next image size: %s' %str(imgSz))
            for _ in range(int(rcvIterN)):
                imgData += self.client.sendMsg(b'img', resp=True)
            # Check whether the image size is same as the sent one.
            if imgSz != len(imgData):
                print("Error: some image byte lose!")
                continue
            frame = cv2.imdecode(pickle.loads(
                imgData, fix_imports=True, encoding="bytes"), cv2.IMREAD_COLOR)
            self.detectTgt(frame)
            # if q entered whole process will stop 
            if cv2.waitKey(1) == ord('q'):
                self.termiate = True 
            time.sleep(1/FRAME_RT)
        # Destroying all the windows when user quit.        
        cv2.destroyAllWindows() 

#-----------------------------------------------------------------------------
    def detectTgt(self, frame):
        """ Motion detection and target tracking function. Result will show in 
            opencv default window.
            reference: https://www.geeksforgeeks.org/webcam-motion-detector-python/
        """
        # Converting colour image to gray_scale image.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        # Converting gray scale image to GaussianBlur.
        gray = cv2.GaussianBlur(gray, (21, 21), 0) 
        # In first iteration we assign the value of staticBack to our first frame.
        if self.staticBack is None: 
            self.staticBack = gray # use the first image as a reference.
            return
        # Difference between static background and current frame (which is GaussianBlur) 
        diffFrame = cv2.absdiff(self.staticBack, gray) 
        # If change in between static background and current frame is greater than 30 
        # it will show white color(255).
        threshFrame = cv2.threshold(diffFrame, self.diffLvl, 255, cv2.THRESH_BINARY)[1] 
        threshFrame = cv2.dilate(threshFrame, None, iterations = 2) 
        # Finding contour of moving object.
        cnts, _ = cv2.findContours(threshFrame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        # old opencv version use the below line:
        # _, cnts, _ = cv2.findContours(threshFrame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        for contour in cnts: 
            if self.contourIgnRng[0]< cv2.contourArea(contour) < self.contourIgnRng[1]:
                (x, y, w, h) = cv2.boundingRect(contour) 
                # Making green rectangles around the moving object.
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) 
        # Show the difference compare frame or the detection tracking frame.
        if self.showDiff:
            cv2.imshow('Different Gray-Scale Image',diffFrame)
        else:
            cv2.imshow('Target Detection Image',frame)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    camIp = '127.0.0.1' if TEST_MD else '172.27.142.65'
    cam = camServer(camIp)
    cam.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()


