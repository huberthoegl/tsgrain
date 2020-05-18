import i2cRtc as RTC

default_time = [0x00,0x42,0x16,0x01,0x03,0x02,0x20] #RTCSetTime(default_time)

RTC.RTCSetTime(default_time)
print("Uhrzeit zurückgesetzt")
