# Render queue

App work Ivan has queued, in the order he wants it built. Each item is one build, in a fresh chat, started from a handoff (see [HANDOFF.md](HANDOFF.md)). Last checked against `main` at **3.21.1** (25 Oct 2026).

- **Every item has two separate gates.** `Awaiting Render` means it is not approved. Ivan's **Render** approves only the named item's exact scope and moves it to `Approved — awaiting Build`; it does not start work or authorize a push. A separate **Build** instruction starts implementation for that approved item. Do not treat approval of one item as approval of the whole queue.
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

**Status:** Awaiting Render. **Approval:** Not yet given. Wireframe approved 22 Oct 2026.
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
- **Next action:** after Ivan gives Render approval for this item and separately says Build, implement it in a fresh chat. Ask Ivan for the search design notes (UI refresh handoff item 4, and item 12 of the songs, takes and markers handoff).
- **Done when:**
  - Every group finds its matches.
  - Take and comment hits open as described above.
  - The circle never covers controls or the floating window.
  - Every screen works at every size in light and dark.
  - The full suite passes.
  - *Unresolved:* any finer criteria in the design notes.

## 2 · Sections on the waveform (Track 2)

**Status:** Approved — awaiting Build. **Render:** Approved by Ivan on 25 Oct 2026 for the scope below.
**Needs:** Track 1 live (it is). A separate Build instruction is still required.

- **Goal:** set a song's timing by scrubbing its track instead of tapping along live.
- **Scope:**
  - Absorb Song Clock Phase B's timeline into the waveform; use one timing model through `ckModel()` and `ckStore()`.
  - Four views: Phrase (6 s), Line (16 s), Song (fixed 24 s overview rows), and Markers (two-column grid).
  - Show a three-line lyric context card above the 148 px Phrase/Line strip; show toggleable lyrics under Song rows.
  - Set section starts from marker chips through a section picker in `sg.order`; enforce chronological order, remove the promoted chip and provide one Undo that restores both timing and marker.
  - Play along from the in-app track, with backing audio on by default and a mute control.
  - Add the Marker grid's large rehearsal tiles, per-marker loop toggles, Replay / Play-Pause / Next transport, active state and quick-add tile.
  - Support Left, Right and Bottom jog positions, with touch expansion for the edge wheels and a full-width Bottom roller.
  - Use red playhead styling and resync looping and the playhead after device sleep.
- **Decided:**
  - Scrubbing the waveform replaces Song Clock B's Timeline.
  - `sg.timing` remains the only timing model; take undo snapshots before edits.
  - Marker data remains `sg.markers = [{ id, t, end?, name? }]`; no migration is needed for existing 3.20 markers or backups.
  - Device-only preferences `trkSongLyrics` and `trkJogPos` live in `vocalSongPrefs`.
  - Pinch stays beside the level pills.
- **Out of scope:**
  - Editing lyrics or section names from the waveform.
  - Cloud syncing audio or peaks; audio remains device-local in IndexedDB `vocalTracks`.
  - Pitch-altering time stretch.
- **Next action:** after Ivan separately says Build, implement this approved scope in a fresh chat with Claude as the sole builder. Check that 3.21 is live first.
- **Done when:**
  - Sections set on the waveform appear in Song Clock timing, and marker promotion is undoable without data loss.
  - Phrase, Line, Song and Markers views meet the approved layout and interaction requirements.
  - Play-along follows track time; sleep/wake looping is verified on iPhone.
  - Existing markers, untimed songs, songs without lyrics and old backups load without error.
  - The full suite passes.

## 3 · Layered marks (Marks 1)

**Status:** Awaiting Render. **Approval:** Not yet given. Wireframes, prototype and plan approved 22 Oct 2026; a build handoff exists in Ivan's project notes.
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
- **Next action:** after Ivan gives Render approval for this item and separately says Build, implement it in a fresh chat from the Marks 1 build handoff, which Ivan pastes in.
- **Done when:**
  - Everything decided above works.
  - Existing marks carry across without loss.
  - Old backups still restore.
  - The full suite passes.
  - *Unresolved:* finer criteria in the build handoff.

## 4 · Marks help (Marks 2)

**Status:** Awaiting Render. **Approval:** Not yet given. Guide text and prototype approved 22 Oct 2026; a build handoff exists in Ivan's project notes.
**Needs:** Marks 1 live.

- **Goal:** explain each mark where it's used.
- **Decided:**
  - A peek card when holding a mark button.
  - A Song key listing this song's marks.
  - A Marks guide with a page per mark: What it is, How to sing it, When to mark it, Example, and Don't confuse with.
  - A How to mark a song walkthrough.
  - All of these are reachable from several places in the app.
- **Assumptions:** the guide's wording is original writing and safe to commit.
- **Next action:** after Ivan gives Render approval for this item and separately says Build, implement it in a fresh chat from the Marks 2 build handoff and guide wording, which Ivan pastes in.
- **Done when:**
  - Every door opens the right help.
  - Every mark has its page.
  - The full suite passes.
  - *Unresolved:* finer criteria.

## 5 · Song Clock A2 (Render 6)

**Status:** Awaiting Render. **Approval:** Not yet given. Planned, not scheduled.
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

**Status:** Awaiting Render. **Approval:** Not yet given. Dates to confirm with Ivan.

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
  - A moving gradient background on Today (Ivan wants to rethink the colours first).
