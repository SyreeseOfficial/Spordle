#!/usr/bin/env python3
from games import (translation, wordle, conjugation, gender,
                   false_friends, rapid_fire, hangman, anagram,
                   number_drill, roguelike, push_your_luck, stakes,
                   quests, settings, stats)
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
    ("Number Drill",     number_drill.play),

    ("Roguelike",        roguelike.play),
    ("Push Your Luck",   push_your_luck.play),
    ("High Stakes",      stakes.play),

    ("Daily Quests",     quests.show),
    ("My Stats",         stats.show),
    ("Settings",         settings.play),
]

def menu():
    U.clear()
    diff       = U.SETTINGS["difficulty"].upper()
    quest_list = quests.get()
    done       = sum(1 for *_, d in quest_list if d)
    if done == 3:
        q_str = f"   {U.GREEN}{U.BOLD}⚡ 3/3 quests!{U.RESET}"
    elif done > 0:
        q_str = f"   {U.YELLOW}⚡ {done}/3 quests{U.RESET}"
    else:
        q_str = f"   {U.GRAY}⚡ 0/3 quests{U.RESET}"

    print(f"\n{U.BOLD} S P O R D L E{U.RESET}   {U.GRAY}[{diff}]{U.RESET}{q_str}")
    U.hr()
    for i, (name, _) in enumerate(GAMES, 1):
        if i == 10:
            print(f"  {U.GRAY}── gambling ────────────────────{U.RESET}")
        elif i == 13:
            print(f"  {U.GRAY}────────────────────────────────{U.RESET}")
        print(f"  {i:>2}. {name}")
    print(f"\n  {U.GRAY} q. Quit{U.RESET}")
    U.hr()
    return input("\n > ").strip().lower()

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
