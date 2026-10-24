# Spordle — Findings

Rounds 1 and 2 (both 2026-10-23) added to the 2026-10-13 audit, checked against HEAD `e6749f1`. The first-pass audit (bugs, UX, data, hygiene) was mostly fixed in `ce53138` and is kept at the bottom as an appendix; the open second-pass items from 2026-10-13 are merged into the sorted list below (effort `?` where the old list gave none). "(older item)" marks an entry that extends one already in this list.

Effort: **XS** under 5 min · **S** about 15 min · **M** about an hour · **L** half a day · **?** not estimated. Sorted by value, then effort, then area.

**253 items.** 10 high, 210 medium, 33 low.

## Do these first

1. `number_drill._to_es` is wrong from one million up: `_to_es(1_000_000)` returns `mil mil` and… _[Bug, XS]_
2. `stats.load()` swallows a bad file and `update()` then overwrites it (round 2 lists this); additionally… _[Bug, S]_
3. Rapid Fire burns round time on its own delays _[Bug, S]_
4. Add example sentences _[Learning, S]_
5. Per-word statistics _[Learning, S]_
6. Ser vs Estar and Por vs Para drills _[Learning, S]_
7. Accent placement quiz _[Learning, S]_
8. Word data is Wiktionary-derived (CC BY-SA 4.0) and verbs come from Fred Jehle's database, but the repo… _[Licensing, S]_

## High value

1. [ ] **[XS]** _Bug_ — `number_drill._to_es` is wrong from one million up: `_to_es(1_000_000)` returns `mil mil` and `_to_es(2_000_000)` returns `dos mil mil` (run today). The function only handles thousands (`n >= 1000` branch) and recurses into itself for the thousands count, so anything ≥ 10^6 repeats `mil`. Add `millón`/`millones` (`un millón`, `dos millones`, with `de` before a noun) before extending the hard range beyond 999.
2. [ ] **[S]** _Bug_ — `stats.load()` swallows a bad file and `update()` then overwrites it (round 2 lists this); additionally `load()` merges only known keys, so any extra data a future version writes (e.g. `_last`, `quest_days`) is dropped when an older version saves. Preserve unknown keys with `blank.update(data)` semantics.
3. [ ] **[S]** _Bug_ — Rapid Fire burns round time on its own delays. Each answer is followed by `time.sleep(0.3)` plus a full `U.clear()` redraw while the clock keeps running, so a 30-second round loses ~0.3 s per answer (about 25% of the round at 1 answer/s) and fast typists are penalised for the animation. Show feedback on the next prompt line without sleeping, or pause the clock during the feedback.
4. [ ] **[S]** _Learning_ — Add example sentences. The game teaches isolated words; showing one short sentence with the word blanked (cloze) after reveal is the cheapest big learning gain. Start with 500 easy words from Tatoeba (CC BY 2.0) stored as `"ex": ["Yo estoy en casa.", "I am at home."]`.
5. [ ] **[S]** _Learning_ — Per-word statistics. Today only counters and a `mastered_words` list exist, so "which words do I keep missing" can't be answered beyond the 50-entry SRS queue. Store `{es: {seen, correct, last, avg_ms}}` for every answered word (cap by pruning words not seen in a year) and show a "Weak words" screen from it.
6. [ ] **[S]** _Learning_ — Ser vs Estar and Por vs Para drills. These are the two most-missed distinctions for learners and neither is a vocabulary question. Add a fill-the-blank game with ~100 curated sentences each, tagged with the rule that decides the answer, and show the rule after every answer.
7. [ ] **[S]** _Learning_ — Accent placement quiz. Spanish stress/tilde rules are deterministic; generate "add the tilde" questions from the existing 5,000 words (strip accents, ask where it goes), which uses existing data and fills a real gap (Spordle only strips accents, never teaches them).
8. [ ] **[S]** _Licensing_ — Word data is Wiktionary-derived (CC BY-SA 4.0) and verbs come from Fred Jehle's database, but the repo ships under MIT with attribution only as a README line. `words.json`/`false_friends.json` need a `data/ATTRIBUTION.md` stating the licenses, and the PKGBUILD should install it next to `LICENSE` (CC BY-SA share-alike applies to the data files, not the code).
9. [ ] **[S]** _Reliability_ — Stats and quests files are written in a read-modify-write cycle with no lock. Two terminals open at once (or a cron-run `--export`) lose one session's results. Take an `fcntl.flock` on the file around `update()` or re-load inside the save with a merge.
10. [ ] **[?]** _Learning features_ — Real spaced repetition. Translation keeps a flat list of the last 50 misses and pulls from it 40 % of the time (`translation.py:6,37,91`); nothing is scheduled, nothing else feeds it, and Rapid Fire, Roguelike, High Stakes and Push Your Luck misses are forgotten. Store per-word `{box, due, seen, missed}` in the stats file (Leitner boxes with intervals of 1, 2, 4, 8, 16 days), update it from every game that grades a word, and add a menu entry "Review (N due)" that serves only due words. Mastery then means "reached box 4", not "3 in a row once".

## Medium value

11. [ ] **[XS]** _Bug_ — `pause()` in auto-advance mode sleeps `advance_delay` seconds uninterruptibly; pressing Enter does nothing and typed-ahead input then lands in the next prompt. Use `select`/`termios` to wait for the delay or a keypress.
12. [ ] **[XS]** _Bug_ — `U.clear()` prints raw ANSI regardless of stdout type, so piping the output (`spordle | tee log`) or running in a dumb terminal fills the stream with escape codes. Skip ANSI when `not sys.stdout.isatty()` or `NO_COLOR` is set (the older item covers Wordle colors only).
13. [ ] **[XS]** _Bug_ — `terminal_width()` falls back to 72 when `os.get_terminal_size()` fails, but the layouts assume at least ~80 (separators are `"─"*width`); wrapping looks wrong in narrow panes. Also react to `SIGWINCH` mid-prompt by re-measuring on every `hr()` (it already does) and cap at 100 so wide terminals don't stretch the bar.
14. [ ] **[XS]** _Bug_ — `check_answer` splits accepted answers on `;`, `,`, `(` and `/` only. Glosses written "to be able to" / "can" with " or " are never split; `check_answer("can", ["to be able to or can"])` is False. Add " or " as a separator and test against the real glosses.
15. [ ] **[S]** _Bug_ — `_norm` removes `to ` after lowercasing but before chunk splitting, so `to be (permanent)` passes `be`; correct, but a typed `"to"` + `"be"` order with extra whitespace ("to  be") leaves two spaces and fails. Collapse internal whitespace in `_norm`.
16. [ ] **[S]** _Bug_ — `ask()` treats the typed text `q` as quit and `f` as flip before checking whether it is an answer; Spanish/English words equal to `q` or `f` don't exist, but in type mode a user mid-typo pressing Enter on `f` flips direction and loses the question. Require `:q`/`:f` or confirm flips in type mode.
17. [ ] **[S]** _Bug_ — `Session.right`'s "NEW BEST STREAK" appears whenever `streak > best` and `streak >= 3`, but `best` starts at 0 each session, so the first streak of 3 in every session announces a "new best" even if the all-time best is 20. Seed `best` from stats at session start for the banner.
18. [ ] **[S]** _Bug_ — `checkpoint()` only prints when `total` hits 10/25/50/100 exactly; in games where `total` can skip (Rapid Fire uses its own counters) or after a Flip it never fires. Also no checkpoint beyond 100. Print every 100 after that.
19. [ ] **[S]** _Bug_ — Translation `srs_pool` is rebuilt every round with a list comprehension over up to 5,000 words and `words.index(word)` is O(n); cheap at this size, but the SRS pool also filters to the current difficulty, so lowering difficulty hides due words (older item lists the delete bug). Show how many are hidden.
20. [ ] **[S]** _Bug_ — Mastery counter increments on any correct answer (reveal-mode self-grading) and needs 3 correct *in total since last miss*, not 3 on different days; a word can be "mastered" within one 10-minute session. Require correct answers on 3 different days (or 3 sessions) with spacing.
21. [ ] **[S]** _Bug_ — `stats.current_streak` counts a day when any session ended, including a 1-question session; an achievement or streak that rewards a single answer encourages gaming. Require a minimum (10 questions or 3 minutes) for a streak day.
22. [ ] **[S]** _Bug_ — Quest progress is computed as `now - snapshot` of lifetime counters, so editing or resetting only one game's stats, or an upgrade that renames a key, produces negative-then-clamped progress. Track progress as explicit per-quest counters incremented in `update()`.
23. [ ] **[S]** _Bug_ — `quests._gen` picks three random quests using `random.choice` with no seed, so reopening the app after midnight can generate different quests if the file is lost; and two players sharing a machine get identical files. Seed with the date for deterministic daily quests (and a stable "quest of the day" for sharing).
24. [ ] **[S]** _Bug_ — `quests.get()` calls `_today_raw` which writes the file when the date changed; a read-only call from the menu performs disk writes every first render of the day. Fine, but if the write fails (read-only home) the quests are regenerated randomly on every menu redraw so they change while you look at them. Cache the generated list in memory.
25. [ ] **[S]** _Bug_ — `stats.update(... run=True)` is passed only by the gambling games; Rapid Fire `runs` is incremented elsewhere. Make `runs` part of `Session.end` for all games and drop per-game special cases in `_rounds`.
26. [ ] **[S]** _Bug_ — `stats._export` writes `mastered_words` count but no header documenting units; also CSV is overwritten each export. Append a timestamped file (`export-2026-10-23.csv`) so history isn't lost.
27. [ ] **[S]** _Bug_ — `stats.show` prints "no data" per game, but `_blank()` always includes every KEYS entry; a game added later has no key in old stats files and `data.get(key, {})` works, though `current_streak` etc. assume key presence for others. Add a schema version and migration function.
28. [ ] **[S]** _Bug_ — `Session.end` shows the summary then `input(" Enter to return to menu...")`; Ctrl-D there raises `EOFError` that `_run` catches, but stats were already saved, fine; however Ctrl-C *before* `end()` (during a game) discards the whole session's stats (`S.update` is only called at the end). Save progress on KeyboardInterrupt in `Session` via try/finally.
29. [ ] **[S]** _Bug_ — Sounds: `play_back_and_wait` joins for at most 0.5 s while the tone generation takes ~8 ms but `aplay` startup can exceed it on slow systems; the sound is cut. Use `Popen(...).wait(timeout=1)` rather than a thread join.
30. [ ] **[S]** _Bug_ — Sounds spawn a new `aplay` process per beep with generated WAV bytes piped in; rapid answers (Rapid Fire) can start dozens of processes. Debounce or reuse a single long-lived player process.
31. [ ] **[S]** _Bug_ — Six games pick the next word with `random.choice` and no bag, so the same word can come up twice in a row or repeat within a handful of rounds (Rapid Fire, Roguelike, Push Your Luck, High Stakes, Hangman, Conjugation); only Translation tracks `seen`. Add one shared `U.word_bag(pool)` generator (as HyperTyper does) and use it everywhere.
32. [ ] **[S]** _Bug_ — Rapid Fire depends on `select.select([sys.stdin], ...)`, which does not work on Windows or when stdin is not a socket-like tty; the README does not say Windows is unsupported and the module imports fine, then fails on the first prompt. Guard with a platform check and a clear message, or use `msvcrt` for the timed read.
33. [ ] **[S]** _Bug_ — Rapid Fire's rate (`per_min`) divides by the full limit even when the last answer finished after the buzzer or the player stopped early with `q`; stopped rounds use elapsed time, timed-out ones use `limit`, so a 28 s run and a 30 s run are rated on different clocks. Use the actual elapsed time in both cases.
34. [ ] **[S]** _Bug_ — Rapid Fire's `U.clear()` on each word flickers the whole screen; redraw only the changed lines (move the cursor home and overwrite) as the HyperTyper frame renderer does.
35. [ ] **[S]** _Bug_ — Hangman picks a new word with `random.choice(pool)` and never removes played words; with the Easy pool (5-letter words in the top 500) the pool is small enough that repeats show up within a session. Track seen words per session.
36. [ ] **[S]** _Bug_ — Hangman's `for ... else` branch (`else: won = all(...)`) after `while wrong < 6` is unreachable logic in practice (the loop condition already handled it); remove the redundant `else` to avoid future drift.
37. [ ] **[S]** _Bug_ — Hangman reveals the whole word on loss but never records which letters were close; add "you had N/M letters" in the loss message to show progress.
38. [ ] **[S]** _Bug_ — High Stakes lets you see the word before betting (the prompt prints `prompt` first), so the "confidence" bet is a free information advantage in typed mode; hide the word until after the bet (show only the category or word length) or make the bet relative to a pre-announced difficulty.
39. [ ] **[S]** _Bug_ — Push Your Luck's multiplier increments after every correct answer even when you choose to bank on the second one, but resets only on bank/wrong; a "push" chain therefore reaches x10+ and the pile at that point dwarfs banked points, so the optimal strategy is "always bank at x3". Rebalance (cap multiplier at x5 or make risk grow faster) and add a test on expected value.
40. [ ] **[S]** _Bug_ — Roguelike never changes after a correct answer: there are no upgrades, no rising difficulty and no relics, so "roguelike" is only a lives counter. Rename or add the roguelike elements (older item lists items).
41. [ ] **[S]** _Bug_ — `conjugation._is_irregular` compares only `yo` present and `él` preterite; verbs irregular in the future (`tener`→`tendré`) or imperfect (`ser`, `ir`, `ver`) count as "regular" in the Regular-only filter. Add the future stem and imperfect checks.
42. [ ] **[S]** _Bug_ — Conjugation picks `random.choice(inf_list)` each round then a random cell; with 507 verbs x 5 tenses x 6 persons there's no review of cells you missed. Feed missed (verb, tense, person) triples into the SRS queue.
43. [ ] **[S]** _Bug_ — `conjugation.play` loops with `continue` when `cands` is empty and no sleep; a data bug where every remaining verb has no candidates (a hostile `verbs.json`) would spin the CPU forever. Filter `inf_list` once up front.
44. [ ] **[S]** _Bug_ — Number Drill's quest and stats count "rounds" but a skipped question (blank Enter) is a wrong answer; same issue Rapid Fire fixed. Add skip semantics that don't hurt accuracy.
45. [ ] **[S]** _Bug_ — `false_friends.play` does not respect the Round Limit or Direction settings the same way as others (settings hints say drills only); verify and document per-game support in a table generated from the registry.
46. [ ] **[S]** _Conjugation_ — Add a "which tense is this?" reverse mode: show a conjugated form and ask the tense/person, which trains recognition instead of production.
47. [ ] **[S]** _Conjugation_ — Show irregularity categories after a miss (stem change, yo-go, spelling change) using a `class` field on verbs (`"e>ie"`, `"yo-go"`); the 637 verbs already carry tables, a rules-based classifier can tag them.
48. [ ] **[S]** _Conjugation_ — Weighted selection by verb frequency and by your error rate per tense; today `random.choice(inf_list)` treats `ser` and `agorar` equally within the pool.
49. [ ] **[S]** _Conjugation_ — Let the user choose tenses (checkboxes) instead of the difficulty fixed set (`TENSES`): practicing only the preterite is the most common request.
50. [ ] **[S]** _Content_ — Support more languages by parameterizing data directories (`data/es`, `data/pt`, `data/fr`) and the UI language names; the Spanish-specific parts (`ñ` handling, `vosotros`) become per-language config.
51. [ ] **[S]** _Content_ — Add dialogue snippets for Hangman/Anagram (a short sentence containing the word with the word hidden) to teach usage rather than isolated words.
52. [ ] **[S]** _Content_ — Add a short daily "word of the day" card on the menu header with example sentence, drawn deterministically from the user's weak or next-unlearned band.
53. [ ] **[S]** _Content_ — Include audio-friendly pronunciation hints using simple respelling (`ZHEH-oh`) for the top 500 words to help learners who don't know the stress rules.
54. [ ] **[S]** _Content_ — Track "cognate trap" words (look like English but differ; `false_friends.json` has 40) in Translation as warning tags (⚠ false friend) when they appear.
55. [ ] **[S]** _Data_ — Fix POS tags with a rule + curated overrides and add a test (older items list numerous wrong tags); the 684 `adj` and 3,047 `n` counts hint at residual misclassification (e.g. `grande`, `joven`).
56. [ ] **[S]** _Data_ — Normalize glosses: strip bracketed fragments (`[+de or desde`), cap at 3 senses, mark the primary sense; 73 prose glosses (older item) and truncated parses.
57. [ ] **[S]** _Data_ — Store accepted alternates explicitly (`"alt": ["to want", "to desire"]`) for the ~400 duplicate-gloss words instead of deriving from shared English strings.
58. [ ] **[S]** _Data_ — Add a data build script (`tools/build_data.py`) that regenerates `words.json` from the upstream dataset with documented filters, so fixes aren't hand-edits that vanish on rebuild.
59. [ ] **[S]** _Data_ — Add `data/SCHEMA.md` describing fields, allowed values and invariants (`g` in m/f/x, `pos` in n/v/adj/adv, `cognate` boolean).
60. [ ] **[S]** _Data_ — Include verb tables for the 598 missing verbs generated from regular rules (older item) with a test comparing generated forms to the 507 existing tables to prove the rules.
61. [ ] **[S]** _Data_ — Compact `verbs.json` (564 KB) by storing endings plus stems for regular verbs; irrelevant for speed (9 ms) but halves the package size.
62. [ ] **[S]** _Data_ — Profanity flag + setting (older item) and a "family friendly" default for the Wordle answer list too (check 5-letter words such as `culos`, `putas`).
63. [ ] **[S]** _Data_ — Add frequency rank per word explicitly to the JSON (index in file is the rank today); sorting or filtering would silently change ranks.
64. [ ] **[S]** _Data_ — Remove obsolete spellings (`fué`, `dió`, `vió`) (older item) and add a CI check against a modern RAE-based word list.
65. [ ] **[S]** _Data_ — Add dialect-neutral/Latin American toggles for `vosotros` (older item) and for words like `coger`, `ordenador` vs `computadora`.
66. [ ] **[S]** _Data_ — Version the data files (`"version": 2` header) so stats referencing words (mastered lists) survive word list changes; word ids rather than strings.
67. [ ] **[S]** _Data_ — Replace string keys in stats (`mastered_words` as Spanish strings) with stable ids; renaming or fixing a word's spelling silently resets its progress.
68. [ ] **[S]** _Docs_ — README: refresh the settings table numbering after every settings change by generating it from `_ROWS` (older item notes the table is stale).
69. [ ] **[S]** _Docs_ — README: add a "Learning approach" section describing how the games map to skills (vocab, listening, grammar) and what Spordle does not cover.
70. [ ] **[S]** _Docs_ — README: add screenshots/GIF per game and a quick-start for typed vs reveal mode.
71. [ ] **[S]** _Docs_ — Fold `UPDATE.md` into a CHANGELOG with dates and remove the contradictions (older item).
72. [ ] **[S]** _Docs_ — Add `CONTRIBUTING.md` explaining how to add a game via the registry (add file, register, add quest, add test).
73. [ ] **[S]** _Docs_ — Add `data/README.md` with the build steps, upstream commits and license notes.
74. [ ] **[S]** _Gameplay_ — Add a "Daily Review" mode that serves exactly the words due today across all games (needs the SRS/Leitner item), with a session cap (20 cards) so reviews stay short.
75. [ ] **[S]** _Gameplay_ — Cloze mode with example sentences (needs the sentence data), 4 multiple-choice options built from distractors of the same part of speech and similar frequency.
76. [ ] **[S]** _Gameplay_ — Listening mode: speak the Spanish word with `espeak-ng`/`say`/`spd-say` and ask for the English meaning (and the reverse dictation) (older item); reuse the player-detection from `sounds.py`.
77. [ ] **[S]** _Gameplay_ — Verb conjugation: add imperative, conditional, imperfect subjunctive, participles and gerunds (older item) and a "tense triggers" hint line ("Si yo ___ rico..." -> imperfect subjunctive).
78. [ ] **[S]** _Gameplay_ — Verb conjugation: add a "complete the table" mode where you fill all six persons of one verb/tense in sequence; today it asks one random cell at a time.
79. [ ] **[S]** _Gameplay_ — Verb conjugation: stem-changing and spelling-change categories (e->ie, o->ue, c->qu, z->c) with the category named after each answer, so irregularity becomes a pattern rather than 637 memorized exceptions.
80. [ ] **[S]** _Gameplay_ — Pronoun drills: direct/indirect object pronouns and their order (`se lo doy`), which many learners fail; short sentence transformations generated from templates.
81. [ ] **[S]** _Gameplay_ — Article and plural drill: `el/la/un/una`, `los/las` with pluralization rules (-s, -es, -ces, accent drop on -ión); generate from `words.json` nouns with the `g` field.
82. [ ] **[S]** _Gameplay_ — Adjective agreement drill: choose the correct form (`rojo/roja/rojos/rojas`) given the noun; needs gender data and the `adj` words.
83. [ ] **[S]** _Gameplay_ — Time and date drill: speak/typing clock times (`las tres y cuarto`), dates and days; extends Number Drill's `_to_es`.
84. [ ] **[S]** _Gameplay_ — Prices and money in Number Drill (older item mentions years and `$3.50`), and phone numbers read digit by digit.
85. [ ] **[S]** _Gameplay_ — Prepositions with verbs (`pensar en`, `soñar con`, `depender de`, `acordarse de`): a fixed list of ~150 pairs, a quick multiple-choice drill.
86. [ ] **[S]** _Gameplay_ — Idioms and proverbs mode with literal vs real meaning (`estar en las nubes`); small curated list, fun for screenshots.
87. [ ] **[S]** _Gameplay_ — Regional variants: tag vocabulary with region (Spain/Mexico/Argentina), set a preferred region and accept all variants when typing, show the variant note after reveal.
88. [ ] **[S]** _Gameplay_ — Pronunciation tips: add IPA or a simple respelling for the 500 easy words and show on reveal (data from Wiktionary, same license).
89. [ ] **[S]** _Gameplay_ — Minimal pairs (`pero/perro`, `ano/año`, `cazar/casar`) as a listening or spelling quiz, since these cause real errors.
90. [ ] **[S]** _Gameplay_ — Thematic decks (food, travel, body, family, work) selectable as a filter for Translation/Rapid Fire; tag words by theme with a small script from the Wiktionary categories.
91. [ ] **[S]** _Gameplay_ — Part-of-speech filter (nouns only, verbs only, adjectives only) for vocab games; the field already exists (needs POS cleanup).
92. [ ] **[S]** _Gameplay_ — "Next 500 words" progression: unlock frequency bands as the previous band reaches 80% mastery, instead of the difficulty enum alone.
93. [ ] **[S]** _Gameplay_ — Sentence builder: unscramble a shuffled Spanish sentence (word order practice) from the example-sentence data.
94. [ ] **[S]** _Gameplay_ — Translation of full sentences with fuzzy match (edit distance and key-word check) for Hard mode.
95. [ ] **[S]** _Gameplay_ — Story/reader mode: a 100-word graded paragraph with tap-to-reveal words; uses the frequency data to pick comprehensible text.
96. [ ] **[S]** _Gameplay_ — Boss round for each streak milestone: 10 questions drawn only from your weakest words.
97. [ ] **[S]** _Gameplay_ — Time-pressure variants for Translation (5 s per card) to build recall speed; Rapid Fire already has a clock, but Translation has none.
98. [ ] **[S]** _Gameplay_ — Wordle variants: 4- and 6-letter word lengths, daily puzzle number + share grid (older item), and a "definition shown" practice mode that tells the English meaning.
99. [ ] **[S]** _Gameplay_ — Hangman: use categories and show the English clue as a hint option; use full vocabulary words (older item says only 5-letter words).
100. [ ] **[S]** _Gameplay_ — Roguelike: items/relics between rounds (skip, 50/50, reveal a letter), actual build variety; today it is a lives counter over Translation.
101. [ ] **[S]** _Gameplay_ — High Stakes: scale bet cap (older item) and add a loan/insurance mechanic; gambling modes teach nothing unless answers are auto-graded (typed mode).
102. [ ] **[S]** _Gender Drill_ — 359 of the 1,099 nouns with an explicit gender are marked `x` (both genders) and are silently skipped by `_gender()`, so a third of the curated data never appears. Add a "both" card ("el/la estudiante") that teaches the pattern, and an explanation line on `-ista`, `-ante` words.
103. [ ] **[S]** _Gender Drill_ — Extend the exercise to indefinite articles (`un/una`) and plural articles (`los/las`), and to agreement ("el problema difícil" vs "la mano difícil") since the single el/la choice is easy to game at 50% chance.
104. [ ] **[S]** _Gender Drill_ — Add a "why" line after each answer using the ending rule or an exception tag (`-ma words are mostly masculine`, `mano is feminine`), stored as `"why"` in `words.json` for the ~100 exceptions.
105. [ ] **[S]** _Gender Drill_ — `_infer_gender` still guesses for nouns without `g` (1,948 of them): add a coverage report script listing nouns whose inferred gender would differ from a Wiktionary-derived gender field so the data can be completed.
106. [ ] **[S]** _Hangman_ — Hangman and Anagram share the 5-letter ASCII pool; offer a "longer words" option using `words.json` entries up to 9 letters, and show part of speech as a hint button costing a life.
107. [ ] **[S]** _High Stakes_ — Allow side bets (confidence in 3 levels) that scale the payout, and a "chip loan" lifeline; and make bets visible in the stats (average bet, biggest win) beyond peak chips.
108. [ ] **[S]** _Learning_ — Leitner/SM-2 scheduling for all vocabulary games (older item "real spaced repetition"); store `due` dates and show "12 due today" on the menu.
109. [ ] **[S]** _Learning_ — Review forecast screen: bar chart of reviews due in the next 7 days.
110. [ ] **[S]** _Learning_ — "Lapses" tracking: words answered wrong after being mastered are flagged leeches after 4 lapses and get extra hints.
111. [ ] **[S]** _Learning_ — Confidence rating in reveal mode (again/hard/good/easy, Anki style) instead of binary got-it/missed; feeds the scheduler.
112. [ ] **[S]** _Learning_ — Daily goal setting (minutes or questions) with a progress bar on the menu; quests are fixed at three.
113. [ ] **[S]** _Learning_ — Streak freeze/rest day: one miss per week doesn't break the login streak (stops the all-or-nothing abandonment).
114. [ ] **[S]** _Learning_ — XP and levels based on correct answers weighted by difficulty and word rank; show the level in the menu header.
115. [ ] **[S]** _Learning_ — Weekly summary printed on first launch of the week: words learned, accuracy, time, best game.
116. [ ] **[S]** _Learning_ — "Words learned" estimate based on mastered words per frequency band (vocabulary size estimator, like testyourvocab).
117. [ ] **[S]** _Learning_ — Placement test on first run: 30 adaptive questions to set the difficulty automatically.
118. [ ] **[S]** _Learning_ — Mistake journal: the last 30 mistakes with what you typed vs the answer, reviewable as a list or a drill.
119. [ ] **[S]** _Learning_ — Typed-answer hint ladder: after a wrong typed answer, show the first letter, then half the word, before revealing.
120. [ ] **[S]** _Learning_ — Immersion toggle: show game UI text in Spanish (menu labels, prompts) once the user opts in; most strings are English today.
121. [ ] **[S]** _Learning_ — Include the example sentence translation toggle to avoid dependence on English.
122. [ ] **[S]** _Learning_ — Etymology/cognate note for words flagged `cognate` ("same in English"), so free points teach a pattern.
123. [ ] **[S]** _Learning_ — False cognate list expansion from 40 to 200 entries (older item says known; list candidates from Wiktionary "false friends" categories).
124. [ ] **[S]** _Learning_ — Import/export of decks: read Anki CSV/TSV into custom word lists, export mistakes for Anki.
125. [ ] **[S]** _Learning_ — User word lists: a `~/.config/spordle/words/*.txt` convention (like HyperTyper's) so learners add their own vocabulary and it joins Translation/Rapid Fire.
126. [ ] **[S]** _Number Drill_ — Numbers above 1,000 also lack the accepted spelling variants in `_variants` (`dieciséis` vs `diez y seis` only up to 29) and the common regional forms `mil quinientos` vs `mil y quinientos` mistakes; add a table-driven test comparing `_to_es` against a reference for 0-9,999 and 1,000,000-3,000,000.
127. [ ] **[S]** _Number Drill_ — Add ordinals (`primero`, `tercero`, `décimo`) with apocope (`primer`, `tercer`), fractions (`un medio`, `tres cuartos`) and decimals (`tres coma cinco`); today the mode is cardinal integers 0-999 only.
128. [ ] **[S]** _Number Drill_ — Show numbers the way Spanish writes them (`1.000`, `3,5`, `€12,50`) in the prompt for some questions: reading locale-formatted numbers is a skill the drill never trains.
129. [ ] **[S]** _Number Drill_ — Dates and years as a mode (`el quince de octubre de dos mil veintiséis`), days of week and months in context; reuses `_to_es` and a small weekday/month table.
130. [ ] **[S]** _Number Drill_ — Telling time (`las tres y cuarto`, `la una menos diez`) with a clock-face prompt; the plural/singular `es la una` vs `son las dos` is a classic stumbling block.
131. [ ] **[S]** _Packaging_ — `pyproject.toml` with a `spordle` console script (older item) so `pipx install` works and data files ship as package data.
132. [ ] **[S]** _Packaging_ — PKGBUILD `pkgver()` uses commit count while a `LICENSE` is installed; add a `check()` running the tests and `.SRCINFO` regeneration in a release script.
133. [ ] **[S]** _Packaging_ — The launcher script is a heredoc in the PKGBUILD; ship a `bin/spordle` file in the repo instead so non-Arch installs share it.
134. [ ] **[S]** _Packaging_ — Provide a Flatpak/AppImage or a Nix flake only if non-Arch users appear; document `python3 spordle.py` install steps for macOS (afplay) in the README.
135. [ ] **[S]** _Packaging_ — Add a man page and shell completion for the CLI flags once they exist.
136. [ ] **[S]** _Push Your Luck_ — Add a visible risk readout: probability estimate from your accuracy on this difficulty so the player can compare it to the pile size, plus a "quit with 80%" suggestion; the mechanic currently hides the odds.
137. [ ] **[S]** _Quality_ — Add type hints and run `mypy`; the dict-shaped stats and settings make typos in keys invisible (`best_streak` vs `bestStreak`).
138. [ ] **[S]** _Quality_ — Replace the global mutable `SETTINGS` dict with a dataclass; games read `U.SETTINGS["x"]` by string key (a KeyError on typos at runtime).
139. [ ] **[S]** _Quality_ — Split `utils.py` (17 KB) into `ui.py` (colors, headers), `io.py` (ask, yn_input), `data.py` (load, pools), and `session.py`.
140. [ ] **[S]** _Quality_ — Remove circular imports (`utils.Session.end` imports `stats` inside the method, `stats` imports `quests` inside `update`); pass dependencies or use a small event bus.
141. [ ] **[S]** _Quality_ — Standardize on one input helper (`prompt()`) that handles EOF/Ctrl-C and the `q` convention so each game doesn't re-implement it.
142. [ ] **[S]** _Quality_ — Replace `print`-heavy rendering with a small `Screen` class that builds lines and prints once per frame; makes UI tests possible and prevents partial redraws.
143. [ ] **[S]** _Quality_ — Run `ruff`/`flake8` and fix unused imports; the games import the same names (`BOLD, RESET`) piecemeal.
144. [ ] **[S]** _Quality_ — Add logging (`~/.local/state/spordle/spordle.log`) of unexpected exceptions, since `_run` swallows only Ctrl-C/EOF but any other error just dumps a traceback.
145. [ ] **[S]** _Quality_ — Add a `--debug` flag that shows the data for each question (word id, pool index) for diagnosing data issues.
146. [ ] **[S]** _Quality_ — Introduce a `Game` base class (or protocol) with `setup()`, `next_question()`, `grade()` and let a single loop handle sessions, quit keys, round limits and stats; 12 games re-implement the same while-loop and quit handling.
147. [ ] **[S]** _Quality_ — Give every game a declared capability set in the registry (`supports_direction`, `supports_rounds`, `answer_modes`) and generate the Settings hints and the README table from it; the hints are currently hard-coded strings that drift.
148. [ ] **[S]** _Quality_ — Collect all user-visible strings in one module (`strings.py`) so adding a language for the UI, fixing a typo or testing output is a single-file task.
149. [ ] **[S]** _Quality_ — `U.ask` is the single place that handles `q`/`f`/typed; extract grading into `grade(raw, answers, mode) -> Grade` returning an enum with partial credit (accent mistake, near miss) so games can react differently.
150. [ ] **[S]** _Quality_ — `stats.update(**extra)` merges unknown keys with max/replace semantics based on the Python type; typos in key names silently create new fields. Declare the allowed fields per game.
151. [ ] **[S]** _Quests_ — Weekly quests and "boss" quests (complete 50 rounds across 3 games) with bigger rewards, and quest rerolls (once a day) so an unwanted quest isn't blocking the 3/3 reward.
152. [ ] **[S]** _Quests_ — Make quest targets adaptive: scale `n` to the player's average daily volume from stats (a 15-correct quest is trivial for heavy users and daunting for new ones).
153. [ ] **[S]** _Rapid Fire_ — Show a live score and streak in the header line (currently `score correct/total` only) and a speed meter (answers per minute) so the player sees pace; the end screen computes it but the run doesn't.
154. [ ] **[S]** _Roguelike_ — Introduce real roguelike structure: floors with bosses (a 10-word gauntlet), relics (extra life, skip, hint), and seeded runs for sharing; the current mode is "lives until you miss".
155. [ ] **[S]** _Settings_ — Settings screen is a 17-row list requiring numbers; add `j/k` navigation and left/right to change values, with a short description line only for the focused row (older UX item proposes this; here is the input model).
156. [ ] **[S]** _Settings_ — Profiles: `--profile NAME` selects a separate set of settings/stats/quests directories (family sharing one machine, or separate Spanish and Portuguese study).
157. [ ] **[S]** _Stats_ — Per-word progress dashboard: list words by status (new, learning, mastered, leech) with counts per frequency band (top 500/1,000/2,000), plus the "words learned" estimate; stats currently only count totals and mastered words.
158. [ ] **[S]** _Stats_ — Accuracy by tense/person for Conjugation and by gender ending for Gender Drill, so the stats say *what* to practice instead of how much.
159. [ ] **[S]** _Tech_ — Replace the `input()`-centric flow with a thin `prompt_toolkit`/`curses` layer optional-installed for single-key choices, history, and live timers; keep the stdlib fallback so the AUR package stays dependency-free.
160. [ ] **[S]** _Tech_ — Run games with a deterministic RNG when `SPORDLE_SEED` is set, and record the seed in the session summary, to reproduce bugs and write end-to-end tests.
161. [ ] **[S]** _Tech_ — Add structured error logging (`~/.local/state/spordle/log`) and a `--debug` flag; a traceback in a game currently exits the process with no record beyond the terminal.
162. [ ] **[S]** _Tech_ — Memoize `words.json` parse (263 KB) and `verbs.json` (564 KB) once per process via `lru_cache`; `U.load` re-reads the file each time a game starts (measured as small, but easy and avoids stutters on slow disks).
163. [ ] **[S]** _Tech_ — Validate `words.json`/`verbs.json` against JSON Schemas at test time (types, allowed `pos`, `g` values, tense keys, six persons) with clear messages for data PRs.
164. [ ] **[S]** _Tech_ — CI: run tests on Linux/macOS with Python 3.8-3.13 and lint with `ruff`; add a data-diff check that fails if `words.json` changes without a regenerated `data/README` summary.
165. [ ] **[S]** _Tech_ — Provide `spordle --export-anki` creating an Anki-compatible TSV/APKG of your missed and mastered words, closing the loop with spaced-repetition tools.
166. [ ] **[S]** _Tests_ — Test `strip_accents`/`match` with the full list of accent collisions (`aún/aun`, `bebé/bebe`) to pin behavior.
167. [ ] **[S]** _Tests_ — Test quests: generation uniqueness (no two quests per game), progress with a stats snapshot, midnight rollover with a patched `date.today`.
168. [ ] **[S]** _Tests_ — Test `stats.update` merge semantics (max for scalars, replace for lists) and achievements unlocking exactly once.
169. [ ] **[S]** _Tests_ — Test settings validation by writing hostile JSON (`{"difficulty": "Hard", "rounds": 7, "rf_time": 45}`) and asserting defaults.
170. [ ] **[S]** _Tests_ — Test each game's `play()` with scripted `input()` for one right and one wrong answer, asserting stats counters; currently only pure helpers are tested.
171. [ ] **[S]** _Tests_ — Snapshot tests for `game_header` and `summary` output at width 40/80/120 with ANSI stripped.
172. [ ] **[S]** _Tests_ — Data tests (older item) as a CI job: no duplicate `es`, no `[`/`]` in glosses, every verb has all six persons for all tenses.
173. [ ] **[S]** _Tests_ — Property test for `_to_es`: round-trip against a reference implementation (`num2words` in a dev-only check) for 0-999,999.
174. [ ] **[S]** _Tests_ — Run the test suite on Python 3.8 through 3.13 in CI (the README promises 3.8+).
175. [ ] **[S]** _Tests_ — Test that every sound name used by `sfx(...)` exists in `sounds.py` (a typo is swallowed by the blanket `except Exception` in `sfx`) by scanning the source with `ast`.
176. [ ] **[S]** _Tests_ — Test that every game in the registry has a `play` function, appears in the stats `KEYS`, and has a quest pool entry or an explicit opt-out.
177. [ ] **[S]** _Translation_ — Show example collocations ("tener hambre") for verbs and top-frequency words, from a small curated field `"ex"`, because isolated translation misses idiomatic usage.
178. [ ] **[S]** _Translation_ — Provide an "I knew it but typed it wrong" override on typed ✗ results (accept as correct for stats, mark as typo for SRS), so a typo does not demote a known word.
179. [ ] **[S]** _Translation_ — Per-direction stats: Spanish→English and English→Spanish accuracy tracked separately (`mastered_words` conflates them), since recognition and recall are different skills.
180. [ ] **[S]** _Translation_ — Weighted random selection by frequency rank within the difficulty pool (more common words more often) instead of uniform over 500/2,000/5,000, which over-samples rare words in Hard.
181. [ ] **[S]** _UI_ — Draw the Wordle keyboard in QWERTY with the Spanish `ñ` key and highlight it; Spanish Wordle needs `ñ` available in the layout.
182. [ ] **[S]** _UI_ — Add box-drawn cards for the question/answer instead of loose lines, with the direction label on the card edge.
183. [ ] **[S]** _UI_ — Show a progress ring/bar for mastered words out of 5,000 on the stats screen with per-band breakdown (top 500 / 2,000 / 5,000).
184. [ ] **[S]** _UI_ — Heatmap calendar of days practiced (last 12 weeks) rendered with block characters in My Stats; uses the session history item.
185. [ ] **[S]** _UI_ — Color-code difficulty consistently (easy green, medium yellow, hard red) in every header (a helper exists: `diff_color`).
186. [ ] **[S]** _UI_ — Add themes: solarized, nord, dracula (themes are 5-tuples; a table of 8 more is cheap) and a high-contrast theme.
187. [ ] **[S]** _UI_ — Terminal bell/flash on wrong answers option (`\033[?5h` reverse video flash) for visual feedback with sounds off.
188. [ ] **[S]** _UX_ — Add `?` / `help` in every prompt listing the available keys (`q`, `f`, Enter) since each game has slightly different controls.
189. [ ] **[S]** _UX_ — Add a global `Ctrl-C` confirmation that saves stats ("Quit and save? [Y/n]") instead of dropping the session silently.
190. [ ] **[S]** _UX_ — Add `--game NAME`, `--difficulty`, `--no-color`, `--version` and `--stats` command-line flags via `argparse`; the AUR launcher passes `"$@"` but `spordle.py` ignores arguments.
191. [ ] **[S]** _UX_ — Remember the last played game and offer "press Enter to continue with <game>" at the menu.
192. [ ] **[S]** _UX_ — Menu number shortcuts: accept the game name prefix (`wo` for Wordle, `ho` for Hangman) in addition to numbers.
193. [ ] **[S]** _UX_ — Show the current difficulty and answer mode in each game's header; hints about why a game behaves differently are in Settings only.
194. [ ] **[S]** _UX_ — Add a short tutorial on first run explaining reveal vs type mode, the controls and the quests.
195. [ ] **[S]** _UX_ — Add configurable Enter-to-continue behaviour: a "fast mode" that merges the feedback and next question into one screen.
196. [ ] **[S]** _UX_ — Replace "Press Enter to play..." banner with an automatic 1 s splash (older item) controlled by a setting.
197. [ ] **[S]** _UX_ — Accessibility: screen-reader-friendly mode (no box drawing, no emoji, plain text labels) and a setting to disable animations/sound-like beeps.
198. [ ] **[S]** _UX_ — Add a `bell` option (terminal `\a`) as sound fallback when no player is installed (older item lists player candidates).
199. [ ] **[S]** _UX_ — Show elapsed time per game in the footer and a per-question timer option for self-timing.
200. [ ] **[S]** _UX_ — Right-align or color-code the ES/EN prompt languages so direction is obvious at a glance (flag emoji optional).
201. [ ] **[S]** _UX_ — Provide an "undo last answer" for self-graded mode (mis-pressed `n`), limited to the previous card.
202. [ ] **[S]** _UX_ — Let users edit/skip a bad word ("this gloss is wrong") and write a report line to a local `reports.txt` for fixing data later.
203. [ ] **[S]** _Wordle_ — Add a Spanish keyboard row with `ñ` and handle `ñ` input; `five_letter()` returns ASCII-only words so `ñ` never appears and the answer set loses words like `niños`, `año` (3 letters, n/a) `sueño`.
204. [ ] **[S]** _Wordle_ — Separate answer list (common words) from the accepted-guess list (all valid 5-letter words, incl. accented) to avoid "not in word list" frustration; accepted list can come from a RAE-based corpus.
205. [ ] **[?]** _Bugs and rough edges_ — Reveal mode needs three Enters per question. `ask()` waits for Enter to reveal, `yn_input` waits for "Got it?", then `Session.advance` calls `pause()` ("Enter to continue") unless Auto-Advance is on (`utils.py:264-282`, `:431-438`). The user has already seen the answer and rated it, so the third Enter is pure friction. Skip `pause()` when `answer == "reveal"` (keep it for typed mode, where the ✓/✗ needs a beat to read), or fold "Got it?" and continue into one prompt: Enter = got it and next, `n` = missed and next.
206. [ ] **[?]** _Bugs and rough edges_ — A corrupt `stats.json` is silently replaced. `stats.load()` returns `_blank()` on `ValueError` (`stats.py:36-49`), and the next `update()` saves over the damaged file, so a half-written or hand-edited file wipes all-time stats, achievements and mastered words with no warning. Rename the bad file to `stats.json.bak` before returning the blank (same for `quests.json`), and print one line saying so.
207. [ ] **[?]** _Bugs and rough edges_ — Typed answers reject articles. `_norm` only strips a leading `to ` (`utils.py:151-155`), so `the house` for `house` and `la casa` for `casa` are marked wrong in Type mode, although both are exactly what a learner types for nouns. Strip a leading `the/a/an` (EN) and `el/la/los/las/un/una` (ES) from both sides before comparing.
208. [ ] **[?]** _Bugs and rough edges_ — Typed answers have no near-miss grace. A single dropped letter in `refrigerador` is a flat ✗, which is why people stay in Reveal mode. Accept edit distance 1 on words of 6+ letters with a visible "(close: refrigerador)" note that counts as correct, behind a Settings toggle ("Typo tolerance"). `difflib.SequenceMatcher` from the stdlib is enough.
209. [ ] **[?]** _Bugs and rough edges_ — Conjugation only covers 507 of the 1,105 verbs in the vocabulary. `verbs.json` holds 637 verbs, and 598 verbs from `words.json` have no table, including `haber` (frequency rank 2), `cambiar`, `cantar`, `considerar` and `quitar`; 593 of the 598 are regular-looking -ar/-er/-ir. The game silently skips them (`conjugation.py:46-52`). Generate regular forms from rules for the missing verbs (the five existing tenses are all rule-driven for regular verbs), and add `haber` and any other missing irregulars by hand, then assert coverage in a test.
210. [ ] **[?]** _Bugs and rough edges_ — False Friends always self-grades. It uses reveal + `yn_input` even when Answer Mode is "type" (`false_friends.py:17-27`), unlike every other vocab game. Make it multiple choice: show the false friend plus 4 real meanings (the right one and 3 `real_en` values from other entries), 1-4 to answer, auto-graded.
211. [ ] **[?]** _Data quality_ — Offensive words are in the practice pool with no switch. 15 entries including `follar`, `culo`, `puto`, `maricón`, `pendejo`, `zorra`, `pene`, `vagina`, `joder` can come up in Rapid Fire, Hangman or Translation (e.g. at rank 828 and 1516) on a shared screen. Add `"tag": "vulgar"` to them and a Settings toggle "Vulgar words" that defaults to off; the filter is one list comprehension in `U.load`-level code.
212. [ ] **[?]** _Data quality_ — Some glosses miss the meaning learners need. `polla` = "young hen", `cabrón` = "billy goat", `pendejo` = "pubic hair", `coger` = "to take" (offensive in much of Latin America), `puto` = "fucking". Reword (or flag) so the first gloss is the usual one, and add a regional note field (`"note": "vulgar in Mexico"`) shown after reveal.
213. [ ] **[?]** _Data quality_ — Obsolete and duplicate spellings are in the list as separate words. `fué`, `dió`, `vió` (pre-2010 orthography, now incorrect), and five accent-collision pairs: `aún`/`aun`, `bebé`/`bebe`, `adónde`/`adonde`, `revolver`/`revólver`, `carne`/`carné`. In accent-insensitive mode the pairs are indistinguishable, so one is always wasted and EN→ES grading has two "right" answers. Remove the old spellings and merge the pairs.
214. [ ] **[?]** _Learning features_ — Keep session history so progress is visible. Stats only hold lifetime totals (`stats.py:27`), so improvement can't be seen. Append one JSON line per finished session to `history.jsonl` (`date, game, correct, total, seconds, difficulty, direction`), then show on My Stats: "last 14 days" bars, accuracy trend per game, and "practiced 5 of the last 7 days". Cap and rotate the file at 5,000 lines.
215. [ ] **[?]** _Learning features_ — Add the missing tenses. `verbs.json` has Present, Preterite, Imperfect, Future and Present Subjunctive only. The same source dataset (Fred Jehle) also has Condicional, Imperfect Subjunctive, Imperativo, Participio and Gerundio, which intermediate learners are expected to know. Gate them by difficulty in `TENSES` (`utils.py:101`) and add a "Participle & gerund" mini-mode (`hablado`, `hablando`).
216. [ ] **[?]** _Learning features_ — Listening practice. If `espeak-ng`, `spd-say` (Linux) or `say` (macOS) is installed, add key `s` after reveal to speak the Spanish word, and a "Dictation" mode that speaks a word and asks you to type it. It is the biggest skill the game doesn't touch, and it needs no bundled audio.
217. [ ] **[?]** _Learning features_ — Wordle extras beyond hard mode: a copyable result grid (🟩🟨⬛ plus "Spordle #<days since launch> 4/6") sent to `wl-copy`/`xclip`/`pbcopy` when available, and a *daily* streak (consecutive days solved, stored from `last_daily`) next to the existing `win_streak`, which counts random games too (`wordle.py:50-57`).
218. [ ] **[?]** _Packaging tests repo_ — Data regression tests. `test_data` checks a handful of words; it would not have caught any item in "Data quality". Add checks: no duplicate `es`/`strip_accents(es)` pairs, every `g` is one of `m/f/x`, every `v` gloss starts with `to `, no `[`/`]` in glosses, every verb in the first 1,000 words has a conjugation table, and no entry tagged `vulgar` appears when the filter is off.
219. [ ] **[?]** _UX and accessibility_ — Single-keypress input. Gender Drill (`1`/`2`/`m`/`f`), yes/no prompts, Hangman letters and menu picks all wait for Enter. Add a `getch()` in `utils.py` using `termios` + `tty.setcbreak` (stdlib, with `input()` fallback when stdin isn't a TTY), and use it where the answer is one key. It roughly halves the keystrokes in the fastest drills.
220. [ ] **[?]** _UX and accessibility_ — Colors carry all the meaning in Wordle. Green, yellow and gray text on the same background (`wordle.py:_render`) is unreadable to some color-blind players and invisible with `NO_COLOR`. Add an Accessibility setting that prints markers as well (`[A]` correct, `(A)` present, ` A ` absent), and honor the `NO_COLOR` environment variable by selecting the `mono` theme at startup.

## Low value / nice to have

221. [ ] **[XS]** _Cleanup_ — `_PRAISE` and `_CONSOLE` lists mix Spanish and English; put them in a `phrases.py` so they can be localized or extended.
222. [ ] **[XS]** _Cleanup_ — `_CHECKPOINTS` uses fixed totals; generate the messages from a function so they scale to 250/500.
223. [ ] **[XS]** _Cleanup_ — `U.five_letter()` re-filters 5,000 words on every call; memoize with `lru_cache` like `_es_by_gloss`.
224. [ ] **[XS]** _Cleanup_ — `load(filename)` reads and parses JSON on every call (words.json is 263 KB); cache with `lru_cache` and return copies where mutated.
225. [ ] **[XS]** _Cleanup_ — `quests._POOL` descriptions are hand-written strings that duplicate the `game`/`key`/`n` fields; build the text from the fields.
226. [ ] **[XS]** _Cleanup_ — `stats._ACHIEVEMENTS` lambdas silently swallow all exceptions in `_check_achievements` (`except Exception: pass`); log them.
227. [ ] **[XS]** _Cleanup_ — `settings._ROWS` has hint strings that restate the setting name; trim hints to what the label cannot say.
228. [ ] **[XS]** _Cleanup_ — Rename `U` and `S` aliases imported in every file to full module names or a consistent `from games import utils as u`.
229. [ ] **[XS]** _Cleanup_ — `utils.py` constants mix UI strings and thresholds (`_CHECKPOINTS`, `_PRAISE`); move to `strings.py` and `config.py` to keep `utils.py` for helpers.
230. [ ] **[XS]** _Cleanup_ — `UPDATE.md` (10 KB) reads as a build diary; convert to `CHANGELOG.md` with dated entries and delete resolved "known issues".
231. [ ] **[S]** _Feature_ — Multiple profiles (`--profile alice`) with separate stats/settings, for shared computers or families.
232. [ ] **[S]** _Feature_ — Terminal "TUI mode" using curses/textual for single-key input and mouse; much of the friction (Enter everywhere) goes away (older item proposes `getch()` first).
233. [ ] **[S]** _Feature_ — Web/PWA front end reading the same JSON data so practice works on a phone; the data is already JSON.
234. [ ] **[S]** _Feature_ — Spaced-repetition sync with Anki via AnkiConnect (push mastered/missed words).
235. [ ] **[S]** _Feature_ — Daily reminder via notify-send/systemd timer when no practice has happened by a set hour.
236. [ ] **[S]** _Feature_ — Podcast/subtitle listening: link words in `words.json` to their most common appearances in a corpus; large project.
237. [ ] **[S]** _Feature_ — Pronunciation check using speech recognition (Vosk offline) for single words; heavy dependency, optional extra.
238. [ ] **[S]** _Feature_ — Daily streak reminders using `notify-send` via a systemd user timer ("Practice Spanish today?") with a `--remind` flag to install the unit.
239. [ ] **[S]** _Feature_ — Ghost opponents: compare your session against your own last week's average per game on the summary screen.
240. [ ] **[M]** _Feature_ — Conversation practice scripted dialogs with branching choices (restaurant, directions) with auto-graded responses.
241. [ ] **[M]** _Feature_ — Two-player local mode where players alternate rounds on the same word list and compare scores.
242. [ ] **[?]** _Bugs and rough edges_ — Practice time includes idle time. `Session.end` uses `time.time() - self.start` (`utils.py:442`), so a terminal left on a question counts as study, which inflates `total_seconds` and the hours on the Stats screen. Accumulate time only between "question shown" and "answer entered", capped at ~60 s per question.
243. [ ] **[?]** _Bugs and rough edges_ — High Stakes turns every bad bet into 1 chip silently (`stakes.py:38-43`): `all`, `max`, a typo, or a blank Enter all become a 1-chip bet with no message. Re-ask on junk, and accept `all`/`max` and plain Enter as "default bet".
244. [ ] **[?]** _Bugs and rough edges_ — Favorites are stored as display labels (`settings.py:_ALL_GAMES = list(LABELS.values())`, `spordle.py:_favorites`). Renaming a game label in `registry.py` silently drops the user's saved favorites. Store registry keys and map to labels for display.
245. [ ] **[?]** _Bugs and rough edges_ — "Sounds: ON" can be a lie. `sounds._PLAYER` only looks for `aplay`/`afplay` (`sounds.py:5`); on a PipeWire/PulseAudio desktop without `alsa-utils` nothing plays and Settings still shows ON. Add `pw-play`, `paplay` and `play` (sox) to the candidates, and show `ON (no player found)` in Settings when `_PLAYER is None`.
246. [ ] **[?]** _Data quality_ — Part of speech is still wrong for many adjectives: `grande`, `joven`, `fuerte`, `real`, `normal`, `común`, `dulce`, `simple`, `total`, `natural`, `local`, `central`, `doble` are all tagged `n`. They are harmless for gender (the heuristic skips them) but make the Anagram hint ("a noun") and any future POS hint wrong. Four `v` entries lack the `to ` gloss (`hecho`, `fué`, `dió`, `vió`) and two non-verbs have one (`adónde`, `adonde`: "to where").
247. [ ] **[?]** _Data quality_ — Gender Drill difficulty doesn't track difficulty. 1,099 nouns carry an explicit `g`; the other 1,948 get their gender from the ending (`-o` is "el", `-a` is "la"), so most rounds are free. Make Hard mean "the ending doesn't give it away": only explicit-`g` nouns that end in `-e`, a consonant, or are classic exceptions (`día`, `mano`, `mapa`, `foto`).
248. [ ] **[?]** _Data quality_ — Number Drill's hard range still ends at 999 (`number_drill.py:_RANGES`), although `_to_es` is now tested up to 31,000. Extend hard to 9,999 and add a fourth "years & prices" mode (1985, 2026, `$3.50` = "tres con cincuenta") for realistic practice.
249. [ ] **[?]** _Learning features_ — Weekly goal on top of daily quests: "practice 5 of 7 days" with a progress line on the menu header and a "Perfect Week" achievement. The quest reward today is only a counter (`quest_days`, three days earns Quest Hunter), which is thin compared with the streak and quest UI around it. Uses the session history above.
250. [ ] **[?]** _Packaging tests repo_ — Add a GitHub Actions workflow running `python3 tests/test_pure.py` on Python 3.8 and 3.12 (the README promises 3.8+; `str.removeprefix` or `match` slipping in would break it unnoticed).
251. [ ] **[?]** _Packaging tests repo_ — AUR hygiene: commit a `.SRCINFO`, add a `check()` function to `PKGBUILD` that runs the tests, and consider `pyproject.toml` with a `[project.scripts] spordle` entry so `pipx install .` works on non-Arch systems.
252. [ ] **[?]** _Packaging tests repo_ — Update `todo.md`/`FINDINGS.md` structure: the Round 1 sections above have no checkboxes, so it's impossible to see what remains. Tick or delete each bullet in a single pass now that most are fixed, and keep this file as the only open-work list.
253. [ ] **[?]** _UX and accessibility_ — Session end always adds another Enter (`utils.py:448`, `Enter to return to menu...`) right after the summary. If the user just pressed Enter to advance, show the summary and go straight back on the next key press, or return to the menu with the summary kept at the top.

---

## Appendix: first-pass audit (2026-10-13), mostly fixed in `ce53138`

_Kept for the data tables and measurements. Not resorted._

### Do these first (top 5)

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

### 1. Bugs

#### Wrong behavior (fix these)

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

#### Gender Drill (own section — it's the worst offender)

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

### 2. UX

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

### 3. UI

- **Mixed streak decoration:** `*** 10 STREAK ***` asterisks in-game vs `⚡ 🔥 ★ ✦` elsewhere. Pick one style (todo already suggests emoji ramp — do it in `streak_display` + `game_header` together).
- **Red is a raw escape code in 6 places** (`"\033[91m"`: `utils.py:232`, `roguelike.py:11`, `push_your_luck.py:39`, `stakes.py:41`, ...). Add `RED` to the theme tuples. Bonus: `mono` then gets a monochrome "red" instead of bypassing the theme.
- **Stats rows don't line up:** each game type uses a different format string (`stats.py:193-203`). One table with fixed columns (`played · correct% · best streak · extra`) is easier to scan.
- **Hangman gallows are a single color for all stages** — `_draw(wrong, ...)`. (Todo has per-part colors; the stage-based color already exists, which is nearly enough.)
- **`last: translation 88% streak 12` on the menu** shows the raw stats key; fine, but pad it consistently with `{name_str:<16}`.

---

### 4. Efficiency & code size

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

### 5. Data quality

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

### 6. Project hygiene

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

### 7. Fix the todo list

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

### Suggested order

1. **15 minutes — the 5 one-liners:** `yn_input`, `match("")`, Rapid Fire `/`, Wordle `Random(seed)`, double-Enter on bust.
   - _(pass 2)_ **+15 minutes — XS fixes:** protect `ñ` in `strip_accents`, Push Your Luck `q` forfeits the pile, Anagram accepts any same-letter pool word, Hangman message for bad input, quit-sound `join`.
   - _(pass 2)_ Conjugation accent warning (S) goes with the `match` change in this step.
2. **1 hour — data + gender:** fix POS rule, add `"g"` field for exceptions, slice Gender by difficulty, skip empty verb forms.
3. **1 hour — correctness of state:** SRS miss-list, stale login streak, quest reset, badge order, settings validation.
4. **Half a day — the refactor:** single game registry, `Session` helper, sound wrapper collapse. Do this *before* adding new games from `todo.md`, or every new game copies the same 40 lines.
5. **Later:** typed-answer mode, XDG paths, LICENSE, tests.

### Skip
- **Daily Wordle reseeds global RNG** — `wordle.py:53`. After one daily game, all later `random.choice` calls this session follow the same fixed sequence for every player that day. Use `random.Random(seed).choice(...)`.
- **Splash screen forces an extra Enter every launch** — `utils.py:187`. Skip it, or show it for 1 second.

---
