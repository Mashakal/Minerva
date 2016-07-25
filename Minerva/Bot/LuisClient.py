
from projectoxford.luis import LuisClient


_SUBSCRIPTION_KEY = '7814a9388ef14151981f2037000ea288'   # Alex Neuenkirk's subscription key.
_APP_IDS = {
    'HelpBot': '3b58ccb7-4165-4af0-9759-b028c73ce4f9',  # Testing only.
    'Petricca': '8f688b1d-6c6a-4245-8ca5-ec7a9eaddb6b'  # Currently the best.
}


class BotLuisClient(LuisClient):

    """A derived class of LuisClient that exposes method raw_query."""

    def __init__(self):
        url = self._build_luis_url('Petricca')
        return super().__init__(url)

    def query(self, text, result='standard'):
        """Sends a query to the LUIS app.

        The standard result is parsed into a tuple, as returned by a 
        call to LuisClient.query().  A verbose result will instead
        return the json from the query.
        
        """
        if result == 'standard':
            return super().query(text)
        elif result in ['verbose', 'v']:
            return super().query_raw(text)
        else:
            raise ValueError("Unknown result type {}.".format(result))

    def _build_luis_url(self, app_name):
        """Returns the url that points to the Project System LUIS app.
        
        There will rarely be more than one app, but implemenation allows
        for it.
        
        """
        items = [
            'https://api.projectoxford.ai/luis/v1/application?id=',
            _APP_IDS[app_name],
            '&subscription-key=',
            _SUBSCRIPTION_KEY,
            '&q='
        ]
        return ''.join(items)