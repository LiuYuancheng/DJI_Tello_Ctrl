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
class pattServer(object):
    def __init__(self):
        self.verifier = patt.pattChecker(4, 'firmwareSample')
        #self.client = udpCom.udpClient(('172.27.142.65', UDP_PORT))
        self.client = udpCom.udpClient(('127.0.0.1', UDP_PORT))

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
            print('The camera firmware attestation successful')

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    pattSer = pattServer()
    pattSer.run()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()


