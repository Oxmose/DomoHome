
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import socket
import array
import struct
import CONSTANTS
import onionGpio

####################################
# MANAGER CLASS
####################################

class ObjectManager:
    def __init__(self):
        pass 

    def toggle(self, obj):
        val = 1
        if(obj['state'] == False):
            val = 0

        # Check if remote
        if(obj['type'] == CONSTANTS.OBJ_TYPE_REM_PWM or obj['type'] == CONSTANTS.OBJ_TYPE_REM_RGB):
            return
   
        if(isinstance(obj['gpio'], int)):
            gpio = onionGpio.OnionGpio(obj['gpio'])
            gpio.setOutputDirection(0)
            gpio.setValue(val * obj['value'])
        else:
            for i in range(0, len(obj['gpio'])):
                gpio = onionGpio.OnionGpio(obj['gpio'][i])
                gpio.setOutputDirection(0)
                gpio.setValue(val * obj['value'][i])



