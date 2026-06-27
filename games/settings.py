from .utils import SETTINGS, BOLD, GREEN, GRAY, CYAN, RESET, clear, hr

_LEVELS = {
    "easy":   "Common words only · present tense only",
    "medium": "Broader vocab · present, preterite, imperfect",
    "hard":   "Full word pool · all 5 tenses",
}

def play():
    clear()
    print(f"\n{BOLD} SETTINGS{RESET}")
    hr()

    current = SETTINGS["difficulty"]
    print(f" Difficulty: {CYAN}{BOLD}{current.upper()}{RESET}\n")
    for i, (lvl, desc) in enumerate(_LEVELS.items(), 1):
        marker = f"{GREEN}>{RESET}" if lvl == current else " "
        print(f" {marker} {i}. {BOLD}{lvl.capitalize():<8}{RESET}  {GRAY}{desc}{RESET}")

    choice = input("\n [1/2/3, or Enter to keep] > ").strip()
    keys = list(_LEVELS)
    if choice in ("1", "2", "3"):
        SETTINGS["difficulty"] = keys[int(choice) - 1]

    print(f"\n {GREEN}Difficulty set to: {BOLD}{SETTINGS['difficulty'].upper()}{RESET}\n")
