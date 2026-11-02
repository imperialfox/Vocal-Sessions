"""Q22 the session clock: one ring in three slices sized by the usual step lengths (median of the last 10, set times
until there are 3), the current slice filling with a tick at its usual move-on, logged steps filling their slice and
going over changing nothing, steps not reached showing ~N min; paused (breathing, grey numbers, Resume); finishing
from the clock into Session saved's own line with Done; opening from the pill and closing by ✕, the dimmed page,
Escape and a sideways swipe either way (follow, threshold, flick, spring back, scrolling and the slider winning);
the floating window's small ring and its pause button; the screen kept on (and let go, and failing quietly);
"Were you away?" (Take it out, Keep it, short gaps); Undo on Log; fixing a step time with hold and slide; surviving
a reload ("Session picked up"); tapping the big number (remembered); steady digits; Progress's split staying exact
after Undo, a time fix and Take it out; Song practice's one slice; motion on, Reduce Motion, and 390 and 375 in
light and dark. Synthetic data only."""
import time
import datetime as dt
from harness import sample, iso, until, now, SP

MOTION_ON = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"
REDUCE_ON = "try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}"
# a wake lock that counts (headless Chromium may have none)
WAKE = """(()=>{window.__wl={req:0,rel:0,held:0};Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request(){window.__wl.req++;window.__wl.held++;
  const l=new EventTarget();l.release=()=>{window.__wl.rel++;window.__wl.held--;l.dispatchEvent(new Event('release'));return Promise.resolve()};return Promise.resolve(l)}}})})()"""
NO_WAKE = "Object.defineProperty(navigator,'wakeLock',{configurable:true,value:undefined})"
REFUSE = "Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request(){window.__refused=(window.__refused||0)+1;return Promise.reject(new DOMException('no','NotAllowedError'))}}})"
WIDE = "document.documentElement.scrollWidth<=innerWidth+1"
OPEN = "!!document.querySelector('#layer .sck')&&U.clock"
SHUT = "!document.querySelector('#layer .sck')&&!U.clock"
TOAST = "t=>[...document.querySelectorAll('.toast')].some(x=>x.textContent.includes(t))"
# a session 37 minutes in: Foundation logged at 22 min, Rotation running
MID = """(()=>{newSession();X.start=Date.now()-37*60e3;X.f={slides:2,humming:3,lip:2,straw:3};X.fEnd=Date.now()-15*60e3;X.fE=22*60;
  saveDraft();go(()=>{U.tab='today';U.view='rot'})})()"""
# leaving the app notes when (in the draft), so a reload can't stand in for time away by itself: this puts the time
# away in the draft just before the next load, once
SEEN_INIT = """try{const s=sessionStorage.getItem('__seen');if(s){sessionStorage.removeItem('__seen');const d=JSON.parse(localStorage.getItem('vocalDraft'));
  d.seen=Date.now()-(+s)*60e3;localStorage.setItem('vocalDraft',JSON.stringify(d))}}catch(e){}"""
FILLS = "[...document.querySelectorAll('#sckRing .sf')].map(c=>[+c.dataset.i,+c.dataset.f])"
LENS = "[...document.querySelectorAll('#sckRing .sl')].map(c=>+c.getAttribute('stroke-dasharray').split(' ')[0])"


def sess(i, days, f, r, a):
    d = now - dt.timedelta(days=days)
    m = f + r + a
    return {"id": f"u{i}", "date": iso(d), "end": iso(d + dt.timedelta(minutes=m)), "mins": m, "f": {"slides": 2}, "fNote": "",
            "rot": {"rung": 2}, "rNote": "", "rotNames": {}, "songName": "", "rate": {}, "takes": [], "split": {"f": f, "r": r, "a": a}}


def usual_data():
    """Twelve sessions with step times (the oldest two very long, so only the last 10 count)."""
    d = sample()
    vals = [(60, 60, 60), (60, 60, 60)] + [(10 + i, 20 + i, 8) for i in range(10)]
    d['sessions'] = [sess(i, 40 - i, *v) for i, v in enumerate(vals)]
    d['lastBackup'] = iso(now)
    return d


def drag(pg, x0, y0, x1, y1, steps=12, ms=16, stamp=None, end=True):
    """A one-finger drag as a touchscreen sends it (stamp: ms between touches as the page sees them, for flicks)."""
    cdp = pg.context.new_cdp_session(pg)
    t0 = time.time()
    at = (lambda i: {'timestamp': t0 + i * stamp / 1000}) if stamp else (lambda i: {})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}], **at(0)})
    for i in range(1, steps + 1):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + (x1 - x0) * i / steps, 'y': y0 + (y1 - y0) * i / steps}], **at(i)})
        pg.wait_for_timeout(ms)
    if end:
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': [], **at(steps)})
        pg.wait_for_timeout(400)  # a tap straight after a swipe is the end of the swipe (as in test_window)
        cdp.detach()
        return None
    return cdp


def box(pg, sel):
    return pg.evaluate("s=>{const r=document.querySelector(s).getBoundingClientRect();return {l:r.left,t:r.top,w:r.width,h:r.height,r:r.right,b:r.bottom}}", sel)


def opened(pg):
    pg.click('#timer')
    return until(pg, OPEN)


def ring(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(MID)
    ok(opened(pg), 'the timer pill opens the clock')
    ok(pg.locator('#sckRing .sl').count() == 3, 'one ring, three slices')
    lens = pg.evaluate(LENS)
    ok(abs(lens[0] / lens[1] - 22 / 19) < 0.01 and abs(lens[1] / lens[2] - 19 / 14) < 0.01,
       f'with too few past sessions, the slices are sized by the set times 22 : 19 : 14 ({[round(x, 1) for x in lens]})')
    cols = pg.evaluate("[...document.querySelectorAll('#sckRing .sf')].map(c=>c.getAttribute('stroke'))")
    ok(cols == ['var(--cF)', 'var(--cR)'], f'the slices are in the step colours, Foundation and Rotation filled so far ({cols})')
    fills = dict(pg.evaluate(FILLS))
    ok(fills[0] == 1 and abs(fills[1] - 15 / 19) < 0.01, f'Foundation (logged) fills its slice, Rotation fills as time passes ({fills})')
    ok(pg.locator('#sckRing .scktk').count() == 1, 'a tick marks the usual move-on')
    ok(pg.inner_text('#sckSub') == 'Usual move-on ~19 min', 'with “Usual move-on ~19 min” under the ring')
    ok(pg.inner_text('#sckC b') == '37:00' and pg.inner_text('#sckC small').startswith('Rotation · 15:0'), 'the total, and the step with its time')
    rows = pg.evaluate("[...document.querySelectorAll('.sckrow')].map(r=>[r.querySelector('.sckn').textContent,r.querySelector('.sckt').textContent,r.style.getPropertyValue('--sc')])")
    ok(rows[0][:2] == ['Foundation', '22:00'] and rows[1][0] == 'Rotation' and rows[2][:2] == ['Application', '~14 min'],
       f'steps not reached show the usual time ({rows})')
    ok([r[2] for r in rows] == ['var(--cF)', 'var(--cR)', 'var(--cA)'], 'names and times in their slice’s colour')
    # a short logged step still fills its whole slice; going over changes nothing
    pg.evaluate("X.fE=60;X.start=Date.now()-60*60e3;SCLOCK.tick()")
    fills = dict(pg.evaluate(FILLS))
    ok(fills[0] == 1 and fills[1] == 1, f'a 1-minute Foundation still fills its slice; Rotation past its usual length is simply full ({fills})')
    ok(pg.evaluate("document.querySelector('#sckRing .sf[data-i=\"1\"]').getAttribute('stroke')") == 'var(--cR)'
       and 'over' not in pg.inner_text('#layer .sck').lower(), 'no colour change and no “over” label')
    ok(pg.inner_text('#sckSub') == 'Usual move-on ~19 min', 'and the line under the ring stays as it was')
    t.shot(pg, 'running')
    # usual lengths from recent sessions
    pg.context.close()
    pg = t.page(b, data=usual_data())
    u = pg.evaluate("SCLOCK.usual()")
    ok(u['f'] == 14.5 and u['r'] == 24.5 and u['a'] == 8, f'usual lengths: the median of the last 10 sessions with that step ({u})')
    ok(pg.evaluate("D.sessions.push({id:'mx',date:new Date().toISOString(),mins:5,mixed:true,f:{},rot:{}});SCLOCK.usual().f") == 14.5,
       'sessions filled in at the end (no split) don’t count')
    pg.context.close()


def paused(b, t):
    ok = t.ok
    pg = t.page(b, init=MOTION_ON)
    pg.evaluate(MID)
    opened(pg)
    until(pg, "!document.getAnimations().some(a=>a.playState==='running'&&a.effect.getTiming().iterations!==Infinity)", 3000)
    pg.click('.sck [data-a=pauseToggle]')
    ok(until(pg, "!!document.querySelector('.sck.paused')") and pg.evaluate("X.paused"), 'the clock’s pause button pauses')
    ok(pg.inner_text('#sckC small') == 'Paused · for 1 min' and pg.inner_text('#sckSub') == 'Paused time isn’t counted',
       '“Paused · for N min” in the centre, “Paused time isn’t counted” below')
    ok(pg.inner_text('.sck .sckmain') == 'Resume', 'the main button becomes Resume')
    grey = pg.evaluate("[getComputedStyle(document.querySelector('.sckbig')).color,getComputedStyle(document.querySelector('.sckrow.cur .sckt')).color,getComputedStyle(document.documentElement).getPropertyValue('--fg2')]")
    ok(grey[0] == grey[1] and grey[0] != pg.evaluate("getComputedStyle(document.querySelector('.scktl')).color"), f'the numbers go grey ({grey[:2]})')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.scksl')).animationName") == 'sckBreathe', 'the ring breathes')
    t.shot(pg, 'paused')
    e1 = pg.evaluate("elapsedSec()"); pg.wait_for_timeout(1100)
    ok(pg.evaluate("elapsedSec()") == e1, 'paused time isn’t counted')
    pg.click('.sck .sckmain')
    ok(until(pg, "!X.paused&&!document.querySelector('.sck.paused')") and pg.evaluate(OPEN), 'Resume carries on, with the clock still open')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.scksl')).animationName") == 'none', 'and the ring stops breathing')
    # digits never animate
    pg.wait_for_timeout(1100)
    ok(pg.evaluate("[...document.querySelectorAll('#sckC, #sckC *, .sckt, #timer')].every(e=>!e.getAnimations().length)"), 'timer digits never animate')
    pg.context.close()
    pg = t.page(b, init=REDUCE_ON)
    pg.evaluate(MID + ";togglePause()")
    opened(pg)
    ok(pg.evaluate("getComputedStyle(document.querySelector('.scksl')).animationName") == 'none', 'Reduce Motion: no breathing while paused')
    pg.context.close()


def steady(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(MID)
    opened(pg)
    f = pg.evaluate("['#timer','.sckbig','#sckC small','.sckrow.cur .sckt','.sckt.fixable'].map(s=>getComputedStyle(document.querySelector(s)).fontVariantNumeric)")
    ok(all('tabular-nums' in x for x in f), f'steady digits: tabular numbers on every clock figure ({f})')
    pg.click('.sck .circ[data-a=clockClose]'); until(pg, SHUT)
    pg.evaluate("go(()=>{U.tab='today';U.view=null})")
    until(pg, "FW.shown==='session'")
    ok('tabular-nums' in pg.evaluate("getComputedStyle(document.querySelector('#fw .fwt')).fontVariantNumeric"), 'and in the floating window')
    pg.context.close()


def swap(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(MID)
    opened(pg)
    pg.click('#sckC')
    ok(pg.inner_text('#sckC b').startswith('15:0') and pg.inner_text('#sckC small') == 'Total 37:00', 'tapping the big number swaps to the step’s time, with the total below')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalClock')).swap") is True, 'the choice is remembered on this device')
    pg.reload(); until(pg, "!document.getElementById('splash')")
    pg.evaluate("go(()=>{U.view='rot'})")
    opened(pg)
    ok(pg.inner_text('#sckC b').startswith('15:'), 'and after a reload')
    pg.click('#sckC')
    ok(pg.inner_text('#sckC b').startswith('37:'), 'tapping again swaps back')
    pg.context.close()


def open_close(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(MID)
    opened(pg)
    pg.click('.sck .circ[data-a=clockClose]')
    ok(until(pg, SHUT), '✕ closes it')
    opened(pg)
    pg.mouse.click(20, 800)
    ok(until(pg, SHUT), 'so does tapping the dimmed page')
    opened(pg)
    pg.keyboard.press('Escape')
    ok(until(pg, SHUT), 'and Escape')
    pg.context.close()
    # motion on: it zooms out of the pill and back into it
    pg = t.page(b, init=MOTION_ON + "try{localStorage.setItem('vocalMotion','4')}catch(e){}")
    pg.evaluate(MID)
    pill = box(pg, '#timer')
    pg.click('#timer')
    until(pg, OPEN)
    pg.wait_for_timeout(30)
    r = box(pg, '#layer .sck')
    cx, cy = r['l'] + r['w'] / 2, r['t'] + r['h'] / 2
    pc = (pill['l'] + pill['w'] / 2, pill['t'] + pill['h'] / 2)
    ok(r['w'] < 300 and abs(cx - pc[0]) < 120 and abs(cy - pc[1]) < 200, f'it starts small, out of the pill ({round(r["w"])} px wide)')
    ok(until(pg, "document.querySelector('#layer .sck').getAnimations().length===0", 8000), 'and grows to its place')
    full = box(pg, '#layer .sck')
    ok(full['w'] > 330, 'full size once open')
    pg.click('.sck .circ[data-a=clockClose]')
    ok(until(pg, SHUT, 1000) and pg.evaluate("!!document.elementFromPoint(20,800).closest('#app')"),
       'closing, the clock is closed at once: the page underneath can be tapped straight away')
    pg.wait_for_timeout(500)
    r = box(pg, '.sck.sckghost') if pg.locator('.sck.sckghost').count() else None
    ok(r is not None and r['w'] < full['w'] - 20 and r['t'] + r['h'] / 2 < full['t'] + full['h'] / 2, 'while a still copy shrinks back towards the pill')
    t.shot(pg, 'closing')
    ok(until(pg, "!document.querySelector('.sckghost')", 8000), 'then it’s gone')
    pg.context.close()
    # Reduce Motion: fades
    pg = t.page(b, init=REDUCE_ON)
    pg.evaluate(MID)
    pg.click('#timer'); until(pg, OPEN)
    k = pg.evaluate("document.querySelector('#layer .sck').getAnimations().map(a=>Object.keys(a.effect.getKeyframes()[0]).filter(x=>!['offset','easing','composite','computedOffset'].includes(x)).join())")
    ok(k and all(x == 'opacity' for x in k), f'Reduce Motion: it fades in ({k})')
    pg.click('.sck .circ[data-a=clockClose]')
    pg.wait_for_timeout(60)
    k = pg.evaluate("(()=>{const e=document.querySelector('.sck.sckghost');return e?e.getAnimations().map(a=>Object.keys(a.effect.getKeyframes()[0]).filter(x=>!['offset','easing','composite','computedOffset'].includes(x)).join()):['gone']})()")
    ok(all(x in ('opacity', 'gone') for x in k), f'and fades out ({k})')
    ok(until(pg, SHUT), 'then it’s gone')
    pg.context.close()


def swipe(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate(MID)
    for d, name in [(1, 'right'), (-1, 'left')]:
        opened(pg)
        r = box(pg, '#layer .sck')
        y = r['t'] + 260
        drag(pg, r['l'] + r['w'] / 2, y, r['l'] + r['w'] / 2 + d * r['w'] * 0.32, y + 6)
        ok(until(pg, SHUT), f'swiping {name} past a fifth of its width closes it')
    opened(pg)
    r = box(pg, '#layer .sck')
    x0, y = r['l'] + r['w'] / 2, r['t'] + 260
    cdp = drag(pg, x0, y, x0 + 70, y + 4, end=False)
    m = box(pg, '#layer .sck')
    ok(pg.evaluate("SCLOCK.state().swiping") and m['l'] > r['l'] + 40 and m['w'] < r['w'], 'mid-swipe it follows the finger and shrinks towards the pill')
    t.shot(pg, 'mid-swipe')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + 30, 'y': y + 4}]})
    pg.wait_for_timeout(30)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); cdp.detach()
    ok(until(pg, "(()=>{const e=document.querySelector('#layer .sck');return !!e&&!e.style.transform})()") and pg.evaluate(OPEN),
       'let go short of a fifth: it springs back and stays open')
    drag(pg, x0, y, x0 - 50, y, steps=4, stamp=16)
    ok(until(pg, SHUT), 'a quick flick closes it')
    opened(pg)
    drag(pg, x0, r['t'] + 400, x0 + 12, r['t'] + 200)
    ok(pg.evaluate(OPEN), 'a scroll up and down the clock isn’t a swipe')
    # the step-time slider beats the swipe
    pg.click('.sck [data-a=sckFix][data-k="0"]')
    until(pg, "!!document.getElementById('sckSlider')")
    s = box(pg, '#sckSlider')
    v0 = pg.evaluate("SCLOCK.state().fix.v")
    drag(pg, s['l'] + s['w'] * 0.45, s['t'] + s['h'] / 2, s['l'] + s['w'] * 0.1, s['t'] + s['h'] / 2)
    ok(pg.evaluate(OPEN) and pg.evaluate("SCLOCK.state().fix.v") < v0, 'sliding the step time moves the slider, not the clock')
    pg.context.close()


def finish(b, t):
    ok = t.ok
    for init, tag in [(None, ''), (MOTION_ON, 'motion on: ')]:
        pg = t.page(b, init=init)
        pg.evaluate("(()=>{newSession();X.start=Date.now()-41*60e3;X.f={slides:2,humming:3,lip:2,straw:3};X.fEnd=Date.now()-25*60e3;X.fE=16*60;"
                    "X.rot={rung:2};X.rEnd=Date.now()-6*60e3;X.rE=35*60;saveDraft();go(()=>{U.tab='today';U.view='app'})})()")
        opened(pg)
        ok(pg.inner_text('.sck .sckmain') == pg.inner_text('#dock [data-a=cta]'), tag + 'the main button is the pinned button: ' + pg.inner_text('.sck .sckmain'))
        pg.click('.sck .sckmain')
        ok(until(pg, "U.view==='saved'&&!!document.querySelector('.sck.fin')"), tag + 'finishing from the clock saves the session and keeps the clock')
        line = pg.inner_text('#app .svd-line')
        ok(pg.inner_text('#sckSub') == line and line.startswith('41 min · '), tag + f'the ring settles into Session saved’s own line ({line})')
        ok(pg.inner_text('#sckC b') == '41 min' and pg.locator('.sck [data-a=sckDone]').count() == 1, tag + 'with the minutes in the centre and Done just below')
        ok(until(pg, "[...document.querySelectorAll('#sckRing .sf')].length===3&&[...document.querySelectorAll('#sckRing .sf')].every(c=>c.dataset.f==='1.000')"),
           tag + 'the ring closes: every slice full')
        if init:
            pg.wait_for_timeout(1500)
            t.shot(pg, 'finished')
        pg.click('.sck [data-a=sckDone]')
        ok(until(pg, "U.view===null&&U.tab==='today'&&!U.clock&&!document.querySelector('#layer .sck')"), tag + 'Done goes on to Today')
        ok(until(pg, "!document.querySelector('.sckghost')"), tag + 'nothing left behind')
        pg.context.close()
    # the long-session check still asks first
    pg = t.page(b)
    pg.evaluate("(()=>{newSession();X.start=Date.now()-100*60e3;X.f={slides:2,humming:3,lip:2,straw:3};X.fEnd=Date.now()-60*60e3;X.fE=40*60;"
                "X.rEnd=Date.now()-30*60e3;X.rE=70*60;saveDraft();go(()=>{U.tab='today';U.view='app'})})()")
    opened(pg)
    pg.click('.sck .sckmain')
    ok(until(pg, "U.sheet==='long'") and not pg.evaluate("U.clock"), 'over 90 minutes, the long-session check comes first, as from the pinned button')
    pg.context.close()


def undo(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate("(()=>{newSession();X.start=Date.now()-20*60e3;X.f={slides:2,humming:3,lip:2,straw:3};saveDraft();go(()=>{U.tab='today';U.view='found'})})()")
    pg.click('#dock [data-a=cta]')
    ok(until(pg, "U.view==='rot'") and until(pg, TOAST, arg='Foundation logged'), 'Log foundation shows an Undo toast')
    pg.click('.toast .ckub')
    ok(until(pg, "U.view==='found'") and pg.evaluate("X.fEnd===null&&X.fE===null"), 'Undo goes back to Foundation with its end cleared')
    pg.wait_for_timeout(1000)
    pg.click('#dock [data-a=cta]')
    until(pg, "U.view==='rot'")
    fE = pg.evaluate("X.fE")
    ok(abs(fE - pg.evaluate("elapsedSec()")) < 1, 'logging again stamps the new end')
    ok(until(pg, "![...document.querySelectorAll('.toast')].some(x=>x.textContent.includes('Foundation logged'))", 8000), 'the toast goes after about 5 s')
    pg.evaluate("X.start-=4*60e3;saveDraft()")  # Rotation has run 4 minutes (under 2 counts as filled in afterwards)
    # from the clock: Log rotation, Undo, the clock still open on Rotation
    opened(pg)
    pg.click('.sck .sckmain')
    ok(until(pg, "U.view==='app'") and pg.evaluate(OPEN), 'Skip rotation from the clock: the clock stays open on Application')
    ok(until(pg, TOAST, arg='Rotation skipped'), 'with its Undo toast')
    pg.click('.toast .ckub')
    ok(until(pg, "U.view==='rot'") and pg.evaluate("X.rEnd===null&&X.rE===null&&X.fE") == fE and pg.evaluate(OPEN),
       'Undo: back on Rotation, Foundation’s end untouched, the clock still open')
    # an Undo that's out of date does nothing
    pg.evaluate("X.rot={rung:2};OP.dockUpd()")
    pg.click('.sck .sckmain'); until(pg, "U.view==='app'")
    pg.evaluate("X.rE=X.rE-1;saveDraft()")
    pg.click('.toast .ckub')
    pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'app' and pg.evaluate("X.rEnd") is not None, 'an Undo after something else has changed the times does nothing')
    # the split, after an Undo: exactly from the stamps
    st = pg.evaluate("[X.fE,X.rE,elapsedSec()]")
    pg.click('.sck .circ[data-a=clockClose]'); until(pg, SHUT)
    pg.evaluate("startFinish()"); until(pg, "U.view==='saved'")
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    e = max(1, st[2]); sc = ss['mins'] * 60 / e
    exp = {'f': round(st[0] * sc / 6) / 10, 'r': round((st[1] - st[0]) * sc / 6) / 10}
    ok(abs(ss['split']['f'] - exp['f']) <= 0.1 and abs(ss['split']['r'] - exp['r']) <= 0.1, f'Progress’s split is from the stamps as they ended up ({ss["split"]} vs {exp})')
    ok(not pg.evaluate("[...document.querySelectorAll('.toast .ckub')].length"), 'and finishing takes away a Log’s Undo')
    pg.context.close()


def fix(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(MID)
    opened(pg)
    ok(pg.locator('.sck [data-a=sckFix]').count() == 1, 'only a finished step’s time can be fixed')
    pg.click('.sck [data-a=sckFix][data-k="0"]')
    ok(until(pg, "!!document.getElementById('sckSlider')"), 'tapping Foundation’s time opens hold and slide')
    ok('Logged 22 min' in pg.inner_text('.sckfix') and pg.inner_text('#sckFixV') == '22 min', 'showing what was logged')
    t.shot(pg, 'fix')
    s = box(pg, '#sckSlider')
    pg.mouse.move(s['l'] + s['w'] * 0.5, s['t'] + s['h'] / 2); pg.mouse.down()
    st = pg.evaluate("SCLOCK.state().fix")
    tgt = 15
    x = s['l'] + 14 + (s['w'] - 28) * (tgt - st['min']) / (st['max'] - st['min'])
    pg.mouse.move(x, s['t'] + s['h'] / 2, steps=8); pg.mouse.up()
    ok(pg.evaluate("SCLOCK.state().fix.v") == tgt and pg.inner_text('#sckFixV') == '15 min', 'holding and sliding sets 15 min')
    ok(pg.inner_text('.sck [data-a=sckFix][data-k="0"]') == '15:00', 'the row shows the new time as it slides')
    pg.focus('#sckSlider'); pg.keyboard.press('ArrowRight'); pg.keyboard.press('ArrowLeft'); pg.keyboard.press('ArrowLeft')
    ok(pg.evaluate("SCLOCK.state().fix.v") == 14, 'the arrow keys move it a minute at a time')
    before = pg.evaluate("[X.fE,X.rE,elapsedSec()-X.fE,elapsedSec()]")
    pg.click('.sck [data-a=sckFixSave]')
    after = pg.evaluate("[X.fE,X.rE,elapsedSec()-X.fE,elapsedSec()]")
    ok(after[0] == 14 * 60 and abs(after[2] - before[2]) < 1.5 and abs((before[3] - after[3]) - 8 * 60) < 1.5,
       f'Save time: Foundation is 14 min, Rotation keeps its own time, the total is 8 min less ({[round(x) if x else x for x in after]})')
    ok(pg.inner_text('.sckrow .sckt') == '14:00' and not pg.evaluate("SCLOCK.state().fix"), 'the clock shows it')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalDraft')).fE") == 14 * 60, 'and it’s saved in the draft')
    # Rotation fixed after it's logged; the split follows exactly
    pg.evaluate("X.rot={rung:2};OP.dockUpd()")
    pg.click('.sck .sckmain'); until(pg, "U.view==='app'")
    pg.click('.sck [data-a=sckFix][data-k="1"]'); until(pg, "!!document.getElementById('sckSlider')")
    pg.evaluate("(()=>{const s=document.getElementById('sckSlider');s.focus()})()")
    v = pg.evaluate("SCLOCK.state().fix.v")
    for _ in range(3): pg.keyboard.press('ArrowRight')
    pg.click('.sck [data-a=sckFixSave]')
    st = pg.evaluate("[X.fE,X.rE,elapsedSec()]")
    ok(st[0] == 14 * 60 and abs((st[1] - st[0]) - (v + 3) * 60) < 1, 'Rotation’s time can be fixed too (longer), Foundation untouched')
    pg.click('.sck .circ[data-a=clockClose]'); until(pg, SHUT)
    pg.evaluate("startFinish()"); until(pg, "U.view==='saved'")
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    sc = ss['mins'] * 60 / st[2]
    ok(abs(ss['split']['f'] - round(14 * 60 * sc / 6) / 10) <= 0.1 and abs(ss['split']['r'] - round((v + 3) * 60 * sc / 6) / 10) <= 0.1,
       f'Progress’s split uses the fixed times ({ss["split"]}, {ss["mins"]} min)')
    pg.context.close()


def window(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(MID)
    pg.evaluate("go(()=>{U.tab='today';U.view=null})")
    ok(until(pg, "FW.shown==='session'"), 'leaving the session shows the floating window')
    ok(pg.locator('#fw .fwring svg .sl').count() == 3 and pg.locator('#fw .fwring .sf').count() == 2, 'with the same ring, small')
    ok(pg.inner_text('#fw .fwkn') == 'Rotation' and pg.inner_text('#fw .fwt').startswith('15:0'), 'beside “Rotation” and its time below (Q26)')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#fw .fwdot')).getPropertyValue('background-color')") ==
       pg.evaluate("getComputedStyle(document.querySelector('#fw .fwring .sf[data-i=\"1\"]')).getPropertyValue('stroke')"),
       'Q26: the dot before the step in its slice’s colour')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#fw .fwkn')).color") == pg.evaluate("getComputedStyle(document.body).color"),
       'Q26: the step’s name in the text colour')
    t.shot(pg, 'window')
    pg.click('#fw [data-a=fwToggle]')
    ok(until(pg, "X.paused") and pg.evaluate("U.view") is None and pg.locator('#fw [data-a=fwToggle][aria-label=Play]').count() == 1,
       'its button pauses, staying on Today')
    pg.click('#fw [data-a=fwToggle]')
    ok(until(pg, "!X.paused"), 'and carries on')
    pg.click('#fw .fwopen')
    ok(until(pg, "U.view==='rot'"), 'tapping the rest opens the session')
    pg.context.close()


def wake(b, t):
    ok = t.ok
    pg = t.page(b, init=WAKE)
    pg.click('[data-a=start]')
    ok(until(pg, "window.__wl.held===1"), 'starting a session keeps the screen on')
    ok(until(pg, TOAST, arg='Screen stays on'), 'with a brief “Screen stays on” chip')
    pg.evaluate("togglePause();rerender()")
    ok(until(pg, "window.__wl.held===0"), 'pausing lets it go')
    pg.evaluate("document.querySelectorAll('.toast').forEach(x=>x.remove());togglePause();rerender()")
    ok(until(pg, "window.__wl.held===1") and until(pg, TOAST, arg='Screen stays on'), 'Resume keeps it on again, with the chip')
    # the app hidden: iOS lets the lock go; back on screen it's asked for again
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
    ok(until(pg, "window.__wl.held===0"), 'hidden: no lock')
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
    ok(until(pg, "window.__wl.held===1"), 'back on screen: kept on again')
    # Song Clock's Stay awake shares the one lock
    pg.evaluate("AWAKE.set('ck',true)")
    pg.wait_for_timeout(100)
    ok(pg.evaluate("window.__wl.held") == 1, 'Song Clock wanting it too doesn’t ask twice')
    pg.evaluate("AWAKE.set('ck',false)")
    pg.wait_for_timeout(100)
    ok(pg.evaluate("window.__wl.held") == 1, 'and letting go of it leaves the session’s')
    pg.evaluate("X.fEnd=Date.now();X.fE=elapsedSec();X.rEnd=Date.now();X.rE=elapsedSec();saveDraft();go(()=>{U.view='app'})")
    pg.evaluate("startFinish()")
    ok(until(pg, "U.view==='saved'") and until(pg, "window.__wl.held===0"), 'finishing lets it go')
    pg.context.close()
    for js, name in [(NO_WAKE, 'no Wake Lock'), (REFUSE, 'a refused Wake Lock')]:
        pg = t.page(b, init=js)
        pg.click('[data-a=start]')
        pg.wait_for_timeout(400)
        ok(pg.evaluate("!!X&&!!X.start") and not pg.evaluate(TOAST, 'Screen stays on'), f'{name}: the session runs, with no chip and no error')
        pg.context.close()


def back_after(pg, mins):
    pg.evaluate("m=>sessionStorage.setItem('__seen',m)", mins)
    pg.reload(); until(pg, "!document.getElementById('splash')")


def away(b, t):
    ok = t.ok
    pg = t.page(b, init=SEEN_INIT)
    pg.evaluate(MID + ";X.start-=40*60e3;saveDraft()")  # Rotation has run 55 minutes
    back_after(pg, 25)
    ok(until(pg, TOAST, arg='Session picked up'), 'reopening the app carries on: “Session picked up”')
    ok(pg.evaluate("U.view===null&&X.fE===22*60&&X.fEnd>0"), 'with the steps kept')
    ok(until(pg, "U.sheet==='away'"), 'after 25 min away it asks')
    ok(pg.inner_text('#layer .sheet h2') == 'You were away 25 min' and pg.locator('[data-a=awayOut]').inner_text() == 'Take it out'
       and pg.locator('[data-a=awayKeep]').inner_text() == 'Keep it, I was singing', '“You were away 25 min”: Take it out / Keep it, I was singing')
    t.shot(pg, 'away')
    e0 = pg.evaluate("elapsedSec()")
    pg.click('[data-a=awayOut]')
    e1 = pg.evaluate("elapsedSec()")
    ok(not pg.evaluate("U.sheet") and abs((e0 - e1) - 25 * 60) < 3 and pg.evaluate("X.fE") == 22 * 60,
       f'Take it out: 25 min less, all of it from the step that was running ({round((e0 - e1) / 60, 1)} min)')
    # Keep it changes nothing
    back_after(pg, 12)
    until(pg, "U.sheet==='away'")
    e0 = pg.evaluate("elapsedSec()")
    pg.click('[data-a=awayKeep]')
    ok(not pg.evaluate("U.sheet") and abs(pg.evaluate("elapsedSec()") - e0) < 2, 'Keep it: the time stays')
    # a short gap just carries on; a paused session isn't asked about
    back_after(pg, 6)
    until(pg, TOAST, arg='Session picked up')
    pg.wait_for_timeout(500)
    ok(pg.evaluate("U.sheet") is None, 'under 10 minutes away, it just carries on')
    pg.evaluate("togglePause()")
    back_after(pg, 40)
    pg.wait_for_timeout(800)
    ok(pg.evaluate("U.sheet") is None, 'paused, it doesn’t ask (paused time isn’t counted anyway)')
    pg.evaluate("togglePause()")
    # leaving the app and coming back (no reload): the time away is noted, and asked about
    pg.evaluate("X.start-=30*60e3;saveDraft()")
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
    ok(abs(pg.evaluate("JSON.parse(localStorage.getItem('vocalDraft')).seen") - pg.evaluate("Date.now()")) < 2000, 'leaving the app notes when, in the draft')
    pg.evaluate("X.seen=Date.now()-15*60e3;Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
    ok(until(pg, "U.sheet==='away'") and 'away 15 min' in pg.inner_text('#layer .sheet h2'), 'coming back after 15 min asks')
    # a step logged after coming back, then Take it out: that step's end moves with it
    pg.evaluate("go(()=>{U.view='rot'})")
    pg.evaluate("X.rot={rung:2};OP.dockUpd()")
    st = pg.evaluate("[X.fE,elapsedSec()]")
    pg.evaluate("OP.advance()")
    until(pg, "U.view==='app'")
    rE0 = pg.evaluate("X.rE")
    pg.evaluate("U.sheet='away';rerender()")
    pg.click('[data-a=awayOut]')
    ok(pg.evaluate("X.fE") == st[0] and abs(pg.evaluate("X.rE") - (rE0 - 15 * 60)) < 2, 'a step logged since coming back keeps the time out of its own length')
    pg.context.close()
    # never more than the step that was running has had
    pg = t.page(b, init=SEEN_INIT)
    pg.evaluate(MID)
    back_after(pg, 30)
    until(pg, "U.sheet==='away'")
    e0 = pg.evaluate("elapsedSec()")
    pg.click('[data-a=awayOut]')
    e1 = pg.evaluate("elapsedSec()")
    ok(abs((e0 - e1) - 15 * 60) < 3 and pg.evaluate("X.fE") == 22 * 60, f'Take it out never takes more than the running step had (15 of 30 min: {round((e0 - e1) / 60, 1)})')
    pg.context.close()


def song(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(SP)
    pg.evaluate("X.song='g_1';X.start=Date.now()-5*60e3;saveDraft();rerender()")
    opened(pg)
    ok(pg.locator('#sckRing .sl').count() == 1 and pg.locator('#sckRing .scktk').count() == 0, 'Song practice: one slice round the ring, no tick')
    ok(pg.inner_text('#sckSub').startswith('Started at') and pg.inner_text('.sck .sckmain') == 'Save song practice', 'its own line and button')
    ok(pg.locator('.sck [data-a=sckFix]').count() == 0, 'nothing to fix')
    pg.context.close()


def screens(b, t):
    ok = t.ok
    for w, h in [(390, 844), (375, 667)]:
        for sc in ['light', 'dark']:
            tag = f'{w} {sc}'
            pg = t.page(b, w=w, h=h, sc=sc)
            pg.evaluate(MID)
            opened(pg)
            r = box(pg, '#layer .sck')
            ok(pg.evaluate(WIDE) and r['l'] >= 0 and r['r'] <= w and r['t'] >= 0 and r['b'] <= h, f'{tag}: the clock fits, no sideways scroll')
            t.shot(pg, f'{w}-{sc}-running')
            pg.click('.sck [data-a=pauseToggle]'); until(pg, "!!document.querySelector('.sck.paused')")
            t.shot(pg, f'{w}-{sc}-paused')
            pg.click('.sck .sckmain'); until(pg, "!X.paused")
            pg.click('.sck [data-a=sckFix][data-k="0"]'); until(pg, "!!document.getElementById('sckSlider')")
            r = box(pg, '.sck .sckmain')
            ok(pg.evaluate(WIDE) and pg.evaluate("(()=>{const e=document.querySelector('#layer .sck');return e.scrollHeight<=e.clientHeight+1||getComputedStyle(e).overflowY==='auto'})()"),
               f'{tag}: with a time open, it still fits (or scrolls inside itself)')
            pg.click('.sck .circ[data-a=clockClose]'); until(pg, SHUT)
            pg.evaluate("go(()=>{U.tab='today';U.view=null})"); until(pg, "FW.shown==='session'")
            f = box(pg, '#fw')
            ok(f['l'] >= 0 and f['r'] <= w and pg.evaluate(WIDE), f'{tag}: the floating window fits')
            t.shot(pg, f'{w}-{sc}-window')
            pg.context.close()


def run(b, t):
    print('-- the ring'); ring(b, t)
    print('-- paused'); paused(b, t)
    print('-- steady digits'); steady(b, t)
    print('-- tap the big number'); swap(b, t)
    print('-- opening and closing'); open_close(b, t)
    print('-- swipe'); swipe(b, t)
    print('-- finish'); finish(b, t)
    print('-- undo'); undo(b, t)
    print('-- fix a step time'); fix(b, t)
    print('-- floating window'); window(b, t)
    print('-- screen stays on'); wake(b, t)
    print('-- away and picked up'); away(b, t)
    print('-- song practice'); song(b, t)
    print('-- screens'); screens(b, t)
