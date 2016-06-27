from LuisInterpreter import PythonLuisInterpreter
from LuisClient import HelpBotLuisClient
from Essentials import printSmart

# Constants
APP_ID = '3b58ccb7-4165-4af0-9759-b028c73ce4f9'     # For HelpBot.
SUBSCRIPTION_KEY = '7814a9388ef14151981f2037000ea288'   # Alex Neuenkirk's subscription key.
LUIS_URL = 'https://api.projectoxford.ai/luis/v1/application?id=' + \
            APP_ID + '&subscription-key=' + SUBSCRIPTION_KEY + '&q='

interp = PythonLuisInterpreter()

# PLAYGROUND
lc = HelpBotLuisClient(LUIS_URL)
q = "Is it possible to check whether PTVS python debugger is attached to process?"
#r = lc.query(q) # Response is 3 tuple from LuisClient.
r = lc.query(q, result='v') # Response is json from Luis.

msg = interp.analyze(r)
print(msg)

#printSmart(r)
#print(r)