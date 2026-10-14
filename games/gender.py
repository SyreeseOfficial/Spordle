import random
from . import utils as U
from .utils import SETTINGS, POOL, BOLD, RESET

_FEM_ENDINGS = ("ción", "sión", "dad", "tad", "tud", "eza", "ura")
_MASC_A_ENDS = ("ma", "pa", "ta", "ca")

def _infer_gender(word):
    """Fallback when words.json has no explicit "g" for a noun."""
    if any(word.endswith(e) for e in _FEM_ENDINGS):
        return "f"
    if word.endswith("a") and not any(word.endswith(e) for e in _MASC_A_ENDS):
        return "f"
    if word.endswith("o"):
        return "m"
    return None

def _gender(w):
    """'m' / 'f', or None to skip ("g": "x" marks words used with both genders)."""
    g = w.get("g") or _infer_gender(w["es"])
    return g if g in ("m", "f") else None

def play():
    words = U.load("words.json")[:POOL[SETTINGS["difficulty"]]]
    nouns = [{"es": w["es"], "en": w["en"], "gender": _gender(w)}
             for w in words if w["pos"] == "n" and _gender(w)]

    s = U.Session("GENDER DRILL")

    while True:
        word = random.choice(nouns)

        U.clear()
        s.header()
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

        article     = "el" if word["gender"] == "m" else "la"
        was_correct = (guess == word["gender"])
        if was_correct:
            s.right(f"{U.praise()}  →  {article} {word['es']}")
        else:
            s.wrong(f"It's  {BOLD}{article} {word['es']}{RESET}  {U.GRAY}")

        if not s.advance(was_correct):
            break

    s.end("gender")
