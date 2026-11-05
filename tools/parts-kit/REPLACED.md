# What the parts kit replaced (Q41)

Every value and part Vocal Sessions dropped when it moved onto Parts kit 1.1.0, in version 3.55. Each row says where it was, what replaced it and the decision behind it (D-numbers are in Ivan's decision register). The reference sheets item that comes next turns these rows into Retired rows with "replaced by". Nothing here is used by the app any more. The old code is in git history before 3.55.

## Motion

| Old value or part | Where it was | Replaced by | Decision |
|---|---|---|---|
| The app's own springs (`SPRINGS`: gentle, nav, ripple, press, release) and their sampling | `js/motion.js` › `MOTION` | The kit's springs, the same numbers, read from `Parts.motion.springs()` | D18 |
| Writing `--ease-*`, `--dur-*`, `.motion-off`, `.motion-reduced` on `<html>` (`MOTION.publish()`) | `js/motion.js` | The kit's `Parts.motion.publish()` (only the kit writes them) | D18 |
| The app's speed and Reduce Motion state | `js/motion.js` | `Parts.motion.setSpeed()`, `setReduced()`; the app still saves `vocalMotion` and `vocalReduce` | D18 |
| The spring fallback curve `cubic-bezier(.25, .9, .3, 1)` | `js/motion.js` | The kit's own fallback | D18 |

## Pop-ups

| Old value or part | Where it was | Replaced by | Decision |
|---|---|---|---|
| The toast (`.toast`, `.toast.long`, its 1.9 s, corners 22 px when long) | `js/ui.js` › `toast()`, `css/app.css` | The kit's toast (`Parts.toast`), 3 s; long ones wrap (`.vs-long`) | D16 |
| The Undo / Retry toast (`.toast.ckundo`, `.ckub`) | `js/ui.js` › `toastBtn()`, `js/clock.js` › `ckToast()`, `css/app.css` | The kit's toast with its button (`undo`, `undoLabel`) | D16 |
| The confirmation sheet (`confirmSheet()`: a sheet with a red `.cta` and a ghost Cancel) | `js/ui.js` | The kit's alert (`Parts.confirm`), via `HOST` | D08 |
| The Take menu, Comment menu and Marker menu as sheets (VS-055, VS-058, VS-068) | `js/takes.js`, `js/track.js` | The kit's action sheet (`Parts.choices`), via `choiceSheet()` | D07 |
| The app's sheet layer: `.scrim` (z 40, `--scrim`, `fade`), `.sheet` (max 440 / 540 wide, 88 vh, `up` 0.55 s `cubic-bezier(0.28, 1.35, 0.45, 1)`, iPad `pop` 0.42 s), its blur `26px … brightness(1.06)` | `css/app.css`, `js/ui.js` › `renderSheet()` | The kit's sheet (`Parts.sheet`) in `#layer`, via `HOST` | D09, D10, D14, D15 |
| Sheet corners 34 (and 28 on iPad) | `css/app.css` › `--r-sheet`, `body.reg .sheet` | 46, the screen's own corners | D17 |
| The sheet header's own glass (`.shead`: sticky, `--glass-strong`, `blur(20px) saturate(--shead-sat)`) | `css/app.css` | Part of the kit's sheet head | D15 |
| Dragging a sheet down by its header (`SD`: 90 pt to close, `.sheet.drag`, `.sheet.back` 0.32 s) | `js/gestures.js`, `css/app.css` | The kit's sheet drag: head or content at the top, a flick at 700 pt/s | D14 |
| The song row's long-press menu (`#ctxmenu`, 480 ms, `.rowc.lifted` with its 16 px corners, `.ctxback`) | `js/songs.js`, `css/app.css` | The kit's long-press menu (`Parts.contextMenu`): lift from 200 ms, open at 700 ms, dim 20% / 25% | D16 |
| The lyric line's hold menu (`#lmenu`, 500 ms, `.sgl.lifted`, `body.lmopen` dimming) | `js/clock.js`, `css/app.css` | The kit's long-press menu | D16 |
| The pull-down menus (`#sortmenu`, `#rmenu`, `#hmenu` as `.ctxmenu` with 18 px corners; `.opmenu`; `.pmenu` with 16 px corners, its scrim and `pmIn`) and their placing (`sgPlace()`, `sgPlaceHintMenu()`) | `js/songs.js`, `js/onepage.js`, `js/patterns.js`, `css/app.css` | The kit's menu (`Parts.menu`, via `KMENU`), 20 corners | D16 |

## Controls and bars

| Old value or part | Where it was | Replaced by | Decision |
|---|---|---|---|
| The switch (`.tgl`, 51 × 31, `transform 0.3s cubic-bezier(0.3, 1.3, 0.5, 1)`, background 0.25 s) | `css/app.css`, eight rows in `js/settings.js`, `js/application.js`, `js/patterns.js`, `js/ui.js` | The kit's switch (`.pk-switch`, `switchHTML()`), 380 ms, drag or flick | (kit default) |
| The segmented control's knob (`.knob`, `placeKnob()`, `placeKnobs()`, `squish` 0.45 s, `transform 0.45s --ease-knob`, `width 0.3s`) and track (`.seg` padding 3, gap 2) | `js/ui.js`, `css/app.css`, 19 controls | The kit's segmented control (`.seg.pk-seg`, `.pk-seg-ind`): equal segments, a 350 ms spring, swells, draggable | D04 |
| The zoom levels' knob outline (`.trklv .knob`) | `css/app.css` | The same outline on `.trklv .pk-seg-ind` | D04 |
| The pattern player's vertical speed bar (`.phbar` 84 × 250, 30 px corners, `.phfill` 0.32 s, `.phticks`, `.phbar.stretch` 0.5 s) | `js/patterns.js`, `css/app.css` | The kit's slider (`#pHudBar.pk-slider`) on a glass card. The bar is kept in git history at 3.54, commit `06dcf72` (the tag `vs-3.54-speedbar` couldn't be pushed from Claude's workspace) | D03 |
| The dock's tab bar (`.tabbar` in `.dockrow`: 54 pt tabs, `max-width 0.45s cubic-bezier(0.3, 1.25, 0.5, 1)`, `padding 0.45s`, `height 0.35s`) | `js/ui.js` › `renderDock1()`, `css/app.css` | The kit's tab bar (`.pk-tabbar`, `.pk-tab-ind`) | D01 |
| The Songs search bar (`#sgbar`: an old `.tabbar.min` shrunk to a Songs circle, its own `.sfield` and Cancel, lifted by the app's `--kb`; `body.sgsearch`) and the old `.tabbar` rules left behind (`padding 0.45s`, `max-width 0.45s`, `height 0.35s`, `transform 0.5s`, `opacity 0.25s`, two near-copy curves). Removed in 3.64 (Q51) | `js/songs.js` › `sgEnsure()`, `songsAfter()`, `css/app.css` | Replaced by kit part 6: the dock's search field opens in the tab bar's place (`.pk-searching`) and filters the Songs list; the kit lifts it (`--pk-kb`) | D01, D02 |
| The tab bar's collapse (`tabMin`, `setTabMin()`, `tabPillPlace()`, `tabRoom()`, `.tabpill`, `.dockrow.min`, `TAB_DOWN` 30, `TAB_UP` 20) | `js/ui.js`, `js/gestures.js`, `js/events.js`, `css/app.css` | Nothing: the tab bar never folds | D01 |
| 12 pt between the tab bar and the search circle | `css/app.css` › `body.phone .dockrow` | 8 pt (`tabBar.searchGap`) | D02 |
| The landscape tab bar's shrinking spacers (Q27) | `css/app.css` | Equal kit tabs, each a row with a smaller icon | D01 |
| The search circle's app glass (`.circ.glass.scirc`) | `js/search.js` | The kit's glass button (`.pk-btn.pk-glass.pk-press.pk-search-circle`) | D02 |
| A top bar icon changing at once | `js/ui.js` › `renderBar()` | The kit's crossing icons (`Parts.bar.swap`) | (kit default) |

## Rows

| Old value or part | Where it was | Replaced by | Decision |
|---|---|---|---|
| `.row:active` scale 0.98 | `css/app.css` | The kit's row press colour (`--pk-row-press`) | D06 |
| `.osum:active` scale 0.98 | `css/app.css` | `--pk-row-press` | D06 |
| `.arch:active`, `.setfoot:active` scale 0.96 | `css/app.css` | `--pk-row-press` | D06 |
| `.apsing:active`, `.apsoft:active`, `.apstop:active` scale 0.96 | `css/app.css` | Darker while pressed (`brightness(0.9)`) | D06 |
| `.rowc:active` `color-mix(--surface 92%, --fg)` | `css/app.css` | `--pk-row-press` | D06 |

## Buttons (Q53, 3.67)

Every button presses through the kit. `KITPRESS` in `js/gestures.js` only gives each button its kit class (parts 12, 14, 15); the press is the kit's.

| Old value or part | Where it was | Replaced by | Decision |
|---|---|---|---|
| `PRESS` (Q33): glass buttons grew 17 pt on `MOTION`'s `press` spring and settled on `release` (WAAPI on `scale`), with an inline `position` and `z-index` 10 while pressed | `js/gestures.js` | The kit's glass press, `.pk-press` (part 12): the same 17 pt, the kit's `press` and `release`, `z-index` 20 while pressed | Q53 |
| The light-up: `.pressing` painting a registered `--lift` colour as a background image, in 150 ms, out 60 ms | `js/gestures.js`, `css/app.css` › `.pressing` | The kit's `::after` layer at `--lift-max` (parts 12 and 15), on its own lift timings | Q53 |
| `PRESS.ON_BAR`: the iPad's top tabs, `.trkb`, `.trkpp`, `.fwbtn`, `.pstep button` only lighting up | `js/gestures.js` | `.pk-press-bar` (part 15) | Q53 |
| The solid shrink: `transform: scale(var(--press))` on `:active` for `.cta`, `.circ`, `.chip`, `.calbtn`, `.cal button`, `.nudge`, `.shbtn`, `.txtbtn`, `.cvpp`, `.cvpill`, `.ckpi`, `.cktile .ckc`, `.trkpad`, `.trkpill`, `.sgplay`, `.sgtkb`, `.tkb`, `.tkbig`, `.pplay`, `.prep`, `.ppill`, `.ladnote`, `.ladrpt` | `css/app.css` | `.pk-press-solid` (part 14): to `--press` (0.93) over `--dur-quick`, back on `release`. The clock's tiles shrink as one (`.cktile`), not just their circle | Q53 |
| Their release: `transition: transform 0.5s var(--ease-pop)` (and `transform var(--dur-quick)` on the ladder's notes) | `css/app.css` (23 rules) | The kit's `release` spring | Q53 |
| The same 0.5 s transition left on rows and row-like cards (`.row`, `.arch`, `.setfoot`, `.osum`, `.apsing`, `.apsoft`, `.apstop`), and `.svd-arch:active` `transform: none` | `css/app.css` | Nothing: they highlight (D06) | D06, Q53 |
| `.glass::after { content: none }` (the old shine's leftover) | `css/app.css` | Nothing: the kit's light-up layer uses `::after` | Q53 |
| Picking chips (`.chip`, toggled by the app): their own shrink | `js/helpers.js`, `js/screens.js`, `js/ui.js`, `css/app.css` | The kit's chips (part 18) in `.pk-chips.pk-static`, no press; `+ Your own` only acts, so it keeps its look and takes `.pk-press-solid` | Q53 (default) |
| The note steppers (Your voice, Find your bridge): two 40 × 36 `--fill` squares either side of the note | `js/patterns.js`, `css/app.css` › `.pvstep button` | The kit's stepper (part 24) beside the note, its halves lighting up (part 15), keeping `patNudge` / `bfStep` and their names | Q53 |
| `.sgsplit .sgcol:has(.pressing)` | `css/app.css` | `:has(.pk-pressed)` | Q53 |

## Values the value test no longer lists

`tests/test_values.py` › `KNOWN` lost every stray above (corners, presses, curves and durations of the parts that moved), and Q40's two glass fixes (`.phbar`, `.pmenu`) went with their parts. Q53 took 23 more (the 0.5 s presses) and Q40's six solid press fixes (`PRESS_FIX`).
