# Changelog

All notable changes to Vocal Sessions. The app's **Changelog** page (Settings › Changelog) is built from this file, so every entry here appears there.

Version numbers follow **major.minor.patch**:
- **Major:** a redesign
- **Minor:** new features
- **Patch:** small fixes

---

## 3.25 · 26 Oct 2026
*Bigger rehearsal controls on the track player (Q09)*

<!-- area: songs -->
**Markers**
- Three big pads replace the round buttons: **Replay**, **Play/Pause** (the widest) and **Next**, with two pills above them: **Backing Sound** and **Loop**.
- **Backing Sound** off keeps the track playing silently: the playhead, the loop and Next carry on, so you can sing the marker on your own. It's on whenever you open the player, and only Markers is silenced.
- **Loop** turns the loop on or off. With no loop yet, it loops the marker you're in.
- **Replay** starts the marker you're in again. **Next** goes to the next marker in time order and scrolls its tile into view.
- Tiles are taller (108 pt), and each tile's loop button is bigger and sits at the bottom right, where your thumb lands.

**Looping**
- The jump back at the end of a loop happens right at the end, so the pause there is shorter, at every speed. The pitch stays the same at 0.75× and 0.5×.

<!-- area: look -->
**The player**
- The left and right jog wheels grow while you hold them, staying where they are on the edge (they no longer slide in).
- In Song, the rows sit in a card, with the **Lyrics** pill at its top right.
- The lyric card above the waveform moves the new line into place with a soft pulse when it changes (a fade with Reduce Motion).

## 3.24 · 26 Oct 2026
*Waveform sections on the track player (Q02)*

<!-- area: songs -->
**Section starts on the waveform**
- Hold a marker and choose **Make this a section start…**, then pick the section. The marker becomes that section's start in Song Clock, so there's one timing for the song, and the toast's **Undo** puts back both the timing and the marker.
- Starts stay in time order: a section that would start before an earlier one (or after a later one) is greyed in the picker, with the reason.
- On a song that's already timed, that section moves to the marker and the other starts stay where they are. On one that isn't, its lines are spread from there, as Sync by sections does.
- Section starts show on the waveform as blue lines with their names. Scrubbing the waveform takes the place of the Timeline that was planned for Song Clock.

**Four views**
- **Phrase** (6 s) and **Line** (16 s): a taller strip, with a card above it showing the line before, the line at the playhead (with its section) and the next.
- **Song**: the whole song in rows of 24 s. The last row ends at the track's end (a 3:14 track ends with a 3:12–3:14 row). The lyrics sit under each row; tap one to go to it, or hide them with the **Lyrics** pill.
- **Markers**: a big tile for each marker. Tap one to play it and loop it to its own end, or to the next marker (the last one runs to the track's end). Markers under half a second apart don't loop. Each tile has its own loop button, the one you picked is outlined and the one playing is tinted, and the last tile adds a marker at the playhead. Its transport is Replay, Play/Pause and Next.
- The view you used before this update is reset to Line, once.

**Play along with the track**
- When the song's track is on this device, play-along plays it and the lyrics follow the track's time. It's on to start with, and the new button beside −0.2 and +0.2 mutes it. Without the track, play-along works as before, lyrics only.
- Pausing play-along pauses the track, and pausing the track (from the lock screen, say) pauses play-along.

<!-- area: look -->
**The player**
- The jog wheel can sit on the left, on the right, or as a full-width roller under the strip (the player's ⋯ menu). The edge wheels slide further in under your finger.
- The playhead is red, in light and dark.
- With the screen locked, the loop is kept as well as iOS allows, and waking puts a playhead that drifted out of the loop back at its start.

## 3.23 · 26 Oct 2026
*Bars, pages and Today that feel like iOS 27 (Q08)*
<!-- area: look -->

**The bars where Apple's are**
- On iPhone, the tab bar now sits low, 21 points from the bottom edge in the home indicator's area, with 21-point margins either side, as in Music and Notes. The four tabs share the bar's width, and the search circle beside it is as tall as the bar.
- The buttons at the top (the gear, Back and the step pill) sit 6 points higher, where Apple's do.
- Everything that rests on the tab bar moved down with it: the floating window, a session's button, Song Clock's and the track player's controls, and Recall's capsule. iPad, Mac and landscape are unchanged.

**A soft edge when you scroll**
- Scrolling a page no longer turns the top bar into a rounded card. Instead, a full-width blur starts behind the status bar and fades away at its lower edge, with no line, and the page scrolls softly under it. The buttons stay glass and the title sits in the middle.

**Today's gradient**
- A soft wash of coral, blue and orange now sits behind Today's date and title, fading out about a third of the way down. Three blobs of colour drift very slowly over a faint grain, and it scrolls away with the page. The cards and Start session are exactly as they were.
- With Reduce motion on it holds still.
- **Settings › Appearance** is new, with one switch: **Gradient background**, on unless you switch it off. It's for this device only and isn't in backups.

**Pages that push in, as on iPhone**
- Songs, Today's pinned songs, Show all songs, Search's songs, lyrics and exercises, the Exercises list, Sync by sections and Check timing from a song, and Settings' rows and Changelog now push their page in from the right. The page underneath slides a little to the left and dims, on the same spring as the zooms.
- Back and swipe back reverse it: the page follows your finger and the one underneath slides back. Let go past about a fifth of the screen, or with a flick, and it finishes at your finger's speed; otherwise it settles back. You can turn it round halfway, either way.
- Everything else that opened with a zoom still does: Song practice, the track, the coach video, Start session, the weekly goal, Show all sessions and the suggested rotation.
- With Reduce motion on, pushes become a short fade.

**The tab bar's collapse**
- Scrolling down a long page now shrinks the tab bar to a small pill at the left, holding the tab you're on, with the search circle staying at the right, the same height. Scrolling up, or tapping the pill, brings it back.
- It moves smoothly now: the bar fades and slides away towards the left while the pill grows in, with no wobble, no jumping icon and nothing else on screen moving.
- It waits for about 30 points of steady scrolling down and comes back after about 20 points up, so a small nudge or the bounce at either end of a page doesn't make it flicker. Scrolls the app makes itself (like going back to where a list was) don't count.
- It only happens on pages with real room to scroll, never in the first 120 points, and never on Search, while you're typing or with a sheet open. Every new page starts with the full bar.

## 3.22 · 26 Oct 2026
*Search, from every tab (Q01)*

<!-- area: look -->
**The search circle**
- A search circle now sits beside the tab bar on every tab, like the iPhone's own apps. It stays beside the tab bar when that shrinks as you scroll, and it's tinted while Search is open.
- On iPad it's a circle at the end of the tab capsule at the top; on a Mac-sized window it's a Search row at the top of the sidebar. Cmd/Ctrl+F opens it from a keyboard.
- The floating window keeps clear of it, in every corner.

<!-- area: songs -->
**The search page**
- Before you type: your recent searches and your pinned songs. Recent searches stay on this device and aren't in backups.
- As you type, results appear straight away, grouped: Songs, Lyrics, Exercises, Sessions and Takes. Each group shows its top three, with "Show all" to see the rest in place.
- Lyrics show the matching line, highlighted, with the song and section under it. Exercises match their names and their write-ups, and say which part matched. Sessions match their notes and feedback words. Takes match the names you've given them and your comments.
- The matching is as forgiving as the Songs list's: capitals, punctuation, accents, word order and a slipped letter in longer words don't matter.
- A song or an exercise zooms open from its result, and Back shrinks it into the same result, with your search still there. A lyric opens its song in Practise, scrolled to that section with it focused. A session opens its details.
- A take opens its song with the takes sheet on All takes and that take expanded. A comment does the same, with the playhead at its time and the comment showing.
- Cancel clears the search and puts the keyboard away.

**The Songs list**
- Songs keeps its own search for filtering the list, now a field under the title on iPhone (the circle beside the tab bar is Search).

## 3.21.1 · 24 Oct 2026
*Exercise pages that read like Apple Health*
<!-- area: look -->

- Exercise pages now have bold, sentence-case titles in place of the small grey labels: "About vocal slides", "Why it helps", "In a song" and "Last done". Other pages keep their labels.
- The About and Why it helps text for all 12 exercises is rewritten in a calm, factual tone: what the exercise is first, then how it's done, then what it does for your voice, ending with one practical tip on what to adjust. Every detail from before is kept.
- Half squeaky now says "squeaky hinge", matching the exercise's name.

---

## 3.21 · 24 Oct 2026
*Settings, like the iPhone's: a row for each, a page for each*
<!-- area: look -->

**The Settings list**
- Settings is now a list of rows, each with its own icon, like the iPhone's Settings app: Backup, Storage, Recall, Coach video, Accessibility, Changelog and View on GitHub. Tap a row to open its page; it zooms open from the row, and Back (or a swipe from anywhere) shrinks it back.
- Each row shows where things stand on the right: when you last backed up (red after two weeks, or if you never have), the space used, the peek length, whether the coach video is added, and the Reduce motion setting.
- The two resets stay at the bottom of the list, in red, and still ask first.
- At the very bottom: the app's icon, name, version and release date. Tap it for the Changelog.

**Backup and Storage pages**
- Both open with a card explaining what the page is for, with a big icon.
- Backup has Export, Import, Check a backup and Undo last restore, when you last backed up, and Backup history, Where backups go and Save a read-me file. Undoing a restore brings you back here.
- Storage shows one bar split by what's using the space (recordings, song tracks, the coach video, and sessions and songs), then the same rows as before: Recordings, Review old takes, Song tracks, Coach video and Storage protection.

**Accessibility**
- New page. **Reduce motion:** Match iPhone (the default), On or Off. On swaps zooms and slides for short fades even if your iPhone's Reduce Motion is off; Off keeps the motion even if it's on.
- **Slow motion** plays every animation four times slower, to check how it feels.
- Both are kept on this device only and are never in backups.

## 3.20.1 · 23 Oct 2026
*Song Clock: pausing keeps your line in place*
<!-- area: fixes -->

- Fixed: pausing play-along near the end of a short song could move the line you were on down the screen. The song page now has room below the lyrics while paused, so the line stays where your eye was.

## 3.20 · 23 Oct 2026
*Songs, takes and markers: one place for every take, and a ✕ that always closes*
<!-- area: songs -->

**Adding a song**
- The Songs list has one +. It opens with a switch: **Add media** (the default) or **Manually**. This replaces New song and New song from track.
- Add media: choose the song's audio from Files. Once it's read, the form opens with its length filled in and linked to the track. The title and artist start empty, since a file's details often aren't right; leave the title blank and the file's name is used. Lyrics are optional.
- Manually is the same form as before, now with a Length.
- Save opens the song. Nothing is kept if you cancel or choose a different file.

**The song list**
- Every song has a play button that plays its track, here and in Today's pinned songs. Without a track on this phone it's greyed, and says "Upload a track to play".
- Each song shows when you last practised it and how many takes it has, recent first, with nothing to grade.
- Today's Song practice card now opens the Songs tab. Recording a take on any song's page starts (or carries on) song practice for that song, timed from the first take. Your past song practice is all still there.

**Takes**
- **Takes** beside the song's title opens every take. From a section, a switch moves between that section's takes and All takes.
- Tap a take to play it and open it out: a waveform you drag to scrub, back and forward 5 seconds, and its name, which you can tap to change.
- Comments at a moment in the take: the time is set the moment you start typing (tap it to nudge it). While the take plays, each comment pops up as it's reached, and dots under the waveform jump to them.
- Swipe right to star a take, left to delete it (it always asks), or hold it for Star, Rename and Delete.
- Every take is kept now, not just the last three. Settings › Storage shows how many there are and has Review old takes, to clear unstarred takes with no comments by hand.
- Names and comments are always in backups, even with Exclude recordings, and the backup sheet shows the size with and without recordings.

**The track player**
- Markers: Marker drops one at the playhead, playing or not. They show in purple on the waveform and as numbered chips under it: tap one to jump there. Give one an end with End here, and it gets its own loop button. Drag the orange handles to fine-tune it.
- Hold a chip to rename, move, change its end or delete it, or clear them all.
- Tapping in Section and Song views moves the playhead and keeps the view. The level buttons (or a pinch) change the zoom.

**Song length**
- With a track, the song's length follows it, shown with a link. Changing it asks "Unlink from track?" first. A length of your own shows a broken link and the track's length beside it; tap it to relink.

**Playing**
- One sound at a time: a take, a recording, the coach video, a song's track or play-along. Starting one stops the others, and the lock screen follows the one playing.
- The floating window's ✕ is on every sound, playing or paused. It stops it and closes the window for good, until you play it again. Nothing else pops up in its place.
- Fixed: takes and tracks play again from the start after they finish.
- Fixed: takes play in both ears with earphones. New takes are recorded as one channel, and older takes with the voice on one side play from a copy made for both ears. Your recordings themselves are never changed.

## 3.19.1 · 23 Oct 2026
*Track player: MP3s can be picked in Files*
<!-- area: fixes -->

- Fixed: on iPhone, audio files were greyed out in Files when adding a track. The picker now names MP3, M4A, WAV, AAC and AIFF files one by one, so they can be chosen.

## 3.19 · 23 Oct 2026
*Track player: loop a phrase of the real song, slowly*
<!-- area: songs -->

**A song's track**
- New: add a song's audio from Files, from the Track row in the song's Practice group, the Add track tile in Song controls, or New song from track on the Songs list (it makes the song, titled from the file name, and you can paste the lyrics later).
- MP3, M4A and WAV all work. Songs from Apple Music can't be added, and a file that won't open says so.
- The track stays on this phone and isn't included in backups, so they stay small. A restored song keeps its loop and timings and says "Track not on this device", with Add track to put the same file back.
- The waveform is read once, when you add the track, so the player opens straight away after that.

**The player**
- Four zoom levels: Phrase and Line are a strip that moves under a fixed playhead; Section and Song show the whole song in rows. Tap a level or pinch, and tap a row to zoom into Line view there.
- The jog wheel on the right: drag slowly for precision, quickly to skim.
- Set start and Set end at the playhead, or drag the orange handles. Audio outside the loop is dimmed, and a double-tap outside it clears it.
- Speed 0.5×, 0.75× or 1×, with the pitch kept, so it stays in key when slowed.
- The loop is saved with the song. The zoom level and speed are remembered on this phone.
- Leave while it plays and a small window says "Playing · song title". Only one thing plays at a time: the track, a take, the coach video or play-along.

## 3.18 · 22 Oct 2026
*Song Clock: sync a song and sing along*
<!-- area: songs -->

**Timing a song**
- New: Sync. Play the song on another device or in your music app, and tap the big pad as each section starts. Your first tap starts the clock, and every tap allows a little for your finger.
- While you sync you see the clock, which section you're on, what you just marked and what's next. Undo takes back the last tap, and tapping a section you've done redoes from there.
- Pause works on one phone: scrub the song back a little, then tap as the section starts, and the clock carries on from there.
- After the last tap, each section's lines are spread evenly by their syllables, so the whole song moves straight away.

**Playing along**
- Turn on Timing and tap the first line as it's sung. The lyrics turn big, the line you're singing sits about a third of the way down, and its words fill as they're sung.
- Lines you've sung dim, and the ones coming up blur a little more the further away they are (Blur ahead).
- Tap any line to jump there. −0.2 and +0.2 move all the lyrics earlier or later, saved, with Undo.
- Pause shows the normal lyrics page with the line you were on highlighted, right where your eye was. Tapping a section still focuses it.
- The screen stays awake while you're timing (Stay awake).
- Leave the song while it plays and a small window says "Playing along" with the time and section. Its button pauses, and tapping it takes you back in step.

**Marks while playing**
- Breaths only (the default): your own breath marks show, and lines with a long gap after them and no breath mark of yours get a small breath dot. Everything else (sing-as labels, runs, higher and lower, notes) is hidden while you sing.
- Off hides breath marks and dots too.

**Check timing**
- A list of every section and line with a bar for how long it lasts. Very short and very long lines are flagged, and so are lines to look at again.
- It shows the song length and how many section starts are set, and Sync again from the start.

**The song's header**
- The artist line now shows the song's length ("Artist · 3:58"). Tap it to change it on clock-style wheels.
- Beside it are up to three pinned buttons (Timing and Key to start with) and ⋯, which opens Song controls: Timing, Check timing, Key, Marks while playing, Blur ahead, Snapping, Stay awake, Sync again and Lyrics. Blue means on. Edit chooses which ones are pinned.
- The pencil now edits the title, artist and length in place, with Edit lyrics, Marks and Done.
- Changing a line of lyrics only clears that line's timing, and marks it to look at again.
- Timing is saved with the song and included in backups. Settings like Blur ahead stay on this device.

## 3.17 · 22 Oct 2026
*Tab order, new icons and tidier lyrics*
<!-- area: look -->

**Tabs**
- The tabs are now in the order Today, Progress, Songs, Exercises: in the tab bar, the iPad's top capsule and the Mac's sidebar. Cmd/Ctrl + 3 opens Songs and Cmd/Ctrl + 4 opens Exercises.
- New icons: Progress is a ring about three quarters full, like Today's goal arch, and Exercises is a small deck of cards.

**Today's title**
- "Today" now sits at exactly the same height as the titles on Progress, Songs and Exercises, so the header no longer jumps when you switch tabs. On iPad and Mac the Songs title lines up too.
- The date sits just above the title, tight to its letters, and still opens the practice calendar.
- The chevron beside "Today" is centred on its letters.

**Sing-as labels**
- A word with a sing-as label now makes room for it, like chords over lyrics: the label sits above its word and the gap after the word grows, so labels never overlap each other, the lyrics or the line above.
- Only lines with a label get taller. The note marker always sits beside its word.
- Recall still hides the labels in place, and Perform still leaves them out.

**Fixes**
- Closing the coach video's small window with ✕ now always hides it. On iPhone it could stay on screen on every page, showing a black box, the exercise name and Play. Only playing the video again brings it back.

## 3.16.1 · 21 Oct 2026
*Coach video chapters from YouTube*
<!-- area: fixes -->

**Fixes**
- Each exercise in the coach video now starts at its YouTube timestamp (Humming at 7:15, Falsetto voice at 19:30, and so on). The times read from the video's slides were a few seconds late, and the level times were off.
- YouTube only marks where each exercise starts, so tapping an exercise plays it from the top, and Loop repeats the whole exercise. The L1 · L2 · L3 picker is gone for now.
- The times live in one list in the app's content file. If you add level times there later (three per exercise), the level picker comes back for those exercises.

## 3.16 · 21 Oct 2026
*Coach video in the app*
<!-- area: practice -->

**Adding it**
- Settings › Coach video › **Add coach video…** picks the video from Files. It stays on this iPhone: it's never put online and isn't in your backups, so keep the file in Files to add it again (after re-adding the app, for example).
- Once added, Settings shows its name, its 12 exercises and 36 levels, and its size, with **Replace video…** and **Remove video**. Reset all data leaves it alone; only Remove removes it.

**The player**
- Exercises › **Coach video** opens it. The row says where you paused, so it doubles as Resume.
- The bar under the video covers only the exercise you're on, as its three levels, so dragging is precise.
- **L1 · L2 · L3** jumps to the start of that level. **Loop** repeats the level you're on. **Speed** goes 0.75× · 1× · 1.25× without changing the pitch.
- Tap any exercise in the list to play it from your current level. The one playing shows small wave bars.
- Back and forward 10 seconds, full screen, and play and pause from the lock screen.

**Other ways in**
- Each exercise's page (1 to 12) has **Play with coach**, starting it at your current level.
- In a session, Foundation and Rotation have a **Coach video** row. It stays hidden until you tap it; then the video sits under the step's title for the rest of the session, playing that step's first exercise at your level. ‹ and › move to the step's other exercises. Next and Back cue the next step's exercise, paused. The session clock carries on separately.

**While you're elsewhere**
- Leave the player (or the session step) while the video plays and it carries on in a small window you can drag to any corner, with a play/pause button. Paused, a small ✕ closes it. Tap it to go back.
- A playing take still wins the window. Playing a take or starting a recording pauses the coach video, and playing the video stops a take.

## 3.15.1 · 19 Oct 2026
*Swipe back shadow*
<!-- area: look -->

**Fixes**
- After swiping back, the page's soft shadow now shrinks with it into its card. Before, it stayed the size of the screen while the page shrank.

## 3.15 · 19 Oct 2026
*Card zoom and swipe back*
<!-- area: look -->

**Opening and closing pages**
- Tapping a card that opens a page now zooms into it: exercises (in Exercises and Today's suggested rotation), songs (in Songs and Today's pinned songs), Show all sessions, Show all song practice, Show all songs, Changelog and the song page's Song practice.
- The page grows out of the card with its title starting where the card's name is, beginning in the card's colour so dark mode never shows an empty dark box.
- Back shrinks the page back into the card it came from, and the list is where you left it, not back at the top.
- If the card has scrolled out of sight, the page just fades and shrinks a little.
- Tapping Back in the middle of a zoom turns it round from wherever it is. Nothing ever waits for a zoom to finish before you can tap.

**Swipe back**
- On any page with a Back button, swipe right from anywhere (not just the edge). The page follows your finger and shrinks a little, with the screen you came from underneath.
- Let go past about a fifth of the screen, or flick, and it goes back into its card. Let go before that and it settles back.
- Whatever your finger lands on comes first: swiping a row to pin or delete it, the level buttons, charts you slide across, sliders and anything that scrolls sideways never start a swipe back.
- On Rotation and Application it goes back a step, like Back.

**Sessions**
- Start session (and Resume session) expands from the button into the session. Song practice expands from its card, on Today or on a song.
- Back from Foundation shrinks the session back into Resume session.
- Finishing shrinks the session back into Start session on Today, behind the summary. Song practice shrinks back into its card.

**Also**
- The weekly goal arc zooms into Progress.
- Tapping a day in the practice calendar grows that day's sessions out of the day.
- Saving a new song shrinks the paste sheet into the song's new row in Songs, then the row opens the song.
- With Reduce Motion on, zooms become a short fade, and a swipe back moves the page sideways without shrinking it.

## 3.14 · 19 Oct 2026
*Motion details*
<!-- area: look -->

**Lists**
- Deleting a session, song practice, exercise or song: the row shrinks away and the rows below slide up to close the gap.
- A new exercise slides into its place in the list.
- Pinning a song makes it travel up into Pinned (and back down when you unpin it). Songs you pin elsewhere slide into Today's pinned list.
- Changing how songs are sorted slides each song to its new place, one after another.
- In All sessions, switching between Sessions and Song practice brings the new rows in one after another.

**Progress**
- Changing the range (D, W, M…) makes the bars ripple to their new heights, left to right.
- The arrows send the ripple the way time goes: earlier runs right to left, later left to right. The total slides the same way, without rolling digits.
- The breakdown bars grow from the left, one row after another.
- Tapping or sliding across the bars still follows your finger instantly.

**Today**
- Once the app has opened, the weekly goal arc fills to this week's minutes and the Monday to Sunday circles ripple in.
- After finishing a session, today's circle pops in once you close the summary.
- After you back up, the backup reminder shrinks away and the page closes the gap.
- The practice calendar's days ripple in when it opens and when you change month.

**Recall**
- Stepping down a hint level hides the lyrics word by word, in reading order. Stepping back up shows them again from the end backwards.
- A line you peek at settles in with a small spring.

**Sessions and songs**
- Next brings the next step in from the right, and Back brings the earlier one in from the left.
- Switching between Practise, Recall and Perform brings the bottom buttons in with a spring. Changing the hint level leaves them still.
- A new take slides in at the top of the takes sheet, and starring a take gives the star a small pop.
- An exercise's level chart draws from left to right, ending on the latest level.

**Backup**
- "Preparing backup" turns into "Backup ready" in the same sheet, which grows to fit instead of rising again.
- After backing up, the red "Last backed up" line fades to its normal colour.

**Reduce Motion**
- With Reduce Motion on (Settings › Accessibility › Motion), nothing slides, pops or ripples. Changes now fade in and out over about a fifth of a second instead of snapping. Before this, every animation was simply switched off.

## 3.13 · 17 Oct 2026
*The launch ripple*
<!-- area: look -->

**Opening the app**
- When the app opens fresh, the sound-wave bars on the icon pulse one after another, like a ripple.
- The launch screen then fades away with a slight zoom, and Today's blocks rise in from top to bottom.
- It only plays when the app opens fresh, or reloads after an update. Switching tabs or coming back to the app doesn't replay it.
- After importing a backup, the ripple plays again on Today, then "Backup restored" shows.
- The first moment looks the same as before: the plain background with the icon, with no white flash or jump.
- If a session is running, its floating window appears once Today has risen in.
- With Reduce Motion on (Settings › Accessibility › Motion), nothing pulses or rises: the launch screen just fades.

## 3.12 · 17 Oct 2026
*A floating window for sessions and takes*
<!-- area: practice -->

**Floating window**
- Leave a session and a small window stays on every other screen, showing what's running (like "Focused session · Rotation") and its time.
- Its button pauses the session without leaving the page. While paused, it says Paused and the time stops.
- Tap it to go straight back to the same step, scrolled to where you were.
- Song practice gets the window once its first take starts, since that's when its clock starts.
- Today's Resume button and the In progress row still work as before.

<!-- area: recordings -->
**Takes**
- Switch away while a take is playing and the window shows the take instead: "Playing · Chorus 2" (or the song's name for song practice), its time and progress, and a pause button.
- Tap it to go back to the song with that section's takes open, or to song practice.
- If a session and a take are both going, the take is shown. The window goes when the take ends.
- Closing a section's takes now lets the take carry on playing, with the window there to pause it.

<!-- area: look -->
**Moving it**
- Drag it to any corner and it springs there, like picture in picture on iPhone. A quick flick sends it to the corner you throw it towards.
- It remembers its corner on this device, starting in the bottom right above the tab bar.
- It stays out of the way: hidden on its own screen, while a sheet is open and while recording, and clear of the tab bar, Recall's hint capsule and the sidebar on iPad and Mac.

## 3.11 · 17 Oct 2026
*Lyrics as one page, and the app's own springs*
<!-- area: songs -->

**The lyrics page**
- A song is now one continuous page. The boxes around each section are gone: small grey labels and a little space separate them, and the lyrics are a comfortable reading size.
- Tap a section to focus it. A soft patch appears behind just that section, with **Record**, its takes and **Marks**.
- While a section is focused, the rest of the song dims and softly blurs, more the further away it is. Far lyrics stay recognisable, and the section labels never blur, so it's easy to pick where to go next.
- Tap the same section again, or anywhere away from the lyrics, and it melts back into the page.
- **Marks** opens Annotate at that section.
- In Recall, tapping a line still peeks at it; tap a section's label to focus it.
- With Reduce Motion on in your iPhone's settings, other sections only dim, with no blur and no easing.
- The lyrics editor keeps its boxes, since they help while typing.

<!-- area: look -->
**Motion**
- The app now has one shared set of springs, so movement can feel the same everywhere: a gentle one for most things, a slightly quicker one for moving between pages, and a livelier one for small pops. The lyrics focus is the first thing to use them, and more will follow.

## 3.10.2 · 16 Oct 2026
*Recall stays put*
<!-- area: songs -->

- Changing the hint level in Recall no longer shows a tip line above the lyrics, so the sections stay exactly where they are.

## 3.10.1 · 16 Oct 2026
*Steadier sheets, honest timing, softer Recall*
<!-- area: fixes -->

**Sheets**
- Scrolling a sheet no longer scrolls the page behind it. When a sheet reaches its top or bottom, or the swipe is on the dimmed page around it, everything behind stays still. This applies to every sheet and to the session clock, with touch and with a mouse or trackpad.
- Tall sheets still scroll inside themselves, and dragging a sheet down by its top still closes it.

<!-- area: practice -->
**Song practice**
- Song practice is timed from your **first take**, not from when it opens. Choosing a song or warming up is never counted.
- Until then the timer says **Not started**, there's no clock or Pause, and the button at the bottom says **Record a take first**.
- Leaving before you've recorded anything drops it quietly, with nothing to resume or discard. Today only shows song practice as in progress once it's timed.
- This works the same from Today, a pinned song or the bottom of a song. Song practice already in progress carries on as before.

<!-- area: progress -->
**Weekly goal**
- Tap the weekly goal on Today to open Progress on this week's sessions.

<!-- area: songs -->
**Recall**
- Hidden letters are now soft rounded pills instead of thin lines. The letters keep their place, so nothing moves as you change level, and the pills fade in.
- Tapping a line shows only that line, and tapping it again while it shows starts its time again.
- **Hold a line** to keep it showing until you let go.
- **Settings › Recall › Peek length** sets how long a tapped line shows: 1, 2, 3 or 5 seconds (2 to start). It's included in backups.
- Screen readers no longer read hidden words aloud.

## 3.10 · 16 Oct 2026
*Songs: Recall, sing it from memory*
<!-- area: songs -->

**Recall**
- **Recall** is a new mode for a song, between Practise and Perform. It hides the lyrics a step at a time, so you can learn them by heart.
- Five levels: **Full lyrics**, **Word shapes** (each word's first letter), **First words** (the first word of each line), **Cues only** and **Blank**. Hidden letters become faint lines in place, so nothing on the page moves as you change level.
- Marks stay visible at every level, so breaths, runs and pitch marks still guide you.
- The hint capsule at the bottom steps between levels: the open eye shows more, the closed eye hides more, and tapping the level's name opens a menu of all five.
- Tap a hidden line to peek at it for a couple of seconds. Tap a section's heading to select it and record, as in Practise.
- The options button (•••) offers **From the start**, **From the end** (sections listed last first) and **Start anywhere**, which picks a section at random and points to it.
- Recall always starts at Full lyrics, from the start.

<!-- area: look -->
**Small screens**
- The Practise, Recall and Perform switch fits beside its buttons on the smallest iPhones.

## 3.9 · 16 Oct 2026
*Songs: record a section and hear it back*
<!-- area: recordings -->

**Record a section**
- In **Practise** or **Perform**, tap a section to select it. It gets a blue outline and two buttons: **Record**, and how many takes it has. Tap it again to let go.
- **Record** starts straight away. The page scrolls to the section, the top bar says what's recording (for example "Recording Chorus 2"), and a recording bar at the bottom shows the time, a level meter and Stop.
- While recording, the screen stays on that section: the Practise and Perform switch dims, other sections can't be tapped, and there's no back or edit until you stop.
- A take stops by itself after 2 minutes. Leaving the app or the song stops it and saves it, as song practice already does.
- Recordings are AAC mono at about 96 kbps where the phone offers it, with the phone's voice processing (echo and noise reduction, automatic volume) turned off, so the take sounds like your voice in the room.

**Hear it back**
- Stopping opens the section's takes over the song: the new take, big, with play, its progress, a star and a reminder that fresh ears help.
- Below it are every take you've starred for that section, and the latest and first while they're kept. **Record again** is at the bottom, and tapping a take adds notes, as in song practice.
- The same sheet opens from the section's takes button. A section that isn't selected shows how many takes it has in its heading.

**Where takes live**
- Each take belongs to one place in the song. Linked repeats share their lyrics, but Chorus 1 and Chorus 2 keep their own takes.
- Unlinking or moving a section keeps its takes with it.
- The keep rule is the same: the last 3 takes of a song, from any section, plus every take you star.
- Takes from before 3.9 belong to the whole song and still play in song practice, which now says which section each take came from.
- Recording a take counts as practising the song, so **Practised today** and the Recently practised order update straight away.

<!-- area: backup -->
**Backups**
- Backups still include recordings. **Exclude recordings** on Backup ready makes a smaller file without them.
- Check a backup and Import say **Recordings not included** for such a file. Restoring it keeps the recordings already on the device, and undoing that restore leaves them alone too.

## 3.8 · 15 Oct 2026
*Songs: lyrics you can mark up*
<!-- area: songs -->

**Songs**
- **Songs** is a new tab. Paste the lyrics of a song you're learning and they're split into labelled sections: verse, pre-chorus, chorus, bridge and the rest.
- Labels are found however the lyrics were written: `[Chorus]`, `Verse 2:`, `PRECHORUS`, `[Chorus: Sam]`. Blank lines split sections too, and a chorus that repeats itself is split in two.
- Website clutter is cleaned out of the paste: links, "You might also like", "Embed" and the "Lyrics" title line. Curly quotes become straight ones.
- Before saving, check the labels. Guesses are marked **Guessed**, and exact repeats are linked, so marks only need adding once. Tap the tick at the top to save.
- The lyrics you pasted are kept exactly as they were, alongside the sections.
- Titles and artists are capitalised for you.

**Marking up a song**
- Each section sits in its own card, one phrase per line, with repeats numbered (Chorus 1, Chorus 2). Long lines shrink to fit, and wrap only as a last resort.
- The pencil opens **Annotate**. Tap a word for Breath, Run, Higher, Lower, Sing as (the vowel to aim for) or a Note. Add an expressive cue to any section.
- A mark on a linked section shows on every repeat, and the same word lights up in each one.
- **Lyrics** edits the words. Marks follow their words as you edit. If a marked word changes, its mark is flagged to check; if it's removed, the mark waits at the top of the section to be moved or removed. The pencil shows how many need checking.
- Hold a section to drag it somewhere else in the song. **Undo** steps back through any change.
- **Unlink** gives one repeat its own copy, so it can change on its own.
- **Practise** shows every mark. **Perform** hides the technical ones and leaves the expressive cues. **Key** explains each mark.
- **Song practice** at the bottom of a song starts song practice with that song picked.

**Finding songs**
- Pin up to 3 songs. They sit at the top of Songs and on **Today**.
- The rest sort by Recently practised, Recently added or Title A–Z, chosen from the heading. Songs not practised yet say **New**.
- Swipe right to pin, left to delete. Press and hold for Pin, Rename and Delete. **Edit** selects several at once.
- **Search** sits at the bottom, beside the tab bar. It searches titles, artists and lyrics, ignores punctuation and accents, finds words in any order (even across lines) and forgives a slipped letter. Recent searches are kept.
- Songs from song practice are in Songs too. **Add lyrics** gives them lyrics and keeps their recordings.

<!-- area: look -->
**Settings moves to Today**
- **Settings** is now the gear at the top right of Today, and Songs takes its place in the tab bar.
- Songs are managed in Songs, so they're no longer listed in Exercises.
- On iPad and Mac, songs are listed on the left and the open song is on the right. New shortcuts: Cmd+F searches songs, Cmd+N adds one, Cmd+E edits, ↑ ↓ move between songs and Cmd+, opens Settings.

<!-- area: backup -->
**Kept safe**
- Backups include every song with its lyrics, marks and original paste.
- Each song is checked on its own when the app opens or a backup is read, so one damaged song can't affect the others. If a song's sections are damaged, they're rebuilt from the original paste.
- Songs you already had are upgraded in place: same name, same recordings, with a date added from their first song practice.

## 3.7.2 · 15 Oct 2026
*Your practice content in one place*
<!-- area: fixes -->

Nothing looks or works differently.
- Everything about your practice that you might want to change now lives in one file, `js/content.js`: goals, the coach video and its timings, the exercises and their write-ups, the quick words, and the Toggl tags. <!-- area: practice -->
- The file starts with a short guide to what's safe to change, and the one thing never to change: an exercise's id, which links it to your history.
- A new check runs with every update and after any edit to that file. It makes sure every exercise has a write-up, quick words and a video timing, and spells out exactly what's missing if not.

## 3.7.1 · 15 Oct 2026
*Tidier inside, the same on the outside*
<!-- area: fixes -->

Nothing looks or works differently. This release makes the app easier and safer to keep improving.
- The app's code is split from one very long file into a dozen readable ones: styles, settings, saved data, screens, the Changelog, backups, sessions and gestures.
- Updates now arrive all at once. The offline copy only switches to a new version after every part of it has downloaded, so a patchy connection mid-update can never leave a half-updated app.
- Every screen was compared before and after, and backups made before and after the change are identical.

## 3.7 · 15 Oct 2026
*Changelog, and data built to last*

<!-- area: look -->
**Changelog**
- **Changelog** in Settings shows every version of the app on a timeline, newest first, grouped into Version 3, 2 and 1.
- A growth chart shows every improvement since the first release, coloured by area. Tap a point to see that version, then jump to it.
- Each version shows its highlights, with **Show all** for the full list. Switch to **Every change** to open them all.
- It reads this changelog directly, so it's always up to date. It works offline too.
- Tapping the version number at the bottom of Settings opens it as well.

<!-- area: backup -->
**Data built to last**
- Your saved data now has a version number, so future updates can upgrade it one tested step at a time. Before any upgrade, the app keeps a copy of your data as it was.
- A backup made by a newer version of the app says so before you restore it, and suggests updating first.
- The app asks iOS to protect its data from being cleared when your iPhone runs low on space. **Storage protection** in Settings shows whether iOS agreed.
- Every update is now checked automatically before it goes live: every screen on every device, backups from earlier versions, and thousands of random taps. <!-- area: fixes -->

## 3.6 · 15 Oct 2026
*Organised, checked backups*
<!-- area: backup -->

**Organised backups**
- Backups are named by month and device, such as **Vocal Sessions backup · 2026-10 · iPhone.json**. Backing up again in the same month, Files asks to replace that month's file, so you keep one per month for each device.
- **Where backups go** in Settings shows how to make an **iCloud Drive › Vocal Sessions › Backups** folder. The first backup offers it too.
- **Backup history** in Settings lists every backup made on this device, with its size and what was in it.

**Checked backups**
- Each backup has a check code, a fingerprint of everything inside it.
- Before you save, the app reads the finished file back and checks it.
- **Check a backup** in Settings tells you whether a file is complete, what's inside and when it was made, without changing anything. It spots files that were cut short while copying, edited, or have damaged recordings.
- Backups from earlier versions still import. They're checked for readability, but have no check code.

**Safer restores**
- Import now shows the backup side by side with what's on this device.
- If anything here isn't in the backup, it tells you what would be removed and offers to back up first.
- **Undo last restore** in Settings puts everything back as it was, recordings included, for 30 days.

**Easy to recognise later**
- Each backup file starts with a short note in plain English: what it is, which device made it, what's inside and how to restore it.
- **Save a read-me file** in Settings saves a text file explaining the backups, to keep in the same folder.

## 3.5 · 15 Oct 2026
*History becomes Progress*

<!-- area: progress -->
**History is now Progress**
- **Recent:** your last 5 sessions, each with a small bar showing how its time split, and **Show all sessions**.
- **Practice time:**
  - A **D · W · M · 6M · Y · All** switch, like the Health app.
  - Your total for the period, with arrows to go back through earlier ones.
  - A stacked bar chart of Foundation, Rotation and Application. Tap or slide across the bars to see each hour, day, week or month.
  - A breakdown with time and percentage for each step.
- **Song practice:** this week's and this month's totals, your last 3 song practices, and **Show all song practice**.
- **All sessions** holds the full Sessions | Song practice list, with the same details, Copy for Toggl, edit and delete as before. On iPad and Mac it keeps its detail pane.

<!-- area: practice -->
**Time per step**
- Each session now saves the real time spent on Foundation, Rotation and Application, from the session clock.
- If a step took under 2 minutes, you probably filled it in at the end, for example while following the coach video in the car. These sessions show as a blended bar on the chart. Their time is still split using the coach video's length for each exercise, scaled by the levels you did, with Application as whatever's left.
- Sessions from before this version are split the same way.
- Session details show the time per step. Edit lets you switch between timed and filled in at the end, and set the minutes for each step.

<!-- area: look -->
**Colours**
- The chart uses indigo (Foundation), teal (Rotation) and amber (Application). They're checked for colour-blind separation and contrast in light and dark mode.

<!-- area: look -->
**More ways to the same place**
- Every summary leads to the same full lists and details. Song practice can be reached from Today, Progress, the calendar, and each song in Exercises.

<!-- area: backup -->
**Works offline**
- The app now keeps a copy of itself on your device, so it opens with no signal. When you're online it still loads fresh and picks up updates, including through pull to refresh.

## 3.4.1 · 14 Oct 2026
*A cleaner launch*
<!-- area: fixes -->

- The launch screen no longer flashes white before the icon appears. The right background colour is set on the very first frame, and the icon is built into the page so it appears at the same moment.
- The icon no longer jumps a few pixels as the app opens. It's centred on the full screen height, so it doesn't move when iOS adjusts the layout at launch, and it lines up exactly with the iOS launch image.

## 3.4 · 14 Oct 2026
*Launch screen*
<!-- area: look -->

**Launch screen**
- Opening the app shows the app icon in the middle of your normal background, light or dark, like a native iOS app.
- It stays up only until your data and recordings are ready, which is at least 0.6 seconds and never more than 2.5. Then it fades away with a slight zoom.
- iOS launch images for every recent iPhone and iPad (portrait and landscape on iPad), in light and dark. iOS shows these the instant you tap the icon, before the app has loaded, so there's no white flash.
  - These images take effect after the app is re-added to the Home Screen. The in-app launch screen works straight away.

## 3.3.2 · 14 Oct 2026
*Fixes from a full audit*
<!-- area: fixes -->

Fixes from a full audit: about 9,000 random taps across every screen and screen size, plus targeted tests and a code review.

- A damaged backup file no longer breaks the app. It's checked first, and all recordings are read before anything on your phone is replaced.
- Damaged saved data, or a full storage space when the app opens, no longer stops it starting.
- Leaving the Application or Song practice screen mid-recording now stops and saves the take, instead of recording in the background.
- On iPad and Mac, scrolling back up in the History or Exercises detail pane no longer triggers pull to refresh.
- Pull to refresh only ever updates to a newer version, never an older cached one.
- Edit and the long-session check refuse minutes that don't make sense (0, negative, or over 600) instead of quietly saving 1 minute.
- If a sheet has nothing to show (for example, notes for a take that was removed), it closes instead of hiding the tab bar.
- The page no longer nudges sideways when a segmented control bounces near the edge of the screen.
- The tab bar no longer stays shrunk when you're back at the top of a page after finishing.
- Coming back to the app refreshes the date and week, so Today is right the next morning.
- History stays in date order even if older data was saved out of order.

## 3.3.1 · 14 Oct 2026
*A way out of every sheet*
<!-- area: look -->

- Every sheet (session details, calendar, edit and others) has a close button (✕) at the top right, as in iOS 27. It stays in place while you scroll, so you can always get out.
- Drag a sheet down by its top to close it.
- Session and song practice details have an edit button (pencil) next to the ✕, replacing the "Edit session" text button. On iPad and Mac, the pencil sits beside the title in the detail pane.
- The extra "Close" button at the bottom of session details has been removed, because the ✕ does the same job.

## 3.3 · 14 Oct 2026
*Pull to refresh, and every screen size*

<!-- area: practice -->
**Pull to refresh**
- On Today and History, pull down from the top to refresh, like a native iOS app.
- The page follows your finger and the spinner fills in as you pull. Let go past the point where it's full to refresh, or earlier to cancel.
- Refreshing re-reads your saved data, updates the date and week, and checks GitHub for a newer version of the app. If there is one, it loads it straight away, so you no longer need to close and reopen the app after an update. <!-- area: backup -->

<!-- area: look -->
**Works on any screen**
- **iPhone on its side:** a compact tab bar with icons beside their labels. Today splits into two columns, and sheets stay a comfortable width.
- **iPad, or a narrower Mac window:**
  - Tabs move to a floating bar at the top, as on iPadOS.
  - Today becomes a two-column dashboard of cards.
  - History and Exercises become split views: pick on the left, see the details on the right.
  - Sheets open as centred cards.
  - Settings and the session steps stay at a readable width.
- **Mac, or iPad in landscape:** a sidebar with Today, History, Exercises and Settings.
- Turning your phone or resizing a window switches the layout straight away.
- With a mouse or trackpad, rows highlight when you hover over them.
- On a keyboard, Cmd (or Ctrl) + 1 to 4 switches between sections.

## 3.2 · 14 Oct 2026
*How did it go?*
<!-- area: practice -->

**How did it go?**
- Finishing a session or song practice opens a short "How did it go?" sheet.
  - Tap any words that fit, such as In control, Bit tight or Breath ran short.
  - Add your own words with "+ Your own". They're saved as chips for next time.
  - "Add a note" opens a text box only when you tap it.
  - Everything is optional, and ✕ skips it.
- How it went shows on the summary, in History, and in Toggl as a "How it went:" line.

**Notes on each exercise**
- A pencil on every Foundation and Rotation exercise opens quick words written for that exercise (for example "Buzz in the mask" for Humming), plus your own words and an optional note.
- These replace the old general note presets.
- Notes show on the summary, in Toggl next to the exercise, and on the exercise's History tab.

**Skip**
- Foundation levels are now Skip · 1 · 2 · 3.
- Skipped exercises don't count as done, and Toggl says "skipped".

**Song practice**
- A new Song practice card on Today for when you just want to sing a song, record takes and see how it went.
- It has its own stats and never counts towards your weekly goal, streak, monthly minutes, last-done dates or suggestions. <!-- area: progress -->
- History has a Sessions | Song practice switch, and song practice shows as a coral dot on the calendar. <!-- area: progress -->
- In Toggl it's tagged `#song-practice`. The Application step in a full session stays `#application`.

<!-- area: recordings -->
**Notes on takes**
- Tap a take to add quick words (like "Flat on the high note") and a note. This works in song practice and Application.
- Take notes are included in backups. <!-- area: backup -->

**Session clock**
- The top bar shows a live timer, such as "1 of 3 · 12:40".
- Tap it to open a larger clock with Pause, Resume and a time for each step. Paused time isn't counted.
- If a session has been running for over 90 minutes when you finish, the app asks how long you actually practised.

<!-- area: progress -->
**Edit finished sessions**
- Open any session or song practice and tap Edit to change the date, minutes, levels, notes and how it went.
- Monthly minutes, your streak, last-done dates and the exercise charts update to match.

<!-- area: practice -->
**Also new**
- Suggested rotation now picks the exercise that's gone longest since you last did it. Exercises you've never done come first.
- A backup reminder appears on Today if you've never backed up, or if it's been more than two weeks. <!-- area: backup -->
- Tap the date or the "Today" title to open the calendar, as well as the arrow. <!-- area: progress -->
- If you leave the app while recording, the take is stopped and saved, and the app tells you when you come back. <!-- area: recordings -->
- A tip about watching the coach video in picture-in-picture with YouTube Premium.
- Sheets no longer replay their slide-up animation when you tap something inside them. <!-- area: look -->

## 3.1 · 14 Oct 2026
*Liquid Glass*
<!-- area: look -->

**Liquid Glass upgrades** (a CSS imitation; the real material is only available to native apps)
- Bars, buttons and sheets have a brighter rim, a soft inner glow and a highlight along the top edge.
- A soft fade sits under the top bar when content scrolls beneath it.
- The tab bar shrinks to a small circle as you scroll down, and comes back when you scroll up or tap it.
- Level pickers have a glass knob that slides between 1, 2 and 3 and stretches slightly as it moves.
- Buttons spring back when pressed, sheets spring up, and the screen eases back behind an open sheet.
- The main session button is tinted glass.

**Exercise glyphs**
- Each exercise has its own icon, coloured by focus area:
  - Blue: cord closure
  - Purple: register
  - Teal: resonance
  - Amber: agility
  - Coral: blend
- Your own exercises get a sparkle icon.
- The glyphs appear on the Exercises tab, in the rotation picker, on each exercise page and in Today's suggestion.

<!-- area: progress -->
**Practice calendar**
- Today shows the full date above the title, with an arrow that opens a calendar of the month.
- Days you practised are highlighted and today is outlined. Arrows move between months.
- Tap a highlighted day to see its session, then tap the session for full details. Closing it returns you to the calendar.
- The calendar shows each month's session count and total time.

**Settings**
- New About section with a link to this GitHub repo.
- The version and release date show at the bottom of Settings.

## 3.0.1 · 14 Oct 2026
*No more accidental zoom*
<!-- area: fixes -->

- Pinch to zoom and double-tap to zoom are turned off, and tapping a text box no longer zooms the page. Quick repeated taps still register.

## 3.0 · 14 Oct 2026
*Today, Settings and exercise pages*
<!-- era: Liquid Glass · Native look, deeper tracking, and an app that stands on its own -->

<!-- area: look -->
**New app icon:** coral background with solid white sound-wave bars.

<!-- area: progress -->
**Today, in the style of Apple Books**
- A progress arch shows this week's minutes against a 70-minute goal.
- A Monday-to-Sunday row fills in each day you practised.
- The streak counts weeks in a row where you hit 70 minutes. The current week never breaks it while it's still in progress.
- Rows for this month's minutes (against 280) and the suggested rotation exercise.

<!-- area: backup -->
**Settings tab (new)**
- **Export backup:** saves one file with everything: sessions, minutes, exercises, songs, settings and recordings.
- **Import backup:** shows what's inside, then replaces this phone's data after you confirm. It also restores the last-backed-up time.
- The last backup time shows under the backup options, and turns red after 14 days.
- Recordings storage, reset this month and reset all data moved here from Today. Reset all data offers to export a backup first.

<!-- area: practice -->
**Exercise pages**
- Tap any exercise to open its own page, with **Summary** and **History** tabs.
- **Summary:** what it is, why it helps, and where it shows up in songs, taken from the vocal exercise write-ups.
- **History:** a chart of your level over time, plus every session the exercise was in.
- Your own exercises can have a description you write yourself.

<!-- area: practice -->
**Exercises tab**
- Descriptions show when each exercise was last done instead of a count. Practice from before 14 Oct shows as "last done before 14 Oct".
- One Coach video link replaces the Watch button on every exercise. During a session, it's a video button in the top bar.

<!-- area: practice -->
**Deleting**
- Swipe left to delete past sessions, takes, songs and your own exercises. Every delete asks "Are you sure?" first.
- Takes can be deleted one at a time.
- Deleting a session takes its minutes off that month and updates last-done dates.

## 2.0 · 14 Oct 2026
*A native iOS redesign*
<!-- era: Native iOS · Rebuilt to look and feel like an iPhone app -->

A full redesign to look and feel like a native iOS app.

<!-- area: look -->
**Look**
- iOS system font, system blue and automatic dark mode. The old orange ivanc.digital styling and Barlow fonts are gone.
- Large titles, rounded list groups and glass bars.

<!-- area: look -->
**Tabs:** Today, History and Exercises.

<!-- area: practice -->
**Sessions**
- Levels use an inline 1 · 2 · 3 picker.
- Rotation lets you pick several exercises, each with its own level.
- Notes come from presets or your own words.
- An unfinished session is saved, so you can resume or discard it later.

<!-- area: recordings -->
**Application step**
- A song library, so you pick a song instead of typing it.
- Record and play back takes:
  - Mono and compressed, up to 2 minutes each
  - Keeps the last 3 takes per song, plus any you star
- Rate pitch, tone and ease from 1 to 3.
- Share a take to Files or iCloud Drive.

<!-- area: progress -->
**History:** every finished session, with Copy for Toggl.

<!-- area: backup -->
**Data**
- Your existing streak, minutes and custom exercises carried over.
- First app icon.

## 1.0 · 25 May 2026
*First release*
<!-- era: The tracker · A simple three-block session tracker -->
<!-- area: practice -->

First release.
- A three-block session tracker: Foundation, Rotation and Application.
- Exercise levels with a confirm step before logging.
- Toggl-ready copy with `#tags`, including Copy All.
- Streak counter and a monthly progress bar towards 280 minutes. <!-- area: progress -->
- Smart rotation suggestions and custom exercises.
- Light-mode design in the ivanc.digital style. <!-- area: look -->
