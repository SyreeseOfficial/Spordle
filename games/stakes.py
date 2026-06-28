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
        print(f"\n{BOLD} HIGH STAKES{RESET}")
        U.hr()
        print(" Bet chips on your confidence before each reveal.")
        print(" Double-or-nothing available after every correct answer.\n")
        print("  1. Spanish → English")
        print("  2. English → Spanish")
        d = input("\n [1/2, default 1] > ").strip()
        es_to_en = d != "2"
    else:
        es_to_en = direction == "es_en"

    chips       = 100
    peak_chips  = 100
    correct     = 0
    total       = 0
    streak      = 0
    best_streak = 0
    don_active  = False   # double-or-nothing pending on next round
    start       = time.time()

    while chips > 0:
        word   = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        U.clear()
        diff     = SETTINGS["difficulty"].upper()
        diff_col = U.GREEN if diff == "EASY" else U.YELLOW if diff == "MEDIUM" else "\033[91m"
        w        = U.terminal_width()
        visible  = f"HIGH STAKES  [{diff}]"
        pad      = " " * max(0, (w - len(visible)) // 2)
        chip_col = U.GREEN if chips >= 100 else U.YELLOW if chips >= 50 else U.GRAY
        don_tag  = f"  {U.YELLOW}{BOLD}⚡ DOUBLE-OR-NOTHING{RESET}" if don_active else ""
        print(f"\n{pad}{BOLD}HIGH STAKES{RESET}  [{diff_col}{diff}{RESET}]")
        U.hr()
        print(f" {chip_col}chips: {BOLD}{chips}{RESET}{don_tag}")
        score_str = f"{correct}/{total}" if total else "—/—"
        stk_col = (f"{U.YELLOW}{BOLD}" if streak >= 5 else U.GREEN if streak >= 3 else U.GRAY)
        stk_str = f"  {stk_col}streak {streak}{RESET}" if streak else ""
        print(f" {U.GRAY}score {score_str}{RESET}{stk_str}")
        U.hr()

        max_bet = min(5, chips)
        print(f" {BOLD}{prompt}{RESET}\n")
        bet_raw = input(f" Bet [1-{max_bet}  /  q = quit] > ").strip()
        if bet_raw.lower() == "q":
            break
        try:
            bet = max(1, min(max_bet, int(bet_raw)))
        except ValueError:
            bet = 1

        effective = bet * (2 if don_active else 1)
        don_active = False

        inp = U.yn_input("\n [Enter to reveal  /  q = quit] > ")
        if inp == "q":
            break

        print(f"\n   → {BOLD}{answer}{RESET}")
        rating = U.yn_input("\n Got it? [Y/n] > ")
        if rating == "q":
            break

        total += 1
        if rating:
            correct     += 1
            streak      += 1
            best_streak  = max(best_streak, streak)
            chips       += effective
            peak_chips   = max(peak_chips, chips)
            print(f"\n {U.GREEN}+{effective} chips  →  {BOLD}{chips}{RESET}{U.streak_display(streak)}")
            U.play_correct()
            U.streak_milestone(streak)
            offer = input(f"\n {U.YELLOW}⚡ Double-or-nothing next? [d / Enter to skip]{RESET} > ").strip().lower()
            if offer == "d":
                don_active = True
                print(f" {U.YELLOW}Stakes doubled for next round!{RESET}")
            U.pause(ok=True)
        else:
            prev_streak = streak
            streak  = 0
            chips  -= effective
            chips   = max(chips, 0)
            print(f"\n {U.GRAY}-{effective} chips  →  {BOLD}{chips}{RESET}  {U.GRAY}{U.wrong_msg(prev_streak)}{RESET}")
            U.play_wrong()
            if chips == 0:
                print(f"\n {U.YELLOW}{BOLD}BUST! Out of chips.{RESET}")
                input(" Enter to return to menu...")
                break
            input("\n Enter to continue...")

    S.update("stakes", correct, total, best_streak, peak_chips=peak_chips)
    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    print(f" {U.CYAN}Peak chips: {BOLD}{peak_chips}{RESET}  Final chips: {BOLD}{chips}{RESET}\n")
    input(" Enter to return to menu...")
