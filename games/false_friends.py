import random
from .utils import (load, GREEN, YELLOW, GRAY, BOLD, RESET,
                    clear, game_header, praise, console, streak_display, summary)

def play():
    friends = load("false_friends.json")
    random.shuffle(friends)

    correct = total = streak = best_streak = 0

    for entry in friends:
        clear()
        game_header("FALSE FRIENDS", correct, total, streak)
        print(f" {BOLD}{entry['es']}{RESET}\n")
        print(f" {GRAY}Looks like:{RESET}  \"{entry['looks_like']}\"\n")

        inp = input(" What does it ACTUALLY mean?  [Enter to reveal  /  q = menu] > ").strip().lower()
        if inp == "q":
            break

        print(f"\n {YELLOW}Actually:{RESET}  {BOLD}{entry['real_en']}{RESET}\n")
        print(f" {GRAY}Remember:{RESET}  {entry['es']}  ≠  {entry['looks_like']}\n")

        rating = input(" Did you know it? [y/n] > ").strip().lower()
        if rating == "q":
            break

        total += 1
        if rating == "y":
            correct += 1
            streak += 1
            best_streak = max(best_streak, streak)
            print(f"\n {GREEN}{praise()}{RESET}{streak_display(streak)}")
        else:
            streak = 0
            print(f"\n {GRAY}{console()}{RESET}")

        input("\n Enter to continue...")

    summary(correct, total, best_streak)
    input(" Enter to return to menu...")
