
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

class Show(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "sites.html"
        v.pageinfo.title = "Sites"
        v.sites = dbmodels.Site.get_all()
        path = os.path.join(os.path.dirname(__file__), 'sites.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Form(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.siteForm
        skey = self.request.get('skey')
        pkey = self.request.get('pkey')
        if skey == '':
            v.pkey = pkey
            v.project = dbmodels.Project.get(pkey)  
            v.pageinfo.title = "Site: %s" % (v.project.name)
        else:
            v.site = dbmodels.Site.get(skey)
            v.project = dbmodels.Project.get(pkey)
            v.pkey = pkey
            v.pageinfo.title = "Site: %s %s" % (v.project.name, v.site.name)

        path = os.path.join(os.path.dirname(__file__), views.main)
       # self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp2.RequestHandler):
    def post(self):
        skey = self.request.get('skey')
        pkey = self.request.get('pkey')
        if skey == '':
            site = dbmodels.Site()
        else:
            site = dbmodels.Site.get(skey)
        site.name = self.request.get('name')
        site.abbr = self.request.get('abbr')
        site.country = self.request.get('country')
        site.project = dbmodels.Project.get(pkey)
        site.capacity = int(self.request.get('capacity'))
        site.comment = self.request.get('comment')
        site.put()
        self.redirect('/projectForm?key=' + pkey)

class Delete(webapp2.RequestHandler):
    def get(self):
        skey = self.request.get('skey')
        pkey = self.request.get('pkey')
        site = dbmodels.Site.get(skey)
        db.delete(site)
        self.redirect('/projectForm?key=' + pkey)
