import time
import RPi.GPIO as GPIO 
import requests
import json
import termplotlib as tpl
import numpy as np
from settings import API_KEY

print("begin")

url = "http://api.openweathermap.org/data/2.5/weather"

querystring = {"zip":"84602,us","APPID": API_KEY}


payload = ""

headers = {
        'Content-Type': 'application/json',
        'Host': "api.openweathermap.org"
        }


def getWeather():
    response = requests.request('GET', url, data=payload, headers=headers, params=querystring)
    res = json.loads(response.text)
    temp = np.round(((res['main']['temp'] - 273.15) * 1.8 + 32) * 10) / 10
    print(temp)
    return temp

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)


BLUE = GPIO.PWM(12,50) #Channel 12 #Frequency 50Hz
RED = GPIO.PWM(18,50) #Channel 18 #Frequency 50Hz


RED.start(0)
BLUE.start(0)

time1 = time.time()
delta = 10*60

temp = getWeather()

temps = np.array([temp,temp])
times = np.array([0,0])

while True:
    time2 = time.time()
    if time2 - time1 >= delta:
        time1 = time.time()
        temp = getWeather()
        temps = np.append(temps,temp)
        times = np.append(times,times[-1]+1)
        if len(times)>12 * 6:
            times = times[1:]
            temps = temps[1:]
        fig = tpl.figure()
        fig.plot(times,temps)
        fig.show()
    if  temp > 32.:
        for dc in range (0,101,5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.1)
        for dc in range(100,-1,-5):
            BLUE.ChangeDutyCycle(dc)
            time.sleep(.1)
    else:
        for dc in range (0,101,5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.1)
        for dc in range(100,-1,-5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.1)
    time.sleep(1)

RED.stop()
BLUE.stop()
GPIO.cleanup()

