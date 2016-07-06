import random

POSITIVE_ACKS = [
    "I can definitely help you with {0}.",
    "I will be happy to assist with {0}.",
    "Sure, I can help you with {0}."
]

SUGGEST_URL = [
    "The following is a good resource: {0}.",
    "I suggest you visit: {0}.",
    "You'll find information on that here: {0}."
]

CLARIFYING = [
    "Which of these is more pertinent in your case?",
    "Which one of these best describes what you need?"
]

ALL_STRINGS = {
    'positive_acks': POSITIVE_ACKS,
    'suggest_url': SUGGEST_URL,
    'clarify': CLARIFYING
}


class Bot(object):
    """Communicates with the user.
    """
    def get_random_string_constant(self, type):
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

    def __prompt(self):
        """Outputs a prompt and returns the user's input.
        """
        return input(">>> ")

    def say(self, s):
        """Print a message from the bot to the standard output.
        """
        print(s)

    def ask(self, s):
        """Print a message/question to the standard output and then
        prints a prompt and gets input from the user.
        """
        print(s)
        return self.__prompt()

    def acknowledge(self, s, positive = True):
        """Output a positive or negative acknowledgement, formatted
        with s.
        """
        t = 'positive_acks' if positive else 'negative_acks'
        r = self.get_random_string_constant(t)
        self.say(r.format(s))

class VSBot(Bot):
    """A Visual Studio bot.
    """
    def suggest_url(self, url):
        """Output a message suggesting the user visit url.
        """
        r = self.get_random_string_constant('suggest_url')
        self.say(r.format(url))

    def clarify(self, opts, msg=None, indent=2):
        """Outputs a clarifying message to standard output followed by an 
        ordered list of options defined by opts.  Ordering starts at 1 and 
        each element of opts is output on a new line.  Returns the opt chosen 
        by the user.  The message can be set explicitly via msg.  Indent can 
        be set explicitly to change the number of spaces before an opt is 
        written to standard output.
        """
        def _validate_input(input, opts):
            """A helper function for clarify.  Checks that a user has entered
            a valid option.  Valid options are determined to be numbers that are
            within the bounds of opts.
            """
            if not input.isnumeric():
                return False
            index = int(input)
            if 0 > index or len(opts) - 1 < index:
                return False
            return True

        m = msg if msg else self.get_random_string_constant('clarify')
        self.say(m)
        for i, v in enumerate(opts):
            print(" " * indent + "{0}: {1}".format(i + 1, v))
        i = self.__prompt()
        while not _validate_input(i, opts):
            self.say("{0} is not a valid choice.".format(i))
            self.ask("Enter a valid choice.")
        return opts[int(i)]