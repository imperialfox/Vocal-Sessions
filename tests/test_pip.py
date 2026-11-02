"""Q26 · Window: Picture in Picture. The floating window's audit fixes and its picture in picture.
Stage 1: every kind starts from a clean window (nothing carries over, e.g. the coach video's ✕ jumping to the top left),
and every ✕ and play button has a 44 pt touch area.
Stage 2, one look: the name first and the time below (no "Playing ·"), the session's step in the text colour after a
coloured dot, a readable red recording window, one progress line, one capsule shape, the dark ring track, and long
names losing their end. Text contrast is checked in light and dark.
Stage 3, behaviour: room at the end of every page for the window in a bottom corner, a fade with Reduce Motion, a
cross-fade between kinds, the press, the lift while dragging, and a steady VoiceOver label.
Stage 4: the coach video as picture in picture (a clean picture, controls on a tap that fade after 3 s, L1 L2 L3, three
sizes by pinch and double-tap, remembered), and tucking every kind of window at either edge.
Every fixture is synthetic (tones and a made-up video). No real music, recordings or course media are used."""
import time
from harness import until
from test_window import CLEAR
from test_batch12 import setup_sounds, sounds, PLAYING, LAUNCH_ARGS as B12_ARGS

LAUNCH_ARGS = B12_ARGS
LEAVE = "go(()=>{U.view=null;U.tab='today'})"
AWAY = "go(()=>{U.view=null;U.tab='history'})"
SHOWN = "!!FW.shown&&!document.getElementById('fw').hidden"
# the window as drawn: its classes, its inline style (not where it sits) and the shape of its markup
SIG = """(()=>{const f=document.getElementById('fw'),st=[...f.style].filter(p=>p!=='transform').map(p=>p+':'+f.style.getPropertyValue(p)).sort();
 const tree=e=>[...e.children].map(c=>c.tagName+'.'+[...c.classList].sort().join('.')+'('+tree(c)+')').join(',');
 return [...f.classList].filter(c=>!['dragging','pressed'].includes(c)).sort().join(' ')+'|'+st.join(';')+'|'+tree(f).replace(/VIDEO[^,)]*\\(\\)/,'')})()"""
# every button in the window and how big its touch area is
TOUCH = """(()=>[...document.querySelectorAll('#fw button, #fw [role=button]')].filter(b=>b.offsetParent!==null&&getComputedStyle(b).visibility!=='hidden').map(b=>{
 const r=b.getBoundingClientRect();return {a:b.dataset.a||'',l:b.getAttribute('aria-label')||'',w:Math.round(r.width*10)/10,h:Math.round(r.height*10)/10}}))()"""
# the coach video's ✕: where it sits and whether its dark circle shows
VX = """(()=>{const f=document.getElementById('fw').getBoundingClientRect(),x=document.querySelector('#fw [data-a=fwX]');if(!x)return null;
 const r=x.getBoundingClientRect(),c=getComputedStyle(x,'::before');return {dx:Math.round(r.left-f.left),dy:Math.round(r.top-f.top),right:Math.round(f.right-r.right),
 circle:c.display!=='none'&&c.content!=='none',col:getComputedStyle(x).color}})()"""


def show(pg, kind, js):
    """Start a sound on Today and leave for Progress, where its window shows (a take's own screen is where it started)."""
    pg.evaluate(LEAVE)
    # 3.43 (not Q26's): the track started while play-along runs never gets its window (the along track's late pause
    # closes it); left for its own queue item. Play-along is stopped first here
    if kind == 'track': pg.evaluate("NOW.kind()==='clock'&&NOW.stop()")
    pg.evaluate(js)
    until(pg, PLAYING[kind], 6000)
    pg.evaluate(AWAY)
    if until(pg, "k=>FW.shown===k&&!document.getElementById('fw').hidden", 4000, kind): return True
    print('    (not shown:', pg.evaluate("JSON.stringify({shown:FW.shown,dis:FW.dis,now:NOW.kind(),trk:TRACK.state()})"), ')')
    return False


# ---------------------------------------------------------------- stage 1 · fixes 2 and 3
def clean(b, t):
    ok = t.ok
    pg, sid = setup_sounds(b, t)
    S = sounds(pg)
    kinds = ['take', 'track', 'clock', 'video']
    sig = {}
    for a in kinds:
        for k in kinds:
            if k == a: continue
            ok(show(pg, a, S[a]), f'{a}: its window shows')
            ok(show(pg, k, S[k]), f'{a} → {k}: {k}’s window takes over')
            sig.setdefault(k, set()).add(pg.evaluate(SIG))
            if k == 'video':
                pg.evaluate("fwCtl(true)")  # stage 4: the ✕ is one of the controls a tap shows
                x = pg.evaluate(VX)
                ok(x and x['dx'] == 4 and x['dy'] == 4 and x['circle'] and x['col'] == 'rgb(255, 255, 255)',
                   f'{a} → video: the video’s ✕ is where it belongs, white on its circle, never greyed (fix 2: {x})')
                pg.evaluate("fwCtl(false)")
                ok('hasx' not in pg.evaluate("document.getElementById('fw').className"), f'{a} → video: no hasx left on the window')
            small = [x for x in pg.evaluate(TOUCH) if x['w'] < 44 or x['h'] < 44]
            ok(not small, f'{k} (after {a}): every button has a 44 pt touch area (fix 3: {small})')
    for k, s in sig.items():
        ok(len(s) == 1, f'{k}’s window is drawn the same whichever kind had it before ({s if len(s) > 1 else 1})')
    pg.evaluate("NOW.stop()")
    # the session's window, after a sound had the window
    show(pg, 'take', S['take'])
    pg.evaluate("NOW.stop();stopPlayback();newSession();X.start=Date.now()-60000;saveDraft()"); pg.evaluate(AWAY)
    ok(until(pg, "FW.shown==='session'", 4000), 'a session’s window after a take’s')
    cls = pg.evaluate("document.getElementById('fw').className")
    ok('hasx' not in cls and 'paused' not in cls, f'nothing of the take’s window is left on the session’s ({cls})')
    small = [x for x in pg.evaluate(TOUCH) if x['w'] < 44 or x['h'] < 44]
    ok(not small, f'session: every button has a 44 pt touch area ({small})')
    pg.context.close()


# ---------------------------------------------------------------- stage 2 · one look (fixes 1, 4, 6–9, 11)
# the contrast of every piece of text in the window against what's behind it (the window's own background laid over
# the page's), as WCAG works it out
CONTRAST = """(()=>{const f=document.getElementById('fw');
 const rgb=s=>{const m=s.match(/[\\d.]+/g).map(Number);return {r:m[0],g:m[1],b:m[2],a:m.length>3?m[3]:1}};
 const over=(c,b)=>({r:c.r*c.a+b.r*(1-c.a),g:c.g*c.a+b.g*(1-c.a),b:c.b*c.a+b.b*(1-c.a),a:1});
 const L=c=>['r','g','b'].map(k=>{const v=c[k]/255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
 const page=rgb(getComputedStyle(document.body).backgroundColor),bg=over(rgb(getComputedStyle(f).backgroundColor),page);
 return [...f.querySelectorAll('.fwk,.fwkn,.fwt,.fwtm')].filter(e=>e.offsetParent!==null&&e.textContent.trim()).map(e=>{
   const c=over(rgb(getComputedStyle(e).color),bg),a=L(c),b=L(bg);return {t:e.textContent.trim().slice(0,24),c:Math.round((Math.max(a,b)+.05)/(Math.min(a,b)+.05)*100)/100}})})()"""
# the window's shape and its progress line
SHAPE = """(()=>{const f=document.getElementById('fw'),r=f.getBoundingClientRect(),cs=getComputedStyle(f),p=f.querySelector('.fwp');
 let line=null;if(p){const q=p.getBoundingClientRect(),i=p.querySelector('i');line={l:Math.round(q.left-r.left),r:Math.round(r.right-q.right),b:Math.round(r.bottom-q.bottom),h:q.height,
 col:getComputedStyle(i).backgroundColor}}
 return {h:Math.round(r.height),rad:cs.borderTopLeftRadius,line,accent:getComputedStyle(document.body).getPropertyValue('--accent').trim(),
 text:[...f.querySelectorAll('.fwk,.fwt,.fwtm')].map(e=>e.textContent).join(' | ')}})()"""
REC = """i=>{const el=fwEl();fwClean(el,'rectrack');FW_REC.draw(el,i);el.setAttribute('aria-label',i.label);FW.shown='rectrack';el.hidden=false;fwPlace(true)}"""
REC_INFO = {'k': 'Track under your take', 't': '1:42', 'p': 0.4, 'on': True, 'label': 'Track under your take, Harbour · Chorus',
            'sub': 'A much longer song name than fits · Chorus 2'}
BLUE = {'light': 'rgb(0, 122, 255)', 'dark': 'rgb(10, 132, 255)'}


def look(b, t):
    ok = t.ok
    import re
    for sc in ('light', 'dark'):
        pg, sid = setup_sounds(b, t)
        pg.emulate_media(color_scheme=sc)
        pg.evaluate("id=>{songById(id).name='A song with a name much too long to fit in the window';save()}", sid)
        S = sounds(pg)
        for k in ['take', 'track', 'clock']:
            ok(show(pg, k, S[k]), f'{sc} {k}: its window shows')
            pg.wait_for_timeout(700)  # a take or track shows its window paused only after half a second in
            for paused in (False, True):
                if paused: pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
                st = f'{sc} {k}{" paused" if paused else ""}'
                c = pg.evaluate(CONTRAST)
                ok(c and all(x['c'] >= 4.5 for x in c), f'{st}: every piece of text passes 4.5:1 ({c})')
                s = pg.evaluate(SHAPE)
                ok(s['h'] == 58 and s['rad'] == '22px', f'{st}: the 58 pt capsule with 22 pt corners ({s["h"]}, {s["rad"]})')
                ok('Playing' not in s['text'] and 'Paused' not in s['text'], f'{st}: no “Playing ·” or “Paused ·” ({s["text"]})')
                ok(re.search(r'\| \d+:\d\d$', s['text']), f'{st}: the name first, the time below ({s["text"]})')
                if k != 'clock':
                    ln = s['line']
                    ok(ln and ln['l'] == 0 and ln['r'] == 0 and ln['b'] == 0 and 2 <= ln['h'] <= 3 and ln['col'] == BLUE[sc],
                       f'{st}: a thin full-width progress line along the bottom edge, in the accent colour ({ln})')
            if k in ('take', 'track'):
                long = pg.evaluate("(()=>{const e=document.querySelector('#fw .fwk'),cs=getComputedStyle(e);return {t:e.textContent,o:cs.textOverflow,w:e.scrollWidth>e.clientWidth}})()")
                ok(long['t'].startswith('A song with a name') and long['o'] == 'ellipsis' and long['w'],
                   f'{sc} {k}: a long name keeps its start and loses its end ({long})')
            pg.evaluate("fwClose()")  # ✕, so it doesn't wait in the window
        # the video's progress line is the same line
        ok(show(pg, 'video', S['video']), f'{sc} video: its window shows')
        ln = pg.evaluate(SHAPE)['line']
        ok(ln and ln['l'] == 0 and ln['r'] == 0 and ln['b'] == 0 and ln['col'] == BLUE[sc], f'{sc} video: the same progress line ({ln})')
        pg.evaluate("NOW.stop();COACH.dismiss();FW.dis={take:1,track:1,clock:1,video:1}")
        # the session: the step's name in the text colour after a dot in its colour, the time below
        pg.evaluate("newSession();X.start=Date.now()-200000;X.fEnd=Date.now()-60000;saveDraft()"); pg.evaluate(AWAY)
        ok(until(pg, "FW.shown==='session'", 4000), f'{sc} session: its window shows')
        for paused in (False, True):
            if paused: pg.evaluate("togglePause()"); pg.wait_for_timeout(150)
            st = f'{sc} session{" paused" if paused else ""}'
            c = pg.evaluate(CONTRAST)
            ok(c and all(x['c'] >= 4.5 for x in c), f'{st}: every piece of text passes 4.5:1 (fix 1: {c})')
            s = pg.evaluate(SHAPE)
            ok(re.match(r'^Rotation \| \d+:\d\d$', s['text']) and s['h'] == 58, f'{st}: “Rotation” above its time, in the same capsule ({s["text"]})')
            d = pg.evaluate("[getComputedStyle(document.querySelector('#fw .fwdot')).backgroundColor,getComputedStyle(document.body).getPropertyValue('--rot').trim()]")
            ok(pg.evaluate("getComputedStyle(document.querySelector('#fw .fwkn')).color") == pg.evaluate("getComputedStyle(document.body).color"),
               f'{st}: the step’s name in the text colour')
        tr = pg.evaluate("getComputedStyle(document.querySelector('#fw .fwring')).getPropertyValue('--sck-track').trim()")
        ok((tr == 'rgba(150, 150, 160, 0.45)') == (sc == 'dark'), f'{sc}: the ring’s empty track is stronger in dark mode only ({tr})')
        t.shot(pg, f'session-{sc}')
        # the recording window (Q20's red track window), drawn as Application draws it
        pg.evaluate("togglePause();X=null;saveDraft()")
        pg.evaluate(REC, REC_INFO); pg.wait_for_timeout(150)
        c = pg.evaluate(CONTRAST)
        ok(c and all(x['c'] >= 4.5 for x in c), f'{sc} recording: white on the deeper red passes 4.5:1 (fix 4: {c})')
        s = pg.evaluate(SHAPE)
        ok(s['h'] == 58 and s['rad'] == '22px', f'{sc} recording: the same capsule, 58 pt with 22 pt corners ({s["h"]}, {s["rad"]})')
        lab = pg.evaluate("(()=>{const k=document.querySelector('#fw .fwk'),cs=getComputedStyle(k);return {t:k.textContent,tt:cs.textTransform,fs:cs.fontSize,svg:!!k.querySelector('svg')}})()")
        ok(lab['t'] == 'Track under your take' and lab['tt'] == 'none' and lab['fs'] == '13px' and lab['svg'],
           f'{sc} recording: “Track under your take” in normal case at 13 pt, with a drawn note ({lab})')
        ln = s['line']
        ok(ln and ln['l'] == 0 and ln['r'] == 0 and ln['b'] == 0, f'{sc} recording: the progress line along the bottom edge ({ln})')
        t.shot(pg, f'recording-{sc}')
        pg.context.close()


# ---------------------------------------------------------------- stage 3 · behaviour (fixes 10, 12–16)
# the last line of text on the page, scrolled to the very bottom, against the window
LAST = """(()=>{scrollTo(0,document.documentElement.scrollHeight);const w=document.createTreeWalker(document.getElementById('app'),NodeFilter.SHOW_TEXT);
 let last=null,n;while(n=w.nextNode()){if(!n.textContent.trim())continue;const p=n.parentElement;if(!p||p.closest('[hidden],.zm,#fw'))continue;
 const cs=getComputedStyle(p);if(cs.visibility==='hidden'||cs.display==='none'||p.offsetParent===null)continue;const r=document.createRange();r.selectNodeContents(n);
 const q=r.getBoundingClientRect();if(q.height&&(!last||q.bottom>=last.b))last={b:q.bottom,t:n.textContent.trim().slice(0,30)}}
 const f=document.getElementById('fw').getBoundingClientRect();return {last,top:f.top,room:getComputedStyle(document.documentElement).getPropertyValue('--fwroom').trim()}})()"""
RUNNING = "newSession();X.start=Date.now()-200000;saveDraft()"
MOTION_ON = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"
REDUCED = "try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}"
ANIMS = """(()=>document.getElementById('fw').getAnimations().filter(a=>!(a instanceof CSSTransition)).map(a=>{const k=a.effect.getKeyframes();return {props:[...new Set(k.flatMap(f=>Object.keys(f).filter(p=>!['offset','easing','composite','computedOffset'].includes(p))))].sort().join(','),d:+a.effect.getTiming().duration}}))()"""


def room(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate(RUNNING)
    for name, tab in [('Today', 'today'), ('Songs', 'songs'), ('Exercises', 'exercises'), ('Progress', 'history')]:
        pg.evaluate("t=>go(()=>{U.view=null;U.tab=t})", tab)
        ok(until(pg, "FW.shown==='session'", 4000), f'{name}: the session’s window shows')
        r = pg.evaluate(LAST)
        h = pg.evaluate("document.getElementById('fw').offsetHeight")
        ok(r['room'] == f'{h + 12}px', f'{name}: room at the end of the page for the window and its gap ({r["room"]})')
        ok(r['last'] and r['last']['b'] <= r['top'], f'{name}: scrolled to the bottom, the last line clears the window ({r})')
        if tab == 'history': t.shot(pg, 'room-progress')
    pg.evaluate("FW.corner='tr';fwPlace()")
    ok(pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--fwroom').trim()") == '0px', 'in a top corner, no extra room')
    pg.evaluate("FW.corner='br';fwPlace();X=null;saveDraft();rerender()")
    ok(until(pg, "!FW.shown") and pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--fwroom').trim()") == '0px',
       'with no window, no extra room')
    pg.context.close()


def reduced(b, t):
    ok = t.ok
    pg = t.page(b, touch=True, init=REDUCED)
    pg.evaluate(RUNNING); pg.evaluate(AWAY)
    ok(until(pg, "FW.shown==='session'", 4000), 'Reduce Motion: the window shows')
    a = pg.evaluate(ANIMS)
    ok(a == [{'props': 'opacity', 'd': 200}], f'Reduce Motion: it fades in over 0.2 s, nothing moving (fix 12: {a})')
    pg.wait_for_timeout(300)
    pg.evaluate("go(()=>{U.view='rot'})")
    a = pg.evaluate(ANIMS)
    ok(a == [{'props': 'opacity', 'd': 200}], f'Reduce Motion: and fades out over 0.2 s ({a})')
    ok(until(pg, "document.getElementById('fw').hidden", 1000), 'and is gone once it has faded')
    pg.context.close()


def swap(b, t):
    ok = t.ok
    for mode, init in (('motion', MOTION_ON), ('Reduce Motion', REDUCED)):
        pg, sid = setup_sounds(b, t) if False else (None, None)
        pg = t.page(b, touch=True, init=init, ctx_args={'permissions': ['microphone']})
        from test_batch12 import lyric_song, add_track, wav_take, SONG
        from test_coach import add as add_video, LONG
        sid = lyric_song(pg)
        pg.evaluate(wav_take(30), ['w1', sid, None, 1])
        add_video(pg, LONG)
        pg.evaluate(LEAVE)
        pg.evaluate("playTake('w1')"); until(pg, PLAYING['take'], 6000); pg.evaluate(AWAY)
        ok(until(pg, "FW.shown==='take'&&!document.getElementById('fw').getAnimations().length", 4000), f'{mode}: the take’s window')
        before = pg.evaluate("(()=>{const r=document.getElementById('fw').getBoundingClientRect();return [r.right,r.bottom]})()")
        pg.evaluate("COACH.play()")
        ok(until(pg, "FW.shown==='video'", 4000), f'{mode}: the coach video takes the window over')
        g = pg.evaluate("(()=>{const g=document.querySelector('.fwghost');return g?{n:document.querySelectorAll('.fwghost').length,v:g.querySelectorAll('video').length,ids:g.querySelectorAll('[id],[data-a]').length,aria:g.getAttribute('aria-hidden')}:null})()")
        ok(g and g['n'] == 1 and g['v'] == 0 and g['ids'] == 0 and g['aria'] == 'true',
           f'{mode}: a still copy of the take’s window fades out over it (no video, ids or actions in it: {g})')
        a = pg.evaluate(ANIMS)
        props = sorted(x['props'] for x in a)
        if mode == 'motion':
            ok('height,transform,width' in props and 'opacity' in props, f'motion: it cross-fades while it springs to its new size (fix 13: {a})')
        else:
            ok(props == ['opacity'], f'Reduce Motion: a cross-fade only, nothing moving ({a})')
        ok(until(pg, "!document.querySelector('.fwghost')&&!document.getElementById('fw').getAnimations().length", 3000), f'{mode}: then the copy goes')
        after = pg.evaluate("(()=>{const r=document.getElementById('fw').getBoundingClientRect();return [r.right,r.bottom,r.width]})()")
        ok(abs(after[0] - before[0]) < 1.5 and abs(after[1] - before[1]) < 1.5 and pg.evaluate("FW.corner") == 'br',
           f'{mode}: the new size sits in the same corner ({before} → {after})')
        ok(pg.evaluate("document.querySelectorAll('video').length") == 1, f'{mode}: still only one video on the page')
        pg.context.close()


def touch(b, t):
    ok = t.ok
    from test_window import drag
    pg = t.page(b, touch=True)
    pg.evaluate(RUNNING); pg.evaluate(AWAY)
    ok(until(pg, "FW.shown==='session'", 4000), 'the session’s window')
    r = pg.evaluate("(()=>{const r=document.querySelector('#fw .fwring').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': r[0], 'y': r[1]}]}); pg.wait_for_timeout(80)
    s = pg.evaluate("[document.getElementById('fw').classList.contains('pressed'),getComputedStyle(document.getElementById('fw')).scale]")
    ok(s[0] and s[1] == '0.97', f'holding the window presses it down slightly, like a list row (fix 14: {s})')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); pg.wait_for_timeout(150)
    ok(not pg.evaluate("document.getElementById('fw').classList.contains('pressed')"), 'letting go, it comes back up')
    pg.tap('#fw .fwopen')  # (touches sent this way don't make a click; a real tap does)
    ok(until(pg, "U.view==='rot'||U.view==='found'", 2000), 'and a tap still goes back to the session')
    pg.evaluate(AWAY); until(pg, "FW.shown==='session'", 4000)
    b2 = pg.evaluate("(()=>{const r=document.querySelector('#fw .fwbtn').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': b2[0], 'y': b2[1]}]}); pg.wait_for_timeout(80)
    ok(not pg.evaluate("document.getElementById('fw').classList.contains('pressed')"), 'holding its play button presses only the button')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); pg.wait_for_timeout(200)
    if pg.evaluate("X.paused"): pg.evaluate("togglePause()")
    # the lift: held mid-drag
    c = pg.evaluate("(()=>{const r=document.getElementById('fw').getBoundingClientRect();return [r.left+40,r.top+29]})()")
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': c[0], 'y': c[1]}]})
    for i in range(1, 6):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': c[0] - i * 8, 'y': c[1] - i * 20}]}); pg.wait_for_timeout(16)
    s = pg.evaluate("(()=>{const f=document.getElementById('fw'),cs=getComputedStyle(f);return [f.classList.contains('dragging'),cs.scale,cs.boxShadow.split('rgba').length-1,f.classList.contains('pressed')]})()")
    ok(s[0] and s[1] == '1.06' and s[2] >= 4 and not s[3], f'dragging, it lifts: a little bigger, with a deeper shadow, and not pressed (fix 15: {s})')
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); pg.wait_for_timeout(400)
    s = pg.evaluate("(()=>{const f=document.getElementById('fw');return [f.classList.contains('dragging'),getComputedStyle(f).scale]})()")
    ok(not s[0] and s[1] in ('none', '1'), f'let go, it settles ({s})')
    cdp.detach()
    pg.context.close()


def voiceover(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(RUNNING); pg.evaluate("X.fEnd=Date.now()-60000;saveDraft()"); pg.evaluate(AWAY)
    ok(until(pg, "FW.shown==='session'", 4000), 'the session’s window')
    L = "(()=>{const f=document.getElementById('fw'),o=f.querySelector('.fwopen');return {g:f.getAttribute('aria-label'),o:o.getAttribute('aria-label'),d:o.getAttribute('aria-describedby'),t:document.getElementById(o.getAttribute('aria-describedby')||'x')?.textContent}})()"
    pg.evaluate("window.__lab=0;new MutationObserver(m=>{window.__lab+=m.length}).observe(document.getElementById('fw'),{attributes:true,subtree:true,attributeFilter:['aria-label','aria-describedby']})")
    a = pg.evaluate(L); pg.wait_for_timeout(2300); z = pg.evaluate(L)
    ok(a['g'] == 'Focused session, Rotation', f'the window’s label says what it is: “Focused session, Rotation” (fix 16: {a["g"]})')
    ok(a['o'] == 'Back to Rotation. Focused session, Rotation' and a['d'] == 'fwT', f'its button: where it goes, with the time as its description ({a})')
    ok(a['t'] != z['t'], f'the time ticks ({a["t"]} → {z["t"]})')
    ok(a['g'] == z['g'] and a['o'] == z['o'] and pg.evaluate("window.__lab") == 0,
       f'but no label is rewritten while it ticks, so VoiceOver doesn’t re-read it every second ({pg.evaluate("window.__lab")} changes)')
    pg.context.close()


# ---------------------------------------------------------------- stage 4 · picture in picture and tucking
from test_coach import CH
VRECT = "(()=>{const r=document.getElementById('fw').getBoundingClientRect();return {l:r.left,t:r.top,r:r.right,b:r.bottom,w:Math.round(r.width),h:Math.round(r.height)}})()"
CTL = "(()=>{const c=document.querySelector('#fw .fwvc');return !!c&&getComputedStyle(c).visibility==='visible'&&FW.ctl})()"
# where each control sits in the window
PARTS_AT = """(()=>{const f=document.getElementById('fw').getBoundingClientRect(),o={};
 document.querySelectorAll('#fw .fwvc button').forEach(b=>{if(b.offsetParent===null||getComputedStyle(b).display==='none')return;const r=b.getBoundingClientRect();
  o[(b.dataset.a||'')+(b.dataset.v||'')]={x:Math.round(r.left-f.left),y:Math.round(r.top-f.top),r:Math.round(f.right-r.right),b:Math.round(f.bottom-r.bottom),w:Math.round(r.width),h:Math.round(r.height)}});return o})()"""


def two_fingers(pg, c, d0, d1, steps=8):
    """A real two-finger pinch around c, from d0 to d1 px apart."""
    cdp = pg.context.new_cdp_session(pg)
    pts = lambda d: [{'x': c[0] - d / 2, 'y': c[1], 'id': 1}, {'x': c[0] + d / 2, 'y': c[1], 'id': 2}]
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': pts(d0)})
    for i in range(1, steps + 1):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': pts(d0 + (d1 - d0) * i / steps)}); pg.wait_for_timeout(16)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    pg.wait_for_timeout(300)
    cdp.detach()


def video_page(b, t, init=None):
    from test_coach import add as add_video, LONG
    pg = t.page(b, touch=True, init=init)
    add_video(pg, LONG)
    pg.evaluate(LEAVE); pg.evaluate("COACH.cue('humming',1,true)")
    until(pg, "!COACH.el().paused", 6000); pg.evaluate(AWAY)
    return pg


def pip(b, t):
    ok = t.ok
    pg = video_page(b, t)
    ok(until(pg, "FW.shown==='video'", 4000), 'the coach video’s window')
    r = pg.evaluate(VRECT)
    ok(r['w'] == 176 and r['h'] == 99, f'small: 176 × 99 ({r})')
    clean = pg.evaluate("(()=>{const f=document.getElementById('fw');return {bar:!!f.querySelector('.fwvb'),txt:[...f.querySelectorAll('*')].filter(e=>e.offsetParent!==null&&getComputedStyle(e).visibility==='visible'&&e.childElementCount===0&&e.textContent.trim()).map(e=>e.textContent)}})()")
    ok(not clean['bar'] and not clean['txt'] and not pg.evaluate(CTL), f'a clean picture: no bar, no words, no controls showing ({clean})')
    t.shot(pg, 'pip-clean')
    pg.tap('#fw .fwvopen')
    ok(until(pg, CTL, 1000), 'one tap shows the controls over the dimmed picture')
    at = pg.evaluate(PARTS_AT)
    ok(at.get('fwX', {}).get('x', 99) <= 6 and at['fwX']['y'] <= 6 and at.get('fwOpen', {}).get('r', 99) <= 6 and at['fwOpen']['y'] <= 6,
       f'✕ at the top left, open the player at the top right ({at.get("fwX")}, {at.get("fwOpen")})')
    ok('fwToggle' in at and 'fwSkip-10' not in at and all(f'fwLv{l}' in at for l in (1, 2, 3)),
       f'small: play/pause along the top, no ±10, and L1 L2 L3 along the bottom ({sorted(at)})')
    t.shot(pg, 'pip-small-controls')
    t0 = time.time()
    ok(until(pg, "!FW.ctl", 5000) and 2.5 < time.time() - t0 < 4.5, f'they fade after about 3 s ({time.time() - t0:.1f} s)')
    pg.tap('#fw .fwvopen'); until(pg, CTL, 1000)
    pg.wait_for_timeout(400)
    r = pg.evaluate(VRECT); pg.touchscreen.tap(r['l'] + 60, r['t'] + 48)  # the dimmed picture, between the buttons
    ok(until(pg, "!FW.ctl", 1000), 'tapping the dimmed picture again hides them')
    pg.wait_for_timeout(400)  # (two taps closer than 0.3 s are a double-tap)
    # the levels, as in the player (Q25)
    pg.tap('#fw .fwvopen'); until(pg, CTL, 1000); pg.wait_for_timeout(350)
    hm = CH[2] if pg.evaluate("COACH_MAP.humming") == 2 else [pg.evaluate("COACH_CH[COACH_MAP.humming][%d]" % i) for i in range(3)]
    pg.tap('#fw [data-a=fwLv][data-v="2"]')
    ok(until(pg, "COACH.here().l===2", 2000) and abs(pg.evaluate("COACH.el().currentTime") - hm[1]) < 0.5, 'L2 jumps to Level 2’s start')
    ok(until(pg, "document.querySelector('#fw [data-a=fwLv][data-v=\"2\"]').getAttribute('aria-pressed')==='true'", 2000), 'and L2 is lit')
    pg.wait_for_timeout(1200); pg.tap('#fw [data-a=fwLv][data-v="2"]')
    ok(abs(pg.evaluate("COACH.el().currentTime") - hm[1]) < 0.5, 'tapping the lit level starts it again (Q25)')
    pg.tap('#fw [data-a=fwLv][data-v="1"]')
    ok(until(pg, "COACH.here().l===1", 2000), 'L1 back to Level 1')
    ok(pg.evaluate(CTL), 'the controls stay while they’re used')
    # sizes: double-tap through them
    pg.evaluate("fwCtl(false)")
    B = pg.evaluate("(()=>{const B=fwBounds();return B.r-B.l})()")
    for want, w in (('m', 264), ('l', round(B)), ('s', 176)):
        pg.dblclick('#fw .fwvopen'); pg.wait_for_timeout(350)
        r = pg.evaluate(VRECT)
        ok(pg.evaluate("FW.vsize") == want and abs(r['w'] - w) <= 1 and abs(r['h'] - round(w * 9 / 16)) <= 1 and not pg.evaluate("FW.ctl"),
           f'double-tap: {want}, {w} pt wide at 16:9, controls as they were ({r}, ctl {pg.evaluate("FW.ctl")})')
        ok(pg.evaluate(CLEAR) == [], f'{want}: clear of the tab bar and top bar, in its corner')
    # medium and large: every control 44 pt
    for s in ('m', 'l'):
        pg.evaluate("s=>{FW.vsize=s;fwPlace();fwCtl(true)}", s); pg.wait_for_timeout(200)
        at = pg.evaluate(PARTS_AT)
        small = {k: v for k, v in at.items() if v['w'] < 44 or v['h'] < 44}
        ok(len(at) == 8 and not small, f'{s}: ✕, open, −10, play, +10 and L1 L2 L3, every one 44 pt ({len(at)}, {small})')
        t.shot(pg, f'pip-{s}-controls')
    t1 = pg.evaluate("COACH.el().currentTime")
    pg.tap('#fw [data-a=fwSkip][data-v="10"]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("COACH.el().currentTime") - t1 - 10) < 1, '+10 skips ten seconds on')
    pg.tap('#fw [data-a=fwSkip][data-v="-10"]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("COACH.el().currentTime") - t1) < 1, '−10 skips ten seconds back')
    pg.tap('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("COACH.el().paused") and pg.evaluate("FW.shown") == 'video', 'pause from the controls; the window stays')
    pg.tap('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    ok(not pg.evaluate("COACH.el().paused"), 'and play again')
    # pinch
    pg.evaluate("FW.vsize='s';fwCtl(false);fwPlace()"); pg.wait_for_timeout(100)
    r = pg.evaluate(VRECT); c = (r['l'] + r['w'] / 2, r['t'] + r['h'] / 2)
    two_fingers(pg, c, 60, 90)  # 1.5 × as wide: 264
    ok(pg.evaluate("FW.vsize") == 'm' and pg.evaluate(VRECT)['w'] == 264, f'pinching out: medium ({pg.evaluate(VRECT)})')
    r = pg.evaluate(VRECT); c = (r['l'] + r['w'] / 2, r['t'] + r['h'] / 2)
    two_fingers(pg, c, 60, 140)
    ok(pg.evaluate("FW.vsize") == 'l', 'pinching out again: large')
    r = pg.evaluate(VRECT); c = (r['l'] + r['w'] / 2, r['t'] + r['h'] / 2)
    two_fingers(pg, c, 200, 40)
    ok(pg.evaluate("FW.vsize") == 's' and pg.evaluate(VRECT)['w'] == 176, 'pinching in all the way: small')
    ok(pg.evaluate("FW.corner") == 'br' and pg.evaluate(CLEAR) == [], 'it stays in its corner')
    # remembered on this device
    r = pg.evaluate(VRECT); c = (r['l'] + r['w'] / 2, r['t'] + r['h'] / 2)
    two_fingers(pg, c, 60, 90)
    pg.reload(); from harness import ready; ready(pg)
    pg.evaluate("COACH.cue('humming',1,true)"); until(pg, "!COACH.el().paused", 6000); pg.evaluate(AWAY)
    ok(until(pg, "FW.shown==='video'", 4000) and pg.evaluate(VRECT)['w'] == 264, 'after a reload it comes back at medium, the last size used')
    pg.context.close()
    # sizes on the iPhone on its side and on iPad: large fits the room it has
    for name, w, h in (('land', 852, 393), ('ipad', 820, 1180)):
        from test_coach import add as add_video, LONG
        pg = t.page(b, w=w, h=h, touch=True)
        add_video(pg, LONG)
        pg.evaluate("COACH.cue('humming',1,true)"); until(pg, "!COACH.el().paused", 6000); pg.evaluate(AWAY)
        until(pg, "FW.shown==='video'", 4000)
        for s in ('s', 'm', 'l'):
            pg.evaluate("s=>{FW.vsize=s;fwPlace();fwCtl(true)}", s); pg.wait_for_timeout(150)
            ok(pg.evaluate(CLEAR) == [], f'{name} {s}: the picture fits, clear of the bars ({pg.evaluate(VRECT)})')
        t.shot(pg, f'pip-{name}-large')
        pg.context.close()


TUCK_KINDS = ['session', 'take', 'track', 'clock', 'video', 'coachpill', 'rectrack']
TUCKED = """(()=>{const f=document.getElementById('fw').getBoundingClientRect(),tb=document.getElementById('fwtab'),d=document.querySelector('.dock').getBoundingClientRect();
 const q=tb&&!tb.hidden?tb.getBoundingClientRect():null;return {tuck:FW.tuck,off:f.right<=0||f.left>=innerWidth,tab:q?{l:Math.round(q.left-d.left),r:Math.round(d.right-q.right)}:null,
 dot:!!tb&&tb.classList.contains('on')&&getComputedStyle(tb.querySelector('.fwtabdot')).display!=='none',room:getComputedStyle(document.documentElement).getPropertyValue('--fwroom').trim(),
 label:tb&&tb.getAttribute('aria-label'),inert:document.getElementById('fw').inert}})()"""


def tucking(b, t):
    ok = t.ok
    from test_window import drag
    pg, sid = setup_sounds(b, t)
    pg.context.close()  # (set-up only to warm the fixtures)
    for side in ('l', 'r'):
        pg, sid = setup_sounds(b, t)
        S = sounds(pg)
        for k in TUCK_KINDS:
            st = f'{k} ({"left" if side == "l" else "right"})'
            if k in S:
                ok(show(pg, k, S[k]), f'{st}: its window')
            elif k == 'session':
                pg.evaluate("newSession();X.start=Date.now()-200000;saveDraft()"); pg.evaluate(AWAY)
                ok(until(pg, "FW.shown==='session'", 4000), f'{st}: its window')
            elif k == 'coachpill':
                pg.evaluate("COACH.dismiss();FW.dis={};newSession();X.start=Date.now()-200000;saveDraft();go(()=>{U.view='found'})")
                until(pg, "FW.shown==='video'", 4000); pg.evaluate("fwClose()")
                ok(until(pg, "FW.shown==='coachpill'", 4000), f'{st}: the Coach pill')
            else:  # the red track window, as Application draws it while recording over the track
                pg.evaluate("X=null;saveDraft();go(()=>{U.view=null;U.tab='history'})")
                pg.evaluate("i=>{FW_REC.info=()=>i}", REC_INFO); pg.evaluate(REC, REC_INFO)
            pg.wait_for_timeout(700)
            # held near the side away from the edge, and pulled all the way to the edge
            r = pg.evaluate("s=>{const r=document.getElementById('fw').getBoundingClientRect();return [s==='l'?r.right-Math.min(30,r.width/4):r.left+Math.min(30,r.width/4),r.top+r.height/2]}", side)
            drag(pg, r[0], r[1], 4 if side == 'l' else 386, r[1] - 30, steps=10, stamp=16)
            s = pg.evaluate(TUCKED)
            ok(s['tuck'] == side and s['off'] and s['tab'] and s['tab']['l' if side == 'l' else 'r'] <= 1 and s['inert'],
               f'{st}: dragged off the edge, it tucks away and leaves a tab at that edge ({s})')
            ok(s['room'] == '0px', f'{st}: no room kept at the bottom of the page while tucked')
            if k in S:
                pg.wait_for_timeout(600)
                ok(pg.evaluate(PLAYING[k]) and s['dot'], f'{st}: it keeps playing, with the blue dot on the tab')
            elif k == 'session':
                a = pg.evaluate("Date.now()-X.start"); pg.wait_for_timeout(1100)
                ok(not pg.evaluate("X.paused") and pg.evaluate("Date.now()-X.start") > a and s['dot'], f'{st}: its clock keeps going, with the dot')
            if k == 'take' and side == 'l':
                t.shot(pg, 'tucked-take-left')
            # bring it back: a tap, or a pull
            if k in ('session', 'video', 'rectrack'):
                tb = pg.evaluate("(()=>{const r=document.getElementById('fwtab').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
                drag(pg, tb[0], tb[1], tb[0] + (60 if side == 'l' else -60), tb[1], steps=6, stamp=16)
                how = 'pulled out'
            else:
                pg.click('#fwtab'); pg.wait_for_timeout(500)
                how = 'tapped'
            s = pg.evaluate(TUCKED)
            ok(not s['tuck'] and s['tab'] is None and not s['inert'] and pg.evaluate("FW.corner[1]") == side and pg.evaluate(CLEAR) == [],
               f'{st}: the tab {how}, it comes back to its corner on that side ({s})')
            if k == 'coachpill':
                pg.evaluate("COACH.dismiss();FW.dis={};X=null;saveDraft();go(()=>{U.view=null;U.tab='history'})")
            elif k == 'session':
                pg.evaluate("X=null;saveDraft();rerender()")
            elif k == 'rectrack':
                pg.evaluate("FW.shown=null;fwUpdate()")
            else:
                pg.evaluate("fwClose()")
            pg.wait_for_timeout(300)
        pg.context.close()
    # a flick to a corner still goes to the corner; a tucked window stays tucked through a sheet
    pg = t.page(b, touch=True)
    pg.evaluate(RUNNING); pg.evaluate(AWAY); until(pg, "FW.shown==='session'", 4000)
    r = pg.evaluate("(()=>{const r=document.getElementById('fw').getBoundingClientRect();return [r.left+40,r.top+29]})()")
    drag(pg, r[0], r[1], r[0] - 120, r[1] - 300, steps=6, stamp=16)
    ok(not pg.evaluate("FW.tuck") and pg.evaluate("FW.corner") == 'tl', 'a flick from its corner still goes to a corner, not off the edge')
    r = pg.evaluate("(()=>{const r=document.getElementById('fw').getBoundingClientRect();return [r.left+r.width/2,r.top+29]})()")
    drag(pg, r[0], r[1], r[0] - 80, r[1], steps=3, ms=0, stamp=16)
    ok(pg.evaluate("FW.tuck") == 'l', 'thrown sideways off the edge, only partly over, it tucks')
    pg.click('#fwtab'); pg.wait_for_timeout(400)
    r = pg.evaluate("(()=>{const r=document.getElementById('fw').getBoundingClientRect();return [r.right-30,r.top+29]})()")
    drag(pg, r[0], r[1], 4, r[1], steps=10, stamp=16)
    ok(pg.evaluate("FW.tuck") == 'l', 'tucked on the left')
    pg.evaluate("U.sheet='calendar';rerender()"); pg.wait_for_timeout(250)
    ok(pg.evaluate("document.getElementById('fwtab').hidden"), 'a sheet hides the tab too')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(300)
    ok(pg.evaluate(TUCKED)['tab'] is not None and pg.evaluate("FW.tuck") == 'l', 'and it comes back still tucked')
    pg.evaluate("X=null;saveDraft();rerender()"); pg.wait_for_timeout(200)
    ok(not pg.evaluate("FW.tuck") and pg.evaluate("document.getElementById('fwtab').hidden"), 'with nothing going, the tab goes and the next window starts untucked')
    pg.context.close()


PARTS = ['clean', 'look', 'room', 'reduced', 'swap', 'touch', 'voiceover', 'pip', 'tucking']


def run(b, t):
    import os
    only = [p for p in os.environ.get('VS_PIP', '').split(',') if p]
    for p in PARTS:
        if not only or p in only:
            globals()[p](b, t)
