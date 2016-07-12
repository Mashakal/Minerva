import InfoManager
import collections

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
     
    def _get_top_scoring_intent(self, json):
        try:
            return json['intents'][0]['intent']
        except LookupError:
            return 'undefined'

    def _get_literals(self, json):
        return set(([e['entity'] for e in json['entities']])) or None

    def _get_types(self, json):
        return set(([e['type'] for e in json['entities']])) or None

    def _literals_given_type(self, t, json):
        return set(([e['entity'] for e in json['entities'] if e['type'] == t])) or None

    def _get_literals_given_parent_type(self, parent, json):
        return set(([child['entity'] for child in json['entities'] if parent in child['type']])) or None

class ProjectSystemLuisInterpreter(BaseLuisInterpreter):
    """Interprets questions for language specific project systems of Visual Studio
    as a part of a help bot.
    """
    def __init__(self, bot, project_system):
        # _info is the main point of access for anything specific to a project (e.g. urls, triggers, keywords).
        self._info = InfoManager.ProjectSystemInfoManager(project_system)
        # Use _bot to interact with the user (e.g. ask a question, clarify between options, acknowledge keywords).
        self._bot = bot
        
        # Maps an intent to a function.
        self._STRATAGIES = {
            'Solve Problem': self._solve_problem,
            'Learn About Topic': self._learn_about_topic,
            'None': self._none_intent
        }

    # Entry.
    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        data = self._format_data(json)
        self._print_from_data(data)
        try:
            self._STRATAGIES[data['intent']](data)
        except KeyError:
            self._STRATAGIES['None']()

    # Utility functions.
    def _print_from_data(self, data):
        for k, v in data.items():
            print("{0}: {1}".format(k.upper(), v))

    def _format_data(self, json):
        """Formats the raw json into a more easily managable dictionary."""
        o = {
        # Meta keys - these point to dictionaries.
            'intents': json['intents'],
            'entities': json['entities'],
        # Leaf keys - these point to a value or some container of values.
            'query': json['query'],
            'intent': json['intents'][0]['intent'],
            # The top scoring intent.
            'top_intent': json['intents'][0]['intent'],
            # All intents OTHER than the top scoring intent.
            'other_intents': json['intents'][1:],
            'subjects': self._literals_given_type('Subject', json),
            'auxiliaries': self._literals_given_type('Auxiliary', json),
            'negators': self._literals_given_type('Negator', json),
            # Action types.
            'gerunds': self._literals_given_type('Action::Gerund', json),
            'conjugated_verbs': self._literals_given_type('Action::Conjugated Verb', json),
            # Jargon
            'jargon': self._get_literals_given_parent_type('Jargon::', json),
            # Solve Problem Triggers.
            'solve_problem_triggers': self._get_literals_given_parent_type('Solve Problem Triggers::', json)
        }
        
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
                path = self._info.find_path_to_trigger_key(word)
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
        counter = collections.Counter()
        for key in flattened_paths:
            counter[key] += 1
        for key, count in counter.most_common(): # Get ALL elements in counter.
            if count > 1:
                paths = remove_duplicates(paths, key) 
        # TODO:  Log how many paths were returned, and which ones.
        return paths
    
    def _map_triggers_to_paths(self):
        """Returns a mapping of a trigger to a set of keys that will lead to the value
        for the key that this trigger is mapped to.
        """
        # Get all triggers as a set.  This function will use 
        triggers = self._info.set_from_key_values(k_to_collect='Triggers')
        raise NotImplementedError("This function is not yet finished.")
       
    # Intent Functions.
    def _learn_about_topic(self, data):
        """Called when the intent is determined to be 'Learn About Topic'.
        """
        self._bot.say("It looks like you want to learn about a topic.")

    def _solve_problem(self, data):
        """Called when the intent is determined to be 'Solve Problem'.
        """
        self._bot.say("It looks like you want to solve a problem.")

    def _get_help(self, data):
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
            """Given a single path, get to an url.
            """
            u = self._info.traverse_keys(path)
            while not isinstance(u, str):   # Path might not lead to url yet.
                # If our path doesn't point to a key with its own url,
                # ask the user where to go from here.
                keys = list(u.keys())
                # We only need to ask when there is more than one potential key.
                if 1 < len(keys):
                    self._bot.acknowledge(path[len(path) - 1])
                    next = self._bot.give_options([k for k in u.keys()])
                    path.append(next)
                else:
                    path.append(keys[0])
                u = self._info.traverse_keys(path)
            return u

        # Check if the user triggered any links to the wiki page.
        paths = clarify_paths(data['paths'])
        if paths:
            urls = [get_ending_url(path) for path in paths]
            topics = [self._info.get_url_description(u) for u in urls]
            self._bot.acknowledge(topics)
            self._bot.suggest_multiple_urls(urls, topics)
        else:
            # Try StackExchange
            self._bot.say("Hmmm, I'm not sure the wiki can help.\nLet me see what I can find through stackoverflow.\n\n")
            #raise NotImplementedError("Querying stackoverflow is not yet implemented.")
            
    def _none_intent(self):
        self._bot.say("I'm sorry, I don't know what you're asking.")
        # "Help me understand what I can do for you?"
        # Give options on different intents, call that function with the original query or a new one, whichever makes more sense.
