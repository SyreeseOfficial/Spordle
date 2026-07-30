# Spordle — Improvement Ideas

## UI

- **Wordle keyboard tracker: use QWERTY layout** instead of alphabetical — matches muscle memory and mirrors every online Wordle
- **Main menu: show per-game best record inline** (e.g., `10. Roguelike        best run: 42`) so there's motivation before entering
- **Streak display: add a fire ramp** — 🔥 at 5, bigger label at 10, animation effect at 25 (just Unicode chars, no library needed)
- **Stats screen: column alignment** — current layout can drift with long numbers; use fixed-width `f"{v:>6}"` formatting
- **Stats screen: add today vs. all-time** — show session correct count next to lifetime totals so players see progress without mental math
- **Progress bar: add label** — current bar shows `[████░░]` but doesn't label min/max; add `Round 7/10` at the end
- **Hangman: color the gallows parts** as wrong guesses accumulate (gray rope, yellow body, red head) — more visual feedback
- **High Stakes: chip color ramp** already exists for green→yellow→gray but starts at wrong thresholds — update so green=profit (>100), yellow=near zero, red=<20
- **Game header: show current difficulty badge** at all times (it's in the header but small) — players forget what they set
- **Rapid Fire: results bar** is good, add a `words/min` count in a contrasting color so it stands out from the wall of text
- **Main menu: indent gambling/meta groups** with a visual section header like the existing `── gambling ──` separator (currently only one separator exists)

## UX

- **In-game "restart" option** — after a session ends, prompt `[r]estart  [q]quit` so players don't have to navigate the menu just to play again
- **Quit mid-game: save partial stats** — currently quitting mid-Translation saves nothing if you typed `q`; at minimum write `_last` so the menu shows your interrupted session
- **Menu: short-name shortcuts** — let players type `t` for Translation, `w` for Wordle, `c` for Conjugation etc. alongside the numbers
- **Settings: show current value next to each option** — the cycle UI already does this but the layout is dense; add a ` (current)` arrow indicator
- **Conjugation: show the full paradigm *before* the answer on hard** so players can self-check — right now it only appears on wrong
- **Translation: show part of speech as hint** (noun/verb/adj) since words.json has `pos`; free one-char hint that removes ambiguity
- **Wordle: accept accented guesses** — currently validates `guess.isalpha()` which accepts accented chars, but 5-letter pool is ASCII only; at minimum strip accents from guess before checking so `canción` → `cancion` works
- **Hangman: show POS category** at round start (`[noun]` or `[verb]`) — reduces frustration on obscure words
- **False Friends: add bidirectional mode** — show the English word that looks Spanish (e.g., "embarrassed" → what does it look like in Spanish?) for extra challenge
- **Number Drill: confirm answer before moving on** in auto-advance mode — numbers are easy to mistype; 0.5s flash is too short for a 10-character answer to register
- **Ctrl+C handler** — currently a KeyboardInterrupt mid-game drops to traceback; catch it at game level, save stats, and print `\n ¡Hasta luego!\n`

## Gameplay & Game Design

### New mechanics
- **Wordle hard mode** — once a letter is confirmed green/yellow, it *must* appear in all future guesses; add as a toggle in Settings
- **Conjugation: focus mode** — option to only drill yo/tú/él forms (the three hardest); currently all 6 persons are equally likely, but yo/tú/él cover 90% of real use
- **Translation: multiple-answer support** — some words have two valid English translations (e.g., `andar` = "to walk" / "to go"); currently only the first EN entry is accepted; split on `/` or `;` and accept any
- **Gender Drill: two-gender words** — words like `el/la artista`, `el/la estudiante` exist in corpus; mark them in data and accept either answer
- **Roguelike: escalating difficulty** — start at easy pool, shift to medium after 10 correct, hard after 25; turns the run into an actual difficulty climb
- **Rapid Fire: target mode** — instead of pure time, give players a target count (e.g., "get 15 in 60s") and show win/fail at end
- **Anagram: multiple valid unscrambles** — some letter sets have more than one Spanish word; accept any valid word from the 5-letter pool, not just the one it was seeded from
- **Push Your Luck: visual pile** — show the `push_pile` as a coin stack using `█` chars (e.g., `[███░░]`) so the loss feels more visceral
- **Number Drill: ordinals & currency** — "1st/2nd/3rd" (primero/segundo/tercero) and "€1.50" (un euro con cincuenta céntimos) as optional sub-modes

### New games
- **Sentence scramble** — show 5–7 Spanish words out of order, type them in correct sequence; tests word order intuition
- **Listening context** (stretch) — show only the English word, player must type the Spanish; effectively EN→ES mode but frame it as "you're the speaker"
- **Fill in the blank** — show a sentence with one word missing, pick from 3 options; tests reading comprehension vs. pure recall
- **Synonyms/Antonyms drill** — given `grande`, type a synonym (`enorme`) or antonym (`pequeño`); builds vocabulary depth
- **Irregular verb spotlight** — focused mini-game: only irregular verbs, only the forms that break the pattern (yo-go verbs: tengo, vengo, salgo); the most common pain point for learners

### Content
- **More false friends** — 40 is thin; known pairs to add: `actual` (current, not actual), `sensible` (sensitive, not sensible), `bizarre` (brave, not bizarre), `embarazar` (to impregnate), `molestar` (to bother), `success` → `éxito`; target 100+
- **Spanish proverbs** — 20–30 common refranes with meaning; add as a new "Refranes" game using the False Friends mechanic (read → reveal)
- **Regional vocabulary notes** — flag words where Spain/Latin America differ (e.g., `coche` vs `carro`, `ordenador` vs `computadora`); show as a note on reveal, not a quiz question
- **Extend number range to 9,999** — `_to_es()` already handles thousands but number_drill caps at 1000; the function is there, just raise the hard-mode cap
- **More verb tenses** — add `Condicional` (conditional) and `Imperativo` (imperative); the Fred Jehle database has them; just needs adding to `verbs.json` and `TENSES`

## Stats & Progression

- [x] **Daily login streak** — track consecutive days played in stats; show streak count in menu header next to quest progress
- [x] **Vocabulary mastered count** — mark a word as "mastered" after N consecutive correct answers; show total mastered in stats screen
- [x] **Most-missed words list** — stats screen option to show your 10 hardest words (words in `miss_words` SRS list, sorted by miss count)
- [x] **Achievements system** — simple badge list stored in stats JSON; examples: `First 100` (100 total correct), `Unstoppable` (25-streak), `Broke the Bank` (Stakes peak 500 chips), `Survived` (Roguelike run of 30); show earned badges in stats screen
- [x] **Time played tracking** — accumulate total session seconds in stats JSON; surface in stats as "Total time: 4h 22m"
- [x] **Export stats** — `s` option in stats menu writes `~/.spordle_export.csv` with all fields; useful for personal tracking in a spreadsheet

## Settings

- [x] **"Favorite games" quick list** — let players mark 2–3 games as favorites; show them at the top of the menu numbered 1–3 before the full list
- [x] **Translation direction per-session flip** — in-game `f` key to flip ES→EN to EN→ES mid-session without going back to settings
- [x] **Auto-advance delay control** — current 0.5s is hardcoded; expose as 0.3s/0.5s/0.8s/1.0s in settings so fast players can go faster
- [x] **Sound volume** — currently `vol=0.35` is hardcoded in `sounds.py:_tone()`; expose as Low/Medium/High in settings

## Technical / Code Quality

- **Preload data on startup** — `words.json` (247 KB) and `verbs.json` (551 KB) are re-read on every game entry; load once in `spordle.py` and pass to games or stash in a module-level cache
- **SRS: true miss count** — `miss_words` list can have duplicates if the same word is missed twice; deduplicate on add (already fixed in recent commit but worth verifying the max-50 cap doesn't silently drop words you actually need)
- **Stats: atomic write** — `stats.py` does a direct JSON dump; if the process dies mid-write the file is corrupted; use `tempfile` + `os.replace()` for atomic save
- **Corrupted stats/settings recovery** — bare `except Exception` swallows the error; on JSON decode failure, rename the bad file to `.bak` and start fresh rather than silently using defaults and later overwriting with empty data
- **Gender heuristic: known exceptions list** — `día` (masculine -a), `mano` (feminine -o), `mapa` (masculine -a) are wrong by the current rule; a small hardcoded exceptions dict (`{"día": "m", "mano": "f", ...}`) fixes the worst offenders without rewriting the heuristic
- **Wordle: daily word freshness** — daily word is seeded by `date.toordinal()` which repeats after the pool is exhausted (584 words ≈ 1.6 years); add a year component to the seed so it never repeats the same word on the same calendar day
- **Sounds: memoize common tones** — `correct()` and `wrong()` are called every round; pre-generate their WAV bytes once at import time and reuse the same temp file (seek to 0, rewrite) to cut 50–100ms per play
- **Ctrl+C handling** — wrap each game's `play()` call in `spordle.py` with `except KeyboardInterrupt` to save stats and exit gracefully
- **Input: strip trailing whitespace** — some players instinctively press Space before Enter; `guess.strip()` is already called in most places but double-check `conjugation.py` and `number_drill.py`

## Fun / Engagement

- **"Boss round" every 10** — at rounds 10, 20, 30... one deliberately harder word (pulled from the top-50 hardest in your SRS miss list, or from the hard pool regardless of difficulty setting); shown with a special `⚡ BOSS ROUND ⚡` header
- **Random Spanish fun facts between rounds** — small pool of 30 facts (etymology, regional quirks, cognates); show one on milestone flashes instead of (or alongside) the current celebration box; keeps sessions educational even at milestones
- **Unlockable themes** — lock "ocean" behind 500 total correct, "sunset" behind 1000; display as `[locked]` in settings until earned; gives players a visible goal beyond quests
- **Combo labels** — at streak 3 show `Double!`, streak 5 `On fire!`, streak 10 `Unstoppable!` in the streak display instead of just the colored number; same mechanic, more personality
- **Wrong-answer "close call" detection** — if player's answer differs from correct by only 1 character (Levenshtein distance 1), show `¡Casi! (Almost!)` instead of the generic wrong message; less discouraging for typos
- **Session mood prompt** — on startup after the greeting, one-line: `¿Cómo te sientes hoy? [1] Sharp  [2] Okay  [3] Tired` and adjust: Sharp=hard pool, Tired=easy pool+hints on; skippable with Enter; takes 2 seconds and personalizes the session
- **Rapid Fire personal record ghost** — during a Rapid Fire run, show your previous best score as a ghost target: `best: 23  current: 17  gap: -6`; simple subtraction, high motivational value
