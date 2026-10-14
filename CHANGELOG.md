# Changelog

All notable changes to Vocal Sessions. The version shows at the bottom of the Settings tab.

Version numbers follow **major.minor.patch**:
- **Major:** a redesign
- **Minor:** new features
- **Patch:** small fixes

---

## 3.3.1 · 14 Oct 2026

- Every sheet (session details, calendar, edit and others) has a close button (✕) at the top right, as in iOS 27. It stays in place while you scroll, so you can always get out.
- Drag a sheet down by its top to close it.
- The extra "Close" button at the bottom of session details has been removed, because the ✕ does the same job.

## 3.3 · 14 Oct 2026

**Pull to refresh**
- On Today and History, pull down from the top to refresh, like a native iOS app.
- The page follows your finger and the spinner fills in as you pull. Let go past the point where it's full to refresh, or earlier to cancel.
- Refreshing re-reads your saved data, updates the date and week, and checks GitHub for a newer version of the app. If there is one, it loads it straight away, so you no longer need to close and reopen the app after an update.

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
- It has its own stats and never counts towards your weekly goal, streak, monthly minutes, last-done dates or suggestions.
- History has a Sessions | Song practice switch, and song practice shows as a coral dot on the calendar.
- In Toggl it's tagged `#song-practice`. The Application step in a full session stays `#application`.

**Notes on takes**
- Tap a take to add quick words (like "Flat on the high note") and a note. This works in song practice and Application.
- Take notes are included in backups.

**Session clock**
- The top bar shows a live timer, such as "1 of 3 · 12:40".
- Tap it to open a larger clock with Pause, Resume and a time for each step. Paused time isn't counted.
- If a session has been running for over 90 minutes when you finish, the app asks how long you actually practised.

**Edit finished sessions**
- Open any session or song practice and tap Edit to change the date, minutes, levels, notes and how it went.
- Monthly minutes, your streak, last-done dates and the exercise charts update to match.

**Also new**
- Suggested rotation now picks the exercise that's gone longest since you last did it. Exercises you've never done come first.
- A backup reminder appears on Today if you've never backed up, or if it's been more than two weeks.
- Tap the date or the "Today" title to open the calendar, as well as the arrow.
- If you leave the app while recording, the take is stopped and saved, and the app tells you when you come back.
- A tip about watching the coach video in picture-in-picture with YouTube Premium.
- Sheets no longer replay their slide-up animation when you tap something inside them.

## 3.1 · 14 Oct 2026

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

**Practice calendar**
- Today shows the full date above the title, with an arrow that opens a calendar of the month.
- Days you practised are highlighted and today is outlined. Arrows move between months.
- Tap a highlighted day to see its session, then tap the session for full details. Closing it returns you to the calendar.
- The calendar shows each month's session count and total time.

**Settings**
- New About section with a link to this GitHub repo.
- The version and release date show at the bottom of Settings.

## 3.0.1 · 14 Oct 2026

- Pinch to zoom and double-tap to zoom are turned off, and tapping a text box no longer zooms the page. Quick repeated taps still register.

## 3.0 · 14 Oct 2026

**New app icon:** coral background with solid white sound-wave bars.

**Today, in the style of Apple Books**
- A progress arch shows this week's minutes against a 70-minute goal.
- A Monday-to-Sunday row fills in each day you practised.
- The streak counts weeks in a row where you hit 70 minutes. The current week never breaks it while it's still in progress.
- Rows for this month's minutes (against 280) and the suggested rotation exercise.

**Settings tab (new)**
- **Export backup:** saves one file with everything: sessions, minutes, exercises, songs, settings and recordings.
- **Import backup:** shows what's inside, then replaces this phone's data after you confirm. It also restores the last-backed-up time.
- The last backup time shows under the backup options, and turns red after 14 days.
- Recordings storage, reset this month and reset all data moved here from Today. Reset all data offers to export a backup first.

**Exercise pages**
- Tap any exercise to open its own page, with **Summary** and **History** tabs.
- **Summary:** what it is, why it helps, and where it shows up in songs, taken from the vocal exercise write-ups.
- **History:** a chart of your level over time, plus every session the exercise was in.
- Your own exercises can have a description you write yourself.

**Exercises tab**
- Descriptions show when each exercise was last done instead of a count. Practice from before 14 Oct shows as "last done before 14 Oct".
- One Coach video link replaces the Watch button on every exercise. During a session, it's a video button in the top bar.

**Deleting**
- Swipe left to delete past sessions, takes, songs and your own exercises. Every delete asks "Are you sure?" first.
- Takes can be deleted one at a time.
- Deleting a session takes its minutes off that month and updates last-done dates.

## 2.0 · 14 Oct 2026

A full redesign to look and feel like a native iOS app.

**Look**
- iOS system font, system blue and automatic dark mode. The old orange ivanc.digital styling and Barlow fonts are gone.
- Large titles, rounded list groups and glass bars.

**Tabs:** Today, History and Exercises.

**Sessions**
- Levels use an inline 1 · 2 · 3 picker.
- Rotation lets you pick several exercises, each with its own level.
- Notes come from presets or your own words.
- An unfinished session is saved, so you can resume or discard it later.

**Application step**
- A song library, so you pick a song instead of typing it.
- Record and play back takes:
  - Mono and compressed, up to 2 minutes each
  - Keeps the last 3 takes per song, plus any you star
- Rate pitch, tone and ease from 1 to 3.
- Share a take to Files or iCloud Drive.

**History:** every finished session, with Copy for Toggl.

**Data**
- Your existing streak, minutes and custom exercises carried over.
- First app icon.

## 1.0 · 25 May 2026

First release.
- A three-block session tracker: Foundation, Rotation and Application.
- Exercise levels with a confirm step before logging.
- Toggl-ready copy with `#tags`, including Copy All.
- Streak counter and a monthly progress bar towards 280 minutes.
- Smart rotation suggestions and custom exercises.
- Light-mode design in the ivanc.digital style.
