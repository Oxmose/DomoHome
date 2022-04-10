
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################
from gpiozero         import OutputDevice
from board            import SCL, SDA
from adafruit_pca9685 import PCA9685

import busio
import requests

####################################
# MANAGER CLASS
####################################
class InternalObjectManager:
    
    def __init__(self):
        self.pwmCtrl = PCA9685(busio.I2C(SCL, SDA))
        self.pwmCtrl.frequency = 200
        self.usedDevices = {}
        
    def setSwitch(self, obj, value):
        if(value != 0):
            value = 1
        else:
            # Useful is value is false and not an int
            value = 0

        # Check object location
        if(obj['node'] == "local"):       
            if(obj['gpio'] in self.usedDevices):
                if(value):
                    self.usedDevices[obj['gpio']].on()
                else: 
                    self.usedDevices[obj['gpio']].off()
            else:
                self.usedDevices[obj['gpio']] = OutputDevice(pin=obj['gpio'], initial_value=value)
        else:
            pload = {'gpio': str(obj['gpio']), 'value': str(value)}
            requests.get("http://" + obj['addr'] + "/setToggle", params=pload)
            
        
    def setPWM(self, obj, pulse):
        if(obj['gpio'] > 15):
            return
        elif(pulse > 100):
            pulse = 100 

        # Check object location
        if(obj['node'] == "local"): 
            dutyCycle = int(65535 * pulse / 100)      
            self.pwmCtrl.channels[obj['gpio']].duty_cycle = dutyCycle
        else:
            pload = {'gpio': str(obj['gpio']), 'value': str(pulse)}
            requests.get("http://" + obj['addr'] + "/setPWM", params=pload)

    def setRGB(self, obj, values):
        for i in range(0, 3):
            if(obj['gpio'][i] > 15):
                return           
        
            if(values[i] > 255):
                values[i] = 255

        if(obj['node'] == "local"): 
            for i in range(0, 3):
                pulse = values[i]
                dutyCycle = int(65535 * pulse / 100)      
                self.pwmCtrl.channels[obj['gpio'][i]].duty_cycle = dutyCycle
        else:
            pload = {
                'gpio': str(obj['gpio'][0]) + '_' + str(obj['gpio'][1]) + '_' + str(obj['gpio'][2]), 
                'value': str(values[0]) + '_' + str(values[1]) + '_' + str(values[2])}
            requests.get("http://" + obj['addr'] + "/setRGB", params=pload)