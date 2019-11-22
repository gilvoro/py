#!/usr/bin/env python2

import numpy as np
import datetime
import csv
import matplotlib.pyplot as plt
import os
import re
import sys
import time
import Tkinter, tkFileDialog

#re checks for dates
isprodate = re.compile('\d\d\d\d-\d\d-\d\d')
iswrongdate = re.compile('\d\d\d\d\d\d')
isnum = re.compile('\d+')

controllist = [('blank',"Negative Control"),('bco','Below Cutoff Control'),('co','Cutoff'),('aco','Above Cutoff Control')]
#because I am a jerk
def wrongdate(date,number):
    correctdate = "20" + date[4:] + date[0:2] + date[2:4]
    #if number == 1:
        #rant1 = ["You didn't use the ISO8601 date format.\n", "Now we have to wait while I jump through hoops to get a sortable date format.\n",
        #"still working.....\n","Well thats 4 seconds we will never get back.\n"]
        #for rant in rant1:
            #sys.stdout.write(rant)
            #sys.stdout.flush()
            #time.sleep(1)
    #elif number == 2:
        #rant2 = ['A second one....\n','17 divide by....\n','carry the one, factor in Planks constant...\n', "I hope I do not have to do this anymore\n"]
        #for rant in rant2:
            #sys.stdout.write(rant)
            #sys.stdout.flush()
            #time.sleep(1)
    #elif 2 < number < 5:
        #rant3 = ['sigh....\n',"","",""]
        #for rant in rant3:
            #sys.stdout.write(rant)
            #sys.stdout.flush()
            #time.sleep(1)
    #elif number == 5:
        #rant4 = ["","","","....why do you hate me?\n"]
        #for rant in rant4:
            #sys.stdout.write(rant)
            #sys.stdout.flush()
            #time.sleep(1)
    return correctdate

#quick window to get the dir where the txt files are.
root = Tkinter.Tk()
root.withdraw()

dirloc = tkFileDialog.askdirectory()
endfolder = os.path.join(dirloc,'ELISA Validation Data')
if not os.path.exists(endfolder):
    os.makedirs(endfolder)

analyte = raw_input("What ELISA assay?:")
matrix = raw_input("For what matrix?:")
bcov = raw_input("What is the concentration in ng/mL of below CO control?:")
cov = raw_input("What is the concentration in ng/mL of CO control?:")
acov = raw_input("What is the concentration in ng/mL of above CO control?:")

datadict = {'stats':{'blanka':[],'bcoa':[],'coa':[],'acoa':[],'blankr':[],'bcor':[],'cor':[],'acor':[],'bcov':bcov, 'cov':cov, 'acov':acov}}

numwd = 1
#open file
for item in os.listdir(dirloc):
#only csv files are considered
    if item.endswith('.csv'):
        print item
#see if it has a run name
        rundate = 'none'
        wdatetest = iswrongdate.search(item)
        if wdatetest:
            rundate = wrongdate(wdatetest.group(),numwd)
            numwd += 1
        else:
            datetest = isprodate.search(item)
            if datetest:
                rundate = datetest.group()
            else:
                print item + ' does not have a date listed and will not be used in the analysis'

        if rundate == 'none':
            pass
        else:
            nameparameters = item.split('.')[0].split(' ')
            testnum = isnum.search(nameparameters[2])
            if testnum:
                runname = rundate + ' run ' + testnum.group()
            else:
                runname = rundate + ' run 1'

            datadict[runname] = {'blanka':[],'bcoa':[],'coa':[],'acoa':[]}

        if rundate == 'none':
            pass
        else:
            with open (os.path.join(dirloc, item), 'rU') as csvfile:
                ud = csv.reader(csvfile)
                rownum = 0

                for row in ud:
                    if rownum == 0:
                        rownum += 1
                    elif rownum == 1:
                        rownum += 1
                        for item in row[1:4]:
                            datadict[runname]['blanka'].append(float(item))
                            datadict['stats']['blanka'].append(float(item))
                    elif rownum == 2:
                        rownum += 1
                        for item in row[1:4]:
                            datadict[runname]['bcoa'].append(float(item))
                            datadict['stats']['bcoa'].append(float(item))
                    elif rownum== 3:
                        rownum += 1
                        for item in row[1:4]:
                            datadict[runname]['coa'].append(float(item))
                            datadict['stats']['coa'].append(float(item))
                    elif rownum == 4:
                        rownum += 1
                        for item in row[1:4]:
                            datadict[runname]['acoa'].append(float(item))
                            datadict['stats']['acoa'].append(float(item))

for run in sorted(datadict.keys()):
    if run == 'stats':
        pass
    else:
        rundict = datadict[run]
        blankabsmean = np.mean(rundict['blanka'])
        for parameter in [('blanka','blankr'),('bcoa','bcor'),('coa','cor'),('acoa','acor')]:
            rundict.setdefault(parameter[1],[])
            for item in rundict[parameter[0]]:
                rundict[parameter[1]].append((item/blankabsmean)*100)
                datadict['stats'][parameter[1]].append((item/blankabsmean)*100)

filename = analyte.lower() + ' in '+ matrix.lower() + ' validation data, ' + datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S') + '.csv'
graphname = analyte.lower() + ' in '+ matrix.lower() + ' validation data, ' + datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S') + '.png'
csvfile = os.path.join(endfolder, filename)
graphfile = os.path.join(endfolder, graphname)

writeout = [(analyte.lower() + ' ELISA assay',''),('In ' + matrix.lower(),''),('Compiled:', datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S')),('','')]


for run in sorted(datadict.keys()):
    if run == 'stats':
        pass
    else:
        writeout.append(('Run:',run))
        writeout.append(['Level', 'Concentration [ng/mL]','Well 1 Abs', 'Well 2 Abs', 'Well 3 Abs','','Well 1 Ratio', 'Well 2 Ratio','Well 3 Ratio'])
        for item in controllist:
            if item[0] == 'blank':
                conc = 'N/A'
            else:
                conc = datadict['stats'][item[0] + 'v'] + 'ng/mL'
            level_info = [item[1],conc]
            for result in datadict[run][item[0]+'a']:
                level_info.append(str(round(result,3)))
            level_info.append('')
            for result in datadict[run][item[0]+'r']:
                level_info.append(str(round(result,2)))
            writeout.append(level_info)
        writeout.append(('',''))

statsdict = datadict['stats']
writeout.append(('Grand Totals',''))
writeout.append(['Level','Concentration [ng/mL]', 'Mean Abs', 'St. Dev of Abs', '%CV of Abs','','Mean Ratio','St. Dev of Ratio','%CV of Ratio','','Lower Threshold','Upper Threshold'])
for item in controllist:
    if item[0] == 'blank':
        conc = 'N/A'
    else:
        conc = statsdict[item[0] + 'v'] + 'ng/mL'
    level_info = [item[1],conc]
    mabs = np.mean(statsdict[item[0]+'a'])
    sdabs = np.std(statsdict[item[0]+'a'])
    cvabs = (sdabs/mabs)*100
    mr = np.mean(statsdict[item[0]+'r'])
    sdr = np.std(statsdict[item[0]+'r'])
    cvr = (sdr/mr)*100
    if item[0] == 'blank':
        rltl = 'N/A'
        rutl = 'N/A'

    else:
        ltl = mr - (2*sdr)
        utl = mr + (2*sdr)
        rltl = round(ltl,1)
        rutl = round(utl,1)

    if item[0] == "bco":
        bco_u = utl
        bco_l = ltl
        bco_mean = mr
    if item[0] == 'co':
        co_u = utl
        co_l = ltl
        co_mean = mr
    if item[0] == 'aco':
        aco_u = utl
        aco_l = ltl
        aco_mean = mr


    level_info = level_info + [ str(round(mabs,3)),str(round(sdabs,3)),str(round(cvabs,2))+'%','', str(round(mr,2)), str(round(sdr,2)), str(round(cvr,2))+'%','',rltl,rutl]
    writeout.append(level_info)
writeout.append(('',''))
writeout.append(('Comparisons',''))
writeout.append(('Control Level One', 'Lower Threshold', 'Control Level Two', 'Upper Threshold', 'Pass?'))
if bco_l > co_mean:
    bcopass = 'Pass'
else:
    bcopass = 'Fail'
if co_mean > aco_u:
    acopass = 'Pass'
else:
    acopass = 'Fail'
writeout.append(('Below Cutoff', str(round(bco_l,2)), 'Cutoff', str(round(co_mean,2)),bcopass))
writeout.append(('Cutoff', str(round(co_mean,2)), 'Above Cutoff', str(round(aco_u,2)),acopass))


with open(csvfile, 'wb') as op:
    wo = csv.writer(op)
    for row in writeout:
        wo.writerow(row)

#setup figures
fig, ax = plt.subplots(figsize = (7,5))
fig.suptitle(analyte.upper() + ' ELISA validation')

ax.axis([0,4,0,100])

#set up ticks
ax.xaxis.set_ticks_position('bottom')
ax.set_xticks(range(1,4,1))
ax.set_xticklabels(['Below Cutoff', 'Cutoff', 'Above Cutoff'], fontsize = 'small')

ax.yaxis.set_ticks_position('left')
ax.set_yticks(range(0,110,10))
ax.set_yticklabels(['0.00','10.0','20.0','30.0','40.0','50.0','60.0','70.0', '80.0','90.0','100.0'], fontsize = 'small' )

colorcode = ['red','green','purple']
ccv = 0

for item in [(bco_l, bco_mean, bco_u),(co_l, co_mean, co_u),(aco_l, aco_mean, aco_u)]:
    ax.axhline(item[0],0,1, color = colorcode[ccv],linestyle = '--', lw = 0.5)
    ax.axhline(item[1],0,1, color = colorcode[ccv],linestyle = '-', lw = 0.5)
    ax.axhline(item[2],0,1, color = colorcode[ccv],linestyle = '--', lw = 0.5)


    ccv += 1

ccv = 0
for item in controllist:
    if item[0] == 'blank':
        pass
    else:
        ax.scatter([(ccv)+1]*len(statsdict[item[0]+'r']),statsdict[item[0]+'r'],color = colorcode[ccv], marker = 'o',s=10)
        ccv += 1

plt.savefig(graphfile)
