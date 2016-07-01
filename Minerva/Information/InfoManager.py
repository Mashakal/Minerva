import PTVS

MODULE_MAP = {
    'ptvs': PTVS
}

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
        self._mod = mod.lower()
        self._updateLinks()
        self._updateKeyMap()

    def literalToKey(self, literal):
        """Returns the appropriate key for links when given a literal.
        For example, if the literal passed in is "debug" it will map this to
        "Debugging" for extraction of information out of LINKS.
        """
        for k, v in self.keyMap.items():
            if literal.lower() in v['Triggers']:
                return k
        return None

    def filterWithKeyword(self, feature, keyword):
        """Determine if a previously identified feature has more specific 
        context in relation to 'keyword'.  Will return a key for
        which to extract a link corresponding feature's link from LINKS.
        """
        try:
            subkeys = self.keyMap[feature]['Subkeys']
        except LookupError:
            return None
        for k, v in subkeys.items():
            if keyword in v:
                return k
        return None

    def getRefinedKeys(self, keyFeature, keywords):
        """Returns a list of refined key features, based on any keywords that were
        found in the original query.  An empty list is returned when no subkeys
        are found.
        """
        refinedKeys = []
        if 0 < len(keywords):
            for word in keywords:
                filtered = self.filterWithKeyword(keyFeature, word)
                if filtered:
                    refinedKeys.append(filtered)
        return refinedKeys