import os

from reportlab.platypus import *
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER
from reportlab.lib.units import inch
import reportlab.lib.colors as colors

from wasperfunc import *

#set the sticker header sytle
sheader = getSampleStyleSheet()["Normal"]
sheader.fontSize += 1
sheader.alignment = TA_CENTER

#set the sticker table style
stable = getSampleStyleSheet()["Normal"]
stable.fontSize = 7
stable.leading = 7
stable.alignment = TA_CENTER


#set the format for header block
sinfoblock = [['BACKGROUND',(0,0),(0,0),'lightgrey'],
              ['BACKGROUND',(2,0),(2,0),'lightgrey'],
              ['BACKGROUND',(4,0),(4,0),'lightgrey'],
              ['BACKGROUND',(6,0),(6,0),'lightgrey'],
              ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
              ['BOX',(0,0),(-1,-1),1,'black'],
              ['LEADING',(0,0),(-1,-1),6],
              ['LEFTPADDING',(0,0), (-1,-1), 3],
              ['RIGHTPADDING',(0,0), (-1,-1), 3]]

#set the base format for the table
sconblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
            ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
            ['BOX',(0,0),(-1,-1),1,'black'],
            ['LINEBELOW',(0,0),(-1,-2),0.5,'black'],
            ['LINEBEFORE',(2,0),(2,-1),0.5,'black'],
            ['LINEBEFORE',(4,0),(4,-1),0.5,'black'],
            ['LINEBEFORE',(6,0),(6,-1),0.5,'black'],
            ['SIZE',(0,0),(-1,-1),5],
            ['LEADING',(0,0),(-1,-1),5],
            ['LEFTPADDING',(0,0), (-1,-1), 2],
            ['RIGHTPADDING',(0,0), (-1,-1), 2],
            ['TOPPADDING',(0,0),(-1,-1),2],
            ['BOTTOMPADDING',(0,0),(-1,-1),2]]

#function to generate the sticker for the waste container
def stickerpdf(hexcode,room,enddate,stream,slist,outputloc):
#define where its going to be saved and the file name
    opname = os.path.join(outputloc,room+' '+stream+' '+enddate+' '+ hexcode + ' sticker.pdf')

#start the document
    doc = SimpleDocTemplate(opname,
                            pagesize = (11*inch, 8.5*inch),
                            topMargin = 0.1*inch,
                            bottomMargin = 0.1*inch,
                            leftMargin = 0.1*inch,
#add a huge right margin so that its just a half page document
                            rightMargin = 5.6*inch)

#this is the header block
    tableinfo = [[bolder('Waste PIN:',stable), Paragraph(hexcode,stable),
                  bolder('Room:',stable), Paragraph(room,stable),
                  bolder('Date Filled:',stable), Paragraph(enddate,stable),
                  bolder('Stream:',stable), Paragraph(stream,stable)]]

#build the flowable starting with the title
    elements = [Paragraph("<b>Chemical Consituents</b>",sheader)]
    elements.append(elements.append(Spacer(0,0.05*inch)))
#add the head block
    elements.append(Table(tableinfo, style = sinfoblock,
                          colWidths=[0.8*inch,0.8*inch,
                                     0.4*inch,0.4*inch,
                                     0.7*inch,0.7*inch,
                                     0.5*inch,0.5*inch]))

#add the chemical block
    contable = []
#change the background color on every other line to grey
    for i in range(1,60):
        if i%2 == 1:
            sconblock.append(['BACKGROUND',(0,i-1),(-1,i-1),'lightgrey'])

#concenate the columns together to then add that to contable
        contable.append(slist[0][i-1]+slist[1][i-1]+slist[2][i-1])

#append the contable
    elements.append(elements.append(Spacer(0,0.1*inch)))
    elements.append(Table(contable, style = sconblock,
                      colWidths=[1.4*inch,0.33*inch,
                                 1.4*inch,0.33*inch,
                                 1.4*inch,0.33*inch]))

    doc.build(elements)
