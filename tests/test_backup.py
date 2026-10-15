"""Backups: export, check, restore, undo, and compatibility with backups from earlier versions.

The sample backups in tests/fixtures were made by the real 3.5 and 3.6 apps. Every future version must
restore them exactly, and a backup made now must still restore in 3.6 (tests/fixtures/app-3.6.html).
"""
import os, json, re
from harness import now, fix, ADD_TAKE, OUT, SEED, ready, UA_IPHONE, url

# Sessions store exercises by these names, so they must never change.
EXERCISE_IDS = {'found': ['slides', 'humming', 'lip', 'straw'],
                'rot': ['falsetto', 'upperlower', 'rung', 'hinge', 'half', 'vertical', 'nasal', 'flex']}

F = os.path.join(OUT, 'backup-files'); os.makedirs(F, exist_ok=True)

def pick(pg, act, path):
    with pg.expect_file_chooser() as fc: pg.click(f'[data-a={act}]')
    fc.value.set_files(path); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)

def close(pg):
    pg.click('.xbtn'); pg.wait_for_timeout(350)

def write(name, obj=None, raw=None):
    p = os.path.join(F, name); open(p, 'w', encoding='utf-8').write(raw if raw is not None else json.dumps(obj)); return p

def same(a, b): return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
# songs from before 3.8 gain an artist, a pin and the date added when upgraded; nothing else about them changes
SONG_ADDED = ('artist', 'pinned', 'added')
def same_songs(now, was):
    return len(now) == len(was) and all(same({k: v for k, v in a.items() if k not in SONG_ADDED}, b) and a['artist'] == '' and a['pinned'] is False and a['added'] > 0
                                        for a, b in zip(now, was))

def run(b, t):
    ok = t.ok
    pg = t.page(b, data=None)
    ok(pg.evaluate("FOUND.map(e=>e.id)") == EXERCISE_IDS['found'] and pg.evaluate("ROT.map(e=>e.id)") == EXERCISE_IDS['rot'],
       'exercise ids are unchanged, so past sessions keep their exercises')
    ok(pg.evaluate("isSecureContext&&!!crypto.subtle"), 'check codes can be calculated')

    # ---- sample backups from earlier versions restore exactly
    for v, status in [('3.5', 'old'), ('3.6', 'good')]:
        src = json.load(open(fix(f'backup-{v}.json'), encoding='utf-8'))
        pg.evaluate("U.tab='settings';render()")
        pick(pg, 'importPick', fix(f'backup-{v}.json'))
        ok(pg.evaluate("pendingImport.status") == status, f'{v} backup checks as "{status}"')
        pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
        D = pg.evaluate("D")
        ok(all(same(D[k], src['data'][k]) for k in ['sessions', 'songSessions', 'custom', 'months', 'words']) and same_songs(D['songs'], src['data']['songs']),
           f'{v} backup: sessions, song practice, songs, exercises, minutes and words restored exactly')
        tk = pg.evaluate("TAKES.map(t=>({id:t.id,size:t.blob.size,note:t.note,type:t.blob.type}))")
        ok(tk == [{'id': 't1', 'size': 3000, 'note': {'w': ['Breathy'], 't': 'Ran out of air'}, 'type': 'audio/mp4'}], f'{v} backup: the recording and its note restored')
        pg.click('[data-a=tab][data-v=history]'); pg.wait_for_timeout(300)
        ok(pg.locator('#pchart').count() == 1 and pg.locator('[data-v=session]').count() >= 1, f'{v} backup: Progress shows the restored sessions')
        pg.click('[data-a=tab][data-v=today]'); pg.wait_for_timeout(200)

    # ---- a backup made now restores in 3.6
    pg.evaluate("U.tab='settings';render()"); pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    now_txt = pg.evaluate("pendingExport.file.text()"); close(pg)
    nowp = write('made-now.json', raw=now_txt)
    old = b.new_context(user_agent=UA_IPHONE, accept_downloads=True).new_page()
    old.goto(url(fix('app-3.6.html'))); old.evaluate(SEED, None); old.reload(); ready(old)
    old.evaluate("U.tab='settings';render()")
    pick(old, 'importPick', nowp)
    ok(old.evaluate("pendingImport.status") == 'good', 'version 3.6 accepts a backup made by this version')
    old.click('[data-a=importYes]'); old.wait_for_function("U.sheet===null", timeout=10000); old.wait_for_timeout(300)
    nd = json.loads(now_txt)['data']
    ok(same(old.evaluate("D.sessions"), nd['sessions']) and old.evaluate("TAKES.length") == 1, 'and restores it completely')
    old.context.close(); pg.context.close()

    # ---- export, check, restore, undo
    pg = t.page(b); pg.evaluate(ADD_TAKE, 't1')
    ok(pg.evaluate("deviceName()") == 'iPhone', 'the device is named iPhone')
    pg.evaluate("tabMin=false;U.tab='settings';U.view=null;U.sheet=null;render()"); pg.wait_for_timeout(300)
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    ok(pg.evaluate("pendingExport.verified"), 'the backup is read back and verified before saving')
    ok(pg.locator('[data-a=bkGuideFrom]').count() == 1, 'the first backup offers the folder guide')
    t.shot(pg, 'export-ready')
    pg.click('[data-a=bkGuideFrom]'); pg.wait_for_timeout(400); ok(pg.evaluate("U.sheet") == 'bkGuide', 'the guide opens'); t.shot(pg, 'guide')
    close(pg); ok(pg.evaluate("U.sheet") == 'exportReady', 'closing the guide returns to Backup ready')
    with pg.expect_download() as dl: pg.click('[data-a=exportSave]')
    d = dl.value; name = d.suggested_filename; bk = os.path.join(F, 'good.json'); d.save_as(bk); pg.wait_for_timeout(300)
    ok(name == f'Vocal Sessions backup · {now.strftime("%Y-%m")} · iPhone.json', 'the file is named by month and device: ' + name)
    txt = open(bk, encoding='utf-8').read(); P = json.loads(txt)
    ok(txt.startswith('{\n  "README": [\n    "This is a backup from Vocal Sessions'), 'the file opens with a plain-English note')
    ok(re.fullmatch('[0-9a-f]{64}', P.get('checkCode') or '') is not None and P['format'] == 2 and P['device'] == 'iPhone', 'check code, format and device are saved')
    ok(P['summary']['sessions'] == 3 and P['summary']['recordings'] == 1, 'the summary counts are right')
    log = pg.evaluate("loadLog()"); ok(len(log) == 1 and log[0]['verified'] and log[0]['name'] == name, 'Backup history records it')
    ok(pg.evaluate("D.lastBackup") == P['exportedAt'], 'the last backup time is updated')
    pg.click('[data-a=exportPrep] >> nth=0'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    ok(pg.locator('[data-a=bkGuideFrom]').count() == 0, 'the folder guide link only shows on the first backup'); close(pg)

    pick(pg, 'checkPick', bk)
    ok(pg.evaluate("pendingImport.status") == 'good' and 'Nothing has been changed' in pg.inner_text('.sheet'), 'Check a backup: a good backup is complete')
    t.shot(pg, 'check-good')
    pg.click('[data-a=bkToImport]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sd.mode") == 'import' and 'COMPARED WITH THIS IPHONE' in pg.inner_text('.sheet').upper(), 'Restore from this backup switches to the comparison')
    ok('Everything on this iPhone is also in this backup' in pg.inner_text('.sheet'), 'nothing would be lost'); close(pg)

    tam = json.loads(txt); tam['data']['sessions'][0]['mins'] = 99; tamp = write('tampered.json', tam)
    pick(pg, 'checkPick', tamp); ok(pg.evaluate("pendingImport.status") == 'changed', 'an edited backup is flagged as changed'); close(pg)
    pick(pg, 'importPick', tamp); ok(pg.locator('[data-a=importYes]').inner_text() == 'Restore anyway', 'a changed backup asks to Restore anyway'); close(pg)
    cut = write('cut.json', raw=txt[:len(txt) // 2]); pick(pg, 'checkPick', cut)
    ok(pg.evaluate("pendingImport.status") == 'broken' and 'cut short' in pg.inner_text('.sheet'), 'a half-copied file is reported as cut short'); close(pg)
    pick(pg, 'importPick', cut); ok(pg.locator('[data-a=importYes]').count() == 0, 'a broken file cannot be restored'); close(pg)
    pick(pg, 'checkPick', write('other.json', {'hello': 1})); ok('isn’t a Vocal Sessions backup' in pg.inner_text('.sheet'), 'other files are not mistaken for backups'); close(pg)
    pick(pg, 'checkPick', write('junk.json', raw='\x00\x01 not json')); ok(pg.evaluate("pendingImport.status") == 'broken', 'binary junk is handled'); close(pg)
    pt = json.loads(txt); pt['takes'][0]['data'] = 'data:audio/mp4;base64,@@@'; del pt['checkCode']
    pick(pg, 'checkPick', write('partial.json', pt))
    ok(pg.evaluate("pendingImport.status") == 'partial' and pg.evaluate("pendingImport.p.takes.length") == 0, 'a damaged recording is flagged and left out'); close(pg)

    # restore comparison and undo
    pg.evaluate("D.sessions.push({id:'snew',date:new Date().toISOString(),mins:22,f:{},rot:{},xn:{},rate:{},takes:[],how:[],howNote:''});save();rerender()")
    pick(pg, 'importPick', bk); sh = pg.inner_text('.sheet')
    ok('1 session on this iPhone isn’t in this backup' in sh and 'older than this iPhone' in sh, 'restoring warns that a newer session would be removed')
    ok(pg.locator('.sheet [data-a=exportPrep]').count() == 1, 'and offers to back up first'); t.shot(pg, 'restore-compare')
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.sessions.length") == 3 and not pg.evaluate("D.sessions.some(s=>s.id==='snew')"), 'restore replaces the data')
    ok(pg.evaluate("!!UNDO&&UNDO.takes.length===1"), 'an undo copy is kept, with recordings')
    pg.evaluate("tabMin=false;U.tab='settings';U.view=null;U.sheet=null;render()"); pg.wait_for_timeout(300); ok(pg.locator('[data-v=undoRestore]').count() == 1, 'Settings shows Undo last restore')
    pg.evaluate("D.sessions.push({id:'safter',date:new Date().toISOString(),mins:10,f:{},rot:{},xn:{},rate:{},takes:[],how:[],howNote:''});save();rerender()")
    pg.click('[data-v=undoRestore]'); pg.wait_for_timeout(400); ok('1 session since then' in pg.inner_text('.sheet'), 'undo warns about sessions logged since')
    pg.click('[data-a=undoYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.sessions.some(s=>s.id==='snew')") and not pg.evaluate("D.sessions.some(s=>s.id==='safter')") and pg.evaluate("TAKES.length") == 1,
       'undo brings back the earlier data and recordings')
    ok(pg.evaluate("UNDO") is None and pg.evaluate("U.tab") == 'settings', 'undo is used up and you stay in Settings')
    pick(pg, 'importPick', bk); pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.reload(); ready(pg)
    ok(pg.evaluate("!!UNDO"), 'the undo copy survives reopening the app')
    pg.evaluate("(async()=>{const u=await getUndo();u.at=Date.now()-31*864e5;await putUndo(u);})()"); pg.wait_for_timeout(300); pg.reload(); ready(pg)
    ok(pg.evaluate("UNDO") is None, 'the undo copy is removed after 30 days')

    pg.evaluate("tabMin=false;U.tab='settings';U.view=null;U.sheet=null;render()"); pg.wait_for_timeout(300); pg.click('[data-v=bkLog]'); pg.wait_for_timeout(400)
    ok(pg.locator('.sheet .row').count() >= 1, 'Backup history lists backups'); close(pg)
    with pg.expect_download() as dl: pg.click('main [data-a=saveReadme]')
    rp = os.path.join(F, dl.value.suggested_filename); dl.value.save_as(rp); rt = open(rp, encoding='utf-8').read()
    ok(dl.value.suggested_filename == 'READ ME – Vocal Sessions backups.txt' and 'HOW TO RESTORE' in rt, 'the read-me file is saved')

    pick(pg, 'importPick', bk); pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000)
    pg.evaluate("tabMin=false;U.tab='settings';U.view=null;U.sheet=null;render()"); pg.wait_for_timeout(200)
    pg.click('[data-v=resetAll]'); pg.wait_for_timeout(300); pg.click('[data-a=resetAll]'); pg.wait_for_timeout(800)
    ok(pg.evaluate("UNDO") is None and pg.evaluate("loadLog().length") == 0, 'Reset all data clears the undo copy and Backup history')
    pg.evaluate("tabMin=false;U.tab='settings';U.view=null;U.sheet=null;render()"); pg.wait_for_timeout(300)
    pick(pg, 'importPick', bk); ok('has no practice saved yet' in pg.inner_text('.sheet'), 'an empty device says so')
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); ok(pg.evaluate("D.sessions.length") == 3, 'restoring into an empty app works')

    # recordings survive the database upgrade from 3.5
    r = pg.evaluate("""async()=>{(await db()).close();dbp=null;await new Promise(r=>{const q=indexedDB.deleteDatabase('vocalTakes');q.onsuccess=q.onerror=q.onblocked=()=>r();});
      await new Promise((res,rej)=>{const q=indexedDB.open('vocalTakes',1);q.onupgradeneeded=()=>q.result.createObjectStore('takes',{keyPath:'id'});q.onsuccess=()=>{const d=q.result;const t=d.transaction('takes','readwrite');t.objectStore('takes').put({id:'old1',songId:'g_1',created:1,len:3,size:3,type:'audio/mp4',blob:new Blob(['abc'])});t.oncomplete=()=>{d.close();res();};};q.onerror=rej;});
      await refreshTakes();const d=await db();return [TAKES.map(t=>t.id),[...d.objectStoreNames]];}""")
    ok(r[0] == ['old1'] and 'undo' in r[1], 'upgrading from 3.5 keeps recordings and adds the undo store')
    pg.context.close()

    # a large backup stays quick: 30 recordings, about 20 MB
    pg = t.page(b, data=None)
    pg.evaluate("""async()=>{for(let i=0;i<30;i++){const a=new Uint8Array(500000);crypto.getRandomValues(a.subarray(0,65536));for(let j=65536;j<a.length;j+=65536)a.set(a.subarray(0,Math.min(65536,a.length-j)),j);
      const b=new Blob([a],{type:'audio/mp4'});await putTake({id:'t'+i,songId:'g',created:Date.now()-i*1000,len:60,size:b.size,type:'audio/mp4',blob:b,star:false,note:{w:[],t:''}});}await refreshTakes();}""")
    ms = pg.evaluate("(async()=>{const s=performance.now();await prepareExport();return performance.now()-s})()")
    ok(pg.evaluate("U.sheet") == 'exportReady' and ms < 20000, f'a 20 MB backup is prepared and verified ({ms / 1000:.1f}s)')
    pg.context.close()
