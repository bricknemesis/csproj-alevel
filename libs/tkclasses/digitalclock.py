
from tkinter import *
from time import strftime
from libs.constants import *

class Clock(Label):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.configure(font = FONT_CONFIG, bg = BG_ACCENT_COLOR, fg = FG_COLOR, width = 10, height = 1)
        self.go()
    
    def update(self):
        now = strftime("%H:%M:%S")
        self.configure(text = now)
    
    def go(self):
        self.update()
        self.after(1000, self.go)