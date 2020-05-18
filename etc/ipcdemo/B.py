import time
import ipc

ipc.open()
ab = ipc.AtoB()
ba = ipc.BtoA()

n = 0
while True:
    msg = ab.getb()  # blocking get
    ba.put("bla")
    time.sleep(1)
    n = n + 1
    if n % 50 == 0:
        print(n)

