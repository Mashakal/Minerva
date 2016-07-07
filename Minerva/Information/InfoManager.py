import PTVS

__MODULE_MAP = {
    'ptvs': PTVS
}

class IncompleteKeyListError(Exception):
    """Raised when a url is being extracted but the key list does not point
    to a url.
    """
    def __init__(self, msg, **kwargs):
        self.message = self.msg = msg
        return super().__init__(**kwargs)

class InfoManager(object):
    """Handles accessing of information data for LuisInterpreters."""
    def __init__(self, moduleName):
        self.update_mod(moduleName)

    def update_mod(self, mod):
        try:
            self.links = __MODULE_MAP[mod].LINKS
            self.key_map = __MODULE_MAP[mod].KEY_MAP
            self.name = __MODULE_MAP[mod].NAME
            self._mod = mod
        except KeyError:
            raise ValueError("Cannot find module {0}".format(mod))

    def literal_to_key(self, literal, d = None):
        """Returns the appropriate key for links when given a literal.
        For example, if the literal passed in is "debug" it will map this to
        "Debugging" for extraction of information out of LINKS.
        """
        d = d if d else self.key_map
        for k, v in d.items():
            if literal.lower() in v['Triggers']:
                return k
        return None

    def get_next_key(self, feature, keyword):
        """Determine if a previously identified feature has any specialized
        context in relation to keywords found by querying LUIS.  Will return 
        a list of keys whose values are either an URL to the specialized feature's 
        information or another dictionary of specializations.
        """
        try:
            # Subkeys points to a dictionary of key value pairs that are a specialized feature
            # as key and a list of triggers (such as synonyms) for that specialized word.
            subkeys = self.key_map[feature]['Subkeys']
        except LookupError:
            # Not all keys have specializations.
            return None

        # Search for the keyword in the current list of specializations.
        for k, v in subkeys.items():
            if keyword in v:
                return k
        return None

    def get_refined_keys(self, key_feature, keywords):
        """Takes keywords that are found by LUIS and searches keyword triggers
        to see if a keyword can be used in context of the keyFeature.  If
        no keywords are found within the current module's encylopedia an empty
        list is returned.
        """
        specialized_keys = []
        if 0 < len(keywords):   # Not all queries return a list of keywords.
            for word in keywords:
                k = self.get_next_key(key_feature, word)
                if k:
                    specialized_keys.append(k)
        return specialized_keys

    def get_all_root_keys(self, keywords):
        """Returns a list of all the root keys matched by words in 'keywords'
        within the current module.
        """
        root_keys = []
        for word in keywords:
            k = self.literal_to_key(word)
            if k:
                root_keys.append(k)
        return root_keys

    def traverse_keys(self, keys):
        """Traverses the links dictionary of the current module by way of keys.
        Returns the value of the deepest key in keys.
        """
        v = self.links  # Start at the root of the links dict.
        # Find the final value pointed to by keys.
        if isinstance(keys, list):
            for key in keys:
                v = v[key]
        elif isinstance(keys, str):
            v = v[keys]
        return v

    def get_url(self, keys):
        """Returns the url pointed to by keys.
        """
        v = self.traverse_keys(keys)
        # We assume a string object is going to be a url.
        if not isinstance(v, str):
            raise IncompleteKeyListError("{0} is not a string.".format(v))
        else:
            return v