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
| `js/session.js` | Running a session (steps, clock, finishing, editing, `togglePause()`) and recording and playing takes |
| `js/window.js` | **The floating window** (`FW`, `FW_KINDS`): a session or playing take shown on every other screen. See The floating window below |
| `js/backup.js` | Export, Check a backup, restore, undo, and Copy for Toggl |
| `js/events.js` | Every button action, swipe to delete, and blocking zoom |
| `js/gestures.js` | Pull to refresh and the update check, rotating, keyboard shortcuts, dragging sheets, scrolling |
| `js/details.js` | **Motion details** (`DET`): rows leaving, arriving and moving, Progress bar ripples, Today's arch fill and week wave, calendar days, session step slides, the Recall wave, sheets that change in place. See Motion below |
| `js/zoom.js` | **Card zoom** (`ZOOM`): cards zooming into their pages and Back shrinking them into their cards, swipe back from anywhere, the Finish, calendar day and new-song zooms. See Motion below |
| `js/launch.js` | **The launch ripple** (`LAUNCH`): the icon's bars pulsing, the launch screen fading and Today rising in. See Motion below |
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
| localStorage | `vocalWindow` | The floating window's corner on this device, `{corner: 'br'}` (not backed up) |
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
- **Stagger:** `MOTION.stagger(i, 'word' | 'row' | 'bar')` gives 30, 45 or 30 ms per item, for `MOTION.animate`'s `delay` (which applies the speed, so the stagger itself doesn't, since 3.13).
- **Reduce Motion** (the iOS setting) and **speed:** `MOTION.on()` is false with Reduce Motion or speed 0. `MOTION.setSpeed(4)` is slow motion for tuning on a device, `setSpeed(1)` puts it back; it's kept in localStorage `vocalMotion`, never in backups. With motion off, every `--dur-*` is `0ms` and `<html>` has `motion-off`.
- **Distance blur:** `MOTION.blur(d)` (up to `BLUR_MAX`, 1.5 px, and 0 with Reduce Motion), `MOTION.dim(d)` (down to 0.3) and `MOTION.dimLabel(d)` (labels only dim, down to 0.45), where `d` is how many lines away from the focus. Song Clock's Blur ahead should reuse these.
- **Tests run with motion off:** the harness sets `vocalMotion` to `0` before each page loads. A test that needs real motion passes its own `init` setting it to `1` (see `test_lyrics.py`).
- **The launch ripple (3.13, `js/launch.js`, `LAUNCH`):** the app's signature moment. On a cold launch the icon's six sound-wave bars pulse in turn (`BAR`: 520 ms each, 70 ms apart, from 120 ms), the launch screen fades with a slight zoom (`FADE`: 300 ms, at 860 ms), then Today's blocks rise in, top to bottom, on `gentle` 45 ms apart (`RISE`). `boot.js` calls `LAUNCH.start()` before the first draw and `LAUNCH.finish()` once recordings have loaded and `LAUNCH.minWait()` has passed (at most `LAUNCH.capWait()`). `restoreImport()` calls `LAUNCH.replay(then)` to replay it on Today, with the toast in `then`. Tab switches and coming back to the app never replay it; an update reload is a cold launch, so it plays.
  - **Where the bars live:** `#splash` in `index.html` is the icon's plain background (an inline WebP, `<img>`) inside `.sp-icon`, with the six bars as `<i>` elements placed over it. Their positions, sizes, colours and shadow were measured from `splash/logo.png` so the icon looks the same at rest as the real one; `css/app.css` (`#splash i`) has their width and shadow. If the icon changes, regenerate the background and re-measure the bars.
  - **Today's blocks** are the elements marked `data-rise` in `scrToday()` (and `pinnedCard()`, `backupNudge()`); they're risen in the order they sit on screen, so the iPad dashboard works too. Add `data-rise` to a new Today block to include it.
  - **Reduce Motion:** no pulses or rises, the launch screen fades in 200 ms. **Motion off** (the tests): it uses the old `.out` class exactly as before 3.13.
  - **`LAUNCH.busy()`** is true from launch until Today has risen; `fwPick()` returns nothing meanwhile, so the floating window appears after the rise.
  - Tests: `tests/test_launch.py` (motion on, Reduce Motion, motion off, import replay, the floating window, and the 3.4 first-frame checks at every size).
- **Motion details (3.14, `js/details.js`, `DET`):** everything only animates elements already in their final place, so nothing ever blocks a tap. With motion off or Reduce Motion every function returns straight away.
  - **Lists:** call `DET.arm()` just before a change that redraws (`DET.arm({stagger: true})` for a re-sort), and `render()` calls `DET.play()` afterwards. Rows opt in with `data-fk` (a stable key, e.g. `sg:<id>`; `sw()` rows get one automatically) and their group with `data-gk`. Removed rows leave a `.det-ghost` copy that shrinks away (pointer-events none); groups ease to their new height; rows that move slide (a ripple when staggered); a row that moves into another group (a pin) travels as a copy so the group's `overflow:hidden` doesn't clip it. Today's `data-rise` blocks take part too (the backup reminder leaving). Add `DET.arm()` before any new delete, add, pin or reorder.
  - **Progress:** `updatePcard({dir})` is the animated version (range: `dir 0`, arrows: `-1`/`1`); `updatePcard()` with no argument (scrubbing) never animates. `DET.bars()` reads heights before the redraw, `DET.pcardIn(was, dir)` ripples from them (scaleY from the baseline, `BASE` in details.js must match `H - B` in `chartSVG`).
  - **Today:** `LAUNCH`'s `done()` calls `DET.todayIn()` (arch `stroke-dashoffset` fill, week row wave). `finishSession()` calls `DET.finished()`, and `DET.after()` (end of `render()`) pops today's circle once Today shows with no sheet. It also slides in pinned songs that weren't on Today last time (`data-fk="tp:<id>"`).
  - **Elsewhere:** `DET.calendarIn()` after opening or changing month; `go()` calls `DET.stepIn(DET.stepDir(from, to))` between Foundation, Rotation and Application; `DET.listIn()` after the All sessions switch; `DET.exLine()` after switching an exercise to History; `DET.takeIn()` / `DET.starPop()` for takes; `DET.dockSwap()` brings the song's bottom capsules in on a mode change only (never on a hint step or redraw).
  - **Recall wave:** `DET.hxSnap()` before a hint change, `DET.hxWave(was)` after: newly hidden words get `--hxd` delays (30 ms a word, in reading order, used by `.hxin .hx` / `::after` in app.css), newly shown words fade from the end backwards. `peekLine()` and the hold call `DET.peek(line)` for a small `ripple` spring.
  - **Sheets changing in place:** `renderSheet()` treats `exporting` → `exportReady` as the same sheet (`DET.inPlace`), so it doesn't rise again; `DET.sheetSwap(oldH)` eases its height and fades the content.
  - **Reduce Motion in CSS (3.14):** the old blanket `* { animation: none; transition: none }` is gone. Under `prefers-reduced-motion` every transition is limited to opacity and colours over 0.2 s, and the keyframes that moved things (`up`, `pop`, `grow`, `clockIn`, `clockOut`, `squish`, `lgdraw`) are redefined as plain fades. New CSS motion gets this for free; don't add `!important` rules that switch fades off.
  - **Not built yet (left for later):** Annotate's marks menu blooming from the word and the section lift while reordering, Perform's larger text scaling (FLIP), the recording bar rising, a take dropping off under the keep rule shrinking away, the progress dashes filling and the step pill moving onto the shared springs.
  - Tests: `tests/test_details.py` (motion on in slow motion, Reduce Motion, motion off). `daily()` seeds a session on each of the last 15 days so the checks don't depend on the day of the week.
- **Card zoom (3.15, `js/zoom.js`, `ZOOM`):** a card that opens a page zooms into it; Back shrinks the page into the card, with the list scrolled back to where it was.
  - **A card opts in with `data-zk="<key>"`**, a key that's the same on the screen you come back to (`ex:<id>`, `sg:<id>`, `sgp:<id>`, `all:sessions`, `all:songs`, `log`, `start`, `songStart`, `goal`, `songs`). The click handler calls `ZOOM.tap(el)`, which remembers the card, and whether the tap was a Back button (`#barL` with an aria-label starting "Back"). `go()` calls `ZOOM.before()` before the change and `ZOOM.after(ctx)` after `render()`: a tapped card and a change of screen is an open (pushed on `ZOOM.stack()` as `{key, from, to, y}`); a Back from the top page to where it came from is a close (popped, scroll put back to `y`). Any other change keeps only the stack entries still on the way back. Code that opens a page itself can call `ZOOM.arm(cardEl)` first. **Don't `DET.arm()` around a zoom**, or rows would FLIP across screens.
  - **How it's drawn:** a fixed layer `.zm` (z-index 24: above the page, below the sidebar, dock, floating window and sheets) holding still copies (`shot()`: a clone of `.wrap` placed where it is, ids and actions stripped, `inert`, top bar pinned where it was). Under it the real app has already moved on, so taps always reach the real app. The window is four nested `.zm-c` boxes, each clipping one rounded corner, moved by `translate` (`win()`), so it grows from the card's rectangle to the screen on transforms only (no clip-path). Inside: the page background, a tint in the card's colour (`.zm-tint`), the page copy (`.zm-body`) and its title (`.zm-title`), scaled so the title starts on the card's label (`anchor()`). A copy of the card (`.zm-ghost`) fades out on the way in and back in on landing; the real card has `.zm-src` (hidden) while the page lands on it. Cards under half the screen width grow the whole page from a miniature, the card scaling up as it fades (`mini()`). Black or white cards (the Start session capsule, `strong()`) hand their colour over quickly so it never fills the screen.
  - **Every part animates with `to(z, el, prop, value, timing)`**, from whatever it shows now, so a Back mid-zoom (or a swipe catching one) turns round from where it is. Timings: the window and page on `nav`; fades in ms. `end(z)` takes the layer away and puts every `.zm-src` card back; scrolling, resizing or leaving the app during a zoom ends it at once.
  - **Swipe back:** touch only, on any screen with a Back button and no sheet, clock or recording. It locks after 10 px if the move is rightwards and mostly sideways, then the page copy follows (`translate(dx·0.55, dy·0.2) scale(1 − 0.28·p)`, sideways only with Reduce Motion), over a still of the screen you came from (`prev`, kept for the last 4 pages). Let go past 22% of the width or faster than 0.45 px/ms and it clicks the real Back button (so it goes wherever Back goes, shrinking into the card if there is one, otherwise fading); otherwise `MOTION.spring()` brings it back at the finger's speed. **Gesture priority:** a swipe never starts on `OWN` (rows `.sw`/`.srow`, inputs, `.seg`, the charts, `.fw`, the dock, anything marked `data-own-gesture`) or on anything that scrolls sideways. Add `data-own-gesture` to anything new with its own sideways gesture.
  - **The other zooms:** `ZOOM.finishing()` / `ZOOM.finished(ctx, 'start' | 'songStart')` around `finishSession()` shrink the session into Start session (or song practice into its card) behind the summary sheet; today's circle pops later, when that sheet closes (3.14). `ZOOM.dayIn(rect)` grows a calendar day's sessions (`[data-zday]`) out of the day. `ZOOM.sheetShot()` and `ZOOM.sheetInto(shot, key, then)` shrink the new song's paste sheet into its row (a `.zm.top` layer, above the dock), then `then` opens the song from that row.
  - **Reduce Motion:** opens and closes are a short fade of the page copy; the swipe moves sideways only. **Motion off:** nothing is drawn, but the stack still works (Back returns to where the list was) and swipe back still goes back.
  - Tests: `tests/test_zoom.py`: every kind of card in and out (to the same card, scroll put back), Back mid-zoom, swipe below and past the threshold and a flick, gesture priority, frame-by-frame checks in dark mode that the window is never an empty box (wide and small cards, the capsule), Finish, the calendar, the new song, Reduce Motion, motion off and four layouts. The random-tap test fails if a zoom layer or hidden card is left behind.

### The lyrics page

Since 3.11 a song is one continuous page: `.sgsong .sgsec` has no background, just its label and space. The lyrics editor (`lyricsEditHTML`) still uses cards. Tapping a section (`sgSec`) or tapping away (the click handler in "taps that aren't on a button") changes `U.sSec` and calls `sgRefocus()`, which **updates the page in place** rather than redrawing it: each section's attributes, header and controls (`.sgrecp`: Record, Takes, Marks) are copied from a fresh `sgSection()`, while the lines stay the same elements so their fade can ease. `sgFocusPaint()` then sets `--fo` (opacity) and `--ff` (blur filter) on every row outside the focused section, by distance in rows; `songsAfter()` calls it after every redraw without easing. In Recall, lines peek, so a section is focused from its label. **Marks** (`sgMarks`) opens Annotate scrolled to that section.

### Recordings

Each take in IndexedDB is `{id, songId, created, len, size, type, star, blob, note?, o?}`. `o` is the place in the song it was recorded from (an `order` entry); takes without one (song practice, and everything before 3.9) belong to the whole song. `prune()` keeps the last `KEEP_TAKES` (3) unstarred takes per song, whatever their section, plus every starred one. Recording a section uses the same `startRec`/`stopRec`/`saveRec` as song practice, with a `{songId, o}` target; while it runs, `rec.o` locks the song screen to it.

### The floating window

Since 3.12, `js/window.js` shows a small window on every screen outside the thing it's for. It's its own element, `#fw`, added to `<body>` and kept across redraws; **it must never go in `#layer`**, or the sheet scroll guards (`overlayOpen()` in gestures.js) would treat it as an open sheet.

- **Kinds:** `FW_KINDS` lists what can be shown, in the order they win: `take` (a take playing or paused from the window), then `session` (a session with a `start`; untimed song practice has none). Each has `active()`, `own()` (you're on its own screen, so it isn't needed), `info()` (its text, time and progress), `toggle()` (its button) and `open()` (back to where you were). If the winner is on its own screen, the next one is tried. Song Clock's "Playing along" can be added as a third kind.
- **Updating:** `render()` calls `fwUpdate()` last; a MutationObserver on `#layer` calls it when sheets, the clock or menus come and go; playback's play and pause events call it too. `fwTick()` only changes its text: every second for a session, and from the take's progress loop. It hides whenever there's a sheet, the clock, a recording, song search or a text field in use.
- **Where you were:** `FW.sess` is `{view, y}`, the session step last shown and its scroll (kept up to date by a scroll listener). `FW.take` is `{id, place}`, set by `playTake()` from `fwHere()`: the tab, view, song, sheet and its `sd`, mode and scroll. Opening restores them through `fwGo()`, which renders and then scrolls.
- **Takes:** `takePlaying(id)` is true only while a take is actually playing, so its own buttons show Play when it's paused from the window, and tapping them carries on. Closing a section's takes sheet stops a paused take but lets a playing one carry on.
- **Corners:** `FW.corner` is `tl`, `tr`, `bl` or `br` (default), kept in localStorage `vocalWindow`. `fwBounds()` measures the room each time: right of the sidebar (the `.dock`'s left and padding), below the top bar, above whatever is in the dock (tab bar, the session button or Recall's hint capsule). Dragging follows the finger with pointer events; on release `fwThrow()` picks the corner from where it is plus 0.2 s of its speed, and springs there with `MOTION.spring()` on `nav`, starting at the finger's speed. There's no tucking against the edge.
- **Motion:** it rises in on `gentle` and shrinks out a little quicker; with motion off or Reduce Motion it just appears. `MOTION.spring(from, to, v, {spring, frame, done})` is a JS spring that starts with a speed, for anything thrown.
- **Tests:** `tests/test_window.py`, and the random-tap test checks it never shows over a sheet, while recording or on its own screen, never leaves the screen, and is there whenever a session is running elsewhere.

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
| `test_window.py` | 3.12: the floating window's clock, pausing from it, going back to the same step and scroll or the same take, a take winning over a session, dragging and flicking to each corner (remembered after a reload), where it hides, and every size in light and dark, including above Recall's hint capsule |
| `test_lyrics.py` | 3.11: the shared springs, the continuous lyrics page, focusing a section (patch, controls, dim and blur by distance, labels sharp), tapping away, Marks, Recall's label focus, Reduce Motion, easing with motion on, and every size with a section focused |
| `test_zoom.py` | 3.15: card zoom into each kind of page and back into the same card (scroll put back), Back mid-zoom, swipe back (follow, threshold, flick, spring back, gesture priority), dark-mode frames never an empty box, Start session and Finish, the calendar day, the new song, Reduce Motion and motion off |
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
