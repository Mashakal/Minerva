import types
import functools
import itertools
import sys
import json
from enum import Enum, unique

import Agent
import InfoManager
import LuisInterpreter
import LuisClient
import Query


def on_message(msg, system):
    #if msg_has_queue(msg):
    #    queue_message(msg)
    #    return
    bot_convo = Conversation(system, msg)
    bot_convo.choose_action()

def load_next_message(msg):
    """Returns the next message in queue."""
    queue = msg.data['queue']
    return queue.pop(0)

def queue_message(msg):
    """Adds the message to its conversation's queue."""
    try:
        queue = msg.data['queue']
    except LookupError:
        queue = []
    finally:
        queue.append(msg)
        msg.data['queue'] = queue
        msg.save_data()

def msg_has_queue(msg):
    """True when the msg.data as a 'queue' key."""
    try:
        msg.data['queue']
    except KeyError:
        return False
    else:
        return True


class Conversation:

    """Handles a conversation with a user and a help bot."""

    def __init__(self, project_system, msg):
        self.project_system = project_system
        self.agent = Agent.VSAgent()
        self.msg = msg

    def initiate_conversation(self):
        """Starts a conversation between the agent and the user."""
        return self.agent.start_query()

    def query_luis(self, query_text):
        """Returns json from a raw_query to the LUIS app."""
        luis_client = LuisClient.BotLuisClient('Petricca')
        json_results = luis_client.query_raw(query_text)
        luis_data = LuisData(json_results)
        return luis_data

    def choose_action(self):
       
        # Deserialize to create instances of custom types.
        self._deserialize_data()

        # For debugging.
        #self._delete_state_information()

        # Load data.
        #self.convo_data = self._load_conversation_data()
        self.luis_data = self._load_luis_data()
        self.interp_data = self._load_interpreter_data()
        self.interp_data['luis_data'] = self.luis_data

        # Interpret.
        self.interpreter = LuisInterpreter.ApiProjectSystemLuisInterpreter(self.agent, self.project_system)
        self.interp_data = self.interpreter.interpret(self.interp_data)
        
        # Post-interpretation administrative tasks.
        self._send_outgoing()

        # Cleanup.
        if self.interp_data['status'] in [LuisInterpreter.InterpreterStatus.Complete, LuisInterpreter.InterpreterStatus.Failed]:
            # Delete the state information.
            self._delete_state_information()
        else:
            self._save_all_data()
        return
      
    def _save_interpreter_data(self):
        """Saves the conversation's interpreter data."""
        self.msg.data['interpreter'] = self.interp_data
        self.msg.save_data()

    def _save_conversation_data(self):
        """Saves the conversation's data."""
        self.msg.data['conversation']['data'] = self.convo_data
        self.msg.save_data()

    def _save_all_data(self):
        """Saves and encodes all data items."""
        #self.msg.data['conversation'] = self.convo_data
        print("VARIABLES when being saved:")
        print(json.dumps(self.interp_data['variables'], cls=DataEncoder, indent=4, sort_keys=True))
        print("STATUS on save: {}".format(self.interp_data['status']))
        self.msg.data['interpreter'] = self.interp_data
        self.msg.data['luis_data'] = self.luis_data
        self.msg.data = json.dumps(self.msg.data, cls=DataEncoder)
        self.msg.save_data()

    def _deserialize_data(self):
        """Deserializes a help bot data encoded json."""
        if self.msg.data:
            self.msg.data = json.loads(self.msg.data, object_hook=DataEncoder.decode_hook)

    def _load_conversation_data(self):
        try:
            return self.msg.data['conversation']['data']
        except LookupError:
           return {'status': LuisInterpreter.InterpreterStatus.Pending,
                   'isActive': True}

    def _load_interpreter_data(self):
        """Returns a conversation's interpreter data."""
        try:
            interp_data = self.msg.data['interpreter']
        except KeyError:
            interp_data = {'status': LuisInterpreter.InterpreterStatus.Pending}
        finally:
            interp_data.update({'msg_text': self.msg.text})
            return interp_data

    def _save_luis_data(self):
        self.msg.data['luis_data'] = self.luis_data
        self.msg.save_data()

    def _load_luis_data(self):
        try:
            luis_data = self.msg.data['luis_data']
        except KeyError:
            luis_data = self.query_luis(self.msg.text)
        return luis_data

    def _send_outgoing(self):
        """Sends any messages added to the outgoing list during interpretation."""
        try:
            outbox = self.interp_data['outgoing']
        except KeyError:
            pass
        else:
            for m in outbox:
                self.msg.post(m)
            # Cleanup.
            del self.interp_data['outgoing']

    def _delete_state_information(self):
        """Clears out any state information for msg's conversation."""
        self.msg.data = {}
        self.msg.save_data()

    # Methods to handle message's conversation's state.
    def _has_active_query(self, msg):
        """True if we have already made a call to the LUIS app."""
        try:
            is_active = msg.data['has_active_query']
        except (AttributeError, KeyError):
            return False
        else:
            return is_active

    def _is_locked(self, msg):
        """True if a helpbot is currently working the conversation."""
        try:
            locked = msg.data['is_locked']
        except LookupError:
            return False
        else:
            return locked

    def _lock(self, msg):
        """Marks the conversation as locked by the helpbot.

        When a conversation is locked it should not be worked by other 
        bots.
        
        """
        self._add_to_data(msg, 'is_locked', True)

    def _unlock(self, msg):
        """Marks a conversation as unlocked.

        When a conversation is unlocked, it can be worked by a 
        bot.

        """
        self._del_from_data(msg, 'is_locked')

    def _mark_active(self, msg):
        """Marks a conversation as being processed."""
        msg.data['has_active_query'] = True
        msg.save_data()

    def _mark_inactive(self, msg):
        """Marks a conversation as no longer being finished."""
        try:
            del msg.data['has_active_query']
        except (AttributeError, KeyError):
            pass
        finally:
            msg.save_data()


class LuisData:

    def __init__(self, json_, attrs=None):
        self.json_ = json_
        self.entities = json_['entities']
        self.intents = json_['intents']
        self.query = json_['query']

        # Set an attr for each entity in the model's entity schema.
        for attr_name, entity_label in LuisClient.MODEL_ENTITY_SCHEMA.items():
            self._set_entity_attr(attr_name, entity_label)

        # Hybrid attributes.
        self.all_jargon = (self.jargon_single or []) + \
                          (self.jargon_phrase or []) + \
                          (self.jargon_debugging or []) 

        
        # Additional setup.
        self._initialize_attrs()
        
        # Handle optional params.
        self.words_of_interest = self.set_from_attrs(attrs) if attrs else None
        self._attrs_of_interest = attrs

    def _add_lists(self, first, second):
        if not first and second:
            return first or second
        if not isinstance(first[0], str):
            first = itertools.chain.from_iterable(first)
        if not isinstance(second[0], str):
            second = itertools.chain.from_iterable(second)
        return first + second

    def _set_entity_attr(self, attr_name, entity_type):
        matching_entities = filter(lambda e: e['type'] == entity_type, self.json_['entities'])
        entity_literals = list(map(lambda e: e['entity'], matching_entities))
        self.__setattr__(attr_name, entity_literals or None)
        print("Set {} to {}".format(attr_name, getattr(self, attr_name)))
        
    def _initialize_attrs(self):
        """Handle any special formatting for any given attribute."""
        # LUIS adds whitespace between nonalpha characters.
        if self.languages:
            self.languages = list(map(lambda e: e.replace(' ', ''), self.languages))

    def set_from_attrs(self, attrs):
        """Returns a set of all values for each attr in attrs."""
        elements = [getattr(self, attr) or [] for attr in attrs]
        print("Elements are: {}".format(elements))
        elements = filter(None, elements)
        return set(functools.reduce(self._add_lists, elements, []))

    def load_words_of_interest(self, attrs):
        """Updates words_of_interest based on attrs."""
        self.words_of_interest = self.set_from_attrs(attrs)
        self._attrs_of_interest = attrs

    def top_intent(self):
        try:
            return self.intents[0]['intent']
        except LookupError:
            return "None"


#region JSON Encoding/Decoding

class DataEncoder(json.JSONEncoder):

    """A customized json encoder for help bot data."""

    def default(self, obj):
        if isinstance(obj, Enum):
            return {"__enum__": str(obj)}
        elif isinstance(obj, set):
            return {"__set__": str(obj)}
        elif isinstance(obj, InfoManager.TopicMatch):
            return {"__TopicMatch__": dict(obj)}
        elif isinstance(obj, Query.StackExchangeResponse):
            return {"__StackExchangeResponse__": obj._json}
        elif isinstance(obj, Query.StackExchangeQuery):
            return {"__StackExchangeQuery__": repr(obj)}
        elif isinstance(obj, Query.QuestionResult):
            return {"__QuestionResult__": obj.serialize()}
        elif isinstance(obj, LuisData):
            return {"__LuisData__": obj.json_}
        return json.JSONEncoder.default(self, obj)

    @classmethod
    def decode_hook(cls, obj):
        if "__enum__" in obj:
            name, member = obj["__enum__"].split('.')
            mod = globals()['LuisInterpreter']
            return getattr(mod.InterpreterStatus, member)
        elif "__set__" in obj:
            return eval(obj["__set__"])
        elif "__TopicMatch__" in obj:
            return InfoManager.TopicMatch._init_from_decode(obj)
        elif "__StackExchangeResponse__" in obj:
            return Query.StackExchangeResponse(None, json=obj["__StackExchangeResponse__"])
        elif "__LuisData__" in obj:
            return LuisData(obj["__LuisData__"])
        return obj


def main():
    learn_interests = ['all_jargon', 'metas', 'services', 'frameworks']
    lc = LuisClient.BotLuisClient('Petricca')
    query_json = lc.query_raw("Tell me about python environments?")
    print(json.dumps(query_json, sort_keys=True, indent=4))
    luis_data = LuisData(query_json, learn_interests)
    for attr in sorted(LuisClient.MODEL_ENTITY_SCHEMA.keys()):
        print("{}: {}".format(attr, getattr(luis_data, attr)))
    print("Words of interest: {}".format(luis_data.words_of_interest))

if __name__ == "__main__":
    main()