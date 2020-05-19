
autostart_steuerung.service
autostart_website.service
     Diese beiden Dateien in /etc/systemd/system/ kopieren und
     "systemctl daemon-reload" eingeben.

db/
     Ein paar Demos zur TinyDB

ipcdemo
     Ein (fehlgeschlagener) Versuch, mit TinyDB eine Interprozesskommunikation
     aufzubauen.

mpipc_client.py
mpipc_srv.py
     IPC mit dem multiprocessing Modul.

reset_datetime.py
     Low-level Zugriff auf den RTC DS3231.

schedule-master.zip
     Das "schedule" Modul fuer von Dan Bader https://pypi.org/project/schedule/
     Wird in der Steuerungssoftware verwendet (Version 0.6.0 vom 21. Januar
     2019)

shdn_program.py
     Demo fuer boot/shutdown.     

tinydb-4.1.1.zip
     Die TinyDB https://pypi.org/project/tinydb/


