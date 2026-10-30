"""Settings › Changelog: built from CHANGELOG.md, so every version in the file must appear on the page."""
import os, re
from harness import ROOT

def run(b, t):
    ok = t.ok
    md = open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read()
    versions = re.findall(r'^## (\d+(?:\.\d+)+) · ', md, re.M)
    pg = t.page(b, data=None)
    p = pg.evaluate("t=>{const r=parseChangelog(t);return {n:r.out.length,warn:r.warn,items:r.out.reduce((n,e)=>n+e.notes.reduce((m,s)=>m+s[1].length,0),0),untitled:r.out.filter(e=>!e.title).map(e=>e.v)}}", md)
    ok(p['n'] == len(versions) and not p['warn'] and not p['untitled'], f'CHANGELOG.md reads cleanly: {p["n"]} versions, {p["items"]} changes' + (f' — {p["warn"]}' if p['warn'] else ''))

    pg.evaluate("U.tab='settings';render()"); pg.wait_for_timeout(200)
    ok(pg.locator('main [data-a=openLog]').count() == 2, 'Settings has a Changelog row and a tappable version line')
    pg.click('.row[data-a=openLog]'); pg.wait_for_function("LOG_STATE==='ready'", timeout=8000); pg.wait_for_timeout(1300)
    ok(pg.evaluate("U.view") == 'log', 'Changelog opens')
    shown = pg.evaluate("[...document.querySelectorAll('.tl-item .tl-v')].map(e=>e.textContent)")
    ok(shown == versions, f'every version appears, newest first ({len(shown)})')
    ok(pg.locator('.tl-item.now .tl-v').inner_text() == pg.evaluate("APP_VERSION"), 'this version is marked')
    ok(pg.locator('.tl-era').count() == len({v.split('.')[0] for v in versions}), 'one era heading per major version')
    total = pg.inner_text('#lgtop .bignum b')
    ok(total == str(p['items']), f'the growth chart counts every change ({total})')
    ok(pg.locator('#lgchart circle').count() == len(versions), 'the chart has a point for every version')
    t.shot(pg, 'top')
    ok(not pg.evaluate("document.documentElement.scrollWidth>innerWidth"), 'no sideways scroll')

    # pick a version on the chart, then jump to it
    pg.click('#lgchart rect[data-k="5"]', force=True); pg.wait_for_timeout(300)
    v5 = list(reversed(versions))[5]
    ok(pg.inner_text('#lgtop .kick').upper().startswith(f'VERSION {v5}'), f'tapping the chart shows version {v5}')
    pg.click('[data-a=lgjump]')
    # the smooth scroll takes longer the further it goes (the timeline grows with every version), so wait for it to land
    sel = f"log-{v5.replace('.', '-')}"
    try:
        pg.wait_for_function("id=>{const t=document.getElementById(id).getBoundingClientRect().top;return t>0&&t<300}", arg=sel, timeout=5000)
    except Exception:
        pass
    top = pg.evaluate(f"document.getElementById('{sel}').getBoundingClientRect().top")
    ok(0 < top < 300, 'Show in timeline scrolls to that version')

    # expand one, then every change
    first = pg.locator('[data-a=logMore]').first; k = first.get_attribute('data-k')
    n_before = pg.locator(f'#log-{k.replace(".", "-")} .tl-list > li').count()
    first.click(); pg.wait_for_timeout(400)
    n_after = pg.locator(f'#log-{k.replace(".", "-")} .tl-list > li').count()
    ok(n_after > n_before, f'Show all opens every change in {k} ({n_before} → {n_after})')
    pg.evaluate("scrollTo(0,0)"); pg.click('[data-a=logMode][data-v=all]'); pg.wait_for_timeout(500)
    ok(pg.locator('.tl-item .tl-list > li').count() == p['items'] and pg.locator('[data-a=logMore]').count() == 0, 'Every change shows them all')
    ok(pg.locator('.tl-sub li').count() > 0 and pg.locator('.tl-list b').count() > 0, 'sub-points and bold words from the file are kept')
    t.shot(pg, 'every-change', full_page=True)
    pg.click('[data-a=logBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") is None and pg.evaluate("U.tab") == 'settings', 'back returns to Settings')
    pg.click('main button.setfoot[data-a=openLog]'); pg.wait_for_timeout(600); ok(pg.evaluate("U.view") == 'log', 'the app’s icon and version at the bottom open it too')
    pg.context.close()

    # a missing file shows a way to retry instead of breaking
    pg = t.page(b, data=None, ctx_args={'service_workers': 'block'})  # no saved copy to fall back on
    pg.route('**/CHANGELOG.md', lambda r: r.abort())
    pg.evaluate("U.tab='settings';render()"); pg.click('.row[data-a=openLog]'); pg.wait_for_function("LOG_STATE==='error'", timeout=8000); pg.wait_for_timeout(200)
    ok(pg.locator('[data-a=logRetry]').count() == 1, 'if the changelog can’t load, Try again is offered')
    pg.unroute('**/CHANGELOG.md'); pg.click('[data-a=logRetry]'); pg.wait_for_function("LOG_STATE==='ready'", timeout=8000); pg.wait_for_timeout(300)
    ok(pg.locator('.tl-item').count() == len(versions), 'Try again loads it')
    pg.context.close()
    t.errors[:] = [e for e in t.errors if 'ERR_FAILED' not in e]  # the blocked request above is expected

    for (w, h, sc, tag) in [(390, 844, 'dark', 'dark'), (820, 1180, 'light', 'ipad'), (1440, 900, 'light', 'mac'), (852, 393, 'light', 'landscape'), (320, 568, 'light', 'small')]:
        q = t.page(b, w, h, sc, data=None, **({'ua': None} if tag == 'mac' else {}))
        q.evaluate("U.tab='settings';render()"); q.wait_for_timeout(150); q.click('.row[data-a=openLog]')
        q.wait_for_function("LOG_STATE==='ready'", timeout=8000); q.wait_for_timeout(1300); t.shot(q, tag)
        ok(not q.evaluate("document.documentElement.scrollWidth>innerWidth"), f'{tag}: fits the screen')
        if tag == 'ipad': ok(q.locator('.toptabs').count() == 1, 'iPad: the tabs stay at the top')
        q.context.close()
