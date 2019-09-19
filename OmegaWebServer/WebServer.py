#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import CONSTANTS

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

####################################
# INTERNAL
####################################

def loadObjects():
    global linkedObj
    global remoteClients
    try:
        f = open('objects.json', encoding='utf-8')
        objects = json.loads(f.read())
        for obj in objects:
            if(obj['type'] == 0 or obj['type'] == 1 or obj['type'] == 2):
                linkedObj[obj['id']] = {'name': obj['name'], 'state': obj['lastState'], 'gpio': obj['gpio']}
            elif(obj['type'] == 3 or obj['type'] == 4):
                linkedObj[obj['id']] = {'name': obj['name'], 'state': obj['lastState'], 'gpio': obj['gpio'], 'remoteClient': obj['remoteClientId']}
            elif(obj['type'] == 5):
                remoteClients[obj['id']] = {'ip': obj['ip'], 'port': obj['port'], 'tempSensor': obj['tempSensor']}
            else:
                print("Unkonwn object type " + str(obj['type']))

        print(linkedObj)
        print(remoteClients)
    except ValueError as e:
        print("ERROR " + e)
    except IOError as e:
        print("ERROR " + e.strerror)
    except Exception as e:     
        print("ERROR While reading object file " + str(e))
        pass

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
if __name__ == '__main__': 
    print("Loading data...")
    loadObjects()
    loadSettings()
    saveSettings()
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")
    servApp.run(debug=True, host='0.0.0.0')