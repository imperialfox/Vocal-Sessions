# Vocal Sessions

A mobile-first companion for structured vocal practice, styled like a native iOS app. It's a single HTML file with no install, no backend and no account. It's designed to live on your iPhone Home Screen.

![License: MIT](https://img.shields.io/badge/license-MIT-blue) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![Works offline](https://img.shields.io/badge/works-offline-blue)

---

## What it does

It guides you through a three-step practice session, keeps a history of your sessions, and produces ready-to-paste [Toggl Track](https://toggl.com/track/) entries with `#tags` inline.

| Step | What | Time |
|---|---|---|
| Foundation | 4 core SOVT exercises, all required | ~25 min |
| Rotation | One or more exercises from a pool of 8, plus any you add | ~15 min |
| Application | Sing a real song or section, record a take, rate it | ~5–10 min |

---

## Features

**Today tab**
- Streak, minutes this month, and progress towards a 280 min/month target
- The least-practised rotation exercise, suggested automatically
- An unfinished session can be resumed or discarded
- Settings: recordings storage, reset this month, reset all data

**Session**
- **Levels:** each exercise has 3 levels, set with a 1 · 2 · 3 picker, so partial sessions are recorded honestly
- **Coach video:** tapping an exercise opens the coach video in YouTube at that exercise's timestamp
- **Multi-select rotation:** pick as many exercises as you like, each with its own level
- **Notes:** one per step, from presets or your own words
- **Application:**
  - Choose a song from your library
  - Record takes and play them back
  - Rate pitch, tone and ease from 1 to 3

**Recordings**
- Mono, compressed audio (about 0.5 MB a minute), up to 2 minutes per take
- Keeps the last 3 takes per song, plus any you star
- Share saves a take to Files or iCloud Drive, named by song and date
- Takes are stored on the phone only

**History tab**
- Every finished session, grouped by month, with levels, notes, song and ratings
- Copy any past session for Toggl again

**Exercises tab**
- Every exercise, with how often and when you last did it
- Add or remove your own exercises (with an optional video timestamp) and songs

**Toggl copy:** one tap copies a line per block, for example:

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

It opens full screen like an app. iOS may ask for microphone access each time you record, which is an Apple limit on Home Screen web apps.

---

## Hosting

GitHub Pages: **Settings → Pages → Deploy from branch → `main` → `/ (root)`**. Changes go live about a minute after each push.

---

## Adapting it for yourself

Everything to edit sits at the top of the `<script>` block:

```js
const VIDEO = 'https://youtu.be/…';  // your coach video
const TARGET = 280;                    // monthly target in minutes
const FOUND = [ { id: 'slides', name: 'Vocal slides', focus: 'agility', ts: 0 }, … ];
const ROT   = [ { id: 'falsetto', name: 'Falsetto voice', focus: 'register', ts: 1170 }, … ];
```

`ts` is the exercise's start time in the video, in seconds.

If the video is private, the YouTube buttons only work for the owner, signed in to YouTube.

---

## Data and privacy

- Session data is stored in `localStorage` and recordings in IndexedDB, both on your device only.
- There's no server, analytics or tracking.
- Deleting the Home Screen app or clearing Safari's website data erases everything, so save takes you want to keep to iCloud Drive.

---

## Stack

Vanilla HTML, CSS and JavaScript, with no frameworks or build step. It uses the iOS system font and a CSS imitation of Liquid Glass (blur and translucency).

---

## License

MIT

---

*Built by [ivanc.digital](https://ivanc.digital)*
