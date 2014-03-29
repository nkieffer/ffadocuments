import reportlab
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors 
from reportlab.pdfgen import canvas
import datetime
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext import db
import dbmodels

WIDTH, HEIGHT = defaultPageSize
MARGIN_LEFT = 50
MARGIN_TOP = 75
MARGIN_RIGHT = WIDTH - MARGIN_LEFT
NORMAL = "Helvetica"
BOLD = "Helvetica-Bold"
OBLIQUE = "Helvetica-Oblique"
styles=getSampleStyleSheet()

def firstPage(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

def laterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d / %s" % (doc.page, "Friends for Asia"))
    canvas.restoreState()
    


class PDF(webapp2.RequestHandler):
    def get(self):
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
<font size='24' face='Helvetica-Bold'>%s</font><br/>
%s
<br/>
%s
<br/>
<font face='Helvetica-Bold'>SDIN#: %s</font>""" % (settings.companyName, settings.companyAddress.replace("\n","<br/>"), settings.email, settings.sdin), style)
        Story.append(address)
        
        partnerAddress = Paragraph("""
<font face='Helvetica-Bold'>%s</font><br/>
%s
""" % (invoice.partner.name, invoice.partner.address.replace("\n","<br/>")), style)

        Story.append(partnerAddress)
        Story.append(Paragraph("<font face='Helvetica-Bold'>Invoice Date:</font> %s <br/><font face='Helvetica-Bold'>Invoice Number:</font> %s" % (timestamp.strftime("%Y-%m-%d"), invoice.key().id()), style))

        tableData = []
        tableData.append(["Volunteer",
                          "Start Date", 
                          "End Date", 
#                          "Base Price", 
#                          "Add Weeks", 
#                          "Per Add Week",
#                          "Add Weeks Fee",
#                          "Discount", 
                          "","",
                          "Item Total"])
        subTotal = 0
        for a in assignments:
            a = a.jsonAssignment
            addWeeks = a["additionalWeeks"] * a["additionalWeekPrice"]                              
            itemSub = a["price"] + addWeeks #- a["discount"]
            assignmentData = [a["volunteer"], 
                              a["start_date"], 
                              a["end_date"],"","",
#                              "$%.2f" % a["price"], 
#                              "%d" % a["additionalWeeks"],
#                              "$%.2f" % a["additionalWeekPrice"],
#                              "$%.2f" % addWeeks,
#                              "$%.2f" % a["discount"], 
                              "$%.2f" % itemSub]
            tableData.append(assignmentData)
            subTotal += itemSub
        subTotal = subTotal + invoice.fees - invoice.discount
        salesTax = subTotal * settings.sales_tax
        total = subTotal + salesTax
        tableData.append(["","","","","Discount:", "-$%.2f" % invoice.discount])
        tableData.append(["","","","","Other Fees:", "$%.2f" % invoice.fees])
        tableData.append(["","","","","Sub-Total:", "$%.2f" % subTotal])
        tableData.append(["","","","","Sales Tax:", "$%.2f" % salesTax])
        tableData.append(["","","","","Total:", "$%.2f" % total])
        
        tableStyle = TableStyle(
            [('ALIGN', (-1,0),(-1,-1), 'RIGHT'),
             ('LINEBELOW',(0,0),(-1,0), 2, colors.black),
             ('LINEBELOW',(0,-6),(-1,-6), 2, colors.black),
#             ('ALIGN', (5,-1),(5,-1), 'RIGHT'),
             ('FACE', (4,-5),(4,-1), 'Helvetica-Bold'),
             ('FACE', (0,0),(-1,0), 'Helvetica-Bold'),
             ('SIZE', (0,0),(-1,-1), 8)])
            
        colWidths = [None, None, None,3.5*inch, None,None]
        table = Table(tableData, colWidths=colWidths, style=tableStyle)
        Story.append(table)
        comment = Paragraph("<b>Comments:</b><br/>%s"%invoice.comment, style)
        Story.append(comment)
        bankInfo = Paragraph("%s Acct #: %s" % (settings.bankName, settings.bankAcctNum), style)
        Story.append(bankInfo)
        
        doc.build(Story, onFirstPage=firstPage, onLaterPages=laterPages)
 
        
        
        
