#!/usr/bin/env python
#coding: utf8
#adapted from here: 
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

i = 0

def doIfHigh(channel):
    global i
    if GPIO.input(channel) == GPIO.HIGH:
        print ("Eingang " + str(channel) + " HIGH " + str(i))
    else:
        print ("Eingang " + str(channel) + " LOW " + str(i))


channel = 17

GPIO.add_event_detect(channel, GPIO.BOTH, callback = doIfHigh, bouncetime = 200)
#GPIO.add_event_detect(channel, GPIO.FALLING, callback = doIfHigh, bouncetime = 200)
# Eigentlicher Programmablauf
while 1:
    time.sleep(0.1)
