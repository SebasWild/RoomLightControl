#!/usr/bin/env python

# Light an LED when motion is detected from a PIR sensor.

import RPi.GPIO as GPIO, os, time

ledPin = 21
pirPin = 16
GPIO.setmode(GPIO.BCM)		# BCM numbering
GPIO.setup(ledPin, GPIO.OUT)	# The LED pin is defined as an output.
GPIO.setup(pirPin, GPIO.IN)	# The PIR Pin is defines as and input.

# Activate the LED when we receive a motion callback
def motion(pin):
	GPIO.output(ledPin, GPIO.HIGH)
	time.sleep(0.5)
	print "Hello!"
	GPIO.output(ledPin, GPIO.LOW)
time.sleep(2)
try:
	GPIO.add_event_detect(pirPin, GPIO.RISING, callback = motion)
	while 1:
		time.sleep(100)
except KeyboardInterrupt:
	print "Quit"
	GPIO.cleanup()

 
