# Changelog

All notable changes to Vocal Sessions. The app's **Changelog** page (Settings › Changelog) is built from this file, so every entry here appears there.

Version numbers follow **major.minor.patch**:
- **Major:** a redesign
- **Minor:** new features
- **Patch:** small fixes

---

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
