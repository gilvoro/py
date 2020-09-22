#helper method for sa_main.py

# import required libraries
import csv
import datetime
import logging
import os
import re
import xlsxwriter


def crn_parser(loc,swloc,esid):
    """Generate a dictionary of CRN listing course number('course'),section number +day and time('section'),
       section instructor ('instructor'), section + instructor ('desc'), and sub-dictionary to hold student
       information
    
        Args:
            loc: location of the crn list file
            swloc: location of student worker .csv files
            esid: list of the expected student ID numbers
        Returns:
            Returns a dictionary
    """
#add the student worker crn
    crndict = {'00000':{'course':'student worker',
                        'section':'na',
                        'instructor':'Senga',
                        'desc':'na_Senga',
                        'students':{}}}
    
# setup crn for responses that cannot be parsed for what every reason
# these are students that don't show up in any of the sections
    crndict['99990'] = {'course': 'non-parsable responses',
                        'section': 'possible drops',
                        'instructor': '',
                        'desc': 'possible drops',
                        'students': {}}

# these are students that do not have a ID == 9
    crndict['99991'] = {'course': 'non-parsable responses',
                        'section': 'student ID error',
                        'instructor': '',
                        'desc': 'student ID error',
                        'students': {}}
    
#open the crn_list and add the CRNs to the dictionary
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
        
# load the student worker file and put them into crn "00000"
# this will need to be adpated based on the type of data received
    with open(swloc, newline='') as csvfile:
        raw_data = csv.reader(csvfile, delimiter=',')
        for row in raw_data:
            if len(row) <= 0:
                pass
            else:
                esid.append(row[2].strip())
                crndict['00000']['students'][row[2].strip()] = {'name': row[1].strip() + ' ' + row[0].strip(),
                                                                'timestamp': 'not completed',
                                                                'contact': 'not completed',
                                                                'phone': 'not completed',
                                                                'agreed': 'no',
                                                                'eye': 'not completed',
                                                                'metadata': []}

#return the dictionary        
        return crndict

def banner_parser(loc,crndict,esid):
    """A method to parse class rosters downloaded from banner to retrive
       the student ID and names and add them to the apporiate crn in the 
       crndict
       
       Args:
            loc: the directory containing the banner files, labeled by crn
            crndict: the dictionary containin the crn information including class roster
            esid: list of the expected student ID numbers
            
       Returns: modifies crndict and esid inplace, retuns a dictionary of course students have withdrawn from
                keyed to their ID
    """
#a list to hold the SID of those individuals that have withdrawn, and from what classes
    withdrawndict = {}
#interate through the files in
    for file in os.listdir(loc):
#files should be named as simple the crn the file repersents
        crn = file.split('.')[0]
        fileloc = os.path.join(loc,file)
#program needs to  keep track of what row is currently being processed
        rowcount = 0
#varible that controls if the script should continue to process the file or not
        passfile = False
#varible to indicate if the rest of the file is (mostly) blank rows
        blankrows = False
#the line that student information starts appearing. Set above the max number of rows initially
        studentinfo = 100
#if for some reason there is crn that is not in list pass the file.
        if crn not in crndict.keys():
            logging.info(crn + ' not in CRN list and will not be processed')
            pass
#open the file and start interating through it
        else:
            with open(fileloc,newline = '') as csvfile:
                raw_data = csv.reader(csvfile, delimiter = ',')
                for row in raw_data:
                    if passfile:
                        pass
#check the file is in the expected format, if not stop processing before an error occurs
                    else:
                        if rowcount == 6:
                            if not row[0].startswith('  CRN'):
                                print('file: ' + file + ' does not fit expected format, please review')
                                print('skipping file ' + file)
                                logging.info('file: ' + file + ' does not fit expected format,skipped')
                                passfile = True
#check the file contains a crn that matches the file name, if it doesn't stop processing it
                        elif rowcount == 7:
                            crncheck = row[0].split(' ')[1]
                            course = row[0].split(' ')[5]
                            if not crn == crncheck:
                                print('file ' + file + ' is named incorrectly')
                                print('CRN in the file is ' + crncheck)
                                logging.info(file + '!= CRN in file, ' + crn)
                                passfile = True
#check the course in the file matches the course in the crndict, mismatch does not stop the processing
                            if not crndict[crn]['course'] == course:
                                print('different course found then expected for ', crn)
                                print('expected ' + crndict[crn]['course'] + ', got ' + course)
                                logging.info('For CRN ' + crn + ' expected ' + crndict[crn]['course'] + ', got ' + course)
#check the instuctor in the file matches the instuctor in the crndict, mismatch does not stop the processing
                        elif rowcount == 10:
                            instructor = row[0].split(',')[0].strip()
                            if not crndict[crn]['instructor'] == instructor:
                                print('different instructor found then expected for ', crn)
                                print('expected ' + crndict[crn]['instructor'] + ', got ' + instructor)
                                logging.info('For CRN ' + crn + ' expected ' + crndict[crn]['course'] + ', got ' + course)
#if at least 10 lines have been read, and the blank rows have not started, start scanning for 'Student'
                        elif rowcount > 10 and not blankrows:
#if the line starts with 'Student', student info will appear in 2 lines. 
                            if 'Student' in row[0].split(' '):
                                studentinfo = rowcount + 2
#when rowcount is at or above studentinfo, check to see the row is blank
                            elif rowcount >= studentinfo:
                                if len(row[0].split(' ')) <= 1:
                                    blankrows = True
#if not extract the student data
                                else:
#student name is white space padded, but the student id is at the same indices
                                    sid = row[0][31:40]
#the student name appears after the four digits and before the student id
                                    workingstring = row[0][5:31]
#remove the whitespace around the name
                                    workingstring = workingstring.strip()
#names are list with surname first, and seperated by a comma, split into individual names
                                    names = workingstring.split(',')
#append the student id to the list.
#note an id may appear multiply times in the list
                                    esid.append(sid)
#if the student has withdrawn and update the dictionary and list                                 
                                    if row[0][65:69].startswith('W'):
                                        logging.info(sid + ' has withdrawn from ' + course)
                                        withdrawndict.setdefault(sid,[])
                                        withdrawndict[sid].append(course)                  
#update the crn diction to with the name becoming given name space surname
                                    crndict[crn]['students'][sid] = {'name':names[1].strip() + ' ' + names[0],
                                                                     'timestamp':'not completed',
                                                                     'contact':'not completed',
                                                                     'phone':'not completed',
                                                                     'agreed':'no',
                                                                     'eye':'not completed',
                                                                     'metadata':[]}


                    rowcount += 1
    return withdrawndict

def survey_parser(loc):
    """A method for processing data from qualtrics survey data for the safety agreements
    
       Args:
            loc:the directory with qualtrics csv
        
        Returns: a dictionary with survey data sorted by student
    """
    
    studentdict = {}
#the file that was generated the most recently
    newdata = 'none'
#the date/time of the current file
    cdate = datetime.datetime(1900,1,1,0,0,0)
#interate through the files and find the one with the most recent date/time
    for file in os.listdir(loc):
        fileparts = file.split('_')
#pull the date out of the file
        fdate = datetime.datetime.strptime(fileparts[1]+'_'+fileparts[2][0:-4],'%B %d, %Y_%H.%M')
        if fdate > cdate:
            cdate = fdate
            newdata = file

#set the file location
    fileloc = os.path.join(loc,newdata)
    print('Using File: ',newdata)
    logging.info('Using File: ' + newdata)
    raw_list = []

#open the file and start processing
    with open(fileloc,newline = '') as csvfile:
        raw_data = csv.reader(csvfile, delimiter = ',')
        for row in raw_data:
#pass those rows that lack relvent information
            if row[0] in ['StartDate','Start Date','{"ImportId":"startDate","timeZone":"America/Denver"}']:
                pass
            elif row[2] == 'Survey Perview':
                pass
            elif row[19] == '':
                pass
#row[1] timestamp of completion, row[17] student name, row[18] student#, row[19] course#, 
#row[22] emergency contact, row[23] emergency phone#, row[24] agreement, row[25] corrective lense info
#row[20] section/day/time, row[21] instuctor
#add a new list information to raw_list 
            else:
                templist = [row[1]]+row[17:19]+row[22:26]+[row[19]]+[row[20].replace(': ','_')+ '_' + row[21]]
                raw_list.append(templist)

#step through each student in rawlist and process the information
        for item in raw_list:
            mdtemp = []
#format the date
            timestamp = datetime.datetime.strptime(item[0],'%Y-%m-%d %H:%M:%S')

#if only 6 digits are present add 900 to the number
            if len(item[2]) == 6:
                sid = '900' + item[2]
            else:
                sid = item[2]

#make a list of the digits in the phone#
            phonelist = [s for s in item[4] if s.isdigit()]
#if there are exactly 10 elements in the phonelist put it back together as (xxx)-xxx-xxxx            
            if len(phonelist) == 10:
                phone = '(' + ''.join(phonelist[0:3]) + ')-' + ''.join(phonelist[3:6]) + '-' + ''.join(phonelist[6:])
#not sure how this would trigger...                
                if len(phone) > 14:
                    mdtemp.append('py')
                else:
                    mdtemp.append('none')
#if the phonelist doesn't have 10 number just use orginal item and flag it.
            else:
                phone = item[4]
                mdtemp.append('pr')
#check to see if they they have agreed
            if item[5]:
                agree = 'yes'
            else:
                agree = 'no'
#use the first part of the response to determine the final response
            if item[6].endswith('laboratory period.'):
                eye = 'Wear eye protection over glasses'
            elif item[6].endswith('chemistry department.'):
                eye = 'Wear eye protection over contacts'
            else:
                eye = 'No corrective lenses used'
#add the student to the dictionary
            studentdict[sid] = {'name':item[1],
                                'timestamp':timestamp,
                                'contact':item[3],
                                'phone':phone,
                                'agreed':agree,
                                'eye':eye,
                                'class':item[8],
                                'metadata':mdtemp}

    return studentdict

def student_replacer(loc,studentdict):
    """A method for replacing data in the studentdict for students that have incorrectly entered their SID or are not attending class
    
       Args:
            loc: the path to the student_replacment file that contains those enteries that need updated
            studentdict: dict generated by survey_parser-holds student responses
        
        Returns: nothing, updated the studentdict in place
    """
#open the file and read each entry into a list
    templist = []
    with open(loc,newline ='') as csvfile:
        raw_data = csv.reader(csvfile,delimiter = ',')
        for row in raw_data:
            templist.append(row)

#go through the list
    for item in templist:
#pass if there is nothing in the list        
        if len(item) < 1:
            pass
#first item in the list is the incorrect student id which should be in studentdict
        elif item[0] in studentdict:
            logging.info('replacing data listed for ' + item[0])
#add a new entry using the correct student id
            studentdict[item[1]] = {'name':item[2],
                                    'timestamp':item[3],
                                    'contact':item[6],
                                    'phone':item[7],
                                    'agreed':item[4],
                                    'eye':item[5],
                                    'class':item[8],
                                    'metadata':[]}
#delete the old entry
            del studentdict[item[0]]

#if we have a over-write entry because non-attendance over-write the existing entry
        elif item[9] == 'over-write':
            logging.info('Adding non-attending: ' + item[0])
            studentdict[item[1]] = {'name':item[2],
                                    'timestamp':item[3],
                                    'contact':item[6],
                                    'phone':item[7],
                                    'agreed':item[4],
                                    'eye':item[5],
                                    'class':item[8],
                                    'metadata':['lg']}


def merger(studentdict, crndict, esid):
    """A method for adding the student data from studentdict into the crndict
    
       Args:
            studentdict: dict generated by survey_parser-holds student responses
            crndict: the dictionary containin the crn information including class roster
            esid: list of the expected student ID numbers 
            
            
        Returns: nothing, updated the crndict in place
    """
    for sid in studentdict:
#if the student ID is the expected length check the to see if its in our expected esid list
        if len(sid) == 9:
            if sid in esid:
#if it is in the list walk through the lab sections add the student to any they are registered for
                for crn in crndict.keys():
                    if sid in crndict[crn]['students'].keys():
                        crndict[crn]['students'][sid] = studentdict[sid]
#if its not put them in the potenial droplist
            else:
                crndict['99990']['students'][sid] = studentdict[sid]
#if the student ID isn't exactly 9 numbers try to place the student with the chosen class
        else:
#varible to check if the student placed into a class
            sidadded = False
            for crn in crndict.keys():
                if crndict[crn]['desc'] == studentdict[sid]['class']:
                    studentdict[sid]['metadata'].append('sr')
                    sidadded = True
                    crndict[crn]['students'][sid] =studentdict[sid]
#if the student cannot be place put student on the incorrect SID list
            if not sidadded:
                print(sidadded)
                crndict['99991']['students'][sid] = studentdict[sid]

def workbookmrk(opname,courseoutput,coursenum,withdrawndict):
    """A method to generate a formated excel file to be uploaded to sharepoint
    
       Args:
            opname: the name and path of the excel file
            courseoutput: a dictionary generated from crndict containing all the sections of single course.            
            coursenum: the coursenum used to insure we do not withdraw a student from the wrong course
            withdrawndict: a dict with the list of course a student has withdrawn from keyed to their ID#
            
        Returns: nothing, generates an excel file
    """
#a list of the keys to use, and a list for the headers
    basecolumns = ['name','timestamp','agreed','eye','contact','phone']
    baseheader = ['900 Number', 'Student Name','Date Complete','Agreed?','Eye Protection',
                  'Emergency Contact Names','Emergency Contact Phone Number']

#make the workbook
    workbook = xlsxwriter.Workbook(opname)

#setup all the formats
    header = workbook.add_format({'bg_color':'#ffffff','bold':True,'bottom':2,'right':1,'align':'center'})
    wdefault = workbook.add_format({'bg_color':'#ffffff','bottom':2,'right':1,'align':'center'})
    gdefault = workbook.add_format({'bg_color':'#d3d3d3','bottom':2,'right':1,'align':'center'})
    yellow = workbook.add_format({'bg_color':'#ffffe0','bold':True,'bottom':2,'right':1,'align':'center'})
    red = workbook.add_format({'bg_color':'#ffcccb','bold':True,'bottom':2,'right':1,'align':'center'})
    greyed = workbook.add_format({'bg_color':'#707b7c','font_color':'#d3d3d3','bottom':2,'right':1,'align':'center'})
    wdt = workbook.add_format({'num_format':'yyyy-mm-dd HH:MM:SS','bottom':2,'right':1,'bg_color':'#ffffff',
                               'align':'center'})
    gdt = workbook.add_format({'num_format':'yyyy-mm-dd HH:MM:SS','bottom':2,'right':1,
                               'bg_color':'#d3d3d3','align':'center'})

#for each section make a new sheet
    for section in sorted(courseoutput.keys()):
        columnnames = []
        headertitles = []
#for the non-parsable book add class a column
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
#if for some reason there are no students in the section move on
        if len(courseoutput[section]) <= 0:
            pass
        else:
            for student in courseoutput[section]:
#if the student has withdrawn from the class greyout the whole row and update the timestamp
                if student in withdrawndict and coursenum in withdrawndict[student]:
                    gformat = greyed
                    dformat = greyed
                    courseoutput[section][student]['timestamp'] = 'withdrawn'
#if the metadata indicates the student is non-attending greyout the whole row
                elif 'lg' in courseoutput[section][student]['metadata']:
                    gformat = greyed
                    dformat = greyed
#even rows are white background
                elif row%2 == 0:
                    gformat = wdefault
                    dformat = wdt
#otherwise use a slight grey background
                else:
                    gformat = gdefault
                    dformat = gdt
#if the student number is wrong use the red format
                if 'sr' in courseoutput[section][student]['metadata']:
                    workingsheet.write(row,0,student,red)
                else:
                    workingsheet.write(row,0,student,gformat)

                col = 1
                for cell in columnnames:
#if something is midly wrong about the phone number highlight in yellow
                    if cell == 'phone' and 'yp' in courseoutput[section][student]['metadata']:
                        workingsheet.write(row,col,courseoutput[section][student][cell],yellow)
#if something is very wrong about the phone number highlight in red
                    elif cell == 'phone' and 'rp' in courseoutput[section][student]['metadata']:
                        workingsheet.write(row,col,courseoutput[section][student][cell],red)
#otherwise use the predetermined format
                    elif cell != 'timestamp':
                        workingsheet.write(row,col,courseoutput[section][student][cell],gformat)
#timestamp uses a slight different format
                    else:
                        workingsheet.write(row,col,courseoutput[section][student][cell],dformat)
                    col += 1
                row += 1

#adjust the rows
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

#close the workbook
    workbook.close()
