
import tkinter as tk
from libs.constants import *

class errorLabel(tk.Label):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs, bg = BG_COLOR, fg = "#ff8080", font = ("Arial", 18), wraplength = "170m")
    
    def raise_error(self, text):
        self.config(text = text)
    
    def hide(self):
        self.config(text = "")