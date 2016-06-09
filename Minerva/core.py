#!/usr/bin/env python

import StackExchange
import sys


class Parameters(object):
    """A class for creating query parameters."""

    def __init__(self, **kwargs):
        """Accepts an arbitrary number of key-value pairs to be added to the parameters object being created."""
        self._paramters = {}
        for k, v in kwargs.items():
            self._paramters[k] = v

    def get(self):
        s = ''
        for k, v in self._paramters.items():
            s += '&' + str(k) + "=" + str(v) if s else str(k) + "=" + str(v)
        return s


def runTests():
    print("Testing class Parameters:")
    params = Parameters(count=15, dance='hipHop')
    assert(params.get() == "dance=hipHop&count=15")
    print("Passed")