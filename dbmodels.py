import datetime
from google.appengine.ext import db
from google.appengine.api import users


class Partner(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    comment = db.TextProperty()
    feed_uri = db.StringProperty()

class Volunteer(db.Model):
    fname = db.StringProperty()
    lname = db.StringProperty()
    country = db.StringProperty()
    DOB = db.DateTimeProperty()
    email = db.EmailProperty()
    partner = db.ReferenceProperty(reference_class=Partner)
    address = db.TextProperty()
    emergency = db.TextProperty()
    invoiced = db.BooleanProperty(default=False)
    comment = db.TextProperty() # not in calender
    status = db.TextProperty() # This is on calender and includes info about paperwork
    @property
    def name(self):
        return "%s, %s" % (self.lname, self.fname)
class Project(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    price = db.FloatProperty()
    sales_tax = db.FloatProperty(default=.075)
    comment = db.TextProperty()
    
class Site(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    project = db.ReferenceProperty(reference_class=Project)
    country = db.StringProperty()
    capacity = db.IntegerProperty()
    comment = db.TextProperty()

class Assignment(db.Model):
    volunteer = db.ReferenceProperty(reference_class=Volunteer)
    partner = db.ReferenceProperty(reference_class=Partner)
    project = db.ReferenceProperty(reference_class=Project)
    site = db.ReferenceProperty(reference_class=Site)
    start_date = db.DateTimeProperty()
    end_date = db.DateTimeProperty()
    #do something with this 
    booking_date = db.DateTimeProperty()
    discount = db.FloatProperty()
    invoiced = db.BooleanProperty(default=False)
    comment = db.TextProperty()
    @property
    def jsonAssignment(self):
        return { "volunteer" : "%s, %s" % (self.volunteer.lname, self.volunteer.fname),
                 "project" : self.project.name,
                 "site" : self.site.name,
                 "start_date" : self.start_date_str,
                 "end_date" : self.end_date_str,
                 "price" : float(self.project.price),
                 "discount" : float(self.discount),
                 "invoiced" : self.invoiced,
                 "key" : unicode(self.key())}
    @property
    def duration(self):
        return self.end_date - self.start_date
    @property
    def item_price(self):
        return self.project.price - self.discount
    @property
    def start_date_str(self):
        return self.start_date.strftime("%Y-%m-%d")# "%d-%d-%d" % (self.start_date.year, self.start_date.month, self.start_date.day)
    @property
    def end_date_str(self):
        return (self.end_date - datetime.timedelta(days=6)).strftime("%Y-%m-%d")#"%d-%d-%d" % (self.end_date.year, self.end_date.month, self.end_date.day - 1)
    @property
    def start_date_date(self):
        return self.start_date.date()
    @property
    def end_date_date(self):
        return self.end_date.date()

class Invoice(db.Model):
    partner = db.ReferenceProperty(reference_class=Partner)
    date = db.DateTimeProperty()
    akeys = db.ListProperty(db.Key)
    comment = db.TextProperty()

class Settings(db.Model):
    companyName = db.StringProperty()
    companyAddress = db.PostalAddressProperty()
    companyPhone1 = db.PhoneNumberProperty()
    companyPhone2 = db.PhoneNumberProperty()
    logo = db.BlobProperty()
    bankName = db.StringProperty()
    bankAcctNum = db.StringProperty()
    email = db.EmailProperty()

