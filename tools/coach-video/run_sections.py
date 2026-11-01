#!/usr/bin/env python3
"""Q24 coach video kit · run_sections.py — render, check and preview several sections, N at a time.

Keeps a checkpoint log (OUTDIR/sections_log.json): each section's state (rendered, checked, previewed, copied)
so an interrupted run picks up at the next unfinished section rather than starting again.
Usage: python3 run_sections.py OUTDIR ORIGINAL.mp4 --workers 2 [--only 1,3,4]
"""
import os, sys, json, subprocess, argparse, threading, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('outdir'); ap.add_argument('original')
ap.add_argument('--workers', type=int, default=2)
ap.add_argument('--only', default='')
a = ap.parse_args()
LOG = os.path.join(a.outdir, 'sections_log.json')
IDS = ['slides', 'humming', 'lip', 'falsetto', 'upperlower', 'straw', 'rung', 'hinge', 'half', 'vertical', 'nasal', 'flex']
lock = threading.Lock()

def load():
    return json.load(open(LOG)) if os.path.exists(LOG) else {}
def mark(sec, **kw):
    with lock:
        d = load(); e = d.setdefault(str(sec), {'id': IDS[sec - 1]}); e.update(kw); e['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        json.dump(d, open(LOG, 'w'), indent=1)

def job(sec):
    name = f'{sec:02d}_{IDS[sec - 1]}'
    mov = os.path.join(a.outdir, name + '.mov')
    st = load().get(str(sec), {})
    if not st.get('rendered'):
        r = subprocess.run([sys.executable, os.path.join(HERE, 'render_section.py'), str(sec), a.outdir],
                           stdout=open(os.path.join(a.outdir, name + '_render.log'), 'w'), stderr=subprocess.STDOUT)
        if r.returncode: mark(sec, rendered=False, error='render failed'); return sec, False
        mark(sec, rendered=True, file=os.path.basename(mov), bytes=os.path.getsize(mov))
    r = subprocess.run([sys.executable, os.path.join(HERE, 'check_section.py'), str(sec), mov, os.path.join(a.outdir, 'checks')],
                       capture_output=True, text=True)
    mark(sec, checked=(r.returncode == 0))
    subprocess.run([sys.executable, os.path.join(HERE, 'preview.py'), str(sec), mov, a.original,
                    os.path.join(a.outdir, 'previews', name + '_preview.mp4')], capture_output=True)
    mark(sec, previewed=True)
    return sec, r.returncode == 0

os.makedirs(os.path.join(a.outdir, 'previews'), exist_ok=True)
secs = [int(x) for x in a.only.split(',')] if a.only else [s for s in range(1, 13) if not load().get(str(s), {}).get('checked')]
with ThreadPoolExecutor(a.workers) as ex:
    for sec, ok in ex.map(job, secs):
        print(f'section {sec:02d}: {"checked" if ok else "CHECK FAILED"}', flush=True)
