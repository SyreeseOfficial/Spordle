import random, time
from . import utils as U
from .utils import SETTINGS, BOLD, RESET

_FEM_ENDINGS = ("ción", "sión", "dad", "tad", "tud", "eza", "ura")
_MASC_A_ENDS = ("ma", "pa", "ta", "ca")

def _infer_gender(word):
    if any(word.endswith(e) for e in _FEM_ENDINGS):
        return "f"
    if word.endswith("a") and not any(word.endswith(e) for e in _MASC_A_ENDS):
        return "f"
    if word.endswith("o"):
        return "m"
    return None

def play():
    all_words = U.load("words.json")
    nouns = [
        {"es": w["es"], "en": w["en"], "gender": _infer_gender(w["es"])}
        for w in all_words
        if w["pos"] == "n" and _infer_gender(w["es"]) is not None
    ]

    correct = total = streak = best_streak = 0
    rounds  = SETTINGS["rounds"]
    start   = time.time()

    while True:
        word = random.choice(nouns)

        U.clear()
        U.game_header("GENDER DRILL", correct, total, streak, best=best_streak)
        print(f" {BOLD}{word['es']}{RESET}  ({word['en']})\n")
        print(f"  1. el  (masculine)")
        print(f"  2. la  (feminine)\n")

        guess = input(" [1/2  or  m/f  or  q = menu] > ").strip().lower()
        if guess == "q":
            break
        if guess in ("1", "m"):
            guess = "m"
        elif guess in ("2", "f"):
            guess = "f"
        else:
            print(" Type 1/m or 2/f.")
            input(" Enter to continue...")
            continue

        total   += 1
        article  = "el" if word["gender"] == "m" else "la"
        if guess == word["gender"]:
            correct  += 1
            streak   += 1
            is_new    = streak > best_streak
            best_streak = max(best_streak, streak)
            print(f"\n {U.GREEN}{U.praise()}  →  {article} {word['es']}{RESET}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
        else:
            streak = 0
            print(f"\n {U.GRAY}It's  {BOLD}{article} {word['es']}{RESET}  {U.GRAY}{U.console()}{RESET}")

        if rounds > 0 and total >= rounds:
            print(f"\n {U.CYAN}{BOLD}Round complete!{RESET}")
            break

        input("\n Enter to continue...")

    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
