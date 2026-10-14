import random
from . import utils as U
from .utils import SETTINGS, POOL, BOLD, RESET

def _hearts(lives, max_lives):
    return U.GREEN + "♥ " * lives + U.GRAY + "♡ " * (max_lives - lives) + RESET

def _header(lives, max_lives, correct):
    U.title_line("ROGUELIKE")
    print(f" {_hearts(lives, max_lives)}   {U.CYAN}score {BOLD}{correct}{RESET}")
    U.hr()

def play():
    words    = U.load("words.json")[:POOL[SETTINGS["difficulty"]]]
    es_to_en = U.ask_direction("ROGUELIKE")

    max_lives = SETTINGS["rl_lives"]
    lives     = max_lives
    s         = U.Session("ROGUELIKE", limit=False)

    while lives > 0:
        word   = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        U.clear()
        _header(lives, max_lives, s.correct)

        rating = U.ask(prompt, U.accepted(word, es_to_en), shown=answer)
        if rating == "q":
            break

        if rating:
            s.right(f"+1  {U.praise()}")
        else:
            lives -= 1
            s.wrong(f"Nope — {BOLD}{answer}{RESET}  {U.GRAY}")
            if lives > 0:
                print(f" {_hearts(lives, max_lives)} remaining")
            else:
                U.sfx("game_over")
                U.clear()
                print(f"\n {U.YELLOW}{BOLD}GAME OVER!{RESET}")
                print(f" The word was: {BOLD}{answer}{RESET}")
                print(f"\n {U.CYAN}Final score: {BOLD}{s.correct}{RESET}")
                break

        s.advance(rating)

    s.end("roguelike", run=True, best_run=s.correct)
