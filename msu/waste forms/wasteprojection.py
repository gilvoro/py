import csv
import os


def projection(baseloc):
    projdict = {}
#go through each coruse and added it to the dictionary
    for course in os.listdir(baseloc):
#skip the additional waste folder
        if course == 'additional waste' or course == 'knonw waste stream' or course == 'base additional waste':
            pass
        else:
#add it to the dictionary, then set that as the working dictionary
            projdict.setdefault(course,{})
            coursedict = projdict[course]
#go for through each lab file in the course folder
            for lab in os.listdir(os.path.join(baseloc,course)):
#add to the course dictionary and then set that as the working dictionary
                coursedict.setdefault(lab.strip(),{})
                labdict = coursedict[lab.strip()]
#go through the data file...
                with open(os.path.join(os.path.join(baseloc,course),lab), newline = '') as csvfile:
                    unsorted_data = csv.reader(csvfile, delimiter = ',')
                    for row in unsorted_data:
#...skip any random row that is less then four....
                        if len(row) < 4:
                            pass
#...skip metadata rows, also have to strip ws from 'updated: because I have several files that have a space after them...'
                        elif row[2] == 'updated:' or row[0] == 'stream':
                            pass
#otherwise add it by stream, then generation rate, then chemical and finally volume
                        else:
                            labdict.setdefault(row[0].lower().strip(),{})
                            labdict[row[0].lower().strip()].setdefault(row[1].lower().strip(),{})
                            labdict[row[0].lower().strip()][row[1].lower().strip()][row[2].lower().strip()] = row[3].lower().strip()

    return(projdict)
