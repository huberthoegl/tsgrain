import subprocess
print("Website am starten")
myprocess = subprocess.Popen(["cd /home/pi/tsgrain/website && /home/pi/venv/bin/python3 -m flask run --host=0.0.0.0"], shell=True)
output, error = myprocess.communicate()
status = myprocess.wait()
