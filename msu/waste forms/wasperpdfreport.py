import os

from reportlab.lib.pagesizes import letter
from reportlab.platypus import *
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
import reportlab.lib.colors as colors

from wasperfunc import *

header = getSampleStyleSheet()["Normal"]
header.fontSize += 5
header.alignment = TA_CENTER

smheader = getSampleStyleSheet()["Normal"]
smheader.fontSize += 2
smheader.alignment = TA_CENTER

parastyle = getSampleStyleSheet()["Normal"]
parastyle.fontSize = 8
parastyle.alignment = TA_CENTER

infostyle = getSampleStyleSheet()["Normal"]
infostyle.fontSize += 1
infostyle.alignment = TA_CENTER

ehsstyle = getSampleStyleSheet()["Normal"]
ehsstyle.fontSize += 1
ehsstyle.alignment = TA_LEFT

infoblocks = [['ALIGN', (0,0),(5,2),'CENTER'],['SPAN',(0,0),(5,0)],['BACKGROUND',(0,1),(0,2),'lightgrey'],
           ['BACKGROUND',(2,1),(2,2),'lightgrey'],['BACKGROUND',(4,1),(4,2),'lightgrey'],
           ['BOX',(0,1),(-1,-1),1,'black'],['LINEBELOW',(0,1),(5,1),0.5,'black']]

conblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
            ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
            ['BOX',(0,0),(-1,-1),1,'black'],
            ['BOX',(4,19),(5,39),1,'black'],
            ['LINEBELOW',(0,0),(-1,-16),0.5,'black'],
            ['LINEBELOW',(0,-17),(-3,-1),0.5,'black'],
            ['LINEBEFORE',(2,0),(2,-1),0.5,'black'],
            ['LINEBEFORE',(4,0),(4,-1),0.5,'black'],
            ['LINEBEFORE',(6,0),(6,-1),0.5,'black'],
            ['SIZE',(0,0),(-1,-1),8],
            ['LEADING',(0,0),(-1,-1),6],
            ['LEFTPADDING',(0,0), (-1,-1), 3],
            ['RIGHTPADDING',(0,0), (-1,-1), 3],
            ['TOPPADDING',(0,0),(-1,-1),2],
            ['BOTTOMPADDING',(0,0),(-1,-1),2],
            ['SPAN',(4,19),(5,20)],
            ['SPAN',(4,21),(5,22)],
            ['SPAN',(4,23),(5,24)],
            ['SPAN',(4,25),(5,27)],
            ['SPAN',(4,28),(5,30)],
            ['SPAN',(4,31),(5,33)],
            ['SPAN',(4,34),(5,36)],
            ['SPAN',(4,37),(5,39)]]

backblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
            ['VALIGN',(0,0),(-1,-1),'MIDDLE'],
            ['BOX',(0,0),(-1,-1),1,'black'],
            ['LINEBELOW',(0,0),(-1,-1),0.5,'black'],
            ['LINEBEFORE',(2,0),(2,-1),0.5,'black'],
            ['LINEBEFORE',(4,0),(4,-1),0.5,'black'],
            ['LINEBEFORE',(6,0),(6,-1),0.5,'black'],
            ['SIZE',(0,0),(-1,-1),8],
            ['LEADING',(0,0),(-1,-1),6],
            ['LEFTPADDING',(0,0), (-1,-1), 3],
            ['RIGHTPADDING',(0,0), (-1,-1), 3],
            ['TOPPADDING',(0,0),(-1,-1),2],
            ['BOTTOMPADDING',(0,0),(-1,-1),2]]

sigblock = [['ALIGN',(0,0),(-1,-1),'CENTER'],
            ['LINEBELOW',(1,0),(1,0),0.5,'black'],
            ['LINEBELOW',(3,0),(3,0),0.5,'black'],]

admininfo = [[Paragraph("<b>Administrative Information</b>",smheader),'','','','',''],
             [bolder('Waste PIN:',infostyle),'2c3fd44567',bolder('Contact:',infostyle),
              'James Laughlin',bolder('Phone Number:',infostyle),'303-605-7173'],
              [bolder('Building:',infostyle),'Science',bolder('Room:',infostyle),'3091',
               bolder('Generated From:',infostyle),'Organic Teaching Lab']]

wasteinfo = [[Paragraph("<b>Waste Characteristics</b>",smheader),'','','','',''],
             [bolder('Container Size:',infostyle),'10-Liter',bolder('Container Material:',infostyle),
              'Plastic',bolder('Physical State:',infostyle),'Liquid'],
              [bolder('pH of the Waste:',infostyle),'n/a',bolder('Approximate Volume:',infostyle),'8-Liters',
               bolder('Filled Date:',infostyle),'2019-10-02']]

siginfo = [[Paragraph("<b>Signature:</b>",smheader),'',Paragraph("<b>Date:</b>",smheader),'']]

def reportpdf(hexcode,contact,phone,room,generator,csize,cmat,
              state,ph,grossvolume,enddate,stream,flist,rlist,
              secpage,outputloc):
    
    opname = os.path.join(outputloc,room+' '+stream+' '+enddate+' '+ hexcode + ' report.pdf')

    admininfo = [[Paragraph("<b>Administrative Information</b>",smheader),'','','','',''],
                 [bolder('Waste PIN:',infostyle),hexcode,bolder('Contact:',infostyle),
                  contact,bolder('Phone Number:',infostyle),phone],
                  [bolder('Building:',infostyle),'Science',bolder('Room:',infostyle),room,
                   bolder('Generated From:',infostyle),generator]]

    wasteinfo = [[Paragraph("<b>Waste Characteristics</b>",smheader),'','','','',''],
                 [bolder('Container Size:',infostyle),csize,bolder('Container Material:',infostyle),
                  cmat,bolder('Physical State:',infostyle),state],
                  [bolder('pH of the Waste:',infostyle),ph,
                   bolder('Approximate Volume:',infostyle),'~'+str(round(grossvolume,0))+'mL',
                   bolder('Filled Date:',infostyle),enddate]]

    doc = SimpleDocTemplate(opname,
                            pagesize = letter,
                            topMargin = 0.2*inch,
                            bottomMargin = 0.2*inch,
                            leftMargin = 0.2*inch,
                            rightMargin = 0.2*inch)

    elements = []
    elements.append(Paragraph('<b>Metropolitan State University, Department of Chemistry and Biochemstry</b>',
                              header))
    elements.append(Spacer(0,0.05*inch))
    elements.append(Paragraph('<b>Hazardous Waste Record Form</b>', header))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Table(admininfo, style = infoblocks,
                          colWidths=[1*inch,1*inch,1*inch,1.25*inch,1.5*inch,2*inch]))
    elements.append(Table(wasteinfo, style = infoblocks,
                          colWidths=[1.45*inch,0.95*inch,2*inch,0.95*inch,1.35*inch,1.05*inch]))
    elements.append(Spacer(0,0.05*inch))
    elements.append(Paragraph('I certify the accuracy of this record; that <b>I have received MSUD Hazardous Waste Traing</b>; that biological materials have been rendered inactive/non-infectious, and that I am actively seeking to minimize the generation of hazardous waste',
                              parastyle))
    elements.append(Spacer(0,0.15*inch))
    elements.append(Table(siginfo, style = sigblock, colWidths = [1.25*inch,3*inch,0.75*inch,2*inch]))
    elements.append(Spacer(0,0.1*inch))
    elements.append(Paragraph("<b>Chemical Consituents</b>",smheader))
    elements.append(Spacer(0,0.05*inch))

    if secpage:
        conblock.append(['SPAN',(4,17),(5,17)])
        conblock.append(['SPAN',(4,18),(5,18)])
        flist[2] = flist[2] + [['This is not a ful list',''],
                                ['See reverse for complete list',''],
                                [bolder('EHS USE ONLY',infostyle),''],
                                ['',''],
                                [bolder('ID:',ehsstyle),''],
                                ['',''],
                                [bolder('Determinations',infostyle),''],
                                ['',''],
                                [bolder('1.)',ehsstyle),''],
                                ['',''],
                                ['',''],
                                [bolder('2.)',ehsstyle),''],
                                ['',''],
                                ['',''],
                                [bolder('3.)',ehsstyle),''],
                                ['',''],
                                ['',''],
                                [bolder('4.)',ehsstyle),''],
                                ['',''],
                                ['',''],
                                [bolder('5.)',ehsstyle),''],
                                ['',''],
                                ['','']]

    else:
        flist[2] = flist[2] + [[bolder('EHS USE ONLY',infostyle),''],
                               ['',''],
                               [bolder('ID:',ehsstyle),''],
                               ['',''],
                               [bolder('Determinations',infostyle),''],
                               ['',''],
                               [bolder('1.)',ehsstyle),''],
                               ['',''],
                               ['',''],
                               [bolder('2.)',ehsstyle),''],
                               ['',''],
                               ['',''],
                               [bolder('3.)',ehsstyle),''],
                               ['',''],
                               ['',''],
                               [bolder('4.)',ehsstyle),''],
                               ['',''],
                               ['',''],
                               [bolder('5.)',ehsstyle),''],
                               ['',''],
                               ['','']]

    contable = []
    for i in range(1,41):
        if i%2 == 1:
            if i < 20:
                conblock.append(['BACKGROUND',(0,i-1),(-1,i-1),'lightgrey'])
            else:
                conblock.append(['BACKGROUND',(0,i-1),(-3,i-1),'lightgrey'])

        contable.append(flist[0][i-1]+flist[1][i-1]+flist[2][i-1])

    elements.append(Table(contable, style = conblock,
                      rowHeights = 13,
                      colWidths=[2.1*inch,0.47*inch,
                                 2.1*inch,0.47*inch,
                                 2.1*inch,0.47*inch]))
    if secpage:
        elements.append(PageBreak())
        title = 'Full Chemical Consituents List for Waste PIN:' + '2c3fd44567'
        elements.append(bolder(title,smheader))
        elements.append(Spacer(0,0.05*inch))

        backtable = []
        for i in range(1,57):
            if i%2 == 1:
                backblock.append(['BACKGROUND',(0,i-1),(-1,i-1),'lightgrey'])

            backtable.append(rlist[0][i-1]+rlist[1][i-1]+rlist[2][i-1])

        elements.append(Table(backtable, style = backblock,
                          rowHeights = 13,
                          colWidths=[2.1*inch,0.47*inch,
                                     2.1*inch,0.47*inch,
                                     2.1*inch,0.47*inch]))

    doc.build(elements)
