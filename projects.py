
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import dbmodels
import os
import datetime
from utilities import *
from google.appengine.ext.webapp import template

class Show(webapp.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "projects.html"
        v.pageinfo.title = "Projects"
        v.projects = dbmodels.Project.all()
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Form(webapp.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "projectForm.html"
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
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp.RequestHandler):
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

class Delete(webapp.RequestHandler):
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
