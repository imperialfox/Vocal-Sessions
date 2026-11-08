"""3.50 Screen IDs (Q36): the register (js/register.js) against the code, every screen's ID on the page, part names,
flows, docs links, the Show screen IDs label, the Changelog's Screens line, and the saved-data list
(MAINTAINING › Where data lives) against every storage key in the code."""
import os, re, sys
import harness
from harness import sample, until
from test_guide import song, mark_side, hold

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'atlas'))
import screens as INV  # the Atlas's settings (Q31; Q30's inventory.py before): inventory() reads every screen the code can show
from atlas_kit import docs as ATLAS_DOCS  # the Atlas kit's reading of the docs (tools/atlas/kit, on the path through screens.py)

PART_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
KINDS = {'Tab', 'Screen', 'Sub-page', 'Sheet', 'Alert', 'Action sheet', 'Overlay'}  # Q41 alerts and action sheets are the parts kit's
REG = "JSON.parse(JSON.stringify(SCREENS))"
HERE = "()=>[document.getElementById('app').dataset.screen,SCR.viewKey()]"
SHEET_ID = "()=>{const s=document.querySelector('#layer :is(.sheet,.pk-alert,.pk-actions):not(.pk-leaving),#layer .clock');return s?s.dataset.screen||'':null}"


def src_all():
    out = ''
    for f in sorted(os.listdir(os.path.join(ROOT, 'js'))):
        if f.endswith('.js') and f != 'register.js': out += open(os.path.join(ROOT, 'js', f), encoding='utf-8').read() + '\n'
    return out


# the U values that show a screen, from its code key
def state_js(key):
    kind, _, rest = key.partition(':')
    if kind == 'tab': return f"go(()=>{{U.tab='{rest}';U.view=null;U.sheet=null}})"
    v, _, sub = rest.partition('/')
    tab = {'set': 'settings', 'guide': 'settings', 'log': 'settings', 'all': 'history', 'ex': 'exercises', 'coach': 'exercises',
           'pat': 'exercises', 'lyr': 'songs', 'trk': 'songs', 'ckCheck': 'songs', 'song': 'songs'}.get(v, 'today')
    extra = ''
    if v == 'set': extra = f"U.setPg='{sub}';"
    if v == 'guide': extra = "U.gPg=" + ("Object.keys(MK_DEF)[0]" if sub == 'mark' else f"'{sub}'") + ";"
    if v == 'ex': extra = "U.exId=FOUND[0].id;"
    if v in ('lyr', 'trk', 'ckCheck'): extra = "U.songId='g_1';"
    pre = ''
    if v in ('found', 'rot', 'app'): pre = "if(!X)newSession();"
    if v == 'song': pre = "if(!X)newSong();X.song='g_1';"
    if v == 'saved': pre = "U.saved={k:D.sessions[D.sessions.length-1].id};"
    return f"(()=>{{{pre}go(()=>{{U.tab='{tab}';U.view='{v}';{extra}U.sheet=null}})}})()"


def register(b, t):
    ok = t.ok
    pg = t.page(b)
    R = pg.evaluate(REG)
    S = R['screens']
    ids = [s['id'] for s in S]
    ok(ids == ['VS-%03d' % (i + 1) for i in range(len(S))], f'{len(S)} screens numbered VS-001 to VS-{len(S):03d} in order, none skipped or used twice')
    ok(len({s['key'] for s in S}) == len(S), 'every code key is in the register once')
    ok(all(s['kind'] in KINDS and s['name'] and s['area'] and (s['status'] == 'Live' or re.fullmatch(r'Retired in \d+\.\d+(\.\d+)?', s['status'])) for s in S),
       'each has a name, an area, a kind and a status (Live, or Retired in a version)')
    bad = [s['id'] + ' › ' + p['name'] for s in S for p in s['parts'] if not PART_RE.match(p['name']) or not p.get('sel')]
    bad += [p['name'] for p in R['shared'] if not PART_RE.match(p['name'])]
    ok(not bad, f'part names are lower case with hyphens, each with where it is ({bad})')
    dup = [s['id'] for s in S if len({p['name'] for p in s['parts']}) != len(s['parts'])]
    ok(not dup, f'no screen names two parts the same ({dup})')
    # flows
    F = R['flows']
    ok([f['id'] for f in F] == ['F-%02d' % (i + 1) for i in range(len(F))] and len(F) >= 5, 'flows numbered F-01 onwards')
    ok([f['name'] for f in F[:5]] == ['Focused session', 'Song practice', 'Add a song', 'Time a song', 'Back up and restore'],
       'the five flows: Focused session, Song practice, Add a song, Time a song, Back up and restore')
    by = {s['id']: s for s in S}
    shared = {p['name'] for p in R['shared']}
    badst = []
    for f in F:
        for st in f['steps']:
            s = by.get(st['screen'])
            if not s or s['status'] != 'Live': badst.append(f['id'] + ': ' + st['screen'])
            elif st.get('part') and st['part'] not in {p['name'] for p in s['parts']} | shared: badst.append(f"{f['id']}: {st['screen']} › {st['part']}")
    ok(not badst, f'every flow step is a Live screen, and every part tapped is one of that screen’s named parts ({badst})')
    ok(all(len(f['steps']) >= 3 for f in F), 'each flow has at least three steps')

    # against the code (the Atlas's inventory reads render(), renderSheet() and every U.tab / U.view / U.sheet)
    inv = INV.inventory(ROOT)
    aliases = {a for s in S for a in s['aliases']}
    missing = sorted(k for k in inv if k not in aliases and k not in ('Screen:set', 'Screen:guide'))
    ok(not missing, f'every screen the code can show ({len(inv)} found) has a register entry ({missing})')
    allsrc = src_all()
    gone = []
    for s in S:
        if s['status'] != 'Live': continue
        kind, _, rest = s['key'].partition(':')
        v, _, sub = rest.partition('/')
        have = {'tab': 'Tab:' + rest, 'sheet': 'Sheet:' + rest}.get(kind)
        if kind == 'view':
            have = 'Sub-page:' + sub if v == 'set' else 'Screen:' + v
            if v == 'guide' and sub not in ('home', 'how', 'mark'): have = None
        if kind == 'overlay':
            if "'" + s['key'] + "'" not in allsrc: gone.append(s['id'])
        elif have not in inv: gone.append(s['id'] + ' ' + s['key'])
    ok(not gone, f'every Live entry’s code key is still in the code ({gone})')
    # every part is in the code: its data-a / data-v value or its #id
    nopart = []
    for s in S:
        for p in s['parts'] + ([] if s is not S[0] else R['shared'] + R['actions']):
            if p.get('status', 'Live') != 'Live': continue  # a retired part's button has left the code (Q51: sgQCancel)
            for a in re.findall(r'data-a="([A-Za-z]+)"', p['sel']):
                if not re.search(r'data-a=\\?"' + a + r'\\?"|\'' + a + r'\'', allsrc): nopart.append(s['id'] + ' › ' + p['name'])
            for i in re.findall(r'#([A-Za-z]+)', p['sel']):
                if not re.search(r'id=\\?"' + i + r'\\?"|\.id = \'' + i + "'|'" + i + "'", allsrc) and i not in ('dock', 'barL', 'app'): nopart.append(s['id'] + ' › ' + p['name'])
    ok(not nopart, f'every named part’s button is still in the code ({nopart})')
    # docs links point at real headings
    secs = {s['file'] + '#' + s['anchor'] for s in ATLAS_DOCS.doc_sections(ROOT, INV.DOC_FILES)}
    nodoc = [s['id'] + ' ' + s['docs'] for s in S if s['docs'] not in secs]
    ok(not nodoc, f'every docs link points at a real heading in README.md or MAINTAINING.md ({nodoc})')
    pg.context.close()


def on_page(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        pg = t.page(b, sc=sc)
        S = pg.evaluate(REG)['screens']
        pg.evaluate("localStorage.setItem('vocalLook',JSON.stringify({ids:true}))")
        pg.reload(); harness.ready(pg)
        wrong, unnamed, labels, seen = [], [], [], {}
        for s in S:
            if s['kind'] not in ('Tab', 'Screen', 'Sub-page'): continue
            pg.evaluate(state_js(s['key'])); pg.wait_for_timeout(60)
            got = pg.evaluate(HERE)
            if got != [s['id'], s['key']]: wrong.append(f"{s['id']} {s['key']} → {got}")
            # the parts on screen carry their names
            res = pg.evaluate("""s=>{const r=[document.getElementById('app'),document.getElementById('bar'),document.getElementById('dock')];
              return s.parts.concat(SCREENS.shared).map(p=>{const els=r.flatMap(x=>[...x.querySelectorAll(p.sel)]);
              return [p.name,els.length,els.every(e=>e.dataset.name===p.name)]})}""", s)
            for n, cnt, named in res:
                if cnt: seen[s['id'] + ' › ' + n] = 1
                if cnt and not named: unnamed.append(s['id'] + ' › ' + n)
            lab = pg.evaluate("document.getElementById('scrid')&&document.getElementById('scrid').textContent")
            if lab != s['id']: labels.append(f"{s['id']}: {lab}")
        ok(not wrong, f'{sc}: every tab, screen and sub-page carries its ID as data-screen ({wrong})')
        ok(not unnamed, f'{sc}: every named part on screen carries its data-name ({unnamed})')
        ok(not labels, f'{sc}: with Show screen IDs on, the label shows the right ID on every one ({labels})')
        if sc == 'light':
            want = ['VS-001 › start-session-button', 'VS-001 › week-goal', 'VS-001 › rotation-row', 'VS-001 › song-practice-card',
                    'VS-008 › song-row', 'VS-008 › new-song-button', 'VS-018 › settings-row', 'VS-019 › export-row', 'VS-019 › import-row',
                    'VS-025 › screen-ids-switch', 'VS-002 › step-button', 'VS-003 › finish-here-button']
            ok(all(w in seen for w in want), f'the main parts are named on their screens ({[w for w in want if w not in seen]})')
        # sheets: every one this sample data can open carries its ID, and the label shows both
        opened, bad = [], []
        for s in S:
            if s['kind'] not in ('Sheet', 'Alert', 'Action sheet'): continue
            k = s['key'][6:]
            r = pg.evaluate("""k=>{const ks=[null,'g_1','s0','s2','sp1',FOUND[0].id,'c0_x'];
              for(const withX of [false,true]){if(withX&&!X)newSession();
                for(const kk of ks){U.view=null;U.tab='today';U.sheet=k;U.sd={k:kk};try{render()}catch(e){}
                  const sh=document.querySelector('#layer :is(.sheet,.pk-alert,.pk-actions):not(.pk-leaving)');if(U.sheet===k&&sh)return [sh.dataset.screen,document.getElementById('scrid').textContent]}}
              return null}""", k)
            pg.evaluate("(()=>{U.sheet=null;U.sd={};if(X){X=null;saveDraft()}render()})()")
            if r:
                opened.append(s['id'])
                if r[0] != s['id'] or r[1] != 'VS-001 · ' + s['id']: bad.append(f"{s['id']} {k}: {r}")
        nsheets = sum(1 for s in S if s['kind'] in ('Sheet', 'Alert', 'Action sheet'))
        ok(not bad and len(opened) >= 30, f'{sc}: {len(opened)} of {nsheets} sheets open from sample data, each carrying its own ID, and the label shows the screen’s then the sheet’s ({bad})')
        t.shot(pg, 'label-' + sc)
        pg.context.close()


def overlays(b, t):
    ok = t.ok
    pg = t.page(b)
    # the session clock over a running session's step
    pg.evaluate(state_js('view:found')); pg.wait_for_timeout(150)
    pg.click('#bar [data-a=clock]'); pg.wait_for_timeout(250)
    ok(pg.evaluate(SHEET_ID) == 'VS-092' and pg.locator('#layer .clock [data-name=pause-button]').count() == 1,
       'the session clock is VS-092 · Session clock, with its pause button named')
    pg.evaluate("(()=>{U.clock=false;render()})()")
    # the floating window: the session on another tab
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})")
    ok(until(pg, "(()=>{const f=document.getElementById('fw');return f&&!f.hidden&&f.dataset.screen==='VS-093'})()"),
       'the floating window is VS-093 · Floating window')
    pg.context.close()
    # the peek card
    pg = t.page(b, w=375, h=667, touch=True)
    S = song(pg)
    mark_side(pg, S)
    hold(pg, '#mksheet .mkb[data-v=peak]', 650)
    ok(pg.evaluate("(()=>{const c=document.getElementById('mkpeek');return c?c.dataset.screen:null})()") == 'VS-095'
       and pg.locator('#mkpeek [data-name=learn-more-button]').count() == 1, 'the peek card is VS-095 · Peek card, its buttons named')
    pg.context.close()
    # the launch screen, read while it's still up (motion on, so it stays nearly a second)
    ctx = b.new_context(viewport={'width': 390, 'height': 844})
    p2 = ctx.new_page()
    p2.goto(harness.url(harness.APP_PATH), wait_until='domcontentloaded')
    v = p2.evaluate("(()=>{const s=document.getElementById('splash');return s?s.dataset.screen||'':'gone'})()")
    ok(v in ('VS-094', 'gone'), f'the launch screen is VS-094 · Launch screen ({v})')
    if v == 'gone': print('  note: the launch screen had already gone; checked only that nothing went wrong')
    ctx.close()


def missing_entry(b, t):
    ok = t.ok
    pg = t.page(b)
    warns = []
    pg.on('console', lambda m: warns.append(m.text) if m.type == 'warning' else None)
    pg.evaluate("(()=>{window.__keep=SCR.BY['tab:find'];delete SCR.BY['tab:find'];go(()=>{U.tab='find';U.view=null})})()"); pg.wait_for_timeout(200)
    ok(pg.evaluate(HERE)[0] == 'VS-???', 'a screen missing from the register shows VS-???')
    ok(any('No screen ID' in w and 'tab:find' in w for w in warns), 'and warns in the console, naming its code key')
    pg.evaluate("(()=>{SCR.BY['tab:find']=window.__keep;go(()=>{U.tab='today';U.view=null})})()")
    pg.context.close()


def label(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        pg = t.page(b, sc=sc)
        before = pg.evaluate("localStorage.getItem('vocalTracker')")
        ok(pg.locator('#scrid').count() == 0, f'{sc}: no label until Show screen IDs is switched on')
        pg.evaluate(state_js('view:set/appear')); pg.wait_for_timeout(150)
        sw = pg.locator('#app [data-a=setIds]')
        ok(sw.count() == 1 and sw.get_attribute('aria-checked') == 'false' and 'Show screen IDs' in sw.inner_text(),
           f'{sc}: Settings › Appearance has a Show screen IDs switch, off')
        sw.click(); pg.wait_for_timeout(150)
        ok(pg.locator('#app [data-a=setIds]').get_attribute('aria-checked') == 'true' and pg.inner_text('#scrid') == 'VS-025',
           f'{sc}: switched on, the label shows this page’s ID, VS-025')
        ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalLook')).ids===true") and pg.evaluate("localStorage.getItem('vocalTracker')") == before,
           f'{sc}: saved on this device only (vocalLook), not in the saved data a backup carries')
        st = pg.evaluate("""(()=>{const l=document.getElementById('scrid'),c=getComputedStyle(l),r=l.getBoundingClientRect();
          const hit=[...document.querySelectorAll('#bar button,#dock button')].filter(b=>{const q=b.getBoundingClientRect();
            return q.width&&r.left<q.right&&r.right>q.left&&r.top<q.bottom&&r.bottom>q.top}).length;
          return {fs:parseFloat(c.fontSize),pe:c.pointerEvents,hidden:l.getAttribute('aria-hidden'),right:innerWidth-r.right,hit,top:r.top}})()""")
        ok(st['fs'] <= 12 and st['pe'] == 'none' and st['hidden'] == 'true' and st['right'] < 20 and st['top'] < 120 and st['hit'] == 0,
           f'{sc}: a small label in the top corner that taps go through, hidden from VoiceOver, covering no bar button ({st})')
        for key in ('tab:today', 'tab:songs', 'tab:history', 'tab:exercises'):
            pg.evaluate(state_js(key)); pg.wait_for_timeout(80)
            hit = pg.evaluate("""(()=>{const r=document.getElementById('scrid').getBoundingClientRect();
              return [...document.querySelectorAll('#bar button,#dock button')].filter(b=>{const q=b.getBoundingClientRect();
              return q.width&&r.left<q.right&&r.right>q.left&&r.top<q.bottom&&r.bottom>q.top}).map(b=>b.dataset.a)})()""")
            if hit: ok(False, f'{sc}: on {key} the label covers {hit}')
        pg.reload(); harness.ready(pg)
        ok(pg.inner_text('#scrid') == 'VS-001', f'{sc}: still on after a reload')
        pg.evaluate(state_js('view:set/appear')); pg.wait_for_timeout(150)
        pg.click('#app [data-a=setIds]'); pg.wait_for_timeout(150)
        ok(pg.locator('#scrid').count() == 0 and pg.evaluate("localStorage.getItem('vocalLook')") is None, f'{sc}: switched off, the label goes')
        pg.context.close()


def changelog(b, t):
    ok = t.ok
    pg = t.page(b)
    p = pg.evaluate("parseChangelog('## 9.1 · 3 Nov 2026\\n*Head*\\n\\n- A change.\\n\\nScreens: VS-009, VS-050\\n\\n## 9.0 · 2 Nov 2026\\n*Old*\\n\\n- One.\\n')")
    ok(p['out'][0].get('screens') == 'VS-009, VS-050' and 'screens' not in p['out'][1] and not p['warn'] and len(p['out'][0]['notes'][0][1]) == 1,
       'a version’s Screens line is read as its screens, not as a change')
    top = open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read().split('\n## ')[1]
    ok(re.search(r'^Screens: (none|VS-\d{3}(, VS-\d{3})*)$', top, re.M), 'the newest version has a Screens line')
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.click('.row[data-a=openLog]')
    ok(until(pg, "LOG_STATE==='ready'&&!!document.querySelector('.tl-item')"), 'the Changelog page loads')
    ok(pg.locator('.tl-scr').count() == 0 and 'Screens:' not in pg.inner_text('#app'), 'with Show screen IDs off, no Screens line shows')
    pg.evaluate("(()=>{SET.setIds(true);rerender()})()"); pg.wait_for_timeout(150)
    first = pg.locator('.tl-item').first
    ok(first.locator('.tl-scr').count() == 1 and first.locator('.tl-scr').inner_text().startswith('Screens: '),
       'with it on, the newest version shows its Screens line under the headline')
    pg.context.close()


def saved_data(b, t):
    ok = t.ok
    m = open(os.path.join(ROOT, 'MAINTAINING.md'), encoding='utf-8').read()
    sec = m[m.index('\n## Where data lives'):m.index('\n### Save safety')]
    rows = [l for l in sec.splitlines() if l.startswith('| ')]
    ok(all(len(l.strip('|').split(' | ')) == 5 for l in rows if not l.startswith('| Field') and not l.startswith('| `peek`') and ('vocal' in l or l.startswith('| Where'))),
       'the saved-data list has Where, Key, Holds, Since and Backed up for every key')
    src = src_all()
    keys = sorted(set(re.findall(r"'(vocal[A-Z]\w*)'", src)))
    miss = [k for k in keys if '`' + k + '`' not in sec]
    ok(len(keys) >= 15 and not miss, f'every storage key and database in the code ({len(keys)}) is in MAINTAINING › Where data lives ({miss})')
    # D.prefs fields, and the pattern player's inside it
    pf = sorted(set(re.findall(r'D\.prefs\.([a-zA-Z]+)', src)))
    pat = set(re.findall(r'^\s{4}(\w+):', re.search(r'const DEF = \{(.*?)\};', src, re.S).group(1), re.M)) | set(re.findall(r'o\.(\w+) != null', src[src.index('function clean(p)'):src.index('function clean(p)') + 4000]))
    tbl = sec[sec.index('**`D.prefs`**'):sec.index('**`vocalSongPrefs`**')]
    ok(pf and all('`' + f + '`' in tbl for f in pf), f'every D.prefs field is in its table ({pf})')
    ok(all('`' + f + '`' in tbl for f in pat), f'and every pattern player choice in D.prefs.pat ({sorted(f for f in pat if "`" + f + "`" not in tbl)})')
    sg = src[src.index('function sgp()'):]
    sg = sg[:sg.index('return SGP;\n}')]
    sf = set(re.findall(r"^\s+'(\w+)',", sg, re.M)) | set(re.findall(r'^\s{4}(\w+):', sg, re.M))
    tb2 = sec[sec.index('**`vocalSongPrefs`**'):]
    ok(len(sf) >= 10 and all('`' + f + '`' in tb2 for f in sf), f'every vocalSongPrefs field is in its table ({sorted(f for f in sf if "`" + f + "`" not in tb2)})')
    look = set(re.findall(r'look\(\)\.(\w+)', src)) | set(re.findall(r'\bo\.(grad|ids)\b', src))
    row = next(l for l in rows if '`vocalLook`' in l)
    ok(look and all('`{' + f in row for f in look), f'every vocalLook field is in its row ({sorted(look)})')


# ---------- Q48 every button and control has a name (MAINTAINING › Screen IDs › Naming rules) ----------
# The kind word every new name ends in (rule 2), and the names from before Q48 that don't, kept as they are (rule 7).
KIND_WORDS = ('button', 'row', 'switch', 'picker', 'field', 'slider', 'stepper', 'tile', 'card', 'tab', 'pill', 'chip', 'menu',
              'line', 'bar', 'link', 'option', 'item', 'word', 'dot', 'grabber')
OLD_NAMES = {'backup-nudge', 'week-goal', 'more-exercises-sort', 'step-summary', 'songs-sort', 'sheet-music-door', 'times',
             'loop-strip', 'dots-view', 'sheet-view'}
# actions that aren't buttons, each with why
NOT_BUTTONS = {
    'ckPickCancel': 'tap outside the length picker to close it; its Set button is named',
    'clockClose': 'tap outside the session clock to close it; the clock’s own buttons are named',
    'patHudClose': 'tap outside the speed panel to close it; its buttons are named',
}
# a router action: one action that opens different screens, so each value is its own button
ROUTERS = {'sheet'}
# standard roles (rule 6) may be different actions on one screen; every other name is one action per screen
ROLES = {'back-button', 'close-button', 'cancel-button', 'confirm-button', 'done-button', 'save-button'}
INTERACTIVE = "button,[data-a],input,select,textarea,a[href],[role=button],[role=switch],[role=slider],[role=tab],.pk-slider"
UNNAMED_JS = """o=>{const out=[],dup={},quiet=[];const re=/^[a-z0-9]+(-[a-z0-9]+)*$/;
 for(const r of o.roots.map(x=>document.querySelector(x)).filter(Boolean))for(const e of r.querySelectorAll(o.sel)){
  const b=e.getBoundingClientRect();if(!b.width||!b.height||e.disabled||e.closest('[aria-hidden=true]'))continue;
  if(o.skip.includes(e.dataset.a))continue;const n=e.dataset.name||'';
  if(!re.test(n)){out.push((e.dataset.a||e.id||e.tagName.toLowerCase())+(e.dataset.v?'='+e.dataset.v:'')+' “'+(e.getAttribute('aria-label')||e.innerText||'').trim().slice(0,24)+'”');continue}
  (dup[n]=dup[n]||new Set()).add(e.dataset.a||e.id||e.className);
  if(e.matches('button,[role=button]')&&!e.getAttribute('aria-label')&&!(e.innerText||'').trim()&&!e.title)quiet.push(n)}
 return {unnamed:out,dup:Object.entries(dup).filter(([n,s])=>s.size>1&&!o.roles.includes(n)).map(([n,s])=>n+' ('+[...s].join(', ')+')'),quiet}}"""


def actions_in_code():
    """Every data-a in the app's code (not the register, not js/vendor), and for a router each data-v it's written with."""
    src = src_all() + open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    acts, routed = set(), set()
    for m in re.finditer(r'data-a=\\?"([A-Za-z][\w-]*)\\?"(?:\s*data-v=\\?"([A-Za-z][\w-]*)\\?")?', src):
        acts.add(m.group(1))
        if m.group(1) in ROUTERS and m.group(2): routed.add(m.group(1) + '=' + m.group(2))
    acts |= set(re.findall(r"dataset\.a = '([A-Za-z]\w*)'", src))
    return acts, routed


def coverage(b, t):
    ok = t.ok
    pg = t.page(b)
    R = pg.evaluate(REG)
    live = lambda p: p.get('status', 'Live') == 'Live'
    allp = [('shared', p) for p in R['shared']] + [('actions', p) for p in R['actions']] + [(s['id'], p) for s in R['screens'] if s['status'] == 'Live' for p in s['parts']]
    sels = ' '.join(p['sel'] for _, p in allp if live(p))
    acts, routed = actions_in_code()
    named = set(re.findall(r'data-a="([^"]+)"', sels))
    named_routes = {a + '=' + v for a, v in re.findall(r'data-a="([^"]+)"\]\[data-v="([^"]+)"', sels)}
    miss = sorted(a for a in acts if a not in named and a not in NOT_BUTTONS and a not in ROUTERS)
    miss += sorted(r for r in routed if r not in named_routes)
    ok(not miss, f'every button in the code has a name: each data-a named in the register or on NOT_BUTTONS with a reason, each sheet it opens by its own name ({len(acts)} actions, {len(routed)} sheets opened by data-v; missing: {miss})')
    ok(all(a in acts for a in NOT_BUTTONS), f'every NOT_BUTTONS action is still in the code ({[a for a in NOT_BUTTONS if a not in acts]})')
    bad = [w + ' › ' + p['name'] for w, p in allp if live(p) and not (PART_RE.match(p['name']) and (p['name'] in OLD_NAMES or any(p['name'] == k or p['name'].endswith('-' + k) for k in KIND_WORDS)))]
    ok(not bad, f'every name is lower case with hyphens and ends in a kind word (button, row, switch…), older names aside ({bad})')
    pos = [w + ' › ' + p['name'] for w, p in allp if re.search(r':nth-|:first-child|:last-child|:first-of-type|:last-of-type', p['sel'])]
    ok(not pos, f'no part is found by its position ({pos})')
    st = [w + ' › ' + p['name'] for w, p in allp if not (live(p) or re.fullmatch(r'Retired in \d+\.\d+(\.\d+)?', p.get('status', '')))]
    ok(not st, f'a part’s status is Live or Retired in a version ({st})')
    clash = []
    for s in R['screens']:
        names = [p['name'] for p in s['parts'] if live(p)]
        old = [w for p in s['parts'] for w in p.get('was', [])]
        clash += [s['id'] + ' › ' + w for w in old if w in names]
        clash += [s['id'] + ' › ' + p['name'] for p in s['parts'] if not live(p) and p['name'] in names]
    ok(not clash, f'an old or retired name is never reused for another part on its screen ({clash})')
    pg.context.close()
    # on screen: every visible control on every screen and sheet the sample data reaches carries a name
    pg = t.page(b)
    song(pg, marks=True)
    S = R['screens']
    unnamed, dups, quiet = [], [], set()
    opt = {'sel': INTERACTIVE, 'skip': list(NOT_BUTTONS), 'roles': sorted(ROLES)}
    for s in S:
        if s['kind'] not in ('Tab', 'Screen', 'Sub-page') or s['status'] != 'Live': continue
        pg.evaluate(state_js(s['key'])); pg.wait_for_timeout(60)
        if pg.evaluate("document.getElementById('app').dataset.screen") != s['id']: continue
        r = pg.evaluate(UNNAMED_JS, dict(opt, roots=['#app', '#bar', '#dock', '#side']))
        unnamed += [s['id'] + ' ' + x for x in r['unnamed']]; dups += [s['id'] + ' ' + x for x in r['dup']]; quiet |= {s['id'] + ' › ' + x for x in r['quiet']}
    nsh = 0
    for s in S:
        if s['kind'] not in ('Sheet', 'Alert', 'Action sheet') or s['status'] != 'Live': continue
        got = pg.evaluate("""k=>{const ks=[null,'g_1','s0','s2','sp1',FOUND[0].id,'c0_x'];
          for(const withX of [false,true]){if(withX&&!X)newSession();
            for(const kk of ks){U.view=null;U.tab='today';U.sheet=k;U.sd={k:kk};try{render()}catch(e){}
              const sh=document.querySelector('#layer :is(.sheet,.pk-alert,.pk-actions):not(.pk-leaving)');if(U.sheet===k&&sh)return sh.dataset.screen}}
          return null}""", s['key'][6:])
        if got == s['id']:
            nsh += 1
            pg.wait_for_timeout(60)
            r = pg.evaluate(UNNAMED_JS, dict(opt, roots=["#layer :is(.sheet,.pk-alert,.pk-actions):not(.pk-leaving)"]))
            unnamed += [s['id'] + ' ' + x for x in r['unnamed']]; dups += [s['id'] + ' ' + x for x in r['dup']]; quiet |= {s['id'] + ' › ' + x for x in r['quiet']}
        pg.evaluate("(()=>{document.querySelectorAll('#layer .pk-alert,#layer .pk-actions').forEach(e=>e.remove());U.sheet=null;U.sd={};if(X){X=null;saveDraft()}render()})()")
        pg.wait_for_timeout(30)
    ok(not unnamed and nsh >= 30, f'on every screen and the {nsh} sheets the sample data opens, every visible control carries its name ({unnamed})')
    ok(not dups, f'one name is one action on a screen, rows and standard roles aside ({dups})')
    if quiet: print('  note  named buttons with no label or text for VoiceOver: ' + ', '.join(sorted(quiet)), flush=True)
    pg.context.close()


def reference(b, t):
    """Q55 the element sheet (reference/elements.md): built from the register and from the app, so it must match what
    the app gives now; every part the sample data reaches has a kit part or a reason; and the check itself catches a
    part with neither, a part missing from the sheet and a value that changed."""
    ok = t.ok
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'reference'))
    import elements as EL
    text, vals = EL.sheet(b)
    have = open(EL.OUT, encoding='utf-8').read()
    diff = [l for l in text.splitlines() if l not in set(have.splitlines())][:3]
    ok(text == have, f'reference/elements.md is up to date with the register and the app (python3 tools/reference/elements.py writes it; new or changed lines: {diff})')
    bad = EL.problems(vals)
    ok(not bad, f'every named part the sample data reaches has a kit part or a reason (REASONS in tools/reference/elements.py) ({bad})')
    reached = sum(1 for p in EL.register() if (p[0], p[1], p[2]) in vals)
    ok(reached >= 200, f'the sheet reads at least 200 parts from the app ({reached})')
    ok(all(v['corner'] and v['press'] and v['motion'] for v in vals.values()), 'every part read has a press, a corner and a motion, even if "none"')
    # the check itself, on copies
    reg = EL.register()
    fake = ('VS-001', 'test-only-button', '[data-a="testOnly"]', 'In use', '', reg[[p[0] for p in reg].index('VS-001')][5])
    v2 = dict(vals); v2[fake[:3]] = {'kit': '', 'press': 'none', 'corner': 'none', 'motion': 'none', 'reason': ''}
    ok(EL.problems(v2, reg + [fake]) == ['VS-001 › test-only-button'], 'a part with no kit part and no reason is caught')
    ok(EL.build(vals, reg + [fake]) != have, 'a part added to the register and missing from the sheet makes it out of date')
    k = next(k for k, v in vals.items() if v['corner'] == 'capsule')
    v3 = dict(vals); v3[k] = dict(vals[k], corner='`--r-card`')
    ok(EL.build(v3) != have, f'a value that changes in the app makes the sheet out of date ({k[0]} › {k[1]})')


def run(b, t):
    register(b, t)
    coverage(b, t)
    reference(b, t)
    on_page(b, t)
    overlays(b, t)
    missing_entry(b, t)
    label(b, t)
    changelog(b, t)
    saved_data(b, t)
