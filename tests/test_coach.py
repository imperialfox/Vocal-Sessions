"""3.16 the coach video: added on the device from Files (never in backups), its chapters, the player page (levels,
Loop, Speed, the scrubber, the exercise list), its doors (Exercises tab, an exercise's page, a session step), the one
<video> kept playing across redraws, the floating window holding it, and every size in light and dark.
The fixtures are synthetic WebM files (Playwright's Chromium can't play H.264): one as long as the real video
(4773 s, so it has chapters) and one of 60 s (no chapters). The real video is never in the repo.
Q25: the chapters are the 36 measured level starts in content.js (COACH_TIMES, frame ÷ 24 to the hundredth of a
second, from tools/coach-video/data/level_frames.json). measured() taps all 36 and checks each lands inside its level's
first frame; every exercise opens at Level 1. single() puts in one start per exercise (LEVELS) to check an exercise
given one time still plays from its top, with no level switch."""
import json, os
from harness import fix, OUT
from test_layout import SIZES, FITS

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']
LONG, SHORT = fix('coach-chapters.webm'), fix('coach-short.webm')
# Q25: the measured level starts, in frames (24 a second), as the Q24 kit measured them from the video's green flash
_LF = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'coach-video', 'data', 'level_frames.json')))
FPS, FRAMES, TOTAL = _LF['fps'], _LF['level_start_frames'], _LF['total_frames']
# CH[n]: exercise n's three level starts in seconds (as content.js writes them, to the hundredth); YT[n]: its Level 1
CH = {n: [round(FRAMES[(n - 1) * 3 + l] / FPS, 2) for l in range(3)] for n in range(1, 13)}
YT = {n: CH[n][0] for n in CH}
LEVELS = "o=>{Object.keys(o).forEach(k=>COACH_CH[k]=o[k]);rerender()}"
T = "COACH.el().currentTime"
PAUSED = "COACH.el().paused"
IN_SLOT = "(()=>{const s=document.querySelector('#app .cv-slot'),v=document.getElementById('cv');return !!s&&!!v&&s.contains(v)})()"
IN_FW = "(()=>{const f=document.getElementById('fw'),v=document.getElementById('cv');return !!FW.shown&&!f.hidden&&!!v&&f.contains(v)})()"
LEAVE = "go(()=>{U.view=null;U.tab='today'})"
# a short, real (playable) recording: 4 s of quiet as a WAV, so a take can play in Chromium
WAV_TAKE = """async(id)=>{const n=8000*4,b=new ArrayBuffer(44+n*2),v=new DataView(b);const w=(o,s)=>[...s].forEach((c,i)=>v.setUint8(o+i,c.charCodeAt(0)));
 w(0,'RIFF');v.setUint32(4,36+n*2,true);w(8,'WAVE');w(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);
 v.setUint32(24,8000,true);v.setUint32(28,16000,true);v.setUint16(32,2,true);v.setUint16(34,16,true);w(36,'data');v.setUint32(40,n*2,true);
 for(let i=0;i<n;i++)v.setInt16(44+i*2,Math.round(Math.sin(i/9)*200),true);
 const bl=new Blob([b],{type:'audio/wav'});await putTake({id,songId:'g_1',created:Date.now()-864e5,len:4,size:bl.size,type:'audio/wav',blob:bl,star:false});
 await refreshTakes();rerender();}"""


# Q26: the coach video's window is just the picture: its controls show after a tap. These show them first, then tap
VNAME = "document.getElementById('fw').getAttribute('aria-label').replace(/^Coach video, /,'')"


def vshow(pg):
    pg.evaluate("FW.shown==='video'&&!FW.ctl&&fwCtl(true)")
    return False


def vclick(pg, sel):
    vshow(pg)
    pg.click(sel)


def add(pg, f=LONG):
    pg.set_input_files('#coachIn', f)
    pg.wait_for_function("COACH.has()&&!COACH.busy()", timeout=15000)
    pg.wait_for_timeout(250)


def near(pg, sec, tol=2.0):
    return abs(pg.evaluate(T) - sec) < tol


def settings(pg):
    # Settings › Coach video, its own page since 3.21
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='coach'})"); pg.wait_for_timeout(200)
    return pg.inner_text('#app')


def storage(b, t):
    ok = t.ok
    pg = t.page(b)
    txt = settings(pg)
    ok(pg.locator('#app [data-a=coachAdd] .lbl').inner_text().strip() == 'Add coach video…', 'Settings › Coach video offers Add coach video…')
    ok('isn’t included in backups' in txt and 'Keep the file in Files' in txt, 'its footer says it stays on the phone and isn’t in backups')
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(200)
    row = pg.locator('#app [data-a=coachSettings]')
    ok(row.count() == 1 and 'Add coach video' in row.inner_text(), 'with no video, the Exercises row reads Add coach video')
    row.click(); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.tab+'/'+U.view+'/'+U.setPg") == 'settings/set/coach', 'and opens Settings › Coach video')
    pg.evaluate("go(()=>{U.tab='exercises';U.view='coach'})"); pg.wait_for_timeout(200)
    ok(pg.locator('#app .empty').count() == 1 and pg.locator('#app [data-a=coachSettings]').count() == 1,
       'the player page with no video shows a short empty state with Add coach video…')

    settings(pg); add(pg)
    txt = settings(pg)
    ok('coach-chapters.webm' in txt and '12 exercises · 3 levels each · 0.1 MB' in txt, 'once added, Settings shows its name, 12 exercises with 3 levels each and its size')
    ok(pg.locator('#app [data-a=coachAdd] .lbl').inner_text().strip() == 'Replace video…' and pg.locator('#app [data-v=coachDel]').count() == 1,
       'with Replace video… and Remove video')
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='storage'})"); pg.wait_for_timeout(200)
    ok('Coach video' in pg.locator('#app .grp:not(.setuse)').filter(has_text='Recordings').inner_text(), 'Settings › Storage counts the video')
    settings(pg)
    ok(pg.evaluate("COACH.meta().chapters") and abs(pg.evaluate("COACH.meta().dur") - 4773) < 1, 'a 79:33 video gets the chapters')
    t.shot(pg, 'settings', full_page=True)

    pg.reload(); t_ready(pg)
    ok(pg.evaluate("COACH.has()") and 'coach-chapters.webm' in settings(pg), 'after a reload, it’s still there')

    add(pg, SHORT)
    txt = settings(pg)
    ok('No chapters' in txt and not pg.evaluate("COACH.chapters()"), 'a video of another length is a plain video: No chapters')
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(200)
    ok('No chapters' in pg.locator('#app [data-a=openCoach]').inner_text(), 'the Exercises row says No chapters')
    pg.evaluate("go(()=>{U.view='ex';U.exId='falsetto';U.exTab='summary'})"); pg.wait_for_timeout(200)
    ok(pg.locator('#app [data-a=openCoach]').count() == 0, 'no Play with coach row without chapters')
    pg.evaluate("go(()=>{U.view='coach'})"); pg.wait_for_timeout(200)
    ok(pg.locator('#app .cvlv').count() == 0 and pg.locator('#app [data-a=coachEx]').count() == 0 and pg.locator('#cvScrub').count() == 1,
       'its player has no levels or exercise list, just the scrubber over the whole video')

    settings(pg)
    pg.click('#app [data-a=sheet][data-v=coachDel]'); pg.wait_for_timeout(250)
    ok(pg.locator('.sheet .cta.red[data-a=coachDel]').count() == 1, 'Remove video asks “Are you sure?” with a red button')
    pg.click('.sheet [data-a=coachDel]'); pg.wait_for_function("!COACH.has()", timeout=5000); pg.wait_for_timeout(200)
    ok(pg.locator('#app [data-a=coachAdd] .lbl').inner_text().strip() == 'Add coach video…', 'removed: Settings offers Add again')
    pg.reload(); t_ready(pg)
    ok(not pg.evaluate("COACH.has()"), 'and it stays gone after a reload')
    pg.context.close()


def t_ready(pg):
    from harness import ready
    ready(pg)


def backups(b, t):
    ok = t.ok
    pg = t.page(b)
    settings(pg); add(pg)
    pg.evaluate("SET.open('backup')"); pg.wait_for_timeout(200); pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=15000)
    txt = pg.evaluate("pendingExport.file.text()")
    ok('coach-chapters' not in txt and 'video/webm' not in txt and len(txt) < 60000, 'a backup doesn’t contain the coach video')
    pg.click('.xbtn'); pg.wait_for_timeout(300)
    p = OUT + '/coach-backup.json'
    open(p, 'w', encoding='utf-8').write(txt)
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(p); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(400)
    ok(pg.evaluate("COACH.has()&&COACH.chapters()"), 'restoring a backup leaves the stored video alone')
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(200)  # the resets are on the main list
    pg.click('[data-a=sheet][data-v=resetAll]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=resetAll]'); pg.wait_for_function("!D.sessions.length", timeout=5000); pg.wait_for_timeout(300)
    ok(pg.evaluate("COACH.has()"), 'Reset all data leaves the coach video (only Remove removes it)')
    pg.reload(); t_ready(pg)
    ok(pg.evaluate("COACH.has()"), 'and it’s still there after a reload')
    pg.context.close()


def levels(pg):
    """Q25: the real chapters have the three levels, so there's nothing to put in; kept so the tests read as before."""
    ok = pg.evaluate("Object.keys(COACH_CH).every(k=>COACH_CH[k].length===3)")
    assert ok, 'every exercise has three level times'


def player(b, t):
    ok = t.ok
    pg = t.page(b)
    settings(pg); add(pg); levels(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(200)
    ok('12 exercises' in pg.locator('#app [data-a=openCoach]').inner_text(), 'the Exercises row says 12 exercises before it’s played')
    ok('3 levels each' in pg.evaluate("COACH.page()"), 'with level times for every exercise, the player says 3 levels each')
    pg.click('#app [data-a=openCoach]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'coach' and pg.evaluate(IN_SLOT) and pg.evaluate(PAUSED), 'it opens the player, with the video in its slot, paused')
    ok(pg.locator('#barL [data-a=coachBack][aria-label=Back]').count() == 1, 'with a Back button')
    ok(pg.locator('#cvScrub[data-own-gesture]').count() == 1, 'the scrubber claims its own gesture, so swipe back leaves it alone')

    # the list: Q25, every exercise opens at Level 1 (falsetto has none logged; the rung's latest is L3)
    pg.click('#app [data-a=coachEx][data-k=falsetto]'); pg.wait_for_timeout(700)
    ok(near(pg, CH[4][0]) and not pg.evaluate(PAUSED), 'tapping Falsetto voice plays it from Level 1')
    ok(pg.inner_text('#cvTitle') == 'Exercise 4 · Falsetto voice' and pg.inner_text('#cvLevel') == 'Level 1 of 3', 'it says Exercise 4 · Falsetto voice, Level 1 of 3')
    ok(pg.locator('#app [data-a=coachEx][data-k=falsetto] .cvwave').count() == 1, 'its row shows the wave bars')
    ok(pg.locator('#app .cvsegs i').count() == 3, 'the scrubber is the exercise’s three levels')
    ok('Level 1' in pg.evaluate("navigator.mediaSession.metadata&&navigator.mediaSession.metadata.title||''"), 'the lock screen gets the exercise and level')
    for l in (2, 3, 1):
        pg.click(f'#app [data-a=coachLv][data-v="{l}"]'); pg.wait_for_timeout(300)
        ok(near(pg, CH[4][l - 1]) and pg.locator(f'#app .cvlv button.on[data-v="{l}"]').count() == 1, f'L{l} jumps to that level’s start')
    pg.click('#app [data-a=coachEx][data-k=rung]'); pg.wait_for_timeout(500)
    ok(near(pg, CH[7][0], 0.5) and pg.evaluate("COACH.here().l") == 1, 'Q25: the rung plays from Level 1, not its latest logged Level 3')
    ok(pg.locator('#app [data-a=coachEx][data-k=rung] .cvwave').count() == 1 and pg.locator('#app .cvwave').count() == 1, 'and the wave bars move to its row')

    # a redraw while playing doesn't pause it (the video waits outside #app while it's redrawn)
    t1 = pg.evaluate(T)
    pg.evaluate("rerender()"); pg.evaluate("rerender()"); pg.wait_for_timeout(600)
    ok(not pg.evaluate(PAUSED) and pg.evaluate(T) > t1 and pg.evaluate(IN_SLOT), 'redrawing the page while it plays doesn’t pause it')

    # Loop: at the level's end, back to its start
    pg.click('#app [data-a=coachEx][data-k=falsetto]'); pg.wait_for_timeout(300)
    pg.click('#app [data-a=coachLv][data-v="2"]'); pg.wait_for_timeout(300)
    pg.click('#app [data-a=coachLoop]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("COACH.prefs().loop") and pg.locator('#app [data-a=coachLoop][aria-pressed=true]').count() == 1, 'Loop turns on')
    pg.evaluate(f"COACH.el().currentTime={CH[4][2] - 1}"); pg.wait_for_timeout(2600)
    tt = pg.evaluate(T)
    ok(CH[4][1] - 0.5 <= tt < CH[4][1] + 4, f'Loop jumps back to Level 2’s start at its end (at {tt:.1f})')
    # Q16: the jump back is timed like the track's loop: within a few ms of the level's end, never ¼ s early,
    # at 1× and at 0.75× (pitch kept)
    for sp in (1, 0.75):
        pg.evaluate("v=>{COACH.el().playbackRate=v}", sp)
        n0 = len(pg.evaluate("COACH.wraps()"))
        pg.evaluate(f"COACH.el().currentTime={CH[4][2] - 0.8}")
        pg.wait_for_function("COACH.el().currentTime<" + str(CH[4][2] - 0.5), timeout=3000)
        pg.evaluate("window.__mx=0;(function f(){const v=COACH.el();if(v&&!v.paused){if(v.currentTime<" + str(CH[4][2] + 1) + ")window.__mx=Math.max(window.__mx,v.currentTime);requestAnimationFrame(f)}})()")
        pg.wait_for_function("n=>COACH.wraps().length>n", arg=n0, timeout=int(6000 / sp))
        W = pg.evaluate("COACH.wraps()")[n0:]
        w = W[0]
        over = round(w['t'] - w['end'], 3)
        ok(abs(w['start'] - CH[4][1]) < 1e-6 and abs(w['end'] - CH[4][2]) < 1e-6 and -0.03 <= over <= 0.03,
           f'Q16 {sp}×: Loop jumps back to Level 2’s start within a few ms of its end ({over:+.3f} s, by {w["by"]})')
        ok(pg.evaluate("window.__mx") >= CH[4][2] - 0.03 and pg.evaluate("window.__mx") < CH[4][2] + 0.05 and pg.evaluate("COACH.el().preservesPitch!==false"),
           f'Q16 {sp}×: the level plays right to its end, no further ({pg.evaluate("window.__mx") - CH[4][2]:+.3f} s)')
        ok(pg.evaluate("COACH.here().l") == 2 and abs(pg.evaluate(T) - CH[4][1]) < 1.5, f'Q16 {sp}×: and it’s still Level 2')
    pg.evaluate("COACH.el().playbackRate=COACH.prefs().speed")
    pg.click('#app [data-a=coachLoop]'); pg.wait_for_timeout(100)
    pg.evaluate(f"COACH.el().currentTime={CH[4][2] - 1}"); pg.wait_for_timeout(2000)
    ok(pg.evaluate(T) > CH[4][2], 'with Loop off it carries on into Level 3')
    ok(pg.inner_text('#cvLevel') == 'Level 3 of 3' and pg.locator('#app .cvlv button.on[data-v="3"]').count() == 1, 'and the level picker follows along')

    # Speed: 0.75× · 1× · 1.25×, pitch kept
    sp = []
    for _ in range(3):
        pg.click('#app [data-a=coachSpeed]'); pg.wait_for_timeout(80)
        sp.append((pg.evaluate("COACH.el().playbackRate"), pg.inner_text('#app [data-a=coachSpeed]')))
    ok([x[0] for x in sp] == [1.25, 0.75, 1] and sp[0][1] == '1.25×' and sp[1][1] == '0.75×', 'Speed cycles 1.25× · 0.75× · 1×')
    ok(pg.evaluate("COACH.el().preservesPitch===true"), 'and keeps the pitch')
    pg.click('#app [data-a=coachSpeed]')

    # the scrubber: dragging seeks within this exercise, following the finger
    pg.evaluate("COACH.pause();scrollTo(0,0)"); pg.wait_for_timeout(200)
    segs = pg.evaluate("[...document.querySelectorAll('#app .cvsegs i')].map(e=>{const r=e.getBoundingClientRect();return [r.left,r.width,r.top+r.height/2]})")
    y = segs[0][2]
    pg.mouse.move(segs[0][0] + 2, y); pg.mouse.down()
    pg.mouse.move(segs[1][0] + segs[1][1] / 2, y, steps=6)
    mid = pg.evaluate(T)
    th = pg.evaluate("parseFloat(document.getElementById('cvThumb').style.left)")
    pg.mouse.up(); pg.wait_for_timeout(200)
    want = (CH[4][1] + CH[4][2]) / 2
    ok(abs(mid - want) < 6, f'dragging to the middle of Level 2 seeks there ({mid:.0f} for {want:.0f})')
    ok(abs(th - (segs[1][0] + segs[1][1] / 2 - pg.evaluate("document.getElementById('cvScrub').getBoundingClientRect().left"))) < 3, 'the thumb is under the finger')
    pg.mouse.move(segs[0][0] + segs[0][1] / 2, y); pg.mouse.down(); pg.mouse.move(segs[0][0] - 200, y, steps=4); pg.mouse.up(); pg.wait_for_timeout(200)
    ok(abs(pg.evaluate(T) - CH[4][0]) < 1, 'dragging past the start stops at the exercise’s start, not the video’s')
    pg.click('#cvPP'); pg.wait_for_timeout(300)
    ok(not pg.evaluate(PAUSED) and pg.locator('#cvPP[aria-label=Pause]').count() == 1, 'the play button plays')
    pg.click('#app .cv-slot'); pg.wait_for_timeout(300)
    ok(pg.evaluate(PAUSED), 'tapping the picture pauses')
    pg.evaluate("rerender()")
    ok(pg.locator('#cvPP[aria-label=Play]').count() == 1, 'and the button says Play')

    # remembered on this device (Speed was left on 1.25× above)
    pg.evaluate("COACH.el().pause()"); pg.wait_for_timeout(200)
    where = pg.evaluate(T)
    pg.reload(); t_ready(pg)
    pg.wait_for_function("COACH.el()&&COACH.el().readyState>=1", timeout=10000); pg.wait_for_timeout(300)
    ok(near(pg, where) and pg.evaluate("COACH.el().playbackRate") == 1.25, 'after a reload it’s where you left it, at the same speed')
    ok(not pg.evaluate("FW.shown"), 'and no window pops up on its own after a reload')
    levels(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(200)
    ok('Paused at Falsetto voice · Level' in pg.locator('#app [data-a=openCoach]').inner_text(), 'the Exercises row says where it’s paused')
    ok(not pg.evaluate("'vocalCoach' in (JSON.parse(localStorage.getItem('vocalTracker'))||{})"), 'its settings aren’t in the app data (so never in backups)')
    pg.context.close()


def doors(b, t):
    ok = t.ok
    pg = t.page(b)
    settings(pg); add(pg); levels(pg)
    # an exercise page
    pg.evaluate("go(()=>{U.tab='exercises';U.view='ex';U.exId='rung';U.exTab='summary'})"); pg.wait_for_timeout(200)
    row = pg.locator('#app [data-a=openCoach][data-k=rung]')
    ok(row.count() == 1 and 'Play with coach' in row.inner_text() and 'From Level 1' in row.inner_text() and 'Level 3' not in row.inner_text(),
       'Q25: an exercise page has Play with coach, From Level 1 (not its logged Level 3)')
    ok(pg.locator('#app [data-a=openCoach][data-k=rung][data-zk="coach:rung"]').count() == 1, 'and it zooms into the player')
    pg.evaluate("go(()=>{U.view='ex';U.exId='c0_x'})"); pg.wait_for_timeout(200)
    ok(pg.locator('#app [data-a=openCoach]').count() == 0, 'your own exercises (not in the video) have no Play with coach row')
    pg.evaluate("go(()=>{U.view='ex';U.exId='rung'})"); pg.wait_for_timeout(200)
    pg.click('#app [data-a=openCoach][data-k=rung]'); pg.wait_for_timeout(600)
    ok(pg.evaluate("U.view") == 'coach' and near(pg, CH[7][0], 0.5) and pg.evaluate("COACH.here().l") == 1 and not pg.evaluate(PAUSED),
       'it opens the player playing the rung from Level 1')
    pg.click('#barL [data-a=coachBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'ex' and pg.evaluate("U.exId") == 'rung', 'Back goes back to the exercise page')
    pg.evaluate("COACH.pause()")

    # Q19 the one-page session: Foundation and Rotation show the video in the floating window, Application a Coach pill
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(150)
    pg.click('[data-a=start]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'found' and pg.locator('#app .cv-slot').count() == 0 and pg.evaluate("FW.shown") == 'video' and pg.evaluate(IN_FW),
       'Foundation shows the coach video in the floating window, not on the page')
    ok(pg.evaluate(PAUSED) and near(pg, CH[1][0], 0.1) and pg.evaluate("COACH.here().l") == 1, 'Q25: cued to Vocal slides at Level 1 (not your Level 3), paused')
    ok(pg.evaluate("X.cv===true") and pg.evaluate("JSON.parse(localStorage.getItem('vocalDraft')).cv===true"), 'cued once for this session (saved on the draft)')
    ok(pg.evaluate(VNAME).startswith('Vocal slides') or pg.evaluate(VNAME).startswith('Slides'), 'the window names the exercise')
    vclick(pg, '#fw [data-a=fwToggle]'); pg.wait_for_timeout(400)
    ok(not pg.evaluate(PAUSED) and pg.evaluate("FW.shown") == 'video', 'its button plays it, in the window')
    pg.evaluate("rerender()"); pg.wait_for_timeout(300)
    ok(not pg.evaluate(PAUSED) and pg.evaluate(IN_FW), 'a redraw of the page doesn’t stop it')
    ok(pg.evaluate("X.start>0") and pg.evaluate("!X.paused"), 'the session timer carries on separately')
    vclick(pg, '#fw [data-a=fwX]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'coachpill' and pg.evaluate(PAUSED) and pg.locator('#fw .fwpill').count() == 1,
       '✕ tucks it into a Coach pill, paused')
    vclick(pg, '#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'video' and pg.evaluate(IN_FW), 'tapping the pill brings the video back')

    # Log foundation: Rotation is cued, paused
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(200)
    pg.evaluate("X.f={slides:2,humming:3,lip:2,straw:1};saveDraft();rerender()")
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(500)
    want = pg.evaluate("(()=>{const id=COACH.stepEx('rot');return COACH_CH[COACH_MAP[id]][0]})()")
    ok(pg.evaluate("U.view") == 'rot' and pg.evaluate("FW.shown") == 'video' and pg.evaluate(IN_FW), 'on Rotation the window stays')
    ok(pg.evaluate(PAUSED) and near(pg, want, 0.1) and pg.evaluate("COACH.here().l") == 1, 'cued to Rotation’s first exercise at Level 1, paused')
    vclick(pg, '#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'coach' and pg.evaluate(IN_SLOT), 'tapping the window opens the full player')
    # Q25: the video's level switch never changes the level logged, and pausing then coming back resumes there
    logged = pg.evaluate("JSON.stringify([X.f,X.rot||{}])")
    pg.click('#app [data-a=coachLv][data-v="3"]'); pg.wait_for_function("COACH.here().l===3", timeout=3000)
    ok(pg.evaluate("JSON.stringify([X.f,X.rot||{}])") == logged, 'Q25: L3 in the player leaves the session’s logged levels as they were')
    pg.evaluate("COACH.pause()"); left = pg.evaluate(T)
    pg.click('#barL [data-a=coachBack]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'rot' and pg.evaluate("FW.shown") == 'video', 'and its Back returns to the session')
    ok(abs(pg.evaluate(T) - left) < 0.05 and pg.evaluate("COACH.here().l") == 3, 'Q25: paused at Level 3, it’s still there back in the session')
    pg.evaluate("X.rot={falsetto:2};saveDraft();rerender()")
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(300)
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'app' and pg.evaluate(PAUSED) and pg.evaluate("FW.shown") == 'coachpill',
       'Application has no chapter: the video pauses and a Coach pill shows instead')
    t.shot(pg, 'app-step')
    vclick(pg, '#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'video' and pg.evaluate(PAUSED), 'the pill brings the video back in Application, paused')
    t.shot(pg, 'app-step')
    pg.context.close()


IN_FRAME = """(f)=>{const t=COACH.el().currentTime;return t>=f/24&&t<(f+1)/24}"""


def measured(b, t):
    """Q25: the real chapters are the 36 measured level starts. Every level tap lands inside its first frame."""
    ok = t.ok
    pg = t.page(b, touch=True)
    got = pg.evaluate("Object.keys(COACH_CH).map(k=>COACH_CH[k])")
    ok(len(got) == 12 and all(len(c) == 3 for c in got), 'all 12 exercises have three level times')
    ok(all(abs(got[i // 3][i % 3] * FPS - f) <= 0.5 for i, f in enumerate(FRAMES)), 'each is its measured frame ÷ 24, within half a frame')
    ok(pg.evaluate("[coachSecs('7:17.21')===437.21,coachSecs('1:04:30.25')===3870.25,coachSecs('0:00.00')===0,coachSecs('2:02.96')===122.96]") == [True] * 4,
       'part-seconds read as m:ss.ff and h:mm:ss.ff (7:17.21 is exactly 437.21)')
    ok(pg.evaluate("[coachSecs('1:04:30'),coachSecs('7:15'),coachSecs('0:00'),isNaN(coachSecs('7.15')),isNaN(coachSecs('')),isNaN(coachSecs('7:1x.2')),isNaN(coachSecs('7.5:15'))]")
       == [3870, 435, 0, True, True, True, True], 'whole-second times still read; anything else is ignored')
    ok(pg.evaluate("COACH_MAP.falsetto===4&&COACH_MAP.upperlower===5&&COACH_MAP.straw===6&&COACH_IDS.length===12"),
       'every exercise is matched to its place in the video (Upper to lower voice included)')
    # VID: the measured lengths, Level 1 to the next exercise's Level 1, adding up to the video
    vid = pg.evaluate("COACH_IDS.map(id=>VID[id])")
    ends = [FRAMES[n * 3] for n in range(1, 12)] + [TOTAL]
    ok(all(abs(vid[n] - (ends[n] - FRAMES[n * 3]) / FPS) < 0.06 for n in range(12)), 'each VID length is its measured length, to a tenth of a second')
    ok(abs(sum(vid) - TOTAL / FPS) < 1 and abs(sum(vid) - pg.evaluate("COACH_END")) < 1, f'the VID lengths add up to the video ({sum(vid):.1f} s)')
    settings(pg); add(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view='coach'})"); pg.wait_for_timeout(200)
    ok('12 exercises · 3 levels each' in pg.inner_text('#app .note'), 'the player says 12 exercises · 3 levels each')
    misses = []
    for n, id in enumerate(pg.evaluate("COACH_IDS"), 1):
        pg.click(f'#app [data-a=coachEx][data-k={id}]')
        pg.wait_for_function("n=>COACH.here().n===n&&!!document.querySelector('#app [data-a=coachEx].cvon[data-k=\"'+COACH_IDS[n-1]+'\"]')", arg=n, timeout=5000)
        first = pg.evaluate("COACH.here().l") == 1 and abs(pg.evaluate(T) - CH[n][0]) < 0.5
        if not first: misses.append(f'{id} opened at L{pg.evaluate("COACH.here().l")}')
        pg.evaluate("COACH.pause()")
        for l in (3, 1, 2):  # out of order, so each tap really moves
            f = FRAMES[(n - 1) * 3 + l - 1]
            pg.click(f'#app [data-a=coachLv][data-v="{l}"]')
            if not (pg.evaluate(IN_FRAME, f) and pg.evaluate("COACH.here().l") == l and pg.evaluate("COACH.here().n") == n):
                misses.append(f'{id} L{l} at {pg.evaluate(T):.3f} for frame {f} ({f / FPS:.3f})')
    ok(not misses, 'all 36 level taps land inside their level’s first frame, never in the one before' + (': ' + '; '.join(misses) if misses else ''))
    # replay: tapping the lit level goes back to its start
    pg.click('#app [data-a=coachEx][data-k=humming]'); pg.wait_for_function("COACH.here().n===2", timeout=5000)
    pg.click('#app [data-a=coachLv][data-v="2"]'); pg.evaluate("COACH.play()")
    pg.wait_for_function(f"COACH.el().currentTime>{CH[2][1] + 1.2}", timeout=5000)
    ok(pg.locator('#app .cvlv button.on[data-v="2"]').count() == 1, 'playing Level 2, L2 is lit')
    pg.evaluate("COACH.pause()")
    pg.click('#app [data-a=coachLv][data-v="2"]')
    ok(pg.evaluate(IN_FRAME, FRAMES[4]) and pg.evaluate("COACH.here().l") == 2, 'tapping the lit L2 goes back to the start of Level 2')
    pg.context.close()


def single(b, t):
    """An exercise given one time instead of three (LEVELS puts in each Level 1 only): no level switch, from its top."""
    ok = t.ok
    pg = t.page(b, touch=True)
    one = "o=>{Object.keys(o).forEach(k=>COACH_CH[k]=o[k])}"
    pg.evaluate(one, {str(k): [v] for k, v in YT.items()})
    settings(pg); add(pg)
    txt = settings(pg)
    ok('12 exercises · 0.1 MB' in txt and 'levels' not in txt.split('Coach video')[1][:200], 'Settings says 12 exercises, no levels')
    pg.evaluate("go(()=>{U.tab='exercises';U.view='coach'})"); pg.wait_for_timeout(200)
    ok('12 exercises' in pg.inner_text('#app .note') and 'levels' not in pg.inner_text('#app .note'), 'the player says 12 exercises')
    for n, id in enumerate(pg.evaluate("COACH_IDS"), 1):
        pg.click(f'#app [data-a=coachEx][data-k={id}]'); pg.wait_for_timeout(250)
        ok(near(pg, YT[n], 0.6), f'exercise {n} ({id}) starts at its time')
    pg.click('#app [data-a=coachEx][data-k=falsetto]'); pg.wait_for_timeout(500)
    ok(not pg.evaluate(PAUSED) and pg.inner_text('#cvTitle') == 'Exercise 4 · Falsetto voice', 'Falsetto voice plays from 19:29.96')
    ok(pg.locator('#app .cvlv').count() == 0 and not pg.locator('#cvLevel').is_visible(), 'no level picker or level line without level times')
    ok(pg.locator('#app .cvsegs i').count() == 1, 'the scrubber is the whole exercise')
    ok(pg.evaluate("navigator.mediaSession.metadata.title") == 'Falsetto voice', 'the lock screen shows the exercise, no level')
    pg.click('#app [data-a=coachLoop]'); pg.wait_for_timeout(100)
    ok(pg.locator('#app [data-a=coachLoop][aria-label="Loop this exercise"][aria-pressed=true]').count() == 1, 'Loop repeats the exercise')
    pg.evaluate(f"COACH.el().currentTime={YT[5] - 1}"); pg.wait_for_timeout(2600)
    tt = pg.evaluate(T)
    ok(YT[4] - 0.5 <= tt < YT[4] + 4, f'at the end of Falsetto voice, Loop goes back to its start (at {tt:.1f})')
    pg.click('#app [data-a=coachLoop]'); pg.wait_for_timeout(100)
    pg.evaluate(f"COACH.el().currentTime={YT[5] - 1}"); pg.wait_for_timeout(2200)
    ok(pg.evaluate(T) > YT[5] and pg.inner_text('#cvTitle') == 'Exercise 5 · Upper to lower voice', 'with Loop off it carries on into Upper to lower voice')
    pg.evaluate("COACH.cue('falsetto',1,false);scrollTo(0,0)"); pg.wait_for_timeout(300)
    sg = pg.evaluate("(()=>{const r=document.querySelector('#app .cvsegs i').getBoundingClientRect();return [r.left,r.width,r.top+r.height/2]})()")
    pg.mouse.move(sg[0] + 2, sg[2]); pg.mouse.down(); pg.mouse.move(sg[0] + sg[1] / 2, sg[2], steps=5); pg.mouse.up(); pg.wait_for_timeout(200)
    ok(abs(pg.evaluate(T) - (YT[4] + YT[5]) / 2) < 6, 'dragging to the middle of the bar goes to the middle of the exercise')

    pg.evaluate("go(()=>{U.view='ex';U.exId='rung';U.exTab='summary'})"); pg.wait_for_timeout(200)
    row = pg.locator('#app [data-a=openCoach][data-k=rung]')
    ok(row.count() == 1 and 'From the start of the exercise' in row.inner_text() and 'Level' not in row.inner_text(), 'Play with coach says it starts from the top')
    row.click(); pg.wait_for_timeout(500)
    ok(near(pg, YT[7], 0.6) and not pg.evaluate(PAUSED), 'and plays Singing on the rung from 32:41.04')
    pg.evaluate("COACH.pause()")

    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(150)
    pg.click('[data-a=start]'); pg.wait_for_timeout(400)
    r = pg.evaluate(VNAME)
    ok(pg.evaluate("FW.shown") == 'video' and 'L' not in r.replace('Vocal slides', '').replace('Slides', ''), 'the session’s window names the exercise, no level')
    ok(near(pg, 0, 0.8) and pg.evaluate(PAUSED), 'cued to Vocal slides from 0:00')
    pg.evaluate("COACH.cue('humming',1,true)"); pg.wait_for_timeout(400)
    pg.evaluate(LEAVE); pg.wait_for_timeout(400)
    ok(pg.evaluate(VNAME) == 'Humming', 'the window says Humming')
    pg.context.close()


def window(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    settings(pg); add(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(150)
    pg.click('#app [data-a=openCoach]'); pg.wait_for_timeout(300)
    pg.click('#app [data-a=coachEx][data-k=falsetto]'); pg.wait_for_timeout(500)
    ok(not pg.evaluate("FW.shown"), 'no window on the player’s own page')
    pg.evaluate(LEAVE); pg.wait_for_timeout(500)
    ok(pg.evaluate("FW.shown") == 'video' and pg.evaluate(IN_FW), 'leaving while it plays shows the video window, holding the video itself')
    t1 = pg.evaluate(T); pg.wait_for_timeout(700)
    ok(not pg.evaluate(PAUSED) and pg.evaluate(T) > t1, 'and it keeps playing')
    ok(pg.evaluate(VNAME) == 'Falsetto · Level 1', 'its label says Falsetto · Level 1 (Q25: every exercise has levels; Q26: the picture has no bar)')
    r = pg.evaluate("(()=>{const r=document.getElementById('fw').getBoundingClientRect();return [r.width,r.height]})()")
    ok(abs(r[0] - 176) < 1 and abs(r[1] - 99) < 1, 'it’s a 16:9 window, 176×99')
    t.shot(pg, 'window')
    for name, js in [('Songs', "go(()=>{U.tab='songs';U.view=null})"), ('Progress', "go(()=>{U.tab='history';U.view=null})")]:
        pg.evaluate(js); pg.wait_for_timeout(250)
        ok(pg.evaluate(IN_FW) and not pg.evaluate(PAUSED), f'it carries on over {name}')
    pg.evaluate("U.sheet='calendar';rerender()"); pg.wait_for_timeout(250)
    ok(not pg.evaluate("FW.shown") and not pg.evaluate(PAUSED), 'a sheet hides the window, and the video plays on')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(300)
    ok(pg.evaluate(IN_FW), 'it comes back when the sheet closes')

    vclick(pg, '#fw [data-a=fwToggle]'); pg.wait_for_timeout(250)
    ok(pg.evaluate(PAUSED) and pg.evaluate("FW.shown") == 'video', 'its button pauses, and the window stays')
    ok(pg.locator('#fw .fwx').is_visible(), 'paused, its controls show the ✕ (Q26: picture in picture)')
    vclick(pg, '#fw [data-a=fwToggle]'); pg.wait_for_timeout(250)
    ok(not pg.evaluate(PAUSED) and pg.locator('#fw .fwx').is_visible(), 'it plays again from the window, and the ✕ stays (3.20: on every sound, playing or paused)')
    vclick(pg, '#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    vclick(pg, '#fw [data-a=fwX]'); pg.wait_for_timeout(500)
    ok(not pg.evaluate("FW.shown") and pg.evaluate(PAUSED), '✕ dismisses it')
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'video', 'playing again brings it back')
    vclick(pg, '#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'coach' and pg.evaluate(IN_SLOT) and not pg.evaluate(PAUSED), 'tapping it goes back to the player, still playing')
    pg.click('#barL [data-a=coachBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") is None, 'Back leaves the player as before')

    # a take wins over the video, and each stops the other
    pg.evaluate(WAV_TAKE, 'tw'); pg.wait_for_timeout(200)
    pg.evaluate("playTake('tw')"); pg.wait_for_timeout(400)
    ok(pg.evaluate(PAUSED), 'playing a take pauses the coach video')
    pg.evaluate("go(()=>{U.tab='history';U.view=null})"); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'take', 'take → video: the playing take has the window')
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("playingId") is None and pg.evaluate("FW.shown") == 'video', 'playing the coach video stops the take')

    # in a session: video → session
    pg.evaluate("COACH.pause()"); pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(200)
    pg.click('[data-a=start]'); pg.wait_for_timeout(300)
    vclick(pg, '#fw [data-a=fwToggle]'); pg.wait_for_timeout(500)
    pg.evaluate("scrollTo(0,0)")
    pg.evaluate(LEAVE); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'video' and pg.evaluate(IN_FW), 'video → session: the playing video has the window over a running session')
    vclick(pg, '#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'found' and pg.evaluate(IN_FW) and not pg.evaluate(PAUSED), 'tapping it goes back to the session’s page, still playing in its window')
    pg.evaluate("COACH.pause()"); pg.wait_for_timeout(200)
    ok(pg.evaluate("FW.shown") == 'video' and pg.evaluate(PAUSED), 'Q19: paused over the session’s page, it stays in its window there')
    pg.evaluate(LEAVE); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'video', 'and, paused in its window, it keeps the window when you leave (3.20)')
    vclick(pg, '#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'found', 'tapping it goes back to the session')
    pg.evaluate("COACH.play()"); pg.evaluate(LEAVE); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'video', 'playing again, the video has the window')
    vclick(pg, '#fw [data-a=fwX]'); pg.wait_for_timeout(400)
    ok(not pg.evaluate("FW.shown"), '3.20: ✕ closes it, and nothing takes its place on this screen')
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'session', 'on the next screen, the session’s window shows again')
    pg.context.close()


# 3.17: Ivan's iPhone kept the window on screen after ✕ (black video area, the exercise name and Play). With motion on,
# ✕ must always end with #fw hidden within the fade's time, even if the fade never finishes, and only a play you
# asked for brings it back (a stray media play event doesn't)
FADE = "(()=>{const a=FW.hideAnim;try{return a?+a.effect.getTiming().duration:0}catch(e){return 0}})()"
GONE = "(()=>{const f=document.getElementById('fw');return !FW.shown&&!!f&&f.hidden})()"


def dismiss(b, t):
    ok = t.ok
    pg = t.page(b, touch=True, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    settings(pg); add(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(1300)
    pg.click('#app [data-a=openCoach]'); pg.wait_for_timeout(1300)
    pg.click('#app [data-a=coachEx][data-k=slides]'); pg.wait_for_timeout(400)
    pg.evaluate(LEAVE); pg.wait_for_timeout(1300)
    ok(pg.evaluate(IN_FW), 'motion on: leaving the player shows the video window')
    vclick(pg, '#fw [data-a=fwToggle]'); pg.wait_for_timeout(400)
    vclick(pg, '#fw [data-a=fwX]')
    d = pg.evaluate(FADE)
    ok(0 < d < 700, f'✕ fades the window out quickly ({d:.0f} ms)')
    pg.wait_for_timeout(int(d) + 200)
    ok(pg.evaluate(GONE) and pg.evaluate(PAUSED), '✕ hides the window within the fade’s time, and the video stays paused')
    # a media play event the app didn't ask for (iOS can fire one when the video is moved) doesn't bring it back
    pg.evaluate("COACH.el().dispatchEvent(new Event('play'))"); pg.wait_for_timeout(300)
    for name, js in [('Songs', "go(()=>{U.tab='songs';U.view=null})"), ('Progress', "go(()=>{U.tab='history';U.view=null})"),
                     ('Today', LEAVE)]:
        pg.evaluate(js); pg.wait_for_timeout(700)
        ok(pg.evaluate(GONE), f'after ✕ it stays hidden on {name}')
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(900)
    ok(pg.evaluate(IN_FW) and pg.locator('#fw').is_visible(), 'only Play brings it back, holding the video')

    # the fade never finishing (as on iOS): the window still hides once its time is up
    vclick(pg, '#fw [data-a=fwToggle]'); pg.wait_for_timeout(400)
    pg.evaluate("window._ma=MOTION.animate;MOTION.animate=function(){const a=window._ma.apply(this,arguments);if(a)a.pause();return a}")
    vclick(pg, '#fw [data-a=fwX]')
    d = pg.evaluate(FADE)
    pg.wait_for_timeout(60)
    ok(not pg.evaluate("document.getElementById('fw').hidden"), 'a fade that never finishes leaves the window up at first (the iPhone bug)')
    pg.wait_for_timeout(int(d) + 250)
    ok(pg.evaluate(GONE), 'but it’s hidden once the fade’s time is up anyway')
    pg.evaluate(LEAVE); pg.wait_for_timeout(500)
    ok(pg.evaluate(GONE), 'and it stays hidden after moving on')
    # the take window uses the same hiding
    pg.evaluate(WAV_TAKE, 'tx'); pg.wait_for_timeout(200)
    pg.evaluate("playTake('tx')"); pg.wait_for_timeout(300)
    pg.evaluate("go(()=>{U.tab='history';U.view=null})"); pg.wait_for_timeout(700)
    ok(pg.evaluate("FW.shown") == 'take' and not pg.evaluate("document.getElementById('fw').hidden"), 'a playing take has the window')
    pg.evaluate("stopPlayback();rerender()")
    d = pg.evaluate(FADE)
    pg.wait_for_timeout(int(d) + 250)
    ok(pg.evaluate(GONE), 'stopping the take hides its window, even if the fade never finishes')
    pg.evaluate("MOTION.animate=window._ma")
    pg.context.close()


def zoom(b, t):
    ok = t.ok
    pg = t.page(b, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    settings(pg); add(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(300)
    pg.click('#app [data-a=openCoach]'); pg.wait_for_timeout(100)
    ok(pg.locator('.zm').count() >= 1, 'the Exercises row zooms into the player (motion on)')
    pg.wait_for_timeout(1200)
    ok(pg.evaluate("U.view") == 'coach' and pg.locator('.zm').count() == 0 and [s['key'] for s in pg.evaluate("ZOOM.stack()")] == ['coach'],
       'the zoom finishes on the player, remembered as coming from its row')
    ok(pg.locator('.zm video').count() == 0, 'zoom copies never copy the video')
    pg.click('#barL [data-a=coachBack]'); pg.wait_for_timeout(1300)
    ok(pg.evaluate("U.view") is None and pg.evaluate("U.tab") == 'exercises' and pg.locator('.zm,.zm-src').count() == 0,
       'Back shrinks it into the row and leaves nothing behind')
    pg.context.close()


def layout(b, t):
    ok = t.ok
    for name, w, h, touch in SIZES:
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, touch=touch)
            settings(pg); add(pg)
            tag = f'{name} {sc}'
            pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(150)
            ok(pg.evaluate(FITS), f'{tag}: Exercises with the coach row fits')
            pg.evaluate("go(()=>{U.view='coach'})"); pg.evaluate("COACH.cue('falsetto',2,false)"); pg.wait_for_timeout(300)
            ok(pg.evaluate(FITS) and pg.evaluate(IN_SLOT), f'{tag}: the player fits, with the video in it')
            ok(pg.evaluate("(()=>{const s=document.querySelector('#app .cv-slot').getBoundingClientRect();return Math.abs(s.width/s.height-16/9)<0.02})()"),
               f'{tag}: the video is 16:9')
            ok(pg.evaluate("(()=>{const r=document.querySelector('#app .cvctl').getBoundingClientRect();return [...document.querySelectorAll('#app .cvctl > *')].every(e=>{const q=e.getBoundingClientRect();return q.right<=r.right+0.5&&q.left>=r.left-0.5})})()"),
               f'{tag}: levels, Loop and Speed fit on one line')
            if name in ('iphone', 'iphone-se', 'ipad', 'mac'): t.shot(pg, f'player-{name}-{sc}', full_page=True)
            pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(150)
            pg.click('[data-a=start]'); pg.wait_for_timeout(400)
            ok(pg.evaluate(FITS) and pg.evaluate(IN_FW), f'{tag}: the session’s page with the video window fits')
            ok(pg.evaluate("(()=>{const f=document.getElementById('fw').getBoundingClientRect(),c=document.querySelector('#dock [data-a=cta]').getBoundingClientRect();return f.bottom<=c.top})()"),
               f'{tag}: and the window sits above the pinned button')
            if name in ('iphone', 'iphone-se'): t.shot(pg, f'step-{name}-{sc}')
            pg.evaluate("COACH.play()"); pg.wait_for_timeout(300)
            pg.evaluate(LEAVE); pg.wait_for_timeout(400)
            ok(pg.evaluate(IN_FW), f'{tag}: the video window shows')
            ok(pg.evaluate("(()=>{const f=document.getElementById('fw').getBoundingClientRect();return f.left>=0&&f.top>=0&&f.right<=innerWidth+0.5&&f.bottom<=innerHeight+0.5})()"),
               f'{tag}: and sits on screen')
            if name in ('iphone',): t.shot(pg, f'window-{name}-{sc}')
            pg.context.close()


def run(b, t):
    measured(b, t)
    single(b, t)
    storage(b, t)
    backups(b, t)
    player(b, t)
    doors(b, t)
    window(b, t)
    dismiss(b, t)
    zoom(b, t)
    layout(b, t)
