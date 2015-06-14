import webapp2
from google.appengine.ext import db
import dbmodels
import os
from utilities import *
import views
import logging
from google.appengine.ext.webapp import template

import logging

class Show(webapp2.RequestHandler):
    def get(self):

        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.settings

        v.pageinfo.title = "Settings"
        v.saved = self.request.get('saved') == '1'
        v.calendar = dbmodels.Calendar.get_by_key_name("main")
        v.settings = db.get(db.Key.from_path('Settings', 'main'))
        
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        logging.info(template.render( "views/"+views.settings, {}))
        self.response.out.write(template.render(path, { "v" : v }))


class Edit(webapp2.RequestHandler):
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
        settings.bankAddress = request.get('bankAddress')
        settings.bankAcctName = request.get('bankAcctName')
        settings.bankAcctNum = request.get('bankAcctNum')
        settings.routingNumber = request.get('routing_number')
        settings.swiftCode = request.get('swift_code')
        logging.info(settings.bankAcctNum)
        settings.email = request.get('email')
        settings.sdin = request.get('sdin')
        settings.sales_tax = float(request.get('sales_tax'))
        settings.num_months = int(request.get('num_months'))
        settings.put()
        self.redirect('/settings?saved=1')
