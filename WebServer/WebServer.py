#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import os
import CONSTANTS
import subprocess

from flask     import Flask, request, render_template, jsonify
from flask_api import status

from InternalObjectManager import InternalObjectManager
from Monitor               import Monitor

####################################
# SERVER STATE VARIALBES
####################################
serverSettings = {'tempUnit': CONSTANTS.TEMPERATURE_UNIT_C, 
                  'tempSensorGPIO': 18, 
                  'openweatherKey': '5f6f9ed658e35a4409a32bfb0271d32c',
				  'openweatherId': '6077243',
				  'envUpdatePeriod': 600,
				  'envUpdateMemory': 1000,
}

linkedObj       = {}
internalManager = InternalObjectManager()

# Monitor 
monitor         = Monitor(0, 0, 0)

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

@servApp.route('/dimmers')
def pwmDisplay():
    return render_template("index.html", display=2)
    
@servApp.route('/RGB')
def ledsDisplay():
    return render_template("index.html", display=3)

####################################
# REST API
####################################
''' Set the server settings '''
@servApp.route('/getSettings')
def getSettings():
    global serverSettings
    return jsonify(error=0, settings=serverSettings)
    
''' Set the settings '''
@servApp.route('/setSettings/<int:unit>/<int:cityId>/<int:refreshRate>/<int:histSize>')
def setSettings(unit, cityId, refreshRate, histSize):
    global serverSettings

    if(unit == CONSTANTS.TEMPERATURE_UNIT_C):
        serverSettings['tempUnit'] = CONSTANTS.TEMPERATURE_UNIT_C
    else:
        serverSettings['tempUnit'] = CONSTANTS.TEMPERATURE_UNIT_F 

    serverSettings['openweatherId']   = cityId
    serverSettings['envUpdatePeriod'] = refreshRate
    serverSettings['envUpdateMemory'] = histSize

    saveSettings()
    print(serverSettings)
    return jsonify(error=0)

''' Reboot '''
@servApp.route('/reboot')
def reboot():
    rebootServer()
    return jsonify(error=0)
    
''' Get the current environment data '''
@servApp.route('/getEnv')
def getEnv():
    global monitor
    sensor_data = monitor.getLastData()
    return jsonify(temp=sensor_data[1], humidity=sensor_data[0], unit=serverSettings['tempUnit'], error=0)
    
''' Get the environment data history'''
@servApp.route('/getEnvHist')
def getEnvHist():
    global monitor
    return jsonify(data=monitor.getData(), unit=serverSettings['tempUnit'], error=0)

''' Set the server object '''
@servApp.route('/getObjects')
def getObjects():
    global linkedObj
    return jsonify(error=0, objects=linkedObj)
    
''' Toggle a given object '''
@servApp.route('/toggle/<int:objId>')
def toggleObject(objId):
    global linkedObj
    
    if(not str(objId) in linkedObj):
        return jsonify(error=1)
        
    objId = str(objId)
    
    linkedObj[objId]['state'] = not linkedObj[objId]['state']
    if(updateObject(objId) != 0):
        linkedObj[objId]['state'] = not linkedObj[objId]['state']
        return jsonify(error=2)

    if(linkedObj[objId]['type'] == CONSTANTS.OBJ_TYPE_SWITCH):
        internalManager.setSwitch(linkedObj[objId], linkedObj[objId]['state'])
    else:
        return jsonify(error=3)

    return jsonify(error=0, objects=linkedObj[objId])

''' Toggle a given PWM object '''
@servApp.route('/togglePWM/<int:objId>')
def togglePWMObject(objId):
    global linkedObj
    
    if(not str(objId) in linkedObj):
        return jsonify(error=1)
        
    objId = str(objId)
    
    linkedObj[objId]['state'] = not linkedObj[objId]['state']
    if(updateObject(objId) != 0):
        linkedObj[objId]['state'] = not linkedObj[objId]['state']
        return jsonify(error=2)
    
    value = linkedObj[objId]['value']
    if(linkedObj[objId]['state'] == False):
        value = 0

    if(linkedObj[objId]['type'] == CONSTANTS.OBJ_TYPE_PWM):
        internalManager.setPWM(linkedObj[objId], value)
    else:
        return jsonify(error=3)

    return jsonify(error=0, objects=linkedObj[objId])
    
''' Set a given PWM object '''
@servApp.route('/setPWM/<int:objId>/<int:value>')
def setPWM(objId, value):
    global linkedObj
    
    if(not str(objId) in linkedObj):
        return jsonify(error=1)
        
    objId = str(objId)
    
    linkedObj[objId]['value'] = value
    
    if(value == 0):
        linkedObj[objId]['state'] = False
    else:
        linkedObj[objId]['state'] = True
        
    if(updateObject(objId) != 0):
        return jsonify(error=2)

    if(linkedObj[objId]['type'] == CONSTANTS.OBJ_TYPE_PWM):
        internalManager.setPWM(linkedObj[objId], value)
    else:
        return jsonify(error=3)

    return jsonify(error=0, objects=linkedObj[objId])
    

''' Toggle a given RGB object '''
@servApp.route('/toggleRGB/<int:objId>')
def toggleRGBObject(objId):
    global linkedObj
    
    if(not str(objId) in linkedObj):
        return jsonify(error=1)
        
    objId = str(objId)
    
    linkedObj[objId]['state'] = not linkedObj[objId]['state']
    if(updateObject(objId) != 0):
        linkedObj[objId]['state'] = not linkedObj[objId]['state']
        return jsonify(error=2)

    if(linkedObj[objId]['type'] == CONSTANTS.OBJ_TYPE_RGB):
        if(linkedObj[objId]['state']):
            # Transpose to percentage
            red = linkedObj[objId]['value'][0]
            green = linkedObj[objId]['value'][1]
            blue = linkedObj[objId]['value'][2]

            red = red * 100 / 255
            green = green * 100 / 255
            blue = blue * 100 / 255
        
            internalManager.setRGB(linkedObj[objId], [red, green, blue])
        else:
            internalManager.setRGB(linkedObj[objId], [0, 0, 0])
    else:
        return jsonify(error=3)

    return jsonify(error=0, objects=linkedObj[objId])

''' Set a given RGB object '''
@servApp.route('/setRGB/<int:objId>/<int:red>/<int:green>/<int:blue>')
def setRGB(objId, red, green, blue):
    global linkedObj
    
    if(not str(objId) in linkedObj):
        return jsonify(error=1)
        
    objId = str(objId)
    
    if(red > 255):
        red = 255
    if(green > 255):
        green = 255
    if(blue > 255):
        blue = 255
    
    linkedObj[objId]['value'] = [red, green, blue]
    
    totalVal = red + green + blue
    
    if(totalVal == 0):
        linkedObj[objId]['state'] = False
    else:
        linkedObj[objId]['state'] = True
        
    if(updateObject(objId) != 0):
        return jsonify(error=2)

    if(linkedObj[objId]['type'] == CONSTANTS.OBJ_TYPE_RGB):
        # Transpose to percentage
        red = red * 100 / 255
        green = green * 100 / 255
        blue = blue * 100 / 255
    
        internalManager.setRGB(linkedObj[objId], [red, green, blue])
    else:
        return jsonify(error=3)

    return jsonify(error=0, objects=linkedObj[objId])
    
####################################
# INTERNAL
####################################

def loadObjects():
    global linkedObj
    linkedObj.clear()
    
    try:
        f = open('objects.json')
        objects = json.loads(f.read())
        for key in objects:
            if(key in linkedObj):
                print("Duplicate object id " + str(key))
                exit(-1)

            obj = objects[key]

            if(obj['type'] == CONSTANTS.OBJ_TYPE_SWITCH or obj['type'] == CONSTANTS.OBJ_TYPE_PWM or obj['type'] == CONSTANTS.OBJ_TYPE_RGB):
                linkedObj[key] = {
                    'type': obj['type'], 
                    'name': obj['name'], 
                    'state': obj['state'], 
                    'value': obj['value'], 
                    'gpio': obj['gpio'],
                    'node': obj['node'],
                    'addr': obj['addr']
                }
            else:
                print("Unkonwn object type " + str(obj['type']))

        print("Loaded " + str(len(linkedObj)) + " objects")
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
        f = open('objects.json', 'r')
        objects = json.loads(f.read())
        currObj = linkedObj[id]

        objects[id]['type'] = currObj['type']
        objects[id]['name'] = currObj['name']
        objects[id]['value'] = currObj['value']
        objects[id]['state'] = currObj['state']
        objects[id]['gpio'] = currObj['gpio']

        f2 = open('objects.json_tmp', 'w')
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
        f.close()
    except:     
        pass

def saveSettings():
    global serverSettings
    try:
        f = open('config.pak', 'w')
        json.dump(serverSettings, f, indent=4)
        f.close()
    except:     
        pass
	

####################################
# MAIN
####################################

def rebootServer():
    global monitor
    
    print("Loading data...")
    
    loadObjects()
    loadSettings()
    saveSettings()
    
    if(monitor != None):
        monitor.stop()
        del monitor
        
    monitor = Monitor(serverSettings['tempSensorGPIO'], serverSettings['envUpdateMemory'], serverSettings['envUpdatePeriod'])
    monitor.start()
    

if __name__ == '__main__': 
    rebootServer()
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")
    servApp.run(debug=True, host='0.0.0.0', use_reloader=False)
    
    