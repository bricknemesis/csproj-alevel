
from libs.constants import BG_ACCENT_COLOR
import tkinter as Tk
import libs.tkclasses.TkImagePool as TkImagePool
import random
from libs.constants import *
from functools import partial

BUTTON_DIMS = (120, 120)
BUTTON_PADDING = (5, 5)

accountTypeButtons = {
    "customer": [],
    "trainer": ["CustomerControlPanel", "LessonControlPanel"],
    "manager": ["CustomerControlPanel", "TrainerControlPanel", "LessonControlPanel"]
}

class DynamicSidebar(Tk.Frame):
    def __init__(self, manager, name, *args, **kwargs):
        self.manager = manager
        self.name = name
        self.sidebar = manager.new(name, *args, **kwargs, height = WINDOW_Y, bg = "pink")
        self.sidebar.config(width = 150, bg = BG_ACCENT_COLOR)
        self.frameNames = []
        self.buttons = {}
    
    def updateButtons(self, arr):
        i = 0
        for buttonName, button in self.buttons.items():
            if not buttonName in arr:
                print("Hide", buttonName)
                #button.place(relx = 99999999999, rely = 99999999999999999)
            else:
                #BUTTON_PADDING[1]*(i == 0 and 1 or 2) + BUTTON_DIMS[1] * i
                #print("Show", buttonName, "at", "x =", BUTTON_PADDING[0], "| y =", BUTTON_DIMS[1] * i + BUTTON_PADDING[1])
                #button.place(x = BUTTON_PADDING[0], y = BUTTON_DIMS[1] * i + BUTTON_PADDING[1], anchor = "nw")
                i += 1

    def addButton(self, imagePath, name, *args, **kwargs):
        img_key = "SidebarButton_"+str(random.randint(1, 9999))
        TkImagePool.open(imagePath, img_key, BUTTON_DIMS)
        self.buttons[name] = Tk.Button(self.sidebar, image = TkImagePool.get(img_key), bg = BG_ACCENT_COLOR, *args, **kwargs, activebackground = BG_ACCENT_COLOR, borderwidth = 0)
        self.buttons[name].config(padx = BUTTON_DIMS[0], pady = BUTTON_DIMS[1])
        self.buttons[name].place(x = BUTTON_PADDING[0], y = (BUTTON_PADDING[1]*(len(self.buttons)-1 == 0 and 1 or 2) + BUTTON_DIMS[1] * (len(self.buttons) - 1) ), anchor = "nw")
        self.updateButtons([])
    
    def linkButton(self, buttonName, frameName):
        def raiseFunc():
            self.manager.show(frameName)
            self.manager.show(self.name, True) #need to constantly be ontop
        self.buttons[buttonName].config(command = raiseFunc)
        self.frameNames.append(frameName)
    
    def updateForAccountType(self, accountType):
        self.updateButtons(accountTypeButtons[accountType])

