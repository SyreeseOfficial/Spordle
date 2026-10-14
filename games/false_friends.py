import random
from . import utils as U
from .utils import BOLD, RESET

def play():
    friends = U.load("false_friends.json")
    random.shuffle(friends)

    s = U.Session("FALSE FRIENDS")

    for entry in friends:
        U.clear()
        s.header()
        print(f" {BOLD}{entry['es']}{RESET}\n")
        print(f" {U.GRAY}Looks like:{RESET}  \"{entry['looks_like']}\"\n")

        if input(" What does it ACTUALLY mean?  [Enter to reveal  /  q = menu] > ").strip().lower() == "q":
            break

        print(f"\n {U.YELLOW}Actually:{RESET}  {BOLD}{entry['real_en']}{RESET}")
        print(f" {U.GRAY}Remember:{RESET}  {entry['es']}  ≠  {entry['looks_like']}\n")

        rating = U.yn_input(" Did you know it? [Y/n] > ")
        if rating == "q":
            break

        if rating:
            s.right()
        else:
            s.wrong()

        if not s.advance(rating):
            break

    s.end("false_friends")
