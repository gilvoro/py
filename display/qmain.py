from tkinter import *
from tkinter import ttk
from tkinter import font



dirloc = 'C:\\pve\\qd\\testfiles'
dfiles = ['skquotes','scquotes']

def quit(*args):
  root.destroy()

root = Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')
root.bind("<Escape>", quit)
root.bind("x", quit)
