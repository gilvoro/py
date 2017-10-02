import csv
import numpy as np
import os
import scipy
import Tkinter, tkFileDialog
import datetime
import dateutil.parser

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

#lists that contain the assays on differnet instruments
gcassays = ['alkaline','opiates/oxys','gc/ms scans']
lcassays = ['ah','amp','an','benzo','can']
gcfidassays = ['bac']

assaycountkeys = ['fid','elisa','gc','lc','other']
outputkeys = ['total','bac','bac_e','bac_e_c','bac_e_c+','other']
breakdownkeys = ['dsfa','bac_e_g', 'bac_e_g+','bac_e_l','bac_e_l+','bac_e_gl','opiates']

ucalist = []
months = []
#setup and get the CSV file
root = Tkinter.Tk()
root.withdraw()
fileloc = tkFileDialog.askopenfilename(defaultextension = '.csv',
                                       filetypes = [('CSV File','.csv'),('All Files','*')],
                                       title ='Please select csv file')

#if a file is chosen open and process data
if fileloc:
    sorted_data = {}
    with open (fileloc, 'rU') as cf:
        unsorted_data = csv.reader(cf)
        for row in unsorted_data:
#skip rows that have no data
            if 1 > len(row):
                pass
#skip the title row or no data rows
            elif row[0] == 'id' or row[0] == '':
                pass
#pull out the created and closed dates, calculate the delta, setup the assaycount dict, and add assays
            else:
                created = dateutil.parser.parse(row[1].split()[0])
                closed = dateutil.parser.parse(row[2].split()[0])
                months.append(closed.strftime('%Y-%m'))
                sampledict = sorted_data.setdefault(row[0],
                                                    {'begin':created,
                                                        'end':closed,
                                                        'delta':(closed-created).days,
                                                        'assaycount':{'elisa':0,
                                                                    'gc':0,
                                                                    'lc':0,
                                                                    'fid':0,
                                                                    'other':0},              
                                                         'assays':[]})

#add lines based on the method, and update the assay count and the assay list
#currently not collecting data based on the different types of ELISA, so just listing it once
#and updateding the count
                if row[5] == 'ELISA':
                    if not 'elisa' in sampledict['assays']:
                        sampledict['assays'].append('elisa')
                    sampledict['assaycount']['elisa'] += 1
#for other methods....
                elif row[5] == 'GCFID':
#go through the individual assays
                    addedcheck = 0
                    for assay in gcfidassays:
#if the analyte is in the assay add the assay to the list and increase the count
                        if int(row[3]) in assaydict[assay]:
                            if not assay in sampledict['assays']:
                                sampledict['assays'].append(assay)
                                sampledict['assaycount']['fid'] += 1
                            addedcheck = 1
#if its not in the list update the the assay list with a generic assay and up the count
                    if addedcheck == 0:
                        sampledict['assays'].append('other GCFID')
                        sampledict['assaycount']['fid'] += 1
                        ucalist.append((row[4],row[5],row[3]))
                elif row[5] == 'GC/MS':
                    addedcheck = 0
                    for assay in gcassays:
                        if int(row[3]) in assaydict[assay]:
                            if not assay in sampledict['assays']:
                                sampledict['assays'].append(assay)
                                sampledict['assaycount']['gc'] += 1
                            addedcheck = 1
                    if addedcheck == 0:
                        sampledict['assays'].append('other gc/ms')
                        sampledict['assaycount']['gc'] += 1
                        ucalist.append((row[4],row[5],row[3]))
                elif row[5] == 'LC-MS/MS':
                    addedcheck = 0
                    for assay in lcassays:
                        if int(row[3]) in assaydict[assay]:
                            if not assay in sampledict['assays']:
                                sampledict['assays'].append(assay)
                                sampledict['assaycount']['lc'] += 1
                            addedcheck = 1
                        elif int(row[3]) in assaydict['benzo scans']:
                            if not 'benzo' in sampledict['assays']:
                                sampledict['assays'].append('benzo')
                                sampledict['assays'].append('benzo scans')
                                sampledict['assaycount']['lc'] += 1
                            else:
                                sampledict['assays'].append('benzo scans')
                                addedcheck = 1
                    if addedcheck == 0:
                        sampledict['assays'].append('other lc-ms/ms')
                        sampledict['assaycount']['lc'] += 1
                        ucalist.append((row[4],row[5],row[3]))
                else:
                    sampledict['assays'].append('other')
                    sampledict['assaycount']['other'] += 1
                    print row[0], row[4], row[5], row[3]
                    ucalist.append((row[4],row[5],row[3]))

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

over120 = []
outputmonth = set(months)

firstdate = min(outputmonth)
                                 
for sample in sorted_data:
    countlist = []
    sampledict = sorted_data[sample]
#if the sample has delta 120 or more exclude it from the totals
    if 'gc/ms scans' in sampledict['assays'] and 'benzo scans' in sampledict['assays']:
        outputdict['dsfa'].append(sampledict['delta'])
    elif sampledict['delta'] > 120:
        over120.append(sample)
    else:
        outputdict['total'].append(sampledict['delta'])
#if it has opiates as an assay we track in addition
        if 'opiates/oxys' in sampledict['assays']:
            outputdict['opiates'].append(sampledict['delta'])
        for key in assaycountkeys:
            countlist.append(sampledict['assaycount'][key])
        #print sample, countlist
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
                elif countlist[3] == 1 and countlist[2] == 0:
                        outputdict['bac_e_l'].append(sampledict['delta'])
                        outputdict['bac_e_c'].append(sampledict['delta'])
                elif countlist[3] > 1 and countlist[2] == 0:
                        outputdict['bac_e_l+'].append(sampledict['delta'])
                        outputdict['bac_e_c+'].append(sampledict['delta'])
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
                elif countlist[3] == 1 and countlist[2] == 0:
                        outputdict['bac_e_g'].append(sampledict['delta'])
                        outputdict['bac_e_c'].append(sampledict['delta'])
                elif countlist[3] > 1 and countlist[2] == 0:
                        outputdict['bac_e_g+'].append(sampledict['delta'])
                        outputdict['bac_e_c+'].append(sampledict['delta'])
                elif countlist[2] != 0 and countlist[3] != 0:
                        outputdict['bac_e_c+'].append(sampledict['delta'])
                        outputdict['bac_e_gl'].append(sampledict['delta'])


writeout = [['Turn Around Times',firstdate],
            ['Totals',''],
            ['Types of test','#samples','Mean','Median','Shortest','Longest','95% completed']]

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

writeout.append(['',''])
writeout.append(['Total number of samples longer then 120 days',str(len(over120)) + ' samples'])
writeout.append(['Samples that took more then 120 days:',''])
for sample in over120:
    writeout.append([sample,''])
writeout.append(['',''])
writeout.append(['The following tests','were not grouped'])
setuca = set(ucalist)
for item in setuca:
    writeout.append(item)

filename = 'Turn around times for ' + firstdate +'.csv'
outputfile = os.path.join(os.path.dirname(fileloc), filename)

with open(outputfile, 'wb') as op:
    wo = csv.writer(op)
    for row in writeout:
        wo.writerow(row)





    
                    
                                
                                
                        
                    
