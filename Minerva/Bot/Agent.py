import itertools
import string
import random
import sys
import DialogueStrings

class Agent:

    """Communicates with the user."""

    def _get_random_string_constant(self, genre):
        """Returns a random string of type genre.

        Returns a random string from the array pointed
        to by genre in the DialogueStrings.ALL_STRINGS dictionary.

        """
        try:
            strings = DialogueStrings.ALL_STRINGS[genre]
        except KeyError:
            raise ValueError("Cannot find strings of type: {}.".format(genre))
        else:
            r = random.randint(0, len(strings) - 1)
            return strings[r]

    def _prompt(self):
        """Outputs a prompt and returns the user's input."""
        r = input(">>> ")
        print()
        return r

    def say(self, s):
        """Print a message from the bot to the standard output."""
        print(s)
        print()

    def ask(self, s):
        """Asks and returns a response to some string output."""
        self.say(s)
        return self._prompt()

    def acknowledge(self, items, genre='positive_acks', conj='and'):
        """Output an acknowledgement message for a container of items.

        Constructs a string given a container of items.  The string
        will join together each item in items and and if there is more
        than one will use the conjunction, conj before the last item.
        Genre can be set explicitly and defaults to 'positive_acks'.
        Conj can be set explicitly and defaults to 'and'.

        For example:
            self.acknowledge(['Debugging']) might output the string:
                'I would be glad to help you with Debugging.'

            self.acknowledge(['Python Environments', 'PyLint']) might output the string:
                'I can definitely assist with Python Environments and PyLint.'

            self.acknowledge(['Python Environments', 'PyLint'], conj='as well as')
                might output the string:
                'I can get you information on PyLint as well as Python Environments.'

        """
        msg = self._get_random_string_constant(genre)
        # Get a string that's formatted to fit the number of items.
        list_string = self._build_list_string(len(items), (1 < len(items)))
        list_string = ''.join([list_string, self._build_conj_string(len(items), conj)])
        # Get a unified string that has the items listed in order.
        list_string = list_string.format(*items)
        # Output.
        self.say(msg.format(list_string))

    def give_options(self, opts, msg=None, indent=2, genre='options'):
        """Require the user to choose a valid option from opts.
        
        Outputs a message to standard output followed by an 
        ordered list of options defined by opts.  Ordering starts at 1 and
        each element of opts is output on a new line.  Returns the opt chosen 
        by the user.  The message can be set explicitly via msg.  Indent can 
        be set explicitly to change the number of empty spaces precending each
        opt.  Genre indicates which string list in ALL_STRINGS to choose from.

        """
        def validate_input(input, no_opts):
            """Returns true when user input is valid, otherwise False."""
            try:
                n = int(input)
            except ValueError:
                return False
            # Valid indices start at 1.
            else:
               if n < 0 or n > no_opts:
                    return False
            return True
        
        if not opts:
            raise ValueError("opts cannot be empty.")

        m = msg or self._get_random_string_constant(genre)
        print(m)
        for i, v in enumerate(opts):
            print(''.join([' ' * indent, '{}: {}'.format(i + 1, v)]))
        print()
        n = self._prompt()
        while not validate_input(n, len(opts)):
            n = self.ask("{} is not valid.  Enter a valid choice.".format(n))
        return opts[int(n) - 1]

    def clarify(self, opts, conj='or'):
        """Returns a choice between opts after being presented to the user.
        
        Constructs a conversation friendly dialogue asking the user to choose
        one of a set of options. A conjunction can be set explicitly.  Opts 
        may also be a list containing only one element, e.g. ['Debugging'] to 
        ask something like 'Are you asking about Debugging?'.

        """
        def validate_input(ans, opts):
            """Returns the choice made by the user if input was valid, or False.
            
            Validates that the user's input matches one of opts.  Returns a set
            of opts where any word in ans is found in any word of that opt.

            """
            # Search for each word in the user's input, ignoring punctuation.
            user_words = {w.lower().strip(string.punctuation) \
                          for w in ans.split(' ')}
            opts_words = [w.lower().split(' ') for w in opts]
            flat_opts_words = {w for li in opts_words for w in li}
            # Find any matching opts_words.
            valid_input = user_words & flat_opts_words
            # Take the valid input and match it to whole opt string matched.
            chosen = {o for o in opts for valid in valid_input \
                      if valid in o.lower()}
            # TODO: Log how many valid input are being returned.
            return chosen

        if not opts:
            raise ValueError("opts cannot be empty.")

        msg = self._get_random_string_constant('clarify')
        # Allow an arbitrary number of opts to be printed.
        msg = ' '.join([msg, self._build_list_string(len(opts), 1 < len(opts))])
        msg = ''.join([msg, self._build_conj_string(len(opts), conj), '?'])
        # Require a match to at least one of opts.
        message = msg.format(tuple(opts))
        opt = validate_input(self.ask(message), opts) # False on failure.
        while not opt:
            # Negative acknowledgement and ask the message again.
            self.say("I don't understand, {0}".format(message))
            opt = validate_input(self._prompt(), opts)
        return opt  # BUG: Might return more than one opt.  Would be better to remove common words like 'and'.

    def _build_conj_string(self, length, conj):
        """Builds the conjunction part of the string, using
        the number of items in opts to determine how the string
        should be formatted.
        """
        s = ''
        if 2 < length:
            s = ''.join([', ', conj, ' {}'])
        elif 2 == length:
            s = ''.join([' ', conj, ' {}'])
        elif 1 == length:
            s = '{}'
        return s

    def _build_list_string(self, length, with_conj=False):
        """Generates a single string that can be formatted using String.format
        given an array-like object.  The array-like object must be converted into
        a tuple and passed as the parameter to the call to String.format.
        """
        num = 0 if not with_conj else length - 1
        return ', '.join(['{}'] * num)


class VSAgent(Agent):

    """A Visual Studio bot."""

    def suggest_url(self, *args, genre='suggest_url'):
        """Outputs a string formatted with tuple (url, topic)."""
        s = self._get_random_string_constant(genre)
        # TODO: Add note about using dialogue strings with suggest_url.
        self.say(s.format(*args))

    def suggest_urls(self, topics, urls):
        """Suggests all url."""
        # Print the suggested url with it's corresponding key/topic.
        g = 'suggest_urls' if len(urls) > 1 else 'suggest_url'
        for i, url in enumerate(urls):
            self.suggest_url(url, topics[i], genre=g)

    def start_query(self, msg=None):
        """Initiates an interaction with the help bot."""
        m = msg or self._get_random_string_constant('start')
        return self.ask(m)


def main():
    agent = VSAgent()
    options = ['Building', 'Cloud Service Project']
    #ans = agent.clarify(options)`
    agent.acknowledge(['Building', 'Cloud Project', 'Remote Debugging'])

if __name__ == "__main__":
    sys.exit(int(main() or 0))