# Multiprocessing IPC Client

import threading
from multiprocessing.managers import BaseManager
import queue


queue_c_to_s = None
queue_s_to_c = None


def connect():
    global queue_s_to_c, queue_c_to_s
    BaseManager.register('queue_StoC')
    BaseManager.register('queue_CtoS')
    m = BaseManager(address=('localhost', 50000), 
                    authkey=b'secret')
    m.connect()
    queue_s_to_c = m.queue_StoC()
    queue_c_to_s = m.queue_CtoS()
            

if __name__ == "__main__":
    connect()

    x = "Hallo"
    print("Schicke Nachricht von C to S: {}".format(x))
    queue_c_to_s.put(x)
    msg = queue_s_to_c.get()
    print("Erhalte Nachricht '{}' von S".format(msg))

    x = [1, 2, 3]
    print("Schicke Nachricht von C to S: {}".format(x))
    queue_c_to_s.put(x)
    msg = queue_s_to_c.get()
    print("Erhalte Nachricht '{}' von S".format(msg))

    x = {'a': 0}
    print("Schicke Nachricht von C to S: {}".format(x))
    queue_c_to_s.put(x)
    msg = queue_s_to_c.get()
    print("Erhalte Nachricht '{}' von S".format(msg))

    
