import numpy as np
import datetime
import csv
import os
import re
import Tkinter, tkFileDialog
from lcmsdatasort import *
from lcmscurvefit import *
from lcmsCMplots import *

#a script to calculate the calibration model of Waters LCMS data for SWGTOX
#validation

#the data dic will hold all of our "raw" information
data = {}

def AIC(residuals,n,k):
    AICvalue = 2*k + n*np.log(np.sum(np.square(residuals))/n)
    return AICvalue
#we set several RE to check various conditions. Namely what the run name is, if we are looking at a
#duetrated standard
isrun = re.compile('[r|R]un\s?\d+')
isis = re.compile('[d|D]\d+')
#Get the assay name.  This will be the header for all the output files
assayname = raw_input('What Assay?: ')

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

analytekeys = sorted(analytekeys)
#go through the dictionary and pull out the target concentrations and measured concnetration and
#and store them in a new dictionary
dataCM = {}
for run in runkeys:
    for analyte in analytekeys:
#this dictionary will be organized by analyte
        dataCM.setdefault(analyte, {})
#vialdict is on a per run per analyte basis since we want the average of the vials for the analysis
        vialdict = {}
        for sampleline in data[run][analyte]:
#need the name confirm its a calibrator, use vial to account for repeated injections
#need the target concnetration and measured concentration for each line
            samplelinedict = data[run][analyte][sampleline]
#we only accept those lines that start with the word calibrator
            if samplelinedict['Name'].lower().startswith('calibrator'):
                #setup a new dictionary within vialdict for each concentration
                try:
                    concdict = vialdict.setdefault(float(samplelinedict['Std. Conc']), {})
                except:
                    concdict = vialdict.setdefault(0.0, {})
#based on the vial position we will setup a new list that stores the injections
                injectionlist = concdict.setdefault(samplelinedict['Vial'], [])
                try:
                    injectionlist.append(float(samplelinedict['Response']))
                except:
                    injectionlist.append(0)

#now we will finish the dataCM dictionary
        for conc in vialdict:
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
#for each analyte generate a graph and CSV file
for analyte in analytekeys:
    
    graphname = assayname + ' validation, ' + analyte + ' graph, ' + datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S') + '.png'
    graphfile = os.path.join(endfolder, graphname)
    filename = assayname + ' validation, ' + analyte + ' data, ' + datetime.datetime.now().strftime('%Y-%m-%d T%H%M%S') + '.csv'     
    csvfile = os.path.join(endfolder, filename)
    conclist = sorted(dataCM[analyte])

#count the number of runs    
    maxnumrun = 0
    for conc in conclist:
        testlen = len(dataCM[analyte][conc])
        if maxnumrun < testlen:
            maxnumrun = testlen
        maxnumrun = maxnumrun - 1

#and setup a header with that many run headers
    headerwriteout = ['Concentration']
    x = 1
    while x < maxnumrun:
        headerwriteout.append('run ' + str(x))
        x += 1
    
    residualdict.setdefault(analyte,{})
    
    writeout = [(analyte,''),('',''),('Calculated Response (Area/IS Area)',''),(headerwriteout + ['mean','stdev','%CV'])]
    rawresponsewriteout = []
#lead with the raw response numbers on the csv files
    for conc in conclist:
        rawresponselist = [str(conc)+ ' ng/mL']
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
                         
        
#we want the residuals for each equation
    functionlist = sorted(consdict[analyte].keys())
    for function in functionlist:
#we also want graph the mean data
        fundict = residualdict[analyte].setdefault(function,{'xdata':[],'ydata':[],
                                                             'xmean':[],'ymean':[],
                                                             'ynorm':[],'ymeannorm':[]})

        writeout.append((function,''))
        numofcons = len(consdict[analyte][function])
#add the terms to the writeout
        conswriteout = ['Zero Order Term:',round(consdict[analyte][function][0],9),
                        'First Order Term:',round(consdict[analyte][function][1],9)]
#if its quadratic we will need the third term as well
        if numofcons == 3:
            conswriteout.append('Second Order Term:')
            conswriteout.append(round(consdict[analyte][function][2],9))
        
    

#backcalc is the back calcs, residuals is the percent residuals, normalized is residuals divided by the stdev of the residuals
        backcalcwriteout = [('Back Calculations',''),(headerwriteout + ['mean','stdev','%CV'])]
        residualwriteout = [('Percent Residuals',''),(headerwriteout + ['mean'])]
        normalizedwriteout = [('Normalized Residuals',''),(headerwriteout + ['stdev'])]
        
        #conclist = sorted(dataCM[analyte])
        for conc in conclist:
            backcalclist = [str(conc) + ' ng/mL']
            residuallist = [str(conc) + ' ng/mL']
            normalizedlist = [str(conc) + ' ng/mL']
            rawresiduals = []
            bcstats = []
            rstats = []
            for run in sorted(dataCM[analyte][conc]):
                if run == 'all':
                    pass
                elif run == 'mean':
                    fundict['xmean'].append(conc)
                    backcalcmean = dataCM[analyte][conc]['mean'][function]['backcalc']
                    residualmean = (backcalcmean-conc)*100/conc
                    dataCM[analyte][conc]['mean'][function]['residual'] = residualmean
                    fundict['ymean'].append(residualmean)
                else:
                    fundict['xdata'].append(conc)
                    backcalc = dataCM[analyte][conc][run][function]['backcalc']
                    residual = (backcalc-conc)*100/conc
                    dataCM[analyte][conc][run][function]['residual'] = residual
                    rawresiduals.append(backcalc-conc)
                    fundict['ydata'].append(residual)
                    backcalclist.append(str(round(backcalc,1))+ ' ng/mL')
                    residuallist.append(str(round(residual,1))+ '%')
                    bcstats.append(backcalc)
                    rstats.append(residual)
            normstd = np.std(rawresiduals)
            for run in sorted(dataCM[analyte][conc]):
                
                if run == 'all':
                    pass
                elif run == 'mean':
                    normalizedmean = (dataCM[analyte][conc]['mean'][function]['backcalc']-conc)/normstd
                    dataCM[analyte][conc]['mean'][function]['normalized'] = normalizedmean
                    fundict['ymeannorm'].append(normalizedmean)
                else:
                    normalized = (dataCM[analyte][conc][run][function]['backcalc']-conc)/normstd
                    dataCM[analyte][conc][run][function]['normalized'] = normalized
                    fundict['ynorm'].append(normalized)
                    normalizedlist.append(str(round(normalized, 2)) + ' SD')
                    

            bmean = np.mean(bcstats)
            rmean = np.mean(rstats)
            bstd = np.std(bcstats)
            bcv = (bstd/bmean)*100
            
            backcalclist = backcalclist + [str(round(bmean,1)) + ' ng/mL',
                                           str(round(bstd,1)) + ' ng/mL',
                                           str(round(bcv,1)) + '%']
            residuallist = residuallist + [str(round(rmean,1)) + '%']

            normalizedlist = normalizedlist + [str(round(normstd,2)) + ' ng/mL']


            backcalcwriteout.append(backcalclist)
            residualwriteout.append(residuallist)
            normalizedwriteout.append(normalizedlist)

        AICcvalue = AIC(residualdict[analyte][function]['ymean'],
                        len(residualdict[analyte][function]['xmean']),numofcons)
        
        writeout.append(conswriteout)
        writeout.append(['AICc:',str(round(AICcvalue,2))])
        writeout.append(['',''])
        writeout = writeout + backcalcwriteout
        writeout.append(['',''])
        writeout = writeout + residualwriteout
        writeout.append(['',''])
        writeout = writeout + normalizedwriteout
        writeout.append(['',''])

    with open(csvfile, 'wb') as op:
        wo = csv.writer(op)
        for row in writeout:
            wo.writerow(row)
        

    graph(residualdict[analyte], consdict[analyte], dataCM[analyte],analyte, graphfile)
            
            
                    

                
                
                
            
                               
                               
                    
        
        
        
        
        
            
                      