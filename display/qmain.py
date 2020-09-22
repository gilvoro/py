import datetime
import sys

from tkinter import *
from tkinter import ttk
from tkinter import font

from qfunc import *
from qdisplay import *

#fileloc and associated csv files
dirloc = '/home/pi/Desktop/quotes'

#make the dictionary to keep time records
tidict ={'tomorrow':datetime.datetime.now().date(),
        'nextchange':datetime.datetime.now().time(),
        'rsb':datetime.datetime.strptime('00:00','%H:%M').time(),
        'rse':datetime.datetime.strptime('00:05','%H:%M').time(),
        'spd':{}}

#kill the main window of the display with a keystroke
def quit(*args):
  root.destroy()
  sys.exit()

#because after is funny a function to call other functions
def checker():
#get the datetime object, then extract the date and time
    now = datetime.datetime.now()
    date = now.date()
    time = now.time()
    print(date,time,tidict['nextchange'])
#first check to see if its a special day
    if now in tidict['spd'].keys():
        print('special day, waiting on code')
#if we have changed days refresh everything
    elif date >= tidict['tomorrow']:
        print('day change')
#get new quotes and change the text
        tqdict = qchooser(qdict)
        textchange(carddict,qdict,tqdict)
#put up the first card
        carddict[pdict['poslist'][0]]['card'].tkraise()
#update the tomorrow and next change
        tidict['tomorrow'] = (datetime.datetime.now()+datetime.timedelta(days=1)).date()
        tidict['nextchange'] = (datetime.datetime.now()+datetime.timedelta(minutes=15)).time()
#update the nextcard variable to one since we are currently displaying zero
        pdict['nextcard'] = 1
    elif tidict['nextchange'] > time >= tidict['rse']:
        print('greater then rse, less then nextchange')
    elif tidict['rse'] > time >= tidict['rsb']:
         print('crazy message display')
    elif time >= tidict['nextchange']:
        print('change card')
        carddict[pdict['poslist'][pdict['nextcard']]]['card'].tkraise()
        pdict['nextcard'] += 1
        if pdict['nextcard'] >= len(carddict.keys()):
            pdict['nextcard'] = 0
        tidict['nextchange'] = (datetime.datetime.now()+datetime.timedelta(minutes=15)).time()
    root.after(60000,checker)

#make qdict
qdict = qdictbuilder(dirloc)
pdict = {'poslist':list(qdict.keys()),'nextcard':0}

#make the root window, bind keys and make if fullscreen
root = Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')
root.bind("<Escape>", quit)
root.bind("x", quit)

#make a card for each display item
carddict = {}
for item in qdict.keys():
    carddict[item] = cardmaker(item,qdict[item]['type'],root)

root.after(0,checker)

root.mainloop()
