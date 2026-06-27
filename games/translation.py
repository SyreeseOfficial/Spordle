import random
from .utils import (load, SETTINGS, POOL, GREEN, GRAY, BOLD, RESET,
                    clear, hr, game_header, praise, console, streak_display, summary)

def play():
    all_words = load("words.json")
    pool_size = POOL[SETTINGS["difficulty"]]

    clear()
    print(f"\n{BOLD} TRANSLATION{RESET}")
    hr()
    print(" Direction:")
    print("  1. Spanish → English  (easier)")
    print("  2. English → Spanish  (harder)")
    d = input("\n [1/2, default 1] > ").strip()
    es_to_en = d != "2"

    correct = total = streak = best_streak = 0
    words = all_words[:pool_size]

    while True:
        word   = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        clear()
        game_header("TRANSLATION", correct, total, streak)

        inp = input(f" {BOLD}{prompt}{RESET}\n Press Enter to reveal > ").strip().lower()
        if inp == "q":
            break

        print(f"\n   → {BOLD}{answer}{RESET}\n")
        rating = input(" Got it? [y/n] > ").strip().lower()
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
