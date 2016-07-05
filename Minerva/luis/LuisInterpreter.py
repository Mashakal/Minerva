from InfoManager import InfoManager
from abc import ABCMeta, abstractmethod
import PTVS

# For development purposes only:
from Essentials import enterAndExitLabels, printSmart


YES_WORDS = ['yes', 'yeah', 'okay', 'ok', 'k', 'y', 'ya', 'right', 'correct', 'that\'s right', 'sure', 'for sure']
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
    def __init__(self, system):
        # Map an intent to a function.
        self.info = InfoManager(system)
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

    #def _findRootKey(self, 

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
            # Get a list of keys in order of traversal to a suggested URL.
            keyPath = self.findPathToLink(data)
            # Use each key to find the URL.
            v = self.info.links[keyPath[0]]
            for i in range(1, len(keyPath)):
                v = v[keyPath[i]]
            print("I suggest you visit this site: {0}".format(v))

        # Help with installation.
        elif "Installation" in data['rootKeys']:
            print("I will be glad to help you with installation.")
            print("This link has the best information about installing PTVS \nand some common packages: {0}.".format(self.info.links['Installation']))
            # Determine the type of the thing that's needing to be installed.
                # How to distinguish between installing PTVS/Project System rather than other item (MahApps, NumPy, 
            # Do the work to get help for that.

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
            # Extract all the Visual Studio Features found in the query.
            features = [literals[i] for i, t in enumerate(types) if t == "Visual Studio Feature"]
            if len(features) > 1:
                # Clarify a feature when there is more than one found.
                for feature in features:
                    # Translate it to match the corresponding key within KEY_MAP.
                    keyFeature = self.info.literalToKey(feature)    # None, if unsuccesful.
                    if keyFeature:
                        ans = input("Are you asking about {0}?\n>>> ".format(keyFeature.lower()))
                        if ans.lower() in YES_WORDS:
                            return keyFeature
                    else:
                        print("I am having trouble mapping {0}.".format(feature))
                        # TODO: LOG
            elif len(features) == 1:
                keyFeature = self.info.literalToKey(features[0])
                if keyFeature:
                    return keyFeature

            # If no features have been returned (either none were found or none were accepted by the user).
            print("I can't seem to figure out which feature you're asking about.")
            print("I'll get you a link to the wiki page.")
            # TODO: LOG
            return "WIKI"   # Default to the wiki's page when mapping to a feature fails.

        def determineSubKey(keyFeature, keywords):
            """Determines the appropriate sub key given a key feature and a list of keywords.
            """
            refinedKeys = self.info.getRefinedKeys(keyFeature, keywords)
            if refinedKeys:
                if 1 < len(refinedKeys):
                    for subkey in refinedKeys:
                        ans = input("Is this about {0}?\n>>> ".format(subkey))
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
                print("I can definitely help you with {0}.".format(keyFeature))
                if type(self.info.links[keyFeature]) is not str:
                    # TODO:  This is risky, let's make sure it doesn't fail.
                    pathToLink.append("BASE_URL")
                return pathToLink
            else:
                pathToLink.append(subkey)
                print("I can definitely help you with {0}.".format(subkey))
                # Determine if any more filtering needs done (do our current keys point to a url?)
                v = self.info.links[pathToLink[0]]
                # Find the last value we have a path to.
                for i in range(1, len(pathToLink)):
                    v = v[pathToLink[i]]
                # If the value is not a string (a url), filter some more.
                if type(v) is not str:
                    # Should probably always be a dictionary, but check just in case...
                    if type(v) is dict:
                        keys = list(v.keys())
                        print("Which of these is more pertinent in your case?")
                        for i in range(len(keys)):
                            print(" {0}: {1}".format(i + 1, keys[i]))
                        index = input(">>> ")
                        try:
                            index = int(index)
                            #print("Great! I suggest you visit this site:\n\t{0}".format(v[keys[index - 1]]))
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



    