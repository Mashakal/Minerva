import requests
from urllib import parse
from enum import Enum, unique

from stackexchangeresponse import StackExchangeResponse


class StackExchangeQuery:
    _API_KEY = 'E3Ht0FN1L57M68Wk56e2RA(('    # API Key for Minerva, from StackExchange.com
    _version = '2.2'
    _netloc = 'api.stackexchange.com'

    def __init__(self, site, query_params={}):
        # See urllib.parse module for definitions of each segment.
        self.segments = {
            'scheme': 'https',
            'netloc': StackExchangeQuery._netloc,
            'path': None,
            'params': None,
            'query': None,
            'fragment': None
        }

        # Query_string object for manipulating query segment.
        self.query_string = StackExchangeQueryString(**query_params)
        # Universal (in terms of paths) default query parameters.
        self.query_string.add_param('site', site)
        self.query_string.add_param('key', StackExchangeQuery._API_KEY)
        self.query_string.add_param('nottagged', 'pycharm')
        #self.query_string.add_param('filter', 'withbody') # Add withbody filter when searching the body is implemented.

        # IDs are added to the path when the URL is built.
        self._ids = []

        # Query path will be converted to a string when URL is built.
        self._query_path = None

    def build_full_url(self):
        """Calls urlunparse to get an url string of segments."""
        return parse.urlunparse(self._get_url_items())

    def _get_url_items(self):
        """Return segments in the the order compliant with urllib.parse."""
        self._build_url_items()
        order = ['scheme', 'netloc', 'path', 'params', 'query', 'fragment']
        return [self.segments[key] for key in order]

    def _build_url_items(self):
        """Make sure all the segments are updated to their appropriate values."""
        if not self._query_path:
            self._query_path = QueryPaths.Search
        if not self.segments['params']:
            self.segments['params'] = ''
        if not self.segments['fragment']:
            self.segments['fragment'] = ''
        self.segments['query'] = self.query_string.get_full_string()
        
        # Further maintenance with the path segment.
        path = self._query_path.value['path']
        self.segments['path'] = '/'.join([path, ';'.join(self._ids)])

    def set_query_path(self, query_path):
        """Set the query path for the SE API request."""
        if not isinstance(query_path, QueryPaths):
            raise ValueError("Query path must be of type QueryPaths, not: {}".format(type(query_path)))
        
        if self._query_path:
            for default in self._query_path.value['query_params']:
                self.query_string.remove_param(default[0])
        
        self._query_path = query_path
        # Set any default tags for this query path.
        # TODO:  We shouldn't have to map true into the tuple.
        for default in map(lambda t: t + (True,), query_path.value['query_params']):
            self.query_string.add_param(*default)

    def add_id(self, id):
        self._ids.append(id)

    def remove_id(self, id):
        try:
            self._ids.remove(id)
        except ValueError:
            pass

    def clear_ids(self):
        """Sets ids to the empty list."""
        self._ids = []

    def go(self):
        """Actually sends the request."""
        content = requests.get(self.build_full_url())
        print("The url after get is: {}".format(content.url))
        self.response = StackExchangeResponse(content)


#region QueryString

_MAX_TAGS = 5    # Per the stack exchange API.
_MAX_PAGE_SIZE = 100

class StackExchangeQueryString:

    """A class for creating a StackExchange API query string."""

    def __init__(self, **kwargs):
        self.parameters = []
        for k in kwargs:
            self.add_param(k, kwargs[k])

    def __str__(self, indent_=4, sort_keys_=True):
        params = map(lambda p: '  ' + str(p), self.parameters)
        head = self.__repr__()
        body = '\n'.join(params)
        return '\n'.join([head, body])

    def __iter__(self):
        for p in self.parameters:
            yield (parse.quote(p.key), self.retrieve(p.key))

    def get(self):
        """A more abstract way of getting the query string as a list of key/value pairs."""
        return self.parameters

    def get_full_string(self):
        """Returns all parameters formatted as a query string appropriate for the StackExchange API.  
        If nothing has been added, returns the empty string"""
        s = map(lambda t: "&{}={}".format(*t), self)
        return ''.join(s)[1:]

    def add_param(self, key, value, override=False):
        """Creates a query parameter given key and value."""
        param = self._get_query_param(key)
        if not param:
            param = QueryParameter(key, value)
            self.parameters.append(param)
        elif override:
            index = self.parameters.index(param)
            param = QueryParameter(key, value)
            self.parameters[index] = param
        else:
            param.add_value(value)

    def remove_param(self, key):
        """Removes a query parameter from this query string."""
        param = self._get_query_param(key)
        if param:
            self.parameters.remove(param)

    def retrieve(self, key):
        """Get's the passed in key's associated value.  None if the key is not found."""
        param = self._get_query_param(key)
        if param:
            return ';'.join(map(parse.quote, param.values))
        return ''
        
    def _validate_page_size(self, num):
        """Raises a ValueError when the page size is not within bounds."""
        if not 0 < num <= _MAX_PAGE_SIZE:
            raise ValueError('Pagesize must be between 1 and 100.')

    def _get_query_param(self, key):
        """Searches self.params for the param with a matching key."""
        for p in self.parameters:
            if p.key == key:
                return p
        return None


class QueryParameter:

    """A query parameter that can hold more than one value."""

    def __init__(self, key, values, delim=';'):
        """Creates a query paramter.

        Values can be a list or a string.

        """
        if not isinstance(values, (str, list)):
            raise TypeError("Values must be list or str, not {}".format(type(values)))
        self.values = values if isinstance(values, list) else [values]
        self.key = key
        self.delim = delim
        self._validate_values()

    def __str__(self):
        """Returns a string formatted for an url.

        If values is empty, returns the empty string.

        """
        values = self.delim.join(self.values)
        if values:
            return '='.join([self.key, values])
        else:
            return ''

    def __iter__(self):
        for v in self.values:
            yield (self.key, self.values)

    def add_value(self, value):
        """Adds the given value to self.values."""
        if value not in self.values:
            self.values.append(value)
        self._validate_values()
        
    def remove_value(self, value):
        try:
            self.values.remove(value)
        except ValueError:
            pass
        self._validate_values()
    
    def clear(self):
        self.values = []

    def _validate_values(self):
        """Determines if a key's values are legal."""
        if not self._is_value_good():
            raise ValueError("{}'s value: {}, is not valid.".format(key, values))

    def _is_value_good(self):
        if self.key == "pagesize":
            return 0 < int(self.values[0]) <= _MAX_PAGE_SIZE
        return True


@unique
class QueryPaths(Enum):

    """Enum types for StackExchange query paths."""

    Questions = {
        'path': '/'.join([StackExchangeQuery._version, 'questions']),
        'query_params': []
    }

    Answers = {
        'path': '/'.join([StackExchangeQuery._version, 'answers']),
        'query_params': []
    }

    Search = {
        'path': '/'.join([StackExchangeQuery._version, 'search']),
        'query_params': []
    }

    AdvancedSearch = {
        'path': '/'.join([StackExchangeQuery._version, 'search', 'advanced']),
        'query_params': [('sort', 'relevance')]
    }



# STACK EXCHANGE QUERY PARAMETERS FOR ADVANCED SEARCH
"""
q           - a free form text parameter, will match all question properties based on an undocumented algorithm.
accepted    - true to return only questions with accepted answers, false to return only those without. Omit to elide constraint.
answers     - the minimum number of answers returned questions must have.
body        - text which must appear in returned questions' bodies.
closed      - true to return only closed questions, false to return only open ones. Omit to elide constraint.
migrated    - true to return only questions migrated away from a site, false to return only those not. Omit to elide constraint.
notice      - true to return only questions with post notices, false to return only those without. Omit to elide constraint.
nottagged   - a semicolon delimited list of tags, none of which will be present on returned questions.
tagged      - a semicolon delimited list of tags, of which at least one will be present on all returned questions.
title       - text which must appear in returned questions' titles.
user        - the id of the user who must own the questions returned.
url         - a url which must be contained in a post, may include a wildcard.
views       - the minimum number of views returned questions must have.
wiki        - true to return only community wiki questions, false to return only non-community wiki ones. Omit to elide constraint.
"""