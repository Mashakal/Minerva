import sys
import string
import json
import itertools

import Query

#def main():
#    question = "Can't view symbols during debugging."
#    title = "How to debug a remote python application using (Python Tools for) Visual Studio?"
#    question_words = set(map(trim_punctuation, question.split(" ")))
#    title_words = set(map(trim_punctuation, title.split(" ")))
#    scores = {w: title.count(w) for w in question_words}
#    print(scores)
#    scores = {w: question.count(w) for w in title_words}
#    print(scores)

def main():
    print(sys.argv)
    return

def trim_punctuation(word):
    """Trims any surrounding punctuation."""
    if len(word) == 1:
        return word if word.isalpha() else ''
    first = last = None
    for i, letter in enumerate(word):
        if letter.isalpha():
            if first is None:
                first = i
            else:
                last = i
    return word[first:last + 1]


"""
def main():
    #mvqp = Query.QueryParameter('tagged', ['ptvs'])
    #print(mvqp.__str__())
    #for el in mvqp:
    #    print("Element is: {}".format(el))
    #mvqp.add_value('debugging')
    #print(str(mvqp))
    #mvqp.remove_value('ptvs')
    #print(str(mvqp))


    #qs = Query.StackExchangeQueryString()
    #qs.add_param('tagged', 'ptvs')
    #qs.add_param('tagged', 'debugging')
    #qs.add_param('intitle', 'c#')

    #print("Remove params:")
    #print(str(qs))
    #qs.remove_param('tagged')
    #qs.remove_param('tagged')
    #qs.remove_param('intitle')
    #qs.remove_param('site')
    #print(str(qs))
    
    #print("Retrieve:")
    #print(str(qs))
    #qs.add_param('tagged', ['ptvs', 'debugging'])
    #print(qs.retrieve('tagged'))
    #print(qs.retrieve('site'))
    #print(str(qs))

    #q = Query.StackExchangeQuery('stackoverflow')
    #q.set_query_path(Query.QueryPaths.AdvancedSearch)
    #q.query_string.add_param('tagged', ['c #', 'python', 'debugging'])
    #q.query_string.add_param('filter', 'withbody')
    #q.query_string.add_param('pagesize', '20')
    #q.query_string.add_param('nottagged', 'pycharm')
    #print(q.query_string.__str__())
    #print(q.build_full_url())
    
    #q.initiate()

    #print(json.dumps(q.response._json, sort_keys=True, indent=4))
    
    # Problems debugging c# and python at the same time in ptvs:
    # all_jargon: {'debugging'}
    # auxiliaries: {'same time'}
    # subjects: {'c #', 'python'}
"""

if __name__ == "__main__":
    main()
