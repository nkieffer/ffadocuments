
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import memcache
import dbmodels
import os
import datetime
from utilities import *
import views
from google.appengine.ext.webapp import template
import logging
import pickle
import json


class CreateCache(webapp2.RequestHandler):
    def get(self):
        query = dbmodels.Volunteer.all()
        query.order('lname').order('fname')
        volunteers = query.fetch(1000)
        db.delete(NewVolunteer.all(keys_only=True))
        for v in volunteers:
            v.partner_name = v.partner.name
            v.all_assignments = [ a.project_name for a in v.assignments ]
        cache = dbmodels.Cache.get_or_insert('volunteers', title="Volunteer Cache")
        cache.data = pickle.dumps(volunteers)
        cache.timestamp = datetime.datetime.now()
        cache.manual = False
        cache.put()

class RetrieveCache(webapp2.RequestHandler):
    def get(self):
        cache = dbmodels.Cache.get_by_key_name('volunteers')
        data = [
            [ v.lname, v.fname, v.country, v.email, v.partner.name, str(v.key()) ] for
            v in pickle.loads(cache.data) ]
        new_volunteers = [v.volunteer for v in dbmodels.NewVolunteer.all()]
        [ data.append([v.lname, v.fname, v.country, v.email, v.partner.name, str(v.key())]) for v in new_volunteers]
        self.response.out.write(json.dumps(data))

class ShowNew(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "volunteersNew.html"#views.volunteers
        v.pageinfo.title = "Volunteers"
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.out.write( template.render(path, { "v" : v }))

class Show(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.volunteers
        v.pageinfo.title = "Volunteers"
        v.key = self.request.get('key')
        view = self.request.get('view')
        if v.key:
            v.partner = dbmodels.Partner.get(v.key)
            if view == 'all':
                v.volunteers = v.partner.allVolunteers
            else:
                v.volunteers = v.partner.activeVolunteers
            v.pageinfo.title = "Volunteers - %s" % v.partner.name
        else:
            v.pageinfo.title = "All Volunteers"
            if view != 'active':
                v.volunteers = dbmodels.Volunteer.get_all()
            else:
                v.volunteers = dbmodels.Volunteer.get_active()
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.out.write( template.render(path, { "v" : v }))
        
class Form(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.volunteerForm
        v.pageinfo.title = "Volunteer Form"
        key = self.request.get('key')
        try:
            v.partnerkey = db.Key(self.request.get('pkey'))
        except db.BadKeyError:
            pass
        if key == '':
            pass
        else:
            v.volunteer = dbmodels.Volunteer.get(key)
            v.assignments = dbmodels.Assignment.get_all_for_volunteer(v.volunteer.key())
            v.assignments.filter("volunteer =", v.volunteer.key()).order("start_date")
            v.total_price = 0.0
            for a in v.assignments:
                v.total_price += a.total_price
        v.partners = dbmodels.Partner.get_all(False)
        
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        if key == '':
            volunteer = dbmodels.Volunteer()
            new_volunteer = True
        else:
            volunteer = dbmodels.Volunteer.get(key)
            new_volunteer = False
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
        if new_volunteer:
            nv = dbmodels.NewVolunteer()
            nv.volunteer = volunteer
            nv.put()
        memcache.delete("volunteer:all")
        memcache.delete("volunteer:all:%s" % volunteer.partner.key())
        memcache.delete("partner:volunteer:active:%s" % volunteer.partner.key())
        memcache.delete("partner:volunteer:all:%s" % volunteer.partner.key())
        memcache.delete("volunteer:delete")
        memcache.delete("volunteer:active")
        logging.info("cleared the cache")
        if key == "":
            self.redirect('/assignmentForm?vkey='+unicode(volunteer.key()))
        else:
            self.redirect('/volunteers')

class Delete(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        volunteer = dbmodels.Volunteer.get(key)
        memcache.delete("volunteer:all")
        memcache.delete("volunteer:all:%s" % volunteer.partner.key())
        memcache.delete("partner:volunteer:active:%s" % volunteer.partner.key())
        memcache.delete("partner:volunteer:all:%s" % volunteer.partner.key())
        memcache.delete("volunteer:delete")
        memcache.delete("volunteer:active")
        logging.info("cleared the cache")

        db.delete(volunteer.assignments)
        db.delete(volunteer)
        self.redirect('/volunteers')
