"""Every screen at every size: iPhone (two sizes, portrait and landscape), iPad both ways and Mac, light and dark.
Also pull to refresh and the keyboard shortcuts. Screenshots of each go to tests/output/."""
import os
from harness import with_song_practice

SIZES = [('iphone', 390, 844, True), ('iphone-small', 375, 667, True), ('iphone-se', 320, 568, True), ('landscape', 852, 393, True),
         ('ipad', 820, 1180, True), ('ipad-landscape', 1180, 820, True), ('mac', 1440, 900, False)]

# VS_LAYOUT_SIZES=iphone,mac checks only those sizes (the runner uses this to check sizes side by side)
_only = [x for x in os.environ.get('VS_LAYOUT_SIZES', '').split(',') if x]
if _only: SIZES = [x for x in SIZES if x[0] in _only]

FITS = "document.documentElement.scrollWidth<=innerWidth"
BAR_IN = "(()=>{const b=document.querySelector('.tabbar,.toptabs,.side .sbi');if(!b)return true;const r=b.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+0.5})()"

SONG = """(()=>{const l='[Verse 1]\\nPaper boats along the gutter racing rain down Elmwood Lane past the bakery\\nRacing rain\\n\\n[Chorus]\\nCarry me, carry me over\\nLet the river know my name\\n\\n[Chorus]\\nCarry me, carry me over\\nLet the river know my name';
 U.sDraft={step:1,title:'River song',artist:'Example band',text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();
 const s=songById(U.songId),sid=s.order[1].sid;s.sections[sid].ann['0:2']={br:1,v:'ah'};s.sections[sid].ann['1:1']={nt:'Lift here'};s.sections[sid].cue='Open, full voice';save();rerender();})()"""

INSIDE = "sel=>{const e=document.querySelector(sel);if(!e)return false;const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+0.5&&r.top>=0&&r.bottom<=innerHeight+0.5}"
# three takes from the chorus (one starred), and that section selected
TAKES = """(async()=>{const s=songById(U.songId),o=s.order[1].o,b=new Blob([new Uint8Array(3000)],{type:'audio/mp4'});
 for(const [id,ago,star] of [['lt1',4,true],['lt2',2,false],['lt3',0,false]])
  await putTake({id,songId:s.id,o,created:Date.now()-ago*864e5-60000,len:16+ago,size:3000,type:'audio/mp4',blob:b,star,note:id==='lt1'?{w:['Breathy'],t:''}:undefined});
 await refreshTakes();U.sSec=o;render();})()"""

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
            for tab in ['history', 'exercises', 'settings', 'songs']:
                pg.evaluate(f"U.tab='{tab}';U.view=null;render()"); pg.wait_for_timeout(250); check(tab)
            pg.evaluate(SONG); pg.wait_for_timeout(300); check('song')
            # a selected section, recording it (without a microphone: the screen as it looks), and its takes
            pg.evaluate(TAKES); pg.wait_for_timeout(300); check('song-selected')
            if pg.locator('.sgsec.sel [data-a=sgRec]').count() != 1: bad.append('selected section has no Record pill')
            pg.evaluate("(()=>{const s=songById(U.songId);rec={o:s.order[1].o,songId:s.id,t:16,stopping:true};render()})()"); pg.wait_for_timeout(300)
            if not pg.evaluate(INSIDE, '.recbar'): bad.append('recording bar off screen')
            if not pg.evaluate("(()=>{const r=document.querySelector('.rechead');return !!r&&r.getBoundingClientRect().width>20&&r.scrollWidth<=r.clientWidth+1})()"): bad.append('recording label missing or cut off')
            check('song-recording')
            pg.evaluate("rec=null;const s=songById(U.songId);U.sheet='sgTakes';U.sd={k:s.id,o:s.order[1].o,fresh:'lt3'};render()"); pg.wait_for_timeout(500)
            if not pg.evaluate(INSIDE, '.sheet') or pg.locator('.sheet .newtake').count() != 1: bad.append('takes sheet off screen')
            check('song-takes')
            pg.evaluate("U.sheet=null;U.sd={};U.sSec=null;render()"); pg.wait_for_timeout(300)
            pg.evaluate("SG_ACT.sgEdit()"); pg.wait_for_timeout(250)
            pg.click('.sgsec >> nth=1 >> .w >> nth=3'); pg.wait_for_timeout(250)
            if not pg.evaluate("(()=>{const m=document.getElementById('emenu');if(!m)return false;const r=m.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+0.5})()"): bad.append('marks menu off screen')
            check('song-edit')
            pg.evaluate("SG_ACT.sgEditMode(document.querySelector('[data-a=sgEditMode][data-v=lyrics]'),'lyrics')"); pg.wait_for_timeout(400); check('song-lyrics')
            pg.evaluate("sgEndEdit(true);U.view=null;U.tab='songs';render();SG_ACT.sgNew()"); pg.wait_for_timeout(500); check('new-song')
            pg.evaluate("U.sheet=null;U.tab='songs';render();startSearch()"); pg.wait_for_timeout(300); check('songs-search')
            pg.evaluate("endSearch();U.view=null;U.tab='today';render()"); pg.wait_for_timeout(200)
            pg.evaluate("U.tab='history';render()"); pg.click('[data-a=openAll][data-v=sessions]'); pg.wait_for_timeout(250); check('all-sessions')
            pg.evaluate("U.view=null;U.tab='settings';render()"); pg.click('.row[data-a=openLog]'); pg.wait_for_function("LOG_STATE==='ready'", timeout=8000); pg.wait_for_timeout(1200); check('changelog')
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

    # pull to refresh on iPhone (once, with the iPhone size)
    if not any(x[0] == 'iphone' for x in SIZES): return
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
