/* Vocal Sessions · application.js
   Q20 Application, the session's last step: pick up where you left off, sing, compare, keep the best take, move on.
   - The card (APPL.body(), drawn by flowBody(2) in screens.js) carries on with the last song and section you sang
     (a take's place, or a session's song saved as ext.app), or the song picked from Other songs. A song with no
     sections is always Whole song. Change section shows its places as pills
   - Sing over the track (this device, vocalSongPrefs.singOver, on by default): with the song's track on the device,
     Sing plays it from just before the section and records over it. It uses Q16's exception and its sheet
     (recOverSheet: headphones, or the speaker after a confirmation). While it records, the card is the recording,
     the page stays still and the floating window is the red track window (FW_REC in window.js)
   - The takes sung here (X.takes), newest first, with their waveforms (takesBlock() in screens.js, shared with Song
     practice): Star, Compare ("This take | Take N", one tap, from the same moment), ↻ Again and Done. Done flashes
     green and the song folds to one line; "Practised, not recorded" folds it without a take
   - Other songs, sorted by Recently practised or A–Z (this page only)
   The draft keeps the card: X.sing = {id, o, st: 'open' | 'done' | 'norec'}. X.song is the song practised, set when a
   take of it is saved or it's marked practised; finishSession() saves it as before, with ss.ext.app = {song, o?, noRec?}
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */
const APPL = (() => {
  const LEAD = 2; // seconds of the track before the section, to come in on
  const SORTS = [
    ['recent', 'Recently practised'],
    ['az', 'A–Z'],
  ];
  const timers = [];
  const slow = () => (MOTION.on() ? MOTION.speed() : 1);
  const later = (fn, ms) => timers.push(setTimeout(fn, ms * slow()));
  const q = (sel) => document.querySelector(sel);

  /* ----- where you left off ----- */
  const sameO = (a, b) => (a || null) === (b || null);
  // a place that's still in the song, else Whole song (null)
  const okO = (sg, o) => (o && hasLyrics(sg) && occIdx(sg, o) >= 0 ? o : null);
  function secName(sg, o) {
    const i = o && hasLyrics(sg) ? occIdx(sg, o) : -1;
    return i < 0 ? 'Whole song' : occLabel(sg, i);
  }
  const appOf = (ss) =>
    ss && ss.ext && ss.ext.app && typeof ss.ext.app.song === 'string' ? ss.ext.app : null;
  // every time a song was sung: its takes, and sessions' songs (practised, not recorded too)
  function sung() {
    const out = [];
    TAKES.forEach((t) => {
      const sg = songById(t.songId);
      if (sg) out.push({ id: sg.id, o: okO(sg, t.o), at: +t.created || 0, take: true });
    });
    (D.sessions || []).forEach((ss) => {
      const a = appOf(ss),
        sg = a && songById(a.song);
      if (sg) out.push({ id: sg.id, o: okO(sg, a.o), at: new Date(sessEnd(ss)).getTime() || 0 });
    });
    return out;
  }
  function carryOn() {
    let best = null;
    sung().forEach((s) => {
      if (!best || s.at > best.at) best = s;
    });
    return best;
  }
  // the section last sung of a song (Whole song if none)
  function lastSec(id) {
    let best = null;
    sung().forEach((s) => {
      if (s.id === id && (!best || s.at > best.at)) best = s;
    });
    return best ? best.o : null;
  }
  // when a song was last sung: any section (o left out), or one section (null: Whole song)
  function lastSung(id, o) {
    let at = 0;
    sung().forEach((s) => {
      if (s.id === id && (o === undefined || sameO(s.o, o)) && s.at > at) at = s.at;
    });
    return at || null;
  }
  // the song on the card: the one picked here, the one this session practised (a 3.39 draft), or where you left off
  function cur() {
    if (!X || isSong()) return null;
    const s = X.sing,
      sg = s && songById(s.id);
    if (sg)
      return {
        sg,
        o: okO(sg, s.o),
        st: s.st === 'done' || s.st === 'norec' ? s.st : 'open',
        skip: Array.isArray(s.skip) ? s.skip.filter(rungOf) : [], // Q37: the ladder's skipped rungs
      };
    const sp = songById(X.song);
    if (sp) return { sg: sp, o: null, st: 'open', skip: [] };
    const c = carryOn();
    return c ? { sg: songById(c.id), o: c.o, st: 'open', carry: true, skip: [] } : null;
  }
  // takes of this song and section: all of them, oldest first, and the ones sung in this session, newest first
  const allAt = (c) => TAKES.filter((t) => t.songId === c.sg.id && sameO(okO(c.sg, t.o), c.o));
  const mineAt = (c) =>
    allAt(c)
      .filter((t) => (X.takes || []).includes(t.id))
      .reverse();
  function prevOf(c, t) {
    const all = allAt(c),
      i = all.indexOf(t);
    return i > 0 ? all[i - 1] : null;
  }
  const short = (t) => TAKE.short(t.id);
  const keep = (c) => {
    X.sing = Object.assign({ id: c.sg.id, o: c.o, st: c.st }, c.skip && c.skip.length ? { skip: c.skip.slice() } : {});
  };

  /* ----- the step's markup ----- */
  function body() {
    if (!X) return '';
    const c = cur(),
      recNow = !!(rec && rec.app);
    if (!D.songs.length)
      return (
        '<div class="grp"><div class="empty">Add a song in Songs to sing it here.</div></div>' +
        '<div class="grp"><button class="row acc" data-a="sheet" data-v="addSong"><span class="lbl">Add song</span>' +
        ICON.plus +
        '</button></div>'
      );
    let h = c ? card(c) : '';
    if (!recNow && !(c && c.st !== 'open')) h += others(c);
    return h;
  }
  function head(c, eye, sub) {
    return (
      '<div class="aphead">' +
      songTile +
      '<span class="lbl"><span class="apeye">' +
      eye +
      '</span><b class="apname">' +
      esc(songTitle(c.sg)) +
      (c.o ? ' · ' + esc(secName(c.sg, c.o)) : '') +
      '</b><small>' +
      sub +
      '</small></span></div>'
    );
  }
  function card(c) {
    const sg = c.sg;
    if (rec && rec.app) return recCard();
    const mine = mineAt(c);
    if (c.st !== 'open') {
      const st = mine.filter((t) => t.star).pop(),
        lad = ladderOn(sg) ? mine.filter(takeRung).length : 0, // Q37: "Song · Section · Ladder · N takes"
        line =
          songTitle(sg) +
          (c.o ? ' · ' + secName(sg, c.o) : '') +
          (c.st === 'norec'
            ? ' · practised, not recorded'
            : lad
              ? ' · Ladder · ' + lad + ' take' + (lad === 1 ? '' : 's')
              : ' · ' + mine.length + ' take' + (mine.length === 1 ? '' : 's') + (st ? ' · ★ ' + short(st) : ''));
      return (
        '<div class="apcard closed" id="apcard"><button class="osum apline' +
        (c.st === 'norec' ? ' skipped' : '') +
        '" data-a="apReopen" aria-label="' +
        esc(line) +
        '. Tap to change"><span class="otick" aria-hidden="true">' +
        (c.st === 'norec' ? '–' : ICON.check) +
        '</span><span class="lbl">' +
        esc(line) +
        '</span><span class="oedit" aria-hidden="true">Edit</span></button></div>'
      );
    }
    const all = allAt(c),
      at = lastSung(sg.id, c.o),
      ago = at ? 'Last sung ' + relDay(new Date(at)) : 'Not sung yet',
      sub = mine.length
        ? mine.length + ' take' + (mine.length === 1 ? '' : 's') + ' today'
        : ago + (all.length ? ' · ' + all.length + ' take' + (all.length === 1 ? '' : 's') : ''),
      eye = mine.length ? 'Today' : at ? 'Carry on' : 'Up next';
    let h =
      '<div class="apcard" id="apcard"><span class="rsweep apsweep" aria-hidden="true"></span>' +
      head(c, eye, esc(sub));
    const secs = hasLyrics(sg) ? sg.order : [];
    if (U.apSec && secs.length)
      h +=
        '<div class="appills" role="group" aria-label="Section">' +
        [null]
          .concat(secs.map((x) => x.o))
          .map(
            (o) =>
              '<button class="appill' +
              (sameO(o, c.o) ? ' on' : '') +
              '" data-a="apSec" data-v="' +
              esc(o || '') +
              '" aria-pressed="' +
              sameO(o, c.o) +
              '">' +
              esc(secName(sg, o)) +
              '</button>'
          )
          .join('') +
        '</div>';
    h += modeSeg(sg);
    if (ladderOn(sg)) return h + ladder(c) + '</div>';
    if (mine.length) {
      const prev = prevOf(c, mine[0]);
      h +=
        takesBlock(mine, { fresh: true, prev, name: short }) +
        '<div class="aprow"><button class="apsoft" data-a="apSing">↻ Again</button><button class="apsoft" data-a="apDone">Done</button></div>';
    } else {
      if (TRACK.has(sg.id))
        h +=
          '<button class="row aptrk" data-a="apOver" role="switch" aria-checked="' +
          overOn() +
          '"><span class="lbl">♪ Sing over the track</span><span class="tgl" aria-checked="' +
          overOn() +
          '" aria-hidden="true"></span></button>';
      h +=
        '<button class="apsing" data-a="apSing"><span class="dot" aria-hidden="true"></span>Sing</button>' +
        '<div class="aplinks">' +
        (secs.length
          ? '<button data-a="apSecs">' + (U.apSec ? 'Keep ' + esc(secName(sg, c.o)) : 'Change section') + '</button><span aria-hidden="true">·</span>'
          : '') +
        '<button data-a="apNoRec">Practised, not recorded</button></div>';
    }
    return h + '</div>';
  }
  // the card while it records: the section, the time, the meter, its words and Stop. Nothing else moves
  function recCard() {
    const sg = songById(rec.songId),
      o = sg ? okO(sg, rec.o) : null,
      r = rungOf(rec.rung), // Q37: a rung of the ladder: its lyric view and the live pitch line
      words = sg ? lyricsOf(sg, o, r ? r.lyr : null) : '';
    return (
      '<div class="apcard rec" id="apcard" role="group" aria-label="Recording"><div class="aphead"><span class="lbl"><b class="apname">' +
      esc(sg ? secName(sg, o) : 'Recording') +
      '</b><small><span class="recdot" aria-hidden="true"></span>Recording' +
      (r ? ' · ' + esc(r.name) : '') +
      (rec.over && rec.from != null ? ' · track from ' + mmss(rec.from) : '') +
      '</small></span><span class="aptime" id="recT">' +
      mmss(rec.t) +
      '</span></div><span class="meter apmeter" id="recMeter" aria-hidden="true">' +
      '<i></i>'.repeat(14) +
      '</span>' +
      (r
        ? '<div class="aplive" id="apLive" style="--rc:' + r.col + '">' + liveSVG([], r.col, null, null, SONGKEY.lanesFor(sg)) + '</div>'
        : '') +
      words +
      '<button class="apstop" data-a="apStop"><span aria-hidden="true"></span>Stop</button></div>'
    );
  }
  // the words to sing: the section's lines, or every section's for Whole song. view (Q37's rungs): 'faint' (the trill
  // and hum: the words faded), 'vowels' (the vowel letters picked out: spelling, not sounds) or the words as they are
  const VOWEL = /[aeiouáéíóúàèìòùâêîôûäëïöüæœ]/i;
  const vowelsOf = (w) =>
    [...w].map((ch) => (VOWEL.test(ch) ? '<b>' + esc(ch) + '</b>' : '<span>' + esc(ch) + '</span>')).join('');
  function lyricsOf(sg, o, view) {
    if (!hasLyrics(sg)) return '';
    const cls = view === 'faint' ? ' faint' : view === 'vowels' ? ' vowels' : '';
    const line = (l) =>
      '<p>' + (view === 'vowels' ? (l || []).map(vowelsOf).join(' ') : esc((l || []).join(' '))) + '</p>';
    if (o) {
      const x = sg.order[occIdx(sg, o)],
        s = x && sg.sections[x.sid];
      return s && s.lines && s.lines.length ? '<div class="aply' + cls + '">' + s.lines.map(line).join('') + '</div>' : '';
    }
    return (
      '<div class="aply' +
      cls +
      '">' +
      sg.order
        .map((x, i) => {
          const s = sg.sections[x.sid];
          return s && s.lines && s.lines.length
            ? '<small>' + esc(occLabel(sg, i)) + '</small>' + s.lines.map(line).join('')
            : '';
        })
        .join('') +
      '</div>'
    );
  }
  function others(c) {
    const list = D.songs.filter((s) => !c || s.id !== c.sg.id),
      k = U.apSort || 'recent';
    if (!list.length) return '';
    const m = {};
    list.forEach((s) => (m[s.id] = lastSung(s.id) || 0));
    list.sort((a, b) =>
      k === 'az'
        ? songTitle(a).localeCompare(songTitle(b), 'en-GB', { sensitivity: 'base' })
        : m[b.id] - m[a.id] || (b.added || 0) - (a.added || 0)
    );
    return (
      '<button class="sorthdr" data-a="apSort" aria-haspopup="menu"><span>' +
      (c ? 'Other songs' : 'Songs') +
      '&nbsp;·&nbsp;</span><span class="sortname">' +
      SORTS.find((x) => x[0] === k)[1] +
      '</span>' +
      ICON.down +
      '</button><div class="grp tiled apsongs">' +
      list
        .map((s) => {
          const at = m[s.id],
            r = at ? relDay(new Date(at)) : '';
          return (
            '<button class="row" data-a="apSong" data-k="' +
            s.id +
            '">' +
            songTile +
            '<span class="lbl">' +
            esc(songTitle(s)) +
            '<small>' +
            (r ? r.charAt(0).toUpperCase() + r.slice(1) : 'Not sung yet') +
            (hasLyrics(s) ? '' : ' · whole song') +
            '</small></span>' +
            chev +
            '</button>'
          );
        })
        .join('') +
      '</div>'
    );
  }
  // a take's waveform: bars from its peaks once they've been read (TAKE.analyse), flat until then
  const BARS = 32;
  function bars(id) {
    const p = TAKE.peaks(id);
    if (!p || !p.length) return null;
    const out = [];
    for (let i = 0; i < BARS; i++) {
      const a = Math.floor((i * p.length) / BARS),
        b = Math.max(a + 1, Math.floor(((i + 1) * p.length) / BARS));
      let mx = 0;
      for (let j = a; j < b && j < p.length; j++) if (p[j] > mx) mx = p[j];
      out.push(Math.max(12, Math.round((mx / 255) * 100)));
    }
    return out;
  }
  const barsHTML = (b) => (b ? b.map((h) => '<i style="height:' + h + '%"></i>').join('') : '<i></i>'.repeat(BARS));
  function wave(id) {
    const b = bars(id);
    return (
      '<span class="tkwv' +
      (b ? '' : ' wait') +
      '" data-wv="' +
      id +
      '" aria-hidden="true">' +
      barsHTML(b) +
      '<span class="tkpg" id="pg-' +
      id +
      '"></span></span>'
    );
  }
  // a take's waveform has just been read: its rows show it, in place
  function waved(id) {
    const b = bars(id);
    if (!b) return;
    document.querySelectorAll('.tkwv.wait[data-wv="' + id + '"]').forEach((w) => {
      const pg = w.querySelector('.tkpg');
      w.classList.remove('wait');
      w.innerHTML = barsHTML(b);
      if (pg) w.appendChild(pg);
    });
  }
  // Compare: one tap between this take and the one before, from the same moment
  function cmpHTML(t, prev, prevName) {
    const on = playingId === prev.id ? 1 : 0;
    return (
      '<div class="seg apcmp" role="group" aria-label="Compare"><span class="knob" aria-hidden="true"></span>' +
      '<button data-a="apCmp" data-v="0" data-k="' +
      t.id +
      '" class="' +
      (on ? '' : 'on') +
      '" aria-pressed="' +
      !on +
      '">This take</button><button data-a="apCmp" data-v="1" data-k="' +
      prev.id +
      '" class="' +
      (on ? 'on' : '') +
      '" aria-pressed="' +
      !!on +
      '">' +
      esc(prevName) +
      '</button></div>'
    );
  }

  /* ----- Q37 the song ladder -----
     A section sung four ways (RUNGS in config.js: lip trill, hum, vowels only, words), each an ordinary take of the
     place with ext.rung. The rungs sung this session fold into one row; only the current rung is open; the rest are
     "Up next". From two rungs, Lines overlays their pitch lines (PITCH) and names where the words part from the trill;
     once all four are sung, Notes of the line plays the trill's held notes. The Straight / Ladder switch is the song's
     own (sg.ext.ladder). Pitch lines are worked out when needed, in memory only */
  const ladderOn = (sg) => !!(sg && sg.ext && sg.ext.ladder === true);
  function modeSeg(sg) {
    const on = ladderOn(sg);
    return (
      '<div class="seg wide apmode" role="group" aria-label="How to sing it"><span class="knob" aria-hidden="true"></span>' +
      '<button data-a="apMode" data-v="straight" class="' +
      (on ? '' : 'on') +
      '" aria-pressed="' +
      !on +
      '">Straight</button><button data-a="apMode" data-v="ladder" class="' +
      (on ? 'on' : '') +
      '" aria-pressed="' +
      on +
      '">Ladder</button></div>'
    );
  }
  // this session's ladder at this place: the newest take of each rung, the rungs skipped, the one to sing next
  function ladState(c) {
    const sung = {};
    mineAt(c).forEach((t) => {
      const r = takeRung(t);
      if (r && !sung[r.id]) sung[r.id] = t;
    });
    const skip = (c.skip || []).filter((id) => !sung[id]),
      cur = RUNGS.find((r) => !sung[r.id] && !skip.includes(r.id)) || null,
      list = RUNGS.filter((r) => sung[r.id]);
    return {
      sung,
      skip,
      cur,
      list,
      later: cur ? RUNGS.filter((r) => RUNGS.indexOf(r) > RUNGS.indexOf(cur) && !sung[r.id] && !skip.includes(r.id)) : [],
      // the lines compared: the trill (else the hum) and the words (else the vowels)
      base: sung.trill ? 'trill' : sung.hum ? 'hum' : null,
      target: sung.words ? 'words' : sung.vowels ? 'vowels' : null,
    };
  }
  const RUN_WORD = { trill: 'trill', hum: 'hum', vowels: 'vowels', words: 'words' };
  function ladder(c) {
    const L = ladState(c),
      n = L.list.length;
    need(L.list.map((r) => L.sung[r.id].id));
    let h = '<div class="lad">';
    if (n) {
      const open = !!U.apFold;
      h +=
        '<button class="ladsum' +
        (open ? ' open' : '') +
        '" data-a="apLadFold" aria-expanded="' +
        open +
        '"><span class="laddots" aria-hidden="true">' +
        L.list.map((r) => '<i style="background:' + r.col + '"></i>').join('') +
        '</span><span class="lbl">' +
        n +
        ' of 4 sung<small>' +
        L.list.map((r) => r.short).join(' · ') +
        (L.skip.length ? ' · skipped ' + L.skip.map((id) => rungOf(id).short).join(', ') : '') +
        '</small></span>' +
        ICON.down +
        '</button>';
      if (open)
        h +=
          '<div class="ladrows">' +
          L.list
            .map((r) => {
              const t = L.sung[r.id],
                on = takePlaying(t.id),
                nm = 'Ladder · ' + r.name;
              return (
                '<div class="ladrow" data-rung="' +
                r.id +
                '"><span class="laddot" style="background:' +
                r.col +
                '" aria-hidden="true"></span><span class="lbl">' +
                (RUNGS.indexOf(r) + 1) +
                ' · ' +
                esc(r.name) +
                '<small>' +
                mmss(t.len) +
                '</small></span>' +
                PITCH.spark(PITCH.got(t.id), r.col) +
                '<button class="tkplay" data-a="playTake" data-k="' +
                t.id +
                '" aria-label="' +
                (on ? 'Pause ' : 'Play ') +
                esc(nm) +
                '">' +
                (on ? ICON.pause : ICON.play) +
                '</button></div>'
              );
            })
            .join('') +
          '</div>';
    }
    if (L.cur) {
      const r = L.cur,
        i = RUNGS.indexOf(r);
      h +=
        '<div class="ladcur" data-rung="' +
        r.id +
        '"><div class="ladrn"><span class="laddot hollow" style="--rc:' +
        r.col +
        '" aria-hidden="true"></span><b>' +
        (i + 1) +
        ' · ' +
        esc(r.name) +
        '</b></div><p class="ladhow">' +
        esc(r.how) +
        '</p>' +
        lyricsOf(c.sg, c.o, r.lyr) +
        (TRACK.has(c.sg.id)
          ? '<button class="row aptrk" data-a="apOver" role="switch" aria-checked="' +
            overOn() +
            '"><span class="lbl">♪ Sing over the track</span><span class="tgl" aria-checked="' +
            overOn() +
            '" aria-hidden="true"></span></button>'
          : '') +
        '<button class="apsing" data-a="apSing"><span class="dot" aria-hidden="true"></span>Sing · ' +
        esc(r.short) +
        '</button><div class="aplinks"><button data-a="apSkip">Skip this rung</button>' +
        (!n && hasLyrics(c.sg) && c.sg.order.length
          ? '<span aria-hidden="true">·</span><button data-a="apSecs">' +
            (U.apSec ? 'Keep ' + esc(secName(c.sg, c.o)) : 'Change section') +
            '</button>'
          : '') +
        (!n ? '<span aria-hidden="true">·</span><button data-a="apNoRec">Practised, not recorded</button>' : '') +
        '</div></div>';
      if (L.later.length) h += '<div class="ladnext">Up next: ' + esc(L.later.map((x) => x.name).join(', ')) + '</div>';
    } else if (!n)
      h +=
        '<p class="ladhow">Every rung skipped.</p><div class="aplinks"><button data-a="apLadAgain">Start the ladder again</button>' +
        '<span aria-hidden="true">·</span><button data-a="apNoRec">Practised, not recorded</button></div>';
    h += '</div>';
    if (n >= 2) h += lines(c, L);
    if (n === 4) h += notesBlock(L);
    if (n >= 2) h += keyPart(c, L);
    if (n && (n >= 2 || !L.cur)) h += '<div class="aprow"><button class="apsoft" data-a="apDone">Done</button></div>';
    return h;
  }
  // which lines are drawn: chosen with the chips (this screen only), else the two compared (all, with only two)
  function lnOn(L, id) {
    const m = U.apLn || {};
    if (id in m) return !!m[id];
    return L.list.length <= 2 || id === L.base || id === L.target;
  }
  function lines(c, L) {
    const got = (id) => PITCH.got(L.sung[id].id),
      ready = L.list.every((r) => got(r.id)),
      ln = L.list.map((r) => ({ a: got(r.id), col: r.col, on: lnOn(L, r.id), key: r.id })),
      sp = spot(c, L);
    let h =
      '<div class="ladsec"><div class="ladhd">Lines</div>' +
      (ready
        ? '<div class="apchart">' +
          PITCH.svg(ln, {
            w: 340,
            h: 170,
            marker: sp && sp.at != null ? { t: sp.t } : null,
            lanes: SONGKEY.lanesFor(c.sg), // Q39 the song key's scale lanes
            label: 'Pitch lines of ' + L.list.map((r) => r.name).join(', '),
          }) +
          '</div>'
        : '<div class="apchart wait" aria-busy="true"><span>Reading the lines…</span></div>') +
      '<div class="ladchips" role="group" aria-label="Lines shown">' +
      L.list
        .map((r) => {
          const on = lnOn(L, r.id);
          return (
            '<button class="ladchip' +
            (on ? '' : ' off') +
            '" data-a="apLine" data-v="' +
            r.id +
            '" aria-pressed="' +
            on +
            '"><i style="background:' +
            r.col +
            '" aria-hidden="true"></i>' +
            esc(r.short) +
            '</button>'
          );
        })
        .join('') +
      (SONGKEY.of(c.sg) && SONGKEY.has()
        ? '<button class="ladchip keychip' +
          (SONGKEY.lanesOn() ? '' : ' off') +
          '" data-a="keyLanes" aria-pressed="' +
          SONGKEY.lanesOn() +
          '"><i aria-hidden="true"></i>Scale lanes</button>'
        : '') +
      '</div>';
    if (sp && sp.none)
      h +=
        '<p class="ladspot">The ' + RUN_WORD[L.target] + ' stay with the ' + RUN_WORD[L.base] + ' all the way through.</p>';
    else if (sp)
      h +=
        '<div class="ladspot"><p>The ' +
        RUN_WORD[L.target] +
        ' part from the ' +
        RUN_WORD[L.base] +
        ' ' +
        esc(sp.where) +
        '<small>Hear the ' +
        RUN_WORD[L.base] +
        ' there, then the ' +
        RUN_WORD[L.target] +
        '.</small></p><button class="apsoft" data-a="apHear">' +
        ICON.play +
        'Hear both</button></div>';
    return h + '</div>';
  }
  // Q39 the song key, then Practise in <key>, from the trill's (or hum's) line, once the lines are read
  function keyPart(c, L) {
    const a = PITCH.got(L.sung[L.base || L.list[0].id].id);
    if (!a || !L.list.every((r) => PITCH.got(L.sung[r.id].id))) return '';
    return SONGKEY.block(c, a, spot(c, L));
  }
  // where the words (or vowels) part from the trill (or hum): {at, len, t, where}, {none: true}, or null (not yet)
  function spot(c, L) {
    if (!L.base || !L.target) return null;
    const a = PITCH.got(L.sung[L.base].id),
      b = PITCH.got(L.sung[L.target].id);
    if (!a || !b) return null;
    const p = PITCH.part(a, b);
    if (!p) return { none: true };
    return Object.assign(p, { where: whereAt(c.sg, c.o, p.t) });
  }
  // named by line when Song Clock has the section's lines timed (the first note taken as its first line's start),
  // otherwise by time
  function whereAt(sg, o, t) {
    try {
      if (hasLyrics(sg) && ckSynced(sg)) {
        const M = ckModel(sg),
          k = o ? occIdx(sg, o) : -1,
          idx = M.L.map((l, i) => i).filter((i) => k < 0 || M.L[i].k === k);
        const t0 = idx.length && M.T[idx[0]] ? M.T[idx[0]][0] : null;
        if (t0 != null) {
          let at = 0;
          idx.forEach((i, n) => {
            if (M.T[i] && M.T[i][0] != null && M.T[i][0] - t0 <= t + 0.05) at = n;
          });
          const l = M.L[idx[at]],
            x = sg.order[l.k],
            s = x && sg.sections[x.sid],
            w = (s && s.lines && s.lines[l.li]) || [];
          return 'on line ' + (at + 1) + (w.length ? ' (“' + w.slice(0, 5).join(' ') + (w.length > 5 ? '…' : '') + '”)' : '');
        }
      }
    } catch (e) {}
    return 'around ' + t.toFixed(1) + ' s';
  }
  // Notes of the line: one button per held note of the trill (the hum or the vowels if there's no trill)
  function lineNotes(L) {
    const id = ['trill', 'hum', 'vowels'].find((r) => L.sung[r]),
      a = id && PITCH.got(L.sung[id].id);
    // Q39: once the song has a key, each note is the nearer note of its scale
    const k = SONGKEY.of(cur() && cur().sg);
    return a ? { from: id, ms: PITCH.held(a).map((h) => (k ? SONGKEY.snap(h.m, k) : Math.round(h.m))).slice(0, 24), k } : null;
  }
  function notesBlock(L) {
    const N = lineNotes(L);
    let h = '<div class="ladsec"><div class="ladhd">Notes of the line</div>';
    if (!N) return h + '<div class="apchart wait" aria-busy="true"><span>Reading the notes…</span></div></div>';
    if (!N.ms.length) return h + '<p class="ladspot">No held notes in your ' + RUN_WORD[N.from] + ' to play.</p></div>';
    const tn = PAT.toneState(),
      nm = (m) => (N.k ? SONGKEY.nameIn(m, N.k) : PITCH.name(m));
    return (
      h +
      '<div class="ladnotes" data-edge-fade data-own-gesture><button class="ladrpt' +
      (U.apRpt ? ' on' : '') +
      '" data-a="apRpt" aria-pressed="' +
      !!U.apRpt +
      '">' +
      ICON_RPT +
      'Repeat</button>' +
      N.ms
        .map(
          (m, i) =>
            '<button class="ladnote' +
            (tn && U.apTone === i ? ' on' : '') +
            '" data-a="apNote" data-v="' +
            i +
            '" aria-label="Play ' +
            nm(m) +
            '">' +
            nm(m) +
            '</button>'
        )
        .join('') +
      '</div><p class="foot">From your ' +
      RUN_WORD[N.from] +
      (N.k ? ', matched to ' + SONGKEY.label(N.k) : '') +
      '. Tap a note to hear it. With Repeat on, it keeps playing until you tap it again.</p></div>'
    );
  }
  const ICON_RPT =
    '<svg class="i" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11V9a4 4 0 0 1 4-4h12l-3-3M20 13v2a4 4 0 0 1-4 4H4l3 3"/></svg>';
  // pitch lines are read when the card needs them; the card is drawn again once they're in (never while recording)
  let needT = 0;
  function need(ids) {
    ids.forEach((id) => {
      if (PITCH.got(id)) return;
      PITCH.ofTake(id).then((a) => {
        if (!a || needT) return;
        needT = setTimeout(() => {
          needT = 0;
          if (X && U.view === 'app' && !rec && !U.sheet && q('#app .lad')) rerender();
        }, 30);
      });
    });
  }
  // the note buttons and Repeat, changed in place
  function paintNotes() {
    const tn = PAT.toneState();
    document.querySelectorAll('#app .ladnote').forEach((b) => {
      const on = !!tn && U.apTone === +b.dataset.v;
      b.classList.toggle('on', on);
    });
    const r = q('#app .ladrpt');
    if (r) {
      r.classList.toggle('on', !!U.apRpt);
      r.setAttribute('aria-pressed', !!U.apRpt);
    }
  }
  function note(i) {
    const c = cur(),
      N = c && lineNotes(ladState(c));
    if (!N || !N.ms.length || !(i >= 0 && i < N.ms.length) || rec) return;
    if (U.apTone === i && PAT.toneState()) {
      PAT.toneStop();
      return paintNotes();
    }
    stopHear();
    if (playingId) stopPlayback();
    const ok = PAT.tone(N.ms[i], {
      repeat: !!U.apRpt,
      onEnd: () => {
        if (U.apTone === i) U.apTone = null;
        paintNotes();
      },
    });
    U.apTone = ok ? i : null;
    paintNotes();
  }
  // Hear both: the trill (or hum) at the parting spot, then the words (or vowels), as takes through NOW
  let hearing = null;
  function stopHear() {
    if (!hearing) return;
    clearTimeout(hearing.timer);
    hearing = null;
  }
  function hear() {
    const c = cur();
    if (!c || rec) return;
    const L = ladState(c),
      sp = spot(c, L);
    if (!sp || sp.none) return;
    stopHear();
    const A = L.sung[L.base],
      B = L.sung[L.target],
      st = (t) => Math.max(0, PITCH.got(t.id).firstT + sp.at - 0.5),
      len = sp.len + 1,
      me = (hearing = {});
    const clip = (t, then) => {
      playTake(t.id, st(t));
      const p = player;
      if (!p) return;
      const go = () => {
        clearTimeout(me.timer);
        me.timer = setTimeout(() => {
          if (hearing !== me || player !== p) return;
          stopPlayback();
          rerender();
          if (then) me.timer = setTimeout(() => hearing === me && then(), 350);
          else hearing = null;
        }, len * 1000);
      };
      p.addEventListener('playing', go, { once: true });
    };
    clip(A, () => clip(B));
  }
  // the live line while a rung records: the recording's own microphone, read on the frame clock (PITCH.live). Its
  // box is found once, and again only once it's been drawn again
  const LIVE = { w: 340, h: 130 };
  function liveSVG(pts, col, rg, dur, lanes) {
    rg = rg || { lo: 52, hi: 67 };
    return PITCH.svg([{ a: pts, col, w: 2.5 }], { w: LIVE.w, h: LIVE.h, lo: rg.lo, hi: rg.hi, dur: dur || 6, label: 'Live pitch line', lanes });
  }
  function liveLine(r) {
    const an = r.mic && r.mic.analyser(PITCH.SET.win),
      ru = rungOf(r.rung);
    if (!an || !ru) return;
    let box = null,
      last = 0;
    const rg = { lo: 52, hi: 67 },
      lanes = SONGKEY.lanesFor(songById(r.songId)); // Q39 the song key's scale lanes, as on Lines
    r.livePts = 0;
    r.lineOff = PITCH.live(an, (pts, p) => {
      if (rec !== r || r.stopping) return r.lineOff && r.lineOff();
      if (!p) return;
      r.livePts = pts.length;
      const now = performance.now();
      if (now - last < 50) return; // about 20 times a second is plenty for a line
      last = now;
      if (!box || !box.isConnected) box = document.getElementById('apLive');
      if (!box) return;
      if (p.m < rg.lo + 1) rg.lo = Math.floor(p.m) - 2;
      if (p.m > rg.hi - 1) rg.hi = Math.ceil(p.m) + 2;
      box.innerHTML = liveSVG(pts, ru.col, rg, Math.max(6, Math.ceil(p.t)), lanes);
    });
  }

  /* ----- singing ----- */
  const overOn = () => sgp().singOver !== false;
  // where the section starts on the track (Song Clock's timing), else the start
  function startAt(sg, o) {
    if (!o || !hasLyrics(sg) || !ckSynced(sg)) return 0;
    const M = ckModel(sg),
      i = ckFirst(M.L, occIdx(sg, o));
    return i >= 0 && M.T[i] && M.T[i][0] != null ? Math.max(0, +M.T[i][0]) : 0;
  }
  function sing() {
    if (!X || isSong() || rec || recBusy) return;
    const c = cur();
    if (!c) return;
    stopPlayback();
    c.st = 'open';
    keep(c);
    U.apSec = false;
    saveDraft();
    const tg = { songId: c.sg.id, o: c.o, app: true };
    if (ladderOn(c.sg)) {
      // Q37: the ladder sings its current rung
      const r = ladState(c).cur;
      if (!r) return;
      tg.rung = r.id;
    }
    if (overOn() && TRACK.has(c.sg.id)) {
      if (REC_OVER.hp) return over(tg, 'hp');
      return askOver(Object.assign(tg, { sing: true })); // Q16's sheet: headphones, or the speaker
    }
    startRec(tg);
  }
  // Sing over the track: the track from just before the section, then the recording over it. Started in the tap, so
  // iPhone lets the track play and wakes the microphone's sound engine
  async function over(tg, mode) {
    if (rec || recBusy) return;
    AUDIO.wake();
    const sg = songById(tg.songId);
    if (!sg) return;
    const from = Math.max(0, startAt(sg, tg.o) - LEAD);
    const ok = await TRACK.playFrom(sg.id, from);
    if (!X || rec || U.view !== 'app') {
      if (ok) quietPause();
      return AUDIO.rest();
    }
    if (ok && mode === 'hp' && !REC_OVER.hp) hpSaid();
    if (ok && mode === 'spk') toast('The track may be heard in your take');
    startRec(Object.assign({}, tg, { from: ok ? from : null }), ok ? mode : null);
  }
  // the app's own pause of the track (a take ended, or a take is about to play): headphones stay remembered
  function quietPause() {
    if (!TRACK.state().playing) return;
    REC_OVER.mine = Date.now();
    TRACK.pause();
  }
  // a take just saved here: its row arrives
  function arrived(id) {
    const r = q('#app .tkrow[data-tk="' + id + '"]');
    if (r) MOTION.animate(r, [{ opacity: 0, transform: 'translateY(-8px) scale(.98)' }, { opacity: 1, transform: 'none' }], { spring: 'gentle', fade: true });
  }

  /* ----- Done, and "Practised, not recorded": the card folds to one line ----- */
  function done(norec) {
    const c = cur();
    if (!c || rec) return;
    stopPlayback();
    timers.forEach(clearTimeout);
    timers.length = 0;
    if (norec) X.song = c.sg.id;
    const fin = () => {
      const c2 = cur();
      if (!c2 || !X) return;
      c2.st = norec ? 'norec' : 'done';
      keep(c2);
      U.apSec = false;
      saveDraft();
      rerender();
      const l = q('#apcard');
      if (l) MOTION.animate(l, [{ opacity: 0.4, transform: 'scale(.98)' }, { opacity: 1, transform: 'none' }], { spring: 'gentle', fade: true });
      OP.dockUpd();
    };
    const sw = q('#apcard .apsweep');
    if (norec || !sw || MOTION.speed() === 0) return fin();
    if (!MOTION.on()) {
      // Reduce Motion: a green flash, no sweep
      sw.animate(
        [
          { opacity: 0, background: 'var(--rg-green)' },
          { opacity: 1, background: 'var(--rg-green)', offset: 0.3 },
          { opacity: 0, background: 'var(--rg-green)' },
        ],
        { duration: 600, easing: 'ease-out' }
      );
      return later(fin, 450);
    }
    const G = MOTION.dur('gentle') / Math.max(1, MOTION.speed()),
      B = 'var(--rg-blue)';
    MOTION.animate(sw, [{ opacity: 1, transform: 'scaleX(0)', background: B }, { opacity: 1, transform: 'scaleX(1)', background: B }], {
      spring: 'gentle',
      fill: 'forwards',
    });
    later(() => {
      sw.getAnimations().forEach((a) => a.cancel());
      MOTION.animate(
        sw,
        [
          { opacity: 1, background: B },
          { opacity: 1, background: 'var(--rg-green-s)', offset: 0.3 },
          { opacity: 1, background: 'var(--rg-green)' },
        ],
        { ms: 650, easing: 'ease-out', fill: 'forwards' }
      );
    }, G * 0.62);
    later(fin, G * 0.62 + 700);
  }

  /* ----- the actions (data-a="ap…") ----- */
  function pick(id) {
    if (rec) return toast('Stop recording first');
    const sg = songById(id);
    if (!sg || !X) return;
    stopPlayback();
    // a song marked practised and then reopened, without a take, isn't the session's song any more
    if (X.song && X.song !== id && !(X.takes || []).some((k) => (TAKES.find((t) => t.id === k) || {}).songId === X.song)) X.song = null;
    X.sing = { id, o: lastSec(id), st: 'open' };
    U.apSec = false;
    U.apFold = false; // Q37: the ladder's fold and lines start afresh for another song
    U.apLn = null;
    saveDraft();
    rerender();
    const c = q('#apcard');
    if (c) {
      const r = c.getBoundingClientRect();
      if (r.top < 80 || r.top > window.innerHeight * 0.5)
        window.scrollTo({ top: Math.max(0, window.scrollY + r.top - 100), behavior: MOTION.on() ? 'smooth' : 'auto' });
      MOTION.animate(c, [{ opacity: 0, transform: 'translateY(10px)' }, { opacity: 1, transform: 'none' }], { spring: 'gentle', fade: true });
    }
  }
  function cmp(el) {
    const id = el.dataset.k,
      list = [...document.querySelectorAll('#app .apcmp [data-a=apCmp]')].map((b) => b.dataset.k);
    if (!id || !TAKES.some((t) => t.id === id)) return;
    // from the same moment as the other take, if it's playing; tapping the one that plays stops it
    if (takePlaying(id)) {
      stopPlayback();
      return paint();
    }
    const at = player && list.includes(playingId) && playingId !== id ? player.currentTime || 0 : 0;
    segPick(el);
    playTake(id, at); // stops the other one first: one sound at a time
  }
  // a take playing or stopping, without redrawing the page (so Compare's knob slides)
  const inPlace = () => !U.sheet && !!q('#app .tkrow');
  function paint() {
    document.querySelectorAll('#app .tkrow').forEach((r) => {
      const id = r.dataset.tk,
        on = takePlaying(id),
        b = r.querySelector('.tkplay'),
        pg = r.querySelector('.tkpg');
      if (r.classList.contains('playing') !== on) {
        r.classList.toggle('playing', on);
        b.innerHTML = on ? ICON.pause : ICON.play;
        b.setAttribute('aria-label', b.getAttribute('aria-label').replace(/^(Play|Pause) /, on ? 'Pause ' : 'Play '));
      }
      if (!on && pg && playingId !== id) pg.style.width = '0';
    });
    const c = q('#app .apcmp');
    if (c) {
      const sel = [...c.querySelectorAll('button')].find((b) => b.dataset.k === playingId);
      if (sel && !sel.classList.contains('on')) segPick(sel);
    }
    fwUpdate();
  }
  function sortMenu(btn) {
    OP.sortMenu(btn, SORTS, U.apSort || 'recent', 'apSortPick');
  }
  function sortPick(v) {
    OP.closeMenu();
    if (!SORTS.some((o) => o[0] === v) || v === (U.apSort || 'recent')) return;
    const before = {};
    document.querySelectorAll('#app .apsongs .row').forEach((el) => (before[el.dataset.k] = el.getBoundingClientRect().top));
    U.apSort = v;
    rerender();
    document.querySelectorAll('#app .apsongs .row').forEach((el) => {
      const b = before[el.dataset.k];
      if (b === undefined) return;
      const dy = b - el.getBoundingClientRect().top;
      if (Math.abs(dy) > 1) MOTION.animate(el, [{ transform: 'translateY(' + dy.toFixed(1) + 'px)' }, { transform: 'none' }], { spring: 'nav' });
    });
  }
  Object.assign(SG_ACT, {
    apSing: () => sing(),
    apStop: () => rec && stopRec(),
    apDone: () => done(false),
    apNoRec: () => done(true),
    apReopen() {
      const c = cur();
      if (!c || rec) return;
      c.st = 'open';
      keep(c);
      saveDraft();
      rerender();
      OP.dockUpd();
    },
    apSong: (el, v, k) => pick(k),
    apSecs() {
      U.apSec = !U.apSec;
      rerender();
      const p = q('#app .appills');
      if (p) MOTION.animate(p, [{ opacity: 0, transform: 'translateY(-6px)' }, { opacity: 1, transform: 'none' }], { spring: 'gentle', fade: true });
    },
    apSec(el, v) {
      const c = cur();
      if (!c || rec) return;
      stopPlayback();
      c.o = okO(c.sg, v || null);
      c.skip = []; // Q37: a new place starts the ladder afresh
      keep(c);
      U.apSec = false;
      saveDraft();
      rerender();
    },
    apOver(el) {
      const p = sgp();
      p.singOver = !overOn();
      saveSGP();
      const on = overOn();
      el.setAttribute('aria-checked', on);
      const t = el.querySelector('.tgl');
      if (t) t.setAttribute('aria-checked', on);
    },
    apCmp: (el) => cmp(el),
    apSort: (el) => sortMenu(el),
    apSortPick: (el, v) => sortPick(v),
    // Q37 the song ladder
    apMode(el, v) {
      const c = cur();
      if (!c || rec) return;
      const on = v === 'ladder';
      if (on === ladderOn(c.sg)) return;
      stopPlayback();
      stopHear();
      PAT.toneStop();
      const e = Object.assign({}, c.sg.ext);
      if (on) e.ladder = true;
      else delete e.ladder;
      if (Object.keys(e).length) c.sg.ext = e;
      else delete c.sg.ext;
      save(); // the song remembers it (backed up with the song)
      segPick(el);
      rerender();
      const l = q('#apcard .lad');
      if (l) MOTION.animate(l, [{ opacity: 0, transform: 'translateY(-6px)' }, { opacity: 1, transform: 'none' }], { spring: 'gentle', fade: true });
    },
    apLadFold() {
      U.apFold = !U.apFold;
      rerender();
      const r = q('#app .ladrows');
      if (r)
        r.querySelectorAll('.ladrow').forEach((x, i) =>
          MOTION.animate(x, [{ opacity: 0, transform: 'translateY(-6px)' }, { opacity: 1, transform: 'none' }], {
            spring: 'gentle',
            delay: MOTION.stagger(i, 'row'),
            fade: true,
          })
        );
    },
    apSkip() {
      const c = cur();
      if (!c || rec) return;
      const L = ladState(c);
      if (!L.cur) return;
      c.skip = (c.skip || []).concat(L.cur.id);
      keep(c);
      saveDraft();
      rerender();
    },
    apLadAgain() {
      const c = cur();
      if (!c || rec) return;
      c.skip = [];
      keep(c);
      saveDraft();
      rerender();
    },
    apLine(el, v) {
      const c = cur();
      if (!c || !rungOf(v)) return;
      const L = ladState(c);
      U.apLn = Object.assign({}, U.apLn, { [v]: !lnOn(L, v) });
      rerender();
    },
    apHear: () => hear(),
    apNote: (el, v) => note(+v),
    apRpt() {
      U.apRpt = !U.apRpt;
      if (!U.apRpt && PAT.toneState() && PAT.toneState().repeat) PAT.toneStop();
      paintNotes();
    },
  });

  // after every redraw (render() in ui.js): the page dims around the card while it records
  function after() {
    const on = !!(rec && rec.app && X && U.view === 'app');
    document.body.classList.toggle('apprec', on);
    // Q37: the ladder's notes and Hear both stop once Application isn't on screen
    if (U.view !== 'app' || !X) {
      if (PAT.toneState() && U.apTone != null) PAT.toneStop();
      U.apTone = null;
      stopHear();
    }
    SONGKEY.after(); // Q39: a suggested pattern playing stops when its row goes
  }
  // the pinned button's empty state: nothing sung yet
  const empty = () => {
    if (!X || isSong()) return true;
    if (X.song) return false;
    const c = cur();
    return !(c && c.st !== 'open');
  };

  return {
    body,
    wave,
    waved,
    cmpHTML,
    over,
    quietPause,
    arrived,
    inPlace,
    paint,
    after,
    empty,
    secName,
    startAt,
    liveLine,
    // tests
    state: () => {
      const c = cur();
      if (!c) return null;
      const out = { id: c.sg.id, o: c.o, st: c.st, carry: !!c.carry, over: overOn(), ladder: ladderOn(c.sg) };
      if (out.ladder) {
        const L = ladState(c),
          sp = spot(c, L),
          N = L.list.length === 4 ? lineNotes(L) : null;
        Object.assign(out, {
          sung: L.list.map((r) => r.id),
          takes: L.list.map((r) => L.sung[r.id].id),
          skip: L.skip,
          cur: L.cur ? L.cur.id : null,
          later: L.later.map((r) => r.id),
          spot: sp ? (sp.none ? 'none' : { at: sp.at, len: sp.len, t: sp.t, where: sp.where }) : null,
          notes: N ? N.ms : null,
          hearing: !!hearing,
          tone: U.apTone,
        });
      }
      return out;
    },
  };
})();
