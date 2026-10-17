# Maintaining Vocal Sessions

Notes for whoever works on the app next, whether that's Ivan, a new Claude session or anyone else. The [README](README.md) covers what the app does; this covers how it's built and how to change it safely.

---

## The short version

1. Change the files in `js/` and `css/` (or `index.html` for markup, `sw.js` for offline behaviour). Practice content (exercises, words, write-ups, goals) is all in `js/content.js`.
2. While building, run `python tests/run.py quick` (about a minute and a half) or just the files you're changing. Before pushing, run `python tests/run.py` (about 3½ minutes). Everything must pass.
3. Run `python tools/release.py 3.7` with the new version, and write the changes in `CHANGELOG.md`.
4. Run `python tests/run.py release` to check the version agrees everywhere.
5. Push to `main`. GitHub Pages publishes it within a minute or two, and the **Tests** check runs on GitHub.

**Working with Claude:** Ivan reviews prototypes first. Nothing is built into the app or pushed until he says **"render"**.
- Research and prototyping happen in one chat; each build happens in a **fresh chat**, started from a short handoff note (the agreed scope, decisions and what's queued), so the build begins with a clear memory.
- Tests are tiered: `quick` or single files while building, the full suite once before pushing. The full suite runs files side by side.

---

## Files

| File | What it is |
|---|---|
| `index.html` | The page: markup, the launch screen, `APP_VERSION`, and the list of css/js files it loads |
| `css/app.css` | All styles. Light and dark colours are the `--variables` at the top |
| `js/*.js` | The app's code, in the order `index.html` loads them (below). No build step: the files are served as they are |
| `sw.js` | Offline support. The page is fetched fresh (4-second timeout, then the saved copy), and a new version is saved for offline use only once the page and every file it loads have downloaded. Versioned css/js files and images come from the saved copy; CHANGELOG.md is fetched fresh. Registered on `https` and on `localhost` (so the tests cover it) |
| `icon.png`, `splash/` | Home Screen icon and iOS launch images (light and dark, every recent iPhone and iPad) |
| `CHANGELOG.md` | What changed in each version, written for Ivan, not developers. The app's Changelog page is built from it (see below) |
| `.nojekyll` | Tells GitHub Pages to serve files exactly as they are, so `CHANGELOG.md` reaches the app as plain text |
| `tests/` | The test suite (see below) |
| `tools/release.py` | Sets the version number everywhere at once |
| `.github/workflows/tests.yml` | Runs the tests on GitHub after every push |

### The code, in load order

| File | Holds |
|---|---|
| `js/content.js` | **The practice content:** goals, coach video and timings (`VID`), exercises (`FOUND`, `ROT`), write-ups (`DESC`), quick words and Toggl tags. Loaded first |
| `js/config.js` | App settings and fixed design: limits, focus areas and colours, exercise icons |
| `js/motion.js` | **The shared springs** (`MOTION`): gentle, nav and ripple springs as CSS `linear()` easings and `--ease-*`/`--dur-*` variables, stagger helpers, Reduce Motion, the speed setting and the distance blur. See Motion below |
| `js/storage.js` | Loading, checking (`cleanData`) and saving data, data-version upgrades, recordings in IndexedDB |
| `js/helpers.js` | Small helpers (dates, text, icons, layout) and the on-screen state `U` |
| `js/screens.js` | Today, Progress, Exercises, Settings and the session steps |
| `js/songs.js` | Songs: the list, pasting and labelling lyrics, the lyrics screen, marks and cues, editing, search, pins, and checking saved songs (`cleanSong`) |
| `js/changelog.js` | Settings › Changelog, built from CHANGELOG.md |
| `js/ui.js` | Top bar, tab bar, sidebar, sheets, `render()` and the sliding picker knobs |
| `js/session.js` | Running a session (steps, clock, finishing, editing) and recording takes |
| `js/backup.js` | Export, Check a backup, restore, undo, and Copy for Toggl |
| `js/events.js` | Every button action, swipe to delete, and blocking zoom |
| `js/gestures.js` | Pull to refresh and the update check, rotating, keyboard shortcuts, dragging sheets, scrolling |
| `js/boot.js` | Starts the app: loads saved data, then draws the first screen. Always last |

They're plain scripts, not modules: they share one global scope, and a file can use anything from the files before it. Nothing runs while the files load except in `boot.js`, so the order only matters for `boot.js` being last. Inside each file, sections are still marked `/* ===== Name ===== */`.

The code is formatted with Prettier (`npx prettier@3.3.3 --write --single-quote --print-width 120 --trailing-comma es5 js css`). Formatting is optional, but keeps changes easy to read.

### Every file has a version in its address

`index.html` loads `js/storage.js?v=3.7.1` and so on. A new version means new addresses, so no phone can mix an old file with a new page, and the offline copy can keep each version complete. `tools/release.py` updates every `?v=`; the release test fails if one is missed or a listed file doesn't exist. **Add a new file by adding its `<script>` (or `<link>`) to `index.html` with the same `?v=`.**

---

## Where data lives

Everything stays on the device. There is no server.

| Where | Key | Holds |
|---|---|---|
| localStorage | `vocalTracker` | All saved data (`D`): sessions, song practice, months, exercises, songs, words, last backup |
| localStorage | `vocalDraft` | The session in progress (`X`), so it survives closing the app. Song practice only has a `start` (and a draft) once its first take starts recording |
| localStorage | `vocalBackupLog` | Backup history for this device |
| localStorage | `vocalSongPrefs` | This device's song sort order and recent searches (not backed up) |
| localStorage | `vocalBeforeUpgrade` | The data as it was before the last data upgrade, kept for 30 days |
| IndexedDB `vocalTakes` (version 2) | store `takes` | Recordings, with their audio as Blobs |
| IndexedDB `vocalTakes` | store `undo` | The copy kept for 30 days after a restore |

`cleanData()` checks anything loaded or restored and drops what's malformed, so damaged data can't stop the app starting. `migrate()` fills in defaults and then runs `upgradeData()`; `normX()` upgrades older drafts.

### Data version

Saved data carries `schema` (currently 2, from 3.8; 1 was 3.7). To change the shape of saved data:

1. Add a numbered step to `UPGRADES` that changes `D` in place, and raise `SCHEMA` to match.
2. Steps run in order the first time the new version opens, and whenever an older backup is restored. Before they run, the data is copied to `vocalBeforeUpgrade`.
3. Add a test in `tests/test_data.py` that loads data from before the step and checks the result.

A backup whose `schema` is higher than the app's shows "Made by a newer version" before restoring.

### Songs

Each song in `D.songs` is its own record. Songs from before 3.8 have only `id` and `name`; everything else is optional.

| Field | Holds |
|---|---|
| `id`, `name` | Never change. Recordings (`songId`) and song practice (`songId`, `songName`) point at them. `name` is the title |
| `artist`, `pinned`, `added` | Artist (may be empty), pinned on Today and at the top of Songs (at most 3), when it was added (ms) |
| `practised` | When a take of it was last recorded (ms), set when a take is saved |
| `original` | The lyrics exactly as pasted. Never edited, so damaged lyrics can be rebuilt from it |
| `sections` | `{sid: {label, cue, lines, ann, orphans}}`. `lines` is an array of lines, each an array of words. `ann` maps `"line:word"` to marks: `br`, `run`, `up`, `dn` (1), `v` (vowel), `nt` (note), and `check` + `was` when the word changed. `orphans` are marks whose word was removed |
| `order` | The running order `[{o, sid}]`. Linked repeats share a `sid`; each `o` is one place in the song, and takes recorded from a section carry it. Unlinking and moving sections never change an `o` |

`cleanSong()` checks each song on its own when data loads or a backup is read: bad values are dropped, marks on missing words and order entries for missing sections are removed, fields it doesn't know are kept, and if the lyrics are unusable but `original` is there, they're rebuilt from it. Practised dates come from recordings (`TAKES`) and `practised`, whichever is later.

### Recall

Recall is a song mode (`U.sMode = 'recall'`) that hides lyrics without changing the layout: `maskText()` wraps hidden letters in `.hx` spans (`aria-hidden`), which are transparent with a rounded pill drawn by `.hx::after`, so every word keeps its width. `U.sHint` is the level (0 Full lyrics to 4 Blank) and `U.sOrder` is `start` or `end`. Neither is saved, and entering Recall always resets them. Tapping a `.rl` line adds `.peeking` for `peekSecs()` (only one line at a time); holding one for `HOLD_MS` adds `.peeking.held` until the pointer lifts. Neither re-renders.

The only Recall setting is **Peek length**, `D.prefs.peek` (1, 2, 3 or 5 seconds; missing means 2). `D.prefs` holds settings that travel with backups; `cleanData()` drops values it doesn't know.

### Motion

Everything that moves uses `MOTION` (`js/motion.js`), so the app feels the same everywhere and later features never add their own easing.

- **Springs:** `gentle` (ζ 0.82, 1.9 Hz: rows, capsules, sheets, fades), `nav` (ζ 0.86, 2.2 Hz: moving between pages, a little quicker) and `ripple` (ζ 0.6, 2.4 Hz: peeks and small pops). CSS uses `var(--dur-gentle)` and `var(--ease-gentle)` (and so on); JS uses `MOTION.animate(el, frames, {spring, delay, ms, fade})`, which does nothing (or a short fade with `fade: true`) when motion is off.
- **Stagger:** `MOTION.stagger(i, 'word' | 'row' | 'bar')` gives 30, 45 or 30 ms per item.
- **Reduce Motion** (the iOS setting) and **speed:** `MOTION.on()` is false with Reduce Motion or speed 0. `MOTION.setSpeed(4)` is slow motion for tuning on a device, `setSpeed(1)` puts it back; it's kept in localStorage `vocalMotion`, never in backups. With motion off, every `--dur-*` is `0ms` and `<html>` has `motion-off`.
- **Distance blur:** `MOTION.blur(d)` (up to `BLUR_MAX`, 1.5 px, and 0 with Reduce Motion), `MOTION.dim(d)` (down to 0.3) and `MOTION.dimLabel(d)` (labels only dim, down to 0.45), where `d` is how many lines away from the focus. Song Clock's Blur ahead should reuse these.
- **Tests run with motion off:** the harness sets `vocalMotion` to `0` before each page loads. A test that needs real motion passes its own `init` setting it to `1` (see `test_lyrics.py`).

### The lyrics page

Since 3.11 a song is one continuous page: `.sgsong .sgsec` has no background, just its label and space. The lyrics editor (`lyricsEditHTML`) still uses cards. Tapping a section (`sgSec`) or tapping away (the click handler in "taps that aren't on a button") changes `U.sSec` and calls `sgRefocus()`, which **updates the page in place** rather than redrawing it: each section's attributes, header and controls (`.sgrecp`: Record, Takes, Marks) are copied from a fresh `sgSection()`, while the lines stay the same elements so their fade can ease. `sgFocusPaint()` then sets `--fo` (opacity) and `--ff` (blur filter) on every row outside the focused section, by distance in rows; `songsAfter()` calls it after every redraw without easing. In Recall, lines peek, so a section is focused from its label. **Marks** (`sgMarks`) opens Annotate scrolled to that section.

### Recordings

Each take in IndexedDB is `{id, songId, created, len, size, type, star, blob, note?, o?}`. `o` is the place in the song it was recorded from (an `order` entry); takes without one (song practice, and everything before 3.9) belong to the whole song. `prune()` keeps the last `KEEP_TAKES` (3) unstarred takes per song, whatever their section, plus every starred one. Recording a section uses the same `startRec`/`stopRec`/`saveRec` as song practice, with a `{songId, o}` target; while it runs, `rec.o` locks the song screen to it.

### Rules that keep old data working

- **Never rename or remove an exercise id** (`slides`, `humming`, `lip`, `straw`, `falsetto`, `upperlower`, `rung`, `hinge`, `half`, `vertical`, `nasal`, `flex`). Sessions store levels by these ids. The backup tests fail if they change.
- **Data changes are additive.** Add fields with a default; don't rename or repurpose existing ones. Older backups must still restore, and new backups must still restore in the previous version.
- **Bump the IndexedDB version only to add stores**, and create each store only if it's missing.

---

## The Changelog page

Settings › Changelog fetches `CHANGELOG.md` and builds the timeline from it (`parseChangelog()`), so **writing the changelog is all it takes**. The format it relies on:

```markdown
## 3.7 · 15 Oct 2026
*Headline shown on the card*
<!-- area: backup -->            ← optional: the area for the whole version

<!-- area: look -->              ← the area for the next section
**Section title**
- A change. Each bullet counts as one improvement.
  - A sub-point (shown in Every change, not counted)
- Another change. <!-- area: fixes -->   ← one bullet in a different area
```

- Areas: `practice`, `songs`, `progress`, `recordings`, `backup`, `look`, `fixes`. Untagged bullets use their section's or version's area, or `fixes` for a patch version and `practice` otherwise.
- An x.0 version can name its era: `<!-- era: Liquid Glass · Native look, deeper tracking… -->`.
- The comments are invisible on GitHub.
- `python tests/run.py release` checks every heading, headline and area tag, and the changelog tests check every version appears in the app.

## Backups

A backup is a JSON file with: a plain-English `README` array, `app`, `format` (2), `appVersion`, `exportedAt`, `device`, `summary`, `data` (= `D`), `draft` (= `X`), `takes` (recordings as data URLs) and `checkCode`.

- **Exclude recordings** writes `takes: []` and `recordingsExcluded: true`, and the check code is worked out on that file as written. Check a backup and Import say "Recordings not included", and restoring one keeps the device's recordings (the undo copy notes `keptTakes`, and undoing leaves them alone).
- `checkCode` is the SHA-256 of `JSON.stringify({data, draft, takes})`. `inspectBackup()` recalculates it to decide whether a file is complete (`good`), from before 3.6 (`old`), edited or partly copied (`changed`), missing some recordings (`partial`) or unusable (`broken`).
- Export reads its own file back through `inspectBackup()` before offering to save it.
- Restore keeps an undo copy first; `undoRestore()` puts it back.
- Files are named `Vocal Sessions backup · YYYY-MM · Device.json`, so iOS offers to replace the month's file.

The fixtures in `tests/fixtures/` are real backups made by 3.5 and 3.6, plus a copy of the 3.6 app. **Don't regenerate them.** They prove that old backups keep working, and that new backups still open in 3.6.

---

## Tests

```
pip install playwright==1.56.0
python -m playwright install chromium
python tests/run.py                  # everything, side by side: about 3½ minutes (before every push)
python tests/run.py quick            # all but layout and random taps: about 1½ minutes (while building)
python tests/run.py backup flows     # just some files
python tests/run.py --one-at-a-time  # everything, one file after another: about 11 minutes
VS_FUZZ_STEPS=2000 python tests/run.py fuzz   # a longer random-tap run
```

The tests run with motion off (see Motion above), so nothing waits on a spring. The tests drive the real app in Chromium, served from `localhost` as GitHub Pages would serve it. Screenshots of every screen go to `tests/output/`. On GitHub they're attached to each run as **screenshots**.

| File | Covers |
|---|---|
| `test_release.py` | The version agrees in the app, README and CHANGELOG |
| `test_content.py` | content.js fits together: every exercise has a valid focus, a write-up, quick words and a video timing; no bare `&`; Toggl tags in use |
| `test_flows.py` | A full session with notes, the clock, Skip, editing, song practice, Toggl text and drafts |
| `test_progress.py` | The Progress chart, ranges, picking bars, time per step and the "doors" to All sessions |
| `test_edge.py` | Every bug from the 3.3.2 audit, so none come back |
| `test_data.py` | Data version upgrades and the copy kept first, backups from a newer version, Storage protection, and opening offline |
| `test_changelog.py` | The Changelog page shows every version in CHANGELOG.md, the chart, Show all, Every change, and a failed load |
| `test_songs.py` | Pasting and labelling lyrics, the song screen, Annotate and Lyrics editing (marks following their words), unlink, reorder, pins, the list, search, Today's pinned songs, older and damaged songs, backups, and iPad/Mac shortcuts |
| `test_backup.py` | Export, Check a backup, damaged files, restore comparison, undo, the old-backup fixtures and the exercise-id guard |
| `test_recording.py` | Recording with a fake microphone, leaving mid-take, keeping 3 takes, and audio in backups |
| `test_recall.py` | Recall: the five hint levels (checked letter by letter, and that nothing moves), peeking, the hint capsule and its menu, From the start, From the end and Start anywhere |
| `test_fixes.py` | 3.10.1: sheets keep their scroll to themselves (real touch swipes and the wheel), song practice timed from its first take, the weekly goal opening Progress, Recall's pills (every line's place checked at each level and size), peeking, holding and Peek length in backups |
| `test_sections.py` | Recording a section: selecting, the lock while recording, takes saved with their place, the review sheet, stars and the keep rule across sections, unlink and reorder, leaving mid-take, and backups with Exclude recordings |
| `test_lyrics.py` | 3.11: the shared springs, the continuous lyrics page, focusing a section (patch, controls, dim and blur by distance, labels sharp), tapping away, Marks, Recall's label focus, Reduce Motion, easing with motion on, and every size with a section focused |
| `test_layout.py` | Every screen on iPhone, iPhone landscape, iPad and Mac, light and dark, plus pull to refresh |
| `test_fuzz.py` | Thousands of random taps, checking nothing breaks after each one |

Running side by side, each layout size and each random-tap seed is its own job, every job has its own browser and test web server, and `VS_JOBS` sets how many run at once (default: twice the processor count). Results are shown per job as each one finishes.

Tests reach into the app through its globals (`D`, `X`, `U`, `render`…), so the scripts must stay classic `<script>`s, not ES modules. `harness.offline(path)` switches the test web server off for a real "no connection" (Playwright's own offline switch doesn't reach the offline helper).

---

## Releasing

`python tools/release.py 3.7` updates `APP_VERSION` and `RELEASE_DATE` in `index.html`, the README badge and "Current version" line, and adds a `## 3.7 · date` section to `CHANGELOG.md` with a placeholder headline and note. The release test fails until both are replaced with the real headline and changes.

Version numbers: **major** for a redesign, **minor** for new features, **patch** for fixes.

The app checks for a newer `APP_VERSION` on pull to refresh, so a release reaches the phone the next time Ivan pulls down on Today or Progress.

---

## Style

The app follows Apple's design language for iOS 26/27 (Liquid Glass imitated in CSS), with British English in plain, friendly words. Everything must work on iPhone, iPhone landscape, iPad and Mac, in light and dark mode.
