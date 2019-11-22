import csv
import datetime
import pyperclip

from bvrgui import *
from bvrfunc import *
from fiddatasort import *

#setup the dir information that are not going to change.
loutputdir = 'c://pve//bvr//outputs'
outputloc = r'//admin.chematox.com/public/labtools/jimscripts/BAC validations'

#get todays date a baselin and generate the timestamp
today = datetime.date.today()
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

#call the gui
if __name__ == '__main__':
     sampleslist, limsdata, summaryfile, weekofdate = maingui()

#get the data out of the summary file.
newdata = fiddatasort(summaryfile)
#get output data
opdict, sampleswithresults = outputdict(sampleslist, limsdata, newdata, weekofdate)

#for each time period generate add the data to the summary file
summaryop = [('Summary File',''),('Compiled on: ',datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')),('','')]
for item in ['3 Months', '6 Months', '9 Months']:
    summaryop.append(('',''))
    summaryop.append(('Time Period: ',item))
    summaryop.append(('Number of Samples', 'Mean %Diff', 'St. Dev', 'RSD', 'Mean - 2sd', 'Mean + 2sd'))
#get the data from the logs for each time period
    measurements = bacrecords(outputloc, opdict, item, outputloc)
    for item in (('All Samples',0),('Last Three Months',12),('Last Month',4)):
#get the calcuation for each subjection of data.
        summaryop.append(summarydata(item[0],item[1],measurements))

#write out the summary file
summaryopfile = os.path.join(os.path.join(outputloc,'summary files'), 'BAC validation summary as of '+ datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')+'.csv')

with open(summaryopfile, 'wb') as op:
    wo = csv.writer(op)
    for row in summaryop:
        wo.writerow(row)

#writeout the textfile for pasting into jira.
textop = []
clipboard = ''
for sample in sorted(sampleswithresults):
    line = sample + ' ' + str(round((opdict[sample]['newresult']),3)) + ' (' + str(round(opdict[sample]['iniresult'],3)) + ') ' + str(round(opdict[sample]['perdiff'],2)) +'%\r\n'
    textop.append(line)
    clipboard = clipboard + line

#copy to the clipboard for ease of use.
pyperclip.copy(clipboard)

outputtext = os.path.join(loutputdir,'BAC validation results for the week of ' + weekofdate.strftime('%Y-%m-%d') + ' (' + timestamp +').txt')
#write out to a textfile
with open(outputtext, 'w') as wo:
    for line in textop:
        wo.write(line)
