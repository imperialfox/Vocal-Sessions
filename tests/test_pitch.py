"""Q37 the shared pitch listener (PITCH, js/pitch.js): pitchy pinned as a classic script, a take's line (10 ms steps,
quiet frames skipped, short islands dropped, octave slips fixed, smoothing), sudden jumps, held notes, where one line
parts from another, takes read once and kept in memory only (never saved or backed up), the live line from an analyser
on the shared frame clock, and the pattern player's one-note call (PAT.tone) with Repeat and one sound at a time.
Synthetic tones made in the page only. `VS_PITCH=lib,line,jumps,held,part,takes,live,tone` runs only those parts."""
import os, json, re
from harness import until

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']

# JS: VOICE(segs, sr) → a Float32Array "voice": each segment [midi or null, seconds, opts], with a few harmonics, a soft
# start and end per note, and optional vibrato (cents) or a slide to another note. WAV(data, sr) → a 16-bit WAV Blob.
# MKTAKE([id, sid, o, segs, ext]) stores one as a take.
VOICE = """window.VOICE=(segs,sr)=>{sr=sr||44100;const n=Math.round(segs.reduce((a,s)=>a+s[1],0)*sr),out=new Float32Array(n);
 let i0=0,ph=0;for(const [m,d,o] of segs){const k=Math.round(d*sr),opt=o||{};if(m!=null){for(let i=0;i<k;i++){const u=i/sr,
 to=opt.to!=null?m+(opt.to-m)*(i/k):m,vib=(opt.vib||0)/100*Math.sin(2*Math.PI*5.5*u),f=440*Math.pow(2,(to+vib-69)/12);
 ph+=2*Math.PI*f/sr;const env=Math.min(1,u/0.02,(d-u)/0.02);out[i0+i]=0.25*env*(Math.sin(ph)+0.5*Math.sin(2*ph)+0.25*Math.sin(3*ph));}}
 i0+=k;}return out};
window.WAV=(d,sr)=>{const n=d.length,b=new ArrayBuffer(44+n*2),v=new DataView(b),w=(p,s)=>[...s].forEach((c,i)=>v.setUint8(p+i,c.charCodeAt(0)));
 w(0,'RIFF');v.setUint32(4,36+n*2,true);w(8,'WAVE');w(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);
 v.setUint32(24,sr,true);v.setUint32(28,sr*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);w(36,'data');v.setUint32(40,n*2,true);
 for(let i=0;i<n;i++)v.setInt16(44+i*2,Math.max(-1,Math.min(1,d[i]))*32000,true);return new Blob([b],{type:'audio/wav'})};
window.MKTAKE=async([id,sid,o,segs,ext,mins])=>{const sr=44100,d=VOICE(segs,sr),bl=WAV(d,sr);
 await putTake(Object.assign({id,songId:sid||'g_1',created:Date.now()-(mins||1)*6e4,len:Math.max(1,Math.round(d.length/sr)),size:bl.size,type:'audio/wav',blob:bl,star:false},o?{o}:{},ext?{ext}:{}));
 await refreshTakes();};0"""

LINE = "(segs)=>{const a=PITCH.line(VOICE(segs,44100),44100);return {n:a.n,first:a.first,firstT:a.firstT,lo:a.lo,hi:a.hi,read:a.read,dur:a.dur,s:Array.from(a.s,v=>isNaN(v)?null:Math.round(v*100)/100)}}"


def at(a, t):
    """The line's value t seconds from its start (not from the first note)."""
    i = int(round(t / 0.01))
    return a['s'][i] if 0 <= i < len(a['s']) else None


def page(b, t):
    pg = t.page(b)
    pg.evaluate(VOICE)
    return pg


def lib(b, t):
    ok = t.ok
    pg = page(b, t)
    ok(pg.evaluate("typeof Pitchy==='object'&&typeof Pitchy.PitchDetector==='function'&&PITCH.has()"), 'pitchy is a classic script: the global Pitchy, with PitchDetector')
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'js', 'pitchy.js'), encoding='utf-8').read()
    ok('pitchy 4.1.0' in src and 'MIT License' in src and 'Ian Johnson' in src and 'Fedor Indutny' in src and 'http' in src.split('\n')[0],
       'the pinned copy names its version and keeps both MIT notices (pitchy and fft.js)')
    ok(not re.search(r'^\s*(import|export)\s', src, re.M) and not re.search(r'fetch\(|importScripts|<script|src=', src), 'no modules and no CDN: it works offline')
    s = pg.evaluate("PITCH.SET")
    ok(s['hop'] == 0.01 and s['win'] == 2048 and s['clarity'] == 0.9 and s['island'] == 0.04 and s['octave'] == 0.15 and s['smooth'] == 0.025,
       'the agreed settings: 10 ms, 2048, clarity 0.90, 40 ms islands, ±150 ms octave check, 25 ms smoothing: ' + json.dumps(s))
    ok(s['jump'] == {'semi': 2, 'within': 0.2, 'steady': 1.2, 'side': 0.05} and s['held'] == {'min': 0.25, 'within': 1} and s['part'] == {'min': 0.1, 'semi': 0.6},
       'jumps, held notes and the parting spot as agreed')
    ok(pg.evaluate("[PITCH.name(60),PITCH.name(69),PITCH.name(66.4),PITCH.name(45)].join(' ')") == 'C4 A4 F♯4 A2', 'note names: C4, A4, F♯4, A2')
    pg.context.close()


def line(b, t):
    ok = t.ok
    pg = page(b, t)
    a = pg.evaluate(LINE, [[None, 0.3], [57, 1.0], [None, 0.3]])
    ok(abs(a['firstT'] - 0.3) < 0.06, 'the first note is found after the quiet start: ' + str(a['firstT']))
    mid = [v for v in a['s'][40:120] if v is not None]
    ok(len(mid) > 70 and all(abs(v - 57) < 0.15 for v in mid), 'a steady A3 reads as 57 throughout')
    ok(at(a, 0.1) is None and at(a, 1.45) is None, 'quiet frames read as no note')
    ok(abs(a['lo'] - 57) < 0.3 and abs(a['hi'] - 57) < 0.3, 'its range: lo and hi')
    # readings: an island under 40 ms is dropped; one of 40 ms is kept
    r = pg.evaluate("(()=>{const m=new Float32Array(100).fill(NaN);for(let i=10;i<13;i++)m[i]=60;for(let i=40;i<44;i++)m[i]=62;"
                    "const a=PITCH.shape(m,1);return [isNaN(a.s[11]),isNaN(a.s[41]),a.first]})()")
    ok(r == [True, False, 40], 'a 30 ms island of readings is dropped, a 40 ms one is kept: ' + json.dumps(r))
    # an octave slip for 60 ms in the middle of a held note is put back
    a = pg.evaluate(LINE, [[57, 0.5], [69, 0.06], [57, 0.5]])
    ok(all(v is None or abs(v - 57) < 0.6 for v in a['s'][45:65]), 'an octave slip is fixed against the median around it')
    # vibrato survives the smoothing; a held note with ±30 cents still reads within a semitone
    a = pg.evaluate(LINE, [[60, 1.2, {'vib': 30}]])
    vals = [v for v in a['s'] if v is not None]
    ok(vals and max(vals) - min(vals) < 0.9 and abs(sum(vals) / len(vals) - 60) < 0.15, 'vibrato reads around the note')
    # silence: no line at all
    a = pg.evaluate(LINE, [[None, 1]])
    ok(a['first'] == -1 and a['lo'] is None and a['read'] == 0, 'silence: no first note, nothing read')
    ok(pg.evaluate("(()=>{const t0=performance.now();PITCH.line(VOICE([[57,10]],44100),44100);return performance.now()-t0})()") < 4000,
       'ten seconds of voice reads in under 4 s')
    pg.context.close()


def jumps(b, t):
    ok = t.ok
    pg = page(b, t)
    J = "(segs)=>PITCH.jumps(PITCH.line(VOICE(segs,44100),44100)).map(j=>({t:Math.round(j.t*100)/100,from:Math.round(j.from*10)/10,to:Math.round(j.to*10)/10}))"
    j = pg.evaluate(J, [[66, 0.5], [69, 0.5]])
    ok(len(j) == 1 and abs(j[0]['from'] - 66) < 0.5 and abs(j[0]['to'] - 69) < 0.5 and abs(j[0]['t'] - 0.5) < 0.08,
       'a crack from F♯4 up to A4 is one jump, at 0.5 s: ' + json.dumps(j))
    j = pg.evaluate(J, [[62, 0.5, {'to': 66}], [66, 0.4]])
    ok(j == [], 'a slide over 500 ms is not a jump: ' + json.dumps(j))
    j = pg.evaluate(J, [[60, 0.4], [61, 0.4]])
    ok(j == [], 'a step of one semitone is not a jump')
    j = pg.evaluate(J, [[60, 0.4], [None, 0.35], [64, 0.4]])
    ok(j == [], 'a new note after a 350 ms breath is not a jump (more than 200 ms)')
    pg.context.close()


def held(b, t):
    ok = t.ok
    pg = page(b, t)
    H = "(segs)=>PITCH.held(PITCH.line(VOICE(segs,44100),44100)).map(h=>({t:Math.round(h.t*100)/100,d:Math.round(h.d*100)/100,m:Math.round(h.m*10)/10}))"
    h = pg.evaluate(H, [[60, 0.4], [62, 0.12], [64, 0.4], [None, 0.2], [67, 0.6]])
    ms = [round(x['m']) for x in h]
    ok(ms == [60, 64, 67], 'held notes: C4, E4 and G4, the 120 ms D4 between them left out: ' + json.dumps(h))
    ok(abs(h[0]['t']) < 0.03 and abs(h[-1]['d'] - 0.6) < 0.08, 'times from the first note, with their lengths')
    h = pg.evaluate(H, [[60, 0.2]])
    ok(h == [], 'a 200 ms note is not held (250 ms or more)')
    h = pg.evaluate(H, [[60, 0.8, {'to': 63}]])
    ok(all(abs(x['d']) < 0.8 for x in h), 'a three-semitone slide is never one held note')
    pg.context.close()


def part(b, t):
    ok = t.ok
    pg = page(b, t)
    P = "([a,b])=>{const x=PITCH.line(VOICE(a,44100),44100),y=PITCH.line(VOICE(b,44100),44100),p=PITCH.part(x,y);return p&&{at:Math.round(p.at*100)/100,len:Math.round(p.len*100)/100,t:Math.round(p.t*100)/100}}"
    trill = [[None, 0.2], [60, 0.5], [64, 0.5], [62, 0.5]]
    words = [[None, 0.6], [60, 0.5], [63, 0.5], [62, 0.5]]  # starts later, flat on the second note
    p = pg.evaluate(P, [trill, words])
    ok(p and abs(p['at'] - 0.5) < 0.08 and abs(p['len'] - 0.5) < 0.1, 'aligned at the first note, the words part on the second note: ' + json.dumps(p))
    ok(p and abs(p['t'] - 0.75) < 0.08, 'its middle is named by time')
    ok(pg.evaluate(P, [trill, trill]) is None, 'the same line: they never part')
    ok(pg.evaluate(P, [trill, [[None, 0.2], [60, 0.5], [64.4, 0.5], [62, 0.5]]]) is None, '0.4 semitone apart is staying with it')
    ok(pg.evaluate(P, [trill, [[None, 0.2], [60, 0.5], [64, 0.42], [66, 0.07], [64, 0.01], [62, 0.5]]]) is None, 'apart for under 100 ms is not a parting spot')
    p = pg.evaluate(P, [trill, [[None, 0.2], [60.8, 0.3], [60, 0.2], [64, 0.5], [60, 0.5]]])
    ok(p and abs(p['at'] - 1.0) < 0.1, 'the longest run wins (the last note, not the short start): ' + json.dumps(p))
    pg.context.close()


def takes(b, t):
    ok = t.ok
    pg = page(b, t)
    pg.evaluate("MKTAKE([ 'p1','g_1',null,[[null,0.2],[57,0.8],[60,0.8]] ])")
    r = pg.evaluate("""async()=>{const p1=PITCH.ofTake('p1'),p2=PITCH.ofTake('p1');const a=await p1;
      return {same:p1===p2,first:Math.round(a.firstT*100)/100,held:PITCH.held(a).map(h=>Math.round(h.m)),got:!!PITCH.got('p1')}}""")
    ok(r['same'] and r['got'], 'a take is read once and kept: the same promise, then its line straight away')
    ok(abs(r['first'] - 0.2) < 0.06 and r['held'] == [57, 60], 'its line, from the recording: ' + json.dumps(r))
    ok(pg.evaluate("PITCH.ofTake('nope').then(a=>a===null)"), 'a take that isn’t there gives no line')
    store = pg.evaluate("JSON.stringify(localStorage)")
    ok('"s":' not in store and 'firstT' not in store, 'lines are never saved')
    exp = pg.evaluate("async()=>{await prepareExport(false);return pendingExport&&pendingExport.file?await pendingExport.file.text():''}")
    ok(exp and 'firstT' not in exp and '"p1"' in exp, 'a backup carries the take but no pitch line')
    pg.evaluate("PITCH.forget('p1')")
    ok(not pg.evaluate("PITCH.got('p1')"), 'forget() lets one go')
    pg.context.close()


def live(b, t):
    ok = t.ok
    pg = page(b, t)
    # a fake analyser playing a steady A3 (with harmonics), then silence
    r = pg.evaluate("""async()=>{const sr=44100;let on=true,ph=0;const an={fftSize:2048,context:{sampleRate:sr},
      getFloatTimeDomainData(buf){for(let i=0;i<buf.length;i++){ph+=2*Math.PI*220/sr;buf[i]=on?0.3*(Math.sin(ph)+0.5*Math.sin(2*ph)):0}}};
      const seen=[];let calls=0;const stop=PITCH.live(an,(pts,p)=>{calls++;if(p)seen.push(p)});
      await new Promise(r=>setTimeout(r,500));const frames=AUDIO.state().frames;on=false;const n1=seen.length;
      await new Promise(r=>setTimeout(r,250));const n2=seen.length;stop();await new Promise(r=>setTimeout(r,60));
      return {n:n1,after:n2-n1,ms:seen.map(p=>Math.round(p.m*10)/10),ts:seen.map(p=>p.t),frames,left:AUDIO.state().frames,calls}}""")
    ok(r['n'] >= 10 and all(abs(m - 57) < 0.3 for m in r['ms']), 'live: a steady A3 reads as 57 from the analyser: ' + json.dumps(r['ms'][:8]))
    ok(r['after'] == 0, 'live: silence adds no points')
    ok(r['frames'] >= 1 and r['left'] == 0, 'live: it reads on the one frame clock, and stop() lets go of it')
    ok(r['ts'] == sorted(r['ts']) and r['ts'][-1] < 1.0, 'live: points carry their time from the start')
    ok(pg.evaluate("typeof PITCH.live(null,()=>{})==='function'"), 'live: no analyser, nothing happens')
    pg.context.close()


def tone(b, t):
    ok = t.ok
    pg = page(b, t)
    pg.evaluate("window.__ends=0;PAT.tone(57,{onEnd:()=>__ends++})")
    st = pg.evaluate("[NOW.kind(),NOW.id(),PAT.toneState()]")
    ok(st[0] == 'pattern' and st[1] == 'tone' and st[2]['m'] == 57 and not st[2]['repeat'], 'one note plays through NOW, in the pattern player’s sound: ' + json.dumps(st))
    ok(until(pg, "!PAT.toneState()&&__ends===1&&NOW.kind()===null", 4000), 'without Repeat it plays once and ends')
    pg.evaluate("window.__ends=0;PAT.tone(60,{repeat:true,onEnd:()=>__ends++})")
    ok(until(pg, "PAT.toneState()&&PAT.toneState().strikes>=3", 5000), 'with Repeat it strikes again every 1.5 s')
    ok(pg.evaluate("PAT.toneState().strikes") <= 3, 'and not faster than that')
    pg.evaluate("PAT.toneStop()")
    ok(pg.evaluate("!PAT.toneState()&&__ends===1&&NOW.kind()===null"), 'it stops when asked, once')
    # one sound at a time: a take starting stops a repeating note
    pg.evaluate("MKTAKE(['p2','g_1',null,[[57,1.5]]])")
    pg.evaluate("window.__ends=0;PAT.tone(62,{repeat:true,onEnd:()=>__ends++})")
    pg.evaluate("playTake('p2')")
    ok(until(pg, "!PAT.toneState()&&__ends===1&&NOW.kind()==='take'"), 'a take starting stops the note (one sound at a time)')
    pg.evaluate("stopPlayback()")
    # another note replaces the first
    pg.evaluate("window.__a=0;window.__b=0;PAT.tone(62,{repeat:true,onEnd:()=>__a++});PAT.tone(64,{repeat:true,onEnd:()=>__b++})")
    ok(pg.evaluate("__a===1&&__b===0&&PAT.toneState().m===64&&NOW.kind()==='pattern'"), 'a second note replaces the first')
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    pg.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
    ok(pg.evaluate("!PAT.toneState()&&__b===1"), 'leaving the app stops it')
    pg.context.close()


PARTS = {'lib': lib, 'line': line, 'jumps': jumps, 'held': held, 'part': part, 'takes': takes, 'live': live, 'tone': tone}


def run(b, t):
    want = [p for p in os.environ.get('VS_PITCH', ','.join(PARTS)).split(',') if p]
    for k in want: PARTS[k](b, t)
