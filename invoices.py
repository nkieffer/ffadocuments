#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import dbmodels
import os
import datetime
from utilities import *
import views
import json
import logging
from google.appengine.ext.webapp import template

import logging

class Show(webapp2.RequestHandler):
    def get(self):
        logging.info("invoices.Show.get")
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.invoices
        v.pageinfo.title = "Invoices"
        v.invoices = dbmodels.Invoice.all()
        v.invoices.order("partner").order("date")
        v.invoices = v.invoices.fetch(1000)
        v.saved = self.request.get('saved') == 'true'
        path = os.path.join(os.path.dirname(__file__), views.main)
        logging.info(path)
        for i in v.invoices:
            logging.info(i.key())
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path,{"v":v}))

class Form(webapp2.RequestHandler):
    def get(self):
        """
        This just loads the page. The content is retrieved with an ajax request from in invoice.js
        """
        logging.info("invoices.Form.get")
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = views.invoiceForm
        ikey = self.request.get('ikey')
        if ikey:
            v.invoice = dbmodels.Invoice.get(ikey)
            v.partner = v.invoice.partner
            v.pageinfo.title = "Invoice for %s %s" % (v.invoice.partner.name, v.invoice.date.date())
            logging.info( ikey)
        else:
            logging.info("no ikey")
            key = self.request.get('key')
            v.partner = dbmodels.Partner.get(key)
            v.pageinfo.title = "Invoice for %s" % v.partner.name
        path = os.path.join(os.path.dirname(__file__), views.main)
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class JSON(webapp2.RequestHandler):
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
        invoicekey = self.request.get('invoicekey')
        on_invoice = []
        if invoicekey:
            i = dbmodels.Invoice.get(invoicekey)
            on_invoice =  [str(k) for k in i.akeys]
        assignments = dbmodels.Assignment.all()
        
        if invoiced != "checked":
            assignments.filter("invoiced =", False)
        assignments.order("start_date").order("end_date")#.order("volunteer.lname")
        assignments.filter("partner =", p.key())
        if alldates != "checked":
            assignments.filter("start_date >=", strtodt(start_date))
            assignments = [a.jsonAssignment for a in assignments if a.end_date <= strtodt(end_date)]
        else:
            assignments = [a.jsonAssignment for a in assignments]
        assignments.sort(lambda a,b: cmp(a['volunteer'].lower(),b['volunteer'].lower()))
        logging.info(len(assignments))
        jsonResponse = {"assignments":assignments, "on_invoice": on_invoice }
        self.response.out.write(json.dumps(jsonResponse))
        
class Save(webapp2.RequestHandler):
    def post(self):
        akeys = map(lambda x: x[5:],filter( lambda x: x[0:5] == "akey:",self.request.params))#self.request.get("akeys").split(":")
        assignments = dbmodels.Assignment.get(akeys)
        invoicekey = self.request.get('invoicekey')
        if invoicekey:
            invoice = dbmodels.Invoice.get(invoicekey)
            logging.info("editting invoice")
        else:
            invoice = dbmodels.Invoice()
            logging.info("creating new invoice")

        invoice.partner = dbmodels.Partner.get(self.request.get('partnerkey'))
        invoice.date = datetime.datetime.now()
        keys = []
        for a in assignments:
            a.invoiced = True
            a.invoiceDate = datetime.datetime.now()
            keys.append(a.key())
            a.put()
        invoice.akeys = keys
        invoice.comment = self.request.get("comment")
        invoice.put()
        
        logging.info(invoice)
        self.redirect("/invoices?saved=true")


class Delete(webapp2.RequestHandler):
    def get(self):
        logging.info("invoices.Delete.get")
        ikey = self.request.get('ikey')
        invoice = dbmodels.Invoice.get(ikey)
        pkey = invoice.partner.key()
        invoice.delete()
        self.redirect("/partnerForm?key="+str(pkey))


