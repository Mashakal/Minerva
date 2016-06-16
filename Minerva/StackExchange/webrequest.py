#!usr/bin/env python
# Special thanks to Lucas Jones (lucjon on github) for providing a portion of the send method's code.  Find it online at https://github.com/lucjon/Py-StackExchange/blob/master/stackexchange/web.py.
import urllib.request
import io
import gzip
import requests
import sys

from stackexchangeresponse import * # only holds the StackExchangeResponse class definition.


class UrlRequester(object):

    def __init__(self, url):
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

    def GET(self):
        """Uses the requests package to submit an HTTP request."""
        content = requests.get(self._url)
        if content.status_code != 200:
            print("There was a problem with the get request.  Error code is: %s." % content.status_code)
            return False
        else:
            print("The status code is %s." % content.status_code)
        return content

# EXAMPLE QUERY STRING:  https://api.stackexchange.com/2.2/questions?order=desc&sort=activity&site=stackoverflow