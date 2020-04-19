from flask import Flask, render_template, request, Response
import time, random
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import traceback
import datetime as dt
import json

from traffic_lights import TrafficLights

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


# Set up the flask app
app = Flask(__name__)		
	
# Set up instance of class
lights = TrafficLights()
	
########## SETUP TIMER ##################

wakeupHour = 6
wakeupMinute = 27 

if(wakeupMinute + 2 >= 60):
	stopHour = wakeupHour + 1
	stopMinute = wakeupMinute - 58
else:
	stopHour = wakeupHour
	stopMinute = wakeupMinute + 2

s.add_job(lights.all_on, 'cron', day_of_week='mon-fri', hour=wakeupHour, minute=wakeupMinute, id='wakeUp')
s.add_job(lights.off, 'cron', day_of_week='mon-fri', hour=stopHour, minute=stopMinute, id='turnOff')
logger.info('Added jobs to wake up and turn off')

#########################################


############# SETUP FLASK ######################

@app.route('/', methods=['POST', 'GET'])
def home():
	if request.method == 'POST':
		if 'on' in request.form:
			lights.all_on()	

		if 'off' in request.form:
			lights.off()

		if 'red' in request.form:
			lights.set_red(1)

		if 'yellow' in request.form:
			lights.set_yellow(1)

		if 'green' in request.form:
			lights.set_green(1)

	redStatus, yellowStatus, greenStatus = ('red', 'yellow', 'green')
	
	return render_template('index.html', red_status=redStatus, yellow_status=yellowStatus, green_status=greenStatus)


# Define simple method to turn on the lights
@app.route('/on', methods=['POST'])
def on():
	if request.method == 'POST':
		lights.all_on()
		return Response(status=200)
	else:
		return Response(status=600)

# Define a simple method to turn off the lights
@app.route('/off', methods=['POST'])
def off():
	if request.method == 'POST':
		lights.off()
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
				
				s.add_job(lights.all_on, 'cron', day_of_week='mon-fri', hour=hour, minute=minute, id='wakeUp')
				s.add_job(lights.off, 'cron', day_of_week='mon-fri', hour=stopHour, minute=stopMinute, id='turnOff')
				
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
	app.run(threaded=True, debug=True, host='0.0.0.0')