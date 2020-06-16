''' A 1 second ticker which can be subsribed. It is timed by the low-level
clock1s module.
'''

import clock1s


class Tick:

    def __init__(self):
        self.ticks = 0
        self.cblist = []
        self.timer = clock1s.PeriodicTimer(1, self._sec1)

    def _sec1(self):   
        # called by threading.Timer
        self.ticks += 1
        if self.cblist:
            for f in self.cblist:
                f()
        return True

    def start(self):
        self.timer.start()

    def subscribe(self, cb):
        self.cblist.append(cb)

    def unsubscribe(self, cb):
        self.cblist.remove(cb)

    

