
from tinydb import TinyDB, Query, where
import datetime
from singleton import Singleton
import config


q = Query()


class RainDB(Singleton):

    def __init__(self):
        self.db = TinyDB(config.DBPATH)  # open database

    def store_job(self, job):
        jobs = self.db.table('jobs', cache_size=0)
        jobs.insert(job)

    def date_exists(self, date):
        '''Check if a job with same iso date (ex. 2020-05-17T23:15:00) 
           is in the db.
        '''
        jobs = self.db.table('jobs', cache_size=0)
        all_jobs = jobs.all()
        for dbjob in all_jobs:
            if dbjob["start"] == date:
                return True
        return False

    def get_jobs(self):
        jobs = self.db.table('jobs', cache_size=0)
        return jobs.all()  # list of dicts

    def delete_job_by_date(self, date):
        jobs = self.db.table('jobs', cache_size=0)
        r = jobs.remove(where('start') == date) 
        return r  # returns list of deleted doc_ids

    def toggle_status(self, date):
        jobs = self.db.table('jobs', cache_size=0)
        lod = jobs.search(where('start') == date) 
        status = lod[0]['status']
        if status == "act":
            status = "ina"
        else:
            status = "act"
        r = jobs.update({"status": status}, where('start') == date)
        return r, status  # return tuple list of doc_ids, new status 'act' or 'ina'

    def get_settings(self):
        settings = self.db.table('settings', cache_size=0)
        return settings.all()

    def get_setting_val(self, stype):
        settings = self.db.table('settings', cache_size=0)
        return settings.search(q.type == stype)[0]['val']

    def set_manual_delay(self, n):
        settings = self.db.table('settings', cache_size=0)
        return settings.update({'val': n}, q.type == 'manual_delay')
    
    def close(self):
        self.db.close() 


if __name__ == "__main__":
    rdb = RainDB()
    jobs = rdb.get_jobs()
    # print(jobs)
    for job in jobs:
        print(job)
    s = rdb.get_settings() # return a list of dicts
    print(s)
    v = rdb.get_setting_val('manual_delay')
    print(v)

    r, s = rdb.toggle_status('2020-05-26T08:00:00')
    print( (r, s) )

    rdb.close()

