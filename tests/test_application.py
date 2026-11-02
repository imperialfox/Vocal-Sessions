"""Q20 Application: carry on where you left off (the last song and section, Whole song for a song with no sections),
Sing over the track (remembered, headphones by default through Q16's sheet, the speaker after its confirmation, the
track starting just before the section), the card while it records (the page still, the red track window), takes with
their waveforms, Star, Compare from the same moment (one sound at a time), ↻ Again, Done folding the song to a line,
"Practised, not recorded", Other songs and their sort, finishing without "How did it go?" (old answers still shown,
the chips still on the edit sheet), Song practice's shared take rows, Reduce Motion and motion on, and 390 and 375 in
light and dark. Synthetic data only: tones made in the test, a fake microphone."""
import json
from harness import until, with_song_practice, fix
from test_clock import LYR, ADD, SPREAD
from test_batch12 import add_track, wav_take
from test_track import track

LAUNCH_ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']
WIDE = "document.documentElement.scrollWidth<=innerWidth+1"
CARD = '#app .osec.active #apcard'
MOTION_ON = "try{localStorage.setItem('vocalMotion','1')}catch(e){}"


def to_app(pg):
    """A session straight to Application, as Foundation and Rotation's buttons would get there."""
    pg.evaluate("U.sheet=null;go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(100)
    pg.click('[data-a=start]'); pg.wait_for_timeout(150)
    pg.evaluate("FOUND.forEach(e=>X.f[e.id]=2);X.fEnd=Date.now();X.fE=elapsedSec();saveDraft();OP.advance()")
    pg.wait_for_timeout(150)
    pg.evaluate("OP.advance()"); pg.wait_for_timeout(200)


def lyric_song(pg, timed=True):
    """Harbour Lights with sections; timed, so Chorus starts at 20 s on the track."""
    sid = pg.evaluate(ADD, ['Harbour Lights', 'Test', LYR]); pg.wait_for_timeout(300)
    if timed:
        n = pg.evaluate("id=>songById(id).order.length", sid)
        pg.evaluate(SPREAD, [sid, [i * 20 for i in range(n)]])
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.wait_for_timeout(150)
    return sid


def occ(pg, sid, i): return pg.evaluate("([id,i])=>songById(id).order[i].o", [sid, i])


def sing(pg, secs=1.2):
    """Sing, wait, Stop, and wait for the take to be saved."""
    n = pg.evaluate("TAKES.length")
    pg.click(f'{CARD} [data-a=apSing]')
    until(pg, "!!rec&&!!document.querySelector('#apcard.rec')", 8000)
    pg.wait_for_timeout(int(secs * 1000))
    pg.click('#apcard [data-a=apStop]')
    until(pg, f"!rec&&TAKES.length==={n + 1}", 8000)
    pg.wait_for_timeout(250)


def carry_on(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid = lyric_song(pg)
    ch = occ(pg, sid, 1)
    # last time: a take of Harbour Lights' Chorus, two days ago, and an older one of the plain song
    pg.evaluate(wav_take(3), ['old1', 'g_1', None, 60 * 24 * 5])
    pg.evaluate(wav_take(3), ['old2', sid, ch, 60 * 24 * 2])
    to_app(pg)
    st = pg.evaluate("APPL.state()")
    ok(st['id'] == sid and st['o'] == ch and st['carry'], 'Carry on picks up the last song and section: ' + json.dumps(st))
    txt = pg.inner_text(CARD)
    ok('CARRY ON' in txt.upper() and 'Harbour Lights · Chorus' in txt and 'Last sung 2 days ago · 1 take' in txt, 'the card says where you left off: ' + txt.replace('\n', ' | '))
    ok(pg.locator(f'{CARD} [data-a=apSing]').inner_text().strip() == 'Sing' and pg.locator(f'{CARD} [data-a=apNoRec]').count() == 1
       and pg.locator(f'{CARD} [data-a=apSecs]').count() == 1, 'Sing, Change section and Practised, not recorded')
    ok(pg.locator(f'{CARD} [data-a=apOver]').count() == 0, 'no Sing over the track without a track on this device')
    ok(pg.inner_text('#dock [data-a=cta]').strip() == 'Skip and finish' and 'Pick a song' in pg.inner_text('#opHint'),
       'nothing sung yet: Skip and finish')
    # Other songs, with their sort heading
    ok(pg.locator('#app .apsongs [data-a=apSong]').count() == 1 and 'OTHER SONGS' in pg.inner_text('#app [data-a=apSort]').upper(),
       'Other songs, under a sort heading')
    ok('whole song' in pg.inner_text('#app .apsongs'), 'a song with no sections says whole song')
    t.shot(pg, 'carry-on')
    # change section: pills for Whole song and each place
    pg.click(f'{CARD} [data-a=apSecs]'); pg.wait_for_timeout(100)
    pills = pg.locator(f'{CARD} .appill').all_inner_texts()
    ok(pills[0] == 'Whole song' and len(pills) == 1 + pg.evaluate("id=>songById(id).order.length", sid), 'Change section shows Whole song and every place: ' + json.dumps(pills))
    pg.click(f'{CARD} .appill >> nth=0'); pg.wait_for_timeout(100)
    ok(pg.evaluate("APPL.state().o") is None and 'Harbour Lights' in pg.inner_text(CARD) and '·' not in pg.inner_text(f'{CARD} .apname'),
       'Whole song picked')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('vocalDraft')).sing") == {'id': sid, 'o': None, 'st': 'open'}, 'the card is kept on the draft')
    # another song: a song with no sections is always Whole song
    pg.click('#app [data-a=apSong][data-k=g_1]'); pg.wait_for_timeout(150)
    st = pg.evaluate("APPL.state()")
    ok(st['id'] == 'g_1' and st['o'] is None and pg.locator(f'{CARD} [data-a=apSecs]').count() == 0, 'a song with no sections falls back to Whole song, with no Change section')
    # the sort menu
    pg.click('#app [data-a=apSort]'); pg.wait_for_timeout(100)
    ok(pg.locator('.opmenu [data-a=apSortPick]').count() == 2, 'the sort menu: Recently practised and A–Z')
    pg.click('.opmenu [data-v=az]'); pg.wait_for_timeout(100)
    ok('A–Z' in pg.inner_text('#app [data-a=apSort]') and pg.locator('.opmenu').count() == 0, 'A–Z picked, the menu closes')
    pg.context.close()

    # a song whose carried-on section has gone, and a session's "practised, not recorded" song
    pg = t.page(b, touch=True)
    sid = lyric_song(pg, timed=False)
    pg.evaluate("([id])=>{D.sessions.push({id:'sx',date:new Date(Date.now()-864e5).toISOString(),end:new Date(Date.now()-864e5+18e5).toISOString(),mins:30,f:{},rot:{},xn:{},rate:{},takes:[],how:[],howNote:'',songName:'Harbour Lights',ext:{app:{song:id,o:'gone',noRec:true}}});save()}", [sid])
    to_app(pg)
    st = pg.evaluate("APPL.state()")
    ok(st['id'] == sid and st['o'] is None, 'a practised-not-recorded session is where you left off; a section that’s gone falls back to Whole song')
    ok('Last sung yesterday' in pg.inner_text(CARD), 'it counts as sung: ' + pg.inner_text(CARD).replace('\n', ' | '))
    pg.context.close()


def singing(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid = lyric_song(pg)
    ch = occ(pg, sid, 1)
    add_track(pg, sid, track())
    pg.evaluate(wav_take(3), ['old2', sid, ch, 60 * 24 * 2])
    to_app(pg)
    ok(pg.locator(f'{CARD} [data-a=apOver]').count() == 1 and pg.get_attribute(f'{CARD} [data-a=apOver]', 'aria-checked') == 'true',
       'Sing over the track, on by default')
    want = pg.evaluate("([id,o])=>APPL.startAt(songById(id),o)", [sid, ch])
    ok(abs(want - 20) < 0.6, 'the Chorus starts at 20 s on the track: ' + str(want))
    # Sing: Q16's sheet asks first (headphones by default)
    pg.click(f'{CARD} [data-a=apSing]')
    ok(until(pg, "U.sheet==='recOver'") and not pg.evaluate("!!rec") and not pg.evaluate("TRACK.state().playing"),
       'Sing over the track asks first, with nothing playing yet')
    t.shot(pg, 'headphones')
    pg.click('.sheet [data-a=recOver][data-v=hp]')
    ok(until(pg, "!!rec&&rec.app&&NOW.under()==='track'", 8000), 'with headphones it records over the track')
    pg.wait_for_timeout(500)
    tt = pg.evaluate("TRACK.state().t")
    ok(17.5 <= tt <= 20.5 and pg.evaluate("rec.from") == 18, 'the track starts just before the Chorus: ' + str(tt))
    ok(pg.locator('#apcard.rec').count() == 1 and 'Recording · track from 0:18' in pg.inner_text('#apcard') and 'Hold on hold on' in pg.inner_text('#apcard'),
       'the card is the recording: the section, the track, its words and Stop')
    ok(until(pg, "FW.shown==='rectrack'&&!document.getElementById('fw').hidden"), 'the floating window is the red track window')
    ok('Harbour Lights · Chorus' in pg.inner_text('#fw') and pg.evaluate("document.getElementById('fw').dataset.kind") == 'rectrack',
       'it shows the song and section: ' + pg.inner_text('#fw').replace('\n', ' | '))
    ok(pg.evaluate("document.body.classList.contains('apprec')") and pg.evaluate("getComputedStyle(document.getElementById('dock')).pointerEvents") == 'none'
       and pg.locator('#app .apsongs').count() == 0, 'the rest of the page steps back while it records')
    ok(pg.evaluate("U.view") == 'app' and pg.locator('#dock .recbar').count() == 0, 'no recording bar: the card has Stop')
    t.shot(pg, 'recording')
    y0 = pg.evaluate("scrollY"); pg.wait_for_timeout(600)
    ok(pg.evaluate("scrollY") == y0, 'the page stays still while it records')
    pg.click('#apcard [data-a=apStop]')
    ok(until(pg, "!rec&&TAKES.length===2", 8000), 'Stop saves the take')
    pg.wait_for_timeout(300)
    ok(not pg.evaluate("TRACK.state().playing") and pg.evaluate("FW.shown") != 'rectrack', 'the track stops with the take')
    tk = pg.evaluate("TAKES[TAKES.length-1]")
    ok(tk['o'] == ch and tk['songId'] == sid and pg.evaluate("X.takes") == [tk['id']] and pg.evaluate("X.song") == sid,
       'the take is the Chorus’s, and joins the session')
    ok(pg.locator(f'{CARD} .tkrow').count() == 1 and 'Take 2' in pg.inner_text(f'{CARD} .tkrow') and 'new' in pg.inner_text(f'{CARD} .tkrow'),
       'the new take shows, as Take 2')
    ok(until(pg, "!!document.querySelector('#apcard .tkwv:not(.wait)')", 8000), 'with its waveform once it’s been read')
    ok(pg.locator(f'{CARD} .apcmp').count() == 1 and pg.locator(f'{CARD} .apcmp button').all_inner_texts() == ['This take', 'Take 1'],
       'Compare: This take | Take 1 (the one before, from another day)')
    ok(pg.locator(f'{CARD} [data-a=apSing]').inner_text().strip() == '↻ Again' and pg.locator(f'{CARD} [data-a=apDone]').count() == 1, '↻ Again and Done')
    ok(pg.inner_text('#dock [data-a=cta]').strip() == 'Finish session', 'something sung: Finish session')
    t.shot(pg, 'take')
    # ↻ Again: headphones remembered, so it records over the track straight away
    pg.click(f'{CARD} [data-a=apSing]')
    ok(until(pg, "!!rec&&rec.app&&rec.over==='hp'", 8000) and pg.evaluate("U.sheet") is None, '↻ Again records the same section over the track without asking again')
    pg.wait_for_timeout(1100)
    pg.click('#apcard [data-a=apStop]'); until(pg, "!rec&&TAKES.length===3", 8000); pg.wait_for_timeout(300)
    ok(pg.evaluate("TAKES[TAKES.length-1].o") == ch and pg.locator(f'{CARD} .tkrow').count() == 2, 'the second take, the same section')
    ok(pg.locator(f'{CARD} .apcmp button').all_inner_texts() == ['This take', 'Take 2'], 'Compare is with the take before')
    # Compare: one sound at a time, from the same moment
    new, prev = pg.evaluate("[TAKES[2].id,TAKES[1].id]")
    pg.click(f'{CARD} .tkrow[data-tk="{new}"] [data-a=playTake]')
    ok(until(pg, f"playingId==='{new}'&&!!player&&!player.paused&&player.currentTime>0.5", 6000), 'the new take plays')
    at = pg.evaluate("player.currentTime")
    pg.click(f'{CARD} .apcmp [data-v="1"]')
    ok(until(pg, f"playingId==='{prev}'&&!!player&&!player.paused", 6000), 'Compare switches to the take before')
    ok(abs(pg.evaluate("player.currentTime") - at) < 0.8, 'from the same moment')
    ok(pg.evaluate("NOW.kind()") == 'take' and pg.evaluate("document.querySelectorAll('#app .tkrow.playing').length") == 1, 'only one take plays')
    ok('on' in pg.get_attribute(f'{CARD} .apcmp [data-v="1"]', 'class'), 'its side of Compare is selected')
    pg.click(f'{CARD} .apcmp [data-v="0"]')
    ok(until(pg, f"playingId==='{new}'&&!!player&&!player.paused", 6000), 'and back')
    pg.click(f'{CARD} .apcmp [data-v="0"]')
    ok(until(pg, "!playingId"), 'tapping the one that plays stops it')
    # Star
    pg.click(f'{CARD} .tkrow[data-tk="{new}"] [data-a=star]')
    ok(until(pg, f"TAKES.find(t=>t.id==='{new}').star===true"), 'Star marks the keeper')
    # the speaker: asks again, and says it may be heard
    pg.evaluate("REC_OVER.hp=false")
    pg.click(f'{CARD} [data-a=apSing]'); until(pg, "U.sheet==='recOver'")
    pg.click('.sheet [data-a=recOver][data-v=spk]')
    ok(until(pg, "!!rec&&rec.over==='spk'", 8000), 'through the speaker after its confirmation')
    pg.wait_for_timeout(1000)
    pg.click('#apcard [data-a=apStop]'); until(pg, "!rec&&TAKES.length===4", 8000); pg.wait_for_timeout(300)
    # without the track
    pg.click(f'{CARD} [data-a=apDone]'); until(pg, "APPL.state().st==='done'")
    pg.click(f'{CARD} [data-a=apReopen]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("APPL.state().st") == 'open', 'Edit opens the song again')
    pg.evaluate("U.sheet=null;X.sing.o=null;saveDraft();rerender()")
    pg.evaluate("sgp().singOver=false;saveSGP();rerender()")
    ok(pg.evaluate("APPL.state().over") is False, 'the switch can be off')
    sing(pg, 1.0)
    ok(pg.evaluate("TAKES[TAKES.length-1].o") is None and not pg.evaluate("TRACK.state().playing"), 'Whole song without the track records on its own')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')", timeout=15000); pg.wait_for_timeout(200)
    ok(pg.evaluate("sgp().singOver") is False, 'the switch is remembered')
    pg.context.close()


def done_and_norec(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)
    sid = lyric_song(pg)
    to_app(pg)
    pg.click('#app [data-a=apSong][data-k=g_1]'); pg.wait_for_timeout(150)
    sing(pg)
    sing(pg)
    ok(pg.locator(f'{CARD} .tkrow').count() == 2 and pg.locator(f'{CARD} .apcmp').count() == 1, 'two takes, with Compare')
    first = pg.evaluate("X.takes[0]")
    pg.click(f'{CARD} .tkrow[data-tk="{first}"] [data-a=star]'); until(pg, f"TAKES.find(t=>t.id==='{first}').star")
    pg.click(f'{CARD} [data-a=apDone]')
    ok(until(pg, "APPL.state().st==='done'"), 'Done')
    line = pg.inner_text('#apcard').replace('\n', ' ')
    ok('Versace on the Floor · bridge · 2 takes · ★ Take 1' in line and pg.locator('#app .apsongs').count() == 0, 'the song folds to its summary line: ' + line)
    t.shot(pg, 'done')
    # finishing: no "How did it go?"
    pg.click('#dock [data-a=cta]')
    ok(until(pg, "X===null&&U.view==='saved'&&!U.sheet"), 'finishing goes straight on to Session saved, with no How did it go?')
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss['songName'] == 'Versace on the Floor · bridge' and len(ss['takes']) == 2 and ss['how'] == [] and ss['ext'] == {'app': {'song': 'g_1'}},
       'the session keeps its song and takes: ' + json.dumps(ss.get('ext')))
    # the edit sheet still has the words
    pg.click('[data-a=savedDone]'); until(pg, "U.view===null")
    pg.evaluate("U.sheet='session';U.sd={k:D.sessions[D.sessions.length-1].id};rerender()")  # Q21: its sheet, as from the calendar
    pg.click('[data-a=editSess]'); until(pg, "U.sheet==='edit'")
    ok(pg.locator('.sheet [data-a=wTog][data-v="In control"]').count() == 1, 'How it went can still be added on the edit sheet')
    pg.evaluate("U.sheet=null;rerender()")
    # Practised, not recorded
    to_app(pg)
    ok(pg.evaluate("APPL.state().id") == 'g_1', 'the next session carries on with that song')
    pg.click('#app [data-a=apSong][data-k="' + sid + '"]'); pg.wait_for_timeout(150)
    pg.click(f'{CARD} [data-a=apNoRec]')
    ok(until(pg, "APPL.state().st==='norec'") and 'practised, not recorded' in pg.inner_text('#apcard'), 'Practised, not recorded folds the song')
    ok(pg.locator('#app [data-a=rate]').count() == 0 and 'Rate the song' not in pg.inner_text('#app'), 'with no Rate the song under it (Q29)')
    t.shot(pg, 'norec')
    ok(pg.inner_text('#dock [data-a=cta]').strip() == 'Finish session', 'and counts as Application')
    pg.click('#dock [data-a=cta]'); until(pg, "X===null")
    ss = pg.evaluate("D.sessions[D.sessions.length-1]")
    ok(ss['songName'] == 'Harbour Lights' and ss['takes'] == [] and ss['ext']['app']['noRec'] is True, 'saved: a song practised with no take')
    to_app(pg)
    ok(pg.evaluate("APPL.state().id") == sid, 'Carry on picks it up next time')
    pg.context.close()


def old_answers(b, t):
    ok = t.ok
    d = with_song_practice()
    d['sessions'][-1]['how'] = ['In control']; d['sessions'][-1]['howNote'] = 'Top felt easier'
    pg = t.page(b, data=d)
    ok(pg.evaluate("D.sessions[2].how") == ['In control'], 'an old session keeps its answers')
    pg.evaluate("U.sheet='session';U.sd={k:'s2'};rerender()"); pg.wait_for_timeout(200)
    ok('In control' in pg.inner_text('.sheet') and 'Top felt easier' in pg.inner_text('.sheet'), 'and still shows them')
    # over 90 minutes still asks how long, then saves
    pg.evaluate("U.sheet=null;rerender()")
    to_app(pg)
    pg.evaluate("X.start=Date.now()-125*60000;saveDraft()")
    pg.click('#dock [data-a=cta]')
    ok(until(pg, "U.sheet==='long'"), 'over 90 minutes still asks how long you practised')
    pg.fill('#longMins', '40'); pg.click('[data-a=longOk]')
    ok(until(pg, "X===null&&U.view==='saved'&&!U.sheet") and pg.evaluate("D.sessions[D.sessions.length-1].mins") == 40, 'then saves, with no How did it go?')
    pg.context.close()


def old_ratings(b, t):
    """Q29: ratings are no longer asked for or shown; an old session's ratings stay in its data, through editing, a reload and a restore."""
    from test_backup import pick, write
    ok = t.ok
    d = with_song_practice()
    s2 = d['sessions'][-1]; s2['songName'] = 'Harbour Lights'; s2['rate'] = {'Pitch': 2, 'Tone': 3}
    s1 = d['sessions'][-2]; s1['rate'] = {'Ease': 1}  # a rating with no song: once an Application section of its own
    pg = t.page(b, data=d)
    pg.evaluate("U.sheet='session';U.sd={k:'s2'};rerender()"); until(pg, "!!document.querySelector('.sheet')")
    sh = pg.inner_text('.sheet')
    ok('Harbour Lights' in sh and 'of 3' not in sh and 'Pitch' not in sh and 'Tone' not in sh, 'an old rated session opens with its song and no scores')
    pg.click('[data-a=editSess]'); until(pg, "U.sheet==='edit'")
    ok(pg.locator('.sheet [data-a=erate]').count() == 0 and 'Pitch' not in pg.inner_text('.sheet'), 'its edit sheet has no Pitch · Tone · Ease')
    pg.fill('#edMins', '33'); pg.click('[data-a=saveEdit]'); until(pg, "U.sheet==='session'")
    ok(pg.evaluate("D.sessions.find(s=>s.id==='s2').rate") == {'Pitch': 2, 'Tone': 3} and pg.evaluate("D.sessions.find(s=>s.id==='s2').mins") == 33,
       'editing it keeps its old rating in the data')
    pg.evaluate("U.sheet='session';U.sd={k:'s1'};rerender()"); until(pg, "!!document.querySelector('.sheet')")
    ok(pg.evaluate("[...document.querySelectorAll('.sheet .hdr')].filter(h=>h.textContent.trim()==='Application').length") == 0,
       'a rating with no song leaves no empty Application section')
    pg.evaluate("U.sheet=null;rerender()"); pg.reload(); until(pg, "!!window.D&&!document.querySelector('#launch')")
    ok(pg.evaluate("D.sessions.find(s=>s.id==='s2').rate") == {'Pitch': 2, 'Tone': 3} and pg.evaluate("D.sessions.find(s=>s.id==='s1').rate") == {'Ease': 1},
       'and after a reload')
    # a backup holding ratings restores them exactly
    src = json.load(open(fix('backup-3.6.json'), encoding='utf-8'))
    src['data']['sessions'][2]['rate'] = {'Pitch': 3, 'Ease': 2}; src['data']['sessions'][2]['songName'] = 'Versace on the Floor · bridge'
    path = write('rated-q29.json', src)
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';U.sheet=null;render()")
    pick(pg, 'importPick', path)
    pg.click('[data-a=importYes]'); until(pg, "U.sheet===null")
    ok(pg.evaluate("D.sessions.find(s=>s.id==='s2').rate") == {'Pitch': 3, 'Ease': 2}, 'a backup with old ratings restores them')
    pg.evaluate("U.tab='today';U.view=null;U.sheet='session';U.sd={k:'s2'};render()"); until(pg, "!!document.querySelector('.sheet')")
    ok('of 3' not in pg.inner_text('.sheet') and 'Versace on the Floor · bridge' in pg.inner_text('.sheet'), 'and its sheet still shows no scores')
    pg.context.close()


def song_practice(b, t):
    """Song practice gets the same take rows: waveforms, Star, Compare and Again; and still asks how it went."""
    ok = t.ok
    pg = t.page(b, touch=True)
    pg.evaluate("(()=>{if(!X)newSong();go(()=>{U.tab='today';U.view='song'})})()"); pg.wait_for_timeout(150)
    pg.click('[data-a=song][data-k=g_1]'); pg.wait_for_timeout(100)
    for i in range(2):
        pg.click('[data-a=rec]'); until(pg, "!!rec", 6000); pg.wait_for_timeout(1100)
        pg.click('[data-a=rec]'); until(pg, f"!rec&&TAKES.length==={i + 1}", 8000); pg.wait_for_timeout(250)
    ok(pg.locator('#app .tkrow').count() == 2 and pg.locator('#app .apcmp').count() == 1 and pg.locator('#app .tkwv').count() == 2,
       'Song practice: take rows with waveforms, and Compare')
    ok(pg.inner_text('#recLbl').strip() == '↻ Again', 'its record button is ↻ Again once it has a take')
    pg.click('#app .tkrow >> nth=0 >> [data-a=takeNote]'); until(pg, "U.sheet==='takeNote'")
    ok(pg.locator('.sheet [data-a=shareTake]').count() == 1 and pg.locator('.sheet [data-v=delTake]').count() == 1, 'the take’s notes sheet has Save or share and Delete take')
    pg.evaluate("closeSheet()")
    t.shot(pg, 'song-practice')
    pg.click('#dock [data-a=cta]')
    ok(until(pg, "U.sheet==='how'"), 'Song practice still asks How did it go?')
    pg.context.close()


def motion(b, t):
    ok = t.ok
    # motion on: Done sweeps and flashes, then folds
    pg = t.page(b, touch=True, init=MOTION_ON)
    lyric_song(pg)
    to_app(pg)
    pg.click('#app [data-a=apSong][data-k=g_1]'); pg.wait_for_timeout(300)
    sing(pg)
    pg.click(f'{CARD} [data-a=apDone]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("APPL.state().st") == 'open' and pg.evaluate("document.querySelector('#apcard .apsweep').getAnimations().length") > 0,
       'motion on: Done sweeps the card first')
    ok(until(pg, "APPL.state().st==='done'", 5000), 'then the song folds')
    pg.context.close()
    # Reduce Motion: a green fade, no sweep
    pg = t.page(b, touch=True, init=MOTION_ON + ";try{localStorage.setItem('vocalReduce','on')}catch(e){}")
    to_app(pg)
    pg.click('#app [data-a=apSong][data-k=g_1]'); pg.wait_for_timeout(300)
    sing(pg)
    pg.click(f'{CARD} [data-a=apDone]'); pg.wait_for_timeout(60)
    an = pg.evaluate("document.querySelector('#apcard .apsweep')?document.querySelector('#apcard .apsweep').getAnimations().map(a=>a.effect.getKeyframes().some(k=>k.transform&&k.transform!=='none')):[]")
    ok(an == [False] or an == [], 'Reduce Motion: no sweep: ' + json.dumps(an))
    ok(until(pg, "APPL.state().st==='done'", 4000), 'and it still folds')
    pg.context.close()


def sizes(b, t):
    ok = t.ok
    for w in (390, 375):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, sc=sc, touch=True)
            sid = lyric_song(pg)
            add_track(pg, sid, track())
            pg.evaluate(wav_take(3), ['old2', sid, occ(pg, sid, 1), 60 * 24 * 2])
            to_app(pg)
            ok(pg.evaluate(WIDE), f'{w} {sc}: Carry on fits, no sideways scroll')
            t.shot(pg, f'{w}-{sc}-carry')
            pg.evaluate("sgp().singOver=false;saveSGP();rerender()")
            sing(pg)
            sing(pg)
            ok(pg.evaluate(WIDE), f'{w} {sc}: takes and Compare fit')
            r = pg.evaluate("(()=>{const a=document.querySelector('#apcard .apcmp').getBoundingClientRect(),c=document.getElementById('apcard').getBoundingClientRect();return [a.left>=c.left-0.5,a.right<=c.right+0.5]})()")
            ok(r == [True, True], f'{w} {sc}: Compare sits inside the card')
            t.shot(pg, f'{w}-{sc}-takes')
            pg.close()


def run(b, t):
    for part in (carry_on, singing, done_and_norec, old_answers, old_ratings, song_practice, motion, sizes):
        part(b, t)
