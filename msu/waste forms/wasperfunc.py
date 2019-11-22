import sys

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER

#functions used in several mods

#funtion to bold all the text for reportlab
def bolder(x,fstyle):
    if len(x):
        return Paragraph("<b>%s</b>" % (x,),fstyle)
    else:
        return x

#function to convert the numbers into text for the reports
def addchem(pos,len,list):
#if the current position is less then current chemical list add the chemical to the output list
    if pos < len:
#things listed 0.01 are less then 0.01
        if list[pos][0] == 0.01:
            templist = [list[pos][1],'<0.01%']
#things listed as 0.1 are less then 0.1
        elif list[pos][0] == 0.1:
            templist = [list[pos][1],'<0.1%']
        else:
#other wise add '~' and % to the number
            templist = [list[pos][1],'~'+str(list[pos][0])+'%']
        return templist
#if the position is larger then the chemical list return an empty list
    else:
        return ['','']

#function to generate the chemical list to added to the report or sticker
def chemlist(volumedict,rownums):
#setup a list to the hold the individual column lists
    collist = []
    x = 0
#add the number of columns need
    while len(rownums) > x:
        collist.append([])
        x += 1
#determine the total number of entries we can have
    cellnum = sum(rownums)
    sortdict = {}
    sortlist = []
    totchem = len(volumedict.keys())
#if the total number of chemicals is greater then the report can hold crash out give up and move to ireland
    if 168 < totchem:
        print('No can do boss, number of chemicals exceeds space for chemcials.')
        sys.exit()
#otherwise add the chemicals to the sort dictionary by percentage
    for chemical in volumedict:
        sortdict.setdefault(volumedict[chemical]['report percent'],[])
        sortdict[volumedict[chemical]['report percent']].append(chemical)
#sort the percentage in decending order
    for percent in sorted(sortdict.keys(),reverse = True):
#sort the chemicals in acending order
        for chemical in sorted(sortdict[percent]):
            sortlist.append([percent,chemical])

#go through the sortlist, call addchem to add chemicals column list
    pos = 0
    row = 0
    col = 0
#fill up the rows so that things don't break
    while pos < cellnum:
#as long was there is still room on the column add chemicals
        if row < rownums[col]:
            collist[col].append(addchem(pos,totchem,sortlist))
            pos += 1
            row += 1
#otherwise move to the next column and add it there
        else:
            col +=1
            collist[col].append(addchem(pos,totchem,sortlist))
            row = 1
            pos += 1

    return collist
