"""3.13 the launch ripple: on a cold launch the icon's bars pulse in turn, the launch screen fades with a slight zoom,
then Today's blocks rise in, top to bottom. Only on a cold launch (and after importing a backup), Reduce Motion gives
a plain fade, motion off behaves as before, the floating window waits for it, and the 3.4 launch screen checks still
hold (no white flash, no jump) at every size in light and dark."""
import json
from harness import sample, SEED, OLD_DRAFT, ready, url, APP_PATH, UA_IPHONE, fix
from test_layout import SIZES

MOTION_ON = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"
# the checks that watch the ripple while it plays run it in slow motion (x4), so a slow machine can't miss it
SLOW = 4
MOTION_SLOW = "try{localStorage.setItem('vocalMotion','%d')}catch(e){}" % SLOW
# the animations running on the bars, Today's blocks and the launch screen, as {delay, frames}
ANIMS = """sel=>[...document.querySelectorAll(sel)].map(el=>el.getAnimations().map(a=>({d:a.effect.getTiming().delay,
  k:a.effect.getKeyframes().map(f=>Object.keys(f).filter(x=>!['offset','easing','composite','computedOffset'].includes(x)).join()).join('|')})))"""
# Today's blocks, in the order they sit on screen
ORDER = """[...document.querySelectorAll('#app [data-rise]')].map((el,i)=>({i,r:el.getBoundingClientRect()}))
  .filter(b=>b.r.height>0&&b.r.bottom>0&&b.r.top<innerHeight)
  .sort((a,b)=>Math.round(a.r.top/4)-Math.round(b.r.top/4)||a.r.left-b.r.left).map(b=>b.i)"""
SETTLED = """(()=>{const els=[...document.querySelectorAll('#app [data-rise]')];return els.length>0&&els.every(el=>
  !el.getAnimations().length&&getComputedStyle(el).opacity==='1'&&['none',''].includes(el.style.transform)&&
  !/matrix\\(1, 0, 0, 1, 0, [1-9]/.test(getComputedStyle(el).transform))})()"""
GONE = "!document.getElementById('splash')"


def cold(b, w=390, h=844, sc='light', init=MOTION_ON, ctx_args=None, data=None):
    """A cold launch with motion on (unless init says otherwise), returned as soon as the page has loaded."""
    args = dict(viewport={'width': w, 'height': h}, device_scale_factor=2, color_scheme=sc, user_agent=UA_IPHONE,
                timezone_id='Europe/London', locale='en-GB')
    args.update(ctx_args or {})
    ctx = b.new_context(**args)
    ctx.add_init_script("try{localStorage.setItem('vocalMotion','0')}catch(e){}")
    if init: ctx.add_init_script(init)
    pg = ctx.new_page()
    pg.goto(url(APP_PATH)); pg.evaluate(SEED, data or sample()); ready(pg)
    pg.reload(wait_until='load')
    return pg


def errors(t, pg, tag):
    pg.on('pageerror', lambda e: t.errors.append(f'launch {tag}: {str(e).splitlines()[0]}'))


def ripple(b, t):
    ok = t.ok
    pg = cold(b, init=MOTION_SLOW); errors(t, pg, 'ripple')
    bars = pg.evaluate(ANIMS, '#splash i')
    ok(len(bars) == 6 and all(len(a) == 1 and a[0]['k'] == 'transform|transform|transform' for a in bars),
       'all six bars of the icon pulse on a cold launch')
    ok([a[0]['d'] for a in bars] == [(120 + 70 * k) * SLOW for k in range(6)], 'they pulse in order, 70 ms apart, starting 120 ms in')
    ok(pg.evaluate("LAUNCH.busy()") and pg.evaluate("!FW.shown"), 'the launch is under way')
    pg.wait_for_function("document.getElementById('splash')&&document.getElementById('splash').dataset.going", timeout=15000)
    sp = pg.evaluate(ANIMS, '#splash, #splash .sp-icon')
    ok(sp[0] and sp[0][0]['k'] == 'opacity|opacity' and sp[1] and sp[1][0]['k'] == 'transform|transform',
       'the launch screen fades with a slight zoom')
    ok(pg.evaluate("getComputedStyle(document.getElementById('splash')).pointerEvents") == 'none', 'it never blocks taps while it fades')
    rise = pg.evaluate(ANIMS, '#app [data-rise]')
    order = pg.evaluate(ORDER)
    delays = [rise[i][0]['d'] if rise[i] else None for i in order]
    ok(len(order) >= 8 and all(d is not None for d in delays), f"Today's blocks rise in ({len(order)} on screen)")
    ok(delays == sorted(delays) and len(set(delays)) == len(delays) and delays[1] - delays[0] == 45 * SLOW,
       'top to bottom, 45 ms apart')
    ok(all(rise[i][0]['k'] == 'opacity,transform|opacity,transform' for i in order), 'each one rises and fades in')
    ok(pg.evaluate("[...document.querySelectorAll('#app [data-rise]')].slice(0,3).every(el=>+getComputedStyle(el).opacity<.2)"),
       'blocks waiting their turn are hidden, so nothing shows before it rises')
    pg.wait_for_function("!LAUNCH.busy()", timeout=15000); pg.wait_for_timeout(100)
    ok(pg.evaluate(GONE), 'the launch screen is gone afterwards')
    ok(pg.evaluate(SETTLED), 'and nothing is left hidden or offset')
    # 3.14: once the ripple is over, the arch fills and the week row ripples; wait for those, then nothing should move
    # (3.23: Today's gradient drifts endlessly; endless animations don't count)
    pg.wait_for_function("!document.getAnimations().some(a=>(a.playState==='running'||a.playState==='pending')&&a.effect.getTiming().iterations!==Infinity)", timeout=15000)
    ok(not pg.evaluate("document.getAnimations().filter(a=>a.playState!=='finished'&&a.effect.getTiming().iterations!==Infinity).length"), 'and nothing is still animating')

    # only on a cold launch
    pg.evaluate("go(()=>{U.tab='songs'})"); pg.wait_for_timeout(100); pg.evaluate("go(()=>{U.tab='today'})"); pg.wait_for_timeout(100)
    ok(pg.evaluate(GONE) and not pg.evaluate("LAUNCH.busy()") and not pg.evaluate(ANIMS, '#app [data-rise]')[0],
       'switching tabs and back to Today does not replay it')
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
    pg.wait_for_timeout(200)
    ok(pg.evaluate(GONE) and not pg.evaluate("LAUNCH.busy()"), 'nor does coming back to the app')

    # importing a backup replays it on Today
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';render()")
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(fix('backup-3.6.json')); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]')
    pg.wait_for_function("!!document.getElementById('splash')", timeout=15000)
    ok(pg.evaluate("U.tab") == 'today' and pg.evaluate("LAUNCH.busy()"), 'importing a backup brings the launch screen back on Today')
    pg.wait_for_function("document.querySelectorAll('#splash i').length===6&&[...document.querySelectorAll('#splash i')].every(i=>i.getAnimations().length)", timeout=15000)
    ok(True, 'and the bars pulse again')
    ok(pg.locator('.toast').count() == 0, 'the "Backup restored" message waits for the ripple')
    pg.wait_for_function("document.getElementById('splash')&&document.getElementById('splash').dataset.going", timeout=15000)
    ok(len([a for a in pg.evaluate(ANIMS, '#app [data-rise]') if a]) >= 8, "Today's blocks rise in again")
    ok(pg.locator('.toast').count() == 1 and 'Backup restored' in pg.locator('.toast').inner_text(), 'and the message shows as the screen goes')
    pg.wait_for_function("!LAUNCH.busy()", timeout=15000)
    # 3.17: under a heavily loaded machine the last rise can be a frame or two behind LAUNCH ending, so allow 1.5 s
    try: pg.wait_for_function(SETTLED, timeout=1500)
    except Exception: pass
    ok(pg.evaluate(GONE) and pg.evaluate(SETTLED), 'then the screen is clear and settled')
    pg.context.close()


def window_waits(b, t):
    ok = t.ok
    d = sample()
    pg = cold(b, init=MOTION_SLOW + ";try{localStorage.setItem('vocalDraft'," + json.dumps(json.dumps(OLD_DRAFT)) + ")}catch(e){}", data=d)
    errors(t, pg, 'window')
    seen = pg.evaluate("""new Promise(r=>{const out=[];const tick=()=>{out.push([LAUNCH.busy(),!!FW.shown]);
      if(LAUNCH.busy()||out.length<5)requestAnimationFrame(tick);else r(out)};tick()})""")
    ok(any(s[0] for s in seen) and not any(s[0] and s[1] for s in seen), 'a running session\'s floating window stays away during the launch')
    pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'session', 'and appears once Today has risen in')
    pg.context.close()


def reduced(b, t):
    ok = t.ok
    pg = cold(b, init=MOTION_SLOW, ctx_args={'reduced_motion': 'reduce'}); errors(t, pg, 'reduced')
    ok(not any(pg.evaluate(ANIMS, '#splash i')), 'Reduce Motion: the bars stay still')
    pg.wait_for_function("document.getElementById('splash')&&document.getElementById('splash').dataset.going", timeout=15000)
    sp = pg.evaluate(ANIMS, '#splash, #splash .sp-icon')
    ok(sp[0] and sp[0][0]['k'] == 'opacity|opacity' and not sp[1], 'the launch screen just fades, with no zoom')
    ok(not any(pg.evaluate(ANIMS, '#app [data-rise]')), 'and Today appears without rising')
    pg.wait_for_function("!LAUNCH.busy()", timeout=15000)
    ok(pg.evaluate(GONE) and pg.evaluate(SETTLED), 'then the screen is clear')
    pg.context.close()


def motion_off(b, t):
    ok = t.ok
    # note how the launch screen leaves, from the very start (a slow machine might otherwise miss it)
    watch = """document.addEventListener('DOMContentLoaded',()=>{const s=document.getElementById('splash');if(!s)return;
      new MutationObserver(()=>{if(s.classList.contains('out')&&!window.__out)window.__out=s.getAnimations().some(a=>!(a instanceof CSSTransition))?'animated':'out'})
      .observe(s,{attributes:true})})"""
    pg = cold(b, init=watch); errors(t, pg, 'off')
    ok(not pg.evaluate("document.getAnimations().length") and not pg.evaluate("LAUNCH.busy()"), 'motion off: no ripple, as before 3.13')
    pg.wait_for_function("!!window.__out", timeout=15000)
    ok(pg.evaluate("window.__out") == 'out', 'the launch screen goes the way it always has')
    pg.wait_for_function(GONE, timeout=3000)
    ok(pg.evaluate(SETTLED), 'and Today is there, untouched')
    pg.context.close()


def pixel(png):
    """The colour of the first pixel of a small screenshot, read with the standard library (GitHub has no image library)."""
    import zlib, struct
    pos, idat, w = 8, b'', 0
    while pos < len(png):
        n, kind = struct.unpack('>I4s', png[pos:pos + 8]); data = png[pos + 8:pos + 8 + n]
        if kind == b'IHDR': w, ch = struct.unpack('>I', data[:4])[0], {2: 3, 6: 4}[data[9]]
        if kind == b'IDAT': idat += data
        pos += 12 + n
    raw = zlib.decompress(idat)
    return tuple(raw[1:4])  # first row, first pixel (filter type 0 or 1 leaves the first pixel as is)


def first_frame(b, t):
    """The 3.4 checks: the first frame is the plain background with the icon, centred on 100lvh, in light and dark."""
    ok = t.ok
    bad = []
    for name, w, h in [(s[0], s[1], s[2]) for s in SIZES]:
        for sc in ('light', 'dark'):
            for js in (False, True):
                ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, color_scheme=sc, java_script_enabled=js,
                                    user_agent=UA_IPHONE)
                pg = ctx.new_page(); pg.goto(url(APP_PATH), wait_until='load')
                g = pg.evaluate("""(()=>{const s=document.getElementById('splash'),i=s.querySelector('.sp-icon'),r=i.getBoundingClientRect(),
                  sr=s.getBoundingClientRect(),bars=[...i.querySelectorAll('i')].map(x=>x.getBoundingClientRect());
                  return {bg:getComputedStyle(document.documentElement).backgroundColor,sbg:getComputedStyle(s).backgroundColor,
                  cx:r.left+r.width/2,cy:r.top+r.height/2,w:r.width,sh:sr.height,sw:sr.width,lvh:(()=>{const d=document.createElement('div');
                  d.style.height='100lvh';document.body.appendChild(d);const v=d.getBoundingClientRect().height;d.remove();return v})(),
                  inside:bars.length===6&&bars.every(b=>b.left>=r.left&&b.right<=r.right&&b.top>=r.top&&b.bottom<=r.bottom),iw:innerWidth}})()""")
                want = 'rgb(242, 242, 247)' if sc == 'light' else 'rgb(0, 0, 0)'
                tag = f'{name} {sc}{" (scripts on)" if js else ""}'
                if g['bg'] != want or g['sbg'] != want: bad.append(f'{tag}: background {g["bg"]} / {g["sbg"]}')
                if abs(g['cx'] - g['iw'] / 2) > 0.6 or abs(g['cy'] - g['sh'] / 2) > 0.6 or abs(g['sh'] - g['lvh']) > 0.6: bad.append(f'{tag}: icon not centred on 100lvh')
                if g['w'] != 112 or not g['inside']: bad.append(f'{tag}: icon or bars out of place')
                if not js:
                    px = pg.screenshot(clip={'x': 2, 'y': 2, 'width': 4, 'height': 4})
                    c = pixel(px)
                    if c != tuple(int(x) for x in want[4:-1].split(', ')): bad.append(f'{tag}: first frame corner is {c}')
                    if name == SIZES[0][0]: pg.screenshot(path=f'{__import__("harness").OUT}/launch-first-frame-{sc}.png')
                ctx.close()
    ok(not bad, 'first frame: plain background with the icon centred on 100lvh, no flash or jump, every size, light and dark' + ('' if not bad else ': ' + '; '.join(bad[:4])))


def sizes(b, t):
    """With motion on, the ripple ends with Today laid out normally at every size, light and dark."""
    ok = t.ok
    bad = []
    for name, w, h in [(s[0], s[1], s[2]) for s in SIZES]:
        for sc in ('light', 'dark'):
            pg = cold(b, w=w, h=h, sc=sc); errors(t, pg, name)
            pg.wait_for_function("!LAUNCH.busy()", timeout=8000); pg.wait_for_timeout(100)
            if not (pg.evaluate(GONE) and pg.evaluate(SETTLED)): bad.append(f'{name} {sc}: not settled')
            if pg.evaluate("document.documentElement.scrollWidth>innerWidth+1"): bad.append(f'{name} {sc}: sideways scroll')
            pg.context.close()
    ok(not bad, 'after the ripple, Today is settled at every size, light and dark' + ('' if not bad else ': ' + '; '.join(bad[:4])))


def run(b, t):
    ripple(b, t)
    window_waits(b, t)
    reduced(b, t)
    motion_off(b, t)
    first_frame(b, t)
    sizes(b, t)
