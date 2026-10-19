"""3.11: the shared springs (js/motion.js) and the lyrics page. One continuous page with no section cards; tapping a
section gives it a soft patch with Record, Takes and Marks while everything else dims and blurs with distance (at most
1.5 px, labels never blurred); tapping away or the same section again clears it; Reduce Motion means dim only; Recall
focuses from the label; the focus fades ease because the page is updated in place, not redrawn."""
from harness import with_song_practice
from test_sections import LYR, ADD

# every lyric row's place, focus state and look, in reading order
ROWS = """()=>[...document.querySelectorAll('.sgsong .sgsec')].flatMap(s=>[...s.querySelectorAll('.sghead,.sgcue,.sgl,.sgnote')].map(e=>{
  const c=getComputedStyle(e),m=/blur\\(([\\d.]+)px\\)/.exec(c.filter);return {o:s.dataset.o,sel:s.classList.contains('sel'),
  label:e.classList.contains('sghead'),op:+c.opacity,blur:m?+m[1]:0}}))"""
BG = "o=>getComputedStyle(document.querySelector(`.sgsec[data-o='${o}']`)).backgroundColor"
CLEAR = 'rgba(0, 0, 0, 0)'


def open_song(t, b, **kw):
    pg = t.page(b, touch=True, data=with_song_practice(), **kw)
    pg.evaluate("U.tab='songs';render()")
    S = pg.evaluate(ADD, LYR)
    pg.wait_for_timeout(300)
    return pg, S


def run(b, t):
    ok = t.ok
    pg, S = open_song(t, b)
    o = S['o']
    sec = lambda x: f'.sgsec[data-o="{x}"]'

    # the shared springs
    m = pg.evaluate("""()=>({names:Object.keys(MOTION.SPRINGS),ease:MOTION.ease('nav'),gentle:MOTION.curve(.82,1.9).ms,
      nav:MOTION.curve(.86,2.2).ms,cap:MOTION.BLUR_MAX,speed:MOTION.speed(),off:document.documentElement.classList.contains('motion-off'),
      dur:getComputedStyle(document.documentElement).getPropertyValue('--dur-gentle').trim(),stag:[MOTION.stagger(2,'word'),MOTION.stagger(2,'row')]})""")
    ok(m['names'] == ['gentle', 'nav', 'ripple'] and m['ease'].startswith('linear('), 'three shared springs, as linear() easings')
    ok(m['nav'] < m['gentle'], 'the navigation spring is a little quicker than the gentle one')
    ok(m['cap'] == 1.5, 'distance blur is capped at 1.5 px')
    ok(m['speed'] == 0 and m['off'] and m['dur'] == '0ms', 'tests run with motion off, so nothing waits on a spring')
    ok(m['stag'] == [60, 90], 'staggers are 30 ms a word and 45 ms a row (MOTION.animate applies the speed, 3.13)')
    pg.evaluate("MOTION.setSpeed(4)")
    m2 = pg.evaluate("[localStorage.getItem('vocalMotion'),MOTION.dur('gentle')===MOTION.curve(.82,1.9).ms*4,MOTION.stagger(1,'word')]")
    ok(m2 == ['4', True, 30], 'slow motion multiplies every spring (staggers through MOTION.animate), and is kept on this device')
    pg.evaluate("MOTION.setSpeed(0)")
    ok(pg.evaluate("MOTION.blur(0)===0&&MOTION.blur(1)<MOTION.blur(3)&&MOTION.blur(9)===1.5&&MOTION.dim(1)>MOTION.dim(4)&&MOTION.dim(20)===.3"),
       'blur grows and opacity falls with distance, within their limits')

    # one continuous page
    ok(pg.locator('.sgsong .sgsec').count() == len(o) and all(pg.evaluate(BG, x) == CLEAR for x in o),
       'no section cards: sections have no background of their own')
    ok(pg.locator('.sgsong .sglab').count() == len(o), 'every section keeps its label')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.sgsong .sgl')).fontSize") == '17px', 'lyrics are body size')
    rows = pg.evaluate(ROWS)
    ok(all(r['op'] == 1 and r['blur'] == 0 for r in rows), 'with nothing focused, nothing is dimmed or blurred')
    t.shot(pg, 'page')

    # focus a section
    keep = pg.evaluate_handle(f"document.querySelector('{sec(o[2])} .sgl')")
    pg.click(sec(o[2]) + ' .sgl >> nth=1'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sSec") == o[2] and pg.evaluate(BG, o[2]) != CLEAR, 'tapping a section gives it a soft patch')
    ok(pg.evaluate(f"document.querySelector('{sec(o[2])}').getBoundingClientRect().width") > 300, 'the patch spans the page')
    btns = pg.locator(sec(o[2]) + ' .sgrecp button').all_inner_texts()
    ok(btns[0].strip() == 'Record' and btns[-1].strip() == 'Marks', 'its controls are Record, then Takes when there are any, then Marks')
    ok(pg.evaluate("(e)=>e.isConnected", keep), 'focusing updates the page in place, so the lines stay put and can ease')
    rows = pg.evaluate(ROWS)
    own = [r for r in rows if r['sel']]
    far = [r for r in rows if not r['sel'] and not r['label']]
    labels = [r for r in rows if not r['sel'] and r['label']]
    ok(own and all(r['op'] == 1 and r['blur'] == 0 for r in own), 'the focused section stays sharp')
    ok(far and all(r['op'] < 1 and 0 < r['blur'] <= 1.5 for r in far), 'every other line is dimmed and blurred, never past 1.5 px')
    ok(labels and all(r['blur'] == 0 and r['op'] < 1 for r in labels), 'other labels dim but never blur')
    idx = [i for i, r in enumerate(rows) if r['sel']]
    after = [r for r in rows[idx[-1] + 1:] if not r['label']]
    ok(all(after[i]['blur'] <= after[i + 1]['blur'] for i in range(len(after) - 1)) and after[0]['blur'] < after[-1]['blur'],
       'the blur grows with distance from the focused section')
    ok(min(r['op'] for r in far) >= 0.3, 'nothing fades below 0.3, so far lyrics stay recognisable')
    t.shot(pg, 'focused')

    # move it, then clear it
    pg.click(sec(o[4]) + ' .sglab'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sSec") == o[4] and pg.locator('.sgsec.sel').count() == 1 and pg.locator('.sgrecp').count() == 1,
       'tapping another section moves the focus and its controls')
    pg.click(sec(o[4]) + ' .sglab'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sSec") is None and all(r['op'] == 1 and r['blur'] == 0 for r in pg.evaluate(ROWS)),
       'tapping the same section again lets it melt back')
    ok('Tap a section to record it' in pg.inner_text('main'), 'the hint comes back when nothing is focused')
    pg.click(sec(o[1]) + ' .sglab'); pg.wait_for_timeout(150)
    ok('Tap a section to record it' not in pg.inner_text('main'), 'the hint goes while a section is focused')
    pg.click('main h1'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sSec") is None and pg.locator('.sgsong.focused').count() == 0, 'tapping away clears the focus')

    # focus survives a redraw, without easing again
    pg.click(sec(o[1]) + ' .sglab'); pg.wait_for_timeout(150)
    pg.evaluate("rerender()")
    rows = pg.evaluate(ROWS)
    ok(pg.locator('.sgsec.sel').count() == 1 and any(r['blur'] > 0 for r in rows), 'the focus is kept when the screen redraws')

    # Marks: Annotate, at that section
    pg.evaluate("scrollTo(0,0)")
    pg.click(sec(o[1]) + ' [data-a=sgMarks]'); pg.wait_for_timeout(900)
    top = pg.evaluate(f"document.querySelector('{sec(o[1])}').getBoundingClientRect().top")
    ok(pg.evaluate("U.sEdit") == 'annotate' and pg.evaluate("U.sSec") is None and 0 < top < 260,
       'Marks opens Annotate, scrolled to that section')
    ok(pg.evaluate("[...document.querySelectorAll('.sgsong .sgsec')].every(s=>getComputedStyle(s).backgroundColor==='rgba(0, 0, 0, 0)')"),
       'Annotate is the continuous page too')
    pg.click('[data-a=sgEditMode][data-v=lyrics]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("getComputedStyle(document.querySelector('.lyred').closest('.sgsec')).backgroundColor") != CLEAR,
       'the lyrics editor keeps its cards for editing')
    pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)

    # Recall: lines peek, labels focus
    pg.click('[data-a=sgMode][data-v=recall]'); pg.wait_for_timeout(400)
    pg.click('[data-a=sgHint][data-v="1"]'); pg.wait_for_timeout(200)
    pg.click(sec(o[2]) + ' .sgl >> nth=0'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sSec") is None and pg.locator(sec(o[2]) + ' .sgl.peeking').count() == 1, 'in Recall, tapping a line peeks')
    pg.click(sec(o[2]) + ' .sglab'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sSec") == o[2] and any(r['blur'] > 0 for r in pg.evaluate(ROWS)), 'in Recall, tapping a label focuses the section')
    t.shot(pg, 'recall-focused')
    pg.context.close()

    # Reduce Motion: dim only, no blur, no easing
    pg, S = open_song(t, b, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}", ctx_args={'reduced_motion': 'reduce'})
    pg.click(f'.sgsec[data-o="{S["o"][3]}"] .sglab'); pg.wait_for_timeout(100)
    rows = pg.evaluate(ROWS)
    ok(all(r['blur'] == 0 for r in rows) and any(r['op'] < 1 for r in rows), 'with Reduce Motion, other sections dim but never blur')
    # 3.14: Reduce Motion no longer switches transitions off; changes fade over about 0.2 s and nothing moves or blurs
    ok(pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('.sgsong .sgl'));const d=c.transitionDuration.split(',').map(parseFloat),p=c.transitionProperty.split(',').map(x=>x.trim());return d.every(x=>x>0&&x<=0.25)&&p.includes('opacity')&&!p.includes('filter')&&!p.includes('transform')})()"),
       'with Reduce Motion, the focus changes with a short fade, no blur or movement')
    pg.context.close()

    # motion on: the focus eases on the gentle spring
    pg, S = open_song(t, b, init="try{localStorage.setItem('vocalMotion','1')}catch(e){}")
    ok(pg.evaluate("MOTION.on()") and pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--dur-gentle').trim()") != '0ms',
       'motion is on for everyone else')
    pg.click(f'.sgsec[data-o="{S["o"][0]}"] .sglab'); pg.wait_for_timeout(60)
    mid = pg.evaluate(f"+getComputedStyle(document.querySelector('.sgsec[data-o=\"{S['o'][5]}\"] .sgl')).opacity")
    pg.wait_for_timeout(900)
    end = pg.evaluate(f"+getComputedStyle(document.querySelector('.sgsec[data-o=\"{S['o'][5]}\"] .sgl')).opacity")
    ok(end < mid < 1, 'with motion on, the far lines fade gradually rather than snapping')
    pg.context.close()

    # every size, light and dark, with a section focused
    for w, h, name in [(390, 844, 'iphone'), (375, 667, 'small'), (852, 393, 'landscape'), (820, 1180, 'ipad'), (1440, 900, 'mac')]:
        for sc in ('light', 'dark'):
            pg, S = open_song(t, b, w=w, h=h, sc=sc)
            pg.click(f'.sgsec[data-o="{S["o"][1]}"] .sglab'); pg.wait_for_timeout(150)
            ov = pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
            pat = pg.evaluate(f"(()=>{{const s=document.querySelector('.sgsec[data-o=\"{S['o'][1]}\"]').getBoundingClientRect();return s.left>=0&&s.right<=innerWidth}})()")
            ok(not ov and pat and pg.locator('.sgsec.sel [data-a=sgRec]').count() == 1, f'{name} {sc}: focused page fits, with its controls')
            t.shot(pg, f'{name}-{sc}')
            pg.context.close()
