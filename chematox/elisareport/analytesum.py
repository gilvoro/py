from StringIO import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
#from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER
from reportlab.lib.units import mm, inch
import reportlab.lib.colors as colors

from elisapdffunc import *


def analytesumpage(fqc,date,initials,metadata,controls,gentime):
#define the buffer
    buffer = StringIO()
#setup the document
    doc = SimpleDocTemplate(buffer,
                            pagesize = letter,
                            leftMargin=0.75*inch,
                            rightMargin=0.75*inch)
#add the address block and the title
    elements = header('ELISA Summary: ' + metadata[0])
#add the assay, date and initals
    rundata = fqc.upper() + ' ' + date + ' ' + initials
    elements.append(Paragraph("<font size='-1'>"+rundata+"</font>",centered))
    elements.append(Spacer(0,0.125*inch))
#start with the matrix control
    elements.append(Paragraph("<font size='+4'>Matrix Control</font>",centered))
    elements.append(Spacer(0,0.125*inch))
#setup the table style
    mctablestyle = []
#get the inital column headers bolded
    mctabledata = [map(bolder,['','Absorbance','Ratio','Notes',''])]
#add the matrix blank data
    mctabledata.append(controls[0][0:-1])
#if there is a flag for yellow backgroun should be yellow otherwise, grey
    if controls[0][-1] == 'y':
        c = colors.yellow
    else:
        c = colors.lightgrey
    mctablestyle.append(['BACKGROUND',(1,1),(3,1),c])
    mctablestyle.append(['ALIGN',(1,1),(3,1),'CENTER'])
    mctablestyle.append(['LINEABOVE',(1,1),(3,1),1,colors.black])
#append the MC data
    elements.append(Table(mctabledata, style = mctablestyle, colWidths=[1*inch, 1.5*inch, 1.0*inch, 2*inch,1*inch]))
#setup the calibrator header and table
    elements.append(Spacer(0,0.125*inch))
    calheader = 'Calibrator: ' + str(metadata[1]) + 'ng/mL'
    elements.append(Paragraph("<font size='+4'>"+calheader+"</font>",centered))
    elements.append(Spacer(0,0.125*inch))
#setup the table style
    caltablestyle = []
#get the inital column headers bolded
    caltabledata = [map(bolder,['','Absorbance','Ratio','Notes',''])]
#add the calibrator data
    caltabledata.append(controls[1][0:-1])
#if there is a flag for yellow backgroun should be yellow otherwise, grey
    if controls[1][-1] == 'y':
        c = colors.yellow
    else:
        c = colors.lightgrey
    caltablestyle.append(['BACKGROUND',(1,1),(3,1),c])
    caltablestyle.append(['ALIGN',(1,1),(3,1),'CENTER'])
    caltablestyle.append(['LINEABOVE',(1,1),(3,1),1,colors.black])
#append the cal data
    elements.append(Table(caltabledata, style = caltablestyle, colWidths=[1*inch, 1.5*inch, 1.0*inch, 2*inch,1*inch]))
#setup the BCC header and table
    elements.append(Spacer(0, 0.125*inch))
    bccheader = 'Control-Below Calibrator: '+str(metadata[2])+'ng/mL'
    elements.append(Paragraph("<font size='+5'>"+bccheader+"</font>",centered))
    elements.append(Spacer(0,0.125*inch))
#setup the table style
    bcctablestyle = []
#get the inital column headers bolded
    bcctabledata = [map(bolder,['Position','Absorbance','Ratio','Notes',''])]
#allow the notes to span both column 3 and 4
    bcctablestyle.append(['SPAN',(3,0),(4,0)])
#add the bcc data
#we start at row 1, row 0 being the titles
    rowindex = 1
    for row in controls[2]:
        bcctabledata.append(row[0:-1])
#get the color of the row
        if row[-1] == 'y':
            c = colors.yellow
        elif (rowindex+1)%2 == 0:
            c = colors.white
        else:
            c = colors.lightgrey
#allow the notes to span both column 3 and 4
        bcctablestyle.append(['SPAN',(3,rowindex),(4,rowindex)])
        bcctablestyle.append(['BACKGROUND',(0,rowindex),(4,rowindex),c])
        rowindex += 1
#center the text
    bcctablestyle.append(['ALIGN',(0,0),(4,(len(bcctabledata)-1)),'CENTER'])
    bcctablestyle.append(['LINEABOVE',(0,1),(4,1),1,colors.black])
#append the below calibrator data
    elements.append(Table(bcctabledata, style = bcctablestyle, colWidths=[1*inch, 1.5*inch, 1.0*inch, 2*inch,1*inch]))
#setup the aCC header and table
    elements.append(Spacer(0, 0.125*inch))
    accheader = 'Control-Above Calibrator: '+str(metadata[3])+'ng/mL'
    elements.append(Paragraph("<font size='+5'>"+accheader+"</font>",centered))
    elements.append(Spacer(0,0.125*inch))
#setup the table style
    acctablestyle = []
#get the inital column headers bolded
    acctabledata = [map(bolder,['Position','Absorbance','Ratio','Notes',''])]
#allow the notes to span both column 3 and 4
    acctablestyle.append(['SPAN',(3,0),(4,0)])
#add the acc data
#we start at row 1, row 0 being the titles
    rowindex = 1
    for row in controls[3]:
        acctabledata.append(row[0:-1])
#get the color of the row
        if row[-1] == 'y':
            c = colors.yellow
        elif (rowindex+1)%2 == 0:
            c = colors.white
        else:
            c = colors.lightgrey
#allow the notes to span both column 3 and 4
        acctablestyle.append(['SPAN',(3,rowindex),(4,rowindex)])
        acctablestyle.append(['BACKGROUND',(0,rowindex),(4,rowindex),c])
        rowindex += 1
#center the text
    acctablestyle.append(['ALIGN',(0,0),(4,(len(acctabledata)-1)),'CENTER'])
    acctablestyle.append(['LINEABOVE',(0,1),(4,1),1,colors.black])
#append the above calibrator data
    elements.append(Table(acctabledata, style = acctablestyle, colWidths=[1*inch, 1.5*inch, 1.0*inch, 2*inch,1*inch]))
#build the document
    doc.build(elements, canvasmaker = generateNumberedCanvasClass(initials,gentime,fqc))

    return buffer
