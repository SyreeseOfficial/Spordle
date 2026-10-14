import random, time
from datetime import date
from . import utils as U
from . import stats as S
from .utils import SETTINGS, POOL_5L, BOLD, RESET

# Use string names so _score() stays theme-independent
_PRI = {"green": 3, "yellow": 2, "gray": 1}

_DAILY_SEED = 20240101  # fixed shuffle: daily words don't repeat until the whole list is used

def _score(guess, target):
    result = ["gray"] * 5
    pool   = list(target)
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            result[i] = "green"
            pool[i]   = None
    for i, g in enumerate(guess):
        if result[i] == "green":
            continue
        if g in pool:
            result[i] = "yellow"
            pool[pool.index(g)] = None
    return result

def _color(name):
    return {"green": U.GREEN, "yellow": U.YELLOW, "gray": U.GRAY}[name]

def _render(guess, colors):
    return " ".join(f"{_color(c)} {g.upper()} {RESET}" for g, c in zip(guess, colors))

def _key(c, used):
    state = used.get(c)
    if state is None:
        return c.upper()                              # untried: default color
    if state == "gray":
        return f"{U.DIM}{U.GRAY}{c.upper()}{RESET}"   # absent: dimmed
    return f"{_color(state)}{c.upper()}{RESET}"

def _keyboard(used):
    for row in ("qwertyuiop", "asdfghjkl", "zxcvbnm"):
        print("  " + " ".join(_key(c, used) for c in row))

def _daily_word(word_list):
    order = word_list[:]
    random.Random(_DAILY_SEED).shuffle(order)
    return order[date.today().toordinal() % len(order)]

def _record(won, n_guesses, start, extra_sets=None):
    g      = S.load()["wordle"]
    streak = g.get("win_streak", 0) + 1 if won else 0
    dist   = dict(g.get("guess_dist", {}))
    if won:
        dist[str(n_guesses)] = dist.get(str(n_guesses), 0) + 1
    msgs = S.update("wordle", int(won), 1, best_streak=streak, seconds=int(time.time() - start),
                    sets={"win_streak": streak, **(extra_sets or {})}, guess_dist=dist)
    U.show_msgs(msgs)

def play():
    answers   = U.five_letter()
    pool_size = POOL_5L[SETTINGS["difficulty"]]
    word_map  = {w["es"].lower(): w["en"] for w in answers}
    # any real 5-letter word (accents stripped) is an allowed guess, not just the answer pool
    valid     = {U.strip_accents(w["es"].lower()) for w in U.load("words.json") if len(w["es"]) == 5}

    U.clear()
    U.game_header("WORDLE", rounds=0)
    print(" Guess the 5-letter Spanish word in 6 tries.\n")
    print("  1. Daily word  (same for everyone today)")
    print("  2. Random word")
    mode = input("\n [1/2, default 1] > ").strip()
    daily = mode != "2"
    today = date.today().isoformat()

    if daily:
        last = S.load()["wordle"].get("last_daily", {})
        if last.get("date") == today:
            res = (f"{U.GREEN}solved in {last['guesses']}/6{RESET}" if last.get("won")
                   else f"{U.GRAY}missed{RESET}")
            print(f"\n You already played today's word: {res}  ({last.get('word', '?')})")
            if input("\n [r = random word, Enter = menu] > ").strip().lower() != "r":
                return
            daily = False
        target = _daily_word([w["es"].lower() for w in answers])
    if not daily:
        target = random.choice([w["es"].lower() for w in answers[:pool_size]])

    guesses = []
    used    = {}
    start   = time.time()

    while len(guesses) < 6:
        U.clear()
        U.game_header("WORDLE", rounds=0)

        for past_guess, colors in guesses:
            print("   " + _render(past_guess, colors))
        for _ in range(6 - len(guesses)):
            print(f"   {U.GRAY}·  ·  ·  ·  ·{RESET}")

        print()
        _keyboard(used)
        print()

        guess = input(f" Guess {len(guesses)+1}/6  [q = menu] > ").strip().lower()

        if guess == "q":
            print(f"\n The word was: {BOLD}{target}{RESET}  ({word_map.get(target, '?')})")
            if daily or guesses:  # quitting is a loss (and ends today's daily)
                _record(False, 0, start, {"last_daily": {"date": today, "won": False, "guesses": 0, "word": target}} if daily else None)
            input(" Enter to return to menu...")
            return

        guess = U.strip_accents(guess)
        if len(guess) != 5 or not guess.isalpha():
            print(" Enter a 5-letter word.")
            input(" Enter to try again...")
            continue
        if guess not in valid:
            print(" Not in the word list.")
            input(" Enter to try again...")
            continue

        colors = _score(guess, target)
        guesses.append((guess, colors))

        for letter, color in zip(guess, colors):
            if _PRI.get(color, 0) > _PRI.get(used.get(letter), 0):
                used[letter] = color

        if guess == target:
            U.clear()
            U.game_header("WORDLE", rounds=0)
            for g, c in guesses:
                print("   " + _render(g, c))
            msgs = ["Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!"]
            print(f"\n {U.GREEN}{BOLD}{msgs[min(len(guesses)-1, 5)]}{RESET}  ({word_map.get(target, '?')})")
            _record(True, len(guesses), start,
                    {"last_daily": {"date": today, "won": True, "guesses": len(guesses), "word": target}} if daily else None)
            input("\n Enter to return to menu...")
            return

    U.clear()
    U.game_header("WORDLE", rounds=0)
    for g, c in guesses:
        print("   " + _render(g, c))
    print(f"\n {U.GRAY}The word was: {BOLD}{target}{RESET}  {U.GRAY}({word_map.get(target, '?')}){RESET}")
    _record(False, 0, start,
            {"last_daily": {"date": today, "won": False, "guesses": 6, "word": target}} if daily else None)
    input("\n Enter to return to menu...")
