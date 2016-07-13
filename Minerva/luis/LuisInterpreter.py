import InfoManager
import collections

# For development purposes only:
from Essentials import enter_and_exit_labels, print_smart
import sys

# Constants
# These may be better off in the Bot module.
_YES_WORDS = ['yes', 'yeah', 'okay', 'ok', 'k', 'y', 'ya', 'right', 'correct', "that's right", 'sure', 'for sure']
_NO_WORDS = ['no', 'n', 'nah', 'nope', 'negative']

class BaseLuisInterpreter(object):
    """A base class for all interpreters."""
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def analyze(self, json):
        """Analyzes the json returned from a call to the base LuisClient class's method, query_raw."""
        raise NotImplementedError("Function analyze has not yet been customized.")
     
    def _get_top_scoring_intent(self, json):
        try:
            return json['intents'][0]['intent']
        except LookupError:
            return 'None'

    def _get_literals(self, json):
        return set(([e['entity'] for e in json['entities']]))

    def _get_types(self, json):
        return set(([e['type'] for e in json['entities']]))

    def _literals_given_type(self, t, json):
        return set(([e['entity'] for e in json['entities'] if e['type'] == t]))

    def _literals_given_parent_type(self, parent, json):
        return set(([child['entity'] for child in json['entities'] if parent in child['type']]))

class ProjectSystemLuisInterpreter(BaseLuisInterpreter):
    """Interprets questions for language specific project systems of Visual Studio
    as a part of a help bot.
    """
    def __init__(self, bot, project_system):
        # _info is the main point of access for anything specific to a project
        self._info = InfoManager.ProjectSystemInfoManager(project_system)

        # Use _bot to interact with the user (e.g. ask a question, clarify between options, acknowledge keywords).
        self._bot = bot
        
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
    def _print_from_data(self, data):
        #for k, v in data.items():
        #    print("{0}: {1}".format(k.upper(), v))
        for key in ['query', 'intent', 'phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']:
            print ("  {0}:\t{1}".format(key.upper(), data[key]))
        print()

    def _format_data(self, json):
        """Formats the raw json into a more easily managable dictionary."""
        return {
        # Meta keys - these point to dictionaries.
            'intents': json['intents'],
            'entities': json['entities'],
        # Leaf keys - these point to a value or some container of values.
            'query': json['query'],
            'intent': json['intents'][0]['intent'],
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

    def __get_paths(self, word_set):
        # I die a little inside everytime I look at this function.
        """Get's paths to all words in the set, if a path for it exists.
        Filters the paths found such that only the deepest path will be
        returned, which is helpful when a Luis picks up a trigger to a key
        and also a trigger to a more specialized version of that key in the
        same query.
        """
        def get_paths(word_set):
            """A helper function for __get_paths.  Returns an unfiltered list
            of all the paths pointed to by words in the word set.
            """
            paths = []
            for word in word_set:
                path = self._info.find_path_to_trigger_key(word)
                if path:
                    paths.append(path)
            return paths
        
        def remove_duplicates(paths, key):
            """Remove all but the longest path from paths."""
            list_max = None     # The list with the longest length.
            # Get the paths that contain key.
            with_key = [path for path in paths if key in path]
            # Find the longest one.
            for path in with_key:
                if not list_max or len(path) > len(list_max):
                    list_max = path
            # Remove all lists of paths that are not the one with the longest length.
            [paths.remove(p) for p in with_key if p is not list_max]
            return paths
        
        paths = get_paths(word_set)
        flattened_paths = [p for path in paths for p in path]
        counts = {}
        counter = collections.Counter()
        for key in flattened_paths:
            counter[key] += 1
        for key, count in counter.most_common(): # Get ALL elements in counter.
            if count > 1:
                paths = remove_duplicates(paths, key) 
        # TODO:  Log how many paths were returned, and which ones.
        return paths

    def __get_all_paths(self, interests, data):
        """Returns a dictionary where the interest is the key and a list of
        keys that map to a url is the value.  If no path is found for any
        interest, its value will be None.
        """
        interests = ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']
        all_paths = {}
        for interest in interests:
            path = self._info.get_paths(data[interest])
            path = self._info.remove_subpaths(path)
            all_paths[interest] = path if path else None
        return all_paths

    def __topic_from_path(self, path):
        """Returns the 'topic' of a path, that is, the last key in the list of
        keys in the path."""
        return path[len(path) - 1]

    def __longest_paths(self, paths):
        max_len = 0
        for path in paths:
            if len(path) > max_len:
                max_len = len(path)
        return [path for path in paths if len(path) == max_len]

    def __complete_path(self, path):
        """If the given path does not already point to a string (we assume if it does the string is an url).
        It will ask the user to clarify the remaining topics until a string is reached.
        """
        end = self._info._traverse_keys(path)
        while not isinstance(end, str):
            options = [k for k in end]
            choice = self._bot.give_options(options)
            path.append(choice)
            end = end[choice]
        return path
      
    def _learn_about_topic(self, data):
        """Another try at learn about topic procedure.
        """
        # Find all paths for any topic of interest found in the user's query.
        interests = ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']
        paths_dict = self.__get_all_paths(interests, data)  # Dictionary - interest: paths
        all_paths = self._info.remove_subpaths(paths_dict)  # List of all paths, subpaths removed.

        # Get all of the deepest paths. THIS IS AN AREA WHOSE LOGIC CAN BE IMPROVED.
        longest_paths = self.__longest_paths(all_paths)
        if not longest_paths:
            # Check if we have anything to go on.
            print("Luis didn't find any keywords in your query.  Sorry.")
            print("In the future, I'll be able to try stackoverflow for you.")
            return    

        # Positive or negative acknowledgement.
        topics = [self.__topic_from_path(path) for path in longest_paths]
        self._bot.acknowledge(topics)

        # Map a topic to a corresponding url.
        urls = {topics[i]: self._info.get_url(path) for i, path in enumerate(longest_paths)}
        for i, path in enumerate(longest_paths):
            path = self.__complete_path(path)
            urls[topics[i]] = self._info.get_url(path)

        # Make sure we have an url, otherwise we need some clarification.
        #topics_needing_chosen = {k: v.keys() for k, v in urls.items() if not isinstance(v, str)}
        #for t in topics_needing_chosen:
        #    choice = self._bot.give_options(topics_needing_chosen[t])
            
        # Suggest the url(s).
        self._bot.suggest_multiple_urls(list(urls.values()), list(urls.keys()))

        # Get feedback if an url was suggested.

        # Make additional action based on the feedback.

    # Intent Functions.
    #def _learn_about_topic(self, data):
    #    """Called when the intent is determined to be 'Learn About Topic'.
    #    """
    #    def path_from_topic(paths, topic):
    #        """Returns the first list in paths whose last element matches
    #        topic.
    #        """
    #        for p in paths:
    #            if p[len(p) - 1] == topic:
    #                return p

    #    self._bot.say("It looks like you want to learn about a topic.")
    #    # Petricca may map a keyword to jargon or to auxiliaries, in most cases.
    #    keywords = data['jargon'] | data['auxiliaries']
    #    paths = self._info.get_paths(keywords)
    #    matched_topics = [p[len(p) - 1] for p in paths]
    #    print("Paths: {0}".format(paths))
    #    print("Matched_topics: {0}".format(matched_topics))

    #    if 1 < len(matched_topics):
    #        topic = self._bot.give_options(matched_topics)
    #        path = path_from_topic(topic)
    #    elif 1 == len(matched_topics):
    #        topic = paths[0][len(paths[0]) - 1]
    #        path = paths[0]
    #    else:
    #        # Let's do something worthwhile here.
    #        pass
    #    self._bot.acknowledge(topic)
    #    url = self._info.get_url(topic)
    #    self._bot.suggest_url(url, topic)


            

    def _solve_problem(self, data):
        """Called when the intent is determined to be 'Solve Problem'.
        """
        self._bot.say("It looks like you want to solve a problem.")

    def _get_help(self, data):
        """Called from function 'analyze' when the intent of a LUIS query is determined
        to be 'Get Help'.
        """
        def clarify_paths(paths):
            """Determine which topic is most pertinent to the user
            when more than one unique path is found given the
            user's query.
            """
            # One path is good, as long Luis picked up the right keywords.
            if 1 == len(paths):
                return paths
            elif 1 < len(paths):
                ending_keys = [p[len(p) - 1] for p in paths]
                ans = self._bot.clarify(ending_keys)
                return [p for p in paths for a in ans if p[len(p) - 1] == a]
            else:
                # No paths found.
                return False

        def get_ending_url(path):
            """Given a single path, get to an url.
            """
            u = self._info.traverse_keys(path)
            while not isinstance(u, str):   # Path might not lead to url yet.
                # If our path doesn't point to a key with its own url,
                # ask the user where to go from here.
                keys = list(u.keys())
                # We only need to ask when there is more than one potential key.
                if 1 < len(keys):
                    self._bot.acknowledge(path[len(path) - 1])
                    next = self._bot.give_options([k for k in u.keys()])
                    path.append(next)
                else:
                    path.append(keys[0])
                u = self._info.traverse_keys(path)
            return u

        # Check if the user triggered any links to the wiki page.
        paths = clarify_paths(data['paths'])
        if paths:
            urls = [get_ending_url(path) for path in paths]
            topics = [self._info.get_url_description(u) for u in urls]
            self._bot.acknowledge(topics)
            self._bot.suggest_multiple_urls(urls, topics)
        else:
            # Try StackExchange
            self._bot.say("Hmmm, I'm not sure the wiki can help.\nLet me see what I can find through stackoverflow.\n\n")
            #raise NotImplementedError("Querying stackoverflow is not yet implemented.")
            
    def _none_intent(self):
        self._bot.say("I'm sorry, I don't know what you're asking.")
        

def main():
    import Agent
    inter = ProjectSystemLuisInterpreter(Agent.VSAgent(), 'ptvs')
    trigger_paths = inter._map_triggers_to_paths()
    for path in trigger_paths:
        print("{0}: {1}".format(path, trigger_paths[path]))

if __name__ == "__main__":
    sys.exit(int(main() or 0))