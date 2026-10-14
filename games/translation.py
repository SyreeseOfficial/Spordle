import random
from . import utils as U
from . import stats as S
from .utils import SETTINGS, POOL, BOLD, RESET

_MISS_CAP = 50

def _hint(answer):
    a = answer[3:] if answer.startswith("to ") else answer
    return a[0].upper()

def play():
    all_words = U.load("words.json")
    words     = all_words[:POOL[SETTINGS["difficulty"]]]
    es_to_en  = U.ask_direction("TRANSLATION")

    # Persisted across sessions. miss_words is kept oldest → newest and never filtered
    # on save (so other difficulties' misses survive); it is filtered only when read.
    t_data         = S.load().get("translation", {})
    mastery_counts = dict(t_data.get("mastery_counts", {}))
    mastered_words = set(t_data.get("mastered_words", []))
    miss           = list(t_data.get("miss_words", [])) if SETTINGS["srs"] else []

    s            = U.Session("TRANSLATION")
    consec_wrong = 0
    tilt_rounds  = 0
    seen         = set()

    while True:
        # Tilt: ease up after 3 consecutive wrong
        pool = words[:min(200, len(words))] if tilt_rounds > 0 else words

        miss_set = set(miss)
        srs_pool = [w for w in words if w["es"] in miss_set] if SETTINGS["srs"] else []

        # Spaced repetition: 40% chance to revisit a missed word
        if srs_pool and random.random() < 0.4:
            word = random.choice(srs_pool)
            idx  = words.index(word)
        else:
            fresh = [w for w in pool if w["es"] not in seen]
            if not fresh:
                seen.clear()
                fresh = pool
            word = random.choice(fresh)
            idx  = pool.index(word)
            seen.add(word["es"])

        prompt = word["es"] if es_to_en else word["en"]
        answer = word["en"] if es_to_en else word["es"]
        dir_label = f"{U.GRAY}[ES→EN  f=flip]{RESET}" if es_to_en else f"{U.GRAY}[EN→ES  f=flip]{RESET}"

        U.clear()
        s.header()
        if tilt_rounds > 0:
            print(f" {U.YELLOW}TILT — easier words for {tilt_rounds} more round{'s' if tilt_rounds != 1 else ''}{RESET}")
        if word["es"] in miss_set:
            print(f" {U.CYAN}SRS — revisiting a missed word{RESET}")
        if word["es"] in mastered_words:
            print(f" {U.GREEN}★ mastered{RESET}")
        if SETTINGS["hints"]:
            print(f"  {U.GRAY}Hint: starts with '{_hint(answer)}'{RESET}\n")

        print(f"  {dir_label}")
        tail = f"   {U.GRAY}(#{idx + 1} most common Spanish word){RESET}" if SETTINGS["show_rank"] else ""
        rating = U.ask(prompt, U.accepted(word, es_to_en), shown=answer, flip=True, tail=tail)
        if rating == "q":
            break
        if rating == "f":
            es_to_en = not es_to_en
            continue

        es_key = word["es"]
        if rating:
            consec_wrong = 0
            if es_key in miss:
                miss.remove(es_key)
            # mastery: 3 consecutive correct marks word as mastered
            mastery_counts[es_key] = mastery_counts.get(es_key, 0) + 1
            if mastery_counts[es_key] >= 3 and es_key not in mastered_words:
                mastered_words.add(es_key)
                print(f"\n {U.GREEN}{BOLD}★ Word mastered: {es_key}{RESET}")
            s.right()
        else:
            consec_wrong += 1
            mastery_counts[es_key] = 0  # reset mastery streak on wrong
            if SETTINGS["srs"]:
                if es_key in miss:
                    miss.remove(es_key)
                miss.append(es_key)
                del miss[:-_MISS_CAP]
            if consec_wrong >= 3:
                tilt_rounds  = 5
                consec_wrong = 0
                s.wrong("")
                print(f"\n {U.YELLOW}TILT — easing up for a few rounds...{RESET}")
            else:
                s.wrong("")

        if tilt_rounds > 0:
            tilt_rounds -= 1

        if not s.advance(rating):
            break

    extra = {"miss_words": miss} if SETTINGS["srs"] else {}
    s.end("translation", mastery_counts=mastery_counts,
          mastered_words=list(mastered_words), **extra)
