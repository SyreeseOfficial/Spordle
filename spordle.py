#!/usr/bin/env python3
import time
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

_GAME_NAMES = [name for name, _ in GAMES]

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

    streak = stats.load().get("login_streak", 0)
    streak_str = f"   {U.CYAN}🔥 {streak}-day streak{U.RESET}" if streak >= 2 else ""

    last = stats.get_last()
    if last and last.get("total", 0) > 0:
        pct      = int(last["correct"] / last["total"] * 100)
        name_str = last["game"].replace("_", " ")
        last_str = f"\n  {U.GRAY}last: {name_str}  {pct}%  streak {last['best_streak']}{U.RESET}"
    else:
        last_str = ""

    print(f"\n{U.BOLD} S P O R D L E{U.RESET}   {U.GRAY}[{diff}]{U.RESET}{q_str}{streak_str}{last_str}")
    U.hr()

    favs = [name for name in U.SETTINGS.get("favorites", []) if name in _GAME_NAMES]
    if favs:
        print(f"  {U.GRAY}── favorites ──────────────────{U.RESET}")
        for fi, name in enumerate(favs, 1):
            print(f"  {U.YELLOW}f{fi}{U.RESET}. {name}")
        print(f"  {U.GRAY}────────────────────────────────{U.RESET}")

    for i, (name, _) in enumerate(GAMES, 1):
        if i == 10:
            print(f"  {U.GRAY}── gambling ────────────────────{U.RESET}")
        elif i == 13:
            print(f"  {U.GRAY}────────────────────────────────{U.RESET}")
        star = f" {U.YELLOW}★{U.RESET}" if name in favs else ""
        print(f"  {i:>2}. {name}{star}")

    print(f"\n  {U.GRAY} q. Quit{U.RESET}")
    U.hr()
    return input("\n > ").strip().lower()

def main():
    U.banner()
    while True:
        choice = menu()
        if choice in ("q", "quit", "exit"):
            U.play_back()
            U.clear()
            print("\n ¡Hasta luego!\n")
            break

        # Favorites: f1/f2/f3
        favs = [name for name in U.SETTINGS.get("favorites", []) if name in _GAME_NAMES]
        if choice.startswith("f") and choice[1:].isdigit():
            fi = int(choice[1:]) - 1
            if 0 <= fi < len(favs):
                U.play_navigate()
                gi = _GAME_NAMES.index(favs[fi])
                t0 = time.time()
                GAMES[gi][1]()
                stats.add_time(int(time.time() - t0))
            continue

        if choice.isdigit() and 1 <= int(choice) <= len(GAMES):
            U.play_navigate()
            t0 = time.time()
            GAMES[int(choice) - 1][1]()
            stats.add_time(int(time.time() - t0))
        else:
            print(" Pick a number from the menu.")
            input(" Enter to continue...")

if __name__ == "__main__":
    main()
