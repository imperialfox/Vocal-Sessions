"""Q43 the pattern player's sounds: the recorded piano (17 notes in audio/piano/, played up to 1.5 semitones up or down),
the smoothed Soft tone and the new output (a fast limiter and a gentle ceiling, with a small room echo).
Offline renders in the page (OfflineAudioContext) check that no note ends in a jump, that the rolled chord can't clip
and that both sounds are as loud as Soft tone was (3.56's recipes and output are copied below as the yardstick).
Also: the piano is the default and a saved choice carries over, every place the player makes a note uses the new
sounds, a note before the recordings are ready (or when they fail) plays Soft tone with no message, and the
recordings are kept for offline. `VS_SOUND=render,choices,places,fallback,offline` runs only those parts."""
import os
from harness import ready, until, url, APP_PATH, SEED, UA_IPHONE, offline, online

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']
PARTS = set((os.environ.get('VS_SOUND') or 'render,choices,places,fallback,offline').split(','))

# JS helpers: M(buf) measures a render (peak, the biggest sample-to-sample step, RMS from a to b seconds);
# NOTES, CHORD and FAST are the sound test's tunes as [midi, start, length]; OLD(name, ev, secs) renders 3.56's
# Soft tone or Piano-ish through 3.56's output, as the yardstick.
JS = r"""
window.M=(b,a,z)=>{let pk=0,st=0,s=0,n=0;for(let c=0;c<b.numberOfChannels;c++){const x=b.getChannelData(c),i0=Math.floor((a||0)*b.sampleRate),i1=Math.min(x.length,Math.floor((z||b.duration)*b.sampleRate));
 for(let i=0;i<x.length;i++){const v=Math.abs(x[i]);if(v>pk)pk=v;if(i&&Math.abs(x[i]-x[i-1])>st)st=Math.abs(x[i]-x[i-1]);if(i>=i0&&i<i1){s+=x[i]*x[i];n++;}}}
 return {peak:pk,step:st,rms:Math.sqrt(s/Math.max(1,n))}};
// J(buf, a): the biggest jump from a seconds on, beyond the waveform's own movement (the second difference
// x[i] - 2x[i-1] + x[i-2], which is near 0 for any smooth wave and the size of the jump at a click)
window.J=(b,a)=>{let j=0;for(let c=0;c<b.numberOfChannels;c++){const x=b.getChannelData(c);for(let i=Math.max(2,Math.floor(a*b.sampleRate));i<x.length;i++){const v=Math.abs(x[i]-2*x[i-1]+x[i-2]);if(v>j)j=v}}return j};
// REL(id, old): one note at a time, low to high, short and long; the biggest jump from just before each release on
window.REL=async(id,old)=>{let j=0;for(const m of [43,52,60,67,74,81])for(const d of [0.12,0.33,1.1]){const s=0.05+d-0.004;
 const b=old?await OLDB(id,[[m,0,d]],d+1):await PAT.offline(d+1,t=>PAT.note(m,t,d,id,1));j=Math.max(j,J(b,s))}return j};
window.NOTES=(()=>{const s=0.3,ns=[60,62,64,67,69,67,64,62,60,64,67,72,71,67,64,60];return ns.map((m,i)=>[m,i*s,i===ns.length-1?0.9:s*0.92])})();
window.CHORD=(()=>{const ev=[],ch=(k,t,d)=>[k-12,k,k+4,k+7].forEach((m,i)=>ev.push([m,t+i*0.03,d]));ch(60,0,1.1);
 [60,62,64,65,67,65,64,62,60].forEach((m,i)=>ev.push([m,1.4+i*0.32,i===8?0.7:0.29]));ch(60,4.6,1.2);return ev})();
window.FAST=(()=>{const ns=[60,62,64,65,67,69,71,72,71,69,67,65,64,62,60,62,64,67,72,67,64,62,60];return ns.map((m,i)=>[m,i*0.125,i===ns.length-1?0.8:0.118])})();
window.NEW=(id,ev,secs)=>PAT.offline(secs,t=>ev.forEach(([m,a,d])=>PAT.note(m,t+a,d,id,1))).then(b=>M(b,0,secs));
window.OLD=(name,ev,secs)=>OLDB(name,ev,secs).then(b=>M(b,0,secs));
window.OLDB=(name,ev,secs)=>{const sr=48000,C=new OfflineAudioContext(2,Math.ceil(sr*secs),sr),hz=m=>440*Math.pow(2,(m-69)/12);
 const comp=C.createDynamicsCompressor();comp.threshold.value=-14;comp.ratio.value=4;const master=C.createGain();master.gain.value=0.9;master.connect(comp);comp.connect(C.destination);
 const bus=C.createGain();bus.connect(master);
 const soft=(f,t,d,out,v)=>{const o=C.createOscillator(),o2=C.createOscillator(),g2=C.createGain();o.type='sine';o2.type='triangle';o.frequency.value=f;o2.frequency.value=f;g2.gain.value=0.18;
  o.connect(out);o2.connect(g2);g2.connect(out);out.gain.setValueAtTime(0,t);out.gain.linearRampToValueAtTime(0.32*v,t+0.03);out.gain.setValueAtTime(0.32*v,t+d);out.gain.linearRampToValueAtTime(0,t+d+0.09);
  [o,o2].forEach(x=>{x.start(t);x.stop(t+d+0.12)})};
 const piano=(f,t,d,out,v)=>{const hold=Math.max(d,0.25),end=t+hold+0.5,low=f<165;out.gain.value=v;
  [[1,1,1.6],[2,0.55,1.1],[3,0.32,0.8],[4,0.2,0.6],[5,0.12,0.45],[6,0.07,0.35],[8,0.035,0.25]].forEach(([n,a,dec])=>{const o=C.createOscillator(),pg=C.createGain(),peak=0.3*a,rest=Math.max(peak*0.18,0.0004);
   o.frequency.value=f*n*(1+0.00035*n*n);o.connect(pg);pg.connect(out);pg.gain.setValueAtTime(0,t);pg.gain.linearRampToValueAtTime(peak,t+0.004);pg.gain.exponentialRampToValueAtTime(rest,t+dec*(low?1.4:1));
   pg.gain.setValueAtTime(rest,t+hold);pg.gain.exponentialRampToValueAtTime(0.0001,end);o.start(t);o.stop(end+0.02)})};
 const play=name==='soft'?soft:piano;ev.forEach(([m,a,d])=>{const g=C.createGain();g.connect(bus);play(hz(m),0.05+a,d,g,1)});
 return C.startRendering()};
window.__toasts=[];const _t=window.toast;window.toast=function(){__toasts.push(String(arguments[0]));return _t.apply(this,arguments)};0
"""

COUNT = """(()=>{const P=(window.BaseAudioContext||window.AudioContext).prototype;window.__n={src:0,osc:0,conv:0};
 const w=(k,f)=>{const o=P[f];P[f]=function(){__n[k]++;return o.apply(this,arguments)}};w('src','createBufferSource');w('osc','createOscillator');w('conv','createConvolver')})();0"""


def db(a, b):
    import math
    return 20 * math.log10(a / b)


def warm(pg):
    """Make the player's context as a tap would (PAT.tone), then wait for the recordings."""
    pg.evaluate("PAT.tone(60)")
    return until(pg, "PAT.piano()==='ready'", 15000)


def run(b, t):
    ok = t.ok
    if 'render' in PARTS: part_render(b, t, ok)
    if 'choices' in PARTS: part_choices(b, t, ok)
    if 'places' in PARTS: part_places(b, t, ok)
    if 'fallback' in PARTS: part_fallback(b, t, ok)
    if 'offline' in PARTS: part_offline(b, t, ok)


def part_render(b, t, ok):
    pg = t.page(b)
    pg.evaluate(JS)
    ok(pg.evaluate("PAT.piano()") == 'none', 'nothing is fetched before the player makes its sound')
    ok(warm(pg), 'the 17 recordings load once the player makes its sound')
    pg.evaluate("PAT.toneStop()")
    # the yardstick: 3.56 as it was
    old_soft = pg.evaluate("OLD('soft',NOTES,6)")
    old_pc = pg.evaluate("OLD('piano',CHORD,6.5)")
    old_j = pg.evaluate("REL('piano',true)")
    old_sc = pg.evaluate("OLD('soft',CHORD,6.5)")
    ok(old_j > 0.1 and old_pc['peak'] > 1.0 and old_sc['peak'] > 1.0,
       f"the yardstick shows what was wrong: Piano-ish's jump at a release {old_j:.2f}, chord peaks {old_sc['peak']:.2f} and {old_pc['peak']:.2f}")
    for sid, name in (('piano', 'the piano'), ('soft', 'Soft tone')):
        n = pg.evaluate("NEW(%r,NOTES,6)" % sid)
        j = pg.evaluate("REL(%r)" % sid)
        c = pg.evaluate("NEW(%r,CHORD,6.5)" % sid)
        ok(j < 0.05, f"{name}: no note ends in a jump (biggest at a release {j:.4f}, under 0.05)")
        ok(c['peak'] < 1.0, f"{name}: the rolled chord peaks below 1.0 ({c['peak']:.2f})")
        d = db(n['rms'], old_soft['rms'])
        ok(abs(d) <= 1.5, f"{name}: as loud as Soft tone was ({d:+.1f} dB)")
    e = pg.evaluate("NEW('ep',CHORD,6.5)")
    ok(e['peak'] < 1.0, f"Electric piano goes through the new output too: its chord peaks at {e['peak']:.2f}")
    # the player's own chord (triad) through its own call, and a note between recordings stays in tune
    tri = pg.evaluate("PAT.offline(2.5,t=>PAT.chord(PAT.triad(60),t,1.1,1)).then(b=>M(b))")
    ok(tri['peak'] < 1.0, f"the player's rolled four-note chord peaks below 1.0 ({tri['peak']:.2f})")
    hz = pg.evaluate("""PAT.offline(1.2,t=>PAT.note(61,t,1,'piano',1)).then(b=>{const x=b.getChannelData(0),sr=b.sampleRate,a=Math.floor(0.2*sr),z=Math.floor(0.9*sr);
      let best=0,bf=0;for(let f=250;f<300;f+=0.25){let re=0,im=0;for(let i=a;i<z;i++){const p=2*Math.PI*f*i/sr;re+=x[i]*Math.cos(p);im+=x[i]*Math.sin(p)}const m=re*re+im*im;if(m>best){best=m;bf=f}}return bf})""")
    ok(abs(hz - 277.18) < 2, f'C♯4, between recordings, is played from C4 sped up and stays in tune ({hz} Hz)')
    pg.context.close()


def part_choices(b, t, ok):
    pg = t.page(b, w=375, h=812)
    ok(pg.evaluate("PAT.state().opts.sound") == 'piano' and pg.evaluate("D.prefs.pat") is None, 'with nothing saved the sound is the piano, and nothing is saved')
    names = pg.evaluate("PAT.SOUNDS.map(s=>[s.id,s.name])")
    ok(names == [['soft', 'Soft tone'], ['piano', 'Piano'], ['ep', 'Electric piano']], f'the sounds: Soft tone, Piano, Electric piano ({names})')
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(100)
    ok(pg.inner_text('#app [data-zk="set:player"] .mut') == 'Piano', 'Settings › Pattern player says Piano')
    for sid, label in (('soft', 'Soft tone'), ('piano', 'Piano'), ('ep', 'Electric piano')):
        pg.evaluate("s=>{D.prefs.pat=Object.assign(D.prefs.pat||{},{sound:s});save()}", sid)
        pg.reload(); ready(pg)
        pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(100)
        ok(pg.evaluate("PAT.state().opts.sound") == sid and pg.inner_text('#app [data-zk="set:player"] .mut') == label, f'a saved {sid} choice opens as {label}')
    pg.context.close()


def part_places(b, t, ok):
    """Every place the player makes a note: the exercise page, a Patterns preview, the song ladder's tone, Practise in a
    key (PAT.hear) and the sample a sound pick plays. With the piano: recordings; with Soft tone: no recordings."""
    pg = t.page(b)
    pg.evaluate(COUNT)
    ok(warm(pg), 'the recordings are ready'); pg.evaluate("PAT.toneStop()")
    pg.evaluate("go(()=>{U.tab='exercises';U.view='ex';U.exId='humming';U.exTab='summary';U.exLv=null;U.prevTab='exercises'})"); pg.wait_for_timeout(300)
    places = {
        'the exercise page': "PAT.play()",
        'a Patterns preview': "PAT.preview(PAT.byN(3))",
        'the song ladder’s note (PAT.tone)': "PAT.tone(57)",
        'Practise in a key (PAT.hear)': "PAT.hear(5,55)",
    }
    for sid in ('piano', 'soft'):
        pg.evaluate("s=>{D.prefs.pat=Object.assign(D.prefs.pat||{},{sound:s});save()}", sid)
        for name, js in places.items():
            pg.evaluate("__n={src:0,osc:0,conv:0}")
            pg.evaluate(js); pg.wait_for_timeout(250)
            n = pg.evaluate("__n")
            pg.evaluate("PAT.state().playing&&PAT.stop();PAT.hearStop();PAT.toneStop()"); pg.wait_for_timeout(100)
            if sid == 'piano':
                ok(n['src'] > 0, f'{name} plays the recorded piano ({n})')
            else:
                ok(n['src'] == 0 and n['osc'] > 0, f'{name} plays Soft tone when it’s chosen ({n})')
    pg.evaluate("__n={src:0,osc:0,conv:0}")
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='player'})"); pg.wait_for_timeout(200)
    pg.click('[data-a=patSoundPick][data-v=piano]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("D.prefs.pat.sound") == 'piano' and pg.evaluate("__n.src") > 0, 'picking Piano in Settings plays a sample of it')
    ok(pg.evaluate("__n.conv") == 0, 'the room echo is made once, with the player’s context, not per note')
    pg.context.close()


def part_fallback(b, t, ok):
    """Before the recordings are ready, or when they can't be read, the piano plays Soft tone, with no message."""
    pg = t.page(b, ctx_args={'service_workers': 'block'})
    pg.evaluate(JS)
    pg.context.route('**/audio/piano/*.mp3', lambda r: r.fulfill(status=200, body=b'not an mp3', headers={'Content-Type': 'audio/mpeg'}))
    pg.evaluate("PAT.tone(60)")
    ok(until(pg, "PAT.piano()==='failed'", 10000), 'recordings that can’t be read leave the piano failed')
    pg.evaluate("PAT.toneStop()")
    p = pg.evaluate("NEW('piano',NOTES,6)")
    s = pg.evaluate("NEW('soft',NOTES,6)")
    ok(abs(db(p['rms'], s['rms'])) < 0.3, f"and it plays Soft tone instead ({db(p['rms'], s['rms']):+.2f} dB)")
    ok(pg.evaluate("__toasts.length") == 0 and pg.locator('.pk-toast').count() == 0, 'with no message')
    pg.context.close()
    # before they're ready: hold the files back, play, then let them through
    pg = t.page(b, ctx_args={'service_workers': 'block'})
    pg.evaluate(COUNT)
    held = []
    pg.context.route('**/audio/piano/*.mp3', lambda r: held.append(r))
    pg.evaluate("PAT.tone(60)"); pg.wait_for_timeout(200)
    ok(pg.evaluate("PAT.piano()") == 'loading' and pg.evaluate("__n.src") == 0 and pg.evaluate("__n.osc") > 0,
       'a note asked for while the recordings load plays Soft tone')
    for r in held: r.continue_()
    pg.context.unroute('**/audio/piano/*.mp3')
    ok(until(pg, "PAT.piano()==='ready'", 15000), 'then they finish loading')
    pg.evaluate("PAT.toneStop()"); pg.wait_for_timeout(100)
    pg.evaluate("__n.src=0;PAT.tone(60)"); pg.wait_for_timeout(150)
    ok(pg.evaluate("__n.src") > 0, 'and the next note is the piano')
    pg.evaluate("PAT.toneStop()")
    pg.context.close()


def part_offline(b, t, ok):
    """The service worker keeps the recordings, so the piano plays with no signal after the first launch."""
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, user_agent=UA_IPHONE, timezone_id='Europe/London')
    ctx.add_init_script("try{localStorage.setItem('vocalMotion','0')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(url(APP_PATH)); pg.evaluate(SEED, {'v2': True}); pg.reload(); ready(pg)
    ok(until(pg, "navigator.serviceWorker&&navigator.serviceWorker.controller!==null", 15000) or (pg.reload() or ready(pg) or until(pg, "navigator.serviceWorker.controller!==null", 15000)), 'the service worker looks after the page')
    ok(warm(pg), 'the recordings load online'); pg.evaluate("PAT.toneStop()")
    kept = pg.evaluate("async()=>{const c=await caches.open('vocal-sessions-v3');let n=0;for(const k of await c.keys())if(/\\/audio\\/piano\\/[A-G]s?\\d\\.mp3$/.test(new URL(k.url).pathname))n++;return n}")
    ok(kept == 17, f'all 17 are saved for offline use ({kept})')
    offline(APP_PATH)
    try:
        pg.reload(); ready(pg)
        pg.evaluate(COUNT)
        ok(warm(pg), 'with no signal, the recordings still load')
        pg.evaluate("PAT.toneStop()"); pg.wait_for_timeout(100)
        pg.evaluate("__n.src=0;PAT.tone(60)"); pg.wait_for_timeout(150)
        ok(pg.evaluate("__n.src") > 0, 'and the piano plays')
        pg.evaluate("PAT.toneStop()")
    finally:
        online(APP_PATH)
    ctx.close()
