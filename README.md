# 🎤 Vocal Session Tracker

A lightweight, mobile-first session companion for structured vocal practice. Built as a single HTML file — no install, no backend, no account required. Designed to live on your iPhone Home Screen.

![License: MIT](https://img.shields.io/badge/license-MIT-orange) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen) ![Works offline](https://img.shields.io/badge/works-offline-blue)

-----

## What it does

Guides you through a three-block vocal practice session and generates ready-to-paste [Toggl Track](https://toggl.com/track/) entries so your time is logged accurately with zero friction.

**The session structure:**

|Block      |What                                       |Time     |
|-----------|-------------------------------------------|---------|
|Foundation |4 core SOVT exercises, all required        |~25 min  |
|Rotation   |1 exercise from a pool of 8 (+ any you add)|~15 min  |
|Application|Sing a real phrase or song                 |~5–10 min|

At the end of each session the app generates pre-formatted Toggl descriptions with `#tag` syntax inline — one paste and your tags are applied automatically.

-----

## Features

- **Level tracking per exercise** — each exercise has 3 levels. Tap to expand and mark how far you got (1, 2, or 3). Partial sessions are recorded honestly.
- **Confirm before logging** — a review sheet slides up before each block is committed, so you can go back and correct levels.
- **Smart rotation suggest** — tracks which exercises you’ve done least often and highlights the most neglected one each session.
- **Add your own exercises** — tap “+ Add exercise for today” in the rotation block to add a custom exercise for that session. Custom exercises persist across sessions.
- **Monthly progress bar** — shows minutes logged vs the 280 min/month target (70 min/week).
- **Streak counter** — tracks consecutive practice days.
- **Toggl-ready copy** — each block generates a single-line description with `#hashtag` tags. “Copy All” bundles all three entries for one paste.
- **localStorage only** — all data stays on your device. Nothing is sent anywhere.
- **Works offline** — once loaded, no internet connection required.

-----

## How to use

### In the browser

Open `index.html` directly in any modern browser. No server needed.

### On iPhone Home Screen (recommended)

1. Host the file (see [Hosting](#hosting) below)
1. Open the URL in **Safari**
1. Tap the Share icon → **Add to Home Screen**
1. Name it and tap Add

It will open full screen like a native app, with no browser chrome.

-----

## Hosting

The simplest free option is GitHub Pages:

1. Fork or clone this repo
1. Go to **Settings → Pages**
1. Set Source to `Deploy from branch` → `main` → `/ (root)`
1. Save — your app will be live at `https://yourusername.github.io/vocal-session`

Alternatively, drag and drop `index.html` onto [Netlify Drop](https://app.netlify.com/drop) for an instant public URL with no account needed.

-----

## The exercise system

### Foundation block (every session, all 4 required)

|Exercise               |Focus       |
|-----------------------|------------|
|Vocal Slides           |Agility     |
|Humming                |Cord closure|
|Lip Bubbling           |Cord closure|
|Singing Through a Straw|Cord closure|

### Rotation pool (pick 1 per session)

|Exercise                  |Focus    |
|--------------------------|---------|
|Falsetto Voice            |Register |
|Upper to Lower Voice      |Register |
|Singing on the Rung       |Resonance|
|Squeaky Hinge             |Register |
|Half Squeaky / Half Normal|Blend    |
|Vertical Mouth            |Resonance|
|Nasal Exercise            |Resonance|
|Vocal Flexibility         |Agility  |

Exercise durations are based on a real vocal coach video series. Levels 1–2–3 represent thirds of the full exercise duration.

### Toggl tag system

Each session generates entries tagged with two tags:

**Block type:** `#foundation` `#rotation` `#application` `#review`

**Focus area:** `#cord-closure` `#register` `#resonance` `#agility` `#blend`

Paste a description like `Foundation: Vocal Slides L3, Humming L2... #foundation #cord-closure` directly into the Toggl description field — the `#` triggers tag autocomplete.

-----

## Adapting it for yourself

The exercise lists, note presets, and monthly target are all defined at the top of the `<script>` block and straightforward to edit:

```js
// Change the monthly target (in minutes)
const TARGET_MIN_MONTH = 280;

// Edit or add foundation exercises
const FOUNDATION = [
  { name: 'Vocal Slides', focus: 'agility', dur: 435 },
  // ...
];

// Edit or add rotation exercises
const ROTATION = [
  { name: 'Falsetto Voice', focus: 'register', dur: 315 },
  // ...
];
```

`dur` is the exercise duration in seconds, used internally for level-time calculations. You can set it to `0` if you don’t need that.

-----

## Data & privacy

All data is stored in `localStorage` on your device only. There is no server, no analytics, no tracking, no cookies. Clearing your browser storage or using a private window will reset the app.

-----

## Stack

- Vanilla HTML, CSS, JavaScript — no frameworks, no build step
- [Barlow / Barlow Condensed](https://fonts.google.com/specimen/Barlow) via Google Fonts
- localStorage for persistence

-----

## License

MIT — do whatever you want with it.

-----

*Built by [ivanc.digital](https://ivanc.digital)*