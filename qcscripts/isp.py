import math
import numpy as np
from scipy import stats

import csv
import datetime
import os
import re
import sys
import Tkinter, tkFileDialog

from lcmsdatasort import *
from is_grapher import *

#setup varible for the session
desktop = os.path.expanduser('~\Desktop')
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
outputloc = r'//admin.chematox.com/public/labtools/jimscripts/is plots'
#outputloc = 'C://Users//James//Desktop//Test'

#setup lists and dicts for the session
analytelist = []
datadict = {}
validassays = {'THC':'CAN','Doxylamine':'AH', 'Amphetamine':'AMP',
             'Carisoprodol':'AN', 'Diazepam':'Benzo'}

assaytype = ['unknown']

#setup re for later use
isis = re.compile('[d|D]\d')


fqc = raw_input('Please enter the FQC-ticket number for the assay: ')
#get the csv file
root = Tkinter.Tk()
root.withdraw()
print 'Please select file'
fileloc = tkFileDialog.askopenfilename(defaultextension = '.txt',
                                       filetypes = [('Text File','.txt'),
                                       		    ('CSV File','.csv')],
                                       initialdir = desktop,
                                       title ='Please select file')

#if you don't give me a file I am done.
if fileloc == '':
    sys.exit()

#take the data and put into a dict via lcmsdatasort
raw_data = lcmsdatasort(fileloc)

#go through the data....
for analyte in sorted(raw_data.keys()):
    if analyte in validassays.keys():
        assaytype = validassays[analyte]
        
    istest = isis.search(analyte)
#pull out the IS
    if istest:
        analytelist.append(analyte)
        analytedict = raw_data[analyte]
        tempdatadict =datadict.setdefault(analyte,{'values':[],
                                                   'lines':[],
                                                   'names':[],
                                                   'length':len(analytedict.keys())})

#convert the line numbers from strings to ints
        linelist = sorted(map(int,analytedict.keys()))

#add only those values that are values, and add there lines to a seperate list
        for line in linelist:
            if analytedict[str(line)]['Area'] != '':
                tempdatadict['values'].append(int(analytedict[str(line)]['Area']))
                tempdatadict['names'].append(analytedict[str(line)]['Name'])
                tempdatadict['lines'].append(line)
            else:
                pass

    else:
        pass

analytepath = os.path.join(outputloc,assaytype)
if not os.path.exists(analytepath):
    os.makedirs(analytepath)

fqcpath = os.path.join(analytepath, fqc)
if not os.path.exists(fqcpath):
    os.makedirs(fqcpath)

for analyte in analytelist:
    print 'Working on ' + analyte
    outputlist = [[analyte,fqc],['','']]
    valuelist = datadict[analyte]['values']
    mean = round(np.mean(valuelist))
    stdev = round(np.std(valuelist))
    a,m,r,p,err = stats.linregress(datadict[analyte]['lines'],valuelist)
    datadict[analyte]['stats'] = [mean,stdev,a,m,r]
    outputlist.append(['mean:',mean,'stdev:',stdev])

    for indice in range(0,len(datadict[analyte]['names']),1):
        if indice%50 == 0:
            outputlist.append(['Name','Raw Area','%Dev from Mean','Stdev from Mean'])
        templist = [datadict[analyte]['names'][indice]]
        rawarea = datadict[analyte]['values'][indice]
        templist.append(rawarea)
        perdev = round(((rawarea-mean)/mean)*100,1)
        templist.append(str(perdev)+'%')
        stdevfrom = round((rawarea-mean)/stdev,1)
        templist.append(stdevfrom)
        outputlist.append(templist)
    
    filename = os.path.join(fqcpath,analyte + ' ' + timestamp + '.csv')
    graphfilename = os.path.join(fqcpath,analyte + '-' + 'graph ' + timestamp + '.png')
    is_plot(analyte, graphfilename, datadict[analyte]['lines'], datadict[analyte]['values'],datadict[analyte]['stats'],datadict[analyte]['length'])

    with open(filename, 'wb') as op:
        wo = csv.writer(op)
        for row in outputlist:
            wo.writerow(row)

