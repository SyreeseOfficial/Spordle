import random
from .utils import load, GREEN, YELLOW, GRAY, BOLD, RESET, hr

def play():
    friends = load("false_friends.json")

    print(f"\n{BOLD}FALSE FRIENDS{RESET} — These Spanish words look like English words, but aren't.")
    print("Press Enter to reveal. Type 'q' to quit.\n")

    correct = total = 0
    random.shuffle(friends)

    for entry in friends:
        hr()
        print(f"{BOLD}{entry['es']}{RESET}")
        print(f"  {GRAY}Looks like:{RESET} \"{entry['looks_like']}\"")

        inp = input("What does it ACTUALLY mean? (Enter to reveal) > ").strip().lower()
        if inp == "q":
            break

        print(f"  {YELLOW}Actually means:{RESET} {BOLD}{entry['real_en']}{RESET}")
        rating = input("Did you know it? [y/n] > ").strip().lower()
        if rating == "q":
            break

        total += 1
        if rating == "y":
            correct += 1
            print(f"{GREEN}+1{RESET}")
        else:
            print(f"{GRAY}Remember: {entry['es']} ≠ {entry['looks_like']}{RESET}")

    if total:
        pct = int(correct / total * 100)
        print(f"\nScore: {correct}/{total} ({pct}%)")
    else:
        print("\nNo words reviewed.")
