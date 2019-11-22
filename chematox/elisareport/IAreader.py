import csv
import os
import datetime
import re
import sys

#a dict to contain the conversion from the plate infomation to analyte
convdict = {'209':'Amphetamine/MDA',
           '210':'Barbiturates',
           '214':'Benzodiazepines',
           '236':'Buprenorphine',
           '205':'Cannabinoids',
           '231':'Carisoprodol',
           '206':'Cocaine Metabolite',
           '218':'Fentanyl',
           '240':'Ketamine',
           '232':'Methadone',
           '211':'Methamphetamine/MDMA',
           '207':'Opiates',
           '221B':'Oxycodone',
           '225':'Tramadol',
           '233':'Zolpidem'}

#couple of to check file date
isdate = re.compile('\d\d/\d\d/\d\d\d\d')
#dictionary to hold inventory data
inventory_data= {}

def IAreader(filelist,rundate):
    unsorted_data = {}
#take the files list and process each file individually
    for item in filelist:
        with open(item, 'rU') as csvfile:
            raw_data = csv.reader(csvfile)
            rownum = 0
            for row in raw_data:
#row number is just used to determine where any problems is
                rownum += 1
#if there is no data on the line skip it
                if row[0] == '':
                    pass
#if we get a line with the date information on it great we will double check that it matches the run date
                elif row[0].startswith('Date of measurement'):
#find the date in the string
                    finddate = isdate.search(row[0])
                    if finddate:
                        checkdate = datetime.datetime.strptime(finddate.group(),'%m/%d/%Y').date()
#compare it to the rundate, if they don't match kill the program.
                        if rundate != checkdate:
                            print 'Entered date:', rundate, 'Run date:', checkdate
                            print os.path.basename(os.path.normpath(item)) + ' was not run on the same date as the run date entered.  \nPlease fix issue and rerun program'
                            close = raw_input('Please press enter to close program')
                            sys.exit()
                        else:
                            pass
#otherwise attempt to added it to the dictionary
                else:
                    try:
                        analytedict = unsorted_data.setdefault(convdict[row[0]],{})
                        analytedict[row[1].lower()] = {'abs':float(row[2]),'ratio':float(row[3])}
                        inventory_data.setdefault(convdict[row[0]],{'catalognum':row[0], 'wellcount':0})
                        inventory_data[convdict[row[0]]]['wellcount'] += 1
#if something is wonky with the row catch the error, print it then move on.
                    except Exception as e:
                        print 'Error encoutnered, traceback reads:'
                        print e
                        print 'not including data from ' + item + ' row ' + str(rownum)

    return unsorted_data, inventory_data
