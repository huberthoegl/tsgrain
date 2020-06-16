

class Monodelay:

    def __init__(self, ticks):
        self.n = 0
        self.secs = 0
        self.callback = None
        self.start = None
        ticks.subscribe(self.tick)
        
    def set_delay(self, n):
        self.secs = n

    def set_cb(self, f):
        self.callback = f

    def run(self):
        self.start = True

    def finish(self):
        # force delay timer to finish
        self.callback()
        self.n = 0
        self.start = False

    def tick(self):
        if self.start:
            self.n += 1
            if self.n == self.secs:
                self.callback()
                self.n = 0
                self.start = False

