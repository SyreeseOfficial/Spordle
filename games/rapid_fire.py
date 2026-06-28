import time, random
from . import utils as U
from . import stats as S
from .utils import SETTINGS, POOL, BOLD, RESET

_TIMES = {1: 15, 2: 30, 3: 60}

def _normalize(s):
    s = U.strip_accents(s.lower().strip())
    return s[3:].strip() if s.startswith("to ") else s

def _check(guess, answer):
    # Take first clean chunk — handles "to X", "X, Y", "X; Y", "X (note)"
    ans = answer.lower().split(";")[0].split(",")[0].split("(")[0].strip()
    return _normalize(guess) == _normalize(ans)

def _timer_color(secs):
    if secs <= 5:  return f"{U.YELLOW}{BOLD}"
    if secs <= 15: return U.YELLOW
    return U.GREEN

def play():
    all_words = U.load("words.json")
    pool_size = POOL[SETTINGS["difficulty"]]
    words     = all_words[:pool_size]

    U.clear()
    print(f"\n{BOLD} RAPID FIRE{RESET}")
    U.hr()

    if SETTINGS["rf_time"] > 0:
        limit = SETTINGS["rf_time"]
        print(f" {SETTINGS['rf_time']}s round  {U.GRAY}(change in Settings → Rapid Fire Time){RESET}\n")
    else:
        print(" Answer as many as you can before time runs out.\n")
        print("  1. 15 seconds  — Sprint")
        print("  2. 30 seconds  — Standard")
        print("  3. 60 seconds  — Endurance\n")
        choice = input(" [1/2/3, default 2] > ").strip()
        limit  = _TIMES.get(int(choice) if choice in ("1","2","3") else 2, 30)

    direction = SETTINGS["direction"]
    if direction == "ask":
        print("\n Direction:")
        print("  1. Spanish → English")
        print("  2. English → Spanish")
        d = input("\n [1/2, default 1] > ").strip()
        es_to_en = d != "2"
    else:
        es_to_en = direction == "es_en"

    input(f"\n {BOLD}Ready? Press Enter to start your {limit}-second round...{RESET}")

    correct = total = 0
    start   = time.time()

    while True:
        remaining = limit - (time.time() - start)
        if remaining <= 0:
            break

        word   = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]
        secs   = int(remaining)

        U.clear()
        t_col = _timer_color(secs)
        print(f"\n{BOLD} RAPID FIRE{RESET}   {t_col}{secs}s left{RESET}   {U.GRAY}score {correct}/{total}{RESET}")
        U.hr()

        guess = input(f" {BOLD}{prompt}{RESET}\n > ").strip()

        # Check time after input returns
        over = (time.time() - start) >= limit
        total += 1
        if _check(guess, answer):
            correct += 1
            print(f" {U.GREEN}✓  {answer}{RESET}")
        else:
            print(f" {U.GRAY}✗  {BOLD}{answer}{RESET}")

        if over:
            time.sleep(0.8)
            break

        time.sleep(0.3)

    # Results
    U.clear()
    print(f"\n{BOLD} TIME'S UP!{RESET}")
    U.hr()
    pct       = int(correct / total * 100) if total else 0
    per_min   = int(correct / (limit / 60)) if correct else 0
    filled    = int(20 * correct / total) if total else 0
    bar       = U.GREEN + "█" * filled + U.GRAY + "░" * (20 - filled) + RESET

    print(f"\n  Words:    {BOLD}{total}{RESET}")
    print(f"  Correct:  {BOLD}{correct}/{total}{RESET}  ({pct}%)")
    print(f"  Rate:     {BOLD}{per_min} correct/min{RESET}")
    print(f"\n  {bar}\n")

    if   pct == 100 and total > 3: print(f"  {U.GREEN}{BOLD}Flawless! ¡Increíble!{RESET}\n")
    elif pct >= 80:                print(f"  {U.GREEN}¡Muy bien! Fast and accurate.{RESET}\n")
    elif pct >= 60:                print(f"  {U.YELLOW}Good pace! Keep pushing.{RESET}\n")
    else:                          print(f"  {U.GRAY}Speed comes with practice!{RESET}\n")

    S.update("rapid_fire", correct, total, best_score=correct, best_per_min=per_min)
    input(" Enter to return to menu...")
