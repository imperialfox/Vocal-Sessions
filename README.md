# Vocal Sessions

A mobile-first companion for structured vocal practice, styled like a native iOS app. It's a single HTML file with no install, no backend and no account. It's designed to live on your iPhone Home Screen.

![Version 3.31](https://img.shields.io/badge/version-3.31-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-blue) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![Works offline](https://img.shields.io/badge/works-offline-blue) [![Tests](https://github.com/imperialfox/Vocal-Sessions/actions/workflows/tests.yml/badge.svg)](https://github.com/imperialfox/Vocal-Sessions/actions/workflows/tests.yml)

**Current version: 3.31 · 30 Oct 2026.** See the [changelog](CHANGELOG.md) for what changed in each release.

---

## What it does

It brings guided practice sessions, progress tracking, and song practice together in one web app. Your sessions, exercises, songs, timing, takes and recordings stay in one place.

| Step | What | Time |
|---|---|---|
| Foundation | 4 core SOVT exercises, all required | ~25 min |
| Rotation | One or more exercises from a pool of 8, plus any you add | ~15 min |
| Application | Sing a real song or section, record a take, rate it | ~5–10 min |

There's also **Song practice**, for when you just want to sing a song and record it. Its clock starts with your first take, and it's kept separate from the focused stats above.

And **Songs**, for learning a song: paste the lyrics, and they're split into labelled sections you can mark up with breaths, runs, pitch, vowels, notes and cues. **Song Clock** times the lyrics so you can sing along with them, and the **track player** loops a phrase of the song's real track, slowly, with the pitch kept.

---

## Tabs

**Today**
- Today's date, tucked just above the title (which sits at the same height as every other tab's title). Tap the date, the title or the arrow to open a practice calendar:
  - Focused sessions are highlighted, and song practice shows as a coral dot.
  - Tap a day to see and open what you did.
- A reminder to back up if you never have, or if it's been more than two weeks
- A progress arch showing this week's minutes against a 70-minute goal. Tap it to open Progress on this week's sessions.
- A Monday-to-Sunday row that fills in each day you practised
- A weekly streak: weeks in a row where you hit 70 minutes. The current week never breaks it while it's still in progress.
- This month's minutes against 280, and the suggested rotation exercise (the one that's gone longest since you last did it)
- Start, resume or discard a session. A session you've left also shows in the **floating window** (below).
- A Song practice card with its own weekly stats. It opens the Songs tab, where every song's page is the place to practise it (song practice already going carries on from its song).
- **Pinned songs:** up to 3 songs you're working on, each with a play button for its track, and **Show all songs**
- **Settings** is the gear at the top right
- A soft moving wash of colour behind the date and title (Settings › Appearance can switch it off)
- Pull down to refresh. This also checks for a newer version of the app and loads it.

**Progress**
- **Recent:** your last 5 sessions, each with a small bar showing how its time split. **Show all sessions** opens the full list.
- **Practice time:**
  - A **D · W · M · 6M · Y · All** switch, like the Health app
  - Your total time for that period, with arrows to step back through earlier ones
  - A stacked bar chart: Foundation (indigo), Rotation (teal) and Application (amber). Tap or slide across the bars to see each hour, day, week or month.
  - A breakdown of time and percentage for each step
- **Filled in at the end:** if you don't tap through each step (for example, following the coach video in the car), the app notices and shows that session as a blended bar. Its time is still split using the coach video's length for each exercise and the levels you did, with Application as whatever's left. Sessions from before this version are split the same way.
- **Song practice:** this week's and this month's totals, your last 3 song practices, and **Show all song practice**
- **All sessions:** a **Sessions | Song practice** list, grouped by month. Open any session to:
  - Edit it with the pencil: date, minutes, levels, notes, how it went, and how its time was split between the steps. Totals, streak and last-done dates update to match.
  - Delete it
- Every summary leads to the same lists and details, from wherever it appears: Progress, the calendar, Today and Exercises.
- Pull down to refresh

**Search** (the circle beside the tab bar)
- A search circle sits beside the tab bar on every tab (iPad: at the end of the tabs at the top; a wide window: a Search row at the top of the sidebar; Cmd + F from a keyboard).
- Before you type: your recent searches (kept on this device only) and your pinned songs.
- As you type, results appear grouped: **Songs**, **Lyrics** (the line, highlighted, with its song and section), **Exercises** (their names and write-ups), **Sessions** (their notes and feedback words) and **Takes** (names you've given them and your comments). Each group shows its top three, with **Show all**.
- A song or exercise zooms open from its result, and Back returns to the same results. A lyric opens its song scrolled to that section, focused. A session opens its details. A take opens its song's takes with that take expanded; a comment also moves to its time and shows it.

**Songs**
- **New song (+):** one button, two ways in. **Add media** (the default) picks the song's audio from Files: once it's read, the form opens with the length taken from the file (linked to it) and the title empty (left blank, it uses the file's name, since metadata can't be trusted). Lyrics are optional; save and the song opens, ready to paste them later. **Manually** is the form below, as it always was. Nothing is stored until you save.
- **Lyrics:** paste lyrics from anywhere. Labels like `[Chorus]`, `Verse 2:` or `PRECHORUS` start sections, and blank lines split them too. Website clutter (links, "You might also like", "Embed") is removed, a chorus that repeats itself is split in two, and exact repeats are linked. Check the labels, change any marked **Guessed**, and save. The original paste is kept untouched.
- **The list:** up to 3 pinned songs at the top, then the rest sorted by Recently practised, Recently added or Title A–Z (tap the heading). Each row says when you last practised it and how many takes it has ("Practised today · 2 takes", or "Not practised yet"), never graded, and has a **play button** for the song's track (greyed, with "Upload a track to play", when there's no track on this device).
  - Swipe right to pin, left to delete. Press and hold (or right-click) for Pin, Rename and Delete. **Edit** selects several songs to pin or delete.
  - **Search songs** (the field under the title) filters the list by titles, artists and lyrics. It ignores case, punctuation and accents, finds words in any order, even across lines, and forgives a slipped letter in longer words. Lyric matches show the line with the words highlighted.
- **A song:** one continuous page, one phrase per line, with a small label above each section, repeats numbered (Chorus 1, Chorus 2) and linked sections marked with a chain.
  - **Tap a section to focus it:** a soft patch appears behind it with **Record**, its takes and **Marks** (which opens the Marks side there). The rest of the song dims and softly blurs with distance, while labels stay sharp. Tap it again, or away from the lyrics, to clear it. With Reduce Motion on, the rest only dims.
  - **Takes** beside the title opens every take of the song (see Takes below).
  - **The header:** the artist and the song's length ("Artist · 3:58"; tap the length to change it on clock-style wheels). With a track, the length follows it and shows a link icon: tapping it asks **Unlink from track?** first. A custom length shows a broken link ("Custom · track is 3:42"); tap it to relink. up to three pinned buttons (Timing and Key to start with), and **⋯** for **Song controls**: Timing, Check timing, Key, Marks while playing, Blur ahead, Snapping, Stay awake, Lyrics and Track. Blue means on; **Edit** chooses what's pinned.
  - **Marks come in four layers**, one for each stage of learning a song: **1 Notes** (pitch, slides, holds, ornaments, rhythm), **2 Phrasing** (phrases, chains, peaks, breaths, shape), **3 Words** (vowels, carrying a consonant, onsets, stress, how to say a word) and **4 Delivery** (register, colour, vibrato, mic, and the section's intention). A **Note** bookmark shows on every layer. Only one layer shows at a time: pick it with the chips **1–4** above the lyrics (remembered on this device). Labels sit above their words like chords over lyrics; phrases are brackets over their words; breaths, chains and Notes sit after theirs.
  - **Practise** shows the chosen layer; **Perform** shows what **Marks while playing** allows, plus the expressive cues. **Key** explains every mark.
  - **Recall** hides the lyrics a step at a time to learn them by heart: Full lyrics, Word shapes, First words, Cues only and Blank. Hidden letters become soft pills in place, so nothing moves; phrase brackets, chains, breaths and Notes stay visible over them. Tap a line to peek, or hold it to keep it showing. Tap a section's label to focus it. Work from the start, from the end, or start anywhere.
  - **Song Clock** (Timing) runs off the song's own track on this device. Without one, Timing reads **Add a track to time this song** and opens Files. Timing saved on an older song (or with its track on another device) is kept and shows on Check timing; play along needs the track. On a song that isn't timed yet, Timing opens the track player to place its sections and lines.
    - **Play along:** tap the first line as it's sung. Play-along plays the song's track and the lyrics follow its time, with a mute button beside the nudges. The lyrics turn big, the line you're singing fills word by word, sung lines dim and coming ones blur a little more with distance (**Blur ahead**). Tap any line to jump there; **−0.2 / +0.2** move all the lyrics, with Undo. **Pause** shows the lyrics page with your line highlighted where your eye was. The screen stays awake while timing (**Stay awake**). Leave the song while it plays and the floating window says **Playing along** with the time and section.
    - **Fix a line while you sing (punch-in):** hold the lyrics for half a second as a line starts. That line (the one you're singing or the next) starts where your finger went down, and letting go sets its end. A toast says **Re-timed**, with Undo. A quick tap still jumps.
    - **Flag** (beside the transport) drops a marker on the track where you are, with Undo. Paused, the same button is **Retime**: the track player opens on the line you're on.
    - **Hold a line** on the song page (Practise or Perform) for its menu: **Retime line** (the track player on that line), **Play from here**, and **Annotate** (the Marks side with the whole line selected, on the layer you used last). The line lifts and the rest dims. In Recall a hold still peeks.
    - **Marks while playing:** **Breaths only** (the default) shows your breath marks, plus a small dot on lines with a long gap after them and no breath mark of yours; everything else is hidden while you sing. **Active layer** also shows the chosen layer's marks on the line you're singing and the next one. **Off** hides them all. Notes never show while you sing.
    - **Check timing:** each section and line with a bar for its length (dashed while it's an estimate), Very short and Very long flags, lines to look at again, section starts set and the song length. Tap any line, **Section starts** or **Time each line** to open the track player on it.
    - **Suggested breaths:** a gap you leave after a line you've placed becomes a suggested breath. It shows only in Phrasing on the Marks side, as a faint dashed **’ +** at the line's end; tap it to make it a real breath mark.
    - Changing a line of lyrics only clears that line's timing (and gives it a to-do marker until you place it again).
    - **Section starts from the waveform:** hold a marker on the track player and choose **Make this a section start…**, then pick the section. Starts stay in time order (places that would break it are greyed, with why), the marker becomes the start, and one **Undo** puts back both the timing and the marker.
  - The pencil edits the title, artist and length in place, with a **Marks · Lyrics** switch and **Done**. On the **Marks** side, tap a word to select it, and tap another on the same line to select the words between. A sheet rises with the chosen layer's five marks and Note; a mark with options shows them underneath, one tap deep, and some take a few words (Sing as, Say, Intention, Notes). **On these words** lists what's already there, each with ✕; adding or removing shows **Undo**. Marks on a linked chorus show on every repeat. Words make room for their labels, so labels never overlap. Add a cue to a section, unlink a repeat to give it its own copy, or hold a section to move it. Undo steps back through changes.
  - **Marking while listening:** tap the pencil while playing along and the Marks side opens with the song still going: the time is a pill at the top (tap to pause), and the line being sung is softly lit without the page moving.
  - **Lyrics** edits the words. Marked words are highlighted, marks follow their words (on every layer), and a mark whose word changed is flagged to check, with **Keep** in the sheet. One whose word was removed waits at the top of its section to be moved or removed. Marks from before 3.27 moved into their layers: breaths into Phrasing, runs and higher/lower into Notes, sing-as into Words, and notes into Notes.
  - **Record a section:** in Practise or Perform, focus a section, then **Record**. The screen stays on that section while it records, with a recording bar at the bottom (time, level meter, Stop). Stopping opens the takes for that section over the song, with the new take ready to play. Each repeat keeps its own takes, even when linked. A take on any song page starts (or carries on) song practice for that song, timed from that first take.
  - **Takes:** a switch between this section's takes and **All takes**, newest first. All takes is grouped by section: a row for each with its count, folding open to its takes (the section you came from starts open). Tap a take to expand and play it: a waveform you drag to scrub, −5 s and +5 s, and its name (tap to rename; the original details stay underneath). **Comments** are stamped with the time: the moment you start typing, the playhead's time is locked (tap it for −1 s, +1 s or Use current time). While it plays, each comment pops up as the playhead passes it; dots under the waveform jump to them. Swipe a take right to star it, left to delete it, or hold it for both. Names and comments are in every backup.
  - **Song practice** at the bottom starts song practice with that song picked.
  - **Track** (beside it) adds the song's audio from Files, then opens the **track player**:
    - **Views:** **Phrase** (6 s) and **Line** (16 s) are a strip moving under a red playhead, with a three-line lyric card above it: the line before, the line at the playhead (with its section) and the next. **Song** shows the whole song in rows of 24 s, the last one ending at the track's end, with the lyrics under each row (the **Lyrics** pill hides them; tap a line to go to it). **Markers** is a grid of tiles (below). Tap a row to move the playhead there (the view stays). Change the view with the level pills, or pinch. Section starts set in Song Clock show as blue lines with their names.
    - **Jog wheel:** on the right, the left or as a full-width roller under the strip (the player's ⋯ menu). Drag slowly for precision, quickly to skim: down (or right, on the roller) is later. The edge wheel slides further in under your finger.
    - **The line lane (Phrase and Line):** a block for each lyric line under the waveform, dashed while it's an estimate and solid once you've placed it. Drag a block's edge to move it; where two lines touch, one handle moves both. Or tap a block and use **Start here** / **End here** at the playhead. With **Snapping** on (Song controls), edges snap to the playhead, section starts and the other lines' edges. Every change has Undo, and it's the song's one timing.
    - **Markers:** **Marker** drops a purple marker at the playhead, playing or not. Markers show on the waveform at every level and as numbered chips in one sideways row: tap a chip to jump there (playing carries on). **End n here** gives the current chip an end, and a chip with an end has its own loop button. Dragging the orange handles while a chip's loop is on updates the chip. Hold a chip to rename it, move it to the playhead, set or remove its end, or delete it; **Clear all markers** is there and in the player's ⋯ menu. Markers are saved with the song.
    - **Markers grid:** a big tile for each marker. Tap one to play it and loop it to its own end, or to the next marker (the last one to the track's end); markers under half a second apart don't loop. Each tile has its own loop button. The marker you picked is outlined and the one playing is tinted, so you see both. The transport here is **Replay** (back to the marker's start), Play/Pause and **Next** (the next marker, moving its loop along). The last tile adds a marker at the playhead.
    - **Loop:** **Set start** and **Set end** at the playhead, or drag the orange handles (they swap if you drag one past the other). Audio outside the loop is dimmed; double-tap outside it to clear it. The transport has back to the loop start, Play and Loop.
    - **Speed:** 0.5×, 0.75× or 1×, with the pitch kept. The view, speed, jog wheel side and Lyrics pill are remembered on this device; the loop is saved with the song. With the screen locked, the loop is kept as well as iOS allows, and waking puts a stray playhead back in the loop.
    - On a Mac or with a keyboard: Space plays, ← and → move a second (Shift: five), I and O set the start and end.
    - MP3, M4A, WAV, AAC and AIFF from Files work; songs from Apple Music can't be added. The track stays on this device and isn't in backups (see [Data and privacy](#data-and-privacy)). Its settings button has **Replace track** and **Remove track**.
- Songs from song practice are here too, and **Add lyrics** gives them lyrics without losing their recordings.

**Exercises**
- **Coach video** at the top: the coach video you've added to this iPhone, or **Add coach video** before you have (see [Coach video](#coach-video))
- Every exercise with its own glyph (coloured by focus area) and when you last did it
- Tap an exercise for its own page:
  - **Summary:** what it is, why it helps, and where it shows up in songs
  - **History:** a chart of your level over time, plus every session it was in, with your notes
- Add your own exercises (with an optional description). Swipe left to delete them.


**Settings** (the gear on Today) works like the iPhone's Settings app: a list of rows, each with its own icon, opening its own page. Each row shows where things stand on the right (when you last backed up, space used, and so on).
- **Backup** (a page with a short explanation at the top):
  - **Export backup:** one file with everything (sessions, minutes, exercises, songs with their lyrics and marks, and recordings), checked before you save it. **Exclude recordings** makes a smaller file without them (the sheet shows the size either way); restoring it keeps the device's recordings. Takes' names and comments are always included. Keep it in iCloud Drive › Vocal Sessions › Backups.
  - **Import backup:** checks the file and compares it with what's on this device, then replaces this device's data after you confirm.
  - **Check a backup:** tells you whether a file is complete and what's inside, without changing anything.
  - **Undo last restore:** for 30 days after a restore.
  - When you last backed up, which turns red after two weeks (on the Settings list too)
  - **Backup history**, **Where backups go** (a set-up guide) and **Save a read-me file**
- **Storage** (a page with a short explanation at the top): one bar showing what's using space (recordings, song tracks, the coach video, and sessions and songs), then recordings (how many takes and how much space), **Review old takes** (unstarred takes with no comments, oldest first, to clear by hand: nothing is ever removed for you), and **Storage protection**, which shows whether iOS has agreed not to clear the app's data when space runs low
- **Recall › Peek length:** how long a tapped line shows in Recall (1, 2, 3 or 5 seconds)
- **Coach video:** add, replace or remove it (see Coach video below)
- **Appearance:** **Gradient background**, the soft moving wash behind Today's header, on unless you switch it off. For this device only, not in backups.
- **Accessibility:** **Reduce motion** (Match iPhone, On or Off) swaps zooms and slides for short fades; **Slow motion** plays every animation four times slower, for checking how it feels. Both are for this device only and aren't in backups.
- **Changelog:** every version on a timeline, with a growth chart of improvements by area. It's built from [CHANGELOG.md](CHANGELOG.md).
- **View on GitHub:** this repo
- Reset this month, and reset all data. Every reset asks first.
- At the bottom, the app's icon, name, version and release date (tap it for the Changelog)

---

## Session details

- **Levels:** each exercise has 3 levels. Foundation uses a Skip · 1 · 2 · 3 picker, and skipped exercises don't count as done.
- **Multi-select rotation:** pick as many as you like, each with its own level
- **Notes per exercise:** the pencil opens quick words written for that exercise, your own saved words, and an optional note
- **Session clock:** a live timer in the top bar
  - Tap it for a larger clock with Pause and a time for each step. Paused time isn't counted.
  - Song practice's clock starts when you record your first take; until then the timer says **Not started**.
  - Sessions over 90 minutes ask how long you actually practised.
- **Floating window:** leave a session, or switch away while something plays, and a small window stays on every other screen.
  - **One sound at a time:** a take, a recording, the coach video, a song's track and play-along all go through one place, so starting any of them stops whatever was playing. The lock screen's buttons follow whichever started last.
  - Every sound's window has a **✕**, playing or paused. It stops the sound and closes the window, and nothing brings it back except playing it again: not switching tabs, a sheet, coming back to the app or a reload. Nothing else pops up in its place on that screen. When a sound finishes, its window goes.
  - A sound's window shows while it plays, and when you paused it from the window (or the lock screen). Paused anywhere else, it doesn't follow you.
  - A session shows what's running (for example "Focused session · Rotation"), its live time and a pause button. Paused, it says Paused and the time stops.
  - A take shows "Playing · Chorus 2" (or the song's name for song practice), its time and progress, and a pause button. It goes when the take ends.
  - A song's track shows "Playing · song title", its time and progress, and a pause button. Pause it on the player itself and it doesn't follow you out.
  - If more than one is going, a take wins, then the coach video, the track, play-along and a session, in that order.
  - Tap it to go back to exactly where you were: the same step at the same scroll, or the song with that section's takes open.
  - Drag it to any corner and it snaps there. It remembers the corner on this device.
  - It hides on its own screen, while a sheet is open and while you're recording.
  - Closing a section's takes sheet lets a playing take carry on, so you can listen while you look at the lyrics.
- **How did it go?** After finishing, tap words that fit (or add your own) and an optional note. You can skip it.
- **Recordings:**
  - Mono AAC at about 96 kbps (about 0.7 MB a minute), with the phone's voice processing off, up to 2 minutes per take
  - Every take is kept; nothing is removed automatically. **Settings › Storage › Review old takes** helps clear old ones by hand.
  - New takes are mixed down to one channel before they're saved. Older takes with the voice on one side play from a copy made for both ears; the original is never changed.
  - Tap a take to add notes, such as "Flat on the high note"
  - Each take can be shared (Save to Files or iCloud Drive) or deleted
  - Leaving the app while recording stops the take and saves it
---

## iPhone, iPad and Mac

The layout follows the device, like a native Apple app:

| Screen | Layout |
|---|---|
| iPhone | A floating tab bar at the bottom, placed as in Apple's own apps, with the search circle beside it. Scrolling down a long page shrinks it to a small pill at the left; scrolling up, or tapping the pill, brings it back |
| iPhone on its side | A compact tab bar, with Today in two columns |
| iPad, or a narrower Mac window | Tabs at the top, a dashboard on Today, and split views for History, Exercises and Songs |
| Mac, or iPad in landscape | A sidebar |

Opening the app shows a short launch screen with the app icon, in light or dark to match your phone. On a fresh open, the icon's sound-wave bars pulse one after another (the launch ripple), then the screen fades with a slight zoom and Today's blocks rise in from top to bottom. It plays again after an update loads or a backup is imported, but not when switching tabs or coming back to the app. With Reduce Motion on, the launch screen just fades. The launch images iOS shows before the app starts are in the `splash` folder.

Lists push their pages in from the right, as on iPhone: a song from Songs, Today's pinned songs, Show all songs, Search's songs, lyrics and exercises, the Exercises list, Check timing and the track player's Retime from a song, and Settings' rows and Changelog. The page underneath slides a little to the left and dims. Other cards that open a page zoom into it: the suggested rotation, Song practice and the track on a song's page, the coach video, Show all sessions, the weekly goal arc, and the Start session button, which expands into the session. Back reverses either, with the list where you left it, and finishing a session shrinks it back into Start session. You can swipe back from anywhere on a page with a Back button, not just the edge: the page follows your finger and goes back past about a fifth of the screen or with a quick flick, otherwise it settles back. Scrolled down, the top bar becomes a soft blur that fades out under the status bar. A row's own swipe (pin or delete), sliders and charts you slide across always come first. Tapping a day in the practice calendar grows its sessions out of the day, and a new song's paste sheet shrinks into its row before the song opens.

Small movements show what changed: deleted rows shrink away and the gap closes, a pinned song travels into Pinned, the Progress bars ripple to new heights in the direction of time, the weekly goal arc fills after launch, and Recall hides lyrics word by word. Anything you drag or scrub follows your finger instantly, and nothing moves while you record or perform. With Reduce Motion on, changes fade instead of moving (zooms become a short fade, and a swipe back moves sideways only).

Sheets open as centred cards on bigger screens. With a mouse or trackpad, rows highlight on hover, and resting on an icon-only button (the top bar's round buttons and the track player's) shows what it does after a moment. On iPad and Mac the track player's marker tiles go three across when their side of the screen has room.

Text sizes, colours and backgrounds follow Apple's: one set of text styles, Apple's system colours in light and dark, and darker grey for anything inside a card. Keyboard shortcuts (Cmd on an iPad keyboard or a Mac, so Ctrl stays for editing text; Ctrl on other computers). They work once per press and not while a sheet or picker is open or you're recording; Cmd + 1 to 4, the arrows and the track player's keys also wait while you're typing:

| Keys | Does |
|---|---|
| Cmd + 1 to 4 | Today, Progress, Songs, Exercises |
| Cmd + , | Settings |
| Cmd + F | Search |
| Cmd + N | New song (in Songs) |
| Cmd + E | Edit the open song, and again for Done |
| ↑ ↓ | Move between songs (iPad and Mac) |
| Esc | Close a sheet, menu or search, or deselect a word |

---

## On iPhone

1. Open the GitHub Pages URL in **Safari**
2. Tap Share → **Add to Home Screen** → Add

iOS sets a Home Screen app's icon when you add it. To pick up a new icon:
1. Export a backup
2. Remove the app and add it again
3. Import the backup

Removing a Home Screen app deletes its data, so always export first.

**On iPad:** the same steps in Safari.

**On a Mac:** in Safari, choose File → Add to Dock. Each device keeps its own data, so use Export and Import backup to move your progress between them.

---

## Adapting it for yourself

Everything to edit is in `js/content.js`, which starts with a guide to what's safe to change: `VIDEO` (your coach video), `TARGET` and `WEEK_TARGET` (minutes), the `FOUND` and `ROT` exercise lists, `DESC` (the write-up shown on each exercise's Summary tab), `EX_WORDS` (quick words for each exercise) and `HOW_WORDS` (the "How did it go?" words), and `VID` (how long each exercise runs in the coach video). Run `python tests/run.py content` after editing to check it all fits together.

---

## Coach video

Since 3.16 the coach video can play inside the app, from a copy kept on your iPhone.

- **Add it:** Settings › Coach video › Add coach video… and pick the video from Files (about 57 MB). It's stored on this device only. It isn't put online, and it isn't in your backups.
- **Keep the file in Files.** After re-adding the app or moving to a new phone, restore your backup, then add the video again the same way.
- **Replace or remove it:** Settings › Coach video › Replace video… or Remove video. Reset all data doesn't remove it.
- **Chapters:** a video the length of the coach video (79:33) gets its 12 exercises, starting at the YouTube timestamps (`COACH_TIMES` in `js/content.js`). Give an exercise three times there (Level 1, 2 and 3) and it gets the L1 · L2 · L3 picker too. Any other video plays as a plain video, without the exercise list.
- **Where it plays:** the player (Exercises › Coach video), Play with coach on an exercise's page, and a Coach video row in Foundation and Rotation that shows the video when you tap it. Leaving while it plays keeps it going in a small window.
- A Home Screen web app may pause when the phone locks. That's iOS, not the app.

## Offline

A small service worker (`sw.js`) keeps a copy of the app on your device. When you're online, the app loads fresh and picks up updates. With no signal, or a connection too slow to answer within 4 seconds, it opens from the saved copy. The changelog is kept for offline use the same way.

## Data and privacy

- Session data and songs are stored in `localStorage`, and recordings, the coach video and song tracks in IndexedDB, all on your device only. The coach video and song tracks are never in backups: a restored song keeps its loop and timings, and says **Track not on this device** until you add the same file again. Lyrics you paste stay on your device and in your backups; they're never part of the public app.
- There's no server, analytics or tracking.
- Backups are plain JSON files that you keep. See [Backups](#backups).

## Backups

**Names.** `Vocal Sessions backup · 2026-10 · iPhone.json`: one file per month for each device. Backing up again in the same month, Files asks whether to replace that month's file.

**Where.** iCloud Drive › Vocal Sessions › Backups. Settings › Backup › Where backups go walks through making the folder the first time; Files remembers it after that.

**Check code.** Every backup ends with a SHA-256 fingerprint of its contents. Before offering to save, the app reads the finished file back and checks it. Check a backup and Import check it again, so a file that was cut short while copying, or edited, is spotted before anything is replaced. Backups from before 3.6 have no check code; they still import and are checked for readability.

**Before you restore.** A backup from a newer version of the app says so and suggests updating first. Import shows the backup next to what's on this device: sessions, song practice, songs, recordings, practice time and the latest practice. If anything on the device isn't in the backup, it says how much would be removed and offers to back up first. A copy of the device's data, recordings included, is kept for 30 days so the restore can be undone.

**Finding them later.** Each file opens with a short plain-English note: what it is, which device and app version made it, how many sessions and recordings it holds, and how to restore it. Settings › Backup › Save a read-me file saves `READ ME – Vocal Sessions backups.txt` for the folder too.

---

## Stack

Vanilla HTML, CSS and JavaScript, with no frameworks or build step: `index.html`, one stylesheet in `css/` and a dozen plain scripts in `js/`. It uses the iOS system font and a CSS imitation of Liquid Glass: rim light, inner glow, a collapsing tab bar, a soft blurred edge under the top bar, sliding glass pickers and springy motion.

---

## Development

See [MAINTAINING.md](MAINTAINING.md) for how the app is built, where data lives, the rules that keep old backups working, and how to release.

- `python tests/run.py` runs the full test suite in Chromium, several files side by side: every screen at every size, a full practice session, songs, backups (including real ones from earlier versions), recording, and thousands of random taps. GitHub runs it after every push. `python tests/run.py quick` skips the slow layout and random-tap checks while building.
- `python tools/release.py 3.7` sets a new version number everywhere at once.

---

## License

MIT

---

*Built by [ivanc.digital](https://ivanc.digital)*
