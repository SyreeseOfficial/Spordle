import random
from datetime import date
from .utils import load, GREEN, YELLOW, GRAY, BOLD, RESET, hr

PRIORITY = {GREEN: 3, YELLOW: 2, GRAY: 1}

def _score(guess, target):
    result = [GRAY] * 5
    pool = list(target)
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            result[i] = GREEN
            pool[i] = None
    for i, g in enumerate(guess):
        if result[i] == GREEN:
            continue
        if g in pool:
            result[i] = YELLOW
            pool[pool.index(g)] = None
    return result

def _render(guess, colors):
    return " ".join(f"{c}{g.upper()}{RESET}" for g, c in zip(guess, colors))

def _show_keyboard(used):
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    for row in rows:
        print("  " + " ".join(
            used.get(c, GRAY) + c.upper() + RESET for c in row
        ))

def play():
    words = load("words_5letter.json")
    word_list = [w["es"].lower() for w in words]
    word_map  = {w["es"].lower(): w["en"] for w in words}

    print(f"\n{BOLD}WORDLE{RESET} — Guess the 5-letter Spanish word in 6 tries.")
    print("[1] Daily word  [2] Random  (default 1)")
    mode = input("> ").strip()

    if mode == "2":
        target = random.choice(word_list)
    else:
        random.seed(date.today().toordinal())
        target = random.choice(word_list)

    guesses = []
    used = {}

    while len(guesses) < 6:
        hr()
        for past_guess, colors in guesses:
            print(" " + _render(past_guess, colors))
        print()
        _show_keyboard(used)
        print()

        guess = input(f"Guess {len(guesses)+1}/6 > ").strip().lower()
        if guess == "q":
            print(f"\nThe word was: {BOLD}{target}{RESET} ({word_map[target]})")
            return
        if len(guess) != 5 or not guess.isalpha():
            print("Enter a 5-letter word.")
            continue

        colors = _score(guess, target)
        guesses.append((guess, colors))

        for letter, color in zip(guess, colors):
            if PRIORITY.get(color, 0) > PRIORITY.get(used.get(letter), 0):
                used[letter] = color

        if guess == target:
            hr()
            for g, c in guesses:
                print(" " + _render(g, c))
            print(f"\n{GREEN}¡Correcto!{RESET} ({word_map[target]}) — {len(guesses)} guess{'es' if len(guesses)>1 else ''}")
            return

    hr()
    for g, c in guesses:
        print(" " + _render(g, c))
    print(f"\n{GRAY}The word was: {BOLD}{target}{RESET} {GRAY}({word_map[target]}){RESET}")
