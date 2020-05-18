import csv
import calendar
import datetime
import logging
import numpy as np
import os
import pandas as pd
import re
import sys
import tkinter
import xlsxwriter

#get the specific tkinter object
from tkinter import filedialog
#get functions
from ordersheet_parser_func import *

#setup the list to control the order data in the op excel files
oporder = ['dop','desc','vendor','cost','payee','fund','cat','sub','end','dor']

#get the date and make a timestamp
now = datetime.datetime.now()
ts = datetime.datetime.strftime(now,'%Y-%m-%d_%H%M%S')
#get the last day of the month from previous month, default to december
ldlm = calendar.monthrange(now.year - 1, 12)[1]
if now.month - 1 > 0:
    ldlm = calendar.monthrange(now.year, now.month-1)[1]

#setup a logger
slloc = os.path.join('c:\\Users\\jlaughl6\\User Assets\\script files\\script_logs','ss_log_' + ts + '.log')
#slloc = os.path.join('c:\\Users\\jlaughl6\\User Assets\\script files\\script_logs','ss_log_test.txt')

logging.basicConfig(filename = slloc,format='%(asctime)s %(levelname)s:%(message)s',level=logging.INFO)
logging.info('logging started')

#get the date range. if none is give default to last month
sdate = input('enter the start date for the report (yyyy-mm-dd): ')
try:
    sdate = datetime.datetime.strptime(sdate,'%Y-%m-%d')
except (ValueError):
    print('using start default date')
    if now.month == 1:
        sdate = str(now.year-1) + '-' + str(12) + '-01'
    else:
        sdate = str(now.year) + '-' + '{:02d}'.format(now.month-1) + '-01'
    logging.info('using default start date: ' + sdate)
    sdate = datetime.datetime.strptime(sdate,'%Y-%m-%d')

edate = input('enter the end date for the report (yyyy-mm-dd): ')
try:
    edate = datetime.datetime.strptime(edate,'%Y-%m-%d')
except (ValueError):
    print('using end default date')
    if now.month == 1:
        edate = str(now.year-1) + '-' + str(12) + '-31'
    else:
        edate = str(now.year) + '-' + '{:02d}'.format(now.month-1) + '-' + '{:02d}'.format(ldlm)
    logging.info('using default end date: ' + edate)
    edate = datetime.datetime.strptime(edate,'%Y-%m-%d')

#determine the fiscal year from the dates provided, no way this will ever be a problem
if edate.month in [1,2,3,4,5,6]:
    fy = 'fy'+str(edate.year)
else:
    fy = 'fy'+str(edate.year + 1)

logging.info('using fiscal year: ' + fy)
print('Using fiscal year: ' + fy)
#setup the default pathway
desktop = os.path.expanduser('~\Desktop')
rloc = 'c:\\Users\\jlaughl6\\User Assets\\script files\\budget\\for_script'
dloc = os.path.join('c:\\Users\\jlaughl6\\User Assets\\script files\\budget',fy)
oploc = os.path.join(dloc,'new_cr_reports')
dbloc = os.path.join(dloc,'database\\ordersheet_db')
nploc = os.path.join(dloc,'database\\not_posted_db')

#make reference dictionary
refdict = getref(rloc)

#get the not posted data
logging.info('getting not posted data')
nts = datetime.datetime(1900,1,1)
nf = 'none'
for f in os.listdir(nploc):
    fts = datetime.datetime.strptime(f.split('_')[2]+' '+f.split('_')[3].split('.')[0],'%Y-%m-%d %H%M%S')
    if fts > nts:
        nts = fts
        nf = f

    if nf != 'none':
        npdf = pd.read_excel(os.path.join(nploc,f),usecols = 'B:N')
        npdf = npdf.fillna('')

#start tkinter and get the file
logging.info('getting file location')
root = tkinter.Tk()
root.withdraw()

fileloc = filedialog.askopenfilename(defaultextension = '.xlsx',
                                   filetypes = [('Excel File','.xlsx')],
                                   initialdir = desktop,
                                   title ='Please select Excel file')

#confirm a file is selected
if not os.path.isfile(fileloc):
    print('No file selected. Program terminating')
    logging.info('no file selected, program terminated')
    logging.shutdown()
    sys.exit()

#get the data for processing
rawdata = dataretrieval(fileloc,dbloc,ts)


databyline = {}
databypur = {}
#need to generate a not received report but do that later- nrlist = []

for line in rawdata:
    sdict = rawdata[line]
#skip rows that have no data in them
    if all(x == 'undetermined' for x in sdict.values()):
        logging.info('skipped line: ' + str(line) + '. no data.')
        pass
    else:
        ldict = {}
#log those sheet/line with no date of purchase, set value to none listed
        try:
            dop = sdict['dop'].to_pydatetime()
        except (AttributeError):
            logging.info('skipped line: ' + str(line) + ' have no date of purchase listed')
            dop = 'none listed'
        ldict['dop'] = dop

        try:
            dor = sdict['dor'].to_pydatetime()
        except (AttributeError):
            logging.info('skipped line: ' + str(line) + ' have not recieved')
            dor = 'not received'

        ldict['dor'] = dor
        ldict['desc'] = sdict['desc'].lower()
        ldict['fund'] = str(sdict['fund']).lower()

#flag non-standard purchaser
        ldict['pur'] = str(sdict['purchase']).lower()
        if str(sdict['purchase']).lower() not in refdict['purchasers']:
            logging.info(sdict['purchase'].lower() + ' not in references')
            print('Purchaser',str(sdict['purchase']).lower())

#log those lines with no cost, set value to none listed
        try:
            cost = float(sdict['cost'])
        except ValueError:
            logging.info('skipped line: ' + str(line) + ' have no line item cost listed')
            cost = 'none listed'
        ldict['cost'] = cost

#based on the 'user' determine the catagory
        user = sdict['user'].lower()
        if len(user.split('-')) == 2:
            ldict['cat'] = user.split('-')[0]
            ldict['end'] = user.split('-')[1]
        elif len(user.split('-')) == 1:
            ldict['cat'] = user.split('-')[0]
            if ldict['cat'] in ['office','student outreach','classroom support']:
                ldict['end'] = 'department'
            else:
                ldict['end'] = 'undetermined'


        ldict['vendor'] = sdict['vendor'].lower()
#probably should have this system account for different names of the same vendor

        if ldict['end'] == 'department':
            ldict['payee'] = 'department'
        elif ldict['cat'] in ['facility','instructional','recruitment','teaching labs']:
            ldict['payee'] = 'department'
        else:
            ldict['payee'] = 'undetermined'

        ldict['sub'] = 'undetermined'

#log those sheet/line with no date of purchase, set value to none listed
        try:
            doa = sdict['doa'].to_pydatetime()
        except (AttributeError):
            logging.info('skipped line: ' + str(line) + ' have no date of addition listed')
            doa = 'none listed'
        ldict['doa'] = doa

        databyline[line] = ldict


for method in refdict['purchasers']:
    purdict = {}
    for line in databyline:
#limit the output to those dates contained with in date range
        try:
            if edate >= databyline[line]['dop'] >= sdate:
                if databyline[line]['pur'] == method:
                    purdict[line] = databyline[line]
#if dop isn't a date error out, this needs to be updated to do something else here but for now whatever
        except (TypeError):
            pass
    mnpdf = npdf[(npdf['method'] == method)]
    mnpdf = mnpdf.drop(columns = ['method'])
    mnpdict = mnpdf.to_dict('index')
#lets not make files for methods that have no data
    if len(purdict) == 0:
        print(method + ' has no charges')
        logging.info(method + ' has no charges')
    else:
        opfilename = os.path.join(oploc,ts +'-'+'status_of-' + method+'.xlsx')
        workbookmkrorder(oporder,refdict['base'],opfilename,purdict,mnpdict)

logging.shutdown()
