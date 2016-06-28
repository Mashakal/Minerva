from LuisInterpreter import PythonLuisInterpreter
from LuisClient import BotLuisClient
from Essentials import printSmart, getFileSize, jsonToFile, fileToJson
import sys

# Constants
APP_ID = '3b58ccb7-4165-4af0-9759-b028c73ce4f9'     # For HelpBot.
SUBSCRIPTION_KEY = '7814a9388ef14151981f2037000ea288'   # Alex Neuenkirk's subscription key.
LUIS_URL = 'https://api.projectoxford.ai/luis/v1/application?id=' + \
            APP_ID + '&subscription-key=' + SUBSCRIPTION_KEY + '&q='

JSON_FILE = "sampleQueryResults.json"


def sendQuery(client, result='standard'):
    q = "Is it possible to check whether PTVS python debugger is attached to process?"
    #r = lc.query(q) # Response is 3 tuple from LuisClient.
    return client.query(q, result) # Response is json from Luis.

def loadDebugJson(client, filename):
    """Loads json from the file specified by 'filename'.  If the file doesn't exist, makes a call to 
    fetchFunction and expects a json object in response.  Will write the newly obtained json to 
    filename."""
    if 0 == getFileSize(filename):
        j = sendQuery(client, result='verbose')
        jsonToFile(j, filename)
    else:
        j = fileToJson(filename)
    return j



def main():
    interp = PythonLuisInterpreter()    # Interprets a LUIS json query response.
    lc = BotLuisClient(LUIS_URL)    # Handles queries to the LUIS client.

    # Get the response as json, from a file or from a new query.
    j = loadDebugJson(lc, JSON_FILE)
    msg = interp.analyze(j)     # Analyze the json, and get a meaningful message (we hope).
    print(msg)  

if __name__ == "__main__":
    sys.exit(int(main() or 0))