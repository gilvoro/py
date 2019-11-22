import numpy as np
import datetime
import csv
import os
import re
import Tkinter, tkFileDialog
from fiddatasort import *

#a script to calculate the bais and precision of Waters LCMS data for SWGTOX
#validation

#the data dic will hold all of our "raw" information
data = {}

#setup a dictionary for the UTAK blood control levels
utakdict ={'methanol':0.037, 'ethanol':0.146, 'isopropanol':0.076, 'acetone':0.08}
#we are only interested in the following compounds
volatiles = ['methanol','ethanol','isopropanol','acetone']

#we set several RE to check various conditions. Namely what the run name is
isrun = re.compile('[r|R]un\s?\d')
#Get the assay name.  This will be the header for all the output files
assayname = raw_input('What Assay?: ')

#quick window to get the dir where the txt files are.
root = Tkinter.Tk()
root.withdraw()

dirloc = tkFileDialog.askdirectory()
endfolder = os.path.join(dirloc,'BP Program Data')
if not os.path.exists(endfolder):
    os.makedirs(endfolder)

root.destroy()
#now we will go through dir and get the file names and build us a new dictionary
for item in os.listdir(dirloc):
#only text files are considered
    if item.endswith('.csv'):
#see if it has a run name
        runtest = isrun.search(item)
        if runtest:
#remove any spaces in the run name and build the dictionary
            runname = str("".join(runtest.group().split())).lower()
            data[runname] = fiddatasort(os.path.join(dirloc, item))
        else:
            print item + " does not have a run listed and will not be used in the analysis"

runkeys = sorted(data.keys())

analytekeys = sorted(volatiles)
#go through the dictionary and pull out the target concentrations and measured concnetration and
#and store them in a new dictionary
dataBP = {}
for run in runkeys:
    for analyte in analytekeys:
#this dictionary will be organized by analyte
        dataBP.setdefault(analyte, {})
        for sampleline in data[run][analyte]:
#need the name confirm its a control
#need the target concnetration and measured concentration for each line
            samplelinedict = data[run][analyte][sampleline]
            if float(samplelinedict['calc']) == 0.000:
                pass
#we only accept those lines that start with the word control
            elif samplelinedict['name'].lower().split(' ')[1] == 'spike':
                conc = float(samplelinedict['name'].lower().split(' ')[0])/10000
                dataBP[analyte].setdefault(conc,{})
                concdict = dataBP[analyte][conc].setdefault(run,{})
                concdict[sampleline] = (round(float(samplelinedict['calc']),3))
            elif samplelinedict['name'].lower().split(' ')[0] == 'utak':
                dataBP[analyte].setdefault('utak',{})
                concdict = dataBP[analyte]['utak'].setdefault(run,{})
                concdict[sampleline] = (round(float(samplelinedict['calc']),3))
                
#setup for the write out        
writeout = []
                
for analyte in analytekeys:
    writeout.append((analyte,''))
    writeout.append('')
    conckeys = sorted(dataBP[analyte].keys())
    for item in conckeys:
        if item == 'utak':
            conc = utakdict[analyte]
            concwriteout = [('UTAK Nominal Conc', str(conc) + ' g/dL'),('Grand Stats', ''),
                            ('Grand Mean','Grand %Bias','Grand StDev', 'Grand %CV')]
            conc = utakdict[analyte]
        else:
            conc = item
            concwriteout = [('Nominal Conc', str(conc) + ' g/dL'),('Grand Stats', ''),
                            ('Grand Mean','Grand %Bias','Grand StDev', 'Grand %CV')]
                                                                                       
        allsamples = []
        runtextleader = ['Run']
        runtextfinish = ['Run Mean', 'Run %Bias', 'Run StDev', 'Run %CV']
#for each block of data get the maxium number of samples    
        maxnumberofsamples = 0
        for run in dataBP[analyte][item]:
            testlen = len(dataBP[analyte][item][run])
            if testlen > maxnumberofsamples:
                maxnumberofsamples = testlen
#now we will extend the tiles to included all of the samples
        concwriteout.append(('Individual Runs',''))
        x = 1
        while x - 1 < maxnumberofsamples:
            runtextleader.append('Sample ' + str(x))
            x += 1
        concwriteout.append(runtextleader + runtextfinish)
#now we will go through the individual runs and get the individual values and stats
        for run in runkeys:
            try:               
                samplevalue = []
                runwriteout = [run]
                for sample in dataBP[analyte][item][run]:
                    samplevalue.append(dataBP[analyte][item][run][sample])
                    allsamples.append(dataBP[analyte][item][run][sample])
                    runwriteout.append(str(round(dataBP[analyte][item][run][sample],4)) + ' g/dL')
                mean = np.mean(samplevalue)
                std = np.std(samplevalue)
                cv = (std/mean)*100
                bias = ((mean-conc)/conc)*100
                if len(runwriteout) < maxnumberofsamples + 1:
                    x = (len(runwriteout)-maxnumberofsamples)+1
                    while x > 0:
                        runwriteout.append('N/A')
                        x = x-1
                concwriteout.append(runwriteout + [str(round(mean,4)) + ' g/dL', str(round(bias, 1)) + '%',
                                               str(round(std,4)) + ' g/dL', str(round(cv,1)) + '%'])
            except:
                print 'There is no ' + run + ' for ' + analyte + ' at ' + str(conc) + ' ng/mL'
                pass

#now calculate the grand stats for all of the samples
        grandmean = np.mean(allsamples)
        grandstd = np.std(allsamples)
        grandcv = (grandstd/grandmean)*100
        grandbias = ((grandmean-conc)/conc)*100

        concwriteout.insert(3,(str(np.round(grandmean,4)) + ' g/dL', str(round(grandbias, 1)) + '%',
                                           str(round(grandstd,4)) + ' g/dL', str(round(grandcv,1)) + '%'))

        writeout = writeout + concwriteout
#good all fashion spacing
        writeout.append('')

    writeout.append('')
    writeout.append('')

#and wright out to the same dir that we are in.
filename = assayname + ' Bias and Precision Data Compiled ' + datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S') + '.csv'     
outputfile = os.path.join(endfolder, filename)

with open(outputfile, 'wb') as op:
    wo = csv.writer(op)
    for row in writeout:
        wo.writerow(row)
                
                
                
            
                               
                               
                    
        
        
        
        
        
            
                      
