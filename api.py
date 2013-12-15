from google.appengine.ext import webapp
import dbmodels
class Api(webapp.RequestHandler):
    def get(self, *args):
        for i in dir(self.request):
            break
            print i, ":  ",
            try:
                exec("print self.request.%s()" % i)
            except:
                exec("print self.request.%s" % i)

        parts = self.request.path.split("/")[2:]
        print parts
        print dir(dbmodels)
            

