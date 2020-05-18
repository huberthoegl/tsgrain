import os

ipc_flag = True

PLATFORM = 'pc'  
# PLATFORM = 'rpi'

if PLATFORM == 'pc':
    DBPATH = '/home/hhoegl/tsgrain/Datenbank/db.json'
    TSGRAIN_FLASK_LOGFILE = '/home/hhoegl/tsgrain/Website/flask.log'
else:
    DBPATH = '/home/pi/tsgrain/Datenbank/db.json'
    TSGRAIN_FLASK_LOGFILE = '/home/pi/tsgrain/Website/flask.log'


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Sicherheitschlüssel'
    DEBUG = True
