#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import CONSTANTS
import os

from flask     import Flask, request, render_template, jsonify
from flask_api import status

from RemoteClientServer import RemoteClientServer

####################################
# SERVER STATE VARIALBES
####################################
serverSettings = {'tempUnit': CONSTANTS.TEMPERATURE_UNIT_C}

remoteClients = {}
linkedObj     = {}

remoteClientServer = RemoteClientServer()

# We have to keep the Flask servAPP as global var
servApp = Flask(__name__)

####################################
# ROUTES
####################################

@servApp.route('/', defaults={'objid': 3})
@servApp.route('/<int:objid>')
def indexId(objid=3):
    return render_template("index.html", objId=objid)

####################################
# REST API
####################################

''' Set the server settings '''
@servApp.route('/getSettings')
def getSettings():
    global serverSettings
    return jsonify(error=0, settings=serverSettings)

''' Set the server object '''
@servApp.route('/getObjects')
def getObjects():
    global linkedObj
    return jsonify(error=0, objects=linkedObj)

''' Get the current temperature '''
@servApp.route('/getTemp')
def getTemp():
    readTemp = 0.0
    for client in remoteClients.values():
        if(client['tempSensor'] == True):
            readTemp = remoteClientServer.reqTemperature(client['ip'], client['port'], serverSettings['tempUnit'])
            break
        
    return jsonify(temp=readTemp, unit=serverSettings['tempUnit'], error=0)

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
    
''' Toggle object '''
@servApp.route('/toggle/<id>/')
def toggle(id):
    if(not str(id) in linkedObj):
        return jsonify(error=1)
 
    linkedObj[id]['state'] = not linkedObj[id]['state']
    if(updateObject(id) != 0):
        linkedObj[id]['state'] = not linkedObj[id]['state']
        return jsonify(error=2)

    if(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_SWITCH):
        pass
    elif(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_PWM):
        pass 
    elif(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_RGB):
        pass
    elif(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_REM_PWM):
        return setPWM(id, linkedObj[id]['value'])
    elif(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_REM_RGB):
        pass
    else:
        return jsonify(error=3)

    return jsonify(error=0)

''' Set PWM object '''
@servApp.route('/pwm/<id>/<int:value>')
def setPWM(id, value):
    if(not str(id) in linkedObj):
        return jsonify(error=1)
    if(value < 0 or value > 255):
        return jsonify(error=2)
 
    # TODO Check for PWM

    oldValue = linkedObj[id]['value']
    linkedObj[id]['value'] = value
    if(updateObject(id) != 0):
        linkedObj[id]['value'] = oldValue
        return jsonify(error=3)

    # Check if remote
    if(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_REM_PWM):
        if(not linkedObj[id]['remoteClient'] in remoteClients):
            return jsonify(error=4)
        return jsonify(error=remoteClientServer.setRemotePWM(linkedObj[id], remoteClients[linkedObj[id]['remoteClient']]))
    elif(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_PWM):
        pass # TODO
    else:
        return jsonify(error=5)

    return jsonify(error=6)

''' Set RGB object '''
@servApp.route('/rgb/<id>/<int:value>')
def setRGB(id, value):
    if(not str(id) in linkedObj):
        return jsonify(error=1)
    red   = (value & 0x00FF0000) >> 16
    green = (value & 0x0000FF00) >> 8
    blue  = value & 0x000000FF

    # TODO Check for RGB 
 
    oldValue = linkedObj[id]['value']
    linkedObj[id]['value'][0] = red
    linkedObj[id]['value'][1] = green
    linkedObj[id]['value'][2] = blue
    if(updateObject(id) != 0):
        linkedObj[id]['value'] = oldValue
        return jsonify(error=3)

    # Check if remote
    if(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_REM_RGB):
        if(not linkedObj[id]['remoteClient'] in remoteClients):
            return jsonify(error=4)
        return jsonify(error=remoteClientServer.setRemoteRGB(linkedObj[id], remoteClients[linkedObj[id]['remoteClient']]))
    elif(linkedObj[id]['type'] == CONSTANTS.OBJ_TYPE_RGB):
        pass # TODO
    else:
        return jsonify(error=5)

    return jsonify(error=6)
####################################
# INTERNAL
####################################

def loadObjects():
    global linkedObj
    global remoteClients

    remoteClients.clear()
    linkedObj.clear()
    try:
        f = open('objects.json', encoding='utf-8')
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
        json.dump(objects, f2)

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
    