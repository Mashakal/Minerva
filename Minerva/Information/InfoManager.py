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

    def find_path_to_trigger_key(self, literal, path=None, dic=None):
        """When literal is found to be a trigger, a list of keys that will lead to
        the key the literal matches is returned.  Otherwise, False is returned.
        """
        d = dic if dic else self.key_map
        p = path if path else []
        for k, v in d.items():
            # See if any keys are triggered by literal in this dict or any of its descendents.
            if isinstance(v, dict):   # A key's triggers are always in its value's dictionary.
                try:
                    if literal.lower() in v['Triggers']:
                        # We found a key in this dict.
                        p.append(k)
                        return p
                    else:
                        # This key wasn't triggered, but...
                        p.append(k) # ...maybe a descendants key will be triggered.
                        p = self.find_path_to_trigger_key(literal, p, v) # ... let's check.
                except KeyError:
                    # A dictionary might not have 'Triggers' as a key.
                    pass    
                # If no key was triggered in any descendants p will be the same, and False.
                if p == path or not p:
                    # Path stays the same or is reset, depending on the 
                    # depth of the dictionary (v) we are searching.
                    p = path if path else []
                # If a descendant's key was triggered by literal, p will have been changed.
                else:
                    return p
        if p:
            # If we're here, no descendant's keys were triggered by literal.
            p.pop() # So remove this key from the path.
        return p or False   # False when no key triggered in root dict.

    def _traverse_keys(self, keys):
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
    def __init__(self, moduleName):
        super().__init__(moduleName)
        self._trigger_map = self._map_triggers_to_paths()

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

    def set_from_key_values(self, dic=None, set_=None, k_to_collect=None):
        """Creates a set of all the values for every key matches the string k_to_collect.  This can be used
        to create Phrase List Features on the fly after creating an info file that adheres
        to the specifications.  It works by searching the key map (or any dict, for that matter) for
        all values of dic['k_to_collect'] and adding them to the the set of those already found.
        You can use this set to seed your Luis app programatically.
        """
        d = dic if dic else self.key_map
        set_ = set_ if set_ else set(())
        k_to_collect = k_to_collect if k_to_collect else 'Triggers'

        for k, v in d.items():
            if isinstance(v, dict):
                try:
                    t = v[k_to_collect]
                    if t:
                        set_ |= t
                except KeyError:
                    pass
                finally:
                    set_ = self.set_from_key_values(v, set_, k_to_collect)
        return set_

    def gen_file_from_info(self, filename, func, **kwargs):
        """Iterates over the return value of func called with kwargs passed in
        as the parameters.  Filename should be a .txt file.  Values will be
        added to the file delimited by a comma.
        """
        fn = filename if filename.endswith('.txt') else filename + '.txt'
        with open(fn, 'w') as fd:
            for el in func(kwargs):
                el += ","
                fd.write(el)
     
    def _map_triggers_to_paths(self):
        """Returns a mapping of a trigger to a set of keys that will lead to the value
        for the key that this trigger is mapped to.
        """
        # Get all triggers as a set.  This function will use 
        triggers = self.set_from_key_values(k_to_collect='Triggers')
        return {trigger: self.find_path_to_trigger_key(trigger) for trigger in triggers}

    def remove_subpaths(self, paths):
        """Removes any path within paths that is a subpath of another path.
        """
        if isinstance(paths, list):
            # Only have to look at the next path in paths if it is sorted.
            paths.sort()
        elif isinstance(paths, dict):
            # Get a list of all the paths in the dict.
            paths = [e for k, v in paths.items() if v for e in v]

        subpaths = []
        for i in range(len(paths) - 1):
            # Check if paths[i] a sublist of paths[i + 1].
            if paths[i][:len(paths[i])] == paths[i + 1][:len(paths[i])]:
                subpaths.append(paths[i])
        for subpath in subpaths:
            paths.remove(subpath)
        return paths

    def get_paths(self, triggers):
        """Returns a list of paths given a list of triggers.  If remove_duplicates is True
        the subpaths will be removed before returning."""
        paths = []
        for trigger in triggers:
            try:
                p = self._trigger_map[trigger]
            except KeyError:
                pass
            else:
                paths.append(p)
        return paths

    def get_url(self, path):
        """Returns the value pointed to by path."""
        return self._traverse_keys(path)

def main():
    im = ProjectSystemInfoManager('ptvs')
    print(im.set_from_key_values())
    im.gen_file_from_info('triggers_we_hope.txt', im.set_from_key_values)

if __name__ == "__main__":
    sys.exit(int(main() or 0))
