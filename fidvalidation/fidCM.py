import numpy as np
import datetime
import csv
import os
import re
import Tkinter, tkFileDialog
from fiddatasort import *
from fidcurvefit import *
from fidCMplots import *

#a script to calculate the calibration model of PerkinElmer HSGCFID for SWGTOX
#validation

#the data dic will hold all of our "raw" information
data = {}

#we are only interested in the following compounds
volatiles = ['methanol','ethanol','isopropanol','acetone']
#we set several RE to check various conditions. Namely what the run name is
isrun = re.compile('[r|R]un\s?\d+')
#Get the assay name.  This will be the header for all the output files
assayname = raw_input('What Assay?: ')
print 'Please list those conc in mg/dL that you would like to excluded from the analysis'
print 'Please seperate mutliple concentraions with a comma and space as follows:25.0, 200.0'
thingstoexclude = raw_input('What Concetrations: ')
concex = thingstoexclude.split(', ')
#quick window to get the dir where the txt files are.
root = Tkinter.Tk()
root.withdraw()

dirloc = tkFileDialog.askdirectory()
endfolder = os.path.join(dirloc,'CM Program Data')
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
dataCM = {}
for run in runkeys:
    is_dict = {}
    for sampleline in data[run]['n-propanol']:
        is_dict[sampleline] = float(data[run]['n-propanol'][sampleline]['area'])
    for analyte in analytekeys:
#this dictionary will be organized by analyte
        dataCM.setdefault(analyte, {})
#vialdict is on a per run per analyte basis since we want the average of the vials for the analysis
        vialdict = {}
        for sampleline in data[run][analyte]:
#need the name confirm its a calibrator, use vial to account for repeated injections
#need the target concnetration and measured concentration for each line
            samplelinedict = data[run][analyte][sampleline]
#if the area is zero we pass the line
            if samplelinedict['area'] == '0.000':
                pass
#we only accept those lines that end with the word mix
            elif samplelinedict['name'].lower().endswith('mix'):
#for graphing purposes the concentraions will be in mg/dL
                conc = float(samplelinedict['name'].split(' ')[0])/10
                if str(conc) in concex:
                    pass
                else:
#setup a new dictionary within vialdict for each concentration
                    concdict = vialdict.setdefault(conc, {})
#based on the names we will setup a new list that stores the repeated measure
                    injectionlist = concdict.setdefault(samplelinedict['name'], [])
                    injectionlist.append(float(samplelinedict['area'])/is_dict[sampleline])
#now we will finish the dataCM dictionary
        for conc in vialdict:
#exluded those concentrations listed above from the analysis 
            dataCM[analyte].setdefault(conc,{})
            dataCM[analyte][conc].setdefault(run, {'raw':[]})
            rawlist = dataCM[analyte][conc][run]['raw']                                             
#collate the data to send to the curve fitting function
            allvalues = dataCM[analyte][conc].setdefault('all',[])
            for vial in vialdict[conc]:
#get the number of vials for later use
                numofn = len(vialdict[conc][vial])
                meaninjection = np.mean(vialdict[conc][vial])
                rawlist.append(meaninjection)
                rawlist.append(numofn)
                allvalues.append(meaninjection)    

#consdict has all of the constants for the different equations per equation
consdict = {}
#go through for each analyte...
for analyte in analytekeys:
    xdata = []
    ydata = [] 
    conckeys = sorted(dataCM[analyte].keys())
#... and get the data in list form to send to customcurve fit
    for conc in conckeys:
        xdata.append(conc)
        ydata.append(dataCM[analyte][conc]['all'])
#customcurve fit handles averaging the ydata and returns the backcalculations based on the curve
#(backcalcdict) and constants for all the equations (consdict)
    consdict[analyte] = customcurvefit(xdata,ydata,dataCM[analyte])    

#go through and calculate the percent residual
residualdict = {}
for analyte in analytekeys:
    
    graphname = assayname + ' validation, ' + analyte + ' graph, ' + datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S') + '.png'
    graphfile = os.path.join(endfolder, graphname)
    filename = assayname + ' validation, ' + analyte + ' data, ' + datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S') + '.csv'     
    csvfile = os.path.join(endfolder, filename)
    conclist = sorted(dataCM[analyte])
    
    maxnumrun = 0
    for conc in conclist:
        testlen = len(dataCM[analyte][conc])
        if maxnumrun < testlen:
            maxnumrun = testlen
        maxnumrun = maxnumrun - 1

    headerwriteout = ['Concentration']
    x = 1
    while x < maxnumrun:
        headerwriteout.append('run ' + str(x))
        x += 1
    
    residualdict.setdefault(analyte,{})
    
    writeout = [(analyte,''),('',''),('Calculated Response (Area/IS Area)',''),(headerwriteout + ['mean','stdev','%CV'])]
    rawresponsewriteout = []
#lead with the raw response numbers
    for conc in conclist:
        rawresponselist = [str(conc)+ ' mg/dL']
        responsemean = np.mean(dataCM[analyte][conc]['all'])
        responsestdev = np.std(dataCM[analyte][conc]['all'])
        responsecv = str(round(((responsestdev/responsemean)*100),2)) + '%'
                               
        for run in sorted(dataCM[analyte][conc]):
                if run == 'mean' or run == 'all':
                    pass
                else:
                    rawresponselist.append(str(round(dataCM[analyte][conc][run]['raw'][0],5)))
                                           
                                        
            
        rawresponselist = rawresponselist + [str(round(responsemean,4)),
                                             str(round(responsestdev,5)),
                                             responsecv]
        rawresponsewriteout.append(rawresponselist)

    writeout = writeout + rawresponsewriteout
    writeout.append(('',''))
                         
        
#we want this for each equation
    functionlist = sorted(consdict[analyte].keys())
    for function in functionlist:
#we also want graph the mean data
        fundict = residualdict[analyte].setdefault(function,{'xdata':[],'ydata':[],
                                                             'xmean':[],'ymean':[],})

        writeout.append((function,''))
        numofcons = len(consdict[analyte][function])
        conswriteout = ['Zero Order Term:',round(consdict[analyte][function][0],9),
                        'First Order Term:',round(consdict[analyte][function][1],9)]
        if numofcons == 3:
            conswriteout.append('Second Order Term:')
            conswriteout.append(round(consdict[analyte][function][2],9))
        writeout.append(conswriteout)
        writeout.append(['',''])
    


        backcalcwriteout = [('Back Calculations',''),(headerwriteout + ['mean','stdev','%CV'])]
        residualwriteout = [('Percent Residuals',''),(headerwriteout + ['mean'])]
        
        #conclist = sorted(dataCM[analyte])
        for conc in conclist:
            backcalclist = [str(conc) + ' mg/dL']
            residuallist = [str(conc) + ' mg/dL']
            bcstats = []
            rstats = []
            for run in sorted(dataCM[analyte][conc]):
                if run == 'all':
                    pass
                elif run == 'mean':
                    fundict['xmean'].append(conc)
                    backcalcmean = dataCM[analyte][conc]['mean'][function][0]
                    residualmean = (backcalcmean-conc)*100/conc
                    dataCM[analyte][conc]['mean'][function].append(residualmean)
                    fundict['ymean'].append(residualmean)
                else:
                    fundict['xdata'].append(conc)
                    backcalc = dataCM[analyte][conc][run][function][0]
                    residual = (backcalc-conc)*100/conc
                    dataCM[analyte][conc][run][function].append(residual)
                    fundict['ydata'].append(residual)
                    backcalclist.append(str(round(backcalc,2))+ ' mg/dL')
                    residuallist.append(str(round(residual,2))+ '%')
                    bcstats.append(backcalc)
                    rstats.append(residual)
                                        

            bmean = np.mean(bcstats)
            rmean = np.mean(rstats)
            bstd = np.std(bcstats)
            bcv = (bstd/bmean)*100
            
            backcalclist = backcalclist + [str(round(bmean,2)) + ' mg/dL',
                                           str(round(bstd,2)) + ' mg/dL',
                                           str(round(bcv,2)) + '%']
            residuallist = residuallist + [str(round(rmean,2)) + '%']
            
            backcalcwriteout.append(backcalclist)
            residualwriteout.append(residuallist)

        writeout = writeout + backcalcwriteout
        writeout.append(['',''])
        writeout = writeout + residualwriteout
        writeout.append(['',''])

    with open(csvfile, 'wb') as op:
        wo = csv.writer(op)
        for row in writeout:
            wo.writerow(row)
        

    graph(residualdict[analyte], consdict[analyte], dataCM[analyte],analyte, graphfile)
            
            
                    

                
                
                
            
                               
                               
                    
        
        
        
        
        
            
                      
