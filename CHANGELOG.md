# Changelog

All notable changes to Vocal Sessions. The app's **Changelog** page (Settings › Changelog) is built from this file, so every entry here appears there.

Version numbers follow **major.minor.patch**:
- **Major:** a redesign
- **Minor:** new features
- **Patch:** small fixes

---

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
