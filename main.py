from flask import Flask, render_template, request, Response
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

# Set up the flask app
app = Flask(__name__)		
	
# Set up instance of class
lights = TrafficLights()


############# SETUP FLASK ROUTES ######################
@app.route('/red/<state>')
def red(state):
	print('red: ' + str(state))
	return 'OK', 200

@app.route('/red')
def red_get():
	return lights.get_red()

@app.route('/green/<state>')
def green(state):
	print('green: ' + str(state))
	return 'OK', 200

@app.route('/green')
def green_get():
	return lights.get_green()

@app.route('/yellow/<state>')
def yellow(state):
	print('yellow: ' + str(state))
	return 'OK', 200

@app.route('/yellow')
def yellow_get():
	return lights.get_yellow()


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

	redStatus = 'red' if lights.get_red() else 'black'
	yellowStatus = 'yellow' if lights.get_yellow() else 'black'
	greenStatus = 'green' if lights.get_green() else 'black'
	
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


if __name__ == '__main__':
	app.run(threaded=True, debug=True, host='0.0.0.0')