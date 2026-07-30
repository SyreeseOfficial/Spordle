from . import utils as U
from . import stats as S
from .utils import SETTINGS, BOLD, RESET

_DIFF_CYCLE    = ["easy", "medium", "hard"]
_THEME_CYCLE   = ["default", "ocean", "sunset", "mono"]
_ROUNDS_CYCLE  = [0, 5, 10, 25]
_DIR_CYCLE     = ["ask", "es_en", "en_es"]
_VERB_CYCLE    = ["all", "irregular", "regular"]
_RFTIME_CYCLE  = [0, 15, 30, 60]
_LIVES_CYCLE   = [1, 2, 3, 5]
_DELAY_CYCLE   = [0.3, 0.5, 0.8, 1.0]
_VOL_CYCLE     = ["low", "medium", "high"]

_ROUNDS_LBL = {0: "Unlimited", 5: "5", 10: "10", 25: "25"}
_DIR_LBL    = {"ask": "Ask each time", "es_en": "ES → EN", "en_es": "EN → ES"}
_VERB_LBL   = {"all": "All verbs", "irregular": "Irregular only", "regular": "Regular only"}
_RF_LBL     = {0: "Ask each time", 15: "15 sec", 30: "30 sec", 60: "60 sec"}
_DELAY_LBL  = {0.3: "0.3s", 0.5: "0.5s", 0.8: "0.8s", 1.0: "1.0s"}

_ALL_GAMES = [
    "Translation","Wordle","Verb Conjugation","Gender Drill","False Friends",
    "Rapid Fire","Hangman","Anagram","Number Drill",
    "Roguelike","Push Your Luck","High Stakes",
]

def _cycle(lst, current):
    return lst[(lst.index(current) + 1) % len(lst)]

def _on(val):
    return f"{U.GREEN}{BOLD}ON{RESET}" if val else f"{U.GRAY}OFF{RESET}"

def _val(v):
    return f"{BOLD}{v}{RESET}"

def _section(label):
    w = U.terminal_width()
    print(f"\n  {U.GRAY}── {label} {'─' * max(0, w - len(label) - 6)}{RESET}")

def _show():
    U.clear()
    d = SETTINGS
    print(f"\n{BOLD} SETTINGS{RESET}")
    U.hr()

    _section("GAMEPLAY")
    print(f"   1. Difficulty       {_val(d['difficulty'].upper())}")
    print(f"      {U.GRAY}easy · medium · hard{RESET}")
    print(f"   2. Round Limit      {_val(_ROUNDS_LBL[d['rounds']])}")
    print(f"      {U.GRAY}5 · 10 · 25 · unlimited{RESET}")
    print(f"   3. Translation Dir  {_val(_DIR_LBL[d['direction']])}")
    print(f"      {U.GRAY}ask · ES→EN · EN→ES{RESET}")
    print(f"   4. Verb Type        {_val(_VERB_LBL[d['verb_type']])}")
    print(f"      {U.GRAY}all · irregular · regular{RESET}")

    _section("DISPLAY")
    print(f"   5. Color Theme      {_val(d['theme'].upper())}")
    print(f"      {U.GRAY}default · ocean · sunset · mono{RESET}")
    print(f"   6. Hints            {_on(d['hints'])}")
    print(f"      {U.GRAY}show first letter before reveal (Translation){RESET}")
    print(f"   7. Word Rank        {_on(d['show_rank'])}")
    print(f"      {U.GRAY}show frequency rank after reveal (Translation){RESET}")

    _section("BEHAVIOUR")
    print(f"   8. Auto-Advance     {_on(d['auto_advance'])}")
    print(f"      {U.GRAY}skip Enter pause after correct answers{RESET}")
    print(f"   9. Advance Delay    {_val(_DELAY_LBL.get(d.get('advance_delay',0.5),'0.5s'))}")
    print(f"      {U.GRAY}0.3s · 0.5s · 0.8s · 1.0s (used when auto-advance is ON){RESET}")
    print(f"  10. Strict Accents   {_on(d['strict_accents'])}")
    print(f"      {U.GRAY}must type exact characters — dieciséis not dieciseis{RESET}")
    print(f"  11. Spaced Rep       {_on(d['srs'])}")
    print(f"      {U.GRAY}revisit recently-missed words in Translation{RESET}")

    _section("MODES")
    print(f"  12. Rapid Fire Time  {_val(_RF_LBL[d['rf_time']])}")
    print(f"      {U.GRAY}15 sec · 30 sec · 60 sec · ask each session{RESET}")
    print(f"  13. Roguelike Lives  {_val(d['rl_lives'])}")
    print(f"      {U.GRAY}1 · 2 · 3 · 5{RESET}")
    print(f"  14. Sounds           {_on(d['sounds'])}")
    print(f"      {U.GRAY}sound effects via aplay (Linux) / afplay (macOS){RESET}")
    print(f"  15. Volume           {_val(d.get('volume','medium').upper())}")
    print(f"      {U.GRAY}low · medium · high{RESET}")

    _section("PERSONALIZATION")
    favs = d.get("favorites", [])
    fav_str = ", ".join(favs) if favs else U.GRAY + "none" + RESET
    print(f"  16. Favorites        {BOLD}{fav_str}{RESET}")
    print(f"      {U.GRAY}games shown at top of menu for quick access{RESET}")

    _section("DATA")
    print(f"  17. Reset Stats      {U.GRAY}wipe all-time records{RESET}")

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
            U.play_navigate()

def play():
    while True:
        _show()
        choice = input("\n > ").strip().lower()
        if choice in ("q", ""):
            U.play_back()
            break

        _TOGGLES = {"8": "auto_advance", "10": "strict_accents", "11": "srs", "14": "sounds"}

        if   choice == "1":  SETTINGS["difficulty"]    = _cycle(_DIFF_CYCLE,   SETTINGS["difficulty"])
        elif choice == "2":  SETTINGS["rounds"]         = _cycle(_ROUNDS_CYCLE, SETTINGS["rounds"])
        elif choice == "3":  SETTINGS["direction"]      = _cycle(_DIR_CYCLE,    SETTINGS["direction"])
        elif choice == "4":  SETTINGS["verb_type"]      = _cycle(_VERB_CYCLE,   SETTINGS["verb_type"])
        elif choice == "5":  U.apply_theme(_cycle(_THEME_CYCLE, SETTINGS["theme"]))
        elif choice == "6":  SETTINGS["hints"]          = not SETTINGS["hints"]
        elif choice == "7":  SETTINGS["show_rank"]      = not SETTINGS["show_rank"]
        elif choice == "8":  SETTINGS["auto_advance"]   = not SETTINGS["auto_advance"]
        elif choice == "9":
            SETTINGS["advance_delay"] = _cycle(_DELAY_CYCLE, SETTINGS.get("advance_delay", 0.5))
        elif choice == "10": SETTINGS["strict_accents"] = not SETTINGS["strict_accents"]
        elif choice == "11": SETTINGS["srs"]            = not SETTINGS["srs"]
        elif choice == "12": SETTINGS["rf_time"]        = _cycle(_RFTIME_CYCLE, SETTINGS["rf_time"])
        elif choice == "13": SETTINGS["rl_lives"]       = _cycle(_LIVES_CYCLE,  SETTINGS["rl_lives"])
        elif choice == "14": SETTINGS["sounds"]         = not SETTINGS["sounds"]
        elif choice == "15": SETTINGS["volume"]         = _cycle(_VOL_CYCLE, SETTINGS.get("volume","medium"))
        elif choice == "16":
            _favorites_menu()
            continue
        elif choice == "17":
            confirm = input(
                f"\n {U.YELLOW}Reset ALL stats? Can't be undone. [y/N] >{RESET} "
            ).strip().lower()
            if confirm == "y":
                S.reset()
                print(f" {U.GREEN}Stats reset.{RESET}")
                input(" Enter to continue...")
        else:
            continue

        if choice in _TOGGLES:
            U.play_toggle(SETTINGS[_TOGGLES[choice]])
        elif choice in ("1","2","3","4","5","9","12","13","15"):
            U.play_navigate()
        elif choice not in ("16", "17"):
            U.play_navigate()
        U.save_settings()
