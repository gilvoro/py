import csv
import datetime
import os
import sys


def getlocations(loc):
    locations = {}
    for item in os.listdir(loc):
        key = item.split('.')[0]
        locations[key] = []
        with open(os.path.join(loc,item),newline='') as csvfile:
            unsorted_data = csv.reader(csvfile, delimiter = ',')
            for row in unsorted_data:
                locations[key].append(row[0].lower())
    
    return locations

def zeropadding(item):
    while len(item) < 5:
         item = '0' + item
    return item


def getsubloc(locationdict):
    newsubloc = input('Enter the sublocation to be inventoried: ').lower()
    if newsubloc in ['exit','e','quit','q']:
        sys.exit()
    elif newsubloc not in locationdict['sub-locations']:
        add = input(newsubloc + ' not found in file, add it?: ')
        if add.lower() == 'y' or add.lower() == 'yes':
            locationdict['sub-locations'].append(newsubloc)
        else:
            newsubloc = getsubloc(locationdict)
    return newsubloc
    
def getloc(locationdict,roominv):
    newloc = input('Enter the location to be inventoried: ').lower()
    if newloc in ['exit','e','quit','q']:
        sys.exit()
    elif newloc not in locationdict['locations']:
        add = input(newloc + ' not found in file, add it?: ')
        if add.lower() == 'y' or add.lower() == 'yes':
            locationdict['locations'].append(newloc)
            newsubloc = getsubloc(locationdict)
            new_locinv = roominv[roominv.recorded_location == newloc]
        else:
            newloc, newsubloc, new_locinv = getloc(locationdict,roominv)
    else:
        newsubloc = getsubloc(locationdict)
        new_locinv = roominv[roominv.recorded_location == newloc]
    return newloc, newsubloc, new_locinv
    
def getroom(locationdict,cheminv):
    newroom = input('Enter the room to be inventoried: ').lower()
    if newroom in ['exit','e','quit','q']:
        sys.exit()
    elif newroom not in locationdict['rooms']:
        add = input(newroom + ' not found in file, add it?: ')
        if add.lower() == 'y' or add.lower() == 'yes':
            locationdict['rooms'].append(newroom)
            new_roominv = cheminv[cheminv.recorded_room == newroom]
            newloc, newsubloc, new_locinv = getloc(locationdict,new_roominv)
        else:
            newroom, newloc, newsubloc, new_roominv, new_locinv = getroom(locationdict,cheminv)
    else:
        new_roominv = cheminv[cheminv.recorded_room == newroom]
        newloc, newsubloc, new_locinv = getloc(locationdict,new_roominv)       
    return newroom, newloc, newsubloc, new_roominv, new_locinv
