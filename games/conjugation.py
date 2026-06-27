import random
from .utils import (load, SETTINGS, TENSES, GREEN, GRAY, BOLD, RESET,
                    strip_accents, clear, hr, game_header, praise, console, streak_display, summary)

_LABELS = {
    "Indicativo/Presente":   "Present",
    "Indicativo/Pretérito":  "Preterite",
    "Indicativo/Imperfecto": "Imperfect",
    "Indicativo/Futuro":     "Future",
    "Subjuntivo/Presente":   "Present Subjunctive",
}

_PERSONS = ["yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas"]

def play():
    verbs    = load("verbs.json")
    inf_list = list(verbs.keys())

    correct = total = streak = best_streak = 0

    while True:
        allowed_tenses = TENSES[SETTINGS["difficulty"]]
        inf    = random.choice(inf_list)
        data   = verbs[inf]
        valid  = [t for t in data["tenses"] if t in allowed_tenses]
        if not valid:
            continue
        tense_key = random.choice(valid)
        person    = random.choice(_PERSONS)
        answer    = data["tenses"][tense_key][person]
        label     = _LABELS.get(tense_key, tense_key)

        clear()
        game_header("VERB CONJUGATION", correct, total, streak)
        print(f" {BOLD}{inf}{RESET}  ({data['en']})")
        print(f" Tense:  {BOLD}{label}{RESET}")
        print(f" Person: {BOLD}{person}{RESET}\n")

        guess = input(" [q = menu] > ").strip().lower()
        if guess == "q":
            break

        total += 1
        if strip_accents(guess) == strip_accents(answer.lower()):
            correct += 1
            streak += 1
            best_streak = max(best_streak, streak)
            note = f"  {GRAY}(full: {answer}){RESET}" if guess != answer.lower() else ""
            print(f"\n {GREEN}{praise()}{RESET}{note}{streak_display(streak)}")
        else:
            streak = 0
            print(f"\n {GRAY}Answer: {BOLD}{answer}{RESET}  {GRAY}{console()}{RESET}")

        input("\n Enter to continue...")

    summary(correct, total, best_streak)
    input(" Enter to return to menu...")
