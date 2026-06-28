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
spordle.py              ← entry point, 15-item menu with quest progress indicator
games/
  __init__.py
  utils.py              ← colors, themes, streak/summary helpers, yn_input(), SETTINGS
  stats.py              ← persistent stats (~/.spordle_stats.json), show(), reset()
  quests.py             ← daily quests (~/.spordle_quests.json), 3/day from pool of 13
  settings.py           ← settings menu (difficulty, theme, rounds, direction, hints, rank, verb type, reset)
  translation.py        ← flashcard ES↔EN, hints, word rank, TILT mechanic
  wordle.py             ← 6-guess, color feedback, keyboard tracker, daily+random modes
  conjugation.py        ← verb+tense+person drill, accents optional, verb type filter
  gender.py             ← m/f noun drill, heuristic-based
  false_friends.py      ← reveal-style, 40 hand-curated traps
  rapid_fire.py         ← timed translation (15/30/60s)
  hangman.py            ← ASCII gallows, 6 guesses, 5-letter words
  anagram.py            ← scrambled Spanish word + English hint
  number_drill.py       ← show a number, type it in Spanish (0-1000 by difficulty)
  roguelike.py          ← 3 lives, wrong = lose a life, chase a high score
  push_your_luck.py     ← bank points safely or push for multiplier, wrong = lose pile
  stakes.py             ← wager chips (1-5) on each answer + double-or-nothing offers
data/
  words.json
  words_5letter.json
  verbs.json
  false_friends.json
```

**Known gaps:**
- Translation gloss quality uneven (Wiktionary parse artifacts)
- Gender heuristic misses -e endings and some exceptions

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

### 2026-06-28 — Session 9

**Sound effects, aliveness + AUR packaging:**

- **Sound effects** (`games/sounds.py`): Procedurally generated tones via stdlib `wave`+`math`+`struct` — no assets, no pip installs. Plays async via `aplay`/`afplay` subprocess + threading. Toggle via Settings option 13.
  - `correct()`: 880Hz ping; `wrong()`: detuned 220/233Hz buzz; `milestone(n)`: ascending chords at streaks 5/10/25; `game_over()`: descending 3-note A-F#-D
  - Navigation sounds: `navigate()` (523Hz click on menu/settings select), `back()` (370Hz on exit), `toggle_on()`/`toggle_off()` (ascending/descending chirp on settings toggles)
- **More alive features:**
  - Time-based greeting in startup banner — ¡Buenos días/Buenas tardes/Buenas noches!
  - Near-best streak nudge in game header — "One more from your best!" when gap ≤ 2
  - `wrong_msg(prev_streak)`: context-aware wrong messages — streak of 7+ says "¡Ay no! 7 streak gone." instead of generic
  - `checkpoint(total)`: `✦ 10 rounds — ¡En racha! ✦` flash at 10/25/50/100 rounds
  - Last session shown in main menu: `last: translation  84%  streak 12`
- **Settings tightened**: removed blank lines between options — all 14 settings now visible at once
- **PKGBUILD** added for AUR packaging as `spordle-git`. `depends=('python' 'alsa-utils')` ensures `aplay` auto-installs. Installs to `/usr/lib/spordle/` with wrapper at `/usr/bin/spordle`.

### 2026-06-28 — Session 8

**Settings polish + visual + QoL:**

- **5 new settings** (now 14 total, grouped in GAMEPLAY/DISPLAY/BEHAVIOUR/MODES/DATA):
  - Auto-Advance: correct answers auto-advance after 0.5s
  - Strict Accents: enforces exact typed characters (dieciséis vs dieciseis)
  - Spaced Repetition (SRS): 40% pull rate from missed-word list, persisted between sessions
  - Rapid Fire Time: set default so per-session prompt is skipped
  - Roguelike Lives: choose 1/2/3/5 starting lives
- **Visual polish**: startup ASCII banner with time greeting, dynamic separator widths, centered game titles with color-coded difficulty badge (green/yellow/red), redesigned session summary, streak milestone boxes at 5/10/25
- **Games updated**: `pause(ok)`, `match()` for accent-aware comparison, `streak_milestone()` in all games, `U.play_correct()`/`U.play_wrong()` in all games

### 2026-06-28 — Session 7

**Gambling + addiction update:**

- **Roguelike** (game 10): 3 lives (♥♥♥), wrong answer costs a life, run ends at 0. Chase best score. Loss aversion loop.
- **Push Your Luck** (game 11): bank points safely or push for an increasing multiplier. Wrong answer loses the whole push pile. Bank/push choice after every correct answer.
- **High Stakes** (game 12): bet 1-5 chips per question on your confidence. Double-or-nothing offer after each correct answer (doubles both gain and risk next round). Start with 100 chips, bust = game over.
- **Daily Quests** (game 13): 3 quests generated fresh each day from a pool of 13. Progress tracked vs stats snapshot at quest-gen time. Quest progress shown live in the main menu header (⚡ 0/3).
- **Tilt mechanic** in Translation: 3 consecutive wrong answers → TILT fires, next 5 questions draw from top-200 easiest words. Prevents frustration exits.
- **Persistent stats** (game 14 / My Stats): all 12 games tracked to `~/.spordle_stats.json`. Per-game: rounds, correct, best streak. Roguelike: best run. Push Your Luck: best banked. High Stakes: peak chips.
- **Verb type filter** (Settings 7): filter Conjugation to irregular/regular/all. Detected via present-tense yo-form heuristic (190 irregular, 447 regular out of 637).
- **Number Drill** (game 9): type any number 0-1000 in Spanish. Difficulty controls range. Accents optional.
- **Reset Stats** (Settings 8): wipes `~/.spordle_stats.json` after confirmation.
- Menu now shows gambling section separator and quest indicator in header.

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
