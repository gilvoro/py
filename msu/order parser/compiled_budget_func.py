import pandas as pd
import xlsxwriter

#a function to make the hyperlink string to open the invoice on sharepoint
def invoicelink(year,vendor,invoice):
#if there no invoice we don't want a hyperlink
    if invoice == 'no invoice':
        link = 'no invoice'
    else:
#the static portions of the string
        spt1 = 'https://msudenver.sharepoint.com/sites/DepartmentofChemistry/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FDepartmentofChemistry%2FShared%20Documents%2FFinances%2Finvoices%2Ffiscal%20year%20'
        spt2 = '%2Epdf&parent=%2Fsites%2FDepartmentofChemistry%2FShared%20Documents%2FFinances%2Finvoices%2Ffiscal%20year%20'
#get the year month out of the invoice
        print(invoice)
        ym = invoice.split('_')[1].split('-')[0] + '%2D' + invoice.split('_')[1].split('-')[1]
#make the invoice into html code
        in1 = invoice.replace('_','%5F')
        in2 = in1.replace('-','%2D')
#any blanks in the name need to be replaced
        nsvendor = vendor.replace(' ','%20')
#make the link
        link = spt1+year+'%2F'+nsvendor+'%2F'+ym+'%2F'+in2+spt2+year+'%2F'+ vendor +'%2F' + ym

    return link

def workbookmkrcomplied(opname,baselist,df,year):
#ranges to for data validation
    ranges = {'funds':[],'payee':[],'category':[],'sub category':[],'endusers':[]}
#make the work book
    workbook = xlsxwriter.Workbook(opname)
#setup all the formats
    default = workbook.add_format({'bottom':2,'right':1,'right_color':'#d3d3d3'})
    center = workbook.add_format({'align':'center','bottom':2,'right':1,'right_color':'#d3d3d3'})
    dt = workbook.add_format({'num_format':'yyyy-mm-dd','align':'center','bottom':2,
                              'right':1,'right_color':'#d3d3d3'})
    usd = workbook.add_format({'num_format':'[$$-409]#,##0.00','align':'center','bottom':2,
                               'right':1,'right_color':'#d3d3d3'})
    lf = workbook.add_format({'font_color':'#0000EE','align':'center',
                              'bottom':2,'right':1,'right_color':'#d3d3d3'})
    f1 = workbook.add_format({'bg_color':'#ffffd4'})
    hf = workbook.add_format({'bg_color':'#d3d3d3','bold':True,'align':'center','bottom':2,'right':1})
#add the sheets
    reportsheet = workbook.add_worksheet('report')
    basesheet = workbook.add_worksheet('validation_data')
#make the base sheet to be used a validation data
#as strings are added flag the cell where we start a new list
    curset = 'none'
    bn = 0
    for item in baselist:
        if item in ranges.keys():
#displace the current count by two because excel index at one, additional because we don't want the label
            ranges[item].append(bn+2)
            if curset in ranges.keys():
#diplace the count by minus one because we don't want the blank.
                ranges[curset].append(bn-1)
#change the curset to the new list
            curset = item
#add the string to the sheet
        basesheet.write(bn,0,item)
        bn += 1
#finish the last list
    ranges[curset].append(bn)
#add the header to the reportsheet
    reportsheet.write_row(0,0,(df.columns),hf)
#add the data to the sheet based on the type of data, going column to column, then row to row
    row = 1
    for item in df.index:
        link = invoicelink(year,df['vendor'][item],df['invoice number'][item])
        col = 0
        for column in df.columns:
            cell = df[column][item]
            if cell in ['none listed','not received','no invoice']:
                reportsheet.write(row,col,cell,center)
            elif column in ['invoice number']:
                reportsheet.write_url(row,col,link,lf,string=cell)
            elif column in ['date of purchase','date of receipt']:
                reportsheet.write_datetime(row,col,cell,dt)
            elif column in ['description']:
                reportsheet.write(row,col,cell,default)
            elif column in ['cost']:
                reportsheet.write_number(row,col,cell,usd)
            else:
                reportsheet.write(row,col,cell,center)
            col += 1
        row += 1

#add some conditional formatting
    reportsheet.conditional_format(1,9,row-1,9,
                                   {'type':'cell','criteria':'==','value':'"not received"','format':f1})
#set up the validation data columns
    plist = '=validation_data!$A$'+str(ranges['payee'][0])+':$A$'+str(ranges['payee'][1])
    reportsheet.data_validation(1,4,row-1,4,{'validate':'list','source':plist})

    flist = '=validation_data!$A$'+str(ranges['funds'][0])+':$A$'+str(ranges['funds'][1])
    reportsheet.data_validation(1,5,row-1,5,{'validate':'list','source':flist})

    clist = '=validation_data!$A$'+str(ranges['category'][0])+':$A$'+str(ranges['category'][1])
    reportsheet.data_validation(1,6,row-1,6,{'validate':'list','source':clist})

    sclist = '=validation_data!$A$'+str(ranges['sub category'][0])+':$A$'+str(ranges['sub category'][1])
    reportsheet.data_validation(1,7,row-1,7,{'validate':'list','source':sclist})

    elist = '=validation_data!$A$'+str(ranges['endusers'][0])+':$A$'+str(ranges['endusers'][1])
    reportsheet.data_validation(1,8,row-1,8,{'validate':'list','source':elist})

#set the column widths
    for x in range(0,len(df.columns)):
        if x == 1:
            reportsheet.set_column(x,x,75)
        elif x == 2:
            reportsheet.set_column(x,x,20)
        elif x == 3:
            reportsheet.set_column(x,x,11)
        elif x == 5:
            reportsheet.set_column(x,x,23)
        elif x == 6:
            reportsheet.set_column(x,x,20)
        elif x == 7:
            reportsheet.set_column(x,x,25)
        elif x == 10:
            reportsheet.set_column(x,x,50)
        else:
            reportsheet.set_column(x,x,15)

#freeze the top row
    reportsheet.freeze_panes(1,0)
    workbook.close()
