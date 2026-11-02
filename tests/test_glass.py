"""Q33 Glass native tuning: the glass material in light and dark (tokens, rim, shadow, sheets keeping their strength),
the shared press (glass buttons grow by 17 pt along their longest side, buttons on a glass bar only light up), the
springs with motion on, Reduce Motion, Reduce transparency (the switch, kept after a reload, never in a backup, and the
browser's own setting), and no grown button cut off or covered at 375, 390 and 402 wide and on iPad.

VS_GLASS=material,press,solid,motion,reduced,transp,clip runs only those parts."""
import os, json
import harness
from test_layout import SONG
import test_track

PARTS = [p for p in os.environ.get('VS_GLASS', '').split(',') if p]

# press an element with a synthetic touch (no click follows), read what it looks like, then let go (pointercancel)
PRESS = """sel=>{const el=typeof sel==='string'?document.querySelector(sel):sel;if(!el)return null;
 const keep=el.getAttribute('style');
 el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'touch',isPrimary:true,button:0}));
 const cs=getComputedStyle(el),r=el.getBoundingClientRect();
 const o={sel:typeof sel==='string'?sel:el.className,cls:el.className,w:el.offsetWidth,h:el.offsetHeight,
  want:1+17/Math.max(el.offsetWidth,el.offsetHeight),scale:cs.scale==='none'?1:parseFloat(cs.scale),
  z:cs.zIndex,pos:cs.position,lift:cs.getPropertyValue('--lift').trim(),bgi:cs.backgroundImage,
  max:getComputedStyle(document.documentElement).getPropertyValue('--lift-max').trim(),
  grows:el.matches(PRESS.GROW),bar:el.matches(PRESS.ON_BAR)};
 el.dispatchEvent(new PointerEvent('pointercancel',{bubbles:true,pointerType:'touch'}));
 o.after=getComputedStyle(el).scale;o.afterCls=el.classList.contains('pressing');o.keep=keep;
 return o}"""
SETTLED = """sel=>{const el=document.querySelector(sel);return !!el&&!el.classList.contains('pressing')&&getComputedStyle(el).scale==='none'}"""

# what clips or covers a pressed element: every ancestor that cuts off its overflow, the screen, and whatever is on top
# at points just inside its grown edges
CLIP = """sel=>{const els=[...document.querySelectorAll(sel)].filter(e=>{const r=e.getBoundingClientRect();
  if(!(r.width>4&&r.height>4&&r.bottom>0&&r.top<innerHeight))return false;
  // only what you can press: on top at its own centre (not hidden, faded out or behind a sheet's dimming)
  const h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return !!h&&e.contains(h)});
 const out=[];
 for(const el of els){
  el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'touch',isPrimary:true,button:0}));
  const r=el.getBoundingClientRect(),bad=[];
  const sc=parseFloat(getComputedStyle(el).scale)||1;
  if(r.left<-0.5||r.top<-0.5||r.right>innerWidth+0.5||r.bottom>innerHeight+0.5)bad.push('off screen');
  for(let a=el.parentElement;a&&a!==document.documentElement;a=a.parentElement){
   const c=getComputedStyle(a);
   if(c.overflowX==='visible'&&c.overflowY==='visible')continue;
   const q=a.getBoundingClientRect(),L=q.left+a.clientLeft,T=q.top+a.clientTop,R=L+a.clientWidth,B=T+a.clientHeight;
   const sx=c.overflowX!=='visible',sy=c.overflowY!=='visible';
   // a part that scrolls cuts off only what's outside what it can scroll to
   const scrollsY=a.scrollHeight>a.clientHeight+1&&/(auto|scroll)/.test(c.overflowY);
   if(sx&&(r.left<L-0.5||r.right>R+0.5))bad.push('cut off sideways by .'+[...a.classList].join('.')+(a.id?'#'+a.id:''));
   if(sy&&!scrollsY&&(r.top<T-0.5||r.bottom>B+0.5))bad.push('cut off by .'+[...a.classList].join('.')+(a.id?'#'+a.id:''));
  }
  const pts=[[r.left+r.width/2,r.top+2],[r.left+r.width/2,r.bottom-2],[r.left+2,r.top+r.height/2],[r.right-2,r.top+r.height/2]];
  for(const [x,y] of pts){if(x<0||y<0||x>=innerWidth||y>=innerHeight)continue;
   const h=document.elementFromPoint(x,y);
   // a point just inside a round button's box can be outside the circle itself: only flag a cover that's a real part
   // something that paints nothing there (a clear bar's own box) doesn't cover it
   const hc=h&&getComputedStyle(h);
   const clear=hc&&/rgba\(0, 0, 0, 0\)|transparent/.test(hc.backgroundColor)&&hc.backgroundImage==='none'&&(hc.backdropFilter||'none')==='none'
     &&![...h.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
   if(h&&!clear&&!el.contains(h)&&!h.contains(el)&&hc.pointerEvents!=='none'){
    const br=parseFloat(getComputedStyle(el).borderTopLeftRadius)*sc;
    const cx=r.left+r.width/2,cy=r.top+r.height/2,rx=Math.max(0,r.width/2-br),ry=Math.max(0,r.height/2-br);
    const dx=Math.max(0,Math.abs(x-cx)-rx),dy=Math.max(0,Math.abs(y-cy)-ry);
    if(Math.hypot(dx,dy)<=br-1)bad.push('covered by .'+[...h.classList].join('.'))}}
  el.dispatchEvent(new PointerEvent('pointercancel',{bubbles:true,pointerType:'touch'}));
  out.push({cls:el.className.replace(' pressing',''),label:el.getAttribute('aria-label')||el.innerText.trim().slice(0,20),scale:+sc.toFixed(3),bad})}
 return out}"""

GO = "js=>go(()=>{U.sheet=null;U.view=null;eval(js)})"
# the status bar's safe area, stood in through the stylesheet's own variable (as test_native): an iPhone 17 Pro's, and
# an iPad's (the Home Screen app draws behind it)
SAFE = "px=>{document.documentElement.style.setProperty('--sat',px+'px');rerender()}"
alpha = lambda c: float(c.rstrip(')').split(',')[-1]) if c.count(',') == 3 else 1.0


def song_seed(b):
    t = harness.T('glass-seed')
    pg = t.page(b)
    pg.evaluate(SONG)
    seed = json.loads(pg.evaluate("localStorage.getItem('vocalTracker')")); sid = pg.evaluate("U.songId")
    pg.context.close()
    return seed, sid


def with_track(pg, sid):
    pg.evaluate(GO, f"U.tab='songs';U.view='lyr';U.songId='{sid}'"); pg.wait_for_timeout(150)
    with pg.expect_file_chooser(timeout=5000) as fc: pg.click('#app [data-a=trkAdd]')
    fc.value.set_files(test_track.track())
    pg.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()", arg=sid, timeout=15000)
    pg.evaluate(GO, f"U.tab='songs';U.view='trk';U.songId='{sid}'"); pg.wait_for_timeout(250)


def markers(pg):
    """The track player's Markers level: its pills and pads instead of the round transport."""
    pg.locator('#app [data-a=trkLevel][data-v="3"]').first.click(); pg.wait_for_timeout(250)


def material(b, t):
    ok = t.ok
    G = """sel=>{const e=document.querySelector(sel);if(!e)return null;const c=getComputedStyle(e),be=getComputedStyle(e,'::before');
      return {bg:c.backgroundColor,bf:c.backdropFilter||c.webkitBackdropFilter,sh:c.boxShadow,pad:be.padding,rim:be.backgroundImage,after:getComputedStyle(e,'::after').content}}"""
    for sc in ('light', 'dark'):
        pg = t.page(b, sc=sc)
        g = pg.evaluate(G, '#bar .circ.glass')
        bar = pg.evaluate(G, '.dockrow .tabbar')
        if sc == 'light':
            ok(g['bg'] == 'rgba(248, 248, 248, 0.53)', f'light: glass is tinted #F8F8F8 at 53% ({g["bg"]})')
            ok(g['bf'] == 'blur(14px) saturate(2.1)', f'light: blur 14 px with saturate 210%, no brightness boost ({g["bf"]})')
            ok(g['sh'].endswith('rgba(0, 0, 0, 0.016) 0px 7px 12px 0px') and '16px' not in g['sh'],
               'light: a barely-there shadow (0 7 px 12 px at 1.6%) and no 16 px inner glow')
            ok(g['sh'].startswith('rgba(255, 255, 255, 0.2) 0px 1px 0.5px 0px inset'), 'light: the rim light is at the top')
            ok(g['rim'].startswith('linear-gradient(rgba(0, 0, 0, 0.063)') or g['rim'].startswith('linear-gradient(rgba(0, 0, 0, 0.062)'),
               f'light: the hairline fades to a fifth where the light hits it ({g["rim"][:60]})')
        else:
            ok(g['bg'] == 'rgba(255, 255, 255, 0.12)', f'dark: glass is white at 12% ({g["bg"]})')
            ok(g['bf'] == 'blur(14px) saturate(1.4)', f'dark: saturate 140% ({g["bf"]})')
            ok('rgba(0, 0, 0, 0) 0px 0px 0px 0px' in g['sh'] and 'rgba(0, 0, 0, 0.' not in g['sh'].replace('rgba(0, 0, 0, 0) ', ''),
               'dark: no shadow')
            ok(g['sh'].startswith('rgba(255, 255, 255, 0.23) 0px -1px 0.5px 0px inset'), 'dark: the rim light is at the bottom')
            ok(g['rim'].startswith('linear-gradient(rgba(0, 0, 0, 0)'), 'dark: the hairline fades out at the ends')
        ok(g['pad'] == '0.5px' and g['after'] == 'none', f'{sc}: a 0.5 pt hairline, and no shine layer')
        ok(bar['bf'] == g['bf'] and bar['bg'] == g['bg'], f'{sc}: the tab bar takes the same material')
        # sheets keep their strength and blur; they take the rim, the shadow and dark mode's saturation
        pg.evaluate(GO, "U.tab='today'"); pg.locator('#app [data-a="openCal"]').first.click(); pg.wait_for_timeout(250)
        s = pg.evaluate(G, '.sheet')
        h = pg.evaluate(G, '.shead')
        strong = 'rgba(250, 250, 252, 0.86)' if sc == 'light' else 'rgba(44, 44, 48, 0.86)'
        sat = '2.1' if sc == 'light' else '1.4'
        ok(s and s['bg'] == strong and s['bf'] == f'blur(26px) saturate({sat}) brightness(1.06)',
           f'{sc}: a sheet keeps its near-solid tint and blur, with {sat} saturation ({s and s["bf"]})')
        ok(s and s['sh'] == g['sh'] and s['pad'] == '0.5px', f'{sc}: and takes the new rim and shadow')
        ok(h and h['bf'] == 'blur(20px) saturate(' + ('1.8' if sc == 'light' else '1.4') + ')', f'{sc}: the sheet header follows its sheet ({h and h["bf"]})')
        t.shot(pg, f'calendar-{sc}')
        pg.context.close()
    # the other blurs the handoff named take the new material too
    pg = t.page(b)
    rules = pg.evaluate("""()=>{const o={};for(const sh of document.styleSheets){for(const r of sh.cssRules){if(['.fwtabin','.opmenu'].includes(r.selectorText))
      o[r.selectorText]=(r.style.backdropFilter||r.style.webkitBackdropFilter)+' | '+r.style.boxShadow}}return o}""")
    ok(all('var(--glass-blur)' in v and 'var(--glass-rim)' in v for v in rules.values()) and len(rules) == 2,
       f'the floating window’s tuck tab and the option menu use the new material ({rules})')
    pg.context.close()


def press(b, t, seed, sid):
    ok = t.ok

    def check(pg, sel, kind):
        o = pg.evaluate(PRESS, sel)
        if not o:
            ok(False, f'{sel}: on screen to press'); return
        if kind == 'grow':
            ok(o['grows'] and abs(o['scale'] - o['want']) <= 0.01,
               f'{sel} ({o["w"]}×{o["h"]}) grows to ×{o["want"]:.3f} (1 + 17 ÷ {max(o["w"], o["h"])}): ×{o["scale"]:.3f}')
        else:
            ok(o['bar'] and not o['grows'] and o['scale'] == 1, f'{sel} sits on a glass bar: it doesn’t change size ({o["scale"]})')
        ok(o['lift'] == o['max'] and o['max'] in o['bgi'], f'{sel} lights up with a white layer under its icon ({o["lift"]})')
        ok(o['pos'] != 'static' and int(o['z']) >= 10, f'{sel} is lifted above its neighbours while pressed (z {o["z"]})')
        back = harness.until(pg, SETTLED, 2000, sel)
        ok(back and pg.evaluate("s=>document.querySelector(s).getAttribute('style')", sel) == o['keep'],
           f'{sel}: let go, it’s back to rest with nothing left behind')

    pg = t.page(b, data=seed)
    # Today: the top bar's circle, the search circle, the tabs
    check(pg, '#bar .circ.glass', 'grow')
    check(pg, '.dockrow .scirc', 'grow')
    check(pg, '.dockrow .tabbar button:not(.on)', 'bar')
    check(pg, '.dockrow .tabbar button.on', 'bar')
    # a real press with the mouse goes through the same rule
    box = pg.locator('#bar .circ.glass').bounding_box()
    pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2); pg.mouse.down()
    sc = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#bar .circ.glass')).scale)")
    pg.evaluate("window.dispatchEvent(new PointerEvent('pointercancel'))")
    pg.mouse.up()
    ok(abs(sc - (1 + 17 / box['width'])) <= 0.01, f'a real mouse press grows it too (×{sc:.3f})')
    # the collapsed tab pill
    pg.evaluate(GO, "U.tab='songs'"); pg.wait_for_timeout(150)
    pg.evaluate("setTabMin(true)"); pg.wait_for_timeout(100)
    check(pg, '.dockrow.min .tabpill', 'grow')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.dockrow.min .tabpill')).transform") == 'none', 'the pill’s own transform is left alone')
    pg.evaluate("setTabMin(false)")
    check(pg, '#app .circ.glass, #bar .circ.glass', 'grow')
    # a sheet's ✕
    pg.evaluate(GO, "U.tab='today'"); pg.locator('#app [data-a="openCal"]').first.click(); pg.wait_for_timeout(250)
    check(pg, '.sheet .xbtn', 'grow')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    # a session: the clock pill (a new press) and the glass main button; on Today, the floating window's play/pause
    pg.evaluate("()=>{newSession();go(()=>{U.view='found'})}"); pg.wait_for_timeout(250)
    check(pg, '#timer[data-a=clock]', 'grow')
    pg.evaluate("window.scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(100)
    check(pg, '.cta.glass', 'grow')
    pg.evaluate(GO, "U.tab='today'"); pg.wait_for_timeout(300)
    check(pg, '.fw .fwbtn', 'bar')
    pg.context.close()

    # the exercise page's pattern dock (Q32's glass pills follow the same rule)
    pg = t.page(b)
    pg.evaluate(GO, "U.tab='exercises';U.view='ex';U.exId='humming';U.exTab='summary'"); pg.wait_for_timeout(300)
    check(pg, '.ppill.glass', 'grow')
    check(pg, '.prep.glass', 'grow')
    check(pg, '.pstep button', 'bar')
    pg.context.close()

    # the track player: marker pills and replay pads grow, the transport only lights up
    pg = t.page(b, data=seed)
    with_track(pg, sid)
    check(pg, '.trktr .trkpp', 'bar')
    check(pg, '.trktr .trkb', 'bar')
    markers(pg)
    check(pg, '.trkpill.glass', 'grow')
    check(pg, '.trkpad.glass', 'grow')
    pg.context.close()

    # buttons in states the screens above don't open: the same rule, measured on each one
    pg = t.page(b)
    pg.evaluate("""()=>{const d=document.createElement('div');d.id='q33';d.style.cssText='position:fixed;left:40px;top:300px;display:flex;gap:20px;z-index:50';
      d.innerHTML='<button class="shbtn glass ok">✓</button><button class="txtbtn glass tinted">Done</button><button class="circ glass tinted">+</button>'+
      '<button class="circ glass sm mkq">?</button><button class="pill glass mktp">0:12</button><button class="txtbtn glass ckgedit">Edit</button>';document.body.appendChild(d)}""")
    for s in ('#q33 .shbtn.ok', '#q33 .txtbtn.tinted', '#q33 .circ.tinted', '#q33 .mkq', '#q33 .mktp', '#q33 .ckgedit'):
        check(pg, s, 'grow')
    pg.context.close()


def solid(b, t):
    """Not glass, so not part of this: they keep their own shrink."""
    ok = t.ok
    pg = t.page(b)
    o = pg.evaluate("""()=>{const q=s=>document.querySelector(s);const m=(e)=>!!e&&e.matches(PRESS.SEL);
      const act=[];for(const sh of document.styleSheets)for(const r of sh.cssRules){if(r.selectorText&&r.selectorText.includes(':active')&&/scale\\(0\\.9/.test(r.style.transform||''))act.push(r.selectorText)}
      return {ink:m(q('#app .cta.ink')),row:m(q('#app .row')),act:act.join(' || ')}}""")
    ok(not o['ink'] and '.cta:not(.glass):active' in o['act'], 'Start session (solid) isn’t part of the glass press and still shrinks')
    ok(not o['row'], 'nor are list rows')
    pg.evaluate(GO, "U.tab='today'"); pg.locator('#app [data-a="openCal"]').first.click(); pg.wait_for_timeout(250)
    ok(not pg.evaluate("document.querySelector('.calhead .circ').matches(PRESS.SEL)"), 'the calendar’s month arrows (not glass) keep their own press')
    # no shrink rule left on any glass button or button on a glass bar
    left = pg.evaluate("""()=>{const out=[];const els=[...document.querySelectorAll(PRESS.SEL)];
      for(const sh of document.styleSheets)for(const r of sh.cssRules){if(!r.selectorText||!r.selectorText.includes(':active'))continue;
       const m=(r.style.transform||'').match(/scale\\(([\\d.]+)/);if(!m||+m[1]>=1)continue;
       for(const s of r.selectorText.split(',')){if(!s.includes(':active'))continue;const base=s.replace(/:active/g,'').trim();
        for(const e of els){try{if(e.matches(base))out.push(base)}catch(x){}}}}return [...new Set(out)]}""")
    ok(not left, f'no glass button on screen still has a shrink rule ({left})')
    pg.context.close()


def motion(b, t):
    ok = t.ok
    pg = t.page(b, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    o = pg.evaluate("""()=>new Promise(res=>{const el=document.querySelector('#bar .circ.glass');const want=1+17/Math.max(el.offsetWidth,el.offsetHeight);
      const sam=[],t0=performance.now();let phase='press';
      el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',isPrimary:true,button:0}));
      const tick=()=>{const t=performance.now()-t0,s=getComputedStyle(el).scale;sam.push([Math.round(t),phase,s==='none'?1:parseFloat(s),getComputedStyle(el).getPropertyValue('--lift').trim()]);
        if(phase==='press'&&t>450){phase='release';window.dispatchEvent(new PointerEvent('pointerup',{pointerType:'touch'}))}
        if(t<1500)requestAnimationFrame(tick);else res({want,sam,cls:el.classList.contains('pressing'),style:el.getAttribute('style')})};
      requestAnimationFrame(tick)})""")
    pr = [s for s in o['sam'] if s[1] == 'press']
    rl = [s for s in o['sam'] if s[1] == 'release']
    mid = [s[2] for s in pr if 10 <= s[0] <= 90]
    ok(mid and any(1.01 < v < o['want'] - 0.01 for v in mid), f'with motion on, it grows on the press spring (part-way at {mid[:3]})')
    ok(abs(pr[-1][2] - o['want']) <= 0.01, f'and settles at ×{o["want"]:.3f} ({pr[-1][2]:.3f})')
    ok(max(s[2] for s in pr) <= o['want'] + 0.03, 'with only a tiny overshoot')
    lo = min(s[2] for s in rl)
    ok(0.9 < lo < 1, f'let go: back on the release spring with one small dip below rest (×{lo:.3f})')
    i = next((k for k, v in enumerate(rl) if v[2] == lo), 0)
    back = next((k for k in range(i, len(rl)) if rl[k][2] >= 0.995), len(rl))
    wob = max([abs(v[2] - 1) for v in rl[back:]] or [0])
    ok(wob <= 0.01, f'and no second wobble (at most {wob:.3f} from rest after the dip)')
    ok(not o['cls'] and o['style'] in (None, ''), 'then everything is put back')
    lifts = [s[3] for s in pr if s[0] > 250]
    ok(lifts and lifts[-1] == 'rgba(255, 255, 255, 0.3)', f'it lights up within about 150 ms ({lifts[-1:]})')
    pg.context.close()


def reduced(b, t):
    ok = t.ok
    pg = t.page(b, init="try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}")
    o = pg.evaluate("""()=>new Promise(res=>{const el=document.querySelector('.dockrow .scirc');const sam=[],t0=performance.now();
      el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',isPrimary:true,button:0}));
      const tick=()=>{const t=performance.now()-t0;sam.push([t,getComputedStyle(el).scale,getComputedStyle(el).getPropertyValue('--lift').trim()]);
        if(t<320)requestAnimationFrame(tick);else{window.dispatchEvent(new PointerEvent('pointerup',{pointerType:'touch'}));res(sam)}};requestAnimationFrame(tick)})""")
    ok(all(s[1] == 'none' for s in o), 'Reduce Motion: no growth')
    ok(any(s[2] not in ('rgba(255, 255, 255, 0.3)', 'rgba(0, 0, 0, 0)', 'transparent') for s in o) and o[-1][2] == 'rgba(255, 255, 255, 0.3)',
       'the light-up still fades in')
    ok(harness.until(pg, "!document.querySelector('.dockrow .scirc').classList.contains('pressing')", 2000), 'and fades out when let go')
    pg.context.close()


def transp(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='access'})"); pg.wait_for_timeout(200)
    sw = '#app [data-a=setTransp][role=switch]'
    ok(pg.locator(sw).count() == 1 and pg.locator(sw).get_attribute('aria-checked') == 'false' and 'Reduce transparency' in pg.inner_text(sw),
       'Settings › Accessibility has a Reduce transparency switch, off')
    bg = "getComputedStyle(document.querySelector('.dockrow .scirc')).backgroundColor"
    ok(pg.evaluate(bg) == 'rgba(248, 248, 248, 0.53)', 'off: the glass tint as it is')
    pg.click(sw); pg.wait_for_timeout(150)
    ok(pg.locator(sw).get_attribute('aria-checked') == 'true' and pg.evaluate("localStorage.getItem('vocalTransp')") == 'on'
       and pg.evaluate("document.documentElement.classList.contains('glass-solid')"), 'on: kept on this device')
    ok(abs(alpha(pg.evaluate(bg)) - 0.665) < 0.004, f'the tint becomes 0.53 × 0.5 + 0.4 = 0.665 ({pg.evaluate(bg)})')
    ok('blur(14px)' in pg.evaluate("getComputedStyle(document.querySelector('.dockrow .scirc')).backdropFilter"), 'and the blur stays')
    t.shot(pg, 'transparency-on')
    pg.reload(); harness.ready(pg)
    ok(pg.evaluate("document.documentElement.classList.contains('glass-solid')") and abs(alpha(pg.evaluate(bg)) - 0.665) < 0.004, 'it’s still on after a reload')
    ok('vocalTransp' not in pg.evaluate("localStorage.getItem('vocalTracker')"), 'it isn’t in the app’s data')
    pg.evaluate("prepareExport(true)"); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    txt = pg.evaluate("pendingExport.file.text()")
    ok('vocalTransp' not in txt and 'glass-solid' not in txt, 'so it’s never in a backup')
    pg.evaluate("U.sheet=null;rerender()")
    pg.emulate_media(color_scheme='dark'); pg.wait_for_timeout(100)
    ok(abs(alpha(pg.evaluate(bg)) - 0.46) < 0.004, f'dark: 0.12 becomes 0.46 ({pg.evaluate(bg)})')
    pg.emulate_media(color_scheme='light')
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='access'})"); pg.wait_for_timeout(150)
    pg.click(sw); pg.wait_for_timeout(150)
    ok(pg.evaluate("localStorage.getItem('vocalTransp')") is None and not pg.evaluate("document.documentElement.classList.contains('glass-solid')"), 'off again goes back')
    # a browser that reports its own Reduce Transparency is followed
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-transparency', 'value': 'reduce'}]})
    pg.wait_for_timeout(150)
    if pg.evaluate("matchMedia('(prefers-reduced-transparency: reduce)').matches"):
        ok(pg.evaluate("document.documentElement.classList.contains('glass-solid')"), 'a browser’s own Reduce Transparency is followed too')
        pg.evaluate("rerender()"); pg.wait_for_timeout(100)
        ok('this browser’s own Reduce Transparency setting is on' in pg.inner_text('#app'), 'and the page says why it’s on')
    else:
        print('  (skipped: this Chromium can’t emulate prefers-reduced-transparency)')
    pg.context.close()


SIZES = [('375', 375, 812), ('390', 390, 844), ('402', 402, 874), ('ipad', 820, 1180)]
GROW_ON_SCREEN = '.glass:is(.circ, .shbtn, .txtbtn, .cta, .tabpill, .trkpad, .trkpill, .ppill, .prep, .mktp), #timer[data-a="clock"]'


def clip(b, t, seed, sid):
    ok = t.ok
    for name, w, h in SIZES:
        for sc in ('light',) if name != '390' else ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, data=seed)
            pg.evaluate(SAFE, 24 if name == 'ipad' else 62)
            screens = [
                ('Today', "U.tab='today'", None),
                ('Songs', "U.tab='songs'", None),
                ('a song', f"U.tab='songs';U.view='lyr';U.songId='{sid}'", None),
                ('Exercises', "U.tab='exercises'", None),
                ('an exercise', "U.tab='exercises';U.view='ex';U.exId='humming';U.exTab='summary'", None),
                ('Settings', "U.tab='settings'", None),
                ('the calendar sheet', "U.tab='today'", '[data-a="openCal"]'),
            ]
            if name != 'ipad':
                screens.append(('the collapsed tab bar', "U.tab='songs'", 'min'))
            for label, js, then in screens:
                pg.evaluate(GO, js); pg.wait_for_timeout(200)
                if then == 'min':
                    pg.evaluate("setTabMin(true)"); pg.wait_for_timeout(100)
                elif then:
                    pg.locator('#app ' + then).first.click(); pg.wait_for_timeout(300)
                res = pg.evaluate(CLIP, GROW_ON_SCREEN)
                bad = [f"{r['cls']} “{r['label']}”: {', '.join(r['bad'])}" for r in res if r['bad']]
                ok(not bad, f'{name} {sc}, {label}: {len(res)} glass buttons pressed, none cut off or covered {bad}')
                if then == 'min': pg.evaluate("setTabMin(false)")
                if then and then != 'min': pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
            # a session (its clock pill and main button)
            pg.evaluate("()=>{newSession();go(()=>{U.view='found'})}"); pg.wait_for_timeout(250)
            for y in (0, 'end'):
                pg.evaluate(f"window.scrollTo(0,{'document.body.scrollHeight' if y == 'end' else 0})"); pg.wait_for_timeout(120)
                res = pg.evaluate(CLIP, GROW_ON_SCREEN)
                bad = [f"{r['cls']} “{r['label']}”: {', '.join(r['bad'])}" for r in res if r['bad']]
                ok(res and not bad, f'{name} {sc}, a session ({"bottom" if y else "top"}): {len(res)} pressed, none cut off or covered {bad}')
            pg.context.close()
        # the track player at this size
        pg = t.page(b, w=w, h=h, data=seed)
        pg.evaluate(SAFE, 24 if name == 'ipad' else 62)
        with_track(pg, sid)
        markers(pg)
        res = pg.evaluate(CLIP, GROW_ON_SCREEN)
        bad = [f"{r['cls']} “{r['label']}”: {', '.join(r['bad'])}" for r in res if r['bad']]
        ok(any('trkpad' in r['cls'] for r in res) and not bad, f'{name}, the track player: {len(res)} pressed, none cut off or covered {bad}')
        pg.context.close()


def run(b, t):
    need = lambda p: not PARTS or p in PARTS
    seed = sid = None
    if need('press') or need('clip'):
        seed, sid = song_seed(b)
    if need('material'): material(b, t)
    if need('press'): press(b, t, seed, sid)
    if need('solid'): solid(b, t)
    if need('motion'): motion(b, t)
    if need('reduced'): reduced(b, t)
    if need('transp'): transp(b, t)
    if need('clip'): clip(b, t, seed, sid)
