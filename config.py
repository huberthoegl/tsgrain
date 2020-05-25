
# USER = '~pi'
USER = '~hhoegl'

# PLATFORM = 'rpi'
PLATFORM = 'pc'  # 'pc', 'rpi'

import os
homedir = os.path.expanduser(USER)

IPC_FLAG = True

NCOURTS = 7

# is now red from database
# MAN_DURATION_SEC = 10  # manual rain duration

TSGRAIN_LOGGER = "TSGRain-Logger"

# manual rain duration
if PLATFORM == 'pc':
    SEC_PER_MIN = 1   # for testing on pc
else:
#   SEC_PER_MIN = 60  # correct value for real world
    SEC_PER_MIN = 1   # correct value for real world

DBPATH = os.path.join(homedir, 'tsgrain/Datenbank/db.json')
LOGFILE = os.path.join(homedir, 'tsgrain/Steuerung/tsgrain.log')
TSGRAIN_FLASK_LOGFILE = os.path.join(homedir, 'tsgrain/Website/flask.log')

# for Flask
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Sicherheitschlüssel'
    DEBUG = True

