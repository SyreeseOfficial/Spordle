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
| 7 | **Hangman** | Classic ASCII gallows, 5-letter Spanish words, 6 guesses |
| 8 | **Anagram** | Unscramble a scrambled Spanish word with an English hint |
| 9 | **Number Drill** | See a number, type it in Spanish — range scales with difficulty |
| 10 | **Roguelike** | 3 lives, wrong answer costs one — chase the highest score |
| 11 | **Push Your Luck** | Bank points safely or push for a growing multiplier — one wrong wipes the pile |
| 12 | **High Stakes** | Bet chips (1–5) on your confidence per round + double-or-nothing offers |

---

## Features

**Practice mechanics**
- Spaced repetition — Translation revisits recently missed words (40% pull rate, persisted to disk)
- Tilt system — 3 wrong in a row triggers 5 rounds of easier words so you don't rage quit
- Verb type filter — drill only irregular verbs, only regular, or all 637
- Accent strictness toggle — practice exact characters or use relaxed matching

**Progression & feedback**
- Streak tracking with live display and milestone celebration boxes at 5 / 10 / 25
- Session summary with score bar and grade after every game
- Persistent all-time stats saved to `~/.spordle_stats.json`
- Daily quests — 3 generated each day from a pool of 13, progress shown in menu header
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

**Requirements:** Python 3.8+, no third-party packages.

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

This automatically installs `alsa-utils` (for sound effects) as a dependency.

---

## Settings

Access from the main menu → option **15 Settings**.

| # | Option | Default | Description |
|---|--------|---------|-------------|
| 1 | Difficulty | Medium | Controls vocab pool size and tense complexity |
| 2 | Round Limit | Unlimited | End a session after 5 / 10 / 25 rounds |
| 3 | Translation Dir | Ask | ES→EN, EN→ES, or ask each session |
| 4 | Verb Type | All | Filter Conjugation to irregular / regular / all |
| 5 | Color Theme | Default | default / ocean / sunset / mono |
| 6 | Hints | Off | Show first letter of the answer before reveal |
| 7 | Word Rank | Off | Show frequency rank after Translation reveal |
| 8 | Auto-Advance | Off | Skip Enter pause after correct (0.5s flash) |
| 9 | Strict Accents | Off | Require exact characters — `dieciséis` not `dieciseis` |
| 10 | Spaced Rep | Off | Revisit recently-missed words in Translation |
| 11 | Rapid Fire Time | Ask | Set a default time so the per-session prompt is skipped |
| 12 | Roguelike Lives | 3 | Starting lives: 1 / 2 / 3 / 5 |
| 13 | Sounds | Off | Sound effects via aplay / afplay |
| 14 | Reset Stats | — | Wipe all-time records |

---

## Data

| File | Contents |
|------|----------|
| `data/words.json` | 5,000 frequency-ranked bilingual ES↔EN pairs |
| `data/words_5letter.json` | 584 five-letter Spanish words (Wordle / Hangman / Anagram) |
| `data/verbs.json` | 637 verbs across 5 tenses (present, preterite, imperfect, future, subjunctive) |
| `data/false_friends.json` | 40 hand-curated false friends |

Sources: [doozan/spanish_data](https://github.com/doozan/spanish_data) (Wiktionary), [ghidinelli/fred-jehle-spanish-verbs](https://github.com/ghidinelli/fred-jehle-spanish-verbs), false friends hand-curated.

---

## Stats & quests

Stats persist between sessions at `~/.spordle_stats.json`.  
Daily quests persist at `~/.spordle_quests.json`.

To reset everything: **Settings → 14. Reset Stats**

---

*Built for intermediate Spanish learners. Pure Python, stdlib only.*
