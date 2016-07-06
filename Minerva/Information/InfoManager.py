import PTVS

MODULE_MAP = {
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
        self.updateMod(moduleName)

    def _updateLinks(self):
        try:
            self.links = MODULE_MAP[self._mod].LINKS
        except LookupError:
            raise ValueError("Cannot find module {0}".format(self._mod))

    def _updateKeyMap(self):
        try:
            self.keyMap = MODULE_MAP[self._mod].KEY_MAP
        except LookupError:
            raise ValueError("Cannot find module {0}".format(self._mod))

    def updateMod(self, mod):
        self._mod = mod
        self._updateLinks()
        self._updateKeyMap()
        self.name = MODULE_MAP[self._mod].NAME

    def literalToKey(self, literal, d = None):
        """Returns the appropriate key for links when given a literal.
        For example, if the literal passed in is "debug" it will map this to
        "Debugging" for extraction of information out of LINKS.
        """
        d = d if d else self.keyMap
        for k, v in d.items():
            if literal.lower() in v['Triggers']:
                return k
        return None

    def getNextSpecializationKey(self, feature, keyword):
        """Determine if a previously identified feature has any specialized
        context in relation to keywords found by querying LUIS.  Will return 
        a list of keys whose values are either an URL to the specialized feature's 
        information or another dictionary of specializations.
        """
        try:
            # Subkeys points to a dictionary of key value pairs that are a specialized feature
            # as key and a list of triggers (such as synonyms) for that specialized word.
            subkeys = self.keyMap[feature]['Subkeys']
        except LookupError:
            # Not all keys have specializations.
            return None

        # Search for the keyword in the current list of specializations.
        for k, v in subkeys.items():
            if keyword in v:
                return k
        return None

    def getRefinedKeys(self, keyFeature, keywords):
        """Takes keywords that are found by LUIS and searches keyword triggers
        to see if a keyword can be used in context of the keyFeature.  If
        no keywords are found within the current module's encylopedia an empty
        list is returned.
        """
        specializedKeys = []
        if 0 < len(keywords):   # Not all queries return a list of keywords.
            for word in keywords:
                k = self.getNextSpecializationKey(keyFeature, word)
                if k:
                    specializedKeys.append(k)
        return specializedKeys

    def getAllRootKeys(self, keywords):
        """Returns a list of all the root keys matched by words in 'keywords'
        within the current module.
        """
        rootKeys = []
        for word in keywords:
            k = self.literalToKey(word)
            if k:
                rootKeys.append(k)
        return rootKeys

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
        # Validate we at least have a string, assuming it is an url.
        if not isinstance(v, str):
            raise IncompleteKeyListError("{0} is not a string.".format(v))
        else:
            return v