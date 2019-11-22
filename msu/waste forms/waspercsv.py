import csv
import datetime
import os

#output for longterm records
def csvrecord(room, stream, hexcode, enddate, grossvolume, volumedict, outputloc):
    opname = os.path.join(outputloc,room+' '+stream+' '+enddate+' '+ hexcode + ' record.csv')
    oplist = [['Waste PIN:',hexcode],['Room Number:',room],['Waste Type:',stream],
              ['Waste Filled Date:', enddate],['Approximate Final Volume:',grossvolume],
              ['',''],['Chemical','Volume(mL)','Approximate Percent','Reported Percent']]

#add chemicals in alphabetical order
    for chemical in sorted(volumedict.keys()):
        templist = [chemical,volumedict[chemical]['volume'],round(volumedict[chemical]['percent'],2),
                    volumedict[chemical]['report percent']]
        oplist.append(templist)

#generate a time stamp
    timestamp = datetime.datetime.now()
    oplist.append(['',''])
    oplist.append(['Record Generated:',timestamp.strftime('%Y-%m-%d %H:%M:%S')])

    with open(opname,'w',newline='') as csvfile:
        wo = csv.writer(csvfile)
        for row in oplist:
            wo.writerow(row)

def csvrequest(room, stream, hexcode, enddate, ph, csize, cmat, state, generator,
               contact, phone, grossvolume, volumedict, outputloc):
    opname = os.path.join(outputloc,room+' '+stream+' '+enddate+' '+ hexcode + ' request.csv')
    oplist = [['Waste PIN:', hexcode],['Generated From:', generator],['Waste Contact:', contact],
              ['Contact Phone Number:', phone],['Building:','Science'],['Room Number:', room],
              ['Waste Type:', stream],['pH of the Waste',ph],['Container Size', csize],
              ['Container Material', cmat],['Physical State', state],['Waste Filled Date:', enddate],
              ['Approximate Final Volume:', grossvolume],['',''],['Chemical','Reported Percent']]

#sort the chemicals in decending order. Hits both percentage and name but eh...
    sortlist = []
    for chemical in sorted(volumedict.keys()):
        sortlist.append([volumedict[chemical]['report percent'],chemical])

    for item in sorted(sortlist, reverse = True):
        if item[0] == 0.01:
            oplist.append([item[1],'<0.01%'])
        elif item[0] == 0.1:
             oplist.append([item[1],'<0.1%'])
        else:
            oplist.append([item[1],'~'+str(item[0])+'%'])

#generate a time stamp
    timestamp = datetime.datetime.now()
    oplist.append(['',''])
    oplist.append(['Record Generated:',timestamp.strftime('%Y-%m-%d %H:%M:%S')])

    with open(opname,'w',newline='') as csvfile:
        wo = csv.writer(csvfile)
        for row in oplist:
            wo.writerow(row)
