# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.40** (1 Nov 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28; Q11 · Data: Save Safety in 3.29; Q12 · Song Clock: Timing Integrity in 3.30; Q13 · Interface: Keyboard Guards in 3.31; Q04 · Marks: Practice Guide in 3.32; Q23 · Interface: Status Bar Glow in 3.33; Q14 · Playback: Smooth Frames in 3.34; Q18 · Tests: GitHub Match in 3.35; Q15 · Marks: Register-Ready Data in 3.36; Q16 · Audio: Voice Analysis Foundations in 3.37; Q17 · Hygiene: Dead Code Sweep in 3.38; Q19 · Session: One-Page Flow in 3.39; Q20 · Session: Application Redesign in 3.40.

- **Every item has two separate gates.** `Awaiting Render` means it is not approved. Ivan's **Render** approves only the named item's exact scope and moves it to `Approved — awaiting Build`; it does not start work or authorize a push. A separate **Build** instruction starts implementation for that approved item. Do not treat approval of one item as approval of the whole queue.
- **The code wins on what's built.** This is a summary, not a spec. Check each note against the code before relying on it.
- **Detailed design notes live in Ivan's private project notes, not in this repo.** Where an item names one, ask Ivan to paste or attach it. Anything not settled here is marked *Unresolved*.
- **Ivan can reorder the queue.** Versions follow build order: each build takes the next minor version when it's built.
- **When an item ships,** remove its section from this file in the same push and set its row in the table below to `Shipped <version>`. Its `CHANGELOG.md` headline (the `*…*` line under the version) ends with its queue ID, e.g. `*Waveform sections on the track player (Q02)*`. The `##` line itself stays `## 3.23 · 27 Oct 2026`, which the app's Changelog page reads.

## Naming

Every queued item has a queue ID and a standard name, used in the queue, in handoffs, in commit messages and in file names. Use these, not the older working names.

- **Items:** `Q[##] · [Subsystem]: [Feature Name]`, e.g. `Q02 · Track: Waveform Sections`.
- **Files** (handoffs, specs, wireframes, prototypes): `q##_[subsystem]_[feature]_[type].[ext]`, lower case with underscores, e.g. `q02_track_waveform_sections_handoff.md`.
- **Releases:** the shipped version's `CHANGELOG.md` headline ends with the queue ID in brackets, e.g. `*Waveform sections on the track player (Q02)*` under `## 3.23 · 27 Oct 2026` (the `##` line keeps its exact format for the app's Changelog page). That's the bridge from queue ID to version. Q01 shipped as 3.22, headline `*Search, from every tab (Q01)*`; Q08 as 3.23.
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q25**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
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
| Q21 | Session: Saved Screen | Approved — awaiting Build | "Session saved" splash, 2+5, 31 Oct 2026 |
| Q22 | Session: Clock Redesign | Approved — awaiting Build | Session clock ring prototype, 31 Oct 2026 |
| Q23 | Interface: Status Bar Glow | Shipped 3.33 | Gradient clipped at the top, 31 Oct 2026 |
| Q24 | Coach: Video Redesign | Approved — awaiting Build | Coach video redesign, 31 Oct–1 Nov 2026 |

Work shipped before this standard (for example Track 1 and Song Clock A1) keeps its version numbers and has no queue ID.

Every item also follows [MAINTAINING.md](MAINTAINING.md): its [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [changelog](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style). On top of that:

- **Check the previous build is live first.** Use the item's **Needs** line. If it records that its required version was verified on `main`, that satisfies this check; otherwise look for the version in `CHANGELOG.md` on `main`. If it isn't there, stop and tell Ivan.
- **Never push with failing tests.** If something can't be finished, commit nothing, leave the item here and report plainly.
- **Everything that moves uses the shared springs.** Every new sound starts through `NOW.start()`.
- **The repo is public.**
  - Never commit real music, recordings, the coach video, course media, lyrics or backups.
  - Never commit with Ivan's personal email. Claude commits as `Claude <noreply@anthropic.com>`.

---

## Order (1 Nov 2026)

Most critical first: **Q21 → Q22 → Q07** (Q19 shipped in 3.39, Q20 in 3.40). Q22 got Render on 31 Oct 2026 (20:59) and goes after Q21, because it builds on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction; each still needs its own Build. They follow Q17 (shipped in 3.38; Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42) and have all shipped. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q21 · Session: Saved Screen

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 31 Oct 2026 (19:58), with Q19 and Q20. The build handoff is in Ivan's project notes as `q21_session_saved_screen_handoff.md`.
**Needs:** Q19 live (shipped in 3.39).

- **Goal:** finishing lands on a calm "Session saved" screen that belongs to Today, then becomes Today with one tap.
- **Scope:** "Session saved"; the week arc with only today's minutes animating in; "N min · Day · weekly goal reached"; the week row with today's dot turning green; "N-week streak continues"; Done centred just below. Done turns the screen into Today: the arc, week row and streak move into place and Done becomes Start session. No count-ups or confetti.
- **Defaults if unanswered:** real minutes, goal and streak; replaces today's shrink-into-Start-session finish; lines without a goal or streak are left out.
- **Out of scope:** Today's own layout; Progress.
- **Next action:** after Ivan separately says Build for Q21, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** the screen shows the right numbers, Done morphs into Today (and fades with Reduce Motion), and the full suite passes.

## Q22 · Session: Clock Redesign

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 31 Oct 2026 (20:59) for the scope below. The build handoff is in Ivan's project notes as `q22_session_clock_redesign_handoff.md`, with a link to the prototype.
**Needs:** Q19 and Q21 live (Q19 shipped in 3.39).

- **Goal:** the session clock becomes a ring you can read at a glance, in the same family as the one-page session, with small fixes that take the stress out of timing.
- **Scope:** one ring in three slices sized by usual step lengths, with a tick at the end of the current slice; finished steps fill their slice, going over changes nothing; paused ring breathes, numbers grey, Resume; finish closes the ring into the saved line; opens by zooming out of the timer pill and closes by swiping sideways anywhere (✕ kept); the floating window uses the same small ring. Plus: screen stays on, "Were you away?" check, Undo on Log, fix a step time (hold and slide), survives closing the app, tap the big number to swap total and step, steady digits, pause from the floating window.
- **Defaults if unanswered:** steps not reached show the usual time ("~14 min"); usual lengths come from recent sessions, with set fallbacks until there are enough; Song practice keeps one full-ring slice; the "away" check appears after 10 min away.
- **Out of scope:** tapping a slice to jump to a step (dropped by Ivan); any auto-pause, buzz or Lock Screen timer; Progress's time split.
- **Next action:** after Ivan separately says Build for Q22, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** the ring, pause, finish, swipe to close and each of the eight features work, light and dark, with and without Reduce Motion, and the full suite passes.

## Q24 · Coach: Video Redesign

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 1 Nov 2026 (13:15) for the scope below. The build handoff is in Ivan's project notes as `q24_coach_video_redesign_handoff.md`, with the plan, the approved wording and the audio timeline beside it.
**Outside the order:** Q24 changes no app code, so it can be built alongside the app items, before or after any of them, whenever Ivan says Build.
**Needs:** nothing from the app. Ivan's Mac linked and awake for copying sections and the DaVinci Resolve stage.

- **Goal:** the coach video looks like part of the redesigned session and reads at a glance: exercise, level, progress, place in the whole video, and Your turn / With coach / Listen.
- **Scope:** a scripted render of new graphics for all 12 exercises (36 levels), built in 12 checked sections (Humming first), then finished in DaVinci Resolve on Ivan's Mac with the original audio untouched, markers and chapters. A render kit in `tools/coach-video/` (slide, tokens, content data, renderer, check script).
- **Defaults if unanswered:** one key = one round; "from" is the note the round starts on; Vocal slides counts his slides; no app version or changelog entry (the app doesn't change).
- **Out of scope:** any app code change (`COACH_TIMES`, a dark copy, links to the Foundation rings); changing the audio or timing; exercises 13–15.
- **Never commit:** the coach video, its audio, rendered sections or fonts (the repo is public). The kit only.
- **Next action:** after Ivan separately says Build for Q24, work from its handoff in a fresh chat.
- **Done when:** all 12 sections are rendered and checked; every level change lands within one frame of the original's; the audio and length are identical; the chapters are in the file; Ivan has watched it in the floating window, the player and full screen.

## Q07 · Song Clock: Dynamic Sync

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

- **Scope:** paced Recall, and recording against the clock.
- **Decided:** marks over Recall's pills stay still while words reveal (a test, not new behaviour).
- **Next action:** confirm dates and scope with Ivan.
- **Done when:** *Unresolved.*

---

## Not scheduled

Kept so they aren't lost. None are queued; ask Ivan before planning any of them.

- **Motion leftovers (was 4d).** Optional; Ivan decides whether they're worth a build:
  - Holding a section in Annotate lifts it while the others ripple aside.
  - Perform's larger text scales up smoothly.
  - The recording bar rises, and Stop turns it into the takes sheet.
  - A session's progress dashes fill, and its step pill moves onto the shared springs.
  - All sessions' old list fades out before the new rows ripple in.
- **Exercise patterns the app plays (31 Oct 2026).** The app generates notes itself (no recordings): exercise patterns in any key, a starting note, stepping up a semitone each round, glides for slides and sirens, and an optional held note underneath. A switchable reference sound (Soft tone · Piano-ish · Electric piano), Piano-ish by default, set in Settings and also cycled from a small chip beside "Hear it" on the exercise page; piano sounds are held longer on glides. Ivan heard a demo and judged a recorded piano unnecessary. Build after Q16 (sound plumbing); check the silent switch and speaker loudness on his iPhone.
- **Exercise page redesign (31 Oct 2026).** Polished mockup for Humming: tile beside the title; a pitch-shape drawing with "Hear it" (dot steps along with a ripple); three at-a-glance facts; the fix tip under the drawing; "How to do it" steps; "Where you feel it" outline with a glow; level dots with the last logged level selected; shorter "Why it helps" with More; quieter small headings for minor sections. Needs per-exercise content drafted from the write-ups and course notes.
- **Pinned ideas:**
  - Timeline drag and drop.
  - A shared song-screen dock.
  - Learning tap lateness.
  - Reusing Chorus 1's timing for Chorus 2.
  - A wide Timeline on iPad.
  - Delivery marks for one repeat only.
  - A demo recording on each mark's guide page.
  - Mark selections across a line break.
  - "Shift all timings" when a re-imported track is a different length.
