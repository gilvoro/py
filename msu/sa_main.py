import csv
import os

from sa_func import *

baseloc = 'c:\\Users\\jlaughl6\\User Assets\\script files\\safety agreement\\'

term = input('What Term (season-YYYY)?: ')

#tsdloc is the term survey data
tclloc = os.path.join(os.path.join(os.path.join(baseloc,'script_files'),term),'crn_list.csv')
tswloc = os.path.join(os.path.join(os.path.join(baseloc,'script_files'),term),'student_workers.csv')
tbfloc = os.path.join(os.path.join(baseloc,'banner_files'),term)
tsdloc = os.path.join(os.path.join(baseloc,'survey_data'),term)
tsfloc = os.path.join(os.path.join(baseloc,'sharepoint_files'),term)

esid = []
crndict = crn_parser(tclloc)

with open(tswloc, newline = '') as csvfile:
    raw_data = csv.reader(csvfile, delimiter = ',')
    for row in raw_data:
        if len(row) <= 0:
            pass
        else:
            esid.append(row[2].strip())
            crndict['00000']['students'][row[2].strip()] = {'name':row[1].strip() + ' ' + row[0].strip(),
                                                            'timestamp':'not completed',
                                                            'contact':'not completed',
                                                            'phone':'not completed',
                                                            'agreed':'no',
                                                            'eye':'not completed',
                                                            'metadata':[]}

crndict['99990'] = {'course':'non-parsable responses',
                    'section':'possible drops',
                    'instructor':'',
                    'desc':'possible drops',
                    'students':{}}
crndict['99991'] = {'course':'non-parsable responses',
                    'section':'student ID error',
                    'instructor':'',
                    'desc':'student ID error',
                    'students':{}}

banner_parser(tbfloc,crndict,esid)
survey_parser(tsdloc,crndict,esid)

outputdict = {}
for crn in crndict:
    outputdict.setdefault(crndict[crn]['course'],{})
    outputdict[crndict[crn]['course']][crndict[crn]['desc']] = crndict[crn]['students']

for course in sorted(outputdict.keys()):
    coursename = course + '.xlsx'
    opname = os.path.join(tsfloc,coursename)
    workbookmrk(opname,outputdict[course])
