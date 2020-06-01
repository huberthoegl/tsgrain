# Read temperature from DS3231 RTC
# https://www.raspberrypi.org/forums/viewtopic.php?t=59808
# evtl. vorher "sudo rmmod rtc_ds1307"

import smbus

bus = smbus.SMBus(1)
address = 0x68

def getTemp(address):
    byte_tmsb = bus.read_byte_data(address, 0x11)
    byte_tlsb = bin(bus.read_byte_data(address, 0x12))[2:].zfill(8)
    return byte_tmsb+int(byte_tlsb[0])*2**(-1)+int(byte_tlsb[1])*2**(-2)

print(getTemp(address))
