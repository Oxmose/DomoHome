
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import socket
import array
import struct

####################################
# SERVER STATE VARIALBES
####################################


####################################
# PACKETS DEFINITIONS
####################################
TEMPERATURE_REQ_ID = 0x2

PACKET_STRUCT = [0 for i in range(0, 20)]
####################################
# SERVER CLASS
####################################

class RemoteClientServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.5)
    
    def reqTemperature(self, ip, port):
        packet = PACKET_STRUCT
        packet[0] = TEMPERATURE_REQ_ID
        while(True):
            self.sendTo(ip, port, array.array('B',packet))
            data = 0.0
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