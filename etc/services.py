#! /usr/bin/python3

import os, sys

SERVICES = ("autostart_steuerung.service", "autostart_website.service")

def usage():
    print('''usage: services.py status|stop|start
''')
    os._exit(0)


def main():
    if len(sys.argv) != 2:
        usage()
    else:
        op = sys.argv[1]

    for svc in SERVICES:  
        cmd = "sudo systemctl {} {}".format(op, svc)
        os.system(cmd)
    

if __name__ == "__main__":
    main()

