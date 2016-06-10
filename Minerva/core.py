#!/usr/bin/env python

import sys
import re

# IDEAS - Incorporate all VS features into the bot.
#       - Answers can have tags so the user can easily understand the contents of each piece of information.

# Constants.
MAX_TAGS = 5    # Per the stack exchange API.

class StackExchangeQuery(object):
    BASE_URL = 'https://api.stackexchange.com'
    VERSION = '2.2'

    def __init__(self, params = None):
        self.startURL = StackExchangeQuery.BASE_URL + "/" + StackExchangeQuery.VERSION
        self.parameters = Parameters(params)
    
    def buildQueryString(self):
        pass


# NOTE:  This class should be standalone, outside of project Minerva (use it as a base class for StackExchange customized parameter class.)
class Parameters(object):
    """A class for creating query parameters."""

    def __init__(self, params = None):
        """Accepts an optional dictionary whose key/value pairs are to be added to this object's parameters variable."""
        self.parameters = {}
        self._size = 0
        self._tagCount = 0
        if params:
            # Make sure all params are strings.
            # QUESTION:  Is this a requirement given python's coercion?
            for k, v in params.items():
                self.addParameter(str(k), str(v))

    def get(self):
        # QUESTION:  Is there a way to do this with python?
        # QUESTION:  Would it be better to return a copy of this dictionary?
        return self.parameters
        
    def getAsQueryString(self):
        """Returns all parameters formatted as a single query string.  If there are no parameters, returns the empty string"""
        s = ''
        for k, v in self.parameters.items():
            s += '&' + k + "=" + v if s else k + "=" + v
        return s

    def addParameter(self, key, value):
        """Adds a single item to parameters.  Returns True if successful and False if the key was already found within parameters."""
        if not key in self.parameters:
            if key == 'tagged': [self.addTag(t) for t in value.split(';')]
            self._size += 1
            self.parameters[key] = value
            return True
        return False

    def deleteParameter(self, key):
        """Deletes the given key from parameters dict.  Returns True on success, otherwise False."""
        if key in self.parameters:
            self.parameters.pop(key)
            self._size -= 1
            return True
        return False

    def getParameter(self, key):
        """Get's the passed in key's associated value.  Returns False if the key is not found."""
        try:
            return self.parameters[key]
        except KeyError:
            return False

    def setParameter(self, key, value):
        # QUESTION:  Is it better to have this function fail if the key does not exist, or add the key/value pair to parameters?
        """Updates the value of a parameter key.  Will add the key/value pair if the key does not exist."""
        self.parameters[key] = value

    def getSize(self):
        return self._size

    def addTag(self, tag):
        """Tag's are within the same query string parameter, and require a unique method for being added.  
        Accepts a single string to add to the tagged key.  Returns True on success and False otherwise."""
        if 0 < self._tagCount < MAX_TAGS:
            self.parameters["tagged"] += ";" + tag
            self._tagCount += 1
            return True
        elif 0 == self._tagCount:
            self.parameters['tagged'] = tag
            self._tagCount += 1
            return True
        return False

    def removeTag(self, tag):
        """Removes the given tag from the 'tagged' key.  Will return True on success and False if there is no 'tagged' key or the given tag does not appear in its value string."""
        try:
            tags = self.getParameter('tagged').split(';')
            tags.remove(tag)
            self.setParameter('tagged', ';'.join(tags))
            self._tagCount -= 1
            if not self._tagCount: print("Delete Success:", self.deleteParameter('tagged'))   # Delete the 'tagged' key if there are no more tags.
            return True
        # ValueError for when tag is not in tags.  AttributeError for when 'tagged' key doesn't exist.
        except (ValueError, AttributeError) as e:
            return False




# Here for testing/debugging.
params = {"tagged":"ptvs;python"}
instance = Parameters(params)
