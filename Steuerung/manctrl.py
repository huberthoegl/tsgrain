'''Manual pushbutton controller.
'''

import config
import monodelay
import logging
import output
if config.PLATFORM == 'pc':
   import pbutton_pc as pbutton
else:  # PLATFORM == 'rpi'
   import pbutton_rpi as pbutton
   import mcp23017
from singleton import Singleton
import db


MC_ACTIVE = 'MC_KEY'   # manual control active
MC_INACTIVE = 'MC_INACTIVE' # ... inactive 


class ManCtrl(Singleton):

    def __init__(self, ticks=None, out=None):
        self.out = output.Output()
        self.logger = logging.getLogger(config.TSGRAIN_LOGGER)
        self.state = MC_INACTIVE
        self.disabled = False
        if ticks: self.dtimer = monodelay.Monodelay(ticks)
        self.key = None
        self.db = db.RainDB()

    def pb_pressed(self, key):
        '''Pushbutton PB1-PB7 and PBAutoOff press events. 
        '''
        if key == pbutton.PBAutoOff:
            # XXX do something
            return

        if key not in pbutton.MAN_KEYS or self.disabled:
            self.state = MC_INACTIVE
            self.key = None
            return

        if not self.disabled and self.state == MC_ACTIVE:
            # stop timer if _same_ button is pressed again
            if key == self.key:
               # same key pressed
               self.dtimer.finish()  # will call delay_end()!
               self.logger.info("pb_pressed: forced manual timer stop for {}".format(key))

        elif not self.disabled and self.state == MC_INACTIVE:
            self.key = key
            self.state = MC_ACTIVE
            delay_in_s = int(self.db.get_setting_val('manual_delay'))*config.SEC_PER_MIN
            self.dtimer.set_delay(delay_in_s)
            self.dtimer.set_cb(self.delay_end)
            self.dtimer.run()
            self.logger.info("pb_pressed: starting manual timer for {}".format(self.key))
            self.out.on(pbutton.key_to_index(key))

        else:
            self.logger.info("pb_pressed: button {} ignored".format(key))

    def delay_end(self):
        '''called when timer has expired or when the button has been pressed a second time.
        '''
        self.state = MC_INACTIVE
        self.logger.info("pb_pressed: manual timer expired for {}".format(self.key))
        self.out.off(pbutton.key_to_index(self.key))
        self.key = None

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False
        if self.state == MC_INACTIVE:
            # Do not clear outputs when manual control was already enabled 
            # and a manual timer is running.
            self.out.all_off()


