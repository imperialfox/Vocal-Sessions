"""Q26 · Window: Picture in Picture. The floating window's audit fixes and its picture in picture.
Stage 1: every kind starts from a clean window (nothing carries over, e.g. the coach video's ✕ jumping to the top left),
and every ✕ and play button has a 44 pt touch area.
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


PARTS = ['clean']


def run(b, t):
    import os
    only = [p for p in os.environ.get('VS_PIP', '').split(',') if p]
    for p in PARTS:
        if not only or p in only:
            globals()[p](b, t)
