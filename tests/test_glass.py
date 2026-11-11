"""Q33 Glass native tuning: the glass material in light and dark (tokens, rim, shadow, sheets keeping their strength),
the press (since Q53 the parts kit's: glass buttons grow by 17 pt along their longest side, part 12; buttons on a glass
bar only light up, part 15; solid buttons shrink to 0.93, part 14; KITPRESS in gestures.js gives each its kind), the
springs with motion on, Reduce Motion, Reduce transparency (the switch, kept after a reload, never in a backup, and the
browser's own setting), and no grown button cut off or covered at 375, 390 and 402 wide and on iPad.

VS_GLASS=material,press,solid,motion,reduced,transp,clip runs only those parts."""
import os, json
import harness
from test_layout import SONG
import test_track

PARTS = [p for p in os.environ.get('VS_GLASS', '').split(',') if p]

# press an element with a synthetic touch (no click follows), read what it looks like, then let go (pointercancel).
# The kit's light-up is its ::after layer (--lift-max), shown while .pk-pressed.
PRESS = """sel=>{const el=typeof sel==='string'?document.querySelector(sel):sel;if(!el)return null;
 el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'touch',isPrimary:true,button:0}));
 const cs=getComputedStyle(el),af=getComputedStyle(el,'::after'),r=el.getBoundingClientRect();
 const o={sel:typeof sel==='string'?sel:el.className,cls:el.className,w:el.offsetWidth,h:el.offsetHeight,
  want:1+17/Math.max(el.offsetWidth,el.offsetHeight),scale:cs.scale==='none'?1:parseFloat(cs.scale),
  z:cs.zIndex,pos:cs.position,lift:af.opacity,liftBg:af.backgroundColor,layer:af.content,
  max:getComputedStyle(document.documentElement).getPropertyValue('--lift-max').trim(),
  kind:KITPRESS.kind(el),has:el.classList.contains(KITPRESS.kind(el)),pressed:el.classList.contains('pk-pressed')};
 el.dispatchEvent(new PointerEvent('pointercancel',{bubbles:true,pointerType:'touch'}));
 o.after=getComputedStyle(el).scale;o.afterCls=el.classList.contains('pk-pressed');
 return o}"""
SETTLED = """sel=>{const el=document.querySelector(sel);if(!el)return false;const s=getComputedStyle(el).scale;
 return !el.classList.contains('pk-pressed')&&(s==='none'||s==='1')&&getComputedStyle(el,'::after').opacity==='0'}"""

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
  out.push({cls:el.className.replace(' pk-pressed',''),label:el.getAttribute('aria-label')||el.innerText.trim().slice(0,20),scale:+sc.toFixed(3),bad})}
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
      return {bg:c.backgroundColor,bf:c.backdropFilter||c.webkitBackdropFilter,sh:c.boxShadow,pad:be.padding,rim:be.backgroundImage,after:getComputedStyle(e,'::after').content,op:getComputedStyle(e,'::after').opacity}}"""
    for sc in ('light', 'dark'):
        pg = t.page(b, sc=sc)
        g = pg.evaluate(G, '#bar .circ.glass')
        bar = pg.evaluate(G, '.dockrow .pk-tabbar')
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
        # Q53: its only ::after is the kit's light-up layer, which shows only while pressed
        ok(g['pad'] == '0.5px' and (g['after'] in ('none', 'normal') or (g['after'] == '""' and g['op'] == '0')),
           f'{sc}: a 0.5 pt hairline, and no shine layer ({g["after"]}, {g["op"]})')
        ok(bar and bar['bg'] == g['bg'], f'{sc}: the tab bar (the parts kit\'s, Q41) takes the same glass tint ({bar and bar["bf"]})')
        # sheets keep their strength and blur; they take the rim, the shadow and dark mode's saturation
        pg.evaluate(GO, "U.tab='today'"); pg.locator('#app [data-a="openCal"]').first.click(); pg.wait_for_timeout(250)
        s = pg.evaluate(G, '.sheet')
        h = pg.evaluate(G, '.shead')
        strong = 'rgba(250, 250, 252, 0.86)' if sc == 'light' else 'rgba(44, 44, 48, 0.86)'
        sat = '2.1' if sc == 'light' else '1.4'
        # Q41 the sheet is the parts kit's: its strong glass (D15), the near-solid tint, the kit's sheet blur
        ok(s and s['bg'] == strong and s['bf'] == f'blur(10px) saturate({sat})',
           f'{sc}: a sheet is the parts kit\'s strong glass: the near-solid tint, its blur, with {sat} saturation ({s and s["bf"]})')
        ok(s and s['sh'] == g['sh'] and s['pad'] == '0.5px', f'{sc}: and takes the new rim and shadow')
        ok(h and h['bf'] == 'none', f'{sc}: the sheet header is part of the kit\'s sheet, with no blur of its own ({h and h["bf"]})')
        t.shot(pg, f'calendar-{sc}')
        pg.context.close()
    # the other blurs the handoff named take the new material too
    pg = t.page(b)
    rules = pg.evaluate("""()=>{const o={};for(const sh of document.styleSheets){for(const r of sh.cssRules){if(['.fwtabin'].includes(r.selectorText))
      o[r.selectorText]=(r.style.backdropFilter||r.style.webkitBackdropFilter)+' | '+r.style.boxShadow}}return o}""")
    ok(all('var(--glass-blur)' in v and 'var(--glass-rim)' in v for v in rules.values()) and len(rules) == 1,
       f'the floating window’s tuck tab uses the new material (Q41: menus are the parts kit\'s) ({rules})')
    pg.context.close()


def press(b, t, seed, sid):
    ok = t.ok

    def check(pg, sel, kind):
        o = pg.evaluate(PRESS, sel)
        if not o:
            ok(False, f'{sel}: on screen to press'); return
        if kind == 'grow':
            ok(o['kind'] == 'pk-press' and o['has'] and abs(o['scale'] - o['want']) <= 0.01,
               f'{sel} ({o["w"]}×{o["h"]}) grows through the kit (part 12) to ×{o["want"]:.3f} (1 + 17 ÷ {max(o["w"], o["h"])}): ×{o["scale"]:.3f}')
        else:
            ok(o['kind'] == 'pk-press-bar' and o['has'] and o['scale'] == 1,
               f'{sel} sits on a glass bar: through the kit (part 15) it doesn’t change size ({o["scale"]})')
        ok(o['pressed'] and o['lift'] == '1' and o['liftBg'].replace(' ', '') == o['max'].replace(' ', ''),
           f'{sel} lights up with a white layer under its icon ({o["lift"]}, {o["liftBg"]})')
        ok(o['pos'] != 'static' and int(o['z']) >= 10, f'{sel} is lifted above its neighbours while pressed (z {o["z"]})')
        back = harness.until(pg, SETTLED, 2000, sel)
        ok(back, f'{sel}: let go, it’s back to rest')

    pg = t.page(b, data=seed)
    # Today: the top bar's circle, the search circle, the tabs
    check(pg, '#bar .circ.glass', 'grow')
    # Q41 the search circle and the tabs are the parts kit's: the circle grows and (Q58, kit 1.4) a pressed tab raises
    # the Liquid Glass bubble (the kit's own, checked in its repo; 1.3's swelling highlight is Retired)
    box = pg.locator('.dockrow .scirc').bounding_box()
    pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2); pg.mouse.down(); pg.wait_for_timeout(250)
    ok(pg.evaluate("document.querySelector('.dockrow .scirc').matches('.pk-btn.pk-glass.pk-press')") and
       pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.dockrow .scirc')).scale)||1") > 1.05, 'the search circle grows while pressed (the kit\'s glass press)')
    pg.mouse.up(); pg.wait_for_timeout(200)
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(100)
    box = pg.locator('.dockrow .pk-tab:not(.on) >> nth=0').bounding_box()
    pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2); pg.mouse.down(); pg.wait_for_timeout(120)
    ok(pg.evaluate("Parts.bubble.state(document.querySelector('.dockrow .pk-tabbar')).up") and pg.locator('.dockrow .pk-tab-ind.pk-live').count() == 0,
       'a pressed tab raises the Liquid Glass bubble, not the old swelling highlight (Q58)')
    pg.evaluate("window.dispatchEvent(new PointerEvent('pointercancel'))"); pg.mouse.up(); pg.wait_for_timeout(200)
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(100)
    # a real press with the mouse goes through the same rule
    box = pg.locator('#bar .circ.glass').bounding_box()
    pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2); pg.mouse.down()
    sc = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#bar .circ.glass')).scale)")
    pg.evaluate("window.dispatchEvent(new PointerEvent('pointercancel'))")
    pg.mouse.up()
    ok(abs(sc - (1 + 17 / box['width'])) <= 0.01, f'a real mouse press grows it too (×{sc:.3f})')
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
    """Q53: solid buttons press through the kit too (part 14, down to --press); rows highlight instead (D06); no app
    press code or :active shrink is left."""
    ok = t.ok
    pg = t.page(b)
    o = pg.evaluate(PRESS, '#app .cta.ink')
    ok(o and o['kind'] == 'pk-press-solid' and o['has'] and abs(o['scale'] - 0.93) < 0.005 and o['layer'] == 'none',
       f'Start session (solid) shrinks to 0.93 through the kit, with no light-up ({o and o["scale"]})')
    ok(o and o['after'] in ('1', 'none'), f'and comes back when let go ({o and o["after"]})')
    ok(pg.evaluate("KITPRESS.kind(document.querySelector('#app .row'))") is None and
       not pg.evaluate("document.querySelector('#app .row').matches('.pk-press, .pk-press-bar, .pk-press-solid')"),
       'list rows aren’t pressed buttons: they highlight (D06)')
    ok(pg.evaluate("typeof PRESS") == 'undefined', 'the app’s own PRESS is gone')
    act = pg.evaluate("""()=>{const out=[];for(const sh of document.styleSheets){if(!(sh.href||'').includes('app.css'))continue;
      for(const r of sh.cssRules){if(r.selectorText&&r.selectorText.includes(':active')&&/scale|transform/.test(r.style.transform+r.style.scale)&&r.style.transform!=='none')out.push(r.selectorText)}}return out}""")
    ok(not act, f'no :active shrink is left in app.css ({act})')
    pg.evaluate(GO, "U.tab='today'"); pg.locator('#app [data-a="openCal"]').first.click(); pg.wait_for_timeout(250)
    o = pg.evaluate(PRESS, '.calhead .circ')
    ok(o and o['kind'] == 'pk-press-solid' and abs(o['scale'] - 0.93) < 0.005, f'the calendar’s month arrows are solid buttons through the kit ({o and o["scale"]})')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    # a new button gets its kind as a finger first lands on it (never as it's drawn: no transitions on a redraw), and
    # a class rewritten later is put right the same way
    o = pg.evaluate("""()=>new Promise(res=>{const d=document.createElement('div');d.innerHTML='<button class="cta" id="q53a">A</button><button class="circ glass" id="q53b">B</button>';
      document.body.appendChild(d);setTimeout(()=>{const a=document.getElementById('q53a'),b=document.getElementById('q53b');const r={rest:a.className,anim:a.getAnimations().length};
      const down=e=>{e.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',isPrimary:true,button:0}));window.dispatchEvent(new PointerEvent('pointercancel'))};
      down(a);down(b);r.a=a.className;r.b=b.className;b.className='cta';down(b);r.b2=b.className;d.remove();res(r)},0)})""")
    ok(o['rest'] == 'cta' and o['anim'] == 0, f'a newly drawn button isn’t touched until it’s pressed ({o})')
    ok('pk-press-solid' in o['a'] and 'pk-press' in o['b'].split(), 'a new button gets its kit press as a finger lands')
    ok('pk-press-solid' in o['b2'] and 'pk-press' not in o['b2'].split(), 'and a button whose class changes is put right the same way')
    # chips (part 18): picking chips are the kit's, with no press; + Your own only acts, so it's solid
    pg.evaluate(GO, "U.sheet='addEx';U.sd={}"); pg.wait_for_timeout(250)
    ch = pg.evaluate("""()=>{const c=document.querySelector('#focusChips .chip');return c&&{kit:c.matches('.pk-chips.pk-static > .pk-chip'),kind:KITPRESS.kind(c)}}""")
    ok(ch and ch['kit'] and ch['kind'] is None, f'the focus chips are the kit’s chips, the app deciding the pick ({ch})')
    pg.locator('#focusChips .chip >> nth=1').click(); pg.wait_for_timeout(100)
    ok(pg.evaluate("[...document.querySelectorAll('#focusChips .chip')].map(c=>c.classList.contains('on'))") [:2] == [False, True],
       'tapping one picks it, as before')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    ok(pg.evaluate("""()=>{const d=document.createElement('div');d.innerHTML=chipsHTML(['A'],[],'k');document.body.appendChild(d);
      const add=d.querySelector('.chip.add'),c=d.querySelector('.pk-chip');KITPRESS.tagIn(d);const r=add.classList.contains('pk-press-solid')&&!add.classList.contains('pk-chip')&&!!c;d.remove();return r}"""),
       '+ Your own only acts: it keeps its look and shrinks (part 14)')
    # the Your voice steppers are the kit's (part 24), their halves only lighting up (part 15)
    pg.evaluate(GO, "U.tab='settings';U.view='set';U.setPg='voice'"); pg.wait_for_timeout(250)
    st = pg.evaluate("""()=>{const s=document.querySelector('.pvstep .pk-stepper.pk-glass');if(!s)return null;const h=[...s.querySelectorAll(':scope > button')];
      return {n:h.length,div:!!s.querySelector('.pk-stepper-div'),bar:h.every(b=>KITPRESS.kind(b)==='pk-press-bar'),acts:h.map(b=>b.dataset.a+':'+b.dataset.k)}}""")
    ok(st and st['n'] == 2 and st['div'] and st['bar'] and st['acts'] == ['patNudge:-1', 'patNudge:1'],
       f'Your voice’s steppers are the kit’s stepper, keeping their actions ({st})')
    o = pg.evaluate(PRESS, '.pvstep .pk-stepper > button')
    ok(o and o['scale'] == 1 and o['lift'] == '1', 'a stepper’s half lights up and doesn’t change size')
    before = pg.inner_text('#pv_hi')
    pg.locator('[data-a=patNudge][data-v=hi][data-k="1"]').click(); pg.wait_for_timeout(100)
    ok(pg.inner_text('#pv_hi') != before, f'and + still moves the note ({before} → {pg.inner_text("#pv_hi")})')
    pg.context.close()


def motion(b, t):
    ok = t.ok
    pg = t.page(b, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    o = pg.evaluate("""()=>new Promise(res=>{const el=document.querySelector('#bar .circ.glass');const want=1+17/Math.max(el.offsetWidth,el.offsetHeight);
      const sam=[],t0=performance.now();let phase='press';
      el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',isPrimary:true,button:0}));
      const tick=()=>{const t=performance.now()-t0,s=getComputedStyle(el).scale;sam.push([Math.round(t),phase,s==='none'?1:parseFloat(s),getComputedStyle(el,'::after').opacity]);
        if(phase==='press'&&t>450){phase='release';window.dispatchEvent(new PointerEvent('pointerup',{pointerType:'touch'}))}
        if(t<1500)requestAnimationFrame(tick);else res({want,sam,cls:el.classList.contains('pk-pressed')})};
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
    ok(not o['cls'], 'then it’s at rest again')
    lifts = [s[3] for s in pr if s[0] > 250]
    ok(lifts and lifts[-1] == '1', f'it lights up within about 150 ms ({lifts[-1:]})')
    ok(any(0 < float(s[3]) < 1 for s in pr if s[0] < 200), 'and the light-up fades in rather than snapping')
    # Q53 a solid button (part 14): down to --press quickly, back on the release spring
    o = pg.evaluate("""()=>new Promise(res=>{const el=document.querySelector('#app .cta.ink');el.scrollIntoView({block:'center'});
      const sam=[],t0=performance.now();let phase='press';
      el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',isPrimary:true,button:0}));
      const tick=()=>{const t=performance.now()-t0,s=getComputedStyle(el).scale;sam.push([Math.round(t),phase,s==='none'?1:parseFloat(s)]);
        if(phase==='press'&&t>400){phase='release';window.dispatchEvent(new PointerEvent('pointerup',{pointerType:'touch'}))}
        if(t<1400)requestAnimationFrame(tick);else res(sam)};requestAnimationFrame(tick)})""")
    pr = [s for s in o if s[1] == 'press']
    rl = [s for s in o if s[1] == 'release']
    ok(any(0.93 < s[2] < 0.995 for s in pr if s[0] < 120) and abs(pr[-1][2] - 0.93) < 0.005,
       f'a solid button eases down to ×0.93 ({[s[2] for s in pr[:4]]} … {pr[-1][2]:.3f})')
    ok(any(0.935 < s[2] < 0.995 for s in rl[:20]) and abs(rl[-1][2] - 1) < 0.003,
       f'and comes back to rest on the release spring, not at once ({[round(s[2], 3) for s in rl[:5]]})')
    pg.context.close()


def reduced(b, t):
    ok = t.ok
    pg = t.page(b, init="try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}")
    o = pg.evaluate("""()=>new Promise(res=>{const el=document.querySelector('#bar .circ.glass');const sam=[],t0=performance.now();
      el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',isPrimary:true,button:0}));
      const tick=()=>{const t=performance.now()-t0;sam.push([t,getComputedStyle(el).scale,getComputedStyle(el,'::after').opacity]);
        if(t<320)requestAnimationFrame(tick);else{window.dispatchEvent(new PointerEvent('pointerup',{pointerType:'touch'}));res(sam)}};requestAnimationFrame(tick)})""")
    ok(all(s[1] == 'none' for s in o), 'Reduce Motion: no growth')
    ok(any(s[2] not in ('0', '1') for s in o) and o[-1][2] == '1', 'the light-up still fades in')
    ok(harness.until(pg, "!document.querySelector('#bar .circ.glass').classList.contains('pk-pressed')&&getComputedStyle(document.querySelector('#bar .circ.glass'),'::after').opacity==='0'", 2000),
       'and fades out when let go')
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
GROW_ON_SCREEN = '.glass:is(.circ, .shbtn, .txtbtn, .cta, .trkpad, .trkpill, .ppill, .prep, .mktp), #timer[data-a="clock"]'


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
            for label, js, then in screens:
                pg.evaluate(GO, js); pg.wait_for_timeout(200)
                if then:
                    pg.locator('#app ' + then).first.click(); pg.wait_for_timeout(300)
                res = pg.evaluate(CLIP, GROW_ON_SCREEN)
                bad = [f"{r['cls']} “{r['label']}”: {', '.join(r['bad'])}" for r in res if r['bad']]
                ok(not bad, f'{name} {sc}, {label}: {len(res)} glass buttons pressed, none cut off or covered {bad}')
                if then: pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
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
