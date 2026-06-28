import random, time
from . import utils as U
from .utils import SETTINGS, POOL_5L, BOLD, RESET

_STAGES = [
    ["       ", " +---+ ", " |   | ", "       ", "       ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", "       ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", "  |    ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|    ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|\\  ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|\\  ", " /     ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|\\  ", " / \\  ", " ===== "],
]

def _draw(wrong, word, guessed, col):
    stage = _STAGES[min(wrong, 6)]
    for line in stage:
        print(f"  {col}{line}{RESET}")
    print()
    display = "  " + "  ".join(c.upper() if c in guessed else "_" for c in word)
    print(f"{BOLD}{display}{RESET}\n")

def play():
    all_words = U.load("words_5letter.json")
    pool      = all_words[:POOL_5L[SETTINGS["difficulty"]]]
    word_map  = {w["es"].lower(): w["en"] for w in pool}
    word_list = list(word_map.keys())

    wins = losses = streak = best_streak = 0
    start = time.time()

    while True:
        target  = random.choice(word_list)
        guessed = set()
        wrong   = 0
        won     = False

        while wrong < 6:
            solved = all(c in guessed for c in target)
            if solved:
                won = True
                break

            wrong_letters = sorted(c for c in guessed if c not in target)
            col = U.GREEN if wrong == 0 else U.YELLOW if wrong < 4 else U.GRAY

            U.clear()
            U.game_header("HANGMAN", wins, wins + losses, streak, best=best_streak)
            _draw(wrong, target, guessed, col)

            wrong_str = " ".join(l.upper() for l in wrong_letters) or "—"
            print(f"  {U.GRAY}Wrong ({wrong}/6):{RESET}  {wrong_str}\n")

            guess = input(" Letter  [q = menu] > ").strip().lower()
            if guess == "q":
                U.summary(wins, wins + losses, best_streak, elapsed=int(time.time() - start))
                input(" Enter to return to menu...")
                return
            if len(guess) != 1 or not guess.isalpha():
                continue
            if guess in guessed:
                print(f"  {U.GRAY}Already guessed '{guess.upper()}'{RESET}")
                input()
                continue

            guessed.add(guess)
            if guess not in target:
                wrong += 1
        else:
            # Ran out of guesses — check if solved on last guess
            won = all(c in guessed for c in target)

        total = wins + losses + 1
        if won:
            wins   += 1
            streak += 1
            is_new  = streak > best_streak
            best_streak = max(best_streak, streak)
            U.clear()
            U.game_header("HANGMAN", wins, total, streak, best=best_streak)
            _draw(wrong, target, guessed, U.GREEN)
            print(f" {U.GREEN}{BOLD}{U.praise()}  →  {target} = {word_map[target]}{RESET}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
        else:
            losses += 1
            streak  = 0
            U.clear()
            U.game_header("HANGMAN", wins, total, streak, best=best_streak)
            _draw(6, target, set(target), U.GRAY)  # reveal full word
            print(f" {U.GRAY}The word was: {BOLD}{target}{RESET}  {U.GRAY}({word_map[target]}){RESET}")

        cont = U.yn_input("\n Play again? [Y/n] > ")
        if cont is not True:
            break

    U.summary(wins, wins + losses, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
