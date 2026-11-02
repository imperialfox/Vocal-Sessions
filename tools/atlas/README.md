# Visual App Atlas (Q30)

Every screen and sheet of Vocal Sessions as saved screenshots, side by side, with where each button goes. A developer tool: the app itself doesn't change, and there's no app version. The map, notes, export and "changes since the last scan" come in Q31.

**The screenshots are saved, not live.** They come from a scan of the app with sample data, and the viewer says so wherever it matters.

## Use

```
python3 tools/atlas/atlas.py             # scan, then open the Atlas in your browser (about 5–10 minutes)
python3 tools/atlas/atlas.py --view      # open the last scan again, without scanning
python3 tools/atlas/atlas.py --no-open   # scan only
python3 tools/atlas/test_atlas.py        # the Atlas's own tests (about 2 minutes)
```

Needs the tests' Playwright, once: `pip install playwright==1.56.0` then `python3 -m playwright install chromium`. Run from anywhere; on the Mac, Ctrl+C stops the viewer.

From a Claude chat, say **"rescan the Atlas"**: Claude runs the scan in its own workspace and updates the private Atlas page on claude.ai.

## Files

| File | What it is |
|---|---|
| `atlas.py` | The command: scans into `data/scans/<date-time>/`, puts the viewer beside it and opens it |
| `scan.py` | The scanner: opens the app in headless Chromium, captures each screen, taps its buttons, writes `atlas.json` |
| `inventory.py` | Reads the code and docs with no browser: every screen the code can show, the doc sections with their GitHub addresses, the changelog |
| `screens.py` | What the scan needs to know about Vocal Sessions: where it starts, areas, names, which doc sections explain what, buttons never tapped |
| `viewer.html` | The Lightbox page (one file); reads `atlas.json` and `shots/` next to it |
| `test_atlas.py` | Tests for all of the above |
| `data/` | Scans. **Git-ignored**: screenshots never go into the repo, which is public |

## How a scan works

1. **Sample data only.** Each screen is opened in a fresh, throwaway browser filled with the tests' sample data (`tests/harness.py`) plus one song with lyrics, sections, marks, three takes and a generated track (`tests/test_layout.py`, `tests/test_track.py`). Never your real data.
2. **Clock frozen, motion off.** The clock is fixed at 2 Nov 2026, 10:00 London time, so dates and "2 days ago" never show up as changes between scans.
3. **Starting screens** (`screens.ROOTS`): the tabs, through their real buttons, plus first launch, a session running, Today in dark mode, the song page with its track and takes (and a section selected), and the session's Rotation and Application steps.
4. **Every button is tapped** on a copy put back exactly as it was before each tap: nothing recording or playing, fresh screen state, saved data, settings and session restored, the Songs screen's menus closed. If the screen's buttons still don't match the first capture, a fresh copy of the app is started.
5. **Whatever a tap opens that isn't captured yet is captured next, through that same button**, so screens are reached the way you'd reach them (opening the calendar by a shortcut once made its month arrows look broken). This repeats until nothing new turns up.
6. **The code's list.** `inventory.py` lists every screen in `render()`, every sheet in `renderSheet()` and the functions it hands sheets to, Settings' pages, and every `U.tab`, `U.view`, `U.sheet` the code sets. Anything no tap reached is shown as **Not captured yet**. Compared with the last scan's list, anything gone from the code is shown as **Gone from the code**.

**Rules** (agreed at Render, 2 Nov 2026):
- A sheet that didn't open is **Failed**, with the reason, never captured as the screen underneath. A failed capture keeps no picture.
- Buttons that need the microphone or a file, save or share a file, replace your data, or delete or clear something are **Not tested**, with the reason, never "Broken". A button that only opens a confirmation sheet is tapped (opening it is safe; its confirm button isn't).
- Buttons that only show after a swipe or a hold: **Not tested**, saying so. Buttons another layer covers get a **forced tap** (the button itself is tapped), marked as one.
- Link statuses: **Seen working** · **Changes this screen** · **Not tested** (with the reason) · **Broken** (tapping threw an error).
- The same screen in another state (first launch, session running, dark) shares its screen's entry for links. Other exercises and guide pages point to the captured one as "same page layout".

## atlas.json

`scan` (when, version, commit, screen size, the frozen clock, `codeChanges` since the last scan), `areas`, `inventory` (the code's list) and `screens`. Each screen: `id`, `title`, `area`, `kind` (Tab · Screen · Sub-page · Sheet · State), `key` (its place in the code's list), `status` (captured · failed · uncaptured · gone), `why`, `errors`, `shot` and `full` (pictures), `links` (each button: label, action, how, why, where it went, `forced`), `from`, `docs` ("Explained in"), `mention` (the last changelog headline that names it), `via` and `how` (the buttons that open it). Q31 compares one scan's `atlas.json` with the last.
