from google.appengine.ext import db
import calendar
import datetime
from dbmodels import Assignment, Site
import logging
import webapp2

class Run(webapp2.RequestHandler):
    def get(self):
        num_months = 3

        now = datetime.datetime.now()

        assignment_query = Assignment.get_all()
        assignment_query.order("end_date")
        logging.info("it worked")

