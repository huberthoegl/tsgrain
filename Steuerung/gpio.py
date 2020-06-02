
from mcp23017 import mcp_handler

import RPi.GPIO as GPIO
import shdn

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    interrupt_expand = 17   # GPIO17 to interrupt output of MCP23017
    interrupt_clock = 27    # GPIO27 to interrupt output of DS3231
    GPIO.setup(interrupt_expand, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(interrupt_clock, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(interrupt_expand, GPIO.RISING, 
                          callback=mcp_handler, bouncetime=50)

    # GPIO22 boot/shutdown button
    shutdown_pin = 22  
    GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(shutdown_pin, GPIO.BOTH, callback=shdn.handler)


