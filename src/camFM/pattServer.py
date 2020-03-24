#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        pattServer.py
#
# Purpose:     This module will create a PATT file checker program. It will 
#              send the PATT bytes check list to the client and compare the 
#              feedback PATT value.
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
FM_PATH = "firmwareSample" # Firmware path need to check.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class pattServer(object):
    def __init__(self, clientIP=None):
        """ Create a UDP server and feed back the checked file's PATT value 
            when the client connect to it.
            Init example: checker = pattServer(clientIP='127.0.0.1')
        """
        blockNum = 4
        # Init the PATT calculator.
        self.verifier = patt.pattChecker(blockNum, FM_PATH)
        # Init the communicate UDP client.
        if clientIP is None: clientIP = '127.0.0.1' 
        self.client = udpCom.udpClient((clientIP, UDP_PORT))

#-----------------------------------------------------------------------------
    def run(self):
        """ Calculate the local file's PATT value and send the check address 
            to the client program, the compare the feed back value.
        """
        # Call the get getAddrList() to generate the random address dynamically 
        addrStr = ';'.join([str(i) for i in self.verifier.getAddrList()])
        verifierChSm = self.verifier.getCheckSum()
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
    clientip = '127.0.0.1' if TEST_MD else "172.27.142.65"
    pattSer = pattServer(clientIP = clientip)
    pattSer.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()


