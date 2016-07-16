import sys
import abc
import itertools

import InfoManager
import collections

# For development purposes only:
from Essentials import enter_and_exit_labels, print_smart


# Constants
# These may be better off in the Bot module.
_YES_WORDS = ['yes', 'yeah', 'okay', 'ok', 'k', 'y', 'ya', 'right', 'correct', "that's right", 'sure', 'for sure']
_NO_WORDS = ['no', 'n', 'nah', 'nope', 'negative']


class BaseLuisInterpreter(abc.ABC):

    """A base class for all interpreters."""
    
    @abc.abstractmethod
    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        raise NotImplementedError("Function analyze has not yet been customized.")
     
    def _get_top_scoring_intent(self, json):
        """Returns the top scoring intent, or None."""
        try:
            return json['intents'][0]['intent']
        except LookupError:
            return 'None'

    def _get_literals(self, json):
        """Returns the set of literals for each entity."""
        return {e['entity'] for e in json['entities']}

    def _get_types(self, json):
        """Returns the set of entity types for each entity."""
        return {e['type'] for e in json['entities']}

    def _literals_given_type(self, t, json):
        """Returns the set of all literals of a certain entity type."""
        return {e['entity'] for e in json['entities'] if e['type'] == t}

    def _literals_given_parent_type(self, parent, json):
        """Returns all literals that are children of entity type parent."""
        return {child['entity'] for child in json['entities'] if parent in child['type']}

    def _print_from_data(self, data):
        """Prints a predefined set of information from data.
        
        This method can easily be overriden to print out whatever is pertinent
        for your application.
        
        """
        for key in ['query', 'intent', 'phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']:
            print ("  {0}:\t{1}".format(key.upper(), data[key]))
        print()


class ProjectSystemLuisInterpreter(BaseLuisInterpreter):

    """Interprets questions for language specific project systems of Visual Studio."""

    def __init__(self, agent, project_system):
        # _info is the main point of access for anything specific to a project
        self._info = InfoManager.ProjectSystemInfoManager(project_system)
        # Use _bot to interact with the user (e.g. ask a question, clarify between options, acknowledge keywords).
        self._agent = agent
        
        # Maps an intent to a function.
        self._STRATAGIES = {
            'Solve Problem': self._solve_problem,
            'Learn About Topic': self._learn_about_topic,
            'None': self._none_intent
        }

    # Entry.
    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        data = self._format_data(json)
        self._print_from_data(data)
        try:
            func = self._STRATAGIES[data['intent']]
        except KeyError:
            func = self._STRATAGIES['None']
        finally:
            func(data)


    # Utility functions.
    def _format_data(self, json):
        """Formats the raw json into a more easily managable dictionary."""
        return {
            # Meta keys - these point to dictionaries.
            'intents': json['intents'],
            'entities': json['entities'],
            # Leaf keys - these point to a value or some container of values.
            'query': json['query'],
            'intent': self._get_top_scoring_intent(json),
            'other_intents': json['intents'][1:],
            'subjects': self._literals_given_type('Subject', json),
            'auxiliaries': self._literals_given_type('Auxiliary', json),
            'negators': self._literals_given_type('Negator', json),
            'gerunds': self._literals_given_type('Action::Gerund', json),
            'conjugated_verbs': self._literals_given_type('Action::Conjugated Verb', json),
            'all_jargon': self._literals_given_parent_type('Jargon::', json),
            'phrase_jargon': self._literals_given_type('Jargon::Phrase', json),
            'single_jargon': self._literals_given_type('Jargon::Single Word', json),
            'solve_problem_triggers': self._literals_given_parent_type('Solve Problem Triggers::', json)
        }

    def _get_paths(self, word_set):
        """Retrieves a list of keys that can be used to traverse an info file's links.

        Filters the paths found such that only the deepest path will be
        returned, which is helpful when LUIS picks up a trigger to a key
        and also a trigger to more specialized version of that same key.

        """     
        #def remove_duplicates(paths, key):
        #    """Remove all but the longest path from paths."""
        #    # Get the paths that contain key.
        #    with_key = [path for path in paths if key in path]
        #    # Find the longest one.
        #    for path in with_key:
        #        if not list_max or len(path) > len(list_max):
        #            list_max = path
        #    # Remove all lists of paths that are not the one with the longest length.
        #    [paths.remove(p) for p in with_key if p is not list_max]
        #    return paths
        
        paths = filter(self._info.find_path_to_trigger_key, word_set)
        flat_paths = itertools.chain.from_iterable(paths)
        #counter = collections.Counter(flat_paths)
        max_ = max(map(len, flat_paths)) 
        paths = filter(lambda x: len(x) == max_, flat_paths)
        #for key, count in counter.most_common(): # Get ALL elements in counter.
        #    if count > 1:
        #        paths = remove_duplicates(paths, key) 
        # TODO:  Log how many paths were returned, and which ones.
        return paths

    def _get_all_paths(self, interests, data):
        """Returns a dictionary where the interest is the key and a list of
        keys that map to a url is the value.  If no path is found for any
        interest, its value will be None.
        """
        interests = ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']
        all_paths = {}
        for interest in interests:
            path = self._info.get_paths(data[interest])
            path = self._info.remove_subpaths(path)
            all_paths[interest] = path or None
        return all_paths

    def _topic_from_path(self, path):
        """Returns the 'topic' of a path, that is, the last key in the list of
        keys in the path."""
        return path[len(path) - 1]

    def _longest_paths(self, paths):
        max_len = 0
        for path in paths:
            if len(path) > max_len:
                max_len = len(path)
        return [path for path in paths if len(path) == max_len]

    def _complete_path(self, path):
        """If the given path does not already point to a string (we assume if it does the string is an url).
        It will ask the user to clarify the remaining topics until a string is reached.
        """
        end = self._info.traverse_keys(path)
        while not isinstance(end, str):
            options = [k for k in end]
            choice = self._agent.give_options(options)
            path.append(choice)
            end = end[choice]
        return path
      
               
    # Intent functions.
    def _learn_about_topic(self, data):
        """Another try at learn about topic procedure.
        """
        # Find all paths for any topic of interest found in the user's query.
        interests = ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']
        paths_dict = self._get_all_paths(interests, data)  # Dictionary - interest: paths
        all_paths = self._info.remove_subpaths(paths_dict)  # List of all paths, subpaths removed.

        # Get all of the deepest paths. THIS IS AN AREA WHOSE LOGIC CAN BE IMPROVED.
        longest_paths = self._longest_paths(all_paths)
        if not longest_paths:
            # Check if we have anything to go on.
            print("Luis didn't find any keywords in your query.  Sorry.")
            print("In the future, I'll be able to try stackoverflow for you.")
            return    

        # Positive or negative acknowledgement.
        topics = [self._topic_from_path(path) for path in longest_paths]
        self._agent.acknowledge(topics)

        # Map a topic to a corresponding url.
        urls = {topics[i]: self._info.get_url(path) for i, path in enumerate(longest_paths)}
        for i, path in enumerate(longest_paths):
            # Complete any path that doesn't point to an url.
            path = self._complete_path(path)
            urls[topics[i]] = self._info.get_url(path)

        # Suggest the url(s).
        self._agent.suggest_multiple_urls(list(urls.values()), list(urls.keys()))

        # Get feedback if an url was suggested.

        # Make additional action based on the feedback.

    def _solve_problem(self, data):
        """Called when the intent is determined to be 'Solve Problem'.
        """
        self._agent.say("It looks like you want to solve a problem.")
           
    def _none_intent(self):
        self._agent.say("I'm sorry, I don't know what you're asking.")
        

def main():
    import Agent
    inter = ProjectSystemLuisInterpreter(Agent.VSAgent(), 'ptvs')
    trigger_paths = inter._map_triggers_to_paths()
    for path in trigger_paths:
        print("{0}: {1}".format(path, trigger_paths[path]))

if __name__ == "__main__":
    main()