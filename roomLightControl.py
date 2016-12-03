
#!/usr/bin/env python

import RPi.GPIO as GPIO, os, time, threading
import logging
import requests
import json
#################################################
# SETUP                                         #
#################################################
ledPin = 21                     # status LED pin
pirPin = 16                     # Pin the PIR is connected to
GPIO.setmode(GPIO.BCM)          # BCM numbering
GPIO.setup(ledPin, GPIO.OUT)    # The LED pin is defined as an output.
GPIO.setup(pirPin, GPIO.IN)     # The PIR Pin is defines as and input.

logging.basicConfig(filename='roomLightControl.log',level=logging.DEBUG)                # Set up the logging file
# Load the config file
with open("./config/config.py") as f:
    exec(f.read())
# All future HTTP requests to the LIFX API must carry this header containing our API key
headers = {
    "Authorization": "Bearer %s" % LIFXtoken,
}
# HTTP PUT payload to turn lights OFF
OFF = {
        "power": "off",
}
# HTTP payload to turn lights ON
ON = {
        "power": "on",
}
lastPayload = None              # The last payload that we sent to the server
setLightLevel = 1               # The light level that we want to maintain in the room
thresholdTime = time.time()     # Time when the timer expires, initialized to right NOW!
lightsTimeout = 2 * 60          # Time in seconds after which lights will turn off if no motion is detected
lastLightState = None           # The last known state of the lights. Refreshed when motion is detected
isTimerExpired = True           # Has the timeout passed? If so, the lights will turn on once motion is detected again
#################################################
# MAIN                                          #
#################################################

# motion() is called when the PIR detects movement in the room
# This will reset the lights OFF timer
def motion(pin):
        global thresholdTime            # We need to declare this as a global var, since odds are we will need to write to it

        time.sleep(1)                   # We need to make sure that motion was actually detected, so wait a bit and check the wire again
        if GPIO.input(pirPin, GPIO.HIGH) != 1:
            return

        currTime = time.time()          # Exact moment we noticed the motion
        # Now that motion has been detected, do we need to act on it?
        # Check the status of the lights. If OFF, turn them ON <-Later on this will also depend on light level

        logging.info("Motion detected at:\t " + time.asctime(time.localtime(currTime)))         # Convert raw time to local and log movement detection

        if lastLightState is None:
                getLightState()
        thresholdTime = time.time() + lightsTimeout             # Every time motion is detected, reset the timeout
        if lastLightState[0]["power"] == "off":                 # For now I assume that the lights will always be in sync, so we only check the first one
                setLightState(ON)                               # Send request to turn lights ON, if light is below setLightLevel
        # Else  Motion was detected, and the lights are already on, there is nothing to do
        time.sleep(1)                                           # Sleep a second before proceding
# GET List Lights 'https://api.lifx.com/v1/lights/all'
# Returns the status of the desired lights (for now, in my case all the lights
def getLightState():
        global lastLightState                                   # Declare this as a global var
        try:
                response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)          # Do the GET request
                if response.status_code != 200:         # Non-200 reponse means that we could not get a proper response. Something went wrong
                        logging.error("Non-200 response code when querying lights state.")
                        return None
                else:                                   # We got a correct JSON reponse back
                        logging.info("getLightStatus() " + str(response.status_code) + "at\t" + time.asctime(time.localtime(time.time())))
                        parsed = lastLightState = json.loads(response.text)             # Deserialize the JSON
                        return parsed
        except requests.ConnectionError:
                # When we get a connection error, simply wait a bit and re-send the request
                time.sleep(2)
                return getLightState()
        return None             # Does this function even need to return anything???
# HTTP POST set the lights using the desired payload
# TODO Implement checking so that we do not send more requests to the server than we need to
def setLightState(payload):
        global lastPayload
        if lastPayload == payload:
                logging.info("Not re-sending a request")
                return
        try:
                response = requests.put('https://api.lifx.com/v1/lights/all/state', data=payload, headers=headers)

                if response.status_code != 200 and response.status_code != 207:         # Non-200 reponse means that we could not get a proper response. Something went wrong
                    logging.error("Non-200 or 207 response code when setting lights state.")
                else:
                        lastPayload = payload
                        parsed = json.loads(response.text)

                        if parsed['results'][0]['status'] == "ok":              # The request went through OK
                                lastLightState[0]["power"] = payload["power"]   # Update the lastLightState so we do not need to make another request
                        logging.info("Set light state to " + str(payload))
        except requests.ConnectionError:
                # If we get a connection error, wait a bit and try again
                time.sleep(2)
                setLightState(payload)
try:
        print "System start in 5 seconds"
        logging.info("SYSTEM START at\t " + time.asctime(time.localtime(time.time())))
        time.sleep(5)

        GPIO.add_event_detect(pirPin, GPIO.RISING, callback = motion, bouncetime=1000)
        logging.info("Registered PIR GPIO rising edge listener")
        getLightState()
        while 1:
                if time.time() >= thresholdTime:                                # Has the timer expired?
                        setLightState(OFF)                                      # No motion detected for some time, turn lights off
                time.sleep(5)                                                   # Tick every 10 seconds
except KeyboardInterrupt:
        print "Quit"
        logging.info("SYSTEM STOP at \t" + time.asctime(time.localtime(time.time())))
        GPIO.cleanup()
