"""3.19 the track player (Track 1): a song's track imported from Files, its waveform read once at import (never again
on open), the four zoom levels (segmented control and pinch), rows that zoom into Line view, the loop (Set start /
Set end, dragging and swapping handles, the 0.5 s minimum, double-tap outside to clear), the loop wrapping while it
plays, speed with the pitch kept, the jog wheel, the floating window and one sound at a time, the song's data
(sg.track and sg.loop in backups; the audio in vocalTracks, which backups, restores and Reset never touch), a
restored song without its track, deleting, and every size in light and dark.
The fixtures are synthetic: tones with gaps, written by the test as WAV files. Nothing copyrighted is ever used."""
import os, wave, struct, math, json
from harness import OUT, ready, fix

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']
# counts every decodeAudioData, so a reopen can prove it didn't decode again
COUNT = ("(()=>{const P=(window.BaseAudioContext||window.AudioContext).prototype,o=P.decodeAudioData;window.__dec=0;"
         "P.decodeAudioData=function(){window.__dec++;return o.apply(this,arguments)}})()")
SONG = "go(()=>{U.tab='songs';U.view='lyr';U.songId='g_1'})"
INK = ("(()=>{const c=document.getElementById('trkC');if(!c)return 0;const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;"
       "let n=0;for(let i=3;i<d.length;i+=4)if(d[i])n++;return n})()")
LOOP = "JSON.stringify(songById(%r).loop||null)"
NIDB = ("async()=>{const d=await new Promise(r=>{const q=indexedDB.open('vocalTracks',1);q.onsuccess=()=>r(q.result)});"
        "const c=s=>new Promise(r=>{const q=d.transaction(s).objectStore(s).count();q.onsuccess=()=>r(q.result)});"
        "const n=[await c('audio'),await c('peaks')];d.close();return n}")
# a short, real recording as a take (4 s of a quiet tone)
WAV_TAKE = """async(id)=>{const n=8000*4,b=new ArrayBuffer(44+n*2),v=new DataView(b);const w=(o,s)=>[...s].forEach((c,i)=>v.setUint8(o+i,c.charCodeAt(0)));
 w(0,'RIFF');v.setUint32(4,36+n*2,true);w(8,'WAVE');w(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);
 v.setUint32(24,8000,true);v.setUint32(28,16000,true);v.setUint16(32,2,true);v.setUint16(34,16,true);w(36,'data');v.setUint32(40,n*2,true);
 for(let i=0;i<n;i++)v.setInt16(44+i*2,Math.round(Math.sin(i/9)*200),true);
 const bl=new Blob([b],{type:'audio/wav'});await putTake({id,songId:'g_1',created:Date.now()-864e5,len:4,size:bl.size,type:'audio/wav',blob:bl,star:false});
 await refreshTakes();rerender();}"""
LYRICS = "[Verse]\nPaper boats along the gutter\nFloat away\n\n[Chorus]\nCarry me over\nLet the river know"


def tones(path, secs, rate=8000):
    """Half a second of tone, half a second of quiet, louder through each five seconds."""
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        fr = bytearray()
        for i in range(int(rate * secs)):
            t = i / rate
            v = int(9000 * math.sin(2 * math.pi * 330 * t) * (0.25 + 0.75 * ((int(t) % 5) / 4))) if int(t * 2) % 2 == 0 else 0
            fr += struct.pack('<h', v)
        w.writeframes(bytes(fr))


def F(name, secs):
    p = os.path.join(OUT, name)
    if not os.path.exists(p): tones(p, secs)
    return p


def track(): return F('Paper Boats.wav', 60)


def loaded(pg, sid='g_1'):
    pg.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()&&TRACK.state().id===id&&TRACK.el()&&TRACK.el().readyState>=1&&!!document.getElementById('trkPP')",
                         arg=sid, timeout=15000)
    pg.wait_for_timeout(200)


def add_row(pg, f=None, sid='g_1'):
    """Add a track through the song page's Practice row (the real door, with the file picker)."""
    with pg.expect_file_chooser() as fc: pg.click('#app [data-a=trkAdd]')
    fc.value.set_files(f or track())
    loaded(pg, sid)


def x_of(pg, v):
    return pg.evaluate("v=>{const c=document.getElementById('trkC'),r=c.getBoundingClientRect(),W=TRK_LEVELS[TRACK.level()].win;"
                       "return r.left+r.width*TRK_HEAD+(v-TRACK.now())*r.width/W}", v)


def strip_y(pg):
    return pg.evaluate("(()=>{const r=document.getElementById('trkStrip').getBoundingClientRect();return r.top+r.height/2})()")


def drag(pg, x0, y0, x1, y1, steps=10):
    pg.mouse.move(x0, y0); pg.mouse.down(); pg.mouse.move(x1, y1, steps=steps); pg.mouse.up(); pg.wait_for_timeout(120)


def loop(pg, sid='g_1'): return json.loads(pg.evaluate(LOOP % sid))


def importing(b, t):
    ok = t.ok
    pg = t.page(b, init=COUNT)
    pg.evaluate(SONG); pg.wait_for_timeout(250)
    acc = pg.evaluate("document.getElementById('trackIn').accept")
    ok('audio/*' not in acc and all(x in acc.split(',') for x in ('.mp3', '.m4a', '.wav', 'audio/mpeg', 'audio/mp4')),
       f'3.19.1: the picker names MP3, M4A and WAV one by one (iOS greys out audio files for audio/*): {acc}')
    row = pg.locator('#app [data-a=trkAdd]')
    ok(row.count() == 1 and 'Add track' in row.inner_text(), 'the song page’s Practice group reads Add track before there’s a track')
    add_row(pg)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("U.songId") == 'g_1', 'adding a track opens the player for that song')
    ok(pg.evaluate("__dec") == 1, f'the track was decoded once, at import ({pg.evaluate("__dec")})')
    sg = pg.evaluate("songById('g_1').track")
    ok(sg and sg['name'] == 'Paper Boats.wav' and abs(sg['dur'] - 60) < 0.05, f'the song keeps the track’s name and length: {sg}')
    n = pg.evaluate("TRACK.peaks().length")
    ok(abs(n - 3000) <= 2, f'its waveform is peaks at 50 a second ({n} for 60 s)')
    ok(pg.evaluate("TRACK.peaks() instanceof Uint8Array"), 'kept as a Uint8Array')
    ok(pg.evaluate(INK) > 1000, 'the strip draws the waveform')
    ok(pg.locator('#barT').inner_text().strip() == 'Versace on the Floor · bridge', 'the top bar shows the song’s title')
    ok(pg.locator('#barL [data-a=trkBack][aria-label=Back]').count() == 1 and pg.locator('#barR [data-a=trkMenu]').count() == 1,
       'with Back and the track’s settings')
    ok(pg.locator('#dock .trktr [data-a=trkToStart]').count() == 1 and pg.locator('#dock #trkPP').count() == 1 and pg.locator('#dock #trkLoopB').count() == 1,
       'the transport (back to loop start, play, loop) is in the dock')
    ok(pg.locator('#app [data-a=trkSet][data-v=start]').count() == 1 and pg.locator('#app [data-a=trkSet][data-v=end]').count() == 1 and pg.locator('#trkSpd').inner_text() == '1×',
       'Set start, Set end and the speed chip are on screen')
    ok(pg.evaluate("[...document.querySelectorAll('#app button,#dock button')].length") <= 12, 'no toolbar of ten icons: only a handful of controls')
    ok(pg.locator('.trkbusy').count() == 0, 'the “Reading the track…” note has gone')
    t.shot(pg, 'player')
    # reopen: nothing decoded again
    pg.reload(); ready(pg)
    ok(pg.evaluate("TRACK.has('g_1')"), 'after a reload, the track is still on the device')
    pg.evaluate(SONG); pg.wait_for_timeout(200)
    r = pg.locator('#app [data-a=trkOpen]')
    ok(r.count() == 1 and 'Track' in r.inner_text() and '1:00' in r.inner_text(), 'the Practice row now opens the player: ' + r.inner_text().replace('\n', ' '))
    r.click(); loaded(pg)
    ok(pg.evaluate("__dec") == 0 and pg.evaluate(INK) > 1000, 'reopening draws the saved waveform without decoding again')
    ok(pg.evaluate(NIDB) == [1, 1], 'the audio and its peaks are separate entries in vocalTracks')
    # Back goes to the song page
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.songId") == 'g_1', 'Back goes to the song page')
    # a file that isn't audio
    bad = os.path.join(OUT, 'not-audio.mp3'); open(bad, 'w').write('this is not audio ' * 50)
    pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId=D.songs[0].id})")
    pg.evaluate("D.songs.push({id:'g_2',name:'Second',added:Date.now()});save();go(()=>{U.view='lyr';U.songId='g_2'})"); pg.wait_for_timeout(200)
    with pg.expect_file_chooser() as fc: pg.click('#app [data-a=trkAdd]')
    fc.value.set_files(bad)
    pg.wait_for_function("!TRACK.busy()", timeout=10000); pg.wait_for_timeout(200)
    ok('can’t be opened. Try an MP3 or M4A from Files' in pg.inner_text('.toast'), 'a file that won’t decode says so: ' + pg.inner_text('.toast'))
    ok(not pg.evaluate("TRACK.has('g_2')") and not pg.evaluate("songById('g_2').track"), 'and nothing is saved')
    # over 60 MB: ask once first
    pg.evaluate("""()=>{TRACK.expect('g_2');const f=new File([new Uint8Array(61*1048576)],'big.mp3',{type:'audio/mpeg'}),dt=new DataTransfer();
      dt.items.add(f);const i=document.getElementById('trackIn');i.files=dt.files;i.dispatchEvent(new Event('change'))}""")
    pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'trkBig' and '61 MB' in pg.inner_text('.sheet'), 'a file over 60 MB asks once before importing')
    pg.click('.sheet .ghost'); pg.wait_for_timeout(250)
    ok(not pg.evaluate("TRACK.busy()") and not pg.evaluate("TRACK.has('g_2')"), 'Cancel leaves it')
    pg.context.close()


def levels(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate(SONG); pg.wait_for_timeout(200); add_row(pg)
    ok(pg.evaluate("TRACK.level()") == 1 and pg.locator('#app .trklv button.on').inner_text() == 'Line', 'it opens on Line')
    names = pg.evaluate("[...document.querySelectorAll('#app .trklv button')].map(b=>b.textContent)")
    ok(names == ['Phrase', 'Line', 'Song', 'Markers'], f'four zoom levels (Q02: Phrase, Line, Song, Markers): {names}')
    pg.click('#app .trklv button[data-v="0"]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("TRACK.level()") == 0 and pg.locator('#trkC').count() == 1 and pg.locator('#trkJog').count() == 1, 'Phrase is the strip with the jog wheel')
    ok(abs(pg.evaluate("document.getElementById('trkStrip').getBoundingClientRect().height") - 148) < 1.5, 'the strip is 148 px tall (Q02)')
    w = pg.evaluate("(()=>{const s=document.getElementById('trkStrip').getBoundingClientRect(),c=document.getElementById('trkC').getBoundingClientRect();return [s.width,c.width]})()")
    ok(abs(w[0] - w[1] - 48) < 1.5, f'the waveform stops 48 px short of the jog wheel ({w})')
    j = pg.evaluate("(()=>{const j=document.getElementById('trkJog').getBoundingClientRect();return [j.width,j.left,innerWidth]})()")
    ok(j[0] == 96 and abs(j[1] - (j[2] - 48)) < 1.5, f'the jog wheel is a 96 px circle half off the right edge ({j})')
    pg.click('#app .trklv button[data-v="2"]'); pg.wait_for_timeout(150)
    ok(pg.locator('#trkC').count() == 0 and pg.locator('#trkJog').count() == 0 and pg.locator('#app .trkrow').count() == 3,
       'Song shows the whole song in rows of 24 s (3 for 60 s), and the jog wheel hides')
    ok(pg.locator('#app .trkrow .trkg').all_inner_texts() == ['0:00', '0:24', '0:48'], 'each row has its time in the gutter')
    ok('Tap to move the playhead' in pg.inner_text('#trkHint'), 'the hint says a tap moves the playhead')
    t.shot(pg, 'rows')
    # 3.20: tapping a row places the playhead there and stays in that view (zoom changes with the pills or a pinch)
    pg.click('#app .trklv button[data-v="2"]'); pg.wait_for_timeout(150)
    r = pg.evaluate("(()=>{const c=document.querySelectorAll('#app .trkrow canvas')[1].getBoundingClientRect();return [c.left+c.width/2,c.top+c.height/2]})()")
    pg.mouse.click(r[0], r[1]); pg.wait_for_timeout(250)
    ok(pg.evaluate("TRACK.level()") == 2 and abs(pg.evaluate("TRACK.now()") - 36) < 0.6, f'tapping the middle of the second row puts the playhead at 0:36 and stays in Song ({pg.evaluate("TRACK.now()")})')
    pg.click('#app .trklv button[data-v="1"]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("TRACK.level()") == 1, 'the Line pill zooms in')
    # pinch
    cdp = pg.context.new_cdp_session(pg)

    def pinch(d0, d1):
        c = pg.evaluate("(()=>{const r=document.getElementById('trkWave').getBoundingClientRect();return [r.left+r.width/2,r.top+Math.min(r.height,96)/2]})()")
        pts = lambda d: [{'x': c[0] - d / 2, 'y': c[1], 'id': 1}, {'x': c[0] + d / 2, 'y': c[1], 'id': 2}]
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': pts(d0)})
        for i in range(1, 11): cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': pts(d0 + (d1 - d0) * i / 10)})
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        pg.wait_for_timeout(200)
    pinch(150, 100)
    ok(pg.evaluate("TRACK.level()") == 2, f'pinching in by 50 px zooms out one level (Line → Song): {pg.evaluate("TRACK.level()")}')
    pinch(120, 220)
    ok(pg.evaluate("TRACK.level()") == 0, f'spreading 100 px zooms in two (Song → Phrase): {pg.evaluate("TRACK.level()")}')
    ok(pg.locator('#app .trklv button.on').inner_text() == 'Phrase', 'the segmented control follows the pinch')
    pinch(300, 60)
    ok(pg.evaluate("TRACK.level()") == 3, 'and a big pinch stops at Markers')
    # speed and zoom are remembered on this device
    pg.click('#app .trklv button[data-v="1"]'); pg.wait_for_timeout(100)
    pg.click('#trkSpd'); pg.wait_for_timeout(100)
    pg.reload(); ready(pg)
    pg.evaluate("TRACK.open('g_1')"); loaded(pg)
    ok(pg.evaluate("TRACK.level()") == 1 and pg.evaluate("TRACK.speed()") == 0.75, 'the zoom level and speed are remembered after a reload')
    ok('trkLevel' in pg.evaluate("localStorage.getItem('vocalSongPrefs')"), 'kept with this device’s song settings, not the backed-up data')
    # gesture priority: a sideways swipe on the strip never goes back
    ok(pg.evaluate("document.getElementById('trkStrip').hasAttribute('data-own-gesture')&&document.getElementById('trkJog').hasAttribute('data-own-gesture')"),
       'the strip and jog wheel claim their own gestures')
    y = strip_y(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 40, 'y': y}]})
    for i in range(1, 9): cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 40 + i * 35, 'y': y}]})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'trk', 'a sideways drag on the strip scrubs instead of swiping back')
    pg.context.close()


def loops(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(SONG); pg.wait_for_timeout(200); add_row(pg)
    pg.click('#app .trklv button[data-v="0"]'); pg.wait_for_timeout(100)  # Phrase: 6 s across the strip
    pg.evaluate("TRACK.seek(10)")
    pg.click('[data-a=trkSet][data-v=start]'); pg.wait_for_timeout(100)
    ok(loop(pg) == {'start': 10, 'end': 60, 'on': True}, f'Set start with no end runs to the end of the song, and turns the loop on: {loop(pg)}')
    pg.evaluate("TRACK.seek(12)"); pg.click('[data-a=trkSet][data-v=end]'); pg.wait_for_timeout(100)
    ok(loop(pg) == {'start': 10, 'end': 12, 'on': True}, f'Set end at the playhead: {loop(pg)}')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalTracker')).songs.find(s=>s.id==='g_1').loop.end") == 12, 'the loop is saved with the song')
    pg.evaluate("TRACK.seek(8)"); pg.click('[data-a=trkSet][data-v=end]'); pg.wait_for_timeout(100)
    ok(loop(pg) == {'start': 0, 'end': 8, 'on': True}, f'an end before the start starts a fresh range from 0:00 (FCP’s In and Out): {loop(pg)}')
    pg.evaluate("songById('g_1').loop={start:10,end:12,on:true};TRACK.seek(11)"); pg.wait_for_timeout(50)
    y = strip_y(pg)
    # drag the start handle past the end: they swap
    drag(pg, x_of(pg, 10), y, x_of(pg, 13.5), y)
    l = loop(pg)
    ok(abs(l['start'] - 12) < 0.05 and abs(l['end'] - 13.5) < 0.1, f'dragging the start handle past the end swaps them: {l}')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalTracker')).songs.find(s=>s.id==='g_1').loop.end") == l['end'], 'and saves on release')
    # the 0.5 s minimum
    drag(pg, x_of(pg, l['end']), y, x_of(pg, l['start'] + 0.1), y)
    l = loop(pg)
    ok(abs(l['end'] - l['start'] - 0.5) < 0.02, f'a loop is never shorter than 0.5 s: {l}')
    # the handle drawn: orange on the strip
    px = pg.evaluate("x=>{const c=document.getElementById('trkC'),r=c.getBoundingClientRect(),k=c.width/r.width,d=c.getContext('2d').getImageData(Math.round((x-r.left)*k),Math.round(c.height-6*k),1,1).data;return [d[0],d[1],d[2],d[3]]}", x_of(pg, l['start']))
    ok(px[0] > 200 and 100 < px[1] < 190 and px[2] < 80, f'the handles are orange ({px})')
    # double-tap inside does nothing; outside clears
    pg.evaluate("songById('g_1').loop={start:10,end:12,on:true};TRACK.seek(11)")
    xi = x_of(pg, 11.5); pg.mouse.click(xi, y); pg.mouse.click(xi, y); pg.wait_for_timeout(150)
    ok(loop(pg) is not None, 'a double-tap inside the loop keeps it')
    xo = x_of(pg, 9); pg.mouse.click(xo, y); pg.mouse.click(xo, y); pg.wait_for_timeout(150)
    ok(loop(pg) is None and 'Loop cleared' in pg.inner_text('.toast'), 'a double-tap outside the loop clears it')
    # scrubbing the strip: the waveform follows the finger, the playhead stays
    pg.evaluate("TRACK.seek(20)")
    drag(pg, 200, y, 140, y)
    ok(abs(pg.evaluate("TRACK.now()") - (20 + 60 * 6 / pg.evaluate("document.getElementById('trkC').getBoundingClientRect().width"))) < 0.2,
       f'dragging the strip left moves later by the distance ({pg.evaluate("TRACK.now()")})')
    # Loop with no loop set
    pg.click('#trkLoopB'); pg.wait_for_timeout(100)
    ok('Set a start and end' in pg.inner_text('.toast'), 'Loop with nothing set says to set a start and end')
    t.shot(pg, 'loop')
    pg.context.close()


def playing(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(SONG); pg.wait_for_timeout(200); add_row(pg)
    for want in (0.75, 0.5, 1):
        pg.click('#trkSpd'); pg.wait_for_timeout(80)
        ok(pg.evaluate("[TRACK.el().playbackRate,TRACK.el().preservesPitch]") == [want, True] and pg.inner_text('#trkSpd') == str(want) + '×',
           f'speed {want}× plays at that rate with the pitch kept')
    pg.evaluate("songById('g_1').loop={start:5,end:6,on:true};save();TRACK.seek(5.6)")
    pg.click('#trkPP'); pg.wait_for_timeout(100)
    ok(not pg.evaluate("TRACK.el().paused") and pg.locator('#trkPP[aria-label=Pause]').count() == 1, 'Play plays (and becomes Pause)')
    s = []
    for _ in range(14): s.append(pg.evaluate("TRACK.el().currentTime")); pg.wait_for_timeout(100)
    ok(max(s) < 6.12 and min(s[4:]) < 5.6 and min(s) >= 4.99, f'the loop wraps while it plays: {[round(x, 2) for x in s]}')
    pg.click('#trkLoopB'); pg.wait_for_timeout(100)
    ok(not loop(pg)['on'] and pg.locator('#trkLoopB.on').count() == 0, 'Loop turns it off (kept, not orange)')
    pg.evaluate("TRACK.seek(5.6)"); pg.wait_for_timeout(900)
    ok(pg.evaluate("TRACK.el().currentTime") > 6.2, 'with the loop off it plays through')
    pg.click('#trkLoopB'); pg.wait_for_timeout(50)
    pg.evaluate("TRACK.seek(30)"); pg.click('[data-a=trkToStart]'); pg.wait_for_timeout(100)
    ok(abs(pg.evaluate("TRACK.now()") - 5) < 0.3, 'back to loop start goes to the loop’s start')
    pg.click('#trkPP'); pg.wait_for_timeout(100)
    pg.evaluate("TRACK.seek(40)"); pg.click('#trkPP'); pg.wait_for_timeout(150)
    ok(5 <= pg.evaluate("TRACK.el().currentTime") < 6.1, 'with the loop on, Play from outside it starts at its start')
    # stillness: the page isn't redrawn while it plays
    pg.evaluate("window.__app=document.getElementById('trkStrip')"); pg.wait_for_timeout(500)
    ok(pg.evaluate("window.__app===document.getElementById('trkStrip')"), 'nothing is redrawn while it plays, only the waveform and time')
    pg.click('#trkPP'); pg.wait_for_timeout(100)
    # the jog wheel
    for lvl, win in ((0, 6), (1, 16)):
        pg.click(f'#app .trklv button[data-v="{lvl}"]'); pg.wait_for_timeout(100)
        pg.evaluate("TRACK.seek(20)")
        j = pg.evaluate("(()=>{const r=document.getElementById('trkJog').getBoundingClientRect();return [r.left+24,r.top+r.height/2]})()")
        drag(pg, j[0], j[1], j[0], j[1] + 90, 12)
        got, exp = pg.evaluate("TRACK.now()") - 20, 90 * win / 300
        ok(abs(got - exp) < 0.12, f'at {["Phrase", "Line"][lvl]}, a 90 px drag on the jog wheel moves {exp:.2f} s ({got:.2f})')
        drag(pg, j[0], j[1], j[0], j[1] - 45, 6)
        ok(abs(pg.evaluate("TRACK.now()") - 20 - exp / 2) < 0.12, 'and dragging up moves it back')
    pg.context.close()


def windows(b, t):
    ok = t.ok
    pg = t.page(b)
    ok(pg.evaluate("FW_KINDS.map(k=>k.id)") == ['take', 'video', 'track', 'clock', 'session'], 'the floating window order is take → video → track → playing along → session')
    pg.evaluate(SONG); pg.wait_for_timeout(200); add_row(pg)
    pg.click('#app .trklv button[data-v="0"]'); pg.wait_for_timeout(100)
    pg.evaluate("TRACK.seek(12)"); pg.click('#trkPP'); pg.wait_for_timeout(300)
    ok(not pg.evaluate("FW.shown"), 'no floating window on the player itself')
    pg.evaluate("go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'track' and 'Playing · Versace on the Floor · bridge' in pg.inner_text('#fw'),
       'leaving while it plays shows “Playing · song title” in the floating window: ' + pg.inner_text('#fw').replace('\n', ' '))
    ok(not pg.evaluate("TRACK.el().paused"), 'and it keeps playing')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("TRACK.el().paused") and pg.evaluate("FW.shown") == 'track', 'its button pauses, and the window stays')
    pg.click('#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("TRACK.level()") == 0 and pg.evaluate("TRACK.now()") > 12, 'tapping it goes back to the player at the same zoom and place')
    pg.evaluate("go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(300)
    ok(not pg.evaluate("FW.shown"), 'paused on its own screen, leaving shows no window')
    # one sound at a time: takes
    pg.evaluate(WAV_TAKE, 'tk1')
    pg.evaluate("TRACK.play()"); pg.wait_for_timeout(200)
    pg.evaluate("playTake('tk1')"); pg.wait_for_timeout(300)
    ok(pg.evaluate("TRACK.el().paused") and pg.evaluate("!!playingId"), 'playing a take pauses the track')
    pg.evaluate("TRACK.play()"); pg.wait_for_timeout(300)
    ok(not pg.evaluate("playingId") and not pg.evaluate("TRACK.el().paused"), 'playing the track stops the take')
    # the coach video
    pg.set_input_files('#coachIn', fix('coach-short.webm'))
    pg.wait_for_function("COACH.has()&&!COACH.busy()", timeout=15000); pg.wait_for_timeout(200)
    pg.evaluate("TRACK.play()"); pg.wait_for_timeout(200)
    pg.evaluate("COACH.play()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("TRACK.el().paused") and not pg.evaluate("COACH.el().paused"), 'playing the coach video pauses the track')
    pg.evaluate("TRACK.play()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("COACH.el().paused") and not pg.evaluate("TRACK.el().paused"), 'playing the track pauses the coach video')
    # Song Clock's play-along
    pg.evaluate("l=>{U.sDraft={step:2,title:'river song',artist:'',text:l,blocks:splitBlocks(l)};sgSaveDraft()}", LYRICS); pg.wait_for_timeout(400)
    # Q05: play-along needs the song's own track on this device, so the river song gets one (from Files, as Add track)
    rid = pg.evaluate("D.songs.find(x=>x.name==='River Song').id")
    pg.evaluate("id=>TRACK.expect(id)", rid); pg.set_input_files('#trackIn', F('River.wav', 20))
    pg.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()", arg=rid, timeout=15000); pg.wait_for_timeout(300)
    pg.evaluate("(()=>{const s=D.songs.find(x=>x.name==='River Song'),L=ckLines(s);ckStore(s,L,ckSpread(s,L,[0,10]),[true,true],L.map(()=>false),{est:true});go(()=>{U.tab='songs';U.view='lyr';U.songId=s.id});ckOn(s)})()")
    pg.wait_for_timeout(200)
    pg.evaluate("TRACK.play()"); pg.wait_for_timeout(300)
    ok(pg.evaluate("NOW.kind()") == 'track' and not pg.evaluate("TRACK.state().along"), 'the track player is playing on its own')
    pg.evaluate("CLOCK.play(0)"); pg.wait_for_timeout(400)
    ok(pg.evaluate("CLOCK.state().run") and pg.evaluate("NOW.kind()") == 'clock' and (pg.evaluate("TRACK.el().paused") or pg.evaluate("TRACK.state().along") == rid),
       'starting play-along stops the track player (play-along takes the sound over, playing its own song’s track)')
    pg.evaluate("TRACK.play()"); pg.wait_for_timeout(300)
    ok(not pg.evaluate("CLOCK.state().run") and not pg.evaluate("TRACK.el().paused"), 'playing the track pauses play-along')
    pg.evaluate("TRACK.pause()")
    # the Song controls grid has a Track tile
    pg.wait_for_timeout(200)
    pg.evaluate("CLOCK.off()")
    pg.evaluate("id=>TRACK.forget([id])", rid); pg.wait_for_timeout(300)  # back to a song without its track
    sid = pg.evaluate("D.songs.find(x=>x.name==='River Song').id")
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})", sid); pg.wait_for_timeout(250)
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250)
    ok(pg.inner_text('.sheet [data-v=track]').strip() == 'Add track', 'the Song controls grid has an Add track tile for a song without one')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(250)
    add_row(pg, sid=sid)
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})", sid); pg.wait_for_timeout(250)
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250)
    ok(pg.inner_text('.sheet [data-v=track]').strip() == 'Track', 'once it has one, the tile reads Track')
    pg.click('.sheet [data-a=ckTile][data-v=track]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("U.songId") == sid, 'and opens the player')
    pg.context.close()


def data(b, t):
    ok = t.ok
    pg = t.page(b)
    # a song with lyrics and timing, so a restore can be checked for both
    pg.evaluate("l=>{U.sDraft={step:2,title:'river song',artist:'',text:l,blocks:splitBlocks(l)};sgSaveDraft()}", LYRICS); pg.wait_for_timeout(400)
    sid = pg.evaluate("D.songs.find(x=>x.name==='River Song').id")
    pg.evaluate("(()=>{const s=D.songs.find(x=>x.name==='River Song'),L=ckLines(s);ckStore(s,L,ckSpread(s,L,[0,10]),[true,true],L.map(()=>false),{est:true})})()")
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})", sid); pg.wait_for_timeout(250)
    add_row(pg, sid=sid)
    pg.evaluate("id=>{songById(id).loop={start:4,end:7.5,on:true};save()}", sid)
    timing = pg.evaluate("id=>JSON.stringify(songById(id).timing)", sid)
    # backups: the track's name, length and the loop travel; the audio doesn't
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='storage'})"); pg.wait_for_timeout(200)
    ok('Song tracks' in pg.inner_text('#app') and '1 ·' in pg.locator('#app .grp:not(.setuse)').filter(has_text='Song tracks').inner_text(), 'Settings › Storage counts the song tracks')
    pg.evaluate("SET.open('backup')"); pg.wait_for_timeout(200); pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=15000)
    txt = pg.evaluate("pendingExport.file.text()")
    bk = json.loads(txt); s = [x for x in bk['data']['songs'] if x['id'] == sid][0]
    ok(s.get('track', {}).get('name') == 'Paper Boats.wav' and s.get('loop') == {'start': 4, 'end': 7.5, 'on': True}, 'a backup carries the song’s track name, length and loop')
    ok('audio/wav' not in txt and len(txt) < 200000, 'but never the track’s audio')
    pg.click('.xbtn'); pg.wait_for_timeout(300)
    p = os.path.join(OUT, 'track-backup.json'); open(p, 'w', encoding='utf-8').write(txt)
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(p); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(400)
    ok(pg.evaluate("id=>TRACK.has(id)", sid) and pg.evaluate(NIDB) == [1, 1], 'restoring a backup leaves vocalTracks alone')
    ok(pg.evaluate("id=>JSON.stringify(songById(id).loop)", sid) == '{"start":4,"end":7.5,"on":true}', 'and the loop comes back with the song')
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(200)
    pg.click('[data-a=sheet][data-v=resetAll]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=resetAll]'); pg.wait_for_function("!D.songs.length", timeout=5000); pg.wait_for_timeout(300)
    ok(pg.evaluate(NIDB) == [1, 1], 'Reset all data leaves vocalTracks alone too')
    ok(not pg.evaluate("TRACK.state().loaded"), 'and the player lets go of the deleted song’s audio')
    pg.context.close()

    # another device: the song comes back without its track
    pg = t.page(b, init=COUNT)
    with pg.expect_file_chooser() as fc:
        pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='backup'})"); pg.wait_for_timeout(200); pg.click('[data-a=importPick]')
    fc.value.set_files(p); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(400)
    ok(not pg.evaluate("id=>TRACK.has(id)", sid), 'on another device, the restored song has no track')
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})", sid); pg.wait_for_timeout(250)
    r = pg.locator('#app [data-a=trkAdd]')
    ok(r.count() == 1 and 'Track not on this device' in r.inner_text() and 'Add track' in r.inner_text(),
       'its song page shows “Track not on this device” with Add track: ' + r.inner_text().replace('\n', ' '))
    ok(pg.evaluate("id=>JSON.stringify(songById(id).timing)", sid) == timing and pg.evaluate("id=>songById(id).loop.end", sid) == 7.5,
       'its loop and timings are intact')
    pg.evaluate("id=>TRACK.open(id)", sid); pg.wait_for_timeout(300)
    ok('Track not on this device' in pg.inner_text('#app') and pg.locator('#app [data-a=trkAdd]').count() == 1, 'the player says the same, with Add track')
    t.shot(pg, 'missing')
    with pg.expect_file_chooser() as fc: pg.click('#app [data-a=trkAdd]')
    fc.value.set_files(track()); loaded(pg, sid)
    ok(pg.evaluate("id=>JSON.stringify(songById(id).loop)", sid) == '{"start":4,"end":7.5,"on":true}' and pg.evaluate("TRACK.state().id") == sid,
       're-importing the same file brings the player back with the same loop')
    ok('different length' not in (pg.inner_text('.toast') if pg.locator('.toast').count() else ''), 'with no length note for the same file')
    # a different length: a quiet note
    pg.click('#barR [data-a=trkMenu]'); pg.wait_for_timeout(250)
    ok('Replace track' in pg.inner_text('.sheet') and 'Remove track' in pg.inner_text('.sheet') and 'isn’t included in backups' in pg.inner_text('.sheet'),
       'the settings button offers Replace track and Remove track')
    with pg.expect_file_chooser() as fc: pg.click('.sheet [data-a=trkReplace]')
    fc.value.set_files(F('Paper Boats long.wav', 63)); pg.wait_for_function("id=>!TRACK.busy()&&TRACK.state().id===id&&TRACK.state().dur>62", arg=sid, timeout=15000)
    pg.wait_for_timeout(200)
    ok('different length, so timings may be off' in pg.inner_text('.toast'), 'replacing with a track of another length says timings may be off')
    SLOTS = "id=>JSON.stringify(songById(id).timing.slots)"
    ok(pg.evaluate(SLOTS, sid) == json.dumps(json.loads(timing)['slots'], separators=(',', ':')) and pg.evaluate("id=>songById(id).loop.end", sid) == 7.5,
       'Replace keeps the loop and timings')
    ok(pg.evaluate("id=>[songById(id).timing.len,songById(id).timing.lenLink]", sid) == [63, True], '3.20: a linked length follows the new file')
    ok(abs(pg.evaluate("id=>songById(id).track.dur", sid) - 63) < 0.05, 'and the song knows the new length')
    # Remove track
    pg.click('#barR [data-a=trkMenu]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=sheet][data-v=trkDel]'); pg.wait_for_timeout(250)
    ok('Remove the track?' in pg.inner_text('.sheet'), 'Remove track asks first')
    pg.click('.sheet [data-a=trkRemove]'); pg.wait_for_timeout(500)
    ok(not pg.evaluate("id=>TRACK.has(id)", sid) and not pg.evaluate("id=>songById(id).track", sid) and pg.evaluate(NIDB) == [0, 0],
       'Remove deletes the audio and peaks and clears the song’s track')
    ok(pg.evaluate("id=>songById(id).loop.end", sid) == 7.5 and pg.evaluate(SLOTS, sid) == json.dumps(json.loads(timing)['slots'], separators=(',', ':')),
       'but the loop and timings stay')
    ok(pg.evaluate("id=>[songById(id).timing.len,!!songById(id).timing.lenLink]", sid) == [63, False], '3.20: the length is kept, no longer linked')
    ok(pg.evaluate("U.view") == 'lyr', 'and goes back to the song')
    # cleanSong checks loops and tracks
    res = pg.evaluate("""[
      cleanSong({id:'a',name:'A',loop:{start:-1,end:5,on:true}}).loop,
      cleanSong({id:'a',name:'A',loop:{start:5,end:3,on:true}}).loop,
      cleanSong({id:'a',name:'A',track:{name:'x.mp3',dur:60},loop:{start:50,end:80,on:true}}).loop,
      cleanSong({id:'a',name:'A',track:{name:'x.mp3',dur:60},loop:{start:59.8,end:70}}).loop,
      cleanSong({id:'a',name:'A',loop:{start:'1',end:5}}).loop,
      cleanSong({id:'a',name:'A',loop:{start:1,end:1.2}}).loop,
      cleanSong({id:'a',name:'A',loop:{start:1,end:4,on:'yes'}}).loop,
      cleanSong({id:'a',name:'A',track:{name:'x.mp3',dur:-3}}).track,
      cleanSong({id:'a',name:'A',track:'x'}).track,
      cleanSong({id:'a',name:'A',track:{dur:61.234}}).track]""")
    ok(res[0] is None and res[1] is None, 'a loop with a negative time or its end before its start is dropped')
    ok(res[2] == {'start': 50, 'end': 60, 'on': True}, f'a loop past the track’s end is clamped to it: {res[2]}')
    ok(res[3] is None and res[4] is None and res[5] is None, 'one left shorter than 0.5 s, or with times that aren’t numbers, is dropped')
    ok(res[6] == {'start': 1, 'end': 4, 'on': False}, 'on is true or false')
    ok(res[7] is None and res[8] is None and res[9] == {'name': '', 'dur': 61.23}, f'a bad track is dropped; a good one is tidied ({res[9]})')
    pg.context.close()


def new_song(b, t):
    # 3.20: New song from track is replaced by the + sheet's Add media (test_batch12 covers it); the old door is gone
    ok = t.ok
    pg = t.page(b)
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); pg.wait_for_timeout(250)
    ok(pg.locator('[data-a=trkNew]').count() == 0 and pg.locator('#barR [data-a=sgNew]').count() == 1,
       'Songs has one + (New song from track is gone)')
    pg.evaluate("D.songs=[];save();go(()=>{U.tab='songs';U.view=null})"); pg.wait_for_timeout(250)
    ok(pg.locator('[data-a=trkNew]').count() == 0 and pg.locator('#app .sgempty [data-a=sgNew]').count() == 1,
       'the empty Songs list offers the same New song')
    pg.context.close()


SIZES = [('iphone', 390, 844), ('small', 375, 667), ('land', 852, 393), ('ipad', 820, 1180), ('mac', 1440, 900)]


def sizes(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        for name, w, h in SIZES:
            pg = t.page(b, w=w, h=h, sc=sc)
            pg.evaluate("go(()=>{U.tab='songs';U.view=split()?null:'lyr';U.songId='g_1'})"); pg.wait_for_timeout(250)
            pg.evaluate("TRACK.expect('g_1')"); pg.set_input_files('#trackIn', track()); loaded(pg)
            pg.evaluate("songById('g_1').loop={start:2,end:4,on:true};TRACK.seek(3);rerender()"); pg.wait_for_timeout(200)
            sw = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
            tr = pg.evaluate("(()=>{const r=document.querySelector('#dock .trktr').getBoundingClientRect();return r.bottom<=innerHeight&&r.top>0&&r.left>=0&&r.right<=innerWidth})()")
            ink = pg.evaluate(INK)
            ok(sw <= 1 and tr and ink > 500, f'{name} {sc}: no sideways scroll, the transport in view, the waveform drawn ({sw}, {tr}, {ink})')
            t.shot(pg, f'{name}-{sc}')
            pg.click('#app .trklv button[data-v="2"]'); pg.wait_for_timeout(150)
            ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth") <= 1, f'{name} {sc}: rows fit too')
            t.shot(pg, f'{name}-{sc}-rows', full_page=True)
            pg.click('#app .trklv button[data-v="1"]'); pg.wait_for_timeout(100)
            pg.context.close()


def run(b, t):
    importing(b, t)
    levels(b, t)
    loops(b, t)
    playing(b, t)
    windows(b, t)
    data(b, t)
    new_song(b, t)
    sizes(b, t)
