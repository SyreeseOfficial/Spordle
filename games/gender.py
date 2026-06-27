import random
from .utils import load, GREEN, GRAY, BOLD, RESET, hr

# Only endings we're confident about — avoids teaching wrong genders
_FEM_ENDINGS = ("ción", "sión", "dad", "tad", "tud", "eza", "ura")
_MASC_A_ENDINGS = ("ma", "pa", "ta", "ca")  # Greek-origin -ma words etc. are masculine

def _infer_gender(word):
    if any(word.endswith(e) for e in _FEM_ENDINGS):
        return "f"
    if word.endswith("a") and not any(word.endswith(e) for e in _MASC_A_ENDINGS):
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

    print(f"\n{BOLD}GENDER DRILL{RESET} — Is the noun masculine or feminine?")
    print("Type 'm' or 'f' (or 'q' to quit).\n")
    print(f"({len(nouns)} nouns in pool)\n")

    correct = total = 0

    while True:
        word = random.choice(nouns)
        hr()
        print(f"{BOLD}{word['es']}{RESET} ({word['en']})")

        guess = input("[m/f] > ").strip().lower()
        if guess == "q":
            break
        if guess not in ("m", "f"):
            print("Type 'm' or 'f'.")
            continue

        total += 1
        article = "el" if word["gender"] == "m" else "la"
        if guess == word["gender"]:
            correct += 1
            print(f"{GREEN}✓ {article} {word['es']}{RESET}")
        else:
            print(f"{GRAY}✗ It's {BOLD}{article} {word['es']}{RESET}")

    if total:
        pct = int(correct / total * 100)
        print(f"\nScore: {correct}/{total} ({pct}%)")
