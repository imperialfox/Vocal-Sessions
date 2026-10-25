# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.21.1** (25 Oct 2026).

- **Nothing here is approved to build yet.** Every item is awaiting Ivan's **"render"**. Earlier approvals (a wireframe, a prototype, a plan) are recorded per item, but only "render" starts a build or a push. When he says it, record when and for what in the handoff.
- **The code wins on what's built.** This is a summary, not a spec. Check each note against the code before relying on it.
- **Detailed design notes live in Ivan's private project notes, not in this repo.** Where an item names one, ask Ivan to paste or attach it. Anything not settled here is marked *Unresolved*.
- **Ivan can reorder the queue.** Versions follow build order: each build takes the next minor version when it's built.
- **When an item ships,** remove it from this file in the same push and say which version it shipped in.

Every item also follows [MAINTAINING.md](MAINTAINING.md): its [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [changelog](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style). On top of that:

- **Check the previous build is live first.** Look for its version in `CHANGELOG.md` on `main`. If it isn't there, stop and tell Ivan.
- **Never push with failing tests.** If something can't be finished, commit nothing, leave the item here and report plainly.
- **Everything that moves uses the shared springs.** Every new sound starts through `NOW.start()`.
- **The repo is public.**
  - Never commit real music, recordings, the coach video, course media, lyrics or backups.
  - Never commit with Ivan's personal email. Claude commits as `Claude <noreply@anthropic.com>`.

---

## 1 · Search (Render 10)

**Approval:** Awaiting Ivan's "render". Wireframe approved 22 Oct 2026.
**Needs:** 3.21 live (it is).

- **Goal:** find anything in the app from one place.
- **Scope:**
  - A permanent search circle beside the tab bar (iOS 26 style), and a search page.
  - It searches songs, lyrics, exercises and sessions, grouped.
  - **Takes group** (added 23 Oct): take names and comment text.
    - Each row shows the name or comment with the match highlighted, then "Song · Take n · when", plus the time for a comment.
    - Tapping a take opens its song with the takes sheet on All takes and that take expanded.
    - Tapping a comment also moves the playhead to its time, with the comment showing.
- **Not in scope:**
  - Settings pages aren't search content (a hit that should open a setting uses `SET.open(k)`).
  - A song's track isn't search content.
- **Decided:**
  - The circle is its own control, not a tab.
  - Search covers everything above, grouped.
- **Assumptions:** the Songs tab keeps its own list filter. This was an interpretation, not Ivan's decision.
- **Open questions:** which screens show the circle. Earlier build notes say it fits beside the Song Clock transport and the track player's transport at 375 px "if shown there", so this hasn't been decided.
- **Notes from earlier builds:**
  - The circle isn't a `TABS()` entry.
  - It must clear the song rows' play buttons, and `fwBounds()` must keep the floating window clear of it.
  - Take names and comments are plain strings in `sg.takeNotes`; default names come from `TAKE.nameOf(id)`.
- **Next action:** once Ivan says "render", build in a fresh chat. Ask Ivan for the search design notes (UI refresh handoff item 4, and item 12 of the songs, takes and markers handoff).
- **Done when:**
  - Every group finds its matches.
  - Take and comment hits open as described above.
  - The circle never covers controls or the floating window.
  - Every screen works at every size in light and dark.
  - The full suite passes.
  - *Unresolved:* any finer criteria in the design notes.

## 2 · Sections on the waveform (Track 2)

**Approval:** Awaiting Ivan's "render". Queued 23 Oct 2026. **Not scheduled until Ivan has used Track 1** (the track player, 3.19).
**Needs:** Track 1 live (it is).

- **Goal:** set a song's timing by scrubbing its track instead of tapping along live.
- **Scope:**
  - Set section starts by scrubbing the waveform, written into Song Clock's timing (one timing system: `ckStore` / `ckModel`).
  - Lyrics under the rows, and the current line above the strip.
  - Play-along runs off the in-app track.
  - Jog wheel left, right or bottom.
  - A marker chip's hold menu gains "Make this the <section> start". This writes its time into the timing and removes the marker.
- **Decided:**
  - Ivan prefers scrubbing the waveform to tapping along live.
  - Song Clock B's Timeline is absorbed here (the waveform is the timeline).
  - Pinch stays beside the level pills.
- **Open questions:**
  - Has Ivan used Track 1 enough to schedule this?
  - *Unresolved:* how the jog wheel's left / right / bottom choice is offered.
- **Notes from earlier builds:**
  - The strip and rows draw on canvases in `draw()`.
  - Play-along should follow `TRACK.now()` when `TRACK.has(id)`.
  - The jog wheel is currently fixed on the right.
- **Next action:** ask Ivan whether he's ready to schedule it. Then ask for the track player design notes ("Track 2, for later").
- **Done when:**
  - Sections set on the waveform appear in Song Clock's timing.
  - A chip promotes into a section start.
  - Play-along follows the track.
  - Old songs and backups still load.
  - The full suite passes.
  - *Unresolved:* finer criteria.

## 3 · Layered marks (Marks 1)

**Approval:** Awaiting Ivan's "render". Wireframes, prototype and plan approved 22 Oct 2026; a build handoff exists in Ivan's project notes.
**Needs:** Song Clock A1 live (it is). Planned after Search, or before it if Ivan asks (nothing depends on Search).

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
- **Notes from earlier builds:**
  - Add `'active'` to the Marks while playing cycle (`ckTileAct('marks')`, `CK_MPNAME`) and draw the active layer in `ckBuild()`.
  - Replace the pencil row's Edit lyrics / Marks pills with the Marks · Lyrics switch.
- **Next action:** once Ivan says "render", build in a fresh chat from the Marks 1 build handoff, which Ivan pastes in.
- **Done when:**
  - Everything decided above works.
  - Existing marks carry across without loss.
  - Old backups still restore.
  - The full suite passes.
  - *Unresolved:* finer criteria in the build handoff.

## 4 · Marks help (Marks 2)

**Approval:** Awaiting Ivan's "render". Guide text and prototype approved 22 Oct 2026; a build handoff exists in Ivan's project notes.
**Needs:** Marks 1 live.

- **Goal:** explain each mark where it's used.
- **Decided:**
  - A peek card when holding a mark button.
  - A Song key listing this song's marks.
  - A Marks guide with a page per mark: What it is, How to sing it, When to mark it, Example, and Don't confuse with.
  - A How to mark a song walkthrough.
  - All of these are reachable from several places in the app.
- **Assumptions:** the guide's wording is original writing and safe to commit.
- **Next action:** once Ivan says "render", build in a fresh chat from the Marks 2 build handoff and the guide wording, which Ivan pastes in.
- **Done when:**
  - Every door opens the right help.
  - Every mark has its page.
  - The full suite passes.
  - *Unresolved:* finer criteria.

## 5 · Song Clock A2 (Render 6)

**Approval:** Awaiting Ivan's "render". Planned, not scheduled.
**Needs:** Marks 1 live.

- **Goal:** time songs line by line, and fix lines in place.
- **Scope:**
  - The line pass, punch-in, flags and markers.
  - A hold menu with Retime line, Play from here and Annotate (Annotate replaces Mark to fix).
  - Suggested breaths from the line pass. They only become marks when Ivan taps them.
- **Decided:** timing says when, marks say how.
- **Open questions:**
  - **The line pass is to be re-scoped with Ivan after Track 2**, because he prefers scrubbing the waveform to tapping along live.
  - *Unresolved:* whether A2's "markers" are separate from the track player's markers (3.20).
- **Notes from earlier builds:**
  - Suggested breaths go with the timing, per line, checked in `cleanTiming()`.
  - Punch-in goes on the play-along layer, and the Flag goes beside the transport.
  - "Time each line" on Check timing only shows a toast until this build.
  - Tests use the test clock (`CLOCK.fake`, `CLOCK.advance`).
- **Next action:** after Track 2, re-scope with Ivan. Don't build until then.
- **Done when:** *Unresolved* until it's re-scoped.

## 6 · Song Clock B (Render 7)

**Approval:** Awaiting Ivan's "render". Dates to confirm with Ivan.

- **Scope:**
  - What's left of B: section starts, wheel pickers and Retime routes.
  - The Timeline itself is absorbed by Track 2.
- **Open questions:** the rest of B is to be re-scoped with Ivan after Track 2.
- **Notes from earlier builds:** these were left waiting for B:
  - Snapping is in the grid but does nothing yet.
  - Check timing's lines aren't tappable yet.
  - Section starts is still a plain row.
- **Next action:** re-scope with Ivan after Track 2.
- **Done when:** *Unresolved.*

## 7 · Song Clock C (Render 8)

**Approval:** Awaiting Ivan's "render". Dates to confirm with Ivan.

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
  - A moving gradient background on Today (Ivan wants to rethink the colours first).
