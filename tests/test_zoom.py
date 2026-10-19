"""3.15 card zoom (js/zoom.js): every kind of card zooms into the right page and Back shrinks it into the right card
(back where the list was), Back in the middle of a zoom reverses it with no stray layers, a swipe back from anywhere
follows the finger and closes past its threshold or on a flick and springs back below it, a row's own swipe (and other
gestures) beat the swipe back, the window is never an empty dark box (sampled frame by frame in dark mode, wide and
small cards), the Start session capsule expands and Finish shrinks back into it, a calendar day's sessions grow out of
the day, the new song's paste sheet shrinks into its row, Reduce Motion gives fades only, and with motion off nothing is
drawn but Back still returns to where the list was."""
from harness import sample, with_song_practice
from test_sections import LYR
from test_window import drag
from test_details import daily

SLOW = 4
ON = "try{localStorage.setItem('vocalMotion','%d')}catch(e){}" % SLOW
# settled: nothing moving (endless pulses, like the changelog's newest dot, don't count) and no zoom on screen
QUIET = "!document.getAnimations().some(a=>(a.playState==='running'||a.playState==='pending')&&a.effect.getTiming().iterations!==Infinity)&&!ZOOM.busy()"
CLEAN = "!document.querySelector('.zm')&&!document.querySelector('.zm-src')&&!ZOOM.busy()"
GROWING = "(()=>{const c=document.querySelector('.zm .zm-c');return !!c&&c.getAnimations().length>0})()"
BACK = '#barL [aria-label^="Back"]'
# freeze every animation (after the zoom's first frames), to look at exact moments
FREEZE = """async js=>{(new Function(js))();for(let i=0;i<3;i++)await new Promise(r=>requestAnimationFrame(r));
  window._an=document.getAnimations().filter(a=>a.effect.getTiming().iterations!==Infinity);window._an.forEach(a=>a.pause());return window._an.length}"""
AT = "t=>window._an.forEach(a=>{a.currentTime=t})"
PLAY = "()=>window._an.forEach(a=>a.play())"
# how much of the window is covered by something: the card's colour, the page or the card itself (never empty)
COVER = """()=>{const z=document.querySelector('.zm');if(!z)return null;const o=s=>{const e=z.querySelector(s);return e?+getComputedStyle(e).opacity:0};
  return 1-(1-o('.zm-tint'))*(1-o('.zm-body'))*(1-o('.zm-ghost'))}"""


def page(b, t, w=390, h=844, sc='light', data=None, init=ON, ctx_args=None):
    return t.page(b, w=w, h=h, sc=sc, touch=True, data=data if data is not None else songs(), init=init, ctx_args=ctx_args)


def songs():
    """sample() with a pinned song that has lyrics, and enough songs to scroll the list."""
    d = with_song_practice()
    d['songs'] = [{"id": "g_1", "name": "Versace on the Floor · bridge", "pinned": True, "added": 5000}] + \
        [{"id": f"g_x{i}", "name": f"Song {i:02d}", "artist": "", "added": 1000 + i, "pinned": False} for i in range(14)]
    return d


def quiet(pg, ms=30000):
    pg.wait_for_function(QUIET, timeout=ms)
    pg.wait_for_timeout(60)


def where(pg):
    return pg.evaluate("U.tab+'|'+(U.view||'')")


def cards(b, t):
    """Each kind of card: zooms into its page, Back shrinks the page into it, and the list is where it was."""
    ok = t.ok
    pg = page(b, t)
    quiet(pg)
    CASES = [
        # (name, how to get to the list, the card, the page it opens)
        ('an exercise row in Exercises', "go(()=>{U.tab='exercises';U.view=null})", '[data-zk="ex:hinge"]', 'exercises|ex'),
        ('Today\'s suggested rotation', "go(()=>{U.tab='today';U.view=null})", '.dash [data-zk^="ex:"]', 'today|ex'),
        ('a pinned song on Today', "go(()=>{U.tab='today';U.view=null})", '[data-zk="sg:g_1"]', 'songs|lyr'),
        ('a song in Songs', "go(()=>{U.tab='songs';U.view=null})", '[data-zk="sg:g_x3"]', 'songs|lyr'),
        ('Show all sessions on Progress', "go(()=>{U.tab='history';U.view=null})", '[data-zk="all:sessions"]', 'history|all'),
        ('Changelog in Settings', "go(()=>{U.tab='settings';U.view=null})", '[data-zk="log"]', 'settings|log'),
        ('the Start session capsule', "go(()=>{U.tab='today';U.view=null})", '[data-zk="start"]', 'today|found'),
        ('the Song practice card', "X=null;saveDraft();go(()=>{U.tab='today';U.view=null})", '[data-zk="songStart"]', 'today|song'),
    ]
    for name, to, card, dest in CASES:
        pg.evaluate(to)
        quiet(pg)
        back_to = where(pg)
        pg.locator(card).first.scroll_into_view_if_needed()
        pg.wait_for_timeout(150)
        pg.locator(card).first.click()
        y0 = pg.evaluate("ZOOM.stack().slice(-1)[0].y")  # where the list was at the tap (the click may scroll to reach it)
        ok(pg.locator('.zm').count() == 1 and pg.locator('.zm .zm-ghost').count() == 1, f'{name}: tapping it starts a zoom from the card')
        ok(pg.locator('.zm .zm-under .zm-hid').count() == 1, f'{name}: the card leaves its place in the list while its copy grows')
        pg.wait_for_function(GROWING, timeout=5000)
        ok(pg.evaluate("[...document.querySelectorAll('.zm *')].flatMap(e=>e.getAnimations()).every(a=>Object.keys(a.effect.getKeyframes()[0]).every(k=>['offset','easing','composite','computedOffset','transform','opacity'].includes(k)))"),
           f'{name}: the zoom moves transforms and opacity only')
        quiet(pg)
        ok(where(pg) == dest and pg.evaluate(CLEAN), f'{name}: opens {dest} and the zoom clears away')
        pg.click(BACK)
        k = pg.evaluate("ZOOM.busy()&&document.querySelector('#app .zm-src')?document.querySelector('#app .zm-src').dataset.zk:''")
        ok(k and pg.locator('#app ' + card.replace('.dash ', '')).first.get_attribute('data-zk') == k,
           f'{name}: Back shrinks the page into the same card (hidden until the page lands on it)')
        quiet(pg)
        ok(where(pg) == back_to and pg.evaluate(CLEAN), f'{name}: back on {back_to}, the card is shown again and nothing is left over')
        ok(abs(pg.evaluate("scrollY") - y0) < 2, f'{name}: the list is where it was ({y0:.0f}px down)')
    ok(pg.evaluate("document.querySelector('#dock .tabbar')&&!document.querySelector('#dock .tabbar.min')") is not False,
       'putting the scroll back doesn\'t shrink the tab bar')
    # the arch zooms into Progress (a tab, so there is no Back to shrink it again)
    pg.evaluate("go(()=>{U.tab='today';U.view=null})")
    quiet(pg)
    pg.click('[data-zk=goal]')
    ok(pg.locator('.zm').count() == 1, 'the weekly goal arch zooms into Progress')
    quiet(pg)
    ok(where(pg) == 'history|' and pg.evaluate("U.range") == 'W' and pg.evaluate(CLEAN), 'landing on this week, with nothing left over')
    pg.click('[data-a=tab][data-v=today]')
    ok(pg.locator('.zm').count() == 0 and pg.evaluate("ZOOM.stack().length") == 0, 'tapping a tab never zooms, and forgets the way back')
    pg.context.close()


def interrupt(b, t):
    """Back in the middle of a zoom reverses it from wherever it is."""
    ok = t.ok
    pg = page(b, t)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    quiet(pg)
    for wait, label in ((0, 'straight away'), (150, 'part way'), (900, 'nearly there')):
        pg.click('[data-zk="ex:rung"]')
        pg.wait_for_timeout(wait)
        pg.click(BACK)
        ok(pg.locator('.zm').count() == 1, f'Back {label}: the same zoom turns round (one layer, not two)')
        quiet(pg)
        ok(where(pg) == 'exercises|' and pg.evaluate(CLEAN) and pg.evaluate("ZOOM.stack().length") == 0,
           f'Back {label}: back on Exercises with no stray page, copy or hidden card')
    # tapping another tab mid-zoom just clears it
    pg.click('[data-zk="ex:rung"]')
    pg.wait_for_timeout(100)
    pg.click('#dock [data-a=tab][data-v=today]', force=True)
    quiet(pg)
    ok(where(pg) == 'today|' and pg.evaluate(CLEAN), 'switching tabs mid-zoom leaves nothing behind')
    # scrolling mid-zoom finishes it at once
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    quiet(pg)
    pg.click('[data-zk="ex:rung"]')
    pg.wait_for_timeout(80)
    pg.evaluate("scrollTo(0,200)")
    pg.wait_for_timeout(150)
    ok(pg.evaluate(CLEAN) and where(pg) == 'exercises|ex', 'scrolling during a zoom finishes it straight away, on the page')
    pg.context.close()


def swipes(b, t):
    """Swipe back from anywhere: follows the finger, closes past the threshold or on a flick, springs back below it."""
    ok = t.ok
    pg = page(b, t)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    quiet(pg)
    pg.click('[data-zk="ex:rung"]')
    quiet(pg)
    # held part way: the page is lifted and follows the finger, smaller as it goes
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 120, 'y': 500}]})
    for i in range(1, 7):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 120 + 10 * i, 'y': 502}]})
        pg.wait_for_timeout(16)
    lifted = pg.evaluate("(()=>{const w=document.querySelector('.zm .zm-win');return w&&document.querySelector('.zm .zm-shade')?getComputedStyle(w).transform:''})()")
    ok(lifted.startswith('matrix(0.9'), 'mid-swipe the page follows the finger, a little smaller, with a soft shadow')
    ok(pg.locator('.zm .zm-under .zm-shot').count() == 1, 'with the screen it came from shown underneath')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    cdp.detach()
    quiet(pg)
    ok(where(pg) == 'exercises|ex' and pg.evaluate(CLEAN), 'let go below the threshold: it springs back and stays')
    # far enough: closes into its card
    drag(pg, 60, 500, 300, 505, steps=12, ms=16)
    ok(where(pg) == 'exercises|', 'past the threshold: it goes back')
    quiet(pg)
    ok(pg.evaluate(CLEAN), 'shrinking into its card, with nothing left over')
    # a quick flick, not far: also closes
    pg.click('[data-zk="ex:rung"]')
    quiet(pg)
    drag(pg, 100, 400, 170, 400, steps=3, ms=0)
    quiet(pg)
    ok(where(pg) == 'exercises|', 'a quick flick goes back even before the threshold')
    # gesture priority: a row's own swipe, a segmented control, a sheet
    pg.click('[data-zk="ex:rung"]')
    quiet(pg)
    seg = pg.locator('#app .seg').first.bounding_box()
    drag(pg, seg['x'] + 20, seg['y'] + seg['height'] / 2, seg['x'] + 260, seg['y'] + seg['height'] / 2)
    quiet(pg)
    ok(where(pg) == 'exercises|ex', 'a swipe that starts on a segmented control isn\'t a swipe back')
    pg.click(BACK)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='history';U.view=null})")
    quiet(pg)
    pg.click('[data-zk="all:sessions"]')
    quiet(pg)
    row = pg.locator('#app .sw').first.bounding_box()
    drag(pg, row['x'] + 30, row['y'] + row['height'] / 2, row['x'] + 290, row['y'] + row['height'] / 2)
    quiet(pg)
    ok(where(pg) == 'history|all', 'a swipe that starts on a row with its own swipe (delete) isn\'t a swipe back')
    h1 = pg.locator('#app h1').bounding_box()
    drag(pg, h1['x'] + 10, h1['y'] + h1['height'] / 2, h1['x'] + 270, h1['y'] + h1['height'] / 2)
    quiet(pg)
    ok(where(pg) == 'history|', 'the same swipe on the page around it (the title) goes back')
    pg.click('[data-zk="all:sessions"]')
    quiet(pg)
    pg.evaluate("U.sheet='session';U.sd={k:'s2'};rerender()")
    quiet(pg)
    drag(pg, 40, 300, 300, 300)
    quiet(pg)
    ok(where(pg) == 'history|all' and pg.evaluate("U.sheet") == 'session', 'with a sheet open, nothing swipes back')
    pg.evaluate("U.sheet=null;rerender()")
    # a vertical swipe scrolls, never goes back
    drag(pg, 100, 600, 130, 300)
    ok(where(pg) == 'history|all', 'swiping up the page scrolls it')
    # pages without a card: a step of the session goes back a step, the page fading away
    pg.evaluate("go(()=>{U.tab='today';U.view=null})")
    quiet(pg)
    pg.click('[data-zk=start]')
    quiet(pg)
    pg.evaluate("FOUND.forEach(e=>X.f[e.id]=2);X.fEnd=Date.now();saveDraft();go(()=>{U.view='rot'})")
    quiet(pg)
    drag(pg, 40, 400, 300, 400)
    quiet(pg)
    ok(where(pg) == 'today|found' and pg.evaluate(CLEAN), 'swiping back on Rotation goes back to Foundation')
    drag(pg, 40, 400, 300, 400)
    quiet(pg)
    ok(where(pg) == 'today|' and pg.evaluate(CLEAN), 'and on Foundation back to Today, into the Resume session capsule')
    # Today has no Back: nothing happens
    drag(pg, 40, 400, 300, 400)
    ok(where(pg) == 'today|' and pg.locator('.zm').count() == 0, 'Today (no Back button) has no swipe back')
    pg.context.close()
    # motion off: no copies are drawn, but the swipe still goes back
    pg = page(b, t, init=None)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    pg.click('[data-zk="ex:rung"]')
    pg.evaluate("window._zm=0;new MutationObserver(m=>m.forEach(r=>r.addedNodes.forEach(n=>{if(n.classList&&n.classList.contains('zm'))window._zm++}))).observe(document.body,{childList:true})")
    drag(pg, 60, 500, 300, 505)
    ok(where(pg) == 'exercises|' and pg.evaluate("window._zm") == 0, 'motion off: the swipe goes back with nothing drawn')
    pg.context.close()


# the page's visible window (where its four corner boxes overlap) and its shadow layer, on screen
SHADE = """()=>{const z=document.querySelector('.zm'),sh=z&&z.querySelector('.zm-shade');if(!sh)return null;
  const rs=[...z.querySelectorAll('.zm-c')].map(e=>e.getBoundingClientRect());
  const w={l:Math.max(...rs.map(r=>r.left)),t:Math.max(...rs.map(r=>r.top)),r:Math.min(...rs.map(r=>r.right)),b:Math.min(...rs.map(r=>r.bottom))};
  const s=sh.getBoundingClientRect();return {w,s:{l:s.left,t:s.top,r:s.right,b:s.bottom},o:+getComputedStyle(sh).opacity}}"""


def shadow(b, t):
    """3.15.1 (Ivan's report): after a swipe back, the page's shadow shrinks with it into its card, frame by frame,
    instead of staying the size of the screen."""
    ok = t.ok
    pg = page(b, t, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    quiet(pg)
    pg.click('[data-zk="ex:slides"]')
    quiet(pg)
    for label, release in (('a swipe past the threshold', 30), ('a swipe let go early (springs back)', 7)):
        cdp = pg.context.new_cdp_session(pg)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 60, 'y': 500}]})
        for i in range(1, release // 3 + 2):
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 60 + 10 * i, 'y': 502}]})
            pg.wait_for_timeout(16)
        held = pg.evaluate(SHADE)
        ok(held and all(abs(held['w'][k] - held['s'][k]) < 2 for k in 'ltrb'), f'{label}: while held, the shadow is the page\'s size')
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        cdp.detach()
        pg.evaluate("()=>{window._an=document.getAnimations().filter(a=>a.effect.getTiming().iterations!==Infinity);window._an.forEach(a=>a.pause())}")
        d = pg.evaluate("MOTION.dur('nav')")
        off = []
        for f in (0, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0):
            pg.evaluate(AT, round(d * f))
            r = pg.evaluate(SHADE)
            if r and r['o'] > 0.02:
                gap = max(abs(r['w'][k] - r['s'][k]) for k in 'ltrb')
                if gap > 2: off.append((round(f, 2), round(gap)))
        pg.evaluate(PLAY)
        quiet(pg)
        ok(not off, f'{label}: once let go, the shadow stays the size of the page at every frame' + (f' (off by px at {off})' if off else ''))
        if release == 30:
            ok(where(pg) == 'exercises|' and pg.evaluate(CLEAN), 'and it lands in its card with nothing left over')
            pg.click('[data-zk="ex:slides"]')
            quiet(pg)
        else:
            ok(where(pg) == 'exercises|ex' and pg.evaluate(CLEAN), 'and it settles back on the page with nothing left over')
    # catching a page while it's still opening: the shadow starts at the page's size there and then
    pg.click(BACK)
    quiet(pg)
    pg.click('[data-zk="ex:slides"]')
    pg.wait_for_timeout(90)
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 200, 'y': 600}]})
    for i in range(1, 4):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 200 + 8 * i, 'y': 601}]})
        pg.wait_for_timeout(16)
    r = pg.evaluate(SHADE)
    ok(r is None or all(abs(r['w'][k] - r['s'][k]) < 2 for k in 'ltrb'), 'catching a page mid-open: its shadow matches the part-open page')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    cdp.detach()
    quiet(pg)
    ok(pg.evaluate(CLEAN), 'and nothing is left over')
    pg.context.close()


def frames(b, t):
    """Frame by frame, in dark mode: the window always shows the card's colour, the page or the card, never empty."""
    ok = t.ok
    pg = page(b, t, sc='dark', init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    quiet(pg)
    d = pg.evaluate("MOTION.dur('nav')")
    times = [round(d * f) for f in (0, 0.05, 0.1, 0.18, 0.26, 0.35, 0.45, 0.55, 0.7, 0.85, 1.0)]

    def watch(js, name):
        pg.evaluate(FREEZE, js)
        low = []
        for tt in times:
            pg.evaluate(AT, tt)
            c = pg.evaluate(COVER)
            if c is not None and c < 0.6:
                low.append((tt, round(c, 2)))
        pg.evaluate(PLAY)
        quiet(pg)
        ok(not low, f'{name}: the window is never an empty box' + (f' (thin at {low})' if low else ''))

    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    quiet(pg)
    watch("document.querySelector('[data-zk=\"ex:rung\"]').click()", 'dark, a row opening')
    watch("document.querySelector('" + BACK + "').click()", 'dark, a page closing into its row')
    pg.evaluate("go(()=>{U.tab='today';U.view=null})")
    quiet(pg)
    watch("document.querySelector('[data-zk=start]').click()", 'dark, Start session expanding')
    watch("document.querySelector('" + BACK + "').click()", 'dark, Foundation shrinking into Resume session')
    # a small card (under half the width) grows the whole page from a miniature
    pg.evaluate("go(()=>{U.tab='history';U.view=null})")
    quiet(pg)
    pg.evaluate("document.querySelector('[data-zk=\"all:sessions\"]').style.width='150px'")
    js = "document.querySelector('[data-zk=\"all:sessions\"]').click()"
    pg.evaluate(FREEZE, js)
    pg.evaluate(AT, round(d * 0.1))
    mini = pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('.zm-content')).transform;const m=/matrix\\(([\\d.]+)/.exec(c);return m?+m[1]:1})()")
    ok(mini < 0.5, f'a small card grows the page from a miniature (page at {mini:.2f} of its size early on)')
    g = pg.evaluate("(()=>{const g=document.querySelector('.zm-ghost');return g?getComputedStyle(g).transform:''})()")
    ok(g.startswith('matrix(') and float(g[7:].split(',')[0]) > 1.05, 'and the card itself scales up as it fades into the page')
    pg.evaluate(PLAY)
    quiet(pg)
    watch("document.querySelector('" + BACK + "').click()", 'dark, a page closing into a small card')
    pg.evaluate("go(()=>{U.tab='history';U.view=null})")
    quiet(pg)
    pg.evaluate("document.querySelector('[data-zk=\"all:sessions\"]').style.width='150px'")
    watch(js, 'dark, a small card opening')
    pg.context.close()


def capsules(b, t):
    """Start session expands into the session; Finish shrinks it back into Start session; song practice too."""
    ok = t.ok
    pg = page(b, t, data=daily())
    quiet(pg)
    pg.click('[data-zk=start]')
    tint = pg.evaluate("(()=>{const e=document.querySelector('.zm-tint');return e?getComputedStyle(e).backgroundColor:'no zoom'})()")
    ok(tint in ('rgb(0, 0, 0)',), f'the window starts in the capsule\'s black ({tint})')
    quiet(pg)
    ok(where(pg) == 'today|found', 'Start session expands into Foundation')
    ok(pg.locator('#dock .cta').count() == 1, 'with its own button in place of the tab bar')
    pg.evaluate("FOUND.forEach(e=>X.f[e.id]=2);X.fEnd=Date.now()-6e5;X.rot={rung:2};X.rEnd=Date.now()-3e5;X.start=Date.now()-9e5;saveDraft();go(()=>{U.view='app'})")
    quiet(pg)
    pg.click('#dock .cta')
    quiet(pg)
    pg.click('[data-a=saveHow]')
    ok(pg.locator('.zm').count() == 1 and pg.locator('#app [data-zk=start].zm-src').count() == 1,
       'Finish: the session shrinks back into Start session (hidden until it lands)')
    quiet(pg)
    ok(pg.evaluate(CLEAN) and pg.evaluate("U.sheet") == 'done' and where(pg) == 'today|', 'then the summary sheet is up over Today, nothing left over')
    pg.evaluate("closeSheet()")
    quiet(pg)
    # song practice from its card, then finishing shrinks into the same card
    pg.click('[data-zk=songStart]')
    quiet(pg)
    ok(where(pg) == 'today|song', 'the Song practice card zooms into song practice')
    pg.evaluate("X.song='g_1';X.start=Date.now()-6e5;X.takes=['t1'];saveDraft();rerender()")
    pg.click('#dock .cta')
    quiet(pg)
    pg.click('[data-a=saveHow]')
    ok(pg.locator('#app [data-zk=songStart].zm-src').count() == 1, 'finishing song practice shrinks back into its card')
    quiet(pg)
    ok(pg.evaluate(CLEAN) and pg.evaluate("U.sheet") == 'songDone', 'then its summary sheet shows')
    pg.context.close()


def calendar(b, t):
    ok = t.ok
    pg = page(b, t, sc='dark', data=daily())
    quiet(pg)
    pg.click('.titlerow [data-a=openCal]')
    quiet(pg)
    pg.click('.cal button.p >> nth=2')
    ok(pg.locator('#layer .zm-day').count() == 1, 'tapping a day: the day grows towards its sessions and fades')
    ok(pg.evaluate("document.querySelector('[data-zday]').getAnimations().some(a=>'transform' in a.effect.getKeyframes()[0])"),
       'and the day\'s sessions grow out of it (small-card zoom)')
    quiet(pg)
    ok(pg.locator('#layer .zm-day').count() == 0 and pg.locator('[data-zday] .row').count() >= 1, 'then the sessions are listed and the copy is gone')
    pg.context.close()


def new_song(b, t):
    ok = t.ok
    pg = page(b, t)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})")
    quiet(pg)
    pg.click('[data-a=sgNew]')
    quiet(pg)
    pg.fill('#sgTitle', 'River song')
    pg.fill('#sgLyr', LYR)
    pg.click('[data-a=sgSplit]')
    quiet(pg)
    pg.click('[data-a=sgSave]')
    ok(pg.locator('.zm.top').count() == 1 and pg.locator('#layer .sheet').count() == 0, 'saving: the paste sheet shrinks (a copy, the real one is gone)')
    k = pg.evaluate("(document.querySelector('#app .zm-src')||{dataset:{}}).dataset.zk")
    ok(bool(k) and k == 'sg:' + pg.evaluate("D.songs.find(s=>s.name==='River Song').id"), 'into the new song\'s row in Songs')
    pg.wait_for_function("U.view==='lyr'&&!ZOOM.busy()", timeout=30000)
    quiet(pg)
    ok(pg.evaluate("songById(U.songId).name") == 'River Song' and pg.evaluate(CLEAN), 'then the row opens the new song')
    ok(pg.evaluate("ZOOM.stack().map(e=>e.key).join()") == k, 'and Back will shrink it into that row')
    pg.context.close()


def reduce(b, t):
    """Reduce Motion: the zoom is a cross-fade, and a swipe back moves sideways only."""
    ok = t.ok
    pg = page(b, t, ctx_args={'reduced_motion': 'reduce'})
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    quiet(pg)
    pg.click('[data-zk="ex:rung"]')
    pg.wait_for_function("document.querySelector('.zm')&&document.querySelector('.zm .zm-win').getAnimations().length>0", timeout=5000)
    keys = pg.evaluate("[...document.querySelectorAll('.zm, .zm *')].flatMap(e=>e.getAnimations()).flatMap(a=>Object.keys(a.effect.getKeyframes()[0])).filter(k=>!['offset','easing','composite','computedOffset'].includes(k))")
    ok(keys and set(keys) == {'opacity'}, f'Reduce Motion: opening is a fade, nothing grows ({sorted(set(keys))})')
    quiet(pg)
    ok(where(pg) == 'exercises|ex' and pg.evaluate(CLEAN), 'and lands on the page')
    pg.click(BACK)
    keys = pg.evaluate("[...document.querySelectorAll('.zm, .zm *')].flatMap(e=>e.getAnimations()).flatMap(a=>Object.keys(a.effect.getKeyframes()[0])).filter(k=>!['offset','easing','composite','computedOffset'].includes(k))")
    ok(set(keys) <= {'opacity'}, 'closing is a fade too')
    quiet(pg)
    ok(where(pg) == 'exercises|' and pg.evaluate(CLEAN), 'back on Exercises')
    pg.click('[data-zk="ex:rung"]')
    quiet(pg)
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 100, 'y': 500}]})
    for i in range(1, 6):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 100 + 12 * i, 'y': 501}]})
        pg.wait_for_timeout(16)
    tf = pg.evaluate("getComputedStyle(document.querySelector('.zm .zm-win')).transform")
    ok(tf.startswith('matrix(1, 0, 0, 1, 60'), f'a swipe back follows the finger sideways only, no shrinking ({tf})')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    cdp.detach()
    quiet(pg)
    ok(where(pg) == 'exercises|ex' and pg.evaluate(CLEAN), 'and it settles back')
    pg.context.close()


def motion_off(b, t):
    """The tests' default: nothing drawn, but Back still returns to where the list was."""
    ok = t.ok
    pg = page(b, t, init=None)
    pg.evaluate("window._zm=0;new MutationObserver(m=>m.forEach(r=>r.addedNodes.forEach(n=>{if(n.classList&&n.classList.contains('zm'))window._zm++}))).observe(document.body,{childList:true})")
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})")
    pg.locator('[data-zk="sg:g_x1"]').scroll_into_view_if_needed()
    y0 = pg.evaluate("scrollY")
    pg.click('[data-zk="sg:g_x1"]')
    ok(where(pg) == 'songs|lyr' and pg.evaluate("scrollY") == 0, 'motion off: the song opens at the top')
    pg.click(BACK)
    ok(where(pg) == 'songs|' and abs(pg.evaluate("scrollY") - y0) < 2 and y0 > 50, f'Back returns to where the list was ({y0:.0f}px down)')
    ok(pg.evaluate("window._zm") == 0, 'and nothing was drawn for it')
    pg.context.close()


def sizes(b, t):
    """Every layout: a zoom in and out leaves nothing behind."""
    ok = t.ok
    for w, h, sc in ((390, 844, 'light'), (852, 393, 'dark'), (820, 1180, 'light'), (1440, 900, 'dark')):
        pg = page(b, t, w=w, h=h, sc=sc)
        quiet(pg)
        pg.evaluate("go(()=>{U.tab='settings';U.view=null})")
        quiet(pg)
        pg.click('[data-zk=log]')
        quiet(pg)
        a = where(pg)
        pg.click(BACK)
        quiet(pg)
        ok(a == 'settings|log' and where(pg) == 'settings|' and pg.evaluate(CLEAN), f'{w}×{h} {sc}: Changelog zooms open and closes cleanly')
        pg.evaluate("go(()=>{U.tab='today';U.view=null})")
        quiet(pg)
        pg.click('[data-zk="sg:g_1"]')
        quiet(pg)
        ok(pg.evaluate("U.songId") == 'g_1' and pg.evaluate(CLEAN), f'{w}×{h} {sc}: a pinned song opens (a page, or the Songs split view)')
        ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{w}×{h} {sc}: no sideways scroll')
        pg.context.close()


def run(b, t):
    cards(b, t)
    interrupt(b, t)
    swipes(b, t)
    shadow(b, t)
    frames(b, t)
    capsules(b, t)
    calendar(b, t)
    new_song(b, t)
    reduce(b, t)
    motion_off(b, t)
    sizes(b, t)
