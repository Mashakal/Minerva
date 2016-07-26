import sys
from enum import Enum, unique

import Agent
import LuisInterpreter
import LuisClient

# For development purposes only:
import Essentials


def on_message(msg):
    if msg_has_queue(msg):
        queue_message(msg)
        return
    bot = ProjectSystemHelpBot('PTVS')
    bot.choose_action(msg)

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
    'Processing': 'processing',
    'WaitingForInput': 'waitingforinput'
}


class ProjectSystemHelpBot:

    """Handles a conversation with a user and an help bot."""

    def __init__(self, project_system):
        self.project_system = project_system
        self.agent = Agent.VSConsoleAgent()

    def initiate_conversation(self):
        """Starts a conversation between the agent and the user."""
        return self.agent.start_query()

    def query_luis(self, query_text):
        """Returns json from a raw_query to the LUIS app."""
        luis_client = LuisClient.BotLuisClient('Petricca')
        return luis_client.query_raw(query_text)

    def choose_action(self, msg):
        self._set_as_current(msg)
        self._set_conversation_state(msg, CONVERSATION_STATES['Processing'])
        # Check if the msg is a brand new query.
        if not self._has_active_query(msg):
            json_results = self.query_luis(msg.text)
            # Save api calls here by adding to data explicitly.
            msg.data['luis_results'] = json_results
            # Marking msg active will also save msg.data.
            self._mark_active(msg)
        self.interpreter = LuisInterpreter.ProjectSystemLuisInterpreter(self.agent, self.project_system)
        response_message = self.interpreter.analyze(msg.data['luis_results'])
        msg.reply(response_message)
        self._delete_state_information(msg)
        return
        
    # Methods to manipulate the message's data attribute.
    def _add_to_data(self, msg, key, value):
        """Adds a key/value pair to msg.data and saves it."""
        msg.data[key] = value
        msg.save_data()

    def _del_from_data(self, msg, key):
        """Deletes key from the msg.data."""
        try:
            del msg.data[key]
        except LookupError:
            pass
        finally:
            msg.save_data()

    def _set_as_current(self, msg):
        """Sets msg as the current message in msg.data."""
        self._add_to_data(msg, 'current_message', msg._activity_id)

    def _reset_current(self, msg):
        """Deletes the current message information."""
        self._del_from_data(msg, 'current_message')

    def _set_conversation_state(self, msg, state):
        """Sets the conversation state."""
        self._add_to_data(msg, 'state', state)

    def _delete_state_information(self, msg):
        """Clears out any state information for msg's conversation."""
        msg.data = {}
        msg.save_data()

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


