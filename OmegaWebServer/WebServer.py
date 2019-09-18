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
remoteClients = []
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

''' Get the current temperature '''
@servApp.route('/getTemp')
def getTemp():
    readTemp = 0.0
    for client in remoteClients:
        if(client['temp'] == True):
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

def loadRemoteClients():
    global remoteClients
    try:
        f = open('rc_data.pak', encoding='utf-8')
        remoteClients = json.loads(f.read())
    except:     
        pass

def saveRemoteClients():
    global remoteClients
    try:
        f = open('rc_data.pak', 'w')
        json.dump(remoteClients, f)
    except:     
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
    loadRemoteClients()
    saveRemoteClients()
    loadSettings()
    saveSettings()
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")
    servApp.run(debug=True, host='0.0.0.0')