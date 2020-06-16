
# https://schedule.readthedocs.io by Dan Bader
import schedule  
import threading
import time


handler_list = []


def add_handler(f):
    global handler_list
    handler_list.append(f)


def _call_handler():
    for f in handler_list:
        f()


def start():
    schedule.every().minute.at(":00").do(_call_handler)
    e = run_continuously()  # e is a threading Event object
    # terminate call to run_pending with e.set() 
    return e


# taken from github.com/mrhwick/schedule 
def run_continuously(interval=1):
        """Continuously run, while executing pending jobs at each elapsed
        time interval.
        @return cease_continuous_run: threading.Event which can be set to
        cease continuous run.
        Please note that it is *intended behavior that run_continuously()
        does not run missed jobs*. For example, if you've registered a job
        that should run every minute and you set a continuous run interval
        of one hour then your job won't be run 60 times at each interval but
        only once.
        """
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run


def my_test_action():
    print("Action")


if __name__ == "__main__":
    add_handler(my_test_action)
    init()
    n = 0
    while True:
        time.sleep(1)
        print(n)
        if n == 160:
            e.set()
        n += 1


