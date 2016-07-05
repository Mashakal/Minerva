from LuisInterpreter import ProjectSystemLuisInterpreter
from LuisClient import BotLuisClient
from Essentials import printSmart, getFileSize, jsonToFile, fileToJson
import sys


# Constants
SUBSCRIPTION_KEY = '7814a9388ef14151981f2037000ea288'   # Alex Neuenkirk's subscription key.
APP_IDS = {
    'HelpBot': '3b58ccb7-4165-4af0-9759-b028c73ce4f9',
    'HelpBot2.0': 'somethinghere'
}

# Debugging items.
JSON_FILE = "sampleQueryResults.json"
JSON_FILE = "errorwhiletryingtoattachdebuger.json"

def buildLuisUrl(appName):
    s = 'https://api.projectoxford.ai/luis/v1/application?id=' + \
            APP_IDS[appName] + '&subscription-key=' + SUBSCRIPTION_KEY + '&q='
    return s

def sendQuery(client, result='standard'):
    #q = "Error while trying to attach debugger from PTVS"
    q = input("What can I help you with?\n>>> ")
    #r = lc.query(q) # Response is 3 tuple from LuisClient.
    return client.query(q, result) # Response is json from Luis.

def loadDebugJson(client, filename):
    """Loads json from the file specified by 'filename'.  Makes a call to sendQuery when
    the file doesn't exist.  Will write the newly obtained json to filename."""
    if 0 == getFileSize(filename):
        j = sendQuery(client, result='verbose')
        jsonToFile(j, filename)
    else:
        j = fileToJson(filename)
    return j



def main():
    interp = ProjectSystemLuisInterpreter('ptvs')    # Interpreter for a LUIS json query response.
    lc = BotLuisClient(buildLuisUrl('HelpBot'))    # Handles queries to the LUIS client.

    # Get the response as json, from a file or from a new query.
    j = sendQuery(lc, 'verbose')
    #j = loadDebugJson(lc, JSON_FILE)
    msg = interp.analyze(j)     # Analyze the json, and get a meaningful message (we hope).
    #print(msg)

if __name__ == "__main__":
    sys.exit(int(main() or 0))