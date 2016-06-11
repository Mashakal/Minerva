#!usr/bin/env python
# Special thanks to Lucas Jones (lucjon on github) for providing a portion of the send method's code.  Find it online at https://github.com/lucjon/Py-StackExchange/blob/master/stackexchange/web.py.
import urllib.request


class UrlRequester(object):

    def __init__(self, url):
        self.setUrl(url)
        self._cache = {}

    def setUrl(self, url):
        self._url = url
        return True if url else False   # Allow quick error check.

    def getUrl(self):
        return self._url

    def send(self):
        # Build the request.
        req = urllib.request.Request(self.getUrl())
        req.add_header('Accept-Encoding', 'gzip')
        req_open = urllib.request.build_opener()

        # Make the request.
        try:
            conn = req_open.open(req)
            info = conn.info()
            data = conn.read()
            error_code = 200
        except urllib.error.HTTPError as e:
            error_code = e.code
            # A hack (header's are undocumented property), but there's a sensible way to get them.
            info = getattr(e, 'headers', {})
            req_data = e.read()

        # Decompress it, if necessary.

        # Check for errors.

        # Cache it.
            #self._cache(req_object)

    def read(self):
        pass

    def __log(self):
        """Log a number of items about this query."""
        # tags, query - should we cache as well
        raise NotImplementedError

    def __cache(self):
        raise NotImplementedError





