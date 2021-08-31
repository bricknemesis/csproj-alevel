
from tkinter import ttk
import re

class Entry(ttk.Entry):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs, style = "Theme.TEntry")