"""Q26 · Window: Picture in Picture. The floating window's audit fixes and its picture in picture.
Stage 1: every kind starts from a clean window (nothing carries over, e.g. the coach video's ✕ jumping to the top left),
and every ✕ and play button has a 44 pt touch area.
Stage 2, one look: the name first and the time below (no "Playing ·"), the session's step in the text colour after a
coloured dot, a readable red recording window, one progress line, one capsule shape, the dark ring track, and long
names losing their end. Text contrast is checked in light and dark.
Every fixture is synthetic (tones and a made-up video). No real music, recordings or course media are used."""
from harness import until
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
                x = pg.evaluate(VX)
                ok(x and x['right'] == 0 and x['dy'] == 0 and x['circle'],
                   f'{a} → video: the video’s ✕ stays at the top right with its dark circle (fix 2: {x})')
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


PARTS = ['clean', 'look']


def run(b, t):
    import os
    only = [p for p in os.environ.get('VS_PIP', '').split(',') if p]
    for p in PARTS:
        if not only or p in only:
            globals()[p](b, t)
