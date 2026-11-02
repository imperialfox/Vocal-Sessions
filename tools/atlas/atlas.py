"""Visual App Atlas (Q30): every screen and sheet of Vocal Sessions as saved screenshots, side by side.

    python3 tools/atlas/atlas.py             scan the app, then open the Atlas in your browser
    python3 tools/atlas/atlas.py --view      open the last scan again, without scanning
    python3 tools/atlas/atlas.py --no-open   scan only (what Claude runs before updating the private Atlas page)
    python3 tools/atlas/atlas.py --quick     capture the screens without tapping their buttons (fast, finds fewer screens)
    python3 tools/atlas/atlas.py --workers 4 how many browsers scan side by side (default: the processor count, up to 6)

Needs the tests' Playwright (pip install playwright==1.56.0, then python3 -m playwright install chromium).
Scans go in tools/atlas/data/scans/<date-time>/ (atlas.json, shots/ and the viewer as index.html). Every scan is kept,
so the next one can be compared with it. tools/atlas/data/ is never committed: the repo is public.
"""
import os, sys, glob, json, shutil, argparse, datetime as dt, functools, threading, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(HERE, 'data')
SCANS = os.path.join(DATA, 'scans')
sys.path.insert(0, HERE)


def scans():
    """Finished scans, oldest first."""
    return sorted(d for d in glob.glob(os.path.join(SCANS, '*')) if os.path.exists(os.path.join(d, 'atlas.json')))


def put_viewer(folder):
    shutil.copy(os.path.join(HERE, 'viewer.html'), os.path.join(folder, 'index.html'))


def serve(folder, open_browser=True):
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=folder))
    url = f'http://localhost:{srv.server_address[1]}/'
    print(f'The Atlas is at {url}  (Ctrl+C to stop)')
    if open_browser: threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: print('\nStopped.')


def main(argv=None):
    ap = argparse.ArgumentParser(description='Visual App Atlas: scan Vocal Sessions and show every screen.')
    ap.add_argument('--view', action='store_true', help='open the last scan without scanning')
    ap.add_argument('--no-open', action='store_true', help='scan only; don’t start the viewer')
    ap.add_argument('--quick', action='store_true', help='don’t tap buttons (only the starting screens are captured)')
    ap.add_argument('--workers', type=int, default=min(6, os.cpu_count() or 2))
    ap.add_argument('--only', help='comma-separated starting screens (for checking a few)')
    ap.add_argument('--app', default=REPO, help='the app folder to scan (default: this repo)')
    ap.add_argument('--out', help='where to write the scan (default: a new folder under tools/atlas/data/scans/)')
    a = ap.parse_args(argv)

    if a.view:
        done = scans()
        if not done: sys.exit('No scans yet. Run python3 tools/atlas/atlas.py first.')
        put_viewer(done[-1]); serve(done[-1]); return

    import scan as SC
    prev = scans()[-1] if scans() else None
    sid = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = os.path.abspath(a.out) if a.out else os.path.join(SCANS, sid)
    os.makedirs(out, exist_ok=True)
    print(f'Scanning {a.app} into {out}')
    SC.scan(a.app, out, workers=a.workers, taps=not a.quick, only=set(a.only.split(',')) if a.only else None,
            prev=prev, scan_id=sid)
    put_viewer(out)
    if not a.no_open: serve(out)


if __name__ == '__main__':
    main()
