#!/usr/bin/env python

import sys
import stackexchange    # A wrapper around the actual StackExchange.com API.
import owl              # Customized query items.

# TODO - You can only have 5 tags per query.


# ID constants.
API_KEY = 'E3Ht0FN1L57M68Wk56e2RA(('    # API Key for Minerva, from StackExchange.com
MY_SO_ID = 4499786  # My (Alex Neuenkirk) stack overflow user id.

# Behavior constants.
IMPOSE_THROTTLING = True    # Tell the stackexchange API to throttle.

# Query constants, mostly for testing.
TAGS = 'ptvs;'  
COUNT = '2'


def testSearch(site, simple=True):
    """ Test the search method from py-stackexchange API. """
    # BUG:  pagesize=Count isn't working.
    results = site.search(tagged=TAGS, pagesize=COUNT) if simple else site.search_advanced(tagged="ironpython", pagesize=COUNT)
    return results

def testFilter(site):
    results = testSearch(site)
    filterResults(results)

def printResults(results):
    # Iterate over each question within the results object.
    for q in results:
        print('%8d--%s' % (q.id, q.title.encode('utf-8')))    
    

def main():
    so = stackexchange.Site(stackexchange.StackOverflow, API_KEY, IMPOSE_THROTTLING)
    me = so.user(MY_SO_ID)
    rs = testSearch(so)
    printResults(rs)
    #testFilter(so)


if __name__ == "__main__":
    sys.exit(int(main() or 0))