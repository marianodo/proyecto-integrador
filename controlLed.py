#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO ## Import GPIO library
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(5, GPIO.OUT) ## Setup GPIO Pin 5 to OUT

def led1():   
        GPIO.output(5,True)
        time.sleep(0.5)
        GPIO.output(5,False)
        time.sleep(0.5)
if __name__ == '__main__':
	File = open("/var/tmp/statusLed.txt","r")
	statusControl = File.readline()
	statusPing = File.readline()
	if int(statusControl) == 1:
		for i in range(8):
			led1()
	elif int(statusPing) == 1:
		GPIO.output(5,True)
	else:
		GPIO.output(5,False)

                

# 1) Ping al router
# 2) Chequeo de Control.py
# 3) Led de encendido.
