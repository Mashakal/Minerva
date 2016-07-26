import sys
import abc
import itertools
import collections

import InfoManager
import DialogueStrings


class AbstractLuisInterpreter(abc.ABC):

    """An interface-like abstract class for LuisInterpreters."""

    @abc.abstractmethod
    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        raise NotImplementedError


class BaseLuisInterpreter(AbstractLuisInterpreter):

    """A base class for all interpreters."""  
     
    def _get_top_scoring_intent(self, json):
        """Returns the top scoring intent, or the string 'None'."""
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

    def _print_from_data(self):
        """Prints a predefined set of information from self.data.
        
        This method can easily be overriden to print out whatever is pertinent
        for your application.
        
        """
        for key in ['query', 'intent', 'phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']:
            print ("  {0}:\t{1}".format(key.upper(), self.data[key]))
        print()


class ProjectSystemLuisInterpreter(BaseLuisInterpreter):

    """Interprets questions for language specific project systems of Visual Studio."""

    def __init__(self, agent, project_system):
        """Construct an interpreter for the given project_system module."""
        # _info is the main point of access for anything specific to a project.
        self._info = InfoManager.ProjectSystemInfoManager(project_system)

        # Use _agent to interact with the user (e.g. ask a question, clarify 
        # between options, acknowledge keywords).
        self._agent = agent
        
        # Intents point to functions.
        self._HANDLERS = {
            'Solve Problem': self._handle_solve,
            'Learn About Topic': self._handle_learn,
            'None': self._handle_none
        }

    # Entry.
    def analyze(self, json, process_data):
        """Analyzes the json returned from a call to LuisClient's method, query_raw.
        
        This is the only public method of the interpreter.
        
        """
        self._init_data(json)
        self._print_from_data() # For development.
        try:
            func = self._HANDLERS[self.data['intent']]
            func = self.test_api_learn_about_topic
        except KeyError:
            func = self._HANDLERS['None']
        finally:
            return func(process_data)
            
    def _init_data(self, json):
        """Initializes the data attribute."""
        self.data = self._format_data(json)


    # Utility functions.
    def _input_request(func, *args, **kwargs):
        """Creates and processes a request for input from the user.
        
        The func passed in is one of the public methods of self.agent
        that fits the purpose of _input_request (e.g., give_options,
        clarify, ask).  Func is called with args and kwargs as its
        paramters.
        
        """
        pass

    def _format_data(self, json):
        """Formats the raw json into a more easily accessible dictionary."""
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

    def _get_all_paths(self, interests):
        """Returns a dict of interest/path pairs.
       
        Interest is the key.  The path that leads to interest is the
        value.

        """
        all_paths = {}
        for interest in interests:
            path = self._info.get_paths(self.data[interest])
            path = self._info.remove_subpaths(path)
            all_paths[interest] = path
        return all_paths

    def _topic_from_path(self, path):
        """Returns the 'topic' of a path.
        
        The 'topic is the last key in the list of keys in the path.
        This is useful anytime you want to refer to a path as a topic
        instead of a list of keys.
        
        """
        return path[len(path) - 1]

    def _longest_paths(self, paths):
        """Returns a list of all paths whose size is equal to the longest."""
        try:
            max_len = max(map(len, paths))
        except ValueError:
            # Raised when paths is an empty set.
            max_len = 0
        return list(filter(lambda x: len(x) == max_len, paths))

    def _complete_path(self, path):
        """Asks for input from the user to determine which path to take.

        If a path does not point to a string value, assumed to be an url, 
        asks for input from the user to help determine where to go.  This
        is necessary when a trigger is found for a meta-like topic such
        as Projects or Debugging.

        """
        end = self._info.traverse_keys(path)
        # Look for a string (an url).
        while not isinstance(end, str):
            options = [k for k in end]
            # Ask the user where to go from here.
            choice = self._agent.give_options(options)
            path.append(choice)
            end = end[choice]
        return path
    
    
    # Intent processes.
    def get_all_longest_paths(self, interests):
        """Returns a list of all of the longest paths in a given set of paths.
        
        The first process of procedure _handle_learn.
        
        """
        paths_dict = self._get_all_paths(interests)
        all_paths = [e for k, v in paths_dict.items() if v for e in v]
        filtered_paths = self._info.remove_subpaths(all_paths)
        return {
            'rv': self._longest_paths(filtered_paths),
            'save_rv_as': 'longest_paths'
        }

    def verify_paths_found(self, paths):
        """True if at least one path was found, otherwise False."""
        if paths:
            return True
        return False

    def get_all_topics(self, paths):
        """Returns the most specialized topic within a path.

        The last key in any path is considered to be the most specialized
        topic for that path, due to the structure of the topics in the
        info.py file's LINKS variable.

        """
        return [self._topic_from_path(p) for p in paths]

    def give_acknowledgement(self, topics):
        """Output a message acknowledging the topics."""
        self._agent.acknowledge(topics)

    def is_path_complete(self, path):
        """If the path doesn't point to a str, determine where to go next.
        
        When the path does not point to a str, then it points to a dict
        whose keys are sub-specializations of the last key (topic) in path.
                
        """
        end = self._info.traverse_keys(path)
        if not isinstance(end, str):
            # Then end is a dict of specializations.
            return False
        return path

    def complete_all_paths(self, paths):
        """Calls complete_path on each path in paths."""
        pass

    
    # API FUNCTIONS
    def test_api_learn_about_topic(self, process_data):
        """Testing learn_about_topic for the Bot Connector."""
        
        interests = ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']
        longest_paths = self.get_all_longest_paths(interests)
        return 

    # Intent functions.
    def _handle_learn(self):
        """Procedure when the intent is Learn About Topic."""
        # Find all paths for any topic of interest found in the user's query.
        interests = ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']
        longest_paths = self.get_all_longest_paths(interests)
        
        if not longest_paths:
            # Check if we have anything to go on.
            print("Luis didn't find any keywords in your query.  Sorry.")
            print("In the future, I'll be able to try stackoverflow for you.")
            return    

        # Positive or negative acknowledgement.
        topics = [self._topic_from_path(p) for p in longest_paths]
        self._agent.acknowledge(topics)

        # Point all topics to a value, we hope it to be an url.
        urls = {}
        for i, path in enumerate(longest_paths):
            completed = self._complete_path(path)
            if completed:
                urls[topics[i]] = self._info.traverse_keys(completed)

        # Suggest the url(s).
        url_items = [k for k in urls.keys()], [v for v in urls.values()]
        self._agent.suggest_urls(url_items[0], url_items[1])

        # Get feedback if an url was suggested.
        # Make additional action based on the feedback.

        # Return only to indicate the end of method _learn_about_topic.
        return

    def _handle_solve(self):
        """Procedure when the intent is Solve Problem."""
        self._agent.say("It looks like you want to solve a problem.")
           
    def _handle_none(self):
        self._agent.say("I'm sorry, I don't know what you're asking.")


class IntentHandler:
    
    """A handler for a given query, used with LuisInterpreters."""

    def __init__(self, process_list):
        self._process_list = process_list
        self._current_process_index = 0
        self._current_process = self._process_list[self._current_process_index]
        
    def next(self, user_text):
        """Called when text is received from the user and a conversation exists."""
        pass


class LearnAboutTopicHandler:
    """Handler for intent Learn About Topic."""

    def __init__(self, obj, data):
        self.obj = obj
        self.state_data = {
            'variables': {
                'interests': ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']
            }
        }
        self.procedures = [
            ('get_all_longest_paths', self.interests),
            ('verify_paths_found', self.state_data['variables']['longest_paths'],


    def on_return(self, returned):
        """Called to update the state data with the info returned."""
        self.state_data[returned['save_rv_as']] = returned['rv']



class AbstractIntentProcess(abc.ABC):
    
    """An abstract class that acts as an interface for IntentProcesses."""

    @abc.abstractclassmethod
    def call():
        raise NotImplementedError


class IntentProcess(AbstractIntentProcess):

    """A process to be executed by an IntentHandler"""

    def __init__(self, func_attr):
        self.func_attr = func_attr
        self.is_complete = False
        
    def call(self, obj, *args, **kwargs):
        """Calls the function tied to this process."""
        rv = getattr(obj, self.func_attr)(args, kwargs)
        return {'returned': rv}



def main():
    processes = [
        'get_all_longest_paths'




if __name__ == "__main__":
    main()