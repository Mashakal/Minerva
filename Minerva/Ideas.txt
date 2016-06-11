# IDEAS - Incorporate all VS features into the bot.
#       - Answers can have tags so the user can easily understand the contents of each piece of information.
#       - We will definitely need a keyboard shortcut for conducting a search, make it EASY AS POSSIBLE.

# HELP BUTTON - as a part of debugging, possibly popping up in the output window when an error occurs.
        # Get feedback from the user after they use this feature, it will be the most dependent on ML to improve.
        # Earn points of some kind for voting for the most helpful resource when a problem is encountered.

# Interface:
#  We can have two buttons that say "Tell me about...{feature}" or "Help me with ... {problem}"
#  This will help prioritize the search method.  Tell me about feature should focus on getting
#  information from the github wiki whereas Help me with problem should prioritize a bing
#  search and a query to any known source of useful information.
#       Sources:
           # StackExchange API
           #    Pros:  Lots of information available, easily parsed.
           #           There could be an option to specifically search stack overflow, without having to use a browser.
           #                - Open in browser option
           #                - A generic search like this could also make use of a bing search, potentially increasing bing traffic.
           #    Cons:  Getting very specific questions, with more than one query tag.
           #    - Looked into using py-stackexchange module found on github but it is limited in the same was as the API.
           #    - Choose your own image (pre-approved) for the Minerva button.