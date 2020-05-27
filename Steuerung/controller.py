
# controller

import config
import tick
import manctrl
import autoctrl
import output
import logging
import sys
import time
from singleton import Singleton

if config.PLATFORM == 'pc':
   import pbutton_pc as pbutton
else:  # PLATFORM == 'rpi'
   import pbutton_rpi as pbutton
   import gpio
   gpio.init()
   import mcp23017
   mcp23017.init()

import led3c
led3c.init()

ticks = tick.Tick()


# states
AUTO_STATE = 'active-state'
MAN_STATE = 'man-state'


class Controller(Singleton):

    def __init__(self):
        self.logger = logging.getLogger(config.TSGRAIN_LOGGER)
        led3c.set_led(led3c.GREEN)
        ticks.start()
        self.state = MAN_STATE
        self.out = output.Output()
        self.mc = manctrl.ManCtrl(ticks=ticks)  # singleton
        self.pb = pbutton.PButtons()
        self.pb.subscribe(self.mc.pb_pressed)
        self.ac = autoctrl.AutoCtrl()
        self.ac.register_auto_on_hdl(self.auto_on_hdl)
        self.ac.register_auto_off_hdl(self.auto_off_hdl)
        self.logger.info("Controller instance created")

    def auto_on_hdl(self):
        # enter AUTO_STATE -- called every minute when automatic is 
        # active. Active court is stored in self.ac.auto_court.
        if self.state == MAN_STATE:
            # MAN_STATE -> AUTO_STATE
            self.logger.info("controller MAN -> AUTO")
            led3c.set_led(led3c.RED)
        self.state = AUTO_STATE
        # Only this one on, all others off. Note that the last output in 
        # a sequence is not actively switched off.  It is cleared by 
        # mc.enable() in auto_off_hdl().
        self.out.on1(self.ac.auto_court) 
        self.mc.disable()

    def auto_off_hdl(self):
        # enter MAN_STATE -- is called every minute if we have jobs, but these
        # jobs are not intime.  If we have no jobs, this function is not called.
        if self.state == AUTO_STATE:
            # AUTO_STATE -> MAN_STATE
            self.logger.info("controller AUTO -> MAN")
            led3c.set_led(led3c.GREEN)
        self.state = MAN_STATE
        self.mc.enable()

    def run(self):
        #try:
        while True:
            time.sleep(1)
        #except:
        #    e = sys.exc_info()[0]
        #    print(e)

