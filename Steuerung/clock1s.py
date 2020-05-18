
# A 1 second timebase

# https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python
# https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679

import logging, threading, functools
import time
import config


class PeriodicTimer(object):
    def __init__(self, interval, callback):
        self.logger = logging.getLogger(config.TSGRAIN_LOGGER)
        self.interval = interval

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            if result:
                # every second a new thread is started
                self.thread = threading.Timer(self.interval,
                                              self.callback)
                self.thread.start()

        self.callback = wrapper

    def start(self):
        self.thread = threading.Timer(self.interval, self.callback)
        self.logger.info("starting 1 sec periodic timer thread {}".format(self.thread.name))
        self.thread.start()

    def cancel(self):
        self.logger.info("cancelling 1 sec periodic timer")
        self.thread.cancel()


if __name__ == "__main__":

    def foo():
        logging.info('foo: Doing some work...')
        return True

    timer = PeriodicTimer(1, foo)
    timer.start()

    for i in range(5):
        time.sleep(2)
        logging.info('Doing some other work...')

    timer.cancel()


