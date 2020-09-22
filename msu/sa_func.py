import csv
import datetime
import os
import re
import xlsxwriter

def crn_parser(loc):
    crndict = {'00000':{'course':'student worker',
                        'section':'na',
                        'instructor':'Senga',
                        'desc':'na_Senga',
                        'students':{}}}

    with open(loc, newline = '') as csvfile:
        raw_data = csv.reader(csvfile, delimiter = ',')
        for row in raw_data:
            if row[0] == '00000':
                pass
            else:
                crndict[row[0]] = {'course':row[1],
                                   'section':row[2],
                                   'instructor':row[3],
                                   'desc':row[2].replace(': ','_') + '_' + row[3],
                                   'students':{}}
        return crndict

def banner_parser(loc,crndict,esid):
    for file in os.listdir(loc):
        crn = file.split('.')[0]
        fileloc = os.path.join(loc,file)
        rowcount = 0
        passfile = False
        blankrows = False
        if crn not in crndict.keys():
            print(crn + ' not in CRN list and will not be processed')
            pass
        else:
            with open(fileloc,newline = '') as csvfile:
                raw_data = csv.reader(csvfile, delimiter = ',')
                for row in raw_data:
                    if passfile:
                        pass
                    else:
                        if rowcount == 6:
                            if not row[0].startswith('  CRN'):
                                print('file: ' + file + ' does not fit expected format, please review')
                                print('skipping file ' + file)
                                passfile = True
                        elif rowcount == 7:
                            crncheck = row[0].split(' ')[1]
                            course = row[0].split(' ')[5]
                            if not crn == crncheck:
                                print('file ' + file + ' is named incorrectly')
                                print('CRN in the file is ' + crncheck)
                                passfile = True
                            if not crndict[crn]['course'] == course:
                                print('different course found then expected for ', crn)
                                print('expected ' + crndict[crn]['course'] + ', got ' + course)
                        elif rowcount == 10:
                            instructor = row[0].split(',')[0].strip()
                            if not crndict[crn]['instructor'] == instructor:
                                print('different instructor found then expected for ', crn)
                                print('expected ' + crndict[crn]['instructor'] + ', got ' + instructor)
                        elif rowcount > 17 and not blankrows:
                            if len(row[0].split(' ')) <= 1:
                                blankrows = True
                            else:
                                sid = row[0][31:40]
                                workingstring = row[0][5:31]
                                workingstring = workingstring.strip()
                                names = workingstring.split(',')
                                esid.append(sid)
                                crndict[crn]['students'][sid] = {'name':names[1].strip() + ' ' + names[0],
                                                                 'timestamp':'not completed',
                                                                 'contact':'not completed',
                                                                 'phone':'not completed',
                                                                 'agreed':'no',
                                                                 'eye':'not completed',
                                                                 'metadata':[]}

                    rowcount += 1

def survey_parser(loc,crndict,esid):
    newdata = 'none'
    cdate = datetime.datetime(1900,1,1,0,0,0)
    for file in os.listdir(loc):
        fileparts = file.split('_')
        fdate = datetime.datetime.strptime(fileparts[1]+'_'+fileparts[2][0:-4],'%B %d, %Y_%H.%M')
        if fdate > cdate:
            cdate = fdate
            newdata = file

    fileloc = os.path.join(loc,newdata)
    print('Using File: ',newdata)

    raw_list = []

    with open(fileloc,newline = '') as csvfile:
        raw_data = csv.reader(csvfile, delimiter = ',')
        for row in raw_data:
            if row[0] in ['StartDate','Start Date','{"ImportId":"startDate","timeZone":"America/Denver"}']:
                pass
            elif row[2] == 'Survey Perview':
                pass
            elif row[19] == '':
                pass
            else:
                templist = [row[1]]+row[17:19]+row[22:26]+[row[19]]+[row[20].replace(': ','_')+ '_' + row[21]]
                raw_list.append(templist)

        for item in raw_list:
            mdtemp = []
            timestamp = datetime.datetime.strptime(item[0],'%Y-%m-%d %H:%M:%S')

            if len(item[2]) == 6:
                sid = '900' + item[2]
            else:
                sid = item[2]


            phonelist = [s for s in item[4] if s.isdigit()]
            if len(phonelist) == 10:
                phone = '(' + ''.join(phonelist[0:3]) + ')-' + ''.join(phonelist[3:6]) + '-' + ''.join(phonelist[6:])
                if len(phone) > 14:
                    mdtemp.append('py')
                else:
                    mdtemp.append('none')
            else:
                phone = item[4]
                mdtemp.append('pr')

            if item[5]:
                agree = 'yes'
            else:
                agree = 'no'

            if item[6].endswith('laboratory period.'):
                eye = 'Wear eye protection over glasses'
            elif item[6].endswith('chemistry department.'):
                eye = 'Wear eye protection over contacts'
            else:
                eye = 'No corrective lenses used'

            if len(sid) == 9:
                if sid in esid:
                    for crn in crndict.keys():
                        if sid in crndict[crn]['students'].keys():
                            crndict[crn]['students'][sid] = {'name':item[1],
                                                             'timestamp':timestamp,
                                                             'contact':item[3],
                                                             'phone':phone,
                                                             'agreed':agree,
                                                             'eye':eye,
                                                             'metadata':mdtemp}
                else:
                    crndict['99990']['students'][sid] = {'name':item[1],
                                                         'timestamp':timestamp,
                                                         'contact':item[3],
                                                         'phone':phone,
                                                         'agreed':agree,
                                                         'eye':eye,
                                                         'metadata':mdtemp,
                                                         'class':item[8]}
            else:
                sidadded = False
                for crn in crndict.keys():
                    if crndict[crn]['desc'] == item[8]:
                        mdtemp.append('sr')
                        sidadded = True
                        crndict[crn]['students'][sid] ={'name':item[1],
                                                        'timestamp':timestamp,
                                                        'contact':item[3],
                                                        'phone':phone,
                                                        'agreed':agree,
                                                        'eye':eye,
                                                        'metadata':mdtemp}
                if not sidadded:
                    print(sidadded)
                    crndict['99991']['students'][sid] = {'name':item[1],
                                                         'timestamp':timestamp,
                                                         'contact':item[3],
                                                         'phone':phone,
                                                         'agreed':agree,
                                                         'eye':eye,
                                                         'metadata':mdtemp,
                                                         'class':item[8]}

def workbookmrk(opname,courseoutput):
    basecolumns = ['name','timestamp','agreed','eye','contact','phone']
    baseheader = ['900 Number', 'Student Name','Date Complete','Agreed?','Eye Protection',
                  'Emergency Contact Names','Emergency Contact Phone Number']

    workbook = xlsxwriter.Workbook(opname)

    header = workbook.add_format({'bg_color':'#ffffff','bold':True,'bottom':2,'right':1,'align':'center'})
    wdefault = workbook.add_format({'bg_color':'#ffffff','bottom':2,'right':1,'align':'center'})
    gdefault = workbook.add_format({'bg_color':'#d3d3d3','bottom':2,'right':1,'align':'center'})
    yellow = workbook.add_format({'bg_color':'#ffffe0','bold':True,'bottom':2,'right':1,'align':'center'})
    red = workbook.add_format({'bg_color':'#ffcccb','bold':True,'bottom':2,'right':1,'align':'center'})
    wdt = workbook.add_format({'num_format':'yyyy-mm-dd HH:MM:SS','bottom':2,'right':1,'bg_color':'#ffffff',
                               'align':'center'})
    gdt = workbook.add_format({'num_format':'yyyy-mm-dd HH:MM:SS','bottom':2,'right':1,
                               'bg_color':'#d3d3d3','align':'center'})

    sheetdict = {}
    for section in sorted(courseoutput.keys()):
        columnnames = []
        headertitles = []
        if section in ['possible drops','student ID error']:
            columnnames = columnnames + basecolumns
            columnnames.append('class')
            headertitles = headertitles + baseheader
            headertitles.append('Listed Class')
        else:
            columnnames = basecolumns
            headertitles = baseheader

        workingsheet = workbook.add_worksheet(section)
        workingsheet.write_row(0,0,headertitles,header)
        row = 1
        if len(courseoutput[section]) <= 0:
            pass
        else:
            for student in courseoutput[section]:
                if row%2 == 0:
                    gformat = wdefault
                    dformat = wdt
                else:
                    gformat = gdefault
                    dformat = gdt

                if 'sr' in courseoutput[section][student]['metadata']:
                    workingsheet.write(row,0,student,red)
                else:
                    workingsheet.write(row,0,student,gformat)

                col = 1
                for cell in columnnames:
                    if cell != 'timestamp':
                        workingsheet.write(row,col,courseoutput[section][student][cell],gformat)
                    elif cell == 'phone' and 'yp' in courseoutput[section][student]['metadata']:
                        workingsheet.write(row,col,courseoutput[section][student][cell],yellow)
                    elif cell == 'phone' and 'rp' in courseoutput[section][student]['metadata']:
                        workingsheet.write(row,col,courseoutput[section][student][cell],red)
                    else:
                        workingsheet.write(row,col,courseoutput[section][student][cell],dformat)
                    col += 1
                row += 1

        for x in range(0,7):
            if x == 0:
                workingsheet.set_column(x,x,11)
            elif x in [1,4,5,6]:
                workingsheet.set_column(x,x,32)
            elif x == 2:
                workingsheet.set_column(x,x,18)
            elif x == 3:
                workingsheet.set_column(x,x,8)
        if len(headertitles) == 8:
            workingsheet.set_column(7,7,30)

    workbook.close()
