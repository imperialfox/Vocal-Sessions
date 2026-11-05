# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.51** (3 Nov 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28; Q11 · Data: Save Safety in 3.29; Q12 · Song Clock: Timing Integrity in 3.30; Q13 · Interface: Keyboard Guards in 3.31; Q04 · Marks: Practice Guide in 3.32; Q23 · Interface: Status Bar Glow in 3.33; Q14 · Playback: Smooth Frames in 3.34; Q18 · Tests: GitHub Match in 3.35; Q15 · Marks: Register-Ready Data in 3.36; Q16 · Audio: Voice Analysis Foundations in 3.37; Q17 · Hygiene: Dead Code Sweep in 3.38; Q19 · Session: One-Page Flow in 3.39; Q20 · Session: Application Redesign in 3.40; Q21 · Session: Saved Screen in 3.41; Q22 · Session: Clock Redesign in 3.42; Q25 · Coach: Frame-Accurate Chapters in 3.43; Q26 · Window: Picture in Picture in 3.44; Q27 · Interface: Landscape Tab Bar Fit in 3.45; Q28 · Hygiene: Toggl Removal in 3.46; Q29 · Session: Song Rating Removal in 3.47; Q24 · Coach: Video Redesign (tooling, no app version: the render kit is in `tools/coach-video/`); Q30 · Atlas: Lightbox Core (tooling, no app version: the Atlas is in `tools/atlas/`); Q32 · Exercises: Redesign in 3.48; Q33 · Interface: Glass Native Tuning in 3.49; Q36 · Interface: Screen IDs in 3.50; Q31 · Atlas: Map and Notes (tooling, no app version); Q40 · Interface: Value Set and Test in 3.51; Q35 · Atlas: Starting States (tooling, no app version).

- **Every item has two separate gates.** `Awaiting Render` means it is not approved. Ivan's **Render** approves only the named item's exact scope and moves it to `Approved — awaiting Build`; it does not start work or authorize a push. A separate **Build** instruction starts implementation for that approved item. Do not treat approval of one item as approval of the whole queue.
- **The code wins on what's built.** This is a summary, not a spec. Check each note against the code before relying on it.
- **Detailed design notes live in Ivan's private project notes, not in this repo.** Where an item names one, ask Ivan to paste or attach it. Anything not settled here is marked *Unresolved*.
- **Check ideas against the app's purpose.** Before planning an item or a Not scheduled idea, ask the first test in [README › What it's for](README.md#what-its-for): does it make practice easier?
- **Ivan can reorder the queue.** Versions follow build order: each build takes the next minor version when it's built.
- **[Release order](#release-order) is the order to build in.** Render places the item in it (at the end unless Ivan says where; tooling with no app version goes under *Any time*), with "needs Q##" in its reason for anything that must ship first. The Build that ships an item removes it from the list in the same push. Render also fills the item's **Size** in the table (Light, Light to medium, Medium, Medium to heavy or Heavy, the effort guessed in its handoff) and ends its Release order line with the approval stamp `(Ivan, 4 Nov 2026)`. The [Render queues](https://imperialfox.github.io/render-queue/) dashboard reads this list for Up next and Next build, and the Size column for each item's size ring.
- **When an item ships,** remove its section from this file in the same push and set its row in the table below to `Shipped <version>`. Its `CHANGELOG.md` headline (the `*…*` line under the version) ends with its queue ID, e.g. `*Waveform sections on the track player (Q02)*`. The `##` line itself stays `## 3.23 · 27 Oct 2026`, which the app's Changelog page reads.

## Naming

Every queued item has a queue ID and a standard name, used in the queue, in handoffs, in commit messages and in file names. Use these, not the older working names.

- **Items:** `Q[##] · [Subsystem]: [Feature Name]`, e.g. `Q02 · Track: Waveform Sections`.
- **Files** (handoffs, specs, wireframes, prototypes): `q##_[subsystem]_[feature]_[type].[ext]`, lower case with underscores, e.g. `q02_track_waveform_sections_handoff.md`.
- **Releases:** the shipped version's `CHANGELOG.md` headline ends with the queue ID in brackets, e.g. `*Waveform sections on the track player (Q02)*` under `## 3.23 · 27 Oct 2026` (the `##` line keeps its exact format for the app's Changelog page). That's the bridge from queue ID to version. Q01 shipped as 3.22, headline `*Search, from every tab (Q01)*`; Q08 as 3.23.
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q58**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
- **Exception, 30 Oct 2026:** Ivan asked for the six stages of the 30 Oct read-only audit, plus its clean-up list, to get IDs straight away, before Render, most critical first. They are **Q11–Q17**. All seven got Render on 30 Oct 2026 and have shipped (3.29–3.31, 3.34, 3.36, 3.37 and 3.38).
- **Exception, 31 Oct 2026:** Ivan asked for the status bar fix to be queued with an ID before Render. It is **Q23**; Render and Build followed the same evening (shipped in 3.33).

Every ID with its **Status** (`Awaiting Render`, `Approved — awaiting Build`, `Building`, `Shipped <version>`, `Blocked`, `Retired`, or `Not scheduled` for an item with an ID that was moved back to the ideas list) and the working names older chats, notes and prototypes use. Render adds the row (or sets it to `Approved — awaiting Build`); the Build that ships it sets `Shipped <version>` in the same push.

| Queue ID | Standard name | Status | Size | Earlier working names |
|---|---|---|---|---|
| Q01 | Search: Global Find | Shipped 3.22 | | Render 10, Search, Global Search |
| Q02 | Track: Waveform Sections | Shipped 3.24 | | Track 2, Sections on the waveform |
| Q03 | Marks: Layered Annotations | Shipped 3.27 | | Marks 1, Layered marks |
| Q04 | Marks: Practice Guide | Shipped 3.32 | | Marks 2, Marks help, Marks guide |
| Q05 | Song Clock: Tap Re-Anchor | Shipped 3.28 | | Song Clock A2, Render 6, Line pass and retime |
| Q06 | Song Clock: Timeline View | Retired → Q05 | | Song Clock B, Render 7, Section starts and wheels |
| Q07 | Song Clock: Dynamic Sync | Not scheduled (Priority 2, ID kept) | | Song Clock C, Render 8, Paced Recall |
| Q08 | Interface: Native iOS Polish | Shipped 3.23 | | Native bars, iOS 27 polish |
| Q09 | Track: Waveform Sections Follow-up | Shipped 3.25 | | Giant 3-Pad dock, Q02 follow-up |
| Q10 | Interface: HIG Foundations Pass | Shipped 3.26 | | Vault ideas wireframes |
| Q11 | Data: Save Safety | Shipped 3.29 | | Audit stage 1, data safety |
| Q12 | Song Clock: Timing Integrity | Shipped 3.30 | | Audit stage 2, timing integrity |
| Q13 | Interface: Keyboard Guards | Shipped 3.31 | | Audit stage 3, input hygiene |
| Q14 | Playback: Smooth Frames | Shipped 3.34 | | Audit stage 4, per-frame work |
| Q15 | Marks: Register-Ready Data | Shipped 3.36 | | Audit stage 5, room for register data |
| Q16 | Audio: Voice Analysis Foundations | Shipped 3.37 | | Audit stage 6, Web Audio seam |
| Q17 | Hygiene: Dead Code Sweep | Shipped 3.38 | | Audit clean-up list |
| Q18 | Tests: GitHub Match | Shipped 3.35 | | Workflow review, 31 Oct 2026 |
| Q19 | Session: One-Page Flow | Shipped 3.39 | | One-page session prototype, 31 Oct 2026 |
| Q20 | Session: Application Redesign | Shipped 3.40 | | One-page session prototype, 31 Oct 2026 |
| Q21 | Session: Saved Screen | Shipped 3.41 | | "Session saved" splash, 2+5, 31 Oct 2026 |
| Q22 | Session: Clock Redesign | Shipped 3.42 | | Session clock ring prototype, 31 Oct 2026 |
| Q23 | Interface: Status Bar Glow | Shipped 3.33 | | Gradient clipped at the top, 31 Oct 2026 |
| Q24 | Coach: Video Redesign | Shipped (tooling, no app version) | | Coach video redesign, 31 Oct–1 Nov 2026 |
| Q25 | Coach: Frame-Accurate Chapters | Shipped 3.43 | | Coach timings, level picker, 1 Nov 2026 |
| Q26 | Window: Picture in Picture | Shipped 3.44 | | Floating window picture in picture and audit fixes, 1 Nov 2026 |
| Q27 | Interface: Landscape Tab Bar Fit | Shipped 3.45 | | "Exerc" cut off on its side, 1 Nov 2026 |
| Q28 | Hygiene: Toggl Removal | Shipped 3.46 | | Get rid of Copy for Toggl, 2 Nov 2026 |
| Q29 | Session: Song Rating Removal | Shipped 3.47 | | Remove "Rate the song", 2 Nov 2026 |
| Q30 | Atlas: Lightbox Core | Shipped (tooling, no app version) | | Visual App Atlas stage 1, Lightbox, 2 Nov 2026 |
| Q31 | Atlas: Map and Notes | Shipped (tooling, no app version) | | Visual App Atlas stage 2, map, notes, export, changes since last scan, 2 Nov 2026; re-scoped onto the Atlas kit, 2 Nov 2026, 19:50; widened with the Atlas kit 1.1 phone pass, 3 Nov 2026, 11:21 |
| Q32 | Exercises: Redesign | Shipped 3.48 | | Exercise patterns the app plays, Exercise page redesign (both 31 Oct), merged 2 Nov 2026 |
| Q33 | Interface: Glass Native Tuning | Shipped 3.49 | | Glass tuning Recon and glass inventory, 2 Nov 2026 |
| Q34 | Interface: Native Menus and Controls | Retired → Q41 | | Component inventory (round 2), worth doing plus smaller wins, 2 Nov 2026; on hold for the parts kit from 2 Nov, replaced by Q41 at its Render on 4 Nov 2026 |
| Q35 | Atlas: Starting States | Shipped (tooling, no app version) | | Atlas: more starting states (Not scheduled idea), from the screen-flow canvas update, 3 Nov 2026 |
| Q36 | Interface: Screen IDs | Shipped 3.50 | | Screen IDs blueprint (permanent IDs for every screen, part names, flows, saved-data list), 3 Nov 2026 |
| Q37 | Session: Song Ladder | Shipped 3.52 | | Song ladder, pitch test page, "Prototype · Song ladder and bridge-aware patterns" (v1–v3), 2 Nov 2026 |
| Q38 | Exercises: Bridge-Aware Patterns | Shipped 3.53 | | Bridge-aware patterns, Find your bridge, same prototype, 2 Nov 2026 |
| Q39 | Songs: Key and Scale Lanes | Shipped 3.54 | | Key detection, scale lanes, suggested patterns, same prototype (v2), 2 Nov 2026 |
| Q40 | Interface: Value Set and Test | Shipped 3.51 | | The value test (consistency audit of 3.49, 2 Nov 2026; called Q35 in early notes before Q35 went to Atlas: Starting States) |
| Q41 | Interface: Parts Kit Move | Shipped 3.55 | | The move of Vocal Sessions onto the parts kit (replaces Q34), Blueprint 4 Nov 2026 |
| Q42 | Songs: Sheet Music Reader and Score | Shipped 3.56 | Heavy | Sheet music reader, milestone M1a of the Sheet Music Reader Blueprint (draft 11), 4 Nov 2026; prototype "Sheet music reader · prototype" (v2) |
| Q43 | Audio: Recorded Piano and Soft Tone | Shipped 3.57 | Medium | Sound test, "Sound test · Vocal Sessions" prototype (v3): options 2 and 4, the pop on Piano-ish, 4 Nov 2026 |
| Q44 | Interface: Motion Smoothness | Shipped 3.58 | Light to medium | Motion and performance review of 3.55, fixes 1 to 5 (the nudge, the slow start, Today resting, the hidden corner animation, the exercise glow), 4 Nov 2026 |
| Q45 | Interface: Kit Top Bar and Search | Shipped 3.59 | Medium | The same review's 5b to 5e: the top blur over the bar's buttons, Today's title on kit part 3, the top bar and soft edge on kit parts 2 and 51, search at the bottom on kit part 6, 4 Nov 2026 |
| Q46 | Atlas: Screen States | Approved — awaiting Build | Light to medium | Atlas capture speed-up, "Atlas screen states and fast pictures" Blueprint piece B, layers 1 and 2 of the capture Recon, 4 Nov 2026 |
| Q47 | Songs: Sheet Music Guide and Views | Shipped 3.60 | Medium to heavy | Sheet Music Reader Blueprint draft 11, milestone M1b, 5 Nov 2026 |
| Q48 | Interface: Name Every Button | Shipped 3.61 | Medium | Name every button (Not scheduled idea, 4 Nov 2026), "Button names plan" (overnight card, 5 Nov 2026), Blueprint draft 2 and its Recon, 5 Nov 2026 |
| Q49 | Interface: Draw Speed and One Cancel | Shipped 3.62 | Light to medium | Random taps and speed Recon of 3.61, 5 Nov 2026 |
| Q50 | Interface: One Door Rule | Shipped 3.63 | Light | UI consistency audit of 3.62, fix group A (findings 1 to 3), 5 Nov 2026 |
| Q51 | Songs: Kit Search Bar | Approved — awaiting Build | Medium | The same audit, fix group B (finding 4) |
| Q52 | Interface: Kit Motion Match | Approved — awaiting Build | Light to medium | The same audit, fix group C (findings 5 to 7; decisions D20 to D22) |
| Q53 | Interface: Kit Buttons | Approved — awaiting Build | Medium | The same audit, fix group D (findings 8 and 9) |
| Q54 | Interface: Value Tidy and Guard | Approved — awaiting Build | Light to medium | The same audit, fix group E (findings 10 to 12) |
| Q55 | Interface: Element Sheet Values | Approved — awaiting Build | Medium | The same audit, fix group F (finding 14); "values come later" in the element sheet |
| Q56 | Settings: Reset All Alert | Approved — awaiting Build | Light | The same audit, finding 13 (decision D23) |
| Q57 | Songs: Sheet Music Formats | Approved — awaiting Build | Medium to heavy | UG's own PDF download rejected by 3.56 to 3.58 (finding, 4 Nov 2026), the vector PDF Recon and the Sheet Music Formats Blueprint (draft 1), 5 Nov 2026 |

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

1. Q57 — High: UG's own PDF download (from the UG app) is rejected today; a second reader beside the picture reader, built so more sources can be added; needs Q42 and Q47 (shipped in 3.56 and 3.60) (Ivan, 5 Nov 2026)
2. Q51 — High: Songs' own search bar is an older copy of the kit's search field; needs Q50 (shipped in 3.63) (Ivan, 5 Nov 2026)
3. Q52 — the page behind sheets, the push and Reduce Motion follow the kit (D20 to D22); needs Q51 (Ivan, 5 Nov 2026)
4. Q53 — every button presses through the kit and `PRESS` retires; needs Q52 (Ivan, 5 Nov 2026)
5. Q54 — the hand-written values left get names and the value test guards the code; needs Q53 (Ivan, 5 Nov 2026)
6. Q55 — the element sheet gets each part's kit part and values; needs Q54 (Ivan, 5 Nov 2026)
7. Q56 — Reset all data as a three-button alert (D23); needs Parts kit 1.3.0 and Q55 (Ivan, 5 Nov 2026)

### Any time

- Q46 — needs Atlas kit 1.2.0 (Q48 shipped in 3.61); tooling, no app version: a state for every screen so a rescan takes every picture quickly (Ivan, 4 Nov 2026)

## Order (3 Nov 2026)

**Q57** (Render 5 Nov 2026, 10:45) goes first in Release order, as the Blueprint's decision 8 set it (Ivan called it important). It adds a second sheet music reader for UG's own PDF download, which the UG app gives, beside the picture reader for Safari prints. It needs Q42 and Q47 (shipped) and doesn't touch Q51 to Q56, which can follow in their own order. **Q50** shipped in 3.63 (Build 5 Nov 2026, in the same chat as the audit, Ivan's choice): the door rule (MAINTAINING › Motion › The door rule), the gear, Today's suggested rotation, Show all sessions and song practice, the song page's Song practice row and Exercises' Add coach video push, and Back returns to the tab you were on; its scope is in this file's history and the handoff. **Q50 to Q56** (Render 5 Nov 2026, 08:04, with Build in the same instruction): the UI consistency audit of 3.62 split into seven items, highest priority first (Ivan: "break it up into segments, high priority first then set it up as a Q## with the standard naming"). They build one after another in Release order, since each touches `css/app.css` or `js/zoom.js`. Q56 also needs Parts kit 1.3.0 (an alert with more than one action), Rendered in the same instruction. **Q49** shipped in 3.62 (Render 5 Nov 2026, 03:52, given ahead with Q48 and recorded once its Recon was written; Build in the same instruction): from the random-taps and speed Recon of 3.61, draws no longer force an early layout (the top bar's width by a ResizeObserver, the floating window placed on the next frame, no scroll back at the top), dates use one formatter each (`fmtDate`), VS-101 and VS-102 have one Cancel, and an open menu closes when the screen changes width (MAINTAINING › Native bars, The floating window, Menus, Style › Dates); its scope is in this file's history and the handoff. **Q48** shipped in 3.61 (Render 5 Nov 2026, 03:52; Build in the same instruction, overnight): every button and control has a part name, most by their action in the register's new `actions` list, with the nine naming rules, `test_screens.py` › `coverage`, the Atlas tapping by name (`NAME()`, `TAP()`) and `reference/elements.md` (MAINTAINING › Screen IDs › Naming rules); its scope is in this file's history and the handoff. Atlas kit 1.2.0, then Q46, can now be built. **Q47** shipped in 3.60 (Render 5 Nov 2026, 00:56; Build in the same instruction, overnight): milestone M1b of the Sheet Music Reader Blueprint, the Sheet music page (VS-108) with the dots and sheet views, the guide on the pattern player's sounds under NOW kind `melody`, the loop on the score and the speed on PAT's stops (MAINTAINING › The Sheet music page); its scope is in this file's history and the handoff. **Q46** (Render 4 Nov 2026, 21:29, with Atlas kit 1.2.0) is tooling with no app version, like Q30, Q31 and Q35, so it sits under *Any time*. Ivan held both until the app names its buttons first: the button-naming idea (Not scheduled, Priority 2) needs its own plan, Render and Build and ships first, then Atlas kit 1.2.0 (recorded in the kit's own handoff), then Q46. It touches only `tools/atlas/`, so it doesn't clash with Q43 to Q45. **Q44** and **Q45** (Render 4 Nov 2026, 18:36, with parts kit 1.2) come from the motion and performance review of 3.55. **Q45** shipped in 3.59 (Render 4 Nov 2026, 18:36; Build 4 Nov 2026, 21:35, built beside Q44 and landed after it): parts kit 1.2.0, the kit's top bar with its soft edge inside it behind the buttons (parts 2 and 51; the buttons at the app's own top area, D19), Today's date and title on the kit's large title (part 3, VS-001), and on the iPhone the search field at the bottom in the tab bar's place, riding above the keyboard (part 6, VS-017), with the zoom's own edge copy gone (MAINTAINING › Native bars, Search, Parts kit); its scope is in this file's history and the handoff. **Q44** shipped in 3.58 (Render 4 Nov 2026, 18:36; Build 4 Nov 2026, 21:35): `.wrap` is `display: flow-root` so the zoom's still copy lands where the real page is (no 6 pt drop on iPhone), VS-014's title row level with every page's, a quicker start in `zoom.js` (measurements read once before the redraw, no still for tabs and sheet buttons, the width kept, a push one frame sooner), Today's shapes resting, no corner animation behind sheets, and the exercise glow's three pulses (MAINTAINING › Motion, The hand-off rule and A quick start; `test_zoom.py` › `handoff`, `test_native.py` › `rests`); its scope is in this file's history and the handoff. **Q43** shipped in 3.57 (Render 4 Nov 2026, 18:28; Build 4 Nov 2026, 22:04): the recorded piano (`audio/piano/`, 17 MIT-licensed notes) replaces Piano-ish as the default sound, Soft tone is smoothed, and the player's new output (a fast limiter, a soft ceiling and a small room echo) gives chords room (MAINTAINING › The pattern player, Sound; `tests/test_sound.py`); its scope is in this file's history and the handoff. **Q42** shipped in 3.56 (Render 4 Nov 2026, 14:13; Build 4 Nov 2026, 19:22): the first of seven milestones in Ivan's Sheet Music Reader Blueprint (draft 11). His own Ultimate Guitar prints are read on the device, in a Worker with pdf.js 4.10.38 pinned in `js/vendor/`, into a score on each song (`MELODY`, `js/melody.js`; the reader `js/melodyread.js`), with every guard, the backups' `melodies` field and the Song page row (MAINTAINING › Sheet music); no page or playback yet (M1b, not yet Rendered); its scope is in this file's history and the handoff. **Q41** (Render 4 Nov 2026, 09:57) moves Vocal Sessions onto the parts kit and replaces **Q34**, which is now Retired. It needs parts kit 1.1 built first (a kit version, recorded in the kit's own handoff) and comes after Q38 and Q39. **Q39** shipped in 3.54 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 10:10, built beside Q38 and landed after it): the song key on the song (`ext.key`), the key sheet (VS-098), scale lanes on pitch lines, Practise in <key> (VS-097) with the pattern player opened from outside an exercise (`PAT.guest`), and musictheoryjs and tonal pinned in `js/musictheory.js` and `js/tonal.js` (MAINTAINING › Key and scale lanes); its scope is in this file's history and the handoff. **Q38** shipped in 3.53 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 10:06): your bridge with Find your bridge (VS-096), the bridge band, softer notes and cue on the exercise page, Stop one past last time, Last time and Listen while I sing (MAINTAINING › Bridge-aware patterns); its scope is in this file's history and the handoff. **Q37** shipped in 3.52 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 00:38): the shared pitch listener (`PITCH`, `js/pitch.js`, with pitchy pinned in `js/pitchy.js`) and the song ladder on Application's card (MAINTAINING › The pitch listener, Song ladder); its scope is in this file's history and the handoff. Q38 and Q39 build on its pitch listener. **Q35** shipped on 3 Nov 2026 as tooling (Build 3 Nov 2026, 17:20): Vocal Sessions' Atlas now has starting states for the coach video, recording and takes, How did it go?, the peek card, Check timing's Overlaps, Past the new end and the rescued copy, a caption for every screen, the flows F-01 and F-02, and hand-written doors (`tools/atlas/README.md` › Starting states); its scope is in this file's history and the handoff. **Q40** shipped in 3.51 (Render 3 Nov 2026, 08:08; Build 3 Nov 2026, 17:19): the named value set at the top of `css/app.css`, `MOTION.EASE`, and `tests/test_values.py` with its shrinking known list (MAINTAINING › Value set); its scope is in this file's history and the handoff. **Q31** shipped on 3 Nov 2026 as tooling (Build 3 Nov 2026, 13:36): Vocal Sessions' Atlas now runs on Atlas kit 1.1.0 (`tools/atlas/kit/`), which its Build made first; its scope is in this file's history and the handoff. **Q37–Q39** (Render 3 Nov 2026, 08:01) are app builds, in that order after Q36, each with its own Build: Q37 brings the shared pitch listener that Q38 and Q39 use. **Q36** shipped in 3.50 (Render 3 Nov 2026, 08:00; Build 3 Nov 2026, 08:15): its register is `js/register.js`, since `js/screens.js` already held the main screens' code. **Q35**'s flows, captions and doors use its IDs. The same Render added Atlas kit 1.0's addition 14 (Stable IDs), still to be built with the kit. **Q35** (Render 3 Nov 2026, 00:39) comes after Q31, which reshapes the settings file it fills in; tooling with no app version, like Q30 and Q31. The same Render widened **Atlas kit 1.0** with additions 9–13 (in that kit's handoff), which Q31's kit copy brings and Q35 uses. **Q33** shipped in 3.49 (Render 2 Nov 2026, 17:41; Build 2 Nov 2026, 21:17). **Q34** (Render 2 Nov 2026, 18:12) is on hold for the parts kit (Ivan, 2 Nov 2026, 22:11); it uses Q33's materials and springs. **Q32** shipped in 3.48 (Render 2 Nov 2026, 15:56; Build 2 Nov 2026, 19:06). Q30 shipped as tooling (Build 2 Nov 2026, 17:57; `tools/atlas/`), and **Q31** builds on it (Render 2 Nov 2026, 15:55, in the same instruction as Q30; re-scoped by a fresh Render at 19:50 to put Vocal Sessions on the universal Atlas kit, built after Prototype kit 1.1 and Atlas kit 1.0; its own Build). Atlas kit 1.0 was built on 3 Nov 2026; Q31 was widened at 11:21 with the Atlas kit 1.1 phone pass, which its Build makes first. Both are tooling with no app version, like Q24, so they can be built outside the app queue's order. Q28 shipped in 3.46 and Q29 in 3.47 (Render 2 Nov 2026, 09:29; Build 09:33, in one instruction, built one after the other). **Q07** was moved back to [Not scheduled](#not-scheduled) on 4 Nov 2026 (16:23, Ivan), Priority 2, keeping its ID. Q27 shipped in 3.45 (Build 2 Nov 2026). Q25 shipped in 3.43 and Q26 in 3.44 (Build 2 Nov 2026); Q25–Q27 got Render on 1 Nov 2026 (19:59), in one instruction, each with its own Build. Q19 shipped in 3.39, Q20 in 3.40, Q21 in 3.41 and Q22 in 3.42. Q22 got Render on 31 Oct 2026 (20:59) and was built on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction, each with its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder. **Q41** shipped in 3.55 (Render 4 Nov 2026, 09:57; Build 4 Nov 2026, 13:14): Vocal Sessions on parts kit 1.1.0, the kit running the motion, its pop-ups, controls, tab bar and rows, and every decision one line in `js/parts.settings.js` (MAINTAINING › Parts kit; what it replaced: `tools/parts-kit/REPLACED.md`); it replaced **Q34**, now Retired; its scope is in this file's history and the handoff. **Q39** shipped in 3.54 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 10:10, built beside Q38 and landed after it): the song key on the song (`ext.key`), the key sheet (VS-098), scale lanes on pitch lines, Practise in <key> (VS-097) with the pattern player opened from outside an exercise (`PAT.guest`), and musictheoryjs and tonal pinned in `js/musictheory.js` and `js/tonal.js` (MAINTAINING › Key and scale lanes); its scope is in this file's history and the handoff. **Q38** shipped in 3.53 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 10:06): your bridge with Find your bridge (VS-096), the bridge band, softer notes and cue on the exercise page, Stop one past last time, Last time and Listen while I sing (MAINTAINING › Bridge-aware patterns); its scope is in this file's history and the handoff. **Q37** shipped in 3.52 (Render 3 Nov 2026, 08:01; Build 4 Nov 2026, 00:38): the shared pitch listener (`PITCH`, `js/pitch.js`, with pitchy pinned in `js/pitchy.js`) and the song ladder on Application's card (MAINTAINING › The pitch listener, Song ladder); its scope is in this file's history and the handoff. Q38 and Q39 build on its pitch listener. **Q35** shipped on 3 Nov 2026 as tooling (Build 3 Nov 2026, 17:20): Vocal Sessions' Atlas now has starting states for the coach video, recording and takes, How did it go?, the peek card, Check timing's Overlaps, Past the new end and the rescued copy, a caption for every screen, the flows F-01 and F-02, and hand-written doors (`tools/atlas/README.md` › Starting states); its scope is in this file's history and the handoff. **Q40** shipped in 3.51 (Render 3 Nov 2026, 08:08; Build 3 Nov 2026, 17:19): the named value set at the top of `css/app.css`, `MOTION.EASE`, and `tests/test_values.py` with its shrinking known list (MAINTAINING › Value set); its scope is in this file's history and the handoff. **Q31** shipped on 3 Nov 2026 as tooling (Build 3 Nov 2026, 13:36): Vocal Sessions' Atlas now runs on Atlas kit 1.1.0 (`tools/atlas/kit/`), which its Build made first; its scope is in this file's history and the handoff. **Q37–Q39** (Render 3 Nov 2026, 08:01) are app builds, in that order after Q36, each with its own Build: Q37 brings the shared pitch listener that Q38 and Q39 use. **Q36** shipped in 3.50 (Render 3 Nov 2026, 08:00; Build 3 Nov 2026, 08:15): its register is `js/register.js`, since `js/screens.js` already held the main screens' code. **Q35**'s flows, captions and doors use its IDs. The same Render added Atlas kit 1.0's addition 14 (Stable IDs), still to be built with the kit. **Q35** (Render 3 Nov 2026, 00:39) comes after Q31, which reshapes the settings file it fills in; tooling with no app version, like Q30 and Q31. The same Render widened **Atlas kit 1.0** with additions 9–13 (in that kit's handoff), which Q31's kit copy brings and Q35 uses. **Q33** shipped in 3.49 (Render 2 Nov 2026, 17:41; Build 2 Nov 2026, 21:17). **Q34** (Render 2 Nov 2026, 18:12) is on hold for the parts kit (Ivan, 2 Nov 2026, 22:11); it uses Q33's materials and springs. **Q32** shipped in 3.48 (Render 2 Nov 2026, 15:56; Build 2 Nov 2026, 19:06). Q30 shipped as tooling (Build 2 Nov 2026, 17:57; `tools/atlas/`), and **Q31** builds on it (Render 2 Nov 2026, 15:55, in the same instruction as Q30; re-scoped by a fresh Render at 19:50 to put Vocal Sessions on the universal Atlas kit, built after Prototype kit 1.1 and Atlas kit 1.0; its own Build). Atlas kit 1.0 was built on 3 Nov 2026; Q31 was widened at 11:21 with the Atlas kit 1.1 phone pass, which its Build makes first. Both are tooling with no app version, like Q24, so they can be built outside the app queue's order. Q28 shipped in 3.46 and Q29 in 3.47 (Render 2 Nov 2026, 09:29; Build 09:33, in one instruction, built one after the other). **Q07** was moved back to [Not scheduled](#not-scheduled) on 4 Nov 2026 (16:23, Ivan), Priority 2, keeping its ID. Q27 shipped in 3.45 (Build 2 Nov 2026). Q25 shipped in 3.43 and Q26 in 3.44 (Build 2 Nov 2026); Q25–Q27 got Render on 1 Nov 2026 (19:59), in one instruction, each with its own Build. Q19 shipped in 3.39, Q20 in 3.40, Q21 in 3.41 and Q22 in 3.42. Q22 got Render on 31 Oct 2026 (20:59) and was built on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction, each with its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q57 · Songs: Sheet Music Formats

**Status:** Approved — awaiting Build. **Render:** 5 Nov 2026, 10:45 (Ivan: "Render"), for the Sheet Music Formats Blueprint (draft 1), every *Default if unanswered* taken (decisions 1 to 8). Earlier (09:30): "It's important that this is supported", and "Skip the testing and assume that since it's a pdf it will match the same as the safari pdf". **Build:** awaiting Ivan's instruction. The build handoff is in Ivan's project notes as `q57_songs_sheet_music_formats_handoff.md` (plan `sheet_music_formats_blueprint.md`; Recon `sheet_music_ug_pdf_download_recon_2026-11-05.md`; test reader `sheet_music_vector_reader_test.py`).

- **Goal:** the app reads UG's own PDF download (vector: music symbols in a SMuFL font, tab numbers and lyrics as text, from the UG app) as well as the Safari print. It's built as a list of readers so more sources can be added later.
- **Scope, one app version:**
  1. **Readers in a list:** `FORMATS` in `js/melodyread.js`, each with `detect()` and `read()` returning the same raw read. `ug-print` is today's picture reader, unchanged. `score-pdf` is new. The score keeps `fmt`, and `READER` goes to 2.
  2. **Which reader:** from the first two pages. More than 20 SMuFL symbols (Leland, Bravura, Petaluma, Sebastian or Finale Maestro) with drawn staves → `score-pdf`; line pictures → `ug-print`. Neither → "This doesn't look like sheet music the app can read yet. Use the PDF from UG's Download PDF, or print it from UG."
  3. **The symbol reader** on the pinned pdf.js (`getTextContent`, font names from `commonObjs`, `getOperatorList` paths):
     - Staves, barlines, key, time and time changes.
     - Pitch from the staff step with accidentals and their carry.
     - Length from the heads, beams, flags, dots, tuplets and grace notes.
     - Rests, multi-bar rests checked against the printed bar numbers, ties.
     - Tab as an optional cross-check.
     - Syllables into `syl`.
     - Repeats, endings and D.S./Coda flagged.
     - Tempo from "♩ = N".
  4. **Fills in the song:** title and artist from page 1. The tempo is offered from the print. The key goes through the key sheet as today.
  5. **The sheet view (Q47) for these files:** each line drawn from the PDF with `page.render()` on the page, clipped to the line, at screen width × pixel ratio. Drawn again each time it opens; nothing stored.
  6. **Guards:**
     - No UG footer: accepted when a reader recognises the file. "Same print on another song" uses the UG id, or else title and artist plus the file's SHA-256.
     - Tab missing: allowed for `score-pdf`.
     - Guitar part: also more than 40% of heads in chords.
     - More than one part: guess the staff with lyrics and flag it in "to check".
     - Tempo changes: first tempo for playback, every change saved with its bar, "Tempo changes in this print" in "to check".
     - Everything else as Q42.
- **Out of scope:**
  - Showing words on the page (M2).
  - Photos, text recognition, and other publishers' picture PDFs.
  - MusicXML (a later entry in `FORMATS`).
  - Tempo maps in playback (M5, M6).
  - Any change to the picture reader's results.
  - Other SMuFL PDFs (MuseScore's own, for example) are accepted if they read, but not promised.
- **Needs:** Q42 and Q47 (shipped in 3.56 and 3.60). First in Release order.
- **Done when:**
  - Ivan's Die With A Smile download reads on his iPhone with 101 of 101 bars adding up and its words saved.
  - The same song's Safari print reads exactly as before.
  - Made-up vector fixtures (Leland, OFL, made by a committed generator) read as intended: sixteenths, beams of two and three, triplets, a grace note, flats and naturals, 2/4, a time change, a tempo change, a repeat and an ending, two parts, no tab, and a guitar part.
  - Every changed guard has its test, and the blip test passes.
  - The sheet view draws these lines at 375 px and on iPad, light and dark, with the playhead placed right.
  - Existing scores and backups open unchanged.
  - `MAINTAINING.md` › Sheet music lists the readers and how to add one.
- **Build order:** the readers list and detection, then the symbol reader against a fixture, then the guards and filling in, then the sheet view, then fixtures and docs. Quick tests after each, the full suite once before pushing, one receipt.

## Q51 · Songs: Kit Search Bar

**Status:** Approved — awaiting Build. **Render:** 5 Nov 2026, 08:04 (Ivan: "Do a blue print break it up into segments, high priority first then set it up as a Q## with the standard naming, I also give you render permissions. Once that's done I also give Build permission"), for the scope below, every *Default if unanswered* taken. **Build:** given in the same instruction, to start once this Render is recorded. Plan: "UI consistency fixes" Blueprint and the item's handoff in Ivan's project notes; findings: the UI consistency audit of 3.62.

- **Goal:** Songs' own search uses the kit's search field (part 6), as Search does, so there's one search bar.
- **Scope:**
  1. Tapping VS-008's search field opens the kit's field in the dock on the pill spring, filtering the Songs list as typed; ✕ restores the list. The in-list field stays as the door.
  2. The kit lifts it above the keyboard (`--pk-kb`); the list gets Search's bottom room.
  3. Retired: `#sgbar`, the old `.tabbar` rules and their known strays, `--kb`, `body.sgsearch`; listed in `tools/parts-kit/REPLACED.md`.
  4. iPad and Mac keep the in-list field.
- **Out of scope:** global Search; the sort menu; the list layout.
- **Needs:** Q50 (shipped in 3.63).
- **Done when:** the dock field opens, filters and closes as above; no `#sgbar`, `.tabbar` or `--kb` left; the value test's known list is shorter; iPad unchanged.

## Q52 · Interface: Kit Motion Match

**Status:** Approved — awaiting Build. **Render:** 5 Nov 2026, 08:04 (Ivan: "Do a blue print break it up into segments, high priority first then set it up as a Q## with the standard naming, I also give you render permissions. Once that's done I also give Build permission"), for the scope below, every *Default if unanswered* taken. **Build:** given in the same instruction, to start once this Render is recorded. Plan: "UI consistency fixes" Blueprint and the item's handoff in Ivan's project notes; findings: the UI consistency audit of 3.62.

- **Goal:** The page behind sheets, the push and Reduce Motion move the kit's way (D20, D21, D22).
- **Scope:**
  1. **D21:** `.wrap` shrinks on the kit's sheet spring and comes back on the sheet's leave timing.
  2. **D22:** `PUSH_UNDER` 0.33, `PUSH_DIM` 0.1 (kit part 10).
  3. **D20:** the Reduce Motion rule and the zoom's Reduce Motion fades use the kit's `--dur-reduced` (100 ms). The two session flashes are cues and keep one shared length, `MOTION.CUE.flash` 650 ms (default).
  4. No new differences from the kit.
- **Out of scope:** the kit's timings; sheets themselves; swipe back thresholds.
- **Needs:** Q51.
- **Done when:** push frames show 33% and 10%; a Reduce Motion sheet fade is 100 ms; the page behind a sheet has no overshoot; Q44's hand-off checks pass.

## Q53 · Interface: Kit Buttons

**Status:** Approved — awaiting Build. **Render:** 5 Nov 2026, 08:04 (Ivan: "Do a blue print break it up into segments, high priority first then set it up as a Q## with the standard naming, I also give you render permissions. Once that's done I also give Build permission"), for the scope below, every *Default if unanswered* taken. **Build:** given in the same instruction, to start once this Render is recorded. Plan: "UI consistency fixes" Blueprint and the item's handoff in Ivan's project notes; findings: the UI consistency audit of 3.62.

- **Goal:** Every button presses through the kit (parts 12, 14, 15, 18, 24) and the app's own `PRESS` retires.
- **Scope:**
  1. Glass buttons take `.pk-press` (part 12); bar buttons `.pk-press-bar` (15); solid buttons `.pk-press-solid` (14), so their 0.5 s ease-pop releases and `:active` scales go.
  2. Rows lose the leftover transform transition (D06).
  3. Toggling chips move to the kit's chips (18); the Your voice and Pattern player steppers to the kit's stepper (24). A chip that only acts takes `.pk-press-solid` (default).
  4. `PRESS`, `.pressing` and the registered `--lift` retire; rows go into `tools/parts-kit/REPLACED.md`.
- **Out of scope:** looks at rest; the tab bar and search circle; D13 finger glint.
- **Needs:** Q52.
- **Done when:** no `PRESS` left; glass grows 17 pt via the kit, bar buttons light up, solid buttons shrink to 0.93 and release on the release spring (sampled); screenshots at rest unchanged.

## Q54 · Interface: Value Tidy and Guard

**Status:** Approved — awaiting Build. **Render:** 5 Nov 2026, 08:04 (Ivan: "Do a blue print break it up into segments, high priority first then set it up as a Q## with the standard naming, I also give you render permissions. Once that's done I also give Build permission"), for the scope below, every *Default if unanswered* taken. **Build:** given in the same instruction, to start once this Render is recorded. Plan: "UI consistency fixes" Blueprint and the item's handoff in Ivan's project notes; findings: the UI consistency audit of 3.62.

- **Goal:** The hand-written values left after Q51 to Q53 take named values, and the value test guards the code too.
- **Scope:**
  1. Every "Name" row of the audit's Custom animations table takes its named value or spring; the rung nudge one length; the launch timings named in `MOTION`.
  2. The eight near-copy curves become `--ease-knob` (small elements) or `gentle` (across the page) (default).
  3. `test_values.py` checks times and keyword easings in `js/`, with a known list that only shrinks.
  4. Keyframes `pop`, `up`, `pmIn` go; the Changelog's "now" dot pulses three times and rests.
  5. Corners within 2 px of a name take it; shadows take the kit's three where they match; raw `#fff` / `#000` become tokens; anything left is listed with a reason.
- **Out of scope:** timing changes you'd notice beyond the near-copies; the kit; new named values.
- **Needs:** Q53.
- **Done when:** the known lists are shorter by every row above; the code guard passes and fails on a new raw time; main screens at rest match within a pixel.

## Q55 · Interface: Element Sheet Values

**Status:** Approved — awaiting Build. **Render:** 5 Nov 2026, 08:04 (Ivan: "Do a blue print break it up into segments, high priority first then set it up as a Q## with the standard naming, I also give you render permissions. Once that's done I also give Build permission"), for the scope below, every *Default if unanswered* taken. **Build:** given in the same instruction, to start once this Render is recorded. Plan: "UI consistency fixes" Blueprint and the item's handoff in Ivan's project notes; findings: the UI consistency audit of 3.62.

- **Goal:** The element sheet shows each named part's kit part and the values it uses.
- **Scope:**
  1. New columns in `reference/elements.md`: Kit part, Press, Corner, Motion, Reason.
  2. Built by `tools/reference/elements.py` from the app (headless, sample data), mapped back to names; unreachable parts keep a dash and are listed.
  3. `test_screens.py` › `reference` fails when a part has neither a kit part nor a reason, or the sheet is out of date.
- **Out of scope:** the saved-data and wording sheets; the visual gallery page.
- **Needs:** Q54.
- **Done when:** every row has a kit part or a reason; the test passes and fails on a missing row; the README drops "Values come later".

## Q56 · Settings: Reset All Alert

**Status:** Approved — awaiting Build. **Render:** 5 Nov 2026, 08:04 (Ivan: "Do a blue print break it up into segments, high priority first then set it up as a Q## with the standard naming, I also give you render permissions. Once that's done I also give Build permission"), for the scope below, every *Default if unanswered* taken. **Build:** given in the same instruction, to start once this Render is recorded. Plan: "UI consistency fixes" Blueprint and the item's handoff in Ivan's project notes; findings: the UI consistency audit of 3.62.

- **Goal:** Reset all data confirms with an alert, like every other delete (D08, D23).
- **Scope:**
  1. VS-082 becomes the kit's alert with Back up first, Delete everything (red) and Cancel; each does what its button does now.
  2. VS-082's kind becomes Alert; part names stay.
  3. The app moves to Parts kit 1.3.0 (unmodified copy, checksums).
- **Out of scope:** Reset this month; backups themselves.
- **Needs:** Parts kit 1.3.0 (`imperialfox/parts-kit`, its handoff in Ivan's project notes), Q55.
- **Done when:** the three-button alert opens and each button works; the kit copy is 1.3.0 and its checksums pass.

## Q46 · Atlas: Screen States

**Status:** Approved — awaiting Build, held. **Render:** 4 Nov 2026, 21:29 ("render for now but delay until app plans to name the buttons first"), for piece B of the "Atlas screen states and fast pictures" Blueprint, every *Default if unanswered* taken, with Atlas kit 1.2.0 (piece A) in the same instruction. Ivan held both until the app names its buttons. **Build:** awaiting Ivan's instruction, after the button-naming idea ships. The build handoff is in Ivan's project notes as `q46_atlas_screen_states_handoff.md`; the plan is `atlas_screen_states_blueprint.md`.

- **Goal:** every Live screen has a state (its sample data and the real taps that reach it), so "rescan the Atlas" takes every picture quickly, through real buttons.
- **Scope, tooling, no app version:**
  1. **The kit copy** moves to Atlas kit 1.2.0, unmodified, checksums updated.
  2. **`tools/atlas/states.py`,** read by `screens.py`: one state per Live screen, by screen ID. The current starting screens and the Q35 starting states move into it; the tabs stay where they are.
  3. **First draft from the scan:** a full scan's `suggested_states.py`, then each state checked by opening it against the last full scan's picture.
  4. **Variants kept:** first launch, session running, dark Today, section selected and every Q35 state, each a named variant of its screen.
  5. **Taps by part name** (`VS-001 › start-session-button`). Q48 names the parts first; any part still unnamed keeps its selector and is listed in `tools/atlas/README.md` › Unnamed parts.
  6. **Written reasons** for screens that can't be held with sample data (likely VS-094 · the launch screen), one plain line each.
  7. **Coverage test** in `tools/atlas/test_atlas.py`, with no browser: every Live register screen has a state or a reason.
  8. **Rescan rules** (`tools/atlas/README.md`, MAINTAINING › Visual App Atlas): "rescan the Atlas" runs the pictures-only scan; "full rescan" runs everything; an app build that changes screens runs the pictures pass for the IDs on its changelog Screens line and fixes any state it broke in the same push.
  9. The Q30 rule stays: screens are reached through real buttons; shortcuts are for set-up only.
- **Out of scope:** any app file (`js/`, `css/`, `index.html`); naming parts (the button-naming idea); per-screen button tests that rerun only what changed, the real iPhone pass and a screen list in Settings (layers 3 to 5 of the capture Recon); any kit change beyond moving to 1.2.0.
- **Needs:** Q48 · Interface: Name Every Button (shipped in 3.61); then Atlas kit 1.2.0 (`imperialfox/atlas-kit`, its handoff `atlas_kit_1_2_handoff.md` in Ivan's project notes).
- **Done when:** every Live screen is captured through its state or shows its written reason; the found-in-code-only count drops to those with a reason; a pictures-only scan of every state takes under 3 minutes in Claude's workspace (timed in the Debrief, with the full scan's time beside it); unchanged screens look the same as in the full scan; the coverage test passes, and fails when a state is taken out.
- **Build order:** the kit copy, then the draft states, then checking each one, then the coverage test and docs. Atlas tests while building, one pictures-only and one full scan before pushing; no app suite (no app file changes). One receipt.

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
- **Song note map (3 Nov 2026).** Map a song's notes, roughly, from its uploaded track, and show them as a faint melody line on Lines and the Track player (VS-010), opened from the Song page (VS-009). Ivan's choice of how it reads the song: if a vocals-only stem is attached to the song (for example exported from Resolve Studio's Music Remixer), run Q37's `PITCH` listener (pitchy) on it; otherwise separate the lead vocal on the phone (onnxruntime-web, MIT, WebGPU with a WebAssembly fallback; first choice the UVR MDX-Net karaoke model, 52.8 MB, MIT with credit to UVR) and run pitchy on that. pitchy alone on a full mix jumps between the singer and the instruments. Melodia in Essentia.js was dropped on 3 Nov 2026: it is AGPL v3 for non-commercial use only, which clashes with the app's MIT licence. If separating isn't possible or is too slow, the note map still runs on the full song, clearly labelled as rough, with a nudge that attaching vocals makes it cleaner (Ivan, 3 Nov 2026). The demucs-rs demo was slow and unreliable on his iPhone and MacBook; next step: he times the karaoke model on his iPhone with the test page "Vocal Sessions · Vocal isolation test". Research: project note `claude/vocal_isolation_recon_2026-11-03.md`. The note map is small and kept as its own file on the song, in backups, while the track and any separated vocal stay out of them. It could feed Q39 (the key from the song itself, not only from takes), the Q37 ladder's target notes and the note buttons. Q42's score store is built to hold it too (a sheet's score wins over one read from the track). Lines and dots only: a reference, never a score. Needs Q37.
  *Why:* it helps you learn your songs and teaches pitch by showing where the melody goes.
- **Reference sheets: elements, saved data and wording (4 Nov 2026; Ivan: high priority).** Three sheets in one `reference/` folder with one index page. Elements: every element with its screen (VS ID), kit part or the app's own, the spring, duration, corner and press it uses, its decision ID and a status (In use · Phasing out · Retired, nothing deleted). Saved data: every key the app stores, whether it's in backups, and the version that added it. Wording: every label, toast, alert and empty-state line, read from the code. Built by a script at each build, plus a visual page, with tests that fail when an element or key has no row or a retired value comes back. Q41 shipped in 3.55 and left it `tools/parts-kit/REPLACED.md` for the Retired rows. Plan notes: `element_sheet_idea_2026-11-04.md` in Ivan's project notes.
  *Why:* it's behind the scenes, but every later change starts from one place that says what exists and what replaced what, so features that make practice easier are quicker and safer to build (Ivan: "it will make things easier next time").

- **Bug: the floating window missing after random taps (found while building Q44, 4 Nov 2026; on 3.57 as well).** GitHub's run of 3.57 (the Q43 receipt push) failed `test_fuzz` seed 14 with "session running but no floating window" and "a closed sound's window came back without a play", and Q44's local full run failed seed 11 the first way (its trace ends: Recall, Song Clock's pencil, then the window's toggle, `fwToggle`). Seed 11 fails on plain 3.57 here too. Not from Q44, which doesn't touch the window. Look at what the window does when the pattern player's new sound (Q43) closes and a session is running. Seen again on 3.61 (5 Nov 2026, Q49's random-taps Recon): a replay of seed 26 ended this way once and not the next time, so it's timing; Q49's time-boxed replay didn't catch it again. *Why:* the floating window is how you get back to a running session or sound.

### Priority 2 · Helps

- **Today widgets (2 Nov 2026).** Patterns and Song practice as widget cards on Today, with an "Edit Today" step to choose which show. Reuses the shared pattern player from Q32 · Exercises: Redesign. Also, 5 Nov 2026: GitHub's run of 3.63 failed seed 11 with "nothing tappable on screen" after Check timing's pick sheet and a turn to 852 × 393; it fails on plain 3.62 too (MAINTAINING › Known test issues).
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
- **Inspector mode (4 Nov 2026).** A switch next to Q36's Show screen IDs (Settings › Appearance) that labels every element on screen with its name (`VS-001 › start-session-button`), on top of the screen ID label. Labels drawn on their own top layer so glass parts don't clip them, redrawn on scroll, screen change and sheet open; to settle at Blueprint: every label at once, or outlines with tap to reveal a name. Ivan chose to wait until after Q41 (shipped 3.55) and the Reference sheets idea above, so it can name every element, not only the main parts, and to build it into the parts kit so every app gets it. Effort guess: Light. Plan notes: `inspector_mode_idea_2026-11-04.md` in Ivan's project notes.
  *Why:* behind the scenes; pointing at any part by name makes changes that make practice easier quicker to ask for and check.
- **Q07 · Song Clock: Dynamic Sync (queued 16 Oct 2026; rescoped 31 Oct; moved here 4 Nov 2026, 16:23, Ivan).** Recall and recording follow the song's track. With the track playing, hidden words reveal just after their moment passes, at the current Recall level; starting play-along no longer switches Recall to Practise; recording a section keeps play-along going (with Q16's headphones default); a take recorded over the track saves its place in the song, plus speed and loop, and its lyrics move along on playback. Ivan's accepted defaults (31 Oct 2026): session takes over the track remember their place too, slowed or looping takes keep speed and loop, no punch-in during paced Recall. It keeps the ID Q07, so it needs a fresh **Render** (not a new number) to go back in the queue. Before then: check it against the Sheet Music Reader milestones, since Q42 onward lays the sheet over the track and may change how lyrics follow the song; and wireframe the timed Recall controls. Plan notes: `q07_song_clock_dynamic_sync_blueprint.md` in Ivan's project notes.
  *Why:* it helps you learn your songs' words in time and ties takes to the lyrics, but practice works without it (Ivan has called it old and low priority).
- **Parts kit: stable part names (5 Nov 2026).** The parts kit writes its own `data-name` from the wording (`Action: Delete`, `Menu row: Rename`, `Cancel`, `Close button`) and tells action sheet and menu buttons apart by position. Next kit version: lower-case standard names (`cancel-button`, `close-button`, `grabber`, `undo-button`), and a `name` on each action and menu row. Q48 names them in the app's register for now. A parts kit version, with its own Render and Build.
  *Why:* behind the scenes; every app on the kit gets steady names without listing them itself.
- **Atlas kit: doors by name (5 Nov 2026).** The Atlas kit's button finder records a door by its action even when the button has a name. Next kit version: prefer `data-name` when there is one, so found doors read `VS-009 › song-row`. An Atlas kit version, with its own Render and Build.
  *Why:* behind the scenes; the map and suggested states speak the same names as Ivan's notes.

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
