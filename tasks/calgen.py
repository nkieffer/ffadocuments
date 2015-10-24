from google.appengine.ext import db
import calendar
import datetime
from dbmodels import Assignment, Calendar, NewAssignment
import logging
import webapp2
import pickle
def assignmentDict(model):
    pass
    
class Run(webapp2.RequestHandler):
    def get(self):
        manual = self.request.get("manual") == "1"
        num_months = 6

        now = datetime.datetime.now().date()
        this_week = now - datetime.timedelta(days=now.weekday())
        dmonth = this_week.month + num_months
        if dmonth > 11:
            dyear = this_week.year + 1
            dmonth = dmonth - 11
        else:
            dyear = this_week.year
        logging.info("{} {}".format(dyear,dmonth))
        end_date = datetime.date(year=dyear, month=dmonth, day=1)
        logging.info(end_date)
        assignments = Assignment.gql("WHERE end_date > :1 ORDER BY end_date", now )
        assignments = [ a for a in assignments if a.start_date.date() < end_date ]
        assignments = sorted(assignments, key=lambda a: a.project_name)
        one_week = datetime.timedelta(days=7)
        weeks = []
        while this_week < end_date:
            this_weeks_assignments = [] 
            for a in assignments:
                
                if a.start_date.date() <= this_week <= a.end_date.date() - datetime.timedelta(days=6):
#                    a.weeks_remaining = ((a.end_date.date() - this_week).days + 1)/7
#                    logging.info(a.weeks_remaining)
                    this_weeks_assignments.append(a)

            weeks.append((this_week, this_weeks_assignments))
            this_week += one_week
        logging.info(weeks)
        calendar = Calendar.get_or_insert("main", title="Main Calendar Data")
        calendar.data = pickle.dumps(weeks)
        calendar.timestamp = datetime.datetime.now()
        calendar.manual = manual
        calendar.put()

        #delete all the NewAssignments that are now in the calendar

        db.delete(NewAssignment.all(keys_only=True))
        if manual:
            self.redirect("/settings?status=calgen")
        
