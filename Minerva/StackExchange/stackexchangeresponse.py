import json

class StackExchangeResponse:

    """Holds the data for a StackExchange API response."""
    
    def __init__(self, content):
        self._content = content   # The response content returned by requests.get.
        self._json = content.json()
        self._results = [] # A response's items.
        for q in self._json['items']:
            self._results.append(StackExchangeResult(q))
        self.result_count = len(self._results)
        
    def print_result(self, resultIndex):
        print(self._results[resultIndex].__str__())

    def get_result(self, resultIndex):
        return self._results[resultIndex]


class StackExchangeResult:
    
    """A base class for defining common response item methods and attributes."""

    def __init__(self, dict_):
        self._d = dict_   # Dictionary holding this item's contents.
    
    def get(self):
        return self._d
        
    def get_value(self, key):
        return self._d[key]

    def __str__(self):
        return json.dumps(self._d, indent=4, sort_keys=True)
        