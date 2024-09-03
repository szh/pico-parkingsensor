import time
from time import sleep_us

import neopixel
from machine import Pin, time_pulse_us

# MODIFIED LIBRARY FROM https://github.com/skgsergio/MicropythonLibs/blob/master/Ultrasonic/ultrasonic.py
    
##
# Ultrasonic library for MicroPython's pyboard.
# Compatible with HC-SR04 and SRF04.
#
# Copyright 2018 - Sergio Conde Gómez <skgsergio@gmail.com>
# Copyright 2014 - Mithru Vigneshwara
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

class Ultrasonic(object):
    def __init__(self, trigger_pin, echo_pin, timeout_us=300000):
        # WARNING: Don't use PA4-X5 or PA5-X6 as echo pin without a 1k resistor

        # Default timeout is a bit more than the HC-SR04 max distance (400 cm):
        # 400 cm * 29 us/cm (speed of sound ~340 m/s) * 2 (round-trip)

        self.timeout = timeout_us

        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.off()

        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def distance_in_inches(self):
        return (self.distance_in_cm() * 0.3937)

    def distance_in_cm(self):
        # Send a 10us pulse
        self.trigger.on()
        sleep_us(10)
        self.trigger.off()

        # Wait for the pulse and calc its duration
        time_pulse = time_pulse_us(self.echo, 1, self.timeout)

        if time_pulse < 0:
            # Error value
            return -1

        # Divide the duration of the pulse by 2 (round-trip) and then divide it
        # by 29 us/cm (speed of sound = ~340 m/s)
        return (time_pulse / 2) / 29

# END

# BEGIN MAIN CODE

PIN_TRIGGER = 16
PIN_ECHO = 17
PIN_NEOPIXEL = 28
NEOPIXEL_COUNT = 12
NEOPIXEL_BRIGHTNESS = 0.8
ERROR_COLOR = (255, 0, 255) # Purple
RED_COLOR = (255, 0, 0)
YELLOW_COLOR = (255, 155, 0)
GREEN_COLOR = (0, 255, 0)

ds = Ultrasonic(16, 17)

np = neopixel.NeoPixel(Pin(PIN_NEOPIXEL), NEOPIXEL_COUNT)

def set_neopixel_color(r, g, b):
    # Adjust brightness
    r = int(r * NEOPIXEL_BRIGHTNESS)
    g = int(g * NEOPIXEL_BRIGHTNESS)
    b = int(b * NEOPIXEL_BRIGHTNESS)
    # Set color
    for i in range(NEOPIXEL_COUNT):
        np[i] = (r, g, b)
    np.write()

def clear_neopixel():
    set_neopixel_color(0, 0, 0)

def blink():
    set_neopixel_color(*ERROR_COLOR)
    time.sleep_ms(100)
    clear_neopixel()
    time.sleep_ms(100)

while True:
    distance = ds.distance_in_cm()
    print(distance)
    
    if (distance < 1):
        # Blink error code 3 times
        for i in range(3):
            blink()
    elif (distance < 50):
        # Set color to red
        set_neopixel_color(*RED_COLOR)
    elif (distance < 75):
        # Set color to yellow
        set_neopixel_color(*YELLOW_COLOR)
    elif (distance < 100):
        # Set color to green
        set_neopixel_color(*GREEN_COLOR)
    else:
        # Turn off
        clear_neopixel()
        
    time.sleep_ms(100)
