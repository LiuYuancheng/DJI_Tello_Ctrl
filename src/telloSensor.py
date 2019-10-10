#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        telloSensor.py
#
# Purpose:     This function is used to create a tcp server to connect to receive 
#              the sensor height data and do the PATT attestation. 
#              
# Author:      Sombuddha Chakrava, Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import socket
import threading
import time
import random
from datetime import datetime
import telloGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloSensor(threading.Thread):
    """ TCP server thread.""" 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False
        self.verifier_checksum = None   # checkSum from local firmware
        self.sensor_checksum = None     # checkSum from the sensor feedback
        self.attitude = None            # sensor reading.
        self.seedVal = None             # random seed.
        self.checkSumfh = None          # filehandler to record the checksum.
        self.iterTime = -1              # Patt iteration time.
        self.blockNum = 1               # memory block size.
        self.stated = 'unsafe'
        # Init TCP communication channel:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(gv.SE_IP)
            self.sock.listen(1)
            self.conn = None
        except:
            print("telloSensor  : TCP socket init error")
            exit()
            raise
        
#-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            # Add the reconnection handling
            self.conn, addr = self.sock.accept()
            print('Connection address:'+str(addr))
            while not self.terminate:
                if self.iterTime > 0:
                    self.checkSumfh = open("checkSumRecord.txt", 'a')
                    self.checkSumfh.write("checksum record: \n")
                    self.getCheckSum(self.blockNum)
                    self.checkSumfh.close()
                else:
                    self.attitude = self.getDistance()
                    if not self.attitude: break
                    print(self.attitude)
                # update the UI.
                self.updateSensorUI()
        print("TCP server terminat.")

#-----------------------------------------------------------------------------
    def getDistance(self):
        """ Get the distance reading from the sensor."""
        if self.conn:
            print('telloSensor  : send distance request.')
            self.conn.sendall(b'-1')
            return self.conn.recv(1024)

#-----------------------------------------------------------------------------
    def getCheckSum(self, number_of_blocks):
        """ Get the local firmware checkSum and the sensor feed back checkSum."""
        # Get the random memory address.
        s_b_and_s_w = self._generate_sb_and_sw()
        self.seedVal = seed_value = "Sb: %s, Sw %s" % (
            hex(s_b_and_s_w[0]), hex(s_b_and_s_w[1]))
        print("telloSensor  : seed val: %s" % seed_value)
        rhos = self._generate_random_block_select_list(
            s_b_and_s_w[0], s_b_and_s_w[1], number_of_blocks)
        address_list = self._generate_all_address(
            s_b_and_s_w[1], rhos, number_of_blocks)
        # Get the firmware from the local pre-saved firmware.
        self.verifier_checksum = self._calculate_sigma_star(address_list)
        print("telloSensor : verifier check sum %s" %
              str(self.verifier_checksum))
        # Connect to the sensor to get the firmware check sum.
        self.sensor_checksum = self.getSensorCheckSum(address_list)
        print("telloSensor : sensor check sum %s" %
              str(self.verifier_checksum))
        self.checkSumfh.write(str(self.verifier_checksum)+"\n")
        self.checkSumfh.write(str(self.sensor_checksum) + "\n")
        if str(self.verifier_checksum) != str(self.sensor_checksum):
            print("The check sum are different.")
            self.iterTime = -1
            self.stated = 'unsafe'
        else:
            print("The check sum are same.")
            self.iterTime -= 1
            self.stated = 'safe'

#-----------------------------------------------------------------------------
    def getSensorCheckSum(self, address_list):
        """ Connect to the sensor and get the check sum."""
        sigma = ''
        for address in address_list:
            self.conn, _ = self.sock.accept()
            if self.conn:
                self.conn.sendall(str(address).encode('utf-8'))
                ch = self.conn.recv(1024).decode('utf-8')
                if ch != '' and ("," in ch) and (len(ch.split(',')[0]) == 2):
                    sigma = sigma + ch.split(',')[0].upper()
                    self.attitude = ch.split(',')[1]
        return sigma

#-----------------------------------------------------------------------------
    def _calculate_sigma_star(self, address_list):
        """ Load the local firmware sample and calculate the PATT check sum."""
        sigma_star = ""
        f = open(gv.FILE_NAME, "r")
        line_list = f.readlines()
        for address in address_list:
            #print ("Address: %s" % address)
            idx = address % gv.WORD_SIZE
            line = line_list[address//gv.WORD_SIZE]
            sigma_star = sigma_star + line[(idx*2)] + line[(idx*2) + 1]
        print ("Stored sigma: %s" % sigma_star)
        f.close()
        return sigma_star

#-----------------------------------------------------------------------------
    def _generate_sb_and_sw(self):
        """ Cenerate sb and sw LYC: (what are sb and sw stand for?)"""
        random.seed(datetime.now())
        return [random.randint(gv.RANDOM_RANGE_MIN, gv.RANDOM_RANGE_MAX) for i in range(2)]

#-----------------------------------------------------------------------------
    def _generate_random_block_select_list(self, s_b, s_w, number_of_blocks):
        """ Return a list of unduplicate number in [1, number_of_blocks]"""
        random.seed(s_b ^ s_w)
        return random.sample(range(1, number_of_blocks+1), number_of_blocks)

#-----------------------------------------------------------------------------
    def _generate_all_address(self, s_w, rhos, number_of_blocks):
        """ generate the randome memory address PATT need to check.
        """
        number_of_words = int(gv.FULL_MEMORY_SIZE_NODE_MCU // number_of_blocks)
        all_address_list = list()
        for rho in rhos:
            beta_list = self._generate_beta_list_for_block(
                s_w, rho, number_of_words)
            for line, beta in enumerate(beta_list):
                address = (gv.BOOT_LOADER_OFFSET + line + (rho-1)
                           * number_of_words) * gv.WORD_SIZE + beta
                all_address_list.append(address)
        return all_address_list

#-----------------------------------------------------------------------------
    def _generate_beta_list_for_block(self, s_w, rho, number_of_words):
        random.seed(rho ^ s_w)
        beta_list = [random.randint(0, gv.WORD_SIZE - 1) for _ in range(number_of_words)]
        return beta_list

#-----------------------------------------------------------------------------
    def setPattParameter(self, iterNum, blockNum):
        """ set the PATT parameters (int, int) """ 
        self.iterTime = int(iterNum)
        self.blockNum = int(blockNum)

#-----------------------------------------------------------------------------
    def updateSensorUI(self):
        """ Update the sensor panel in the main UI."""
        if gv.iSensorPanel:
            dataSet = (self.iterTime,
                       self.seedVal,
                       self.stated,
                       self.sensor_checksum,
                       self.verifier_checksum,
                       self.attitude)
        gv.iSensorPanel.updateInfo(dataSet)

#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True
        if self.conn: self.conn.close()
