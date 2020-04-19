import time
import traceback
import RPi.GPIO as gpio

## Setup GPIO
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

class TrafficLights():
    def __init__(self, red=16, yellow=17, green=18, startoff=True):
        self.red = red
        self.green = green
        self.yellow = yellow
        
        self.configure_gpio()

        if(startoff):
            self.off()

    def configure_gpio(self):
        gpio.setup([self.red, self.green, self.yellow], gpio.OUT)

    # Turn all off
    def off(self):
        self.set_red(0)
        self.set_green(0)
        self.set_yellow(0)
        

    # Define function to turn on all lights
    def all_on(self):
        self.set_red(1)
        self.set_green(1)
        self.set_yellow(1)
            
    
    def set_red(self, state='toggle'):
        if(state == 'toggle'):
            gpio.output(self.red, not gpio.input(self.red))
        elif(state == 1 or state == 'on'):
            gpio.output(self.red, 1)
        elif(state == 0 or state == 'off'):
            gpio.output(self.red, 0)

    def set_green(self, state='toggle'):
        if(state == 'toggle'):
            gpio.output(self.green, not gpio.input(self.green))
        elif(state == 1 or state == 'on'):
            gpio.output(self.green, 1)
        elif(state == 0 or state == 'off'):
            gpio.output(self.green, 0)

    def set_yellow(self, state='toggle'):
        if(state == 'toggle'):
            gpio.output(self.yellow, not gpio.input(self.yellow))
        elif(state == 1 or state == 'on'):
            gpio.output(self.yellow, 1)
        elif(state == 0 or state == 'off'):
            gpio.output(self.yellow, 0)