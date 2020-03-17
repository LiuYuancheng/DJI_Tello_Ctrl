#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        pattChecker.py
#
# Purpose:     This module will create a camera firmware PATT checking function
#              
# Author:       Yuancheng Liu
#
# Created:     2020/03/16
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import random
from datetime import datetime

# parameters used by PATT firmware attestation.
RANDOM_RANGE_MAX = 10000
RANDOM_RANGE_MIN = 1000
FULL_MEMORY_SIZE_NODE_MCU = 64
WORD_SIZE = 16
BOOT_LOADER_OFFSET = 256

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class pattChecker(object):
    """ Patt firmware attestation checker""" 
    def __init__(self, blockNum, fmPath):
        self.checkSumfh = None      # filehandler to record the checksum.
        self.blockNum = blockNum    # memory block size.
        self.fmPath = fmPath        # Firmware path
        self.addrList= []           # PATT memory address

#-----------------------------------------------------------------------------
    def getAddrList(self):
        """ Return the PATT random memory address.
        """
        [sb, sw] = self._generate_sb_and_sw()
        rhos = self._generate_random_block_select_list(sb, sw, self.blockNum)
        self.addrList = self._generate_all_address(sw, rhos, self.blockNum)
        return self.addrList

#-----------------------------------------------------------------------------
    def getCheckSum(self, address_list=None):
        """ Get the local firmware checkSum and the sensor feed back checkSum."""
        # Get the firmware from the local pre-saved firmware.
        if not (address_list is None): self.addrList = address_list
        if len(self.addrList) == 0:  return None 
        verifier_checksum = self._calculate_sigma_star(self.addrList, self.fmPath)
        print("firmware sum %s" %str(verifier_checksum))
        return str(verifier_checksum)

#-----------------------------------------------------------------------------
    def _calculate_sigma_star(self, address_list, firmwFile):
        """ Load the local firmware sample and calculate the PATT check sum."""
        sigma_star = ""
        with open(firmwFile, "rb") as fh:
            bytesData = fh.read()
            for address in address_list:
                sigma_star = sigma_star + bytesData[address:address+1].hex()
        return str(sigma_star).upper()

#-----------------------------------------------------------------------------
    def _generate_sb_and_sw(self):
        """ Cenerate sb and sw LYC: (what are sb and sw stand for?)"""
        random.seed(datetime.now())
        return [random.randint(RANDOM_RANGE_MIN, RANDOM_RANGE_MAX) for i in range(2)]

#-----------------------------------------------------------------------------
    def _generate_random_block_select_list(self, s_b, s_w, number_of_blocks):
        """ Return a list of unduplicate number in [1, number_of_blocks]"""
        random.seed(s_b ^ s_w)
        return random.sample(range(1, number_of_blocks+1), number_of_blocks)

#-----------------------------------------------------------------------------
    def _generate_all_address(self, s_w, rhos, number_of_blocks):
        """ generate the randome memory address PATT need to check.
        """
        number_of_words = int(FULL_MEMORY_SIZE_NODE_MCU // number_of_blocks)
        all_address_list = list()
        for rho in rhos:
            beta_list = self._generate_beta_list_for_block(
                s_w, rho, number_of_words)
            for line, beta in enumerate(beta_list):
                address = (BOOT_LOADER_OFFSET + line + (rho-1)
                           * number_of_words) * WORD_SIZE + beta
                all_address_list.append(address)
        return all_address_list

#-----------------------------------------------------------------------------
    def _generate_beta_list_for_block(self, s_w, rho, number_of_words):
        random.seed(rho ^ s_w)
        beta_list = [random.randint(0, WORD_SIZE - 1) for _ in range(number_of_words)]
        return beta_list


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def testCase():
    print("Start the PATT test : ")
    # Empty address list calculation test:
    tester = pattChecker(4, 'firmwareSample')
    if tester.getCheckSum() == None:
        print("Empty address last calcuation test pass.")
    else:
        print("Empty address last calcuation test Fail.")
    # Verifier check test
    verifier = pattChecker(4, 'firmwareSample')
    addrList = verifier.getAddrList()
    verifierChSm = verifier.getCheckSum()
    testChSm = tester.getCheckSum(address_list=addrList)
    if verifierChSm == testChSm:
        print("PATT attestation calcuation test pass.")
    else:
        print("PATT attestation calcuation test Fail.")

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    testCase()

