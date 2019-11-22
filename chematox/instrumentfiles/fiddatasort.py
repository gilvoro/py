import os
import csv

#a function which takes data from PerkinElmer HSGCFID and converts
#it into a dictionary for use by other scripts
def numberdisplay(num):
    try:
        test = float(num)
        returnvalue = num
    except:
        returnvalue = '0.000'
        
    return returnvalue

def fiddatasort(filename):

    sorted_data = {}
    with open (filename, 'rU') as csvfile:
        unsorted_data = csv.reader(csvfile)
#go row by row of the raw data
        for row in unsorted_data:
#pass by row that have no fields in them
            if len(row) < 3:
                pass
#if the cell-1 has nothing in it and cell 4 has something
#set the compoundname to cell 4
            elif row[1] == '' and row[4] != '':
                compoundname = row[4].lower()
                sorted_data.setdefault(compoundname, {})
#we don't collect the column headers
            elif row[1].startswith('Date') or row[1].startswith('Injection'):
                pass
#whatever information is displayed on sample number becomes a key list later
#so if that is blank we skip the entery
            elif row[3] == '':
                pass
#else we build the dictionary
            else:  
                sorted_data[compoundname].setdefault(row[3],{'name':row[2],
                                                             'calc':numberdisplay(row[4]),
                                                             'height':numberdisplay(row[5]),
                                                             'area':numberdisplay(row[6])})

    return sorted_data
