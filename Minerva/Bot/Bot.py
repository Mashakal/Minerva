import random
from DialogueStrings import ALL_STRINGS

class Bot(object):
    """Communicates with the user.
    """
    def _get_random_string_constant(self, type):
        """Grabs an array of strings from the ALL_STRINGS dictionary.
        Returns a random string from the extracted array.
        """
        try:
            strings = ALL_STRINGS[type]
        except LookupError:
            raise ValueError("Cannot find strings of type: {0}.".format(type))
        else:
            r = random.randint(0, len(strings) - 1)
            return strings[r]

    def _prompt(self):
        """Outputs a prompt and returns the user's input.
        """
        print()
        r = input(">>> ")
        print()
        return r

    def say(self, s):
        """Print a message from the bot to the standard output.
        """
        print(s)

    def ask(self, s):
        """Print a message/question to the standard output and then
        prints a prompt and gets input from the user.
        """
        print(s)
        return self._prompt()

    def acknowledge(self, s, positive=True):
        """Output a positive or negative acknowledgement, formatted
        with s.
        """
        t = 'positive_acks' if positive else 'negative_acks'
        r = self._get_random_string_constant(t)
        self.say(r.format(s))

    def clarify(self, opts, msg=None, indent=2):
        """Outputs a clarifying message to standard output followed by an 
        ordered list of options defined by opts.  Ordering starts at 1 and 
        each element of opts is output on a new line.  Returns the opt chosen 
        by the user.  The message can be set explicitly via msg.  Indent can 
        be set explicitly to change the number of empty spaces precending each
        opt.
        """
        def _validate_input(input, opts):
            """A helper function for clarify.  Checks that a user has entered
            a valid option.  Valid options are determined to be numbers that are
            within the bounds of opts.
            """
            if not input.isnumeric():
                return False
            index = int(input)
            if 0 >= index or len(opts) < index:
                return False
            return True

        m = msg if msg else self._get_random_string_constant('clarify')
        self.say(m)
        for i, v in enumerate(opts):
            print(" " * indent + "{0}: {1}".format(i + 1, v))
        i = self._prompt()
        while not _validate_input(i, opts):
            i = self.ask("{0} is not valid.  Enter a valid choice.".format(i))
        return opts[int(i) - 1]

class VSBot(Bot):
    """A Visual Studio bot.
    """
    def suggest_url(self, url):
        """Output a message suggesting the user visit url.
        """
        r = self._get_random_string_constant('suggest_url')
        self.say(r.format(url))

    def start_query(self, msg=None):
        m = msg if msg else self._get_random_string_constant('start')
        return self.ask(m)
