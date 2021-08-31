
objects = {}

def create(name, object):
    objects[name] = object

def get(name):
    return objects.get(name)

def getlist(*names):
    toReturn = {}
    for name in names:
        toReturn[name] = objects.get(name)
    return toReturn
