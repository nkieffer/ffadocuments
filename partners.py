#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import util
from google.appengine.ext import ndb
from google.appengine.api import memcache
import dbmodels
import os
import datetime
from utilities import *
import views
import json
import logging
from google.appengine.ext.webapp import template

import logging

class Show(webapp2.RequestHandler):
    def get(self):

        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.partners
        logging.info(views.partners)
        v.pageinfo.title = "Partners"
        app = webapp2.get_app()
        added = app.registry.get('ADD_PARTNER')
        v.partners = dbmodels.Partner.all()#get_all(added)
        app.registry['ADD_PARTNER'] = False
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Form(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.partnerForm
        v.pageinfo.title = "Partner Form"
        key = self.request.get('key')
        if key == '':
            pass
        else:
            v.partner = dbmodels.Partner.get(key)
            v.partner.invoices.order("date")
            
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        if key == '':
            partner = dbmodels.Partner()
        else:
            partner = dbmodels.Partner.get(key)
        partner.name = self.request.get('name')
        partner.abbr = self.request.get('abbr')
        partner.address = self.request.get('address')
        partner.comment = self.request.get('comment')

        partner.put()
        webapp2.get_app().registry['ADD_PARTNER'] = True
        memcache.delete("partner:all")
        self.redirect('/partners')


class Delete(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        partner = dbmodels.Partner.get(key)
        db.delete(partner)
        self.redirect('/partners')

