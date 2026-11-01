"""Q21 the Session saved screen: finishing a focused session lands on "Session saved" (the week arch with only today's
minutes drawing in, "N min · Day · weekly goal reached", the week row with the day just practised green, "N-week
streak continues", Done below), and Done turns it into Today: the arch, week row and streak line move onto their places,
Done becomes Start session, the rest of Today rises in. The numbers are the app's own (minutes, weekday, goal, streak),
the goal and streak lines are left out when they don't apply, nothing counts up, Reduce Motion fades, a layout the
morph can't land on (no streak, landscape, a page too tall) fades, taps work mid-morph, Song practice keeps its own
finish, and the screen at 390 and 375 in light and dark (plus the larger page zoom as a stand-in for larger text).
Synthetic data only."""
import datetime as dt
from harness import sample, iso, until, now

MOTION_ON = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"
REDUCE_ON = "try{localStorage.setItem('vocalMotion','1');localStorage.setItem('vocalReduce','on')}catch(e){}"
WIDE = "document.documentElement.scrollWidth<=innerWidth+1"
QUIET = "!document.getAnimations().some(a=>(a.playState==='running'||a.playState==='pending')&&a.effect.getTiming().iterations!==Infinity)"
# animations on matching elements: their properties (minus the offset and easing) and their delay
ANIM = """sel=>[...document.querySelectorAll(sel)].flatMap(el=>el.getAnimations().filter(a=>a.effect.getTiming().iterations!==Infinity)
  .map(a=>({d:a.effect.getTiming().delay,k:Object.keys(a.effect.getKeyframes()[0]).filter(x=>!['offset','easing','composite','computedOffset'].includes(x)).join()})))"""
RECT = "sel=>{const e=document.querySelector(sel);if(!e)return null;const r=e.getBoundingClientRect();return {l:r.left,t:r.top,w:r.width,h:r.height,b:r.bottom}}"
PIECES = {'arc': '#app .arch', 'week': '#app .week', 'streak': '#app .streak', 'btn': '#app [data-zk=start]'}
SAVED_PIECES = {'arc': '#app [data-sv=arc]', 'week': '#app [data-sv=week]', 'streak': '#app [data-sv=streak]', 'btn': '#app [data-sv=btn]'}


def full():
    """A streak and a goal reached: last week 80 minutes, 40 more earlier today, backed up today (no reminder)."""
    d = sample()
    ws = now.replace(hour=12, minute=0, second=0, microsecond=0) - dt.timedelta(days=now.weekday())
    lw = ws - dt.timedelta(days=4)
    early = now.replace(hour=0, minute=1, second=0, microsecond=0)
    d['sessions'] = [
        {"id": "lw", "date": iso(lw), "end": iso(lw + dt.timedelta(minutes=80)), "mins": 80, "f": {"slides": 2}, "fNote": "",
         "rot": {}, "rNote": "", "rotNames": {}, "songName": "", "rate": {}, "takes": []},
        {"id": "am", "date": iso(early), "end": iso(early + dt.timedelta(minutes=40)), "mins": 40, "f": {"slides": 2}, "fNote": "",
         "rot": {}, "rNote": "", "rotNames": {}, "songName": "", "rate": {}, "takes": []},
    ]
    d['lastBackup'] = iso(now)
    return d


def none():
    """No sessions at all: no streak, and 20 minutes stays under the weekly goal."""
    d = sample()
    d['sessions'] = []
    d['lastBackup'] = iso(now)
    return d


def finish(pg, mins):
    """A session of about mins minutes through Foundation, Rotation and Application, then Finish session."""
    pg.evaluate("U.sheet=null;go(()=>{U.tab='today';U.view=null})")
    pg.click('[data-a=start]')
    until(pg, "U.view==='found'")
    pg.evaluate(f"""FOUND.forEach(e=>X.f[e.id]=2);X.start=Math.max(Date.now()-{mins}*60000,startOfDay(new Date()).getTime()+1000);
      X.fEnd=Date.now();X.fE=elapsedSec()*0.4;X.rot={{rung:2}};X.rEnd=Date.now();X.rE=elapsedSec()*0.7;saveDraft();go(()=>{{U.view='app'}})""")
    pg.click('#dock [data-a=cta]')
    return until(pg, "X===null&&U.view==='saved'")


def numbers(b, t):
    ok = t.ok
    # a streak and the goal reached
    pg = t.page(b, data=full())
    ok(finish(pg, 41), 'finishing a session lands on Session saved')
    n = pg.evaluate("""(()=>{const ss=D.sessions[D.sessions.length-1],w=weekInfo();return {mins:ss.mins,day:new Date(ss.date).toLocaleDateString('en-GB',{weekday:'long'}),
      wm:Math.round(w.mins),streak:w.streak,reached:w.mins>=WEEK_TARGET,now:startOfDay(ss.date).getTime(),ws:w.ws.getTime(),id:ss.id,
      pa:Math.min(100,Math.round(w.mins/WEEK_TARGET*100)),pb:Math.min(100,Math.round((w.mins-ss.mins)/WEEK_TARGET*100))}})()""")
    ok(pg.evaluate("U.saved.k") == n['id'] and pg.evaluate("U.tab") == 'today' and not pg.evaluate("U.sheet"), 'for the session just saved, with no sheet over it')
    ok(pg.inner_text('#app h1').strip() == 'Session saved', 'the title is Session saved')
    ok(pg.inner_text('#app .arch .c b').strip() == str(n['wm']), f"the arch shows this week's minutes ({n['wm']})")
    line = pg.inner_text('#app .svd-line').strip()
    ok(line == f"{n['mins']} min · {n['day']} · weekly goal reached" and n['reached'], f'the line: real minutes, the real weekday and goal reached ({line})')
    ok(pg.inner_text('#app [data-sv=streak]').strip() == f"{n['streak']}-week streak continues" and n['streak'] >= 1, f"the streak line ({n['streak']} weeks)")
    was = pg.evaluate("document.querySelector('#app .svd-was').getAttribute('stroke-dasharray')")
    new = pg.evaluate("(()=>{const p=document.querySelector('#app .svd-new');return [p.getAttribute('stroke-dasharray'),p.getAttribute('stroke-dashoffset')]})()")
    ok(was == f"{n['pb']} 100" and new == [f"{n['pa'] - n['pb']} 100", str(-n['pb'])],
       f"the arch: the week so far ({was}), then today's minutes on top ({new[0]} from {new[1]})")
    ok(pg.evaluate("getComputedStyle(document.querySelector('#app .svd-was')).opacity") == '0.4', 'the week so far drawn lighter')
    dot = pg.evaluate("(()=>{const d=document.querySelector('#app .week .svd-now');return d?[d.getAttribute('aria-label'),getComputedStyle(d).backgroundColor,"
                      "getComputedStyle(document.querySelector('.svd-line')).color]:null})()")
    green = pg.evaluate("(()=>{const p=document.createElement('i');p.style.color='var(--good)';document.body.appendChild(p);const c=getComputedStyle(p).color;p.remove();return c})()")
    ok(dot and dot[0].startswith(n['day']) and dot[1] == green and pg.locator('#app .week .svd-now').count() == 1, f"that day's circle is green ({dot and dot[0]})")
    ok(pg.locator('#dock .tabbar').count() == 0 and pg.inner_text('#barT').strip() == 'Session saved' and pg.inner_text('#barR').strip() == '',
       'no tab bar and no top-bar buttons: Done is the way on')
    done = pg.evaluate(RECT, '#app .svd-done'); st = pg.evaluate(RECT, '#app [data-sv=streak]')
    ok(done and abs(done['l'] + done['w'] / 2 - 195) < 1 and 8 <= done['t'] - st['b'] <= 40 and done['b'] <= 844 - 100,
       'Done is centred just below the streak line, not pinned at the bottom')
    t.shot(pg, 'reached')
    # Done: Today (motion off: straight there)
    pg.click('[data-a=savedDone]')
    ok(until(pg, "U.view===null&&U.tab==='today'") and pg.evaluate("U.saved") is None and pg.locator('#dock .tabbar').count() == 1
       and pg.locator('#app [data-zk=start]').inner_text().strip() == 'Start session', 'Done turns it into Today, with Start session and the tab bar')
    ok(pg.locator('#app .svd-now').count() == 0 and pg.locator('#app .week span.today.done').count() == 1, "Today shows the day as practised, in its own colour")
    pg.context.close()

    # no streak, goal not reached
    pg = t.page(b, data=none())
    ok(finish(pg, 20), 'a first session')
    n = pg.evaluate("(()=>{const ss=D.sessions[0],w=weekInfo();return {mins:ss.mins,day:new Date(ss.date).toLocaleDateString('en-GB',{weekday:'long'}),streak:w.streak,wm:w.mins}})()")
    line = pg.inner_text('#app .svd-line').strip()
    ok(line == f"{n['mins']} min · {n['day']}" and n['wm'] < 70, f'under the goal, the line is minutes and day only ({line})')
    ok(n['streak'] == 0 and pg.locator('#app [data-sv=streak]').count() == 0, 'with no streak, the streak line is left out')
    ok(pg.locator('#app .svd-was').count() == 0 and pg.locator('#app .svd-new').count() == 1, 'nothing from earlier in the week: all of the arch is today')
    accent = pg.evaluate("(()=>{const p=document.createElement('i');p.style.color='var(--accent)';document.body.appendChild(p);const c=getComputedStyle(p).color;p.remove();return c})()")
    ok(pg.evaluate("getComputedStyle(document.querySelector('#app .svd-new')).stroke") == accent, 'in Today’s blue while under the goal, as Today draws it')
    t.shot(pg, 'first')
    # the session deleted from somewhere else: plain Today
    pg.evaluate("D.sessions=[];render()")
    ok(pg.evaluate("U.view") is None and pg.locator('#app .titlerow').count() == 1, 'if the session has gone, Today shows instead')
    pg.context.close()


def song(b, t):
    """Song practice keeps its own finish (How did it go?, then its summary sheet over Today)."""
    ok = t.ok
    pg = t.page(b)
    pg.evaluate("(()=>{newSong();X.song='g_1';X.start=Date.now()-6e5;X.takes=['t1'];saveDraft();go(()=>{U.tab='today';U.view='song'})})()")
    pg.click('#dock .cta')
    ok(until(pg, "U.sheet==='how'"), 'Song practice still asks how it went')
    pg.click('[data-a=saveHow]')
    ok(until(pg, "U.sheet==='songDone'") and pg.evaluate("U.view") is None, 'and lands on its own summary, not Session saved')
    pg.context.close()


def motion(b, t):
    ok = t.ok
    pg = t.page(b, data=full(), init=MOTION_ON)
    finish(pg, 41)
    sv = pg.evaluate(ANIM, '#app [data-sv]')
    ok(len(sv) >= 6 and all('transform' in a['k'] and 'opacity' in a['k'] for a in sv), f'its parts rise in ({len(sv)})')
    order = {k: pg.evaluate(ANIM, f'#app [data-sv={k}]') for k in ['title', 'arc', 'line', 'week', 'streak', 'btn']}
    ds = [order[k][0]['d'] for k in ['title', 'arc', 'line', 'week', 'streak', 'btn']]
    ok(ds == sorted(ds) and ds[0] == 0, f'top to bottom ({ds})')
    draw = pg.evaluate(ANIM, '#app .svd-new')
    ok(len(draw) == 1 and draw[0]['k'] == 'strokeDasharray', "only today's minutes draw into the arch")
    ok(pg.evaluate(ANIM, '#app .svd-was') == [], 'the week so far stays still')
    ok(pg.evaluate(ANIM, '#app .arch .c b') == [] and pg.inner_text('#app .arch .c b').strip() == str(pg.evaluate("Math.round(weekInfo().mins)")),
       'the number is its final value from the start (no count-up)')
    dot = pg.evaluate(ANIM, '#app .svd-now')
    ok(sorted(','.join(sorted(a['k'].split(','))) for a in dot) == ['backgroundColor,borderColor,color', 'transform'], "the day's circle turns green with a small pop")
    ok(pg.locator('.confetti, canvas').count() == 0, 'no confetti')
    pg.wait_for_function(QUIET, timeout=15000)
    t.shot(pg, 'motion-saved')
    was = {k: pg.evaluate(RECT, s) for k, s in SAVED_PIECES.items()}

    # Done, paused 40% of the way: each piece is between where it was and its place on Today
    pg.click('[data-a=savedDone]')
    pg.evaluate("document.getAnimations().forEach(a=>{const t=a.effect.getTiming();if(t.iterations===Infinity)return;a.pause();a.currentTime=(t.delay||0)+t.duration*0.4})")
    mid = {k: pg.evaluate(RECT, s) for k, s in PIECES.items()}
    stk = pg.evaluate(ANIM, '#app .streak')
    tf = pg.evaluate("sel=>[...document.querySelectorAll(sel)].map(e=>e.getAnimations().length)", '#app .arch, #app .week, #app .streak, #app [data-zk=start]')
    ok(pg.evaluate("U.view") is None and all(x >= 1 for x in tf), f'Done: Today is drawn at once and its pieces are moving ({tf})')
    btn = pg.evaluate(ANIM, '#app [data-zk=start]')
    ok(any(a['k'] == 'color' for a in btn) and any(a['k'] == 'transform' for a in btn), 'Done moves to Start session’s place and its words fade in')
    rest = pg.evaluate(ANIM, '#app .grp[data-rise], #app .titlerow h1, #app .titlerow .dateline, #dock .dockrow')
    ok(len(rest) >= 4 and all('opacity' in a['k'] for a in rest), 'the title, the date, the rest of Today and the tab bar rise in')
    pg.evaluate("document.getAnimations().forEach(a=>{const t=a.effect.getTiming();if(t.iterations===Infinity)return;a.currentTime=(t.delay||0)+t.duration})")
    end = {k: pg.evaluate(RECT, s) for k, s in PIECES.items()}
    btw = lambda k: min(was[k]['t'], end[k]['t']) - 1 <= mid[k]['t'] <= max(was[k]['t'], end[k]['t']) + 1 and abs(was[k]['t'] - end[k]['t']) > 4
    ok(all(btw(k) for k in ['arc', 'week', 'btn']), 'mid-way, the arch, week row and button sit between the two screens: '
       + ', '.join(f"{k} {was[k]['t']:.0f}→{mid[k]['t']:.0f}→{end[k]['t']:.0f}" for k in ['arc', 'week', 'btn']))
    ok(any('transform' in a['k'] for a in stk) and min(was['streak']['t'], end['streak']['t']) - 1 <= mid['streak']['t'] <= max(was['streak']['t'], end['streak']['t']) + 1,
       f"and so does the streak line ({was['streak']['t']:.0f}→{mid['streak']['t']:.0f}→{end['streak']['t']:.0f})")
    ok(pg.evaluate(ANIM, '#app .svd-tmp') != [] or pg.locator('#app .svd-tmp').count() >= 1, 'the week so far darkens into Today’s solid arch as it moves')
    pg.evaluate("document.getAnimations().forEach(a=>a.play())")
    pg.wait_for_function(QUIET, timeout=15000)
    ok(pg.locator('.svd-tmp').count() == 0 and pg.evaluate("document.querySelector('#app .arch svg path[pathLength]').style.visibility") == '',
       'once landed, Today’s own arch is back with nothing left over')
    landed = {k: pg.evaluate(RECT, s) for k, s in PIECES.items()}
    pg.evaluate("rerender()")
    fresh = {k: pg.evaluate(RECT, s) for k, s in PIECES.items()}
    ok(all(abs(landed[k][x] - fresh[k][x]) < 0.6 for k in PIECES for x in 'ltwh'), 'every piece lands exactly on Today’s real layout')
    t.shot(pg, 'motion-today')
    pg.context.close()

    # a tap mid-morph still works: Start session starts a session
    pg = t.page(b, data=full(), init=MOTION_ON)
    finish(pg, 41)
    pg.wait_for_function(QUIET, timeout=15000)
    pg.evaluate("MOTION.setSpeed(4)")
    pg.click('[data-a=savedDone]')
    pg.click('#app [data-a=start]')
    ok(until(pg, "U.view==='found'&&!!X"), 'Start session can be tapped while it’s still moving')
    pg.evaluate("MOTION.setSpeed(1)")
    pg.context.close()


def fallback(b, t):
    """Where the morph can't land exactly, Today simply fades in."""
    ok = t.ok
    cases = [('no streak', none(), 390, 844, None), ('landscape', full(), 852, 393, None),
             ('larger page zoom', full(), 390, 844, "document.documentElement.style.zoom='1.35'")]
    for name, data, w, h, js in cases:
        pg = t.page(b, w=w, h=h, data=data, init=MOTION_ON)
        if js: pg.evaluate(js)
        finish(pg, 41)
        pg.wait_for_function(QUIET, timeout=15000)
        ok(pg.evaluate(WIDE), f'{name}: Session saved fits the width')
        t.shot(pg, 'fallback-' + name.replace(' ', '-'))
        was = {k: pg.evaluate(RECT, s) for k, s in SAVED_PIECES.items() if k != 'btn'}
        pg.click('[data-a=savedDone]')
        moved = pg.evaluate(ANIM, '#app .arch, #app .week, #app .streak')
        app = pg.evaluate(ANIM, '#app')
        if js and moved:
            # the zoomed page may still be one the morph can land on: then its first frame must be exactly the saved screen
            pg.evaluate("document.getAnimations().forEach(a=>{if(a.effect.getTiming().iterations!==Infinity){a.pause();a.currentTime=0}})")
            first = {k: pg.evaluate(RECT, s) for k, s in PIECES.items() if k != 'btn'}
            ok(all(abs(first[k]['t'] - was[k]['t']) < 2 and abs(first[k]['l'] - was[k]['l']) < 2 for k in first), f'{name}: it morphs from exactly where the pieces were')
            pg.evaluate("document.getAnimations().forEach(a=>a.play())")
        else:
            ok(not moved and app and all(a['k'] == 'opacity' for a in app), f'{name}: Today fades in, nothing tries to move')
        pg.wait_for_function(QUIET, timeout=15000)
        landed = {k: pg.evaluate(RECT, s) for k, s in PIECES.items()}
        pg.evaluate("rerender()")
        fresh = {k: pg.evaluate(RECT, s) for k, s in PIECES.items()}
        ok(pg.evaluate(WIDE) and pg.evaluate("U.view") is None and all(abs(landed[k][x] - fresh[k][x]) < 0.6 for k in PIECES for x in 'ltwh'),
           f'{name}: and Today is left exactly as it is')
        pg.context.close()


def reduce(b, t):
    ok = t.ok
    pg = t.page(b, data=full(), init=REDUCE_ON)
    finish(pg, 41)
    sv = pg.evaluate(ANIM, '#app [data-sv]')
    ok(len(sv) >= 6 and all(a['k'] == 'opacity' for a in sv) and pg.evaluate(ANIM, '#app .svd-new') == [] and pg.evaluate(ANIM, '#app .svd-now') == [],
       'Reduce Motion: the screen fades in; nothing draws, pops or rises')
    pg.wait_for_function(QUIET, timeout=15000)
    t.shot(pg, 'reduce')
    pg.click('[data-a=savedDone]')
    an = pg.evaluate(ANIM, '#app, #app *, #dock *')
    ok(an and all(a['k'] == 'opacity' for a in an), 'and Done fades into Today, with nothing moving')
    pg.wait_for_function(QUIET, timeout=15000)
    ok(pg.evaluate("U.view") is None, 'Today is there')
    pg.context.close()


def screens(b, t):
    ok = t.ok
    for w, h in [(390, 844), (375, 667)]:
        for sc in ['light', 'dark']:
            pg = t.page(b, w=w, h=h, sc=sc, data=full())
            finish(pg, 41)
            tag = f'{w} {sc}'
            r = pg.evaluate(RECT, '#app .svd-done')
            ok(pg.evaluate(WIDE) and r and r['b'] <= h and abs(r['l'] + r['w'] / 2 - w / 2) < 1, f'{tag}: fits, Done on screen and centred')
            t.shot(pg, f'{w}-{sc}')
            pg.click('[data-a=savedDone]')
            ok(until(pg, "U.view===null") and pg.evaluate(WIDE), f'{tag}: Today after Done fits')
            pg.context.close()


def run(b, t):
    print('-- numbers'); numbers(b, t)
    print('-- song practice'); song(b, t)
    print('-- motion'); motion(b, t)
    print('-- fallback'); fallback(b, t)
    print('-- reduce motion'); reduce(b, t)
    print('-- screens'); screens(b, t)
