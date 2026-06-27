import random
from .utils import load, GREEN, GRAY, BOLD, RESET, hr

def play():
    words = load("words.json")
    print(f"\n{BOLD}TRANSLATION{RESET} — Flashcard style. Press Enter to reveal, then rate yourself.")
    print("Direction: [1] ES→EN  [2] EN→ES  (default 1)")
    d = input("> ").strip()
    es_to_en = d != "2"

    correct = total = 0
    print("\nType 'q' at any prompt to quit.\n")

    while True:
        word = random.choice(words)
        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]

        hr()
        inp = input(f"{BOLD}{prompt}{RESET}\n(press Enter to reveal) > ").strip().lower()
        if inp == "q":
            break

        print(f"  → {BOLD}{answer}{RESET}")
        rating = input("Got it? [y/n] > ").strip().lower()
        if rating == "q":
            break

        total += 1
        if rating == "y":
            correct += 1
            print(f"{GREEN}+1{RESET}")
        else:
            print(f"{GRAY}Keep practicing!{RESET}")

    if total:
        pct = int(correct / total * 100)
        print(f"\nScore: {correct}/{total} ({pct}%)")
