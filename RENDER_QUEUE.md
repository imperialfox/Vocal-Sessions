# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.37** (1 Nov 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28; Q11 · Data: Save Safety in 3.29; Q12 · Song Clock: Timing Integrity in 3.30; Q13 · Interface: Keyboard Guards in 3.31; Q04 · Marks: Practice Guide in 3.32; Q23 · Interface: Status Bar Glow in 3.33; Q14 · Playback: Smooth Frames in 3.34; Q18 · Tests: GitHub Match in 3.35; Q15 · Marks: Register-Ready Data in 3.36; Q16 · Audio: Voice Analysis Foundations in 3.37.

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
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q24**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
- **Exception, 30 Oct 2026:** Ivan asked for the six stages of the 30 Oct read-only audit, plus its clean-up list, to get IDs straight away, before Render, most critical first. They are **Q11–Q17**. All seven got Render on 30 Oct 2026; Q11–Q16 have shipped (3.29–3.31, 3.34, 3.36 and 3.37), and Q17 is `Approved — awaiting Build`.
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
| Q17 | Hygiene: Dead Code Sweep | Approved — awaiting Build | Audit clean-up list |
| Q18 | Tests: GitHub Match | Shipped 3.35 | Workflow review, 31 Oct 2026 |
| Q19 | Session: One-Page Flow | Approved — awaiting Build | One-page session prototype, 31 Oct 2026 |
| Q20 | Session: Application Redesign | Approved — awaiting Build | One-page session prototype, 31 Oct 2026 |
| Q21 | Session: Saved Screen | Approved — awaiting Build | "Session saved" splash, 2+5, 31 Oct 2026 |
| Q22 | Session: Clock Redesign | Approved — awaiting Build | Session clock ring prototype, 31 Oct 2026 |
| Q23 | Interface: Status Bar Glow | Shipped 3.33 | Gradient clipped at the top, 31 Oct 2026 |

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

Most critical first: **Q17 → Q19 → Q20 → Q21 → Q22 → Q07**. Q22 got Render on 31 Oct 2026 (20:59) and goes after Q21, because it builds on the one-page session and the saved screen. Q19–Q21 got Render on 31 Oct 2026 (19:58), in one instruction; each still needs its own Build. They go after Q17 (Q20 needs Q16's track-while-recording, shipped in 3.37). Q11–Q17 got Render on 30 Oct 2026 (06:42); each still needs its own Build. What has shipped is in the table's Status column. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q17 · Hygiene: Dead Code Sweep

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q17_hygiene_dead_code_sweep_handoff.md`.
**Needs:** Q14 live (it touches the same files).

- **Goal:** remove what nothing uses.
- **Scope:**
  - **Remove:** `mkWords`, `timing.real`, the `CK.trk` checks, the unreachable no-track dock branch, the empty `ckLine()`, and stale "Sync" / tap captions and comments.
  - **Remove ten unused CSS selectors:** `.newtag`, `.rright`, `.playbig`, `.sgtag`, `.prog`, `.sgtake`, `.foot.sgfresh`, `.tkw`, `.sgvk`, `.ckcen`.
  - **Fix:** each song gets its own timing Undo; recheck the loading track after a peaks re-read in `open1()`.
  - **Note:** data step 4 does nothing (`cleanSection` migrates first). Keep the step; don't delete it. (Q15 added this note in the code and MAINTAINING.md in 3.36.)
- **Out of scope:** behaviour changes beyond the two small fixes.
- **Next action:** after Ivan separately says Build for Q17, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** nothing visible changes; the full suite passes.

## Q19 · Session: One-Page Flow

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 31 Oct 2026 (19:58) for the scope below, in one instruction covering Q19–Q21. Each is its own build and needs its own **Build**. The build handoff is in Ivan's project notes as `q19_session_one_page_flow_handoff.md`, with a link to the prototype.
**Needs:** Q17 live (queue order).

- **Goal:** a focused session runs on one page; Foundation, Rotation and Application follow each other in place.
- **Scope:**
  - **One page:** the screen stays put; a finished section folds to a summary line and the next slides in; a faded preview of what's next. One pinned button keeps today's labels and still records each step's end. Progress's time split is untouched.
  - **Pulling past an unfinished section springs back**; finished sections can be reopened; no jumping ahead.
  - **Floating window:** the coach video in Foundation and Rotation, a "Coach ▸" pill in Application; draggable, snaps to corners.
  - **Foundation levels:** tap a row's ring to cycle 1 → 2 → 3 → Skip. Level 3 sweeps the card blue then green and opens a comment box; levels 1–2 open "What kept it at level N?" reasons plus "+ Your own"; after a reason the card folds and the next exercise is nudged.
  - **Rotation:** the suggested card on top, then "More exercises" sortable by Longest ago, Most recent or A–Z; Skip rotation; "Just Foundation today? Finish here".
  - **Wording:** "Foundation", never "SOVT".
- **Defaults if unanswered:** reasons saved like exercise notes are now; the old multi-page session is replaced with no switch back (old sessions and drafts still open); Application keeps today's content until Q20.
- **Out of scope:** Q20 and Q21's parts; merging Song practice into Songs; Progress's time split.
- **Next action:** after Ivan separately says Build for Q19, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** a whole session runs on one page with each step's end logged as now; a 3.31 draft resumes; the full suite passes.

## Q20 · Session: Application Redesign

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 31 Oct 2026 (19:58), with Q19 and Q21. The build handoff is in Ivan's project notes as `q20_session_application_redesign_handoff.md`.
**Needs:** Q19 and Q16 live.

- **Goal:** the Application step is quick and satisfying: pick up where you left off, sing, compare, keep the best take.
- **Scope:** a Carry on card (last song and section; the track starts there); songs with no sections fall back to Whole song; a remembered Sing over the track switch (headphones by default, as agreed in Q16) with a headphones hint; the red track window while recording; takes with waveforms, Star, one-tap Compare from the second take, ↻ Again and Done; "Practised, not recorded"; Other songs with a sort heading; the "How did it go?" sheet removed from finishing.
- **Defaults if unanswered:** ↻ Again included; past "How did it go?" answers stay, and the chips stay on the session edit sheet; shared take-row changes reach Song practice too.
- **Out of scope:** the Session saved screen; merging Song practice into Songs; voice analysis.
- **Next action:** after Ivan separately says Build for Q20, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** recording with and without the track, Star, Compare, Again, Done and "Practised, not recorded" work; finishing doesn't ask how it went; the full suite passes.

## Q21 · Session: Saved Screen

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 31 Oct 2026 (19:58), with Q19 and Q20. The build handoff is in Ivan's project notes as `q21_session_saved_screen_handoff.md`.
**Needs:** Q19 live.

- **Goal:** finishing lands on a calm "Session saved" screen that belongs to Today, then becomes Today with one tap.
- **Scope:** "Session saved"; the week arc with only today's minutes animating in; "N min · Day · weekly goal reached"; the week row with today's dot turning green; "N-week streak continues"; Done centred just below. Done turns the screen into Today: the arc, week row and streak move into place and Done becomes Start session. No count-ups or confetti.
- **Defaults if unanswered:** real minutes, goal and streak; replaces today's shrink-into-Start-session finish; lines without a goal or streak are left out.
- **Out of scope:** Today's own layout; Progress.
- **Next action:** after Ivan separately says Build for Q21, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** the screen shows the right numbers, Done morphs into Today (and fades with Reduce Motion), and the full suite passes.

## Q22 · Session: Clock Redesign

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 31 Oct 2026 (20:59) for the scope below. The build handoff is in Ivan's project notes as `q22_session_clock_redesign_handoff.md`, with a link to the prototype.
**Needs:** Q19 and Q21 live.

- **Goal:** the session clock becomes a ring you can read at a glance, in the same family as the one-page session, with small fixes that take the stress out of timing.
- **Scope:** one ring in three slices sized by usual step lengths, with a tick at the end of the current slice; finished steps fill their slice, going over changes nothing; paused ring breathes, numbers grey, Resume; finish closes the ring into the saved line; opens by zooming out of the timer pill and closes by swiping sideways anywhere (✕ kept); the floating window uses the same small ring. Plus: screen stays on, "Were you away?" check, Undo on Log, fix a step time (hold and slide), survives closing the app, tap the big number to swap total and step, steady digits, pause from the floating window.
- **Defaults if unanswered:** steps not reached show the usual time ("~14 min"); usual lengths come from recent sessions, with set fallbacks until there are enough; Song practice keeps one full-ring slice; the "away" check appears after 10 min away.
- **Out of scope:** tapping a slice to jump to a step (dropped by Ivan); any auto-pause, buzz or Lock Screen timer; Progress's time split.
- **Next action:** after Ivan separately says Build for Q22, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** the ring, pause, finish, swipe to close and each of the eight features work, light and dark, with and without Reduce Motion, and the full suite passes.

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
