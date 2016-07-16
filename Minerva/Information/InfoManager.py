import sys
import importlib


class InfoManager:
    """Handles accessing of information data for LuisInterpreters."""
    def __init__(self, moduleName):
        self.update_mod(moduleName)

    def update_mod(self, mod):
        """Sets the InfoManager's module, which is the object's access
        to information.
        """
        try:
            self._mod = importlib.import_module(mod)
        except ImportError:
            raise ValueError("Cannot find module {} in sys.path.".format(mod))
        
        # Trigger map is module specific.
        self._trigger_map = self._map_triggers_to_paths()

    def find_path_to_trigger_key(self, literal, path_=None, dict_=None):
        """Returns a list of keys that will lead to information on literal.

        The list comes from searching INFO.KEY_MAP for a specific key's set of 
        triggers (keys are generally topics).  When a trigger is matched, the list of
        keys that lead to the matched trigger (including the current key) is returned.
        
        """
        dict_ = dict_ or self._mod.KEY_MAP
        path = path_ or []
        # See if any keys are triggered by literal in this dict or any of its descendents.
        for k, v in dict_.items():
            # Don't search for a key/value pair unless it's v is a dictionary.
            if isinstance(v, dict):
                # Add the key we are looking at to the path.
                path.append(k)
                # Look for 'Triggers' key, and if it exists, look for literal in the set it points to.
                if 'Triggers' in v and literal in v['Triggers']:
                    # We found a key in this dict, return the path that leads to it.
                    return path
                else:
                    # Let's check in this dict's descendants.
                    path = self.find_path_to_trigger_key(literal, path, v)
                # If no key was triggered in any descendants p will be the same or False.
                if path == path_ or not path:
                    # Path stays the same or is reset, depending on the 
                    # depth of the dictionary (v) we are searching.
                    path = path_ or []
                # If a descendant's key was triggered by literal, p will have been changed.
                else:
                    return path
        if path:
            # If we're here, no descendant's keys were triggered by literal.
            path.pop() # So remove this key from the path.
        return path

    def traverse_keys(self, keys):
        """Traverses the links dictionary of the current module by way of keys.

        Returns the value of the deepest key in keys.
        """
        v = self._mod.LINKS  # Start at the root of the links dict.
        # Find the final value pointed to by keys.
        for key in keys:
            v = v[key]
        return v

    def set_from_key_values(self, dict_=None, set_=None, k_to_collect=None):
        """Returns the set of all values whose keys are all k_to_collect.
        
        Note:  Current implementation requires the value to be a set.

        Works by searching a dictionary for any key equal to k_to_collect and then 
        adds the set for which k_to_collect points to (current implementation expects 
        a set) as a value.

        """
        dict_ = dict_ or self._mod.KEY_MAP
        set_ = set_ or set(())
        k_to_collect = k_to_collect or 'Triggers'

        for k, v in dict_.items():
            # Only look for a key/value pair in a dictionary.
            if isinstance(v, dict):
                if k_to_collect in v:
                    t = v[k_to_collect]
                    set_ |= t
                set_ = self.set_from_key_values(v, set_, k_to_collect)
        return set_

    def _map_triggers_to_paths(self):
        """Returns a dictionary in the form of {'Trigger': {'First Key', 'Second Key'}}.
        
        Setting each trigger as a key in one dictionary at the start of the program 
        increases the processing speed overall.  Searching the INFO.KEY_MAP dictionary
        (calling self.find_path_to_trigger_key) is expensive.

        """
        # Get all triggers as a set.
        triggers = self.set_from_key_values(k_to_collect='Triggers')
        return {trigger: self.find_path_to_trigger_key(trigger) for trigger in triggers}

    def gen_file_from_info(self, filename, func, **kwargs): # TODO: BROKEN!.
        """Writes all values returned by func to filename.txt.
        
        Iterates over the return value of func called with kwargs passed in
        as the parameters.  Filename should end with '.txt' or have no extension.
        Values will be added to the file delimited by a comma, without newlines.
        """
        fn = filename if filename.endswith('.txt') else filename + '.txt'
        with open(fn, 'w') as fd:
            for el in func(kwargs):
                fd.write(','.join(el))

    def remove_subpaths(self, paths):
        """Removes any path within paths that is a subpath of any other path."""
        # Algorithm is much simpler with a sorted list of paths.
        paths.sort()
        # Find all subpaths, i.e. where paths[i] is a sublist of paths[i + 1].
        subpaths = [paths[i] for i in range(len(paths) - 1) \
                    if paths[i] == paths[i + 1][:len(paths[i])]]
        filter(paths.remove, subpaths)
        return paths

    def get_paths(self, trigs):
        """Returns a list of paths given a list of triggers."""
        return [self._trigger_map[t] for t in trigs if t in self._trigger_map]


class ProjectSystemInfoManager(InfoManager):

    """A derived class from InfoManager specific to Project Systems."""

    def get_url_description(self, url):
        """Returns a reformatted string of the last filename in an url.
        
        Grabs the last filename, which is usually the most descriptive of
        a link, from url.  If url matches the expected format, it will extract
        and reformat the name for printing.  If url does not match, False is 
        returned.  
        
        The following is an example of the expected format for
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
    im = ProjectSystemInfoManager('PTVS')
    print(im.set_from_key_values())
    im.gen_file_from_info('triggers_we_hope.txt', im.set_from_key_values)


if __name__ == "__main__":
    main()
