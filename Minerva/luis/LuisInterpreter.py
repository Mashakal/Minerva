from abc import ABCMeta, abstractmethod
from Essentials import enterAndExitLabels
import PTVS

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
    def getAllLiteralsOfType(cls, type, json):
        return [e['entity'] for e in json['entities'] if e['type'] == type]

class PythonLuisInterpreter(BaseLuisInterpreter):
    """Interprets quetions for the Python Tools for Visual Studio help bot."""

    def __init__(self):
        # Map an intent to a function.
        self._STRATAGIES = {
            'Get Help': self._getHelp,
            'undefined': self._undefined
        }
        self.response = ""

    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        self.response = ""
        intent = self.getTopScoringIntent(json)
        return self._STRATAGIES[intent](json)

    def _getHelp(self, json):
        """Called from function 'analyze' when the intent of a LUIS query is determined
        to be 'Get Help'.
        """
        literals = self.getLiterals(json)
        types = self.getTypes(json)
        keywords = self.getAllLiteralsOfType('Keyword', json)
        for i in range(len(literals)):
            print("%s - %s" % (types[i], literals[i]))

        if "Visual Studio Feature" in types:
            self.evaluateFeatureQuery(literals, types, keywords)

    def evaluateFeatureQuery(self, literals, types, keywords):
        """Handles the processing of a query that contains a Visual Studio Feature entity.
        """
        feature = self.literalFromType("Visual Studio Feature", literals, types)
        keyFeature = PTVS.literalToKey(feature)
        if keyFeature:
            print("I can definitely help you with {0}.\n".format(keyFeature.lower()))
            # Evaluate the keywords for a more defined feature.
            refinedKeys = PTVS.getRefinedKeys(keyFeature, keywords)
        if refinedKeys:
            for index, value in enumerate(refinedKeys):
                r = input("Are you asking about {0}? Y/N".format(value))
                if 'Y' == r.upper():
                     refined = PTVS.LINKS[keyFeature][value]
        if refined:
            if type(refined) is dict:
                keys = refined.keys()
                items = refined.values()
                print("Okay, which is more pertinent to what you're looking for?")
                for i in range(len(items)):
                    print("{0}: {1}".format(i + 1, items[i]))
                index = input()
                try:
                    index = int(index)
                    print("I suggest you visit this site: {0}".format(refined[keys[index]]))
                except IndexError:
                    print("That was not a valid selection.")



    def literalFromType(self, type, literals, types):
        """Returns the literal string for the first of 'type' found within types."""
        i = types.index(type)
        return literals[i]

    def _undefined(self):
        return "I'm sorry, I don't know what you're asking."



    