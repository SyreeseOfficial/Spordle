import random, time
from . import utils as U
from . import stats as S
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

def _is_irregular(inf, data):
    yo = data["tenses"].get("Indicativo/Presente", {}).get("yo", "")
    if not yo or not inf.endswith(("ar", "er", "ir")):
        return False
    return yo != inf[:-2] + "o"

def play():
    verbs    = U.load("verbs.json")
    inf_list = list(verbs.keys())

    verb_type = SETTINGS["verb_type"]
    if verb_type != "all":
        want_irreg = (verb_type == "irregular")
        inf_list = [inf for inf in inf_list if _is_irregular(inf, verbs[inf]) == want_irreg]
    if not inf_list:
        print(f"\n {U.GRAY}No verbs match current filter ({verb_type}). Change it in Settings.{RESET}")
        input(" Enter to return to menu...")
        return

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
        vt_tag = f"  {U.GRAY}[{verb_type}]{RESET}" if verb_type != "all" else ""
        print(f" {BOLD}{inf}{RESET}  ({data['en']}){vt_tag}")
        print(f" Tense:  {BOLD}{label}{RESET}")
        print(f" Person: {BOLD}{person}{RESET}\n")

        guess = input(" [q = menu] > ").strip()
        if guess.lower() == "q":
            break

        total += 1
        was_correct = U.match(guess, answer)
        if was_correct:
            correct  += 1
            streak   += 1
            is_new    = streak > best_streak
            best_streak = max(best_streak, streak)
            exact_note = f"  {U.GRAY}(full: {answer}){RESET}" if guess.lower() != answer.lower() else ""
            print(f"\n {U.GREEN}{U.praise()}{RESET}{exact_note}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
            U.play_correct()
            U.streak_milestone(streak)
        else:
            prev_streak = streak
            streak = 0
            print(f"\n {U.GRAY}Answer: {BOLD}{answer}{RESET}  {U.GRAY}{U.wrong_msg(prev_streak)}{RESET}")
            _show_paradigm(data["tenses"][tense_key], person)
            U.play_wrong()

        U.checkpoint(total)

        if rounds > 0 and total >= rounds:
            print(f"\n {U.CYAN}{BOLD}Round complete!{RESET}")
            break

        U.pause(ok=was_correct)

    S.update("conjugation", correct, total, best_streak)
    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
