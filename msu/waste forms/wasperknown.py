import csv
import os

#function to deliver a wastedict for known or fixed waste
def knowncalc(room, grossvolume, loc):
#get the known waste profiles for the room
    wastefiles = []
    wiploc = os.path.join(loc,'known waste stream')
    for item in os.listdir(wiploc):
        if item.startswith(room):
            wastefiles.append(item)

#print out the profiles and have the user choose the correct one
    x = 1
    print('')
    for item in sorted(wastefiles):
        print(str(x) + '.)' + item.split('.')[0])
        x += 1
    print('')
    wastenum = input('Which profile number?: ')
    waste = wastefiles[int(wastenum)-1]
    print('')

#build the waste dictionary based o the file choosen
    wastedict = {}
    with open(os.path.join(wiploc,waste), newline = '') as csvfile:
        unsorted_data = csv.reader(csvfile, delimiter = ',')
        for row in unsorted_data:
#...skip any random row that is less then four....
            if len(row) < 4:
                pass
#...skip metadata rows
            elif row[2] == 'updated:' or row[0] == 'chemical':
                pass
#otherwise calculate the percentage of waste from the gross volume, then added it to the dictionary
            else:
                calcvolume = round((float(row[1])*(grossvolume/100)),2)
                wastedict[row[0].lower().strip()] = {'volume':calcvolume,'percent':float(row[1]),'report percent':float(row[1])}

#return the waste profile
    return wastedict
