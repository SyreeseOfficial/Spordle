# Single source of truth for the playable games: (stats key, menu label, menu group).
GAMES = [
    ("translation",    "Translation",      "study"),
    ("wordle",         "Wordle",           "study"),
    ("conjugation",    "Verb Conjugation", "study"),
    ("gender",         "Gender Drill",     "study"),
    ("false_friends",  "False Friends",    "study"),
    ("rapid_fire",     "Rapid Fire",       "study"),
    ("hangman",        "Hangman",          "study"),
    ("anagram",        "Anagram",          "study"),
    ("number_drill",   "Number Drill",     "study"),
    ("roguelike",      "Roguelike",        "gamble"),
    ("push_your_luck", "Push Your Luck",   "gamble"),
    ("stakes",         "High Stakes",      "gamble"),
]

KEYS   = [k for k, _, _ in GAMES]
LABELS = {k: label for k, label, _ in GAMES}
