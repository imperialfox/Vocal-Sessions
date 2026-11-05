"""Q47 · Songs: Sheet Music Guide and Views. The Sheet music page (VS-108): a song's score as dots or as the print's own
lines, the guide playing the vocal line, a loop in bars, the speed, and the starting note in one tap.

The prints are the made-up tunes from tools/make_melody_fixtures.py (tests/fixtures/melody/): no real music.
Parts (VS_MELPAGE=page,guide,taps,loop,sheet,screens):
- page: the Song page row opens VS-108 (and zooms from its card); the top bar's circle opens VS-099; Back returns to the
  Song page; the dots view has a line per few bars, bar numbers, flagged bars shaded, muted notes hollow, unsure marked;
  the bars stepper; a song with no score; the written line as 10 ms points (H35)
- guide: Play starts the guide under NOW kind 'melody' and its notes come from the pattern player's output (scheduled,
  muted notes silent); Pause keeps the place; leaving the page, hiding the app or another sound stops it (H2, H28);
  the speed steps along PAT's stops and is kept on this device (H12)
- taps: a bar plays from there; a dot sounds its note when stopped and jumps while playing (H15); give me my note when
  stopped (PAT.tone) and while playing (the guide's own bus, nothing stops)
- loop: Loop on the line, the guide wrapping inside it, Change by tapping two bars, off and on again, saved on the score
  (H14) and never on the track player's sg.loop
- sheet: the print's lines cut again from the kept print (decision 22), a button per bar on its line, the playhead on the
  bar, the fallback on the page when pdf.js won't load in the Worker, Print not on this device, only lines near the
  screen decoded (H47)
- screens: VS-108 at 375 px and on iPad, light and dark, with Reduce Motion; the transport in the dock"""
import os
from harness import ready, until, OUT
from test_melody import read_save, fresh

PARTS = set((os.environ.get('VS_MELPAGE') or 'page,guide,taps,loop,sheet,screens').split(','))
SONG = "go(()=>{U.tab='songs';U.view='lyr';U.songId='g_1';U.sheet=null})"
OPEN = "SG_ACT.melOpen(null,null,'g_1')"
# a made-up score with no print: 8 bars of 4/4, two notes a beat, one muted and one unsure
SCORE = """async()=>{const n=[];for(let b=0;b<8;b++)for(let k=0;k<8;k++)n.push({tick:b*1920+k*240,len:240,midi:60+((b+k)%7)});
  n[3].flag='jump';n[5].flag='unsure';
  const bars=[];for(let b=0;b<8;b++)bars.push({tick:b*1920,len:1920,n:b+1,ln:Math.floor(b/4),x0:100+(b%4)*500,x1:600+(b%4)*500});
  bars[6].f=['numbers'];
  await MELODY._put('g_1',{v:1,rev:1,at:5,tempo:120,time:[4,4],key:0,octave:0,shift:0,bars,notes:n,rests:[],anchors:[],loop:null,ug:{id:'77'}},0);
  const sg=songById('g_1');sg.ext=Object.assign({},sg.ext,{melody:{ug:'77',at:5}});save();await MELODY._reloadAll();rerender()}"""
# count the notes the guide sends to the pattern player's output
SPY = """(()=>{window.__notes=[];const g=PAT.guide,o=g.note;g.note=function(m,t,d,b,v){window.__notes.push({m,t,d});return o.apply(this,arguments)}})()"""
TONES = """(()=>{window.__tones=[];const o=PAT.tone;PAT.tone=function(m){window.__tones.push(m);return o.apply(this,arguments)}})()"""
ST = 'MELPLAY.state()'


def page_with_score(t, b, **kw):
    pg = fresh(t, b, **kw)
    pg.evaluate(SCORE)
    pg.evaluate(SONG)
    return pg


def run(b, t):
    if 'page' in PARTS:
        pg = page_with_score(t, b)
        row = pg.locator('#app [data-a="melOpen"]')
        t.ok(row.count() == 1 and row.get_attribute('data-zk') == 'mel:g_1', 'the Song page row opens the Sheet music page and zooms from its card')
        row.click()
        t.ok(until(pg, "U.view==='mel'&&document.querySelector('#app').dataset.screen==='VS-108'"), 'VS-108 opens from the row')
        t.ok(pg.evaluate("document.querySelector('.mpsub').textContent").startswith('Sheet music'), 'the page says Sheet music under the song\'s title')
        n = pg.evaluate("document.querySelectorAll('#mpBody .mpln').length")
        t.ok(n == 4, 'the dots view draws a line every 2 bars on an iPhone (8 bars, 4 lines): %s' % n)
        t.ok(pg.evaluate("[...document.querySelectorAll('.mpln:first-child .pt')].map(x=>x.textContent).join(',')") == '1,2', 'each line is labelled with its bar numbers')
        t.ok(pg.evaluate("document.querySelectorAll('.mpbarbg.flag').length") >= 1, 'a flagged bar is shaded')
        t.ok(pg.evaluate("document.querySelectorAll('.mpn.muted').length") == 1, 'a muted note is drawn hollow')
        t.ok(pg.evaluate("document.querySelectorAll('.mpn.unsure').length") == 1, 'an unsure note is marked')
        t.ok(pg.evaluate("document.querySelectorAll('.mpn').length") == 64, 'every note is drawn')
        pg.click('[data-a="mpZoom"][data-v="1"]')
        t.ok(pg.evaluate("document.querySelectorAll('#mpBody .mpln').length") == 3 and pg.evaluate("sgp().melBars") == 3, 'More bars a line: 3 a line, kept on this device')
        pg.click('[data-a="mpZoom"][data-v="-1"]')
        pg.click('[data-a="melInfo"]')
        t.ok(until(pg, "U.sheet==='melSheet'&&document.querySelector('#layer [data-screen]')&&document.querySelector('#layer [data-screen]').dataset.screen==='VS-099'") or pg.evaluate("U.sheet") == 'melSheet', 'the top bar circle opens VS-099, the score\'s settings')
        pg.evaluate("U.sheet=null;U.sd={};rerender()")
        pts = pg.evaluate("(()=>{const s=MELODY.get('g_1');const p=MELODY.points(s,3840,5760);let gap=0;for(let i=1;i<p.length;i++)gap=Math.max(gap,p[i].t-p[i-1].t);return {n:p.length,gap}})()")
        t.ok(pts['gap'] <= 0.0101 and pts['n'] > 180, 'the written line is a point every 10 ms inside notes, with no gaps between joined notes (H35): %s' % pts)
        pg.click('[data-a="mpBack"]')
        t.ok(until(pg, "U.view==='lyr'"), 'Back returns to the Song page')
        pg.evaluate("go(()=>{U.tab='songs';U.view='mel';U.songId='g_2';U.sheet=null})")
        t.ok(until(pg, "U.view==='mel'") and 'not on this device' in pg.inner_text('#app'), 'a song with no score shows Sheet not on this device')
        pg.close()

    if 'guide' in PARTS:
        pg = page_with_score(t, b)
        pg.evaluate(OPEN)
        until(pg, "U.view==='mel'")
        pg.evaluate(SPY)
        pg.click('#mpPP')
        t.ok(until(pg, ST + ".on&&NOW.kind()==='melody'"), 'Play starts the guide under NOW kind melody')
        t.ok(until(pg, "window.__notes.length>=3", 3000), 'its notes go to the pattern player\'s output, scheduled ahead')
        t.ok(pg.evaluate("document.querySelector('#mpPP').dataset.on") == 'true', 'the play button turns to Pause in place')
        t.ok(until(pg, ST + ".tick>500", 3000), 'the playhead moves through the score')
        t.ok(pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#mpHead')).opacity)") == 1, 'the playhead shows on its line')
        until(pg, ST + ".tick>1000", 3000)
        gaps = pg.evaluate("(()=>{const a=window.__notes.map(x=>x.t);const t0=a[0];return a.map(x=>Math.round((x-t0)*100)/100).slice(0,7)})()")
        t.ok(0.75 not in gaps and 0.5 in gaps and 1.0 in gaps, 'a muted note stays silent (the 4th, a jump), the notes around it play: %s' % gaps)
        pg.click('#mpPP')
        t.ok(until(pg, "!" + ST + ".on") and pg.evaluate(ST + ".pos.g_1") > 0, 'Pause stops it and keeps the place')
        at = pg.evaluate(ST + ".pos.g_1")
        pg.click('#mpPP')
        t.ok(until(pg, ST + ".on") and pg.evaluate(ST + ".tick") >= at - 5, 'Play carries on from there')
        pg.evaluate("PAT.tone(60)")
        t.ok(until(pg, "!" + ST + ".on"), 'another sound starting stops the guide')
        pg.click('#mpPP')
        until(pg, ST + ".on")
        pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));Object.defineProperty(document,'hidden',{configurable:true,get:()=>false})")
        t.ok(until(pg, "!" + ST + ".on"), 'hiding the app stops the guide')
        pg.click('#mpPP')
        until(pg, ST + ".on")
        pg.click('[data-a="mpBack"]')
        t.ok(until(pg, "U.view==='lyr'&&!" + ST + ".on&&NOW.kind()!=='melody'"), 'leaving the page stops the guide (H28)')
        pg.evaluate(OPEN)
        until(pg, "U.view==='mel'")
        sp0 = pg.evaluate(ST + ".speed")
        pg.click('[data-a="mpSpd"][data-v="-1"]')
        pg.click('[data-a="mpSpd"][data-v="-1"]')
        t.ok(sp0 == 1 and pg.evaluate(ST + ".speed") == 0.8 and pg.inner_text('#mpSpdV') == '0.8×', 'Slower steps along the pattern player\'s stops: 1× to 0.8× (H12)')
        t.ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalSongPrefs')).melSpeed") == pg.evaluate("PAT.SPEEDS.indexOf(0.8)"), 'the speed is kept on this device')
        pg.click('#mpPP')
        until(pg, ST + ".on")
        t.ok(abs(pg.evaluate(ST + ".tps") - 480 * 2 * 0.8) < 0.01, 'the guide plays at 0.8× (ticks a second)')
        pg.click('[data-a="mpSpd"][data-v="1"]')
        t.ok(until(pg, "Math.abs(" + ST + ".tps-480*2*0.9)<0.01") and pg.evaluate(ST + ".on"), 'a new speed while playing carries on at it')
        pg.click('#mpPP')
        pg.close()

    if 'taps' in PARTS:
        pg = page_with_score(t, b)
        pg.evaluate(OPEN)
        until(pg, "U.view==='mel'")
        pg.evaluate(SPY + ';' + TONES)
        pg.evaluate("document.querySelector('.mpbarbg[data-v=\"2\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        t.ok(until(pg, ST + ".on") and pg.evaluate(ST + ".tick") >= 3840, 'tapping a bar plays from there (bar 3)')
        pg.evaluate("document.querySelector('[data-a=\"mpDot\"][data-v=\"40\"] .mphit').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        t.ok(until(pg, ST + ".on&&" + ST + ".tick>=9600&&" + ST + ".tick<11000") and pg.evaluate("window.__tones.length") == 0, 'a dot tapped while playing jumps there; nothing else sounds and it keeps playing (H15)')
        n0 = pg.evaluate("window.__notes.length")
        pg.click('[data-a="mpMy"]')
        t.ok(pg.evaluate(ST + ".on") and pg.evaluate("window.__notes.length") > n0 and pg.evaluate("window.__tones.length") == 0, 'Give me my note while playing sounds on the guide\'s own bus and nothing stops')
        pg.click('#mpPP')
        until(pg, "!" + ST + ".on")
        pg.evaluate("document.querySelector('[data-a=\"mpDot\"][data-v=\"9\"] .mphit').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        t.ok(pg.evaluate("window.__tones") == [pg.evaluate("MELODY.get('g_1').notes[9].midi")] and pg.evaluate(ST + ".pos.g_1") == 1920 + 240, 'a dot tapped when stopped sounds its note and moves the playhead there')
        pg.click('[data-a="mpMy"]')
        t.ok(len(pg.evaluate("window.__tones")) == 2 and pg.evaluate("window.__tones[1]") == pg.evaluate("MELODY.get('g_1').notes[9].midi"), 'Give me my note when stopped plays the next note from the playhead')
        pg.evaluate("document.querySelector('[data-a=\"mpDot\"][data-v=\"3\"] .mphit').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        t.ok(len(pg.evaluate("window.__tones")) == 2 and 'misread' in ' '.join(pg.evaluate("window.__toasts||[]")), 'a muted dot stays silent and says why')
        pg.close()

    if 'loop' in PARTS:
        pg = page_with_score(t, b)
        pg.evaluate("songById('g_1').loop=null;save()")
        pg.evaluate(OPEN)
        until(pg, "U.view==='mel'")
        pg.click('#mpLoopB')
        t.ok(until(pg, "(MELODY.get('g_1').loop||{}).on===true"), 'Loop turns on a loop')
        L = pg.evaluate("MELODY.get('g_1').loop")
        t.ok(L['from'] == 0 and L['to'] == 3840, 'over the line the playhead is on (bars 1–2): %s' % L)
        t.ok(until(pg, "document.querySelector('.mploop.on')&&document.querySelector('#mpLoopB.on')"), 'the strip says Looping and the button lights')
        t.ok(pg.evaluate("songById('g_1').loop") is None, 'the track player\'s loop is never touched (H14)')
        pg.evaluate("Object.assign(sgp(),{melSpeed:PAT.SPEEDS.length-1});saveSGP()")
        pg.click('#mpPP')
        until(pg, ST + ".on")
        t.ok(until(pg, "window.__wrapped=(window.__wrapped||0)+(" + ST + ".tick<500&&window.__lastT>3000?1:0),window.__lastT=" + ST + ".tick,window.__wrapped>0", 6000), 'the guide wraps back to the loop\'s start')
        t.ok(pg.evaluate(ST + ".tick") < 3840, 'and stays inside the loop')
        pg.click('#mpPP')
        pg.click('[data-a="mpPick"]')
        t.ok(until(pg, "document.querySelector('.mploop.picking')"), 'Change asks for the first bar')
        pg.evaluate("document.querySelector('.mpbarbg[data-v=\"4\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        t.ok(until(pg, "document.querySelector('.mpbarbg.picked')") and 'last bar' in pg.inner_text('.mploop'), 'then its last bar, with the first one marked')
        pg.evaluate("document.querySelector('.mpbarbg[data-v=\"6\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        t.ok(until(pg, "MELODY.get('g_1').loop.from===7680&&MELODY.get('g_1').loop.to===13440"), 'the loop is now bars 5–7, saved on the score')
        t.ok(until(pg, "document.querySelector('.mploop').textContent.includes('5–7')"), 'the strip names the bars')
        pg.click('#mpLoopB')
        t.ok(until(pg, "MELODY.get('g_1').loop.on===false&&document.querySelector('.mploop:not(.on)')"), 'Loop again turns it off, kept for next time')
        pg.click('#mpLoopB')
        t.ok(until(pg, "MELODY.get('g_1').loop.on===true&&MELODY.get('g_1').loop.from===7680"), 'and on again over the same bars')
        pg.evaluate("location.reload()")
        ready(pg)
        until(pg, "MELODY.loaded()")
        t.ok(pg.evaluate("MELODY.get('g_1').loop.from") == 7680, 'the loop is still there after a relaunch')
        pg.close()

    if 'sheet' in PARTS:
        pg = fresh(t, b)
        t.ok(read_save(pg, 'rain-on-the-ferry.pdf'), 'a print read onto the song')
        t.ok(pg.evaluate("MELODY.get('g_1').bars.every(b=>Number.isInteger(b.pi))"), 'each bar keeps the picture it\'s on (pi)')
        pg.evaluate(OPEN)
        until(pg, "U.view==='mel'")
        pg.click('[data-a="mpView"][data-v="sheet"]')
        t.ok(pg.evaluate("sgp().melView") == 'sheet', 'the view is kept on this device')
        t.ok(until(pg, ST + ".sheet.state==='ready'&&document.querySelectorAll('.mpsheet .mpimg').length>0", 20000), 'the sheet view cuts the print\'s lines again and shows them')
        nb = pg.evaluate("document.querySelectorAll('.mpsheet .mpbar').length")
        t.ok(nb == pg.evaluate("MELODY.get('g_1').bars.length"), 'a button per bar, on its line: %s' % nb)
        t.ok(until(pg, "[...document.querySelectorAll('.mpsheet img')].some(i=>i.getAttribute('src'))"), 'the lines on screen are decoded')
        pg.evaluate("document.querySelector('.mpbar[data-v=\"2\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        t.ok(until(pg, ST + ".on"), 'tapping a bar on the print plays from there')
        t.ok(until(pg, "parseFloat(document.querySelector('#mpHead').style.opacity)===1"), 'the playhead sits on the print')
        pg.click('#mpPP')
        # the fallback: pdf.js on the page
        pg.evaluate("MELODY._cutOpt({nopdf:true});SG_ACT.mpView(document.querySelector('[data-a=mpView][data-v=dots]'),'dots')")
        pg.evaluate("go(()=>{U.view='lyr'})")
        pg.evaluate("go(()=>{U.view='mel';U.songId='g_1'})")
        t.ok(pg.evaluate("MELODY.cut('g_1').then(l=>l&&l.length)") > 0, 'when pdf.js won\'t load in the Worker, the page cuts the lines itself')
        pg.evaluate("MELODY._cutOpt(null)")
        pg.evaluate("async()=>{await MELODY.removePrints()}")
        pg.evaluate("go(()=>{U.view='lyr'})")
        pg.evaluate("Object.assign(sgp(),{melView:'sheet'});saveSGP();go(()=>{U.view='mel';U.songId='g_1'})")
        t.ok(until(pg, "document.querySelector('#app').textContent.includes('Print not on this device')"), 'with the print removed: Print not on this device, and the dots still play')
        pg.close()

    if 'screens' in PARTS:
        for (w, h, sc, name) in [(375, 812, 'light', '375-light'), (375, 812, 'dark', '375-dark'), (820, 1180, 'light', 'ipad')]:
            pg = page_with_score(t, b, w=w, h=h, sc=sc)
            pg.evaluate(OPEN)
            until(pg, "U.view==='mel'")
            t.ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), 'VS-108 has no sideways scroll at %s' % name)
            t.ok(pg.locator('#dock .mptr').count() == 1, 'the transport is in the dock at %s' % name)
            bad = pg.evaluate("/\\b(undefined|NaN|null)\\b/.test(document.querySelector('#app').innerText)")
            t.ok(not bad, 'no undefined, NaN or null on screen at %s' % name)
            if name == 'ipad':
                t.ok(pg.evaluate("document.querySelectorAll('#mpBody .mpln').length") == 2, 'iPad shows 4 bars a line')
            t.shot(pg, 'melpage-' + name)
            pg.close()
        pg = page_with_score(t, b, w=375, h=812)
        pg.evaluate("document.documentElement.classList.add('motion-reduced')")
        pg.evaluate(OPEN)
        t.ok(until(pg, "U.view==='mel'"), 'VS-108 opens with Reduce Motion')
        pg.close()
