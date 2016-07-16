from projectoxford.luis import LuisClient

class BotLuisClient(LuisClient):
    """A derived class of LuisClient that exposes method raw_query."""

    def query(self, text, result='standard'):
        if result == 'standard':
            return super().query(text)
        elif result in ['verbose', 'v']:
            return super().query_raw(text)
        else:
            raise ValueError("Unknown result type {0}.".format(result))