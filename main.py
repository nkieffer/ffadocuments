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
import views
from google.appengine.api import users

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if users:
            v = TemplateValues()
            path = os.path.join(os.path.dirname(__file__), "index.html")
            self.response.out.write(template.render(path, { "v" : v }))
        else:
            self.redirect(users.create_login_url("/"))
            
class API(webapp2.RequestHandler):
    def get(self, id):
        self.response.out.write(id)

routes= [
    ('/', MainHandler),
    webapp2.Route('/partners', handler='partners.Handler'),
    webapp2.Route('/partners/<id>', handler='partners.Handler'),
 #   webapp2.Route('/main', handler="main.Show")
    # webapp2.Route('/calendar', handler="assignments.Show"),
    # webapp2.Route('/volunteers', handler="volunteers.Show", name="volunteers"),
    # webapp2.Route('/volunteerForm', handler="volunteers.Form", name="volunteerForm"),
    # webapp2.Route('/volunteerEdit', handler="volunteers.Edit", name="volunteerEdit"),
    # webapp2.Route('/volunteerDelete', handler="volunteers.Delete", name="volunteerDelete"),
    # webapp2.Route('/partners', handler="partners.Show"),
     webapp2.Route('/partnerForm', handler="partners.Form"),
     webapp2.Route('/partnerEdit', handler="partners.Edit"),
    # webapp2.Route('/partnerDelete', handler="partners.Delete"),
    # webapp2.Route('/invoices', handler="invoices.Show"),
    # webapp2.Route('/invoiceForm', handler="invoices.Form"),
    # webapp2.Route('/invoiceView', handler="invoices.View"),
    # webapp2.Route('/invoiceJSON', handler="invoices.JSON"),
    # webapp2.Route('/invoiceSave', handler="invoices.Save"),
    # webapp2.Route('/invoiceDelete', handler="invoices.Delete"),
    # webapp2.Route('/projects', handler="projects.Show"),
    # webapp2.Route('/projectForm', handler="projects.Form"),
    # webapp2.Route('/projectEdit', handler="projects.Edit"),
    # webapp2.Route('/projectDelete', handler="projects.Delete"),
    # webapp2.Route('/siteForm', handler="sites.Form"),
    # webapp2.Route('/siteEdit', handler="sites.Edit"),
    # webapp2.Route('/siteDelete', handler="sites.Delete"),
    # webapp2.Route('/assignments', handler="assignments.Show"),
    # webapp2.Route('/assignmentForm', handler="assignments.Form"),
    # webapp2.Route('/assignmentEdit', handler="assignments.Edit"),
    # webapp2.Route('/assignmentDelete', handler="assignments.Delete"),
    # webapp2.Route('/ajaxAssignment', handler="assignments.ajaxAssignment"),
    # webapp2.Route('/ajaxComment', handler="assignments.ajaxComment"),
    # webapp2.Route('/dump', Dump),
    # ('/api/(.+)', API),#"api.Api"),
    # webapp2.Route('/pdf', handler="pdftest.PDF"),
    # webapp2.Route('/settings', handler="settings.Show"),
    # webapp2.Route('/settingsEdit', handler="settings.Edit")
    ]
                
app = webapp2.WSGIApplication( routes,  config = { "ADD_PARTNER" : False },
                                 debug=True)
#    util.run_wsgi_app(app)

#if __name__=="__main__":
#    main()
    


