import random, time
from . import utils as U
from .utils import SETTINGS, POOL_5L, BOLD, RESET

def _shuffle(word):
    letters = list(word)
    for _ in range(50):
        random.shuffle(letters)
        if letters != list(word):
            return "".join(letters)
    return "".join(letters)

def play():
    all_words = U.load("words_5letter.json")
    pool      = all_words[:POOL_5L[SETTINGS["difficulty"]]]
    word_map  = {w["es"].lower(): w["en"] for w in pool}
    word_list = list(word_map.keys())

    correct = total = streak = best_streak = 0
    rounds  = SETTINGS["rounds"]
    start   = time.time()

    while True:
        target   = random.choice(word_list)
        scrambled = _shuffle(target)

        U.clear()
        U.game_header("ANAGRAM", correct, total, streak, best=best_streak)
        print(f" Unscramble the Spanish word:\n")
        print(f"  {BOLD}{' '.join(scrambled.upper())}{RESET}\n")
        print(f"  {U.GRAY}Meaning: {word_map[target]}{RESET}\n")

        guess = input(" [q = menu] > ").strip().lower()
        if guess == "q":
            break

        total += 1
        if guess == target:
            correct += 1
            streak  += 1
            is_new   = streak > best_streak
            best_streak = max(best_streak, streak)
            print(f"\n {U.GREEN}{U.praise()}  →  {target}{RESET}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
        else:
            streak = 0
            print(f"\n {U.GRAY}Answer: {BOLD}{target}{RESET}  {U.GRAY}{U.console()}{RESET}")

        if rounds > 0 and total >= rounds:
            print(f"\n {U.CYAN}{BOLD}Round complete!{RESET}")
            break

        input("\n Enter to continue...")

    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
