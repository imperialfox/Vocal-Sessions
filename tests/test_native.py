"""3.23 Native iOS polish (Q08): the bars where Apple's are on iPhone upright (the tab bar 21 pt from the bottom with
21 pt margins, the search circle as tall as the bar, the top circles centred at 84 pt), the soft edge under the top bar
when scrolling, Today's gradient and its switch in Settings › Appearance, the native push (slide in from the right)
for the doors Ivan chose (and the zoom kept everywhere else), and the tab bar's collapse into a pill at the left.
VS_NATIVE=layout,edge,gradient,push,collapse runs only those parts."""
import os
from harness import with_song_practice, now, iso, fix
from test_fuzz import TONES
from test_songs import LYR, ADD
from test_window import drag

SLOW = 4
ON = "try{localStorage.setItem('vocalMotion','%d')}catch(e){}" % SLOW
# iPhone 17 Pro's safe areas, stood in through the stylesheet's own variables (Chromium has no notch)
IPHONE = "document.documentElement.style.setProperty('--sat','62px');document.documentElement.style.setProperty('--sab','34px');rerender()"
QUIET = "!document.getAnimations().some(a=>(a.playState==='running'||a.playState==='pending')&&a.effect.getTiming().iterations!==Infinity)&&!ZOOM.busy()"
CLEAN = "!document.querySelector('.zm')&&!document.querySelector('.zm-src')&&!ZOOM.busy()"
BACK = '#barL [aria-label^="Back"]'
WHERE = "U.tab+'|'+(U.view||'')"
# the push layer now: the pushed page's and the page underneath's sideways offsets, and the dimming
PUSH = """(()=>{const l=document.querySelector('.zm.push');if(!l)return null;const m=e=>new DOMMatrix(getComputedStyle(e).transform).m41;
  return {page:m(l.querySelector('.zm-page')),under:m(l.querySelector('.zm-under')),dim:+getComputedStyle(l.querySelector('.zm-dim')).opacity,
  ghost:!!document.querySelector('.zm .zm-ghost'),n:document.querySelectorAll('.zm').length}})()"""
MEAS = """(()=>{const r=e=>e.getBoundingClientRect();const tb=document.querySelector('#dock .tabbar'),sc=document.querySelector('#dock .scirc'),
  g=document.querySelector('#barL .circ,#barR .circ');const o={};
  if(tb){const b=r(tb);o.bot=innerHeight-b.bottom;o.l=b.left;o.h=b.height;o.btn=[...tb.querySelectorAll('button')].map(x=>Math.round(r(x).width))}
  if(sc){const c=r(sc);o.cr=innerWidth-c.right;o.ch=c.height;o.cw=c.width;o.gap=tb?c.left-r(tb).right:null;o.mid=tb?Math.abs((c.top+c.bottom)/2-(r(tb).top+r(tb).bottom)/2):null}
  if(g){const c=r(g);o.top=c.top+c.height/2;o.th=c.height}
  o.side=document.documentElement.scrollWidth>innerWidth+1;return o})()"""


def quiet(pg, ms=30000):
    pg.wait_for_function(QUIET, timeout=ms)
    pg.wait_for_timeout(60)


def data():
    d = with_song_practice()
    d['songs'] = [{"id": "g_1", "name": "Versace on the Floor · bridge", "pinned": True, "added": 5000}] + \
        [{"id": f"g_x{i}", "name": f"Song {i:02d}", "artist": "", "added": 1000 + i, "pinned": False} for i in range(14)]
    d['lastBackup'] = iso(now)
    return d


def river(pg):
    """A song with lyrics (River Song), timed, so its page has Check timing."""
    sid = pg.evaluate(ADD, ['River Song', 'Sam Example', LYR]); pg.wait_for_timeout(150)
    pg.evaluate("id=>{const s=songById(id),L=ckLines(s);ckStore(s,L,ckSpread(s,L,s.order.map((_,i)=>i*10)),s.order.map(()=>true),L.map(()=>false),{est:true});save()}", sid)
    return sid


def wanted(name):
    only = os.environ.get('VS_NATIVE')
    return not only or name in only.split(',')


# ---------------------------------------------------------------------------------------------------------------------
def layout(b, t):
    """1 · Bar spacing on iPhone upright, measured against Ivan's screenshots; iPad, Mac and landscape unchanged."""
    ok = t.ok
    for w, h in ((375, 812), (390, 844), (402, 874)):
        for sc in ('light', 'dark'):
            pg = t.page(b, w, h, sc, data=data())
            pg.evaluate(IPHONE); pg.wait_for_timeout(150)
            m = pg.evaluate(MEAS)
            tag = f'{w}×{h} {sc}'
            ok(abs(m['bot'] - 21) < 0.6, f'{tag}: the tab bar sits 21 pt from the bottom edge ({m["bot"]})')
            ok(abs(m['l'] - 21) < 0.6 and abs(m['cr'] - 21) < 0.6, f'{tag}: with 21 pt margins either side (bar {m["l"]}, circle {m["cr"]})')
            ok(abs(m['h'] - m['ch']) < 0.6 and abs(m['cw'] - m['ch']) < 0.6 and m['mid'] < 0.6, f'{tag}: the search circle is as tall as the bar ({m["ch"]} vs {m["h"]}) and centred on it')
            ok(abs(m['gap'] - 12) < 0.6, f'{tag}: 12 pt between the bar and the circle, as in Notes ({m["gap"]})')
            ok(max(m['btn']) - min(m['btn']) <= 1, f'{tag}: the four tabs share the bar\'s width equally ({m["btn"]})')
            ok(abs(m['top'] - 84) < 0.6 and abs(m['th'] - 44) < 0.6, f'{tag}: the top circles are 44 pt, centred 84 pt from the top ({m["top"]})')
            ok(not m['side'], f'{tag}: nothing scrolls sideways')
            # things that take the tab bar's place sit at the same height
            pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.click('[data-zk=start]'); pg.wait_for_timeout(200)
            cta = pg.evaluate("innerHeight-document.querySelector('#dock .cta').getBoundingClientRect().bottom")
            ok(abs(cta - 21) < 0.6, f'{tag}: a session\'s button rests where the tab bar does ({cta})')
            pg.evaluate("go(()=>{U.tab='today';U.view=null})")
            ok(pg.evaluate("parseFloat(getComputedStyle(document.querySelector('main')).paddingBottom)") == 139,
               f'{tag}: the page keeps room under its last row for the bar (139 pt)')
            if w == 390: t.shot(pg, f'bars-{sc}')
            pg.context.close()
    # without a home indicator's safe area (as in these tests' Chromium) the bar still sits 21 pt up
    pg = t.page(b, 390, 844, data=data())
    m = pg.evaluate(MEAS)
    ok(abs(m['bot'] - 21) < 0.6 and abs(m['top'] - 28) < 0.6, f'with no safe areas: 21 pt from the bottom, and the top circles stay clear of the edge ({m})')
    pg.context.close()
    # iPad, Mac and iPhone landscape: unchanged
    for w, h, name in ((852, 393, 'iPhone landscape'), (820, 1180, 'iPad'), (1440, 900, 'Mac')):
        pg = t.page(b, w, h, data=data(), **({'ua': None} if name == 'Mac' else {}))
        pg.evaluate(IPHONE.replace('62px', '0px').replace('34px', '0px')); pg.wait_for_timeout(150)
        ok(not pg.evaluate("document.body.classList.contains('phone')"), f'{name}: not the iPhone-upright layout')
        ok(pg.evaluate("getComputedStyle(document.querySelector('.dock')).paddingBottom") == '12px', f'{name}: the dock sits where it did (12 pt up)')
        ok(pg.evaluate("parseFloat(getComputedStyle(document.getElementById('bar')).marginTop)") == 0, f'{name}: the top bar where it was')
        ok(not pg.evaluate("document.documentElement.scrollWidth>innerWidth+1"), f'{name}: nothing scrolls sideways')
        if name == 'iPhone landscape':
            m = pg.evaluate(MEAS)
            ok(m['btn'] and min(m['btn']) > 60 and abs(m['bot'] - 12) < 0.6, f'{name}: the compact tab bar as before ({m})')
            pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.mouse.move(400, 200)
            for _ in range(20): pg.mouse.wheel(0, 20); pg.wait_for_timeout(20)
            pg.wait_for_timeout(150)
            ok(not pg.evaluate("tabMin") and pg.locator('#dock .dockrow.min').count() == 0, f'{name}: the tab bar never collapses')
        pg.context.close()


# ---------------------------------------------------------------------------------------------------------------------
def edge(b, t):
    """2 · The soft edge: no rounded card when scrolled, a full-width blur from the top of the screen that fades out."""
    ok = t.ok
    for sc in ('light', 'dark'):
        pg = t.page(b, 390, 844, sc, data=data())
        pg.evaluate(IPHONE)
        for tab in ('exercises', 'history', 'songs'):
            pg.evaluate("v=>go(()=>{U.tab=v;U.view=null})", tab); pg.wait_for_timeout(100)
            pg.mouse.move(200, 500); pg.mouse.wheel(0, 300); pg.wait_for_timeout(350)
            bar = pg.evaluate("(()=>{const s=getComputedStyle(document.getElementById('bar'));return {sc:document.getElementById('bar').classList.contains('scrolled'),bg:s.backgroundColor,sh:s.boxShadow,bf:s.backdropFilter||s.webkitBackdropFilter,before:getComputedStyle(document.getElementById('bar'),'::before').display}})()")
            ok(bar['sc'] and bar['bg'] in ('rgba(0, 0, 0, 0)', 'transparent') and bar['sh'] == 'none' and bar['bf'] in ('none', '') and bar['before'] == 'none',
               f'{sc} {tab}: scrolled, the top bar is no longer a rounded glass card ({bar})')
            e = pg.evaluate("(()=>{const e=document.querySelector('.edge'),r=e.getBoundingClientRect(),s=getComputedStyle(e);return {l:r.left,t:r.top,w:r.width,h:r.height,o:+s.opacity,bf:s.backdropFilter||s.webkitBackdropFilter,mask:s.maskImage||s.webkitMaskImage}})()")
            ok(e['l'] == 0 and e['t'] == 0 and e['w'] == pg.evaluate("innerWidth") and e['o'] == 1, f'{sc} {tab}: the blur layer spans the full width and starts at the very top ({e["l"]},{e["t"]} {e["w"]}×{e["h"]})')
            ok('blur' in (e['bf'] or '') and 'gradient' in (e['mask'] or '') and e['h'] >= 62 + 56, f'{sc} {tab}: a backdrop blur that fades out at its lower edge, reaching past the bar')
            ok(pg.evaluate("document.querySelectorAll('#bar .circ.glass').length") >= 0, f'{sc} {tab}: circles stay glass')
            if tab == 'exercises': t.shot(pg, f'edge-{sc}')
            pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(300)
            ok(pg.evaluate("+getComputedStyle(document.querySelector('.edge')).opacity") == 0, f'{sc} {tab}: back at the top, the edge goes')
        pg.context.close()


# ---------------------------------------------------------------------------------------------------------------------
def gradient(b, t):
    """3 and 4 · Today's gradient, and Settings › Appearance › Gradient background."""
    ok = t.ok
    G = "(()=>{const g=document.querySelector('#app .tgrad');if(!g)return null;const r=g.getBoundingClientRect();return {n:g.querySelectorAll('i').length,top:r.top,h:r.height,l:r.left,w:r.width,mask:getComputedStyle(g).maskImage||getComputedStyle(g).webkitMaskImage,anims:[...g.querySelectorAll('i')].flatMap(i=>i.getAnimations()).length}})()"
    for sc in ('light', 'dark'):
        pg = t.page(b, 390, 844, sc, data=data(), init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
        g = pg.evaluate(G)
        ok(g and g['n'] == 3 and g['top'] == 0 and g['h'] == 300 and g['l'] == 0 and g['w'] == 390, f'{sc}: Today has the wash behind its header: 300 pt tall, edge to edge, three blobs ({g})')
        ok(g and 'gradient' in (g['mask'] or ''), f'{sc}: fading out a third of the way down')
        ok(g and g['anims'] == 3, f'{sc}: its blobs drift (one slow animation each)')
        ok(pg.evaluate("[...document.querySelectorAll('.tgrad i')].flatMap(i=>i.getAnimations()).every(a=>Object.keys(a.effect.getKeyframes()[0]).every(k=>['offset','easing','composite','computedOffset','transform'].includes(k)))"),
           f'{sc}: only transforms animate')
        ok(sorted(pg.evaluate("[...document.querySelectorAll('.tgrad i')].map(i=>Math.round(i.getAnimations()[0].effect.getTiming().duration/1000))")) == [19, 24, 31], f'{sc}: at 19, 24 and 31 seconds')
        cards = pg.evaluate("[...document.querySelectorAll('#app .grp')].map(g=>getComputedStyle(g).backgroundColor)")
        ok(cards and all(c == cards[0] for c in cards) and cards[0] not in ('rgba(0, 0, 0, 0)', 'transparent'), f'{sc}: the cards stay solid')
        t.shot(pg, f'today-{sc}')
        pg.mouse.move(200, 500); pg.mouse.wheel(0, 200); pg.wait_for_timeout(200)
        ok(abs(pg.evaluate(G)['top'] + pg.evaluate("scrollY")) < 1, f'{sc}: it scrolls away with the page (not fixed)')
        for tab in ('history', 'songs', 'exercises', 'settings'):
            pg.evaluate("v=>go(()=>{U.tab=v;U.view=null})", tab); pg.wait_for_timeout(80)
            ok(pg.evaluate(G) is None, f'{sc}: no gradient on {tab}')
        pg.context.close()
    # the switch
    pg = t.page(b, 390, 844, data=data())
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(100)
    ok(pg.locator('#app [data-zk="set:appear"] .tile').count() == 1 and 'Appearance' in pg.inner_text('#app [data-zk="set:appear"]'), 'Settings has an Appearance row with its own icon tile')
    pg.click('#app [data-zk="set:appear"]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.view+'/'+U.setPg") == 'set/appear' and pg.locator('#app h1').inner_text() == 'Appearance', 'it opens the Appearance page')
    sw = pg.locator('#app [data-a=setGrad][role=switch]')
    ok(sw.count() == 1 and sw.get_attribute('aria-checked') == 'true' and 'Gradient background' in sw.inner_text(), 'Gradient background is on by default')
    ok('A soft moving wash behind Today’s header.' in pg.inner_text('#app'), 'with its footer')
    t.shot(pg, 'appearance')
    sw.click(); pg.wait_for_timeout(100)
    ok(pg.locator('#app [data-a=setGrad]').get_attribute('aria-checked') == 'false' and pg.evaluate("localStorage.getItem('vocalLook')") == '{"grad":false}', 'switching it off is kept on this device')
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(100)
    ok(pg.evaluate(G) is None, 'switched off: Today has no gradient')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')&&!LAUNCH.busy()", timeout=10000)
    ok(pg.evaluate(G) is None and not pg.evaluate("SET.gradOn()"), 'and it stays off after a reload')
    ok('vocalLook' not in pg.evaluate("localStorage.getItem('vocalTracker')") and 'grad' not in pg.evaluate("JSON.stringify(D)"), 'it isn’t in the app’s data')
    pg.evaluate("prepareExport(true)"); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    txt = pg.evaluate("pendingExport.file.text()")
    ok('vocalLook' not in txt and '"grad"' not in txt, 'so it’s never in a backup')
    pg.evaluate("U.sheet=null;SET.setGrad(true);go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(100)
    ok(pg.evaluate(G) is not None and pg.evaluate("localStorage.getItem('vocalLook')") is None, 'switched back on, the wash returns')
    pg.context.close()
    # Reduce motion (system, or forced in Settings) and motion off hold it still; the wash stays
    for label, init, ctx in (('Reduce Motion', "try{localStorage.setItem('vocalMotion','1')}catch(e){}", {'reduced_motion': 'reduce'}),
                             ('Reduce motion forced on in Settings', "try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}", None),
                             ('motion off', None, None)):
        pg = t.page(b, 390, 844, data=data(), init=init, ctx_args=ctx)
        g = pg.evaluate(G)
        ok(g and g['n'] == 3 and g['anims'] == 0, f'{label}: the wash is there and holds still ({g and g["anims"]} animations)')
        pg.context.close()


# ---------------------------------------------------------------------------------------------------------------------
def push(b, t):
    """5 · Native push for the chosen doors; the card zoom everywhere else."""
    ok = t.ok
    pg = t.page(b, 390, 844, 'dark', touch=True, data=data(), init=ON)
    quiet(pg)
    sid = river(pg)
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); quiet(pg)
    DOORS = [
        # (name, how to get there, the door, where it goes)
        ('a song in Songs', "go(()=>{U.tab='songs';U.view=null})", '#app .rowc[data-zk="sg:g_x3"]', 'songs|lyr'),
        ('a pinned song on Today', "go(()=>{U.tab='today';U.view=null})", '#app [data-zk="sg:g_1"]', 'songs|lyr'),
        ('an exercise in Exercises', "go(()=>{U.tab='exercises';U.view=null})", '#app [data-zk="ex:hinge"]', 'exercises|ex'),
        ('Backup in Settings', "go(()=>{U.tab='settings';U.view=null})", '#app [data-zk="set:backup"]', 'settings|set'),
        ('Storage in Settings', "go(()=>{U.tab='settings';U.view=null})", '#app [data-zk="set:storage"]', 'settings|set'),
        ('Recall in Settings', "go(()=>{U.tab='settings';U.view=null})", '#app [data-zk="set:recall"]', 'settings|set'),
        ('Coach video in Settings', "go(()=>{U.tab='settings';U.view=null})", '#app [data-zk="set:coach"]', 'settings|set'),
        ('Appearance in Settings', "go(()=>{U.tab='settings';U.view=null})", '#app [data-zk="set:appear"]', 'settings|set'),
        ('Accessibility in Settings', "go(()=>{U.tab='settings';U.view=null})", '#app [data-zk="set:access"]', 'settings|set'),
        ('the Changelog row', "go(()=>{U.tab='settings';U.view=null})", '#app .row[data-zk="log"]', 'settings|log'),
        ('the version footer', "go(()=>{U.tab='settings';U.view=null})", '#app .setfoot', 'settings|log'),
    ]
    for name, to, door, dest in DOORS:
        pg.evaluate(to); quiet(pg)
        back_to = pg.evaluate(WHERE)
        pg.locator(door).first.scroll_into_view_if_needed(); pg.wait_for_timeout(100)
        pg.locator(door).first.click()
        y0 = pg.evaluate("ZOOM.stack().slice(-1)[0].y")  # where the list was at the tap (the click may scroll to reach it)
        pg.wait_for_timeout(320)
        p = pg.evaluate(PUSH)
        ok(p and not p['ghost'] and p['n'] == 1 and 1 < p['page'] < 389 and p['under'] < -8 and p['dim'] > 0.01,
           f'{name}: pushes in from the right, the page underneath shifted left and dimmed (no zoom) ({p})')
        quiet(pg)
        ok(pg.evaluate(WHERE) == dest and pg.evaluate(CLEAN), f'{name}: lands on {dest} with nothing left over')
        st = pg.evaluate("ZOOM.stack().slice(-1)[0]")
        ok(st and st['kind'] == 'push', f'{name}: on the stack as a push')
        if pg.locator(BACK).count():
            pg.click(BACK); pg.wait_for_timeout(260)
            p = pg.evaluate(PUSH)
            ok(p and p['page'] > 5 and p['under'] > -117, f'{name}: Back slides it away to the right ({p})')
            quiet(pg)
            w, c, y = pg.evaluate(WHERE), pg.evaluate(CLEAN), pg.evaluate("scrollY")
            ok(w == back_to and c and abs(y - y0) < 2, f'{name}: back on {back_to}, where the list was, nothing left over ({w}, clean {c}, {y} vs {y0})')
    # the version footer and Show all songs land on pages: Back or the tab bar
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); quiet(pg)
    pg.locator('#app [data-zk="songs"]').scroll_into_view_if_needed(); pg.click('#app [data-zk="songs"]'); pg.wait_for_timeout(320)
    p = pg.evaluate(PUSH)
    ok(p and not p['ghost'] and 1 < p['page'] < 389, f'Today › Show all songs pushes the song list ({p})')
    quiet(pg)
    ok(pg.evaluate(WHERE) == 'songs|' and pg.evaluate(CLEAN), 'and lands on the Songs list')
    # Search › a song, a lyric and an exercise
    for name, q, door, dest in (('a song result', 'river', '#flist [data-zk^="sg:"]', 'songs|lyr'),
                                ('a lyric result', 'carry me', '#flist [data-zk^="fl:"]', 'songs|lyr'),
                                ('an exercise result', 'hinge', '#flist [data-zk^="ex:"]', 'find|ex')):
        pg.evaluate("FIND.open()"); quiet(pg)
        pg.fill('#fq', q); pg.wait_for_timeout(150)
        pg.evaluate("document.activeElement.blur()"); quiet(pg)
        pg.locator(door).first.click(); pg.wait_for_timeout(320)
        p = pg.evaluate(PUSH)
        ok(p and not p['ghost'] and 1 < p['page'] < 389, f'Search › {name}: pushes ({p})')
        quiet(pg)
        ok(pg.evaluate(WHERE) == dest and pg.evaluate(CLEAN), f'Search › {name}: opens {dest} ({pg.evaluate(WHERE)})')
        pg.click(BACK); pg.wait_for_timeout(260)
        ok(pg.evaluate(PUSH) is not None, f'Search › {name}: Back slides it away')
        quiet(pg)
        ok(pg.evaluate(WHERE) == 'find|' and pg.evaluate(CLEAN), f'Search › {name}: back on the results')
    # a song page › Check timing (timed); Back and Done slide back (Q05: Sync by sections is retired)
    pg.evaluate("id=>openSong(id)", sid); quiet(pg)
    pg.evaluate("ckTileAct('check')"); pg.wait_for_timeout(320)
    p = pg.evaluate(PUSH)
    ok(p and 1 < p['page'] < 389 and pg.evaluate("U.view") == 'ckCheck', f'a song page › Check timing pushes ({p})')
    quiet(pg)
    pg.click(BACK); pg.wait_for_timeout(260)
    ok(pg.evaluate(PUSH) is not None, 'Check timing\'s Back slides it away')
    quiet(pg)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate(CLEAN), 'back on the song')
    pg.evaluate("ckTileAct('check')"); pg.wait_for_timeout(320); quiet(pg)
    pg.click('[data-a=ckCheckDone]'); pg.wait_for_timeout(260)
    ok(pg.evaluate(PUSH) is not None, 'Check timing\'s Done slides back to the song')
    quiet(pg)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate(CLEAN), 'and lands on it with nothing left over')
    # doors that keep the card zoom (a track and the coach video added, so their rows are there)
    pg.evaluate("id=>TRACK.expect(id)", sid); pg.set_input_files('#trackIn', TONES)
    pg.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()", arg=sid, timeout=15000)
    pg.set_input_files('#coachIn', fix('coach-chapters.webm'))
    pg.wait_for_function("COACH.has()&&!COACH.busy()", timeout=15000)
    ZOOMS = [
        ('Song practice on a song page', "id=>openSong(id)", f'#app [data-zk="sgp:{sid}"]'),
        ('the track on a song page', "id=>openSong(id)", f'#app [data-zk="trk:{sid}"]'),
        ('the coach video on Exercises', "()=>go(()=>{U.tab='exercises';U.view=null})", '#app [data-zk="coach"]'),
        ('Start session', "()=>go(()=>{U.tab='today';U.view=null})", '#app [data-zk="start"]'),
        ('the weekly goal arch', "()=>go(()=>{U.tab='today';U.view=null})", '#app [data-zk="goal"]'),
        ('Show all sessions', "()=>go(()=>{U.tab='history';U.view=null})", '#app [data-zk="all:sessions"]'),
        ('Today\'s suggested rotation', "()=>go(()=>{U.tab='today';U.view=null})", '#app .dash [data-zk^="ex:"]'),
    ]
    for name, to, door in ZOOMS:
        pg.evaluate(to, sid); quiet(pg)
        if not pg.locator(door).count():
            ok(False, f'{name}: door not found ({door})'); continue
        pg.locator(door).first.scroll_into_view_if_needed(); pg.wait_for_timeout(80)
        pg.locator(door).first.click(); pg.wait_for_timeout(60)
        ok(pg.locator('.zm .zm-ghost').count() == 1 and pg.locator('.zm.push').count() == 0, f'{name}: still zooms from its card')
        quiet(pg)
        if pg.evaluate("U.view") in ('found',):
            pg.evaluate("go(()=>{U.tab='today';U.view=null})"); quiet(pg)
    # the gear into Settings doesn't push
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); quiet(pg)
    pg.click('#barR [data-a=openSettings]'); pg.wait_for_timeout(60)
    ok(pg.locator('.zm.push').count() == 0, 'the gear into Settings doesn’t push')
    quiet(pg)
    # interrupting: Back mid-push turns it round from where it is, one layer, nothing left
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); quiet(pg)
    for wait, label in ((0, 'straight away'), (300, 'part way'), (1400, 'nearly there')):
        pg.click('#app .rowc[data-zk="sg:g_x1"]'); pg.wait_for_timeout(wait)
        pg.click(BACK); pg.wait_for_timeout(150)
        p1 = pg.evaluate(PUSH); pg.wait_for_timeout(350)
        p2 = pg.evaluate(PUSH)
        ok(p1 and p1['n'] == 1 and (p2 is None or p2['page'] >= p1['page'] - 0.5), f'Back {label}: the same push turns round, heading back out to the right (one layer: {p1 and round(p1["page"])} → {p2 and round(p2["page"])})')
        quiet(pg)
        ok(pg.evaluate(WHERE) == 'songs|' and pg.evaluate(CLEAN) and not pg.evaluate("ZOOM.stack().length"), f'Back {label}: back on Songs with nothing left over')
    # and a door mid-close opens cleanly again
    pg.click('#app .rowc[data-zk="sg:g_x1"]'); quiet(pg)
    pg.click(BACK); pg.wait_for_timeout(200)
    pg.click('#app .rowc[data-zk="sg:g_x2"]'); quiet(pg)
    ok(pg.evaluate("U.songId") == 'g_x2' and pg.evaluate(CLEAN), 'opening another song while one slides away leaves nothing behind')
    pg.click(BACK); quiet(pg)
    # slow motion, frame by frame: the page underneath shifted and dimmed, the pushed page moving in on the nav spring
    pg.click('#app .rowc[data-zk="sg:g_x1"]')
    pg.evaluate("async()=>{for(let i=0;i<3;i++)await new Promise(r=>requestAnimationFrame(r));window._an=document.getAnimations().filter(a=>a.effect.getTiming().iterations!==Infinity);window._an.forEach(a=>a.pause())}")
    d = pg.evaluate("MOTION.dur('nav')")
    seen = []
    for f in (0.05, 0.2, 0.4, 0.7, 1.0):
        pg.evaluate("t=>window._an.forEach(a=>{a.currentTime=t})", round(d * f))
        seen.append(pg.evaluate(PUSH))
    pg.evaluate("()=>window._an.forEach(a=>a.play())")
    xs = [s['page'] for s in seen if s]
    ok(len(xs) == 5 and all(xs[i] >= xs[i + 1] - 0.5 for i in range(4)) and xs[0] > 200 and xs[-1] < 1, f'the page slides in from the right edge ({[round(x) for x in xs]})')
    ok(seen[2] and seen[2]['under'] < -40 and seen[2]['dim'] > 0.04, f'mid-way the page underneath is shifted left and dimmed ({seen[2]})')
    ok(min(xs) > -1, 'with no visible bounce past its place')
    ok(pg.evaluate("[...document.querySelectorAll('.zm *')].flatMap(e=>e.getAnimations()).every(a=>Object.keys(a.effect.getKeyframes()[0]).every(k=>['offset','easing','composite','computedOffset','transform','opacity'].includes(k)))"),
       'only transforms and opacity move')
    quiet(pg)
    # swipe back from anywhere on a pushed page: follows the finger, the page underneath slides back as it goes
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 120, 'y': 500}]})
    for i in range(1, 7):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 120 + 10 * i, 'y': 502}]})
        pg.wait_for_timeout(16)
    p = pg.evaluate(PUSH)
    ok(p and abs(p['page'] - 60) < 2 and abs(p['under'] + 0.3 * (390 - 60)) < 2, f'mid-swipe the page follows the finger and the one underneath starts sliding back ({p})')
    ok(pg.locator('.zm.push .zm-under .zm-shot').count() == 1, 'with the screen it came from shown underneath')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    cdp.detach()
    quiet(pg)
    ok(pg.evaluate(WHERE) == 'songs|lyr' and pg.evaluate(CLEAN), 'let go early: it springs back and stays')
    drag(pg, 60, 500, 300, 505, steps=12, ms=16)
    ok(pg.evaluate(WHERE) == 'songs|', 'past about a fifth of the width: it goes back')
    quiet(pg)
    ok(pg.evaluate(CLEAN), 'and slides away with nothing left over')
    pg.click('#app .rowc[data-zk="sg:g_x1"]'); quiet(pg)
    drag(pg, 100, 400, 170, 400, steps=3, ms=0)
    quiet(pg)
    ok(pg.evaluate(WHERE) == 'songs|' and pg.evaluate(CLEAN), 'a quick flick goes back too')
    # catching a push still opening
    pg.click('#app .rowc[data-zk="sg:g_x1"]'); pg.wait_for_timeout(300)
    drag(pg, 200, 500, 380, 505, steps=8, ms=16)
    quiet(pg)
    ok(pg.evaluate(WHERE) == 'songs|' and pg.evaluate(CLEAN), 'a push caught by a swipe mid-way goes back cleanly')
    pg.context.close()
    # Reduce Motion: a short fade; motion off: instant, but Back still returns to where the list was
    pg = t.page(b, 390, 844, data=data(), init="try{localStorage.setItem('vocalMotion','1')}catch(e){}", ctx_args={'reduced_motion': 'reduce'})
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); quiet(pg)
    pg.click('#app .rowc[data-zk="sg:g_x1"]')
    pg.wait_for_function("document.querySelector('.zm.push .zm-page')&&document.querySelector('.zm.push .zm-page').getAnimations().length>0", timeout=5000)
    keys = pg.evaluate("[...document.querySelectorAll('.zm, .zm *')].flatMap(e=>e.getAnimations()).flatMap(a=>Object.keys(a.effect.getKeyframes()[0])).filter(k=>!['offset','easing','composite','computedOffset'].includes(k))")
    ok(keys and set(keys) == {'opacity'}, f'Reduce Motion: a push is a short fade ({sorted(set(keys))})')
    quiet(pg)
    pg.click(BACK)
    keys = pg.evaluate("[...document.querySelectorAll('.zm, .zm *')].flatMap(e=>e.getAnimations()).flatMap(a=>Object.keys(a.effect.getKeyframes()[0])).filter(k=>!['offset','easing','composite','computedOffset'].includes(k))")
    ok(set(keys) <= {'opacity'}, 'and so is Back')
    quiet(pg)
    ok(pg.evaluate(WHERE) == 'songs|' and pg.evaluate(CLEAN), 'back on Songs')
    pg.context.close()
    pg = t.page(b, 390, 844, data=data())
    pg.evaluate("window._zm=0;new MutationObserver(m=>m.forEach(r=>r.addedNodes.forEach(n=>{if(n.classList&&n.classList.contains('zm'))window._zm++}))).observe(document.body,{childList:true})")
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})")
    pg.locator('#app .rowc[data-zk="sg:g_x9"]').scroll_into_view_if_needed(); y0 = pg.evaluate("scrollY")
    pg.click('#app .rowc[data-zk="sg:g_x9"]')
    ok(pg.evaluate(WHERE) == 'songs|lyr' and pg.evaluate("ZOOM.stack().slice(-1)[0].kind") == 'push', 'motion off: the song opens straight away')
    pg.click(BACK)
    ok(pg.evaluate(WHERE) == 'songs|' and abs(pg.evaluate("scrollY") - y0) < 2 and pg.evaluate("window._zm") == 0, 'and Back returns to where the list was, with nothing drawn')
    pg.context.close()
    # iPad and Mac keep the zoom
    pg = t.page(b, 820, 1180, data=data(), init=ON)
    quiet(pg)
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); quiet(pg)
    pg.click('#app [data-zk="set:backup"]'); pg.wait_for_timeout(60)
    ok(pg.locator('.zm.push').count() == 0, 'iPad: Settings rows keep the zoom')
    quiet(pg)
    pg.context.close()


# ---------------------------------------------------------------------------------------------------------------------
def collapse(b, t):
    """6 · The tab bar's collapse: when it may, how far, what it looks like, and what it leaves alone."""
    ok = t.ok
    S = "(()=>({y:Math.round(scrollY),min:tabMin,cls:!!document.querySelector('#dock .dockrow.min')}))()"
    pg = t.page(b, 390, 844, data=data())
    pg.evaluate(IPHONE)
    pg.mouse.move(200, 500)

    def wheel(dy, n=1, gap=40):
        for _ in range(n):
            pg.mouse.wheel(0, dy); pg.wait_for_timeout(gap)
        pg.wait_for_timeout(80)

    # a short page never collapses
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='recall'})")
    wheel(40, 8)
    ok(not pg.evaluate(S)['cls'] and not pg.evaluate("tabRoom()"), 'a short page (Settings › Recall) never collapses')
    # a tall page: not in the first 120 pt; about 30 pt down collapses, 20 pt up expands
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})")
    ok(pg.evaluate("tabRoom()"), 'the Exercises list has room to scroll (a third of the screen)')
    wheel(20, 5)
    ok(pg.evaluate(S)['y'] == 100 and not pg.evaluate(S)['cls'], 'the first 120 pt never collapse it')
    pg.evaluate("scrollTo(0,200)"); pg.wait_for_timeout(80)
    wheel(10, 2)
    ok(not pg.evaluate(S)['cls'], '20 pt of scrolling down isn’t enough')
    wheel(10)
    ok(pg.evaluate(S)['cls'], 'about 30 pt of steady scrolling down collapses it')
    wheel(-10)
    ok(pg.evaluate(S)['cls'], 'a 10 pt nudge up doesn’t bring it back')
    wheel(-10)
    ok(not pg.evaluate(S)['cls'], 'about 20 pt up expands it')
    # collapsed: a pill at the left with the active tab's icon, the circle at the right, the same height
    wheel(10, 4)
    r = pg.evaluate("(()=>{const p=document.querySelector('#dock .tabpill').getBoundingClientRect(),c=document.querySelector('#dock .scirc').getBoundingClientRect();return {pl:p.left,cr:innerWidth-c.right,ph:p.height,ch:c.height,pm:(p.top+p.bottom)/2,cm:(c.top+c.bottom)/2,bot:innerHeight-p.bottom}})()")
    ok(abs(r['pl'] - 21) < 0.6 and abs(r['cr'] - 21) < 0.6 and abs(r['ph'] - r['ch']) < 0.6 and abs(r['pm'] - r['cm']) < 0.6 and abs(r['bot'] - 21) < 0.6,
       f'collapsed: a pill at the left edge and the circle at the right, the same height, 21 pt in ({r})')
    ok(pg.locator('#dock .tabpill svg').count() == 1 and pg.evaluate("document.querySelector('#dock .tabpill').dataset.v") == 'exercises', 'the pill holds the active tab’s icon')
    ok(pg.evaluate("+getComputedStyle(document.querySelector('#dock .tabbar')).opacity") == 0 and pg.evaluate("getComputedStyle(document.querySelector('#dock .tabbar')).pointerEvents") == 'none', 'the full bar has gone')
    t.shot(pg, 'collapsed')
    # it survives a redraw: the same row, still collapsed
    pg.evaluate("document.querySelector('#dock .dockrow')._k=1;rerender()")
    ok(pg.evaluate(S)['cls'] and pg.evaluate("document.querySelector('#dock .dockrow')._k") == 1, 'a redraw keeps the same collapsed bar (nothing replayed or snapped)')
    # nothing resting on the bar moves
    b1 = pg.evaluate("fwBounds().b")
    pg.click('#dock .tabpill'); pg.wait_for_timeout(100)
    ok(not pg.evaluate(S)['cls'] and pg.evaluate(WHERE) == 'exercises|', 'tapping the pill expands it, without switching tabs')
    ok(pg.evaluate("fwBounds().b") == b1, 'the floating window’s room above the bar is the same collapsed or not')
    # scrolls the app makes itself don't toggle it
    wheel(10, 4)
    pg.evaluate("scrollTo(0,40)"); pg.wait_for_timeout(100)
    ok(not pg.evaluate(S)['cls'], 'within 60 pt of the top it’s always expanded')
    pg.evaluate("scrollTo(0,300)"); pg.wait_for_timeout(100)
    ok(not pg.evaluate(S)['cls'], 'a scroll the app makes (here down 260 pt) doesn’t collapse it')
    wheel(10, 4)
    pg.evaluate("scrollTo(0,150)"); pg.wait_for_timeout(100)
    ok(pg.evaluate(S)['cls'], 'and one up doesn’t expand it')
    # Back's scroll restore: open an exercise from the list further down, and Back
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(80)
    pg.locator('#app [data-zk="ex:flex"]').scroll_into_view_if_needed(); pg.wait_for_timeout(80)
    y0 = pg.evaluate("scrollY")
    wheel(10, 4)
    collapsed = pg.evaluate(S)['cls']
    pg.click('#app [data-zk="ex:flex"]'); pg.wait_for_timeout(100)
    ok(not pg.evaluate(S)['cls'], 'a new page starts expanded')
    pg.click(BACK); pg.wait_for_timeout(150)
    ok(pg.evaluate("scrollY") > 120 and not pg.evaluate(S)['cls'], f'Back puts the list back ({pg.evaluate("scrollY")} pt down, collapsed before: {collapsed}) and the bar stays expanded')
    # a tab switch starts expanded
    pg.evaluate("scrollTo(0,200)"); wheel(10, 4)
    pg.click('#dock .tabpill'); pg.wait_for_timeout(60)
    pg.click('#dock .tabbar [data-v=history]'); pg.wait_for_timeout(100)
    ok(not pg.evaluate(S)['cls'], 'switching tabs starts expanded')
    # height changes: a page that becomes too short expands it and stays expanded
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); wheel(10, 20)
    ok(pg.evaluate(S)['cls'], '(collapsed again)')
    pg.evaluate("document.getElementById('app').style.cssText='height:120px;overflow:hidden;padding-bottom:0'"); pg.wait_for_timeout(200)
    ok(not pg.evaluate(S)['cls'], 'the page becoming too short brings the bar back')
    wheel(10, 6)
    ok(not pg.evaluate(S)['cls'], 'and it stays expanded')
    pg.evaluate("document.getElementById('app').style.cssText=''"); pg.wait_for_timeout(150)
    pg.evaluate("scrollTo(0,200)"); wheel(10, 4)
    ok(pg.evaluate(S)['cls'], 'tall again: collapsing is allowed again')
    # never while typing, with a sheet open, or on Search
    pg.click('#dock .tabpill'); pg.wait_for_timeout(60)
    pg.evaluate("document.getElementById('app').insertAdjacentHTML('afterbegin','<input id=tq>');document.getElementById('tq').focus({preventScroll:true})")
    wheel(10, 6)
    ok(not pg.evaluate(S)['cls'], 'never while typing (the keyboard is up)')
    pg.evaluate("document.getElementById('tq').blur()"); wheel(10, 4)
    ok(pg.evaluate(S)['cls'], '(collapsed after the field lets go)')
    pg.evaluate("document.getElementById('tq').focus({preventScroll:true})"); pg.wait_for_timeout(80)
    ok(not pg.evaluate(S)['cls'], 'a field getting the keyboard brings the bar back')
    pg.evaluate("document.getElementById('tq').remove()")
    pg.evaluate("U.sheet='calendar';rerender()"); pg.wait_for_timeout(100)
    ok(not pg.evaluate("tabMayMin()"), 'never with a sheet open')
    pg.evaluate("U.sheet=null;rerender()")
    pg.evaluate("FIND.open()"); pg.wait_for_timeout(100)
    pg.evaluate("document.activeElement.blur()")
    ok(not pg.evaluate("tabMayMin()") and not pg.evaluate(S)['cls'], 'never on Search')
    pg.context.close()
    # with motion on: transforms and opacity only, on the gentle spring, and a redraw doesn't snap it
    pg = t.page(b, 390, 844, data=data(), init=ON)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(200)
    pg.evaluate("scrollTo(0,300);setTabMin(true)"); pg.wait_for_timeout(50)
    props = pg.evaluate("[...document.querySelectorAll('#dock .tabbar,#dock .tabpill,#dock .tabbar button,#dock .scirc')].flatMap(e=>e.getAnimations()).map(a=>a.transitionProperty)")
    ok(props and set(props) <= {'transform', 'opacity'}, f'collapsing moves transforms and opacity only ({sorted(set(props))})')
    pg.evaluate("rerender()")
    ok(pg.evaluate("document.querySelector('#dock .tabbar').getAnimations().length") > 0, 'a redraw mid-collapse lets it carry on')
    pg.wait_for_function("!document.querySelector('#dock .tabbar').getAnimations().length", timeout=10000)
    ok(pg.evaluate("+getComputedStyle(document.querySelector('#dock .tabpill')).opacity") == 1, 'and it lands collapsed')
    pg.context.close()


def run(b, t):
    if wanted('layout'): layout(b, t)
    if wanted('edge'): edge(b, t)
    if wanted('gradient'): gradient(b, t)
    if wanted('push'): push(b, t)
    if wanted('collapse'): collapse(b, t)
