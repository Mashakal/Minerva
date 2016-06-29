LINKS = {
    "WIKI": "https://github.com/Microsoft/PTVS/wiki",
    "Installation": "https://github.com/Microsoft/PTVS/wiki/PTVS-Installation",
    "Feature Matrix": "https://github.com/Microsoft/PTVS/wiki/Features-Matrix",
    "Overview Videos": "https://github.com/Microsoft/PTVS/wiki/Videos",
    "Contributing": "https://github.com/Microsoft/PTVS/wiki/Contributing-to-PTVS",
    "Build Instructions": "https://github.com/Microsoft/PTVS/wiki/Build-Instructions-for-PTVS",
    "Tutorials": {
        "Bottle and Azure Table Storage": "https://github.com/Microsoft/PTVS/wiki/Bottle-and-Azure-Table-Storage-on-Azure",
        "Bottle and MongoDB": "https://github.com/Microsoft/PTVS/wiki/Bottle-and-MongoDB-on-Azure",
        "Flask and Azure Table Storage": "https://github.com/Microsoft/PTVS/wiki/Flask-and-Azure-Table-Storage-on-Azure",
        "Flask and MongoDB": "https://github.com/Microsoft/PTVS/wiki/Flask-and-MongoDB-on-Azure",
        "Django and SQL Database": "https://github.com/Microsoft/PTVS/wiki/Django-and-SQL-Database-on-Azure",
        "Django and MySQL": "https://github.com/Microsoft/PTVS/wiki/Django-and-MySQL-on-Azure"
    },
    "Editing": "https://github.com/Microsoft/PTVS/wiki/Editor-Features",
    "Intellisense": "https://github.com/Microsoft/PTVS/wiki/Editor-Features#intellisense",
    "Navigation": "https://github.com/Microsoft/PTVS/wiki/Editor-Features#navigation",
    "Code Formatting": "https://github.com/Microsoft/PTVS/wiki/Code-Formatting",
    "Refactoring": {
        "BASE_URL": "https://github.com/Microsoft/PTVS/wiki/Refactoring",
        "Rename": "https://github.com/Microsoft/PTVS/wiki/Refactoring#rename-variable",
        "Extract Method": "https://github.com/Microsoft/PTVS/wiki/Refactoring#extract-method",
        "Add Import": "https://github.com/Microsoft/PTVS/wiki/Refactoring#add-import",
        "Remove Imports": "https://github.com/Microsoft/PTVS/wiki/Refactoring#remove-imports"
    },
    "Interactive REPL": {
        "BASE_URL": "https://github.com/Microsoft/PTVS/wiki/Interactive-REPL",
        "Switching Scopes": "https://github.com/Microsoft/PTVS/wiki/Interactive-REPL#switching-scopes",
        "Send Code to Interactive": "https://github.com/Microsoft/PTVS/wiki/Interactive-REPL#sending-code-to-interactive",
        "Using IPython with PTVS": "https://github.com/Microsoft/PTVS/wiki/Using-IPython-with-PTVS"
    },
    "Debugging": {
        "BASE_URL": "https://github.com/Microsoft/PTVS/wiki/Debugging",
        "Basic Debugging": "https://github.com/Microsoft/PTVS/wiki/Debugging#basic-debugging",
        "Debugging with a Project": "https://github.com/Microsoft/PTVS/wiki/Debugging#debugging-with-a-project",
        "Debugging without a Project": "https://github.com/Microsoft/PTVS/wiki/Debugging#debugging-without-a-project",
        "The Debug Interactive Window": "https://github.com/Microsoft/PTVS/wiki/Debugging#the-debug-interactive-window",
        "Remote Debugging": {
            "Windows, Linux, and OS X": "https://github.com/Microsoft/PTVS/wiki/Cross-Platform-Remote-Debugging",
            "Microsoft Azure Web Sites": "https://github.com/Microsoft/PTVS/wiki/Azure-Remote-Debugging"
        },
        "Mixed-Mode Debugging": "https://github.com/Microsoft/PTVS/wiki/Mixed-Mode-Debugging"
    },
    "Profiling": "https://github.com/Microsoft/PTVS/wiki/Profiling",
    "Projects": {
        "BASE_URL": "https://github.com/Microsoft/PTVS/wiki/Projects",
        "Project Types": "https://github.com/Microsoft/PTVS/wiki/Projects#project-types",
        "Django": "https://github.com/Microsoft/PTVS/wiki/Django",
        "Web Projects": "https://github.com/Microsoft/PTVS/wiki/Web-Project",
        "Cloud Service Project": "https://github.com/Microsoft/PTVS/wiki/Cloud-Project",
        "Working without Projects": "https://github.com/Microsoft/PTVS/wiki/Projects#lightweight-usage-project-free",
        "New Project from Existing Code": "https://github.com/Microsoft/PTVS/wiki/Projects#create-project-from-existing-files",
        "Linked Files": "https://github.com/Microsoft/PTVS/wiki/Projects#linked-files",
        "Search Paths": "https://github.com/Microsoft/PTVS/wiki/Projects#search-paths",
        "References": "https://github.com/Microsoft/PTVS/wiki/Projects#references",
        "Python Environments": "https://github.com/Microsoft/PTVS/wiki/Python-Environments",
        "Managing Requirements": "https://github.com/Microsoft/PTVS/wiki/Python-Environments#managing-required-packages"
    },
    "Unit Tests": "https://github.com/Microsoft/PTVS/wiki/Unit-Tests",
    "PyLint": "https://github.com/Microsoft/PTVS/wiki/PyLint",
    "Azure SDK for Python": "https://github.com/Microsoft/PTVS/wiki/AzureSDK",
    "Kinect for Python": "https://github.com/Microsoft/PTVS/wiki/PyKinect",
    "wfastcgi (on PyPI)": "https://pypi.python.org/pypi/wfastcgi"
}

# TODO:  Make updating this map with new synonyms/triggers automatic.
KEY_MAP = {
    "Debugging": {
        'synonyms': ['debug', 'debugger', 'debugging', 'debuggor'],
        'keywords': {
            'Remote Debugging': ['remote', 'attach', 'attached', 'nonlocal', 'ptvsd']
        }
    }
}

def literalToKey(literal):
    """Returns the appropriate key for links when given a literal.
    For example, if the literal passed in is "debug" it will map this to
    "Debugging" for extraction of information out of LINKS.
    """
    for k, v in KEY_MAP.items():
        if literal.lower() in v['synonyms']:
            return k
    return None

def filterWithKeyword(feature, keyword):
    """Determine if a previously identified feature has more specific 
    context in relation to 'keyword'.  Will return a key for
    which to extract a link corresponding feature's link from LINKS.
    """
    keywords = KEY_MAP[feature]['keywords']
    for k, v in keywords.items():
        if keyword in v:
            return k
    return None

def getRefinedKeys(keyFeature, keywords):
    """Returns a list of refined key features, based on any keywords that were
    found in the original query.
    """
    refinedKeys = []
    if 0 < len(keywords):
        for word in keywords:
            filtered = filterWithKeyword(keyFeature, word)
            if filtered:
                refinedKeys.append(filtered)
    return refinedKeys