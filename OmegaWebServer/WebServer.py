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
@servApp.route('/toggle/<id>')
def toggle(id):
    if(not str(id) in linkedObj):
        return jsonify(error=1)
    linkedObj[id]['state'] = not linkedObj[id]['state']
    print("OK")
    updateObject(id)
    return jsonify(error=0)
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

            if(obj['type'] == 0 or obj['type'] == 1 or obj['type'] == 2):
                linkedObj[key] = {'type': obj['type'], 'name': obj['name'], 'state': obj['lastState'], 'value': obj['value'], 'gpio': obj['gpio']}
            elif(obj['type'] == 3 or obj['type'] == 4):
                linkedObj[key] = {'type': obj['type'], 'name': obj['name'], 'state': obj['lastState'], 'value': obj['value'], 'gpio': obj['gpio'], 'remoteClient': obj['remoteClientId']}
            elif(obj['type'] == 5):
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

    except ValueError as e:
        print("ERROR " + str(e))
        exit(-1)
    except IOError as e:
        print("ERROR " + e.strerror)
        exit(-1)
    except Exception as e:     
        print("ERROR While reading object file " + str(e))
        exit(-1)

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
    