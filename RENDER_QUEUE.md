# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.26** (28 Oct 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26.

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
- **New items:** an idea gets its ID when Ivan says **Render** for it, taking the next unused number (the next is **Q11**). IDs are never reused or renumbered, even when the queue is reordered or an item ships.

Older chats, notes and prototypes use working names. They map like this:

| Queue ID | Standard name | Earlier working names |
|---|---|---|
| Q01 | Search: Global Find | Render 10, Search, Global Search |
| Q02 | Track: Waveform Sections | Track 2, Sections on the waveform |
| Q03 | Marks: Layered Annotations | Marks 1, Layered marks |
| Q04 | Marks: Practice Guide | Marks 2, Marks help, Marks guide |
| Q05 | Song Clock: Tap Re-Anchor | Song Clock A2, Render 6, Line pass and retime |
| Q06 | Song Clock: Timeline View | Song Clock B, Render 7, Section starts and wheels |
| Q07 | Song Clock: Dynamic Sync | Song Clock C, Render 8, Paced Recall |
| Q08 | Interface: Native iOS Polish | Native bars, iOS 27 polish (shipped in 3.23) |
| Q09 | Track: Waveform Sections Follow-up | Giant 3-Pad dock, Q02 follow-up (shipped in 3.25) |
| Q10 | Interface: HIG Foundations Pass | Vault ideas wireframes (shipped in 3.26) |

Work shipped before this standard (for example Track 1 and Song Clock A1) keeps its version numbers and has no queue ID.

Every item also follows [MAINTAINING.md](MAINTAINING.md): its [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [changelog](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style). On top of that:

- **Check the previous build is live first.** Use the item's **Needs** line. If it records that its required version was verified on `main`, that satisfies this check; otherwise look for the version in `CHANGELOG.md` on `main`. If it isn't there, stop and tell Ivan.
- **Never push with failing tests.** If something can't be finished, commit nothing, leave the item here and report plainly.
- **Everything that moves uses the shared springs.** Every new sound starts through `NOW.start()`.
- **The repo is public.**
  - Never commit real music, recordings, the coach video, course media, lyrics or backups.
  - Never commit with Ivan's personal email. Claude commits as `Claude <noreply@anthropic.com>`.

---

## Q03 · Marks: Layered Annotations

**Status:** Approved — awaiting Build. **Approval:** Render given by Ivan on 29 Oct 2026 (22:41) for the scope below: everything under **Decided**, with the two questions settled under **Settled at Render**. Wireframes, prototype and plan were approved 22 Oct 2026. The build handoff and design spec (recovered from the 22 Oct chat and updated for 3.26) are in Ivan's project notes as `q03_marks_layered_annotations_handoff.md` and `q03_marks_layered_annotations_spec.md`.
**Needs:** 3.26 live (verified on `main` at `56da976`, 29 Oct 2026).

- **Goal:** marks that match how a song is learned, one layer at a time.
- **Decided:**
  - **Four layers:**
    - Notes, Phrasing, Words and Delivery.
    - Tone and Feel are merged into Delivery, and rhythm is folded into Notes.
    - Each layer has five marks plus a Note bookmark.
    - Options are one tap deep, and only one layer shows at a time.
  - **Editing:**
    - One edit mode with a Marks · Lyrics switch.
    - Phrases are brackets that chain.
    - Repeated choruses share their marks.
    - Marking while listening keeps the clock running.
    - Annotate's old marks move across into the layers.
  - **Display:**
    - Word labels sit above the word, in the 3.17 sing-as style (not the prototype's inline chips).
    - Marks show over Recall's pills.
    - Marks while playing gains an "Active layer" setting.
- **Settled at Render (Ivan, 29 Oct 2026):**
  - The track player's lyrics (the card above the waveform, the lines under the Song rows) stay plain: no marks there.
  - Note text isn't searchable in this item; pinned for later.
- **Not in this item:** help screens (Q04); suggested breaths and the hold menu's Annotate (Q05); Delivery marks for one repeat only, demo recordings and selections across a line break (pinned).
- **Notes from earlier builds:**
  - Add `'active'` to the Marks while playing cycle (`ckTileAct('marks')`, `CK_MPNAME`) and draw the active layer in `ckBuild()`.
  - Replace the pencil row's Edit lyrics / Marks pills with the Marks · Lyrics switch.
- **Next action:** after Ivan separately says Build, implement it from the Q03 build handoff.
- **Done when:**
  - Everything decided above works.
  - Existing marks carry across without loss.
  - Old backups still restore.
  - The full suite passes.
  - *Unresolved:* finer criteria in the build handoff.

## Q04 · Marks: Practice Guide

**Status:** Awaiting Render. **Approval:** Not yet given. Guide text and prototype approved 22 Oct 2026; a build handoff exists in Ivan's project notes.
**Needs:** Q03 live.

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

## Q05 · Song Clock: Tap Re-Anchor

**Status:** Awaiting Render. **Approval:** Not yet given. Planned, not scheduled.
**Needs:** Q03 live.

- **Goal:** time songs line by line, and fix lines in place.
- **Scope:**
  - The line pass, punch-in, flags and markers.
  - A hold menu with Retime line, Play from here and Annotate (Annotate replaces Mark to fix).
  - Suggested breaths from the line pass. They only become marks when Ivan taps them.
- **Decided:** timing says when, marks say how.
- **Open questions:**
  - **The line pass is to be re-scoped with Ivan after Q02**, because he prefers scrubbing the waveform to tapping along live.
  - *Unresolved:* whether Q05's "markers" are separate from the track player's markers (3.20).
- **Notes from earlier builds:**
  - Suggested breaths go with the timing, per line, checked in `cleanTiming()`.
  - Punch-in goes on the play-along layer, and the Flag goes beside the transport.
  - "Time each line" on Check timing only shows a toast until this build.
  - Tests use the test clock (`CLOCK.fake`, `CLOCK.advance`).
- **Next action:** after Q02, re-scope with Ivan. Don't build until then.
- **Done when:** *Unresolved* until it's re-scoped.

## Q06 · Song Clock: Timeline View

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

- **Scope:**
  - What's left of B: section starts, wheel pickers and Retime routes.
  - The Timeline itself is absorbed by Q02.
- **Open questions:** the rest of B is to be re-scoped with Ivan after Q02.
- **Notes from earlier builds:** these were left waiting for B:
  - Snapping is in the grid but does nothing yet.
  - Check timing's lines aren't tappable yet.
  - Section starts is still a plain row.
- **Next action:** re-scope with Ivan after Q02.
- **Done when:** *Unresolved.*

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
