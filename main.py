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
import dbmodels
import volunteers, partners, projects, sites, assignments, api, pdftest, settings
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

class MainHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect("/calendar")
        else:
            self.redirect(users.create_login_url("/"))

class Dump(webapp.RequestHandler):
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


                
app = webapp.WSGIApplication([('/', MainHandler),
                              ('/calendar', assignments.Show),
                              ('/volunteers', volunteers.Show),
                              ('/volunteerForm', volunteers.Form),
                              ('/volunteerEdit', volunteers.Edit),
                              ('/partners', partners.Show),
                              ('/partnerForm', partners.Form),
                              ('/partnerEdit', partners.Edit),
                              ('/partnerDelete', partners.Delete),
                              ('/invoiceForm', partners.Invoice),
                              ('/invoice', partners.Invoice),
                              ('/invoicet', partners.Invoicet),
                              ('/invoiceCreate', partners.InvoiceCreate),
                              ('/invoiceConfirm',partners.InvoiceConfirm),
                              ('/invoiceDelete', partners.InvoiceDelete),
                              ('/invoiceViewAll', partners.InvoiceViewAll),
                              ('/projects', projects.Show),
                              ('/projectForm', projects.Form),
                              ('/projectEdit', projects.Edit),
                              ('/projectDelete', projects.Delete),
                              ('/siteForm', sites.Form),
                              ('/siteEdit', sites.Edit),
                              ('/siteDelete', sites.Delete),
                              ('/assignments', assignments.Show),
                              ('/assignmentForm', assignments.Form),
                              ('/assignmentEdit', assignments.Edit),
                              ('/assignmentDelete', assignments.Delete),
                              ('/ajaxAssignment', assignments.ajaxAssignment),
                              ('/ajaxComment', assignments.ajaxComment),
                              ('/dump', Dump),
                              ('/api/(.*)', api.Api),
                              ('/pdf', pdftest.PDF),
                              ('/settings', settings.Show),
                              ('/settingsEdit', settings.Edit)
                              ],
                                 debug=True)
#    util.run_wsgi_app(app)

#if __name__=="__main__":
#    main()
    


