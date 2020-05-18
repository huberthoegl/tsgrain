
import config
import logging

if config.PLATFORM == 'rpi':
    import mcp23017   # must have been initlzd with mcp23017.init() 

# Colors: rot, gruen, blau, gelb, violett, tuerkis, weiss

OFF = 'off'
RED = 'red'
GREEN = 'green'
BLUE = 'blue'
WHITE = 'white'
YELLOW = 'yellow'


logger = None


def init():
    global logger
    logger = logging.getLogger(config.TSGRAIN_LOGGER)


def set_led(color=GREEN):
    logger.info("led3c set_led {}".format(color))
    if color == OFF:
        if config.PLATFORM == 'rpi':
            mcp23017.status_led(False, False, False) 
    if color == RED:
        if config.PLATFORM == 'rpi':
            mcp23017.status_led(True, False, False) 
    if color == GREEN:
        if config.PLATFORM == 'rpi':
            mcp23017.status_led(False, True, False) 
    if color == BLUE:
        if config.PLATFORM == 'rpi':
            mcp23017.status_led(False, False, True) 
    if color == YELLOW:
        if config.PLATFORM == 'rpi':
            mcp23017.status_led(True, True, False) 
    if color == WHITE:
        if config.PLATFORM == 'rpi':
            mcp23017.status_led(True, True, True) 


