"""Q02 · Track: Waveform Sections. The track player's four views (Phrase 6 s and Line 16 s strips, 148 px, with a
three-line lyric card above; Song in 24 s rows ending at the track's end, with lyrics under them; Markers, a grid of
rehearsal tiles), a marker made into a section start through the section picker (time order kept, one Undo for the
timing and the marker), the Markers grid's tiles, loops, transport and quick add, the jog wheel on the left, the
right or as a bottom roller, the red playhead, play-along running off the song's track (with a mute button, and
lyric-only without the track), the loop kept after the phone sleeps, the level reset, and old data.
The audio is synthetic: tones with gaps, written by the test as WAV files. Nothing copyrighted is ever used."""
import json
from harness import ready
from test_track import F, loaded, add_row, x_of, strip_y, drag, loop, INK

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']
LYR = """[Verse 1]
Morning light on the harbour wall
Counting boats as the tide comes in

[Chorus]
Hold on hold on to the sound
Carry me home when the lights go down

[Verse 2]
Paper maps and a borrowed coat
Somebody's song on the radio

[Chorus]
Hold on hold on to the sound
Carry me home when the lights go down"""
ADD = """([t,a,l])=>{U.sDraft={step:1,title:t,artist:a,text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();return U.songId}"""
OPEN = "id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})"
TL = "id=>JSON.parse(JSON.stringify(songById(id).timing||null))"
MK = "id=>JSON.parse(JSON.stringify(songById(id).markers||null))"
# markers at given times (as if added with the Marker button), straight into the song's data
SETMK = """([id,ts])=>{const sg=songById(id);sg.markers=ts.map((t,i)=>typeof t==='number'?{id:'m'+i,t}:Object.assign({id:'m'+i},t));save();rerender()}"""
PLAYER = "id=>TRACK.open(id)"


def lyric_song(pg, title='Harbour'):
    sid = pg.evaluate(ADD, [title, 'Harbour Lights', LYR]); pg.wait_for_timeout(350)
    return sid


def with_track(pg, sid, secs=60, name='Harbour.wav'):
    """Give a song its track through the song page's Practice row (the real door)."""
    pg.evaluate(OPEN, sid); pg.wait_for_timeout(300)
    pg.evaluate("id=>TRACK.expect(id)", sid)
    pg.set_input_files('#trackIn', F(name, secs))
    loaded(pg, sid)


def level(pg, i):
    pg.click(f'#app .trklv button[data-v="{i}"]'); pg.wait_for_timeout(200)


def hold(pg, sel):
    pg.hover(sel); pg.mouse.down(); pg.wait_for_timeout(650); pg.mouse.up(); pg.wait_for_timeout(250)


def no_side(pg):
    return pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth+1")


def views(b, t):
    ok = t.ok
    # a level saved by 3.19–3.22 (3 was Song's 30 s rows) is reset to the new default once
    pg = t.page(b)
    pg.evaluate("localStorage.setItem('vocalSongPrefs',JSON.stringify({trkLevel:3,trkSpeed:0.75}));SGP=null")
    sid = lyric_song(pg)
    with_track(pg, sid, 194, 'Harbour 194.wav')
    names = pg.evaluate("[...document.querySelectorAll('#app .trklv button')].map(b=>b.textContent)")
    ok(names == ['Phrase', 'Line', 'Song', 'Markers'], f'four views: Phrase, Line, Song and Markers ({names})')
    ok(pg.evaluate("TRACK.level()") == 1, 'a level saved before Q02 is reset to the default, Line')
    p = pg.evaluate("JSON.parse(localStorage.getItem('vocalSongPrefs'))")
    ok(p.get('trkLvV') == 2 and p.get('trkLevel') == 1 and p.get('trkSpeed') == 0.75,
       f'the reset is saved once, and the speed is kept ({p})')
    level(pg, 0)
    pg.reload(); ready(pg); pg.evaluate(PLAYER, sid); loaded(pg, sid)
    ok(pg.evaluate("TRACK.level()") == 0, 'a level chosen after the reset is kept after a reload (no second reset)')
    # the strips: 148 px, 6 s and 16 s
    h = pg.evaluate("document.getElementById('trkStrip').getBoundingClientRect().height")
    ok(abs(h - 148) < 1.5, f'the Phrase and Line strip is 148 px tall ({h})')
    ok(pg.evaluate("TRK_LEVELS[0].win") == 6 and pg.evaluate("TRK_LEVELS[1].win") == 16, 'Phrase shows 6 s, Line 16 s')
    ok(pg.evaluate(INK) > 1000, 'the strip draws the waveform')
    # the red playhead, in both themes
    for sc, want in (('light', '#ff3b30'), ('dark', '#ff453a')):
        pg.emulate_media(color_scheme=sc); pg.wait_for_timeout(80)
        v = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--trk-playhead').trim()")
        ok(v.lower() == want, f'{sc}: the playhead uses --trk-playhead, red ({v})')
    pg.emulate_media(color_scheme='light')
    pg.evaluate("TRACK.setLevel(1,false)"); pg.wait_for_timeout(150)
    px = pg.evaluate("""(()=>{const c=document.getElementById('trkC'),g=c.getContext('2d'),x=Math.round(c.width*TRK_HEAD),
      d=g.getImageData(x,Math.round(c.height*0.6),1,1).data;return [d[0],d[1],d[2]]})()""")
    ok(px[0] > 200 and px[1] < 90 and px[2] < 90, f'the playhead is drawn red on the strip ({px})')
    # Song: 24 s rows, the last one ending at the track's end (3:14 → a 3:12–3:14 row)
    level(pg, 2)
    rows = pg.evaluate("[...document.querySelectorAll('#app .trkrow')].map(r=>r.getAttribute('aria-label'))")
    ok(len(rows) == 9, f'a 3:14 track has 9 rows of 24 s ({len(rows)})')
    ok(rows and rows[0].startswith('0:00 to 0:24') and rows[-1].startswith('3:12 to 3:14'),
       f'the rows run 0:00–0:24 … 3:12–3:14 ({rows[0] if rows else None} … {rows[-1] if rows else None})')
    ok(pg.locator('#app .trkly').count() == 0 and pg.locator('#app [data-a=trkSongLyrics]').count() == 0,
       'an untimed song has no lyrics under the rows and no Lyrics pill')
    pg.locator('#app .trkrow').nth(8).click(position={'x': 300, 'y': 20}); pg.wait_for_timeout(150)
    v = pg.evaluate("TRACK.now()")
    ok(192 <= v <= 194, f'a tap on the last row moves the playhead inside 3:12–3:14 ({v:.2f})')
    # Markers: a grid with the quick-add tile, and the Markers transport
    level(pg, 3)
    ok(pg.locator('#trkGrid .trkqa').count() == 1 and pg.locator('#trkGrid .trktl[data-mk]').count() == 0,
       'Markers with no markers: just the quick-add tile')
    ok(pg.locator('#dock [data-a=trkReplay]').count() == 1 and pg.locator('#dock [data-a=trkNext]').count() == 1
       and pg.locator('#dock #trkPP').count() == 1, 'the Markers transport is Replay, Play/Pause and Next')
    ok(pg.locator('#app [data-a=trkSet]').count() == 0 and pg.locator('#trkMk').count() == 0, 'the grid replaces the chips and Set start/end')
    level(pg, 1)
    ok(pg.locator('#dock #trkLoopB').count() == 1 and pg.locator('#trkMk').count() == 1, 'back on Line: the player’s transport and chips again')
    ok(no_side(pg), 'no sideways scroll')
    pg.context.close()


SPREAD = """id=>{const sg=songById(id),M=ckModel(sg);ckStore(sg,M.L,ckSpread(sg,M.L,[4,18,32,46]),[true,true,true,true],M.marks,{est:true});rerender()}"""


def lyrics_card(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    with_track(pg, sid, 60)
    card = pg.inner_text('#trkCtx')
    ok('section start' in card and pg.locator('#trkCtx .trkcc').count() == 0,
       f'an untimed song’s card says how to set section starts ({card!r})')
    pg.evaluate(SPREAD, sid); pg.evaluate(PLAYER, sid); loaded(pg, sid)
    pg.evaluate("TRACK.seek(20)"); pg.wait_for_timeout(150)
    M = pg.evaluate("id=>{const M=ckModel(songById(id));return {T:M.T,L:M.L.map(l=>l.words.join(' '))}}", sid)
    i = max(k for k, r in enumerate(M['T']) if r[0] <= 20)
    lines = pg.evaluate("[...document.querySelectorAll('#trkCtx .trkcl')].map(p=>p.textContent)")
    ok(len(lines) == 3, f'three lines above the strip ({len(lines)})')
    ok(lines[1].startswith(M['L'][i]) and lines[0] == M['L'][i - 1] and lines[2] == M['L'][i + 1],
       f'the line at the playhead in the middle, the one before above, the next below ({lines})')
    ok(pg.inner_text('#trkCtx .trkcs') == 'Chorus 1', f'with its section ({pg.inner_text("#trkCtx .trkcs")})')
    pg.evaluate("TRACK.seek(1)"); pg.wait_for_timeout(150)
    ok('Before Verse 1' in pg.inner_text('#trkCtx') and M['L'][0] in pg.inner_text('#trkCtx .trkcn'),
       'before the first line: “Before Verse 1”, with the first line next')
    # playing: the card follows the playhead without redrawing the page
    pg.evaluate("document.getElementById('trkStrip').dataset.keep='1'")
    pg.evaluate("TRACK.seek(%f)" % (M['T'][3][0] - 0.3)); pg.evaluate("TRACK.play()"); pg.wait_for_timeout(900); pg.evaluate("TRACK.pause()")
    ok(M['L'][3] in pg.inner_text('#trkCtx .trkcc') and pg.evaluate("document.getElementById('trkStrip').dataset.keep") == '1',
       'while it plays, the card moves on to the next line in place')
    # Song: lyrics under the rows, toggled with the Lyrics pill (kept on this device)
    level(pg, 2)
    ok(pg.locator('#app .trkly').count() >= 2 and pg.locator('#app .trkll').count() == len(M['L']),
       f'Song shows every line under its row ({pg.locator("#app .trkll").count()} of {len(M["L"])})')
    ok(pg.locator('#app .trkls').all_inner_texts()[:2] == ['VERSE 1', 'CHORUS 1'] or
       [x.upper() for x in pg.locator('#app .trkls').all_inner_texts()[:2]] == ['VERSE 1', 'CHORUS 1'],
       'with each section’s name where it starts')
    pg.locator('#app .trkll').nth(2).click(); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("TRACK.now()") - M['T'][2][0]) < 0.05, 'tapping a line moves the playhead to it')
    ok(pg.get_attribute('#app [data-a=trkSongLyrics]', 'aria-pressed') == 'true', 'the Lyrics pill is on by default')
    pg.click('#app [data-a=trkSongLyrics]'); pg.wait_for_timeout(150)
    ok(pg.locator('#app .trkly').count() == 0 and pg.evaluate("sgp().trkSongLyrics") is False, 'the pill hides them')
    ok('trkSongLyrics' in pg.evaluate("localStorage.getItem('vocalSongPrefs')") and
       'trkSongLyrics' not in pg.evaluate("localStorage.getItem('vocalTracker')"), 'kept on this device, never in the backed-up data')
    pg.click('#app [data-a=trkSongLyrics]'); pg.wait_for_timeout(150)
    # a song without lyrics: no card, no promotion
    pg.evaluate("id=>{const sg=songById(id);delete sg.sections;delete sg.order;save();TRACK.open(id)}", sid); pg.wait_for_timeout(300)
    level(pg, 1)
    ok(pg.locator('#trkCtx').count() == 0 and pg.evaluate(INK) > 1000, 'a song without lyrics: just the strip, no card')
    pg.context.close()


def promotion(b, t):
    ok = t.ok
    pg = t.page(b, touch=False)
    pg.evaluate("CLOCK.fake(50000)")
    sid = lyric_song(pg)
    with_track(pg, sid, 60)
    pg.evaluate(SETMK, [sid, [3.5, 17, {'t': 22, 'end': 24, 'name': 'Riff'}]])
    # hold a chip: its menu has the door
    hold(pg, '#trkMk .trkchip[data-mk=m1] .trkchb')
    ok(pg.evaluate("U.sheet") == 'trkMkMenu' and pg.locator('.sheet [data-a=trkMkSec]').count() == 1,
       'holding a chip offers “Make this a section start…”')
    pg.click('.sheet [data-a=trkMkSec]'); pg.wait_for_timeout(250)
    rows = pg.evaluate("[...document.querySelectorAll('.sheet [data-a=trkMkSecPick]')].map(r=>[r.dataset.v,r.querySelector('.lbl').firstChild.textContent,r.getAttribute('aria-disabled')])")
    ok([r[1] for r in rows] == ['Verse 1', 'Chorus 1', 'Verse 2', 'Chorus 2'] and not any(r[2] for r in rows),
       f'the picker lists the running order; nothing is set yet so every place is open ({rows})')
    # untimed: the lines are spread from that start
    pg.click('.sheet [data-a=trkMkSecPick][data-v="1"]'); pg.wait_for_timeout(300)
    T = pg.evaluate(TL, sid)
    M = pg.evaluate("id=>{const M=ckModel(songById(id));return {T:M.T,anch:M.anch,first:M.L.findIndex(l=>l.k===1)}}", sid)
    ok(M['anch'] == [False, True, False, False] and abs(M['T'][M['first']][0] - 17) < 0.01,
       f'Chorus 1 starts at the marker’s time (17 s) in Song Clock’s timing ({M["anch"]}, {M["T"][M["first"]]})')
    ok(T and T.get('est') is True, 'an untimed song’s lines are spread, marked as estimated like Sync by sections')
    ok([m['id'] for m in pg.evaluate(MK, sid)] == ['m0', 'm2'], 'the promoted chip is removed')
    ok(pg.evaluate("U.sheet") is None and 'Chorus 1 starts at 0:17.0' in pg.inner_text('.toast') and
       pg.locator('.toast .ckub').count() == 1, 'a toast says so, with Undo')
    ok(pg.evaluate("CLOCK.synced(songById(%r))" % sid), 'the song is timed in Song Clock now')
    ok(pg.evaluate("TRACK.secStarts()") == [{'k': 1, 't': 17, 'label': 'Chorus 1'}], 'and the start is drawn on the waveform')
    # one Undo restores both
    pg.click('.toast .ckub'); pg.wait_for_timeout(300)
    ok(not pg.evaluate("CLOCK.synced(songById(%r))" % sid) and not (pg.evaluate(TL, sid) or {}).get('slots')
       and [m['id'] for m in pg.evaluate(MK, sid)] == ['m0', 'm1', 'm2'],
       'Undo restores the timing and the marker together')
    # timed: in order with the starts already set
    pg.evaluate(SPREAD, sid); pg.evaluate(PLAYER, sid); loaded(pg, sid)
    before = pg.evaluate("id=>ckModel(songById(id)).T", sid)
    pg.evaluate(SETMK, [sid, [3.5, 17, 40, 50]])
    ch = pg.evaluate("TRACK.secChoices('m0')")
    ok(ch[0]['why'] == '' and 'Must come after Verse 1' in ch[1]['why'],
       f'3.5 s can start Verse 1 (moving it), but not Chorus 1, which must come after Verse 1’s start ({[c["why"] for c in ch]})')
    ch = pg.evaluate("TRACK.secChoices('m2')")
    ok(ch[0]['why'].startswith('Must come before') and ch[1]['why'] and ch[3]['why'] == '' and ch[3]['set'] == 46,
       f'40 s can’t start Verse 1 or Chorus 1; Chorus 2 is open, set at 0:46 now ({[(c["why"], c["set"]) for c in ch]})')
    pg.evaluate("TRACK.jump('m2')")
    hold(pg, '#trkMk .trkchip[data-mk=m2] .trkchb'); pg.click('.sheet [data-a=trkMkSec]'); pg.wait_for_timeout(250)
    off = pg.evaluate("[...document.querySelectorAll('.sheet [data-a=trkMkSecPick][aria-disabled=true]')].map(r=>r.dataset.v)")
    ok(off == ['0', '1'], f'the picker greys the places that would break the order ({off})')
    pg.click('.sheet [data-a=trkMkSecPick][data-v="0"]', force=True); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") == 'trkMkSec' and pg.evaluate(TL, sid)['slots'] and
       abs(pg.evaluate("id=>ckModel(songById(id)).T[0][0]", sid) - before[0][0]) < 0.01, 'a greyed place does nothing')
    pg.click('.sheet [data-a=trkMkSecPick][data-v="3"]'); pg.wait_for_timeout(300)
    after = pg.evaluate("id=>ckModel(songById(id)).T", sid)
    M = pg.evaluate("id=>{const M=ckModel(songById(id));return {anch:M.anch,f:[0,1,2,3].map(k=>M.L.findIndex(l=>l.k===k))}}", sid)
    f = M['f']
    ok(abs(after[f[3]][0] - 40) < 0.01 and all(abs(after[f[k]][0] - before[f[k]][0]) < 0.01 for k in (0, 1, 2)),
       f'moving Chorus 2 to 40 s keeps the other set starts where they were ({[after[i][0] for i in f]})')
    ok(all(after[i][0] < after[i + 1][0] for i in range(len(after) - 1)), 'every line is still in time order')
    ok(pg.evaluate("TRACK.secStarts().map(s=>s.t)") == [4, 18, 32, 40], 'the waveform shows the four starts')
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(250)
    ok(abs(pg.evaluate("id=>ckModel(songById(id)).T", sid)[f[3]][0] - 46) < 0.01 and len(pg.evaluate(MK, sid)) == 4,
       'Undo puts Chorus 2 back at 0:46 and the marker back')
    # Check timing counts the starts
    pg.evaluate("TRACK.promote('m1',1)"); pg.wait_for_timeout(250)
    pg.evaluate("id=>{CK.ret=null;ckOpenCheck(songById(id))}", sid); pg.wait_for_timeout(300)
    ok('4 of 4 set' in pg.inner_text('#app'), 'Song Clock’s Check timing shows the starts set on the waveform')
    # data: the timing and markers are in backups like any song field; old marker loops without an end keep their chip
    d = pg.evaluate("(()=>{const sg=JSON.parse(JSON.stringify(songById(U.songId)));sg.loop={start:3.5,end:40,on:true,mk:'m0'};return cleanSong(sg)})()")
    ok((d.get('loop') or {}).get('mk') == 'm0' and 'm0' not in [m['id'] for m in d.get('markers', [])] or (d.get('loop') or {}).get('mk') == 'm0',
       'a loop that belongs to a marker without an end keeps it (the Markers grid’s loops)')
    d = pg.evaluate("(()=>{const sg=JSON.parse(JSON.stringify(songById(U.songId)));sg.loop={start:3.5,end:40,on:true,mk:'gone'};return cleanSong(sg)})()")
    ok('mk' not in (d.get('loop') or {}), 'a loop whose marker has gone loses the link')
    pg.context.close()


def grid(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=667)
    sid = lyric_song(pg)
    with_track(pg, sid, 60)
    pg.evaluate(SETMK, [sid, [2, {'t': 9, 'end': 12, 'name': 'Run into the chorus'}, 25, 25.3, 40]])
    level(pg, 3)
    ok(pg.locator('#trkGrid .trktl[data-mk]').count() == 5 and pg.locator('#trkGrid .trkqa').count() == 1,
       'a tile for each marker, then the quick-add tile')
    cols = pg.evaluate("getComputedStyle(document.getElementById('trkGrid')).gridTemplateColumns.split(' ').length")
    ok(cols == 2, f'two columns ({cols})')
    ok(pg.inner_text('#trkGrid .trktl[data-mk=m1] .trktn') == 'Run into the chorus' and
       pg.inner_text('#trkGrid .trktl[data-mk=m0] .trktn') == 'Marker 1', 'named markers show their name, others “Marker n”')
    ok(pg.evaluate("TRACK.rangeOf('m0')")['e'] == 9 and pg.evaluate("TRACK.rangeOf('m1')")['e'] == 12 and
       abs(pg.evaluate("TRACK.rangeOf('m4')")['e'] - 60) < 0.05,
       'each runs to its own end, else the next marker, and the last to the track’s end')
    ok(pg.get_attribute('#trkGrid .trktl[data-mk=m2] .trktlo', 'aria-disabled') == 'true' and
       pg.get_attribute('#trkGrid .trktl[data-mk=m0] .trktlo', 'aria-disabled') is None,
       'a marker under 0.5 s from the next can’t loop (its loop button is greyed)')
    # tap a tile: it plays and loops its range
    pg.click('#trkGrid .trktl[data-mk=m0] .trktlb'); pg.wait_for_function("TRACK.state().playing", timeout=5000)
    L = loop(pg, sid)
    ok(L and L['start'] == 2 and L['end'] == 9 and L['on'] and L.get('mk') == 'm0', f'tapping marker 1 plays and loops 0:02–0:09 ({L})')
    pg.wait_for_timeout(300)
    cls = pg.evaluate("document.querySelector('#trkGrid .trktl[data-mk=m0]').className")
    ok('sel' in cls and 'play' in cls, f'it’s selected and playing at once ({cls})')
    ok(pg.get_attribute('#trkGrid .trktl[data-mk=m0] .trktlo', 'aria-pressed') == 'true', 'its loop button is on')
    pg.evaluate("TRACK.seek(8.9)"); pg.wait_for_timeout(500)
    v = pg.evaluate("TRACK.now()")
    ok(2 <= v < 3.2, f'the loop wraps back to the marker’s start ({v:.2f})')
    # selected and playing are separate: play elsewhere, the selection stays
    pg.evaluate("TRACK.seek(26)"); pg.evaluate("songById(%r).loop.on=false" % sid); pg.wait_for_timeout(300)
    cls = pg.evaluate("[...document.querySelectorAll('#trkGrid .trktl[data-mk]')].map(e=>e.dataset.mk+':'+(e.classList.contains('sel')?'s':'')+(e.classList.contains('play')?'p':''))")
    ok('m0:s' in cls and 'm3:p' in cls, f'the playing marker follows the playhead while the selection stays ({cls})')
    pg.evaluate("TRACK.pause()"); pg.wait_for_timeout(150)
    # the loop button: on and off without playing
    pg.click('#trkGrid .trktl[data-mk=m4] .trktlo'); pg.wait_for_timeout(150)
    L = loop(pg, sid)
    ok(L['start'] == 40 and abs(L['end'] - 60) < 0.05 and L['on'] and L['mk'] == 'm4' and not pg.evaluate("TRACK.state().playing"),
       f'a tile’s loop button loops the last marker to the end without playing ({L})')
    pg.click('#trkGrid .trktl[data-mk=m4] .trktlo'); pg.wait_for_timeout(150)
    ok(loop(pg, sid)['on'] is False, 'and turns it off again')
    pg.click('#trkGrid .trktl[data-mk=m2] .trktlo', force=True); pg.wait_for_timeout(200)
    ok('Too short' in pg.inner_text('.toast'), 'a marker too close to the next says it’s too short to loop')
    # a too-short marker still plays, without a loop
    pg.click('#trkGrid .trktl[data-mk=m2] .trktlb'); pg.wait_for_function("TRACK.state().playing", timeout=5000); pg.wait_for_timeout(700)
    ok(not loop(pg, sid)['on'] and pg.evaluate("TRACK.now()") > 25.5, 'tapping it plays on from there with no loop')
    # the transport: Next and Replay
    pg.click('#dock [data-a=trkNext]'); pg.wait_for_timeout(200)
    ok(abs(pg.evaluate("TRACK.now()") - 40) < 0.4 and pg.evaluate("TRACK.state().playing"), 'Next goes to the next marker')
    pg.evaluate("TRACK.seek(43)"); pg.wait_for_timeout(100)
    pg.click('#dock [data-a=trkReplay]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("TRACK.now()") - 40) < 0.4, 'Replay goes back to the start of the marker it’s in')
    pg.click('#trkGrid .trktl[data-mk=m0] .trktlb'); pg.wait_for_timeout(150)
    pg.click('#dock [data-a=trkNext]'); pg.wait_for_timeout(150)
    L = loop(pg, sid)
    ok(L['mk'] == 'm1' and L['start'] == 9 and L['end'] == 12, f'with a marker loop on, Next moves the loop to the next marker ({L})')
    pg.click('#dock #trkPP'); pg.wait_for_timeout(150)
    ok(not pg.evaluate("TRACK.state().playing"), 'Play/Pause pauses')
    # quick add
    pg.evaluate("TRACK.seek(33.4)"); pg.wait_for_timeout(100)
    ok(pg.inner_text('#trkQaT') == '0:33.4', 'the quick-add tile shows the playhead’s time')
    pg.click('#trkGrid .trkqa'); pg.wait_for_timeout(200)
    ok(pg.locator('#trkGrid .trktl[data-mk]').count() == 6 and any(abs(m['t'] - 33.4) < 0.05 for m in pg.evaluate(MK, sid)),
       'and adds a marker there')
    # hold a tile: the same menu as a chip
    hold(pg, '#trkGrid .trktl[data-mk=m1] .trktlb')
    ok(pg.evaluate("U.sheet") == 'trkMkMenu' and pg.locator('.sheet [data-a=trkMkSec]').count() == 1, 'holding a tile opens the marker’s menu')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(200)
    ok(no_side(pg), 'no sideways scroll at 375 px')
    t.shot(pg, 'markers-375')
    # existing chips are unchanged: a tap jumps, it doesn't loop
    level(pg, 1)
    pg.evaluate("songById(%r).loop.on=false" % sid)
    pg.click('#trkMk .trkchip[data-mk=m2] .trkchb'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("TRACK.now()") - 25) < 0.05 and not loop(pg, sid)['on'], 'chips still jump on a tap, as before')
    pg.context.close()


def jog(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid = lyric_song(pg)
    with_track(pg, sid, 60)
    ok(pg.evaluate("TRACK.jogPos()") == 'right' and pg.locator('.trkstrip.jog-right #trkJog').count() == 1, 'the jog wheel starts on the right')
    pg.click('#barR [data-a=trkMenu]'); pg.wait_for_timeout(250)
    ok(pg.locator('.sheet [data-a=trkJogPos]').count() == 3 and
       pg.get_attribute('.sheet [data-a=trkJogPos][data-v=right]', 'aria-checked') == 'true', 'the ⋯ menu has Left, Right and Bottom roller')
    pg.click('.sheet [data-a=trkJogPos][data-v=left]'); pg.wait_for_timeout(200)
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(250)
    j = pg.evaluate("(()=>{const j=document.getElementById('trkJog').getBoundingClientRect(),c=document.getElementById('trkC').getBoundingClientRect(),s=document.getElementById('trkStrip').getBoundingClientRect();return [j.left,j.width,c.left-s.left,c.width,s.width]})()")
    ok(abs(j[0] + 48) < 1.5 and abs(j[2] - 48) < 1.5 and abs(j[4] - j[3] - 48) < 1.5,
       f'Left: the wheel is half off the left edge, the waveform starts 48 px in ({j})')
    # the wheel grows under the finger; down is later, as on the right
    c = pg.evaluate("(()=>{const r=document.getElementById('trkJog').getBoundingClientRect();return [r.right-20,r.top+r.height/2]})()")
    t0 = pg.evaluate("TRACK.now()")
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': c[0], 'y': c[1]}]})
    for i in range(1, 7): cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': c[0], 'y': c[1] + i * 15}]})
    tf = pg.evaluate("getComputedStyle(document.getElementById('trkJog')).transform")
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); pg.wait_for_timeout(150)
    ok(tf not in ('none', '') , f'the edge wheel slides further in while it’s held ({tf})')
    ok(pg.evaluate("TRACK.now()") - t0 > 2, f'dragging it down moves later ({pg.evaluate("TRACK.now()") - t0:.2f} s)')
    ok('jogPos' not in pg.evaluate("localStorage.getItem('vocalTracker')") and
       '"trkJogPos":"left"' in pg.evaluate("localStorage.getItem('vocalSongPrefs')"), 'the side is kept on this device only')
    # bottom: a full-width roller under the strip; right is later
    pg.click('#barR [data-a=trkMenu]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=trkJogPos][data-v=bottom]'); pg.wait_for_timeout(200)
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(250)
    r = pg.evaluate("(()=>{const j=document.getElementById('trkJog'),r=j.getBoundingClientRect(),s=document.getElementById('trkStrip').getBoundingClientRect(),c=document.getElementById('trkC').getBoundingClientRect();return [j.className,r.width,innerWidth,r.top>=s.bottom,c.width,s.width,r.height]})()")
    ok(r[0] == 'trkroll' and abs(r[1] - r[2]) < 1.5 and r[3] and abs(r[4] - r[5]) < 1.5,
       f'Bottom: a full-width roller under the strip, and the waveform takes the whole width ({r})')
    ok('roller' in pg.inner_text('#trkHint'), 'the hint names the roller')
    t0 = pg.evaluate("TRACK.now()")
    y = r[6] / 2 + pg.evaluate("document.getElementById('trkJog').getBoundingClientRect().top")
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 100, 'y': y}]})
    for i in range(1, 7): cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 100 + i * 15, 'y': y}]})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); pg.wait_for_timeout(150)
    d = pg.evaluate("TRACK.now()") - t0
    ok(abs(d - 90 * 16 / 300) < 0.6, f'dragging the roller right by 90 px moves 90 × 16 / 300 s later ({d:.2f})')
    ok(pg.evaluate("U.view") == 'trk', 'a sideways drag on the roller never swipes back')
    ok(no_side(pg), 'no sideways scroll')
    t.shot(pg, 'roller')
    pg.context.close()


def along(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    with_track(pg, sid, 60)
    pg.evaluate(SPREAD, sid)
    pg.evaluate(OPEN, sid); pg.wait_for_timeout(300)
    pg.evaluate("id=>ckOn(songById(id))", sid); pg.wait_for_timeout(300)
    ok(pg.locator('#dock .cktr #ckMute').count() == 1 and pg.get_attribute('#ckMute', 'aria-pressed') == 'false',
       'with the song’s track on this device, play-along has a mute button (backing on by default)')
    pg.click('#dock .cktr [data-a=ckPP]'); pg.wait_for_function("TRACK.state().playing&&TRACK.state().along", timeout=8000); pg.wait_for_timeout(600)
    st = pg.evaluate("[TRACK.now(),CLOCK.now(),TRACK.state().muted,NOW.kind(),FW_KINDS.find(k=>k.id==='track').active()]")
    ok(abs(st[0] - st[1]) < 0.15 and st[2] is False, f'play-along plays the track and its lyrics follow the track’s time ({st[:3]})')
    ok(st[3] == 'clock' and not st[4], 'it’s play-along’s sound (one sound at a time), not the track player’s')
    pg.evaluate("TRACK.el().currentTime=30"); pg.wait_for_timeout(400)
    ok(abs(pg.evaluate("CLOCK.now()") - 30) < 0.6, 'a jump in the track moves the lyrics with it')
    pg.click('#ckMute'); pg.wait_for_timeout(100)
    ok(pg.evaluate("TRACK.state().muted") and pg.get_attribute('#ckMute', 'aria-pressed') == 'true', 'Mute mutes the track; the lyrics carry on')
    pg.click('#ckMute'); pg.wait_for_timeout(100)
    # tapping a line jumps the track too
    pg.evaluate("document.querySelectorAll('#ckpa .ckl')[4].click()"); pg.wait_for_timeout(400)
    want = pg.evaluate("id=>ckModel(songById(id)).T[4][0]", sid)
    ok(abs(pg.evaluate("TRACK.now()") - want) < 0.6, f'tapping a line moves the track there ({pg.evaluate("TRACK.now()"):.2f} vs {want:.2f})')
    # pause: both stop
    pg.click('#dock .cktr [data-a=ckPP]'); pg.wait_for_timeout(300)
    ok(not pg.evaluate("TRACK.state().playing") and not pg.evaluate("CLOCK.state().run") and pg.evaluate("TRACK.state().along") is None,
       'pausing play-along pauses the track')
    # the lock screen (the track paused from outside): play-along pauses with it
    pg.click('#dock .cktr [data-a=ckPP]'); pg.wait_for_function("TRACK.state().along", timeout=5000); pg.wait_for_timeout(300)
    pg.evaluate("TRACK.el().pause()"); pg.wait_for_timeout(300)
    ok(not pg.evaluate("CLOCK.state().run"), 'the track paused from outside pauses play-along too')
    # another sound stops both
    pg.click('#dock .cktr [data-a=ckPP]'); pg.wait_for_function("TRACK.state().along", timeout=5000); pg.wait_for_timeout(200)
    pg.evaluate("COACH.play&&NOW.start('take','x',()=>{})"); pg.evaluate("NOW.start('take','x',()=>{})"); pg.wait_for_timeout(300)
    ok(not pg.evaluate("CLOCK.state().run") and not pg.evaluate("TRACK.state().playing"), 'starting another sound stops play-along and its track')
    # the end of the track: play-along stops there, and the player's loop doesn't take over
    pg.evaluate("id=>{songById(id).loop={start:1,end:60,on:true};save()}", sid)
    pg.evaluate("ckPlay()"); pg.wait_for_function("TRACK.state().along", timeout=5000)
    pg.evaluate("TRACK.el().currentTime=59.3"); pg.wait_for_function("!CLOCK.state().run", timeout=5000); pg.wait_for_timeout(500)
    ok(not pg.evaluate("TRACK.state().playing"), 'at the track’s end play-along stops, and the player’s loop doesn’t restart it')
    ckoff = pg.evaluate("ckOff()")
    # without the track on this device: lyric-only, no mute
    pg.evaluate("id=>TRACK.forget([id])", sid); pg.wait_for_timeout(300)
    pg.evaluate("id=>ckOn(songById(id))", sid); pg.wait_for_timeout(300)
    ok(pg.locator('#ckMute').count() == 0, 'without the track on this device, no mute button')
    pg.evaluate("CLOCK.fake(10000);ckPlay()"); pg.evaluate("CLOCK.advance(3)")
    ok(pg.evaluate("CLOCK.state().run") and not pg.evaluate("TRACK.state().playing") and pg.evaluate("TRACK.state().along") is None,
       'play-along runs on its own clock, lyrics only, as before')
    pg.evaluate("ckOff()")
    pg.context.close()


def sleep(b, t):
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    with_track(pg, sid, 60)
    pg.evaluate("id=>{songById(id).loop={start:10,end:14,on:true};save()}", sid)
    pg.evaluate("TRACK.play()"); pg.wait_for_function("TRACK.state().playing", timeout=5000)
    # asleep: the screen locked and the playhead found past the loop on waking
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true})")
    pg.evaluate("TRACK.el().currentTime=30"); pg.wait_for_timeout(250)
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
    pg.wait_for_timeout(200)
    v = pg.evaluate("TRACK.now()")
    ok(10 <= v < 11.5, f'waking with the playhead outside the loop puts it back at the loop’s start ({v:.2f})')
    # while hidden, the loop is kept on timeupdate too (no animation frames on a locked screen)
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true})")
    pg.evaluate("TRACK.seek(13.6)"); pg.wait_for_timeout(1300)
    v = pg.evaluate("TRACK.now()")
    ok(10 <= v < 13.95, f'while hidden the loop still wraps ({v:.2f})')
    pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false})")
    pg.evaluate("TRACK.pause()")
    pg.context.close()


SIZES = [('375', 375, 667), ('390', 390, 844), ('land', 852, 393), ('ipad', 820, 1180), ('mac', 1440, 900)]


def sizes(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        for name, w, h in SIZES:
            pg = t.page(b, w=w, h=h, sc=sc)
            sid = lyric_song(pg)
            with_track(pg, sid, 60)
            pg.evaluate(SPREAD, sid); pg.evaluate(SETMK, [sid, [2, {'t': 9, 'end': 12, 'name': 'Run into the chorus'}, 25, 40]])
            pg.evaluate(PLAYER, sid); loaded(pg, sid); pg.evaluate("TRACK.seek(20)")
            bad = []
            for i in range(4):
                for jp in (('right', 'left', 'bottom') if i < 2 else ('right',)):
                    pg.evaluate("v=>{sgp().trkJogPos=v;saveSGP()}", jp); pg.evaluate("i=>TRACK.setLevel(i,false)", i)
                    pg.evaluate("TRACK.setLevel((TRACK.level()+1)%4,false)"); pg.evaluate("i=>TRACK.setLevel(i,false)", i); pg.wait_for_timeout(120)
                    r = pg.evaluate("""(()=>{const d=document.querySelector('#dock .trktr');return [document.documentElement.scrollWidth<=innerWidth+1,
                        !!d&&d.getBoundingClientRect().bottom<=innerHeight+1]})()""")
                    if not all(r): bad.append((i, jp, r))
                    if i < 2 and pg.evaluate(INK) < 500: bad.append((i, jp, 'no ink'))
                if name in ('375', 'ipad') and sc == 'dark' or name == '390' and sc == 'light':
                    t.shot(pg, f'{name}-{sc}-{i}')
            ok(not bad, f'{name} {sc}: every view and jog side fits, with no sideways scroll and the transport in view ({bad})')
            pg.context.close()


def run(b, t):
    views(b, t)
    lyrics_card(b, t)
    promotion(b, t)
    grid(b, t)
    jog(b, t)
    along(b, t)
    sleep(b, t)
    sizes(b, t)
