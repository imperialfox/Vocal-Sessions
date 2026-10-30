"""Q11 Save safety: damaged saved data rescued before anything saves over it, one bad song dropped on its own, the shared
IndexedDB helper (abort, a dropped connection, blocked), takes that fail to save kept for Retry, a draft that can't be
saved, and a launch that always ends even when the first draw or the data goes wrong."""
import json, os
from harness import ready, url, APP_PATH, SP, sample, SEED

LAUNCH_ARGS = ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']

CUT = json.dumps(sample())[:-40]  # a save cut off part-way
TOAST = "(document.querySelector('.toast')||{}).textContent||''"
RESCUED = "SAFE.rescued().map(c=>({why:c.why,text:c.text,bytes:c.bytes}))"
# the database stops (aborts) every save of a take while window.__abort is set: what a full phone looks like
ABORT = """(()=>{const P=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(v,k){const r=P.call(this,v,k);
  if(window.__abort&&this.name==='takes')this.transaction.abort();return r}})()"""


def fresh(b, t, data, init=None, route=None, **ctx):
    """A page whose stored data is set before the app first opens (raw text, so it can be damaged)."""
    c = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, timezone_id='Europe/London',
                      locale='en-GB', accept_downloads=True, service_workers='block', **ctx)
    c.add_init_script("try{localStorage.setItem('vocalMotion','0')}catch(e){}")
    if init: c.add_init_script(init)
    pg = c.new_page()
    tag = 'safety'
    pg.on('pageerror', lambda e: t.errors.append(f'{tag}: {str(e).splitlines()[0]}'))
    if route: pg.route(*route)
    pg.goto(url(APP_PATH))
    pg.wait_for_function("!document.getElementById('splash')", timeout=15000)
    pg.evaluate("raw=>{localStorage.clear();if(raw!==null)localStorage.setItem('vocalTracker',raw)}", data)
    pg.reload()
    return pg


def run(b, t):
    ok = t.ok

    # ----- a cut-off save is copied before anything saves over it, and the app says so -----
    pg = fresh(b, t, CUT)
    ready(pg)
    pg.wait_for_function("SAFE.rescued().length===1", timeout=8000)
    r = pg.evaluate(RESCUED)
    ok(r and r[0]['why'] == 'unreadable' and r[0]['text'] == CUT, 'a cut-off vocalTracker is copied exactly as it was, into IndexedDB')
    pg.wait_for_function("document.querySelector('.toast')", timeout=8000)
    ok('couldn’t be read' in pg.evaluate(TOAST) and 'Settings › Backup' in pg.evaluate(TOAST), 'and the app says so, pointing to Settings › Backup')
    t.shot(pg, 'rescued-toast')
    ok(pg.locator('[data-a=tab]').count() > 0, 'the app still opens')
    stored = pg.evaluate("localStorage.getItem('vocalTracker')")
    ok(stored != CUT and json.loads(stored).get('schema'), 'once the copy is safe, the app saves as normal')
    # it's said once: reopening doesn't copy or say it again
    pg.reload(); ready(pg); pg.wait_for_timeout(600)
    ok(len(pg.evaluate(RESCUED)) == 1 and 'couldn’t be read' not in pg.evaluate(TOAST), 'the message is shown once, and the copy is kept')
    # Settings › Backup: save it as a file, or delete it
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';render()"); pg.wait_for_timeout(300)
    ok(pg.locator('[data-a=rescueSave]').count() == 1 and 'rescued data' in pg.inner_text('#app').lower(), 'Settings › Backup shows the rescued copy')
    t.shot(pg, 'rescued-settings')
    with pg.expect_download(timeout=5000) as dl: pg.click('[data-a=rescueSave]')
    ok(open(dl.value.path(), encoding='utf-8').read() == CUT and dl.value.suggested_filename.endswith('.txt'),
       'Save the rescued copy gives back exactly what was stored')
    ok(pg.evaluate("SET.sizes().find(x=>x.k==='app').b") >= len(CUT), 'Storage counts the rescued copy')
    pg.click('[data-a=sheet][data-v=rescueDel]'); pg.wait_for_timeout(400)
    ok('can’t be undone' in pg.inner_text('.sheet'), 'deleting it asks first')
    pg.click('.sheet [data-a=rescueDel]'); pg.wait_for_timeout(500)
    ok(pg.evaluate("SAFE.rescued().length") == 0 and pg.locator('[data-a=rescueSave]').count() == 0, 'and then deletes it')
    pg.reload(); ready(pg)
    ok(pg.evaluate("SAFE.rescued().length") == 0, 'it stays deleted')
    pg.context.close()

    # saving waits while a copy is being made
    pg = fresh(b, t, json.dumps(sample())); ready(pg)
    before = pg.evaluate("localStorage.getItem('vocalTracker')")
    pg.evaluate("holdSaves(new Promise(r=>setTimeout(r,600)));D.months['1999-01']=5;save()")
    ok(pg.evaluate("localStorage.getItem('vocalTracker')") == before, 'saving waits while a safety copy is being made')
    pg.wait_for_timeout(800)
    ok(json.loads(pg.evaluate("localStorage.getItem('vocalTracker')"))['months'].get('1999-01') == 5, 'and saves once it’s done')

    # one song that makes the checks fail is dropped on its own, and the data as it was is copied
    d = sample(); d['songs'].append({'id': 'bad', 'name': 'Bad'}); raw = json.dumps(d)
    res = pg.evaluate("""raw=>{const o=cleanSong;cleanSong=s=>{if(s&&s.id==='bad')throw new Error('test');return o(s)};
      localStorage.setItem('vocalTracker',raw);const d=load();cleanSong=o;return d.songs.map(s=>s.id)}""", raw)
    ok(res == ['g_1'], 'a song the checks can’t handle is dropped alone; the other songs (and everything else) load')
    pg.wait_for_function("SAFE.rescued().some(c=>c.why==='song')", timeout=5000)
    ok(pg.evaluate("SAFE.rescued().find(c=>c.why==='song').text") == raw, 'and the data as it was is copied first')
    ok(pg.evaluate("cleanData({sessions:[],songs:[{id:'a',name:'A'},null,7]}).songs.length") == 1, 'cleanData still drops malformed songs quietly')
    r = pg.evaluate("""async(raw)=>{const o=cleanSong;cleanSong=s=>{if(s&&s.id==='bad')throw new Error('test');return o(s)};
      const src={app:'vocal-sessions',format:2,appVersion:'3.29',exportedAt:new Date().toISOString(),data:JSON.parse(raw),takes:[]};
      const r=await inspectBackup(JSON.stringify(src),'x.json',100);cleanSong=o;
      return [r.status!=='broken',r.songsBad,r.p.data.songs.length,bkReportHTML(r,'import').includes('A song is damaged')]}""", raw)
    ok(r == [True, 1, 1, True], 'a backup with a song that can’t be read says so before restoring, and the rest restores')
    pg.context.close()

    # nowhere to copy it: the stored text is left exactly as it was, and nothing saves over it
    pg = fresh(b, t, CUT, init="Object.defineProperty(window,'indexedDB',{configurable:true,get:()=>undefined})")
    ready(pg); pg.wait_for_timeout(500)
    pg.evaluate("D.months['1999-01']=5;save()")
    ok(pg.evaluate("localStorage.getItem('vocalTracker')") == CUT and pg.evaluate("SAVE_LOCK") == 'uncopied',
       'if it can’t be copied, the damaged data is left untouched and nothing is saved over it')
    pg.wait_for_function("document.querySelector('.toast')", timeout=8000)
    ok('left as it was' in pg.evaluate(TOAST), 'and the app says so')
    pg.context.close()

    # ----- the shared IndexedDB helper -----
    pg = t.page(b)
    r = pg.evaluate("""async()=>{const d=await db();d.close();   // the connection goes (iOS can drop it)
      const b=new Blob([new Uint8Array(2000)],{type:'audio/mp4'});
      await putTake({id:'tc',songId:'g_1',created:Date.now(),len:2,size:b.size,type:'audio/mp4',blob:b,star:false});
      await refreshTakes();return TAKES.map(t=>t.id)}""")
    ok(r == ['tc'], 'a dropped connection is reopened, and the save goes through')
    r = pg.evaluate("""async()=>{const X1=IDB.define('vocalQ11Test',1,{s:null});await X1.tx('s','readwrite',s=>s.put(1,'a'));
      let msg='';await X1.tx('s','readwrite',s=>{s.put(2,'b');s.transaction.abort()}).catch(e=>msg='rejected');
      const a=await X1.tx('s','readonly',s=>s.get('a')),b2=await X1.tx('s','readonly',s=>s.get('b'));return [msg,a,b2===undefined]}""")
    ok(r == ['rejected', 1, True], 'an aborted transaction rejects (it never hangs), and the next one works')
    r = pg.evaluate("""async()=>{const raw=await new Promise(r=>{const q=indexedDB.open('vocalQ11Block',1);q.onsuccess=()=>r(q.result)});
      const t0=Date.now();const X2=IDB.define('vocalQ11Block',2,{s:null});
      const m=await X2.open().then(()=>'opened',e=>'gave up');const ms=Date.now()-t0;raw.close();
      const again=await X2.open().then(()=>'opened',()=>'no');return [m,ms<7000,again]}""")
    ok(r == ['gave up', True, 'opened'], 'a blocked open gives up after a few seconds, and opens once it isn’t blocked')
    pg.context.close()

    # ----- a take that can't be saved is kept, with Retry -----
    pg = t.page(b, ctx_args={'permissions': ['microphone']}, init=ABORT)
    pg.evaluate(SP); pg.click('[data-a=song][data-k=g_1]')
    pg.evaluate("window.__abort=true")
    pg.click('[data-a=rec]'); pg.wait_for_timeout(1800); pg.click('[data-a=rec]')
    pg.wait_for_function("UNSAVED.length===1", timeout=8000)
    ok(pg.evaluate("TAKES.length") == 0 and pg.evaluate("UNSAVED[0].t.blob.size") > 1000, 'an aborted save keeps the take, audio and all, in memory')
    ok('Couldn’t save the take' in pg.evaluate(TOAST) and pg.locator('.toast .ckub').inner_text() == 'Retry', 'and says so, with Retry')
    t.shot(pg, 'take-retry')
    ok(pg.evaluate("X&&X.start>0"), 'the song practice it belongs to carries on')
    pg.click('.toast .ckub'); pg.wait_for_timeout(700)
    ok(pg.evaluate("UNSAVED.length") == 1 and 'Still couldn’t save' in pg.evaluate(TOAST), 'Retry while it still fails keeps it and says so')
    pg.evaluate("window.__abort=false"); pg.click('.toast .ckub'); pg.wait_for_timeout(900)
    ok(pg.evaluate("UNSAVED.length") == 0 and pg.evaluate("TAKES.length") == 1 and 'Take saved' in pg.evaluate(TOAST), 'Retry saves it once there’s room')
    ok(pg.evaluate("X.takes.length") == 1 and pg.evaluate("X.takes[0]===TAKES[0].id"), 'and it joins the song practice it was recorded in')
    # missed the toast: coming back to the app tries again
    pg.evaluate("window.__abort=true")
    pg.click('[data-a=rec]'); pg.wait_for_timeout(1500); pg.click('[data-a=rec]')
    pg.wait_for_function("UNSAVED.length===1", timeout=8000)
    pg.evaluate("window.__abort=false;document.querySelector('.toast')&&document.querySelector('.toast').remove()")
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
    pg.wait_for_function("UNSAVED.length===0", timeout=5000)
    ok(pg.evaluate("TAKES.length") == 2, 'a take still waiting is saved when the app comes back to the screen')
    pg.context.close()

    # ----- a draft that can't be saved warns -----
    pg = t.page(b)
    pg.evaluate("""(()=>{const S=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){
      if(k==='vocalDraft')throw new DOMException('full','QuotaExceededError');return S.call(this,k,v)}})()""")
    pg.evaluate("X={start:Date.now(),kind:'focused'};normX();saveDraft()")
    ok('Couldn’t save your practice so far' in pg.evaluate(TOAST), 'a draft that can’t be saved warns, as saving does')
    pg.evaluate("document.querySelector('.toast').remove();saveDraft()")
    ok(pg.evaluate(TOAST) == '', 'and doesn’t repeat itself on every save')
    pg.context.close()

    # ----- the launch screen always goes -----
    def patched(js):
        def handle(route):
            resp = route.fetch()
            route.fulfill(response=resp, body=resp.text() + '\n' + js)
        return handle
    throw_draw = ";(function(){const r=render;let n=0;render=function(){if(!n++)throw new Error('first draw (test)');return r.apply(this,arguments)}})();"
    pg = fresh(b, t, json.dumps(sample()), route=('**/js/ui.js*', patched(throw_draw)))
    pg.wait_for_function("!document.getElementById('splash')", timeout=10000)
    ok(True, 'the launch screen goes even if the first draw throws')
    ok(any('first draw' in e for e in pg.evaluate("BOOT_ERRORS")) and 'Something went wrong' in pg.inner_text('#app'), 'and a message is shown in its place')
    pg.wait_for_function("document.querySelector('.toast')", timeout=8000)
    ok('Something went wrong' in pg.evaluate(TOAST), 'with a toast')
    t.shot(pg, 'boot-draw-failed')
    pg.context.close()

    good = json.dumps(sample())
    throw_mig = ";(function(){const m=migrate;let n=0;migrate=function(){if(!n++)throw new Error('migrate (test)');return m.apply(this,arguments)}})();"
    pg = fresh(b, t, good, route=('**/js/storage.js*', patched(throw_mig)))
    ready(pg)
    ok(pg.locator('[data-a=tab]').count() > 0 and pg.evaluate("SAVE_LOCK") == 'boot', 'if opening the data goes wrong, the app still opens, with saving off')
    pg.evaluate("D.months['1999-01']=5;save()")
    ok(pg.evaluate("localStorage.getItem('vocalTracker')") == good, 'and the stored data is left exactly as it was')
    pg.wait_for_function("document.querySelector('.toast')", timeout=8000)
    ok('left as it was' in pg.evaluate(TOAST), 'and says so')
    pg.context.close()
