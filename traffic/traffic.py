from flask import Flask, render_template, request, Response
import time, random

try:
	import RPi.GPIO as gpio
	gpioFlag = True
except:
	print("RPI GPIO not found")
	gpioFlag = False

from apscheduler.schedulers.background import BackgroundScheduler
import logging
import traceback
import datetime as dt
import json


########### PARAMETERS ###################
# Pins for relays
red = 16
yellow = 17
green = 18

debugSet = True
external = False
##########################################
##########################################

# Setup logging
logger = logging.getLogger('mainLog')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(lineno)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)

# Get flask logger
flaskLogger = logging.getLogger('werkzeug')
flaskLogger.setLevel(logging.WARNING)
flaskLogger.addHandler(fh)
flaskLogger.addHandler(sh)

# Setup scheduler
s = BackgroundScheduler(misfire_grace_time=60, max_instances=1, timezone='America/New_York')
s.start()
logger.info('Scheduler setup')

relays = [16, 17, 18]


# Setup GPIO lines
if(gpioFlag):
	try:
		gpio.setmode(gpio.BCM)
		gpio.setwarnings(False)
		for i in relays:
			gpio.setup(i, gpio.OUT)
			gpio.output(i, 1)  # Start with all off
	except:
		logger.error('Could not setup GPIO')
		logger.error(traceback.print_exc())


# Set up the flask app
app = Flask(__name__)


# Define class to control the lights
class trafficLights():
	def __init__(self, red, yellow, green):
		self.red = red
		self.green = green
		self.yellow = yellow
		
	# Turn all off
	def turnOff(self):
		if(gpioFlag):
			try:
				gpio.output(self.red, 1)
				gpio.output(self.green, 1)
				gpio.output(self.yellow, 1)
				logger.info("Turned all off")
				
			except Exception as e:
				logger.error(str(e))
		else:
			logger.info('All off')
		

	# Define function to turn on all lights
	def turnOn(self):
		if(gpioFlag):
			try:
				gpio.output(self.red, 0)
				gpio.output(self.green, 0)
				gpio.output(self.yellow, 0)
				logger.info("Turned all on")

			except Exception as e:
				logger.error(str(e))
		else:
			logger.info('All on')
			
	# Set colors
	def set(self, color, set='toggle'):
		if(gpioFlag):
			try:
				if(color == 'red'):
					if(set == 'toggle'):
						gpio.output(self.red, not gpio.input(self.red))
					elif(set == 'on' or str(set) == '0'):
						gpio.output(self.red, 0)
					elif(set == 'off' or str(set) == '1'):
						gpio.output(self.red, 1)
				
				if(color == 'green'):
					if(set == 'toggle'):
						gpio.output(self.green, not gpio.input(self.green))
					elif(set == 'on' or str(set) == '0'):
						gpio.output(self.green, 0)
					elif(set == 'off' or str(set) == '1'):
						gpio.output(self.green, 1)
				
				if(color == 'yellow'):
					if(set == 'toggle'):
						gpio.output(self.yellow, not gpio.input(self.yellow))
					elif(set == 'on' or str(set) == '0'):
						gpio.output(self.yellow, 0)
					elif(set == 'off' or str(set) == '1'):
						gpio.output(self.yellow, 1)
			except Exception as e:
				logger.error(str(e))
		else:
			logger.info('Set ' + str(color) + ' to ' + str(set))
		
	# Return the status of the lights
	def getStatus(self, light='all'):
		if(gpioFlag):
			try:
				if(gpio.input(red)):
					redStatus = 'black'
				else:
					redStatus = 'red'			

				if(gpio.input(green)):
					greenStatus = 'black'
				else:
					greenStatus = 'green'

				if(gpio.input(yellow)):
					yellowStatus = 'black'
				else:
					yellowStatus = '#ff9900'
					
				if(light == 'all'):
					return redStatus, yellowStatus, greenStatus
				elif(light == 'red'):
					return redStatus
				elif(light == 'yellow'):
					return yellowStatus
				elif(light == 'green'):
					return greenStatus
					
			except Exception as e:
				logger.error(str(e))
				return 'black', 'black', 'black'
		else:
			x = random.randint(0, 4)
			if(x == 0): return 'black', 'black', 'black'
			elif(x == 1): return 'red', 'black', 'green'
			elif(x == 2): return 'red', 'black', 'black'
			elif(x == 3): return 'black', 'yellow', 'black'
			elif(x == 4): return 'black', 'black', 'green'
			
	def getState(self, light):
		if(light == 'red'):
			return gpio.input(self.yellow)
		elif(light == 'yellow'):
			return gpio.input(self.yellow)
		elif(light == 'green'):
			return gpio.input(self.yellow)
			
	
# Set up instance of class
lights = trafficLights(red, yellow, green)
	
########## SETUP TIMER ##################

wakeupHour = 6
wakeupMinute = 27 

if(wakeupMinute + 2 >= 60):
	stopHour = wakeupHour + 1
	stopMinute = wakeupMinute - 58
else:
	stopHour = wakeupHour
	stopMinute = wakeupMinute + 2

s.add_job(lights.turnOn, 'cron', day_of_week='mon-fri', hour=wakeupHour, minute=wakeupMinute, id='wakeUp')
s.add_job(lights.turnOff, 'cron', day_of_week='mon-fri', hour=stopHour, minute=stopMinute, id='turnOff')
logger.info('Added jobs to wake up and turn off')

#########################################


############# SETUP FLASK ######################

@app.route('/', methods=['POST', 'GET'])
def home():
	if request.method == 'POST':
		if 'on' in request.form:
			lights.turnOn()	

		if 'off' in request.form:
			lights.turnOff()

		if 'red' in request.form:
			lights.set('red')

		if 'yellow' in request.form:
			lights.set('yellow')

		if 'green' in request.form:
			lights.set('green')

	redStatus, yellowStatus, greenStatus = lights.getStatus()
	
	return render_template('index.html', red_status=redStatus, yellow_status=yellowStatus, green_status=greenStatus)


# Define simple method to turn on the lights
@app.route('/on', methods=['POST'])
def on():
	if request.method == 'POST':
		lights.turnOn()
		return Response(status=200)
	else:
		return Response(status=600)

# Define a simple method to turn off the lights
@app.route('/off', methods=['POST'])
def off():
	if requet.method == 'POST':
		lights.turnOff()
		return Response(status=200)
	else:
		return Response(status=600)

# Define a method for a notification sequence
@app.route('/text', methods=['POST'])
def textNotification():
	if request.method == 'POST':
		logger.info('Text received')
		previousState = lights.getState('green')
		logger.debug('Previous state: ' + str(previousState))
		lights.set('green', 'off')
		time.sleep(1)
		lights.set('green', 'on')
		time.sleep(1)
		lights.set('green', 'off')
		time.sleep(1)
		lights.set('green', 'on')
		time.sleep(1)
		lights.set('green', 'off')
		time.sleep(1)
		lights.set('green', previousState)
		return Response(status=200)

	else:
		return Response(status=600)
		
# Define a method for configuration  options
@app.route('/config', methods=['GET', 'POST'])
def configuration():
	global wakeupHour, wakeupMinute
	if request.method == 'POST':
		logger.info('New wakeup time ' + str(request.form['wakeup']))
		try:
			hour = int(str(request.form['wakeup']).split(":")[0])
			minute = int(str(request.form['wakeup']).split(":")[1])
			
			if(minute + 2 >= 60):
				stopHour = hour + 1
				stopMinute = minute - 58
			else:
				stopHour = hour
				stopMinute = minute + 2
		
			if(hour < 24 and minute < 60 and hour >= 0 and minute >= 0):
				s.remove_job('wakeUp')
				s.remove_job('turnOff')
				
				s.add_job(lights.turnOn, 'cron', day_of_week='mon-fri', hour=hour, minute=minute, id='wakeUp')
				s.add_job(lights.turnOff, 'cron', day_of_week='mon-fri', hour=stopHour, minute=stopMinute, id='turnOff')
				
				wakeupHour = hour
				wakeupMinute = minute 
			else:
				logger.error('Invalid wakeup time')
		
		except Exception as e:
			logger.error("Couldn't set new wakeup time. " + str(e))
			
		wakeupString = str(wakeupHour) + ":" + str(wakeupMinute)
		return render_template('config.html', wakeupTime = wakeupString)
	
	else:
		wakeupString = str(wakeupHour) + ":" + str(wakeupMinute)
		return render_template('config.html', wakeupTime = wakeupString)

if __name__ == '__main__':
	if(external):
		app.run(threaded=True, debug=debugSet, host='0.0.0.0')
	else:
		app.run(threaded=True, debug=debugSet)
