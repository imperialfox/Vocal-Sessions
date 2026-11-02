"""Visual App Atlas (Q30) · what the scanner needs to know about Vocal Sessions.

The scanner reads the list of screens from the code (inventory.py). This file only says:
  - where it starts (ROOTS): the tabs, reached through their real buttons, and the extra states
    (first launch, session running, Today in dark mode, a song with its track and takes);
  - everything else is found by tapping: a button that opens a screen or sheet the code can show becomes that
    screen's way in ("door"), so screens are opened the way you'd reach them, through their real buttons;
  - which area each screen belongs to, which doc sections explain it, and which buttons are never tapped.
"""
import datetime as dt
from zoneinfo import ZoneInfo

APP = {'name': 'Vocal Sessions', 'url': 'https://imperialfox.github.io/Vocal-Sessions/'}
VIEWPORT = {'w': 402, 'h': 874, 'name': 'iPhone 17 Pro'}
# the clock is frozen at this moment for every scan, so dates and "2 days ago" never show up as changes
FIXED_TIME = dt.datetime(2026, 11, 2, 10, 0, 0, tzinfo=ZoneInfo('Europe/London'))
DATA = 'sample data (tests) + one song with lyrics, sections, marks, takes and a generated track'

# Steps: ('tap', css) taps a real button; ('js', code) is a shortcut, used only for set-up the app has no button for.
TAB = lambda v: ('tap', '[data-a="tab"][data-v="' + v + '"]')
SONG_PAGE = [TAB('songs'), ('tap', '[data-a="sgOpen"][data-k="{song}"]')]  # {song}: the sample song's id

# id, title, area, kind, inventory key, steps, set-up, docs ((file, section label), ...), state of
ROOTS = [
    dict(id='today', title='Today', area='Today', kind='Tab', key='Tab:today', steps=[], setup=[]),
    dict(id='today-empty', title='Today · first launch', area='Today', kind='State', key='Tab:today', steps=[], setup=['empty'], state_of='today'),
    dict(id='today-session', title='Today · session running', area='Today', kind='State', key='Tab:today', steps=[], setup=['session'], state_of='today',
         docs=[('MAINTAINING.md', 'The floating window')]),
    dict(id='today-dark', title='Today · dark mode', area='Today', kind='State', key='Tab:today', steps=[], setup=['dark'], state_of='today',
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
         steps=SONG_PAGE + [('tap', '[data-a="sgSec"]')], setup=['track', 'takes'], state_of='song-page', taps=True),
]

TAB_AREA = {'today': 'Today', 'history': 'Progress', 'songs': 'Songs', 'exercises': 'Exercises', 'find': 'Search', 'settings': 'Settings'}
VIEW_AREA = {'lyr': 'Songs', 'trk': 'Songs', 'ckCheck': 'Songs', 'song': 'Songs', 'found': 'Session', 'rot': 'Session', 'app': 'Session',
             'saved': 'Session', 'all': 'Progress', 'ex': 'Exercises', 'coach': 'Exercises', 'set': 'Settings', 'guide': 'Settings', 'log': 'Settings'}
AREAS = ['Today', 'Progress', 'Session', 'Songs', 'Exercises', 'Search', 'Settings']

# Names for what the scan finds (otherwise it uses the screen's own heading)
TITLES = {'Screen:lyr': 'Song page', 'Screen:trk': 'Track player', 'Screen:found': 'Session', 'Screen:all': 'All sessions',
          'Screen:log': 'Changelog', 'Screen:coach': 'Coach video', 'Screen:ckCheck': 'Check timing', 'Screen:saved': 'Session saved',
          'Screen:song': 'Song practice', 'Screen:rot': 'Session · Rotation', 'Screen:app': 'Session · Application',
          'Sheet:sgKey': 'Key for this song', 'Sheet:sgTakes': 'Takes', 'Sheet:calendar': 'Calendar', 'Sheet:session': 'Session details',
          'Sheet:edit': 'Edit session', 'Screen:guide:home': 'Marks guide'}
# One page standing for others with the same layout: "Exercise page · Humming"
TITLE_PREFIX = {'Screen:ex': 'Exercise page', 'Screen:guide:mark': 'Marks guide · a mark', 'Sheet:exNote': 'Exercise notes'}

# Doc sections, most specific first (file, section label as inventory.doc_sections() names it)
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

# Words to find a screen's latest changelog headline (otherwise its title)
WORDS = {'Screen:lyr': ['lyrics page', 'song page'], 'Screen:trk': ['track player'], 'Screen:found': ['one-page session', 'session'],
         'Screen:saved': ['session saved', 'saved screen'], 'Screen:coach': ['coach video', 'coach'], 'Screen:guide': ['marks guide', 'practice guide'],
         'Screen:ckCheck': ['song clock', 'timing'], 'Screen:log': ['changelog'], 'Tab:find': ['search'], 'Tab:history': ['progress'],
         'Sheet:sgKey': ['marks', 'key'], 'Sheet:sgTakes': ['takes'], 'Sheet:away': ['clock'], 'Sub-page:appear': ['status bar', 'appearance', 'gradient']}

# The same layout with other content: one is captured, the rest point to it as "same page layout"
def family(sig):
    tab, view, sheet, *rest = sig.split('|')
    if sheet: return 'Sheet:' + sheet
    if view == 'ex': return 'Screen:ex'
    if view == 'guide': return 'Screen:guide:' + ('home' if rest and rest[0] == 'home' else 'how' if rest and rest[0] == 'how' else 'mark')
    if view == 'set': return 'Sub-page:' + (rest[0] if rest else '')
    if view: return 'Screen:' + view
    return 'Tab:' + tab

# Buttons never tapped, with the reason shown. A button that only opens a sheet to confirm (data-a="sheet") is tapped:
# opening a confirmation is safe, and its own confirm button is on this list.
SKIP = [
    (r'^(rec|sgRec|apSing|recOver)$', 'Not tested: needs the microphone'),
    (r'^(trkAdd|trkReplace|coachAdd|importPick|checkPick|sgAddPick|ckAddTrack)$', 'Not tested: needs a file from the Files app'),
    (r'[eE]xport|^shareTake$|^saveReadme$', 'Not tested: saves or shares a file'),
    (r'^(importYes|undoYes|rescueSave)$', 'Not tested: replaces or rewrites your data'),
    (r'Del|^del|[rR]emove|[cC]lear|[rR]eset|[dD]iscard|[wW]ipe|^rm|Rm$|Rm[A-Z]', 'Not tested: deletes or clears something'),
]
SAFE_ACTIONS = {'sheet'}  # only opens a sheet

# How the scanner talks to the app (run in the page)
STATE = "(()=>({tab:U.tab,view:U.view||null,sheet:U.sheet||null,setPg:U.setPg||null,gPg:U.gPg||null,exId:U.exId||null}))()"
SNAPSHOT = """()=>{window.__D=structuredClone(D);window.__X=X?structuredClone(X):null;
 window.__LS=Object.fromEntries(Object.keys(localStorage).map(k=>[k,localStorage.getItem(k)]));
 try{window.__SG=JSON.stringify(SG)}catch(e){window.__SG=null}}"""
# back to exactly how it was after set-up: nothing recording or playing, fresh screen state, saved data, settings and session
# as they were, and the Songs screen's own menus and selections closed (SG). The scanner also checks the screen's buttons
# match the first capture, and starts a fresh copy of the app if anything still differs.
RESET = """()=>{try{if(typeof rec!=='undefined'&&rec)stopRec()}catch(e){};try{NOW.stop()}catch(e){};try{stopPlayback()}catch(e){};
 try{localStorage.clear();for(const [k,v] of Object.entries(window.__LS||{}))localStorage.setItem(k,v)}catch(e){};
 try{if(window.__SG)Object.assign(SG,JSON.parse(window.__SG));SGP=null}catch(e){};
 U=freshU();D=structuredClone(window.__D);X=window.__X?structuredClone(window.__X):null;
 document.querySelectorAll('.toast').forEach(t=>t.remove());closeSwipes();window.scrollTo(0,0);render()}"""
SETUP_JS = {
    'session': "()=>{newSession();render()}",
    # a session part-way through (as the tests set one up): Foundation logged, and for 'rot-done' Rotation too
    'found-done': "()=>{newSession();FOUND.forEach(e=>X.f[e.id]=2);X.start=Date.now()-20*60000;X.fEnd=Date.now();X.fE=elapsedSec()*0.6;saveDraft();render()}",
    'rot-done': "()=>{newSession();FOUND.forEach(e=>X.f[e.id]=2);X.start=Date.now()-30*60000;X.fEnd=Date.now();X.fE=elapsedSec()*0.4;X.rot={rung:2};X.rEnd=Date.now();X.rE=elapsedSec()*0.7;saveDraft();render()}",
}
TITLE_JS = """()=>{const sh=document.querySelector('.scrim .sheet');if(sh){const h=sh.querySelector('h1,h2,.stitle,.shtitle');
  return (sh.getAttribute('aria-label')||(h&&h.innerText)||'').replace(/\\s+/g,' ').trim()}
  const h=document.querySelector('#app h1,#app .ntitle,#app h2');return h?h.innerText.replace(/\\s+/g,' ').trim():''}"""


def sig(s):
    """What identifies a screen: tab + view + sheet (+ the sub-page or exercise)."""
    v = s.get('view')
    k = [s.get('tab') if not v else '', v or '', s.get('sheet') or '']
    if v == 'set': k.append(s.get('setPg') or '')
    if v == 'guide': k.append(s.get('gPg') or '')
    if v == 'ex': k.append(s.get('exId') or '')
    return '|'.join(k)


def keys_of(sg):
    """The inventory entries a captured screen accounts for."""
    tab, view, sheet, *rest = sg.split('|')
    out = []
    if tab: out.append('Tab:' + tab)
    if view: out.append('Screen:' + view)
    if sheet: out.append('Sheet:' + sheet)
    if view == 'set' and rest and rest[0]: out.append('Sub-page:' + rest[0])
    return out


def area_of(sg, under=None):
    tab, view, sheet, *rest = sg.split('|')
    if view: return VIEW_AREA.get(view, under or 'Other')
    return TAB_AREA.get(tab, under or 'Other')


def describe(sg):
    tab, view, sheet, *rest = sg.split('|')
    return ' · '.join(x for x in [tab and f'{tab} tab', view and f'screen “{view}”', sheet and f'sheet “{sheet}”', *[r for r in rest if r]] if x)
