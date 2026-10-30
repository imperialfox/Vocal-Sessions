"""Q13 Interface: Keyboard Guards. Keyboard shortcuts on iPad and Mac never fire twice, while typing, or during a
recording: one shared typing check (KEYS.typing) and one place shortcuts go through (KEYS.add / KEYS.route), holding a
key never repeats a toggle, a key another control already handled is left alone, nothing fires while a picker, sheet
or recording is open, the Song length picker's arrows stay in the picker, Cmd+1–4 follows the tab bar's rules, Apple
devices use Cmd only (Ctrl's text-editing keys stay free), and Enter to confirm ignores keys pressed while composing
text in another script. Escape still closes what it did."""
import os, re
from harness import with_song_practice, UA_IPHONE
from test_track import track, loaded

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']
ADD = """([t,a,l])=>{U.sDraft={step:1,title:t,artist:a,text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();return U.songId}"""
LYR_A = '[Verse]\nPaper boats along the gutter\nFloat away\n\n[Chorus]\nCarry me over\nLet the river know'
LYR_B = '[Verse]\nCoffee on the counter\n\n[Chorus]\nTurn it up'
# a key sent by script, as an iPad keyboard or an input method would send it: returns whether it was handled
KEY = """([sel,o])=>{const el=sel?document.querySelector(sel):document.activeElement||document.body;
  const e=new KeyboardEvent('keydown',Object.assign({bubbles:true,cancelable:true},o));el.dispatchEvent(e);return e.defaultPrevented}"""
JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'js')


def songs_split(b, t, ua=UA_IPHONE):
    """iPad (or a Mac window with ua=None): two songs, the first open beside the list."""
    pg = t.page(b, 820, 1180, data=with_song_practice(), ua=ua, ctx_args={'permissions': ['microphone']})
    a = pg.evaluate(ADD, ['River song', 'Example band', LYR_A]); bb = pg.evaluate(ADD, ['Kitchen radio', '', LYR_B])
    pg.evaluate("U.tab='songs';U.view=null;render()"); pg.wait_for_timeout(250)
    pg.click(f'.sgcol .rowc[data-k="{a}"]'); pg.wait_for_timeout(250)
    return pg, a, bb


def run(b, t):
    ok = t.ok

    # ----- 1. one shared typing check: the old copies are gone -----
    src = {f: open(os.path.join(JS, f), encoding='utf-8').read() for f in os.listdir(JS) if f.endswith('.js')}
    copies = [f for f, s in src.items() if f != 'helpers.js' and re.search(r"""(closest|matches)\(\s*['"]input,\s*textarea""", s)]
    ok(not copies, 'the "is the user typing?" check is written once, in KEYS (helpers.js): ' + ', '.join(copies))
    ok(src['gestures.js'].count("addEventListener('keydown', KEYS.route") == 1, 'one place shortcuts are handled (KEYS.route, gestures.js)')

    # ----- 4. Apple devices: Cmd only, so Ctrl's text-editing keys stay free -----
    pg, A, B = songs_split(b, t)
    ok(pg.evaluate("KEYS.apple"), 'an iPad counts as an Apple device')
    pg.keyboard.press('Control+e'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sEdit") is None, 'Ctrl+E doesn’t edit the song on an iPad (Cmd only)')
    pg.keyboard.press('Control+f'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'songs', 'Ctrl+F doesn’t open Search on an iPad')
    pg.keyboard.press('Control+2'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'songs', 'Ctrl+2 doesn’t switch tabs on an iPad')
    pg.click('#sgqi'); pg.keyboard.type('riv')
    ok(not pg.evaluate(KEY, [None, {'key': 'e', 'ctrlKey': True}]) and not pg.evaluate(KEY, [None, {'key': 'n', 'ctrlKey': True}])
       and not pg.evaluate(KEY, [None, {'key': 'f', 'ctrlKey': True}]), 'Ctrl+E, N and F are left to the text field while typing')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    pg.evaluate("document.activeElement&&document.activeElement.blur()")
    pg.keyboard.press('Meta+e'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sEdit") == 'annotate', 'Cmd+E edits the song')
    # holding a key never repeats a toggle
    pg.keyboard.down('Meta'); pg.keyboard.down('e'); pg.keyboard.down('e'); pg.keyboard.down('e'); pg.keyboard.up('e'); pg.keyboard.up('Meta')
    pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sEdit") is None, 'holding Cmd+E is Done once, not Done-Edit-Done')

    # ----- 3. Cmd+1–4 follows the tab bar: the same side effects (sgTabTap) -----
    pg.keyboard.press('Meta+e'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sEdit") == 'annotate', 'editing again')
    pg.keyboard.press('Meta+2'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'history' and pg.evaluate("U.sEdit") is None, 'Cmd+2 leaves an edit the way tapping the tab does (sgTabTap)')
    pg.keyboard.press('Meta+3'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'songs', 'Cmd+3 back to Songs')
    pg.keyboard.down('Meta'); pg.keyboard.down('1'); pg.keyboard.down('1'); pg.keyboard.up('1'); pg.keyboard.up('Meta'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'today', 'Cmd+1 opens Today (held, once)')
    pg.keyboard.press('Meta+3'); pg.wait_for_timeout(250)
    # while typing: no tab switch
    pg.click('#sgqi'); pg.keyboard.type('kit'); pg.keyboard.press('Meta+2'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'songs' and pg.evaluate("document.activeElement.id") == 'sgqi', 'no tab switch while typing')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    pg.evaluate("document.activeElement&&document.activeElement.blur()")
    pg.click(f'.sgcol .rowc[data-k="{A}"]'); pg.wait_for_timeout(250)

    # ----- 2. the Song length picker's arrows stay in the picker; Set is for the song it was opened for -----
    pg.evaluate("id=>{const s=songById(id);s.timing={len:200,real:false,est:false,slots:{}};save();rerender()}", A)
    pg.wait_for_timeout(200)
    pg.click('#app .cklen[data-a=ckLen]'); pg.wait_for_timeout(300)
    ok(pg.locator('#ckpk').count() == 1 and pg.evaluate("document.activeElement.classList.contains('ckwcol')"), 'the length picker is open, a wheel focused')
    ok(pg.inner_text('#ckpOut') == '3:20', 'it shows the song’s length')
    pg.keyboard.press('ArrowDown'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.songId") == A and pg.locator('#ckpk').count() == 1, '↓ in the picker doesn’t open the next song')
    ok(pg.inner_text('#ckpOut') == '4:20', '↓ moves the minutes wheel: ' + pg.inner_text('#ckpOut'))
    # a key that reaches the page while the picker is up does nothing either
    pg.evaluate(KEY, ['body', {'key': 'ArrowDown'}]); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.songId") == A, 'nor does ↓ elsewhere while the picker is open')
    pg.keyboard.press('Meta+2'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.tab") == 'songs' and pg.locator('#ckpk').count() == 1, 'no tab switch while the picker is open')
    pg.click('#ckpk [data-a=ckPickSet]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("id=>songById(id).timing.len", A) == 260 and not pg.evaluate("id=>songById(id).timing", B),
       'Set gives the length to the song the picker was opened for, and only that one')
    ok(pg.evaluate("U.songId") == A, 'the same song is still open')
    pg.evaluate("document.activeElement&&document.activeElement.blur()")
    nxt = pg.evaluate("id=>{const k=[...document.querySelectorAll('#slist .rowc')].map(r=>r.dataset.k);return k[Math.min(k.length-1,k.indexOf(id)+1)]}", A)
    pg.keyboard.press('ArrowDown'); pg.wait_for_timeout(250)
    ok(nxt != A and pg.evaluate("U.songId") == nxt, '↓ still moves to the next song once the picker is gone')
    pg.keyboard.press('ArrowUp'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.songId") == A, '↑ moves back')

    # ----- 1. no shortcuts while a sheet is open; Escape still closes it -----
    pg.evaluate("U.sheet='calendar';U.sd={};U.calMonth=new Date(new Date().getFullYear(),new Date().getMonth(),1);rerender()"); pg.wait_for_timeout(250)
    cur = pg.evaluate("U.songId")
    pg.keyboard.press('Meta+2'); pg.keyboard.press('Meta+f'); pg.keyboard.press('ArrowDown'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'songs' and pg.evaluate("U.sheet") == 'calendar' and pg.evaluate("U.songId") == cur,
       'no shortcuts while a sheet is open')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sheet") is None, 'Escape still closes the sheet')

    # ----- 1. a key another control already handled is left alone -----
    pg.evaluate("""()=>{const d=document.createElement('div');d.id='kxh';d.tabIndex=0;document.body.appendChild(d);
      d.addEventListener('keydown',e=>e.preventDefault())}""")
    pg.evaluate(KEY, ['#kxh', {'key': '2', 'metaKey': True}]); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'songs', 'a key a control already handled doesn’t also switch tabs')
    pg.evaluate(KEY, ['#kxh', {'key': 'ArrowDown'}]); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.songId") == cur, 'or move to the next song')
    pg.evaluate("document.getElementById('kxh').remove()")

    # ----- 3. Cmd+1–4 during a recording: no switch, the take keeps recording -----
    pg.click('.sgpane .sgsec >> nth=0 >> .sglab'); pg.wait_for_timeout(150)
    pg.click('.sgpane [data-a=sgRec]'); pg.wait_for_function("!!rec", timeout=5000); pg.wait_for_timeout(600)
    pg.keyboard.press('Meta+2'); pg.keyboard.press('Meta+4'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'songs' and pg.evaluate("!!rec"), 'Cmd+2 and Cmd+4 don’t switch tabs or stop a recording')
    pg.keyboard.press('Meta+e'); pg.keyboard.press('Meta+n'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sEdit") is None and not pg.evaluate("U.sDraft"), 'no other shortcuts while recording')
    pg.click('#dock [data-a=sgStop]'); pg.wait_for_function("!rec", timeout=5000); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgTakes', 'the take saves (its takes sheet opens)')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    pg.context.close()

    # ----- 4. elsewhere (Linux, Windows): Ctrl, as before, and Cmd does nothing -----
    pg, A, B = songs_split(b, t, ua=None)
    ok(not pg.evaluate("KEYS.apple"), 'a Linux window isn’t an Apple device')
    pg.keyboard.press('Meta+2'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'songs', 'Meta+2 does nothing off Apple devices')
    pg.keyboard.press('Control+2'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'history', 'Ctrl+2 switches tabs off Apple devices')
    pg.context.close()

    # ----- 3. Cmd+1–4 during a session step: no switch -----
    pg, A, B = songs_split(b, t)
    pg.keyboard.press('Meta+1'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'today', 'Cmd+1 opens Today')
    pg.click('[data-a=start]'); pg.wait_for_timeout(300)
    v = pg.evaluate("U.view")
    pg.keyboard.press('Meta+3'); pg.wait_for_timeout(250)
    ok(v == 'found' and pg.evaluate("U.view") == 'found' and pg.evaluate("U.tab") == 'today', 'no tab switch on a session step')
    pg.keyboard.press('Meta+f'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.tab") == 'today' and pg.evaluate("U.view") == 'found', 'nor Search')
    pg.evaluate("U.view='found';render()"); pg.click('[data-a=exit]'); pg.wait_for_timeout(200)

    # ----- 5. Enter to confirm ignores keys pressed while composing text -----
    # Search's field
    pg.keyboard.press('Meta+f'); pg.wait_for_timeout(250)
    pg.keyboard.type('かわ')
    for o in ({'key': 'Enter', 'isComposing': True}, {'key': 'Enter', 'keyCode': 229}):
        pg.evaluate(KEY, ['#fq', o]); pg.wait_for_timeout(100)
    ok(pg.evaluate("document.activeElement.id") == 'fq' and 'かわ' not in (pg.evaluate("localStorage.getItem('vocalSongPrefs')") or ''),
       'Search: Enter while composing keeps the keyboard and saves nothing')
    pg.evaluate(KEY, ['#fq', {'key': 'Enter'}]); pg.wait_for_timeout(150)
    ok(pg.evaluate("document.activeElement.id") != 'fq', 'Search: Enter after composing puts the keyboard away')
    pg.keyboard.press('Meta+3'); pg.wait_for_timeout(250)
    # the Songs list's own filter
    pg.click('#sgqi'); pg.keyboard.type('かわ')
    pg.evaluate(KEY, [None, {'key': 'Enter', 'isComposing': True}]); pg.wait_for_timeout(100)
    ok(pg.evaluate("document.activeElement.id") == 'sgqi', 'Songs filter: Enter while composing keeps the keyboard')
    pg.evaluate(KEY, [None, {'key': 'Enter'}]); pg.wait_for_timeout(100)
    ok(pg.evaluate("document.activeElement.id") != 'sgqi', 'Songs filter: Enter after composing puts it away')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    pg.click(f'.sgcol .rowc[data-k="{A}"]'); pg.wait_for_timeout(250)
    # the song's title in place (the pencil)
    pg.click('.sgpane [data-a=ckPencil], #barR [data-a=ckPencil]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("CK.head") and pg.locator('#ckTitle').count() == 1, 'the pencil edits the title in place')
    pg.focus('#ckTitle')
    pg.evaluate(KEY, ['#ckTitle', {'key': 'Enter', 'isComposing': True}]); pg.wait_for_timeout(150)
    ok(pg.evaluate("CK.head") and pg.locator('#ckTitle').count() == 1, 'Title: Enter while composing doesn’t finish')
    pg.evaluate(KEY, ['#ckTitle', {'key': 'Enter'}]); pg.wait_for_timeout(150)
    ok(not pg.evaluate("CK.head"), 'Title: Enter after composing finishes')
    # a mark's text field
    pg.evaluate("""()=>{window.__mk=0;const o=SG_ACT.mkText;SG_ACT.mkText=function(){window.__mk++};window.__mkO=o;
      const i=document.createElement('input');i.id='mkIn';document.body.appendChild(i);i.focus()}""")
    pg.evaluate(KEY, ['#mkIn', {'key': 'Enter', 'isComposing': True}]); pg.evaluate(KEY, ['#mkIn', {'key': 'Enter', 'keyCode': 229}])
    ok(pg.evaluate("window.__mk") == 0, 'Marks: Enter while composing doesn’t add the mark')
    pg.evaluate(KEY, ['#mkIn', {'key': 'Enter'}])
    ok(pg.evaluate("window.__mk") == 1, 'Marks: Enter after composing adds it')
    pg.evaluate("SG_ACT.mkText=window.__mkO;document.getElementById('mkIn').remove()")
    pg.context.close()

    # ----- 1. the track page: holding Space plays once; typing and handled keys are left alone -----
    pg = t.page(b, 820, 1180, data=with_song_practice())
    pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId='g_1'})"); pg.wait_for_timeout(300)
    with pg.expect_file_chooser() as fc: pg.click('#app [data-a=trkAdd]')
    fc.value.set_files(track()); loaded(pg)
    pg.evaluate("(()=>{const e=TRACK.el();window.__pp=[];e.addEventListener('play',()=>__pp.push('play'));e.addEventListener('pause',()=>__pp.push('pause'))})()")
    pg.evaluate("document.activeElement&&document.activeElement.blur()")
    pg.keyboard.down(' '); pg.keyboard.down(' '); pg.keyboard.down(' '); pg.keyboard.down(' '); pg.keyboard.up(' '); pg.wait_for_timeout(400)
    ok(pg.evaluate("__pp") == ['play'] and not pg.evaluate("TRACK.el().paused"), 'holding Space plays once (no play/pause flutter): ' + str(pg.evaluate("__pp")))
    pg.keyboard.press(' '); pg.wait_for_timeout(300)
    ok(pg.evaluate("TRACK.el().paused"), 'Space again pauses')
    t0 = pg.evaluate("TRACK.now()")
    pg.keyboard.down('ArrowRight'); pg.keyboard.down('ArrowRight'); pg.keyboard.down('ArrowRight'); pg.keyboard.up('ArrowRight'); pg.wait_for_timeout(200)
    ok(pg.evaluate("TRACK.now()") - t0 > 2.5, 'holding → keeps moving (a move, not a toggle)')
    pg.evaluate("window.__pp=[]")
    pg.evaluate("""()=>{const d=document.createElement('div');d.id='kxh';d.tabIndex=0;document.body.appendChild(d);
      d.addEventListener('keydown',e=>e.preventDefault())}""")
    pg.evaluate(KEY, ['#kxh', {'key': ' '}]); pg.wait_for_timeout(250)
    ok(pg.evaluate("__pp") == [], 'Space a control already handled doesn’t also play')
    pg.evaluate("""()=>{const i=document.createElement('input');i.id='kxi';document.body.appendChild(i);i.focus()}""")
    pg.keyboard.press(' '); pg.wait_for_timeout(250)
    ok(pg.evaluate("__pp") == [] and pg.input_value('#kxi') == ' ', 'Space while typing types a space')
    pg.evaluate("document.getElementById('kxi').remove();document.getElementById('kxh').remove()")
    pg.context.close()
