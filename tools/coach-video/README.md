# Coach video render kit (Q24)

Renders the redesigned coach video graphics: 12 exercises, 36 levels, 1920 × 1080 at 24 fps. The graphics sit over the original coach audio, which is never changed. **No media or fonts live here.** The original video and Ivan's SF Pro font files stay on his Mac (`~/Movies/Coach Video Redesign`).

## Files

| File | What it is |
|---|---|
| `content.json` | The approved wording for all 36 levels: the line to do, up to three facts, syllables, and the rim (original video) colour |
| `data/audio_timeline.json` | Pill states (Your turn / With coach / Listen) and rounds, from the audio pass (1 Nov 2026) |
| `data/level_frames.json` | The 36 level-start frames, measured frame by frame from the original's green flash |
| `data/markers.json`, `data/chapters.ffmetadata` | The same 36 starts as Resolve markers and as MP4 chapters |
| `build_data.js` | Builds `data.js` from the above, plus `FOCUS_COL` and `GLYPH` from `js/config.js`, so the tile matches the app |
| `slide.html` | The slide (still v4 + clip v2 motion). `frame(t)` draws any moment from the time alone |
| `render_section.py` | Renders one exercise section, reusing frames when nothing changes and adding motion blur only in transitions |
| `check_section.py` | Checks a section: frame count, each level wipe on its start frame (±1), the push on frame 0, and the green 1 s before the end. Also makes a contact sheet and an energy trace |
| `preview.py` | A short quick look with the original audio |
| `run_sections.py` | Renders, checks and previews sections N at a time, with a checkpoint log (`sections_log.json`) |
| `stills.py` | Single frames at given times, for a look |

## Use

```
node build_data.js                     # once, or after changing content, timeline or app colours
python3 run_sections.py OUT "Vocal coach video 2.mp4" --workers 2
python3 run_sections.py OUT "Vocal coach video 2.mp4" --only 7   # re-render one section after a fix
```

Needs Python with Playwright, NumPy and Pillow, plus ffmpeg, and SF Pro installed as a system font ("SF Pro", variable).

## Finishing (DaVinci Resolve, Ivan's Mac)

- **Timeline** "Q24 Coach Video Redesign", in the project "Vocal Excersise video", starting at 00:00:00:00.
  - V2: the 12 sections, each placed on its start frame (no gaps).
  - V1 and A1: the original video, under the sections as a sync reference, with its audio.
- **Markers:** 36 markers at the level starts. The 12 exercise starts are blue and the other levels are green.
- **Export:** H.264 MP4, 1080p24, with the video capped at 600 kb/s.
- **After export:** the audio is replaced by a stream copy of the original's audio (bit-for-bit identical), and the 36 chapters are added from `data/chapters.ffmetadata`. Both are done with ffmpeg, using `-c copy`.
