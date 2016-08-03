YES_WORDS = ['yes', 'yeah', 'okay', 'ok', 'k', 'y', 'ya', 
             'right', 'correct', "that's right", 'sure', 'for sure']

NO_WORDS = ['no', 'n', 'nah', 'nope', 'negative']

POSITIVE_ACKS = [
    "I can definitely help you with {0}.",
    "I will be happy to assist with {0}.",
    "Sure, I can help you with {0}."
]

NEGATIVE_ACKS = [

]

END = [
    "Thanks for giving me a chance.  Let me know if I can help with anything else."
]

SUGGEST_URLS = [
    # {0} is the url, {1} is the topic.
    "[This link]({0}) is a good resource for {1}.\n",
    "For {1}, I suggest you visit here: {0}.\n",
    "You'll find information on {1} here:\n{0}.\n"
]

SUGGEST_URL = [
    "You'll find information on that here:\n\t{0}.",
    "For that, I suggest you visit:\n\t{0}.",
    "The following is a good resource for that:\n\t{0}."
]

OPTIONS = [
    "Which of these is more pertinent in your case?",
    "Which one of these best describes what you need?"
]

START = [
    "What can I help you with?",
    "How can I help you?",
    "What can I do for you?"
]

CLARIFY = [
    "Are you asking about",
    "Which is your main point of interest"
]

ALL_STRINGS = {
    'positive_acks': POSITIVE_ACKS,
    'suggest_url': SUGGEST_URL,
    'clarify': CLARIFY,
    'start': START,
    'options': OPTIONS,
    'negative_acks': NEGATIVE_ACKS,
    'end': END,
    'suggest_urls': SUGGEST_URLS,
    'yes': YES_WORDS,
    'no': NO_WORDS
}