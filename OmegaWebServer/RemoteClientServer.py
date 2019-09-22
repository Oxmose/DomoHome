
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import socket
import array
import struct
import CONSTANTS

####################################
# SERVER STATE VARIALBES
####################################

####################################
# PACKETS DEFINITIONS
####################################

PACKET_STRUCT = [0 for i in range(0, 20)]

####################################
# SERVER CLASS
####################################

class RemoteClientServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.5)
    
    def reqTemperature(self, ip, port, unit):
        packet = PACKET_STRUCT
        packet[0] = CONSTANTS.TEMPERATURE_REQ_ID
        if(unit == CONSTANTS.TEMPERATURE_UNIT_C):
            packet[4] = CONSTANTS.TEMPERATURE_UNIT_C
        else:
            packet[4] = CONSTANTS.TEMPERATURE_UNIT_F

        data = 0.0
        for i in range(0, 5):
            self.sendTo(ip, port, array.array('B',packet))
            try:
                data = self.socket.recvfrom(20)
                tempFloat = list(data[0])[4:8]
                data = struct.unpack('f',  bytes(tempFloat))
                break
            except socket.timeout:
                pass
        
        return data

    def setRemotePWM(self, obj, server):
        packet = PACKET_STRUCT
        stateVal = 0 
        if(obj['state']):
            stateVal = 1
        packet[0] = CONSTANTS.PWM_REQ_ID
        packet[4] = obj['gpio']
        packet[5] = obj['value'] * stateVal
        sent = False
        for i in range(0, 5):
            self.sendTo(server['ip'], server['port'], array.array('B',packet))
            try:
                data = self.socket.recvfrom(20)
                returnType = list(data[0])[0]
                returnVal  = list(data[0])[1]
                if(returnType == CONSTANTS.RESPONSE_PACKET_TYPE and returnVal == 0):
                    sent = True
                    break
            except socket.timeout:
                pass
        
        if(sent):
            return 0
        else:
            return 1
    
    def sendTo(self, ip, port, buffer):
        self.socket.sendto(buffer, (ip, port))