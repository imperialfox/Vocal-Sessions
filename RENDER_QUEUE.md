# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.51** (3 Nov 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28; Q11 · Data: Save Safety in 3.29; Q12 · Song Clock: Timing Integrity in 3.30; Q13 · Interface: Keyboard Guards in 3.31; Q04 · Marks: Practice Guide in 3.32; Q23 · Interface: Status Bar Glow in 3.33; Q14 · Playback: Smooth Frames in 3.34; Q18 · Tests: GitHub Match in 3.35; Q15 · Marks: Register-Ready Data in 3.36; Q16 · Audio: Voice Analysis Foundations in 3.37; Q17 · Hygiene: Dead Code Sweep in 3.38; Q19 · Session: One-Page Flow in 3.39; Q20 · Session: Application Redesign in 3.40; Q21 · Session: Saved Screen in 3.41; Q22 · Session: Clock Redesign in 3.42; Q25 · Coach: Frame-Accurate Chapters in 3.43; Q26 · Window: Picture in Picture in 3.44; Q27 · Interface: Landscape Tab Bar Fit in 3.45; Q28 · Hygiene: Toggl Removal in 3.46; Q29 · Session: Song Rating Removal in 3.47; Q24 · Coach: Video Redesign (tooling, no app version: the render kit is in `tools/coach-video/`); Q30 · Atlas: Lightbox Core (tooling, no app version: the Atlas is in `tools/atlas/`); Q32 · Exercises: Redesign in 3.48; Q33 · Interface: Glass Native Tuning in 3.49; Q36 · Interface: Screen IDs in 3.50; Q31 · Atlas: Map and Notes (tooling, no app version); Q40 · Interface: Value Set and Test in 3.51; Q35 · Atlas: Starting States (tooling, no app version).

- **Every item has two separate gates.** `Awaiting Render` means it is not approved. Ivan's **Render** approves only the named item's exact scope and moves it to `Approved — awaiting Build`; it does not start work or authorize a push. A separate **Build** instruction starts implementation for that approved item. Do not treat approval of one item as approval of the whole queue.
- **The code wins on what's built.** This is a summary, not a spec. Check each note against the code before relying on it.
- **Detailed design notes live in Ivan's private project notes, not in this repo.** Where an item names one, ask Ivan to paste or attach it. Anything not settled here is marked *Unresolved*.
- **Check ideas against the app's purpose.** Before planning an item or a Not scheduled idea, ask the first test in [README › What it's for](README.md#what-its-for): does it make practice easier?
- **Ivan can reorder the queue.** Versions follow build order: each build takes the next minor version when it's built.
- **[Release order](#release-order) is the order to build in.** Render places the item in it (at the end unless Ivan says where; tooling with no app version goes under *Any time*), with "needs Q##" in its reason for anything that must ship first. The Build that ships an item removes it from the list in the same push. The [Render queues](https://imperialfox.github.io/render-queue/) dashboard reads this list for Up next and Next build.
- **When an item ships,** remove its section from this file in the same push and set its row in the table below to `Shipped <version>`. Its `CHANGELOG.md` headline (the `*…*` line under the version) ends with its queue ID, e.g. `*Waveform sections on the track player (Q02)*`. The `##` line itself stays `## 3.23 · 27 Oct 2026`, which the app's Changelog page reads.

## Naming

Every queued item has a queue ID and a standard name, used in the queue, in handoffs, in commit messages and in file names. Use these, not the older working names.

- **Items:** `Q[##] · [Subsystem]: [Feature Name]`, e.g. `Q02 · Track: Waveform Sections`.
- **Files** (handoffs, specs, wireframes, prototypes): `q##_[subsystem]_[feature]_[type].[ext]`, lower case with underscores, e.g. `q02_track_waveform_sections_handoff.md`.
- **Releases:** the shipped version's `CHANGELOG.md` headline ends with the queue ID in brackets, e.g. `*Waveform sections on the track player (Q02)*` under `## 3.23 · 27 Oct 2026` (the `##` line keeps its exact format for the app's Changelog page). That's the bridge from queue ID to version. Q01 shipped as 3.22, headline `*Search, from every tab (Q01)*`; Q08 as 3.23.
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q42**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
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
| Q31 | Atlas: Map and Notes | Shipped (tooling, no app version) | Visual App Atlas stage 2, map, notes, export, changes since last scan, 2 Nov 2026; re-scoped onto the Atlas kit, 2 Nov 2026, 19:50; widened with the Atlas kit 1.1 phone pass, 3 Nov 2026, 11:21 |
| Q32 | Exercises: Redesign | Shipped 3.48 | Exercise patterns the app plays, Exercise page redesign (both 31 Oct), merged 2 Nov 2026 |
| Q33 | Interface: Glass Native Tuning | Shipped 3.49 | Glass tuning Recon and glass inventory, 2 Nov 2026 |
| Q34 | Interface: Native Menus and Controls | Retired → Q41 | Component inventory (round 2), worth doing plus smaller wins, 2 Nov 2026; on hold for the parts kit from 2 Nov, replaced by Q41 at its Render on 4 Nov 2026 |
| Q35 | Atlas: Starting States | Shipped (tooling, no app version) | Atlas: more starting states (Not scheduled idea), from the screen-flow canvas update, 3 Nov 2026 |
| Q36 | Interface: Screen IDs | Shipped 3.50 | Screen IDs blueprint (permanent IDs for every screen, part names, flows, saved-data list), 3 Nov 2026 |
| Q37 | Session: Song Ladder | Shipped 3.52 | Song ladder, pitch test page, "Prototype · Song ladder and bridge-aware patterns" (v1–v3), 2 Nov 2026 |
| Q38 | Exercises: Bridge-Aware Patterns | Shipped 3.53 | Bridge-aware patterns, Find your bridge, same prototype, 2 Nov 2026 |
| Q39 | Songs: Key and Scale Lanes | Approved — awaiting Build | Key detection, scale lanes, suggested patterns, same prototype (v2), 2 Nov 2026 |
| Q40 | Interface: Value Set and Test | Shipped 3.51 | The value test (consistency audit of 3.49, 2 Nov 2026; called Q35 in early notes before Q35 went to Atlas: Starting States) |
| Q41 | Interface: Parts Kit Move | Approved — awaiting Build | The move of Vocal Sessions onto the parts kit (replaces Q34), Blueprint 4 Nov 2026 |

Work shipped before this standard (for example Track 1 and Song Clock A1) keeps its version numbers and has no queue ID.

Every item also follows [MAINTAINING.md](MAINTAINING.md): its [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [changelog](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style). On top of that:

- **Check the previous build is live first.** Use the item's **Needs** line. If it records that its required version was verified on `main`, that satisfies this check; otherwise look for the version in `CHANGELOG.md` on `main`. If it isn't there, stop and tell Ivan.
- **Never push with failing tests.** If something can't be finished, commit nothing, leave the item here and report plainly.
- **Everything that moves uses the shared springs.** Every new sound starts through `NOW.start()`.
- **The repo is public.**
  - Never commit real music, recordings, the coach video, course media, lyrics or backups.
  - Never commit with Ivan's personal email. Claude commits as `Claude <noreply@anthropic.com>`.

---

## Release order

Build top to bottom; each still needs its own **Build**. One line per item: `N. Q## — reason`, with "needs Q##" for anything that must ship first. Names live in the table above. The paragraph under Order below is the history behind it.

1. Q39 — needs Q37 (shipped in 3.52)
2. Q41 — needs parts kit 1.1 (`imperialfox/parts-kit`, built first); after Q38 (shipped in 3.53) and Q39 (Ivan, 4 Nov 2026)

## Order (3 Nov 2026)

**Q41** (Render 4 Nov 2026, 09:57) moves Vocal Sessions onto the parts kit and replaces **Q34**, which is now Retired. It needs parts kit 1.1 built first (a kit version, recorded in the kit's own handoff) and comes after Q38 and Q39. **Q38** shipped in 3.53 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 10:06): your bridge with Find your bridge (VS-096), the bridge band, softer notes and cue on the exercise page, Stop one past last time, Last time and Listen while I sing (MAINTAINING › Bridge-aware patterns); its scope is in this file's history and the handoff. **Q37** shipped in 3.52 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 00:38): the shared pitch listener (`PITCH`, `js/pitch.js`, with pitchy pinned in `js/pitchy.js`) and the song ladder on Application's card (MAINTAINING › The pitch listener, Song ladder); its scope is in this file's history and the handoff. Q38 and Q39 build on its pitch listener. **Q35** shipped on 3 Nov 2026 as tooling (Build 3 Nov 2026, 17:20): Vocal Sessions' Atlas now has starting states for the coach video, recording and takes, How did it go?, the peek card, Check timing's Overlaps, Past the new end and the rescued copy, a caption for every screen, the flows F-01 and F-02, and hand-written doors (`tools/atlas/README.md` › Starting states); its scope is in this file's history and the handoff. **Q40** shipped in 3.51 (Render 3 Nov 2026, 08:08; Build 3 Nov 2026, 17:19): the named value set at the top of `css/app.css`, `MOTION.EASE`, and `tests/test_values.py` with its shrinking known list (MAINTAINING › Value set); its scope is in this file's history and the handoff. **Q31** shipped on 3 Nov 2026 as tooling (Build 3 Nov 2026, 13:36): Vocal Sessions' Atlas now runs on Atlas kit 1.1.0 (`tools/atlas/kit/`), which its Build made first; its scope is in this file's history and the handoff. **Q37–Q39** (Render 3 Nov 2026, 08:01) are app builds, in that order after Q36, each with its own Build: Q37 brings the shared pitch listener that Q38 and Q39 use. **Q36** shipped in 3.50 (Render 3 Nov 2026, 08:00; Build 3 Nov 2026, 08:15): its register is `js/register.js`, since `js/screens.js` already held the main screens' code. **Q35**'s flows, captions and doors use its IDs. The same Render added Atlas kit 1.0's addition 14 (Stable IDs), still to be built with the kit. **Q35** (Render 3 Nov 2026, 00:39) comes after Q31, which reshapes the settings file it fills in; tooling with no app version, like Q30 and Q31. The same Render widened **Atlas kit 1.0** with additions 9–13 (in that kit's handoff), which Q31's kit copy brings and Q35 uses. **Q33** shipped in 3.49 (Render 2 Nov 2026, 17:41; Build 2 Nov 2026, 21:17). **Q34** (Render 2 Nov 2026, 18:12) is on hold for the parts kit (Ivan, 2 Nov 2026, 22:11); it uses Q33's materials and springs. **Q32** shipped in 3.48 (Render 2 Nov 2026, 15:56; Build 2 Nov 2026, 19:06). Q30 shipped as tooling (Build 2 Nov 2026, 17:57; `tools/atlas/`), and **Q31** builds on it (Render 2 Nov 2026, 15:55, in the same instruction as Q30; re-scoped by a fresh Render at 19:50 to put Vocal Sessions on the universal Atlas kit, built after Prototype kit 1.1 and Atlas kit 1.0; its own Build). Atlas kit 1.0 was built on 3 Nov 2026; Q31 was widened at 11:21 with the Atlas kit 1.1 phone pass, which its Build makes first. Both are tooling with no app version, like Q24, so they can be built outside the app queue's order. Q28 shipped in 3.46 and Q29 in 3.47 (Render 2 Nov 2026, 09:29; Build 09:33, in one instruction, built one after the other). **Q07** is still awaiting Render. Q27 shipped in 3.45 (Build 2 Nov 2026). Q25 shipped in 3.43 and Q26 in 3.44 (Build 2 Nov 2026); Q25–Q27 got Render on 1 Nov 2026 (19:59), in one instruction, each with its own Build. Q19 shipped in 3.39, Q20 in 3.40, Q21 in 3.41 and Q22 in 3.42. Q22 got Render on 31 Oct 2026 (20:59) and was built on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction, each with its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q07 · Song Clock: Dynamic Sync

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

- **Scope:** paced Recall, and recording against the clock.
- **Decided:** marks over Recall's pills stay still while words reveal (a test, not new behaviour).
- **Next action:** confirm dates and scope with Ivan.
- **Done when:** *Unresolved.*

## Q41 · Interface: Parts Kit Move

**Status:** Approved — awaiting Build. **Render:** 4 Nov 2026, 09:57. Ivan: "render for the move", for the Blueprint as written at 10:00 with every *Default if unanswered* taken. **Build:** awaiting Ivan's instruction. The build handoff is in Ivan's project notes as `q41_interface_parts_kit_move_handoff.md` (plan `vs_parts_kit_move_blueprint.md`). Replaces Q34 · Interface: Native Menus and Controls (Retired; its agreed numbers became the parts kit's defaults).

- **Goal:** the menus, sheets, alerts, toasts, switches, segmented controls, slider, tab bar, top bar buttons and rows come from the parts kit, and every look decision (D01–D18 in Ivan's decision register) is one line in `js/parts.settings.js`.
- **Scope, one app version in four stages:**
  1. **Add the kit:** parts kit 1.1.0 pinned unchanged (`css/parts-kit.css`, `js/parts-kit.js`, docs and checksums in `tools/parts-kit/`), the settings file, and the kit runs the motion (D18): `js/motion.js` keeps its helpers but reads springs, speed and Reduce Motion from `Parts.motion`; Settings › Accessibility calls the kit and still saves the choices on the device. The app lists only its differences from the kit (none today), checked by a difference test. Nothing you'd see changes.
  2. **Pop-ups:** toasts, alerts (D08), action sheets (D07), menus in one style with 20 corners and a 700 ms hold (D16), and sheets inside the kit's sheet (D09, D10, D14, D15, D17).
  3. **Controls and bars:** switches, segmented controls (D04), the speed slider (D03), the tab bar (D01, D02), top bar buttons, the search field.
  4. **Rows:** a highlight while pressed instead of shrinking (D06).
- **Default if unanswered (all taken):**
  - The app keeps its own sheet system (which sheet is open, back between sheets) and draws each sheet inside the kit's sheet.
  - Every `confirmSheet()` sheet becomes an alert; sheets that are only a list of choices become action sheets (probably VS-050, VS-055, VS-058, VS-066, VS-068; the Build checks each and lists them in the handoff first); the rest stay sheets.
  - The kit's tab bar replaces the app's; the dock's other states stay the app's own.
  - The named shadow set only on parts that move here.
  - The next minor version; the decisions register's move into `DECISIONS.md` stays its own piece of work.
  - A plain list of everything replaced in `tools/parts-kit/REPLACED.md`, for the reference sheets item that follows.
- **Out of scope:** the element, saved-data and wording reference sheets (the next item); `DECISIONS.md`; the Scroll Behaviour Pass's other fixes; placing D11–D13 (they stay off); the floating window, session clock ring and coach video controls; waveform scrubbers, swipe actions, reorderable lists, haptics; Smart file drop; any change to the kit itself.
- **Needs:** parts kit 1.1 built first (spring overrides, one-element timings, `Parts.differences()`). After Q38 and Q39 in Release order.
- **Done when:** the kit copy is unchanged and its settings load cleanly; the kit owns the motion and Speed 0, slow motion and forced Reduce Motion reach every part and survive a reload; D01–D10 and D14–D18 behave as recorded and D11–D13 are off; no long-press menu before 700 ms, toasts stay 3 s, every sheet has 46 corners and closes on a flick; every confirmation is an alert and each still does what it did; the value test's known list only shrinks; the Atlas opens every screen with no new "Failed"; `tests/test_parts.py` passes at 375, 390 and 402 wide and on iPad, and the full suite passes locally and on GitHub.
- **Build order:** four stages in one fresh chat, quick tests after each, the full suite once before pushing; one receipt.

---

## Q39 · Songs: Key and Scale Lanes

**Status:** Approved — awaiting Build. **Render:** 3 Nov 2026, 08:01, in the same instruction as Q37 and Q38. **Build:** awaiting Ivan's instruction. The build handoff is in Ivan's project notes as `q39_songs_key_and_scale_lanes_handoff.md`.

- **Goal:** sing a song in its key. The app finds the song's key, lays the scale over your pitch lines, and suggests patterns from the library in that key.
- **Scope:**
  - **A key per song:** worked out from the song's takes (a 12-note profile of their steady pitch, then Krumhansl–Schmuckler, from musictheoryjs 3.2.2, ISC, as a pinned copy). When the top two keys are close, it asks ("Which key is this song in? F major · D minor · Other…"); otherwise it suggests one. Other… and Change open a key sheet (Major or Minor, and 12 notes, spelled as in each key). Chosen once and saved on the song. Doors: Lines and the song's page.
  - **Scale lanes** on pitch lines (Lines and the live line): the key's notes as faint lanes, with the home note marked and names spelled from tonal 6.5.1 (MIT, pinned copy). A switch turns them off. Descriptive only.
  - **Practise in the key:** the note to work on (where the lines part, or else the line's top note), then up to three library patterns that play in the song's key and reach that note. Each shows its range and what it trains, with Play and a door into the pattern player on that note, staying on this key. Q37's note buttons follow the key once it's set.
- **Default if unanswered:**
  - One key per song (key changes within a song later).
  - Suggested patterns start on the key's home note, keep every note in the key and go no lower than A2, one from each group where possible. When nothing reaches the note exactly, patterns that pass through it are offered instead.
  - Opening one doesn't change the exercise's saved choices.
  - With lanes on, they replace Q38's bridge band on pitch lines.
- **Out of scope:** chords, moving a song to another key, any score or right/wrong colouring.
- **Needs:** Q37 shipped. The pattern player opening on a given pattern, note and Stay on this key is part of this item.
- **Done when:** the key is found and asked or suggested correctly for synthetic melodies; the key sheet saves to the song (and survives a backup); lanes are spelled correctly in sharp and flat keys; suggestions follow the rules above and open the pattern player as described; old data loads unchanged; 375 px and dark mode; the full suite passes; Ivan's iPhone checks.

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
- **Song note map (3 Nov 2026).** Map a song's notes, roughly, from its uploaded track, and show them as a faint melody line on Lines and the Track player (VS-010), opened from the Song page (VS-009). Ivan's choice of how it reads the song: if a vocals-only stem is attached to the song (for example exported from Resolve Studio's Music Remixer), run Q37's `PITCH` listener (pitchy) on it; otherwise separate the lead vocal on the phone (onnxruntime-web, MIT, WebGPU with a WebAssembly fallback; first choice the UVR MDX-Net karaoke model, 52.8 MB, MIT with credit to UVR) and run pitchy on that. pitchy alone on a full mix jumps between the singer and the instruments. Melodia in Essentia.js was dropped on 3 Nov 2026: it is AGPL v3 for non-commercial use only, which clashes with the app's MIT licence. If separating isn't possible or is too slow, the note map still runs on the full song, clearly labelled as rough, with a nudge that attaching vocals makes it cleaner (Ivan, 3 Nov 2026). The demucs-rs demo was slow and unreliable on his iPhone and MacBook; next step: he times the karaoke model on his iPhone with the test page "Vocal Sessions · Vocal isolation test". Research: project note `claude/vocal_isolation_recon_2026-11-03.md`. The note map is small and kept as its own file on the song, in backups, while the track and any separated vocal stay out of them. It could feed Q39 (the key from the song itself, not only from takes), the Q37 ladder's target notes and the note buttons. Lines and dots only: a reference, never a score. Needs Q37.
  *Why:* it helps you learn your songs and teaches pitch by showing where the melody goes.
- **Reference sheets: elements, saved data and wording (4 Nov 2026; Ivan: high priority).** Three sheets in one `reference/` folder with one index page. Elements: every element with its screen (VS ID), kit part or the app's own, the spring, duration, corner and press it uses, its decision ID and a status (In use · Phasing out · Retired, nothing deleted). Saved data: every key the app stores, whether it's in backups, and the version that added it. Wording: every label, toast, alert and empty-state line, read from the code. Built by a script at each build, plus a visual page, with tests that fail when an element or key has no row or a retired value comes back. Comes right after Q41, which leaves it `tools/parts-kit/REPLACED.md` for the Retired rows. Plan notes: `element_sheet_idea_2026-11-04.md` in Ivan's project notes.
  *Why:* it's behind the scenes, but every later change starts from one place that says what exists and what replaced what, so features that make practice easier are quicker and safer to build (Ivan: "it will make things easier next time").

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
- **Smart file drop (3 Nov 2026).** Drag a file onto the app, or bring it in from the phone, and the app works out what to do with it from the file type and the screen you're on. Ivan's example: Add song (VS-045) and New song (VS-051) should take a dropped file. First guesses, to settle at wireframe: on Add song or New song, a song file starts a new song with it as the track (named from the file) and a text file becomes the words; on the Song page (VS-009), a song file becomes the track, or the vocals-only stem for the Song note map if its name says vocals or acapella (asking when unsure); a backup file anywhere offers Import backup (never restores without asking); anywhere else, one short "Use this for…" sheet with the likeliest choice first, so it doesn't add choice fatigue. **Phone limits to check:** an iPhone Home Screen web app can't appear in the Share sheet (Safari hasn't shipped the Web Share Target API, so only Chrome on Android has it; WebKit bug 194593), so on the phone the doors are drag and drop (holding a file in Files and switching apps; test on iOS 26) and the app's own file pickers. Drag and drop works on a computer and iPad. **Next:** wireframe after the parts kit is done (the new kit of glass parts, not the prototype kit), so the wireframes and prototype can pull their parts from it (Ivan, 3 Nov 2026; which kit confirmed 20:50). New song's part of it follows decision D10 option A: a dropped file does what picking one does, so the sheet grows to full (`claude/parts_decisions_2026-11-02.md`).
  *Why:* another door in that saves taps, the several-doorways principle.

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
- **Spectrogram view (3 Nov 2026).** A spectrogram of a song's track or a take (time across, pitch up, brightness for loudness), like the one in the demucs-rs demo Ivan tried while researching vocal isolation for the Song note map. It could be animated later, for example scrolling live while a take records or plays. Ivan sees it as "just a cool thing to look at". It could also teach one day: a voice's harmonics show as stacked stripes, and a ringing tone shows as a bright band high up. Low priority.
  *Why:* feel only; practice works the same without it.

### Parked · Doesn't fit

None yet.

## Ivan's to-do

Things for Ivan to look at himself, at some point. Not queue items: nothing here is planned or approved. Tick one off by deleting its line.

- **Parts kit and the prototype kit (3 Nov 2026).** Decision 6 of the parts kit 1.0 Blueprint (`claude/parts_kit_1_0_blueprint.md` in the Singing project): should the prototype kit, and the shared rules file the kits keep identical (`SHARED.md`), change so prototypes load the parts kit? Until he decides, the default stands: parts kit 1.0 changes neither, and joins `SHARED.md` with the first prototype that uses it (Smart file drop's).
