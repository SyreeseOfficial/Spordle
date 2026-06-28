# Spordle — Spanish CLI Practice Tool

## Project Overview

Multi-game Spanish language practice tool for the terminal. Target user: intermediate Spanish learner.

**Runtime:** Python, stdlib only.
**Word list:** Bilingual (Spanish ↔ English pairs). 5-letter subset for Wordle/Hangman/Anagram. Full vocab for everything else.
**Accent marks:** Option C for v1 — no accented words in pool. Removes input friction, vocab practice still works. Revisit later.

---

## Game List

| Game | What it drills | Priority | Notes |
|---|---|---|---|
| **Translation** | Vocab recall (ES→EN or EN→ES) | v1 | Most educationally dense |
| **Wordle** | Spelling + vocab recognition | v1 | 5-letter words, 6 guesses, color feedback |
| **Verb Conjugation** | Give verb + tense + person → type conjugation | v1 | Hardest to build; needs conjugation dataset. Highest ROI for intermediate learners |
| **El/La Gender Drill** | Noun → type m or f | v1 | Trivial to build on top of word list |
| **False Friends** | Tricky words that look like English but aren't | v1 | Small curated list, fast to build. e.g. embarazada ≠ embarrassed |
| **Hangman** | Vocab with partial letter info | v2 | Easy add-on, reuses word list |
| **Anagram** | Unscramble a Spanish word | v2 | Fun filler, reuses word list, low priority |

---

## Key Decisions

1. **Accent marks:** No accented words in v1 word pool (Option C). Revisit for v2.
2. **Word list:** Done — 5,000 frequency-ranked bilingual pairs.
3. **Verb conjugation data:** Done — 637 verbs across 5 tenses.
4. **False friends list:** Done — 40 hand-curated entries.

---

## Data Files (`data/`)

| File | Contents | Count |
|---|---|---|
| `words.json` | Bilingual ES↔EN pairs, frequency-ranked. Fields: `es`, `en`, `pos` | 5,000 words |
| `words_5letter.json` | Subset of words.json, 5-letter ASCII-only Spanish words (for Wordle/Hangman/Anagram) | 584 words |
| `verbs.json` | 637 verbs with conjugations. Fields: `en`, `tenses → {person: form}` | 637 verbs |
| `false_friends.json` | Hand-curated false friends. Fields: `es`, `looks_like`, `real_en` | 40 entries |

**Sources:**
- Words: [doozan/spanish_data](https://github.com/doozan/spanish_data) (Wiktionary-based), filtered to top 5000 by frequency
- Verbs: [ghidinelli/fred-jehle-spanish-verbs](https://github.com/ghidinelli/fred-jehle-spanish-verbs) (Fred Jehle database)
- False friends: hand-curated

**Verb tenses included:** Indicativo/Presente, Indicativo/Pretérito, Indicativo/Imperfecto, Indicativo/Futuro, Subjuntivo/Presente

---

## Where We Left Off (resume here)

**All v1 games are built and smoke-tested. Ready to run and play.**

Run with: `python3 spordle.py` from `/home/sy/Documents/Code/Spordle/`

**Current file structure:**
```
spordle.py              ← entry point, numbered menu
games/
  __init__.py
  utils.py              ← load(), colors, themes, streak/summary helpers, yn_input()
  settings.py           ← settings menu (difficulty, theme, rounds, direction, hints, rank)
  translation.py        ← flashcard ES↔EN, self-rated Y/n, hints, word rank
  wordle.py             ← 6-guess, color feedback, keyboard tracker, daily+random modes
  conjugation.py        ← verb+tense+person drill, accents optional, paradigm on wrong
  gender.py             ← m/f noun drill, heuristic-based (2076 nouns in pool)
  false_friends.py      ← reveal-style, 40 hand-curated traps
  rapid_fire.py         ← timed translation (15/30/60s), pick time at game start
  hangman.py            ← ASCII gallows, 6 guesses, 5-letter words
  anagram.py            ← scrambled Spanish word + English hint, unscramble it
data/
  words.json
  words_5letter.json
  verbs.json
  false_friends.json
```

**What's next (v2 / polish):**
- Play it — translation gloss quality may need cleanup (some definitions are messy from Wiktionary parse)
- Stats persistence across sessions (`~/.spordle_stats.json`)
- Accent mark support (strip-and-compare already done in conjugation — extend to word list)
- Gender heuristic misses -e endings and has edge cases — could use a curated list instead
- Number Drill game (procedural, no data needed — show 47, type "cuarenta y siete")

---

## Session Log

### 2026-06-27 — Session 1

- Decided on multi-game suite (started as Wordle-only)
- 7 games total: 5 in v1, 2 in v2
- User is intermediate Spanish level
- App name: **Spordle**
- Sourced and processed all data files

### 2026-06-27 — Session 2

- Built all 5 v1 games + entry point + shared utils
- All imports and data loading smoke-tested and passing
- Ready to play: `python3 spordle.py`

### 2026-06-27 — Session 5

- Added Rapid Fire: timed translation (15/30/60 sec), prompted at game start, shows correct/min rate
- Added Hangman: ASCII art gallows, 6 wrong guesses, streak tracking, reveals full word on loss
- Added Anagram: scrambled 5-letter word + English meaning shown, unscramble it
- Menu expanded to 9 games
- Anagram explanation: scrambled letters of a Spanish word — e.g. `R L A O B` → type `arbol`

### 2026-06-27 — Session 4

- Streak always visible in header (0, 1, 2... not just 3+) with color coding: gray→green→yellow+bold
- Round progress bar shown in header when round limit is active
- Best streak shown next to current streak in header every round
- New personal best notification fires inline when you beat your best (≥3 streak)
- Session timer tracked per game, shown in summary (e.g. "Time: 4:32")

### 2026-06-27 — Session 3

- Enter now defaults to "y" everywhere (yn_input helper)
- Added 4 color themes: default / ocean / sunset / mono — live switching in Settings
- Settings menu expanded: difficulty, theme, round limit (5/10/25/∞), translation direction, hints, word rank
- Round limit: shows "Round X/Y" progress counter; "Round complete!" when done
- Translation: respects direction preference from settings (skip the ask), hints (first letter), word frequency rank after reveal
- Conjugation: shows full paradigm table for that tense on wrong answer
- Summary screen now grades the session (Flawless / Strong / Good effort / ¡Ánimo!)
- All games refactored to `U.GREEN` style color access so themes propagate live
- Wordle color logic refactored to use string names ("green"/"yellow"/"gray") instead of ANSI codes as dict keys

---

*Update this file whenever direction changes, decisions are made, or significant features are added.*
