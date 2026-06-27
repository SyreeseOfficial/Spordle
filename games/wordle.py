import random
from datetime import date
from .utils import (load, SETTINGS, POOL_5L, GREEN, YELLOW, GRAY, BOLD, RESET,
                    clear, hr, game_header)

_PRIORITY = {GREEN: 3, YELLOW: 2, GRAY: 1}

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
    return " ".join(f"{c} {g.upper()} {RESET}" for g, c in zip(guess, colors))

def _keyboard(used):
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    for row in rows:
        print("  " + " ".join(used.get(c, GRAY) + c.upper() + RESET for c in row))

def play():
    all_words  = load("words_5letter.json")
    pool_size  = POOL_5L[SETTINGS["difficulty"]]
    words      = all_words[:pool_size]
    word_list  = [w["es"].lower() for w in words]
    word_map   = {w["es"].lower(): w["en"] for w in words}

    clear()
    game_header("WORDLE")
    print(" Guess the 5-letter Spanish word in 6 tries.\n")
    print("  1. Daily word  (same for everyone today)")
    print("  2. Random word")
    mode = input("\n [1/2, default 1] > ").strip()

    if mode == "2":
        target = random.choice(word_list)
    else:
        random.seed(date.today().toordinal() + pool_size)
        target = random.choice(word_list)

    guesses = []
    used    = {}

    while len(guesses) < 6:
        clear()
        game_header("WORDLE", streak=0)

        # Draw board
        for past_guess, colors in guesses:
            print("   " + _render(past_guess, colors))
        for _ in range(6 - len(guesses)):
            print(f"   {GRAY}·  ·  ·  ·  ·{RESET}")

        print()
        _keyboard(used)
        print()

        guess = input(f" Guess {len(guesses)+1}/6  [q = menu] > ").strip().lower()

        if guess == "q":
            print(f"\n The word was: {BOLD}{target}{RESET}  ({word_map.get(target, '?')})")
            input(" Enter to return to menu...")
            return

        if len(guess) != 5 or not guess.isalpha():
            print(" Enter a 5-letter word.")
            input(" Enter to try again...")
            continue

        colors = _score(guess, target)
        guesses.append((guess, colors))

        for letter, color in zip(guess, colors):
            if _PRIORITY.get(color, 0) > _PRIORITY.get(used.get(letter), 0):
                used[letter] = color

        if guess == target:
            clear()
            game_header("WORDLE")
            for g, c in guesses:
                print("   " + _render(g, c))
            msgs = ["Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!"]
            print(f"\n {GREEN}{BOLD}{msgs[min(len(guesses)-1, 5)]}{RESET}  ({word_map.get(target, '?')})")
            input("\n Enter to return to menu...")
            return

    clear()
    game_header("WORDLE")
    for g, c in guesses:
        print("   " + _render(g, c))
    print(f"\n {GRAY}The word was: {BOLD}{target}{RESET}  {GRAY}({word_map.get(target, '?')}){RESET}")
    input("\n Enter to return to menu...")
