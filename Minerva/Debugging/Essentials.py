
# FUNCTIONS
def print_smart(item, depth=0):
    """Prints a container object and its contents in a readable way."""
    if isinstance(item, str, int, float, bool):
        print(' ' * (depth * 3) + str(item))
        return
    new_depth = depth + 1
    if isinstance(item, list):
        for el in item:
            print_smart(el, depth)
    elif isinstance(item, dict):
        for key in item:
            print(' ' * (depth * 3) + str(key))
            print_smart(item[key], depth=new_depth)
    else:
        s = "Function print_smart isn't sure what to do with the type: {0}".format(item)
        print_smart(s, depth=depth)

def json_to_file(j, filename):
    """Appends data to the given file.  If the file does not exist it is created."""
    import json
    with open(filename, 'w') as fdesc:
        json.dump(j, fdesc)

def file_to_json(filename):
    """Loads a json object from a file."""
    import json
    with open(filename, 'r') as fdesc:
        j = json.load(fdesc)
    return j

def get_file_size(filename):
    try:
        from os import stat
        st = stat(filename)
        return st.st_size
    except FileNotFoundError:
        return 0

def load_debug_json(filename, fetch_function, query=None):
# Not finished. Do not use.
    """Loads json from the file specified by 'filename'.  If the file doesn't exist, makes a call to 
    fetchFunction and expects a json object in response.  Will write the newly obtained json to 
    filename."""
    if 0 == get_file_size(f):
        j = fetch_function(query) if query else fetch_function()
        json_to_file(j, filename)
    else:
        j = file_to_json(filename)
    return j

# DECORATORS
def enter_and_exit_labels(func):
    from functools import wraps
    @wraps(func)
    def wrap(*args):
        print("Entering", func.__module__ +':'+ func.__name__)
        func(*args)
        print("Exiting", func.__module__ +':'+ func.__name__)
    return wrap