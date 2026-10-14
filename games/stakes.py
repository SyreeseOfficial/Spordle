import random
from . import utils as U
from .utils import SETTINGS, POOL, BOLD, RESET

def play():
    words = U.load("words.json")[:POOL[SETTINGS["difficulty"]]]
    es_to_en = U.ask_direction(
        "HIGH STAKES",
        " Bet chips on your confidence before each reveal.\n"
        " Double Bet available after every correct answer.\n")

    chips      = 100
    peak_chips = 100
    dbl_active = False   # Double Bet pending on next round
    s          = U.Session("HIGH STAKES", limit=False)

    while chips > 0:
        word   = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        U.clear()
        chip_col = U.GREEN if chips >= 100 else U.YELLOW if chips >= 50 else U.GRAY
        dbl_tag  = f"  {U.YELLOW}{BOLD}⚡ DOUBLE BET{RESET}" if dbl_active else ""
        U.title_line("HIGH STAKES")
        U.hr()
        print(f" {chip_col}chips: {BOLD}{chips}{RESET}{dbl_tag}")
        score_str = f"{s.correct}/{s.total}" if s.total else "—/—"
        stk_col = (f"{U.YELLOW}{BOLD}" if s.streak >= 5 else U.GREEN if s.streak >= 3 else U.GRAY)
        stk_str = f"  {stk_col}streak {s.streak}{RESET}" if s.streak else ""
        print(f" {U.GRAY}score {score_str}{RESET}{stk_str}")
        U.hr()

        max_bet = min(max(5, chips // 10), chips)  # the cap grows with your stack
        print(f" {BOLD}{prompt}{RESET}\n")
        bet_raw = input(f" Bet [1-{max_bet}  /  q = quit] > ").strip()
        if bet_raw.lower() == "q":
            break
        try:
            bet = max(1, min(max_bet, int(bet_raw)))
        except ValueError:
            bet = 1

        effective  = bet * (2 if dbl_active else 1)
        dbl_active = False

        print()
        rating = U.ask(prompt, U.accepted(word, es_to_en), shown=answer, show_prompt=False)
        if rating == "q":
            break

        if rating:
            chips     += effective
            peak_chips = max(peak_chips, chips)
            s.right(f"+{effective} chips  →  {chips}")
            offer = input(f"\n {U.YELLOW}⚡ Double Bet next? [d / Enter to skip]{RESET} > ").strip().lower()
            if offer == "d":
                dbl_active = True
                print(f" {U.YELLOW}Bet doubled for next round!{RESET}")
        else:
            chips = max(chips - effective, 0)
            s.wrong(f"-{effective} chips  →  {BOLD}{chips}{RESET}  {U.GRAY}")
            if chips == 0:
                print(f"\n {U.YELLOW}{BOLD}BUST! Out of chips.{RESET}")
                break

        s.advance(rating)

    s.end("stakes",
          footer=f" {U.CYAN}Peak chips: {BOLD}{peak_chips}{RESET}  Final chips: {BOLD}{chips}{RESET}\n",
          run=True, peak_chips=peak_chips)
