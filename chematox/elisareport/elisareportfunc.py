import re
import sys
import os
import datetime
import pyPdf
import json
from calendar import monthrange


#check to see if an entered date is valid
def getdate():
    isdate = re.compile('\d\d\d\d-\d\d-\d\d')
    entereddate = raw_input('Please enter in the following format YYYY-MM-DD: ')
    datetest = isdate.match(entereddate)
#let them out if they want out
    if entereddate.lower() == 'quit' or entereddate.lower() == 'q' or entereddate.lower() == 'exit':
        sys.exit()
#if we have the date in isoformat
    elif datetest:
#try to turn it into a datetime object
        try:
            date = datetime.datetime.strptime(entereddate,'%Y-%m-%d')
#on a value error ask print the error then ask the user to re enter the date.
        except ValueError as e:
            print 'Value Error encoutnered, traceback reads:'
            print e
            print ''
            print 'Something is incorrect about the date entered'
            return getdate()
#then if its inside the time frame of this program return the datetime object
        if datetime.datetime(2019,01,01) <= date <= datetime.datetime.today():
            print 'Using ' + date.strftime('%Y-%m-%d') + ' as the date'
            return date.date()
#else ask the user to reenter the date.
        else:
            print 'Date outside range. Please enter a date between 2019-01-01 and ' + datetime.datetime.today().strftime('%Y-%m-%d')
            return getdate()
    else:
        print 'Date not in YYYY-MM-DD format'
        getdate()


#get the matrix the assays was done in
def getmatrix(matrixlist):
#build a readerable formate for the options
    selectiontext = 'Your options are '
    for item in matrixlist:
        selectiontext = selectiontext + item + ', '
    selectiontext = selectiontext[0:-2] +': '
#get the user input
    print 'Please enter the matrix used for this assay'
    enteredmatrix = raw_input(selectiontext).lower()
#let them out if they want out
    if enteredmatrix.lower() == 'quit' or enteredmatrix.lower() == 'q' or enteredmatrix.lower() == 'exit':
        sys.exit()
#if its in the list return it
    elif enteredmatrix in matrixlist:
        print 'Using ' + enteredmatrix + ' as the matrix'
        return enteredmatrix
#else ask the user again
    else:
        print enteredmatrix + ' is not an option'
        return getmatrix(matrixlist)


#Function to get the FQC number
def getfqc():
    fqccheck = re.compile('[f|F][q|Q][c|C]-\d\d\d\d\d?')
    inputfqc = raw_input('Please enter the fqc number for the run: ')
#let people out if they don't want any part of it
    if inputfqc.lower() == 'quit' or inputfqc.lower() == 'q' or inputfqc.lower() == 'exit':
        sys.exit()
#check the input
    fqcmatch = fqccheck.match(inputfqc)
#if the input is longer then expected (9) its consider wrong
    if 9 < len(inputfqc):
        print inputfqc + ' is not a recgnonized fqc number.'
        return getfqc()
#if not correct recall the function
    if not fqcmatch:
        print inputfqc + ' is not a recgnonized fqc number.'
        return getfqc()
#if correct return the input
    elif fqcmatch:
        print 'Using ' + inputfqc.lower() + ' as the fqc number'
        return inputfqc.lower()


#function to to check make sure the initials are in the lims
def getinitials(initiallist):
    inputedinitials = raw_input('Please enter your intials: ').upper()
#let people out if they don't want any part of it
    if inputedinitials.lower() == 'quit' or inputedinitials.lower() == 'q' or inputedinitials.lower() == 'exit':
        sys.exit()
#check to see if they are in the database
    elif inputedinitials in initiallist:
        print 'Using ' + inputedinitials + ' as the initials'
        return inputedinitials
    else:
        print inputedinitials + ' not found in the lims'
        return getinitials(initiallist)


#function to get a list of files that match the file type and fqc#
def getfilelist(dirloc,fqcnum):
    filelist = []
#excluded items without the correct file type
    for item in os.listdir(dirloc):
        if not item.lower().endswith('.asc'):
            pass
#from those that remain select only those that start with correct fqcnum
        elif item.lower().startswith(fqcnum):
            filelist.append(os.path.join(dirloc, item))
#return the list of files
    return sorted(filelist)


#a function for removing unwanted plates and getting a confirmation that plates are correct
def getplatelist(platelist,excludedplates,fqcnum):
    modifiedplatelist = []
    exludedindices = []
#make sure the list is sorted
    platelist = sorted(platelist)
#if there are not any plates in the that match it terminate the program
    if len(platelist) == 0:
        print 'No files found or selected, terminating program'
        close = raw_input('Please press enter to close program')
        sys.exit()
#get a positive response if the files are the correct ones
#list out the files
    print ''
    print 'These are the files found for ' + fqcnum + ':'
    x = 1
    for plate in platelist:
        print str(x) + ')' + plate.split('/')[-1]
        x += 1
#get the a positive response that these are the correct plates or a list of ones to excluded
    print ''
    print 'Please enter the number or numbers of files you want to exclude \nseperating each number with a comma'
    excludedfiles = raw_input('If you wish use all the files please type "all" or "a": ')
    print ''
#if they are the correct plates return the list
    if excludedfiles.lower() == 'all' or excludedfiles.lower() == 'a':
        print 'Using all files listed above'
        print ''
        #return platelist
        includedplates = platelist
#if they fail to give a positive response or a list of items then close the program
    elif excludedfiles.lower() == '':
        print 'No files selected, terminating program'
        close = raw_input('Hit enter to close')
        sys.exit()
#finally if they have list of numbers remove those items from the list and call the function again.
    else:
        for filenum in excludedfiles.split(','):
#if we have a number
            if filenum.isdigit():
#convert it into an int
                indexnum = int(filenum)-1
#if that int is less then the length of the plate list added it
                if len(platelist) > indexnum:
                    exludedindices.append(indexnum)
#go through the plate list and add to a new list those items that weren't excluded
        for plate in platelist:
            if platelist.index(plate) in exludedindices:
#update the exculdedplates list so
                excludedplates.append(plate)
            else:
                modifiedplatelist.append(plate)
#call the function again until we get a positive response
        includedplates,excludedplates = getplatelist(modifiedplatelist,excludedplates,fqcnum)
        #return getplatelist(modifiedplatelist,fqcnum)
    return includedplates,excludedplates

#from jkominek/chematox/elisa.py
#formats and adds annotations to the PDF page.
def annotate_page(page, data):
    no = pyPdf.generic.NameObject

    annots = page.setdefault(no('/Annots'), pyPdf.generic.ArrayObject())
    if type(annots) == pyPdf.generic.IndirectObject:
        annots = annots.getObject()

    new_annot = pyPdf.generic.DictionaryObject()
    new_annot[no('/Type')] = no('/Annot')
    new_annot[no('/Subtype')] = no('/FreeText')
    new_annot[no('/DA')] = pyPdf.generic.TextStringObject('/Helv 11.99995 Tf 0 0 0 rg')
    new_annot[no('/IT')] = no('/FreeText')
    new_annot[no('/Rect')] = \
        pyPdf.generic.ArrayObject(map(pyPdf.generic.NumberObject,
                                      [18, 555.83800, 18, 555.83800]))
    new_annot[no('/F')] = pyPdf.generic.NumberObject(4)
    new_annot[no('/Contents')] = pyPdf.generic.TextStringObject(json.dumps(data))

    annots.append(new_annot)
