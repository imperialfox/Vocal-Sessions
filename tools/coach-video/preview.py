#!/usr/bin/env python3
"""Q24 coach video kit · preview.py — a short quick-look clip of one section, with the original audio.

Clips: the section's start (title moment), each level change, and the green completion into the end.
960 x 540, so it's light enough to watch on a phone.
Usage: python3 preview.py SECTION SECTION.mov ORIGINAL.mp4 OUT.mp4
"""
import sys, os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sec, mov, orig, out = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
data = json.loads(open(os.path.join(HERE, 'data.js')).read().split('window.DATA=', 1)[1].rstrip().rstrip(';'))
lv = data['levels']; s = sec - 1
start = lv[s * 3]['startFrame']
end = lv[s * 3 + 3]['startFrame'] if s < 11 else data['totalFrames']
n = end - start
L2, L3 = lv[s * 3 + 1]['startFrame'] - start, lv[s * 3 + 2]['startFrame'] - start
# each clip runs on past the first pill change after its start (where the practice begins), plus 6 s
def past_first_change(k, a_rel):
    l = lv[s * 3 + k]; t0 = (start + a_rel) / 24
    ch = [st[0] for st in l['states'][1:] if st[0] > t0 + 1]
    t = ch[0] if ch else t0 + 8
    return int(round((t - start / 24) * 24)) + 6 * 24
cuts = [(0, max(9 * 24, past_first_change(0, 0))), (L2 - 6 * 24, max(L2 + 5 * 24, past_first_change(1, L2))),
        (L3 - 6 * 24, max(L3 + 5 * 24, past_first_change(2, L3))), (n - 12 * 24, n)]
inputs, fc, k = [], [], 0
for a, b in cuts:
    a = max(0, a); b = min(n, b)
    ta, tb = a / 24, b / 24
    oa = (start + a) / 24
    inputs += ['-ss', f'{ta:.4f}', '-t', f'{tb - ta:.4f}', '-i', mov, '-ss', f'{oa:.4f}', '-t', f'{tb - ta:.4f}', '-i', orig]
    fc.append(f'[{2*k}:v]scale=960:540,setsar=1,fps=24[v{k}];[{2*k+1}:a]aresample=48000,afade=t=in:d=0.05,afade=t=out:st={tb-ta-0.08:.3f}:d=0.08[a{k}]')
    k += 1
fc.append(''.join(f'[v{i}][a{i}]' for i in range(k)) + f'concat=n={k}:v=1:a=1[v][a]')
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart', out], check=True)
print('preview', out)
