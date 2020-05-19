'''Pushbuttons on RPi with MCP23017 (I2C)
'''

import config
import mcp23017

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


_instance = None


def pb_press_handler(ir_nr, key_nr):
    _instance._press(key_nr)

def pb_release_handler(ir_nr, key_nr):
    _instance._release(key_nr)


class PButtons:

    def __init__(self):
        # only one instantiation is allowed!
        global _instance
        self.cblist = []
        self.panelkey = None
        self.pressed = False
        _instance = self
        mcp23017.add_press_handler(pb_press_handler)
        mcp23017.add_release_handler(pb_release_handler)

    def _press(self, key_nr):
        '''The _press() method can be called multiple times, but it calls
        the callback functions only at the first time. This is a good 
        behaviour when the low-level key fires repeatedly on a longer 
        press duration.
        '''
        if key_nr == 0:
            self.panelkey = PB1
        elif key_nr == 1:
            self.panelkey = PB2
        elif key_nr == 2:
            self.panelkey = PB3
        elif key_nr == 3:
            self.panelkey = PB4
        elif key_nr == 4:
            self.panelkey = PB5
        elif key_nr == 5:
            self.panelkey = PB6
        elif key_nr == 6:
            self.panelkey = PB7
        elif key_nr == 7:
            self.panelkey = PBAutoOff
        else:
            return
        if not self.pressed:
            self.pressed = True
            for f in self.cblist:
                f(self.panelkey)

    def _release(self, key_nr): 
        self.pressed = False
        self.panelkey = None

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

