"""3.22 Search (Q01): the search circle beside the tab bar on every main tab (iPad: the end of the top capsule; Mac: a
row at the top of the sidebar), and the search page: recent searches and pinned songs before typing, then Songs,
Lyrics, Exercises, Sessions and Takes, grouped, with "Show all", updated in place as you type, and every result
opening the right place (and Back returning to the results)."""
import os, datetime as dt
from harness import with_song_practice, iso, now
from test_songs import LYR, ADD
from test_batch12 import wav_take

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required']
TODAY = "go(()=>{U.tab='today';U.view=null})"
OPEN = "FIND.open()"
GROUPS = "[...document.querySelectorAll('#flist [data-fg]')].map(g=>g.dataset.fg)"
ROWS = "g=>[...document.querySelectorAll('#flist [data-fg=\"'+g+'\"] .frow')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())"
# what's on screen overlapping: two rectangles
HIT = """([a,b])=>{const x=document.querySelector(a),y=document.querySelector(b);if(!x||!y)return null;const r=x.getBoundingClientRect(),s=y.getBoundingClientRect();
 return !(r.right<=s.left||s.right<=r.left||r.bottom<=s.top||s.bottom<=r.top)}"""


def data():
    d = with_song_practice()
    d['songSessions'][0]['how'] = ['Warm', 'Free']
    d['sessions'][1]['howNote'] = 'breath felt shorter than usual'
    d['sessions'][2]['xn'] = {'rung': {'w': ['Jaw open'], 't': 'jaw tight at the top'}}
    return d


def seed(pg):
    """Two songs with lyrics (River Song pinned), and two takes on River Song: one renamed, one with a comment."""
    pg.evaluate(ADD, ['River Song', 'Sam Example', LYR]); pg.wait_for_timeout(200)
    pg.evaluate(ADD, ['Kitchen Radio', '', 'Verse\nTurn the dial and sing along\nHumming on the counter top']); pg.wait_for_timeout(200)
    rid = pg.evaluate("D.songs.find(s=>s.name==='River Song').id")
    pg.evaluate("id=>{songById(id).pinned=true;save()}", rid)
    pg.evaluate(wav_take(6), ['ka', rid, None, 30])
    pg.evaluate(wav_take(6), ['kb', rid, None, 10])
    pg.evaluate("id=>{songById(id).takeNotes={ka:{name:'Harbour runs'},kb:{comments:[{t:2.5,text:'pitchy on the bridge'}]}};save()}", rid)
    pg.evaluate(TODAY); pg.wait_for_timeout(200)
    return rid


def typed(pg, q):
    pg.fill('#fq', q); pg.wait_for_timeout(120)


def circle(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=844, data=data())
    seed(pg)
    for tab in ('today', 'history', 'songs', 'exercises', 'settings'):
        pg.evaluate("v=>go(()=>{U.tab=v;U.view=null})", tab); pg.wait_for_timeout(150)
        c = pg.locator('#dock .scirc[data-a=findOpen]')
        ok(c.count() == 1 and c.get_attribute('aria-label') == 'Search', f'{tab}: the search circle sits in the dock')
        lay = pg.evaluate("(()=>{const b=document.querySelector('#dock .tabbar').getBoundingClientRect(),c=document.querySelector('#dock .scirc').getBoundingClientRect();return {gap:c.left-b.right,mid:Math.abs((c.top+c.bottom)/2-(b.top+b.bottom)/2),h:c.height}})()")
        ok(0 <= lay['gap'] <= 12 and lay['mid'] < 1.5 and lay['h'] >= 44, f'{tab}: beside the tab bar, centred on it ({lay})')
        ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{tab}: nothing scrolls sideways')
    # a pushed page keeps the tab bar, so it keeps the circle too
    pg.evaluate("go(()=>{U.tab='exercises';U.view='ex';U.exId='rung';U.prevTab='exercises'})"); pg.wait_for_timeout(150)
    ok(pg.locator('#dock .scirc').count() == 1, 'an exercise page keeps the circle')
    # the tab bar shrinking on scroll: the circle stays beside the shrunk circle
    pg.evaluate(TODAY); pg.wait_for_timeout(150)
    pg.evaluate("tabMin=true;scrollTo(0,400);renderDock()"); pg.wait_for_timeout(500)
    if pg.locator('#dock .tabbar.min').count():
        g = pg.evaluate("(()=>{const b=document.querySelector('#dock .tabbar').getBoundingClientRect(),c=document.querySelector('#dock .scirc').getBoundingClientRect();return c.left-b.right})()")
        ok(0 <= g <= 12, f'with the tab bar shrunk, the circle stays beside it (gap {g:.1f})')
    else:
        ok(False, 'the tab bar shrinks when asked (to check the circle beside it)')
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(200)
    # opening
    pg.click('#dock .scirc'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.tab") == 'find' and pg.evaluate("U.view") is None, 'tapping the circle opens Search')
    ok(pg.evaluate("document.activeElement.id") == 'fq', 'with its field focused')
    ok(pg.locator('#dock .scirc.on').count() == 1 and pg.locator('#dock .tabbar button.on').count() == 0
       and pg.evaluate("document.querySelector('#dock .scirc').getAttribute('aria-current')") == 'page',
       'the circle is tinted as selected, and no tab is')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#dock .scirc')).color") != pg.evaluate("getComputedStyle(document.querySelector('#dock .tabbar button')).color"),
       'its icon takes the accent colour')
    pg.evaluate("scrollTo(0,600)"); pg.wait_for_timeout(300)
    ok(pg.locator('#dock .tabbar.min').count() == 0, 'on Search the tab bar never shrinks (it has no tab of its own to shrink to)')
    pg.evaluate("scrollTo(0,0)")
    t.shot(pg, 'empty')
    # a tab takes you away; the circle brings you back with what you typed
    typed(pg, 'river')
    pg.click('#dock .tabbar [data-v=exercises]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'exercises', 'a tab leaves Search')
    pg.click('#dock .scirc'); pg.wait_for_timeout(250)
    ok(pg.input_value('#fq') == 'river' and 'River Song' in pg.inner_text('#flist'), 'and the circle comes back to the same search')
    # Cmd/Ctrl+F
    pg.evaluate(TODAY); pg.wait_for_timeout(200)
    pg.evaluate("document.activeElement&&document.activeElement.blur()"); pg.keyboard.press('Control+f'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'find' and pg.evaluate("document.activeElement.id") == 'fq', 'Cmd/Ctrl+F opens Search')
    # the Songs list keeps its own filter
    pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); pg.wait_for_timeout(200)
    pg.click('#app .sgqbtn'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sFocus") and pg.evaluate("document.activeElement.id") == 'sgqb', 'the Songs list’s own search field still filters the list')
    pg.evaluate("endSearch()"); pg.wait_for_timeout(150)
    pg.context.close()


def groups(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=844, data=data())
    seed(pg)
    pg.evaluate(OPEN); pg.wait_for_timeout(250)
    typed(pg, 'river')
    ok(pg.evaluate(GROUPS)[:1] == ['songs'] and any(r.startswith('River Song') for r in pg.evaluate(ROWS, 'songs')), 'Songs: by title')
    typed(pg, 'sam example')
    ok(any('River Song' in r and 'Sam Example' in r for r in pg.evaluate(ROWS, 'songs')), 'Songs: by artist')
    typed(pg, 'elmwood')
    ly = pg.evaluate(ROWS, 'lyrics')
    ok(ly and 'Racing rain down Elmwood Lane' in ly[0] and 'River Song · Verse 1' in ly[0], f'Lyrics: the line, then “Song · Section” ({ly})')
    ok(pg.locator('#flist [data-fg=lyrics] mark.sgmk').count() >= 1, 'with the match highlighted')
    typed(pg, 'elmwod')
    ok(any('Elmwood' in r for r in pg.evaluate(ROWS, 'lyrics')), 'a small typo still finds it (the Songs list’s forgiving matching)')
    typed(pg, 'ELMWOOD lane')
    ok(any('Elmwood' in r for r in pg.evaluate(ROWS, 'lyrics')), 'case and word order don’t matter')
    typed(pg, 'humming')
    g = pg.evaluate(GROUPS)
    ok(any(r.startswith('Humming') for r in pg.evaluate(ROWS, 'exercises')), 'Exercises: by name')
    ok('lyrics' in g and g.index('lyrics') < g.index('exercises'), f'groups keep their order: Songs, Lyrics, Exercises, Sessions, Takes ({g})')
    typed(pg, 'motorboat')
    ex = pg.evaluate(ROWS, 'exercises')
    ok(ex and ex[0].startswith('Lip bubbling') and 'About ·' in ex[0] and 'motorboat' in ex[0], f'Exercises: by their write-up, saying which part matched ({ex})')
    typed(pg, 'shorter than usual')
    se = pg.evaluate(ROWS, 'sessions')
    ok(len(se) == 1 and 'breath felt shorter' in se[0], f'Sessions: by their note ({se})')
    typed(pg, 'jaw tight')
    se = pg.evaluate(ROWS, 'sessions')
    ok(len(se) == 1 and 'Singing on the rung: Jaw open' in se[0], f'Sessions: by an exercise’s note, naming the exercise ({se})')
    typed(pg, 'free')
    se = pg.evaluate(ROWS, 'sessions')
    ok(len(se) == 1 and 'Song practice' in se[0], f'Sessions: by a feedback word, song practice included ({se})')
    typed(pg, 'harbour runs')
    tk = pg.evaluate(ROWS, 'takes')
    ok(len(tk) == 1 and tk[0].startswith('Harbour runs') and 'River Song · Take 1 · ' in tk[0], f'Takes: a renamed take, then “Song · Take n · when” ({tk})')
    typed(pg, 'pitchy')
    tk = pg.evaluate(ROWS, 'takes')
    ok(len(tk) == 1 and 'pitchy on the bridge' in tk[0] and '· 0:02' in tk[0], f'Takes: a comment, with its time ({tk})')
    typed(pg, 'zzqxv')
    ok('No results for “zzqxv”' in pg.inner_text('#flist'), 'no results says so')
    typed(pg, '   ')
    ok(pg.locator('#flist [data-fg]').count() == 0, 'spaces alone search nothing')
    # Show all expands in place
    typed(pg, 'the')
    rows = pg.evaluate("FIND.find('the')")
    n = rows['lyrics']
    ok(n > 4, f'“the” finds several lyric lines ({n})')
    ok(pg.locator('#flist [data-fg=lyrics] .frow').count() == 3 and f'Show all {n}' in pg.inner_text('#flist [data-fg=lyrics] .fmore'), 'a group shows its top three, then “Show all n”')
    pg.click('#flist [data-fg=lyrics] .fmore'); pg.wait_for_timeout(150)
    ok(pg.locator('#flist [data-fg=lyrics] .frow').count() == n and pg.locator('#flist [data-fg=lyrics] .fmore').count() == 0 and pg.evaluate("U.tab") == 'find',
       'Show all expands it in place')
    t.shot(pg, 'results')
    # typing keeps the same field (and keyboard), only the results redraw
    pg.fill('#fq', ''); pg.click('#fq')
    pg.evaluate("document.getElementById('fq').__keep=1")
    pg.keyboard.type('kitch', delay=30); pg.wait_for_timeout(100)
    ok(pg.evaluate("document.getElementById('fq').__keep===1&&document.activeElement.id==='fq'"), 'typing redraws only the results, so the keyboard stays up')
    ok(any(r.startswith('Kitchen Radio') for r in pg.evaluate(ROWS, 'songs')), 'and results follow each letter')
    ok(pg.locator('#flist [data-fg=lyrics] .fmore').count() == 0 and pg.evaluate("U.fAll") == [], 'a new search starts with its groups closed again')
    pg.context.close()


def recents(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=844, data=data())
    seed(pg)
    pg.evaluate(OPEN); pg.wait_for_timeout(250)
    ok('pinned songs' in pg.inner_text('#flist').lower() and pg.locator('#flist .frow[data-k]').count() == 1, 'before typing: pinned songs')
    typed(pg, 'elmwood'); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
    ok(pg.evaluate("document.activeElement.id") != 'fq', 'Enter puts the keyboard away')
    typed(pg, 'humming'); pg.click('#flist [data-fg=exercises] .frow >> nth=0'); pg.wait_for_timeout(300)
    pg.click('#barL [data-a=exBack]'); pg.wait_for_timeout(300)
    typed(pg, '')
    rc = pg.evaluate("[...document.querySelectorAll('#flist .recent .rtxt2')].map(r=>r.innerText.trim())")
    ok(rc == ['humming', 'elmwood'], f'Enter and tapping a result both save the search, newest first ({rc})')
    ok('findRecent' in pg.evaluate("localStorage.getItem('vocalSongPrefs')") and 'findRecent' not in pg.evaluate("localStorage.getItem('vocalTracker')"),
       'recent searches stay on this device (not in the saved data that backups carry)')
    pg.click('#flist [data-a=findRecent][data-v=elmwood]'); pg.wait_for_timeout(150)
    ok(pg.input_value('#fq') == 'elmwood' and any('Elmwood' in r for r in pg.evaluate(ROWS, 'lyrics')), 'tapping a recent search runs it')
    typed(pg, '')
    pg.click('#flist [data-a=findRmRecent][data-v=elmwood]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("FIND.recents()") == ['humming'], 'the ✕ removes one')
    pg.click('#flist [data-a=findClearRecent]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("FIND.recents()") == [] and pg.locator('#flist .recent').count() == 0, 'Clear removes them all')
    pg.evaluate("D.songs.forEach(s=>s.pinned=false);save();rerender()"); pg.wait_for_timeout(150)
    ok('Search your songs, lyrics, exercises and sessions.' in pg.inner_text('#flist'), 'with nothing to show yet, a line says what it searches')
    # Cancel and Escape
    pg.click('#fq'); typed(pg, 'river')
    ok(pg.locator('.fbar .scancel').is_visible(), 'Cancel shows while searching')
    pg.click('.fbar .scancel'); pg.wait_for_timeout(150)
    ok(pg.input_value('#fq') == '' and pg.evaluate("document.activeElement.id") != 'fq' and pg.evaluate("U.tab") == 'find',
       'Cancel clears the search and puts the keyboard away')
    pg.click('#fq'); typed(pg, 'river'); pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    ok(pg.input_value('#fq') == '', 'Escape clears it too')
    pg.reload(); from harness import ready; ready(pg)
    ok(pg.evaluate("FIND.recents()") == [], 'still cleared after a reload')
    pg.context.close()


def opening(b, t):
    ok = t.ok
    pg = t.page(b, w=390, h=844, touch=True, data=data())
    rid = seed(pg)
    pg.evaluate(OPEN); pg.wait_for_timeout(250)
    # a song zooms into its page; Back returns to the same results
    typed(pg, 'river')
    pg.evaluate("document.activeElement.blur()")
    pg.click('#flist [data-fg=songs] .frow >> nth=0'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.songId") == rid and pg.evaluate("U.sMode") == 'practise', 'a song opens its page')
    ok(pg.evaluate("ZOOM.stack().length") == 1 and pg.evaluate("ZOOM.stack()[0].key") == 'sg:' + rid, 'zooming from its row')
    pg.click('#barL [data-a=sgBack]'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.tab") == 'find' and pg.input_value('#fq') == 'river' and pg.evaluate("ZOOM.stack().length") == 0,
       'Back returns to the same results (shrinking into the row)')
    ok(pg.evaluate("document.activeElement.id") != 'fq', 'without opening the keyboard again')
    # a lyric: the song in Practise, scrolled to the section, with it focused
    typed(pg, 'never made for standing')
    pg.evaluate("document.activeElement.blur()")
    o = pg.evaluate("document.querySelector('#flist [data-fg=lyrics] .frow').dataset.o")
    sec = pg.evaluate(ROWS, 'lyrics')[0]
    pg.click('#flist [data-fg=lyrics] .frow >> nth=0'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.sSec") == o and pg.locator(f'.sgsec.sel[data-o="{o}"]').count() == 1,
       f'a lyric opens its song with its section focused ({sec})')
    pos = pg.evaluate("o=>{const s=document.querySelector('.sgsec[data-o=\"'+o+'\"]').getBoundingClientRect(),b=document.getElementById('bar').getBoundingClientRect();return {y:scrollY,top:s.top,bar:b.bottom,max:document.documentElement.scrollHeight-innerHeight}}", o)
    ok(pos['y'] > 100 and (pos['bar'] - 2 <= pos['top'] <= pos['bar'] + 40 or (pos['y'] >= pos['max'] - 2 and pos['top'] < 844 * 0.5)),
       f'scrolled to that section, just under the top bar (or as far as the page goes) ({pos})')
    t.shot(pg, 'lyric')
    pg.click('#barL [data-a=sgBack]'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.tab") == 'find', 'Back returns to Search')
    # an exercise zooms into its page
    typed(pg, 'motorboat'); pg.evaluate("document.activeElement.blur()")
    pg.click('#flist [data-fg=exercises] .frow >> nth=0'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.view") == 'ex' and pg.evaluate("U.exId") == 'lip' and pg.evaluate("ZOOM.stack()[0].key") == 'ex:lip', 'an exercise zooms into its page')
    pg.click('#barL [data-a=exBack]'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.tab") == 'find' and pg.input_value('#fq') == 'motorboat', 'Back returns to Search')
    # a session opens its details sheet over the results
    typed(pg, 'jaw tight'); pg.evaluate("document.activeElement.blur()")
    pg.click('#flist [data-fg=sessions] .frow >> nth=0'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.sheet") == 'session' and pg.evaluate("U.sd.k") == 's2' and pg.locator('#layer .sheet').count() == 1, 'a session opens its details sheet')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.tab") == 'find' and pg.locator('#flist [data-fg=sessions] .frow').count() == 1, 'closing it leaves the results')
    typed(pg, 'free'); pg.evaluate("document.activeElement.blur()")
    pg.click('#flist [data-fg=sessions] .frow >> nth=0'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.sheet") == 'songSession', 'song practice opens its own sheet')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(300)
    # a take: its song, the takes sheet on All takes, that take expanded (not playing)
    typed(pg, 'harbour runs'); pg.evaluate("document.activeElement.blur()")
    pg.click('#flist [data-fg=takes] .frow >> nth=0'); pg.wait_for_timeout(450)
    st = pg.evaluate("TAKE.state()")
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.songId") == rid and pg.evaluate("U.sheet") == 'sgTakes' and pg.evaluate("U.sd.all") is True
       and st['open'] == 'ka' and st['tab'] == 'all', f'a take opens its song with the takes sheet on All takes, that take expanded ({st})')
    ok(pg.locator('#layer .tkr.open').count() == 1 and pg.locator('#layer .tkseg').count() == 0 and pg.evaluate("playingId") is None, 'expanded, and not playing yet')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(300)
    pg.click('#barL [data-a=sgBack]'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.tab") == 'find', 'and the song’s Back returns to Search')
    # a comment: also the playhead at its time, with the comment showing
    typed(pg, 'pitchy'); pg.evaluate("document.activeElement.blur()")
    pg.click('#flist [data-fg=takes] .frow >> nth=0'); pg.wait_for_timeout(450)
    st = pg.evaluate("TAKE.state()")
    ok(st['open'] == 'kb' and abs(pg.evaluate("TAKE.now('kb')") - 2.5) < 0.06, f'a comment opens its take with the playhead at its time ({pg.evaluate("TAKE.now(\'kb\')")})')
    ok('pitchy on the bridge' in st['pop'] and 'pitchy on the bridge' in pg.inner_text('#tkPop'), 'with the comment showing')
    t.shot(pg, 'comment')
    pg.click('#layer [data-a=tkPlay]'); pg.wait_for_function("!!player&&!player.paused", timeout=5000); pg.wait_for_timeout(200)
    ok(pg.evaluate("playingId") == 'kb' and pg.evaluate("player.currentTime") >= 2.4, 'and Play starts from there')
    pg.evaluate("stopPlayback()")
    pg.context.close()


def wide(b, t):
    ok = t.ok
    for name, w, h in (('ipad', 820, 1180), ('mac', 1440, 900)):
        pg = t.page(b, w=w, h=h, ua=None, data=data())
        rid = seed(pg)
        if name == 'ipad':
            c = pg.locator('#barT .toptabs .tsr[data-a=findOpen]')
            ok(c.count() == 1, 'iPad: a search circle at the end of the top capsule')
            ok(pg.evaluate("(()=>{const n=document.querySelector('#barT .toptabs'),c=n.querySelector('.tsr');return n.lastElementChild===c&&c.getBoundingClientRect().width>=34})()"),
               'iPad: last in the capsule, a full-size circle')
        else:
            c = pg.locator('#side .sbi[data-a=findOpen]')
            ok(c.count() == 1 and pg.evaluate("document.querySelector('#side .sbi')===document.querySelector('#side [data-a=findOpen]')"),
               'Mac: a Search row at the top of the sidebar')
        c.click(); pg.wait_for_timeout(300)
        ok(pg.evaluate("U.tab") == 'find' and pg.evaluate("document.activeElement.id") == 'fq', f'{name}: it opens Search with the field focused')
        sel = '#barT .toptabs .tsr.on' if name == 'ipad' else '#side .sbi.on[data-a=findOpen]'
        ok(pg.locator(sel).count() == 1, f'{name}: shown as selected')
        typed(pg, 'river')
        pg.click('#flist [data-fg=songs] .frow >> nth=0'); pg.wait_for_timeout(350)
        ok(pg.evaluate("U.tab") == 'songs' and pg.evaluate("U.songId") == rid, f'{name}: a song opens beside the Songs list')
        pg.click('#side [data-a=findOpen]' if name == 'mac' else '#barT .toptabs .tsr'); pg.wait_for_timeout(300)
        ok(pg.input_value('#fq') == 'river', f'{name}: Search keeps what was typed')
        typed(pg, 'elmwood')
        pg.click('#flist [data-fg=lyrics] .frow >> nth=0'); pg.wait_for_timeout(400)
        o = pg.evaluate("U.sSec")
        ok(pg.evaluate("U.tab") == 'songs' and o and pg.locator(f'.sgpane .sgsec.sel[data-o="{o}"]').count() == 1, f'{name}: a lyric opens with its section focused')
        pg.context.close()


def window_clear(b, t):
    """The floating window (a session running) never covers the circle, in any corner."""
    ok = t.ok
    for w, h in ((375, 667), (390, 844), (852, 393)):
        pg = t.page(b, w=w, h=h, touch=True, data=data())
        pg.evaluate("newSession();X.start=Date.now()-6e4;saveDraft();go(()=>{U.view=null;U.tab='today'})"); pg.wait_for_timeout(400)
        bad = []
        for tab in ('today', 'find'):
            pg.evaluate("v=>go(()=>{U.tab=v;U.view=null})", tab); pg.wait_for_timeout(300)
            pg.evaluate("document.activeElement&&document.activeElement.blur&&document.activeElement.blur()"); pg.wait_for_timeout(150)
            for c in ('br', 'bl', 'tr', 'tl'):
                pg.evaluate("c=>{FW.corner=c;fwUpdate();const p=fwCornerXY(c);FW.el.style.transform='translate('+p.x+'px,'+p.y+'px)'}", c); pg.wait_for_timeout(120)
                if not pg.evaluate("FW.shown"): bad.append(f'{tab} {c}: no window'); continue
                if pg.evaluate(HIT, ['#fw', '#dock .scirc']): bad.append(f'{tab} {c}')
        ok(not bad, f'{w}x{h}: the floating window never covers the circle ({bad})')
        pg.context.close()


SIZES = [('375', 375, 667, True), ('390', 390, 844, True), ('land', 852, 393, True), ('ipad', 820, 1180, True), ('mac', 1440, 900, False)]


def sizes(b, t):
    ok = t.ok
    for name, w, h, touch in SIZES:
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, touch=touch, ua=None if name in ('ipad', 'mac') else __import__('harness').UA_IPHONE, data=data())
            seed(pg)
            pg.evaluate(OPEN); pg.wait_for_timeout(250)
            ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{name} {sc}: the empty page fits')
            typed(pg, 'carry')
            pg.evaluate("document.activeElement.blur()"); pg.wait_for_timeout(150)
            ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{name} {sc}: results fit, nothing sideways')
            ok(pg.evaluate("[...document.querySelectorAll('#flist .frow')].every(r=>r.getBoundingClientRect().right<=innerWidth+0.5)"), f'{name} {sc}: every row inside the screen')
            if name in ('375', '390', 'land'):
                ok(pg.evaluate("(()=>{const c=document.querySelector('#dock .scirc').getBoundingClientRect();return c.left>=0&&c.right<=innerWidth&&c.bottom<=innerHeight})()"),
                   f'{name} {sc}: the circle is on screen')
                # scrolled to the bottom, the last result clears the tab bar and the circle
                pg.evaluate("scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(250)
                ok(pg.evaluate("(()=>{const r=[...document.querySelectorAll('#flist .frow')].pop().getBoundingClientRect(),d=document.querySelector('#dock').firstElementChild.getBoundingClientRect();return r.bottom<=d.top+1})()"),
                   f'{name} {sc}: scrolled to the bottom, the last result clears the dock')
                pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(150)
            t.shot(pg, f'{name}-{sc}')
            # Songs: the rows' play buttons never end up under the dock at the bottom of the list
            if name in ('375', '390'):
                for i in range(8):
                    pg.evaluate(ADD, [f'Song {i}', '', 'Verse\nLine one\nLine two'])
                pg.evaluate("go(()=>{U.tab='songs';U.view=null})"); pg.wait_for_timeout(250)
                pg.evaluate("scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(250)
                ok(pg.evaluate("(()=>{const p=[...document.querySelectorAll('#slist .sgplay')].pop().getBoundingClientRect(),d=document.querySelector('#dock').firstElementChild.getBoundingClientRect();return p.bottom<=d.top+1})()"),
                   f'{name} {sc}: on Songs, the last row’s play button clears the tab bar and circle')
                t.shot(pg, f'songs-{name}-{sc}')
            pg.context.close()


PARTS = ['circle', 'groups', 'recents', 'opening', 'wide', 'window_clear', 'sizes']


def run(b, t):
    import traceback
    only = os.environ.get('VS_SEARCH')
    for n in (only.split(',') if only else PARTS):
        try:
            globals()[n](b, t)
        except Exception as ex:
            tb = traceback.extract_tb(ex.__traceback__)
            line = next((f.lineno for f in reversed(tb) if f.filename.endswith('test_search.py')), '?')
            t.fails.append(f'{n} crashed at line {line}: ' + str(ex).split(chr(10))[0][:160])
            print(f'  FAIL  {n} crashed at line {line}: {ex}')
