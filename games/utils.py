import json, os, random, unicodedata

_DATA = os.path.join(os.path.dirname(__file__), "..", "data")

BOLD  = "\033[1m"
RESET = "\033[0m"

# Theme-mutable — updated by apply_theme(); games access as U.GREEN etc.
GREEN  = "\033[92m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
CYAN   = "\033[96m"

_THEMES = {
    "default": ("\033[92m", "\033[93m", "\033[90m", "\033[96m"),  # green / yellow / gray / cyan
    "ocean":   ("\033[94m", "\033[96m", "\033[90m", "\033[95m"),  # blue  / cyan  / gray / magenta
    "sunset":  ("\033[91m", "\033[95m", "\033[90m", "\033[93m"),  # red   / magenta / gray / yellow
    "mono":    ("\033[1m",  "\033[2m",  "\033[2m",  "\033[1m"),   # bold  / dim   / dim  / bold
}

def apply_theme(name):
    global GREEN, YELLOW, GRAY, CYAN
    GREEN, YELLOW, GRAY, CYAN = _THEMES.get(name, _THEMES["default"])
    SETTINGS["theme"] = name

SETTINGS = {
    "difficulty": "medium",
    "theme":      "default",
    "rounds":     0,          # 0 = unlimited
    "direction":  "ask",      # "ask" | "es_en" | "en_es"
    "hints":      False,      # show first letter before reveal in translation
    "show_rank":  False,      # show word frequency rank after reveal
}

POOL    = {"easy": 500,  "medium": 2000, "hard": 5000}
POOL_5L = {"easy": 150,  "medium": 350,  "hard": 584}
TENSES  = {
    "easy":   ["Indicativo/Presente"],
    "medium": ["Indicativo/Presente", "Indicativo/Pretérito", "Indicativo/Imperfecto"],
    "hard":   ["Indicativo/Presente", "Indicativo/Pretérito", "Indicativo/Imperfecto",
               "Indicativo/Futuro", "Subjuntivo/Presente"],
}

_PRAISE  = ["¡Excelente!", "¡Muy bien!", "¡Perfecto!", "¡Brillante!", "¡Correcto!", "¡Increíble!", "¡Fantástico!"]
_CONSOLE = ["¡Ánimo!", "Keep going!", "Almost there!", "You'll get it!", "¡No te rindas!", "Practice makes perfect!"]

def load(filename):
    with open(os.path.join(_DATA, filename)) as f:
        return json.load(f)

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def praise():  return random.choice(_PRAISE)
def console(): return random.choice(_CONSOLE)

def clear():
    print("\033[2J\033[H", end="")

def hr():
    print(GRAY + "─" * 44 + RESET)

def streak_display(n):
    if n >= 10: return f"  {YELLOW}{BOLD}*** {n} STREAK — ¡FUEGO! ***{RESET}"
    if n >= 5:  return f"  {YELLOW}** {n} in a row — ¡Caliente!{RESET}"
    if n >= 3:  return f"  {YELLOW}* {n} in a row!{RESET}"
    return ""

def yn_input(prompt):
    """Enter or 'y' = True, 'n' = False, 'q' = 'q'."""
    r = input(prompt).strip().lower()
    if r == "q":
        return "q"
    return r != "n"  # empty string (Enter) or "y" both return True

def game_header(name, correct=0, total=0, streak=0, best=0):
    diff   = SETTINGS["difficulty"].upper()
    rounds = SETTINGS["rounds"]

    # Line 1: name + difficulty + round count
    rnd_str = f"   {total}/{rounds}" if rounds > 0 else ""
    print(f"\n{BOLD} {name}  [{diff}]{rnd_str}{RESET}")

    # Round progress bar (only in round-limit mode)
    if rounds > 0:
        filled = int(18 * total / rounds) if total > 0 else 0
        bar    = GREEN + "█" * filled + GRAY + "░" * (18 - filled) + RESET
        print(f" [{bar}]")

    # Line 2: score + streak (always shown) + best
    score_str = f"{correct}/{total}" if total else "—/—"
    if   streak >= 10: stk_col, dots = f"{YELLOW}{BOLD}", " ***"
    elif streak >= 5:  stk_col, dots = YELLOW,             " **"
    elif streak >= 3:  stk_col, dots = GREEN,              " *"
    else:              stk_col, dots = GRAY,               ""
    stk_str  = f"{stk_col}streak {streak}{dots}{RESET}"
    best_str = f"   {GRAY}best {best}{RESET}" if best > 0 else ""

    print(f" {GRAY}score {score_str}{RESET}   {stk_str}{best_str}")
    print(f" {GRAY}q = menu{RESET}")
    hr()

def summary(correct, total, best_streak, elapsed=0):
    hr()
    if not total:
        print(" No rounds played.\n")
        return
    pct    = int(correct / total * 100)
    filled = int(20 * correct / total)
    bar    = GREEN + "█" * filled + GRAY + "░" * (20 - filled) + RESET
    print(f"\n {BOLD}Session Summary{RESET}")
    print(f"  Score:       {BOLD}{correct}/{total}{RESET}  ({pct}%)")
    print(f"  Best streak: {BOLD}{best_streak}{RESET}")
    if elapsed > 0:
        m, s = divmod(elapsed, 60)
        print(f"  Time:        {m}:{s:02d}")
    print(f"  {bar}")
    if   pct == 100: print(f"\n  {GREEN}{BOLD}¡Perfecto! Flawless session!{RESET}")
    elif pct >= 80:  print(f"\n  {GREEN}¡Muy bien! Strong work.{RESET}")
    elif pct >= 60:  print(f"\n  {YELLOW}Good effort — keep it up!{RESET}")
    else:            print(f"\n  {GRAY}¡Ánimo! It gets easier.{RESET}")
    print()
