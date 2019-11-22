import re
import numpy as np

def dataprocess(unsorted_data,report_data,cutoffs,matrix,samplelist):
#setup a list to hold all the CTnums
    ctnumsread = []
#output list for lims
    limsoutput = []
#list of ct numbers that are not in the samplelist
    wrong_ct = []
#get the matrix, and captilize the first letter
    matrix = report_data['metadata']['matrix'][0].upper() + report_data['metadata']['matrix'][1:]
#standard value data for cutoff plots
    standarddata = {}
#go through analyte by analyte
    for analyte in sorted(unsorted_data.keys()):
        print 'Processing data for ' + analyte
        analytestandard = standarddata.setdefault(analyte, {})
#get the cutoff value, and then calculate the below and above values
        covalue = float(cutoffs[analyte]['cutoff'])
        bcovalue = covalue/2
        acovalue = covalue*2
#setup the lsit for the assay summary
        forassaysum = [matrix, analyte]
        assaynoteslist = []
#setup the list for passing to the report script
        report_data['analytepdfs'][analyte] = [[analyte + '-' + matrix,
                                               str(covalue),
                                               str(bcovalue),
                                               str(acovalue)]]
#a list to store the individual controls lists
        controllist = []
#get the samples for analyte
        analytedict = unsorted_data[analyte]
#find the blank and set the list and dictionary
        blanklist = ['',round(analytedict['blank']['abs'],3),round(analytedict['blank']['ratio'],1)]
        notes = 'None'
        rowcolor = 'none'
#want the absorbance for standard information
        analytestandard['blank'] = analytedict['blank']['abs']
#add notes if needed
#flag low absorbance
        if 0.7 > float(blanklist[1]):
            notes = 'low abs.'
            rowcolor = 'y'
            assaynoteslist.append('mc')
#append the list with notes and color value
        blanklist.append(notes)
        blanklist.append('')
        blanklist.append(rowcolor)
        controllist.append(blanklist)
#find the calibrator and set the list and dictionary
        callist = ['',round(analytedict['calibrator']['abs'],3),round(analytedict['calibrator']['ratio'],1)]
        calratio = analytedict['calibrator']['ratio']
        notes = 'None'
        rowcolor = 'none'
#want the ratio for standard information
        analytestandard['calibrator'] = analytedict['calibrator']['ratio']
#add notes if needed
#flag a ratio above 90
        if 90.0 < float(callist[2]):
            notes = 'cal near mb'
            rowcolor = 'y'
            assaynoteslist.append('cal')
#flag a ratio above 70
        elif 70.0 < float(callist[2]):
            notes = 'high ratio'
            rowcolor = 'y'
            assaynoteslist.append('cal')
#flag a ratio below 30
        elif 30.0 > float(callist[2]):
            notes = 'low ratio'
            rowcolor = 'y'
            assaynoteslist.append('cal')
#append the list with notes and color value
        callist.append(notes)
        callist.append('')
        callist.append(rowcolor)
        controllist.append(callist)
#test to see if there are MOR Controls
        if 'mor above cal' in analytedict.keys():
            MORtest = True
        else:
            MORtest = False
#now process the controls
        for controltype in [' below cal', ' above cal']:
#setup the control list so we can add things in the order need, and a dictionary to store the data
            conposlist = ['Average of Run', 'BOR', 'EOR']
            conposdict = {'Average of Run':['Average of Run'],'BOR':['BOR'],'EOR':['EOR']}
#use these list to calculate teh average or the runs
            conabs = []
            conratios = []
#if we have MOR controls add those items in
            if MORtest:
                conposlist.insert(2,'MOR')
                conposdict['MOR'] = ['MOR']
#for everything expect the average get the data out of the dict
            for position in conposlist[1:]:
#add to the position dict and the average list for the abs and the ratio
                conposdict[position].append(analytedict[position.lower()+controltype]['abs'])
                conabs.append(analytedict[position.lower()+controltype]['abs'])
                conposdict[position].append(analytedict[position.lower()+controltype]['ratio'])
                conratios.append(analytedict[position.lower()+controltype]['ratio'])
#add the average list to the dictionary
            analytestandard[controltype.lstrip()] = conratios
#average the list and round to 3 for abs and 1 for ratio
            conposdict['Average of Run'].append(round(np.mean(conabs),3))
            conposdict['Average of Run'].append(round(np.mean(conratios),1))
#crude way of seeing if there is any drift subtracted each position from each other position
            if MORtest:
                driftvalues = [abs(conratios[0]-conratios[1]),abs(conratios[0]-conratios[2]),
                               abs(conratios[1]-conratios[2])]
            else:
                driftvalues = [abs(conratios[0]-conratios[1])]
#if its 10 or over we call it drift, made up number by the way
            for value in driftvalues:
                if 10.0 <= value:
                    driftcheck = True
                else:
                    driftcheck = False
#add notes as need
            if controltype == ' below cal':
#also get the average below ratio for flagging samples between the bco and co
                belowratio = conposdict['Average of Run'][2]
                for position in conposlist:
#if the bco ratio is lower then the co flag it
                    if calratio > conposdict[position][2]:
#if there is drift and the average ratio is below the cutoff joint note
                        if position == 'Average of Run' and driftcheck:
                            notes = 'ratio below cal, check drift'
                        else:
                            notes = 'ratio below cal'
                        rowcolor = 'y'
                        assaynoteslist.append('bcc')
#if there just drift flag the average
                    elif position == 'Average of Run' and driftcheck:
                        notes = 'check drift'
                        rowcolor = 'y'
                        assaynoteslist.append('bcc')
                    else:
                        notes = 'None'
                        rowcolor = 'none'
#add the notes and the color
                    conposdict[position].append(notes)
                    conposdict[position].append('')
                    conposdict[position].append(rowcolor)

            elif controltype == ' above cal':
                for position in conposlist:
#if the aco ratio is higher then the co flag it
                    if calratio < conposdict[position][2]:
#if there is drift and the average ratio is below the cutoff joint note
                        if position == 'Average of Run' and driftcheck:
                            notes = 'ratio above cal, check drift'
                        else:
                            notes = 'ratio above cal'
                            rowcolor = 'y'
                            assaynoteslist.append('acc')
#if there just drift flag the average
                    elif position == 'Average of Run' and driftcheck:
                        notes = 'check drift'
                        rowcolor = 'y'
                        assaynoteslist.append('acc')
                    else:
                        notes = 'None'
                        rowcolor = 'none'
#add the notes and the color
                    conposdict[position].append(notes)
                    conposdict[position].append('')
                    conposdict[position].append(rowcolor)

#walk through and add each position list to a templsit
            templist = []
            for position in conposlist:
                templist.append(conposdict[position])
#add the list of position list to the control list
            controllist.append(templist)

#Add the lists of list to the analyte list
        report_data['analytepdfs'][analyte].append(controllist)

#if the we have no flags for the assay summary, we have not notes
        if len(assaynoteslist) == 0:
            forassaysum.append('None')
            forassaysum.append('none')
#other wise add those controls that were an issue
        else:
            notes = 'flagged for: '
            for item in set(assaynoteslist):
                notes = notes + item + ', '
#cut off any trailing comma or space
            forassaysum.append(notes[0:-2])
            forassaysum.append('y')

#add the anayte list to the assay summary
        report_data['assaypdf'].append(forassaysum)
#re for CT#
        ctnumcheck = re.compile('\d\d\d\d\d\d[A-Z]?')
#walk through all the samples, this will included the controls and blank
        for sample in analytedict:
#make a list for with all the pertinate information
            screenrow = [analyte, str(covalue) +'ng/mL',calratio, round(analytedict[sample]['ratio'],1),
                         round(analytedict[sample]['abs'],3)]
#if we are below the CO but above the average BCO ratio we are negative but blue
            if belowratio > round(analytedict[sample]['ratio'],1) > calratio:
                screenrow.append('Negative')
                screenrow.append('b')
#if we are above the CO we are yellow but negative
            elif calratio > round(analytedict[sample]['ratio'],1):
                screenrow.append('Positive')
                screenrow.append('y')
#otherwise we default to negative
            else:
                screenrow.append('Negative')
                screenrow.append('none')
#see if we have a CT number
            isctnum = ctnumcheck.match(sample.upper())
            if isctnum:
#if we do but don't have a letter add 'A', make sure we have a sample in the dict and append the new list
                if 6 == len(isctnum.group()):
                    samplect = isctnum.group() +'A'
#are we in the sample list? if so add the data, if not, flag and pass
                    if samplect in samplelist:
                        ctnumsread.append(int(isctnum.group()))
#set the dictionary to the sample number, add just the numeric poritions to be used in annotations
                        report_data['samplepdfs'].setdefault(samplect,[int(isctnum.group()),[]])
                        templist = report_data['samplepdfs'][samplect][1]
                        templist.append(screenrow)
#add data to the limsout as follows analyte, test_id, ct#, result, matrix
                        limsoutput.append([analyte,cutoffs[analyte]['id'],samplect,screenrow[5],matrix])
                    else:
                        wrong_ct.append([samplect,analyte])
#if we do have a letter use that, make sure we have a sample in the dict and append the new list
                elif 7 == len(isctnum.group()):
                    samplect = isctnum.group()
                    if samplect in samplelist:
#add just the numeric porition to a list for pdf annotations
                        ctnumsread.append(int(isctnum.group()[0:6]))
#set the dictionary to the sample number, add just the numeric poritions to be used in annotations
                        report_data['samplepdfs'].setdefault(samplect,[int(isctnum.group()[0:6]),[]])
                        templist = report_data['samplepdfs'][samplect][1]
                        templist.append(screenrow)
#add data to the limsout as follows analyte, test_id, ct#, result, matrix
                        limsoutput.append([analyte,cutoffs[analyte]['id'],samplect,screenrow[5],matirx])
                    else:
                        wrong_ct.append([samplect,analyte])
#or if we have another valid name, make sure we have a sample in the dict and append the new list
                elif sample.lower().startswith('val') or sample.lower().startswith('exp'):
                    report_data['samplepdfs'].setdefault(isctnum.group(),['none',[]])
                    templist = report_data['samplepdfs'][int(isctnum.group())][1]
                    templist.append(screenrow)
#otherwise don't do anything
                else:
                    pass
    report_data['ctnums'] = sorted(set(ctnumsread))

#print out those samples that were encountered but no in the samplelist
    print ''
    print 'The following samples were encounted in the data but not in the samplelist, \nand were not processed:'
    for pair in wrong_ct:
        print pair[0] +  ' encounted on ' + pair[1] + ' plate'

#sort the limsout put list and return it and the standdata
    limsoutput = sorted(limsoutput)
    limsoutput.insert(0,['results',''])
    return limsoutput, standarddata
