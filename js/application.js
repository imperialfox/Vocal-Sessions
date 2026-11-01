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
    if (sg) return { sg, o: okO(sg, s.o), st: s.st === 'done' || s.st === 'norec' ? s.st : 'open' };
    const sp = songById(X.song);
    if (sp) return { sg: sp, o: null, st: 'open' };
    const c = carryOn();
    return c ? { sg: songById(c.id), o: c.o, st: 'open', carry: true } : null;
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
    X.sing = { id: c.sg.id, o: c.o, st: c.st };
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
    if (c && !recNow && X.song)
      h +=
        '<div class="hdr">Rate the song</div><div class="grp">' +
        ['Pitch', 'Tone', 'Ease']
          .map((k) => '<div class="row"><span class="lbl">' + k + '</span>' + seg('rate', k, X.rate[k]) + '</div>')
          .join('') +
        '</div>';
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
        line =
          songTitle(sg) +
          (c.o ? ' · ' + secName(sg, c.o) : '') +
          (c.st === 'norec'
            ? ' · practised, not recorded'
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
      words = sg ? lyricsOf(sg, o) : '';
    return (
      '<div class="apcard rec" id="apcard" role="group" aria-label="Recording"><div class="aphead"><span class="lbl"><b class="apname">' +
      esc(sg ? secName(sg, o) : 'Recording') +
      '</b><small><span class="recdot" aria-hidden="true"></span>Recording' +
      (rec.over && rec.from != null ? ' · track from ' + mmss(rec.from) : '') +
      '</small></span><span class="aptime" id="recT">' +
      mmss(rec.t) +
      '</span></div><span class="meter apmeter" id="recMeter" aria-hidden="true">' +
      '<i></i>'.repeat(14) +
      '</span>' +
      words +
      '<button class="apstop" data-a="apStop"><span aria-hidden="true"></span>Stop</button></div>'
    );
  }
  // the words to sing: the section's lines, or every section's for Whole song
  function lyricsOf(sg, o) {
    if (!hasLyrics(sg)) return '';
    const line = (l) => '<p>' + esc((l || []).join(' ')) + '</p>';
    if (o) {
      const x = sg.order[occIdx(sg, o)],
        s = x && sg.sections[x.sid];
      return s && s.lines && s.lines.length ? '<div class="aply">' + s.lines.map(line).join('') + '</div>' : '';
    }
    return (
      '<div class="aply">' +
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
  });

  // after every redraw (render() in ui.js): the page dims around the card while it records
  function after() {
    const on = !!(rec && rec.app && X && U.view === 'app');
    document.body.classList.toggle('apprec', on);
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
    // tests
    state: () => {
      const c = cur();
      return c ? { id: c.sg.id, o: c.o, st: c.st, carry: !!c.carry, over: overOn() } : null;
    },
  };
})();
