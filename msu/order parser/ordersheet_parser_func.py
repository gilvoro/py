import csv
import datetime
import logging
import numpy as np
import os
import pandas as pd
import re
import xlsxwriter

#function to pull data from csv file to generate refrence dicts
def getref(fileloc):
    logging.info('setting up reference dictionary')
    rdict ={'vendors':{},'purchasers':[],'base':[]}
#walk through files, if we have on that doesn't relate to this part we will need to change things
    for file in os.listdir(fileloc):
#get the key to dictionary and the correct working object
        key = file.split('.')[0]
        wobj = rdict[key]
#open the file
        with open(os.path.join(fileloc,file), newline = '') as csvfile:
            unsorted_data = csv.reader(csvfile, delimiter = ',')
#if we are a file that we need regex go here
            if key in ['vendors']:
                for row in unsorted_data:
                    if row[0] == '':
                        pass
                    else:
#website will have no white space but people will want it so re should compile no white space
                        temp = re.compile("".join(row[0].split()))
                        wobj[row[0]] = temp
            elif key in ['base']:
                for row in unsorted_data:
                    if row == []:
                        wobj.append('')
                    else:
                        wobj.append(row[0])
            else:
                for row in unsorted_data:
                    if row[0] == '':
                        pass
                    else:
                        wobj.append(row[0])
    return rdict

#function to get the data out of a download sharepoint excel file
def dataretrieval(fileloc,dbloc,ts):
    logging.info('processing order sheet files')
#set the column headers
    columns = ['doa','desc','pnum','web','user','dop','purchase','fund','vendor','cost','dor']
#setup the base data fram and return dictionary
    rdf = pd.DataFrame(columns = columns)
    rdict = {}
#setup a way to make sure the most recent file is used.
    nts = datetime.datetime.strptime('1900-01-01','%Y-%m-%d')
    nf = 'None'
#if we have files already find the newest one and...
    if len(os.listdir(dbloc)) > 0:
        for f in os.listdir(dbloc):
            cts = datetime.datetime.strptime(f.split('.')[0],'%Y-%m-%d_%H%M%S')
            if cts > nts:
                nf = f
                nts = cts
#...and read and add that to the return datafram
        olddata = pd.read_excel(os.path.join(dbloc,f),usecols = 'B:L')
        rdf = pd.concat([rdf,olddata],ignore_index = True)

#get the correct file
    rawinput = pd.read_excel(fileloc,sheet_name=None,
                             header = None,
                             names = columns,
                             usecols='B:E,I,L:P,R',skiprows=[0,1,2,3])
#remove unecessary sheets
    rawinput.pop('data',None)
    rawinput.pop('template',None)
#fill in missing values add add it to the return datafram
    for df in rawinput:
        filled = rawinput[df].fillna('undetermined')
        rdf = pd.concat([rdf,filled],ignore_index = True)
#drop duplicates keeping the last added to the datafram
    rdf.drop_duplicates(subset = ['doa','desc','pnum','web','dop'],
                        keep = 'last',inplace = True)
#reset the index so as not drive myself mad
    rdf.reset_index(drop=True, inplace = True)
#export as record
    rdf.to_excel(os.path.join(dbloc,ts + '.xlsx'))
    rdict = rdf.to_dict('index')

    return rdict

#a function to generate excel reports
def workbookmkrorder(oporder,baselist,opname,purdict,npdict):
#start logging
    logging.info('Making output for ' + opname.split('\\')[-1])
#ranges to for data validation
    ranges = {'funds':[],'payee':[],'category':[],'sub category':[],'endusers':[]}
#make the work book
    workbook = xlsxwriter.Workbook(opname)
#setup all the formats
    default = workbook.add_format({'bottom':2,'right':1,'right_color':'#d3d3d3'})
    center = workbook.add_format({'align':'center','bottom':2,'right':1,'right_color':'#d3d3d3'})
    dt = workbook.add_format({'num_format':'yyyy-mm-dd','align':'center','bottom':2,
                              'right':1,'right_color':'#d3d3d3'})
    usd = workbook.add_format({'num_format':'[$$-409]#,##0.00','align':'center','bottom':2,
                               'right':1,'right_color':'#d3d3d3'})
    f1 = workbook.add_format({'bg_color':'#ffffd4'})
    hf = workbook.add_format({'bg_color':'#d3d3d3','bold':True,'align':'center','bottom':2,'right':1})
#add the sheets
    reportsheet = workbook.add_worksheet('report')
    basesheet = workbook.add_worksheet('validation_data')
#make the base sheet to be used a validation data
#as strings are added flag the cell where we start a new list
    curset = 'none'
    bn = 4
    basesheet.write(0,0,'binary')
    basesheet.write(1,0,'yes')
    basesheet.write(2,0,'no')
    for item in baselist:
        if item in ranges.keys():
#displace the current count by two because excel index at one, additional because we don't want the label
            ranges[item].append(bn+2)
            if curset in ranges.keys():
#diplace the count by minus one because we don't want the blank.
                ranges[curset].append(bn-1)
#change the curset to the new list
            curset = item
#add the string to the sheet
        basesheet.write(bn,0,item)
        bn += 1
#finish the last list
    ranges[curset].append(bn)
#the headers for the columns in the report
    opcols = ('date of purchase','description','vendor','cost','payee','fund','category','sub category',
              'end user','date of receipt','posted','invoice number')
#add the header to the reportsheet
    reportsheet.write_row(0,0,opcols,hf)
#add the data to the sheet based on type of data, going column to column, then row to row
    row = 1
#add those items that hadn't been posted as of the last report first
    for line in npdict:
        col = 0
        for item in opcols:
            if npdict[line][item] in ['none listed','not received']:
                reportsheet.write(row,col,npdict[line][item],center)
            elif item in ['date of purchase','date of receipt']:
                reportsheet.write_datetime(row,col,npdict[line][item],dt)
            elif item in ['description']:
                reportsheet.write(row,col,npdict[line][item],default)
            elif item in ['cost']:
                reportsheet.write_number(row,col,npdict[line][item],usd)
            else:
                reportsheet.write(row,col,npdict[line][item],center)
            col += 1
        row += 1
#add the new items
    for line in purdict:
        col = 0
        for item in oporder:
            if purdict[line][item] in ['none listed','not received']:
                reportsheet.write(row,col,purdict[line][item],center)
            elif item in ['dop','dor']:
                reportsheet.write_datetime(row,col,purdict[line][item],dt)
            elif item in ['desc']:
                reportsheet.write(row,col,purdict[line][item],default)
            elif item in ['cost']:
                reportsheet.write_number(row,col,purdict[line][item],usd)
            else:
                reportsheet.write(row,col,purdict[line][item],center)
            col +=1
        reportsheet.write(row,col,'yes',center)
        col += 1
        reportsheet.write(row,col,'',center)
        row += 1

#add in the conditional formats to add a yellow background to those items that need attention
    reportsheet.conditional_format(1,0,row-1,0,
                                   {'type':'cell','criteria':'==','value':'"none listed"','format':f1})
    reportsheet.conditional_format(1,2,row-1,2,
                                   {'type':'cell','criteria':'==','value':'"undetermined"','format':f1})
    reportsheet.conditional_format(1,3,row-1,3,
                                   {'type':'cell','criteria':'==','value':'"none listed"','format':f1})
    reportsheet.conditional_format(1,4,row-1,8,
                                   {'type':'cell','criteria':'==','value':'"undetermined"','format':f1})
    reportsheet.conditional_format(1,9,row-1,9,
                                   {'type':'cell','criteria':'==','value':'"not received"','format':f1})

#setup the validation data lists
    reportsheet.data_validation(1,10,row-1,10,{'validate':'list','source':'=validation_data!$A$2:$A$3'})

    plist = '=validation_data!$A$'+str(ranges['payee'][0])+':$A$'+str(ranges['payee'][1])
    reportsheet.data_validation(1,4,row-1,4,{'validate':'list','source':plist})

    flist = '=validation_data!$A$'+str(ranges['funds'][0])+':$A$'+str(ranges['funds'][1])
    reportsheet.data_validation(1,5,row-1,5,{'validate':'list','source':flist})

    clist = '=validation_data!$A$'+str(ranges['category'][0])+':$A$'+str(ranges['category'][1])
    reportsheet.data_validation(1,6,row-1,6,{'validate':'list','source':clist})

    sclist = '=validation_data!$A$'+str(ranges['sub category'][0])+':$A$'+str(ranges['sub category'][1])
    reportsheet.data_validation(1,7,row-1,7,{'validate':'list','source':sclist})

    elist = '=validation_data!$A$'+str(ranges['endusers'][0])+':$A$'+str(ranges['endusers'][1])
    reportsheet.data_validation(1,8,row-1,8,{'validate':'list','source':elist})

#set the column widths
    for x in range(0,len(oporder)+2):
        if x == 1:
            reportsheet.set_column(x,x,75)
        elif x == 2:
            reportsheet.set_column(x,x,20)
        elif x == 3:
            reportsheet.set_column(x,x,11)
        elif x == 5:
            reportsheet.set_column(x,x,23)
        elif x == 6:
            reportsheet.set_column(x,x,18)
        elif x == 7:
            reportsheet.set_column(x,x,25)
        elif x == 10:
            reportsheet.set_column(x,x,10)
        else:
            reportsheet.set_column(x,x,15)

#freeze the top row
    reportsheet.freeze_panes(1,0)

    workbook.close()
