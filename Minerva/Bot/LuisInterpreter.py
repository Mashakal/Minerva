import warnings
import json
import operator
import string
import sys
import abc
import itertools
import collections
from enum import Enum, unique
from nltk.corpus import stopwords

import InfoManager
import DialogueStrings
import HelpBot
import Query
import LuisClient


#region Enumerations

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


#region Interpreters

class AbstractLuisInterpreter(abc.ABC):

    """An interface-like abstract class for LuisInterpreters."""

    @abc.abstractmethod
    def interpret(self, json):
        """Interprets a user's query."""
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
        for attr_name in sorted(LuisClient.MODEL_ENTITY_SCHEMA):
            print("{}: {}".format(attr_name, getattr(self.luis_data, attr_name)))
        print()

    def _quick_parse(self, text):
        """Parses a string of text to return a list of all words and non-alpha characters."""
        items = []
        breadcrumb = 0
        for i, letter in enumerate(text):
            if not letter.isalpha():
                items.append(text[breadcrumb:i].lower())
                breadcrumb = i + 1
        # Look for a trailing word when there is no trailing punctuation.
        if text[-1].isalpha():
            items.append(text[breadcrumb:].lower())
        return items


class ProjectSystemLuisInterpreter(BaseLuisInterpreter):

    """Interprets questions for language specific project systems of Visual Studio."""

    def __init__(self, agent, project_system):
        """Construct an interpreter for the given project_system module."""
        self._info = InfoManager.ProjectSystemInfoManager(project_system)
        self._agent = agent
        # Intents point to handlers.
        self._HANDLERS = {'Solve Problem': self._handle_solve,
                          'Learn About Topic': self._handle_learn,
                          'None': self._handle_none}

    # Entry.
    def interpret(self, json):
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
        self._info = InfoManager.ProjectSystemInfoManager(project_system)
        self._agent = agent
        self._handlers = {'Learn About Topic': LearnAboutTopicHandler,
                          'Solve Problem': SolveProblemHandler,
                          'Debugging Help': DebuggingHelpHandler,
                          'Get Opinion': GetOpinionHandler}

    def interpret(self, data):
        self.data = data
        self.luis_data = data['luis_data']

        assert isinstance(self.luis_data, HelpBot.LuisData)

        #if data['status'] is InterpreterStatus.Pending:
        #    # This is a new query.
        #    self.data['luis_data']['formatted'] = self._format_data(data['luis_data']['json'])

        _Handler = self._handlers.get(self.luis_data.top_intent(), DefaultHandler)
        intent_handler = _Handler(self, self.data)
        self.luis_data.load_words_of_interest(self.data['variables']['interests'])
        self._print_from_data()
        print(json.dumps(self.data['luis_data'], indent=3, sort_keys=True, cls=HelpBot.DataEncoder))

        # Work the query.
        while intent_handler.data['status'] is InterpreterStatus.Working:
            intent_handler.run_process()
        
        # Return updated data.
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
            'negators': set(map(lambda x: x.replace(" ", ""), 
                                 self._literals_given_type('Negator', json))),
            'gerunds': self._literals_given_type('Action::Gerund', json),
            'conjugated_verbs': self._literals_given_type('Action::Conjugated Verb', json),
            'all_action': self._literals_given_parent_type('Action::', json),
            'all_jargon': self._literals_given_parent_type('Jargon::', json),
            'phrase_jargon': self._literals_given_type('Jargon::Phrase', json),
            'single_jargon': self._literals_given_type('Jargon::Single Word', json),
            'solve_problem_triggers': self._literals_given_parent_type('Solve Problem Triggers::', json)
        }
        return data

    def _longest_paths(self, paths):
        """Returns a list of all paths whose size is equal to the longest."""
        try:
            max_len = max(map(len, paths))
        except ValueError:
            # Raised when paths is an empty set.
            max_len = 0
        return list(filter(lambda x: len(x) == max_len, paths))

    def _filter_stopwords(self, to_filter):
        """Removes stopwords from to_filter."""
        filter_out = set(stopwords.words('english'))
        word_set = set(to_filter)
        return word_set - filter_out

    def _get_all_topic_matches(self, query):
        """Returns a dictionary of topic/score pairs."""
        # NLTK package (stopwords) raises ResourceWarning.
        warnings.simplefilter("ignore", ResourceWarning)

        # Get all query words that are not also nltk.corpus.stopwords
        self.filter_out = set(stopwords.words('english'))
        query_words = set(self._quick_parse(query))
        filtered_words = query_words - self.filter_out
        print("Filtered Words: {}".format(filtered_words))
        # Use filtered words to get linient scores.
        linient_scores = self._info.liniently_get_scores(filtered_words)
        print("Linient scores: {}".format(linient_scores))

        print("Words of interest: {}".format(self.luis_data.words_of_interest))
        strict_scores = self._info.strictly_get_scores(self.luis_data.words_of_interest)
        print("Strict scores: {}".format(strict_scores))
        # Combine the scores.
        matches = []
        for k,v in linient_scores.items():
            score, path = v
            match = InfoManager.TopicMatch(k, score)
            if k in strict_scores:
                match.score += strict_scores[k][0] # score
            match.path = path
            matches.append(match)
        return matches

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
       
    def _outgoing_message(self, message):
        """Construct and send a message to the user."""
        return {'next': Next.Continue, 
                'post': self._agent.say(message)}

    # Intent processes.
    # Default.
    def default_fail(self):
        return {'next': Next.Failure,
                'post': self._agent.say("I'm sorry, but I don't think I can help you with that.")}

    # Get Opinion
    def opinion_message(self):
        return {'next': Next.Complete,
                'post': self._agent.say("Sorry, but my opinion isn't worth much ... _yet_.")}

    # Solve Problem.
    def send_solve_problem_acknowledgement(self):
        """Sends a acknowledgement to the user."""
        message = "Let me see what I can find about this on StackOverflow.com."
        return self._outgoing_message(message)

    def get_stackexchange_query_params(self, query_text):
        """Returns a dict of stackexchange query parameters."""
        strict_params = {
            'tagged': self.luis_data.all_jargon + \
                      (self.luis_data.services or []) + \
                      (self.luis_data.metas or []) + \
                      (self.luis_data.frameworks or []),
            'intitle': self.luis_data.intent_descripters
        }
        self.raw_tags = strict_params['tagged']
        return {'next': Next.Continue, 
                'strict_params': strict_params}

    def create_stackexchange_query(self, params):
        """Creates an sends a stackexchange query."""
        query_responses = []
        query = Query.StackExchangeQuery('stackoverflow', query_params=params)
        query.set_query_path(Query.QueryPaths.AdvancedSearch)
        return {'next': Next.Continue, 'query': query}

    def get_query_responses(self, query):
        """Returns a list of query responses."""
        query.initiate()
        # Did we get any responses?
        if not query.response.result_count:
            popped = query.query_string.tagged.pop()
            print("POPPED IS: {}".format(popped))
        else:
            return {'next': Next.Continue, 'query_response': query.response}
        # If not, try a more linient query if possible, otherwise fail.
        if not popped:
            return {'next': Next.Failure, 'post': "Couldn't find anything."}
        else:
            # Try to find queries that at least have the popped tag in the body.
            #query.query_string.add_param('body', popped)
            pass
        return self.get_query_responses(query)
        
    def print_responses(self, response):
        """Prints all records in a query response."""
        response.print_results()
        return {'next': Next.Continue}

    def score_responses(self, query_response, query_text):
        for r in query_response.results:
            r.combine_scores(self.filter_out, self.raw_tags, query_text)
        sorted_results = sorted(query_response.results, key=operator.attrgetter('combined_score'), reverse=True)[:5]
        return {'next': Next.Continue,
                'sorted_results': sorted_results}

    def suggest_results(self, sorted_results):
        """Output a message suggesting the top results."""
        return {'next': Next.Complete,
                'post': self._agent.suggest_stackexchange_results(sorted_results)}
    

    # Learn about topic.
    def get_top_matches(self, top_count, query):
        """Gets the first top_count topics from all matched topics."""
        MIN_SCORE = 2
        topic_matches = self._get_all_topic_matches(query)
        # Sort and filter the topics by score.
        sorted_scores = sorted(topic_matches, key=operator.attrgetter('score'), reverse=True)
        top_matches = list(filter(lambda x: x.score >= MIN_SCORE, sorted_scores))[:top_count]
        print("The top matches are: {}".format(top_matches))
        # Filter by path.
        top_matches = self._info.remove_subpaths(top_matches)
        return {'next': Next.Continue,
                'top_matches': top_matches}

    def verify_matches_found(self, top_matches):
        """True if at least one path was found, otherwise False."""
        if top_matches:
            return {'next': 'continue'}
        else:
            return {'next': Next.Failure,
                    'post': "I'm sorry.  I can't seem to find anything to help with that."}

    def evaluate_paths(self, top_matches):
        """If the path doesn't point to a str, determine where to go next.
        
        When the path does not point to a str, then it points to a dict
        whose keys are sub-specializations of the last key (topic) in path.
        
        """
        incompletes = []
        completes = []

        for match in top_matches:
            end = self._info.traverse_keys(match.path)
            if not isinstance(end, str):
                incompletes.append(match)
            else:
                completes.append(match)
        _ret = {
            'complete_matches': completes,
            'incomplete_matches': incompletes,
            'next': Next.Continue
        }
        return  _ret
    
    def complete_matches(self, incomplete_matches, match_index):
        _ret = {}
        # Check whether or not we need to do anything.
        while match_index < len(incomplete_matches):
            match = incomplete_matches[match_index]
            # A path might have had a key added since it was marked as incomplete.
            if not self._is_path_complete(match.path):
                options = [t for t in self._info.traverse_keys(match.path)]
                # We don't need any user input if there's only one option.
                if len(options) == 1:
                    match.path.append(options[0])
                    self.complete_matches(incomplete_matches, match_index)
                _ret['post'] = self._get_unfinished_path_message(match.path)
                _ret['next'] = Next.WaitThenContinue
                _ret['match_index'] = match_index
                _ret['options'] = options
                return _ret
            else:
                match_index += 1
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
        
    def add_key_to_path(self, incomplete_matches, match_index, chosen_opt):
        """Adds the chosen opt (key) to the incomplete path."""
        incomplete_matches[match_index].path.append(chosen_opt)
        _ret = {'next': Next.Reroute, 'reroute': {'f_attr': 'complete_matches'}}
        return _ret
    
    def combine_path_lists(self, incomplete, complete):
        """Combines the incomplete adn complete list."""
        complete = incomplete + complete
        return {'next': Next.Continue, 
                'complete_matches': complete}
    
    def get_all_topics(self, matches):
        """Returns the most specialized topic within a path.
        The last key in any path is considered to be the most specialized
        topic for that path, due to the structure of the topics in the
        info.py file's LINKS variable.
        """
        topics = [self._topic_from_path(m.path) for m in matches]
        print("Topics are: {}".format(topics))
        return {
            'next': Next.Continue,
            'topics': topics
        }

    def get_url_items(self, topics, matches):
        """Get url for all complete paths."""
        urls = {topic: self._info.traverse_keys(matches[i].path) for i, topic in enumerate(topics)}
        return {
            'next': Next.Continue,
            'urls': urls
        }

    def make_suggestion(self, url_dict):
        reply = self._agent.suggest_urls(url_dict)
        return {
            'post': reply,
            'next': Next.Complete
        }

    def fail_for_delete(self):
        """Terminates the query with a failure."""
        return {'next': Next.Failure, 'post': 'Quitting as expected.'}


    # Debugging Help
    def determine_debug_topic(self, top_matches):
        top_match = top_matches[0]
        if top_match.topic in ['Remote Debugging']:
            ret_ = {'primary_topic': DebugTopic.Remote}
        elif top_match.topic in ['Mixed-Mode/Native Debugging']:
            ret_ = {'primary_topic': DebugTopic.MixedMode}
        elif top_match.topic in ['Basic Debugging']:
            ret_ = {'primary_topic': DebugTopic.General}
        else:
            ret_ = {'primary_topic':  DebugTopic.Unidentified}
        ret_.update(next=Next.Continue)
        return ret_

    def determine_secondary_intent(self):
        try:
            intent = self.luis_data.intents[1]
        except LookupError:
            intent = 'Learn About Topic'
        finally:
            if intent == 'Solve Problem':
                secondary_intent = DebugTopic.SolveProblem
            elif intent == 'Learn About Topic':
                secondary_intent = DebugTopic.LearnAbout
            else:
                # Do what? Default to LearnAbout...?
                secondary_intent = DebugTopic.LearnAbout
        return {'next': Next.Continue,
                'secondary_intent': secondary_intent}

    def filter_from_primary_topic(self, primary_topic, secondary_intent):
        ret_ = {}
        # Handle Remote.
        if primary_topic is DebugTopic.Remote:
            if self._search_for_substrings(SubstringLibrary.Cloud):
                primary_topic = DebugTopic.RemoteAzure
            else:
                primary_topic = DebugTopic.RemoteCrossPlatform

        # Handle Mixed-Mode.
        elif primary_topic is DebugTopic.MixedMode:
            self._handle_mixed_mode(secondary_intent)
                

        ret_ = {'debug_topic': primary_topic}
        return

    def _handle_mixed_mode(self, secondary_intent):
        if secondary_intent is DebugTopic.SolveProblem:
            not_python = filter(lambda lang: not 'pyth' in lang,
                            self.luis_data.languages)
            param_tags = ['debugging', 'mixed-mode']
            if not_python:
                # Query tags for SE query, each matched language.
                param_tags += list(not_python)
            query = self.create_stackexchange_query({'tagged': param_tags})
            return {'next': Next.Reroute,
                    'reroute': {'f_attr': 'get_query_responses'},
                    'query': query}
        else:
            s = "It looks like you want to debug in a multi-language environment."

    def _search_for_substrings(self, substrings):
        """Searches the words of interest for any substring in stubstrings."""
        data_words = list(self.luis_data.words_of_interest)
        for sub in substrings:
            if any(sub in e for e in data_words):
                return True
   

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
class SubstringLibrary(Enum):
    Cloud = ['web',
             'azure',
             'cloud',
             'deployed',
             'aws']

@unique
class DebugTopic(Enum):
    General = 1
    Remote = 2
    MixedMode = 3
    RemoteAzure = 4
    RemoteCrossPlatform = 5
    Unidentified = 6
    SolveProblem = 7
    LearnAbout = 8


#region Intent Handlers

class AbstractBaseHandler:
    
    """A base class to handle Luis determined intents."""

    def __init__(self, obj, data):
        self.obj = obj
        self.procedures = [
            ('default_fail', [], False)
        ]
        self._load_from_data(data)

    def run_process(self):
        """Runs the current process."""
        print('\n')
        proc = self.procedures[self.data['variables']['proc_index']]
        f_attr, v_attr, needs_message = proc
        print("RUNNING:\n   {}".format(f_attr))
        args = [self.data['variables'][attr] for attr in v_attr]
        if needs_message:
            args.append(self.data['msg_text'])
        print('\n   '.join(["ARGS:"] + ["{}"] * len(args)).format(*args))
        ret = getattr(self.obj, f_attr)(*args)
        print("RETURNED:")
        print(json.dumps(ret, sort_keys=True, indent=3, cls=HelpBot.DataEncoder))
        self._handle_return(ret)
        self._handle_next(ret)

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

    def _load_from_data(self, data):
        self.data = data
        self.data['variables'] = {'proc_index': 0, 'interests': []}
        self.data['status'] = InterpreterStatus.Working


class DefaultHandler(AbstractBaseHandler):

    """Handles the default case."""

    pass


class LearnAboutTopicHandler(AbstractBaseHandler):

    """Handler for intent Learn About Topic."""

    def __init__(self, obj, data):
        self.obj = obj
        self.procedures = [
            # (Function_Attribute, [data_variable_names], is_msg_needed)
            ('get_top_matches', ['top_count'], True),   # top_matches
            ('verify_matches_found', ['top_matches'], False),
            ('evaluate_paths', ['top_matches'], False),  # complete_matches, incomplete_matches
            ('complete_matches', ['incomplete_matches', 'match_index'], False), # options, match_index - or - None
            ('check_input_on_unfinished_path', ['options'], True), # chosen_opt - or - None
            ('add_key_to_path', ['incomplete_matches', 'match_index', 'chosen_opt'], False),
            ('combine_path_lists', ['incomplete_matches', 'complete_matches'], False),
            ('get_all_topics', ['complete_matches'], False),
            ('get_url_items', ['topics', 'complete_matches'], False), # urls:dict
            ('make_suggestion', ['urls'], False)]
        self._load_from_data(data)

    def _load_from_data(self, data):
        self.data = data
        if data['status'] is InterpreterStatus.Pending:
            # Initialize.
            self.data['variables'] = {
                'interests': ['all_jargon', 
                              'metas', 
                              'services', 
                              'frameworks', 
                              'languages',
                              'other_subjects'
                              ],
                'top_count': 1,
                'match_index': 0,
                'proc_index': 0}
        elif data['status'] is InterpreterStatus.WaitingToContinue:
            self.data['variables']['proc_index'] += 1
        self.data['status'] = InterpreterStatus.Working


class DebuggingHelpHandler(AbstractBaseHandler):

    """Handler for intent Debugging Help."""

    def __init__(self, obj, data):
        self.obj = obj
        self.procedures = [                                       # RETURNS.........
            ('get_top_matches', ['top_count'], True),               # top_matches
            ('determine_debug_topic', ['top_count'], False),        # primary_topic
            ('determine_secondary_intent', [], False),              # secondary_intent
            # Route to another function handler from filter_from_primary_topic.
            ('filter_from_primary_topic', ['primary_topic', 'secondary_intent'], False),
            # Mixed-Mode Debugging & SolveProblem:                  # query
            ('get_query_responses', ['query'], False),              # query_response
            ('print_responses', ['query_response'], False),
            ('fail_for_delete', [], False)
        ]
        self._load_from_data(data)

    def _load_from_data(self, data):
        self.data = data
        if data['status'] is InterpreterStatus.Pending:
            # Initialize
            self.data['variables'] = {
                'interests': ['metas',
                              'services',
                              'frameworks',
                              'languages',
                              'other_subjects',
                              'jargon_debugging'],
                'top_count': 1,
                'match_index': 0,
                'proc_index': 0}
        elif data['status'] is InterpreterStatus.WatingToContinue:
            self.data['variables']['proc_index'] += 1
        self.data['status'] = InterpreterStatus.Working


class SolveProblemHandler(AbstractBaseHandler):

    """Handler for intent Solve Problem."""

    def __init__(self, obj, data):
        self.obj = obj
        self.procedures = [
            ('get_top_matches', ['interests', 'top_count'], True), # top_matches, may be None.
            #('send_solve_problem_acknowledgement', [], False),
            ('get_stackexchange_query_params', [], True), # strict_params
            ('create_stackexchange_query', ['strict_params'], False), # query
            ('get_query_responses', ['query'], False),  # query_response
            #('print_responses', ['query_response'], False),
            ('score_responses', ['query_response'], True), # sorted_results
            ('suggest_results', ['sorted_results'], False), # None
            ('fail_for_delete', [], False)
        ]
        self._load_from_data(data)

    def _load_from_data(self, data):
        self.data = data
        if data['status'] is InterpreterStatus.Pending:
            # Initialize... variables for all process/entry function.
            self.data['variables'] = {
                'interests': ['subjects', 'auxiliaries', 'negators', 'all_action', 'all_jargon'],
                'top_count': 1,
                'proc_index': 0}
        elif data['status'] is InterpreterStatus.WaitingToContinue:
            self.data['variables']['proc_index'] += 1
        self.data['status'] = InterpreterStatus.Working


class GetOpinionHandler(AbstractBaseHandler):

    """Handler for intent Get Opinion."""

    def __init__(self, obj, data):
        self.obj = obj
        self.procedures = [
            ('opinion_message', [], False)
        ]
        self._load_from_data(data)