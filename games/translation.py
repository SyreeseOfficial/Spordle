import random, time
from . import utils as U
from . import stats as S
from .utils import SETTINGS, POOL, BOLD, RESET

def play():
    all_words = U.load("words.json")
    pool_size = POOL[SETTINGS["difficulty"]]
    words     = all_words[:pool_size]

    direction = SETTINGS["direction"]
    if direction == "ask":
        U.clear()
        print(f"\n{BOLD} TRANSLATION{RESET}")
        U.hr()
        print("  1. Spanish → English  (easier)")
        print("  2. English → Spanish  (harder)")
        d = input("\n [1/2, default 1] > ").strip()
        es_to_en = d != "2"
    else:
        es_to_en = direction == "es_en"

    correct = total = streak = best_streak = 0
    consec_wrong = 0
    tilt_rounds  = 0
    rounds  = SETTINGS["rounds"]
    start   = time.time()

    while True:
        pool = words[:min(200, len(words))] if tilt_rounds > 0 else words
        idx  = random.randrange(len(pool))
        word = pool[idx]
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        U.clear()
        U.game_header("TRANSLATION", correct, total, streak, best=best_streak)
        if tilt_rounds > 0:
            print(f" {U.YELLOW}TILT — easier words for {tilt_rounds} more round{'s' if tilt_rounds != 1 else ''}{RESET}")

        if SETTINGS["hints"]:
            print(f"  {U.GRAY}Hint: starts with '{answer[0].upper()}'{RESET}\n")

        inp = U.yn_input(f" {BOLD}{prompt}{RESET}\n Enter to reveal > ")
        if inp == "q":
            break

        print(f"\n   → {BOLD}{answer}{RESET}")
        if SETTINGS["show_rank"]:
            print(f"   {U.GRAY}(#{idx + 1} most common Spanish word){RESET}")

        rating = U.yn_input("\n Got it? [Y/n] > ")
        if rating == "q":
            break

        total += 1
        if rating:
            correct      += 1
            streak       += 1
            consec_wrong  = 0
            is_new        = streak > best_streak
            best_streak   = max(best_streak, streak)
            print(f"\n {U.GREEN}{U.praise()}{RESET}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
        else:
            streak       = 0
            consec_wrong += 1
            if consec_wrong >= 3:
                tilt_rounds  = 5
                consec_wrong = 0
                print(f"\n {U.YELLOW}TILT — easing up for a few rounds...{RESET}")
            else:
                print(f"\n {U.GRAY}{U.console()}{RESET}")

        if tilt_rounds > 0:
            tilt_rounds -= 1

        if rounds > 0 and total >= rounds:
            print(f"\n {U.CYAN}{BOLD}Round complete!{RESET}")
            break

        input("\n Enter to continue...")

    S.update("translation", correct, total, best_streak)
    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
