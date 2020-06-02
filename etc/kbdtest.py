
import RPi.GPIO as GPIO
import time
import smbus
import logging

logger = logging.getLogger("kbd-logger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("kbdtest.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

presscount = 0
counter = 0

PB1 = 'PB1'
PB2 = 'PB2'
PB3 = 'PB3'
PB4 = 'PB4'
PB5 = 'PB5'
PB6 = 'PB6'
PB7 = 'PB7'
PBAutoOff = 'PBAutoOff'


def press_handler(intnr, keynr):
    global presscount
    presscount += 1
    print("press_handler", keynr)


def release_handler(intnr, keynr):
    global presscount
    presscount -= 1
    print("release_handler", keynr)



def mcp_handler2(intr_nr):
    '''Interrupt Service Routine fuer I2C Expander 2, PORTA

    Diese Variante erzeugt nur einen Interrupt beim Druecken der Taste. Das Loslassen wird
    durch Polling festgestellt.

    GPIO.add_event_detect(17, 
                          GPIO.RISING, 
                          callback=mcp_handler2)   # omitted bouncetime! 

    Initialisierung des MCP:
    bus.write_byte_data(expand_2, INTCONA_2, 0xFF) # all pins compared against defval
    '''
    global counter
    intfa = bus.read_byte_data(expand_2, INTFA_2)    # first read INTFA, then ...
    bus.write_byte_data(expand_2, GPINTENA_2, 0x00)  # ... disable MCP INTRs (clears INTFA!)

    time.sleep(0.1)

    print("{} {} intfa={:x}".format(counter, presscount, intfa))

    capa = bus.read_byte_data(expand_2, INTCAPA_2)  # clears intr flag
    # print("capa={:x}".format(capa))
    if capa == 0xfe: 
        bt = PB1
        press_handler(intr_nr, bt)
    elif capa == 0xfd: 
        bt = PB2
        press_handler(intr_nr, bt)
    elif capa == 0xfb: 
        bt = PB3
        press_handler(intr_nr, bt)
    elif capa == 0xf7: 
        bt = PB4
        press_handler(intr_nr, bt)
    elif capa == 0xef: 
        bt = PB5
        press_handler(intr_nr, bt)
    elif capa == 0xdf: 
        bt = PB6
        press_handler(intr_nr, bt)
    elif capa == 0xbf: 
        bt = PB7
        press_handler(intr_nr, bt)
    elif capa == 0x7f: 
        bt = PBAutoOff
        press_handler(intr_nr, bt)

    while True:
        # wait for button release
        gpa = bus.read_byte_data(expand_2, GPIOA_2)   # clears intr flag
        # print("gpa={:x}".format(gpa))
        if gpa == 0xff: 
            release_handler(intr_nr, bt)
            break
        time.sleep(0.1)

    counter += 1
    bus.write_byte_data(expand_2, GPINTENA_2, 0xff)  # enable interrupts



def mcp_handler(intr_nr):
    '''Interrupt Service Routine fuer I2C Expander 2, PORTA

    Haengt gelegentlich nach der folgenden Logzeile:
    2020-06-02 15:48:27,934 - kbd-logger - INFO - mcp_handler: read_interrupt NONE KEY
    Danach erzeugt der MCP keinen Interrupt mehr.

    Initialisierung des MCP:
    bus.write_byte_data(expand_2, INTCONA_2, 0x00) #1: Compared agains previous pin value

    Initialisierung des RPi Interrupt-Eingang:
    GPIO.add_event_detect(17, 
                          GPIO.RISING, 
                          callback=mcp_handler, bouncetime=100)  

    '''
    key_nr = read_interrupt()  
    if key_nr == None:
        logger.info("mcp_handler: read_interrupt NONE KEY")
        gpa = read_tasten()  # dummy read to clear interrupt condition (1.6.20)
        return  # key could not be identified
    time.sleep(0.1)
    capa = read_intcapa()
    if capa == 255:
        logger.info("mcp_handler: calling release_handler({}, {}, capa={})".format(intr_nr, key_nr, capa))
        release_handler(intr_nr, key_nr)
        gpa = read_tasten()  # dummy read to clear interrupt condition (1.6.20)
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
        gpa = read_tasten()  # dummy read to clear interrupt condition (1.6.20)



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
    bus.write_byte_data(expand_2, INTCONA_2, 0xFF) #1: Compared against defval
    # bus.write_byte_data(expand_2, INTCONA_2, 0x00) #1: Compared agains previous pin value

    iocon = bus.read_byte_data(expand_2, IOCONA_2) #IOCON Register bearbeiten
    iocon = iocon | 0b01111010
    # Die Steuerung am Tennisheim benoetigt unbedingt, dass beide Interrupts
    # INTA und INTB gespiegelt werden (iocon = 0x7a; mit iocon = 0x3a 
    # funktioniert es nicht!
    bus.write_byte_data(expand_2, IOCONA_2, iocon)

    # Starten des Interrupts entweder durch Auslesen GPIO oder durch Auslesen
    # INTCAP
    Gpio_wert = bus.read_byte_data(expand_2, GPIOA_2) 



def read_interrupt():
    '''Gibt zurueck, welche Taste gedrueckt wurde (0...7). 
    '''
    # The INTF register reflects the interrupt condition on the
    # port pins of any pin that is enabled for interrupts via the
    # GPINTEN register. A set bit indicates that the
    # associated pin caused the interrupt.
    irwert = bus.read_byte_data(expand_2, INTFA_2)
    mask = 0x01
    i = 0
    while i < 8:
        if mask & irwert:
            break
        else:
            mask <<= 1
            i += 1
    if 0 <= i <= 7:
        return i
    else:
        logger.info("read_interrupt: ungueltige Taste, irwert=0x{:x}".format(irwert))
        return None


def read_tasten():
    '''Read the value on the port GPIOA.
    
    Manual: "The interrupt condition is cleared after the LSB of the data 
    is clocked out during a read command of GPIO or INTCAP."
    '''
    return bus.read_byte_data(expand_2, GPIOA_2) 



def read_intcapa():
    '''INTCAP captures the GPIO port value at the time the interrupt
    occured.

    Manual: "The interrupt condition is cleared after the LSB of the 
    data is clocked out during a read command of GPIO or INTCAP."
    '''
    return bus.read_byte_data(expand_2, INTCAPA_2) 


if __name__ == "__main__":
    bus = smbus.SMBus(1)
    init()

    # GPIO17 to interrupt output of MCP23017
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.add_event_detect(17, 
                          GPIO.RISING, 
                          callback=mcp_handler2) 
    
    while True:
        time.sleep(1)
