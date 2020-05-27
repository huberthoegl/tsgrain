import json
import time
from datetime import datetime
from datetime import timedelta
from singleton import Singleton
import db
import config
import clock1m
import logging


class CourtTimeslot:

    def __init__(self, court, starttime, endtime, jobdict):
        
        self.court = court   #  0, 1, ..., NCOURTS-1
        self.starttime = starttime  # datetime obj
        self.endtime = endtime # datetime obj
        self.jobdict = jobdict

    def check(self, dt):
        '''dt is a datetime object'''
        if self.jobdict['cycle'] == '0':
            # one-time rain cycle
            if self.starttime <= dt < self.endtime:
                return True
            else:
                return False
        elif self.jobdict['cycle'] == '24':
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
        delta = timedelta(seconds=int(D['duration']) * 60)
        self.cts_list = []
        for i in range(config.NCOURTS):
            if D['courts'][i] == '*':
                cts = CourtTimeslot(i, dt, dt + delta, self.jobdict)
                self.cts_list.append(cts) 
                dt = dt + delta
            else:
                pass

    def is_intime(self, dt):
        '''check if time dt is somewhere in the timeslot list. If true,
        return the court number (0...6). If not, return None.

        A daily job (cycle='24') is intime every day after the start date
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
        if self.jobdict['status'] == 'act':
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
        if now >= self.cts_list[-1].endtime and self.jobdict['cycle'] == '0':
            return True
        else:
            return False

    def print(self):
        for cts in self.cts_list:
            print(cts)


class AutoCtrl(Singleton):
    def __init__(self):
        self.logger = logging.getLogger(config.TSGRAIN_LOGGER)
        clock1m.add_handler(self.min1cb)
        clock1m.start()
        self.rdb = db.RainDB() # singleton
        self.logger.info("starting 1 min periodic callback handler")
        self.current = None

    def min1cb(self):
        # callback every minute constructs an up-to-date sequence list
        jobs = self.rdb.get_jobs()
        self.seqlist = []
        for job in jobs:
           self.seqlist.append(Sequence(job))

        now = datetime.fromtimestamp(time.time())
        for s in self.seqlist:
            if s.is_active():
                self.auto_court = s.is_intime(now)
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
    adict = {'status': 'act', 'start': '2020-05-26T23:30:00', 'duration': '30', 
             'courts': '*******', 'cycle': '0'} 

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

