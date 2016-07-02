# Use this to populate all the stackoverflow questions that are tagged with PTVS into Minerva's LUIS app.
from stackexchangequery import StackExchangeQuery
from projectoxford.luis import LuisClient
import time

APP_ID = '26a55f39-2c75-4387-8bf9-0fb9feddbca3'     # For Minerva.
SUBSCRIPTION_KEY = '7814a9388ef14151981f2037000ea288'   # Alex Neuenkirk's subscription key.
LUIS_URL = 'https://api.projectoxford.ai/luis/v1/application?id=' + \
            APP_ID + '&subscription-key=' + SUBSCRIPTION_KEY + '&q='

lc = LuisClient(LUIS_URL)

# Query all stackoverflow questions tagged with 'ptvs'
query = StackExchangeQuery('stackoverflow')
query.queryString.addTags('ptvs')
query.queryString.addPair('pagesize', 100)
query.queryString.addPair('page', 2)

print('Sending request:')
print(query.buildFullUrl())
query.go()

print('We have', len(query.response._results), 'results')

for res in query.response._results:
    time.sleep(0.1)
    try:
        title = res.getValue('title')
        print("Attempting to add", title)
        lc.query(title)
    except ValueError as e:
        pass