from StringIO import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
#from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER
from reportlab.lib.units import mm, inch
import reportlab.lib.colors as colors

from elisapdffunc import *


def assaysumpage(fqc, date, initials, screens,gentime):
#define the buffer
    buffer = StringIO()
#setup the document
    doc = SimpleDocTemplate(buffer,
                            pagesize = letter,
                            leftMargin=0.75*inch,
                            rightMargin=0.75*inch)

#add the address block and the title
    elements = header('ELISA Assay Quality Summary')
#add the assay, date and initals
    rundata = fqc.upper() + ' ' + date + ' ' + initials
    elements.append(Paragraph("<font size='-1'>"+rundata+"</font>",centered))
    elements.append(Spacer(0,0.25*inch))
#setup the table style, may have to set this equal to TableStyle()
    tablestyle = []

#get the inital column headers bolded
    tabledata = [map(bolder,['Matrix','Screen','Notes'])]
#determine the number of screens then divide it up so every 3 rows is grey
    rownum = len(screens)
    for x in range(0,rownum,3):
        if x%6 == 3:
            rowcolor = colors.lightgrey
        else:
            rowcolor = colors.white
#add it to the tablestyle noting that the column headers are on row one
        tablestyle.append(['BACKGROUND',(0,x+1),(2,x+3),rowcolor])

#go through the data and add the individual screens
    rowidx = 1
    for line in screens:
#last item in the line is the color
        tabledata.append(line[0:-1])
#if its yellow...
        if line[-1] == 'y':
#...update the style
            tablestyle.append(['BACKGROUND',(0,rowidx),(2,rowidx),colors.yellow])
        rowidx += 1
#center the text
    tablestyle.append(['ALIGN',(0,0),(2,(len(tabledata)-1)),'CENTER'])
    tablestyle.append(['LINEABOVE',(0,1),(2,1),1,colors.black])
#append the table
    elements.append(Table(tabledata, style=tablestyle, colWidths=[1*inch, 2.5*inch, 3.5*inch]))

#build the document
    doc.build(elements, canvasmaker = generateNumberedCanvasClass(initials,gentime,fqc))

    return buffer
