# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.42** (1 Nov 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28; Q11 · Data: Save Safety in 3.29; Q12 · Song Clock: Timing Integrity in 3.30; Q13 · Interface: Keyboard Guards in 3.31; Q04 · Marks: Practice Guide in 3.32; Q23 · Interface: Status Bar Glow in 3.33; Q14 · Playback: Smooth Frames in 3.34; Q18 · Tests: GitHub Match in 3.35; Q15 · Marks: Register-Ready Data in 3.36; Q16 · Audio: Voice Analysis Foundations in 3.37; Q17 · Hygiene: Dead Code Sweep in 3.38; Q19 · Session: One-Page Flow in 3.39; Q20 · Session: Application Redesign in 3.40; Q21 · Session: Saved Screen in 3.41; Q22 · Session: Clock Redesign in 3.42; Q24 · Coach: Video Redesign (tooling, no app version: the render kit is in `tools/coach-video/`); Q30 · Atlas: Lightbox Core (tooling, no app version: the Atlas is in `tools/atlas/`); Q32 · Exercises: Redesign in 3.48.

- **Every item has two separate gates.** `Awaiting Render` means it is not approved. Ivan's **Render** approves only the named item's exact scope and moves it to `Approved — awaiting Build`; it does not start work or authorize a push. A separate **Build** instruction starts implementation for that approved item. Do not treat approval of one item as approval of the whole queue.
- **The code wins on what's built.** This is a summary, not a spec. Check each note against the code before relying on it.
- **Detailed design notes live in Ivan's private project notes, not in this repo.** Where an item names one, ask Ivan to paste or attach it. Anything not settled here is marked *Unresolved*.
- **Check ideas against the app's purpose.** Before planning an item or a Not scheduled idea, ask the first test in [README › What it's for](README.md#what-its-for): does it make practice easier?
- **Ivan can reorder the queue.** Versions follow build order: each build takes the next minor version when it's built.
- **When an item ships,** remove its section from this file in the same push and set its row in the table below to `Shipped <version>`. Its `CHANGELOG.md` headline (the `*…*` line under the version) ends with its queue ID, e.g. `*Waveform sections on the track player (Q02)*`. The `##` line itself stays `## 3.23 · 27 Oct 2026`, which the app's Changelog page reads.

## Naming

Every queued item has a queue ID and a standard name, used in the queue, in handoffs, in commit messages and in file names. Use these, not the older working names.

- **Items:** `Q[##] · [Subsystem]: [Feature Name]`, e.g. `Q02 · Track: Waveform Sections`.
- **Files** (handoffs, specs, wireframes, prototypes): `q##_[subsystem]_[feature]_[type].[ext]`, lower case with underscores, e.g. `q02_track_waveform_sections_handoff.md`.
- **Releases:** the shipped version's `CHANGELOG.md` headline ends with the queue ID in brackets, e.g. `*Waveform sections on the track player (Q02)*` under `## 3.23 · 27 Oct 2026` (the `##` line keeps its exact format for the app's Changelog page). That's the bridge from queue ID to version. Q01 shipped as 3.22, headline `*Search, from every tab (Q01)*`; Q08 as 3.23.
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q35**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
- **Exception, 30 Oct 2026:** Ivan asked for the six stages of the 30 Oct read-only audit, plus its clean-up list, to get IDs straight away, before Render, most critical first. They are **Q11–Q17**. All seven got Render on 30 Oct 2026 and have shipped (3.29–3.31, 3.34, 3.36, 3.37 and 3.38).
- **Exception, 31 Oct 2026:** Ivan asked for the status bar fix to be queued with an ID before Render. It is **Q23**; Render and Build followed the same evening (shipped in 3.33).

Every ID with its **Status** (`Awaiting Render`, `Approved — awaiting Build`, `Building`, `Shipped <version>`, `Blocked` or `Retired`) and the working names older chats, notes and prototypes use. Render adds the row (or sets it to `Approved — awaiting Build`); the Build that ships it sets `Shipped <version>` in the same push.

| Queue ID | Standard name | Status | Earlier working names |
|---|---|---|---|
| Q01 | Search: Global Find | Shipped 3.22 | Render 10, Search, Global Search |
| Q02 | Track: Waveform Sections | Shipped 3.24 | Track 2, Sections on the waveform |
| Q03 | Marks: Layered Annotations | Shipped 3.27 | Marks 1, Layered marks |
| Q04 | Marks: Practice Guide | Shipped 3.32 | Marks 2, Marks help, Marks guide |
| Q05 | Song Clock: Tap Re-Anchor | Shipped 3.28 | Song Clock A2, Render 6, Line pass and retime |
| Q06 | Song Clock: Timeline View | Retired → Q05 | Song Clock B, Render 7, Section starts and wheels |
| Q07 | Song Clock: Dynamic Sync | Awaiting Render | Song Clock C, Render 8, Paced Recall |
| Q08 | Interface: Native iOS Polish | Shipped 3.23 | Native bars, iOS 27 polish |
| Q09 | Track: Waveform Sections Follow-up | Shipped 3.25 | Giant 3-Pad dock, Q02 follow-up |
| Q10 | Interface: HIG Foundations Pass | Shipped 3.26 | Vault ideas wireframes |
| Q11 | Data: Save Safety | Shipped 3.29 | Audit stage 1, data safety |
| Q12 | Song Clock: Timing Integrity | Shipped 3.30 | Audit stage 2, timing integrity |
| Q13 | Interface: Keyboard Guards | Shipped 3.31 | Audit stage 3, input hygiene |
| Q14 | Playback: Smooth Frames | Shipped 3.34 | Audit stage 4, per-frame work |
| Q15 | Marks: Register-Ready Data | Shipped 3.36 | Audit stage 5, room for register data |
| Q16 | Audio: Voice Analysis Foundations | Shipped 3.37 | Audit stage 6, Web Audio seam |
| Q17 | Hygiene: Dead Code Sweep | Shipped 3.38 | Audit clean-up list |
| Q18 | Tests: GitHub Match | Shipped 3.35 | Workflow review, 31 Oct 2026 |
| Q19 | Session: One-Page Flow | Shipped 3.39 | One-page session prototype, 31 Oct 2026 |
| Q20 | Session: Application Redesign | Shipped 3.40 | One-page session prototype, 31 Oct 2026 |
| Q21 | Session: Saved Screen | Shipped 3.41 | "Session saved" splash, 2+5, 31 Oct 2026 |
| Q22 | Session: Clock Redesign | Shipped 3.42 | Session clock ring prototype, 31 Oct 2026 |
| Q23 | Interface: Status Bar Glow | Shipped 3.33 | Gradient clipped at the top, 31 Oct 2026 |
| Q24 | Coach: Video Redesign | Shipped (tooling, no app version) | Coach video redesign, 31 Oct–1 Nov 2026 |
| Q25 | Coach: Frame-Accurate Chapters | Shipped 3.43 | Coach timings, level picker, 1 Nov 2026 |
| Q26 | Window: Picture in Picture | Shipped 3.44 | Floating window picture in picture and audit fixes, 1 Nov 2026 |
| Q27 | Interface: Landscape Tab Bar Fit | Shipped 3.45 | "Exerc" cut off on its side, 1 Nov 2026 |
| Q28 | Hygiene: Toggl Removal | Shipped 3.46 | Get rid of Copy for Toggl, 2 Nov 2026 |
| Q29 | Session: Song Rating Removal | Shipped 3.47 | Remove "Rate the song", 2 Nov 2026 |
| Q30 | Atlas: Lightbox Core | Shipped (tooling, no app version) | Visual App Atlas stage 1, Lightbox, 2 Nov 2026 |
| Q31 | Atlas: Map and Notes | Approved — awaiting Build | Visual App Atlas stage 2, map, notes, export, changes since last scan, 2 Nov 2026; re-scoped onto the Atlas kit, 2 Nov 2026, 19:50 |
| Q32 | Exercises: Redesign | Shipped 3.48 | Exercise patterns the app plays, Exercise page redesign (both 31 Oct), merged 2 Nov 2026 |
| Q33 | Interface: Glass Native Tuning | Shipped 3.49 | Glass tuning Recon and glass inventory, 2 Nov 2026 |
| Q34 | Interface: Native Menus and Controls | Blocked (on hold for the parts kit, 2 Nov 2026) | Component inventory (round 2), worth doing plus smaller wins, 2 Nov 2026 |

Work shipped before this standard (for example Track 1 and Song Clock A1) keeps its version numbers and has no queue ID.

Every item also follows [MAINTAINING.md](MAINTAINING.md): its [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [changelog](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style). On top of that:

- **Check the previous build is live first.** Use the item's **Needs** line. If it records that its required version was verified on `main`, that satisfies this check; otherwise look for the version in `CHANGELOG.md` on `main`. If it isn't there, stop and tell Ivan.
- **Never push with failing tests.** If something can't be finished, commit nothing, leave the item here and report plainly.
- **Everything that moves uses the shared springs.** Every new sound starts through `NOW.start()`.
- **The repo is public.**
  - Never commit real music, recordings, the coach video, course media, lyrics or backups.
  - Never commit with Ivan's personal email. Claude commits as `Claude <noreply@anthropic.com>`.

---

## Order (2 Nov 2026)

**Q33** shipped in 3.49 (Render 2 Nov 2026, 17:41; Build 2 Nov 2026, 21:17). **Q34** (Render 2 Nov 2026, 18:12) is on hold for the parts kit (Ivan, 2 Nov 2026, 22:11); it uses Q33's materials and springs. **Q32** shipped in 3.48 (Render 2 Nov 2026, 15:56; Build 2 Nov 2026, 19:06). Q30 shipped as tooling (Build 2 Nov 2026, 17:57; `tools/atlas/`), and **Q31** builds on it (Render 2 Nov 2026, 15:55, in the same instruction as Q30; re-scoped by a fresh Render at 19:50 to put Vocal Sessions on the universal Atlas kit, built after Prototype kit 1.1 and Atlas kit 1.0; its own Build). Both are tooling with no app version, like Q24, so they can be built outside the app queue's order. Q28 shipped in 3.46 and Q29 in 3.47 (Render 2 Nov 2026, 09:29; Build 09:33, in one instruction, built one after the other). **Q07** is still awaiting Render. Q27 shipped in 3.45 (Build 2 Nov 2026). Q25 shipped in 3.43 and Q26 in 3.44 (Build 2 Nov 2026); Q25–Q27 got Render on 1 Nov 2026 (19:59), in one instruction, each with its own Build. Q19 shipped in 3.39, Q20 in 3.40, Q21 in 3.41 and Q22 in 3.42. Q22 got Render on 31 Oct 2026 (20:59) and was built on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction, each with its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q07 · Song Clock: Dynamic Sync

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

- **Scope:** paced Recall, and recording against the clock.
- **Decided:** marks over Recall's pills stay still while words reveal (a test, not new behaviour).
- **Next action:** confirm dates and scope with Ivan.
- **Done when:** *Unresolved.*

## Q31 · Atlas: Map and Notes

**Status:** Approved — awaiting Build. **Render:** 2 Nov 2026, 19:50 (re-scope). Ivan: "Render. This is how I want things to be. Building system in place to be more optimal." This replaces the 15:55 Render (Ivan: "render stage one and two. add a Q## with standard naming but seperate them"); the item, its name and its features are the same, but they are now built once in the universal Atlas kit and Vocal Sessions uses that kit. **Build:** awaiting Ivan's instruction.

Gives the Vocal Sessions Atlas the map, notes Claude can read, export, and what changed since the last scan, by moving it onto the **Atlas kit** (`imperialfox/atlas-kit`, a separate universal tool with its own version, handoff and gates, no Q number). Tooling only, no app version.

- **Build order:** Prototype kit 1.1 (in `imperialfox/prototype-kit`), then Atlas kit 1.0, then Q31. Each has its own Build.
- **Scope:**
  - `tools/atlas/` keeps only Vocal Sessions' own settings: today's `screens.py` (start screens, areas, names, skip list, reset steps) plus the sample-data and docs hooks now in `scan.py` and `inventory.py`.
  - A pinned, unmodified copy of the Atlas kit in `tools/atlas/kit/`, with its version noted in `tools/atlas/README.md`; updated by copying a newer release (no submodule).
  - **What the kit brings** (the features approved at 15:55, unchanged):
    - **Map:** screens in area regions, lines for links the scan saw working (button, opens a sheet, back, tab bar; each can be shown or hidden), plus "found in code only" lines. Click a line for what's tapped and its code action. Drag cards, add labels, Tidy layout, pan, zoom, Fit all. The layout is saved and never redrawn while a label is being typed.
    - **Notes:** "Add note" (or N) on a screen. **Tap a part** (with Bigger part / Smaller) or draw a **Box**, write the note and pick an optional kind. Saved in the shared note format v1 (`SHARED.md` in both kits): screen, scan, marked area, the element's tag, classes, text and path, and its key styles. Never records what's typed in a field. Statuses: Open, Looking into it, Fixed, Dismissed.
    - **Export for Claude:** Copy report (Markdown), Download .zip (report, notes.json and a cropped picture of each marked area), Copy as queue ideas (text only, for Not scheduled below, each with a priority checked against the app's purpose), and an option to mark them "Looking into it".
    - **Changes since the last scan:** new, gone, looks different (how much and where), links changed, failed this time; before and now with a wipe slider; the `CHANGELOG.md` versions and queue IDs released in between, never claiming which one caused a change; a "show only changes" filter.
    - **Proposed screens:** a prototype listed against the real screen it changes is shown beside it, with the wipe.
  - **One Atlas page:** the Q30 page ("Atlas · Vocal Sessions") gets the notes store and becomes the home. The stage-2 prototype page is retired (its store is empty, so nothing is lost; it is only deleted if Ivan asks).
  - **"Check my notes"** in a Claude chat reads the Atlas page's notes and the notes of the prototypes it lists, in one format ("check my Atlas notes" still works).
  - Tests.
- **Agreed (defaults taken at Render):** the kit lives in its own public repo, MIT; a pinned copy, not a submodule; the Q30 page is home; prototype notes on a page not published on claude.ai stay on that device; "check my notes" covers both kits; each kit version gets its own Render and Build in that kit's `HANDOFF.md`, with no Q number. Notes have one home (the private Atlas page), so there are never two copies; only notes sent as queue ideas reach the repo, and as text only.
- **Out of scope:** compare views across screens or sizes (not queued); wiring up a second app or site; any change to the app.
- **The repo is public:** notes, pictures and screenshots never go into git.
- **Needs:** Q30 (shipped 2 Nov 2026 as tooling: `tools/atlas/`); Atlas kit 1.0 built and released.
- **Done when:**
  - Vocal Sessions scans exactly as Q30 did, through its settings file, and the kit copy in `tools/atlas/kit/` is unmodified.
  - Notes and layout survive a rescan and a reload, on phone and Mac, and Claude can list the notes from a chat, together with notes from a listed prototype.
  - The report has the screen, marked area, element details and note; the .zip has a picture per note; queue ideas come out text-only in this file's format.
  - A rescan after an app change shows the right new, gone and changed screens, and names the versions released in between.
  - The app's own full test suite still passes.

## Q34 · Interface: Native Menus and Controls

**Status:** Blocked: on hold for the parts kit (Ivan, 2 Nov 2026, 22:11: "yep hold"). Menus and controls will be built once in the parts kit, a separate kit planned from the Flutter library's parts, and this item gets a fresh Render when Vocal Sessions moves onto it. Do not Build the scope below as written. **Render:** 2 Nov 2026, 18:12. Ivan: "render", for the Blueprint as drafted with every *Default if unanswered* taken, after choosing both the worth-doing items and the smaller wins "for that extra polish" (18:05). **Build:** awaiting Ivan's instruction.

Menus, the top bar's buttons and the small controls move like iOS 27. Where the Flutter kit `sdegenaar/liquid_glass_widgets` (MIT) measured a number against real iPhone recordings, that number is used; otherwise its by-eye numbers are. The handoff and the inventory are in Ivan's project notes: `q34_interface_native_menus_controls_handoff.md` and `component_inventory_2026-11-02.md` (his private page "Component inventory · Vocal Sessions"). The measured values are in `liquid_glass_widgets_values.md` (+ `_part2.md`). Ask him to attach them.

- **Scope, stage 1 (menus and the top bar):**
  - **Long-press menus** (a song row, `#ctxmenu`; a lyric line in play-along, `#lmenu`), measured:
    - the menu opens at 700 ms (was 480 ms and `CK_HOLD`)
    - the row or line lifts to ×1.04 from about 200 ms, and letting go early opens nothing
    - the dim is 20% (light) / 25% (dark) with no blur, and the row stays sharp above it
    - it closes in 170 ms
    - right-click opens it straight away
  - **One menu style for every menu:** `.ctxmenu` and `.opmenu` become one component, with blur 22 over `#F5F5F7` at 80% (`#252528` in dark), a 0.5 pt border (black 30% / white 20%), the shadow `0 8px 33px rgba(0,0,0,.08)` and radius 18.
  - **Pull-down menus** (Songs' sort and heading menus, Recall, the session's and Application's sort menus):
    - they grow out of their button on new `menuOpen` (z 0.73, f 1.74 Hz) and `menuClose` (z 0.74, f 2.25 Hz) springs
    - no dim
    - the blur ramps in over 260 ms
  - **Top bar buttons**, measured. `renderBar()` keeps each slot's circle:
    - **New icon:** it blurs out (σ 6) and in (σ 3.5), with the circle swelling up to 22%.
    - **Appearing:** 250 ms, from 1.1 to 1, with the icon sharpening from an 8 px blur.
    - **Leaving:** 350 ms, with the icon gone by 55%.
    - It only runs when the bar redraws in place. Push, zoom and swipe back stay as Q08 built them.
- **Scope, stage 2 (controls), kit numbers by eye:**
  - **Toasts:** drop in from the top over 500 ms and leave upwards over 350 ms. They stay 3 s (was 1.9 s) unless the caller sets a time.
  - **Switches (`.tgl`):**
    - the knob travels over 380 ms (ease-in-out), widening while it moves and within 120 ms of a press
    - the knob can be dragged: a flick faster than 200 px/s decides it, otherwise whichever side it's past halfway
    - a tap on the row still toggles
  - **Segmented controls (`.seg`):**
    - the settled slide and squish stay for taps
    - new: the knob can be dragged, and settles on a `segSettle` spring (z 0.85, f 2.86 Hz)
    - the knob swells by 12 × 8 px while pressed
  - **Search fields:**
    - Songs' bottom search field stretches at most about 7 pt lengthwise and 2 pt up and down when dragged (measured)
    - plain text fields use the solid grey well, 12% light / 24% dark
  - Reduce Motion: fades only.
- **Defaults taken:** the 700 ms hold, menu radius 18, the bar morph only on in-place redraws, the segmented control's slide kept for taps, toasts 3 s.
- **Out of scope:**
  - Sheets' flick to close and their corners (moved to the Scroll Behaviour Pass draft).
  - Submenus, and the drag shrink for sheets that grow out of a button (the app has neither).
  - Swipe actions on rows, and the tab bar's highlight and dragging.
  - Waveform scrubbers (no knob). The kit's ×1.35 knob suits Q32's speed slider, but it isn't part of Q32 without its own Render.
  - Haptics.
- **Build order:** two stages in one build, with quick tests after each.
- **Needs:** Q33 built first (its materials and the `release` spring), and Q32 before that.
- **Done when:**
  - The hold, lift, dim and close timings above are met. Every menu shares one style.
  - Pull-down menus grow out of their button. Top bar circles morph, appear and leave with the measured timings, with labels and actions always right.
  - Toasts, switches, segmented controls and the search field behave as above. Taps work as before.
  - Reduce Motion gives fades only.
  - A new `tests/test_menus.py` (with a `controls` part) and a `morph` part in `test_native.py` pass at 375, 390 and 402 wide and on iPad. The fuzzer finds no menu left open, and the full suite passes.
  - Ivan checks on his iPhone: the 700 ms hold, the Songs sort menu, the gear and Back morph, dragging a switch and the Progress range control, and the 3 s toast.

---

## Not scheduled

Ideas kept so they aren't lost. None are queued; ask Ivan before planning any of them.

**How they're ranked.** Every idea is checked against the README's [What it's for](README.md#what-its-for), starting with its first test: *does it make practice easier, getting you singing faster with less fuss?*

- **Priority 1 · Core:** a bug that gets in the way of practice, or an idea that clearly serves the recordings, both halves of practice, connecting everything, or teaching.
- **Priority 2 · Helps:** makes practice smoother or easier to reach; practice works without it.
- **Priority 3 · Polish:** feel and finish only.
- **Parked · Doesn't fit:** clashes with what the app isn't (a grader, karaoke, a habit tracker). Kept with its reason so it isn't suggested again.

Each idea has its priority, the date it was added and a *Why* line. New ideas go into the right tier; within a tier, newest last. This section stays at the bottom of the file. Ivan can move anything.

### Priority 1 · Core

- **Bug: no floating window for a track started during play-along (found while building Q26, 2 Nov 2026; on 3.43 as well).** Starting a song's track (its player or a song row's play button) while Song Clock plays along gives the track no floating window. Play-along's own track pauses a moment later, and that pause closes the track's window (`fwPaused('track')` in window.js) after `NOW.start('track')` opened it. Needs its own Render; `tests/test_pip.py`'s `show()` stops play-along first to step round it.
  *Why:* it breaks practice with a song.
- **Exercise takes (2 Nov 2026; pinned from Q32 by Ivan).** Record yourself while a pattern plays on an exercise page: the take is kept on that exercise with its pattern, key and speed, and played back in the exercise's History, reusing the app's recorder and takes.
  *Why:* the recordings are the heart of the app, and this lets you hear your exercises improve, not only your songs.

### Priority 2 · Helps

- **Today widgets (2 Nov 2026).** Patterns and Song practice as widget cards on Today, with an "Edit Today" step to choose which show. Reuses the shared pattern player from Q32 · Exercises: Redesign.
  *Why:* more doors to practice, and fewer taps to start singing.
- **Reusing Chorus 1's timing for Chorus 2.** *Why:* less setting up before you can practise a song.
- **"Shift all timings" when a re-imported track is a different length.** *Why:* saves redoing timings by hand.
- **Learning tap lateness.** *Why:* play-along lines up better with less fiddling.
- **A demo recording on each mark's guide page.** *Why:* it teaches by ear, not only in words.
- **A shared song-screen dock.** *Why:* the same controls in the same place on every song screen.
- **Note lengths and attacks in the pattern player (2 Nov 2026).** Notes that can be sustained or short and detached, and different note lengths (rhythms), shown with music notes on the pattern drawing. Builds on the shared pattern player from Q32 · Exercises: Redesign.
  *Why:* runs are trained detached first, then connected, and rhythm makes patterns closer to real songs.

### Priority 3 · Polish

- **Motion leftovers (was 4d).** Optional; Ivan decides whether they're worth a build:
  - Holding a section in Annotate lifts it while the others ripple aside.
  - Perform's larger text scales up smoothly.
  - The recording bar rises, and Stop turns it into the takes sheet.
  - A session's progress dashes fill, and its step pill moves onto the shared springs.
  - All sessions' old list fades out before the new rows ripple in.
  *Why:* feel only; practice works the same without them.
- **Timeline drag and drop.** *Why:* nicer editing; the current way works.
- **A wide Timeline on iPad.** *Why:* iPad only.
- **Delivery marks for one repeat only.** *Why:* a rare case.
- **Mark selections across a line break.** *Why:* a rare case.

### Parked · Doesn't fit

None yet.
