"""Recording takes with a fake microphone: saving, leaving mid-take, keeping the last 3, playback, and backing up audio."""
import json
from harness import ready

LAUNCH_ARGS = ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']

def run(b, t):
    ok = t.ok
    pg = t.page(b, ctx_args={'permissions': ['microphone']})
    pg.click('[data-a=songStart]'); pg.click('[data-a=song][data-k=g_1]')
    pg.click('[data-a=rec]'); pg.wait_for_timeout(2500); pg.click('[data-a=rec]'); pg.wait_for_timeout(1200)
    ok(pg.evaluate("TAKES.length") == 1, 'recording and stopping saves a take')
    ok(pg.evaluate("X.takes.length") == 1, 'the take belongs to this song practice')

    pg.click('[data-a=rec]'); pg.wait_for_timeout(1500)
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(1200)
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(900)
    ok(pg.evaluate("TAKES.length") == 2 and pg.locator('.toast').count() == 1, 'leaving the app mid-take saves it and says so')

    pg.click('[data-a=rec]'); pg.wait_for_timeout(1200); pg.click('[data-a=exit]'); pg.wait_for_timeout(1500)
    ok(not pg.evaluate("!!rec"), 'leaving the screen stops the recording')
    pg.wait_for_timeout(500)

    pg.click('[data-a=songStart]'); pg.wait_for_timeout(200)
    for _ in range(3):
        pg.click('[data-a=rec]'); pg.wait_for_timeout(1100); pg.click('[data-a=rec]'); pg.wait_for_timeout(900)
    ok(pg.evaluate("TAKES.filter(t=>t.songId==='g_1'&&!t.star).length") == 3, 'only the last 3 unstarred takes per song are kept')
    pg.click('[data-a=playTake] >> nth=0'); pg.wait_for_timeout(400); ok(pg.evaluate("!!playingId"), 'a take plays')
    pg.click('[data-a=playTake] >> nth=0'); pg.wait_for_timeout(200)
    pg.click('[data-a=cta]'); pg.wait_for_timeout(500); pg.click('[data-a=saveHow]'); pg.wait_for_timeout(500)
    ss = pg.evaluate("D.songSessions[0]"); ok(bool(ss) and len(ss['takes']) >= 1, 'song practice is saved with its takes')
    pg.click('.xbtn[data-a=close]'); pg.wait_for_timeout(300)

    pg.evaluate("scrollTo(0,0);U.tab='settings';U.view=null;tabMin=false;render()"); pg.wait_for_timeout(300)
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    with pg.expect_download(timeout=5000) as dl: pg.click('[data-a=exportSave]')
    path = dl.value.path(); data = json.load(open(path, encoding='utf-8'))
    ok(len(data['takes']) >= 3, 'the backup includes the recordings')
    pg.evaluate("(async()=>{await clearTakes();D={v2:true};migrate();save();await refreshTakes();render();})()"); pg.wait_for_timeout(300)
    pg.evaluate("U.tab='settings';render()")
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(path); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.songSessions.length") == 1 and pg.evaluate("TAKES.length") >= 3, 'importing the file restores song practice and recordings')
    ok(pg.evaluate("TAKES.every(t=>t.blob&&t.blob.size>0)"), 'restored recordings have their audio')
