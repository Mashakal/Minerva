#!usr/bin/env python
# Special thanks to Lucas Jones (lucjon on github) for providing a portion of the send method's code.  Find it online at https://github.com/lucjon/Py-StackExchange/blob/master/stackexchange/web.py.
import urllib.request
import io
import gzip
import requests
import sys


class UrlRequester(object):

    def __init__(self, url):
        self._url = url

    def setUrl(self, url):
        self._url = url

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
            code = 200
        except urllib.error.HTTPError as e:
            code = e.code
            # A hack (header's are undocumented property), but there's a sensible way to get them.
            info = getattr(e, 'headers', {})
            req_data = e.read()

        # Decompress it, if necessary.
        if info.get('Content-Encoding') == 'gzip':  # Guaranteed by SE API.
            data_stream = io.BytesIO(req_data)
            gzip_stream = gzip.GripFile(fileobj = data_stream)
            actual_data = gzip_stream.read()
        else:
            # Handle cases where proxy server has already decompressed.
            actual_data = req_data

        # Check for errors.
        #if code != 200:


        # Cache it.
            #self._cache(req_object)

    def GET(self, params = None):
        r = requests.get(self._url, params = params)
        print(r.json())
        print("Test.")


    def read(self):
        pass

    def __log(self):
        """Log a number of items about this query."""
        # tags, query - should we cache as well
        raise NotImplementedError

    def __cache(self):
        raise NotImplementedError





# Testing and Debugging.
def main():
    pass

if __name__ == "__main__":
    sys.exit(int(main() or 0))