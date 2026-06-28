import random, time
from . import utils as U
from . import stats as S
from .utils import SETTINGS, POOL, BOLD, RESET

def _hearts(lives, max_lives):
    return U.GREEN + "♥ " * lives + U.GRAY + "♡ " * (max_lives - lives) + RESET

def _header(lives, max_lives, correct):
    diff     = SETTINGS["difficulty"].upper()
    diff_col = U.GREEN if diff == "EASY" else U.YELLOW if diff == "MEDIUM" else "\033[91m"
    w        = U.terminal_width()
    visible  = f"ROGUELIKE  [{diff}]"
    pad      = " " * max(0, (w - len(visible)) // 2)
    print(f"\n{pad}{BOLD}ROGUELIKE{RESET}  [{diff_col}{diff}{RESET}]")
    print(f" {_hearts(lives, max_lives)}   {U.CYAN}score {BOLD}{correct}{RESET}")
    U.hr()

def play():
    all_words = U.load("words.json")
    pool_size = POOL[SETTINGS["difficulty"]]
    words     = all_words[:pool_size]

    max_lives   = SETTINGS["rl_lives"]
    lives       = max_lives
    correct     = 0
    total       = 0
    streak      = 0
    best_streak = 0
    start       = time.time()

    while lives > 0:
        word   = random.choice(words)
        prompt = word["es"]
        answer = word["en"]

        U.clear()
        _header(lives, max_lives, correct)
        print(f" {BOLD}{prompt}{RESET}\n")

        inp = U.yn_input(" [Enter to reveal  /  q = quit] > ")
        if inp == "q":
            break

        print(f"\n   → {BOLD}{answer}{RESET}")
        rating = U.yn_input("\n Got it? [Y/n] > ")
        if rating == "q":
            break

        total += 1
        if rating:
            correct += 1
            streak  += 1
            best_streak = max(best_streak, streak)
            print(f"\n {U.GREEN}+1  {U.praise()}{RESET}{U.streak_display(streak)}")
            U.play_correct()
            U.streak_milestone(streak)
            U.pause(ok=True)
        else:
            prev_streak = streak
            streak = 0
            lives -= 1
            U.play_wrong()
            if lives > 0:
                print(f"\n {U.GRAY}Nope — {BOLD}{answer}{RESET}  {U.wrong_msg(prev_streak)}")
                print(f" {_hearts(lives, max_lives)} remaining")
                input("\n Enter to continue...")
            else:
                U.play_game_over()
                U.clear()
                print(f"\n {U.YELLOW}{BOLD}GAME OVER!{RESET}")
                print(f" The word was: {BOLD}{answer}{RESET}")
                print(f"\n {U.CYAN}Final score: {BOLD}{correct}{RESET}")

    S.update("roguelike", correct, total, best_streak, best_run=correct)
    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
