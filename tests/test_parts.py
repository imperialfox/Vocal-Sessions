"""Q41 the parts kit: the pinned copy (unchanged, checked against its checksums), its settings (no problems, every
decision's line), the kit running the motion (D18: speed, slow motion and forced Reduce Motion reach the kit's parts and
the app's own animations, and survive a reload; only the kit writes the motion variables and classes), the list of
differences from the kit (only the sheet settings, no motion), and the parts the app now takes from the kit: toasts, alerts, action sheets, menus,
sheets, switches, the segmented control, the speed slider, the tab bar and rows (MAINTAINING › Parts kit).
VS_PARTS=pin,motion,diff,popups,controls,looks runs only those parts."""
import os, re, hashlib
import harness
from harness import until

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, 'tools', 'parts-kit')
ONLY = [x for x in os.environ.get('VS_PARTS', '').split(',') if x]

# Every way the app differs from the parts kit, each with its decision ID. Parts.differences() must match this list
# exactly: a difference nobody decided fails, and so does a line that no longer differs (take it off). At Q41 only
# the sheet settings differ from the kit's defaults; no spring or timing does.
DIFFERENCES = {
    'setting sheet.withStops': 'D09',  # New song opens at the 45% stop
    'setting sheet.growsToFull': 'D10',  # … and grows to full when a file is picked or Manually is chosen
    'setting sheet.fullScreen': 'D10',  # the Marks key is a full-screen cover
}

DECISIONS = ['D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D18']


def want(part):
    return not ONLY or part in ONLY


def src(p):
    return open(os.path.join(ROOT, p), encoding='utf-8').read()


def pin(b, t):
    ok = t.ok
    sums = {}
    for line in open(os.path.join(KIT, 'SHA256SUMS.txt'), encoding='utf-8'):
        if line.strip():
            h, name = line.split()
            sums[name] = h
    for name, where in (('parts-kit.css', 'css'), ('parts-kit.js', 'js')):
        got = hashlib.sha256(open(os.path.join(ROOT, where, name), 'rb').read()).hexdigest()
        ok(sums.get(name) == got, f'{where}/{name} is the kit release unchanged (its SHA256SUMS.txt line matches)')
    for f in ('README.md', 'CHANGELOG.md', 'LICENSE.txt'):
        ok(os.path.exists(os.path.join(KIT, f)), f'tools/parts-kit/{f} is kept beside the pinned copy')
    ver = re.search(r'^## (\d+\.\d+\.\d+)', src('tools/parts-kit/CHANGELOG.md'), re.M).group(1)
    ok(f"VERSION = '{ver}'" in src('js/parts-kit.js') or f'"{ver}"' in src('js/parts-kit.js') or ver in src('js/parts-kit.js')[:400],
       f'the copy is the version its changelog says ({ver})')
    ok(f'Parts kit {ver}' in src('MAINTAINING.md'), f'MAINTAINING › Parts kit names the pinned version ({ver})')
    html = src('index.html')
    order = re.findall(r'(?:src|href)="((?:js|css)/[^"?]+)\?v=', html)
    ok(order.index('css/parts-kit.css') < order.index('css/app.css'), "the kit's stylesheet loads before the app's")
    ok(order.index('js/parts-kit.js') < order.index('js/parts.settings.js') < order.index('js/motion.js'),
       "the kit's script, then its settings, load before js/motion.js")
    s = src('js/parts.settings.js')
    miss = [d for d in DECISIONS if d not in s]
    ok(not miss, f'the settings file has a line for each decision D01–D16 and D18 ({miss})')
    pg = t.page(b)
    r = pg.evaluate("({v:Parts.version,p:Parts.problems.slice(),m:Parts.current.motion,hold:Parts.current.timing.hold,toast:Parts.current.timing.toast})")
    ok(r['v'] == ver and r['p'] == [], f'the kit {ver} is loaded and its settings load with no problems ({r["p"]})')
    ok(r['m'] == 'kit', 'the kit runs the motion (motion: kit, D18)')
    ok(r['hold'] == 700 and r['toast'] == 3000, 'long-press menus open at 700 ms and toasts stay 3 s')


VARS = "()=>{const s=document.documentElement.style,c=document.documentElement.classList;return {g:s.getPropertyValue('--dur-gentle'),n:s.getPropertyValue('--dur-nav'),sh:s.getPropertyValue('--dur-sheet'),sp:s.getPropertyValue('--pk-speed'),off:c.contains('motion-off'),red:c.contains('motion-reduced'),on:MOTION.on(),kon:Parts.motion.on()}}"


def motion(b, t):
    ok = t.ok
    # only the kit writes the motion variables and classes
    bad = []
    for f in sorted(os.listdir(os.path.join(ROOT, 'js'))):
        if not f.endswith('.js') or f.startswith('parts-kit'):
            continue
        s = src('js/' + f)
        for pat in (r"setProperty\(\s*'--(ease|dur)-", r"classList\.(toggle|add|remove)\(\s*'motion-(off|reduced)'"):
            if re.search(pat, s):
                bad.append(f)
    ok(not bad, f'only the kit writes --ease-*, --dur-*, .motion-off and .motion-reduced ({sorted(set(bad))})')
    ok(not re.search(r'SPRINGS\s*=\s*\{', src('js/motion.js')), "js/motion.js makes no springs of its own (they're the kit's)")
    # motion off (the tests' speed 0) reaches the kit and the app
    pg = t.page(b)
    v = pg.evaluate(VARS)
    ok(v['g'] == '0ms' and v['sh'] == '0ms' and v['sp'] == '0' and v['off'] and not v['on'] and not v['kon'],
       f'speed 0 (set before the page loads) reaches the kit and MOTION: every spring 0 ms, motion-off ({v})')
    ok(pg.evaluate("JSON.stringify(MOTION.SPRINGS)===JSON.stringify(Parts.motion.springs())"), "MOTION's springs are the kit's")
    # normal speed
    pg = t.page(b, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    v = pg.evaluate(VARS)
    ms = pg.evaluate("Parts.motion.curve(.82,1.9).ms")
    ok(v['g'] == f'{ms}ms' and v['sp'] == '1' and not v['off'] and v['on'], f'at normal speed gentle is the kit\'s {ms} ms ({v})')
    # slow motion from Settings › Accessibility
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='access'})")
    until(pg, "!!document.querySelector('[data-a=setSlow]')")
    pg.click('[data-a=setSlow]')
    until(pg, "Parts.motion.speed()===4")
    v = pg.evaluate(VARS)
    ok(v['sp'] == '4' and v['g'] == f'{ms * 4}ms' and pg.evaluate("localStorage.getItem('vocalMotion')") == '4',
       f'Slow motion sets the kit\'s speed to 4 and saves it on this device ({v})')
    ok(pg.evaluate("MOTION.dur('gentle')===Parts.motion.spring('gentle')"), "the app's own animations follow the kit's slow motion")
    # (the harness sets the speed before every load, so a reload is a fresh page with this device's saved speed)
    pg2 = t.page(b, init="try{localStorage.setItem('vocalMotion','4')}catch(e){}")
    ok(pg2.evaluate("Parts.motion.speed()===4&&MOTION.speed()===4"), 'slow motion survives a reload (handed to the kit at start-up)')
    pg2.context.close()
    # forced Reduce Motion
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='access'})")
    until(pg, "!!document.querySelector('[data-a=setReduce][data-v=on]')")
    pg.click('[data-a=setReduce][data-v=on]')
    v = pg.evaluate(VARS)
    ok(v['red'] and not v['on'] and not v['kon'] and pg.evaluate("localStorage.getItem('vocalReduce')") == 'on',
       f'forced Reduce Motion reaches the kit and the app, and is saved on this device ({v})')
    pg.reload()
    harness.ready(pg)
    v = pg.evaluate(VARS)
    ok(v['red'] and pg.evaluate("Parts.motion.reduced()"), 'forced Reduce Motion survives a reload')
    # the kit's parts follow it: a toast fades rather than drops
    pg.evaluate("toast('Hello')")
    ok(pg.evaluate("matchMedia&&document.documentElement.classList.contains('motion-reduced')&&!!document.querySelector('.pk-toast')"),
       'a kit part (a toast) shows under the forced Reduce Motion')
    pg.click('[data-a=setReduce][data-v=off]') if pg.query_selector('[data-a=setReduce][data-v=off]') else None
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='access'})")
    until(pg, "!!document.querySelector('[data-a=setReduce][data-v=off]')")
    pg.click('[data-a=setReduce][data-v=off]')
    ok(not pg.evaluate("Parts.motion.reduced()") and pg.evaluate("localStorage.getItem('vocalReduce')") == 'off',
       'forcing Reduce Motion off reaches the kit')
    # the device's own setting is followed when Match iPhone is chosen
    pg = t.page(b, ctx_args={'reduced_motion': 'reduce'})
    ok(pg.evaluate("Parts.motion.reduced()&&MOTION.reduced()&&document.documentElement.classList.contains('motion-reduced')"),
       "with Match iPhone, the device's Reduce Motion reaches the kit and the app")


def diff(b, t):
    ok = t.ok
    pg = t.page(b)
    seen = {}
    for name, js in (('Today', "go(()=>{U.tab='today';U.view=null;U.sheet=null})"),
                     ('Songs', "go(()=>{U.tab='songs';U.view=null;U.sheet=null})"),
                     ('Exercises', "go(()=>{U.tab='exercises';U.view=null;U.sheet=null})"),
                     ('Settings', "go(()=>{U.tab='settings';U.view=null;U.sheet=null})"),
                     ('New song', "go(()=>{U.tab='songs';U.view=null});U.sheet='sgNew';U.sd={};rerender()")):
        pg.evaluate(js)
        pg.wait_for_timeout(120)
        for d in pg.evaluate("Parts.differences().map(d=>[d.key,d.text])"):
            seen.setdefault(d[0], (name, d[1]))
    extra = {k: v for k, v in seen.items() if k not in DIFFERENCES}
    stale = [k for k in DIFFERENCES if k not in seen]
    ok(not extra, f'every way the app differs from the kit is on the list with its decision ID ({extra})')
    ok(not stale, f'every line on the list still differs (take off any that no longer do: {stale})')
    ok(all(re.fullmatch(r'D\d\d', v) for v in DIFFERENCES.values()), 'each listed difference has a decision ID')


def touch_drag(pg, x, y0, y1, steps=6, ms=16):
    """A quick finger drag (a flick when steps × ms is short)."""
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y0}]})
    for i in range(1, steps + 1):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y0 + (y1 - y0) * i / steps}]})
        pg.wait_for_timeout(ms)
    pg.wait_for_timeout(16)  # a finger lifts a frame after its last move
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    pg.wait_for_timeout(250)


def popups(b, t):
    """Stage 2: toasts, alerts (D08), action sheets (D07), menus (D16) and sheets (D09, D10, D14, D15, D17)."""
    ok = t.ok
    pg = t.page(b, touch=True)
    # toasts: the kit's, 3 s
    pg.evaluate("toast('Saved')")
    ok(pg.locator('#layer .pk-toast').count() == 1 and pg.inner_text('#layer .pk-toast').strip() == 'Saved', 'a toast is the parts kit\'s')
    pg.wait_for_timeout(2500)
    ok(pg.locator('#layer .pk-toast:not(.pk-leaving)').count() == 1, 'it stays past 2.5 s')
    ok(until(pg, "!document.querySelector('#layer .pk-toast:not(.pk-leaving)')", 2000), 'and goes at 3 s')
    # an "Are you sure?" is an alert: Cancel and a red action, never the browser's own
    pg.evaluate("window.confirm=()=>{window.__nat=1;return true};U.sheet='delSession';U.sd={k:D.sessions[0].id};rerender()")
    a = pg.locator('#layer .pk-alert')
    ok(a.count() == 1 and pg.locator('#layer .pk-alert .pk-red').inner_text() == 'Delete session' and pg.locator('#layer .pk-alert [data-a=no]').inner_text() == 'Cancel',
       'Delete session asks with the kit\'s alert: Cancel and a red Delete session')
    ok(pg.evaluate("document.querySelector('#layer .pk-alert').dataset.screen") == 'VS-041', 'the alert keeps its screen ID (VS-041)')
    pg.click('#layer .pk-alert [data-a=no]'); pg.wait_for_timeout(100)
    n = pg.evaluate("D.sessions.length")
    ok(pg.evaluate("U.sheet") is None and pg.locator('#layer .pk-alert:not(.pk-leaving)').count() == 0, 'Cancel closes it and changes nothing')
    pg.evaluate("U.sheet='delSession';U.sd={k:D.sessions[0].id};rerender()")
    pg.click('#layer .pk-alert .pk-red'); pg.wait_for_timeout(200)
    ok(pg.evaluate("D.sessions.length") == n - 1 and not pg.evaluate("window.__nat"), 'the red action does what the sheet did (the session is deleted)')
    # menus: one style, 20 corners, the hold at 700 ms
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); pg.wait_for_timeout(150)
    bx = pg.locator('#app .rowc').first.bounding_box()
    pg.mouse.move(bx['x'] + 60, bx['y'] + 20); pg.mouse.down(); pg.wait_for_timeout(600)
    ok(pg.locator('#layer .pk-menu').count() == 0, 'no long-press menu before 700 ms')
    pg.wait_for_timeout(250); pg.mouse.up(); pg.wait_for_timeout(150)
    ok(pg.locator('#layer .pk-menu#ctxmenu').count() == 1, 'it opens at 700 ms')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#layer .pk-menu')).borderRadius") == '20px', 'with 20 corners')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#layer .pk-dim')).backgroundColor") in ('rgba(0, 0, 0, 0.2)', 'rgba(0, 0, 0, 0.25)'),
       'and the page dimmed 20% (25% in dark), no blur')
    pg.click('#layer .pk-dim', position={'x': 20, 'y': 100}); pg.wait_for_timeout(250)
    ok(pg.evaluate("SG.ctx") is None and pg.locator('#layer .pk-menu').count() == 0, 'tapping away closes it')
    pg.click('#hdrsort'); pg.wait_for_timeout(150)
    ok(pg.evaluate("getComputedStyle(document.querySelector('#sortmenu')).borderRadius") == '20px' and pg.locator('#sortmenu.pk-menu').count() == 1,
       'a pull-down menu is the same menu, 20 corners')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.evaluate("SG.sortMenu") is False, 'Escape closes it')
    # sheets: 46 corners, strong glass, a flick and a pull from the content close them
    pg.evaluate("go(()=>{U.tab='today';U.view=null});U.calMonth=null;U.sheet='calendar';U.sd={};rerender()"); pg.wait_for_timeout(200)
    sh = pg.locator('#layer .vs-sheet')
    ok(sh.count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#layer .vs-sheet')).borderTopLeftRadius") == '46px', 'a sheet has 46 corners (D17)')
    ok(pg.evaluate("document.querySelector('#layer .vs-sheet').matches('.pk-sheet.pk-glass.pk-strong')"), 'and the strong glass (D15)')
    hb = pg.locator('#layer .vs-sheet .shead').bounding_box()
    touch_drag(pg, hb['x'] + 60, hb['y'] + 20, hb['y'] + 380, steps=6, ms=16)
    ok(until(pg, "U.sheet===null", 2000), 'a flick down closes it')
    pg.evaluate("U.sheet='persist';U.sd={};rerender()"); pg.wait_for_timeout(200)
    bd = pg.locator('#layer .vs-sheet .pk-sheet-body .bkstat').bounding_box()
    ok(pg.locator('#layer .vs-sheet .pk-sheet-body.pk-at-top').count() == 1, 'its content is at the top')
    touch_drag(pg, bd['x'] + 20, bd['y'] + 10, bd['y'] + 370, steps=6, ms=16)
    ok(until(pg, "U.sheet===null", 2000), 'pulling down from its content closes it too')
    # New song at the 45% stop, growing to full; the Marks key as a full-screen cover
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); pg.click('#barR [data-a=sgNew]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("HOST.ctl()&&HOST.ctl().stop") == 'medium', 'New song opens at the 45% stop on Add media (D09)')
    pg.click('#layer [data-a=sgAddMode][data-v=manual]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("HOST.ctl()&&HOST.ctl().stop") == 'full', 'and grows to full when Manually is chosen (D10)')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId=D.songs[0].id});U.sheet='sgKey';U.sd={};rerender()"); pg.wait_for_timeout(200)
    ok(pg.locator('#layer .vs-sheet.pk-cover').count() == 1, 'the Marks key opens as a full-screen cover (D10)')
    pg.click('#layer .vs-sheet [data-a=close]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") is None, 'its ✕ closes it')
    pg.context.close()


def controls(b, t):
    """Stages 3 and 4: switches, the segmented control (D04), the speed slider (D03), the tab bar (D01, D02), the top
    bar's buttons and rows (D06)."""
    ok = t.ok
    js = ''.join(open(os.path.join(ROOT, 'js', f), encoding='utf-8').read() for f in os.listdir(os.path.join(ROOT, 'js')) if f.endswith('.js') and not f.startswith('parts-kit'))
    ok('class="tgl"' not in js and 'class="knob"' not in js and 'class="opmenu' not in js, 'no old switch, knob or menu markup is left in the code')
    css = open(os.path.join(ROOT, 'css', 'app.css'), encoding='utf-8').read()
    ok(not re.search(r'\.row:active\s*\{[^}]*transform', css) and not re.search(r':active[^{]*\{[^}]*scale\(0\.9[68]\)', css), 'rows highlight while pressed, none shrinks (D06)')
    pg = t.page(b, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='appear'})"); pg.wait_for_timeout(200)
    ok(pg.locator('#app .pk-switch').count() >= 2, 'Settings › Appearance has the kit\'s switches')
    row = '#app [data-a=setIds]'
    on = pg.evaluate(f"document.querySelector('{row}').getAttribute('aria-checked')") == 'true'
    pg.click(row); pg.wait_for_timeout(60)
    ok(pg.evaluate(f"document.querySelector('{row} .pk-switch').classList.contains('on')") != on and
       pg.evaluate(f"document.querySelector('{row}').getAttribute('aria-checked')") == ('false' if on else 'true'), 'a tap on its row toggles it')
    ok(pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--dur-switch').trim()") == '380ms', 'the switch moves over 380 ms')
    pg.click(row); pg.wait_for_timeout(450)
    # segmented controls
    pg.evaluate("go(()=>{U.tab='history';U.view=null})"); pg.wait_for_timeout(200)
    seg = '#app .seg.pk-seg'
    ok(pg.locator(seg).count() >= 1 and pg.locator(seg + ' > .pk-seg-ind').count() >= 1, 'Progress\'s range is the kit\'s segmented control')
    ok(pg.evaluate("Parts.current.segmented.style") == 'gallery' and pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--dur-snap').trim()") != '',
       'the gallery\'s knob on its spring, no squish (D04)')
    pg.click(seg + ' > button >> nth=2'); pg.wait_for_timeout(400)
    ok(pg.evaluate(f"document.querySelector('{seg}').style.getPropertyValue('--pk-i')") == '2', 'a tap moves the knob there')
    # the tab bar
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(200)
    ok(pg.locator('#dock .pk-dock .pk-tabbar.pk-glass > .pk-tab-ind').count() == 1 and pg.locator('#dock .pk-tab').count() == 4, 'the tab bar is the kit\'s (D01)')
    g = pg.evaluate("(()=>{const p=document.querySelector('#dock .pk-tabbar').getBoundingClientRect(),c=document.querySelector('#dock .scirc').getBoundingClientRect();return c.left-p.right})()")
    ok(abs(g - 8) < 0.6, f'the search circle sits 8 pt from it (D02: {g:.1f})')
    pg.click('#dock .pk-tab[data-v=songs]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.tab") == 'songs' and pg.evaluate("document.querySelector('#dock .pk-tabbar').style.getPropertyValue('--pk-i')") == '2', 'a tab opens its page and the highlight moves to it')
    # the speed slider
    pg.evaluate("go(()=>{U.tab='exercises';U.view='ex';U.exId='humming';U.exTab='summary'})"); pg.wait_for_timeout(300)
    if pg.locator('#pSpd').count():
        pg.click('#pSpd'); pg.wait_for_timeout(200)
        ok(pg.locator('#pHud.on .pk-slider').count() == 1 and pg.locator('#pHud .phbar').count() == 0, 'the speed control is the kit\'s slider, not the vertical bar (D03)')
        sb = pg.locator('#pHud .pk-slider').bounding_box()
        pg.mouse.move(sb['x'] + sb['width'] / 2, sb['y'] + sb['height'] / 2); pg.mouse.down(); pg.wait_for_timeout(200)
        ok(pg.locator('#pHud .pk-slider.pk-held').count() == 1, 'its knob grows while held')
        pg.mouse.up()
    else:
        ok(False, 'the exercise page shows the speed pill')
    pg.context.close()


SIZES = [(375, 812, False), (390, 844, False), (402, 874, False), (820, 1180, True)]


def looks(b, t):
    """Each overlay at 375, 390 and 402 wide and on iPad, in light, dark, Reduce Motion and Reduce transparency: no
    errors, nothing sideways, the sheet's corners and the alert where they should be."""
    ok = t.ok
    for w, h, pad in SIZES:
        for mode in ('light', 'dark', 'reduce', 'solid'):
            init = "try{localStorage.setItem('vocalTransp','on')}catch(e){}" if mode == 'solid' else None
            pg = t.page(b, w, h, 'dark' if mode == 'dark' else 'light', init=init,
                        ctx_args={'reduced_motion': 'reduce'} if mode == 'reduce' else None, **({'ua': None} if pad else {}))
            tag = f'{w}×{h} {mode}'
            pg.evaluate("U.sheet='addSong';U.sd={};rerender()"); pg.wait_for_timeout(150)
            r = pg.evaluate("(()=>{const s=document.querySelector('#layer .vs-sheet'),b=s.getBoundingClientRect();return {rad:getComputedStyle(s).borderTopLeftRadius,l:b.left,r:innerWidth-b.right,bot:innerHeight-b.bottom,side:document.documentElement.scrollWidth>innerWidth+1}})()")
            ok(r['rad'] == '46px' and r['l'] >= 7.5 and r['r'] >= 7.5 and abs(r['bot'] - 8) < 1.5 and not r['side'], f'{tag}: a sheet sits 8 pt in, with 46 corners ({r})')
            if pad: ok(r['l'] > 100, f'{tag}: on iPad it stays at most 540 pt wide, in the middle')
            pg.evaluate("U.sheet='resetMonth';U.sd={};rerender()"); pg.wait_for_timeout(150)
            a = pg.evaluate("(()=>{const s=document.querySelector('#layer .pk-alert:not(.pk-leaving)').getBoundingClientRect();return {c:Math.abs((s.left+s.right)/2-innerWidth/2),in:s.top>0&&s.bottom<innerHeight}})()")
            ok(a['c'] < 1.5 and a['in'], f'{tag}: the alert sits in the middle ({a})')
            if mode == 'solid': ok(pg.evaluate("document.documentElement.classList.contains('glass-solid')"), f'{tag}: Reduce transparency reaches the kit\'s glass')
            if mode == 'reduce': ok(pg.evaluate("Parts.motion.reduced()"), f'{tag}: Reduce Motion reaches the kit')
            pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
            ok(pg.evaluate("Parts.open") == 0 and not pg.evaluate("!!document.querySelector('#layer .pk-dim.pk-on')"), f'{tag}: nothing is left open')
            if w == 390 and mode in ('light', 'dark'): t.shot(pg, f'alert-{mode}')
            pg.context.close()


def run(b, t):
    for name, fn in (('pin', pin), ('motion', motion), ('diff', diff), ('popups', popups), ('controls', controls), ('looks', looks)):
        if want(name):
            fn(b, t)
