import webapp2
import os
import logging
from utilities import *
import views
from google.appengine.ext.webapp import template

class Show(webapp2.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.home
        v.pageinfo.title = "Home"
        v.params = TemplateValues()
        path = os.path.join(os.path.dirname(__file__), views.main)
        logging.info
        self.response.out.write(template.render(path, { "v" : v }))
