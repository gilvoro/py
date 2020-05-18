import csv
import datetime
import pandas as pd
import os
import xlsxwriter

from compiled_budget_func import workbookmkrcomplied

#get datetime and make a timestamp
now = datetime.datetime.now()
ts = datetime.datetime.strftime(now,'%Y-%m-%d_%H%M%S')

#figure out which fiscal year we are in
if now.month in [1,2,3,4,5,6]:
    fy = 'fy'+str(now.year)
    year = str(now.year)
else:
    fy = 'fy'+str(mow.year + 1)
    year = str(now.year + 1)

#file locations
rloc = 'c:\\Users\\jlaughl6\\User Assets\\script files\\budget\\for_script\\base.csv'
dloc = os.path.join('c:\\Users\\jlaughl6\\User Assets\\script files\\budget',fy)
nploc = os.path.join(dloc,'database\\not_posted_db')
pfloc = os.path.join(dloc,'processed_reports')
opname = os.path.join(dloc,'compiled_reports\\budget report ' + fy + ' as of ' + ts + '.xlsx')

#make a blank data frame
df =  pd.DataFrame()

#for every file in the fiscal year processed_reports add that data to the dataframe
for file in os.listdir(pfloc):
    if file.endswith('-processed.xlsx'):
#get the purchase method based on the filename
        method = file.split('-')[4]
        tempdf = pd.read_excel(os.path.join(pfloc,file),
                               sheet_name = 'report')
        tempdf['method'] = method
        df = pd.concat([df,tempdf],ignore_index = True)
#for ease of processing put everything into lowercase
        for header in ['description','vendor','payee','fund','category','sub category','end user','method']:
            df[header] = df[header].str.lower()
    else:
        print(file + ' not processed')
        pass

#get those line items that have not posted
npdf = df[(df['posted'] == 'no')]
#drop the line items that have not posted
df = df[(df['posted'] == 'yes')]
#drop the posted column
df = df.drop(columns = ['posted'])
#sort and re-index the datafram
df.sort_values(by = ['date of purchase', 'method','vendor','invoice number'])
df.reset_index(drop=True, inplace = True)

#get the validation date list
baselist = []
with open(rloc, newline ='') as csvfile:
    data = csv.reader(csvfile, delimiter = ',')
    for row in data:
        try:
            baselist.append(row[0])
        except(IndexError):
            baselist.append('')

#make the excel sheet for the compiled budget
workbookmkrcomplied(opname,baselist,df,year)

npdf.to_excel(os.path.join(nploc,'not_posted_' + ts +'.xlsx'))
