from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import dbmodels
import os
import datetime
from utilities import *

import json
import logging
import md5
from google.appengine.ext.webapp import template

import logging

class Show(webapp.RequestHandler):
    def get(self):

        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "settings.html"

        v.pageinfo.title = "Settings"
        logging.info("A")
        v.settings = db.get(db.Key.from_path('Settings', 'main'))
        logging.info("B")
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))


class Edit(webapp.RequestHandler):
    def post(self):
        request = self.request
        
        settings = dbmodels.Settings.get(db.Key.from_path("Settings", "main"))
        logging.info(settings)
        logging.info(type(request.get('companyName')))
        if not settings:
            settings = dbmodels.Settings(key_name="main")

        settings.companyName = request.get(u'companyName')
        settings.companyAddress = request.get('companyAddress')
        settings.companyPhone1 = request.get('companyPhone1')
        settings.companyPhone2 = request.get('companyPhone2')
        settings.bankName = request.get('bankName')
        settings.bankAcctNum = request.get('bankAcctNum')
        logging.info(settings.bankAcctNum)
        settings.email = request.get('email')
        settings.put()
        self.redirect('/settings')
