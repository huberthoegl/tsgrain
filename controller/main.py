

import conf
import atexit
import controller
import time
import logging
import mpipc_srv
import led3c
import db
import signal
import output


# https://docs.python.org/3/howto/logging-cookbook.html
# levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
logger = logging.getLogger(conf.TSGRAIN_LOGGER)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(conf.LOGFILE)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


def quit():
    '''called on Ctrl-C'''
    logger.info("quit handler")
    led3c.set_led(led3c.OFF)
    o = output.Output()
    o.all_off()


def sigterm_handler(signum, frame):
    '''called when program is terminated with systemctl stop ...
    or with "shutdown -r now". See shdn.py for the shutdown/reboot button which 
    runs either "shutdown -r now" or "shutdown -h now" and sets a nice color
    for the status led.
    '''
    logger.info("program received SIGTERM (signum={})".format(signum))
    # do not switch off status led, it is set in shdn.py
    # led3c.set_led(led3c.OFF)  
    o = output.Output()
    o.all_off()
    import os
    os._exit(0)


def main():
    import sys
    logger.info("starting main")
    atexit.register(quit)
    signal.signal(signal.SIGTERM, sigterm_handler)
    mpipc_srv.start_ipc_server()
    rdb = db.RainDB()
    rdb.inc_startcount()
    co = controller.Controller()
    co.run()


if __name__ == "__main__":
    main()
