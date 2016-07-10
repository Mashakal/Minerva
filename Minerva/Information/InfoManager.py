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
        print(msg)
        return super().__init__(**kwargs)

class InfoManager(object):
    """Handles accessing of information data for LuisInterpreters."""
    def __init__(self, moduleName):
        self.update_mod(moduleName)

    def update_mod(self, mod):
        """Sets the InfoManager's module, which is the object's access
        to information.
        """
        try:
            self.links = _MODULE_MAP[mod].LINKS
            self.key_map = _MODULE_MAP[mod].KEY_MAP
            self.name = _MODULE_MAP[mod].NAME
            self._mod = mod
        except KeyError:
            raise ValueError("Cannot find module named: {0}".format(mod))

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

class ProjectSystemInfoManager(InfoManager):
    """ A derived class from InfoManager.  Has some logic that is coupled with
    project systems as a whole.
    """

    def get_url_description(self, url):
        """Grabs the last filename, which is usually the most descriptive of
        a link, from url.  If url matches the expected format, it will extract
        and reformat the name for printing.  If url does not match, False is 
        returned.  The following is an example of the expected format for
        url:  "https://github.com/Microsoft/PTVS/wiki".  In this case 'wiki'
        is returned.
        """
        last = url.rfind('/')
        if 0 <= last:
            s = url[last + 1:]
            s = s.replace('-', ' ')
            s = s.replace('#', ': ')
        return s or False


def main():
    im = ProjectSystemInfoManager('ptvs')
    return    

if __name__ == "__main__":
    sys.exit(int(main() or 0))
