import sys
import string

import Bot
from LuisInterpreter import ProjectSystemLuisInterpreter
from LuisClient import BotLuisClient
from Agent import VSAgent

# For development purposes only.
from Essentials import print_smart, get_file_size, json_to_file, file_to_json

# Constants.
SUBSCRIPTION_KEY = '7814a9388ef14151981f2037000ea288'   # Alex Neuenkirk's subscription key.
APP_IDS = {
    'HelpBot': '3b58ccb7-4165-4af0-9759-b028c73ce4f9',
    'Petricca': '8f688b1d-6c6a-4245-8ca5-ec7a9eaddb6b'
}

# Debugging items.
JSON_FILE = 'petricca_test_file.json'
JSON_FILE = 'petricca_multiple_single_jargon.json'
JSON_FILE = 'petricca_remote_debugging_cloud_project.json'

def build_luis_url(app_name):
    s = 'https://api.projectoxford.ai/luis/v1/application?id=' + \
            APP_IDS[app_name] + '&subscription-key=' + SUBSCRIPTION_KEY + '&q='
    return s

def load_debug_json(client, filename):
    """Loads json from the file specified by 'filename'.  
    
    Makes a call to sendQuery when the file doesn't exist.
    Will write the newly obtained json to filename.

    """
    if 0 == get_file_size(filename):
        q = VSAgent().start_query()
        j = client.query(q, 'verbose')
        json_to_file(j, filename)
    else:
        j = file_to_json(filename)
    return j



def main():
    #bot = Bot.ProjectSystemBot('ptvs')

    bot = VSAgent()   # Interacts with the user.
    interp = ProjectSystemLuisInterpreter(bot, 'PTVS')    # Interpreter for a LUIS json query response.
    lc = BotLuisClient(build_luis_url('Petricca'))    # Handles queries to the LUIS client.

    # Get the response as json, from a file or from a new query.
    j = lc.query(bot.start_query(), 'verbose')
    #j = load_debug_json(lc, JSON_FILE)
    interp.analyze(j)     # Analyze the json, and get a meaningful message (we hope).


if __name__ == "__main__":
    sys.exit(int(main() or 0))