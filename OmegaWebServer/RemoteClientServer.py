
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
    
    def sendTo(self, ip, port, buffer):
        self.socket.sendto(buffer, (ip, port))