"""Q10 · Interface: HIG Foundations Pass (3.26). The design foundations brought in line with Apple's HIG:
1 one named set of text sizes (every font-size in css/app.css comes from it), 2 Apple's system colours light and dark
with the app's own colours pointing at them (marker numbers tinted so their labels pass 4.5:1), 3 background layers
(a box inside a card is the darker grey with no outline; an empty value shows a faint dash), 4 the marker tiles
following their own side's width (three, two or one across), 5 a soft fade on whichever edge of a sideways row has
more behind it, 6 selected text in a wash of the accent, 7 All takes as fold-out section rows, 8 hover hints on
icon-only buttons with a mouse or trackpad only.
VS_HIG=sizes,colours,layers,adaptive,fade,select,fold,hints runs only those parts."""
import os, re
from harness import ROOT, UA_IPHONE
from test_layout import SONG

_only = [x for x in os.environ.get('VS_HIG', '').split(',') if x]
wanted = lambda k: not _only or k in _only
CSS = os.path.join(ROOT, 'css', 'app.css')

# a colour as computed by the browser (rgb(), rgba() or color(srgb …)) → (r, g, b, a) in 0–255
def rgba(s):
    s = s.strip()
    m = re.match(r'color\(srgb ([\d.e-]+) ([\d.e-]+) ([\d.e-]+)(?: / ([\d.e-]+))?\)', s)
    if m: return tuple(float(m.group(i)) * 255 for i in (1, 2, 3)) + (float(m.group(4) or 1),)
    m = re.match(r'rgba?\(([\d.]+), ([\d.]+), ([\d.]+)(?:, ([\d.]+))?\)', s)
    if m: return tuple(float(m.group(i)) for i in (1, 2, 3)) + (float(m.group(4) or 1),)
    raise ValueError(s)

def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])

def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)

def over(fg, bg):
    """fg (possibly see-through) laid over an opaque bg."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1,)

VAR = "k=>getComputedStyle(document.documentElement).getPropertyValue(k).trim()"
# a variable's resolved colour, as a real element computes it
RES = "k=>{const e=document.createElement('i');e.style.color='var('+k+')';document.body.appendChild(e);const c=getComputedStyle(e).color;e.remove();return c}"


def sizes(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    raw = [m.group(0) for m in re.finditer(r'font-size:\s*([^;]+);', css) if not re.fullmatch(r'var\(--t-[a-z0-9-]+\)|0', m.group(1).strip())]
    ok(not raw, f'every font-size in app.css is one of the named sizes ({len(raw)} others: {raw[:5]})')
    named = dict(re.findall(r'--(t-[a-z0-9-]+):\s*(\d+)px', css))
    apple = {'t-large': '34', 't-title1': '28', 't-title2': '22', 't-title3': '20', 't-body': '17', 't-callout': '16',
             't-subhead': '15', 't-footnote': '13', 't-caption1': '12', 't-caption2': '11'}
    ok(all(named.get(k) == v for k, v in apple.items()), f'the named set is Apple’s text styles ({named})')
    used = set(re.findall(r'var\(--(t-[a-z0-9-]+)\)', css))
    ok(used <= set(named), f'every size used is defined ({used - set(named)})')
    pg = t.page(b, 390, 844)
    ok(pg.evaluate("getComputedStyle(document.querySelector('#app h1')).fontSize") == '34px', 'a page title is Large Title, 34 px')
    ok(pg.evaluate("getComputedStyle(document.body).fontSize") == '17px', 'body text is 17 px')
    pg.close()


def colours(b, t):
    ok = t.ok
    want = {'light': {'--coral': (255, 59, 48), '--star': (255, 149, 0), '--pause': (255, 149, 0), '--cF': (88, 86, 214),
                      '--cR': (48, 176, 199), '--cA': (255, 149, 0), '--trk-mk': (175, 82, 222), '--trk-loop': (255, 149, 0)},
            'dark': {'--coral': (255, 69, 58), '--star': (255, 159, 10), '--pause': (255, 159, 10), '--cF': (94, 92, 230),
                     '--cR': (64, 200, 224), '--cA': (255, 159, 10), '--trk-mk': (191, 90, 242), '--trk-loop': (255, 159, 10)}}
    for sc in ['light', 'dark']:
        pg = t.page(b, 390, 844, sc)
        got = {k: tuple(round(x) for x in rgba(pg.evaluate(RES, k))[:3]) for k in want[sc]}
        bad = {k: v for k, v in got.items() if v != want[sc][k]}
        ok(not bad, f'{sc}: the app’s colours are Apple’s system colours ({bad})')
        ok(got['--cA'] == got['--trk-loop'], f'{sc}: the Progress gradient’s A stop is the loop’s orange')
        # marker numbers: a purple wash, a dark (or, in dark mode, light) number, a purple dot; the number passes 4.5:1
        pg.evaluate("""(()=>{const d=document.createElement('div');d.id='mkp';d.innerHTML='<div class=\"trkchb\"><b>3</b></div><div class=\"trktl\"><div class=\"trktlb\"><b>12</b></div></div><div class=\"trktl play\"><div class=\"trktlb\"><b>4</b></div></div>';document.getElementById('app').appendChild(d)})()""")
        surf = rgba(pg.evaluate(RES, '--surface'))
        for sel, what in [('#mkp .trkchb b', 'a chip’s number'), ('#mkp .trktl:not(.play) .trktlb b', 'a tile’s number'),
                          ('#mkp .trktl.play .trktlb b', 'the playing tile’s number')]:
            cs = pg.evaluate("s=>{const e=document.querySelector(s),c=getComputedStyle(e),d=getComputedStyle(e,'::before');return [c.color,c.backgroundColor,d.backgroundColor,d.width]}", sel)
            bg = over(rgba(cs[1]), surf)
            r = contrast(rgba(cs[0]), bg)
            ok(r >= 4.5, f'{sc}: {what} meets 4.5:1 on its wash ({r:.2f})')
            ok(cs[3] == '7px' and rgba(cs[2])[3] == 1, f'{sc}: {what} has its coloured dot')
        tab = contrast(rgba(pg.evaluate(RES, '--trk-mk-inkfg')), rgba(pg.evaluate(RES, '--trk-mk-ink')))
        ok(tab >= 4.5, f'{sc}: a numbered tab on the waveform meets 4.5:1 ({tab:.2f})')
        # the warning banner: an orange tint with dark (dark mode: light) text
        wb, wf = rgba(pg.evaluate(RES, '--warnbg')), rgba(pg.evaluate(RES, '--warnfg'))
        ok(contrast(wf, wb) >= 7, f'{sc}: warning text on its orange tint reads clearly ({contrast(wf, wb):.1f}:1)')
        ok(wb[0] > wb[1] > wb[2], f'{sc}: the warning tint is orange ({wb[:3]})')
        pg.close()


def layers(b, t):
    ok = t.ok
    for sc in ['light', 'dark']:
        pg = t.page(b, 390, 844, sc)
        bg, bg2, bg3 = (rgba(pg.evaluate(RES, k)) for k in ('--bg', '--bg2', '--bg3'))
        ok(bg2 == rgba(pg.evaluate(RES, '--surface')), f'{sc}: a card is the secondary grouped background')
        ok(bg3 != bg2 and lum(bg3) < lum(bg2) if sc == 'light' else lum(bg3) > lum(bg2), f'{sc}: a box inside a card is a different grey ({bg3[:3]})')
        pg.evaluate("""(()=>{const d=document.createElement('div');d.className='grp';d.id='lyp';d.innerHTML='<div class=\"row\"><span class=\"lbl\">Note</span><span class=\"mut\"></span></div><div class=\"row\"><span class=\"lbl\">Total</span><span class=\"mut\">35m</span></div><input class=\"ckin2\">';document.getElementById('app').appendChild(d)})()""")
        ok(pg.evaluate("getComputedStyle(document.querySelector('#lyp .row .mut:empty'),'::before').content").startswith('"—"'),
           f'{sc}: an empty value shows a dash')
        ok(pg.evaluate("getComputedStyle(document.querySelector('#lyp .row:nth-child(2) .mut'),'::before').content") in ('none', 'normal'),
           f'{sc}: a value that’s there shows no dash')
        dash = rgba(pg.evaluate("getComputedStyle(document.querySelector('#lyp .row .mut:empty'),'::before').color"))
        ok(dash[3] < 0.3, f'{sc}: the dash is faint (Apple’s quaternary label)')
        cs = pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('#lyp .ckin2'));return [c.backgroundColor,c.boxShadow]})()")
        ok(rgba(cs[0]) == bg3 and cs[1] == 'none', f'{sc}: the in-place title field inside its card is the darker grey with no outline')
        pg.close()


def adaptive(b, t):
    ok = t.ok
    for name, w, h in [('ipad', 1180, 820), ('mac', 1440, 900)]:
        pg = t.page(b, w, h, ua=None if name == 'mac' else UA_IPHONE)
        cols = pg.evaluate("""ws=>ws.map(w=>{const d=document.createElement('div');d.style.width=w+'px';
          d.innerHTML='<div class=\"trkgw\"><div class=\"trkgrid\"><i></i><i></i><i></i><i></i></div></div>';document.getElementById('app').appendChild(d);
          const n=getComputedStyle(d.querySelector('.trkgrid')).gridTemplateColumns.split(' ').length;d.remove();return n})""", [700, 540, 400, 300, 260])
        ok(cols == [3, 3, 2, 2, 1], f'{name}: marker tiles go 3 across with room, 2 on a phone’s width, 1 when narrow ({cols})')
        pg.close()


def fade(b, t):
    ok = t.ok
    pg = t.page(b, 390, 844, touch=True)
    pg.evaluate("""(()=>{const d=document.createElement('div');d.id='fx';d.setAttribute('data-edge-fade','');d.style.cssText='display:flex;gap:8px;overflow-x:auto;width:300px';
      d.innerHTML=Array.from({length:8},(_,i)=>'<span style=\"flex:none;width:90px;height:30px\">'+i+'</span>').join('');document.body.appendChild(d);
      const f=document.createElement('div');f.id='fy';f.setAttribute('data-edge-fade','');f.style.cssText='display:flex;overflow-x:auto;width:300px';f.innerHTML='<span style=\"width:90px\">a</span>';document.body.appendChild(f);render()})()""")
    pg.wait_for_timeout(100)
    cls = lambda s: pg.evaluate("s=>{const e=document.querySelector(s);return (e.classList.contains('fadel')?'L':'')+(e.classList.contains('fader')?'R':'')}", s)
    ok(cls('#fx') == 'R', f'at the start: a fade on the right only ({cls("#fx")})')
    pg.evaluate("document.getElementById('fx').scrollLeft=200"); pg.wait_for_timeout(100)
    ok(cls('#fx') == 'LR', f'in the middle: a fade on both sides ({cls("#fx")})')
    pg.evaluate("const e=document.getElementById('fx');e.scrollLeft=e.scrollWidth"); pg.wait_for_timeout(100)
    ok(cls('#fx') == 'L', f'at the end: the right fade goes ({cls("#fx")})')
    ok(cls('#fy') == '', 'a row that fits has no fade')
    pg.wait_for_timeout(400)
    m = pg.evaluate("getComputedStyle(document.getElementById('fx')).webkitMaskImage||getComputedStyle(document.getElementById('fx')).maskImage")
    ok('linear-gradient' in m and '32px' in m, f'the fade is a soft mask on the edge ({m[:80]})')
    pg.evaluate("document.documentElement.classList.add('motion-reduced')")
    tp = pg.evaluate("getComputedStyle(document.getElementById('fx')).transitionProperty")
    ok('--fade' not in tp, f'Reduce Motion: the fade switches without easing ({tp})')
    pg.close()


def select(b, t):
    ok = t.ok
    for sc in ['light', 'dark']:
        pg = t.page(b, 390, 844, sc)
        pg.evaluate("""(()=>{const d=document.createElement('div');d.innerHTML='<textarea id=\"sx\"></textarea><div id=\"sy\" contenteditable=\"true\">la la</div><p id=\"sz\">x</p>';document.getElementById('app').appendChild(d)})()""")
        acc = rgba(pg.evaluate(RES, '--accent'))
        for sel, what in [('#sx', 'a text field'), ('#sy', 'the lyrics editor')]:
            c = rgba(pg.evaluate("s=>getComputedStyle(document.querySelector(s),'::selection').backgroundColor", sel))
            ok(abs(c[0] - acc[0]) < 2 and abs(c[2] - acc[2]) < 2 and 0.1 < c[3] < 0.35, f'{sc}: selected text in {what} is a light wash of the accent ({c})')
            ok(rgba(pg.evaluate("s=>getComputedStyle(document.querySelector(s)).caretColor", sel))[:3] == acc[:3], f'{sc}: {what}’s caret is the accent')
        pg.close()


TK = """(async()=>{const s=songById(U.songId),b=new Blob([new Uint8Array(3000)],{type:'audio/mp4'});let n=0;
 for(const [oi,k] of [[0,2],[1,3],[2,1]]) for(let j=0;j<k;j++){n++;await putTake({id:'q'+n,songId:s.id,o:s.order[oi].o,created:Date.now()-n*864e5,len:15,size:3000,type:'audio/mp4',blob:b,star:false});}
 await refreshTakes();render();})()"""
HEADS = "[...document.querySelectorAll('#layer .tkfh')].map(b=>b.querySelector('.lbl').textContent+'|'+b.querySelector('.mut').textContent+'|'+b.getAttribute('aria-expanded'))"


def fold(b, t):
    ok = t.ok
    pg = t.page(b, 390, 844, touch=True)
    pg.evaluate(SONG); pg.evaluate(TK); pg.wait_for_timeout(300)
    pg.evaluate("SG_ACT.tkOpenAll(null,null,U.songId)"); pg.wait_for_timeout(400)
    ok(pg.evaluate(HEADS) == ['Verse|2 takes|false', 'Chorus 1|3 takes|false', 'Chorus 2|1 take|false'],
       f'All takes: a row per section in song order, with its count, all folded ({pg.evaluate(HEADS)})')
    ok(pg.locator('#layer .tkr').count() == 0, 'folded: no takes showing')
    pg.click('#layer .tkfh >> nth=1'); pg.wait_for_timeout(400)
    ok(pg.evaluate(HEADS)[1].endswith('|true') and pg.locator('#layer .tkfin .tkr').count() == 3, 'tapping Chorus 1 folds its three takes open')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#layer .tkfold.open .tkchev')).transform") != 'none', 'its chevron turns down')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#layer .tkfold:not(.open) .tkchev')).color") == pg.evaluate(RES, '--accent'), 'the chevron is tinted')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#layer .tkfin .tkfg')).backgroundColor") == pg.evaluate(RES, '--bg3'),
       'the takes inside sit on the darker grey')
    # a take inside plays and expands as before
    pg.click('#layer .tkfin .tkr >> nth=0 >> .tkhead'); pg.wait_for_timeout(400)
    ok(pg.locator('#layer .tkr.open').count() == 1, 'a take inside expands')
    pg.click('#layer .tkfh >> nth=0'); pg.wait_for_timeout(400)
    ok(pg.evaluate(HEADS)[0].endswith('|true') and pg.evaluate(HEADS)[1].endswith('|true'), 'more than one section can be open')
    pg.click('#layer .tkfh >> nth=1'); pg.wait_for_timeout(500)
    ok(pg.evaluate(HEADS)[1].endswith('|false') and pg.locator('#layer .tkr.open').count() == 0, 'folding a section shut collapses its expanded take')
    # from a section: All takes opens with that section folded open; the section's own tab is a plain list
    pg.evaluate("U.sheet=null;rerender()"); pg.wait_for_timeout(300)
    pg.evaluate("const s=songById(U.songId);U.sheet='sgTakes';U.sd={k:s.id,o:s.order[2].o};rerender()"); pg.wait_for_timeout(400)
    ok(pg.locator('#layer .tkfh').count() == 0 and pg.locator('#layer .tkr').count() == 1, 'a section’s own tab stays a plain list')
    pg.click('#layer [data-a=tkTab][data-v=all]'); pg.wait_for_timeout(400)
    ok(pg.evaluate(HEADS)[2].endswith('|true') and sum(h.endswith('|true') for h in pg.evaluate(HEADS)) == 1,
       f'switching to All takes opens the section it came from ({pg.evaluate(HEADS)})')
    # Search opens a take: its section is open and the take expanded
    pg.evaluate("U.sheet=null;rerender()"); pg.wait_for_timeout(300)
    pg.evaluate("TAKE.openAt('q2')"); pg.wait_for_timeout(500)
    ok(pg.evaluate(HEADS)[0].endswith('|true') and pg.locator('#layer .tkr.open[data-tk=q2]').count() == 1, 'a take opened from Search shows inside its open section')
    pg.close()
    # a song whose takes are all in one section: a plain list, as before
    pg = t.page(b, 390, 844, touch=True)
    pg.evaluate(SONG)
    pg.evaluate("""(async()=>{const s=songById(U.songId),b=new Blob([new Uint8Array(3000)],{type:'audio/mp4'});
      for(const id of ['p1','p2']) await putTake({id,songId:s.id,o:s.order[1].o,created:Date.now()-864e5,len:12,size:3000,type:'audio/mp4',blob:b});await refreshTakes();render()})()""")
    pg.wait_for_timeout(300); pg.evaluate("SG_ACT.tkOpenAll(null,null,U.songId)"); pg.wait_for_timeout(400)
    ok(pg.locator('#layer .tkfh').count() == 0 and pg.locator('#layer .tkr').count() == 2, 'takes from one section only: a plain list')
    pg.close()


def hints(b, t):
    ok = t.ok
    shown = "(()=>{const h=document.getElementById('hint');return h&&h.classList.contains('show')?h.textContent:''})()"
    pg = t.page(b, 1440, 900, ua=None)
    pg.evaluate("U.tab='history';render()"); pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(300)
    back = '#barL .circ'
    pg.hover(back); pg.wait_for_timeout(250)
    ok(pg.evaluate(shown) == '', 'no hint straight away')
    pg.wait_for_timeout(600)
    ok(pg.evaluate(shown) == pg.get_attribute(back, 'aria-label'), f'resting on Back shows its label ({pg.evaluate(shown)!r})')
    r, hr = pg.evaluate("[document.querySelector('#barL .circ').getBoundingClientRect().bottom,document.getElementById('hint').getBoundingClientRect().top]")
    ok(hr > r, 'a top bar hint sits below its button')
    ok(pg.evaluate("(()=>{const r=document.getElementById('hint').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})()"), 'the hint stays on screen')
    pg.mouse.move(700, 600); pg.wait_for_timeout(250)
    ok(pg.evaluate(shown) == '', 'moving away hides it')
    pg.hover(back); pg.wait_for_timeout(900); pg.mouse.down(); pg.wait_for_timeout(50)
    ok(pg.evaluate(shown) == '', 'pressing the button hides it')
    pg.mouse.up(); pg.wait_for_timeout(300)
    ok(pg.locator('#hint.show').count() == 0, 'no hint left behind after the page changes')
    # the search circle and an ordinary row get / don't get hints
    pg.evaluate("U.view=null;U.tab='today';render()"); pg.wait_for_timeout(300)
    if pg.locator('.scirc').count():
        pg.hover('.scirc >> nth=0'); pg.wait_for_timeout(900)
        ok(pg.evaluate(shown) == pg.get_attribute('.scirc >> nth=0', 'aria-label'), 'the search circle has a hint')
    pg.hover('[data-a=start]'); pg.wait_for_timeout(900)
    ok(pg.evaluate(shown) == '', 'a button with its own words has no hint')
    pg.close()
    # touch: never
    pg = t.page(b, 390, 844, touch=True)
    pg.evaluate("U.tab='history';render()"); pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(300)
    pg.evaluate("""(()=>{const b=document.querySelector('#barL .circ');b.dispatchEvent(new PointerEvent('pointerover',{bubbles:true,pointerType:'touch'}))})()""")
    pg.wait_for_timeout(900)
    ok(pg.evaluate(shown) == '', 'a touch never shows a hint')
    pg.close()


def run(b, t):
    if wanted('sizes'): sizes(b, t)
    if wanted('colours'): colours(b, t)
    if wanted('layers'): layers(b, t)
    if wanted('adaptive'): adaptive(b, t)
    if wanted('fade'): fade(b, t)
    if wanted('select'): select(b, t)
    if wanted('fold'): fold(b, t)
    if wanted('hints'): hints(b, t)
