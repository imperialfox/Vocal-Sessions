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
  - the screen register from Q36 (IDS), so screens, notes and the map layout are keyed by VS-… IDs;
  - Q35: starting states for the screens no tap reaches from the tabs (the coach video, recording and takes, How did it
    go?, the peek card, Check timing's Overlaps, Past the new end, rescued data), a caption for every screen (CAPTIONS),
    the first flows, F-01 and F-02 from the register (FLOWS), and the doors the scan can't test, written by hand (DOORS).
"""
import datetime as dt
import json
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
    harness, test_layout, test_track = _tests(ctx['app'])
    pg.emulate_media(reduced_motion='no-preference')   # the system's Reduce Motion off, as in the tests (motion itself is off)
    if 'mic' in setup: pg.add_init_script(FAKE_MIC)    # Q35: a made-up microphone (a steady tone), before the app loads
    _open(pg, harness, ctx['app'], None if 'empty' in setup else ctx['seed'])
    if 'damaged' in setup:  # Q35: saved data cut off part-way (as test_safety does), so the app rescues a copy as it opens
        pg.evaluate("s=>localStorage.setItem('vocalTracker',s)", json.dumps(ctx['seed'])[:-40])
        pg.reload(); harness.ready(pg)
        pg.wait_for_function('()=>SAFE.rescued().length===1', timeout=10000)
    if 'coach' in setup:  # Q35: the tests' made-up coach video, as Settings › Coach video's file picker would add it
        pg.set_input_files('#coachIn', harness.fix('coach-chapters.webm'))
        pg.wait_for_function('()=>COACH.has()&&!COACH.busy()', timeout=20000)
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
    if 'short-track' in setup:  # Q35: the next file picker gets a 20 s track, shorter than the song's timing
        short = test_track.F('Paper Boats 20.wav', 20)
        pg.on('filechooser', lambda fc: fc.set_files(short))
    if 'sheet' in setup:  # Q42: the tests' made-up print read onto the song through its real Add sheet music row, then saved
        pg.evaluate("id=>go(()=>{U.sheet=null;U.tab='songs';U.view='lyr';U.songId=id})", ctx['song'])
        with pg.expect_file_chooser(timeout=5000) as fc: pg.click('#app [data-a=melAdd]')
        fc.value.set_files(harness.fix('melody/paper-lanterns.pdf'))
        pg.wait_for_function("()=>['melRead','melTitle'].includes(U.sheet)", timeout=20000)
        if pg.evaluate("U.sheet") == 'melTitle': pg.click('#layer [data-a=melTitleHere]')
        pg.click('#layer [data-a=melSave]')
        pg.wait_for_function('id=>MELODY.has(id)', arg=ctx['song'], timeout=10000)
        pg.evaluate("()=>{U.sheet=null;U.sd={};go(()=>{U.tab='today';U.view=null})}")
    if 'pdf-next' in setup:  # Q42: the next file picker gets the tests' made-up print
        pg.on('filechooser', lambda fc: fc.set_files(harness.fix('melody/paper-lanterns.pdf')))


# Q35: a made-up microphone for the recording states: a steady 220 Hz tone at a low level, never a real voice
FAKE_MIC = """(()=>{if(!navigator.mediaDevices)return;
 navigator.mediaDevices.getUserMedia=async()=>{const ac=new AudioContext();try{await ac.resume()}catch(e){}
  const o=ac.createOscillator(),g=ac.createGain(),d=ac.createMediaStreamDestination();o.frequency.value=220;g.gain.value=0.2;
  o.connect(g).connect(d);o.start();return d.stream};})();"""

SETUP_JS = {
    'session': "()=>{newSession();render()}",
    # a session part-way through (as the tests set one up): Foundation logged, and for 'rot-done' Rotation too
    'found-done': "()=>{newSession();FOUND.forEach(e=>X.f[e.id]=2);X.start=Date.now()-20*60000;X.fEnd=Date.now();X.fE=elapsedSec()*0.6;saveDraft();render()}",
    'rot-done': "()=>{newSession();FOUND.forEach(e=>X.f[e.id]=2);X.start=Date.now()-30*60000;X.fEnd=Date.now();X.fE=elapsedSec()*0.4;X.rot={rung:2};X.rEnd=Date.now();X.rE=elapsedSec()*0.7;saveDraft();render()}",
    # Q35 (after 'takes', with the song's page set up): song practice of the sample song, 10 minutes in, with its newest take
    'song-draft': "()=>{newSong();X.song=U.songId;X.start=Date.now()-6e5;X.takes=['lt3'];saveDraft();render()}",
    # Q35: every line of the song placed by hand (section k's lines at 20k, 20k+5… s), as test_integrity does
    'timed': """()=>{const sg=songById(U.songId),M=ckModel(sg),T=M.L.map(l=>[l.k*20+l.li*5,l.k*20+l.li*5+4.5]);
      ckStore(sg,M.L,T,sg.order.map(()=>true),M.marks);rerender()}""",
    # Q35: the last section moved above the one before it (the end of a hold-and-drag), so lines overlap. A drag makes
    # the song page ignore taps for 0.4 s after it (so letting go doesn't also tap); that's cleared, as time would
    'moved': "()=>{SG.drag={el:true,from:2,to:1};sgEndDrag();sgSuppress=0}",
    # Q35: markers at 0:10 and 0:40 on the track (the 20 s replacement leaves 0:40 past its end)
    'late-marker': "()=>{const sg=songById(U.songId);sg.markers=[{id:'m0',t:10},{id:'m1',t:40}];save();rerender()}",
}


# Q35: steps that wait or hold on the way to a screen. They open nothing themselves: the screen still opens through its
# real buttons. UNTIL waits for the app to be ready (a recording to start, a take to be saved), and if it never is,
# the screen is "Failed" with that reason, never captured. HOLD presses a real button for about 0.7 s and lets go, as a
# finger does (a hold isn't a tap, so it can't be a 'tap' step).
def UNTIL(cond, what, ms=10000):
    return ('js', 'async()=>{/*until*/const t0=performance.now();while(!(' + cond + ')){if(performance.now()-t0>' + str(ms)
            + ')throw new Error(' + json.dumps('Didn’t open: ' + what, ensure_ascii=False) + ');await new Promise(r=>setTimeout(r,50))}}')


def HOLD(sel, ms=700):
    return ('js', 'async()=>{/*hold*/const b=document.querySelector(' + json.dumps(sel, ensure_ascii=False) + ');if(!b)throw new Error('
            + json.dumps('Didn’t open: couldn’t hold ' + sel + ' (not on screen)', ensure_ascii=False) + ');'
            'const r=b.getBoundingClientRect(),o={bubbles:true,cancelable:true,composed:true,pointerId:7,pointerType:"touch",isPrimary:true,'
            'clientX:r.left+r.width/2,clientY:r.top+r.height/2};b.dispatchEvent(new PointerEvent("pointerdown",o));'
            'await new Promise(r=>setTimeout(r,' + str(ms) + '));b.dispatchEvent(new PointerEvent("pointerup",o));'
            'await new Promise(r=>setTimeout(r,150))}')


def version(app_dir):
    m = re.search(r"APP_VERSION\s*=\s*'([^']+)'", open(os.path.join(app_dir, 'index.html'), encoding='utf-8').read())
    return m.group(1) if m else None


# ---------- where the scan starts ----------
# Steps: ('tap', css) taps a real button; ('js', code) is a shortcut, used only for set-up the app has no button for.
TAB = lambda v: ('tap', '[data-a="tab"][data-v="' + v + '"]')
SONG_PAGE = [TAB('songs'), ('tap', '[data-a="sgOpen"][data-k="{song}"]')]  # {song}: the sample song's id
# Q35: Application with the sample song picked, then Sing, waiting until it records; Stop, waiting for the nth take
APPL_REC = UNTIL("!!rec&&!!document.querySelector('#apcard.rec')", 'the recording didn’t start')
APPL_SING = [('tap', '[data-a="resume"]'), ('tap', '#app [data-a="apSong"][data-k="{song}"]'), ('tap', '#apcard [data-a="apSing"]'), APPL_REC]
APPL_STOP = lambda n: [('wait', 1200), ('tap', '#apcard [data-a="apStop"]'),
                       UNTIL("!rec&&TAKES.length===" + str(n) + "&&!document.querySelector('#apcard .tkwv.wait')", 'take ' + str(n) + ' wasn’t saved')]
CHECK_TIMING = SONG_PAGE + [('tap', '#app [data-a="ckGrid"]'), ('tap', '.scrim .sheet [data-a="ckTile"][data-v="check"]')]
BACKUP = [('tap', '[data-a="openSettings"]'), ('tap', '#app [data-a="setPg"][data-v="backup"]')]

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
] + [
    # ----- Q35 · Atlas: Starting States: screens no tap from the starting screens above can reach -----
    # VS-015 · Coach video: the player, with the tests' made-up video added (the real door is a file picker)
    dict(id='coach-video', title='Coach video', area='Exercises', kind='Screen', key='Screen:coach',
         steps=[TAB('exercises'), ('tap', '#app [data-a="openCoach"]'), UNTIL('COACH.has()&&!COACH.busy()', 'the coach video didn’t load')],
         setup=['coach'], docs=[('MAINTAINING.md', 'The coach video')]),
    # VS-004 · Application: recording, its take, and two takes to compare (a made-up microphone; no track, so no Sing over the track)
    dict(id='session-recording', title='Session · Application · recording', area='Session', kind='State', key='Screen:app',
         steps=APPL_SING + [('wait', 1000)], setup=['rot-done', 'mic'], state_of='session-application', state='recording'),
    dict(id='session-takes', title='Session · Application · takes', area='Session', kind='State', key='Screen:app',
         steps=APPL_SING + APPL_STOP(1), setup=['rot-done', 'mic'], state_of='session-application', state='takes'),
    dict(id='session-compare', title='Session · Application · compare', area='Session', kind='State', key='Screen:app',
         steps=APPL_SING + APPL_STOP(1) + [('tap', '#apcard [data-a="apSing"]'), APPL_REC] + APPL_STOP(2),
         setup=['rot-done', 'mic'], state_of='session-application', state='compare'),
    # VS-031 · How did it go?: song practice of the sample song with a take, then its real Save button. Its own buttons
    # (Save, Skip) then open VS-044 · Song practice saved
    dict(id='song-how', title='How did it go?', area='Songs', kind='Sheet', key='Sheet:how',
         steps=SONG_PAGE + [('tap', '#app [data-a="sgPractise"]'), ('tap', '#dock [data-a="cta"]')], setup=['takes', 'song-draft']),
    # VS-095 · Peek card: on the Marks side, tap a word, then hold the Peak mark button
    dict(id='peek-card', title='Peek card', area='Songs', kind='Overlay', key='Screen:lyr',
         steps=SONG_PAGE + [('tap', '[data-a="ckPencil"]'), ('tap', '[data-a="ckHeadMarks"]'), ('tap', '#app .w >> nth=1'),
                            HOLD('#mksheet .mkb[data-v="peak"]'), UNTIL("!!document.getElementById('mkpeek')", 'the peek card didn’t show')],
         setup=['track', 'takes'], docs=[('MAINTAINING.md', 'Marks guide')]),
    # VS-011 · Check timing, and its Overlaps state: every line placed by hand, then a timed section moved
    dict(id='check-timing', title='Check timing', area='Songs', kind='Screen', key='Screen:ckCheck', steps=CHECK_TIMING, setup=['track', 'takes']),
    dict(id='check-timing-overlaps', title='Check timing · Overlaps', area='Songs', kind='State', key='Screen:ckCheck',
         steps=CHECK_TIMING, setup=['track', 'takes', 'timed', 'moved'], state_of='check-timing', state='overlaps'),
    # VS-072 · Past the new end: the track replaced through the track menu with a 20 s file, with lines and a marker past it
    dict(id='track-past-end', title='Past the new end', area='Songs', kind='Sheet', key='Sheet:trkPast',
         steps=SONG_PAGE + [('tap', '#app [data-a="trkOpen"]'), ('tap', '[data-a="trkMenu"]'), ('tap', '.scrim .sheet [data-a="trkReplace"]'),
                            UNTIL("U.sheet==='trkPast'", 'the shorter track didn’t ask about what’s past its end', 20000)],
         setup=['track', 'timed', 'late-marker', 'short-track']),
    # VS-019 · Settings › Backup, and with a rescued copy of saved data that couldn't be read; and VS-080 · Delete the
    # rescued copy from there (its own Delete is never tapped). VS-080 has its own starting state because the copy's
    # button names the moment it was rescued, which differs in every fresh copy of the app
    dict(id='settings-backup', title='Settings › Backup', area='Settings', kind='Sub-page', key='Sub-page:backup', steps=BACKUP, setup=[]),
    dict(id='backup-rescued', title='Settings › Backup · rescued data', area='Settings', kind='State', key='Sub-page:backup',
         steps=BACKUP, setup=['damaged'], state_of='settings-backup', state='rescued data', taps=True,
         docs=[('MAINTAINING.md', 'Save safety (3.29, Q11)')]),
    dict(id='rescued-delete', title='Delete the rescued copy', area='Settings', kind='Sheet', key='Sheet:rescueDel',
         steps=BACKUP + [('tap', '#app [data-a="sheet"][data-v="rescueDel"]')], setup=['damaged']),
    # Q42: VS-100 · Sheet music read, after the Song page's Add sheet music row is given a made-up print; VS-099 · Sheet
    # music, from the row once it's saved; VS-105 · Remove the prints?, from Settings › Storage with a print kept
    dict(id='sheet-music-read', title='Sheet music read', area='Songs', kind='Sheet', key='Sheet:melRead',
         steps=SONG_PAGE + [('tap', '#app [data-a="melAdd"]'), UNTIL("['melRead','melTitle'].includes(U.sheet)", 'the print wasn’t read', 20000)],
         setup=['pdf-next']),
    dict(id='sheet-music', title='Sheet music', area='Songs', kind='Sheet', key='Sheet:melSheet',
         steps=SONG_PAGE + [('tap', '#app [data-a="melOpen"]')], setup=['sheet']),
    dict(id='sheet-prints-delete', title='Remove the prints?', area='Settings', kind='Sheet', key='Sheet:melPrintsDel',
         steps=[('tap', '[data-a="openSettings"]'), ('tap', '#app [data-a="setPg"][data-v="storage"]'), ('tap', '#app [data-v="melPrintsDel"]')], setup=['sheet']),
]

# ---------- captions (Q35): one plain line per screen, by screen ID (a state by its ID, then ~ and the state) ----------
CAPTIONS = {
    'VS-001': 'Home tab: weekly goal, streak, start a session', 'VS-001~first-launch': 'The very first open, before any practice',
    'VS-001~session-running': 'A session in progress: Resume or Discard', 'VS-001~dark-mode': 'Today in dark mode',
    'VS-002': 'Foundation: tap a row’s level (1, 2, 3, Skip)', 'VS-003': 'Rotation: the suggested exercise and the rest',
    'VS-004': 'Application: pick a song, sing it, keep the best take', 'VS-004~recording': 'The card records; the page stays still',
    'VS-004~takes': 'A take saved: play, star, Again or Done', 'VS-004~compare': 'Two takes: switch between them to compare',
    'VS-005': 'Session saved: the week’s arc; Done goes to Today', 'VS-006': 'Recent sessions and the practice-time chart',
    'VS-007': 'Every session and song practice, by month', 'VS-008': 'Pinned and recently practised songs, and search',
    'VS-009': 'One song: practise, recall, perform, record', 'VS-009~section-selected': 'A section picked: record it, its takes, marks',
    'VS-010': 'The song’s track: waveform, sections, markers, loop', 'VS-011': 'Sections and lines, and whether they’re timed',
    'VS-011~overlaps': 'A timed section moved: dashed lines, Overlaps flags', 'VS-012': 'Just singing: pick a song and record takes',
    'VS-013': 'The exercise library and the coach video', 'VS-014': 'One exercise: its pattern, levels and how to do it',
    'VS-015': 'The coach video player: levels, Loop, every exercise', 'VS-016': 'Every pattern the app can play, by group',
    'VS-017': 'Search songs, lyrics, exercises and sessions', 'VS-018': 'A list of rows, each opening its own page',
    'VS-019': 'Export, import and check a backup', 'VS-019~rescued-data': 'Saved data that couldn’t be read: save or delete the copy',
    'VS-020': 'Space used, and reviewing old takes', 'VS-021': 'How long a peek shows the words', 'VS-022': 'Add, replace or remove the coach video',
    'VS-023': 'Your voice type and range', 'VS-024': 'The pattern player’s sound, ending and vowel cue', 'VS-025': 'Background and how things look',
    'VS-026': 'Reduce motion, transparency and slow motion', 'VS-027': 'Every version on a timeline',
    'VS-028': 'Every mark, and how to mark a song', 'VS-029': 'Four passes to mark a song, and good habits', 'VS-030': 'One mark: what it means and when to use it',
    'VS-031': 'After song practice: words for how it felt, all optional', 'VS-032': 'A long session: check the minutes before saving',
    'VS-033': 'Notes on one exercise in this session', 'VS-034': 'Add your own word to the list', 'VS-035': 'Back after a long gap: count the time away?',
    'VS-036': 'The session is finished', 'VS-037': 'Throw away the session in progress?', 'VS-038': 'Practice calendar: a day opens its sessions',
    'VS-039': 'One session: levels, notes and time split', 'VS-040': 'Change a session’s date, minutes and levels', 'VS-041': 'Delete this session?',
    'VS-042': 'One song practice: time, song and takes', 'VS-043': 'Delete this song practice?', 'VS-044': 'Over Today: time, song and takes, saved',
    'VS-045': 'Pick a song for song practice', 'VS-046': 'Delete this song and its takes?', 'VS-047': 'Recording with the track playing: headphones?',
    'VS-048': 'Notes on one take', 'VS-049': 'Delete this take?', 'VS-050': 'Timing, Check timing, Key and the song’s switches',
    'VS-051': 'Add a song: from media, or type it in', 'VS-052': 'Name a section (Verse, Chorus…)', 'VS-053': 'This song’s marks, and the guide',
    'VS-054': 'Takes for this section, or all of them', 'VS-055': 'A take’s menu: Star, Rename, Delete', 'VS-056': 'Delete this take?',
    'VS-057': 'Old takes to keep or clear', 'VS-058': 'A comment on a take: edit or delete', 'VS-059': 'Stop the song’s length following its track?',
    'VS-060': 'Match the song’s length to its track again?', 'VS-061': 'A line on how to sing a section', 'VS-062': 'Stop this section sharing with its copies?',
    'VS-063': 'Pinned is full: unpin one first', 'VS-064': 'Give the song a new name', 'VS-065': 'Delete this song (or the chosen songs)?',
    'VS-066': 'Replace or remove the track, jog wheel side', 'VS-067': 'Remove the track from this phone?', 'VS-068': 'A marker’s menu: rename, loop, section start',
    'VS-069': 'Make this marker a section start', 'VS-070': 'Give the marker a name', 'VS-071': 'Clear every marker?',
    'VS-072': 'A shorter track: trim what’s past its end, or keep it', 'VS-073': 'A large file: add it anyway?', 'VS-074': 'Add your own exercise',
    'VS-075': 'Describe what the exercise is', 'VS-076': 'Delete this exercise?', 'VS-077': 'How much space recordings use',
    'VS-078': 'Delete every recording?', 'VS-079': 'Remove the coach video from this phone?', 'VS-080': 'Delete the rescued copy?',
    'VS-081': 'Set this month’s minutes back to zero?', 'VS-082': 'Delete everything and start again?', 'VS-083': 'Making the backup file',
    'VS-084': 'The backup file is ready to save', 'VS-085': 'Ask the phone to keep the app’s data', 'VS-086': 'What a backup file holds, before restoring',
    'VS-087': 'Where backups go and how to keep them', 'VS-088': 'Every backup made from this phone', 'VS-089': 'Restoring a backup',
    'VS-090': 'Put things back as they were before the restore?', 'VS-091': 'Undoing the restore', 'VS-092': 'The session clock: each step’s slice, and Pause',
    'VS-093': 'The floating window for a take, track or video', 'VS-094': 'The launch screen as the app opens', 'VS-095': 'Hold a mark: a quick reminder of it',
    'VS-096': 'Find your bridge: one slow slide, then From and To',
    'VS-097': 'A suggested pattern in the song’s key, on its note', 'VS-098': 'Choose the song’s key: Major or Minor, and its home note',
    'VS-099': 'A song’s sheet music: key, bars, range, tempo, to check', 'VS-100': 'A print just read: check it, set the octave and tempo, save',
    'VS-101': 'This print is on another song: open it, or add it here', 'VS-102': 'A print with another title: this song, a new one, or cancel',
    'VS-103': 'Replace the sheet music? The old score is kept 30 days', 'VS-104': 'A big or long PDF: read it anyway?',
    'VS-105': 'Remove the prints and keep every score?', 'VS-106': 'Reading a print, line by line, with Cancel',
    'VS-107': 'Delete sheet music whose song has gone?',
}

# ---------- doors the scan can't test (Q35): swipes, holds, timed sheets and file pickers, written by hand ----------
DOORS = [
    # swipes
    {'from': 'VS-013', 'to': 'VS-076', 'how': 'Swipe your own exercise’s row left, then Delete', 'kind': 'Swipe'},
    {'from': 'VS-008', 'to': 'VS-065', 'how': 'Swipe a song left, then Delete', 'kind': 'Swipe'},
    {'from': 'VS-007', 'to': 'VS-043', 'how': 'Swipe a song practice left, then Delete', 'kind': 'Swipe'},
    {'from': 'VS-054', 'to': 'VS-056', 'how': 'Swipe a take left, then Delete', 'kind': 'Swipe'},
    # holds
    {'from': 'VS-008', 'to': 'VS-064', 'how': 'Hold a song, then Rename', 'kind': 'Hold'},
    {'from': 'VS-008', 'to': 'VS-063', 'how': 'Hold a song, then Pin, with Pinned already full', 'kind': 'Hold'},
    {'from': 'VS-054', 'to': 'VS-055', 'how': 'Hold a take', 'kind': 'Hold'},
    {'from': 'VS-054', 'to': 'VS-058', 'how': 'Hold a comment on a take', 'kind': 'Hold'},
    {'from': 'VS-010', 'to': 'VS-068', 'how': 'Hold a marker', 'kind': 'Hold'},
    {'from': 'VS-009', 'to': 'VS-095', 'how': 'On the Marks side, tap a word, then hold a mark button (a starting state opens it)', 'kind': 'Hold'},
    # timed
    {'from': 'VS-002', 'to': 'VS-035', 'how': 'Come back to a running session after a long gap', 'kind': 'Timed'},
    {'from': 'VS-083', 'to': 'VS-084', 'how': 'When the backup file is ready', 'kind': 'Timed'},
    {'from': 'VS-089', 'to': 'VS-001', 'how': 'When the restore is done', 'kind': 'Timed'},
    {'from': 'VS-091', 'to': 'VS-019', 'how': 'When the undo is done', 'kind': 'Timed'},
    # file pickers, and import, export and restore (never tapped by the scan)
    {'from': 'VS-019', 'to': 'VS-083', 'how': 'Export backup: makes a file to save or share', 'kind': 'File'},
    {'from': 'VS-019', 'to': 'VS-086', 'how': 'Check a backup: choose a backup file', 'kind': 'File picker'},
    {'from': 'VS-019', 'to': 'VS-089', 'how': 'Import backup: choose a file, then Restore', 'kind': 'File picker'},
    {'from': 'VS-019', 'to': 'VS-090', 'how': 'Undo last restore (shows after a restore)', 'kind': 'After a restore'},
    {'from': 'VS-090', 'to': 'VS-091', 'how': 'Undo: puts the data back (never tapped)', 'kind': 'Replaces your data'},
    {'from': 'VS-022', 'to': 'VS-015', 'how': 'Add coach video: choose a video file (a starting state adds the tests’ one)', 'kind': 'File picker'},
    {'from': 'VS-009', 'to': 'VS-073', 'how': 'Add track: choose a file over the size limit', 'kind': 'File picker'},
    {'from': 'VS-066', 'to': 'VS-072', 'how': 'Replace track… with a shorter file (a starting state does this)', 'kind': 'File picker'},
    {'from': 'VS-004', 'to': 'VS-047', 'how': 'Sing with the song’s track on this phone and Sing over the track on', 'kind': 'Microphone'},
    {'from': 'VS-004', 'to': 'VS-097', 'how': 'Sing two ladder rungs, set the song key on Lines, then › on a suggested pattern', 'kind': 'Microphone'},
    {'from': 'VS-094', 'to': 'VS-019~rescued-data', 'how': 'The app opens with saved data it can’t read; the toast leads here', 'kind': 'Timed'},
    # Q42 sheet music: file pickers, the questions a print can ask, and the reading pill
    {'from': 'VS-051', 'to': 'VS-100', 'how': 'Choose sheet music: a UG print fills in the new song (a starting state reads one on the Song page)', 'kind': 'File picker'},
    {'from': 'VS-009', 'to': 'VS-106', 'how': 'While a print reads, line by line, with Cancel', 'kind': 'Timed'},
    {'from': 'VS-009', 'to': 'VS-101', 'how': 'Add sheet music: a print already on another song', 'kind': 'File picker'},
    {'from': 'VS-009', 'to': 'VS-102', 'how': 'Add sheet music: a print whose title isn’t the song’s', 'kind': 'File picker'},
    {'from': 'VS-099', 'to': 'VS-103', 'how': 'Replace with a new print…, then choose a print', 'kind': 'File picker'},
    {'from': 'VS-009', 'to': 'VS-104', 'how': 'Add sheet music: a PDF over 30 MB or 40 pages', 'kind': 'File picker'},
    {'from': 'VS-100', 'to': 'VS-098', 'how': 'Save sheet music: the print’s key is offered on the key sheet', 'kind': 'After a read'},
    {'from': 'VS-020', 'to': 'VS-107', 'how': 'A sheet whose song was deleted or reset, under Sheets with no song: Delete', 'kind': 'After a reset'},
]


# ---------- flows (Q35): the main journeys from the register (js/register.js), walked through their real buttons ----------
# Each step taps one button, then the scan takes a picture. Steps with capture=False tap without a picture (several level
# rings, or Sing before waiting for the recording); a step with only js waits (UNTIL) and then takes the picture.
_wait = lambda cond, what: UNTIL(cond, what)[1]
RIVER = ':has-text("River Song")'   # the sample song made in prepare()
FLOWS = [
    dict(id='F-01', title='Focused session', start='today', setup=['mic'], start_moment='Today',
         caption='A whole session on one page: Foundation, Rotation, then a song in Application, saved',
         steps=[dict(tap='#app [data-a="start"]', moment='Foundation, fresh'),
                dict(tap='#app [data-a="ring"][data-k="slides"]', capture=False),
                dict(tap='#app [data-a="ring"][data-k="humming"]', capture=False),
                dict(tap='#app [data-a="ring"][data-k="lip"]', capture=False),
                dict(tap='#app [data-a="ring"][data-k="straw"]', label='Tap each row’s level', moment='levels set'),
                dict(tap='#dock [data-a="cta"]', moment='Rotation'),
                dict(tap='#dock [data-a="cta"]', moment='Application'),
                dict(tap='#app [data-a="apSong"]' + RIVER, moment='a song picked'),
                dict(tap='#apcard [data-a="apSing"]', capture=False),
                dict(js=_wait("!!rec&&!!document.querySelector('#apcard.rec')", 'the recording didn’t start'), wait=1200, label='Sing', moment='recording'),
                dict(tap='#apcard [data-a="apStop"]', capture=False),
                dict(js=_wait("!rec&&TAKES.length===1&&!document.querySelector('#apcard .tkwv.wait')", 'the take wasn’t saved'), label='Stop', moment='takes'),
                dict(tap='#apcard [data-a="apDone"]', moment='song done'),
                dict(tap='#dock [data-a="cta"]', moment='Session saved'),
                dict(tap='#app [data-name="done-button"]', moment='back on Today')]),
    dict(id='F-02', title='Song practice', start='today', setup=['mic'], start_moment='Today',
         caption='Pick a song, record a take, say how it went, saved',
         steps=[dict(tap='#app [data-a="songStart"]', moment='pick a song'),
                dict(tap='#app [data-a="sgOpen"]' + RIVER, moment='the song'),
                dict(tap='#app [data-a="sgPractise"]', moment='Song practice'),
                dict(tap='#app [data-a="rec"]', capture=False),
                dict(js=_wait('!!rec', 'the recording didn’t start'), wait=1200, label='Record', moment='recording'),
                dict(tap='#app [data-a="rec"]', capture=False),
                dict(js=_wait('!rec&&TAKES.length===1', 'the take wasn’t saved'), label='Stop', moment='a take recorded'),
                dict(tap='#dock [data-a="cta"]', moment='How did it go?'),
                dict(tap='.scrim .sheet [data-a="saveHow"]', moment='saved')]),
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
# a sheet's own buttons are looked for inside it, so a row underneath can't be tapped instead. The peek card (#mkpeek,
# VS-095) counts as one too (Q35): it's drawn over the song page with its own ID and buttons, like a sheet
SHEET = '.scrim .sheet, #mkpeek'
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
