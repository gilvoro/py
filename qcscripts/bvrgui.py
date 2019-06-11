import datetime
import psycopg2
import psycopg2.extensions
from pubsub import pub
import wx
import wx.adv
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
#define a checklist box
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
                wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
#define the base panel for the maingui
class basepanel(wx.Panel):
    def __init__(self, parent, date, samplelist):
        wx.Panel.__init__(self,parent)
#define the parent for later reference
        self.parent = self.GetParent()

#display elements that will not change
        headerlab = wx.StaticText(self, label="BAC validations for the week of",
                                  style=wx.ALIGN_CENTRE_HORIZONTAL)
        samplenumlab = wx.StaticText(self,label="ChemaTox Numbers",
                                     style=wx.ALIGN_CENTRE_HORIZONTAL)
        runcvlab = wx.StaticText(self, label="Summary .CSV", style=wx.ALIGN_CENTRE_HORIZONTAL)
#display elemetns that will be updated
        self.datelab = wx.StaticText(self, label=date)
        self.summarytc = wx.TextCtrl(self, value = '', size = (145,-1), style = wx.TE_READONLY)
#define the checkbox windows to two columns one for checkboxes and one for CT numbers
        self.checkbox = CheckListCtrl(self)
        self.checkbox.InsertColumn(0,'', width = 20)
        self.checkbox.InsertColumn(1,'ChemaTox Numbers', width = 125)
#go through the inital sample list and populate the check box
        index = 0
        for item in samplelist:
            self.checkbox.InsertItem(index,'')
            self.checkbox.SetItem(index,1,str(item))
            self.checkbox.CheckItem(index)
            index +=1
#define the buttons
        changedate = wx.Button(self, label = 'Change Date')
#built in widget for a file selection window
        self.summaryfp = wx.FilePickerCtrl(self,message = 'Select summary file',
                                           wildcard = "CSV Files (*.csv)|*.csv",
                                           size = (100,25),
                                           style = wx.FLP_OPEN |wx.FLP_FILE_MUST_EXIST)
#more buttons, order the widgets such that tabbing through them behaves as suspected
        selectall = wx.Button(self, label = 'Select All', size = (100,25))
        deselectall = wx.Button(self, label = 'Deselect All', size = (100,25))
        confirmbutton = wx.Button(self, label = 'Confirm', size = (100,25))
        cancelbutton = wx.Button(self, label = 'Cancel', size = (100,25))
#simple line
        tline = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
#boxes to group the file selection and confirm/cancel
        sbox1 = wx.StaticBox(self)
        sbox2 = wx.StaticBox(self, size = (260,-1))
        sboxsizer1 = wx.StaticBoxSizer(sbox1, wx.VERTICAL)
        sboxsizer2 = wx.StaticBoxSizer(sbox2, wx.HORIZONTAL)
#more sizers.
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vboxL = wx.BoxSizer(wx.VERTICAL)
        vboxR = wx.BoxSizer(wx.VERTICAL)
        vboxt = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
#build the header
        vboxt.Add(headerlab, flag = wx.ALIGN_CENTER|wx.EXPAND|wx.LEFT|wx.RIGHT,
                   border = 10)
        vboxt.Add(self.datelab, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5)
        vboxt.Add(changedate, flag = wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT,
                   border = 5)
#build the file selection area
        sboxsizer1.Add(runcvlab, flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,
                   border = 10)
        sboxsizer1.Add(self.summarytc, flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM,
                   border = 10)
        sboxsizer1.Add(self.summaryfp, flag = wx.EXPAND)
#build the left side area
        vboxL.Add(sboxsizer1, flag = wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.RIGHT,
                   border = 10)
        vboxL.Add(selectall,flag = wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.RIGHT,
                   border = 10)
        vboxL.Add(deselectall, flag = wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM,
                   border = 10)
#build the right side area
        vboxR.Add(samplenumlab, flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,
                   border = 10)
        vboxR.Add(self.checkbox, flag = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,
                   border = 10)
#build the middle area
        hbox1.Add(vboxL)
        hbox1.Add(vboxR)
#build bottom area
        sboxsizer2.AddSpacer(20)
        sboxsizer2.Add(confirmbutton, flag = wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM,
                       border = 10)
        sboxsizer2.AddSpacer(20)
        sboxsizer2.Add(cancelbutton,flag=wx.ALIGN_RIGHT|wx.TOP|wx.BOTTOM,
                       border = 10)
#build the panel
        vbox1.Add(vboxt, flag = wx.ALIGN_CENTER)
        vbox1.AddSpacer(10)
        vbox1.Add(tline, flag = wx.EXPAND)
        vbox1.Add(hbox1)
        vbox1.Add(sboxsizer2, flag = wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border = 10)
        self.SetSizer(vbox1)

#bind all the functions
        changedate.Bind(wx.EVT_BUTTON,self.datechoose)
        self.summaryfp.Bind(wx.EVT_FILEPICKER_CHANGED,self.runfilechoose)
        selectall.Bind(wx.EVT_BUTTON,self.selectallfunc)
        deselectall.Bind(wx.EVT_BUTTON,self.deselectallfunc)
        confirmbutton.Bind(wx.EVT_BUTTON,parent.confirm)
        cancelbutton.Bind(wx.EVT_BUTTON,parent.cancel)
#pop-up the date selection frame/panel
    def datechoose(self,event):
        datewindow = dateframe(parent = wx.GetTopLevelParent(self), pos = self.GetScreenPosition(), date = datetime.datetime.strptime(self.datelab.GetLabel(),'%Y-%m-%d'))
#when a new file is selected update the display and output varible
    def runfilechoose(self,event):
        self.summarytc.SetValue(self.summaryfp.GetPath())
        self.parent.summaryfile = self.summaryfp.GetPath()
#select all the checkboxes
    def selectallfunc(self,event):
        num = self.checkbox.GetItemCount()
        for i in range(num):
            self.checkbox.CheckItem(i, True)
#deselect all the checkboxes
    def deselectallfunc(self,event):
        num = self.checkbox.GetItemCount()
        for i in range(num):
            self.checkbox.CheckItem(i, False)
#date panel class
class datepanel(wx.Panel):
    def __init__(self, parent,date):
        wx.Panel.__init__(self,parent)
#define the parent for later reference
        self.parent = self.GetParent()
#define all the widgets
        self.datepicker = wx.adv.CalendarCtrl(self, date=date)
        self.seldate = wx.StaticText(self, label = 'Selected Date: ' + date.strftime('%Y-%m-%d'))
        exitbutton = wx.Button(self, label = 'Cancel', size = (100,25))
        okbutton = wx.Button(self, label = 'Ok', size = (100,25))
#build the layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
#build the bottom area
        hbox.AddSpacer(10)
        hbox.Add(okbutton)
        hbox.AddSpacer(15)
        hbox.Add(exitbutton)
#build the top portion
        vbox.AddSpacer(5)
        vbox.Add(self.seldate, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5)
        vbox.AddSpacer(5)
        vbox.Add(self.datepicker, flag = wx.EXPAND|wx.LEFT|wx.RIGHT, border = 5)
        vbox.AddSpacer(5)
        vbox.Add(hbox)
        self.SetSizer(vbox)
#bind all the functions
        okbutton.Bind(wx.EVT_BUTTON,parent.confirm)
        exitbutton.Bind(wx.EVT_BUTTON,parent.closewindow)
        self.datepicker.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED,self.newdate)
#when we select a new date update the datepicker widget so it hightlights the correct date,
#update the top label so it displays the correct date, and update the dateframe date varible
    def newdate(self,event):
        rawdate = event.GetDate()
        self.datepicker.SetDate(rawdate)
        self.seldate.SetLabel('Selected Date: ' + rawdate.Format('%Y-%m-%d'))
        self.parent.date = rawdate.Format('%Y-%m-%d')
#dateframe class
class dateframe(wx.Frame):
    def __init__(self,parent,pos,date):
#define the date to report back to the baseframe
        self.date = date.strftime('%Y-%m-%d')
        wx.Frame.__init__(self, parent=parent, title = "Date Window", pos = pos,
                          style = wx.CAPTION | wx.CLOSE_BOX)
#call the datepanel
        panel = datepanel(self,date)
        self.SetSize((240,250))
        self.Show()
#close the frame without updating anything
    def closewindow(self,event):
        self.Close(True)
#close the window with sending a message about update the date.
    def confirm(self,event):
        pub.sendMessage('date_select', dateupdate = self.date)
        self.Close(True)
#baseframe class
class baseframe(wx.Frame):
    def __init__(self, *args, **kw):
        super(baseframe, self).__init__(*args, **kw)
        self.Centre()
#Create a status bar which should update things if the LIMS is slow.
        self.sb = self.CreateStatusBar()
        self.Show(True)
        pub.subscribe(self.sbupdate, 'sb_update')
#get the dates need to get the samples based on day of date
        self.startofweek, self.begindate, self.enddate, self.datetext = dates(datetime.date.today())
#get the samples list and data from teh lims
        self.samples, self.data = dbq(self.begindate, self.enddate)
#set output varibles and some other parameters
        self.opsamples = []
        self.summaryfile = ''
        self.SetSize((380,410))
        self.SetTitle('BAC validation report')
        self.SetWindowStyleFlag(wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
#start the panel
        self.panel = basepanel(self,self.datetext,self.samples)
#listen for updates on the date
        pub.subscribe(self.dateupdate, "date_select")
#when the date changes update the necessary varibles and displays
    def dateupdate(self, dateupdate):
#get the new start of the week
        self.startofweek, self.begindate, self.enddate, self.datetext = dates(datetime.datetime.strptime(dateupdate,'%Y-%m-%d').date())
#update the static text
        self.panel.datelab.SetLabel(self.datetext)
#get the samples and data associated with the new dates and update the checkbox.
        self.samples, self.data = dbq(self.begindate, self.enddate)
        self.panel.checkbox.DeleteAllItems()
        index = 0
        for item in self.samples:
            self.panel.checkbox.InsertItem(index,'')
            self.panel.checkbox.SetItem(index,1,str(item))
            self.panel.checkbox.CheckItem(index)
            index +=1
#hopefully update the status bar.
    def sbupdate(self, status):
        self.sb.SetStatusText(status)
#close the windows without doing anything of interest
    def cancel(self,event):
        self.Close(True)
#see what samples are selected and update the output list
    def confirm(self, event):
        selectedsamples = []
        num = self.panel.checkbox.GetItemCount()
        for i in range(num):
            if self.panel.checkbox.IsChecked(i):
                selectedsamples.append(self.panel.checkbox.GetItemText(i, col = 1))
        self.opsamples = selectedsamples
        self.Close(True)
#define the maingui function, the returns maybe moved to the confirm button.
def maingui():
    fwin = wx.App()
    a = baseframe(None)
    fwin.MainLoop()
    return a.opsamples, a.data, a.summaryfile, a.startofweek
#given any date find the modnay of that week, the wednesday of the previous week and following sunday.
def dates(givendate):
    mondaydate = givendate + datetime.timedelta(days = -givendate.weekday())
    beforedate = mondaydate - datetime.timedelta(days = 5)
    afterdate = mondaydate + datetime.timedelta(days = 6)
    textmondaydate = mondaydate.strftime('%Y-%m-%d')
    return mondaydate, beforedate, afterdate, textmondaydate
#get the data out of the lims
def dbq(firstdate, seconddate):
#from jkominek/chematox/display.py
#update the status bar
    pub.sendMessage('sb_update', status = 'Connecting to LIMS')
#connect to the database
    conn = psycopg2.connect("host=lims-db.chematox.com dbname=chematox user=reader password=immunoassay")
    c = conn.cursor()
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, c)
    c.execute("set application_name = 'bac validation report'")
    conn.commit()
#update the status bar
    pub.sendMessage('sb_update', status = 'Collecting ChemaTox Numbers')
#this query gets those samples that have had a new request made against them in the given time period and the request was made by CT Validations.
    c.execute("""select ss.id from entities e, requests r, request_history rh, samplesets ss where rh.stamp between %s and %s and rh.action = 'I' and r.id = rh.key and r.requestor = e.id and e.name = 'ChemaTox Validation - Forensic' and r.sample_set = ss.id""",(firstdate, seconddate))
#toss them ct numbers into a list
    samplelist= []
    for sampleset in c:
        samplelist.append(sampleset[0])
#update the status bar
    pub.sendMessage('sb_update', status = 'Collecting Previous Results')
#go through and get all the alcohol results for the samples.
    limsdata = {}
    for sampleset in samplelist:
        c.execute("""select t.testdate, t.result from samplesets ss, samples s, tests t where ss.id = %s and s.sample_set = ss.id and t.sample = s.id and t.type = 393""",(sampleset,))
#put those results into a dict
        for date, result in c:
            limsdata.setdefault(sampleset,{})
            limsdata[sampleset][date] = result
#remember to close the connection
    conn.close()
#update the status bar and return the list and dict
    pub.sendMessage('sb_update', status = 'Task Complete')
    return samplelist, limsdata

#this is subject to change and move to a different script
# today = datetime.date.today()
# if __name__ == '__main__':
#      sampleslist, limsdata, summaryfile, weekofdate = maingui()
