import random, time
from . import utils as U
from . import stats as S
from .utils import SETTINGS, BOLD, RESET

def play():
    friends = U.load("false_friends.json")
    random.shuffle(friends)

    correct = total = streak = best_streak = 0
    rounds  = SETTINGS["rounds"]
    start   = time.time()

    for entry in friends:
        U.clear()
        U.game_header("FALSE FRIENDS", correct, total, streak, best=best_streak)
        print(f" {BOLD}{entry['es']}{RESET}\n")
        print(f" {U.GRAY}Looks like:{RESET}  \"{entry['looks_like']}\"\n")

        inp = U.yn_input(" What does it ACTUALLY mean?  [Enter to reveal  /  q = menu] > ")
        if inp == "q":
            break

        print(f"\n {U.YELLOW}Actually:{RESET}  {BOLD}{entry['real_en']}{RESET}")
        print(f" {U.GRAY}Remember:{RESET}  {entry['es']}  ≠  {entry['looks_like']}\n")

        rating = U.yn_input(" Did you know it? [Y/n] > ")
        if rating == "q":
            break

        total += 1
        if rating:
            correct  += 1
            streak   += 1
            is_new    = streak > best_streak
            best_streak = max(best_streak, streak)
            print(f"\n {U.GREEN}{U.praise()}{RESET}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
            U.streak_milestone(streak)
        else:
            streak = 0
            print(f"\n {U.GRAY}{U.console()}{RESET}")

        if rounds > 0 and total >= rounds:
            print(f"\n {U.CYAN}{BOLD}Round complete!{RESET}")
            break

        U.pause(ok=rating)

    S.update("false_friends", correct, total, best_streak)
    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
