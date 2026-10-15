"""Problems found in the 3.3.2 audit. Each check here once failed; they must stay fixed."""
from harness import sample, ready

TOUCH = """(a)=>{const [type,y,sel]=a;const el=document.querySelector(sel)||document.body;const t=new Touch({identifier:3,target:el,clientX:600,clientY:y});
  const e=new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true});el.dispatchEvent(e);return e.defaultPrevented}"""

def run(b, t):
    ok = t.ok
    # saved data that is literally "null"
    pg = t.page(b, data=None); pg.evaluate("localStorage.setItem('vocalTracker','null')"); pg.reload(); ready(pg)
    ok(pg.locator('[data-a=start]').count() == 1, 'the app starts when saved data is "null"')
    pg.context.close()

    # storage full from the very start
    pg = t.page(b, data=None, init="Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError')}")
    ok(pg.locator('[data-a=start]').count() == 1, 'the app starts when storage is full')
    pg.context.close()

    # a damaged backup must never break the app
    pg = t.page(b)
    pg.evaluate("pendingImport={p:{app:'vocal-sessions',data:{sessions:'oops',months:5,songs:null},takes:[]}};restoreImport()"); pg.wait_for_timeout(600)
    ok(pg.locator('[data-a=tab]').count() > 0, 'the app still works after restoring damaged data')
    pg.context.close()

    # iPad: scrolling a detail pane back up must not pull to refresh
    pg = t.page(b, 820, 1180, touch=True)
    pg.click('[data-a=tab][data-v=history]'); pg.wait_for_timeout(200); pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('.pane').style.maxHeight='300px';document.querySelector('.pane').scrollTop=200")
    pg.evaluate(TOUCH, ['touchstart', 400, '.pane'])
    prev = [pg.evaluate(TOUCH, ['touchmove', 400 + i * 15, '.pane']) for i in range(1, 6)]
    pg.evaluate(TOUCH, ['touchend', 475, '.pane'])
    ok(not any(prev) and not pg.evaluate("PTR.busy"), 'iPad: scrolling a detail pane back up does not pull to refresh')
    pg.context.close()

    # pull to refresh only ever moves to a newer version
    pg = t.page(b)
    ok(pg.evaluate("cmpVer('3.10','3.9')>0 && cmpVer('3.5','3.5.1')<0 && cmpVer('3.6','3.6')===0"), 'version comparison orders 3.10 after 3.9')
    # Edit refuses nonsense minutes
    pg.click('[data-a=tab][data-v=history]'); pg.click('[data-v=session] >> nth=0'); pg.wait_for_timeout(500); pg.click('.shead [data-a=editSess]'); pg.wait_for_timeout(500)
    before = pg.evaluate("E&&E.mins")
    pg.fill('#edMins', '-40'); pg.click('[data-a=saveEdit]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.evaluate("D.sessions.every(s=>s.mins>0)"), 'Edit refuses -40 minutes')
    pg.context.close()

    # a sheet with nothing to show closes instead of hiding the tab bar
    pg = t.page(b); pg.evaluate("U.sheet='takeNote';U.sd={k:'gone'};rerender()")
    ok(pg.locator('[data-a=tab]').count() > 0 and pg.evaluate("U.sheet") is None, 'a sheet with nothing to show closes itself')
    pg.context.close()

    # sessions saved out of order are shown in date order
    d = sample(); d['sessions'] = [d['sessions'][2], d['sessions'][0], d['sessions'][1]]
    pg = t.page(b, data=d); pg.click('[data-a=tab][data-v=history]'); pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(300)
    hd = pg.locator('main .hdr').all_inner_texts()
    ok(len(hd) == len(set(hd)), 'All sessions never repeats a month heading')

    # coming back to the app refreshes the screen (so Today shows the right date next morning)
    n = pg.evaluate("""(()=>{let n=0;const r=window.render;window.render=function(k){n++;return r(k)};
      Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'));window.render=r;return n})()""")
    ok(n > 0, 'returning to the app redraws the screen with the current date')

    # the sliding picker knob must not push the page sideways
    ok(pg.evaluate("getComputedStyle(document.documentElement).overflowX==='clip'&&getComputedStyle(document.body).overflowX==='clip'"),
       'the page clips sideways overflow, so picker bounces never shift it')
    pg.context.close()
