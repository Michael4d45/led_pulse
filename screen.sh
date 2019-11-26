#! /bin/bash

screen -S weather -X quit;
screen -dmS weather;
screen -S weather -X stuff "python3 led.py"$(echo -ne "\015");
