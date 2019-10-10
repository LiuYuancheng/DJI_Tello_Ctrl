#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        telloSensor.py
#
# Purpose:     This function is used to create a controller to control the DJI 
#              Tello Drone and connect to the height sensor.
#
# Author:      Yuancheng Liu
#
# Created:     2019/07/01
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import psutil
import socket
import threading
import time
import random
from datetime import datetime
import telloGlobal as gv

class telloSensor(threading.Thread):
    """ Add the TCP thread here: 
    """ 
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.terminate = False
        self.verifier_checksum = None
        self.sensor_checksum = None
        self.attitude = None
        self.iterTime = -1
        self.blockNum = 1
        self.seedVal = None
        # Show the netowrk
        for name in psutil.net_if_addrs().keys():
            if 'wlxe84e062bb806' in name:
                print("telloSensor  : network %s" %str(name))
                break
        
        # TCP communication channel:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(gv.SE_IP)
            self.sock.listen(1)
            self.conn = None
        except:
            print("telloSensor  : TCP socket init error")
            raise
        
#-----------------------------------------------------------------------------
    def run(self):
        while not self.terminate:
            # Add the reconnection handling 
            self.conn, addr = self.sock.accept()
            print('Connection address:'+str(addr))
            while not self.terminate:
                if self.iterTime > 0:
                    self.getCheckSum(self.blockNum )
                else:
                    data = self.getDistance()
                    if not data: break
                    print(data)
                gv.iSensorPanel.updateInfo((self.iterTime, self.seedVal, 'check', self.sensor_checksum, self.verifier_checksum, self.attitude))
        print("TCP server terminat.")

#-----------------------------------------------------------------------------
    def getDistance(self):
        """ Get the distance reading from the sensor.
        """
        if self.conn:
            self.conn.sendall(b'-1')
            return self.conn.recv(1024)

#-----------------------------------------------------------------------------
    def getCheckSum(self, number_of_blocks):
        s_b_and_s_w = self.generate_sb_and_sw()
        self.seedVal = seed_value = "Sb: %s, Sw %s" % (hex(s_b_and_s_w[0]), hex(s_b_and_s_w[1]))
        print("telloSensor  : seed val: %s" %seed_value)
        rhos = self.generate_random_block_select_list(s_b_and_s_w[0], s_b_and_s_w[1], number_of_blocks)
        address_list = self.generate_all_address(s_b_and_s_w[1], rhos, number_of_blocks)
        self.verifier_checksum = self.calculate_sigma_star(address_list) 
        print("telloSensor : verifier check sum %s" %str(self.verifier_checksum))
        self.sensor_checksum = self.getSensorCheckSum(address_list)
        print("telloSensor : sensor check sum %s" %str(self.verifier_checksum))
        if self.verifier_checksum != self.sensor_checksum:
            self.iterTime = -1

#-----------------------------------------------------------------------------
    def getSensorCheckSum(self, address_list):
        sigma = ''
        for address in address_list:
            if self.conn:
                self.conn.sendall(str(address).encode('utf-8'))
                ch = self.conn.recv(1024).decode('utf-8')
                if ch != '' and ("," in ch) and (len(ch.split(',')[0]) == 2):
                    sigma = sigma + ch.split(',')[0].upper()
                    self.attitude = ch.split(',')[1]
        return sigma

#-----------------------------------------------------------------------------
    def setPattParameter(self, iterNum, blockNum):
        self.iterTime = iterNum
        self.blockNum = blockNum

#-----------------------------------------------------------------------------
    def calculate_sigma_star(self, address_list):
        sigma_star = ""
        f = open(gv.FILE_NAME, "r")
        line_list = f.readlines()
        for address in address_list:
            #print ("Address: %s" % address)
            idx = address % gv.WORD_SIZE
            line = line_list[address/gv.WORD_SIZE]
            sigma_star = sigma_star + line[(idx*2)] + line[(idx*2) + 1]
        print ("Stored sigma: %s" % sigma_star)
        f.close()
        return sigma_star

#-----------------------------------------------------------------------------
    def generate_sb_and_sw(self):
        random.seed(datetime.now())
        return [random.randint(gv.RANDOM_RANGE_MIN, gv.RANDOM_RANGE_MAX) for i in range(2)]

#-----------------------------------------------------------------------------
    def generate_random_block_select_list(self, s_b, s_w, number_of_blocks):
        """ return a list of unduplicate number in [1, number_of_blocks]
        """
        random.seed(s_b ^ s_w)
        return random.sample(range(1, number_of_blocks+1), number_of_blocks)

#-----------------------------------------------------------------------------
    def generate_all_address(self, s_w, rhos, number_of_blocks):
        number_of_words = gv.FULL_MEMORY_SIZE_NODE_MCU / number_of_blocks
        all_address_list = list()
        for rho in rhos:
            beta_list = self.generate_beta_list_for_block(s_w, rho, number_of_words)
            for line, beta in enumerate(beta_list):
                address = (gv.BOOT_LOADER_OFFSET + line + (rho-1)* number_of_words) * gv.WORD_SIZE + beta
                all_address_list.append(address)
        return all_address_list

#-----------------------------------------------------------------------------
    def generate_beta_list_for_block(self, s_w, rho, number_of_words):
        random.seed(rho ^ s_w)
        beta_list = [random.randint(0, gv.WORD_SIZE - 1) for _ in range(number_of_words)]
        return beta_list

#-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True
        if self.conn: self.conn.close()