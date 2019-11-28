from tkinter import *
from tkinter import ttk
from tkinter import font

# def quit(*args):
# 	root.destroy()

#to quickly make all the frames we need for the display
def framemaker(title,type,parent,fc = 'black',bc = 'white'):
    typedict={'quote':['-mainframe','-holder','-messagebox','-signbox','-orginbox',
                      '-msg','-ph1','-ph2','-sign','-org',
                      '-phtxt','-msgtxt','-signtxt','-orgtxt'],
             'fallacy':['-mainframe','-title','-msg','-titletxt','-msgtxt'],
             'message':['-mainframe','-msg','-msgtxt']}

    returndict = {}

    namelist = []
    for item in typedict[type]:
        namelist.append(title+item)

    if type == 'quote':
#make the parent frame
        returndict[namelist[0]] = Frame(parent, bg=bc)
        returndict[namelist[0]].place(relheight = 1.0, relwidth = 1.0)
#make the holding frame for the other frames
        returndict[namelist[1]] = Frame(returndict[namelist[0]], bg=bc)
        returndict[namelist[1]].place(relx = 0.5, rely = 0.5, anchor =CENTER)
#Make the frame for the Message
        returndict[namelist[2]] = Frame(returndict[namelist[1]],bg=bc)
        returndict[namelist[2]].pack()
#make the signiture line
        returndict[namelist[3]] = Frame(returndict[namelist[1]],bg=bc)
        returndict[namelist[3]].pack()
#make the orgin line
        returndict[namelist[4]] = Frame(returndict[namelist[1]],bg=bc)
        returndict[namelist[4]].pack()
#make the message varibles
        returndict[namelist[10]] = StringVar()
        returndict[namelist[10]].set('               ')
        returndict[namelist[11]] = StringVar()
        returndict[namelist[11]].set('Error 302: Need more code')
        returndict[namelist[12]] = StringVar()
        returndict[namelist[12]].set('-Program')
        returndict[namelist[13]] = StringVar()
        returndict[namelist[13]].set('the ether')
#add the labels into the various frames
#message into the messagebox
        returndict[namelist[5]] = Message(returndict[namelist[2]],
                                          textvariable = returndict[namelist[11]],
                                          font = fnt,
                                          aspect = 500,
                                          fg = fc,
                                          bg = bc,
                                          justify=CENTER)
        returndict[namelist[5]].pack()
#placeholder
        returndict[namelist[6]] = Label(returndict[namelist[3]],
                                        textvariable = returndict[namelist[10]],
                                        font = fnt,
                                        fg = fc,
                                        bg = bc)
        returndict[namelist[6]].grid(row = 0, column = 0)
#signature
        returndict[namelist[8]] = Label(returndict[namelist[3]],
                                        textvariable = returndict[namelist[12]],
                                        font = fnt,
                                        fg = fc,
                                        bg = bc,
                                        justify=CENTER)
        returndict[namelist[8]].grid(row = 0, column = 1, columnspan = 3)
#placeholder
        returndict[namelist[7]] = Label(returndict[namelist[3]],
                                        textvariable = returndict[namelist[10]],
                                        font = fnt,
                                        fg = fc,
                                        bg = bc)
        returndict[namelist[7]].grid(row = 0, column = 4)
#orgin line
        returndict[namelist[9]] = Label(returndict[namelist[4]],
                                                  textvariable = returndict[namelist[13]],
                                                  font = fnt,
                                                  fg = fc,
                                                  bg = bc,
                                                  justify=CENTER)
        returndict[namelist[9]].pack()

        return returndict

    elif type == 'fallacy':
#make the parent frame
        returndict[namelist[0]] = Frame(parent, bg=bc)
        returndict[namelist[0]].place(relheight = 1.0, relwidth = 1.0)
#set the message variables
        returndict[namelist[3]] = StringVar()
        returndict[namelist[3]].set('Test Title')
        returndict[namelist[4]] = StringVar()
        returndict[namelist[4]].set('Test Message. Waiting on actual input')
#build the frame
        returndict[namelist[1]] = Label(returndict[namelist[0]],
                                                  textvariable = returndict[namelist[3]],
                                                  font = fnt,
                                                  fg = fc,
                                                  bg = bc,
                                                  justify=CENTER)
        returndict[namelist[1]].place(relx = 0.5, rely = 0.1, anchor =CENTER)
        returndict[namelist[4]] = Message(returndict[namelist[0]],
                                          textvariable = returndict[namelist[4]],
                                          font = fnt,
                                          aspect = 500,
                                          fg = fc,
                                          bg = bc,
                                          justify=CENTER)
        returndict[namelist[4]].place(relx = 0.5, rely = 0.5, anchor =CENTER)

        return returndict

    elif type == 'message':
#make the parent frame
        returndict[namelist[0]] = Frame(parent, bg=bc)
        returndict[namelist[0]].place(relheight = 1.0, relwidth = 1.0)
#set message variables
        returndict[namelist[2]] = StringVar()
        returndict[namelist[2]].set('Test Messages Screen. Waiting on actual input')
#build frame
        returndict[namelist[1]] = Message(returndict[namelist[0]],
                                          textvariable = returndict[namelist[2]],
                                          font = fnt,
                                          aspect = 500,
                                          fg = fc,
                                          bg = bc,
                                          justify=CENTER)
        returndict[namelist[1]].place(relx = 0.5, rely = 0.5, anchor =CENTER)
        return returndict


# root = Tk()
# root.attributes("-fullscreen", True)
# root.configure(background='black')
# root.bind("<Escape>", quit)
# root.bind("x", quit)
# fnt = font.Font(family='Helvetica', size=32, weight='bold')
#
# test = framemaker('test','message',root)
# root.mainloop()
