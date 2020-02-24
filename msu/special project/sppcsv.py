import csv
import os
import datetime

def intcsv(basedict, outputloc):
    now = datetime.datetime.now()
    ts = now.strftime('(%Y-%m-%d %H%M)')

    intfile = os.path.join(outputloc,'instrument list ' + ts +'.csv' )

    opdict = {}

    for section in basedict:
        opdict[section] = {'organic':{'FT-IR':0,'NMR':0},
                           'analytical':{'GC/MS':0,'HPLC':0,'Microwave Digestor':0,'UV/VIS spectrophotometer':0},
                           'other':[]}

        for group in basedict[section]:
            intlist = basedict[section][group]['instruments']
            for item in intlist:
                x = 0
                for c in opdict[section].keys():
                    if c == 'other' and x == 1:
                        pass
                    elif c == 'other' and x == 0:
                        opdict[section]['other'].append(item)
                    elif item in opdict[section][c].keys():
                        opdict[section][c][item] += 1
                        x += 1


    oplist = [('Instruments by Section','')]
    oplist.append(('',''))

    for section in opdict:
        oplist.append((section,''))
        oplist.append(('',''))
        oplist.append(('Organic Instruments',''))
        oplist.append(('Instrument','Number of Groups'))
        for item in opdict[section]['organic']:
            oplist.append((item,opdict[section]['organic'][item]))
        oplist.append(('',''))
        oplist.append(('Analytical Instruments',''))
        oplist.append(('Instrument','Number of Groups'))
        for item in opdict[section]['analytical']:
            oplist.append((item,opdict[section]['analytical'][item]))
        oplist.append(('',''))
        oplist.append(('Other Instruments Requested',''))
        for item in opdict[section]['other']:
            oplist.append((item,''))
        oplist.append(('',''))

    with open(intfile,'w',newline='') as csvfile:
        wo = csv.writer(csvfile)
        for row in oplist:
            wo.writerow(row)

def chemcsv(basedict, outputloc):
    now = datetime.datetime.now()
    ts = now.strftime('(%Y-%m-%d %H%M)')

    chemfile = os.path.join(outputloc,'chemical list ' + ts + '.csv')
    casfile = os.path.join(outputloc, 'cas# list' + ts + '.csv')

    opdict = {}
    gundefined = []
    sundefined = []

    for section in basedict:
        for group in basedict[section]:
            for chemical in basedict[section][group]['chemicals']:
                if chemical[0] == 'up':
                    gundefined.append(chemical[1])
                elif chemical[0] == 'upr':
                    sundefined.append(chemical[1])
                else:
                    opdict.setdefault(chemical[1],{'names':[],'sections':[]})
                    if section not in opdict[chemical[1]]['sections']:
                        opdict[chemical[1]]['sections'].append(section)
                    if chemical[0] not in opdict[chemical[1]]['names']:
                        opdict[chemical[1]]['names'].append(chemical[0])

    oplist = [('Chemicals Requested',''),('','')]
    caslist = [('CAS numbers','')]

    for chemical in opdict:
        caslist.append((chemical,''))
        oplist.append(('CAS#',chemical))
        oplist.append(['Sections',]+opdict[chemical]['sections'])
        oplist.append(['Names Listed',]+opdict[chemical]['names'])
        oplist.append(('',''))

    oplist.append(('Single Chemicals that did not parse correclty:',''))
    for item in sundefined:
        oplist.append((item,''))

    oplist.append(('',''))
    oplist.append(('Whole responses that did not parse correctly:',''))
    for item in gundefined:
        oplist.append((item,''))

    with open(chemfile,'w',newline='') as csvfile:
        wo = csv.writer(csvfile)
        for row in oplist:
            wo.writerow(row)

    with open(casfile,'w',newline='') as csvfile:
        wo = csv.writer(csvfile)
        for row in caslist:
            wo.writerow(row)

def reparsecsv(basedict,outputloc):
    now = datetime.datetime.now()
    ts = now.strftime('(%Y-%m-%d %H%M)')

    rpfile = os.path.join(outputloc,'Group Breakdown by Section' + ts + '.csv')

    oplist = [('Section',''),('','')]

    for section in basedict:
        oplist.append((section,''))
        oplist.append(('',''))
        for group in basedict[section]:
            oplist.append((group,''))
            oplist.append(('Member','email address'))
            groupdict = basedict[section][group]

            for name in groupdict['names']:
                if name[0] == 'ur':
                    oplist.append(('Unable to parse response correctly',''))
                    oplist.append((name[1],''))
                elif name[0] == 'urp':
                    oplist.append('Unable to parse name/email correctly:',name[1])
                else:
                    oplist.append((name[0],name[1]))

            oplist.append(('',''))
            oplist.append(('Project Description',''))
            oplist.append((groupdict['description'],''))

            oplist.append(('',''))
            oplist.append(('Requested Equipment',''))
            for item in groupdict['equipment']:
                oplist.append((item,''))

            oplist.append(('',''))
            oplist.append(('Requested Instrument',''))
            for item in groupdict['instruments']:
                oplist.append((item,''))

            oplist.append(('',''))
            oplist.append(('Requested Chemicals',''))
            for chemical in groupdict['chemicals']:
                if chemical[0] == 'ur':
                    oplist.append(('Unable to parse response correctly',''))
                    oplist.append((chemical[1],''))
                elif chemical[0] == 'upr':
                    oplist.append(('Unable to parse chemical information correctly:',chemical[1]))
                else:
                    oplist.append((chemical[0],chemical[1]))

    with open(rpfile,'w',newline='') as csvfile:
        wo = csv.writer(csvfile)
        for row in oplist:
            wo.writerow(row)
