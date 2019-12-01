#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 15:19:36 2019

@author: armen, harvey
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

blink(RED, 0)
blink(BLUE, 0)
blink(GREEN, 0)

temp = getTemp()
precip = getPrecip()
temps = [temp]
times = [0]
wait = 600 #10 min in seconds
max_plot_len = int(24*3600/wait)

start()
end()

clear = lambda: os.system('clear')


def blink(COLOR, t):
    for dc in range (0,101,5):
        COLOR.ChangeDutyCycle(dc)
        time.sleep(t)
    for dc in range(100,-1,-5):
        RED.ChangeDutyCycle(dc)
        time.sleep(t)


def quickBlink(COLOR):
    blink(COLOR, .01)
    blink(COLOR, .01)


def slowBlink(COLOR):
    blink(COLOR, .1)


def flashTemp():
    if temp >= 90:
        quickBlink(RED)
    elif temp < 90 and temp > 32:
        slowBlink(RED)
    elif temp <= 32 and temp > 0:
        slowBlink(BLUE)
    else:
        quickBlink(BLUE)


def flashPrecip():
    if precip == 1:
        quickBlink(GREEN)
    else:
        GREEN.ChangeDutyCycle(0)


def getTemp():
    #request weather
    response = requests.request('GET', url, data=payload, headers=headers, params=querystring)
    res = json.loads(response.text)
    #convert Kelvin to Fahrenheit
    temp = round((res['main']['temp'] - 273.15) * 1.8 + 32, 1)
    if res['weather'][0]['id'] or res['weather'][-1]['id'] < 700:
        precip = 1
    else:
        precip = 0


def append():
    temps.insert(0,temp)
    times.append(times[-1]-wait/3600)
    if len(times)>max_plot_len:
        times = times[0:max_plot_len]
        temps = temps[0:max_plot_len]


def plot():
    clear()
    fig = tpl.figure()
    fig.plot(times, temps)
    fig.show()


def start():
    start = time.time()
    while True:
        now = time.time()
        if now - start >= wait:
            start = time.time()
            getWeather()
            append()
            plot()
        flashTemp()
        flashPrecip()
        time.sleep(1)


def end():
    RED.stop()
    BLUE.stop()
    GPIO.cleanup()

