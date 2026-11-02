# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.42** (1 Nov 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28; Q11 · Data: Save Safety in 3.29; Q12 · Song Clock: Timing Integrity in 3.30; Q13 · Interface: Keyboard Guards in 3.31; Q04 · Marks: Practice Guide in 3.32; Q23 · Interface: Status Bar Glow in 3.33; Q14 · Playback: Smooth Frames in 3.34; Q18 · Tests: GitHub Match in 3.35; Q15 · Marks: Register-Ready Data in 3.36; Q16 · Audio: Voice Analysis Foundations in 3.37; Q17 · Hygiene: Dead Code Sweep in 3.38; Q19 · Session: One-Page Flow in 3.39; Q20 · Session: Application Redesign in 3.40; Q21 · Session: Saved Screen in 3.41; Q22 · Session: Clock Redesign in 3.42; Q24 · Coach: Video Redesign (tooling, no app version: the render kit is in `tools/coach-video/`).

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
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q30**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
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
| Q28 | Hygiene: Toggl Removal | Approved — awaiting Build | Get rid of Copy for Toggl, 2 Nov 2026 |
| Q29 | Session: Song Rating Removal | Approved — awaiting Build | Remove "Rate the song", 2 Nov 2026 |

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

Next: **Q28**, then **Q29** (both approved — awaiting Build; Render 2 Nov 2026, 09:29). Q29 follows Q28 because both touch a session's sheet, and Q28 removes the Toggl text that also lists ratings. **Q07** is still awaiting Render. Q27 shipped in 3.45 (Build 2 Nov 2026). Q25 shipped in 3.43 and Q26 in 3.44 (Build 2 Nov 2026); Q25–Q27 got Render on 1 Nov 2026 (19:59), in one instruction, each with its own Build. Q19 shipped in 3.39, Q20 in 3.40, Q21 in 3.41 and Q22 in 3.42. Q22 got Render on 31 Oct 2026 (20:59) and was built on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction, each with its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q28 · Hygiene: Toggl Removal

**Status:** Approved — awaiting Build.
**Render:** 2 Nov 2026, 09:29. Ivan: "get rid of any \"copy for toggl\" in any part of the app: render." Scope below. Build not yet given.

- **Why:** the app no longer depends on Toggl ([README › What it's for](README.md#what-its-for)), so copying a session out for it is leftover.
- **Scope:** remove Copy for Toggl from every part of the app:
  - the Copy for Toggl buttons on a session's sheet and a song practice's sheet, and the "Toggl tag #song-practice" line;
  - the copy action, `togglLines()` and the "Copied for Toggl" toast; `copyText()` too if nothing else uses it;
  - the `TOGGL` tags in `js/content.js`, and Toggl wording in comments and file headers;
  - the Toggl checks in `test_content.py`, `test_flows.py` and `test_application.py` (keep what they check that isn't Toggl);
  - Toggl in `README.md` and `MAINTAINING.md`.
- **Kept:** each exercise's focus (it still sets the icon colour); old "How did it go?" answers still show in history.
- **Not changed:** saved data and backups (nothing about Toggl is stored); `tests/fixtures/app-3.6.html`, a frozen old version used by the restore tests.
- **Done when:** no "Toggl" is left in `js/`, `css/`, `index.html` or the docs outside `CHANGELOG.md`'s history; the full suite passes locally and on GitHub; a normal app version with a changelog headline ending "(Q28)".
- **Handoff:** `q28_hygiene_toggl_removal_handoff.md` in Ivan's project notes.

## Q29 · Session: Song Rating Removal

**Status:** Approved — awaiting Build.
**Render:** 2 Nov 2026, 09:29. Ivan: "the application rate the song can also go since I always seem to skip that at the end any ways: render - approved." Scope below. Build not yet given. Build after Q28.

- **Why:** the app isn't a grader ([README › What it's for](README.md#what-its-for)), and Ivan always skips the rating.
- **Scope:**
  - remove "Rate the song" (Pitch · Tone · Ease) from a session's Application step;
  - remove the Pitch · Tone · Ease rows from a session's edit sheet.
- **Default if unanswered:** old ratings stop showing on a session's sheet as well, so no scores show anywhere. They stay in the saved data.
- **Not changed:** saved data and backups. The `rate` field stays, per [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), and old backups still restore. Song practice's "How did it go?" words (words, not scores) and Star on takes stay.
- **Done when:** no Pitch · Tone · Ease rating can be given or seen; sessions with old ratings still open, edit and restore; the full suite passes locally and on GitHub; a normal app version with a changelog headline ending "(Q29)".
- **Handoff:** `q29_session_song_rating_removal_handoff.md` in Ivan's project notes.

## Q07 · Song Clock: Dynamic Sync

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

- **Scope:** paced Recall, and recording against the clock.
- **Decided:** marks over Recall's pills stay still while words reveal (a test, not new behaviour).
- **Next action:** confirm dates and scope with Ivan.
- **Done when:** *Unresolved.*

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
- **Exercises: Redesign (merged 2 Nov 2026 from "Exercise patterns the app plays" and "Exercise page redesign", both 31 Oct).** Each exercise page explains the exercise and plays it: piano-like notes the app makes itself (no recordings), 23 practice patterns from warm-ups to riffs and runs, the coach's starting notes, a snapping speed slider and voice range warnings. Vocal slides has no "Hear it". The pattern player is built as one shared piece so other places can reuse it. Details: `exercises_redesign_blueprint.md` in Ivan's project notes. A prototype is made; the page content draft and Render are still to do.
  *Why:* it teaches, and it gets you singing straight from the exercise.

### Priority 2 · Helps

- **Today widgets (2 Nov 2026).** Patterns and Song practice as widget cards on Today, with an "Edit Today" step to choose which show. Reuses the shared pattern player from Exercises: Redesign.
  *Why:* more doors to practice, and fewer taps to start singing.
- **Reusing Chorus 1's timing for Chorus 2.** *Why:* less setting up before you can practise a song.
- **"Shift all timings" when a re-imported track is a different length.** *Why:* saves redoing timings by hand.
- **Learning tap lateness.** *Why:* play-along lines up better with less fiddling.
- **A demo recording on each mark's guide page.** *Why:* it teaches by ear, not only in words.
- **A shared song-screen dock.** *Why:* the same controls in the same place on every song screen.

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
