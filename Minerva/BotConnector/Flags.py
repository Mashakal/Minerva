# Need flags that hold data (state information).
class Flag(Exception):

    """Used as a flag, stores a dict in attribute named data."""

    def __init__(self, **kwargs):
        self.data = kwargs

# Enum style flags.
class NeedChoiceBetweenOptions(Flag): pass
class NeedClarification(Flag): pass