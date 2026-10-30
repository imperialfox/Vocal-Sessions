# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.27** (29 Oct 2026). **Shipped:** Q01 · Search: Global Find in 3.22; Q08 · Interface: Native iOS Polish in 3.23; Q02 · Track: Waveform Sections in 3.24; Q09 · Track: Waveform Sections Follow-up in 3.25; Q10 · Interface: HIG Foundations Pass in 3.26; Q03 · Marks: Layered Annotations in 3.27.

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
| Q03 | Marks: Layered Annotations | Marks 1, Layered marks (shipped in 3.27) |
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

## Q05 · Song Clock: Tap Re-Anchor

**Status:** Building (Build given by Ivan on 30 Oct 2026, 00:33). **Approval:** Render given by Ivan on 29 Oct 2026 (22:58) for the re-scoped item below (re-scoped and wireframed the same day; it absorbs Q06's leftovers, and Q06 is retired). The build handoff is in Ivan's project notes as `q05_song_clock_tap_reanchor_handoff.md`.
**Needs:** Q03 live (shipped in 3.27; where its parts plug in: MAINTAINING.md › Marks, "For Q05").

- **Goal:** time songs line by line from the song's own track, and fix lines in place. No more side-by-side listening (music on another device while tapping in the app).
- **Going:**
  - Song Clock timing needs the song's track on this device (`TRACK.has(sg.id)`). Without one, Timing reads "Add a track to time this song" and opens the track picker.
  - Sync by sections (the 3.18 tap pad) and play-along without a track are retired. Section starts come from the waveform (3.24's Make this a section start…).
  - Timing already saved on older songs is kept untouched in data and backups.
  - The live line pass isn't built. Check timing's "Time each line" toast goes.
  - No separate orange flags: the Flag uses the track's markers (3.20).
  - Q06 · Song Clock: Timeline View is retired; its leftovers are in this item.
- **Coming:**
  - Line blocks on the waveform in the track player's Phrase and Line views: one per lyric line, estimated ones dashed. Drag an edge (one handle where two lines touch), or select a block and use Start here / End here. Snapping (about 10 px) to the playhead, section starts and neighbouring edges, using the existing Snapping setting. Undo on every change. Writes into Song Clock's timing.
  - Punch-in in play-along: hold the lyrics 0.5 s as a line starts; release sets its end. Toast with Undo. A quick tap still jumps.
  - Flag beside the play-along transport adds a track marker; paused, the same slot is Retime (the player in Line view on the current line).
  - Hold menu on a lyric line in Practise or Perform: Retime line, Play from here, Annotate (Q03's Marks side, whole line selected). Not in Recall.
  - Check timing: every line row, Time each line and Section starts open the player in Line view on that line.
  - Suggested breaths: gaps between lines (on lines with no breath mark of Ivan's) stored with the timing per section line, checked in `cleanTiming()` and carried in backups. Shown only in Q03's Phrasing layer; tapping one makes it a real Breath mark.
- **Settled at Render / Build:** a song with saved timing but no track on this device has no play-along; its timing is kept and shows on Check timing (Ivan, 30 Oct 2026).
- **Decided:** timing says when, marks say how. One sound at a time.
- **Not in it:** any timing without a track; Q07; the pinned ideas below.
- **Next action:** building now from the Q05 build handoff.
- **Done when:**
  - Everything above works; no path starts timing without a track.
  - Older timing survives untouched and old backups restore.
  - The full suite passes; the changelog headline ends with (Q05); Q05 is removed from this file in the same push.

## Q06 · Song Clock: Timeline View

**Status:** Retired at Q05's Render (29 Oct 2026). Its leftovers (tappable Check timing lines, Retime routes, snapping) are part of Q05. The ID isn't reused.

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
