# load a tinydb with json module

import json

fo = open("dbtest.json", "r")
db = json.load(fo)
print(type(db))

print(db['_default']['1']['val'])

print("---")

Ablaufliste = db['Ablaufliste'].items()
for k, db in Ablaufliste:
       print(k, db)

