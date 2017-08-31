#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#import atom
import sys
#sys.path.insert(0, "reportlab.zip")
from google.appengine.ext import webapp
import webapp2
import dbmodels
#import volunteers, partners, projects, sites, assignments, api, pdftest, settings, invoices
import reportlab
import os, sys
from google.appengine.ext.webapp import template, util
from utilities import *
from dbmodels import *
from csv import writer
import StringIO
import zipfile
import reportlab
import datetime
import logging
import random
from google.appengine.api import users

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect("/calendar")
        else:
            self.redirect(users.create_login_url("/"))

class Dump(webapp2.RequestHandler):
    def get(self):
        tables = [Partner.all(),
                Volunteer.all(),
                Project.all(),
                Site.all(),
                Assignment.all(),
                Invoice.all()]
        out = StringIO.StringIO()
        z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
        date = datetime.datetime.now()
        for table in tables:
            model = str(table._model_class).replace("<","").replace(">","").replace("class", "").replace(" ", "").replace("'","")
            fn = "%s.%s.xml" % (model, date.strftime("%Y-%m-%d"))
            dio = StringIO.StringIO()
            dio.write("<?xml version='1.0' encoding='ISO-8859-1'?><%ss date='%s'>" % (model, date.strftime("%Y-%m-%d")))
            for row in table:
                dio.write(row.to_xml())
            dio.write("</%ss>" % model)
            z.writestr(fn, dio.getvalue())
        z.close()
        out.seek(0)
        self.response.headers.add_header("Content-type", "application/zip")
        self.response.headers.add_header("Content-disposition", 'attachment; filename=ffabackup.zip')
        self.response.out.write( out.read())

class API(webapp2.RequestHandler):
    def get(self, id):
        self.response.out.write(id)
def name():
        letters = "abcdefghijklmnopqrstuvwxyz"
        name = "".join([ random.choice(letters) for i in range(0, random.randint(5,10))])
        return name
class GenData(webapp2.RequestHandler):
    def get(self):

        partners = []
        while True:
            paname = name()
            p = dbmodels.Partner(name=paname, abbr=paname[:2], comment=paname+" "+paname, address="here\nthere\neverywhere")
            p.put()
            partners.append(p)
            if random.random() <.05:
                break
        logging.info(partners)
        projects = []
        while True:
            prname = name()
            price = 1000+(1000*random.random())
            pr = dbmodels.Project(name=prname, abbr=prname[:2], price=price, additionalWeekPrice=price*.1, minimum_duration=2, comment="No Comment")
            pr.put()
            projects.append(pr)
            if  random.random() < .05:
                break
        volunteers = []
        while True:
            vol = dbmodels.Volunteer()
            vol.fname = name()
            vol.lname = name()
            vol.country = random.choice(("US", "CA", "FR", "DE", "NE", "EN"))
            vol.DOB = datetime.datetime(random.randint(1970, 1985), random.randint(1,12), random.randint(1,27))
            vol.email = vol.fname+vol.lname+"@"+name()+".com"
            vol.partner = random.choice(partners)
            vol.address = "Here\nThere\nEverywhere"
            vol.emergency = "!!!"
            vol.comment = "---"
            vol.status = "OK"
            vol.put()
            volunteers.append(vol)
            if random.random() < .02:
                break
        
        for v in volunteers:
            while True:
                a = dbmodels.Assignment()
                a.volunteer = v
                a.project = random.choice(projects)
                a.project_name = a.project.name
                a.volunteer_name = a.volunteer.name
                a.partner = v.partner
                a.partner_name = v.partner.name
                now = datetime.datetime.now()
                delta = datetime.timedelta(days=now.weekday())
                basedate = now-delta
                a.start_date = basedate + datetime.timedelta(weeks=random.randint(0, 10))
                a.end_date = a.start_date + datetime.timedelta(weeks=random.randint(2,20))
                a.num_weeks = (a.end_date - a.start_date).days / 7
                a.put()
                n = dbmodels.NewAssignment()
                n.assignment = a
                n.put()
                if random.random > 0.05:
                    break
                                                       
routes= [
    ('/', MainHandler),
    webapp2.Route('/calendar', handler="assignments.Show"),
    webapp2.Route('/volunteers', handler="volunteers.Show", name="volunteers"),
    webapp2.Route('/volunteersNew', handler="volunteers.ShowNew", name="volunteersNew"),
    webapp2.Route('/volunteerForm', handler="volunteers.Form", name="volunteerForm"),
    webapp2.Route('/volunteerEdit', handler="volunteers.Edit", name="volunteerEdit"),
    webapp2.Route('/volunteerDelete', handler="volunteers.Delete", name="volunteerDelete"),
    webapp2.Route('/volunteerCreateCache', handler="volunteers.CreateCache", name="volunteerCreateCache")
,
    webapp2.Route('/volunteerRetrieveCache', handler="volunteers.RetrieveCache", name="volunteerRetrieveCache"),
    webapp2.Route('/partners', handler="partners.Show"),
    webapp2.Route('/partnerForm', handler="partners.Form"),
    webapp2.Route('/partnerEdit', handler="partners.Edit"),
    webapp2.Route('/partnerDelete', handler="partners.Delete"),
    webapp2.Route('/invoiceGen', handler="invoices.Generate"),
    webapp2.Route('/invoices', handler="invoices.Show"),
    webapp2.Route('/invoiceForm', handler="invoices.Form"),
    webapp2.Route('/invoiceView', handler="invoices.View"),
    webapp2.Route('/invoiceJSON', handler="invoices.JSON"),
    webapp2.Route('/invoiceSave', handler="invoices.Save"),
    webapp2.Route('/invoiceDelete', handler="invoices.Delete"),
    webapp2.Route('/projects', handler="projects.Show"),
    webapp2.Route('/projectForm', handler="projects.Form"),
    webapp2.Route('/projectEdit', handler="projects.Edit"),
    webapp2.Route('/projectDelete', handler="projects.Delete"),
    webapp2.Route('/siteForm', handler="sites.Form"),
    webapp2.Route('/siteEdit', handler="sites.Edit"),
    webapp2.Route('/siteDelete', handler="sites.Delete"),
    webapp2.Route('/assignments', handler="assignments.Show"),
    webapp2.Route('/assignmentForm', handler="assignments.Form"),
    webapp2.Route('/assignmentEdit', handler="assignments.Edit"),
    webapp2.Route('/assignmentDelete', handler="assignments.Delete"),
    webapp2.Route('/ajaxAssignment', handler="assignments.ajaxAssignment"),
    webapp2.Route('/ajaxComment', handler="assignments.ajaxComment"),
    webapp2.Route('/dump', Dump),
    ('/api/(.+)', API),#"api.Api"),
    webapp2.Route('/pdf', handler="pdftest.PDF"),
    webapp2.Route('/settings', handler="settings.Show"),
    webapp2.Route('/settingsEdit', handler="settings.Edit"),
    webapp2.Route('/tasks/calgen', handler="tasks.calgen.Run"),
    webapp2.Route('/gendata', handler=GenData)
    ]
                
app = webapp2.WSGIApplication( routes,  config = { "ADD_PARTNER" : False },
                                 debug=True)
#    util.run_wsgi_app(app)

#if __name__=="__main__":
#    main()
    


