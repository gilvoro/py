import wx
import wx.adv
import datetime
import re
import os
from pubsub import pub
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

matrixlist = ['Blood','Urine','Plasma']
inilist = ['JRL','RLA','CKE','KCP','LMW']
today = datetime.datetime.today()
defaultdir = os.path.normpath('F:/firefly/Programs/pve/gui/files')
inival = ''
matrixval = ''
selecteddate = ''

def filesearch(fqc):
    isfqc = re.compile('fqc-\d\d\d\d\d?')
    isvalidnum = re.compile('fqc-\d\d\d\d\d?')
    fqctrue = False
    if fqc.lower().startswith('fqc'):
        fqctrue = re.match(isfqc,fqc.lower())
        newfqc = fqc.lower()
    else:
        fqctrue = re.match(isvalidnum,fqc)
        newfqc = 'fqc-' + fqc
    return fqctrue, newfqc

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
                wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class basepanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self,parent)

        datelab = wx.StaticText(self, label='Date Of Run (YYYY-MM-DD)',style=wx.ALIGN_CENTRE_HORIZONTAL)
        inilab = wx.StaticText(self, label='Tech Initals',style=wx.ALIGN_CENTRE_HORIZONTAL)
        matrixlab = wx.StaticText(self, label='Matrix',style=wx.ALIGN_CENTRE_HORIZONTAL)
        runfilelab = wx.StaticText(self, label='Run List .CSV',style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.datetext = wx.TextCtrl(self, value = today.strftime('%Y-%m-%d'), style=wx.TE_CENTRE)
        datechoosebutton = wx.Button(self, label = 'Choose Date')
        self.matrixcb = wx.ComboBox(self, choices=matrixlist,style=wx.CB_READONLY)
        self.inicb = wx.ComboBox(self, choices=inilist,style=wx.CB_READONLY)
        self.runfiletc = wx.TextCtrl(self, value = '', style = wx.TE_READONLY)
        self.runfile = wx.FilePickerCtrl(self,message = 'Select a run last as a .CSV file',
                                         wildcard = "CSV Files (*.csv)|*.csv",
                                         style = wx.FLP_OPEN |wx.FLP_FILE_MUST_EXIST)
        filelistlab = wx.StaticText(self, label = 'Plate Directory',style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.filelisttc = wx.StaticText(self,label = defaultdir)
        self.filelistdir = wx.DirPickerCtrl(self,style=wx.DIRP_DIR_MUST_EXIST)
        self.filelistdir.SetInitialDirectory(defaultdir)
        checkboxlab = wx.StaticText(self, label = 'Enter FQC Number', style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.checkboxtc = wx.TextCtrl(self, value = '', style=wx.TE_CENTRE|wx.TE_PROCESS_ENTER)
        self.checkbox = CheckListCtrl(self)
        self.checkbox.InsertColumn(0,'', width = 20)
        self.checkbox.InsertColumn(1,'Files')
        selectall = wx.Button(self, label = 'Select All')
        deselectall = wx.Button(self, label = 'Deselect All')
        confirmbutton = wx.Button(self, label = 'Confirm', size = (100,25))
        cancelbutton = wx.Button(self, label = 'Cancel', size = (100,25))

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        lsizer = wx.GridBagSizer(5,5)
        lsizer.Add(datelab, pos = (0,0), span=(1,2), flag = wx.ALIGN_CENTER|wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,
                  border= 10)
        lsizer.Add(self.datetext, pos = (1,0), span=(1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(datechoosebutton, pos = (2,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(matrixlab, pos = (3,0), span = (1,1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT,border = 10)
        lsizer.Add(self.matrixcb, pos = (4,0), span = (1,1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(inilab, pos = (3,1), span = (1,1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(self.inicb, pos = (4,1), span = (1,1), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(runfilelab,pos = (5,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(self.runfiletc,pos = (6,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(self.runfile, pos = (7,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(filelistlab, pos = (8,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(self.filelisttc, pos = (9,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        lsizer.Add(self.filelistdir, pos = (10,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)

        rsizer = wx.GridBagSizer(5,5)
        rsizer.Add(checkboxlab, pos = (0,0), span = (1,2), flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,
                   border = 10)
        rsizer.Add(self.checkboxtc, pos = (1,0), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        rsizer.Add(self.checkbox, pos = (2,0,), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        rsizer.Add(selectall, pos = (3,0,), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)
        rsizer.Add(deselectall, pos = (4,0,), span = (1,2), flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 10)

        hbox2.AddSpacer(40)
        hbox2.Add(confirmbutton)
        hbox2.AddSpacer(45)
        hbox2.Add(cancelbutton)
        hbox2.AddSpacer(40)

        hbox1.Add(lsizer)
        hbox1.Add(rsizer)
        vbox1.Add(hbox1)
        vbox1.AddSpacer(10)
        vbox1.Add(hbox2)
        self.SetSizer(vbox1)

        datechoosebutton.Bind(wx.EVT_BUTTON,self.datechoose)
        self.runfile.Bind(wx.EVT_FILEPICKER_CHANGED,self.runfilechoose)
        self.filelistdir.Bind(wx.EVT_DIRPICKER_CHANGED,self.dirchoose)
        self.checkboxtc.Bind(wx.EVT_TEXT_ENTER,self.fqcenter)
        selectall.Bind(wx.EVT_BUTTON,self.selectallfunc)
        deselectall.Bind(wx.EVT_BUTTON,self.deselectallfunc)
        confirmbutton.Bind(wx.EVT_BUTTON,self.confirm)
        cancelbutton.Bind(wx.EVT_BUTTON,parent.cancel)

        pub.subscribe(self.dateupdate, "date_select")

    def dateupdate(self, dateupdate):
        self.datetext.SetValue(dateupdate)

    def datechoose(self,event):
        selecteddate = self.datetext.GetValue()
        datewindow = dateframe(parent = wx.GetTopLevelParent(self), pos = self.GetScreenPosition(), date = datetime.datetime.strptime(self.datetext.GetValue(),'%Y-%m-%d'))
        pub.sendMessage('date_select', dateupdate = selecteddate)

    def runfilechoose(self,event):
        self.runfiletc.SetValue(self.runfile.GetPath())

    def dirchoose(self,event):
        self.filelisttc.SetLabel(self.filelistdir.GetPath())

    def fqcenter(self,event):
        fqctrue, fqc = filesearch(self.checkboxtc.GetValue())
        if fqctrue:
            self.checkbox.DeleteAllItems()
            index = 0
            workdir = os.path.normpath(self.filelisttc.GetLabel())
            for item in os.listdir(workdir):
                if item.lower().startswith(fqc):
                    if item.lower().endswith('.csv'):
                        self.checkbox.InsertItem(index,'')
                        self.checkbox.SetItem(index,1,item)
                        self.checkbox.CheckItem(index)
                        index += 1

        else:
            self.checkboxtc.Clear()
            self.checkbox.DeleteAllItems()

    def selectallfunc(self,event):
        num = self.checkbox.GetItemCount()
        for i in range(num):
            self.checkbox.CheckItem(i, True)

    def deselectallfunc(self,event):
        num = self.checkbox.GetItemCount()
        for i in range(num):
            self.checkbox.CheckItem(i, False)

    def confirm(self,event):
        #some check for isodate
        rundate = datetime.datetime.strptime(self.datetext.GetValue(),'%Y-%m-%d')
        runmatrix = self.matrixcb.GetValue()
        runtech = self.inicb.GetValue()
        runlist = self.runfiletc.GetValue()
        fileloc = self.filelisttc.GetLabel()
        filelist = []
        num = self.checkbox.GetItemCount()
        for i in range(num):
            if self.checkbox.IsChecked(i):
                filelist.append(self.checkbox.GetItemText(i, col = 1))
        foroutput = [rundate,runtech,runmatrix,fileloc,filelist,runlist]
        print foroutput
        pub.sendMessage('output_update', outputdata = foroutput)

class datepanel(wx.Panel):
    def __init__(self, parent,date):
        wx.Panel.__init__(self,parent)
        self.date = date
        self.datepicker = wx.adv.CalendarCtrl(self, date=self.date)
        self.seldate = wx.StaticText(self, label = 'Selected Date: ' + self.date.strftime('%Y-%m-%d'),
                                     style=wx.ALIGN_CENTRE_HORIZONTAL)
        exitbutton = wx.Button(self, label = 'Cancel', size = (100,25))
        okbutton = wx.Button(self, label = 'Ok', size = (100,25))

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        hbox.AddSpacer(10)
        hbox.Add(okbutton)
        hbox.AddSpacer(15)
        hbox.Add(exitbutton)

        vbox.AddSpacer(5)
        vbox.Add(self.seldate, flag = wx.EXPAND)
        vbox.AddSpacer(5)
        vbox.Add(self.datepicker, flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 5)
        vbox.AddSpacer(5)
        vbox.Add(hbox)

        self.SetSizer(vbox)

        okbutton.Bind(wx.EVT_BUTTON,parent.confirm)
        exitbutton.Bind(wx.EVT_BUTTON,parent.closewindow)
        self.datepicker.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED,self.newdate)

    def newdate(self,event):
        rawdate = event.GetDate()
        self.datepicker.SetDate(rawdate)
        self.seldate.SetLabel('Selected Date: ' + rawdate.FormatISODate())
        pub.sendMessage('date_select', dateupdate = rawdate.FormatISODate())


class dateframe(wx.Frame):
    def __init__(self,parent,pos,date):
        self.date = date.strftime('%Y-%m-%d')
        wx.Frame.__init__(self, parent=parent, title = "Date Window", pos = pos,
                          style = wx.CAPTION | wx.CLOSE_BOX)
        panel = datepanel(self,date)
        self.SetSize((240,240))
        self.Show()


    def closewindow(self,event):
        pub.sendMessage('date_select', dateupdate = self.date)
        self.Close(True)

    def confirm(self,event):
        self.Close(True)

#class conframe(wx.Frame):
    #def __init__(self,parent,date,initials,matrix,fileloc,filelist,runlist)

class baseframe(wx.Frame):

    def __init__(self, *args, **kw):
        self.date = 'none'
        self.initials = 'none'
        self.matrix = 'none'
        self.fileloc = 'none'
        self.filelist = 'none'
        self.runlist = 'none'
        super(baseframe, self).__init__(*args, **kw)
        self.SetSize((335,390))
        self.SetTitle('ELISA Report Generator')
        panel = basepanel(self)
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText('ELISA Report Generator')
        self.Centre()
        self.Show(True)

        pub.subscribe(self.output, "output_update")

    def cancel(self,event):
        self.Close(True)

    def output(self,outputdata):
        self.date = outputdata[0]
        self.initials = outputdata[1]
        self.matrix = outputdata[2]
        self.fileloc = outputdata[3]
        self.filelist = outputdata[4]
        self.runlist = outputdata[5]

def maingui():
    fwin = wx.App()
    a = baseframe(None)
    fwin.MainLoop()
    return a.date, a.initials, a.matrix,a.fileloc, a.filelist, a.runlist

if __name__ == '__main__':
    selecteddate, initials, matrix, fileloc, filelist, runlist = maingui()

print selecteddate, initials, matrix, fileloc, filelist, runlist
