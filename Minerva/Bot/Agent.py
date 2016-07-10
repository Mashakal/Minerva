import string
import random
import sys
import DialogueStrings

class Agent(object):
    """Communicates with the user.
    """
    def _get_random_string_constant(self, genre):
        """Extracts an array of strings from the ALL_STRINGS dictionary.
        Returns a random string from the extracted array.
        """
        try:
            strings = DialogueStrings.ALL_STRINGS[genre]
        except KeyError:
            raise ValueError("Cannot find strings of type: {0}.".format(genre))
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
        prints a prompt, then returns the input from the user.
        """
        print(s)
        return self._prompt()

    def acknowledge(self, items, genre='positive_acks', conj='and'):
        """Output a positive acknowledgement, formatted
        with s.  Formats the number of items being acknowledged
        with and uses conj as the conjunction.
        """
        s = self._get_random_string_constant(genre)
        if isinstance(items, list):
            # Get a string that's formatted to fit the number of items.
            f = self._build_list_string(len(items), True)
            f += self._build_conj_string(len(items), conj)
            # Get a unified string that has the items listed in order.
            f = f % tuple(items)
            self.say(s.format(f))
        else:
            # Assumes items is a string.
            self.say(s.format(items))

    def give_options(self, opts, msg=None, indent=2, genre='options'):
        """Outputs a message to standard output followed by an 
        ordered list of options defined by opts.  Ordering starts at 1 and 
        each element of opts is output on a new line.  Returns the opt chosen 
        by the user.  The message can be set explicitly via msg.  Indent can 
        be set explicitly to change the number of empty spaces precending each
        opt.  Genre indicates which string list in ALL_STRINGS to choose from.
        """
        def validate_input(input, opts):
            """A helper function for clarify.  Checks that a user has entered
            a valid option.  Valid options are determined to be numbers that are
            within the bounds of opts.
            """
            if not input.isnumeric():
                return False
            n = int(input)
            # Valid indices start at 1.
            if 0 >= n or len(opts) < n:
                return False
            return True
        
        if not opts:
            raise ValueError("opts cannot be empty.")

        m = msg if msg else self._get_random_string_constant(genre)
        self.say(m)
        for i, v in enumerate(opts):
            print(" " * indent + "{0}: {1}".format(i + 1, v))
        n = self._prompt()
        while not validate_input(n, opts):
            n = self.ask("{0} is not valid.  Enter a valid choice.".format(n))
        return opts[int(n) - 1]

    def clarify(self, opts, conj='or'):
        """Constructs a conversation friendly dialogue asking
        the user to choose one of a set of options. A conjunction
        can be set explicitly.  Opts may also be a list 
        containing only one element, e.g. ['Debugging'] to get
        something like 'Are you asking about Debugging?'.
        """
        def validate_input(ans, opts):
            """Validates that the user's input matches one of opts.  
            Returns a set of opts where any word in ans is found 
            in any word of that opt.
            """
            # Search for each word in the user's input, ignoring punctuation.
            user_words = {w.lower().strip(string.punctuation) for w in ans.split(" ")}
            opts_words = [w.lower().split(" ") for w in opts]
            flat_opts_words = set(([w for li in opts_words for w in li]))
            # Find any matching opts.
            valid_input = user_words & flat_opts_words
            # Take the valid input and match it to its corresponding opts.
            chosen = set(([o for o in opts for valid in valid_input if valid in o.lower()]))
            # TODO: Log how many valid input are being returned.
            return chosen if chosen else False

        if not opts:
            raise ValueError("opts cannot be empty.")

        msg = self._get_random_string_constant('clarify')
        # Allow an arbitrary number of opts to be printed.
        msg += " " + self._build_list_string(len(opts), True if 1 < len(opts) else False)
        # Conjunction string depends on size of opts.
        msg += self._build_conj_string(len(opts), conj)
        msg += "?"
        # Require a match to at least one of opts.
        opt = validate_input(self.ask(msg % tuple(opts)), opts) # False on failure.
        while not opt:
            # Negative acknowledgement and ask the message again.
            self.say("I don't understand, {0}".format((msg % tuple(opts)).lower()))
            opt = validate_input(self._prompt(), opts)
        return opt

    def _build_conj_string(self, length, conj):
        """Builds the conjunction part of the string, using
        the number of items in opts to determine how the string
        should be formatted.
        """
        if 2 < length:
            s = ", " + conj + " %s"
        elif 2 == length:
            s = " " + conj + " %s"
        elif 1 == length:
            s = "%s"
        return s

    def _build_list_string(self, length, with_conj=False):
        """Generates a single string that can be formatted using String.format
        given an array-like object.  The array-like object must be converted into
        a tuple and passed as the parameter to the call to String.format.
        """
        # A '%s' is added when the conjunction string is built.
        mul = length - 1 if with_conj else length
        return "%s" % ", ".join(['%s'] * mul)



class VSAgent(Agent):
    """A Visual Studio bot.
    """
    def suggest_url(self, url, topic, genre='suggest_url'):
        """Output a message suggesting the user learn more about topic at url.
        """
        s = self._get_random_string_constant(genre)
        if genre == 'suggest_url':
            self.say(s.format(url))
        else:
            self.say(s.format(topic, url))

    def suggest_multiple_urls(self, urls, topics):
        """Suggests all url.
        """
        # Print the suggested url with it's corresponding key/topic.
        genre = 'suggest_mult_url' if 1 < len(urls) else 'suggest_url'
        for i, url in enumerate(urls):
            self.suggest_url(url, topics[i], genre)

    def start_query(self, msg=None):
        """Initiates an interaction with the help bot.
        """
        m = msg if msg else self._get_random_string_constant('start')
        return self.ask(m)


def main():
    agent = VSAgent()
    options = ['Building', 'Cloud Service Project']
    ans = agent.clarify(options)
    print(ans)

if __name__ == "__main__":
    sys.exit(int(main() or 0))