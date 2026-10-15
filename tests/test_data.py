"""Data version upgrades, backups from newer versions, storage protection and working offline."""
import json, os
from harness import sample, ready, fix, OUT

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
    from harness import url, APP_PATH
    pg.goto(url(APP_PATH)); ready(pg)
    pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); ready(pg)
    ok(pg.evaluate("!!navigator.serviceWorker.controller"), 'the offline helper is running')
    pg.evaluate("U.tab='settings';render()"); pg.click('.row[data-a=openLog]'); pg.wait_for_function("LOG_STATE==='ready'", timeout=8000)
    ctx.set_offline(True)
    pg.reload(); ready(pg)
    ok(pg.locator('[data-a=tab]').count() > 0, 'with no connection, the app still opens')
    pg.evaluate("U.tab='settings';render()"); pg.click('.row[data-a=openLog]'); pg.wait_for_function("LOG_STATE!=='loading'", timeout=8000); pg.wait_for_timeout(300)
    ok(pg.locator('.tl-item').count() > 5, 'and the Changelog opens from the saved copy')
    ctx.set_offline(False)
    for e in errs: t.errors.append('offline: ' + e)
    ctx.close()
