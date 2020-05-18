import time, os
from tinydb import TinyDB, Query
# TinyDB.DEFAULT_TABLE_KWARGS = {'cache_size': 0}

DB = 'ipc.json'

db = None
pipes = None
q = Query()


def create():
    global db, pipes

    if os.path.exists(DB):
        os.unlink(DB)

    db = TinyDB(DB)
    pipes = db.table('pipes', cache_size=0)
    docid = pipes.insert({'type': 'chab', 'active': 0, 'val': 0})  
    docid = pipes.insert({'type': 'chba', 'active': 0, 'val': 5})


def open():
    global db, pipes
    db = TinyDB(DB)
    pipes = db.table('pipes', cache_size=0)


class AtoB:
    def __init__(self):
        pass

    def put(self, msg):
        r = pipes.update({'active': 1, 'val': msg}, q.type == 'chab')

    def getb(self):
        '''getb - blocking get 
        TODO: add timeout 
        '''
        while True:
            # must do the search in every loop iteration
            self.ch = pipes.search(q.type == 'chab')[0]
            if self.ch['active'] == 1:
                msg = self.ch['val']
                pipes.update({'active': 0, 'val': 0}, q.type == 'chab')
                return msg
            time.sleep(0.5)


class BtoA:
    def __init__(self):
        pass

    def put(self, msg):
        r = pipes.update({'active': 1, 'val': msg}, q.type == 'chba')

    def getb(self):
        while True:
            # must do the search in every loop iteration
            self.ch = pipes.search(q.type == 'chba')[0]
            if self.ch['active'] == 1:
                msg = self.ch['val']
                pipes.update({'active': 0, 'val': 0}, q.type == 'chba')
                return msg
            time.sleep(0.5)


if __name__ == "__main__":
    create()
    ab = AtoB()
    ab.put("Hi")
    while True:
        time.sleep(1)
