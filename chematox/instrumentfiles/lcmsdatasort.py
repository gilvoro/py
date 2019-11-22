import csv

#a function which takes data from Water's Target Lynx and converts
#it into a dictionary for use by other scripts


def lcmsdatasort(filename):
    sorted_data = {}
    with open (filename, 'rU') as csvfile:
        unsorted_data = csv.reader(csvfile, delimiter='\t')
#go row by row of the raw data
        for row in unsorted_data:
#pass by row that have no fields in them
            if len(row) < 1:
                pass
#if the line starts with Compound set compound name
#to whatever comes after the colon
            elif row[0].startswith('Compound'):
                compoundname = row[0].split(':')[1].strip()
                sorted_data.setdefault(compoundname, {})
#now we can by pass any line that only has one field
            elif len(row) < 2:
                pass
#whatever information is displayed on column names becomes a key list later
            elif row[0] == '' and row[1] != '':
                columnkeys = row[1:]
#if the row has sample information then we start building the dictionary
            elif row[0] != '' and row[1] != '':
                x = 0
                sorted_data[compoundname].setdefault(row[0],{})
                while x < len(row):
                    if x == 0:
                        x += 1
                        pass
                    else:
                        sorted_data[compoundname][row[0]][columnkeys[x-1]]=row[x]
                        x += 1

            else:
                pass

    return sorted_data
