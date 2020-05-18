import time
import ipc

# starte gleichzeitig:
# python A.py
# python B.py

# Laeuft nach einer Weile auf eine Exception
# json.decoder.JSONDecodeError: Extra data: line 1 column 104 (char 103)
# 
# => Bidirektionaler Datentransfer mit tinydb funktioniert 
# nicht ueber laengere Zeit.

ipc.create()
ab = ipc.AtoB()
ba = ipc.BtoA()

time.sleep(5)
print("start")
n = 0
while n < 1000:
    ab.put("hi")
    msg = ba.getb()
    print(n, msg)
    n = n + 1
    if n % 50 == 0:
        print(n)

time.sleep(5)

#ba = ipc.BtoA()
#msg = ba.getb()
#print(msg)
