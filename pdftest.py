import reportlab
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors 
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
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
      #  assignments = sorted(assignments, key=lambda assignment: assignment.start_date)
        settings = dbmodels.Settings.get(db.Key.from_path("Settings", "main"))
        timestamp = datetime.datetime.now()
        self.response.headers.add_header("Content-type", "application/pdf")
        self.response.headers.add_header("Content-disposition", 'attachment; filename=%s-%s.pdf' % (str(invoice.partner.name), timestamp.strftime("%Y-%m-%d")))

        doc = SimpleDocTemplate(self.response.out, leftMargin=inch*.5)
        doc.timestamp = timestamp
        Story = []
        style = styles["Normal"]
        style.spaceAfter = inch * 0.5
     #   style.leftIndent = -inch #* 0.5
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
                          "Project", 
                          "Start Date", 
                          "# Weeks", 
                          
                          "",#"",
                          "Item Total"])
        subTotal = 0
        for i, a in enumerate(assignments):
            a = a.jsonAssignment
            prev = assignments[i-1].jsonAssignment
            addWeeks = a["additionalWeeks"] * a["additionalWeekPrice"]
            if i > 0 and a['volunteer'] == assignments[i-1].jsonAssignment['volunteer']:
                itemSub = a['additionalWeekPrice'] * a['minimum_duration'] + addWeeks
                a['volunteer'] = '"'
            else:
            
                itemSub = a["price"] + addWeeks #- a["discount"]
            assignmentData = [a["volunteer"], 
                              a["project"],
                              a["start_date"], 
                              int(a["num_weeks"]),
                            #  "",
                              "",
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
            
        colWidths = [2*inch, 2*inch, None, None,None, None]
        table = Table(tableData, colWidths=colWidths, style=tableStyle)
        table.hAlign = "LEFT"
        Story.append(table)
        if invoice.comment != "":
            comment = Paragraph("<b>Comments:</b><br/>%s"%invoice.comment, style)
            Story.append(comment)
        bankInfo = Paragraph("""
<b>Bank Info</b><br/>
%s<br/>
%s<br/>
<br/>
<b>Acct. Name:</b> %s<br/> 
<b>Acct. #:</b> %s<br/> 
<b>Routing #:</b> %s<br/> 
<b>Swift Code:</b> %s<br/> 
""" % (settings.bankName, 
       settings.bankAddress.replace("\n", "<br/>"),
       settings.bankAcctName,
       settings.bankAcctNum,
       settings.routingNumber,
       settings.swiftCode), style)
        Story.append(bankInfo)
        
        doc.build(Story, onFirstPage=firstPage, onLaterPages=laterPages)
 
        
        
        
