import random, select, sys, time
from . import utils as U
from . import stats as S
from .utils import SETTINGS, POOL, BOLD, RESET

_TIMES = {1: 15, 2: 30, 3: 60}

def _timer_color(secs):
    if secs <= 5:  return f"{U.YELLOW}{BOLD}"
    if secs <= 15: return U.YELLOW
    return U.GREEN

def _timed_input(prompt, remaining):
    """input() that gives up when the round ends; None on timeout."""
    print(prompt, end="", flush=True)
    if not select.select([sys.stdin], [], [], remaining)[0]:
        print()
        return None
    line = sys.stdin.readline()
    if line == "":
        raise EOFError
    return line.rstrip("\n")

def _flush_stdin():
    try:
        import termios
        termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)  # drop half-typed text
    except Exception:
        pass

def play():
    words = U.load("words.json")[:POOL[SETTINGS["difficulty"]]]
    words = [w for w in words if not w.get("cognate")] or words  # identical cognates are free points

    U.clear()
    print(f"\n{BOLD} RAPID FIRE{RESET}")
    U.hr()

    if SETTINGS["rf_time"] > 0:
        limit = SETTINGS["rf_time"]
        print(f" {limit}s round  {U.GRAY}(change in Settings → Rapid Fire Time){RESET}\n")
    else:
        print(" Answer as many as you can before time runs out.\n")
        print("  1. 15 seconds  — Sprint")
        print("  2. 30 seconds  — Standard")
        print("  3. 60 seconds  — Endurance\n")
        choice = input(" [1/2/3, default 2] > ").strip()
        limit  = _TIMES.get(int(choice) if choice in ("1","2","3") else 2, 30)

    es_to_en = U.ask_direction("RAPID FIRE")

    input(f"\n {BOLD}Ready? Press Enter to start your {limit}-second round...{RESET}")

    correct = total = streak = best_streak = 0
    quit_early = False
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

        guess = _timed_input(f" {BOLD}{prompt}{RESET}  {U.GRAY}(Enter = skip, q = stop){RESET}\n > ", remaining)
        if guess is None:
            print(f" {U.GRAY}Time!{RESET}")
            time.sleep(0.8)
            break
        guess = guess.strip()
        if guess.lower() == "q":
            quit_early = True
            break
        if not guess:   # skip: not counted as wrong
            continue

        total += 1
        if U.check_answer(guess, U.accepted(word, es_to_en)):
            correct += 1
            streak  += 1
            best_streak = max(best_streak, streak)
            print(f" {U.GREEN}✓  {answer}{RESET}")
        else:
            streak = 0
            print(f" {U.GRAY}✗  {BOLD}{answer}{RESET}")

        time.sleep(0.3)

    _flush_stdin()

    # Results
    U.clear()
    print(f"\n{BOLD} {'ROUND STOPPED' if quit_early else 'TIME' + chr(39) + 'S UP!'}{RESET}")
    U.hr()
    pct       = int(correct / total * 100) if total else 0
    per_min   = int(correct / ((time.time() - start if quit_early else limit) / 60)) if correct else 0
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

    # best score is per time limit (a 60s run always beats a 15s one); stopped rounds don't set records
    best = {} if quit_early else {f"best_score_{limit}": correct}
    U.show_msgs(S.update("rapid_fire", correct, total, best_streak, seconds=int(time.time() - start),
                         run=True, **best))
    input(" Enter to return to menu...")
