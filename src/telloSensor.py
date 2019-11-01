#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        telloSensor.py
#
# Purpose:     This module is used to create a tcp communication server to receive 
#              the Arduino_ESP8266 height data and do the PATT attestation. 
#              
# Author:      Sombuddha Chakrava, Yuancheng Liu
#
# Created:     2019/10/04
# Copyright:   YC @ Singtel Cyber Security Research & Development Laboratory
# License:     YC
#-----------------------------------------------------------------------------

import time
import random
import socket
import threading

from datetime import datetime
import telloGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class telloSensor(threading.Thread):
    """ TCP server thread.""" 
    def __init__(self, threadID, name, clientMax):
        threading.Thread.__init__(self)
        self.terminate = False
        self.attitude = None            # sensor reading.
        self.checkSumfh = None          # filehandler to record the checksum.
        self.iterTime = -1              # Patt iteration time.
        self.blockNum = 1               # memory block size.
        self.stated = 'unsafe'
        # Init TCP communication channel:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(gv.SE_IP)
            self.sock.listen(clientMax)
            self.conn = None
        except:
            print("telloSensor  : TCP socket server init error.")
            exit()
            raise
        
#-----------------------------------------------------------------------------
    def run(self):
        """ main loop to communicate with the clients.(overwirte thread.run())"""
        while not self.terminate:
            self.conn, addr = self.sock.accept()
            if gv.iMainFrame: gv.iMainFrame.updateSenConn(True)
            print('Connection address:'+str(addr))
            while not self.terminate:
                if self.iterTime > 0:
                    if gv.iSensorPanel: gv.iSensorPanel.updateInfo(iterN=self.attitude)
                    self.checkSumfh = open("checkSumRecord.txt", 'a')
                    self.checkSumfh.write("checksum record [%s]: \n" %str(datetime.today()))
                    self.getCheckSum(self.blockNum)
                    self.checkSumfh.close()
                else:
                    self.attitude = self.getDistance()
                    if not self.attitude: break # client send Null and want to break the connection.
                    if gv.iSensorPanel: 
                        print("Sensor feedback data: %s" %str(self.attitude))
                        gv.iSensorPanel.updateInfo(alti=self.attitude)
            if gv.iMainFrame: gv.iMainFrame.updateSenConn(False)
            print("Sensor disconnected.")
        print("TCP server terminat.")

#-----------------------------------------------------------------------------
    def getDistance(self):
        """ Get the distance reading from the sensor."""
        if self.conn:
            print('telloSensor  : send distance request.')
            self.conn.sendall(b'-1')
            return self.conn.recv(1024).decode('utf-8')

#-----------------------------------------------------------------------------
    def getCheckSum(self, number_of_blocks):
        """ Get the local firmware checkSum and the sensor feed back checkSum."""
        # Get the random memory address.
        s_b_and_s_w = self._generate_sb_and_sw()
        seedVal = "Sb: %s, Sw %s" % (
            hex(s_b_and_s_w[0]), hex(s_b_and_s_w[1]))
        #print("telloSensor  : seed val: %s" % seed_value)
        if gv.iSensorPanel: gv.iSensorPanel.updateInfo(sead=seedVal)
        rhos = self._generate_random_block_select_list(
            s_b_and_s_w[0], s_b_and_s_w[1], number_of_blocks)
        address_list = self._generate_all_address(
            s_b_and_s_w[1], rhos, number_of_blocks)
        # Get the firmware from the local pre-saved firmware.
        verifier_checksum = self._calculate_sigma_star(address_list)
        if gv.iSensorPanel:  gv.iSensorPanel.updateChecksum(local=verifier_checksum)
        print("telloSensor : verifier check sum %s" %
              str(verifier_checksum))
        # Connect to the sensor to get the firmware check sum.
        sensor_checksum = self.getSensorCheckSum(address_list)
        print("telloSensor : sensor check sum %s" %
              str(verifier_checksum))
        # recort the check sum to local file.
        self.checkSumfh.write(str(verifier_checksum)+"\n")
        self.checkSumfh.write(str(sensor_checksum) + "\n")
        if str(verifier_checksum) != str(sensor_checksum):
            print("The check sum are different.")
            gv.iMainFrame.updateSenDis(False)
            self.stated = 'unsafe'
            self.iterTime = 0 # stop iteration if the attesation find unsafe.
        else:
            print("The check sum are same.")
            gv.iMainFrame.updateSenDis(True)
            self.stated = 'safe'
            self.iterTime -= 1 # decrease the iteration time for the next around.

#-----------------------------------------------------------------------------
    def getSensorCheckSum(self, address_list):
        """ Connect to the sensor and get the check sum."""
        sigma, listLen, timeU = '', len(address_list), time.time()
        if self.conn:
            self.conn.sendall(str(listLen).encode('utf-8'))
            self.attitude = self.conn.recv(1024).decode('utf-8')
            # Send all the addresses.
            self.conn.sendall(str(';'.join([str(i) for i in address_list])).encode('utf-8'))
            data = self.conn.recv(1024).decode('utf-8')
            if "," in data:
                ch, self.attitude = data.split(',')
                # print("Feed back checksum: %s" %str((ch)))
                sigma += ch.upper()
                # Update the display area.
                if gv.iSensorPanel: 
                    gv.iSensorPanel.updateChecksum(remote=ch.upper())
                    gv.iSensorPanel.updateInfo(iterN = self.iterTime, alti=self.attitude, timeU = str(time.time()-timeU))
                    gv.iSensorPanel.updateProgress(64, listLen)
        return sigma

#-----------------------------------------------------------------------------
    def _calculate_sigma_star(self, address_list):
        """ Load the local firmware sample and calculate the PATT check sum."""
        sigma_star = ""
        with open(gv.FIRM_FILE, "rb") as fh:
            bytesData = fh.read()
            for address in address_list:
                sigma_star = sigma_star + bytesData[address:address+1].hex()
        return str(sigma_star).upper()

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
    def stop(self):
        """ Stop the thread."""
        self.terminate = True
        if self.conn: self.conn.close()
        # Create a client to connect to the server to turnoff the server loop
        closeClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        closeClient.connect(('127.0.0.1', gv.SE_IP[1]))
        closeClient.close()

