from functools import wraps
import sys


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
        printSmart(self._json)

    def getResult(self, resultIndex):
        return self._results[resultIndex]


class StackExchangeResult(object):
    """A base class for defining common response item methods and attributes."""

    def __init__(self, dic):
        self._dic = dic   # Dictionary holding this item's contents.
    
    def get(self):
        return self._dic
        
    def getValue(self, key):
        return self._dic[key]

    def printAllPairs(self):
        for key in self._dic:
            print(key.upper()),
            printSmart(self._dic[key], depth=1)