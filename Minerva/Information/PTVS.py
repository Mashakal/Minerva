############################################################################################
# TO NOTE:
#  - All keys in LINKS should be unique.
#  - All triggers in KEY_MAP should be unique.
#  - All punctuation in triggers should be separated by spaces, to conform to LUIS standards.
############################################################################################
# There should be some way to validate that there are no triggers are the same for two separate keys.

NAME = "PTVS"

LINKS = {
    # All key MUST lead to either a url or a dictionary of keys that lead to a url.
    "WIKI": "https://github.com/Microsoft/PTVS/wiki",
    "Installation": "https://github.com/Microsoft/PTVS/wiki/PTVS-Installation",
    "Packages": {
        "Installing Packages": 'https://github.com/Microsoft/PTVS/wiki/PTVS-Installation#python-package-installation-options',
        "Managing Required Packages": "https://github.com/Microsoft/PTVS/wiki/Python-Environments#managing-required-packages"
    },
    "Feature Matrix": "https://github.com/Microsoft/PTVS/wiki/Features-Matrix",
    "Overview Videos": "https://github.com/Microsoft/PTVS/wiki/Videos",
    "Contributing": "https://github.com/Microsoft/PTVS/wiki/Contributing-to-PTVS,",
    "Build Instructions": "https://github.com/Microsoft/PTVS/wiki/Build-Instructions-for-PTVS",
    "Tutorials": {
        "Bottle and Azure Table Storage": "https://github.com/Microsoft/PTVS/wiki/Bottle-and-Azure-Table-Storage-on-Azure",
        "Bottle and MongoDB": "https://github.com/Microsoft/PTVS/wiki/Bottle-and-MongoDB-on-Azure",
        "Flask and Azure Table Storage": "https://github.com/Microsoft/PTVS/wiki/Flask-and-Azure-Table-Storage-on-Azure",
        "Flask and MongoDB": "https://github.com/Microsoft/PTVS/wiki/Flask-and-MongoDB-on-Azure",
        "Django and SQL Database": "https://github.com/Microsoft/PTVS/wiki/Django-and-SQL-Database-on-Azure",
        "Django and MySQL": "https://github.com/Microsoft/PTVS/wiki/Django-and-MySQL-on-Azure",
        "Python Interpreters": "https://www.youtube.com/watch?v=KY1GEOo3qy0&feature=youtu.be",
    },
    "Environments": {
        "Environments Home": "https://github.com/Microsoft/PTVS/wiki/Python-Environments",
        "The Python Environment": "https://github.com/Microsoft/PTVS/wiki/Python-Environments#the-python-environment",
        "Global Environments": "https://github.com/Microsoft/PTVS/wiki/Python-Environments#global-environments",
        "Project Environments": "https://github.com/Microsoft/PTVS/wiki/Python-Environments#project-environments",
        "Virtual Environments": "https://github.com/Microsoft/PTVS/wiki/Python-Environments#virtual-environments",
    },
    "Editing": "https://github.com/Microsoft/PTVS/wiki/Editor-Features",
    "Intellisense": "https://github.com/Microsoft/PTVS/wiki/Editor-Features#intellisense",
    "Navigation": "https://github.com/Microsoft/PTVS/wiki/Editor-Features#navigation",
    "Code Formatting": "https://github.com/Microsoft/PTVS/wiki/Code-Formatting",
    "Refactoring": {
        "Refactoring": "https://github.com/Microsoft/PTVS/wiki/Refactoring",
        "Rename": "https://github.com/Microsoft/PTVS/wiki/Refactoring#rename-variable",
        "Extract Method": "https://github.com/Microsoft/PTVS/wiki/Refactoring#extract-method",
        "Add Import": "https://github.com/Microsoft/PTVS/wiki/Refactoring#add-import",
        "Remove Imports": "https://github.com/Microsoft/PTVS/wiki/Refactoring#remove-imports"
    },
    "Interactive REPL": {
        "Interactive REPL Home": "https://github.com/Microsoft/PTVS/wiki/Interactive-REPL",
        "Switching Scopes": "https://github.com/Microsoft/PTVS/wiki/Interactive-REPL#switching-scopes",
        "Send Code to Interactive": "https://github.com/Microsoft/PTVS/wiki/Interactive-REPL#sending-code-to-interactive",
        "Using IPython with PTVS": "https://github.com/Microsoft/PTVS/wiki/Using-IPython-with-PTVS"
    },
    "Debugging": {
        "Debugging Home": "https://github.com/Microsoft/PTVS/wiki/Debugging",
        "Basic Debugging": "https://github.com/Microsoft/PTVS/wiki/Debugging#basic-debugging",
        "Debugging with a Project": "https://github.com/Microsoft/PTVS/wiki/Debugging#debugging-with-a-project",
        "Debugging without a Project": "https://github.com/Microsoft/PTVS/wiki/Debugging#debugging-without-a-project",
        "The Debug Interactive Window": "https://github.com/Microsoft/PTVS/wiki/Debugging#the-debug-interactive-window",
        "Remote Debugging": {
            "Cross Platform": "https://github.com/Microsoft/PTVS/wiki/Cross-Platform-Remote-Debugging",
            "Microsoft Azure Web Sites": "https://github.com/Microsoft/PTVS/wiki/Azure-Remote-Debugging",
        },
        "Mixed-Mode/Native Debugging": {
            'General Info': "https://github.com/Microsoft/PTVS/wiki/Mixed-Mode-Debugging",
            'Symbols for Mixed-Mode Debugging': 'https://github.com/Microsoft/PTVS/wiki/Symbols-for-Python-mixed-mode-debugging'
        }
    },
    "Profiling": "https://github.com/Microsoft/PTVS/wiki/Profiling",
    "Projects": {
        "Projects Home": "https://github.com/Microsoft/PTVS/wiki/Projects",
        "Project Types": "https://github.com/Microsoft/PTVS/wiki/Projects#project-types",
        "Django": "https://github.com/Microsoft/PTVS/wiki/Django",
        "Web Projects": "https://github.com/Microsoft/PTVS/wiki/Web-Project",
        "Cloud Service Project": "https://github.com/Microsoft/PTVS/wiki/Cloud-Project",
        "Working Without Projects": "https://github.com/Microsoft/PTVS/wiki/Projects#lightweight-usage-project-free",
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
    "wfastcgi (on PyPI)": "https://pypi.python.org/pypi/wfastcgi",
    "Azure": {
        "Deploy to Azure": "https://github.com/Microsoft/PTVS/wiki/Web-Project#publishing-to-microsoft-azure",
        "Azure Home": "https://azure.microsoft.com/en-us/free/"
    },
    "The Zen of Python": "http://www.thezenofpython.com/",
    "Porting to Python 3": "https://docs.python.org/3.3/howto/pyporting.html",
    "Python Versions": {
        "Which Python Version Should I Use?": "https://wiki.python.org/moin/Python2orPython3"
    },
    "AWS": {
        "Deploy to AWS": "https://aws.amazon.com/python/"
    }
}


KEY_MAP = {
    'Tutorials': {
        'Triggers': {'tutorials', 'tutorial', 'show me'},
        'Bottle and Azure Table Storage': {
            'Triggers': {'bottle and azure table storage', 'bottle and azure', 'bottle table storage'}
        },
        'Bottle and MongoDB': {
            'Triggers': {'bottle and mongodb', 'mongodb and bottle'}
        },
        'Flask and Azure Table Storage': {
            'Triggers': {'flask and azure table storage', 'flask and azure', 'flask table storage'}
        },
        'Flask and MongoDB': {
            'Triggers': {'flask and mongodb', 'mongodb and flask', 'flask mongodb', 'mongodb flask'}
        },
        'Django and SQL Database': {
            'Triggers': {'django and sql database', 'django and sql', 'django database', 'django with sql'}
        },
        'Django and MySql': {
            'Triggers': {'django and mysql', 'django with mysql'}
        },
        'Python Interpreters': {
            'Triggers': {'interpreters tutorial', 'interpreter tutorial'}
        }
    },
    'Environments': {
        'Triggers': {'environments', 'env', 'envs'},
        'Environments Home': {
            'Triggers': {''}
        },
        'The Python Environment': {
            'Triggers': {'environment', 'env', 'envs', 'environments'}
        },
        'Global Environments': {
            'Triggers': {'global environements', 'global environment'}
        },
        'Project Environments': {
            'Triggers': {'project environments', 'project environment'}
        },
        'Virtual Environments': {
            'Triggers': {'virtual environments', 'virtual environment', 'v env', 'venv', 'venvs'}
        }
    },
    'Packages': {
        'Triggers': {'packages', 'modules'},
        'Installing Packages': {
            'Triggers': {'installing packages', 'installing modules', 'how to install', 'how do i install', 'wheels', 'wheel'}
        },
        'Managing Required Packages': {
            'Triggers': {'managing required packages', 'required packages', 'requirements', 'requirements file', 'requirements.txt', 'how to use requirements'}
        }
    },
    'WIKI': {
        'Triggers': {'wiki'}
    },
    "Installation": {
        "Triggers": {'installation', 'install', 'instalation', 'installs'}
    },
    'Projects': {
        "Django": {
            'Triggers': {'django', 'django web project', 'django project'}
        },
        'Web Projects': {
            'Triggers': {'web projects', 'web', 'deploy', 'deploy a website', 'web project'}
        },
        'Project Types': {
            'Triggers': {'project types', 'types', 'type'}
        },
        'Cloud Service Project': {
            'Triggers': {'cloud service project', 'cloud project', 'cloud', 'cloud projects'}
        },
        'Working Without Projects': {
            'Triggers': {'working without projects', 'without projects', 'lightweight', 'lightweight-usage', 'project-free', 'project free'}
        },
        'New Project from Existing Code':{
            'Triggers': {'new project', 'existing code', 'create project', 'create new project'}
        },
        'Linked Files': {
            'Triggers': {'linked files', 'linked', 'linked file', 'create a linked file', 'link a file', 'link'}
        },
        'Search Paths': {
            'Triggers': {'search paths', 'user defined modules', 'user defined packages', 'custom packages'}
        },
        'References': {
            'Triggers': {'references', 'what are references'}
        }
    },
    'Navigation': {
        'Triggers': {'navigation', 'navigate'}
    },
    'Refactoring': {
        'Triggers': {'refactoring'},
        'Rename': {
            'Triggers': {'rename', 'rename a variable', 'rename something', 'rename a symbol'}
        },
        'Extract Method': {
            'Triggers': {'extract method', 'extract'}
        },
        'Add Import': {
            'Triggers': {'add import', 'add imports', 'add an import'}
        },
        'Remove Imports': {
            'Triggers': {'remove imports', 'remove import'}
        }
    },
    "Debugging": {
        'Triggers': {'debugging', 'debug', 'debugger', 'debuggor'},
        'Remote Debugging': {
            'Triggers': {'remote debugging', 'remote debug', 'debug remotely', 'remote', 'attach', 'attached', 'nonlocal', 'attach', 'attach a process', 'ptvsd'}
        },
        'Basic Debugging': {
            'Triggers': {'basic debugging', 'debugging', 'debug', 'debugger', 'debuggor'}
        },
        'Debugging with a Project': {
            'Triggers': {'debugging with a project'}
        },
        'Debugging without a Project': {
            'Triggers': {'debugging without a project'}
        },
        'The Debug Interactive Window': {
            'Triggers': {'debug interactive window', 'debugging interactive window', 'interactive window'}
        },
        'Mixed-Mode/Native Debugging': {
            'Triggers': {'mixed - mode debugging', 'mixed mode', 'mixed - mode', 'mixed mode debugging', 'native debugging', 'native debug'},
            'Symbols for Mixed-Mode Debugging': {
                'Triggers': {'symbols', 'download symbols', 'winpython', 'enthought canopy'}
            }
        }
    },
    'Interactive REPL': {
        'Triggers': {'interactive repl', 'repl', 'interactive'},
        'Switching Scopes': {
            'Triggers': {'switching scopes', 'changing scopes'}
        },
        'Send Code to Interactive': {
            'Triggers': {'send code to interactive', 'send to interactive', 'to interactive'}
        },
        'Using IPython with PTVS': {
            'Triggers': {'using ipython with ptvs', 'using ipython', 'ipython'}
        }
    },
    "Feature Matrix": {
        'Triggers': {'feature matrix', 'features'}
    },
    'Overview Videos': {
        'Triggers': {'overview videos', 'video', 'videos', 'overview'}
    },
    'Contributing': {
        'Triggers': {'contributing', 'contribute', 'pull request'}
    },
    'Build Instructions': {
        'Triggers': {'build instructions', 'building', 'build'}
    },
    'Editing': {
        'Triggers': {'editing', 'code editing'}
    },
    'Intellisense': {
        'Triggers': {'intellisense', 'autocomplete', 'completions', 'signature help', 'quick info', 'completion'}
    },
    'Code Formatting': {
        'Triggers': {'code formatting'}
    },
    'Profiling': {
        'Triggers': {'profiling', 'profiler', 'performance report', 'performance reports'}
    },
    'Unit Tests': {
        'Triggers': {'unit tests', 'tests', 'unittests', 'unittest', 'unit test', 'unittesting', 'unit testing'}
    },
    'PyLint': {
        'Triggers': {'pylint', 'py lint', 'linter'}
    },
    'Azure SDK for Python': {
        'Triggers': {'azure sdk for', 'azure sdk', 'sdk'}
    },
    'Kinect for Python': {
        'Triggers': {'kinect for', 'kinect'}
    },
    'wfastcgi (on PyPI)': {
        'Triggers': {'wfastcgi', 'wfastcgi on pypi', 'pypi wfastcgi'}
    },
    'Azure': {
        'Deploy to Azure': {
            'Triggers': {'deploy to azure', 'deployment on azure', 'deploy a website', 'deploy a flask website', 'deploy a django website', 'deploy a website'}
        },
        'Azure Home': {
            'Triggers': {'azure', 'azure home'}
        }
    },
    'The Zen of Python': {
        'Triggers': {'the zen of python', 'zen of python', 'zen'}
    },
    'Porting to Python 3': {
        'Triggers': {'porting to', 'porting code', 'python3', 'python 3', 'port code', 'port', 'from python 2', 'from python2'}
    },
    'Python Versions': {
        'Triggers': {'python versions'},
        'Which Python Version Should I Use?': {
            'Triggers': {'which python version should I use', 'which version', 'which python', 'why python 3', 'why python 2'}
        }
    },
    'AWS': {
        'Deploy to AWS': {
            'Triggers': {'deploy to aws', 'aws'}
        }
    }
}
