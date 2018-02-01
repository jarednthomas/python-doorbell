#!/usr/bin/python
"""
doorbell
~~~~~~~~

Python based doorbell for the Raspberry Pi
"""

import os
import time
import RPi.GPIO as GPIO
from datetime import datetime

# pins (BCM) https://pinout.xyz/
button = 4
RED = 25
GREEN = 24
BLUE = 23

# variables
startRecordingMinSec = 1

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

buttonPressedTime = None
def buttonStateChanged(pin):
    """ Defines Button Press Event """
    global buttonPressedTime

    if not (GPIO.input(pin)):
        if buttonPressedTime is None:
            GPIO.output(RED, False)
            GPIO.output(GREEN, False)
            GPIO.output(BLUE, False)
            buttonPressedTime = datetime.now()

    else:
        if buttonPressedTime is not None:
            elapsed = (datetime.now() - buttonPressedTime).total_seconds()
            buttonPressedTime = None

            # if button was held long enough
            if elapsed >= startRecordingMinSec:
                # prompt user
                GPIO.output(GREEN, True)
                os.system('mpg123 -q ./sounds/whos_there.mp3 &')
                time.sleep(1.25)
                GPIO.output(GREEN,False)
                # indicate recording with red
                os.system('arecord -d 2 -f S16_LE -r 41000 ./sounds/recent_greeting.wav &')
                GPIO.output(RED, True)
                time.sleep(2)
                GPIO.output(RED, False)
                # indicate playback with blue
                GPIO.output(BLUE, True)
                os.system('aplay -d 2 -f S16_LE -r 41000 ./sounds/recent_greeting.wav &')
                time.sleep(2)
                GPIO.output(BLUE, False)

            # if button was not held long enough, regular buzzer
            elif elapsed < startRecordingMinSec:
                GPIO.output(BLUE, True)
                os.system('mpg123 -q ./sounds/doorbuzz.mp3 &')
                time.sleep(.2)
                GPIO.output(BLUE, False)

try:
    GPIO.add_event_detect(button, GPIO.BOTH, callback=buttonStateChanged)
    while True:
        time.sleep(2) # sleep to reduce CPU usage

except KeyboardInterrupt:
    print("\n")

finally:
    GPIO.output(RED, False)
    GPIO.output(GREEN, False)
    GPIO.output(BLUE, False)
    GPIO.cleanup()
