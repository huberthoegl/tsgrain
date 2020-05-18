# tinydb.readthedocs.io/en/latest/getting-started.html

from tinydb import TinyDB, Query, where

from tinydb.operations import delete 
# delete example:
# db.update(delete('key1'), User.name == 'John')
# delete(key), increment(key), decrement(key), add(key, value), subtract(key,
# value), set(key, value)

db = TinyDB('dbtest.json')
ablaeufe = db.table('Ablaufliste', cache_size=0)

for a in ablaeufe:
    print(a.doc_id, "-->", a)

r = ablaeufe.remove(where('duration') == 35)  
print("(duration 35) ===>", r)

r = ablaeufe.contains(doc_id=12)
if r == True:
    ablaeufe.remove(doc_ids=[12])

for x in ablaeufe:
    print(x.doc_id, "-->", x)

# print(ablaeufe.all())
