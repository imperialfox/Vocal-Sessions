"""Q03 · Marks: Layered Annotations: the older Annotate marks moving across (from saved data and an old backup), checking
saved marks, every mark drawn as the spec says, selecting words, the marks sheet (every mark, options, text, removing
and Undo), linked repeats, marks following their words, the layer chips, Recall, Marks while playing, marking while
listening, and every size in light and dark.
VS_MARKS=data,draw,sheet,views,listen,sizes runs only those parts."""
import json, os, tempfile, hashlib
from harness import sample, with_song_practice, ready, url, APP_PATH

PARTS = set((os.environ.get('VS_MARKS') or 'data,draw,sheet,views,listen,sizes').split(','))

# invented lines (the repo is public: never real lyrics)
LYR = ("[Verse]\nPaper boats along the gutter\nRacing rain down Elmwood Lane\n\n[Chorus]\nCarry me over the water\nLet the river know my name\n\n"
       "[Verse]\nEvery window holds a candle\nEvery doorway holds a frame\n\n[Chorus]\nCarry me over the water\nLet the river know my name")
ADD = """l=>{U.sDraft={step:1,title:'river song',artist:'',text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();
  return songById(U.songId).order.map(x=>({o:x.o,sid:x.sid}))}"""
SONG = "songById(U.songId)"


def secs(pg):
    return pg.evaluate(f"{SONG}.order.map(x=>({{o:x.o,sid:x.sid}}))")


def word(o, li, wi):
    return f'.sgsec[data-o="{o}"] .sgl[data-li="{li}"] .w[data-wi="{wi}"]'


def run(b, t):
    ok = t.ok

    # ===== the older marks move across, and saved marks are checked =====
    if 'data' in PARTS:
        d = sample()
        d['schema'] = 3
        d['songs'] = [{"id": "g_9", "name": "Old Marks", "artist": "", "pinned": False, "added": 1700000000000,
                       "sections": {"x1": {"label": "Verse", "cue": "Soft", "lines": [["one", "two", "three"], ["four", "five"]],
                                           "ann": {"0:0": {"up": 1, "br": 1}, "0:1": {"dn": 1, "run": 1}, "0:2": {"v": "ah", "nt": "Lift it", "check": 1, "was": "tree"},
                                                   "1:0": {"glow": "warm"}, "1:9": {"br": 1}, "bad": {"br": 1}},
                                           "orphans": [{"id": "r1", "was": "six", "ann": {"br": 1, "nt": "Gone"}}, {"id": "r2", "was": "x", "ann": "junk"}]}},
                       "order": [{"o": "o1", "sid": "x1"}]}]
        pg = t.page(b, data=d)
        sec = pg.evaluate("D.songs[0].sections.x1")
        M = sec['marks']
        has = lambda **k: any(all(m.get(a) == v for a, v in k.items()) for m in M)
        ok(pg.evaluate("D.schema") == 4, 'data from 3.26 upgrades to data version 4')
        ok(has(type='pitch', opt='Up', L='notes', line=0, w0=0) and has(type='breath', L='phrasing', line=0, w1=0, opt='')
           and has(type='pitch', opt='Down', line=0, w0=1) and has(type='ornament', opt='Run', line=0, w0=1), 'breath, run, higher and lower move into their layers')
        ok(has(type='vowel', opt='Sing as…', text='ah', L='words', w0=2) and has(type='note', L='note', text='Lift it', w0=2), 'sing as and notes move across with their text')
        ok(all(m.get('check') == 1 and m.get('was') == 'tree' for m in M if m['w0'] == 2 and m['line'] == 0), 'a mark flagged to check stays flagged, with the word it was on')
        ok(has(type='note', text='glow: warm', line=1, w0=0), 'anything else on an old mark is kept as a Note (nothing dropped)')
        ok(not any(m['line'] == 1 and m['w0'] == 9 for m in M) and len(M) == 7, f'a mark on a missing word is dropped ({len(M)} marks)')
        H = sec['held']
        ok(len(H) == 2 and all(h['was'] == 'six' for h in H) and {h['type'] for h in H} == {'breath', 'note'}, 'marks waiting to be moved move across too')
        ok(sec['ann']['0:0'] == {'br': 1, 'up': 1} and sec['ann']['0:2'].get('v') == 'ah' and sec['ann']['0:2'].get('check') == 1 and sec['orphans'][0]['was'] == 'six',
           f'the older copy is kept beside them, so a backup still opens in 3.26 ({sec["ann"]})')
        pg.reload(); ready(pg)
        ok(pg.evaluate("D.songs[0].sections.x1.marks.map(m=>m.id).join()") == ','.join(m['id'] for m in M), 'reopening changes nothing')

        # cleanSong drops only bad marks
        bad = pg.evaluate("""()=>{const L=[['a','b','c'],['d']],mk=(o)=>Object.assign({id:'q'+Math.random(),L:'phrasing',type:'breath',opt:'',line:0,w0:0,w1:0,text:''},o);
          const s=cleanSong({id:'z',name:'Z',sections:{x:{label:'Verse',lines:L,marks:[mk({}),mk({type:'zap'}),mk({L:'notes'}),mk({opt:'Huge'}),mk({line:5}),mk({w0:2,w1:1,type:'phrase'}),
            mk({w1:7}),mk({type:'intention',L:'delivery',line:-1,text:'first'}),mk({type:'intention',L:'delivery',line:-1,text:'second'}),mk({type:'say',L:'words'}),
            mk({type:'peak',w0:0,w1:2}),mk({type:'phrase',w0:0,w1:2}),mk({type:'note',L:'note',text:'x'.repeat(300)}),mk({w0:1,w1:1,extra:{k:1}})]}},order:[{o:'o',sid:'x'}]});
          return s.sections.x.marks.map(m=>[m.type,m.w0,m.w1,(m.text||'').length,!!m.extra])}""")
        types = [x[0] for x in bad]
        ok(types.count('breath') == 2 and 'zap' not in types and types.count('intention') == 1 and 'say' not in types,
           f'unknown types, wrong layers, bad options, lines or words out of range, a second Intention and missing text are dropped ({types})')
        ok(['peak', 0, 0, 0, False] in bad and ['phrase', 0, 2, 0, False] in bad, 'a one-word mark given a range sits on its word; a range keeps it')
        ok(any(x[0] == 'note' and x[3] == 200 for x in bad) and any(x[4] for x in bad), 'long notes are cut to 200 characters, and fields from a newer version are kept')

        # device prefs: the layer is remembered, never in a backup
        pg.evaluate("MARKS.setLayer('delivery')"); pg.reload(); ready(pg)
        ok(pg.evaluate("MARKS.layer()") == 'delivery', 'the chosen layer survives a reload')
        pg.evaluate("prepareExport(false,false)"); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
        bk = pg.evaluate("pendingExport.file.text()")
        ok('mkLayer' not in bk and '"marks"' in bk and '"held"' in bk, 'backups carry the marks, not the device settings')
        pg.context.close()

        # an old backup (3.26, data version 3) restores through the same move
        old = sample(); old['schema'] = 3
        old['songs'] = [{"id": "g_8", "name": "Backup Song", "artist": "", "pinned": False, "added": 1700000000000,
                         "sections": {"x1": {"label": "Chorus", "cue": "", "lines": [["la", "la", "la"]], "ann": {"0:1": {"br": 1, "v": "oh"}}, "orphans": []}},
                         "order": [{"o": "o1", "sid": "x1"}]}]
        pg = t.page(b)
        path = os.path.join(tempfile.mkdtemp(), 'old-backup.json')
        body = {"data": old, "draft": None, "takes": []}
        code = hashlib.sha256(json.dumps(body, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        with open(path, 'w') as f:
            json.dump({"app": "vocal-sessions", "format": 2, "appVersion": "3.26", "exportedAt": "2026-10-28T10:00:00Z", **body, "checkCode": code}, f)
        pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';render()"); pg.wait_for_timeout(200)
        with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
        fc.value.set_files(path); pg.wait_for_function("U.sheet==='bkReport'", timeout=8000)
        pg.click('[data-a=importYes]')
        pg.wait_for_function("D.songs.some(s=>s.id==='g_8')&&!U.sheet", timeout=15000)
        m = pg.evaluate("D.songs.find(s=>s.id==='g_8').sections.x1.marks.map(m=>m.type+':'+m.w1+':'+(m.text||''))")
        ok(sorted(m) == ['breath:1:', 'vowel:1:oh'] and pg.evaluate("D.schema") == 4, f'an old backup restores with its marks in their layers ({m})')
        pg.context.close()

    # ===== drawing: every mark as the spec's table says =====
    if 'draw' in PARTS:
        pg = t.page(b, 390, 844, touch=True, data=with_song_practice())
        pg.evaluate("U.tab='songs';render()"); o = pg.evaluate(ADD, LYR); pg.wait_for_timeout(200)
        v1, ch = o[0], o[1]
        put = """([sid,L,type,opt,line,w0,w1,text])=>{const s=songById(U.songId).sections[sid];MARKS.add(s,{li:line,w0,w1},type,opt,text);save();}"""
        S = [
            ('notes', 'pitch', 'Up', 0, 0, 0, ''), ('notes', 'slide', 'Scoop up', 0, 1, 1, ''), ('notes', 'hold', '', 0, 4, 4, ''),
            ('notes', 'ornament', 'Run', 1, 0, 0, ''), ('notes', 'rhythm', 'Pushed', 1, 2, 2, ''),
            ('phrasing', 'phrase', '', 0, 0, 3, ''), ('phrasing', 'chain', '', 0, 4, 4, ''), ('phrasing', 'peak', '', 0, 2, 2, ''),
            ('phrasing', 'breath', 'Sneak', 1, 4, 4, ''), ('phrasing', 'shape', 'Swell', 1, 0, 3, ''), ('phrasing', 'shape', 'End: release', 1, 0, 3, ''),
            ('words', 'vowel', 'Tall', 0, 0, 0, ''), ('words', 'carry', '', 0, 1, 1, ''), ('words', 'onset', 'Hard', 0, 2, 2, ''),
            ('words', 'stress', '', 1, 1, 2, ''), ('words', 'say', '', 1, 4, 4, 'el-mwood'), ('words', 'vowel', 'Sing as…', 0, 2, 2, 'ah'),
            ('delivery', 'register', 'Mix', 0, 0, 0, ''), ('delivery', 'colour', 'Belt', 0, 0, 0, ''), ('delivery', 'vibrato', 'Start vibrato', 0, 4, 4, ''),
            ('delivery', 'mic', 'Pull back', 1, 4, 4, ''), ('delivery', 'intention', '', -1, 0, 0, 'to someone far away'),
            ('note', 'note', 'Trouble spot', 1, 3, 3, 'Breath runs out'),
        ]
        for L, ty, opt, li, w0, w1, tx in S: pg.evaluate(put, [v1['sid'], L, ty, opt, max(li, 0), w0, w1, tx])
        pg.evaluate("rerender()"); pg.wait_for_timeout(200)
        W = f"(li,wi)=>document.querySelectorAll('.sgsec[data-o=\"{v1['o']}\"] .sgl[data-li=\"'+li+'\"] .w')[wi]"
        lab = lambda li, wi: pg.evaluate(f"(({W})({li},{wi}).querySelector('.v')||{{}}).textContent||''")
        cls = lambda li, wi, c: pg.evaluate(f"({W})({li},{wi}).classList.contains('{c}')")
        nxt = lambda li, wi, sel: pg.evaluate(f"(e=>!!e&&e.matches('{sel}'))(({W})({li},{wi}).nextElementSibling)")
        lay = lambda L: (pg.evaluate(f"MARKS.setLayer('{L}');rerender()"), pg.wait_for_timeout(150))
        lay('notes')
        ok(lab(0, 0) == '↑' and lab(0, 1) == '↗ scoop' and lab(1, 0) == '∿ run' and lab(1, 2) == '» push', 'Notes: pitch, slide, ornament and rhythm labels sit above their words')
        ok(cls(0, 4, 'mhold'), 'Notes: hold is a line running past its word')
        ok(pg.locator(f'.sgsec[data-o="{v1["o"]}"] .mph').count() == 0, 'Notes shows no Phrasing marks')
        lay('phrasing')
        ok(pg.locator(f'.sgsec[data-o="{v1["o"]}"] .sgl[data-li="0"] .mph').count() == 1 and
           pg.evaluate(f"document.querySelector('.sgsec[data-o=\"{v1['o']}\"] .sgl[data-li=\"0\"] .mph').querySelectorAll('.w').length") == 4,
           'Phrasing: a phrase is a bracket over its four words')
        ok(nxt(0, 4, '.mchain'), 'Phrasing: chain is a link after its word')
        ok(lab(0, 2) == '^', 'Phrasing: peak is a tick above its word')
        ok(nxt(1, 4, '.m.br.sn'), 'Phrasing: a sneak breath is the smaller breath after its word')
        ok(lab(1, 0) == 'swell' and lab(1, 3) == 'release', 'Phrasing: shape labels its first word (swell) and its ending its last (release)')
        ok(pg.locator(f'.sgsec[data-o="{v1["o"]}"] .w .v').count() == 3, 'Phrasing shows no other layer\'s labels')
        lay('words')
        ok(lab(0, 0) == 'tall' and lab(0, 2) == 'hard · ah' and lab(1, 4) == 'say: el-mwood', 'Words: vowel, onset and say labels; two on one word joined with " · "')
        ok(nxt(0, 1, '.mtie'), 'Words: carry is a tie after its word')
        st = pg.evaluate(f"(()=>{{const e=document.querySelector('.sgsec[data-o=\"{v1['o']}\"] .sgl[data-li=\"1\"] .mst');return e?e.querySelectorAll('.w').length:0}})()")
        ok(st == 2, 'Words: stress is a thick line under its words')
        lay('delivery')
        ok(lab(0, 0) == 'mix · belt' and lab(0, 4) == '≈ vib' and lab(1, 4) == 'mic back', 'Delivery: register, colour, vibrato and mic labels')
        ok('to someone far away' in pg.inner_text(f'.sgsec[data-o="{v1["o"]}"] .mint'), 'Delivery: Intention is a line under the section label')
        ok(pg.locator(f'.sgsec[data-o="{v1["o"]}"] .m.nt').count() == 1 and 'Breath runs out' in pg.inner_text(f'.sgsec[data-o="{v1["o"]}"] .sgnote'),
           'every layer: a Note is a bookmark after its word, its text under the line')
        lay('phrasing')
        ok(pg.locator(f'.sgsec[data-o="{v1["o"]}"] .m.nt').count() == 1, 'the Note shows on Phrasing too')
        # a label and a peak on one word, and a bracket round labelled words
        pg.evaluate(put, [v1['sid'], 'phrasing', 'shape', 'Arc', 0, 2, 3, '']); pg.evaluate("rerender()"); pg.wait_for_timeout(150)
        ok(lab(0, 2) == '^arc', f'a label and a peak on one word: the tick first, then the label ({lab(0, 2)})')
        ok(pg.locator(f'.sgsec[data-o="{v1["o"]}"] .sgl[data-li="0"] .mph .w.hv').count() >= 1, 'a phrase bracket goes round words with labels')
        # nothing overlaps: every label clear of every other label and of the words
        clash = pg.evaluate("""()=>{const R=e=>e.getBoundingClientRect(),out=[];for(const L of ['notes','phrasing','words','delivery']){MARKS.setLayer(L);rerender();
          const v=[...document.querySelectorAll('#app .sgl .w .v')],w=[...document.querySelectorAll('#app .sgl .w')].map(x=>x.querySelector('.wt')||x);
          const hit=(a,b)=>{a=R(a);b=R(b);return a.width>0&&b.width>0&&a.left<b.right-.5&&b.left<a.right-.5&&a.top<b.bottom-.5&&b.top<a.bottom-.5};
          v.forEach((a,i)=>v.slice(i+1).concat(w).forEach(b=>{if(hit(a,b))out.push(L+': '+a.textContent+' × '+b.textContent)}))}return out}""")
        ok(not clash, f'on every layer, no label overlaps a word or another label {clash[:3]}')
        t.shot(pg, 'draw-delivery', full_page=True)
        pg.context.close()

    # ===== selecting words and the marks sheet =====
    if 'sheet' in PARTS:
        pg = t.page(b, 390, 844, touch=True, data=with_song_practice())
        pg.evaluate("U.tab='songs';render()"); o = pg.evaluate(ADD, LYR); pg.wait_for_timeout(200)
        v1, ch, ch2 = o[0], o[1], o[3]
        pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(250)
        ok(pg.locator('.mkchips .mkchip').count() == 4 and pg.locator('.mkchip.on').inner_text().strip().endswith('Phrasing'), 'the Marks side has the layer chips, Phrasing first by default')
        ok(pg.locator('#mkcap').count() == 1 and 'Select words to mark' in pg.inner_text('#mkcap'), 'with nothing selected, a capsule says Select words to mark')
        sel = lambda: pg.evaluate("SG.sel&&[SG.sel.li,SG.sel.w0,SG.sel.w1]")
        pg.click(word(v1['o'], 0, 1)); pg.wait_for_timeout(150)
        ok(sel() == [0, 1, 1] and pg.locator('#mksheet').count() == 1 and pg.locator('#mkcap').count() == 0, 'tapping a word selects it and the sheet rises')
        pg.click(word(v1['o'], 0, 3)); pg.wait_for_timeout(150)
        ok(sel() == [0, 1, 3] and pg.locator(f'.sgsec[data-o="{v1["o"]}"] .w.on').count() == 3, 'another word on the line extends the selection to it')
        ok('“boats along the”' in pg.inner_text('#mksheet'), 'the sheet shows the selected words')
        pg.click(word(v1['o'], 0, 2)); pg.wait_for_timeout(150)
        ok(sel() == [0, 2, 2], 'a word inside the selection starts again from it')
        pg.click(word(v1['o'], 0, 2)); pg.wait_for_timeout(150)
        ok(sel() is None and pg.locator('#mksheet').count() == 0, 'the only selected word clears it')
        pg.click(word(v1['o'], 0, 0)); pg.click(word(v1['o'], 1, 2)); pg.wait_for_timeout(150)
        ok(sel() == [1, 2, 2], 'a word on another line starts a new selection')
        ok(pg.locator('#mksheet .mkb').count() == 6, 'the sheet always has six buttons: the layer\'s five and Note')
        # where one-word marks land in a range
        pg.click(word(v1['o'], 1, 0)); pg.click(word(v1['o'], 1, 3)); pg.wait_for_timeout(150)
        pg.click('#mksheet [data-a=mkPick][data-v=peak]'); pg.wait_for_timeout(150)
        pg.click('#mksheet [data-a=mkPick][data-v=chain]'); pg.wait_for_timeout(150)
        pg.click('#mksheet [data-a=mkPick][data-v=phrase]'); pg.wait_for_timeout(150)
        M = lambda sid: pg.evaluate(f"{SONG}.sections['{sid}'].marks")
        got = {m['type']: (m['w0'], m['w1']) for m in M(v1['sid'])}
        ok(got.get('peak') == (0, 0) and got.get('chain') == (3, 3) and got.get('phrase') == (0, 3), f'a peak lands on the first word, a chain on the last, a phrase keeps the range ({got})')
        ok(sel() == [1, 0, 3], 'the selection stays after adding')
        # every mark, through the sheet
        allw = []
        for L in ['notes', 'phrasing', 'words', 'delivery']:
            pg.click(f'[data-a=mkLayer][data-v={L}]'); pg.wait_for_timeout(120)
            for ty in pg.evaluate(f"MK_BY['{L}']"):
                d = pg.evaluate(f"MK_DEF['{ty}']")
                pg.click(word(ch['o'], 0, 1)) if sel() != [0, 1, 1] or pg.evaluate("SG.sel.o") != ch['o'] else None
                pg.wait_for_timeout(80)
                pg.click(f'#mksheet [data-a=mkPick][data-v={ty}]'); pg.wait_for_timeout(100)
                if d['opts']:
                    opt = d['opts'][-1]
                    pg.click(f'#mksheet [data-a=mkOpt][data-v="{opt}"]'); pg.wait_for_timeout(100)
                else:
                    opt = ''
                if pg.locator('#mkIn').count():
                    pg.fill('#mkIn', 'xx-' + ty); pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
                have = any(m['type'] == ty and m['opt'] == opt for m in M(ch['sid']))
                allw.append((ty, have))
        ok(all(h for _, h in allw), f'every mark can be added through the sheet {[x for x, h in allw if not h]}')
        # Note, on any layer, with optional text
        pg.click('#mksheet [data-a=mkPick][data-v=note]'); pg.click('#mksheet [data-a=mkOpt][data-v=Question]'); pg.wait_for_timeout(100)
        pg.click('[data-a=mkText]'); pg.wait_for_timeout(150)
        ok(any(m['type'] == 'note' and m['opt'] == 'Question' and m['text'] == '' for m in M(ch['sid'])), 'a Note needs no text')
        # empty text refused for Say
        pg.click('[data-a=mkLayer][data-v=words]'); pg.wait_for_timeout(120)
        n0 = len(M(ch['sid']))
        pg.click('#mksheet [data-a=mkPick][data-v=say]'); pg.wait_for_timeout(100); pg.click('[data-a=mkText]'); pg.wait_for_timeout(150)
        ok(len(M(ch['sid'])) == n0 and pg.locator('#mksheet .mkerr').count() == 1, 'Say with no text is refused, with a message in the sheet')
        # On these words: remove, then Undo from the toast; Undo after adding too
        chips = pg.locator('#mksheet .mkchipx').count()
        ok(chips >= 5, f'"On these words" lists the layer\'s marks and Notes on the selection ({chips})')
        pg.click('#mksheet [data-a=mkRm] >> nth=0'); pg.wait_for_timeout(150)
        ok(len(M(ch['sid'])) == n0 - 1 and 'Removed' in pg.inner_text('.toast'), 'removing from "On these words" says so')
        pg.click('.toast .ckub'); pg.wait_for_timeout(150)
        ok(len(M(ch['sid'])) == n0, 'Undo in the toast puts it back')
        pg.click('#mksheet [data-a=mkPick][data-v=carry]'); pg.wait_for_timeout(150)
        ok('Added Carry' in pg.inner_text('.toast'), 'adding says "Added Carry"')
        pg.click('.toast .ckub'); pg.wait_for_timeout(150)
        ok(len(M(ch['sid'])) == n0, 'and Undo takes it away again')
        # linked repeats: the same marks on every copy, the same words highlighted
        ok(pg.locator(f'.sgsec[data-o="{ch2["o"]}"] .w.echo').count() >= 1, 'selecting in Chorus 1 highlights the same words in the repeat')
        pg.click('[data-a=mkLayer][data-v=delivery]'); pg.wait_for_timeout(150)
        l1 = pg.evaluate(f"(document.querySelector('{word(ch['o'], 0, 1)} .v')||{{}}).textContent")
        l2 = pg.evaluate(f"(document.querySelector('{word(ch2['o'], 0, 1)} .v')||{{}}).textContent")
        ok(l1 == l2 and l1, f'a mark added in Chorus 1 shows in its repeat ({l1} | {l2}) {[(m["type"],m["line"],m["w0"]) for m in M(ch["sid"])]}')
        ok('to someone' not in pg.inner_text('main') and pg.locator(f'.sgsec[data-o="{ch2["o"]}"] .mint').count() == 1, 'the Intention shows on every repeat')
        # check this: a deleted line sends its marks to wait; a changed word in a range keeps the range, flagged
        pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        pg.click('[data-a=sgEditMode][data-v=lyrics]'); pg.wait_for_timeout(300)
        pg.evaluate(f"""()=>{{const e=document.querySelector('.lyred[data-k="{v1['sid']}"]');e.innerText='Paper boats along the gutter';}}""")
        pg.click('[data-a=sgEditMode][data-v=annotate]'); pg.wait_for_timeout(300)
        s1 = pg.evaluate(f"{SONG}.sections['{v1['sid']}']")
        ok(len(s1['held']) == 3 and all(h['was'] for h in s1['held']) and not any(m.get('line') == 1 for m in s1['marks']),
           f'deleting a marked line sends its marks to wait at the top ({len(s1["held"])})')
        ok(pg.locator(f'.sgsec[data-o="{v1["o"]}"] .sgwarn').count() == 3, 'each one is explained there, with Move and Remove')
        pg.click(f'.sgsec[data-o="{v1["o"]}"] [data-a=sgORemove] >> nth=0'); pg.wait_for_timeout(150)
        ok(len(pg.evaluate(f"{SONG}.sections['{v1['sid']}'].held")) == 2, 'Remove takes one away')
        pg.evaluate(f"(()=>{{const s={SONG}.sections['{ch['sid']}'];MARKS.add(s,{{li:1,w0:0,w1:3}},'stress','','');save();rerender()}})()")
        pg.click('[data-a=sgEditMode][data-v=lyrics]'); pg.wait_for_timeout(300)
        pg.evaluate(f"""()=>{{const e=document.querySelector('.lyred[data-k="{ch['sid']}"]');e.innerText='Carry me over the water\\nLet a river know my name';}}""")
        pg.click('[data-a=sgEditMode][data-v=annotate]'); pg.wait_for_timeout(300)
        stv = [m for m in M(ch['sid']) if m['type'] == 'stress' and m['line'] == 1]
        ok(len(stv) == 1 and (stv[0]['w0'], stv[0]['w1']) == (0, 3) and stv[0].get('check') == 1 and stv[0].get('was') == 'the',
           f'a changed word inside a range keeps the range, flagged to check ({stv})')
        pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)
        ok('to check' in pg.inner_text('.toast'), 'Done says how many marks to check')
        t.shot(pg, 'sheet')
        pg.context.close()

    # ===== the layer chips, Recall, Perform and Marks while playing =====
    if 'views' in PARTS:
        pg = t.page(b, 390, 844, touch=True, data=with_song_practice())
        pg.evaluate("U.tab='songs';render()"); o = pg.evaluate(ADD, LYR); pg.wait_for_timeout(200)
        v1 = o[0]
        pg.evaluate(f"""(()=>{{const s={SONG}.sections['{v1['sid']}'];[['phrasing','phrase','',0,0,3],['phrasing','breath','Full',0,4,4],['phrasing','chain','',0,4,4],
          ['words','vowel','Tall',0,1,1],['notes','pitch','Up',1,0,0],['note','note','',1,2,2]].forEach(m=>MARKS.add(s,{{li:m[3],w0:m[4],w1:m[5]}},m[1],m[2],m[1]==='note'?'Soft here':''));save();rerender()}})()""")
        ok(pg.locator('#app .mkchips').count() == 1 and pg.locator('.mkchip.on').inner_text().strip().endswith('Phrasing'), 'Practise has the layer chips')
        pg.evaluate("window.scrollTo(0,300)"); pg.wait_for_timeout(100)
        A = "(()=>{const l=[...document.querySelectorAll('#app .sgl')].find(l=>l.getBoundingClientRect().top>=90);return [l.dataset.o,l.dataset.li,l.getBoundingClientRect().top]})()"
        a0 = pg.evaluate(A)
        pg.evaluate("document.querySelector('[data-a=mkLayer][data-v=words]').click()"); pg.wait_for_timeout(200)
        y1 = pg.evaluate(f"document.querySelector('.sgl[data-o=\"{a0[0]}\"][data-li=\"{a0[1]}\"]').getBoundingClientRect().top")
        ok(abs(y1 - a0[2]) < 2, f'switching layer keeps the line you were looking at in place ({a0[2]} → {y1})')
        ok(pg.evaluate(f"(document.querySelectorAll('.sgsec[data-o=\"{v1['o']}\"] .sgl[data-li=\"0\"] .w')[1].querySelector('.v')||{{}}).textContent") == 'tall' and pg.locator('#app .mph').count() == 0, 'a layer chip shows that layer only')
        pg.reload(); ready(pg)
        ok(pg.evaluate("MARKS.layer()") == 'words', 'the chosen layer is remembered')
        pg.evaluate(f"openSong('{pg.evaluate('D.songs.find(s=>s.name===\"River Song\").id')}')"); pg.wait_for_timeout(300)
        pg.evaluate("MARKS.setLayer('phrasing');rerender()")
        # Recall: brackets, chains, breaths and Notes only, and nothing moves between levels
        pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(300)
        pos = lambda: pg.evaluate("[...document.querySelectorAll('#app .mph,#app .m.br,#app .mchain,#app .m.nt')].map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.width)]})")
        p0 = pos()
        ok(len(p0) == 4 and pg.locator('#app .w .v').count() == 0 and pg.locator('#app .mkchips').count() == 0,
           f'Recall shows only the bracket, the chain, the breath and the Note ({len(p0)}), no labels and no chips')
        same = True
        for lv in range(1, 5):
            pg.click('.hcap [data-v="1"]'); pg.wait_for_timeout(150)
            same = same and pos() == p0
        ok(same, 'the marks over the pills never move between hint levels')
        t.shot(pg, 'recall')
        # Perform follows Marks while playing
        pg.click('[data-a=sgMode][data-v=perform]'); pg.wait_for_timeout(300)
        ok(pg.locator('#app .m.br').count() == 1 and pg.locator('#app .mph, #app .m.nt').count() == 0 and 'Breaths' in pg.inner_text('.sgbanner'),
           'Perform with Breaths only: just the breaths')
        pg.evaluate("ckPref('marksPlaying','active');rerender()"); pg.wait_for_timeout(200)
        ok(pg.locator('#app .mph').count() == 1 and pg.locator('#app .m.nt').count() == 0, 'Perform with Active layer: the chosen layer, never Notes')
        pg.evaluate("ckPref('marksPlaying','off');rerender()"); pg.wait_for_timeout(200)
        ok(pg.locator('#app .m.br, #app .mph').count() == 0, 'Perform with Off: no marks')
        pg.click('[data-a=sgMode][data-v=practise]'); pg.wait_for_timeout(200)
        # play-along: Active layer on the line being sung and the next one only; breaths everywhere
        pg.evaluate("ckPref('marksPlaying','active');CLOCK.fake(10000)")
        pg.evaluate(f"(()=>{{const s={SONG},L=ckLines(s);ckStore(s,L,ckSpread(s,L,[0,10,20,30]),[true,true,true,true],L.map(()=>false),{{est:true}});rerender()}})()")
        pg.click('.ckrow [data-a=ckTile][data-v=timing]'); pg.wait_for_timeout(300)
        pg.click('#ckpa .ckl[data-i="0"]'); pg.wait_for_timeout(200)
        vis = lambda i: pg.evaluate(f"(()=>{{const l=document.querySelector('#ckpa .ckl[data-i=\"{i}\"]'),b=l.querySelector('.mph');return b?getComputedStyle(b).backgroundImage!=='none':null}})()")
        ok(vis(0) is True, 'Active layer: the phrase bracket shows on the line being sung')
        pg.evaluate("CLOCK.advance(16)"); pg.wait_for_timeout(150)
        cur = int(pg.evaluate("document.querySelector('#ckpa .ckl.now').dataset.i"))
        ok(cur >= 2 and vis(0) is False, f'and goes when the song moves on (line {cur})')
        ok(pg.locator('#ckpa .ckl[data-i="0"] .ckbr').count() == 1 and pg.locator('#ckpa .m.nt').count() == 0, 'breaths show on every line; Notes never show while playing')
        h0 = pg.evaluate("document.querySelector('#ckpa .ckl[data-i=\"0\"]').offsetHeight")
        pg.evaluate("CLOCK.advance(-16)"); pg.wait_for_timeout(150)
        h1 = pg.evaluate("document.querySelector('#ckpa .ckl[data-i=\"0\"]').offsetHeight")
        ok(abs(h0 - h1) < 0.5, 'lines keep their height as the marks come and go (stillness while singing)')
        pg.context.close()

    # ===== marking while listening =====
    if 'listen' in PARTS:
        pg = t.page(b, 390, 844, touch=True, data=with_song_practice())
        pg.evaluate("U.tab='songs';render()"); o = pg.evaluate(ADD, LYR); pg.wait_for_timeout(200)
        pg.evaluate("CLOCK.fake(10000)")
        pg.evaluate(f"(()=>{{const s={SONG},L=ckLines(s);ckStore(s,L,ckSpread(s,L,[0,10,20,30]),[true,true,true,true],L.map(()=>false),{{est:true}});rerender()}})()")
        pg.click('.ckrow [data-a=ckTile][data-v=timing]'); pg.wait_for_timeout(300)
        pg.click('#ckpa .ckl[data-i="0"]'); pg.wait_for_timeout(200)
        ok(pg.evaluate("CLOCK.state().run"), 'play-along is running')
        pg.click('#barR [data-a=ckPencil]'); pg.wait_for_timeout(300)
        ok(pg.evaluate("U.sEdit") == 'annotate' and pg.evaluate("CLOCK.state().run"), 'the pencil goes straight to Marks and the clock keeps going')
        ok(pg.locator('#barL .mktp #mkT').count() == 1 and pg.locator('#ckpa:not([hidden])').count() == 0 and pg.locator('#fw:not([hidden]) .fwk').count() == 0,
           'the clock is a pill in the top bar; the big view and the floating window stay away')
        t0 = pg.inner_text('#mkT')
        pg.evaluate("CLOCK.advance(12)"); pg.wait_for_timeout(150)
        ok(pg.inner_text('#mkT') != t0, 'the pill keeps time')
        y = pg.evaluate("scrollY")
        cur = pg.evaluate("(()=>{const l=document.querySelector('.sgl.mknow');return l&&[l.dataset.o,l.dataset.li]})()")
        ok(cur == [o[1]['o'], '0'], f'the line being sung is softly lit ({cur})')
        pg.click(word(o[0]['o'], 0, 2)); pg.wait_for_timeout(150)
        pg.click('#mksheet [data-a=mkPick][data-v=peak]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("CLOCK.state().run") and pg.locator('.sgl.mknow').count() == 1, 'marking doesn\'t stop the clock or lose the highlight')
        pg.evaluate("CLOCK.advance(10)"); pg.wait_for_timeout(150)
        ok(abs(pg.evaluate("scrollY") - y) < 1 and pg.evaluate("document.querySelector('.sgl.mknow').dataset.o") == o[2]['o'], 'the highlight moves on; the page never scrolls by itself')
        pg.click('#barL .mktp'); pg.wait_for_timeout(200)
        ok(not pg.evaluate("CLOCK.state().run") and pg.evaluate("U.sEdit") == 'annotate', 'tapping the pill pauses, still marking')
        pg.click('#barL .mktp'); pg.wait_for_timeout(200)
        ok(pg.evaluate("CLOCK.state().run"), 'and again carries on')
        t.shot(pg, 'listen')
        pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)
        ok(pg.locator('#ckpa:not([hidden])').count() == 1 and pg.evaluate("CLOCK.state().run"), 'Done goes back to playing along')
        pg.context.close()

    # ===== every size, light and dark =====
    if 'sizes' in PARTS:
        for w, h, sc in [(375, 667, 'light'), (375, 667, 'dark'), (390, 844, 'dark'), (852, 393, 'light'), (820, 1180, 'light'), (1440, 900, 'dark')]:
            pg = t.page(b, w, h, sc=sc, touch=w < 1000, data=with_song_practice(), **({'ua': None} if w > 1000 else {}))
            pg.evaluate("U.tab='songs';render()"); o = pg.evaluate(ADD, LYR); pg.wait_for_timeout(200)
            # many labels on one narrow line
            pg.evaluate(f"""(()=>{{const s={SONG}.sections['{o[0]['sid']}'];for(let i=0;i<5;i++){{MARKS.add(s,{{li:0,w0:i,w1:i}},'colour','Breathy','');MARKS.add(s,{{li:0,w0:i,w1:i}},'register','Falsetto','');MARKS.add(s,{{li:0,w0:i,w1:i}},'mic','Come close','')}}
              MARKS.setLayer('delivery');save();rerender()}})()""")
            pg.wait_for_timeout(200)
            if w >= 700:
                sid = pg.evaluate("U.songId")
                pg.evaluate(f"U.tab='songs';U.view=null;render();openSong('{sid}')"); pg.wait_for_timeout(300)
            pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(200)
            pg.click(f'.sgsec[data-o="{o[0]["o"]}"] .w >> nth=2'); pg.wait_for_timeout(200)
            pg.click('#mksheet [data-a=mkPick][data-v=colour]'); pg.wait_for_timeout(150)
            r = pg.evaluate("""(()=>{const s=document.getElementById('mksheet').getBoundingClientRect();return {side:document.documentElement.scrollWidth>innerWidth+1,
              inside:s.left>=0&&s.right<=innerWidth+0.5&&s.bottom<=innerHeight+0.5&&s.top>=0}})()""")
            ok(not r['side'] and r['inside'], f'{w}x{h} {sc}: no sideways scroll with many labels, and the sheet fits on screen ({r})')
            t.shot(pg, f'size-{w}x{h}-{sc}')
            pg.context.close()
