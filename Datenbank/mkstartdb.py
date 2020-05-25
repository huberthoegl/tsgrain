# tinydb.readthedocs.io/en/latest/getting-started.html

import os, time
from tinydb import TinyDB

if os.path.exists('start_db.json'):
    os.unlink('start_db.json')

db = TinyDB('start_db.json')

settings = db.table('settings', cache_size=0)  # disable cache
settings.insert({'type': 'startcnt', 'val': 0}) # count restarts 
settings.insert({'type': 'manual_delay', 'val': 5})  # minutes

jobs = db.table('jobs', cache_size=0)  # disable cache

jobs.insert({'status': 'act',
             'start': '2020-05-18T18:00:00', 
             'duration': '30', 
             'courts': '*******', 
             'cycle': '0'})

jobs.insert({'status': 'act',
             'start': '2020-05-18T22:00:00', 
             'duration': '5', 
             'courts': '*******', 
             'cycle': '0'})

