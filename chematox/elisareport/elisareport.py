import csv
import re
import sys
import os
import pyPdf
import datetime
import psycopg2
import psycopg2.extensions
import shutil

from pyPdf import PdfFileReader, PdfFileWriter
#other script files
from elisareportfunc import *
from IAreader import *
from elisareportdata import *
from assaysum import *
from analytesum import *
from samplesum import *

#hardcode directory for initail coding
testfiles = '/aquifer/home/james/pve/elisareport/test files/'

#beginning list and dictionarys
currentinitalslist = []
analytecutoff = {}
report_data = {'metadata':{},
              'assaypdf':[],
              'analytepdfs':{},
              'samplepdfs':{}}

#get the date
usetodaydate = raw_input("Use today's date for the assay (enter 'y' for yes or n for 'no'): ")
if usetodaydate.lower() == 'quit' or usetodaydate.lower() == 'q' or usetodaydate.lower() == 'exit':
    sys.exit()
elif usetodaydate.lower() == 'y' or  usetodaydate.lower() == 'yes' or usetodaydate.lower() == '':
    print 'Using ' + datetime.datetime.today().strftime('%Y-%m-%d') + ' as the date'
    rundate = datetime.datetime.today().date()
else:
    rundate = getdate()
#rundate = datetime.datetime.strptime('2019-02-19','%Y-%m-%d').date()
gentime = datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S')
report_data['metadata']['rundate'] = rundate

#get the matrix
acceptablematrix = ['blood','plasma','urine']
print ''
matrixtype = getmatrix(acceptablematrix)
#matrixtype = 'blood'
report_data['metadata']['matrix'] = matrixtype

#from jkominek/chematox/display.py
conn = psycopg2.connect("host=lims-db.chematox.com dbname=chematox user=reader password=immunoassay")
c = conn.cursor()
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, c)
c.execute("set application_name = 'elisa report'")
conn.commit()
#get all the intials of the current employees and add them to a list
c.execute("""select e.initials from employees e where e.stop = '2100-01-01'""")
for returned in c:
    if returned == '' or returned == ' ' or returned == 'None':
        pass
    else:
        currentinitalslist.append(returned[0])
#get the cutoff limits for all the ELISA in the entered matrix
c.execute("""select tt.analyte, tt.id, l.value, l.as_of from testtypes tt, limits l where tt.method = 'ELISA' and tt.submethod is null and l.testtype = tt.id and l.matrix = %s""",(matrixtype,))
#add the results to a dictionary
for analyte, id, value, as_of in c:
    analytedict = analytecutoff.setdefault(analyte,{'id':id,
                                                    'cutoff':value,
                                                    'e_date':as_of})
#check and replace with new values if applicable.
    if as_of > analytedict['e_date']:
        analytedict['cutoff'] = value
        analytedict['e_date'] = as_of
#close the connection
conn.close()

#check to see if the initials entered are in the lims
print ''
initials = getinitials(currentinitalslist)
#initials = 'jrl'
report_data['metadata']['tech'] = initials

#check that they are adding in a probably formated FQC number
print ''
fqcnum = getfqc()
#fqcnum = 'fqc-9999'
report_data['metadata']['fqcnum'] = fqcnum

#go find the file for sample list
samplelistfolder = '/aquifer/home/james/pve/elisareport/sample lists/'
samplelistname = fqcnum + ' sample list.csv'
unsorted_samplelist = []
ctnumcheck = re.compile('\d\d\d\d\d\d[A-Z]?')
#try to open the sample list, if its not there capture the error and report back
try:
    with open (os.path.join(samplelistfolder,samplelistname),'rU') as csvfile:
        raw_data = csv.reader(csvfile)
        for row in raw_data:
            for item in row:
                unsorted_samplelist.append(item)
except (OSError, IOError) as e:
    print 'Error encountnered, traceback reads:'
    print e
    print 'Please fix error and rerun the program'
    close = raw_input('Please press enter close program')
    sys.exit()

samplelist = []
#go throught the unsorted list item by item and add any ct numbers to the list.
for item in unsorted_samplelist:
    isctnum = ctnumcheck.match(item.upper())
    if isctnum:
        if 6 == len(isctnum.group()):
            samplelist.append(isctnum.group() +'A')
        elif 7 == len(isctnum.group()):
            samplelist.append(isctnum.group())
#we want only unique values
samplelist = set(samplelist)

#get the list of files that for the FQCnum and check that are correct
platelist, excludedplates = getplatelist(getfilelist(testfiles, fqcnum),[],fqcnum)
#filelist = getfilelist(testfiles,fqcnum)

#get the unsorted date out of files. Assume this script will change when reader changes
unsorted_data,inventory_data = IAreader(platelist, rundate)

#process the data for the report and make the lims file
dataforlims, standard_data = dataprocess(unsorted_data, report_data, analytecutoff, matrixtype, samplelist)

#get the individual pages for the PDF
document = []
#assay summary first
r = assaysumpage(report_data['metadata']['fqcnum'],
                 datetime.datetime.strftime(report_data['metadata']['rundate'],('%Y-%m-%d')),
                 report_data['metadata']['tech'], report_data['assaypdf'],gentime)

#add the annotation notes
r.annotation = {'section': 'Calibration & Controls',
                'CT#':report_data['ctnums'],
                'page_name':'Assay Summary'}

#add to the document
document.append(r)

#make analyte summary for each analyte
for analyte in sorted(report_data['analytepdfs'].keys()):
    ana_page_name = 'Summary ' + report_data['analytepdfs'][analyte][0][0]
    r = analytesumpage(report_data['metadata']['fqcnum'],
                     datetime.datetime.strftime(report_data['metadata']['rundate'],('%Y-%m-%d')),
                     report_data['metadata']['tech'], report_data['analytepdfs'][analyte][0],
                     report_data['analytepdfs'][analyte][1],gentime)
#add the annotation notes
    r.annotation = {'section': 'Calibration & Controls',
                    'CT#':report_data['ctnums'],
                    'page_name':ana_page_name}
#add to the document
    document.append(r)

#make summary for each summary
for sample in sorted (report_data['samplepdfs'].keys()):
#set up the annotations, if the sample is a val or exp it should go into laserfiche, else it should
#blank the section and listing no ct number should prevent it from going anyway interesting i think
    sam_page_name = 'ELSIA report: ' + sample + ' ' + fqcnum
    if report_data['samplepdfs'][sample][0] == 'none':
        secanno = ''
        ctnumanno = []
    else:
        secanno = 'Lab Results'
        ctnumanno = [int(report_data['samplepdfs'][sample][0])]

    r = samplesumpage(report_data['metadata']['fqcnum'],sample, report_data['samplepdfs'][sample][1],
                      report_data['metadata']['tech'],gentime)
#add the annotation notes
    r.annotation = {'section': secanno,
                        'CT#':ctnumanno,
                        'page_name':sam_page_name}
#add to the document
    document.append(r)

#output folder
procdir = '/aquifer/home/james/pve/elisareport/processed/'
procfolder = fqcnum + ' ELISA'

#get the general path for the data, make sure it exists
procpath = os.path.join(procdir,procfolder)
if not os.path.exists(procpath):
    os.makedirs(procpath)

#output files names
pdfop = os.path.join(procpath,fqcnum + ' ' + gentime + '.pdf')
limsop = os.path.join(procpath, fqcnum + ' lims upload ' + gentime + '.csv')

#add the annotations to the pdf pages
reportout = PdfFileWriter()
#walk through the documents adding annotations to each page
for odoc in document:
    doc = PdfFileReader(odoc)
#check to see if it has annotation notes
    if hasattr(odoc, 'annotation'):
        annot = odoc.annotation
#not sure this is correct
    else:
        annot = [ ]
#add method to the annotations
    annot['method'] = 'ELISA'
#call jay's annotation function add stuff then add the page to pdf for the report
    for page in doc.pages:
        annotate_page(page, annot)
        reportout.addPage(page)

#make and save the pdf file
reportout.write(file(pdfop,'wb'))

#get the number of standard wells used per analyte and add them to the inventory data and add it to the output
dataforlims.append(['inventory',''])
for analyte in sorted(inventory_data.keys()):
    standardtotal = 2 + len(standard_data[analyte]['below cal']) + len(standard_data[analyte]['above cal'])
#add data to the output as follows analyte, catalog#, total wells used, number of well used for standards
    dataforlims.append([analyte, inventory_data[analyte]['catalognum'],
                        inventory_data[analyte]['wellcount'],standardtotal])
#add the cut of data to the output file
dataforlims.append(['cutoffs',''])
for analyte in sorted(standard_data):
#add data to the limsout as follows analyte, calibrator ratio
    dataforlims.append([analyte,standard_data[analyte]['calibrator']])
#write out the limsfile
with open (limsop, 'wb') as op:
    print row
    wo = csv.writer(op)
    for row in dataforlims:
        wo.writerow(row)

#clean up. Move files around
print ''
print 'Moving included raw data files'
incpath = os.path.join(procpath, 'raw data-included')
if not os.path.exists(incpath):
    os.makedirs(incpath)
for item in platelist:
    shutil.copy(item,os.path.join(incpath,(item.split('/')[-1])))

print 'Moving excluded raw data files'
expath = os.path.join(procpath, 'raw data-excluded')
if not os.path.exists(expath):
    os.makedirs(expath)
for item in excludedplates:
    shutil.copy(item,os.path.join(expath,(item.split('/')[-1])))

close = raw_input('Please press enter to close program')
sys.exit()
