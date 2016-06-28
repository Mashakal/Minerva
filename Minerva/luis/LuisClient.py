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
            raise ValueError("Unknown result type %s" % result)

