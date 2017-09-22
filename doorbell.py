#!/usr/bin/python
# doorbell 2.0
# by Jared Thomas (jnthomas0129)

import os
import time
import RPi.GPIO as GPIO
import httplib, urllib
from datetime import datetime

# pins
# This is using one RGB LED and one button 
# these will likely need to be changed unless your wiring setup is identical
button = 5
RED    = 22
GREEN  = 18
BLUE   = 16

# variables
startRecordingMinSec = 1

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

# defines Push Message
def Push(title, message, url):

    # -----------------------------------	
    # PASTE VALUES FOR PUSHOVER.NET BELOW
    # -----------------------------------
    application_token = "remove me and paste  app token"  # <--- "examplelkjsdlfkjsdlfkjsdf"
    user_token        = "remove me and paste user token"  # <--- "examplelksjdflkjsdflkjsdf"

    # Start Connection with Pushover API Server
    conn = httplib.HTTPSConnection("api.pushover.net:443")

    # Send a POST request
    conn.request("POST", "/1/messages.json",
    urllib.urlencode({
    "token": application_token,
    "user": user_token, 
    "title": title, 
    "message": message, 
    "url": url, 
    }), { "Content -type": "application/x-www-form-urlendcoded" })

    conn.getresponse()


# defines button press event
buttonPressedTime = None
def buttonStateChanged(pin):
    global buttonPressedTime

    if not (GPIO.input(pin)):
	# button is down
	if buttonPressedTime is None:
	    
	    # ensure all LEDs off
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
		os.system('arecord -d 2 -f S16_LE -r 41000 Greeting.wav &')
		GPIO.output(RED, True)
		time.sleep(2)
		GPIO.output(RED, False)

		# indicate when playing back with blue
		GPIO.output(BLUE, True)
		os.system('aplay -d 2 -f S16_LE -r 41000 Greeting.wav &')
		time.sleep(2)
		GPIO.output(BLUE, False)
		Push("Doorbell", "You have a message", "")


	    elif elapsed < startRecordingMinSec:

	        # play sound for regular doorbell
		# mp3 file and location will need to be updated based on your setup
	        os.system('mpg123 -q /home/pi/Scripts/doorbell/sounds/doorbell.mp3 &')
		GPIO.output(BLUE, True)
		Push('Doorbell', 'Ding Dong', '')
		GPIO.output(BLUE, False)

try:
    # subscribe to button presses
    GPIO.add_event_detect(button, GPIO.BOTH, callback=buttonStateChanged)

    while True:
        # sleep to reduce CPU usage
        time.sleep(1)

except KeyboardInterrupt:
	print("\n")
	pass

finally:
    GPIO.output(RED, False)
    GPIO.output(GREEN, False)
    GPIO.output(BLUE, False)
    GPIO.cleanup()
