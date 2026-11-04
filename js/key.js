/* Vocal Sessions · key.js (Q39)
   SONGKEY: a song's key, its scale lanes on pitch lines, and patterns from the library to practise in that key.
   - The key {tonic, mode} is an optional field on the song (sg.ext.key), in backups. It's worked out from the song's
     takes (a 12-note profile of their steady pitch, then Krumhansl–Schmuckler, musictheoryjs's detectKey in
     js/musictheory.js) and chosen once: asked when the top two are close, suggested otherwise. The key sheet (VS-098)
     sets or changes it.
   - Scale lanes: the key's notes as faint lanes on PITCH.svg, the home note in the accent, spelled by tonal
     (js/tonal.js: B♭4, not A♯4). Descriptive only: nothing is coloured right or wrong. Switched on Lines (this device).
   - Practise in <key>: the note to work on (where the words part from the trill, else the line's top note), then up to
     three LIB patterns in the key that reach it, each with Play and a door into the pattern player (VS-097), which
     opens on that pattern and note, staying on this key, without touching any exercise's saved choices.
   See MAINTAINING › Key and scale lanes. */
const SONGKEY = (() => {
  const q = (sel) => document.querySelector(sel);
  const MAJ = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'],
    MIN = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B'],
    MODES = ['major', 'minor'],
    SET = { steady: 0.25, close: 0.15, enough: 150, floor: 45, most: 3 },
    DEG = ['home note', '2nd', '3rd', '4th', '5th', '6th', '7th'],
    pc = (m) => ((Math.round(m) % 12) + 12) % 12,
    glyph = (s) => String(s).replace(/#/g, '♯').replace(/b/g, '♭'),
    has = () => typeof Tonal === 'object' && typeof MusicTheory === 'object' && typeof MusicTheory.detectKey === 'function';
  const names = (mode) => (mode === 'minor' ? MIN : MAJ);
  // a key as saved: {tonic, mode}, the tonic spelled as on the key sheet; anything else is null
  function valid(k) {
    return !!k && typeof k === 'object' && MODES.includes(k.mode) && names(k.mode).includes(k.tonic);
  }
  const tonicPc = (k) => names(k.mode).indexOf(k.tonic);
  const label = (k) => (valid(k) ? glyph(k.tonic) + ' ' + k.mode : '');
  const of = (sg) => (sg && sg.ext && valid(sg.ext.key) ? sg.ext.key : null);
  function set(sg, k) {
    if (!sg) return;
    if (k && valid(k)) {
      sg.ext = Object.assign({}, sg.ext || {}, { key: { tonic: k.tonic, mode: k.mode } });
    } else if (sg.ext) {
      delete sg.ext.key;
      if (!Object.keys(sg.ext).length) delete sg.ext;
    }
    save();
  }
  // cleanSong(): a key that isn't one of the 24 is dropped; other fields in ext are kept
  function clean(ext) {
    if (ext && 'key' in ext && !valid(ext.key)) delete ext.key;
    else if (ext && ext.key) ext.key = Object.assign({}, ext.key);
  }

  /* ----- spelling ----- */
  const scaleCache = new Map();
  // the key's seven notes as tonal spells them ('F G A Bb C D E'), each with its pitch class
  function scale(k) {
    const id = k.tonic + ' ' + k.mode;
    if (scaleCache.has(id)) return scaleCache.get(id);
    let ns = [];
    try {
      ns = Tonal.Scale.get(id).notes || [];
    } catch (e) {}
    const out = ns.map((n) => ({ n, pc: Tonal.Note.chroma(n) }));
    scaleCache.set(id, out);
    return out;
  }
  const pcs = (k) => new Set(scale(k).map((x) => x.pc));
  // a MIDI note spelled in the key (B♭4 in F major), or by pitch class off the scale
  function nameIn(m, k) {
    m = Math.round(m);
    const s = k && scale(k).find((x) => x.pc === pc(m));
    if (s) {
      const base = Math.floor(m / 12) - 1;
      for (const o of [base, base + 1, base - 1]) if (Tonal.Note.midi(s.n + o) === m) return glyph(s.n) + o;
    }
    return PITCH.name(m);
  }
  // the nearer note of the scale (a tie goes down)
  function snap(m, k) {
    if (!k || !isFinite(m)) return Math.round(m);
    const S = pcs(k);
    let best = Math.round(m),
      d = 99;
    for (let x = Math.floor(m) - 2; x <= Math.ceil(m) + 2; x++)
      if (S.has(pc(x)) && Math.abs(x - m) < d - 1e-9) {
        d = Math.abs(x - m);
        best = x;
      }
    return best;
  }
  const degree = (m, k) => {
    const i = scale(k).findIndex((x) => x.pc === pc(m));
    return i < 0 ? '' : DEG[i];
  };
  // the lanes for a chart from lo to hi: [{m, name, home}]
  function lanes(k, lo, hi) {
    if (!valid(k) || !has()) return [];
    const S = pcs(k),
      t = tonicPc(k),
      out = [];
    for (let m = Math.ceil(lo); m <= hi; m++) if (S.has(pc(m))) out.push({ m, name: nameIn(m, k), home: pc(m) === t });
    return out;
  }

  /* ----- finding the key ----- */
  // 12 bins: every frame that sits within 0.25 of both its neighbours, counted at its nearest note
  function profile(list) {
    const h = new Array(12).fill(0);
    let n = 0;
    (list || []).forEach((a) => {
      if (!a || !a.s) return;
      const s = a.s;
      for (let i = 1; i < a.n - 1; i++) {
        const v = s[i];
        if (isNaN(v) || isNaN(s[i - 1]) || isNaN(s[i + 1])) continue;
        if (Math.abs(v - s[i - 1]) > SET.steady || Math.abs(v - s[i + 1]) > SET.steady) continue;
        h[pc(v)]++;
        n++;
      }
    });
    return { h, n };
  }
  // the top two keys for a profile, spelled as on the key sheet: [{tonic, mode, score}]
  function find(h) {
    if (!has() || !h || h.every((v) => !v)) return [];
    return MusicTheory.detectKey(h)
      .slice(0, 2)
      .map((e) => ({ tonic: names(e.mode)[e.tonic], mode: e.mode, score: e.score }));
  }
  // what to say: {st: 'ask' | 'suggest' | 'few' | 'none', top, frames}. 'few': not enough steady singing yet
  function verdict(h, n) {
    if (!n) return { st: 'none', top: [], frames: 0 };
    if (n < SET.enough) return { st: 'few', top: [], frames: n };
    const top = find(h);
    if (!top.length) return { st: 'few', top: [], frames: n };
    return { st: top.length > 1 && top[0].score - top[1].score <= SET.close ? 'ask' : 'suggest', top, frames: n };
  }
  // every take of the song, read one at a time through PITCH (lines stay in memory), then the verdict; kept per song
  // until its takes change
  const found = new Map();
  function detect(id) {
    const ts = (typeof TAKES !== 'undefined' ? TAKES : []).filter((t) => t.songId === id),
      sig = ts.map((t) => t.id).join(','),
      f = found.get(id);
    if (f && f.sig === sig) return f;
    const me = { sig, st: 'reading', done: 0, of: ts.length, top: [] };
    found.set(id, me);
    if (!ts.length) return Object.assign(me, verdict(null, 0));
    (async () => {
      const lines = [];
      for (const t of ts) {
        const a = await PITCH.ofTake(t.id);
        if (a) lines.push(a);
        me.done++;
      }
      if (found.get(id) !== me) return;
      const p = profile(lines);
      Object.assign(me, verdict(p.h, p.n));
      redraw();
    })();
    return me;
  }
  let drawT = 0;
  function redraw() {
    clearTimeout(drawT);
    drawT = setTimeout(() => {
      if ((U.view === 'app' && !rec && q('#app .keyblk')) || U.sheet === 'keyPick') rerender();
    }, 30);
  }

  /* ----- this device: Scale lanes on or off (localStorage vocalLook.lanes) ----- */
  function look() {
    try {
      const o = JSON.parse(localStorage.getItem('vocalLook') || '{}');
      return o && typeof o === 'object' && !Array.isArray(o) ? o : {};
    } catch (e) {
      return {};
    }
  }
  const lanesOn = () => look().lanes !== false;
  function setLanes(on) {
    const o = look();
    if (on) delete o.lanes;
    else o.lanes = false;
    try {
      localStorage.setItem('vocalLook', JSON.stringify(o));
    } catch (e) {}
  }
  // what PITCH.svg draws for a song: a function of the chart's range, or null
  const lanesFor = (sg) => {
    const k = of(sg);
    return k && lanesOn() && has() ? (lo, hi) => lanes(k, lo, hi) : null;
  };

  /* ----- suggestions ----- */
  const lo = (p) => Math.min(...p.semi.filter((v) => v !== null)),
    hi = (p) => Math.max(...p.semi.filter((v) => v !== null));
  // every note of p, played from the key note kn, in the key and none below A2
  const fits = (p, kn, S) => kn + lo(p) >= SET.floor && p.semi.every((s) => s === null || S.has(pc(kn + s)));
  // up to three patterns that play in the key and peak on the target: one per group (riffs, flips, warm-ups) where
  // possible, then the rest in library order. If none peaks on it, patterns that pass through it instead.
  // [{p, kn, lo, hi, exact}]
  function suggest(k, target) {
    if (!valid(k) || !isFinite(target)) return [];
    const S = pcs(k),
      t = tonicPc(k),
      lib = PAT.LIB.filter((p) => p.semi.some((v) => v !== null)),
      row = (p, kn, exact) => ({ p, kn, lo: kn + lo(p), hi: kn + hi(p), exact });
    let pool = lib
      .map((p) => {
        const kn = target - hi(p);
        return pc(kn) === t && fits(p, kn, S) ? row(p, kn, true) : null;
      })
      .filter(Boolean);
    if (!pool.length)
      pool = lib
        .map((p) => {
          // the highest of its notes that can sit on the target
          const steps = [...new Set(p.semi.filter((v) => v !== null))].sort((a, b) => b - a);
          for (const s of steps) {
            const kn = target - s;
            if (pc(kn) === t && fits(p, kn, S)) return row(p, kn, false);
          }
          return null;
        })
        .filter(Boolean);
    const out = [];
    ['r', 'x', 'w'].forEach((g) => {
      const x = pool.find((r) => r.p.g === g);
      if (x && out.length < SET.most) out.push(x);
    });
    pool.forEach((r) => {
      if (out.length < SET.most && !out.includes(r)) out.push(r);
    });
    return out;
  }

  /* ----- Lines: the song key, then Practise in <key> ----- */
  // the note to work on: the held note of the trill (else the hum) at the parting spot, else the line's top note
  function target(a, sp, k) {
    if (!a) return null;
    const H = PITCH.held(a);
    if (sp && sp.at != null && H.length) {
      const at = sp.at;
      let h = H.find((x) => x.t <= at && at <= x.t + x.d);
      if (!h) {
        const near = H.map((x) => ({ x, d: Math.min(Math.abs(x.t - at), Math.abs(x.t + x.d - at)) })).sort((u, v) => u.d - v.d)[0];
        if (near && near.d <= 0.5) h = near.x;
      }
      if (h) return { m: snap(h.m, k), at: true };
    }
    const top = H.length ? Math.max(...H.map((x) => x.m)) : a.hi;
    return isFinite(top) ? { m: snap(top, k), at: false } : null;
  }
  const IC_PLAY = ICON.play,
    IC_STOP =
      '<svg class="i" viewBox="0 0 24 24"><rect x="6.5" y="6.5" width="11" height="11" rx="2" fill="currentColor" stroke="none"/></svg>';
  let shown = []; // the rows on screen, for Play and ›: [{p, kn, ...}]
  let ctx = null; // {id: the song, k: the key, m: the target}
  // c: Application's place ({sg, o}); a: the trill's (or hum's) line; sp: the parting spot (or {none}), where: its name
  function block(c, a, sp) {
    const sg = c.sg,
      k = of(sg);
    if (!has()) return '';
    let h = '<div class="ladsec keyblk"><div class="ladhd">Song key</div>';
    if (k) {
      h +=
        '<div class="keyrow"><span class="lbl">' +
        esc(label(k)) +
        '</span><button class="apsoft" data-a="keyChange" data-k="' +
        sg.id +
        '">Change</button></div></div>';
      return h + practise(c, a, sp, k);
    }
    const f = detect(sg.id);
    const foot = '<p class="foot">From your takes. You only choose once for each song.</p>';
    if (f.st === 'reading')
      return h + '<div class="apchart wait" aria-busy="true"><span>Listening for the key…</span></div></div>';
    if (f.st === 'ask')
      return (
        h +
        '<div class="keyq"><p>Which key is this song in?</p></div><div class="keyopts">' +
        f.top
          .map(
            (x, i) =>
              '<button class="apsoft" data-a="keyUse" data-k="' + sg.id + '" data-v="' + i + '">' + esc(label(x)) + '</button>'
          )
          .join('') +
        '<button class="apsoft" data-a="keyChange" data-k="' +
        sg.id +
        '">Other…</button></div>' +
        foot +
        '</div>'
      );
    if (f.st === 'suggest')
      return (
        h +
        '<div class="keyq"><p>This sounds like ' +
        esc(label(f.top[0])) +
        '</p></div><div class="keyopts"><button class="apsoft keyuse" data-a="keyUse" data-k="' +
        sg.id +
        '" data-v="0">Use</button><button class="apsoft" data-a="keyChange" data-k="' +
        sg.id +
        '">Other…</button></div>' +
        foot +
        '</div>'
      );
    return (
      h +
      '<div class="keyq"><p>Not enough singing yet to hear the key.<small>Sing a little more of the song, or choose its key.</small></p></div>' +
      '<div class="keyopts"><button class="apsoft" data-a="keyChange" data-k="' +
      sg.id +
      '">Choose…</button></div></div>'
    );
  }
  function practise(c, a, sp, k) {
    const T = target(a, sp, k);
    let h = '<div class="ladsec keyprac"><div class="ladhd">Practise in ' + esc(label(k)) + '</div>';
    if (!T) {
      shown = [];
      return h + '<div class="apchart wait" aria-busy="true"><span>Reading the notes…</span></div></div>';
    }
    const where = T.at && sp && sp.where ? 'Where the words part (' + sp.where + ')' : 'The line’s top note';
    const deg = degree(T.m, k);
    ctx = { id: c.sg.id, k, m: T.m };
    shown = suggest(k, T.m);
    h +=
      '<p class="keytgt">' +
      esc(where) +
      ' sits on <b>' +
      nameIn(T.m, k) +
      '</b>' +
      (deg ? ', the ' + deg + ' of ' + esc(label(k)) : '') +
      '.</p>';
    if (!shown.length) return h + '<p class="foot">No pattern in the library reaches it in this key.</p></div>';
    const pv = PAT.state().preview;
    h +=
      '<div class="keypats">' +
      shown
        .map((r, i) => {
          const on = pv === r.p.n && hearing === i,
            nm = r.p.name.replace(/&amp;/g, '&');
          return (
            '<div class="keypat" data-n="' +
            r.p.n +
            '"><button class="tkplay" data-a="keyHear" data-v="' +
            i +
            '" aria-label="' +
            (on ? 'Stop ' : 'Play ') +
            esc(nm) +
            '">' +
            (on ? IC_STOP : IC_PLAY) +
            '</button><button class="keygo" data-a="keyGo" data-v="' +
            i +
            '" data-zk="keyp" data-push aria-label="Practise ' +
            esc(nm) +
            ' in ' +
            esc(label(k)) +
            '"><span class="lbl">' +
            r.p.name +
            ' · ' +
            nameIn(r.lo, k) +
            '–' +
            nameIn(r.hi, k) +
            '<small>' +
            r.p.line +
            '</small></span>' +
            chev +
            '</button></div>'
          );
        })
        .join('') +
      '</div><p class="foot">' +
      (shown[0].exact
        ? 'Each plays in ' + esc(label(k)) + ' and peaks on ' + nameIn(T.m, k) + '.'
        : 'None peaks on ' + nameIn(T.m, k) + ' in this key, so these pass through it.') +
      '</p></div>';
    return h;
  }
  // Play: the pattern once in the key, in the pattern player's sound; again stops it
  let hearing = null;
  function hear(i) {
    const r = shown[i];
    if (!r) return;
    if (hearing === i && PAT.state().preview === r.p.n) {
      PAT.hearStop();
      hearing = null;
      return paintRows();
    }
    if (typeof stopPlayback === 'function' && typeof playingId !== 'undefined' && playingId) stopPlayback();
    hearing = i;
    PAT.hear(r.p.n, r.kn, () => {
      if (hearing === i) hearing = null;
      paintRows();
    });
    paintRows();
  }
  function paintRows() {
    const pv = PAT.state().preview;
    document.querySelectorAll('#app .keypat [data-a="keyHear"]').forEach((b) => {
      const i = +b.dataset.v,
        r = shown[i],
        on = !!r && pv === r.p.n && hearing === i;
      b.innerHTML = on ? IC_STOP : IC_PLAY;
      b.setAttribute('aria-label', (on ? 'Stop ' : 'Play ') + (r ? r.p.name.replace(/&amp;/g, '&') : ''));
    });
  }
  // ›: the pattern player on its own page, on that pattern and note, staying on this key
  function goTo(i) {
    const r = shown[i];
    if (!r || !ctx) return;
    const sg = songById(ctx.id);
    if (!sg) return;
    hearing = null;
    const from = U.view;
    PAT.guest({ id: sg.id, name: sg.name, n: r.p.n, k: r.kn, key: label(ctx.k) });
    go(() => {
      U.keypFrom = from;
      U.keyp = { id: sg.id, k: ctx.k, m: ctx.m };
      U.view = 'keyp';
    });
  }
  function back() {
    go(() => {
      U.view = U.keypFrom || null;
      U.keypFrom = null;
    });
  }
  // VS-097 Practise in <key>
  function page() {
    const P = U.keyp,
      sg = P && songById(P.id);
    if (!sg || !valid(P.k)) return '<h1>Practise</h1>';
    const deg = degree(P.m, P.k);
    return (
      '<h1>Practise in ' +
      esc(label(P.k)) +
      '</h1><p class="sgsub keysub">' +
      esc(sg.name) +
      ' · ' +
      nameIn(P.m, P.k) +
      (deg ? ', the ' + deg : '') +
      '</p>' +
      PAT.card() +
      '<p class="foot">It stays on this key until you switch off Stay on this key. Your exercises’ own choices aren’t changed.</p>'
    );
  }
  const title = () => (U.keyp && valid(U.keyp.k) ? 'Practise in ' + label(U.keyp.k) : 'Practise');

  /* ----- VS-098 the key sheet ----- */
  function open(id) {
    const sg = songById(id);
    if (!sg) return;
    const k = of(sg),
      f = !k && found.get(id),
      pre = k || (f && f.top && f.top[0]) || { tonic: 'C', mode: 'major' };
    U.sd = { k: id, tonic: pre.tonic, mode: pre.mode };
    U.sheet = 'keyPick';
    rerender();
  }
  function sheet() {
    const sd = U.sd || {},
      sg = songById(sd.k);
    if (!sg) return '';
    const mode = sd.mode === 'minor' ? 'minor' : 'major',
      ns = names(mode);
    return sheetWrap(
      'Song key',
      '<p class="note">' +
        esc(sg.name) +
        '</p><div class="keymode"><div class="seg wide" role="group" aria-label="Major or minor"><span class="knob" aria-hidden="true"></span>' +
        MODES.map(
          (m) =>
            '<button data-a="keyMode" data-v="' +
            m +
            '" class="' +
            (m === mode ? 'on' : '') +
            '" aria-pressed="' +
            (m === mode) +
            '">' +
            (m === 'major' ? 'Major' : 'Minor') +
            '</button>'
        ).join('') +
        '</div></div><div class="keygrid" role="group" aria-label="Home note">' +
        ns
          .map(
            (n) =>
              '<button class="ladnote' +
              (n === sd.tonic ? ' on' : '') +
              '" data-a="keyNote" data-v="' +
              n +
              '" aria-pressed="' +
              (n === sd.tonic) +
              '">' +
              glyph(n) +
              '</button>'
          )
          .join('') +
        '</div><button class="cta" data-a="keySave">Use ' +
        esc(label({ tonic: ns.includes(sd.tonic) ? sd.tonic : ns[0], mode })) +
        '</button>',
      'Song key'
    );
  }
  function pickMode(v) {
    const sd = U.sd || {};
    if (!MODES.includes(v)) return;
    const i = names(sd.mode === 'minor' ? 'minor' : 'major').indexOf(sd.tonic);
    sd.mode = v;
    sd.tonic = names(v)[i < 0 ? 0 : i]; // the same note, spelled for the other mode (D♭ ↔ C♯)
    rerender();
  }
  function pickNote(v) {
    const sd = U.sd || {};
    if (!names(sd.mode === 'minor' ? 'minor' : 'major').includes(v)) return;
    sd.tonic = v;
    rerender();
  }
  function keep() {
    const sd = U.sd || {},
      sg = songById(sd.k),
      k = { tonic: sd.tonic, mode: sd.mode === 'minor' ? 'minor' : 'major' };
    if (!sg || !valid(k)) return;
    set(sg, k);
    U.sheet = null;
    U.sd = {};
    rerender();
    toast('Song key · ' + label(k));
  }
  function use(id, i) {
    const sg = songById(id),
      f = found.get(id),
      k = f && f.top && f.top[+i];
    if (!sg || !k) return;
    set(sg, k);
    rerender();
    toast('Song key · ' + label(k));
  }

  // the song page's Key row (VS-009 › key-row)
  function row(sg) {
    if (!has()) return '';
    const k = of(sg);
    return (
      '<button class="row" data-a="keyChange" data-k="' +
      sg.id +
      '"><span class="tile" style="--c:var(--accent)" aria-hidden="true">' +
      '<svg class="i" viewBox="0 0 24 24"><path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/></svg>' +
      '</span><span class="lbl">Key<small>' +
      (k ? esc(label(k)) : 'Not set · found from your takes, or choose it') +
      '</small></span>' +
      chev +
      '</button>'
    );
  }

  // leaving Lines: a pattern playing from a row stops
  function after() {
    if (hearing != null && !q('#app .keypat')) {
      if (PAT.state().preview != null) PAT.hearStop();
      hearing = null;
    }
  }

  Object.assign(SG_ACT, {
    keyChange: (el, v, k) => open(k),
    keyUse: (el, v, k) => use(k, v),
    keyMode: (el, v) => pickMode(v),
    keyNote: (el, v) => pickNote(v),
    keySave: () => keep(),
    keyHear: (el, v) => hear(+v),
    keyGo: (el, v) => goTo(+v),
    keyBack: () => back(),
    keyLanes: () => {
      setLanes(!lanesOn());
      rerender();
    },
  });

  return {
    SET,
    MAJ,
    MIN,
    has,
    valid,
    label,
    of,
    set,
    clean,
    scale,
    nameIn,
    snap,
    degree,
    lanes,
    lanesOn,
    setLanes,
    lanesFor,
    profile,
    find,
    verdict,
    detect,
    suggest,
    target,
    block,
    page,
    title,
    sheet,
    open,
    row,
    after,
    // for the tests
    state: () => ({ shown: shown.map((r) => ({ n: r.p.n, kn: r.kn, lo: r.lo, hi: r.hi, exact: r.exact })), ctx, hearing }),
  };
})();
