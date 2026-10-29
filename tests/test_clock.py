"""3.18 Song Clock (phase A1): the song header's length and picker, the controls grid and pinned icons, Sync by
sections (with a test clock that only moves when told), spreading lines by syllables, the timing maths, play-along
(current line, jumping, nudges with Undo, pausing onto the song page), Marks while playing, Check timing, the pencil,
lyric edits, the floating window, data upgrades, damaged timing, backups, the wake lock, and every size in light
and dark."""
import json, copy
from harness import sample, ready, OUT, now, iso

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


def song(pg):
    sid = pg.evaluate(ADD, ['Harbour', 'Harbour Lights', LYR]); pg.wait_for_timeout(400)
    return sid


def tl(pg):
    return pg.evaluate("JSON.parse(JSON.stringify(songById(U.songId).timing||null))")


def sync(pg, gaps=(12, 12, 12, 12)):
    """Sync by sections from the grid, tapping the real pad with the test clock moving between taps."""
    pg.click('.ckrow [data-a=ckGrid]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=ckTile][data-v=sync]'); pg.wait_for_timeout(300)
    for g in gaps:
        pg.click('#ckpad'); pg.evaluate(f"CLOCK.advance({g})")
    pg.wait_for_timeout(300)


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=844, touch=True)
    pg.evaluate(WAKE)
    pg.evaluate("CLOCK.fake(50000)")
    sid = song(pg)
    t.shot(pg, 'song')

    # ---------- the header: "Artist · 3:58", pinned icons, ⋯ ----------
    ok(pg.inner_text('.ckart').strip() == 'Harbour Lights', 'the header shows the artist with no length while it isn\'t set')
    pins = pg.evaluate("[...document.querySelectorAll('.ckrow .ckpi')].map(b=>b.dataset.v||b.dataset.a)")
    ok(pins == ['timing', 'key', 'ckGrid'], f'Timing and Key are pinned beside the artist by default, and ⋯ is last ({pins})')
    ok(pg.locator('.sgmodes [data-a=sgKey]').count() == 0, 'Key has moved from the modes row to the header')
    ok(pg.evaluate("CLOCK.synced(songById(U.songId))") is False and tl(pg) is None, 'a new song has no timing (not synced)')

    # the length picker: wheels, a live readout, Cancel and Set, just below what was tapped
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250); pg.click('.sheet [data-a=ckTile][data-v=check]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'ckSync', 'Check timing on an unsynced song starts Sync instead')
    pg.click('[data-a=ckSyncX]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'lyr' and not pg.evaluate("CLOCK.state().syncing"), '✕ before any tap goes back to the song')
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
    ok(pg.inner_text('.ckart').replace(' ', ' ').strip() == 'The Lights · 3:58', 'the header reads "Artist · 3:58": ' + pg.inner_text('.ckart'))
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
    ok(labels == ['Timing', 'Check timing', 'Key', 'Marks while playing', 'Blur ahead', 'Snapping', 'Stay awake', 'Sync again', 'Lyrics', 'Add track'],
       'the grid has the ten tiles in order (3.19: Track last): ' + ', '.join(labels))
    on = pg.evaluate("[...document.querySelectorAll('.sheet .cktile.on')].map(e=>e.dataset.v)")
    ok(on == ['marks', 'blur', 'snap', 'awake'], f'blue means on: Marks while playing, Blur ahead, Snapping and Stay awake start on ({on})')
    ok(pg.inner_text('.sheet [data-v=marks] small') == 'Breaths only', 'Marks while playing shows its value, Breaths only by default')
    ok(pg.locator('.sheet [data-v=snap] .ckab').inner_text() == 'A', 'Snapping has its A badge when on')
    t.shot(pg, 'grid')
    pg.click('.sheet [data-a=ckGridEdit]'); pg.wait_for_timeout(200)
    ok('2 of 3 pinned' in pg.inner_text('.sheet') and pg.locator('.sheet .ckpb.on').count() == 2, 'Edit shows what is pinned')
    pg.click('.sheet [data-a=ckTile][data-v=check]'); pg.wait_for_timeout(200)
    ok('3 of 3 pinned' in pg.inner_text('.sheet'), 'tapping a tile in Edit pins it')
    pg.click('.sheet [data-a=ckTile][data-v=sync]'); pg.wait_for_timeout(200)
    ok('3 is the most' in pg.inner_text('.toast') and '3 of 3 pinned' in pg.inner_text('.sheet'), 'no more than 3 can be pinned')
    pg.click('.sheet [data-a=ckTile][data-v=key]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=ckGridEdit]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(300)
    pins = pg.evaluate("[...document.querySelectorAll('.ckrow .ckpi')].map(b=>b.dataset.v||b.dataset.a)")
    ok(pins == ['timing', 'check', 'ckGrid'], f'the pinned icons follow (Key unpinned, Check timing pinned): {pins}')
    pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250)
    pg.click('.sheet [data-a=ckTile][data-v=snap]'); pg.wait_for_timeout(200)
    ok(pg.locator('.sheet [data-v=snap].on').count() == 0 and pg.locator('.sheet [data-v=snap] .ckab').count() == 0, 'Snapping turns off (and does nothing else until the Timeline)')
    pg.click('.sheet [data-a=ckTile][data-v=snap]'); pg.wait_for_timeout(150)
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(250)

    # ---------- Sync, the section pass ----------
    pg.click('.ckrow [data-a=ckTile][data-v=timing]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'ckSync' and 'Start the song' in pg.inner_text('main'), 'Timing on an unsynced song starts Sync: "Start the song"')
    ok(pg.locator('#dock #ckpad').count() == 1 and 'as “Verse 1” starts' in pg.inner_text('#ckpad'), 'the big pad sits at the bottom: Tap as "Verse 1" starts')
    ok(pg.locator('.ckrl.first').count() == 1 and 'first' in pg.inner_text('.ckrl.first').lower(), 'the first section is marked First')
    t.shot(pg, 'sync-ready')
    wl0 = pg.evaluate("window.__wl.req")
    pg.click('#ckpad'); pg.wait_for_timeout(150)
    st = pg.evaluate("CLOCK.state()")
    ok(st['syncRun'] and st['pass']['raw'][0] == 0, 'the first tap starts the clock at the expected start (0:00)')
    ok(pg.evaluate("window.__wl.req") == wl0 + 1 and st['wake'], 'Stay awake: the screen is kept awake while syncing')
    ok('Section 2 of 4' in pg.inner_text('main') and pg.locator('#ckST').count() == 1, 'the live screen shows the timer and "Section 2 of 4"')
    pg.evaluate("CLOCK.advance(12)"); pg.click('#ckpad'); pg.wait_for_timeout(100)
    raw = pg.evaluate("CLOCK.state().pass.raw")
    ok(abs(raw[1] - 12.0) < 0.002, f'every tap has 0.15 s taken off for the finger (clock 12.15 → {raw[1]})')
    ok(pg.inner_text('#ckST') == '0:12', 'the timer shows the clock')
    ok('just marked' in pg.inner_text('main').lower() and 'next' in pg.inner_text('main').lower(), 'Now and Next are shown')
    t.shot(pg, 'sync-live')
    # Undo the last tap
    pg.evaluate("CLOCK.advance(3)"); pg.click('#ckpad'); pg.wait_for_timeout(100)
    pg.click('[data-a=ckSyncUndo]'); pg.wait_for_timeout(150)
    st = pg.evaluate("CLOCK.state()")
    ok(st['pass']['idx'] == 2 and st['pass']['raw'][2] is None, 'Undo takes the last tap back')
    # Pause = re-anchor: the clock stops; the next tap resumes from the guessed start
    pg.evaluate("CLOCK.advance(9)")
    pg.click('[data-a=ckSyncPause]'); pg.wait_for_timeout(150)
    st = pg.evaluate("CLOCK.state()")
    ok(not st['syncRun'] and 'Scrub the song back a little' in pg.inner_text('main'), 'Pause stops the clock and says to scrub back, then tap as this section starts')
    guess = st['pass']['pending']
    ok(guess is not None and guess > 12, f'the clock waits at a guessed start for this section ({guess})')
    pg.evaluate("CLOCK.advance(30)")
    ok(pg.evaluate("CLOCK.syncNow()") == guess, 'nothing moves while paused')
    pg.click('#ckpad'); pg.wait_for_timeout(100)
    raw = pg.evaluate("CLOCK.state().pass.raw")
    ok(abs(raw[2] - guess) < 0.002 and pg.evaluate("CLOCK.state().syncRun"), 'the tap after Pause marks the guessed start and the clock carries on from it')
    # redo from a done item
    pg.click('.ckdone[data-v="1"]'); pg.wait_for_timeout(150)
    st = pg.evaluate("CLOCK.state()")
    ok(st['pass']['idx'] == 1 and st['pass']['raw'][1] is None and st['pass']['raw'][2] is None and not st['syncRun'],
       'tapping a done section redoes from there')
    ok(abs(st['pass']['pending'] - 12.0) < 0.002, 'redoing waits at that section\'s old start')
    pg.click('#ckpad'); pg.evaluate("CLOCK.advance(12)"); pg.click('#ckpad'); pg.evaluate("CLOCK.advance(12)"); pg.click('#ckpad')
    pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'ckCheck' and not pg.evaluate("CLOCK.state().syncing"), 'the last tap finishes the pass and opens Check timing')
    ok('Timing saved' in pg.inner_text('.toast') and pg.locator('.toast .ckub').count() == 1, 'a toast says Timing saved, with Undo')
    ok(not pg.evaluate("CLOCK.state().wake"), 'the wake lock goes once the pass ends')
    T = tl(pg)
    M = pg.evaluate("CLOCK.model()")
    starts = [M['T'][i][0] for i in range(len(M['L'])) if i == 0 or M['L'][i]['k'] != M['L'][i - 1]['k']]
    ok([round(x, 2) for x in starts] == [0, 12, 24, 36], f'each tapped section starts where it was tapped: {starts}')
    ok(T['est'] is True and all(s['anch'] for s in T['slots'].values()), 'the lines are an estimate, and every tapped section is a set start')
    ok(len(T['slots']) == 4 and len(set(T['slots'].keys())) == 4, 'timing is kept per place in the running order (Chorus 2 has its own times)')
    # even spread by syllables inside each section, ending a second before the next tap
    v1 = [M['T'][i] for i in range(len(M['L'])) if M['L'][i]['k'] == 0]
    d0, d1 = v1[0][1] - v1[0][0], v1[1][1] - v1[1][0]
    syl = pg.evaluate("CLOCK.model().L.slice(0,2).map(l=>l.syl.reduce((a,b)=>a+b,0))")
    ok(abs(d0 / d1 - syl[0] / syl[1]) < 0.02, f'lines share a section by syllables ({d0:.2f}/{d1:.2f} vs {syl})')
    ok(abs(v1[1][1] - 11.0) < 0.01, f'a section\'s last line ends a second before the next section ({v1[1][1]})')

    # ---------- Check timing ----------
    txt = pg.inner_text('main')
    ok('Song length' in txt and '3:58' in txt and '4 of 4 set' in txt and 'To-do markers' not in txt, 'Check timing: Song length, Section starts (4 of 4 set), no To-do row without markers')
    ok('Time each line' in txt and 'spread evenly' in txt, 'a note says the lines are spread evenly, with Time each line')
    ok(pg.locator('.ckr').count() == 8 and pg.locator('.ckd').count() == 8 and pg.locator('.ckadot').count() == 4,
       'each section and its lines, with duration bars and a dot for each set start')
    t.shot(pg, 'check', full_page=True)
    # Undo from the toast puts the timing back
    pg.click('.toast .ckub'); pg.wait_for_timeout(250)
    ok(tl(pg) == {'len': 238, 'real': False, 'est': False, 'slots': {}}, 'Undo puts the song back as it was (length only)')
    pg.click('[data-a=ckSyncAgain]'); pg.wait_for_timeout(300)
    for g in (12, 12, 12, 12):
        pg.click('#ckpad'); pg.evaluate(f"CLOCK.advance({g})")
    pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'ckCheck' and pg.evaluate("CLOCK.synced(songById(U.songId))"), 'Sync again from the start syncs the song again')
    # flags: very short and very long lines
    pg.evaluate("""(()=>{const s=songById(U.songId),o=s.order[0].o;s.timing.slots[o].lines=[[0,0.25],[0.3,20]];s.timing.slots[s.order[1].o].lines[0]=[21,24];save();rerender()})()""")
    txt = pg.inner_text('main')
    ok('Very short' in txt and 'Very long' in txt, 'Very short (under 0.4 s) and Very long (over 15 s) are flagged')
    pg.evaluate("(()=>{const s=songById(U.songId);s.timing.slots[s.order[2].o].marks=[1];save();rerender()})()")
    ok('To-do markers' in pg.inner_text('main') and pg.locator('.ckmk').count() == 1, 'To-do markers show when there are any, with a flag on the line')
    pg.click('[data-a=ckCheckBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'lyr', 'Back goes to the song')

    # ---------- play-along ----------
    pg.evaluate("(()=>{const s=songById(U.songId);delete s.timing;save()})()")
    pg.click('.ckrow [data-a=ckGrid]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=ckTile][data-v=sync]'); pg.wait_for_timeout(250)
    for g in (12, 12, 12, 12):
        pg.click('#ckpad'); pg.evaluate(f"CLOCK.advance({g})")
    pg.wait_for_timeout(300); pg.click('[data-a=ckCheckDone]'); pg.wait_for_timeout(300)
    # Ivan's breath mark on the first line, a sing-as label and a run on the second
    pg.evaluate("""(()=>{const s=songById(U.songId),a=s.sections[s.order[0].sid].ann;a['0:2']={br:1};a['1:0']={v:'kow',run:1,up:1,nt:'Soft'};MARKS.fromAnn(s.sections[s.order[0].sid]);
      // long gaps after line 0 (which has a breath mark) and line 2 (which has none)
      const v=s.timing.slots[s.order[0].o].lines,c=s.timing.slots[s.order[1].o].lines;v[0][1]=v[0][0]+2;c[0][1]=c[0][0]+1.5;save();rerender()})()""")
    pg.click('.ckrow [data-a=ckTile][data-v=timing]'); pg.wait_for_timeout(300)
    st = pg.evaluate("CLOCK.state()")
    ok(st['on'] and not st['run'] and pg.locator('#ckpa:not([hidden])').count() == 1, 'Timing on a synced song turns play-along on, waiting for the first line')
    ok('Tap the first line as it’s sung' in pg.inner_text('#ckpa .ckcap'), 'it says to tap the first line as it\'s sung')
    ok(pg.locator('#dock .cktr').count() == 1 and pg.locator('.cktr [data-a=ckNudge]').count() == 2, 'the transport capsule has −0.2, play and the time, and +0.2')
    ok(pg.locator('.ckrow [data-v=timing].on').count() == 1, 'the Timing icon is blue while play-along is on')
    wl0 = pg.evaluate("window.__wl.req")
    pg.click('#ckpa .ckl[data-i="0"]'); pg.wait_for_timeout(150)
    st = pg.evaluate("CLOCK.state()")
    ok(st['run'] and abs(pg.evaluate("CLOCK.now()")) < 0.01, 'tapping the first line starts the clock from it')
    ok(pg.evaluate("NOW.kind()") == 'clock', '3.20: play-along starts through the one sound owner, so anything else playing stops')
    ok(pg.evaluate("window.__wl.req") == wl0 + 1 and st['wake'], 'Stay awake keeps the screen on while playing along')
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
    # Marks while playing, Breaths only (the default)
    ok(pg.locator('#ckpa .ckl[data-i="0"] .ckbr').count() == 1, 'Breaths only: Ivan\'s breath mark shows on its line')
    ok(pg.locator('#ckpa .ckl[data-i="0"] .ckdot').count() == 0, 'no automatic dot on a line that has his breath mark')
    ok(pg.locator('#ckpa .v, #ckpa .run, #ckpa .m, #ckpa .sgnote').count() == 0 and 'kow' not in pg.inner_text('#ckpa'),
       'sing-as labels, runs, pitch arrows and notes are hidden while playing')
    M = pg.evaluate("CLOCK.model()")
    gaps = [(M['T'][i + 1][0] - (M['T'][i][1]), i) for i in range(len(M['L']) - 1)]
    dots = pg.evaluate("[...document.querySelectorAll('#ckpa .ckl')].filter(l=>l.querySelector('.ckdot')).map(l=>+l.dataset.i)")
    want = [i for g, i in gaps if g > 1.2 and i != 0]
    ok(dots == want and len(dots) > 0, f'an automatic dot only on lines with a gap over 1.2 s and no breath mark ({dots} vs {want})')
    # tap a line to jump there
    pg.click('#ckpa .ckl[data-i="5"]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("CLOCK.now()") - M['T'][5][0]) < 0.01 and pg.evaluate("document.querySelector('#ckpa .ckl.now').dataset.i") == '5',
       'tapping any line jumps the clock there')
    # −0.2 / +0.2: move all lyrics, saved, with Undo
    before = pg.evaluate("CLOCK.model().T.map(x=>x[0])")
    pg.click('.cktr [data-v="0.2"]'); pg.wait_for_timeout(150)
    after = pg.evaluate("CLOCK.model().T.map(x=>x[0])")
    ok(all(abs(a - b - 0.2) < 0.002 for a, b in zip(after, before)), '+0.2 moves every line 0.2 s later')
    ok('Lyrics 0.2 s later' in pg.inner_text('.toast') and pg.locator('.toast .ckub').count() == 1, 'with a toast and Undo')
    saved = json.loads(pg.evaluate("localStorage.getItem('vocalTracker')"))
    ok(any(s.get('timing') and abs(list(s['timing']['slots'].values())[0]['lines'][0][0] - 0.2) < 0.002 for s in saved['songs']), 'the nudge is saved')
    pg.click('.toast .ckub'); pg.wait_for_timeout(150)
    ok(pg.evaluate("CLOCK.model().T.map(x=>x[0])") == before and pg.evaluate("CLOCK.state().run"), 'Undo puts the lyrics back (and the clock keeps running)')
    pg.click('.cktr [data-v="-0.2"]'); pg.wait_for_timeout(150)
    ok(abs(pg.evaluate("CLOCK.model().T[3][0]") - (before[3] - 0.2)) < 0.002, '−0.2 moves every line earlier')
    pg.click('.toast .ckub'); pg.wait_for_timeout(150)
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
    # a playing take wins over play-along
    pg.evaluate("CLOCK.off()"); pg.wait_for_timeout(200)
    ok(pg.locator('#ckpa:not([hidden])').count() == 0 and pg.locator('#dock .cktr').count() == 0 and not pg.evaluate("CLOCK.state().wake"),
       'turning Timing off leaves play-along')

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
    M = pg.evaluate("CLOCK.model()")
    ok(M['T'][4][1] < M['T'][5][0] < M['T'][6][0], 'play-along spreads it between its neighbours meanwhile')
    pg.click('#barR [data-a=sgUndo]') if pg.locator('#barR [data-a=sgUndo]').count() else None

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
        "o1": {"lines": [[1, 2], [0.5, 9], "junk", [4, 3]], "anch": True, "marks": [1, 7, 'a', 1]},
        "o2": {"lines": [[10, 30], [12, 13]], "anch": "yes", "marks": []},
        "o9": {"lines": [[1, 2]]}, "o3": "nope"}}
    bad['songs'].append({"id": "g_2", "name": "Broken", "artist": "", "timing": [1, 2, 3],
                         "sections": {"x1": {"label": "Verse", "cue": "", "lines": [["Hi"]], "ann": {}, "orphans": []}}, "order": [{"o": "o1", "sid": "x1"}]})
    p3 = t.page(b, data=bad)
    tm = p3.evaluate("D.songs[0].timing")
    ok(p3.evaluate("D.songs.length") == 2 and p3.evaluate("D.songs[0].sections.x1.lines.length") == 2, 'damaged timing never breaks a song')
    ok(tm['len'] is None and tm['real'] is False and tm['slots']['o1']['lines'] == [[1, 2], [None, None]] and tm['slots']['o1']['marks'] == [1],
       f'out-of-order lines, junk and extra lines are dropped, markers checked ({tm["slots"]["o1"]})')
    ok(tm['slots']['o2']['lines'] == [[10, 12], [12, 13]] and tm['slots']['o2']['anch'] is False, 'an overlapping end is trimmed to the next start; a bad set start is dropped')
    ok('o9' not in tm['slots'] and 'o3' not in tm['slots'], 'timing for places no longer in the running order is dropped')
    ok('timing' not in p3.evaluate("D.songs[1]"), 'timing that isn\'t an object is dropped')
    p3.evaluate("(()=>{U.tab='songs';U.view='lyr';U.songId='g_1';render()})()"); p3.wait_for_timeout(300)
    ok(p3.evaluate("CLOCK.synced(songById('g_1'))") and p3.locator('.ckrow').count() == 1, 'the song still opens and plays along with what was kept')
    p3.close(); p2.close()
    # a backup round trip keeps the timing
    keep = tl(pg)
    pg.evaluate("prepareExport(true,false)"); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    text = pg.evaluate("pendingExport.file.text()")
    pg.evaluate("(()=>{songById(U.songId).timing={len:5,real:false,est:false,slots:{}};save()})()")
    pg.evaluate("async t=>{pendingImport=await inspectBackup(t,'b.json',t.length);await restoreImport()}", text)
    pg.wait_for_function("!U.sheet||U.sheet!=='importing'", timeout=10000); pg.wait_for_timeout(600)
    back = pg.evaluate("JSON.parse(JSON.stringify(D.songs.find(s=>s.name==='Harbour Song').timing))")
    ok(back == keep, f'a backup and restore keeps the timing exactly ({back} vs {keep})')

    # ---------- every size, light and dark ----------
    sizes = [(375, 667, 'light'), (390, 844, 'dark'), (852, 393, 'light'), (820, 1180, 'dark'), (1440, 900, 'light'), (320, 568, 'dark')]
    for w, h, sc in sizes:
        p = t.page(b, w=w, h=h, sc=sc, touch=w < 1400)
        p.evaluate("CLOCK.fake(10000)")
        song(p)
        p.evaluate("(()=>{if(split()){U.tab='songs';U.view=null}else{U.tab='songs';U.view='lyr'}render()})()"); p.wait_for_timeout(250)
        nm = f'{w}x{h} {sc}'
        probs = []
        def side(where):
            if p.evaluate("document.documentElement.scrollWidth") > w + 1: probs.append('sideways scroll on ' + where)
        side('the song')
        if p.locator('.ckrow').count() != 1: probs.append('no header row')
        p.click('[data-a=ckGrid]'); p.wait_for_timeout(250); side('the grid')
        gr = p.locator('.sheet .ckgrid').bounding_box()
        if not gr or gr['width'] > w: probs.append('grid too wide')
        p.click('.sheet [data-a=ckTile][data-v=sync]'); p.wait_for_timeout(300); side('Sync')
        for g in (8, 8, 8):
            p.click('#ckpad'); p.evaluate(f"CLOCK.advance({g})")
        pad = p.locator('#ckpad').bounding_box()
        if p.evaluate("!!document.querySelector('#dock #ckpad')") is not True: probs.append('pad not in the dock')
        if not pad or pad['y'] + pad['height'] > h + 1: probs.append('pad off screen')
        last = p.evaluate("(()=>{const l=[...document.querySelectorAll('#app .ckrow2')].pop();return l?l.getBoundingClientRect().bottom:0})()")
        if w < 700 and h > 600 and last > pad['y'] + 2: probs.append(f'live screen under the pad ({last} > {pad["y"]})')
        if w == 375: t.shot(p, f'sync-{sc}')
        p.click('#ckpad'); p.wait_for_timeout(350); side('Check timing')
        if w == 375 or w == 390: t.shot(p, f'check-{sc}-{w}', full_page=True)
        p.click('[data-a=ckCheckDone]'); p.wait_for_timeout(300)
        p.click('.ckrow [data-a=ckTile][data-v=timing]'); p.wait_for_timeout(250)
        p.click('#ckpa .ckl[data-i="0"]'); p.evaluate("CLOCK.advance(3)"); p.wait_for_timeout(200); side('play-along')
        tr = p.locator('#dock .cktr').bounding_box(); pa = p.locator('#ckpa').bounding_box()
        if not tr or tr['y'] + tr['height'] > h: probs.append('transport off screen')
        if not pa or pa['width'] < 200: probs.append('play-along view missing')
        # Render 10's search circle goes beside whatever is in the dock, so the transport and pad must stay in it
        if p.evaluate("!!document.querySelector('#dock .cktr')") is not True: probs.append('transport not in the dock')
        if w == 375 or w == 820: t.shot(p, f'play-{sc}-{w}')
        p.click('.cktr [data-a=ckPP]'); p.wait_for_timeout(250); side('paused')
        if p.locator('.sgl.ckcur').count() != 1: probs.append('no current line when paused')
        if w == 375: t.shot(p, f'paused-{sc}')
        ok(not probs, f'{nm}: header, grid, Sync, Check timing and play-along fit ({"; ".join(probs) or "ok"})')
        p.close()
