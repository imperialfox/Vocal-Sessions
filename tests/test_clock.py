"""Song Clock (3.18, phase A1; Q05 Song Clock: Tap Re-Anchor): the song header's length and picker, the controls grid
and pinned icons, timing that needs the song's track on this device (Timing asks for it; Sync by sections is retired),
the timing maths, play-along (current line, jumping, nudges with Undo, pausing onto the song page), Marks while
playing, Check timing (every row opens the track player on its line), the line lane on the track's waveform (dragging
edges, snapping, Start here / End here, Undo), punch-in, Flag and Retime, the hold menu on a lyric line, suggested
breaths, the pencil, lyric edits, the floating window, data upgrades, damaged timing, backups, the wake lock, and every
size in light and dark.
Play-along's audio is stubbed here (TRACK.along), so the test clock drives the lyrics; test_waveform plays the real
synthetic track. The audio files are tones with gaps, written by the test. Nothing copyrighted is ever used."""
import json, copy
from harness import sample, ready, OUT, now, iso
from test_track import F, loaded

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
# a wake lock that counts, since headless Chromium has none
WAKE = """(()=>{window.__wl={req:0,rel:0,held:0};Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request(){window.__wl.req++;window.__wl.held++;
  const l=new EventTarget();l.release=()=>{window.__wl.rel++;window.__wl.held--;l.dispatchEvent(new Event('release'));return Promise.resolve()};return Promise.resolve(l)}}})})()"""
# play-along's track is stubbed: the test clock (CLOCK.fake / CLOCK.advance) moves the lyrics, not the audio
QUIET = "TRACK.along=async()=>true"
OPEN = "id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})"
# the section starts at 0, 12, 24 and 36 s and the lines spread between them (as a marker promoted on the waveform does)
SPREAD = """([id,s])=>{const sg=songById(id),M=ckModel(sg);ckStore(sg,M.L,ckSpread(sg,M.L,s),s.map(()=>true),M.marks,{est:true});rerender()}"""


def song(pg):
    sid = pg.evaluate(ADD, ['Harbour', 'Harbour Lights', LYR]); pg.wait_for_timeout(400)
    return sid


def tl(pg):
    return pg.evaluate("JSON.parse(JSON.stringify(songById(U.songId).timing||null))")


def model(pg):
    return pg.evaluate("CLOCK.model()")


def give_track(pg, sid, secs=60, name='Harbour.wav', door='.ckrow [data-a=ckTile][data-v=timing]'):
    """Add the song's track through a real door (by default the pinned Timing icon, which asks for it)."""
    with pg.expect_file_chooser() as fc: pg.click(door)
    fc.value.set_files(F(name, secs))
    pg.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()", arg=sid, timeout=15000); pg.wait_for_timeout(300)


def lane_x(pg, v):
    """The x of time v on the line lane (it shares the strip's scale, playhead at 40%)."""
    return pg.evaluate("v=>{const c=document.getElementById('trkLC'),r=c.getBoundingClientRect(),W=TRK_LEVELS[TRACK.level()].win;"
                       "return r.left+r.width*TRK_HEAD+(v-TRACK.now())*r.width/W}", v)


def lane_y(pg):
    return pg.evaluate("(()=>{const r=document.getElementById('trkLane').getBoundingClientRect();return r.top+r.height/2})()")


def hold(pg, sel, ms=650):
    pg.hover(sel); pg.mouse.down(); pg.wait_for_timeout(ms); pg.mouse.up(); pg.wait_for_timeout(250)


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=844, touch=True)
    pg.evaluate(WAKE)
    pg.evaluate("CLOCK.fake(50000)")
    pg.evaluate(QUIET)
    sid = song(pg)
    t.shot(pg, 'song')

    # ---------- the header: "Artist · 3:58", pinned icons, ⋯ ----------
    ok(pg.inner_text('.ckart').strip() == 'Harbour Lights', 'the header shows the artist with no length while it isn\'t set')
    pins = pg.evaluate("[...document.querySelectorAll('.ckrow .ckpi')].map(b=>b.dataset.v||b.dataset.a)")
    ok(pins == ['timing', 'key', 'ckGrid'], f'Timing and Key are pinned beside the artist by default, and ⋯ is last ({pins})')
    ok(pg.locator('.sgmodes [data-a=sgKey]').count() == 0, 'Key has moved from the modes row to the header')
    ok(pg.evaluate("CLOCK.synced(songById(U.songId))") is False and tl(pg) is None, 'a new song has no timing (not synced)')

    # Check timing with no track and no timing: it asks for the track (Sync by sections is retired)
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250); pg.click('.sheet [data-a=ckTile][data-v=check]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'ckCheck' and pg.locator('#app [data-a=ckAddTrack]').count() == 1 and
       'Add a track to time this song' in pg.inner_text('#app'), 'Check timing on an untimed song without a track offers Add a track to time this song')
    ok(pg.locator('[data-a=ckSyncAgain], #ckpad').count() == 0, 'nothing offers Sync by sections any more')
    pg.click('#barL [data-a=ckCheckBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'lyr', 'Back goes to the song')

    # the length picker: wheels, a live readout, Cancel and Set, just below what was tapped
    pg.click('#barR [data-a=ckPencil]'); pg.wait_for_timeout(300)
    lb = pg.locator('.ckedrow [data-a=ckLen]')
    ok(lb.inner_text() == 'Add length', 'the pencil offers Add length')
    lb.click(); pg.wait_for_timeout(300)
    ok(pg.locator('#ckpk .ckwcol').count() == 2, 'the length picker has a minutes and a seconds wheel')
    r1, r2 = lb.bounding_box(), pg.locator('#ckpk .ckpop').bounding_box()
    ok(abs(r2['y'] - (r1['y'] + r1['height'] + 8)) < 2, 'it pops over just below what was tapped')
    ok(pg.inner_text('#ckpOut') == '3:30', 'it starts at 3:30 when no length is set')
    nm = pg.evaluate("document.querySelectorAll('#ckpk .ckwcol')[0].querySelectorAll('[data-v]').length")
    ns = pg.evaluate("document.querySelectorAll('#ckpk .ckwcol')[1].querySelectorAll('[data-v]').length")
    ok(nm == 21 and ns == 60, f'minutes 0–20 and seconds 00–59 ({nm}, {ns})')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#ckpk .ckwcol')).scrollSnapType").startswith('y'), 'the wheels snap to each value')
    pg.evaluate("(()=>{const c=document.querySelectorAll('#ckpk .ckwcol');c[0].scrollTop=3*36;c[1].scrollTop=58*36})()"); pg.wait_for_timeout(200)
    ok(pg.inner_text('#ckpOut') == '3:58', 'the readout follows the wheels: ' + pg.inner_text('#ckpOut'))
    pg.locator('#ckpk .ckwcol').nth(1).press('ArrowUp'); pg.wait_for_timeout(100)
    ok(pg.inner_text('#ckpOut') == '3:57', 'arrow keys move a wheel')
    pg.locator('#ckpk .ckwcol').nth(1).press('ArrowDown'); pg.wait_for_timeout(100)
    pg.click('#ckpk button[data-a=ckPickCancel]'); pg.wait_for_timeout(200)
    ok(pg.locator('#ckpk').count() == 0 and tl(pg) is None, 'Cancel changes nothing')
    lb.click(); pg.wait_for_timeout(250)
    pg.evaluate("(()=>{const c=document.querySelectorAll('#ckpk .ckwcol');c[0].scrollTop=3*36;c[1].scrollTop=58*36})()"); pg.wait_for_timeout(200)
    pg.click('#ckpk [data-a=ckPickSet]'); pg.wait_for_timeout(300)
    ok(tl(pg)['len'] == 238 and 'Song length 3:58' in pg.inner_text('.toast'), 'Set saves the length')

    # the pencil: title and artist in place, Edit lyrics, Marks, Done
    ok(pg.locator('.ckerow [data-a=ckHeadLyrics]').count() == 1 and pg.locator('.ckerow [data-a=ckHeadMarks]').count() == 1 and
       pg.locator('.ckerow [data-a=ckHeadDone]').count() == 1, 'the pencil row has Edit lyrics, Marks and Done')
    pg.fill('#ckTitle', 'harbour song'); pg.fill('#ckArtist', 'the lights')
    pg.click('[data-a=ckHeadDone]'); pg.wait_for_timeout(300)
    s = pg.evaluate("songById(U.songId)")
    ok(s['name'] == 'Harbour Song' and s['artist'] == 'The Lights', 'Done saves the title and artist (capitalised like the rest of the app)')
    ok(pg.inner_text('.ckart').replace(' ', ' ').strip() == 'The Lights · 3:58', 'the header reads "Artist · 3:58": ' + pg.inner_text('.ckart'))
    pg.click('.ckart [data-a=ckLen]'); pg.wait_for_timeout(250)
    ok(pg.locator('#ckpk').count() == 1 and pg.inner_text('#ckpOut') == '3:58', 'tapping the length opens the picker on it')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    ok(pg.locator('#ckpk').count() == 0, 'Escape closes the picker')
    pg.click('#barR [data-a=ckPencil]'); pg.wait_for_timeout(250); pg.click('[data-a=ckHeadLyrics]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.sEdit") == 'lyrics', 'Edit lyrics opens the lyrics editor')
    pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)

    # ---------- the ⋯ controls grid ----------
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(300)
    labels = pg.evaluate("[...document.querySelectorAll('.sheet .cktile .cktl2')].map(e=>e.childNodes[0].textContent)")
    ok(labels == ['Add a track to time this song', 'Check timing', 'Key', 'Marks while playing', 'Blur ahead', 'Snapping', 'Stay awake', 'Lyrics', 'Add track'],
       'the grid has nine tiles (Q05: Sync again is retired; without the track, Timing reads Add a track to time this song): ' + ', '.join(labels))
    on = pg.evaluate("[...document.querySelectorAll('.sheet .cktile.on')].map(e=>e.dataset.v)")
    ok(on == ['marks', 'blur', 'snap', 'awake'], f'blue means on: Marks while playing, Blur ahead, Snapping and Stay awake start on ({on})')
    ok(pg.inner_text('.sheet [data-v=marks] small') == 'Breaths only', 'Marks while playing shows its value, Breaths only by default')
    ok(pg.locator('.sheet [data-v=snap] .ckab').inner_text() == 'A', 'Snapping has its A badge when on')
    t.shot(pg, 'grid')
    pg.click('.sheet [data-a=ckGridEdit]'); pg.wait_for_timeout(200)
    ok('2 of 3 pinned' in pg.inner_text('.sheet') and pg.locator('.sheet .ckpb.on').count() == 2, 'Edit shows what is pinned')
    pg.click('.sheet [data-a=ckTile][data-v=check]'); pg.wait_for_timeout(200)
    ok('3 of 3 pinned' in pg.inner_text('.sheet'), 'tapping a tile in Edit pins it')
    pg.click('.sheet [data-a=ckTile][data-v=blur]'); pg.wait_for_timeout(200)
    ok('3 is the most' in pg.inner_text('.toast') and '3 of 3 pinned' in pg.inner_text('.sheet'), 'no more than 3 can be pinned')
    pg.click('.sheet [data-a=ckTile][data-v=key]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=ckGridEdit]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(300)
    pins = pg.evaluate("[...document.querySelectorAll('.ckrow .ckpi')].map(b=>b.dataset.v||b.dataset.a)")
    ok(pins == ['timing', 'check', 'ckGrid'], f'the pinned icons follow (Key unpinned, Check timing pinned): {pins}')
    ok(pg.get_attribute('.ckrow [data-v=timing]', 'aria-label') == 'Add a track to time this song' and
       pg.locator('.ckrow [data-v=timing][aria-pressed]').count() == 0, 'the pinned Timing icon reads Add a track to time this song, and isn\'t a switch')
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=ckTile][data-v=snap]'); pg.wait_for_timeout(200)
    ok(pg.locator('.sheet [data-v=snap].on').count() == 0 and pg.locator('.sheet [data-v=snap] .ckab').count() == 0, 'Snapping turns off')
    pg.click('.sheet [data-a=ckTile][data-v=snap]'); pg.wait_for_timeout(150)
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(250)

    # ---------- Q05: timing needs the song's track ----------
    # an older song's saved timing, with no track on this device: kept, shown on Check timing, no play-along
    pg.evaluate(SPREAD, [sid, [0, 12, 24, 36]])
    keep0 = tl(pg)
    ok(pg.get_attribute('.ckrow [data-v=timing]', 'aria-label') == 'Add a track to time this song', 'with timing but no track, Timing still asks for the track')
    pg.click('.ckrow [data-a=ckTile][data-v=check]'); pg.wait_for_timeout(300)
    txt = pg.inner_text('#app')
    ok(pg.locator('.ckr').count() == 8 and 'Play-along needs the song’s track' in txt and pg.locator('#app [data-a=ckAddTrack]').count() == 1,
       'Check timing shows the saved timing, and says play-along needs the track')
    pg.click('#barL [data-a=ckCheckBack]'); pg.wait_for_timeout(300)
    pg.evaluate("ckOn(songById(U.songId))"); pg.wait_for_timeout(200)
    ok(not pg.evaluate("CLOCK.state().on") and pg.locator('#ckpa:not([hidden])').count() == 0, 'no play-along on the app\'s own clock without the track')
    ok(tl(pg) == keep0, 'and the saved timing is untouched')
    pg.evaluate("(()=>{const s=songById(U.songId);delete s.timing.slots;s.timing.est=false;save();rerender()})()")
    # the pinned Timing icon opens the track picker (the same door as the song's Track row)
    give_track(pg, sid)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate(f"TRACK.has('{sid}')"), 'the pinned Timing icon opens the file picker; the track is added and its player opens, as Add track does')
    loaded(pg, sid)
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(350)
    ok(pg.get_attribute('.ckrow [data-v=timing]', 'aria-label') == 'Timing', 'with the track, the icon is Timing again')
    # Timing on an untimed song with its track: straight to the track player, to place lines on the waveform
    pg.click('.ckrow [data-a=ckTile][data-v=timing]'); pg.wait_for_timeout(400)
    loaded(pg, sid)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("TRACK.level()") == 1 and pg.locator('#trkLane').count() == 1,
       'Timing on an untimed song opens the track player in Line view, with the line lane under the waveform')
    ok(pg.evaluate("TRACK.laneSel()") == 0 and pg.locator('#trkInfo [data-a=trkLnStart]').count() == 1,
       'the first line is selected, with Start here and End here')
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.view") == 'lyr', 'Back returns to the song')

    # ---------- Check timing ----------
    pg.evaluate(SPREAD, [sid, [0, 12, 24, 36]])
    pg.click('.ckrow [data-a=ckTile][data-v=check]'); pg.wait_for_timeout(300)
    T = tl(pg)
    M = model(pg)
    starts = [M['T'][i][0] for i in range(len(M['L'])) if i == 0 or M['L'][i]['k'] != M['L'][i - 1]['k']]
    ok([round(x, 2) for x in starts] == [0, 12, 24, 36], f'each section starts where it was set: {starts}')
    ok(T['est'] is True and all(s['anch'] for s in T['slots'].values()) and all(M['est']), 'the lines are an estimate, every line estimated, and every section start is set')
    ok(len(T['slots']) == 4 and len(set(T['slots'].keys())) == 4, 'timing is kept per place in the running order (Chorus 2 has its own times)')
    v1 = [M['T'][i] for i in range(len(M['L'])) if M['L'][i]['k'] == 0]
    d0, d1 = v1[0][1] - v1[0][0], v1[1][1] - v1[1][0]
    syl = pg.evaluate("CLOCK.model().L.slice(0,2).map(l=>l.syl.reduce((a,b)=>a+b,0))")
    ok(abs(d0 / d1 - syl[0] / syl[1]) < 0.02, f'lines share a section by syllables ({d0:.2f}/{d1:.2f} vs {syl})')
    ok(abs(v1[1][1] - 11.0) < 0.01, f'a section\'s last line ends a second before the next section ({v1[1][1]})')
    txt = pg.inner_text('main')
    ok('Song length' in txt and '3:58' in txt and '4 of 4 set' in txt and 'To-do markers' not in txt, 'Check timing: Song length, Section starts (4 of 4 set), no To-do row without markers')
    ok('Time each line' in txt and 'spread evenly' in txt, 'a note says the lines are spread evenly, with Time each line')
    ok(pg.locator('button.ckr').count() == 8 and pg.locator('.ckd.est').count() == 8 and pg.locator('.ckadot').count() == 4,
       'each line is a button, estimated lines have dashed bars, and a dot for each set start')
    ok(pg.locator('#app [data-a=ckSyncAgain]').count() == 0, 'no Sync again from the start')
    t.shot(pg, 'check', full_page=True)
    # a line row opens the player in Line view on that line (pushed), and Back comes back to Check timing
    pg.click('button.ckr[data-i="3"]'); pg.wait_for_timeout(400); loaded(pg, sid)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("TRACK.laneSel()") == 3 and abs(pg.evaluate("TRACK.now()") - M['T'][3][0]) < 0.05,
       'a line row opens the player with that line selected and the playhead on its start')
    ok(pg.evaluate("ZOOM.stack().slice(-1)[0].kind") == 'push', 'it\'s pushed in, like Check timing')
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.view") == 'ckCheck', 'Back returns to Check timing')
    pg.click('#app [data-a=ckRetime].sgpill'); pg.wait_for_timeout(350); loaded(pg, sid)
    ok(pg.evaluate("TRACK.laneSel()") == 0, 'Time each line opens the first estimated line')
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(300)
    pg.click('#app .row[data-a=ckRetime]'); pg.wait_for_timeout(350); loaded(pg, sid)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("TRACK.laneSel()") == 0, 'the Section starts row opens the player too')
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(300)
    # flags: very short and very long lines
    pg.evaluate("""(()=>{const s=songById(U.songId),o=s.order[0].o;s.timing.slots[o].lines=[[0,0.25],[0.3,20]];s.timing.slots[s.order[1].o].lines[0]=[21,24];save();rerender()})()""")
    txt = pg.inner_text('main')
    ok('Very short' in txt and 'Very long' in txt, 'Very short (under 0.4 s) and Very long (over 15 s) are flagged')
    pg.evaluate("(()=>{const s=songById(U.songId);s.timing.slots[s.order[2].o].marks=[1];save();rerender()})()")
    ok('To-do markers' in pg.inner_text('main') and pg.locator('.ckmk').count() == 1, 'To-do markers show when there are any, with a flag on the line')
    pg.click('[data-a=ckCheckDone]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'lyr', 'Done goes back to the song')

    # ---------- Q05 the line lane ----------
    pg.evaluate(SPREAD, [sid, [0, 12, 24, 36]])
    pg.evaluate(f"id=>CLOCK.retime(songById(id),1)", sid); pg.wait_for_timeout(400); loaded(pg, sid)
    M = model(pg)
    ok(pg.evaluate("TRACK.laneSel()") == 1, 'CLOCK.retime opens the player on a line')
    blocks = pg.evaluate("""(()=>{const c=document.getElementById('trkLC'),s=document.getElementById('trkC');
      return [c.getBoundingClientRect().left-s.getBoundingClientRect().left,c.getBoundingClientRect().width-s.getBoundingClientRect().width,c.height>0]})()""")
    ok(abs(blocks[0]) < 1.5 and abs(blocks[1]) < 1.5 and blocks[2], f'the lane lines up with the waveform ({blocks})')
    t.shot(pg, 'lane')
    # drag the end of line 1 (Counting boats…) where it meets nothing: estimated lines have gaps between them
    e1 = M['T'][1][1]
    pg.evaluate("TRACK.seek(%f)" % (e1 - 1)); pg.wait_for_timeout(150)
    x0 = lane_x(pg, e1); y = lane_y(pg)
    pg.mouse.move(x0, y); pg.mouse.down(); pg.mouse.move(x0 - 20, y, steps=6); pg.mouse.up(); pg.wait_for_timeout(250)
    M2 = model(pg)
    pps = pg.evaluate("document.getElementById('trkLC').getBoundingClientRect().width/16")
    ok(abs((e1 - M2['T'][1][1]) * pps - 20) < 4 or abs(M2['T'][1][1] - (e1 - 1)) < 0.02,
       f'dragging a block\'s edge moves it (or snaps to the playhead) ({e1:.2f} → {M2["T"][1][1]:.2f})')
    ok(not M2['est'][1] and all(M2['est'][i] for i in range(len(M2['est'])) if i != 1), 'that line is placed now (solid); the rest stay estimated')
    ok('Re-timed' in pg.inner_text('.toast') and pg.locator('.toast .ckub').count() == 1, 'with a toast and Undo')
    pg.click('.toast .ckub'); pg.wait_for_timeout(300)
    ok(abs(model(pg)['T'][1][1] - e1) < 0.002 and all(model(pg)['est']), 'Undo puts it back')
    # snapping: an edge dropped near the playhead lands on it
    pg.evaluate("TRACK.seek(%f)" % (e1 + 0.15)); pg.wait_for_timeout(150)
    x0 = lane_x(pg, e1)
    pg.mouse.move(x0, y); pg.mouse.down(); pg.mouse.move(x0 + 4, y, steps=4); pg.mouse.up(); pg.wait_for_timeout(250)
    ok(abs(model(pg)['T'][1][1] - (e1 + 0.15)) < 0.01, f'with Snapping on, an edge near the playhead snaps to it ({model(pg)["T"][1][1]:.3f})')
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(250)
    pg.evaluate("ckPref('snapping',false)")
    pg.evaluate("TRACK.seek(%f)" % (e1 + 0.15)); pg.wait_for_timeout(150)
    x0 = lane_x(pg, e1)
    pg.mouse.move(x0, y); pg.mouse.down(); pg.mouse.move(x0 + 4, y, steps=4); pg.mouse.up(); pg.wait_for_timeout(250)
    ok(abs(model(pg)['T'][1][1] - (e1 + 0.15)) > 0.02, 'with Snapping off, it stays where it was dropped')
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(250)
    pg.evaluate("ckPref('snapping',true)")
    # where two lines touch, one handle moves both
    pg.evaluate("""id=>{const s=songById(id),o=s.order[0].o;s.timing.slots[o].lines=[[1,4],[4,9]];s.timing.est=false;save();rerender()}""", sid)
    pg.wait_for_timeout(300); loaded(pg, sid)
    pg.evaluate("TRACK.seek(2)"); pg.wait_for_timeout(150)
    x0 = lane_x(pg, 4); y = lane_y(pg)
    pg.mouse.move(x0, y); pg.mouse.down(); pg.mouse.move(x0 + 25, y, steps=6); pg.mouse.up(); pg.wait_for_timeout(250)
    r = model(pg)['raw']
    ok(abs(r[0][1] - r[1][0]) < 0.002 and r[0][1] > 4.5, f'one handle moves the end of one line and the start of the next together ({r[0]}, {r[1]})')
    ok('Moved' in pg.inner_text('.toast'), 'with a toast and Undo')
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(250)
    # never past a neighbour
    x0 = lane_x(pg, 4)
    pg.mouse.move(x0, y); pg.mouse.down(); pg.mouse.move(x0 - 200, y, steps=8); pg.mouse.up(); pg.wait_for_timeout(250)
    r = model(pg)['raw']
    ok(r[0][1] >= r[0][0] + 0.1 - 1e-6 and r[1][0] >= r[0][0] + 0.1 - 1e-6, f'an edge never passes the line\'s other edge ({r[0]}, {r[1]})')
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(250)
    # tap a block to select it; Start here / End here at the playhead
    pg.evaluate("TRACK.seek(6)"); pg.wait_for_timeout(150)
    pg.mouse.click(lane_x(pg, 6.5), y); pg.wait_for_timeout(200)
    ok(pg.evaluate("TRACK.laneSel()") == 1 and 'Counting boats' in pg.inner_text('#trkInfo'), 'tapping a block selects it, named beside the time')
    pg.evaluate("TRACK.seek(5.2)"); pg.wait_for_timeout(100)
    pg.click('#trkInfo [data-a=trkLnStart]'); pg.wait_for_timeout(250)
    r = model(pg)['raw']
    ok(abs(r[1][0] - 5.2) < 0.01 and abs(r[1][1] - 9) < 0.01 and abs(r[0][1] - 4) < 0.01, f'Start here moves its start to the playhead ({r[1]})')
    pg.evaluate("TRACK.seek(8.4)"); pg.wait_for_timeout(100)
    pg.click('#trkInfo [data-a=trkLnEnd]'); pg.wait_for_timeout(250)
    r = model(pg)['raw']
    ok(abs(r[1][1] - 8.4) < 0.01, f'End here sets its end at the playhead ({r[1]})')
    pg.evaluate("TRACK.seek(4)"); pg.wait_for_timeout(100)
    pg.click('#trkInfo [data-a=trkLnEnd]'); pg.wait_for_timeout(250)
    ok('past the line’s start' in pg.inner_text('.toast') and abs(model(pg)['raw'][1][1] - 8.4) < 0.01, 'End here before the start says so and changes nothing')
    pg.click('#trkInfo [data-a=trkLnX]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("TRACK.laneSel()") == -1 and 'tap a line below to select it' in pg.inner_text('#trkInfo'), '✕ clears the selection')
    ok(pg.locator('#trkLane[data-own-gesture]').count() == 1, 'the lane has its own gesture, so a drag never swipes back')
    # the lane is in Phrase and Line only
    pg.click('#app .trklv button[data-v="2"]'); pg.wait_for_timeout(200)
    ok(pg.locator('#trkLane').count() == 0, 'Song view has no lane')
    pg.click('#app .trklv button[data-v="1"]'); pg.wait_for_timeout(200)
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(300)

    # ---------- play-along ----------
    pg.evaluate(SPREAD, [sid, [0, 12, 24, 36]])
    # Ivan's breath mark on the first line, a sing-as label and a run on the second
    pg.evaluate("""(()=>{const s=songById(U.songId),a=s.sections[s.order[0].sid].ann;a['0:2']={br:1};a['1:0']={v:'kow',run:1,up:1,nt:'Soft'};MARKS.fromAnn(s.sections[s.order[0].sid]);
      // long gaps after line 0 (which has a breath mark) and line 2 (which has none)
      const v=s.timing.slots[s.order[0].o].lines,c=s.timing.slots[s.order[1].o].lines;v[0][1]=v[0][0]+2;c[0][1]=c[0][0]+1.5;save();rerender()})()""")
    pg.click('.ckrow [data-a=ckTile][data-v=timing]'); pg.wait_for_timeout(300)
    st = pg.evaluate("CLOCK.state()")
    ok(st['on'] and not st['run'] and pg.locator('#ckpa:not([hidden])').count() == 1, 'Timing on a timed song with its track turns play-along on, waiting for the first line')
    ok('Tap the first line as it’s sung' in pg.inner_text('#ckpa .ckcap'), 'it says to tap the first line as it\'s sung')
    ok(pg.locator('#dock .cktr').count() == 1 and pg.locator('.cktr [data-a=ckNudge]').count() == 2 and pg.locator('.cktr #ckMute').count() == 1,
       'the transport capsule has −0.2, play and the time, +0.2 and the track\'s mute')
    ok(pg.locator('.cktr [data-a=ckRetimeNow]').count() == 1, 'paused, the last slot is Retime')
    ok(pg.locator('.ckrow [data-v=timing].on').count() == 1, 'the Timing icon is blue while play-along is on')
    wl0 = pg.evaluate("window.__wl.req")
    pg.click('#ckpa .ckl[data-i="0"]'); pg.wait_for_timeout(150)
    st = pg.evaluate("CLOCK.state()")
    ok(st['run'] and abs(pg.evaluate("CLOCK.now()")) < 0.01, 'tapping the first line starts the clock from it')
    ok(pg.evaluate("NOW.kind()") == 'clock', '3.20: play-along starts through the one sound owner, so anything else playing stops')
    ok(pg.evaluate("window.__wl.req") == wl0 + 1 and st['wake'], 'Stay awake keeps the screen on while playing along')
    ok(pg.locator('.cktr [data-a=ckFlag]').count() == 1 and pg.locator('.cktr [data-a=ckRetimeNow]').count() == 0, 'playing, the same slot is Flag')
    ok('hold to fix it' in pg.inner_text('#ckpa .ckcap'), 'the caption mentions holding to fix a line')
    pg.evaluate("CLOCK.advance(1)"); pg.wait_for_timeout(150)
    cur = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].findIndex(l=>l.classList.contains('now'))")
    ok(cur == 0, 'the current line is the first')
    fill = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl.now .ckw')].map(w=>+w.style.getPropertyValue('--p'))")
    ok(fill[0] == 1 and fill[-1] == 0 and 0 <= fill[2] <= 1, f'its words fill as they\'re sung ({fill})')
    box = pg.evaluate("(()=>{const v=document.querySelector('#ckpa .ckview'),l=document.querySelector('#ckpa .ckl.now');return [v.getBoundingClientRect().top,v.clientHeight,l.getBoundingClientRect().top]})()")
    ok(abs(box[2] - box[0] - box[1] * 0.3) < 3, f'the current line sits at about 30% of the view ({box})')
    pg.evaluate("CLOCK.advance(11.5)"); pg.wait_for_timeout(150)
    cls = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].map(l=>l.className.replace('ckl ','').replace(' nx',''))")
    ok(cls[:4] == ['past', 'past', 'now', 'fut'], f'past lines dim, the current one is clear, and upcoming lines wait ({cls[:4]})')
    blur = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl.fut')].slice(0,3).map(l=>l.style.filter)")
    ok(blur[0] and blur[0] != blur[1] and all('blur' in b for b in blur), f'Blur ahead: upcoming lines blur more with distance ({blur})')
    ok(max(float(b[5:-3]) for b in pg.evaluate("[...document.querySelectorAll('#ckpa .ckl.fut')].map(l=>l.style.filter)")) <= 1.5,
       'never more than 1.5 px, as on the lyrics page')
    ok(float(pg.evaluate("document.querySelector('#ckpa .ckl.past').style.opacity")) < 0.5, 'past lines are dimmed')
    t.shot(pg, 'play')
    ok(pg.locator('#ckpa .ckl[data-i="0"] .ckbr').count() == 1, 'Breaths only: Ivan\'s breath mark shows on its line')
    ok(pg.locator('#ckpa .ckl[data-i="0"] .ckdot').count() == 0, 'no automatic dot on a line that has his breath mark')
    ok(pg.locator('#ckpa .v, #ckpa .run, #ckpa .m, #ckpa .sgnote').count() == 0 and 'kow' not in pg.inner_text('#ckpa'),
       'sing-as labels, runs, pitch arrows and notes are hidden while playing')
    M = model(pg)
    gaps = [(M['T'][i + 1][0] - (M['T'][i][1]), i) for i in range(len(M['L']) - 1)]
    dots = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].filter(l=>l.querySelector('.ckdot')).map(l=>+l.dataset.i)")
    want = [i for g, i in gaps if g > 1.2 and i != 0]
    ok(dots == want and len(dots) > 0, f'an automatic dot only on lines with a gap over 1.2 s and no breath mark ({dots} vs {want})')
    pg.click('#ckpa .ckl[data-i="5"]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("CLOCK.now()") - M['T'][5][0]) < 0.01 and pg.evaluate("document.querySelector('#ckpa .ckl.now').dataset.i") == '5',
       'tapping any line jumps the clock there')
    before = pg.evaluate("CLOCK.model().T.map(x=>x[0])")
    pg.click('.cktr [data-v="0.2"]'); pg.wait_for_timeout(150)
    after = pg.evaluate("CLOCK.model().T.map(x=>x[0])")
    ok(all(abs(a - b - 0.2) < 0.002 for a, b in zip(after, before)), '+0.2 moves every line 0.2 s later')
    ok('Lyrics 0.2 s later' in pg.inner_text('.toast') and pg.locator('.toast .ckub').count() == 1, 'with a toast and Undo')
    saved = json.loads(pg.evaluate("localStorage.getItem('vocalTracker')"))
    ok(any(s.get('timing') and s['timing'].get('slots') and abs(list(s['timing']['slots'].values())[0]['lines'][0][0] - 0.2) < 0.002 for s in saved['songs']), 'the nudge is saved')
    pg.click('.toast .ckub'); pg.wait_for_timeout(150)
    ok(pg.evaluate("CLOCK.model().T.map(x=>x[0])") == before and pg.evaluate("CLOCK.state().run"), 'Undo puts the lyrics back (and the clock keeps running)')
    pg.click('.cktr [data-v="-0.2"]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("CLOCK.model().T[3][0]") - (before[3] - 0.2)) < 0.002, '−0.2 moves every line earlier')
    pg.click('.toast .ckub'); pg.wait_for_timeout(150)

    # ---------- Q05 punch-in ----------
    M = model(pg)
    pg.evaluate("document.querySelector('#ckpa .ckl[data-i=\"2\"]').click()"); pg.wait_for_timeout(100)
    pg.evaluate("CLOCK.advance(0.9)")  # just after line 2 starts
    t_press = pg.evaluate("CLOCK.now()")
    lb3 = pg.locator('#ckpa .ckl[data-i="2"]').bounding_box()
    pg.mouse.move(lb3['x'] + 40, lb3['y'] + 10); pg.mouse.down(); pg.wait_for_timeout(650)
    ok(pg.evaluate("CLOCK.state().punch") and pg.locator('#ckpa .ckl.punch[data-i="2"]').count() == 1 and 'Let go when' in pg.inner_text('#ckpa .ckcap'),
       'holding the lyrics half a second punches in on the line nearest the press, and says when to let go')
    pg.evaluate("CLOCK.advance(2.5)")
    pg.mouse.up(); pg.wait_for_timeout(250)
    r = model(pg)
    ok(abs(r['raw'][2][0] - (t_press - 0.15)) < 0.01 and abs(r['raw'][2][1] - (t_press + 2.5 - 0.15)) < 0.01,
       f'the line starts where the finger went down and ends where it let go (less the finger\'s 0.15 s) ({r["raw"][2]} vs {t_press:.2f})')
    ok(not r['est'][2] and r['est'][3], 'that line is placed; the others stay estimated')
    ok('Re-timed “Hold on hold on to the sound”' in pg.inner_text('.toast') and pg.locator('.toast .ckub').count() == 1, 'a toast says Re-timed, with Undo')
    ok(pg.evaluate("CLOCK.state().run") and pg.evaluate("document.querySelector('#ckpa .ckl.now')") is not None, 'play-along carries on')
    pg.click('.toast .ckub'); pg.wait_for_timeout(200)
    ok(abs(model(pg)['raw'][2][0] - M['raw'][2][0]) < 0.002, 'Undo puts the line back')
    # a quick tap still jumps (no punch-in)
    pg.mouse.click(lb3['x'] + 40, lb3['y'] + 10); pg.wait_for_timeout(150)
    ok(not pg.evaluate("CLOCK.state().punch") and abs(pg.evaluate("CLOCK.now()") - M['T'][2][0]) < 0.05 and model(pg)['raw'] == M['raw'],
       'a quick tap still jumps to the line, changing nothing')

    # ---------- Q05 Flag ----------
    pg.evaluate("CLOCK.advance(1.3)")
    tf = pg.evaluate("CLOCK.now()")
    pg.click('.cktr [data-a=ckFlag]'); pg.wait_for_timeout(200)
    mk = pg.evaluate("JSON.parse(JSON.stringify(songById(U.songId).markers||[]))")
    ok(len(mk) == 1 and abs(mk[0]['t'] - (tf - 0.15)) < 0.02, f'Flag adds a marker on the track at the current time ({mk})')
    ok('Marker 1 at' in pg.inner_text('.toast') and pg.locator('.toast .ckub').count() == 1, 'with a toast and Undo')
    pg.click('.toast .ckub'); pg.wait_for_timeout(200)
    ok(not pg.evaluate("songById(U.songId).markers"), 'Undo takes the marker away')

    # pause shows the song page with the current line highlighted, where the eye was
    pg.evaluate("document.querySelector('#ckpa .ckl[data-i=\"2\"]').click()"); pg.evaluate("CLOCK.advance(1)"); pg.wait_for_timeout(100)
    y0 = pg.evaluate("document.querySelector('#ckpa .ckl.now').getBoundingClientRect().top")
    rel0 = pg.evaluate("window.__wl.rel")
    pg.click('.cktr [data-a=ckPP]'); pg.wait_for_timeout(300)
    ok(pg.locator('#ckpa:not([hidden])').count() == 0 and not pg.evaluate("CLOCK.state().run"), 'Pause shows the song page')
    cur = pg.evaluate("(()=>{const l=document.querySelector('.sgl.ckcur');return l&&[l.textContent,l.getBoundingClientRect().top]})()")
    ok(cur and cur[0] == 'Hold on hold on to the sound', f'the current line is highlighted on the song page ({cur})')
    ok(cur and abs(cur[1] - y0) < 4, f'and kept where the eye was ({y0:.0f} → {cur[1]:.0f}; scrollY, page, window, ckplay: ' +
       str(pg.evaluate("[scrollY,document.documentElement.scrollHeight,innerHeight,document.documentElement.classList.contains('ckplay')]")) + ')')
    ok(pg.evaluate("window.__wl.rel") == rel0 + 1 and not pg.evaluate("CLOCK.state().wake"), 'the wake lock is released on pause')
    t.shot(pg, 'paused')
    pg.click('.sgsec[data-o] >> nth=1'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sSec") is not None and pg.locator('.sgsec.sel').count() == 1, 'tap-to-focus sections still works while paused')
    pg.click('.sgsec.sel'); pg.wait_for_timeout(200)
    # Retime (paused): the player in Line view on the current line
    pg.click('.cktr [data-a=ckRetimeNow]'); pg.wait_for_timeout(400); loaded(pg, sid)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("TRACK.level()") == 1 and pg.evaluate("TRACK.laneSel()") == 2,
       'paused, Retime opens the player in Line view on the current line')
    ok(pg.evaluate("NOW.kind()") != 'clock' or not pg.evaluate("CLOCK.state().run"), 'play-along stays paused (one sound at a time)')
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.view") == 'lyr', 'Back returns to the song')
    pg.click('.cktr [data-a=ckPP]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("CLOCK.state().run") and pg.locator('#ckpa:not([hidden])').count() == 1, 'play carries on in the big view')

    # Marks while playing: Off hides breath marks and dots too; kept on this device, never in backups
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(200); pg.click('.sheet [data-a=ckTile][data-v=marks]'); pg.wait_for_timeout(200)
    ok(pg.inner_text('.sheet [data-v=marks] small') == 'Active layer', 'Marks while playing cycles to Active layer (Q03)')
    pg.click('.sheet [data-a=ckTile][data-v=marks]'); pg.wait_for_timeout(200)
    ok(pg.inner_text('.sheet [data-v=marks] small') == 'Off' and pg.locator('.sheet [data-v=marks].on').count() == 0, 'Marks while playing cycles to Off')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(250)
    ok(pg.locator('#ckpa .ckbr, #ckpa .ckdot').count() == 0, 'Off hides breath marks and automatic dots')
    prefs = json.loads(pg.evaluate("localStorage.getItem('vocalSongPrefs')"))
    ok(prefs.get('marksPlaying') == 'off' and prefs.get('pins') == ['timing', 'check'], f'the settings are kept in vocalSongPrefs ({prefs})')
    pg.evaluate("prepareExport(false,false)"); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    bk = pg.evaluate("pendingExport.file.text()")
    ok('marksPlaying' not in bk and 'blurAhead' not in bk and '"timing"' in bk, 'backups carry the timing but not the device settings')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(200)
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(200); pg.click('.sheet [data-a=ckTile][data-v=marks]'); pg.wait_for_timeout(150)
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(200)

    # the floating window: "Playing along · 1:24 · Verse 2", hidden on its own screen
    pg.evaluate("CLOCK.advance(1)")
    ok(pg.evaluate("FW.shown") is None, 'no play-along window on the song it plays from')
    pg.click('#barL [data-a=sgBack]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("FW.shown") == 'clock' and pg.locator('#fw:not([hidden])').count() == 1, 'leaving the song while playing along shows the floating window')
    fk = pg.inner_text('#fw .fwk'); ft = pg.inner_text('#fw .fwt')
    ok(fk == 'Playing along' and __import__('re').match(r'^\d:\d\d · (Verse|Chorus) \d$', ft), f'it says Playing along, the time and the section ({fk} / {ft})')
    ok(not pg.evaluate("CLOCK.state().wake") and pg.evaluate("CLOCK.state().run"), 'the clock keeps going, but the screen may sleep away from the song')
    order = pg.evaluate("FW_KINDS.map(k=>k.id)")
    ok(order == ['take', 'video', 'track', 'clock', 'session'], f'take → video → playing along → session ({order})')
    t.shot(pg, 'window')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    ok(not pg.evaluate("CLOCK.state().run") and 'Paused' in pg.inner_text('#fw .fwt'), 'its button pauses')
    pg.click('#fw [data-a=fwToggle]'); pg.wait_for_timeout(200)
    pg.evaluate("CLOCK.advance(3)"); pg.wait_for_timeout(100)
    t0 = pg.evaluate("CLOCK.now()")
    pg.click('#fw [data-a=fwOpen]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("FW.shown") is None and pg.locator('#ckpa:not([hidden])').count() == 1 and
       abs(pg.evaluate("CLOCK.now()") - t0) < 0.01, 'tapping it returns to the song, in step')
    pg.evaluate("CLOCK.off()"); pg.wait_for_timeout(200)
    ok(pg.locator('#ckpa:not([hidden])').count() == 0 and pg.locator('#dock .cktr').count() == 0 and not pg.evaluate("CLOCK.state().wake"),
       'turning Timing off leaves play-along')

    # ---------- Q05 the hold menu on a lyric line ----------
    line = '#app .sgl[data-o="%s"][data-li="1"]' % pg.evaluate("songById(U.songId).order[1].o")
    hold(pg, line)
    ok(pg.evaluate("CLOCK.lineMenu()") is not None and pg.locator('#lmenu [role=menuitem]').count() == 3,
       'holding a line half a second opens its menu: Retime line, Play from here, Annotate')
    ok([x.strip() for x in pg.evaluate("[...document.querySelectorAll('#lmenu button')].map(b=>b.textContent)")] == ['Retime line', 'Play from here', 'Annotate'],
       'in that order')
    ok(pg.locator(line + '.lifted').count() == 1 and pg.evaluate("document.body.classList.contains('lmopen')") and
       float(pg.evaluate("getComputedStyle(document.querySelector('#app .sgl:not(.lifted)')).opacity")) < 0.6, 'the line lifts and the others dim')
    ok(pg.evaluate("U.sSec") is None, 'the hold doesn\'t also focus the section')
    t.shot(pg, 'hold-menu')
    pg.click('.ctxback'); pg.wait_for_timeout(200)
    ok(pg.evaluate("CLOCK.lineMenu()") is None and pg.locator('#lmenu').count() == 0 and pg.locator('.sgl.lifted').count() == 0, 'tapping away closes it')
    # a short press is still a tap (section focus), and a moving finger (a scroll) never opens it
    pg.mouse.move(*[pg.locator(line).bounding_box()[k] + 20 for k in ('x', 'y')]); pg.mouse.down(); pg.wait_for_timeout(100); pg.mouse.up(); pg.wait_for_timeout(300)
    ok(pg.evaluate("CLOCK.lineMenu()") is None and pg.evaluate("U.sSec") is not None, 'a quick tap focuses the section as before')
    pg.click('.sgsec.sel'); pg.wait_for_timeout(200)
    bx = pg.locator(line).bounding_box()
    pg.mouse.move(bx['x'] + 20, bx['y'] + 10); pg.mouse.down(); pg.mouse.move(bx['x'] + 20, bx['y'] + 60, steps=5); pg.wait_for_timeout(600); pg.mouse.up(); pg.wait_for_timeout(200)
    ok(pg.evaluate("CLOCK.lineMenu()") is None, 'moving the finger lets the hold go')
    # Retime line
    hold(pg, line); pg.click('#lmenu [data-a=ckLmRetime]'); pg.wait_for_timeout(400); loaded(pg, sid)
    ok(pg.evaluate("U.view") == 'trk' and pg.evaluate("TRACK.laneSel()") == 3, 'Retime line opens the player on that line')
    pg.click('#barL [data-a=trkBack]'); pg.wait_for_timeout(350)
    # Play from here
    hold(pg, line); pg.click('#lmenu [data-a=ckLmPlay]'); pg.wait_for_timeout(300)
    M = model(pg)
    ok(pg.evaluate("CLOCK.state().run") and abs(pg.evaluate("CLOCK.now()") - M['T'][3][0]) < 0.05 and pg.evaluate("NOW.kind()") == 'clock',
       'Play from here starts play-along from that line')
    pg.click('.cktr [data-a=ckPP]'); pg.wait_for_timeout(250)
    pg.evaluate("CLOCK.off()"); pg.wait_for_timeout(200)
    # Annotate: the Marks side, the whole line selected, the last-used layer
    pg.evaluate("MARKS.setLayer('words')")
    hold(pg, line); pg.click('#lmenu [data-a=ckLmMark]'); pg.wait_for_timeout(350)
    sel = pg.evaluate("SG.sel")
    ok(pg.evaluate("U.sEdit") == 'annotate' and sel and sel['li'] == 1 and sel['w0'] == 0 and sel['w1'] == 7 and pg.evaluate("MARKS.layer()") == 'words'
       and pg.locator('#mksheet').count() == 1, f'Annotate opens the Marks side with the whole line selected, on the last-used layer ({sel})')
    pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)
    # not in Recall, where a hold peeks
    pg.evaluate("U.sMode='recall';U.sHint=2;rerender()"); pg.wait_for_timeout(300)
    hold(pg, '#app .sgl[data-li="1"] >> nth=1')
    ok(pg.evaluate("CLOCK.lineMenu()") is None and pg.locator('#lmenu').count() == 0, 'no hold menu in Recall')
    pg.evaluate("U.sMode='practise';U.sHint=0;rerender()"); pg.wait_for_timeout(300)

    # ---------- Q05 suggested breaths ----------
    pg.evaluate("""id=>{const s=songById(id),o=s.order[0].o,c=s.order[1].o;
      ckSetLines(s,{0:[0,2],1:[3,6]},true);ckSetLines(s,{2:[7,8.5]},true)}""", sid); pg.wait_for_timeout(200)
    T = tl(pg)
    o0 = pg.evaluate("songById(U.songId).order[0].o")
    sbs = {k: v.get('sb') for k, v in T['slots'].items() if v.get('sb')}
    ok(sbs == {o0: [1]}, f'a gap after a placed line (Verse 1 line 2 ends at 6 s, the chorus starts at 7 s) is stored as a suggested breath ({sbs})')
    ok(0 not in (T['slots'][o0].get('sb') or []), 'not on a line that already has a breath mark of Ivan\'s (Verse 1 line 1), nor where lines touch')
    pg.evaluate("SG_ACT.sgEdit()"); pg.evaluate("MARKS.setLayer('phrasing');rerender()"); pg.wait_for_timeout(300)
    ok(pg.locator('.sgsb').count() == 1 and pg.locator(f'.sgl[data-o="{o0}"][data-li="1"] .sgsb').count() == 1,
       'in Phrasing on the Marks side, a faint dashed ’ + sits at that line\'s end')
    pg.evaluate("MARKS.setLayer('notes');rerender()"); pg.wait_for_timeout(200)
    ok(pg.locator('.sgsb').count() == 0, 'not on other layers')
    pg.evaluate("MARKS.setLayer('phrasing');rerender()"); pg.wait_for_timeout(200)
    t.shot(pg, 'suggested-breath')
    pg.click('.sgsb'); pg.wait_for_timeout(300)
    sec = pg.evaluate("(()=>{const s=songById(U.songId);return s.sections[s.order[0].sid]})()")
    ok(any(m['type'] == 'breath' and m['line'] == 1 and m['w0'] == len(sec['lines'][1]) - 1 for m in sec['marks']),
       'tapping it makes a real Breath mark on the line\'s last word')
    ok(pg.locator('.sgsb').count() == 0 and not (tl(pg)['slots'][o0].get('sb')), 'and the suggestion goes')
    ok('Added Breath' in pg.inner_text('.toast') and pg.locator('.toast .ckub').count() == 1, 'with Undo')
    pg.click('.toast .ckub'); pg.wait_for_timeout(300)
    ok(pg.locator('.sgsb').count() == 1, 'Undo brings the suggestion back')
    pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)
    ok(pg.locator('.sgsb').count() == 0, 'never outside the Marks side')

    # ---------- lyric edits: only changed lines lose their time ----------
    before = pg.evaluate("CLOCK.model().raw")
    v2 = pg.evaluate("songById(U.songId).order[2].sid")
    pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(200)
    pg.evaluate("U.sEdit='lyrics';rerender()"); pg.wait_for_timeout(300)
    pg.evaluate(f"""()=>{{const e=document.querySelector('.lyred[data-k="{v2}"]');e.innerText='Paper maps and a borrowed coat\\nSomebody else on the radio';}}""")
    pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)
    raw = pg.evaluate("CLOCK.model().raw")
    o2 = pg.evaluate("songById(U.songId).order[2].o")
    ok(raw[4] == before[4] and raw[5] == [None, None] and raw[:4] == before[:4] and raw[6:] == before[6:], 'editing a line clears only that line\'s time')
    ok(tl(pg)['slots'][o2]['marks'] == [1], f'and gives it a to-do marker ({tl(pg)["slots"][o2]})')
    M = model(pg)
    ok(M['T'][4][1] < M['T'][5][0] < M['T'][6][0] and M['est'][5], 'play-along spreads it between its neighbours meanwhile (estimated)')
    # placing it again clears its to-do marker
    pg.evaluate("s=>ckSetLines(songById(s),{5:[CLOCK.model().T[5][0],null]},true)", sid)
    ok(tl(pg)['slots'][o2]['marks'] == [], 'placing the line again clears its to-do marker')

    # ---------- the timing maths ----------
    maths = pg.evaluate("""(()=>{const L=[{syl:[1,1]},{syl:[1,1,1,1,1,1,1,1]},{syl:[1]}];
      const a=ckEnd(L,[[0,null],[2,null],[9,null]],0), b=ckEnd(L,[[0,null],[5,null],[9,null]],1), c=ckEnd(L,[[0,null],[2,null],[9,null]],2);
      const T=ckOrder([[5,6],[5.05,9],[4,4.02]]);
      return {a,b,c,T}})()""")
    ok(maths['a'] == 1.2 and maths['c'] == 9 + 1.2, 'a line with no end lasts 0.3 s a syllable, at least 1.2 s')
    ok(maths['b'] == 7.4, 'a missing end stops at the next line\'s start, or after its estimate (8 syllables: 2.4 s)')
    T = maths['T']
    ok(T[0][1] <= T[1][0] and abs(T[1][0] - 5.1) < 1e-6 and abs(T[2][0] - 5.2) < 1e-6 and abs(T[2][1] - 5.3) < 1e-6,
       f'lines stay in order: each starts at least 0.1 s after the last, the previous end is trimmed, and every line lasts at least 0.1 s ({T})')
    w = pg.evaluate("(()=>{const f=ckWarp([[10,12],[20,30]]);return [f(5),f(10),f(15),f(20),f(25)]})()")
    ok(w == [7, 12, 21, 30, 35], f'stretching between set starts is piecewise, with a plain shift outside them ({w})')
    # an estimated song stops being estimated once every line has been placed
    pg.evaluate(SPREAD, [sid, [0, 12, 24, 36]])
    pg.evaluate("s=>{const sg=songById(s),M=ckModel(sg);const ch={};M.T.forEach((r,i)=>{if(i<M.T.length-1)ch[i]=[r[0],r[1]]});ckSetLines(sg,ch,true)}", sid)
    ok(tl(pg)['est'] is True and sum(model(pg)['est']) == 1, 'with one line left to place, the song is still estimated')
    pg.evaluate("s=>{const sg=songById(s),M=ckModel(sg),n=M.T.length-1;ckSetLines(sg,{[n]:[M.T[n][0],M.T[n][1]]},true)}", sid)
    T = tl(pg)
    ok(T['est'] is False and not any('fix' in s for s in T['slots'].values()) and not any(model(pg)['est']),
       'once every line has its own start, the song stops being estimated')
    t.shot(pg, 'song-synced')

    # ---------- data: upgrade, damaged timing, backups ----------
    old = sample(); old['schema'] = 2
    old['songs'] = [{"id": "g_1", "name": "Old Song", "artist": "", "pinned": False, "added": 1,
                     "sections": {"x1": {"label": "Verse", "cue": "", "lines": [["One", "two"], ["Three", "four"]], "ann": {}, "orphans": []}},
                     "order": [{"o": "o1", "sid": "x1"}, {"o": "o2", "sid": "x1"}]}]
    p2 = t.page(b, data=old)
    ok(p2.evaluate("D.schema") >= 3 and 'timing' not in p2.evaluate("D.songs[0]"), 'data from before 3.18 upgrades past schema 3, and its songs have no timing (not synced)')
    bad = copy.deepcopy(old); bad['schema'] = 3
    bad['songs'][0]['timing'] = {"len": "x", "real": 1, "est": True, "slots": {
        "o1": {"lines": [[1, 2], [0.5, 9], "junk", [4, 3]], "anch": True, "marks": [1, 7, 'a', 1], "fix": [0, 5, 'x'], "sb": [0, 1, 1, -2]},
        "o2": {"lines": [[10, 30], [12, 13]], "anch": "yes", "marks": [], "sb": "nope"},
        "o9": {"lines": [[1, 2]]}, "o3": "nope"}}
    bad['songs'].append({"id": "g_2", "name": "Broken", "artist": "", "timing": [1, 2, 3],
                         "sections": {"x1": {"label": "Verse", "cue": "", "lines": [["Hi"]], "ann": {}, "orphans": []}}, "order": [{"o": "o1", "sid": "x1"}]})
    p3 = t.page(b, data=bad)
    tm = p3.evaluate("D.songs[0].timing")
    ok(p3.evaluate("D.songs.length") == 2 and p3.evaluate("D.songs[0].sections.x1.lines.length") == 2, 'damaged timing never breaks a song')
    ok(tm['len'] is None and tm['real'] is False and tm['slots']['o1']['lines'] == [[1, 2], [None, None]] and tm['slots']['o1']['marks'] == [1],
       f'out-of-order lines, junk and extra lines are dropped, markers checked ({tm["slots"]["o1"]})')
    ok(tm['slots']['o1'].get('fix') == [0] and tm['slots']['o1'].get('sb') == [0] and 'sb' not in tm['slots']['o2'],
       f'Q05: placed lines and suggested breaths are checked (in range, no repeats, only on timed lines) ({tm["slots"]["o1"]})')
    ok(tm['slots']['o2']['lines'] == [[10, 12], [12, 13]] and tm['slots']['o2']['anch'] is False, 'an overlapping end is trimmed to the next start; a bad set start is dropped')
    ok('o9' not in tm['slots'] and 'o3' not in tm['slots'], 'timing for places no longer in the running order is dropped')
    ok('timing' not in p3.evaluate("D.songs[1]"), 'timing that isn\'t an object is dropped')
    # a suggested breath on a line that has a breath mark of Ivan's goes
    sb2 = p3.evaluate("""(()=>{const s=JSON.parse(JSON.stringify(D.songs[0]));s.sections.x1.marks=[{id:'b1',L:'phrasing',type:'breath',opt:'',line:0,w0:1,w1:1,text:''}];
      return cleanSong(s).timing.slots.o1.sb||null})()""")
    ok(sb2 is None, 'a suggested breath goes once its line has a breath mark')
    p3.evaluate("(()=>{U.tab='songs';U.view='lyr';U.songId='g_1';render()})()"); p3.wait_for_timeout(300)
    ok(p3.evaluate("CLOCK.synced(songById('g_1'))") and p3.locator('.ckrow').count() == 1, 'the song still opens with what was kept')
    p3.close(); p2.close()
    # a backup round trip keeps the timing, with its placed lines and suggested breaths
    pg.evaluate(SPREAD, [sid, [0, 12, 24, 36]])
    pg.evaluate("s=>ckSetLines(songById(s),{1:[3,5]},true)", sid)
    pg.evaluate("s=>ckSetLines(songById(s),{2:[7,9]},true)", sid)
    keep = tl(pg)
    ok(any(s.get('fix') for s in keep['slots'].values()) and any(s.get('sb') for s in keep['slots'].values()), f'the timing has placed lines and a suggested breath ({keep["slots"]})')
    pg.evaluate("prepareExport(true,false)"); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    text = pg.evaluate("pendingExport.file.text()")
    pg.evaluate("(()=>{songById(U.songId).timing={len:5,real:false,est:false,slots:{}};save()})()")
    pg.evaluate("async t=>{pendingImport=await inspectBackup(t,'b.json',t.length);await restoreImport()}", text)
    pg.wait_for_function("!U.sheet||U.sheet!=='importing'", timeout=10000); pg.wait_for_timeout(600)
    back = pg.evaluate("JSON.parse(JSON.stringify(D.songs.find(s=>s.name==='Harbour Song').timing))")
    ok(back == keep, f'a backup and restore keeps the timing exactly ({back} vs {keep})')
    ok(pg.evaluate(f"TRACK.has('{sid}')"), 'and the track stays on the device (tracks are never in backups)')

    # ---------- every size, light and dark ----------
    sizes = [(375, 667, 'light'), (390, 844, 'dark'), (852, 393, 'light'), (820, 1180, 'dark'), (1440, 900, 'light'), (320, 568, 'dark')]
    for w, h, sc in sizes:
        p = t.page(b, w=w, h=h, sc=sc, touch=w < 1400)
        p.evaluate("CLOCK.fake(10000)"); p.evaluate(QUIET)
        sid2 = song(p)
        home = "(()=>{if(split()){U.tab='songs';U.view=null}else{U.tab='songs';U.view='lyr'}render()})()"
        p.evaluate(home); p.wait_for_timeout(250)
        nm = f'{w}x{h} {sc}'
        probs = []
        def side(where):
            if p.evaluate("document.documentElement.scrollWidth") > w + 1: probs.append('sideways scroll on ' + where)
        side('the song')
        if p.locator('.ckrow').count() != 1: probs.append('no header row')
        p.click('[data-a=ckGrid]'); p.wait_for_timeout(250); side('the grid')
        gr = p.locator('.sheet .ckgrid').bounding_box()
        if not gr or gr['width'] > w: probs.append('grid too wide')
        p.click('.sheet [data-a=close]'); p.wait_for_timeout(250)
        p.evaluate("id=>TRACK.expect(id)", sid2); p.set_input_files('#trackIn', F('Harbour.wav', 60))
        p.wait_for_function("id=>TRACK.has(id)&&!TRACK.busy()", arg=sid2, timeout=15000); p.wait_for_timeout(300)
        p.evaluate(SPREAD, [sid2, [0, 12, 24, 36]])
        p.evaluate("id=>CLOCK.retime(songById(id),2)", sid2); p.wait_for_timeout(400); loaded(p, sid2); side('the line lane')
        lb2 = p.locator('#trkInfo').bounding_box(); ln2 = p.locator('#trkLane').bounding_box()
        if not ln2 or ln2['height'] < 40: probs.append('no lane')
        if not lb2 or lb2['x'] + lb2['width'] > w + 1: probs.append('lane row too wide')
        if p.locator('#trkInfo [data-a=trkLnEnd]').count() != 1: probs.append('no End here')
        if w == 375 or w == 820: t.shot(p, f'lane-{sc}-{w}')
        p.evaluate("id=>{CK.ret=null;ckOpenCheck(songById(id))}", sid2); p.wait_for_timeout(350); side('Check timing')
        if w == 375 or w == 390: t.shot(p, f'check-{sc}-{w}', full_page=True)
        p.click('[data-a=ckCheckDone]'); p.wait_for_timeout(300)
        p.evaluate("id=>{U.songId=id}", sid2); p.evaluate(home); p.wait_for_timeout(250)
        p.click('.ckrow [data-a=ckTile][data-v=timing]'); p.wait_for_timeout(250)
        p.click('#ckpa .ckl[data-i="0"]'); p.evaluate("CLOCK.advance(3)"); p.wait_for_timeout(200); side('play-along')
        tr = p.locator('#dock .cktr').bounding_box(); pa = p.locator('#ckpa').bounding_box()
        if not tr or tr['y'] + tr['height'] > h: probs.append('transport off screen')
        if not tr or tr['x'] < 0 or tr['x'] + tr['width'] > w: probs.append('transport too wide')
        if not pa or pa['width'] < 200: probs.append('play-along view missing')
        if p.evaluate("!!document.querySelector('#dock .cktr')") is not True: probs.append('transport not in the dock')
        fl = p.locator('.cktr [data-a=ckFlag]').bounding_box()
        if not fl or fl['width'] < 44 or fl['x'] + fl['width'] > w: probs.append('no Flag in reach')
        if w == 375 or w == 820: t.shot(p, f'play-{sc}-{w}')
        p.click('.cktr [data-a=ckPP]'); p.wait_for_timeout(250); side('paused')
        if p.locator('.sgl.ckcur').count() != 1: probs.append('no current line when paused')
        if p.locator('.cktr [data-a=ckRetimeNow]').count() != 1: probs.append('no Retime when paused')
        if w == 375: t.shot(p, f'paused-{sc}')
        ok(not probs, f'{nm}: header, grid, the line lane, Check timing and play-along fit ({"; ".join(probs) or "ok"})')
        p.close()
