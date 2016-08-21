import functools
import itertools
import json
from enum import Enum, unique

import Agent
import InfoManager
import LuisInterpreter
import LuisClient
import Query


def on_message(msg, system):
    bot_convo = Conversation(system, msg)
    bot_convo.choose_action()

def home():
    """Returns an HTML that contains an embedded Chat."""
    return "<!DOCTYPE html><html><head><meta charset='utf-8'><title>PTVS Feature Bot</title></head><body><iframe src='https://webchat.botframework.com/embed/pythontoolsfeaturebot?s=FZyF_pOmjcM.cwA.PJg.HZCQ39qn1m0o5eVbGlMlWjc8E1rFdAbxucvLslvHGAg' width=502, height=750></iframe></body></html>"
    

class Conversation:

    """Handles a conversation with a user and a help bot."""

    def __init__(self, project_system, msg):
        self.project_system = project_system
        self.agent = Agent.VSAgent()
        self.msg = msg

    def query_luis(self, query_text):
        """Returns json from a raw_query to the LUIS app."""
        luis_client = LuisClient.BotLuisClient('Petricca')
        json_results = luis_client.query_raw(query_text)
        luis_data = LuisData(json_results)
        return luis_data

    def choose_action(self):
        """Reviews the conversation's message data and reacts appropriately."""
        # Deserialize to create instances of custom types.
        self._deserialize_data()

        # Load data.
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

    def _save_all_data(self):
        """Saves and encodes all data items."""
        self.msg.data['interpreter'] = self.interp_data
        self.msg.data['luis_data'] = self.luis_data
        self.msg.data = json.dumps(self.msg.data, cls=DataEncoder)
        self.msg.save_data()

    def _deserialize_data(self):
        """Deserializes a help bot data encoded json."""
        if self.msg.data:
            self.msg.data = json.loads(self.msg.data, object_hook=DataEncoder.decode_hook)

    def _load_interpreter_data(self):
        """Returns a conversation's interpreter data."""
        try:
            interp_data = self.msg.data['interpreter']
        except KeyError:
            interp_data = {'status': LuisInterpreter.InterpreterStatus.Pending}
        finally:
            interp_data.update({'msg_text': self.msg.text})
            return interp_data

    def _load_luis_data(self):
        """Either loads or queries luis, returning a LuisData instance."""
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
                self.msg.reply(m)
            # Cleanup.
            del self.interp_data['outgoing']

    def _delete_state_information(self):
        """Clears out any state information for msg's conversation."""
        self.msg.data = {}
        self.msg.save_data()


class LuisData:
    
    """A class that makes accessing LUIS Response JSON more manageable."""

    def __init__(self, json_, attrs=None):
        self.json_ = json_
        self.entities = json_['entities']
        self.intents = json_['intents']
        self.query = json_['query']

        # Set an attr for each entity in the model's entity schema.
        for attr_name, entity_label in LuisClient.MODEL_ENTITY_SCHEMA.items():
            self._set_entity_attr(attr_name, entity_label)

        # Composite attributes.
        self.all_jargon = self.jargon_single + self.jargon_phrase + self.jargon_debugging
        self.learn_about_triggers = self.learn_about_phrases + self.learn_about_singles

        # Additional setup.
        self._initialize_attrs()

        # Handle optional params.
        self.words_of_interest = self.set_from_attrs(attrs) if attrs else None
        self._attrs_of_interest = attrs

    def _add_lists(self, first, second):
        """Adds a list of strs or a list of lists of strs together."""
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
        self.__setattr__(attr_name, entity_literals or [])
        print("Set {} to {}".format(attr_name, getattr(self, attr_name)))
        
    def _initialize_attrs(self):
        """Handle any special formatting for any attribute that needs it."""
        if self.languages:
            # LUIS adds whitespace between nonalpha characters.
            self.languages = list(map(lambda e: e.replace(' ', ''), self.languages))

    def set_from_attrs(self, attrs):
        """Returns a set of all values for each attr in attrs."""
        elements = [getattr(self, attr) or [] for attr in attrs]
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