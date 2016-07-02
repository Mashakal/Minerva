#!usr/bin/env python
import sys
from stackexchangequery import StackExchangeQuery
from stackexchangeresponse import StackExchangeResult
import json, random
from os import stat
import math

# Minerva extracts the pertinent information from the user's message.

DEBUGGING = True
DEBUG_FILE = 'debugfile.json'
site = 'stackoverflow'

# Example 'Help me with':  'sending http request with requests package'
# Let's say Minerva extracts the following tags:  requests, http-request
# Minerva will add by default tags:  'python', 
# Therefore, for the stack exchange query we have the following tags:  requests, python

def help():
    # Get the tags from somewhere.
    tags = ['ptvs']
    q = createQuery('stackoverflow', tags)
    q.queryString.addPair('pagesize', 5)
    q.go()
    displayTop3(q.response)

def displayTop3(response):
    for i in range(5):
        r = response.getResult(i)
        #r.printAllPairs()
        print("." * 15)
        #print("TITLE:  %s" % r.getValue('title'))
        #print('LINK:  %s' % r.getValue('link'))
        #if (round(random.random()) == 0):
            #simulateClick(r)
            #return
        simulateClick(r)

def getAnswerContents(result):
    answerId = result.getValue('accepted_answer_id')
    q = StackExchangeQuery(site)
    q.setQueryType('answers')
    q.addId(answerId)
    print(q.buildFullUrl())


def main():
    help()

def simulateClick(result):
    if 'accepted_answer_id' in result.get().keys():
        getAnswerContents(result)
    else:
        print("No answer contents...\n")


def getAnswer(result):
    if bool(result.getValue('is_answered')):
        answerId = result.getValue('accepted_answer_id')
        #q = createQuery(site, {'

def createQuery(site, tags):
    query = StackExchangeQuery(site)
    query.queryString.addTags(tags)
    return query

def getFileSize(filename):
    st = stat(filename)
    return st.st_size

def getDebugFile(filename):
    try:
        f = open(filename, "a+")
        return f
    except Exception as e:
        print("There was a problem with the file.")
        return None

def writeJsonToFile(data, fDesc):
    try:
        json.dump(data, fDesc)
        return True
    except Exception as e:
        print("There was a problem writing to the file.")
        print(e.strerror)
        return False

if __name__ == "__main__":
    sys.exit(int(main() or 0))