# Vocal Sessions

A mobile-first companion for structured vocal practice, styled like a native iOS app. It's a single HTML file with no install, no backend and no account. It's designed to live on your iPhone Home Screen.

![Version 3.3](https://img.shields.io/badge/version-3.3-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-blue) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![Works offline](https://img.shields.io/badge/works-offline-blue)

**Current version: 3.3 · 14 Oct 2026.** See the [changelog](CHANGELOG.md) for what changed in each release.

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

**History**
- A **Sessions | Song practice** switch
- Every finished session, grouped by month, with levels, notes and how it went
- Open a session to:
  - Copy it for Toggl again
  - **Edit** the date, minutes, levels, notes and how it went. Totals, streak and last-done dates update to match.
  - Delete it
- Pull down to refresh
- Swipe left to delete. Deleting asks first, takes its minutes off the month, and updates last-done dates.

**Exercises**
- One link to the coach video, opening in YouTube
- Every exercise with its own glyph (coloured by focus area) and when you last did it
- Tap an exercise for its own page:
  - **Summary:** what it is, why it helps, and where it shows up in songs
  - **History:** a chart of your level over time, plus every session it was in, with your notes
- Add your own exercises (with an optional description) and songs. Swipe left to delete them.

**Settings**
- **Export backup:** one file with everything (sessions, minutes, exercises, songs and recordings). Save it to iCloud Drive.
- **Import backup:** shows what's in the file, then replaces this phone's data after you confirm.
- When you last backed up, which turns red after two weeks
- Recordings storage, reset this month, and reset all data. Every reset asks first.
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

Everything to edit sits at the top of the `<script>` block: `VIDEO` (your coach video), `TARGET` and `WEEK_TARGET` (minutes), the `FOUND` and `ROT` exercise lists, `DESC` (the write-up shown on each exercise's Summary tab), `EX_WORDS` (quick words for each exercise) and `HOW_WORDS` (the "How did it go?" words).

---

## Data and privacy

- Session data is stored in `localStorage` and recordings in IndexedDB, both on your device only.
- There's no server, analytics or tracking.
- Backups are plain JSON files that you keep.

---

## Stack

Vanilla HTML, CSS and JavaScript, with no frameworks or build step. It uses the iOS system font and a CSS imitation of Liquid Glass: rim light, inner glow, a shrinking tab bar, sliding glass pickers and springy motion.

---

## License

MIT

---

*Built by [ivanc.digital](https://ivanc.digital)*
