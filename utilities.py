import datetime
from google.appengine.api import users
import logging

class TemplateValues(object):
    def __init__(self):
        self.user = users.get_current_user()
        self.logout_url = users.create_logout_url("/")
        self.login_url = users.create_login_url("/")
def expdate():
    delta = datetime.timedelta(days=7)
    expdate = datetime.datetime.now()+delta
    return expdate.ctime()

def session():
    user = users.get_current_user()
    logout_url = users.create_logout_url("/")
    login_url = users.create_login_url("/")
    return { "user" : user,
             "login_url" : login_url,
             "logout_url" : logout_url}


def strtodt(date_str):
    d = date_str.split("-")
    return datetime.datetime(*[int(x) for x in d])

def log(fn, *args, **kwargs):
    def decorated(*args, **kwargs):    
        logging.info("Calling %s.%s"%(fn.__module__,fn.__name__))
        fn(*args, **kwargs)
    return decorated
    