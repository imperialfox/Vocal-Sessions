# Vocal Sessions

A mobile-first companion for structured vocal practice, styled like a native iOS app. It's a single HTML file with no install, no backend and no account. It's designed to live on your iPhone Home Screen.

![Version 3.7.2](https://img.shields.io/badge/version-3.7.2-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-blue) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![Works offline](https://img.shields.io/badge/works-offline-blue) [![Tests](https://github.com/imperialfox/Vocal-Sessions/actions/workflows/tests.yml/badge.svg)](https://github.com/imperialfox/Vocal-Sessions/actions/workflows/tests.yml)

**Current version: 3.7.2 · 15 Oct 2026.** See the [changelog](CHANGELOG.md) for what changed in each release.

---

## What it does

It guides you through a three-step practice session, keeps a history of every session, and produces ready-to-paste [Toggl Track](https://toggl.com/track/) entries with `#tags` inline.

| Step | What | Time |
|---|---|---|
| Foundation | 4 core SOVT exercises, all required | ~25 min |
| Rotation | One or more exercises from a pool of 8, plus any you add | ~15 min |
| Application | Sing a real song or section, record a take, rate it | ~5–10 min |

There's also **Song practice**, for when you just want to sing a song and record it. It's kept separate from the focused stats above.

---

## Tabs

**Today**
- Today's date above the title. Tap the date, the title or the arrow to open a practice calendar:
  - Focused sessions are highlighted, and song practice shows as a coral dot.
  - Tap a day to see and open what you did.
- A reminder to back up if you never have, or if it's been more than two weeks
- A progress arch showing this week's minutes against a 70-minute goal
- A Monday-to-Sunday row that fills in each day you practised
- A weekly streak: weeks in a row where you hit 70 minutes. The current week never breaks it while it's still in progress.
- This month's minutes against 280, and the suggested rotation exercise (the one that's gone longest since you last did it)
- Start, resume or discard a session
- A Song practice card with its own weekly stats
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
  - Copy it for Toggl again
  - Edit it with the pencil: date, minutes, levels, notes, how it went, and how its time was split between the steps. Totals, streak and last-done dates update to match.
  - Delete it
- Every summary leads to the same lists and details, from wherever it appears: Progress, the calendar, Today and Exercises.
- Pull down to refresh

**Exercises**
- One link to the coach video, opening in YouTube
- Every exercise with its own glyph (coloured by focus area) and when you last did it
- Tap an exercise for its own page:
  - **Summary:** what it is, why it helps, and where it shows up in songs
  - **History:** a chart of your level over time, plus every session it was in, with your notes
- Add your own exercises (with an optional description) and songs. Tap a song to see its song practice. Swipe left to delete them.

**Settings**
- **Export backup:** one file with everything (sessions, minutes, exercises, songs and recordings), checked before you save it. Keep it in iCloud Drive › Vocal Sessions › Backups.
- **Import backup:** checks the file and compares it with what's on this device, then replaces this device's data after you confirm.
- **Check a backup:** tells you whether a file is complete and what's inside, without changing anything.
- **Undo last restore:** for 30 days after a restore.
- **Backup history**, **Where backups go** (a set-up guide) and **Save a read-me file**
- When you last backed up, which turns red after two weeks
- **Storage:** recordings, and **Storage protection**, which shows whether iOS has agreed not to clear the app's data when space runs low
- Reset this month, and reset all data. Every reset asks first.
- **Changelog:** every version on a timeline, with a growth chart of improvements by area. It's built from [CHANGELOG.md](CHANGELOG.md), and tapping the version number opens it too.
- A link back to this GitHub repo, and the app version with its release date

---

## Session details

- **Levels:** each exercise has 3 levels. Foundation uses a Skip · 1 · 2 · 3 picker, and skipped exercises don't count as done.
- **Multi-select rotation:** pick as many as you like, each with its own level
- **Notes per exercise:** the pencil opens quick words written for that exercise, your own saved words, and an optional note
- **Session clock:** a live timer in the top bar
  - Tap it for a larger clock with Pause and a time for each step. Paused time isn't counted.
  - Sessions over 90 minutes ask how long you actually practised.
- **How did it go?** After finishing, tap words that fit (or add your own) and an optional note. You can skip it.
- **Recordings:**
  - Mono, compressed audio (about 0.5 MB a minute), up to 2 minutes per take
  - Keeps the last 3 takes per song plus any you star
  - Tap a take to add notes, such as "Flat on the high note"
  - Each take can be shared (Save to Files or iCloud Drive) or deleted
  - Leaving the app while recording stops the take and saves it
- **Toggl copy:** one line per block, for example:

```
Foundation: Vocal slides L3, Humming L3, Lip bubbling L3, Singing through a straw L2 #foundation #cord-closure
Vertical mouth L2/3 #rotation #resonance
Application: Versace on the Floor · bridge — pitch 2, tone 3, ease 2 #application
How it went: In control, Bit tight
```

Notes appear next to their exercise, and skipped exercises say "skipped". Song practice copies as one line tagged `#song-practice`.

Paste into Toggl's description field; the `#` triggers tag autocomplete.

---

## iPhone, iPad and Mac

The layout follows the device, like a native Apple app:

| Screen | Layout |
|---|---|
| iPhone | A floating tab bar at the bottom |
| iPhone on its side | A compact tab bar, with Today in two columns |
| iPad, or a narrower Mac window | Tabs at the top, a dashboard on Today, and split views for History and Exercises |
| Mac, or iPad in landscape | A sidebar |

Opening the app shows a short launch screen with the app icon, in light or dark to match your phone. The launch images for each device are in the `splash` folder.

Sheets open as centred cards on bigger screens. With a mouse or trackpad, rows highlight on hover, and Cmd (or Ctrl) + 1 to 4 switches sections.

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

Everything to edit is in `js/content.js`, which starts with a guide to what's safe to change: `VIDEO` (your coach video), `TARGET` and `WEEK_TARGET` (minutes), the `FOUND` and `ROT` exercise lists, `DESC` (the write-up shown on each exercise's Summary tab), `EX_WORDS` (quick words for each exercise) and `HOW_WORDS` (the "How did it go?" words), plus `TOGGL` (the Toggl tags) and `VID` (how long each exercise runs in the coach video). Run `python tests/run.py content` after editing to check it all fits together.

---

## Offline

A small service worker (`sw.js`) keeps a copy of the app on your device. When you're online, the app loads fresh and picks up updates. With no signal, or a connection too slow to answer within 4 seconds, it opens from the saved copy. The changelog is kept for offline use the same way.

## Data and privacy

- Session data is stored in `localStorage` and recordings in IndexedDB, both on your device only.
- There's no server, analytics or tracking.
- Backups are plain JSON files that you keep. See [Backups](#backups).

## Backups

**Names.** `Vocal Sessions backup · 2026-10 · iPhone.json`: one file per month for each device. Backing up again in the same month, Files asks whether to replace that month's file.

**Where.** iCloud Drive › Vocal Sessions › Backups. Settings › Where backups go walks through making the folder the first time; Files remembers it after that.

**Check code.** Every backup ends with a SHA-256 fingerprint of its contents. Before offering to save, the app reads the finished file back and checks it. Check a backup and Import check it again, so a file that was cut short while copying, or edited, is spotted before anything is replaced. Backups from before 3.6 have no check code; they still import and are checked for readability.

**Before you restore.** A backup from a newer version of the app says so and suggests updating first. Import shows the backup next to what's on this device: sessions, song practice, songs, recordings, practice time and the latest practice. If anything on the device isn't in the backup, it says how much would be removed and offers to back up first. A copy of the device's data, recordings included, is kept for 30 days so the restore can be undone.

**Finding them later.** Each file opens with a short plain-English note: what it is, which device and app version made it, how many sessions and recordings it holds, and how to restore it. Settings › Save a read-me file saves `READ ME – Vocal Sessions backups.txt` for the folder too.

---

## Stack

Vanilla HTML, CSS and JavaScript, with no frameworks or build step: `index.html`, one stylesheet in `css/` and a dozen plain scripts in `js/`. It uses the iOS system font and a CSS imitation of Liquid Glass: rim light, inner glow, a shrinking tab bar, sliding glass pickers and springy motion.

---

## Development

See [MAINTAINING.md](MAINTAINING.md) for how the app is built, where data lives, the rules that keep old backups working, and how to release.

- `python tests/run.py` runs the full test suite in Chromium: every screen at every size, a full practice session, backups (including real ones from earlier versions), recording, and thousands of random taps. GitHub runs it after every push.
- `python tools/release.py 3.7` sets a new version number everywhere at once.

---

## License

MIT

---

*Built by [ivanc.digital](https://ivanc.digital)*
