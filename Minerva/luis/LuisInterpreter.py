from InfoManager import InfoManager

# For development purposes only:
from Essentials import enterAndExitLabels, printSmart

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
            'literals': self._get_literals(json),
            'types': self._get_types(json),
            'keywords': self._get_all_literals_of_type('Keyword', json),
            'intent': self._get_top_scoring_intent(json),
        }

        o['root_keys'] = self._info.getAllRootKeys(o['keywords'])

        return o

    def _get_help(self, json):
        """Called from function 'analyze' when the intent of a LUIS query is determined
        to be 'Get Help'.
        """
        data = self._format_data(json)
        
        # Print some debugging information.
        print("QUERY: {0}".format(json['query']))
        for i in range(len(data['literals'])):
            print("%s: %s" % (data['types'][i].upper(), data['literals'][i]))
        print()

        # Help with a VS feature.
        if "Visual Studio Feature" in data['types']:
            self._process_visual_studio_feature(data)

        # Help with installation.
        elif "Installation" in data['root_keys']:
            self._bot.acknowledge('installation')
            self._bot.say("This link has the best information about installing PTVS \nand some common packages: {0}.".format(self._info.links['Installation']))
            # TODO:  What if they want help with a different type of installation.

        # Help with feature matrix.
        elif "Feature Matrix" in data['root_keys']:
            # This assumes the Project System in the query is the same as the current module.
            if "Project System" in data['types']:
                self._bot.say("You can learn about {0}'s features here: {1}".format(self._info.name, self._info.get_url('Feature Matrix')))
            else:
                ans = self._bot.ask("Are you asking about features of {0}?".format(self._info.name))
                if ans in _YES_WORDS:
                    self._bot.say("You can learn about {0}'s features here: {1}".format(self._info.name, self._info.links['Feature Matrix']))
                else:
                    # TODO:  Make this better.
                    feature = input("What feature are you asking about?\n>>> ")
                    data['literals'].append(feature)
                    data['types'].append("Visual Studio Feature")
                    rootKey = self._info.literalToKey(feature)
                    if rootKey:
                        data['root_keys'].append(rootKey)
                    data['root_keys'] = self._info.getAllRootKeys(data['keywords'])
                    self._process_visual_studio_feature(data)

        # General help.
            # Feature matrix, installation, overview videos, contributing, build instructions, tutorials.
            # Can we make this a catch-all else statement, at the end?  We will see...

        # Help with editing:
        elif "Editing" in data['root_keys']:
            self._bot.acknowledge('Editing')
            url = self._info.get_url('Editing')
            self._bot.suggest_url(url)
            
                    
    def _process_visual_studio_feature(self, data):
        # Get a list of keys in order of traversal to a suggested URL.
        key_path = self._find_path_to_link(data)
        url = self._info.get_url(key_path)
        self._bot.suggest_url(url)

    def _find_path_to_link(self, data):
        """Obtain a list of keys that will allow traversal through
        a dictionary.  The keys will point to an url.
        """
        def determine_key_feature(literals, types):
            """A helper function for _find_path_to_link.  Determines the key feature
            for which the user is querying.  Will validate with the user when
            more than one feature is found.  A key freature is defined as a root level
            feature.
            """
            # Extract all the literals of type Visual Studio Feature found in the query.
            features = [literals[i] for i, t in enumerate(types) if t == "Visual Studio Feature"]
            if len(features) > 1:
                # Clarify a feature when there is more than one found.
                for feature in features:
                    # Translate it to match the corresponding key within KEY_MAP.
                    key_feature = self._info.literalToKey(feature)    # None, if unsuccesful.
                    if key_feature:
                        ans = self._bot.ask("Are you asking about {0}?".format(key_feature.lower()))
                        if ans.lower() in _YES_WORDS:
                            return key_feature
                    else:
                        self._bot.say("I am having trouble mapping {0}.".format(feature))
                        # TODO: LOG
            elif len(features) == 1:
                key_feature = self._info.literalToKey(features[0])
                if key_feature:
                    return key_feature

            # If no features have been returned (either none were found or none were accepted by the user).
            self._bot.say("I can't seem to figure out which feature you're asking about.")
            self._bot.say("I'll get you a link to the wiki page.")
            # TODO: LOG
            return "WIKI"   # Default to the wiki's page when mapping to a feature fails.

        def determine_subkey(key_feature, keywords):
            """A Helper function for _find_path_to_link.  Determines the appropriate sub key 
            given a key feature and a list of keywords.
            """
            refined_keys = self._info.getRefinedKeys(key_feature, keywords)
            if refined_keys:
                if 1 < len(refined_keys):
                    for subkey in refined_keys:
                        ans = self._bot.ask("Is this about {0}?".format(subkey))
                        if ans.lower() in _YES_WORDS:
                            return subkey
                        else:
                            # TODO: LOG
                            pass
                else:
                    return refined_keys[0]
            return None

        path_to_link = []

        # Determine the root key.
        key_feature = determine_key_feature(data['literals'], data['types'])

        # Determine the subkey, if there is one.
        if key_feature:
            path_to_link.append(key_feature)
            # Use any keywords found by LUIS to determine if there are likely subkeys.
            subkey = determine_subkey(key_feature, data['keywords'])
            if not subkey:
                self._bot.acknowledge(key_feature)
                if not isinstance(self._info.links[key_feature], str):
                    path_to_link.append("BASE_URL") # TODO:  This is risky, let's make sure it doesn't fail.
                return path_to_link
            else:
                path_to_link.append(subkey)
                self._bot.acknowledge(subkey)
                # Determine if any more filtering needs done (do our current keys point to a url?)
                v = self._info.traverse_keys(path_to_link)
                if not isinstance(v, str):  # TODO:  Is this safe as an if statement -> will you ever need to find more than one additional key?
                    # Should probably always be a dictionary, but check just in case...
                    if isinstance(v, dict):
                        keys = list(v.keys())
                        next_key = self._bot.clarify(keys)
                        path_to_link.append(next_key)
                    else:
                        # TODO: LOG
                        print("Expected a dictionary but got type: {0}".format(type(v)))
                    return path_to_link
        else:
            print("There was a problem determining your feature.  I'll send you to the wiki.")
            # TODO: LOG
            return ['WIKI']

    def _undefined(self):
        return "I'm sorry, I don't know what you're asking."