#!/usr/bin/env python3
"""Q24 coach video kit · check_section.py

Checks one rendered section against the measured level frames of the original video:
  * frame count and length
  * each level change: the blue wipe starts on the level's start frame (within one frame)
  * the exercise change: the new page starts pushing in on the section's first frame
  * the green completion starts 1 s (24 frames) before the section's end
Also writes a contact sheet and an energy trace (how much each frame changes) as PNGs.

Usage: python3 check_section.py SECTION FILE.mov OUTDIR
Exit code 0 = all checks passed.
"""
import sys, os, json, subprocess
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sec, path, outdir = int(sys.argv[1]), sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
data = json.loads(open(os.path.join(HERE, 'data.js')).read().split('window.DATA=', 1)[1].rstrip().rstrip(';'))
lv, ex = data['levels'], data['exercises']
s = sec - 1
start = lv[s * 3]['startFrame']
end = lv[s * 3 + 3]['startFrame'] if s < 11 else data['totalFrames']
n_exp = end - start
lvl = [lv[s * 3 + k]['startFrame'] - start for k in range(3)]   # 0, L2, L3 (section-relative)
green = n_exp - 24
W, H = 480, 270
sc = W / 1920

def hexrgb(c): return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32)

# frames we keep for the sheet and the checks
keep = set()
for c in (0, lvl[1], lvl[2], green):
    keep.update(range(max(0, c - 8), min(n_exp, c + 16)))
sheet_at = sorted(set([0, 6, 12, 48, 80, 120, lvl[1] // 2, lvl[1] - 24, lvl[1] + 4, lvl[1] + 13, lvl[1] + 48,
                       (lvl[1] + lvl[2]) // 2, lvl[2] - 24, lvl[2] + 4, lvl[2] + 13, lvl[2] + 48,
                       (lvl[2] + n_exp) // 2, n_exp - 200, green + 6, n_exp - 1]))
keep.update(sheet_at)
proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={W}:{H}:flags=area', '-f', 'rawvideo',
                         '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
kept, energy, prev, n = {}, [], None, 0
fs = W * H * 3
while True:
    b = proc.stdout.read(fs)
    if len(b) < fs: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    ff = f.astype(np.float32)
    energy.append(0.0 if prev is None else float(np.abs(ff - prev).mean()))
    prev = ff
    if n in keep: kept[n] = f.copy()
    n += 1
proc.wait()

res = {'section': sec, 'id': ex[s]['id'], 'frames': n, 'expected': n_exp, 'checks': []}
def check(name, ok, detail):
    res['checks'].append({'check': name, 'ok': bool(ok), 'detail': detail})

check('frame count', n == n_exp, f'{n} frames, expected {n_exp}')

def region(f, x0, x1, y0, y1):
    return f[int(y0 * sc):int(y1 * sc), int(x0 * sc):int(x1 * sc)].astype(np.float32)

def first_change(c, x0, x1, y0, y1, thr=0.6):
    base = region(kept[c - 6], x0, x1, y0, y1)
    for k in range(c - 5, c + 12):
        if k in kept and np.abs(region(kept[k], x0, x1, y0, y1) - base).mean() > thr:
            return k
    return None

# level wipes: the card's left edge (x 88-140) picks up the blue tint as the wipe starts
for k, c in ((2, lvl[1]), (3, lvl[2])):
    got = first_change(c, 90, 150, 300, 820)
    ok = got is not None and 0 <= got - c <= 1
    check(f'level {k} wipe', ok, f'wipe first seen at section frame {got}, level starts at {c} (video frame {c + start})')
# green completion, 24 frames before the end
got = first_change(green, 90, 150, 300, 820)
check('green completion', got is not None and 0 <= got - green <= 1, f'first seen at {got}, expected {green}')
# exercise change: frame 0 shows the old page's rim at the right edge, then the new page pushes in
rim_new = hexrgb(ex[s]['rim'])
if s == 0:
    c0 = kept[0][int(540 * sc), -2].astype(np.float32)
    check('first frame', np.abs(c0 - rim_new).max() < 30, f'right edge {c0.astype(int).tolist()} vs rim {rim_new.astype(int).tolist()}')
else:
    rim_old = hexrgb(ex[s - 1]['rim'])
    c0 = kept[0][int(540 * sc), int(1890 * sc)].astype(np.float32)   # frame 0: still the old page's rim
    c1 = kept[1][int(540 * sc), -1].astype(np.float32)               # frame 1: the new page has started to cover the right edge (motion-blurred, so compare with frame 0)
    check('page push starts on frame 0', np.abs(c0 - rim_old).max() < 30 and np.abs(c1 - c0).max() > 60,
          f'frame 0 at x1890 {c0.astype(int).tolist()} (old {rim_old.astype(int).tolist()}), frame 1 right edge {c1.astype(int).tolist()} (new {rim_new.astype(int).tolist()})')
res['passed'] = all(c['ok'] for c in res['checks'])

name = f'{sec:02d}_{ex[s]["id"]}'
# contact sheet, 4 across, with labels
cols = 4; rows = (len(sheet_at) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W, rows * (H + 22)), 'white'); d = ImageDraw.Draw(sheet)
for i, fr in enumerate(sheet_at):
    if fr not in kept: continue
    x, y = (i % cols) * W, (i // cols) * (H + 22)
    sheet.paste(Image.fromarray(kept[fr]), (x, y + 22))
    t = (start + fr) / 24
    d.text((x + 6, y + 5), f'frame {fr} · video {int(t // 60)}:{t % 60:05.2f}', fill='black')
sheet.save(os.path.join(outdir, name + '_sheet.png'))
# energy trace
E = np.array(energy); w = 1600; h = 300
img = Image.new('RGB', (w, h + 30), 'white'); d = ImageDraw.Draw(img)
mx = max(1e-6, np.percentile(E, 99.9))
for x in range(w):
    a0, a1 = int(x * n / w), max(int(x * n / w) + 1, int((x + 1) * n / w))
    v = E[a0:a1].max() if a1 > a0 else 0
    d.line([(x, h), (x, h - min(1, v / mx) * (h - 10))], fill=(0, 122, 255))
for c, lab in ((lvl[1], 'L2'), (lvl[2], 'L3'), (green, 'green')):
    x = int(c / n * w); d.line([(x, 0), (x, h)], fill=(255, 59, 48)); d.text((x + 3, h + 8), lab, fill='black')
d.text((4, h + 8), f'{name}: per-frame change (max {E.max():.2f}); red = level change / green completion', fill='black')
img.save(os.path.join(outdir, name + '_energy.png'))
res['energy_still_frames'] = int((E < 0.01).sum())
json.dump(res, open(os.path.join(outdir, name + '_check.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
sys.exit(0 if res['passed'] else 1)
