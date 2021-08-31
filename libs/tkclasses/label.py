
from tkinter import ttk

class Label(ttk.Label):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs, style = "Theme.TLabel")