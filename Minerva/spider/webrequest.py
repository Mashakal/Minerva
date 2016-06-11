#!usr/bin/env python
try:
    import urllib
    httpGet = urllib.request.urlopen
except ImportError:
    import urllib2
    httpGet = urllib2.urlopen


class Request(object):

    def __init__(self):
        pass

    def setUrl(self, url):
        pass

    def getUrl(self):
        pass

    def send(self):
        pass

    def read(self):
        pass

    def _log(self):
        """Log a number of items about this query."""
        # tags, query - should we cache as well
        pass

    def _cache(self):
        raise NotImplementedError





