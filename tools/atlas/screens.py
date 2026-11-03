"""Visual App Atlas · Vocal Sessions' settings for the Atlas kit (Q31; the Atlas began as Q30).

The scanning, the viewer, notes and "check my notes" are the Atlas kit's (a pinned, unmodified copy in kit/; README
there explains every name below). This file is everything the kit needs to know about Vocal Sessions:
  - how to open it with sample data (load, prepare): the tests' sample data plus one song with lyrics, sections,
    marks, three takes and a generated track, with the clock frozen and motion off. Never real data;
  - where the scan starts (ROOTS): the tabs, reached through their real buttons, and the extra states (first launch,
    session running, Today in dark mode, a song with its track and takes). Everything else is found by tapping: a
    button that opens a screen or sheet becomes that screen's way in ("door");
  - how to tell which screen is showing and put the app back after a tap (WHERE, key, SNAPSHOT, RESET);
  - the screens the code can show (inventory), read from the code with no browser, so anything the scan missed is
    listed as "Not captured yet";
  - which area each screen belongs to, which doc sections explain it, and which buttons are never tapped;
  - the screen register from Q36 (IDS), so screens, notes and the map layout are keyed by VS-… IDs.
"""
import datetime as dt
import os
import re
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, 'kit'))
from atlas_kit import code as CODE  # noqa: E402  (the kit's helpers for reading JavaScript)

APP = {'name': 'Vocal Sessions', 'url': 'https://imperialfox.github.io/Vocal-Sessions/'}
KIND = 'screens'
APP_DIR = '../..'   # the repo, from this folder
VIEWPORT = {'w': 402, 'h': 874, 'name': 'iPhone 17 Pro'}
# the clock is frozen at this moment for every scan, so dates and "2 days ago" never show up as changes
FIXED_TIME = dt.datetime(2026, 11, 2, 10, 0, 0, tzinfo=ZoneInfo('Europe/London'))
TIMEZONE, LOCALE, SCALE = 'Europe/London', 'en-GB', 2
DATA = 'sample data (tests) + one song with lyrics, sections, marks, takes and a generated track'
INIT_SCRIPT = "try{localStorage.setItem('vocalMotion','0')}catch(e){}"   # motion off, as in the tests
AREAS = ['Today', 'Progress', 'Session', 'Songs', 'Exercises', 'Search', 'Settings']
GH = 'https://github.com/imperialfox/Vocal-Sessions/blob/main/'
DOC_FILES, DOCS_URL, CHANGELOG = ['README.md', 'MAINTAINING.md'], GH, 'CHANGELOG.md'
QUEUE = {'file': 'RENDER_QUEUE.md', 'section': 'Not scheduled'}


def _tests(app_dir, only_harness=False):
    """The scanned app's own test helpers (sample data, the song, the generated track)."""
    t = os.path.join(app_dir, 'tests')
    if t not in sys.path: sys.path.insert(0, t)
    import harness
    if only_harness: return harness
    import test_layout, test_track  # noqa: E401
    return harness, test_layout, test_track


USER_AGENT = _tests(REPO, only_harness=True).UA_IPHONE


# ---------- opening the app with sample data ----------
def prepare(ctx):
    """Once per scan: the tests' sample data plus one song (lyrics, sections, marks), made at the frozen time, and a
    generated track file. {song} in the steps below is that song's id."""
    harness, test_layout, test_track = _tests(ctx['app'])
    from playwright.sync_api import sync_playwright
    harness.now = FIXED_TIME  # the sample's dates are counted back from the frozen time
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx2 = b.new_context(viewport={'width': VIEWPORT['w'], 'height': VIEWPORT['h']}, timezone_id=TIMEZONE, locale=LOCALE, user_agent=USER_AGENT)
        ctx2.clock.install(time=FIXED_TIME.timestamp())
        ctx2.add_init_script(INIT_SCRIPT)
        pg = ctx2.new_page()
        _open(pg, harness, ctx['app'], harness.sample())
        pg.evaluate(test_layout.SONG)
        import json
        seed = json.loads(pg.evaluate("localStorage.getItem('vocalTracker')")); song = pg.evaluate('U.songId')
        b.close()
    return {'seed': seed, 'song': song, 'track': test_track.track(), 'vars': {'song': song}}


def _open(pg, harness, app_dir, data):
    pg.goto(harness.url(os.path.join(app_dir, 'index.html')))   # served from localhost, as the tests and Pages serve it
    pg.evaluate(harness.SEED, data)
    pg.reload()
    harness.ready(pg)


def load(pg, setup, ctx):
    """A fresh app page with the sample data (none for 'empty'), then the set-up a starting screen asks for."""
    harness, test_layout, _ = _tests(ctx['app'])
    pg.emulate_media(reduced_motion='no-preference')   # the system's Reduce Motion off, as in the tests (motion itself is off)
    _open(pg, harness, ctx['app'], None if 'empty' in setup else ctx['seed'])
    if 'track' in setup or 'takes' in setup:
        pg.evaluate("id=>go(()=>{U.sheet=null;U.tab='songs';U.view='lyr';U.songId=id})", ctx['song'])
    if 'track' in setup:  # through the song page's real Add track button, with the file picker
        with pg.expect_file_chooser(timeout=5000) as fc: pg.click('#app [data-a=trkAdd]')
        fc.value.set_files(ctx['track'])
        pg.wait_for_function('id=>TRACK.has(id)&&!TRACK.busy()', arg=ctx['song'], timeout=20000)
    if 'takes' in setup:
        pg.evaluate(test_layout.TAKES)
        pg.wait_for_function('()=>TAKES.length>=3', timeout=5000)
    for k in setup:
        if k in SETUP_JS: pg.evaluate(SETUP_JS[k])


SETUP_JS = {
    'session': "()=>{newSession();render()}",
    # a session part-way through (as the tests set one up): Foundation logged, and for 'rot-done' Rotation too
    'found-done': "()=>{newSession();FOUND.forEach(e=>X.f[e.id]=2);X.start=Date.now()-20*60000;X.fEnd=Date.now();X.fE=elapsedSec()*0.6;saveDraft();render()}",
    'rot-done': "()=>{newSession();FOUND.forEach(e=>X.f[e.id]=2);X.start=Date.now()-30*60000;X.fEnd=Date.now();X.fE=elapsedSec()*0.4;X.rot={rung:2};X.rEnd=Date.now();X.rE=elapsedSec()*0.7;saveDraft();render()}",
}


def version(app_dir):
    m = re.search(r"APP_VERSION\s*=\s*'([^']+)'", open(os.path.join(app_dir, 'index.html'), encoding='utf-8').read())
    return m.group(1) if m else None


# ---------- where the scan starts ----------
# Steps: ('tap', css) taps a real button; ('js', code) is a shortcut, used only for set-up the app has no button for.
TAB = lambda v: ('tap', '[data-a="tab"][data-v="' + v + '"]')
SONG_PAGE = [TAB('songs'), ('tap', '[data-a="sgOpen"][data-k="{song}"]')]  # {song}: the sample song's id

# id, title, area, kind, the code-list key, steps, set-up, docs ((file, section label), ...), and for a state: state_of, state
ROOTS = [
    dict(id='today', title='Today', area='Today', kind='Tab', key='Tab:today', steps=[], setup=[]),
    dict(id='today-empty', title='Today · first launch', area='Today', kind='State', key='Tab:today', steps=[], setup=['empty'], state_of='today', state='first launch'),
    dict(id='today-session', title='Today · session running', area='Today', kind='State', key='Tab:today', steps=[], setup=['session'], state_of='today', state='session running',
         docs=[('MAINTAINING.md', 'The floating window')]),
    dict(id='today-dark', title='Today · dark mode', area='Today', kind='State', key='Tab:today', steps=[], setup=['dark'], state_of='today', state='dark mode',
         docs=[('MAINTAINING.md', 'Design foundations (3.26, Q10)')]),
    dict(id='progress', title='Progress', area='Progress', kind='Tab', key='Tab:history', steps=[TAB('history')], setup=[]),
    dict(id='songs', title='Songs', area='Songs', kind='Tab', key='Tab:songs', steps=[TAB('songs')], setup=[]),
    dict(id='exercises', title='Exercises', area='Exercises', kind='Tab', key='Tab:exercises', steps=[TAB('exercises')], setup=[]),
    dict(id='search', title='Search', area='Search', kind='Tab', key='Tab:find', steps=[('tap', '[data-a="findOpen"]')], setup=[]),
    dict(id='settings', title='Settings', area='Settings', kind='Tab', key='Tab:settings', steps=[('tap', '[data-a="openSettings"]')], setup=[]),
    # the session's later steps, through Today's real Resume button with a session part-way through
    dict(id='session-rotation', title='Session · Rotation', area='Session', kind='Screen', key='Screen:rot', steps=[('tap', '[data-a="resume"]')], setup=['found-done']),
    dict(id='session-application', title='Session · Application', area='Session', kind='Screen', key='Screen:app', steps=[('tap', '[data-a="resume"]')], setup=['rot-done']),
    # a song with everything on it: its track (added through the real Add track button) and three takes
    dict(id='song-page', title='Song page', area='Songs', kind='Screen', key='Screen:lyr', steps=SONG_PAGE, setup=['track', 'takes']),
    dict(id='song-section', title='Song page · section selected', area='Songs', kind='State', key='Screen:lyr',
         steps=SONG_PAGE + [('tap', '[data-a="sgSec"]')], setup=['track', 'takes'], state_of='song-page', state='section selected', taps=True),
]

TAB_AREA = {'today': 'Today', 'history': 'Progress', 'songs': 'Songs', 'exercises': 'Exercises', 'find': 'Search', 'settings': 'Settings'}
VIEW_AREA = {'lyr': 'Songs', 'trk': 'Songs', 'ckCheck': 'Songs', 'song': 'Songs', 'found': 'Session', 'rot': 'Session', 'app': 'Session',
             'saved': 'Session', 'all': 'Progress', 'ex': 'Exercises', 'coach': 'Exercises', 'set': 'Settings', 'guide': 'Settings', 'log': 'Settings'}

# Names for what the scan finds when the register has none (otherwise the screen's own heading)
TITLES = {'Screen:lyr': 'Song page', 'Screen:trk': 'Track player', 'Screen:found': 'Session', 'Screen:all': 'All sessions',
          'Screen:log': 'Changelog', 'Screen:coach': 'Coach video', 'Screen:ckCheck': 'Check timing', 'Screen:saved': 'Session saved',
          'Screen:song': 'Song practice', 'Screen:rot': 'Session · Rotation', 'Screen:app': 'Session · Application',
          'Sheet:sgKey': 'Key for this song', 'Sheet:sgTakes': 'Takes', 'Sheet:calendar': 'Calendar', 'Sheet:session': 'Session details',
          'Sheet:edit': 'Edit session', 'Screen:guide:home': 'Marks guide'}
# One page standing for others with the same layout: "Exercise page · Humming"
TITLE_PREFIX = {'Screen:ex': 'Exercise page', 'Screen:guide:mark': 'Marks guide · a mark', 'Sheet:exNote': 'Exercise notes'}

# Doc sections, most specific first (file, section label as the kit's docs.doc_sections() names it)
R, M = 'README.md', 'MAINTAINING.md'
AREA_DOCS = {'Today': [(R, 'Tabs › Today')], 'Progress': [(R, 'Tabs › Progress')], 'Songs': [(R, 'Tabs › Songs'), (M, 'Songs')],
             'Exercises': [(R, 'Tabs › Exercises')], 'Search': [(R, 'Tabs › Search'), (M, 'Search')],
             'Settings': [(R, 'Tabs › Settings'), (M, 'Settings')], 'Session': [(M, 'The one-page session (3.39, Q19)'), (R, 'Session details')]}
KEY_DOCS = {
    'Screen:lyr': [(M, 'The lyrics page')], 'Screen:trk': [(M, 'The track player')], 'Screen:ckCheck': [(M, 'Song Clock')],
    'Screen:coach': [(M, 'The coach video'), (R, 'Coach video')], 'Screen:guide': [(M, 'Marks guide')],
    'Screen:log': [(M, 'The Changelog page')], 'Screen:saved': [(M, 'Session saved (3.41, Q21)')],
    'Screen:found': [(M, 'The one-page session (3.39, Q19)'), (M, 'Application (3.40, Q20)')], 'Screen:song': [(M, 'Recordings')],
    'Screen:ex': [(R, 'Tabs › Exercises')], 'Screen:all': [(R, 'Tabs › Progress')],
    'Sheet:sgKey': [(M, 'Marks'), (M, 'Marks guide')], 'Sheet:sgTakes': [(M, 'Recordings')], 'Sheet:sgTakeMenu': [(M, 'Recordings')],
    'Sheet:ckGrid': [(M, 'Song Clock')], 'Sheet:away': [(M, 'The session clock (3.42, Q22)')], 'Sheet:recOver': [(M, 'Recordings')],
    'Sheet:storage': [(M, 'Where data lives')], 'Sheet:persist': [(M, 'Where data lives')],
    'Sheet:bkGuide': [(R, 'Backups'), (M, 'Backups')], 'Sheet:bkReport': [(M, 'Backups')], 'Sheet:bkLog': [(M, 'Backups')],
    'Sub-page:backup': [(R, 'Backups'), (M, 'Backups')], 'Sub-page:storage': [(M, 'Where data lives'), (M, 'Save safety (3.29, Q11)')],
    'Sub-page:recall': [(M, 'Recall')], 'Sub-page:coach': [(M, 'The coach video'), (R, 'Coach video')],
    'Sub-page:appear': [(M, 'Native bars (3.23, Q08)'), (M, 'Motion')], 'Sub-page:access': [(M, 'Motion')],
}
PREFIX_DOCS = [('Sheet:trk', [(M, 'The track player')]), ('Sheet:ck', [(M, 'Song Clock')]), ('Sheet:sg', [(M, 'Songs')])]


def code_key(fam):
    """A screen's entry in the code's list: other exercises and guide pages share their screen's ('Screen:guide')."""
    return 'Screen:' + fam.split(':')[1] if fam.startswith('Screen:') else fam


def docs(fam, area):
    """(file, section label) pairs that explain a screen, most specific first. A starting screen's own docs come first."""
    key = code_key(fam)
    want = list(KEY_DOCS.get(key, []))
    for pre, d in PREFIX_DOCS:
        if key.startswith(pre): want += d
    return want + AREA_DOCS.get(area, [])


# Words to find a screen's latest changelog headline (otherwise its title)
WORDS = {'Screen:lyr': ['lyrics page', 'song page'], 'Screen:trk': ['track player'], 'Screen:found': ['one-page session', 'session'],
         'Screen:saved': ['session saved', 'saved screen'], 'Screen:coach': ['coach video', 'coach'], 'Screen:guide': ['marks guide', 'practice guide'],
         'Screen:ckCheck': ['song clock', 'timing'], 'Screen:log': ['changelog'], 'Tab:find': ['search'], 'Tab:history': ['progress'],
         'Sheet:sgKey': ['marks', 'key'], 'Sheet:sgTakes': ['takes'], 'Sheet:away': ['clock'], 'Sub-page:appear': ['status bar', 'appearance', 'gradient']}
for _p in ('home', 'how', 'mark'): WORDS['Screen:guide:' + _p] = WORDS['Screen:guide']


# ---------- telling screens apart ----------
# Keys look like 'today||' (tab, screen, sheet), '|set||backup' (a Settings page) or '|ex||humming' (an exercise).
# The code's list (inventory) and starting screens use 'Kind:name' keys ('Tab:today', 'Sheet:calendar').
WHERE = "(()=>({tab:U.tab,view:U.view||null,sheet:U.sheet||null,setPg:U.setPg||null,gPg:U.gPg||null,exId:U.exId||null}))()"
# Sheets and pages are still moving into place a quarter of a second after a tap (the glass sheet's rise and corners,
# the Changelog's rows, a page's title), so a picture taken then lands a point higher or lower from one scan to the next
# and every rescan would call them "looks different". Before reading the screen (and so before each picture): wait
# until the page's animations have finished (at most 1.5 s), hold any looping one (a pulse) on its first frame, then
# wait until the open sheet, the screen and its title keep their place, size and corners, and the page its height,
# for three frames (at most 1 s), since some of the movement is drawn by script, which the animation list doesn't show.
SETTLED = "()=>!document.getAnimations().some(a=>a.playState==='running'&&a.effect&&a.effect.getTiming().iterations!==Infinity)"
STEADY = """async()=>{document.getAnimations().forEach(a=>{try{if(a.effect&&a.effect.getTiming().iterations===Infinity){a.pause();a.currentTime=0}}catch(e){}});
 const box=e=>{if(!e)return '';const r=e.getBoundingClientRect(),c=getComputedStyle(e);return [r.top,r.left,r.width,r.height,c.borderTopLeftRadius,c.transform,c.opacity].join(',')};
 const sig=()=>[box(document.querySelector('.scrim .sheet')),box(document.getElementById('app')),box(document.querySelector('#app h1,#app .ntitle,#app h2')),
  document.documentElement.scrollHeight,scrollY].join('|');
 let last=sig(),same=0;const t0=performance.now();
 while(same<3&&performance.now()-t0<1000){await new Promise(r=>requestAnimationFrame(r));const n=sig();same=n===last?same+1:0;last=n}}"""


def where(pg):
    """Which screen is showing, once it has settled (WHERE, read by key below)."""
    try: pg.wait_for_function(SETTLED, timeout=1500)
    except Exception: pass   # still moving after 1.5 s: read it anyway
    pg.evaluate(STEADY)
    return pg.evaluate(WHERE)


def key(s):
    """What identifies a screen: tab + view + sheet (+ the sub-page or exercise)."""
    v = s.get('view')
    k = [s.get('tab') if not v else '', v or '', s.get('sheet') or '']
    if v == 'set': k.append(s.get('setPg') or '')
    if v == 'guide': k.append(s.get('gPg') or '')
    if v == 'ex': k.append(s.get('exId') or '')
    return '|'.join(k)


def _parts(sg):
    return (sg.split('|') + ['', '', ''])[:3] + sg.split('|')[3:]


# The same layout with other content: one is captured, the rest point to it as "same page layout"
def family(sg):
    if '|' not in sg: return sg   # already a code-list key ('Tab:today')
    tab, view, sheet, *rest = _parts(sg)
    if sheet: return 'Sheet:' + sheet
    if view == 'ex': return 'Screen:ex'
    if view == 'guide': return 'Screen:guide:' + ('home' if rest and rest[0] == 'home' else 'how' if rest and rest[0] == 'how' else 'mark')
    if view == 'set': return 'Sub-page:' + (rest[0] if rest else '')
    if view: return 'Screen:' + view
    return 'Tab:' + tab


def keys_of(sg):
    """The code-list entries a captured screen accounts for."""
    if '|' not in sg: return [code_key(sg)]
    tab, view, sheet, *rest = _parts(sg)
    out = []
    if tab: out.append('Tab:' + tab)
    if view: out.append('Screen:' + view)
    if sheet: out.append('Sheet:' + sheet)
    if view == 'set' and rest and rest[0]: out.append('Sub-page:' + rest[0])
    return out


def area_of(sg, under=None):
    if '|' not in sg: return None
    tab, view, sheet, *rest = _parts(sg)
    if view: return VIEW_AREA.get(view, 'Other')
    return TAB_AREA.get(tab, 'Other')


def kind_of(fam, sheet_open):
    return 'Sheet' if fam.startswith('Sheet:') else 'Sub-page' if fam.startswith('Sub-page:') else 'Screen'


def describe(sg):
    if '|' not in sg: return sg
    tab, view, sheet, *rest = _parts(sg)
    return ' · '.join(x for x in [tab and f'{tab} tab', view and f'screen “{view}”', sheet and f'sheet “{sheet}”', *[r for r in rest if r]] if x)


def link_kind(l):
    """Tab bar, Back, Opens a sheet or Button, for the map's lines."""
    a = l['action']
    if a in ('tab', 'findOpen'): return 'Tab bar'
    if a.lower().endswith('back') or a in ('close', 'setPgBack'): return 'Back'
    to = l.get('toSig')
    if to and _parts(to)[2] and l.get('opensSheet'): return 'Opens a sheet'
    return 'Button'


# ---------- what the scan sees and taps ----------
SHEET = '.scrim .sheet'   # a sheet's own buttons are looked for inside it, so a row underneath can't be tapped instead
BUTTONS = '[data-a]'
TITLE_JS = """()=>{const sh=document.querySelector('.scrim .sheet');if(sh){const h=sh.querySelector('h1,h2,.stitle,.shtitle');
  return (sh.getAttribute('aria-label')||(h&&h.innerText)||'').replace(/\\s+/g,' ').trim()}
  const h=document.querySelector('#app h1,#app .ntitle,#app h2');return h?h.innerText.replace(/\\s+/g,' ').trim():''}"""
# buttons behind a swipe (a row's Delete) or hidden from view: "Not tested: only shows after a swipe, a hold or a menu"
HIDDEN_JS = "e=>!!(e.closest('.sw')&&!e.closest('.fg'))||!!e.closest('[aria-hidden=true]')"

# Buttons never tapped, with the reason shown, by their action (data-a). A button that only opens a sheet to confirm
# (data-a="sheet") is tapped: opening a confirmation is safe, and its own confirm button is on this list.
# The kit checks a button's action, value and label. ACTION keeps each pattern to one-word names starting in lower case
# (actions like "sgDelRow"), so labels ("4 Delivery", "Clear tone") are never read as deleting or clearing; "del…" and
# "rm…" at the start need a capital after them (delSession), so a value like "delivery" isn't either.
ACTION = r'^(?=[a-z]\w*$)'
SKIP = [
    (ACTION + r'(?:rec|sgRec|apSing|recOver)$', 'Not tested: needs the microphone'),
    (ACTION + r'(?:trkAdd|trkReplace|coachAdd|importPick|checkPick|sgAddPick|ckAddTrack)$', 'Not tested: needs a file from the Files app'),
    (ACTION + r'(?:.*[eE]xport|shareTake$|saveReadme$)', 'Not tested: saves or shares a file'),
    (ACTION + r'(?:importYes|undoYes|rescueSave)$', 'Not tested: replaces or rewrites your data'),
    (ACTION + r'(?:.*(?:Del|[rR]emove|[cC]lear|[rR]eset|[dD]iscard|[wW]ipe|Rm$|Rm[A-Z])|del[A-Z]|rm[A-Z])', 'Not tested: deletes or clears something'),
]
SAFE_ACTIONS = {'sheet'}  # only opens a sheet

SNAPSHOT = """()=>{window.__D=structuredClone(D);window.__X=X?structuredClone(X):null;
 window.__LS=Object.fromEntries(Object.keys(localStorage).map(k=>[k,localStorage.getItem(k)]));
 try{window.__SG=JSON.stringify(SG)}catch(e){window.__SG=null}}"""
# back to exactly how it was after set-up: nothing recording or playing, fresh screen state, saved data, settings and session
# as they were, and the Songs screen's own menus and selections closed (SG). The kit also checks the screen's buttons
# match the first capture, and starts a fresh copy of the app if anything still differs.
RESET = """()=>{try{if(typeof rec!=='undefined'&&rec)stopRec()}catch(e){};try{NOW.stop()}catch(e){};try{stopPlayback()}catch(e){};
 try{localStorage.clear();for(const [k,v] of Object.entries(window.__LS||{}))localStorage.setItem(k,v)}catch(e){};
 try{if(window.__SG)Object.assign(SG,JSON.parse(window.__SG));SGP=null}catch(e){};
 U=freshU();D=structuredClone(window.__D);X=window.__X?structuredClone(window.__X):null;
 document.querySelectorAll('.toast').forEach(t=>t.remove());closeSwipes();window.scrollTo(0,0);render()}"""

# ---------- screen IDs (Q36): js/register.js ----------
# Read from the running page; each screen's ID is on the screen itself (data-screen on #app, and on the sheet).
# The register keeps each part as {name, sel}; the kit wants the names.
IDS = {'register': "SCREENS.screens.map(s=>Object.assign({},s,{parts:(s.parts||[]).map(p=>p.name)}))",
       'screen_attr': 'data-screen', 'part_attr': 'data-name', 'prefix': 'VS-', 'digits': 3}


# ---------- the code's list of screens (no browser) ----------
def inventory(app_dir):
    """Every screen state the code can show, as {'Kind:name': {'kind', 'name', 'where'}}.

    Kinds: Tab (U.tab), Screen (U.view), Sheet (U.sheet), Sub-page (Settings pages, U.setPg).
    Sources, so nothing the drawing code can show is missed:
      - render(): each `v === 'x'` and the tab table `{today: scrToday, ...}`
      - renderSheet(): each `s === 'x'`, and the sheets of the functions it hands a family of sheets to
        (a `/^sg[A-Z]/` test hands every 'sg…' sheet named in that function, and so on)
      - Settings' TITLE table (its pages)
      - every `U.tab = 'x'`, `U.view = 'x'`, `U.sheet = 'x'`, `U.setPg = 'x'` and `data-a="sheet" data-v="x"` in the code
    """
    src = CODE.sources(os.path.join(app_dir, 'js'))
    allsrc = '\n'.join(src.values())
    found = {}

    def add(kind, name, where):
        k = kind + ':' + name
        if k not in found: found[k] = {'kind': kind, 'name': name, 'where': where}

    r = CODE.function_body(src.get('ui.js', allsrc), 'render')
    for v in re.findall(r"\bv\s*===\s*'([A-Za-z]\w*)'", r): add('Screen', v, 'render()')
    tabs = re.search(r"\{\s*((?:\s*\w+\s*:\s*[\w.]+\s*,?)+)\s*\}\s*\[\s*U\.tab\s*\]", r)
    if tabs:
        for t in re.findall(r'(\w+)\s*:', tabs.group(1)): add('Tab', t, 'render()')
    # a view drawn by a fall-through (scrFlow) is named in config's FLOW table
    flow = re.search(r'const FLOW\s*=\s*\{([^}]*)\}', allsrc)
    if flow and 'scrFlow' in r:
        for v in re.findall(r'(\w+)\s*:', flow.group(1)): add('Screen', v, 'render() › scrFlow (FLOW)')

    rs = CODE.function_body(src.get('ui.js', allsrc), 'renderSheet')
    for s in re.findall(r"\bs\s*===\s*'([A-Za-z]\w*)'", rs): add('Sheet', s, 'renderSheet()')
    # families handed on: `s && /^sg[A-Z]/.test(s)) h = songSheet(s)`
    for pre, fn in re.findall(r"/\^(\w+)(?:\[[^\]]*\])?/\.test\(s\)\)\s*h\s*=\s*([\w.]+)\(", rs):
        name = fn.split('.')[-1]
        for f, code in src.items():  # every function by that name (TRACK.sheet is a `function sheet` in track.js)
            body = CODE.function_body(code, name)
            for s in re.findall(r"(?:\b\w\s*===?\s*|case\s+)'(" + pre + r"[A-Z]\w*)'", body):
                add('Sheet', s, 'renderSheet() › ' + fn + '()')

    title = re.search(r'const TITLE\s*=\s*\{(.*?)\};', src.get('settings.js', ''), re.S)
    if title:
        for k in re.findall(r"(\w+)\s*:\s*'", title.group(1)): add('Sub-page', k, 'Settings TITLE')

    for kind, rx in [('Tab', r"U\.tab\s*=\s*'([a-z]\w*)'"), ('Screen', r"U\.view\s*=\s*'([A-Za-z]\w*)'"),
                     ('Sheet', r"U\.sheet\s*=\s*'([A-Za-z]\w*)'"), ('Sub-page', r"U\.setPg\s*=\s*'([a-z]\w*)'"),
                     ('Sheet', r'data-a=\\?"sheet\\?"\s+data-v=\\?"([A-Za-z]\w*)\\?"')]:
        for f, code in src.items():
            for m in re.findall(rx, code): add(kind, m, f)
    return found
