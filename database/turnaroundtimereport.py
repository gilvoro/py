import numpy as np
import os
import sys
import re
import scipy
import csv
import datetime
import psycopg2
import psycopg2.extensions

#want the date in a specific format
isdate = re.compile('\d\d\d\d-\d\d')

#a function to get a date and check to make sure it valid for the use on this script
def getdate(text):
    entereddate = raw_input(text)
    datetest = isdate.match(entereddate)
    if entereddate.lower() == 'quit' or entereddate.lower() == 'q' or entereddate.lower() == 'exit':
        sys.exit()
    elif datetest:
        testyear,testmonth = entereddate.split('-')
        if 0 >= int(testyear):
            print 'Date outside range. Please enter a date between 2013-01 and ' + datetime.datetime.today().strftime('%Y-%m')
            getdate('Please enter in the following format YYYY-MM: ')
        elif not 0 <= int(testmonth) <= 12:
            print 'Not a valid month.  Please enter a month between 01-12'
            getdate('Please enter in the following format YYYY-MM: ')
        if datetime.datetime(2013,01,01) <= datetime.datetime(int(testyear), int(testmonth), 01) <= datetime.datetime.today():
            return testyear, testmonth
        else:
            print 'Date outside range. Please enter a date between 2013-01 and ' + datetime.datetime.today().strftime('%Y-%m')
            getdate('Please enter in the following format YYYY-MM: ')
    else:
        print 'Date not in YYYY-MM format'
        getdate('Please enter in the following format YYYY-MM: ')
        
#get the year and month for the report
testyear, testmonth = getdate('Please enter the year and month you would like a report for \nor type quit to exit.\nPlease enter in the following format YYYY-MM: ')

#from jkominek/chematox/display.py
conn = psycopg2.connect("host=lims-db.chematox.com dbname=chematox user=reader password=immunoassay")
c = conn.cursor()
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, c)
c.execute("set application_name = 'forensic dashboard'")
conn.commit()

#the sql queary
c.execute("""select t.id, r.id, ss.id, ss.created, r.certified, t.type, tt.analyte, tt.method, tt.submethod from requests r, tests t, samplesets ss, testtypes tt where extract(year from r.certified)= """ +testyear+ """ and extract(month from r.certified)= """ +testmonth+ """ and r.id = t.request and r.sample_set = ss.id and t.type = tt.id""")

sqldata = {}
for test, request, sampleset, creation, certified, testtype, analyte, method, submethod in c:
#collect the request related data....
    sqldata.setdefault(request, {'sampleset':sampleset,
                                 'creation date':creation,
                                 'certified':certified,
                                 'tests':{}})
#the test specific data
    sqldata[request]['tests'].setdefault(test,[testtype, method, submethod,analyte.encode('ascii','ignore')])
    
#a dictionary that list all of the analytes in an assay
assaydict = {'bac':[393],
             'gc/ms scans':[397],
             'ah':[691,694,692],
             'amp':[666,665,654,667],
             'an':[598,597],
             'benzo':[610,584,585,583,581,590,580,582,589,586],
             'benzo scans':[588],
             'can':[570,571,688,685,682],
             'alkaline':[155,147,72,493,115,84,169,50,290,71,433,47,158,208,111,465,309,140,55,341,46,58,294,179,152,43],
             'opiates/oxys':[123,339,305,320,356,366,365],
             'other volatiles':[392,490,497]}

#lists that contain the assays on differnet types instruments
methoddict = {'GC/MS':['alkaline','opiates/oxys','gc/ms scans'],
              'LC-MS/MS':['ah','amp','an','benzo','can'],
              'GCFID':['bac']}

#other list used during the script
assaycountkeys = ['GCFID','elisa','GC/MS','LC-MS/MS','other']
outputkeys = ['total','bac','bac_e','bac_e_c','bac_e_c+','other']
breakdownkeys = ['dsfa','bac_e_g', 'bac_e_g+','bac_e_l','bac_e_l+','bac_e_gl','opiates']
#the list for undefined tests
ucalist = []

sorted_data = {}
#get desired data out of the sqldata
for entry in sqldata.keys():
    sampledict = sorted_data.setdefault(entry,
                                        {'begin':sqldata[entry]['creation date'],
                                        'end':sqldata[entry]['certified'],
                                        'delta':(sqldata[entry]['certified']-sqldata[entry]['creation date']).days,
                                        'assaycount':{'elisa':0,
                                                      'GCFID':0,
                                                      'LC-MS/MS':0,
                                                      'GC/MS':0,
                                                      'other':0},
                                        'assays':[]})
#add lines based on the method, and update the assay count and the assay list
    for test in sqldata[entry]['tests']:
        testlist = sqldata[entry]['tests'][test]
        addedcheck = 0
#special case for benzo scans
        if testlist[0] == 588:
            if not 'benzo' in sampledict['assays']:
                sampledict['assays'].append('benzo')
                sampledict['assays'].append('benzo scans')
                sampledict['assaycount']['LC-MS/MS'] += 1
            else:
                sampledict['assays'].append('benzo scans')
            addedcheck = 1
#currently not collecting data based on the different types of ELISA, so just listing it once
#and updateding the count#ELISA 
        elif testlist[1] == 'ELISA':
            if not 'elisa' in sampledict['assays']:
                sampledict['assays'].append('elisa')
            sampledict['assaycount']['elisa'] += 1
            addedcheck = 1
#for the other items check to see if the method is a valid key in the methoddict
        elif testlist[1] in methoddict.keys():
#check each assay in the methoddict...
            for assay in methoddict[testlist[1]]:
#to see if the test is listed
                if testlist[0] in assaydict[assay]:
#if we find the test in the assay check to see if the assay has been listed if it hasn't listed it and
#and increase the number of tests done
                    if not assay in sampledict['assays']:
                        sampledict['assays'].append(assay)
                        sampledict['assaycount'][testlist[1]] += 1
#the indicate we have added the check
                    addedcheck = 1
#after going through the list if we still haven't added, check to see if we an "other" test
#if we don't then added it.
            if addedcheck == 0:
                if not 'other ' + testlist[1] in sampledict['assays']:
                    sampledict['assays'].append('other ' + testlist[1])
                sampledict['assaycount'][testlist[1]] += 1
#add the unfound test to the ucalist
                ucalist.append(tuple(testlist))
#if the assay isn't found, add check and add other to the assay list, increase count and update UCAlist
        else:
            if not 'other' in sampledict['assays']:
                sampledict['assays'].append('other')
            sampledict['assaycount']['other'] += 1
            ucalist.append(tuple(testlist))

#dict for the human readable output            
outputdict = {'total':['All Samples'],
              'bac':['Blood Alcohol Only'],
              'bac_e':['Blood Alcohol and No Confirmations'],
              'bac_e_g':['One GC/MS Assay'],
              'bac_e_g+':['Multiple GC/MS Assay'],
              'bac_e_l':['One LC-MS/MS Assay'],
              'bac_e_l+':['Multiple LC-MS/MS Assay'],
              'bac_e_c':['One Confirmation'],
              'bac_e_c+':['Multiple Confirmations'],
              'bac_e_gl':['At least one GC/MS and one LC-MS/MS Assay'],
              'dsfa':['DSFA cases'],
              'opiates':['Had Opiate/Oxy Assay'],
              'other':['Had Some Other Test']}

#this probably could be an output of the getdate
firstdate = testyear + '-' + testmonth
over120 = []
                                 
for sample in sorted_data:
    countlist = []
    sampledict = sorted_data[sample]
#if its a DSFA case exclude it
    if 'gc/ms scans' in sampledict['assays'] and 'benzo scans' in sampledict['assays']:
        outputdict['dsfa'].append(sampledict['delta'])
#if the sample has delta 120 or more exclude it from the totals
    elif sampledict['delta'] > 120:
        over120.append(sample)
    else:
        outputdict['total'].append(sampledict['delta'])
#if it has opiates as an assay we track in addition
        if 'opiates/oxys' in sampledict['assays']:
            outputdict['opiates'].append(sampledict['delta'])
        for key in assaycountkeys:
            countlist.append(sampledict['assaycount'][key])
#if we have another random test I want it out of the group as a whole.
        if 0 < countlist[4]:
            outputdict['other'].append(sampledict['delta'])

#if we have a positive bac
        elif 0 < countlist[0]:
#and no other methods add the delta to bac
            if np.sum(countlist) == 1:
                outputdict['bac'].append(sampledict['delta'])
#or no positive elisa add to the bac_e
            elif 0 < countlist[1]:
                if np.sum(countlist[2:4]) == 0:
                    outputdict['bac_e'].append(sampledict['delta'])
#if we have just one gc test add it to bac_e_g and bac_e_c
                elif countlist[2] == 1 and countlist[3] == 0:
                        outputdict['bac_e_g'].append(sampledict['delta'])
                        outputdict['bac_e_c'].append(sampledict['delta'])
#if we more then one gc test add it to bac_e_g+ and bac_e_c+
                elif countlist[2] > 1 and countlist[3] == 0:
                        outputdict['bac_e_g+'].append(sampledict['delta'])
                        outputdict['bac_e_c+'].append(sampledict['delta'])
#if we have just one lc test add it to bac_e_l and bac_e_c
                elif countlist[3] == 1 and countlist[2] == 0:
                        outputdict['bac_e_l'].append(sampledict['delta'])
                        outputdict['bac_e_c'].append(sampledict['delta'])
#if we more then one lc test add it to bac_e_l+ and bac_e_c+
                elif countlist[3] > 1 and countlist[2] == 0:
                        outputdict['bac_e_l+'].append(sampledict['delta'])
                        outputdict['bac_e_c+'].append(sampledict['delta'])
#if we have a least one gc and at least one lc add it to the bac_e_gl and bac_e_c+
                elif countlist[2] != 0 and countlist[3] != 0:
                        outputdict['bac_e_c+'].append(sampledict['delta'])
                        outputdict['bac_e_gl'].append(sampledict['delta'])

#if we have no bac
        elif 0 == countlist[0]:
#or no positive elisa add to the bac_e
            if 0 < countlist[1]:
                if np.sum(countlist[2:4]) == 0:
                    outputdict['bac_e'].append(sampledict['delta'])
#if we have just one gc test add it to bac_e_g and bac_e_c
                elif countlist[2] == 1 and countlist[3] == 0:
                        outputdict['bac_e_g'].append(sampledict['delta'])
                        outputdict['bac_e_c'].append(sampledict['delta'])
#if we more then one gc test add it to bac_e_g+ and bac_e_c+
                elif countlist[2] > 1 and countlist[3] == 0:
                        outputdict['bac_e_g+'].append(sampledict['delta'])
                        outputdict['bac_e_c+'].append(sampledict['delta'])
#if we have just one lc test add it to bac_e_l and bac_e_c                        
                elif countlist[3] == 1 and countlist[2] == 0:
                        outputdict['bac_e_g'].append(sampledict['delta'])
                        outputdict['bac_e_c'].append(sampledict['delta'])
#if we more then one lc test add it to bac_e_l+ and bac_e_c+
                elif countlist[3] > 1 and countlist[2] == 0:
                        outputdict['bac_e_g+'].append(sampledict['delta'])
                        outputdict['bac_e_c+'].append(sampledict['delta'])
#if we have a least one gc and at least one lc add it to the bac_e_gl and bac_e_c+                        
                elif countlist[2] != 0 and countlist[3] != 0:
                        outputdict['bac_e_c+'].append(sampledict['delta'])
                        outputdict['bac_e_gl'].append(sampledict['delta'])


writeout = [['Turn Around Times',firstdate],
            ['Totals',''],
            ['Types of test','#samples','Mean','Median','Shortest','Longest','95% completed']]

#go through the output dict and get stats.  If the list contains no entries just n/a it
for key in outputkeys:
    if outputdict[key][1:]:
        temparray = np.asarray(outputdict[key][1:])
        total = len(temparray)
        mean = np.mean(temparray)
        median = np.median(temparray)
        minnum = np.amin(temparray)
        maxnum = np.amax(temparray)
        per = np.percentile(temparray,95)
        writeout.append([outputdict[key][0],
                         str(total) + ' samples',
                         str(round(mean))+' days',
                         str(round(median))+' days',
                         str(round(minnum))+' days',
                         str(round(maxnum))+' days',
                         str(round(per))+' days'])

    else:
        writeout.append([outputdict[key][0],'0', 'n/a','n/a','n/a','n/a','n/a'])

writeout.append(['',''])
writeout.append(['Break down by type',''])
writeout.append(['Types of test','#samples','Mean','Median','Shortest','Longest','95% completed'])

#go thru the breakdownkey and collect stats, if there aren't any entries n/a the rest             
for key in breakdownkeys:
    if outputdict[key][1:]:
        temparray = np.asarray(outputdict[key][1:])
        total = len(temparray)
        mean = np.mean(temparray)
        median = np.median(temparray)
        minnum = np.amin(temparray)
        maxnum = np.amax(temparray)
        per = np.percentile(temparray,95)
        writeout.append([outputdict[key][0],
                         str(total) + ' samples',
                         str(round(mean))+' days',
                         str(round(median))+' days',
                         str(round(minnum))+' days',
                         str(round(maxnum))+' days',
                         str(round(per))+' days'])
    else:
        writeout.append([outputdict[key][0],'0', 'n/a','n/a','n/a','n/a','n/a'])

#add the samples that took longer then 120 days
writeout.append(['',''])
writeout.append(['Total number of samples longer then 120 days',str(len(over120)) + ' samples'])
writeout.append(['Samples that took more then 120 days:',''])
for sample in over120:
    writeout.append([sample,''])
#add thos enteries that were on the ucalist
writeout.append(['',''])
writeout.append(['The following tests','were not grouped'])
setuca = set(ucalist)
for item in setuca:
    writeout.append(item)

#output the file to the desktop on windows
filename = 'Turn around times for ' + firstdate +'.csv'
outputfile = os.path.join(os.path.join(os.environ["HOMEPATH"],"Desktop"), filename)

with open(outputfile, 'wb') as op:
    wo = csv.writer(op)
    for row in writeout:
        wo.writerow(row)                    
    
    
    
