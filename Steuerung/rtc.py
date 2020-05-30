#DS 3231 RTC Real Time Clock, Registerbelegung auf Datenblatt S.15

import smbus
import time
from datetime import datetime, time, date

#I2C-Adresse 
address = 0x68
#Register für Aktuelle Zeit
register = 0x00 #Hierbei wird diesmal nicht write_byte_data verwendet um 7 Byte sofort am Stück in das Register zu schreiben, deshalb ist nur das erste byte zu adressieren
seconds = 0x00
minutes = 0x01
hours = 0x02
date = 0x04
month = 0x05
year = 0x06
#Register für Alarm 1
alarm1_seconds = 0x07
alarm1_minutes = 0x08
alarm1_hours = 0x09
alarm1_date = 0x0A
#Register für Alarm 2
alarm2_minutes = 0x0B
alarm2_hours = 0x0C
alarm2_date = 0x0D
#Alarm Control Register
alarm_control = 0x0E
alarm_status = 0x0F

#Struktur: sec min hour week day month year
default_time = [0x00,0x42,0x16,0x01,0x03,0x02,0x20] #RTCSetTime(default_time)
wochentag  = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]; #Wochentag Funktion -- Nicht benützt

#Funktionen zum auslesen/schreiben
######################################################
bus = smbus.SMBus(1)
def RTCSetTime(neue_zeit):
    bus.write_i2c_block_data(address,register,neue_zeit)
  
def RTCGetTime():
    return bus.read_i2c_block_data(address,register,7);

#Funktionen für Formatieren der Ausgabe
#######################################################
#Auslesen und Zuückgeben der aktuellen zeit auf dem RTC
def RTCReturnTime():
    time = RTCGetTime()
    #time[0] = time[0]&0x7F  #sec        
    time[1] = time[1]&0x7F  #min
    time[2] = time[2]&0x3F  #hour
    return("%s:%s" %(zweistelligeZahl(time[2]), zweistelligeZahl(time[1])))
    #return("%s:%s:%s" %(zweistelligeZahl(time[2]), zweistelligeZahl(time[1]), zweistelligeZahl(time[0])))

#zwingt Input auf 2 Zeichen um es auf Website ausgeben zu können
def zweistelligeZahl(value):
    x1 = (int(value/16))
    x0 = int(value % 16)
    return str(x1) + str(x0)

#Auslesen und zuückgeben der aktuellen Datums auf dem RTC
def RTCReturnDate():
    time = RTCGetTime()
    time[4] = time[4]&0x3F  #day
    time[5] = time[5]&0x1F  #month
    return datetime.strptime(("%x.%x.20%x" %(time[4], time[5], time[6])), "%d.%m.%Y")

def RTC_aktuelle_Zeit():
    time = RTCGetTime()
    time[1] = time[1]&0x7F  #min
    time[2] = time[2]&0x3F  #hour
    time[4] = time[4]&0x3F  #day
    time[5] = time[5]&0x1F  #month
    return("20%s-%s-%s %s:%s" %(zweistelligeZahl(time[6]), zweistelligeZahl(time[5]), zweistelligeZahl(time[4]),  zweistelligeZahl(time[2]), zweistelligeZahl(time[1])))


#Funktionen zum Formatieren der Eingabe
#############################################################
#website: Uhrzeit ändern
def RTCChangeTime(uhrzeit):
    #uhrzeit kommt als string_time variable formatiert, muss also umgewandelt werden
    var_x = uhrzeit.split(":")
    stunden = (int(int(var_x[0])/10)*16)+(int(var_x[0]) % 10) #siehe Registerstruktur des DS3231
    minuten = (int(int(var_x[1])/10)*16)+(int(var_x[1]) % 10)
    #sekunden = (int(int(var_x[2])/10)*16)+(int(var_x[2]) % 10)
    bus.write_byte_data(address, hours, stunden)
    bus.write_byte_data(address, minutes, minuten)
    #bus.write_byte_data(address, seconds, sekunden)

#website: Datum ändern    
def RTCChangeDate(datum):
    var_x = datum.split("-")
    Tag = (int(int(var_x[2])/10)*16)+(int(var_x[2]) % 10)
    Monat = (int(int(var_x[1])/10)*16)+(int(var_x[1]) % 10)
    Jahr = (int((int(var_x[0])-2000)/10)*16)+((int(var_x[0])-2000) % 10)
    bus.write_byte_data(address, date, Tag)
    bus.write_byte_data(address, month, Monat)
    bus.write_byte_data(address, year, Jahr)
    print("var_x: ", var_x, "TMJ:", Tag, Monat, Jahr)



#Alarm
##################################################################
#Alarm auslesen, sowohl alarm 1 als auch alarm 2 werden ausgelesen und zurückgesetzt
def getAlarm():
    status = bus.read_byte_data(address, alarm_status)
    status_ausgabe = status&0b00000011
    status_write = status&0b11111100
    bus.write_byte_data(address, alarm_status, status_write)
    return status_ausgabe

#Alarm1 aktivieren    
def enableAlarm1(minuten):

    time = RTCGetTime()
    #sec #wird ignoriert da nur auf ganze Minuten ausgelöst werden soll     
    time[1] = time[1]&0x7F  #min
    time[2] = time[2]&0x3F  #hour

    #a1m1 = bus.read_byte_data(address, alarm1_seconds)
    a1m1 = 0b00000000
    bus.write_byte_data(address, alarm1_minutes, a1m1)

    #Alarm1 Minuten
    minuten_e = ((int(time[1])%16)+(minuten%10))
    if minuten_e >= 10:
        zm = 1
        minuten_e = minuten_e%10
    else:
        zm = 0
    minuten_z = int((time[1]/16)+(minuten/10)+zm)
    if minuten_z >= 6:
        h = 1
        minuten_z = minuten_z%6
    else:
        h = 0
    a1m2 = (minuten_z*16)+minuten_e    
    bus.write_byte_data(address, alarm1_minutes, a1m2)

    #Alarm1 Stunden
    stunden = int(minuten/60)
    stunden_e = ((int(time[2])%16)+(stunden%10)+h)
    if stunden_e >= 10:
        zs = 1
        stunden_e = stunden_e%10
    else:
        zs = 0
    stunden_z = int((time[2]/16)+(stunden/10)+zs)
    if stunden_z >= 3:
        stunden_z = stunden_z%3
    if stunden_z >= 2 and stunden_e >= 4: #24h Ausnahme
        stunden_e = 0
        stunden_z = 0
    a1m3 = (stunden_z*16)+stunden_e  
    bus.write_byte_data(address, alarm1_hours, a1m3)

    a1m4 = bus.read_byte_data(address, alarm1_date)
    a1m4 = a1m4|0b10000000
    a1m4 = a1m4&0b10111111
    bus.write_byte_data(address, alarm1_date, a1m4)
    print("Alarm1: neue Zeit: %s%s:%s%s   alte Zeit: %s" %(stunden_z, stunden_e,minuten_z, minuten_e, RTCReturnTime()))
    #print("neue_zeit: ", a1m2, "  , ", a1m3, " ||| ", RTCReturnTime())
    #print("alte_zeit: ", time[1], "  , ", time[2], " ||| ", RTCReturnTime())

    #Alarm Config
    control = bus.read_byte_data(address, alarm_control)
    control = control|0b00000101 
    bus.write_byte_data(address, alarm_control, control)

    status = bus.read_byte_data(address, alarm_status)
    status = status&0b01111110
    bus.write_byte_data(address, alarm_status, status)


#Alarm2 aktivieren    
def enableAlarm2(minuten):

    time = RTCGetTime()
    #sec #wird ignoriert da nur auf ganze Minuten ausgelöst werden soll     
    time[1] = time[1]&0x7F  #min
    time[2] = time[2]&0x3F  #hour

    #Alarm1 Minuten
    minuten_e = ((int(time[1])%16)+(minuten%10))
    if minuten_e >= 10:
        zm = 1
        minuten_e = minuten_e%10
    else:
        zm = 0
    minuten_z = (int(time[1]/16))+(int(minuten/10))+zm
    if minuten_z >= 6:
        h = 1
        minuten_z = minuten_z%6
    else:
        h = 0
    a2m2 = (minuten_z*16)+minuten_e    
    bus.write_byte_data(address, alarm2_minutes, a2m2)

    #Alarm1 Stunden
    stunden = int(minuten/60)
    stunden_e = ((int(time[2])%16)+(stunden%10)+h)
    if stunden_e >= 10:
        zs = 1
        stunden_e = stunden_e%10
    else:
        zs = 0
    stunden_z = (int(time[2]/16))+(int(stunden/10))+zs
    if stunden_z >= 3:
        stunden_z = stunden_z%3
    if stunden_z >= 2 and stunden_e >= 4: #24h Ausnahme
        stunden_e = 0
        stunden_z = 0
    a2m3 = (stunden_z*16)+stunden_e  
    bus.write_byte_data(address, alarm2_hours, a2m3)

    a2m4 = bus.read_byte_data(address, alarm2_date)
    a2m4 = a2m4|0b10000000
    a2m4 = a2m4&0b10111111
    bus.write_byte_data(address, alarm2_date, a2m4)
    
    print("Alarm2: neue Zeit: %s%s:%s%s   alte Zeit: %s" %(stunden_z, stunden_e,minuten_z, minuten_e, RTCReturnTime()))
    #print("neue_zeit: ", a2m2, "  , ", a2m3, " ||| ", RTCReturnTime())
    #print("alte_zeit: ", time[1], "  , ", time[2], " ||| ", RTCReturnTime())

    #AlarmConfig
    control = bus.read_byte_data(address, alarm_control)
    control = control|0b00000110 
    bus.write_byte_data(address, alarm_control, control)

    status = bus.read_byte_data(address, alarm_status)
    status = status&0b01111101
    bus.write_byte_data(address, alarm_status, status)


#Alarm Ausschalten durch Deaktivieren von A1IE bzw A2IE
def disableAlarm1():
    control = bus.read_byte_data(address, alarm_control)
    control = control&0b11111110 #A1IE deaktivieren
    bus.write_byte_data(address, alarm_control, control)

def disableAlarm2():
    control = bus.read_byte_data(address, alarm_control)
    control = control&0b11111101 #A2IE deaktivieren
    bus.write_byte_data(address, alarm_control, control)


