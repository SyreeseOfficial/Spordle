#!/usr/bin/env python3
from games import (translation, wordle, conjugation, gender,
                   false_friends, rapid_fire, hangman, anagram, settings)
from games import utils as U

GAMES = [
    ("Translation",      translation.play),
    ("Wordle",           wordle.play),
    ("Verb Conjugation", conjugation.play),
    ("Gender Drill",     gender.play),
    ("False Friends",    false_friends.play),
    ("Rapid Fire",       rapid_fire.play),
    ("Hangman",          hangman.play),
    ("Anagram",          anagram.play),
    ("Settings",         settings.play),
]

def menu():
    U.clear()
    diff = U.SETTINGS["difficulty"].upper()
    print(f"\n{U.BOLD}╔════════════════════════════════╗{U.RESET}")
    print(f"{U.BOLD}║       S P O R D L E           ║{U.RESET}")
    print(f"{U.BOLD}║    Spanish Practice CLI       ║{U.RESET}")
    print(f"{U.BOLD}╠════════════════════════════════╣{U.RESET}")
    for i, (name, _) in enumerate(GAMES, 1):
        is_settings = name == "Settings"
        if is_settings:
            label = f"{name}  {U.GRAY}[{diff}]{U.RESET}"
            print(f"{U.BOLD}║{U.RESET}  {i}. {label:<40}{U.BOLD}║{U.RESET}")
        else:
            print(f"{U.BOLD}║{U.RESET}  {i}. {name:<28}{U.BOLD}║{U.RESET}")
    print(f"{U.BOLD}║{U.RESET}                                {U.BOLD}║{U.RESET}")
    print(f"{U.BOLD}║{U.RESET}  {U.GRAY}q. Quit{U.RESET}                         {U.BOLD}║{U.RESET}")
    print(f"{U.BOLD}╚════════════════════════════════╝{U.RESET}")
    return input("\n> ").strip().lower()

def main():
    while True:
        choice = menu()
        if choice in ("q", "quit", "exit"):
            U.clear()
            print("\n ¡Hasta luego!\n")
            break
        if choice.isdigit() and 1 <= int(choice) <= len(GAMES):
            GAMES[int(choice) - 1][1]()
        else:
            print(" Pick a number from the menu.")
            input(" Enter to continue...")

if __name__ == "__main__":
    main()
