import random
from . import utils as U
from .utils import SETTINGS, POOL_5L, BOLD, RESET

def _shuffle(word):
    letters = list(word)
    for _ in range(50):
        random.shuffle(letters)
        if letters != list(word):
            return "".join(letters)
    return "".join(letters)

def play():
    everything = U.five_letter()
    pool       = everything[:POOL_5L[SETTINGS["difficulty"]]]
    word_map   = {w["es"].lower(): w for w in pool}
    word_list  = list(word_map)
    # hacer/echar, padre/pared...: any real word with the same letters is a valid answer
    by_letters = {}
    for w in everything:
        by_letters.setdefault("".join(sorted(w["es"].lower())), set()).add(w["es"].lower())

    s = U.Session("ANAGRAM")

    while True:
        target    = random.choice(word_list)
        entry     = word_map[target]
        scrambled = _shuffle(target)

        U.clear()
        s.header()
        print(f" Unscramble the Spanish word:\n")
        print(f"  {BOLD}{' '.join(scrambled.upper())}{RESET}\n")
        # many glosses contain the answer itself (hotel, color...) — then show only the word type
        if U.strip_accents(target) in entry["en"].lower():
            clue = {"n": "noun", "v": "verb", "adj": "adjective", "adv": "adverb"}.get(entry["pos"], "word")
            print(f"  {U.GRAY}Hint: a {clue}, {len(target)} letters{RESET}\n")
        else:
            print(f"  {U.GRAY}Meaning: {entry['en']}{RESET}\n")

        guess = input(" [q = menu] > ").strip().lower()
        if guess == "q":
            break

        ok = guess in by_letters.get("".join(sorted(target)), ())
        if ok:
            note = f"  {U.GRAY}(I had: {target}){RESET}" if guess != target else ""
            s.right(f"{U.praise()}  →  {guess}", note=note)
        else:
            s.wrong(f"Answer: {BOLD}{target}{RESET}  {U.GRAY}")

        if not s.advance(ok):
            break

    s.end("anagram")
