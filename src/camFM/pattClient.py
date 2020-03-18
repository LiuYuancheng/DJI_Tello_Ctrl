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

import udpCom
import pattChecker as patt

UDP_PORT = 5006

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class pattClient(object):
    def __init__(self):
        self.tester = patt.pattChecker(4, 'firmwareSample')
        self.server = udpCom.udpServer(None, UDP_PORT)

    #-----------------------------------------------------------------------------
    def run(self):
        print("Server thread run() start.")
        self.server.serverStart(handler=self.msgHandler)
        print("Server thread run() end.")

    #-----------------------------------------------------------------------------
    def msgHandler(self, msg):
        """ The test handler method passed into the UDP server to handle the 
            incoming messages.
        """
        print("Incomming message: %s" % str(msg))
        addrList = msg.decode('utf-8').split(';')
        testChSm = self.tester.getCheckSum(address_list=[int(i) for i in addrList])
        return testChSm


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    cam = pattClient()
    cam.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()



