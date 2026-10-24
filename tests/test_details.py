"""3.14 motion details (js/details.js): rows leave and the gap closes, new rows slide in, rows move to their new places
(sort) and a pinned song travels, Progress bars ripple in the direction of time while scrubbing stays instant, the
breakdown bars grow row by row, Today's arch fills and the week row ripples after the launch, today's circle pops after a
session, calendar days ripple, session steps slide in the direction you're heading, Recall masks and unmasks word by word,
a sheet that changes in place keeps its place, and Reduce Motion gives fades only (motion off: nothing at all)."""
import datetime as dt
from harness import sample, with_song_practice, iso
from test_sections import LYR, ADD

SLOW = 4
ON = "try{localStorage.setItem('vocalMotion','%d')}catch(e){}" % SLOW
SKIP = "['offset','easing','composite','computedOffset']"
# the animations running on matching elements, as {delay, props}
ANIM = f"""sel=>[...document.querySelectorAll(sel)].flatMap(el=>el.getAnimations().map(a=>({{d:a.effect.getTiming().delay,
  k:Object.keys(a.effect.getKeyframes()[0]).filter(x=>!{SKIP}.includes(x)).join()}})))"""
QUIET = "!document.getAnimations().some(a=>a.playState==='running'||a.playState==='pending')"


def daily():
    """sample() plus a session on each of the last 15 days (today included), so every week has bars and the arch has
    minutes whatever day the tests run on."""
    d = sample()
    now = dt.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    for i in range(15):
        s = now - dt.timedelta(days=i)
        d['sessions'].append({"id": f"sd{i}", "date": iso(s), "end": iso(s + dt.timedelta(minutes=10 + i)), "mins": 10 + i,
                              "f": {"slides": 2}, "fNote": "", "rot": {}, "rNote": "", "rotNames": {}, "songName": "",
                              "rate": {}, "takes": []})
    return d


def quiet(pg, ms=30000):
    pg.wait_for_function(QUIET, timeout=ms)


def page(b, t, w=390, h=844, data=None, init=ON, sc='light', ctx_args=None):
    pg = t.page(b, w=w, h=h, sc=sc, touch=True, data=data if data is not None else sample(), init=init, ctx_args=ctx_args)
    return pg


def lists(b, t):
    ok = t.ok
    pg = page(b, t)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='history';U.view='all'})")
    quiet(pg)
    n = pg.locator('#app .sw').count()
    ok(n == 3, 'All sessions lists the three sessions')
    # delete the newest: its copy shrinks away, the rows below slide up, the group closes the gap
    pg.evaluate("U.sheet='delSession';U.sd={k:'s2'};rerender()")
    quiet(pg)
    top = pg.evaluate("document.querySelector('#app .sw').dataset.fk")
    pg.click('[data-a=delSession]')
    pg.wait_for_timeout(60)
    ok(pg.locator('.det-ghost').count() == 1, 'a deleted row leaves a copy that shrinks away')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.det-ghost')).pointerEvents") == 'none', 'which never blocks taps')
    g = pg.evaluate(ANIM, '#app [data-gk]')
    ok(any('minHeight' in a['k'] for a in g), 'the group eases down to its new height, closing the gap')
    rows = pg.evaluate(ANIM, '#app .sw')
    ok(len(rows) == 2 and all(r['k'] == 'transform' for r in rows), 'the rows below slide up into the gap')
    ok(len({r['d'] for r in rows}) == 1, 'all together, so they stay inside the closing group')
    quiet(pg)
    ok(pg.locator('.det-ghost').count() == 0 and pg.locator('#app .sw').count() == 2, 'afterwards the copy is gone and two rows remain')
    ok(pg.evaluate("document.querySelector('#app .sw').dataset.fk") != top, 'the newest row is the one that left')
    pg.context.close()

    # songs: pinning travels, sorting ripples
    d = sample()
    d['songs'] = [{"id": "g_a", "name": "Mid", "artist": "", "added": 3000, "pinned": False},
                  {"id": "g_b", "name": "Alpha", "artist": "", "added": 2000, "pinned": False},
                  {"id": "g_c", "name": "Zeta", "artist": "", "added": 1000, "pinned": False}]
    pg = page(b, t, data=d)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='songs'})")
    quiet(pg)
    ok(pg.locator('[data-gk=songs] .srow').count() == 3 and pg.locator('[data-gk=pinned]').count() == 0, 'three songs, none pinned')
    order0 = pg.evaluate("[...document.querySelectorAll('[data-gk=songs] .srow')].map(e=>e.dataset.fk)")
    pg.evaluate("SG_ACT.sgSetSort(null,'az')")
    pg.wait_for_timeout(60)
    mv = pg.evaluate(ANIM, '[data-gk=songs] .srow')
    ok(len(mv) >= 2 and all(a['k'] == 'transform' for a in mv), 'a new sort order slides the rows that moved')
    ds = sorted({a['d'] for a in mv})
    ok(len(ds) >= 2 and ds[1] - ds[0] == 45 * SLOW, 'as a ripple, 45 ms apart')
    quiet(pg)
    order1 = pg.evaluate("[...document.querySelectorAll('[data-gk=songs] .srow')].map(e=>e.dataset.fk)")
    ok(order1 == ['sg:g_b', 'sg:g_a', 'sg:g_c'] and order1 != order0, 'and they end in the new order')
    pg.evaluate("togglePin('g_c')")
    pg.wait_for_timeout(80)
    ok(pg.locator('.det-ghost').count() >= 1, 'a pinned song travels up as a copy, so no group clips it on the way')
    ok(pg.evaluate("document.querySelector('[data-fk=\"sg:g_c\"]').style.visibility") == 'hidden', 'while its own row waits where it will land')
    ok(pg.locator('[data-gk=pinned]').count() == 1, 'the Pinned group is there')
    quiet(pg)
    ok(pg.locator('.det-ghost').count() == 0 and pg.evaluate("document.querySelector('[data-fk=\"sg:g_c\"]').style.visibility") == '',
       'afterwards the copy is gone and the row shows')
    # a new exercise slides into its place
    pg.evaluate("go(()=>{U.tab='exercises'})")
    quiet(pg)
    pg.evaluate("U.sheet='addEx';rerender()")
    pg.fill('#exName', 'Glide'); pg.wait_for_timeout(50)
    pg.click('[data-a=saveEx]'); pg.wait_for_timeout(60)
    new = pg.evaluate(ANIM, '#app [data-gk=custom] .sw')
    ok(any(a['k'] == 'opacity,transform' for a in new), 'a new exercise slides in')
    quiet(pg)
    pg.context.close()


def progress(b, t):
    ok = t.ok
    pg = page(b, t, data=daily())
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='history'})")
    quiet(pg)
    pg.click('[data-a=prange][data-v=M]')
    pg.wait_for_function("document.querySelectorAll('#pchart g.bar').length>10", timeout=15000)
    per = pg.evaluate("""()=>[...document.querySelectorAll('#pchart g.bar')].map(g=>[...g.querySelectorAll('path, rect:not([data-pick])')]
      .map(s=>s.getAnimations().map(a=>a.effect.getTiming().delay)).flat()).filter(a=>a.length).map(a=>Math.min(...a))""")
    ok(len(per) >= 1, 'switching the range ripples the bars in')
    ok(per == sorted(per), 'left to right')
    quiet(pg)
    pg.click('[data-a=prange][data-v=W]'); pg.wait_for_function("document.querySelectorAll('#pchart g.bar').length===7", timeout=15000)
    quiet(pg)
    ok(not pg.evaluate("U.pick"), 'no bar is picked')
    # the previous week: the wave runs right to left (the direction of time), from the old heights
    pg.click('[data-a=pnav][data-v="-1"]'); pg.wait_for_timeout(50)
    per = pg.evaluate("""()=>[...document.querySelectorAll('#pchart g.bar')].map(g=>[...g.querySelectorAll('path, rect:not([data-pick])')]
      .map(s=>s.getAnimations().map(a=>a.effect.getTiming().delay)).flat()).filter(a=>a.length).map(a=>Math.min(...a))""")
    ok(len(per) >= 2 and per == sorted(per, reverse=True), 'stepping back runs the wave right to left')
    head = pg.evaluate(ANIM, '#pcard .bignum')
    ok(head and head[0]['k'] == 'opacity,transform', 'the headline total slides the way time goes, with no rolling digits')
    brk = pg.evaluate(ANIM, '#pbrk .share i')
    ok(len(brk) == 3 and all(a['k'] == 'transform' for a in brk) and [a['d'] for a in brk] == [0, 45 * SLOW, 90 * SLOW],
       'the breakdown bars grow from the left, row by row')
    quiet(pg)
    # scrubbing across the bars follows the finger: nothing is animated
    pg.evaluate("U.pick=3;updatePcard()")
    ok(pg.evaluate("document.querySelectorAll('#pcard *, #pbrk *').length>0") and
       not any(pg.evaluate("[...document.querySelectorAll('#pcard *, #pbrk *')].some(e=>e.getAnimations().length)") for _ in [0]),
       'picking a bar is instant: no animation behind the finger')
    pg.context.close()


def today(b, t):
    ok = t.ok
    pg = page(b, t, data=daily())
    pg.wait_for_function("!document.getElementById('splash')&&!LAUNCH.busy()", timeout=20000)
    arch = pg.evaluate(ANIM, '.arch svg path[pathLength]')
    wk = pg.evaluate(ANIM, '.week span')
    ok(len(arch) == 1 and arch[0]['k'] == 'strokeDashoffset', 'once the launch ripple has gone, the arch fills')
    ok(len(wk) == 7 and all(a['k'] == 'opacity,transform' for a in wk), 'and the week row ripples in')
    ok([a['d'] for a in wk] == sorted(a['d'] for a in wk) and wk[1]['d'] > wk[0]['d'], 'left to right')
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='songs'})"); pg.evaluate("go(()=>{U.tab='today'})"); pg.wait_for_timeout(100)
    ok(not pg.evaluate(ANIM, '.arch svg path[pathLength]') and not pg.evaluate(ANIM, '.week span'), 'returning to Today does not replay them')
    # a finished session: today's circle pops once its sheet has gone
    pg.evaluate("DET.finished();U.sheet='done';U.sd={k:'s0'};rerender()"); pg.wait_for_timeout(100)
    ok(not pg.evaluate(ANIM, '.week span.today'), 'while the sheet is up, it waits')
    pg.evaluate("U.sheet=null;U.sd={};rerender()"); pg.wait_for_timeout(60)
    pop = pg.evaluate(ANIM, '.week span.today')
    ok(len(pop) == 1 and pop[0]['k'] == 'transform', "then today's circle pops")
    quiet(pg)
    # the backup reminder: after backing up it shrinks away and the page closes the gap
    ok(pg.locator('.nudge').count() == 1, 'the backup reminder is showing (last backup 20 days ago)')
    pg.evaluate("DET.arm();D.lastBackup=new Date().toISOString();save();rerender()")
    pg.wait_for_timeout(60)
    gh = pg.evaluate("[...document.querySelectorAll('.det-ghost')].map(g=>g.textContent.trim().slice(0,24))")
    ok(pg.locator('#app .nudge').count() == 0 and any(g.startswith('Last backup') for g in gh),
       f'the reminder leaves a copy that shrinks away ({gh})')
    blocks = pg.evaluate(ANIM, '#app [data-rise]')
    ok(any(a['k'] == 'transform' for a in blocks), 'and the blocks below slide up')
    quiet(pg)
    ok(pg.locator('.det-ghost').count() == 0, 'then nothing is left')
    pg.context.close()


def calendar_and_steps(b, t):
    ok = t.ok
    pg = page(b, t)
    quiet(pg)
    pg.click('.calbtn'); pg.wait_for_timeout(60)
    days = pg.evaluate(ANIM, '.cal button')
    ok(len(days) >= 28 and all(a['k'] == 'opacity,transform' for a in days), 'the calendar\'s days ripple in')
    ds = sorted({a['d'] for a in days})
    ok(ds[0] == 0 and ds[1] - ds[0] == 28 * SLOW, 'along the diagonal, a little apart')
    quiet(pg)
    pg.evaluate("U.sheet=null;U.sd={};rerender()"); quiet(pg)
    # session steps: Next comes in from the right, Back from the left
    pg.evaluate("newSession();go(()=>{U.view='found'})"); quiet(pg)
    pg.evaluate("go(()=>{U.view='rot'})"); pg.wait_for_timeout(40)
    a = pg.evaluate("document.getElementById('app').getAnimations().map(a=>a.effect.getKeyframes()[0].transform)")
    ok(len(a) == 1 and a[0].startswith('translateX(') and not a[0].startswith('translateX(-'), 'going on, the next step slides in from the right')
    quiet(pg)
    pg.evaluate("go(()=>{U.view='found'})"); pg.wait_for_timeout(40)
    a = pg.evaluate("document.getElementById('app').getAnimations().map(a=>a.effect.getKeyframes()[0].transform)")
    ok(len(a) == 1 and a[0].startswith('translateX(-'), 'going back, the earlier step slides in from the left')
    quiet(pg)
    pg.evaluate("go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(40)
    ok(not pg.evaluate("document.getElementById('app').getAnimations().length"), 'leaving the session is not a step: no slide')
    pg.context.close()


def recall(b, t):
    ok = t.ok
    pg = page(b, t, data=with_song_practice(), ctx_args={'permissions': ['microphone']})
    quiet(pg)
    pg.evaluate("U.tab='songs';render()")
    pg.evaluate(ADD, LYR); pg.wait_for_timeout(300); quiet(pg)
    pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(260)
    ok(pg.evaluate(ANIM, '#dock > *'), "switching to Recall brings its capsules in with a spring")
    quiet(pg)
    pg.click('[data-a=sgHint][data-v="1"]'); pg.wait_for_timeout(60)
    ok(not pg.evaluate(ANIM, '#dock > *'), 'stepping the hint level leaves the capsules still')
    ds = pg.evaluate("[...document.querySelectorAll('.hx')].filter(x=>x.style.getPropertyValue('--hxd')).map(x=>parseFloat(x.style.getPropertyValue('--hxd')))")
    ok(len(ds) > 10, 'stepping down a level masks the words with a wave')
    ok(ds == sorted(ds) and ds[0] == 0, 'in reading order, starting at once')
    ok(sorted({round(b_ - a_) for a_, b_ in zip(ds, ds[1:]) if b_ != a_}) in ([30 * SLOW], [30 * SLOW, 60 * SLOW]), 'a word at a time, 30 ms apart')
    quiet(pg)
    # stepping up again unmasks, from the end back to the start
    pg.click('[data-a=sgHint][data-v="-1"]'); pg.wait_for_timeout(60)
    sh = pg.evaluate("[...document.querySelectorAll('.sgl .w')].filter(w=>w.getAnimations().length).map(w=>w.getAnimations()[0].effect.getTiming().delay)")
    ok(len(sh) > 10 and sh == sorted(sh, reverse=True), 'stepping back up reveals the words from the end backwards')
    quiet(pg)
    # a peeked line gets a small spring
    pg.click('[data-a=sgHint][data-v="1"]'); quiet(pg)
    pg.click('.rl >> nth=0'); pg.wait_for_timeout(40)
    pk = pg.evaluate("[...document.querySelectorAll('.rl.peeking')].map(l=>l.getAnimations().map(a=>Object.keys(a.effect.getKeyframes()[0]).filter(x=>!['offset','easing','composite','computedOffset'].includes(x)).join()))")
    ok(pk == [['transform']], 'a line you peek at settles in with a small spring')
    quiet(pg)
    pg.context.close()


def sheets(b, t):
    ok = t.ok
    pg = page(b, t)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='backup'})"); quiet(pg)
    pg.evaluate("window.__sw=null;const f=DET.sheetSwap;DET.sheetSwap=h=>{window.__sw=h;return f(h)}")
    pg.click('[data-a=exportPrep]')
    pg.wait_for_function("U.sheet==='exportReady'", timeout=20000)
    ok(pg.evaluate("window.__sw") > 50, 'Preparing backup becomes Backup ready in the same sheet, from its old height')
    ok(pg.evaluate("document.querySelector('#layer .sheet').classList.contains('still')"), 'it does not rise again')
    quiet(pg)
    pg.context.close()


def reduced(b, t):
    ok = t.ok
    pg = page(b, t, ctx_args={'reduced_motion': 'reduce'})
    pg.wait_for_function("!document.getElementById('splash')", timeout=20000)
    ok(not pg.evaluate("MOTION.on()"), 'Reduce Motion: movement is off')
    pg.click('.calbtn'); pg.wait_for_timeout(60)
    an = pg.evaluate("[...document.querySelectorAll('#layer .sheet, #layer .scrim')].flatMap(e=>e.getAnimations().map(a=>Object.keys(a.effect.getKeyframes()[0]).filter(x=>!['offset','easing','composite','computedOffset'].includes(x)).join()))")
    ok(an and all(k == 'opacity' for k in an), 'a sheet fades in instead of rising')
    ok(not pg.evaluate(ANIM, '.cal button'), 'the calendar days do not ripple')
    pg.evaluate("U.sheet=null;U.sd={};rerender()")
    pg.evaluate("go(()=>{U.tab='history';U.view='all'})")
    pg.evaluate("U.sheet='delSession';U.sd={k:'s2'};rerender()")
    pg.click('[data-a=delSession]'); pg.wait_for_timeout(60)
    ok(pg.locator('.det-ghost').count() == 0, 'a deleted row just goes: no shrinking copy')
    ok(pg.evaluate("[...document.querySelectorAll('#app *')].every(e=>e.getAnimations().every(a=>!Object.keys(a.effect.getKeyframes()[0]).includes('transform')))"),
       'and nothing slides, scales or moves')
    pg.context.close()


def motion_off(b, t):
    ok = t.ok
    pg = t.page(b, touch=True, data=sample())
    pg.evaluate("go(()=>{U.tab='history';U.view='all'})")
    pg.evaluate("U.sheet='delSession';U.sd={k:'s2'};rerender()")
    pg.click('[data-a=delSession]'); pg.wait_for_timeout(60)
    APP_ANIMS = "[...document.querySelectorAll('#app, #app *')].reduce((n,e)=>n+e.getAnimations().length,0)"
    ok(pg.locator('.det-ghost').count() == 0 and pg.evaluate(APP_ANIMS) == 0, 'motion off: no copies, nothing in the page animates, as before 3.14')
    ok(pg.locator('#app .sw').count() == 2, 'and the row is simply gone')
    pg.evaluate("U.range='M';updatePcard({dir:0})")
    ok(pg.evaluate(APP_ANIMS) == 0, 'the chart does not animate either')
    pg.context.close()


def run(b, t):
    for f in (lists, progress, today, calendar_and_steps, recall, sheets, reduced, motion_off):
        print(f'-- {f.__name__}', flush=True)
        f(b, t)
