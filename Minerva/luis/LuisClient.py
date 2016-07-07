from projectoxford.luis import LuisClient

class BotLuisClient(LuisClient):
    def __init__(self, url):
        return super().__init__(url)

    def query(self, text, result='standard'):
        if result == 'standard':
            return super().query(text)
        elif result in ['verbose', 'v']:
            return super().query_raw(text)
        else:
            raise ValueError("Unknown result type {0}.".format(result))

#class ResponseData(object):
#    """Formatted response data from a LuisClient query.
#    """
#    def __init__(self, json):
#        self._json = json

#    def _get_top_scoring_intent(self):
#        try:
#            return self._json['intents'][0]['intent']
#        except LookupError:
#            return 'undefined'

#    def _get_literals(self):
#        return [e['entity'] for e in self._json['entities']]

#    def _get_types(self):
#        return [e['type'] for e in self._json['entities']]

#    def _get_all_literals_of_type(self, t):
#        return [e['entity'] for e in self._json['entities'] if e['type'] == t]

#class ProjectSystemResponseData(ResponseData):
#    """A data object with formatted data that
#    correlates to a Project System information module.
#    """
#    def __init__(self, json, info_manager):
#        super().__init__(json)
#        self.data = self.__format_data()
#        self._info = info_manager

#    def __format_data(self):
#        """Formats the raw json into a more easily managable dictionary."""
#        o = {
#            'literals': self._get_literals(),
#            'types': self._get_types(),
#            'keywords': self._get_all_literals_of_type('Keyword'),
#            'intent': self._get_top_scoring_intent(),
#        }
#        o['root_keys'] = self._info.get_all_root_keys(o['keywords'])
#        return o
