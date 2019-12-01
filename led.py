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

wait = 10 #s

def Clear():
    os.system('clear')


def blink(COLOR, t):
    for dc in range (0,101,5):
        COLOR.ChangeDutyCycle(dc)
        time.sleep(t)
    for dc in range(100,-1,-5):
        COLOR.ChangeDutyCycle(dc)
        time.sleep(t)


def quickBlink(COLOR):
    blink(COLOR, .01)
    blink(COLOR, .01)


def slowBlink(COLOR):
    blink(COLOR, .1)
    

def flashTemp(T):
    if T>=90:
        quickBlink(RED)
    elif T<90 and T>32:
        slowBlink(RED)
    elif T<=32 and T>0:
        slowBlink(BLUE)
    else:
        quickBlink(BLUE)


def getWeather():
    response = requests.request('GET', url, data=payload, headers=headers, params=querystring)
    res = json.loads(response.text)
    temperature = round((res['main']['temp'] - 273.15) * 1.8 + 32, 1)
    if res['weather'][0]['id'] < 700:
        precip = 1
    else:
        precip = 0
    return temperature,precip


def Append(temp,temps,times):
    temps.insert(0,temp)
    times.append(times[-1]-wait/3600)
    if len(times)>24*3600/wait:
        times = times[0:int(24*3600/wait)]
        temps = temps[0:int(24*3600/wait)]
        
                
def flashPrecip(binary):
    if binary == 1:
        quickBlink(GREEN)
    else:
        GREEN.ChangeDutyCycle(0)
                
            
def Plot(times,temps):
    fig = tpl.figure()
    fig.plot(times,temps)
    fig.show()
        

def Start():
    temp,precip = getWeather()
    temps = [temp]
    times = [0]
    start = time.time()
    while True:
        now = time.time()
        if now - start >= wait:
            start = time.time()
            temp,precip = getWeather()
            Append(temp,temps,times)
            Clear()
            Plot(times,temps)
        flashTemp(temp)
        flashPrecip(precip)
        time.sleep(1)


def End():
    RED.stop()
    BLUE.stop()
    GPIO.cleanup()
    
    
Start()
End()
