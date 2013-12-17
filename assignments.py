
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import dbmodels
import os
import json
import datetime
import calgen
import math
import logging
import time
from utilities import *
from google.appengine.ext.webapp import template
from dbmodels import Partner, Project, Site, Volunteer


class Show(webapp.RequestHandler):
    def get(self):
        
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "assignments.html"
        v.pageinfo.title = "Calendar"
        v.params = TemplateValues()
        v.params.country = self.request.get("country")
        v.params.partner = self.request.get("partner")
        v.params.project = self.request.get("project")
        v.params.site = self.request.get("site")
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        ct = 0
        v.months = []
        t1 = time.time()
        while ct < 12:
            thisMonth = calgen.Month(year, month, self.request)
            thisMonth.populate()
            v.months.append(thisMonth)
            month += 1
            if month ==13:
                month = 1
                year += 1
            ct += 1
       # for m in v.months:
       #     m.populate()
        t2 = time.time()
        logging.info("calgen: %f" % (t2 - t1))
        v.partners = db.GqlQuery("SELECT  name FROM Partner").fetch(1000)
        v.projects = db.GqlQuery("SELECT  name FROM Project").fetch(1000)
        v.countries = db.GqlQuery("SELECT DISTINCT country FROM Site").fetch(1000)
        v.sites = db.GqlQuery("SELECT name FROM Site").fetch(1000)
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Form(webapp.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "assignmentForm.html"
        v.pageinfo.title = "Assignment Form"
        v.weeks = range(52)
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
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp.RequestHandler):
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
        assignment.site = dbmodels.Site.get(self.request.get('site'))
        assignment.start_date = datetime.datetime(*sd)
        assignment.end_date = datetime.datetime(*ed)
        assignment.comment = self.request.get('comment')
        assignment.discount = float(self.request.get('discount'))
        assignment.put()
        logging.info( str(assignment.start_date)+" "+ str(assignment.end_date))
        self.redirect('/volunteerForm?key=' + vkey)

class Delete(webapp.RequestHandler):
    def get(self):
        akey = self.request.get('akey')
        vkey = self.request.get('vkey')
        assignment = dbmodels.Assignment.get(akey)
        db.delete(assignment)
        self.response.out.write(akey+"<br>")
        self.response.out.write(vkey+"<br>")
        self.redirect('/volunteerForm?key=' + vkey)
        
class ajaxAssignment(webapp.RequestHandler):
    def get(self):
        start_date = self.request.get('start_date')
        end_date = self.request.get('end_date')
        project = dbmodels.Project.get(self.request.get('project'))
        site = dbmodels.Site.get(self.request.get('site'))
        respData = []
        assignments = dbmodels.Assignment.all()
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

class ajaxComment(webapp.RequestHandler):
    def get(self):
        assignmentid = self.request.get('assignmentid')
        comment = self.request.get('comment')
        assignment = dbmodels.Assignment.get(assignmentid)
        assignment.comment = comment
        assignment.put()
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps({"message":""}))
