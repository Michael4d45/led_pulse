import os
import time
import RPi.GPIO as GPIO 
import requests
import json
import termplotlib as tpl
from settings import API_KEY

url = "http://api.openweathermap.org/data/2.5/weather"

querystring = {"zip":"84602,us","APPID": API_KEY}

payload = ""

headers = {
        'Content-Type': 'application/json',
        'Host': "api.openweathermap.org"
        }


GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

BLUE = GPIO.PWM(12,50) #Channel 12 #Frequency 50Hz
RED = GPIO.PWM(18,50) #Channel 18 #Frequency 50Hz

RED.start(0)
BLUE.start(0)


def getWeather():
    response = requests.request('GET', url, data=payload, headers=headers, params=querystring)
    res = json.loads(response.text)
    temperature = round((res['main']['temp'] - 273.15) * 1.8 + 32, 1)
    print(temperature)
    return temperature

Clear = lambda: os.system('clear')


temp = getWeather()
temps = [temp]
times = [0]
wait = 10 #s


def Append():
    global temp
    global temps
    global times
    temp = getWeather()
    temps.insert(0,temp)
    times.append(times[-1]-wait/3600)
    if len(times)>24*3600/wait:
        times = times[0:24*3600/wait]
        temps = temps[0:24*3600/wait]

def flashTemp():
    global temp
    if temp>=90:
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
    if temp<90 and temp>32:
        for dc in range (0,101,5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.1)
        for dc in range(100,-1,-5):
            RED.ChangeDutyCycle(dc)
            time.sleep(.1)
    if temp<=32 and temp>0:
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
            
def Plot():
    global times
    global temps
    fig = tpl.figure()
    fig.plot(times,temps)
    fig.show()
        
    
start = time.time()


while True:
    now = time.time()
    if now - start >= wait:
        start = time.time()
        Append()
        Clear()
        Plot()
    flashTemp()
    time.sleep(1)


RED.stop()
BLUE.stop()
GPIO.cleanup()
