import json, os, random, unicodedata

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
CYAN   = "\033[96m"
RESET  = "\033[0m"

def hr():
    print(GRAY + "─" * 44 + RESET)

def clear():
    print("\033[2J\033[H", end="")

# Shared difficulty settings — mutated by settings menu
SETTINGS = {"difficulty": "medium"}

# How many words to use per difficulty
POOL = {"easy": 500, "medium": 2000, "hard": 5000}
POOL_5L = {"easy": 150, "medium": 350, "hard": 584}

# Conjugation tenses per difficulty
TENSES = {
    "easy":   ["Indicativo/Presente"],
    "medium": ["Indicativo/Presente", "Indicativo/Pretérito", "Indicativo/Imperfecto"],
    "hard":   ["Indicativo/Presente", "Indicativo/Pretérito", "Indicativo/Imperfecto",
               "Indicativo/Futuro", "Subjuntivo/Presente"],
}

_PRAISE   = ["¡Excelente!", "¡Muy bien!", "¡Perfecto!", "¡Brillante!", "¡Correcto!", "¡Increíble!"]
_CONSOLE  = ["¡Ánimo!", "Keep going!", "Almost there!", "You'll get it!", "No te rindas!"]

def praise():   return random.choice(_PRAISE)
def console():  return random.choice(_CONSOLE)

def streak_display(n):
    if n >= 10: return f"{YELLOW}{BOLD} *** {n} STREAK — ¡FUEGO! ***{RESET}"
    if n >= 5:  return f"{YELLOW} ** {n} in a row — ¡Caliente!{RESET}"
    if n >= 3:  return f"{YELLOW} * {n} in a row!{RESET}"
    return ""

def game_header(name, correct=0, total=0, streak=0):
    diff  = SETTINGS["difficulty"].upper()
    score = f"  {correct}/{total}" if total else ""
    stk   = f"  {streak_display(streak)}" if streak >= 3 else ""
    print(f"\n{BOLD} {name}  [{diff}]{score}{stk}{RESET}")
    print(f"{GRAY} q = menu{RESET}")
    hr()

def summary(correct, total, best_streak):
    hr()
    if not total:
        print(" No rounds played.")
        return
    pct = int(correct / total * 100)
    bar_len = 20
    filled = int(bar_len * correct / total)
    bar = GREEN + "█" * filled + GRAY + "░" * (bar_len - filled) + RESET
    print(f"\n {BOLD}Session Summary{RESET}")
    print(f"  Score:       {BOLD}{correct}/{total}{RESET}  ({pct}%)")
    print(f"  Best streak: {BOLD}{best_streak}{RESET}")
    print(f"  {bar}\n")
