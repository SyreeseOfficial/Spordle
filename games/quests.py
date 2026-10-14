import json, os, random
from datetime import date
from . import utils as U
from .utils import BOLD, RESET

# Three quests a day, never two for the same game; "runs" quests count whole sessions.
_POOL = [
    {"desc": "Get 15 correct in Translation",    "game": "translation",    "key": "correct", "n": 15},
    {"desc": "Play 20 rounds of Translation",    "game": "translation",    "key": "played",  "n": 20},
    {"desc": "Get 10 correct in Conjugation",    "game": "conjugation",    "key": "correct", "n": 10},
    {"desc": "Play 15 rounds of Conjugation",    "game": "conjugation",    "key": "played",  "n": 15},
    {"desc": "Get 10 correct in Number Drill",   "game": "number_drill",   "key": "correct", "n": 10},
    {"desc": "Get 20 correct in Gender Drill",   "game": "gender",         "key": "correct", "n": 20},
    {"desc": "Win 3 Hangman games",              "game": "hangman",        "key": "correct", "n": 3},
    {"desc": "Play 5 Hangman games",             "game": "hangman",        "key": "played",  "n": 5},
    {"desc": "Get 8 correct in Anagram",         "game": "anagram",        "key": "correct", "n": 8},
    {"desc": "Get 5 correct in False Friends",   "game": "false_friends",  "key": "correct", "n": 5},
    {"desc": "Get 10 correct in Rapid Fire",     "game": "rapid_fire",     "key": "correct", "n": 10},
    {"desc": "Play 2 Wordle games",              "game": "wordle",         "key": "played",  "n": 2},
    {"desc": "Complete 2 Roguelike runs",        "game": "roguelike",      "key": "runs",    "n": 2},
    {"desc": "Finish 2 Push Your Luck runs",     "game": "push_your_luck", "key": "runs",    "n": 2},
    {"desc": "Play 2 High Stakes runs",          "game": "stakes",         "key": "runs",    "n": 2},
]
_KEYS = ("played", "correct", "runs")

def _today():
    return str(date.today())

def _load_raw():
    try:
        with open(U.QUESTS_PATH) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None

def _gen(stats_now):
    snap = {g: {k: d.get(k, 0) for k in _KEYS} for g, d in stats_now.items() if isinstance(d, dict)}
    pool, chosen = _POOL[:], []
    while pool and len(chosen) < 3:
        q = random.choice(pool)
        chosen.append(q)
        pool = [p for p in pool if p["game"] != q["game"]]
    return {"date": _today(), "snapshot": snap, "quests": chosen, "notified": [], "rewarded": False}

def _today_raw(stats_now):
    raw = _load_raw()
    if not raw or raw.get("date") != _today():
        raw = _gen(stats_now)
        U.save_json(U.QUESTS_PATH, raw)
    return raw

def ensure(stats_now):
    _today_raw(stats_now)

def get(stats_now=None):
    """Return list of (desc, progress, target, done) for today's quests."""
    if stats_now is None:
        from . import stats as S
        stats_now = S.load()
    raw  = _today_raw(stats_now)
    snap = raw.get("snapshot", {})
    result = []
    for q in raw["quests"]:
        now_val  = stats_now.get(q["game"], {}).get(q["key"], 0)
        snap_val = snap.get(q["game"], {}).get(q["key"], 0)
        progress = max(0, now_val - snap_val)
        result.append((q["desc"], progress, q["n"], progress >= q["n"]))
    return result

def notify(msgs):
    """After a stats update: append a line for each newly finished quest (and the daily reward)."""
    from . import stats as S
    msgs = list(msgs)
    raw  = _today_raw(S.load())
    done = [i for i, (*_, d) in enumerate(get()) if d]
    for i in done:
        if i not in raw["notified"]:
            raw["notified"].append(i)
            msgs.append(f"⚡ Quest complete: {raw['quests'][i]['desc']}")
    if len(done) == 3 and not raw.get("rewarded"):
        raw["rewarded"] = True
        msgs.append("⚡ All 3 daily quests done!")
        msgs += S.add_quest_day()
    U.save_json(U.QUESTS_PATH, raw)
    return msgs

def reset():
    try:
        os.remove(U.QUESTS_PATH)
    except OSError:
        pass

def show():
    quests = get()
    U.clear()
    print(f"\n{BOLD} DAILY QUESTS{RESET}  {U.GRAY}(reset at midnight){RESET}")
    U.hr()
    for desc, prog, target, done in quests:
        bar_n  = int(20 * min(prog, target) / target)
        bar    = U.GREEN + "█" * bar_n + U.GRAY + "░" * (20 - bar_n) + RESET
        status = f"{U.GREEN}{BOLD}DONE!{RESET}" if done else f"{U.GRAY}{prog}/{target}{RESET}"
        print(f"\n  {BOLD}{desc}{RESET}")
        print(f"  [{bar}]  {status}")
    completed = sum(1 for *_, d in quests if d)
    print(f"\n  {U.CYAN}{completed}/3 quests completed today{RESET}")
    if completed == 3:
        print(f"  {U.YELLOW}{BOLD}ALL DONE — ¡Increíble!{RESET}")
    U.hr()
    input("\n Enter to return to menu...")
