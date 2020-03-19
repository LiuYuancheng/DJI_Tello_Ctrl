#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        pattServer.py
#
# Purpose:     This module will create a PATT file checker program
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
TEST_MD = True # test mode flag

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class pattServer(object):
    def __init__(self, clientIP):
        """ Create a UDP server and feed back the checked file's PATT value 
            when the client connect to it.
            Init example: checker = pattClient(filePath='firmwareSample')
        """
        blockNum = 4
        self.verifier = patt.pattChecker(blockNum, 'firmwareSample')
        #self.client = udpCom.udpClient(('172.27.142.65', UDP_PORT))
        self.client = udpCom.udpClient(('127.0.0.1', UDP_PORT))

#-----------------------------------------------------------------------------
    def run(self):
        addrList = self.verifier.getAddrList()
        verifierChSm = self.verifier.getCheckSum()
        addrStr = ';'.join([str(i) for i in addrList])
        result = self.client.sendMsg(addrStr, resp=True)
        print('Local_PATT: %s' %verifierChSm)
        print('CameraPATT: %s' %result.decode('utf-8'))
        if verifierChSm == result.decode('utf-8'):
            print('Patt check result: verifierChechsum == camreaCheckSum')
            print('The camera firmware attestation successful')
        else:
            print('Patt check result: verifierChechsum != camreaCheckSum')
            print('The camera firmware attestation fail.')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    clientip = '127.0.0.1' if TEST_MD else 172.27.142.65
    pattSer = pattServer(clientIP = clientip)
    pattSer.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()


