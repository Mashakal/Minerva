from InfoManager import InfoManager
from Bot import VSBot
from abc import ABCMeta, abstractmethod
import PTVS

# For development purposes only:
from Essentials import enterAndExitLabels, printSmart

# Constants
# These may be better off in the Bot module.
YES_WORDS = ['yes', 'yeah', 'okay', 'ok', 'k', 'y', 'ya', 'right', 'correct', "that's right", 'sure', 'for sure']
NO_WORDS = ['no', 'n', 'nah', 'nope', 'negative']

class AbstractLuisInterpreter(object):
    """An interface for creating extension specific interpreters for Visual Studio."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def analyze(self, json):
        pass

class BaseLuisInterpreter(AbstractLuisInterpreter):
    """A base class for all interpreters."""
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def analyze(self, json):
        """Analyzes the json returned from a call to the base LuisClient class's method, query_raw."""
        raise NotImplementedError("Function analyze has not yet been customized.")

    @classmethod
    def getTopScoringIntent(cls, json):
        try:
            return json['intents'][0]['intent']
        except LookupError:
            return 'undefined'

    @classmethod
    def getLiterals(cls, json):
        return [e['entity'] for e in json['entities']]

    @classmethod
    def getTypes(cls, json):
        return [e['type'] for e in json['entities']]

    @classmethod
    def getAllLiteralsOfType(cls, t, json):
        return [e['entity'] for e in json['entities'] if e['type'] == t]

class ProjectSystemLuisInterpreter(BaseLuisInterpreter):
    """Interprets questions for language specific project systems of Visual Studio
    as a part of a help bot.
    """
    def __init__(self, project_system):
        self.info = InfoManager(project_system)
        self.bot = VSBot()
        
        # Maps an intent to a function.
        self._STRATAGIES = {
            'Get Help': self._getHelp,
            'undefined': self._undefined
        }

    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        intent = self.getTopScoringIntent(json)
        return self._STRATAGIES[intent](json)

    def _formatData(self, json):
        """Formats the raw json into a more easily managable dictionary."""
        o = {
            'literals': self.getLiterals(json),
            'types': self.getTypes(json),
            'keywords': self.getAllLiteralsOfType('Keyword', json),
            'intent': self.getTopScoringIntent(json),
        }
        o['rootKeys'] = self.info.getAllRootKeys(o['keywords'])
        return o

    def _getHelp(self, json):
        """Called from function 'analyze' when the intent of a LUIS query is determined
        to be 'Get Help'.
        """
        data = self._formatData(json)
        
        # Print some debugging information.
        print()
        print("Query: {0}".format(json['query']))
        for i in range(len(data['literals'])):
            print("%s: %s" % (data['types'][i].upper(), data['literals'][i]))
        print()

        # Help with a VS feature.
        if "Visual Studio Feature" in data['types']:
            self.process_visual_studio_feature(data)

        # Help with installation.
        elif "Installation" in data['rootKeys']:
            self.bot.acknowledge('installation')
            self.bot.say("This link has the best information about installing PTVS \nand some common packages: {0}.".format(self.info.links['Installation']))
            # TODO:  What if they want help with a different type of installation.

        # Help with feature matrix.
        elif "Feature Matrix" in data['rootKeys']:
            if "Project System" in data['types']:
                self.bot.say("You can learn about {0}'s features here: {1}".format(self.info.name, self.info.get_url('Feature Matrix')))
            else:
                ans = self.bot.ask("Are you asking about features of {0}?".format(self.info.name))
                if ans in YES_WORDS:
                    self.bot.say("You can learn about {0}'s features here: {1}".format(self.info.name, self.info.links['Feature Matrix']))
                else:
                    # TODO:  Make this better.
                    feature = input("What feature are you asking about?\n>>> ")
                    data['literals'].append(feature)
                    data['types'].append("Visual Studio Feature")
                    rootKey = self.info.literalToKey(feature)
                    if rootKey:
                        data['rootKeys'].append(rootKey)
                    data['rootKeys'] = self.info.getAllRootKeys(data['keywords'])
                    self.process_visual_studio_feature(data)

        # General help.
            # Feature matrix, installation, overview videos, contributing, build instructions, tutorials.
            # Can we make this a catch-all else statement, at the end?  We will see...

        # Help with editing:
        elif "Editing" in data['rootKeys']:
            self.bot.acknowledge('Editing')
            url = self.info.get_url('Editing')
            self.bot.suggest_url(url)
            
                    
    def process_visual_studio_feature(self, data):
        # Get a list of keys in order of traversal to a suggested URL.
        keyPath = self.findPathToLink(data)
        url = self.info.get_url(keyPath)
        self.bot.suggest_url(url)

    def findPathToLink(self, data):
        """A meaty helper function for _getHelp.  Attempts to find the key
        feature and any subcategory of that feature and returns a list of
        keys that will lead to the link for the feature requested by the
        user.
        """
        def determineKeyFeature(literals, types):
            """A helper function for findPathToLink.  Determines the key feature
            for which the user is querying.  Will validate with the user when
            more than one feature is found.
            """
            # Extract all the literals of type Visual Studio Feature found in the query.
            features = [literals[i] for i, t in enumerate(types) if t == "Visual Studio Feature"]
            if len(features) > 1:
                # Clarify a feature when there is more than one found.
                for feature in features:
                    # Translate it to match the corresponding key within KEY_MAP.
                    keyFeature = self.info.literalToKey(feature)    # None, if unsuccesful.
                    if keyFeature:
                        ans = self.bot.ask("Are you asking about {0}?".format(keyFeature.lower()))
                        if ans.lower() in YES_WORDS:
                            return keyFeature
                    else:
                        self.bot.say("I am having trouble mapping {0}.".format(feature))
                        # TODO: LOG
            elif len(features) == 1:
                keyFeature = self.info.literalToKey(features[0])
                if keyFeature:
                    return keyFeature

            # If no features have been returned (either none were found or none were accepted by the user).
            self.bot.say("I can't seem to figure out which feature you're asking about.")
            self.bot.say("I'll get you a link to the wiki page.")
            # TODO: LOG
            return "WIKI"   # Default to the wiki's page when mapping to a feature fails.

        def determineSubKey(keyFeature, keywords):
            """Determines the appropriate sub key given a key feature and a list of keywords.
            """
            refinedKeys = self.info.getRefinedKeys(keyFeature, keywords)
            if refinedKeys:
                if 1 < len(refinedKeys):
                    for subkey in refinedKeys:
                        ans = self.bot.ask("Is this about {0}?".format(subkey))
                        if ans.lower() in YES_WORDS:
                            return subkey
                        else:
                            # TODO: LOG
                            pass
                else:
                    return refinedKeys[0]
            return None

        keyFeature = subkey = None
        pathToLink = [] # Holds the path to the link in terms of keys within the PTVS.LINKS dict.

        # Determine the root key.
        keyFeature = determineKeyFeature(data['literals'], data['types'])
        # Determine the subkey, if there is one.
        if keyFeature:
            pathToLink.append(keyFeature)
            # Use any keywords found by LUIS to determine if there are likely subkeys.
            subkey = determineSubKey(keyFeature, data['keywords'])
            if not subkey:
                self.bot.acknowledge(keyFeature)
                if not isinstance(self.info.links[keyFeature], str):
                    # TODO:  This is risky, let's make sure it doesn't fail.
                    pathToLink.append("BASE_URL")
                return pathToLink
            else:
                pathToLink.append(subkey)
                self.bot.acknowledge(subkey)
                # Determine if any more filtering needs done (do our current keys point to a url?)
                v = self.info.traverse_keys(pathToLink)
                if not isinstance(v, str):
                    # Should probably always be a dictionary, but check just in case...
                    if isinstance(v, dict):
                        keys = list(v.keys())
                        print("Which of these is more pertinent in your case?")
                        for i in range(len(keys)):
                            print(" {0}: {1}".format(i + 1, keys[i]))
                        index = input(">>> ")
                        try:
                            index = int(index)
                            pathToLink.append(keys[index - 1])
                        except (ValueError, IndexError):
                            print("I'm sorry, that wasn't a valid selection.")
                    else:
                        # TODO: LOG
                        print("Expected a dictionary but got type: {0}".format(type(v)))
                    return pathToLink
        else:
            print("There was a problem determining your feature.  I'll send you to the wiki.")
            # TODO: LOG
            return ['WIKI']

    def _undefined(self):
        return "I'm sorry, I don't know what you're asking."



    