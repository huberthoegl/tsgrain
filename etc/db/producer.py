# tinydb.readthedocs.io/en/latest/getting-started.html


'''
cat db.json | jq

or

cat db.json | python -m json.tool

Pretty to compact convertion:

  cat db.json.pretty | jq -c

'''

import os, time
from tinydb import TinyDB, Query

if os.path.exists('dbtest.json'):
    os.unlink('dbtest.json')

db = TinyDB('dbtest.json')
docid = db.insert({'type': 'startcnt', 'val': 0})  # insert document
docid = db.insert({'type': 'mandelay', 'val': 5})

for item in db:
    print("0>", item)

ablaeufe = db.table('Ablaufliste', cache_size=0)  # disable cache

n = 0
duration = 20
# while n < 20:
while True:
    s = input("{}> ".format(n))
    doc_id = ablaeufe.insert({'start': '20-05-11T22:00', 
                              'duration': duration, 
                              'courts': '*******', 
                              'days': '1'})
                              # cycle: no, 12h, d, ...
    duration += 5
    n += 1


'''
r = db.all()
print("all>", r)


for i, item in enumerate(db):
    print(i, "->", item)

print("%%>", ablaeufe.all())

for item in ablaeufe:
    print("=>", item)
'''

# db.truncate() # alles loeschen
# print(db.all())

