#!/usr/bin/env python3
from games import translation, wordle, conjugation, gender, false_friends, settings
from games.utils import SETTINGS, BOLD, GRAY, CYAN, RESET, clear

GAMES = [
    ("Translation",      translation.play),
    ("Wordle",           wordle.play),
    ("Verb Conjugation", conjugation.play),
    ("Gender Drill",     gender.play),
    ("False Friends",    false_friends.play),
    ("Settings",         settings.play),
]

def menu():
    clear()
    diff = SETTINGS["difficulty"].upper()
    print(f"\n{BOLD}╔══════════════════════════════╗{RESET}")
    print(f"{BOLD}║      S P O R D L E          ║{RESET}")
    print(f"{BOLD}║   Spanish Practice CLI      ║{RESET}")
    print(f"{BOLD}╠══════════════════════════════╣{RESET}")
    for i, (name, _) in enumerate(GAMES, 1):
        is_settings = name == "Settings"
        label = f"{name}  {GRAY}[{diff}]{RESET}" if is_settings else name
        print(f"{BOLD}║{RESET}  {i}. {label:<38}{BOLD}║{RESET}" if is_settings
              else f"{BOLD}║{RESET}  {i}. {name:<26}{BOLD}║{RESET}")
    print(f"{BOLD}║{RESET}                              {BOLD}║{RESET}")
    print(f"{BOLD}║{RESET}  {GRAY}q. Quit{RESET}                       {BOLD}║{RESET}")
    print(f"{BOLD}╚══════════════════════════════╝{RESET}")
    return input("\n> ").strip().lower()

def main():
    while True:
        choice = menu()
        if choice in ("q", "quit", "exit"):
            clear()
            print("\n ¡Hasta luego!\n")
            break
        if choice.isdigit() and 1 <= int(choice) <= len(GAMES):
            GAMES[int(choice) - 1][1]()
        else:
            print(" Pick a number from the menu.")
            input(" Enter to continue...")

if __name__ == "__main__":
    main()
