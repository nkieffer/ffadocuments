from google.appengine.ext import webapp
import webapp2
import dbmodels

class Api(webapp2.RequestHandler):
    def get(self, arg):
        self.response.write(arg)
            

