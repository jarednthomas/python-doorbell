#!/usr/bin/python
# doorbell 2.0
# by Jared Thomas (jnthomas0129)

import os
import time
import RPi.GPIO as GPIO
import httplib, urllib
from datetime import datetime

# Pins (BCM) https://pinout.xyz/
button_pin = 4
red_pin = 25
green_pin = 24
blue_pin = 23

# Variables
buttonHoldDuration = 1

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
    """ Defines Button Press Event """
    global buttonPressedTime

    if not (GPIO.input(pin)):
        if buttonPressedTime is None:
            GPIO.output(red_pin, False)
            GPIO.output(green_pin, False)
            GPIO.output(blue_pin, False)
            buttonPressedTime = datetime.now()

    else:
        if buttonPressedTime is not None:
            elapsed = (datetime.now() - buttonPressedTime).total_seconds()
            buttonPressedTime = None

            # if button was held long enough
            if elapsed >= buttonHoldDuration:
                # prompt user
                GPIO.output(green_pin, True)
                os.system('mpg123 -q ./sounds/whos_there.mp3 &')
                time.sleep(1.25)
                GPIO.output(green_pin,False)
                # indicate recording with red
                os.system('arecord -d 2 -f S16_LE -r 41000 ./sounds/recent_greeting.wav &')
                GPIO.output(red_pin, True)
                time.sleep(2)
                GPIO.output(red_pin, False)
                # indicate playback with blue
                GPIO.output(blue_pin, True)
                os.system('aplay -d 2 -f S16_LE -r 41000 ./sounds/recent_greeting.wav &')
                Push("Doorbell", "You have a message", "")
                time.sleep(2)
                GPIO.output(blue_pin, False)

            # if button was not held long enough, regular buzzer
            elif elapsed < buttonHoldDuration:
                GPIO.output(blue_pin, True)
                os.system('mpg123 -q ./sounds/doorbuzz.mp3 &')
                Push('Doorbell', 'Ding Dong', '')
                time.sleep(.2)
                GPIO.output(blue_pin, False)

try:
    print("[Doorbell Active] CTRL-C to Quit")
    GPIO.add_event_detect(button_pin, GPIO.BOTH, callback=buttonStateChanged)
    while True:
        time.sleep(1) # sleep to reduce CPU usage

except KeyboardInterrupt:
    print("\n")

finally:
    GPIO.output(red_pin, False)
    GPIO.output(green_pin, False)
    GPIO.output(blue_pin, False)
    GPIO.cleanup()
