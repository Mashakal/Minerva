
# FUNCTIONS
def printSmart(item, depth = 0):
    """Prints a container object and its contents in a highly readable way."""
    if type(item) in [str, int, float, bool]:
        print(' ' * (depth * 3) + str(item))
        return
    newDepth = depth + 1
    if isinstance(item, list):
        for el in item:
            printSmart(el, depth)
    elif isinstance(item, dict):
        for key in item:
            print(' ' * (depth * 3) + str(key))
            printSmart(item[key], depth=newDepth)
    else:
        s = 'printSmart isn\'t sure what to do with the type: ' + str(type(item))
        printSmart(s, depth=depth)

def jsonToFile(js, filename):
    """Appends data to the given file.  If the file does not exist it is created."""
    import json
    with open(filename, 'w') as fdesc:
        json.dump(js, fdesc)

def fileToJson(filename):
    """Loads a json object from a file."""
    import json
    with open(filename, 'r') as fdesc:
        js = json.load(fdesc)
    return js

def getFileSize(filename):
    try:
        from os import stat
        st = stat(filename)
        return st.st_size
    except FileNotFoundError:
        return 0

def loadDebugJson(filename, fetchFunction, query=None):
# Not finished.
    """Loads json from the file specified by 'filename'.  If the file doesn't exist, makes a call to 
    fetchFunction and expects a json object in response.  Will write the newly obtained json to 
    filename."""
    if 0 == getFileSize(f):
        j = fetchFunction(query) if query else fetchFunction()
        jsonToFile(j, filename)
    else:
        j = fileToJson(filename)
    return j

# DECORATORS
def enterAndExitLabels(func):
    from functools import wraps
    @wraps(func)
    def wrap(*args):
        print("Entering", func.__module__ +':'+ func.__name__)
        func(*args)
        print("Exiting", func.__module__ +':'+ func.__name__)
    return wrap