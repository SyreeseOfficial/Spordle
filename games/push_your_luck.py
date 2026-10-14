import random
from . import utils as U
from .utils import SETTINGS, POOL, BOLD, RESET

def play():
    words = U.load("words.json")[:POOL[SETTINGS["difficulty"]]]
    es_to_en = U.ask_direction(
        "PUSH YOUR LUCK",
        "  Bank points to lock them in safely.\n"
        "  Push to multiply — but one wrong and you lose the pile.\n")

    banked     = 0
    multiplier = 1
    push_pile  = 0
    s          = U.Session("PUSH YOUR LUCK", limit=False)

    while True:
        word   = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        U.clear()
        U.title_line("PUSH YOUR LUCK")
        U.hr()
        mult_col = f"{U.YELLOW}{BOLD}" if multiplier > 2 else (U.YELLOW if multiplier > 1 else U.GRAY)
        print(f" {U.GREEN}banked: {BOLD}{banked}{RESET}   "
              f"pile: {U.YELLOW}{push_pile}{RESET}   "
              f"mult: {mult_col}x{multiplier}{RESET}")
        U.hr()

        rating = U.ask(prompt, U.accepted(word, es_to_en), shown=answer)
        if rating == "q":
            if push_pile:  # quitting is not a free bank: the open pile is forfeited
                print(f"\n {U.GRAY}Pile of {push_pile} forfeited.{RESET}")
            break

        if rating:
            earned      = multiplier
            push_pile  += earned
            multiplier += 1
            s.right(f"+{earned} → pile: {push_pile}  (next mult: x{multiplier})")
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
        else:
            s.wrong(f"Wrong — lost pile of {push_pile}!  Banked total: {BOLD}{banked}{RESET}  {U.GRAY}")
            push_pile  = 0
            multiplier = 1

        U.pause(ok=rating)

    s.end("push_your_luck", footer=f" {U.CYAN}Final banked score: {BOLD}{banked}{RESET}\n",
          run=True, best_run=banked)
