#! /usr/bin/env python

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
PIR_PIN = 16
LED_PIN = 21
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
def MOTION(PIR_PIN):
	localtime = time.asctime(time.localtime(time.time()))
	print "Motion detected! " + localtime
	GPIO.output(LED_PIN, GPIO.HIGH)
	time.sleep(0.5)
	GPIO.output(LED_PIN, GPIO.LOW)
print "PIR Module Test (CTRL+C to exit)"
time.sleep(2)
print "Ready"
try:
	while 1:
		if GPIO.input(PIR_PIN):
			MOTION(PIR_PIN)
			
except KeyboardInterrupt:
       print " Quit"
       GPIO.cleanup()
