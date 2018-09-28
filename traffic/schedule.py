import RPi.GPIO as gpio
import time
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Setup logger
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
FORMAT = logging.Formatter('%(asctime)-15s - %(levelname)s -  %(message)s')
fh = logging.FileHandler(filename='log.log')
fh.setFormatter(FORMAT)
fh.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setFormatter(FORMAT)
sh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(sh)

s = BackgroundScheduler(coalescing=True, misfire_grace_time=5, max_instances=1, timezone='America/New_York')
s.start()
logger.info('Scheduler set up')

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

logger.info('Pins initialized')

def allOn():
	for i in pins:
		gpio.output(i, 0)
	logger.info('All on, good morning!')

# Setup timer
s.add_job(allOn, 'cron', hour=6, minute=30, id='wakeUp')
logger.info('Job added')

while(1):
	time.sleep(60)
