
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
		# Init the PWM controller
		self.pwmCont = PCA9685()
		self.pwmCont.set_pwm_freq(255);
	
	def setSwitch(self, gpio, value):
		if(value != 0):
			value = 1
			
		hwGpio = onionGpio.OnionGpio(gpio)
		hwGpio.setOutputDirection(value)
		
	def setPWM(self, gpio, value):
		self.pwmCont.set_pwm(gpio, 0, value)