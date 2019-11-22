import numpy as np
import datetime
import csv
import os
import re
import Tkinter, tkFileDialog
from lcmsdatasort import *

#a script to calculate the bais and precision of Waters LCMS data for SWGTOX
#validation

#the data dic will hold all of our "raw" information
data = {}

#we set several RE to check various conditions. Namely what the run name is, if we are looking at a
#duetrated standard
isrun = re.compile('[r|R]un\s?\d')
isis = re.compile('[d|D]\d')
#Get the assay name.  This will be the header for all the output files
assayname = raw_input('What Assay?: ')

#quick window to get the dir where the txt files are.

dirloc = tkFileDialog.askdirectory()
endfolder = os.path.join(dirloc,'BP Program Data')
if not os.path.exists(endfolder):
    os.makedirs(endfolder)

#now we will go through dir and get the file names and build us a new dictionary
for item in os.listdir(dirloc):
#only text files are considered
    if item.endswith('.txt'):
#see if it has a run name
        runtest = isrun.search(item)
        if runtest:
#remove any spaces in the run name and build the dictionary
            runname = str("".join(runtest.group().split())).lower()
            data[runname] = lcmsdatasort(os.path.join(dirloc, item))
        else:
            print item + " does not have a run listed and will not be used in the analysis"

runkeys = sorted(data.keys())
analytekeys = []
#get a list of compounds that are not internal standards
for run in runkeys:
    analytelist = data[run].keys()
    for analyte in analytelist:
#test for internal standard
        istest = isis.search(analyte)
#if its duetrated we don't want it
        if istest:
            pass
#if its not, check to see if we already have it and if not added it
        else:
            if analyte in analytekeys:
                pass
            else:
                analytekeys.append(analyte)

#go through the dictionary and pull out the target concentrations and measured concnetration and
#and store them in a new dictionary
dataBP = {}
for run in runkeys:
    for analyte in analytekeys:
#this dictionary will be organized by analyte
        dataBP.setdefault(analyte, {})
#vialdict is on a per run per analyte basis since we want the average of the vials for the analysis
        vialdict = {}
        for sampleline in data[run][analyte]:
#need the name confirm its a control, use vial to account for repeated injections
#need the target concnetration and measured concentration for each line
            samplelinedict = data[run][analyte][sampleline]
#we only accept those lines that start with the word control
            if samplelinedict['Name'].lower().startswith('control'):
#setup a new dictionary within vialdict for each concentration
                try:
                    concdict = vialdict.setdefault(float(samplelinedict['Std. Conc']), {})
                except:
                    concdict = vialdict.setdefault(0.0, {})
#based on the vial position we will setup a new list that stores the injections
                injectionlist = concdict.setdefault(samplelinedict['Vial'], [])
                try:
                    injectionlist.append(float(samplelinedict['ng/mL']))
                except:
                    injectionlist.append(0)

#now we will finish the dataBP dictionary
        for conc in vialdict:
            dataBP[analyte].setdefault(conc,{})
            conclist = dataBP[analyte][conc].setdefault(run, [])
            for vial in vialdict[conc]:
#get the number of vials for later use
                numofn = len(vialdict[conc][vial])
                meaninjection = np.mean(vialdict[conc][vial])
                conclist.append((meaninjection, numofn))
                
#setup for the write out        
writeout = []
                
for analyte in dataBP:
    writeout.append((analyte,''))
    writeout.append('')
    conckeys = sorted(dataBP[analyte].keys())
    for conc in conckeys:
        concwriteout = [('Nominal Conc', str(conc) + ' ng/mL'),('Grand Stats', ''),('Grand Mean','Grand %Bias',
                                                                                'Grand StDev', 'Grand %CV')]
        allsamples = []
        runtextleader = ['Run']
        runtextfinish = ['Run Mean', 'Run %Bias', 'Run StDev', 'Run %CV']
#for each block of data get the maxium number of samples    
        maxnumberofsamples = 0
        for run in dataBP[analyte][conc]:
            testlen = len(dataBP[analyte][conc][run])
            if testlen > maxnumberofsamples:
                maxnumberofsamples = testlen
#now we will extend the tiles to included all of the samples
        concwriteout.append(('Individual Days',''))
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
                for sample in dataBP[analyte][conc][run]:
                    samplevalue.append(sample[0])
                    allsamples.append(sample[0])
                    runwriteout.append(str(round(sample[0],1)) + ' ng/uL (n=' + str(sample[1]) +')' )
                mean = np.mean(samplevalue)
                std = np.std(samplevalue)
                cv = (std/mean)*100
                bias = ((mean-conc)/conc)*100
                concwriteout.append(runwriteout + [str(round(mean,1)) + ' ng/mL', str(round(bias, 1)) + '%',
                                               str(round(std,1)) + ' ng/mL', str(round(cv,1)) + '%'])
            except:
                print 'There is no ' + run + ' for ' + analyte + ' at ' + str(conc) + ' ng/mL'
                pass

#now calculate the grand stats for all of the samples
        grandmean = np.mean(allsamples)
        grandstd = np.std(allsamples)
        grandcv = (grandstd/grandmean)*100
        grandbias = ((grandmean-conc)/conc)*100

        concwriteout.insert(3,(str(np.round(grandmean,1)) + ' ng/mL', str(round(grandbias, 1)) + '%',
                                           str(round(grandstd,1)) + ' ng/mL', str(round(grandcv,1)) + '%'))

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
