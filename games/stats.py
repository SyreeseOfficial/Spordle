import csv, json, os
from datetime import date, timedelta
from . import utils as U
from .utils import BOLD, RESET

_PATH = os.path.expanduser("~/.spordle_stats.json")

_GAMES = ["translation","wordle","conjugation","gender","false_friends",
          "rapid_fire","hangman","anagram","number_drill",
          "roguelike","push_your_luck","stakes"]

_ACHIEVEMENTS = [
    ("first_play",  "First Play",     lambda d: sum(g.get("played",0)  for g in d.values() if isinstance(g,dict)) >= 1),
    ("first_100",   "First 100",      lambda d: sum(g.get("correct",0) for g in d.values() if isinstance(g,dict)) >= 100),
    ("unstoppable", "Unstoppable",    lambda d: any(g.get("best_streak",0) >= 25 for g in d.values() if isinstance(g,dict))),
    ("broke_bank",  "Broke the Bank", lambda d: d.get("stakes",{}).get("peak_chips",0) >= 500),
    ("survived",    "Survived",       lambda d: d.get("roguelike",{}).get("best_run",0) >= 30),
    ("century",     "Century",        lambda d: sum(g.get("played",0)  for g in d.values() if isinstance(g,dict)) >= 100),
    ("polyglot",    "Polyglot",       lambda d: len(d.get("translation",{}).get("mastered_words",[])) >= 25),
]

def _blank():
    d = {g: {"played": 0, "correct": 0, "best_streak": 0} for g in _GAMES}
    d["total_seconds"]   = 0
    d["login_streak"]    = 0
    d["last_played_date"] = ""
    d["achievements"]    = []
    return d

def load():
    if os.path.exists(_PATH):
        try:
            with open(_PATH) as f:
                data = json.load(f)
            blank = _blank()
            for g in _GAMES:
                blank[g].update(data.get(g, {}))
            for k in ("total_seconds", "login_streak", "last_played_date", "achievements"):
                if k in data:
                    blank[k] = data[k]
            if "_last" in data:
                blank["_last"] = data["_last"]
            return blank
        except Exception:
            pass
    return _blank()

def _save(data):
    with open(_PATH, "w") as f:
        json.dump(data, f, indent=2)

def _check_achievements(data):
    earned = set(data.get("achievements", []))
    for slug, _, cond in _ACHIEVEMENTS:
        if slug not in earned:
            try:
                if cond(data):
                    earned.add(slug)
            except Exception:
                pass
    data["achievements"] = list(earned)

def update(game, correct, total, best_streak=0, **extra):
    if total == 0:
        return
    data = load()
    g = data.setdefault(game, {"played": 0, "correct": 0, "best_streak": 0})
    g["played"]      += total
    g["correct"]     += correct
    g["best_streak"]  = max(g["best_streak"], best_streak)
    for k, v in extra.items():
        if isinstance(v, (list, dict)):
            g[k] = v
        else:
            g[k] = max(g.get(k, 0), v)
    data["_last"] = {"game": game, "correct": correct, "total": total, "best_streak": best_streak}

    today = date.today().isoformat()
    last  = data.get("last_played_date", "")
    if last == today:
        pass
    elif last == (date.today() - timedelta(days=1)).isoformat():
        data["login_streak"] = data.get("login_streak", 0) + 1
    else:
        data["login_streak"] = 1
    data["last_played_date"] = today

    _check_achievements(data)
    _save(data)

def add_time(seconds):
    if seconds < 5:
        return
    data = load()
    data["total_seconds"] = data.get("total_seconds", 0) + seconds
    _save(data)

def get_last():
    return load().get("_last")

def reset():
    _save(_blank())

def set_list(game, key, items):
    data = load()
    data.setdefault(game, {})
    data[game][key] = items
    _save(data)

def _fmt_time(seconds):
    h, rem = divmod(int(seconds), 3600)
    m = rem // 60
    return f"{h}h {m:02d}m" if h else f"{m}m"

def _show_miss_words(data):
    miss = data.get("translation", {}).get("miss_words", [])
    U.clear()
    print(f"\n{BOLD} MOST-MISSED WORDS{RESET}  {U.GRAY}(Translation SRS queue){RESET}")
    U.hr()
    if not miss:
        print(f"\n  {U.GRAY}No missed words on record. Keep playing!{RESET}")
    else:
        shown = miss[-10:] if len(miss) > 10 else miss
        for w in reversed(shown):
            print(f"   {U.YELLOW}• {w}{RESET}")
        if len(miss) > 10:
            print(f"\n  {U.GRAY}({len(miss)} total in queue, showing 10 most recent){RESET}")
    U.hr()
    input("\n Enter to go back...")

def _export(data):
    path = os.path.expanduser("~/.spordle_export.csv")
    _LABELS = {
        "translation":"Translation","wordle":"Wordle","conjugation":"Verb Conjugation",
        "gender":"Gender Drill","false_friends":"False Friends","rapid_fire":"Rapid Fire",
        "hangman":"Hangman","anagram":"Anagram","number_drill":"Number Drill",
        "roguelike":"Roguelike","push_your_luck":"Push Your Luck","stakes":"High Stakes",
    }
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["game","played","correct","best_streak"])
        for key, label in _LABELS.items():
            g = data.get(key, {})
            w.writerow([label, g.get("played",0), g.get("correct",0), g.get("best_streak",0)])
    print(f"\n  {U.GREEN}Exported to {path}{RESET}")
    input("  Enter to continue...")

def show():
    while True:
        data = load()
        U.clear()
        print(f"\n{BOLD} MY STATS{RESET}")
        U.hr()

        # Global summary line
        streak    = data.get("login_streak", 0)
        total_sec = data.get("total_seconds", 0)
        mastered  = len(data.get("translation", {}).get("mastered_words", []))
        streak_str  = f"⚡ {streak}-day streak" if streak else "no streak yet"
        time_str    = _fmt_time(total_sec) if total_sec else "—"
        print(f"  {U.CYAN}{streak_str}{RESET}   {U.GRAY}time: {time_str}   mastered: {mastered} words{RESET}")
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

        # Achievements
        earned = data.get("achievements", [])
        if earned:
            U.hr()
            _slug_to_name = {s: n for s, n, _ in _ACHIEVEMENTS}
            badges = "   ".join(f"{U.YELLOW}★ {_slug_to_name.get(s,s)}{RESET}" for s in earned)
            print(f"\n  {BOLD}ACHIEVEMENTS{RESET}  {badges}")

        U.hr()
        print(f"  {U.GRAY}[m] most-missed words   [e] export CSV   Enter to go back{RESET}")
        choice = input("\n > ").strip().lower()
        if choice == "m":
            _show_miss_words(data)
        elif choice == "e":
            _export(data)
        else:
            break
