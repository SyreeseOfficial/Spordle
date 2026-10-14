```
╔════════════════════════════════════╗
║       S  P  O  R  D  L  E         ║
║        Spanish Practice CLI        ║
╚════════════════════════════════════╝
```

> A multi-game Spanish language practice tool for the terminal. Built for intermediate learners who want daily drilling without leaving the command line.

---

## Games

| # | Game | What it drills |
|---|------|----------------|
| 1 | **Translation** | Flashcard vocab — Spanish ↔ English, your choice of direction |
| 2 | **Wordle** | Spelling + recognition — 6 guesses, color-coded letter feedback |
| 3 | **Verb Conjugation** | Give a verb, tense, and person — type the correct conjugated form |
| 4 | **Gender Drill** | Nouns → `el` or `la` — fast reflexes for gendered articles |
| 5 | **False Friends** | Tricky words that look English but aren't (`embarazada` ≠ embarrassed) |
| 6 | **Rapid Fire** | Timed translation sprint — 15s / 30s / 60s, measures correct/min |
| 7 | **Hangman** | Classic ASCII gallows, 6 guesses — word length scales with difficulty (5 / 6–7 / 8+) |
| 8 | **Anagram** | Unscramble a scrambled Spanish word with an English hint |
| 9 | **Number Drill** | See a number, type it in Spanish — range scales with difficulty |
| 10 | **Roguelike** | 3 lives, wrong answer costs one — chase the highest score |
| 11 | **Push Your Luck** | Bank points safely or push for a growing multiplier — one wrong wipes the pile |
| 12 | **High Stakes** | Bet chips on your confidence per round (cap grows with your stack) + Double Bet offers |

---

## Features

**Practice mechanics**
- Spaced repetition — Translation revisits recently missed words (40% pull rate, persisted to disk)
- Tilt system — 3 wrong in a row triggers 5 rounds of easier words so you don't rage quit
- Verb type filter — drill only irregular verbs, only regular, or all 637
- Accent strictness toggle — practice exact characters or use relaxed matching (`ñ` is always required)
- Answer Mode — self-rate after reveal, or type the answer and get auto-graded

**Progression & feedback**
- Streak tracking with live display and milestone celebration boxes at 5 / 10 / 25
- Session summary with score bar and grade after every game
- Persistent all-time stats saved under `~/.local/share/spordle/`
- Daily quests — 3 generated each day from a pool of 15 (never two for the same game), progress shown in menu header
- Round checkpoints at 10 / 25 / 50 / 100 rounds mid-session
- Context-aware wrong messages — breaking a 7-streak gets a different response than missing your first
- Near-best streak nudge in header when you're 1–2 away from your record
- Last session result shown in the main menu on return

**Polish**
- 4 color themes: default / ocean / sunset / mono
- Dynamic separator widths that fill your terminal
- Time-based greeting on startup — ¡Buenos días / Buenas tardes / Buenas noches!
- Sound effects via `aplay` (Linux) or `afplay` (macOS) — procedurally generated, no bundled files
- Auto-advance mode skips the Enter pause after correct answers (0.5s flash instead)

---

## Install

**Requirements:** Python 3.8+, no third-party packages, and a Unix-like terminal (Linux / macOS) with ANSI colors and emoji. Windows `cmd` is not supported.

```bash
git clone https://github.com/SyreeseOfficial/Spordle.git
cd Spordle
python3 spordle.py
```

**Arch Linux (AUR)**

```bash
yay -S spordle-git
spordle
```

Sound effects need `alsa-utils` (`aplay`); it is an optional dependency — install it if you want sounds.

---

## Settings

Access from the main menu → option **15 Settings**. Numbers below match the on-screen list.

| # | Option | Default | Description |
|---|--------|---------|-------------|
| 1 | Difficulty | Medium | Controls vocab pool size, tense complexity, Hangman word length |
| 2 | Round Limit | Unlimited | End a drill after 5 / 10 / 25 rounds (Translation, Conjugation, Gender, Anagram, Number, False Friends only) |
| 3 | Direction | Ask | ES→EN, EN→ES, or ask each session (Translation, Rapid Fire, Roguelike, Push Your Luck, High Stakes) |
| 4 | Verb Type | All | Filter Conjugation to irregular / regular / all |
| 5 | Answer Mode | Reveal | `reveal` = self-rate; `type` = type the answer, auto-graded |
| 6 | Color Theme | Default | default / ocean / sunset / mono |
| 7 | Hints | Off | Show first letter of the answer before reveal |
| 8 | Word Rank | Off | Show frequency rank after Translation reveal |
| 9 | Auto-Advance | Off | Skip Enter pause after correct |
| 10 | Advance Delay | 0.5s | Flash time when auto-advance is on |
| 11 | Strict Accents | Off | Require exact characters — `dieciséis` not `dieciseis` |
| 12 | Spaced Rep | Off | Revisit recently-missed words in Translation |
| 13 | Rapid Fire Time | Ask | Set a default time so the per-session prompt is skipped |
| 14 | Roguelike Lives | 3 | Starting lives: 1 / 2 / 3 / 5 |
| 15 | Sounds | Off | Sound effects via aplay / afplay |
| 16 | Volume | Medium | low / medium / high |
| 17 | Favorites | — | Up to 3 games pinned to the top of the menu |
| 18 | Reset Stats | — | Wipe all-time records and daily quests |

---

## Data

| File | Contents |
|------|----------|
| `data/words.json` | 5,000 frequency-ranked bilingual ES↔EN pairs (optional `g` noun gender, `cognate` flag). The 584 five-letter ASCII words for Wordle / Anagram are derived from it at load |
| `data/verbs.json` | 637 verbs across 5 tenses (present, preterite, imperfect, future, subjunctive) |
| `data/false_friends.json` | 40 hand-curated false friends |

Sources: [doozan/spanish_data](https://github.com/doozan/spanish_data) (Wiktionary), [ghidinelli/fred-jehle-spanish-verbs](https://github.com/ghidinelli/fred-jehle-spanish-verbs), false friends hand-curated.

---

## Stats & quests

Files follow the XDG spec (`$XDG_CONFIG_HOME` / `$XDG_DATA_HOME`):

| File | Path |
|------|------|
| Settings | `~/.config/spordle/settings.json` |
| Stats | `~/.local/share/spordle/stats.json` |
| Daily quests | `~/.local/share/spordle/quests.json` |
| CSV export | `~/.local/share/spordle/export.csv` |

Old `~/.spordle_*.json` files are moved there automatically on first launch.

To reset everything: **Settings → 18. Reset Stats**

## Tests

```bash
python3 tests/test_pure.py
```

---

*Built for intermediate Spanish learners. Pure Python, stdlib only.*
