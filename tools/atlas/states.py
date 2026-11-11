"""Visual App Atlas · Vocal Sessions' screen states (Q46 · Atlas: Screen States, on Atlas kit 1.2.0).

One state for every Live screen in the register (js/register.js), by its screen ID: the sample data it needs (setup,
the names in screens.py's load() and SETUP_JS) and the real taps that reach it (steps). A pictures-only rescan
(`python3 tools/atlas/atlas.py --pictures`) opens each one and takes its picture; a full rescan also taps every button.
screens.py adds these after the tabs, which stay there.

- Taps name the part (`'VS-001 › start-session-button'`, `'› settings-button'` for a shared part), so a redesign that
  moves a button doesn't break its state. `[data-k="…"]` picks a row by its key and `:has-text("…")` by what it says,
  never by its place. A part with no name yet keeps its selector, and is listed in README › Unnamed parts.
- Screens are reached through their real buttons (the Q30 rule). Set-up (sample data, a made-up microphone, a file
  chosen) is the only shortcut. UNTIL waits for the app, HOLD holds a button for 0.7 s and SWIPE drags a row left, as a
  finger does; none of them opens a screen itself.
- After its steps the kit reads the screen's ID off the page; a state that lands anywhere else is Failed, "opened VS-0xx
  instead of VS-0yy".
- NO_STATE: a screen that can't be held on screen with sample data, with one plain line saying why.
- Adding a screen: give it a state here (or a reason) in the same build; test_atlas.py › coverage fails without one.
  A full scan writes a draft for every screen it found by tapping into its folder's suggested_states.py.
"""
import json

ARROW = '›'


# ---------- steps that wait, hold or swipe (Q35, Q46) ----------
def UNTIL(cond, what, ms=10000):
    """Wait for the app (a recording to start, a take to be saved). If it never is, the state is Failed with `what`."""
    return ('js', 'async()=>{/*until*/const t0=performance.now();while(!(' + cond + ')){if(performance.now()-t0>' + str(ms)
            + ')throw new Error(' + json.dumps('Didn’t open: ' + what, ensure_ascii=False) + ');await new Promise(r=>setTimeout(r,50))}}')


def HOLD(sel, ms=700):
    """Press a real button for about 0.7 s and let go, as a finger does (a hold isn't a tap, so it can't be a 'tap' step)."""
    return ('js', 'async()=>{/*hold*/const b=document.querySelector(' + json.dumps(sel, ensure_ascii=False) + ');if(!b)throw new Error('
            + json.dumps('Didn’t open: couldn’t hold ' + sel + ' (not on screen)', ensure_ascii=False) + ');'
            'const r=b.getBoundingClientRect(),o={bubbles:true,cancelable:true,composed:true,pointerId:7,pointerType:"touch",isPrimary:true,'
            'clientX:r.left+r.width/2,clientY:r.top+r.height/2};b.dispatchEvent(new PointerEvent("pointerdown",o));'
            'await new Promise(r=>setTimeout(r,' + str(ms) + '));b.dispatchEvent(new PointerEvent("pointerup",o));'
            'await new Promise(r=>setTimeout(r,150))}')


def SWIPE(sel, dx=-110):
    """Drag a real row to the left with a thumb's touches, so its Delete (or Pin) shows. The next step taps that button."""
    return ('js', 'async()=>{/*swipe*/const b=document.querySelector(' + json.dumps(sel, ensure_ascii=False) + ');if(!b)throw new Error('
            + json.dumps('Didn’t open: couldn’t swipe ' + sel + ' (not on screen)', ensure_ascii=False) + ');'
            'const r=b.getBoundingClientRect(),y=r.top+r.height/2,x0=r.left+r.width*0.7;'
            'const T=x=>new Touch({identifier:7,target:b,clientX:x,clientY:y,pageX:x,pageY:y});'
            'const f=(k,x)=>b.dispatchEvent(new TouchEvent(k,{bubbles:true,cancelable:true,composed:true,touches:k==="touchend"?[]:[T(x)],'
            'targetTouches:k==="touchend"?[]:[T(x)],changedTouches:[T(x)]}));'
            # the app's rows listen for touches (Progress, Exercises, takes) or for pointers (Songs), so both are sent
            'const P=(k,x)=>b.dispatchEvent(new PointerEvent(k,{bubbles:true,cancelable:true,composed:true,pointerId:7,pointerType:"touch",isPrimary:true,clientX:x,clientY:y}));'
            'P("pointerdown",x0);f("touchstart",x0);for(let i=1;i<=6;i++){const x=x0+' + str(dx) + '*i/6;P("pointermove",x);f("touchmove",x);await new Promise(r=>setTimeout(r,16))}'
            'P("pointerup",x0+' + str(dx) + ');f("touchend",x0+' + str(dx) + ');await new Promise(r=>setTimeout(r,250))}')


def T(ref):
    """A tap on a part by name: T('VS-009 › song-row[data-k="{song}"]'). {song} is the sample song's id (prepare())."""
    return ('tap', ref)


def IN(screen, css):
    """A CSS selector inside a sheet (for HOLD and SWIPE, which take selectors)."""
    return '#layer [data-screen="' + screen + '"] ' + css


# ---------- the ways in that many states share ----------
SONG = '[data-k="{song}"]'
RIVER = '.rowc[aria-label="River Song"]'   # the sample song's row, for HOLD and SWIPE (selectors only; {song} is for taps)
SONG_PAGE = [T('› songs-tab'), T('VS-008 › song-row' + SONG)]
SONG_CONTROLS = SONG_PAGE + [T('VS-009 › controls-button')]
TRACK = SONG_PAGE + [T('VS-009 › control-tile[data-v="timing"]')]
MARKERS = TRACK + [T('VS-010 › level-picker[data-v="3"]'), HOLD('#trkGrid .trktlb[data-k="m0"]')]
LYRICS = SONG_CONTROLS + [T('VS-050 › control-tile[data-v="lyrics"]')]
ANNOTATE = LYRICS + [T('› edit-mode-tab[data-v="annotate"]'), UNTIL("U.sEdit==='annotate'&&!!document.querySelector('[data-a=sgCue]')", 'the Marks side didn’t open')]
TAKES = SONG_PAGE + [T('VS-009 › takes-button' + SONG)]
SONG_PRACTICE = SONG_PAGE + [T('VS-009 › song-practice-row' + SONG)]
HOW = SONG_PAGE + [T('VS-009 › song-practice-row'), T('VS-012 › save-button')]
SETTINGS = [T('› settings-button')]
SET_ROW = lambda v: SETTINGS + [T('VS-018 › settings-row[data-v="' + v + '"]')]
STORAGE = SET_ROW('storage')
BACKUP = SET_ROW('backup')
SESSION = [T('› progress-tab'), T('VS-006 › session-row[data-v="session"][data-k="s2"]')]
EXERCISES = [T('› exercises-tab')]
CHECK_TIMING = SONG_CONTROLS + [T('VS-050 › control-tile[data-v="check"]')]
APPL_REC = UNTIL("!!rec&&!!document.querySelector('#apcard.rec')", 'the recording didn’t start')
APPL_SING = [T('VS-001 › resume-session-button'), T('VS-004 › song-row' + SONG), T('VS-004 › sing-button'), APPL_REC]
APPL_STOP = lambda n: [('wait', 1200), T('VS-004 › stop-button'),
                       UNTIL("!rec&&TAKES.length===" + str(n) + "&&!document.querySelector('#apcard .tkwv.wait')", 'take ' + str(n) + ' wasn’t saved')]
READ_PRINT = [T('VS-009 › sheet-music-row'), UNTIL("U.sheet==='melTitle'", 'the print wasn’t read', 20000)]


# ---------- the states ----------
# Starting states from before Q46 keep their ids, titles and code keys, so notes and the map stay where they were.
ROOTS = [
    # the session's later steps, through Today's real Resume button with a session part-way through
    dict(id='session-rotation', screen='VS-003', title='Session · Rotation', area='Session', kind='Screen', key='Screen:rot',
         steps=[T('VS-001 › resume-session-button')], setup=['found-done']),
    dict(id='session-application', screen='VS-004', title='Session · Application', area='Session', kind='Screen', key='Screen:app',
         steps=[T('VS-001 › resume-session-button')], setup=['rot-done']),
    # a song with everything on it: its track (added through the real Add track button) and three takes
    dict(id='song-page', screen='VS-009', title='Song page', area='Songs', kind='Screen', key='Screen:lyr', steps=SONG_PAGE, setup=['track', 'takes']),
    dict(id='song-section', screen='VS-009', title='Song page · section selected', area='Songs', kind='State', key='Screen:lyr',
         steps=SONG_PAGE + [T('VS-009 › section-row')], setup=['track', 'takes'], state_of='song-page', state='section selected', taps=True),

    # ----- Q35 · Atlas: Starting States -----
    # VS-015 · Coach video: the player, with the tests' made-up video added (the real door is a file picker)
    dict(id='coach-video', screen='VS-015', title='Coach video', area='Exercises', kind='Screen', key='Screen:coach',
         steps=EXERCISES + [T('VS-013 › coach-video-row'), UNTIL('COACH.has()&&!COACH.busy()', 'the coach video didn’t load')],
         setup=['coach'], docs=[('MAINTAINING.md', 'The coach video')]),
    # VS-004 · Application: recording, its take, and two takes to compare (a made-up microphone; no track, so no Sing over the track)
    dict(id='session-recording', screen='VS-004', title='Session · Application · recording', area='Session', kind='State', key='Screen:app',
         steps=APPL_SING + [('wait', 1000)], setup=['rot-done', 'mic'], state_of='session-application', state='recording'),
    dict(id='session-takes', screen='VS-004', title='Session · Application · takes', area='Session', kind='State', key='Screen:app',
         steps=APPL_SING + APPL_STOP(1), setup=['rot-done', 'mic'], state_of='session-application', state='takes'),
    dict(id='session-compare', screen='VS-004', title='Session · Application · compare', area='Session', kind='State', key='Screen:app',
         steps=APPL_SING + APPL_STOP(1) + [T('VS-004 › sing-button'), APPL_REC] + APPL_STOP(2),
         # a page of its own: two takes in a row need a fresh copy, not the page the takes state used
         setup=['rot-done', 'mic', 'own-page:compare'], state_of='session-application', state='compare'),
    # VS-031 · How did it go?: song practice of the sample song with a take, then its real Save button
    dict(id='song-how', screen='VS-031', title='How did it go?', area='Songs', kind='Sheet', key='Sheet:how', steps=HOW, setup=['takes', 'song-draft']),
    # VS-095 · Peek card: on the Marks side, tap a word, then hold the Peak mark button
    dict(id='peek-card', screen='VS-095', title='Peek card', area='Songs', kind='Overlay', key='Screen:lyr',
         steps=SONG_PAGE + [T('VS-009 › edit-timing-button'), T('VS-009 › marks-tab'), ('tap', '#app .w >> nth=1'),
                            HOLD('#mksheet .mkb[data-v="peak"]'), UNTIL("!!document.getElementById('mkpeek')", 'the peek card didn’t show')],
         setup=['track', 'takes'], docs=[('MAINTAINING.md', 'Marks guide')]),
    # VS-011 · Check timing, and its Overlaps state: every line placed by hand, then a timed section moved
    dict(id='check-timing', screen='VS-011', title='Check timing', area='Songs', kind='Screen', key='Screen:ckCheck', steps=CHECK_TIMING, setup=['track', 'takes']),
    dict(id='check-timing-overlaps', screen='VS-011', title='Check timing · Overlaps', area='Songs', kind='State', key='Screen:ckCheck',
         steps=CHECK_TIMING, setup=['track', 'takes', 'timed', 'moved'], state_of='check-timing', state='overlaps'),
    # VS-072 · Past the new end: the track replaced through the track menu with a 20 s file, with lines and a marker past it
    dict(id='track-past-end', screen='VS-072', title='Past the new end', area='Songs', kind='Sheet', key='Sheet:trkPast',
         steps=SONG_PAGE + [T('VS-009 › open-track-button'), T('VS-010 › track-settings-button'), T('VS-066 › replace-track-button'),
                            UNTIL("U.sheet==='trkPast'", 'the shorter track didn’t ask about what’s past its end', 20000)],
         setup=['track', 'timed', 'late-marker', 'short-track']),
    # VS-019 · Settings › Backup, with a rescued copy of saved data that couldn't be read; and VS-080 · Delete the rescued
    # copy (its own starting state: the copy's button names the moment it was rescued, different in every fresh copy)
    dict(id='settings-backup', screen='VS-019', title='Settings › Backup', area='Settings', kind='Sub-page', key='Sub-page:backup', steps=BACKUP, setup=[]),
    dict(id='backup-rescued', screen='VS-019', title='Settings › Backup · rescued data', area='Settings', kind='State', key='Sub-page:backup',
         steps=BACKUP, setup=['damaged'], state_of='settings-backup', state='rescued data', taps=True,
         docs=[('MAINTAINING.md', 'Save safety (3.29, Q11)')]),
    dict(id='rescued-delete', screen='VS-080', title='Delete the rescued copy', area='Settings', kind='Sheet', key='Sheet:rescueDel',
         steps=BACKUP + [T('VS-019 › delete-copy-button')], setup=['damaged']),
    # Q42 and Q47: VS-100 · Sheet music read (the made-up print's title isn't the sample song's, so VS-102 asks first);
    # VS-108 · Sheet music page and VS-099 · Sheet music, once a print is saved; VS-105 · Remove the prints?
    dict(id='sheet-music-read', screen='VS-100', title='Sheet music read', area='Songs', kind='Sheet', key='Sheet:melRead',
         steps=SONG_PAGE + READ_PRINT + [T('VS-102 › this-song-button'), UNTIL("U.sheet==='melRead'", 'the read print didn’t show')],
         setup=['pdf-next']),
    dict(id='sheet-music-page', screen='VS-108', title='Sheet music page', area='Songs', kind='Screen', key='Screen:mel',
         steps=SONG_PAGE + [T('VS-009 › sheet-music-row')], setup=['sheet']),
    dict(id='sheet-music', screen='VS-099', title='Sheet music', area='Songs', kind='Sheet', key='Sheet:melSheet',
         steps=SONG_PAGE + [T('VS-009 › sheet-music-row'), T('VS-108 › sheet-settings-button')], setup=['sheet']),
    dict(id='sheet-prints-delete', screen='VS-105', title='Remove the prints?', area='Settings', kind='Sheet', key='Sheet:melPrintsDel',
         steps=STORAGE + [T('VS-020 › remove-prints-row')], setup=['sheet']),

    # ----- Q46: every other Live screen, by its ID (first drafts from the full scan's suggested_states.py) -----
    # Today and the session
    dict(id='vs-002', screen='VS-002', steps=[T('VS-001 › start-session-button')], setup=[]),
    dict(id='vs-005', screen='VS-005', steps=[T('VS-001 › resume-session-button'), T('VS-003 › finish-here-button')], setup=['found-done']),
    dict(id='vs-032', screen='VS-032', steps=[T('VS-001 › resume-session-button'), T('VS-003 › finish-here-button')], setup=['found-done', 'long-session']),
    dict(id='vs-037', screen='VS-037', steps=[T('VS-001 › discard-session-button')], setup=['session']),
    dict(id='vs-038', screen='VS-038', steps=[T('VS-001 › date-line')], setup=[]),
    dict(id='vs-014', screen='VS-014', steps=[T('VS-001 › rotation-row[data-k="upperlower"]')], setup=[]),
    dict(id='vs-016', screen='VS-016', steps=[T('VS-001 › rotation-row[data-k="upperlower"]'), T('VS-014 › pattern-pill')], setup=[]),
    dict(id='vs-096', screen='VS-096', steps=[T('VS-001 › rotation-row[data-k="upperlower"]'), T('VS-014 › bridge-line')], setup=[]),
    # Progress
    dict(id='vs-007', screen='VS-007', steps=[T('› progress-tab'), T('VS-006 › show-all-row[data-v="sessions"]')], setup=[]),
    dict(id='vs-039', screen='VS-039', steps=SESSION, setup=[]),
    dict(id='vs-040', screen='VS-040', steps=SESSION + [T('VS-039 › edit-session-button[data-k="s2"]')], setup=[]),
    dict(id='vs-041', screen='VS-041', steps=SESSION + [T('VS-039 › delete-session-button[data-k="s2"]')], setup=[]),
    dict(id='vs-033', screen='VS-033', steps=SESSION + [T('VS-039 › edit-session-button[data-k="s2"]'), T('VS-040 › exercise-note-button[data-k="slides"]')], setup=[]),
    dict(id='vs-042', screen='VS-042', steps=[T('› progress-tab'), T('VS-006 › session-row[data-v="songSession"][data-k="sp1"]')], setup=['song-session']),
    dict(id='vs-043', screen='VS-043', steps=[T('› progress-tab'), T('VS-006 › session-row[data-v="songSession"][data-k="sp1"]'),
                                              T('VS-042 › delete-song-practice-button')], setup=['song-session']),
    # Songs
    dict(id='vs-051', screen='VS-051', steps=[T('› songs-tab'), T('VS-008 › new-song-button')], setup=[]),
    dict(id='vs-063', screen='VS-063', steps=[T('› songs-tab'), HOLD(RIVER), ('tap', '[data-a="sgCtxPin"]')], setup=['pins-full']),
    dict(id='vs-064', screen='VS-064', steps=[T('› songs-tab'), HOLD(RIVER), ('tap', '[data-a="sgCtxRename"]')], setup=[]),
    dict(id='vs-065', screen='VS-065', steps=[T('› songs-tab'), SWIPE(RIVER), T('VS-008 › swipe-delete-button' + SONG)], setup=[]),
    # the song page and its sheets
    dict(id='vs-050', screen='VS-050', steps=SONG_CONTROLS, setup=['track', 'takes']),
    dict(id='vs-053', screen='VS-053', steps=SONG_PAGE + [T('VS-009 › control-tile[data-v="key"]')], setup=['track', 'takes']),
    dict(id='vs-098', screen='VS-098', steps=SONG_PAGE + [T('VS-009 › key-row' + SONG)], setup=['track', 'takes']),
    dict(id='vs-059', screen='VS-059', steps=SONG_PAGE + [T('VS-009 › song-length-row')], setup=['track', 'takes']),
    dict(id='vs-060', screen='VS-060', steps=SONG_PAGE + [T('VS-009 › relink-button')], setup=['track', 'unlinked']),
    dict(id='vs-052', screen='VS-052', steps=LYRICS + [T('VS-009 › label-button')], setup=['track', 'takes']),
    dict(id='vs-061', screen='VS-061', steps=ANNOTATE + [T('VS-009 › cue-button')], setup=['track', 'takes']),
    dict(id='vs-062', screen='VS-062', steps=ANNOTATE + [T('VS-009 › unlink-button')], setup=['track', 'takes']),
    dict(id='vs-030', screen='VS-030', steps=SONG_PAGE + [T('VS-009 › edit-timing-button'), T('VS-009 › marks-tab'), ('tap', '#app .w >> nth=1'),
                                              HOLD('#mksheet .mkb[data-v="peak"]'), UNTIL("!!document.getElementById('mkpeek')", 'the peek card didn’t show'),
                                              T('VS-095 › learn-more-button[data-v="peak"]')], setup=['track', 'takes']),
    # takes
    dict(id='vs-054', screen='VS-054', steps=TAKES, setup=['track', 'takes']),
    dict(id='vs-055', screen='VS-055', steps=TAKES + [HOLD(IN('VS-054', '[data-name="take-row"]'))], setup=['track', 'takes']),
    dict(id='vs-056', screen='VS-056', steps=TAKES + [SWIPE(IN('VS-054', '[data-name="take-row"]')), T('VS-054 › delete-take-button')], setup=['track', 'takes']),
    dict(id='vs-058', screen='VS-058', steps=TAKES + [T('VS-054 › take-row'), HOLD('#layer .tkcm')], setup=['track', 'takes', 'take-comment']),
    # the track player and its sheets
    dict(id='vs-010', screen='VS-010', steps=TRACK, setup=['track', 'takes']),
    dict(id='vs-066', screen='VS-066', steps=TRACK + [T('VS-010 › track-settings-button')], setup=['track', 'takes']),
    dict(id='vs-067', screen='VS-067', steps=TRACK + [T('VS-010 › track-settings-button'), T('VS-066 › remove-track-button')], setup=['track', 'takes']),
    dict(id='vs-068', screen='VS-068', steps=MARKERS, setup=['track', 'late-marker']),
    dict(id='vs-071', screen='VS-071', steps=TRACK + [T('VS-010 › track-settings-button'), ('tap', IN('VS-066', '[data-a="sheet"][data-v="trkMkClear"]'))],
         setup=['track', 'late-marker']),
    dict(id='vs-073', screen='VS-073', steps=SONG_PAGE + [T('VS-009 › add-track-row')], setup=['big-track']),
    # song practice
    dict(id='vs-012', screen='VS-012', steps=SONG_PRACTICE, setup=['track', 'takes']),
    dict(id='vs-045', screen='VS-045', steps=SONG_PRACTICE + [T('VS-012 › add-song-button')], setup=['track', 'takes']),
    dict(id='vs-048', screen='VS-048', steps=SONG_PRACTICE + [T('VS-012 › take-note-button[data-k="lt3"]')], setup=['track', 'takes']),
    dict(id='vs-049', screen='VS-049', steps=SONG_PRACTICE + [T('VS-012 › take-note-button[data-k="lt3"]'), T('VS-048 › delete-button')], setup=['track', 'takes']),
    dict(id='vs-047', screen='VS-047', steps=TRACK + [T('› play-button'), ('wait', 500), T('› back-button'), T('VS-009 › song-practice-row'),
                                              T('VS-012 › record-button')], setup=['track', 'takes', 'mic']),
    dict(id='vs-044', screen='VS-044', steps=HOW + [T('VS-031 › skip-button')], setup=['takes', 'song-draft']),
    dict(id='vs-034', screen='VS-034', steps=HOW + [T('VS-031 › add-word-button[data-k="how"]')], setup=['takes', 'song-draft']),
    # sheet music
    dict(id='vs-102', screen='VS-102', steps=SONG_PAGE + READ_PRINT, setup=['pdf-next']),
    dict(id='vs-101', screen='VS-101', steps=[T('› songs-tab'), T('VS-008 › song-row[data-k="g_1"]'), T('VS-009 › sheet-music-row'),
                                              UNTIL("U.sheet==='melSame'", 'the print wasn’t found on the other song', 20000)], setup=['sheet', 'pdf-next']),
    dict(id='vs-104', screen='VS-104', steps=SONG_PAGE + [T('VS-009 › sheet-music-row')], setup=['big-pdf']),
    dict(id='vs-107', screen='VS-107', steps=STORAGE + [('tap', '#app [data-a="sheet"][data-v="melOrphanDel"]')], setup=['sheet', 'orphan-sheet']),
    # Exercises
    dict(id='vs-074', screen='VS-074', steps=EXERCISES + [T('VS-013 › add-exercise-row')], setup=[]),
    dict(id='vs-075', screen='VS-075', steps=EXERCISES + [T('VS-013 › exercise-row[data-k="c0_x"]'), T('VS-014 › edit-description-button')], setup=[]),
    dict(id='vs-076', screen='VS-076', steps=EXERCISES + [SWIPE('.sw[data-fk="delEx:c0_x"] .fg'), T('VS-013 › delete-exercise-button[data-k="c0_x"]')], setup=[]),
    # Settings
    dict(id='vs-020', screen='VS-020', steps=STORAGE, setup=[]),
    dict(id='vs-021', screen='VS-021', steps=SET_ROW('recall'), setup=[]),
    dict(id='vs-022', screen='VS-022', steps=SET_ROW('coach'), setup=[]),
    dict(id='vs-079', screen='VS-079', steps=SET_ROW('coach') + [('tap', '#app [data-a="sheet"][data-v="coachDel"]')], setup=['coach']),
    dict(id='vs-023', screen='VS-023', steps=SET_ROW('voice'), setup=[]),
    dict(id='vs-024', screen='VS-024', steps=SET_ROW('player'), setup=[]),
    dict(id='vs-025', screen='VS-025', steps=SET_ROW('appear'), setup=[]),
    dict(id='vs-026', screen='VS-026', steps=SET_ROW('access'), setup=[]),
    dict(id='vs-027', screen='VS-027', steps=SETTINGS + [T('VS-018 › changelog-row')], setup=[]),
    dict(id='vs-028', screen='VS-028', steps=SETTINGS + [T('VS-018 › marks-guide-row[data-v="home"]')], setup=[]),
    dict(id='vs-029', screen='VS-029', steps=SETTINGS + [T('VS-018 › marks-guide-row[data-v="home"]'), T('VS-028 › guide-row[data-v="how"]')], setup=[]),
    dict(id='vs-081', screen='VS-081', steps=SETTINGS + [T('VS-018 › reset-month-row')], setup=[]),
    dict(id='vs-082', screen='VS-082', steps=SETTINGS + [T('VS-018 › reset-all-row')], setup=[]),
    dict(id='vs-084', screen='VS-084', steps=SETTINGS + [T('VS-018 › reset-all-row'), T('VS-082 › back-up-button')], setup=[]),
    dict(id='vs-077', screen='VS-077', steps=STORAGE + [T('VS-020 › recordings-row')], setup=[]),
    dict(id='vs-078', screen='VS-078', steps=STORAGE + [T('VS-020 › recordings-row'), T('VS-077 › delete-all-button')], setup=[]),
    dict(id='vs-057', screen='VS-057', steps=STORAGE + [T('VS-020 › review-takes-row')], setup=[]),
    dict(id='vs-085', screen='VS-085', steps=STORAGE + [T('VS-020 › storage-protection-row')], setup=[]),
    dict(id='vs-087', screen='VS-087', steps=BACKUP + [T('VS-019 › backup-guide-row')], setup=[]),
    dict(id='vs-088', screen='VS-088', steps=BACKUP + [T('VS-019 › history-row')], setup=[]),
]

# A page of its own for every state that holds or swipes. The app ignores a tap that comes just after a hold or a swipe,
# by the clock, and the kit sets the clock back for each state on a reused page, so the next state's taps would all be
# ignored. 'own-page:<id>' sets nothing up; it only keeps the state off a shared page.
for _r in ROOTS:
    if any(st[0] == 'js' and st[1].startswith(('async()=>{/*hold*/', 'async()=>{/*swipe*/')) for st in _r['steps']):
        _r['setup'] = list(_r['setup']) + ['own-page:' + _r['id']]

# Screens that can't be held on screen with sample data, one plain line each (shown as "No state · <reason>")
NO_STATE = {
    'VS-035': 'Shows only when you come back to a running session after a long gap; a scan can’t wait that long',
    'VS-036': 'No button opens it in 3.72: a finished session lands on VS-005 · Session saved since Q21',
    'VS-046': 'No button opens it in 3.72: a song is deleted through VS-065 · Delete song (from its page)',
    'VS-069': 'Opens from the marker menu (hold a marker); after the scan’s made-up hold, the menu’s buttons don’t take its taps',
    'VS-070': 'Opens from the marker menu (hold a marker); after the scan’s made-up hold, the menu’s buttons don’t take its taps',
    'VS-083': 'Shows while a backup file is being made; the scan never makes or saves files',
    'VS-086': 'Needs a backup file chosen in the file picker; the scan never reads backup files',
    'VS-089': 'Shows while a backup replaces your data; the scan never restores',
    'VS-090': 'Shows only after a restore; the scan never restores',
    'VS-091': 'Shows while a restore is being undone; the scan never restores',
    'VS-092': 'Drawn over the session page, which the scan reads instead: tap the clock pill on VS-002',
    'VS-093': 'Drawn over other screens, which the scan reads instead: see VS-001 · session running',
    'VS-094': 'The launch screen is gone before the page settles',
    'VS-097': 'Opens only after singing two ladder rungs on Lines; the made-up microphone’s steady tone can’t sing them',
    'VS-103': 'Replace with a new print… opens no file picker in the scan’s browser, so the second print never arrives',
    'VS-106': 'Shows only while a print is being read, a second or two',
}
