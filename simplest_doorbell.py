#!/usr/bin/env python3
"""
doorbell.py
~~~~~~~~~~~

Python based doorbell script for the Raspberry Pi
"""

import os
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

switch_pin = 18
led_pin = 23

GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_pin, GPIO.OUT)

led_state = False
old_input_state = True                                             # pulled-up
print("[Doorbell Active] CTRL-C to Quit")
try:

    while True:
        new_input_state = GPIO.input(switch_pin)                   # down
        if new_input_state == True and old_input_state == False:   # pressed
            led_state = not led_state
            os.system('aplay -q /home/pi/Scripts/doorbell/sounds/dong.wav &')
        elif new_input_state == False and old_input_state == True: # released
            led_state = not led_state
            os.system('aplay -q /home/pi/Scripts/doorbell/sounds/ding.wav &')
	# update input state and led state 
        old_input_state = new_input_state
        GPIO.output(led_pin, led_state)

except KeyboardInterrupt:
    print("\n")

finally:
    GPIO.output(led_pin, False)
    GPIO.cleanup()
