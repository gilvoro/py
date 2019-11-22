import datetime
import os
import sys

#import the other modules
from wasteprojection import *
from waspercalc import *
from waspercsv import *
from wasperfunc import *
from wasperpdfreport import *
from waspersticker import *
from wasperknown import *

#define the file locations
baseloc = 'C:\\Users\\jlaughl6\\User Assets\\safety and waste management\\waste management\\'
projectloc = 'C:\\Users\\jlaughl6\\User Assets\\safety and waste management\\waste management\\waste projections'
recordloc = 'C:\\Users\\jlaughl6\\User Assets\\safety and waste management\\waste management\\waste container records\\container record'
csvrequestloc = 'C:\\Users\\jlaughl6\\User Assets\\safety and waste management\\waste management\\waste container records\\csv request'
pdfreportloc = 'C:\\Users\\jlaughl6\\User Assets\\safety and waste management\\waste management\\waste container records\\pdf report'
stickerloc = 'C:\\Users\\jlaughl6\\User Assets\\safety and waste management\\waste management\\waste container records\\stickers'

#collected data from the user
type = input('What type of waste?: ')
room = input('Waste from which room?: ')
stream = input('What waste stream?: ')
enddate = input('What date was the waste pulled?: ')
eddt = datetime.datetime.strptime(enddate, '%Y-%m-%d')
grossvolume = float(input('Approximent volume of waste?: '))
print('')

#if the type is known then skip the projection and read the waste profile
if type == 'known' or type == 'fixed':
    volumedict = knowncalc(room, grossvolume, projectloc)
#otherwise go to the projections
else:
#define the addtional waste file
    awfile = os.path.join(os.path.join(projectloc,'additional waste'),
                          'additional waste ' + room + ' ' + stream + ' ' + enddate + '.csv')
#inform the user if additional waste file is found
    if os.path.exists(awfile):
        print('Found the following additional waste file: ' + awfile.split('\\')[-1])
#if none is found inform the user and set the awfile to none
    else:
        print('No additional waste file found.')
        awfile = 'none'

#get the projection data from that module
    projdict = projection(projectloc)
#get the volume
    volumedict = percalc(room, stream, grossvolume, projdict, awfile)

#get the code for the waste
hexcode = hex(int(room)).split('x')[1]
#prefix with the room in hex, then hex code for the unicode for the first two letters of waste stream
if type == 'known' or type == 'fixed':
    hexcode = hexcode + '6b6e'
elif stream == 'aqueous':
    hexcode = hexcode + '6171'
elif stream == 'organic':
    hexcode = hexcode + '6f72'
else:
    hexcode = hexcode + '6f74'

#finally add the end date as hexcode
hexdate = hex(int(eddt.year)).split('x')[1]+hex(int(eddt.month)).split('x')[1]+hex(int(eddt.day)).split('x')[1]
hexcode = hexcode + hexdate

#make record file and file for others
csvrecord(room, stream, hexcode, enddate, grossvolume, volumedict, recordloc)

#collect additional informations
ph = input('What is the pH of the waste?: ')
csize = input('What is size of the container?: ')
cmat = input('What material is the container made of?: ')
state = input('What is the physcial state of the waste?: ')
generator = input('From what process was the waste generated?: ')
contact = input('Who is the contact for this waste?: ')
phone = input('What is the contacts phone number?: ')

#make csv request
csvrequest(room, stream, hexcode, enddate, ph, csize, cmat, state, generator,
               contact, phone, grossvolume, volumedict, csvrequestloc)

#generate the chemical list for report pdfs
#variable to manage if we have a second page on the report or not
secpage = False
#if we have more then 99 samples then we will need to generate second page and a shorter list for front
if 99 < len(volumedict.keys()):
    flist = chemlist(volumedict,[40,40,17])
    rlist = chemlist(volumedict,[56,56,56])
    secpage = True
#otherwise the longer list for the front and no second page.
else:
    flist = chemlist(volumedict,[40,40,19])
    rlist = chemlist(volumedict,[56,56,56])

#make the report pdf
reportpdf(hexcode,contact,phone,room,generator,csize,cmat,
           state,ph,grossvolume,enddate,stream,flist,rlist,
           secpage,pdfreportloc)

#generate the chemical list for sticker pdf
slist = chemlist(volumedict,[59,59,59])

#make the sticker pdf
stickerpdf(hexcode,room,enddate,stream,slist,stickerloc)
