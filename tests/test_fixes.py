"""3.10.1 fixes: sheets keep their scroll to themselves, song practice is timed from its first take, the weekly goal
opens Progress, and Recall's pills, hold to peek and Peek length setting."""
import os, json
from harness import with_song_practice, ready, OUT, fix, SEED, UA_IPHONE
from test_recall import LYR, ADD

LAUNCH_ARGS = ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']


def swipe(pg, x, y0, y1, steps=10):
    """A real one-finger swipe, sent the way a touchscreen sends it."""
    cdp = pg.context.new_cdp_session(pg)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y0}]})
    for i in range(1, steps + 1):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y0 + (y1 - y0) * i / steps}]})
        pg.wait_for_timeout(16)
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    pg.wait_for_timeout(450)
    cdp.detach()


def sheets(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=700, touch=True, data=with_song_practice())
    pg.evaluate("document.querySelector('main').style.paddingBottom='1200px'")  # room to scroll Today
    swipe(pg, 200, 500, 250)
    ok(pg.evaluate("scrollY") > 50, 'a swipe on the page scrolls it (so the swipes below are real)')
    pg.click('.titlerow [data-a=openCal]'); pg.wait_for_timeout(700)
    ok(pg.evaluate("U.sheet") == 'calendar', 'the practice calendar opens')
    pg.evaluate("scrollTo(0,120)"); pg.wait_for_timeout(200)  # the page behind, part way down
    y = pg.evaluate("scrollY")
    box = pg.locator('.sheet').bounding_box()
    for name, (x, ya, yb) in {
        'the calendar sheet (up)': (box['x'] + box['width'] / 2, box['y'] + box['height'] * .7, box['y'] + box['height'] * .2),
        'the calendar sheet (down)': (box['x'] + box['width'] / 2, box['y'] + box['height'] * .3, box['y'] + box['height'] * .8),
        'the dimmed page (up)': (200, 60, 20) if box['y'] < 90 else (200, box['y'] - 10, 20),
    }.items():
        swipe(pg, x, ya, yb)
        ok(pg.evaluate("scrollY") == y and pg.evaluate("U.sheet") == 'calendar', f'swiping {name} leaves the page behind still')
    pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    pg.mouse.wheel(0, 600); pg.wait_for_timeout(300); pg.mouse.wheel(0, -600); pg.wait_for_timeout(300)
    ok(pg.evaluate("scrollY") == y, 'the mouse wheel over the sheet leaves the page behind still')
    pg.mouse.move(195, 20); pg.mouse.wheel(0, 600); pg.wait_for_timeout(300)
    ok(pg.evaluate("scrollY") == y, 'the mouse wheel over the dimmed page leaves it still')

    # dragging the header down still closes the sheet
    hb = pg.locator('.sheet .shead').bounding_box()
    swipe(pg, hb['x'] + 40, hb['y'] + 10, hb['y'] + 260)
    pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") is None, 'dragging a sheet down by its header still closes it')

    # a tall sheet still scrolls inside itself, and stops at its ends without moving the page
    pg.evaluate("U.tab='settings';U.view=null;render();scrollTo(0,0)"); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('main').style.paddingBottom='1200px';scrollTo(0,80)")
    y = pg.evaluate("scrollY")
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000); pg.wait_for_timeout(700)
    tall = pg.evaluate("(()=>{const s=document.querySelector('.sheet');return s.scrollHeight>s.clientHeight+20})()")
    ok(tall, 'Backup ready is taller than the screen here')
    box = pg.locator('.sheet').bounding_box()
    cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    swipe(pg, cx, cy + 120, cy - 120)
    ok(pg.evaluate("document.querySelector('.sheet').scrollTop") > 20 and pg.evaluate("scrollY") == y, 'a swipe scrolls the tall sheet itself')
    pg.mouse.move(cx, cy)
    for _ in range(4): pg.mouse.wheel(0, 800); pg.wait_for_timeout(150)
    ok(pg.evaluate("(()=>{const s=document.querySelector('.sheet');return s.scrollTop+s.clientHeight>=s.scrollHeight-2})()"),
       'the wheel scrolls it to the bottom')
    swipe(pg, cx, cy + 120, cy - 120); pg.mouse.wheel(0, 800); pg.wait_for_timeout(300)
    ok(pg.evaluate("scrollY") == y, 'going past its bottom leaves the page behind still')
    pg.evaluate("document.querySelector('.sheet').scrollTop=0"); pg.wait_for_timeout(100)
    pg.mouse.wheel(0, -800); pg.wait_for_timeout(300)
    ok(pg.evaluate("scrollY") == y, 'and so does going past its top')
    pg.context.close()


def song_practice(b, t):
    ok = t.ok
    pg = t.page(b, ctx_args={'permissions': ['microphone']})
    pg.click('[data-a=songStart]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'song' and pg.evaluate("X.start") is None, 'song practice opens with no start time')
    ok(pg.inner_text('#timer').strip() == 'Not started', 'the timer pill says Not started')
    ok(pg.locator('#timer[data-a]').count() == 0, 'the pill doesn’t open the clock')
    pg.click('#timer'); pg.wait_for_timeout(300)
    ok(pg.locator('.clock').count() == 0 and not pg.evaluate("U.clock"), 'so there’s no clock or Pause yet')
    ok(pg.inner_text('#dock .cta').strip() == 'Record a take first', 'the dock button says Record a take first')
    pg.click('#dock .cta', force=True); pg.wait_for_timeout(300)  # aria-disabled, so Playwright needs force
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("X") is not None and pg.locator('.toast').count() == 1, 'and can’t save it')
    ok(pg.evaluate("localStorage.getItem('vocalDraft')") is None, 'nothing is kept as a draft')
    pg.wait_for_timeout(1300)
    ok(pg.inner_text('#timer').strip() == 'Not started' and pg.evaluate("elapsedSec()") == 0, 'waiting isn’t counted')
    pg.click('#bar [data-a=exit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("X") is None, 'leaving before a take drops it quietly')
    ok('In progress' not in pg.inner_text('main') and pg.locator('[data-a=resume]').count() == 0, 'Today shows nothing in progress')

    # the clock starts with the first take
    pg.click('[data-a=songStart]'); pg.wait_for_timeout(200)
    pg.click('[data-a=song][data-k=g_1]'); pg.wait_for_timeout(1200)
    opened = pg.evaluate("Date.now()")
    pg.click('[data-a=rec]'); pg.wait_for_function("!!rec", timeout=5000)
    st = pg.evaluate("[X.start, rec.started]")
    ok(st[0] is not None and st[0] == st[1] and st[0] >= opened, 'the clock starts when the first take starts recording')
    ok(json.loads(pg.evaluate("localStorage.getItem('vocalDraft')") or '{}').get('start') == st[0], 'the draft is kept from then on')
    pg.wait_for_timeout(2200)
    ok(pg.inner_text('#timer').strip() not in ('Not started', '0:00') and pg.locator('#timer[data-a=clock]').count() == 1,
       'the pill shows the running time: ' + pg.inner_text('#timer'))
    pg.click('[data-a=rec]'); pg.wait_for_timeout(1300)
    ok(pg.evaluate("X.takes.length") == 1 and pg.evaluate("X.start") == st[0], 'saving the take keeps the start')
    ok(pg.inner_text('#dock .cta').strip() == 'Save song practice', 'and the dock button saves again')
    pg.click('#timer'); pg.wait_for_timeout(500)
    ok(pg.locator('.clock').count() == 1, 'the clock opens now')
    pg.click('.clock [data-a=clockClose]'); pg.wait_for_timeout(500)
    pg.click('#bar [data-a=exit]'); pg.wait_for_timeout(300)
    ok('In progress' in pg.inner_text('main'), 'once timed, Today shows song practice in progress')
    pg.click('[data-a=songStart]'); pg.wait_for_timeout(300)
    pg.evaluate("X.start-=4*60e3;saveDraft()")  # four minutes since the first take
    pg.click('#dock .cta'); pg.wait_for_timeout(500); pg.click('[data-a=saveHow]'); pg.wait_for_timeout(500)
    ss = pg.evaluate("D.songSessions[D.songSessions.length-1]")
    ok(ss['mins'] == 4 and pg.evaluate(f"new Date({json.dumps(ss['date'])}).getTime()") == st[0] - 240000,
       'a saved song practice counts its minutes from the first take')
    pg.click('.xbtn[data-a=close]'); pg.wait_for_timeout(300)

    # from a song's screen too
    pg.evaluate(ADD, LYR); pg.wait_for_timeout(300)
    pg.click('[data-a=sgPractise]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'song' and pg.evaluate("X.start") is None and pg.inner_text('#timer').strip() == 'Not started',
       'Song practice from a song isn’t timed until a take either')
    pg.click('#bar [data-a=exit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("X") is None, 'and leaving it drops it')

    # a draft from an older version, with a start, carries on as before
    started = pg.evaluate("Date.now()-10*60e3")
    pg.evaluate("d=>{localStorage.setItem('vocalDraft',JSON.stringify(d))}",
                {'kind': 'song', 'start': started, 'song': 'g_1', 'f': {}, 'xn': {}, 'rot': {}, 'rate': {}, 'takes': [], 'how': [], 'howNote': '', 'pausedTotal': 0})
    pg.reload(); ready(pg)
    ok('In progress' in pg.inner_text('main'), 'an older song practice draft still shows in progress')
    pg.click('[data-a=songStart]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("X.start") == started and pg.inner_text('#timer').strip().startswith('10:'), 'and resumes with its own start: ' + pg.inner_text('#timer'))
    pg.context.close()


def goal(b, t):
    ok = t.ok
    for w, h in [(390, 844), (1180, 820)]:
        pg = t.page(b, w=w, h=h, ua=UA_IPHONE if w < 500 else None)
        pg.evaluate("U.tab='history';U.range='M';U.roff=-2;U.histTab='songs';render()"); pg.wait_for_timeout(200)
        pg.evaluate("U.tab='today';render();scrollTo(0,0)"); pg.wait_for_timeout(200)
        a = pg.locator('button.arch[data-a=goalOpen]')
        ok(a.count() == 1 and 'Open Progress' in (a.get_attribute('aria-label') or '') and 'minute goal' in a.get_attribute('aria-label'),
           f'{w}x{h}: the goal arc is a button: ' + str(a.get_attribute('aria-label')))
        a.click(); pg.wait_for_timeout(400)
        st = pg.evaluate("[U.tab,U.view,U.range,U.roff,U.histTab,scrollY]")
        ok(st == ['history', None, 'W', 0, 'sessions', 0], f'{w}x{h}: it opens Progress on this week’s sessions: {st}')
        ok(pg.locator('[data-a=prange][data-v=W].on').count() == 1, f'{w}x{h}: the week range is selected')
        pg.evaluate("U.tab='today';U.histTab='songs';render()"); pg.wait_for_timeout(200)
        pg.focus('button.arch'); pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
        ok(pg.evaluate("[U.tab,U.histTab]") == ['history', 'sessions'], f'{w}x{h}: Enter does the same')
        pg.context.close()


# each line's place and size, measured from the top of the lyrics (Recall's subtitle sits above them)
LINES = """()=>{const o=document.querySelector('.sgsec').getBoundingClientRect();
  return [...document.querySelectorAll('.sgl,.sgnote,.sgcue')].map(x=>{const r=x.getBoundingClientRect();return [r.x-o.x,r.y-o.y,r.width,r.height].map(n=>Math.round(n*10)/10)})}"""
PILLS = """()=>[...document.querySelectorAll('.hx')].every(x=>{const a=getComputedStyle(x,'::after');
  return x.getAttribute('aria-hidden')==='true'&&a.content!=='none'&&a.borderRadius!=='0px'&&a.backgroundColor!=='rgba(0, 0, 0, 0)'
    &&getComputedStyle(x).color==='rgba(0, 0, 0, 0)'&&a.opacity==='1'})"""


def recall(b, t):
    ok = t.ok
    sizes = [(390, 844, 'light'), (390, 844, 'dark'), (820, 1180, 'light'), (1440, 900, 'dark')]
    for w, h, sc in sizes:
        tag = f'{w}x{h} {sc}'
        pg = t.page(b, w=w, h=h, sc=sc, touch=w < 500, ua=UA_IPHONE if w < 500 else None, data=with_song_practice())
        pg.evaluate("U.tab='songs';render()")
        pg.evaluate(ADD, LYR); pg.wait_for_timeout(300)
        pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(450)
        full = pg.evaluate(LINES)
        for lv, name in enumerate(['Word shapes', 'First words', 'Cues only', 'Blank'], 1):
            pg.evaluate(f"SG_ACT.sgSetHint(null,{lv})"); pg.wait_for_timeout(500)
            n = pg.locator('.hx').count()
            ok(n > 0 and pg.evaluate(PILLS), f'{tag} · {name}: {n} hidden runs show as pills, hidden from screen readers')
            ok(pg.evaluate(LINES) == full, f'{tag} · {name}: every line keeps its place and size')
            cue = pg.locator('.sgcue .hx').count()
            ok((cue > 0) == (lv == 4), f'{tag} · {name}: the cue line hides only at Blank')
            if w == 390 and lv in (1, 4): t.shot(pg, f'pills-{sc}-{lv}')
        pg.context.close()

    # peeking, holding and the Peek length setting
    pg = t.page(b, touch=False, data=with_song_practice())
    pg.evaluate("U.tab='songs';render()")
    pg.evaluate(ADD, LYR); pg.wait_for_timeout(300)
    sid = pg.evaluate("U.songId")
    pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(400)
    pg.evaluate("SG_ACT.sgSetHint(null,4)"); pg.wait_for_timeout(400)
    ok(pg.evaluate("peekSecs()") == 2, 'Peek length starts at 2 seconds')
    L1, L2 = '.sgsec >> nth=1 >> .sgl >> nth=0', '.sgsec >> nth=1 >> .sgl >> nth=1'
    pg.click(L1); pg.wait_for_timeout(500)
    ok(pg.evaluate("getComputedStyle(document.querySelector('.sgl.peeking .hx'),'::after').opacity") == '0', 'peeking fades the pills out')
    pg.click(L2); pg.wait_for_timeout(300)
    ok(pg.locator('.sgsec >> nth=1 >> .sgl.peeking').count() == 1 and 'peeking' in pg.locator(L2).get_attribute('class'),
       'only the tapped line shows')
    pg.wait_for_timeout(1000); pg.click(L2); pg.wait_for_timeout(1300)
    ok(pg.locator('.sgl.peeking').count() == 1, 'tapping again mid-peek starts its time again')
    pg.wait_for_timeout(1000)
    ok(pg.locator('.sgl.peeking').count() == 0, 'then it hides after the peek length')

    # hold to keep showing
    bb = pg.locator(L1).bounding_box()
    pg.mouse.move(bb['x'] + 20, bb['y'] + bb['height'] / 2); pg.mouse.down(); pg.wait_for_timeout(700)
    ok('peeking' in pg.locator(L1).get_attribute('class'), 'holding a line shows it')
    pg.wait_for_timeout(2600)
    ok('peeking' in pg.locator(L1).get_attribute('class'), 'it keeps showing past the peek length while held')
    pg.mouse.up(); pg.wait_for_timeout(300)
    ok(pg.locator('.sgl.peeking').count() == 0, 'letting go hides it again')
    ok(pg.evaluate("U.sSec") is None, 'holding doesn’t select the section')

    # Settings › Recall › Peek length
    pg.evaluate("U.sMode='practise';U.view=null;U.tab='settings';render();scrollTo(0,0)"); pg.wait_for_timeout(300)
    seg = pg.locator('[aria-label="Peek length"]')
    ok(seg.count() == 1 and [x.strip() for x in seg.locator('button').all_inner_texts()] == ['1 s', '2 s', '3 s', '5 s']
       and seg.locator('button.on').inner_text().strip() == '2 s', 'Settings › Recall › Peek length offers 1, 2, 3 and 5 s, set to 2 s')
    t.shot(pg, 'settings-recall')
    seg.locator('[data-v="1"]').click(); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.prefs.peek") == 1, 'choosing 1 s saves it')
    pg.reload(); ready(pg)
    pg.evaluate("U.tab='settings';render()"); pg.wait_for_timeout(200)
    ok(pg.evaluate("peekSecs()") == 1 and pg.locator('[aria-label="Peek length"] button.on').inner_text().strip() == '1 s', 'it’s kept after a reload')
    pg.evaluate("U.tab='songs';render()"); pg.wait_for_timeout(200)
    pg.evaluate("id=>openSong(id)", sid); pg.wait_for_timeout(300)
    pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(400); pg.evaluate("SG_ACT.sgSetHint(null,4)"); pg.wait_for_timeout(300)
    pg.click(L1); pg.wait_for_timeout(600)
    ok(pg.locator('.sgl.peeking').count() == 1, 'a peek shows the line')
    pg.wait_for_timeout(700)
    ok(pg.locator('.sgl.peeking').count() == 0, 'and hides after 1 s')

    # backups carry it; older backups get the default
    pg.evaluate("U.sMode='practise';U.view=null;U.tab='settings';render();scrollTo(0,0)"); pg.wait_for_timeout(200)
    pg.locator('[aria-label="Peek length"] [data-v="5"]').click(); pg.wait_for_timeout(200)
    pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    with pg.expect_download(timeout=5000) as dl: pg.click('[data-a=exportSave]')
    path = os.path.join(OUT, 'fixes-backup.json'); dl.value.save_as(path)
    ok(json.load(open(path, encoding='utf-8'))['data'].get('prefs', {}).get('peek') == 5, 'the backup includes Peek length')
    pg.evaluate("D.prefs={peek:3};save()"); pg.reload(); ready(pg)
    pg.evaluate("U.tab='settings';render()"); pg.wait_for_timeout(300)
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(path); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("peekSecs()") == 5, 'restoring it brings Peek length back')
    pg.evaluate("U.tab='settings';U.view=null;render()"); pg.wait_for_timeout(300)  # restoring returns to Today
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(fix('backup-3.6.json')); pg.wait_for_function("U.sheet==='bkReport'", timeout=10000); pg.wait_for_timeout(200)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("peekSecs()") == 2, 'an older backup without it gets the 2 s default')
    ok(pg.evaluate("cleanData({prefs:{peek:7}}).prefs.peek") is None and pg.evaluate("cleanData({prefs:'x'}).prefs") == {},
       'a damaged Peek length is dropped')
    pg.context.close()


def run(b, t):
    sheets(b, t)
    song_practice(b, t)
    goal(b, t)
    recall(b, t)
