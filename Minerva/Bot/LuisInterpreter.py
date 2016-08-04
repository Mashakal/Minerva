import operator
import string
import sys
import abc
import itertools
import collections
from nltk.corpus import stopwords
from enum import Enum, unique

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

    def _quick_parse(self, text):
        """Parses a string of text to return a list of all words and non-alpha characters."""
        items = []
        breadcrumb = 0
        for i, letter in enumerate(text):
            if not letter.isalpha():
                items.append(text[breadcrumb:i].lower())
                breadcrumb = i + 1
        # Look for a trailing word.
        if text[-1].isalpha():
            items.append(text[breadcrumb:].lower())
        return items


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
    def analyze(self, json):
        """Analyzes the json returned from a call to LuisClient's method, query_raw."""
        self.data = self._format_data(json)
        self._print_from_data() # For development.
        try:
            func = self._HANDLERS[self.data['intent']]
        except KeyError:
            func = self._HANDLERS['None']
        finally:
            return func()


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
        longest_paths = self._longest_paths(interests)
        
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

    def interpret(self, data):
        self.data = data
        if data['status'] is InterpreterStatus.Pending:
        #if data['status'] == 'pending':
            # This is a new query.
            self.data['luis_data']['formatted'] = self._format_data(data['luis_data']['json'])
            #self.data['variables']['proc_index'] = 0
            self._print_from_data()

        # Create the needed intent handler instance.
        intent_handler = LearnAboutTopicHandler(self, self.data)

        while intent_handler.data['status'] is InterpreterStatus.Working:
            intent_handler.run_process()

        return intent_handler.data

    def _format_data(self, json):
        """Formats the raw json into a more easily accessible dictionary."""
        data = {
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
        # Cannot serialize empty sets.
        return {k: v or None for k,v in data.items()}

    def _longest_paths(self, paths):
        """Returns a list of all paths whose size is equal to the longest."""
        try:
            max_len = max(map(len, paths))
        except ValueError:
            # Raised when paths is an empty set.
            max_len = 0
        return list(filter(lambda x: len(x) == max_len, paths))

    def _get_all_topic_matches(self, interests, query):
        """Returns a dictionary of topic/score pairs."""
        # Get all query words that are not also nltk.corpus.stopwords
        filter_out = set(stopwords.words('english'))
        query_words = set(self._quick_parse(query))
        filtered_words = query_words - filter_out
        
        print("Filtered words are: {}".format(filtered_words))

        # Use filtered words to get linient scores.
        linient_scores = self._info.liniently_get_scores(filtered_words)

        print("Linient scores are {}".format(linient_scores))

        # Use interested entities to get strict scores.
        entities = [self.data['luis_data']['formatted'][interest] for interest in interests]
        entities = list(filter(None, entities))
        strict_scores = self._info.strictly_get_scores(entities)

        print("Strict scores are: {}".format(strict_scores))

        # Combine the scores.
        all_scores = {}
        for k,v in linient_scores.items():
            if k in strict_scores:
                all_scores[k] = v + strict_scores[k]
            else:
                all_scores[k] = v
        return all_scores

    def _get_all_paths(self, interests):
        """Returns a dict of interest/path pairs.
       
        Interest is the key.  The path that leads to interest is the
        value.

        """
        all_paths = {}
        triggers = self.data['luis_data']['formatted']
        print("Interests are: {}".format(interests))
        for interest in interests:
            path = self._info.get_paths(self.data['luis_data']['formatted'][interest])
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

    def _get_unfinished_path_message(self, path):
        """Returns a string 'give options' message."""
        end = self._info.traverse_keys(path)
        options = [k for k in end]
        topic = path[len(path) - 1]
        #self.give_acknowledgement(topic)
        message = "For {}, which of these is more closely related to what you're asking about?".format(topic)
        return self._agent.give_options(options, msg=message)

    def _is_path_complete(self, path):
        """True if the path is complete, else False."""
        end = self._info.traverse_keys(path)
        if not isinstance(end, str):
            return False
        return True

    def _print_from_data(self):
        """Prints a predefined set of information from self.data.
        
        This method can easily be overriden to print out whatever is pertinent
        for your application.
        
        """
        for key in ['query', 'intent', 'phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects']:
            print ("  {0}:\t{1}".format(key.upper(), self.data['luis_data']['formatted'][key]))
        print()

    # Intent processes.
    def get_top_scoring_topics(self, interests, top_count, query):
        """Gets the first top_count topics from all matched topics."""
        topic_matches = self._get_all_topic_matches(interests, query)
        print("Topic matches are: {}".format(topic_matches))
        # Sort and filter the topics.
        sorted_scores = sorted(topic_matches.items(), key=operator.itemgetter(1), reverse=True)
        print("Sorted scores are: {}".format(sorted_scores))
        top_topics = list(filter(lambda x: x[1] > 0, sorted_scores))[:top_count - 1]
        print("The top_topics are: {}".format(top_topics))
        return {'next': Next.Continue,
                'top_topics': top_topics}

    def get_paths_from_top_topics(self, top_topics):
        """Finds all unique topics and their paths."""
        unfiltered_paths = self._info.get_paths([t[0] for t in top_topics])
        print("The unfiltered paths are: {}".format(unfiltered_paths))
        filtered_paths = self._info.remove_subpaths(unfiltered_paths)
        print("The filtered paths are: {}".format(filtered_paths))
        return {'next': Next.Continue,
                'filtered_paths': filtered_paths}

    def verify_paths_found(self, filtered_paths):
        """True if at least one path was found, otherwise False."""
        if filtered_paths:
            return {'next': 'continue'}
        else:
            return {'next': Next.Failure,
                    'post': "Luis didn't find any keywords in your query, I'm sorry. In the future, I'll be able to search StackOverflow for you."}

    def evaluate_paths(self, filtered_paths):
        """If the path doesn't point to a str, determine where to go next.
        
        When the path does not point to a str, then it points to a dict
        whose keys are sub-specializations of the last key (topic) in path.
        
        """
        incompletes = []
        completes = []

        for path in filtered_paths:
            end = self._info.traverse_keys(path)
            if not isinstance(end, str):
                incompletes.append(path)
            else:
                completes.append(path)
        _ret = {
            'complete_paths': completes,
            'incomplete_paths': incompletes,
            'next': Next.Continue
        }
        return  _ret
    
    def complete_paths(self, incomplete_paths, path_index):
        _ret = {}
        # Check whether or not we need to do anything.
        while path_index < len(incomplete_paths):
            path = incomplete_paths[path_index]
            # A path might have had a key added since it was marked as incomplete.
            if not self._is_path_complete(path):
                _ret['post'] = self._get_unfinished_path_message(path)
                _ret['next'] = Next.WaitThenContinue
                _ret['path_index'] = path_index
                _ret['options'] = [t for t in self._info.traverse_keys(path)]
                return _ret
            else:
                path_index += 1
        # Reroute when all paths have been completed.
        _ret['next'] = Next.Reroute
        _ret['reroute'] = {'f_attr': 'combine_path_lists'}
        return _ret
    
    def check_input_on_unfinished_path(self, options, input):
        """True when the input is valid."""
        try:
            n = int(input)
        except ValueError:
            passed = False
        # Valid indices start at 1.
        else:
            if n <= 0 or n > len(options):
                passed = False
            else:
                passed = True
        fail_message = "{} is not a valid input.  Please enter a number from 1-{}".format(input, len(options))
        if passed:
            return {
                'next': Next.Continue,
                'chosen_opt': options[n - 1]
            }
        else:
            return {
                'next': Next.WaitThenStay,
                'post': fail_message,
            }
        
    def add_key_to_path(self, incomplete_paths, path_index, chosen_opt):
        """Adds the chosen opt (key) to the incomplete path."""
        incomplete_paths[path_index].append(chosen_opt)
        _ret = {'next': Next.Reroute, 'reroute': {'f_attr': 'complete_paths'}}
        return _ret
    
    def combine_path_lists(self, incomplete, complete):
        """Combines the incomplete adn complete list."""
        complete = incomplete + complete
        return {'next': Next.Continue, "complete_paths": complete}
    
    def get_all_topics(self, paths):
        """Returns the most specialized topic within a path.

        The last key in any path is considered to be the most specialized
        topic for that path, due to the structure of the topics in the
        info.py file's LINKS variable.

        """
        return {
            'next': Next.Continue,
            'topics': [self._topic_from_path(p) for p in paths]
        }

    def get_url_items(self, topics, paths):
        """Get url for all complete paths."""
        urls = {topic: self._info.traverse_keys(paths[i]) for i, topic in enumerate(topics)}
        return {
            'next': Next.Continue,
            'urls': urls
        }

    def make_suggestion(self, url_dict, topics):
        print("\nUrl_Dict is:\n{}".format(url_dict))
        print("\nTopics are:\n{}".format(topics))
        reply = self._agent.suggest_urls([v for k,v in url_dict.items()], topics)
        return {
            'post': reply,
            'next': Next.Complete
        }
   
    # BELOW ARE DEPRECATED (or at least, not currently used).

    def give_acknowledgement(self, items):
        """Output a message acknowledging the topics."""
        return {'next': Next.Continue,
                'post': self._agent.acknowledge(items)}

    def get_all_longest_paths(self, interests):
        """Returns a list of all of the longest paths in a given set of paths.
        
        The first process of procedure _handle_learn.
        
        """
        paths_dict = self._get_all_paths(interests)
        all_paths = [e for k, v in paths_dict.items() if v for e in v]
        filtered_paths = self._info.remove_subpaths(all_paths)
        return {
            'longest_paths': self._longest_paths(filtered_paths),
            'next': Next.Continue
        }


@unique
class Next(Enum):
    # Go to the next procedure.
    Continue = 0
    # Wait for input from the user, then go to the next procedure.
    WaitThenContinue = 1
    # Wait for input from the user, then call the same procedure again.
    WaitThenStay = 2
    # Stop interpreting, end query.
    Failure = 3
    # Stop interpreting, end query.
    Complete = 4
    # Reroute the next process to another function attribute.
    Reroute = 5


@unique
class InterpreterStatus(Enum):
    # Currently in process.
    Working = 0
    # Interpretation finished unsuccessfully.
    Failed = 1
    # Interpretation finished successfully.
    Complete = 2
    # Waiting for input.
    WaitingToStay = 3
    WaitingToContinue = 4
    # A new query needs started.
    Pending = 5


class LearnAboutTopicHandler:
    """Handler for intent Learn About Topic."""

    def __init__(self, obj, data):
        self.obj = obj
        self.procedures = [
            # (Function_Attribute, [data_variable_names], is_msg_needed)
            ('get_top_scoring_topics', ['interests', 'top_count'], True),   # top_topics
            ('get_paths_from_top_topics', ['top_topics'], False),   # filtered_paths
            #('get_all_longest_paths', ['interests'], False),
            ('verify_paths_found', ['filtered_paths'], False),
            ('evaluate_paths', ['filtered_paths'], False),  # completed_paths, incomplete_paths
            ('complete_paths', ['incomplete_paths', 'path_index'], False), # options, path_index - or - None
            ('check_input_on_unfinished_path', ['options'], True), # chosen_opt - or - None
            ('add_key_to_path', ['incomplete_paths', 'path_index', 'chosen_opt'], False),
            ('combine_path_lists', ['incomplete_paths', 'complete_paths'], False),
            ('get_all_topics', ['complete_paths'], False),
            #('give_acknowledgement', ['topics'], False),
            ('get_url_items', ['topics', 'complete_paths'], False),
            ('make_suggestion', ['urls', 'topics'], False)]
        self._load_from_data(data)

    def run_process(self):
        """Runs the current process."""
        proc = self.procedures[self.data['variables']['proc_index']]
        f_attr, v_attr, needs_message = proc
        print("About to try running {}.".format(f_attr))
        args = [self.data['variables'][attr] for attr in v_attr]
        if needs_message:
            args.append(self.data['msg_text'])
        print("Args are: {}".format(*args))
        ret = getattr(self.obj, f_attr)(*args)
        print("Returned by {}".format(f_attr))
        print(ret)
        print("\nVariables are now:\n{}\n\n".format(self.data['variables']))
        self._handle_return(ret)
        self._handle_next(ret)

    def _load_from_data(self, data):
        """Loads the needed information from the data passed in during instantiation."""
        self.data = data
        if data['status'] is InterpreterStatus.Pending:
            # Initialize.
            self.data['variables'] = {
                'interests': ['phrase_jargon', 'single_jargon', 'auxiliaries', 'subjects'],
                'top_count': 3,
                'proc_index': 0,
                'path_index': 0}
        elif data['status'] is InterpreterStatus.WaitingToContinue:
            self.data['variables']['proc_index'] += 1
        self.data['status'] = InterpreterStatus.Working

    # PRIVATE METHODS
        
    def _handle_return(self, ret):
        """Manages the returned object after a process has been called."""
        KEY_ATTRS = ['post', 'next']
        # Look for outgoing.
        if 'post' in ret:
            self._add_outgoing_message(ret['post'])

        # Update variables
        for attr in ret:
            if attr not in KEY_ATTRS:
                self.data['variables'][attr] = ret[attr]

    def _handle_next(self, ret):
        """Determine what to do after a process has been run."""
        if ret['next'] == Next.Failure:
            self.data['status'] = InterpreterStatus.Failed
        elif ret['next'] == Next.Complete:
            self.data['status'] = InterpreterStatus.Complete
        elif ret['next'] == Next.WaitThenStay:
            self.data['status'] = InterpreterStatus.WaitingToStay
        elif ret['next'] == Next.WaitThenContinue:
            self.data['status'] = InterpreterStatus.WaitingToContinue
        elif ret['next'] == Next.Reroute:
            self._reroute(ret['reroute'])
        else:
            # Go to the next process.
            self.data['variables']['proc_index'] += 1

    def _reroute(self, reroute_data):
        """Changes the current procedure index to match the f_attr of reroute_data.

        Currently only changing the function index is implemented.  In the future,
        changing the variables may be added.

        """
        for i, proc in enumerate(self.procedures):
            if proc[0] == reroute_data['f_attr']:
                self.data['variables']['proc_index'] = i

    def _add_outgoing_message(self, message):
        """Adds a message to the outgoing list."""
        try:
            msgs = self.data['outgoing']
        except KeyError:
            msgs = []
        msgs.append(message)
        self.data['outgoing'] = msgs