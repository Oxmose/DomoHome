#! /usr/bin/python
# -*- coding:utf-8 -*-

RESPONSE_PACKET_TYPE = 0x2

TEMPERATURE_REQ_ID = 0x2
TEMPERATURE_UNIT_C = 0
TEMPERATURE_UNIT_F = 1

PWM_REQ_ID = 0x4
RGB_REQ_ID = 0x5

# Types contsants
OBJ_TYPE_SWITCH  = 0
OBJ_TYPE_PWM     = 1
OBJ_TYPE_RGB     = 2
OBJ_TYPE_REM_PWM = 3
OBJ_TYPE_REM_RGB = 4
OBJ_TYPE_REMOTE  = 5