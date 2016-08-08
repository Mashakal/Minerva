

import query

def main():
    q = stackexchangequery.StackExchangeQuery('stackoverflow', {'tagged': 'ptvs'})
    print(q.build_full_url())
    q.set_query_type(query.QueryTypes.AdvancedSearch)



if __name__ == "__main__":
    main()