# Maintaining Vocal Sessions

Notes for whoever works on the app next, whether that's Ivan, a new Claude session or anyone else. The [README](README.md) covers what the app does; this covers how it's built and how to change it safely.

---

## The short version

1. Change `index.html` (and `sw.js` if offline behaviour changes).
2. Run `python tests/run.py`. Everything must pass.
3. Run `python tools/release.py 3.7` with the new version, and write the changes in `CHANGELOG.md`.
4. Run `python tests/run.py release` to check the version agrees everywhere.
5. Push to `main`. GitHub Pages publishes it within a minute or two, and the **Tests** check runs on GitHub.

**Working with Claude:** Ivan reviews prototypes first. Nothing is built into the app or pushed until he says **"render"**.

---

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app: markup, styles and script in one file, with no build step |
| `sw.js` | Offline support. Everything except images is fetched fresh (4-second timeout, then the saved copy); images come from the saved copy. Registered on `https` and on `localhost` (so the tests cover it) |
| `icon.png`, `splash/` | Home Screen icon and iOS launch images (light and dark, every recent iPhone and iPad) |
| `CHANGELOG.md` | What changed in each version, written for Ivan, not developers. The app's Changelog page is built from it (see below) |
| `.nojekyll` | Tells GitHub Pages to serve files exactly as they are, so `CHANGELOG.md` reaches the app as plain text |
| `tests/` | The test suite (see below) |
| `tools/release.py` | Sets the version number everywhere at once |
| `.github/workflows/tests.yml` | Runs the tests on GitHub after every push |

Inside `index.html`, the script is split into sections marked `/* ===== Name ===== */`: Config, Storage, Recordings, Helpers, UI state, Screens, Progress, Chrome, Render, Session logic, Recording, Backup, Copy, Events and Pull to refresh.

---

## Where data lives

Everything stays on the device. There is no server.

| Where | Key | Holds |
|---|---|---|
| localStorage | `vocalTracker` | All saved data (`D`): sessions, song practice, months, exercises, songs, words, last backup |
| localStorage | `vocalDraft` | The session in progress (`X`), so it survives closing the app |
| localStorage | `vocalBackupLog` | Backup history for this device |
| localStorage | `vocalBeforeUpgrade` | The data as it was before the last data upgrade, kept for 30 days |
| IndexedDB `vocalTakes` (version 2) | store `takes` | Recordings, with their audio as Blobs |
| IndexedDB `vocalTakes` | store `undo` | The copy kept for 30 days after a restore |

`cleanData()` checks anything loaded or restored and drops what's malformed, so damaged data can't stop the app starting. `migrate()` fills in defaults and then runs `upgradeData()`; `normX()` upgrades older drafts.

### Data version

Saved data carries `schema` (currently 1, from 3.7). To change the shape of saved data:

1. Add a numbered step to `UPGRADES` that changes `D` in place, and raise `SCHEMA` to match.
2. Steps run in order the first time the new version opens, and whenever an older backup is restored. Before they run, the data is copied to `vocalBeforeUpgrade`.
3. Add a test in `tests/test_data.py` that loads data from before the step and checks the result.

A backup whose `schema` is higher than the app's shows "Made by a newer version" before restoring.

### Rules that keep old data working

- **Never rename or remove an exercise id** (`slides`, `humming`, `lip`, `straw`, `falsetto`, `upperlower`, `rung`, `hinge`, `half`, `vertical`, `nasal`, `flex`). Sessions store levels by these ids. The backup tests fail if they change.
- **Data changes are additive.** Add fields with a default; don't rename or repurpose existing ones. Older backups must still restore, and new backups must still restore in the previous version.
- **Bump the IndexedDB version only to add stores**, and create each store only if it's missing.

---

## The Changelog page

Settings › Changelog fetches `CHANGELOG.md` and builds the timeline from it (`parseChangelog()`), so **writing the changelog is all it takes**. The format it relies on:

```markdown
## 3.7 · 15 Oct 2026
*Headline shown on the card*
<!-- area: backup -->            ← optional: the area for the whole version

<!-- area: look -->              ← the area for the next section
**Section title**
- A change. Each bullet counts as one improvement.
  - A sub-point (shown in Every change, not counted)
- Another change. <!-- area: fixes -->   ← one bullet in a different area
```

- Areas: `practice`, `progress`, `recordings`, `backup`, `look`, `fixes`. Untagged bullets use their section's or version's area, or `fixes` for a patch version and `practice` otherwise.
- An x.0 version can name its era: `<!-- era: Liquid Glass · Native look, deeper tracking… -->`.
- The comments are invisible on GitHub.
- `python tests/run.py release` checks every heading, headline and area tag, and the changelog tests check every version appears in the app.

## Backups

A backup is a JSON file with: a plain-English `README` array, `app`, `format` (2), `appVersion`, `exportedAt`, `device`, `summary`, `data` (= `D`), `draft` (= `X`), `takes` (recordings as data URLs) and `checkCode`.

- `checkCode` is the SHA-256 of `JSON.stringify({data, draft, takes})`. `inspectBackup()` recalculates it to decide whether a file is complete (`good`), from before 3.6 (`old`), edited or partly copied (`changed`), missing some recordings (`partial`) or unusable (`broken`).
- Export reads its own file back through `inspectBackup()` before offering to save it.
- Restore keeps an undo copy first; `undoRestore()` puts it back.
- Files are named `Vocal Sessions backup · YYYY-MM · Device.json`, so iOS offers to replace the month's file.

The fixtures in `tests/fixtures/` are real backups made by 3.5 and 3.6, plus a copy of the 3.6 app. **Don't regenerate them.** They prove that old backups keep working, and that new backups still open in 3.6.

---

## Tests

```
pip install playwright==1.56.0
python -m playwright install chromium
python tests/run.py                  # everything, about 10 minutes
python tests/run.py backup flows     # just some files
VS_FUZZ_STEPS=2000 python tests/run.py fuzz   # a longer random-tap run
```

The tests drive the real app in Chromium, served from `localhost` as GitHub Pages would serve it. Screenshots of every screen go to `tests/output/`. On GitHub they're attached to each run as **screenshots**.

| File | Covers |
|---|---|
| `test_release.py` | The version agrees in the app, README and CHANGELOG |
| `test_flows.py` | A full session with notes, the clock, Skip, editing, song practice, Toggl text and drafts |
| `test_progress.py` | The Progress chart, ranges, picking bars, time per step and the "doors" to All sessions |
| `test_edge.py` | Every bug from the 3.3.2 audit, so none come back |
| `test_data.py` | Data version upgrades and the copy kept first, backups from a newer version, Storage protection, and opening offline |
| `test_changelog.py` | The Changelog page shows every version in CHANGELOG.md, the chart, Show all, Every change, and a failed load |
| `test_backup.py` | Export, Check a backup, damaged files, restore comparison, undo, the old-backup fixtures and the exercise-id guard |
| `test_recording.py` | Recording with a fake microphone, leaving mid-take, keeping 3 takes, and audio in backups |
| `test_layout.py` | Every screen on iPhone, iPhone landscape, iPad and Mac, light and dark, plus pull to refresh |
| `test_fuzz.py` | Thousands of random taps, checking nothing breaks after each one |

Tests reach into the app through its globals (`D`, `X`, `U`, `render`…), so the script must stay a classic `<script>`, not an ES module.

---

## Releasing

`python tools/release.py 3.7` updates `APP_VERSION` and `RELEASE_DATE` in `index.html`, the README badge and "Current version" line, and adds a `## 3.7 · date` section to `CHANGELOG.md` with a placeholder headline and note. The release test fails until both are replaced with the real headline and changes.

Version numbers: **major** for a redesign, **minor** for new features, **patch** for fixes.

The app checks for a newer `APP_VERSION` on pull to refresh, so a release reaches the phone the next time Ivan pulls down on Today or Progress.

---

## Style

The app follows Apple's design language for iOS 26/27 (Liquid Glass imitated in CSS), with British English in plain, friendly words. Everything must work on iPhone, iPhone landscape, iPad and Mac, in light and dark mode.
