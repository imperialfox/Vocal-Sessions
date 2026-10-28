"""3.20 Render 12 · songs, takes and markers.
The + sheet (Add media or Manually), play buttons on song rows, one sound at a time through one owner, a floating
window whose ✕ always closes, the song length linked to its track, one song list from Today and the Songs tab, the
takes sheet (All takes, the scrubber, ±5 s, swipes, hold, rename, timestamped comments), keeping every take, takes and
tracks playing again after they finish, takes playing in both ears, and the track player's markers and chips.
Every fixture is synthetic: tones written by the tests as WAV files. No real music or recordings are ever used."""
import os, json, wave, struct, math
from harness import OUT, ready
from test_track import track, F, loaded, NIDB, LYRICS, tones
from test_clock import LYR, ADD, sync
from test_layout import FITS
from test_coach import add as add_video, LONG

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']
SONG = "id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})"
LIST = "go(()=>{U.tab='songs';U.view=null})"
LEAVE = "go(()=>{U.view=null;U.tab='today'})"
SHOWN = "!!FW.shown&&!document.getElementById('fw').hidden"
GONE = "(()=>{const f=document.getElementById('fw');return !FW.shown&&(!f||f.hidden)})()"


def wav_take(secs=4, ch=1, silent_right=False, rate=8000, tone=330):
    """JS that stores a playable take: a tone, mono or two-channel (optionally with the right side silent)."""
    return """async([id,sid,o,mins])=>{const secs=%s,ch=%d,sr=%d,n=sr*secs,b=new ArrayBuffer(44+n*2*ch),v=new DataView(b);
 const w=(p,s)=>[...s].forEach((c,i)=>v.setUint8(p+i,c.charCodeAt(0)));
 w(0,'RIFF');v.setUint32(4,36+n*2*ch,true);w(8,'WAVE');w(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,ch,true);
 v.setUint32(24,sr,true);v.setUint32(28,sr*2*ch,true);v.setUint16(32,2*ch,true);v.setUint16(34,16,true);w(36,'data');v.setUint32(40,n*2*ch,true);
 for(let i=0;i<n;i++){const s=Math.round(Math.sin(2*Math.PI*%d*i/sr)*6000);for(let c=0;c<ch;c++)v.setInt16(44+(i*ch+c)*2,c===1&&%s?0:s,true)}
 const bl=new Blob([b],{type:'audio/wav'});await putTake(Object.assign({id,songId:sid||'g_1',created:Date.now()-(mins||1)*6e4,len:secs,size:bl.size,type:'audio/wav',blob:bl,star:false},o?{o}:{}));
 await refreshTakes();rerender();}""" % (secs, ch, rate, tone, 'true' if silent_right else 'false')


def held(pg):
    """Hold until the menu has opened (setTimeout can fire late when many tests run side by side), then a little longer."""
    try: pg.wait_for_function("['sgTakeMenu','sgCmtMenu','trkMkMenu'].includes(U.sheet)", timeout=4000)
    except Exception: pass
    pg.wait_for_timeout(120)


def lyric_song(pg, name='Harbour'):
    sid = pg.evaluate(ADD, [name, 'Harbour Lights', LYR]); pg.wait_for_timeout(300)
    return sid


def add_track(pg, sid, f=None):
    pg.evaluate("id=>TRACK.expect(id)", sid)
    pg.set_input_files('#trackIn', f or track())
    pg.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()", arg=sid, timeout=15000)
    pg.wait_for_timeout(300)


# ---------------------------------------------------------------- 1 · the + sheet
def add_sheet(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(LIST); pg.wait_for_timeout(250)
    ok(pg.locator('[data-a=trkNew]').count() == 0 and pg.locator('#barR [data-a=sgNew]').count() == 1, 'Songs has one + (New song from track is gone)')
    pg.click('#barR [data-a=sgNew]'); pg.wait_for_timeout(300)
    on = pg.locator('.sheet .sgaddseg button.on')
    ok(on.count() == 1 and on.inner_text() == 'Add media' and 'Manually' in pg.inner_text('.sheet .sgaddseg'),
       'the + sheet opens with a two-part switch, Add media on the left and chosen')
    ok(pg.locator('.sheet .sgdrop[data-a=sgAddPick]').count() == 1 and 'Choose audio file' in pg.inner_text('.sheet'), 'with a drop area: Choose audio file')
    ok(pg.locator('#sgTitle').count() == 0, 'the form waits for a file')
    t.shot(pg, 'add-media')
    # Manually: the form as before, a Length with no link
    pg.click('.sheet [data-a=sgAddMode][data-v=manual]'); pg.wait_for_timeout(250)
    ok(pg.locator('#sgTitle').count() == 1 and pg.locator('#sgLyr').count() == 1 and pg.locator('.sheet [data-a=sgAddPick]').count() == 0,
       'Manually is the form, with no file row')
    ok(pg.locator('.sheet .lnk').count() == 0 and 'Add a track later and its length can link to it' in pg.inner_text('.sheet'),
       'its Length has no link, with the foot note')
    t.shot(pg, 'add-manual')
    pg.click('.sheet [data-a=sgAddMode][data-v=media]'); pg.wait_for_timeout(250)
    # Add media: the file is read, the form expands
    with pg.expect_file_chooser() as fc: pg.click('.sheet [data-a=sgAddPick]')
    fc.value.set_files(track())
    pg.wait_for_function("U.sDraft&&U.sDraft.media&&!TRACK.busy()", timeout=15000); pg.wait_for_timeout(250)
    ok('Paper Boats.wav added' in pg.inner_text('.sheet .sgadded'), 'a green line says the file was added')
    ok(pg.input_value('#sgTitle') == '' and pg.get_attribute('#sgTitle', 'placeholder') == 'Paper Boats' and pg.input_value('#sgArtist') == '',
       'nothing is assumed from it: Title and Artist start empty, the title’s placeholder is the file name')
    ok(pg.inner_text('.sheet .sglenv').startswith('1:00') and pg.locator('.sheet .sglenv .lnk.on').count() == 1,
       'Length is the file’s duration, with the link icon')
    ok(pg.evaluate(NIDB) == [0, 0], 'nothing is in vocalTracks until Save')
    ok(pg.locator('.sheet [data-a=sgSplit]').inner_text() == 'Save song', 'with no lyrics the button saves straight away')
    pg.fill('#sgLyr', '[Verse]\nA line'); pg.wait_for_timeout(100)
    ok(pg.locator('.sheet [data-a=sgSplit]').inner_text() == 'Next', 'typing lyrics turns it into Next')
    pg.fill('#sgLyr', ''); pg.wait_for_timeout(100)
    t.shot(pg, 'add-media-file')
    # swap the file
    with pg.expect_file_chooser() as fc: pg.click('.sheet .sgswap')
    fc.value.set_files(F('Paper Boats long.wav', 63))
    pg.wait_for_function("U.sDraft&&U.sDraft.media&&U.sDraft.media.name==='Paper Boats long.wav'", timeout=15000); pg.wait_for_timeout(250)
    ok(pg.inner_text('.sheet .sglenv').startswith('1:03') and pg.evaluate(NIDB) == [0, 0], 'Choose a different file swaps it, still nothing stored')
    # cancelling keeps nothing
    pg.click('.sheet .xbtn'); pg.wait_for_timeout(300)
    ok(pg.evaluate(NIDB) == [0, 0] and pg.evaluate("D.songs.length") == 1, 'closing the sheet leaves nothing behind')
    # a bad file says so
    bad = os.path.join(OUT, 'not-audio.mp3'); open(bad, 'wb').write(b'not audio at all' * 50)
    pg.click('#barR [data-a=sgNew]'); pg.wait_for_timeout(250)
    with pg.expect_file_chooser() as fc: pg.click('.sheet [data-a=sgAddPick]')
    fc.value.set_files(bad); pg.wait_for_function("!TRACK.busy()", timeout=10000); pg.wait_for_timeout(300)
    ok('can’t be opened' in pg.inner_text('.toast') and not pg.evaluate("U.sDraft.media"), 'a file that can’t be opened says so')
    # Save with a blank title: the file's name, the track attached, the length linked, landing on the song page
    with pg.expect_file_chooser() as fc: pg.click('.sheet [data-a=sgAddPick]')
    fc.value.set_files(track())
    pg.wait_for_function("U.sDraft&&U.sDraft.media", timeout=15000); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=sgSplit]')
    pg.wait_for_function("U.view==='lyr'&&!U.sheet", timeout=10000); pg.wait_for_timeout(300)
    sg = pg.evaluate("songById(U.songId)")
    ok(sg['name'] == 'Paper Boats' and sg['track']['name'] == 'Paper Boats.wav', f'a blank title uses the file name, and the track is attached: {sg["name"]}')
    ok(sg['timing']['len'] == 60 and sg['timing'].get('lenLink') is True, 'the song’s length is the track’s, linked')
    ok(pg.evaluate("TRACK.has(U.songId)") and pg.evaluate(NIDB) == [1, 1], 'the audio and peaks are stored on Save')
    ok('No lyrics yet' in pg.inner_text('#app') and pg.locator('#app [data-a=trkOpen]').count() == 1, 'Save lands on the song page (lyrics can be pasted later)')
    ok(pg.locator('#app .sgart .lnk.on').count() == 1, 'and its length shows the link icon')
    # a custom length in the sheet: unlink first, then the picker
    pg.evaluate(LIST); pg.wait_for_timeout(200)
    pg.click('#barR [data-a=sgNew]'); pg.wait_for_timeout(250)
    with pg.expect_file_chooser() as fc: pg.click('.sheet [data-a=sgAddPick]')
    fc.value.set_files(track())
    pg.wait_for_function("U.sDraft&&U.sDraft.media", timeout=15000); pg.wait_for_timeout(250)
    pg.fill('#sgTitle', 'Custom length'); pg.fill('#sgArtist', 'Someone')
    pg.click('.sheet [data-a=sgAddLen]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgLenUnlink' and 'Unlink from track?' in pg.inner_text('.sheet')
       and 'stop matching the uploaded audio' in pg.inner_text('.sheet') and pg.locator('.sheet .cta.red').inner_text() == 'Unlink',
       'tapping a linked length asks “Unlink from track?” (Unlink in red)')
    pg.click('.sheet [data-a=sgLenUnlinkYes]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.sheet") == 'sgNew' and pg.locator('#ckpk').count() == 1, 'Unlink goes back to the sheet with the length picker open')
    ok(pg.input_value('#sgTitle') == 'Custom length' and pg.input_value('#sgArtist') == 'Someone', 'what was typed is kept')
    pg.evaluate("CK.pk.vals.m=3;CK.pk.vals.s=30"); pg.click('#ckpk [data-a=ckPickSet]'); pg.wait_for_timeout(300)
    ok(pg.inner_text('.sheet .sglenv').startswith('3:30') and pg.locator('.sheet .lnk.off').count() == 1 and 'Custom · track is 1:00' in pg.inner_text('.sheet'),
       'a custom length shows the broken link and the track’s length')
    pg.click('.sheet [data-a=sgSplit]'); pg.wait_for_function("U.view==='lyr'&&!U.sheet", timeout=10000); pg.wait_for_timeout(300)
    tm = pg.evaluate("songById(U.songId).timing")
    ok(tm['len'] == 210 and not tm.get('lenLink'), 'saved with its own length, unlinked')
    # Manually is unchanged: no track
    pg.evaluate(LIST); pg.wait_for_timeout(200)
    pg.click('#barR [data-a=sgNew]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=sgAddMode][data-v=manual]'); pg.wait_for_timeout(200)
    pg.fill('#sgTitle', 'by hand'); pg.fill('#sgLyr', LYRICS); pg.click('.sheet [data-a=sgSplit]'); pg.wait_for_timeout(300)
    ok(pg.locator('.sheet .blk').count() == 2, 'Manually still goes on to label the sections')
    pg.click('.sheet [data-a=sgSave]'); pg.wait_for_function("U.view==='lyr'&&!U.sheet", timeout=10000); pg.wait_for_timeout(300)
    sg = pg.evaluate("songById(U.songId)")
    ok(sg['name'] == 'By Hand' and 'track' not in sg and 'timing' not in sg, 'and saves a song with no track or length')
    ok(pg.evaluate(NIDB) == [2, 2], 'only the two songs added from media have tracks')
    pg.context.close()


# ---------------------------------------------------------------- 2 · play buttons on song rows
def rows(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    pg.evaluate(LIST); pg.wait_for_timeout(250)
    btn = pg.locator(f'#app [data-a=sgRowPlay][data-k="{sid}"]')
    ok(btn.count() == 1 and btn.get_attribute('aria-disabled') == 'true' and 'off' in btn.get_attribute('class'),
       'every song row has a play button, greyed (aria-disabled) with no track on this device')
    ok(pg.evaluate(f"(()=>{{const r=document.querySelector('#app [data-fk=\"sg:{sid}\"] .rowc').getBoundingClientRect(),p=document.querySelector('#app [data-a=sgRowPlay][data-k=\"{sid}\"]').getBoundingClientRect();return p.right<=r.right&&p.left>r.left+r.width/2&&Math.abs((p.top+p.bottom)/2-(r.top+r.bottom)/2)<6}})()"),
       'on the right, in line with the name')
    btn.click(force=True); pg.wait_for_timeout(150)  # aria-disabled, so Playwright needs force
    ok(pg.inner_text('.toast') == 'Upload a track to play' and pg.evaluate("U.view") is None, 'still tappable: it says “Upload a track to play” and stays on the list')
    pg.wait_for_timeout(1200)
    ok(pg.locator('.toast').count() == 0, 'for about a second')
    rm = pg.inner_text(f'#app [data-fk="sg:{sid}"] .rmeta')
    ok('Not practised yet' in rm, 'a row says “Not practised yet” with no takes: ' + rm)
    add_track(pg, sid); pg.evaluate(LIST); pg.wait_for_timeout(300)
    btn = pg.locator(f'#app [data-a=sgRowPlay][data-k="{sid}"]')
    ok(btn.get_attribute('aria-disabled') is None, 'with a track it’s ready')
    btn.click(); pg.wait_for_function("TRACK.state().playing", timeout=8000); pg.wait_for_timeout(300)
    ok(pg.evaluate("TRACK.state().id") == sid and pg.evaluate("U.view") is None, 'it plays the song’s track from the list')
    ok('on' in btn.get_attribute('class') and btn.get_attribute('aria-label').startswith('Pause'), 'the row’s button shows pause while it plays')
    ok(pg.evaluate("FW.shown") == 'track' and pg.evaluate(SHOWN), 'and the floating window shows, since its player isn’t on screen')
    sp = pg.evaluate("TRACK.speed()")
    ok(pg.evaluate("TRACK.el().preservesPitch") is True and pg.evaluate("TRACK.el().playbackRate") == sp, 'through the track player’s audio, pitch kept, at the remembered speed')
    btn.click(); pg.wait_for_timeout(250)
    ok(not pg.evaluate("TRACK.state().playing") and 'on' not in btn.get_attribute('class'), 'tapping it again pauses')
    ok(pg.evaluate(GONE), 'paused from the row (not the window), no window stays')
    # Today's pinned rows have one too
    pg.evaluate(f"(()=>{{songById('{sid}').pinned=true;save();go(()=>{{U.tab='today';U.view=null}})}})()"); pg.wait_for_timeout(300)
    ok(pg.locator(f'#app .sgtprow [data-a=sgRowPlay][data-k="{sid}"]').count() == 1, 'Today’s pinned songs have the play button too')
    pg.click(f'#app .sgtprow [data-a=sgRowPlay][data-k="{sid}"]'); pg.wait_for_function("TRACK.state().playing", timeout=5000); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'today' and pg.evaluate("FW.shown") == 'track', 'it plays there without leaving Today')
    pg.click(f'#app .sgtprow [data-a=sgRowPlay][data-k="{sid}"]'); pg.wait_for_timeout(200)
    # a take: the row says so
    pg.evaluate(wav_take(), ['tk1', sid, None, 1]); pg.evaluate(LIST); pg.wait_for_timeout(300)
    rm = pg.inner_text(f'#app [data-fk="sg:{sid}"] .rmeta')
    ok('Practised today' in rm and '1 take' in rm, 'with a take: “Practised today · 1 take”: ' + rm)
    pg.context.close()


# ---------------------------------------------------------------- 3 · one sound at a time, ✕ always closes
def sounds(pg):
    """Start each kind of sound. Returns {kind: js that starts it}."""
    return {
        'take': "playTake('w1')",
        'track': "TRACK.play()",
        'video': "COACH.play()",
        'clock': "(()=>{const s=songById(window.__ck);if(!CK.on||CK.songId!==s.id)ckOn(s);ckPlay(0)})()",
    }
PLAYING = {
    'take': "!!player&&!player.paused&&playingId==='w1'",
    # Q02: play-along of a song with its track plays that track under Song Clock (along); that's the clock's sound
    'track': "TRACK.state().playing&&!TRACK.state().along",
    'video': "!COACH.el().paused",
    'clock': "CLOCK.state().run",
}


def setup_sounds(b, t):
    pg = t.page(b, ctx_args={'permissions': ['microphone']})
    pg.evaluate("CLOCK.fake(50000)")
    sid = lyric_song(pg)
    sync(pg)
    pg.evaluate("id=>{window.__ck=id}", sid)
    pg.evaluate(wav_take(30), ['w1', sid, None, 1])
    add_track(pg, sid)
    pg.evaluate(SONG, sid); pg.wait_for_timeout(200)
    pg.evaluate("go(()=>{U.tab='songs';U.view='trk';U.songId=window.__ck})"); loaded(pg, sid)
    add_video(pg, LONG)
    pg.evaluate(LEAVE); pg.wait_for_timeout(300)
    return pg, sid


def one_sound(b, t):
    ok = t.ok
    pg, sid = setup_sounds(b, t)
    S = sounds(pg)
    kinds = list(S)
    for a in kinds:
        for c in kinds:
            if a == c: continue
            pg.evaluate(S[a]); pg.wait_for_function(PLAYING[a], timeout=8000); pg.wait_for_timeout(150)
            pg.evaluate(S[c]); pg.wait_for_function(PLAYING[c], timeout=8000); pg.wait_for_timeout(250)
            still = [k for k in kinds if pg.evaluate(PLAYING[k])]
            ok(still == [c] and pg.evaluate("NOW.kind()") == c, f'{a} then {c}: only {c} plays ({still})')
            ok(pg.evaluate("NOW.last()") == c, f'the lock screen follows {c}')
    pg.evaluate("NOW.stop()"); pg.wait_for_timeout(200)
    ok(not any(pg.evaluate(PLAYING[k]) for k in kinds), 'NOW.stop() stops whatever plays')
    # recording stops every sound
    pg.evaluate(S['track']); pg.wait_for_function(PLAYING['track'], timeout=5000)
    pg.evaluate(SONG, sid); pg.wait_for_timeout(200)
    o = pg.evaluate("id=>songById(id).order[0].o", sid)
    pg.evaluate("o=>{U.sSec=o;rerender()}", o); pg.wait_for_timeout(150)
    pg.click(f'.sgsec[data-o="{o}"] [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1200)
    ok(not pg.evaluate(PLAYING['track']) and pg.evaluate("NOW.kind()") == 'rec', 'a recording stops the track')
    pg.click('[data-a=sgStop]'); pg.wait_for_function("!rec&&U.sheet==='sgTakes'", timeout=5000); pg.wait_for_timeout(300)
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    o = pg.evaluate("id=>songById(id).order[1].o", sid)
    for k in kinds:
        pg.evaluate(S[k]); pg.wait_for_function(PLAYING[k], timeout=8000); pg.wait_for_timeout(150)
        pg.evaluate("([id,o])=>startRec({songId:id,o})", [sid, o]); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(250)
        ok(not pg.evaluate(PLAYING[k]), f'recording stops the {k}')
        pg.evaluate("stopRec()"); pg.wait_for_function("!rec", timeout=5000); pg.wait_for_timeout(400)
        pg.evaluate("U.sheet=null;U.sd={};rerender()"); pg.wait_for_timeout(150)
    pg.context.close()


def x_closes(b, t):
    ok = t.ok
    pg, sid = setup_sounds(b, t)
    S = sounds(pg)
    pg.evaluate("newSession();rerender()")  # a session waiting underneath, to check nothing pops up in the window's place
    for k in S:
        for paused in (False, True):
            pg.evaluate(S[k]); pg.wait_for_function(PLAYING[k], timeout=8000); pg.wait_for_timeout(150)
            pg.evaluate("go(()=>{U.view=null;U.tab='history'})"); pg.wait_for_timeout(300)
            if paused:
                pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(250)
            ok(pg.evaluate("FW.shown") == k and pg.locator('#fw [data-a=fwX]').is_visible(),
               f'{k} {"paused" if paused else "playing"}: its window has a ✕')
            pg.click('#fw [data-a=fwX]'); pg.wait_for_timeout(600)
            ok(pg.evaluate(GONE) and not pg.evaluate(PLAYING[k]), f'{k}: ✕ stops it and closes the window')
            ok(pg.evaluate("FW.shown") != 'session', f'{k}: the waiting session doesn’t pop up in its place')
            # nothing brings it back but an explicit play
            pg.evaluate("rerender();fwUpdate()"); pg.wait_for_timeout(150)
            pg.evaluate("U.sheet='storage';rerender()"); pg.wait_for_timeout(200); pg.evaluate("closeSheet()"); pg.wait_for_timeout(250)
            pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(200)
            ok(pg.evaluate("FW.shown") != k, f'{k}: a redraw, a sheet and the app coming back don’t bring it back')
            pg.evaluate("go(()=>{U.view=null;U.tab='exercises'})"); pg.wait_for_timeout(300)
            ok(pg.evaluate("FW.shown") == 'session', f'{k}: a tab switch doesn’t bring it back (the session shows on the next screen)')
            if k == 'video':
                pg.evaluate("COACH.el().dispatchEvent(new Event('play'))"); pg.wait_for_timeout(200)
                ok(pg.evaluate("FW.shown") != 'video', 'a stray play event doesn’t bring the video back')
    # an explicit play brings it back
    pg.evaluate(S['track']); pg.wait_for_function(PLAYING['track'], timeout=5000); pg.wait_for_timeout(250)
    ok(pg.evaluate("FW.shown") == 'track', 'an explicit play brings its window back')
    # a reload: nothing comes back
    pg.click('#fw [data-a=fwX]'); pg.wait_for_timeout(400)
    pg.reload(); ready(pg); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") in (None, 'session'), 'after a reload, no sound’s window comes back')
    pg.evaluate("X=null;saveDraft();rerender()")
    # pausing a sound on its own screen, then leaving: no window
    pg.evaluate("go(()=>{U.tab='songs';U.view='trk';U.songId=window.__ck||songById(D.songs.find(s=>s.track).id).id})")
    sid2 = pg.evaluate("D.songs.find(s=>s.track).id"); pg.evaluate("id=>go(()=>{U.tab='songs';U.view='trk';U.songId=id})", sid2); loaded(pg, sid2)
    pg.evaluate("TRACK.play()"); pg.wait_for_function("TRACK.state().playing", timeout=5000)
    pg.evaluate("TRACK.pause()"); pg.wait_for_timeout(150)
    pg.evaluate(LEAVE); pg.wait_for_timeout(300)
    ok(pg.evaluate(GONE), 'pausing a sound on its own screen and leaving shows no window')
    # a sound that finishes takes its window with it
    pg.evaluate(wav_take(2), ['short', sid2, None, 1])
    pg.evaluate(SONG, sid2); pg.wait_for_timeout(200)
    pg.evaluate("playTake('short')"); pg.wait_for_function("!!player&&!player.paused", timeout=5000)
    pg.evaluate(LEAVE); pg.wait_for_timeout(250); ok(pg.evaluate("FW.shown") == 'take', 'a short take shows its window elsewhere')
    pg.wait_for_function("!player", timeout=5000); pg.wait_for_timeout(500)
    ok(pg.evaluate(GONE), 'when it finishes, its window leaves')
    pg.context.close()


# ---------------------------------------------------------------- 4 · song length linked to the track
def length(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    add_track(pg, sid)
    pg.evaluate(SONG, sid); pg.wait_for_timeout(300)
    tm = pg.evaluate("id=>songById(id).timing", sid)
    ok(tm['len'] == 60 and tm['lenLink'] is True, 'adding a track sets the length to the track’s, linked')
    ok(pg.locator('#app .ckrow .cklen .lnk.on').count() == 1 and pg.inner_text('#app .cklen').startswith('1:00'), 'the header shows 1:00 with the link icon')
    pg.click('#app .cklen'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgLenUnlink' and pg.locator('#ckpk').count() == 0, 'tapping it asks “Unlink from track?” before any picker')
    pg.click('.sheet [data-a=close].ghost'); pg.wait_for_timeout(250)
    ok(pg.evaluate("id=>songById(id).timing.lenLink", sid) is True, 'Cancel keeps it linked')
    pg.click('#app .cklen'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=sgLenUnlinkYes]'); pg.wait_for_timeout(400)
    ok(pg.locator('#ckpk').count() == 1 and not pg.evaluate("id=>!!songById(id).timing.lenLink", sid), 'Unlink, then the picker opens')
    pg.evaluate("CK.pk.vals.m=3;CK.pk.vals.s=30"); pg.click('#ckpk [data-a=ckPickSet]'); pg.wait_for_timeout(300)
    ok(pg.locator('#app .ckrow [data-a=ckRelink].lnk.off').count() == 1 and 'Custom · track is 1:00' in pg.inner_text('#app'),
       'a custom length shows the broken link and “Custom · track is 1:00”')
    t.shot(pg, 'length-custom')
    pg.click('#app [data-a=ckRelink]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgLenRelink' and 'Your custom length 3:30 will be replaced with 1:00' in pg.inner_text('.sheet'),
       'relinking a different length asks first')
    pg.click('.sheet [data-a=sgLenRelinkYes]'); pg.wait_for_timeout(300)
    tm = pg.evaluate("id=>songById(id).timing", sid)
    ok(tm['len'] == 60 and tm['lenLink'] is True and 'Relinked to track' in pg.inner_text('.toast'), 'Relink puts it back, with a toast')
    # equal lengths relink straight away
    pg.evaluate("id=>{delete songById(id).timing.lenLink;save();rerender()}", sid); pg.wait_for_timeout(200)
    pg.click('#app [data-a=ckRelink]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("id=>songById(id).timing.lenLink", sid) is True, 'with the same length it relinks without asking')
    # replace follows when linked; stays when not
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='trk';U.songId=id})", sid); loaded(pg, sid)
    add_track(pg, sid, F('Paper Boats long.wav', 63)); pg.wait_for_timeout(300)
    ok(pg.evaluate("id=>[songById(id).timing.len,songById(id).timing.lenLink]", sid) == [63, True], 'replacing the track: a linked length follows it')
    pg.evaluate("id=>{const t=songById(id).timing;t.len=200;delete t.lenLink;save()}", sid)
    add_track(pg, sid); pg.wait_for_timeout(300)
    ok(pg.evaluate("id=>[songById(id).timing.len,!!songById(id).timing.lenLink]", sid) == [200, False], 'an unlinked length stays')
    # a song that already has a different length keeps it, unlinked
    s2 = lyric_song(pg, 'Second')
    pg.evaluate("id=>{const s=songById(id);s.timing=s.timing||{len:null,real:false,est:false,slots:{}};s.timing.len=95;save()}", s2)
    add_track(pg, s2); pg.wait_for_timeout(300)
    ok(pg.evaluate("id=>[songById(id).timing.len,!!songById(id).timing.lenLink]", s2) == [95, False], 'a song with a different length keeps it, shown unlinked')
    # remove track: unlinked, length kept
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='trk';U.songId=id})", sid); loaded(pg, sid)
    pg.evaluate("id=>{const t=songById(id).timing;t.len=60;t.lenLink=true;save()}", sid)
    pg.click('#barR [data-a=trkMenu]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=sheet][data-v=trkDel]'); pg.wait_for_timeout(250); pg.click('.sheet [data-a=trkRemove]'); pg.wait_for_timeout(500)
    ok(pg.evaluate("id=>[songById(id).timing.len,!!songById(id).timing.lenLink]", sid) == [60, False], 'Remove track unlinks it and keeps the length')
    ok(pg.locator('#app .lnk').count() == 0, 'with no track, no icon')
    # cleanTiming checks lenLink
    r = pg.evaluate("[cleanTiming({len:200,lenLink:'yes'},{order:[]}),cleanTiming({len:200,lenLink:true},{order:[]}),cleanTiming({len:null,lenLink:true,slots:{}},{order:[]})]")
    ok('lenLink' not in r[0] and r[1]['lenLink'] is True and r[2] is None, 'cleanTiming keeps lenLink only when it’s true and there’s a length')
    pg.context.close()


# ---------------------------------------------------------------- 5 · one song list, two doors
def one_list(b, t):
    ok = t.ok
    from harness import with_song_practice
    d = with_song_practice()
    d['songs'].append({'id': 'g_2', 'name': 'Second song', 'added': 1})
    pg = t.page(b, data=d, ctx_args={'permissions': ['microphone']})
    pg.evaluate(wav_take(), ['old', 'g_1', None, 3000]); pg.wait_for_timeout(200)
    before = pg.evaluate("[D.songSessions.length,TAKES.length]")
    pg.click('[data-a=songStart]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.tab") == 'songs' and pg.evaluate("U.view") is None and pg.locator('.zm').count() == 0,
       'Today’s Song practice card switches to the Songs tab (no zoom)')
    ok(pg.locator('#dock .tabbar button.on[data-v=songs]').count() == 1, 'with Songs highlighted in the tab bar')
    ok(pg.evaluate("[D.songSessions.length,TAKES.length]") == before, 'practice records and takes are untouched')
    # recent first
    order = pg.evaluate("[...document.querySelectorAll('#app .srow')].map(r=>r.dataset.fk)")
    ok(order[0] == 'sg:g_1', f'recent first: the practised song is on top ({order})')
    # practice records still open from their song, Progress and the calendar
    pg.evaluate("go(()=>{U.tab='history';U.view='all';U.histTab='songs'})"); pg.wait_for_timeout(300)
    pg.click('[data-v=songSession] >> nth=0'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'songSession', 'All sessions › Song practice still opens each one')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId='g_1'})"); pg.wait_for_timeout(300)
    ok(pg.locator('#app [data-a=sgPractise]').count() == 1, 'a song’s Song practice row is still there')
    # recording on a song page starts song practice for that song
    sid = lyric_song(pg)
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); pg.wait_for_timeout(200)
    pg.click(f'#app [data-fk="sg:{sid}"] .rowc'); pg.wait_for_timeout(300)
    o = pg.evaluate("id=>songById(id).order[0].o", sid)
    pg.evaluate("o=>{U.sSec=o;rerender()}", o); pg.wait_for_timeout(150)
    ok(pg.evaluate("X") is None, 'no song practice before a take')
    pg.click(f'.sgsec[data-o="{o}"] [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1200)
    st = pg.evaluate("[X&&X.kind,X&&X.song,X&&X.start,rec.started]")
    ok(st[0] == 'song' and st[1] == sid and st[2] == st[3], 'a take on a song page from the Songs tab starts song practice, timed from it')
    pg.click('[data-a=sgStop]'); pg.wait_for_function("!rec&&U.sheet==='sgTakes'", timeout=5000); pg.wait_for_timeout(300)
    ok(pg.evaluate("X.takes.length") == 1, 'and the take belongs to it')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    ok(not pg.evaluate(SHOWN), 'on its own song page, the session window doesn’t cover it')
    pg.evaluate(LEAVE); pg.wait_for_timeout(300)
    ok(pg.evaluate("FW.shown") == 'session', 'elsewhere, song practice has its window')
    pg.click('[data-a=songStart]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.songId") == sid, 'in progress, Today’s card carries on from that song’s page')
    pg.context.close()


# ---------------------------------------------------------------- 6–8 · the takes sheet, rename, comments
def takes(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=844)
    sid = lyric_song(pg)
    o = pg.evaluate("id=>songById(id).order.map(x=>x.o)", sid)
    for i, (oo, m) in enumerate([(o[0], 50), (o[1], 40), (o[1], 30), (None, 20), (o[0], 10)]):
        pg.evaluate(wav_take(6), ['k%d' % i, sid, oo, m])
    pg.evaluate(SONG, sid); pg.wait_for_timeout(300)
    hb = pg.locator('#app .sgtkb')
    ok(hb.count() == 1 and hb.inner_text().strip() == 'Takes · 5', 'a Takes button sits beside the title, with the count')
    ok(pg.evaluate("(()=>{const h=document.querySelector('#app .sgtrow h1').getBoundingClientRect(),b=document.querySelector('#app .sgtkb').getBoundingClientRect();return b.left>=h.right-1&&Math.abs((b.top+b.bottom)/2-(h.top+h.bottom)/2)<14})()"),
       'beside the title, on its line')
    hb.click(); pg.wait_for_timeout(300)
    heads = pg.evaluate("[...document.querySelectorAll('.sheet .tkfh')].map(b=>b.querySelector('.lbl').textContent+' · '+b.querySelector('.mut').textContent)")
    ok(pg.evaluate("U.sheet") == 'sgTakes' and pg.locator('.sheet .tkseg').count() == 0 and pg.locator('.sheet .tkr').count() == 0
       and heads == ['Verse 1 · 2 takes', 'Chorus 1 · 2 takes', 'Other takes · 1 take'],
       f'it opens the takes sheet on All takes, a folded row per section (Q10): {heads}')
    pg.evaluate("""[...document.querySelectorAll('.sheet .tkfh[aria-expanded=false]')].map(b=>b.dataset.v).forEach(v=>SG_ACT.tkFold(document.querySelector('.sheet .tkfh[data-v=\"'+v+'\"]'),v))"""); pg.wait_for_timeout(200)
    names = pg.evaluate("[...document.querySelectorAll('.sheet .tkr .tktx b')].map(b=>b.textContent)")
    ok(len(names) == 5 and names[0].startswith('Take 5') and names[1].startswith('Take 1') and names[-1].startswith('Take 4'),
       f'sections in song order, newest first inside each, numbered: {names}')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    # from a section: the switch
    pg.evaluate("o=>{U.sSec=o;rerender()}", o[1]); pg.wait_for_timeout(200)
    pg.click(f'.sgsec[data-o="{o[1]}"] [data-a=sgTakes]'); pg.wait_for_timeout(300)
    seg = pg.inner_text('.sheet .tkseg')
    ok('Chorus 1 · 2' in seg and 'All takes · 5' in seg and pg.locator('.sheet .tkseg button.on').inner_text().startswith('Chorus'),
       'from a section, the switch reads “Chorus 1 · 2 | All takes · 5” and opens on the section: ' + seg.replace('\n', ' | '))
    ok(pg.locator('.sheet .tkr').count() == 2, 'with that section’s takes')
    pg.click('.sheet [data-a=tkTab][data-v=all]'); pg.wait_for_timeout(250)
    ok(pg.locator('.sheet .tkfh').count() == 3 and pg.locator('.sheet .tkr').count() == 2 and pg.locator('.sheet .tkseg').count() == 1,
       'All takes switches in place, with the section it came from folded open')
    pg.click('.sheet [data-a=tkTab][data-v=sec]'); pg.wait_for_timeout(250)
    # tap a row: it expands and plays
    pg.click('.sheet .tkr >> nth=0 >> .tkhead .tktx'); pg.wait_for_function("!!player&&!player.paused", timeout=5000); pg.wait_for_timeout(300)
    ok(pg.locator('.sheet .tkr.open').count() == 1 and pg.evaluate("playingId") == 'k2', 'tapping a row expands it (one at a time) and plays it')
    ok(pg.locator('.sheet .tkr.open #tkWave canvas').count() == 1 and pg.locator('.sheet .tkr.open [data-a=tkSkip]').count() == 2
       and pg.locator('.sheet .tkr.open #tkCIn').count() == 1, 'expanded: a waveform scrubber, −5 s and +5 s, and the comment field')
    ok(pg.get_attribute('.sheet #tkWave', 'data-own-gesture') is not None, 'the scrubber has its own gesture')
    pg.wait_for_timeout(500)
    ink = pg.evaluate("(()=>{const c=document.getElementById('tkC');const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i])n++;return n})()")
    ok(ink > 500, 'the waveform is drawn on a canvas')
    ok(pg.evaluate("TAKE.ext('k2')") and pg.evaluate("TAKE.ext('k2').n") > 200, 'peaks are worked out once and kept on the device')
    # second row: only one expanded
    pg.click('.sheet .tkr:not(.open) .tktx'); pg.wait_for_timeout(300)
    ok(pg.locator('.sheet .tkr.open').count() == 1 and pg.evaluate("playingId") == 'k1', 'another row: it expands in place of the first and plays')
    pg.click('.sheet #tkPP'); pg.wait_for_timeout(200)
    ok(pg.evaluate("player.paused"), 'its play button pauses')
    # scrub follows the finger
    r = pg.evaluate("(()=>{const r=document.getElementById('tkWave').getBoundingClientRect();return [r.left,r.top+r.height/2,r.width]})()")
    pg.mouse.move(r[0] + r[2] * 0.1, r[1]); pg.mouse.down(); pg.mouse.move(r[0] + r[2] * 0.5, r[1], steps=6)
    mid = pg.evaluate("TAKE.now('k1')")
    pg.mouse.up(); pg.wait_for_timeout(150)
    ok(abs(mid - 3) < 0.4, f'dragging the waveform scrubs, following the finger ({mid:.2f} s at the middle of 6 s)')
    pg.click('.sheet [data-a=tkSkip][data-v="5"]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("TAKE.now('k1')") - 5.95) < 0.1, '+5 s clamps at the end')
    pg.click('.sheet [data-a=tkSkip][data-v="-5"]'); pg.click('.sheet [data-a=tkSkip][data-v="-5"]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("TAKE.now('k1')") == 0, '−5 s clamps at the start')
    ok(pg.inner_text('#tkEl') == '0:00' and pg.inner_text('#tkRm') == '−0:06', 'elapsed and −remaining times')
    # rename
    pg.click('.sheet [data-a=tkRename]'); pg.wait_for_timeout(250)
    ok(pg.locator('#tkNameIn').count() == 1 and pg.evaluate("document.activeElement.id") == 'tkNameIn', 'tapping the name gives an inline field')
    pg.fill('#tkNameIn', 'Best so far'); pg.press('#tkNameIn', 'Enter'); pg.wait_for_timeout(250)
    ok(pg.evaluate("id=>songById(id).takeNotes.k1.name", sid) == 'Best so far' and pg.evaluate("TAKES.find(t=>t.id==='k1').o") == o[1],
       'Enter saves it as a separate label; the take’s place is unchanged')
    ok('Take 2 · Chorus 1' in pg.inner_text('.sheet .tkr.open .tkname'), 'the renamed take shows its original details underneath')
    pg.click('.sheet [data-a=tkRename]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=tkNameClear]'); pg.click('.sheet [data-a=tkNameDone]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("id=>!(songById(id).takeNotes&&songById(id).takeNotes.k1)", sid) and pg.evaluate("TAKE.nameOf('k1')") == 'Take 2 · Chorus 1',
       'an empty name restores the default')
    pg.click('.sheet [data-a=tkRename]'); pg.wait_for_timeout(200); pg.fill('#tkNameIn', 'Keeper'); pg.press('#tkNameIn', 'Enter'); pg.wait_for_timeout(200)
    # comments: the time locks on the first character
    pg.evaluate("TAKE.seekTo('k1',2.4)")
    pg.click('#tkCIn'); pg.keyboard.type('F'); pg.wait_for_timeout(100)
    ok(pg.evaluate("TAKE.state().draft.t") == 2.4 and pg.inner_text('#tkStamp') == 'at 0:02' and pg.is_visible('#tkHint'),
       'typing the first character locks the playhead time, with the chip and its hint')
    pg.evaluate("TAKE.seekTo('k1',4)"); pg.keyboard.type('lat on the high note'); pg.wait_for_timeout(100)
    ok(pg.evaluate("TAKE.state().draft.t") == 2.4, 'the time stays locked while typing')
    pg.click('#tkStamp'); pg.wait_for_timeout(100)
    ok(pg.is_visible('#tkNudge'), 'tapping the chip shows −1 s · +1 s · Use current time')
    pg.click('.sheet [data-a=tkNudge][data-v="1"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("TAKE.state().draft.t") == 3.4, '+1 s nudges it')
    pg.click('.sheet [data-a=tkNudge][data-v=now]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("TAKE.state().draft.t") == 4, 'Use current time takes the playhead')
    pg.press('#tkCIn', 'Enter'); pg.wait_for_timeout(300)
    cm = pg.evaluate("id=>songById(id).takeNotes.k1.comments", sid)
    ok(cm == [{'t': 4, 'text': 'Flat on the high note'}], f'Enter posts it to the take: {cm}')
    pg.click('#tkCIn'); pg.keyboard.type('x'); pg.fill('#tkCIn', ''); pg.dispatch_event('#tkCIn', 'input'); pg.wait_for_timeout(100)
    ok(pg.evaluate("TAKE.state().draft.t") is None and not pg.is_visible('#tkStamp'), 'clearing the field lets go of the time')
    pg.evaluate("TAKE.seekTo('k1',1)"); pg.click('#tkCIn'); pg.keyboard.type('Breath here'); pg.click('.sheet [data-a=tkPost]'); pg.wait_for_timeout(300)
    cm = pg.evaluate("id=>songById(id).takeNotes.k1.comments.map(c=>c.t)", sid)
    ok(cm == [1, 4], 'comments are sorted by time')
    ok(pg.locator('.sheet .tkdots .tkdot').count() == 2 and pg.locator('.sheet .tkcl .tkcm').count() == 2, 'dots under the waveform and a list')
    # pop-ups while playing, not on a jump
    pg.evaluate("TAKE.seekTo('k1',0.3)"); pg.click('.sheet #tkPP')
    pg.wait_for_function("TAKE.state().pop.includes('Breath here')", timeout=4000)
    ok(True, 'while playing, a comment pops up above the waveform as the playhead passes it')
    pg.click('.sheet #tkPP'); pg.wait_for_timeout(2200)
    pg.evaluate("TAKE.seekTo('k1',4.6)"); pg.wait_for_timeout(100)
    ok(pg.evaluate("TAKE.state().pop") == '', 'jumping past a comment doesn’t pop it up')
    pg.click('.sheet .tkdots .tkdot >> nth=1'); pg.wait_for_timeout(150)
    ok(pg.evaluate("TAKE.now('k1')") == 4 and 'Flat on the high note' in pg.evaluate("TAKE.state().pop"), 'tapping a dot jumps there and shows it')
    # hold a comment: Edit · Delete
    box = pg.locator('.sheet .tkcm >> nth=0').bounding_box()
    pg.mouse.move(box['x'] + 20, box['y'] + 10); pg.mouse.down(); held(pg); pg.mouse.up(); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sheet") == 'sgCmtMenu', 'holding a comment offers Edit and Delete')
    pg.click('.sheet [data-a=tkCEdit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakes' and pg.locator('#tkCIn').count() == 1 and pg.input_value('#tkCIn') == 'Breath here', 'Edit puts it back in the field: ' + str(pg.evaluate("[U.sheet,JSON.stringify(U.sd),TAKE.state()]")))
    pg.fill('#tkCIn', 'Breathe before this'); pg.dispatch_event('#tkCIn', 'input'); pg.click('.sheet [data-a=tkPost]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("id=>songById(id).takeNotes.k1.comments[0]", sid) == {'t': 1, 'text': 'Breathe before this'}, 'and saves it in place')
    box = pg.locator('.sheet .tkcm >> nth=0').bounding_box()
    pg.mouse.move(box['x'] + 20, box['y'] + 10); pg.mouse.down(); held(pg); pg.mouse.up(); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=tkCDel]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("id=>songById(id).takeNotes.k1.comments.length", sid) == 1, 'Delete removes it')
    t.shot(pg, 'takes-open')
    # collapse: doesn't stop a playing take
    pg.click('.sheet #tkPP'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=tkCollapse]'); pg.wait_for_timeout(250)
    ok(pg.locator('.sheet .tkr.open').count() == 0 and pg.evaluate("!!player&&!player.paused"), 'collapsing doesn’t stop it')
    pg.evaluate("stopPlayback();rerender()"); pg.wait_for_timeout(150)
    ok(pg.locator('.sheet .tkr[data-tk=k1] .tkcmn').count() == 1 and pg.inner_text('.sheet .tkr[data-tk=k1] .tktx b') == 'Keeper',
       'a collapsed row shows its name and a comment icon with the count')
    # swipes: right stars, left deletes; only that side's colour shows
    pg.click('.sheet [data-a=tkTab][data-v=all]'); pg.wait_for_timeout(250)
    pg.evaluate("""[...document.querySelectorAll('.sheet .tkfh[aria-expanded=false]')].map(b=>b.dataset.v).forEach(v=>SG_ACT.tkFold(document.querySelector('.sheet .tkfh[data-v=\"'+v+'\"]'),v))"""); pg.wait_for_timeout(200)  # Q10: every section folded open, so the swipes run inside them

    def swipe(tk, dx, hold=False):
        bb = pg.locator(f'.sheet .tkr[data-tk={tk}]').bounding_box()
        y = bb['y'] + bb['height'] / 2; x0 = bb['x'] + bb['width'] / 2
        pg.mouse.move(x0, y); pg.mouse.down(); pg.mouse.move(x0 + dx, y, steps=8)
        cls = pg.get_attribute(f'.sheet .tkr[data-tk={tk}]', 'class')
        vis = pg.evaluate("tk=>[...document.querySelectorAll('.sheet .tkr[data-tk=\"'+tk+'\"] .tkacts button')].map(b=>getComputedStyle(b).visibility)", tk)
        pg.mouse.up(); pg.wait_for_timeout(450)
        return cls, vis
    cls, vis = swipe('k3', 60)
    ok('sr' in cls and vis == ['visible', 'hidden'], f'a short swipe right shows only the orange Star ({vis})')
    ok(pg.evaluate("+document.querySelector('.sheet .tkr[data-tk=k3]').dataset.x") == 84, 'and leaves the 84 px button showing')
    pg.click('.sheet .tkr[data-tk=k3] .tkas'); pg.wait_for_timeout(400)
    ok(pg.evaluate("TAKES.find(t=>t.id==='k3').star") is True and 'Starred' in pg.inner_text('.toast'), 'tapping it stars the take')
    cls, vis = swipe('k0', 240)
    ok(pg.evaluate("TAKES.find(t=>t.id==='k0').star") is True, 'a swipe right past half the row stars straight away')
    cls, vis = swipe('k4', -60)
    ok('sl' in cls and vis == ['hidden', 'visible'], f'a short swipe left shows only the red Delete ({vis})')
    pg.click('.sheet .tkr[data-tk=k4] .tkad'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakeDel' and 'Delete this take?' in pg.inner_text('.sheet'), 'Delete always asks')
    pg.click('.sheet [data-a=close].ghost'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakes' and pg.evaluate("TAKES.length") == 5, 'Cancel goes back to the takes')
    swipe('k1', -260)
    ok(pg.evaluate("U.sheet") == 'sgTakeDel' and 'its comment' in pg.inner_text('.sheet'), 'past half the row, delete asks too, mentioning its comments')
    pg.click('.sheet [data-a=tkDelYes]'); pg.wait_for_timeout(500)
    ok(pg.evaluate("TAKES.length") == 4 and pg.evaluate("id=>!(songById(id).takeNotes&&songById(id).takeNotes.k1)", sid)
       and pg.evaluate("U.sheet") == 'sgTakes' and 'Take deleted' in pg.inner_text('.toast'), 'deleting removes the take with its name and comments')
    ok(pg.evaluate("TAKE.ext('k1')") is None, 'and its waveform on the device')
    # hold a row: Star · Rename · Delete
    bb = pg.locator('.sheet .tkr[data-tk=k2]').bounding_box()
    pg.mouse.move(bb['x'] + 60, bb['y'] + 20); pg.mouse.down(); held(pg); pg.mouse.up(); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sheet") == 'sgTakeMenu' and all(x in pg.inner_text('.sheet') for x in ('Star', 'Rename', 'Delete')), 'holding a row: Star · Rename · Delete')
    pg.click('.sheet [data-a=tkMenuRename]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakes' and pg.locator('#tkNameIn').count() == 1, 'Rename opens the take with its name field')
    pg.press('#tkNameIn', 'Escape'); pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    pg.context.close()


# ---------------------------------------------------------------- 9 · keep every take, storage, backups
def keep_all(b, t):
    ok = t.ok
    pg = t.page(b, ctx_args={'permissions': ['microphone']})
    sid = lyric_song(pg)
    o = pg.evaluate("id=>songById(id).order[0].o", sid)
    pg.evaluate(SONG, sid); pg.wait_for_timeout(200)
    for i in range(20):
        pg.evaluate("o=>{U.sSec=o;U.sheet=null;rerender()}", o); pg.wait_for_timeout(60)
        pg.click(f'.sgsec[data-o="{o}"] [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(1050)
        pg.click('[data-a=sgStop]'); pg.wait_for_function(f"!rec&&TAKES.length==={i + 1}", timeout=5000)
    ok(pg.evaluate("TAKES.length") == 20, 'record 20 takes of one song: all 20 are kept')
    ids = pg.evaluate("TAKES.map(t=>t.id)")
    pg.evaluate("([sid,a,b])=>{const s=songById(sid);s.takeNotes={[a]:{name:'Named'},[b]:{comments:[{t:1,text:'A comment'}]}};save()}", [sid, ids[3], ids[1]])
    pg.evaluate("(async()=>{const t=TAKES[2];t.star=true;await putTake(t);await refreshTakes()})()"); pg.wait_for_timeout(200)
    # Settings › Storage
    pg.evaluate("U.sheet=null;U.sd={};go(()=>{U.tab='settings';U.view='set';U.setPg='storage'})"); pg.wait_for_timeout(300)
    row = pg.inner_text('#app [data-a=sheet][data-v=storage]')
    ok('Recordings' in row and '20 takes' in row and 'MB' in row, 'Settings › Storage: “Recordings · 20 takes · x MB”: ' + row.replace('\n', ' '))
    pg.click('#app [data-a=tkReview]'); pg.wait_for_timeout(300)
    n = pg.locator('.sheet .tkrv').count()
    ok(pg.evaluate("U.sheet") == 'sgReview' and n == 18, f'Review old takes lists unstarred takes with no comments ({n} of 20)')
    first = pg.evaluate("document.querySelector('.sheet .tkrv [data-a=tkRvDel]').dataset.k")
    ok(first == ids[0], 'oldest first')
    pg.click('.sheet .tkrv [data-a=tkRvDel] >> nth=0'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakeDel', 'each one deletes with a confirmation')
    pg.click('.sheet [data-a=tkDelYes]'); pg.wait_for_timeout(500)
    ok(pg.evaluate("U.sheet") == 'sgReview' and pg.locator('.sheet .tkrv').count() == 17 and pg.evaluate("TAKES.length") == 19, 'and the list is back, one shorter')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    # backups: size beside Exclude recordings; names and comments always in
    pg.evaluate("SET.open('backup')"); pg.wait_for_timeout(200); pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=15000); pg.wait_for_timeout(200)
    txt = pg.inner_text('.sheet [data-a=exportNoRec]')
    ok('Without recordings: under 1 MB' in txt and 'With them:' in txt, 'the export sheet shows the expected size beside Exclude recordings: ' + txt.replace('\n', ' '))
    with pg.expect_download(timeout=8000) as dl: pg.click('[data-a=exportSave]')
    full = json.load(open(dl.value.path(), encoding='utf-8'))
    s = [x for x in full['data']['songs'] if x['id'] == sid][0]
    ok(len(full['takes']) == 19 and s['takeNotes'][ids[3]]['name'] == 'Named', 'a backup keeps every take, their names and comments')
    pg.wait_for_timeout(300); pg.evaluate("U.sheet&&closeSheet()"); pg.wait_for_timeout(200)
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=15000)
    pg.click('[data-a=exportNoRec]'); pg.wait_for_function("pendingExport&&!pendingExport.busy&&pendingExport.noRec", timeout=15000); pg.wait_for_timeout(200)
    with pg.expect_download(timeout=8000) as dl: pg.click('[data-a=exportSave]')
    p = os.path.join(OUT, 'batch12-norec.json'); data = dl.value.path(); txt = open(data, encoding='utf-8').read(); open(p, 'w', encoding='utf-8').write(txt)
    lean = json.loads(txt); s = [x for x in lean['data']['songs'] if x['id'] == sid][0]
    ok(lean['takes'] == [] and s['takeNotes'][ids[1]]['comments'][0]['text'] == 'A comment', 'with Exclude recordings, names and comments are still in')
    pg.wait_for_timeout(300); pg.evaluate("U.sheet&&closeSheet()"); pg.wait_for_timeout(200)
    # restore it: takes stay on the device, names and comments come back with the song
    pg.evaluate("id=>{delete songById(id).takeNotes;save()}", sid)
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(p); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(400)
    ok(pg.evaluate("TAKES.length") == 19 and pg.evaluate("([s,a])=>songById(s).takeNotes[a].name", [sid, ids[3]]) == 'Named',
       'restoring keeps all 19 takes, with their names and comments')
    pg.context.close()


# ---------------------------------------------------------------- 10 · playing again after the end
def replay(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    pg.evaluate(wav_take(1), ['r1', sid, None, 1])
    pg.evaluate("id=>{U.sheet='sgTakes';U.sd={k:id,all:true};go(()=>{U.tab='songs';U.view='lyr';U.songId=id});U.sheet='sgTakes';U.sd={k:id,all:true};rerender()}", sid); pg.wait_for_timeout(300)
    pg.click('.sheet .tkr .tkpp'); pg.wait_for_function("!!player&&!player.paused", timeout=5000)
    pg.wait_for_function("!player", timeout=5000); pg.wait_for_timeout(300)
    pg.click('.sheet .tkr #tkPP'); pg.wait_for_function("!!player&&!player.paused", timeout=5000)
    ok(pg.evaluate("player.currentTime") < 0.6, 'a take that finished plays again from 0:00 (the expanded take’s button)')
    pg.wait_for_function("!player", timeout=5000); pg.wait_for_timeout(300)
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(150)
    pg.evaluate("playTake('r1')"); pg.wait_for_function("!!player&&!player.paused", timeout=5000)
    # the take's length is known only once its metadata has loaded (slow on a busy runner): wait for it
    pg.wait_for_function("!!player&&isFinite(player.duration)&&player.duration>0", timeout=10000)
    pg.evaluate("player.pause();player.currentTime=player.duration"); pg.wait_for_timeout(200)
    pg.evaluate("FW_KINDS[0].toggle()"); pg.wait_for_function("!!player&&!player.paused", timeout=10000)
    ok(pg.evaluate("player.currentTime") < 0.6, 'from the floating window too')
    pg.evaluate("stopPlayback()")
    # the track
    add_track(pg, sid, F('Short.wav', 2))
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='trk';U.songId=id})", sid); loaded(pg, sid)
    pg.evaluate("TRACK.play()"); pg.wait_for_function("TRACK.el().ended", timeout=8000); pg.wait_for_timeout(200)
    pg.click('#trkPP'); pg.wait_for_function("TRACK.state().playing", timeout=5000)
    ok(pg.evaluate("TRACK.now()") < 0.8, 'a track that finished plays again from 0:00')
    pg.evaluate("TRACK.pause();TRACK.seek(TRACK.len())"); pg.evaluate(LEAVE); pg.wait_for_timeout(200)
    pg.evaluate("id=>TRACK.playSong(id)", sid); pg.wait_for_function("TRACK.state().playing", timeout=5000)
    ok(pg.evaluate("TRACK.now()") < 0.8, 'and from a song row’s play button')
    pg.context.close()


# ---------------------------------------------------------------- 11 · both ears
def both_ears(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    pg.evaluate(wav_take(3, ch=2, silent_right=True), ['side', sid, None, 2])
    pg.evaluate(wav_take(3, ch=2), ['stereo', sid, None, 1])
    before = pg.evaluate("(async()=>{const t=TAKES.find(x=>x.id==='side');return [...new Uint8Array(await t.blob.arrayBuffer())].reduce((a,b)=>(a*31+b)>>>0,7)})()")
    pg.evaluate("(async()=>{await TAKE.analyse('side');await TAKE.analyse('stereo')})()"); pg.wait_for_timeout(300)
    ok(pg.evaluate("TAKE.ext('side').side") == 0 and pg.evaluate("TAKE.hasMono('side')"), 'a take with one silent side is flagged, with a both-ears copy')
    ok(pg.evaluate("TAKE.ext('stereo').side") is None and not pg.evaluate("TAKE.hasMono('stereo')"), 'a normal stereo take is left as it is')
    out = pg.evaluate("""(async()=>{const t=TAKES.find(x=>x.id==='side'),bl=TAKE.blobFor(t);
      const ab=await new OfflineAudioContext(2,1,8000).decodeAudioData(await bl.arrayBuffer());
      const ctx=new OfflineAudioContext(2,ab.length,ab.sampleRate),s=ctx.createBufferSource();s.buffer=ab;s.connect(ctx.destination);s.start();
      const r=await ctx.startRendering(),rms=c=>{const d=r.getChannelData(c);let q=0;for(let i=0;i<d.length;i++)q+=d[i]*d[i];return Math.sqrt(q/d.length)};
      return [ab.numberOfChannels,rms(0),rms(1)]})()""")
    ok(out[0] == 1 and out[1] > 0.05 and out[2] > 0.05, f'it plays out of both channels ({out})')
    after = pg.evaluate("(async()=>{const t=TAKES.find(x=>x.id==='side');return [...new Uint8Array(await t.blob.arrayBuffer())].reduce((a,b)=>(a*31+b)>>>0,7)})()")
    ok(before == after, 'the stored recording is byte-identical: the original is never rewritten')
    pg.evaluate("playTake('side')"); pg.wait_for_function("!!player&&!player.paused", timeout=5000)
    ok(pg.evaluate("NOW.kind()") == 'take' and pg.evaluate("player.src.startsWith('blob:')"), 'it plays through the usual take player, so one sound at a time and the window still apply')
    pg.evaluate("stopPlayback()")
    # new takes: mixed down to one channel before encoding
    r = pg.evaluate("""(async()=>{const ac=new AudioContext(),o=ac.createOscillator(),d=ac.createMediaStreamDestination();d.channelCount=2;o.connect(d);o.start();
      const m=await monoStream(d.stream);const same=m.stream===d.stream;if(m.close)m.close();ac.close();return [same,!!m.close]})()""")
    ok(r == [False, True] or r == [True, False], f'a two-channel microphone is mixed to mono when the browser allows ({r})')
    ok(pg.evaluate("TAKE.ext('side').n") > 50, 'its waveform is kept too')
    pg.context.close()


# ---------------------------------------------------------------- 13 · track player markers and chips
def markers(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=667)
    sid = lyric_song(pg)
    add_track(pg, sid)
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='trk';U.songId=id})", sid); loaded(pg, sid)
    ok(pg.locator('#app [data-a=trkMkAdd]').count() == 1 and pg.locator('#app #trkMk .trkchip').count() == 0, 'Add marker sits beside Set start · Set end')
    pg.evaluate("TRACK.seek(10)"); pg.click('#app [data-a=trkMkAdd]'); pg.wait_for_timeout(150)
    pg.evaluate("TRACK.seek(4)"); pg.click('#app [data-a=trkMkAdd]'); pg.wait_for_timeout(150)
    mk = pg.evaluate("TRACK.markers()")
    ok([m['t'] for m in mk] == [4, 10], 'markers are added at the playhead, in time order')
    chips = pg.evaluate("[...document.querySelectorAll('#trkMk .trkchb b')].map(b=>b.textContent)")
    ok(chips == ['1', '2'] and '0:04.0' in pg.inner_text('#trkMk'), f'chips are numbered by time and renumber when one is added: {chips}')
    pg.evaluate("TRACK.seek(20);TRACK.play()"); pg.wait_for_function("TRACK.state().playing", timeout=5000); pg.wait_for_timeout(200)
    pg.click('#app [data-a=trkMkAdd]'); pg.wait_for_timeout(150)
    ok(len(pg.evaluate("TRACK.markers()")) == 3 and pg.evaluate("TRACK.state().playing"), 'adding one while playing carries on playing')
    ink = pg.evaluate("(()=>{const c=document.getElementById('trkC'),g=c.getContext('2d'),d=g.getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<d.length;i+=4)if(d[i]>100&&d[i+2]>180&&d[i+1]<140)n++;return n})()")
    ok(ink > 20, 'markers draw on the waveform in purple')
    pg.click('#trkMk .trkchip >> nth=1 >> .trkchb'); pg.wait_for_timeout(250)
    ok(abs(pg.evaluate("TRACK.now()") - 10) < 0.4 and pg.evaluate("TRACK.state().playing"), 'tapping a chip jumps there and keeps playing')
    ok(pg.locator('#trkMk .trkchip.cur').count() == 1, 'the tapped chip is outlined as current')
    pg.evaluate("TRACK.pause()"); pg.wait_for_timeout(150)
    pg.evaluate("TRACK.seek(8)"); pg.wait_for_timeout(100)
    eh = pg.locator('#trkEndH')
    ok(eh.count() == 1 and 'End 2 here' in eh.inner_text() and eh.get_attribute('aria-disabled') == 'true', '“End 2 here” is greyed while the playhead is before it')
    eh.click(force=True); pg.wait_for_timeout(150)  # aria-disabled, so Playwright needs force
    ok('past marker 2' in pg.inner_text('.toast') and 'end' not in pg.evaluate("TRACK.markers()")[1], 'with a hint')
    pg.evaluate("TRACK.seek(13.5)"); pg.wait_for_timeout(100)
    pg.click('#trkEndH'); pg.wait_for_timeout(150)
    ok(pg.evaluate("TRACK.markers()")[1].get('end') == 13.5 and '0:10.0–0:13.5' in pg.inner_text('#trkMk'), 'End 2 here sets its end at the playhead')
    # chip loop
    pg.click('#trkMk .trkchip >> nth=1 >> .trkchl'); pg.wait_for_timeout(150)
    L = pg.evaluate("id=>songById(id).loop", sid)
    ok(L['start'] == 10 and L['end'] == 13.5 and L['on'] and L['mk'] == pg.evaluate("TRACK.markers()[1].id"), 'a chip with an end has its own loop: on, that range is the loop')
    ok(pg.locator('#trkMk .trkchl.on').count() == 1 and pg.locator('#trkLoopB.on').count() == 1, 'its loop button and the transport show it on, in orange')
    # a second chip with a range: switching loops
    pg.click('#trkMk .trkchip >> nth=2 >> .trkchb'); pg.wait_for_timeout(100)
    pg.evaluate("TRACK.seek(TRACK.markers()[2].t+2)"); pg.click('#trkEndH'); pg.wait_for_timeout(150)
    pg.click('#trkMk .trkchip >> nth=2 >> .trkchl'); pg.wait_for_timeout(150)
    L = pg.evaluate("id=>songById(id).loop", sid)
    ok(L['mk'] == pg.evaluate("TRACK.markers()[2].id") and pg.locator('#trkMk .trkchl.on').count() == 1, 'there’s only one loop: another chip’s loop switches to it')
    pg.click('#trkLoopB'); pg.wait_for_timeout(150)
    ok(not pg.evaluate("id=>songById(id).loop.on", sid) and pg.locator('#trkMk .trkchl.on').count() == 0, 'loop off in the transport turns it off')
    pg.click('#trkMk .trkchip >> nth=1 >> .trkchl'); pg.wait_for_timeout(150)
    # dragging a handle updates the chip
    pg.evaluate("TRACK.seek(11.5)"); pg.wait_for_timeout(150)
    y = pg.evaluate("(()=>{const r=document.getElementById('trkStrip').getBoundingClientRect();return r.top+r.height/2})()")
    xs = pg.evaluate("v=>{const c=document.getElementById('trkC'),r=c.getBoundingClientRect(),W=TRK_LEVELS[TRACK.level()].win;return r.left+r.width*TRK_HEAD+(v-TRACK.now())*r.width/W}", 13.5)
    pg.mouse.move(xs, y); pg.mouse.down(); pg.mouse.move(xs + 25, y, steps=5); pg.mouse.up(); pg.wait_for_timeout(200)
    m2 = pg.evaluate("TRACK.markers()[1]"); L = pg.evaluate("id=>songById(id).loop", sid)
    ok(m2['end'] > 13.6 and abs(m2['end'] - L['end']) < 0.01, f'dragging the orange handle while a chip’s loop is on updates the chip ({m2["end"]})')
    pg.evaluate("TRACK.seek(12)"); pg.click('#app [data-a=trkSet][data-v=start]'); pg.wait_for_timeout(150)
    L = pg.evaluate("id=>songById(id).loop", sid)
    ok('mk' not in L and pg.evaluate("TRACK.markers()[1].t") == 10, 'Set start detaches the loop from the chip; the chip keeps its range')
    # hold a chip
    pg.locator('#trkMk .trkchip >> nth=0 >> .trkchb').scroll_into_view_if_needed()
    bb = pg.locator('#trkMk .trkchip >> nth=0 >> .trkchb').bounding_box()
    pg.mouse.move(bb['x'] + 10, bb['y'] + 10); pg.mouse.down(); held(pg); pg.mouse.up(); pg.wait_for_timeout(250)
    txt = pg.inner_text('.sheet')
    ok(pg.evaluate("U.sheet") == 'trkMkMenu' and all(x in txt for x in ('Rename', 'Move to playhead', 'Set end here', 'Delete marker', 'Clear all markers')),
       'holding a chip: Rename · Move to playhead · Set end here · Delete marker · Clear all markers…')
    pg.click('.sheet [data-a=trkMkRename]'); pg.wait_for_timeout(250)
    pg.fill('#trkMkIn', 'Run'); pg.click('.sheet [data-a=trkMkSaveName]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("TRACK.markers()[0].name") == 'Run' and 'Run' in pg.inner_text('#trkMk'), 'Rename names the chip')
    pg.evaluate("TRACK.seek(30)"); pg.wait_for_timeout(100)
    pg.locator('#trkMk .trkchip >> nth=0 >> .trkchb').scroll_into_view_if_needed()
    bb = pg.locator('#trkMk .trkchip >> nth=0 >> .trkchb').bounding_box()
    pg.mouse.move(bb['x'] + 10, bb['y'] + 10); pg.mouse.down(); held(pg); pg.mouse.up(); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=trkMkMove]'); pg.wait_for_timeout(250)
    ok([m['t'] for m in pg.evaluate("TRACK.markers()")][-1] == 30 and pg.evaluate("TRACK.markers()[2].name") == 'Run', 'Move to playhead moves it, renumbering by time')
    pg.locator('#trkMk .trkchip >> nth=2 >> .trkchb').scroll_into_view_if_needed()
    bb = pg.locator('#trkMk .trkchip >> nth=2 >> .trkchb').bounding_box()
    pg.mouse.move(bb['x'] + 10, bb['y'] + 10); pg.mouse.down(); held(pg); pg.mouse.up(); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=trkMkDel]'); pg.wait_for_timeout(250)
    ok(len(pg.evaluate("TRACK.markers()")) == 2 and 'Marker deleted' in pg.inner_text('.toast'), 'Delete marker removes it')
    # backups carry markers, with or without the track
    bk = pg.evaluate("id=>JSON.parse(JSON.stringify(songById(id)))", sid)
    ok(len(bk['markers']) == 2 and bk['markers'][0]['end'] > 13, 'markers are saved with the song (so in backups)')
    cl = pg.evaluate("s=>{const x=JSON.parse(JSON.stringify(s));delete x.track;return cleanSong(x).markers}", bk)
    ok(len(cl) == 2, 'and survive a restore without the track')
    res = pg.evaluate("""[
      cleanSong({id:'a',name:'A',markers:[{id:'x',t:-1},{id:'y',t:5,end:5.2},{id:'y',t:6},{t:3},{id:'z',t:'2'}]}).markers,
      cleanSong({id:'a',name:'A',track:{name:'t',dur:20},markers:[{id:'b',t:12,end:40},{id:'a',t:3},{id:'c',t:30}]}).markers,
      cleanSong({id:'a',name:'A',markers:[{id:'m',t:1,end:3}],loop:{start:1,end:3,on:true,mk:'gone'}}).loop,
      cleanSong({id:'a',name:'A',markers:[{id:'m',t:1,end:3}],loop:{start:1,end:3,on:true,mk:'m'}}).loop,
      cleanSong({id:'a',name:'A',markers:'nope'}).markers]""")
    ok(res[0] == [{'id': 'y', 't': 5}], f'cleanSong drops bad markers and duplicate ids, and an end under 0.5 s: {res[0]}')
    ok([m['id'] for m in res[1]] == ['a', 'b'] and res[1][1]['end'] == 20, f'sorted by time, ends clamped to the track, past the end dropped: {res[1]}')
    ok('mk' not in res[2] and res[3]['mk'] == 'm' and res[4] is None, 'a loop’s chip is kept only if that marker exists')
    # Clear all: both doors
    pg.click('#barR [data-a=trkMenu]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-v=trkMkClear]'); pg.wait_for_timeout(250)
    ok('Clear all markers?' in pg.inner_text('.sheet'), 'Clear all is in the player’s ⋯ menu, and asks')
    pg.click('.sheet [data-a=trkMkClearYes]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("TRACK.markers()") == [] and pg.locator('#trkMk .trkchip').count() == 0, 'and clears them')
    # taps in Section and Song stay put; the chip row scrolls sideways at 375 px
    for v in range(12):
        pg.evaluate(f"TRACK.seek({2 + v * 4})"); pg.click('#app [data-a=trkMkAdd]'); pg.wait_for_timeout(40)
    w = pg.evaluate("(()=>{const m=document.getElementById('trkMk');return [m.scrollWidth,m.clientWidth,m.getBoundingClientRect().height,document.documentElement.scrollWidth,innerWidth]})()")
    ok(w[0] > w[1] and w[2] < 45 and w[3] <= w[4], f'with many chips the row scrolls sideways in one line, the page doesn’t ({w})')
    ok(pg.get_attribute('#trkMk', 'data-own-gesture') is not None, 'the chip row has its own gesture')
    t.shot(pg, 'chips')
    # (Q02: Song is the only row view now; Markers is a grid)
    for lv in (2,):
        pg.click(f'#app .trklv button[data-v="{lv}"]'); pg.wait_for_timeout(200)
        r = pg.evaluate("(()=>{const c=document.querySelectorAll('#app .trkrow canvas')[0].getBoundingClientRect();return [c.left+c.width*0.25,c.top+c.height/2]})()")
        pg.mouse.click(r[0], r[1]); pg.wait_for_timeout(200)
        ok(pg.evaluate("TRACK.level()") == lv, 'a tap in Song view moves the playhead and stays there')
    pg.click('#app .trklv button[data-v="0"]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("TRACK.level()") == 0 and pg.evaluate(FITS), 'the pills change the zoom')
    pg.context.close()


# ---------------------------------------------------------------- layout: every new screen and sheet
SIZES = [('375', 375, 667), ('390', 390, 844), ('land', 852, 393), ('ipad', 820, 1180), ('mac', 1440, 900)]


def layout(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        for name, w, h in SIZES:
            pg = t.page(b, w=w, h=h, sc=sc, **({'ua': None} if name == 'mac' else {}))
            sid = lyric_song(pg)
            add_track(pg, sid)
            pg.evaluate(wav_take(6), ['L1', sid, pg.evaluate("id=>songById(id).order[0].o", sid), 3])
            pg.evaluate("([id,a])=>{songById(id).takeNotes={L1:{name:'A long name for a take that goes on',comments:[{t:2,text:'Comment'}]}};save()}", [sid, 'L1'])
            bad = []
            pg.evaluate(LIST); pg.wait_for_timeout(250)
            if not pg.evaluate(FITS): bad.append('songs list scrolls sideways')
            pg.click('[data-a=sgNew] >> nth=0'); pg.wait_for_timeout(300)
            if not pg.evaluate(FITS): bad.append('add sheet scrolls sideways')
            t.shot(pg, f'{name}-{sc}-add')
            pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
            pg.evaluate("id=>{go(()=>{U.tab='songs';U.view=split()?null:'lyr';U.songId=id})}", sid); pg.wait_for_timeout(300)
            if pg.locator('#app .sgtkb').count() != 1: bad.append('no Takes button')
            if not pg.evaluate(FITS): bad.append('song page scrolls sideways')
            pg.click('#app .sgtkb'); pg.wait_for_timeout(300)
            pg.click('.sheet .tkr .tktx'); pg.wait_for_timeout(400)
            pg.evaluate("stopPlayback()")
            if pg.locator('.sheet .tkr.open #tkWave').count() != 1 or not pg.evaluate(FITS): bad.append('takes sheet')
            if pg.evaluate("(()=>{const s=document.querySelector('.sheet'),r=s.getBoundingClientRect();return r.left<0||r.right>innerWidth+0.5})()"): bad.append('takes sheet off screen')
            t.shot(pg, f'{name}-{sc}-takes')
            pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
            pg.evaluate("id=>go(()=>{U.tab='songs';U.view='trk';U.songId=id})", sid); loaded(pg, sid)
            for v in (5, 9, 14):
                pg.evaluate(f"TRACK.seek({v})"); pg.click('#app [data-a=trkMkAdd]'); pg.wait_for_timeout(60)
            pg.click('#trkMk .trkchb >> nth=0'); pg.wait_for_timeout(100)
            if not pg.evaluate(FITS): bad.append('track player with chips scrolls sideways')
            t.shot(pg, f'{name}-{sc}-chips')
            ok(not bad, f'{name} {sc}: every new screen fits' + (': ' + ', '.join(bad) if bad else ''))
            pg.context.close()


PARTS = ['add_sheet', 'rows', 'one_sound', 'x_closes', 'length', 'one_list', 'takes', 'keep_all', 'replay', 'both_ears', 'markers', 'layout']


def run(b, t):
    import traceback
    only = os.environ.get('VS_B12')
    for n in (only.split(',') if only else PARTS):
        # each part on its own, so one that crashes doesn't hide the rest (and says which it was)
        try:
            globals()[n](b, t)
        except Exception as ex:
            tb = traceback.extract_tb(ex.__traceback__)
            line = next((f.lineno for f in reversed(tb) if f.filename.endswith('test_batch12.py')), '?')
            t.fails.append(f'{n} crashed at line {line}: ' + str(ex).split(chr(10))[0][:160])
            print(f'  FAIL  {n} crashed at line {line}: {ex}')
