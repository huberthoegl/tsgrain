'''Enable I2C bus with "sudo raspi-config"
Python package python3-smbus must be installed.
'''

import smbus
import time
import array
import math
import logging
import conf
 
bus = smbus.SMBus(1)

logger = logging.getLogger(conf.TSGRAIN_LOGGER)

press_handler = None
release_handler = None


def mcp_handler(intr_nr):
    '''Interrupt Service Routine fuer I2C Expander 2, PORTA
    '''
    key_nr = read_interrupt()  
    if key_nr == None:
        logger.info("mcp_handler: read_interrupt NONE KEY ###############################")
        read_tasten()  # dummy read to clear interrupt condition
        bus.write_byte_data(expand_2, GPINTENA_2, 0xff)  # enable interrupts ???
        return  # key could not be identified
    time.sleep(0.1)
    capa = read_intcapa()
    if capa == 255:
        logger.info("mcp_handler: calling release_handler({}, {}, capa={})".format(intr_nr, key_nr, capa))
        release_handler(intr_nr, key_nr)
        read_tasten()  # dummy read to clear interrupt condition
    else:
        logger.info("mcp_handler: calling press_handler({}, {}, capa={})".format(intr_nr, key_nr, capa))
        if capa == 0xfe: # P1
            press_handler(intr_nr, key_nr)
        elif capa == 0xfd: # P2
            press_handler(intr_nr, key_nr)
        elif capa == 0xfb: # P3
            press_handler(intr_nr, key_nr)
        elif capa == 0xf7: # P4
            press_handler(intr_nr, key_nr)
        elif capa == 0xef: # P5
            press_handler(intr_nr, key_nr)
        elif capa == 0xdf: # P6
            press_handler(intr_nr, key_nr)
        elif capa == 0xbf: # P7
            press_handler(intr_nr, key_nr)
        elif capa == 0x7f: # PBAutoOff
            press_handler(intr_nr, key_nr)
        read_tasten()  # dummy read to clear interrupt condition


def add_press_handler(f):
    # f(ir_nr, key_nr)
    global press_handler
    press_handler = f


def add_release_handler(f):
    # f(ir_nr, key_nr)
    global release_handler
    release_handler = f


def init():
    global expand_1, expand_2, OLATA_1, OLATB_1, OLATA_2, OLATB_2, INTFA_2, \
            GPIOA_2, GPINTENA_2, INTCAPA_2

    #Konfiguration I2C
    ##### Erweiterungsboard 1 -- Output-Platine
     
    expand_1 = 0x27 # i2c Adresse
    IODIRA_1 = 0x00 # Pin Register 
    IODIRB_1 = 0x01 # Pin Register
    OLATA_1 = 0x14 # Register fuer GPA Ausgabe
    OLATB_1 = 0x15 # Register fuer GPB Ausgabe
      
    # Definiere GPA/OLATA und GPB/OLATB als Output // 1 für Ausgabe, 
    # 0 für Eingabe
    bus.write_byte_data(expand_1,IODIRA_1,0x00)
    bus.write_byte_data(expand_1,IODIRB_1,0x00)
     
    # GPA/OLATA und GPB/OLATB default Werte setzen
    bus.write_byte_data(expand_1,OLATA_1,0x00)
    bus.write_byte_data(expand_1,OLATB_1,0xFF)

    ##### Erweiterungsboard 2 -- Input-Platine
    expand_2 = 0x23 # i2c Adresse
    IODIRA_2 = 0x00 # Pin Register
    IODIRB_2 = 0x01 # Pin Register
    GPPUA_2 = 0x0C # Register für Pull-Up Widerstände
    GPIOA_2 = 0x12 # Register fuer GPA Eingabe
    OLATB_2 = 0x15 # Register fuer GPB Ausgabe
      
    # Definiere GPA und GPB als Input
    # Alle 8 GPA sind als Input und Interrupt eingestellt
    bus.write_byte_data(expand_2,IODIRA_2,0xFF) 
    bus.write_byte_data(expand_2,IODIRB_2,0x00)

    # GPB als Output deklariert für Status LED
    bus.write_byte_data(expand_2,OLATB_2,0x00) 

    bus.write_byte_data(expand_2,GPPUA_2, 0xFF) 

    # Konfiguration für Interrupt Board2-GPB
    IOCONA_2 = 0x0A # Konfigurationsregister für INTPOL
    INTCONA_2 = 0x08 # Interrupt auf Abweichung vom Standartwert festlegen
    DEFVALA_2 = 0x06 # Standartwert des Pins
    GPINTENA_2 = 0x04 # Interrupt für welchen Pin festlegen
    INTCAPA_2 = 0x10
    INTFA_2 = 0x0E #Interrupt Flag register

    bus.write_byte_data(expand_2, GPINTENA_2, 0xFF) #pins on interrupt
    bus.write_byte_data(expand_2, DEFVALA_2, 0xFF) #standartwert 1
    # bus.write_byte_data(expand_2, INTCONA_2, 0xFF) #1: interrupt auf abweichung von Defval, 0: interrupt auf flanke
    bus.write_byte_data(expand_2, INTCONA_2, 0x00) #1: interrupt auf abweichung von Defval, 0: interrupt auf flanke

    iocon = bus.read_byte_data(expand_2, IOCONA_2) #IOCON register bearbeiten
    iocon = iocon | 0b01111010
    # iocon = 0x3a
    bus.write_byte_data(expand_2, IOCONA_2, iocon)

    # Starten des Interrupts durch Auslesen GPIO
    Gpio_wert = bus.read_byte_data(expand_2, GPIOA_2) 




def init2():
    global expand_1, expand_2, OLATA_1, OLATB_1, OLATA_2, OLATB_2, INTFA_2, \
            GPIOA_2, GPINTENA_2, INTCAPA_2

    expand_2 = 0x23 # i2c Adresse
    GPINTENA_2 = 0x04 # Interrupt für welchen Pin festlegen
    INTCONA_2 = 0x08 # Interrupt auf Abweichung vom Standartwert festlegen
    bus.write_byte_data(expand_2, GPINTENA_2, 0xFF) #pins on interrupt
    bus.write_byte_data(expand_2, INTCONA_2, 0x00) #1: interrupt auf abweichung von Defval, 0: interrupt auf flanke



def output_write(wert):
    '''Each bit in wert is 0 (inactive) or 1 (active). The output driver 
    is driven active low, i.e. we have to flip each bit.
    '''
    wert = ~wert
    bus.write_byte_data(expand_1, OLATB_1, wert)
    

def led_write(wert):
    bus.write_byte_data(expand_1, OLATA_1, wert)
      

def status_led(r, g, b):
    wert = 0
    if r == True:
        wert = wert+1
    if g == True:
        wert = wert+4
    if b == True:
        wert = wert+2    
    bus.write_byte_data(expand_2,OLATB_2,wert)


def read_interrupt():
    '''Gibt zurueck, welche Taste gedrueckt wurde (0...7). 
    '''
    irwert = bus.read_byte_data(expand_2, INTFA_2)
    mask = 0x01
    i = 0
    while i < 8:
        if mask & irwert:
            break
        else:
            mask <<= 1
            i += 1
    #print("read_interrupt: irwert={} i={}".format(irwert, i))
    if 0 <= i <= 7:
        return i
    else:
        return None


def read_tasten():
    '''Manual: "The interrupt condition is cleared after the LSB of the data is clocked out during
    a read command of GPIO or INTCAP."
    '''
    return bus.read_byte_data(expand_2, GPIOA_2) 
    

def read_intcapa():
    '''Manual: "The interrupt condition is cleared after the LSB of the data is clocked out during
    a read command of GPIO or INTCAP."
    '''
    return bus.read_byte_data(expand_2, INTCAPA_2) 



def setDefaultRelaisOutput(): # sofortiges Setzen beim Starten der Steuerung
    bus.write_byte_data(expand_1, OLATB_1, 0xFF)


def cleanup():
    # called on program exit with Ctrl-C
    output_write(0x00)


def my_press_handler(ir_nr, key_nr):
    print("Button pressed. n = {}.".format(key_nr))


def my_release_handler(ir_nr, key_nr):
    print("Button released. n = {}.".format(key_nr))


if __name__ == "__main__":

    import atexit
    atexit.register(cleanup)

    add_press_handler(my_press_handler)
    add_release_handler(my_release_handler)

    init()

    status_led(True, True, True)
  
    # Siehe auch interrupt_routine_expand()
