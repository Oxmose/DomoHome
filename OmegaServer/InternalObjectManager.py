
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################
import onionGpio
from PCA9685 import PCA9685

####################################
# MANAGER CLASS
####################################
class InternalObjectManager:
    
    def __init__(self):
        self.pwmCtrl = PCA9685()
        self.pwmCtrl.set_pwm_freq(200)
        
    def setSwitch(self, gpio, value):
        if(value != 0):
            value = 1
            
        hwGpio = onionGpio.OnionGpio(gpio)
        hwGpio.setOutputDirection(value)
        
    def setPWM(self, channel, pulse):
        if(channel > 15):
            return;
        value = [0, 0]
        if(pulse == 0):
            value[0] = 0
            value[1] = 4096
        elif(pulse >= 100):
            value[0] = 4096
            value[1] = 0
        else:
            value[0] = 0
            value[1] = 4096 * pulse / 100
        
        self.pwmCtrl.set_pwm(channel, value[0], value[1])

