# Constants.
_API_STRINGS = {
    'api': '/v3',
    'conversation': '/conversations',
    'activities': '/activities'
}


# Functions.
def _get_conversation_path(id):
    items = [
        _API_STRINGS['api'],
        _API_STRINGS['conversation'],
        '/',
        id,
        _API_STRINGS['activities']
    ]
    return ''.join(items)


def buld_reply_url(data):
    base = data['serviceUrl']
    path = _get_conversation_path(data['conversation']['id'])
    return ''.join([base, path])