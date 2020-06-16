from app import app
from flask import render_template, flash, redirect, url_for, request
from app.forms import InputForm, SettingsForm, SetDateTimeForm, StatusForm

import queue
import sys
import logging
from multiprocessing.managers import BaseManager
from datetime import datetime, date, time, timedelta
import json
import conf
import termin

logger = logging.getLogger("TSGRain-Flask-Logger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(conf.TSGRAIN_FLASK_LOGFILE)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

if conf.IPC_FLAG:
    BaseManager.register('queue_StoC')
    BaseManager.register('queue_CtoS')
    m = BaseManager(address=('localhost', 50000), authkey=b'secret')
    try:
        m.connect()
    except:
        logger.error("BaseManager connect(): error")

    queue_s_to_c = m.queue_StoC()
    queue_c_to_s = m.queue_CtoS()


@app.route('/')
@app.route('/index')
def index():
    logger.info('routes.py: /index')
    return redirect(url_for('manuell'))


@app.route('/manuell', methods=['GET', 'POST'])
def manuell():
    
    status_form = StatusForm()
    
    n = None
    if request.method == 'POST':
        if request.form.get('platz_1') == 'Platz 1':
            n = 0
        elif request.form.get('platz_2') == 'Platz 2':
            n = 1
        elif request.form.get('platz_3') == 'Platz 3':
            n = 2
        elif request.form.get('platz_4') == 'Platz 4':
            n = 3
        elif request.form.get('platz_5') == 'Platz 5':
            n = 4
        elif request.form.get('platz_6') == 'Platz 6':
            n = 5
        elif request.form.get('platz_7') == 'Platz 7':
            n = 6
        else: 
            logger.info("unknown button pressed")
        
        msg = json.dumps({"cmd": "press-button", "n": n})
        logger.info("queue_c_to_s.put: {}".format(msg))
        if conf.IPC_FLAG: 
            queue_c_to_s.put(msg)
            resp = queue_s_to_c.get() # ok
        logger.info("queue_s_to_c.get: {}".format(resp))

    import time as ti; ti.sleep(0.1)
    msg = '{"cmd": "get-outputs"}'
    logger.info("queue_c_to_s.put: {}".format(msg))
    if conf.IPC_FLAG: 
        queue_c_to_s.put(msg) 
        outputs = queue_s_to_c.get()
    # outputs is a byte (0, b6, b5, b4, b3, b2, b1, b0)
    # bits is a list [b0, b1, b2, b3, b4, b5, b6]
    b0 = 1 if outputs&0x01 else 0
    b1 = 1 if outputs&0x02 else 0
    b2 = 1 if outputs&0x04 else 0
    b3 = 1 if outputs&0x08 else 0
    b4 = 1 if outputs&0x10 else 0
    b5 = 1 if outputs&0x20 else 0
    b6 = 1 if outputs&0x40 else 0
    bits = [b0, b1, b2, b3, b4, b5, b6]
    return render_template('manuell.html',  title='Manuell', 
                           status_form=status_form, bits=bits)


@app.route('/newjob', methods=['GET', 'POST'])
def newjob():
    form_input = InputForm()
    if form_input.validate_on_submit():
        #print("===2===")
        # Wird nach dem Submit unten bei ===1=== nochmal aufgerufen!
        # Pruefe, ob form_input.date_start.data und form_input.time_start.data
        # in der Tinydb bereits vorkommen!
        dtstr = form_input.date_start.data + "T" + form_input.time_start.data + ":00"
        msg = json.dumps({"cmd": "date-exists", "date": dtstr})
        logger.info("queue_c_to_s.put: {}".format(msg))
        if conf.IPC_FLAG: queue_c_to_s.put(msg)
        exists = queue_s_to_c.get() # True or False
        logger.info("queue_s_to_c.get: {}".format(exists))
        if not exists:
            crts = ""
            if form_input.platz_1.data:
                crts = crts + "*"
            else:
                crts = crts + "."
            if form_input.platz_2.data:
                crts = crts + "*"
            else:
                crts = crts + "."
            if form_input.platz_3.data:
                crts = crts + "*"
            else:
                crts = crts + "."
            if form_input.platz_4.data:
                crts = crts + "*"
            else:
                crts = crts + "."
            if form_input.platz_5.data:
                crts = crts + "*"
            else:
                crts = crts + "."
            if form_input.platz_6.data:
                crts = crts + "*"
            else:
                crts = crts + "."
            if form_input.platz_7.data:
                crts = crts + "*"
            else:
                crts = crts + "."

            js = json.dumps({"status": "active", 
                             "start": dtstr, 
                             "duration": int(form_input.time_dauer.data), 
                             "courts": crts, 
                             "cycle": form_input.zyklus_zeit.data})

            msg = '{"cmd": "store-job", "job": ' + js + '}'
            logger.info('routes.py newjob/: {}'.format(msg))

            if conf.IPC_FLAG: 
                queue_c_to_s.put(msg)
                resp = queue_s_to_c.get() # ok

        else:
            flash("Der Auftrag existiert bereits")
        return redirect(url_for('jobs'))

    #print("===1===")
    return render_template('newjob.html', title='Neuer Job', form_input=form_input)


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():

    # Get an unsorted list of jobs
    if conf.IPC_FLAG: 
        msg = '{"cmd": "get-jobs"}'
        queue_c_to_s.put(msg)
        jobs = queue_s_to_c.get() # list of dicts
    termine = []
    for job in jobs:
        t = termin.Termin()
        t.status = job["status"]
        t.datumuhrzeit_start = job["start"] 
        t.time_dauer = job["duration"]  # int
        if job["courts"][0] == '*': 
            t.platz_1 = True 
        else: 
            t.platz_1 = False
        if job["courts"][1] == '*': 
            t.platz_2 = True 
        else: 
            t.platz_2 = False
        if job["courts"][2] == '*': 
            t.platz_3 = True 
        else: 
            t.platz_3 = False
        if job["courts"][3] == '*': 
            t.platz_4 = True 
        else: 
            t.platz_4 = False
        if job["courts"][4] == '*': 
            t.platz_5 = True 
        else: 
            t.platz_5 = False
        if job["courts"][5] == '*': 
            t.platz_6 = True 
        else: 
            t.platz_6 = False
        if job["courts"][6] == '*': 
            t.platz_7 = True 
        else: 
            t.platz_7 = False
        t.zyklus = job["cycle"]   # "no" or "daily"
        termine.append(t)
    return render_template('jobs.html', title='Aufträge', termine=termine)



@app.route('/flipstatus', methods=['POST'])
def jobstatus():
    datumuhrzeit_start = request.form.get('uhrzeit')
    if conf.IPC_FLAG: 
        msg = '{"cmd": "toggle-status-by-date", "date": ' + '\"'+datumuhrzeit_start+'\"' + '}'
        queue_c_to_s.put(msg)
        r = queue_s_to_c.get() 
    return redirect(url_for('jobs'))



@app.route("/delete", methods=["POST"])
def delete():
    datumuhrzeit_start = request.form.get('uhrzeit')
    if conf.IPC_FLAG: 
        msg = '{"cmd": "delete-job-by-date", "date": ' + '\"'+datumuhrzeit_start+'\"' + '}'
        queue_c_to_s.put(msg)
        result = queue_s_to_c.get() 
    return redirect(url_for('jobs'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    sfo = SettingsForm()

    class Einstellungen:
        pass

    if conf.IPC_FLAG: 
        msg = '{"cmd": "get-settings" }'
        queue_c_to_s.put(msg)
        result = queue_s_to_c.get()  # list of dict
        logger.info("/settings: {}".format(msg))

    einstellungen = Einstellungen()
    einstellungen.dauer_manuell = result[1]['val']  # int!

    if sfo.validate_on_submit():
        if isNotBlank(sfo.dauer_manuell.data):
            einstellungen.dauer_manuell = int(sfo.dauer_manuell.data)

        if conf.IPC_FLAG: 
            D = {'type': 'manual_delay', 'val': int(sfo.dauer_manuell.data)}
            msg = json.dumps({"cmd": "set-settings", "manual_delay": D})
            logger.info("{}".format(msg))
            queue_c_to_s.put(msg)
            result = queue_s_to_c.get()  

        return redirect(url_for('settings'))

    return render_template('settings.html',  
                           title='Einstellungen', 
                           sfo=sfo, 
                           einstellungen=einstellungen)



@app.route('/setdatetime', methods=['GET', 'POST'])
def setdatetime():
    form_setdatetime = SetDateTimeForm()

    if form_setdatetime.validate_on_submit():
        if isNotBlank(form_setdatetime.date_new.data):
            # date is set in controller/rtc.py
            pass
        if isNotBlank(form_setdatetime.time_new.data):
            # time is set in controller/rtc.py
            pass

        if conf.IPC_FLAG: 
            msg = json.dumps({"cmd": "set-datetime", 
                              "date": form_setdatetime.date_new.data,
                              "time": form_setdatetime.time_new.data})
            logger.info("{}".format(msg))
            queue_c_to_s.put(msg)
            result = queue_s_to_c.get() # ok 

        return redirect(url_for('setdatetime'))

    import time 
    datum = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    uhrzeit = time.strftime("%H:%M:%S", time.localtime(time.time()))
    return render_template('setdatetime.html', title='Einstellungen', 
           form_setdatetime=form_setdatetime, uhrzeit=uhrzeit, datum=datum)



# Filterfunktionen für Jinja

def format_datetime(value):
    x = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    return x.strftime("%d.%m.%Y, %H:%M")

def format_platz(value):
    if value == True:
        return 'x'
    else:
        return '-'

def format_zyklus(value):
    if value == "no":
        return 'einmalig'
    elif value == "daily":
        return 'täglich'
    else:
        return 'unbekannt'

def format_status(value):
    if value == "active":
        return 'Aktiv'
    elif value == "inactive":
        return 'Inaktiv'

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['platz'] = format_platz
app.jinja_env.filters['zyklus'] = format_zyklus
app.jinja_env.filters['status'] = format_status


# Funktion um leere strings zu überprüfen
def isNotBlank(value):
    if not value:
        return False
    else:
        return True


if __name__ == "__main__":
    app.run('0.0.0.0', port=80, debug=True)
