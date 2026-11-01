"""Q15 · Marks: Register-Ready Data. A backup made by the *next* version (tests/fixtures/backup-next.json, made up: no
real lyrics) carries marks this version doesn't know (a new type, option or layer) and extra fields (`ext` and others)
on marks, held marks, timing, slots, timed lines, markers and the loop. It must restore here with nothing lost, go back
out unchanged, keep the unknown marks inactive (invisible, uncounted, never replaced) and keep every extra field
through editing: re-adding and moving marks, lyric edits, re-timing a line, clearing the length and setting a loop."""
import json, os
from harness import fix, ready, until, OUT, url, APP_PATH

F = os.path.join(OUT, 'extras-files'); os.makedirs(F, exist_ok=True)
NEXT = fix('backup-next.json')
SONG = "songById('g_n1')"
SEC = SONG + ".sections.x1"


def same(a, b): return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def pick(pg, path):
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(path)
    return until(pg, "U.sheet==='bkReport'")


def export(pg):
    pg.evaluate("prepareExport(false,false)")
    until(pg, "U.sheet==='exportReady'")
    txt = pg.evaluate("pendingExport.file.text()")
    pg.evaluate("U.sheet=null;rerender()")
    return json.loads(txt)


def by_id(lst): return {m['id']: m for m in lst}


def run(b, t):
    ok = t.ok
    src = json.load(open(NEXT, encoding='utf-8'))
    want = src['data']['songs'][0]
    x1 = want['sections']['x1']
    idle_ids = ['k2', 'k3', 'k4', 'k5', 'k8']

    # ---- restoring the next version's backup
    pg = t.page(b, data=None)
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';render()")
    ok(pick(pg, NEXT), 'the next version’s backup opens in Import')
    ok(pg.evaluate("pendingImport.status") == 'good' and pg.evaluate("pendingImport.songsBad||0") == 0,
       f'it checks as complete, with no song left out ({pg.evaluate("pendingImport.status")})')
    pg.click('[data-a=importYes]'); until(pg, "U.sheet===null&&D.songs.length===1")
    got = pg.evaluate(SONG)
    ok(same(got, want), 'the song restores exactly: unknown marks, held marks, `ext` and other extra fields at every level')
    if not same(got, want):
        for k in want:
            if not same(got.get(k), want[k]): print('    differs:', k, json.dumps(got.get(k))[:300])
    ok(same(pg.evaluate("D.ext"), src['data']['ext']), 'a field the next version adds to the data itself is kept')
    ok(pg.evaluate("D.schema") == 4, 'the data version stays 4 (no field changes its meaning)')

    # ---- and goes back out unchanged
    out = export(pg)
    ok(same(out['data']['songs'], src['data']['songs']), 'a backup made now carries the song back out unchanged')
    diff = [k for k in src['data'] if k != 'lastBackup' and not same(out['data'].get(k), src['data'][k])]
    ok(not diff, f'and everything else in the data too ({diff})')
    pg.reload(); ready(pg)
    ok(same(pg.evaluate(SONG), want), 'reopening the app changes nothing')

    # ---- inactive marks: kept, but nothing shows, counts or lists them
    live = pg.evaluate(f"MARKS.live({SEC}.marks).map(m=>m.id)")
    ok(live == ['k1', 'k6', 'k7', 'k9', 'k10'], f'a new type, option or layer, or a layer that doesn’t match, is inactive ({live})')
    ok(pg.evaluate(f"MARKS.live({SEC}.held).map(m=>m.id)") == ['h1'], 'so are held marks from the next version')
    ok(pg.evaluate(f"MARKS.checks({SEC})") == 1, 'the pencil’s count leaves them out (only the one held mark it knows)')
    ok(pg.evaluate(f"MARKS.onSel({SEC},{{li:0,w0:0,w1:3}},'delivery').map(m=>m.id).sort()") == ['k1', 'k7', 'k9'],
       '“On these words” lists only the marks it knows')
    ok(pg.evaluate(f"MARKS.marked({SEC},0)") == [True, False, False, True] and pg.evaluate(f"MARKS.breaths({SEC},1)") == [False, False, True],
       'the lyrics editor’s highlights and Song Clock’s breaths ignore them')
    ok(pg.evaluate(f"MARKS.intention({SEC}).id") == 'k7', 'the section’s Intention is the one it knows')
    act = pg.evaluate(f"MARKS.line({SEC},0,MARKS.show('active','delivery'),(wi,w,d)=>w+'['+d.lab.join('|')+']').html")
    brs = pg.evaluate(f"MARKS.line({SEC},1,MARKS.show('breaths'),(wi,w)=>w).html")
    ok('chest' in act and 'fry' not in act and brs.count('m br') == 1, 'play-along’s Active layer and Breaths draw only known marks')
    ok(same(pg.evaluate(f"{SEC}.ann"), x1['ann']) and same(pg.evaluate(f"{SEC}.orphans"), x1['orphans']),
       'the copy kept for 3.26 leaves them out')

    pg.evaluate(f"MARKS.setLayer('delivery');go(()=>{{U.tab='songs';U.view='lyr';U.songId='g_n1'}})")
    until(pg, "!!document.querySelector('.sgsec[data-o=\"o1\"] .sgl')")
    txt = pg.inner_text('#app').lower()
    ok('chest' in txt and 'tell a story' in txt, 'the song page shows the marks it knows (Delivery)')
    ok(not any(w in txt for w in ['fry', 'loose jaw', 'shoulders', 'build slowly']), 'and none of the inactive ones')
    pg.evaluate("MARKS.setLayer('phrasing');rerender()")
    until(pg, "!!document.querySelector('.sgsec[data-o=\"o1\"] .sgl[data-li=\"1\"]')")
    ok(pg.locator('.sgsec[data-o="o1"] .sgl[data-li="1"] .m.br').count() == 1, 'one breath on the line: the inactive one isn’t drawn')
    t.shot(pg, 'song-phrasing')
    pg.evaluate("SG_ACT.sgEdit()"); until(pg, "U.sEdit==='annotate'")
    txt = pg.inner_text('#app')
    ok('“fa”' in txt and '“so”' not in txt and '“ti”' not in txt, 'the Marks side lists only the held mark it knows')
    pg.evaluate("U.sheet='sgKey';U.sd={};rerender()"); until(pg, "U.sheet==='sgKey'&&!!document.querySelector('.sheet')")
    key = pg.inner_text('.sheet')
    ok('Chest' in key and 'watch pitch' in key and not any(w in key for w in ['fry', 'Jaw', 'neck', 'Build slowly', 'shoulders']),
       'Key for this song counts only the marks it knows')
    t.shot(pg, 'key')
    pg.evaluate("U.sheet=null;rerender()")

    # ---- editing keeps extra fields, and never touches inactive marks
    r = pg.evaluate(f"""(()=>{{const s={SEC},r=MARKS.add(s,{{li:0,w0:0,w1:0}},'register','Chest','');save();
      return {{m:r.m,gone:r.gone.map(x=>x.id)}}}})()""")
    ok(r['gone'] == ['k1'] and same(r['m'].get('ext'), x1['marks'][0]['ext']), f're-adding a mark keeps the fields of the one it replaces ({r["m"]})')
    r = pg.evaluate(f"""(()=>{{const s={SEC},r=MARKS.add(s,{{li:0,w0:1,w1:1}},'register','Mix','');save();
      return {{gone:r.gone.map(x=>x.id),k2:s.marks.some(m=>m.id==='k2')}}}})()""")
    ok(r['gone'] == [] and r['k2'], 'adding a mark of the same type on its word never replaces an inactive one')
    pg.evaluate("U.songId='g_n1';SG.pend={sid:'x1',id:'h1'};selectWord({o:'o1',sid:'x1',li:0,wi:2})")
    m = pg.evaluate(f"{SEC}.marks.find(m=>m.id==='h1')")
    ok(m and m['line'] == 0 and m['w0'] == 2 and same(m.get('ext'), {'note': 'x'}) and m['opt'] == 'Full',
       f'moving a held mark keeps its fields ({m})')
    pg.evaluate("SG.pend={sid:'x1',id:'h2'};selectWord({o:'o1',sid:'x1',li:0,wi:3})")
    ok(pg.evaluate(f"{SEC}.held.map(m=>m.id)") == ['h2', 'h3'] and not pg.evaluate(f"{SEC}.marks.some(m=>m.id==='h2')"),
       'an inactive held mark can’t be moved, and stays where it is')
    after = by_id(pg.evaluate(f"{SEC}.marks"))
    orig = by_id(x1['marks'])
    ok(all(same(after.get(i), orig[i]) for i in idle_ids), 'the inactive marks are exactly as they were after all that')
    ok(same(after['k6'], orig['k6']) and same(after['k9'], orig['k9']), 'and so are the marks that weren’t edited, extra fields and all')

    # lyric edits: every mark follows its words, inactive ones too, and only known ones are counted
    rl = pg.evaluate(f"""(()=>{{const c=JSON.parse(JSON.stringify({SEC})),f=relink(c,[['ha','la','la','la','la']]);
      return {{f,m:c.marks.map(m=>[m.id,m.line,m.w0,m.w1]),h:c.held.map(m=>m.id),checks:MARKS.checks(c)}}}})()""")
    pos = {x[0]: x[1:] for x in rl['m']}
    ok(pos.get('k2') == [0, 2, 2] and pos.get('k3') == [0, 3, 4], f'an inactive mark follows its words ({rl["m"]})')
    # (h1 was moved above, so the known marks waiting are the two from the removed line)
    ok({'k4', 'k5'} <= set(rl['h']) and rl['f'] == 2 and rl['checks'] == 2,
       f'one whose word goes waits in held, kept; only the known marks are counted to check ({rl})')

    # timing: re-timing a line, clearing the length, a timing with only extra fields
    pg.evaluate(f"ckSetLines({SONG},{{0:[11,14]}},true)")
    tm = pg.evaluate(f"{SONG}.timing")
    s1, s2 = tm['slots']['o1'], tm['slots']['o2']
    ok(same(tm.get('ext'), {'tempo': 96}) and tm.get('grid') == 'a field outside ext', f'a re-timed line keeps the timing’s own extra fields ({list(tm)})')
    ok(same(s1.get('ext'), {'transition': 'chest to mix'}) and s1.get('flag') == 'kept', 'and each slot’s')
    ok(s1['lines'][0] == [11, 14, {'anchor': 'onset'}] and s1['lines'][1] == [15, 19.5] and s2['lines'][1] == [None, None, {'somatic': 'relax'}],
       f'and each line’s, timed or not ({s1["lines"]}, {s2["lines"]})')
    pg.evaluate(f"ckUndo()")
    ok(same(pg.evaluate(f"{SONG}.timing"), want['timing']), 'Undo puts the timing back exactly')
    pg.evaluate(f"ckSetLen({SONG},0)")
    ok(pg.evaluate(f"{SONG}.timing.len") is None and same(pg.evaluate(f"{SONG}.timing.ext"), {'tempo': 96}), 'clearing the length keeps them')
    lone = pg.evaluate("""[cleanTiming({len:null,slots:{},ext:{a:1}},null),cleanTiming({len:null,slots:{}},null),
      (()=>{const s={id:'z',name:'Z',timing:{len:90,slots:{},ext:{a:1}}};ckSetLen(s,0);return s.timing||null})()]""")
    ok(lone[0] is not None and same(lone[0]['ext'], {'a': 1}) and lone[1] is None and lone[2] is not None,
       f'timing with nothing but extra fields is kept; empty timing still goes ({lone})')

    # markers and the loop keep theirs when checked again
    mk = pg.evaluate(f"[cleanMarkers({SONG}.markers),cleanLoop({SONG}.loop,200)]")
    ok(same(mk[0], want['markers']) and same(mk[1], want['loop']), 'markers and the loop keep their extra fields when checked')

    # ---- the duplicate check still works with extra fields
    d = pg.evaluate("""(()=>{const L=[['a','b']],k=(o)=>Object.assign({id:'d'+Math.random(),L:'phrasing',type:'breath',opt:'',line:0,w0:1,w1:1,text:''},o),
      n=(l)=>mkCleanList(l,L).length;
      return [n([k({}),k({})]),n([k({ext:{a:1}}),k({ext:{a:2}})]),n([k({ext:{a:1,b:2}}),k({ext:{b:2,a:1}})]),
        n([k({type:'zz'}),k({type:'zz'})]),n([k({type:'zz',line:4})]),n([k({type:5})]),n([k({opt:'New',ext:{a:1}}),k({opt:'New',ext:{a:2}})])]})()""")
    ok(d == [1, 2, 1, 1, 0, 0, 2], f'exact duplicates go; marks that differ only in `ext` are both kept; inactive ones are checked the same way ({d})')

    # ---- the edited song still saves and goes out with every extra field
    pg.reload(); ready(pg)
    out = export(pg)
    sg = out['data']['songs'][0]
    ok(all(same(by_id(sg['sections']['x1']['marks']).get(i), orig[i]) for i in idle_ids) and [h['id'] for h in sg['sections']['x1']['held']] == ['h2', 'h3'],
       'after editing and reopening, a new backup still carries every inactive mark unchanged')
    ok(same(sg['timing']['slots']['o1']['ext'], {'transition': 'chest to mix'}) and same(sg['ext'], want['ext']) and same(sg['sections']['x1']['ext'], x1['ext']),
       'and the timing’s, song’s and section’s extra fields')
    pg.context.close()
