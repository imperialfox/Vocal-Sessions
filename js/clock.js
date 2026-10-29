/* Vocal Sessions · clock.js
   Song Clock (3.18, phase A1): timing for a song's lyrics. Sync a song by tapping as each section starts, then play
   along with the words filling as they're sung, and check the timing line by line.
   Timing says when; marks say how. Timing is its own layer on the song record (sg.timing) and never changes the
   lyrics, sections, marks or takes.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Song Clock: the numbers ===== */
const CK_LAG = 0.15; // seconds taken off every tap or press, for the time a finger takes
const CK_MIN = 0.1; // a line lasts at least this long, and starts at least this long after the one before
const CK_DOT = 1.2; // a gap after a line longer than this gets an automatic breath dot
const CK_GAP = 0.35; // the gap left between lines spread evenly
const CK_MAXLEN = 20 * 60 + 59; // the song length picker goes to 20:59
const CK_TILES = ['timing', 'check', 'key', 'marks', 'blur', 'snap', 'awake', 'sync', 'lyrics', 'track']; // 3.19: track
const CK_MP = ['off', 'breaths', 'active']; // Marks while playing (Q03 added Active layer to the cycle)

// what's on screen now; nothing here is saved
const CK = {
  songId: null, // the song play-along belongs to
  on: false, // play-along is on
  ever: false, // it has been started since it was turned on
  pc: { base: 0, perf: 0, run: false }, // the play-along clock
  sc: { base: 0, perf: 0, run: false }, // the Sync clock
  P: null, // the Sync pass in progress
  head: false, // the pencil: title, artist and length edited in place
  gridEdit: false, // the controls grid is choosing what to pin
  ret: null, // where Sync and Check timing go back to
  undo: [], // timing as it was before each change, for the Undo toasts
  lastA: -2, // the line play-along last drew as current
  sig: '', // what the play-along view was built from
  raf: 0,
  fake: null, // tests: a clock that only moves when told (ms)
  wl: null, // the screen wake lock
  wlWant: false, // the wake lock is wanted now
  wlBusy: false,
  pk: null, // the length picker on screen
  lastTxt: '',
  trk: false, // Q02: play-along follows the song's track on this device (backing audio), not its own clock
  mute: false, // Q02: the backing audio muted (this time only; it starts on)
};

/* ===== Song Clock: the clock ===== */
const ckMs = () => (CK.fake != null ? CK.fake : performance.now());
const ckClk = (c) => (c.run ? c.base + (ckMs() - c.perf) / 1000 : c.base);
// Q02: while play-along plays the song's track, its time is the track's (so speed, a stall or a seek all follow);
// until the audio is playing, Song Clock's own clock carries on
function ckNow(c) {
  if (c === CK.pc && c.run && CK.trk) {
    const v = TRACK.alongNow(CK.songId);
    if (v != null) return v;
  }
  return ckClk(c);
}
// the track stopped under play-along (lock screen, another sound, the end of the track): play-along pauses too
function ckAlongStopped() {
  if (CK.pc.run) ckPause();
}
function ckSet(c, t) {
  c.base = Math.max(0, t);
  c.perf = ckMs();
}
function ckGo(c) {
  if (c.run) return;
  c.perf = ckMs();
  c.run = true;
}
function ckHalt(c) {
  if (!c.run) return;
  c.base = ckNow(c);
  c.run = false;
}
const ckFmt = (t) => {
  t = Math.max(0, t || 0);
  const m = Math.floor(t / 60),
    s = Math.floor(t - m * 60);
  return m + ':' + String(s).padStart(2, '0');
};
// vowel groups: how a line's time is shared between its words
const ckSyl = (w) =>
  Math.max(
    1,
    (
      String(w)
        .toLowerCase()
        .match(/[aeiouy]+/g) || []
    ).length
  );

/* ===== Song Clock: this device's settings (in vocalSongPrefs, never backed up) ===== */
function ckPrefs() {
  const p = sgp();
  if (p.ckReady) return p;
  const o = Object.assign({}, p); // sgp() keeps these keys as they were stored; they're checked here
  // Marks while playing is a string, so Marks 1 can add 'active' without changing anything stored
  p.marksPlaying = CK_MP.includes(o.marksPlaying) ? o.marksPlaying : 'breaths';
  p.blurAhead = typeof o.blurAhead === 'boolean' ? o.blurAhead : true;
  p.snapping = typeof o.snapping === 'boolean' ? o.snapping : true;
  p.stayAwake = typeof o.stayAwake === 'boolean' ? o.stayAwake : true;
  p.pins = Array.isArray(o.pins)
    ? o.pins.filter((x, i, a) => CK_TILES.includes(x) && a.indexOf(x) === i).slice(0, 3)
    : ['timing', 'key'];
  Object.defineProperty(p, 'ckReady', { value: true, enumerable: false });
  return p;
}
function ckPref(k, v) {
  ckPrefs()[k] = v;
  saveSGP();
}

/* ===== Song Clock: checking saved timing =====
   sg.timing = {len, real, est, slots: {o: {lines: [[start, end|null], …], anch, marks: [line…]}}}
   Timing belongs to places in the running order (o), not to sections: Chorus 2 is sung at a different time from
   Chorus 1. Anything malformed is dropped without touching the rest of the song. */
function cleanTiming(t, sg) {
  if (!t || typeof t !== 'object' || Array.isArray(t)) return null;
  const num = (x) => typeof x === 'number' && isFinite(x) && x >= 0;
  const out = {
    len: num(t.len) && t.len > 0 && t.len <= CK_MAXLEN ? Math.round(t.len) : null,
    real: t.real === true,
    est: t.est === true,
    slots: {},
  };
  // 3.20: the length follows the song's track (set when a track is added; unlinked by hand)
  if (t.lenLink === true && out.len != null) out.lenLink = true;
  const order = sg && Array.isArray(sg.order) ? sg.order : [];
  const src = t.slots && typeof t.slots === 'object' && !Array.isArray(t.slots) ? t.slots : {};
  order.forEach((x) => {
    const sec = sg.sections && sg.sections[x.sid],
      s = src[x.o];
    if (!sec || !s || typeof s !== 'object' || Array.isArray(s) || !Array.isArray(s.lines)) return;
    const n = sec.lines.length;
    let prev = null;
    const lines = [];
    for (let i = 0; i < n; i++) {
      const r = s.lines[i];
      let a = Array.isArray(r) && num(r[0]) ? r[0] : null,
        b = Array.isArray(r) && num(r[1]) ? r[1] : null;
      // in order and never overlapping: a line that starts too soon after the one before loses its time
      if (a != null && prev && prev[0] != null && a < prev[0] + CK_MIN - 1e-6) a = null;
      if (a == null) b = null;
      else {
        if (prev && prev[1] != null && prev[1] > a) prev[1] = a;
        if (b != null && b < a + CK_MIN - 1e-6) b = null;
      }
      const l = [a, b];
      lines.push(l);
      if (a != null) prev = l;
    }
    const marks = (Array.isArray(s.marks) ? s.marks : [])
      .filter((m, i, arr) => Number.isInteger(m) && m >= 0 && m < n && arr.indexOf(m) === i)
      .sort((p, q) => p - q);
    out.slots[x.o] = { lines, anch: s.anch === true, marks };
  });
  if (!Object.keys(out.slots).length && out.len == null) return null;
  return out;
}

/* ===== Song Clock: the song's lines, one after another ===== */
// every line in running order: {o, sid, li, k (place in the order), words, br (a breath mark of Ivan's on it)}
function ckLines(sg) {
  const L = [];
  if (!hasLyrics(sg)) return L;
  sg.order.forEach((x, k) => {
    const sec = sg.sections[x.sid];
    sec.lines.forEach((words, li) =>
      L.push({
        o: x.o,
        sid: x.sid,
        li,
        k,
        words,
        syl: words.map(ckSyl),
        br: MARKS.breaths(sec, li), // Q03: the layered marks (marks.js)
      })
    );
  });
  return L;
}
// a section's first line, as an index into ckLines
const ckFirst = (L, k) => L.findIndex((l) => l.k === k);
const ckEstDur = (l) => Math.max(1.2, l.syl.reduce((a, b) => a + b, 0) * 0.3);
const ckSynced = (sg) => !!(sg && sg.timing && hasLyrics(sg) && ckRaw(sg, ckLines(sg)).some((t) => t[0] != null));
// the saved times, one [start, end] per line (null where there's none)
function ckRaw(sg, L) {
  const s = (sg.timing && sg.timing.slots) || {};
  return L.map((l) => {
    const r = s[l.o] && s[l.o].lines[l.li];
    return r ? [r[0], r[1]] : [null, null];
  });
}
// times to play from: lines without a time are spread between their neighbours, and everything is kept in order
function ckFill(L, raw) {
  const T = raw.map((r) => [r[0], r[1]]),
    n = T.length;
  let i = 0;
  while (i < n) {
    if (T[i][0] != null) {
      i++;
      continue;
    }
    let j = i;
    while (j < n && T[j][0] == null) j++;
    const p = i - 1,
      durs = [];
    for (let m = i; m < j; m++) durs.push(ckEstDur(L[m]));
    const tot = durs.reduce((a, b) => a + b, 0) + CK_GAP * (durs.length - 1);
    let from = p >= 0 ? ckEnd(L, T, p) + CK_GAP : null,
      to = j < n ? T[j][0] - CK_GAP : null,
      sc = 1;
    if (from == null) from = to != null ? Math.max(0, to - tot) : 0;
    if (to != null && to - from > 0.2) sc = Math.min(1, (to - from) / tot);
    let t = from;
    for (let m = i; m < j; m++) {
      const d = durs[m - i] * sc;
      T[m] = [+t.toFixed(3), +(t + d).toFixed(3)];
      t += d + CK_GAP * sc;
    }
    i = j;
  }
  ckOrder(T);
  return T;
}
// a line's end: its own, else the next line's start or an estimate (0.3 s a syllable, at least 1.2 s)
function ckEnd(L, T, i) {
  if (T[i][1] != null) return T[i][1];
  const nx = i + 1 < T.length && T[i + 1][0] != null ? T[i + 1][0] : Infinity;
  return Math.min(nx, T[i][0] + ckEstDur(L[i]));
}
// lines in order and never overlapping: each starts at least 0.1 s after the one before, which ends by then
function ckOrder(T) {
  let prev = null;
  T.forEach((l) => {
    if (l[0] == null) return;
    if (l[0] < 0) l[0] = 0;
    if (prev) {
      if (l[0] < prev[0] + CK_MIN) l[0] = +(prev[0] + CK_MIN).toFixed(3);
      if (prev[1] != null && prev[1] > l[0]) prev[1] = l[0];
    }
    if (l[1] != null && l[1] < l[0] + CK_MIN) l[1] = +(l[0] + CK_MIN).toFixed(3);
    prev = l;
  });
  return T;
}
function ckAt(T, t) {
  let a = -1;
  for (let i = 0; i < T.length; i++) {
    if (T[i][0] == null) continue;
    if (T[i][0] <= t) a = i;
    else break;
  }
  return a;
}
// everything play-along and Check timing need for one song
function ckModel(sg) {
  const L = ckLines(sg),
    raw = ckRaw(sg, L),
    T = ckFill(L, raw);
  const slots = (sg.timing && sg.timing.slots) || {};
  return {
    sg,
    L,
    raw,
    T,
    anch: sg.order.map((x) => !!(slots[x.o] && slots[x.o].anch)),
    marks: L.map((l) => !!(slots[l.o] && slots[l.o].marks.includes(l.li))),
    end: (i) => ckEnd(L, T, i),
  };
}
// write lines' times (and section starts, to-do markers) back into the song, and save
function ckStore(sg, L, T, anch, marks, flags) {
  const old = sg.timing || {},
    slots = {};
  sg.order.forEach((x, k) => {
    slots[x.o] = { lines: [], anch: !!(anch && anch[k]), marks: [] };
  });
  L.forEach((l, i) => {
    const s = slots[l.o];
    s.lines[l.li] = [T[i][0] == null ? null : +T[i][0].toFixed(3), T[i][1] == null ? null : +T[i][1].toFixed(3)];
    if (marks && marks[i]) s.marks.push(l.li);
  });
  sg.timing = Object.assign(
    { len: old.len == null ? null : old.len, real: !!old.real, est: !!old.est },
    old.lenLink && old.len != null ? { lenLink: true } : {},
    flags || {},
    { slots }
  );
  save();
}
// withMarks (Q02): a marker made into a section start; the same Undo puts the marker (and its loop) back too
function ckSnap(sg, withMarks) {
  const u = { id: sg.id, t: JSON.stringify(sg.timing || null) };
  if (withMarks) u.mk = JSON.stringify({ markers: sg.markers || null, loop: sg.loop || null });
  CK.undo.push(u);
  if (CK.undo.length > 40) CK.undo.shift();
}
function ckUndo() {
  const u = CK.undo.pop(),
    sg = u && songById(u.id);
  if (!sg) return;
  const t = JSON.parse(u.t);
  if (t) sg.timing = t;
  else delete sg.timing;
  if (u.mk) {
    const o = JSON.parse(u.mk);
    if (o.markers) sg.markers = o.markers;
    else delete sg.markers;
    if (o.loop) sg.loop = o.loop;
    else delete sg.loop;
  }
  save();
  CK.lastA = -2;
  CK.sig = '';
  rerender();
  ckTick();
  toast('Undone');
}
// a toast with an Undo button
function ckToast(text, undo) {
  toast(text);
  if (!undo) return;
  const el = document.querySelector('.toast');
  if (!el) return;
  el.classList.add('ckundo');
  const b = document.createElement('button');
  b.className = 'ckub';
  b.textContent = 'Undo';
  b.addEventListener('click', (e) => {
    e.stopPropagation();
    el.remove();
    undo();
  });
  el.appendChild(b);
  clearTimeout(toastT);
  toastT = setTimeout(() => el.remove(), 4500);
}

/* ===== Song Clock: spreading lines evenly between section taps =====
   starts[k] is when place k in the running order starts (null if it wasn't tapped). Each section's lines are spread
   by syllables, squeezed or stretched to end a second before the next tapped section. */
function ckSpread(sg, L, starts) {
  const T = L.map(() => [null, null]);
  let cursor = 0;
  sg.order.forEach((x, k) => {
    const idx = [];
    L.forEach((l, i) => l.k === k && idx.push(i));
    if (!idx.length) return;
    let s0 = starts[k];
    if (s0 == null) s0 = k ? cursor + 1.5 : 0;
    const nxt = k + 1 < starts.length && starts[k + 1] != null ? starts[k + 1] : null;
    const durs = idx.map((i) => ckEstDur(L[i])),
      total = durs.reduce((a, b) => a + b, 0) + CK_GAP * (idx.length - 1);
    let sc = 1;
    if (nxt != null) {
      const room = nxt - 1 - s0;
      if (room > 0.5) sc = room / total;
    }
    let t = s0;
    idx.forEach((i, m) => {
      const d = durs[m] * sc;
      T[i] = [+t.toFixed(3), +(t + d).toFixed(3)];
      t += d + CK_GAP * sc;
    });
    cursor = t - CK_GAP * sc;
  });
  return ckOrder(T);
}
// piecewise-linear stretch through a set of [from, to] points; before the first and after the last, a plain shift
function ckWarp(pts) {
  const P = [];
  pts
    .filter((p) => isFinite(p[0]) && isFinite(p[1]))
    .sort((a, b) => a[0] - b[0])
    .forEach((p) => {
      if (!P.length || p[0] - P[P.length - 1][0] > 1e-4) P.push(p);
    });
  return (x) => {
    if (!P.length) return x;
    if (x <= P[0][0]) return x + P[0][1] - P[0][0];
    const Z = P[P.length - 1];
    if (x >= Z[0]) return x + Z[1] - Z[0];
    for (let j = 0; j < P.length - 1; j++) {
      const a = P[j],
        b = P[j + 1];
      if (x <= b[0]) return a[1] + ((x - a[0]) / (b[0] - a[0])) * (b[1] - a[1]);
    }
    return x;
  };
}

/* ===== Song Clock: lyric edits =====
   Called before a section's lines change. Only lines whose text changed lose their time; they get a to-do marker,
   and play-along spreads them between their neighbours until they're timed again. */
function ckLyricsChanged(sg, sid, oldLines, newLines) {
  if (!sg.timing || !sg.timing.slots) return;
  const key = (l) => ({ n: sgNorm(l.join(' ')) });
  const ops = align(oldLines.map(key), newLines.map(key));
  sg.order.forEach((x) => {
    if (x.sid !== sid) return;
    const s = sg.timing.slots[x.o];
    if (!s) return;
    const lines = [],
      marks = [];
    let changed = false;
    ops.forEach((op) => {
      if (op[0] === '=') {
        lines[op[2]] = (s.lines[op[1]] || [null, null]).slice();
        if (s.marks.includes(op[1])) marks.push(op[2]);
      } else if (op[0] === '+') {
        // align() gives ['=', old, new], ['-', old] and ['+', new]
        lines[op[1]] = [null, null];
        marks.push(op[1]);
        changed = true;
      } else changed = true;
    });
    for (let i = 0; i < newLines.length; i++) if (!lines[i]) lines[i] = [null, null];
    s.lines = lines;
    s.marks = marks.sort((a, b) => a - b);
    if (changed && !lines.some((l) => l[0] != null)) s.anch = false;
  });
}

/* ===== Song Clock: where it is ===== */
const ckSong = () => songById(CK.songId);
// play-along is on for the song on screen
function ckHere() {
  const sg = songShown();
  return !!(sg && CK.on && sg.id === CK.songId);
}
// the big lyric view shows while play-along runs (and before its first line, to tap it)
const ckBig = () => ckHere() && (CK.pc.run || !CK.ever) && !U.sEdit && !CK.head && !rec && !U.sheet;
function ckReturnPlace() {
  return split() ? { tab: 'songs', view: null } : { tab: 'songs', view: 'lyr' };
}

/* ===== Song Clock: play-along ===== */
function ckOn(sg) {
  if (!ckSynced(sg)) return ckStartSync(sg);
  CK.songId = sg.id;
  CK.on = true;
  CK.ever = false;
  CK.trk = TRACK.has(sg.id);
  CK.mute = false;
  ckHalt(CK.pc);
  const M = ckModel(sg);
  ckSet(CK.pc, M.T.length ? M.T[0][0] : 0);
  if (U.sMode === 'recall') U.sMode = 'practise';
  U.sSec = null;
  CK.lastA = -2;
  CK.sig = '';
  rerender();
}
function ckOff() {
  CK.on = false;
  CK.ever = false;
  ckHalt(CK.pc);
  TRACK.alongPause();
  CK.sig = '';
  ckWake();
  rerender();
}
// play from a line (or carry on from where the clock is)
function ckPlay(i) {
  const sg = ckSong();
  if (!sg || !CK.on) return;
  if (i != null) {
    const M = ckModel(sg);
    if (M.T[i]) ckSet(CK.pc, M.T[i][0]);
  }
  NOW.start('clock', sg.id, () => ckPause()); // one sound at a time (3.20)
  CK.ever = true;
  ckGo(CK.pc);
  // Q02: with the song's track on this device, play-along plays it and follows its time (lyric-only without it)
  // (where it should be is fixed now: a redraw below would otherwise read the track's old place back)
  CK.trk = TRACK.has(sg.id);
  if (CK.trk) {
    const t0 = ckClk(CK.pc),
      m0 = ckMs();
    TRACK.along(sg.id, () => t0 + (ckMs() - m0) / 1000, CK.mute);
  }
  CK.lastA = -2;
  if (ckHere()) rerender();
  else fwUpdate();
  ckWake();
  ckLoop();
}
// pausing shows the song page, with the current line kept where your eye was
function ckPause() {
  if (!CK.pc.run) return;
  const cur = document.querySelector('#ckpa:not([hidden]) .ckl.now'),
    y = cur ? cur.getBoundingClientRect().top : null;
  ckHalt(CK.pc);
  TRACK.alongPause();
  ckWake();
  NOW.ended('clock');
  fwPaused('clock'); // 3.20: paused anywhere but the window (or lock screen): no window follows
  if (!ckHere()) return fwUpdate();
  rerender();
  const line = document.querySelector('.sgl.ckcur');
  if (line && y != null) window.scrollTo(0, Math.max(0, window.scrollY + line.getBoundingClientRect().top - y));
}
function ckNudge(d) {
  const sg = ckSong();
  if (!sg || !ckSynced(sg)) return;
  ckSnap(sg);
  const M = ckModel(sg),
    T = M.raw.map((r) => [r[0] == null ? null : Math.max(0, r[0] + d), r[1] == null ? null : Math.max(0, r[1] + d)]);
  ckStore(sg, M.L, ckOrder(T), M.anch, M.marks);
  CK.lastA = -2;
  CK.sig = '';
  if (!CK.pc.run) rerender();
  else CLOCK.after();
  ckTick();
  ckToast('Lyrics 0.2 s ' + (d < 0 ? 'earlier' : 'later'), ckUndo);
}

// the big lyric view: its own layer over the song page, so pausing just shows the page underneath
function ckLayer() {
  let el = $('ckpa');
  if (el) return el;
  el = document.createElement('div');
  el.id = 'ckpa';
  el.className = 'ckpa';
  el.hidden = true;
  el.innerHTML = '<div class="ckview"><div class="ckin"></div></div><p class="ckcap" aria-live="polite"></p>';
  document.body.appendChild(el);
  el.addEventListener('click', (e) => {
    const l = e.target.closest('.ckl');
    if (!l || !CK.on) return;
    ckPlay(+l.dataset.i); // tap a line to jump the clock there (the first tap starts it)
  });
  el.addEventListener('contextmenu', (e) => e.preventDefault());
  return el;
}
function ckBuild(sg) {
  const M = ckModel(sg),
    mp = ckPrefs().marksPlaying,
    L = MARKS.layer(),
    // Q03 Active layer: the chosen layer's marks are drawn on every line, but show only on the line being sung and
    // the next one (CSS, from .now and .nx), so lines never change height as the song moves on; breaths show on all
    show = mp === 'active' ? (m) => m.L === L && m.type !== 'breath' : () => false;
  let h = '',
    lastK = -1;
  M.L.forEach((l, i) => {
    if (l.k !== lastK) {
      lastK = l.k;
      h += '<p class="cklab" data-k="' + l.k + '">' + esc(occLabel(sg, l.k)) + '</p>';
      const it = mp === 'active' && L === 'delivery' && MARKS.intention(sg.sections[l.sid]);
      if (it) h += '<p class="mint ckint" data-k="' + l.k + '">' + esc(it.text) + '</p>';
    }
    // Marks while playing, Breaths only: Ivan's breath marks on every line; an automatic dot only on a line with a
    // long gap after it and no breath mark of his. Bookmarks never show while playing.
    const mine = mp !== 'off' && l.br.some(Boolean),
      gap = i + 1 < M.T.length ? M.T[i + 1][0] - M.end(i) : 0,
      dot = mp !== 'off' && !l.br.some(Boolean) && gap > CK_DOT;
    const r = MARKS.line(sg.sections[l.sid], l.li, show, (wi, w, d) => {
      const lab = MARKS.labRow(d),
        word = '<span class="ckw">' + esc(w) + '</span>',
        br = mine && l.br[wi] ? '<span class="ckbr" aria-label="breath">' + SG_BR + '</span>' : '';
      return (
        (lab || d.cls.length
          ? '<span class="ckwd' +
            (lab ? ' hv' : '') +
            (d.cls.length ? ' ' + d.cls.join(' ') : '') +
            '">' +
            lab +
            word +
            '</span>'
          : word) + br
      );
    });
    h +=
      '<p class="ckl fut' +
      (r.labelled ? ' hasv' : '') +
      '" data-a="ckLine" data-i="' +
      i +
      '">' +
      r.html +
      (dot ? '<span class="ckdot" aria-label="breathe"></span>' : '') +
      '</p>';
  });
  return h;
}
function ckSig(sg) {
  const p = ckPrefs();
  return (
    sg.id +
    '|' +
    JSON.stringify(sg.timing) +
    '|' +
    JSON.stringify(sg.order) +
    '|' +
    p.marksPlaying +
    '|' +
    p.blurAhead +
    '|' +
    MARKS.layer() +
    '|' +
    sg.order.map((x) => JSON.stringify(sg.sections[x.sid].marks)).join()
  );
}
// draw the current line, word fill, distance blur and dots; called every frame while the clock runs
function ckTick() {
  // Q02: Song Clock's own clock keeps up with the track, so a jump or a pause carries on from the right place
  if (CK.pc.run && CK.trk) {
    const v = TRACK.alongNow(CK.songId);
    if (v != null) {
      CK.pc.base = v;
      CK.pc.perf = ckMs();
    }
  }
  const el = $('ckpa');
  const sg = ckSong();
  if (el && !el.hidden && sg) {
    const M = ckModel(sg),
      t = ckNow(CK.pc),
      a = ckAt(M.T, t),
      lines = el.querySelectorAll('.ckl');
    if (a !== CK.lastA && lines.length) {
      CK.lastA = a;
      const blurOn = ckPrefs().blurAhead;
      lines.forEach((ln, i) => {
        const d = i - a;
        ln.classList.toggle('past', i < a);
        ln.classList.toggle('now', i === a);
        ln.classList.toggle('fut', i > a);
        ln.classList.toggle('nx', i === a + 1); // Q03 Active layer shows on this line and the next
        ln.style.opacity = i < a ? '0.4' : d > 0 && blurOn ? MOTION.dim(d) : '';
        const b = d > 0 && blurOn ? MOTION.blur(d) : 0;
        ln.style.filter = b ? 'blur(' + b + 'px)' : '';
        if (i !== a) ln.querySelectorAll('.ckw').forEach((w) => w.style.setProperty('--p', i < a ? 1 : 0));
      });
      el.querySelectorAll('.cklab').forEach((lb) => {
        const k = +lb.dataset.k,
          first = ckFirst(M.L, k),
          d = first - a;
        lb.style.opacity = d > 0 && blurOn ? MOTION.dimLabel(d) : '';
      });
      const tg = lines[Math.max(a, 0)],
        box = el.querySelector('.ckin');
      box.style.transform = 'translateY(' + Math.round(box.parentNode.clientHeight * 0.3 - tg.offsetTop) + 'px)';
      const cap = el.querySelector('.ckcap'),
        ct = CK.pc.run ? 'Tap a line to jump to it' : 'Tap the first line as it’s sung';
      if (cap.textContent !== ct) cap.textContent = ct;
    }
    if (a >= 0 && lines[a]) {
      const s = M.T[a][0],
        e = M.end(a),
        sy = M.L[a].syl,
        tot = sy.reduce((x, y) => x + y, 0);
      let c = 0;
      lines[a].querySelectorAll('.ckw').forEach((w, k) => {
        const w0 = s + ((e - s) * c) / tot;
        c += sy[k];
        const w1 = s + ((e - s) * c) / tot;
        w.style.setProperty('--p', Math.max(0, Math.min(1, (t - w0) / Math.max(0.05, w1 - w0))).toFixed(3));
      });
    }
    // an automatic dot brightens through the gap after its line
    el.querySelectorAll('.ckdot.on').forEach((d) => d.classList.remove('on'));
    if (a >= 0 && lines[a] && t > M.end(a)) {
      const d = lines[a].querySelector('.ckdot');
      if (d) d.classList.add('on');
    }
  }
  // the transport's time and the Sync timer change only their text (motion rule 8: digits never animate)
  const tt = $('ckT');
  if (tt) {
    const v = ckFmt(ckNow(CK.pc));
    if (tt.textContent !== v) tt.textContent = v;
  }
  // Q03 marking while listening: the timer pill in the top bar, and a soft highlight on the line being sung (the page
  // never scrolls by itself, so it stays where Ivan is marking)
  const mt = $('mkT');
  if (mt) {
    const v = ckFmt(ckNow(CK.pc));
    if (mt.textContent !== v) mt.textContent = v;
  }
  if (U.sEdit === 'annotate' && sg && ckHere()) {
    const M = ckModel(sg),
      a = CK.ever ? ckAt(M.T, ckNow(CK.pc)) : -1,
      l = a >= 0 ? M.L[a] : null,
      key = l ? l.o + '|' + l.li : '';
    if (key !== CK.mkLine) {
      CK.mkLine = key;
      document.querySelectorAll('.sgl.mknow').forEach((x) => x.classList.remove('mknow'));
      if (l) {
        const line = document.querySelector('.sgl[data-o="' + l.o + '"][data-li="' + l.li + '"]');
        if (line) line.classList.add('mknow');
      }
    }
  }
  const st = $('ckST');
  if (st && CK.P) {
    const v = ckFmt(ckNow(CK.sc));
    if (st.textContent !== v) st.textContent = v;
  }
  if (FW.shown === 'clock') {
    const v = ckFwText();
    if (v !== CK.lastTxt) {
      CK.lastTxt = v;
      fwTick();
    }
  }
}
function ckLoop() {
  if (CK.raf) return;
  const f = () => {
    CK.raf = 0;
    if (!CK.pc.run && !CK.sc.run) return;
    ckTick();
    CK.raf = requestAnimationFrame(f);
  };
  CK.raf = requestAnimationFrame(f);
}

/* ===== Song Clock: keeping the screen awake while timing (Stay awake) ===== */
function ckWake() {
  const want =
    ckPrefs().stayAwake &&
    !document.hidden &&
    ((CK.pc.run && ckHere()) || (CK.sc.run && U.view === 'ckSync' && !!CK.P));
  CK.wlWant = !!want;
  try {
    if (want && !CK.wl && !CK.wlBusy && navigator.wakeLock) {
      CK.wlBusy = true;
      navigator.wakeLock
        .request('screen')
        .then((l) => {
          CK.wlBusy = false;
          if (!CK.wlWant) return l.release().catch(() => {});
          CK.wl = l;
          l.addEventListener('release', () => {
            if (CK.wl === l) CK.wl = null;
          });
        })
        .catch(() => {
          CK.wlBusy = false;
        });
    } else if (!want && CK.wl) {
      const l = CK.wl;
      CK.wl = null;
      l.release().catch(() => {});
    }
  } catch (e) {
    CK.wlBusy = false;
  }
}
document.addEventListener('visibilitychange', () => ckWake());

/* ===== Song Clock: Sync, the section pass =====
   Tap the pad as each section starts; the first tap starts the clock. Pause on one phone means re-anchor: scrub the
   song back a little, then tap as this section starts, and the clock carries on from the guessed start. */
function ckStartSync(sg, keepRet) {
  if (!hasLyrics(sg)) return;
  if (rec) return toast('Stop recording first');
  if (CK.on && CK.songId === sg.id) {
    CK.on = false;
    CK.ever = false;
    ckHalt(CK.pc);
    TRACK.alongPause();
  }
  NOW.stop(); // timing with music in another app: nothing here keeps playing
  const n = sg.order.length;
  CK.P = {
    id: sg.id,
    idx: 0,
    raw: Array.from({ length: n }, () => null),
    started: false,
    note: false,
    pending: null,
  };
  CK.P.pending = ckGuess(sg, 0);
  ckHalt(CK.sc);
  ckSet(CK.sc, CK.P.pending);
  if (!keepRet || !CK.ret) CK.ret = ckReturnPlace();
  CK.head = false;
  U.clock = false;
  ckPushFrom('ck:sync');
  go(() => {
    U.songId = sg.id;
    U.view = 'ckSync';
    U.sheet = null;
    U.sd = {};
  });
}
// where section k is expected to start: after the last one tapped, or where the song's timing has it
function ckGuess(sg, k) {
  const P = CK.P,
    synced = ckSynced(sg),
    M = ckModel(sg),
    f = (j) => M.T[ckFirst(M.L, j)][0];
  if (k > 0 && P.raw[k - 1] != null) {
    if (synced) return P.raw[k - 1] + (f(k) - f(k - 1));
    let d = 0;
    M.L.forEach((l) => l.k === k - 1 && (d += ckEstDur(l) + CK_GAP));
    return P.raw[k - 1] + d + 1.5;
  }
  return synced ? f(k) : 0;
}
function ckPadDown() {
  const P = CK.P,
    sg = P && songById(P.id);
  if (!sg || U.view !== 'ckSync' || P.idx >= P.raw.length) return;
  if (P.pending != null) {
    // the first tap (or the first after a pause) starts the clock from the expected start
    ckSet(CK.sc, P.pending + CK_LAG);
    ckGo(CK.sc);
    P.pending = null;
    P.note = false;
    ckLoop();
  }
  P.started = true;
  P.raw[P.idx] = +Math.max(0, ckNow(CK.sc) - CK_LAG).toFixed(3);
  P.idx++;
  ckWake();
  if (P.idx >= P.raw.length) return ckFinish();
  ckSyncPaint();
}
function ckSyncPause() {
  const P = CK.P,
    sg = P && songById(P.id);
  if (!sg || !P.started || P.note) return;
  ckHalt(CK.sc);
  P.pending = ckGuess(sg, P.idx);
  ckSet(CK.sc, P.pending);
  P.note = true;
  ckWake();
  ckSyncPaint();
}
function ckRedo(k) {
  const P = CK.P,
    sg = P && songById(P.id);
  if (!sg || k < 0 || k >= P.idx) return;
  const prev = P.raw[k];
  for (let j = k; j < P.raw.length; j++) P.raw[j] = null;
  P.idx = k;
  ckHalt(CK.sc);
  P.pending = prev != null ? prev : ckGuess(sg, k);
  ckSet(CK.sc, P.pending);
  P.note = true;
  ckWake();
  ckSyncPaint();
}
function ckSyncUndo() {
  const P = CK.P;
  if (!P || P.idx <= 0 || P.note) return;
  P.idx--;
  P.raw[P.idx] = null;
  ckSyncPaint();
}
// after the pass: lines are spread evenly inside each section, and the tapped sections become set starts
function ckFinish() {
  const P = CK.P,
    sg = P && songById(P.id);
  ckHalt(CK.sc);
  CK.P = null;
  ckWake();
  if (!sg) return ckLeave();
  const tapped = [];
  P.raw.forEach((s, k) => s != null && tapped.push(k));
  if (!tapped.length) return ckLeave(sg);
  ckSnap(sg);
  const M = ckModel(sg),
    anch = M.anch.slice();
  let T;
  if (ckSynced(sg)) {
    // already timed: keep the first tapped section where it is and stretch the rest through the taps
    const f = (k) => M.T[ckFirst(M.L, k)][0],
      off = f(tapped[0]) - P.raw[tapped[0]],
      w = ckWarp(tapped.map((k) => [f(k), P.raw[k] + off]));
    T = M.T.map((r) => [w(r[0]), r[1] == null ? null : w(r[1])]);
    ckOrder(T);
    tapped.forEach((k) => (anch[k] = true));
    ckStore(sg, M.L, T, anch, M.marks);
  } else {
    T = ckSpread(sg, M.L, P.raw);
    tapped.forEach((k) => (anch[k] = true));
    ckStore(sg, M.L, T, anch, M.marks, { est: true });
  }
  ckOpenCheck(sg, true);
  ckToast('Timing saved', ckUndo);
}
function ckLeave(sg) {
  ckHalt(CK.sc);
  CK.P = null;
  ckWake();
  sg = sg || songById(U.songId);
  if (sg && ckSynced(sg)) return ckOpenCheck(sg, true);
  ckBack();
}
function ckBack() {
  const r = CK.ret || ckReturnPlace();
  CK.ret = null;
  go(() => {
    U.tab = r.tab;
    U.view = r.view;
    U.sheet = null;
    U.sd = {};
  });
}
// 3.23 (Q08): from a song page, Sync by sections and Check timing push in from the right; between the two they
// replace each other, so Back (or ✕, or Done) still slides away to the song page
function ckPushFrom(key) {
  if (U.view === 'lyr') ZOOM.armPush(key);
  else if (U.view === 'ckSync' || U.view === 'ckCheck') ZOOM.retarget();
}
function ckOpenCheck(sg, keepRet) {
  if (!keepRet || !CK.ret) CK.ret = ckReturnPlace();
  CK.head = false;
  ckPushFrom('ck:check');
  go(() => {
    U.songId = sg.id;
    U.view = 'ckCheck';
    U.sheet = null;
    U.sd = {};
  });
}
function ckSyncPage() {
  const P = CK.P,
    sg = P && songById(P.id);
  if (!sg) return '<div class="sgempty"><b>Nothing to sync.</b></div>';
  if (!P.started && !P.note) {
    let list = '';
    sg.order.slice(0, 6).forEach((x, k) => {
      list += k
        ? '<p class="ckrl">' + esc(occLabel(sg, k)) + '</p>'
        : '<p class="ckrl first">' + esc(occLabel(sg, k)) + ' <span class="cktag">First</span></p>';
    });
    if (sg.order.length > 6) list += '<p class="ckrl more">and ' + (sg.order.length - 6) + ' more</p>';
    return (
      '<div class="cksync ready"><h1>Start the song</h1><p class="cksub">Tap the pad as each section starts. A few taps get the whole song moving. Your first tap starts the clock.</p>' +
      '<div class="ckcard">' +
      list +
      '</div><p class="foot ckfoot">Play it on another device or in your music app. On a computer, the space bar works too.</p></div>'
    );
  }
  return '<div class="cksync live" id="cklive">' + ckLiveHTML(sg) + '</div>';
}
function ckLiveHTML(sg) {
  const P = CK.P,
    n = P.raw.length,
    name = (k) => esc(occLabel(sg, k));
  let h =
    '<div class="ckprog"><span class="foot">Section ' +
    Math.min(P.idx + 1, n) +
    ' of ' +
    n +
    '</span><div class="ckbar"><i style="width:' +
    ((P.idx / n) * 100).toFixed(1) +
    '%"></i></div></div><div class="cklist">';
  for (let k = Math.max(0, P.idx - (P.note ? 3 : 4)); k < (P.note ? P.idx : P.idx - 1); k++)
    h +=
      '<button class="ckdone" data-a="ckRedo" data-v="' +
      k +
      '" aria-label="Redo from here: ' +
      name(k) +
      '"><span>' +
      name(k) +
      '</span><span aria-hidden="true">✓</span></button>';
  if (P.note)
    h +=
      '<div class="cknote">Scrub the song back a little, then tap the pad as this section starts.</div><div class="cknow"><span class="cktag">From here</span>' +
      name(P.idx) +
      '</div>';
  else {
    if (P.idx > 0) h += '<div class="cknow"><span class="cktag">Just marked</span>' + name(P.idx - 1) + '</div>';
    if (P.idx < n) h += '<div class="cknext"><span class="cktag">Next</span>' + name(P.idx) + '</div>';
  }
  h +=
    '</div><div class="ckrow2"><button class="sgpill" data-a="ckSyncPause"' +
    (P.started && !P.note ? '' : ' disabled') +
    '>' +
    ICON.pause +
    'Pause</button><button class="sgpill" data-a="ckFinish">Finish</button></div>';
  return h;
}
// a tap only changes what's needed: the live list, the pad's words and the top bar
function ckSyncPaint() {
  const sg = CK.P && songById(CK.P.id),
    live = $('cklive');
  if (!sg || !live) return rerender();
  live.innerHTML = ckLiveHTML(sg);
  const pad = $('ckpad');
  if (pad) pad.innerHTML = ckPadInner(sg);
  renderBar();
  ckTick();
}
function ckPadInner(sg) {
  const P = CK.P;
  return '<b>Tap</b><span>' + (P.idx < P.raw.length ? 'as “' + esc(occLabel(sg, P.idx)) + '” starts' : '') + '</span>';
}

/* ===== Song Clock: Check timing ===== */
function ckCheckPage() {
  const sg = songById(U.songId);
  if (!sg || !hasLyrics(sg)) return '<div class="sgempty"><b>This song was deleted.</b></div>';
  const M = ckModel(sg),
    synced = ckSynced(sg),
    nAnch = M.anch.filter(Boolean).length,
    nMarks = M.marks.filter(Boolean).length,
    len = sg.timing && sg.timing.len;
  let h =
    '<h1>Check timing</h1><p class="sgart">' +
    esc(songTitle(sg)) +
    '</p><div class="grp"><button class="row" data-a="ckLen"><span class="lbl">Song length</span><span class="mut">' +
    (len ? ckFmt(len) : 'Add') +
    '</span>' +
    chev +
    '</button><div class="row"><span class="lbl">Section starts</span><span class="mut">' +
    nAnch +
    ' of ' +
    sg.order.length +
    ' set</span></div>' +
    (nMarks
      ? '<div class="row"><span class="lbl">To-do markers</span><span class="mut">' + nMarks + '</span></div>'
      : '') +
    '</div>';
  if (!synced)
    return (
      h +
      '<p class="foot ckfootc">This song isn’t synced yet.</p><button class="cta ink ckcta" data-a="ckSyncAgain">Sync</button>'
    );
  if (sg.timing.est)
    h +=
      '<div class="cknote2">Lines are spread evenly between your section taps. For exact timing, time each line once.<div><button class="sgpill blue" data-a="ckLinePass">Time each line</button></div></div>';
  let lastK = -1;
  M.L.forEach((l, i) => {
    if (l.k !== lastK) {
      if (lastK >= 0) h += '</div>';
      lastK = l.k;
      h +=
        '<div class="hdr">' +
        (M.anch[l.k] ? '<span class="ckadot" aria-label="Start set"></span>' : '') +
        esc(occLabel(sg, l.k)) +
        '</div><div class="grp ckgrp">';
    }
    const dur = M.end(i) - M.T[i][0],
      flag = dur < 0.4 ? 'Very short' : dur > 15 ? 'Very long' : '';
    h +=
      '<div class="ckr" data-i="' +
      i +
      '"><span class="ckt">' +
      esc(l.words.join(' ')) +
      '</span><span class="cktl">' +
      (M.marks[i] ? '<span class="ckmk" role="img" aria-label="To-do marker"></span>' : '') +
      (flag
        ? '<span class="ckflag">' + flag + '</span>'
        : '<i class="ckd" style="width:' + Math.max(8, Math.round(Math.min(dur / 8, 1) * 80)) + 'px"></i>') +
      '</span></div>';
  });
  if (lastK >= 0) h += '</div>';
  h +=
    '<button class="cta ink ckcta" data-a="ckCheckDone" data-pop>Done</button><div class="ckcen"><button class="lnkbtn" data-a="ckSyncAgain">Sync again from the start</button></div>';
  return h;
}

/* ===== Song Clock: the song header ===== */
// "Artist · 3:58", up to three pinned icons, then ⋯
function ckHeadHTML(sg) {
  const len = sg.timing && sg.timing.len,
    p = ckPrefs();
  if (CK.head)
    return (
      '<div class="ckedrow"><input class="ckin2" id="ckArtist" aria-label="Artist" placeholder="Artist" autocomplete="off" value="' +
      esc(sg.artist || '') +
      '"><span class="mut" aria-hidden="true">·</span><button class="cklen ed" data-a="ckLen" aria-label="Song length">' +
      (len ? ckFmt(len) : 'Add length') +
      '</button></div><div class="ckerow"><div class="cksw" role="group" aria-label="Edit"><button data-a="ckHeadMarks">' +
      'Marks' +
      (checkCount(sg) ? '<span class="sgbadge">' + checkCount(sg) + '</span>' : '') +
      '</button><button data-a="ckHeadLyrics">Lyrics</button></div><span class="sp"></span><button class="sgpill blue" data-a="ckHeadDone">Done</button></div>'
    );
  const art = esc(sg.artist || ''),
    lenB = ckLenHTML(sg);
  const pins = p.pins
    .map((id) => {
      const t = ckTile(id, sg);
      return (
        '<button class="ckpi' +
        (t.on ? ' on' : '') +
        '" data-a="ckTile" data-v="' +
        id +
        '" aria-label="' +
        t.l +
        '"' +
        (t.toggle ? ' aria-pressed="' + !!t.on + '"' : '') +
        '>' +
        t.ic +
        '</button>'
      );
    })
    .join('');
  return (
    '<div class="ckrow"><p class="sgart ckart">' +
    art +
    (art && lenB ? '<span aria-hidden="true"> · </span>' : '') +
    lenB +
    '</p>' +
    pins +
    '<button class="ckpi" data-a="ckGrid" aria-label="Song controls">' +
    SGI.more +
    '</button></div>' +
    ckLenFoot(sg)
  );
}
// 3.20 the length and its link to the song's track: 'on' follows the track, 'off' is a custom length beside one
function ckLinkState(sg) {
  const len = sg && sg.timing && sg.timing.len;
  if (!sg || !sg.track || !len) return '';
  return sg.timing.lenLink ? 'on' : 'off';
}
function ckLenHTML(sg) {
  const len = sg.timing && sg.timing.len,
    st = ckLinkState(sg);
  if (!len) return '';
  return (
    '<button class="cklen" data-a="ckLen" aria-label="Song length ' +
    ckFmt(len) +
    (st === 'on' ? ', linked to the track' : '') +
    '">' +
    ckFmt(len) +
    (st === 'on' ? '<span class="lnk on">' + SG_LNK + '</span>' : '') +
    '</button>' +
    (st === 'off'
      ? '<button class="lnk off" data-a="ckRelink" aria-label="Relink to the track">' + SG_UNLNK + '</button>'
      : '')
  );
}
function ckLenFoot(sg) {
  return ckLinkState(sg) === 'off'
    ? '<p class="cklenf">Custom · track is ' + ckFmt(Math.round(sg.track.dur)) + '</p>'
    : '';
}
function ckTitleInput(sg) {
  return (
    '<input class="ckin2 ckh1" id="ckTitle" aria-label="Song title" autocomplete="off" value="' +
    esc(songTitle(sg)) +
    '">'
  );
}
// keep what's typed in the title and artist fields
function ckCommitHead() {
  const sg = songById(U.songId),
    t = $('ckTitle'),
    a = $('ckArtist');
  if (!sg || (!t && !a)) return false;
  let ch = false;
  if (t) {
    const v = titleCase(t.value);
    if (v && v !== sg.name) {
      sg.name = v;
      ch = true;
    }
  }
  if (a) {
    const v = titleCase(a.value);
    if (v !== (sg.artist || '')) {
      sg.artist = v;
      ch = true;
    }
  }
  if (ch) save();
  return ch;
}
function ckHeadEnd() {
  ckCommitHead();
  CK.head = false;
}

/* ===== Song Clock: the controls grid ===== */
const CKI = {
  clock: SGI.clock,
  list: '<svg class="i" viewBox="0 0 24 24"><path d="M10 6h10M10 12h10M10 18h10"/><path d="M3.5 6l1.2 1.2L7 5M3.5 12l1.2 1.2L7 11M3.5 18l1.2 1.2L7 17"/></svg>',
  key: SGI.music,
  marks:
    '<svg class="i" viewBox="0 0 24 24" style="fill:currentColor;stroke:none"><circle cx="5" cy="12" r="2.4"/><circle cx="12" cy="12" r="2.4" opacity=".6"/><circle cx="19" cy="12" r="2.4" opacity=".3"/></svg>',
  blur: '<svg class="i" viewBox="0 0 24 24"><path d="M4 7h16"/><path d="M5.5 12h13" opacity=".6"/><path d="M8 17h8" opacity=".3"/></svg>',
  snap: '<svg class="i" viewBox="0 0 24 24"><path d="M6 4v8a6 6 0 0012 0V4"/><path d="M6 8h3.5M14.5 8H18"/></svg>',
  awake:
    '<svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6L7 7M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/></svg>',
  sync: '<svg class="i" viewBox="0 0 24 24"><path d="M19.5 12a7.5 7.5 0 11-2.3-5.4"/><path d="M19.5 4v4.5H15"/></svg>',
  lyrics:
    '<svg class="i" viewBox="0 0 24 24"><path d="M4 6h16M4 11h16M4 16h9"/><path d="M16.5 16.5l3 3-3 .6.6-3z"/></svg>',
  track:
    '<svg class="i" viewBox="0 0 24 24"><path d="M3.5 12h1M7 8.5v7M10.5 5v14M14 9v6M17.5 6.5v11M21 10.5v3"/></svg>',
  // Q02 the backing track's sound, and muted
  sound:
    '<svg class="i" viewBox="0 0 24 24"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4.5 4.5 0 010 6M18 6.5a8 8 0 010 11"/></svg>',
  muted:
    '<svg class="i" viewBox="0 0 24 24"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M16 9.5l5 5M21 9.5l-5 5"/></svg>',
};
const CK_MPNAME = { off: 'Off', breaths: 'Breaths only', active: 'Active layer' };
// each tile: its label, icon, whether it's on (blue), and its value line where it has one
function ckTile(id, sg) {
  const p = ckPrefs(),
    playing = !!(sg && CK.on && CK.songId === sg.id);
  return (
    {
      timing: { l: 'Timing', ic: CKI.clock, toggle: true, on: playing },
      check: { l: 'Check timing', ic: CKI.list },
      key: { l: 'Key', ic: CKI.key },
      marks: {
        l: 'Marks while playing',
        ic: CKI.marks,
        toggle: true,
        on: p.marksPlaying !== 'off',
        val: CK_MPNAME[p.marksPlaying],
      },
      blur: { l: 'Blur ahead', ic: CKI.blur, toggle: true, on: p.blurAhead },
      snap: { l: 'Snapping', ic: CKI.snap, toggle: true, on: p.snapping, auto: true },
      awake: { l: 'Stay awake', ic: CKI.awake, toggle: true, on: p.stayAwake },
      sync: { l: 'Sync again', ic: CKI.sync },
      lyrics: { l: 'Lyrics', ic: CKI.lyrics },
      // 3.19 the track player: opens it, or adds the song's track
      track: { l: sg && TRACK.has(sg.id) ? 'Track' : 'Add track', ic: CKI.track },
    }[id] || { l: id, ic: '' }
  );
}
function ckGridSheet() {
  const sg = songById(U.songId),
    p = ckPrefs(),
    ed = CK.gridEdit;
  const tiles = CK_TILES.map((id) => {
    const t = ckTile(id, sg),
      pin = p.pins.includes(id),
      on = t.on && !ed;
    return (
      '<button class="cktile' +
      (on ? ' on' : '') +
      '" data-a="ckTile" data-v="' +
      id +
      '"' +
      (t.toggle && !ed ? ' aria-pressed="' + !!t.on + '"' : '') +
      (ed ? ' aria-label="' + (pin ? 'Unpin ' : 'Pin ') + t.l + '"' : '') +
      '><span class="ckc">' +
      t.ic +
      (t.auto && t.on && !ed ? '<span class="ckab" aria-hidden="true">A</span>' : '') +
      (ed ? '<span class="ckpb' + (pin ? ' on' : '') + '" aria-hidden="true">' + (pin ? '✓' : '+') + '</span>' : '') +
      '</span><span class="cktl2">' +
      t.l +
      (t.val ? '<small>' + t.val + '</small>' : '') +
      '</span></button>'
    );
  }).join('');
  return sheetWrap(
    'Song controls',
    '<div class="ckgrid">' +
      tiles +
      '</div><p class="foot ckgnote">' +
      (ed
        ? 'Choose up to 3 to pin beside the artist. ' + p.pins.length + ' of 3 pinned.'
        : 'Blue is on. A means it adjusts by itself.') +
      '</p>',
    'Song controls',
    '<button class="txtbtn glass ckgedit" data-a="ckGridEdit">' + (ed ? 'Done' : 'Edit') + '</button>'
  );
}
function ckTileAct(id, fromGrid) {
  const sg = songById(U.songId),
    p = ckPrefs();
  if (fromGrid && CK.gridEdit) {
    const i = p.pins.indexOf(id);
    if (i >= 0) p.pins.splice(i, 1);
    else {
      if (p.pins.length >= 3) return toast('Unpin one first. 3 is the most');
      p.pins.push(id);
    }
    saveSGP();
    return rerender();
  }
  const close = () => {
    if (U.sheet === 'ckGrid') {
      U.sheet = null;
      U.sd = {};
    }
  };
  switch (id) {
    case 'timing':
      if (!sg || !hasLyrics(sg)) return;
      close();
      if (CK.on && CK.songId === sg.id) return ckOff();
      return ckOn(sg);
    case 'check':
      if (!sg || !hasLyrics(sg)) return;
      close();
      return ckSynced(sg) ? ckOpenCheck(sg) : ckStartSync(sg);
    case 'key':
      U.sheet = 'sgKey';
      U.sd = {};
      return rerender();
    case 'marks': {
      // Q03: Off → Breaths only → Active layer → Off
      const n = CK_MP[(CK_MP.indexOf(p.marksPlaying) + 1) % CK_MP.length];
      ckPref('marksPlaying', n);
      CK.sig = '';
      rerender();
      return toast(
        'Marks while playing: ' + CK_MPNAME[n] + (n === 'active' ? ' (' + mkLayerName(MARKS.layer()) + ')' : '')
      );
    }
    case 'blur':
      ckPref('blurAhead', !p.blurAhead);
      CK.sig = '';
      rerender();
      return toast(p.blurAhead ? 'Blur ahead on' : 'Blur ahead off');
    case 'snap':
      ckPref('snapping', !p.snapping);
      rerender();
      return toast(p.snapping ? 'Snapping on' : 'Snapping off');
    case 'awake':
      ckPref('stayAwake', !p.stayAwake);
      ckWake();
      rerender();
      return toast(p.stayAwake ? 'The screen stays awake while timing' : 'The screen can sleep');
    case 'sync':
      if (!sg || !hasLyrics(sg)) return;
      close();
      return ckStartSync(sg);
    case 'lyrics':
      if (!sg || !hasLyrics(sg)) return;
      close();
      return ckLyricsEdit();
    case 'track':
      if (!sg) return;
      close();
      if (TRACK.has(sg.id)) return TRACK.open(sg.id);
      rerender();
      return TRACK.pick(sg.id);
  }
}

/* ===== Song Clock: the song length picker =====
   Clock-style wheels: minutes 0–20 and seconds 00–59, not looping, one band across with the units in it. It pops
   over just below whatever was tapped. */
const CK_RH = 36;
function ckPick(anchor, value, onSet) {
  ckPickClose();
  const v = Math.max(0, Math.min(CK_MAXLEN, Math.round(value || 0)));
  const pk = { vals: { m: Math.floor(v / 60), s: v % 60 }, onSet };
  CK.pk = pk;
  const el = document.createElement('div');
  el.id = 'ckpk';
  el.className = 'ckpk';
  el.innerHTML =
    '<div class="ckpscrim" data-a="ckPickCancel"></div><div class="ckpop glass" role="dialog" aria-modal="true" aria-label="Song length" data-own-gesture><div class="ckphd"><span>Song length</span><b id="ckpOut"></b></div><div class="ckwh"><div class="ckband"></div></div><div class="ckpft"><button class="lnkbtn mut" data-a="ckPickCancel">Cancel</button><button class="lnkbtn" data-a="ckPickSet">Set</button></div></div>';
  document.body.appendChild(el);
  const wh = el.querySelector('.ckwh');
  const inits = [];
  const col = (key, n, pad, unit) => {
    const wrap = document.createElement('div');
    wrap.className = 'ckwwrap';
    const c = document.createElement('div');
    c.className = 'ckwcol';
    c.tabIndex = 0;
    c.dataset.k = key;
    c.setAttribute('role', 'spinbutton');
    c.setAttribute('aria-label', key === 'm' ? 'Minutes' : 'Seconds');
    let h = '<div class="ckwp"></div>';
    for (let i = 0; i < n; i++) h += '<div data-v="' + i + '">' + (pad ? String(i).padStart(2, '0') : i) + '</div>';
    c.innerHTML = h + '<div class="ckwp"></div>';
    wrap.appendChild(c);
    const u = document.createElement('span');
    u.className = 'ckwu';
    u.textContent = unit;
    wrap.appendChild(u);
    wh.appendChild(wrap);
    const items = [...c.querySelectorAll('[data-v]')];
    const paint = () => {
      if (CK.pk !== pk) return;
      const pos = c.scrollTop / CK_RH;
      items.forEach((it, i) => {
        const d = Math.min(Math.abs(i - pos), 3);
        it.style.opacity = (1 - d * 0.28).toFixed(2);
      });
      const i = Math.max(0, Math.min(n - 1, Math.round(pos)));
      if (pk.vals[key] !== i) {
        pk.vals[key] = i;
        ckPickOut();
      }
      c.setAttribute('aria-valuenow', i);
    };
    c.addEventListener('scroll', () => requestAnimationFrame(paint), { passive: true });
    c.addEventListener('click', (e) => {
      const it = e.target.closest('[data-v]');
      if (it) c.scrollTo({ top: +it.dataset.v * CK_RH, behavior: MOTION.on() ? 'smooth' : 'auto' });
    });
    c.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      e.preventDefault();
      const i = Math.max(0, Math.min(n - 1, pk.vals[key] + (e.key === 'ArrowDown' ? 1 : -1)));
      c.scrollTop = i * CK_RH;
      paint();
    });
    inits.push(() => {
      c.scrollTop = pk.vals[key] * CK_RH;
      paint();
    });
  };
  col('m', 21, false, 'min');
  col('s', 60, true, 'sec');
  // pops over just below what was tapped (above it if there's no room)
  const pop = el.querySelector('.ckpop'),
    r = anchor && anchor.getBoundingClientRect ? anchor.getBoundingClientRect() : null,
    vw = document.documentElement.clientWidth,
    vh = window.innerHeight,
    w = pop.offsetWidth,
    h = pop.offsetHeight;
  let left = r ? r.left + r.width / 2 - w / 2 : (vw - w) / 2;
  left = Math.max(12, Math.min(vw - w - 12, left));
  let top = r ? r.bottom + 8 : (vh - h) / 2;
  if (r && top + h > vh - 12) top = r.top - h - 8;
  if (top < 12) top = Math.max(12, (vh - h) / 2);
  pop.style.left = left + 'px';
  pop.style.top = top + 'px';
  inits.forEach((f) => f());
  ckPickOut();
  MOTION.animate(
    pop,
    [
      { opacity: 0, transform: 'scale(.94)' },
      { opacity: 1, transform: 'none' },
    ],
    {
      spring: 'gentle',
      fade: true,
    }
  );
  const first = el.querySelector('.ckwcol');
  try {
    first.focus({ preventScroll: true });
  } catch (e) {}
  fwUpdate();
}
function ckPickOut() {
  const o = $('ckpOut');
  if (o && CK.pk) o.textContent = CK.pk.vals.m + ':' + String(CK.pk.vals.s).padStart(2, '0');
}
function ckPickClose() {
  const el = $('ckpk');
  if (el) el.remove();
  CK.pk = null;
}
function ckSetLen(sg, v) {
  if (!sg) return;
  ckSnap(sg);
  if (!sg.timing) sg.timing = { len: null, real: false, est: false, slots: {} };
  sg.timing.len = v > 0 ? Math.min(CK_MAXLEN, Math.round(v)) : null;
  delete sg.timing.lenLink; // a length set by hand is the song's own (3.20)
  if (sg.timing.len == null && !Object.keys(sg.timing.slots || {}).length) delete sg.timing;
  save();
  rerender();
  ckToast(v > 0 ? 'Song length ' + ckFmt(v) : 'Song length cleared', ckUndo);
}

/* ===== Song Clock: the floating window ===== */
function ckFwText() {
  const sg = ckSong();
  if (!sg) return '';
  const M = ckModel(sg),
    t = ckNow(CK.pc),
    a = ckAt(M.T, t);
  return (CK.pc.run ? '' : 'Paused · ') + ckFmt(t) + (a >= 0 ? ' · ' + occLabel(sg, M.L[a].k) : '');
}
const CK_FW = {
  id: 'clock',
  active: () => !!(CK.on && CK.ever && hasLyrics(ckSong())),
  // its own screen is the song it plays from
  own() {
    const sg = songShown();
    return !!(sg && sg.id === CK.songId);
  },
  info() {
    return {
      k: 'Playing along',
      t: ckFwText(),
      p: null,
      on: CK.pc.run,
      open: 'Back to the song',
      label: 'Playing along' + (CK.pc.run ? '' : ', paused'),
    };
  },
  toggle() {
    if (CK.pc.run) ckPause();
    else ckPlay();
    fwTick();
  },
  close() {
    if (CK.pc.run) ckPause();
    CK.ever = false;
  },
  open() {
    const sg = ckSong();
    if (!sg) return;
    ckPickClose();
    CK.lastA = -2;
    CK.sig = '';
    const r = ckReturnPlace();
    fwGo(() => {
      U.tab = r.tab;
      U.view = r.view;
      U.songId = sg.id;
      U.sheet = null;
      U.sd = {};
      if (U.sMode === 'recall') U.sMode = 'practise';
    }, 0);
    // paused: back on the song page at the line it stopped on
    const line = document.querySelector('.sgl.ckcur');
    if (line && !CK.pc.run) line.scrollIntoView({ block: 'center' });
  },
};
// take → video → playing along → session
FW_KINDS.splice(
  Math.max(
    0,
    FW_KINDS.findIndex((k) => k.id === 'session')
  ),
  0,
  CK_FW
);

// the big view's place: the song's column, from just below its header row to the bottom of the screen
function ckPlace(el) {
  const box = document.querySelector('.sgpane') || $('app'),
    r = box.getBoundingClientRect(),
    head = document.querySelector('.ckrow'),
    bar = Math.max(0, $('bar').getBoundingClientRect().bottom),
    top = Math.max(bar, head ? head.getBoundingClientRect().bottom + 4 : bar);
  el.style.left = r.left + 'px';
  el.style.width = r.width + 'px';
  el.style.top = Math.round(top) + 'px';
}
window.addEventListener('resize', () => {
  const el = $('ckpa');
  if (el && !el.hidden) {
    ckPlace(el);
    CK.lastA = -2;
    ckTick();
  }
});

/* ===== Song Clock: after every redraw ===== */
const CLOCK = {
  // Q03 marking while listening: the clock is running under the Marks side
  marking: () => !!(U.sEdit === 'annotate' && ckHere() && CK.ever),
  timerPill() {
    if (!CLOCK.marking()) return '';
    return (
      '<button class="pill glass mktp" data-a="ckPP" aria-label="' +
      (CK.pc.run ? 'Pause' : 'Play') +
      ' play-along">' +
      (CK.pc.run ? ICON.pause : ICON.play) +
      '<span id="mkT">' +
      ckFmt(ckNow(CK.pc)) +
      '</span></button>'
    );
  },
  before() {
    // keep what's typed in the pencil's fields; leave it (and stop timing passes) when the song isn't on screen
    if (CK.head) ckCommitHead();
    if (CK.head && !songShown()) CK.head = false;
  },
  after() {
    // a Sync pass only lives on its own screen
    if (CK.P && U.view !== 'ckSync') {
      ckHalt(CK.sc);
      CK.P = null;
    }
    if (U.view !== 'ckSync' && U.view !== 'ckCheck' && CK.pk && !songShown()) ckPickClose();
    if (CK.on && !hasLyrics(ckSong())) {
      CK.on = false;
      ckHalt(CK.pc);
      TRACK.alongPause();
    }
    const el = ckLayer(),
      sg = ckSong(),
      big = ckBig();
    if (big) {
      // it covers the song below its header, so the title, the pinned icons and ⋯ stay in reach; the page goes
      // to its top when the view appears and can't scroll away underneath it
      if (el.hidden) window.scrollTo(0, 0);
      document.documentElement.classList.add('ckplay');
      ckPlace(el);
      const sig = ckSig(sg);
      el.classList.toggle('mpact', ckPrefs().marksPlaying === 'active'); // Q03 Active layer
      if (CK.sig !== sig || el.hidden) {
        CK.sig = sig;
        const inn = el.querySelector('.ckin');
        inn.innerHTML = ckBuild(sg);
        inn.classList.add('nofx');
        el.hidden = false;
        CK.lastA = -2;
        ckTick();
        void inn.offsetWidth;
        inn.classList.remove('nofx');
      } else ckTick();
    } else if (!el.hidden) {
      el.hidden = true;
      CK.sig = '';
    }
    document.body.classList.toggle('ckplay', big);
    if (!big) document.documentElement.classList.remove('ckplay');
    // 3.20: paused, the song page has room below its end, so the current line can stay where the eye was (a taller
    // header or wider fonts could leave too little page to scroll)
    document.body.classList.toggle('ckpaused', !!(CK.on && ckHere() && !CK.pc.run && !U.sEdit));
    document.body.classList.toggle('cksyncon', U.view === 'ckSync');
    // paused: the song page shows the current line
    document.querySelectorAll('.sgl.ckcur').forEach((l) => l.classList.remove('ckcur'));
    if (ckHere() && CK.ever && !CK.pc.run && !U.sEdit) {
      const M = ckModel(sg),
        a = Math.max(0, ckAt(M.T, ckNow(CK.pc))),
        l = M.L[a];
      const line = l && document.querySelector('.sgl[data-o="' + l.o + '"][data-li="' + l.li + '"]');
      if (line) line.classList.add('ckcur');
    }
    ckWake();
    CK.mkLine = null; // the song page was redrawn: the marking highlight goes back on at the next tick
    if (CLOCK.marking()) ckTick();
    if (CK.pc.run || CK.sc.run) ckLoop();
  },
  // the transport (play-along) or the pad (Sync), in the dock
  dock() {
    if (U.view === 'ckSync' && CK.P) {
      const sg = songById(CK.P.id);
      if (!sg) return '';
      return (
        '<button class="ckpad" id="ckpad" data-a="ckPad" data-own-gesture aria-label="Tap as the section starts">' +
        ckPadInner(sg) +
        '</button>'
      );
    }
    if (!ckHere() || U.sEdit || CK.head || recallOn()) return '';
    return (
      '<div class="cktr glass" role="group" aria-label="Play along"><button class="cknb" data-a="ckNudge" data-v="-0.2" aria-label="Move all lyrics 0.2 seconds earlier">−0.2</button><button class="ckpp" data-a="ckPP" aria-label="' +
      (CK.pc.run ? 'Pause' : 'Play') +
      '">' +
      (CK.pc.run ? ICON.pause : ICON.play) +
      '<span id="ckT">' +
      ckFmt(ckNow(CK.pc)) +
      '</span></button><button class="cknb" data-a="ckNudge" data-v="0.2" aria-label="Move all lyrics 0.2 seconds later">+0.2</button>' +
      // Q02: the song's track plays under play-along (on by default); without it on this device, no mute button
      (TRACK.has(CK.songId)
        ? '<button class="cknb ckmute' +
          (CK.mute ? ' on' : '') +
          '" id="ckMute" data-a="ckMute" aria-pressed="' +
          CK.mute +
          '" aria-label="' +
          (CK.mute ? 'Unmute the track' : 'Mute the track') +
          '">' +
          (CK.mute ? CKI.muted : CKI.sound) +
          '</button>'
        : '') +
      '</div>'
    );
  },
  bar() {
    if (U.view === 'ckSync') {
      const P = CK.P,
        live = P && (P.started || P.note);
      return {
        l: '<button class="circ glass" data-a="ckSyncX" data-pop aria-label="Close">' + ICON.x + '</button>',
        t: live
          ? '<span class="pill glass ckpill"><span class="recdot" aria-hidden="true"></span><span id="ckST">' +
            ckFmt(ckNow(CK.sc)) +
            '</span></span>'
          : 'Sync timing',
        r: live
          ? '<button class="circ glass" data-a="ckSyncUndo" aria-label="Undo last tap"' +
            (P.idx > 0 && !P.note ? '' : ' disabled') +
            '>' +
            SGI.undo +
            '</button>'
          : '',
      };
    }
    return {
      l: '<button class="circ glass" data-a="ckCheckBack" aria-label="Back">' + ICON.back + '</button>',
      t: 'Check timing',
      r: '',
    };
  },
  page: () => (U.view === 'ckSync' ? ckSyncPage() : ckCheckPage()),
  headHTML: ckHeadHTML,
  lenHTML: ckLenHTML,
  lenFoot: ckLenFoot,
  titleInput: ckTitleInput,
  editingHead: () => CK.head,
  gridSheet: ckGridSheet,
  lyricsChanged: ckLyricsChanged,
  synced: ckSynced,
  // for the tests: a clock that only moves when told
  fake(ms) {
    CK.fake = ms;
  },
  advance(sec) {
    if (CK.fake == null) CK.fake = performance.now();
    CK.fake += sec * 1000;
    ckTick();
  },
  tick: ckTick,
  model: (id) => ckModel(songById(id || U.songId)),
  now: () => ckNow(CK.pc),
  syncNow: () => ckNow(CK.sc),
  pick: (anchor, v, f) => ckPick(anchor, v, f),
  pickClose: ckPickClose,
  padDown: ckPadDown,
  play: ckPlay,
  pause: ckPause,
  off: ckOff,
  state: () => ({
    on: CK.on,
    ever: CK.ever,
    run: CK.pc.run,
    songId: CK.songId,
    syncing: !!CK.P,
    syncRun: CK.sc.run,
    pass: CK.P ? JSON.parse(JSON.stringify(CK.P)) : null,
    head: CK.head,
    wake: CK.wlWant,
    picker: !!CK.pk,
    undo: CK.undo.length,
    trk: CK.trk,
    mute: CK.mute,
  }),
  // stop everything (Reset all data, a restore)
  reset() {
    CK.on = CK.ever = false;
    ckHalt(CK.pc);
    ckHalt(CK.sc);
    TRACK.alongPause();
    CK.P = null;
    CK.head = false;
    CK.undo = [];
    ckPickClose();
    ckWake();
  },
};

/* ===== Song Clock: actions (data-a="ck…") ===== */
Object.assign(SG_ACT, {
  ckTile(el, v) {
    ckTileAct(v, !!el.closest('.sheet'));
  },
  ckGrid() {
    if (rec) return toast('Stop recording first');
    CK.gridEdit = false;
    U.sheet = 'ckGrid';
    U.sd = {};
    rerender();
  },
  ckGridEdit() {
    CK.gridEdit = !CK.gridEdit;
    rerender();
  },
  ckLen(el) {
    const sg = songById(U.songId);
    if (!sg) return;
    ckCommitHead();
    // 3.20: a length linked to the track asks before it's changed by hand
    if (ckLinkState(sg) === 'on') {
      U.sheet = 'sgLenUnlink';
      U.sd = { k: sg.id };
      return rerender();
    }
    ckPick(el, (sg.timing && sg.timing.len) || 210, (v) => ckSetLen(sg, v));
  },
  ckRelink() {
    sgRelink(songById(U.songId));
  },
  ckPencil() {
    const sg = songById(U.songId);
    if (!hasLyrics(sg)) return;
    if (rec) return toast('Stop recording first');
    // Q03 marking while listening: with play-along running, the pencil goes straight to Marks and the clock carries on
    if (CK.pc.run && ckHere()) return SG_ACT.sgEdit();
    U.sSec = null;
    CK.head = true;
    rerender();
    setTimeout(() => {
      const i = $('ckTitle');
      if (i) i.focus({ preventScroll: true });
    }, 60);
  },
  ckHeadDone() {
    ckHeadEnd();
    rerender();
  },
  ckHeadLyrics() {
    ckHeadEnd();
    ckLyricsEdit();
  },
  ckHeadMarks() {
    ckHeadEnd();
    SG_ACT.sgEdit();
  },
  ckPP() {
    if (CK.pc.run) ckPause();
    else ckPlay();
  },
  ckNudge(el, v) {
    ckNudge(+v);
  },
  // Q02: mute the track under play-along (the lyrics still follow its time)
  ckMute() {
    CK.mute = !CK.mute;
    TRACK.alongMute(CK.mute);
    const b = $('ckMute');
    if (b) {
      b.classList.toggle('on', CK.mute);
      b.setAttribute('aria-pressed', CK.mute);
      b.setAttribute('aria-label', CK.mute ? 'Unmute the track' : 'Mute the track');
      b.innerHTML = CK.mute ? CKI.muted : CKI.sound;
    }
    toast(CK.mute ? 'Track muted' : 'Track on');
  },
  ckSyncX() {
    ckLeave();
  },
  ckSyncUndo() {
    ckSyncUndo();
  },
  ckSyncPause() {
    ckSyncPause();
  },
  ckFinish() {
    ckFinish();
  },
  ckRedo(el, v) {
    ckRedo(+v);
  },
  ckCheckBack() {
    ckBack();
  },
  ckCheckDone() {
    ckBack();
  },
  ckSyncAgain() {
    const sg = songById(U.songId);
    if (sg) ckStartSync(sg, true);
  },
  // the pad works on pointerdown and the lines through the layer's own click handler; these are just their names
  ckPad() {},
  ckLine() {},
  ckPickSet() {
    const pk = CK.pk;
    if (!pk) return;
    const val = pk.vals.m * 60 + pk.vals.s;
    ckPickClose();
    pk.onSet(val);
  },
  ckPickCancel() {
    ckPickClose();
  },
  ckLinePass() {
    toast('Timing each line arrives in the next update');
  },
});
// straight into editing the lyrics
function ckLyricsEdit() {
  if (CK.pc.run) ckPause();
  SG_ACT.sgEdit();
  if (U.sEdit) {
    U.sEdit = 'lyrics';
    rerender();
  }
}

/* ===== Song Clock: the pad, from a finger or the space bar ===== */
document.addEventListener(
  'pointerdown',
  (e) => {
    if (e.button > 0) return;
    const p = e.target.closest && e.target.closest('#ckpad');
    if (!p) return;
    e.preventDefault();
    p.classList.add('down');
    ckPadDown();
  },
  { passive: false }
);
['pointerup', 'pointercancel'].forEach((t) =>
  document.addEventListener(t, () => {
    const p = $('ckpad');
    if (p) p.classList.remove('down');
  })
);
document.addEventListener('keydown', (e) => {
  if (U.sheet) return;
  const typing = e.target.closest && e.target.closest('input,textarea,[contenteditable="true"]');
  if (U.view === 'ckSync' && CK.P && e.key === ' ' && !typing) {
    e.preventDefault();
    if (!e.repeat) ckPadDown();
    return;
  }
  if (e.key === 'Escape') {
    if (CK.pk) {
      ckPickClose();
      return;
    }
    if (CK.head && songShown()) {
      ckHeadEnd();
      rerender();
    }
  }
  if (e.key === 'Enter' && typing && CK.head && (e.target.id === 'ckTitle' || e.target.id === 'ckArtist')) {
    e.preventDefault();
    ckHeadEnd();
    rerender();
  }
});
