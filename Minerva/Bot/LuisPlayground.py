import sys
import string

from LuisInterpreter import ProjectSystemLuisInterpreter
from LuisClient import BotLuisClient
from Agent import VSConsoleAgent

# For development purposes only.
from Essentials import print_smart, get_file_size, json_to_file, file_to_json

# Constants.


# Debugging items.
JSON_FILE = 'petricca_test_file.json'
JSON_FILE = 'petricca_multiple_single_jargon.json'
JSON_FILE = 'petricca_remote_debugging_cloud_project.json'



def load_debug_json(client, filename):
    """Loads json from the file specified by 'filename'.  
    
    Makes a call to sendQuery when the file doesn't exist.
    Will write the newly obtained json to filename.

    """
    if 0 == get_file_size(filename):
        q = VSConsoleAgent().start_query()
        j = client.query(q, 'verbose')
        json_to_file(j, filename)
    else:
        j = file_to_json(filename)
    return j



def main():
    #bot = Bot.ProjectSystemBot('ptvs')
    bot = VSConsoleAgent()   # Interacts with the user.
    interp = ProjectSystemLuisInterpreter(bot, 'PTVS')    # Interpreter for a LUIS json query response.
    lc = BotLuisClient()    # Handles queries to the LUIS client.

    # Get the response as json, from a file or from a new query.
    j = lc.query(bot.start_query(), 'verbose')
    #j = load_debug_json(lc, JSON_FILE)
    interp.analyze(j)     # Analyze the json, and get a meaningful message (we hope).


if __name__ == "__main__":
    main()