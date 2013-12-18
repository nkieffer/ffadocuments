from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import dbmodels
import os
import datetime
from utilities import *

import json
import logging
from google.appengine.ext.webapp import template

import logging

class Show(webapp.RequestHandler):
    def get(self):
        logging.info("invoices.Show.get")
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = 'invoiceList.html'
        v.pageinfo.title = "Invoices"
        v.invoices = dbmodels.Invoice.all()
        v.invoices.order("date").order("partner")
        v.invoices = v.invoices.fetch(1000)
        logging.info(v.invoices)
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        logging.info(path)
        for i in v.invoices:
            logging.info(i.key())
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path,{"v":v}))

class Form(webapp.RequestHandler):
    def get(self):
        """
        This just loads the page. The content is retrieved with an ajax request from in invoice.js
        """
        logging.info("invoices.Form.get")
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "invoiceForm.html"
        key = self.request.get('key')
        v.partner = dbmodels.Partner.get(key)
        v.pageinfo.title = "Invoice for %s" % v.partner.name
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class JSON(webapp.RequestHandler):
    def get(self):
        options = {"start_date": self.request.get('start_date'),
                "end_date" : self.request.get('end_date'),
                "partnerkey" : self.request.get('partnerkey'),
                "invoiced" : self.request.get('invoiced'),
                "alldates" : self.request.get('alldates')}

        start_date = self.request.get('start_date')
        end_date = self.request.get('end_date')
        partnerkey = self.request.get('partnerkey')
        invoiced = self.request.get('invoiced')
        alldates = self.request.get('alldates')

        p = dbmodels.Partner.get(partnerkey)
        assignments = dbmodels.Assignment.all()
        if invoiced != "checked":
            assignments.filter("invoiced =", False)
        assignments.order("start_date").order("end_date")#.order("volunteer.lname")
        assignments.filter("partner =", p.key())
        if alldates != "checked":
            assignments.filter("start_date >=", strtodt(start_date))
            map(lambda a: logging.info(str(a.end_date)+" "+str(strtodt(end_date))), assignments)
            assignments = [a.jsonAssignment for a in assignments if a.end_date <= strtodt(end_date)]
        else:
            assignments = [a.jsonAssignment for a in assignments]
        assignments.sort(lambda a,b: cmp(a['volunteer'].lower(),b['volunteer'].lower()))
        self.response.out.write(json.dumps(assignments))

class View(webapp.RequestHandler):
    def post(self):
        logging.info("invoices.View.post")
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "invoice.html"
        pkey = self.request.get('partnerkey')
        #extract assignment keys from parameters
        
        akeys = map(lambda x: x[5:],filter( lambda x: x[0:5] == "akey:",self.request.params))
        v.assignments = dbmodels.Assignment.get(akeys)
        akeys = []
        for a in v.assignments:
            akeys.append(str(a.key()))
            a.put()
        v.akeys = ":".join(akeys)
        v.subtotal = sum([a.item_price for a in v.assignments])
        v.salestax = v.subtotal * .075
        v.total = "%.2f" % (v.subtotal + v.salestax)
        v.salestax = "%.2f" % v.salestax
        v.subtotal = "%.2f" % v.subtotal
        v.partner = dbmodels.Partner.get(pkey)
        v.pageinfo.title = "Invoice for %s" % v.partner.name
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path,{"v":v}))
 
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "invoice.html"
        v.ikey = self.request.get('ikey')
        v.invoice = dbmodels.Invoice.get(v.ikey)
        v.pageinfo.title = "Invoice for %s" % v.invoice.partner.name
        v.assignments = dbmodels.Assignment.get(v.invoice.akeys)
        v.subtotal = sum([a.item_price for a in v.assignments])
        v.salestax = v.subtotal * .075
        v.total = "%.2f" % (v.subtotal + v.salestax)
        v.salestax = "%.2f" % v.salestax
        v.subtotal = "%.2f" % v.subtotal
        v.saved = True
        v.pageinfo.html = "invoice.html"
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path,{"v":v}))
        
class Save(webapp.RequestHandler):
    def get(self):
        akeys = self.request.get("akeys").split(":")
        assignments = dbmodels.Assignment.get(akeys)
        invoice = dbmodels.Invoice()

        invoice.partner = dbmodels.Partner.get(self.request.get('pkey'))
        invoice.date = datetime.datetime.now()
        keys = []
        for a in assignments:
            a.invoiced = True
            a.invoiceDate = datetime.datetime.now()
            keys.append(a.key())
            a.put()
        invoice.akeys = keys
        invoice.put()
        logging.info(invoice)
        self.response.out.write(json.dumps(True))

class Delete(webapp.RequestHandler):
    def get(self):
        logging.info("invoices.Delete.get")
        ikey = self.request.get('ikey')
        invoice = dbmodels.Invoice.get(ikey)
        pkey = invoice.partner.key()
        invoice.delete()
        self.redirect("/partnerForm?key="+str(pkey))


