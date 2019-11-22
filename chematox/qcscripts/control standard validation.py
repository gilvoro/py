import numpy as np
from scipy import stats
import datetime
import os
import csv
import re
import Tkinter, tkFileDialog
import math

name_dict = {'THC':'CAN','Doxylamine':'AH', 'Amphetamine':'AMP',
             'Carisoprodol':'AN', 'Diazepam':'Benzo','Hydroxyzine':'HXY'}
date = datetime.datetime.now().strftime('%Y-%m-%d')

#we set several RE to check various conditions. Namely what the run name is, if we are looking at a
#duetrated standard
isis = re.compile('[d|D]\d')
isfqc = re.compile('[f|F][q|Q][c|C]\-?\d+')
isisodate = re.compile('\d\d\d\d\-\d\d-\d\d')
isqan = re.compile('[q|Q][a|A]\-?\d+')

def qanumcheck(setname):
    whatqanum = raw_input('Please enter the QA-ticket number for the ' + setname + ' \nin the following manner: qa-###, or type quit to exit: ')
    qatest = isqan.search(whatqanum)
    if whatqanum.lower() == 'quit' or whatqanum.lower() == 'q' or whatqanum.lower() == 'exit':
        sys.exit()
    elif qatest:
        isnum = re.search('\d+',str("".join(qatest.group().split())).lower())
            #pull out the QA number
        qaname = 'qa-'+str("".join(isnum.group().split()))
    else:
        print'invalid QA number or incorrect format.'
        qaname = qanumcheck()

    return qaname

def lcmsdatasort(filename):
    sorted_data = {}
    with open (filename, 'rU') as csvfile:
        unsorted_data = csv.reader(csvfile, delimiter='\t')
#go row by row of the raw data
        for row in unsorted_data:
#pass by row that have no fields in them
            if len(row) < 1:
                pass
#if the line starts with Compound set compound name
#to whatever comes after the colon
            elif row[0].startswith('Compound'):
                compoundname = row[0].split(':')[1].strip()
                sorted_data.setdefault(compoundname, {})
#now we can by pass any line that only has one field
            elif len(row) < 2:
                pass
#whatever information is displayed on column names becomes a key list later
            elif row[0] == '' and row[1] != '':
                columnkeys = row[1:]
#if the row has sample information then we start building the dictionary
            elif row[0] != '' and row[1] != '':
                x = 0
                sorted_data[compoundname].setdefault(int(row[0]),{})
                while x < len(row):
                    if x == 0:
                        x += 1
                        pass
                    else:
                        sorted_data[compoundname][int(row[0])][columnkeys[x-1]]=row[x]
                        x += 1

            else:
                pass

    return sorted_data            

#setup and get the csv file
controlqanum = qanumcheck('controls')

root = Tkinter.Tk()
root.withdraw()

sorted_data = {}
print 'Please select a folder'
dirloc = tkFileDialog.askdirectory(initialdir = '',
                                    title ='Please select folder')

if dirloc == '':
    sys.exit()



#Sort the data
for item in os.listdir(dirloc):
    if not item.endswith('.txt'):
        print item + ' not a text file'
        pass
    else:
        fqctest = isfqc.search(item)
        if fqctest:
            #find the number within the fqctest
            isnum = re.search('\d+',str("".join(fqctest.group().split())).lower())
            #pull out the FQC number
            fqcname = 'fqc-'+str("".join(isnum.group().split()))
            #check to see if we have an isodate
            datetest = isisodate.search(item)
            if datetest:
            #if there is a date put the FQC number and date together
                fqccomp = fqcname + ' ' + str("".join(datetest.group().split()))
                sorted_data[fqccomp] = lcmsdatasort(os.path.join(dirloc, item))
            else:
                print 'no date present in ' + item
                pass
        else:
            print 'no fqc number present in ' + item

processed_data = {}
analyte_list = sorted(sorted_data.keys())
writeout = [['compiled on:',date],['','']]
initialdata = []
initialdatadict = {}
for fqc in sorted_data.keys():
    analyte_list = sorted_data[fqc].keys()
    for analyte in analyte_list:
        istest = isis.search(analyte)
        if istest:
            pass
        else:
            if analyte in name_dict.keys():
                assaytype = name_dict[analyte]
            processed_data.setdefault(analyte,{})
            analytedict = sorted_data[fqc][analyte]
            for sampleline in analytedict:
                if analytedict[sampleline]['Name'].lower().startswith('new control'):
                    if analyte == 'THC-COOH' and analytedict[sampleline]['Std. Conc'] == '130.0':
                        processed_data[analyte].setdefault(125,{'output':[],'measured':[]})
                        processed_data[analyte][125]['measured'].append(float(analytedict[sampleline]['ng/mL']))
                        sdev = (float(analytedict[sampleline]['ng/mL']) - 125)/125
                        sdev = round(sdev*100,1)
                        processed_data[analyte][float(analytedict[sampleline]['Std. Conc'])]['output'].append([fqc,'125.0 ng/mL',str(sdev)+'%'])                    
                    else:
                        processed_data[analyte].setdefault(float(analytedict[sampleline]['Std. Conc']),{'output':[],'measured':[]})
                        processed_data[analyte][float(analytedict[sampleline]['Std. Conc'])]['measured'].append(float(analytedict[sampleline]['ng/mL']))
                        sdev = (float(analytedict[sampleline]['ng/mL']) - float(analytedict[sampleline]['Std. Conc']))/float(analytedict[sampleline]['Std. Conc'])
                        sdev = round(sdev*100,1)
                        processed_data[analyte][float(analytedict[sampleline]['Std. Conc'])]['output'].append([fqc,
                                                                                                               analytedict[sampleline]['ng/mL']+' ng/mL',
                                                                                                               str(sdev)+'%'])
for analyte in sorted(processed_data.keys()):
    numberlevel = len(processed_data[analyte].keys())
    newanalytedict = processed_data[analyte]
    maxsamples = 0
    writeout.append([analyte,''])
    initialdatadict[analyte] = {}
    levellist = []
    for level in newanalytedict:
        raw_data = newanalytedict[level]['measured']
        if maxsamples < len(raw_data):
            maxsamples = len(raw_data)
        mean = np.mean(raw_data)
        stdev = np.std(raw_data)
        cv = (stdev/mean)*100
        dev = ((mean - level)/level)*100

        newanalytedict[level]['stats'] = {'target':['nominal',str(level)+' ng/mL'],
                                          'mean':['mean',str(round(mean,1))+' ng/mL'],
                                          'stdev':['stdev',str(round(stdev,1))+' ng/mL'],
                                          'cv':['%cv',str(round(cv,2))+'%'],
                                          'dev':['%dev',str(round(dev,2))+'%']}
        
        initialdatadict[analyte][level] = {'mean':str(round(mean,2)),
                                          'stdev':str(round(stdev,2))}

    for level in sorted(newanalytedict.keys()):
        levellist.append('control at:')
        levellist.append(str(level)+'ng/mL')
        levellist.append('')
        levellist.append('')
        x = len(newanalytedict[level]['output'])
        if maxsamples > x:
            while x < maxsamples:
                newanalytedict[level]['output'].append(['','',''])
                x += 1 

    writeout.append(levellist)
    writeout.append(['fqc/date','measurement','%dev','']*numberlevel)

    y = 0
    while maxsamples > y:
        templist = []
        for level in sorted(newanalytedict.keys()):
            templist = templist + (newanalytedict[level]['output'][y]) + ['']
        writeout.append(templist)
        y += 1

    writeout.append(['',''])
    
    for key in ['target','mean','stdev','cv','dev']:
        templist = []
        for level in sorted(newanalytedict.keys()):
            templist = templist + newanalytedict[level]['stats'][key]+['','']
        writeout.append(templist)

    writeout.append(['',''])
    writeout.append(['',''])

for analyte in sorted(initialdatadict.keys()):
    tempinidata = [analyte.lower()]
    controlnum = 1
    for level in sorted(initialdatadict[analyte].keys()):
        tempinidata.append('control ' + str(controlnum))
        tempinidata = tempinidata + [initialdatadict[analyte][level]['mean'],
                                     initialdatadict[analyte][level]['stdev']]
        controlnum += 1

    initialdata.append(tempinidata)

writeout.insert(0,[controlqanum, 'controls for:', assaytype])          
        
assay_name = assaytype + ' ' + controlqanum + ' ' + date + '.csv'
assay_record = os.path.join(dirloc, assay_name)

initial_record = os.path.join(dirloc, 'initial data.csv')            


with open(assay_record,'wb')as csvfile:
    wo= csv.writer(csvfile)
    for item in writeout:
        wo.writerow(item)

with open(initial_record, 'wb') as csvfile:
    wo= csv.writer(csvfile)
    for item in initialdata:
        wo.writerow(item)
