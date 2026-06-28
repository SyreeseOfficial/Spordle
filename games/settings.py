from . import utils as U
from . import stats as S
from .utils import SETTINGS, BOLD, RESET, apply_theme

_DIFFICULTY_CYCLE = ["easy", "medium", "hard"]
_THEME_CYCLE      = ["default", "ocean", "sunset", "mono"]
_ROUNDS_CYCLE     = [0, 5, 10, 25]
_DIRECTION_CYCLE  = ["ask", "es_en", "en_es"]
_VERB_CYCLE       = ["all", "irregular", "regular"]

_ROUNDS_LABEL = {0: "Unlimited", 5: "5", 10: "10", 25: "25"}
_DIR_LABEL    = {"ask": "Ask each time", "es_en": "ES → EN", "en_es": "EN → ES"}
_VERB_LABEL   = {"all": "All verbs", "irregular": "Irregular only", "regular": "Regular only"}

def _cycle(lst, current):
    return lst[(lst.index(current) + 1) % len(lst)]

def _show():
    U.clear()
    d = SETTINGS
    print(f"\n{BOLD} SETTINGS{RESET}")
    U.hr()
    print(f"  1. Difficulty     {BOLD}{d['difficulty'].upper()}{RESET}")
    print(f"     easy · medium · hard\n")
    print(f"  2. Color Theme    {BOLD}{d['theme'].upper()}{RESET}")
    print(f"     default · ocean · sunset · mono\n")
    print(f"  3. Round Limit    {BOLD}{_ROUNDS_LABEL[d['rounds']]}{RESET}")
    print(f"     5 · 10 · 25 · unlimited\n")
    print(f"  4. Translation    {BOLD}{_DIR_LABEL[d['direction']]}{RESET}")
    print(f"     ask each time · ES→EN · EN→ES\n")
    print(f"  5. Hints          {BOLD}{'ON' if d['hints'] else 'OFF'}{RESET}")
    print(f"     show first letter before reveal in Translation\n")
    print(f"  6. Word Rank      {BOLD}{'ON' if d['show_rank'] else 'OFF'}{RESET}")
    print(f"     show frequency rank after reveal in Translation\n")
    print(f"  7. Verb Type      {BOLD}{_VERB_LABEL[d['verb_type']]}{RESET}")
    print(f"     all · irregular only · regular only\n")
    print(f"  8. Reset Stats    {U.GRAY}wipe all-time records{RESET}\n")
    U.hr()
    print(f"  {U.GRAY}Enter a number to change, or q to go back{RESET}")

def play():
    while True:
        _show()
        choice = input("\n > ").strip().lower()
        if choice == "q" or choice == "":
            break
        if   choice == "1": SETTINGS["difficulty"] = _cycle(_DIFFICULTY_CYCLE, SETTINGS["difficulty"])
        elif choice == "2": apply_theme(_cycle(_THEME_CYCLE, SETTINGS["theme"]))
        elif choice == "3": SETTINGS["rounds"]     = _cycle(_ROUNDS_CYCLE, SETTINGS["rounds"])
        elif choice == "4": SETTINGS["direction"]  = _cycle(_DIRECTION_CYCLE, SETTINGS["direction"])
        elif choice == "5": SETTINGS["hints"]      = not SETTINGS["hints"]
        elif choice == "6": SETTINGS["show_rank"]  = not SETTINGS["show_rank"]
        elif choice == "7": SETTINGS["verb_type"]  = _cycle(_VERB_CYCLE, SETTINGS["verb_type"])
        elif choice == "8":
            confirm = input(f"\n {U.YELLOW}Reset ALL stats? This can't be undone. [y/N] >{RESET} ").strip().lower()
            if confirm == "y":
                S.reset()
                print(f" {U.GREEN}Stats reset.{RESET}")
                input(" Enter to continue...")
