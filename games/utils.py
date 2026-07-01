import json, os, random, time, unicodedata

_DATA          = os.path.join(os.path.dirname(__file__), "..", "data")
_SETTINGS_PATH = os.path.expanduser("~/.spordle_settings.json")

BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"

# Theme-mutable — updated by apply_theme(); games access as U.GREEN etc.
GREEN  = "\033[92m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
CYAN   = "\033[96m"

_THEMES = {
    "default": ("\033[92m", "\033[93m", "\033[90m", "\033[96m"),
    "ocean":   ("\033[94m", "\033[96m", "\033[90m", "\033[95m"),
    "sunset":  ("\033[91m", "\033[95m", "\033[90m", "\033[93m"),
    "mono":    ("\033[1m",  "\033[2m",  "\033[2m",  "\033[1m"),
}

def apply_theme(name):
    global GREEN, YELLOW, GRAY, CYAN
    GREEN, YELLOW, GRAY, CYAN = _THEMES.get(name, _THEMES["default"])
    SETTINGS["theme"] = name

def save_settings():
    with open(_SETTINGS_PATH, "w") as f:
        json.dump(SETTINGS, f, indent=2)

SETTINGS = {
    "difficulty":    "medium",
    "theme":         "default",
    "rounds":        0,        # 0 = unlimited
    "direction":     "ask",    # "ask" | "es_en" | "en_es"
    "hints":         False,
    "show_rank":     False,
    "verb_type":     "all",    # "all" | "irregular" | "regular"
    "auto_advance":  False,    # skip Enter after correct answers
    "strict_accents":False,    # must type exact accented characters
    "rf_time":       0,        # default Rapid Fire time; 0 = ask each session
    "rl_lives":      3,        # Roguelike starting lives: 1/2/3/5
    "srs":           False,    # spaced repetition in Translation
    "sounds":        False,    # sound effects via aplay
}

POOL    = {"easy": 500,  "medium": 2000, "hard": 5000}
POOL_5L = {"easy": 150,  "medium": 350,  "hard": 584}
TENSES  = {
    "easy":   ["Indicativo/Presente"],
    "medium": ["Indicativo/Presente", "Indicativo/Pretérito", "Indicativo/Imperfecto"],
    "hard":   ["Indicativo/Presente", "Indicativo/Pretérito", "Indicativo/Imperfecto",
               "Indicativo/Futuro", "Subjuntivo/Presente"],
}

_PRAISE  = ["¡Excelente!", "¡Muy bien!", "¡Perfecto!", "¡Brillante!",
            "¡Correcto!", "¡Increíble!", "¡Fantástico!"]
_CONSOLE = ["¡Ánimo!", "Keep going!", "Almost there!", "You'll get it!",
            "¡No te rindas!", "Practice makes perfect!"]

_WRONG_STREAK = [
    "¡Ay no! {n} streak gone.", "Nooo — {n} in a row lost!",
    "¡Ánimo! You had {n}.",    "That stings. {n} was great though.",
]
_WRONG_CLOSE = [
    "So close — {n} in a row gone.", "¡Casi! {n} streak ended.",
]

_CHECKPOINTS = {
    10: "10 rounds — ¡En racha!",
    25: "25 rounds — ¡Caliente!",
    50: "50 rounds — Dedication!",
   100: "100 rounds — ¡Leyenda!",
}

def load(filename):
    with open(os.path.join(_DATA, filename)) as f:
        return json.load(f)

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")

def match(guess, answer):
    """Compare ignoring accents unless strict_accents is on."""
    g, a = guess.lower().strip(), answer.lower().strip()
    if SETTINGS.get("strict_accents"):
        return g == a
    return strip_accents(g) == strip_accents(a)

def praise():  return random.choice(_PRAISE)
def console(): return random.choice(_CONSOLE)

def wrong_msg(prev_streak=0):
    if prev_streak >= 5:
        return random.choice(_WRONG_STREAK).format(n=prev_streak)
    if prev_streak >= 3:
        return random.choice(_WRONG_CLOSE).format(n=prev_streak)
    return console()

def checkpoint(total):
    msg = _CHECKPOINTS.get(total)
    if msg:
        w   = terminal_width()
        pad = " " * max(0, (w - len(msg) - 6) // 2)
        print(f"\n{pad}{CYAN}✦ {msg} ✦{RESET}")

def play_correct():
    try:
        from . import sounds as _S
        _S.correct()
    except Exception:
        pass

def play_wrong():
    try:
        from . import sounds as _S
        _S.wrong()
    except Exception:
        pass

def play_navigate():
    try:
        from . import sounds as _S
        _S.navigate()
    except Exception:
        pass

def play_back():
    try:
        from . import sounds as _S
        _S.back()
    except Exception:
        pass

def play_toggle(on):
    try:
        from . import sounds as _S
        (_S.toggle_on if on else _S.toggle_off)()
    except Exception:
        pass

def play_game_over():
    try:
        from . import sounds as _S
        _S.game_over()
    except Exception:
        pass

def terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 72

def clear():
    print("\033[2J\033[H", end="")

def hr():
    print(GRAY + "─" * terminal_width() + RESET)

def banner():
    clear()
    inner = 36
    w     = terminal_width()
    pad   = " " * max(0, (w - inner - 2) // 2)
    top   = "╔" + "═" * inner + "╗"
    bot   = "╚" + "═" * inner + "╝"
    blank = "║" + " " * inner + "║"
    print(f"\n{pad}{CYAN}{top}{RESET}")
    print(f"{pad}{CYAN}{blank}{RESET}")
    print(f"{pad}{CYAN}║{BOLD}{'S  P  O  R  D  L  E'.center(inner)}{RESET}{CYAN}║{RESET}")
    print(f"{pad}{CYAN}{blank}{RESET}")
    print(f"{pad}{GRAY}║{'Spanish Practice CLI'.center(inner)}║{RESET}")
    print(f"{pad}{CYAN}{blank}{RESET}")
    print(f"{pad}{CYAN}{bot}{RESET}")
    hour = time.localtime().tm_hour
    if   5 <= hour < 12: greeting = "¡Buenos días!"
    elif 12 <= hour < 20: greeting = "¡Buenas tardes!"
    else:                 greeting = "¡Buenas noches!"
    gpad = " " * max(0, (w - len(greeting)) // 2)
    print(f"\n{gpad}{YELLOW}{greeting}{RESET}\n")
    input(f"{pad}  {GRAY}Press Enter to play...{RESET} ")

def pause(ok=False):
    """Auto-advance skips Enter after correct; always waits after wrong."""
    if SETTINGS.get("auto_advance") and ok:
        time.sleep(0.5)
    else:
        input("\n Enter to continue...")

def yn_input(prompt):
    """Enter or 'y' = True, 'n' = False, 'q' = 'q'."""
    r = input(prompt).strip().lower()
    if r == "q":
        return "q"
    return r != "n"

def streak_display(n):
    if n >= 10: return f"  {YELLOW}{BOLD}*** {n} STREAK — ¡FUEGO! ***{RESET}"
    if n >= 5:  return f"  {YELLOW}** {n} in a row — ¡Caliente!{RESET}"
    if n >= 3:  return f"  {GREEN}* {n} in a row!{RESET}"
    return ""

def streak_milestone(n):
    """Print a celebration box at streak 5, 10, 25."""
    _msgs = {
        5:  (f"  5 STREAK — ¡Caliente!  ", YELLOW),
        10: (f"  10 STREAK — ¡FUEGO!    ", f"{YELLOW}{BOLD}"),
        25: (f"  25 STREAK — LEGENDARIO  ", f"{YELLOW}{BOLD}"),
    }
    if n not in _msgs:
        return
    msg, col = _msgs[n]
    w   = terminal_width()
    pad = " " * max(0, (w - len(msg) - 2) // 2)
    print(f"\n{pad}{col}┌{'─' * len(msg)}┐{RESET}")
    print(f"{pad}{col}│{msg}│{RESET}")
    print(f"{pad}{col}└{'─' * len(msg)}┘{RESET}")
    try:
        from . import sounds as _S
        _S.milestone(n)
    except Exception:
        pass

def _diff_color():
    d = SETTINGS["difficulty"]
    return GREEN if d == "easy" else YELLOW if d == "medium" else "\033[91m"

def game_header(name, correct=0, total=0, streak=0, best=0):
    diff     = SETTINGS["difficulty"].upper()
    rounds   = SETTINGS["rounds"]
    w        = terminal_width()
    diff_col = _diff_color()

    rnd_str  = f"  {total}/{rounds}" if rounds > 0 else ""
    visible  = f"{name}  [{diff}]{rnd_str}"
    pad      = " " * max(0, (w - len(visible)) // 2)
    print(f"\n{pad}{BOLD}{name}{RESET}  [{diff_col}{diff}{RESET}]{rnd_str}")

    if rounds > 0:
        bar_w  = min(28, w - 4)
        filled = int(bar_w * total / rounds) if total > 0 else 0
        bar    = GREEN + "█" * filled + GRAY + "░" * (bar_w - filled) + RESET
        bpad   = " " * max(0, (w - bar_w - 2) // 2)
        print(f"{bpad}[{bar}]")

    score_str = f"{correct}/{total}" if total else "—/—"
    if   streak >= 10: stk_col, dots = f"{YELLOW}{BOLD}", " ***"
    elif streak >= 5:  stk_col, dots = YELLOW,             " **"
    elif streak >= 3:  stk_col, dots = GREEN,              " *"
    else:              stk_col, dots = GRAY,               ""
    stk_str  = f"{stk_col}streak {streak}{dots}{RESET}"
    best_str = f"   {GRAY}best {best}{RESET}" if best > 0 else ""

    print(f"\n {GRAY}score {score_str}{RESET}   {stk_str}{best_str}")
    print(f" {GRAY}q = menu{RESET}")
    if best > 0 and 0 < streak < best:
        gap = best - streak
        if gap <= 2:
            print(f" {YELLOW}{'One more' if gap == 1 else f'{gap} away'} from your best!{RESET}")
    hr()

def summary(correct, total, best_streak, elapsed=0):
    hr()
    if not total:
        print(f"\n  {GRAY}No rounds played.{RESET}\n")
        return

    pct = int(correct / total * 100)
    w   = terminal_width()

    if   pct == 100: grade, col = "¡Perfecto! Flawless session!", GREEN
    elif pct >= 80:  grade, col = "¡Muy bien! Strong work.",      GREEN
    elif pct >= 60:  grade, col = "Good effort — keep it up!",    YELLOW
    else:            grade, col = "¡Ánimo! It gets easier.",      GRAY

    bar_w  = min(36, w - 6)
    filled = int(bar_w * correct / total)
    bar    = col + "█" * filled + GRAY + "░" * (bar_w - filled) + RESET

    time_str   = ""
    if elapsed > 0:
        m, s = divmod(elapsed, 60)
        time_str = f"   {GRAY}{m}:{s:02d}{RESET}"

    streak_str = f"   {GRAY}best streak {BOLD}{best_streak}{RESET}" if best_streak else ""

    print(f"\n  {BOLD}SESSION SUMMARY{RESET}")
    hr()
    print(f"\n  {col}{BOLD}{pct}%{RESET}   {BOLD}{correct} / {total}{RESET}{time_str}{streak_str}")
    print(f"\n  {bar}\n")
    print(f"  {col}{BOLD}{grade}{RESET}\n")

def _load_settings():
    if not os.path.exists(_SETTINGS_PATH):
        return
    try:
        with open(_SETTINGS_PATH) as f:
            saved = json.load(f)
        for k in SETTINGS:
            if k in saved:
                SETTINGS[k] = saved[k]
        apply_theme(SETTINGS["theme"])
    except Exception:
        pass

_load_settings()
