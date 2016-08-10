import os
import sys
import argparse
from bottle import get, post, request

if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    import bottle
    bottle.debug(True)

from message import Message
import HelpBot as bot

PROJECT_SYSTEM = 'PTVS'

@get('/')
def home():
    try:
        bot.home
    except AttributeError:
        pass
    else:
        return bot.home()
    
    return "TODO: home page"


@post('/api/messages')
def root():
    msg = Message(request.json)

    if msg.type.lower() == 'ping':
        return

    if msg.type.lower() == 'message':
        return bot.on_message(msg, PROJECT_SYSTEM)

    try:
        handler = getattr(bot, msg.type)
    except AttributeError:
        return {"message": "TODO: " + msg.type}
    else:
        return handler(msg)



def parse_cmd_args():
    # Handle command line args.
    global PROJECT_SYSTEM
    parser = argparse.ArgumentParser()
    parser.add_argument("--proj_sys", "--project_system", help="The project system whose information is to be used.")
    args = parser.parse_args()
    if args.proj_sys:
        PROJECT_SYSTEM = args.proj_sys.upper()

if __name__ == '__main__':
    import bottle
    bottle.debug(True)

    if len(sys.argv) > 1:
        parse_cmd_args()

    # Starts a local test server.
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '3978'))
    except ValueError:
        PORT = 3978
    bottle.run(server='wsgiref', host=HOST, port=PORT)

    

    
else:
    import bottle

    wsgi_app = bottle.default_app()
