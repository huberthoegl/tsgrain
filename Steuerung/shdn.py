# Nach einem Beispiel von 
# http://www.netzmafia.de/skripten/hardware/RasPi/Projekt-OnOff/index.html

import subprocess, time, sys, os
import config
import logging
import RPi.GPIO as GPIO
import led3c

logger = logging.getLogger(config.TSGRAIN_LOGGER)


# must be run as root
uid = os.getuid() 
if uid > 0:
  logger.error("shdn must be run as root")
  sys.exit(0)


# Zeitdauer des Tastendrucks
duration = 0


def handler(pin):
  '''see gpio.py'''

  global duration

  if not (GPIO.input(pin)):
    # Taste gedrueckt
    led3c.set_led(color=led3c.WHITE)
    if duration == 0:
      duration = time.time()
  else:
    # Taste losgelassen
    if duration > 0:
      elapsed = (time.time() - duration)
      duration = 0
      if elapsed >= 3:  # laenger als 3 Sekunden 
        led3c.set_led(color=led3c.VIOLET)
        logger.info("shutdown -h now (elapsed={:3.1f})".format(elapsed))
        subprocess.call(['shutdown', '-h', 'now'], shell=False) 
      elif elapsed >= 0.1: # Entprellzeit
        # 0.1 bis < 3 sek
        led3c.set_led(color=led3c.BLUE)
        logger.info("shutdown -r now (elapsed={:3.1f})".format(elapsed))
        subprocess.call(['shutdown', '-r', 'now'], shell=False) 

