
#this class isnt done yet

import tkinter as tk

imageObjects = {}

class ImageButton(tk.Button):
    def __init__(self, root, image, *args, **kwargs):
        self.button = tk.Button(root, *args, **kwargs)