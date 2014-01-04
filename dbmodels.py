import datetime
from google.appengine.ext import db
from google.appengine.api import users
import logging

class Partner(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    comment = db.TextProperty()
    address = db.TextProperty()
    feed_uri = db.StringProperty()
    
    @property
    def active_volunteers(self):
        return [v for v in self.volunteers if v.active_assignments > 0]

class Volunteer(db.Model):
    fname = db.StringProperty()
    lname = db.StringProperty()
    country = db.StringProperty()
    DOB = db.DateTimeProperty()
    email = db.EmailProperty()
    partner = db.ReferenceProperty(reference_class=Partner, collection_name="volunteers")
    address = db.TextProperty()
    emergency = db.TextProperty()
    invoiced = db.BooleanProperty(default=False)
    comment = db.TextProperty() # not in calender
    status = db.TextProperty() # This is on calender and includes info about paperwork
    @property
    def name(self):
        return "%s, %s" % (self.lname, self.fname)

    @property
    def active_assignments(self):
         return self.assignments.filter("end_date >=", datetime.datetime.now()).count()
class Project(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    price = db.FloatProperty()
    additionalWeekPrice = db.FloatProperty()
    sales_tax = db.FloatProperty(default=.075)
    comment = db.TextProperty()
    
class Site(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    project = db.ReferenceProperty(reference_class=Project, collection_name="sites")
    country = db.StringProperty()
    capacity = db.IntegerProperty()
    comment = db.TextProperty()

class Assignment(db.Model):
    volunteer = db.ReferenceProperty(reference_class=Volunteer, collection_name="assignments")
    partner = db.ReferenceProperty(reference_class=Partner, collection_name="assignments")
    project = db.ReferenceProperty(reference_class=Project, collection_name='assignments')
    site = db.ReferenceProperty(reference_class=Site)
    start_date = db.DateTimeProperty()
    end_date = db.DateTimeProperty()
    num_weeks = db.IntegerProperty()
    #do something with this 
    booking_date = db.DateTimeProperty()
    invoiceDate = db.DateTimeProperty()
    discount = db.FloatProperty()
    invoiced = db.BooleanProperty(default=False)
    comment = db.TextProperty()
    @property
    def projectName(self):
        return self.project.name
    @property
    def jsonAssignment(self):
        duration = self.duration.days / 7.0
        return { "volunteer" : "%s, %s" % (self.volunteer.lname, self.volunteer.fname),
                 "project" : self.project.name,
                 "site" : self.site.name,
                 "start_date" : self.start_date_str,
                 "end_date" : self.end_date_str,
                 "duration" : duration,
                 "additionalWeeks" : duration - 2,
                 "price" : float(self.project.price),
                 "additionalWeekPrice" : self.project.additionalWeekPrice,
               #  "discount" : float(self.discount),
                 "invoiced" : self.invoiced,
                 "key" : unicode(self.key())}
    @property
    def duration(self):
        return self.end_date - self.start_date
    @property
    def additional_weeks(self):
        logging.info(str(self.num_weeks))
        return self.num_weeks - 2
    @property
    def additional_weeks_price(self):
        return self.project.additionalWeekPrice * self.additional_weeks
    @property
    def item_price(self):
        return self.project.price
    @property
    def total_price(self):
        return self.additional_weeks_price + self.item_price
    @property
    def start_date_str(self):
        return self.start_date.strftime("%Y-%m-%d")# "%d-%d-%d" % (self.start_date.year, self.start_date.month, self.start_date.day)
    @property
    def end_date_str(self):
#        return (self.end_date - datetime.timedelta(days=6)).strftime("%Y-%m-%d")#"%d-%d-%d" % (self.end_date.year, self.end_date.month, self.end_date.day - 1)
        return (self.end_date).strftime("%Y-%m-%d")#"%d-%d-%d" % (self.end_date.year, self.end_date.month, self.end_date.day - 1)
    @property
    def start_date_date(self):
        return self.start_date.date()
    @property
    def end_date_date(self):
        return self.end_date.date()

class Invoice(db.Model):
    partner = db.ReferenceProperty(reference_class=Partner, collection_name="invoices")
    date = db.DateTimeProperty()
    akeys = db.ListProperty(db.Key)
    comment = db.TextProperty()
    discount = db.FloatProperty()
    fees = db.FloatProperty()

class Settings(db.Model):
    companyName = db.StringProperty()
    companyAddress = db.PostalAddressProperty()
    companyPhone1 = db.PhoneNumberProperty()
    companyPhone2 = db.PhoneNumberProperty()
    logo = db.BlobProperty()
    bankName = db.StringProperty()
    bankAcctNum = db.StringProperty()
    email = db.EmailProperty()
    sdin = db.StringProperty()
