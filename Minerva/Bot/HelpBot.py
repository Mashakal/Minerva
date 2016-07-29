import sys
from enum import Enum, unique

import Agent
import LuisInterpreter
import LuisClient
from LuisInterpreter import InterpreterStatus

# For development purposes only:
import Essentials


def on_message(msg):
    #if msg_has_queue(msg):
    #    queue_message(msg)
    #    return
    bot_convo = Conversation('PTVS', msg)
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


# Strings for easier json decoding.
CONVERSATION_STATES = {
    'Processing': 'Processing',
    'Waiting': 'Waiting'
}


class Conversation:

    """Handles a conversation with a user and a help bot."""

    def __init__(self, project_system, msg):
        self.project_system = project_system
        self.agent = Agent.BotConnectorAgent()
        self.msg = msg

    def initiate_conversation(self):
        """Starts a conversation between the agent and the user."""
        return self.agent.start_query()

    def query_luis(self, query_text):
        """Returns json from a raw_query to the LUIS app."""
        luis_client = LuisClient.BotLuisClient('Petricca')
        json_results = luis_client.query_raw(query_text)
        return {'json': json_results,
                'query': query_text}

    def choose_action(self):
        # Mark this message as the one currently being processed.
        #self._set_as_current(self.msg)

        # For debugging.
        self._delete_state_information()

        # Load data.
        self.convo_data = self._load_conversation_data()
        self.luis_data = self._load_luis_data()
        self.interp_data = self._load_interpreter_data()

        print("\nConversation data:")
        print(self.convo_data)
        print("\nLuis data:")
        print(self.luis_data)
        print("\nInterp data:")
        print(self.interp_data)

        print("\n\n")

        # Interpret.
        self.interpreter = LuisInterpreter.ApiProjectSystemLuisInterpreter(self.agent, self.project_system)
        self.interp_data = self.interpreter.interpret(self.interp_data)
        
        print("\n\n")
        
        # Post-interpretation administrative tasks.
        self._send_outgoing()

        # Cleanup.
        if self.interp_data['status'] in [InterpreterStatus.Complete, InterpreterStatus.Failed]:
            # Delete the state information.
            print("We should be deleting the state info.")
            self._delete_state_information()
        else:
            print('We should retain the state info.')
            self._save_all_data()
        return
       
    def _save_interpreter_data(self):
        """Saves the conversation's interpreter data."""
        self.msg.data['interpreter'] = self.interp_data
        self.msg.save_data()

    def _save_conversation_data(self):
        """Saves the conversation's data."""
        self.msg.data['conversation'] = self.convo_data
        self.msg.save_data()

    def _save_all_data(self):
        """Saves all data items."""
        self.msg.data['conversation'] = self.convo_data
        self.msg.data['interpreter'] = self.interp_data
        self.msg.data['luis_data'] = self.luis_data
        self.msg.save_data()

    def _load_conversation_data(self):
        try:
            return self.msg.data['conversation']['data']
        except LookupError:
           return {'status': InterpreterStatus.Pending,
                   'isActive': True}

    def _load_interpreter_data(self):
        """Returns a conversation's interpreter data."""
        try:
            interp_data = self.msg.data['interpreter']
        except KeyError:
            interp_data = {'status': InterpreterStatus.Pending}
        finally:
            interp_data.update({'msg_text': self.msg.text})
            interp_data['luis_data'] = self.luis_data
            return interp_data

    def _save_luis_data(self):
        self.msg.data['luis_data'] = self.luis_data
        self.msg.save_data()

    def _load_luis_data(self):
        try:
            luis_data = self.msg.data['luis_data']
        except KeyError:
            luis_data = self.query_luis(self.msg.text)
        finally:
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