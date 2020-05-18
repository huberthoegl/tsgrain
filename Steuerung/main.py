

import config
import atexit
import controller
import time
import logging
import mpipc_srv

# https://docs.python.org/3/howto/logging-cookbook.html
# levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
logger = logging.getLogger(config.TSGRAIN_LOGGER)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(config.LOGFILE)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)



def quit():
    pass 


def main():
    import sys
    logger.info("starting main")
    atexit.register(quit)
    mpipc_srv.start_ipc_server()
    co = controller.Controller()
    co.run()


if __name__ == "__main__":
    main()

