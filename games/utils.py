import functools, json, os, random, shutil, sys, time, unicodedata
from . import sounds

_DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def _xdg(var, default):
    return os.path.join(os.environ.get(var) or os.path.expanduser(default), "spordle")

CONFIG_DIR    = _xdg("XDG_CONFIG_HOME", "~/.config")
DATA_DIR      = _xdg("XDG_DATA_HOME",   "~/.local/share")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
STATS_PATH    = os.path.join(DATA_DIR,   "stats.json")
QUESTS_PATH   = os.path.join(DATA_DIR,   "quests.json")
EXPORT_PATH   = os.path.join(DATA_DIR,   "export.csv")

_OLD_PATHS = (("~/.spordle_settings.json", SETTINGS_PATH),
              ("~/.spordle_stats.json",    STATS_PATH),
              ("~/.spordle_quests.json",   QUESTS_PATH))

BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"

# Theme-mutable — updated by apply_theme(); games access as U.GREEN etc.
GREEN  = "\033[92m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
CYAN   = "\033[96m"
RED    = "\033[91m"

_THEMES = {
    "default": ("\033[92m", "\033[93m", "\033[90m", "\033[96m", "\033[91m"),
    "ocean":   ("\033[94m", "\033[96m", "\033[90m", "\033[95m", "\033[91m"),
    "sunset":  ("\033[91m", "\033[95m", "\033[90m", "\033[93m", "\033[31m"),
    "mono":    ("\033[1m",  "\033[2m",  "\033[2m",  "\033[1m",  "\033[7m"),
}

def apply_theme(name):
    global GREEN, YELLOW, GRAY, CYAN, RED
    GREEN, YELLOW, GRAY, CYAN, RED = _THEMES.get(name, _THEMES["default"])
    SETTINGS["theme"] = name

_warned = False

def save_json(path, obj):
    """Atomic write; a read-only home must not crash the game."""
    global _warned
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(obj, f, indent=2)
        os.replace(tmp, path)
        return True
    except OSError as e:
        if not _warned:
            _warned = True
            print(f" {YELLOW}Could not save to {path}: {e.strerror}{RESET}", file=sys.stderr)
        return False

def save_settings():
    save_json(SETTINGS_PATH, SETTINGS)

SETTINGS = {
    "difficulty":    "medium",
    "theme":         "default",
    "rounds":        0,        # 0 = unlimited
    "direction":     "ask",    # "ask" | "es_en" | "en_es"
    "hints":         False,
    "show_rank":     False,
    "verb_type":     "all",    # "all" | "irregular" | "regular"
    "answer":        "reveal", # "reveal" (self-rate) | "type" (typed + auto-graded)
    "auto_advance":  False,    # skip Enter after correct answers
    "advance_delay": 0.5,      # seconds to wait in auto-advance mode
    "strict_accents":False,    # must type exact accented characters
    "rf_time":       0,        # default Rapid Fire time; 0 = ask each session
    "rl_lives":      3,        # Roguelike starting lives: 1/2/3/5
    "srs":           False,    # spaced repetition in Translation
    "sounds":        False,    # sound effects via aplay
    "volume":        "medium", # sound volume: low / medium / high
    "favorites":     [],       # list of game names marked as favorites
}

# Allowed values for every cycled setting; also used to validate a hand-edited file.
CHOICES = {
    "difficulty":    ["easy", "medium", "hard"],
    "theme":         ["default", "ocean", "sunset", "mono"],
    "rounds":        [0, 5, 10, 25],
    "direction":     ["ask", "es_en", "en_es"],
    "verb_type":     ["all", "irregular", "regular"],
    "answer":        ["reveal", "type"],
    "advance_delay": [0.3, 0.5, 0.8, 1.0],
    "rf_time":       [0, 15, 30, 60],
    "rl_lives":      [1, 2, 3, 5],
    "volume":        ["low", "medium", "high"],
}
_BOOLS = ("hints", "show_rank", "auto_advance", "strict_accents", "srs", "sounds")

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

def five_letter():
    """Wordle / Hangman / Anagram answer list: 5-letter ASCII words, frequency order."""
    return [w for w in load("words.json") if len(w["es"]) == 5 and w["es"].isascii()]

def strip_accents(s):
    # ñ is a letter, not an accent: protect it from NFD
    s = s.replace("ñ", "\0").replace("Ñ", "\1")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s.replace("\0", "ñ").replace("\1", "Ñ")

def match(guess, answer):
    """Compare ignoring accents unless strict_accents is on."""
    g, a = guess.lower().strip(), answer.lower().strip()
    if not g:
        return False
    if SETTINGS.get("strict_accents"):
        return g == a
    return strip_accents(g) == strip_accents(a)

def _norm(s):
    s = s.lower().strip()
    if not SETTINGS.get("strict_accents"):
        s = strip_accents(s)
    return s[3:].strip() if s.startswith("to ") else s

def check_answer(guess, answers):
    """Typed vocab answer: matches any ; , ( / separated chunk of any accepted answer."""
    g = _norm(guess)
    if not g:
        return False
    for a in answers:
        for chunk in a.replace(";", "/").replace(",", "/").replace("(", "/").split("/"):
            if g == _norm(chunk):
                return True
    return False

@functools.lru_cache(maxsize=None)
def _es_by_gloss():
    d = {}
    for w in load("words.json"):
        d.setdefault(w["en"], []).append(w["es"])
    return d

def accepted(word, es_to_en):
    """Every answer that counts: EN→ES accepts any Spanish word sharing the gloss."""
    if es_to_en:
        return [word["en"]]
    return _es_by_gloss().get(word["en"], [word["es"]])

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

def sfx(name, *args):
    """Play a sound effect by name; returns the playback thread (or None)."""
    try:
        return getattr(sounds, name)(*args)
    except Exception:
        return None

def play_back_and_wait():
    t = sfx("back")
    if t:
        t.join(0.5)  # daemon thread: give it a moment before the process exits

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
        time.sleep(SETTINGS.get("advance_delay", 0.5))
    else:
        input("\n Enter to continue...")

def yn_input(prompt):
    """Enter/'y' = True, 'n' = False, 'q' = 'q'. Anything else asks again."""
    while True:
        r = input(prompt).strip().lower()
        if r == "q":
            return "q"
        if r in ("", "y", "yes"):
            return True
        if r in ("n", "no"):
            return False
        print(f" {GRAY}Type y, n, or q.{RESET}")

def ask(prompt, answers, shown=None, flip=False, show_prompt=True, tail=""):
    """One vocab question. 'reveal' mode: Enter, see answer, self-rate. 'type' mode: type it,
    auto-graded. Returns True/False, or 'q' (quit) / 'f' (flip, only if flip=True)."""
    typed = SETTINGS.get("answer") == "type"
    head  = f" {BOLD}{prompt}{RESET}\n" if show_prompt else ""
    raw   = input(f"{head} {'Type the answer' if typed else 'Enter to reveal'} > ").strip()
    low   = raw.lower()
    if low == "q":
        return "q"
    if flip and low == "f":
        return "f"
    print(f"\n   → {BOLD}{shown or answers[0]}{RESET}")
    if tail:
        print(tail)
    if typed:
        ok = check_answer(raw, answers)
        print(f" {GREEN}✓{RESET}" if ok else f" {RED}✗{RESET}")
        return ok
    return yn_input("\n Got it? [Y/n] > ")

def ask_direction(title, blurb=""):
    """Returns es_to_en for the Direction setting, asking if set to 'ask'."""
    direction = SETTINGS["direction"]
    if direction != "ask":
        return direction == "es_en"
    clear()
    print(f"\n{BOLD} {title}{RESET}")
    hr()
    if blurb:
        print(blurb)
    print("  1. Spanish → English  (easier)")
    print("  2. English → Spanish  (harder)")
    return input("\n [1/2, default 1] > ").strip() != "2"

def streak_badge(n):
    return "🔥" if n >= 5 else "⚡" if n >= 3 else ""

def streak_display(n):
    if n >= 10: return f"  {YELLOW}{BOLD}🔥 {n} STREAK — ¡FUEGO!{RESET}"
    if n >= 5:  return f"  {YELLOW}🔥 {n} in a row — ¡Caliente!{RESET}"
    if n >= 3:  return f"  {GREEN}⚡ {n} in a row!{RESET}"
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
    sfx("milestone", n)

def diff_color():
    d = SETTINGS["difficulty"]
    return GREEN if d == "easy" else YELLOW if d == "medium" else RED

def title_line(name, suffix=""):
    """Centered 'NAME  [DIFF]' line; suffix is plain text appended after the tag."""
    diff = SETTINGS["difficulty"].upper()
    pad  = " " * max(0, (terminal_width() - len(f"{name}  [{diff}]{suffix}")) // 2)
    print(f"\n{pad}{BOLD}{name}{RESET}  [{diff_color()}{diff}{RESET}]{suffix}")

def game_header(name, correct=0, total=0, streak=0, best=0, rounds=None):
    w      = terminal_width()
    rounds = SETTINGS["rounds"] if rounds is None else rounds

    title_line(name, f"  {total}/{rounds}" if rounds > 0 else "")

    if rounds > 0:
        bar_w  = min(28, w - 4)
        filled = min(bar_w, int(bar_w * total / rounds)) if total > 0 else 0
        bar    = GREEN + "█" * filled + GRAY + "░" * (bar_w - filled) + RESET
        bpad   = " " * max(0, (w - bar_w - 2) // 2)
        print(f"{bpad}[{bar}]")

    score_str = f"{correct}/{total}" if total else "—/—"
    if   streak >= 10: stk_col = f"{YELLOW}{BOLD}"
    elif streak >= 5:  stk_col = YELLOW
    elif streak >= 3:  stk_col = GREEN
    else:              stk_col = GRAY
    badge    = f" {streak_badge(streak)}" if streak_badge(streak) else ""
    stk_str  = f"{stk_col}streak {streak}{badge}{RESET}"
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

def show_msgs(msgs):
    for m in msgs or ():
        print(f" {YELLOW}{BOLD}{m}{RESET}")

class Session:
    """Counters + feedback shared by every scored game (streaks, banners, sounds, summary)."""

    def __init__(self, name, limit=True):
        self.name   = name
        self.rounds = SETTINGS["rounds"] if limit else 0
        self.correct = self.total = self.streak = self.best = 0
        self.start  = time.time()

    def header(self):
        game_header(self.name, self.correct, self.total, self.streak, self.best, rounds=self.rounds)

    def right(self, text=None, note=""):
        self.total   += 1
        self.correct += 1
        self.streak  += 1
        is_new    = self.streak > self.best
        self.best = max(self.best, self.streak)
        print(f"\n {GREEN}{text or praise()}{RESET}{note}{streak_display(self.streak)}")
        if is_new and self.streak >= 3:
            print(f" {YELLOW}{BOLD}✦ NEW BEST STREAK! ✦{RESET}")
        sfx("correct")
        streak_milestone(self.streak)

    def wrong(self, text=""):
        """text is printed before the consolation line (include its own colors/GRAY)."""
        self.total += 1
        prev, self.streak = self.streak, 0
        print(f"\n {GRAY}{text}{wrong_msg(prev)}{RESET}")
        sfx("wrong")
        return prev

    def advance(self, ok):
        """After feedback: checkpoint, round limit, pause. False when the round limit is hit."""
        checkpoint(self.total)
        if self.rounds > 0 and self.total >= self.rounds:
            print(f"\n {CYAN}{BOLD}Round complete!{RESET}")
            return False
        pause(ok=ok)
        return True

    def end(self, game, footer="", **extra):
        from . import stats as S
        elapsed = int(time.time() - self.start)
        msgs = S.update(game, self.correct, self.total, self.best, seconds=elapsed, **extra)
        summary(self.correct, self.total, self.best, elapsed=elapsed)
        show_msgs(msgs)
        if footer:
            print(footer)
        input(" Enter to return to menu...")

def _valid(key, val):
    if key in CHOICES:
        return not isinstance(val, bool) and val in CHOICES[key]
    if key in _BOOLS:
        return isinstance(val, bool)
    if key == "favorites":
        return isinstance(val, list) and all(isinstance(x, str) for x in val)
    return False

def _load_settings():
    try:
        with open(SETTINGS_PATH) as f:
            saved = json.load(f)
    except (OSError, ValueError):
        return
    if isinstance(saved, dict):
        for k, v in saved.items():
            if k in SETTINGS and _valid(k, v):
                SETTINGS[k] = v
    apply_theme(SETTINGS["theme"])

def init():
    """Move pre-XDG dotfiles into place once, then load saved settings."""
    for old, new in _OLD_PATHS:
        old = os.path.expanduser(old)
        if os.path.exists(old) and not os.path.exists(new):
            try:
                os.makedirs(os.path.dirname(new), exist_ok=True)
                shutil.move(old, new)
            except OSError:
                pass
    _load_settings()
