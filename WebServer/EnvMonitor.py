#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################

import json
import Logger
import Constants
import Config
import time
import requests

from os.path import exists
from threading import Thread, Lock
from time import sleep

####################################
# CONSTANTS
####################################

MODULE_NAME = "EnvMonitor"

####################################
# GLOBAL VARIABLES
####################################

# None.

####################################
# FUNCTIONS
####################################

class EnvMonitor:
    def __init__(self):
        self.isInit     = False
        self.thread     = None
        self.thRun      = False
        self.envLock    = Lock()
        self.updateLock = Lock()
        self.envFile    = None
        self.envData    = []

    def __del__(self):
        if self.envFile != None:
            self.envFile.close()

    def isComment(self, str):
        for i in range(len(str)):
            if str[i] == ' ':
                continue
            if str[i] == '#':
                return True
            else:
                return False

        return True

    def load(self, envSaveFile):
        # Open / Create the environment file
        try:
            self.envData = []
            self.envFile = open(envSaveFile, "a+")

            # Load Data
            self.envFile.seek(0)
            line = self.envFile.readline()
            while(line):
                if(not self.isComment(line)):
                    line = line.strip()

                    dataInfo = line.split(",")
                    # Format is time, temp, hum, lum
                    self.envData.append({
                        "time": int(dataInfo[0]),
                        "t": float(dataInfo[1]),
                        "h": float(dataInfo[2]),
                        "l": float(dataInfo[3]),
                    })

                line = self.envFile.readline()

            self.envFilename = envSaveFile
            self.isInit = True

            Logger.LOG_SUCCESS(MODULE_NAME, Constants.INFO_LOADED_ENV_FILE)

        except OSError as exc:
            Logger.LOG_ERROR(MODULE_NAME, Constants.ERROR_CANNOT_LOAD_ENV_FILE + " " + str(exc),
                             Constants.ERROR_CANNOT_LOAD_ENV_FILE_CODE, True)
        except Exception as exc:
            Logger.LOG_ERROR(MODULE_NAME, Constants.ERROR_UNKNOWN + " " + str(exc),
                             Constants.ERROR_UNKNOWN_CODE, False)


    def start(self):
        self.thread = Thread(target = self.threadRoutine)
        self.thRun  = True
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.thRun = False
            Logger.LOG_INFO(MODULE_NAME, Constants.INFO_WAITING_FOR_THREAD)
            self.thread.join();
        else:
            Logger.LOG_WARNING(MODULE_NAME, Constants.WARNING_STOP_NONEXISTANT_THREAD, None)

    def update(self):
        try:
            # Prepare request
            reqURL = Config.nodeIP + Config.nodeRouteEnv
            Logger.LOG_INFO(MODULE_NAME, Constants.INFO_REQUESTING_NODE)
            response = requests.get(reqURL)

            # Parse response
            response = response.json()

            Logger.LOG_INFO(MODULE_NAME, Constants.INFO_REQUESTING_NODE_OK)

            # Add data to environment data
            self.envLock.acquire()
            self.envData.append({"l": response["lum"],
                                 "t": response["temp"],
                                 "h": response["humidity"],
                                 "time": time.time()})
            if self.envFile != None:
                strData = "{},{},{},{}\n".format(response["timestamp"],
                                                 response["temp"],
                                                 response["humidity"],
                                                 response["lum"])
                self.envFile.write(strData)
                self.envFile.flush()
            self.envLock.release()

            # Save data to file
        except Exception as exc:
            Logger.LOG_ERROR(MODULE_NAME, str(exc), Constants.ERROR_UNKNOWN_CODE, False)

    def forceUpdate(self):
        self.updateLock.acquire()
        lastUpdate = time.time()
        self.updateLock.release()
        self.update()

    def threadRoutine(self):
        lastUpdate = 0
        while(self.thRun):
            curTime = time.time()
            self.updateLock.acquire()
            if lastUpdate + Config.envRefreshPeriod <= curTime:
                lastUpdate = curTime
                self.updateLock.release()
                self.update()
            else:
                self.updateLock.release()
            # Alsways sleep 1 second
            sleep(1)

    def getLastData(self):
        self.envLock.acquire()
        data = self.envData[-1]
        self.envLock.release()
        return data

####################################
# MAIN
####################################

if __name__ == '__main__':
    envMon = EnvMonitor()
    envMon.load("testEnv.db")
    envMon.stop()
    envMon.start()
    sleep(10)
    print(envMon.envData)
    envMon.stop()

################################################################################
# EOF