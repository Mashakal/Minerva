import sys
import importlib
import itertools


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

    def liniently_get_scores(self, words):
        """Returns a dict of count of the number of times a trigger was liniently triggered by words."""
        scores = {}
        for k in self._trigger_map:
            scores[k] = 0
            for word in words:
                if word in k.lower().split(' '):
                    scores[k] += 1
        return {k:v for k,v in scores.items() if v > 0}

    def strictly_get_scores(self, entities):
        """Returns a dict of the number of times a trigger was strictly triggered by words."""
        MATCH_VALUE = 3
        scores = {}
        for entity in itertools.chain.from_iterable(entities):
            for k in self._trigger_map:
                if entity == k:
                    scores[k] = entity.count(' ') + MATCH_VALUE
                    break
        return {k:v for k,v in scores.items() if v > 0}

    def find_path_to_trigger_key(self, literal, path_=None, dict_=None):
        """Returns a list of keys that will lead to information on literal.

        The list comes from searching INFO.KEY_MAP for a specific key's set of 
        triggers (keys are generally topics).  When a trigger is matched, the 
        list of keys that lead to the matched trigger (including the current 
        key) is returned.
        
        """
        dict_ = dict_ or self._mod.KEY_MAP
        path = path_ or []
        # See if any keys are triggered by literal in this dict or 
        # any of its descendents.
        for k, v in dict_.items():
            # Don't search for a key/value pair unless v is a dictionary.
            if isinstance(v, dict):
                # Add the key we are looking at to the path.
                path.append(k)
                # Look for 'Triggers' key, and if it exists,
                # look for literal in the set it points to.
                if 'Triggers' in v and literal in v['Triggers']:
                    # We found a key in this dict,
                    # return the path that leads to it.
                    return path
                else:
                    # Let's check in v's descendants.
                    path = self.find_path_to_trigger_key(literal, path, v)
                # If no key was triggered in any descendants p will be 
                # the same or False.
                if path == path_ or not path:
                    # Path stays the same or is reset, depending on the 
                    # depth of the dictionary (v) we are searching.
                    path = path_ or []
                # If a descendant's key was triggered by literal, p will 
                # have been changed.
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
            try:
                v = v[key]
            except KeyError:
                raise ValueError("Illegal path list.  This list cannot be traversed: {}".format(keys))
        return v

    def set_from_key_values(self, k_to_collect, dict_=None, set_=None):
        """Returns the set of all values whose keys are all k_to_collect.
        
        Note:  Current implementation requires the value to be a set.

        Works by searching a dictionary for any key equal to k_to_collect 
        and then adds the set for which k_to_collect points to (current 
        implementation expects a set) as a value.

        """
        dict_ = dict_ or self._mod.KEY_MAP
        set_ = set_ or set(())
        
        for k, v in dict_.items():
            # Only look for a key/value pair in a dictionary.
            if isinstance(v, dict):
                if k_to_collect in v:
                    t = v[k_to_collect]
                    set_ |= t
                set_ = self.set_from_key_values(k_to_collect, v, set_)
        return set_

    def gen_file_from_info(self, filename, func, delim='\n', *args, **kwargs):
        """Writes all values returned by func to filename.txt.
        
        Uses delim to join the return value of func called using both
        args and kwargs.  Filename should end with '.txt' or have no 
        extension.  Values will be added to the file delimited by delim, 
        with a default of '\n'.

        """
        with open(filename, 'w') as fd:
            fd.write(delim.join(func(*args, **kwargs)))

    def remove_subpaths(self, paths):
        """Removes any path within paths that is a subpath of any other path."""
        # Algorithm is much simpler when the list of paths is sorted.
        if not paths:
            return []
        paths.sort()
        # Find all subpaths, i.e. where paths[i] is a sublist of paths[i + 1].
        subpaths = [paths[i] for i in range(len(paths) - 1) \
                    if paths[i] == paths[i + 1][:len(paths[i])]]
        filter(paths.remove, subpaths)
        return paths

    def get_paths(self, topics):
        """Returns a list of paths given a list of trigger literals from a user's query."""
        if topics:
            return [self._trigger_map[t] for t in topics if t in self._trigger_map]
        return None

    def _map_triggers_to_paths(self):
        """Returns a dictionary of triggers as key and their paths as values.
        
        Setting each trigger as a key in one dictionary at the start of the 
        program increases the processing speed overall.  Searching the 
        INFO.KEY_MAP dictionary (calling self.find_path_to_trigger_key) is 
        expensive.

        """
        triggers = self.set_from_key_values('Triggers')
        return {trigger: self.find_path_to_trigger_key(trigger) \
                for trigger in triggers}



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
        if last > -1:
            s = url[last + 1:]
            s = s.replace('-', ' ')
            s = s.replace('#', ': ')
        return s or False