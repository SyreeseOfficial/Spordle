import random
from . import utils as U
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
        if t == 1:
            parts.append("mil")
        else:
            pre = _to_es(t)  # "uno" shortens before mil: veintiún mil, treinta y un mil
            if pre.endswith("veintiuno"):
                pre = pre[:-9] + "veintiún"
            elif pre.endswith("uno"):
                pre = pre[:-3] + "un"
            parts.append(pre + " mil")
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

def _variants(n):
    """Older spellings still accepted: diez y seis, veinte y uno."""
    if 16 <= n <= 19:  return [f"diez y {_ONES[n - 10]}"]
    if 21 <= n <= 29:  return [f"veinte y {_ONES[n - 20]}"]
    return []

def _pick(lo, hi):
    """Choose the digit count first so 1- and 2-digit numbers get practice too."""
    d = random.randint(len(str(lo)), len(str(hi)))
    return random.randint(max(lo, 10 ** (d - 1) if d > 1 else 0), min(hi, 10 ** d - 1))

_RANGES = {"easy": (0, 20), "medium": (0, 99), "hard": (0, 999)}

def play():
    lo, hi = _RANGES[SETTINGS["difficulty"]]
    s = U.Session("NUMBER DRILL")

    while True:
        n      = _pick(lo, hi)
        answer = _to_es(n)

        U.clear()
        s.header()
        print(f" Type this number in Spanish:\n")
        print(f"  {BOLD}{n}{RESET}\n")

        guess = input(" [q = menu] > ").strip().lower()
        if guess == "q":
            break

        ok = any(U.match(guess, a) for a in [answer] + _variants(n))
        if ok:
            note = f"  {U.GRAY}(full: {answer}){RESET}" if guess != answer else ""
            s.right(f"{U.praise()}  →  {answer}", note=note)
        else:
            s.wrong(f"Answer: {BOLD}{answer}{RESET}  {U.GRAY}")

        if not s.advance(ok):
            break

    s.end("number_drill")
