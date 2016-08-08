import json

import query

def main():
    #mvqp = query.QueryParameter('tagged', ['ptvs'])
    #print(mvqp.__str__())
    #for el in mvqp:
    #    print("Element is: {}".format(el))
    #mvqp.add_value('debugging')
    #print(str(mvqp))
    #mvqp.remove_value('ptvs')
    #print(str(mvqp))

    #qs = query.StackExchangeQueryString()
    #for o in qs.params: print(o)
    
    #print(str(qs))
    #qs.add_param('tagged', 'ptvs')
    #qs.add_param('tagged', 'debugging')
    #qs.add_param('intitle', 'c#')
    #print(str(qs))
    #print(qs.get_full_string())

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

    q = query.StackExchangeQuery('stackoverflow')
    q.set_query_path(query.QueryPaths.AdvancedSearch)
    q.query_string.add_param('tagged', ['c #', 'python', 'debugging'])
    q.query_string.add_param('filter', 'withbody')
    q.query_string.add_param('pagesize', '20')
    q.query_string.add_param('nottagged', 'pycharm')
    print(q.query_string.__str__())
    print(q.build_full_url())
    
    q.go()

    print(json.dumps(q.response._json, sort_keys=True, indent=4))
    
    # Problems debugging c# and python at the same time in ptvs:
    # all_jargon: {'debugging'}
    # auxiliaries: {'same time'}
    # subjects: {'c #', 'python'}
    

if __name__ == "__main__":
    main()


#segments = {
#    'scheme': 'https',
#    'netloc': 'api.stackexchange.com',
#    'path': '2.2/questions',
#    'params': '',
#    'query': 'order=desc&sort=activity&site=stackoverflow',
#    'fragment': ''
#}