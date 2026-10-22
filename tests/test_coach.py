"""3.16 the coach video: added on the device from Files (never in backups), its chapters, the player page (levels,
Loop, Speed, the scrubber, the exercise list), its doors (Exercises tab, an exercise's page, a session step), the one
<video> kept playing across redraws, the floating window holding it, and every size in light and dark.
The fixtures are synthetic WebM files (Playwright's Chromium can't play H.264): one as long as the real video
(4773 s, so it has chapters) and one of 60 s (no chapters). The real video is never in the repo.
3.16.1: the chapters are the YouTube timestamps in content.js (COACH_TIMES), one start per exercise, so the real app
has no level jumps. youtube() checks that. The level tests put in made-up level times (LEVELS) to check the level
picker, Loop of a level and the level segments still work for exercises given three times."""
import json
from harness import fix, OUT
from test_layout import SIZES, FITS

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']
LONG, SHORT = fix('coach-chapters.webm'), fix('coach-short.webm')
# the YouTube timestamps (content.js COACH_TIMES), in seconds
YT = {1: 0, 2: 435, 3: 790, 4: 1170, 5: 1485, 6: 1605, 7: 1960, 8: 2480, 9: 2917, 10: 3410, 11: 3870, 12: 4260}
# made-up level times on top of them, only for the level tests
CH = {1: [0, 126, 373], 2: [435, 578, 683], 3: [790, 940, 1056], 4: [1170, 1271, 1382], 5: [1485, 1540, 1571],
      6: [1605, 1718, 1834], 7: [1960, 2160, 2333], 8: [2480, 2627, 2758], 9: [2917, 3121, 3278],
      10: [3410, 3625, 3756], 11: [3870, 3972, 4093], 12: [4260, 4418, 4539]}
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


def add(pg, f=LONG):
    pg.set_input_files('#coachIn', f)
    pg.wait_for_function("COACH.has()&&!COACH.busy()", timeout=15000)
    pg.wait_for_timeout(250)


def near(pg, sec, tol=2.0):
    return abs(pg.evaluate(T) - sec) < tol


def settings(pg):
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(200)
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
    ok(pg.evaluate("U.tab") == 'settings' and not pg.evaluate("U.view"), 'and opens Settings')
    pg.evaluate("go(()=>{U.tab='exercises';U.view='coach'})"); pg.wait_for_timeout(200)
    ok(pg.locator('#app .empty').count() == 1 and pg.locator('#app [data-a=coachSettings]').count() == 1,
       'the player page with no video shows a short empty state with Add coach video…')

    settings(pg); add(pg)
    txt = settings(pg)
    ok('coach-chapters.webm' in txt and '12 exercises · 0.1 MB' in txt, 'once added, Settings shows its name, 12 exercises and its size')
    ok(pg.locator('#app [data-a=coachAdd] .lbl').inner_text().strip() == 'Replace video…' and pg.locator('#app [data-v=coachDel]').count() == 1,
       'with Replace video… and Remove video')
    ok('Coach video' in pg.locator('#app .grp').filter(has_text='Recordings').inner_text(), 'the Storage group counts the video')
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
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=15000)
    txt = pg.evaluate("pendingExport.file.text()")
    ok('coach-chapters' not in txt and 'video/webm' not in txt and len(txt) < 60000, 'a backup doesn’t contain the coach video')
    pg.click('.xbtn'); pg.wait_for_timeout(300)
    p = OUT + '/coach-backup.json'
    open(p, 'w', encoding='utf-8').write(txt)
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(p); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(400)
    ok(pg.evaluate("COACH.has()&&COACH.chapters()"), 'restoring a backup leaves the stored video alone')
    settings(pg)
    pg.click('[data-a=sheet][data-v=resetAll]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=resetAll]'); pg.wait_for_function("!D.sessions.length", timeout=5000); pg.wait_for_timeout(300)
    ok(pg.evaluate("COACH.has()"), 'Reset all data leaves the coach video (only Remove removes it)')
    pg.reload(); t_ready(pg)
    ok(pg.evaluate("COACH.has()"), 'and it’s still there after a reload')
    pg.context.close()


def levels(pg):
    pg.evaluate(LEVELS, {str(k): v for k, v in CH.items()}); pg.wait_for_timeout(100)


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

    # the list: an exercise from its current level (falsetto has none logged: L1; the rung's latest is L3)
    pg.click('#app [data-a=coachEx][data-k=falsetto]'); pg.wait_for_timeout(700)
    ok(near(pg, CH[4][0]) and not pg.evaluate(PAUSED), 'tapping Falsetto voice plays it from Level 1 (none logged)')
    ok(pg.inner_text('#cvTitle') == 'Exercise 4 · Falsetto voice' and pg.inner_text('#cvLevel') == 'Level 1 of 3', 'it says Exercise 4 · Falsetto voice, Level 1 of 3')
    ok(pg.locator('#app [data-a=coachEx][data-k=falsetto] .cvwave').count() == 1, 'its row shows the wave bars')
    ok(pg.locator('#app .cvsegs i').count() == 3, 'the scrubber is the exercise’s three levels')
    ok('Level 1' in pg.evaluate("navigator.mediaSession.metadata&&navigator.mediaSession.metadata.title||''"), 'the lock screen gets the exercise and level')
    for l in (2, 3, 1):
        pg.click(f'#app [data-a=coachLv][data-v="{l}"]'); pg.wait_for_timeout(300)
        ok(near(pg, CH[4][l - 1]) and pg.locator(f'#app .cvlv button.on[data-v="{l}"]').count() == 1, f'L{l} jumps to that level’s start')
    pg.click('#app [data-a=coachEx][data-k=rung]'); pg.wait_for_timeout(500)
    ok(near(pg, CH[7][2]), 'the rung plays from Level 3, its latest logged level')
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
    ok(row.count() == 1 and 'Play with coach' in row.inner_text() and 'Level 3' in row.inner_text(), 'an exercise page has Play with coach at its level (Level 3)')
    ok(pg.locator('#app [data-a=openCoach][data-k=rung][data-zk="coach:rung"]').count() == 1, 'and it zooms into the player')
    pg.evaluate("go(()=>{U.view='ex';U.exId='c0_x'})"); pg.wait_for_timeout(200)
    ok(pg.locator('#app [data-a=openCoach]').count() == 0, 'your own exercises (not in the video) have no Play with coach row')
    pg.evaluate("go(()=>{U.view='ex';U.exId='rung'})"); pg.wait_for_timeout(200)
    pg.click('#app [data-a=openCoach][data-k=rung]'); pg.wait_for_timeout(600)
    ok(pg.evaluate("U.view") == 'coach' and near(pg, CH[7][2]) and not pg.evaluate(PAUSED), 'it opens the player playing the rung at Level 3')
    pg.click('#barL [data-a=coachBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'ex' and pg.evaluate("U.exId") == 'rung', 'Back goes back to the exercise page')
    pg.evaluate("COACH.pause()")

    # a session step: hidden until tapped
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(150)
    pg.click('[data-a=start]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'found' and pg.locator('#app [data-a=coachShow]').count() == 1 and pg.locator('#app .cv-slot').count() == 0,
       'Foundation shows a Coach video row, with the player hidden')
    ok('Level 3' in pg.locator('#app [data-a=coachShow]').inner_text() and 'Vocal slides' in pg.locator('#app [data-a=coachShow]').inner_text(),
       'the row names the first exercise and its level (Vocal slides · Level 3)')
    pg.click('#app [data-a=coachShow]'); pg.wait_for_timeout(600)
    ok(pg.evaluate(IN_SLOT) and not pg.evaluate(PAUSED) and near(pg, CH[1][2]), 'tapping it shows the video in the step, playing Vocal slides Level 3')
    ok(pg.evaluate("X.cv===true") and pg.evaluate("JSON.parse(localStorage.getItem('vocalDraft')).cv===true"), 'it stays shown for this session (saved on the draft)')
    ok('Vocal slides · Level 3' in pg.inner_text('#cvCap'), 'its caption says what’s playing')
    pg.click('#app [data-a=coachStepEx][data-v="1"]'); pg.wait_for_timeout(400)
    ok(near(pg, CH[2][2]) and not pg.evaluate(PAUSED), '› moves to the step’s next exercise (Humming, Level 3), still playing')
    pg.evaluate("rerender()"); pg.wait_for_timeout(300)
    ok(not pg.evaluate(PAUSED) and pg.evaluate(IN_SLOT), 'a redraw of the step doesn’t stop it')
    ok(pg.evaluate("X.start>0") and pg.evaluate("!X.paused"), 'the session timer carries on separately')

    # Next: Rotation is cued, paused
    pg.evaluate("X.f={slides:2,humming:3,lip:2,straw:1};saveDraft();rerender()")
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(250); pg.click('.sheet [data-a=confirmF]'); pg.wait_for_timeout(500)
    want = pg.evaluate("(()=>{const id=COACH.stepEx('rot');return COACH_CH[COACH_MAP[id]][COACH.level(id)-1]})()")
    ok(pg.evaluate("U.view") == 'rot' and pg.evaluate(IN_SLOT), 'after Next, Rotation shows the video (no tap needed again)')
    ok(pg.evaluate(PAUSED) and near(pg, want), 'cued to Rotation’s first exercise at its level, paused')
    pg.click('#barL [data-a=view]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'found' and pg.evaluate(PAUSED) and near(pg, CH[1][1]), 'Back to Foundation cues Vocal slides at this session’s Level 2, paused')
    pg.evaluate("X.fEnd=Date.now();X.fE=1;X.rot={falsetto:2};saveDraft();go(()=>{U.view='rot'})"); pg.wait_for_timeout(300)
    ok(near(pg, CH[4][1]), 'Rotation cues the exercise you picked (Falsetto voice, Level 2)')
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(300)
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'app' and pg.locator('#app .cv-slot').count() == 0 and pg.evaluate(PAUSED),
       'Application has no chapter: the slot hides and the video pauses')
    t.shot(pg, 'app-step')
    pg.context.close()


def youtube(b, t):
    """The real chapters: one start per exercise, from the YouTube timestamps. No level jumps."""
    ok = t.ok
    pg = t.page(b, touch=True)
    ok(pg.evaluate("Object.keys(COACH_CH).map(k=>COACH_CH[k])") == [[YT[n]] for n in range(1, 13)],
       'the chapters are exactly the YouTube timestamps, one per exercise')
    ok(pg.evaluate("[coachSecs('1:04:30'),coachSecs('7:15'),coachSecs('0:00'),isNaN(coachSecs('7.15')),isNaN(coachSecs(''))]") == [3870, 435, 0, True, True],
       'times read as h:mm:ss or m:ss; anything else is ignored')
    ok(pg.evaluate("COACH_MAP.falsetto===4&&COACH_MAP.upperlower===5&&COACH_MAP.straw===6&&COACH_IDS.length===12"),
       'every exercise is matched to its place in the video (Upper to lower voice included)')
    settings(pg); add(pg)
    txt = settings(pg)
    ok('12 exercises · 0.1 MB' in txt and 'levels' not in txt.split('Coach video')[1][:200], 'Settings says 12 exercises, no levels')
    pg.evaluate("go(()=>{U.tab='exercises';U.view='coach'})"); pg.wait_for_timeout(200)
    ok('12 exercises' in pg.inner_text('#app .note') and 'levels' not in pg.inner_text('#app .note'), 'the player says 12 exercises')
    for n, id in enumerate(pg.evaluate("COACH_IDS"), 1):
        pg.click(f'#app [data-a=coachEx][data-k={id}]'); pg.wait_for_timeout(250)
        ok(near(pg, YT[n], 0.6), f'exercise {n} ({id}) starts at its YouTube time')
    pg.click('#app [data-a=coachEx][data-k=falsetto]'); pg.wait_for_timeout(500)
    ok(not pg.evaluate(PAUSED) and pg.inner_text('#cvTitle') == 'Exercise 4 · Falsetto voice', 'Falsetto voice plays from 19:30')
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
    ok(near(pg, YT[7], 0.6) and not pg.evaluate(PAUSED), 'and plays Singing on the rung from 32:40')
    pg.evaluate("COACH.pause()")

    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(150)
    pg.click('[data-a=start]'); pg.wait_for_timeout(300)
    r = pg.inner_text('#app [data-a=coachShow]')
    ok('Coach video' in r and 'Vocal slides' in r and 'Level' not in r, 'the session row names the exercise, no level')
    pg.click('#app [data-a=coachShow]'); pg.wait_for_timeout(500)
    ok(near(pg, 0, 0.8) and not pg.evaluate(PAUSED), 'tapping it plays Vocal slides from 0:00')
    pg.click('#app [data-a=coachStepEx][data-v="1"]'); pg.wait_for_timeout(400)
    ok(near(pg, YT[2], 0.8) and pg.inner_text('#cvCap') == 'Exercise 2 · Humming', '› goes to Humming at 7:15')
    pg.evaluate(LEAVE); pg.wait_for_timeout(400)
    ok(pg.inner_text('#fw .fwk') == 'Humming', 'the window says Humming')
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
    ok(pg.inner_text('#fw .fwk') == 'Falsetto', 'its bar says Falsetto')
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

    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(250)
    ok(pg.evaluate(PAUSED) and pg.evaluate("FW.shown") == 'video', 'its button pauses, and the window stays')
    ok(pg.locator('#fw .fwx').is_visible(), 'paused, a small ✕ appears')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(250)
    ok(not pg.evaluate(PAUSED) and not pg.locator('#fw .fwx').is_visible(), 'it plays again from the window, and the ✕ goes')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    pg.click('#fw [data-a=coachX]'); pg.wait_for_timeout(500)
    ok(not pg.evaluate("FW.shown") and pg.evaluate(PAUSED), '✕ dismisses it')
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'video', 'playing again brings it back')
    pg.click('#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
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
    pg.click('#app [data-a=coachShow]'); pg.wait_for_timeout(500)
    pg.evaluate("scrollTo(0,0)")
    pg.evaluate(LEAVE); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'video' and pg.evaluate(IN_FW), 'video → session: the playing video has the window over a running session')
    pg.click('#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'found' and pg.evaluate(IN_SLOT) and not pg.evaluate(PAUSED), 'tapping it goes back to the session step, still playing')
    pg.evaluate("COACH.pause()"); pg.evaluate(LEAVE); pg.wait_for_timeout(300)
    pg.click('#fw [data-a=coachX]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'session', 'dismissed, the session’s window takes its place')
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
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(400)
    pg.click('#fw [data-a=coachX]')
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
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(400)
    pg.evaluate("window._ma=MOTION.animate;MOTION.animate=function(){const a=window._ma.apply(this,arguments);if(a)a.pause();return a}")
    pg.click('#fw [data-a=coachX]')
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
            pg.click('[data-a=start]'); pg.wait_for_timeout(250)
            pg.click('#app [data-a=coachShow]'); pg.wait_for_timeout(300)
            ok(pg.evaluate(FITS) and pg.evaluate(IN_SLOT), f'{tag}: a session step with the video fits')
            if name in ('iphone', 'iphone-se'): t.shot(pg, f'step-{name}-{sc}')
            pg.evaluate(LEAVE); pg.wait_for_timeout(400)
            ok(pg.evaluate(IN_FW), f'{tag}: the video window shows')
            ok(pg.evaluate("(()=>{const f=document.getElementById('fw').getBoundingClientRect();return f.left>=0&&f.top>=0&&f.right<=innerWidth+0.5&&f.bottom<=innerHeight+0.5})()"),
               f'{tag}: and sits on screen')
            if name in ('iphone',): t.shot(pg, f'window-{name}-{sc}')
            pg.context.close()


def run(b, t):
    youtube(b, t)
    storage(b, t)
    backups(b, t)
    player(b, t)
    doors(b, t)
    window(b, t)
    dismiss(b, t)
    zoom(b, t)
    layout(b, t)
