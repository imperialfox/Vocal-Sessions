"""Songs: pasting lyrics, labels and links, marks that follow their words, editing, pins, search, the Today card,
older songs, damaged songs and backups."""
import json, os
from harness import sample, with_song_practice, ready, OUT, url, APP_PATH

LYR = """River Song Lyrics
[Verse 1]
Paper boats along the gutter
Racing rain down Elmwood Lane
PRECHORUS
[Hold your breath, it’s coming](https://example.com/annotation)
[Chorus: Sam]
Carry me, carry me over
Let the river know my name

Verse 2:
Every window holds a candle
Every doorway holds a frame
You might also like
[Pre Chorus]
Hold your breath, it's coming
[Chorus]
Carry me, carry me over
Let the river know my name

I was never made for standing still
Never one to stay the same

[Refrain]
Carry me, carry me over
Let the river know my name
Carry me, carry me over
Let the river know my name12Embed"""

ADD = """([t,a,l])=>{U.sDraft={step:1,title:t,artist:a,text:l};U.sDraft.blocks=splitBlocks(l);U.sDraft.step=2;sgSaveDraft();return U.songId}"""


def run(b, t):
    ok = t.ok
    pg = t.page(b, touch=True, data=with_song_practice())

    # reading a messy paste
    bl = pg.evaluate("l=>splitBlocks(l).map(x=>({l:x.label,g:!!x.guessed,m:x.match,k:x.linked,d:!!x.doubled,t:x.text}))", LYR)
    labels = [x['l'] for x in bl]
    ok(labels == ['Verse', 'Pre-chorus', 'Chorus', 'Verse', 'Pre-chorus', 'Chorus', 'Verse', 'Chorus', 'Chorus'],
       'labels are found in brackets, with a colon, in capitals and with singer names: ' + ', '.join(labels))
    ok(not any('Lyrics' in x['t'] or 'Embed' in x['t'] or 'might also' in x['t'] or 'http' in x['t'] for x in bl),
       'website clutter, links and the "Lyrics" title line are removed')
    ok("it's coming" in bl[1]['t'], 'curly apostrophes become straight ones')
    ok(bl[6]['g'] and bl[6]['l'] == 'Verse' and bl[6]['m'] is None and bl[7]['m'] == 2, 'an unlabelled block is guessed (and flagged), and a [Refrain] links to the chorus')
    ok(bl[8]['d'] and bl[7]['t'] == bl[8]['t'], 'a chorus that repeats itself is split in two')
    ok(bl[5]['m'] == 2 and bl[5]['k'] and bl[4]['m'] == 1, 'exact repeats are linked to the first one')
    ok(pg.evaluate("splitBlocks('').length") == 0 and pg.evaluate("splitBlocks('\\n\\n  \\n').length") == 0, 'an empty paste makes no sections')
    ok(pg.evaluate("titleCase('the long and winding road')") == 'The Long And Winding Road' and pg.evaluate("titleCase('OPM iPhone songs')") == 'OPM iPhone Songs',
       'titles are capitalised, words with capitals already are left alone')

    # the Songs tab, a new song through the sheet
    pg.click('[data-a=tab][data-v=songs]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'songs' and 'Versace on the Floor' in pg.inner_text('main'), 'Songs is a tab, and songs from song practice are in it')
    ok('No lyrics' in pg.inner_text('main'), 'a song without lyrics says so')
    pg.click('#barR [data-a=sgNew]'); pg.wait_for_timeout(400)
    pg.fill('#sgTitle', 'river song'); pg.fill('#sgArtist', 'example band')
    pg.click('[data-a=sgSplit]'); pg.wait_for_timeout(250)
    ok('Paste some lyrics first' in pg.inner_text('.sheet'), 'Next with no lyrics asks for them')
    pg.fill('#sgLyr', LYR); pg.click('[data-a=sgSplit]'); pg.wait_for_timeout(300)
    ok(pg.locator('.sheet .blk').count() == 9 and 'Guessed' in pg.inner_text('.sheet'), 'Label sections shows each block, with guesses marked')
    pg.click('.sheet [data-a=sgBlockLabel][data-k="6"]'); pg.wait_for_timeout(300)
    pg.click('.sheet [data-a=sgPick][data-v=Bridge]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'sgNew' and pg.evaluate("U.sDraft.blocks[6].label") == 'Bridge' and not pg.evaluate("U.sDraft.blocks[6].guessed"),
       'changing a label returns to the list with the guess cleared')
    t.shot(pg, 'label-sections', full_page=True)
    pg.click('.shead [data-a=sgSave]'); pg.wait_for_timeout(400)
    sg = pg.evaluate("songById(U.songId)")
    ok(sg['name'] == 'River Song' and sg['artist'] == 'Example Band', 'the tick saves it, with the title and artist capitalised')
    ok(sg['original'] == LYR, 'the original paste is kept exactly as it was')
    ok(len(sg['order']) == 9 and len(sg['sections']) == 5, 'repeats share one section: 9 in the running order, 5 written once')
    ok(pg.evaluate("U.view") == 'lyr' and pg.locator('.sgsec').count() == 9, 'the new song opens')
    ok(pg.evaluate("[...document.querySelectorAll('.sglab')].map(x=>x.textContent)")[:3] == ['Verse 1', 'Pre-chorus 1', 'Chorus 1'],
       'repeated labels are numbered')
    t.shot(pg, 'song', full_page=True)

    # Perform hides technical marks
    pg.evaluate("const s=songById(U.songId);const sid=s.order[0].sid;s.sections[sid].ann['0:1']={br:1,nt:'Soft'};s.sections[sid].cue='Gentle';save();rerender()")
    ok(pg.locator('.m.br').count() == 1 and pg.locator('.sgnote').count() == 1, 'Practise shows marks and notes')
    pg.click('[data-a=sgMode][data-v=perform]'); pg.wait_for_timeout(400)
    ok(not pg.locator('.m.br').first.is_visible() and pg.locator('.perform .sgcue').first.is_visible(), 'Perform hides marks and keeps cues')
    pg.click('[data-a=sgMode][data-v=practise]'); pg.wait_for_timeout(300)
    pg.click('[data-a=sgKey]'); pg.wait_for_timeout(300); ok('Marks key' in pg.inner_text('.sheet'), 'Key explains the marks'); pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    # Annotate: marks on linked sections, echo and undo
    pg.click('#barR [data-a=sgEdit]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sEdit") == 'annotate' and pg.locator('#barT .seg').count() == 1, 'the pencil opens Annotate | Lyrics in the top bar')
    ch = pg.evaluate("songById(U.songId).order[2].o")
    pg.click(f'.sgsec[data-o="{ch}"] .w >> nth=4'); pg.wait_for_timeout(250)
    ok(pg.locator('#emenu').count() == 1, 'tapping a word opens the marks menu above it')
    pg.click('#emenu [data-v=br]'); pg.wait_for_timeout(250)
    sid = pg.evaluate("songById(U.songId).order[2].sid")
    ok(pg.evaluate(f"songById(U.songId).sections['{sid}'].ann['0:4'].br") == 1, 'Breath marks the word')
    ok(pg.locator('.w.echo').count() >= 1, 'the same word in linked sections is highlighted too')
    pg.click('#emenu [data-v=up]'); pg.click('#emenu [data-v=dn]'); pg.wait_for_timeout(200)
    a = pg.evaluate(f"songById(U.songId).sections['{sid}'].ann['0:4']")
    ok(a.get('dn') == 1 and not a.get('up'), 'Higher and Lower replace each other')
    pg.click('#emenu [data-v=v]'); pg.wait_for_timeout(350); pg.fill('#sgVIn', 'ah'); pg.click('[data-a=sgSaveVowel]'); pg.wait_for_timeout(300)
    ok(pg.evaluate(f"songById(U.songId).sections['{sid}'].ann['0:4'].v") == 'ah' and pg.locator('.w .v').count() >= 1, 'Sing as shows above the word')
    pg.click('[data-a=sgUndo]'); pg.wait_for_timeout(250)
    ok(not pg.evaluate(f"songById(U.songId).sections['{sid}'].ann['0:4'].v"), 'Undo takes the last change back')
    pg.click(f'.sgsec[data-o="{ch}"] [data-a=sgCue]'); pg.wait_for_timeout(300); pg.fill('#sgCueIn', 'Open, full voice'); pg.click('[data-a=sgSaveCue]'); pg.wait_for_timeout(300)
    ok(pg.evaluate(f"songById(U.songId).sections['{sid}'].cue") == 'Open, full voice', 'a cue is added to the section')

    # Lyrics: marks follow their words, a changed word is flagged, a removed one waits
    pg.click('[data-a=sgEditMode][data-v=lyrics]'); pg.wait_for_timeout(400)
    ok(pg.locator('.lyred').count() == 5 and pg.locator('.lyred .mk').count() >= 1, 'Lyrics shows each section once, with marked words highlighted')
    pg.evaluate(f"""()=>{{const e=document.querySelector('.lyred[data-k="{sid}"]');e.innerText='Oh carry me, carry me further\\nLet the river know my name';}}""")
    pg.click('[data-a=sgEditMode][data-v=annotate]'); pg.wait_for_timeout(400)
    ann = pg.evaluate(f"songById(U.songId).sections['{sid}'].ann")
    ok('0:5' in ann and ann['0:5'].get('check') == 1 and ann['0:5'].get('was') == 'over', f'a mark on a changed word moves with it and is flagged to check ({ann})')
    ok(pg.locator('.sgbadge').count() == 0 and pg.locator('.w.chk').count() >= 1, 'flagged words are outlined while editing')
    pg.click(f'.sgsec[data-o="{ch}"] .w.chk >> nth=0'); pg.wait_for_timeout(250)
    ok('Was on “over”' in pg.inner_text('#emenu'), 'the menu says what the word was')
    pg.click('#emenu [data-a=sgCKeep]'); pg.wait_for_timeout(250)
    ok(not pg.evaluate(f"songById(U.songId).sections['{sid}'].ann['0:5'].check"), 'Keep clears the flag')
    v1 = pg.evaluate("songById(U.songId).order[0].sid")
    pg.click('[data-a=sgEditMode][data-v=lyrics]'); pg.wait_for_timeout(400)
    pg.evaluate(f"""()=>{{const e=document.querySelector('.lyred[data-k="{v1}"]');e.innerText='Paper along the gutter\\nRacing rain down Elmwood Lane';}}""")
    pg.click('[data-a=sgDone]'); pg.wait_for_timeout(400)
    s1 = pg.evaluate(f"songById(U.songId).sections['{v1}']")
    ok(len(s1['orphans']) == 1 and s1['orphans'][0]['was'] == 'boats' and s1['orphans'][0]['ann'].get('nt') == 'Soft', 'a mark whose word was removed is kept to move or remove')
    ok(pg.locator('.sgbadge').inner_text() == '1', 'the pencil shows how many marks to check')
    pg.click('#barR [data-a=sgEdit]'); pg.wait_for_timeout(250)
    ok('was on “boats”, which was removed' in pg.inner_text('main'), 'the removed word is explained at the top of its section')
    pg.click('[data-a=sgOMove]'); pg.wait_for_timeout(250)
    pg.click(f'.sgsec[data-o="{pg.evaluate("songById(U.songId).order[0].o")}"] .w >> nth=2'); pg.wait_for_timeout(250)
    ok(pg.evaluate(f"songById(U.songId).sections['{v1}'].ann['0:2'].nt") == 'Soft' and not pg.evaluate(f"songById(U.songId).sections['{v1}'].orphans.length"),
       'Move puts the mark on the word you tap')

    # Unlink, reorder
    p2 = pg.evaluate("songById(U.songId).order[4].o")
    pg.click(f'.sgsec[data-o="{p2}"] [data-a=sgUnlink]'); pg.wait_for_timeout(300)
    ok('can’t be linked back' in pg.inner_text('.sheet'), 'Unlink asks first')
    pg.click('[data-a=sgDoUnlink]'); pg.wait_for_timeout(300)
    s = pg.evaluate("songById(U.songId)")
    ok(s['order'][4]['sid'] != s['order'][1]['sid'] and len(s['sections']) == 6, 'Unlink gives that section its own copy')
    before = [x['o'] for x in s['order']]
    pg.evaluate("window.scrollTo(0,0)")
    box = pg.locator('.sgsec >> nth=0').bounding_box()
    pg.mouse.move(box['x'] + 30, box['y'] + 12); pg.mouse.down(); pg.wait_for_timeout(650)
    ok(pg.locator('.crow').count() == 9, 'holding a section shows compact rows to drag')
    r2 = pg.locator('.crow >> nth=2').bounding_box()
    for i in range(1, 11): pg.mouse.move(box['x'] + 30, r2['y'] + r2['height'] / 2 * i / 10 + 20 + i * 2)
    pg.mouse.up(); pg.wait_for_timeout(400)
    after = [x['o'] for x in pg.evaluate("songById(U.songId).order")]
    ok(after != before and sorted(after) == sorted(before), 'dragging reorders the sections')
    pg.click('[data-a=sgUndo]'); pg.wait_for_timeout(250)
    ok([x['o'] for x in pg.evaluate("songById(U.songId).order")] == before, 'and Undo puts them back')
    pg.click('[data-a=sgDone]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sEdit") is None, 'Done leaves editing')
    saved = json.loads(pg.evaluate("localStorage.getItem('vocalTracker')"))
    ok(any(x.get('sections') for x in saved['songs']), 'lyrics and marks are saved')

    # a song with no lyrics gets them added, keeping its recordings
    pg.evaluate("putTake({id:'tz',songId:'g_1',created:Date.now()-3600e3,len:9,size:10,type:'audio/mp4',star:false,blob:new Blob([new Uint8Array(10)])}).then(refreshTakes).then(rerender)")
    pg.wait_for_timeout(300)
    pg.click('[data-a=sgBack]'); pg.wait_for_timeout(250)
    pg.click('.rowc[data-k=g_1]'); pg.wait_for_timeout(300)
    ok('No lyrics yet' in pg.inner_text('main'), 'a song without lyrics offers to add them')
    pg.click('[data-a=sgAddLyrics]'); pg.wait_for_timeout(350)
    ok(pg.input_value('#sgTitle') == 'Versace on the Floor · bridge', 'its title is filled in')
    pg.fill('#sgLyr', '[Bridge]\nLet me unzip this dress\nLet me give you a song'); pg.click('[data-a=sgSplit]'); pg.wait_for_timeout(300)
    pg.click('.sheet .cta[data-a=sgSave]'); pg.wait_for_timeout(400)
    g = pg.evaluate("songById('g_1')")
    ok(g and len(g['order']) == 1 and pg.evaluate("TAKES.some(t=>t.songId==='g_1')") and len(pg.evaluate("D.songs")) == 2, 'the lyrics join the same song, which keeps its takes')

    # song practice from a song
    pg.click('[data-a=sgPractise]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'song' and pg.evaluate("X.song") == 'g_1', 'Song practice opens with this song picked')
    pg.click('[data-a=sheet][data-v=discard]'); pg.wait_for_timeout(300); pg.click('[data-a=discardYes]'); pg.wait_for_timeout(300)

    # the list: pins (up to 3), sorting, swipe, press and hold, select
    for n in ['Kitchen radio', 'paper lanterns', 'Morning light']:
        pg.evaluate(ADD, [n, '', '[Verse]\nA line for ' + n + '\n\n[Chorus]\nSing it out for ' + n])
    pg.evaluate("U.tab='songs';U.view=null;render()"); pg.wait_for_timeout(250)
    ok(pg.locator('.newtag').count() >= 3, 'songs never practised are marked New')
    for i in range(4):
        pg.evaluate(f"togglePin(sortedSongs(D.songs.filter(s=>!s.pinned))[0].id)")
    pg.wait_for_timeout(300)
    ok(pg.evaluate("D.songs.filter(s=>s.pinned).length") == 3 and pg.evaluate("U.sheet") == 'sgPinFull', 'a fourth pin asks which song to unpin')
    pg.click('.sheet [data-a=sgSwapPin] >> nth=0'); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.songs.filter(s=>s.pinned).length") == 3 and pg.evaluate("U.sheet") is None, 'and swaps them')
    ok(pg.inner_text('.hdr >> nth=0') == 'PINNED' or pg.inner_text('.hdr >> nth=0').lower() == 'pinned', 'pinned songs are at the top')
    pg.click('#hdrsort'); pg.wait_for_timeout(250); pg.click('#sortmenu [data-v=az]'); pg.wait_for_timeout(250)
    rest = pg.evaluate("[...document.querySelectorAll('.grp:last-of-type .rowc b')].map(x=>x.textContent)")
    ok(rest == sorted(rest, key=str.lower) and pg.evaluate("JSON.parse(localStorage.getItem('vocalSongPrefs')).sort") == 'az', 'the sort menu sorts, and is remembered')
    # swipe right to pin, left to delete
    rid = pg.evaluate(ADD, ['Spare song', '', 'Just one line'])
    ren = pg.evaluate(ADD, ['Old name', '', 'Another line'])
    pg.evaluate("U.tab='songs';U.view=null;render()"); pg.wait_for_timeout(250)
    row = pg.locator(f'.rowc[data-k="{rid}"]'); rb = row.bounding_box()
    pg.mouse.move(rb['x'] + 40, rb['y'] + 20); pg.mouse.down()
    for i in range(1, 9): pg.mouse.move(rb['x'] + 40 - i * 15, rb['y'] + 22)
    pg.mouse.up(); pg.wait_for_timeout(450)
    ok(pg.locator(f'.rowc[data-k="{rid}"]').evaluate("e=>+e.dataset.x") == -88, 'swiping left shows Delete')
    t.shot(pg, 'swipe')
    pg.click(f'.srow:has(.rowc[data-k="{rid}"]) .act.del'); pg.wait_for_timeout(350)
    ok(pg.evaluate("U.sheet") == 'sgDel' and 'can’t be undone' in pg.inner_text('.sheet'), 'delete asks first')
    pg.click('[data-a=sgDoDel]'); pg.wait_for_timeout(400)
    ok(not pg.evaluate(f"!!songById('{rid}')"), 'and deletes the song')
    # press and hold
    row = pg.locator(f'.rowc[data-k="{ren}"]'); rb = row.bounding_box()
    pg.mouse.move(rb['x'] + 60, rb['y'] + 20); pg.mouse.down(); pg.wait_for_timeout(650); pg.mouse.up(); pg.wait_for_timeout(300)
    ok(pg.locator('#ctxmenu').count() == 1 and pg.evaluate("U.view") is None, 'press and hold opens Pin, Rename, Delete without opening the song')
    t.shot(pg, 'hold-menu')
    pg.click('[data-a=sgCtxRename]'); pg.wait_for_timeout(350); pg.fill('#sgRenIn', 'renamed song'); pg.click('[data-a=sgSaveRename]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.songs.some(s=>s.name==='Renamed Song')"), 'Rename capitalises too')
    # select
    pg.click('#barR [data-a=sgListEdit]'); pg.wait_for_timeout(250)
    ok(pg.locator('.selc').count() == len(pg.evaluate("D.songs")) and pg.locator('.etool').count() == 1, 'Edit shows select circles and a Pin / Delete toolbar')
    pg.click('#barL [data-a=sgSelAll]'); pg.wait_for_timeout(200)
    ok('selected' in pg.inner_text('#barT'), 'Select all selects every song')
    pg.click('#barL [data-a=sgSelAll]'); pg.click('#barR [data-a=sgListDone]'); pg.wait_for_timeout(200)

    # search
    pg.click('[data-a=sgSearch]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("document.activeElement.id") == 'sgqb' and pg.locator('#sgbar').is_visible() and pg.locator('#dock .tabbar').count() == 0,
       'search opens at the bottom, with the tab bar shrunk to a circle')
    for q, want in [('carry further', 'River Song'), ('KITCHEN', 'Kitchen Radio'), ('elmwood', 'River Song'), ('candls', 'River Song'),
                    ('carry dress', None), ('lanterns sing', 'Paper Lanterns'), ('example', 'River Song')]:
        pg.fill('#sgqb', q); pg.wait_for_timeout(150)
        got = pg.evaluate("[...document.querySelectorAll('#slist .rowc b')].map(x=>x.textContent)")
        ok((want in got) if want else not got, f'search "{q}" finds {want or "nothing"} ({got})')
    pg.fill('#sgqb', 'elmwood'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    ok(pg.locator('.hitline mark').count() >= 1, 'a lyric match shows the line with the words highlighted')
    pg.click('#slist .rowc >> nth=0'); pg.wait_for_timeout(300); pg.click('[data-a=sgBack]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sFocus") and pg.input_value('#sgqb') == 'elmwood', 'back from a result returns to the results')
    pg.click('[data-a=sgQClear]'); pg.wait_for_timeout(200)
    ok('elmwood' in pg.inner_text('main'), 'recent searches are listed')
    pg.mouse.click(200, 500); pg.wait_for_timeout(250)
    ok(not pg.evaluate("U.sFocus") and pg.locator('#dock .tabbar').count() == 1, 'tapping empty space ends an empty search')

    # Today's pinned songs
    pg.click('[data-a=tab][data-v=today]'); pg.wait_for_timeout(250)
    ok('pinned songs' in pg.inner_text('main').lower() and pg.locator('main [data-a=sgOpen][data-v=today]').count() == 3, 'Today lists pinned songs')
    pg.click('main [data-a=sgOpen][data-v=today] >> nth=0'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") == 'lyr', 'a pinned song opens from Today')
    pg.click('[data-a=sgBack]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'today', 'and Back returns to Today')
    pg.click('[data-a=sgAll]'); pg.wait_for_timeout(250); ok(pg.evaluate("U.tab") == 'songs', 'Show all songs opens Songs')

    # Settings is the gear on Today
    pg.click('[data-a=tab][data-v=today]'); pg.wait_for_timeout(200)
    pg.click('#barR [data-a=openSettings]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.tab") == 'settings' and pg.locator('#dock .tabbar button.on').get_attribute('data-v') == 'today', 'the gear opens Settings, under Today')
    pg.click('[data-a=setBack]'); pg.wait_for_timeout(250); ok(pg.evaluate("U.tab") == 'today', 'Back returns to Today')
    ok(pg.locator('#dock .tabbar [data-a=tab]').count() == 4 and pg.locator('#dock .tabbar [data-v=settings]').count() == 0, 'the tab bar is Today, Progress, Exercises, Songs')

    # backup round trip
    pg.evaluate("U.tab='settings';render()")
    with pg.expect_download() as dl:
        pg.click('[data-a=exportPrep]'); pg.wait_for_function("U.sheet==='exportReady'", timeout=8000); pg.click('[data-a=exportSave]')
    path = os.path.join(OUT, 'songs-backup.json'); dl.value.save_as(path)
    bk = json.load(open(path, encoding='utf-8'))
    ok(any(s.get('sections') and s.get('original') for s in bk['data']['songs']), 'a backup holds the songs with their lyrics, marks and original paste')
    before = pg.evaluate("JSON.stringify(D.songs)")
    pg.evaluate("D.songs=[];save()")
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(path); pg.wait_for_function("U.sheet==='bkReport'", timeout=8000)
    pg.click('[data-a=importYes]'); pg.wait_for_timeout(1200)
    after = json.loads(pg.evaluate("JSON.stringify(D.songs)")); was = json.loads(before)
    ok(after == was, 'restoring it brings every song back exactly' + ('' if after == was else f' — {[(a, b) for a, b in zip(after, was) if a != b][:1]}'))
    pg.context.close()

    # older songs, damaged songs and future fields
    d = sample()
    good = {"id": "g_2", "name": "Good", "artist": "A", "pinned": True, "added": 1700000000000, "future": {"x": 1},
            "sections": {"x1": {"label": "Chorus", "cue": "", "lines": [["la", "la"]], "ann": {"0:1": {"br": 1, "later": 2}, "5:5": {"br": 1}}, "orphans": [], "colour": "red"}},
            "order": [{"o": "o1", "sid": "x1"}, {"o": "o2", "sid": "missing"}]}
    broken = {"id": "g_3", "name": "Broken", "sections": "oops", "order": [], "original": "[Verse]\nOne two\n\n[Chorus]\nThree four"}
    junk = [None, 5, {"id": "g_4"}, {"name": "no id"}, {"id": "g_5", "name": "Bad bits", "artist": 7, "pinned": "yes", "added": "never", "sections": {}, "order": "x"}]
    d['songs'] = d['songs'] + [good, broken] + junk
    pg = t.page(b, data=d)
    S = pg.evaluate("D.songs")
    ids = [s['id'] for s in S]
    ok(ids == ['g_1', 'g_2', 'g_3', 'g_5'], f'each song is checked on its own: damaged ones are dropped, the rest kept ({ids})')
    g2 = next(s for s in S if s['id'] == 'g_2')
    ok(g2['future'] == {'x': 1} and g2['sections']['x1']['colour'] == 'red' and g2['sections']['x1']['ann']['0:1']['later'] == 2,
       'fields from a newer version are kept')
    ok('5:5' not in g2['sections']['x1']['ann'] and len(g2['order']) == 1, 'marks on missing words and missing sections are dropped')
    g3 = next(s for s in S if s['id'] == 'g_3')
    ok(len(g3.get('order', [])) == 2 and g3['sections'][g3['order'][1]['sid']]['label'] == 'Chorus', 'damaged lyrics are rebuilt from the original paste')
    g5 = next(s for s in S if s['id'] == 'g_5')
    ok(g5['artist'] == '' and g5['pinned'] is False and g5['added'] > 0 and 'sections' not in g5, 'bad values are replaced with defaults')
    g1 = next(s for s in S if s['id'] == 'g_1')
    ok(g1['name'] == 'Versace on the Floor · bridge' and g1['artist'] == '' and g1['pinned'] is False and g1['added'] > 0, 'a song from before 3.8 is upgraded')
    pg.evaluate("U.tab='songs';render()"); pg.wait_for_timeout(200)
    ok(pg.locator('.rowc').count() == 4, 'every kept song shows in Songs')
    pg.click('.rowc[data-k=g_3]'); pg.wait_for_timeout(300)
    ok(pg.locator('.sgsec').count() == 2, 'the rebuilt song opens')
    pg.context.close()

    # an empty app
    pg = t.page(b, data=None)
    pg.click('[data-a=tab][data-v=songs]'); pg.wait_for_timeout(250)
    ok('Add your first song' in pg.inner_text('main') and pg.locator('[data-a=sgSearch]').count() == 0, 'with no songs, Songs invites you to add one')
    t.shot(pg, 'empty')
    pg.context.close()

    # iPad and Mac: list and song side by side, keyboard shortcuts
    for name, w, h in [('ipad', 820, 1180), ('mac', 1440, 900)]:
        pg = t.page(b, w, h, data=with_song_practice(), **({'ua': None} if name == 'mac' else {}))
        pg.evaluate(ADD, ['River song', 'Example band', LYR]); pg.evaluate(ADD, ['Kitchen radio', '', '[Verse]\nCoffee on the counter\n\n[Chorus]\nTurn it up'])
        pg.evaluate("U.tab='songs';U.view=null;render()"); pg.wait_for_timeout(300)
        ok(pg.locator('.sgcol .rowc').count() == 3 and pg.locator('.sgpane .sgsec').count() > 0, f'{name}: songs on the left, the open song on the right')
        pg.click('.sgcol .rowc[data-k] >> text=River Song'); pg.wait_for_timeout(300)
        ok('River Song' in pg.inner_text('.sgpane h1') and pg.evaluate("U.view") is None, f'{name}: tapping a song shows it beside the list')
        pg.keyboard.press('Control+e'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.sEdit") == 'annotate' and pg.locator('.sgpane .sgedit').count() == 1, f'{name}: Cmd+E edits the song')
        pg.click('.sgpane .sgsec >> nth=0 >> .w >> nth=0'); pg.wait_for_timeout(250)
        ok(pg.locator('#emenu').count() == 1, f'{name}: the marks menu opens')
        t.shot(pg, name + '-edit')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200); ok(pg.locator('#emenu').count() == 0, f'{name}: Escape closes it')
        pg.keyboard.press('Control+e'); pg.wait_for_timeout(250); ok(pg.evaluate("U.sEdit") is None, f'{name}: Cmd+E again is Done')
        pg.keyboard.press('Control+f'); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.activeElement.id") == 'sgqi', f'{name}: Cmd+F searches songs')
        pg.keyboard.type('turn'); pg.wait_for_timeout(200)
        ok(pg.evaluate("[...document.querySelectorAll('#slist .rowc b')].map(x=>x.textContent)") == ['Kitchen Radio'] and pg.evaluate("document.activeElement.id") == 'sgqi',
           f'{name}: results update as you type, keeping the keyboard')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        pg.locator('body').click(position={'x': w - 40, 'y': h - 40}); pg.wait_for_timeout(100)
        cur = pg.evaluate("U.songId"); pg.keyboard.press('ArrowDown'); pg.wait_for_timeout(250)
        ok(pg.evaluate("U.songId") != cur, f'{name}: arrow keys move between songs')
        pg.keyboard.press('Control+4'); pg.wait_for_timeout(200); ok(pg.evaluate("U.tab") == 'songs', f'{name}: Cmd+4 opens Songs')
        pg.keyboard.press('Control+,'); pg.wait_for_timeout(200); ok(pg.evaluate("U.tab") == 'settings', f'{name}: Cmd+, opens Settings')
        pg.context.close()

    # rotating an iPad while a song is open keeps it open
    pg = t.page(b, 700, 1000, touch=True, data=with_song_practice())
    pg.set_viewport_size({'width': 600, 'height': 1000}); pg.wait_for_timeout(200)
    sid = pg.evaluate(ADD, ['River song', '', LYR]); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.view") == 'lyr', 'narrow: the song opens on its own screen')
    pg.set_viewport_size({'width': 900, 'height': 1000}); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.view") is None and pg.evaluate("U.tab") == 'songs' and pg.evaluate("U.songId") == sid and pg.locator('.sgpane .sgsec').count() > 0,
       'wider: the same song shows beside the list')
    pg.context.close()
