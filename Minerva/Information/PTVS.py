# There should be some way to validate that there are no triggers are the same for two separate keys.

NAME = "PTVS"

LINKS = {
    # All key MUST lead to either a url or a dictionary of keys that lead to a url.
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
            "Microsoft Azure Web Sites": "https://github.com/Microsoft/PTVS/wiki/Azure-Remote-Debugging",
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
#KEY_MAP = {
#    "Installation": {
#        "Triggers": ['installation', 'install', 'instalation', 'installs']
#    },
#    "Debugging": {
#        'Triggers': ['debugging', 'debug', 'debugger', 'debuggor'],
#        'Subkeys': {
#            'Remote Debugging': ['remote', 'attach', 'attached', 'nonlocal', 'ptvsd']
#        }
#    },
#    "Feature Matrix": {
#        'Triggers': ['feature matrix', 'features']
#    },
#    'Overview Videos': {
#        'Triggers': ['overview videos', 'video', 'videos', 'overview']
#    },
#    'Contributing': {
#        'Triggers': ['contributing', 'contribute', 'pull request']
#    },
#    'Build Instructions': {
#        'Triggers': ['build instructions', 'building', 'build']
#    },
#    'Editing': {
#        'Triggers': ['editing', 'code editing']
#    }
#}

KEY_MAP = {
    "Installation": {
        "Triggers": ['installation', 'install', 'instalation', 'installs']
    },
    'Projects': {
        'Triggers': ['projects', 'project'],
        "Django": {
            'Triggers': ['django']
        },
        'Web Projects': {
            'Triggers': ['web projects', 'web']
        },
        'Project Types': {
            'Triggers': ['project types', 'types', 'type']
        },
        'Cloud Service Project': {
            'Triggers': ['cloud service project', 'cloud project', 'cloud']
        },
        'Working Without Projects': {
            'Triggers': ['working without projects', 'without projects', 'lightweight', 'lightweight-usage', 'project-free', 'project free']
        }
    },
    "Debugging": {
        'Triggers': ['debugging', 'debug', 'debugger', 'debuggor'],
        'Remote Debugging': {
            'Triggers': ['remote', 'attach', 'attached', 'nonlocal', 'ptvsd']
        }
    },
    "Feature Matrix": {
        'Triggers': ['feature matrix', 'features']
    },
    'Overview Videos': {
        'Triggers': ['overview videos', 'video', 'videos', 'overview']
    },
    'Contributing': {
        'Triggers': ['contributing', 'contribute', 'pull request']
    },
    'Build Instructions': {
        'Triggers': ['build instructions', 'building', 'build']
    },
    'Editing': {
        'Triggers': ['editing', 'code editing']
    }
}