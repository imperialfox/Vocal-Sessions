"""3.21 Settings: a main list of icon rows, each opening its own page (Backup and Storage with a hero card), an
Accessibility page with Reduce motion and Slow motion, and the app's icon, name and version at the bottom."""
import datetime as dt
from harness import iso, now, sample

MAIN = "go(()=>{U.tab='settings';U.view=null})"
PAGE = "k=>go(()=>{U.tab='settings';U.view='set';U.setPg=k})"
VALUE = "k=>document.querySelector('#app [data-zk=\"set:'+k+'\"] .mut').textContent.trim()"


def main_list(b, t):
    ok = t.ok
    d = sample()
    d['lastBackup'] = iso(now - dt.timedelta(days=1))
    pg = t.page(b, w=375, h=812, data=d)
    pg.evaluate(MAIN); pg.wait_for_timeout(200)
    keys = pg.evaluate("[...document.querySelectorAll('#app [data-a=setPg]')].map(r=>r.dataset.v)")
    ok(keys == ['backup', 'storage', 'recall', 'coach', 'appear', 'access'], f'the main list opens Backup, Storage, Recall, Coach video, Appearance and Accessibility ({keys})')
    ok(pg.evaluate("[...document.querySelectorAll('#app .grp')].slice(0,3).every(g=>g.classList.contains('tiled'))"),
       'in three groups of icon rows (separators start after the icons)')
    tiles = pg.evaluate("[...document.querySelectorAll('#app .grp.tiled .row')].map(r=>{const s=r.querySelector('.tile');return s?getComputedStyle(s).backgroundColor+'|'+s.innerHTML:''})")
    ok(len(tiles) == 8 and all(tiles) and len(set(tiles)) == 8, 'every row has its own icon tile: no colour and glyph used twice')
    ok(pg.evaluate("[...document.querySelectorAll('#app .grp.tiled .tile svg')].every(s=>s.getBoundingClientRect().width>15)"), 'and the glyphs draw')
    ok(pg.evaluate(VALUE, 'backup') == 'Yesterday' and pg.locator('#app [data-zk="set:backup"] .setwarn').count() == 0,
       'Backup shows when you last backed up: “Yesterday”')
    ok(pg.evaluate(VALUE, 'storage').endswith(' MB'), 'Storage shows the space used: ' + pg.evaluate(VALUE, 'storage'))
    ok(pg.evaluate(VALUE, 'recall') == '2 s' and pg.evaluate(VALUE, 'coach') == 'Not added' and pg.evaluate(VALUE, 'access') == 'System',
       'Recall shows its peek length, Coach video whether it’s added, Accessibility its setting')
    ok(pg.locator('#app .row[data-a=openLog][data-zk=log] .tile').count() == 1 and pg.evaluate("APP_VERSION") in pg.inner_text('#app .row[data-a=openLog]'),
       'Changelog is an icon row showing the version')
    gh = pg.locator('#app a.row[href*="github.com/imperialfox"]')
    ok(gh.count() == 1 and gh.locator('.tile').count() == 1 and gh.get_attribute('target') == '_blank', 'View on GitHub is an icon row that opens GitHub')
    ok(pg.locator('#app [data-v=resetMonth] .dng').count() == 1 and pg.locator('#app [data-v=resetAll] .dng').count() == 1,
       'the two resets stay on the main list, in red')
    ft = pg.locator('#app .setfoot')
    ok(ft.count() == 1 and ft.locator('img[src^="icon.png"]').count() == 1 and 'Vocal Sessions' in ft.inner_text()
       and pg.evaluate("APP_VERSION+' · '+RELEASE_DATE") in ft.inner_text(), 'the bottom shows the app’s icon, name, version and date')
    ok(pg.evaluate("(()=>{const i=document.querySelector('.setfoot img');return i.complete&&i.naturalWidth>0})()"), 'and the icon loads')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways at 375 px')
    pg.evaluate("scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(300)
    ok(pg.evaluate("document.querySelector('.setfoot b').getBoundingClientRect().bottom<document.querySelector('#dock').firstElementChild.getBoundingClientRect().top"),
       'scrolled to the bottom, the name clears the tab bar')
    t.shot(pg, 'main')
    # over two weeks: red
    pg.evaluate("D.lastBackup=new Date(Date.now()-20*864e5).toISOString();rerender()")
    ok(pg.locator('#app [data-zk="set:backup"] .setwarn').count() == 1, 'over two weeks since a backup, its value turns red')
    pg.evaluate("D.lastBackup=null;rerender()")
    ok(pg.evaluate(VALUE, 'backup') == 'Never' and pg.locator('#app [data-zk="set:backup"] .setwarn').count() == 1, 'never backed up: “Never”, in red')
    pg.context.close()


def pages(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        pg = t.page(b, w=375, h=812, sc=sc)
        for k, title, hero in (('backup', 'Backup', True), ('storage', 'Storage', True), ('recall', 'Recall', False),
                               ('coach', 'Coach video', False), ('appear', 'Appearance', False), ('access', 'Accessibility', False)):
            pg.evaluate(MAIN); pg.wait_for_timeout(150)
            pg.click(f'#app [data-zk="set:{k}"]'); pg.wait_for_timeout(250)
            ok(pg.evaluate("U.view+'/'+U.setPg") == 'set/' + k, f'{sc}: the {title} row opens its page')
            ok(pg.locator('#barL [data-a=setPgBack][aria-label="Back to Settings"]').count() == 1, f'{sc} {title}: a Back button')
            ok(pg.locator('#app h1').first.inner_text().strip() == title, f'{sc} {title}: titled {title}')
            ok((pg.locator('#app .sethero .tile.big').count() == 1) == hero, f'{sc} {title}: ' + ('a hero card with the big icon' if hero else 'a plain page'))
            ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{sc} {title}: fits the screen')
            t.shot(pg, f'{k}-{sc}', full_page=True)
            pg.click('#barL [data-a=setPgBack]'); pg.wait_for_timeout(250)
            ok(pg.evaluate("U.tab") == 'settings' and not pg.evaluate("U.view"), f'{sc} {title}: Back returns to the main list')
        pg.context.close()
    # what's on each page
    pg = t.page(b)
    pg.evaluate(PAGE, 'backup'); pg.wait_for_timeout(200)
    for a in ('exportPrep', 'importPick', 'checkPick', 'saveReadme'):
        ok(pg.locator(f'#app [data-a={a}]').count() == 1, f'Backup has {a}')
    ok(pg.locator('#app [data-v=bkLog]').count() == 1 and pg.locator('#app [data-v=bkGuide]').count() == 1, 'and Backup history and Where backups go')
    ok(pg.locator('#app .foot.warn').count() == 1 and 'over two weeks' in pg.inner_text('#app'), 'the last backup line turns red after two weeks')
    ok('never backed up' in pg.inner_text('#app') and 'Song tracks and the coach video' in pg.inner_text('#app'),
       'and says what a backup leaves out')
    pg.click('#app [data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=15000)
    ok(pg.locator('.sheet [data-a=exportNoRec]').count() == 1, 'Export opens the usual sheet, with Exclude recordings')
    pg.evaluate("U.sheet=null;pendingExport=null;rerender()")
    pg.evaluate(PAGE, 'storage'); pg.wait_for_timeout(200)
    s = pg.evaluate("SET.sizes()")
    ok([x['l'] for x in s] == ['Recordings', 'Song tracks', 'Coach video', 'Sessions and songs'], 'Storage counts recordings, song tracks, the coach video and app data')
    ok(pg.locator('#app .setbar i').count() == len([x for x in s if x['b'] > 0]) and pg.locator('#app .setkey span').count() == 4,
       'one bar split by what’s using the space, with a key')
    ok(pg.locator('#app [data-a=tkReview]').count() == 1 and pg.locator('#app [data-v=persist]').count() == 1, 'with Review old takes and Storage protection')
    ok(pg.evaluate("document.querySelector('.setuse').getAttribute('aria-label')").endswith('MB'), 'the bar has a spoken summary')
    pg.evaluate(PAGE, 'recall'); pg.wait_for_timeout(200)
    pg.click('#app [aria-label="Peek length"] [data-v="5"]'); pg.wait_for_timeout(200)
    pg.click('#barL [data-a=setPgBack]'); pg.wait_for_timeout(200)
    ok(pg.evaluate(VALUE, 'recall') == '5 s', 'changing the peek length shows on the main list')
    pg.context.close()


def accessibility(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate(PAGE, 'access'); pg.wait_for_timeout(200)
    ok(pg.locator('#app [data-a=setReduce]').all_inner_texts() == ['Match iPhone', 'On', 'Off'], 'Reduce motion: Match iPhone, On or Off')
    ok(pg.locator('#app [data-a=setReduce][data-v=system][aria-checked=true] svg').count() == 1, 'Match iPhone is ticked to begin with')
    ok(not pg.evaluate("MOTION.reduced()") and 'off at the moment' in pg.inner_text('#app'), 'which says the iPhone’s setting is off')
    pg.click('#app [data-a=setReduce][data-v=on]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("localStorage.getItem('vocalReduce')") == 'on' and pg.evaluate("MOTION.reduced()")
       and pg.evaluate("document.documentElement.classList.contains('motion-reduced')"), 'On reduces motion here, kept on this device')
    ok('vocalReduce' not in pg.evaluate("localStorage.getItem('vocalTracker')"), 'it isn’t in the app’s data, so never in a backup')
    pg.evaluate("U.sheet='resetMonth';rerender()"); pg.wait_for_timeout(100)
    ok(pg.evaluate("getComputedStyle(document.querySelector('.sheet')).animationName") == 'rmIn', 'with it on, a sheet fades in rather than rising')
    pg.evaluate("U.sheet=null;rerender()")
    ok(pg.evaluate("getComputedStyle(document.querySelector('#app .row')).transitionProperty").startswith('opacity'), 'and only fades and colours can ease')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')", timeout=15000)
    ok(pg.evaluate("MOTION.reduced()"), 'it’s still on after reopening the app')
    pg.evaluate(PAGE, 'access'); pg.wait_for_timeout(200)
    pg.click('#app [data-a=setReduce][data-v=off]'); pg.wait_for_timeout(200)
    ok(not pg.evaluate("MOTION.reduced()") and not pg.evaluate("document.documentElement.classList.contains('motion-reduced')"), 'Off turns it off')
    pg.emulate_media(reduced_motion='reduce'); pg.wait_for_timeout(100)
    ok(not pg.evaluate("MOTION.reduced()"), 'even when the iPhone’s Reduce Motion is on')
    pg.click('#app [data-a=setReduce][data-v=system]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("MOTION.reduced()") and pg.evaluate("localStorage.getItem('vocalReduce')") is None and 'on at the moment' in pg.inner_text('#app'),
       'Match iPhone follows the iPhone again (on here)')
    pg.evaluate(MAIN); pg.wait_for_timeout(150)
    ok(pg.evaluate(VALUE, 'access') == 'System', 'the main list shows System')
    pg.emulate_media(reduced_motion='no-preference'); pg.wait_for_timeout(100)
    # Slow motion
    pg.evaluate("MOTION.setSpeed(1)"); pg.evaluate(PAGE, 'access'); pg.wait_for_timeout(200)
    sw = '#app [data-a=setSlow]'
    ok(pg.locator(sw + '[role=switch][aria-checked=false]').count() == 1, 'Slow motion is a switch, off')
    pg.click(sw); pg.wait_for_timeout(200)
    ok(pg.evaluate("MOTION.speed()") == 4 and pg.evaluate("localStorage.getItem('vocalMotion')") == '4' and pg.locator(sw + '[aria-checked=true]').count() == 1,
       'turning it on plays everything four times slower')
    pg.click(sw); pg.wait_for_timeout(200)
    ok(pg.evaluate("MOTION.speed()") == 1 and pg.evaluate("localStorage.getItem('vocalMotion')") is None, 'and off again goes back to normal')
    pg.context.close()


def coach_link(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate("go(()=>{U.tab='exercises';U.view=null})"); pg.wait_for_timeout(200)
    pg.click('#app [data-a=coachSettings]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view+'/'+U.setPg") == 'set/coach' and pg.locator('#app [data-a=coachAdd]').count() == 1,
       'Add coach video from Exercises opens Settings › Coach video')
    pg.keyboard.press('Control+,'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'settings' and not pg.evaluate("U.view"), 'Cmd/Ctrl + , opens the main list')
    pg.context.close()


def wide(b, t):
    ok = t.ok
    for name, w, h in (('landscape', 852, 393), ('ipad', 820, 1180), ('mac', 1440, 900)):
        pg = t.page(b, w=w, h=h, **({'ua': None} if name == 'mac' else {}))
        pg.evaluate(PAGE, 'storage'); pg.wait_for_timeout(250)
        ok(pg.locator('#barL [data-a=setPgBack]').count() == 1 and pg.evaluate("document.documentElement.scrollWidth<=innerWidth"),
           f'{name}: a Settings page has Back and fits')
        t.shot(pg, f'storage-{name}')
        pg.context.close()


def run(b, t):
    main_list(b, t)
    pages(b, t)
    accessibility(b, t)
    coach_link(b, t)
    wide(b, t)
