from InfoManager import InfoManager

# For development purposes only:
from Essentials import enter_and_exit_labels, print_smart

# Constants
# These may be better off in the Bot module.
_YES_WORDS = ['yes', 'yeah', 'okay', 'ok', 'k', 'y', 'ya', 'right', 'correct', "that's right", 'sure', 'for sure']
_NO_WORDS = ['no', 'n', 'nah', 'nope', 'negative']

class BaseLuisInterpreter(object):
    """A base class for all interpreters."""
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def analyze(self, json):
        """Analyzes the json returned from a call to the base LuisClient class's method, query_raw."""
        raise NotImplementedError("Function analyze has not yet been customized.")

    @classmethod
    def _get_top_scoring_intent(cls, json):
        try:
            return json['intents'][0]['intent']
        except LookupError:
            return 'undefined'

    @classmethod
    def _get_literals(cls, json):
        return [e['entity'] for e in json['entities']]

    @classmethod
    def _get_types(cls, json):
        return [e['type'] for e in json['entities']]

    @classmethod
    def _get_all_literals_of_type(cls, t, json):
        return [e['entity'] for e in json['entities'] if e['type'] == t]

class ProjectSystemLuisInterpreter(BaseLuisInterpreter):
    """Interprets questions for language specific project systems of Visual Studio
    as a part of a help bot.
    """
    def __init__(self, bot, project_system):
        self._info = InfoManager(project_system)
        self._bot = bot
        
        # Maps an intent to a function.
        self._STRATAGIES = {
            'Get Help': self._get_help,
            'undefined': self._undefined
        }

    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        intent = self._get_top_scoring_intent(json)
        return self._STRATAGIES[intent](json)

    def _format_data(self, json):
        """Formats the raw json into a more easily managable dictionary."""
        o = {
            #'query': json['query'],
            #'literals': self._get_literals(json),
            #'types': self._get_types(json),
            'keywords': self._get_all_literals_of_type('Keyword', json),
            'vs_features': self._get_all_literals_of_type('Visual Studio Feature', json),
            'intent': self._get_top_scoring_intent(json)
        }
        #o['root_keys'] = self._info.get_all_root_keys(o['keywords'])
        o['paths'] = self.__get_paths(set(o['keywords'] + o['vs_features']))
        return o

    def __get_paths(self, word_set):
        # I die a little inside everytime I look at this function.
        """Get's paths to all words in the set, if a path for it exists.
        Filters the paths found such that only the deepest path will be
        returned, which is helpful when a Luis picks up a trigger to a key
        and also a trigger to a more specialized version of that key in the
        same query.
        """
        def get_paths(word_set):
            """A helper function for __get_paths.  Returns an unfiltered list
            of all the paths pointed to by words in the word set.
            """
            paths = []
            for word in word_set:
                path = self._info.find_key_path(word)
                if path:
                    paths.append(path)
            return paths
        
        def remove_duplicates(paths, key):
            """Remove all but the longest path from paths."""
            list_max = None     # The list with the longest length.
            # Get the paths that contain key.
            with_key = [path for path in paths if key in path]
            # Find the longest one.
            for path in with_key:
                if not list_max or len(path) > len(list_max):
                    list_max = path
            # Remove all lists of paths that are not the one with the longest length.
            [paths.remove(p) for p in with_key if p is not list_max]
            return paths
        
        paths = get_paths(word_set)
        flattened_paths = [p for path in paths for p in path]
        counts = {}
        for key in flattened_paths:
            if key in counts.keys():
                counts[key] += 1
            else:
                counts[key] = 1
        for key, count in counts.items():
            if count > 1:
                paths = remove_duplicates(paths, key) 
        # TODO:  Log how many paths were returned, and which ones.
        return paths
    
    def _get_help(self, json):
        """Called from function 'analyze' when the intent of a LUIS query is determined
        to be 'Get Help'.
        """
        def clarify_paths(paths):
            """Determine which topic is most pertinent to the user
            when more than one unique path is found given the
            user's query.
            """
            # One path is good, as long Luis picked up the right keywords.
            if 1 == len(paths):
                return paths
            elif 1 < len(paths):
                ending_keys = [p[len(p) - 1] for p in paths]
                ans = self._bot.clarify(ending_keys)
                return [p for p in paths for a in ans if p[len(p) - 1] == a]
            else:
                # No paths found.
                return False

        def get_ending_url(path):
            u = self._info.traverse_keys(path)
            while not isinstance(u, str):   # Path might not lead to url yet.
                if 'Home' in u.keys():
                    path.append('Home') # Some keys have sub keys and an url.
                else:
                    # If our path doesn't point to a key with its own url,
                    # ask the user where to go from here.
                    keys = list(u.keys())
                    # We only need to ask when there is more than one potential key.
                    if 1 < len(keys):
                        next = self._bot.give_options([k for k in u.keys()])
                        path.append(next)
                    else:
                        path.append(keys[0])
                u = self._info.traverse_keys(path)
            return u

        data = self._format_data(json)
        
        # Print some debugging information.
        #print("QUERY: {0}".format(data['query']))
        #for i in range(len(data['literals'])):
        #    print("{0}: {1}".format(data['types'][i].upper(), data['literals'][i]))
        #print("*" * 79)

        # Check if the user triggered any links to the wiki page.
        paths = clarify_paths(data['paths'])
        if paths:
            self._bot.acknowledge([p[len(p) - 1] for p in paths])
            urls = [get_ending_url(path) for path in paths]
            for url in urls:
                self._bot.suggest_url(url)
        else:
            # Try StackExchange
            self._bot.say("Hmmm, I'm sorry.  Let me see what I can find through stackoverflow.")
            pass

    def _undefined(self):
        self._bot.say("I'm sorry, I don't know what you're asking.")
