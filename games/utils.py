import json, os, unicodedata

_DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def load(filename):
    with open(os.path.join(_DATA, filename)) as f:
        return json.load(f)

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

GREEN  = "\033[92m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def hr():
    print(GRAY + "─" * 40 + RESET)
