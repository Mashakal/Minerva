#!/usr/bin/env python
import stackexchangeparameters as separams


class Query(object):
    BASE_URL = 'https://api.stackexchange.com'
    VERSION = '2.2'
    VALID_QUERY_TYPES = ['questions']   # Only add valid query types as they are implemented in Minerva.
    VALID_SITES = ['stackoverflow'] # Could potentially add additional sites without any additional implementation.

    def __init__(self, site, params = None):
        self.startURL = Query.BASE_URL + "/" + Query.VERSION
        self.parameters = separams.Parameters(params)
        self.setQueryType('questions')
        self.setSite(site)
    
    def buildQueryString(self):
        return self.startURL + '/' + self.getQueryType() + '?' + self.parameters.getAsQueryString()

    def setQueryType(self, type):
        if not type in Query.VALID_QUERY_TYPES:
            raise ValueError("%s as a query type is not implemented." % type)
        self._queryType = type

    def getQueryType(self):
        return self._queryType

    def setSite(self, site):
        if not site in Query.VALID_SITES:
            raise ValueError("%s is not a valid StackExchange site or its querying is not implemented in Minerva." % site)
        self._site = site

    def getSite(self):
        return self._site


# Here for testing/debugging.
params = {"tagged":"ptvs;python"}
instance = Query('stackoverflow', params)
print(instance.buildQueryString())