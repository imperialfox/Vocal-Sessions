"""Visual App Atlas (Q30) · the scanner.

Opens Vocal Sessions in throwaway headless browsers filled with sample data (never real data), with the clock frozen and
motion off. Starting from the tabs and a few states (screens.ROOTS), it captures each screen (top of screen and full
length), taps every button on it on a reset copy and records where each one lands. Any screen or sheet a tap opens
that hasn't been captured yet is then opened the same way, through that real button, captured and tapped in turn,
until nothing new turns up. Screens the code can show that no tap reached are listed as "Not captured yet".

Writes <out>/atlas.json and <out>/shots/. Used by atlas.py; the Playwright version should match the tests'.
"""
import os, re, sys, json, time, hashlib, datetime as dt, subprocess, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inventory as INV
import screens as S

TAP_WAIT = 160      # ms after a tap for the app to draw
MAX_BUTTONS = 40    # per screen
MAX_PASSES = 5


# ---------- the sample data ----------
def make_seed(repo):
    """The tests' sample data plus one song (lyrics, sections, marks), made at the frozen time. Returns
    (saved data, the song's id, a generated track file)."""
    sys.path.insert(0, os.path.join(repo, 'tests'))
    from playwright.sync_api import sync_playwright
    import harness, test_layout, test_track
    harness.now = S.FIXED_TIME  # the sample's dates are counted back from the frozen time
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = open_app(b, repo, harness.sample(), dark=False)
        pg.evaluate(test_layout.SONG)
        seed = json.loads(pg.evaluate("localStorage.getItem('vocalTracker')")); song_id = pg.evaluate("U.songId")
        b.close()
    return seed, song_id, test_track.track()


def open_app(b, repo, data, dark=False, errors=None):
    """A fresh app page (like the tests' harness.page), with the clock frozen at S.FIXED_TIME."""
    sys.path.insert(0, os.path.join(repo, 'tests'))
    import harness
    ctx = b.new_context(viewport={'width': S.VIEWPORT['w'], 'height': S.VIEWPORT['h']}, device_scale_factor=2,
                        color_scheme='dark' if dark else 'light', has_touch=False, accept_downloads=False,
                        timezone_id='Europe/London', locale='en-GB', user_agent=harness.UA_IPHONE)
    ctx.clock.install(time=S.FIXED_TIME.timestamp())
    ctx.add_init_script("try{localStorage.setItem('vocalMotion','0')}catch(e){}")
    pg = ctx.new_page()
    if errors is not None:
        pg.on('pageerror', lambda e: errors.append(str(e).splitlines()[0][:240]))
        pg.on('console', lambda m: errors.append('console: ' + m.text[:240]) if m.type == 'error' else None)
    pg.goto(harness.url(os.path.join(repo, 'index.html')))
    pg.evaluate(harness.SEED, data)
    pg.reload()
    harness.ready(pg)
    return pg


# ---------- one worker: capture some screens and tap their buttons ----------
def skip_reason(a, v):
    if a in S.SAFE_ACTIONS: return None
    for rx, why in S.SKIP:
        if re.search(rx, a): return why
    return None


# a sheet's own buttons are looked for inside the sheet, so a row underneath with the same action can't be tapped instead
BUTTONS = """()=>{const sh=document.querySelector('.scrim .sheet'),root=sh||document,pre=sh?'.scrim .sheet ':'';const seen=new Set(),out=[];
  root.querySelectorAll('[data-a]').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||!r.height)return;
   if(e.closest('[hidden]'))return;
   const k=e.dataset.a+'|'+(e.dataset.v||'')+'|'+(e.dataset.k||'');if(seen.has(k))return;seen.add(k);
   const q=s=>s.replace(/["\\\\]/g,'\\\\$&');
   const lbl=(e.getAttribute('aria-label')||e.innerText||e.textContent||e.title||'').replace(/\\s+/g,' ').trim().slice(0,60);
   out.push({a:e.dataset.a,v:e.dataset.v||'',k:e.dataset.k||'',label:lbl,
    sel:pre+'[data-a="'+q(e.dataset.a)+'"]'+(e.dataset.v?'[data-v="'+q(e.dataset.v)+'"]':'')+(e.dataset.k?'[data-k="'+q(e.dataset.k)+'"]':'')})});
  return out}"""


def job(args):
    entries, repo, out, seed, song_id, track_file, taps = args
    from playwright.sync_api import sync_playwright
    sys.path.insert(0, os.path.join(repo, 'tests'))
    import test_layout
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        errors = []

        def fresh(setup):
            data = None if 'empty' in setup else seed
            pg = open_app(b, repo, data, dark='dark' in setup, errors=errors)
            if 'track' in setup or 'takes' in setup:
                pg.evaluate("id=>go(()=>{U.sheet=null;U.tab='songs';U.view='lyr';U.songId=id})", song_id)
            if 'track' in setup:  # through the song page's real Add track button, with the file picker
                with pg.expect_file_chooser(timeout=5000) as fc: pg.click('#app [data-a=trkAdd]')
                fc.value.set_files(track_file)
                pg.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()", arg=song_id, timeout=20000)
            if 'takes' in setup:
                pg.evaluate(test_layout.TAKES)
                pg.wait_for_function("()=>TAKES.length>=3", timeout=5000)
            for k in setup:
                if k in S.SETUP_JS: pg.evaluate(S.SETUP_JS[k])
            pg.evaluate(S.SNAPSHOT)   # what every tap goes back to
            pg.evaluate(S.RESET)
            pg.wait_for_timeout(60)
            return pg

        def tap(pg, sel, force=False):
            loc = pg.locator(sel.replace('{song}', song_id)).first
            if force: loc.dispatch_event('click')
            else: loc.click(timeout=2500)
            pg.wait_for_timeout(TAP_WAIT)

        def open_(pg, ent):
            for st in ent['steps']:
                kind, arg = st[0], st[1]
                if kind == 'js':  # a shortcut, for set-up only
                    pg.evaluate("js=>go(()=>{eval(js)})", arg); pg.wait_for_timeout(TAP_WAIT); continue
                try:
                    tap(pg, arg, force=(kind == 'force'))
                except Exception:
                    raise RuntimeError('Didn’t open: couldn’t tap ' + arg.replace('{song}', 'the song') + ' on the way there (not on screen)')
            pg.wait_for_timeout(80)
            return S.sig(pg.evaluate(S.STATE))

        for ent in entries:
            sid = ent['id']
            r = {'id': sid, 'status': 'captured', 'errors': [], 'links': []}
            errors.clear()
            pg = None
            try:
                pg = fresh(ent['setup'])
                landed = open_(pg, ent)
                r['sig'] = landed
                want = ent.get('expect')
                if want and S.family(landed) != S.family(want):
                    raise RuntimeError('Didn’t open: landed on ' + S.describe(landed) + ' instead')
                if not want and not S.family(landed).startswith(ent['key']):
                    raise RuntimeError('Didn’t open: landed on ' + S.describe(landed) + ' instead')
                if ent['kind'] == 'Sheet' and not pg.locator('.scrim .sheet').count():
                    raise RuntimeError('Didn’t open: the sheet isn’t on screen')
                r['title'] = pg.evaluate(S.TITLE_JS)
                pg.screenshot(path=os.path.join(out, 'shots', sid + '.jpg'), type='jpeg', quality=82)
                pg.screenshot(path=os.path.join(out, 'shots', sid + '-full.jpg'), type='jpeg', quality=78, full_page=True)
                r['fullHeight'] = pg.evaluate("document.documentElement.scrollHeight")
                r['errors'] = list(dict.fromkeys(errors))
                if not taps or not ent.get('taps', True):
                    res[sid] = r; pg.context.close(); continue
                btns = pg.evaluate(BUTTONS)
                look = [b['sel'] for b in btns]      # how the screen should look each time it's put back
                btns = btns[:MAX_BUTTONS]
                for bt in btns:
                    link = {'action': bt['a'], 'value': bt['v'], 'label': bt['label'] or bt['a'], 'selector': bt['sel']}
                    why = skip_reason(bt['a'], bt['v'])
                    if why:
                        link.update(how='not-tested', why=why); r['links'].append(link); continue
                    try:
                        pg.evaluate(S.RESET); before = open_(pg, ent)
                        if before != landed or [b['sel'] for b in pg.evaluate(BUTTONS)] != look:
                            # something from the last tap is still showing: start this screen again on a fresh copy
                            pg.context.close(); pg = fresh(ent['setup']); before = open_(pg, ent)
                        if before != landed:
                            link.update(how='not-tested', why='Not tested: couldn’t put the screen back as it was to try it'); r['links'].append(link); continue
                        loc = pg.locator(bt['sel']).first
                        if not loc.count() or not loc.is_visible() or loc.evaluate("e=>!!(e.closest('.sw')&&!e.closest('.fg'))||!!e.closest('[aria-hidden=true]')"):
                            link.update(how='not-tested', why='Not tested: only shows after a swipe, a hold or a menu'); r['links'].append(link); continue
                        n = len(errors)
                        try:
                            tap(pg, bt['sel'])
                        except Exception as e:
                            msg = str(e)
                            if 'intercept' in msg or 'not stable' in msg or 'outside of the viewport' in msg or 'Timeout' in msg:
                                tap(pg, bt['sel'], force=True)   # another layer covers it: tap the button itself
                                link['forced'] = True
                            else: raise
                        after = S.sig(pg.evaluate(S.STATE))
                        if len(errors) > n: link.update(how='broken', why=errors[-1][:200])
                        elif after == before: link.update(how='stays')
                        else: link.update(how='seen', toSig=after)
                    except Exception as e:
                        first = str(e).strip().splitlines()[0][:160] if str(e).strip() else type(e).__name__
                        link.update(how='not-tested', why='Not tested: couldn’t tap it (' + first + ')')
                    r['links'].append(link)
                pg.context.close()
            except Exception as e:
                r['status'] = 'failed'; r['why'] = (str(e).strip().splitlines() or [type(e).__name__])[0][:220]
                r['errors'] = list(dict.fromkeys(errors))
                for f in (sid + '.jpg', sid + '-full.jpg'):  # a failed capture never keeps a picture
                    try: os.remove(os.path.join(out, 'shots', f))
                    except OSError: pass
                try:
                    if pg: pg.context.close()
                except Exception: pass
            res[sid] = r
        b.close()
    return res


def run_parallel(entries, workers, common):
    if not entries: return {}
    n = max(1, min(workers, len(entries)))
    parts = [entries[i::n] for i in range(n)]
    out = {}
    if n == 1:
        out.update(job((parts[0],) + common))
    else:
        with cf.ProcessPoolExecutor(n) as ex:
            for r in ex.map(job, [(p,) + common for p in parts]): out.update(r)
    return out


# ---------- docs, changelog ----------
def docs_for(key, area, extra, sections, problems):
    want = list(extra or [])
    want += S.KEY_DOCS.get(key, [])
    for pre, d in S.PREFIX_DOCS:
        if key.startswith(pre): want += d
    want += S.AREA_DOCS.get(area, [])
    out = []
    for f, label in want:
        hit = next((d for d in sections if d['file'] == f and d['label'] == label), None)
        if not hit: problems.add(f + ' › ' + label); continue
        d = {'file': f, 'heading': hit['label'], 'url': hit['url'], 'anchor': hit['anchor']}
        if d not in out: out.append(d)
    return out[:3]


def mention_for(key, title, log):
    words = [w.lower() for w in (S.WORDS.get(key) or [title.split(' · ')[0]])]
    for c in log:
        t = c['title'].lower()
        if any(re.search(r'\b' + re.escape(w) + r'\b', t) for w in words): return c
    return None


# ---------- the whole scan ----------
def scan(repo, out, workers=2, taps=True, only=None, prev=None, say=print, scan_id=None, roots=None):
    t0 = time.time()
    repo = os.path.abspath(repo); out = os.path.abspath(out)
    os.makedirs(os.path.join(out, 'shots'), exist_ok=True)
    inv = INV.inventory(repo)
    say(f'Code: {len(inv)} screens and sheets the app can show')
    seed, song_id, track_file = make_seed(repo)
    common = (repo, out, seed, song_id, track_file, taps)

    entries, results = [], {}
    for r in (roots if roots is not None else S.ROOTS):
        if only and r['id'] not in only: continue
        e = dict(r, docs=r.get('docs', []), how='Root')
        if e.get('state_of') and 'taps' not in e: e['taps'] = False  # a state shares its screen's links
        entries.append(e)
    gone_roots = [e for e in entries if e['key'] not in inv]
    queue = [e for e in entries if e['key'] in inv]
    fams = {}  # family -> entry id (captured or queued)
    for e in queue:
        if not e.get('state_of'): fams[e['key']] = e['id']
    passes = 0
    while queue and passes < MAX_PASSES:
        passes += 1
        say(f'Pass {passes}: {len(queue)} screen' + ('s' if len(queue) != 1 else ''))
        results.update(run_parallel(queue, workers, common))
        for e in queue:
            r = results[e['id']]
            if r.get('sig') and r['status'] == 'captured' and not e.get('state_of'):
                fams.setdefault(S.family(r['sig']), e['id'])
        if only or not taps: break
        queue = []
        for e in list(entries):  # every link seen working that opens something not captured yet becomes its door
            r = results.get(e['id'])
            if not r or r['status'] != 'captured': continue
            for l in r['links']:
                if l.get('how') != 'seen': continue
                fam = S.family(l['toSig'])
                if fam in fams: continue
                kind = 'Sheet' if fam.startswith('Sheet:') else 'Sub-page' if fam.startswith('Sub-page:') else 'Screen'
                ninv = 'Screen:' + fam.split(':')[1] if fam.startswith('Screen:') else fam
                nid = re.sub(r'[^a-z0-9]+', '-', fam.lower()).strip('-')
                step = ('force' if l.get('forced') else 'tap', l['selector'])
                ne = dict(id=nid, fam=fam, title=None, area=S.area_of(l['toSig']), kind=kind, key=ninv, steps=list(e['steps']) + [step],
                          setup=list(e['setup']), expect=l['toSig'], docs=[], how='Found', via={'from': e['id'], 'label': l['label']})
                fams[fam] = nid; entries.append(ne); queue.append(ne)

    # ---------- put it together ----------
    sections = INV.doc_sections(repo); log = INV.changelog(repo); problems = set()
    by_id = {e['id']: e for e in entries}
    plain_by_sig, by_fam, by_sheet = {}, {}, {}
    for e in entries:
        r = results.get(e['id'])
        if not r or r['status'] != 'captured' or not r.get('sig'): continue
        if not e.get('state_of'): plain_by_sig.setdefault(r['sig'], e['id'])
        if not e.get('state_of'): by_fam.setdefault(S.family(r['sig']), e['id'])
        sh = r['sig'].split('|')[2]
        if sh and not e.get('state_of'): by_sheet.setdefault(sh, e['id'])
    for e in entries:  # a state's sig points to its plain screen
        r = results.get(e['id'])
        if r and r.get('sig') and e.get('state_of'): plain_by_sig.setdefault(r['sig'], e['state_of'])

    screens = []
    for e in entries:
        r = results.get(e['id']) or {'status': 'gone', 'errors': [], 'links': []}
        if e in gone_roots:
            r = {'status': 'gone', 'why': 'In the Atlas’s list, but the code no longer has ' + e['key'], 'errors': [], 'links': []}
        for l in r['links']:
            a = l['action']
            if l.get('toSig'):
                to = plain_by_sig.get(l['toSig'])
                tsh = l['toSig'].split('|')[2]
                if not to and tsh: to = by_sheet.get(tsh)
                if not to:
                    to = by_fam.get(S.family(l['toSig']))
                    if to: l['family'] = S.describe(l['toSig'])
                l['to'] = to
                if not to: l['toLabel'] = S.describe(l['toSig'])
            l['kind'] = ('Tab bar' if a in ('tab', 'findOpen') else 'Back' if a.lower().endswith('back') or a in ('close', 'setPgBack')
                         else 'Opens a sheet' if l.get('toSig') and l['toSig'].split('|')[2] and not (r.get('sig') or '||').split('|')[2] else 'Button')
        fam = e.get('fam') or e['key']
        head = (r.get('title') or '').strip()
        title = (e.get('title') or S.TITLES.get(fam) or S.TITLES.get(e['key'])
                 or (S.TITLE_PREFIX[fam] + (' · ' + head if head else '') if fam in S.TITLE_PREFIX else None)
                 or head or S.describe(r.get('sig') or e.get('expect') or e['key']))
        area = e['area'] if e['area'] in S.AREAS else 'Other'
        shot = 'shots/' + e['id'] + '.jpg' if r['status'] == 'captured' else None
        how = ' → '.join(('tap ' if s[0] == 'tap' else 'forced tap ' if s[0] == 'force' else 'shortcut ') + s[1] for s in e['steps']) or 'the app as it opens'
        if e['setup']: how = 'set up with ' + ', '.join(e['setup']) + '; ' + how
        screens.append({
            'id': e['id'], 'title': title, 'area': area, 'kind': e['kind'], 'key': e['key'], 'setup': e['setup'],
            'stateOf': e.get('state_of'), 'found': e['how'], 'via': e.get('via'), 'how': how,
            'status': r['status'], 'why': r.get('why'), 'errors': r.get('errors', []), 'sig': r.get('sig'),
            'shot': shot, 'full': 'shots/' + e['id'] + '-full.jpg' if shot else None, 'fullHeight': r.get('fullHeight'),
            'hash': hashlib.sha1(open(os.path.join(out, shot), 'rb').read()).hexdigest()[:12] if shot else None,
            'links': r['links'], 'docs': docs_for(e['key'], area, e.get('docs'), sections, problems),
            'mention': mention_for(e['key'], title, log)})
    by = {s['id']: s for s in screens}
    for s in screens:
        s['from'] = [{'from': o['id'], 'label': l['label'], 'how': l['how']} for o in screens for l in o['links']
                     if l.get('to') == s['id'] and o['id'] != s['id'] and not o.get('stateOf')]
        if s.get('stateOf') and not s['links'] and s['stateOf'] in by:
            s['linksOf'] = s['stateOf']

    # what the code can show that this scan didn't reach
    have = set()
    for s in screens:
        if s['status'] == 'captured' and s['sig']: have.update(S.keys_of(s['sig']))
    tried = {s['key'] for s in screens if s['status'] == 'failed'}
    uncaptured = []
    for k, v in sorted(inv.items(), key=lambda kv: (['Tab', 'Screen', 'Sub-page', 'Sheet'].index(kv[1]['kind']), kv[0])):
        if k in have or k in tried: continue
        uncaptured.append({'id': 'code-' + re.sub(r'[^a-z0-9]+', '-', k.lower()).strip('-'), 'title': v['name'], 'kind': v['kind'],
                           'key': k, 'area': 'Not captured yet', 'status': 'uncaptured',
                           'why': 'Found in the code (' + v['where'] + '), but no button the scan tapped opened it',
                           'links': [], 'from': [], 'docs': [], 'errors': []})

    # compared with the last scan's code list: what's new and what's gone (the full comparison is Q31)
    code_changes = None
    if prev and os.path.exists(os.path.join(prev, 'atlas.json')):
        pa = json.load(open(os.path.join(prev, 'atlas.json'), encoding='utf-8'))
        pinv = set(pa.get('inventory', []))
        code_changes = {'since': pa['scan'].get('id'), 'sinceVersion': pa['scan'].get('version'),
                        'added': sorted(set(inv) - pinv), 'gone': sorted(pinv - set(inv))}
        for k in code_changes['gone']:
            kind, name = k.split(':', 1)
            uncaptured.append({'id': 'gone-' + re.sub(r'[^a-z0-9]+', '-', k.lower()).strip('-'), 'title': name, 'kind': kind, 'key': k,
                               'area': 'No longer in the code', 'status': 'gone',
                               'why': 'In the code at the last scan (' + str(pa['scan'].get('version')) + '), not any more',
                               'links': [], 'from': [], 'docs': [], 'errors': []})

    head = subprocess.run(['git', '-C', repo, 'log', '-1', '--format=%h %s'], capture_output=True, text=True).stdout.strip()
    ver = re.search(r"APP_VERSION\s*=\s*'([^']+)'", open(os.path.join(repo, 'index.html'), encoding='utf-8').read())
    now = dt.datetime.now(dt.timezone.utc)
    atlas = {'format': 3, 'app': S.APP,
             'scan': {'id': scan_id or now.strftime('%Y%m%dT%H%M%SZ'), 'at': now.isoformat(timespec='seconds'), 'seconds': round(time.time() - t0),
                      'commit': head, 'version': ver.group(1) if ver else (log[0]['version'] if log else ''),
                      'viewport': S.VIEWPORT, 'data': S.DATA, 'clock': S.FIXED_TIME.isoformat(), 'passes': passes,
                      'codeStates': len(inv), 'codeChanges': code_changes, 'docProblems': sorted(problems),
                      'prev': os.path.basename(prev) if prev else None},
             'areas': S.AREAS, 'inventory': sorted(inv), 'screens': screens + uncaptured}
    json.dump(atlas, open(os.path.join(out, 'atlas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    c = lambda st: sum(s['status'] == st for s in atlas['screens'])
    nl = [l for s in screens for l in s['links']]
    say(f"{c('captured')} captured, {c('failed')} failed, {c('uncaptured')} found in code only, {len(nl)} buttons "
        f"({sum(l['how'] == 'seen' for l in nl)} seen working, {sum(l['how'] == 'stays' for l in nl)} change their screen, "
        f"{sum(l['how'] == 'not-tested' for l in nl)} not tested, {sum(l['how'] == 'broken' for l in nl)} broken), {round(time.time() - t0)} s")
    if code_changes and (code_changes['added'] or code_changes['gone']):
        say('Since the last scan, in the code: ' + ', '.join(['+ ' + k for k in code_changes['added']] + ['– ' + k for k in code_changes['gone']]))
    if problems: say('Doc sections not found: ' + '; '.join(sorted(problems)))
    return atlas
