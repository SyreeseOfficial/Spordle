import random, time
from . import utils as U
from . import stats as S
from .utils import SETTINGS, BOLD, RESET

_ONES = ["cero","uno","dos","tres","cuatro","cinco","seis","siete",
         "ocho","nueve","diez","once","doce","trece","catorce","quince",
         "dieciséis","diecisiete","dieciocho","diecinueve"]

_TWENTIES = {
    20:"veinte",21:"veintiuno",22:"veintidós",23:"veintitrés",
    24:"veinticuatro",25:"veinticinco",26:"veintiséis",
    27:"veintisiete",28:"veintiocho",29:"veintinueve",
}

_TENS = ["","","","treinta","cuarenta","cincuenta",
         "sesenta","setenta","ochenta","noventa"]

_HUNDREDS = ["","ciento","doscientos","trescientos","cuatrocientos",
             "quinientos","seiscientos","setecientos","ochocientos","novecientos"]

def _to_es(n):
    if n < 20:   return _ONES[n]
    if n <= 29:  return _TWENTIES[n]
    parts = []
    if n >= 1000:
        t = n // 1000
        parts.append("mil" if t == 1 else _to_es(t) + " mil")
        n %= 1000
    if n >= 100:
        h, r = n // 100, n % 100
        parts.append("cien" if h == 1 and r == 0 else _HUNDREDS[h])
        n = r
    if n >= 30:
        t, o = n // 10, n % 10
        parts.append(_TENS[t] + (" y " + _ONES[o] if o else ""))
    elif n > 0:
        parts.append(_TWENTIES[n] if n in _TWENTIES else _ONES[n])
    return " ".join(parts)

_RANGES = {"easy": (0, 20), "medium": (0, 100), "hard": (0, 1000)}

def play():
    lo, hi = _RANGES[SETTINGS["difficulty"]]

    correct = total = streak = best_streak = 0
    rounds  = SETTINGS["rounds"]
    start   = time.time()

    while True:
        n      = random.randint(lo, hi)
        answer = _to_es(n)

        U.clear()
        U.game_header("NUMBER DRILL", correct, total, streak, best=best_streak)
        print(f" Type this number in Spanish:\n")
        print(f"  {BOLD}{n}{RESET}\n")

        guess = input(" [q = menu] > ").strip().lower()
        if guess == "q":
            break

        total += 1
        ok    = U.match(guess, answer)
        if ok:
            correct += 1
            streak  += 1
            is_new   = streak > best_streak
            best_streak = max(best_streak, streak)
            exact_note = f"  {U.GRAY}(full: {answer}){RESET}" if guess.lower() != answer else ""
            print(f"\n {U.GREEN}{U.praise()}  →  {answer}{RESET}{exact_note}{U.streak_display(streak)}")
            if is_new and streak >= 3:
                print(f" {U.YELLOW}{BOLD}*** NEW BEST STREAK! ***{RESET}")
            U.play_correct()
            U.streak_milestone(streak)
        else:
            prev_streak = streak
            streak = 0
            print(f"\n {U.GRAY}Answer: {BOLD}{answer}{RESET}  {U.GRAY}{U.wrong_msg(prev_streak)}{RESET}")
            U.play_wrong()

        U.checkpoint(total)

        if rounds > 0 and total >= rounds:
            print(f"\n {U.CYAN}{BOLD}Round complete!{RESET}")
            break

        U.pause(ok=ok)

    S.update("number_drill", correct, total, best_streak)
    U.summary(correct, total, best_streak, elapsed=int(time.time() - start))
    input(" Enter to return to menu...")
