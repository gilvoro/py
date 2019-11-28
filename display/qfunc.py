import csv
import datetime
import random
import os

dirloc = 'C:\\pve\\qd\\testfiles'
dfiles = ['skquotes','scquotes']

def qchooser(sdict):
  quotedict = {}
  seldict = {}
  random.seed(datetime.datetime.now().year+datetime.datetime.now().month+
             datetime.datetime.now().day+datetime.datetime.now().microsecond)
  for item in dfiles:
    quotedict[item] = []
    with open(os.path.join(dirloc,item+'.csv'),newline = '') as csvfile:
        rawlines = csv.reader(csvfile, delimiter = ',')
        for row in rawlines:
            if row[0] == 'type' or row[0] == '' or row[0] == 'quote':
                pass
            else:
                quotedict[item].append(row)

    newq = randomizer(sdict[item],len(quotedict[item])-1)
    seldict[item] = quotedict[item][newq]
    sdict[item].append(newq)
  return sdict,seldict

def randomizer(sellist,length):
    rnum = random.randint(0,length)
    if rnum in sellist:
        randomizer(sellist,length)

    return rnum

thing = qchooser({'skquotes':[],'scquotes':[]})
