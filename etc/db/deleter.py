# tinydb.readthedocs.io/en/latest/getting-started.html

from tinydb import TinyDB, Query, where
from tinydb.operations import delete 

# delete?

db = TinyDB('dbtest.json')
ablaeufe = db.table('Ablaufliste', cache_size=0)

n = 0
while True:
    s = input("{}>".format(n))
    if s == "s":
        for a in ablaeufe:
            print(a.doc_id)
    if s[0] == 'r':
        a, n = s.split()
        print(a, n)
        n = int(n)
        ablaeufe.remove(doc_ids=[n])
    n += 1

'''
r = ablaeufe.remove(where('duration') == 35)  
print("(duration 35) ===>", r)

r = ablaeufe.contains(doc_id=12)
if r == True:
    ablaeufe.remove(doc_ids=[12])

for x in ablaeufe:
    print(x.doc_id, "-->", x)
'''

# print(ablaeufe.all())
