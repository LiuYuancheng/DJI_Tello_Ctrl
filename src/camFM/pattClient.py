#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        pattClient.py
#
# Purpose:     This module create a file PATT check client and feed back the 
#              PATT value when the server connect to it.
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
    def __init__(self, filePath=None):
        """ Create a UDP server and feed back the checked file's PATT value 
            when the client connect to it.
            Init example: checker = pattClient(filePath='firmwareSample')
        """
        blockNum = 4
        self.tester = patt.pattChecker(blockNum, filePath)
        self.server = udpCom.udpServer(None, UDP_PORT)

    #-----------------------------------------------------------------------------
    def run(self):
        print("PATT checker client run() start.")
        self.server.serverStart(handler=self.msgHandler)
        print("PATT checker client run() end.")

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
    checker = pattClient(filePath='firmwareSample')
    checker.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()



