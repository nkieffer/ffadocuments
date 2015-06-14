

#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import memcache
import dbmodels
import os
import json
import datetime
import calgen
import math
import logging
import time
import pickle
from utilities import *
import views
from google.appengine.ext.webapp import template
from dbmodels import Partner, Project, Site, Volunteer, Settings, Calendar
from StringIO import StringIO

class Show(webapp2.RequestHandler):
    def get(self):
        t1 = time.time()        
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "assignments.html"# views.assignments
        logging.info(v.pageinfo.html)
        v.pageinfo.title = "Calendar"
        v.params = TemplateValues()
#        v.params.country = self.request.get("country")
#        v.params.partner = self.request.get("partner")
#        v.params.project = self.request.get("project")
#        v.params.site = self.request.get("site")
        v.calendar = sorted(pickle.loads(Calendar.get_by_key_name("main").data))
        new_assignments = dbmodels.NewAssignment.all()
        for i, week in enumerate(v.calendar):
            for assignment in new_assignments:
                if assignment.assignment.start_date.date() <= week[0] <=  assignment.assignment.end_date.date():
                    v.calendar[i][1].append(assignment.assignment)
            v.calendar[i][1].sort(key=lambda a: (a.project_name, a.start_date,a.end_date))
            
        logging.info(v.calendar)
        
        
        # for week, assignments in sorted(v.calendar.items(), key=lambda i: i[0]):
        #     self.response.out.write("<h6>{}</h6>".format(week))
        #     self.response.out.write("<ul>")
        #     for a in assignments:
        #         self.response.out.write("<li>{} {} {}</li>".format(a.project.name, a.start_date.date(), a.end_date.date()))
        #     self.response.out.write("</ul>")
        # now = datetime.datetime.now()
        # year = now.year
        # month = now.month
       # settings = Settings.get_all()
       # try:
       #     num_months = Settings.get_all().num_months
       # except:
        # num_months = 4
        # logging.info("num_months = " + str(int(num_months)))
        #v.months = memcache.get("calendar")
        #if v.months is None:
        # v.months = []
        
        # ct = 0
        # while ct < num_months:
        #     thisMonth = calgen.Month(year, month, self.request)
        #     thisMonth.populate()
        #     tm = TemplateValues()
        #     tm.name = thisMonth.name
        #     tm.year = thisMonth.year
        #     tm.weeks = thisMonth.weeks
        #     logging.info("TM:\n\t" + str(tm))
        #     cacheKey = "calendar:%d:%d" % (year, month)
        #     monthHTML = memcache.get(cacheKey)
        #     if monthHTML is None:
        #         path = os.path.join(os.path.dirname(__file__), "views", "calendar.html")
        #         monthHTML = template.render(path, {"tm" : tm })
        #         logging.info("Creating cache: %s" % cacheKey)
        #         memcache.add(cacheKey, monthHTML)
        #     else:
        #         logging.info("Using cache: %s" % cacheKey)
        #     v.months.append(monthHTML)
        #     month += 1
        #     if month ==13:
        #         month = 1
        #         year += 1
        #     ct += 1
        # v.partners = Partner.get_all(False)#db.GqlQuery("SELECT  name FROM Partner").fetch(1000)
        # v.projects = Project.get_all()#db.GqlQuery("SELECT  name FROM Project").fetch(1000)
        # v.countries = memcache.get("countries")
        # if v.countries is None:
        #     v.countries = db.GqlQuery("SELECT DISTINCT country FROM Site").fetch(1000)
        #     memcache.add("countries", v.countries)

        # v.sites = Site.get_all()#db.GqlQuery("SELECT name FROM Site").fetch(1000)

 #       t2 = time.time()
 #       logging.info("calgen: %f" % (t2 - t1))

        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        logging.info(template.render("views/assignments.html", {"v":v}))
        self.response.out.write(template.render(path, { "v" : v }))

class Form(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.assignmentForm
        v.pageinfo.title = "Assignment Form"
        v.weeks = range(2,52)
        origin = self.request.get('origin')
        if origin == "calendar":
            v.project = Project.get(self.request.get('project'))
            v.calsites = Site.all()
            v.calsites.filter("project =", v.project.key())
            v.site = Site.get(self.request.get('site'))
            v.start_date = self.request.get('start_date')
            v.sites = dbmodels.Site.all()
            v.projects = dbmodels.Project.all()
            v.volunteers = Volunteer.all()
            
        else:
            vkey = self.request.get('vkey')
            akey = self.request.get('akey')
            if akey == '':
                pass
            else:
                v.assignment = dbmodels.Assignment.get(akey)
            v.vkey = vkey
            v.volunteer = dbmodels.Volunteer.get(vkey)
            v.sites = dbmodels.Site.all()
            v.projects = dbmodels.Project.all()
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp2.RequestHandler):
    def post(self):
        akey = self.request.get('akey')
        vkey = self.request.get('vkey')
 #       print self.request
        partnerkey = self.request.get('partnerkey')
        if akey == '':
            assignment = dbmodels.Assignment()
            assignment.reg_date = datetime.datetime.now() 
            assignment.volunteer = dbmodels.Volunteer.get(self.request.get('vkey'))
        else:
            assignment = dbmodels.Assignment.get(akey)
        sd = [ int(x) for x in self.request.get('start_date').split("-")]
        ed = [ int(x) for x in self.request.get('end_date').split("-")]
        assignment.partner = dbmodels.Partner.get(partnerkey)
        assignment.project = dbmodels.Project.get(self.request.get('project'))
        assignment.project_name = assignment.project.name
        assignment.partner_name = assignment.partner.name
        assignment.volunteer_name = assignment.volunteer.name
#        assignment.site = dbmodels.Site.get(self.request.get('site'))
        assignment.start_date = datetime.datetime(*sd)
        assignment.end_date = datetime.datetime(*ed)
        logging.info("--------"+self.request.get('weeks'))
        assignment.num_weeks = int(self.request.get('weeks'))
        logging.info("++++++++"+str(assignment.num_weeks))
        assignment.comment = self.request.get('comment')
#        assignment.discount = float(self.request.get('discount'))
        assignment.put()
        new_assignment = dbmodels.NewAssignment()
        new_assignment.assignment = assignment
        new_assignment.put()
        months = (assignment.end_date - assignment.start_date).days/30
        year = assignment.start_date.year
        month = assignment.start_date.month
        #Delete memcache for each calendar month this assignment should 
        #Appear in
        while months >= 0:
            cache_name = "calendar:{}:{}".format(year, month)
            logging.info("deleting cache: {}".format(cache_name))
            memcache.delete(cache_name)
            month += 1
            if month == 13:
                month = 0
                year += 1
            months -= 1
                           
        memcache.delete("assignment:volunteer:%s" % vkey)
        logging.info( str(assignment.start_date)+" "+ str(assignment.end_date))
        self.redirect('/volunteerForm?key=' + vkey)

class Delete(webapp2.RequestHandler):
    def get(self):
        akey = self.request.get('akey')
        vkey = self.request.get('vkey')
        assignment = dbmodels.Assignment.get(akey)
        db.delete(assignment)
        self.response.out.write(akey+"<br>")
        self.response.out.write(vkey+"<br>")
        self.redirect('/volunteerForm?key=' + vkey)
        
class ajaxAssignment(webapp2.RequestHandler):
    def get(self):
        start_date = self.request.get('start_date')
        end_date = self.request.get('end_date')
        project = dbmodels.Project.get(self.request.get('project'))
        site = dbmodels.Site.get(self.request.get('site'))
        respData = []
        assignments = dbmodels.Assignment.get_all()
        assignments.filter("site = ", site)
#        assignments.filter("start_date >=",
#                           datetime.datetime(*[int(x) for x in self.request.get('start_date').split("-")]))
#        assignments.filter("end_date <=",
#                           datetime.datetime(*[int(x) for x in self.request.get('end_date').split("-")]))
#        assignments.filter("project =", project)
#        assignments.filter("site =", site)

        if assignments.count(1000) > 0:
            for a in assignments:
                respData.append({ "vname" : "%s, %s" % (a.volunteer.lname, a.volunteer.fname),
                              "start_date" : a.start_date_str,
                              "end_date" : a.end_date_str,
                              "duration" : str(a.duration) })
        else:
            respData.append("No Assignments")
        respData.append(site.capacity)
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(respData))

class ajaxComment(webapp2.RequestHandler):
    def get(self):
        assignmentid = self.request.get('assignmentid')
        comment = self.request.get('comment')
        assignment = dbmodels.Assignment.get(assignmentid)
        assignment.comment = comment
        assignment.put()
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps({"message":""}))
