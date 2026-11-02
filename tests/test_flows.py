"""A full day of use on iPhone: suggestions, a session with notes, the clock, editing, song practice and its sheet."""
import json, datetime as dt
from harness import now, OLD_DRAFT, ready, SP, until

def run(b, t):
    pg = t.page(b)
    ok = t.ok
    t.ok(pg.locator('.nudge').count() == 1, 'backup reminder shows after 20 days')

    # suggested rotation: never done first, then done before dates were kept, then the one done longest ago
    pg.evaluate("allRot().forEach(e=>D.ex[e.id]={n:1,last:new Date(Date.now()-864e5).toISOString()});D.ex.vertical={n:1,last:new Date(Date.now()-8*864e5).toISOString()};delete D.ex.upperlower")
    ok(pg.evaluate("suggested().id") == 'upperlower', 'suggestion: an exercise never done comes first')
    pg.evaluate("D.ex.upperlower={n:0,last:null}")
    ok(pg.evaluate("suggested().id") == 'upperlower', 'suggestion: 0 times with no date still counts as never done')
    pg.evaluate("D.ex.upperlower={n:2,last:new Date().toISOString()};D.ex.falsetto={n:1,last:null}")
    ok(pg.evaluate("suggested().id") == 'falsetto', 'suggestion: then exercises done before dates were kept')
    pg.evaluate("D.ex.falsetto={n:2,last:new Date().toISOString()}")
    ok(pg.evaluate("suggested().id") == 'vertical', 'suggestion: then the one done longest ago')
    pg.reload(); ready(pg)

    pg.click('button.dateline'); pg.wait_for_timeout(500); ok(pg.locator('.cal').count() == 1, 'tapping the date opens the calendar')
    pg.click('.scrim .ghost'); pg.wait_for_timeout(300)
    pg.click('.tbtn'); pg.wait_for_timeout(500); ok(pg.locator('.cal').count() == 1, 'tapping Today opens the calendar')
    pg.click('.scrim .ghost'); pg.wait_for_timeout(300)

    # Foundation with Skip and exercise notes (Q19: on one page, tapping each row through its levels; the words for
    # "What kept it at level N?" are saved as the exercise's note, as the notes sheet saved them)
    cnt = lambda e: pg.evaluate(f"(D.ex['{e}']||{{n:0}}).n")
    lip0, hum0 = cnt('lip'), cnt('humming')
    pg.click('[data-a=start]')
    ring = lambda k, n: [pg.click(f'#app .osec.active [data-a=ring][data-k={k}]') for _ in range(n)]
    for k, n in [('slides', 3), ('humming', 2), ('lip', 4), ('straw', 2)]:
        ring(k, n)
    ok(pg.evaluate("X.f") == {'slides': 3, 'humming': 2, 'lip': 0, 'straw': 2}, 'tapping the rows sets 3, 2, Skip and 2')
    hb = '#app .rgi[data-rk="f:humming"]'
    ok(until(pg, f"!!document.querySelector('{hb} .unfold.open')"), 'level 2 opens “What kept it at level 2?”')
    pg.click(f'{hb} [data-a=rcue][data-v="Lost the buzz"]')
    pg.click(f'{hb} [data-a=rown]'); pg.fill(f'{hb} .ownin', 'Nose tickle'); pg.keyboard.press('Enter')
    until(pg, "(X.xn.humming||{w:[]}).w.length===2")
    t.shot(pg, 'exercise-note')
    ok(pg.evaluate("X.xn.humming") == {'w': ['Lost the buzz', 'Nose tickle'], 't': ''}, 'exercise note saved with your own word')
    ok('Nose tickle' in pg.evaluate("D.words.x_humming"), 'your own word is kept for next time')

    # session clock
    pg.click('#timer'); pg.wait_for_timeout(700)
    pg.click('[data-a=pauseToggle]'); pg.wait_for_timeout(1300)
    t1 = pg.evaluate("elapsedSec()"); pg.wait_for_timeout(1200); t2 = pg.evaluate("elapsedSec()")
    ok(abs(t2 - t1) < 0.01 and pg.evaluate("X.paused"), 'paused time is not counted')
    t.shot(pg, 'clock-paused')
    pg.click('[data-a=pauseToggle]'); pg.wait_for_timeout(1100); ok(pg.evaluate("elapsedSec()") > t2, 'resume counts again')
    ok('❚❚' not in pg.inner_text('#timer'), 'the timer pill shows running time')
    pg.click('.sck .circ[data-a=clockClose]'); ok(until(pg, "!document.querySelector('.clock')"), '✕ closes the clock (Q22)')

    pg.click('[data-a=cta]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'rot' and '3 done · 1 skipped' in pg.inner_text('#app .osec.folded'), 'Foundation folds to a line saying 3 done · 1 skipped')
    ring('nasal', 3)
    nb = '#app .rgi[data-rk="r:nasal"]'
    ok(until(pg, f"!!document.querySelector('{nb} .unfold.open')"), 'level 3 opens “How did it feel?”')
    pg.click(f'{nb} [data-a=rcue][data-v="Low notes clear"]')
    t.shot(pg, 'rotation')
    pg.click('[data-a=cta]'); pg.wait_for_timeout(200)
    pg.click('[data-a=apSong][data-k=g_1]'); pg.click('[data-a=apNoRec]'); pg.wait_for_timeout(100)
    pg.click('[data-a=rate][data-k=Pitch][data-v="2"]')
    t.shot(pg, 'application', full_page=True)
    pg.click('[data-a=cta]'); pg.wait_for_timeout(700)
    # Q20: finishing goes straight on, with no How did it go?
    ok(pg.evaluate("X") is None and pg.evaluate("U.sheet") is None and pg.evaluate("U.view") == 'saved', 'finishing saves straight away, with no How did it go?, onto Session saved (Q21)')
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss['how'] == [] and ss['howNote'] == '' and ss['rate'] == {'Pitch': 2} and ss['songName'] == 'Versace on the Floor · bridge', 'saved with its song and rating')
    ok(ss['f']['lip'] == 0, 'Skip is stored as 0')
    ok(cnt('lip') == lip0 and cnt('humming') == hum0 + 1, 'a skipped exercise is not counted as done')
    t.shot(pg, 'done', full_page=True)
    pg.click('[data-a=savedDone]'); until(pg, "U.view===null&&U.tab==='today'")
    pg.evaluate("U.sheet='session';U.sd={k:D.sessions[D.sessions.length-1].id};rerender()")  # its sheet, as from the calendar
    sh = pg.inner_text('.sheet')
    ok('Skipped' in sh and 'Lost the buzz, Nose tickle' in sh and 'Low notes clear' in sh and 'Versace on the Floor · bridge' in sh
       and 'Toggl' not in sh,
       "the session's sheet shows skips, notes and the song, with no Copy for Toggl (Q28)")

    # edit a finished session
    mk = now.strftime('%Y-%m'); m0 = pg.evaluate(f"D.months['{mk}']"); mins0 = ss['mins']
    pg.click('[data-a=editSess]'); pg.wait_for_timeout(600); t.shot(pg, 'edit', full_page=True)
    pg.fill('#edMins', '50'); pg.click('[data-a=eflv][data-k=lip][data-v="2"]')
    pg.click('.sheet [data-a=wTog][data-v="Bit tight"]')
    pg.click('[data-a=saveEdit]'); pg.wait_for_timeout(500)
    ss2 = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss2['mins'] == 50 and pg.evaluate(f"D.months['{mk}']") == m0 - mins0 + 50, 'editing minutes updates the month')
    ok(cnt('lip') == lip0 + 1 and ss2['how'] == ['Bit tight'], 'editing a level from Skip counts the exercise, and how it went can still be added')
    ok(pg.evaluate("U.sheet") == 'session', 'saving returns to the session')
    pg.click('[data-a=editSess]'); pg.wait_for_timeout(400)
    old = (now - dt.timedelta(days=40)).strftime('%Y-%m-%d'); pg.fill('#edDate', old); pg.click('[data-a=saveEdit]'); pg.wait_for_timeout(300)
    if old[:7] != mk:
        ok(pg.evaluate(f"D.months['{mk}']") == m0 - mins0, 'moving the date moves the minutes to that month')
    ok(pg.evaluate("D.ex.lip.last") < pg.evaluate("new Date().toISOString()"), 'last-done dates are recalculated')
    pg.click('.sheet .xbtn[data-a=close]'); pg.wait_for_timeout(300)

    # song practice, with the long-session check and a take note
    w0 = pg.evaluate("weekInfo().mins"); m1 = pg.evaluate(f"D.months['{mk}']||0")
    pg.click('[data-a=tab][data-v=today]'); pg.evaluate(SP); pg.wait_for_timeout(200)
    ok(pg.evaluate("X.kind") == 'song', 'song practice starts its own kind of session')
    pg.evaluate("X.start=Date.now()-125*60000;saveDraft()")
    pg.click('[data-a=song][data-k=g_1]')
    pg.evaluate("putTake({id:'tTest',songId:'g_1',created:Date.now(),len:42,size:20000,type:'audio/mp4',star:false,blob:new Blob([new Uint8Array(20000)],{type:'audio/mp4'})}).then(()=>{X.takes.push('tTest');saveDraft();return refreshTakes()}).then(rerender)")
    pg.wait_for_timeout(500); t.shot(pg, 'song', full_page=True)
    pg.click('[data-a=takeNote]'); pg.wait_for_timeout(500); pg.click('.sheet [data-a=wTog][data-v="Breathy"]'); pg.click('.sheet [data-a=openNote]'); pg.fill('#tnText', 'Ran out of air'); pg.click('.sheet .cta'); pg.wait_for_timeout(500)
    ok(pg.evaluate("allTakes().then(t=>t.find(x=>x.id==='tTest').note)") == {'w': ['Breathy'], 't': 'Ran out of air'}, 'take note saved')
    pg.click('[data-a=cta]'); pg.wait_for_timeout(600)
    ok(pg.evaluate("U.sheet") == 'long', 'over 90 minutes asks how long you practised'); t.shot(pg, 'long')
    pg.fill('#longMins', '30'); pg.click('[data-a=longOk]'); pg.wait_for_timeout(500)
    ok('30m' in pg.inner_text('.sheet .shtop'), 'How did it go? shows the corrected time')
    pg.click('.sheet [data-a=wTog][data-v="Breath ran short"]'); pg.click('[data-a=saveHow]'); pg.wait_for_timeout(600)
    so = pg.evaluate("D.songSessions[0]"); ok(so['mins'] == 30 and so['how'] == ['Breath ran short'], 'song practice saved with 30 minutes')
    ok(pg.evaluate("weekInfo().mins") == w0 and pg.evaluate(f"D.months['{mk}']||0") == m1, 'song practice leaves weekly and monthly minutes alone')
    ok('Toggl' not in pg.inner_text('.sheet') and 'Kept out of your focused goal and streak.' in pg.inner_text('.sheet'),
       "song practice's sheet has no Copy for Toggl or Toggl tag (Q28)")
    pg.click('.sheet .xbtn[data-a=close]'); pg.wait_for_timeout(300)
    # the session started 125 minutes ago: just after midnight on a Monday that's last week, so the card has no line
    this_wk = pg.evaluate("weekStart(new Date(D.songSessions[0].date)).getTime()===weekStart(new Date()).getTime()")
    ok(('This week · 1 session' in pg.inner_text('main')) == this_wk, 'the Song practice card shows its own stats' + ('' if this_wk else ' (started last week: none this week)'))

    # the same song practice from several doors
    pg.click('[data-a=tab][data-v=history]'); pg.wait_for_timeout(200)
    pg.click('[data-a=openAll][data-v=songs]'); pg.wait_for_timeout(300)
    ok(pg.locator('[data-v=songSession]').count() == 1, 'All sessions › Song practice lists it')
    pg.click('[data-a=allBack]'); pg.wait_for_timeout(200)
    pg.click('[data-a=tab][data-v=today]'); pg.click('[data-a=openCal]')
    pg.wait_for_selector('.cal')
    # Q18: it's dated when it started (125 minutes ago), so in the first two hours of a month it's in last month,
    # and the calendar opens on this one: go back a month first
    if pg.evaluate("(()=>{const d=new Date(D.songSessions[0].date),n=new Date();return d.getMonth()!==n.getMonth()})()"):
        pg.click('[data-a=calMove][data-v="-1"]')
    until(pg, "document.querySelectorAll('.cal button.s').length===1", timeout=3000)
    ok(pg.locator('.cal button.s').count() == 1, 'the calendar shows a coral dot for it')
    pg.click('.scrim .ghost'); pg.wait_for_timeout(300)
    pg.evaluate("U.view='ex';U.exId='humming';U.exTab='history';render()"); pg.wait_for_timeout(200)
    ok('Lost the buzz' in pg.inner_text('main'), "the exercise's History shows its note")
    pg.evaluate("U.view=null;U.tab='today';render()")

    # backup round trip in memory
    pg.evaluate("prepareExport()"); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    txt = pg.evaluate("pendingExport.file.text()"); data = json.loads(txt)
    ok(len(data['data']['songSessions']) == 1 and any(x.get('note') for x in data['takes']), 'a backup holds song practice and take notes')
    n_sess = len(data['data']['sessions'])
    pg.evaluate("U.sheet=null;rerender()")
    pg.evaluate("(async()=>{await clearTakes();D={v2:true};migrate();save();await refreshTakes();render();})()"); pg.wait_for_timeout(400)
    pg.evaluate("async t=>{pendingImport=await inspectBackup(t,'x.json');return restoreImport()}", txt); pg.wait_for_timeout(1200)
    ok(pg.evaluate("D.sessions.length") == n_sess and pg.evaluate("D.songSessions.length") == 1
       and pg.evaluate("TAKES.find(t=>t.id==='tTest').note.t") == 'Ran out of air', 'restoring brings everything back')

    # an unfinished session from 3.1 is upgraded
    pg.evaluate("d=>{localStorage.setItem('vocalDraft',JSON.stringify(d))}", OLD_DRAFT); pg.reload(); ready(pg)
    ok(pg.evaluate("X.kind") == 'focused' and pg.evaluate("Array.isArray(X.how)"), 'an unfinished session from 3.1 is upgraded')
    pg.click('[data-a=resume]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'found' and int(pg.inner_text('#timer').split('· ')[-1].split(':')[0]) >= 12, 'resuming keeps the original start time')
    pg.click('[data-a=exit]'); pg.click('[data-a=songStart]'); ok(pg.evaluate("U.view") != 'song', 'song practice is blocked while a session is open')

    # delete song practice
    pg.evaluate("U.sheet=null;U.prevTab='history';U.tab='history';U.view='all';U.histTab='songs';render()")
    pg.click('[data-v=songSession]'); pg.wait_for_timeout(400); pg.click('.sheet [data-v=delSongSess]'); pg.wait_for_timeout(300); pg.click('[data-a=delSongSess]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.songSessions.length") == 0, 'song practice can be deleted')

    pg.evaluate("U.view=null;U.tab='settings';render()"); pg.evaluate("scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(300)
    v = pg.evaluate("APP_VERSION")
    ft = pg.locator('main .setfoot'); ok(ft.count() == 1 and 'Vocal Sessions' in ft.inner_text() and v in ft.inner_text() and ft.locator('img').count() == 1, f'Settings ends with the app’s icon, name and version {v}')
