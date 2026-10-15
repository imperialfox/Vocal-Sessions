"""Every screen at every size: iPhone (two sizes, portrait and landscape), iPad both ways and Mac, light and dark.
Also pull to refresh and the keyboard shortcuts. Screenshots of each go to tests/output/."""
from harness import with_song_practice

SIZES = [('iphone', 390, 844, True), ('iphone-small', 375, 667, True), ('iphone-se', 320, 568, True), ('landscape', 852, 393, True),
         ('ipad', 820, 1180, True), ('ipad-landscape', 1180, 820, True), ('mac', 1440, 900, False)]

FITS = "document.documentElement.scrollWidth<=innerWidth"
BAR_IN = "(()=>{const b=document.querySelector('.tabbar,.toptabs,.side .sbi');if(!b)return true;const r=b.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+0.5})()"

TOUCH = """(a)=>{const [type,y]=a;const t=new Touch({identifier:1,target:document.body,clientX:200,clientY:y});
  const e=new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true});document.body.dispatchEvent(e);return e.defaultPrevented}"""

def run(b, t):
    ok = t.ok
    data = with_song_practice()
    for name, w, h, touch in SIZES:
        for sc in ['light', 'dark']:
            pg = t.page(b, w, h, sc, touch=touch, data=data, **({'ua': None} if name == 'mac' else {}))
            tag = f'{name}-{sc}'
            bad = []
            def check(screen):
                if not pg.evaluate(FITS): bad.append(screen + ' scrolls sideways')
                if not pg.evaluate(BAR_IN): bad.append(screen + ' tabs off screen')
                t.shot(pg, f'{tag}-{screen}')
            check('today')
            for tab in ['history', 'exercises', 'settings']:
                pg.evaluate(f"U.tab='{tab}';U.view=null;render()"); pg.wait_for_timeout(250); check(tab)
            pg.evaluate("U.tab='history';render()"); pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(250); check('all-sessions')
            pg.evaluate("U.view=null;U.tab='today';render()"); pg.click('[data-a=openCal]'); pg.wait_for_timeout(600); check('calendar')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            pg.click('[data-a=start]'); pg.wait_for_timeout(300); check('foundation')
            pg.click('#timer'); pg.wait_for_timeout(700); check('clock'); pg.click('.cbtn.hide'); pg.wait_for_timeout(400)
            pg.evaluate("U.view='rot';render()"); pg.wait_for_timeout(250); check('rotation')
            pg.evaluate("U.view='app';render()"); pg.wait_for_timeout(250); check('application')
            pg.evaluate("U.view='found';render()"); pg.click('[data-a=exit]'); pg.wait_for_timeout(200)
            ok(not bad, f'{tag}: every screen fits' + (' — ' + '; '.join(bad) if bad else ''))
            if sc == 'light' and name in ('ipad', 'ipad-landscape', 'mac'):
                pg.evaluate("U.tab='history';render()"); pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(300)
                ok(pg.locator('.pane .ph').count() == 1, f'{name}: All sessions has a detail pane')
                pg.click('[data-v=session] >> nth=1'); pg.wait_for_timeout(300)
                ok(pg.evaluate("U.sheet") is None and pg.locator('.row.sel').count() == 1, f'{name}: tapping a session fills the pane')
                pg.evaluate("U.view=null;U.tab='exercises';render()"); pg.wait_for_timeout(200)
                pg.click('[data-a=openEx][data-k=rung]'); pg.wait_for_timeout(300)
                ok('Singing on the rung' in pg.inner_text('.pane'), f'{name}: an exercise opens in the pane')
            if name == 'mac' and sc == 'light':
                pg.keyboard.press('Control+2'); pg.wait_for_timeout(200); ok(pg.evaluate("U.tab") == 'history', 'Mac: Cmd/Ctrl+2 opens Progress')
            pg.context.close()

    # pull to refresh on iPhone
    pg = t.page(b, touch=True)
    def drag(y0, y1, steps=10):
        pg.evaluate(TOUCH, ['touchstart', y0])
        for i in range(1, steps + 1): pg.evaluate(TOUCH, ['touchmove', y0 + (y1 - y0) * i / steps])
    drag(200, 330)
    ok(pg.evaluate("parseFloat(document.getElementById('app').style.transform.replace(/[^0-9.]/g,''))") > 0, 'pull to refresh: the page follows your finger')
    pg.evaluate(TOUCH, ['touchend', 330]); pg.wait_for_timeout(500)
    ok(not pg.evaluate("PTR.busy") and pg.evaluate("document.getElementById('app').style.transform") == '', 'a short pull springs back')
    pg.evaluate("D.sessions.push({id:'zz',date:new Date().toISOString(),mins:5,f:{},rot:{},takes:[]});localStorage.setItem('vocalTracker',JSON.stringify(D));D.sessions.pop()")
    drag(200, 520); pg.evaluate(TOUCH, ['touchend', 520]); pg.wait_for_timeout(300); ok(pg.evaluate("PTR.busy"), 'a long pull refreshes')
    pg.wait_for_timeout(1300); ok(not pg.evaluate("PTR.busy") and pg.evaluate("D.sessions.some(s=>s.id==='zz')"), 'refreshing re-reads saved data')
    pg.click('[data-a=tab][data-v=exercises]'); drag(200, 520); pg.evaluate(TOUCH, ['touchend', 520]); pg.wait_for_timeout(200)
    ok(not pg.evaluate("PTR.busy"), 'no pull to refresh on Exercises')
