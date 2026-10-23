"""Random-tap tester: taps, types, scrolls, resizes and reloads at random, checking after every step that nothing is broken.
Each seed is a repeatable run. More steps:  VS_FUZZ_STEPS=2000 python tests/run.py fuzz"""
import os, json, random, collections
from harness import with_song_practice, OUT, ready, now, iso, url, APP_PATH, fix

STEPS = int(os.environ.get('VS_FUZZ_STEPS', '200'))
# 3.19: a short synthetic track (tones with gaps), written once
TONES = os.path.join(OUT, 'fuzz-tones.wav')
if not os.path.exists(TONES):
    import wave, struct, math
    with wave.open(TONES, 'wb') as _w:
        _w.setnchannels(1); _w.setsampwidth(2); _w.setframerate(8000)
        _w.writeframes(b''.join(struct.pack('<h', int(6000 * math.sin(i / 4)) if (i // 4000) % 2 == 0 else 0) for i in range(8000 * 12)))
SEEDS = [int(s) for s in os.environ.get('VS_FUZZ_SEEDS', '11,12,13,14').split(',')]
SIZES=[(390,844,True),(375,667,True),(852,393,True),(820,1180,True),(1180,820,True),(1440,900,False),(320,568,True)]
TEXTS=['','x','  ','<b>bold</b> & "quotes" \'single\'','😀🎤 emoji','A'*300,'-5','0','999999','12.7','#tag','Line\nbreak']
INV=r"""(()=>{const p=[];const L=document.getElementById('layer');
 if(document.documentElement.scrollWidth>innerWidth+1)p.push('sideways scroll '+document.documentElement.scrollWidth+'>'+innerWidth);
 if(U.sheet&&!L.querySelector('.sheet'))p.push('sheet state "'+U.sheet+'" but nothing shown');
 if(!U.sheet&&L.querySelector('.sheet'))p.push('sheet shown without state');
 if(isFlow(U.view)&&!X)p.push('in a session view with no session');
 if(!U.sheet&&!U.view&&!U.sList&&!document.querySelector('[data-a=tab]'))p.push('no way to switch tabs');
 if(U.view==='lyr'&&!songById(U.songId))p.push('song screen with no song');
 D.songs.forEach(s=>{if(s.order&&s.order.some(x=>!s.sections[x.sid]))p.push('song '+s.id+' points at a missing section');});
 if(isFlow(U.view)&&!U.sheet&&!document.querySelector('#dock [data-a=cta]'))p.push('session view without its action button');
 for(const k in D.months){const v=D.months[k];if(!(v>=0)||!isFinite(v))p.push('bad month '+k+'='+v);}
 D.sessions.concat(D.songSessions).forEach(s=>{if(!(s.mins>0)||!isFinite(s.mins))p.push('bad mins '+s.id+'='+s.mins);if(isNaN(new Date(s.date)))p.push('bad date '+s.id);});
 for(const k in D.ex){const e=D.ex[k];if(!(e.n>=0))p.push('bad ex count '+k+'='+e.n);if(e.last&&isNaN(new Date(e.last)))p.push('bad last '+k);}
 const txt=(document.getElementById('app').innerText+' '+L.innerText+' '+document.getElementById('bar').innerText);
 if(/\bundefined\b|\bNaN\b|\[object Object\]|\bnull\b/.test(txt))p.push('bad text: '+(txt.match(/.{0,40}(undefined|NaN|\[object Object\]|\bnull\b).{0,30}/)||[''])[0]);
 if(X&&X.paused&&!X.pausedAt)p.push('paused without time');
 if(!rec&&(document.querySelector('.sgmodes.locked,.recbar')))p.push('song locked or recording bar shown without recording');
 if(!!document.querySelector('#dock .hcap')!==(recallOn()&&!U.sheet&&!rec))p.push('hint capsule shown when it shouldn\'t be, or missing in Recall');
 if(document.querySelector('.hx')&&!recallOn())p.push('hidden letters outside Recall');
 const fw=document.getElementById('fw'),ae=document.activeElement,typing=ae&&ae.matches&&ae.matches('input,textarea');
 if(FW.shown){if(U.sheet||L.firstElementChild)p.push('floating window over a sheet');if(rec)p.push('floating window while recording');
   if(FW.shown==='session'&&isFlow(U.view))p.push('session window on its own screen');
   const r=fw.getBoundingClientRect();if(!FW.drag&&!FW.stopSpring&&!fw.getAnimations().length&&(r.left<-1||r.right>innerWidth+1||r.top<-1||r.bottom>innerHeight+1))p.push('floating window off screen');}
 else if(X&&X.start&&!LAUNCH.busy()&&!isFlow(U.view)&&!U.sheet&&!U.clock&&!L.firstElementChild&&!rec&&!U.sFocus&&!typing)p.push('session running but no floating window');
 const cv=document.getElementById('cv'),cvs=document.querySelector('#app .cv-slot');
 if(document.querySelectorAll('video').length>1)p.push('more than one video element');
 if(cv&&cvs&&!cvs.contains(cv))p.push('coach video not in its slot');
 if(FW.shown==='video'&&(cvs||U.view==='coach'))p.push('video window on its own screen');
 if(FW.shown==='video'&&cv&&!fw.contains(cv))p.push('video window without the video');
 if(LAUNCH.busy()){window.__lb=window.__lb||performance.now();if(performance.now()-window.__lb>8000)p.push('launch ripple stuck')}else window.__lb=0;
 if(ZOOM.busy()){window.__zb=window.__zb||performance.now();if(performance.now()-window.__zb>5000)p.push('card zoom stuck')}else{window.__zb=0;
   if(document.querySelector('.zm'))p.push('a zoom layer left behind');if(document.querySelector('.zm-src'))p.push('a card left hidden after a zoom');}
 const ck=CLOCK.state();
 if(ck.wake&&!((ck.run&&songShown()&&songShown().id===ck.songId)||(ck.syncRun&&U.view==='ckSync')))p.push('wake lock held while not timing');
 if(FW.shown==='clock'&&FW_KINDS.find(k=>k.id==='clock').own())p.push('play-along window on its own screen');
 if(U.view!=='ckSync'&&(ck.syncing||ck.syncRun))p.push('Sync clock running after leaving Sync');
 if(!document.getElementById('ckpa').hidden&&!(ck.on&&songShown()&&!U.sEdit))p.push('play-along view shown without play-along');
 if(document.documentElement.classList.contains('ckplay')&&document.getElementById('ckpa').hidden)p.push('page scrolling locked without play-along');
 const tk=TRACK.state();
 if(FW.shown==='track'&&U.view==='trk'&&U.songId===tk.id)p.push('track window on its own screen');
 if(tk.playing&&!FW.shown&&!(U.view==='trk'&&U.songId===tk.id)&&!LAUNCH.busy()&&!U.sheet&&!U.clock&&!L.firstElementChild&&!rec&&!U.sFocus&&!typing)p.push('track playing with no way back to it');
 if(tk.playing&&((COACH.el()&&!COACH.el().paused)||(typeof player!=='undefined'&&player&&!player.paused)||ck.run))p.push('two sounds at once');
 if(tk.loaded&&!songById(tk.id))p.push('a deleted song’s track still loaded');
 if(U.view==='trk'&&!U.sheet&&TRACK.has(U.songId)&&tk.loaded&&tk.id===U.songId&&!document.querySelector('#dock .trktr'))p.push('track player without its transport');
 try{JSON.parse(localStorage.getItem('vocalTracker'))}catch(e){p.push('saved data unreadable')}
 const sumOk=Object.keys(D.months).length>=0;
 return p;})()"""
VIS=r"""(()=>{const L=document.getElementById('layer');const root=L.querySelector('.scrim,.clock')?L:document;
 const els=[...root.querySelectorAll('[data-a],input:not([type=file]),textarea')].filter(e=>{const r=e.getBoundingClientRect();if(r.width<2||r.height<2)return false;if(r.bottom<0||r.top>innerHeight||r.right<0||r.left>innerWidth)return false;
   const cx=Math.min(innerWidth-1,Math.max(0,r.left+r.width/2)),cy=Math.min(innerHeight-1,Math.max(0,r.top+r.height/2));const t=document.elementFromPoint(cx,cy);return t&&(t===e||e.contains(t)||t.closest('[data-a]')===e);});
 return els.map((e,i)=>{e.setAttribute('data-fz',i);return {i,a:e.dataset.a||e.tagName.toLowerCase(),v:e.dataset.v||'',k:e.dataset.k||'',id:e.id||'',type:e.type||''};});})()"""
# no microphone here: Record shows on a selected section, but recording itself is covered by test_recording and test_sections
SKIP = {'importPick', 'checkPick', 'exportSave', 'saveReadme', 'rec', 'sgRec', 'coachAdd', 'coachFS', 'trkAdd', 'trkNew', 'trkReplace'}
HEAVY = ('sgOpen','sgSec','sgTakes','playTake','star','sgMode','sgHint','sgHMenu','sgSetHint','sgRMenu','sgOrder','sgAnywhere','sgEdit','sgWord','sgMark','sgEditMode','sgNew','sgSplit','sgSave','sgSearch','sgListEdit','sgToggle','sgCue','sgUnlink','start','songStart','resume','cta','confirmF','tog','rlv','flv','wTog','saveHow','skipHow','editSess','saveEdit','exNote','takeNote','addWord','saveWord',
         'openNote','longOk','pauseToggle','fwOpen','fwToggle','clock','sheet','calDay','calSession','eflv','input','textarea',
         # 3.18 Song Clock
         'ckGrid','ckTile','ckPad','ckLine','ckPP','ckNudge','ckRedo','ckSyncPause','ckSyncUndo','ckFinish','ckSyncX','ckCheckDone','ckSyncAgain','ckLen','ckPickSet','ckPencil','ckHeadDone',
         # 3.19 the track player
         'trkOpen','trkPP','trkLoop','trkSet','trkLevel','trkRow','trkToStart','trkSpeed','trkMenu','trkBack')

def run(b, t):
    found = collections.OrderedDict()
    def note(key, trace):
        if key not in found: found[key] = list(trace)[-12:]
    for seed in SEEDS:
        R = random.Random(seed); w, h, touch = R.choice(SIZES)
        ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch, color_scheme=R.choice(['light', 'dark']), accept_downloads=True,
                            timezone_id='Europe/London', locale='en-GB')
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('JavaScript error: ' + str(e).split('\n')[0]))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
        pg.on('dialog', lambda d: d.dismiss())
        pg.goto(url(APP_PATH))
        data = with_song_practice(); data['songSessions'][0]['takes'] = ['tA']
        pg.evaluate("o=>{localStorage.clear();localStorage.setItem('vocalTracker',JSON.stringify(o))}", data); pg.reload(); ready(pg)
        pg.evaluate("l=>{U.sDraft={step:1,title:'river song',artist:'',text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();U.view=null;U.tab='today';render()}",
                    "[Verse]\nPaper boats along the gutter\n\n[Chorus]\nCarry me over\nLet the river know\n\n[Chorus]\nCarry me over\nLet the river know")
        pg.evaluate("putTake({id:'tA',songId:'g_1',created:Date.now()-864e5,len:30,size:5000,type:'audio/mp4',star:false,blob:new Blob([new Uint8Array(5000)],{type:'audio/mp4'})}).then(refreshTakes).then(rerender)")
        # 3.18: the river song is synced, so play-along, Check timing and Sync are all in reach of the random taps
        pg.evaluate("(()=>{const s=D.songs.find(x=>x.name==='River Song'),L=ckLines(s);ckStore(s,L,ckSpread(s,L,[0,10,20]),[true,true,true],L.map(()=>false),{est:true})})()")
        # a take from the river song's first chorus, so a section has takes and its sheet can open
        pg.evaluate("(()=>{const s=D.songs.find(x=>x.name==='River Song');return putTake({id:'tB',songId:s.id,o:s.order[1].o,created:Date.now()-2*864e5,len:14,size:5000,type:'audio/mp4',star:true,blob:new Blob([new Uint8Array(5000)],{type:'audio/mp4'})}).then(refreshTakes).then(rerender)})()")
        # 3.16: the coach video added, so its player, doors and window are in the random taps too
        pg.set_input_files('#coachIn', fix('coach-chapters.webm'))
        pg.wait_for_function("COACH.has()&&!COACH.busy()", timeout=15000)
        pg.wait_for_timeout(200)
        # 3.19: a short track on the first song, so the player, its doors and its window are in the random taps too
        pg.evaluate("TRACK.expect('g_1')"); pg.set_input_files('#trackIn', TONES)
        pg.wait_for_function("TRACK.has('g_1')&&!TRACK.busy()", timeout=15000)
        pg.evaluate("songById('g_1').loop={start:2,end:4,on:true};save();go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(200)
        trace = collections.deque(maxlen=20); trace.append(f'seed {seed}, {w}x{h}')
        for step in range(STEPS):
            r = R.random()
            try:
                if r < 0.03:
                    w, h, _ = R.choice(SIZES); pg.set_viewport_size({'width': w, 'height': h}); trace.append(f'resize {w}x{h}'); pg.wait_for_timeout(120)
                elif r < 0.05:
                    pg.reload(); trace.append('reload'); ready(pg)
                elif r < 0.07:
                    pg.keyboard.press('Escape'); trace.append('escape')
                elif r < 0.09:
                    pg.mouse.wheel(0, R.choice([-800, 400, 1500])); trace.append('scroll'); pg.wait_for_timeout(120)
                elif r < 0.10:
                    pg.evaluate("X&&(X.start=Date.now()-" + str(R.choice([60, 3600, 7200, 100000])) + "*1000, saveDraft())"); trace.append('age session')
                else:
                    els = [e for e in pg.evaluate(VIS) if e['a'] not in SKIP]
                    if not els:
                        note('nothing tappable on screen', trace); trace.append('nothing tappable'); pg.keyboard.press('Escape'); continue
                    wts = [0.15 if x['a'] in ('tab', 'exTab', 'histTab') else (3 if x['a'] in HEAVY else 1) for x in els]
                    e = R.choices(els, weights=wts)[0]; sel = f'[data-fz="{e["i"]}"]'
                    if e['a'] in ('input', 'textarea'):
                        val = R.choice(TEXTS)
                        if e['type'] == 'date': val = R.choice(['2026-01-01', '2025-12-31', '2030-05-05', iso(now)[:10]])
                        if e['type'] == 'number': val = R.choice(['0', '-3', '45', '99999', '', '7.5'])
                        try: pg.fill(sel, val, timeout=1500)
                        except Exception: pass
                        trace.append(f'type {e["id"] or e["a"]} = {val[:20]!r}')
                    else:
                        trace.append(f'tap {e["a"]} v={e["v"][:20]} k={e["k"][:14]}')
                        pg.click(sel, timeout=1500, no_wait_after=True)
                    pg.wait_for_timeout(R.choice([30, 80, 250]))
                for x in errs: note(x, trace)
                errs.clear()
                for prob in pg.evaluate(INV):
                    if prob not in found: pg.screenshot(path=os.path.join(OUT, f'fuzz-{len(found)}.png'))
                    note(prob, trace)
            except Exception as ex:
                msg = str(ex).split('\n')[0][:120]
                if 'Timeout' in msg: trace.append('tap timed out'); continue
                note('test driver: ' + msg, trace)
        ctx.close()
    if not found:
        t.ok(True, f'{len(SEEDS) * STEPS} random steps over {len(SEEDS)} runs found no problems')
    for k, tr in found.items():
        t.ok(False, 'random taps found: ' + k)
        for x in tr: print('        ' + x)
