
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import dbmodels
import os
import datetime
from utilities import *
import views
from google.appengine.ext.webapp import template
import logging

class Show(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.volunteers
        v.pageinfo.title = "Volunteers"
#        v.volunteers = dbmodels.Volunteer.all()
#        v.volunteers.order('partner').order('lname')
        v.key = self.request.get('key')
        view = self.request.get('view')
        if v.key:
            v.partner = dbmodels.Partner.get(v.key)
#            logging.info(partner.volunteers)
            if view == 'all':
                v.volunteers = v.partner.volunteers#.filter("partner =", partner)
            else:
                v.volunteers = v.partner.active_volunteers
            v.pageinfo.title = "Volunteers - %s" % v.partner.name
        else:
            v.volunteers = dbmodels.Volunteer.all()
            v.pageinfo.title = "All Volunteers"
            if view == 'active':
#                v.volunteers.filter('active_assignments >', 0)
                v.volunteers = [i for i in v.volunteers if i.active_assignments > 0]
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.out.write( template.render(path, { "v" : v }))

class Form(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.volunteerForm
        v.pageinfo.title = "Volunteer Form"
        key = self.request.get('key')
        if key == '':
            pass
        else:
            v.volunteer = dbmodels.Volunteer.get(key)
            v.assignments = dbmodels.Assignment.all()
            v.assignments.filter("volunteer =", v.volunteer.key()).order("start_date")
            v.total_price = 0.0
            for a in v.assignments:
                v.total_price += a.total_price
        v.partners = dbmodels.Partner.all()
        
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        if key == '':
            volunteer = dbmodels.Volunteer()
        else:
            volunteer = dbmodels.Volunteer.get(key)
        volunteer.fname = self.request.get('fname')
        volunteer.lname = self.request.get('lname')
        volunteer.country = self.request.get('country')
        volunteer.DOB = datetime.datetime(int(self.request.get('year')), int(self.request.get('month')), int(self.request.get('day')))
        volunteer.partner = dbmodels.Partner.get(self.request.get('partner'))
        volunteer.email = self.request.get('email') or None
        volunteer.address = self.request.get('address')
        volunteer.emergency = self.request.get('emergency')
        volunteer.comment = self.request.get('comment')
        volunteer.put()
        if key == "":
            self.redirect('/assignmentForm?vkey='+unicode(volunteer.key()))
        else:
            self.redirect('/volunteers')
