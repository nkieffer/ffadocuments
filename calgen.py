from google.appengine.ext import db
import calendar
import datetime
from dbmodels import Assignment, Site
import logging

class Month():
    names = [ "January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    def __init__(self, year, month, request):
        self.month = month
        self.name = self.names[month-1]
        self.year = year
        self.calendar = calendar.Calendar(0)
        self.weeks = []
        self.request = request
        
    def addWeek(self,  week):
        self.weeks.append(week)

    def populate(self):
        country = self.request.get("country")
        partner = self.request.get("partner")
        project = self.request.get("project")
        site = self.request.get("site")

        oneweek = datetime.timedelta(days=7)
        weeks = [x[0] for x in  self.calendar.monthdatescalendar(self.year, self.month) if x[0].month == self.month]
        a_query = Assignment.get_all()#_all()
        a_query.filter("end_date >", weeks[0])
        for week in weeks:
            a_query.filter("end_date >", week).order("end_date")
#            a_query = db.GqlQuery("SELECT * FROM Assignment WHERE start_date < :1 ORDER BY start_date, end_date DESC", week + oneweek)

            assignments = [a for a in a_query]
            assignments = filter(lambda a: week >= a.start_date.date(), assignments)
            if country:
                assignments = filter(lambda a: a.site.country == country, assignments)
            if partner:
                assignments = filter(lambda a: unicode(a.partner.key()) == unicode(partner), assignments)

            if project:
                assignments = filter(lambda a: unicode(a.project.key()) == unicode(project), assignments)

            if site:
                assignments = filter(lambda a: unicode(a.site.key()) == unicode(site), assignments)



            if len(assignments) > 0:
                assignments = sorted(assignments, key=lambda a: a.project.name)
                new_week = Week(week)
                new_week.setAssignments(assignments)
                self.addWeek(new_week)
            

class Week():
    def __init__(self, week):
        self.week = week
        self.strweek = week.strftime("%Y-%m-%d")
        self.oneweek = datetime.timedelta(days=7)
        self.__assignments = []
    def setAssignments(self, assignments):
        oneweek = datetime.timedelta(days=7)
        self.__assignments = assignments
        for a in self.__assignments:
            a.weeks_remaining = ((a.end_date.date() - self.week).days + 1)/7
            a.first_week = (self.week + oneweek) >= a.start_date_date >= self.week
            a.last_week = (self.week + oneweek) >= a.end_date_date >= self.week

    @property
    def assignments(self):
        return self.__assignments

