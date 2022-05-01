#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import hashlib
import uuid
import flask_login
import socket
import shutil
import os
import UserDB
import Config
import EnvMonitor
import Constants
import Logger
import time

from datetime import datetime
from flask import Flask, request, render_template, jsonify, redirect, url_for

####################################
# CONSTANTS
####################################

STORE_UNIT  = ["B", "KB", "MB", "GB", "TB"]
MODULE_NAME = "MAIN"

####################################
# SERVER STATE VARIALBES
####################################

# We have to keep the Flask servAPP as global var
servApp   = Flask(__name__)
servLogin = flask_login.LoginManager()

envMonitor = EnvMonitor.EnvMonitor()

################################################################################
# FUNCTIONS
################################################################################
@servLogin.user_loader
def user_loader(username):
    return UserDB.getUserByUsername(username)

@servLogin.request_loader
def request_loader(request):
    username = request.form.get("username")
    return UserDB.getUserByUsername(username)


################################################################################
# ROUTES | OPEN
################################################################################
@servApp.route('/')
@servApp.route('/login')
def indexId():
    return render_template("index.html")

@servApp.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for("indexId"))

@servLogin.unauthorized_handler
def unauthorized_handler():
    """ DEBUG PURPOSE ONLY
    username = "alexy"
    passwd   = "password"

    user = UserDB.getUserByUsername(username)
    if(user == None):
        return jsonify(error=Constants.ERROR_INCORRECT_CRED_CODE, message=Constants.ERROR_INCORRECT_CRED_MSG)

    # Hash given password
    strToHash = username + passwd + str(user.regtime)
    hash = hashlib.sha256(strToHash.encode("utf-8"))
    if hash.hexdigest() == user.password:
        # Add user to session and redirect to dashboard
        flask_login.login_user(user)
        # Todo Remove
        return redirect(url_for("historyRoute"))
        return jsonify(error=0)
    else:
        return jsonify(error=Constants.ERROR_INCORRECT_CRED_CODE, message=Constants.ERROR_INCORRECT_CRED_MSG)
    """
    return redirect(url_for("indexId"))

################################################################################
# ROUTES | LOGIN REQUIRED
################################################################################
@servApp.route('/dash')
@flask_login.login_required
def dashboardRoute():
    # Get NAS disk information
    total, used, free = shutil.disk_usage(Config.NASMountPoint)
    usedUnitIdx  = 0
    totalUnitIdx = 0
    while(used > 1024):
        used = used / 1024
        usedUnitIdx += 1
    while(total > 1024):
        total = total / 1024
        totalUnitIdx += 1

    return render_template("dashboard.html",
                           diskUsed = "{:.2f}".format(used), diskTotal = "{:.2f}".format(total),
                           diskUsedUnit = STORE_UNIT[usedUnitIdx], diskTotalUnit = STORE_UNIT[totalUnitIdx],
                           diskPercent = "{:.2f}".format(used / total * 100),
                           weatherApiKey = flask_login.current_user.weatherApiKey,
                           serverApiKey = flask_login.current_user.serverApiKey)

@servApp.route('/history')
@flask_login.login_required
def historyRoute():
    return render_template("history.html",
                           weatherApiKey = flask_login.current_user.weatherApiKey,
                           serverApiKey = flask_login.current_user.serverApiKey)

@servApp.route('/tryLogin')
@flask_login.login_required
def tryLogin():
    return jsonify(error=0)

################################################################################
# API | OPEN
################################################################################

@servApp.route('/doLogin/', methods = ["POST"])
def doLogin():
    if request.method == "POST":
        username = request.form["username"]
        passwd   = request.form["passwd"]

        user = UserDB.getUserByUsername(username)
        if(user == None):
            return jsonify(error=Constants.ERROR_INCORRECT_CRED_CODE, message=Constants.ERROR_INCORRECT_CRED_MSG)

        # Hash given password
        strToHash = username + passwd + str(user.regtime)
        hash = hashlib.sha256(strToHash.encode("utf-8"))
        if hash.hexdigest() == user.password:
            # Add user to session and redirect to dashboard
            flask_login.login_user(user)
            return jsonify(error=0)
        else:
            return jsonify(error=Constants.ERROR_INCORRECT_CRED_CODE, message=Constants.ERROR_INCORRECT_CRED_MSG)
    else:
        print("Accessed doLogin with incorrect method.")
        return jsonify(error=Constants.ERROR_UNAUTHORIZED_CODE, message=Constants.ERROR_UNAUTHORIZED_MSG)

################################################################################
# API | KEY REQUIRED
################################################################################
@servApp.route('/getHourEnv/<sampleCount>/<factor>/<apiKey>')
@flask_login.login_required
def getHourEnv(sampleCount, factor, apiKey):
    sampleCount = int(sampleCount)
    factor      = int(factor)

    if not UserDB.checkApiKey(apiKey):
        return jsonify(error = Constants.ERROR_INVALID_API_KEY_CODE,
                       msg = Constants.ERROR_INVALID_API_KEY)

    lastHour = 0

    # Get the min time to get samples from
    lastTimeStamp = time.time() // factor * factor - (sampleCount * factor)
    lastIdx = len(envMonitor.envData) - 1
    # Get the last data
    timedData = {}

    while(lastIdx >= 0 and envMonitor.envData[lastIdx]["time"] >= lastTimeStamp):
        hourBound = envMonitor.envData[lastIdx]["time"] // factor * factor
        if hourBound in timedData:
            timedData[hourBound].append(envMonitor.envData[lastIdx])
        else:
            if len(timedData) + 1 > sampleCount:
                break
            timedData[hourBound] = [envMonitor.envData[lastIdx]]
        lastIdx -= 1

    if sampleCount != len(timedData):
        Logger.LOG_WARNING(MODULE_NAME, Constants.WARNING_SAMPLE_COUNT_MISSMATCH, None)
        Logger.LOG_WARNING(MODULE_NAME, "Samples count: " + str(sampleCount) + " | " + str(len(timedData)), None)

    # Average on the samples
    samples = []
    for timeValue in sorted(timedData):
        avgTemp = 0
        avgHum  = 0
        avgLum  = 0

        for data in timedData[timeValue]:
            avgTemp += data["t"]
            avgHum  += data["h"]
            avgLum  += data["l"]

        dataCount = len(timedData[timeValue])
        avgTemp /= dataCount
        avgHum  /= dataCount
        avgLum  /= dataCount

        samples.append({
            "t": avgTemp,
            "h": avgHum,
            "l": avgLum,
            "time": timeValue
        })

    return jsonify(error = 0, data = samples)

@servApp.route('/getEnvlast/<apiKey>')
def getEnvlast(apiKey):
    if not UserDB.checkApiKey(apiKey):
        return jsonify(error = Constants.ERROR_INVALID_API_KEY_CODE,
                       msg = Constants.ERROR_INVALID_API_KEY)

    return jsonify(error=0, lastEnv=envMonitor.getLastData())

@servApp.route('/getNASStatus/<apiKey>')
def getNASStatus(apiKey):
    if not UserDB.checkApiKey(apiKey):
        return jsonify(error = Constants.ERROR_INVALID_API_KEY_CODE,
                       msg = Constants.ERROR_INVALID_API_KEY)

    # Get services status
    isSAMBAEnabled = os.system('sudo systemctl is-active --quiet smbd') == 0
    isFTPEnabled   = os.system('sudo systemctl is-active --quiet proftpd') == 0

    total, used, free = shutil.disk_usage(Config.NASMountPoint)
    usedUnitIdx  = 0
    totalUnitIdx = 0
    while(used > 1024):
        used = used / 1024
        usedUnitIdx += 1
    while(total > 1024):
        total = total / 1024
        totalUnitIdx += 1

    return jsonify(error=0, ftpEnabled=isFTPEnabled, smbdEnabled=isSAMBAEnabled, diskUsed = "{:.2f}".format(used), diskTotal = "{:.2f}".format(total),
                           diskUsedUnit = STORE_UNIT[usedUnitIdx], diskTotalUnit = STORE_UNIT[totalUnitIdx],
                           diskPercent = "{:.2f}".format(used / total * 100))

################################################################################
# API | LOGIN REQUIRED
################################################################################

@servApp.route('/updateEnvLast')
@flask_login.login_required
def updateEnvlast():
    envMonitor.forceUpdate()
    return jsonify(error=0, lastEnv=envMonitor.getLastData())

@servApp.route('/toggleFTP/<action>')
@flask_login.login_required
def toggleFTP(action):
    if action == "on":
        os.system('sudo service proftpd start')
        return jsonify(error=0)
    elif action == "off":
        os.system('sudo service proftpd stop')
        return jsonify(error=0)
    else:
        return jsonify(error=1)

@servApp.route('/toggleSMBD/<action>')
@flask_login.login_required
def toggleSMBD(action):
    if action == "on":
        os.system('sudo service smbd start')
        return jsonify(error=0)
    elif action == "off":
        os.system('sudo service smbd stop')
        return jsonify(error=0)
    else:
        return jsonify(error=1)

####################################
# MAIN
####################################

if __name__ == '__main__':
    print("#============================#")
    print("|    Starting the server     |")
    print("#============================#")

    # Load user DB
    UserDB.loadUsers()

    # Start environment monitor
    envMonitor.load(Constants.ENV_FILE)
    envMonitor.start()

    servApp.secret_key = uuid.uuid4().hex
    servLogin.init_app(servApp)
    servApp.run(debug=True, host='0.0.0.0', use_reloader=False)

    envMonitor.stop()


################################################################################
# EOF