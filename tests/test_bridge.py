"""3.53 Exercises: Bridge-Aware Patterns (Q38): your bridge, saved with Your voice ({lo, hi}, checked by PAT.clean, in
backups, kept when the voice type changes); Find your bridge (VS-096): one slide drawn live with jump markers, the zone
suggested from the first jump (2 below its lower note to 1 above), From and To, Use this bridge, Try again, set it by
feel, the highest note, a blocked microphone, closing mid-slide letting go of the microphone, one sound at a time, and
its two doors (the exercise page's bridge line, Settings › Your voice); the exercise page (VS-014): the band, ringed
notes, the bridge line and its rounds, reference notes in the zone at 55%, the cue (Thinner · quieter on hums, the
narrower vowel on vowels, its switch); Stop one past last time (and the earlier stop winning with Stop at my top note);
Last time moving up only when a round's top is held cleanly while listening; Listen while I sing (the voice dot and
trail, the microphone through the shared audio service, nothing recorded); and 375 and 390 in light and dark, with
Reduce Motion. A fake microphone whose analyser plays synthetic tones only.
`VS_BRIDGE=data,sheet,page,cue,stop,listen,sizes` runs only those parts."""
import json, os, re
from harness import until
from test_backup import pick, write

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']
LV = "([id,lv])=>go(()=>{U.tab='exercises';U.view='ex';U.exId=id;U.exTab='summary';U.exLv={id,lv};U.prevTab='exercises'})"
ST = "PAT.state()"
FS = "PAT.fbState()"
WIDE = "document.documentElement.scrollWidth<=innerWidth+1"
NOTE = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B']
# the microphone's 2048 analyser hears window.__voice(seconds) as a MIDI note (null: silence); the meter's stays as is
MIC = """(()=>{const L=AUDIO.listen;window.__an=[];window.__voice=()=>null;AUDIO.listen=(s)=>{const m=L(s);if(!m)return m;const A=m.analyser;
 m.analyser=(n)=>{const a=A(n);__an.push(n);if(n!==2048)return a;const sr=a.context.sampleRate,t0=performance.now();
 a.getFloatTimeDomainData=(buf)=>{const v=__voice((performance.now()-t0)/1000);if(v==null){buf.fill(0);return}const f=440*Math.pow(2,(v-69)/12);
 for(let i=0;i<buf.length;i++){const ph=2*Math.PI*f*i/sr;buf[i]=0.3*(Math.sin(ph)+0.5*Math.sin(2*ph))}};return a};return m}})()"""
# a slow slide up from E3 that jumps from E4 to G4 at 2.5 s
SLIDE = "window.__voice=t=>t>5.5?null:t<2.5?52+t*4.8:67+(t-2.5)*2"
FAST = "D.prefs.pat=Object.assign(D.prefs.pat||{},{cue:false,spd:{1:11}});save()"


def name(m):
    return NOTE[m % 12] + str(m // 12 - 1)


def on_page(pg, id='humming', lv=1):
    pg.evaluate(LV, [id, lv])
    until(pg, "!!document.getElementById('pcCard')")


def first_round(pg):
    s = pg.evaluate(ST)
    semi = pg.evaluate(f"PAT.byN({s['pattern']}).semi")
    return s, semi


def data(b, t):
    ok = t.ok
    pg = t.page(b)
    s = pg.evaluate(ST)
    ok(s['bridge'] is None and s['last'] is None and pg.evaluate("D.prefs.pat") is None, 'data from before 3.53: no bridge, no Last time, nothing saved')
    ok({k: s['opts'][k] for k in ('stopLast', 'bcue', 'listen')} == {'stopLast': False, 'bcue': True, 'listen': False},
       'Stop one past last time and Listen while I sing start off; the bridge cue starts on')
    # checking: a bad bridge goes and the voice stays; a bad Last time goes; good ones are kept
    c = pg.evaluate("""PAT.clean({voice:{type:'Tenor',lo:44,hi:69,fal:74,bridge:{lo:67,hi:64}},ex:{humming:{p:1,last:{m:'x',at:1}},lip:{last:{m:60,at:1793000000000}}},
      stopLast:'yes',bcue:false,listen:true})""")
    ok(c == {'voice': {'type': 'Tenor', 'lo': 44, 'hi': 69, 'fal': 74}, 'ex': {'humming': {'p': 1}, 'lip': {'last': {'m': 60, 'at': 1793000000000}}}, 'bcue': False, 'listen': True},
       f'checking drops a bridge the wrong way round and a bad Last time, and keeps the rest ({c})')
    c = pg.evaluate("PAT.clean({voice:{type:'Custom',lo:44,hi:69,fal:74,bridge:{lo:64,hi:67,z:1}}}).voice.bridge")
    ok(c == {'lo': 64, 'hi': 67, 'z': 1}, 'a good bridge is kept, with fields it doesn’t know')
    # the voice type and the steppers keep the bridge
    pg.evaluate("PAT.setBridge(66,63)")
    ok(pg.evaluate("D.prefs.pat.voice.bridge") == {'lo': 63, 'hi': 66}, 'setting the bridge saves it lowest first, with Your voice')
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='voice'})"); pg.wait_for_timeout(100)
    pg.click('[data-a=patVoiceType]'); pg.click('[data-a=patMenuPick][data-v=Alto]'); pg.wait_for_timeout(100)
    v = pg.evaluate("D.prefs.pat.voice")
    ok(v['type'] == 'Alto' and v['bridge'] == {'lo': 63, 'hi': 66}, f'changing the voice type keeps the bridge ({v})')
    pg.click('[data-a=patNudge][data-v=hi][data-k="1"]'); pg.wait_for_timeout(100)
    v = pg.evaluate("D.prefs.pat.voice")
    ok(v['type'] == 'Custom' and v['bridge'] == {'lo': 63, 'hi': 66}, 'and so does a stepper')
    # reload and a backup round trip
    pg.evaluate("D.prefs.pat=Object.assign(D.prefs.pat,{stopLast:true,bcue:false,listen:true,ex:{humming:{last:{m:57,at:Date.now()}}}});save()")
    want = pg.evaluate("JSON.stringify(D.prefs.pat)")
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')", timeout=15000)
    ok(pg.evaluate("JSON.stringify(D.prefs.pat)") == want, 'the bridge, Last time and the three switches survive a reload')
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';render()"); pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    txt = pg.evaluate("pendingExport.file.text()")
    ok(json.dumps(json.loads(txt)['data']['prefs']['pat'], sort_keys=True) == json.dumps(json.loads(want), sort_keys=True), 'and go into the backup')
    p = write('bridge-now.json', raw=txt)
    pg.evaluate("U.sheet=null;D.prefs.pat={};save();render()")
    pick(pg, 'importPick', p)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("JSON.stringify(D.prefs.pat)") == want, 'restoring the backup brings them back')
    pg.context.close()


def sheet(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate(MIC)
    on_page(pg)
    ok('Find your bridge' in pg.inner_text('#pcBridge') and 'Find it' in pg.inner_text('#pcBridge'), 'with no bridge, the exercise page offers Find your bridge')
    pg.click('#pcBridge')
    ok(until(pg, "U.sheet==='bridge'") and pg.get_attribute('#layer .sheet', 'data-screen') == 'VS-096', 'its line opens the Find your bridge sheet (VS-096)')
    ok('Slide slowly up on “ee”' in pg.inner_text('#layer') and pg.locator('#layer [data-a=bfStart]').count() == 1, 'it explains the slide, with Start')
    pg.evaluate(SLIDE)
    pg.click('#layer [data-a=bfStart]')
    ok(until(pg, f"{FS}.listening&&{FS}.points>20", 8000), 'Start listens')
    ok(pg.evaluate("AUDIO.state().users") == 1 and 2048 in pg.evaluate("__an"), 'through the shared audio service, on one 2048 analyser')
    ok(until(pg, "(document.querySelector('#bfLive path')||{getAttribute:()=>''}).getAttribute('d').length>40"), 'the line draws live')
    ok(until(pg, "document.querySelectorAll('#bfLive .pj').length>=1", 8000), 'with a marker where the voice jumps')
    calls = pg.evaluate("""async()=>{let n=0;const g=document.getElementById.bind(document);document.getElementById=(id)=>{if(id==='bfLive')n++;return g(id)};
      await new Promise(r=>setTimeout(r,500));document.getElementById=g;return n}""")
    ok(calls == 0, f'the box isn’t looked up again while it’s on screen ({calls})')
    until(pg, f"{FS}.points>0&&performance.now()>0", 100)
    pg.wait_for_timeout(3200)
    pg.click('#layer [data-a=bfStop]')
    ok(until(pg, f"{FS}.phase==='done'"), 'Done stops listening')
    f = pg.evaluate(FS)
    txt = pg.inner_text('#layer')
    ok(pg.evaluate("AUDIO.state().users") == 0 and not f['listening'], 'and lets go of the microphone')
    j = f['jumps'][0]
    ok(round(j['from']) == 64 and round(j['to']) == 67, f'it finds the jump: E4 up to G4 ({j})')
    ok('Your voice jumped at E4, up to G4' in txt, f'and says so: {txt[:120]!r}')
    ok(f['lo'] == 62 and f['hi'] == 65 and pg.inner_text('#bf_lo') == 'D4' and pg.inner_text('#bf_hi') == 'F4', 'it suggests 2 below the jump’s lower note to 1 above: D4–F4')
    ok(re.search(r'Highest note: [A-G]', txt) and f['top'] >= 70, f'and shows the highest note reached ({f["top"]})')
    pg.click('#layer [data-a=bfStep][data-v=hi][data-k="1"]')
    ok(pg.inner_text('#bf_hi') == 'F♯4', 'To moves up a semitone')
    pg.click('#layer [data-a=bfStep][data-v=lo][data-k="1"]'); pg.click('#layer [data-a=bfStep][data-v=lo][data-k="1"]')
    pg.click('#layer [data-a=bfStep][data-v=lo][data-k="1"]'); pg.click('#layer [data-a=bfStep][data-v=lo][data-k="1"]')
    pg.click('#layer [data-a=bfStep][data-v=lo][data-k="1"]')
    ok(pg.inner_text('#bf_lo') == 'G4' and pg.inner_text('#bf_hi') == 'G4', 'From can’t pass To: it carries To with it')
    pg.click('#layer [data-a=bfStep][data-v=lo][data-k="-1"]'); pg.click('#layer [data-a=bfStep][data-v=lo][data-k="-1"]'); pg.click('#layer [data-a=bfStep][data-v=lo][data-k="-1"]')
    pg.click('#layer [data-a=bfUse]')
    ok(until(pg, "U.sheet===null") and pg.evaluate("D.prefs.pat.voice.bridge") == {'lo': 64, 'hi': 67}, 'Use this bridge saves it and closes the sheet')
    ok('Bridge set · E4–G4' in pg.evaluate("document.querySelector('.toast').textContent"), 'with a toast')
    ok(pg.inner_text('#pcBridge').startswith('Bridge E4–G4'), 'the exercise page now shows it')
    # the second door: Settings › Your voice
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='voice'})"); pg.wait_for_timeout(100)
    ok('E4–G4' in pg.inner_text('[data-a=patBridge]'), 'Settings › Your voice shows the bridge')
    pg.click('[data-a=patBridge]')
    ok(until(pg, "U.sheet==='bridge'"), 'and opens the same sheet')
    # no jump: set it by feel, the saved bridge kept as the start
    pg.evaluate("window.__voice=t=>t>1.6?null:60")
    pg.click('#layer [data-a=bfStart]'); until(pg, f"{FS}.points>20", 8000); pg.wait_for_timeout(1700)
    pg.click('#layer [data-a=bfStop]'); until(pg, f"{FS}.phase==='done'")
    ok('No jump this time' in pg.inner_text('#layer') and pg.inner_text('#bf_lo') == 'E4' and pg.inner_text('#bf_hi') == 'G4',
       'a slide with no jump says so, and From and To start on your bridge, to set by feel')
    ok(pg.locator('#layer [data-a=bfStart]').inner_text() == 'Try again', 'with Try again')
    pg.click('#layer [data-a=bfStart]')
    ok(until(pg, f"{FS}.phase==='listening'"), 'Try again listens again')
    # closing mid-slide lets go of the microphone
    until(pg, "AUDIO.state().users===1", 5000)
    pg.click('#layer .xbtn')
    ok(until(pg, "U.sheet===null&&AUDIO.state().users===0") and pg.evaluate(FS)['phase'] == 'ready', 'closing it mid-slide lets go of the microphone')
    # Set it by feel, straight away
    pg.click('[data-a=patBridge]'); until(pg, "U.sheet==='bridge'")
    pg.click('#layer [data-a=bfFeel]')
    ok('Set it by feel' in pg.inner_text('#layer') and pg.locator('#layer [data-a=bfUse]').count() == 1 and pg.evaluate("AUDIO.state().users") == 0,
       'Set it by feel goes straight to From and To, without the microphone')
    pg.click('#layer .xbtn'); until(pg, "U.sheet===null")
    # one sound at a time: whatever plays stops before it listens
    pg.evaluate("NOW.start('track','x',()=>{})")
    pg.click('[data-a=patBridge]'); until(pg, "U.sheet==='bridge'")
    pg.click('#layer [data-a=bfStart]')
    ok(pg.evaluate("NOW.kind()") is None, 'one sound at a time: anything playing stops before it listens')
    pg.click('#layer .xbtn'); until(pg, "U.sheet===null&&AUDIO.state().users===0", 5000)
    # a blocked microphone
    pg.evaluate("()=>{navigator.mediaDevices.getUserMedia=()=>Promise.reject(new Error('no'))}")
    pg.click('[data-a=patBridge]'); until(pg, "U.sheet==='bridge'")
    pg.click('#layer [data-a=bfStart]')
    ok(until(pg, f"{FS}.phase==='blocked'") and 'Microphone access was blocked' in pg.inner_text('#layer') and pg.locator('#layer [data-a=bfUse]').count() == 1,
       'a blocked microphone says so, and you can still set it by hand')
    t.shot(pg, 'blocked')
    pg.context.close()


def page(b, t):
    ok = t.ok
    pg = t.page(b)
    on_page(pg)
    ok(pg.locator('#pcDraw .pband').count() == 0 and pg.locator('#pcDraw .pring').count() == 0, 'no bridge: no band, no rings')
    s, semi = first_round(pg)
    r0 = s['route'][0]
    pg.evaluate(f"PAT.setBridge({r0 + 2},{r0 + 4});rerender()")
    zone = [r0 + x for x in semi if x is not None and r0 + 2 <= r0 + x <= r0 + 4]
    ok(pg.locator('#pcDraw .pband').count() == 1 and f'Bridge {name(r0 + 2)}–{name(r0 + 4)}' in pg.text_content('#pcDraw .pband'), 'the band sits behind the drawing, labelled with the zone')
    ok(pg.locator('#pcDraw .pring').count() == len(zone), f'notes in the zone are ringed ({len(zone)})')
    ok(pg.evaluate("[...document.querySelectorAll('#pcDraw .pring')].every(e=>getComputedStyle(e).stroke.startsWith('rgb(255, 149'))"), 'in orange')
    xs = [i + 1 for i, k in enumerate(s['route']) if any(x is not None and r0 + 2 <= k + x <= r0 + 4 for x in semi)]
    want = f'Bridge {name(r0 + 2)}–{name(r0 + 4)} · rounds {xs[0]}–{xs[-1]} cross it. Those notes play softer.'
    ok(want in pg.inner_text('#pcBridge') and 'Change' in pg.inner_text('#pcBridge'), f'the line names the rounds that cross it: {pg.inner_text("#pcBridge")!r}')
    # a zone no round reaches
    pg.evaluate("PAT.setBridge(100,102);rerender()")
    ok('no round crosses it' in pg.inner_text('#pcBridge') and pg.locator('#pcDraw .pband').count() == 0, 'a zone no round reaches says so, with no band')
    pg.evaluate(f"PAT.setBridge({r0 + 2},{r0 + 4});rerender()")
    # the start note moves: the line follows
    for _ in range(6): pg.click('[data-a=patShift][data-v="1"]'); pg.wait_for_timeout(40)
    r2 = pg.evaluate(ST)['route']
    xs2 = [i + 1 for i, k in enumerate(r2) if any(x is not None and r0 + 2 <= k + x <= r0 + 4 for x in semi)]
    ok(xs2 and f'rounds {xs2[0]}–{xs2[-1]}' in pg.inner_text('#pcBridge') or (len(xs2) == 1 and f'round {xs2[0]} ' in pg.inner_text('#pcBridge')),
       f'starting higher, the line follows ({pg.inner_text("#pcBridge")!r})')
    pg.evaluate("D.prefs.pat.ex={};save();rerender()")
    # softer notes: 55% in the zone, as many as are ringed
    pg.evaluate(FAST); on_page(pg)
    pg.click('#pPlay')
    ok(until(pg, "PAT.state().runs.length>=1", 5000), 'it plays')
    v = pg.evaluate(ST)['runs'][-1]['vols']
    ok(sorted(set(v)) == [0.55, 1] and v.count(0.55) == len(zone) and pg.evaluate("PAT.BRIDGE_VOL") == 0.55, f'the reference notes in the zone play at 55% ({v})')
    pg.click('#pPlay'); pg.wait_for_timeout(100)
    # Change opens the sheet
    pg.click('#pcBridge')
    ok(until(pg, "U.sheet==='bridge'"), 'Change opens Find your bridge')
    pg.click('#layer .xbtn'); until(pg, "U.sheet===null")
    # Settings › Pattern player has the two switches
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='player'})"); pg.wait_for_timeout(100)
    ok(pg.locator('[data-a=patBCue][aria-checked=true]').count() == 1 and pg.locator('[data-a=patListen][aria-checked=false]').count() == 1,
       'Settings › Pattern player has Bridge cue (on) and Listen while I sing (off)')
    pg.context.close()


def cue(b, t):
    ok = t.ok
    pg = t.page(b)

    def m(w):
        c = pg.evaluate("w=>PAT.cueOf(w)", w)
        return c and c['from'] + '>' + c['to']
    ok([m(w) for w in ('ah', 'wah', 'ee', 'hee', 'me', 'eh', 'may', 'hay', 'oh', 'woh', 'hoe', 'bow')] ==
       ['ah>uh', 'ah>uh', 'ee>ih', 'ee>ih', 'ee>ih', 'eh>ih', 'eh>ih', 'eh>ih', 'oh>uh', 'oh>uh', 'oh>uh', 'oh>uh'],
       'the narrower vowel: ah → uh, ee → ih, eh → ih, oh → uh')
    ok([m(w) for w in ('hmmm', 'brrr', 'runnng', 'hoo', 'mum')] == [None] * 5, 'hums, trills, ng and oo get no vowel: Thinner · quieter')
    # a hum: Thinner · quieter while a bridge note plays
    pg.evaluate(FAST); on_page(pg)
    s, semi = first_round(pg)
    r0 = s['route'][0]
    pg.evaluate(f"PAT.setBridge({r0 + 2},{r0 + 4});rerender()")
    ok(pg.locator('#pcCue[hidden]').count() == 1, 'the cue waits, hidden')
    pg.click('#pPlay')
    ok(until(pg, "PAT.state().cue", 6000) and pg.inner_text('#pcCue') == 'Thinner · quieter', 'Humming: “Thinner · quieter” while a bridge note plays')
    ok(until(pg, "!PAT.state().cue", 6000) and pg.locator('#pcCue[hidden]').count() == 1, 'and it goes once the notes leave the zone')
    pg.click('#pPlay'); pg.wait_for_timeout(100)
    # a vowel: the narrower one, plus quieter
    pg.evaluate("D.prefs.pat=Object.assign(D.prefs.pat,{vowel:'all',ex:{falsetto:{p:1}}});save()")
    on_page(pg, 'falsetto', 1)
    s, semi = first_round(pg)
    r0 = s['route'][0]
    pg.evaluate(f"PAT.setBridge({r0 + 2},{r0 + 4});rerender()")
    pg.click('#pPlay')
    ok(until(pg, "PAT.state().cue", 6000) and pg.inner_text('#pcCue') == 'ee ih · quieter' and pg.locator('#pcCue s').inner_text() == 'ee',
       f'a vowel exercise: the vowel crossed out, the narrower one and “quieter” ({pg.inner_text("#pcCue")!r})')
    pg.click('#pPlay'); pg.wait_for_timeout(100)
    # the switch turns it off
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='player'})"); pg.wait_for_timeout(100)
    pg.click('[data-a=patBCue]')
    ok(pg.evaluate("D.prefs.pat.bcue") is False, 'Settings › Pattern player › Bridge cue switches it off')
    on_page(pg, 'falsetto', 1)
    pg.click('#pPlay'); until(pg, "PAT.state().runs.length>=1", 5000)
    seen = pg.evaluate("""async()=>{let s=false;const e=Date.now()+2500;while(Date.now()<e){if(PAT.state().cue||!document.getElementById('pcCue').hidden)s=true;await new Promise(r=>setTimeout(r,40))}return s}""")
    ok(not seen, 'and then it never shows')
    pg.click('#pPlay')
    pg.context.close()


def stop(b, t):
    ok = t.ok
    pg = t.page(b)
    on_page(pg, 'flex', 1)
    s, semi = first_round(pg)
    hi = max(x for x in semi if x is not None)
    full = s['full']
    ok(pg.locator('#pcLast[hidden]').count() == 1, 'no Last time yet: nothing shown')
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='voice'})"); pg.wait_for_timeout(100)
    ok(pg.locator('[data-a=patStopTop] + [data-a=patStopLast]').count() == 1, 'Stop one past last time sits next to Stop at my top note')
    pg.click('[data-a=patStopLast]')
    ok(pg.evaluate("D.prefs.pat.stopLast") is True, 'and switches on')
    on_page(pg, 'flex', 1)
    ok(len(pg.evaluate(ST)['route']) == len(full) and 'Last time: not yet' in pg.inner_text('#pcLast'), 'with no Last time the route is whole, and the card says how to set it')
    lm = full[6] + hi
    pg.evaluate(f"D.prefs.pat.ex={{flex:{{last:{{m:{lm},at:Date.now()}}}}}};save();rerender()")
    ix = next(i for i, k in enumerate(full) if k + hi > lm)
    r = pg.evaluate(ST)['route']
    ok(len(r) == ix + 1, f'the route ends one round past Last time ({len(r)} of {len(full)}, Last time {name(lm)})')
    ok(pg.inner_text('#pcLast') == f'Last time: {name(lm)} · today · stops one round past it', f'“{pg.inner_text("#pcLast")}”')
    # both on: the earlier stop wins
    ta = full[4] + hi
    tn = max(1, next(i for i, k in enumerate(full) if k + hi > ta))
    pg.evaluate("D.prefs.pat.voice={type:'Custom',lo:40,hi:%d,fal:%d};D.prefs.pat.stopTop=true;save();rerender()" % (ta, ta))
    ok(tn < ix + 1 and len(pg.evaluate(ST)['route']) == tn, f'with Stop at my top note on too, the earlier stop wins (your top first: {tn} rounds)')
    pg.evaluate("D.prefs.pat.voice={type:'Custom',lo:40,hi:%d,fal:%d};save();rerender()" % (full[-1] + hi, full[-1] + hi))
    ok(len(pg.evaluate(ST)['route']) == ix + 1, 'and the other way (Last time first)')
    pg.evaluate("D.prefs.pat.stopTop=false;D.prefs.pat.stopLast=false;save();rerender()")
    ok(len(pg.evaluate(ST)['route']) == len(full) and pg.inner_text('#pcLast') == f'Last time: {name(lm)} · today', 'switched off, the route is whole and Last time is just a fact')
    pg.context.close()


def listen(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate(MIC)
    pg.evaluate(FAST)
    on_page(pg)
    s, semi = first_round(pg)
    r0 = s['route'][0]
    top = r0 + max(x for x in semi if x is not None)
    ok(pg.locator('#pcListen[aria-checked=false]').count() == 1 and 'Headphones' not in pg.inner_text('#pcListen'), 'Listen while I sing starts off')
    pg.click('#pcListen')
    ok(pg.evaluate("D.prefs.pat.listen") is True and pg.locator('#pcListen[aria-checked=true]').count() == 1 and 'Headphones in, so it only hears you' in pg.inner_text('#pcListen'),
       'on, it says “Headphones in, so it only hears you”')
    ok(not pg.evaluate(ST)['listening'] and pg.evaluate("AUDIO.state().users") == 0, 'it only listens while the pattern plays')
    pg.evaluate(f"window.__voice=()=>{top}")
    pg.evaluate("()=>{window.__rec=0;const S=MediaRecorder.prototype.start;MediaRecorder.prototype.start=function(){__rec++;return S.apply(this,arguments)}}")
    pg.click('#pPlay')
    ok(until(pg, "PAT.state().listening&&PAT.state().heard>10", 8000), 'Play listens')
    st = pg.evaluate("AUDIO.state()")
    ok(st['users'] == 1 and 2048 in pg.evaluate("__an") and pg.evaluate("NOW.kind()") == 'pattern', 'through the shared audio service, while the pattern’s sound plays on its own')
    ok(until(pg, "document.querySelector('#pcDraw .pvoice').style.display===''&&document.querySelector('#pcDraw .ptrail').getAttribute('points').length>10", 5000),
       'your voice shows as a dot and a trail on the drawing')
    ok(until(pg, f"(PAT.state().last||{{}}).m==={top}", 8000), f'holding the round’s top cleanly moves Last time up to it ({name(top)})')
    ok(pg.inner_text('#pcLast') == f'Last time: {name(top)} · today', 'quietly, on the card')
    ok(pg.evaluate("document.querySelectorAll('.toast').length") == 0 or 'Last' not in pg.evaluate("(document.querySelector('.toast')||{}).textContent||''"), 'with no message')
    # nothing looked up per frame for the voice
    calls = pg.evaluate("""async()=>{let n=0;const q=Element.prototype.querySelector;Element.prototype.querySelector=function(s){if(/pvoice|ptrail/.test(s))n++;return q.call(this,s)};
      await new Promise(r=>setTimeout(r,400));Element.prototype.querySelector=q;return n}""")
    ok(calls <= 2, f'the dot and trail are found once per round, not every frame ({calls})')
    pg.click('#pPlay'); pg.wait_for_timeout(200)
    ok(not pg.evaluate(ST)['listening'] and until(pg, "AUDIO.state().users===0", 3000), 'Stop lets go of the microphone')
    ok(pg.evaluate("__rec") == 0, 'nothing is recorded')
    # a wobbly top doesn't count; neither does a voice that never reaches it
    pg.evaluate("D.prefs.pat.ex={};save();rerender()")
    pg.evaluate(f"window.__voice=t=>{top}+(Math.floor(t*12)%2?1.6:-1.6)")
    pg.click('#pPlay'); until(pg, "PAT.state().heard>30", 8000); pg.wait_for_timeout(1500)
    ok(pg.evaluate(ST)['last'] is None, 'a top that wobbles more than a semitone isn’t held cleanly: Last time stays')
    # turning Listen off while playing stops listening at once
    pg.click('#pcListen')
    ok(until(pg, "!PAT.state().listening&&AUDIO.state().users===0", 3000) and pg.evaluate(ST)['playing'], 'switching Listen off mid-pattern lets go of the microphone and the pattern plays on')
    pg.evaluate(f"window.__voice=()=>{top}")
    pg.wait_for_timeout(2000)
    ok(pg.evaluate(ST)['last'] is None, 'without listening, Last time never changes')
    pg.click('#pPlay')
    # leaving the page stops listening
    pg.click('#pcListen'); pg.click('#pPlay'); until(pg, "PAT.state().listening", 5000)
    pg.click('#barL [aria-label^=Back]'); pg.wait_for_timeout(300)
    ok(not pg.evaluate(ST)['listening'] and until(pg, "AUDIO.state().users===0", 3000), 'going Back stops listening')
    pg.context.close()


def sizes(b, t):
    ok = t.ok
    for w, h in ((375, 667), (390, 844)):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, touch=True)
            pg.evaluate(MIC)
            on_page(pg)
            s, semi = first_round(pg)
            r0 = s['route'][0]
            pg.evaluate(f"PAT.setBridge({r0 + 2},{r0 + 4});D.prefs.pat=Object.assign(D.prefs.pat,{{listen:true,stopLast:true,ex:{{humming:{{last:{{m:{r0 + 9},at:Date.now()}}}}}}}});save();rerender()")
            ok(pg.evaluate(WIDE) and not re.search(r'undefined|NaN|null', pg.inner_text('#app')), f'{w} {sc}: the exercise page fits, nothing reads undefined')
            ok(pg.evaluate("[...document.querySelectorAll('#pcBridge,#pcLast,#pcListen')].every(e=>e.getBoundingClientRect().right<=innerWidth)"), f'{w} {sc}: the new lines fit the card')
            pg.evaluate("document.getElementById('pcCard').scrollIntoView()")
            t.shot(pg, f'page-{w}-{sc}')
            pg.click('#pcBridge'); until(pg, "U.sheet==='bridge'")
            t.shot(pg, f'sheet-{w}-{sc}')
            pg.evaluate(SLIDE); pg.click('#layer [data-a=bfStart]'); until(pg, f"{FS}.points>20", 8000); pg.wait_for_timeout(3000)
            t.shot(pg, f'slide-{w}-{sc}')
            pg.click('#layer [data-a=bfStop]'); until(pg, f"{FS}.phase==='done'")
            ok(pg.evaluate(WIDE) and not re.search(r'undefined|NaN|null', pg.inner_text('#layer')), f'{w} {sc}: the sheet fits, nothing reads undefined')
            ok(pg.evaluate("[...document.querySelectorAll('#layer button')].every(e=>{const r=e.getBoundingClientRect();return r.right<=innerWidth&&r.left>=0})"), f'{w} {sc}: its buttons fit')
            t.shot(pg, f'result-{w}-{sc}', full_page=True)
            pg.context.close()
    # Reduce Motion: the sheet opens and closes
    pg = t.page(b, touch=True, init="try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}")
    on_page(pg)
    pg.click('#pcBridge')
    ok(until(pg, "U.sheet==='bridge'") and until(pg, "!!document.querySelector('#layer .sheet')"), 'Reduce Motion: the sheet opens')
    pg.click('#layer .xbtn')
    ok(until(pg, "U.sheet===null"), 'and closes')
    pg.context.close()


PARTS = {'data': data, 'sheet': sheet, 'page': page, 'cue': cue, 'stop': stop, 'listen': listen, 'sizes': sizes}


def run(b, t):
    want = [p for p in os.environ.get('VS_BRIDGE', ','.join(PARTS)).split(',') if p]
    for k in want: PARTS[k](b, t)
