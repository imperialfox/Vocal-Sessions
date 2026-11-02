"""Tests for the Visual App Atlas (Q30): the scanner and the viewer.

    python3 tools/atlas/test_atlas.py            everything (about 2 minutes)
    python3 tools/atlas/test_atlas.py code docs  only some parts: code, docs, rules, git, scan, viewer

Not part of the app's suite (tests/run.py), so GitHub's test run stays as long as it was. Uses the tests' Playwright
(1.56.0) and TZ=Europe/London, like the app's tests. Everything is made in a temporary folder; nothing is left behind.
"""
import os, re, sys, json, shutil, tempfile, subprocess, functools, threading, struct, zlib
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import inventory as INV
import screens as S

PASSED, FAILS = 0, []
def ok(cond, msg):
    global PASSED
    if cond: PASSED += 1
    else: FAILS.append(msg)
    print(('  pass  ' if cond else '  FAIL  ') + msg, flush=True)


def app_copy(tmp):
    """A copy of the app (page, code, styles, docs, tests' helpers) to change safely."""
    dst = os.path.join(tmp, 'app')
    os.makedirs(dst)
    for f in ('index.html', 'sw.js', 'icon.png', 'CHANGELOG.md', 'README.md', 'MAINTAINING.md'):
        shutil.copy(os.path.join(REPO, f), dst)
    for d in ('js', 'css', 'splash'):
        shutil.copytree(os.path.join(REPO, d), os.path.join(dst, d))
    os.makedirs(os.path.join(dst, 'tests'))
    for f in ('harness.py', 'test_layout.py', 'test_track.py'):
        shutil.copy(os.path.join(REPO, 'tests', f), os.path.join(dst, 'tests'))
    os.makedirs(os.path.join(dst, 'tests', 'fixtures'), exist_ok=True)
    return dst


def add_dummy(app):
    """A dummy screen in render() and a dummy sheet in renderSheet(), as a new feature would add them."""
    p = os.path.join(app, 'js', 'ui.js'); s = open(p, encoding='utf-8').read()
    s2 = s.replace("    v === 'log'\n      ? scrLog()", "    v === 'atlasDummy'\n      ? scrLog()\n      : v === 'log'\n      ? scrLog()", 1)
    s2 = s2.replace("  if (s && /^sg[A-Z]/.test(s)) h = songSheet(s);", "  if (s === 'atlasDummySheet') h = '';\n  else if (s && /^sg[A-Z]/.test(s)) h = songSheet(s);", 1)
    assert s2 != s and s2.count('atlasDummy') == 2, 'the dummy screen could not be added (render() changed shape?)'
    open(p, 'w', encoding='utf-8').write(s2)


# ---------- code ----------
def t_code():
    print('The screen list comes from the code')
    inv = INV.inventory(REPO)
    ui = open(os.path.join(REPO, 'js', 'ui.js'), encoding='utf-8').read()
    r = INV.function_body(ui, 'render'); rs = INV.function_body(ui, 'renderSheet')
    ok(len(r) > 500 and len(rs) > 500, 'render() and renderSheet() are found in js/ui.js')
    views = set(re.findall(r"v === '(\w+)'", r)); sheets = set(re.findall(r"s === '(\w+)'", rs))
    ok(views and all('Screen:' + v in inv for v in views), f'every screen named in render() is listed ({len(views)})')
    ok(sheets and all('Sheet:' + s in inv for s in sheets), f'every sheet named in renderSheet() is listed ({len(sheets)})')
    tabs = re.search(r"\{([^{}]*)\}\[U\.tab\]", r)
    ok(tabs and all('Tab:' + t in inv for t in re.findall(r'(\w+):', tabs.group(1))), 'every tab in render()’s tab table is listed')
    ok(any(v['where'].endswith('songSheet()') for v in inv.values()) and 'Sheet:sgKey' in inv, 'sheets renderSheet() hands to songSheet() are listed')
    ok(any('sheet()' in v['where'] for v in inv.values()) and 'Sheet:trkMenu' in inv, 'and those it hands to the track player’s sheet()')
    ok('Sheet:sgRenIn' not in inv, 'a field id that looks like a sheet name isn’t listed')
    ok(all('Sub-page:' + k in inv for k in ('backup', 'storage', 'recall', 'coach', 'appear', 'access')), 'Settings’ pages are listed')
    with tempfile.TemporaryDirectory() as tmp:
        app = app_copy(tmp); add_dummy(app)
        inv2 = INV.inventory(app)
        ok('Screen:atlasDummy' in inv2 and 'Sheet:atlasDummySheet' in inv2, 'a dummy screen and sheet added to the code are listed')
        ok(set(inv2) - set(inv) == {'Screen:atlasDummy', 'Sheet:atlasDummySheet'}, 'and nothing else changes')
    ok(INV.function_body('function a(){ const s = "}"; /* } */ return `${ {b:1}.b }` } function z(){}', 'a').endswith('}` }'),
       'braces inside strings, comments and templates don’t end a function early')


# ---------- docs ----------
def t_docs():
    print('“Explained in” links land on the right sections')
    ok(INV.gh_slug('Save safety (3.29, Q11)') == 'save-safety-329-q11', 'GitHub’s address for “Save safety (3.29, Q11)”')
    ok(INV.gh_slug("What it's for") == 'what-its-for', 'for “What it’s for”')
    ok(INV.gh_slug('3.47 · 2 Nov 2026') == '347--2-nov-2026', 'for a changelog heading “3.47 · 2 Nov 2026”')
    ok(INV.gh_slug('The `sw.js` file') == 'the-swjs-file', 'code marks count as their text')
    secs = INV.doc_sections(REPO)
    wanted = set()
    for v in list(S.KEY_DOCS.values()) + list(S.AREA_DOCS.values()) + [d for _, d in S.PREFIX_DOCS] + [r.get('docs', []) for r in S.ROOTS]:
        wanted.update(v)
    missing = [f'{f} › {l}' for f, l in wanted if not any(d['file'] == f and d['label'] == l for d in secs)]
    ok(not missing, 'every section the Atlas links to exists' + (': missing ' + '; '.join(missing) if missing else f' ({len(wanted)})'))
    # each address really is that heading's anchor: the heading on that line makes that slug
    bad = []
    for d in secs:
        lines = open(os.path.join(REPO, d['file']), encoding='utf-8').read().splitlines()
        if d.get('sub'):
            if not lines[d['line'] - 1].startswith('**' + d['heading']) or d['anchor'] != 'tabs': bad.append(d['label'])
            continue
        h = re.match(r'^#{2,3} (.+?)\s*$', lines[d['line'] - 1])
        sl = INV.gh_slug(h.group(1)) if h else None
        if not h or not (d['anchor'] == sl or re.fullmatch(re.escape(sl) + r'-\d+', d['anchor'])) or not d['url'].endswith('#' + d['anchor']):
            bad.append(d['label'])
    ok(not bad, 'each link’s address is its own heading’s' + (': ' + ', '.join(bad) if bad else ''))
    dup = [d for d in secs if d['file'] == 'MAINTAINING.md' and d['heading'] == 'Backups']
    ok(dup and dup[0]['anchor'] == 'backups', 'a heading used once keeps the plain address')
    sub = next((d for d in secs if d['label'] == 'Tabs › Today'), None)
    ok(sub and sub['url'].endswith('README.md#tabs'), 'README’s bold “Today” links to the Tabs section it sits in (it has no address of its own)')
    log = INV.changelog(REPO)
    ok(log and log[0]['url'].endswith('#' + INV.gh_slug(log[0]['version'] + ' · ' + log[0]['date'])), 'changelog links use the version heading’s address')
    ok(all(c['q'] is None or re.match(r'Q\d+$', c['q']) for c in log), 'queue IDs are read from the headlines')


# ---------- rules ----------
def t_rules():
    print('The scan’s rules')
    import scan as SC
    ok(all(st[0] == 'tap' for r in S.ROOTS for st in r['steps']), 'every starting screen is opened through real buttons (no shortcuts)')
    ok(SC.skip_reason('sheet', 'delSession') is None, 'a button that only opens a confirmation sheet is tapped')
    ok(SC.skip_reason('sgDoDel', '') and 'deletes' in SC.skip_reason('sgDoDel', ''), 'a button that deletes is never tapped, with its reason')
    ok('microphone' in (SC.skip_reason('rec', '') or ''), 'recording: “needs the microphone”')
    ok('file' in (SC.skip_reason('trkAdd', '') or ''), 'Add track: “needs a file”')
    ok('shares' in (SC.skip_reason('exportPrep', '') or ''), 'Export: “saves or shares a file”')
    ok(SC.skip_reason('tab', 'today') is None and SC.skip_reason('openCal', '') is None, 'ordinary buttons are tapped')
    ok(S.family('|ex||humming') == S.family('|ex||rung'), 'other exercise pages share one entry (same page layout)')
    ok(S.family('today||') == 'Tab:today' and S.family('|set||backup') == 'Sub-page:backup', 'tabs and Settings pages have their own entries')
    ok(S.FIXED_TIME.tzinfo is not None, 'the clock is frozen at a fixed moment, London time')


# ---------- git ----------
def t_git():
    print('Scans never go into git')
    r = subprocess.run(['git', '-C', REPO, 'check-ignore', '-q', 'tools/atlas/data/scans/x/atlas.json'])
    ok(r.returncode == 0, 'tools/atlas/data/ is git-ignored')
    r = subprocess.run(['git', '-C', REPO, 'ls-files', 'tools/atlas/data'], capture_output=True, text=True)
    ok(r.stdout.strip() == '', 'nothing under tools/atlas/data/ is tracked')
    r = subprocess.run(['git', '-C', REPO, 'ls-files', 'tools/atlas'], capture_output=True, text=True)
    ok(not re.search(r'\.(jpg|png|json)$', r.stdout, re.M), 'no screenshots or scan results are tracked in tools/atlas/')


# ---------- the scanner, end to end ----------
def t_scan():
    print('The scanner (a few screens, in a copy of the app)')
    import scan as SC
    quiet = lambda *a: None
    with tempfile.TemporaryDirectory() as tmp:
        app = app_copy(tmp); add_dummy(app)
        roots = [r for r in S.ROOTS if r['id'] == 'today'] + [
            dict(id='cal', title='Calendar', area='Today', kind='Sheet', key='Sheet:calendar', steps=[('tap', '[data-a="openCal"]')], setup=[]),
            dict(id='no-sheet', title='A sheet that doesn’t open', area='Today', kind='Sheet', key='Sheet:calendar', steps=[], setup=[], taps=False),
            dict(id='no-button', title='A button that isn’t there', area='Today', kind='Sheet', key='Sheet:calendar', steps=[('tap', '[data-a="atlasNothing"]')], setup=[], taps=False),
            dict(id='old-screen', title='Removed screen', area='Today', kind='Screen', key='Screen:atlasRemoved', steps=[], setup=[], taps=False)]
        a1 = os.path.join(tmp, 'scan1'); os.makedirs(a1)
        A = SC.scan(app, a1, workers=2, taps=True, only={'today', 'cal', 'no-sheet', 'no-button', 'old-screen'}, say=quiet, roots=roots)
        by = {s['id']: s for s in A['screens']}
        ok(by['today']['status'] == 'captured' and os.path.exists(os.path.join(a1, 'shots', 'today.jpg')), 'Today is captured, top of screen')
        ok(os.path.exists(os.path.join(a1, 'shots', 'today-full.jpg')), 'and full length')
        ok(by['cal']['status'] == 'captured' and by['cal']['sig'].endswith('|calendar'), 'the calendar opens through its real button')
        ok(by['cal']['links'] and not any(l['how'] == 'broken' for l in by['cal']['links']), 'its buttons (month arrows) are tapped and none is “broken”')
        ok(any(l['how'] in ('stays', 'seen') for l in by['cal']['links']), 'and they’re recorded as working')
        for k in ('no-sheet', 'no-button'):
            s = by[k]
            ok(s['status'] == 'failed' and s['shot'] is None and not os.path.exists(os.path.join(a1, 'shots', k + '.jpg')),
               f'“{s["title"]}”: failed, with no picture kept (never the screen underneath)')
            ok(s['why'] and s['why'].strip(), '  and it says why: ' + (s['why'] or '')[:80])
        ok(by['old-screen']['status'] == 'gone', 'a starting screen whose code is gone is reported gone, not captured')
        dummy = next((s for s in A['screens'] if s.get('key') == 'Screen:atlasDummy'), None)
        ok(dummy and dummy['status'] == 'uncaptured', 'the dummy screen added to the code appears, as “Not captured yet”')
        ok(any(s.get('key') == 'Sheet:atlasDummySheet' and s['status'] == 'uncaptured' for s in A['screens']), 'and the dummy sheet')
        ok(A['scan']['clock'].startswith('2026-11-02T10:00'), 'the scan records the frozen clock')
        today = by['today']
        ok(any(l['how'] == 'not-tested' and 'saves or shares' in l.get('why', '') for l in today['links']), 'Today’s Back up button is “Not tested”, with its reason')
        ok(any(l.get('to') == 'cal' for l in today['links']), 'Today’s date leads to the Calendar entry')
        ok(any(f['from'] == 'today' for f in by['cal']['from']), 'and the Calendar says it comes from Today')
        ok(json.load(open(os.path.join(a1, 'atlas.json')))['inventory'] == A['inventory'], 'atlas.json keeps the code’s list for the next scan')

        # the dummy removed: the next scan reports it gone
        shutil.rmtree(os.path.join(app, 'js')); shutil.copytree(os.path.join(REPO, 'js'), os.path.join(app, 'js'))
        a2 = os.path.join(tmp, 'scan2'); os.makedirs(a2)
        B = SC.scan(app, a2, workers=1, taps=False, only={'today'}, prev=a1, say=quiet, roots=roots)
        cc = B['scan']['codeChanges']
        ok(cc and set(cc['gone']) == {'Screen:atlasDummy', 'Sheet:atlasDummySheet'} and not cc['added'], 'the dummy removed: the next scan reports it gone')
        ok(any(s.get('key') == 'Screen:atlasDummy' and s['status'] == 'gone' for s in B['screens']), 'and lists it as “Gone from the code”')
        ok(not any(s.get('key') == 'Screen:atlasDummy' and s['status'] == 'uncaptured' for s in B['screens']), 'not as found in code')


# ---------- the viewer ----------
def png(w, h, rgb):
    raw = b''.join(b'\x00' + bytes(rgb) * w for _ in range(h))
    chunk = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


def sample_atlas(folder):
    os.makedirs(os.path.join(folder, 'shots'))
    for i in ('a', 'b', 'c'):
        for f in (i + '.jpg', i + '-full.jpg'):
            open(os.path.join(folder, 'shots', f), 'wb').write(png(40, 87, (200, 210, 230)))
    secs = INV.doc_sections(REPO)
    doc = lambda f, l: next({'file': d['file'], 'heading': d['label'], 'url': d['url'], 'anchor': d['anchor']} for d in secs if d['file'] == f and d['label'] == l)
    link = lambda **k: dict({'action': 'x', 'label': 'x', 'selector': '[data-a="x"]', 'kind': 'Button'}, **k)
    sc = lambda id, title, area, kind, **k: dict({'id': id, 'title': title, 'area': area, 'kind': kind, 'key': 'Tab:today', 'setup': [], 'status': 'captured',
                                                  'errors': [], 'links': [], 'from': [], 'docs': [], 'shot': 'shots/' + id + '.jpg', 'full': 'shots/' + id + '-full.jpg',
                                                  'fullHeight': 1400, 'how': 'tap [data-a="x"]', 'sig': 'today||'}, **k)
    atlas = {'format': 3, 'app': {'name': 'Vocal Sessions', 'url': 'https://imperialfox.github.io/Vocal-Sessions/'},
             'scan': {'id': 'T', 'at': '2026-11-02T18:00:00+00:00', 'seconds': 300, 'commit': 'abc1234 Test', 'version': '3.47',
                      'viewport': {'w': 402, 'h': 874, 'name': 'iPhone 17 Pro'}, 'data': 'sample data', 'clock': '2026-11-02T10:00:00+00:00',
                      'codeChanges': None}, 'areas': S.AREAS, 'inventory': [],
             'screens': [
                 sc('a', 'Today', 'Today', 'Tab', docs=[doc('README.md', 'Tabs › Today')],
                    links=[link(action='openCal', label='Monday 2 November', how='seen', to='b', toSig='today||calendar', kind='Opens a sheet'),
                           link(action='exportPrep', label='Back up', how='not-tested', why='Not tested: saves or shares a file'),
                           link(action='ring', label='Hidden ring', how='stays', forced=True),
                           link(action='tab', label='Songs', how='seen', to='c', kind='Tab bar')],
                    mention={'version': '3.41', 'q': 'Q21', 'title': 'Session saved (Q21)', 'url': 'https://example.invalid/#341'}),
                 sc('b', 'Calendar', 'Today', 'Sheet', docs=[doc('MAINTAINING.md', 'Save safety (3.29, Q11)')], **{'from': [{'from': 'a', 'label': 'Monday 2 November', 'how': 'seen'}]}),
                 sc('c', 'Songs', 'Songs', 'Tab', errors=['TypeError: x is undefined']),
                 sc('d', 'Broken sheet', 'Songs', 'Sheet', status='failed', shot=None, full=None, why='Didn’t open: landed on songs tab instead'),
                 {'id': 'code-x', 'title': 'trkMkName', 'kind': 'Sheet', 'key': 'Sheet:trkMkName', 'area': 'Not captured yet', 'status': 'uncaptured',
                  'why': 'Found in the code', 'links': [], 'from': [], 'docs': [], 'errors': []}]}
    json.dump(atlas, open(os.path.join(folder, 'atlas.json'), 'w'))
    shutil.copy(os.path.join(HERE, 'viewer.html'), os.path.join(folder, 'index.html'))


def t_viewer():
    print('The viewer (Mac and iPhone sizes)')
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as tmp:
        sample_atlas(tmp)
        class Q(SimpleHTTPRequestHandler):
            def log_message(self, *a): pass
        srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=tmp))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = f'http://localhost:{srv.server_address[1]}/'
        with sync_playwright() as p:
            b = p.chromium.launch()
            for w, h, name in ((1440, 900, 'Mac'), (402, 874, 'iPhone')):
                errs = []
                pg = b.new_page(viewport={'width': w, 'height': h})
                pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
                pg.goto(url); pg.wait_for_selector('.card')
                ok(pg.locator('.card').count() == 4, f'{name}: four screens shown (the one found only in code hidden)')
                ok(pg.locator('.card[data-id="d"] .th.fail').count() == 1 and pg.locator('.card[data-id="d"] img').count() == 0,
                   f'{name}: the failed screen shows as failed, never a blank picture')
                ok('not live' in pg.inner_text('body'), f'{name}: says the screenshots are saved, not live')
                ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{name}: nothing wider than the window')
                if name == 'Mac':
                    ok(pg.locator('nav.side').is_visible() and not pg.locator('#mchips').is_visible(), 'Mac: filters in the side bar')
                    pg.check('#showCode'); ok(pg.locator('.card').count() == 5 and pg.locator('.card[data-id="code-x"] .th.unc').count() == 1, 'Mac: “Show screens found only in code” adds it, dashed')
                    pg.uncheck('#showCode')
                    pg.click('#side [data-f="area"][data-v="Songs"]'); ok(pg.locator('.card').count() == 2, 'Mac: an area filter')
                    pg.click('#side [data-f="area"][data-v=""]')
                    pg.click('[data-g="status"]'); ok(pg.locator('.ghead h2').first.inner_text().startswith('✓'), 'Mac: group by status')
                    pg.click('[data-g="area"]')
                    pg.fill('#q', 'monday 2'); ok(pg.locator('.card').count() == 1 and pg.locator('.card[data-id="a"]').count() == 1, 'Mac: search finds a screen by a button’s label')
                    pg.fill('#q', ''); pg.keyboard.press('Escape')
                    pg.keyboard.press('/'); ok(pg.evaluate("document.activeElement.id") == 'q', 'Mac: / goes to search')
                    pg.keyboard.press('Escape')
                    pg.locator('.card[data-id="a"]').focus()
                    pg.keyboard.press('ArrowRight'); ok(pg.evaluate("document.activeElement.dataset.id") == 'b', 'Mac: arrows move between screens')
                    pg.keyboard.press('Enter'); ok(pg.locator('#det.open').count() == 1 and 'Calendar' in pg.inner_text('#det .dtitle'), 'Mac: Enter opens the details')
                    ok(pg.locator('#det a[href$="#save-safety-329-q11"]').count() == 1, 'Mac: “Explained in” links to the section’s address')
                    ok('Today' in pg.inner_text('#det'), 'Mac: “Comes from” names Today')
                    pg.keyboard.press('f'); ok(pg.locator('#full.open').count() == 1 and 'not live' in pg.inner_text('#fsub'), 'Mac: F shows the full length')
                    pg.keyboard.press('Escape'); ok(pg.locator('#full.open').count() == 0 and pg.locator('#det.open').count() == 1, 'Mac: Esc closes it, then')
                    pg.click('[data-step="-1"]'); d = pg.inner_text('#det')
                    ok('Today' in pg.inner_text('#det .dtitle'), 'Mac: previous goes to the screen before')
                    ok('Not tested' in d and 'saves or shares a file' in d and 'Forced tap' not in d, 'Mac: a not-tested button with its reason')
                    pg.click('[data-t="stays"]'); ok('Forced tap' in pg.inner_text('#det'), 'Mac: a forced tap is marked as one')
                    ok(pg.locator('#det a[href$="README.md#tabs"]').count() == 1 and 'Q21' in d, 'Mac: docs and the last changelog mention')
                    pg.click('#det button.lrow[data-go="b"]'); ok('Calendar' in pg.inner_text('#det .dtitle'), 'Mac: “Leads to” opens that screen')
                    pg.keyboard.press('Escape'); ok(pg.locator('#det.open').count() == 0, 'Mac: Esc closes the details')
                    pg.click('.card[data-id="c"]'); ok('TypeError' in pg.inner_text('#det .err'), 'Mac: a screen’s errors are listed')
                    pg.click('#rescan'); ok(pg.locator('#pop.open').count() == 1 and 'atlas.py' in pg.inner_text('#pop'), 'Mac: Rescan says how')
                else:
                    ok(not pg.locator('nav.side').is_visible() and pg.locator('#mchips').is_visible(), 'iPhone: filters as chips')
                    cols = pg.evaluate("getComputedStyle(document.querySelector('.grid')).gridTemplateColumns.split(' ').length")
                    ok(cols == 3, f'iPhone: three columns ({cols})')
                    pg.click('.card[data-id="a"]')
                    box = pg.locator('#det').bounding_box()
                    ok(box and box['width'] >= w - 1 and box['height'] >= h - 1, 'iPhone: details fill the screen')
                    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'iPhone: and fit its width')
                    pg.click('#dclose'); ok(pg.locator('#det.open').count() == 0, 'iPhone: ✕ closes them')
                    pg.goto(url + '?again#s-b'); pg.wait_for_selector('#det.open', timeout=5000); ok('Calendar' in pg.inner_text('#det .dtitle'), 'iPhone: a link to a screen (#s-b) opens it')
                ok(not errs, f'{name}: no page errors' + (': ' + '; '.join(errs[:2]) if errs else ''))
                pg.close()
            b.close()
        srv.shutdown()


PARTS = {'code': t_code, 'docs': t_docs, 'rules': t_rules, 'git': t_git, 'scan': t_scan, 'viewer': t_viewer}
if __name__ == '__main__':
    for n in (sys.argv[1:] or list(PARTS)):
        try: PARTS[n]()
        except Exception as e:
            import traceback; traceback.print_exc(); FAILS.append(f'{n} crashed: {e}')
    print(f'\n{PASSED} passed, {len(FAILS)} failed')
    for f in FAILS: print('  FAIL  ' + f)
    sys.exit(1 if FAILS else 0)
