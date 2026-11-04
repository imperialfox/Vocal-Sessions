"""3.48 Exercises: Redesign (Q32): the shared pattern player (js/patterns.js) and the redesigned exercise pages.
The pattern library (60 patterns, the groups and families, minor patterns, quick touches and held notes), every
exercise's route copied from the coach video's note data, the range check against your voice (the falsetto top for the
falsetto exercises and the Flips), Stop at my top note, the drawing, playing (rounds moving up, Stay on this key, Speed
up each round, the home ending, one sound at a time, the screen kept awake, stopping when the page goes), the Patterns
page (the card zoom from the pattern pill and back, swipe back, Reduce Motion, groups, Favourites, picking, press and
hold for what a pattern trains, Back to default), the speed slider, Settings › Your voice and Pattern player, saved
choices surviving a reload and a backup round trip (and malformed ones dropped, unknown ones kept), the vowel cue, and
every exercise page at 375 px in light and dark, plus iPad.
VS_PAT=library,routes,range,drawing,playing,page,zoom,speed,settings,data,sizes runs only those parts."""
import json, os
from harness import sample, until, OUT
from test_window import drag
from test_backup import pick, write

HERE = os.path.dirname(os.path.abspath(__file__))
EX = "id=>go(()=>{U.tab='exercises';U.view='ex';U.exId=id;U.exTab='summary';U.exLv=null;U.prevTab='exercises'})"
LV = "([id,lv])=>go(()=>{U.tab='exercises';U.view='ex';U.exId=id;U.exTab='summary';U.exLv={id,lv};U.prevTab='exercises'})"
ST = "PAT.state()"
CLEAN = "!document.querySelector('.zm')&&!document.querySelector('.zm-src')&&!ZOOM.busy()"
QUIET = "!document.getAnimations().some(a=>(a.playState==='running'||a.playState==='pending')&&a.effect.getTiming().iterations!==Infinity)&&!ZOOM.busy()"
NOTE = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B']


def midi(s):
    n, o = s[:-1], int(s[-1])
    return 12 * (o + 1) + NOTE.index(n)


def library(b, t):
    ok = t.ok
    pg = t.page(b)
    L = pg.evaluate("PAT.LIB.map(p=>({n:p.n,g:p.g,sub:p.sub,line:p.line,semi:p.semi,rh:p.rh,steps:p.steps}))")
    ok([p['n'] for p in L] == list(range(1, 61)), 'the library has 60 patterns, numbered 1 to 60 in the order they show')
    cnt = {g: sum(1 for p in L if p['g'] == g) for g in 'warx'}
    ok(cnt == {'w': 8, 'a': 7, 'r': 33, 'x': 12}, f'Warm-ups 8, Agility 7, Riffs and runs 33, Flips 12 ({cnt})')
    fam = {s: sum(1 for p in L if p['sub'] == s) for s in 'stlm'}
    ok(fam == {'s': 8, 't': 7, 'l': 9, 'm': 9}, f'the riffs in four families: Short riffs 8, Turns and slingshots 7, Long runs 9, Minor, blues and gospel 9 ({fam})')
    ok(all(p['line'] and len(p['line']) < 70 for p in L), 'every pattern says what it trains, in one short line')
    ok(all(p['rh'] is None or len(p['rh']) == len(p['semi']) for p in L), 'note lengths, where a pattern has them, cover every note')
    minor = pg.evaluate("PAT.LIB.filter(PAT.isMinor).map(p=>p.n)")
    ok(minor == [19, 25, 40, 41, 42, 43, 44, 45], f'minor patterns are the ones with ♭3 or ♭7 and no major 3rd ({minor}); the gospel runs stay major')
    ok(pg.evaluate("JSON.stringify(PAT.triad(48,PAT.byN(42)))") == '[36,48,51,55]' and pg.evaluate("JSON.stringify(PAT.triad(48,PAT.byN(1)))") == '[36,48,52,55]',
       'a minor pattern’s chord is minor (C3: C2 C3 E♭3 G3), a major one’s major')
    quick = [p['n'] for p in L if p['rh'] and any(x < 0.5 for x in p['rh'])]
    ok(quick == [56, 57, 58, 59, 60], f'only the glide flips have quick touches (a length under 0.5): {quick}')
    ok(pg.evaluate("JSON.stringify(PAT.FAV_SEED)") == '[22,31,33,36,39,46,40,44]', 'Favourites start with the eight riffs in Bruno Mars’s style')
    defs = pg.evaluate("Object.fromEntries(Object.entries(EX_PAGE).map(([k,v])=>[k,v.def||0]))")
    ok(defs == {'slides': 0, 'humming': 1, 'lip': 1, 'straw': 1, 'falsetto': 2, 'upperlower': 6, 'rung': 3, 'hinge': 4, 'half': 2, 'vertical': 2, 'nasal': 1, 'flex': 5},
       'each exercise opens on its agreed default pattern (none for Vocal slides)')
    bad = pg.evaluate("""Object.entries(EX_PAGE).filter(([k,v])=>!DESC[k]||v.how.length<4||v.L.length!==3||v.facts.length!==3||v.facts.some(f=>!f.length||f.some(x=>!FACT_ICON[x[0]]))||!['palate','mask','nose','lips','head','centre'].includes(v.where[0])).map(e=>e[0])""")
    ok(not bad, f'every exercise page has its steps, Where you feel it, three levels and facts with icons ({bad})')
    pg.context.close()


def routes(b, t):
    ok = t.ok
    tl = json.load(open(os.path.join(HERE, '..', 'tools', 'coach-video', 'data', 'audio_timeline.json'), encoding='utf-8'))
    pg = t.page(b)
    shifts = {('humming', 2): -4, ('half', 1): -7, ('upperlower', 1): -7, ('upperlower', 2): -7, ('upperlower', 3): -7}
    bad = []
    for lvl in tl['levels']:
        ex, n = lvl['exercise'], lvl['level']
        id = lvl['id'].rsplit('_', 1)[0]
        want = []
        for r in lvl['rounds']:
            if r[2] and (not want or want[-1] != midi(r[2])): want.append(midi(r[2]))
        want = [m + shifts.get((id, n), 0) for m in want]
        pg.evaluate(LV, [id, n])
        got = pg.evaluate("PAT.state().full") if pg.evaluate("!!document.getElementById('pcCard')") else []
        if id == 'hinge':
            want = [48, 47, 46, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]  # never saved: made up, C3 down to A2, up to G3
        if got != want: bad.append(f'{id} {n}: {got} vs {want}')
    ok(not bad, 'every level plays the coach’s starting notes from the note data (shifted onto key notes where the coach starts above the key; Squeaky hinge made up)' + (': ' + '; '.join(bad[:3]) if bad else ''))
    pg.evaluate(EX, 'slides')
    ok(pg.locator('#pcCard').count() == 0 and pg.locator('#app .pcard .pdraw').count() == 1 and 'No “Hear it”' in pg.inner_text('#app .pcard')
       and pg.locator('#dock .pdock').count() == 0 and pg.locator('#dock .pk-tabbar').count() == 1,
       'Vocal slides has no “Hear it”: a still picture of the slides, and the tab bar stays')
    # the level shown: the last logged, then the dots
    d = sample()
    pg.context.close()
    pg = t.page(b, data=d)
    last = pg.evaluate("exLogged('humming')")
    pg.evaluate(EX, 'humming')
    ok(pg.locator('#app .exlvl.on').inner_text() == str(last or 1) and (not last or f'Last logged at level {last}' in pg.inner_text('#app')),
       f'the page opens on the last logged level ({last})')
    pg.click('#app .exlvl[data-v="2"]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("PAT.state().route[0]") == midi('E3') - 4 and 'Hum through a melodic pattern.' in pg.inner_text('#app')
       and pg.locator('#app .exlvl.on').inner_text() == '2', 'tapping level 2 shows its words and its starting notes')
    facts = pg.evaluate("[...document.querySelectorAll('#app .exfact .l')].map(e=>e.textContent)")
    ok(facts == ['Feel the buzz', 'Placement', 'Keep it'] and pg.locator('#app .exfact svg').count() == 3, f'and its three facts with their icons ({facts})')
    # the starting note: the stepper, remembered for the exercise
    pg.click('[data-a=patShift][data-v="1"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("PAT.state().route[0]") == midi('E3') - 3 and pg.inner_text('#pStart') == 'C♯3' and pg.evaluate("D.prefs.pat.ex.humming.off") == 1,
       'the + stepper starts a semitone higher, remembered for this exercise')
    pg.click('[data-a=patShift][data-v="-1"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("!(D.prefs.pat.ex||{}).humming"), 'and back where it was, nothing is left saved')
    pg.context.close()


def range_(b, t):
    ok = t.ok
    pg = t.page(b)
    ok(pg.evaluate("JSON.stringify(PAT.state().voice)") == '{"type":"Tenor","lo":44,"hi":69,"fal":74}', 'your voice starts as a tenor: G♯2 · A4 · falsetto top D5')
    pg.evaluate(LV, ['flex', 1]); pg.wait_for_timeout(100)
    txt = pg.inner_text('#pcRange')
    ok('Reaches A♯4 by round 18 · above your tenor top (A4)' in txt and pg.locator('#pcRange.bad').count() == 1, f'Vocal flexibility 1 warns where it goes above your top: {txt!r}')
    pg.evaluate("D.prefs.pat={voice:{type:'Custom',lo:44,hi:54,fal:56}};rerender()")
    ok(pg.locator('#pcDraw .pout').count() >= 1 and pg.evaluate("[...document.querySelectorAll('#pcDraw .pout')].every(e=>getComputedStyle(e).fill.startsWith('rgb(255, 149'))"),
       'the drawing labels the round’s notes that are out of range, in orange')
    pg.evaluate("D.prefs.pat={};rerender()")
    pg.evaluate(LV, ['falsetto', 2]); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['top'] == 74 and 'top (D5)' in pg.inner_text('#pcRange'), 'Falsetto voice checks against the falsetto top (D5)')
    pg.evaluate(LV, ['humming', 1]); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['top'] == 69, 'Humming checks against your highest comfortable note (A4)')
    pg.evaluate("D.prefs.pat=Object.assign(D.prefs.pat||{},{ex:{humming:{p:49}}});rerender()")
    ok(pg.evaluate(ST)['top'] == 74 and '(using falsetto)' in pg.inner_text('#pcRange'), 'a Flips pattern checks against the falsetto top on any exercise')
    pg.evaluate("D.prefs.pat.ex={};rerender()")
    # low: below your bottom
    for _ in range(3): pg.click('[data-a=patShift][data-v="-1"]'); pg.wait_for_timeout(60)
    ok('below your tenor bottom (G♯2)' in pg.inner_text('#pcRange'), 'starting lower warns where it dips below your bottom')
    ok('⚠' in pg.evaluate("document.querySelector('.pk-toast').textContent"), 'and the stepper’s toast warns straight away')
    pg.evaluate("D.prefs.pat.ex={};rerender()")
    # Stop at my top note
    pg.evaluate(LV, ['flex', 1]); pg.wait_for_timeout(100)
    pg.evaluate("go(()=>{U.tab='settings';U.view='set';U.setPg='voice'})"); pg.wait_for_timeout(100)
    pg.click('[data-a=patStopTop]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("D.prefs.pat.stopTop") is True, 'Stop at my top note can be switched on in Settings › Your voice')
    pg.evaluate(LV, ['flex', 1]); pg.wait_for_timeout(100)
    s = pg.evaluate(ST)
    ok(len(s['route']) == 17 and len(s['full']) == 18 and 'Stops after round 17 of 18, before going above your tenor top (A4)' in pg.inner_text('#pcRange'),
       f'on: the route ends before the first round above your top ({len(s["route"])} of {len(s["full"])})')
    pg.context.close()


def drawing(b, t):
    ok = t.ok
    pg = t.page(b)
    g = pg.evaluate("PAT.geom(PAT.byN(18)).map(p=>p.x)")
    ok(abs((g[1] - g[0]) - 2 * (g[2] - g[1])) < 0.01, 'a held note takes twice the room on the drawing (Hook riff: 5 – 4 3)')
    pg.evaluate("D.prefs.pat={ex:{humming:{p:56}}};"); pg.evaluate(EX, 'humming')
    r = pg.evaluate("[...document.querySelectorAll('#pcDraw .pdot')].map(d=>+d.getAttribute('r'))")
    ok(r[:3] == [6, 3.6, 6], f'a quick touch is drawn smaller ({r[:3]})')
    pg.evaluate("D.prefs.pat={ex:{humming:{p:9}}};rerender()")
    ok(pg.locator('#pcDraw .pline').count() == 5, 'a breath breaks the line (Build-up: five pieces)')
    pg.evaluate("D.prefs.pat={notes:'notes'};rerender()")
    ok(pg.locator('#pcDraw .pnt ellipse').count() == 9 and pg.locator('#pcDraw circle.pdot').count() == 0, 'Music notes draws note heads with stems instead of dots')
    pg.evaluate("D.prefs.pat={};rerender()")
    ok(pg.locator('#pcDraw circle.pdot').count() == 9 and pg.locator('#pcDraw .phead').count() == 1, 'dots by default, with the playhead waiting')
    # the vowel cue: only on open-vowel exercises with a scale pattern
    pg.evaluate(EX, 'falsetto')
    ok(pg.locator('#pcVowel[hidden]').count() == 1, 'no vowel cue on Falsetto voice’s default (a triad, not a scale)')
    pg.evaluate("D.prefs.pat={ex:{falsetto:{p:1}}};rerender()")
    ok(pg.inner_text('#pcVowel').split() == ['Sing', 'on', 'hoo', 'next', 'hee'], f'with the five-note scale it shows: {pg.inner_text("#pcVowel")!r}')
    pg.evaluate("D.prefs.pat.vowel='all';rerender()")
    ok('ee' in pg.inner_text('#pcVowel') and 'eh' in pg.inner_text('#pcVowel'), 'Mixed vowels: ee, eh, ah, oh, oo')
    pg.evaluate("D.prefs.pat.vowel='off';rerender()")
    ok(pg.locator('#pcVowel[hidden]').count() == 1, 'and Off hides it')
    pg.evaluate("D.prefs.pat={ex:{humming:{p:1}}}"); pg.evaluate(EX, 'humming')
    ok(pg.locator('#pcVowel[hidden]').count() == 1, 'never on Humming')
    pg.context.close()


def playing(b, t):
    ok = t.ok
    pg = t.page(b)
    # quick rounds: the 3-note riff at 2×, no chord
    pg.evaluate("D.prefs.pat={ex:{humming:{p:16}},spd:{16:11},cue:false}"); pg.evaluate(LV, ['humming', 1])
    pg.click('#pPlay')
    ok(until(pg, "PAT.state().runs.length>=3", 12000), 'Play starts the rounds')
    s = pg.evaluate(ST)
    ok(s['playing'] and pg.evaluate("NOW.kind()") == 'pattern' and pg.evaluate("AWAKE.wants('pat')"), 'it plays through the one sound owner, and keeps the screen awake')
    ok([r['k'] for r in s['runs'][:3]] == s['route'][:3], f'each round moves to the next key of the route ({[r["k"] for r in s["runs"][:3]]})')
    ok(pg.locator('#pPlay[aria-label=Stop]').count() == 1 and 'Round' in pg.inner_text('#pcStat'), 'the button becomes Stop and the card says which round')
    ok(until(pg, "document.querySelector('#pcDraw .phead').style.display===''", 3000), 'the playhead moves through the drawing')
    # Stay on this key
    pg.click('#pRep'); n0 = len(pg.evaluate(ST)['runs'])
    ok(until(pg, f"PAT.state().runs.length>={n0 + 2}", 8000), 'Stay on this key: rounds carry on')
    rr = pg.evaluate(ST)['runs'][n0 - 1:]
    ok(len(set(r['k'] for r in rr)) == 1 and 'on repeat' in pg.inner_text('#pcStat') and pg.locator('#pRep.on[aria-pressed=true]').count() == 1,
       f'Stay on this key repeats the same key ({[r["k"] for r in rr]})')
    pg.click('#pRep'); pg.wait_for_timeout(50)
    # stop
    pg.click('#pPlay'); pg.wait_for_timeout(100)
    s = pg.evaluate(ST)
    ok(not s['playing'] and pg.evaluate("NOW.kind()") is None and not pg.evaluate("AWAKE.wants('pat')"), 'Stop ends it, lets go of the sound and the screen')
    # Speed up each round: one stop a round, up to 2×, the saved speed unchanged
    pg.evaluate("D.prefs.pat.spd={16:8};D.prefs.pat.ramp=true;rerender()")
    n0 = len(pg.evaluate(ST)['runs'])
    pg.click('#pPlay')
    ok(until(pg, f"PAT.state().runs.length>={n0 + 4}", 15000), 'Speed up each round plays on')
    sp = [r['spd'] for r in pg.evaluate(ST)['runs'][n0:n0 + 4]]
    ok(sp[:4] == [1.35, 1.5, 1.75, 2], f'each round is one speed stop faster, up to 2× ({sp})')
    ok(pg.locator('#pSpd.ramping').count() == 1, 'the speed pill shows the live speed in blue')
    pg.click('#pPlay'); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['speed'] == 1.35 and pg.evaluate("D.prefs.pat.spd[16]") == 8, 'stopping goes back to your chosen speed; the saved speed never changed')
    pg.evaluate("D.prefs.pat.ramp=false;rerender()")
    # one sound at a time: another sound stops it
    pg.click('#pPlay'); until(pg, "PAT.state().playing", 3000)
    pg.evaluate("NOW.start('track','x',()=>{})"); pg.wait_for_timeout(100)
    ok(not pg.evaluate(ST)['playing'] and pg.evaluate("NOW.kind()") == 'track', 'another sound starting stops the pattern')
    pg.evaluate("NOW.stop()")
    # leaving the page stops it
    pg.click('#pPlay'); until(pg, "PAT.state().playing", 3000)
    pg.click('#barL [aria-label^=Back]'); pg.wait_for_timeout(200)
    ok(not pg.evaluate(ST)['playing'] and pg.evaluate("NOW.kind()") is None, 'going Back stops it')
    # to the end: the home ending
    pg.evaluate("D.prefs.pat.voice={type:'Custom',lo:40,hi:50,fal:52};D.prefs.pat.stopTop=true;D.prefs.pat.ending='chord'"); pg.evaluate(LV, ['humming', 1])
    n = len(pg.evaluate(ST)['route'])
    pg.click('#pPlay')
    ok(until(pg, "!PAT.state().playing", 15000) and 'Home · C3' in pg.inner_text('#pcStat'), f'after the last round ({n}) it goes home to the starting key: “Home · C3”')
    ok(until(pg, "!/Home/.test(document.getElementById('pcStat').textContent)", 5000) and 'Starts on C3' in pg.inner_text('#pcStat'), 'and settles back to “Starts on”')
    pg.context.close()


def page_(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=812)
    pg.evaluate(EX, 'humming')
    pg.click('[data-a=patOpen]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'pat' and pg.locator('#app h1').inner_text() == 'Patterns' and pg.inner_text('#app .pfor') == 'Humming', 'the pattern pill opens the Patterns page, for this exercise')
    ok(pg.locator('#dock *').count() == 0, 'it has no dock: only its tiles scroll')
    ok(pg.locator('#app .pgrp button').count() == 5 and pg.locator('#app .pgrp button.on').inner_text() == 'Warm-ups'
       and pg.locator('#app .pgrp [aria-label=Favourites] .pstar').count() == 1, 'the group control: ★ (Favourites) · Warm-ups · Agility · Riffs and runs · Flips, open on the chosen pattern’s group')
    ok(pg.locator('#app .pt').count() == 8 and pg.locator('#app .pt.on .pchk').count() == 1 and pg.locator('#app .pt.on .pdft').count() == 1, 'eight warm-ups; the chosen one has a ✓ and the default is marked')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth") and pg.evaluate("(()=>{const s=document.querySelector('.pgrp');return s.scrollWidth<=s.clientWidth+1})()"),
       'nothing scrolls sideways, and the group control fits at 375 px')
    # the window stays put while the tiles scroll
    y0 = pg.evaluate("document.getElementById('pWin').getBoundingClientRect().top")
    pg.evaluate("scrollTo(0,400)"); pg.wait_for_timeout(100)
    y1 = pg.evaluate("document.getElementById('pWin').getBoundingClientRect().top")
    ok(y1 < y0 and y1 > 40 and pg.evaluate("scrollY") > 100, f'the window stays fixed under the bar while the tiles scroll ({y0:.0f} → {y1:.0f})')
    pg.evaluate("scrollTo(0,0)")
    # groups
    pg.click('#app .pgrp [data-v=r]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("[...document.querySelectorAll('#pTiles .psub')].map(e=>e.textContent)") == ['Short riffs', 'Turns and slingshots', 'Long runs', 'Minor, blues and gospel']
       and pg.locator('#pTiles .pt').count() == 33, 'Riffs and runs: 33, under their four family headings')
    pg.click('#app .pgrp [data-v=f]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("[...document.querySelectorAll('#pTiles .pnum')].map(e=>+e.textContent)") == [22, 31, 33, 36, 39, 46, 40, 44]
       and pg.locator('#app .pgrp .pfseg .pstar.on').count() == 1, 'Favourites: the eight riffs, in the order added, and the star fills')
    # favourites
    pg.click('#pTiles .pfav[data-v="22"]'); pg.wait_for_timeout(100)
    ok(22 not in pg.evaluate(ST)['favs'] and pg.evaluate("document.querySelector('.pk-toast').textContent") == 'Removed from Favourites', 'a tile’s star removes it, with a toast')
    pg.click('#app .pgrp [data-v=w]'); pg.wait_for_timeout(100)
    pg.click('#pTiles .pfav[data-v="3"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['favs'][-1] == 3 and pg.locator('#pTiles .pfav[data-v="3"].on[aria-pressed=true]').count() == 1, 'and adds any pattern, outlined off and filled on')
    pg.evaluate("D.prefs.pat.fav=[];"); pg.click('#app .pgrp [data-v=f]'); pg.wait_for_timeout(100)
    ok('No favourites yet' in pg.inner_text('#pTiles'), 'with none: “No favourites yet”')
    pg.click('#app .pgrp [data-v=w]'); pg.wait_for_timeout(100)
    # press and hold: what it trains, never a pick
    box = pg.locator('#pTiles .pt[data-v="4"]').bounding_box()
    pg.mouse.move(box['x'] + 40, box['y'] + 50); pg.mouse.down(); pg.wait_for_timeout(700)
    held = pg.evaluate("(()=>{const t=document.querySelector('#pTiles .pt[data-v=\"4\"]');return t.classList.contains('held')&&getComputedStyle(t.querySelector('.pline')).opacity==='1'})()")
    t.shot(pg, 'hold')
    pg.mouse.up(); pg.wait_for_timeout(150)
    ok(held, 'press and hold a tile: its steps fade into what it trains')
    ok(pg.evaluate(ST)['pattern'] == 1 and pg.evaluate(ST)['preview'] is None, 'letting go picks and plays nothing')
    ok(pg.get_attribute('#pTiles .pt[data-v="4"]', 'aria-description') == 'Landing the top note cleanly, with no slide', 'VoiceOver reads what it trains as the hint')
    pg.wait_for_timeout(400)
    # a tap picks and plays it in the window
    pg.click('#pTiles .pt[data-v="4"]'); pg.wait_for_timeout(150)
    s = pg.evaluate(ST)
    ok(s['pattern'] == 4 and s['preview'] == 4 and pg.evaluate("D.prefs.pat.ex.humming.p") == 4, 'a tap picks it (remembered for this exercise) and plays it once')
    ok(pg.locator('#pWin .pwplay.live').count() == 1 and pg.locator('#pTiles .pt.live').count() == 1 and pg.inner_text('#pWin .pwh b') == 'Octave jump',
       'the window shows it playing, and the tile’s play turns blue')
    ok(until(pg, "document.querySelector('#pwDraw .phead').style.display===''", 3000), 'its drawing plays like the exercise page’s, playhead and all')
    ok(pg.evaluate("(()=>{const w=document.getElementById('pWin');return !w.classList.contains('live')&&getComputedStyle(w).outlineStyle==='none'})()"), 'the window never highlights itself')
    pg.click('#pWin .pwplay'); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['preview'] is None and pg.evaluate("NOW.kind()") is None, 'its stop button stops it')
    pg.click('#pTiles .preset'); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['pattern'] == 1 and not pg.evaluate("(D.prefs.pat.ex||{}).humming"), 'Back to default goes back to the exercise’s default')
    pg.click('#pTiles .pt[data-v="7"]'); pg.wait_for_timeout(100)
    pg.click('#barL [aria-label^=Back]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'ex' and 'Octave scale' in pg.inner_text('#dock .ppat') and pg.evaluate("NOW.kind()") is None, 'Back returns to the exercise, on the new pattern, with the preview stopped')
    pg.context.close()


def zoom(b, t):
    ok = t.ok
    on = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"
    pg = t.page(b, touch=True, init=on)
    pg.evaluate(EX, 'humming'); pg.wait_for_function(QUIET, timeout=10000)
    pg.click('[data-a=patOpen]')
    ok(until(pg, "!!document.querySelector('.zm .zm-c')", 3000), 'opening Patterns zooms from the pattern pill (the app’s card zoom)')
    ok(until(pg, CLEAN, 10000) and pg.evaluate("U.view") == 'pat' and pg.evaluate("ZOOM.stack().slice(-1)[0].key") == 'pat', 'and lands on the page, with nothing left over')
    pg.click('#barL [aria-label^=Back]')
    ok(until(pg, "!!document.querySelector('#dock .ppat.zm-src')", 3000), 'Back shrinks it into the pill (hidden while the page lands on it)')
    ok(until(pg, CLEAN, 10000) and pg.evaluate("U.view") == 'ex' and pg.locator('#dock .ppat').is_visible(), 'and the pill comes back')
    # swipe back from anywhere
    pg.click('[data-a=patOpen]'); until(pg, CLEAN, 10000); pg.wait_for_function(QUIET, timeout=10000)
    y = pg.evaluate("(()=>{const r=document.querySelector('#app h1').getBoundingClientRect();return r.top+r.height/2})()")
    drag(pg, 40, y, 330, y + 4, steps=12, ms=16)
    ok(until(pg, CLEAN, 10000) and pg.evaluate("U.view") == 'ex', 'swiping back from the page closes it past the threshold')
    pg.context.close()
    pg = t.page(b, touch=True, init=on, ctx_args={'reduced_motion': 'reduce'})
    pg.evaluate(EX, 'humming'); pg.wait_for_function(QUIET, timeout=10000)
    pg.click('[data-a=patOpen]')
    until(pg, "!!document.querySelector('.zm')&&document.getAnimations().length>0", 3000)
    keys = pg.evaluate("[...document.querySelectorAll('.zm, .zm *')].flatMap(e=>e.getAnimations()).flatMap(a=>Object.keys(a.effect.getKeyframes()[0])).filter(k=>!['offset','easing','composite','computedOffset'].includes(k))")
    ok(set(keys) <= {'opacity'}, f'Reduce Motion: it fades instead ({sorted(set(keys))})')
    until(pg, CLEAN, 10000)
    pg.click('#barL [aria-label^=Back]'); until(pg, CLEAN, 10000)
    pg.evaluate("D.prefs.pat={ex:{humming:{p:16}},spd:{16:11},cue:false}"); pg.evaluate(LV, ['humming', 1]); pg.click('#pPlay')
    until(pg, "PAT.state().runs.length>=2", 8000)
    ok(pg.locator('#pcDraw .prip').count() == 0, 'and no ripples on the notes')
    pg.click('#pPlay')
    pg.context.close()


def speed(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate(EX, 'humming')
    ok(pg.inner_text('#pSpd') == '1×', 'the speed pill starts at 1×')
    pg.click('#pSpd'); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['hud'] and pg.locator('#pHud.on .pk-slider[role=slider][data-max="11"][data-step="1"]').count() == 1,
       'a tap opens the slider (Q41: the parts kit\'s, D03): 12 stops')
    ok(pg.evaluate("[...document.querySelectorAll('#pHudLabs span')].map(s=>s.textContent)") == ['0.5×', '1×', '2×'], 'only 0.5×, 1× and 2× are labelled')
    pg.click('#pHud [data-a=patSpdStep][data-v="1"]'); pg.wait_for_timeout(50)
    ok(pg.inner_text('#pHudVal') == '1.1×' and pg.inner_text('#pSpd') == '1.1×' and pg.evaluate("D.prefs.pat.spd[1]") == 6, 'the + in the bubble goes up one stop, saved for this pattern')
    ok(pg.evaluate("document.querySelector('#pHudBar').dataset.value") == '6', 'and the slider follows it')
    # drag the kit's slider: its knob grows while held, and it snaps to the stops
    bb = pg.locator('#pHud .pk-slider').bounding_box()
    step = bb['width'] / 11
    y = bb['y'] + bb['height'] / 2
    drag(pg, bb['x'] + step * 6, y, bb['x'] + step * 9, y, steps=6, ms=16)
    ok(pg.evaluate(ST)['speed'] == 1.5, f'dragging it to the ninth stop sets 1.5× ({pg.evaluate(ST)["speed"]}×)')
    drag(pg, bb['x'] + step * 9, y, bb['x'] - 200, y, steps=10, ms=16)
    ok(pg.evaluate(ST)['speed'] == 0.5, 'and past the start stops at 0.5×')
    pg.click('#pHud [data-a=patRamp]'); pg.wait_for_timeout(50)
    ok(pg.evaluate("D.prefs.pat.ramp") is True and pg.locator('#pHudRamp.on').count() == 1 and pg.locator('#pSpd.ramping').count() == 1, 'Speed up each round is a toggle in the bubble')
    pg.click('#pHud [data-a=patRamp]')
    ok(until(pg, "!PAT.state().hud", 5000), 'the slider closes by itself after a moment')
    # each pattern its own speed
    pg.evaluate("D.prefs.pat.ex={humming:{p:2}};rerender()")
    ok(pg.inner_text('#pSpd') == '1×', 'another pattern keeps its own speed')
    pg.evaluate("D.prefs.pat.ex={};rerender()")
    ok(pg.inner_text('#pSpd') == '0.5×', 'and the first one remembers 0.5×')
    # holding the pill opens it too, and a drag carries on
    sb = pg.locator('#pSpd').bounding_box()
    cx, cy = sb['x'] + sb['width'] / 2, sb['y'] + sb['height'] / 2
    pg.mouse.move(cx, cy); pg.mouse.down(); pg.wait_for_timeout(450)
    ok(pg.evaluate(ST)['hud'], 'holding the pill opens the slider')
    for i in range(1, 7): pg.mouse.move(cx + step * 0.5 * i, cy); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(100)
    ok(pg.evaluate(ST)['speed'] == 0.8, f'and dragging straight on changes it ({pg.evaluate(ST)["speed"]}×)')
    t.shot(pg, 'slider')
    pg.context.close()


def settings(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=812)
    pg.evaluate("go(()=>{U.tab='settings';U.view=null})"); pg.wait_for_timeout(100)
    ok(pg.inner_text('#app [data-zk="set:voice"] .mut') == 'Tenor' and pg.inner_text('#app [data-zk="set:player"] .mut') == 'Soft tone',
       'Settings lists Your voice (Tenor) and Pattern player (Soft tone)')
    pg.click('#app [data-zk="set:voice"]'); pg.wait_for_timeout(200)
    ok(pg.locator('#app h1').inner_text() == 'Your voice' and [pg.inner_text(f'#pv_{k}') for k in ('lo', 'hi', 'fal')] == ['G♯2', 'A4', 'D5'], 'Your voice: G♯2 · A4 · D5')
    pg.click('[data-a=patVoiceType]'); pg.wait_for_timeout(100)
    ok(pg.locator('.pmenu [role=menuitemradio]').count() == 6 and pg.locator('.pmenu [aria-checked=true]').inner_text().strip().endswith('Tenor'), 'Voice type is a pop-up menu of six, with a ✓ on Tenor')
    pg.click('.pmenu [data-v=Baritone]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("JSON.stringify(D.prefs.pat.voice)") == '{"type":"Baritone","lo":45,"hi":67,"fal":72}' and pg.locator('.pmenu').count() == 0, 'picking Baritone sets its range')
    pg.click('[data-a=patNudge][data-v=hi][data-k="1"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("D.prefs.pat.voice.type") == 'Custom' and pg.inner_text('#pv_hi') == 'G♯4', 'a stepper makes it Custom')
    t.shot(pg, 'voice')
    pg.click('#barL [aria-label^=Back]'); pg.wait_for_timeout(200)
    ok(pg.inner_text('#app [data-zk="set:voice"] .mut') == 'Custom', 'Back to Settings, showing Custom')
    pg.click('#app [data-zk="set:player"]'); pg.wait_for_timeout(200)
    pg.click('[data-a=patSoundPick][data-v=piano]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("D.prefs.pat.sound") == 'piano' and pg.locator('[data-a=patSoundPick][aria-checked=true]').inner_text().strip() == 'Piano-ish', 'Pattern player: the sound')
    pg.click('[data-a=patDrone]'); pg.click('[data-a=patCue]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("[D.prefs.pat.drone,D.prefs.pat.cue]") == [False, False], 'Held note underneath and Chord before each round switch off')
    pg.click('[data-a=patEnding][data-v=note]'); pg.click('[data-a=patVowel][data-v=all]'); pg.click('[data-a=patNotes][data-v=notes]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("[D.prefs.pat.ending,D.prefs.pat.vowel,D.prefs.pat.notes]") == ['note', 'all', 'notes'], 'Ending, Vowel cue and Notes on the drawing are segmented controls')
    t.shot(pg, 'player')
    # the sound menu in the dock
    pg.evaluate(EX, 'humming')
    pg.click('#pSnd'); pg.wait_for_timeout(100)
    items = pg.evaluate("[...document.querySelectorAll('.pmenu button')].map(b=>(b.querySelector('svg')?'✓':'')+b.textContent)")
    ok(items == ['Soft tone', '✓Piano-ish', 'Electric piano', 'Held note underneath'],
       f'the sound pill opens a menu with a ✓, and Held note underneath under it ({items})')
    pg.click('.pmenu [data-v=ep]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("D.prefs.pat.sound") == 'ep' and 'Electric piano' in pg.inner_text('#pSnd'), 'picking one changes the pill')
    # the range line opens Your voice, and Back returns to the exercise
    pg.click('#pcRange'); pg.wait_for_timeout(200)
    ok(pg.evaluate("[U.view,U.setPg]") == ['set', 'voice'] and pg.locator('#barL [aria-label=Back]').count() == 1, 'tapping the range line opens Your voice')
    pg.click('#barL [aria-label^=Back]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("[U.view,U.exId]") == ['ex', 'humming'], 'and Back returns to the exercise')
    pg.context.close()


def data(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(EX, 'humming')
    pg.click('[data-a=patShift][data-v="1"]')
    pg.evaluate("D.prefs.pat=Object.assign(D.prefs.pat,{spd:{1:3},fav:[5,22],voice:{type:'Alto',lo:53,hi:74,fal:77},sound:'piano',drone:false,cue:false,ending:'note',vowel:'all',notes:'notes',stopTop:true,ramp:true});D.prefs.pat.ex.humming.p=7;save()")
    want = pg.evaluate("JSON.stringify(D.prefs.pat)")
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')", timeout=15000)
    ok(pg.evaluate("JSON.stringify(D.prefs.pat)") == want, 'every saved choice survives a reload')
    # a backup round trip
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';render()"); pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=10000)
    txt = pg.evaluate("pendingExport.file.text()")
    ok(json.dumps(json.loads(txt)['data']['prefs']['pat'], sort_keys=True) == json.dumps(json.loads(want), sort_keys=True), 'and goes into the backup')
    p = write('patterns-now.json', raw=txt)
    pg.evaluate("U.sheet=null;D.prefs.pat={};save();render()")
    pick(pg, 'importPick', p)
    pg.click('[data-a=importYes]'); pg.wait_for_function("U.sheet===null", timeout=10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("JSON.stringify(D.prefs.pat)") == want, 'restoring the backup brings every choice back')
    # malformed fields dropped, unknown ones kept
    c = pg.evaluate("""PAT.clean({ex:{humming:{p:99,off:'x',z:1},lip:5},spd:{1:40,2:3},fav:[1,1,'a',99,4],voice:{type:'Opera',lo:1,hi:2,fal:3},sound:7,drone:'yes',
      ending:'loud',vowel:'ex',notes:'dots',future:{a:1}})""")
    ok(c == {'ex': {'humming': {'z': 1}}, 'spd': {'2': 3}, 'fav': [1, 4], 'vowel': 'ex', 'notes': 'dots', 'future': {'a': 1}},
       f'checking drops only what’s malformed and keeps fields it doesn’t know ({c})')
    ok(pg.evaluate("(()=>{const d=cleanData({sessions:[],prefs:{pat:{fav:[3],next:true}}});return JSON.stringify(d.prefs.pat)})()") == '{"fav":[3],"next":true}',
       'cleanData checks the player’s choices the same way')
    pg.context.close()
    # data from before: no choices, everything on its default
    pg = t.page(b)
    ok(pg.evaluate("D.prefs.pat") is None, 'data from before 3.48 has no player choices')
    pg.evaluate(EX, 'humming')
    s = pg.evaluate(ST)
    ok(s['pattern'] == 1 and s['speed'] == 1 and s['opts'] == {'sound': 'soft', 'drone': True, 'cue': True, 'ending': 'chord', 'vowel': 'ex', 'notes': 'dots', 'stopTop': False, 'ramp': False,
                                                                       'stopLast': False, 'bcue': True, 'listen': False}
       and pg.evaluate("D.prefs.pat") is None, 'and the player starts on its defaults without saving anything')
    pg.context.close()


def sizes(b, t):
    ok = t.ok
    ids = ['slides', 'humming', 'lip', 'straw', 'falsetto', 'upperlower', 'rung', 'hinge', 'half', 'vertical', 'nasal', 'flex']
    for sc in ('light', 'dark'):
        for w, h in ((375, 812), (390, 844)):
            pg = t.page(b, w=w, h=h, sc=sc)
            bad = []
            for id in ids:
                pg.evaluate(EX, id); pg.wait_for_timeout(60)
                over = pg.evaluate("document.documentElement.scrollWidth>innerWidth")
                txt = pg.inner_text('#app') + pg.inner_text('#dock')
                dk = pg.evaluate("(()=>{const d=document.querySelector('#dock .pdock');if(!d)return true;return [...d.querySelectorAll('button,.pstep')].every(e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.width>=40})})()")
                if over or not dk or any(x in txt for x in ('undefined', 'NaN', 'null')): bad.append(id)
                if w == 375: t.shot(pg, f'{id}-{sc}')
            ok(not bad, f'{w} {sc}: every exercise page fits, its dock fits, nothing reads undefined ({bad})')
            if w == 375:
                pg.evaluate(EX, 'humming'); pg.click('[data-a=patOpen]'); pg.wait_for_timeout(150)
                ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{w} {sc}: the Patterns page fits')
                t.shot(pg, f'patterns-{sc}')
                pg.evaluate("scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(100)
                t.shot(pg, f'patterns-end-{sc}')
                pg.click('#barL [aria-label^=Back]'); pg.wait_for_timeout(150)
                # scrolled to the bottom, the last text clears the dock
                pg.evaluate("scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(100)
                ok(pg.evaluate("(()=>{const g=[...document.querySelectorAll('#app .grp')].pop().getBoundingClientRect();return g.bottom<=document.querySelector('#dock .pdock').getBoundingClientRect().top})()"),
                   f'{w} {sc}: scrolled to the end, the page clears the dock')
            pg.context.close()
    # iPad: in the split view the dock sits under the exercise's pane
    pg = t.page(b, w=1180, h=820)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null;U.exId='falsetto';U.exTab='summary'})"); pg.wait_for_timeout(200)
    r = pg.evaluate("(()=>{const p=document.querySelector('#app .pane').getBoundingClientRect(),d=document.querySelector('#dock .pdock').getBoundingClientRect();return [p.left,p.right,d.left,d.right]})()")
    ok(r[2] >= r[0] - 1 and r[3] <= r[1] + 1, f'iPad split view: the dock sits under the exercise, not across the list ({r})')
    t.shot(pg, 'ipad')
    pg.click('[data-a=patOpen]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'pat', 'and its pill opens Patterns')
    pg.click('#barL [aria-label^=Back]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("[U.view,U.tab]") == [None, 'exercises'], 'Back returns to the split view')
    pg.context.close()
    # iPhone on its side
    pg = t.page(b, w=852, h=393)
    pg.evaluate(EX, 'humming'); pg.wait_for_timeout(150)
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth") and pg.locator('#dock .pdock').count() == 1, 'iPhone on its side: the page and its dock fit')
    t.shot(pg, 'landscape')
    pg.context.close()


PARTS = {'library': library, 'routes': routes, 'range': range_, 'drawing': drawing, 'playing': playing, 'page': page_, 'zoom': zoom,
         'speed': speed, 'settings': settings, 'data': data, 'sizes': sizes}


def run(b, t):
    want = [p for p in os.environ.get('VS_PAT', '').split(',') if p]
    for name, fn in PARTS.items():
        if want and name not in want: continue
        print(f'  · {name}')
        try:
            fn(b, t)
        except Exception as e:
            t.ok(False, f'{name}: stopped: {str(e).splitlines()[0]}')
