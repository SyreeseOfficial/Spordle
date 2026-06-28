import json, os, random
from datetime import date
from . import utils as U
from .utils import BOLD, RESET

_PATH = os.path.expanduser("~/.spordle_quests.json")

_POOL = [
    {"desc": "Get 15 correct in Translation",   "game": "translation",    "key": "correct", "n": 15},
    {"desc": "Get 10 correct in Conjugation",   "game": "conjugation",    "key": "correct", "n": 10},
    {"desc": "Get 10 correct in Number Drill",  "game": "number_drill",   "key": "correct", "n": 10},
    {"desc": "Get 20 correct in Gender Drill",  "game": "gender",         "key": "correct", "n": 20},
    {"desc": "Win 3 Hangman games",             "game": "hangman",        "key": "correct", "n": 3},
    {"desc": "Get 8 correct in Anagram",        "game": "anagram",        "key": "correct", "n": 8},
    {"desc": "Play 20 rounds of Translation",   "game": "translation",    "key": "played",  "n": 20},
    {"desc": "Play 15 rounds of Conjugation",   "game": "conjugation",    "key": "played",  "n": 15},
    {"desc": "Complete a Roguelike run",        "game": "roguelike",      "key": "played",  "n": 1},
    {"desc": "Score in Push Your Luck",         "game": "push_your_luck", "key": "played",  "n": 1},
    {"desc": "Play High Stakes",                "game": "stakes",         "key": "played",  "n": 1},
    {"desc": "Get 5 correct in False Friends",  "game": "false_friends",  "key": "correct", "n": 5},
    {"desc": "Get 10 correct in any Rapid Fire","game": "rapid_fire",     "key": "correct", "n": 10},
]

def _today():
    return str(date.today())

def _load_raw():
    if os.path.exists(_PATH):
        try:
            with open(_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return None

def _save(data):
    with open(_PATH, "w") as f:
        json.dump(data, f, indent=2)

def _gen(stats_now):
    snap = {g: d.copy() for g, d in stats_now.items()}
    chosen = random.sample(_POOL, min(3, len(_POOL)))
    return {"date": _today(), "snapshot": snap, "quests": chosen}

def get():
    """Return list of (desc, progress, target, done) for today's quests."""
    from . import stats as S
    stats_now = S.load()
    raw = _load_raw()
    if not raw or raw.get("date") != _today():
        raw = _gen(stats_now)
        _save(raw)

    snap = raw.get("snapshot", {})
    result = []
    for q in raw["quests"]:
        now_val  = stats_now.get(q["game"], {}).get(q["key"], 0)
        snap_val = snap.get(q["game"], {}).get(q["key"], 0)
        progress = max(0, now_val - snap_val)
        result.append((q["desc"], progress, q["n"], progress >= q["n"]))
    return result

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
