"""Q37 the song ladder in Application (VS-004): the Straight / Ladder switch (remembered per song, in its backup), the
four rungs (their instructions, lyric views, Skip this rung, Sing over the track), the live pitch line from the
recording's own microphone, ladder takes as ordinary takes named by their rung, the fold (the sung rungs in one row,
"Up next", only the current rung open), Lines (overlaid, each switchable, the parting spot by time or by line, Hear
both through NOW), Notes of the line (one per held note of the trill, Repeat until tapped again, one sound at a time),
Done folding to "Song · Section · Ladder · N takes", old data and backups, no scores, and 375 and 390 in light and dark
with Reduce Motion. Synthetic tones made in the page and a fake microphone only.
`VS_LADDER=switch,rungs,live,lines,notes,done,data,sizes` runs only those parts."""
import os, json, re
from harness import until
from test_application import to_app, lyric_song, occ, CARD
from test_pitch import VOICE

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']
WIDE = "document.documentElement.scrollWidth<=innerWidth+1"

# synthetic rungs, as MKTAKE segments: the words go flat on the second note; the trill has three held notes
TRILL = [[None, 0.2], [60, 0.5], [64, 0.5], [62, 0.5]]
HUM = [[None, 0.3], [60, 0.5], [64, 0.5], [62, 0.5]]
VOWELS = [[None, 0.2], [60, 0.5], [64, 0.5], [62, 0.5]]
WORDS = [[None, 0.5], [60, 0.5], [63, 0.5], [62, 0.5]]


def setup(pg, timed=True, track=False):
    sid = lyric_song(pg, timed)
    if track:
        from test_batch12 import add_track
        from test_track import track as tr
        add_track(pg, sid, tr())
    pg.evaluate(VOICE)
    ch = occ(pg, sid, 1)
    to_app(pg)
    pg.evaluate("([id,o])=>{X.sing={id,o,st:'open'};saveDraft();rerender()}", [sid, ch])
    return sid, ch


def ladder_on(pg):
    pg.click(f'{CARD} [data-a=apMode][data-v=ladder]')
    until(pg, "APPL.state().ladder===true")


def sung(pg, sid, ch, rung, segs, n):
    """A rung sung this session: a synthetic take of the place with its rung, joined to the session."""
    pg.evaluate("async([id,sid,o,segs,rung])=>{await MKTAKE([id,sid,o,segs,{rung}]);X.takes.push(id);X.song=sid;saveDraft();rerender()}",
                [n, sid, ch, segs, rung])


def lines_ready(pg):
    return until(pg, "!!document.querySelector('#apcard .apchart svg')", 10000)


def switch(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg)
    ok(pg.locator(f'{CARD} .apmode button').all_inner_texts() == ['Straight', 'Ladder'] and 'on' in pg.get_attribute(f'{CARD} .apmode [data-v=straight]', 'class'),
       'the card has a Straight / Ladder switch, on Straight')
    ok(pg.locator(f'{CARD} .lad').count() == 0 and pg.inner_text(f'{CARD} [data-a=apSing]').strip() == 'Sing', 'Straight is the card as before')
    ladder_on(pg)
    ok(pg.evaluate("id=>songById(id).ext", sid) == {'ladder': True}, 'Ladder is remembered on the song (ext.ladder)')
    ok(pg.evaluate("id=>JSON.parse(localStorage.getItem('vocalTracker')).songs.find(s=>s.id===id).ext", sid) == {'ladder': True}, 'and saved')
    txt = pg.inner_text(CARD)
    ok('1 · Lip trill' in txt and 'Sing the section on a lip trill' in txt and pg.inner_text(f'{CARD} [data-a=apSing]').strip() == 'Sing · Trill',
       'the first rung: Lip trill, its instruction and Sing · Trill')
    ok('Up next: Hum, Vowels only, Words' in txt, 'the rungs still to come are one line: ' + txt.replace('\n', ' | '))
    ok(pg.locator(f'{CARD} .ladcur').count() == 1 and pg.locator(f'{CARD} .ladsum').count() == 0, 'only the current rung is open; nothing sung yet')
    ok(pg.locator(f'{CARD} .aply.faint').count() == 1 and 'Hold on hold on' in pg.inner_text(f'{CARD} .aply'), 'the trill’s words are there, faded')
    # another song is still Straight
    pg.click('#app [data-a=apSong][data-k=g_1]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("APPL.state().ladder") is False and pg.evaluate("songById('g_1').ext") is None, 'the switch is per song: another song is still Straight')
    pg.evaluate("([id,o])=>{X.sing={id,o,st:'open'};saveDraft();rerender()}", [sid, ch])
    ok(pg.evaluate("APPL.state().ladder") is True, 'and back on this song, it’s the ladder')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')", timeout=15000); pg.wait_for_timeout(200)
    pg.evaluate("go(()=>{U.tab='today';U.view='app'})"); pg.wait_for_timeout(200)
    ok(pg.evaluate("APPL.state().ladder") is True and pg.locator(f'{CARD} .lad').count() == 1, 'after a reload the song is still a ladder')
    pg.click(f'{CARD} [data-a=apMode][data-v=straight]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("id=>songById(id).ext", sid) is None and pg.locator(f'{CARD} .lad').count() == 0, 'Straight again: the field is gone and the card is as before')
    pg.context.close()


def rungs(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg)
    ladder_on(pg)
    n = pg.evaluate("TAKES.length")
    pg.click(f'{CARD} [data-a=apSing]')
    ok(until(pg, "!!rec&&!!document.querySelector('#apcard.rec')", 8000), 'Sing · Trill records')
    ok(pg.evaluate("rec.rung") == 'trill' and 'Recording · Lip trill' in pg.inner_text('#apcard'), 'the recording card names the rung')
    ok(pg.locator('#apcard #apLive svg').count() == 1 and pg.locator('#apcard .aply.faint').count() == 1, 'the live line and the faded words while it records')
    pg.wait_for_timeout(1100)
    pg.click('#apcard [data-a=apStop]')
    ok(until(pg, f"!rec&&TAKES.length==={n + 1}", 8000), 'Stop saves the take')
    pg.wait_for_timeout(300)
    tk = pg.evaluate("TAKES[TAKES.length-1]")
    ok(tk['ext'] == {'rung': 'trill'} and tk['o'] == ch and tk['songId'] == sid, 'a ladder take is an ordinary take of the place, with its rung')
    ok(pg.evaluate("t=>TAKE.short(t)", tk['id']) == 'Ladder · Lip trill' and pg.evaluate("t=>TAKE.nameOf(t)", tk['id']) == 'Ladder · Lip trill · Chorus 1',
       'named by its rung: Ladder · Lip trill')
    ok(tk['id'] in pg.evaluate("X.takes") and pg.evaluate("X.song") == sid, 'it joins the session, as Application’s takes do')
    st = pg.evaluate("APPL.state()")
    ok(st['sung'] == ['trill'] and st['cur'] == 'hum', 'the next rung is the hum')
    txt = pg.inner_text(CARD)
    ok('1 of 4 sung' in txt and 'Trill' in txt and '2 · Hum' in txt and 'Up next: Vowels only, Words' in txt, 'the sung rung folds into one row: ' + txt.replace('\n', ' | '))
    ok(pg.locator(f'{CARD} .ladrows').count() == 0 and pg.get_attribute(f'{CARD} .ladsum', 'aria-expanded') == 'false', 'folded until tapped')
    ok(pg.locator(f'{CARD} [data-a=apNoRec]').count() == 0 and pg.locator(f'{CARD} [data-a=apDone]').count() == 0, 'one rung in: no Done yet, no Practised, not recorded')
    # Skip this rung
    pg.click(f'{CARD} [data-a=apSkip]'); pg.wait_for_timeout(150)
    st = pg.evaluate("APPL.state()")
    ok(st['cur'] == 'vowels' and st['skip'] == ['hum'] and 'skipped Hum' in pg.inner_text(f'{CARD} .ladsum'), 'Skip this rung moves on, and the row says it was skipped')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalDraft')).sing.skip") == ['hum'], 'skipped rungs are kept on the draft')
    # Vowels only: the vowel letters picked out (spelling, not sounds)
    b1 = pg.locator(f'{CARD} .aply.vowels p >> nth=0').locator('b').all_inner_texts()
    ok(''.join(b1) == 'oooooeou', 'Vowels only picks out the vowel letters: ' + ''.join(b1))
    ok(pg.inner_text(f'{CARD} .aply.vowels p >> nth=0') == 'Hold on hold on to the sound', 'and keeps the words readable')
    # the fold opens and closes
    pg.click(f'{CARD} [data-a=apLadFold]'); pg.wait_for_timeout(150)
    ok(pg.locator(f'{CARD} .ladrow').count() == 1 and pg.get_attribute(f'{CARD} .ladsum', 'aria-expanded') == 'true'
       and pg.locator(f'{CARD} .ladrow [data-a=playTake][data-k="{tk["id"]}"]').count() == 1, 'tapped, it opens to the rung’s row with its play button')
    pg.click(f'{CARD} .ladrow [data-a=playTake]')
    ok(until(pg, f"playingId==='{tk['id']}'&&NOW.kind()==='take'", 6000), 'the rung’s take plays, through NOW')
    pg.evaluate("stopPlayback();rerender()")
    pg.click(f'{CARD} [data-a=apLadFold]'); pg.wait_for_timeout(150)
    ok(pg.locator(f'{CARD} .ladrow').count() == 0, 'and folds again')
    # Change section starts the ladder afresh at that place
    sung(pg, sid, ch, 'words', WORDS, 'w1')
    ok(pg.evaluate("APPL.state().cur") == 'vowels', 'a later rung sung doesn’t change which one is next')
    pg.evaluate("([o])=>SG_ACT.apSec(null,o)", [occ(pg, sid, 0)])
    st = pg.evaluate("APPL.state()")
    ok(st['sung'] == [] and st['skip'] == [] and st['cur'] == 'trill', 'another place starts the ladder afresh')
    pg.evaluate("([o])=>SG_ACT.apSec(null,o)", [ch])
    # every rung skipped, nothing sung
    pg.evaluate("([o])=>SG_ACT.apSec(null,o)", [occ(pg, sid, 2)])
    for _ in range(4): pg.click(f'{CARD} [data-a=apSkip]'); pg.wait_for_timeout(80)
    ok('Every rung skipped' in pg.inner_text(CARD) and pg.locator(f'{CARD} [data-a=apLadAgain]').count() == 1, 'every rung skipped: Start the ladder again')
    pg.click(f'{CARD} [data-a=apLadAgain]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("APPL.state().cur") == 'trill', 'which starts again from the trill')
    pg.context.close()

    # Sing over the track and Q16's headphones sheet, unchanged
    pg = t.page(b, touch=True)
    sid, ch = setup(pg, track=True)
    ladder_on(pg)
    ok(pg.locator(f'{CARD} .ladcur [data-a=apOver]').count() == 1, 'Sing over the track on the current rung')
    pg.click(f'{CARD} [data-a=apSing]')
    ok(until(pg, "U.sheet==='recOver'"), 'it asks with the headphones sheet first')
    pg.click('.sheet [data-a=recOver][data-v=hp]')
    ok(until(pg, "!!rec&&rec.app&&rec.rung==='trill'&&NOW.under()==='track'", 8000), 'with headphones it records the rung over the track')
    pg.wait_for_timeout(1000)
    pg.click('#apcard [data-a=apStop]'); until(pg, "!rec", 8000); pg.wait_for_timeout(300)
    ok(not pg.evaluate("TRACK.state().playing") and pg.evaluate("TAKES[TAKES.length-1].ext.rung") == 'trill', 'the track stops with the take')
    pg.click(f'{CARD} [data-a=apSing]')
    ok(until(pg, "!!rec&&rec.rung==='hum'&&rec.over==='hp'", 8000) and pg.evaluate("U.sheet") is None, 'the hum goes straight in: headphones were said')
    pg.click('#apcard [data-a=apStop]'); until(pg, "!rec", 8000)
    pg.context.close()


def live(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg)
    ladder_on(pg)
    # the recording's microphone: its 2048 analyser hears a steady A3 (the fake microphone itself only beeps)
    pg.evaluate("""(()=>{const L=AUDIO.listen;window.__an=[];AUDIO.listen=(s)=>{const m=L(s);if(!m)return m;const A=m.analyser;
      m.analyser=(n)=>{const a=A(n);__an.push(n);if(n!==2048)return a;let ph=0;const sr=a.context.sampleRate;
      a.getFloatTimeDomainData=(buf)=>{for(let i=0;i<buf.length;i++){ph+=2*Math.PI*220/sr;buf[i]=0.3*(Math.sin(ph)+0.5*Math.sin(2*ph))}};return a};return m}})()""")
    pg.click(f'{CARD} [data-a=apSing]')
    ok(until(pg, "!!rec&&rec.livePts>10", 8000), 'while a rung records, the live line reads the voice')
    ok(until(pg, "(document.querySelector('#apLive path')||{getAttribute:()=>''}).getAttribute('d').length>20"), 'and draws it')
    st = pg.evaluate("AUDIO.state()")
    ok(st['made'] == 1 and st['users'] == 1 and pg.evaluate("__an.slice().sort((a,b)=>a-b)") == [512, 2048], 'from the recording’s own microphone: one context, the meter and one 2048 analyser')
    ok(pg.evaluate("AUDIO.state().frames") == 2, 'the meter and the line share the one frame clock')
    # nothing looked up on the page per frame: the box is found once
    calls = pg.evaluate("""async()=>{let n=0;const g=document.getElementById.bind(document);document.getElementById=(id)=>{if(id==='apLive')n++;return g(id)};
      await new Promise(r=>setTimeout(r,600));document.getElementById=g;return n}""")
    ok(calls == 0, 'the live box isn’t looked up again while it’s on screen: ' + str(calls))
    t.shot(pg, 'live')
    pg.click('#apcard [data-a=apStop]'); until(pg, "!rec", 8000); pg.wait_for_timeout(200)
    ok(pg.evaluate("AUDIO.state().frames") == 0, 'Stop lets go of the frame clock')
    pg.context.close()


def lines(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg)
    ladder_on(pg)
    sung(pg, sid, ch, 'trill', TRILL, 'l1')
    ok(pg.locator(f'{CARD} .ladsec').count() == 0, 'one rung: no Lines yet')
    sung(pg, sid, ch, 'hum', HUM, 'l2')
    ok(lines_ready(pg), 'two rungs: Lines, once they’ve been read')
    ok(pg.locator(f'{CARD} .apchart path[data-ln]').count() == 2 and pg.locator(f'{CARD} .ladchip').all_inner_texts() == ['Trill', 'Hum'],
       'both lines overlaid, each with its switch')
    ok(pg.locator(f'{CARD} .ladspot').count() == 0, 'trill and hum only: nothing to compare the words with yet')
    ok(pg.locator(f'{CARD} [data-a=apDone]').count() == 1, 'Done from two rungs')
    sung(pg, sid, ch, 'words', WORDS, 'l3')
    until(pg, "APPL.state().spot&&APPL.state().spot!=='none'", 8000)
    sp = pg.evaluate("APPL.state().spot")
    ok(sp and abs(sp['at'] - 0.5) < 0.1 and abs(sp['len'] - 0.5) < 0.1, 'the words part from the trill on the second note, aligned at the first: ' + json.dumps(sp))
    ok(sp and sp['where'] == 'on line 1 (“Hold on hold on to…”)' , 'with Song Clock timing it’s named by line: ' + (sp or {}).get('where', ''))
    txt = pg.inner_text(f'{CARD} .ladspot')
    ok('The words part from the trill on line 1' in txt and pg.locator(f'{CARD} [data-a=apHear]').count() == 1, 'it says where, with Hear both: ' + txt.replace('\n', ' | '))
    ok(pg.locator(f'{CARD} .apchart .pm').count() == 1, 'the spot is marked on the lines')
    on = pg.locator(f'{CARD} .apchart path[data-ln]').evaluate_all("p=>p.map(x=>x.dataset.ln)")
    ok(on == ['trill', 'words'], 'with three rungs, the trill and the words are drawn: ' + json.dumps(on))
    pg.click(f'{CARD} .ladchip[data-v=hum]'); pg.wait_for_timeout(100)
    ok(pg.locator(f'{CARD} .apchart path[data-ln=hum]').count() == 1 and pg.get_attribute(f'{CARD} .ladchip[data-v=hum]', 'aria-pressed') == 'true', 'a line switched on')
    pg.click(f'{CARD} .ladchip[data-v=trill]'); pg.wait_for_timeout(100)
    ok(pg.locator(f'{CARD} .apchart path[data-ln=trill]').count() == 0 and 'off' in pg.get_attribute(f'{CARD} .ladchip[data-v=trill]', 'class'), 'and off')
    # Hear both: the trill at the spot, then the words, one sound at a time
    pg.evaluate("window.__seq=[];const P=playTake;playTake=(id,at)=>{__seq.push([id,Math.round(at*100)/100]);return P(id,at)};0")
    pg.click(f'{CARD} [data-a=apHear]')
    ok(until(pg, "__seq.length===2", 8000), 'Hear both plays two clips')
    seq = pg.evaluate("__seq")
    ok(seq[0][0] == 'l1' and seq[1][0] == 'l3', 'the trill, then the words: ' + json.dumps(seq))
    ok(abs(seq[0][1] - (0.2 + sp['at'] - 0.5)) < 0.08 and abs(seq[1][1] - (0.5 + sp['at'] - 0.5)) < 0.08, 'each from just before the spot in its own take')
    ok(until(pg, "!playingId&&!APPL.state().hearing", 8000), 'and stops after the words')
    pg.context.close()

    # by time, without Song Clock timing; and lines that stay together
    pg = t.page(b, touch=True)
    sid, ch = setup(pg, timed=False)
    ladder_on(pg)
    sung(pg, sid, ch, 'trill', TRILL, 'm1')
    sung(pg, sid, ch, 'vowels', [[None, 0.4], [60, 0.5], [64, 0.5], [62, 0.5]], 'm2')
    until(pg, "APPL.state().spot==='none'", 8000)
    ok(pg.inner_text(f'{CARD} .ladspot') == 'The vowels stay with the trill all the way through.', 'no parting spot: it says so plainly: ' + pg.inner_text(f'{CARD} .ladspot'))
    sung(pg, sid, ch, 'words', WORDS, 'm3')
    until(pg, "APPL.state().spot&&APPL.state().spot!=='none'", 8000)
    ok(pg.evaluate("APPL.state().spot.where").startswith('around 0.'), 'without timing it’s named by time: ' + pg.evaluate("APPL.state().spot.where"))
    txt = pg.inner_text(CARD)
    ok(not re.search(r'\d+ ?%|score|in tune|correct|wrong', txt, re.I), 'no score, percentage or right/wrong anywhere')
    ok(pg.evaluate("JSON.stringify(localStorage)").count('firstT') == 0, 'pitch lines are never saved')
    pg.context.close()


def notes(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg)
    ladder_on(pg)
    for r, segs, n in (('trill', TRILL, 'n1'), ('hum', HUM, 'n2'), ('vowels', VOWELS, 'n3')):
        sung(pg, sid, ch, r, segs, n)
    ok(pg.locator(f'{CARD} .ladnotes').count() == 0, 'three rungs: no notes row yet')
    sung(pg, sid, ch, 'words', WORDS, 'n4')
    ok(until(pg, "!!document.querySelector('#apcard .ladnote')", 10000), 'all four sung: Notes of the line')
    ok(pg.locator(f'{CARD} .ladnote').all_inner_texts() == ['C4', 'E4', 'D4'] and pg.evaluate("APPL.state().notes") == [60, 64, 62],
       'one button per held note of the trill, labelled by note')
    ok('From your trill' in pg.inner_text(f'{CARD} .ladsec >> nth=1'), 'it says where the notes come from')
    ok(pg.locator(f'{CARD} .ladcur').count() == 0 and 'Up next' not in pg.inner_text(CARD), 'no rung left to sing')
    t.shot(pg, 'all-four')
    pg.click(f'{CARD} .ladnote >> nth=1')
    ok(pg.evaluate("[PAT.toneState()&&PAT.toneState().m,NOW.kind(),NOW.id()]") == [64, 'pattern', 'tone'], 'a tap plays E4 in the pattern player’s sound, through NOW')
    ok('on' in pg.get_attribute(f'{CARD} .ladnote >> nth=1', 'class'), 'its button lights while it plays')
    ok(until(pg, "!PAT.toneState()&&!document.querySelector('#apcard .ladnote.on')", 5000), 'without Repeat it plays once')
    pg.click(f'{CARD} [data-a=apRpt]')
    ok(pg.get_attribute(f'{CARD} [data-a=apRpt]', 'aria-pressed') == 'true', 'Repeat on')
    pg.click(f'{CARD} .ladnote >> nth=0')
    ok(until(pg, "PAT.toneState()&&PAT.toneState().strikes>=3", 6000), 'with Repeat it keeps striking, every 1.5 s')
    ok(pg.evaluate("PAT.toneState().m") == 60 and 'on' in pg.get_attribute(f'{CARD} .ladnote >> nth=0', 'class'), 'C4, lit')
    pg.click(f'{CARD} .ladnote >> nth=2')
    ok(pg.evaluate("PAT.toneState().m") == 62 and pg.locator(f'{CARD} .ladnote.on').count() == 1, 'another note takes over: one at a time')
    pg.click(f'{CARD} .ladnote >> nth=2')
    ok(pg.evaluate("!PAT.toneState()&&NOW.kind()===null") and pg.locator(f'{CARD} .ladnote.on').count() == 0, 'tapped again, it stops')
    pg.click(f'{CARD} .ladnote >> nth=0')
    pg.click(f'{CARD} [data-a=apLadFold]'); pg.wait_for_timeout(100)
    pg.click(f'{CARD} .ladrow [data-a=playTake] >> nth=0')
    ok(until(pg, "!PAT.toneState()&&NOW.kind()==='take'"), 'a take starting stops the note')
    pg.evaluate("stopPlayback();rerender()")
    pg.click(f'{CARD} .ladnote >> nth=0')
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(150)
    ok(pg.evaluate("!PAT.toneState()"), 'leaving Application stops it')
    pg.context.close()


def done(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg)
    ladder_on(pg)
    sung(pg, sid, ch, 'trill', TRILL, 'd1')
    sung(pg, sid, ch, 'words', WORDS, 'd2')
    pg.click(f'{CARD} [data-a=apDone]')
    ok(until(pg, "APPL.state().st==='done'"), 'Done')
    ok(pg.inner_text(f'{CARD} .apline .lbl') == 'Harbour Lights · Chorus 1 · Ladder · 2 takes', 'the card folds to one line: ' + pg.inner_text(f'{CARD} .apline'))
    ok(pg.inner_text('#dock [data-a=cta]').strip() == 'Finish session', 'Finish session')
    pg.click(f'{CARD} [data-a=apReopen]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("APPL.state().sung") == ['trill', 'words'], 'Edit opens the ladder where it was')
    # ladder takes are ordinary takes: the song's takes sheet, Star and Compare as now
    pg.evaluate("TAKES.find(t=>t.id==='d2').star=true;putTake(TAKES.find(t=>t.id==='d2'))")
    pg.evaluate("([id,o])=>{go(()=>{U.tab='songs';U.view='lyr';U.songId=id});U.sheet='sgTakes';U.sd={k:id,o};rerender()}", [sid, ch])
    ok(until(pg, "!!document.querySelector('.sheet')"), 'the song’s takes sheet opens')
    ok('Ladder · Lip trill' in pg.inner_text('.sheet') and 'Ladder · Words' in pg.inner_text('.sheet'), 'with the ladder takes, named by their rung')
    pg.evaluate("U.sheet=null;rerender()")
    pg.evaluate("go(()=>{U.tab='today';U.view='app'})"); pg.wait_for_timeout(150)
    pg.click(f'{CARD} [data-a=apDone]'); until(pg, "APPL.state().st==='done'")
    pg.evaluate("startFinish()"); pg.wait_for_timeout(400)
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss['ext']['app']['song'] == sid and ss['ext']['app']['o'] == ch and set(ss['takes'] if 'takes' in ss else ['d1', 'd2']) >= {'d1', 'd2'},
       'the session saves its song and takes as before')
    pg.context.close()


def data(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg)
    ladder_on(pg)
    sung(pg, sid, ch, 'trill', TRILL, 'b1')
    # a backup carries the song's switch and the take's rung, and restores them
    txt = pg.evaluate("async()=>{await prepareExport(false);return await pendingExport.file.text()}")
    p = json.loads(txt)
    ok([s for s in p['data']['songs'] if s['id'] == sid][0].get('ext') == {'ladder': True}, 'the backup has the song’s Ladder switch')
    ok([x for x in p['takes'] if x['id'] == 'b1'][0].get('ext') == {'rung': 'trill'}, 'and the take’s rung (recordings are in backups by default)')
    ok('firstT' not in txt, 'and no pitch lines')
    r = pg.evaluate("async(txt)=>{const r=await inspectBackup(txt,'b.json',txt.length);return [r.status,r.p.data.songs.find(s=>s.ext).ext,r.p.takes.find(x=>x.id==='b1').ext]}", txt)
    ok(r[0] == 'good' and r[1] == {'ladder': True} and r[2] == {'rung': 'trill'}, 'Check a backup keeps both: ' + json.dumps(r))
    # extras this version doesn't know are kept; damaged ones dropped
    cl = pg.evaluate("""[cleanSong({id:'x',name:'X',ext:{ladder:true,later:{a:1}}}).ext,cleanSong({id:'x',name:'X',ext:{ladder:'yes',later:1}}).ext,
      'ext' in cleanSong({id:'x',name:'X',ext:'bad'}),'ext' in cleanSong({id:'x',name:'X'})]""")
    ok(cl == [{'ladder': True, 'later': {'a': 1}}, {'later': 1}, False, False], 'cleanSong keeps unknown extras, drops a bad ladder value and a bad ext: ' + json.dumps(cl))
    # a take with a rung this version doesn't know is an ordinary take
    pg.evaluate("MKTAKE(['b2','%s','%s',[[60,1]],{rung:'kazoo'}])" % (sid, ch))
    ok(pg.evaluate("TAKE.short('b2')").startswith('Take ') and not pg.evaluate("takeRung(TAKES.find(t=>t.id==='b2'))"), 'an unknown rung is an ordinary take')
    pg.context.close()
    # old data loads unchanged: the sample (3.1-shaped) and a 3.51 song without ext
    pg = t.page(b, touch=True)
    ok(pg.evaluate("songById('g_1').ext") is None and pg.evaluate("D.songs.length") == 1, 'old data loads with no ladder fields added')
    to_app(pg)
    pg.click('#app [data-a=apSong][data-k=g_1]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("APPL.state().ladder") is False and pg.locator(f'{CARD} .apmode').count() == 1, 'and every song starts on Straight')
    pg.context.close()


def sizes(b, t):
    ok = t.ok
    for w, h in ((375, 667), (390, 844)):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, touch=True)
            sid, ch = setup(pg)
            ladder_on(pg)
            for r, segs, n in (('trill', TRILL, 's1'), ('hum', HUM, 's2'), ('vowels', VOWELS, 's3'), ('words', WORDS, 's4')):
                sung(pg, sid, ch, r, segs, n)
            until(pg, "!!document.querySelector('#apcard .ladnote')", 10000)
            pg.click(f'{CARD} [data-a=apLadFold]'); pg.wait_for_timeout(150)
            ok(pg.evaluate(WIDE), f'{w} {sc}: no sideways scroll with everything open')
            ok(pg.evaluate("[...document.querySelectorAll('#apcard .ladrow, #apcard .ladsum, #apcard .apchart')].every(e=>e.getBoundingClientRect().right<=innerWidth)"),
               f'{w} {sc}: the rows and lines fit the card')
            body = pg.inner_text('#app')
            ok(not re.search(r'undefined|NaN|null', body), f'{w} {sc}: no undefined, NaN or null on screen')
            pg.evaluate("document.querySelector('#apcard').scrollIntoView()")
            t.shot(pg, f'{w}-{sc}', full_page=True)
            pg.context.close()
    # Reduce Motion: the fold still opens, without moving
    pg = t.page(b, touch=True, init="try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}")
    sid, ch = setup(pg)
    ladder_on(pg)
    sung(pg, sid, ch, 'trill', TRILL, 'r1')
    pg.click(f'{CARD} [data-a=apLadFold]')
    ok(until(pg, "document.querySelectorAll('#apcard .ladrow').length===1"), 'Reduce Motion: the fold opens')
    pg.context.close()


PARTS = {'switch': switch, 'rungs': rungs, 'live': live, 'lines': lines, 'notes': notes, 'done': done, 'data': data, 'sizes': sizes}


def run(b, t):
    want = [p for p in os.environ.get('VS_LADDER', ','.join(PARTS)).split(',') if p]
    for k in want: PARTS[k](b, t)
