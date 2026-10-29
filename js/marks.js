/* Vocal Sessions · marks.js
   Q03 · Marks: Layered Annotations. Marks come in four layers, one per stage of learning a song (Notes, Phrasing,
   Words, Delivery), plus a Note bookmark on every layer. Only one layer shows at a time.
   This file holds what each mark is, checking saved marks, moving the older Annotate marks across, the copy kept in
   the older shape (so a backup still opens in 3.26), and drawing a line's marks. The marks sheet and selecting words
   are in songs.js, beside the rest of the song screen.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Marks: what each mark is ===== */
const MK_LAYERS = [
  ['notes', 'Notes'],
  ['phrasing', 'Phrasing'],
  ['words', 'Words'],
  ['delivery', 'Delivery'],
];
const MK_BY = {
  notes: ['pitch', 'slide', 'hold', 'ornament', 'rhythm'],
  phrasing: ['phrase', 'chain', 'peak', 'breath', 'shape'],
  words: ['vowel', 'carry', 'onset', 'stress', 'say'],
  delivery: ['register', 'colour', 'vibrato', 'mic', 'intention'],
};
// at: where a mark lands when several words are selected ('first', 'last', the whole 'range', or the 'section')
// txt: options that take text (true: every option, or the mark itself when it has none); need: text is required
const MK_DEF = {
  pitch: { L: 'notes', n: 'Pitch', g: '↕', opts: ['Up', 'Down', 'Starting note'], at: 'last' },
  slide: { L: 'notes', n: 'Slide', g: '↗', opts: ['Scoop up', 'Fall off', 'Slide between'], at: 'last' },
  hold: { L: 'notes', n: 'Hold', g: '━', opts: [], at: 'last' },
  ornament: { L: 'notes', n: 'Ornament', g: '∿', opts: ['Run', 'Riff', 'Turn', 'Flip', 'Grace note'], at: 'last' },
  rhythm: { L: 'notes', n: 'Rhythm', g: '»', opts: ['Pushed', 'Laid back', 'Off the beat'], at: 'last' },
  phrase: { L: 'phrasing', n: 'Phrase', g: '⌜⌝', opts: [], at: 'range' },
  chain: { L: 'phrasing', n: 'Chain', g: 'link', opts: [], at: 'last' },
  peak: { L: 'phrasing', n: 'Peak', g: '^', opts: [], at: 'first' },
  breath: { L: 'phrasing', n: 'Breath', g: 'breath', opts: ['Quick', 'Full', 'Sneak'], at: 'last' },
  shape: {
    L: 'phrasing',
    n: 'Shape',
    g: '<',
    opts: ['Swell', 'Fade', 'Arc', 'End: cut', 'End: release', 'End: fade'],
    at: 'range',
  },
  vowel: {
    L: 'words',
    n: 'Vowel',
    g: 'ɑ',
    opts: ['Tall', 'Open', 'Modified', 'Hold first vowel', 'Sing as…'],
    at: 'last',
    txt: ['Hold first vowel', 'Sing as…'],
    need: ['Sing as…'],
  },
  carry: { L: 'words', n: 'Carry', g: '‿', opts: [], at: 'last' },
  onset: { L: 'words', n: 'Onset', g: '›', opts: ['Soft', 'Breathy', 'Hard'], at: 'first' },
  stress: { L: 'words', n: 'Stress', g: 'stress', opts: [], at: 'range' },
  say: { L: 'words', n: 'Say', g: 'Aa', opts: [], at: 'last', txt: true, need: true },
  register: {
    L: 'delivery',
    n: 'Register',
    g: '⇅',
    opts: ['Chest', 'Mix', 'Head', 'Falsetto', 'Flip here'],
    at: 'first',
  },
  colour: {
    L: 'delivery',
    n: 'Colour',
    g: '◐',
    opts: ['Light', 'Full', 'Belt', 'Cry', 'Twang', 'Breathy'],
    at: 'first',
  },
  vibrato: { L: 'delivery', n: 'Vibrato', g: '≈', opts: ['Start vibrato', 'Straight tone'], at: 'last' },
  mic: { L: 'delivery', n: 'Mic', g: '◎', opts: ['Pull back', 'Come close'], at: 'last' },
  intention: { L: 'delivery', n: 'Intention', g: '♡', opts: [], at: 'section', txt: true, need: true },
  note: {
    L: 'note',
    n: 'Note',
    g: 'bookmark',
    opts: ['Trouble spot', 'Original does…', 'My version', 'Question'],
    at: 'last',
    txt: true,
  },
};
const MK_TEXT_MAX = 80,
  MK_NOTE_MAX = 200; // the older Annotate notes could be 200 characters, so a Note keeps that
const MKI = {
  bookmark:
    '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5h10v17l-5-3.6-5 3.6z" fill="currentColor" stroke="none"/></svg>',
  link: '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a4 4 0 005.66 0l3-3a4 4 0 00-5.66-5.66l-1 1"/><path d="M14 10a4 4 0 00-5.66 0l-3 3a4 4 0 005.66 5.66l1-1"/></svg>',
};
const mkLayerName = (L) => (MK_LAYERS.find((x) => x[0] === L) || [0, 'Note'])[1];
const mkLayerNum = (L) => MK_LAYERS.findIndex((x) => x[0] === L) + 1;
// where a mark of this type and option lands in a selection
function mkAt(type, opt) {
  if (type === 'register' && opt === 'Flip here') return 'last';
  return MK_DEF[type].at;
}
// whether an option (or the mark itself) takes text, and whether it must have some
function mkTakesText(type, opt) {
  const d = MK_DEF[type];
  if (!d || !d.txt) return false;
  return d.txt === true ? true : d.txt.includes(opt);
}
function mkNeedsText(type, opt) {
  const d = MK_DEF[type];
  if (!d || !d.need) return false;
  return d.need === true ? true : d.need.includes(opt);
}
const mkMax = (type) => (type === 'note' ? MK_NOTE_MAX : MK_TEXT_MAX);
const mkId = () => 'm' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);

/* ===== Marks: the layer shown, and Marks while playing (device only, never in backups) ===== */
function mkLayer() {
  const p = sgp();
  return MK_BY[p.mkLayer] ? p.mkLayer : 'phrasing';
}
function mkSetLayer(L) {
  if (!MK_BY[L]) return;
  sgp().mkLayer = L;
  saveSGP();
}

/* ===== Marks: checking saved marks =====
   sec.marks = [{id, L, type, opt, line, w0, w1, text, check?, was?}], stored once per section, so every repeat of a
   chorus shows the same marks. sec.held = marks whose word was removed, waiting at the top of the section to be moved
   or removed: [{id, L, type, opt, text, was}]. A bad mark is dropped on its own; the song is never touched. Fields
   this version doesn't know are kept on each mark. */
function mkClean(m, lines) {
  if (!m || typeof m !== 'object' || Array.isArray(m)) return null;
  const d = MK_DEF[m.type];
  if (!d || m.L !== d.L) return null;
  const b = Object.assign({}, m);
  b.id = typeof b.id === 'string' && b.id ? b.id.slice(0, 40) : mkId();
  if (typeof b.opt !== 'string') b.opt = '';
  if (b.opt && !d.opts.includes(b.opt)) return null;
  b.text = typeof b.text === 'string' ? b.text.trim().slice(0, mkMax(b.type)) : '';
  if (mkNeedsText(b.type, b.opt) && !b.text) return null;
  if (b.check) b.check = 1;
  else delete b.check;
  if (typeof b.was !== 'string' || !b.check) delete b.was;
  if (lines === null) {
    // a held mark: no place in the lyrics
    delete b.line;
    delete b.w0;
    delete b.w1;
    delete b.check;
    b.was = typeof m.was === 'string' ? m.was.slice(0, 60) : '';
    return b;
  }
  if (d.at === 'section') {
    if (b.line !== -1) return null;
    b.w0 = b.w1 = 0;
    return b;
  }
  if (!Number.isInteger(b.line) || !lines[b.line]) return null;
  const n = lines[b.line].length;
  if (!Number.isInteger(b.w0) || !Number.isInteger(b.w1) || b.w0 < 0 || b.w1 >= n || b.w0 > b.w1) return null;
  // a one-word mark always sits on one word (a range from somewhere else lands where it would have landed)
  const at = mkAt(b.type, b.opt);
  if (at === 'first') b.w1 = b.w0;
  else if (at === 'last') b.w0 = b.w1;
  return b;
}
function mkCleanList(list, lines) {
  const out = [],
    seen = new Set(),
    ids = new Set();
  let intent = false;
  (Array.isArray(list) ? list : []).forEach((m) => {
    const b = mkClean(m, lines);
    if (!b) return;
    if (b.type === 'intention') {
      if (intent) return; // one Intention per section
      intent = true;
    }
    const k = [b.L, b.type, b.opt, b.line, b.w0, b.w1, b.text].join('|');
    if (seen.has(k)) return;
    seen.add(k);
    if (ids.has(b.id)) b.id = mkId();
    ids.add(b.id);
    out.push(b);
  });
  return out;
}
function mkCleanHeld(list) {
  return (Array.isArray(list) ? list : []).map((m) => mkClean(m, null)).filter(Boolean);
}

/* ===== Marks: moving the older Annotate marks across =====
   Before 3.27 a section kept `ann`, mapping "line:word" to {br, run, up, dn, v (sing as), nt (note), check, was}, and
   `orphans`, [{id, was, ann}] for marks whose word was removed. Each becomes a mark in its layer. Anything else found
   on an old mark is kept as a plain Note carrying its name and value, so nothing is ever dropped. */
const MK_OLD = ['br', 'run', 'up', 'dn', 'v', 'nt', 'check', 'was'];
function mkFromOld(a, line, wi) {
  const out = [],
    at = (L, type, opt, text) =>
      out.push({ id: mkId(), L, type, opt: opt || '', line, w0: wi, w1: wi, text: text || '' });
  if (!a || typeof a !== 'object') return out;
  if (a.up) at('notes', 'pitch', 'Up');
  if (a.dn) at('notes', 'pitch', 'Down');
  if (a.run) at('notes', 'ornament', 'Run');
  if (a.br) at('phrasing', 'breath', '');
  if (typeof a.v === 'string' && a.v.trim()) at('words', 'vowel', 'Sing as…', a.v.trim().slice(0, MK_TEXT_MAX));
  if (typeof a.nt === 'string' && a.nt.trim()) at('note', 'note', '', a.nt.trim().slice(0, MK_NOTE_MAX));
  for (const k in a) {
    if (MK_OLD.includes(k)) continue;
    const v = a[k];
    if (v == null || v === false || v === '' || v === 0) continue;
    const t = typeof v === 'object' ? JSON.stringify(v) : String(v);
    at('note', 'note', '', (k + (t === '1' || t === 'true' ? '' : ': ' + t)).slice(0, MK_NOTE_MAX));
  }
  if (a.check)
    out.forEach((m) => {
      m.check = 1;
      if (typeof a.was === 'string') m.was = a.was;
    });
  return out;
}
// a section from before 3.27 (it has `ann` and no `marks`): its marks in the new shape
function mkMigrate(c, lines) {
  const marks = [],
    held = [];
  if (c.ann && typeof c.ann === 'object' && !Array.isArray(c.ann))
    for (const k in c.ann) {
      const m = /^(\d+):(\d+)$/.exec(k);
      if (!m) continue;
      mkFromOld(c.ann[k], +m[1], +m[2]).forEach((x) => marks.push(x));
    }
  (Array.isArray(c.orphans) ? c.orphans : []).forEach((o) => {
    if (!o || typeof o !== 'object') return;
    mkFromOld(o.ann, 0, 0).forEach((x) => {
      delete x.check;
      x.was = typeof o.was === 'string' ? o.was : '';
      held.push(x);
    });
  });
  return { marks: mkCleanList(marks, lines), held: mkCleanHeld(held) };
}

/* ===== Marks: the copy kept in the older shape =====
   Data changes are additive: a backup made now must still restore in 3.26. So each section also keeps `ann` and
   `orphans` as 3.26 would have written them, worked out from the marks every time they change. Marks with no older
   equivalent (a phrase, a vowel shape with no text) aren't in it. This version only ever reads `marks`. */
function mkOld(m) {
  switch (m.type) {
    case 'breath':
      return { br: 1 };
    case 'ornament':
      return m.opt === 'Run' ? { run: 1 } : null;
    case 'pitch':
      return m.opt === 'Up' ? { up: 1 } : m.opt === 'Down' ? { dn: 1 } : null;
    case 'vowel':
      return m.text ? { v: m.text.slice(0, 20) } : null;
    case 'note':
      return { nt: (m.text || m.opt || 'Note').slice(0, 200) };
  }
  return null;
}
function mkMirror(sec) {
  const ann = {};
  (sec.marks || []).forEach((m) => {
    if (m.line < 0) return;
    const o = mkOld(m);
    if (!o) return;
    const k = m.line + ':' + m.w1;
    const a = (ann[k] = Object.assign(ann[k] || {}, o));
    if (m.check) {
      a.check = 1;
      if (m.was) a.was = m.was;
    }
  });
  sec.ann = ann;
  sec.orphans = (sec.held || [])
    .map((m) => {
      const o = mkOld(m);
      return o ? { id: m.id, was: m.was || '', ann: o } : null;
    })
    .filter(Boolean);
}
// a section loaded or restored: marks checked (or moved across from before 3.27), and the older copy redone
function mkCleanSection(c, lines) {
  let marks, held;
  if (Array.isArray(c.marks)) {
    marks = mkCleanList(c.marks, lines);
    held = mkCleanHeld(c.held);
  } else ({ marks, held } = mkMigrate(c, lines));
  const s = { marks, held };
  mkMirror(s);
  return s;
}
// marks to check: those flagged after a lyric edit, and those waiting at the top of their section
function mkCheckCount(sec) {
  return (sec.held || []).length + (sec.marks || []).filter((m) => m.check).length;
}

/* ===== Marks: marks follow their words =====
   When lyrics change, a word-level comparison (align() in songs.js) moves each mark to where its word went. A mark
   whose word changed moves to the new word and is flagged to check; one whose word was removed waits at the top of its
   section. A range keeps the words that are still there. */
function mkRelink(sec, A, B, ops) {
  // where each old word went: {li, wi, changed, was} or null
  const to = new Map(),
    key = (li, wi) => li + ':' + wi;
  let dels = [],
    ins = [];
  const flush = () => {
    dels.forEach((i, k) =>
      to.set(
        key(A[i].li, A[i].wi),
        ins[k] != null ? { li: B[ins[k]].li, wi: B[ins[k]].wi, changed: true, was: A[i].w } : null
      )
    );
    dels = [];
    ins = [];
  };
  ops.forEach((op) => {
    if (op[0] === '=') {
      flush();
      to.set(key(A[op[1]].li, A[op[1]].wi), { li: B[op[2]].li, wi: B[op[2]].wi, changed: false });
    } else if (op[0] === '-') dels.push(op[1]);
    else ins.push(op[1]);
  });
  flush();
  let flagged = 0;
  const out = [];
  (sec.marks || []).forEach((m) => {
    if (m.line < 0) return out.push(m);
    const pts = [];
    for (let w = m.w0; w <= m.w1; w++) pts.push(to.get(key(m.line, w)));
    const kept = pts.filter(Boolean);
    // a range keeps the words still on the first remaining word's line
    const first = kept[0];
    if (!first) {
      const h = Object.assign({}, m, { was: m.was || (sec.lines[m.line] || [])[m.w1] || '' });
      delete h.line;
      delete h.w0;
      delete h.w1;
      delete h.check;
      sec.held = (sec.held || []).concat(h);
      flagged++;
      return;
    }
    const same = kept.filter((p) => p.li === first.li),
      changed = pts.some((p) => !p || p.changed) || same.length < kept.length;
    const n = Object.assign({}, m, { line: first.li, w0: first.wi, w1: same[same.length - 1].wi });
    if (changed) {
      n.check = 1;
      const c = pts.find((p) => p && p.changed);
      n.was = m.was || (c ? c.was : (sec.lines[m.line] || []).slice(m.w0, m.w1 + 1).join(' '));
      flagged++;
    }
    out.push(n);
  });
  sec.marks = out;
  return flagged;
}

/* ===== Marks: which marks a view draws ===== */
const MK_RECALL = ['phrase', 'chain', 'breath'];
// a test for which marks to draw: 'layer' (that layer plus Notes), 'recall' (brackets, chains, breaths and Notes),
// 'breaths', 'perform' (Marks while playing on a still page), or 'none'
function mkShow(kind, L) {
  switch (kind) {
    case 'layer':
      return (m) => m.L === L || m.L === 'note';
    case 'recall':
      return (m) => MK_RECALL.includes(m.type) || m.L === 'note';
    case 'breaths':
      return (m) => m.type === 'breath';
    case 'active':
      return (m) => m.L === L || m.type === 'breath';
  }
  return () => false;
}
// what a word wears, for one line: labels above, the peak tick, classes, glyphs after it, and the phrase brackets and
// stress underlines over word ranges
function mkDeco(sec, li, show) {
  const n = sec.lines[li].length,
    W = Array.from({ length: n }, () => ({ lab: [], pk: false, cls: [], after: '', mid: [], fresh: false })),
    ph = [],
    st = [],
    notes = [];
  (sec.marks || []).forEach((m) => {
    if (m.line !== li || m.w1 >= n || !show(m)) return;
    const w = W[m.w0],
      e = W[m.w1],
      o = m.opt,
      f = m.id === MARKS.fresh ? ' mkfresh' : '';
    switch (m.type) {
      case 'phrase':
        ph.push([m.w0, m.w1, f]);
        return;
      case 'stress':
        st.push([m.w0, m.w1, f]);
        return;
      case 'peak':
        w.pk = true;
        w.fresh = w.fresh || !!f;
        w.mid.push(m);
        return;
      case 'hold':
        e.cls.push('mhold' + f);
        e.mid.push(m);
        return;
      case 'chain':
        e.after += '<span class="mg mchain' + f + '" aria-label="chain">' + MKI.link + '</span>';
        return;
      case 'breath':
        e.after +=
          '<span class="m br' +
          (o === 'Sneak' ? ' sn' : '') +
          f +
          '" aria-label="' +
          (o ? o.toLowerCase() + ' ' : '') +
          'breath">' +
          SG_BR +
          '</span>';
        return;
      case 'carry':
        e.after += '<span class="mg mtie' + f + '" aria-label="carry">‿</span>';
        return;
      case 'note':
        e.after += '<span class="m nt' + f + '" aria-label="note">' + MKI.bookmark + '</span>';
        if (m.text) notes.push(m);
        return;
    }
    const t = mkLabel(m);
    if (!t) return;
    const at = m.type === 'shape' ? (o.startsWith('End') ? 'last' : 'first') : mkAt(m.type, o);
    const to = at === 'first' ? w : e;
    to.lab.push(t);
    to.mid.push(m);
    to.fresh = to.fresh || !!f;
  });
  return { W, ph, st, notes };
}
// the text of a label above a word
function mkLabel(m) {
  const o = m.opt;
  switch (m.type) {
    case 'pitch':
      return { Up: '↑', Down: '↓', 'Starting note': '♪' }[o] || '↕';
    case 'slide':
      return { 'Scoop up': '↗ scoop', 'Fall off': '↘ fall', 'Slide between': '⤳ slide' }[o] || 'slide';
    case 'ornament':
      return o ? '∿ ' + (o === 'Grace note' ? 'grace' : o.toLowerCase()) : '∿';
    case 'rhythm':
      return { Pushed: '» push', 'Laid back': '« back', 'Off the beat': '↯ off' }[o] || 'rhythm';
    case 'shape':
      return (
        { 'End: cut': 'cut', 'End: release': 'release', 'End: fade': 'fade out' }[o] || (o ? o.toLowerCase() : 'shape')
      );
    case 'vowel':
      return m.text || { Tall: 'tall', Open: 'open', Modified: 'mod', 'Hold first vowel': '1st vowel' }[o] || 'vowel';
    case 'onset':
      return o ? o.toLowerCase() : 'onset';
    case 'say':
      return 'say: ' + m.text;
    case 'register':
      return o === 'Flip here' ? 'flip' : o ? o.toLowerCase() : 'register';
    case 'colour':
      return o ? o.toLowerCase() : 'colour';
    case 'vibrato':
      return o === 'Straight tone' ? 'straight' : '≈ vib';
    case 'mic':
      return o === 'Come close' ? 'mic close' : 'mic back';
  }
  return '';
}
// the label row above a word: the peak tick first, then the labels joined with " · "
function mkLabRow(w, extra) {
  if (!w.lab.length && !w.pk) return '';
  return (
    '<span class="v' +
    (w.fresh ? ' mkfresh' : '') +
    (extra || '') +
    '">' +
    (w.pk ? '<i class="mpk" aria-label="peak">^</i>' : '') +
    w.lab.map(esc).join(' · ') +
    '</span>'
  );
}
/* one line: word(wi, w, deco) draws each word's own element; this puts the glyphs after it, the brackets and stress
   underlines round word ranges (spaces inside a range are inside it, so the line under it is unbroken), and the
   spaces. Ranges of one kind on one line never overlap (adding one replaces any it overlaps). */
function mkLineHTML(sec, li, show, word, wrapCls) {
  const d = mkDeco(sec, li, show),
    ln = sec.lines[li],
    n = ln.length,
    opens = Array.from({ length: n }, () => ''),
    closes = Array.from({ length: n }, () => '');
  d.ph.forEach((r) => {
    opens[r[0]] += '<span class="mph' + r[2] + (wrapCls || '') + '">';
    closes[r[1]] = '</span>' + closes[r[1]];
  });
  d.st.forEach((r) => {
    opens[r[0]] += '<span class="mst' + r[2] + (wrapCls || '') + '">';
    closes[r[1]] = '</span>' + closes[r[1]];
  });
  // brackets go outside stress underlines when both start or end on one word (only one layer shows at a time, so this
  // is only ever Recall's brackets inside nothing)
  let h = '';
  ln.forEach((w, wi) => {
    h += opens[wi] + word(wi, w, d.W[wi]) + d.W[wi].after + closes[wi];
    if (wi < n - 1 && !/mtie/.test(d.W[wi].after)) h += ' ';
  });
  return { html: h, notes: d.notes, labelled: d.W.some((w) => w.lab.length || w.pk) };
}
// the line in one section a selection or a held mark points at, as words
const mkWords = (sec, m) => (sec.lines[m.line] || []).slice(m.w0, m.w1 + 1).join(' ');
// a short name for a mark: "Breath · Quick", "Vowel · ah→ee", "Note"
function mkName(m) {
  const d = MK_DEF[m.type];
  if (!d) return 'Mark';
  const bits = [d.n];
  if (m.opt) bits.push(m.opt);
  if (m.text && m.type !== 'note') bits.push('“' + m.text + '”');
  return bits.join(' · ');
}
// a tile's glyph for a mark button
function mkGlyph(type) {
  const g = MK_DEF[type].g;
  if (g === 'breath') return '<span class="m br">' + SG_BR + '</span>';
  if (g === 'link') return MKI.link;
  if (g === 'bookmark') return MKI.bookmark;
  if (g === 'stress') return '<u>a</u>';
  return esc(g);
}

/* ===== Marks: changing them =====
   add(): puts a mark on a selection {sid, li, w0, w1}, keeping the layer's rules: a one-word mark on its word, one of
   each type and option per word, ranges of one kind on a line never overlapping, one Intention per section. Returns
   the marks it replaced, so Undo can put them back. */
function mkAdd(sec, sel, type, opt, text) {
  const d = MK_DEF[type];
  if (!d) return null;
  const at = mkAt(type, opt),
    m = {
      id: mkId(),
      L: d.L,
      type,
      opt: opt || '',
      line: sel.li,
      w0: sel.w0,
      w1: sel.w1,
      text: (text || '').trim().slice(0, mkMax(type)),
    };
  if (at === 'first') m.w1 = m.w0;
  if (at === 'last') m.w0 = m.w1;
  if (at === 'section') {
    m.line = -1;
    m.w0 = m.w1 = 0;
  }
  const gone = [];
  sec.marks = (sec.marks || []).filter((x) => {
    let out = false;
    if (x.type === type) {
      if (at === 'section') out = true;
      else if (x.line === m.line) {
        if (at === 'range')
          out =
            x.w0 <= m.w1 && m.w0 <= x.w1 && (type !== 'shape' || x.opt.startsWith('End') === m.opt.startsWith('End'));
        // one-word marks: the same word gets one of each type (pitch Up replaces Down; two Notes may share a word)
        else out = x.w0 === m.w0 && (type !== 'note' || (x.opt === m.opt && x.text === m.text));
      }
    }
    if (out) gone.push(x);
    return !out;
  });
  sec.marks.push(m);
  mkMirror(sec);
  return { m, gone };
}
function mkRemove(sec, id) {
  const i = (sec.marks || []).findIndex((x) => x.id === id);
  if (i < 0) return null;
  const m = sec.marks.splice(i, 1)[0];
  mkMirror(sec);
  return m;
}
// marks of a layer (and Notes) touching a selection, plus any flagged to check on any layer
function mkOnSel(sec, sel, L) {
  return (sec.marks || [])
    .filter((m) => m.line === sel.li && m.w0 <= sel.w1 && sel.w0 <= m.w1 && (m.L === L || m.L === 'note' || m.check))
    .concat(L === 'delivery' ? (sec.marks || []).filter((m) => m.type === 'intention') : []);
}

const MARKS = {
  fresh: null, // the mark just added, which fades in once
  layer: mkLayer,
  setLayer: mkSetLayer,
  show: mkShow,
  line: mkLineHTML,
  labRow: mkLabRow,
  clean: mkCleanSection,
  mirror: mkMirror,
  relink: mkRelink,
  add: mkAdd,
  remove: mkRemove,
  onSel: mkOnSel,
  name: mkName,
  checks: mkCheckCount,
  // tests and the data upgrade: a section's marks from the older `ann` and `orphans`, replacing what's there
  fromAnn(sec) {
    const r = mkMigrate({ ann: sec.ann, orphans: sec.orphans }, sec.lines);
    sec.marks = r.marks;
    sec.held = r.held;
    mkMirror(sec);
  },
  // Song Clock: which words of a line have a breath mark of Ivan's
  breaths(sec, li) {
    const b = sec.lines[li].map(() => false);
    (sec.marks || []).forEach((m) => {
      if (m.type === 'breath' && m.line === li && b[m.w1] != null) b[m.w1] = true;
    });
    return b;
  },
  // which words of a line have a mark of any kind (the lyrics editor highlights them)
  marked(sec, li) {
    const b = sec.lines[li].map(() => false);
    (sec.marks || []).forEach((m) => {
      if (m.line === li) for (let w = m.w0; w <= m.w1 && w < b.length; w++) b[w] = true;
    });
    return b;
  },
  intention: (sec) => (sec.marks || []).find((m) => m.type === 'intention') || null,
};
