import os
import pandas as pd
import PyPDF2
import tkinter

from tkinter import filedialog

from sppcsv import *
from spppdf import *

#setup the default pathway
desktop = os.path.expanduser('~\Desktop')

#start tkinter and get the file
root = tkinter.Tk()
root.withdraw()
fileloc = filedialog.askopenfilename(defaultextension = '.xlsx',
                                       filetypes = [('Excel File','.xlsx')],
                                       initialdir = desktop,
                                       title ='Please select Excel file')
#get the correct file
rawinput = pd.read_excel(fileloc)

#change columns names
rawinput.columns = ('id','ignore-1','ignore-2','ignore-3','ignore-4','section','names','description','equipment','instruments','chemicals')
#transpose the dataframe....
formated = rawinput.transpose()
#...and put in to a diction
rawdict = formated.to_dict()

basedict = {}
#for each entry in the dictionary process it into a more useful form
for record in rawdict:
    groupnum = 'Group-' + str(rawdict[record]['id'])
#base the new dictionary via section then group number
    basedict.setdefault(rawdict[record]['section'],{})
    basedict[rawdict[record]['section']].setdefault(groupnum,{})
    groupdict = basedict[rawdict[record]['section']][groupnum]

#take the raw names input and split on ;
    rnames = rawdict[record]['names'].split(';')

#if there is only one entry on the split ;
#check to see if the students failed to follow directions or there is only one student
    if len(rnames) == 1:
#split on a comma to see if we get a name and an email
        pnames = rnames[0].split(',')
        if len(pnames) == 2:
#if we do put into the dictionary
            groupdict['names'] = [(pnames[0].strip(),pnames[1].strip())]
#if we don't assume assume it was not done correctly
        else:
            groupdict['names'] = ['up',rawdict[record]['names']]
#if we do get several entries on the split ; further split them into name/email
    else:
        namelist = []
        for pair in rnames:
            pnames = pair.split(',')
#if we get exactly 2 entries add them to the list
            if len(pnames) == 2:
                namelist.append((pnames[0],pnames[1]))
#if we don't assume they failed to enter the data correctly
            else:
                namelist.append(('upr',pair))

        groupdict['names'] = namelist

#simply add the description to the dictionary
    groupdict['description'] = rawdict[record]['description']

#split up the equipment and strip out any white space
    pequip = rawdict[record]['equipment'].split(';')
    pequiplist = []
    for item in pequip:
        pequiplist.append(item.strip())

    groupdict['equipment'] = pequiplist

#split the instruments and discard any 'blank' entries
    pint = rawdict[record]['instruments'].split(';')
    pintlist = []

    for item in pint:
        if item == '':
            pass
        else:
            pintlist.append(item)

    groupdict['instruments'] = pintlist

#split the chemicals.
    rche = rawdict[record]['chemicals'].split(';')

#if we get just one entry on the split, try to parse it further to the individual entries
    if len(rche) == 1:
                pche = rche[0].split(',')
                if len(pnames) == 4:
        #if we do put into the dictionary
                    groupdict['chemicals'] = [(pche[0].strip(),pche[1].strip(),pche[2].strip(),pche[3].strip()),]
        #if we don't assume assume it was not done correctly
                else:
                    groupdict['chemicals'] = ['up',rawdict[record]['chemicals']]
    else:
            chelist = []
            for entry in rche:
                pche = entry.split(',')
    #if we get exactly 2 entries add them to the list
                if len(pche) == 4:
                    chelist.append((pche[0].strip(),pche[1].strip(),pche[2].strip(),pche[3].strip()))
    #if we don't assume they failed to enter the data correctly or used IUPAC name with lots of comma's
                else:
                    chelist.append(('upr',entry))

            groupdict['chemicals'] = chelist

intcsv(basedict,desktop)
chemcsv(basedict,desktop)
reparsecsv(basedict,desktop)
for section in basedict:
    reportout = PyPDF2.PdfFileWriter()
    b = section.split(' ')
    filename = os.path.join(desktop, b[0] + ' ' + b[1].split(':')[0] + ' ' + b[5]  + '.pdf')
    for group in basedict[section]:
        a = PyPDF2.PdfFileReader(grouppage(section,group,basedict[section][group]))
        reportout.appendPagesFromReader(a)

# reportout = PyPDF2.PdfFileWriter()
# for page in pdf:
#     a = PyPDF2.PdfFileReader(page)
#     reportout.appendPagesFromReader(a)

    reportout.write(open(os.path.join(filename),'wb'))
