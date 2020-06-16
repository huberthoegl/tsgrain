import json
import time
from datetime import datetime
from datetime import timedelta
from singleton import Singleton
import db
import manctrl
import conf
import clock1m
import logging
import led3c
if conf.PLATFORM == 'pc':
    import pbutton_pc as pbutton
else:  # PLATFORM == 'rpi'
    import pbutton_rpi as pbutton



class CourtTimeslot:

    def __init__(self, court, starttime, endtime, jobdict):
        
        self.court = court   #  0, 1, ..., NCOURTS-1
        self.starttime = starttime  # datetime obj
        self.endtime = endtime # datetime obj
        self.jobdict = jobdict

    def check(self, dt):
        '''dt is a datetime object'''
        if self.jobdict['cycle'] == 'no':
            # one-time rain cycle
            if self.starttime <= dt < self.endtime:
                return True
            else:
                return False
        elif self.jobdict['cycle'] == 'daily':
            # repeat every day
            # if dt is >= than starttime, shift it days_delta days backward
            if dt >= self.starttime:
                tdo = dt - self.starttime  # timedelta obj
                days_delta = tdo.days  # 0, 1, 2, ...
                dtshifted = dt - timedelta(days=days_delta)
                if self.starttime <= dtshifted < self.endtime:
                    return True
                else:
                    return False
                
    def __str__(self):
        return "<{}#{}#{}>".format(self.court, str(self.starttime), 
                                   str(self.endtime))


class Sequence:
    '''
    Convert a job (dict) to a Sequence object. A Sequence contains 
    a list of CourtTimeslots.
    '''
    def __init__(self, D):
        self.jobdict = D
        self.startstr = self.jobdict['start']
        dt = datetime.fromisoformat(self.startstr)
        delta = timedelta(seconds=D['duration'] * 60)
        self.cts_list = []
        for i in range(conf.NCOURTS):
            if D['courts'][i] == '*':
                cts = CourtTimeslot(i, dt, dt + delta, self.jobdict)
                self.cts_list.append(cts) 
                dt = dt + delta
            else:
                pass

    def is_intime(self, dt):
        '''check if time dt is somewhere in the timeslot list. If true,
        return the court number (0...6). If not, return None.

        A daily job (cycle='daily') is intime every day after the start date
        has approached.

        dt should not match the endtime. If it matches the endtime and 
        a next timeslot exists, then the starttime of the next slot must
        be used (both are identical). If no next timeslot exists, return 
        None.
        '''
        for cts in self.cts_list:
            if cts.check(dt):
                return cts.court
            else:
                pass
        return None

    def is_active(self):
        '''check if the status of the job is active'''
        if self.jobdict['status'] == 'active':
            return True
        else:
            return False

    def is_outdated(self, otherdate=None):
        '''check if the current time is past the Sequence and if it is 
        a one time job. If both is true, the sequence can be removed from the 
        database.
        '''
        if otherdate == None:
            now = datetime.fromtimestamp(time.time())
        else:
            now = otherdate
        if now >= self.cts_list[-1].endtime and self.jobdict['cycle'] == 'no':
            return True
        else:
            return False

    def print(self):
        for cts in self.cts_list:
            print(cts)


class AutoCtrl(Singleton):
    def __init__(self):
        self.logger = logging.getLogger(conf.TSGRAIN_LOGGER)
        clock1m.add_handler(self.min1cb)
        clock1m.start()
        self.rdb = db.RainDB() # singleton
        self.logger.info("starting 1 min periodic callback handler")
        self.current = None
        self.mc = manctrl.ManCtrl()
        self._autooff_startstr = None
        self.auto_court = None

    def autooff_btn_callback(self, key):
        '''If the PBAutoOff button is pressed, a running job is changed to status 'inactive'.  
        The job is _not_ made again active when the button is pressed a second time.
        '''
        if key == pbutton.PBAutoOff:
            if self.auto_court in (0, 1, 2, 3, 4, 5, 6):
                # we have a running job
                date = self._s.startstr
                self._autooff_startstr = date
                r, s = self.rdb.toggle_status(date)
                self.logger.info("autooff_btn_callback: setting job status {}".format(s))
                if s == 'inactive':
                    for i in range(4):
                        led3c.set_led(led3c.RED)
                        time.sleep(0.5)
                        led3c.set_led(led3c.OFF)
                        time.sleep(0.5)
                    led3c.set_led(led3c.GREEN)
                    self.mc.enable()  # clear outputs, enable manual control
                    self.auto_court = None
            else:
                # XXX this works only when RPi has not been rebootet. Maybe 
                # a better solution would be to write the autooff job to the db
                if self._autooff_startstr:
                    if self.rdb.date_exists(self._autooff_startstr) and \
                       not self.rdb.job_is_active(self._autooff_startstr):
                        # job exists and is not active
                        r, s = self.rdb.toggle_status(self._autooff_startstr)
                        self.logger.info("autooff_btn_callback: should be active: {}".format(s))
                        color = led3c.get_led()
                        for i in range(4):
                            led3c.set_led(color)
                            time.sleep(0.5)
                            led3c.set_led(led3c.OFF)
                            time.sleep(0.5)
                        led3c.set_led(color)
                    self._autooff_startstr = None
        else:
            # ignore all other buttons
            return  

    def min1cb(self):
        # callback every minute constructs an up-to-date sequence list
        jobs = self.rdb.get_jobs()
        self.seqlist = []
        for job in jobs:
           self.seqlist.append(Sequence(job))

        now = datetime.fromtimestamp(time.time())
        for self._s in self.seqlist:
            if self._s.is_active():
                self.auto_court = self._s.is_intime(now)
                if self.auto_court in (0, 1, 2, 3, 4, 5, 6):
                    # switch controller state to "automatic" (disables manual ctrl)
                    if self.current != self.auto_court:  # edge-detect
                        self.logger.info("controller: auto starting court {}".format(self.auto_court))
                        self.current = self.auto_court
                    self.auto_on_hdl()
                else:
                    # switch controller state to "manual" (enables manual ctrl)
                    if self.current != self.auto_court:  # edge-detect
                        self.logger.info("controller: sequence over")
                    self.current = None
                    self.auto_off_hdl()
            else:
                # job is inactive
                self.current = None
                self.auto_off_hdl()

        # delete outdated jobs (only delete jobs which run only one time!)
        for s in self.seqlist:
            if s.is_outdated():
                self.rdb.delete_job_by_date(s.startstr)
                self.logger.info("deleted outdated job {}".format(s.startstr))

    def register_auto_on_hdl(self, f):
        self.auto_on_hdl = f

    def register_auto_off_hdl(self, f):
        self.auto_off_hdl = f

    
if __name__ == "__main__":
    adict = {'status': 'active', 'start': '2020-05-26T23:30:00', 
             'duration': 30, 'courts': '*******', 'cycle': 'no'} 

    s = Sequence(adict)
    s.print()

    dt_test = datetime.fromisoformat('2020-05-26T23:30:00')
    r = s.is_intime(dt_test)
    print("active slot?", r)

    dt_test = datetime.fromisoformat('2020-05-29T01:20:00')
    r = s.is_intime(dt_test)
    print("active slot?", r)

    dt_test = datetime.fromisoformat('2020-06-15T02:00:59')
    r = s.is_intime(dt_test)
    print("active slot?", r)

    r = s.is_outdated(otherdate=dt_test)
    print("outdated?", r)

    r = s.is_outdated(otherdate=dt_test)
    print("outdated?", r)

