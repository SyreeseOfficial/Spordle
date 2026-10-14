# Spordle — Findings

Code + data audit on 2026-10-13 (commit `249d5f4`). Every bug below was **reproduced**, not guessed. Things already listed in `todo.md` are not repeated unless the todo is wrong (see [Fix the todo list](#7-fix-the-todo-list)).

Effort tags: **XS** < 5 min · **S** ~15 min · **M** ~1 hr · **L** half a day.

## Do these first (top 5)

| # | What | Where | Effort |
|---|------|-------|--------|
| 1 | `yn_input` treats `no`, `nope`, `x` as **yes** | `utils.py:196` | XS |
| 2 | Blank Enter is "correct" for verbs with empty forms (`doler`, `llover`, `nevar`, `ocurrir`) | `utils.py:88`, `verbs.json` | XS |
| 3 | Rapid Fire rejects `favor`, `color`, `grey` (answer is `favor/favour`) | `rapid_fire.py:12` | XS |
| 4 | Daily Wordle calls global `random.seed()` — poisons every later random pick in the session | `wordle.py:53` | XS |
| 5 | Gender Drill teaches wrong answers (`la foto` marked masculine, `el día` feminine) and drops 213 common nouns | `gender.py:6-24` | M |

**Pass 2 additions (tagged _pass 2_ below) that belong near the top:**

| # | What | Where | Effort |
|---|------|-------|--------|
| 6 | Accent-stripping makes Conjugation accept the wrong *tense* (`él canto` for preterite `cantó`; 9.2% of all 19,020 forms collide) | `utils.py:88`, `conjugation.py:68` | S |
| 7 | `ñ` is treated as an accent: `ano` = `año`, `sonar` = `soñar`, `campana` = `campaña` | `utils.py:84` | XS |
| 8 | Push Your Luck: typing `q` at the reveal/“Got it?” prompt **banks the pile for free** — pushing carries no risk | `push_your_luck.py:54,60` | XS |

---

## 1. Bugs

### Wrong behavior (fix these)

- **`yn_input` says yes to anything but `n`** — `utils.py:196-201`. Typing `no` → `True`. Demo: `'no'`, `'nope'`, `'x'` all return `True`; only exact `n` works. Hits Translation, False Friends, Roguelike, Push Your Luck, High Stakes. Fix: `r in ("n", "no")` → False, `r in ("", "y", "yes")` → True, else re-ask.
- **Empty answer counts as correct** — `utils.py:88-93`. `match("", "") == True`. Four verbs (`doler`, `llover`, `nevar`, `ocurrir`) have 90 empty forms in `verbs.json`, so Conjugation can show you a blank answer. Fix: skip empty forms when picking a person/tense (and `if not guess: return False` in `match`).
- **Rapid Fire never accepts alternates** — `rapid_fire.py:12-15`. It splits on `; , (` but not `/`. 6 words fail even when typed perfectly: `favor/favour`, `color / colour`, `favorito`, `gris`, `fibra`, `galleta`. Add `/` to the split and accept *any* chunk, not only the first.
- **Rapid Fire credits answers after time is up** — `rapid_fire.py:75-81`. `over` is computed, then the answer is scored anyway. Either don't score it or say so. The timer also only refreshes between words, so a slow typist sees a stale "12s left".
- **Rapid Fire best score mixes time limits** — `rapid_fire.py:108`. `best_score` is a single max across 15s / 30s / 60s, so a 60s run always beats every 15s run. Key it by limit (`best_score_30`). _(pass 2)_ `best_per_min` has the same flaw in reverse: it extrapolates a 15 s sprint to a minute, so one lucky short run can set an unbeatable record.
- **Daily Wordle reseeds global RNG** — `wordle.py:53`. After one daily game, all later `random.choice` calls this session follow the same fixed sequence for every player that day. Use `random.Random(seed).choice(...)`.
- **Daily Wordle word changes with difficulty** — same line, `+ pool_size`. "Same for everyone today" is false unless everyone uses the same difficulty.
- **Daily Wordle repeats randomly, not after 1.6 years** — `random.choice` on a date seed is not a permutation, so you can get the same word two weeks apart. (`todo.md` describes this wrong.) Fix: `words[ordinal % len(words)]` over a list shuffled once with a fixed seed.
- **Daily Wordle can be replayed forever** — each replay adds a win to stats. Store `last_daily` date in stats and show the previous result instead.
- **Hangman progress bar overflows** — `hangman.py:49` passes `rounds` into `game_header`, but Hangman never stops at the limit. With `rounds=5` and 7 games played, the bar is 39 blocks in a 28-wide box (reproduced). Either honor `rounds` or call `game_header` with `rounds` forced to 0 here.
- **Translation hint is useless for verbs** — `translation.py:72`. Hint is `answer[0]`; ES→EN verbs are `to ...`, so the hint is always "T". Skip the leading `to `.
- **SRS silently deletes missed words** — `translation.py:26-28, 138`. The miss list is filtered to the *current difficulty pool*, then written back. Play on Easy once and every miss from Medium/Hard is erased. Also, it's ordered by word rank (not recency), so `pop(0)` evicts the *most common* word, and the "10 most recent" screen in `stats.py:123` is really "10 rarest". Fix: store the miss list in recency order, filter only when *reading*, never when saving.
- **Stale login streak on the menu** — `spordle.py:43-44`. The menu shows `🔥 N-day streak` straight from disk. Skip a week and it still says N until you play. Compare `last_played_date` to today/yesterday before showing it.
- **Roguelike / Push Your Luck stats are mislabeled** — `stats.py:197-199`. `played` counts *rounds answered*, but the screen says "runs". The quest "Complete a Roguelike run" (`quests.py:17`) is done after one round. Store `runs` separately.
- **Badge order reshuffles every save** — `stats.py:61`, `list(set)`. String hash randomization means achievements appear in a different order each launch. Use a list and `append` if new.
- **Reflexive verbs are never "irregular"** — `conjugation.py:21-25`. `endswith(("ar","er","ir"))` is false for all 71 `-se` verbs, so `acostarse` lands in the "regular only" filter. Strip `se` first.
- **"Irregular" only checks the present `yo` form** — same function. Misses preterite-irregulars (`andar`, `leer`) and flags spelling-only changes (`coger → cojo`). Acceptable, but the label overpromises.
- **Settings crash on a hand-edited file** — `utils.py:299-310`, `settings.py:27`. `"difficulty": "Hard"` → `KeyError` on game start; `"rounds": 7` → `KeyError` on the Settings screen; `rf_time: 45` → `ValueError` in `_cycle`. Validate each loaded value against its allowed list; fall back to the default.
- **Stats reset leaves quests stuck** — `stats.py:101`. Quest progress is `now − snapshot`; after a reset `now` is 0 and the snapshot isn't, so progress stays at 0 until you pass your old totals. Delete the quests file on reset.
- **Double "Enter" on bust** — `stakes.py:102` then `:109`. Remove the first one.
- **Accent-stripping makes Conjugation accept the wrong tense** _(pass 2)_ — `utils.py:88-93` used by `conjugation.py:68`. The accent *is* the answer for many forms: `él canto` is accepted for preterite `cantó`, `yo hable` for preterite `hablé` (which is also the present-subjunctive spelling). Measured over `verbs.json`: **1,756 of 19,020 forms (9.2%)** equal a *different* form of the same verb once accents are stripped. Default `strict_accents` is off, so this is what every new player gets. Fix (S): in Conjugation, accept the unaccented guess but print `⚠ accent matters: cantó (preterite) ≠ canto (present)`, or just always compare strictly there.
- **`ñ` is not an accent** _(pass 2)_ — `utils.py:84-86`. NFD splits `ñ` into `n` + a combining mark, so `strip_accents("año") == "ano"`. In the pool: `año`/`ano`, `soñar`/`sonar`, `campaña`/`campana` (3 of the 8 collisions; 66 words contain `ñ`). Typing `ano` for "year" is accepted (and is a different, rude, word). Fix (XS): protect it — `s.replace("ñ", "\0")` before NFD, restore after — so `ñ` still needs to be typed.
- **Push Your Luck: `q` is a free bank** _(pass 2)_ — `push_your_luck.py:54` and `:60` both do `banked += push_pile` on quit. After you pick "push", you see the next word, can see the answer, and if you got it wrong type `q` instead of `n` to keep the whole pile. The "one wrong and you lose the pile" rule only applies if you're honest. Fix (XS): `q` forfeits the pile (or is refused while `push_pile > 0`; banking stays an explicit choice at the bank prompt).
- **Rapid Fire "sessions" are really words** _(pass 2)_ — `stats.py:195` prints `{played} sessions`, but `rapid_fire.py:108` calls `S.update(..., correct, total)` so `played` grows by the number of words. A few 60 s rounds also unlock the `Century` achievement (`played ≥ 100`), which is meant to be 100 rounds. Same family as the Roguelike "runs" mislabel above. Fix (XS): pass `played=1` as an extra, or relabel to "words".
- **Anagram marks valid answers wrong** _(pass 2)_ — `anagram.py:39`. 80 of the 584 words sit in 37 anagram groups (`hacer`/`echar`, `padre`/`pared`, `miedo`/`medio`, `meter`/`temer`, `sacar`/`casar`, `tocar`/`actor`...). Typing the other real word from the same pool is scored wrong. Fix (XS): accept any pool word with `sorted(guess) == sorted(target)`, and show the intended one in the feedback. (Todo lists the idea; this is the size of it.)
- **Anagram gives the answer away** _(pass 2)_ — `anagram.py:32` prints `Meaning: {en}` under the scramble. For 50 of the 584 words the English gloss *contains* the answer (`error`→"error", `hotel`, `total`, `radio`, `local`, `favor`→"favor/favour", `color`...). 44 are identical cognates. Fix (XS): hide the meaning when `strip_accents(es) in gloss`, or show only POS + length.
- **Hangman silently swallows whole-word guesses** _(pass 2)_ — `hangman.py:61`. Anything that isn't one letter just redraws the screen with no message, so typing the answer looks like a freeze. Also `á`/`é` count as a *wrong* letter (the targets are ASCII). Fix (XS): print "one letter at a time", strip accents, or accept a full-word guess (right = win, wrong = lose a life).
- **Wordle `q` reveals the word and records nothing** _(pass 2)_ — `wordle.py:74-77`. In Daily mode that shows today's answer and lets you restart for free; it should count as a loss (and, with the `last_daily` fix above, end today's game). Every other game saves on `q`.
- **Quit "back" sound never plays** _(pass 2)_ — `utils.py:133`, `sounds.py:54`. `play_back()` starts a *daemon* thread, then `spordle.py:81-84` prints and exits immediately; the thread is killed before `aplay` runs. Measured with a stub `aplay` on `PATH`: **0 of 5** quits produced a sound (menu-navigate beeps: 5 of 5). Fix (XS): have `_play` return the thread and `.join(timeout=0.5)` on quit.
- **Rapid Fire has no way out** _(pass 2)_ — `rapid_fire.py:72`. `q` is just a wrong answer, and a blank Enter (skip) costs accuracy. A 60 s round can only be left with Ctrl+C. Add `q` (discard or save partial) and a skip key that doesn't count as wrong.

### Gender Drill (own section — it's the worst offender)

`gender.py` *guesses* gender from endings instead of storing it, so the game confidently teaches errors:

| Word | Game says | Truth |
|------|-----------|-------|
| `día` | la | el |
| `mano` | el | la |
| `foto` | el | la |
| `moto` | el | la |
| `radio`, `cura`, `guía` | one gender | both exist |

It also **excludes every noun ending `-ma/-pa/-ta/-ca`** to dodge masculine `-ma` words, which removes **213 common nouns** — `puerta`, `carta`, `boca`, `cama`, `fiesta`, `pregunta`, `ropa`, `cuenta`... — while keeping the exceptions. And it ignores the difficulty setting (always all 2,076 nouns, rare ones included).

**Fix (M):** add an optional `"g": "m"|"f"` field to nouns in `words.json` (start by hand-listing ~150 exceptions: `día, mano, mapa, problema, tema, sistema, programa, idioma, foto, moto, radio...`), fall back to the heuristic only when absent, and slice by `POOL[difficulty]` like the other games.

---

## 2. UX

- **Self-grading is the biggest design hole.** Translation, Roguelike, Push Your Luck and High Stakes never check what you type. In Translation, whatever you type at "Enter to reveal" is thrown away (`translation.py:75`). Combined with bug #1, pressing Enter twice is a perfect score, and the gambling modes have no real stakes. Option (L): optionally type the answer and use `rapid_fire._check` (after the fixes above); keep reveal-and-rate as a "relaxed" setting.
- **Round Limit applies to only 6 of 12 games.** Hangman, Wordle, Rapid Fire, Roguelike, Push Your Luck, High Stakes ignore it. Rename to make that clear, or grey it out in the sub-label.
- **Direction setting is ignored by Roguelike** (always ES→EN) and Strict Accents is ignored by Rapid Fire (`_normalize` always strips). Pick one rule and apply it everywhere. _(pass 2)_ The setting is labelled "Translation Dir" but also drives Rapid Fire, Push Your Luck and High Stakes — rename it "Direction".
- **Settings screen is ~45 lines tall** (17 rows × 2 lines + headers). On a 24–30 row terminal the top scrolls off after `clear()`. Fold the grey hint line into the value row, highlight the *current* option in `easy · [medium] · hard` form, and drop the hints for obvious toggles. This also fixes the todo item "show current value".
- **Wordle keyboard can't tell "untried" from "absent"** — `wordle.py:34`. Both are gray. Show untried in the default color and absent letters dimmed or struck.
- **Wordle accepts any 5 letters** (`zzzzz`). `words.json` has 658 five-character words (584 ASCII answers + 74 accented, e.g. `árbol`). Validating against those, with accents stripped, catches typos without burning a guess. It's a small list, so you may want a bigger accepted-guess list than the answer list.
- **Conjugation difficulty ignores verb rarity** — `conjugation.py:46`. Easy mode still serves `agorar` and `acontecer`. Filter `inf_list` to verbs in `words.json[:POOL[difficulty]]`.
- **Reflexive verbs give no hint** — you see `aburrirse`, must type `me aburro`. Show `(reflexive: include me/te/se)` or accept the form without the pronoun.
- **`f9` (unknown favorite) silently does nothing** — `spordle.py:90-96`. Print the same "Pick a number" message.
- **Splash screen forces an extra Enter every launch** — `utils.py:187`. Skip it, or show it for 1 second.
- **Unsupported-terminal case:** `clear()` + emoji + ANSI assume a modern Linux terminal. Fine for Arch/Omarchy; just say so in README so nobody files "doesn't work on Windows cmd".
- **No feedback when a quest or achievement completes.** You only find out on the menu. Print one line in `S.update` return value, shown after the summary.
- **Roguelike, Push Your Luck, High Stakes print no "NEW BEST STREAK"** and Push Your Luck uses `console()` instead of `wrong_msg` — small inconsistencies from copy-paste (see §4).
- **Double-or-nothing isn't "or nothing"** — `stakes.py:88`. It just doubles the next bet, free, with no extra risk. It's strictly positive if you're right >50% (and you grade yourself). Rename ("Double Bet") or make a miss cost the doubled amount *plus* a penalty.
- **High Stakes can't really end** _(pass 2)_ — `stakes.py:56`. Start is 100 chips but the bet cap is `min(5, chips)`, so busting takes 20+ straight misses (10+ with doubles) and the cap never grows. Scale it: `max_bet = max(5, chips // 10)`. Also makes the `Broke the Bank` (500 chips) achievement mean something.
- **Number Drill "hard" is 90% three-digit numbers** _(pass 2)_ — `number_drill.py:51`. `randint(0, 1000)` is uniform (measured: 1% one-digit, 9% two-digit, 90% three-digit), so you almost never practice 30–99 or the `y` tens. Pick the digit count first, then the number.
- **Stats don't know Wordle** _(pass 2)_ — `wordle.py:98`. `S.update("wordle", 1, 1)` passes no streak, so the menu's `last:` line always says `streak 0` after Wordle, Wordle can't count toward `Unstoppable`, and there's no win streak or guess-distribution (the two stats people actually want from Wordle). Same `streak 0` for Rapid Fire.
- **Daily quests overlap and some are free** _(pass 2)_ — `quests.py:42`. `random.sample` can serve "15 correct in Translation" *and* "20 rounds of Translation" together; 3 of the 13 quests have `n=1` (done after one round — and the Roguelike one says "run" but counts rounds, see §1). There are no Wordle/Hangman-play quests and no reward for finishing. Group quests by game and give `n=1` ones a larger target.
- **CSV export is thinner than the todo says** _(pass 2)_ — `stats.py:141-144` writes four columns (`game, played, correct, best_streak`). Missing: Rapid Fire best, peak chips, best run, mastered count, login streak, total time. `todo.md` has this ticked as "all fields".

---

## 3. UI

- **Mixed streak decoration:** `*** 10 STREAK ***` asterisks in-game vs `⚡ 🔥 ★ ✦` elsewhere. Pick one style (todo already suggests emoji ramp — do it in `streak_display` + `game_header` together).
- **Red is a raw escape code in 6 places** (`"\033[91m"`: `utils.py:232`, `roguelike.py:11`, `push_your_luck.py:39`, `stakes.py:41`, ...). Add `RED` to the theme tuples. Bonus: `mono` then gets a monochrome "red" instead of bypassing the theme.
- **Stats rows don't line up:** each game type uses a different format string (`stats.py:193-203`). One table with fixed columns (`played · correct% · best streak · extra`) is easier to scan.
- **Hangman gallows are a single color for all stages** — `_draw(wrong, ...)`. (Todo has per-part colors; the stage-based color already exists, which is nearly enough.)
- **`last: translation 88% streak 12` on the menu** shows the raw stats key; fine, but pad it consistently with `{name_str:<16}`.

---

## 4. Efficiency & code size

Most of this is **deleting**, not optimizing.

- **Sound wrappers: 7 near-identical functions** — `utils.py:112-152` (+ a copy in `streak_milestone`). Replace with one: `def sfx(name, *a): getattr(sounds, name)(*a)` inside a single `try`. ~35 lines gone.
- **Game list lives in 4 places:** `spordle.py:GAMES`, `stats.py:_GAMES` + `_LABELS` (defined **twice**, in `show()` and `_export()`), `settings.py:_ALL_GAMES`. Make one registry (`key, label, play`, plus a `group` field) and derive everything. Also fixes the hard-coded `i == 10` / `i == 13` separators in `spordle.py:65-68`.
- **Correct/wrong block is copy-pasted into ~9 games** (streak++, best, new-best banner, sound, milestone, checkpoint, round-limit, pause, summary). A small `Session` helper (`record(ok) → prints feedback`) removes ~150 lines and fixes the inconsistencies in §2 by construction. This is the single biggest cleanup (L).
- **Header code duplicated 3×:** `roguelike.py:9-17`, `push_your_luck.py:37-44`, `stakes.py:39-47` re-implement `game_header`'s title/centering; they also inline the difficulty color that `utils._diff_color()` already provides. Make `_diff_color` public and call it.
- **Sound playback spawns an extra process each time:** `sounds.py:43` runs `which aplay` then `which afplay` via `subprocess` on every beep. Use `shutil.which` once at import. *(Measured: generating the longest tone in pure Python takes ~8 ms — the todo's "memoize tones" item is not worth doing.)*
- **Menu does 5 disk reads per redraw** — `spordle.py:34-47`: `quests.get()` (reads quests file + `stats.load()`), then `stats.load()` again, then `get_last()` which loads a third time. Load stats once, pass it down.
- **Two read-modify-write cycles per session** — `stats.update` then `stats.add_time`. Fold elapsed seconds into `update`.
- **`stats.add_time` counts time on the Stats / Settings / Quests screens** — `spordle.py:95,102` wraps *every* menu item. Only time actual games.
- **Redundant data file:** `words_5letter.json` (584 entries) is exactly the ASCII 5-letter words of `words.json`, in the same order (verified: 584 = 584, no extras). Derive at load (`len(w["es"]) == 5 and w["es"].isascii()`) and delete the file, so POS/gloss fixes happen in one place.
- **Dead code:** `prev_streak = total - correct` (`push_your_luck.py:82`, never read); `if not valid: continue` (`conjugation.py:49-50`, every verb has every tense); identity dicts `_ROUNDS_LBL` / `_DELAY_LBL` in `settings.py` (an f-string does the job).
- **Quests file snapshots the whole stats file** _(pass 2)_ — `quests.py:_gen`, `{g: d.copy()}` is shallow, so `mastery_counts`, `mastered_words` and `miss_words` are written into `~/.spordle_quests.json` every day. Measured with 1,500 mastery entries: stats 29.8 KB, **quests 33.6 KB**, both re-read on every menu redraw. Keep only the counters quests use: `{g: {k: d.get(k, 0) for k in ("played", "correct")}}`.
- **Everything is cold-compiled on each AUR launch** _(pass 2)_ — `PKGBUILD` copies sources to `/usr/lib/spordle`, which a normal user can't write `__pycache__` into. Measured `import spordle`: 70–80 ms with no bytecode cache vs 35–40 ms with one. Add `python -m compileall -q "$pkgdir/usr/lib/spordle"` to `package()`. (XS, tiny win, but also what Arch Python packages normally do.)
- **Not worth doing** (todo says otherwise): preloading `verbs.json` — measured 9 ms. `words.index(word)` / `pool.index(word)` per round — 5,000 items, microseconds.

---

## 5. Data quality

- **POS tags are wrong for ~29 verbs:** `haber`, `hacer`, `decir`, `querer`, `sentir`, `vivir`, `comer`, `poder`, `abrir`, `correr`, `andar`... tagged `n`. `este` is tagged `n` too. This must be fixed before any "show part of speech" hint from `todo.md` ships. Quick rule: gloss starts with `to ` and ends `ar/er/ir` → `v`.
- **73 glosses are dictionary prose, not translations:** `venir` → "Senses relating to literal movement. [+de or desde", `moto` → `clipping of "motocicleta"`, `mayor` → `comparative of "grande": bigger`. Rapid Fire's `_check` can never match these. Clean to the first clause, or add a short `"alt"` list.
- **Poor primary glosses:** `querer` = "to desire" (should be "to want"), `haber` = "have".
- **Broken glosses from a truncated parse** _(pass 2)_ — 4 glosses have an unclosed bracket: `venir`, `diferente` ("different [+a or de (from"), `reír` ("to laugh [+de (at"), `advertir`. Three glosses are a single function word that Rapid Fire accepts as the whole answer: `canario` → "of" (real: "of the Canary Islands"), `encendido` → "on", `ello` → "it". `detente` is glossed as "a painted or embroidered image of a saint…" (a rare noun; the common reading is the imperative of `detener`), and `televisión` / `coca` have 80+ character glosses. Fix with the prose-gloss cleanup above (cut at the first `[`, `(`, or `.`; hand-fix the 3 one-word ones).
- **Identical cognates are free points** _(pass 2)_ — 241 of 5,000 words (4.8%) are the same string in both languages after accent-stripping (`idea`, `general`, `doctor`, `plan`, `hospital`…): 14 in Easy's 500, 83 in Medium's 2,000, 44 of the 584 five-letter words. In ES→EN modes (Translation, Rapid Fire, Roguelike…) these score without knowing anything. Not a bug; tag them (`"cognate": true`) so Rapid Fire / Anagram can skip or flag them.
- **Hangman and Anagram only use 5-letter words** _(pass 2)_ — difficulty just widens the pool (150 → 350 → 584). Hangman with 5 letters and 6 lives is easy at every level. Using `words.json` with length by difficulty (5 / 6–7 / 8+) would make the setting do something.
- **399 English glosses map to more than one Spanish word** (`to be`, `day`, `time`, `well`...). EN→ES modes (Translation flip, Rapid Fire, Push Your Luck, High Stakes) will mark `ser` wrong for "to be" when you answered `estar`. Accept any Spanish word that shares the gloss.
- **`false_friends.json` is only 40 rows** (known; `todo.md`'s list is mostly already in it — see §7).
- **`verbs.json` is 536 KB** with 5 tenses × 6 persons spelled out. It works; only worth compacting if startup ever matters (it doesn't — 9 ms).

---

## 6. Project hygiene

- **No LICENSE file** though `PKGBUILD` says `license=('MIT')`. Add `LICENSE` and install it in `package()` (AUR requires it for MIT).
- **`alsa-utils` is a hard `depends`** in `PKGBUILD:8`, but sounds are off by default. Move to `optdepends=('alsa-utils: sound effects')`.
- **Four dotfiles in `$HOME`** (`.spordle_settings.json`, `_stats`, `_quests`, `_export.csv`). Move to `~/.config/spordle/` and `~/.local/share/spordle/` (respect `XDG_*`), with a one-time migration of the old files. README lines 42, 117, 118 then need updating.
- **Write failures crash the game** — `stats._save`, `quests._save`, `utils.save_settings` have no try/except or atomic replace (todo covers atomic; also handle `PermissionError`/read-only home).
- **Ctrl+C / Ctrl+D are unhandled everywhere** — `EOFError` as well as `KeyboardInterrupt`. Put one `try/except (KeyboardInterrupt, EOFError)` around the game call in `spordle.py` (todo lists Ctrl+C twice, under UX and Technical — it's one task).
- **Zero tests.** The pure functions are easy wins and have already produced bugs here: `_to_es`, `_score`, `_infer_gender`, `rapid_fire._check`, `match`, `yn_input`. One `tests/test_pure.py` with `assert`s would have caught items 1–3 above.
- **README is stale** _(pass 2)_ — the Settings table numbers don't match the screen: Strict Accents is **10** (README: 9), Spaced Rep **11** (10), Rapid Fire Time **12** (11), Roguelike Lives **13** (12), Sounds **14** (13), and "Reset Stats" is **17** (README says 14, twice, including "Settings → 14. Reset Stats"). Missing from the table: Advance Delay, Volume, Favorites.
- **`UPDATE.md` contradicts the data** _(pass 2)_ — Key Decision #1 says "no accented words in the pool"; `words.json` has 872 accented words (17%) and 66 with `ñ`. That's why the accent bugs in §1 matter. Update the doc, or fold `UPDATE.md` into README and delete it.
- **Doc clutter:** `how-to-run.md` is one line (`python3 spordle.py`) — fold into README and delete. `my-todos.md` (AUR upload, screenshots, portfolio) is personal release tasks — merge into `todo.md` under "Release".
- **Number Drill extension caveat** (todo "extend to 9,999"): `_to_es` is wrong above 20,000 — `21000` → "veintiuno mil", `31000` → "treinta y uno mil" (should be `veintiún mil`, `treinta y un mil`). Fine for ≤ 9,999; fix before going higher.
- **Number Drill rejects valid variants** such as `veinte y uno` and `dieciseis` vs `diez y seis` (older spellings). Low priority.

---

## 7. Fix the todo list

Items in `todo.md` that are already done, wrong, or not worth it:

| `todo.md` item | Status |
|----------------|--------|
| Wordle keyboard: use QWERTY | **Already done** — `wordle.py:32` is QWERTY. Delete. |
| More false friends: `actual`, `sensible`, `molestar`, `success→éxito` | **Already in the file** (`actual`, `sensible`, `molestar`, `éxito` all present). Only `bizarre`/`embarazar` are missing. |
| Input: strip trailing whitespace | **Already done** — `match()` and every `input()` call `.strip()`. Delete. |
| Wordle daily freshness ("584 words ≈ 1.6 years") | **Mis-diagnosed** — see §1; it repeats at random much sooner. |
| Sounds: memoize common tones | **Skip** — measured ~8 ms. |
| Preload data on startup | **Skip** — measured 9 ms. |
| Ctrl+C handling (listed twice) | Merge into one item. |
| High Stakes chip color ramp "starts at wrong thresholds" | Current: green ≥100, yellow ≥50, gray below. Reasonable; delete unless you want red. |
| POS hint in Translation / Hangman | **Blocked** until POS data is fixed (§5). Hangman uses `words_5letter.json`, which has POS too. |
| Gender heuristic exceptions: "`mapa` (masculine -a) is wrong by the rule" _(pass 2)_ | **Wrong for `mapa`** — `_MASC_A_ENDS` already contains `pa`, so `mapa` is *dropped*, not taught wrong. The real damage is `día`, `mano`, `foto`, `moto` (§1 Gender table). |
| "Quit mid-game: save partial stats — quitting mid-Translation saves nothing" _(pass 2)_ | **Wrong.** Translation, Gender, Conjugation, Anagram, Number Drill, False Friends, Roguelike, Push Your Luck, High Stakes and Hangman all break to `S.update`. Only **Wordle** (`return` on `q`) and **Rapid Fire** (no `q` at all) skip it. |
| "Export stats — writes all fields" (ticked) _(pass 2)_ | **Only 4 columns**; see §2. Untick or finish it. |
| "Number Drill: confirm answer before moving on in auto-advance mode" _(pass 2)_ | **Not needed.** Auto-advance only skips the pause after a *correct* answer; wrong answers always wait. If the flash feels short, raise Advance Delay (setting 9). |
| "Conjugation: focus mode — only yo/tú/él" _(pass 2)_ | Worth doing, but also consider the inverse: **drop `vosotros`** (an on/off setting). It's absent in Latin American Spanish, and today it's 1 in 6 questions. |

---

## Suggested order

1. **15 minutes — the 5 one-liners:** `yn_input`, `match("")`, Rapid Fire `/`, Wordle `Random(seed)`, double-Enter on bust.
   - _(pass 2)_ **+15 minutes — XS fixes:** protect `ñ` in `strip_accents`, Push Your Luck `q` forfeits the pile, Anagram accepts any same-letter pool word, Hangman message for bad input, quit-sound `join`.
   - _(pass 2)_ Conjugation accent warning (S) goes with the `match` change in this step.
2. **1 hour — data + gender:** fix POS rule, add `"g"` field for exceptions, slice Gender by difficulty, skip empty verb forms.
3. **1 hour — correctness of state:** SRS miss-list, stale login streak, quest reset, badge order, settings validation.
4. **Half a day — the refactor:** single game registry, `Session` helper, sound wrapper collapse. Do this *before* adding new games from `todo.md`, or every new game copies the same 40 lines.
5. **Later:** typed-answer mode, XDG paths, LICENSE, tests.

## Skip
- **Daily Wordle reseeds global RNG** — `wordle.py:53`. After one daily game, all later `random.choice` calls this session follow the same fixed sequence for every player that day. Use `random.Random(seed).choice(...)`.
- **Splash screen forces an extra Enter every launch** — `utils.py:187`. Skip it, or show it for 1 second.
