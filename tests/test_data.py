"""Data version upgrades, backups from newer versions, storage protection and working offline."""
import json, os
from harness import sample, ready, fix, OUT, url, APP_PATH, offline, online

PERSIST = {'granted': "navigator.storage.persisted=async()=>false;navigator.storage.persist=async()=>true",
           'refused': "navigator.storage.persisted=async()=>false;navigator.storage.persist=async()=>false",
           'missing': "Object.defineProperty(navigator,'storage',{value:undefined})"}

def run(b, t):
    ok = t.ok
    # data saved before 3.7 has no version number: it's upgraded, and a copy is kept first
    pg = t.page(b)
    S = pg.evaluate("SCHEMA")
    ok(pg.evaluate("D.schema") == S, f'older data is upgraded to data version {S}')
    saved = json.loads(pg.evaluate("localStorage.getItem('vocalTracker')"))
    ok(saved.get('schema') == S, 'the upgraded data is saved')
    pre = json.loads(pg.evaluate("localStorage.getItem('vocalBeforeUpgrade')") or 'null')
    ok(pre and pre['from'] == 0 and pre['to'] == S and 'schema' not in pre['data'] and [x['id'] for x in pre['data']['sessions']] == [x['id'] for x in sample()['sessions']],
       'a copy of the data as it was is kept before upgrading')
    ok(pre and saved['sessions'] == pre['data']['sessions'] and saved['months'] == pre['data']['months'] and {k: v for k, v in saved.items() if k != 'schema'} == pre['data'], 'upgrading changes nothing else')
    # once upgraded, reopening doesn't upgrade again
    pg.evaluate("localStorage.removeItem('vocalBeforeUpgrade')"); pg.reload(); ready(pg)
    ok(pg.evaluate("localStorage.getItem('vocalBeforeUpgrade')") is None, 'reopening up-to-date data makes no new copy')
    # the copy is removed after 30 days
    pg.evaluate("localStorage.setItem('vocalBeforeUpgrade',JSON.stringify({from:0,to:1,at:Date.now()-31*864e5,data:{}}))"); pg.reload(); ready(pg)
    ok(pg.evaluate("localStorage.getItem('vocalBeforeUpgrade')") is None, 'the copy is removed after 30 days')
    pg.context.close()

    # an empty app needs no copy
    pg = t.page(b, data=None)
    ok(pg.evaluate("D.schema") == S and pg.evaluate("localStorage.getItem('vocalBeforeUpgrade')") is None, 'a new, empty app starts on the current data version')
    # a backup from a newer version says so
    src = json.load(open(fix('backup-3.6.json'), encoding='utf-8'))
    src['data']['schema'] = S + 1; src['appVersion'] = '9.9'; del src['checkCode']
    p = os.path.join(OUT, 'from-the-future.json'); json.dump(src, open(p, 'w', encoding='utf-8'))
    pg.evaluate("U.tab='settings';render()")
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(p); pg.wait_for_function("U.sheet==='bkReport'", timeout=8000)
    ok('Made by a newer version' in pg.inner_text('.sheet') and '9.9' in pg.inner_text('.sheet'), 'a backup from a newer version warns before restoring')
    t.shot(pg, 'newer-backup')
    pg.context.close()

    # storage protection
    for case, init in PERSIST.items():
        pg = t.page(b, init=init); pg.evaluate("U.tab='settings';render()"); pg.wait_for_timeout(300)
        row = pg.locator('[data-v=persist]').inner_text()
        want = {'granted': 'On', 'refused': 'Off', 'missing': 'Not available'}[case]
        ok(want in [x.strip() for x in row.split('\n')], f'Storage protection shows "{want}" when the browser {case} it')
        pg.click('[data-v=persist]'); pg.wait_for_timeout(400); t.shot(pg, 'persist-' + case)
        ok(pg.locator('[data-a=persistAsk]').count() == (1 if case == 'refused' else 0), f'Ask again {"is" if case == "refused" else "isn’t"} offered when {case}')
        pg.context.close()

    # offline: the app, and the changelog, open with no connection
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(url(APP_PATH)); ready(pg)
    pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); ready(pg)
    ok(pg.evaluate("!!navigator.serviceWorker.controller"), 'the offline helper is running')
    pg.evaluate("U.tab='settings';render()"); pg.click('.row[data-a=openLog]'); pg.wait_for_function("LOG_STATE==='ready'", timeout=8000)
    offline(APP_PATH)
    pg.reload(); ready(pg)
    ok(pg.locator('[data-a=tab]').count() > 0, 'with no connection, the app still opens')
    pg.evaluate("U.tab='settings';render()"); pg.click('.row[data-a=openLog]'); pg.wait_for_function("LOG_STATE!=='loading'", timeout=8000); pg.wait_for_timeout(300)
    ok(pg.locator('.tl-item').count() > 5, 'and the Changelog opens from the saved copy')
    online(APP_PATH)
    for e in errs: t.errors.append('offline: ' + e)
    ctx.close()

    # an update that can't fully download never replaces the working offline copy
    import shutil, re as _re
    from harness import ROOT
    site = os.path.join(OUT, 'update-site'); shutil.rmtree(site, ignore_errors=True)
    os.makedirs(site)
    for f in ['index.html', 'sw.js', 'CHANGELOG.md', 'icon.png']: shutil.copy(os.path.join(ROOT, f), os.path.join(site, f))
    for d in ['js', 'css', 'splash']: shutil.copytree(os.path.join(ROOT, d), os.path.join(site, d))
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London'); pg = ctx.new_page()
    pg.goto(url(os.path.join(site, 'index.html'))); ready(pg); pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); ready(pg)
    pg.wait_for_function("caches.open('vocal-sessions-v3').then(c=>c.match('./')).then(r=>!!r)", timeout=10000)
    v_old = pg.evaluate("APP_VERSION")
    html = open(os.path.join(site, 'index.html'), encoding='utf-8').read()
    broken = _re.sub(r'\?v=[\d.]+"', '?v=99.0"', html).replace("const APP_VERSION='" + v_old, "const APP_VERSION='99.0").replace('js/boot.js?v=99.0', 'js/not-there.js?v=99.0')
    open(os.path.join(site, 'index.html'), 'w', encoding='utf-8').write(broken)
    pg.reload(); pg.wait_for_timeout(2500)  # the new page arrives, but one of its files is missing
    ok(pg.evaluate("caches.open('vocal-sessions-v3').then(c=>c.match('./')).then(r=>r.text()).then(t=>t.includes(\"APP_VERSION='" + v_old + "'\"))"),
       'an update with a missing file is not saved for offline use')
    site_page = os.path.join(site, 'index.html')
    offline(site_page); pg.reload(); ready(pg)
    ok(pg.evaluate("APP_VERSION") == v_old and pg.locator('[data-a=tab]').count() > 0, f'offline, the complete {v_old} still opens')
    online(site_page)
    open(os.path.join(site, 'index.html'), 'w', encoding='utf-8').write(html.replace("const APP_VERSION='" + v_old, "const APP_VERSION='99.1").replace('?v=' + v_old + '"', '?v=99.1"'))
    pg.reload(); ready(pg); pg.wait_for_timeout(1500)
    ok(pg.evaluate("caches.open('vocal-sessions-v3').then(c=>c.match('./')).then(r=>r.text()).then(t=>t.includes(\"APP_VERSION='99.1'\"))"),
       'a complete update is saved for offline use')
    offline(site_page); pg.reload(); ready(pg)
    ok(pg.evaluate("APP_VERSION") == '99.1' and pg.locator('[data-a=tab]').count() > 0, 'and opens offline')
    ok(pg.evaluate("caches.open('vocal-sessions-v3').then(c=>c.keys()).then(k=>k.filter(r=>/\\/js\\//.test(r.url)&&!r.url.includes('v=99.1')).length)") == 0,
       'files from older versions are cleared from the offline copy')
    online(site_page)
    ctx.close()
