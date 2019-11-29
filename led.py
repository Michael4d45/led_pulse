# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 15:19:36 2019

@author: armen
"""

import os
import time
import RPi.GPIO as GPIO 
import requests
import json
import termplotlib as tpl
from settings import API_KEY

url = "http://api.openweathermap.org/data/2.5/weather"

querystring = {"zip":"84604,us","APPID": API_KEY}

payload = ""

headers = {
        'Content-Type': 'application/json',
        'Host': "api.openweathermap.org"
        }


GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)

BLUE = GPIO.PWM(18,50) #Channel 18 #Frequency 50Hz
RED = GPIO.PWM(12,50) #Channel 12 #Frequency 50Hz
GREEN = GPIO.PWM(32,50) #Channel 32 #Frequency 50Hz

RED.start(0)
BLUE.start(0)
GREEN.start(0)


def getTemp():
    response = requests.request('GET', url, data=payload, headers=headers, params=querystring)
    res = json.loads(response.text)
    temperature = round((res['main']['temp'] - 273.15) * 1.8 + 32, 1)
    return temperature

def getPrecip():
    response = requests.request('GET', url, data=payload, headers=headers, params=querystring)
    res = json.loads(response.text)
    print(res['weather'])
    if res['main']['temp'] < 700:
        return 1
    else:
        return 0

Clear = lambda: os.system('clear')


temp = getTemp()
precip = getPrecip()
temps = [temp]
times = [0]
wait = 600 #s


def Append(temps,times):
    temp = getTemp()
    temps.insert(0,temp)
    times.append(times[-1]-wait/3600)
    if len(times)>24*3600/wait:
        times = times[0:int(24*3600/wait)]
        temps = temps[0:int(24*3600/wait)]

def flashTemp(T):
    if T>=90:
        for dc in range (0,101,5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range(100,-1,-5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range (0,101,5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range(100,-1,-5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.01)
    elif T<90 and T>32:
        for dc in range (0,101,5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.1)
        for dc in range(100,-1,-5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.1)
    elif T<=32 and T>0:
        for dc in range (0,101,5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.1)
        for dc in range(100,-1,-5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.1)
    else:
        for dc in range (0,101,5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range(100,-1,-5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range (0,101,5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range(100,-1,-5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.01)
                
def flashPrecip(binary):
    if binary == 1:
        for dc in range (0,101,5):
            GREEN.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range(100,-1,-5):
            GREEN.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range (0,101,5):
            GREEN.ChangeDutyCycle(dc)
            time.sleep(.01)
        for dc in range(100,-1,-5):
            GREEN.ChangeDutyCycle(dc)
            time.sleep(.01)
    else:
        GREEN.ChangeDutyCycle(0)
                
            
def Plot():
    fig = tpl.figure()
    fig.plot(times,temps)
    fig.show()
        
    
start = time.time()


while True:
    now = time.time()
    if now - start >= wait:
        start = time.time()
        Append(temps,times)
        precip = getPrecip()
        Clear()
        Plot()
    flashTemp(temp)
    flashPrecip(precip)
    time.sleep(1)


RED.stop()
BLUE.stop()
GPIO.cleanup()
