import PTVS
import sys

_MODULE_MAP = {
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
            self.links = _MODULE_MAP[mod].LINKS
            self.key_map = _MODULE_MAP[mod].KEY_MAP
            self.name = _MODULE_MAP[mod].NAME
            self._mod = mod
        except KeyError:
            raise ValueError("Cannot find module named: {0}".format(mod))

    def literal_to_key(self, literal, d=None):
        """Returns the appropriate key for links when given a literal.
        For example, if the literal passed in is "debug" it will map this to
        "Debugging" for extraction of information out of LINKS.
        """
        d = d if d else self.key_map
        for k, v in d.items():
            if literal.lower() in v['Triggers']:
                return k
        return None

    def is_literal_trigger(self, literal, d=None):
        """When literal is found to be a trigger, a list of keys that will lead to
        the item the literal matches is returned.  Otherwise, False is returned.
        """
        raise NotImplementedError("is_literal_trigger's implementation is not complete.")

        d = d if d else self.key_map
        for k, v in d.items():
            if isinstance(v, dict):
                try:
                    if literal in v['Triggers']:
                        return k
                    else:
                        return is_literal_trigger(literal, v)
                except KeyError:
                    pass
    
    def test_is_literal_trigger(self, literal, path=None, d=None):
        """When literal is found to be a trigger, a list of keys that will lead to
        the item the literal matches is returned.  Otherwise, False is returned.
        """
        d = d if d else _MODULE_MAP['ptvs'].KEY_MAP_TESTER
        p = path if path else []
        for k, v in d.items():
            if isinstance(v, dict):
                try:
                    if literal in v['Triggers']:
                        p.append(k)
                        return p
                    else:
                        p.append(k)
                        return self.test_is_literal_trigger(literal, p, v)
                except KeyError:
                    pass
        return False

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

    #def test_get_next_key(self, keyword, d):
        
    #    for k, v in d.items():
    #        if isinstance(v, dict):
    #            try:
    #                if keyword in v['Triggers']:
    #                    return True

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


def main():
    im = InfoManager('ptvs')
    path = im.test_is_literal_trigger('attach')
    print(path)

if __name__ == "__main__":
    sys.exit(int(main() or 0))
