
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################
import onionGpio
import subprocess
import threading
import time
import datetime

####################################
# MANAGER CLASS
####################################
class Monitor:
    
    def __init__(self, sensorGpio, envMemorySize, period):
        self.sensorGpio = sensorGpio
        self.envMemory = []
        self.envMemoryIndex = -1
        self.period = period
        self.running = False
        self.thread = threading.Thread(target=self.threadRoutine)
        self.thread.daemon = True
        
        for i in range(envMemorySize):
            self.envMemory.append(["-1", "-1"])
            
        self.sensorLock = threading.Lock()
        
    def __del__(self): 
        self.stop()
        
    def threadRoutine(self):
        sensorData = [0, 1]
        while(self.running):
            now = time.time()
            
            sensorData[1] = -100.0
            while(sensorData[1] < -50.0):
                proc = subprocess.Popen(['./checkHumidity ' + str(self.sensorGpio) + ' DHT22'], stdout=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                sensorData = out.decode("utf-8").splitlines()
                sensorData[1] = float(sensorData[1])
               
            sensorData[1] += 273.15
            sensorData[1] = str(sensorData[1])
            dateData = datetime.datetime.now()
            
            self.sensorLock.acquire()
            self.envMemoryIndex = (self.envMemoryIndex + 1) % len(self.envMemory)
            self.envMemory[self.envMemoryIndex] = sensorData.copy()
            self.envMemory[self.envMemoryIndex].append(str(dateData.hour) + ":" + str(dateData.minute));
            self.sensorLock.release()
            
            now = time.time() - now
            if(self.period > now):
                time.sleep(self.period - now)

    def start(self):
        self.running = True
        self.thread.start()
        
    def stop(self):
        print("Stopping Monitor...")
        if(self.running == True):
            self.running = False
            self.sensorLock.release()
            self.thread.join()
            print("Monitor stopped")
        
    def getData(self):
        return self.envMemory, self.envMemoryIndex
    
    def getLastData(self):
        self.sensorLock.acquire()
        data = self.envMemory[self.envMemoryIndex]
        self.sensorLock.release()
        return data