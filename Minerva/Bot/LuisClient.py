
from projectoxford.luis import LuisClient


_SUBSCRIPTION_KEY = '7814a9388ef14151981f2037000ea288'   # Alex Neuenkirk's subscription key.
_APP_IDS = {
    'HelpBot': '3b58ccb7-4165-4af0-9759-b028c73ce4f9',  # Testing only.
    'Petricca': '8f688b1d-6c6a-4245-8ca5-ec7a9eaddb6b'  # Currently the best.
}


class BotLuisClient(LuisClient):

    """A derived class of LuisClient."""

    def __init__(self, app_name):
        self.app_name = app_name
        url = self._build_luis_url()
        return super().__init__(url)

    def _build_luis_url(self):
        """Returns the url that points to the Project System LUIS app.
        
        There will rarely be more than one app, but implemenation allows
        for it.
        
        """
        items = [
            'https://api.projectoxford.ai/luis/v1/application?id=',
            _APP_IDS[self.app_name],
            '&subscription-key=',
            _SUBSCRIPTION_KEY,
            '&q='
        ]
        return ''.join(items)


MODEL_ENTITY_SCHEMA = {
    'negators': 'Negator',

    'languages': 'Subjects::Programming Language',
    'installables': 'Subjects::Installable',
    'other_subjects': 'Subjects::Other',
    'metas': 'Subjects::Meta',
    'frameworks': 'Subjects::Framework',
    'services': 'Subjects::Services',
    'settings': 'Subjects::Settings',

    'learn_about_phrases': 'Learn About Triggers::Phrase',
    'learn_about_singles': 'Learn About Triggers::Single',

    'gerunds': 'Action::Gerund',
    'verbs': 'Action::Conjugated Verb',
    'install_something': 'Action::Install Something',

    'jargon_single': 'Jargon::Single Word',
    'jargon_phrase': 'Jargon::Phrase',
    'jargon_debugging': 'Jargon::Debugging',

    'subject_adjectives': 'Auxiliary::Subject Adjective',
    'jargon_adjectives': 'Auxiliary::Jargon Adjective',
    'intent_descripters': 'Auxiliary::Intent Descripter',
    'versions': 'Auxiliary::Version'
}