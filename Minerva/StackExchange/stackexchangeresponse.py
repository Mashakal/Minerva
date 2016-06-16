#!user/bin/env python
from functools import wraps
import sys

def enterAndExitLabels(func):
    @wraps(func)
    def wrap(*args):
        print("Entering", func.__module__ +':'+ func.__name__)
        func(*args)
        print("Exiting", func.__module__ +':'+ func.__name__)
    return wrap


class StackExchangeResponse(object):
    """Holds the data for a StackExchange API response."""
    def __init__(self, content):
        self._content = content   # The response content returned by requests.get.
        self._json = content.json()
        self._results = []    # A list of StackExchangeItems or its derivations.
        for q in self._json['items']:
            self._results.append(StackExchangeResult(q))
        self.resultCount = len(self._results)
        

    def printResult(self, resultIndex):
        self._results[resultIndex].getAllValues()

    def printAll(self):
        StackExchangeResult.printSmart(self._json)

    def getResult(self, resultIndex):
        return self._results[resultIndex]


class StackExchangeResult(object):
    """An base class for defining common response item methods and attributes."""

    def __init__(self, dic):
        self._dic = dic   # Dictionary holding this item's contents.
    
    def get(self):
        return self._dic

    def getValue(self, key):
        return self._dic[key]

    def printAllPairs(self):
        for key in self._dic:
            print(key.upper()),
            self.printSmart(self._dic[key], depth=1)

    @classmethod
    def printSmart(self, item, depth = 0):
        if type(item) in [str, int, float, bool]:
            print(' ' * (depth * 3) + str(item).upper())
            return
        newDepth = depth + 1
        if isinstance(item, list):
            for el in item:
                self.printSmart(el, depth)
        elif isinstance(item, dict):
            for key in item:
                print(' ' * (depth * 3) + str(key).upper())
                self.printSmart(item[key], depth=newDepth)
        else:
            s = 'printSmart isn\'t sure what to do with the type: ' + str(type(item))
            self.printSmart(s, depth=depth)