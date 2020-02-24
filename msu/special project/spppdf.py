import io
import os
import reportlab.lib.colors as colors

from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER, TA_LEFT
from reportlab.lib.units import inch

header = getSampleStyleSheet()["Normal"]
header.fontSize += 5
header.alignment = TA_CENTER

generalstyle = getSampleStyleSheet()["Normal"]
generalstyle.fontSize += 1
generalstyle.alignment = TA_CENTER

def bolder(x,fstyle):
    if len(x):
        return Paragraph("<b>%s</b>" % (x,),fstyle)
    else:
        return x

def grouppage(section,group,groupdict):
    buffer = io.BytesIO()

    names = groupdict['names']

    nameblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
                ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
                ['BOX',(0,1),(-1,-1),1,'black'],
                ['LINEBELOW',(0,0),(-1,0),0.5,'black']]


    if names[0] == 'up':
        nameinfo = [[Paragraph("<b>Failed to Parse Input</b>",generalstyle)],names[1]]
        nameblock = nameblock + [['LINEBELOW',(0,0),(-1,0),0.5,'black']]
    else:
        nameinfo = [[Paragraph("<b>Name</b>",generalstyle),Paragraph("<b>Email Address</b>",generalstyle)]]
        nameblock.append(['LINEBELOW',(0,0),(-1,0),0.5,'black'])

        x = 1
        for name in names:
            if name[0] == 'upr':
                nameinfo.append([Paragraph("<b>Failed to Parse:</b>",generalstyle),name[1]])
                nameblock.append(['LINEBELOW',(0,x),(-1,x),0.5,'black'])
            else:
                nameinfo.append([name[0],name[1]])
                nameblock.append(['LINEBELOW',(0,x),(-1,x),0.5,'black'])
            if x%2 == 1:
                nameblock.append(['BACKGROUND',(0,x),(-1,x),'lightgrey'])

    descblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
                ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
                ['BOX',(0,1),(-1,-1),1,'black'],
                ['LINEBELOW',(0,0),(-1,0),0.5,'black']]

    descinfo = [[Paragraph("<b>Description</b>",generalstyle)],[Paragraph(groupdict['description'],generalstyle)]]

    equip = groupdict['equipment']

    equipblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
                ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
                ['BOX',(0,1),(-1,-1),1,'black'],
                ['LINEBELOW',(0,0),(-1,-1),0.5,'black']]

    equipinfo = [[Paragraph("<b>Equipment</b>",generalstyle)]]

    x = 1
    for item in equip:
        equipinfo.append([item])
        equipblock.append(['LINEBELOW',(0,x),(-1,x),0.5,'black'])
        if x%2 == 1:
            equipblock.append(['BACKGROUND',(0,x),(-1,x),'lightgrey'])
        x += 1

    instrument = groupdict['instruments']

    intblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
                ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
                ['BOX',(0,1),(-1,-1),1,'black'],
                ['LINEBELOW',(0,0),(-1,0),0.5,'black']]

    intinfo = [[Paragraph("<b>Instrunments</b>",generalstyle)]]

    x = 1
    for item in instrument:
        intinfo.append([item])
        intblock.append(['LINEBELOW',(0,x),(-1,x),0.5,'black'])
        if x%2 == 1:
            intblock.append(['BACKGROUND',(0,x),(-1,x),'lightgrey'])
        x += 1

    chemicals = groupdict['chemicals']

    chemblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
                ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
                ['BOX',(0,1),(-1,-1),1,'black'],
                ['LINEBELOW',(0,0),(-1,0),0.5,'black']]


    if chemicals[0] == 'up':
        cheminfo = [[Paragraph("<b>Failed to Parse Input</b>",generalstyle)],[chemicals[1]]]
        chemblock = chemblock + [['LINEBELOW',(0,0),(-1,0),0.5,'black']]
    else:
        cheminfo = [[Paragraph("<b>Name</b>",generalstyle),Paragraph("<b>CAS Number</b>",generalstyle),
                     Paragraph("<b>Strength</b>",generalstyle),Paragraph("<b>Amount</b>",generalstyle)]]
        chemblock.append(['LINEBELOW',(0,0),(-1,0),0.5,'black'])

        x = 1
        for chemical in chemicals:
            if chemical[0] == 'upr':
                cheminfo.append([Paragraph("<b>Failed to Parse:</b>",generalstyle),chemical[1]])
                chemblock.append(['LINEBELOW',(0,x),(-1,x),0.5,'black'])
                chemblock.append(['SPAN',(1,x),(-1,x)])
            else:
                cheminfo.append([chemical[0],chemical[1],chemical[2],chemical[3]])
                chemblock.append(['LINEBELOW',(0,x),(-1,x),0.5,'black'])
            if x%2 == 1:
                chemblock.append(['BACKGROUND',(0,x),(-1,x),'lightgrey'])
            x += 1


    doc = SimpleDocTemplate(buffer,
                            pagesize = letter,
                            topMargin = 0.5*inch,
                            bottomMargin = 0.5*inch,
                            leftMargin = 0.5*inch,
                            rightMargin = 0.5*inch)

    elements = []
    elements.append(Paragraph(section,header))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Paragraph(group,header))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Table(nameinfo, style = nameblock))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Table(descinfo, style = descblock))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Table(equipinfo, style = equipblock))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Table(intinfo, style = intblock))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Table(cheminfo, style = chemblock))

    doc.build(elements)

    return buffer
