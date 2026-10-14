"""Pure-function checks. Run: python3 tests/test_pure.py  (or pytest)."""
import builtins, os, sys, tempfile

_tmp = tempfile.mkdtemp()
os.environ["XDG_CONFIG_HOME"] = os.environ["XDG_DATA_HOME"] = _tmp  # never touch real data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from games import utils as U, number_drill, wordle, conjugation, gender, stats, quests

def test_yn_input():
    def ask(reply):
        replies = iter(reply if isinstance(reply, list) else [reply])
        builtins.input = lambda _="": next(replies)
        return U.yn_input("")
    assert ask("") is True and ask("y") is True and ask("YES") is True
    assert ask("n") is False and ask("no") is False
    assert ask("q") == "q"
    assert ask(["x", "nope", "n"]) is False  # junk re-asks

def test_match():
    U.SETTINGS["strict_accents"] = False
    assert not U.match("", "")
    assert U.match("hable", "hablé")
    assert not U.match("ano", "año") and U.match("año", "año")
    assert U.strip_accents("soñar") == "soñar"
    U.SETTINGS["strict_accents"] = True
    assert not U.match("hable", "hablé")
    U.SETTINGS["strict_accents"] = False

def test_check_answer():
    assert U.check_answer("favour", ["favor/favour"]) and U.check_answer("favor", ["favor/favour"])
    assert U.check_answer("run", ["to run"]) and U.check_answer("colour", ["color / colour"])
    assert U.check_answer("to go", ["to go, to travel"]) and U.check_answer("travel", ["to go, to travel"])
    assert not U.check_answer("", ["x"]) and not U.check_answer("cat", ["dog"])

def test_accepted_alternates():
    w = {"es": "ser", "en": "to be"}
    assert "estar" in U.accepted(w, False) and U.accepted(w, True) == ["to be"]

def test_to_es():
    t = number_drill._to_es
    assert t(0) == "cero" and t(16) == "dieciséis" and t(21) == "veintiuno" and t(100) == "cien"
    assert t(21000) == "veintiún mil" and t(31000) == "treinta y un mil" and t(1000) == "mil"
    assert t(2021) == "dos mil veintiuno"
    assert "diez y seis" in number_drill._variants(16)
    for _ in range(200):
        assert 0 <= number_drill._pick(0, 999) <= 999

def test_wordle_score():
    assert wordle._score("perro", "perro") == ["green"] * 5
    assert wordle._score("aaaaa", "abcde") == ["green"] + ["gray"] * 4
    assert wordle._score("hecho", "tecla")[1] == "green"

def test_gender():
    assert gender._infer_gender("nación") == "f" and gender._infer_gender("libro") == "m"
    assert gender._gender({"es": "día", "g": "m"}) == "m"
    assert gender._gender({"es": "radio", "g": "x"}) is None

def test_irregular():
    verbs = U.load("verbs.json")
    irr = lambda v: conjugation._is_irregular(v, verbs[v])
    assert not irr("hablar") and irr("tener") and irr("andar")
    assert irr("acostarse") and not irr("aburrirse")

def test_data():
    words = U.load("words.json")
    assert len(U.five_letter()) == 584
    assert all(w["pos"] == "v" for w in words if w["es"] in ("hacer", "decir", "querer", "poder"))
    g = {w["es"]: w.get("g") for w in words}
    assert g["día"] == "m" and g["mano"] == "f" and g["foto"] == "f"

def test_stats_and_quests():
    stats.reset()
    msgs = stats.update("translation", 3, 5, 3, seconds=10)
    assert stats.load()["translation"]["played"] == 5 and isinstance(msgs, list)
    stats.update("roguelike", 2, 4, 2, run=True, best_run=2)
    assert stats.load()["roguelike"]["runs"] == 1
    d = stats.load()
    assert len(set(g for g in d["achievements"])) == len(d["achievements"])
    qs = quests.get()
    assert len(qs) == 3

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
