
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
        v.pageinfo.html = views.projects
        v.pageinfo.title = "Projects"
        v.projects = dbmodels.Project.all()
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Form(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.projectForm
        v.pageinfo.title = "Project Form"
        key = self.request.get('key')
        if key == '':
            pass
        else:
            v.project = dbmodels.Project.get(key)
            query = db.GqlQuery("SELECT * FROM Site WHERE project = :1", v.project.key())
            v.sites = query.fetch(50)
            v.sites.sort(key=lambda site: site.country)
            v.sites.sort(key=lambda site: site.name)
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        if key == '':
            project = dbmodels.Project()
        else:
            project = dbmodels.Project.get(key)
        project.name = self.request.get('name')
        project.abbr = self.request.get('abbr')
        project.price = float(self.request.get('price'))
        project.additionalWeekPrice = float(self.request.get('additionalWeekPrice'))
        project.comment = self.request.get('comment')
        project.put()
        self.redirect('/projects')

class Delete(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        project = dbmodels.Project.get(key)
        sites = dbmodels.Site.all()
        sites.filter("project =",project)
            #        for s in sites:
#self.response.out.write(s.name)
        db.delete(sites)
        db.delete(project)
        self.redirect('/projects')
