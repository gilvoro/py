# -*- coding: cp1252 -*-
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
desktop = os.path.expanduser('~\Desktop')
date = datetime.datetime.now().strftime('%Y-%m-%d')

#we set several RE to check various conditions. Namely what the run name is, if we are looking at a
#duetrated standard
isis = re.compile('[d|D]\d')
isdate = re.compile('\d\d\d\d-\d\d-\d\d')

outputdir = 'C://scriptfiles//neat solution stats'

#a function to return a the number of items for 90%, 75%, 50%
def checklen(item):
    fulllen = len(item)
    returnlist = [0]
    returnlist.append(fulllen-int(round(0.9*fulllen)))
    returnlist.append(fulllen-int(round(0.75*fulllen)))
    returnlist.append(fulllen-int(round(0.5*fulllen)))
    if fulllen > 9:
        returnlist.append(fulllen-10)

    return returnlist

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

#simple function to check length of a number and round according
def rounder(num):
    if 0 == num:
        return 0.00
    elif 1 > abs(num):
        dist = abs(int(math.log10(abs(num))))+ 2
        return round(num,dist)
    elif 10 > abs(num):
        return round(num,2)
    elif 100 > abs(num):
        return round(num,1)
    else:
        return round(num)
            

#setup and get the csv file
root = Tkinter.Tk()
root.withdraw()
#see if this data will be added to the neat solution IS record
add = raw_input('Add record data? (y/n): ')
if add.lower() == 'y' or add.lower() == 'yes':
    commit = True
else:
    commit = False

#work out what instrument we are working on
whatinstrument = raw_input('What Instrument? ((d)affy/(m)arvin): ')
if whatinstrument.lower() == 'd' or whatinstrument.lower() == 'daffy':
    instrument = 'daffy'
    record_dir = 'R://labtools//jimscripts//neat injection records//'
else:
    instrument = 'marvin'
    record_dir = 'Z://labtools//jimscripts//neat injection records//'


print 'Please select text file'
fileloc = tkFileDialog.askopenfilename(defaultextension = '.txt',
                                       filetypes = [('TXT Files','.txt')],
                                       initialdir = desktop,
                                       title ='Please select text file')

if fileloc == '':
    sys.exit()

#Sort the data
sorted_data = lcmsdatasort(fileloc)

metric_data = {}
#sort the keys so we the lines in order
analyte_list = sorted(sorted_data.keys())

for analyte in analyte_list:
        if analyte in name_dict.keys():
            assayname = name_dict[analyte]
#test for internal standard
        istest = isis.search(analyte)
#if its duetrated we don't want it
        if istest:
            pass
#if its not a duetrated analyte we information out of the list
        else:
#update the metric_data with the analyte
            metric_data.setdefault(analyte,{'rt':[],'area':[],'isarea':[],
                                            'ionratio':[], 'rr':[]})
#setup a seris of list that point to the dict and will be appended with the
#relvant data
            rt_list = metric_data[analyte]['rt']
            area_list = metric_data[analyte]['area']
            isarea_list = metric_data[analyte]['isarea']
            ionratio_list = metric_data[analyte]['ionratio']
            rr_list = metric_data[analyte]['rr']
            
            analyte_dict = sorted_data[analyte]
            line_list = sorted(analyte_dict.keys())
#if it is a neat solution injection I want the following data.
            for line in line_list:
                if analyte_dict[line]['Name'].startswith('Neat Solution'):
                    rt_list.append(float(analyte_dict[line]['RT']))
                    area_list.append(float(analyte_dict[line]['Area']))
                    isarea_list.append(float(analyte_dict[line]['IS Area']))
                    try:
                        ionratio_list.append(float(analyte_dict[line]['1º Ratio Actual']))
                    except:
                        ionratio_list.append(float(analyte_dict[line]['1º Ratio (Act)']))
                    rr_list.append(float(analyte_dict[line]['Response']))

                else:
                    pass
#go look for old data
assay_record = os.path.join(record_dir,instrument,assayname + ' neat injection record.csv')
record_dict = {}
current_analyte = ''
haverecord = True
#try to open if the file
try:
    with open (assay_record, 'rU') as csvfile:
        record_data = csv.reader(csvfile, delimiter=',')
        for row in record_data:
            if row[0] == 'analyte':
                current_analyte = row[1]
                record_dict.setdefault(current_analyte,{})
#whatever information is displayed on column names becomes a key list later
            elif row[0] == '' and row[1] != '':
                columnkeys = row[1:]
#if the row has sample information then we start building the dictionary                
            elif isdate.match(row[0]):
                x = 0
                record_dict[current_analyte].setdefault(row[0],{})
#iterate over the row, add each cell by the corresponding column header
                while x < len(row):
                    if x == 0:
                        x += 1
                        pass
                    else:
                        record_dict[current_analyte][row[0]][columnkeys[x-1]]=row[x]
                        x += 1

            else:
                pass     
#if no record is found says so
except:
    print 'No Record found for ' + assayname + ' neat injection'
    haverecord = False

                
    
#
writeoutlist = [['Neat Solution Stats',''],['Compiled',date,'at ' + datetime.datetime.now().strftime('%H:%M:%S')],['','']]

#get the keys in alphabetical order
analyte_list_2 = sorted(metric_data.keys())

for analyte in analyte_list_2:
    analyte_dict_2 = metric_data[analyte]
    writeoutlist = writeoutlist +[[analyte,''],['','RT','RT','RT',
                                                '','Area','Area','Area',
                                                '','IS Area','IS Area','IS Area',
                                                '','Response','Response','Response',
                                                '','Ratio','Ratio','Ratio'],
                                              ['','Most Common','Range','# more -/+ 0.01',
                                               '','Mean','St. Dev','%CV',
                                               '','Mean','St. Dev','%CV',
                                               '','Mean','St. Dev','%CV',
                                               '','Mean','St. Dev','%CV',]]

#setup the columns I want to pull data from        
    keylist = ['area','isarea','rr','ionratio']

    
    rt_data = analyte_dict_2['rt']
    numitem = checklen(rt_data)

#setup the lists to hold the calculations
    hundred_list = ['100% injections']
    ninety_list = ['Last 90% injections']
    quarter_list = ['Last 75% injections']
    half_list = ['Last 50% injections']
    lastten = ['Last 10 injections']

#....and a dictionary to hold the lists
    op_list_dict = {0:hundred_list,1:ninety_list,2:quarter_list,3:half_list,4:lastten}

#rt are done differently so they are called seperately
    rt_data = analyte_dict_2['rt']
    numitem = checklen(rt_data)
#if 10 injections or or more run add set lasttencheck to true
    if len(numitem) == 5:
        lasttencheck = True
    else:
        lasttencheck = False
        
    y = 0
    while y < len(numitem):
#call the correct list using the index
        temp_list = op_list_dict[y]
#slice the list to only included the correct portion 
        calc_list = np.asarray(rt_data[numitem[y]:])
#find the mode of the RT
        most_rt = float(stats.mode(calc_list,axis=None)[0])
        low_rt = np.amin(calc_list)
        high_rt = np.amax(calc_list)
        x = 0
#determine the number of samples with a RT great the 0.01 away from the mode
        for value in calc_list:
            if round(most_rt-0.01,2) <= value <= round(most_rt+0.01,2):
                pass
            else:
                x += 1
        temp_list.append(str(most_rt))
        temp_list.append(str(low_rt) + '-' + str(high_rt))
        temp_list.append(str(x))
        temp_list.append('')
        y += 1


#the other parameter are handle the same way as each other
    for key in keylist:
        data = analyte_dict_2[key]
        numitem = checklen(data)

        y = 0
        while y < len(numitem):
            temp_list = op_list_dict[y]
            calc_list = np.asarray(data[numitem[y]:])
            mean = np.mean(calc_list)
            stdev = np.std(calc_list)

            cv = (stdev/mean)*100
            temp_list.append(str(rounder(mean)))
            temp_list.append(str(rounder(stdev)))
            temp_list.append(str(rounder(cv))+'%')
            temp_list.append('')
            y += 1

    if lasttencheck:
        opkeys = [0,1,2,3,4]
    else:
        opkeys = [0,1,2,3]
        

    for listkey in opkeys:
        writeoutlist.append(op_list_dict[listkey])
        
    if haverecord:
        commonrt = []
        outrt = []
        analytearea = []
        isarea = []
        response = []
        ratio = []
        analyte_record = record_dict[analyte]
        lastfive = sorted(analyte_record.keys())[-5:]
        
        for item in lastfive:
            commonrt.append(float(analyte_record[item]['common rt']))
            outrt.append(float(analyte_record[item]['out rt']))
            analytearea.append(float(analyte_record[item]['mean area']))
            isarea.append(float(analyte_record[item]['mean is']))
            response.append(float(analyte_record[item]['mean response']))
            ratio.append(float(analyte_record[item]['mean ratio']))
        
        
        numberofrecords = 'Mean of Last ' + str(len(lastfive)) + ' Assays'
        writeoutlist.append([numberofrecords,str(float(stats.mode(commonrt,axis=None)[0])),'',str(np.mean(outrt)),
                            '',str(rounder(np.mean(analytearea))),'','','',
                            str(rounder(np.mean(isarea))),'','','',
                            str(rounder(np.mean(response))),'','','',
                            str(rounder(np.mean(ratio)))])
                        
    if commit:
        analyte_record = record_dict.setdefault(analyte,{})
        rdata = op_list_dict[3]
        analyte_record[date] = {'common rt':rdata[1],'rt range':rdata[2],'out rt':rdata[3],
                                'mean area':rdata[5],'stdev area':rdata[6],'%cv area':rdata[7],
                                'mean is':rdata[9],'stdev is':rdata[10],'%cv is':rdata[11],
                                'mean response':rdata[13],'stdev response':rdata[14], '%cv response':rdata[15],
                                'mean ratio':rdata[17],'stdev ratio':rdata[18],'%cv ratio':rdata[19]}
                            
    writeoutlist.append(['',''])
            
        
outputname = 'neat solution ' + assayname + ' ' + datetime.datetime.now().strftime('%Y-%m-%d %H%M%S') + '.csv'
outputfile = os.path.join(outputdir,outputname)

with open(outputfile,'wb')as csvfile:
    wo = csv.writer(csvfile)
    for item in writeoutlist:
        wo.writerow(item)

recordheader = ['common rt', 'rt range', 'out rt', 'mean area', 'stdev area', '%cv area',
                'mean is', 'stdev is', '%cv is', 'mean response', 'stdev response', '%cv response',
                'mean ratio', 'stdev ratio', '%cv ratio']

record_output = [['Neat Solution Record',''],['Compiled',date,'at ' + datetime.datetime.now().strftime('%H:%M:%S')],
                 ['','']]

for analyte in analyte_list_2:
    record_output.append(['analyte',analyte])
    record_output.append(['']+recordheader)
    for date in sorted(record_dict[analyte].keys()):
        templist = [date]
        for item in recordheader:
            templist.append(record_dict[analyte][date][item])
        record_output.append(templist)
    record_output.append(['',''])
        

with open(assay_record,'wb')as csvfile:
    wo= csv.writer(csvfile)
    for item in record_output:
        print 'writing a row'
        wo.writerow(item)

os.startfile(outputdir)
