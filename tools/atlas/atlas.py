"""Visual App Atlas · Vocal Sessions: every screen and sheet as saved screenshots, the map, notes and changes.

    python3 tools/atlas/atlas.py             scan the app, then open the Atlas in your browser
    python3 tools/atlas/atlas.py --view      open the last scan again, without scanning
    python3 tools/atlas/atlas.py --no-open   scan only (what Claude runs before updating the private Atlas page)
    python3 tools/atlas/atlas.py --quick     capture the starting screens without tapping their buttons (fast, finds fewer screens)
    python3 tools/atlas/atlas.py --workers 4 how many browsers scan side by side (default: the processor count, up to 6)

The Atlas kit's command (kit/atlas.py) with Vocal Sessions' settings (screens.py); every option of the kit's works here.
Needs the tests' Playwright (pip install playwright==1.56.0, then python3 -m playwright install chromium) and Pillow.
Scans go in tools/atlas/data/scans/<date-time>/ (atlas.json, shots/ and the viewer as index.html). Every scan is kept,
so the next one can be compared with it. tools/atlas/data/ is never committed: the repo is public.
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, 'kit')

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--settings' not in args: args = ['--settings', os.path.join(HERE, 'screens.py')] + args
    sys.argv = [os.path.join(KIT, 'atlas.py')] + args
    sys.path[0] = KIT   # the kit's own folder first, as when it runs by itself
    runpy.run_path(os.path.join(KIT, 'atlas.py'), run_name='__main__')
