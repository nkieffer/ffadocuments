import webapp2
import logging
import datetime
import json
import os
import views
from utilities import *
from dbmodels import Assignment, Archive
from tasks import calgen
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
def new_week():
    return [ {},{},{},{},{},{},{},{},{},{},{},{}]
SC = 0#starts by country
SA = 1#starts by age
SP = 2#starts by project
SR = 3#starts by partner



def set_data(archive, key, country, yob, project, partner, OCCUPANCY=False):
    OCCUPANCY = 4 if OCCUPANCY else 0 
    if not archive.has_key(key):
        archive[key] = new_week()
    if archive[key][SC+OCCUPANCY].has_key(country):
        archive[key][SC+OCCUPANCY][country] += 1
    else:
        archive[key][SC+OCCUPANCY][country] = 1

    if archive[key][SA+OCCUPANCY].has_key(yob):
        archive[key][SA+OCCUPANCY][yob] += 1
    else:
        archive[key][SA+OCCUPANCY][yob] = 1

    if archive[key][SP+OCCUPANCY].has_key(project):
        archive[key][SP+OCCUPANCY][project] += 1
    else:
        archive[key][SP+OCCUPANCY][project] = 1

    if archive[key][SR+OCCUPANCY].has_key(partner):
        archive[key][SR+OCCUPANCY][partner] += 1
    else:
        archive[key][SR+OCCUPANCY][partner] = 1

class Run(webapp2.RequestHandler):
    def get(self):
        years = self.request.get("years")
        confirm = self.request.get("confirm")
        arched_volunteers = 0
        arched_assignments = 0
        years = 1 if years == "" else int(years)
        assignments = Assignment.all()
        assignment_count = assignments.count()
        #cutoff = datetime.datetime.now() - datetime.timedelta(days=365*years)
        cutoff = datetime.datetime(years, 1, 1)
        assignments.filter("end_date <=", cutoff)
        assignments.order("end_date").order("start_date")
        logging.info(assignments.count())
        archive = {}
        durations = {}#[{}, {}, {}, {}]
        volunteers = []
        week = datetime.timedelta(weeks=1)
        for a in assignments:
            v = a.volunteer
            partner = a.partner_name
            if v not in volunteers:
                volunteers.append(v)
            yob = v.DOB.year
            country = v.country
            project_name = a.project_name
            s = a.start_date
            e = a.end_date
            year = s.year
            duration = e - s
            duration = duration.days
            slot_index = 8
            for prop in (country, yob, partner, project_name):
                key = str(s.date())
                if not archive.has_key(key):
                    archive[key] = new_week()
                if archive[key][slot_index].has_key(prop):
                    archive[key][slot_index][prop].append(duration)
                else:
                    archive[key][slot_index][prop] = [duration]
                slot_index += 1
            slot_index = 0
            for prop in (country, yob, partner, project_name):
                if not durations.has_key(s.year):
                    durations[year] = [{},{},{},{}]
                if durations[year][slot_index].has_key(prop):
                    durations[year][slot_index][prop].append(duration)
                else:
                    durations[year][slot_index][prop] = [duration]
                slot_index += 1
            key = str(s.date())

            set_data(archive, key, country, yob, project_name, partner);
            
            
            while s < e:
                month = s.month-1
                key = str(s.date())
                set_data(archive, str(s.date()), country, yob, project_name, partner, OCCUPANCY=True)
                s += week
            archive['durations'] = durations
            if confirm == "hellyes":
                a.delete()
            arched_assignments += 1
        volunteer_data = [{}, {}]
        for v in volunteers:

            if confirm == "hellyes" and v.num_assignments == 0:
                v.delete()
            arched_volunteers += 1
        
        dates = sorted(archive.keys())#filter(lambda key: key != "durations", sorted(archive.keys()))
        archive_years = {}
        for date in dates:
            year = date.split("-")[0]
            if archive_years.has_key(year):
                archive_years[year][date] = archive[date]
            else:
                archive_years[year] = {date: archive[date]}
        logging.info(durations.keys())
        for year in sorted(filter(lambda key: key != "durations", archive_years.keys())):
            arch_ent = Archive.get_or_insert(year)
            this_arch = archive_years[year]
            this_arch['durations'] = durations[int(year)]
            if arch_ent.data is None:
                arch_ent.year = int(year)
                arch_ent.data = this_arch
            else:
                data = arch_ent.data
                logging.info(type(data))
                for week in filter(lambda x: x != 'durations', this_arch.keys()):
                    if data.has_key(week):
                        for section in range(8):
                            for key in this_arch[week][section].keys():
                                if data[week][section].has_key(key):
                                    logging.info(data)
                                    logging.info(week)
                                    logging.info(section)
                                    logging.info(key)
                                    data[week][section][key] += 1
                                else:
                                    
                                    data[week][section][key] = 1
                    else:
                        data[week] = new_week()
                        for section in range(8):
                            for key in this_arch[week][section].keys():
                                if data[week][section].has_key(key):
                                    data[week][section][key] += 1
                                else:
                                    data[week][section][key] = 1
                                 
                    
            arch_ent.put()
       # for year in durations:
       #     logging.info(str(year)+"------")
       #     archive_years[str(year)]['durations'] = durations[year]
       # a = json.dumps(archive_years)
       # msg = "{} out of {} volunteers nuked<br>{} out of {} assignments nuked".format(arched_volunteers, len(volunteers), arched_assignments, assignment_count)
      #  self.response.out.write(msg+"<br><script>a ="+a+";d="+json.dumps(durations)+";</script>")

class ReportAjax(webapp2.RequestHandler):
    def get(self):
        year = self.request.get("year")
        logging.info(year)
        if year == "":
            archive = {a.year : a.data for a in Archive.query()}
        else:
            key =ndb.Key('Archive', year)
            logging.info(key)
            archive = [key.get().data]
        self.response.out.write(json.dumps(archive))

class Report(webapp2.RequestHandler):
    def get(self):
        year = self.request.get("year")
        if year == "":
            years = Archive.query().fetch(100, keys_only=True)
            v = TemplateValues()
            v.pageinfo = TemplateValues()
            v.pageinfo.html = views.reports
            logging.info(v.pageinfo.html)
            v.pageinfo.title = "Reports"
            
            path = os.path.join(os.path.dirname(__file__), views.main)
            # self.response.headers.add_header("Expires", expdate())
            v.years = years
            self.response.out.write(template.render(path, { "v" : v }))
        else:
            key = ndb.Key('Archive', year);
            self.response.out.write(json.dumps(key.get().data))
    
