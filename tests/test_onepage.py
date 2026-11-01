"""Q19 the one-page session: Foundation, Rotation and Application on one page. Tapping a row through its levels, level
3's sweep and "How did it feel?", levels 1 and 2's "What kept it at level N?" after a short settle, a picked word
folding the row and nudging the next, the pinned button recording each step's end as before (so Progress's split is
the same for the same times), pulling past the bottom, reopening a finished step and never jumping ahead, Skip
rotation and "Just Foundation today? Finish here", More exercises' sort, a 3.31 draft resuming, Reduce Motion, and
the page at 390 and 375 in light and dark. Synthetic data only."""
import json, time
from harness import fix, until
from test_window import drag

FIXT = json.load(open(fix('draft-3.31.json')))
WIDE = "document.documentElement.scrollWidth<=innerWidth+1"
ACTIVE = '#app .osec.active'
ROW = lambda s, k: f'#app .osec:not(.preview) .rgi[data-rk="{s}:{k}"]'
OPEN = lambda s, k: f"!!document.querySelector('{ROW(s, k)} .unfold.open')"
MOTION_ON = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"


def draft(pg, name, mins_ago=40):
    """Put a 3.31 draft in place, moved so it started mins_ago minutes ago, and reload."""
    d = dict(FIXT[name])
    shift = int(time.time() * 1000) - mins_ago * 60000 - d['start']
    for k in ('start', 'fEnd', 'rEnd'):
        if d.get(k): d[k] += shift
    pg.evaluate("d=>localStorage.setItem('vocalDraft',JSON.stringify(d))", d)
    pg.reload()
    pg.wait_for_function("!document.getElementById('splash')&&!LAUNCH.busy()", timeout=15000)
    pg.wait_for_timeout(150)


def tap(pg, s, k, n=1):
    for _ in range(n): pg.click(f'{ROW(s, k)} [data-a=ring]')


def cta(pg): return pg.inner_text('#dock [data-a=cta]').strip()


def levels(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.click('[data-a=start]'); pg.wait_for_timeout(200)
    ok(pg.locator('#app .osec').count() == 2 and pg.locator('#app .osec.active h1').inner_text() == 'Foundation'
       and pg.locator('#app .osec.preview h1').inner_text() == 'Rotation', 'one page: Foundation, with Rotation faded underneath')
    ok(pg.evaluate("U.view") == 'found' and cta(pg) == 'Log foundation' and 'opwait' in pg.get_attribute('#dock [data-a=cta]', 'class'),
       'one pinned button, Log foundation, waiting')
    ok('0 of 4 set' in pg.inner_text('#opHint'), 'its hint counts what’s set')
    txt = pg.inner_text('#app') + pg.inner_text('#dock')
    ok('SOVT' not in txt and 'Foundation' in txt, 'it says Foundation, never SOVT')
    # Foundation: 1 → 2 → 3 → Skip → 1
    seen = []
    for i in range(5):
        tap(pg, 'f', 'slides')
        seen.append([pg.evaluate("X.f.slides"), pg.text_content(f"{ROW('f', 'slides')} .ring text"), pg.inner_text(f"{ROW('f', 'slides')} small")])
    ok([x[0] for x in seen] == [1, 2, 3, 0, 1] and [x[1] for x in seen] == ['1', '2', '3', 'Skip', '1'],
       'tapping a Foundation row cycles 1 → 2 → 3 → Skip → 1: ' + json.dumps(seen))
    ok(seen[3][2] == 'Skipped' and seen[0][2].startswith('Level 1'), 'its line says the level, or Skipped')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalDraft')).f.slides") == 1, 'each tap is saved on the draft')
    off = pg.evaluate(f"getComputedStyle(document.querySelector('{ROW('f', 'slides')} .arc')).strokeDashoffset")
    ok(abs(float(off.replace('px', '')) - 100.53 * 2 / 3) < 0.5, 'the ring is a third full at level 1')
    # level 1: the box waits a moment, then asks what kept it there
    ok(not pg.evaluate(OPEN('f', 'slides')), 'level 1’s box waits for the settle')
    ok(until(pg, OPEN('f', 'slides'), timeout=3000), 'then “What kept it at level 1?” opens')
    box = pg.inner_text(f"{ROW('f', 'slides')} .cuebox")
    ok('What kept it at level 1?' in box and all(w in box for w in ['Cracked going up', 'Still warming up', 'Voice felt tired', 'Short on time', 'Kept it easy today', '+ Your own']),
       'with the exercise’s reasons, the shared ones and + Your own')
    t.shot(pg, 'reasons')
    # a reason folds the row and nudges the next exercise
    pg.click(f"{ROW('f', 'slides')} [data-a=rcue][data-v='Still warming up']")
    ok(pg.evaluate("X.xn.slides") == {'w': ['Still warming up'], 't': ''}, 'the reason is saved as the exercise’s note')
    ok(until(pg, f"document.querySelector('{ROW('f', 'slides')}').classList.contains('folded')", timeout=3000), 'then the row folds to one faded line')
    ok('Level 1 · Still warming up' in pg.inner_text(f"{ROW('f', 'slides')} small") and not pg.evaluate(OPEN('f', 'slides')), 'saying its level and reason')
    ok(until(pg, f"document.querySelector('{ROW('f', 'humming')}').classList.contains('rnudge')", timeout=3000), 'and the next exercise gets a nudge')
    t.shot(pg, 'folded')
    tap(pg, 'f', 'slides')
    ok(pg.evaluate("X.f.slides") == 1 and pg.evaluate(OPEN('f', 'slides')), 'tapping a folded row opens its box again, keeping the level')
    # level 3: green, and "How did it feel?" at once (motion off)
    tap(pg, 'f', 'humming', 3)
    ok(until(pg, OPEN('f', 'humming'), timeout=3000) and 'How did it feel?' in pg.inner_text(f"{ROW('f', 'humming')} .cuebox"),
       'level 3 opens “How did it feel?”')
    ok(all(w in pg.inner_text(f"{ROW('f', 'humming')} .cuebox") for w in pg.evaluate("EX_WORDS.humming")), 'with the exercise’s own words')
    ok(pg.evaluate(f"document.querySelector('{ROW('f', 'humming')}').classList.contains('peak')"), 'its ring and line turn green')
    t.shot(pg, 'level3')
    # + Your own
    pg.click(f"{ROW('f', 'humming')} [data-a=rown]"); pg.fill(f"{ROW('f', 'humming')} .ownin", 'Felt it in my nose'); pg.keyboard.press('Enter')
    ok(until(pg, "(X.xn.humming||{w:[]}).w.includes('Felt it in my nose')") and 'Felt it in my nose' in pg.evaluate("D.words.x_humming"),
       '+ Your own adds a word, kept for next time')
    # missing: the button says so and points at it
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'found' and 'Set a level or Skip for each exercise' in pg.inner_text('.toast'), 'Log foundation with exercises unset says so')
    ok(pg.evaluate(f"document.querySelector('{ROW('f', 'lip')}').classList.contains('rneed')"), 'and flashes what’s missing')
    tap(pg, 'f', 'lip', 4); tap(pg, 'f', 'straw', 2)
    ok('tinted' in pg.get_attribute('#dock [data-a=cta]', 'class') and 'Next: Rotation' in pg.inner_text('#opHint'), 'all set: the button is ready, Next: Rotation')
    # no jumping ahead
    ok(pg.evaluate("(()=>{const p=document.querySelector('#app .osec.preview');return p.inert&&getComputedStyle(p).pointerEvents==='none'})()"),
       'the faded Rotation can’t be tapped')
    pg.evaluate("OP.reopen(1);OP.reopen(2)"); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.view") == 'found' and pg.evaluate("U.fEdit") is None, 'and nothing opens a later step')
    # Log foundation: stamped as before, Foundation folds, Rotation comes up
    e0 = pg.evaluate("elapsedSec()")
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.view") == 'rot' and abs(pg.evaluate("X.fE") - e0) < 1.5 and pg.evaluate("X.fEnd>0"),
       'Log foundation records Foundation’s end at the tap (fEnd and fE), as before')
    ok(pg.locator('#app .osec.folded').count() == 1 and '3 done · 1 skipped' in pg.inner_text('#app .osec.folded'), 'Foundation folds to a line: 3 done · 1 skipped')
    ok(pg.evaluate("scrollY") == 0 and pg.locator('#app .osec.active h1').inner_text() == 'Rotation', 'Rotation is the open step, at the top')
    pg.context.close()


def rotation(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.click('[data-a=start]'); pg.wait_for_timeout(150)
    pg.evaluate("FOUND.forEach(e=>X.f[e.id]=2);saveDraft();OP.advance()"); pg.wait_for_timeout(200)
    sug = pg.evaluate("suggested().id")
    ok(pg.locator(f"{ROW('r', sug)}.big .eyebrow").inner_text().lower() == 'suggested', 'the suggested exercise is a card on top')
    hd = ' '.join(pg.text_content('#app .sorthdr').replace('\xa0', ' ').split())
    ok(hd == 'More exercises · Longest ago', 'then More exercises · Longest ago: ' + hd)
    ok(cta(pg) == 'Skip rotation' and pg.locator('#dock [data-a=finHere]').inner_text() == 'Just Foundation today? Finish here',
       'with nothing picked: Skip rotation, and Just Foundation today? Finish here')
    # Rotation: + → 1 → 2 → 3 → off
    seen = []
    for i in range(4):
        tap(pg, 'r', 'rung'); seen.append(pg.evaluate("X.rot.rung===undefined?null:X.rot.rung"))
    ok(seen == [1, 2, 3, None], 'tapping a Rotation row cycles 1 → 2 → 3 → off: ' + json.dumps(seen))
    ok(pg.text_content(f"{ROW('r', 'rung')} .ring text") == '+' and 'ago' in pg.inner_text(f"{ROW('r', 'rung')} small"), 'off again, it shows how long ago it was done')
    tap(pg, 'r', 'rung', 2)
    ok(cta(pg) == 'Log 1 exercise' and pg.locator('#dock [data-a=finHere]').count() == 0, 'one picked: Log 1 exercise, and no Finish here')
    tap(pg, 'r', sug)
    ok(cta(pg) == 'Log 2 exercises', 'two: Log 2 exercises')
    # sort
    pg.click('#app [data-a=rSort]'); pg.wait_for_timeout(150)
    ok(pg.locator('.opmenu [data-a=rSortPick]').count() == 3, 'the sort menu offers Longest ago, Most recent and A–Z')
    t.shot(pg, 'sort-menu')
    pg.click('.opmenu [data-v=az]'); pg.wait_for_timeout(150)
    names = pg.evaluate("[...document.querySelectorAll('#app .sortlist .rgi .lbl')].map(l=>l.firstChild.textContent)")
    ok(names == sorted(names, key=str.lower) and pg.locator('.opmenu').count() == 0 and 'A–Z' in pg.inner_text('#app .sortname'), 'A–Z sorts the list')
    pg.click('#app [data-a=rSort]'); pg.click('.opmenu [data-v=recent]'); pg.wait_for_timeout(150)
    first = pg.evaluate("document.querySelector('#app .sortlist .rgi').dataset.rk")
    ok(first == 'r:rung' or pg.evaluate("(D.ex[document.querySelector('#app .sortlist .rgi').dataset.rk.slice(2)]||{}).last") is not None,
       'Most recent puts the latest done first')
    # reopen Foundation, change it, Done; its end stays as it was
    fe = pg.evaluate("[X.fEnd,X.fE]")
    pg.click('#app .osec.folded [data-a=flowOpen]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.fEdit") == 0 and pg.locator('#app .osec.reopened [data-a=flowDone]').count() == 1, 'tapping Foundation’s line reopens it, with Done')
    t.shot(pg, 'reopened')
    tap(pg, 'f', 'lip')
    pg.click('#app [data-a=flowDone]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("X.f.lip") == 3 and pg.evaluate("U.fEdit") is None and pg.evaluate("[X.fEnd,X.fE]") == fe and pg.evaluate("U.view") == 'rot',
       'a change is kept, Done folds it again, and Foundation’s end isn’t touched')
    pg.evaluate("X.rot={};saveDraft();render()")
    e0 = pg.evaluate("elapsedSec()")
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'app' and pg.evaluate("X.rot") == {} and abs(pg.evaluate("X.rE") - e0) < 1.5,
       'Skip rotation goes on to Application, recording Rotation’s end as before')
    ok('Not today' in pg.inner_text('#app .osec.folded[data-sec="1"]'), 'Rotation’s line says Not today')
    ok(cta(pg) == 'Finish session' and pg.locator('#app .osec.active [data-a=song]').count() >= 1, 'Application keeps its song list, with Finish session')
    t.shot(pg, 'application')
    pg.context.close()


def finishing(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    # the same times give the same split as before: Foundation 15, Rotation 15, Application 10
    draft(pg, 'midApplication')
    pg.click('[data-a=resume]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'app' and pg.locator('#app .osec.folded').count() == 2, 'a 3.31 draft in Application resumes there, both steps folded')
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(300); pg.click('[data-a=saveHow]'); pg.wait_for_timeout(400)
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss.get('mixed') is False and ss['split'] == {'f': 15, 'r': 15, 'a': 10} and ss['rot'] == {'rung': 3}, 'Progress’s split is unchanged: ' + json.dumps(ss.get('split')))
    pg.evaluate("U.sheet=null;rerender()")
    # Just Foundation today? Finish here: Rotation ends at the save, Application gets none
    draft(pg, 'midRotation')
    pg.evaluate("X.rot={};saveDraft()")
    pg.click('[data-a=resume]'); pg.wait_for_timeout(200)
    pg.click('#dock [data-a=finHere]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'how', 'Finish here opens How did it go?')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'rot' and not pg.evaluate("X.rEnd") and not pg.evaluate("U.finHere"), 'closing it leaves the session running on Rotation')
    pg.click('#dock [data-a=finHere]'); pg.wait_for_timeout(300); pg.click('[data-a=saveHow]'); pg.wait_for_timeout(400)
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss['rot'] == {} and ss['split']['a'] == 0 and abs(ss['split']['f'] - 20) < 0.5 and ss['split']['r'] > 0 and pg.evaluate("X") is None,
       'saved with no Rotation and no Application time: ' + json.dumps(ss['split']))
    ok(ss['xn']['humming'] == {'w': ['Buzz in the mask'], 't': 'Better after straw'} and ss['xn']['slides'] == 'old string note', 'its notes from 3.31 are kept as they were')
    pg.context.close()


def resume(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    draft(pg, 'midRotation')
    pg.click('[data-a=resume]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'rot' and pg.locator('#app .osec.folded').count() == 1 and pg.locator('#app .osec.active h1').inner_text() == 'Rotation',
       'a 3.31 draft saved mid-Rotation resumes on Rotation')
    ok(pg.evaluate("X.f") == {'slides': 3, 'humming': 2, 'lip': 0, 'straw': 2} and '3 done · 1 skipped · 20:00' in pg.inner_text('#app .osec.folded'),
       'Foundation is folded with its levels and its time')
    ok(pg.text_content(f"{ROW('r', 'nasal')} .ring text") == '2' and pg.inner_text(f"{ROW('r', 'falsetto')} small") == 'Tap to set a level',
       'Rotation shows the level it had, and an exercise picked without one')
    ok(cta(pg) == 'Log 2 exercises', 'the button counts both')
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'rot' and 'Set a level for each exercise you picked' in pg.inner_text('.toast'), 'as before, each picked exercise needs a level')
    tap(pg, 'r', 'falsetto')
    ok(pg.evaluate("X.rot.falsetto") == 1, 'tapping it gives it level 1')
    pg.click('#app .osec.folded [data-a=flowOpen]'); pg.wait_for_timeout(150)
    ok('Level 2 · Buzz in the mask — Better after straw' in pg.inner_text(f"{ROW('f', 'humming')} small")
       and 'old string note' in pg.inner_text(f"{ROW('f', 'slides')} small"), 'its notes show on Foundation’s rows, old ones too')
    tap(pg, 'f', 'humming')
    ok(until(pg, OPEN('f', 'humming')) and 'Better after straw' in pg.inner_text(f"{ROW('f', 'humming')} .cuebox"), 'and its written note shows in the box')
    pg.click('#app [data-a=flowDone]'); pg.wait_for_timeout(100)
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'app', 'then on to Application')
    # an older draft (before step times were kept) still opens
    draft(pg, 'noStamps')
    pg.click('[data-a=resume]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'rot' and abs(pg.evaluate("X.fE") - 600) < 1, 'a draft from before 3.2 resumes on Rotation, its time filled in')
    pg.context.close()


def pull(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.click('[data-a=start]'); pg.wait_for_timeout(200)
    pg.evaluate("scrollTo(0,document.documentElement.scrollHeight)"); pg.wait_for_timeout(150)
    # hold the pull part-way: the page follows the finger, with resistance, saying what's needed
    cdp = pg.context.new_cdp_session(pg)
    send = lambda ty, y: cdp.send('Input.dispatchTouchEvent', {'type': ty, 'touchPoints': [] if ty == 'touchEnd' else [{'x': 200, 'y': y}]})
    send('touchStart', 700)
    for i in range(1, 13):
        send('touchMove', 700 - i * 25); pg.wait_for_timeout(16)
    st = pg.evaluate("OP.state()")
    tf = pg.evaluate("document.getElementById('app').style.transform")
    ok(st['pull'] and 0 < st['off'] < 300 and tf.startswith('translateY(-'), 'pulling past the bottom moves the page with resistance (' + tf + ')')
    ok('Set a level or Skip for each exercise' in pg.inner_text('#opPull') and float(pg.evaluate("getComputedStyle(document.getElementById('opPull')).opacity")) > 0.5,
       'and says what’s still needed')
    t.shot(pg, 'pull')
    send('touchEnd', 0); cdp.detach(); pg.wait_for_timeout(300)
    ok(not pg.evaluate("OP.state().pull") and pg.evaluate("document.getElementById('app').style.transform") == '' and pg.evaluate("U.view") == 'found',
       'letting go springs back, still on Foundation')
    ok(until(pg, "!!document.querySelector('#app .rgi.rneed')", timeout=3000), 'a long pull points at what’s missing')
    # a short sideways swipe is not a pull
    pg.evaluate("scrollTo(0,document.documentElement.scrollHeight)"); pg.wait_for_timeout(100)
    drag(pg, 300, 600, 200, 590, steps=6)
    ok(not pg.evaluate("OP.state().pull") and pg.evaluate("document.getElementById('app').style.transform") == '', 'a sideways swipe doesn’t pull')
    # the wheel (trackpad) does the same, and lets go by itself
    pg.mouse.move(200, 500)
    for _ in range(4): pg.mouse.wheel(0, 120); pg.wait_for_timeout(20)
    ok(pg.evaluate("OP.state().pull"), 'the wheel at the bottom pulls too')
    ok(until(pg, "!OP.state().pull&&document.getElementById('app').style.transform===''", timeout=3000), 'and springs back when it stops')
    pg.context.close()


def motion(b, t):
    """Motion on (slow motion, so it can be caught): level 3's sweep, the fold, the steps moving; Reduce Motion fades."""
    ok = t.ok
    pg = t.page(b, touch=True, init=MOTION_ON)
    pg.evaluate("MOTION.setSpeed(4)")
    pg.click('[data-a=start]'); pg.wait_for_timeout(300)
    tap(pg, 'f', 'slides', 3)
    sw = ROW('f', 'slides') + ' .rsweep'
    ok(until(pg, f"document.querySelector('{sw}').getAnimations().some(a=>String(a.effect.getKeyframes()[0].transform).startsWith('scaleX(0)'))", timeout=4000),
       'level 3: the card fills from the left')
    ok(not pg.evaluate(OPEN('f', 'slides')), 'before the box opens')
    ok(until(pg, f"document.querySelector('{ROW('f', 'slides')}').classList.contains('peak')", timeout=8000), 'then it flashes green and the ring turns green')
    ok(until(pg, OPEN('f', 'slides'), timeout=4000), 'then the box unfolds, inside the green')
    t.shot(pg, 'sweep')
    pg.evaluate("MOTION.setSpeed(1)")
    tap(pg, 'f', 'humming', 2)
    ok(not pg.evaluate(OPEN('f', 'humming')), 'level 2 waits for the settle')
    ok(until(pg, OPEN('f', 'humming'), timeout=3000), 'then its box opens')
    pg.evaluate("FOUND.forEach(e=>{if(!(e.id in X.f))X.f[e.id]=1});saveDraft()")
    pg.click('#dock [data-a=cta]'); pg.wait_for_timeout(30)
    an = pg.evaluate("[...document.querySelectorAll('#app .osec')].map(s=>s.getAnimations().length)")
    ok(pg.evaluate("U.view") == 'rot' and all(n >= 1 for n in an), 'logging Foundation moves all three steps: ' + json.dumps(an))
    pg.wait_for_timeout(1200)
    # Reduce Motion: only fades
    pg.evaluate("localStorage.setItem('vocalReduce','on');MOTION.publish()")
    pg.click('#app .osec.folded [data-a=flowOpen]'); pg.wait_for_timeout(30)
    kf = pg.evaluate("[...document.querySelectorAll('#app .osec')].flatMap(s=>s.getAnimations().map(a=>Object.keys(a.effect.getKeyframes()[0]).filter(k=>!['offset','easing','composite','computedOffset'].includes(k))))")
    ok(kf and all(k == ['opacity'] for k in kf), 'with Reduce Motion, reopening a step only fades: ' + json.dumps(kf))
    tap(pg, 'f', 'lip', 2)
    ok(until(pg, OPEN('f', 'lip'), timeout=3000), 'level 3 with Reduce Motion still opens its box')
    ok(not pg.evaluate(f"document.querySelector('{ROW('f', 'lip')} .rsweep').getAnimations().some(a=>a.effect.getKeyframes().some(k=>k.transform))"),
       'with a fade, not a sweep')
    pg.context.close()


def screens(b, t):
    ok = t.ok
    for w, h in ((390, 844), (375, 667)):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, touch=True)
            tag = f'{w} {sc}'
            pg.click('[data-a=start]'); pg.wait_for_timeout(200)
            tap(pg, 'f', 'slides', 2); until(pg, OPEN('f', 'slides'), timeout=3000)
            ok(pg.evaluate(WIDE), f'{tag}: Foundation with a box open fits, no sideways scroll')
            t.shot(pg, f'found-{w}-{sc}')
            pg.evaluate("FOUND.forEach(e=>X.f[e.id]=3);X.xn.slides={w:['Smooth glide'],t:''};saveDraft();OP.advance()"); pg.wait_for_timeout(200)
            ok(pg.evaluate(WIDE), f'{tag}: Rotation fits')
            r = pg.evaluate("(()=>{const c=document.querySelector('#dock [data-a=cta]').getBoundingClientRect(),f=document.querySelector('#dock .opfin').getBoundingClientRect();return [c.bottom<=innerHeight,f.bottom<=innerHeight,c.left>=0,c.right<=innerWidth]})()")
            ok(all(r), f'{tag}: the button and Finish here are on screen')
            t.shot(pg, f'rot-{w}-{sc}')
            pg.evaluate("X.rot={rung:2};saveDraft();OP.advance()"); pg.wait_for_timeout(200)
            ok(pg.evaluate(WIDE), f'{tag}: Application fits')
            t.shot(pg, f'app-{w}-{sc}', full_page=True)
            pg.context.close()


def run(b, t):
    print('-- levels'); levels(b, t)
    print('-- rotation'); rotation(b, t)
    print('-- finishing'); finishing(b, t)
    print('-- resume'); resume(b, t)
    print('-- pull'); pull(b, t)
    print('-- motion'); motion(b, t)
    print('-- screens'); screens(b, t)
