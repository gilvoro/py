import csv
import datetime
import random
import os

#a function to build the qdict which will be the primary databse in the program
def qdictbuilder(dirloc):
    qdict = {}
#look at all of the files in the dir, pass spm and add the rest to dictionary
    for item in os.listdir(dirloc):
        if item == 'spm.csv':
            pass
        else:
            qdict[item.split('.')[0]] = {'type':'none',
                                         'pslist':[],
                                         'qlist':[]}
#open each file and update the dictionary
            with open(os.path.join(dirloc,item),newline = '') as csvfile:
                rawlines = csv.reader(csvfile, delimiter = ',')
                for row in rawlines:
                    if row[0] == '' or row[0] == 'quote':
                        pass
                    elif row[0] == 'type':
                        qdict[item.split('.')[0]]['type'] = row[1].lower()
                    else:
                        qdict[item.split('.')[0]]['qlist'].append(row)
    return qdict


#function to select today's quotes randomly
def qchooser(qdict):
    tqlist = {}
#seed a random number based on the date and time
    random.seed(datetime.datetime.now().year+datetime.datetime.now().month+
                datetime.datetime.now().day+datetime.datetime.now().microsecond)
#get the random quote index and add the quote
    for item in qdict.keys():
        randomizer(qdict[item]['pslist'],len(qdict[item]['qlist'])-1)
#add the quote index at the last number added to the pslist
        tqlist[item] = qdict[item]['qlist'][qdict[item]['pslist'][-1]]
    return tqlist


#function to change the text on the item cards
def textchange(carddict,qdict,tqdict):
    for item in qdict.keys():
        if item in tqdict.keys() and item in carddict.keys():
            type = qdict[item]['type']
            if type == 'quote':
                carddict[item]['msgtxt'].set(tqdict[item][0])
                carddict[item]['signtxt'].set(tqdict[item][1])
                carddict[item]['orgtxt'].set(tqdict[item][2])
    #need more code here for non-quote but later
            else:
                pass
        else:
            print(item + 'not found in todays quotes or cards')
            pass


#randomly generate the numbers for the pslist
def randomizer(pslist,length):
#select a random index for the list
    rnum = random.randint(0,length)
#and keep doing so until we get one we haven't selected yet
    if rnum in pslist:
        randomizer(pslist,length)
#change the random seed by the new rnum
    random.seed(datetime.datetime.now().year+datetime.datetime.now().month+
                datetime.datetime.now().day+datetime.datetime.now().microsecond+rnum)
#append the plist
    pslist.append(rnum)
