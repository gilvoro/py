import csv

#the dictinary containing the extra volume of water, acetone and the relavent labs
roomdict = {'3085':[0.1,0.1,'1150','2150'],'3089':[0.1,0.1,'1801','1811'],'3091':[0.1,0.1,'3120','3130']}

def percalc(room, stream, grossvolume, projdict, awfile):
#wiplist holds the information for each lab
    wiplist = []
#wipdict hold the "acutal' volumes of chemicals
    wipdict = {}
#wexdict holds the "expected" volume of chemicals
    wexdict = {}
#wkdict holds the "known" volumes
    wkdict = {}
#mixvolume is the gross volume minus the "known" additions
    mixvolume = grossvolume
#A value to track the percentage of the waste left
    perleft = 100
#the expected volume is the volume of waste predicted if everything was perfect:
    expectedvolume = 0
#determine the number of experiments for each course, and the number of sections and days each ran
    for course in roomdict[room][2:]:
        numexp = int(input('how many experiments for ' + course + ' ?: '))
        i = 0
#list out the experiments
        while i < numexp:
            experlist = sorted(projdict[course].keys())
            x=1
            templist = []
            print('')
            for experiment in experlist:
                templist.append(experiment)
                print(str(x)+'.) ' + experiment.split('.')[0])
                x += 1
            print('')
#collect which experiments, then the number fo days that it has run, then the number of sections it has run
            expernum = input('which experiment number?: ')
            exper = templist[int(expernum)-1]
            days = float(input('how many days has the experiment run?: '))
            sections = float(input('how many sections has the experiment run?: '))
            wiplist.append([course,exper,days,sections])
            print('')
            i += 1

#tranlate the wiplist into a chemical list in the wipdict
    for wip in wiplist:
#check to see if the stream is in part of the listed experiments waste stream
        if stream in projdict[wip[0]][wip[1]].keys():
#get the factor for the chemical based on often its run and generation rate
            for gr in projdict[wip[0]][wip[1]][stream].keys():
                if gr == 'day':
                    factor = wip[2]
                elif gr == 'section':
                    factor = wip[3]
                elif gr == 'student':
                    factor = wip[3]*12
                else:
                    factor = 0
                    print(gr + ' is not a recognized generation rate')
                    print(wip)
#get the expected volume for the chemicals at the given generation rate
                for chemical in projdict[wip[0]][wip[1]][stream][gr]:
                    expvol = float(projdict[wip[0]][wip[1]][stream][gr][chemical])*factor
                    wexdict.setdefault(chemical,0)
#add the expected volume to the current vaule and to the total expected volume
                    wexdict[chemical] += expvol
                    expectedvolume += expvol

#if we have additional waste add them to wkdict
    if awfile != 'none':
        with open(awfile, newline = '') as csvfile:
            unsorted_data = csv.reader(csvfile, delimiter = ',')
            for row in unsorted_data:
#pass anything that has less then two lines
                if len(row) < 2:
                    pass
#pass the header
                elif row[0].lower() == 'chemical':
                    pass
#otherwise added to the dictionary
                else:
                    wkdict.setdefault(row[0].lower(),0)
                    wkdict[row[0].lower()] += float(row[1])
#adjust the mix volume down
                    mixvolume = mixvolume - float(row[1])
#add the chemical to the wexdiction so its not skipped
                    wexdict.setdefault(row[0].lower(),0)
#now adjust based on the base volume of each container being water or acetone
    if stream == 'aqueous':
        wkdict.setdefault('water',0)
#add the room factor times the gross volume as catch all for cleaning
        wkdict['water'] += (grossvolume * roomdict[room][0])
#adjust the mix volume by the same factor
        mixvolume = mixvolume - (grossvolume * roomdict[room][0])

    if stream == 'organic':
            wkdict.setdefault('acetone',0)
#add the room factor times the gross volume as catch all for cleaning
            wkdict['acetone'] += (grossvolume * roomdict[room][1])
#adjust the mix volume by the same factor
            mixvolume = mixvolume - (grossvolume * roomdict[room][1])
#calculate the "actual" volumes and percentages

    for chemical in wexdict:
        wipdict.setdefault(chemical,{'volume':0,'percent':0,'report percent':0})
#calculate the percentage of expected volume each chemical is
        perwex = float(wexdict[chemical]/expectedvolume)
#calculate the "actual" volume in the waste stream
        wipvolume = perwex*mixvolume
#add the known volume of the chemical if there is any
        if chemical in wkdict.keys():
            wipvolume += wkdict[chemical]
#add the volume to the wip dictionary
        wipdict[chemical]['volume'] += round(wipvolume,2)
#calculate the 'actual' percentage of the waste each chemical is
        wipper = (wipvolume/grossvolume)*100
#now update the 'acutal' percentage and the reproted percentage
        wipdict[chemical]['percent'] += wipper
            #skip water in aqueous waste and acetone in organic
        if chemical == 'water' and stream == 'aqueous':
            pass
        elif chemical == 'acetone' and stream == 'organic':
            pass
#anthing below 0.1 will be listed as less then, then take the high estimate off the percentage
        elif wipper < 0.01:
            wipdict[chemical]['report percent'] = 0.01
        elif 0.01 <= wipper < 0.1:
            wipdict[chemical]['report percent'] = 0.1
            perleft = perleft - 0.1
        elif 0.1 <= wipper < 1:
            wipdict[chemical]['report percent'] = 1.0
            perleft = perleft - 1
        else:
            wipdict[chemical]['report percent'] = round(wipper,0)
            perleft = perleft - round(wipper,1)

#then adjust the water or acetone report percentage to the left over percentage
    if stream == 'aqueous':
        wipdict['water']['report percent'] = round(perleft,0)

    if stream == 'organic':
        wipdict['acetone']['report percent'] = round(perleft,0)

    return wipdict
