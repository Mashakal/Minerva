import itertools
import requests
from urllib import parse
from enum import Enum, unique

from stackexchangeresponse import StackExchangeResponse
import webrequest as web


class QueryTypes(Enum):

    """Enum types for StackExchange queries."""

    Questions = '/'.join([StackExchangeQuery._version, 'questions'])
    Answers = '/'.join([StackExchangeQuery._version, 'answers'])
    Search = '/'.join([StackExchangeQuery._version, 'search'])
    AdvancedSearch = '/'.join([StackExchangeQuery._version, 'search', 'advanced'])

class StackExchangeQuery(object):
    _API_KEY = 'E3Ht0FN1L57M68Wk56e2RA(('    # API Key for Minerva, from StackExchange.com
    _version = '2.2'
    _netloc = 'api.stackexchange.com'
    _paths = {'questions': '/'.join([_version, 'questions']),
              'answers': '/'.join([_version, 'answers']),
              'search': '/'.join([_version, 'search']),
              'advanced_search': '/'.join([_version, 'search', 'advanced'])}

    def __init__(self, site, query_params=None):
        # See urllib.parse module for definitions of each segment.
        self.segments = {
            'scheme': 'https',
            'netloc': StackExchangeQuery._netloc,
            'path': None,
            'params': None,
            'query': None,
            'fragment': None
        }
        # We have a query string object to allow rich functionality in manipulating this query's url.
        self.query_string = StackExchangeQueryString(**query_params)
        self.set_site(site)
        self.query_string.add_pair('key', StackExchangeQuery._API_KEY)
    
    def build_full_url(self):
        """Calls urlunparse to get an url string of segments."""
        return parse.urlunparse(self._get_url_items())

    def _get_url_items(self):
        """Return segments in the the order as defined by urllib.parse."""
        self._build_url_items()
        order = ['scheme', 'netloc', 'path', 'params', 'query', 'fragment']
        return [self.segments[key] for key in order]
        
    def _build_url_items(self):
        # Update all segments.
        if not self.segments['path']:
            self.segments['path'] = QueryTypes.Search
        if not self.segments['params']:
            self.segments['params'] = ''
        if not self.segments['fragment']:
            self.segments['fragment'] = ''
        
        self.segments['query'] = self.query_string.get_full_string()

    def set_query_type(self, type):
        
        self.idAdded = False

    def set_site(self, site):
        """Sets the StackExchange site to query."""
        self.query_string.add_pair('site', site)

    def add_id(self, id):
        if not self.idAdded:
            self.segments['path'] = '/'.join([self.segments['path'], str(id)])
            self.idAdded = True
            return True
        return False

    def go(self):
        content = requests.get(self.build_full_url())
        self.response = StackExchangeResponse(content)

    
#region QueryString

MAX_TAGS = 5    # Per the stack exchange API.
MAX_PAGE_SIZE = 100


class StackExchangeQueryString:

    """A class for creating a StackExchange API query string."""

    def __init__(self, **kwargs):
        self.parameters = {}
        self.size = 0
        self._tag_count = 0
        # Default parameters.
        self.add_pair('site', 'stackoverflow')
        for k in kwargs:
            self.add_pair(k, kwargs[k])

    def __str__(self, indent_=4, sort_keys_=True):
        import json
        head = self.__repr__()
        body = json.dumps(self.parameters, indent=indent_, sort_keys=sort_keys_)
        return '\n'.join([head, body])

    def __iter__(self):
        for k in self.parameters:
            yield (k, self.parameters[k])

    def get(self):
        """A more abstract way of getting the query string as a list of key/value pairs."""
        return self.parameters

    def get_full_string(self):
        """Returns all parameters formatted as a query string appropriate for the StackExchange API.  
        If nothing has been added, returns the empty string"""
        s = map(lambda t: "&{}={}".format(*t), self)
        return ''.join(s)[1:]

    def add_pair(self, key, value):
        """Adds a single item to parameters.
       
        If 'key' is already found in parameters, its value is updated to 'value'.
        
        """
        key, value = str(key), str(value)
        if not key in self.parameters:
            if key == 'tagged':
                self.add_tags(value.split(';'))
            elif key == 'pagesize':
                self._validate_page_size(int(value))
            self.size += 1
            self.parameters[key] = value
        else:
            self.set_pair(key, value)

    def remove_pair(self, key):
        """Deletes key from parameters.  No action if key is not in parameters."""
        if key in self.parameters:
            self.parameters.pop(key)
            self.size -= 1

    def retrieve(self, key):
        """Get's the passed in key's associated value.  None if the key is not found."""
        try:
            return self.parameters[key]
        except KeyError:
            return None

    def set_pair(self, key, value):
        """Updates the value of a parameter key.  Will add the key/value pair if the key does not exist."""
        if key in self.parameters:
            self.parameters[key] = str(value)
        else:
            self.add_pair(key, value)

    def add_tag(self, tag):
        """Accepts a single string to add to the tagged key.
        
        Tags are within the same query string parameter, and require a unique 
        method for being added.
        
        """
        try:
            tagged = self.parameters["tagged"]
        except KeyError:
            self.parameters['tagged'] = tag
        else:
            self.parameters['tagged'] = ''.join([tagged, ';', tag])
        finally:
            self._tag_count += 1

    def add_tags(self, tags):
        """Add a list of tags to the query string."""
        iter_ = tags if isinstance(tags, list) else [tags]
        tags_str = ';'.join([t for t in iter_])
        self.add_tag(tags_str)
            
    def remove_tag(self, tag):
        """Removes the given tag from the 'tagged' key.  True on success.
        
        Returns False when there is no 'tagged' key or the given tag does 
        not appear in its value string.
        
        """
        try:
            tags = self.retrieve('tagged').split(';') # Raises AttributeError.
            tags.remove(tag)    # Raises ValueError.
        except (ValueError, AttributeError):
            pass
        else:
            self.set_pair('tagged', ';'.join(tags))
            self._tag_count -= 1
            if not self._tag_count:
                # Delete the 'tagged' key if there are no more tags.
                self.remove_pair('tagged')
        
    def _validate_page_size(self, num):
        """Raises a ValueError when the page size is not within bounds."""
        if not 0 < num <= MAX_PAGE_SIZE:
            raise ValueError('Pagesize must be between 1 and 100.')


#segments = {
#    'scheme': 'https',
#    'netloc': 'api.stackexchange.com',
#    'path': '2.2/questions',
#    'params': '',
#    'query': 'order=desc&sort=activity&site=stackoverflow',
#    'fragment': ''
#}

def main():
    qs = StackExchangeQueryString(**{'pagesize': 100})
    qs.add_tag('ptvs')
    qs.remove_tag('ptvs')
    print(qs.get_full_string())
    qs.add_tags(['debugging', 'c#', 'python'])
    print(qs.get_full_string())
    qs.remove_tag('python')
    print(qs.get_full_string())
    qs.remove_pair('tagged')
    print(qs.get_full_string())
    qs.add_pair('tagged', 'ptvs')
    print(qs.get_full_string())
    qs.add_tags(['debugging', 'c#', 'python'])
    print(str(qs))

if __name__ == "__main__":
    main()