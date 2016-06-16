# Constants.
MAX_TAGS = 5    # Per the stack exchange API.
MAX_PAGE_SIZE = 100

class StackExchangeQueryString(object):
    """A class for creating a StackExchange API query string."""

    def __init__(self, params = None):
        """Accepts an optional dictionary whose key/value pairs that are converted into a 
        StackExchange API query string."""
        self.parameters = {}
        self._size = 0
        self._tagCount = 0
        # Default parameters.
        self.addPair('site', 'stackoverflow')
        if params:
            # Make sure all params are strings.
            # QUESTION:  Is this a requirement given python's coercion?
            for k, v in params.items():
                self.addPair(str(k), str(v))
    
    def __dict__(self):
        """Returns all key/value pairs."""
        return self.parameters

    def get(self):
        """A more abstract way of getting the query string as a list of key/value pairs."""
        return self.__dict__()

    def getFullString(self):
        """Returns all parameters formatted as a query string appropriate for the StackExchange API.  
        If nothing has been added, returns the empty string"""
        s = ''
        for k, v in self.parameters.items():
            s += '&' + k + "=" + v if s else k + "=" + v
        return s

    def addPair(self, key, value):
        """Adds a single item to parameters.  Returns True if successful and False if the key was 
        already found within parameters."""
        key = str(key)
        value = str(value)
        if not key in self.parameters:
            # TODO:  Make this better, we are currently overriding the additions a few lines down and addTag in this context is simply counting the number of tags.
            if key == 'tagged': [self.addTag(t) for t in value.split(';')]
            elif key == 'pagesize': self.__validatePageSize(int(value))
            self._size += 1
            self.parameters[key] = value
            return True
        else:
            self.setPair(key, value)
        return False

    def removePair(self, key):
        """Deletes the given key from parameters dict.  Returns True on success, otherwise False."""
        if key in self.parameters:
            self.parameters.pop(key)
            self._size -= 1
            return True
        return False

    def retrieve(self, key):
        """Get's the passed in key's associated value.  Returns False if the key is not found."""
        try:
            return self.parameters[key]
        except KeyError:
            return False

    def setPair(self, key, value):
        """Updates the value of a parameter key.  Will add the key/value pair if the key does not exist."""
        if key in self.parameters:
            self.parameters[key] = value
            return True
        else:
            self.addPair(key, value)

    def getSize(self):
        """Returns the number of keys in the query string."""
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

    def addTags(self, tags):
        """Add a list of tags to the query string."""
        if type(tags) is str:
            self.addTag(tags)
        else:
            for tag in tags:
                self.addTag(tag)

    def removeTag(self, tag):
        """Removes the given tag from the 'tagged' key.  Will return True on success and False if there 
        is no 'tagged' key or the given tag does not appear in its value string."""
        try:
            tags = self.retrieve('tagged').split(';')
            tags.remove(tag)
            self.setPair('tagged', ';'.join(tags))
            self._tagCount -= 1
            if not self._tagCount: print(self.removePair('tagged'))   # Delete the 'tagged' key if there are no more tags.
            return True
        # ValueError for when tag is not in tags.  AttributeError for when 'tagged' key doesn't exist.
        except (ValueError, AttributeError):
            return False


    def __validatePageSize(self, num):
        if not 0 < num <= MAX_PAGE_SIZE:
            raise ValueError('Pagesize must be between 1 and 100.')