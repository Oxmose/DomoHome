#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

from flask     import Flask, request, render_template, jsonify
from flask_api import status

from RemoteClientServer import RemoteClientServer

####################################
# SERVER STATE VARIALBES
####################################

remoteClients = [{'id': 0, 'ip': "192.168.0.11", 'port': 5000, 'temp': True}]

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
            readTemp = remoteClientServer.reqTemperature(client['ip'], client['port'])
            break
        
    return jsonify(temp=readTemp, error=0)

####################################
# MAIN
####################################
if __name__ == '__main__': 
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")
    servApp.run(debug=True, host='0.0.0.0')