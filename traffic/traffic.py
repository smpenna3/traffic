from flask import Flask, render_template, request, Response
import time
try:
	import RPi.GPIO as gpio
except:
	print("RPI GPIO not found")

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

debugSet = False
external = True
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


# Setup scheduler
s = BackgroundScheduler(misfire_grace_time=60, max_instances=1, timezone='America/New_York')
s.start()
logger.info('Scheduler setup')

relays = [16, 17, 18]

# Setup GPIO lines
try:
	gpio.setmode(gpio.BCM)
	gpio.setwarnings(False)
	for i in relays:
		gpio.setup(i, gpio.OUT)
		gpio.output(i, 1)  # Start with all off
except:
	logger.error('Could not setup GPIO')
logger.error(traceback.print_exc())

app = Flask(__name__)

def turnOff():
	gpio.output(red, 1)
	gpio.output(green, 1)
	gpio.output(yellow, 1)

	logger.info("Turned all off")

def turnOn():
	gpio.output(red, 0)
	gpio.output(green, 0)
	gpio.output(yellow, 0)

	logger.info("Turned all on")


########## SETUP TIMER ##################

s.add_job(turnOn, 'cron', day_of_week='mon-fri', hour=6, minute=40, id='wakeUp')
s.add_job(turnOff, 'cron', day_of_week='mon-fri', hour=6, minute=43, id='turnOff')
logger.info('Added jobs to wake up and turn off')

#########################################


############# SETUP FLASK ######################

@app.route('/', methods=['POST', 'GET'])
def home():
	if request.method == 'POST':
		if 'on' in request.form:
			turnOn()	

		if 'off' in request.form:
			turnOff()

		if 'red' in request.form:
			gpio.output(red, not gpio.input(red))

		if 'yellow' in request.form:
			gpio.output(yellow, not gpio.input(yellow))

		if 'green' in request.form:
			gpio.output(green, not gpio.input(green))

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

	return render_template('index.html', red_status=redStatus, yellow_status=yellowStatus, green_status=greenStatus)


# Define simple REST API accessible method to turn on the lights
@app.route('/on', methods=['POST'])
def on():
	if request.method == 'POST':
		turnOn()
		return Response(status=200)
	else:
		return Response(status=600)

# Define a simple RESTFUL method to turn off the lights
@app.route('/off', methods=['POST'])
def off():
	if requet.method == 'POST':
		turnOff()
		return Response(status=200)
	else:
		return Response(status=600)

@app.route('/text', methods=['POST'])
def textNotification():
	if request.method == 'POST':
		logger.info('Text received')
		previousState = gpio.input(green)
		logger.debug('Previous state: ' + str(previousState))
		gpio.output(green, 1)
		time.sleep(1)
		gpio.output(green, 0)
		time.sleep(1)
		gpio.output(green, 1)
		time.sleep(1)
		gpio.output(green, 0)
		time.sleep(1)
		gpio.output(green, 1)
		time.sleep(1)
		gpio.output(green, previousState)
		return Response(status=200)

	else:
		return Response(status=600)

if __name__ == '__main__':
	if(external):
		app.run(threaded=True, debug=debugSet, host='0.0.0.0')
	else:
		app.run(threaded=True, debug=debugSet)
