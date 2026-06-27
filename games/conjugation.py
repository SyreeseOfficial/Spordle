import random, time
from . import utils as U
from .utils import SETTINGS, TENSES, BOLD, RESET

_LABELS = {
    "Indicativo/Presente":   "Present",
    "Indicativo/Pretérito":  "Preterite",
    "Indicativo/Imperfecto": "Imperfect",
    "Indicativo/Futuro":     "Future",
    "Subjuntivo/Presente":   "Present Subjunctive",
}
_PERSONS = ["yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas"]

def _show_paradigm(tense_data, correct_person):
    print(f"\n  {U.GRAY}Full paradigm:{RESET}")
    for person, form in tense_data.items():
        marker = f"{U.GREEN}>{RESET}" if person == correct_person else " "
        print(f"  {marker} {person:<14} {BOLD}{form}{RESET}")

def play():
    verbs    = U.load("verbs.json")
    inf_list = list(verbs.keys())
    correct  = total = streak = best_streak = 0
    rounds   = SETTINGS["rounds"]
    start    = time.time()

    while True:
        allowed   = TENSES[SETTINGS["difficulty"]]
        inf       = random.choice(inf_list)
        data      = verbs[inf]
        valid     = [t for t in data["tenses"] if t in allowed]
        if not valid:
            continue
        tense_key = random.choice(valid)
        person    = random.choice(_PERSONS)
        answer    = data["tenses"][tense_key][person]
        label     = _LABELS.get(tense_key, tense_key)

        U.clear()
        U.game_header("VERB CONJUGATION", correct, total, streak, best=best_streak)
        print(f" {BOLD}{inf}{RESET}  ({data['en']})")
        print(f" Tense:  {BOLD}{label}{RESET}")
        print(f" Person: {BOLD}{person}{RESET}\n")

        guess = input(" [q = menu] > ").strip().lower()
        if guess == "q":
            break

        total += 1
        if U.strip_accents(guess) == U.strip_accents(answer.lower()):
            correct  += 1
            streak   += 1
            is_new    = streak > best_streak
            best_streak = max(best_streak, streak)
            note = f"  {U.GRAY}(full: {answer}){RESET}" if guess != answer.lower() else ""
            print(f"\n {U.GREEN}{U.praise()}{RESET}{note}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
        else:
            streak = 0
            print(f"\n {U.GRAY}Answer: {BOLD}{answer}{RESET}  {U.GRAY}{U.console()}{RESET}")
            _show_paradigm(data["tenses"][tense_key], person)

        if rounds > 0 and total >= rounds:
            print(f"\n {U.CYAN}{BOLD}Round complete!{RESET}")
            break

        input("\n Enter to continue...")

    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
