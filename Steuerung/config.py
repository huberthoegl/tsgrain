
PLATFORM = 'pc'  # 'pc', 'rpi'
# PLATFORM = 'rpi'

NCOURTS = 7

# is now red from database
# MAN_DURATION_SEC = 10  # manual rain duration

TSGRAIN_LOGGER = "TSGRain-Logger"


if PLATFORM == 'rpi':
    DBPATH = '/home/pi/tsgrain/Datenbank/db.json'
    LOGFILE = '/home/pi/tsgrain/Steuerung/tsgrain.log'
else:
    DBPATH = '/home/hhoegl/tsgrain/Datenbank/db.json'
    LOGFILE = '/home/hhoegl/tsgrain/Steuerung/tsgrain.log'

