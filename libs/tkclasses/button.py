
from tkinter import ttk

class Button(ttk.Button):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs, style = "Placeholder.TButton")