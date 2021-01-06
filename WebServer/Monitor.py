
#! /usr/bin/python
# -*- coding:utf-8 -*-

####################################
# IMPORTS
####################################
import threading
import time
import adafruit_dht
import json
import os

####################################
# MANAGER CLASS
####################################
class Monitor:
    
    def __init__(self, sensorGpio, envMemorySize, period):
        self.envMemory = []
        self.envMemoryIndex = -1
        self.period = period
        self.running = False
        self.thread = threading.Thread(target=self.threadRoutine)
        self.thread.daemon = True
        
        for i in range(envMemorySize):
            self.envMemory.append([-1, -1, -1])
            
        self.sensorLock = threading.Lock()
        self.sensor = adafruit_dht.DHT22(sensorGpio)
    def __del__(self): 
        self.stop()
        
    def threadRoutine(self):
        sensorData = [0, 1]
        while(self.running):
            now = time.time()
            readOk = False
            while(not readOk):
                try: 
                    sensorData = [self.sensor.humidity, self.sensor.temperature]
                    if(sensorData[0] != None):
                        readOk = True
                except:
                    print("Could not read DHT22, retry...")
                    time.sleep(0.5)

            sensorData[1] += 273.15
            dateData = time.time()
            
            self.sensorLock.acquire()
            self.envMemoryIndex = (self.envMemoryIndex + 1) % len(self.envMemory)
            self.envMemory[self.envMemoryIndex] = sensorData.copy()
            self.envMemory[self.envMemoryIndex].append(dateData)
            

            # Save data
            f2 = open('env_hist.json_tmp', 'w')
            objects = {}
            objects['data'] = [self.envMemory, self.envMemoryIndex]

            json.dump(objects, f2, indent=4)
            f2.close()
            os.remove('env_hist.json')
            os.rename('env_hist.json_tmp', 'env_hist.json')

            self.sensorLock.release()
            
            now = time.time() - now
            if(self.period > now):
                time.sleep(self.period - now)

    def start(self):
        # Load data 
        f = open('env_hist.json', 'r')
        data = json.loads(f.read())
        self.envMemoryIndex = data['data'][1]
        self.envMemory = data['data'][0]

        f.close()

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