import csv
import os
import pandas as pd

from cheminv_reconcile_main_func import *

basedir = 'C:\\Users\\jlaughl6\\User Assets\\script files\\chemical_inventory\\'
sfdir = os.path.join(basedir,'script_files')
sidir = os.path.join(basedir,'script_inventory')

# roomlistfile = os.path.join(sfdir,'rooms.csv')
# locationlistfile = os.path.join(sfdir,'locations.csv')
# sublistfile = os.path.join(sfdir,'sub-locations.csv') 

cheminvfilename = 'chemical_inventory_' + datetime.datetime.now().strftime('%Y-%m-%d %H%M%S') + '.csv'

currentroom = ''
currentloc = ''
currentsubloc = ''

def getinventory(loc):
    inventory = {}
    mostrecentdate = datetime.datetime(2000,1,1)
    mostrecentfile = ''
    for item in os.listdir(loc):
        filename = item.split('.')[0]
        checkdate = datetime.datetime.strptime(filename.split('_')[2],'%Y-%m-%d %H%M%S')
        if checkdate > mostrecentdate:
            mostrecentdate = checkdate
            mostrecentfile = item

    return pd.read_csv(os.path.join(loc,mostrecentfile))

def zeropadding(item):
    while len(item) < 5:
         item = '0' + item
    return item

chem_inventory = getinventory(sidir)
chem_inventory['inventory_number'] = chem_inventory['inventory_number'].apply(zeropadding)
chem_inventory = chem_inventory.applymap(lambda x: x.lower() if type(x) == str else x)
locdict = getlocations(sfdir)    
currentroom, currentloc, currentsubloc, room_inventory, location_inventory = getroom(locdict,chem_inventory)

scan = ''
print('')

while scan not in ['exit','e','quit','q']:
    print('Enter the next inventory item, change_room, change_location, change_sublocation, or exit')
    scan = input('Next entery: ').lower()
    if scan in ['exit','e','quit','q']:
        pass
    elif scan == 'change_room':
        print('Changing Room')
        currentroom, currentloc, currentsubloc, room_inventory, location_inventory = getroom(locdict,chem_inventory)
    elif scan == 'change_location':
        print('Changing Location')
        currentloc, currentsubloc, location_inventory = getloc(locdict,chem_inventory)
    elif scan == 'change_sublocation':
        print('Changing Sublocation')
        currentsubloc = getsubloc(chem_inventory)
    elif scan.isdigit() or scan.startswith('mche'):
        
    else:
        print('Entry not recogized')
    
    print('')

print('out of the loop')        