#Keir Murray
#07/05/2021

import tkinter as tk
from libs.constants import *

class frames:
    def __init__(self, root):
        self.root = root
        self.frames = {}
        self.raisebindings = {}
        self.root.update()
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
    
    def get(self, name):
        return self.frames.get(name)
    
    def new(self, name, *args, **kwargs):
        if self.get(name): return
        self.frames[name] = tk.Frame(self.root, *args, **kwargs)
        self.frames[name].config(bg = BG_COLOR, width = self.width, height = self.height)
        self.raisebindings[name] = []
        return self.frames[name]
    
    def show(self, name, bypass_placement = False):
        frame = self.get(name)
        if frame:
            if not bypass_placement:
                frame.grid(row = 0, column = 0, sticky = "news")
            frame.tkraise()
            for func in self.raisebindings[name]:
                func()
    
    def bindraise(self, name, func):
        self.raisebindings[name].append(func)

    def hide(self, name):
        frame = self.get(name)
        if frame:
            frame.place(relx = 9999999999999, rely = 999999999999) #ugly hack for "hiding" a frame