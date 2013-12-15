import sys
import reportlab
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate , SimpleDocTemplate , KeepTogether
from reportlab.lib.units import mm, inch
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors 
from reportlab.pdfgen import canvas

styles=getSampleStyleSheet()
import json
import datetime

from google.appengine.ext import webapp
from google.appengine.ext import db
from StringIO import StringIO
import dbmodels

WIDTH, HEIGHT = defaultPageSize
MARGIN_LEFT = 50
MARGIN_TOP = 75
MARGIN_RIGHT = WIDTH - MARGIN_LEFT
NORMAL = "Helvetica"
BOLD = "Helvetica-Bold"
OBLIQUE = "Helvetica-Oblique"

class Numberer(object):
    def __init__(self, start=0, increment=1, end=None):
        self.start = start
        self.increment = increment
        self.end = end
        self.current = start
    def __call__(self, mod=0):
        next = self.current + self.increment + mod
        if self.end and (next > self.end):
            self.current = self.start
            next = self.start
        else:
            self.current = next
        return next
        
def firstPage(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

def laterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d / %s" % (doc.page, "This is info"))
    canvas.restoreState()
    


class PDF(webapp.RequestHandler):
    def get(self):
        print "asdfasdfasdf"
        invoice = dbmodels.Invoice.get(self.request.get("ikey"))
        assignments = dbmodels.Assignment.get([str(key) for key in invoice.akeys])
        settings = dbmodels.Settings.get(db.Key.from_path("Settings", "main"))
        timestamp = datetime.datetime.now()
        self.response.headers.add_header("Content-type", "application/pdf")
        self.response.headers.add_header("Content-disposition", 'attachment; filename=%s-%s.pdf' % (str(invoice.partner.name), timestamp.strftime("%Y-%m-%d")))

        doc = SimpleDocTemplate(self.response.out)
        doc.timestamp = timestamp
        Story = []
        style = styles["Normal"]
        style.spaceAfter = inch * 0.5
        style.leftIndent = -inch * 0.5
        address = Paragraph("""
<font size='24' face='Helvetica-Bold' color='red'>%s</font><br/>
%s
<br/>
%s
<br/>
<font face='Helvetica-Bold'>SDIN#: 26-2762978</font>""" % (settings.companyName, settings.companyAddress.replace("\n","<br/>"), settings.email), style)
        Story.append(address)

        Story.append(Paragraph("<font face='Helvetica-Bold'>Invoice Date:</font> %s <br/><font face='Helvetica-Bold'>Invoice Number:</font> %d" % (timestamp.strftime("%Y-%m-%d"), 1245), style))

        tableData = []
        tableData.append(["Volunteer","Start Date", "End Date", "Price", "Discount", "Item Total"])
        subTotal = 0
        for a in assignments:
            a = a.jsonAssignment
            itemSub = a["price"] - a["discount"]
            assignmentData = [a["volunteer"], a["start_date"], a["end_date"], "$%.2f" % a["price"], "$%.2f" % a["discount"], "$%.2f" % itemSub]
            tableData.append(assignmentData)
            subTotal += itemSub
        salesTax = subTotal * 0.07
        total = subTotal + salesTax
        tableData.append(["","","","","Sub-Total:", "$%.2f" % subTotal])
        tableData.append(["","","","","Sales Tax:", "$%.2f" % salesTax])
        tableData.append(["","","","","Total:", "$%.2f" % total])
        
        tableStyle = TableStyle(
            [('ALIGN', (3,0),(5,-1), 'RIGHT'),
             ('LINEBELOW',(0,0),(-1,0), 2, colors.black),
             ('LINEBELOW',(0,-4),(-1,-4), 2, colors.black),
             ('FACE', (4,-3),(4,-1), 'Helvetica-Bold'),
             ('FACE', (0,0),(-1,0), 'Helvetica-Bold'),
             ('SIZE', (1,1),(-1,-1), 8)])
            

        table = Table(tableData, colWidths=[2*inch, inch, inch, inch, inch, inch], style=tableStyle)
        Story.append(table)
        bankInfo = Paragraph("%s Acct #: %s" % (settings.bankName, settings.bankAcctNum), style)
        Story.append(bankInfo)
        doc.build(Story, onFirstPage=firstPage, onLaterPages=laterPages)
 
        
        
        
