import RPi.GPIO as GPIO ## Import GPIO library
import time
import os
GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(3, GPIO.OUT) ## Setup GPIO Pin 7 to OUT

GPIO.output(3,True)
time.sleep(3)
GPIO.output(3,False)