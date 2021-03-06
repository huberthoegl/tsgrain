# Multiprocessing IPC Server

import time
import threading
import logging
import queue
from multiprocessing.managers import BaseManager
import conf
import manctrl
import json
import db
import led3c

if conf.PLATFORM == 'pc':
   import pbutton_pc as pbutton
else:
   import pbutton_rpi as pbutton
   import rtc


PORT = 50000

logger = None
thr = None
bmg = None
running = True
logger = logging.getLogger(conf.TSGRAIN_LOGGER)
rdb = db.RainDB() # singleton
manual_control = None


def worker():
    global bmg
    import sys
    queue_StoC = queue.Queue() 
    queue_CtoS = queue.Queue() 
    BaseManager.register('queue_StoC', callable=lambda: queue_StoC)
    BaseManager.register('queue_CtoS', callable=lambda: queue_CtoS)
    bmg = BaseManager(address=('', PORT), authkey=b'secret')
    bmg.start()

    queue_s_to_c = bmg.queue_StoC()
    queue_c_to_s = bmg.queue_CtoS()    
    
    while running: 
        try:
            msg = queue_c_to_s.get()
            # message types (json)
            # '{ "cmd": "press-button", "n": <int>}'
            # '{ "cmd": "get-outputs"}'
            # '{ "cmd": "date-exists", "date": "2020-05-17T22:10:00" }'
            # '{ "cmd": "store-job", "job": { ...job...} }'
            # '{ "cmd": "get-jobs" }'
            # '{ "cmd": "delete-job-by-date", "date": "2020-05-17T22:10:00" }'
            # '{ "cmd": "toggle-status-by-date", "date": "2020-05-17T22:10:00" }'
            # '{ "cmd": "get-settings" }'
            # '{ "cmd": "set-settings", <settings> }'
            # '{ "cmd": "set-datetime", "date": ..., "time": ... }'

            D = json.loads(msg)
            logger.info("received ipc msg: {}".format(D))

            if D['cmd'] == 'press-button':
               n = D['n']
               key = pbutton.MAN_KEYS[n]
               manual_control.pb_pressed(key) 
               reply = 'ok'
               logger.info("ipc reply: {}".format(reply))
               queue_s_to_c.put(reply)
               time.sleep(0.1)

            if D['cmd'] == 'get-outputs':
               outputs = manual_control.out.get()
               logger.info("ipc reply: {}".format(outputs))
               queue_s_to_c.put(outputs)

            if D['cmd'] == 'date-exists':
               date = D['date']
               r = rdb.date_exists(date)
               logger.info("ipc reply: {}".format(r))
               queue_s_to_c.put(r)  # send True or False

            if D['cmd'] == 'store-job':
               job = D['job']
               rdb.store_job(job)
               reply = 'ok'
               logger.info("ipc reply: {}".format(reply))
               queue_s_to_c.put(reply)

            if D['cmd'] == 'get-jobs':
               jobs = rdb.get_jobs()
               # jobs is a LoD
               logger.info("ipc reply: {}".format("jobs as LoD..."))
               queue_s_to_c.put(jobs)

            if D['cmd'] == 'delete-job-by-date':
               date = D['date']
               r = rdb.delete_job_by_date(date)
               logger.info("ipc reply: {}".format(r))
               queue_s_to_c.put(r)  # return list of deleted doc_ids
               manual_control.enable() 
               led3c.set_led(led3c.GREEN)

            if D['cmd'] == 'toggle-status-by-date':
               date = D['date']
               r, s = rdb.toggle_status(date)
               logger.info("ipc reply: r={} s={}".format(r, s))
               if s == 'inactive':
                   # if job is running, immediately stop it. 
                   manual_control.enable() 
                   led3c.set_led(led3c.GREEN)
               queue_s_to_c.put(r)  # return list of toggled doc_ids

            if D['cmd'] == 'get-settings':
               r = rdb.get_settings()
               logger.info("ipc reply: {}".format(r))
               queue_s_to_c.put(r)  

            if D['cmd'] == 'set-settings':
               n = D['manual_delay']['val']
               rdb.set_manual_delay(n)
               queue_s_to_c.put("ok")  

            if D['cmd'] == 'set-datetime':
               if conf.PLATFORM == 'rpi':
                   # XXX to do: must be rewritten
                   # rtc.RTCChangeDate(D['date'])
                   # rtc.RTCChangeTime(D['time'])
                   pass
               queue_s_to_c.put("ok")  

        except:
            # XXX to do: don't catch all exceptions here, only Ctrl-C!
            e = sys.exc_info()[0]
            break
            
            
def start_ipc_server():
    global manual_control, thr
    thr = threading.Thread(target=worker)
    thr.start()
    logger.info("starting multiprocessing ipc server thread {}".format(thr.name))
    manual_control = manctrl.ManCtrl()  # singleton


if __name__ == "__main__":
    # start_ipc_server()
    msg = '{ "cmd": "presskey", "n": 3}'
    D = json.loads(msg)
    print(D)
    print(D['cmd'])
    print(D['n'])

