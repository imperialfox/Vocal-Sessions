"""Progress tab: the chart ranges, picking a bar, the doors to All sessions, and time per step."""
import json
from harness import with_song_practice

def run(b, t):
    ok = t.ok
    data = with_song_practice()
    pg = t.page(b, data=data)
    sp = pg.evaluate("splitOf(D.sessions.find(s=>s.id==='s2'))")
    exp_f = (435 + 355 + 380 * 2 / 3 + 355) / 60; exp_r = (520 + 437 / 3) / 60
    k = 30 / (exp_f + exp_r) if exp_f + exp_r > 30 else 1
    ok(sp['mixed'] and abs(sp['f'] - exp_f * k) < 0.01 and abs(sp['f'] + sp['r'] + sp['a'] - 30) < 0.01,
       'an older session is split using the coach video, scaled to its 30 minutes')
    pg.click('[data-a=tab][data-v=history]'); pg.wait_for_timeout(300)
    ok(pg.locator('main .grp >> nth=0').locator('[data-v=session]').count() >= 1, 'Recent shows sessions')
    ok(pg.locator('#pchart rect[data-pick]').count() == 7, 'the week chart has 7 bars')
    for r, nb in [('D', 24), ('M', None), ('6M', 26), ('Y', 12), ('All', None), ('W', 7)]:
        pg.click(f'[data-a=prange][data-v="{r}"]'); pg.wait_for_timeout(300)
        n = pg.locator('#pchart rect[data-pick]').count(); ok((nb is None and n > 0) or n == nb, f'{r} range draws {n} bars')
    bx = pg.locator('#pchart').bounding_box(); pg.mouse.click(bx['x'] + bx['width'] * 0.2, bx['y'] + bx['height'] * 0.6); pg.wait_for_timeout(200)
    ok('PRACTISED' in pg.inner_text('#pcard .kick').upper(), 'tapping a bar shows that day')
    t.shot(pg, 'picked')
    pg.wait_for_timeout(400); pg.click('h1'); pg.wait_for_timeout(200)
    ok('TOTAL' in pg.inner_text('#pcard .kick').upper(), 'tapping elsewhere goes back to the total')
    pg.click('[data-a=pnav][data-v="-1"]'); pg.wait_for_timeout(200); ok(pg.evaluate("U.roff") == -1, 'the back arrow steps back a week')
    pg.click('[data-a=prange][data-v="W"]'); pg.wait_for_timeout(300)
    t.shot(pg, 'progress', full_page=True)

    pg.click('[data-a=openAll][data-v=songs]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'all' and pg.evaluate("U.histTab") == 'songs', 'Show all song practice opens the list on its tab')
    pg.click('[data-a=allBack]'); pg.wait_for_timeout(200); ok(pg.evaluate("U.view") is None and pg.evaluate("U.tab") == 'history', 'back returns to Progress')
    pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.histTab") == 'sessions' and pg.locator('.ptag').count() >= 1, 'Show all sessions lists them, older ones tagged as filled in at the end')
    pg.click('[data-a=allBack]'); pg.click('[data-a=tab][data-v=exercises]'); pg.wait_for_timeout(200)
    ok(pg.locator('main [data-a=openAll][data-v=songs]').count() == 0 and 'Versace' not in pg.inner_text('main'), 'songs live in Songs now, not Exercises')

    # a timed session
    pg.click('[data-a=tab][data-v=today]'); pg.click('[data-a=start]'); pg.wait_for_timeout(200)
    pg.evaluate("for(const e of FOUND)X.f[e.id]=3;X.rot={rung:3};X.start=Date.now()-50*60000;X.fE=25*60;X.rE=40*60;X.fEnd=Date.now();X.rEnd=Date.now();saveDraft();U.view='app';render()")
    pg.click('[data-a=cta]'); pg.wait_for_timeout(500); pg.click('[data-a=saveHow]'); pg.wait_for_timeout(500)
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss['mixed'] is False and ss['split'] == {'f': 25, 'r': 15, 'a': 10}, 'a timed session saves its real split ' + json.dumps(ss.get('split')))
    pg.click('.xbtn[data-a=close]'); pg.wait_for_timeout(300)
    # filled in at the end
    pg.click('[data-a=start]'); pg.wait_for_timeout(200)
    pg.evaluate("for(const e of FOUND)X.f[e.id]=3;X.rot={vertical:2};X.start=Date.now()-45*60000;X.fE=44*60;X.rE=44.5*60;X.fEnd=Date.now();X.rEnd=Date.now();saveDraft();U.view='app';render()")
    pg.click('[data-a=cta]'); pg.wait_for_timeout(500); pg.click('[data-a=saveHow]'); pg.wait_for_timeout(500)
    ss = pg.evaluate("D.sessions[D.sessions.length-1]"); sp = pg.evaluate("splitOf(D.sessions[D.sessions.length-1])")
    ok(ss['mixed'] is True and 'split' not in ss, 'quick steps mark the session as filled in at the end')
    ok(abs(sp['f'] - 25.4) < 0.1 and abs(sp['r'] - 460 * 2 / 3 / 60) < 0.1, 'and it is split by the coach video')
    pg.click('.shead [data-a=editSess]'); pg.wait_for_timeout(500); pg.click('[data-a=esplit][data-v=timed]'); pg.wait_for_timeout(400)
    pg.fill('#edF', '20'); pg.fill('#edR', '10'); a = pg.inner_text('#edA'); t.shot(pg, 'edit-split', full_page=True)
    pg.click('[data-a=saveEdit]'); pg.wait_for_timeout(400); ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss['mixed'] is False and ss['split'] == {'f': 20, 'r': 10, 'a': 15}, f'Edit sets timed minutes ({a} shown for Application)')
    pg.click('.shead [data-a=editSess]'); pg.wait_for_timeout(500); pg.fill('#edF', '40'); pg.click('[data-a=saveEdit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'edit', 'Edit refuses steps adding up to more than the total')
    pg.click('[data-a=esplit][data-v=mixed]'); pg.wait_for_timeout(400); pg.click('[data-a=saveEdit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.sessions[D.sessions.length-1].mixed") is True, 'Edit can switch back to filled in at the end')
    pg.click('.xbtn[data-a=close]'); pg.wait_for_timeout(300)
    pg.click('[data-a=tab][data-v=history]'); pg.click('[data-a=prange][data-v=D]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("period().sess.length") == 2, 'Day view shows both new sessions')
    ok(not pg.evaluate("document.documentElement.scrollWidth>innerWidth"), 'no sideways scroll')

    ip = t.page(b, 1180, 820, data=data); ip.click('[data-a=tab][data-v=history]'); ip.wait_for_timeout(300)
    ip.click('[data-a=openAll][data-v=sessions]'); ip.wait_for_timeout(300)
    ok(ip.locator('.pane .ph').count() == 1, 'on iPad, All sessions has a detail pane'); t.shot(ip, 'ipad-all')
