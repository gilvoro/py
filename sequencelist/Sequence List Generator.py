#initial setup
#updated 2016-09-22
#--------------------------------------------------------------------------------------------------------------

import os
import csv
import re
import datetime
import sys
import calendar
import Tkinter, tkFileDialog
import subprocess
import getpass


cyear = int(datetime.date.today().strftime('%Y'))
currentdate = datetime.date.today().isoformat()
solventblanknumber = 1
sequencelistdir = 'C:\\scriptfiles\\sequence lists'
desktop = os.path.expanduser('~\Desktop')

#list of letters to add to sample names if there are repeats
alphabet = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
            'q','r','s','t','u','v','w','x','y','z')

#row on the trays for the LCMS
rowconversion = ('A','B','C','D','E','F')

#intial questions to get the date if not the current one    
yearquestion = 'Please enter the year for this run (YYYY): '
monthquestion = 'Please enter the month for this run (MM): '
dayquestion = 'Please enter the day for this run (DD): '


#lcms specific functions
#--------------------------------------------------------------------------------------------------------------

#check user entered year and return it
def getyear(text):
    year = raw_input(text)
    if len(year) == 2:
        year = '20' + year
    if year.lower() == 'quit' or year.lower() == 'q' or year.lower() == 'exit':
        sys.exit()        
    elif year.isdigit():
        if int(year) < cyear or int(year) > cyear + 1 or len(year) != 4:
            yearquestion = str(year) + ' is not a valid entry.\nPlease enter the year for this run (YYYY): '
            year = getyear(yearquestion)
    else:
        yearquestion = str(year) + ' is not a valid entry.\nPlease enter the year for this run (YYYY): '
        year = getyear(yearquestion)

    return year

#check user entered month and return it
def getmonth(text):
    month = raw_input(text)
    if len(month) == 1:
        month = '0' + month
    if month.lower() == 'quit'or month.lower() == 'q' or month.lower() == 'exit':
        sys.exit()        
    elif month.isdigit():
        if int(month) < 1 or int(month) > 12 or len(month) != 2:
            monthquestion = str(month) + ' is not a valid entry.\nPlease enter the month for this run (MM): '
            month = getmonth(monthquestion)
    else:
        monthquestion = str(month) + ' is not a valid entry.\nPlease enter the month for this run (MM): '
        month = getmonth(monthquestion)

    return month

#check user entered day and return it
def getday(text):
    day = raw_input(text)
    if len(day) == 1:
        day = '0' + day
    if day.lower() == 'quit' or day.lower() == 'q' or day.lower() == 'exit':
        sys.exit()        
    elif day.isdigit():
        if int(day) < 1 or int(day) > calendar.monthrange(int(year),int(month))[1] or len(day) != 2:
            dayquestion = str(day) + ' is not a valid entry.\nPlease enter the day for this run (DD): '
            day = getday(dayquestion)
    else:
        dayquestion = str(day) + ' is not a valid entry.\nPlease enter the day for this run (DD): '
        day = getday(dayquestion)

    return day

#check user entered well number and returns well with an uppercase letter for the lcms
def getinitialwellnumlcms(text):
    iswellnum = re.compile('[1|2]:[A-E],[1-8]')
    wellnum = raw_input(text)
    if wellnum.lower() == 'quit' or wellnum.lower() == 'q' or wellnum.lower() == 'exit':
        sys.exit()

    if iswellnum.match(wellnum.upper()):
        return wellnum.upper()

    else:
        print "nope"
        wellnum = getinitialwellnumlcms(wellnum+' is not a vaild well number.\nPlease enter the first well used: ')

#takes the numeric well position and outputs the well number for lcms
def getwellnum(position):
    if position > 48:
        tray = '2'
        position = position - 48
    else:
        tray = '1'
        
    row = rowconversion[((position-1)/8)]
        
    if position%8 == 0:
        col = '8'
    else:
        col = str(position%8)
        
    wellnum = tray + ':' + row + ',' + col
    
    return wellnum 

#takes well number and gets numeric well position
def getpostion(wellnum):
    position = 0
    if wellnum[0] == '2':
        position += 48

    position += rowconversion.index(wellnum[2])*8

    position += int(wellnum[4])

    return position

#gets a sample line for the output file, sample+date, sample, well number, sampletype
def sampleline(samplename, date, position, sampletype):
    datedsamplename = samplename + ' ' + date
    
    return [datedsamplename, samplename, position, sampletype] + sequencefiller

#gives increasing number of solvent blank as the list is generated
def solventline():
    global solventblanknumber
    solventblank = 'Solvent Blank ' + str(solventblanknumber)
    datedsolventblank = solventblank + ' ' + rdate
    solventblanknumber += 1
    
    return [datedsolventblank, solventblank, initialwellnum, 'Solvent']  + sequencefiller

#adds cc blanks to the sequence
def ccline(position):
    returnlist = []
    if position == 'start':
        x = 0
        while x < 5:
            returnlist.append(['Starting Blank ' + rdate + ' inj-' + alphabet[x], 'Starting Blank',
                               initialwellnum, 'Solvent']+ sequencefiller)
            x +=1

    if position == 'end':
        x = 0
        while x < 5:
            returnlist.append(['Ending Blank ' + rdate + ' inj-' + alphabet[x], 'Ending Blank',
                               initialwellnum, 'Solvent']+ sequencefiller)
            x +=1

    return returnlist
            

#takes items from the standard list formats them to go into the dictionary
def addstandard(placelist, samplename, repeats, blanks,curpos,sampletype):
    templist = standarddict[placelist]
    
    x = 0    

#if the sequence list format lists after, the program will add a blank after each injection
    if blanks.lower() == 'after':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
                templist.append(['solvent'])
                x += 1
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
            templist.append(['solvent'])

#if the sequence list format lists bracket, the program will add a blank before and after each injection
    elif blanks.lower() == 'bracket':
        templist.append(['solvent'])
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
                x += 1
            templist.append(['solvent'])
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
            templist.append(['solvent'])

#if the sequence list format lists set, the program will add a blank after all the injection
    elif blanks.lower() == 'set':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
                x += 1
            templist.append(['solvent'])
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
            templist.append(['solvent'])

    elif blanks.lower() == 'before':
            templist.append(['solvent'])
            if repeats.lower() != 'none' and int(repeats) > 1:
                while x < int(repeats):
                    templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
                    x += 1
            else:
                templist.append(sampleline(samplename,rdate,curpos,sampletype))

#if the squence list format lists none, the program will add no blanks            
    else:
        if repeats.lower() != 'none' and int(repeats) > 1:
            x = 0
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
                x += 1
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
                            
            
#takes MOR items from the standard list formats them to go into the dictionary            
def MORaddstandard(placelist, samplename, repeats, blanks,curpos,sampletype):
    templist = standarddict[placelist]

#if the sequence list format lists after, the program will add a blank after each injection
    if blanks.lower() == 'after':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
                templist.append(['solvent'])
                templist.append(['end'])
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
            templist.append(['solvent'])
            templist.append(['end'])

#if the sequence list format lists bracket, the program will add a blank before and after each injection
    elif blanks.lower() == 'bracket':
        templist.append(['solvent'])
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
            templist.append(['solvent'])
            templist.append(('end'))
            
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
            templist.append(['solvent'])
            templist.append(['end'])

#if the sequence list format lists set, the program will add a blank after all the injection
    elif blanks.lower() == 'set':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
            templist.append(['solvent'])
            templist.append(('end'))
            
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
            templist.append(['solvent'])
            templist.append(['end'])

#if the squence list format lists none, the program will add no blanks         
    else:
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(sampleline(samplename + ' inj-' + alphabet[x],rdate,curpos,sampletype))
                templist.append(['end'])
        else:
            templist.append(sampleline(samplename,rdate,curpos,sampletype))
            templist.append(['end'])

#gcms specific functions
#--------------------------------------------------------------------------------------------------------------
#return a solvent blank line for gcms
def solventlinegcms():
        global solventblanknumber
        if solventblanknumber < 2:
            solventblank = 'MeOH Blank 0' + str(solventblanknumber)
        solventblank = 'MeOH Blank ' + str(solventblanknumber)
        
        solventblanknumber += 1

        return ['Sample', '100', solventblank, 'BLANK',solventblank] + sequencefillerpartone + [''] + sequencefillerparttwo

#return a sample line for gcms
def samplelinegcms(samplename, position, sampletype, level):
    return [sampletype, position, samplename, gcmsmethod, samplename] + sequencefillerpartone + [level] + sequencefillerparttwo

#check that the user enter vial number is valid
def getvial(text):
    vial = raw_input(text)
    if vial == 'quit' or vial == 'q' or vial == 'exit':
        sys.exit()   
    if vial.isdigit():
        if 1 <= int(vial) <= 100:
            vial = int(vial)
        else:
            vial = getvial(str(vial) + ' is not a valid entry.\nPlease enter the starting vial: ')
    else:
        vial = getvial(str(vial) + ' is not a valid entry.\nPlease enter the starting vial: ')

    return vial

#check that the user enter methanol blank will work
def getmethanol(text):
    methanolnumber = raw_input(text)
    if not methanolnumber.isdigit():
        methanolnumber = getmethanol(str(methanolnumber)+ ' is not a valid entry.\nPlease enter the first methanol blank number: ')
    else:
        methanolnumber = int(methanolnumber)

    return methanolnumber

#takes items from the standard list formats them to go into the dictionary but for gcms
def addstandardgcms(placelist, samplename, repeats, blanks,curpos,sampletype,level):
    templist = standarddict[placelist]
    
    x = 0    
        
    if blanks.lower() == 'after':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x], curpos, sampletype, level))
                templist.append(['solvent'])
                x += 1
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            templist.append(['solvent'])

    elif blanks.lower() == 'bracket':
        templist.append(['solvent'])
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
                x += 1
            templist.append(['solvent'])
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            templist.append(['solvent'])

    elif blanks.lower() == 'set':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
                x += 1
            templist.append(['solvent'])
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            templist.append(['solvent'])

    elif blanks.lower() == 'before':
            templist.append(['solvent'])
            if repeats.lower() != 'none' and int(repeats) > 1:
                while x < int(repeats):
                    templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
                    x += 1
            else:
                templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            
    else:
        if repeats.lower() != 'none' and int(repeats) > 1:
            x = 0
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
                x += 1
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))

#takes MOR items from the standard list formats them to go into the dictionary            
def MORaddstandardgcms(placelist, samplename, repeats, blanks,curpos,sampletype,level):
    templist = standarddict[placelist]
    if blanks.lower() == 'after':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
                templist.append(['solvent'])
                templist.append(['end'])
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            templist.append(['solvent'])
            templist.append(['end'])

    elif blanks.lower() == 'bracket':
        templist.append(['solvent'])
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
            templist.append(['solvent'])
            templist.append(('end'))
            
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            templist.append(['solvent'])
            templist.append(['end'])

    elif blanks.lower() == 'set':
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
            templist.append(['solvent'])
            templist.append(('end'))
            
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            templist.append(['solvent'])
            templist.append(['end'])

    else:
        if repeats.lower() != 'none' and int(repeats) > 1:
            while x < int(repeats):
                templist.append(samplelinegcms(samplename + ' inj-' + alphabet[x],curpos, sampletype, level))
                templist.append(['end'])
        else:
            templist.append(samplelinegcms(samplename,curpos, sampletype, level))
            templist.append(['end'])
    
#collect information form the user
#--------------------------------------------------------------------------------------------------------------
#get the current available assay formats
assaylist = []
if os.path.exists('Z://labtools//jimscripts//sequence list formats//'):
    assayfolder = 'Z://labtools//jimscripts//sequence list formats//'
else:
    assayfolder = 'R://labtools//jimscripts//sequence list formats//'
    
x = 1
for f in sorted(os.listdir(assayfolder)):
    if f.endswith('.csv'):
        assaylist.append(f.split('.')[0])
        print str(x) + '.) ' +f.split('.')[0]
        x += 1


#get which assay the user wants to build a sequence for
whichnum = raw_input('Please enter the number of the assay you would like to use: ')
if not whichnum.isdigit():
    assaytype = os.path.join(assayfolder, 'can blood lcms.csv')
    assayname = 'can'
    assayinstrument = 'lcms'
elif int(whichnum) - 1 in range(len(assaylist)):
    whichassay = assaylist[int(whichnum)-1]
    assaytype = os.path.join(assayfolder, whichassay + '.csv' )
    assayname = whichassay.split(' ')[0]
    assayinstrument = whichassay.split(' ')[-1]
else:
    assaytype = os.path.join(assayfolder, 'can blood lcms.csv')
    assayname = 'can'
    assayinstrument = 'lcms'

#setup and get the csv file
root = Tkinter.Tk()
root.withdraw()
print 'Please select csv file'
fileloc = tkFileDialog.askopenfilename(defaultextension = '.csv',
                                       filetypes = [('CSV File','.csv')],
                                       initialdir = desktop,
                                       title ='Please select csv file')

if fileloc == '':
    sys.exit()
    
if assayinstrument == 'lcms':    
#check if the user wants to use the todays date, if not get the date they want
    usecurrentdate = raw_input("Would you like to use today's date for this run?(y/n): ")
    if usecurrentdate.lower() == 'quit' or usecurrentdate.lower() == 'q' or usecurrentdate.lower() == 'exit':
        sys.exit()
    elif usecurrentdate.lower() == 'n' or usecurrentdate.lower() == 'no':
        year = getyear(yearquestion)
        month = getmonth(monthquestion)
        day = getday(dayquestion)
        rdate = year + '-' + month + '-' + day
    else:
        rdate = currentdate

#check if the user wants to use 1:A,1 and if not get the first well
    iwnq = raw_input('Is the first well used 1:A,1? (y/n): ')
    if iwnq.lower() == 'quit' or iwnq.lower() == 'q' or iwnq.lower() == 'exit':
        sys.exit()
    if iwnq.lower() == 'n' or iwnq.lower() == 'no':
        initialwellnum = getinitialwellnumlcms('Please enter the first well used: ')
    else:
        initialwellnum = '1:A,1'

elif assayinstrument == 'gcms':
#get the starting vial position
    initialvial = getvial('Please enter the vial number for the first sample: ')
    solventblanknumber = getmethanol('Please enter the number of the first Methanol Blank: ')
    rdate = currentdate

else:
    print 'Whoa whoa whoa, nothing I can do boss.  Need More code'

#build the  standards template
#--------------------------------------------------------------------------------------------------------------
#open the standard's file
standardlist = []
print assaytype
with open (assaytype, 'rU') as csvfile:
    raw_data = csv.reader(csvfile)
    for row in raw_data:
        standardlist.append(row)


standarddict = {'BORlist':[], 'MORlist':[], 'EORlist':[],
                'BORlistUr':[], 'MORlistUr':[], 'EORlistUr':[]}
#setup a dictionary so that the same standard can be used in a variety of places in the run without a new position
uniquedict = {}

if assayinstrument == 'gcms':
    curpos = initialvial
    urinefirst = False
    gcmsmethod = standardlist[3][1]
    sequencefillerpartone = standardlist[4][1:2]
    sequencefillerparttwo = standardlist[5][1:4]

    for row in standardlist:
        if standardlist.index(row) == 8:
            if row[7].lower() == 'urine' or row[7].lower() == 'ur' or row[7].lower() == 'u':
                urinefirst = True

        if standardlist.index(row) < 8:
            pass

        else:
#enter the row into the dictionary of unique standards if not already there
            if  not row[0] in uniquedict.keys():
                uniquedict.setdefault(row[0],curpos)
                curpos += 1
#enter the row into the dictionary of unique standards

#Decided if this is a urine or other control and add the apporiate values            
            if row[7].lower() == 'urine' or row[7].lower() == 'ur' or row[7].lower() == 'u':
                standardname = row[0] + row[10] + ' Ur'
                matrixdict = 'Ur'
            else:
                standardname = row[0] + row[10]
                matrixdict = ''
                
            if row[1].lower() != 'none':
                addstandardgcms('BORlist'+matrixdict, standardname,row[1],row[2],uniquedict[row[0]],row[8],row[9])
            if row[3].lower() != 'none':
               MORaddstandardgcms('MORlist'+matrixdict, 'MOR ' + standardname,row[3],row[4],uniquedict[row[0]],row[8],row[9])
            if row[5].lower() != 'none':
                addstandardgcms('EORlist'+matrixdict, 'EOR ' + standardname,row[5],row[6],uniquedict[row[0]],row[8],row[9])

    
if assayinstrument == 'lcms':
    curpos = getpostion(initialwellnum) + 1
    urinefirst = False
    sequencefiller = standardlist[3][1:]
    
    for row in standardlist:
#setup to do blood and urine in the same sequence not used
        #if standardlist.index(row) == 6:
            #if row[7].lower() == 'urine' or row[7].lower() == 'ur' or row[7].lower() == 'u':
                #urinefirst = True
                
        if standardlist.index(row) < 6:
            pass
        else:
#set well number and dictionary of unique standards if not already there
            if  not row[0] in uniquedict.keys():
                curwellnum = getwellnum(curpos)
                uniquedict.setdefault(row[0],curwellnum)
                curpos += 1
#Decided if this is a urine or other control and add the apporiate values            
            if row[7].lower() == 'urine' or row[7].lower() == 'ur' or row[7].lower() == 'u':
                standardname = row[0] + row[9] + ' Ur'
                matrixdict = 'Ur'
            else:
                standardname = row[0] + row[9]
                matrixdict = ''

#add the standards to the apporiate                
            if row[1].lower() != 'none':
                addstandard('BORlist'+matrixdict, standardname,row[1],row[2],uniquedict[row[0]],row[8])
            if row[3].lower() != 'none':
               MORaddstandard('MORlist'+matrixdict, 'MOR ' + standardname,row[3],row[4],uniquedict[row[0]],row[8])
            if row[5].lower() != 'none':
                addstandard('EORlist'+matrixdict, 'EOR ' + standardname,row[5],row[6],uniquedict[row[0]],row[8])
    
MORcontrolsUr = 0
MORcontrols = 0
for item in standarddict['MORlistUr']:
    if item[0] == 'solvent' or item[0] == 'end':
        pass
    else:
        MORcontrolsUr += 1

for item in standarddict['MORlist']:
    if item[0] == 'solvent' or item[0] == 'end':
        pass
    else:
        MORcontrols += 1

#build the list of ct numbers
#---------------------------------------------------------------------------------------------------------------
rawlist = []
with open(fileloc,'rU')as csvfile:
    raw_data = csv.reader(csvfile)
    for row in raw_data:
        rawlist.append(row)


ctlist = []
ctlistUr = []
isctnum = re.compile('\d\d\d\d\d\d')
ismatrixlisted = re.compile('[a-zA-Z]/[a-zA-Z]')
sampleletter = re.compile('[a-zA-Z]')
for row in rawlist:
    for item in row:
#Test to see if the matrix is listed and if it is put in the right spot
            l = ismatrixlisted.search(item)
            m = isctnum.search(item)
            if m:
                if l:
                    matrixtest = l.group().lower()
                    if matrixtest[0] == 'u':
                        templist = ctlistUr
                    else:
                        templist = ctlist
                else:
                    templist = ctlist
                ctnum = m.group()
                sampleletterloc = m.end()
                try:
                    n = sampleletter.match(item[sampleletterloc])
                    if n:
                        name = ctnum + item[sampleletterloc].upper()
                    else:
                        name = ctnum+'A'
                except:
                    name = ctnum+'A'
                templist.append(name)
            else:
                pass

ctlist = sorted(ctlist)
ctlistUr = [x + ' Ur' for x in ctlistUr]
ctlistUr = sorted(ctlistUr)
sequencelist = []

#build sequence list for LCMS
#--------------------------------------------------------------------------------------------------------------
def sequencelistbuilder(ctnums, MORcount, matrixcontrol):
    
    global curpos

    sequencelist.append(solventline())
    
    if standardlist[2][1].lower() == 'even' or standardlist[2][1].lower() == 'evenly':
        controlcountmax = len(ctnums)/(MORcount + 1)
    else:
        controlcountmax = int(standardlist[2][1])

    for item in standarddict['BORlist'+ matrixcontrol]:
        if item[0] == 'solvent':
            sequencelist.append(solventline())
        else:
            sequencelist.append(item)

    try:
        samplerepeats = int(standardlist[1][3])
    except:
        samplerepeats = 1
        
    samplesfromlastcontrol = 0
    MORcontrolsrun = 0
    MORlistpostion =  0

    for item in ctnums:
        repeated = 0
        if samplesfromlastcontrol >= controlcountmax and MORcontrolsrun < MORcount:
            x = 0
            templist = standarddict['MORlist'+ matrixcontrol]
            while x < 1:
                if templist[MORlistpostion][0] == 'solvent':
                    sequencelist.append(solventline())
                    MORlistpostion += 1
                
                elif templist[MORlistpostion][0] == 'end':
                    MORlistpostion +=1
                    samplesfromlastcontrol = 0
                    x = 1
                
                else:
                    sequencelist.append(templist[MORlistpostion])
                    MORlistpostion +=1
                    MORcontrolsrun +=1

            if standardlist[1][1].lower() == 'after':
                if samplerepeats == 1:
                    sequencelist.append(sampleline(item, rdate, getwellnum(curpos),'Analyte'))
                    sequencelist.append(solventline())
                else:   
                    while repeated < samplerepeats:
                        sequencelist.append(sampleline(item + ' inj-' + alphabet[repeated], rdate, getwellnum(curpos),'Analyte'))
                        sequencelist.append(solventline())
                        repeated += 1
                samplesfromlastcontrol += 1
                curpos += 1

            else:
                if samplerepeats == 1:
                    sequencelist.append(sampleline(item, rdate, getwellnum(curpos),'Analyte'))

                else:   
                    while repeated < samplerepeats:
                        sequencelist.append(sampleline(item + ' inj-' + alphabet[repeated], rdate, getwellnum(curpos),'Analyte'))
                        repeated += 1
                samplesfromlastcontrol += 1
                curpos += 1
    
        else:
            if standardlist[1][1].lower() == 'after':
                if samplerepeats == 1:
                    sequencelist.append(sampleline(item, rdate, getwellnum(curpos),'Analyte'))
                    sequencelist.append(solventline())
                else:   
                    while repeated < samplerepeats:
                        sequencelist.append(sampleline(item + ' inj-' + alphabet[repeated], rdate, getwellnum(curpos),'Analyte'))
                        sequencelist.append(solventline())
                        repeated += 1
                samplesfromlastcontrol += 1
                curpos += 1

            else:
                if samplerepeats == 1:
                    sequencelist.append(sampleline(item, rdate, getwellnum(curpos),'Analyte'))

                else:   
                    while repeated < samplerepeats:
                        sequencelist.append(sampleline(item + ' inj-' + alphabet[repeated], rdate, getwellnum(curpos),'Analyte'))
                        repeated += 1
                samplesfromlastcontrol += 1
                curpos += 1


    for item in standarddict['EORlist'+ matrixcontrol]:
        if item[0] == 'solvent':
            sequencelist.append(solventline())
        else:
            sequencelist.append(item)

#build sequence list for GCMS
#--------------------------------------------------------------------------------------------------------------
def sequencelistbuildergcms(ctnums, MORcount, matrixcontrol):
    
    global curpos
    
    sequencelist.append(solventlinegcms())
    
    if standardlist[2][1].lower() == 'even' or standardlist[2][1].lower() == 'evenly':
        controlcountmax = len(ctnums)/(MORcount + 1)
    else:
        controlcountmax = int(standardlist[2][1])

    for item in standarddict['BORlist'+ matrixcontrol]:
        if item[0] == 'solvent':
            sequencelist.append(solventlinegcms())
        else:
            sequencelist.append(item)

    samplesfromlastcontrol = 0
    MORcontrolsrun = 0
    MORlistpostion =  0

    for item in ctnums:
        if samplesfromlastcontrol >= controlcountmax and MORcontrolsrun < MORcount:
            x = 0
            templist = standarddict['MORlist'+ matrixcontrol]
            while x < 1:
                if templist[MORlistpostion][0] == 'solvent':
                    sequencelist.append(solventlinegcms())
                    MORlistpostion += 1
                
                elif templist[MORlistpostion][0] == 'end':
                    MORlistpostion +=1
                    samplesfromlastcontrol = 0
                    x = 1
                
                else:
                    sequencelist.append(templist[MORlistpostion])
                    MORlistpostion +=1
                    MORcontrolsrun +=1

            if standardlist[1][1].lower() == 'after':
                sequencelist.append(samplelinegcms(item, curpos,'Analyte',''))
                sequencelist.append(solventlinegcms())
                samplesfromlastcontrol += 1
                curpos += 1

            else:
                sequencelist.append(samplelinegcms(item, curpos,'Analyte',''))
                samplesfromlastcontrol += 1
                curpos += 1
    
        else:
            if standardlist[1][1].lower() == 'after':
                sequencelist.append(samplelinegcms(item, curpos,'Analyte',''))
                sequencelist.append(solventlinegcms())
                samplesfromlastcontrol += 1
                curpos += 1

            else:
                sequencelist.append(samplelinegcms(item, curpos,'Analyte',''))
                samplesfromlastcontrol += 1
                curpos += 1


    for item in standarddict['EORlist'+ matrixcontrol]:
        if item[0] == 'solvent':
            sequencelist.append(solventlinegcms())
        else:
            sequencelist.append(item)

#choose what goes to the sequence builder in what order
#---------------------------------------------------------------------------------------------------------------        
if assayinstrument == 'lcms':
    sequencelist = sequencelist + ccline('start')
    if len(ctlistUr) < 1:
        sequencelistbuilder(ctlist,MORcontrols,'')
    elif len(ctlist) < 1:
        sequencelistbuilder(ctlistUr,MORcontrolsUr,'Ur')
    else:
        if urinefirst:
            sequencelistbuilder(ctlistUr,MORcontrolsUr,'Ur')
            sequencelistbuilder(ctlist,MORcontrols,'')
        else:
            sequencelistbuilder(ctlist,MORcontrols,'')
            sequencelistbuilder(ctlistUr,MORcontrolsUr,'Ur')
            
    sequencelist.append(solventline())
    sequencelist = sequencelist + ccline('end')
    
if assayinstrument == 'gcms':
    if len(ctlistUr) < 1:
        sequencelistbuildergcms(ctlist,MORcontrols,'')
    elif len(ctlist) < 1:
        sequencelistbuildergcms(ctlistUr,MORcontrolsUr,'Ur')
    else:
        if urinefirst:
            sequencelistbuildergcms(ctlistUr,MORcontrolsUr,'Ur')
            sequencelistbuildergcms(ctlist,MORcontrols,'')
        else:
            sequencelistbuildergcms(ctlist,MORcontrols,'')
            sequencelistbuildergcms(ctlistUr,MORcontrolsUr,'Ur')

    sequencelist.append(solventlinegcms())



if assayinstrument == 'lcms':
    dl = ','
    endtag = ').csv'
    
elif assayinstrument == 'gcms':
    dl = '\t'
    endtag = ').txt'
    
else:
    dl = ';'
    endtag = '.txt'

opfilename = assayname + ' ' + rdate + ' (' + datetime.datetime.now().strftime('%H%M%S')+ endtag
outputfile = os.path.join(sequencelistdir, opfilename)

with open(outputfile,'wb')as csvfile:
    wo = csv.writer(csvfile,delimiter = dl)
    for item in sequencelist:
        wo.writerow(item)


os.startfile(sequencelistdir)
       
            
    
