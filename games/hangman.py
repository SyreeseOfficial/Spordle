import contextlib, io, random
from . import utils as U
from .utils import SETTINGS, POOL, BOLD, RESET

# word length by difficulty: the setting changes how hard the words are, not just how rare
_LENGTHS = {"easy": (5, 5), "medium": (6, 7), "hard": (8, 99)}

_STAGES = [
    ["       ", " +---+ ", " |   | ", "       ", "       ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", "       ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", "  |    ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|    ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|\\  ", "       ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|\\  ", " /     ", " ===== "],
    ["       ", " +---+ ", " |   | ", "  O    ", " /|\\  ", " / \\  ", " ===== "],
]

def _draw(wrong, word, norm, guessed, col):
    # gallows stay gray, the figure takes the stage color
    for i, line in enumerate(_STAGES[min(wrong, 6)]):
        print(f"  {col if 3 <= i <= 5 else U.GRAY}{line}{RESET}")
    print()
    display = "  " + "  ".join(c.upper() if n in guessed else "_" for c, n in zip(word, norm))
    print(f"{BOLD}{display}{RESET}\n")

def _board(s, wrong, target, norm, guessed, col, outcome):
    """Redraw the finished board, then print the outcome (counted before the header is drawn)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        outcome()
    U.clear()
    s.header()
    _draw(wrong, target, norm, guessed, col)
    print(buf.getvalue(), end="")

def play():
    lo, hi = _LENGTHS[SETTINGS["difficulty"]]
    pool   = [w for w in U.load("words.json")[:POOL[SETTINGS["difficulty"]]]
              if w["es"].isalpha() and lo <= len(w["es"]) <= hi]

    s = U.Session("HANGMAN", limit=False)

    while True:
        entry   = random.choice(pool)
        target  = entry["es"].lower()
        norm    = U.strip_accents(target)   # guesses ignore accents; ñ is its own letter
        guessed = set()
        wrong   = 0
        won     = False

        while wrong < 6:
            if all(n in guessed for n in norm):
                won = True
                break

            wrong_letters = sorted(c for c in guessed if c not in norm)
            col = U.GREEN if wrong == 0 else U.YELLOW if wrong < 4 else U.RED

            U.clear()
            s.header()
            _draw(wrong, target, norm, guessed, col)

            wrong_str = " ".join(l.upper() for l in wrong_letters) or "—"
            print(f"  {U.GRAY}Wrong ({wrong}/6):{RESET}  {wrong_str}\n")

            guess = input(" Letter or whole word  [q = menu] > ").strip().lower()
            if guess == "q":
                s.end("hangman")
                return
            if not guess.isalpha():
                print(f"  {U.GRAY}Letters only.{RESET}")
                input()
                continue
            guess = U.strip_accents(guess)
            if len(guess) > 1:
                if guess == norm:
                    guessed.update(norm)
                else:
                    wrong += 1
                    print(f"  {U.GRAY}'{guess}' isn't the word.{RESET}")
                    input()
                continue
            if guess in guessed:
                print(f"  {U.GRAY}Already guessed '{guess.upper()}'{RESET}")
                input()
                continue

            guessed.add(guess)
            if guess not in norm:
                wrong += 1
        else:
            won = all(n in guessed for n in norm)

        if won:
            _board(s, wrong, target, norm, guessed, U.GREEN,
                   lambda: s.right(f"{U.praise()}  →  {target} = {entry['en']}"))
        else:
            _board(s, 6, target, norm, set(norm), U.GRAY,   # reveal full word
                   lambda: s.wrong(f"The word was: {BOLD}{target}{RESET}  {U.GRAY}({entry['en']})  "))

        if U.yn_input("\n Play again? [Y/n] > ") is not True:
            break

    s.end("hangman")
