# Visual App Atlas

Every screen and sheet of Vocal Sessions as saved screenshots, with where each button goes, a **map** of how they link, **notes** on any part of a screen that Claude can read, an **export** for Claude, and **what changed since the last scan**. On a phone it's made for a thumb: pinch to zoom, swipes and a bottom bar. A developer tool: the app itself doesn't change, and there's no app version.

**The screenshots are saved, not live.** They come from a scan of the app with sample data, and the viewer says so wherever it matters.

It runs on the **Atlas kit** (`imperialfox/atlas-kit`), one Atlas for any app: this folder holds only what's particular to Vocal Sessions, plus a pinned copy of the kit.

**Atlas kit version: 1.1.0** (3 Nov 2026) · [its changelog](kit/CHANGELOG.md) · [its README](kit/README.md)

## Use

```
python3 tools/atlas/atlas.py             # scan, then open the Atlas in your browser (about 5–10 minutes)
python3 tools/atlas/atlas.py --view      # open the last scan again, without scanning
python3 tools/atlas/atlas.py --no-open   # scan only
python3 tools/atlas/test_atlas.py        # the Atlas's own tests (about a minute)
```

Needs the tests' Playwright and Pillow, once: `pip install playwright==1.56.0 pillow` then `python3 -m playwright install chromium`. Run from anywhere; on the Mac, Ctrl+C stops the viewer. Every option of the kit's `atlas.py` works here (`--quick`, `--only`, `--proposed`, `--baselines`; see [kit/README › Use](kit/README.md#use)).

From a Claude chat, say **"rescan the Atlas"**: Claude runs the scan in its own workspace and updates the private Atlas page on claude.ai. Say **"check my notes"** and Claude reads the notes you left on that page (and on any prototype listed there).

## The Atlas page and notes

- **One home:** the private page "Atlas · Vocal Sessions" on claude.ai, with its store declared (everyone signed in who can open it reads; only Ivan writes). Notes, the map layout and listed prototypes live there, in note format v1 ([kit/SHARED.md](kit/SHARED.md)). **Notes never go into git.** Only notes sent with "Copy as queue ideas" reach the repo, as text, in [RENDER_QUEUE.md › Not scheduled](../../RENDER_QUEUE.md#not-scheduled), each with a priority checked against the app's purpose.
- **Keyed by screen ID** (`VS-001`…, from `js/register.js`, Q36), so a note stays on its screen and part after a rename or a redesign. States share their screen's ID: `VS-001~dark-mode`.
- **Changes since the last scan** never claim which release caused a change; they list the versions released in between.

## Files

| File | What it is |
|---|---|
| `atlas.py` | The command: the kit's `atlas.py` with this folder's settings. Scans into `data/scans/<date-time>/`, puts the viewer beside it and opens it |
| `screens.py` | Vocal Sessions' settings for the kit: how to open the app with sample data, where the scan starts, how to tell screens apart and put the app back after a tap, the code's list of screens, areas, names, doc sections, the screen register and the buttons never tapped |
| `test_atlas.py` | Tests for the settings, the kit copy, a scan of a copy of the app, and the viewer with notes |
| `kit/` | The Atlas kit, **a pinned, unmodified copy** (no submodule). Never edit it here: change the kit in its own repo, release it, then copy the release in |
| `kit.sha256` | The copy's files and their checksums, so the tests can tell it's unmodified |
| `data/` | Scans. **Git-ignored**: screenshots never go into the repo, which is public |

**Updating the kit:** copy a newer release's `atlas.py`, `atlas_kit/`, `viewer.html`, `README.md`, `CHANGELOG.md`, `LICENSE.txt` and `SHARED.md` into `kit/`, run `(cd tools/atlas && sha256sum $(cd kit && find . -type f ! -path '*/__pycache__/*' | sort | sed 's|^\./|kit/|') > kit.sha256)`, update the version line above, and run the tests.

## How a scan works

1. **Sample data only.** Each screen is opened in a fresh, throwaway browser filled with the tests' sample data (`tests/harness.py`) plus one song with lyrics, sections, marks, three takes and a generated track (`tests/test_layout.py`, `tests/test_track.py`). Never your real data.
2. **Clock frozen, motion off, screens settled.** The clock is fixed at 2 Nov 2026, 10:00 London time, so dates and "2 days ago" never show up as changes between scans. Each screen is read (and pictured) only once it has stopped moving: animations finished, any looping one held on its first frame, and an open sheet's place, size and corners steady for three frames. Without that, sheets caught still rising landed a point apart from one scan to the next, and a rescan of an unchanged app called about 20 of them "looks different".
3. **Starting screens** (`ROOTS` in `screens.py`): the tabs, through their real buttons, plus first launch, a session running, Today in dark mode, the song page with its track and takes (and a section selected), and the session's Rotation and Application steps.
4. **Every button is tapped** on a copy put back exactly as it was before each tap: nothing recording or playing, fresh screen state, saved data, settings and session restored, the Songs screen's menus closed. If the screen's buttons still don't match the first capture, a fresh copy of the app is started.
5. **Whatever a tap opens that isn't captured yet is captured next, through that same button**, so screens are reached the way you'd reach them. This repeats until nothing new turns up.
6. **The code's list** (`inventory()` in `screens.py`): every screen in `render()`, every sheet in `renderSheet()` and the functions it hands sheets to, Settings' pages, and every `U.tab`, `U.view`, `U.sheet` the code sets. Anything no tap reached is shown as **Not captured yet**; compared with the last scan, anything gone from the code is listed too.
7. **Screen IDs** are read off each screen (`data-screen`, and `data-name` for its parts). A captured screen with no register entry is flagged "No ID yet · suggested VS-0xx" (the register changes only in an app build); a register entry no screen showed is "Not found this scan", never deleted.

**Rules** (agreed at Render, 2 Nov 2026):
- A sheet that didn't open is **Failed**, with the reason, never captured as the screen underneath. A failed capture keeps no picture.
- Buttons that need the microphone or a file, save or share a file, replace your data, or delete or clear something are **Not tested**, with the reason, never "Broken". A button that only opens a confirmation sheet is tapped (opening it is safe; its confirm button isn't).
- Buttons that only show after a swipe or a hold: **Not tested**, saying so. Buttons another layer covers get a **forced tap** (the button itself is tapped), marked as one.
- Link statuses: **Seen working** · **Changes this screen** · **Not tested** (with the reason) · **Broken** (tapping threw an error).
- The same screen in another state (first launch, session running, dark) shares its screen's entry for links. Other exercises and guide pages point to the captured one as "same page layout".

**Not yet:** Vocal Sessions' own flows, captions and hand-written doors (the kit can show them) come with Q35.

## atlas.json

The kit's format: [kit/README › atlas.json](kit/README.md#atlasjson).
