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
        print(f"\n{BOLD} PUSH YOUR LUCK{RESET}")
        U.hr()
        print("  Bank points to lock them in safely.")
        print("  Push to multiply — but one wrong and you lose the pile.\n")
        print("  1. Spanish → English")
        print("  2. English → Spanish")
        d = input("\n [1/2, default 1] > ").strip()
        es_to_en = d != "2"
    else:
        es_to_en = direction == "es_en"

    banked     = 0
    multiplier = 1
    push_pile  = 0
    correct    = 0
    total      = 0
    start      = time.time()

    while True:
        word   = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        U.clear()
        diff     = SETTINGS["difficulty"].upper()
        diff_col = U.GREEN if diff == "EASY" else U.YELLOW if diff == "MEDIUM" else "\033[91m"
        w        = U.terminal_width()
        visible  = f"PUSH YOUR LUCK  [{diff}]"
        pad      = " " * max(0, (w - len(visible)) // 2)
        print(f"\n{pad}{BOLD}PUSH YOUR LUCK{RESET}  [{diff_col}{diff}{RESET}]")
        U.hr()
        mult_col = f"{U.YELLOW}{BOLD}" if multiplier > 2 else (U.YELLOW if multiplier > 1 else U.GRAY)
        print(f" {U.GREEN}banked: {BOLD}{banked}{RESET}   "
              f"pile: {U.YELLOW}{push_pile}{RESET}   "
              f"mult: {mult_col}x{multiplier}{RESET}")
        U.hr()
        print(f" {BOLD}{prompt}{RESET}\n")

        inp = U.yn_input(" [Enter to reveal  /  q = quit] > ")
        if inp == "q":
            banked += push_pile  # bank on quit
            break

        print(f"\n   → {BOLD}{answer}{RESET}")
        rating = U.yn_input("\n Got it? [Y/n] > ")
        if rating == "q":
            banked += push_pile
            break

        total += 1
        if rating:
            correct   += 1
            earned     = multiplier
            push_pile += earned
            multiplier += 1
            print(f"\n {U.GREEN}+{earned} → pile: {push_pile}  (next mult: x{multiplier}){RESET}")
            print(f"\n  1. {U.GREEN}Bank {push_pile} pts{RESET}  {U.GRAY}(safe total: {banked + push_pile}){RESET}")
            print(f"  2. {U.YELLOW}Push for x{multiplier}{RESET}  {U.GRAY}(risky){RESET}\n")
            choice = input(" [1/Enter = bank   2 = push] > ").strip()
            if choice == "2":
                print(f" {U.YELLOW}Pushing for x{multiplier}...{RESET}")
            else:
                banked    += push_pile
                push_pile  = 0
                multiplier = 1
                print(f" {U.GREEN}{BOLD}Banked! Total: {banked}{RESET}")
            U.play_correct()
        else:
            prev_streak = total - correct  # not streak-based but still track
            print(f"\n {U.GRAY}Wrong — lost pile of {push_pile}!  Banked total: {BOLD}{banked}{RESET}  {U.GRAY}{U.console()}{RESET}")
            push_pile  = 0
            multiplier = 1
            U.play_wrong()

        U.pause(ok=rating)

    S.update("push_your_luck", correct, total, best_run=banked)
    U.summary(correct, total, 0, elapsed=int(time.time() - start))
    print(f" {U.CYAN}Final banked score: {BOLD}{banked}{RESET}\n")
    input(" Enter to return to menu...")
