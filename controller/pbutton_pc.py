'''Pushbutton simulation on Linux PC keyboard
Uses keys 1, 2, 3, 4, 5, 6, 7 and 0 (Auto Off)
'''

import conf
import logging
from pynput import keyboard

logger = logging.getLogger(conf.TSGRAIN_LOGGER)

# Panelkeys
PB1 = 'PB1'
PB2 = 'PB2'
PB3 = 'PB3'
PB4 = 'PB4'
PB5 = 'PB5'
PB6 = 'PB6'
PB7 = 'PB7'
PBAutoOff = 'PBAutoOff'

MAN_KEYS = (PB1, PB2, PB3, PB4, PB5, PB6, PB7)

def key_to_index(key):
    if key == PB1:
        return 0
    elif key == PB2:
        return 1
    elif key == PB3:
        return 2
    elif key == PB4:
        return 3
    elif key == PB5:
        return 4
    elif key == PB6:
        return 5
    elif key == PB7:
        return 6
    elif key == PBAutoOff:
        return 7


class PButtons:
    def __init__(self):
        listener = keyboard.Listener(on_press=self._press, 
                                     on_release=self._release)
        logger.info("pynput: starting keyboard listener thread")
        listener.start()
        self.cblist = []
        self.panelkey = None
        self.pressed = False

    def _release(self, key):
        self.pressed = False

    def _press(self, key):
        '''The _press() method can be called multiple times, but it calls
        the callback functions only at the first time. This is a good 
        behaviour to handle automatic key press repetition.
        '''
        #print("you pressed:", key, type(key), key.char, type(key.char))
        if hasattr(key, 'char'):
            if key.char == '1':
                self.panelkey = PB1
            elif key.char == '2':
                self.panelkey = PB2
            elif key.char == '3':
                self.panelkey = PB3
            elif key.char == '4':
                self.panelkey = PB4
            elif key.char == '5':
                self.panelkey = PB5
            elif key.char == '6':
                self.panelkey = PB6
            elif key.char == '7':
                self.panelkey = PB7
            elif key.char == '0':
                self.panelkey = PBAutoOff
            else:
                return
        else:
            return
        if not self.pressed:
            self.pressed = True
            for f in self.cblist:
                f(self.panelkey)

    def subscribe(self, cb):
        self.cblist.append(cb)

    def unsubscribe(self, cb):
        self.cblist.remove(cb)



if __name__ == "__main__":
    import time

    def hello(panelkey):
        print("callback hello:", panelkey)

    def bunny(panelkey):
        print("callback bunny:", panelkey)

    b = PButtons()
    b.subscribe(hello)
    b.subscribe(bunny)

    n = 0
    while n < 10:
        time.sleep(1)
        n = n + 1

