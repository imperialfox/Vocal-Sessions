"""3.12 the floating window: a running session or a playing take stays in sight on every other screen. Its clock,
pausing from it, going back to exactly where you were, a take winning over a session, dragging and throwing it to a
corner (remembered after a reload), where it hides, and every size in light and dark."""
from harness import with_song_practice, SP
from test_layout import SIZES
from test_sections import LYR, ADD

LAUNCH_ARGS = ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']

SHOWN = "(()=>{const f=document.getElementById('fw');return !!f&&!f.hidden&&!!FW.shown})()"
TEXT = "(()=>{const f=document.getElementById('fw');return f?f.querySelector('.fwk').textContent+' | '+f.querySelector('.fwt').textContent:''})()"
RECT = "(()=>{const r=document.getElementById('fw').getBoundingClientRect();return {l:r.left,t:r.top,r:r.right,b:r.bottom,w:r.width,h:r.height}})()"
# where the corner should be, and the room the window has
SPOT = "c=>{const p=fwCornerXY(c),B=fwBounds();return {x:p.x,y:p.y,B}}"
# what the window must stay clear of: the tab bar or dock button, the top bar, the sidebar and Recall's hint capsule
CLEAR = """(()=>{const f=document.getElementById('fw').getBoundingClientRect(),hit=[];
 const over=(a,b)=>a.left<b.right-0.5&&a.right>b.left+0.5&&a.top<b.bottom-0.5&&a.bottom>b.top+0.5;
 [['the tab bar','#dock .tabbar'],['the dock','#dock .cta'],['the hint capsule','#dock .hcap'],['the top bar','#bar'],['the sidebar','#side']].forEach(([n,s])=>{
   const e=document.querySelector(s);if(e&&e.offsetParent!==null&&getComputedStyle(e).display!=='none'&&over(f,e.getBoundingClientRect()))hit.push(n)});
 if(f.left<0||f.top<0||f.right>innerWidth+0.5||f.bottom>innerHeight+0.5)hit.push('the screen edge');
 return hit})()"""


# leaving a step the way the sidebar, top tabs or a keyboard shortcut do (iPhone goes back through Foundation)
LEAVE = "go(()=>{U.view=null;U.tab='today'})"


def drag(pg, x0, y0, x1, y1, steps=12, ms=16):
    """A real one-finger drag, sent the way a touchscreen sends it."""
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}]})
    for i in range(1, steps + 1):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + (x1 - x0) * i / steps, 'y': y0 + (y1 - y0) * i / steps}]})
        pg.wait_for_timeout(ms)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    pg.wait_for_timeout(400)
    cdp.detach()


def centre(pg):
    r = pg.evaluate(RECT)
    return r['l'] + r['w'] / 2, r['t'] + 22


def at_corner(pg, c):
    r, s = pg.evaluate(RECT), pg.evaluate(SPOT, c)
    return abs(r['l'] - s['x']) < 1.5 and abs(r['t'] - s['y']) < 1.5


def session(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    ok(not pg.evaluate(SHOWN), 'no window with nothing going')
    pg.click('[data-a=start]'); pg.wait_for_timeout(200)
    ok(not pg.evaluate(SHOWN), 'no window on the session’s own screen')
    pg.evaluate("X.fEnd=Date.now();X.fE=1;saveDraft();go(()=>{U.view='rot'})")
    pg.evaluate("document.getElementById('app').style.paddingBottom='1400px'")  # room to scroll Rotation
    pg.evaluate("scrollTo(0,320)"); pg.wait_for_timeout(250)
    pg.evaluate(LEAVE); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.tab") == 'today' and pg.evaluate(SHOWN), 'leaving the session shows the window on Today')
    ok(pg.evaluate("FW.shown") == 'session' and pg.evaluate(TEXT).startswith('Focused session · Rotation |'),
       'it says what’s running: Focused session · Rotation')
    t1 = pg.evaluate(TEXT); pg.wait_for_timeout(2100)
    ok(pg.evaluate(TEXT) != t1, 'its time ticks')
    ok(pg.evaluate(CLEAR) == [], 'it sits clear of the tab bar and the top bar')
    ok(at_corner(pg, 'br'), 'it starts in the bottom right corner')
    t.shot(pg, 'today')
    for name, js in [('Songs', "go(()=>{U.tab='songs';U.view=null})"), ('Settings', "go(()=>{U.tab='settings';U.view=null})"),
                     ('Progress', "go(()=>{U.tab='history';U.view=null})")]:
        pg.evaluate(js); pg.wait_for_timeout(250)
        ok(pg.evaluate(SHOWN) and pg.evaluate("FW.shown") == 'session', f'and on {name}')
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); pg.wait_for_timeout(200)

    # pause and play from the window, without leaving the page
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("X.paused") and pg.evaluate("U.tab") == 'songs' and not pg.evaluate("U.view"), 'its button pauses the session and stays on Songs')
    p1 = pg.evaluate(TEXT)
    ok('| Paused · ' in p1 and pg.locator('#fw [data-a=fwToggle][aria-label=Play]').count() == 1, 'it says Paused, with a play button')
    pg.wait_for_timeout(1300)
    ok(pg.evaluate(TEXT) == p1, 'and the time stops')
    t.shot(pg, 'paused')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    ok(not pg.evaluate("X.paused") and 'Paused' not in pg.evaluate(TEXT), 'tapping it again carries on')

    # a sheet hides it
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(200)
    pg.click('.titlerow [data-a=openCal]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.sheet") == 'calendar' and not pg.evaluate(SHOWN), 'it hides while a sheet is open')
    pg.click('.scrim .ghost'); pg.wait_for_timeout(300)
    ok(pg.evaluate(SHOWN), 'and comes back when it closes')

    # back to exactly where you were
    pg.click('#fw .fwopen'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'rot', 'tapping it goes back to Rotation')
    ok(abs(pg.evaluate("scrollY") - 320) < 2, 'at the same scroll')
    ok(not pg.evaluate(SHOWN), 'and it’s gone on its own screen')
    pg.evaluate("scrollTo(0,140)"); pg.wait_for_timeout(250)
    pg.evaluate(LEAVE); pg.wait_for_timeout(250)
    ok(pg.locator('[data-a=resume]').count() >= 1, 'Today’s Resume button is still another way back')
    pg.click('#fw .fwopen'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'rot' and abs(pg.evaluate("scrollY") - 140) < 2, 'it remembers the newest scroll')
    pg.evaluate(LEAVE); pg.wait_for_timeout(250)

    # drag to each corner; it snaps there
    for c, (fx, fy) in [('tl', (0.15, 0.2)), ('tr', (0.85, 0.2)), ('bl', (0.15, 0.75)), ('br', (0.85, 0.75))]:
        x, y = centre(pg)
        drag(pg, x, y, 390 * fx, 844 * fy)
        ok(pg.evaluate("FW.corner") == c and at_corner(pg, c), f'dragged to the {c} corner, it snaps there')
        ok(pg.evaluate("U.view") is None, 'dragging doesn’t open it')
    # a quick flick goes to the corner it's thrown towards, though it's let go of before halfway up
    x, y = centre(pg)
    drag(pg, x, y, x - 150, y - 150, steps=3, ms=0)
    ok(pg.evaluate("FW.corner") == 'tl' and at_corner(pg, 'tl'), 'a quick flick up and left lands in the top left')
    x, y = centre(pg)
    drag(pg, x, y, x + 20, y + 14, steps=12, ms=40)  # (3.23: the corners sit 21 pt in on iPhone, a little closer)
    ok(pg.evaluate("FW.corner") == 'tl', 'a slow short drag springs back to its corner')
    ok(pg.evaluate(CLEAR) == [], 'in the top corner it stays below the top bar')
    t.shot(pg, 'top-left')
    pg.reload()
    pg.wait_for_function("!document.getElementById('splash')&&!LAUNCH.busy()", timeout=8000); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.corner") == 'tl' and pg.evaluate(SHOWN) and at_corner(pg, 'tl'), 'the corner is remembered after a reload')
    ok('vocalWindow' not in pg.evaluate("JSON.stringify(Object.keys(D))"), 'and it isn’t part of the saved data')
    pg.click('#fw .fwopen'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'rot', 'after a reload it still goes back to the session')

    # with motion on, it springs in and out
    pg.evaluate("MOTION.setSpeed(1)")
    pg.evaluate(LEAVE); pg.wait_for_timeout(60)
    ok(pg.evaluate("document.getElementById('fw').getAnimations().length") >= 1, 'with motion on it springs in')
    pg.wait_for_timeout(1200)
    x, y = centre(pg)
    drag(pg, x, y, 330, 700, steps=6, ms=16)
    pg.wait_for_timeout(1500)
    ok(pg.evaluate("FW.corner") == 'br' and at_corner(pg, 'br') and not pg.evaluate("!!FW.stopSpring"), 'and its snap springs to the corner and settles')
    pg.click('#fw .fwopen'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.view") == 'rot', 'tapping still opens it with motion on')
    pg.wait_for_timeout(600)
    ok(pg.evaluate("document.getElementById('fw').hidden"), 'and it shrinks away')
    pg.evaluate("MOTION.setSpeed(0)")
    pg.context.close()


def takes(b, t):
    ok = t.ok
    pg = t.page(b, touch=True, ctx_args={'permissions': ['microphone']})
    # song practice: no window until its first take
    pg.evaluate(SP); pg.click('[data-a=song][data-k=g_1]'); pg.wait_for_timeout(200)
    pg.evaluate("go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(200)
    ok(not pg.evaluate(SHOWN), 'untimed song practice has no window')
    pg.evaluate(SP); pg.click('[data-a=song][data-k=g_1]')
    pg.click('[data-a=rec]'); pg.wait_for_timeout(300)
    ok(not pg.evaluate(SHOWN), 'no window while recording')
    pg.wait_for_timeout(3500); pg.click('[data-a=rec]'); pg.wait_for_function("TAKES.length===1", timeout=5000); pg.wait_for_timeout(300)
    pg.click('#barL [data-a=exit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'session' and pg.evaluate(TEXT).startswith('Song practice |'), 'once timed, song practice gets its window')
    pg.click('#fw .fwopen'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'song', 'which goes back to song practice')

    # a take playing: switch away and its window shows, winning over the session
    pg.click('[data-a=playTake] >> nth=0'); pg.wait_for_function("!!player&&!player.paused", timeout=3000)
    ok(not pg.evaluate(SHOWN), 'no window on the screen the take is playing from')
    pg.click('#barL [data-a=exit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'take', 'leaving with a take playing shows the take, not the session')
    ok(pg.evaluate(TEXT).startswith('Playing · Versace on the Floor · bridge |'), 'it says Playing and the song’s name')
    ok(pg.locator('#fw .fwp').count() == 1, 'with its progress')
    t.shot(pg, 'take')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("player.paused") and pg.evaluate("!!playingId") and pg.evaluate("U.tab") == 'today' and not pg.evaluate("U.view"),
       'its button pauses the take and stays on Today')
    ok(pg.evaluate(TEXT).startswith('Paused · ') and pg.evaluate("FW.shown") == 'take', 'it says Paused')
    c1 = pg.evaluate("player.currentTime"); pg.wait_for_timeout(500)
    ok(pg.evaluate("player.currentTime") == c1, 'and the take stays where it was')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_function("!!player&&!player.paused", timeout=3000)
    ok(pg.evaluate(TEXT).startswith('Playing · '), 'tapping again plays on')
    pg.click('#fw .fwopen'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'song' and pg.evaluate("!!player"), 'tapping it returns to the take, still playing')
    ok(pg.locator('#app [data-a=playTake][data-k="' + pg.evaluate("playingId") + '"] svg path[d^="M8 5"]').count() == 1,
       'where its own button shows it playing')
    pg.click('#barL [data-a=exit]'); pg.wait_for_timeout(250)
    pg.evaluate("player.dispatchEvent(new Event('ended'))"); pg.wait_for_timeout(250)
    ok(pg.evaluate("FW.shown") == 'session', 'when the take ends, the session’s window is back')
    pg.click('#fw .fwopen'); pg.wait_for_timeout(300)
    pg.click('[data-a=playTake] >> nth=0'); pg.wait_for_function("!!player&&!player.paused", timeout=3000)
    pg.click('[data-a=playTake] >> nth=0'); pg.wait_for_timeout(200)
    ok(not pg.evaluate("!!player"), 'its own button still stops a playing take')
    pg.evaluate("X=null;saveDraft();go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(200)
    ok(not pg.evaluate(SHOWN), 'nothing going, no window')

    # a section's take: played in its takes sheet, then the sheet closed and the tab switched
    pg.evaluate("U.tab='songs';render()")
    S = pg.evaluate(ADD, LYR); pg.wait_for_timeout(300)
    o1 = S['o'][0]; sec = f'.sgsec[data-o="{o1}"]'
    pg.click(sec + ' .sgl >> nth=0'); pg.wait_for_timeout(200)
    pg.click(sec + ' [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(300)
    ok(not pg.evaluate(SHOWN), 'no window while a section is recording')
    pg.wait_for_timeout(3200)
    pg.click('[data-a=sgStop]'); pg.wait_for_function("U.sheet==='sgTakes'", timeout=5000); pg.wait_for_timeout(300)
    pg.click('.sheet #tkPP'); pg.wait_for_function("!!player&&!player.paused", timeout=3000)
    ok(not pg.evaluate(SHOWN), 'no window over the takes sheet')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(300)
    ok(pg.evaluate("!!player&&!player.paused"), 'closing the takes sheet lets the take carry on')
    ok(pg.evaluate("FW.shown") == 'take' and pg.evaluate(TEXT).startswith('Playing · Verse'), 'with its window on the song, naming the section')
    pg.click('[data-a=tab][data-v=today]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'take', 'switching tab, the take’s window shows')
    pg.click('#fw .fwopen'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.sheet") == 'sgTakes' and pg.evaluate("U.sd.o") == o1,
       'tapping it goes back to the song with that section’s takes')
    pg.click('.sheet .tkr [data-a=tkPlay] >> nth=0'); pg.wait_for_timeout(200)
    ok(pg.evaluate("!!player&&player.paused"), 'pausing it there pauses it')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(250)
    ok(not pg.evaluate("!!player"), 'closing the sheet with it paused ends it')
    ok(not pg.evaluate(SHOWN), 'and the window goes')
    pg.context.close()


def sizes(b, t):
    ok = t.ok
    for name, w, h, touch in SIZES:
        for sc in (['light', 'dark'] if name in ('iphone', 'ipad', 'mac') else ['light']):
            pg = t.page(b, w=w, h=h, sc=sc, touch=touch)
            pg.evaluate("newSession();go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(300)
            ok(pg.evaluate(SHOWN) and pg.evaluate(CLEAR) == [], f'{name} {sc}: the window sits clear of everything, in the bottom right')
            ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{name} {sc}: no sideways scroll')
            for c in ['tl', 'bl', 'tr']:
                pg.evaluate("c=>{FW.corner=c;fwPlace()}", c)
                if pg.evaluate(CLEAR) != []: ok(False, f'{name} {sc}: the {c} corner overlaps ' + ', '.join(pg.evaluate(CLEAR)))
            pg.evaluate("FW.corner='br';fwPlace()")
            t.shot(pg, f'{name}-{sc}')
            # Recall's hint capsule
            pg.evaluate("go(()=>{U.tab='songs';U.view=null})")
            pg.evaluate(ADD, LYR); pg.wait_for_timeout(200)
            if pg.evaluate("U.view") != 'lyr' and pg.evaluate("!!songOpenInPane()") is False: pg.evaluate("go(()=>{U.view='lyr'})")
            pg.evaluate("U.sMode='recall';render()"); pg.wait_for_timeout(250)
            ok(pg.evaluate(SHOWN) and pg.evaluate(CLEAR) == [], f'{name} {sc}: in Recall it sits above the hint capsule')
            if name in ('iphone', 'mac'): t.shot(pg, f'{name}-{sc}-recall')
            pg.context.close()


def run(b, t):
    session(b, t)
    takes(b, t)
    sizes(b, t)
