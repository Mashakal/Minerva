
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


# DECORATORS
from functools import wraps

def enterAndExitLabels(func):
    @wraps(func)
    def wrap(*args):
        print("Entering", func.__module__ +':'+ func.__name__)
        func(*args)
        print("Exiting", func.__module__ +':'+ func.__name__)
    return wrap