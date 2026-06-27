import random
from .utils import load, strip_accents, GREEN, GRAY, BOLD, RESET, hr

TENSE_LABELS = {
    "Indicativo/Presente":   "Present",
    "Indicativo/Pretérito":  "Preterite",
    "Indicativo/Imperfecto": "Imperfect",
    "Indicativo/Futuro":     "Future",
    "Subjuntivo/Presente":   "Present Subjunctive",
}

PERSONS = ["yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas"]

def play():
    verbs = load("verbs.json")
    inf_list = list(verbs.keys())

    print(f"\n{BOLD}VERB CONJUGATION{RESET} — Type the conjugated form. Accents optional.")
    print("Type 'q' to quit.\n")

    correct = total = 0

    while True:
        inf = random.choice(inf_list)
        data = verbs[inf]
        tense_key = random.choice(list(data["tenses"].keys()))
        person = random.choice(PERSONS)
        answer = data["tenses"][tense_key][person]
        label = TENSE_LABELS.get(tense_key, tense_key)

        hr()
        print(f"{BOLD}{inf}{RESET} ({data['en']})")
        print(f"  {label} — {BOLD}{person}{RESET}")

        guess = input("> ").strip().lower()
        if guess == "q":
            break

        total += 1
        if strip_accents(guess) == strip_accents(answer.lower()):
            correct += 1
            if guess != answer.lower():
                print(f"{GREEN}✓ Correct!{RESET} (full form: {answer})")
            else:
                print(f"{GREEN}✓ Correct!{RESET}")
        else:
            print(f"{GRAY}✗ Answer: {BOLD}{answer}{RESET}")

    if total:
        pct = int(correct / total * 100)
        print(f"\nScore: {correct}/{total} ({pct}%)")
