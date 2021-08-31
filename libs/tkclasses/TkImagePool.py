
from PIL import ImageTk, Image

pool = {}

def open(path, name, dims=None):
    if get(name): return pool.get(name)
    imageObj = Image.open(path)
    if dims: imageObj = imageObj.resize(dims, Image.ANTIALIAS)
    pool[name] = ImageTk.PhotoImage( imageObj )
    return pool[name]

def get(name):
    return pool.get(name)