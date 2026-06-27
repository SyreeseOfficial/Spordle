from . import utils as U
from .utils import SETTINGS, BOLD, RESET, apply_theme

_DIFFICULTY_CYCLE = ["easy", "medium", "hard"]
_THEME_CYCLE      = ["default", "ocean", "sunset", "mono"]
_ROUNDS_CYCLE     = [0, 5, 10, 25]          # 0 = unlimited
_DIRECTION_CYCLE  = ["ask", "es_en", "en_es"]

_ROUNDS_LABEL = {0: "Unlimited", 5: "5", 10: "10", 25: "25"}
_DIR_LABEL    = {"ask": "Ask each time", "es_en": "ES → EN", "en_es": "EN → ES"}

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
    U.hr()
    print(f"  {U.GRAY}Enter a number to cycle through options, or q to go back{RESET}")

def play():
    while True:
        _show()
        choice = input("\n > ").strip().lower()
        if choice == "q" or choice == "":
            break
        if choice == "1":
            SETTINGS["difficulty"] = _cycle(_DIFFICULTY_CYCLE, SETTINGS["difficulty"])
        elif choice == "2":
            new_theme = _cycle(_THEME_CYCLE, SETTINGS["theme"])
            apply_theme(new_theme)
        elif choice == "3":
            SETTINGS["rounds"] = _cycle(_ROUNDS_CYCLE, SETTINGS["rounds"])
        elif choice == "4":
            SETTINGS["direction"] = _cycle(_DIRECTION_CYCLE, SETTINGS["direction"])
        elif choice == "5":
            SETTINGS["hints"] = not SETTINGS["hints"]
        elif choice == "6":
            SETTINGS["show_rank"] = not SETTINGS["show_rank"]
