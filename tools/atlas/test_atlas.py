"""Tests for the Visual App Atlas: Vocal Sessions' settings for the Atlas kit, the kit copy, a scan and the viewer.

    python3 tools/atlas/test_atlas.py            everything (about two minutes)
    python3 tools/atlas/test_atlas.py code docs  only some parts: code, docs, rules, settings, kit, git, scan, viewer, states

Not part of the app's suite (tests/run.py), so GitHub's test run stays as long as it was. Uses the tests' Playwright
(1.56.0) and TZ=Europe/London, like the app's tests. The kit has its own tests in its own repo; these check what's
particular to Vocal Sessions. Everything is made in a temporary folder; nothing is left behind.
"""
import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(HERE, 'kit')
sys.path.insert(0, KIT)
from atlas_kit import VERSION, code as CODE, docs as DOCS, settings as SET  # noqa: E402

SETTINGS = os.path.join(HERE, 'screens.py')
ST = SET.load(SETTINGS)
S = ST.mod

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
    for f in ('index.html', 'sw.js', 'icon.png', 'CHANGELOG.md', 'README.md', 'MAINTAINING.md', 'RENDER_QUEUE.md'):
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
    inv = S.inventory(REPO)
    ui = open(os.path.join(REPO, 'js', 'ui.js'), encoding='utf-8').read()
    r = CODE.function_body(ui, 'render'); rs = CODE.function_body(ui, 'renderSheet')
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
        inv2 = S.inventory(app)
        ok('Screen:atlasDummy' in inv2 and 'Sheet:atlasDummySheet' in inv2, 'a dummy screen and sheet added to the code are listed')
        ok(set(inv2) - set(inv) == {'Screen:atlasDummy', 'Sheet:atlasDummySheet'}, 'and nothing else changes')


# ---------- docs ----------
def t_docs():
    print('“Explained in” links land on the right sections')
    secs = DOCS.doc_sections(REPO, S.DOC_FILES, S.DOCS_URL)
    wanted = set()
    for v in list(S.KEY_DOCS.values()) + list(S.AREA_DOCS.values()) + [d for _, d in S.PREFIX_DOCS] + [r.get('docs', []) for r in S.ROOTS]:
        wanted.update(v)
    missing = [f'{f} › {l}' for f, l in wanted if not any(d['file'] == f and d['label'] == l for d in secs)]
    ok(not missing, 'every section the Atlas links to exists' + (': missing ' + '; '.join(missing) if missing else f' ({len(wanted)})'))
    bad = []
    for d in secs:
        if (d['file'], d['label']) not in wanted: continue
        lines = open(os.path.join(REPO, d['file']), encoding='utf-8').read().splitlines()
        if d.get('sub'):
            if not lines[d['line'] - 1].startswith('**' + d['heading']) or d['anchor'] != 'tabs': bad.append(d['label'])
            continue
        h = re.match(r'^#{2,3} (.+?)\s*$', lines[d['line'] - 1])
        sl = DOCS.gh_slug(h.group(1)) if h else None
        if not h or not (d['anchor'] == sl or re.fullmatch(re.escape(sl) + r'-\d+', d['anchor'])) or not d['url'] == S.GH + d['file'] + '#' + d['anchor']:
            bad.append(d['label'])
    ok(not bad, 'each link’s address is its own heading’s on GitHub' + (': ' + ', '.join(bad) if bad else ''))
    sub = next((d for d in secs if d['label'] == 'Tabs › Today'), None)
    ok(sub and sub['url'].endswith('README.md#tabs'), 'README’s bold “Today” links to the Tabs section it sits in (it has no address of its own)')
    log = DOCS.changelog(REPO, S.CHANGELOG, S.DOCS_URL)
    ok(log and log[0]['url'] == S.GH + 'CHANGELOG.md#' + DOCS.gh_slug(log[0]['version'] + ' · ' + log[0]['date']), 'changelog links use the version heading’s address')
    ok(log and log[0]['version'] == S.version(REPO), f'the newest changelog entry is the app’s version ({S.version(REPO)})')
    ok(all(c['q'] is None or re.match(r'Q\d+$', c['q']) for c in log), 'queue IDs are read from the headlines')


# ---------- rules ----------
def t_rules():
    print('The scan’s rules')
    ok(all(real_step(st) for r in S.ROOTS for st in r['steps']), 'every starting screen is opened through real buttons (no shortcuts; Q35 adds only waits and holds)')
    ok(ST.skip_reason('sheet', 'delSession', 'Delete session') is None, 'a button that only opens a confirmation sheet is tapped')
    ok('deletes' in (ST.skip_reason('sgDoDel', '', 'Delete') or ''), 'a button that deletes is never tapped, with its reason')
    ok('microphone' in (ST.skip_reason('rec', '', 'Record') or ''), 'recording: “needs the microphone”')
    ok('file' in (ST.skip_reason('trkAdd', '', 'Add track') or ''), 'Add track: “needs a file”')
    ok('shares' in (ST.skip_reason('exportPrep', '', 'Back up') or ''), 'Export: “saves or shares a file”')
    ok(ST.skip_reason('tab', 'today', 'Today') is None and ST.skip_reason('openCal', '', 'Monday 2 November') is None, 'ordinary buttons are tapped')
    ok(ST.skip_reason('mkLayer', 'delivery', '4 Delivery') is None and ST.skip_reason('wTog', 'Clear tone', 'Clear tone') is None
       and ST.skip_reason('gdOpen', 'chain', 'Chain No reset between two phrases') is None, 'labels and values never count as deleting (“4 Delivery”, “Clear tone”, “No reset”)')
    acts = sorted({m for f in os.listdir(os.path.join(REPO, 'js')) if f.endswith('.js')
                   for m in re.findall(r'data-a=\\?"([A-Za-z]+)\\?"', open(os.path.join(REPO, 'js', f), encoding='utf-8').read())})
    bare = lambda a: next((why for rx, why in S.SKIP if re.search(rx, a)), None) if a not in S.SAFE_ACTIONS else None
    odd = [a for a in acts if ST.skip_reason(a, '', 'Some label') != bare(a)]
    ok(acts and not odd, f'every action in the code is decided by its name alone ({len(acts)} actions)' + (': ' + ', '.join(odd) if odd else ''))
    ok(ST.family('|ex||humming') == ST.family('|ex||rung'), 'other exercise pages share one entry (same page layout)')
    ok(ST.family('today||') == 'Tab:today' and ST.family('|set||backup') == 'Sub-page:backup', 'tabs and Settings pages have their own entries')
    ok(ST.family('Tab:today') == 'Tab:today' and ST.keys_of('Screen:guide:home') == ['Screen:guide'], 'code-list keys (as the starting screens use) pass through')
    ok(ST.kind_of('Sheet:calendar', True) == 'Sheet' and ST.kind_of('Sub-page:backup', False) == 'Sub-page', 'sheets and Settings pages get their kind')
    ok(S.link_kind({'action': 'tab'}) == 'Tab bar' and S.link_kind({'action': 'setPgBack'}) == 'Back'
       and S.link_kind({'action': 'openCal', 'toSig': 'today||calendar', 'opensSheet': True}) == 'Opens a sheet', 'map lines: tab bar, back, opens a sheet')
    ok(ST.fixed_time.tzinfo is not None and ST.timezone == 'Europe/London', 'the clock is frozen at a fixed moment, London time')
    ok(ST.ids and ST.ids['prefix'] == 'VS-' and ST.queue == {'file': 'RENDER_QUEUE.md', 'section': 'Not scheduled'}, 'screen IDs from the register; queue ideas go to RENDER_QUEUE.md › Not scheduled')


def real_step(st):
    """A tap, a fixed wait, or Q35's UNTIL (waits for the app) and HOLD (presses a real button): none opens a screen itself."""
    return st[0] in ('tap', 'wait') or (st[0] == 'js' and (st[1].startswith('async()=>{/*until*/') or st[1].startswith('async()=>{/*hold*/')))


# ---------- Q35: starting states, captions, flows and doors (settings only, no browser) ----------
REG_JS = open(os.path.join(REPO, 'js', 'register.js'), encoding='utf-8').read()
REG_IDS = set(re.findall(r"id: '(VS-\d+)'", REG_JS))
REG_FLOWS = dict(re.findall(r"id: '(F-\d+)',\s*name: '([^']+)'", REG_JS))
Q35_STATES = {'coach-video': 'Screen:coach', 'session-recording': 'Screen:app', 'session-takes': 'Screen:app', 'session-compare': 'Screen:app',
              'song-how': 'Sheet:how', 'peek-card': 'Screen:lyr', 'check-timing-overlaps': 'Screen:ckCheck', 'track-past-end': 'Sheet:trkPast',
              'backup-rescued': 'Sub-page:backup', 'rescued-delete': 'Sheet:rescueDel'}


def t_settings():
    print('Q35: starting states, captions, flows and doors in the settings')
    roots = {r['id']: r for r in S.ROOTS}
    ok(all(k in roots and roots[k]['key'] == v for k, v in Q35_STATES.items()), f'a starting state for each screen in the handoff ({len(Q35_STATES)})')
    ok(all(roots[r['state_of']] for r in S.ROOTS if r.get('state_of')), 'every state belongs to a starting screen')
    ok(all(not st[1].startswith('async()=>{/*until*/') or 'throw new Error("Didn’t open: ' in st[1] for r in S.ROOTS for st in r['steps'] if st[0] == 'js'),
       'a wait that never ends says why, so the screen is “Failed”, never captured')
    ok(len(REG_IDS) >= 95 and REG_IDS <= set(S.CAPTIONS), f'every screen in the register has a caption ({len(REG_IDS)})' + (': missing ' + ', '.join(sorted(REG_IDS - set(S.CAPTIONS))) if REG_IDS - set(S.CAPTIONS) else ''))
    odd = [k for k, v in S.CAPTIONS.items() if k.split('~')[0] not in REG_IDS or not v.strip() or '\n' in v or len(v) > 64]
    ok(not odd, 'each caption is one short line, on a screen in the register' + (': ' + ', '.join(odd) if odd else ''))
    ok([f['id'] for f in S.FLOWS] == ['F-01', 'F-02'] and all(REG_FLOWS.get(f['id']) == f['title'] for f in S.FLOWS),
       'the first flows are the register’s F-01 · Focused session and F-02 · Song practice')
    ok(all(f['start'] in roots for f in S.FLOWS) and all(s.get('tap') or s.get('js') for f in S.FLOWS for s in f['steps'])
       and all(s['js'].startswith('async()=>{/*until*/') for f in S.FLOWS for s in f['steps'] if s.get('js')), 'flows start on a starting screen and tap real buttons (their only js waits)')
    bad = [d for d in S.DOORS if d['from'].split('~')[0] not in REG_IDS or d['to'].split('~')[0] not in REG_IDS or not d.get('how') or not d.get('kind')]
    ok(S.DOORS and not bad, f'every hand-written door joins two screens in the register, saying how and what kind ({len(S.DOORS)})' + (f': {bad}' if bad else ''))
    kinds = {d['kind'] for d in S.DOORS}
    ok({'Swipe', 'Hold', 'Timed', 'File picker'} <= kinds, 'doors for swipes, holds, timed sheets and file pickers')
    ok(all(any(d['to'] == t for d in S.DOORS) for t in ('VS-083', 'VS-086', 'VS-089')), 'export, check a backup and restore are doors only, never captured')


# ---------- the kit copy ----------
def t_kit():
    print('The kit copy is pinned and unmodified')
    lines = [l.split('  ', 1) for l in open(os.path.join(HERE, 'kit.sha256'), encoding='utf-8').read().splitlines() if l.strip()]
    files = {f: h for h, f in lines}
    bad = [f for f, h in files.items() if not os.path.exists(os.path.join(HERE, f)) or hashlib.sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest() != h]
    have = {os.path.relpath(os.path.join(d, f), HERE) for d, _, fs in os.walk(KIT) for f in fs if '__pycache__' not in d}
    ok(files and not bad, f'every file in kit/ matches its checksum in kit.sha256 ({len(files)} files)' + (': ' + ', '.join(bad) if bad else ''))
    ok(have == set(files), 'and nothing else is in kit/' + (': ' + ', '.join(sorted(have ^ set(files))) if have != set(files) else ''))
    readme = open(os.path.join(HERE, 'README.md'), encoding='utf-8').read()
    ok(f'Atlas kit version: {VERSION}' in readme, f'tools/atlas/README.md notes the kit’s version ({VERSION})')
    ok(VERSION == '1.1.0' and f'const KIT_VERSION = \'{VERSION}\'' in open(os.path.join(KIT, 'viewer.html'), encoding='utf-8').read(), 'the viewer is the same kit version')
    left = [f for f in ('scan.py', 'inventory.py', 'viewer.html') if os.path.exists(os.path.join(HERE, f))]
    ok(not left, 'tools/atlas/ keeps only Vocal Sessions’ own settings (no scanner or viewer of its own)' + (': ' + ', '.join(left) if left else ''))


# ---------- git ----------
def t_git():
    print('Scans and notes never go into git')
    r = subprocess.run(['git', '-C', REPO, 'check-ignore', '-q', 'tools/atlas/data/scans/x/atlas.json'])
    ok(r.returncode == 0, 'tools/atlas/data/ is git-ignored')
    r = subprocess.run(['git', '-C', REPO, 'ls-files', 'tools/atlas/data'], capture_output=True, text=True)
    ok(r.stdout.strip() == '', 'nothing under tools/atlas/data/ is tracked')
    r = subprocess.run(['git', '-C', REPO, 'ls-files', 'tools/atlas'], capture_output=True, text=True)
    ok(not re.search(r'\.(jpg|png|json)$', r.stdout, re.M), 'no screenshots, scan results or notes are tracked in tools/atlas/')


# ---------- a scan, end to end, through the kit ----------
def settings_for(tmp, app, roots):
    """Vocal Sessions' settings with test starting screens, scanning a copy of the app."""
    p = os.path.join(tmp, 'atlas_test_settings.py')
    open(p, 'w').write(f'import sys\nsys.path.insert(0, {HERE!r})\nfrom screens import *  # noqa\n'
                       f'from screens import _tests, _open  # noqa\nAPP_DIR = {app!r}\nROOTS = {roots!r}\n')
    return p


def find(A, slug):
    return next((s for s in A['screens'] if s.get('slug', s['id']) == slug or s['id'] == slug), None)


SCANS = {}


def t_scan():
    print('A scan through the kit (a few screens, in a copy of the app)')
    from atlas_kit import engine
    quiet = lambda *a: None
    tmp = SCANS.setdefault('tmp', tempfile.mkdtemp(prefix='vs-atlas-test-'))
    app = app_copy(tmp); add_dummy(app)
    roots = [r for r in S.ROOTS if r['id'] in ('today', 'today-dark')] + [dict(r, taps=False) for r in S.ROOTS if r['id'] == 'exercises'] + [
        dict(id='cal', title='Calendar', area='Today', kind='Sheet', key='Sheet:calendar', steps=[('tap', '[data-a="openCal"]')], setup=[]),
        dict(id='no-sheet', title='A sheet that doesn’t open', area='Today', kind='Sheet', key='Sheet:calendar', steps=[], setup=[], taps=False),
        dict(id='no-button', title='A button that isn’t there', area='Today', kind='Sheet', key='Sheet:calendar', steps=[('tap', '[data-a="atlasNothing"]')], setup=[], taps=False),
        dict(id='old-screen', title='Removed screen', area='Today', kind='Screen', key='Screen:atlasRemoved', steps=[], setup=[], taps=False)]
    sp = settings_for(tmp, app, roots)
    a1 = os.path.join(tmp, 'scan1'); os.makedirs(a1)
    A = engine.scan(sp, app, a1, workers=2, taps=True, only={r['id'] for r in roots}, say=quiet, scan_id='T1')
    today, cal = find(A, 'today'), find(A, 'cal')
    ok(today and today['id'] == 'VS-001' and today['status'] == 'captured' and os.path.exists(os.path.join(a1, today['shot'])), 'Today is captured under its screen ID (VS-001), top of screen')
    ok(os.path.exists(os.path.join(a1, today['full'])), 'and full length')
    dark = find(A, 'today-dark')
    ok(dark and dark['id'].startswith('VS-001~') and dark['sid'] == 'VS-001' and dark['stateOf'] == 'VS-001', f'Today in dark mode shares its ID as a state ({dark and dark["id"]})')
    reg = {r['id']: r for r in A['screens'] if r.get('sid')}
    ok(cal and cal['status'] == 'captured' and cal['sig'].endswith('|calendar') and cal['idFrom'] == 'screen', f'the calendar opens through its real button, its ID read off the sheet ({cal and cal["id"]})')
    ok(cal['links'] and not any(l['how'] == 'broken' for l in cal['links']), 'its buttons (month arrows) are tapped and none is “broken”')
    ok(any(l['how'] in ('stays', 'seen') for l in cal['links']), 'and they’re recorded as working')
    ok(any(e.get('part') == 'start-session-button' for e in today['elements']), 'what’s on Today is mapped for tap-a-part notes, with the register’s part names')
    for k in ('no-sheet', 'no-button'):
        s = find(A, k)
        ok(s['status'] == 'failed' and s['shot'] is None and not os.path.exists(os.path.join(a1, 'shots', k + '.jpg')),
           f'“{k}” ({s["title"]}): failed, with no picture kept (never the screen underneath)')
        ok(s['why'] and s['why'].strip(), '  and it says why: ' + (s['why'] or '')[:80])
    ok(find(A, 'old-screen')['status'] == 'gone', 'a starting screen whose code is gone is reported gone, not captured')
    ok(any(s.get('key') == 'Screen:atlasDummy' and s['status'] == 'uncaptured' for s in A['screens']), 'the dummy screen added to the code appears, as “Not captured yet”')
    ok(A['scan']['clock'].startswith('2026-11-02T10:00') and A['scan']['version'] == S.version(app), 'the scan records the frozen clock and the app’s version')
    ok(any(l['how'] == 'not-tested' and 'saves or shares' in l.get('why', '') for l in today['links']), 'Today’s Back up button is “Not tested”, with its reason')
    ok(any(l.get('to') == cal['id'] and l['kind'] == 'Opens a sheet' for l in today['links']), 'Today’s date leads to the Calendar, as a line that opens a sheet')
    ok(any(l['kind'] == 'Tab bar' for l in today['links']), 'the tab bar’s buttons are marked Tab bar')
    ok(any(f['from'] == today['id'] for f in cal['from']), 'and the Calendar says it comes from Today')
    ok(today['docs'] and today['docs'][0]['url'].startswith(S.GH), 'Today’s “Explained in” links point at GitHub')
    ok(A['app']['queue'] == S.QUEUE and A['kit'] == VERSION, 'atlas.json names the queue for ideas and the kit version')

    # a rescan with no change to the app: nothing is called different (screens are read once they've settled)
    a0 = os.path.join(tmp, 'scan0'); os.makedirs(a0)
    Z = engine.scan(sp, app, a0, workers=2, taps=False, only={'today', 'cal', 'exercises'}, prev=a1, say=quiet, scan_id='T1b')
    moved = [s['id'] for s in Z['screens'] if s['status'] == 'captured' and (s.get('change') or {}).get('kind') == 'looks-different']
    ok(not moved and find(Z, 'cal')['status'] == 'captured', 'a rescan with no change to the app calls nothing different, the Calendar sheet included' + (f' ({moved})' if moved else ''))

    # the app changes: Today looks different, the dummy screen is gone, and a version is released in between
    shutil.rmtree(os.path.join(app, 'js')); shutil.copytree(os.path.join(REPO, 'js'), os.path.join(app, 'js'))
    with open(os.path.join(app, 'css', 'app.css'), 'a') as f: f.write('\n#app[data-screen="VS-001"] h1{background:#e33!important;color:#fff!important}\n')
    lp = os.path.join(app, 'CHANGELOG.md'); log = open(lp, encoding='utf-8').read()
    v = S.version(app); nv = v.split('.')[0] + '.' + str(int(v.split('.')[1]) + 1)
    open(lp, 'w', encoding='utf-8').write(log.replace('\n## ' + v + ' ', f'\n## {nv} · 4 Nov 2026\n\n*A test release (Q99)*\n\nScreens: VS-001\n\n## {v} ', 1))
    ip = os.path.join(app, 'index.html'); page = open(ip, encoding='utf-8').read()
    open(ip, 'w', encoding='utf-8').write(re.sub(r"APP_VERSION\s*=\s*'[^']+'", f"APP_VERSION='{nv}'", page, count=1))
    a2 = os.path.join(tmp, 'scan2'); os.makedirs(a2)
    B = engine.scan(sp, app, a2, workers=2, taps=False, only={'today', 'cal', 'exercises'}, prev=a1, baselines=[a1], say=quiet, scan_id='T2')
    t2, e2 = find(B, 'today'), find(B, 'exercises')
    ok((t2.get('change') or {}).get('kind') == 'looks-different' and t2['change'].get('prevShot'), 'a rescan after an app change: Today looks different, with its before picture')
    ok(B['scan']['version'] == nv and (e2.get('change') or {}).get('kind') != 'looks-different', 'Exercises, unchanged, isn’t')
    ok([c['version'] for c in B['scan']['prev']['between']] == [nv], f'the version released in between is named ({nv}), never claimed as the cause')
    cc = B['scan'].get('codeChanges') or {}
    ok(set(cc.get('gone', [])) == {'Screen:atlasDummy', 'Sheet:atlasDummySheet'} and not cc.get('added'), 'the dummy removed from the code: listed as gone')
    SCANS.update(a1=a1, a2=a2)


# ---------- the viewer, with notes ----------
FAKE_STORE = r"""(() => {
  if (window.__preset && !sessionStorage.getItem('__fakeDocs')) sessionStorage.setItem('__fakeDocs', window.__preset);
  const docs = JSON.parse(sessionStorage.getItem('__fakeDocs') || '{}'), subs = [];
  const persist = () => sessionStorage.setItem('__fakeDocs', JSON.stringify(docs));
  const fire = () => setTimeout(() => subs.forEach(f => f()), 0);
  const copy = v => JSON.parse(JSON.stringify(v));
  const snap = p => ({ id: p.split('/').pop(), exists: p in docs, data: () => copy(docs[p]) });
  const docRef = p => ({ set: async v => { docs[p] = copy(v); persist(); fire(); }, update: async v => { docs[p] = Object.assign({}, docs[p], copy(v)); persist(); fire(); },
    delete: async () => { delete docs[p]; persist(); fire(); }, onSnapshot(cb) { const f = () => cb(snap(p)); subs.push(f); setTimeout(f, 0); return () => {}; } });
  const colRef = n => ({ doc: id => docRef(n + '/' + id),
    onSnapshot(cb) { const f = () => cb({ docs: Object.keys(docs).filter(k => k.startsWith(n + '/') && k.split('/').length === 2).map(snap), metadata: { fromCache: false } }); subs.push(f); setTimeout(f, 0); return () => {}; } });
  window.__store = { docs };
  window.claude = { use: async n => (n === 'db' ? { doc: docRef, collection: colRef } : null) };
})();"""


class Serve:
    def __init__(self, folder):
        shutil.copy(os.path.join(KIT, 'viewer.html'), os.path.join(folder, 'index.html'))
        class Q(SimpleHTTPRequestHandler):
            def log_message(self, *a): pass
        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=folder))
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f'http://127.0.0.1:{self.srv.server_address[1]}/'

    def close(self):
        self.srv.shutdown(); self.srv.server_close()


def t_viewer():
    print('The viewer with Vocal Sessions’ scan (Mac and iPhone), notes kept across a rescan')
    if 'a1' not in SCANS and 'tmp' not in SCANS: t_scan()
    if 'a1' not in SCANS: ok(False, 'the viewer needs the scan above'); return
    from playwright.sync_api import sync_playwright
    v1, v2 = Serve(SCANS['a1']), Serve(SCANS['a2'])
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            def page(url, w, h, preset=None, phone=False):
                ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=phone, has_touch=phone)
                pg = ctx.new_page(); errs = []
                pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
                if preset is not None: pg.add_init_script('window.__preset = ' + json.dumps(json.dumps(preset)) + ';')
                pg.add_init_script(FAKE_STORE)
                pg.goto(url); pg.wait_for_selector('.card'); pg.wait_for_timeout(200)
                return pg, errs
            pg, errs = page(v1.url, 1440, 900)
            ok(pg.title() == 'Atlas · Vocal Sessions' and 'not live' in pg.inner_text('body'), 'Mac: “Atlas · Vocal Sessions”, saying the screenshots are saved, not live')
            ok(pg.locator('.card[data-id="VS-001"] .sid', has_text='VS-001').count() == 1, 'Mac: cards show their screen IDs')
            pg.click('.card[data-id="VS-001"]'); pg.wait_for_selector('#det.open')
            ok(pg.locator('#det a[href^="' + S.GH + '"]').count() >= 1, 'Mac: details link to the docs on GitHub')
            # a note on a named part, through the page's own note maker
            pg.evaluate("""async()=>{const s=byId['VS-001'], e=s.elements.find(x=>x.part==='start-session-button');
              await saveNote(makeNote(s,{x:e.x,y:e.y,w:e.w,h:e.h},e,'The start button could sit higher','Layout or spacing'))}""")
            pg.wait_for_timeout(300)
            store = pg.evaluate('JSON.parse(JSON.stringify(window.__store.docs))')
            notes = [v for k, v in store.items() if k.startswith('notes/')]
            n = notes[0] if notes else {}
            ok(n.get('v') == 1 and n.get('screen') == 'VS-001' and n.get('part') == 'start-session-button' and n.get('app') == 'Vocal Sessions',
               'a note is saved in note format v1, on VS-001 › start-session-button')
            rep = pg.evaluate('reportMd(NOTES)')
            ok('VS-001' in rep and 'start-session-button' in rep and 'The start button could sit higher' in rep and 'Kit ' + VERSION in rep,
               'the copied report has the screen, the part, its details and the note')
            q = pg.evaluate('queueMd(NOTES)')
            ok(q.startswith('Please add these to RENDER_QUEUE.md › Not scheduled') and 'priority checked against the app’s purpose' in q and '<' not in q,
               'queue ideas come out as text for RENDER_QUEUE.md › Not scheduled, each to get a priority')
            pg.click('[data-view="map"]'); pg.wait_for_timeout(300)
            ok(pg.locator('#map .mcard[data-mid="VS-001"]').count() == 1 and pg.locator('#map path.edge').count() >= 1, 'Mac: the map shows the screens and their lines')
            ok(not [x for x in errs if 'ERR_' not in x], 'Mac: no errors' + (': ' + '; '.join(errs[:2]) if errs else ''))
            pg.context.close()
            # the rescan, on a phone, with the same store
            pg, errs = page(v2.url, 393, 659, preset=store, phone=True)
            ok(pg.locator('.card[data-id="VS-001"] .npin').count() == 1, 'iPhone, after a rescan: the note is still on Today (VS-001)')
            ok(pg.locator('#bfold', has_text='changed since the last scan').count() == 1, 'iPhone: the changes banner is folded to one line')
            ok(pg.locator('.seg.views').bounding_box()['y'] > 600, 'iPhone: Lightbox · Map · Flows in the bottom bar')
            ok(pg.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'iPhone: nothing wider than the screen')
            ok(not [x for x in errs if 'ERR_' not in x], 'iPhone: no errors' + (': ' + '; '.join(errs[:2]) if errs else ''))
            pg.context.close()
            b.close()
    finally:
        v1.close(); v2.close()
    # "check my notes": the Atlas page's notes and a listed prototype's, together
    atlas = [dict(v, id=k.split('/')[1]) for k, v in store.items() if k.startswith('notes/')]
    proto = [dict(atlas[0], id='p-1', n=1, source='prototype', text='Moved the button up in the prototype', created='2026-11-03T09:00:00Z',
                  updated='2026-11-03T09:00:00Z', **{'from': {'prototype': 'Start higher', 'kit': '1.1.0'}})] if atlas else []
    tmp = SCANS['tmp']
    pa, pp = os.path.join(tmp, 'atlas_notes.json'), os.path.join(tmp, 'proto_notes.json')
    json.dump(atlas, open(pa, 'w')); json.dump(proto, open(pp, 'w'))
    rep = subprocess.run([sys.executable, '-m', 'atlas_kit.notes', pa, pp], cwd=KIT, capture_output=True, text=True).stdout
    sect = next((x for x in rep.split('## ') if x.startswith('VS-001')), '')
    ok('· atlas (' in sect and '· prototype (' in sect, '“check my notes”: the Atlas’s note and a listed prototype’s come back together under VS-001')


def t_states():
    print('Q35: the new starting states, both flows and the viewer (a copy of the app)')
    from atlas_kit import engine
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix='q35-', dir=SCANS.setdefault('tmp', tempfile.mkdtemp(prefix='vs-atlas-test-')))
    app = app_copy(tmp)   # its own copy: the scan test above changes its copy of the app
    want = ['today', 'song-page'] + list(Q35_STATES) + ['session-application', 'check-timing', 'settings-backup']
    sp = settings_for(tmp, app, [dict(r, taps=False) for r in S.ROOTS if r['id'] in want])
    out = os.path.join(tmp, 'scan-q35'); os.makedirs(out)
    A = engine.scan(sp, app, out, workers=2, taps=False, say=lambda *a: None, scan_id='T35')
    by = {s.get('slug', s['id']): s for s in A['screens']}
    ids = {'coach-video': 'VS-015', 'session-recording': 'VS-004~recording', 'session-takes': 'VS-004~takes', 'session-compare': 'VS-004~compare',
           'song-how': 'VS-031', 'peek-card': 'VS-095', 'check-timing-overlaps': 'VS-011~overlaps', 'track-past-end': 'VS-072', 'backup-rescued': 'VS-019~rescued-data', 'rescued-delete': 'VS-080'}
    for k, v in ids.items():
        s = by.get(k) or {}
        ok(s.get('status') == 'captured' and s.get('id') == v and s.get('shot') and os.path.exists(os.path.join(out, s['shot'])),
           f'{k}: captured as {v}' + ('' if s.get('status') == 'captured' else f' ({s.get("status")}: {s.get("why")})'))
    ok(not any(s['status'] == 'uncaptured' and s['key'] in ('Screen:coach', 'Sheet:how', 'Sheet:trkPast') for s in A['screens']), 'none of them is left as found in code only')
    ok(by['song-how']['caption'] == S.CAPTIONS['VS-031'] and by['session-takes']['caption'] == S.CAPTIONS['VS-004~takes'], 'captions reach screens and states')
    ok(any(d['from'] == 'VS-009' and d['to'] == 'VS-095' and d['kind'] == 'Hold' for d in A['doors']), 'hand-written doors are matched to screens (VS-009 › hold › VS-095)')
    fl = {f['id']: f for f in A['flows']}
    F1 = [x['screen'] for x in fl.get('F-01', {}).get('steps', [])]
    F2 = [x['screen'] for x in fl.get('F-02', {}).get('steps', [])]
    ok(fl.get('F-01', {}).get('status') == 'captured' and F1[:2] == ['VS-001', 'VS-002'] and 'VS-003' in F1 and 'VS-004' in F1 and F1[-2:] == ['VS-005', 'VS-001'],
       f'F-01 · Focused session steps through Today, Foundation, Rotation, Application, Session saved ({fl.get("F-01", {}).get("why") or F1})')
    ok(fl.get('F-02', {}).get('status') == 'captured' and F2[:4] == ['VS-001', 'VS-008', 'VS-009', 'VS-012'] and F2[-2:] == ['VS-031', 'VS-044'],
       f'F-02 · Song practice steps through Songs, the song, Song practice, How did it go?, saved ({fl.get("F-02", {}).get("why") or F2})')
    ok(all(x.get('shot') and os.path.exists(os.path.join(out, x['shot'])) for f in A['flows'] for x in f['steps']), 'every flow step has its picture')
    v = Serve(out)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1440, 'height': 900}); pg = ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.add_init_script(FAKE_STORE); pg.goto(v.url); pg.wait_for_selector('.card')
            ok(S.CAPTIONS['VS-015'] in pg.inner_text('.card[data-id="VS-015"]'), 'Mac: captions show on cards')
            pg.click('[data-view="map"]'); pg.wait_for_timeout(300)
            ok(pg.locator('#map path.edge.door').count() >= 1, 'Mac: hand-written doors are drawn on the map as dotted lines')
            pg.click('[data-view="flows"]'); pg.wait_for_selector('.fstage')
            seen = []
            for i in range(len(fl['F-01']['steps'])):
                seen.append(pg.inner_text('.finfo .sid') if pg.locator('.finfo .sid').count() else None)
                if i < len(fl['F-01']['steps']) - 1: pg.click('[data-fgo="1"]'); pg.wait_for_timeout(60)
            ok(seen == F1, 'Mac: F-01 steps through in the viewer, each step linked to its screen')
            ok(not errs, 'Mac: no errors' + (': ' + '; '.join(errs[:2]) if errs else ''))
            b.close()
    finally:
        v.close()


PARTS = {'code': t_code, 'docs': t_docs, 'rules': t_rules, 'settings': t_settings, 'kit': t_kit, 'git': t_git, 'scan': t_scan, 'viewer': t_viewer,
         'states': t_states}
if __name__ == '__main__':
    try:
        for n in (sys.argv[1:] or list(PARTS)):
            try: PARTS[n]()
            except Exception as e:
                import traceback; traceback.print_exc(); FAILS.append(f'{n} crashed: {e}')
    finally:
        if 'tmp' in SCANS: shutil.rmtree(SCANS['tmp'], ignore_errors=True)
    print(f'\n{PASSED} passed, {len(FAILS)} failed')
    for f in FAILS: print('  FAIL  ' + f)
    sys.exit(1 if FAILS else 0)
