#!/usr/bin/env python

import sys


class StackExchangeQuery(object):
    BASE_URL = 'https://api.stackexchange.com'
    VERSION = '2.2'
    def __init__(self, params = None):
        self.startURL = StackExchangeQuery.BASE_URL + "/" + StackExchangeQuery.VERSION
        self.parameters = Parameters(params)
    
    def buildQueryString(self):
        pass



class Parameters(object):
    """A class for creating query parameters."""

    def __init__(self, params = None):
        """Accepts an arbitrary number of key-value pairs to be added to the parameters object being created."""
        self.parameters = {}
        self._size = 0
        if params:
            for k, v in params.items():
                self.addParameter(k, v)
        
    def getParameterString(self):
        """Returns all parameters formatted as a single query string.  If there are no parameters, returns the empty string"""
        s = ''
        for k, v in self.parameters.items():
            s += '&' + str(k) + "=" + str(v) if s else str(k) + "=" + str(v)
        return s

    def addParameter(self, key, value):
        """Adds a single parameter to parameters.  Returns True if successful and False otherwise.  False indicates the key was already found within parameters."""
        if not self.parameters.get(key, False):
            self._size += 1
            self.parameters[key] = value
            return True
        return False

    def getSize(self):
        return self._size

    



st = {
    "tagged": "ptvs",
    "pagesize": "1"
}

query = StackExchangeQuery(st)
print(query.parameters.getParameterString())
print(query.parameters.getSize())