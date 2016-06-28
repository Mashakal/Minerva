#!/usr/bin/env python
from querystring import StackExchangeQueryString
from stackexchangeresponse import StackExchangeResponse
import webrequest as web
from urllib import parse
import requests

class StackExchangeQuery(object):
    _API_KEY = 'E3Ht0FN1L57M68Wk56e2RA(('    # API Key for Minerva, from StackExchange.com
    _version = '2.2'
    _netloc = 'api.stackexchange.com'
    _paths = {
        'questions': _version + '/questions',
        'answers': _version + '/answers'
    }

    def __init__(self, site, queryParams = None):
        self.segments = {
            'scheme': 'https',
            'netloc': StackExchangeQuery._netloc,
            'path': None,
            'params': None,   # Do not confuse this with query string parameters, which should be put with query as the key.  See urllib.parse module for more.
            'query': None,
            'fragment': None
        }
        # We have a query string object to allow rich functionality in manipulating this query's url.
        self.queryString = StackExchangeQueryString(queryParams)
        self.setSite(site)
        self.queryString.addPair('key', StackExchangeQuery._API_KEY)
    
    def buildFullUrl(self):
        self.__buildUrlItems()
        return parse.urlunparse(self.__getIterableUrlItems())

    def __getIterableUrlItems(self):
        """Get all values from the segments dictionary in the appropriate order as defined by the urllib.parse module."""
        order = ['scheme', 'netloc', 'path', 'params', 'query', 'fragment']
        segs = []
        for key in order:
            segs.append(self.segments[key])
        return segs

    def __buildUrlItems(self):
        if self.segments['path'] is None:
            # Default to 'questions' when not set explicitly.
            self.segments['path'] = StackExchangeQuery._paths['questions']
        if self.segments['params'] is None:
            self.segments['params'] = ''
        self.segments['query'] = self.queryString.getFullString()
        if self.segments['fragment'] is None:
            self.segments['fragment'] = ''

    def setQueryType(self, type):
        if not type in StackExchangeQuery._paths.keys():
            raise ValueError("%s as a query type is not implemented." % type)
        self.segments['path'] = StackExchangeQuery._paths[type]
        self.idAdded = False    # changing the query type removes added ids.

    def setSite(self, site):
        self.queryString.addPair('site', site)

    def addId(self, id):
        if not self.idAdded:
            self.segments['path'] = self.segments['path'] + '/' + str(id)
            self.idAdded = True
            return True
        return False

    def go(self):
        content = requests.get(self.buildFullUrl())
        self.response = StackExchangeResponse(content)

    
# Here for testing/debugging.
#queryParams = {"tagged":"ptvs;python", 'pagesize':'1'}
#q = StackExchangeQuery('stackoverflow', queryParams)
#q.go()
#q.response.printAll()






#segments = {
#    'scheme': 'https',
#    'netloc': 'api.stackexchange.com',
#    'path': '2.2/questions',
#    'params': '',
#    'query': 'order=desc&sort=activity&site=stackoverflow',
#    'fragment': ''
#}