"""Recall: the five hint levels hide letters in place without moving the layout, tapping a line peeks at it, the hint
capsule and its menu, From the start / From the end / Start anywhere, and Recall always starting at Full lyrics."""
from harness import with_song_practice

LYR = ("[Verse]\nPaper boats along the gutter\nRacing rain down Elmwood Lane\n\n[Chorus]\nCarry me over\nLet the river know\n\n"
       "[Verse]\nEvery window holds a candle\n\n[Chorus]\nCarry me over\nLet the river know\n\n[Outro]\nLet the river know my name")
ADD = """l=>{U.sDraft={step:1,title:'river song',artist:'',text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();
  const s=songById(U.songId),sid=s.order[1].sid;s.sections[sid].ann['0:1']={br:1,v:'mee'};s.sections[sid].ann['1:3']={nt:'Lift the last word'};
  s.sections[sid].cue='Open, full voice';save();rerender();return s.order.map(x=>x.o)}"""
# the text a reader can see on the first chorus: hidden letters are transparent
SEEN = """()=>{const s=document.querySelectorAll('.sgsec')[1];const c=s.cloneNode(true);c.querySelectorAll('.hx').forEach(x=>x.textContent='_'.repeat(x.textContent.length));
  const v=c.querySelector('.w .v');const vt=v?v.textContent:'';c.querySelectorAll('.w .v').forEach(x=>x.remove());
  return [...c.querySelectorAll('.sgl,.sgnote,.sgcue')].map(x=>x.textContent.trim()).concat(['v:'+vt])}"""
BOXES = "()=>[...document.querySelectorAll('.sgsec')].map(s=>{const r=s.getBoundingClientRect();return [Math.round(r.height),Math.round(r.width)]})"


def run(b, t):
    ok = t.ok
    pg = t.page(b, touch=True, data=with_song_practice())
    pg.evaluate("U.tab='songs';render()")
    order = pg.evaluate(ADD, LYR); pg.wait_for_timeout(300)
    ok(pg.locator('[data-a=sgMode]').count() == 3 and pg.locator('[data-a=sgMode][data-v=recall]').inner_text().strip() == 'Recall',
       'Recall sits between Practise and Perform')
    sizes = pg.evaluate(BOXES)
    pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.sMode") == 'recall' and pg.evaluate("U.sHint") == 0 and pg.locator('.hx').count() == 0, 'Recall starts at Full lyrics')
    ok(pg.locator('#dock .hcap').count() == 1 and pg.locator('#dock .tabbar').count() == 0 and 'Full lyrics' in pg.inner_text('.hcap'),
       'the hint capsule takes the place of the tab bar')
    ok(pg.locator('.hcap [data-v="-1"]').is_disabled() and not pg.locator('.hcap [data-v="1"]').is_disabled(), 'Show more is off at Full lyrics')
    ok(pg.locator('[data-a=sgKey]').count() == 0 and pg.locator('#sgrbtn').count() == 1, 'Recall has its options button instead of Key')

    expect = {
        1: (['C____ m_ o___', 'L__ t__ r____ k___', 'Lift the last word', 'Open, full voice', 'v:mee'], 'Word shapes'),
        2: (['Carry __ ____', 'Let ___ _____ ____', '____ ___ ____ ____', 'Open, full voice', 'v:___'], 'First words'),
        3: (['_____ __ ____', '___ ___ _____ ____', '____ ___ ____ ____', 'Open, full voice', 'v:___'], 'Cues only'),
        4: (['_____ __ ____', '___ ___ _____ ____', '____ ___ ____ ____', '____, ____ _____', 'v:___'], 'Blank'),
    }
    for lv in range(1, 5):
        pg.click('.hcap [data-v="1"]'); pg.wait_for_timeout(250)
        seen = pg.evaluate(SEEN); want, name = expect[lv]
        ok(sorted(seen) == sorted(want), f'{name}: ' + ' | '.join(seen))
        ok(name in pg.inner_text('.hcap') and pg.locator('.hdots i.on').count() == 1, f'the capsule says {name}')
        ok(pg.evaluate(BOXES) == sizes, f'{name}: nothing moves')
    ok(pg.locator('.hcap [data-v="1"]').is_disabled(), 'Hide more is off at Blank')
    ok(pg.locator('.sgsec >> nth=1 >> .m.br').count() == 1 and pg.locator('.sgsec >> nth=1 >> .m.nt').count() == 1, 'marks stay visible in Recall')
    t.shot(pg, 'blank', full_page=True)

    # peek
    pg.click('.sgsec >> nth=1 >> .sgl >> nth=0'); pg.wait_for_timeout(600)
    ok(pg.locator('.sgsec >> nth=1 >> .sgl.peeking').count() == 1 and pg.evaluate("U.sSec") is None,
       'tapping a hidden line peeks at it, without selecting the section')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.sgl.peeking .hx')).color") != 'rgba(0, 0, 0, 0)', 'the peeked letters show')
    t.shot(pg, 'peek')
    pg.wait_for_timeout(2400)
    ok(pg.locator('.sgl.peeking').count() == 0, 'and hides them again after a moment')
    pg.click('.sgsec >> nth=1 >> .sglab'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sSec") == order[1] and pg.locator('.sgsec.sel [data-a=sgRec]').count() == 1, 'tapping a heading still selects the section to record')
    pg.click('.sgsec >> nth=1 >> .sglab'); pg.wait_for_timeout(200)
    pg.focus('.sgsec >> nth=2 >> .sgl >> nth=0'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    ok(pg.locator('.sgsec >> nth=2 >> .sgl.peeking').count() == 1, 'Enter peeks at a focused line')

    # the hint menu
    pg.click('#sghname'); pg.wait_for_timeout(300)
    ok(pg.locator('#hmenu [role=menuitemradio]').count() == 5 and pg.locator('#hmenu [aria-checked=true]').inner_text().strip() == 'Blank',
       'the level menu lists the five levels')
    ok(pg.evaluate("(()=>{const m=document.getElementById('hmenu').getBoundingClientRect(),c=document.querySelector('.hcap').getBoundingClientRect();return m.bottom<=c.top&&m.left>=0&&m.right<=innerWidth})()"),
       'it opens above the capsule, on screen')
    pg.click('#hmenu [data-v="2"]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sHint") == 2 and pg.locator('#hmenu').count() == 0, 'picking a level closes the menu')
    pg.click('#sghname'); pg.wait_for_timeout(200); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.locator('#hmenu').count() == 0, 'Escape closes it')

    # where to start
    pg.click('#sgrbtn'); pg.wait_for_timeout(300)
    ok(pg.locator('#rmenu button').count() == 3 and pg.locator('#rmenu [aria-checked=true]').inner_text().strip() == 'From the start', 'the options menu')
    pg.click('#rmenu [data-v=end]'); pg.wait_for_timeout(500)
    ok(pg.evaluate("[...document.querySelectorAll('.sgsec')].map(s=>s.dataset.o)") == order[::-1] and 'Working from the end' in pg.inner_text('main'),
       'From the end lists the sections last first')
    pg.click('#sgrbtn'); pg.wait_for_timeout(200); pg.click('#rmenu [data-a=sgAnywhere]'); pg.wait_for_timeout(400)
    ok('Start from' in pg.inner_text('.toast') and pg.locator('.sgsec.flash').count() == 1, 'Start anywhere picks a section and points to it')
    pg.click('#sgrbtn'); pg.wait_for_timeout(200); pg.click('#rmenu [data-v=start]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("[...document.querySelectorAll('.sgsec')].map(s=>s.dataset.o)") == order, 'From the start puts them back')

    # leaving and coming back: always Full lyrics
    pg.click('[data-a=sgMode][data-v=practise]'); pg.wait_for_timeout(400)
    ok(pg.locator('.hx').count() == 0 and pg.locator('#dock .hcap').count() == 0 and pg.locator('#dock .tabbar').count() == 1,
       'Practise shows everything and the tab bar again')
    pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.sHint") == 0 and pg.locator('.hx').count() == 0, 'coming back to Recall starts at Full lyrics again')
    pg.click('.hcap [data-v="1"]'); pg.wait_for_timeout(200)
    pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(250)
    ok(pg.locator('.hx').count() == 0 and pg.locator('#dock .hcap').count() == 0, 'editing shows the full lyrics')
    pg.evaluate("sgEndEdit(true);rerender()"); pg.wait_for_timeout(200)

    # on iPad and Mac too
    for w, h in [(820, 1180), (1440, 900)]:
        pg2 = t.page(b, w, h, ua=None if w > 1000 else None, data=with_song_practice())
        pg2.evaluate("U.tab='songs';render()"); pg2.evaluate(ADD, LYR); pg2.wait_for_timeout(300)
        pg2.click('[data-a=sgMode][data-v=recall]'); pg2.wait_for_timeout(400)
        pg2.click('.hcap [data-v="1"]'); pg2.wait_for_timeout(200)
        ok(pg2.locator('.hcap').count() == 1 and pg2.locator('.hx').count() > 0 and pg2.evaluate("document.documentElement.scrollWidth<=innerWidth"),
           f'{w}x{h}: Recall works in the song pane')
        pg2.context.close()
