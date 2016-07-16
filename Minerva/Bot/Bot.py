import sys

import Agent
import LuisInterpreter
import LuisClient

# For development purposes only:
import Essentials


class Bot:
    pass


class ProjectSystemBot(Bot):
    """A bot for Visual Studio Project Systems."""

    def __init__(self, project_system):
        self._luis_client = LuisClient.BotLuisClient()
        self.agent = Agent.VSAgent()
        self.interpreter = LuisInterpreter.ProjectSystemLuisInterpreter(self.agent, project_system)

    def initiate_conversation(self):
        """Starts a conversation between the agent and the user."""
        return self.agent.start_query()
