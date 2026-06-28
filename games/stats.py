import json, os
from . import utils as U
from .utils import BOLD, RESET

_PATH = os.path.expanduser("~/.spordle_stats.json")

_GAMES = ["translation","wordle","conjugation","gender","false_friends",
          "rapid_fire","hangman","anagram","number_drill",
          "roguelike","push_your_luck","stakes"]

def _blank():
    return {g: {"played": 0, "correct": 0, "best_streak": 0} for g in _GAMES}

def load():
    if os.path.exists(_PATH):
        try:
            with open(_PATH) as f:
                data = json.load(f)
            blank = _blank()
            for g in _GAMES:
                blank[g].update(data.get(g, {}))
            return blank
        except Exception:
            pass
    return _blank()

def _save(data):
    with open(_PATH, "w") as f:
        json.dump(data, f, indent=2)

def update(game, correct, total, best_streak=0, **extra):
    if total == 0:
        return
    data = load()
    g = data.setdefault(game, {"played": 0, "correct": 0, "best_streak": 0})
    g["played"]      += total
    g["correct"]     += correct
    g["best_streak"]  = max(g["best_streak"], best_streak)
    for k, v in extra.items():
        g[k] = max(g.get(k, 0), v)
    _save(data)

def reset():
    _save(_blank())

def show():
    data = load()
    U.clear()
    print(f"\n{BOLD} MY STATS{RESET}")
    U.hr()

    _LABELS = {
        "translation":    "Translation",
        "wordle":         "Wordle",
        "conjugation":    "Verb Conjugation",
        "gender":         "Gender Drill",
        "false_friends":  "False Friends",
        "rapid_fire":     "Rapid Fire",
        "hangman":        "Hangman",
        "anagram":        "Anagram",
        "number_drill":   "Number Drill",
        "roguelike":      "Roguelike",
        "push_your_luck": "Push Your Luck",
        "stakes":         "High Stakes",
    }

    for key, label in _LABELS.items():
        g = data.get(key, {})
        played  = g.get("played", 0)
        correct = g.get("correct", 0)
        best    = g.get("best_streak", 0)

        if played == 0:
            print(f"  {label:<22} {U.GRAY}no data{RESET}")
            continue

        pct = int(correct / played * 100) if played else 0
        col = U.GREEN if pct >= 80 else U.YELLOW if pct >= 60 else U.GRAY
        stk = f"  best streak {BOLD}{best}{RESET}" if best else ""

        if key == "rapid_fire":
            bpm = g.get("best_per_min", 0)
            print(f"  {BOLD}{label:<22}{RESET} {played} sessions  best {g.get('best_score', 0)} corr  {bpm}/min")
        elif key == "roguelike":
            print(f"  {BOLD}{label:<22}{RESET} {played:>4} runs   {col}{correct}/{played} ({pct}%){RESET}  best run {BOLD}{g.get('best_run', 0)}{RESET}")
        elif key == "push_your_luck":
            print(f"  {BOLD}{label:<22}{RESET} {played:>4} rounds  best banked {BOLD}{g.get('best_run', 0)}{RESET}")
        elif key == "stakes":
            print(f"  {BOLD}{label:<22}{RESET} {played:>4} rounds  {col}{correct}/{played} ({pct}%){RESET}  peak chips {BOLD}{g.get('peak_chips', 100)}{RESET}")
        else:
            print(f"  {BOLD}{label:<22}{RESET} {played:>4} rounds  {col}{correct}/{played} ({pct}%){RESET}{stk}")

    U.hr()
    input("\n Enter to return to menu...")
