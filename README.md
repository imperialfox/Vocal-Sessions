# Vocal Sessions

A mobile-first companion for structured vocal practice, styled like a native iOS app. It's a single HTML file with no install, no backend and no account. It's designed to live on your iPhone Home Screen.

![License: MIT](https://img.shields.io/badge/license-MIT-blue) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![Works offline](https://img.shields.io/badge/works-offline-blue)

---

## What it does

It guides you through a three-step practice session, keeps a history of every session, and produces ready-to-paste [Toggl Track](https://toggl.com/track/) entries with `#tags` inline.

| Step | What | Time |
|---|---|---|
| Foundation | 4 core SOVT exercises, all required | ~25 min |
| Rotation | One or more exercises from a pool of 8, plus any you add | ~15 min |
| Application | Sing a real song or section, record a take, rate it | ~5–10 min |

---

## Tabs

**Today**
- Today's date above the title, with an arrow that opens a practice calendar. Practised days are highlighted; tap one to see and open its session.
- A progress arch showing this week's minutes against a 70-minute goal
- A Monday-to-Sunday row that fills in each day you practised
- A weekly streak: weeks in a row where you hit 70 minutes. The current week never breaks it while it's still in progress.
- This month's minutes against 280, and the least-practised rotation exercise
- Start, resume or discard a session

**History**
- Every finished session, grouped by month, with levels, notes, song and ratings
- Copy any session for Toggl again
- Swipe left, or open a session, to delete it. Deleting asks first, takes its minutes off the month, and updates last-done dates.

**Exercises**
- One link to the coach video, opening in YouTube
- Every exercise with its own glyph (coloured by focus area) and when you last did it
- Tap an exercise for its own page:
  - **Summary:** what it is, why it helps, and where it shows up in songs
  - **History:** a chart of your level over time, plus every session it was in
- Add your own exercises (with an optional description) and songs. Swipe left to delete them.

**Settings**
- **Export backup:** one file with everything (sessions, minutes, exercises, songs and recordings). Save it to iCloud Drive.
- **Import backup:** shows what's in the file, then replaces this phone's data after you confirm.
- When you last backed up, which turns red after two weeks
- Recordings storage, reset this month, and reset all data. Every reset asks first.
- A link back to this GitHub repo, and the app version with its release date

---

## Session details

- **Levels:** each exercise has 3 levels, set with a 1 · 2 · 3 picker
- **Multi-select rotation:** pick as many as you like, each with its own level
- **Notes:** one per step, from presets or your own words
- **Recordings:**
  - Mono, compressed audio (about 0.5 MB a minute), up to 2 minutes per take
  - Keeps the last 3 takes per song plus any you star
  - Each take can be shared (Save to Files or iCloud Drive) or deleted
- **Toggl copy:** one line per block, for example:

```
Foundation: Vocal slides L3, Humming L3, Lip bubbling L3, Singing through a straw L2 #foundation #cord-closure
Vertical mouth L2/3 #rotation #resonance
Application: Versace on the Floor · bridge — pitch 2, tone 3, ease 2 #application
```

Paste into Toggl's description field; the `#` triggers tag autocomplete.

---

## On iPhone

1. Open the GitHub Pages URL in **Safari**
2. Tap Share → **Add to Home Screen** → Add

iOS sets a Home Screen app's icon when you add it. To pick up a new icon:
1. Export a backup
2. Remove the app and add it again
3. Import the backup

Removing a Home Screen app deletes its data, so always export first.

---

## Adapting it for yourself

Everything to edit sits at the top of the `<script>` block: `VIDEO` (your coach video), `TARGET` and `WEEK_TARGET` (minutes), the `FOUND` and `ROT` exercise lists, and `DESC` (the write-up shown on each exercise's Summary tab).

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
