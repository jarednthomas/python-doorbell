#!/usr/bin/python
"""
doorbell
~~~~~~~~

Python based doorbell for the Raspberry Pi
"""

import os
import time
import RPi.GPIO as GPIO
import httplib, urllib
from subprocess import call
from datetime import datetime

# pins (BCM) https://pinout.xyz/
button = 4
RED    = 25
GREEN  = 24
BLUE   = 23

# variables
startRecordingMinSec = 1

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

# defines button press event
buttonPressedTime = None
def buttonStateChanged(pin):
    global buttonPressedTime
    if not (GPIO.input(pin)):
	# button is down
	if buttonPressedTime is None:
	    # reset LEDs
	    GPIO.output(RED, False)
	    GPIO.output(GREEN, False)
	    GPIO.output(BLUE, False)
	    buttonPressedTime = datetime.now()
    else:
	# button is up
	if buttonPressedTime is not None:
            elapsed = (datetime.now() - buttonPressedTime).total_seconds()
	    buttonPressedTime = None

	    # button was held long enough
	    if elapsed >= startRecordingMinSec:

	        # prompt for recording input
		# mp3 file and location will need to be updated based on your setup
		GPIO.output(GREEN, True)
		os.system('mpg123 -q /home/pi/Scripts/doorbell/sounds/whos_there.mp3 &')
		time.sleep(1.25)
		GPIO.output(GREEN,False)

		# indicate recording with red
		os.system('arecord -d 2 -f S16_LE -r 41000 ./sounds/Greeting.wav &')
		GPIO.output(RED, True)
		time.sleep(2)
		GPIO.output(RED, False)

		# indicate when playing back with blue
		GPIO.output(BLUE, True)
		os.system('aplay -d 2 -f S16_LE -r 41000 ./sounds/Greeting.wav &')
		time.sleep(2)
		GPIO.output(BLUE, False)

	    # button was not held long enough
	    elif elapsed < startRecordingMinSec:

	        # play sound for regular doorbell
		# mp3 file and location will need to be updated based on your setup
		GPIO.output(BLUE, True)
	        os.system('mpg123 -q /home/pi/Scripts/doorbell/sounds/doorbuzz.mp3 &')
		time.sleep(.2)
		GPIO.output(BLUE, False)

try:
    # subscribe to button presses
    GPIO.add_event_detect(button, GPIO.BOTH, callback=buttonStateChanged)

    while True:
        # sleep to reduce CPU usage
        time.sleep(2)

except KeyboardInterrupt:
	print("\n")
	pass

finally:
    GPIO.output(RED, False)
    GPIO.output(GREEN, False)
    GPIO.output(BLUE, False)
    GPIO.cleanup()
