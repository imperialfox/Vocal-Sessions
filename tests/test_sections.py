"""Recording a section of a song with a fake microphone: selecting a section, the screen locked while recording,
takes saved to their place in the song, the review sheet, stars and the keep rule across sections, unlinking and
reordering, leaving mid-take, and backups made with Exclude recordings."""
import json
from harness import with_song_practice

LAUNCH_ARGS = ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']

LYR = ("[Verse]\nPaper boats along the gutter\nRacing rain down Elmwood Lane\nPast the bakery and the station\n\n[Chorus]\nCarry me over\nLet the river know\n\n"
       "[Verse]\nEvery window holds a candle\nEvery doorway holds a frame\nEvery stranger knows the chorus\n\n[Chorus]\nCarry me over\nLet the river know\n\n"
       "[Bridge]\nI was never made for standing still\nNever one to stay the same\nHold your breath, it's coming\n\n[Outro]\nLet the river know my name")
ADD = """l=>{U.sDraft={step:1,title:'river song',artist:'',text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();
  const s=songById(U.songId);return {id:s.id,o:s.order.map(x=>x.o),sid:s.order.map(x=>x.sid)}}"""
# watch what the app asks the microphone and the recorder for
SPY = """()=>{const M=window.MediaRecorder;window.MediaRecorder=class extends M{constructor(s,o){super(s,o);window._recOpts=o||{};
  const tr=s.getAudioTracks()[0];window._recSet=tr&&tr.getSettings?tr.getSettings():{}}};
  window.MediaRecorder.isTypeSupported=M.isTypeSupported.bind(M);
  const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
  navigator.mediaDevices.getUserMedia=c=>{window._recAsk=c;return g(c)}}"""


def run(b, t):
    ok = t.ok
    pg = t.page(b, touch=True, data=with_song_practice(), ctx_args={'permissions': ['microphone']})
    pg.evaluate("U.tab='songs';render()")
    S = pg.evaluate(ADD, LYR); pg.wait_for_timeout(300)
    o1, o2, o3, o4 = S['o'][:4]
    ok(S['sid'][1] == S['sid'][3], 'the repeated chorus is linked')
    sec = lambda o: f'.sgsec[data-o="{o}"]'
    def select(o):
        if pg.evaluate("U.sSec") != o: pg.click(sec(o) + ' .sglab'); pg.wait_for_timeout(150)

    # tap a section to select it
    ok('Tap a section to record it' in pg.inner_text('main'), 'the song says sections can be recorded')
    pg.click(sec(o4) + ' .sgl >> nth=0'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sSec") == o4 and pg.locator(sec(o4) + '.sel').count() == 1, 'tapping a section selects it, with an outline')
    ok(pg.locator(sec(o4) + ' [data-a=sgRec]').count() == 1 and pg.locator(sec(o4) + ' [data-a=sgTakes]').count() == 0,
       'a selected section offers Record, and no takes pill before there are takes')
    ok('Tap a section' not in pg.inner_text('main'), 'the hint goes once a section is selected')
    pg.click(sec(o4) + ' .sgl >> nth=0'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sSec") is None and pg.locator('.sgsec.sel').count() == 0, 'tapping it again deselects it')
    pg.click(sec(o2) + ' .sglab'); pg.wait_for_timeout(150); pg.click(sec(o4) + ' .sglab'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sSec") == o4 and pg.locator('.sgsec.sel').count() == 1, 'tapping another section moves the selection')
    pg.click('[data-a=sgMode][data-v=perform]'); pg.wait_for_timeout(400)
    pg.click(sec(o4) + ' .sglab'); pg.wait_for_timeout(200)
    ok(pg.locator(sec(o4) + '.sel [data-a=sgRec]').count() == 1, 'sections can be selected in Perform too')
    pg.click('[data-a=sgMode][data-v=practise]'); pg.wait_for_timeout(400)
    pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(200)
    ok(pg.locator('[data-a=sgSec]').count() == 0 and pg.locator('[data-a=sgRec]').count() == 0, 'sections can’t be selected while editing')
    pg.evaluate("sgEndEdit(true);rerender()"); pg.wait_for_timeout(200)

    # record from a section
    pg.evaluate(SPY)
    pg.click(sec(o4) + ' .sglab'); pg.wait_for_timeout(150)
    pg.click(sec(o4) + ' [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1300)
    ok(pg.evaluate("rec.o") == o4 and pg.evaluate("rec.songId") == S['id'], 'Record starts straight away, for that place in the song')
    ok(pg.inner_text('#barT').strip() == 'Recording Chorus 2', 'the top bar says what’s recording: ' + pg.inner_text('#barT').strip())
    ok(pg.locator('.sgmodes.locked').count() == 1 and pg.locator('[data-a=sgSec]').count() == 0, 'the mode switch dims and sections can’t be tapped')
    ok(pg.locator('#barL [data-a=sgBack]').count() == 0 and pg.locator('[data-a=sgEdit]').count() == 0, 'no back or edit while recording')
    ok(pg.locator('#dock .recbar').count() == 1 and pg.locator('#dock .tabbar').count() == 0 and pg.locator('#recMeter i').count() == 14,
       'the recording bar, with the timer and a level meter, takes the place of the tab bar')
    ok(pg.locator(sec(o4) + '.recording').count() == 1 and pg.locator('[data-a=sgRec]').count() == 0, 'the section being recorded is marked, without its pills')
    ok(pg.evaluate("rec.lv.length") > 0, 'the level meter is listening')
    ok(pg.evaluate("scrollY") > 100 and pg.evaluate("(()=>{const r=document.querySelector('.sgsec.recording').getBoundingClientRect(),b=document.querySelector('.recbar').getBoundingClientRect();return r.top<260&&r.top>0&&r.bottom<b.top})()"),
       'the page scrolls to the section, clear of the recording bar')
    ok(pg.evaluate("/\\d:\\d\\d/.test(document.getElementById('recT').textContent)"), 'the timer runs')
    pg.click(sec(o2) + ' .sglab', force=True); pg.wait_for_timeout(150)
    ok(pg.evaluate("rec&&rec.o") == o4 and pg.evaluate("U.sSec") == o4, 'tapping another section does nothing while recording')
    ask = pg.evaluate("window._recAsk.audio"); opts = pg.evaluate("window._recOpts")
    ok(ask.get('echoCancellation') is False and ask.get('noiseSuppression') is False and ask.get('autoGainControl') is False and ask.get('channelCount') == 1,
       'voice processing is off, mono')
    ok(opts.get('audioBitsPerSecond') == 96000, 'about 96 kbps')
    ok(pg.evaluate("pickMime()") != '' , 'a recording format is picked: ' + pg.evaluate("pickMime()"))
    t.shot(pg, 'recording')
    pg.click('[data-a=sgStop]'); pg.wait_for_function("U.sheet==='sgTakes'", timeout=5000); pg.wait_for_timeout(300)
    tk = pg.evaluate("TAKES.map(t=>({id:t.id,o:t.o,s:t.songId,star:t.star}))")
    ok(len(tk) == 1 and tk[0]['o'] == o4 and tk[0]['s'] == S['id'], 'stopping saves the take with its place in the song')
    ok(pg.evaluate("Date.now()-songById(U.songId).practised") < 10000, 'recording a take marks the song as practised')
    txt = pg.text_content('.sheet')
    ok('Chorus 2' in txt and 'New take' in txt and 'Just now' in txt and 'Fresh ears help' in txt, 'the review sheet opens over the song with the new take')
    ok(pg.evaluate("U.view") == 'lyr' and pg.locator('#app .sgsong').count() == 1, 'it’s layered on the same screen')
    ok(pg.locator('.sheet [data-a=sgRec]').inner_text().strip() == 'Record again', 'with Record again')
    t.shot(pg, 'review-sheet')

    pg.click('.newtake [data-a=playTake]'); pg.wait_for_timeout(900)
    ok(pg.evaluate("playingId") == tk[0]['id'], 'the new take plays')
    ok(pg.evaluate(f"parseFloat(document.getElementById('pg-{tk[0]['id']}').style.width)||0") > 0, 'with its progress showing')
    pg.click('.newtake [data-a=playTake]'); pg.wait_for_timeout(150)
    pg.click('.newtake [data-a=star]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("TAKES[0].star") is True and pg.locator('.newtake .star.on').count() == 1, 'starring the new take')
    pg.click('.newtake [data-a=takeNote]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'takeNote', 'notes on a take use the take-note sheet')
    pg.click('.sheet .chip >> nth=0'); pg.click('.sheet [data-a=close].cta'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakes' and pg.evaluate("TAKES[0].note.w.length") == 1, 'and come back to the takes')

    pg.click('.sheet [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1200)
    ok(pg.evaluate("U.sheet") is None, 'Record again closes the sheet and records')
    pg.click('[data-a=sgStop]'); pg.wait_for_function("U.sheet==='sgTakes'&&TAKES.length===2", timeout=5000); pg.wait_for_timeout(200)
    txt = pg.text_content('.sheet')
    ok('Starred' in txt and pg.locator('.sheet .sgtake').count() == 1, 'the starred take is listed under the new one')
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(300)
    ok(pg.locator(sec(o4) + ' [data-a=sgTakes]').inner_text().strip() == '2 takes', 'the selected section shows "2 takes"')
    pg.click(sec(o4) + ' [data-a=sgTakes]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakes' and 'New take' not in pg.text_content('.sheet') and 'Latest' in pg.text_content('.sheet'),
       'the takes pill opens the same sheet, with the latest take')
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(200)
    pg.click(sec(o4) + ' .sglab'); pg.wait_for_timeout(200)
    ok('2 takes' in pg.inner_text(sec(o4) + ' .sghead') and pg.locator(sec(o2) + ' .shared').count() == 0,
       'deselected, its header says "2 takes"; the linked Chorus 1 keeps its own (none)')

    # the keep rule: the last 3 per song, from any section, plus starred
    for _ in range(3):
        select(o1)
        pg.click(sec(o1) + ' [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1100)
        pg.click('[data-a=sgStop]'); pg.wait_for_function("U.sheet==='sgTakes'", timeout=5000); pg.wait_for_timeout(150)
        pg.click('.sheet .xbtn'); pg.wait_for_timeout(200)
    loose = pg.evaluate(f"TAKES.filter(t=>t.songId==='{S['id']}'&&!t.star).map(t=>t.o)")
    ok(len(loose) == 3 and loose.count(o1) == 3, 'only the last 3 unstarred takes of the song are kept, across sections')
    ok(pg.evaluate("TAKES.filter(t=>t.star).length") == 1 and pg.evaluate(f"TAKES.find(t=>t.star).o") == o4, 'the starred take is kept')
    select(o1); pg.click(sec(o1) + ' [data-a=sgTakes]'); pg.wait_for_timeout(300)
    ok('First' in pg.text_content('.sheet') and 'Latest' in pg.text_content('.sheet') and '1 more take in Song practice' in pg.text_content('.sheet'),
       'the sheet shows the latest and the first: ' + pg.text_content('.sheet').replace('\n', ' | ')[:160])
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(200)

    # older takes without a place belong to the whole song, and still show in song practice
    pg.evaluate(f"""(async()=>{{const b=new Blob([new Uint8Array(3000)],{{type:'audio/mp4'}});
      await putTake({{id:'old1',songId:'{S['id']}',created:Date.now()-5*864e5,len:9,size:3000,type:'audio/mp4',blob:b,star:true}});await refreshTakes();rerender();}})()""")
    pg.wait_for_timeout(300)
    ok(pg.evaluate("TAKES.length") == 5 and pg.evaluate("[...document.querySelectorAll('.sgsec')].every(s=>!/[45] takes/.test(s.textContent))"),
       'a take without a place isn’t counted on any section')
    pg.click(f'[data-a=sgPractise]'); pg.wait_for_timeout(400)
    rows = pg.evaluate("[...document.querySelectorAll('.tk')].map(x=>x.textContent)")
    ok(len(rows) == 5 and sum('Verse 1 · ' in r for r in rows) == 3 and sum('Chorus 2 · ' in r for r in rows) == 1,
       'song practice lists every take, saying which section each came from')
    pg.click('[data-a=sheet][data-v=discard]'); pg.wait_for_timeout(250); pg.click('[data-a=discardYes]'); pg.wait_for_timeout(300)
    pg.evaluate(f"openSong('{S['id']}')"); pg.wait_for_timeout(300)

    # unlinking and reordering keep takes in place
    pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(150)
    pg.evaluate(f"U.sheet='sgUnlink';U.sd={{k:'{o4}'}};SG_ACT.sgDoUnlink()"); pg.wait_for_timeout(150)
    pg.evaluate("SG.drag={el:true,from:3,to:0};sgEndDrag()"); pg.wait_for_timeout(150)
    pg.evaluate("sgEndEdit(true);rerender()"); pg.wait_for_timeout(250)
    first = pg.evaluate("songById(U.songId).order[0]")
    ok(first['o'] == o4 and first['sid'] != S['sid'][1], 'the chorus was unlinked and moved to the top')
    ok(pg.evaluate(f"TAKES.filter(t=>t.o==='{o4}').length") == 1 and '1 take' in pg.inner_text('.sgsec >> nth=0'),
       'its takes moved with it')
    select(o4); pg.click(sec(o4) + ' [data-a=sgTakes]'); pg.wait_for_timeout(300)
    ok('Chorus' in pg.inner_text('.sheet h2') and pg.locator('.sheet .sgtake').count() == 1, 'and its sheet still lists it')
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(200)

    # leaving the app mid-take saves it, and the sheet is waiting on return
    select(o3); pg.click(sec(o3) + ' [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1200)
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(1000)
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(800)
    ok(pg.evaluate("!rec") and pg.evaluate(f"TAKES.some(t=>t.o==='{o3}')") and pg.evaluate("U.sheet") == 'sgTakes'
       and 'saved when you left' in pg.inner_text('.toast'), 'leaving the app stops and saves the take, with the sheet waiting')
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(200)

    # recording stops at the time limit, and when leaving the song
    pg.click(sec(o3) + ' [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1100)
    pg.evaluate("rec.started=Date.now()-(MAX_TAKE+1)*1000"); pg.wait_for_function("!rec", timeout=4000); pg.wait_for_timeout(500)
    ok(pg.evaluate("U.sheet") == 'sgTakes', 'recording stops by itself at the time limit')
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(200)
    pg.click(sec(o3) + ' [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1100)
    ids = pg.evaluate("TAKES.map(t=>t.id)")
    pg.evaluate("go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_function("!rec", timeout=4000); pg.wait_for_timeout(400)
    ok(pg.evaluate("ids=>TAKES.some(t=>!ids.includes(t.id))", ids) and pg.evaluate("U.sheet") is None and 'stopped and saved' in pg.inner_text('.toast'),
       'leaving the song stops and saves the take')
    pg.evaluate("sgp().sort='recent';U.tab='songs';U.view=null;render()"); pg.wait_for_timeout(300)
    first_row = pg.inner_text('#slist .rowc >> nth=0')
    ok('River Song' in first_row and 'Practised today' in first_row, 'the list shows it practised today, first under Recently practised')
    pg.context.close()

    # backups: Exclude recordings
    pg = t.page(b, data=with_song_practice())
    pg.evaluate("""(async()=>{const b=new Blob([new Uint8Array(3000).map((_,i)=>i%251)],{type:'audio/mp4'});
      for(const [id,o] of [['k1','oA'],['k2',null]])await putTake(Object.assign({id,songId:'g_1',created:Date.now()-864e5,len:12,size:b.size,type:'audio/mp4',blob:b,star:false},o?{o}:{}));
      await refreshTakes();U.tab='settings';render();})()"""); pg.wait_for_timeout(300)
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    ok(pg.locator('[data-a=exportNoRec][aria-checked=false]').count() == 1, 'backups include recordings unless you exclude them')
    with pg.expect_download(timeout=5000) as dl: pg.click('[data-a=exportSave]')
    full = json.load(open(dl.value.path(), encoding='utf-8'))
    ok(len(full['takes']) == 2 and any(x.get('o') == 'oA' for x in full['takes']) and 'recordingsExcluded' not in full,
       'a normal backup carries the recordings, with their place in the song')
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    pg.click('[data-a=exportNoRec]'); pg.wait_for_function("pendingExport&&pendingExport.noRec&&!pendingExport.busy", timeout=10000); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") == 'exportReady' and 'Not included' in pg.text_content('.sheet') and pg.locator('[data-a=exportNoRec][aria-checked=true]').count() == 1,
       'Exclude recordings remakes the file on the same sheet')
    t.shot(pg, 'export-no-recordings')
    with pg.expect_download(timeout=5000) as dl: pg.click('[data-a=exportSave]')
    path = dl.value.path(); nr = json.load(open(path, encoding='utf-8'))
    ok(nr['takes'] == [] and nr['recordingsExcluded'] is True and nr['summary']['recordings'] == 0, 'the file has no recordings and says so')
    ok(pg.evaluate("p=>checkCode(p)", nr) == nr['checkCode'], 'its check code covers the file as written')
    ok('left out' in ' '.join(nr['README']), 'its read-me says the recordings were left out')
    pg.wait_for_timeout(300)
    ok(pg.evaluate("loadLog()[0].noRec") is True, 'the backup history notes it')

    with pg.expect_file_chooser() as fc: pg.click('[data-a=checkPick]')
    fc.value.set_files(path); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000)
    txt = pg.text_content('.sheet')
    ok('This backup is complete' in txt and 'Recordings not included' in txt, 'Check a backup: complete, recordings not included')
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(200)

    pg.evaluate("D.sessions.pop();save();render()")
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(path); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000)
    txt = pg.text_content('.sheet')
    ok('Recordings not included' in txt and 'keeps the 2 recordings' in txt and 'Restoring removes' not in txt,
       'Import says recordings aren’t included and this device’s are kept')
    t.shot(pg, 'import-no-recordings', full_page=True)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("TAKES.length") == 2 and pg.evaluate("TAKES.every(t=>t.blob&&t.blob.size>0)") and pg.evaluate("D.sessions.length") == 3,
       'restoring it keeps this device’s recordings')
    ok('recordings were kept' in pg.inner_text('.toast'), 'and says so')
    pg.evaluate("U.tab='settings';render()"); pg.click('[data-a=sheet][data-v=undoRestore]'); pg.wait_for_timeout(300)
    ok('didn’t include recordings' in pg.text_content('.sheet'), 'the undo sheet says the recordings were kept')
    pg.click('[data-a=undoYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("TAKES.length") == 2 and pg.evaluate("D.sessions.length") == 2, 'undoing it leaves the recordings alone')
