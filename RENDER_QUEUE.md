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
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q32**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
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
| Q30 | Atlas: Lightbox Core | Approved — awaiting Build | Visual App Atlas stage 1, Lightbox, 2 Nov 2026 |
| Q31 | Atlas: Map and Notes | Approved — awaiting Build | Visual App Atlas stage 2, map, notes, export, changes since last scan, 2 Nov 2026 |

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

**Q30**, then **Q31** (Render 2 Nov 2026, 15:55, in one instruction, each with its own Build; Q31 builds on Q30). Both are tooling with no app version, like Q24, so they can be built outside the app queue's order. Q28 shipped in 3.46 and Q29 in 3.47 (Render 2 Nov 2026, 09:29; Build 09:33, in one instruction, built one after the other). **Q07** is still awaiting Render. Q27 shipped in 3.45 (Build 2 Nov 2026). Q25 shipped in 3.43 and Q26 in 3.44 (Build 2 Nov 2026); Q25–Q27 got Render on 1 Nov 2026 (19:59), in one instruction, each with its own Build. Q19 shipped in 3.39, Q20 in 3.40, Q21 in 3.41 and Q22 in 3.42. Q22 got Render on 31 Oct 2026 (20:59) and was built on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction, each with its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q07 · Song Clock: Dynamic Sync

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

- **Scope:** paced Recall, and recording against the clock.
- **Decided:** marks over Recall's pills stay still while words reveal (a test, not new behaviour).
- **Next action:** confirm dates and scope with Ivan.
- **Done when:** *Unresolved.*

## Q30 · Atlas: Lightbox Core

**Status:** Approved — awaiting Build. **Render:** 2 Nov 2026, 15:55. Ivan: "render stage one and two. add a Q## with standard naming but seperate them". This is stage one; stage two is Q31. **Build:** awaiting Ivan's instruction.

A developer tool that shows every screen and sheet of Vocal Sessions as real screenshots side by side, from a scan of the app with sample data. Tooling only: the app itself doesn't change and there's no app version (like Q24).

- **Scope:**
  - A new `tools/atlas/` folder: the scanner and one self-contained viewer page, built from Ivan's working prototype (2 Nov 2026; design notes and prototype source are in his project notes).
  - **Scanner:** runs the app headless with the tests' sample data plus one song (lyrics, sections, marks, takes, a generated track), reusing `tests/harness.py`. Its screen list comes from the code (every `U.tab`, `U.view`, `U.sheet` and Settings page), with a set-up recipe for each tab, screen and sub-page and for as many sheets as can be opened safely. Captures each at iPhone 17 Pro size, light (top of screen and full length), plus the prototype's extra states (first launch, session running, Today in dark mode), with the clock frozen and motion off. Taps every button on each screen and records where it lands. Lists screens the code can show but the scan didn't open as "Not captured yet".
  - **Viewer:** the Lightbox grid grouped by area, kind or status; card size; search (screens and button labels); filters; "show screens found only in code"; a details panel (big picture, full length, status, "Explained in" links to `README.md` / `MAINTAINING.md` sections, last changelog mention, errors, Leads to / Comes from with how sure each link is); previous/next; keyboard (/, arrows, Enter, Esc, F); phone layout. Says "saved screenshots, not live" wherever it matters.
  - **How it's opened:** from a Claude chat ("rescan the Atlas": Claude runs the scan and updates Ivan's private Atlas page) and on the Mac with one command (`python3 tools/atlas/atlas.py`).
  - **History:** each scan's results are kept so the next one can be compared (the comparison view itself is Q31).
  - Tests for the scanner and viewer.
- **Agreed (rules from the prototype):**
  - Open a screen through its real button whenever that button does set-up (the calendar's month arrows looked broken when it was opened by a shortcut). A shortcut must never produce a "broken" result.
  - Put the app back exactly as it was before every tap (fresh UI state, saved data and any session restored), or one tap leaks into the next.
  - A sheet that didn't open is "Failed", never captured as the screen underneath.
  - Buttons that need a mic, a file or a download, delete something, or only appear after a swipe are "Not tested", with the reason, never "Broken". Buttons covered by another layer get a forced tap, marked as such.
  - Link statuses: Seen working · Changes this screen · Not tested (with reason) · Broken (tapping threw an error).
  - Same screen in another state (first launch, session running, dark) shares one entry for links; other exercises and guide pages point to the captured one as "same page layout".
  - Look: the dark "pro tool" look as prototyped.
- **Out of scope:** the map, notes, export and changes since the last scan (Q31); compare views, other screen sizes and a dark-mode pass of every screen (not queued); any change to the app.
- **The repo is public:** screenshots and scan output never go into git (`tools/atlas/data/` is git-ignored); scans use sample data only.
- **Needs:** nothing in particular; can be built any time.
- **Done when:**
  - The scan finds every screen named in `render()` and `renderSheet()`; a test adds a dummy screen and sees it appear, then removes it and sees it reported gone.
  - A failed capture shows as failed, never as a blank card; no "broken" result comes from how the scan opened a screen.
  - "Explained in" links land on the right sections.
  - Nothing under `tools/atlas/data/` is tracked by git; the app's own full test suite still passes.
  - The viewer works at Mac and iPhone sizes, and the Mac command is documented in `MAINTAINING.md`.

## Q31 · Atlas: Map and Notes

**Status:** Approved — awaiting Build. **Render:** 2 Nov 2026, 15:55. Ivan: "render stage one and two. add a Q## with standard naming but seperate them". This is stage two; stage one is Q30. **Build:** awaiting Ivan's instruction.

Adds the map, notes Claude can read, export, and what changed since the last scan to the Atlas. Tooling only, no app version.

- **Scope:**
  - **Map:** screens in area regions, lines for links the scan saw working (button, opens a sheet, back, tab bar; each can be shown or hidden), plus "found in code only" lines. Click a line for what's tapped and its code action. Drag cards, add labels, Tidy layout, pan, zoom, Fit all. The layout is saved and never redrawn while a label is being typed.
  - **Notes:** "Add note" (or N) on a screen. **Tap a part** (with Bigger part / Smaller) or draw a **Box**, write the note and pick an optional kind. Each note is saved with its screen, scan, marked area, the element's tag, classes, text and path, and its key styles. Never records what's typed in a field. A notes list with statuses: Open, Looking into it, Fixed, Dismissed.
  - **Where notes live:** the private Atlas page's own store (only Ivan can write), so Claude reads them directly. Saying "check my Atlas notes" in a Claude chat is the main handoff. A rescan never touches notes or layout.
  - **Export for Claude:** Copy report (Markdown with all the details above), Download .zip (report, notes.json and a cropped picture of each marked area), Copy as queue ideas (a message for Claude to add them to Not scheduled below, text only, each with a priority checked against the app's purpose), and an option to mark them "Looking into it".
  - **Changes since the last scan:** new, gone, looks different (how much and where), links changed, failed this time; before and now side by side with a wipe slider; the `CHANGELOG.md` versions and queue IDs released in between, never claiming which one caused a change. A "show only changes" filter.
  - Tests.
- **Agreed:** notes have one home (the private Atlas page), so there are never two copies; only notes sent as queue ideas reach the repo, and as text only.
- **Out of scope:** compare views across screens or sizes (not queued); any change to the app.
- **The repo is public:** notes, pictures and screenshots never go into git.
- **Needs:** Q30 built first.
- **Done when:**
  - Notes and layout survive a rescan and a reload, on phone and Mac, and Claude can list the notes from a chat.
  - The report has the screen, marked area, element details and note; the .zip has a picture per note; queue ideas come out text-only in this file's format.
  - A rescan after an app change shows the right new, gone and changed screens, and names the versions released in between.
  - The app's own full test suite still passes.

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
- **Note lengths and attacks in the pattern player (2 Nov 2026).** Notes that can be sustained or short and detached, and different note lengths (rhythms), shown with music notes on the pattern drawing. Builds on the shared pattern player from Exercises: Redesign.
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
