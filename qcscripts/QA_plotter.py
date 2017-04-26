import os
import sys
import shutil
import subprocess
import re
import csv
import datetime
import numpy as np
from scipy import stats
from xmr_grapher import *


#a script to proccess LCMS data to generate xmr charts
#Define file locations
inputloc = 'C:/scriptfiles/xmr inputs'
outputloc = r'//radon.chematox.com/public/labtools/jimscripts/xmr plots'
parametersloc = r'//radon.chematox.com/public/labtools/jimscripts/xmr parameters'

#dictionary with the datasort fuction in it
datasortfuctions = {'lcms': 'lcmsdatasort'}

#generate a list of supported assays
assaylist = []
for f in sorted(os.listdir(parametersloc)):
    if f.endswith('.csv'):
        assaylist.append(f.split('.')[0])

#get a human readable date and one all run together
readdate = datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')
date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

#setup some RE
isfqc = re.compile('[f|F][q|Q][c|C]\-?\d+')
isqan = re.compile('[q|Q][a|A]\-?\d+')
isisodate = re.compile('\d\d\d\d\-\d\d-\d\d')

#function to get the assaytype
def assaycheck():
    for a in range(len(assaylist)):
        print str(a+1) + '.) ' + assaylist[a]
    whichnum = raw_input('Please enter the number of the assay you would like to use\nor type quit to exit: ')
    if whichnum.lower() == 'quit' or whichnum.lower() == 'q' or whichnum.lower() == 'exit':
        sys.exit()
    elif not whichnum.isdigit():
        print 'No number selected'
        assaynum = assaycheck()
    elif int(whichnum) - 1 in range(len(assaylist)):
        assaynum = int(whichnum)-1

    return assaynum

def qanumcheck():
    whatqanum = raw_input('Please enter the QA-ticket number for the controls (qa-###)\nor type quit to exit: ')
    qatest = isqan.search(whatqanum)
    if whatqanum.lower() == 'quit' or whatqanum.lower() == 'q' or whatqanum.lower() == 'exit':
        sys.exit()
    elif qatest:
        isnum = re.search('\d+',str("".join(qatest.group().split())).lower())
            #pull out the QA number
        qaname = 'qa-'+str("".join(isnum.group().split()))
    else:
        print'invalid QA number or incorrect format.'
        qaname = qanumcheck()

    return qaname

#function to allow the user to review the data before uploading.  Not implemented yet
def reviewcheck(filedict):
    print 'Please review the following for accuracy:'
    for a in range(len(filedict.keys())):
        item = sorted(filedict.keys())[a]           
        print  str(a+1) + '.) ' + item + ' - ' + filedict[item]['datarun']

#function to get the paramters for the desired assay.  Currently returns a list and a dictionary        
def getparameters(fileloc):
    #open the parameter file
    #this will contain currently the name of the assay and the instrument type
    returnlist = []
    #this will contain the list of controls to be examined and if they have validation or initial data asscociated with them (1=yes)
    returndict = {}
    rownum = 0
    with open(fileloc, 'rU') as csvfile:
        raw_data = csv.reader(csvfile)
        for row in raw_data:
        #currently rows 0 and 1 contain things for the list
            if rownum < 2:
                returnlist.append(row[1])
                rownum += 1
        #currently rows past row 2 have items for the dict
            elif rownum >2:
                returndict[row[0]] = [row[1]]
                rownum += 1
        #the items in row 2 are just to make the file human readable
            else:
                rownum += 1

    return returnlist, returndict

#fuction to check for the script file and if it does exist make it
def scriptfilemaker(targetfolder):
    forscriptfolder_make = os.path.join(targetfolder, 'for script')
    if not os.path.exists(forscriptfolder_make):
        os.makedirs(forscriptfolder_make)

    return forscriptfolder_make

#a function to get the initial data for the LCMS with 6 initial measurements
def lcmsinitialdata(forscriptfolder):
    initialdict = {}
    initialfile = os.path.join(forscriptfolder, 'initial data.csv')
    if os.path.isfile(initialfile):
        with open(initialfile, 'rU') as csvfile:
            raw_data = csv.reader(csvfile)
            for row in raw_data:
                if (len(row)-1)%3 != 0:
                    pass
                else:
                    initialdict.setdefault(row[0],{})
                    for a in range((len(row)-1)/3):
                        initialdict[row[0]][row[(a*3)+1]] = {'mean':row[(a*3)+2],'sd':row[(a*3)+3]}

    return initialdict

#a function to check for previous data, and remove unwated FQC from the list
def previousdatafun(forscriptfolder,fqclisttemp):
    datadict = {}
    #a holder varible to for the file location
    previousdata = 'none'
    #a comparison varible to see what is the more recent scriptfile
    previousdatacheck = 0
    #get a list of all the scriptfiles in the script folder
    for scriptfile in os.listdir(forscriptfolder):
        #ignore things that don't start with script data
        if scriptfile.startswith('script data'):
            #pull out the date/time stamp and see if its bigger then the last one
            if scriptfile.split('-')[1] > previousdatacheck:
                #if it is then current file because the one we compare everythint to
                previousdatacheck = scriptfile.split('-')[1]
                previousdata = os.path.join(forscriptfolder, scriptfile)

    #setup a list FQC to remove from the FQC list, and thus not processed
    fqcremove = []
    #what analyte are we currently looking at?
    canalyte = 'none'
    #what level are we currently looking at?
    clevel = 'none'
    #a list of fqc numbers where we will use new data, not data loaded before
    fqcprevious = []
    #just make sure we have real files
    if previousdata != 'none' and os.path.isfile(previousdata):
        #read the file
        with open(previousdata, 'rU') as csvfile:
            raw_data = csv.reader(csvfile)
            for row in raw_data:
                #assume we are going to add this line to datedict
                writeto = True
                if row[0] == '' or row[0] == ' ':
                    print 'Empty row in previous data, passing'
                #if the line starts with analyte we have a new analyte and new dict entry
                elif row[0] == 'analyte':
                    datadict[row[1]] = {}
                    canalyte = row[1]
                #if the line starts with level we have a new level and new dict entry
                elif row[0] == 'level':
                    datadict[canalyte][row[1]] = {}
                    clevel = row[1]
                #if the rows that start withs these we want
                elif row[0].lower().startswith('fqc') or row[0].lower() == 'n_values':
                    #if we have already flagged this fqc number to use new data then we will not add it
                    if row[0] in fqcprevious:
                        writeto = False
                    #if we have already flagged this fqc number as to be removed from the new data move on
                    elif row[0] in fqcremove:
                        pass
                    #if this fqc number is in the fqclist then findout what to do about that
                    elif row[0] in fqclist:
                        print row[0].split('\n')[0] + ' ' + row[0].split('\n')[1] + ' was previously uploaded'
                        overwrite = raw_input('If you wish to proceed with overriding previous data please type yes: ')
                        #the user must actively agree to using the new data opposed to the old
                        if overwrite.lower() == 'yes':
                            print "New data will be used"
                            fqcprevious.append(row[0])
                            writeto = False
                        else:
                            print 'Data loaded previously will be used.'
                            fqcremove.append(row[0])

                    #if we still want that data, turn it into floats and added to the datadict
                    if writeto:
                            templist = []
                            for a in row[1:]:
                                templist.append(a)
                            datadict[canalyte][clevel][row[0]]= map(float,templist)

                #remove those items from the fqclist that we have decided are not being added.
                for x in fqcremove:
                    if x in fqclisttemp:
                        fqclist.remove(x)
                        print x, 'duplicates data already uploaded and will not be used'

    return datadict, fqclisttemp
        
#setup a dict for fqc:filelocations
fqcdict = {}
#get which assay is being used
parameterfile = os.path.join(parametersloc, assaylist[assaycheck()] + '.csv')



for newfile in os.listdir(inputloc):
    #print out a list of files that are in the input location
    print 'checking the following file: ',newfile
    #default to adding the file to the list of files to process
    addfilecheck = True
    #check to see if there is a FQC number in the file
    fqctest = isfqc.search(newfile)
    if fqctest:
        #find the number within the fqctest
        isnum = re.search('\d+',str("".join(fqctest.group().split())).lower())
        #pull out the FQC number
        fqcname = 'fqc-'+str("".join(isnum.group().split()))
        #check to see if we have an isodate
        datetest = isisodate.search(newfile)
        if datetest:
        #if there is a date put the FQC number and date together
            fqccomp = fqcname + '\n' + str("".join(datetest.group().split()))
        #check for duplicate files in the keys of fqcdict        
            if fqccomp in fqcdict.keys():
                print fqcname + ' has already had one file uploaded.\nIf a second is uploaded it will override the first.'
                addfile = raw_input('If you wish to proceed with overriding the file please type yes: ')
                #if its a duplicate FQC# and I am not told to overwrite, set it so its not added to dict and move on
                if addfile.lower() != 'yes':
                    aadfilecheck = False
                    print newfile + ' is a duplicate and was not processed'
        #if it does not have a iso date move on
        else:
            addfilecheck = False
            print newfile + ' does not have a valid iso date and was not processed'
    #if it does not have a valid FQC number move
    else:
        addfilecheck = False
        print newfile + ' does not have a valid fqc number and was not processed'
    #if we are to add the file add it to the fqcdict along with the pathway
    if addfilecheck:
        fqcdict[fqccomp] = {'fileloc':os.path.join(inputloc,newfile)}
print ' '       

#open the parameter file
parameterlist, parameterdict = (getparameters(parameterfile))
#setup a list by FQC number of the fqcnumbers to be loaded
fqclist = sorted(fqcdict.keys())

#check to see if there is correct instrument folder and make one if there isn't
#instfolder = os.path.join(outputloc, parameterlist[1])
#if not os.path.exists(instfolder):
    #os.makedirs(instfolder)

#check to see if there is correct assay folder and make one if there isn't
#assayfolder = os.path.join(instfolder, parameterlist[0])
#if not os.path.exists(assayfolder):
    #os.makedirs(assayfolder)

#--------------------------------------------------------------------------------
#check to see what type of instrument is being run and see what path we go down
if parameterlist[1].lower() == 'lcms':
    from lcmsdatasort import *

    #we will need to skip IS files
    isis = re.compile('[d|D]\d')

    #setup to get the data
    dataforfile = {}
    #get the qa-number for the controls
    controlqanum = qanumcheck()
    print ' '
    
    #check for a folder in output related to this qanum if there isn't one make it
    controlqafolder = os.path.join(outputloc,
                                   parameterlist[1].lower()+'-'+parameterlist[0].lower()+'-'+controlqanum)
    if not os.path.exists(controlqafolder):
        os.makedirs(controlqafolder)

    #get the scriptfolder
    forscriptfolder = scriptfilemaker(controlqafolder)

    #get the initialdata
    initialdict = lcmsinitialdata(forscriptfolder)

    #get previous data
    dataforfile,fqcrunlist = previousdatafun(forscriptfolder, fqclist) 

   #terms that will invalidate control usage
    non_control_list = ['dilution', 'new', 'old']
    
    for fqc in fqcrunlist:
        #call datasort and get back the dict
        workingdata = lcmsdatasort(fqcdict[fqc]['fileloc'])
        #go through the data by analyte
        for analyte in workingdata.keys():
            #if the analyte is a IS move on
            istest = isis.search(analyte)
            if istest:
                pass
            else:
                dataforfile.setdefault(analyte,{})
                analytedict = workingdata[analyte]
                #only looking for data for those level specified
                for level in sorted(parameterdict.keys()):
                    measurelist = []
                    #need to turn the sampline numbers into int so they sort right and we see the data in order
                    for item in sorted(map(int,analytedict.keys())):
                        #but I still need the string of the item to get the data out of the workingdata dict
                        sampleline = str(item)
                        #ignore those dilutions, old controls, new controls in the data
                        if any(s in analytedict[sampleline]['Name'].lower() for s in non_control_list):
                            pass
                        #check the line for the current level we are looking at add the nominal value, and the measured value
                        elif level in analytedict[sampleline]['Name'].lower():
                            dataforfile[analyte].setdefault(level,{})
                            dataforfile[analyte][level].setdefault('n_values',[])
                            dataforfile[analyte][level]['n_values'].append(float(analytedict[sampleline]['Std. Conc']))
                            measurelist.append(analytedict[sampleline]['ng/mL'])
                        #if the assay is cannabinoids check for the control 5-8 and add them to the currect data group
                        elif parameterlist[0] == 'cannabinoids' and level.startswith('control'):
                            addlevel = 'control ' + str(int(level.split(' ')[1])+4)
                            if addlevel in analytedict[sampleline]['Name'].lower():
                                dataforfile[analyte][level]['n_values'].append(float(analytedict[sampleline]['Std. Conc']))
                                measurelist.append(analytedict[sampleline]['ng/mL'])
                        #if the list actually has items in it add them to dict
                        if len(measurelist) > 0:
                            dataforfile[analyte][level][fqc]= map(float,measurelist)

    #writeout the data for the script to use next time
    outputscriptfilename = 'script data-' + date + '-.csv'
    outputscriptfile = os.path.join(forscriptfolder, outputscriptfilename)
    scriptwo = []
    for analyte in dataforfile:
        scriptwo.append(['analyte',analyte])
        for level in dataforfile[analyte]:
            scriptwo.append(['level',level])
            for fqc in dataforfile[analyte][level]:
                templist = [fqc]
                for value in dataforfile[analyte][level][fqc]:
                    templist.append(value)
                scriptwo.append(templist)

    with open(outputscriptfile, 'wb') as op:
        wo = csv.writer(op)
        for row in scriptwo:
            wo.writerow(row)

    #by analyte make the graph and the the writeout file
    for analyte in sorted(dataforfile.keys()):
        #check for the analyte file and if its not there make it
        analytefolder = os.path.join(controlqafolder, analyte)
        if not os.path.exists(analytefolder):
            os.makedirs(analytefolder)

        #make a human write out file
        humanwo = [['Compiled on:',readdate],['','']]     
        #setup the file names, the units, tolerances for the graph and the graphdict
        name = analyte + ' ' + date
        graphfile = os.path.join(analytefolder, name + '.png')
        outputfile = os.path.join(analytefolder, name + '.csv')
        humanwo.append([analyte,''])
        humanwo.append(['',''])
        units = 'ng/mL'
        tolerance = [0.7,0.8,0.9,1.1,1.2,1.3]
        dataforgraph = {}
        analytedict = dataforfile[analyte]

        #again we are only interested in those level laid out in the parameter file
        for level in sorted(parameterdict.keys()):
            dataforgraph[level] = {}
            #check the initialdatadict to see if intial data, if don't or never did set it to 'none'
            if int(parameterdict[level][0]) == 1:
                try:
                    dataforgraph[level]['i_mean'] = float(initialdict[analyte.lower()][level]['mean'])
                except:
                    print 'No inital data found for ' + analyte + ' at ' + level
                    dataforgraph[level]['i_mean'] = 'none'
            else:
                dataforgraph[level]['i_mean'] = 'none'
            
            leveldict = analytedict[level]
            #check to see if we have more then one value for the nominal value if we do let the user know
            if len(set(leveldict['n_values'])) > 1:
                print analyte + ' ' + level + ' has inconsistant nominal values'

            #because of round in targetlynx we have to manually set the level for THC-COOH for control 3 
            if analyte.lower() == 'thc-cooh' and level == 'control 3':
                dataforgraph[level]['n_value'] = 125.0
            #otherwise we use the most common value in the n_value list as the nonimal level
            else:
                dataforgraph[level]['n_value'] = stats.mode(map(float,leveldict['n_values']))[0][0]

            dataforgraph[level]['xlabels'] = []
            dataforgraph[level]['ydata'] = []

            #going list of fqc numbers in order we add them to the dataforgraph dict
            for item in sorted(leveldict.keys()):
                if item == 'n_values':
                    pass
                else:
                    dataforgraph[level]['xlabels'].append(item)
                    dataforgraph[level]['ydata'].append(leveldict[item])

#generate the graphs and get bunch of stats back.
#because I am lazy this reports out the aggregated stats, the range stats, the nominal value and initial value
        resultsdict = xmr_plot(dataforgraph,tolerance,units,analyte,graphfile)

        #work on the writout
        for level in sorted(dataforfile[analyte].keys()):
            humanwo.append([level,'nominal value:', resultsdict[level]['n_value'],'initial measurement:',resultsdict[level]['i_mean']])
            humanwo.append(['FQC#','Date Run','Run Mean','Run St. Dev.', 'Run CV%','Individual Measurements'])
            for fqc in sorted(dataforfile[analyte][level].keys()):
                if fqc == 'n_values':
                    pass
                else:
                    t_mean = round(np.mean(dataforfile[analyte][level][fqc]),2)
                    t_std = round(np.std(dataforfile[analyte][level][fqc]),3)
                    t_cv = round((t_std/t_mean)*100,3)
                    templist = [fqc.split('\n')[0],fqc.split('\n')[1], str(t_mean)+units,
                                str(t_std)+units, str(t_cv)+'%']
                    for a in dataforfile[analyte][level][fqc]:
                        templist.append(str(a) + units)
                    humanwo.append(templist)
            humanwo.append(['',''])
            humanwo.append(['Aggregate Mean', 'Aggregate St. Dev.', 'Aggregate %CV', 'Lower Control Limit','Upper Control Limit'])
            humanwo.append(resultsdict[level]['agg'])
            humanwo.append(['',''])
            humanwo.append(['Range Mean','Range St. Dev.','Range %CV', 'Range Upper Control', 'Individual Calculations'])
            humanwo.append(resultsdict[level]['ragg'] + resultsdict[level]['rdata'])
            humanwo.append(['',''])
        humanwo.append(['',''])

        #writeout the file
        with open(outputfile, 'wb') as op:
            wo = csv.writer(op)
            for row in humanwo:
                wo.writerow(row)

    
    #check for a folder in output related to this qanum if there isn't one make it
    olduploadscon = os.path.join(controlqafolder,'old uploads')
    if not os.path.exists(olduploadscon):
        os.makedirs(olduploadscon)

    print ' '
    
    for fqc in fqclist:
        shutil.copy(fqcdict[fqc]['fileloc'],os.path.join(olduploadscon,fqc.split('\n')[0] + ' ' + date))
        print fqcdict[fqc]['fileloc'] + ' copied'

    print ' '

    print 'Type all if you want to delete all input files,\ntype none to delete none of the input files,\ntype some to delete select files'
    deletecheck = raw_input('Please enter all, none, or some:')

    if deletecheck.lower() == 'all':
        for newfile in os.listdir(inputloc):
            os.remove(os.path.join(inputloc,newfile))
    elif deletecheck.lower() == 'some':
        for newfile in os.listdir(inputloc):
            delete = raw_input('Enter delete to delete ' + newfile + 'from the input folder: ')
            if delete.lower() == 'delete':
                os.remove(os.path.join(inputloc,newfile))

    raw_input('hit enter to close the program')
    
                           

            

                

                    
            
    
    
                    
        




    
               
                                    
        





        
