"""Random-tap tester: taps, types, scrolls, resizes and reloads at random, checking after every step that nothing is broken.
Each seed is a repeatable run. More steps:  VS_FUZZ_STEPS=2000 python tests/run.py fuzz"""
import os, json, random, collections
from harness import with_song_practice, OUT, ready, now, iso, url, APP_PATH

STEPS = int(os.environ.get('VS_FUZZ_STEPS', '200'))
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
 try{JSON.parse(localStorage.getItem('vocalTracker'))}catch(e){p.push('saved data unreadable')}
 const sumOk=Object.keys(D.months).length>=0;
 return p;})()"""
VIS=r"""(()=>{const L=document.getElementById('layer');const root=L.querySelector('.scrim,.clock')?L:document;
 const els=[...root.querySelectorAll('[data-a],input:not([type=file]),textarea')].filter(e=>{const r=e.getBoundingClientRect();if(r.width<2||r.height<2)return false;if(r.bottom<0||r.top>innerHeight||r.right<0||r.left>innerWidth)return false;
   const cx=Math.min(innerWidth-1,Math.max(0,r.left+r.width/2)),cy=Math.min(innerHeight-1,Math.max(0,r.top+r.height/2));const t=document.elementFromPoint(cx,cy);return t&&(t===e||e.contains(t)||t.closest('[data-a]')===e);});
 return els.map((e,i)=>{e.setAttribute('data-fz',i);return {i,a:e.dataset.a||e.tagName.toLowerCase(),v:e.dataset.v||'',k:e.dataset.k||'',id:e.id||'',type:e.type||''};});})()"""
SKIP = {'importPick', 'checkPick', 'exportSave', 'saveReadme', 'rec'}
HEAVY = ('sgOpen','sgEdit','sgWord','sgMark','sgEditMode','sgNew','sgSplit','sgSave','sgSearch','sgListEdit','sgToggle','sgCue','sgUnlink','start','songStart','resume','cta','confirmF','tog','rlv','flv','wTog','saveHow','skipHow','editSess','saveEdit','exNote','takeNote','addWord','saveWord',
         'openNote','longOk','pauseToggle','clock','sheet','calDay','calSession','eflv','input','textarea')

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
        pg.wait_for_timeout(200)
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
