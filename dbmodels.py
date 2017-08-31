import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.datastore import entity_pb
from google.appengine.api import users
from google.appengine.api import memcache
import logging
import webapp2

class Calendar(db.Model):
    data = db.BlobProperty()
    timestamp = db.DateTimeProperty()
    manual = db.BooleanProperty()

class Cache(db.Model):
    data = db.BlobProperty()
    timestamp = db.DateTimeProperty()
    manual = db.BooleanProperty()

class Partner(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    comment = db.TextProperty()
    address = db.TextProperty()
    feed_uri = db.StringProperty()
    
    @property
    def activeVolunteers(self):
        cacheKey = "partner:volunteer:active:%s" % self.key()
        activeVolunteers = memcache.get(cacheKey)
        if activeVolunteers is None:
            logging.info("creating cache: "  + cacheKey)
            activeVolunteers = [v for v in self.volunteers if v.active_assignments > 0]
            memcache.add(cacheKey, activeVolunteers)
        else:
            logging.info("using cache: " + cacheKey)
        return activeVolunteers

    @property
    def allVolunteers(self):
        cacheKey = "partner:volunteer:all:%s" % self.key()
        allVolunteers = memcache.get(cacheKey)
        if allVolunteers is None:
            logging.info("creating cache: "  + cacheKey)
            allVolunteers = [a for a in self.volunteers.order("lname")]
            memcache.add(cacheKey, allVolunteers)
        else:
            logging.info("using cache: " + cacheKey)
        return allVolunteers
    
    @classmethod
    def get_all(cls, added):
        cacheKey = "partner:all"
        logging.info("Added = " + str(added))
        allPartners = memcache.get(cacheKey)
        if allPartners is None or added:
            logging.info("creating cache: "  + cacheKey)
            allPartners = cls.all()
            memcache.add(cacheKey, allPartners)
        return allPartners

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

    @classmethod
    def get_all(cls):
        cacheKey = "volunteer:all"
        allInstances = memcache.get(cacheKey)
        if allInstances is None:
            logging.info("creating cache: " + cacheKey)
            allInstances = cls.all().order('lname')
            allInstances = [a for a in allInstances]
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances

    @classmethod
    def get_active(cls):
        cacheKey = "volunteer:active"
        allInstances = memcache.get(cacheKey)
        if allInstances is None:
            logging.info("creating cache: " + cacheKey)
            allInstances = cls.all()
            allInstances = [a for a in allInstances if a.active_assignments > 0]
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances

    @classmethod
    def get_for_partner(cls, partnerkey):
        cacheKey = "volunteers_for_partner:%s" % partnerkey
        allInstances = memcache.get(cacheKey)
        if allInstances is None:
            logging.info("creating cache: " + cacheKey)
            allInstances = cls.all()
            allInstances.filter("partner =", partnerkey)
            allInstances = [a for a in allInstances]
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances
        
    @property
    def name(self):
        return "%s, %s" % (self.lname, self.fname)

    @property
    def active_assignments(self):
         return self.assignments.filter("end_date >=", datetime.datetime.now()).count()

    @property
    def num_assignments(self):
        return self.assignments.count()
    
    @property
    def json(self):
        pass

class NewVolunteer(db.Model):
    volunteer = db.ReferenceProperty(reference_class=Volunteer)

       
class Project(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    price = db.FloatProperty()
    additionalWeekPrice = db.FloatProperty()
    minimum_duration = db.IntegerProperty()
    sales_tax = db.FloatProperty(default=.075)
    comment = db.TextProperty()

    @classmethod
    def get_all(cls):
        cacheKey = "project:all"
        allInstances = memcache.get(cacheKey)
        if allInstances is None:
            logging.info("creating cache: "  + cacheKey)
            allInstances = [a for a in cls.all()]
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances
    
class Site(db.Model):
    name = db.StringProperty()
    abbr = db.StringProperty()
    project = db.ReferenceProperty(reference_class=Project, collection_name="sites")
    country = db.StringProperty()
    capacity = db.IntegerProperty()
    comment = db.TextProperty()
    @classmethod
    def get_all(cls):
        cacheKey = "site:all"
        allInstances = memcache.get(cacheKey)
        if allInstances is None:
            logging.info("creating cache: "  + cacheKey)
            allInstances = [a for a in cls.all()]
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances

class Assignment(db.Model):
    volunteer = db.ReferenceProperty(reference_class=Volunteer, collection_name="assignments")

    partner = db.ReferenceProperty(reference_class=Partner, collection_name="assignments")
    project = db.ReferenceProperty(reference_class=Project, collection_name='assignments')
    project_name = db.StringProperty(default=None)
    partner_name = db.StringProperty(default=None)
    volunteer_name = db.StringProperty(default=None)

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
    expired = db.BooleanProperty(default=False)
    
    def __str__(self):
        return "{} {} {} {} {} {}<br>".format(self.project_name, self.volunteer_name, self.partner_name, self.partner_name, str(self.start_date), str(self.end_date))
    @classmethod
    def get_all(cls):
        cacheKey = "assignment:all"
        allInstances = memcache.get(cacheKey)
        if allInstances is None:
            logging.info("creating cache: "  + cacheKey)
            allInstances = cls.all()
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances
    
    @classmethod
    def get_all_for_volunteer(cls, vkey):
        cacheKey = "assignment:volunteer:%s" % vkey
        allInstances = memcache.get(cacheKey)
        if allInstances is None:
            logging.info("creating cache: "  + cacheKey)
            allInstances = cls.all().filter("volunteer =", vkey).order("start_date")
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances

    @property
    def projectName(self):
        return self.project.name
    @property
    def jsonAssignment(self):
        duration = self.duration.days / 7.0
        return { "volunteer" : "%s, %s" % (self.volunteer.lname, self.volunteer.fname),
                 "project" : self.project.name,
                 "minimum_duration" : self.project.minimum_duration,
      #           "site" : self.site.name,
                 "start_date" : self.start_date_str,
                 "end_date" : self.end_date_str,
                 "num_weeks" : (self.end_date - self.start_date).days / 7.0,
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
        try:
#        return (self.end_date - datetime.timedelta(days=6)).strftime("%Y-%m-%d")#"%d-%d-%d" % (self.end_date.year, self.end_date.month, self.end_date.day - 1)
            return (self.start_date + datetime.timedelta(weeks=self.num_weeks-1)).strftime("%Y-%m-%d")#"%d-%d-%d" % (self.end_date.year, self.end_date.month, self.end_date.day - 1)
        except TypeError:
            return ""
    @property
    def start_date_date(self):
        return self.start_date.date()
    @property
    def end_date_date(self):
        return self.end_date.date()


class NewAssignment(db.Model):
    assignment = db.ReferenceProperty(reference_class=Assignment)
    assignment_id = db.StringProperty() #used to match for deleting

class Invoice(db.Model):
    partner = db.ReferenceProperty(reference_class=Partner, collection_name="invoices")
    date = db.DateTimeProperty()
    akeys = db.ListProperty(db.Key)
    comment = db.TextProperty()
    discount = db.FloatProperty()
    fees = db.FloatProperty()
    @classmethod
    def get_all(cls):
        allInstances = memcache.get("invoice:all")
        if allInstances is None:
            logging.info("creating cache: "  + cacheKey)
            allInstances = cls.all()
            memcache.add("invoice:all", allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances

class Settings(db.Model):
    companyName = db.StringProperty()
    companyAddress = db.PostalAddressProperty()
    companyPhone1 = db.PhoneNumberProperty()
    companyPhone2 = db.PhoneNumberProperty()
    logo = db.BlobProperty()
    bankName = db.StringProperty()
    bankAddress = db.PostalAddressProperty()
    bankAcctName = db.StringProperty()
    bankAcctNum = db.StringProperty()
    routingNumber = db.StringProperty()
    swiftCode = db.StringProperty()
    email = db.EmailProperty()
    sdin = db.StringProperty()
    sales_tax = db.FloatProperty(default=0.0)
    num_months = db.IntegerProperty(default=6)
    @classmethod
    def get_all(cls):
        cacheKey = "settings:all"
        allInstances = memcache.get(cacheKey)
        logging.info("******")
        logging.info(allInstances)
        if allInstances is None:
            logging.info("creating cache: "  + cacheKey)
            allInstances = cls.all()[0]
            memcache.add(cacheKey, allInstances)
        else:
            logging.info("using cache: " + cacheKey)
        return allInstances

class Archive(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    year = ndb.IntegerProperty()
    data = ndb.JsonProperty()
    
