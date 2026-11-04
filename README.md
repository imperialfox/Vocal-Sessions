# Vocal Sessions

**A practice room in your pocket. It coaches you through your warm-up, helps you learn your songs, and keeps every take so you can hear your voice improve.**

It's a web app styled like a native iOS app: a single HTML file with no install, no backend and no account, designed to live on your iPhone Home Screen. It runs on its own, with no other apps needed.

![Version 3.57](https://img.shields.io/badge/version-3.57-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-blue) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![Works offline](https://img.shields.io/badge/works-offline-blue) [![Tests](https://github.com/imperialfox/Vocal-Sessions/actions/workflows/tests.yml/badge.svg)](https://github.com/imperialfox/Vocal-Sessions/actions/workflows/tests.yml)

**Current version: 3.57 · 4 Nov 2026.** See the [changelog](CHANGELOG.md) for what changed in each release.

---

## What it's for

The goal is a better voice overall: range, control and tone. A good session is one where you hear that you sound better.

- **The recordings are the heart of it.** They're proof you're improving, honest feedback and a record of the journey, and they can't be replaced. Everything else could be rebuilt.
- **Exercises and songs are equal halves** of the same practice. Neither is just the warm-up or just the reward.
- **It connects everything.** Takes belong to songs, sections and exercises, so nothing sits on its own.
- **It teaches.** It explains how each exercise goes and why, as well as running it.

What it isn't:
- **Not a grader.** It never scores or judges your singing.
- **Not a karaoke app.** Singing along is training, not for fun or sharing.
- **Not a habit tracker.** Streaks and minutes are a side benefit, not the point.

**The first test for any new idea: does it make practice easier?** Does it get you singing sooner, with less fuss?

Earlier versions were a logbook alongside a time tracker and a YouTube video. Since then the app has grown to cover the whole practice.

---

## What it does

It brings guided practice sessions, progress tracking, and song practice together in one web app. Your sessions, exercises, songs, timing, takes and recordings stay in one place.

| Step | What | Time |
|---|---|---|
| Foundation | 4 core exercises, all required | ~25 min |
| Rotation | One or more exercises from a pool of 8, plus any you add | ~15 min |
| Application | Sing a real song or section and record a take | ~5–10 min |

There's also **Song practice**, for when you just want to sing a song and record it. Its clock starts with your first take, and it's kept separate from the focused stats above.

And **Songs**, for learning a song: paste the lyrics, and they're split into labelled sections you can mark up with breaths, runs, pitch, vowels, notes and cues. **Song Clock** times the lyrics so you can sing along with them, the **track player** loops a phrase of the song's real track, slowly, with the pitch kept, and **sheet music** reads your own Ultimate Guitar print of the song into its notes, bars and key.

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
  - **Practise** shows the chosen layer; **Perform** shows what **Marks while playing** allows, plus the expressive cues. **Key** lists the marks this song uses; tap one to learn it.
  - **The Marks guide** has a page for every mark (what it is, how to sing it, when to mark it, an example, and what not to confuse it with) and **How to mark a song**. Hold a mark button on the Marks side for a quick card about it. The guide opens from Settings, the song's ⋯ controls and the Marks side.
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
  - **Sheet music (3.56):** add your own Ultimate Guitar print of the song (in UG, the Vocals part, notation plus tab view, printed from Safari as a PDF). It's read on your phone, line by line, with Cancel, into the song's notes, bars, rests and key. Check what was read, set the octave (Lower, As written or Higher, suggested from Your voice) and the tempo, and save; the key sheet then offers the print's key. The row shows the key, bars, range and where the song sits against your voice; tap it for what to check (bars that don't add up, repeats, notes it muted). A print that isn't right says what to do. The score is in your backups; the PDF stays on this device. New song's **Add media** takes a print too. No playback yet.
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
  - **Summary:** the exercise explained and ready to sing. A drawing of the pattern with a red playhead, three facts for the level, a fix tip, **How to do it**, **Where you feel it**, the level dots (on the level you last logged), why it helps and where it shows up in songs.
  - **Hear it:** the app plays the pattern itself, with a recorded piano (or notes it makes itself), starting on the coach's notes for the level and moving up a key each round. A chord sets up each key, a low note holds underneath, and it ends back on the starting key. The dock has the pattern, its speed (a slider from 0.5× to 2×, or speeding up each round), the sound (Piano, the default, Soft tone or Electric piano), the starting note, Stay on this key and Play. It plays with the silent switch on and keeps the screen awake. Vocal slides has a picture instead.
  - **Patterns:** tap the pattern to choose from 60: Warm-ups, Agility, Riffs and runs (short riffs, turns and slingshots, long runs, minor, blues and gospel) and Flips (full voice into falsetto), plus your ★ Favourites. Tap one to hear it; press and hold to see what it trains. Each exercise remembers its pattern, starting note and speeds.
  - **Your voice:** the card warns when a pattern goes above or below your range (set in **Settings › Your voice**), and can stop at your top note.
  - **Your bridge** (3.53), where your voice flips: **Find your bridge** listens to one slow slide on "ee", draws it as you go and marks where your voice jumps, then suggests a zone around it (two notes below to one above) that you can change before **Use this bridge**. No jump? Set it by feel. Once it's set, the drawing shades the bridge and rings its notes, the line under it says which rounds cross it, those reference notes play softer, and while one plays a cue says **Thinner · quieter** (on a hum) or the narrower vowel (ah → uh, ee → ih) and quieter. The cue can be switched off in Settings › Pattern player.
  - **Listen while I sing** (off to start): while the pattern plays, the microphone shows your voice as a dot with a short trail on the drawing. Headphones in, so it only hears you. Nothing is recorded. When you hold a round's top note cleanly, **Last time** moves up quietly ("Last time: F4 · today"), and **Stop one past last time** (Settings › Your voice) ends the exercise one round past it. No scores, no right or wrong.
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
- **Your voice:** your voice type (Bass to Soprano, tenor to start) and its lowest and highest comfortable notes and falsetto top, which the exercise pages check patterns against, **Stop at my top note** and **Stop one past last time** (when both are on, the earlier stop wins), and **Your bridge**, which opens Find your bridge. In backups.
- **Pattern player:** the sound, the held note underneath, the chord before each round, the ending (home chord, home note or off), the vowel cue, dots or music notes on the drawing, the **Bridge cue** and **Listen while I sing**. In backups.
- **Appearance:** **Gradient background**, the soft moving wash behind Today's header, on unless you switch it off, and (3.50) **Show screen IDs**, a small label in the corner with each screen's permanent ID (such as VS-001 for Today), for pointing at a screen in a note. Both are for this device only, not in backups.
- **Accessibility:** **Reduce motion** (Match iPhone, On or Off) swaps zooms and slides for short fades; **Reduce transparency** makes the glass more solid, so what's on it is easier to read; **Slow motion** plays every animation four times slower, for checking how it feels. All are for this device only and aren't in backups.
- **Changelog:** every version on a timeline, with a growth chart of improvements by area. It's built from [CHANGELOG.md](CHANGELOG.md).
- **View on GitHub:** this repo
- Reset this month, and reset all data. Every reset asks first.
- At the bottom, the app's icon, name, version and release date (tap it for the Changelog)

---

## Session details

- **One page (3.39):** Foundation, Rotation and Application follow each other on one page. A finished step folds to a one-line summary (tap it to change anything, then Done), the next one slides up, and the one after shows faded underneath. You can't jump ahead: pulling past the bottom springs back and says what's still needed. One pinned button logs each step: **Log foundation**, **Log N exercises** (or **Skip rotation** with nothing picked) and **Finish session**.
- **Levels:** each exercise has 3 levels. Tap an exercise's row to go up a level: Foundation goes 1, 2, 3, then Skip (skipped exercises don't count as done); Rotation goes 1, 2, 3, then off.
  - At level 3 the card sweeps blue then green and asks **How did it feel?**; at levels 1 and 2, after a moment, **What kept it at level N?** Tap any words (or **+ Your own**); they're saved as that exercise's note, and the row folds to one line so you can move on to the next.
- **Rotation:** the suggested exercise on top, then **More exercises**, sorted by Longest ago, Most recent or A–Z, each saying when you last did it. Pick as many as you like. **Just Foundation today? Finish here** ends the session from an empty Rotation.
- **Coach video in a session:** it sits in the floating window during Foundation and Rotation, cued to the step's exercise; Application shows a **Coach ▸** pill instead. Drag either to any corner. ✕ tucks the video into the pill.
- **Session clock:** a live timer in the top bar
  - Tap it for the clock (3.42): one ring in three slices (Foundation, Rotation, Application) sized by your usual time for each step, with a tick where you usually move on. Logged steps fill their slice; going over changes nothing. Tap the big number to show the step's time first. Swipe it sideways, or ✕, to close it.
  - Pause from the clock or the floating window (which shows the same ring, small). Paused time isn't counted. The clock's main button logs the step or finishes, like the pinned button.
  - Undo for a few seconds after each Log; tap a finished step's time to fix it (hold and slide).
  - The screen stays on while a session runs. Leave for more than 10 minutes and it asks whether to take the time out. Close the app and the session carries on when you come back.
  - Song practice's clock starts when you record your first take; until then the timer says **Not started**.
  - Sessions over 90 minutes ask how long you actually practised.
- **Floating window:** leave a session, or switch away while something plays, and a small window stays on every other screen.
  - **One sound at a time:** a take, a recording, the coach video, a song's track and play-along all go through one place, so starting any of them stops whatever was playing. The lock screen's buttons follow whichever started last.
  - **Recording over the track (3.37):** the one exception. Tap Record while a song's track plays and the app asks first: **Record with headphones** or **Record through the speaker** (the track may be heard in the take). The track keeps playing through the take and after it. Headphones are remembered while the track keeps playing; the speaker asks every time.
  - Every sound's window has a **✕**, playing or paused. It stops the sound and closes the window, and nothing brings it back except playing it again: not switching tabs, a sheet, coming back to the app or a reload. Nothing else pops up in its place on that screen. When a sound finishes, its window goes.
  - A sound's window shows while it plays, and when you paused it from the window (or the lock screen). Paused anywhere else, it doesn't follow you.
  - Every window shows what it is on top (a session's step after a dot in its colour, a take's section, the song's name) and its time below, with a thin progress line along its bottom edge where there is one (3.44). The play/pause button shows whether it's playing; paused, the time greys and stops.
  - A take goes when it ends. Pause a song's track on the player itself and it doesn't follow you out.
  - **Tuck it away (3.44):** drag or throw any window off the left or right edge. It leaves a small tab with an arrow, and a blue dot while something plays; sound and timers carry on. Tap the tab or pull it out to bring it back.
  - In a bottom corner, every page leaves room at its end so the last line scrolls clear of it.
  - If more than one is going, a take wins, then the coach video, the track, play-along and a session, in that order.
  - Tap it to go back to exactly where you were: the same step at the same scroll, or the song with that section's takes open.
  - Drag it to any corner and it snaps there. It remembers the corner on this device.
  - It hides on its own screen, while a sheet is open and while you're recording.
  - Closing a section's takes sheet lets a playing take carry on, so you can listen while you look at the lyrics.
- **Session saved (3.41):** finishing a session lands on a calm screen that belongs to Today: this week's arch, with only today's minutes drawing in, then "41 min · Sunday · weekly goal reached" (the last part once the goal is reached), the week's circles with today's turning green, and "N-week streak continues" when there's a streak. Nothing counts up. **Done** turns it into Today: the arch, the circles and the streak line move into their places, Done becomes **Start session**, and the rest of Today rises in. With Reduce Motion it fades. The session's details are on its sheet, from the calendar or All sessions.
- **Song ladder (3.52):** Application's song card has a **Straight / Ladder** switch, remembered for each song. A ladder sings the section four ways, one take each: **Lip trill**, **Hum**, **Vowels only** and **Words**. Each rung has its own instruction and its own view of the words (faded for the trill and hum, the vowel letters picked out for Vowels only), and any rung can be skipped. While a rung records, its pitch line draws live. The rungs you've sung fold into one row ("2 of 4 sung · Trill · Hum") that opens when tapped; only the rung you're on stays open, and the rest are one "Up next" line.
  - **Lines** (from two rungs): the rungs' pitch lines on top of each other, each switched on or off, lined up at their first note. It names where the words (or vowels) part from the trill (or hum), by line when the song is timed, otherwise by time, with **Hear both**: the trill there, then the words. If they don't part, it says so.
  - **Notes of the line** (once all four are sung): one button per note held in your trill, labelled by note. Tap one to hear it in the pattern player's sound; with **Repeat** on it keeps playing until you tap it again.
  - Ladder takes are ordinary takes of the section ("Ladder · Lip trill" and so on), with Star, Compare, notes and backups as before. Pitch lines are worked out on the phone when needed and never saved. There's no score anywhere: lines, not grades.
  - **Song key (3.54):** under the lines, the app works out the song's key from all its takes. When two keys fit about as well, it asks ("Which key is this song in? F major · D minor · Other…"); otherwise it suggests one ("This sounds like F major", with Use). You choose once for each song, and can change it from Lines or the **Key** row on the song's page (Major or Minor, and 12 notes spelled for the key). The key is saved with the song and its backups.
  - **Scale lanes:** once a song has a key, its notes show as faint lanes behind the pitch lines, on Lines and while you record, with the home note in blue and each note spelled for the key (B♭4 in F major, not A♯4). A **Scale lanes** chip turns them off on this device. They only show where the notes are; nothing is marked right or wrong.
  - **Practise in the key:** the note to work on (where the words part from the trill, or else the line's top note), as in "sits on A4, the 3rd of F major", then up to three patterns from the pattern player's library that play in the song's key and reach that note, each with its range, what it trains and Play. Tap one to open the pattern player on that note, staying on the key; your exercises' own choices aren't changed. The note buttons match the key too.
- **How did it go?** After song practice, tap words that fit (or add your own) and an optional note. You can skip it. A focused session no longer asks (3.40); you can still add words on its edit sheet.
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

Lists push their pages in from the right, as on iPhone: a song from Songs, Today's pinned songs, Show all songs, Search's songs, lyrics and exercises, the Exercises list, Check timing and the track player's Retime from a song, and Settings' rows and Changelog. The page underneath slides a little to the left and dims. Other cards that open a page zoom into it: the suggested rotation, Song practice and the track on a song's page, the coach video, Show all sessions, the weekly goal arc, and the Start session button, which expands into the session. Back reverses either, with the list where you left it, and finishing song practice shrinks it back into its card (a focused session lands on Session saved instead). You can swipe back from anywhere on a page with a Back button, not just the edge: the page follows your finger and goes back past about a fifth of the screen or with a quick flick, otherwise it settles back. Scrolled down, the top bar becomes a soft blur that fades out under the status bar. A row's own swipe (pin or delete), sliders and charts you slide across always come first. Tapping a day in the practice calendar grows its sessions out of the day, and a new song's paste sheet shrinks into its row before the song opens.

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
- **Chapters:** a video the length of the coach video (79:33) gets its 12 exercises, starting at times measured frame by frame from the video itself (3.43, `COACH_TIMES` in `js/content.js`). Give an exercise three times there (Level 1, 2 and 3) and it gets the L1 · L2 · L3 picker too. Any other video plays as a plain video, without the exercise list.
- **Where it plays:** the player (Exercises › Coach video), Play with coach on an exercise's page, and the floating window during a session's Foundation and Rotation (Application has a Coach ▸ pill). Leaving while it plays keeps it going in a small window.
- **Picture in picture (3.44):** the small window is just the video. Tap it for its controls (✕, open the player, −10 · play · +10 and L1 L2 L3), which fade after about 3 seconds. Pinch or double-tap for small, medium or the full width; the last size is kept on this device.
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

Vanilla HTML, CSS and JavaScript, with no frameworks or build step: `index.html`, one stylesheet in `css/` and a dozen plain scripts in `js/`. It uses the iOS system font and a CSS imitation of Liquid Glass, tuned to numbers measured on iOS 27: a hairline edge with rim light, glass buttons that grow when pressed, a collapsing tab bar, a soft blurred edge under the top bar, sliding glass pickers and springy motion.

It uses four libraries, each kept as a fixed copy so the app needs nothing from the internet: [pdf.js](https://github.com/mozilla/pdf.js) 4.10.38 for opening sheet music prints (`js/vendor/pdfjs-4.10.38/`, loaded only when a print is added), [pitchy](https://github.com/ianprime0509/pitchy) 4.1.0 (with [fft.js](https://github.com/indutny/fft.js)) for reading pitch (`js/pitchy.js`), and, for a song's key, [musictheoryjs](https://github.com/Zachacious/MusicTheoryJS) 3.2.2's key finder (`js/musictheory.js`) and [tonal](https://github.com/tonaljs/tonal) 6.5.1's scales and note names (`js/tonal.js`).

The look and motion follow Apple's guidance, with numbers taken (never code) from a few open-source Liquid Glass projects. What came from where is in [DESIGN_REFERENCES.md](DESIGN_REFERENCES.md).

---

## Development

See [MAINTAINING.md](MAINTAINING.md) for how the app is built, where data lives, the rules that keep old backups working, and how to release.

- `python tests/run.py` runs the full test suite in Chromium, several files side by side: every screen at every size, a full practice session, songs, backups (including real ones from earlier versions), recording, and thousands of random taps. GitHub runs it after every push. `python tests/run.py quick` skips the slow layout and random-tap checks while building.
- `python tools/release.py 3.7` sets a new version number everywhere at once.
- Every screen has a permanent ID (`VS-001` onwards), listed with its named parts and the main journeys in `js/register.js` (see [MAINTAINING.md](MAINTAINING.md#screen-ids)).
- `python3 tools/atlas/atlas.py` scans the app with sample data and shows every screen as saved screenshots, with a map, notes Claude can read and what changed since the last scan (the Visual App Atlas, on the Atlas kit; see [MAINTAINING.md](MAINTAINING.md#visual-app-atlas-q30)).

---

## License

MIT

`js/vendor/pdfjs-4.10.38/` is pdf.js 4.10.38 (Copyright Mozilla Foundation), under the Apache License 2.0, unchanged, with its `LICENSE` in the same folder. `js/pitchy.js` is pitchy 4.1.0 (Copyright 2018-2021 Ian Johnson) with fft.js 4.0.4 (Copyright Fedor Indutny, 2017), both under the MIT License; their notices are at the top of the file. `js/musictheory.js` is part of musictheoryjs 3.2.2 (Copyright 2020-2026 Zach Moore, ISC License) and `js/tonal.js` is part of tonal 6.5.1 (Copyright 2015 danigb, MIT License); each notice is at the top of its file. The piano notes in `audio/piano/` are from [piano-sound-samples](https://github.com/Leethring/piano-sound-samples) (Copyright 2020 Liam Lee, made with MuseScore), under the MIT License, trimmed and levelled; the licence is in the same folder.

---

*Built by [ivanc.digital](https://ivanc.digital)*
