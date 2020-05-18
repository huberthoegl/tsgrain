# Multiprocessing IPC Server

import threading
from multiprocessing.managers import BaseManager
import queue


def worker():
    global website_pin

    queue_StoC = queue.Queue() 
    queue_CtoS = queue.Queue() 
    BaseManager.register('queue_StoC', callable=lambda: queue_StoC)
    BaseManager.register('queue_CtoS', callable=lambda: queue_CtoS)
    m = BaseManager(address=('', 50000), authkey=b'secret')
    m.start()

    queue_s_to_c = m.queue_StoC()
    queue_c_to_s = m.queue_CtoS()    
    
    while True: 
        msg = queue_c_to_s.get()
        queue_s_to_c.put("srv: got {}".format(msg))
            
            

if __name__ == "__main__":
    t = threading.Thread(target=worker)
    print(t.name)
    t.start()

