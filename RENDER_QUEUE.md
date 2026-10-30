# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.28.1** (30 Oct 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27; Q05 · Song Clock: Tap Re-Anchor in 3.28.

- **Every item has two separate gates.** `Awaiting Render` means it is not approved. Ivan's **Render** approves only the named item's exact scope and moves it to `Approved — awaiting Build`; it does not start work or authorize a push. A separate **Build** instruction starts implementation for that approved item. Do not treat approval of one item as approval of the whole queue.
- **The code wins on what's built.** This is a summary, not a spec. Check each note against the code before relying on it.
- **Detailed design notes live in Ivan's private project notes, not in this repo.** Where an item names one, ask Ivan to paste or attach it. Anything not settled here is marked *Unresolved*.
- **Ivan can reorder the queue.** Versions follow build order: each build takes the next minor version when it's built.
- **When an item ships,** remove it from this file in the same push and say which version it shipped in. Its `CHANGELOG.md` headline (the `*…*` line under the version) ends with its queue ID, e.g. `*Waveform sections on the track player (Q02)*`. The `##` line itself stays `## 3.23 · 27 Oct 2026`, which the app's Changelog page reads.

## Naming

Every queued item has a queue ID and a standard name, used in the queue, in handoffs, in commit messages and in file names. Use these, not the older working names.

- **Items:** `Q[##] · [Subsystem]: [Feature Name]`, e.g. `Q02 · Track: Waveform Sections`.
- **Files** (handoffs, specs, wireframes, prototypes): `q##_[subsystem]_[feature]_[type].[ext]`, lower case with underscores, e.g. `q02_track_waveform_sections_handoff.md`.
- **Releases:** the shipped version's `CHANGELOG.md` headline ends with the queue ID in brackets, e.g. `*Waveform sections on the track player (Q02)*` under `## 3.23 · 27 Oct 2026` (the `##` line keeps its exact format for the app's Changelog page). That's the bridge from queue ID to version. Q01 shipped as 3.22, headline `*Search, from every tab (Q01)*`; Q08 as 3.23.
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q18**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.
- **Exception, 30 Oct 2026:** Ivan asked for the six stages of the 30 Oct read-only audit, plus its clean-up list, to get IDs straight away, before Render, most critical first. They are **Q11–Q17**, and each is still `Awaiting Render`.

Older chats, notes and prototypes use working names. They map like this:

| Queue ID | Standard name | Earlier working names |
|---|---|---|
| Q01 | Search: Global Find | Render 10, Search, Global Search |
| Q02 | Track: Waveform Sections | Track 2, Sections on the waveform |
| Q03 | Marks: Layered Annotations | Marks 1, Layered marks (shipped in 3.27) |
| Q04 | Marks: Practice Guide | Marks 2, Marks help, Marks guide |
| Q05 | Song Clock: Tap Re-Anchor | Song Clock A2, Render 6, Line pass and retime (shipped in 3.28) |
| Q06 | Song Clock: Timeline View | Song Clock B, Render 7, Section starts and wheels (retired: folded into Q05) |
| Q07 | Song Clock: Dynamic Sync | Song Clock C, Render 8, Paced Recall |
| Q08 | Interface: Native iOS Polish | Native bars, iOS 27 polish (shipped in 3.23) |
| Q09 | Track: Waveform Sections Follow-up | Giant 3-Pad dock, Q02 follow-up (shipped in 3.25) |
| Q10 | Interface: HIG Foundations Pass | Vault ideas wireframes (shipped in 3.26) |
| Q11 | Data: Save Safety | Audit stage 1, data safety |
| Q12 | Song Clock: Timing Integrity | Audit stage 2, timing integrity |
| Q13 | Interface: Keyboard Guards | Audit stage 3, input hygiene |
| Q14 | Playback: Smooth Frames | Audit stage 4, per-frame work |
| Q15 | Marks: Register-Ready Data | Audit stage 5, room for register data |
| Q16 | Audio: Voice Analysis Foundations | Audit stage 6, Web Audio seam |
| Q17 | Hygiene: Dead Code Sweep | Audit clean-up list |

Work shipped before this standard (for example Track 1 and Song Clock A1) keeps its version numbers and has no queue ID.

Every item also follows [MAINTAINING.md](MAINTAINING.md): its [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [changelog](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style). On top of that:

- **Check the previous build is live first.** Use the item's **Needs** line. If it records that its required version was verified on `main`, that satisfies this check; otherwise look for the version in `CHANGELOG.md` on `main`. If it isn't there, stop and tell Ivan.
- **Never push with failing tests.** If something can't be finished, commit nothing, leave the item here and report plainly.
- **Everything that moves uses the shared springs.** Every new sound starts through `NOW.start()`.
- **The repo is public.**
  - Never commit real music, recordings, the coach video, course media, lyrics or backups.
  - Never commit with Ivan's personal email. Claude commits as `Claude <noreply@anthropic.com>`.

---

## Order (30 Oct 2026)

Most critical first: **Q11 → Q12 → Q13 → Q04 → Q14 → Q15 → Q16 → Q17 → Q07**. Q11–Q17 got Render on 30 Oct 2026 (06:42); each still needs its own Build. The audit items come from a read-only audit of 3.28.1 on 30 Oct 2026. Detailed findings, with file and line references and how each was checked, are in the audit (`vocal_sessions_audit_2026-10-30.md` in Ivan's project notes; ask him to attach it). Ivan can reorder.

## Q11 · Data: Save Safety

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q11_data_save_safety_handoff.md`.
**Needs:** 3.28.1 live (verified on `main`, 30 Oct 2026). Nothing else.

- **Goal:** no path in the app can silently lose saved data, a take, or a session in progress.
- **Scope:**
  - **Damaged saved data:** if `vocalTracker` can't be read, copy the raw text somewhere safe *before* anything saves over it, and tell Ivan. Check each song on its own, so one bad song is dropped rather than everything. Today `load()` returns `{}` and `boot.js` saves it straight away; reproduced in the audit with a cut-off save.
  - **One shared IndexedDB helper** for recordings, the coach video, tracks and take extras, handling complete, error, abort and blocked, and reconnecting after a dropped connection. The recordings helper has no `onabort` today.
  - **A take that fails to save** keeps its audio in memory with Retry, and is never dropped without a message.
  - **`saveDraft()`** warns when it fails, as `save()` does.
  - **The 30-day pre-upgrade copy** moves from localStorage into IndexedDB, so it no longer halves the space for saved data.
  - **Startup** is guarded, so the launch screen always goes away and an error is shown.
- **Out of scope:** any change to what's saved or to the backup format.
- **Detail for the builder to confirm with Ivan at Build (within this scope):** where the rescued raw copy lives and how he's told. Proposed: kept in IndexedDB, with a one-time message pointing to Settings › Backup.
- **Next action:** after Ivan separately says Build for Q11, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** a cut-off `vocalTracker` keeps its raw copy and the app says so; a simulated aborted save shows a message and keeps the take; a failed draft save warns; the old-backup fixtures still restore; the full suite passes.

## Q12 · Song Clock: Timing Integrity

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q12_song_clock_timing_integrity_handoff.md`.
**Needs:** Q11 live.

- **Goal:** timing Ivan placed by hand is never moved or overwritten by something he didn't do to it, and guesses are never saved as if placed.
- **Scope:**
  - **Moving a section** in a timed song no longer squashes other sections' lines. Reproduced: after moving Chorus 2 above Verse 2 and re-timing one line, Verse 2 became 75.1–75.4 s.
  - **`ckOrder`** never rewrites placed lines, only estimated ones. Overlaps between placed lines get flagged on Check timing instead.
  - **Punch-in, line-lane edits and promote** read placed times only, never estimates, so an estimate can't become a hard limit or be saved as placed.
  - **Promoting a marker** lands the section start on the marker; earlier sections are squeezed, or marked as estimates if there's no room.
  - **Replacing a track** with a shorter one: Undo, and the same check for timing past the new end as for markers, with Keep / Trim instead of deleting.
  - **A section start** stops counting as set once its first line loses its time.
- **Out of scope:** new timing features; the screen layout.
- **Decided by Ivan (30 Oct 2026):** moving a timed section turns that section's line times into estimates (dashed, shown on Check timing), with its section start kept. Other sections' times don't change. (He chose this over stopping with an explanation, or keeping the times with Undo.)
- **Next action:** after Ivan separately says Build for Q12, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** moving a timed section and then editing one line changes no other section; adding a line between two touching lines moves no placed line; promoting into a late section lands on the marker; replacing a track offers Undo; the full suite passes.

## Q13 · Interface: Keyboard Guards

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q13_interface_keyboard_guards_handoff.md`.
**Needs:** nothing (independent).

- **Goal:** keyboard shortcuts on iPad and Mac never fire twice, while typing, or during a recording.
- **Scope:**
  - **One shared typing check** and one place where keys are handled. Holding a key doesn't repeat play/pause. A key another control already handled is left alone. No shortcuts while a picker, sheet or recording is open.
  - **The Song length picker's** arrow keys no longer also open the next song (and "Set" no longer applies the length to the song you started on).
  - **Cmd+1–4** follows the same rules as the tab bar: no tab switch during a recording or session, or while typing.
  - **Shortcuts use Cmd only** on Apple devices, leaving Ctrl's text-editing keys alone.
  - **Enter to confirm** ignores keys pressed while composing text in another script (for example Japanese).
- **Out of scope:** new shortcuts.
- **Next action:** after Ivan separately says Build for Q13, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** each case above has a test; the full suite passes.

## Q14 · Playback: Smooth Frames

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q14_playback_smooth_frames_handoff.md`.
**Needs:** Q12 live (the timing model settles there).

- **Goal:** play-along and the track page do the least work possible on each frame, so lyrics and the waveform stay smooth on older iPhones.
- **Scope:**
  - **Song Clock:** keep the timing model between frames; look up lines once per redraw; read the screen before writing to it; blur only lines on screen.
  - **Track page:** draw the waveform layer only when zoom, loop or markers change, and draw just the playhead each frame; cache the font; only update labels when they change. In rows view, redraw only the row the playhead is in.
  - **A punch-in** updates the lines it changed instead of rebuilding the whole view.
- **Out of scope:** any visual change. Everything must look the same.
- **Next action:** after Ivan separately says Build for Q14, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** existing visual and timing tests pass unchanged; a test counts per-frame work (no timing model rebuilt, no layout reads after writes); the full suite passes.

## Q15 · Marks: Register-Ready Data

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q15_marks_register_ready_data_handoff.md`.
**Needs:** Q12 live. Must come before any register feature.

- **Goal:** new fields on marks and timing (for example register details, transition anchors, somatic notes) survive editing, backups, and a restore into the previous version.
- **Scope:**
  - **Build on the Marks Register layer**, which already exists (Chest, Mix, Head, Falsetto, Flip here). No second register system on track markers.
  - **A mark with an unknown type or option** is kept but inactive, not deleted. Moving or re-adding a mark keeps its extra fields.
  - **Timing keeps fields it doesn't know** at the timing, slot and line level. Today `cleanTiming` and `ckStore` rebuild timing from a fixed list on every edit.
  - **One documented place for optional extras** on each record.
  - **A test** restores a backup made by the *next* version into this one, with nothing lost.
- **Out of scope:** any new register screens or marks. This item only prepares the data.
- **Next action:** after Ivan separately says Build for Q15, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** the next-version backup test passes; the old-backup fixtures still restore; the full suite passes.

## Q16 · Audio: Voice Analysis Foundations

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q16_audio_voice_analysis_foundations_handoff.md`.
**Needs:** Q14 and Q15 live.

- **Goal:** a clean place for future pitch and vocal-weight analysis to plug in, without risking one sound at a time, the lock screen, or the pitch-kept slow-down.
- **Scope:**
  - **One shared audio service** (a single AudioContext) used by the mono mix and the level meter, and later by the analysers. It listens to the microphone only; the track stays on its own player.
  - **One frame clock** for any visualiser, with no page look-ups per frame.
  - **The coach video's level loop** uses the track's precise timer, so the end of a level isn't clipped (today it cuts up to about ¼ s).
  - **Ivan checks the track loop's join on his iPhone** at 1× and 0.5×. If there's an audible gap, try a short fade at the join.
- **Out of scope:** the pitch / vocal-weight analysis and visualiser themselves (a later item).
- **Decided by Ivan (30 Oct 2026):** the backing track may keep playing while the microphone is listened to or recorded. Today, starting a recording stops every sound; this changes that, and only for the backing track. Everything else still follows one sound at a time.
- **Risk to settle in the handoff:** voice processing is off for takes, so through the speaker the track will leak into the microphone (and into the take and any analysis). Headphones avoid it; the handoff should say what happens without them.
- **Next action:** after Ivan separately says Build for Q16, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** the meter and mono mix share one audio service; the coach loop wraps within a few ms in tests; the full suite passes; Ivan's phone check is recorded.

## Q17 · Hygiene: Dead Code Sweep

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 30 Oct 2026 (06:42) for the scope below, in one instruction covering Q11–Q17. Each item is still its own build, in queue order, and needs its own **Build**. The build handoff is in Ivan's project notes as `q17_hygiene_dead_code_sweep_handoff.md`.
**Needs:** Q14 live (it touches the same files).

- **Goal:** remove what nothing uses.
- **Scope:**
  - **Remove:** `mkWords`, `timing.real`, the `CK.trk` checks, the unreachable no-track dock branch, the empty `ckLine()`, and stale "Sync" / tap captions and comments.
  - **Remove ten unused CSS selectors:** `.newtag`, `.rright`, `.playbig`, `.sgtag`, `.prog`, `.sgtake`, `.foot.sgfresh`, `.tkw`, `.sgvk`, `.ckcen`.
  - **Fix:** each song gets its own timing Undo; recheck the loading track after a peaks re-read in `open1()`.
  - **Note:** data step 4 does nothing (`cleanSection` migrates first). Keep the step; don't delete it.
- **Out of scope:** behaviour changes beyond the two small fixes.
- **Next action:** after Ivan separately says Build for Q17, check its **Needs** are live, then implement only this scope in a fresh chat from its handoff.
- **Done when:** nothing visible changes; the full suite passes.

## Q04 · Marks: Practice Guide

**Status:** Awaiting Render. **Approval:** Not yet given. Guide text and prototype approved 22 Oct 2026; a build handoff exists in Ivan's project notes.
**Needs:** Q03 live (shipped in 3.27). Notes for it are in MAINTAINING.md › Marks ("For Q04"). The handoff from 22 Oct predates 3.27, so check it against the code.

- **Goal:** explain each mark where it's used.
- **Decided:**
  - A peek card when holding a mark button.
  - A Song key listing this song's marks.
  - A Marks guide with a page per mark: What it is, How to sing it, When to mark it, Example, and Don't confuse with.
  - A How to mark a song walkthrough.
  - All of these are reachable from several places in the app.
- **Assumptions:** the guide's wording is original writing and safe to commit.
- **Next action:** after Ivan gives Render approval for this item and separately says Build, implement it in a fresh chat from the Q04 build handoff (written earlier as the Marks 2 handoff) and guide wording, which Ivan pastes in.
- **Done when:**
  - Every door opens the right help.
  - Every mark has its page.
  - The full suite passes.
  - *Unresolved:* finer criteria.

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
