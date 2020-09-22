# A program to take qualtrics safety agreement data and banner software, process them
# and return spreadsheets of student responses by section and lists by instructors of students
# who have failed to complete the survey

# import required libraries
import csv
import datetime
import logging
import os

# uses all the functions from in the helper script
from sa_func import *

# header for the student lists so that it is a copy and paste email
nr = 'The following is a list of students that have yet to complete their Lab Safety Agreement. Please have these students fill out the safety agreement if they are still attending. If they are not attending the class anymore please let me know.\n'

# salution dictionary for those instructors that are not doctors
sdict = {'Miller': 'Mr. ', 'Smiley': 'Mr. '}

# get timestampe and start the logger
ts = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H%M%S')

slloc = os.path.join(
    'c:\\Users\\jlaughl6\\User Assets\\script files\\script_logs', 'sa_log_' + ts + '.log')

logging.basicConfig(filename=slloc,
                    format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)
logging.info('logging started')

# get the term we are dealing with
term = input('What Term (season-YYYY)?: ')
logging.info(term)

# setup all the locations needed, tlc = term crn list, tsw = term student workers, tsr = term student replacement
# tbf = term banner files, tsd = term survey data, tsf = term sharepoint files, tnp = term no response
baseloc = 'c:\\Users\\jlaughl6\\User Assets\\script files\\safety_agreement\\'
tclloc = os.path.join(os.path.join(os.path.join(baseloc, 'script_files'), term), 'crn_list.csv')
tswloc = os.path.join(os.path.join(os.path.join(baseloc, 'script_files'), term), 'student_workers.csv')
tsrloc = os.path.join(os.path.join(os.path.join(baseloc, 'script_files'), term), 'student_replacement.csv')
tbfloc = os.path.join(os.path.join(baseloc, 'banner_files'), term)
tsdloc = os.path.join(os.path.join(baseloc, 'survey_data'), term)
tsfloc = os.path.join(os.path.join(baseloc, 'sharepoint_files'), term)
tnploc = os.path.join(os.path.join(baseloc, 'no_response'), term)

# esid is the a list that contains the expected studient ids
esid = []
# get the crn into a dictionary
crndict = crn_parser(tclloc,tswloc,esid)
logging.info('Retrived the CRNs.')

# process the banner files updating the expect student id list and crn dictionary, and producing the withdraw dictionary
withdrawndict = banner_parser(tbfloc, crndict, esid)
logging.info('Processsed the banner files.')

# process the survey data to get a list of student reponses.
# If students have done the survey multiple times the newer enteries replace the older ones
studentdict = survey_parser(tsdloc)
logging.info('Processed survey data.')

# go through the and replace the enteries in the
# student dictionary that are found in teh student replacment file
student_replacer(tsrloc, studentdict)
logging.info('Students replaced.')

# go through the crn dictionary and update the student info with that found in
# the student dictionary
merger(studentdict, crndict, esid)
logging.info('Student information added to CRNs.')

# go through the crn dictionary, added data by course to outputdict and instructor
# to noresponsedict.
outputdict = {}
noresponsedict = {}
for crn in crndict:
    outputdict.setdefault(crndict[crn]['course'], {})
    noresponsedict.setdefault(crndict[crn]['instructor'], {})
#add the entiry of students of a section to the output dictionary by course/secion
    outputdict[crndict[crn]['course']][crndict[crn]['desc']] = crndict[crn]['students']
#add the course + section to the no response dictionary
    noresponsedict[crndict[crn]['instructor']][crndict[crn]['course'] + '_' + crndict[crn]['section']] = []
    studentlist = noresponsedict[crndict[crn]['instructor']][crndict[crn]['course'] + '_' + crndict[crn]['section']]
#if the student has not completed the survey add them to the no response dictionary
    for student in crndict[crn]['students']:
        if crndict[crn]['students'][student]['timestamp'] == 'not completed' and not (student in withdrawndict and crndict[crn]['course'] in withdrawndict[student]):
            studentlist.append(crndict[crn]['students'][student]['name'])
logging.info('Generated output dictionary and no response dictionary.')

#go through the output dictionary by course and generate needed spreadsheets
for course in sorted(outputdict.keys()):
    coursename = course + '.xlsx'
    opname = os.path.join(tsfloc, coursename)
    workbookmrk(opname, outputdict[course],course,withdrawndict)
logging.info('Spreadsheets made.')

#go through the no response dictionary and generate the form letters
for instructor in noresponsedict:
    if instructor == '':
        pass
    else:
        filename = instructor + '.txt'
        opname = os.path.join(tnploc, filename)
#make sure we use the rigth title
        if instructor in sdict.keys():
            saluation = sdict[instructor]
        else:
            saluation = 'Dr. '

#start the list used to generate the text file 
        oplist = [saluation + instructor + '\n', nr]

#add each course followed by section followed by students to the list
        for course in noresponsedict[instructor]:
            oplist.append('\n')
            oplist.append(course + '\n')
            if noresponsedict[instructor][course]:
                for student in noresponsedict[instructor][course]:
                    oplist.append('\t' + student + '\n')
#just to make sure the course has been missed
            else:
                oplist.append('\tnone\n')
#make the needed txt files 
    opfile = open(opname, 'w')
    opfile.writelines(oplist)
    opfile.close()
logging.info('Text files made.')

#open the sharepoint file directory
os.startfile(tsfloc)
