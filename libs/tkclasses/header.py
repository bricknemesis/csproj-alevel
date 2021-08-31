
#Keir Murray
#18/09/2020

from tkinter import *
from libs.constants import *
import libs.tkclasses.frames as frames

def new(frame, text):
    header = Label(frame, text = text, font = ("bold", 35), bg = BG_COLOR, fg = FG_COLOR)
    header.place(relx = 0.5, rely = 0.06, anchor = ("center"))