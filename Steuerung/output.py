'''Control the outputs.

The output numbers n are 0 (bit0) to 6 (bit6).
'''

import config
from singleton import Singleton
if config.PLATFORM == 'rpi':
    import mcp23017



if config.PLATFORM == 'pc':
    def write_outputs_and_leds(bits):
        print("PC only: write_outputs_and_leds: {:02x}".format(bits))
else:
    def write_outputs_and_leds(bits):
        mcp23017.output_write(bits) 
        mcp23017.led_write(bits) 


class Output(Singleton):

    def __init__(self):
        self._out = 0  # bit field

    def on(self, n):
        '''Switch on output n. Other previously active outputs are _not
        changed_! 
        '''
        self._out |= (1 << n)    # set bit n
        write_outputs_and_leds(self._out)

    def on1(self, n):
        '''Switch on only output n. All other outputs are off. 
        '''
        self._out = (1 << n)    # set only bit n 
        write_outputs_and_leds(self._out)

    def off(self, n):
        '''Switch off output n. Other previously active outputs are _not
        changed_! 
        '''
        self._out &= ~(1 << n)   # clear bit n
        write_outputs_and_leds(self._out)

    def all_off(self):
        self._out = 0x00
        write_outputs_and_leds(self._out)

    def get(self):
        return self._out  # return all output bits
 
    


def print_bits(n):
    for i in range(7, -1, -1):
       if n & (1 << i):
           print("1", end="")
       else:
           print("0", end="")
    print()


if __name__ == "__main__":
    o = Output()
    o.on(0)
    o.on(7)
    o.on(1)
    o.off(7)
    print_bits(~o._out)

