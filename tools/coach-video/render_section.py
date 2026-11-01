#!/usr/bin/env python3
"""Q24 coach video kit · render_section.py

Renders one exercise section of the redesigned coach video, 1920 x 1080 at 24 fps, no audio.
Each section starts on its exercise's boundary frame and ends on the frame before the next.

Speed-ups (Ivan, 1 Nov 2026):
  * frame reuse: a frame is only drawn when the slide's HTML changes; otherwise the last one is repeated
  * motion blur (film-style shutter, sub-frames averaged) only in the transition windows

Usage:
  python3 render_section.py SECTION OUTDIR [--from N --to M]   SECTION is 1-12 (video order)
Writes OUTDIR/NN_<id>.mov (H.264, yuv420p, BT.709) and OUTDIR/NN_<id>.json (stats).
"""
import sys, os, json, time, base64, io, subprocess, argparse
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('section', type=int)
ap.add_argument('outdir')
ap.add_argument('--from', dest='f0', type=int, default=None, help='first frame, relative to the section')
ap.add_argument('--to', dest='f1', type=int, default=None, help='end frame (exclusive), relative to the section')
ap.add_argument('--crf', type=int, default=12)
a = ap.parse_args()

data = json.loads(open(os.path.join(HERE, 'data.js')).read().split('window.DATA=', 1)[1].rstrip().rstrip(';'))
FPS = data['fps']
lv = data['levels']
s = a.section - 1
ex = data['exercises'][s]
start = lv[s * 3]['startFrame']
end = lv[s * 3 + 3]['startFrame'] if s < 11 else data['totalFrames']
f0 = a.f0 or 0
f1 = a.f1 if a.f1 is not None else end - start
name = f"{a.section:02d}_{ex['id']}"
os.makedirs(a.outdir, exist_ok=True)
out = os.path.join(a.outdir, name + ('' if (f0 == 0 and f1 == end - start) else f'_{f0}-{f1}') + '.mov')

W, H = 1920, 1080
enc = subprocess.Popen([
    'ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', str(a.crf), '-g', '48', '-bf', '2',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-movflags', '+faststart', out], stdin=subprocess.PIPE)

t_start = time.time()
stats = {'section': a.section, 'id': ex['id'], 'name': ex['name'], 'startFrame': start, 'endFrame': end,
         'from': f0, 'to': f1, 'frames': 0, 'drawn': 0, 'reused': 0, 'subframes': 0}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--force-color-profile=srgb', '--disable-lcd-text', '--font-render-hinting=none'])
    p = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
    errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto('file://' + os.path.join(HERE, 'slide.html'))
    info = p.evaluate('window.ready')
    stats['measure'] = info
    cdp = p.context.new_cdp_session(p)

    def shot():
        r = cdp.send('Page.captureScreenshot', {'format': 'png', 'optimizeForSpeed': True})
        return np.asarray(Image.open(io.BytesIO(base64.b64decode(r['data']))).convert('RGB'))

    last = None
    for i in range(f0, f1):
        t = (start + i) / FPS
        S = p.evaluate('t => window.info(t).blur', t)
        if S > 1:
            acc = None
            for k in range(S):
                tt = t + k / (FPS * 2 * (S - 1))      # a 180-degree shutter
                p.evaluate('t => window.frame(t)', tt)
                img = shot().astype(np.float32)
                acc = img if acc is None else acc + img
            p.evaluate('t => window.force(t)', t)      # leave the DOM at the frame time for the next comparison
            last = (acc / S + 0.5).astype(np.uint8)
            stats['drawn'] += 1; stats['subframes'] += S
        else:
            changed = p.evaluate('t => window.frame(t)', t)
            if changed or last is None:
                last = shot(); stats['drawn'] += 1; stats['subframes'] += 1
            else:
                stats['reused'] += 1
        enc.stdin.write(last.tobytes())
        stats['frames'] += 1
        if i % 480 == 0:
            el = time.time() - t_start
            print(f'{name} frame {i}/{f1} drawn {stats["drawn"]} reused {stats["reused"]} {el:.0f}s', flush=True)
    b.close()
enc.stdin.close(); enc.wait()
stats['seconds'] = round(time.time() - t_start, 1)
stats['errors'] = errs
stats['file'] = out
json.dump(stats, open(out[:-4] + '.json', 'w'), indent=1)
print('DONE', json.dumps({k: stats[k] for k in ('frames', 'drawn', 'reused', 'subframes', 'seconds')}), out, flush=True)
if errs: print('PAGE ERRORS', errs); sys.exit(1)
