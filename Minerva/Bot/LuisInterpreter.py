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
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        self.data = self._format_data(json)
        self._print_from_data() # For development.
        try:
            func = self._HANDLERS[self.data['intent']]
            func = self.test_api_learn_about_topic
        except KeyError:
            func = self._HANDLERS['None']
        finally:
            return func(process_data)


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


class ApiProjectSystemLuisInterpreter(BaseLuisInterpreter):

    def __init__(self, agent, project_system):
        """Construct an interpreter for the given project_system module."""
        # _info is the main point of access for anything specific to a project.
        self._info = InfoManager.ProjectSystemInfoManager(project_system)

        # Use _agent to interact with the user (e.g. ask a question, clarify 
        # between options, acknowledge keywords).
        self._agent = agent
        
    def analyze(self):
        pass

    def interpret(self, state_data):
        if not 'state' in state_data:
            # This is a new query.
            self.interp_data = {}
            self.interp_data['json'] = state_data['query_json']
            self.interp_data['json_data'] = self._format_data(self.interp_data['json'])
            self.interp_data['proc_index'] = 0
        else:
            self.interp_data = state_data

        # Create the needed intent handler instance.
        intent_handler = LearnAboutTopicHandler(self, self.interp_data)
        
        # Set the interpreter state to working.
        #self.interp_data.set_state('working')

        while intent_handler.data['status'] == 'working':
            intent_handler.run_process()

        return intent_handler.get_data()


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

    # Intent processes.
    def get_all_longest_paths(self, interests):
        """Returns a list of all of the longest paths in a given set of paths.
        
        The first process of procedure _handle_learn.
        
        """
        paths_dict = self._get_all_paths(interests)
        all_paths = [e for k, v in paths_dict.items() if v for e in v]
        filtered_paths = self._info.remove_subpaths(all_paths)
        return {
            'longest_paths': self._longest_paths(filtered_paths),
            'next': 'continue'
        }

    def verify_paths_found(self, paths):
        """True if at least one path was found, otherwise False."""
        if paths:
            return {'next': 'continue'}
        else:
            return {
                'next': 'fail',
                'post': '  \n'.join(["Luis didn't find any keywords in your query, I'm sorry.",
                                    "In the future, I'll be able to search StackOverflow for you."])
            }

    def get_all_topics(self, paths):
        """Returns the most specialized topic within a path.

        The last key in any path is considered to be the most specialized
        topic for that path, due to the structure of the topics in the
        info.py file's LINKS variable.

        """
        return {
            'next': 'continue',
            'topics': [self._topic_from_path(p) for p in paths]
        }

    def give_acknowledgement(self, topics):
        """Output a message acknowledging the topics."""
        return {
            'next': 'continue',
            'post': self._agent.acknowledge(topics)
        }

    def find_complete_paths(self, paths):
        """If the path doesn't point to a str, determine where to go next.
        
        When the path does not point to a str, then it points to a dict
        whose keys are sub-specializations of the last key (topic) in path.
                
        """
        incompletes = []
        for i, path in enumerate(paths):
            end = self._info.traverse_keys(path)
            if not isinstance(end, str):
                # Then end is a dict of specializations.
                if 'Home' in end:
                    paths[i].append('Home')
                else:
                    paths.pop(i)
                    incompletes.append(path)
        return {
            'complete_paths': paths,
            'incomplete_paths': incompletes,
            'next': 'continue'
        }

    def get_url_items(self, topics):
        """Get url for all complete paths."""
        urls = {topic: self._info.traverse_keys(topic) for topic in topics}
        return {
            'next': 'continue',
            'urls': urls
        }

    def suggest_urls(self, urls):
        return {
            'post': self._agent.give_options(urls, msg="Visit the following:"),
            'next': 'complete'
        }

    def complete_unfinished_paths(self, unfinished_paths, current_path_index=0):
        """Asks the user where to go from here."""
        path = unfinished_paths[current_path_index]
        end = self._info.traverse_keys(path)
        options = [k for k in end]
        reply = self._agent.give_options(options)
        return {
            'next': 'waiting',
            'reply': reply,
            'options': options,
            'current_path_index': current_path_index
        }

    def check_input_on_unfinished_path(self, input, options):
        """True when the input is valid."""
        try:
            n = int(input)
        except ValueError:
            passed = False
        # Valid indices start at 1.
        else:
            if n < 0 or n > len(options):
                passed = False
            else:
                passed = True
        return {
            'passed': passed
        }
    

class LearnAboutTopicHandler:
    """Handler for intent Learn About Topic."""

    def __init__(self, obj, data):
        self.obj = obj
        self.variables = {
            'interests': ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects'],
            'longest_paths': [],
            'topics': [],
        }
        self._data = {'variables': self.variables}
        self.procedures = [
            # (Function_Attribute, [variable_names])
            ('get_all_longest_paths', ['interests']),
            ('verify_paths_found', ['longest_paths']),
            ('get_all_topics', ['longest_paths']),
            ('find_complete_paths', ['longest_paths']),
            ('get_url_items', ['topics']),
            ('suggest_urls', ['urls'])
            #('complete_unfinished_paths', ['unfinished_paths', 'current_path_index']),
            #('check_input_on_unfinished_path', ['input', 'options'])
        ]
        self.proc_index = data['proc_index']
        self.data = data
        self.data['status'] = 'working'
        
    def get_data(self):
        """Updates and returns the handler's data."""
        self._data['variables'] = self.variables
        self.data['proc_index'] = self.proc_index
        return self.data.update(self._data)

    def run_process(self):
        """Runs the current process."""
        proc = self.procedures[self.proc_index]
        f_attr, v_attr = proc
        print("About to try running {}.".format(f_attr))
        print(self.variables[v_attr])

        if len(v_attr) <= 1:
            ret = getattr(self.obj, f_attr)(self.variables[v_attr])
        else:
            ret = getattr(self.obj, f_attr)(*[self.variables[attr] for attr in v_attr])
        self.handle_return(ret)
        self.handle_next(ret)

        
    def handle_return(self, ret):
        """Manages the returned object after a process has been called."""
        KEY_ATTRS = ['post', 'next']
        # Look for outgoing.
        if 'post' in ret:
            self._add_outgoing_message(ret['post'])

        # Update variables
        for attr in ret:
            if attr not in KEY_ATTRS:
                self.variables[attr] = ret[attr]

    def handle_next(self, ret):
        """Determine what to do after a process has been ran."""
        if ret['next'] == 'fail':
            self.data['status'] = 'failed'
        elif ret['next'] == 'complete':
            self.data['status'] = 'complete'
        else:
            self.proc_index += 1

        
    def _add_outgoing_message(self, message):
        """Adds a message to the outgoing list."""
        try:
            msgs = self.data['outgoing']
        except KeyError:
            msgs = []
        msgs.append(message)
        self.data['outgoing'] = msgs



class IntentProcess:

    """A process to be executed by an IntentHandler."""

    def __init__(self, func_attr, var_names, vars_dict):
        # The string value of a callable object.
        self.func_attr = func_attr
        self.vars = [vars_dict[attr] for attr in var_names]
        
        # A list of vars named as strings for each var 
        # accepted by func_attr.
        self.accepts = var_names
        
    def call(self, obj, *args, **kwargs):
        """Calls the function tied to this process."""
        rv = getattr(obj, self.func_attr)(args, kwargs)
        return {'returned': rv}


class InterpreterData:
    
    """A container for LuisInterpreter data."""

    _STATES = {
        'initializing': 'initializing',
        'initialized': 'initialized',
        'working': 'working',
        'waiting': 'waiting',
        'finished': 'finished'
    }

    def __init__(self, data=None):
        object.__setattr__(self, '_data', data or {})
        self.set_state('initializing')

    def __getattr__(self, attr):
        try:
            v = self._data[attr]
        except KeyError:
            v = getattr(self, attr, None)
        finally:
            return v

    def __setattr__(self, attr, value):
        self._data[attr] = value

    def set_state(self, value):
        """Sets the appropriate state based on value.

        Will raise a ValueError when the given value is not
        an appropriate key for InterpreterData.STATES.

        """
        # TODO:  We should save this through the api.
        try:
            self._data['state'] = InterpreterData._STATES[value]
        except KeyError:
            raise ValueError("{} is not a valid state.".format(value))
    
def main():
    data = InterpreterData()
    print(data.state)
    data.set_state('working')
    print(data.state)
    

    

if __name__ == "__main__":
    main()