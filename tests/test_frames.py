"""Q14 · Playback: Smooth Frames (3.34). Play-along and the track page do the least work they can on each frame, and
look exactly as before:
- play-along keeps its timing model between frames (no ckModel while playing) and finds its lines once per build
- a line change reads the layout first and only then writes, so no layout read ever follows a write in a frame
- Blur ahead goes only on lines on screen (and a screen either side), the rest have no filter
- a line tap in the big view and a punch-in never rebuild the view or redraw the app; the lines stay, their dots as a
  new build would draw them
- the track page draws the waveform's layer once and each frame copies it into place with just the playhead: no
  getComputedStyle, a marker added while playing shows at once, the colours follow the theme
- the Song card redraws only the row the playhead is in (and the one it left), and every row after a resize
The audio files are tones with gaps, written by the test. Nothing copyrighted is ever used."""
from test_track import F, loaded

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']

# a long song: 15 sections of 4 lines (60 lines), plain words
WORDS = ['morning', 'harbour', 'counting', 'paper', 'river', 'carry', 'lantern', 'window', 'silver', 'gentle']
LYR = '\n\n'.join(
    f'[{"Verse" if s % 2 == 0 else "Chorus"} {s // 2 + 1}]\n' +
    '\n'.join(' '.join(WORDS[(s * 4 + l + k) % 10] for k in range(6)) for l in range(4))
    for s in range(15))
ADD = """([t,a,l])=>{U.sDraft={step:1,title:t,artist:a,text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();return U.songId}"""
OPEN = "id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})"
QUIET = "TRACK.along=async()=>true"
# every line placed: 2 s each, a 0.6 s gap, and a 1.6 s gap after every third line (automatic dots)
PLACE = """id=>{const sg=songById(id),M=ckModel(sg);let t=0;const T=M.L.map((l,i)=>{const r=[t,t+2];t+=2+(i%3===2?1.6:0.6);return r});
  ckStore(sg,M.L,T,sg.order.map(()=>true),M.marks);rerender()}"""
# counts ckModel and render calls, and logs layout reads and DOM writes while __fw.on
INSTR = r"""(()=>{const F=window.__fw={on:false,log:[],model:0,render:0,gcs:0};
  const m=window.ckModel;window.ckModel=function(){F.model++;return m.apply(this,arguments)};
  const r=window.render;window.render=function(){F.render++;return r.apply(this,arguments)};
  const R=(P,n)=>{const d=Object.getOwnPropertyDescriptor(P,n);if(!d)return;Object.defineProperty(P,n,{configurable:true,get(){if(F.on)F.log.push('R '+n);return d.get.call(this)}})};
  ['offsetTop','offsetLeft','offsetHeight','offsetWidth'].forEach(n=>R(HTMLElement.prototype,n));
  ['clientHeight','clientWidth','scrollTop','scrollHeight','scrollWidth'].forEach(n=>R(Element.prototype,n));
  const gb=Element.prototype.getBoundingClientRect;Element.prototype.getBoundingClientRect=function(){if(F.on)F.log.push('R rect');return gb.call(this)};
  const gc=window.getComputedStyle;window.getComputedStyle=function(){F.gcs++;if(F.on)F.log.push('R style');return gc.apply(this,arguments)};
  const W=(P,n)=>{const d=Object.getOwnPropertyDescriptor(P,n);if(!d||!d.set)return;Object.defineProperty(P,n,{configurable:true,get:d.get,set(v){if(F.on)F.log.push('W '+n);d.set.call(this,v)}})};
  ['opacity','filter','transform'].forEach(n=>W(CSSStyleDeclaration.prototype,n));W(Node.prototype,'textContent');W(Element.prototype,'innerHTML');
  const sp=CSSStyleDeclaration.prototype.setProperty;CSSStyleDeclaration.prototype.setProperty=function(){if(F.on)F.log.push('W setProperty');return sp.apply(this,arguments)};
  ['add','remove','toggle'].forEach(n=>{const f=DOMTokenList.prototype[n];DOMTokenList.prototype[n]=function(){if(F.on)F.log.push('W class');return f.apply(this,arguments)}});
  const sa=Element.prototype.setAttribute;Element.prototype.setAttribute=function(){if(F.on)F.log.push('W attr');return sa.apply(this,arguments)};
  const ia=Element.prototype.insertAdjacentHTML;Element.prototype.insertAdjacentHTML=function(){if(F.on)F.log.push('W html');return ia.apply(this,arguments)};
  // canvas drawing per canvas (by id; '' is an off-screen layer)
  F.cv={};const C=CanvasRenderingContext2D.prototype;['fillRect','clearRect','drawImage','fillText'].forEach(n=>{const f=C[n];C[n]=function(){
    if(F.on){const k=(this.canvas.id||(this.canvas.isConnected?'row'+(this.canvas.parentNode&&this.canvas.parentNode.dataset.r):''))+':'+n;F.cv[k]=(F.cv[k]||0)+1}return f.apply(this,arguments)}});
})()"""
# play-along ticks with real frames between them: per tick, any layout read after a write
TICKS = """async([n,dt])=>{const F=__fw,bad=[],seen=new Set();F.model=0;F.render=0;
  for(let i=0;i<n;i++){F.on=true;F.log=[];CLOCK.advance(dt);F.on=false;
    const w=F.log.findIndex(x=>x[0]==='W'),r=F.log.slice(w<0?F.log.length:w).filter(x=>x[0]==='R');
    if(r.length)bad.push(i+': '+F.log.slice(0,12).join(','));
    const now=document.querySelector('#ckpa .ckl.now');if(now)seen.add(now.dataset.i);
    await new Promise(r=>requestAnimationFrame(()=>r()))}
  return {bad,model:F.model,render:F.render,lines:seen.size}}"""


def song(pg):
    sid = pg.evaluate(ADD, ['Long Song', 'Frames', LYR]); pg.wait_for_timeout(350)
    pg.evaluate(OPEN, sid); pg.wait_for_timeout(300)
    pg.evaluate("id=>TRACK.expect(id)", sid)
    pg.set_input_files('#trackIn', F('Frames 240.wav', 240))
    loaded(pg, sid)
    pg.evaluate(PLACE, sid)
    return sid


def clock(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = song(pg)
    ok(pg.evaluate("id=>ckModel(songById(id)).L.length", sid) == 60, 'a 60-line song with its track')
    pg.evaluate(QUIET); pg.evaluate("CLOCK.fake(performance.now())")
    pg.evaluate(OPEN, sid); pg.wait_for_timeout(300)
    pg.click('.ckrow [data-a=ckTile][data-v=timing]'); pg.wait_for_timeout(300)
    pg.evaluate(INSTR)
    # the first tap starts play-along without redrawing the app
    pg.click('#ckpa .ckl[data-i="0"]'); pg.wait_for_timeout(150)
    F = pg.evaluate("__fw")
    ok(pg.evaluate("CLOCK.state().run") and F['render'] == 0, f'tapping the first line starts play-along without a full redraw ({F["render"]})')
    ok(pg.locator('.cktr [data-a=ckFlag]').count() == 1 and 'hold to fix it' in pg.inner_text('#ckpa .ckcap'),
       'the transport shows Flag and the caption changes, as before')
    pg.evaluate("CLOCK.advance(0.5)")
    # 30 s of play in quarter seconds, with a real frame between each: about 12 line changes
    r = pg.evaluate(TICKS, [120, 0.25])
    ok(r['model'] == 0, f'no timing-model rebuild while playing ({r["model"]} over 120 frames)')
    ok(not r['bad'], f'no layout read after a write in any frame ({r["bad"][:3]})')
    ok(r['lines'] >= 10, f'the current line moved on through the song ({r["lines"]} lines)')
    ok(r['render'] == 0, 'playing never redraws the app')
    # the window's text every frame uses the kept model too
    n = pg.evaluate("(()=>{__fw.model=0;for(let i=0;i<30;i++)ckFwText();return __fw.model})()")
    ok(n == 0, f'the floating window\'s text doesn\'t rebuild the model ({n})')
    # Blur ahead: on screen lines blur by distance as before; far below, no filter
    st = pg.evaluate("""(()=>{const v=document.querySelector('#ckpa .ckview').getBoundingClientRect(),a=+document.querySelector('#ckpa .ckl.now').dataset.i;
      return [...document.querySelectorAll('#ckpa .ckl')].map(l=>{const r=l.getBoundingClientRect(),i=+l.dataset.i;
        return {i,d:i-a,f:l.style.filter,on:r.bottom>=v.top&&r.top<=v.bottom,far:r.top>v.bottom+2*v.height,want:i>a?MOTION.blur(i-a):0}})})()""")
    onl = [x for x in st if x['on'] and x['d'] > 0]
    ok(onl and all(x['f'] == f"blur({x['want']}px)" for x in onl), f'every upcoming line on screen has its distance blur ({[x["f"] for x in onl][:6]})')
    far = [x for x in st if x['far']]
    ok(far and all(x['f'] == '' for x in far), f'lines far below the screen have no filter ({len(far)} lines)')
    ok(all(x['f'] == '' for x in st if x['d'] <= 0), 'past and current lines are never blurred')
    # a tap on a line while playing jumps without a full redraw
    pg.evaluate("__fw.render=0")
    pg.evaluate("document.querySelector('#ckpa .ckl[data-i=\"9\"]').click()"); pg.wait_for_timeout(150)
    M = pg.evaluate("id=>ckModel(songById(id)).T", sid)
    ok(abs(pg.evaluate("CLOCK.now()") - M[9][0]) < 0.01 and pg.evaluate("document.querySelector('#ckpa .ckl.now').dataset.i") == '9',
       'tapping a line jumps there')
    ok(pg.evaluate("__fw.render") == 0, 'a line tap doesn\'t redraw the app')
    st = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].slice(9,13).map(l=>l.style.filter)")
    ok(st[0] == '' and st[1] == 'blur(0.3px)' and st[3] == 'blur(0.9px)', f'the lines after it blur from there ({st})')
    # a punch-in fixes its line in place: the same lines stay, with the dots a new build would draw
    pg.evaluate("document.querySelectorAll('#ckpa .ckl').forEach(l=>l.__q14=1)")
    pg.evaluate("CLOCK.advance(0.1)")
    box = pg.locator('#ckpa .ckl.now').bounding_box()
    pg.mouse.move(box['x'] + 30, box['y'] + 10); pg.mouse.down(); pg.wait_for_timeout(650)
    ok(pg.locator('#ckpa .ckl.punch').count() == 1, 'holding the lyrics picks a line to punch in')
    # let go 1.2 s into the line: a 1.4 s gap before the next line, so it gains an automatic dot
    pg.evaluate("CLOCK.advance(1.25)")
    pg.evaluate("__fw.render=0")
    pg.mouse.up(); pg.wait_for_timeout(200)
    raw = pg.evaluate("id=>ckModel(songById(id)).raw", sid)
    ok(abs(raw[9][1] - raw[9][0] - 1.25) < 0.05, f'letting go sets the line\'s end ({raw[9]})')
    ok(pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].every(l=>l.__q14===1)"), 'the big view wasn\'t rebuilt: every line is the same element')
    ok(pg.evaluate("__fw.render") == 0, 'the punch-in didn\'t redraw the app')
    want = pg.evaluate("""id=>{const d=document.createElement('div');d.innerHTML=ckBuild(songById(id));
      return [...d.querySelectorAll('.ckl')].filter(l=>l.querySelector('.ckdot')).map(l=>+l.dataset.i)}""", sid)
    got = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].filter(l=>l.querySelector('.ckdot')).map(l=>+l.dataset.i)")
    ok(got == want and 9 in got and len(got) > 5, f'its dots are the ones a new build would draw ({got[:6]} vs {want[:6]})')
    ok(pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].every(l=>l.querySelectorAll('.ckdot').length<=1)"), 'no line has two dots')
    r = pg.evaluate(TICKS, [16, 0.25])
    ok(not r['bad'] and r['model'] == 0, f'after the punch-in, frames are still clean ({r["bad"][:2]}, {r["model"]})')
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(200)
    ok(abs(pg.evaluate("id=>ckModel(songById(id)).raw", sid)[9][1] - raw[9][1]) > 0.05, 'Undo takes the punch-in back')
    t.shot(pg, 'play')
    pg.context.close()


def player(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = song(pg)
    pg.evaluate("id=>TRACK.open(id)", sid); pg.wait_for_timeout(300)
    pg.evaluate("TRACK.setLevel(1,false)"); pg.wait_for_timeout(150)
    pg.evaluate(INSTR)
    pg.evaluate("TRACK.seek(20)"); pg.evaluate("TRACK.play()"); pg.wait_for_function("TRACK.state().playing", timeout=5000)
    pg.wait_for_timeout(300)
    r = pg.evaluate("""async()=>{const F=__fw;F.cv={};F.gcs=0;F.on=true;F.log=[];let n=0;
      await new Promise(res=>{const f=()=>{if(++n<40)requestAnimationFrame(f);else res()};requestAnimationFrame(f)});
      F.on=false;return {cv:F.cv,gcs:F.gcs,n}}""")
    cv, n = r['cv'], r['n']
    ok(r['gcs'] == 0, f'no getComputedStyle while playing ({r["gcs"]})')
    ok(cv.get('trkC:drawImage', 0) >= n - 4 and cv.get('trkC:fillRect', 0) <= cv.get('trkC:drawImage', 0) + 2,
       f'each frame copies the waveform layer into place and draws just the playhead ({cv})')
    ok(cv.get(':fillRect', 0) < 400, f'the layer itself is drawn rarely, not every frame ({cv.get(":fillRect", 0)} bar rects in 40 frames)')
    ok(cv.get('trkLC:fillText', 0) == 0 and cv.get('trkLC:drawImage', 0) >= n - 4, f'the line lane is copied too, its words drawn once ({cv})')
    ok(pg.evaluate("TRACK.now()") > 20.4, 'the track played on')
    # a marker added while playing shows straight away (the layer is drawn again)
    pg.click('[data-a=trkMkAdd]'); pg.wait_for_timeout(200)
    px = pg.evaluate("""(()=>{const c=document.getElementById('trkC'),g=c.getContext('2d'),k=c.width/c.getBoundingClientRect().width,
      t=TRACK.now(),m=songById(U.songId).markers[0].t,x=Math.round((c.width*TRK_HEAD+(m-t)*c.width/16)+11*k),
      d=g.getImageData(x,Math.round(11*k),1,1).data;return [d[0],d[1],d[2],d[3]]})()""")
    ok(px[3] > 200 and px[2] > 120 and px[1] < 120, f'a new marker\'s tab is drawn on the strip at once ({px})')
    pg.evaluate("TRACK.pause()"); pg.wait_for_timeout(150)
    # the colours follow the theme: dark bars are light
    BAR = """(()=>{const c=document.getElementById('trkC'),d=c.getContext('2d').getImageData(0,Math.round(c.height*0.58),c.width,1).data;let lo=0,hi=0;
      for(let i=0;i<d.length;i+=4){if(d[i+3]<250)continue;if(d[i]>200&&d[i+1]>200&&d[i+2]>200)hi++;if(d[i]<60&&d[i+1]<60&&d[i+2]<60)lo++}return [lo,hi]})()"""
    lo, hi = pg.evaluate(BAR)
    ok(lo > 20 and hi == 0, f'light: the bars are dark ({lo}, {hi})')
    pg.emulate_media(color_scheme='dark'); pg.evaluate("rerender()"); pg.wait_for_timeout(200)
    lo, hi = pg.evaluate(BAR)
    ok(hi > 20 and lo == 0, f'dark: the bars are drawn again light ({lo}, {hi})')
    pg.emulate_media(color_scheme='light'); pg.evaluate("rerender()"); pg.wait_for_timeout(150)
    # Song card: only the playhead's row is drawn while playing
    pg.evaluate("TRACK.setLevel(2,false)"); pg.wait_for_timeout(200)
    pg.evaluate("TRACK.seek(30)"); pg.evaluate("TRACK.play()"); pg.wait_for_function("TRACK.state().playing", timeout=5000)
    pg.wait_for_timeout(200)
    r = pg.evaluate("""async()=>{const F=__fw;F.cv={};F.on=true;let n=0;
      await new Promise(res=>{const f=()=>{if(++n<30)requestAnimationFrame(f);else res()};requestAnimationFrame(f)});
      F.on=false;return Object.keys(F.cv).filter(k=>k.endsWith(':clearRect')).map(k=>k.split(':')[0])}""")
    ok(r == ['row1'], f'only the row the playhead is in is drawn ({r})')
    pg.evaluate("TRACK.pause()"); pg.wait_for_timeout(100)
    rows = pg.evaluate("document.querySelectorAll('#app .trkrow canvas').length")
    ink = "[...document.querySelectorAll('#app .trkrow canvas')].map(c=>{const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i])n++;return n})"
    ok(rows == 10 and all(x > 100 for x in pg.evaluate(ink)), 'every row still shows its waveform')
    # a resize (rotating the iPad) draws every row again at its new size
    pg.set_viewport_size({'width': 430, 'height': 844}); pg.wait_for_timeout(300)
    fitd = pg.evaluate("[...document.querySelectorAll('#app .trkrow canvas')].every(c=>Math.abs(c.width-Math.round(c.getBoundingClientRect().width*devicePixelRatio))<=1)")
    ok(fitd and all(x > 100 for x in pg.evaluate(ink)), 'after a resize every row is drawn again at its new width')
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(200)
    pg.evaluate("TRACK.setLevel(1,false)"); pg.wait_for_timeout(200)
    t.shot(pg, 'player')
    pg.context.close()


def run(b, t):
    clock(b, t)
    player(b, t)
