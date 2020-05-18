from tinydb import TinyDB, Query

db = TinyDB('dbtest.json')

q = Query()


r = db.update({'val': 42}, q.type == 'startcnt')
print("1>", r)

r = db.search(q.type == 'startcnt')
print("2>", r)
n = r[0]['val']
print("2>", n)

# db.remove(Fruit.count < 5)
