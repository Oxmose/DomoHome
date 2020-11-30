#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import os
import onionGpio
import CONSTANTS
import subprocess

from flask     import Flask, request, render_template, jsonify
from flask_api import status

####################################
# SERVER STATE VARIALBES
####################################
serverSettings = {'tempUnit': CONSTANTS.TEMPERATURE_UNIT_C, 
                  'tempSensorGPIO': 0, 
                  'openweatherKey': '5f6f9ed658e35a4409a32bfb0271d32c',
				  'openweatherId': '6077243'
}

remoteClients = {}
linkedObj     = {}

# Sensors 
tempSensor = {}

# We have to keep the Flask servAPP as global var
servApp = Flask(__name__)

####################################
# ROUTES
####################################
@servApp.route('/')
@servApp.route('/dash')
def indexId():
    return render_template("index.html", display=0)

@servApp.route('/switches')
def switchesDisplay():
    return render_template("index.html", display=1)

# api.openweathermap.org/data/2.5/weather?id=6077243&appid=5f6f9ed658e35a4409a32bfb0271d32c

####################################
# REST API
####################################
''' Set the server settings '''
@servApp.route('/getSettings')
def getSettings():
    global serverSettings
    return jsonify(error=0, settings=serverSettings)
    
''' Set the current temperature unit '''
@servApp.route('/setTempUnit/<int:unit>')
def setTempUnit(unit):
    global serverSettings

    if(unit == CONSTANTS.TEMPERATURE_UNIT_C):
        serverSettings['tempUnit'] = CONSTANTS.TEMPERATURE_UNIT_C
    else:
        serverSettings['tempUnit'] = CONSTANTS.TEMPERATURE_UNIT_F 

    saveSettings()
    return jsonify(error=0)

''' Reboot '''
@servApp.route('/reboot')
def reboot():
    rebootServer()
    return jsonify(error=0)
    
''' Get the current environment data '''
@servApp.route('/getEnv')
def getEnv():
    proc = subprocess.Popen(['./checkHumidity ' + str(serverSettings['tempSensorGPIO']) + ' DHT22'], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    sensor_data = out.split('\n')
    return jsonify(temp=sensor_data[1], humidity=sensor_data[0], unit=serverSettings['tempUnit'], error=0)
    
####################################
# INTERNAL
####################################

def loadObjects():
    global linkedObj
    global remoteClients

    remoteClients.clear()
    linkedObj.clear()
    try:
        f = open('objects.json')
        objects = json.loads(f.read())
        for key in objects:
            if(key in linkedObj or key in remoteClients):
                print("Duplicate object id " + str(key))
                exit(-1)

            obj = objects[key]

            if(obj['type'] == CONSTANTS.OBJ_TYPE_SWITCH or obj['type'] == CONSTANTS.OBJ_TYPE_PWM or obj['type'] == CONSTANTS.OBJ_TYPE_RGB):
                linkedObj[key] = {'type': obj['type'], 'name': obj['name'], 'state': obj['lastState'], 'value': obj['value'], 'gpio': obj['gpio']}
            elif(obj['type'] == CONSTANTS.OBJ_TYPE_REM_PWM or obj['type'] == CONSTANTS.OBJ_TYPE_REM_RGB):
                linkedObj[key] = {'type': obj['type'], 'name': obj['name'], 'state': obj['lastState'], 'value': obj['value'], 'gpio': obj['gpio'], 'remoteClient': obj['remoteClientId']}
            elif(obj['type'] == CONSTANTS.OBJ_TYPE_REMOTE):
                remoteClients[key] = {'ip': obj['ip'], 'port': obj['port'], 'tempSensor': obj['tempSensor']}
            else:
                print("Unkonwn object type " + str(obj['type']))

        print("Loaded " + str(len(linkedObj)) + " objects")
        print("Loaded " + str(len(remoteClients)) + " remote client")
    except ValueError as e:
        print("ERROR " + e)
        exit(-1)
    except IOError as e:
        print("ERROR " + e.strerror)
        exit(-1)
    except Exception as e:     
        print("ERROR While reading object file " + str(e))
        exit(-1)

def updateObject(id):
    try:
        f = open('objects.json', 'r', encoding='utf-8')
        objects = json.loads(f.read())
        currObj = linkedObj[id]

        objects[id]['type'] = currObj['type']
        objects[id]['name'] = currObj['name']
        objects[id]['lastState'] = currObj['state']
        objects[id]['value'] = currObj['value']
        objects[id]['gpio'] = currObj['gpio']
        if('remoteClient' in currObj):
            objects[id]['remoteClientId'] = currObj['remoteClient']

        f2 = open('objects.json_tmp', 'w', encoding='utf-8')
        json.dump(objects, f2, indent=4)

        f.close()
        f2.close()
        os.remove('objects.json')
        os.rename('objects.json_tmp', 'objects.json')

        return 0
    except ValueError as e:
        print("ERROR " + str(e))
        return 1
    except IOError as e:
        print("ERROR " + e.strerror)
        return 1
    except Exception as e:     
        print("ERROR While reading object file " + str(e))
        return 1

def loadSettings():
    global serverSettings
    try:
        f = open('config.pak', encoding='utf-8')
        serverSettings = json.loads(f.read())
    except:     
        pass

def saveSettings():
    global serverSettings
    try:
        f = open('config.pak', 'w')
        json.dump(serverSettings, f)
    except:     
        pass
        
def initSensors():
	tempSensor = onionGpio.OnionGpio(serverSettings['tempSensorGPIO'])
	

####################################
# MAIN
####################################

def rebootServer():
    print("Loading data...")
    loadObjects()
    loadSettings()
    saveSettings()
    

if __name__ == '__main__': 
    rebootServer()
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")
    servApp.run(debug=True, host='0.0.0.0')
    