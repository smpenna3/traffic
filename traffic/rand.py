import RPi.GPIO as gpio
import time
from random import randint

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

try:
	while(1):
		gpio.output(Red, randint(0, 1))
		gpio.output(Green, randint(0, 1))
		gpio.output(Yellow, randint(0, 1))
		time.sleep(1)

except:
	gpio.output(Red, 1)
	gpio.output(Green, 1)
	gpio.output(Yellow, 1)
