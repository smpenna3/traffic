import time
import traceback
import RPi.GPIO as gpio

## Setup GPIO
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

class TrafficLights():
    # Seconds between switching events
    rate_limit = 0.5

    def __init__(self, red=16, yellow=17, green=18, startoff=True):
        # Setup the gpio pins
        self.red_gpio = red
        self.green_gpio = green
        self.yellow_gpio = yellow

        ## Setup timers for each color channel so they aren't switched too fast
        # The mechanical relays allow switching 10x per second max, but this
        # is rate limited to 2Hz for safety and longevity
        self.red_timer = time.time()
        self.green_timer = time.time()
        self.yellow_timer = time.time()
        
        # Setup the GPIO pins as ouputs
        self.configure_gpio()

        # Turn off the lights to start
        if(startoff):
            self.off()


    def configure_gpio(self):
        gpio.setup([self.red_gpio, self.green_gpio, self.yellow_gpio], gpio.OUT)


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
        if((time.time() - self.red_timer) > self.rate_limit):
            if(state == 'toggle'):
                gpio.output(self.red_gpio, self.get_red())
            elif(state == 1 or state == 'on'):
                gpio.output(self.red_gpio, 0)
            elif(state == 0 or state == 'off'):
                gpio.output(self.red_gpio, 1)
        else:
            print("Red exceeded rate limit!")

    def get_red(self):
        ''' Return the state of the light 

        Important note! States are reversed such that 1 is off and 0 is on
        '''
        return not gpio.input(self.red_gpio)


    def set_green(self, state='toggle'):
        if((time.time() - self.green_timer) > self.rate_limit):
            if(state == 'toggle'):
                gpio.output(self.green_gpio, self.get_green())
            elif(state == 1 or state == 'on'):
                gpio.output(self.green_gpio, 0)
            elif(state == 0 or state == 'off'):
                gpio.output(self.green_gpio, 1)
        else:
            print("Green exceeded rate limit!")

    def get_green(self):
        ''' Return the state of the light 

        Important note! States are reversed such that 1 is off and 0 is on
        '''
        return not gpio.input(self.green_gpio)


    def set_yellow(self, state='toggle'):
        if((time.time() - self.yellow_timer) > self.rate_limit):
            if(state == 'toggle'):
                gpio.output(self.yellow_gpio, self.get_yellow())
            elif(state == 1 or state == 'on'):
                gpio.output(self.yellow_gpio, 0)
            elif(state == 0 or state == 'off'):
                gpio.output(self.yellow_gpio, 1)
        else:
            print("Yellow exceeded rate limit!")

    def get_yellow(self):
        ''' Return the state of the light 

        Important note! States are reversed such that 1 is off and 0 is on
        '''
        return not gpio.input(self.yellow_gpio)