from StringIO import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
#from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER
from reportlab.lib.units import mm, inch
import reportlab.lib.colors as colors

from elisapdffunc import *

def samplesumpage(fqc,samplename, sampledata, initials, gentime):
#define the buffer
    buffer = StringIO()
#setup the document
    doc = SimpleDocTemplate(buffer,
                            pagesize = letter,
                            leftMargin=0.75*inch,
                            rightMargin=0.75*inch)
#add the address block and the title
    elements = header('ELISA Analysis Report')
#add the sample number
    samplenum = 'ChemaTox # ' + samplename
    elements.append(Paragraph("<font size='-1'>"+samplenum+"</font>",centered))
    elements.append(Spacer(0,0.125*inch))
#add the column titles
    tabledata=[map(bolder,['Analytes','Calibrator','Calibrator','Sample','Sample','Sample']),
               map(bolder,['Tested','Concentration','Ratio','Ratio','Absorbance','Result'])]
#set up the tablestyle = []
    tablestyle = []
#add the row data, we start on row two because column titles
    rowindex = 2
#flag the correct color
    for row in sampledata:
        tabledata.append(row[0:-1])
        if row[-1] == 'y':
            c = colors.yellow
        elif row[-1] == 'b':
            c = colors.lightblue
        elif 2 < (rowindex+1)%6:
            c = colors.lightgrey
        else:
            c = colors.white
#update the table style
        tablestyle.append(['BACKGROUND',(0,rowindex),(5,rowindex),c])
        rowindex += 1

    tablestyle.append(['ALIGN', (0,0),(5,(len(tabledata)-1)),'CENTER'])
    tablestyle.append(['LINEABOVE',(0,2),(5,2),1,colors.black])
#add the table to the elements
    elements.append(Table(tabledata, style=tablestyle,
                          colWidths=[1.75*inch, 1.5*inch, 1.0*inch, 1.0*inch,1.25*inch,1.0*inch]))
#build the document
    doc.build(elements, canvasmaker = generateNumberedCanvasClass(initials,gentime,fqc))

    return buffer
