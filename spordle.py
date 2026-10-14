#!/usr/bin/env python3
from games import (translation, wordle, conjugation, gender,
                   false_friends, rapid_fire, hangman, anagram,
                   number_drill, roguelike, push_your_luck, stakes,
                   quests, settings, stats)
from games import utils as U
from games.registry import GAMES as _REGISTRY

_PLAY = {
    "translation": translation.play, "wordle": wordle.play, "conjugation": conjugation.play,
    "gender": gender.play, "false_friends": false_friends.play, "rapid_fire": rapid_fire.play,
    "hangman": hangman.play, "anagram": anagram.play, "number_drill": number_drill.play,
    "roguelike": roguelike.play, "push_your_luck": push_your_luck.play, "stakes": stakes.play,
}

# (label, play, menu group) — games come from the registry, then the tools
ENTRIES = [(label, _PLAY[key], group) for key, label, group in _REGISTRY] + [
    ("Daily Quests", quests.show,   "tools"),
    ("My Stats",     stats.show,    "tools"),
    ("Settings",     settings.play, "tools"),
]
_SEPARATORS = {"gamble": "── gambling ────────────────────", "tools": "────────────────────────────────"}

def menu():
    U.clear()
    data       = stats.load()
    diff       = U.SETTINGS["difficulty"].upper()
    quest_list = quests.get(data)
    done       = sum(1 for *_, d in quest_list if d)
    if done == 3:
        q_str = f"   {U.GREEN}{U.BOLD}⚡ 3/3 quests!{U.RESET}"
    elif done > 0:
        q_str = f"   {U.YELLOW}⚡ {done}/3 quests{U.RESET}"
    else:
        q_str = f"   {U.GRAY}⚡ 0/3 quests{U.RESET}"

    streak = stats.current_streak(data)
    streak_str = f"   {U.CYAN}🔥 {streak}-day streak{U.RESET}" if streak >= 2 else ""

    last = stats.get_last(data)
    if last and last.get("total", 0) > 0:
        pct      = int(last["correct"] / last["total"] * 100)
        name_str = last["game"].replace("_", " ")
        last_str = f"\n  {U.GRAY}last: {name_str:<16} {pct}%  streak {last['best_streak']}{U.RESET}"
    else:
        last_str = ""

    print(f"\n{U.BOLD} S P O R D L E{U.RESET}   {U.GRAY}[{diff}]{U.RESET}{q_str}{streak_str}{last_str}")
    U.hr()

    favs = _favorites()
    if favs:
        print(f"  {U.GRAY}── favorites ──────────────────{U.RESET}")
        for fi, name in enumerate(favs, 1):
            print(f"  {U.YELLOW}f{fi}{U.RESET}. {name}")
        print(f"  {U.GRAY}────────────────────────────────{U.RESET}")

    group = ENTRIES[0][2]
    for i, (name, _, g) in enumerate(ENTRIES, 1):
        if g != group:
            group = g
            print(f"  {U.GRAY}{_SEPARATORS[g]}{U.RESET}")
        star = f" {U.YELLOW}★{U.RESET}" if name in favs else ""
        print(f"  {i:>2}. {name}{star}")

    print(f"\n  {U.GRAY} q. Quit{U.RESET}")
    U.hr()
    return input("\n > ").strip().lower()

def _favorites():
    names = [name for name, *_ in ENTRIES]
    return [name for name in U.SETTINGS.get("favorites", []) if name in names]

def _run(play):
    """Run one game; Ctrl+C / Ctrl+D drops back to the menu instead of crashing."""
    try:
        play()
    except (KeyboardInterrupt, EOFError):
        print()

def main():
    U.init()
    try:
        U.banner()
        while True:
            choice = menu()
            if choice in ("q", "quit", "exit"):
                break

            index = None
            if choice.startswith("f") and choice[1:].isdigit():  # favorites: f1/f2/f3
                favs = _favorites()
                fi = int(choice[1:]) - 1
                if 0 <= fi < len(favs):
                    index = [name for name, *_ in ENTRIES].index(favs[fi])
            elif choice.isdigit() and 1 <= int(choice) <= len(ENTRIES):
                index = int(choice) - 1

            if index is None:
                print(" Pick a number from the menu.")
                input(" Enter to continue...")
                continue
            U.sfx("navigate")
            _run(ENTRIES[index][1])
    except (KeyboardInterrupt, EOFError):
        pass
    U.play_back_and_wait()
    U.clear()
    print("\n ¡Hasta luego!\n")

if __name__ == "__main__":
    main()
