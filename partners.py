from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import dbmodels
import os
import datetime
from utilities import *

import json
import logging
import md5
from google.appengine.ext.webapp import template

import logging

class Show(webapp.RequestHandler):
    def get(self):

        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "partners.html"
        v.pageinfo.title = "Partners"
        v.partners = dbmodels.Partner.all()
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Form(webapp.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "partnerForm.html"
        v.pageinfo.title = "Partner Form"
        key = self.request.get('key')
        if key == '':
            pass
        else:
            v.partner = dbmodels.Partner.get(key)
            v.invoices = dbmodels.Invoice.all()
            v.invoices.filter("partner =", v.partner.key())
            v.invoices.order("date")
            
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

class Edit(webapp.RequestHandler):
    def post(self):
        key = self.request.get('key')
        if key == '':
            partner = dbmodels.Partner()
        else:
            partner = dbmodels.Partner.get(key)
        partner.name = self.request.get('name')
        partner.abbr = self.request.get('abbr')
        partner.comment = self.request.get('comment')
        partner.put()
        self.redirect('/partners')


class Delete(webapp.RequestHandler):
    def get(self):
        key = self.request.get('key')
        partner = dbmodels.Partner.get(key)
        db.delete(partner)
        self.redirect('/partners')

class Invoice(webapp.RequestHandler):
    def get(self):
        """
        This just loads the page. The content is retrieved with an ajax request from in assignments.js
        """
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = "invoiceForm.html"
        key = self.request.get('key')
        v.partner = dbmodels.Partner.get(key)
        v.pageinfo.title = "Invoice for %s" % v.partner.name
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path, { "v" : v }))

    def post(self):
        params = {"start_date": self.request.get('start_date'),
                "end_date" : self.request.get('end_date'),
                "partnerkey" : self.request.get('partnerkey'),
                "invoiced" : self.request.get('invoiced'),
                "alldates" : self.request.get('alldates')}
             
        start_date = self.request.get('start_date')
        end_date = self.request.get('end_date')
        partnerkey = self.request.get('partnerkey')
        invoiced = self.request.get('invoiced')
        alldates = self.request.get('alldates')


        assignments = dbmodels.Assignment.all()
        assignments.filter("partner = ", dbmodels.Partner.get(partnerkey))

        assignments.order("start_date")

        ass = []
        for a in assignments:
            a_dict = {}
            a_dict['name'] = "%s, %s" % (a.volunteer.lname, a.volunteer.fname)
            a_dict['project'] = a.project.name
            a_dict['site'] = a.site.name
            a_dict['start_date'] = a.start_date_str
            a_dict['end_date'] = a.end_date_str
            a_dict['duration'] = a.duration
            a_dict['price'] = a.project.price
            a_dict['discount'] = a.discount
            a_dict['invoiced'] = a.invoiced
            a_dict['res'] = a.start_date < datetime.datetime(*[int(x) for x in end_date.split("-")])
            ass.append(a_dict)
        params['assignments'] = ass
        self.response.out.write(json.dumps(params))

class Invoicet(webapp.RequestHandler):
    def get(self):
        options = {"start_date": self.request.get('start_date'),
                "end_date" : self.request.get('end_date'),
                "partnerkey" : self.request.get('partnerkey'),
                "invoiced" : self.request.get('invoiced'),
                "alldates" : self.request.get('alldates')}

        logging.info(options)
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
            assignments = [a.jsonAssignment for a in assignments if a.end_date <= strtodt(end_date)]
        else:
            assignments = [a.jsonAssignment for a in assignments]
        assignments.sort(lambda a,b: cmp(a['volunteer'].lower(),b['volunteer'].lower()))
        self.response.out.write(json.dumps(assignments))

class InvoiceCreate(webapp.RequestHandler):
    def post(self):
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
        path = os.path.join(os.path.dirname(__file__), 'invoice.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path,{"v":v}))
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.ikey = self.request.get('ikey')
        v.invoice = dbmodels.Invoice.get(v.ikey)
        v.assignments = dbmodels.Assignment.get(v.invoice.akeys)
        v.subtotal = sum([a.item_price for a in v.assignments])
        v.salestax = v.subtotal * .075
        v.total = "%.2f" % (v.subtotal + v.salestax)
        v.salestax = "%.2f" % v.salestax
        v.subtotal = "%.2f" % v.subtotal
        v.saved = True
        v.pageinfo.html = "invoice.html"
        path = os.path.join(os.path.dirname(__file__), 'invoice.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path,{"v":v}))
        
class InvoiceConfirm(webapp.RequestHandler):
    def get(self):
        akeys = self.request.get("akeys").split(":")
        assignments = dbmodels.Assignment.get(akeys)
        invoice = dbmodels.Invoice()

        invoice.partner = dbmodels.Partner.get(self.request.get('pkey'))
        invoice.date = datetime.datetime.now()
        keys = []
        for a in assignments:
            a.invoiced = True
            keys.append(a.key())
            a.put()
        invoice.akeys = keys# ["'%s'" % k for k in keys]
        invoice.put()
        logging.info(invoice)
        self.response.out.write(json.dumps(True))

class InvoiceDelete(webapp.RequestHandler):
    def get(self):
        ikey = self.request.get('ikey')
        invoice = dbmodels.Invoice.get(ikey)
        pkey = invoice.partner.key()
        #print pkey
        invoice.delete()
        self.redirect("/partnerForm?key="+str(pkey))

class InvoiceViewAll(webapp.RequestHandler):
    def get(self):
        v = TemplateValues()
        v.pageinfo = TemplateValues()
        v.pageinfo.html = 'invoiceList.html'
        v.pageinfo.title = "Invoices"
        v.invoices = dbmodels.Invoice.all()
        v.invoices.order("date").order("partner")
        path = os.path.join(os.path.dirname(__file__), 'main.html')
        self.response.headers.add_header("Expires", expdate())
        self.response.out.write(template.render(path,{"v":v}))
