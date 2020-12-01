
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################
import onionGpio


####################################
# MANAGER CLASS
####################################
class InternalObjectManager:
	
	def setSwitch(self, gpio, value):
		if(value != 0):
			value = 1
			
		hwGpio = onionGpio.OnionGpio(gpio)
		hwGpio.setOutputDirection(value)