import csv
import datetime
import numpy as np
import os

#a function which takes the lims data and the data from the summary csv and sorts and links them
def outputdict(samples, limsdata, newdata, mondaydate):
    opdata = {}
    opresults = []
#walk through the samples selected from the gui
    for sample in samples:
#a control value to  be able to pass on samples that are less then 3 months old
        checksample = True
        initialdate = sorted(limsdata[int(sample)])[0]
#find the delta based on date of the monday of the week the samples are run
        deltadays = abs((mondaydate - initialdate).days)
#numbers are 8, 5 and 2 months and one days, since i don't know exactly the citeria used for selectiing the validation samples.
        if deltadays >= 241:
            opdata[sample] = {'inidate':initialdate.strftime('%Y-%m-%d'),
                            'delta':'9 Months',
                            'iniresult':float(limsdata[int(sample)][initialdate])}
        elif deltadays >= 151:
            opdata[sample] = {'inidate':initialdate.strftime('%Y-%m-%d'),
                            'delta':'6 Months',
                            'iniresult':float(limsdata[int(sample)][initialdate])}
        elif deltadays >= 61:
            opdata[sample] = {'date':initialdate.strftime('%Y-%m-%d'),
                            'delta':'3 Months',
                            'iniresult':float(limsdata[int(sample)][initialdate])}
        else:
            print sample + 'appears to be less then 3 months old, please consult with a supervisor'
            checksample = False

#if we are checking the sample the go through and pull out the data for the sample from the summary file
        if checksample:
            newresults = []
            newdates = []
            for line in newdata['ethanol']:
                if newdata['ethanol'][line]['name'].startswith(sample):
                    newresults.append(float(newdata['ethanol'][line]['calc']))
                    newdates.append(newdata['ethanol'][line]['doi'])

#if we don't have any results for the sample let the user know
            if len(newresults) < 1:
                print sample + ' does not not have any results in selected summary file'
#append the list with samples that have results, and then collect the data
            else:
                opresults.append(sample)
#take the date of the first injection (if the injection are close to midnight you can get two dates)
                newdate = sorted(newdates)[0]
#average the results
                newmean = np.mean(newresults)
                perdiff = ((newmean - opdata[sample]['iniresult'])/opdata[sample]['iniresult'])*100
                opdata[sample]['newresult'] = newmean
                opdata[sample]['newdate'] = newdate
                opdata[sample]['perdiff'] = perdiff

    return opdata, opresults

#a function to read, update and write the new logfile for each time period, also returns a list of percent differences
def bacrecords(filedir, newdata, timeperiod, outputloc):
#get the file location and names
    outputloc = os.path.join(filedir, timeperiod + ' data')
    outputfile = os.path.join(outputloc,'log as of ' + datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')+'.csv')
#find the last updated log file.
    lastupdate = os.path.join(outputloc,sorted(os.listdir(outputloc))[-1])
    opdata = []
    measurements = []
#open the and read the last log file
    with open(lastupdate, 'rU') as csvfile:
        recorddata = csv.reader(csvfile)
        for row in recorddata:
#we are going to record the data again so might add it as we go through this list
            opdata.append(tuple(row))
#clearly the header is of no use to us
            if row[0] == 'date_tested':
                pass
#we are just adding the percent difference to the the list we return
            else:
                measurements.append(float(row[2]))

    for sample in newdata:
#if we sample has the right delta
        if newdata[sample]['delta'] == timeperiod:
#and isn't already in the opdata, and thus the measurement list add it to both
            if (newdata[sample]['newdate'],str(sample),str(newdata[sample]['perdiff'])) not in opdata:
                measurements.append(newdata[sample]['perdiff'])
                opdata.append((newdata[sample]['newdate'],sample,str(newdata[sample]['perdiff'])))

#write out the log file and return the list of percent differences
    with open(outputfile, 'wb') as op:
        wo = csv.writer(op)
        for row in opdata:
            wo.writerow(row)
    return measurements

#a function to generate the summary data
def summarydata(leader, length, measurements):
#if the number of measurements is less then the requried length, report N/A out
    if len(measurements) < length:
        return (leader,'N/A','N/A','N/A','N/A','N/A')
#0 denotes all records should be processed
    elif length == 0:
        testrange = measurements
        mean = np.mean(testrange)
        std = np.std(testrange)
        rsd = (std/mean)*100
        lowrange = mean - 2*std
        highrange = mean + 2*std
        return (leader, str(round(mean,3))+'%', round(std,3), str(round(rsd,1))+'%',
                str(round(lowrange,3))+'%', str(round(highrange,3))+'%')
    else:
#measurements should be given a list of oldest at 0 to newest. The last bit should give us just those last items
        testrange = measurements[len(measurements)-length:]
        mean = np.mean(testrange)
        std = np.std(testrange)
        rsd = std/mean
        lowrange = np.mean - 2*std
        highrange = np.mean + 2*std
        return (leader, str(round(mean,3))+'%', round(std,3), str(round(rsd,1))+'%',
                str(round(lowrange,3))+'%', str(round(highrange,3))+'%')
