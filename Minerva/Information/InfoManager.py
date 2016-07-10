import PTVS
import sys
from Essentials import enter_and_exit_labels

_MODULE_MAP = {
    'ptvs': PTVS
}

class IncompleteKeyListError(Exception):
    """Raised when a url is being extracted but the key list does not point
    to a url.
    """
    def __init__(self, msg, **kwargs):
        self.message = self.msg = msg
        print(msg)
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

    #def literal_to_key(self, literal, dic=None):
    #    """Returns the appropriate key for links when given a literal.
    #    For example, if the literal passed in is "debug" it will map this to
    #    "Debugging" for extraction of information out of LINKS.
    #    """
    #    d = dic if dic else self.key_map
    #    for k, v in d.items():
    #        if literal.lower() in v['Triggers']:
    #            return k
    #    return None

    def find_key_path(self, literal, path=None, dic=None):
        """When literal is found to be a trigger, a list of keys that will lead to
        the item the literal matches is returned.  Otherwise, False is returned.
        """
        d = dic if dic else self.key_map
        p = path if path else []
        for k, v in d.items():
            # See if our literal is in any of this key's triggers.
            if isinstance(v, dict):     # A key's triggers are always in its value's dictionary.
                try:
                    if literal.lower() in v['Triggers']:
                        # We found a key in this dict.
                        p.append(k)
                        return p
                    else:
                        # This key wasn't triggered, but maybe...
                        p.append(k) # ...one of k's children might lead us to a trigger...
                        p = self.find_key_path(literal, p, v) # ... let's check.
                except KeyError:
                    pass    # A dictionary might not have 'Triggers' as a key.
                # p will now be different than path if we found a subkey in this dict's children.
                # Or it will be False, no subkey was triggered.
                if p == path or not p:
                    # Path stays the same or is reset, depending on the 
                    # depth of the dictionary (v) we are searching.
                    p = path if path else []
                else:
                    # We found a key in a child dict.
                    return p
        if p:
            # None of v's subkeys were triggered, nor any of its heir's subkeys.
            p.pop() # Ditch v's key.
        return p or False

    #def get_next_key(self, feature, keyword):
    #    """Determine if a previously identified feature has any specialized
    #    context in relation to keywords found by querying LUIS.  Will return 
    #    a list of keys whose values are either an URL to the specialized feature's 
    #    information or another dictionary of specializations.
    #    """
    #    try:
    #        # Subkeys points to a dictionary of key value pairs that are a specialized feature
    #        # as key and a list of triggers (such as synonyms) for that specialized word.
    #        subkeys = self.key_map[feature]['Subkeys']
    #    except LookupError:
    #        # Not all keys have specializations.
    #        return None

    #    # Search for the keyword in the current list of specializations.
    #    for k, v in subkeys.items():
    #        if keyword in v:
    #            return k
    #    return None

    #def get_refined_keys(self, key_feature, keywords):
    #    """Takes keywords that are found by LUIS and searches keyword triggers
    #    to see if a keyword can be used in context of the keyFeature.  If
    #    no keywords are found within the current module's encylopedia an empty
    #    list is returned.
    #    """
    #    specialized_keys = []
    #    if 0 < len(keywords):   # Not all queries return a list of keywords.
    #        for word in keywords:
    #            k = self.get_next_key(key_feature, word)
    #            if k:
    #                specialized_keys.append(k)
    #    return specialized_keys

    #def get_all_root_keys(self, keywords):
    #    """Returns a list of all the root keys matched by words in 'keywords'
    #    within the current module.
    #    """
    #    root_keys = []
    #    for word in keywords:
    #        k = self.literal_to_key(word)
    #        if k:
    #            root_keys.append(k)
    #    return root_keys

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

def main():
    im = InfoManager('ptvs')
    path = im.find_key_path('code editing')
    print(path)

if __name__ == "__main__":
    sys.exit(int(main() or 0))
