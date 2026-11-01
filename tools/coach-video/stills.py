#!/usr/bin/env python3
"""Q24 kit · stills.py — save single frames at given times (seconds) for a look. Usage: stills.py OUTDIR t1 t2 ..."""
import sys, os
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); out=sys.argv[1]; ts=[float(x) for x in sys.argv[2:]]
os.makedirs(out,exist_ok=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(args=['--force-color-profile=srgb']); p=b.new_page(viewport={'width':1920,'height':1080})
    errs=[]; p.on('pageerror',lambda e:errs.append(str(e)))
    p.goto('file://'+os.path.join(HERE,'slide.html')); print(p.evaluate('window.ready'))
    for t in ts:
        p.evaluate('t=>window.force(t)',t); p.screenshot(path=f'{out}/t{t:09.3f}.png')
    b.close()
print('errors',errs)
