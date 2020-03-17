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

import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import zlib


import udpCom
# image transfer : https://gist.github.com/kittinan/e7ecefddda5616eab2765fdb2affed1b
# motion detection: geeksforgeeks.org/webcam-motion-detector-python/

HOST=''
UDP_PORT = 5005

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class camServer(object):
    def __init__(self):
        self.payload_size = struct.calcsize(">L")
        self.client = udpCom.udpClient(('172.27.142.65', UDP_PORT))
        self.motion_list = [ None, None ] 
        self.termiate = False

    def run(self):
        data = b""
        while not self.termiate:
            while len(data) < self.payload_size:
                result = self.client.sendMsg(b'img', resp=True)
                data += result
            packed_msg_size = data[:self.payload_size]
            data = data[self.payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            frame_data = data[:msg_size]
            data = data[msg_size:]
            try:
                frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                self.tgtDect(frame)
            except:
                print("incomming image error")

    def tgtDect(self, frame):
        motion = 0
        # Converting color image to gray_scale image 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    
        # Converting gray scale image to GaussianBlur  
        # so that change can be find easily 
        gray = cv2.GaussianBlur(gray, (21, 21), 0) 
    
        # In first iteration we assign the value  
        # of static_back to our first frame 
        if static_back is None: 
            static_back = gray
            return

        # Difference between static background  
        # and current frame(which is GaussianBlur) 
        diff_frame = cv2.absdiff(static_back, gray) 
    
        # If change in between static background and 
        # current frame is greater than 30 it will show white color(255) 
        thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1] 
        thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2) 
    
        # Finding contour of moving object 
        cnts, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    
        for contour in cnts: 
            if cv2.contourArea(contour) < 10000: 
                return
            motion = 1
    
            (x, y, w, h) = cv2.boundingRect(contour) 
            # making green rectangle arround the moving object 
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) 
    
        # Appending status of motion 
        self.motion_list.append(motion) 
        self.motion_list = self.motion_list[-2:] 
        cv2.imshow('ImageWindow',frame)
        cv2.waitKey(1)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    cam = camServer()
    cam.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()


