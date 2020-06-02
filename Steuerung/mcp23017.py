'''Enable I2C bus with "sudo raspi-config"
Python package python3-smbus must be installed.
'''

import smbus
import time
import array
import math
import logging
import config
 
bus = smbus.SMBus(1)

logger = logging.getLogger(config.TSGRAIN_LOGGER)

press_handler = None
release_handler = None


def mcp_handler(intr_nr):
    '''Interrupt Service Routine fuer I2C Expander 2, PORTA

    Diese Variante erzeugt nur einen Interrupt beim Druecken der Taste. Das Loslassen wird
    durch Polling festgestellt. 

    GPIO.add_event_detect(17, 
                          GPIO.RISING, 
                          callback=mcp_handler)   # omitted bouncetime! 

    Initialisierung des MCP:
    bus.write_byte_data(expand_2, INTCONA_2, 0xFF) # all pins compared against defval
    '''
    # global counter

    # The INTF register reflects the interrupt condition on the
    # port pins of any pin that is enabled for interrupts via the
    # GPINTEN register. A set bit indicates that the
    # associated pin caused the interrupt.
    intfa = bus.read_byte_data(expand_2, INTFA_2)    # first read INTFA, then ...
    bus.write_byte_data(expand_2, GPINTENA_2, 0x00)  # ... disable MCP INTRs (clears INTFA!)

    time.sleep(0.1)

    # print("{} {} intfa={:x}".format(counter, presscount, intfa))

    # INTCAP captures the GPIO port value at the time the interrupt occured
    capa = bus.read_byte_data(expand_2, INTCAPA_2)  # clears intr flag
    # print("capa={:x}".format(capa))
    if capa == 0xfe: 
        bt = 0
        press_handler(intr_nr, bt)
    elif capa == 0xfd: 
        bt = 1
        press_handler(intr_nr, bt)
    elif capa == 0xfb: 
        bt = 2
        press_handler(intr_nr, bt)
    elif capa == 0xf7: 
        bt = 3
        press_handler(intr_nr, bt)
    elif capa == 0xef: 
        bt = 4
        press_handler(intr_nr, bt)
    elif capa == 0xdf: 
        bt = 5
        press_handler(intr_nr, bt)
    elif capa == 0xbf: 
        bt = 6
        press_handler(intr_nr, bt)
    elif capa == 0x7f: 
        bt = 7
        press_handler(intr_nr, bt)
    logger.info("mcp_handler: calling press_handler({}, {}, capa={})".format(intr_nr, bt, capa))

    n = 0
    while True:
        # wait for button release

        # Read the value on the port GPIOA
        gpa = bus.read_byte_data(expand_2, GPIOA_2)   # clears intr flag
        # print("gpa={:x}".format(gpa))
        if gpa == 0xff: 
            logger.info("mcp_handler: button released after {}*100ms".format(n))
            release_handler(intr_nr, bt)
            break
        time.sleep(0.1)
        n += 1

    # counter += 1
    bus.write_byte_data(expand_2, GPINTENA_2, 0xff)  # enable interrupts



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
    bus.write_byte_data(expand_1, IODIRA_1, 0x00)
    bus.write_byte_data(expand_1, IODIRB_1, 0x00)
     
    # GPA/OLATA und GPB/OLATB default Werte setzen
    bus.write_byte_data(expand_1, OLATA_1, 0x00)
    bus.write_byte_data(expand_1, OLATB_1, 0xFF)

    ##### Erweiterungsboard 2 -- Input-Platine
    expand_2 = 0x23 # i2c Adresse
    IODIRA_2 = 0x00 # Pin Register
    IODIRB_2 = 0x01 # Pin Register
    GPPUA_2 = 0x0C # Register für Pull-Up Widerstände
    GPIOA_2 = 0x12 # Register fuer GPIOA Eingabe
    OLATB_2 = 0x15 # Register fuer GPIOB Ausgabe
      
    # Definiere GPA und GPB als Input
    # Alle 8 GPA sind als Input und Interrupt eingestellt
    bus.write_byte_data(expand_2, IODIRA_2, 0xFF) 
    bus.write_byte_data(expand_2, IODIRB_2, 0x00)

    # GPB als Output deklariert für Status LED
    bus.write_byte_data(expand_2, OLATB_2, 0x00) 

    bus.write_byte_data(expand_2, GPPUA_2, 0xFF) 

    # Konfiguration für Interrupt Board2-GPB
    IOCONA_2 = 0x0A # Konfigurationsregister für INTPOL
    INTCONA_2 = 0x08 # Interrupt auf Abweichung vom Standartwert festlegen
    DEFVALA_2 = 0x06 # Standartwert des Pins
    GPINTENA_2 = 0x04 # Interrupt für welchen Pin festlegen
    INTCAPA_2 = 0x10 # Interrupt Captured Register
    INTFA_2 = 0x0E # Interrupt Flag register

    bus.write_byte_data(expand_2, GPINTENA_2, 0xFF) #pins on interrupt
    bus.write_byte_data(expand_2, DEFVALA_2, 0xFF) #standartwert 1
    bus.write_byte_data(expand_2, INTCONA_2, 0xFF) #1: Interrupt auf Abweichung von Defval
    # bus.write_byte_data(expand_2, INTCONA_2, 0x00) #1: Interrupt auf vorherigen Pinzustand

    iocon = bus.read_byte_data(expand_2, IOCONA_2) #IOCON Register bearbeiten
    iocon = iocon | 0b01111010
    # Die Steuerung am Tennisheim benoetigt unbedingt, dass beide Interrupts
    # INTA und INTB gespiegelt werden (iocon = 0x7a; mit iocon = 0x3a 
    # funktioniert es nicht!
    bus.write_byte_data(expand_2, IOCONA_2, iocon)

    # Starten des Interrupts entweder durch Auslesen GPIO oder durch Auslesen
    # INTCAP
    Gpio_wert = bus.read_byte_data(expand_2, GPIOA_2) 


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
    bus.write_byte_data(expand_2, OLATB_2, wert)




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
