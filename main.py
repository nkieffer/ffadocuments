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

routes= [
    ('/', MainHandler),
    webapp2.Route('/calendar', handler="assignments.Show"),
    webapp2.Route('/volunteers', handler="volunteers.Show", name="volunteers"),
    webapp2.Route('/volunteerForm', handler="volunteers.Form", name="volunteerForm"),
    webapp2.Route('/volunteerEdit', handler="volunteers.Edit", name="volunteerEdit"),
    webapp.Route('/partners', handler="partners.Show"),
    webapp.Route('/partnerForm', handler="partners.Form"),
    webapp.Route('/partnerEdit', handler="partners.Edit"),
    webapp.Route('/partnerDelete', handler="partners.Delete"),
    webapp.Route('/invoices', handler="invoices.Show"),
    webapp.Route('/invoiceForm', handler="invoices.Form"),
    webapp.Route('/invoiceView', handler="invoices.View"),
    webapp.Route('/invoiceJSON', handler="invoices.JSON"),
    webapp.Route('/invoiceSave', handler="invoices.Save"),
    webapp.Route('/invoiceDelete', handler="invoices.Delete"),
    webapp.Route('/projects', handler="projects.Show"),
    webapp.Route('/projectForm', handler="projects.Form"),
    webapp.Route('/projectEdit', handler="projects.Edit"),
    webapp.Route('/projectDelete', handler="projects.Delete"),
    webapp.Route('/siteForm', handler="sites.Form"),
    webapp.Route('/siteEdit', handler="sites.Edit"),
    webapp.Route('/siteDelete', handler="sites.Delete"),
    webapp.Route('/assignments', handler="assignments.Show"),
    webapp.Route('/assignmentForm', handler="assignments.Form"),
    webapp.Route('/assignmentEdit', handler="assignments.Edit"),
    webapp.Route('/assignmentDelete', handler="assignments.Delete"),
    webapp.Route('/ajaxAssignment', handler="assignments.ajaxAssignment"),
    webapp.Route('/ajaxComment', handler="assignments.ajaxComment"),
    webapp.Route('/dump', Dump),
    ('/api/(.+)', API),#"api.Api"),
    webapp.Route('/pdf', handler="pdftest.PDF"),
    webapp.Route('/settings', handler="settings.Show"),
    webapp.Route('/settingsEdit', handler="settings.Edit")
    ]
                
app = webapp2.WSGIApplication( routes,
                                 debug=True)
#    util.run_wsgi_app(app)

#if __name__=="__main__":
#    main()
    


