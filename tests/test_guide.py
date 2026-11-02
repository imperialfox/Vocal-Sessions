"""Q04 · Marks: Practice Guide: the guide's words (every mark has them), the guide's pages (home, a page per mark, How to
mark a song), Key for this song (only the song's marks, options and counts, Notes, the empty state), the peek card
(hold vs tap, dismissals, one at a time), every door into them and Back to where you were, the native push, every
size in light and dark, and Reduce Motion.
VS_GUIDE=text,pages,key,peek,doors,push,sizes runs only those parts."""
import os
from harness import sample
from test_marks import LYR, ADD, SONG, secs, word

PARTS = set((os.environ.get('VS_GUIDE') or 'text,pages,key,peek,doors,push,sizes').split(','))
TYPES = "Object.keys(MK_DEF)"
FITS = "document.documentElement.scrollWidth<=innerWidth"
INSIDE = "sel=>{const e=document.querySelector(sel);if(!e)return false;const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+0.5&&r.top>=0&&r.bottom<=innerHeight+0.5}"
HERE = "[U.tab,U.view,U.gPg||null]"
OPEN_WORD = """(()=>{const w=[...document.querySelectorAll('#app .sgl .w')].find(w=>{const r=w.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
  return y>0&&y<innerHeight&&document.elementFromPoint(x,y)&&document.elementFromPoint(x,y).closest('.w')===w&&!w.classList.contains('on')});
  const r=w.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})()"""


def song(pg, marks=True):
    """The river song on its Marks side, with a few marks (the chorus is linked, so its marks are shared)."""
    S = pg.evaluate(ADD, LYR)
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view=split()?null:'lyr';U.songId=id})", pg.evaluate(f"{SONG}.id")); pg.wait_for_timeout(250)
    if marks:
        pg.evaluate("""S=>{const s=songById(U.songId),v=s.sections[S[0].sid],c=s.sections[S[1].sid];
          MARKS.add(v,{li:0,w0:0,w1:3},'phrase','','');MARKS.add(v,{li:0,w0:3,w1:3},'breath','Quick','');MARKS.add(v,{li:1,w0:4,w1:4},'breath','Full','');
          MARKS.add(c,{li:0,w0:0,w1:0},'pitch','Up','');MARKS.add(c,{li:1,w0:1,w1:1},'pitch','Down','');MARKS.add(c,{li:0,w0:2,w1:2},'breath','Quick','');
          MARKS.add(c,{li:1,w0:3,w1:3},'note','Trouble spot','Lift it');MARKS.add(c,{li:0,w0:1,w1:1},'note','','');save();rerender()}""", S)
    return S


def mark_side(pg, S, li=0, wi=1, k=0):
    pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(200)
    pg.click(word(S[k]['o'], li, wi)); pg.wait_for_timeout(200)


def hold(pg, sel, ms):
    bx = pg.locator(sel).first.bounding_box()
    pg.mouse.move(bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)
    pg.mouse.down(); pg.wait_for_timeout(ms); pg.mouse.up(); pg.wait_for_timeout(150)


def nmarks(pg):
    return pg.evaluate(f"Object.values({SONG}.sections).reduce((a,c)=>a+c.marks.length,0)")


def run(b, t):
    ok = t.ok

    # ===== the words: every mark has its text, and its example is a real mark =====
    if 'text' in PARTS:
        pg = t.page(b)
        miss = pg.evaluate(f"""{TYPES}.filter(k=>{{const g=GUIDE.marks[k];return !g||!['peek','what','how','when'].every(f=>typeof g[f]==='string'&&g[f].length>8)
          ||!g.ex||!g.ex.w||!g.vs||typeof g.vs.t!=='string'}})""")
        ok(not miss, f'every mark in MK_DEF has its guide text: peek line, What it is, How to sing it, When to mark it, an example and Don’t confuse with ({miss})')
        ok(pg.evaluate(f"Object.keys(GUIDE.marks).every(k=>MK_DEF[k])&&Object.keys(GUIDE.marks).length===({TYPES}).length"), 'and no text for a mark that doesn’t exist (21 marks plus Note)')
        bad = pg.evaluate(f"""{TYPES}.filter(k=>{{const s=MKG.exSec(k);return mkCleanList(s.marks,s.lines).length!==s.marks.length}})""")
        ok(not bad, f'every example is made of valid marks, so it draws exactly as on a song ({bad})')
        ok(pg.evaluate(f"{TYPES}.every(k=>!GUIDE.marks[k].vs.to||(MK_DEF[GUIDE.marks[k].vs.to]&&GUIDE.marks[k].vs.to!==k))"), 'every Don’t confuse with points at another mark')
        ok(pg.evaluate("GUIDE.marks.slide.tech==='portamento'"), 'Slide carries its technical name, portamento')
        ok(pg.evaluate("GUIDE.how.passes.length===4&&GUIDE.how.habits.length===5&&GUIDE.how.habits.some(h=>h[0]==='Let timing help.'&&/suggested breath/.test(h[1]))"),
           'the walkthrough has four passes and five habits, with Let timing help reworded for suggested breaths')
        pg.context.close()

    # ===== the pages =====
    if 'pages' in PARTS:
        pg = t.page(b, w=375, h=812)
        pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(150)
        pg.click('#app [data-zk="mk:guide"]'); pg.wait_for_timeout(250)
        ok(pg.evaluate(HERE) == ['settings', 'guide', 'home'] and pg.locator('#app h1').inner_text() == 'Marks guide', 'the guide home is titled Marks guide')
        ok('four layers' in pg.inner_text('#app .gdlead'), 'with its lead')
        hdrs = pg.evaluate("[...document.querySelectorAll('#app .hdr')].map(h=>h.textContent)")
        ok(hdrs == ['1 · Notes', '2 · Phrasing', '3 · Words', '4 · Delivery', 'Every layer'], f'a group per layer, then Every layer ({hdrs})')
        rows = pg.evaluate("[...document.querySelectorAll('#app [data-a=gdOpen]')].map(r=>r.dataset.v)")
        ok(rows == ['how'] + pg.evaluate("MK_BY.notes.concat(MK_BY.phrasing,MK_BY.words,MK_BY.delivery,['note'])"), 'How to mark a song, then every mark in layer order, then Note')
        ok(pg.evaluate("[...document.querySelectorAll('#app [data-a=gdOpen][data-v]')].filter(r=>MK_DEF[r.dataset.v]).every(r=>r.querySelector('.gdg').innerHTML===(d=>(d.innerHTML=mkGlyph(r.dataset.v),d.innerHTML))(document.createElement('span'))&&r.querySelector('small').textContent===(r.dataset.v==='note'?GUIDE.noteSub:GUIDE.marks[r.dataset.v].peek))"),
           'each mark’s row shows its glyph, name and peek line')
        ok('Linked' in pg.inner_text('#app') and 'pencil' in pg.inner_text('#app .foot'), 'the old key’s Linked row and its footnote are kept')
        t.shot(pg, 'home', full_page=True)
        # every mark's page from the home, and Back to the home
        bad = []
        for ty in pg.evaluate(TYPES):
            pg.click(f'#app [data-a=gdOpen][data-v="{ty}"]'); pg.wait_for_timeout(120)
            g = pg.evaluate("t=>({h:document.querySelector('#app h1').textContent,big:!!document.querySelector('#app .tile.big.gdbig'),"
                            "secs:[...document.querySelectorAll('#app .hdr.exh')].map(h=>h.textContent),chips:[...document.querySelectorAll('#app .gdchip')].map(c=>c.textContent),"
                            "badge:document.querySelector('#app .ex-h .badge').textContent,ex:document.querySelectorAll('#app .gdex .w').length,"
                            "opts:MK_DEF[t].opts,n:MK_DEF[t].n,here:[U.view,U.gPg]})", ty)
            if g['here'] != ['guide', ty]: bad.append(ty + ' opens ' + str(g['here']))
            if g['h'] != g['n'] or not g['big']: bad.append(ty + ' title or tile')
            if g['secs'] != ['What it is', 'How to sing it', 'When to mark it', 'Example', 'Don’t confuse with']: bad.append(ty + ' sections ' + str(g['secs']))
            if g['opts'] and g['chips'] != g['opts']: bad.append(ty + ' chips ' + str(g['chips']))
            if not g['opts'] and len(g['chips']) != 1: bad.append(ty + ' one-tap chip')
            if not g['ex']: bad.append(ty + ' has no drawn example')
            if not pg.evaluate(FITS): bad.append(ty + ' scrolls sideways')
            pg.click('#barL [data-a=gdBack]'); pg.wait_for_timeout(120)
            if pg.evaluate(HERE) != ['settings', 'guide', 'home']: bad.append(ty + ' Back went to ' + str(pg.evaluate(HERE)))
        ok(not bad, 'all 21 marks and Note have a page: big tile, title, layer badge, option chips, the five sections and a drawn example; Back returns to the home' + (' — ' + '; '.join(bad) if bad else ''))
        # what the examples draw
        pg.click('#app [data-a=gdOpen][data-v=slide]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("[...document.querySelectorAll('#app .ex-h .badge')].map(b=>b.textContent).join('|')") == '1 · Notes|portamento',
           'Slide’s page shows its layer badge and portamento')
        ok('↗ scoop' in pg.inner_text('#app .gdex .v'), 'its example draws the scoop label with the real renderer')
        # Don't confuse with: to the other mark's page, and Back to this one
        pg.click('#app [data-a=gdOpen][data-v=ornament]'); pg.wait_for_timeout(150)
        ok(pg.evaluate(HERE) == ['settings', 'guide', 'ornament'], 'Don’t confuse with opens the other mark’s page')
        pg.click('#barL [data-a=gdBack]'); pg.wait_for_timeout(150)
        ok(pg.evaluate(HERE) == ['settings', 'guide', 'slide'], 'and Back returns to the mark you came from')
        for ty, sel in (('phrase', '.gdex .mph'), ('stress', '.gdex .mst'), ('hold', '.gdex .mhold'), ('breath', '.gdex .m.br'), ('chain', '.gdex .mchain'),
                        ('carry', '.gdex .mtie'), ('note', '.gdex .m.nt'), ('intention', '.gdex .mint'), ('peak', '.gdex .mpk')):
            pg.evaluate(f"MKG.open('{ty}')"); pg.wait_for_timeout(80)
            ok(pg.locator('#app ' + sel).count() >= 1, f'{ty}’s example draws as on a song ({sel})')
        pg.evaluate("MKG.open('chain')"); pg.wait_for_timeout(80)
        ok(pg.locator('#app .gdex .mph').count() == 2, 'Chain’s example draws both phrases, joined by the chain')
        pg.evaluate("MKG.open('rhythm')"); pg.wait_for_timeout(80)
        ok(pg.locator('#app [data-a=gdOpen]').count() == 0 and 'Song Clock' in pg.inner_text('#app'), 'Rhythm’s Don’t confuse with is Song Clock timing, with no link')
        # How to mark a song
        pg.evaluate("MKG.open('home')"); pg.wait_for_timeout(100)
        pg.click('#app [data-a=gdOpen][data-v=how]'); pg.wait_for_timeout(150)
        ok(pg.locator('#app h1').inner_text() == 'How to mark a song' and pg.locator('#app .gdpass li').count() == 4, 'How to mark a song shows the four passes')
        ok(pg.locator('#app .gdhabits p').count() == 5 and 'Let timing help.' in pg.inner_text('#app .gdhabits'), 'and all five habits, Let timing help included')
        t.shot(pg, 'how', full_page=True)
        pg.context.close()

    # ===== Key for this song =====
    if 'key' in PARTS:
        pg = t.page(b)
        S = song(pg)
        pg.click('.ckrow [data-a=ckTile][data-v=key]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.sheet") == 'sgKey' and pg.locator('.sheet h2').inner_text() == 'Key for this song', 'the Key tile (pinned beside the artist) opens Key for this song')
        ok('Only the marks this song uses' in pg.inner_text('.sheet'), 'with its lead')
        hdrs = pg.evaluate("[...document.querySelectorAll('.sheet .hdr')].map(h=>h.textContent)")
        ok(hdrs == ['1 · Notes', '2 · Phrasing', 'Notes'], f'only the layers the song uses, in layer order, then Notes ({hdrs})')
        rows = pg.evaluate("[...document.querySelectorAll('.sheet [data-a=gdKeyRow]')].map(r=>r.dataset.v+'|'+r.querySelector('.lbl').firstChild.textContent+'|'+(r.querySelector('small')||{}).textContent)")
        ok(rows[:3] == ['pitch|Pitch|Up, Down · 2 in song', 'phrase|Phrase|1 in song', 'breath|Breath|Quick, Full · 3 in song'],
           f'a row per mark used: the options used and how many (a linked repeat counted once) ({rows[:3]})')
        ok(rows[3:] == ['note|Trouble spot|Lift it', 'note|Note|On “me”'] or rows[3:] == ['note|Note|On “me”', 'note|Trouble spot|Lift it'],
           f'then each Note: its type, then its text (or the words it’s on) ({rows[3:]})')
        t.shot(pg, 'key')
        pg.click('.sheet [data-a=gdKeyRow][data-v=breath]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.sheet") is None and pg.evaluate(HERE)[1:] == ['guide', 'breath'], 'a row closes the sheet and opens that mark’s page')
        pg.click('#barL [data-a=gdBack]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.sheet") is None, 'Back returns to the song')
        # the empty state
        pg.evaluate(f"(()=>{{const s={SONG};Object.values(s.sections).forEach(c=>{{c.marks=[];MARKS.mirror(c)}});save();U.sheet='sgKey';U.sd={{}};rerender()}})()"); pg.wait_for_timeout(200)
        ok('No marks yet. Add marks with the pencil.' in pg.inner_text('.sheet') and pg.locator('.sheet [data-a=gdKeyRow][data-v=home]').count() == 1,
           'a song with no marks: “No marks yet. Add marks with the pencil.” and a Marks guide link')
        pg.click('.sheet [data-a=gdKeyRow][data-v=home]'); pg.wait_for_timeout(250)
        ok(pg.evaluate(HERE)[1:] == ['guide', 'home'] and pg.evaluate("U.sheet") is None, 'which opens the guide home')
        pg.context.close()

    # ===== the peek card =====
    if 'peek' in PARTS:
        pg = t.page(b, w=375, h=667, touch=True)
        S = song(pg)
        mark_side(pg, S)
        n0 = nmarks(pg)
        hold(pg, '#mksheet .mkb[data-v=peak]', 650)
        ok(pg.locator('#mkpeek').count() == 1 and pg.evaluate("MKG.state().peek") == 'peak', 'holding a mark button about half a second opens its peek card')
        ok(nmarks(pg) == n0, 'and letting go doesn’t add the mark')
        c = pg.inner_text('#mkpeek')
        ok('Peak' in c and 'The word the phrase leans towards.' in c and 'One tap' in c and 'Learn more' in c and 'Close' in c,
           'the card shows the name, the options line, the peek line, Close and Learn more')
        ok(pg.locator('#mkpeek .gdex .mpk').count() == 1, 'and the example, drawn by the real renderer')
        ok(pg.evaluate(INSIDE, '#mkpeek'), 'the card is on screen at 375 × 667')
        ok(pg.evaluate("document.getElementById('mkpeek').getBoundingClientRect().bottom<=document.getElementById('mksheet').getBoundingClientRect().top+0.5"), 'above the marks sheet')
        t.shot(pg, 'peek')
        pg.click('#mkpeek [data-a=gdPeekClose]'); pg.wait_for_timeout(150)
        ok(pg.locator('#mkpeek').count() == 0 and nmarks(pg) == n0, 'Close dismisses it')
        # a plain tap still adds
        pg.click('#mksheet .mkb[data-v=peak]'); pg.wait_for_timeout(200)
        ok(nmarks(pg) == n0 + 1 and pg.locator('#mkpeek').count() == 0, 'a plain tap still adds the mark, with no card')
        n1 = nmarks(pg)
        hold(pg, '#mksheet .mkb[data-v=chain]', 250)
        ok(pg.locator('#mkpeek').count() == 0 and nmarks(pg) == n1 + 1, 'a short press is a tap: it adds, with no card')
        n1 = nmarks(pg)
        # a tap outside only closes the card (on a taller iPhone, where words show round the card)
        pg.set_viewport_size({'width': 430, 'height': 932}); pg.wait_for_timeout(300)
        hold(pg, '#mksheet .mkb[data-v=breath]', 650)
        sel = pg.evaluate("JSON.stringify(SG.sel)")
        # a word in plain view (not under the card, the sheet or the bars), tapped where it is: a click that scrolls the
        # page first would close the card by scrolling
        wb = pg.evaluate(OPEN_WORD)
        pg.mouse.click(wb['x'], wb['y']); pg.wait_for_timeout(200)
        ok(pg.locator('#mkpeek').count() == 0 and pg.evaluate("JSON.stringify(SG.sel)") == sel, f'a tap outside closes the card and does nothing else ({sel} → {pg.evaluate("JSON.stringify(SG.sel)")}, card {pg.locator("#mkpeek").count()})')
        pg.mouse.click(wb['x'], wb['y']); pg.wait_for_timeout(200)
        ok(pg.evaluate("JSON.stringify(SG.sel)") != sel and pg.evaluate("!!SG.sel"), 'and the next tap works as usual')
        pg.click(word(S[0]['o'], 0, 1)); pg.wait_for_timeout(200)
        # one card at a time
        hold(pg, '#mksheet .mkb[data-v=breath]', 650)
        hold(pg, '#mksheet .mkb[data-v=shape]', 650)
        ok(pg.locator('#mkpeek').count() == 1 and pg.evaluate("MKG.state().peek") == 'shape' and nmarks(pg) == n1, 'holding another button swaps the card: one at a time, nothing added')
        ok('Swell · Fade · Arc' in pg.inner_text('#mkpeek .pkt small'), 'its options sit in one line; the card never picks one')
        # a scroll dismisses it
        wb = pg.evaluate(OPEN_WORD)
        pg.mouse.move(wb['x'], wb['y']); pg.mouse.wheel(0, 300); pg.wait_for_timeout(250)
        ok(pg.locator('#mkpeek').count() == 0, 'a scroll dismisses it')
        # leaving the screen dismisses it
        hold(pg, '#mksheet .mkb[data-v=breath]', 650)
        pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(200)
        ok(pg.locator('#mkpeek').count() == 0, 'leaving the screen dismisses it')
        pg.evaluate(f"id=>go(()=>{{U.tab='songs';U.view='lyr';U.songId=id}})", pg.evaluate(f"{SONG}.id")); pg.wait_for_timeout(200)
        mark_side(pg, S)
        # Learn more: that mark's page, and Back to the marks sheet with the selection kept
        hold(pg, '#mksheet .mkb[data-v=breath]', 650)
        sel = pg.evaluate("JSON.stringify(SG.sel)")
        pg.click('#mkpeek [data-a=gdPeekMore]'); pg.wait_for_timeout(250)
        ok(pg.evaluate(HERE)[1:] == ['guide', 'breath'] and pg.locator('#mkpeek').count() == 0, 'Learn more opens that mark’s guide page, and the card goes')
        pg.click('#barL [data-a=gdBack]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.sEdit") == 'annotate' and pg.evaluate("JSON.stringify(SG.sel)") == sel and pg.locator('#mksheet').count() == 1,
           'Back lands on the Marks side with the selection and the marks sheet kept')
        # landscape: the card stays on screen
        pg.set_viewport_size({'width': 852, 'height': 393}); pg.wait_for_timeout(300)
        hold(pg, '#mksheet .mkb[data-v=shape]', 650)
        ok(pg.locator('#mkpeek').count() == 1 and pg.evaluate(INSIDE, '#mkpeek'), 'in iPhone landscape the card stays on screen')
        pg.context.close()

    # ===== the doors =====
    if 'doors' in PARTS:
        pg = t.page(b)
        S = song(pg)
        # the marks sheet's "?"
        mark_side(pg, S)
        sel = pg.evaluate("JSON.stringify(SG.sel)")
        q = pg.locator('#mksheet .mkhd [data-a=gdKey]')
        ok(q.count() == 1 and q.get_attribute('aria-label') == 'Key for this song' and
           pg.evaluate("(()=>{const q=document.querySelector('#mksheet [data-a=gdKey]'),x=document.querySelector('#mksheet [data-a=mkClear]');return q.compareDocumentPosition(x)&Node.DOCUMENT_POSITION_FOLLOWING})()"),
           'the marks sheet has a “?” before ✕')
        q.click(); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.sheet") == 'sgKey', '“?” opens Key for this song')
        pg.click('.sheet [data-a=close].xbtn'); pg.wait_for_timeout(250)
        ok(pg.locator('#mksheet').count() == 1 and pg.evaluate("JSON.stringify(SG.sel)") == sel, 'closing it brings the marks sheet back, selection kept')
        # the capsule
        pg.click('#mksheet [data-a=mkClear]'); pg.wait_for_timeout(200)
        cap = pg.locator('#mkcap [data-a=gdOpen][data-v=home]')
        ok(cap.count() == 1 and 'Select words to mark' in pg.inner_text('#mkcap'), 'the “Select words to mark” capsule has a Marks guide link')
        cap.click(); pg.wait_for_timeout(250)
        ok(pg.evaluate(HERE)[1:] == ['guide', 'home'], 'which opens the guide home')
        pg.click('#barL [data-a=gdBack]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.sEdit") == 'annotate' and pg.locator('#mkcap').count() == 1, 'and Back returns to the Marks side')
        pg.evaluate("sgEndEdit(false);rerender()"); pg.wait_for_timeout(200)
        # the ⋯ grid: a Marks guide row under the tiles, kept in Edit, and the Key tile still pinned and pinnable
        pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250)
        r = pg.locator('.sheet .ckgguide [data-a=gdOpen][data-v=home]')
        ok(r.count() == 1 and pg.evaluate("(()=>{const g=document.querySelector('.sheet .ckgrid'),r=document.querySelector('.sheet .ckgguide');return g.compareDocumentPosition(r)&Node.DOCUMENT_POSITION_FOLLOWING})()"),
           'the grid has a Marks guide row under its tiles')
        ok(pg.locator('.sheet .ckgrid [data-v=guide]').count() == 0, 'it isn’t a tile, so it can’t be pinned')
        pg.click('.sheet [data-a=ckGridEdit]'); pg.wait_for_timeout(200)
        ok(pg.locator('.sheet .ckgguide [data-a=gdOpen]').count() == 1, 'it stays in Edit')
        pg.click('.sheet [data-a=ckTile][data-v=key]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("ckPrefs().pins").count('key') == 0, 'the Key tile still unpins')
        pg.click('.sheet [data-a=ckTile][data-v=key]'); pg.wait_for_timeout(150)
        ok('key' in pg.evaluate("ckPrefs().pins"), 'and pins again')
        pg.click('.sheet [data-a=ckGridEdit]'); pg.wait_for_timeout(150)
        pg.click('.sheet .ckgguide [data-a=gdOpen]'); pg.wait_for_timeout(250)
        ok(pg.evaluate(HERE)[1:] == ['guide', 'home'] and pg.evaluate("U.sheet") is None, 'the row closes the grid and opens the guide home')
        pg.click('#barL [data-a=gdBack]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.view") == 'lyr', 'Back returns to the song')
        pg.click('[data-a=ckGrid]'); pg.wait_for_timeout(250)
        pg.click('.sheet [data-a=ckTile][data-v=key]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.sheet") == 'sgKey' and 'Key for this song' in pg.inner_text('.sheet'), 'the grid’s Key tile opens Key for this song')
        pg.evaluate("U.sheet=null;rerender()")
        # Settings
        pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(200)
        keys = pg.evaluate("[...document.querySelectorAll('#app .grp.tiled.setgap')][0].querySelectorAll('.row').length&&[...[...document.querySelectorAll('#app .grp.tiled.setgap')][0].querySelectorAll('.row')].map(r=>r.dataset.v)")
        ok(keys == ['recall', 'coach', 'home', 'voice', 'player', 'appear', 'access'], f'Settings has a Marks guide row after Coach video ({keys})')
        sr = pg.locator('#app .row[data-a=gdOpen][data-v=home]')
        ok(sr.locator('.tile').count() == 1 and sr.locator('.mut:not([aria-hidden])').count() == 0 and sr.inner_text().strip().startswith('Marks guide'),
           'with its own icon tile and no value')
        sr.click(); pg.wait_for_timeout(250)
        ok(pg.evaluate(HERE) == ['settings', 'guide', 'home'], 'which opens the guide home')
        pg.click('#barL [data-a=gdBack]'); pg.wait_for_timeout(250)
        ok(pg.evaluate(HERE) == ['settings', None, None], 'and Back returns to Settings')
        pg.context.close()

    # ===== the native push on iPhone, swipe back, and Reduce Motion =====
    if 'push' in PARTS:
        on = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"
        pg = t.page(b, w=390, h=844, touch=True, init=on)
        pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(300)
        pg.click('#app [data-zk="mk:guide"]'); pg.wait_for_timeout(80)
        ok(pg.locator('.zm.push').count() == 1, 'the Settings row pushes the guide in from the right on iPhone')
        pg.wait_for_function("!ZOOM.busy()", timeout=5000); pg.wait_for_timeout(100)
        st = pg.evaluate("ZOOM.stack().map(s=>s.key+'/'+s.kind)")
        ok(st == ['mk:guide/push'], f'as a push on the stack ({st})')
        pg.click('#app [data-zk="mk:pitch"]'); pg.wait_for_function("!ZOOM.busy()", timeout=5000); pg.wait_for_timeout(100)
        ok(pg.evaluate("ZOOM.stack().map(s=>s.key)") == ['mk:guide', 'mk:pitch'], 'a mark’s row pushes its page')
        # swipe back from the title: past the threshold goes back to the home
        bx = pg.locator('#app h1').bounding_box()
        y = bx['y'] + bx['height'] / 2
        pg.evaluate("""a=>{const [x0,x1,y]=a,el=document.querySelector('#app h1');const f=(type,x)=>{const t=new Touch({identifier:7,target:el,clientX:x,clientY:y});
          el.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true}))};
          f('touchstart',x0);for(let i=1;i<=12;i++)f('touchmove',x0+(x1-x0)*i/12);f('touchend',x1)}""", [bx['x'] + 10, bx['x'] + 260, y])
        pg.wait_for_function("!ZOOM.busy()", timeout=5000); pg.wait_for_timeout(200)
        ok(pg.evaluate(HERE) == ['settings', 'guide', 'home'], 'swiping back from a mark’s page returns to the guide home')
        pg.click('#barL [data-a=gdBack]'); pg.wait_for_function("!ZOOM.busy()", timeout=5000); pg.wait_for_timeout(100)
        ok(pg.evaluate(HERE) == ['settings', None, None] and pg.evaluate("ZOOM.stack().length") == 0 and pg.locator('.zm').count() == 0,
           'Back slides the guide away to Settings, leaving nothing behind')
        # from a song's Key sheet (no card): pushed all the same
        S = song(pg)
        pg.click('.ckrow [data-a=ckTile][data-v=key]'); pg.wait_for_timeout(500)
        pg.click('.sheet [data-a=gdKeyRow][data-v=pitch]'); pg.wait_for_timeout(60)
        ok(pg.locator('.zm.push').count() == 1, 'a row in Key for this song pushes its page too')
        pg.wait_for_function("!ZOOM.busy()", timeout=5000)
        pg.context.close()
        # Reduce Motion: the card and the pages fade
        pg = t.page(b, w=390, h=844, touch=True, init=on, ctx_args={'reduced_motion': 'reduce'})
        S = song(pg)
        mark_side(pg, S)
        pg.evaluate("(()=>{window.__kf=[];const a=Element.prototype.animate;Element.prototype.animate=function(k,o){if(this.id==='mkpeek')__kf.push(k);return a.call(this,k,o)}})()")
        hold(pg, '#mksheet .mkb[data-v=breath]', 600)
        kf = pg.evaluate("__kf.flatMap(k=>k.flatMap(f=>Object.keys(f)))")
        ok(kf and set(kf) == {'opacity'}, f'with Reduce Motion the peek card only fades ({sorted(set(kf))})')
        pg.click('#mkpeek [data-a=gdPeekMore]')
        pg.wait_for_function("document.querySelector('.zm.push .zm-page')&&document.querySelector('.zm.push .zm-page').getAnimations().length>0", timeout=5000)
        keys = pg.evaluate("[...document.querySelectorAll('.zm, .zm *')].flatMap(e=>e.getAnimations()).flatMap(a=>Object.keys(a.effect.getKeyframes()[0])).filter(k=>!['offset','easing','composite','computedOffset'].includes(k))")
        ok(keys and set(keys) == {'opacity'}, f'and a guide page fades in rather than sliding ({sorted(set(keys))})')
        pg.wait_for_function("!ZOOM.busy()", timeout=5000)
        ok(pg.evaluate(HERE)[1:] == ['guide', 'breath'], 'landing on the right page')
        pg.context.close()

    # ===== every size, light and dark =====
    if 'sizes' in PARTS:
        for w, h, sc, touch in ((390, 844, 'light', True), (375, 667, 'dark', True), (320, 568, 'light', True), (852, 393, 'dark', True),
                                (820, 1180, 'light', True), (1180, 820, 'dark', True), (1440, 900, 'light', False)):
            pg = t.page(b, w=w, h=h, sc=sc, touch=touch, **({'ua': None} if w == 1440 else {}))
            S = song(pg)
            bad = []
            for pgk in ('home', 'how', 'chain', 'register', 'colour', 'intention'):
                pg.evaluate(f"MKG.open('{pgk}')"); pg.wait_for_timeout(150)
                if not pg.evaluate(FITS): bad.append(pgk + ' scrolls sideways')
                if pg.evaluate("U.view") != 'guide' or not pg.locator('#app h1').count(): bad.append(pgk + ' didn’t open')
            t.shot(pg, f'{w}x{h}-{sc}-mark')
            for i in range(8): pg.evaluate("MKG.back()"); pg.wait_for_timeout(60)
            if pg.evaluate("U.view") == 'guide': bad.append('Back didn’t leave the guide')
            pg.evaluate("U.sheet='sgKey';U.sd={};rerender()"); pg.wait_for_timeout(250)
            if not pg.evaluate(INSIDE, '.sheet') and pg.evaluate("document.querySelector('.sheet').getBoundingClientRect().left<0"): bad.append('key sheet off screen')
            if not pg.evaluate(FITS): bad.append('key sheet scrolls sideways')
            pg.evaluate("U.sheet=null;rerender()"); pg.wait_for_timeout(150)
            mark_side(pg, S)
            hold(pg, '#mksheet .mkb[data-v=breath]', 650)
            if not pg.evaluate(INSIDE, '#mkpeek'): bad.append('peek card off screen')
            if not pg.evaluate(FITS): bad.append('peek card scrolls sideways')
            t.shot(pg, f'{w}x{h}-{sc}-peek')
            ok(not bad, f'{w}×{h} {sc}: the guide pages, Key for this song and the peek card fit' + (' — ' + '; '.join(bad) if bad else ''))
            pg.context.close()
