
from tkinter import ttk
from tkinter import *
import libs.tkclasses.frames as frames
import textwrap

def wrap(string, length=8):
    #print(type(string))
    #return "\n".join(textwrap.wrap(string, length))
    return string

class TV:
    def __init__(self, root, *args):
        self.treeview = ttk.Treeview(root, columns = ( *[*args][1:], ) )
        self.lastColumnNumber = -1

        scroll = Scrollbar(root)
        scroll.configure(command = self.treeview.yview)
        self.treeview.configure(yscrollcommand = scroll.set)

        for heading in args:
            self.lastColumnNumber += 1
            self.treeview.heading(f"#{self.lastColumnNumber}", text = heading)
        
        for i in range(0, len(args)):
            self.treeview.column(f"#{i}", stretch = NO, width = 90)
    
    def insert(self, header, values):
        self.treeview.insert("", "end", text = header, values = values)
    
    def flush(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)