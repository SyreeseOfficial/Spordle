import random
from .utils import (load, GREEN, GRAY, BOLD, RESET,
                    clear, game_header, praise, console, streak_display, summary)

_FEM_ENDINGS  = ("ción", "sión", "dad", "tad", "tud", "eza", "ura")
_MASC_A_ENDS  = ("ma", "pa", "ta", "ca")

def _infer_gender(word):
    if any(word.endswith(e) for e in _FEM_ENDINGS):
        return "f"
    if word.endswith("a") and not any(word.endswith(e) for e in _MASC_A_ENDS):
        return "f"
    if word.endswith("o"):
        return "m"
    return None

def play():
    all_words = load("words.json")
    nouns = [
        {"es": w["es"], "en": w["en"], "gender": _infer_gender(w["es"])}
        for w in all_words
        if w["pos"] == "n" and _infer_gender(w["es"]) is not None
    ]

    correct = total = streak = best_streak = 0

    while True:
        word = random.choice(nouns)

        clear()
        game_header("GENDER DRILL", correct, total, streak)
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

        total += 1
        article = "el" if word["gender"] == "m" else "la"
        if guess == word["gender"]:
            correct += 1
            streak += 1
            best_streak = max(best_streak, streak)
            print(f"\n {GREEN}{praise()}  →  {article} {word['es']}{RESET}{streak_display(streak)}")
        else:
            streak = 0
            print(f"\n {GRAY}It's  {BOLD}{article} {word['es']}{RESET}  {GRAY}{console()}{RESET}")

        input("\n Enter to continue...")

    summary(correct, total, best_streak)
    input(" Enter to return to menu...")
