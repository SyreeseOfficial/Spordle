import csv, os
from datetime import date, timedelta
from . import utils as U
from .registry import KEYS, LABELS
from .utils import BOLD, RESET

def _sum(d, key):
    return sum(g.get(key, 0) for g in d.values() if isinstance(g, dict))

def _rounds(d):
    # Rapid Fire's `played` counts words, so it contributes whole runs instead
    return sum(g.get("runs", 0) if k == "rapid_fire" else g.get("played", 0)
               for k, g in d.items() if isinstance(g, dict))

_ACHIEVEMENTS = [
    ("first_play",  "First Play",     lambda d: _rounds(d) >= 1),
    ("first_100",   "First 100",      lambda d: _sum(d, "correct") >= 100),
    ("unstoppable", "Unstoppable",    lambda d: any(g.get("best_streak", 0) >= 25 for g in d.values() if isinstance(g, dict))),
    ("broke_bank",  "Broke the Bank", lambda d: d.get("stakes", {}).get("peak_chips", 0) >= 500),
    ("survived",    "Survived",       lambda d: d.get("roguelike", {}).get("best_run", 0) >= 30),
    ("century",     "Century",        lambda d: _rounds(d) >= 100),
    ("polyglot",    "Polyglot",       lambda d: len(d.get("translation", {}).get("mastered_words", [])) >= 25),
    ("quest_hunter","Quest Hunter",   lambda d: d.get("quest_days", 0) >= 3),
]
_NAMES = {s: n for s, n, _ in _ACHIEVEMENTS}

def _blank():
    d = {g: {"played": 0, "correct": 0, "best_streak": 0} for g in KEYS}
    d["total_seconds"]    = 0
    d["login_streak"]     = 0
    d["last_played_date"] = ""
    d["achievements"]     = []
    d["quest_days"]       = 0
    return d

def load():
    try:
        import json
        with open(U.STATS_PATH) as f:
            data = json.load(f)
        blank = _blank()
        for g in KEYS:
            blank[g].update(data.get(g, {}))
        for k in ("total_seconds", "login_streak", "last_played_date", "achievements", "quest_days", "_last"):
            if k in data:
                blank[k] = data[k]
        return blank
    except (OSError, ValueError, AttributeError):
        return _blank()

def _save(data):
    U.save_json(U.STATS_PATH, data)

def _check_achievements(data):
    earned = data.setdefault("achievements", [])
    new = []
    for slug, name, cond in _ACHIEVEMENTS:
        if slug not in earned:
            try:
                if cond(data):
                    earned.append(slug)
                    new.append(f"★ Achievement unlocked: {name}")
            except Exception:
                pass
    return new

def current_streak(data):
    """Login streak as of today: stale once a full day has been skipped."""
    last = data.get("last_played_date", "")
    if last in (date.today().isoformat(), (date.today() - timedelta(days=1)).isoformat()):
        return data.get("login_streak", 0)
    return 0

def update(game, correct, total, best_streak=0, seconds=0, run=False, sets=None, **extra):
    """Fold one session into the stats file. Scalars in `extra` keep their max, lists/dicts
    are replaced, `sets` overwrites. Returns lines to show (new achievements, finished quests)."""
    if total == 0:
        return []
    data = load()
    from . import quests
    quests.ensure(data)  # snapshot today's baseline before this session counts
    g = data.setdefault(game, {"played": 0, "correct": 0, "best_streak": 0})
    g["played"]      += total
    g["correct"]     += correct
    g["best_streak"]  = max(g["best_streak"], best_streak)
    if run:
        g["runs"] = g.get("runs", 0) + 1
    for k, v in extra.items():
        if isinstance(v, (list, dict)):
            g[k] = v
        else:
            g[k] = max(g.get(k, 0), v)
    g.update(sets or {})
    data["_last"] = {"game": game, "correct": correct, "total": total, "best_streak": best_streak}
    data["total_seconds"] = data.get("total_seconds", 0) + seconds

    today = date.today().isoformat()
    last  = data.get("last_played_date", "")
    if last == today:
        pass
    elif last == (date.today() - timedelta(days=1)).isoformat():
        data["login_streak"] = data.get("login_streak", 0) + 1
    else:
        data["login_streak"] = 1
    data["last_played_date"] = today

    msgs = _check_achievements(data)
    _save(data)

    return quests.notify(msgs)

def add_quest_day():
    """Reward for clearing all three daily quests; returns achievement lines."""
    data = load()
    data["quest_days"] = data.get("quest_days", 0) + 1
    msgs = _check_achievements(data)
    _save(data)
    return msgs

def get_last(data=None):
    return (data or load()).get("_last")

def reset():
    _save(_blank())
    from . import quests
    quests.reset()

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
        for w in reversed(miss[-10:]):  # miss is kept oldest → newest
            print(f"   {U.YELLOW}• {w}{RESET}")
        if len(miss) > 10:
            print(f"\n  {U.GRAY}({len(miss)} total in queue, showing 10 most recent){RESET}")
    U.hr()
    input("\n Enter to go back...")

def _export(data):
    g = lambda key: data.get(key, {})
    cols = ["played", "correct", "best_streak", "runs", "best_score_15", "best_score_30",
            "best_score_60", "best_run", "peak_chips", "mastered_words"]
    try:
        os.makedirs(os.path.dirname(U.EXPORT_PATH), exist_ok=True)
        with open(U.EXPORT_PATH, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["game"] + cols)
            for key in KEYS:
                row = [g(key).get(c, 0) for c in cols[:-1]]
                row.append(len(g(key).get("mastered_words", [])))
                w.writerow([LABELS[key]] + row)
            w.writerow([])
            w.writerow(["login_streak", current_streak(data)])
            w.writerow(["total_seconds", data.get("total_seconds", 0)])
            w.writerow(["achievements", " ".join(_NAMES.get(s, s) for s in data.get("achievements", []))])
        print(f"\n  {U.GREEN}Exported to {U.EXPORT_PATH}{RESET}")
    except OSError as e:
        print(f"\n  {U.RED}Export failed: {e.strerror}{RESET}")
    input("  Enter to continue...")

def _extra(key, g):
    """Last table column: the one game-specific stat worth showing."""
    if key == "rapid_fire":
        best = " · ".join(f"{t}s {g[f'best_score_{t}']}" for t in (15, 30, 60) if g.get(f"best_score_{t}"))
        return f"{g.get('runs', 0)} runs · best {best}" if best else ""
    if key == "roguelike":      return f"{g.get('runs', 0)} runs · best run {g.get('best_run', 0)}"
    if key == "push_your_luck": return f"{g.get('runs', 0)} runs · best banked {g.get('best_run', 0)}"
    if key == "stakes":         return f"{g.get('runs', 0)} runs · peak chips {g.get('peak_chips', 100)}"
    if key == "wordle":
        dist = g.get("guess_dist", {})
        wins = sum(dist.values())
        avg  = sum(int(k) * v for k, v in dist.items()) / wins if wins else 0
        return f"avg {avg:.1f} guesses" if wins else ""
    return ""

def show():
    while True:
        data = load()
        U.clear()
        print(f"\n{BOLD} MY STATS{RESET}")
        U.hr()

        streak    = current_streak(data)
        total_sec = data.get("total_seconds", 0)
        mastered  = len(data.get("translation", {}).get("mastered_words", []))
        streak_str  = f"⚡ {streak}-day streak" if streak else "no streak yet"
        time_str    = _fmt_time(total_sec) if total_sec else "—"
        print(f"  {U.CYAN}{streak_str}{RESET}   {U.GRAY}time: {time_str}   mastered: {mastered} words{RESET}")
        U.hr()

        print(f"  {U.GRAY}{'game':<18}{'played':>7}{'correct':>9}{'streak':>8}   extra{RESET}")
        for key in KEYS:
            g = data.get(key, {})
            played = g.get("played", 0)
            if played == 0:
                print(f"  {LABELS[key]:<18} {U.GRAY}no data{RESET}")
                continue
            correct = g.get("correct", 0)
            pct = int(correct / played * 100)
            col = U.GREEN if pct >= 80 else U.YELLOW if pct >= 60 else U.GRAY
            print(f"  {BOLD}{LABELS[key]:<18}{RESET}{played:>7}{col}{pct:>8}%{RESET}"
                  f"{g.get('best_streak', 0):>8}   {U.GRAY}{_extra(key, g)}{RESET}")
        print(f"  {U.GRAY}(Rapid Fire counts words; Roguelike / Push Your Luck / High Stakes count rounds){RESET}")

        earned = data.get("achievements", [])
        if earned:
            U.hr()
            badges = "   ".join(f"{U.YELLOW}★ {_NAMES.get(s, s)}{RESET}" for s in earned)
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
