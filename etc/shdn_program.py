
# Nach einem Beispiel von 
# http://www.netzmafia.de/skripten/hardware/RasPi/Projekt-OnOff/index.html

import RPi.GPIO as GPIO
import subprocess, time, sys, os

# GPIO-Pin 22
PORT = 22

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Zeitdauer des Tastendrucks
duration = 0


def handler(pin):
  global duration

  if not (GPIO.input(pin)):
    # Taste gedrueckt
    print("gedrueckt")
    if duration == 0:
      duration = time.time()
  else:
    print("los")
    # Taste losgelassen
    if duration > 0:
      elapsed = (time.time() - duration)
      duration = 0
      if elapsed >= 3:  # Drei sekunden für Taster drücken
        # add logger
        print("Shutdown -h now")
        subprocess.call(['shutdown', '-h', 'now'], shell=False) 
      elif elapsed >= 0.1: # Entprellzeit
        # add logger
        print("Shutdown -r now")
        subprocess.call(['shutdown', '-r', 'now'], shell=False) 


if __name__ == "__main__":
   GPIO.add_event_detect(PORT, GPIO.BOTH, callback=handler)

   uid = os.getuid() 
   if uid > 0:
      print ("Programm benoetigt root-Rechte!")
      sys.exit(0)

   while True:
      try:
         time.sleep(300)
      except KeyboardInterrupt:
         print ("Bye")
         sys.exit(0)

