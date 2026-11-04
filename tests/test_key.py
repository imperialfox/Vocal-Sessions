"""Q39 the song key and scale lanes (SONGKEY, js/key.js): musictheoryjs (detectKey) and tonal (Scale, Note, Key) pinned as
classic scripts with their notices; the key found from every take's steady frames, asked when the top two are close
and suggested otherwise; the key sheet (VS-098: Major / Minor and 12 notes spelled for the key) from Lines and the
song page's Key row (VS-009), saved on the song (ext.key) and in backups; scale lanes on Lines and the live line
(spelled B♭4, not A♯4; the home note in the accent; a chip turns them off on this device); Practise in <key> (the note
at the parting spot or the line's top note, up to three LIB patterns in the key that peak on it, one per group, riffs
first, none below A2, or patterns that pass through it); Play through NOW; › into the pattern player (VS-097) on that
pattern and note, staying on the key, never changing an exercise's saved choices; Q37's note buttons matched to the
key; old data and bad keys; 375 and 390 in light and dark. Synthetic melodies (a G major tune, an A minor blues line,
a line that fits F major and D minor) and a fake microphone only.
`VS_KEY=lib,find,spell,suggest,lines,sheet,player,notes,data,sizes` runs only those parts."""
import os, json, re
from harness import until
from test_ladder import setup, ladder_on, sung, lines_ready, CARD, WIDE
from test_pitch import VOICE

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']

# synthetic melodies, as MKTAKE segments [midi or None, seconds]
G_TUNE = [[None, 0.2], [67, .4], [69, .4], [71, .4], [72, .4], [74, .6], [76, .4], [78, .4], [79, .8], [74, .4], [71, .4], [67, .8]]
A_BLUES = [[None, 0.2], [57, .6], [60, .4], [62, .4], [63, .3], [64, .6], [67, .4], [69, .8], [67, .4], [64, .4], [60, .4], [57, .8]]
# fits F major and D minor (as in the prototype): the trill, then the words, which part from it on the A4
FD_TRILL = [[None, 0.2], [62, .4], [64, .4], [65, .4], [67, .4], [65, .4], [69, .6], [67, .4], [70, .4], [65, .8]]
FD_WORDS = [[None, 0.2], [62, .4], [64, .4], [65, .4], [67, .4], [65, .4], [67, .6], [67, .4], [70, .4], [65, .8]]
PROF = "(segs)=>{const a=PITCH.line(VOICE(segs,44100),44100);const p=SONGKEY.profile([a]);return SONGKEY.verdict(p.h,p.n)}"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lib(b, t):
    ok = t.ok
    pg = t.page(b)
    ok(pg.evaluate("typeof MusicTheory.detectKey==='function'&&typeof Tonal.Scale.get==='function'&&typeof Tonal.Note.midi==='function'&&typeof Tonal.Key.majorKey==='function'&&SONGKEY.has()"),
       'both libraries are classic scripts: MusicTheory.detectKey and Tonal.Scale, Note and Key')
    for f, words in (('musictheory.js', ['musictheoryjs 3.2.2', 'ISC License', 'Zach Moore', 'https://']), ('tonal.js', ['tonal 6.5.1', 'MIT License', 'danigb', 'https://'])):
        src = open(os.path.join(ROOT, 'js', f), encoding='utf-8').read()
        ok(all(w in src[:2000] for w in words), f'{f}: pinned, with its version and notice at the top')
        ok(len(src) < 40000, f'{f}: only what’s used ({len(src)} bytes)')
    ok(pg.evaluate("Tonal.Scale.get('F major').notes.join(' ')") == 'F G A Bb C D E', 'tonal spells F major with B♭')
    pg.context.close()


def find(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(VOICE)
    v = pg.evaluate(PROF, G_TUNE)
    ok(v['st'] == 'suggest' and v['top'][0]['tonic'] == 'G' and v['top'][0]['mode'] == 'major', 'a G major tune: it suggests G major (' + json.dumps(v['top']) + ')')
    v = pg.evaluate(PROF, A_BLUES)
    ok(v['st'] == 'suggest' and v['top'][0] == {**v['top'][0], 'tonic': 'A', 'mode': 'minor'}, 'an A minor blues line: it suggests A minor')
    v = pg.evaluate(PROF, FD_TRILL)
    ok(v['st'] == 'ask' and [(x['tonic'], x['mode']) for x in v['top']] == [('F', 'major'), ('D', 'minor')],
       'a line that fits two related keys: it asks, F major or D minor (' + json.dumps(v['top']) + ')')
    ok(abs(v['top'][0]['score'] - v['top'][1]['score']) <= 0.15, 'because the top two are within 0.15')
    v = pg.evaluate(PROF, [[None, .2], [60, .5]])
    ok(v['st'] == 'few', 'half a second of one note: not enough to hear the key')
    ok(pg.evaluate("SONGKEY.verdict(null,0).st") == 'none', 'no takes: nothing to go on')
    # only steady frames count (within 0.25 of both neighbours): a quick swoop adds next to nothing, a held note all of it
    n = pg.evaluate("(segs)=>SONGKEY.profile([PITCH.line(VOICE(segs,44100),44100)]).n", [[None, .2], [60, .25, {'to': 72}]])
    n2 = pg.evaluate("(segs)=>SONGKEY.profile([PITCH.line(VOICE(segs,44100),44100)]).n", [[None, .2], [60, .25]])
    ok(n < 6 and n2 > 15, f'a quick swoop has almost no steady frames ({n}); a held note of the same length has them ({n2})')
    # spelled as on the key sheet
    sp = pg.evaluate("[SONGKEY.find([0,0,0,0,0,0,0,0,0,0,0,0]).length,SONGKEY.find((()=>{const h=Array(12).fill(0);[1,3,5,6,8,10,0].forEach(p=>h[p]+=3);h[1]+=6;return h})())[0]]")
    ok(sp[0] == 0 and sp[1]['tonic'] == 'Db' and sp[1]['mode'] == 'major', 'a D♭ major profile is spelled D♭, not C♯: ' + json.dumps(sp[1]))
    pg.context.close()


def spell(b, t):
    ok = t.ok
    pg = t.page(b)
    L = pg.evaluate("SONGKEY.lanes({tonic:'F',mode:'major'},64,72)")
    ok([x['name'] for x in L] == ['E4', 'F4', 'G4', 'A4', 'B♭4', 'C5'] and [x['m'] for x in L] == [64, 65, 67, 69, 70, 72],
       'F major lanes from E4 to C5: ' + ' '.join(x['name'] for x in L))
    ok([x['name'] for x in L if x['home']] == ['F4'], 'the home note is F4')
    ok(pg.evaluate("SONGKEY.lanes({tonic:'E',mode:'major'},63,68).map(x=>x.name).join(' ')") == 'D♯4 E4 F♯4 G♯4', 'a sharp key: E major has D♯, F♯, G♯')
    ok(pg.evaluate("SONGKEY.lanes({tonic:'Eb',mode:'minor'},58,64).map(x=>x.name).join(' ')") == 'B♭3 C♭4 D♭4 E♭4', 'a flat key: E♭ minor is spelled by tonal (C♭4)')
    ok(pg.evaluate("SONGKEY.lanes({tonic:'C#',mode:'minor'},59,61).map(x=>x.name).join(' ')") == 'B3 C♯4', 'C♯ minor keeps C♯')
    ok(pg.evaluate("[SONGKEY.snap(69.4,{tonic:'F',mode:'major'}),SONGKEY.snap(68.4,{tonic:'F',mode:'major'}),SONGKEY.snap(66,{tonic:'F',mode:'major'})]") == [69, 69, 65],
       'notes snap to the nearer scale note (a tie goes down)')
    ok(pg.evaluate("[SONGKEY.degree(69,{tonic:'F',mode:'major'}),SONGKEY.degree(65,{tonic:'F',mode:'major'}),SONGKEY.degree(62,{tonic:'D',mode:'minor'})]") == ['3rd', 'home note', 'home note'],
       'A is the 3rd of F major; F and D are home notes')
    ok(pg.evaluate("[SONGKEY.valid({tonic:'Bb',mode:'minor'}),SONGKEY.valid({tonic:'A#',mode:'major'}),SONGKEY.valid({tonic:'Db',mode:'minor'}),SONGKEY.valid({tonic:'C#',mode:'minor'}),SONGKEY.valid({tonic:'C',mode:'lydian'})]") == [True, False, False, True, False],
       'a saved key is one of the 24 as the sheet spells them')
    ok(pg.evaluate("SONGKEY.label({tonic:'Bb',mode:'major'})") == 'B♭ major', 'labels use ♭ and ♯')
    pg.context.close()


def suggest(b, t):
    ok = t.ok
    pg = t.page(b)
    CHECK = """([k,m])=>{const S=new Set(Tonal.Scale.get(k.tonic+' '+k.mode).notes.map(n=>Tonal.Note.chroma(n))),tp=Tonal.Note.chroma(k.tonic);
      return SONGKEY.suggest(k,m).map(r=>{const ns=r.p.semi.filter(v=>v!==null).map(v=>r.kn+v);
        return {n:r.p.n,g:r.p.g,exact:r.exact,home:((r.kn%12)+12)%12===tp,inKey:ns.every(x=>S.has(((x%12)+12)%12)),low:Math.min(...ns),top:Math.max(...ns),hits:ns.includes(m)}})}"""
    for k, m, nm in (({'tonic': 'F', 'mode': 'major'}, 69, 'F major, A4'), ({'tonic': 'D', 'mode': 'minor'}, 69, 'D minor, A4'), ({'tonic': 'G', 'mode': 'major'}, 74, 'G major, D5')):
        rows = pg.evaluate(CHECK, [k, m])
        ok(1 <= len(rows) <= 3, f'{nm}: up to three patterns ({len(rows)})')
        ok(all(r['exact'] and r['home'] and r['inKey'] and r['low'] >= 45 and r['top'] == m for r in rows),
           f'{nm}: each in the key from its home note, every note in the key, none below A2, peaking on the target: ' + json.dumps(rows))
        gs = [r['g'] for r in rows]
        ok(len(set(gs)) == len(gs) or len(rows) == 3, f'{nm}: one per group where possible ({gs})')
        if 'r' in gs: ok(gs[0] == 'r', f'{nm}: riffs first')
    # every key's own minor patterns only appear in minor keys: nothing with a ♭3 in F major
    mins = pg.evaluate("SONGKEY.suggest({tonic:'F',mode:'major'},69).filter(r=>PAT.isMinor(r.p)).length")
    ok(mins == 0, 'no minor pattern is offered in a major key')
    # the fallback: where nothing peaks on the note, patterns that pass through it
    fb = pg.evaluate("""()=>{for(const mode of ['major','minor'])for(const tonic of (mode==='major'?SONGKEY.MAJ:SONGKEY.MIN))for(let m=48;m<=79;m++){
        const k={tonic,mode},r=SONGKEY.suggest(k,m);if(r.length&&!r[0].exact)return {k,m,r:r.map(x=>({n:x.p.n,kn:x.kn,exact:x.exact,hits:x.p.semi.some(v=>v!==null&&x.kn+v===m)}))}}return null}""")
    ok(fb is not None and all(not x['exact'] and x['hits'] for x in fb['r']), 'where nothing peaks on the note, the patterns pass through it: ' + json.dumps(fb)[:200])
    ok(pg.evaluate("SONGKEY.suggest({tonic:'C',mode:'major'},44).length") == 0, 'nothing below A2 is ever offered (a target of G♯2)')
    pg.context.close()


def to_lines(pg, trill=FD_TRILL, words=FD_WORDS, ids=('k1', 'k2')):
    sid, ch = setup(pg, timed=False)
    ladder_on(pg)
    sung(pg, sid, ch, 'trill', trill, ids[0])
    sung(pg, sid, ch, 'words', words, ids[1])
    lines_ready(pg)
    return sid, ch


def lines(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = to_lines(pg)
    ok(until(pg, "!!document.querySelector('#apcard .keyblk [data-a=keyUse]')", 10000), 'Lines: the song key, from the takes')
    txt = pg.inner_text(f'{CARD} .keyblk')
    ok('Which key is this song in?' in txt and pg.locator(f'{CARD} [data-a=keyUse]').all_inner_texts() == ['F major', 'D minor'] and 'Other…' in txt,
       'close keys: it asks, with both and Other…: ' + txt.replace('\n', ' | '))
    ok('From your takes. You only choose once for each song.' in txt, 'and says where it came from')
    ok(pg.locator(f'{CARD} .plane').count() == 0 and pg.locator(f'{CARD} .keychip').count() == 0, 'no lanes before there’s a key')
    pg.evaluate("document.querySelector('#apcard .apchart').scrollIntoView()")
    t.shot(pg, 'ask')
    pg.click(f'{CARD} [data-a=keyUse] >> nth=0')
    ok(pg.evaluate("id=>songById(id).ext", sid) == {'ladder': True, 'key': {'tonic': 'F', 'mode': 'major'}}, 'F major is saved on the song, beside the ladder switch')
    ok(pg.evaluate("id=>JSON.parse(localStorage.getItem('vocalTracker')).songs.find(s=>s.id===id).ext.key", sid) == {'tonic': 'F', 'mode': 'major'}, 'and stored')
    ok('F major' in pg.inner_text(f'{CARD} .keyblk') and pg.locator(f'{CARD} .keyblk [data-a=keyChange]').inner_text() == 'Change', 'it shows the key, with Change')
    # lanes
    ok(pg.locator(f'{CARD} .apchart .plane').count() >= 5 and pg.locator(f'{CARD} .apchart .plane.home').count() >= 1, 'scale lanes on Lines, the home note marked')
    labels = pg.locator(f'{CARD} .apchart text.pn').evaluate_all("e=>e.map(x=>x.textContent)")
    ok('B♭4' in labels and not any('♯' in x for x in labels) and pg.locator(f'{CARD} .apchart text.pn.home').evaluate_all("e=>e.map(x=>x.textContent)")[0].startswith('F'),
       'lanes spelled for F major (B♭4, no sharps), the home F in the accent: ' + ' '.join(labels))
    ok(pg.locator(f'{CARD} .apchart path[data-ln]').count() == 2, 'the lines are drawn on top, as before (no colouring)')
    ok(pg.locator(f'{CARD} .keychip').inner_text() == 'Scale lanes' and pg.get_attribute(f'{CARD} .keychip', 'aria-pressed') == 'true', 'a Scale lanes chip, on')
    pg.click(f'{CARD} .keychip')
    ok(pg.locator(f'{CARD} .apchart .plane').count() == 0 and pg.evaluate("JSON.parse(localStorage.getItem('vocalLook')).lanes") is False,
       'off: no lanes, remembered on this device (vocalLook.lanes)')
    ok('lanes' not in json.dumps(pg.evaluate("id=>songById(id)", sid)), 'not on the song or in its backup')
    pg.click(f'{CARD} .keychip')
    ok(pg.locator(f'{CARD} .apchart .plane').count() >= 5 and 'lanes' not in pg.evaluate("localStorage.getItem('vocalLook')||''"), 'on again')
    # Practise in F major
    ok(until(pg, "!!document.querySelector('#apcard .keyprac .keypat')"), 'Practise in F major, with patterns')
    tg = pg.inner_text(f'{CARD} .keytgt')
    ok(re.match(r'Where the words part \(around [\d.]+ s\) sits on A4, the 3rd of F major\.', tg) is not None, 'the target: the trill’s held note where the words part: ' + tg)
    st = pg.evaluate("SONGKEY.state()")
    ok(1 <= len(st['shown']) <= 3 and all(r['hi'] == 69 and r['exact'] and (r['kn'] - 65) % 12 == 0 for r in st['shown']),
       'up to three patterns in F major peaking on A4: ' + json.dumps(st['shown']))
    row = pg.inner_text(f'{CARD} .keypat >> nth=0')
    ok(re.search(r' · [A-G]♭?\d–A4', row) and len(row.split('\n')) >= 2, 'each row shows its range and what it trains: ' + row.replace('\n', ' | '))
    pg.evaluate("document.querySelector('#apcard .apchart').scrollIntoView()")
    t.shot(pg, 'practise')
    # Play: once in the key, through NOW, one sound at a time
    pg.click(f'{CARD} [data-a=keyHear] >> nth=0')
    n0 = st['shown'][0]['n']
    ok(pg.evaluate("[PAT.state().preview,NOW.kind(),NOW.id()]") == [n0, 'pattern', 'preview'], 'Play plays it in the pattern player’s sound, through NOW')
    ok(pg.get_attribute(f'{CARD} [data-a=keyHear] >> nth=0', 'aria-label').startswith('Stop'), 'its button becomes Stop')
    pg.click(f'{CARD} [data-a=keyHear] >> nth=0')
    ok(pg.evaluate("PAT.state().preview===null&&NOW.kind()===null") and pg.get_attribute(f'{CARD} [data-a=keyHear] >> nth=0', 'aria-label').startswith('Play'), 'tapped again, it stops')
    pg.click(f'{CARD} [data-a=keyHear] >> nth=0')
    pg.click(f'{CARD} [data-a=apHear]')
    ok(until(pg, "PAT.state().preview===null&&NOW.kind()==='take'"), 'Hear both starting stops it')
    pg.evaluate("stopPlayback();rerender()")
    txt = pg.inner_text(CARD)
    ok(not re.search(r'\d+ ?%|score|in tune|correct|wrong', txt, re.I), 'no score, percentage or right/wrong anywhere')
    # the live line while the next rung records: the same lanes (the recording's microphone hears a steady A3)
    pg.evaluate("""(()=>{const L=AUDIO.listen;AUDIO.listen=(s)=>{const m=L(s);if(!m)return m;const A=m.analyser;
      m.analyser=(n)=>{const a=A(n);if(n!==2048)return a;let ph=0;const sr=a.context.sampleRate;
      a.getFloatTimeDomainData=(buf)=>{for(let i=0;i<buf.length;i++){ph+=2*Math.PI*220/sr;buf[i]=0.3*(Math.sin(ph)+0.5*Math.sin(2*ph))}};return a};return m}})()""")
    pg.click(f'{CARD} [data-a=apSing]')
    ok(until(pg, "!!rec&&rec.livePts>10", 8000) and until(pg, "document.querySelectorAll('#apLive .plane').length>=5"), 'the live line has the scale lanes too')
    ok(pg.locator('#apLive .plane.home').count() >= 1, 'with the home note marked')
    pg.click('#apcard [data-a=apStop]'); until(pg, "!rec", 8000)
    pg.context.close()

    # a key it's sure of: "This sounds like G major" with Use; and top note when the words stay with the trill
    pg = t.page(b, touch=True)
    sid, ch = to_lines(pg, G_TUNE, G_TUNE, ('g1', 'g2'))
    ok(until(pg, "!!document.querySelector('#apcard .keyblk .keyuse')", 10000), 'a clear key: one suggestion')
    txt = pg.inner_text(f'{CARD} .keyblk')
    ok('This sounds like G major' in txt and pg.inner_text(f'{CARD} .keyuse') == 'Use' and 'Other…' in txt, 'This sounds like G major, Use, Other…')
    pg.click(f'{CARD} .keyuse')
    ok(pg.evaluate("id=>songById(id).ext.key", sid) == {'tonic': 'G', 'mode': 'major'}, 'Use saves G major')
    until(pg, "!!document.querySelector('#apcard .keytgt')")
    ok(pg.inner_text(f'{CARD} .keytgt') == 'The line’s top note sits on G5, the home note of G major.', 'no parting spot: the line’s top note: ' + pg.inner_text(f'{CARD} .keytgt'))
    ln = pg.evaluate("SONGKEY.lanes({tonic:'G',mode:'major'},64,80).map(x=>x.name)")
    labels = pg.locator(f'{CARD} .apchart text.pn').evaluate_all("e=>e.map(x=>x.textContent)")
    ok('F♯5' in ln and not any('♭' in x for x in labels) and pg.locator(f'{CARD} .apchart .plane').count() >= 7, 'G major lanes have F♯ and no flats: ' + ' '.join(labels))
    pg.context.close()


def sheet(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = to_lines(pg)
    until(pg, "!!document.querySelector('#apcard [data-a=keyUse]')", 10000)
    pg.click(f'{CARD} .keyblk [data-a=keyChange]')
    ok(until(pg, "document.querySelector('#layer [data-screen]')&&document.querySelector('#layer [data-screen]').dataset.screen==='VS-098'") or pg.evaluate("U.sheet") == 'keyPick',
       'Other… opens the key sheet (VS-098)')
    ok(pg.evaluate("[U.sd.tonic,U.sd.mode]") == ['F', 'major'], 'starting on the key it heard best')
    ok(pg.locator('.keygrid .ladnote').all_inner_texts() == ['C', 'D♭', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B'], 'Major: 12 notes spelled for major keys')
    t.shot(pg, 'sheet-major')
    pg.click('.keymode [data-a=keyMode][data-v=minor]')
    ok(pg.locator('.keygrid .ladnote').all_inner_texts() == ['C', 'C♯', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'B♭', 'B'], 'Minor: with C♯ and G♯')
    ok(pg.inner_text('[data-a=keySave]') == 'Use F minor', 'the note stays, the mode changes')
    pg.click('.keygrid [data-a=keyNote][data-v="C#"]')
    ok(pg.inner_text('[data-a=keySave]') == 'Use C♯ minor' and pg.locator('.keygrid .ladnote.on').inner_text() == 'C♯', 'C♯ picked')
    pg.click('.keymode [data-a=keyMode][data-v=major]')
    ok(pg.inner_text('[data-a=keySave]') == 'Use D♭ major', 'the same note in major is spelled D♭')
    pg.click('.keymode [data-a=keyMode][data-v=minor]')
    pg.click('[data-a=keySave]')
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("id=>songById(id).ext.key", sid) == {'tonic': 'C#', 'mode': 'minor'}, 'Use saves C♯ minor and closes the sheet')
    ok('C♯ minor' in pg.inner_text(f'{CARD} .keyblk'), 'Lines shows it')
    # the song page's Key row
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id})", sid); pg.wait_for_timeout(200)
    row = pg.locator('#app .grp [data-a=keyChange]')
    ok(row.count() == 1 and 'Key' in row.inner_text() and 'C♯ minor' in row.inner_text(), 'the song page has a Key row: ' + row.inner_text().replace('\n', ' | '))
    ok(row.get_attribute('data-name') == 'key-row', 'named VS-009 › key-row')
    row.click()
    ok(until(pg, "U.sheet==='keyPick'") and pg.evaluate("[U.sd.tonic,U.sd.mode]") == ['C#', 'minor'], 'it opens the sheet on the song’s key')
    pg.click('.keymode [data-a=keyMode][data-v=major]')
    pg.click('.keygrid [data-a=keyNote][data-v=Bb]')
    pg.click('[data-a=keySave]')
    ok(pg.evaluate("id=>songById(id).ext.key", sid) == {'tonic': 'Bb', 'mode': 'major'} and 'B♭ major' in pg.inner_text('#app .grp [data-a=keyChange]'), 'changed to B♭ major from the song page')
    pg.context.close()
    # a song without takes: Not set
    pg = t.page(b, touch=True)
    pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId='g_1'})"); pg.wait_for_timeout(200)
    ok('Not set' in pg.inner_text('#app .grp [data-a=keyChange]'), 'a song with no key: Not set')
    pg.click('#app .grp [data-a=keyChange]')
    ok(until(pg, "U.sheet==='keyPick'") and pg.evaluate("[U.sd.tonic,U.sd.mode]") == ['C', 'major'], 'the sheet starts on C major')
    pg.context.close()


def player(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = to_lines(pg)
    until(pg, "!!document.querySelector('#apcard [data-a=keyUse]')", 10000)
    pg.click(f'{CARD} [data-a=keyUse] >> nth=0')
    until(pg, "!!document.querySelector('#apcard .keypat')")
    pg.evaluate("D.prefs=D.prefs||{};D.prefs.pat=Object.assign({ex:{lip:{p:3,off:2}},spd:{}},D.prefs.pat||{});save()")
    before = pg.evaluate("JSON.stringify(D.prefs.pat.ex)")
    r = pg.evaluate("SONGKEY.state().shown[0]")
    pg.click(f'{CARD} [data-a=keyGo] >> nth=0')
    ok(until(pg, "U.view==='keyp'"), '› opens Practise in F major')
    ok(pg.get_attribute('#app', 'data-screen') == 'VS-097', 'VS-097 · Practise in key')
    ok(pg.inner_text('#barT') == 'Practise in F major' and 'A4, the 3rd' in pg.inner_text('#app'), 'its title and the note: ' + pg.inner_text('#app .keysub'))
    s = pg.evaluate("PAT.state()")
    ok(s['guest'] and s['pattern'] == r['n'] and s['route'] == [r['kn']] and s['hold'] is True, 'the pattern player on that pattern and note, Stay on this key on: ' + json.dumps({k: s[k] for k in ('pattern', 'route', 'hold')}))
    ok(pg.locator('#app #pcCard').count() == 1 and pg.locator('#dock #pPlay').count() == 1 and pg.get_attribute('#pRep', 'aria-pressed') == 'true', 'its drawing and its dock, with Stay on this key on')
    ok(pg.get_attribute('#pRep', 'data-name') == 'stay-on-key-button', 'parts named on VS-097')
    t.shot(pg, 'player')
    pg.click('#pPlay')
    ok(until(pg, "PAT.state().playing&&PAT.state().runs.length>=1"), 'Play')
    ok(pg.evaluate("PAT.state().runs.slice(-1)[0]") == {**pg.evaluate("PAT.state().runs.slice(-1)[0]"), 'k': r['kn'], 'n': r['n'], 'hold': True}, 'it plays that pattern from that note, holding the key')
    pg.click('#pPlay')
    ok(until(pg, "!PAT.state().playing"), 'Stop')
    pg.click('#dock [data-a=patShift][data-v="1"]')
    ok(pg.evaluate("PAT.state().route") == [r['kn'] + 1], 'the starting note can move')
    # the Patterns page from here, and back
    pg.click('#dock [data-a=patOpen]')
    ok(until(pg, "U.view==='pat'"), 'the pattern pill opens Patterns')
    pg.click('#app [data-a=patGroup][data-v=w]')
    pg.click('#app #pTiles [data-a=patPick][data-v="2"]')
    ok(pg.evaluate("PAT.state().pattern") == 2, 'a pattern picked')
    pg.click('#barL [data-a=patBack]')
    ok(until(pg, "U.view==='keyp'") and pg.evaluate("PAT.state().pattern") == 2, 'Back returns to Practise in F major, with the new pattern')
    ok(pg.evaluate("JSON.stringify(D.prefs.pat.ex)") == before and 'song:' not in pg.evaluate("localStorage.getItem('vocalTracker')"),
       'no exercise’s saved choices changed, and nothing about the guest saved')
    pg.click('#barL [data-a=keyBack]')
    ok(until(pg, "U.view==='app'") and pg.locator(f'{CARD} .keyprac').count() == 1, 'Back returns to Application’s Lines')
    # an exercise page afterwards is itself again
    pg.evaluate("go(()=>{U.tab='exercises';U.view='ex';U.exId='lip';U.exTab='summary'})"); pg.wait_for_timeout(200)
    s = pg.evaluate("PAT.state()")
    ok(not s['guest'] and s['key'] == 'lip' and s['pattern'] == 3 and s['hold'] is False, 'an exercise page has its own pattern and choices: ' + json.dumps({k: s[k] for k in ('key', 'pattern', 'hold')}))
    pg.context.close()


def notes(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid, ch = setup(pg, timed=False)
    ladder_on(pg)
    # the trill a little flat on its second note: matched to the key, it's the nearer scale note
    trill = [[None, 0.2], [65, .5], [68.6, .5], [70, .5]]
    for r, segs, n in (('trill', trill, 'n1'), ('hum', trill, 'n2'), ('vowels', trill, 'n3'), ('words', trill, 'n4')):
        sung(pg, sid, ch, r, segs, n)
    ok(until(pg, "!!document.querySelector('#apcard .ladnote')", 10000), 'all four sung')
    ok(pg.evaluate("APPL.state().notes") == [65, 69, 70], 'with no key, the nearest notes: ' + json.dumps(pg.evaluate("APPL.state().notes")))
    pg.evaluate("id=>{SONGKEY.set(songById(id),{tonic:'F',mode:'major'});rerender()}", sid)
    until(pg, "!!document.querySelector('#apcard .ladnote')")
    ok(pg.evaluate("APPL.state().notes") == [65, 69, 70], 'with F major: A4 and B♭4 are in the key')
    ok(pg.locator(f'{CARD} .ladnote').all_inner_texts() == ['F4', 'A4', 'B♭4'], 'and spelled for it: ' + ' '.join(pg.locator(f'{CARD} .ladnote').all_inner_texts()))
    ok('From your trill, matched to F major' in pg.inner_text(CARD), 'it says they’re matched to F major')
    pg.evaluate("id=>{SONGKEY.set(songById(id),{tonic:'Eb',mode:'major'});rerender()}", sid)
    until(pg, "!!document.querySelector('#apcard .ladnote')")
    ok(pg.evaluate("APPL.state().notes") == [65, 68, 70] and pg.locator(f'{CARD} .ladnote').all_inner_texts() == ['F4', 'A♭4', 'B♭4'],
       'in E♭ major the flat second note snaps to A♭4: ' + json.dumps(pg.evaluate("APPL.state().notes")))
    pg.context.close()


def data(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate("SONGKEY.set(songById('g_1'),{tonic:'Eb',mode:'major'})")
    txt = pg.evaluate("async()=>{await prepareExport(false);return await pendingExport.file.text()}")
    p = json.loads(txt)
    ok([s for s in p['data']['songs'] if s['id'] == 'g_1'][0].get('ext') == {'key': {'tonic': 'Eb', 'mode': 'major'}}, 'the backup has the song’s key')
    r = pg.evaluate("async(txt)=>{const r=await inspectBackup(txt,'b.json',txt.length);return [r.status,r.p.data.songs[0].ext]}", txt)
    ok(r == ['good', {'key': {'tonic': 'Eb', 'mode': 'major'}}], 'Check a backup keeps it: ' + json.dumps(r))
    cl = pg.evaluate("""[cleanSong({id:'x',name:'X',ext:{key:{tonic:'F',mode:'minor',later:1},ladder:true}}).ext,
      cleanSong({id:'x',name:'X',ext:{key:{tonic:'H',mode:'major'},later:2}}).ext,
      cleanSong({id:'x',name:'X',ext:{key:'F major'}}).ext,
      'ext' in cleanSong({id:'x',name:'X'})]""")
    ok(cl == [{'key': {'tonic': 'F', 'mode': 'minor', 'later': 1}, 'ladder': True}, {'later': 2}, {}, False],
       'cleanSong keeps a good key (and fields it doesn’t know), drops a bad one, keeps the rest: ' + json.dumps(cl))
    pg.evaluate("SONGKEY.set(songById('g_1'),null)")
    ok(pg.evaluate("songById('g_1').ext") is None, 'clearing the key leaves no empty ext')
    pg.context.close()
    pg = t.page(b, touch=True)
    ok(pg.evaluate("songById('g_1').ext") is None and pg.evaluate("SONGKEY.of(songById('g_1'))") is None, 'old data loads with no key')
    ok(pg.evaluate("localStorage.getItem('vocalLook')") is None and pg.evaluate("SONGKEY.lanesOn()"), 'scale lanes are on by default, with nothing saved')
    pg.context.close()


def sizes(b, t):
    ok = t.ok
    for w, h in ((375, 667), (390, 844)):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, touch=True)
            sid, ch = to_lines(pg)
            until(pg, "!!document.querySelector('#apcard [data-a=keyUse]')", 10000)
            pg.click(f'{CARD} [data-a=keyUse] >> nth=0')
            until(pg, "!!document.querySelector('#apcard .keypat')")
            ok(pg.evaluate(WIDE), f'{w} {sc}: no sideways scroll on Lines with the key')
            ok(pg.evaluate("[...document.querySelectorAll('#apcard .keypat, #apcard .keyblk, #apcard .apchart')].every(e=>e.getBoundingClientRect().right<=innerWidth)"),
               f'{w} {sc}: the key and the patterns fit the card')
            ok(not re.search(r'undefined|NaN|null', pg.inner_text('#app')), f'{w} {sc}: no undefined, NaN or null on screen')
            pg.evaluate("document.querySelector('#apcard .keyprac').scrollIntoView()")
            t.shot(pg, f'lines-{w}-{sc}')
            pg.click(f'{CARD} .keyblk [data-a=keyChange]')
            until(pg, "U.sheet==='keyPick'")
            ok(pg.evaluate("[...document.querySelectorAll('.keygrid .ladnote')].every(e=>e.getBoundingClientRect().right<=innerWidth)"), f'{w} {sc}: the key sheet fits')
            t.shot(pg, f'sheet-{w}-{sc}')
            pg.evaluate("U.sheet=null;rerender()")
            pg.click(f'{CARD} [data-a=keyGo] >> nth=0')
            until(pg, "U.view==='keyp'")
            ok(pg.evaluate(WIDE) and not re.search(r'undefined|NaN|null', pg.inner_text('#app')), f'{w} {sc}: Practise in F major fits')
            t.shot(pg, f'player-{w}-{sc}')
            pg.context.close()


PARTS = {'lib': lib, 'find': find, 'spell': spell, 'suggest': suggest, 'lines': lines, 'sheet': sheet, 'player': player, 'notes': notes, 'data': data, 'sizes': sizes}


def run(b, t):
    want = [p for p in os.environ.get('VS_KEY', ','.join(PARTS)).split(',') if p]
    for k in want: PARTS[k](b, t)
