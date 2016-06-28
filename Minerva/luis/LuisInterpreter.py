from abc import ABCMeta, abstractmethod
from Essentials import enterAndExitLabels

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

    def analyze(self):
        """Analyzes the json returned from a call to the base LuisClient class's method, query_raw."""
        # Code to analyze goes here.
        raise NotImplementedError


class PythonLuisInterpreter(AbstractLuisInterpreter):
    """Interprets quetions for the Python Tools for Visual Studio help bot."""

    # Map an intent to a function.
    def __init__(self):
        self._STRATAGIES = {
            'Get Help': self.__getHelp,
            'undefined': self.__undefined
        }

    def analyze(self, json):
        intent = self.__getTopScoringIntent(json)
        return self._STRATAGIES[intent](json)

    def __getTopScoringIntent(self, json):
        try:
            return json['intents'][0]['intent']
        except KeyError:
            return 'undefined'

    def __getHelp(cls, json):
        return "I will be happy to help."

    def __undefined(cls):
        return "I'm sorry, I don't know what you're asking."



    