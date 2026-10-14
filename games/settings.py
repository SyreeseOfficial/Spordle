from . import utils as U
from . import stats as S
from .registry import LABELS
from .utils import SETTINGS, CHOICES, BOLD, RESET

_ALL_GAMES = list(LABELS.values())

_FMT = {
    "rounds":        lambda v: "∞" if v == 0 else str(v),
    "direction":     lambda v: {"ask": "ask", "es_en": "ES→EN", "en_es": "EN→ES"}[v],
    "rf_time":       lambda v: "ask" if v == 0 else f"{v}s",
    "advance_delay": lambda v: f"{v}s",
}

# (section, key, label, hint) — numbered in order on screen; key None = special row
_ROWS = [
    ("GAMEPLAY",  "difficulty",     "Difficulty",     ""),
    ("",          "rounds",         "Round Limit",    "drills only (not Wordle, Hangman, Rapid Fire, gambling)"),
    ("",          "direction",      "Direction",      "vocab games (Translation, Rapid Fire, gambling)"),
    ("",          "verb_type",      "Verb Type",      "irregular yo or él preterite"),
    ("",          "answer",         "Answer Mode",    "reveal = self-rate, type = auto-graded"),
    ("DISPLAY",   "theme",          "Color Theme",    ""),
    ("",          "hints",          "Hints",          "first letter before reveal (Translation)"),
    ("",          "show_rank",      "Word Rank",      "frequency rank after reveal (Translation)"),
    ("BEHAVIOUR", "auto_advance",   "Auto-Advance",   "skip Enter after correct answers"),
    ("",          "advance_delay",  "Advance Delay",  "used when auto-advance is on"),
    ("",          "strict_accents", "Strict Accents", "must type é, not e (ñ always required)"),
    ("",          "srs",            "Spaced Rep",     "revisit missed words in Translation"),
    ("MODES",     "rf_time",        "Rapid Fire Time",""),
    ("",          "rl_lives",       "Roguelike Lives",""),
    ("",          "sounds",         "Sounds",         "aplay (Linux) / afplay (macOS)"),
    ("",          "volume",         "Volume",         ""),
    ("MORE",      "favorites",      "Favorites",      ""),
    ("",          "reset",          "Reset Stats",    "wipe all-time records and quests"),
]

def _on(val):
    return f"{U.GREEN}{BOLD}ON{RESET}" if val else f"{U.GRAY}OFF{RESET}"

def _opts(key):
    fmt = _FMT.get(key, str)
    return " · ".join(f"{BOLD}[{fmt(v)}]{RESET}" if v == SETTINGS[key] else fmt(v) for v in CHOICES[key])

def _value(key):
    if key in CHOICES:
        return _opts(key)
    if key == "favorites":
        favs = SETTINGS.get("favorites", [])
        return ", ".join(favs) if favs else f"{U.GRAY}none{RESET}"
    if key == "reset":
        return ""
    return _on(SETTINGS[key])

def _show():
    U.clear()
    print(f"\n{BOLD} SETTINGS{RESET}")
    U.hr()
    for i, (section, key, label, hint) in enumerate(_ROWS, 1):
        if section:
            print(f"  {U.GRAY}── {section}{RESET}")
        tip = f"  {U.GRAY}{hint}{RESET}" if hint else ""
        print(f"  {i:>2}. {label:<16} {_value(key)}{tip}")
    U.hr()
    print(f"  {U.GRAY}Enter a number to change, q to go back{RESET}")

def _favorites_menu():
    while True:
        U.clear()
        print(f"\n{BOLD} FAVORITES{RESET}")
        U.hr()
        favs = set(SETTINGS.get("favorites", []))
        for i, name in enumerate(_ALL_GAMES, 1):
            star = f"{U.YELLOW}★{RESET}" if name in favs else " "
            print(f"  {star} {i:>2}. {name}")
        U.hr()
        print(f"  {U.GRAY}Type a number to toggle · q to go back{RESET}")
        print(f"  {U.GRAY}Max 3 favorites{RESET}")
        c = input("\n > ").strip().lower()
        if c in ("q", ""):
            break
        if c.isdigit() and 1 <= int(c) <= len(_ALL_GAMES):
            name = _ALL_GAMES[int(c) - 1]
            if name in favs:
                favs.discard(name)
            elif len(favs) < 3:
                favs.add(name)
            else:
                print(f"  {U.YELLOW}Already 3 favorites — remove one first{RESET}")
                input("  Enter to continue...")
                continue
            SETTINGS["favorites"] = [g for g in _ALL_GAMES if g in favs]  # preserve order
            U.save_settings()
            U.sfx("navigate")

def play():
    while True:
        _show()
        choice = input("\n > ").strip().lower()
        if choice in ("q", ""):
            U.sfx("back")
            break
        if not (choice.isdigit() and 1 <= int(choice) <= len(_ROWS)):
            continue
        key = _ROWS[int(choice) - 1][1]

        if key == "favorites":
            _favorites_menu()
            continue
        if key == "reset":
            confirm = input(
                f"\n {U.YELLOW}Reset ALL stats? Can't be undone. [y/N] >{RESET} "
            ).strip().lower()
            if confirm == "y":
                S.reset()
                print(f" {U.GREEN}Stats reset.{RESET}")
                input(" Enter to continue...")
            continue

        if key in CHOICES:
            lst = CHOICES[key]
            new = lst[(lst.index(SETTINGS[key]) + 1) % len(lst)]
            if key == "theme":
                U.apply_theme(new)
            else:
                SETTINGS[key] = new
            U.sfx("navigate")
        else:
            SETTINGS[key] = not SETTINGS[key]
            U.sfx("toggle_on" if SETTINGS[key] else "toggle_off")
        U.save_settings()
