"""Q12 · Song Clock: Timing Integrity (3.30). Timing Ivan placed by hand is never moved or overwritten by something he
didn't do to it, and guesses are never saved as if placed:
- moving a timed section turns that section's line times into estimates (its start kept); other sections don't change
- ckOrder only ever rewrites estimated lines; placed lines that overlap are flagged on Check timing instead
- punch-in, the line lane and promote read placed times (M.raw with M.est), never the filled model M.T
- adding a line between two touching placed lines moves neither of them
- promoting a marker lands the section start on the marker (earlier sections squeezed, or left as estimates)
- replacing a track with a shorter one: Keep / Trim for anything past the new end, with Undo
- a section start stops counting as set once its first line loses its time
The audio files are tones with gaps, written by the test. Nothing copyrighted is ever used."""
import json
from test_track import F, loaded

LYR = """[Verse 1]
Morning light on the harbour wall
Counting boats as the tide comes in
Gulls above the chimney smoke
Salt and rope and a long way home

[Chorus]
Hold on hold on to the sound
Carry me home when the lights go down
Every road leads back to you
Hold on hold on

[Verse 2]
Paper maps and a borrowed coat
Somebody's song on the radio
Rain again on the ferry glass
Counting stops till the morning comes

[Chorus]
Hold on hold on to the sound
Carry me home when the lights go down
Every road leads back to you
Hold on hold on"""

ADD = """([t,a,l])=>{U.sDraft={step:1,title:t,artist:a,text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();return U.songId}"""
OPEN = "id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})"
TL = "id=>JSON.parse(JSON.stringify(songById(id).timing||null))"
MK = "id=>JSON.parse(JSON.stringify(songById(id).markers||null))"
SETMK = """([id,ts])=>{const sg=songById(id);sg.markers=ts.map((t,i)=>typeof t==='number'?{id:'m'+i,t}:Object.assign({id:'m'+i},t));save();rerender()}"""
# every line placed by hand: section k's lines start at 20k, 20k+5, 20k+10, 20k+15 and last 4.5 s
PLACE = """id=>{const sg=songById(id),M=ckModel(sg),T=M.L.map(l=>[l.k*20+l.li*5,l.k*20+l.li*5+4.5]);
  ckStore(sg,M.L,T,sg.order.map(()=>true),M.marks);rerender();return sg.order.map(x=>x.o)}"""
# the starts saved in one place of the running order (by its o)
STARTS = "([id,o])=>songById(id).timing.slots[o].lines.map(r=>r[0])"
MODEL = """id=>{const M=ckModel(songById(id));return {T:M.T,raw:M.raw,est:M.est,anch:M.anch,placed:M.placed,
  k:M.L.map(l=>l.k),o:M.L.map(l=>l.o)}}"""


def lyric_song(pg, title='Harbour', lyr=LYR):
    sid = pg.evaluate(ADD, [title, 'Harbour Lights', lyr]); pg.wait_for_timeout(350)
    return sid


def with_track(pg, sid, secs=90, name='Harbour 90.wav'):
    """Give a song its track through the song page's Practice row (the real door)."""
    pg.evaluate(OPEN, sid); pg.wait_for_timeout(300)
    pg.evaluate("id=>TRACK.expect(id)", sid)
    pg.set_input_files('#trackIn', F(name, secs))
    loaded(pg, sid)


def moving(b, t):
    """The audit's reproduction (C1): move Chorus 2 above Verse 2 in a timed song, then re-time one line."""
    ok = t.ok
    pg = t.page(b)
    sid = lyric_song(pg)
    os_ = pg.evaluate(PLACE, sid)
    v2, c2 = os_[2], os_[3]
    ok(pg.evaluate(STARTS, [sid, v2]) == [40, 45, 50, 55], 'Verse 2 starts at 40, 45, 50 and 55 s')
    # hold Chorus 2 and drag it above Verse 2
    pg.evaluate(OPEN, sid); pg.wait_for_timeout(300)
    pg.evaluate("SG.drag={el:true,from:3,to:2};sgEndDrag()"); pg.wait_for_timeout(200)
    ok(pg.evaluate("id=>songById(id).order.map(x=>x.o)", sid) == [os_[0], os_[1], c2, v2], 'Chorus 2 now comes before Verse 2')
    M = pg.evaluate(MODEL, sid)
    ok(all(M['est'][i] for i in range(len(M['o'])) if M['o'][i] == c2),
       'the moved section’s lines become estimates (drawn dashed, listed on Check timing)')
    ok(not any(M['est'][i] for i in range(len(M['o'])) if M['o'][i] != c2), 'no other section’s lines become estimates')
    ok(M['anch'] == [True, True, True, True] and pg.evaluate(STARTS, [sid, c2])[0] == 60,
       'the moved section keeps its start (60 s), still counted as set')
    ok(pg.evaluate(STARTS, [sid, c2]) == [60, 65, 70, 75], 'its estimated lines keep their times until they’re placed again')
    # re-time line 1 (as punch-in, a lane edge or Start here would)
    pg.evaluate("id=>ckSetLines(songById(id),{0:[0.5,4.5]},true)", sid); pg.wait_for_timeout(150)
    ok(pg.evaluate(STARTS, [sid, v2]) == [40, 45, 50, 55],
       f'after re-timing line 1, Verse 2 is still 40, 45, 50, 55 s ({pg.evaluate(STARTS, [sid, v2])})')
    ok(pg.evaluate(STARTS, [sid, os_[1]]) == [20, 25, 30, 35] and pg.evaluate(STARTS, [sid, c2]) == [60, 65, 70, 75],
       'and no other section changes')
    ok(pg.evaluate(STARTS, [sid, os_[0]]) == [0.5, 5, 10, 15], 'only the re-timed line moved')
    # ±0.2 s nudges move every line together, and never squash one section into another
    pg.evaluate("id=>{CK.songId=id;ckNudge(0.2)}", sid); pg.wait_for_timeout(150)
    ok(pg.evaluate(STARTS, [sid, v2]) == [40.2, 45.2, 50.2, 55.2] and pg.evaluate(STARTS, [sid, c2]) == [60.2, 65.2, 70.2, 75.2],
       f'a nudge moves every line by 0.2 s, out of order or not ({pg.evaluate(STARTS, [sid, v2])})')
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(150)
    # Check timing flags placed lines that overlap (Verse 2 now starts before Chorus 2's start)
    pg.evaluate("id=>{CK.ret=null;ckOpenCheck(songById(id))}", sid); pg.wait_for_timeout(300)
    flags = pg.evaluate("[...document.querySelectorAll('#app .ckr')].map(r=>(r.querySelector('.ckflag')||{}).textContent||'')")
    ok(flags.count('Overlaps') >= 1 and all(f in ('', 'Overlaps') for f in flags),
       f'Check timing flags the lines out of order with “Overlaps”, rewriting nothing ({flags})')
    ok(pg.locator('#app .ckd.est').count() >= 3, 'and draws the moved section’s lines dashed')
    ok(pg.evaluate(STARTS, [sid, v2]) == [40, 45, 50, 55], 'opening Check timing changes nothing')
    # placing the moved section's lines again makes the song placed again
    pg.evaluate("""id=>{const sg=songById(id),M=ckModel(sg),ch={};M.L.forEach((l,i)=>{if(l.k===2)ch[i]=[38+l.li*0.4,38+l.li*0.4+0.3]});
      ckSetLines(sg,ch,true)}""", sid)
    T = pg.evaluate(TL, sid)
    ok(T['est'] is False and not any('fix' in s for s in T['slots'].values()) and not any(pg.evaluate(MODEL, sid)['est']),
       'once every moved line is placed again, nothing is estimated (and no placed-by-hand list is kept)')
    # Undo of the move puts the order and timing back (the song's own Undo)
    pg.evaluate("id=>{const sg=songById(id);ckStore(sg,ckLines(sg),ckLines(sg).map((l,i)=>[i*3,i*3+2]),sg.order.map(()=>true),[])}", sid)
    pg.evaluate("SG.drag={el:true,from:0,to:1};sgEndDrag()"); pg.wait_for_timeout(150)
    ok(pg.evaluate("SG.undo.length") >= 1, 'moving a section can be undone')
    # moving an untimed section of a timed song: nothing to turn into estimates
    pg.evaluate("""id=>{const sg=songById(id),L=ckLines(sg);ckStore(sg,L,L.map(l=>l.k<2?[l.k*20+l.li*5,l.k*20+l.li*5+4]:[null,null]),
      sg.order.map((x,k)=>k<2),[],{est:false})}""", sid)
    before = pg.evaluate(TL, sid)
    pg.evaluate("SG.drag={el:true,from:3,to:2};sgEndDrag()"); pg.wait_for_timeout(150)
    after = pg.evaluate(TL, sid)
    ok(after['est'] is False and after['slots'] == before['slots'], 'moving a section with no times leaves the timing alone')
    pg.context.close()


def ordering(b, t):
    ok = t.ok
    pg = t.page(b)
    # ckOrder with a placed mask: placed lines are never touched; estimates are kept in order around them
    r = pg.evaluate("ckOrder([[10,12],[5,6],[5.02,9],[20,null]],[true,true,false,true])")
    ok(r[0] == [10, 12] and r[1] == [5, 6] and r[3] == [20, None], f'placed lines are never rewritten ({r})')
    ok(r[2][0] == 5.1 and r[2][1] == 9, f'an estimate still starts at least 0.1 s after the line before ({r[2]})')
    r = pg.evaluate("ckOrder([[10,12],[5,6]])")
    ok(r[1][0] == 10.1, 'without a mask every line is an estimate (as before)')
    # touching placed lines with a new line between them (H3)
    sid = lyric_song(pg)
    pg.evaluate("""id=>{const sg=songById(id),L=ckLines(sg),T=L.map((l,i)=>[i*2+10,i*2+12]);ckStore(sg,L,T,sg.order.map(()=>true),[])}""", sid)
    o0 = pg.evaluate("id=>songById(id).order[0].o", sid)
    ok(pg.evaluate(STARTS, [sid, o0]) == [10, 12, 14, 16], 'Verse 1’s lines touch: 10–12, 12–14, 14–16, 16–18')
    pg.evaluate("""id=>{const sg=songById(id),x=sg.order[0],sec=sg.sections[x.sid],old=sec.lines.map(l=>l.slice()),nw=old.slice();
      nw.splice(1,0,['Oh','oh','oh']);nw.splice(1,0,['Hey']);ckLyricsChanged(sg,x.sid,old,nw);sec.lines=nw;save();rerender()}""", sid)
    M = pg.evaluate(MODEL, sid)
    ok(M['T'][0][0] == 10 and M['T'][3][0] == 12 and M['raw'][3][0] == 12,
       f'adding two lines between two touching placed lines moves neither of them ({M["T"][:4]})')
    ok(M['est'][1] and M['est'][2] and 10 < M['T'][1][0] < M['T'][2][0] < 12,
       f'the new lines are estimates squeezed between them ({M["T"][1]}, {M["T"][2]})')
    ok(all(M['T'][i][0] < M['T'][i + 1][0] for i in range(len(M['T']) - 1)), 'every line is still in time order')
    pg.evaluate("id=>ckSetLines(songById(id),{10:[26.2,27.8]},true)", sid)
    M = pg.evaluate(MODEL, sid)
    ok(M['raw'][3] == [12, 14] and M['raw'][1] == [None, None] and M['raw'][2] == [None, None],
       'editing another line saves neither the neighbours’ pushed times nor the estimates')
    # bounds for punch-in and Start here: the nearest placed lines, never estimates (H2)
    sp = pg.evaluate("""id=>{const sg=songById(id),M=ckModel(sg);const s=sg.order.map((x,k)=>k*20);
      ckStore(sg,M.L,ckSpread(sg,M.L,s),s.map(()=>true),M.marks,{est:true});const N=ckModel(sg);
      return {b:ckBounds(N,2),b0:ckBounds(N,0),first:N.L.findIndex(l=>l.k===1),est:N.est,placed:N.placed}}""", sid)
    ok(sp['b'] == [0, 20], f'on spread timing, a line’s bounds are its section’s start and the next one, not its estimated neighbours ({sp["b"]})')
    ok(sp['b0'] == [None, 20], f'the first line has no lower bound ({sp["b0"]})')
    ok(sp['placed'][0] and sp['placed'][sp['first']] and not sp['placed'][1], 'set section starts count as placed; spread lines don’t')
    # a section start stops counting as set once its first line loses its time (M4)
    pg.evaluate("""id=>{const sg=songById(id),x=sg.order[1],sec=sg.sections[x.sid],old=sec.lines.map(l=>l.slice()),nw=old.slice();
      nw[0]=['A','new','first','line'];ckLyricsChanged(sg,x.sid,old,nw);sec.lines=nw;save();rerender()}""", sid)
    T = pg.evaluate(TL, sid)
    sl = [T['slots'][x] for x in pg.evaluate("id=>songById(id).order.map(x=>x.o)", sid)]
    ok(sl[1]['anch'] is False and sl[3]['anch'] is False, 'changing a section’s first line clears its set start (every place it’s sung)')
    ok(sl[0]['anch'] is True and sl[2]['anch'] is True, 'other sections keep theirs')
    pg.evaluate("id=>{const sg=songById(id);sg.timing.slots[sg.order[2].o].lines[0]=[null,null];sg.timing.slots[sg.order[2].o].anch=true}", sid)
    ok(pg.evaluate(MODEL, sid)['anch'][2] is False, 'a start saved as set without its first line’s time doesn’t count as set')
    pg.context.close()


def promoting(b, t):
    ok = t.ok
    pg = t.page(b, touch=False)
    pg.evaluate("CLOCK.fake(50000)")
    # H4: Intro, Verse, Pre-chorus, Chorus; promote a marker at 0:20 as the Chorus start on an untimed song
    words = ['Morning', 'Harbour', 'Lantern', 'Ferry', 'Paper', 'Silver']
    long_lyr = '\n\n'.join('[%s]\n' % n + '\n'.join(f'{w} {n.lower()} light on the wall as the boats come in {j}' for j, w in enumerate(words))
                           for n in ('Intro', 'Verse', 'Pre-chorus', 'Chorus'))
    sid = lyric_song(pg, 'Long', long_lyr)
    with_track(pg, sid, 90)
    pg.evaluate(SETMK, [sid, [20, 50, 4, 1]])
    pg.evaluate("TRACK.promote('m0',3)"); pg.wait_for_timeout(250)
    M = pg.evaluate(MODEL, sid)
    f1, f3 = M['k'].index(1), M['k'].index(3)
    ok(abs(M['T'][f3][0] - 20) < 1e-6 and M['raw'][f3][0] == 20, f'the Chorus starts on the marker, 0:20 ({M["T"][f3]})')
    ok(all(M['T'][i][0] < 20 for i in range(f3)), 'every earlier section is squeezed in before it')
    ok(all(M['T'][i][0] < M['T'][i + 1][0] for i in range(len(M['T']) - 1)), 'every line is in time order')
    ok(M['anch'] == [False, False, False, True], f'only the Chorus counts as set ({M["anch"]})')
    # no room at all: a marker at 0:01 starting the Chorus leaves the earlier lines as estimates
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(200)
    pg.evaluate("TRACK.promote('m3',3)"); pg.wait_for_timeout(250)
    M = pg.evaluate(MODEL, sid)
    ok(M['raw'][f3][0] == 1 and M['T'][f3][0] == 1, f'with no room before it, the Chorus still starts on the marker ({M["T"][f3]})')
    ok(all(M['raw'][i] == [None, None] and M['est'][i] for i in range(f3)),
       'and the lines before it are left as estimates (no time of their own)')
    # a later promotion on the now-timed song lands on its marker too, and keeps the other start
    pg.evaluate("ckUndo()"); pg.wait_for_timeout(200)
    pg.evaluate("TRACK.promote('m1',3)"); pg.wait_for_timeout(250)
    pg.evaluate("TRACK.promote('m2',1)"); pg.wait_for_timeout(250)
    M = pg.evaluate(MODEL, sid)
    ok(M['raw'][f1][0] == 4 and M['raw'][f3][0] == 50, f'Verse at 0:04 and Chorus still at 0:50 ({M["raw"][f1][0]}, {M["raw"][f3][0]})')
    ok(all(r[0] is not None and r[0] >= 0 for r in M['raw']) and
       all(M['T'][i][0] < M['T'][i + 1][0] for i in range(len(M['T']) - 1)), 'every line is in time order, none before 0:00')
    # a timed song: promote warps the saved times only, so estimates stay estimates (H3)
    sid2 = lyric_song(pg, 'Timed')
    pg.evaluate("""id=>{const sg=songById(id),L=ckLines(sg);ckStore(sg,L,L.map((l,i)=>i===5?[null,null]:[i*4,i*4+3]),sg.order.map(()=>true),[])}""", sid2)
    with_track(pg, sid2, 90)
    pg.evaluate(SETMK, [sid2, [44]])
    before = pg.evaluate(MODEL, sid2)
    pg.evaluate("TRACK.promote('m0',2)"); pg.wait_for_timeout(250)
    M = pg.evaluate(MODEL, sid2)
    f2 = M['k'].index(2)
    ok(M['raw'][f2][0] == 44, f'Verse 2 starts on the marker ({M["raw"][f2]})')
    ok(M['raw'][5] == [None, None] and M['est'][5], 'a line with no time of its own is still an estimate afterwards')
    ok(M['raw'][0] == before['raw'][0] and M['raw'][12] == before['raw'][12], 'the other set starts stay put')
    ok(all(M['T'][i][0] < M['T'][i + 1][0] for i in range(len(M['T']) - 1)), 'every line is in time order')
    # promoting into the first set start far earlier: earlier lines are squeezed in, never below 0
    pg.evaluate("id=>{const sg=songById(id),L=ckLines(sg);ckStore(sg,L,L.map((l,i)=>[30+i*2,31+i*2]),sg.order.map((x,k)=>k===2),[])}", sid2)
    pg.evaluate(SETMK, [sid2, [6]])
    pg.evaluate("TRACK.promote('m0',2)"); pg.wait_for_timeout(250)
    M = pg.evaluate(MODEL, sid2)
    ok(M['raw'][M['k'].index(2)][0] == 6 and all(r[0] >= 0 for r in M['raw']) and
       all(M['raw'][i][0] < M['raw'][i + 1][0] for i in range(len(M['raw']) - 1)),
       f'moving the only set start back to 0:06 squeezes the lines before it between 0 and the marker ({[r[0] for r in M["raw"][:9]]})')
    pg.context.close()


def replacing(b, t):
    ok = t.ok
    pg = t.page(b, touch=False)
    sid = lyric_song(pg)
    with_track(pg, sid, 90)
    pg.evaluate(PLACE, sid)
    pg.evaluate(SETMK, [sid, [10, {'t': 30, 'end': 70}, 75]])
    pg.evaluate("id=>{const sg=songById(id);sg.loop={start:30,end:80,on:true};save()}", sid)
    t0, m0 = pg.evaluate(TL, sid), pg.evaluate(MK, sid)
    # replace it with a shorter mix (a 60 s file)
    pg.evaluate("id=>TRACK.expect(id)", sid)
    pg.set_input_files('#trackIn', F('Harbour 60.wav', 60))
    pg.wait_for_function("U.sheet==='trkPast'", timeout=15000); pg.wait_for_timeout(200)
    txt = pg.inner_text('.sheet')
    ok('2 markers' in txt and '4 lines' in txt and pg.locator('.sheet [data-a=trkPastKeep]').count() == 1 and
       pg.locator('.sheet [data-a=trkPastTrim]').count() == 1,
       f'replacing with a shorter track asks what to do with what’s past its end: Keep or Trim ({txt!r})')
    ok(pg.evaluate(MK, sid) == m0 and pg.evaluate(TL, sid)['slots'] == t0['slots'], 'nothing is deleted while it asks')
    pg.click('.sheet [data-a=trkPastKeep]'); pg.wait_for_timeout(300)
    ok(pg.evaluate(MK, sid) == m0 and pg.evaluate(TL, sid)['slots'] == t0['slots'], 'Keep keeps every marker and line time')
    ok(pg.locator('.toast .ckub').count() == 1, 'with Undo')
    ok(pg.evaluate("id=>songById(id).loop", sid)['end'] == 60, 'the loop is trimmed to the new length, as before')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')", timeout=15000); pg.wait_for_timeout(300)
    ok(pg.evaluate(MK, sid) == m0, 'kept markers past the end survive a reload (swap back to the longer mix and they’re there)')
    # back to the long mix, then the short one again, and Trim
    pg.evaluate(OPEN, sid); pg.wait_for_timeout(300)
    pg.evaluate("id=>TRACK.expect(id)", sid); pg.set_input_files('#trackIn', F('Harbour 90.wav', 90)); loaded(pg, sid)
    ok(pg.evaluate("U.sheet") != 'trkPast', 'a longer track doesn’t ask')
    pg.evaluate("id=>TRACK.expect(id)", sid); pg.set_input_files('#trackIn', F('Harbour 60.wav', 60))
    pg.wait_for_function("U.sheet==='trkPast'", timeout=15000); pg.wait_for_timeout(200)
    pg.click('.sheet [data-a=trkPastTrim]'); pg.wait_for_timeout(300)
    mk = pg.evaluate(MK, sid)
    ok([m['t'] for m in mk] == [10, 30] and mk[1]['end'] == 60, f'Trim drops markers past the end and ends a marker at it ({mk})')
    M = pg.evaluate(MODEL, sid)
    late = [i for i in range(len(M['raw'])) if M['k'][i] == 3]
    ok(all(M['raw'][i] == [None, None] for i in late) and all(r[1] is None or r[1] <= 60 for r in M['raw']),
       'lines that start past the end lose their time; nothing ends past it')
    ok(M['anch'][3] is False, 'and that section’s start no longer counts as set')
    ok(pg.evaluate("id=>ckModel(songById(id)).marks", sid)[late[0]], 'trimmed lines get a to-do marker')
    ok(pg.locator('.toast .ckub').count() == 1, 'Trim has Undo')
    pg.click('.toast .ckub'); pg.wait_for_timeout(300)
    ok(pg.evaluate(MK, sid) == m0 and pg.evaluate(TL, sid)['slots'] == t0['slots'], 'Undo puts every marker and line time back')
    pg.context.close()


def run(b, t):
    moving(b, t)
    ordering(b, t)
    promoting(b, t)
    replacing(b, t)
