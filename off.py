import RPi.GPIO as gpio
import time

# Set board numbering to BCM
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

Red = 16
Yellow = 17
Green = 18
# On = 0
# Off = 1

timeSleep = 2

pins = [16, 17, 18]

for i in pins:
	gpio.setup(i, gpio.OUT)
	gpio.output(i, 1)
