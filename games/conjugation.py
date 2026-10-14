import random
from . import utils as U
from .utils import SETTINGS, TENSES, POOL, BOLD, RESET

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
    """Irregular present yo or irregular él preterite (reflexive pronouns ignored)."""
    base = inf[:-2] if inf.endswith("se") else inf
    if not base.endswith(("ar", "er", "ir")):
        return False
    stem = base[:-2]
    t    = data["tenses"]
    yo   = t.get("Indicativo/Presente", {}).get("yo", "").split(" ")[-1]
    el   = t.get("Indicativo/Pretérito", {}).get("él/ella", "").split(" ")[-1]
    if not yo:
        return False
    if yo != stem + "o":
        return True
    return bool(el) and el != stem + ("ó" if base.endswith("ar") else "ió")

def _accent_warning(verb_tenses, guess, answer, answer_label):
    """If the unaccented guess is really another form of this verb, say which."""
    g = guess.lower().strip()
    for tense, forms in verb_tenses.items():
        for person, form in forms.items():
            if form.lower() == g and form.lower() != answer.lower():
                other = f"{person} {_LABELS.get(tense, tense)}"
                return (f"  {U.YELLOW}⚠ accent matters: {answer} ({answer_label}) ≠ {g} ({other}){RESET}")
    return ""

def play():
    verbs    = U.load("verbs.json")
    inf_list = list(verbs.keys())

    # Difficulty also limits verb rarity: keep verbs found in the current word pool
    known    = {w["es"] for w in U.load("words.json")[:POOL[SETTINGS["difficulty"]]]}
    common   = [v for v in inf_list if v in known or (v.endswith("se") and v[:-2] in known)]
    inf_list = common or inf_list

    verb_type = SETTINGS["verb_type"]
    if verb_type != "all":
        want_irreg = (verb_type == "irregular")
        inf_list = [inf for inf in inf_list if _is_irregular(inf, verbs[inf]) == want_irreg]
    if not inf_list:
        print(f"\n {U.GRAY}No verbs match current filter ({verb_type}). Change it in Settings.{RESET}")
        input(" Enter to return to menu...")
        return

    allowed = TENSES[SETTINGS["difficulty"]]
    s       = U.Session("VERB CONJUGATION")

    while True:
        inf   = random.choice(inf_list)
        data  = verbs[inf]
        # skip the (few) verbs with blank forms, e.g. weather verbs
        cands = [(t, p) for t in data["tenses"] if t in allowed
                 for p in _PERSONS if data["tenses"][t].get(p)]
        if not cands:
            continue
        tense_key, person = random.choice(cands)
        answer = data["tenses"][tense_key][person]
        label  = _LABELS.get(tense_key, tense_key)

        U.clear()
        s.header()
        vt_tag = f"  {U.GRAY}[{verb_type}]{RESET}" if verb_type != "all" else ""
        refl   = f"  {U.GRAY}(reflexive: include me/te/se){RESET}" if inf.endswith("se") else ""
        print(f" {BOLD}{inf}{RESET}  ({data['en']}){vt_tag}{refl}")
        print(f" Tense:  {BOLD}{label}{RESET}")
        print(f" Person: {BOLD}{person}{RESET}\n")

        guess = input(" [q = menu] > ").strip()
        if guess.lower() == "q":
            break

        was_correct = U.match(guess, answer)
        if was_correct:
            note = ""
            if guess.lower() != answer.lower():
                note = (_accent_warning(data["tenses"], guess, answer, label)
                        or f"  {U.GRAY}(full: {answer}){RESET}")
            s.right(note=note)
        else:
            s.wrong(f"Answer: {BOLD}{answer}{RESET}  {U.GRAY}")
            _show_paradigm(data["tenses"][tense_key], person)

        if not s.advance(was_correct):
            break

    s.end("conjugation")
