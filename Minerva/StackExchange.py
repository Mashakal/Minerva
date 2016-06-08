#!/usr/bin/env python

import sys
import stackexchange    # A wrapper around the actual StackExchange.com API.


# ID constants.
API_KEY = 'E3Ht0FN1L57M68Wk56e2RA(('    # API Key for Minerva, from StackExchange.com
MY_SO_ID = 4499786  # My (Alex Neuenkirk) stack overflow user id.

# Behavior constants.
IMPOSE_THROTTLING = True    # Tell the stackexchange API to throttle.


def main():
    so = stackexchange.Site(stackexchange.StackOverflow, API_KEY, IMPOSE_THROTTLING)
    me = so.user(MY_SO_ID)
    #testAdvanced(so)
    testSimple(so)

def testAdvanced(site):
    """ Test the advanced search method from py-stackexchange API. """
    results = site.search_advanced(tagged="ptvs")
    printResults(results)

def testSimple(site):
    results = site.search(tagged="ptvs")
    printResults(results)

def printResults(results):
    # Iterate over each question within the results object.
    for q in results:
        print('%8d--%s' % (q.id, q.title))

if __name__ == "__main__":
    sys.exit(int(main() or 0))