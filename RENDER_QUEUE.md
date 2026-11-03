# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.50** (3 Nov 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28; Q11 · Data: Save Safety in 3.29; Q12 · Song Clock: Timing Integrity in 3.30; Q13 · Interface: Keyboard Guards in 3.31; Q04 · Marks: Practice Guide in 3.32; Q23 · Interface: Status Bar Glow in 3.33; Q14 · Playback: Smooth Frames in 3.34; Q18 · Tests: GitHub Match in 3.35; Q15 · Marks: Register-Ready Data in 3.36; Q16 · Audio: Voice Analysis Foundations in 3.37; Q17 · Hygiene: Dead Code Sweep in 3.38; Q19 · Session: One-Page Flow in 3.39; Q20 · Session: Application Redesign in 3.40; Q21 · Session: Saved Screen in 3.41; Q22 · Session: Clock Redesign in 3.42; Q25 · Coach: Frame-Accurate Chapters in 3.43; Q26 · Window: Picture in Picture in 3.44; Q27 · Interface: Landscape Tab Bar Fit in 3.45; Q28 · Hygiene: Toggl Removal in 3.46; Q29 · Session: Song Rating Removal in 3.47; Q24 · Coach: Video Redesign (tooling, no app version: the render kit is in `tools/coach-video/`); Q30 · Atlas: Lightbox Core (tooling, no app version: the Atlas is in `tools/atlas/`); Q32 · Exercises: Redesign in 3.48; Q33 · Interface: Glass Native Tuning in 3.49; Q36 · Interface: Screen IDs in 3.50.

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
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q41**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
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
| Q34 | Interface: Native Menus and Controls | Blocked (on hold for the parts kit, 2 Nov 2026) | Component inventory (round 2), worth doing plus smaller wins, 2 Nov 2026 |
| Q35 | Atlas: Starting States | Approved — awaiting Build | Atlas: more starting states (Not scheduled idea), from the screen-flow canvas update, 3 Nov 2026 |
| Q36 | Interface: Screen IDs | Shipped 3.50 | Screen IDs blueprint (permanent IDs for every screen, part names, flows, saved-data list), 3 Nov 2026 |
| Q37 | Session: Song Ladder | Approved — awaiting Build | Song ladder, pitch test page, "Prototype · Song ladder and bridge-aware patterns" (v1–v3), 2 Nov 2026 |
| Q38 | Exercises: Bridge-Aware Patterns | Approved — awaiting Build | Bridge-aware patterns, Find your bridge, same prototype, 2 Nov 2026 |
| Q39 | Songs: Key and Scale Lanes | Approved — awaiting Build | Key detection, scale lanes, suggested patterns, same prototype (v2), 2 Nov 2026 |
| Q40 | Interface: Value Set and Test | Approved — awaiting Build | The value test (consistency audit of 3.49, 2 Nov 2026; called Q35 in early notes before Q35 went to Atlas: Starting States) |

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

1. Q40 — touches the whole stylesheet, so first
2. Q37 — brings the pitch listener
3. Q38 — needs Q37
4. Q39 — needs Q37

### Any time

- Q35 — tooling, no app version (its Needs, Q31 and Q36, have shipped)

## Order (3 Nov 2026)

**Q31** shipped on 3 Nov 2026 as tooling (Build 3 Nov 2026, 13:36): Vocal Sessions' Atlas now runs on Atlas kit 1.1.0 (`tools/atlas/kit/`), which its Build made first; its scope is in this file's history and the handoff. **Q37–Q39** (Render 3 Nov 2026, 08:01) are app builds, in that order after Q36, each with its own Build: Q37 brings the shared pitch listener that Q38 and Q39 use. **Q36** shipped in 3.50 (Render 3 Nov 2026, 08:00; Build 3 Nov 2026, 08:15): its register is `js/register.js`, since `js/screens.js` already held the main screens' code. **Q35**'s flows, captions and doors use its IDs. The same Render added Atlas kit 1.0's addition 14 (Stable IDs), still to be built with the kit. **Q35** (Render 3 Nov 2026, 00:39) comes after Q31, which reshapes the settings file it fills in; tooling with no app version, like Q30 and Q31. The same Render widened **Atlas kit 1.0** with additions 9–13 (in that kit's handoff), which Q31's kit copy brings and Q35 uses. **Q33** shipped in 3.49 (Render 2 Nov 2026, 17:41; Build 2 Nov 2026, 21:17). **Q34** (Render 2 Nov 2026, 18:12) is on hold for the parts kit (Ivan, 2 Nov 2026, 22:11); it uses Q33's materials and springs. **Q32** shipped in 3.48 (Render 2 Nov 2026, 15:56; Build 2 Nov 2026, 19:06). Q30 shipped as tooling (Build 2 Nov 2026, 17:57; `tools/atlas/`), and **Q31** builds on it (Render 2 Nov 2026, 15:55, in the same instruction as Q30; re-scoped by a fresh Render at 19:50 to put Vocal Sessions on the universal Atlas kit, built after Prototype kit 1.1 and Atlas kit 1.0; its own Build). Atlas kit 1.0 was built on 3 Nov 2026; Q31 was widened at 11:21 with the Atlas kit 1.1 phone pass, which its Build makes first. Both are tooling with no app version, like Q24, so they can be built outside the app queue's order. Q28 shipped in 3.46 and Q29 in 3.47 (Render 2 Nov 2026, 09:29; Build 09:33, in one instruction, built one after the other). **Q07** is still awaiting Render. Q27 shipped in 3.45 (Build 2 Nov 2026). Q25 shipped in 3.43 and Q26 in 3.44 (Build 2 Nov 2026); Q25–Q27 got Render on 1 Nov 2026 (19:59), in one instruction, each with its own Build. Q19 shipped in 3.39, Q20 in 3.40, Q21 in 3.41 and Q22 in 3.42. Q22 got Render on 31 Oct 2026 (20:59) and was built on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction, each with its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q07 · Song Clock: Dynamic Sync

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

- **Scope:** paced Recall, and recording against the clock.
- **Decided:** marks over Recall's pills stay still while words reveal (a test, not new behaviour).
- **Next action:** confirm dates and scope with Ivan.
- **Done when:** *Unresolved.*

## Q35 · Atlas: Starting States

**Status:** Approved — awaiting Build. **Render:** 3 Nov 2026, 00:39. Ivan: "Render all mentioned", for this item (agreed at 00:29 as its own small item: "1. okay") together with Atlas kit 1.0's additions 9–13. **Build:** awaiting Ivan's instruction. The build handoff is in Ivan's project notes as `q35_atlas_starting_states_handoff.md`.

Vocal Sessions' Atlas settings only (`tools/atlas/`, outside the kit copy). Tooling, no app version.

- **Goal:** the scan reaches the screens it now lists as found in code only, and Vocal Sessions uses kit 1.0's new features.
- **Scope:**
  - **Starting states** so the scan captures: the coach video player (the tests' synthetic coach video, `tests/fixtures/coach-chapters.webm`); recording and takes in Application (a fake microphone, as `tests/test_application.py` uses); song practice's "How did it go?" and its saved sheet (a song practice with a take); a mark's peek card (a hold); Check timing after a timed section moves (Overlaps); a shorter replacement track (Past the new end); and the rescued-data warning with Settings › Backup's rescued copy.
  - Each still opens through its real buttons from its starting state, with a full reset before every tap; a state that doesn't open is "Failed", never a capture.
- **Default if unanswered:** Q35 also fills in Vocal Sessions' settings for kit 1.0's additions: a one-line caption per screen; the focused session (Foundation to Session saved) and song practice as the first flows; hand-written doors for swipes, holds, timed sheets and file pickers.
- **Out of scope:** any app change; any change to the kit copy; screens that need a real file chosen by hand (import, export, restore) beyond listing them as hand-written doors.
- **Needs:** Q31 live (and so Atlas kit 1.0 with additions 9–14), and Q36 live (screen IDs; added at Q36's Render, 3 Nov 2026, 08:00). Its flows, captions and doors use Q36's IDs.
- **Next action:** after Ivan separately says Build for Q35, check Q31 is on `main`, then implement only this scope in a fresh chat from its handoff.
- **Done when:** each screen above is captured or honestly "Failed"; the found-in-code-only count drops by those screens; the two flows step through in the viewer; the Atlas tests pass; the app's full suite still passes.

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

## Q37 · Session: Song Ladder

**Status:** Approved — awaiting Build. **Render:** 3 Nov 2026, 08:01. Ivan: "Render", choosing "All three, as 3 items" (Q37, Q38, Q39; first numbered Q36–Q38 in this chat, renumbered because Q36 was taken a minute earlier by Interface: Screen IDs), from the prototype "Prototype · Song ladder and bridge-aware patterns" (v3). **Build:** awaiting Ivan's instruction. The build handoff is in Ivan's project notes as `q37_session_song_ladder_handoff.md`.

- **Goal:** help exercises carry over into songs. A section is sung four ways (lip trill, hum, vowels only, words), and the pitch lines show where the words drift from the trill.
- **Scope:**
  - **The shared pitch listener** (`PITCH`, its own file in `js/`, reusable by Q38 and Q39): pitchy 4.1.0 (MIT, McLeod method) as a pinned copy in the repo, with its licence. It reads a take's pitch line after recording (10 ms steps, clarity 0.90, blips under 40 ms dropped, octave slips fixed, light smoothing) and listens live through `rec.mic.analyser()` on `AUDIO.frame` (Q16's seam). It also finds sudden jumps (2 semitones or more within 200 ms, steady either side) and held notes.
  - **Application's card** gets a Straight / Ladder switch. A ladder is four rungs, each a take of the chosen place with its own instruction and lyric view: the words faded for trill and hum, vowel letters picked out for Vowels only, and the words for Words. Any rung can be skipped. Sing over the track and Q16's headphones rule work as now. While recording, the pitch line draws live.
  - **The rungs fold away:** the sung rungs fold into one row ("2 of 4 sung · Trill · Hum") that opens when tapped, the rungs still to come are one line ("Up next"), and only the current rung stays open.
  - **Lines** (from two rungs): the rungs' pitch lines overlaid, each switchable. The word or moment where the words (or vowels) part from the trill (or hum) is named, with **Hear both** (the trill, then the words, at that spot, through `NOW`). If they don't part, it says so plainly.
  - **Notes of the line** (once all four are sung): a row of note buttons from the trill's held notes. Tap to hear one. With **Repeat** on, it keeps playing until tapped again.
  - Done folds the card to one line. Ladder takes are ordinary takes of the place (Star, Compare, notes and backups as now), named by their rung.
- **Default if unanswered:**
  - The switch is on the card (not a link under Sing), remembered per song.
  - Vowels only picks out the vowel letters of the words (spelling, not sounds).
  - Note buttons are labelled by note, one per held note of the trill. Words come when timing allows, not in this item.
  - Pitch lines are worked out when needed and never saved or backed up.
  - The notes play in the pattern player's sound.
- **Out of scope:** the bridge band and every bridge feature (Q38); key, scale lanes and suggested patterns (Q39); a ladder door on the song's page; any score, percentage or right/wrong colouring.
- **Needs:** Q36 shipped (it's built after Q36, on the version Q36 ships in).
- **Done when:** a ladder can be sung, skipped, folded and finished in Application; pitch lines and the parting spot are right for synthetic test tones; Hear both and the note buttons follow one sound at a time; old data and backups load unchanged; 375 px, dark mode and Reduce Motion; the full suite passes; Ivan's iPhone checks.

## Q38 · Exercises: Bridge-Aware Patterns

**Status:** Approved — awaiting Build. **Render:** 3 Nov 2026, 08:01, in the same instruction as Q37 and Q39. **Build:** awaiting Ivan's instruction. The build handoff is in Ivan's project notes as `q38_exercises_bridge_aware_patterns_handoff.md`.

- **Goal:** help through the register break. The pattern player knows your bridge and guides you through it instead of letting you push.
- **Scope:**
  - **Your bridge**, saved with Your voice. **Find your bridge** is a sheet with one slow slide on "ee", the line drawn live with jump markers. It suggests a zone (two semitones below the jump to one above), with From and To steppers, Use this bridge and Try again. With no jump, you set it by feel. Doors: the exercise page and Settings › Your voice.
  - **The exercise page:**
    - The bridge band on the drawing, with notes in the zone ringed.
    - A line ("Bridge E4–G4 · rounds 11–14 cross it. Those notes play softer.") with Change.
    - The reference notes in the zone play softer.
    - A cue while a bridge note plays: "Thinner · quieter" on hummed exercises, a narrower vowel (ah → uh) on vowel exercises.
  - **Stop one past last time:** the route ends one round past the highest top note last sung cleanly. "Last time" moves on quietly only when a higher top is held cleanly while listening.
  - **Listen while I sing** (off by default): your voice as a dot and short trail on the drawing, with a headphones hint.
- **Default if unanswered:**
  - The reference notes in the zone play at 55% volume.
  - The cue can be switched off in Settings › Pattern player.
  - Stop one past last time is one setting, next to Stop at my top note; when both are on, the earlier stop wins.
  - "Last time" is kept per exercise.
  - Without listening, nothing changes it.
- **Out of scope:** recording on the exercise page (Exercise takes, Not scheduled); key and scale lanes (Q39); any score or right/wrong colouring.
- **Needs:** Q37 shipped (the pitch listener).
- **Done when:** the bridge can be found, changed and saved (and survives a backup); the band, ringed notes, softer notes and cue follow the zone; Stop one past last time and Last time behave as above with synthetic tones; the voice dot follows a test tone; one sound at a time; 375 px, dark mode and Reduce Motion; the full suite passes; Ivan's iPhone checks.

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

## Q40 · Interface: Value Set and Test

**Status:** Approved — awaiting Build. **Render:** 3 Nov 2026, 08:08. Ivan: "Render what's currently there", for the value test as planned after the consistency audit of 3.49, with every *Default if unanswered* taken. **Build:** awaiting Ivan's instruction. The build handoff is in Ivan's project notes as `q40_interface_value_set_and_test_handoff.md` (the audit: `consistency_audit_2026-11-02.md`; design decisions D01–D15: `parts_decisions_2026-11-02.md`).

- **Goal:** one named set of look and motion values, and a test that stops new stray values, so the app stops drifting. The audit counted 26 corner sizes, 7 press shrinks, 49 hand-written curves in the stylesheet (7 in code) and 31 durations.
- **Scope:**
  - **The named set** beside the text sizes: corners (`--r-small` 10, `--r-medium` 14, `--r-card` 20, `--r-large` 26, `--r-sheet` 34; capsules and circles as now; graphic bits of 6 px and under exempt), `--press` 0.93 for solid buttons, named easings (`--ease-pop`, `--ease-knob`, `--ease-out`, plus the spring variables) and fade timings (`--dur-quick` 120 ms, `--dur-fade` 200 ms).
  - **Exact matches renamed** to the names, with no visual change.
  - **A shrinking list:** every other value stays and is written into the test as a known stray; new strays fail, and the list may only get shorter.
  - **Two small fixes:** the pattern player's speed bar and menu (`.phbar`, `.pmenu`) onto the glass tokens; solid button presses at 0.90, 0.94, 0.95 and 0.97 snapped to 0.93.
  - **`tests/test_values.py`** (corners, presses, easings and durations in `css/app.css`; `cubic-bezier` in `js/`), and a "Value set (Q40)" part in `MAINTAINING.md`.
- **Default if unanswered:** the values above; rows and row-like cards keep their 0.98 / 0.96 shrink as known strays (decision D06 replaces them with a highlight at the parts kit move); slow ambient loops exempt; shadows reported, not enforced.
- **Out of scope:** snapping non-matching values, every decision in D01–D15, sheets (Scroll Behaviour Pass), menus and the rest of Q34 (on hold for the parts kit).
- **Build:** on its own (it touches `css/app.css` throughout), after a rebase.

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
- **Smart file drop (3 Nov 2026).** Drag a file onto the app, or bring it in from the phone, and the app works out what to do with it from the file type and the screen you're on. Ivan's example: Add song (VS-045) and New song (VS-051) should take a dropped file. First guesses, to settle at wireframe: on Add song or New song, a song file starts a new song with it as the track (named from the file) and a text file becomes the words; on the Song page (VS-009), a song file becomes the track, or the vocals-only stem for the Song note map if its name says vocals or acapella (asking when unsure); a backup file anywhere offers Import backup (never restores without asking); anywhere else, one short "Use this for…" sheet with the likeliest choice first, so it doesn't add choice fatigue. **Phone limits to check:** an iPhone Home Screen web app can't appear in the Share sheet (Safari hasn't shipped the Web Share Target API, so only Chrome on Android has it; WebKit bug 194593), so on the phone the doors are drag and drop (holding a file in Files and switching apps; test on iOS 26) and the app's own file pickers. Drag and drop works on a computer and iPad. **Next:** wireframe after the kit is done, so the wireframes and prototype can pull their parts from it (Ivan, 3 Nov 2026).
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
