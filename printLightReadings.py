#!/usr/bin/env python

# Example for RC timing reading for Raspberry Pi
# Must be used with GPIO 0.3.1a or later - earlier verions
# are not fast enough!

import RPi.GPIO as GPIO, time, os      

DEBUG = 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)	# Pin for the output status LED
targetBrightness = 1000		# The brightness we want the room to be

def RCtime (RCpin):
        reading = 0
        GPIO.setup(RCpin, GPIO.OUT)
        GPIO.output(RCpin, GPIO.LOW)
        time.sleep(0.1)

        GPIO.setup(RCpin, GPIO.IN)
        # This takes about 1 millisecond per loop cycle
        while (GPIO.input(RCpin) == GPIO.LOW):
                reading += 1
        return reading

while True:                                     
	reading = RCtime(20)
	print(reading)
	if reading > targetBrightness:
		# We increase LIFX brightness here
		GPIO.output(26, GPIO.HIGH)
	else:
		# We decrease brightness here, and do the loop again.
		GPIO.output(26, GPIO.LOW) 
