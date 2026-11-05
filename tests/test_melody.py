"""Q42 · Songs: Sheet Music Reader and Score. Ivan's own Ultimate Guitar print (a Safari PDF, notation plus tab, Vocals
part) read on the device, in a Worker, into a score kept on the song.

The prints are made-up tunes drawn UG-style by tools/make_melody_fixtures.py (tests/fixtures/melody/): no real prints,
music or words. Parts (VS_MELODY=read,catcher,clean,backup,guards,screens,offline):
- read: every fixture reads as intended through the real Worker (bars, notes, lengths, ties, triplets, dots, rests,
  multi-bar rests, the pickup, a 2/4 bar, bar numbers, two-digit frets, bend labels, grace notes, slides, a harmony
  stack, flat and sharp keys, repeats); the blip test; progress by line; Cancel; the app usable while it reads; the
  fallback when pdf.js won't load in the Worker; nothing fetched from anywhere else
- catcher: fret, range, jump and unsure checks, and the "to check" list
- clean: cleanMelody() record by record, a damaged score to Rescued data, the note and score put back together, the
  score-shape upgrade with its safety copy, two windows, deleting a song, Reset all, Sheets with no song, Remove
  prints, a print that won't save
- backup: the melodies field and its own check code (checkCode unchanged), a round trip, 3.5 and 3.6 backups, a
  backup made now opening in 3.6 as good, damaged sheet music, restore's Undo, prints never in backups
- guards: every input guard in MAINTAINING › Sheet music
- screens: the Song page row (VS-009), VS-099, VS-100, the New song door (VS-051), Settings › Storage (VS-020), the key
  offered through VS-098, at 375 px and on iPad, light and dark, with Reduce Motion
- offline: an import works offline after the first (pdf.js cached by the service worker)"""
import os, json
from harness import fix, ready, until, OUT, url, APP_PATH, SEED, UA_IPHONE, offline, online

MEL = fix('melody')
PARTS = set((os.environ.get('VS_MELODY') or 'read,catcher,clean,backup,guards,screens,offline').split(','))
SONG = "go(()=>{U.tab='songs';U.view='lyr';U.songId='g_1'})"
NAME = "n=>{songById('g_1').name=n;save();rerender()}"
# hand a fixture to the reader as the file picker would (opt: test-only options for the Worker)
START = """async([name,target,opt,ok])=>{const r=await fetch('tests/fixtures/melody/'+name);const b=await r.blob();
  const f=new File([b],name,{type:'application/pdf'});window.__toasts=window.__toasts||[];await MELODY.start(f,target,ok,opt)}"""
TOASTS = "(()=>{window.__toasts=[];const o=window.toast;window.toast=function(t){window.__toasts.push(t);return o.apply(this,arguments)};const ob=window.toastBtn;window.toastBtn=function(t){window.__toasts.push(t);return ob.apply(this,arguments)}})()"
NM = "m=>'C C#D D#E F F#G G#A A#B '.substr((m%12)*2,2).trim()+(Math.floor(m/12)-1)"
# the bars of a score as text, for comparing: "n:len|notes (name/eighths)|rests"
BARS = ("id=>{const s=MELODY.get(id);const nm=" + NM + ";return s.bars.map(b=>b.n+':'+b.len/240+'|'+s.notes.filter(n=>n.tick>=b.tick&&n.tick<b.tick+b.len)"
        ".map(n=>nm(n.midi)+'/'+(+(n.len/240).toFixed(3))+(n.flag?'!'+n.flag:'')).join(' ')+'|'+s.rests.filter(n=>n.tick>=b.tick&&n.tick<b.tick+b.len).map(n=>'r'+n.len/240).join(' ')+(b.f?'|'+b.f.join(','):''))}")
COUNT = ("async(st)=>{const d=await new Promise(r=>{const q=indexedDB.open('vocalMelodies',1);q.onsuccess=()=>r(q.result)});"
         "const n=await new Promise(r=>{const q=d.transaction(st).objectStore(st).count();q.onsuccess=()=>r(q.result)});d.close();return n}")

# what each print should read as (checked by eye against the tune in the generator, then kept)
PAPER = ['0:2|A3/2|', '1:32||r32', '5:8|D4/2 E4/2 F#4/3 E4/1|', '6:8|D4/8|', '7:8|F#4/2 E4/0.667 D4/0.667 E4/0.667 F#4/2|r2',
         '8:8|A4/3.5 G4/0.5 F#4/2 E4/2|', '9:8|G4/2 A4/2 B4/2 A4/2|', '10:8|F#4/1.5 E4/0.5 D4/2 E4/2 F#4/2|', '11:8|E4/12|',
         '12:8|D4/1 C#4/1 B3/2|', '13:8|D4/2 E4/2 F#4/2 G4/2|', '14:8|A4/2 G4/2 F#4/4|', '15:4|E4/2 D4/2|',
         '16:8|D4/2 E4/1 F#4/1 E4/0.5 D4/1 C#4/2|r0.5', '17:8|D4/6|r2', '18:8||r8']
RAIN = ['1:8|D#4/2 F4/2 G4/2 G#4/2|', '2:8|A#4/4 G4/4|', '3:8|G#4/2 G4/2 F4/2 D#4/2|', '4:8|F4/6|r2', '5:8|G4/2 G#4/1 A#4/1 C5/2 A#4/2|',
        '6:8|G#4/4 F4/4|', '7:8|D#4/2 F4/2 G4/2 F4/2|', '8:8|D#4/8|']
NIGHT = ['1:8|C4/2 D4/2 E4/2 D4/2|', '2:24||r24', '5:8|E4/4 D4/4|', '6:8|C4/2 D4/2 E4/4||numbers', '7:8|D4/8|',
         '8:8|C4/2 D4/2!fret E4/2 D4/2||numbers', '9:8|C4/2 D5/2!jump E4/2 G4/2!unsure|', '10:8|E4/2 A2/2!range C4/4|']


def fresh(t, b, **kw):
    pg = t.page(b, **kw)
    pg.evaluate(TOASTS)
    return pg


def read(pg, name, target=None, opt=None, ok=False, wait="U.sheet==='melRead'"):
    pg.evaluate(START, [name, target or {'id': 'g_1'}, opt, ok])
    return until(pg, wait, 20000)


def read_save(pg, name, sid='g_1'):
    """Read a print onto a song, from its page, through every question it asks, then save it."""
    pg.evaluate("id=>go(()=>{U.tab='songs';U.view='lyr';U.songId=id;U.sheet=null})", sid)
    pg.evaluate(START, [name, {'id': sid}, None, False])
    for _ in range(4):
        if not until(pg, "['melRead','melTitle','melSame','melReplace'].includes(U.sheet)", 20000): return False
        s = pg.evaluate("U.sheet")
        if s == 'melRead': break
        pg.evaluate({'melTitle': "SG_ACT.melTitleHere()", 'melSame': "SG_ACT.melSameGo()", 'melReplace': "SG_ACT.melReplaceYes()"}[s])
    pg.evaluate("SG_ACT.melSave()")
    ok = until(pg, "id=>MELODY.has(id)&&U.sheet!=='melRead'", 8000, sid)
    pg.evaluate("U.sheet=null;U.sd={};rerender()")
    return ok


def blips(pg, sid):
    """One-note spikes of 10 or more semitones among the notes that play (the blip test)."""
    return pg.evaluate("""id=>{const l=MELODY.line(MELODY.get(id));let n=0;for(let i=1;i+1<l.length;i++){const a=l[i].midi-l[i-1].midi,b=l[i].midi-l[i+1].midi;
      if(Math.abs(a)>=10&&Math.abs(b)>=10&&Math.sign(a)===Math.sign(b))n++}return n}""", sid)


def run(b, t):
    ok = t.ok
    if 'read' in PARTS: part_read(b, t, ok)
    if 'catcher' in PARTS: part_catcher(b, t, ok)
    if 'clean' in PARTS: part_clean(b, t, ok)
    if 'backup' in PARTS: part_backup(b, t, ok)
    if 'guards' in PARTS: part_guards(b, t, ok)
    if 'screens' in PARTS: part_screens(b, t, ok)
    if 'offline' in PARTS: part_offline(b, t, ok)


def part_read(b, t, ok):
    pg = fresh(t, b)
    reqs = []
    pg.on('request', lambda r: reqs.append(r.url))
    pg.evaluate(NAME, 'Paper Lanterns'); pg.evaluate(SONG); pg.wait_for_timeout(200)
    # progress by line, and the app carrying on while it reads (a timer keeps ticking; a redraw works)
    pg.evaluate("window.__prog=[];window.__tick=0;window.__iv=setInterval(()=>window.__tick++,20);"
                "const o=MELODY.busyText;setInterval(()=>{const r=MELODY.reading();if(r&&r.lines)window.__prog.push(r.line+'/'+r.lines)},5)")
    pg.evaluate(START, ['paper-lanterns.pdf', {'id': 'g_1'}, None, False])
    ok(until(pg, "MELODY.reading()!==null"), 'reading starts in the background')
    ok(pg.locator('.melbusy[data-screen="VS-106"]').count() == 1 and 'Cancel' in pg.inner_text('.melbusy'), 'the reading pill (VS-106) shows, with Cancel')
    pg.evaluate("go(()=>{U.tab='today';U.view=null})"); pg.evaluate(SONG)
    ok(until(pg, "U.sheet==='melRead'", 20000), 'the print reads and Sheet music read (VS-100) opens')
    prog = pg.evaluate("window.__prog")
    ok(len(prog) >= 1 and all(p.endswith('/4') for p in prog), 'progress is by line (line n of 4): %s' % sorted(set(prog))[:4])
    ok(pg.evaluate("window.__tick") >= 3, 'the page stayed usable while it read (its timers kept running)')
    ok(pg.evaluate(COUNT, 'melodies') == 0, 'nothing is saved before Save')
    pg.evaluate("SG_ACT.melSave()"); until(pg, "MELODY.has('g_1')")
    got = pg.evaluate(BARS, 'g_1')
    ok(got == PAPER, 'Paper Lanterns reads as written: the pickup, the 4-bar rest, a tie across a bar line, the triplet, dots and double dots, a sixteenth rest, two-digit frets past a bend label, the grace note left out, the slide, the harmony stack’s top note, the 2/4 bar (%s)' % [g for g, w in zip(got, PAPER) if g != w])
    s = pg.evaluate("MELODY.get('g_1')")
    ok(s['key'] == 2 and s['time'] == [4, 4] and s['shift'] == 0 and s['reader'] == 1 and s['v'] == 1 and s['src'] == 'sheet', 'its key (2 sharps), time (4/4), shift, reader and shape versions')
    ok(all(isinstance(n['tick'], int) and isinstance(n['len'], int) for n in s['notes']) and s['bars'][1]['tick'] == 480, 'everything is in whole ticks, 480 a beat (the one-beat pickup is 480)')
    ok(s['ug'] == {'id': '9000001', 'title': 'Paper Lanterns', 'artist': 'The Made Up Band'}, 'the title, artist and tab id come from the UG footer')
    ok(pg.evaluate("JSON.stringify(songById('g_1').ext.melody)").startswith('{"ug":"9000001","at":'), 'the song carries only the note {ug, at}')
    ok(not any(n.get('syl') for n in s['notes']), 'no words are read in this milestone (M2)')
    ok(blips(pg, 'g_1') == 0, 'blip test: no one-note spike of 10+ semitones in Paper Lanterns')
    pg.evaluate("U.sheet=null;rerender()")
    # the other prints
    for name, want, sid in [('rain-on-the-ferry.pdf', RAIN, 'g_r'), ('night-bus-home.pdf', NIGHT, 'g_n'), ('lighthouse-steps.pdf', None, 'g_l')]:
        pg.evaluate("id=>{D.songs.push({id,name:id,added:Date.now()});save()}", sid)
        ok(read_save(pg, name, sid), f'{name} reads and saves')
        if want:
            got = pg.evaluate(BARS, sid)
            ok(got == want, f'{name} reads as written ({[g for g, w in zip(got, want) if g != w]})')
        ok(blips(pg, sid) == 0, f'blip test: no one-note spike in what plays of {name}')
    ok(pg.evaluate("MELODY.get('g_r').key") == -3, 'a flat key: 3 flats')
    ok(pg.evaluate("MELODY.get('g_l').repeats") and pg.evaluate("MELODY.checks(MELODY.get('g_l'))[0].why") == 'This print uses repeats; the order may be wrong.',
       'repeats, a first ending and a coda are flagged: "This print uses repeats; the order may be wrong"')
    ok(pg.evaluate("MELODY.get('g_l').bars.filter(b=>(b.f||[]).includes('repeat')).length") == 1, 'the bar with the repeat sign is flagged once')
    ok(not [u for u in reqs if not u.startswith('http://localhost')], 'no request leaves the app’s own address')
    ok(any('/js/vendor/pdfjs-4.10.38/pdf.min.js' in u for u in reqs) and any('/js/melodyread.js?v=' in u for u in reqs), 'the Worker and pdf.js load from the app’s own folders')
    # Cancel mid-read: nothing kept, nothing left reading
    pg.evaluate(START, ['paper-lanterns.pdf', {'id': 'g_r'}, None, False])
    until(pg, "MELODY.reading()!==null")
    pg.click('.melbusy [data-a="melCancel"]')
    ok(until(pg, "MELODY.reading()===null&&!document.querySelector('.melbusy')") and pg.evaluate("MELODY.get('g_r').ug.id") == '9000002', 'Cancel stops the read and keeps what was there')
    # the fallback: pdf.js won't load inside the Worker, so the page reads the pictures and hands them over
    pg.evaluate("U.sheet=null;rerender()")
    pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId='g_r'})")
    ok(read(pg, 'rain-on-the-ferry.pdf', {'id': 'g_r'}, {'nopdf': True}, wait="['melRead','melReplace','melTitle'].includes(U.sheet)"), 'the fallback (pictures read on the page) reads too')
    ok(pg.evaluate("typeof MELREAD==='object'"), 'and it loaded the reader on the page only then')
    pg.context.close()


def part_catcher(b, t, ok):
    pg = fresh(t, b)
    pg.evaluate("id=>{D.songs.push({id,name:'Night Bus Home',added:Date.now()});save()}", 'g_n')
    read_save(pg, 'night-bus-home.pdf', 'g_n')
    s = pg.evaluate("MELODY.get('g_n')")
    fl = [n.get('flag') for n in s['notes'] if n.get('flag')]
    ok(sorted(fl) == ['fret', 'jump', 'range', 'unsure'], 'the catcher: an unreadable fret, a spike, a note far out of range and a tab that disagrees (%s)' % fl)
    ok(pg.evaluate("MELODY.line(MELODY.get('g_n')).length") == len(s['notes']) - 3, 'caught notes are muted; the unsure one plays')
    ck = pg.evaluate("MELODY.checks(MELODY.get('g_n'))")
    whys = ' / '.join(c['why'] for c in ck)
    ok(any('The print says bar 7 here; the reader counted 6.' == c['why'] and c['n'] == 6 for c in ck), 'a printed bar number that disagrees flags its line (H1)')
    ok('tab number couldn’t be read' in whys and 'far outside the song’s range' in whys and 'jump of 10 semitones' in whys and 'disagree' in whys, 'the "to check" list says why for each')
    # the catcher itself, on made-up notes
    pg.evaluate("()=>new Promise(r=>{const s=document.createElement('script');s.src=document.querySelector('link[href^=\"js/melodyread.js\"]').getAttribute('href');s.onload=r;document.head.appendChild(s)})")
    res = pg.evaluate("""MELREAD.catchNotes([60,62,64,65,67,65,64,62,60,62,64,62,60].map(m=>({midi:m,sure:true})).concat([{midi:84,sure:true},{midi:62,sure:true},{midi:62,bad:true},{midi:64,sure:false},{midi:62,sure:true}])).map(n=>n.flag||'')""")
    ok(res[13] == 'range' and res[15] == 'fret' and res[16] == 'unsure' and res.count('') == 15, 'catchNotes: range, fret and unsure on made-up notes')
    res = pg.evaluate("""MELREAD.catchNotes([60,62,64,66,67,65,64,62,60,74,60,62,64].map(m=>({midi:m,sure:true}))).map(n=>n.flag||'')""")
    ok(res[9] == 'jump' and res.count('') == 12, 'catchNotes: a one-note spike of 14 semitones, inside the range, is muted as a jump')
    pg.context.close()


def part_clean(b, t, ok):
    pg = fresh(t, b)
    c = pg.evaluate("""JSON.stringify(MELODY.cleanMelody({v:1,rev:2,tempo:500,shift:30,octave:9,key:12,time:[4,3],extra:{a:1},
      bars:[{tick:0,len:1920,n:1},{tick:'x',len:1,n:1}],
      notes:[{tick:480,len:480,midi:62,later:true},{tick:0,len:480,midi:60},{tick:0,len:480,midi:'C4'},{tick:960,len:480,midi:20},{tick:960,len:480,midi:100},
             {tick:-5,len:480,midi:60},{tick:600,len:480,midi:64},{tick:960,len:0,midi:60},{tick:1440,len:240,midi:65,flag:'unsure'}]}))""")
    c = json.loads(c)
    ok([n['midi'] for n in c['notes']] == [60, 62, 65], 'cleanMelody drops bad notes (not numbers, MIDI outside 33–96, negative, overlapping, no length) and sorts')
    ok(c['tempo'] == 300 and c['shift'] == 12 and c['octave'] == 2 and c['key'] == 7 and c['time'] == [4, 4] and len(c['bars']) == 1, 'it clamps the tempo, shift, octave and key, and checks the time and bars')
    ok(c['extra'] == {'a': 1} and c['notes'][1]['later'] is True and c['rests'] == [] and c['anchors'] == [] and c['loop'] is None, 'it keeps unknown fields')
    ok(pg.evaluate("[null,1,'x',[],{notes:1},{notes:[],bars:'x'}].map(x=>MELODY.cleanMelody(x)).every(x=>x===null)"), 'it gives null for junk and never throws')
    # a damaged score in the store goes to Rescued data; the song carries on
    pg.evaluate("""async()=>{const d=await new Promise(r=>{const q=indexedDB.open('vocalMelodies',1);q.onupgradeneeded=()=>{['melodies','prints','undo'].forEach(s=>q.result.createObjectStore(s))};q.onsuccess=()=>r(q.result)});
      await new Promise(r=>{const t=d.transaction('melodies','readwrite');t.objectStore('melodies').put({notes:'broken'},'g_1');t.objectStore('melodies').put({v:1,rev:1,at:1,tempo:90,time:[4,4],key:0,bars:[{tick:0,len:1920,n:1}],notes:[{tick:0,len:480,midi:60}]},'g_x');t.oncomplete=r});d.close()}""")
    pg.evaluate("songById('g_1').ext={melody:{ug:'1',at:1}};save()")
    pg.reload(); ready(pg); pg.evaluate(TOASTS)
    until(pg, "MELODY.loaded()")
    ok(pg.evaluate("SAFE.rescued().some(c=>c.why==='melody')") and not pg.evaluate("MELODY.has('g_1')"), 'an unreadable score goes to Rescued data')
    pg.evaluate(SONG); pg.wait_for_timeout(200)
    ok('Sheet not on this device' in pg.inner_text('[data-a="melAdd"]'), 'a note with no score shows "Sheet not on this device"; the song works')
    ok(pg.evaluate("MELODY.orphans()") == ['g_x'], 'a score with no song is listed, not deleted at launch')
    # a score with no note gets its note back at launch
    pg.evaluate("songById('g_1').ext={};save()")
    pg.evaluate("async()=>{await MELODY._put('g_1',{v:1,rev:1,at:5,tempo:90,time:[4,4],key:0,bars:[{tick:0,len:1920,n:1}],notes:[{tick:0,len:480,midi:60}],ug:{id:'77'}},0)}")
    pg.evaluate("delete songById('g_1').ext;save()")
    pg.reload(); ready(pg); until(pg, "MELODY.loaded()")
    ok(pg.evaluate("JSON.stringify(songById('g_1').ext.melody)") == '{"ug":"77","at":5}', 'a score whose song lost its note gets the note back at launch')
    # the score-shape upgrade keeps the old score in the safety copies for 30 days
    v = pg.evaluate("MELODY._testUpgrade(s=>Object.assign(s,{upgraded:true}))")
    pg.evaluate("MELODY._reloadAll()")
    ok(pg.evaluate("MELODY.get('g_1').upgraded===true&&MELODY.get('g_1').v") == v, 'a score in an older shape is upgraded by its numbered step')
    ok(pg.evaluate("SAFE.list().some(m=>m.key==='melodyBeforeUpgrade:g_1')"), 'and the old one is kept in the safety copies first')
    # two windows: a write from an older rev is refused and the score reloaded
    other = pg.context.new_page(); other.goto(url(APP_PATH)); ready(other); until(other, "MELODY.loaded()")
    pg.evaluate("MELODY.edit('g_1',{tempo:120})"); until(pg, "MELODY.get('g_1').tempo===120")
    other.evaluate(TOASTS)
    other.evaluate("MELODY.edit('g_1',{tempo:80})"); other.wait_for_timeout(400)
    ok(other.evaluate("MELODY.get('g_1').tempo") == 120 and any('another window' in x for x in other.evaluate("window.__toasts")), 'two windows: the older one’s write is refused and it shows the latest')
    other.close()
    # a print that won't save: the score is still usable
    pg.evaluate("""(()=>{const o=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(v,k){if(this.name==='prints'){throw new DOMException('full','QuotaExceededError')}return o.apply(this,arguments)}})()""")
    pg.evaluate(TOASTS)
    pg.evaluate("id=>{D.songs.push({id,name:'Rain On The Ferry',added:Date.now()});save()}", 'g_r')
    read_save(pg, 'rain-on-the-ferry.pdf', 'g_r')
    ok(pg.evaluate("MELODY.has('g_r')&&!MELODY.hasPrint('g_r')") and 'Print not saved; storage is full' in pg.evaluate("window.__toasts"), 'a print that won’t save leaves the score usable, with "Print not saved; storage is full"')
    pg.reload(); ready(pg); until(pg, "MELODY.loaded()")
    # deleting a song deletes its score and print
    pg.evaluate("id=>{D.songs.push({id,name:'Paper Lanterns',added:Date.now()});save()}", 'g_p')
    read_save(pg, 'paper-lanterns.pdf', 'g_p')
    ok(pg.evaluate("MELODY.hasPrint('g_p')") and pg.evaluate(COUNT, 'prints') == 1, 'the print is kept on the device')
    pg.evaluate("deleteSongs(['g_p'])"); pg.wait_for_timeout(300)
    ok(not pg.evaluate("MELODY.has('g_p')") and pg.evaluate(COUNT, 'prints') == 0, 'deleting a song deletes its score and print')
    # Reset all leaves scores and prints; Storage lists sheets with no song, with Delete
    read_save(pg, 'paper-lanterns.pdf', 'g_r')
    n0 = pg.evaluate(COUNT, 'melodies')
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';render()")
    pg.evaluate("document.querySelector('[data-a=resetAll]')?null:0"); pg.evaluate("(()=>{const e=document.createElement('button');e.dataset.a='resetAll';document.body.appendChild(e);e.click();e.remove()})()")
    until(pg, "D.songs.length===0", 5000)
    ok(pg.evaluate(COUNT, 'melodies') == n0 and pg.evaluate(COUNT, 'prints') == 1, 'Reset all data leaves scores and prints, as it leaves tracks')
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='storage';render()"); pg.wait_for_timeout(200)
    ok(pg.locator('text=Sheets with no song').count() == 1 and pg.locator('[data-v="melOrphanDel"]').count() == n0, 'Storage lists "Sheets with no song", each with Delete')
    t.shot(pg, 'storage-orphans')
    pg.locator('[data-v="melOrphanDel"]').first.click(); pg.wait_for_timeout(300)
    ok(pg.locator('[data-screen="VS-107"]').count() == 1, 'Delete asks first (VS-107)')
    pg.locator('.pk-alert-btn.pk-red').click(); pg.wait_for_timeout(400)
    ok(pg.evaluate(COUNT, 'melodies') == n0 - 1, 'and deletes that score')
    # Remove prints, keep scores
    pg.evaluate("U.sheet=null;render()")
    ok(pg.locator('[data-v="melPrintsDel"]').count() == 1, 'Storage has Remove prints, keep scores')
    pg.click('[data-v="melPrintsDel"]'); pg.wait_for_timeout(300); pg.locator('.pk-alert-btn.pk-red').click(); pg.wait_for_timeout(400)
    ok(pg.evaluate(COUNT, 'prints') == 0 and pg.evaluate(COUNT, 'melodies') == n0 - 1, 'it removes the prints and keeps the scores')
    ok(pg.evaluate("SET.sizes().map(x=>x.k).join()") == 'rec,trk,cv,app,mel', 'Storage counts sheet music last, read by key (H45)')
    pg.context.close()


def export(pg):
    pg.evaluate("prepareExport(false,false)")
    until(pg, "U.sheet==='exportReady'", 15000)
    txt = pg.evaluate("pendingExport.file.text()")
    pg.evaluate("U.sheet=null;rerender()")
    return txt


def importing(pg, path):
    pg.evaluate("U.tab='settings';U.view='set';U.setPg='backup';U.sheet=null;render()")
    with pg.expect_file_chooser() as fc: pg.click('[data-a=importPick]')
    fc.value.set_files(path)
    return until(pg, "U.sheet==='bkReport'")


def part_backup(b, t, ok):
    F = os.path.join(OUT, 'melody-files'); os.makedirs(F, exist_ok=True)
    pg = fresh(t, b)
    pg.evaluate(NAME, 'Paper Lanterns')
    read_save(pg, 'paper-lanterns.pdf')
    pg.evaluate("MELODY.edit('g_1',{tempo:112})"); until(pg, "MELODY.get('g_1').tempo===112")
    txt = export(pg)
    p = json.loads(txt)
    ok(isinstance(p.get('melodies'), list) and len(p['melodies']) == 1 and p['melodies'][0]['id'] == 'g_1' and len(p.get('melodiesCode', '')) == 64, 'a backup carries the scores as `melodies` with their own check code')
    ok('blob' not in json.dumps(p['melodies']) and len(txt) < 200000, 'prints are never in backups')
    code = pg.evaluate("p=>checkCode(p)", {'data': p['data'], 'draft': p['draft'], 'takes': p['takes']})
    ok(code == p['checkCode'], 'checkCode is still over data, draft and takes only')
    good = os.path.join(F, 'with-sheet.json'); open(good, 'w').write(txt)
    # an older app calls it good
    old = b.new_context(user_agent=UA_IPHONE, accept_downloads=True).new_page()
    old.goto(url(fix('app-3.6.html'))); old.evaluate(SEED, None); old.reload(); ready(old)
    old.evaluate("U.tab='settings';render()")
    with old.expect_file_chooser() as fc: old.click('[data-a=importPick]')
    fc.value.set_files(good); until(old, "U.sheet==='bkReport'")
    ok(old.evaluate("pendingImport.status") == 'good', 'version 3.6 calls a backup with sheet music good')
    old.context.close()
    # round trip: export, reset, import
    pg.evaluate("(()=>{const e=document.createElement('button');e.dataset.a='resetAll';document.body.appendChild(e);e.click();e.remove()})()")
    until(pg, "D.songs.length===0", 5000)
    pg.evaluate("async()=>{await MELODY.forget(['g_1'])}")
    ok(not pg.evaluate("MELODY.has('g_1')"), '(the score is gone from this device)')
    importing(pg, good)
    ok(pg.evaluate("pendingImport.status") == 'good' and pg.evaluate("pendingImport.mel.state") == 'good', 'the backup checks as good, sheet music included')
    pg.click('[data-a=importYes]'); until(pg, "U.sheet===null", 10000)
    ok(pg.evaluate("MELODY.has('g_1')&&MELODY.get('g_1').tempo") == 112 and pg.evaluate("!!songById('g_1').ext.melody"), 'restoring brings the score back with the song’s note')
    pg.reload(); ready(pg); until(pg, "MELODY.loaded()")
    ok(pg.evaluate("MELODY.get('g_1').tempo") == 112 and pg.evaluate("MELODY.checks(MELODY.get('g_1')).length") == 0, 'and it’s kept after a relaunch')
    pg.evaluate(SONG); pg.wait_for_timeout(200)
    ok('Sheet music' in pg.inner_text('[data-a="melOpen"]'), 'the Song page shows it')
    # restore's undo: the device's scores come back
    pg.evaluate("MELODY.edit('g_1',{tempo:77})"); until(pg, "MELODY.get('g_1').tempo===77")
    importing(pg, good); pg.click('[data-a=importYes]'); until(pg, "U.sheet===null", 10000)
    ok(pg.evaluate("MELODY.get('g_1').tempo") == 112, 'a restore writes the backup’s score')
    pg.evaluate("undoRestore()"); until(pg, "U.sheet===null&&UNDO===null", 10000); pg.wait_for_timeout(300)
    ok(pg.evaluate("MELODY.get('g_1').tempo") == 77, 'Undo puts the device’s score back')
    # damaged sheet music: the rest restores, the text goes to Rescued data
    bad = json.loads(txt); bad['melodies'][0]['notes'] = 'cut short'
    badp = os.path.join(F, 'damaged-sheet.json'); open(badp, 'w').write(json.dumps(bad))
    importing(pg, badp)
    ok(pg.evaluate("pendingImport.mel.state") == 'damaged' and pg.locator('text=Sheet music is damaged').count() == 1, 'damaged sheet music is its own state, shown before restoring')
    ok(pg.evaluate("pendingImport.status") == 'good', 'the rest of the backup still checks as good')
    t.shot(pg, 'damaged-report')
    pg.click('[data-a=importYes]'); until(pg, "U.sheet===null", 10000)
    ok(pg.evaluate("D.songs.length") == 1 and pg.evaluate("SAFE.rescued().some(c=>c.why==='melody')"), 'the rest restores and the sheet music’s text goes to Rescued data')
    # 3.5 and 3.6 backups still open
    for v, status in [('3.5', 'old'), ('3.6', 'good')]:
        importing(pg, fix(f'backup-{v}.json'))
        ok(pg.evaluate("pendingImport.status") == status and pg.evaluate("pendingImport.mel.state") == 'none', f'a {v} backup checks as "{status}", with no sheet music')
        pg.click('[data-a=importYes]'); until(pg, "U.sheet===null", 10000)
        ok(pg.evaluate("D.songs.length") >= 1, f'and restores')
    importing(pg, fix('backup-next.json'))
    ok(pg.evaluate("pendingImport.status") in ('good', 'old', 'unchecked'), 'backup-next.json still opens')
    pg.context.close()


def part_guards(b, t, ok):
    pg = fresh(t, b)
    pg.evaluate(NAME, 'Paper Lanterns'); pg.evaluate(SONG); pg.wait_for_timeout(200)
    def last(): return (pg.evaluate("window.__toasts") or [''])[-1]
    def go(name, opt=None, wait="MELODY.reading()===null&&!document.querySelector('.melbusy')"):
        pg.evaluate("window.__toasts=[]")
        pg.evaluate(START, [name, {'id': 'g_1'}, opt, False]); pg.wait_for_timeout(100)
        return until(pg, wait, 20000)
    # not a PDF (by its first bytes, not its name)
    pg.evaluate("""async()=>{window.__toasts=[];const f=new File(['hello, not a pdf'],'song.pdf',{type:'application/pdf'});await MELODY.start(f,{id:'g_1'})}""")
    ok(last() == 'This isn’t a PDF.', 'not a PDF: "This isn’t a PDF."')
    pg.evaluate("""async()=>{window.__toasts=[];const f=new File(['%PDF-1.7\\n garbage that is no pdf at all'],'x.pdf');await MELODY.start(f,{id:'g_1'})}""")
    until(pg, "MELODY.reading()===null", 15000); pg.wait_for_timeout(100)
    ok(last() == 'This PDF can’t be opened.', 'a damaged PDF: "This PDF can’t be opened."')
    go('locked.pdf'); ok(last() == 'This PDF can’t be opened.', 'a locked PDF: "This PDF can’t be opened."')
    go('no-footer.pdf'); ok(last() == 'This doesn’t look like an Ultimate Guitar print. Print it from UG as notation plus tab.', 'no UG footer: not an Ultimate Guitar print')
    go('no-music.pdf'); ok(last().startswith('This doesn’t look like an Ultimate Guitar print'), 'no music pictures: not an Ultimate Guitar print')
    go('notation-only.pdf'); ok(last() == 'This print has the notation but no tab. In UG choose notation plus tab, then print again.', 'notation only: says which view to print')
    go('tab-only.pdf'); ok(last() == 'This print has the tab but no notation. In UG choose notation plus tab, then print again.', 'tab only: says which view to print')
    go('guitar-part.pdf'); ok(last() == 'This looks like a guitar part. Print the Vocals part.', 'a guitar part: "Print the Vocals part"')
    go('few-bars.pdf'); ok(last() == 'Only 2 of 8 bars could be read, too few to keep. Check it’s the notation plus tab view.', 'under a third of bars adding up: not saved, says what it found')
    go('paper-lanterns.pdf', {'limits': {'notes': 20}}); ok(last().startswith('This print has more than a song’s worth'), 'over the limit of notes or bars: the read stops')
    ok(pg.evaluate(COUNT, 'melodies') == 0 and not pg.evaluate("songById('g_1').ext"), 'none of these saved anything')
    # over 40 pages: asks first
    pg.evaluate(START, ['long.pdf', {'id': 'g_1'}, None, False])
    ok(until(pg, "U.sheet==='melBig'", 15000) and 'It has 41 pages' in pg.inner_text('#layer'), 'over 40 pages: asks first (VS-104)')
    pg.evaluate("SG_ACT.close?SG_ACT.close():0"); pg.locator('.pk-alert-btn[data-a="no"]').click()
    ok(until(pg, "MELODY.reading()===null"), 'Cancel stops it')
    pg.evaluate(START, ['long.pdf', {'id': 'g_1'}, None, False]); until(pg, "U.sheet==='melBig'", 15000)
    pg.evaluate("window.__toasts=[]"); pg.locator('.pk-alert-btn.pk-red').click()
    ok(until(pg, "MELODY.reading()===null", 15000) and last().startswith('This doesn’t look like'), 'Read it anyway carries on (this one has no music)')
    # over 30 MB: asks first, before reading anything
    pg.evaluate("""async()=>{const f=new File([new Uint8Array(31*1048576)],'big.pdf');await MELODY.start(f,{id:'g_1'})}""")
    ok(until(pg, "U.sheet==='melBig'") and 'It is 31 MB' in pg.inner_text('#layer') and pg.evaluate("MELODY.reading()") is None, 'over 30 MB: asks first, before reading')
    pg.locator('.pk-alert-btn[data-a="no"]').click(); pg.wait_for_timeout(200)
    # importing while recording: disabled
    pg.evaluate("rec={fake:true};rerender()")
    ok(pg.locator('[data-a="melAdd"][aria-disabled="true"]').count() == 1 and 'Finish the take first' in pg.inner_text('[data-a="melAdd"]'), 'while recording, Add sheet music says "Finish the take first"')
    pg.evaluate("window.__toasts=[]"); pg.evaluate("MELODY.pick({id:'g_1'})")
    ok(last() == 'Finish the take first', 'and won’t open the picker')
    pg.evaluate("rec=null;rerender()")
    # the title differs from the song: this song, a new song, or cancel
    pg.evaluate(NAME, 'Something Else Entirely')
    ok(read(pg, 'paper-lanterns.pdf', wait="U.sheet==='melTitle'"), 'a print with another title asks (VS-102)')
    ok('This print is Paper Lanterns by The Made Up Band.' in pg.inner_text('#layer'), 'saying what the print is')
    # Q49 one Cancel: the kit's own, which does the sheet's Cancel
    pg.wait_for_timeout(400)
    c = pg.evaluate("[...document.querySelectorAll('#layer .pk-actions:not(.pk-leaving) .pk-action')].filter(b=>b.textContent.trim()==='Cancel').map(b=>b.className)")
    ok(len(c) == 1 and 'pk-cancel' in c[0], f'one Cancel, the kit’s own ({c})')
    pg.click('#layer .pk-actions:not(.pk-leaving) .pk-action.pk-cancel')
    ok(until(pg, "U.sheet===null&&!held()") if pg.evaluate("typeof held==='function'") else until(pg, "U.sheet===null"), 'tapping it closes the sheet')
    ok(not pg.evaluate("MELODY.has('g_1')"), 'Cancel keeps nothing')
    read(pg, 'paper-lanterns.pdf', wait="U.sheet==='melTitle'"); pg.evaluate("SG_ACT.melTitleNew()")
    ok(pg.evaluate("U.sheet") == 'sgNew' and pg.evaluate("U.sDraft.title") == 'Paper Lanterns' and pg.evaluate("U.sDraft.artist") == 'The Made Up Band' and pg.evaluate("!!U.sDraft.melody"), 'Make a new song opens New song with the print’s title and artist')
    pg.evaluate("U.sDraft=null;U.sheet=null;rerender()")
    read(pg, 'paper-lanterns.pdf', wait="U.sheet==='melTitle'"); pg.evaluate("SG_ACT.melTitleHere()")
    ok(pg.evaluate("U.sheet") == 'melRead', 'This song carries on to Sheet music read')
    pg.evaluate("SG_ACT.melSave()"); until(pg, "MELODY.has('g_1')")
    pg.evaluate("U.sheet=null;U.sd={};rerender()")  # the key sheet it offered
    # a second print: ask to replace; the old one to the safety copies; octave and anchors carry over
    pg.evaluate("MELODY.edit('g_1',{octave:1})"); until(pg, "MELODY.get('g_1').octave===1")
    pg.evaluate("async()=>{const s=MELODY.get('g_1');s.anchors=[{tick:0,t:1.5}];s.rev++;await MELODY._put('g_1',s,s.rev-1)}")
    pg.evaluate(NAME, 'Paper Lanterns')
    ok(read(pg, 'paper-lanterns.pdf', wait="U.sheet==='melReplace'") and pg.locator('[data-screen="VS-103"]').count() == 1, 'a second print asks to replace (VS-103)')
    pg.evaluate("SG_ACT.melReplaceYes()")
    ok(pg.evaluate("U.sheet") == 'melRead' and pg.evaluate("MELODY.held().octave") == 1, 'the octave carries over')
    rev = pg.evaluate("MELODY.get('g_1').rev")
    pg.evaluate("SG_ACT.melSave()"); until(pg, "id=>MELODY.get('g_1').rev>id", arg=rev)
    ok(pg.evaluate("MELODY.get('g_1').anchors") == [{'tick': 0, 't': 1.5}] and pg.evaluate("MELODY.get('g_1').octave") == 1, 'the anchors and octave are kept')
    ok(pg.evaluate("SAFE.list().some(m=>m.key.startsWith('melody:g_1:'))"), 'the old score is kept in the safety copies for 30 days')
    pg.evaluate("U.sheet=null;U.sd={};rerender()")
    # the same UG print on another song: offer to open it
    pg.evaluate("D.songs.push({id:'g_2',name:'Paper Lanterns',added:Date.now()});save();go(()=>{U.view='lyr';U.songId='g_2'})")
    ok(read(pg, 'paper-lanterns.pdf', {'id': 'g_2'}, wait="U.sheet==='melSame'"), 'the same UG print on another song asks (VS-101)')
    pg.evaluate("SG_ACT.melSameOpen(null,null,'g_1')")
    ok(pg.evaluate("U.view") == 'lyr' and pg.evaluate("U.songId") == 'g_1' and not pg.evaluate("MELODY.has('g_2')"), 'Open takes you to that song, adding nothing')
    # leaving mid-read: a "Sheet ready" toast; a song deleted meanwhile drops the read
    pg.evaluate(START, ['rain-on-the-ferry.pdf', {'id': 'g_2'}, None, False]); until(pg, "MELODY.reading()!==null")
    pg.evaluate("window.__toasts=[];go(()=>{U.tab='today';U.view=null})")
    ok(until(pg, "MELODY.reading()===null", 20000) and 'Sheet ready' in pg.evaluate("window.__toasts"), 'leaving mid-read: "Sheet ready" when it finishes')
    ok(not pg.evaluate("MELODY.has('g_2')"), '(and nothing is saved until it’s opened and saved)')
    pg.evaluate(START, ['rain-on-the-ferry.pdf', {'id': 'g_2'}, None, False]); until(pg, "MELODY.reading()!==null")
    pg.evaluate("window.__toasts=[];deleteSongs(['g_2'])")
    ok(until(pg, "MELODY.reading()===null", 20000) and pg.evaluate("U.sheet") is None and 'Sheet ready' not in pg.evaluate("window.__toasts"), 'a read whose song was deleted is dropped')
    pg.context.close()


def part_screens(b, t, ok):
    for w, h, sc, red in [(375, 812, 'light', False), (375, 812, 'dark', True), (820, 1180, 'light', False), (820, 1180, 'dark', False)]:
        tag = f'{w}-{sc}' + ('-reduced' if red else '')
        pg = fresh(t, b, w=w, h=h, sc=sc, init="try{localStorage.setItem('vocalReduce','on')}catch(e){}" if red else None)
        pg.evaluate(NAME, 'Paper Lanterns'); pg.evaluate(SONG); pg.wait_for_timeout(300)
        row = pg.locator('#app [data-name="sheet-music-row"]')
        ok(row.count() == 1 and 'Add sheet music' in row.inner_text(), f'{tag}: the Song page has Add sheet music (VS-009 › sheet-music-row)')
        if w == 375 and sc == 'light':
            with pg.expect_file_chooser() as fc: row.click()
            fc.value.set_files(os.path.join(MEL, 'paper-lanterns.pdf'))
            ok(until(pg, "U.sheet==='melRead'", 20000) and pg.locator('[data-screen="VS-100"]').count() == 1, f'{tag}: the real door reads the print into VS-100')
        else:
            read(pg, 'paper-lanterns.pdf')
        t.shot(pg, 'read-' + tag)
        ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{tag}: nothing runs off the side')
        pg.click('#layer [data-a="melOct"][data-v="1"]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("MELODY.held().octave") == 1, f'{tag}: Higher moves the octave')
        pg.click('#layer [data-a="melTempo"][data-v="1"]'); pg.wait_for_timeout(100)
        pg.fill('#melTempoIn', '183'); pg.dispatch_event('#melTempoIn', 'change'); pg.wait_for_timeout(100)
        pg.click('#layer [data-a="melTempo"][data-v="1"]'); pg.wait_for_timeout(100)
        ok(pg.evaluate("MELODY.held().tempo") == 184, f'{tag}: the tempo is typed and moves by 1')
        pg.click('#layer [data-a="melSave"]'); until(pg, "MELODY.has('g_1')")
        ok(until(pg, "U.sheet==='keyPick'") and pg.evaluate("U.sd.tonic") == 'D' and 'From the print: D major or B minor' in pg.inner_text('#layer'),
           f'{tag}: the key is offered through the key sheet (VS-098), on D, never set without asking')
        ok(not pg.evaluate("SONGKEY.of(songById('g_1'))"), f'{tag}: (nothing set until Use)')
        pg.evaluate("U.sheet=null;rerender()"); pg.wait_for_timeout(200)
        txt = pg.inner_text('#app [data-name="sheet-music-row"]')
        ok('Sheet music' in txt and '18 bars' in txt and 'sits' in txt, f'{tag}: the row shows the key, bars, range and where the song sits ({txt.splitlines()[-2] if len(txt.splitlines()) > 1 else txt})')
        t.shot(pg, 'row-' + tag)
        row.click(); until(pg, "U.view==='mel'")  # Q47: the row opens the Sheet music page (VS-108); its top bar circle opens VS-099
        pg.click('#barR [data-a="melInfo"]'); pg.wait_for_timeout(300)
        ok(pg.locator('[data-screen="VS-099"]').count() == 1 and pg.evaluate("U.sheet") == 'melSheet', f'{tag}: the Sheet music page\'s circle opens Sheet music (VS-099) with the to-check list')
        ok(pg.evaluate("MELODY.get('g_1').octave") == 1 and pg.evaluate("MELODY.get('g_1').tempo") == 184, f'{tag}: the octave and tempo were saved')
        pg.click('#layer [data-a="melOct"][data-v="0"]'); until(pg, "MELODY.get('g_1').octave===0")
        ok(True, f'{tag}: the octave changes from VS-099 too')
        t.shot(pg, 'sheet-' + tag, full_page=True)
        ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{tag}: VS-099 fits')
        pg.evaluate("go(()=>{U.view='lyr';U.songId='g_1';U.sheet=null;U.sd={}})"); until(pg, "U.view==='lyr'")
        if w == 375 and sc == 'light':
            # the row with no print on this device, and with a note but no score
            pg.evaluate("songById('g_1').ext.melody={ug:'1',at:1};save()")
            pg.evaluate("async()=>{await MELODY.forget(['g_1']);rerender()}"); pg.wait_for_timeout(200)
            ok('Sheet not on this device' in row.inner_text(), f'{tag}: "Sheet not on this device" when the score isn’t here')
            # New song (VS-051): Add media takes a PDF too
            pg.evaluate("U.tab='songs';U.view=null;render()")
            pg.evaluate("U.sDraft={step:1,title:'',artist:'',text:'',mode:'media'};U.sheet='sgNew';U.sd={};rerender()"); pg.wait_for_timeout(300)
            ok(pg.locator('#layer [data-name="sheet-music-door"]').count() == 1, f'{tag}: New song (VS-051) has Choose sheet music')
            t.shot(pg, 'newsong-' + tag)
            with pg.expect_file_chooser() as fc: pg.click('#layer [data-a="sgAddPdf"]')
            fc.value.set_files(os.path.join(MEL, 'rain-on-the-ferry.pdf'))
            ok(until(pg, "U.sheet==='sgNew'&&U.sDraft&&!!U.sDraft.melody", 20000), f'{tag}: the print is read for the new song')
            ok(pg.input_value('#sgTitle') == 'Rain On The Ferry' and pg.input_value('#sgArtist') == 'Nobody Real', f'{tag}: its title and artist fill New song’s fields')
            t.shot(pg, 'newsong-read-' + tag)
            pg.click('#layer [data-a="sgSplit"]')
            ok(until(pg, "D.songs.some(s=>s.name==='Rain On The Ferry'&&s.ext&&s.ext.melody)", 8000), f'{tag}: Save song saves the song with its sheet music')
            nid = pg.evaluate("D.songs.find(s=>s.name==='Rain On The Ferry').id")
            ok(until(pg, "id=>MELODY.has(id)&&MELODY.hasPrint(id)", 5000, nid), f'{tag}: the score and the print are kept')
            # Settings › Storage
            pg.evaluate("U.tab='settings';U.view='set';U.setPg='storage';U.sheet=null;render()"); pg.wait_for_timeout(300)
            ok(pg.locator('#app').get_attribute('data-screen') == 'VS-020' and pg.locator('text=Sheet music').count() >= 1 and pg.locator('[data-name="remove-prints-row"]').count() == 1, f'{tag}: Settings › Storage has a Sheet music row and Remove prints, keep scores')
            t.shot(pg, 'storage-' + tag)
        pg.context.close()


def part_offline(b, t, ok):
    """The service worker saves pdf.js on the first import, so an import works with no signal afterwards."""
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, user_agent=UA_IPHONE, timezone_id='Europe/London')
    ctx.add_init_script("try{localStorage.setItem('vocalMotion','0')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(url(APP_PATH)); pg.evaluate(SEED, {'v2': True, 'songs': [{'id': 'g_1', 'name': 'Paper Lanterns'}]}); pg.reload(); ready(pg)
    ok(until(pg, "navigator.serviceWorker&&navigator.serviceWorker.controller!==null", 15000) or (pg.reload() or ready(pg) or until(pg, "navigator.serviceWorker.controller!==null", 15000)), 'the service worker looks after the page')
    pg.evaluate(TOASTS)
    ok(read_save(pg, 'paper-lanterns.pdf'), 'a first import, online')
    ok(pg.evaluate("async()=>{const c=await caches.open('vocal-sessions-v3');return !!(await c.match(new URL('js/vendor/pdfjs-4.10.38/pdf.min.js',location.href).href))&&!!(await c.match(new URL('js/vendor/pdfjs-4.10.38/pdf.worker.min.js',location.href).href))}"),
       'pdf.js is saved for offline use after the first import')
    ok(pg.evaluate("async()=>{const c=await caches.open('vocal-sessions-v3');return !!(await c.match(document.querySelector('link[href^=\"js/melodyread.js\"]').getAttribute('href')))}"), 'the reader is saved with the app’s files')
    pg.evaluate("D.songs.push({id:'g_2',name:'Rain On The Ferry'});save()")
    fetched = pg.evaluate("async()=>{const r=await fetch('tests/fixtures/melody/rain-on-the-ferry.pdf');return Array.from(new Uint8Array(await r.arrayBuffer()))}")
    offline(APP_PATH)
    try:
        pg.reload(); ready(pg); pg.evaluate(TOASTS)
        pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId='g_2'})")
        pg.evaluate("async(a)=>{const f=new File([new Uint8Array(a)],'rain.pdf',{type:'application/pdf'});await MELODY.start(f,{id:'g_2'})}", fetched)
        ok(until(pg, "U.sheet==='melRead'", 20000), 'with no signal, a print still reads (%s)' % pg.evaluate("JSON.stringify([window.__toasts,U.sheet,MELODY.reading()])"))
    finally:
        online(APP_PATH)
    ctx.close()
