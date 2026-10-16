/* Vocal Sessions · songs.js
   Songs: the list, pasting lyrics, the lyrics screen with marks and cues, editing, search and pinned songs.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Songs: constants and icons ===== */
const SG_LABELS = [
  'Intro',
  'Verse',
  'Pre-chorus',
  'Chorus',
  'Post-chorus',
  'Bridge',
  'Hook',
  'Interlude',
  'Tag',
  'Outro',
];
const MAXPIN = 3;
const SG_SORTS = { recent: 'Recently practised', added: 'Recently added', az: 'Title A–Z' };
const SG_BR =
  '<svg viewBox="0 0 10 17" aria-hidden="true"><circle cx="5" cy="5" r="4.2"/><path d="M9 6C9 11 6.6 14.6 2.4 16.4" stroke="currentColor" stroke-width="2.6" fill="none" stroke-linecap="round"/></svg>';
const SGI = {
  music:
    '<svg class="i" viewBox="0 0 24 24"><path d="M9 18V5.5l11-2.5v12.5"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="15.5" r="3"/></svg>',
  search: '<svg class="i" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L20 20"/></svg>',
  pin: '<svg class="i" viewBox="0 0 24 24" style="fill:currentColor;stroke:none"><path d="M15.2 3.3a1 1 0 011.4 0l4.1 4.1a1 1 0 010 1.4l-1.2 1.2a1 1 0 01-1.1.2l-.6-.2-3.3 3.3.3 2.6a1 1 0 01-.3.8l-1 1a1 1 0 01-1.4 0l-3-3-4.2 4.2a1 1 0 01-1.4-1.4l4.2-4.2-3-3a1 1 0 010-1.4l1-1a1 1 0 01.8-.3l2.6.3 3.3-3.3-.2-.6a1 1 0 01.2-1.1z"/></svg>',
  unpin:
    '<svg class="i" viewBox="0 0 24 24"><path d="M15.5 4l4.5 4.5-1.6 1.2-3.6 3.6.3 2.9-1.4 1.4-7.4-7.4 1.4-1.4 2.9.3 3.6-3.6z"/><path d="M8.5 15.5L4 20M3 3l18 18"/></svg>',
  clock: '<svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
  xc: '<svg class="i" viewBox="0 0 24 24" style="fill:currentColor;stroke:none"><path d="M12 2.5a9.5 9.5 0 110 19 9.5 9.5 0 010-19zm-3.3 5L7.5 8.7 10.8 12l-3.3 3.3 1.2 1.2 3.3-3.3 3.3 3.3 1.2-1.2-3.3-3.3 3.3-3.3-1.2-1.2-3.3 3.3z"/></svg>',
  link: '<svg class="i" viewBox="0 0 24 24"><path d="M10 14a4 4 0 005.66 0l3-3a4 4 0 00-5.66-5.66l-1 1"/><path d="M14 10a4 4 0 00-5.66 0l-3 3a4 4 0 005.66 5.66l1-1"/></svg>',
  note: '<svg class="i" viewBox="0 0 24 24"><path d="M5 5h14v10h-7l-4 4v-4H5z"/></svg>',
  undo: '<svg class="i" viewBox="0 0 24 24"><path d="M9 7L4 12l5 5"/><path d="M4 12h10a6 6 0 010 12"/></svg>',
  grip: '<svg class="i" viewBox="0 0 24 24"><path d="M5 8h14M5 12h14M5 16h14"/></svg>',
  down: '<svg class="i" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>',
  wave: '<svg class="i" viewBox="0 0 24 24"><path d="M5 10v4M9 6v12M13 8v8M17 4v16M21 10v4"/></svg>',
  pen: '<svg class="i" viewBox="0 0 24 24"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>',
  check: '<svg class="i" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  trash:
    '<svg class="i" viewBox="0 0 24 24"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 002 2h6a2 2 0 002-2l1-12M9 7V4h6v3"/></svg>',
  x: '<svg class="i" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  mic: '<svg class="i" viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0013 0M12 17.5V21"/></svg>',
  eye: '<svg class="i" viewBox="0 0 24 24"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/></svg>',
  eyeOff:
    '<svg class="i" viewBox="0 0 24 24"><path d="M10.6 5.6A10 10 0 0112 5.5c6 0 9.5 6.5 9.5 6.5a17 17 0 01-2.6 3.4M6.6 6.6C3.9 8.3 2.5 12 2.5 12S6 18.5 12 18.5c1.9 0 3.6-.6 5-1.5M9.9 9.9a3 3 0 004.2 4.2M3 3l18 18"/></svg>',
  updown: '<svg class="i" viewBox="0 0 12 18"><path d="M2.5 6.5L6 3l3.5 3.5M2.5 11.5L6 15l3.5-3.5"/></svg>',
  more: '<svg class="i" viewBox="0 0 24 24" style="fill:currentColor;stroke:none"><circle cx="6" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="18" cy="12" r="1.8"/></svg>',
  shuffle:
    '<svg class="i" viewBox="0 0 24 24"><path d="M3 7h3.5c4.5 0 6.5 10 11 10H21M3 17h3.5c1.8 0 3-1.6 4.1-3.6M14.4 9.6C15.5 7.6 16.7 7 18 7h3M18 4l3 3-3 3M18 14l3 3-3 3"/></svg>',
};
// Recall: how much of the lyrics to hide. Letters turn into grey lines in place, so the layout never moves
const SG_HINTS = ['Full lyrics', 'Word shapes', 'First words', 'Cues only', 'Blank'];
const PEEKS = [1, 2, 3, 5]; // Settings › Recall › Peek length, in seconds
const peekSecs = () => (PEEKS.includes(+(D.prefs || {}).peek) ? +D.prefs.peek : 2);
const HOLD_MS = 350; // holding a line this long keeps it showing until you let go
// moments on screen that don't need saving: the selected word, undo steps, open menus, a drag in progress
const SG = {
  word: null,
  undo: [],
  pend: null,
  ctx: null,
  sortMenu: false,
  drag: null,
  pulse: null,
  told: false,
  sw: null,
  swOpen: null,
  noSync: false,
  rMenu: false,
  hMenu: false,
};

/* ===== Songs: small helpers ===== */
const sgId = (p) => p + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const songById = (id) => (id ? D.songs.find((s) => s.id === id) : null);
const hasLyrics = (s) => !!(s && s.sections && Array.isArray(s.order) && s.order.length);
const sgNorm = (w) => (w || '').toLowerCase().replace(/[^\p{L}\p{N}']/gu, '');
const toLines = (t) =>
  String(t || '')
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => l.split(/\s+/));
const uses = (sg, sid) => sg.order.filter((x) => x.sid === sid).length;
const occIdx = (sg, o) => sg.order.findIndex((x) => x.o === o);
function occLabel(sg, idx) {
  const lab = sg.sections[sg.order[idx].sid].label;
  const all = sg.order.filter((x) => sg.sections[x.sid].label === lab);
  if (all.length < 2) return lab;
  return lab + ' ' + sg.order.slice(0, idx + 1).filter((x) => sg.sections[x.sid].label === lab).length;
}
function checkCount(sg) {
  if (!hasLyrics(sg)) return 0;
  let n = 0;
  for (const k in sg.sections) {
    const s = sg.sections[k];
    n += s.orphans.length;
    for (const a in s.ann) if (s.ann[a].check) n++;
  }
  return n;
}
const takesOf = (id) => TAKES.filter((t) => t.songId === id).length;
// takes recorded from one place in a song (an entry in its order), oldest first
const takesAt = (id, o) => TAKES.filter((t) => t.songId === id && t.o === o);
// a section of this song is being recorded: the screen is locked to it
const recHere = (sg) => !!(rec && rec.o && sg && rec.songId === sg.id);
// Recall is on for the song on screen (not while editing)
const recallOn = () => U.sMode === 'recall' && !U.sEdit && hasLyrics(songShown());
const hintLv = () => (recallOn() ? U.sHint || 0 : 0);
// hide letters without moving them: 'shape' keeps each word's first letter, 'all' hides every letter
function maskText(t, mode) {
  let out = '',
    run = '',
    seen = false;
  const flush = () => {
    if (run) out += '<span class="hx" aria-hidden="true">' + esc(run) + '</span>';
    run = '';
  };
  for (const c of String(t)) {
    const letter = /[\p{L}\p{N}]/u.test(c);
    if (letter && (mode === 'all' || seen)) run += c;
    else {
      flush();
      out += esc(c);
    }
    if (letter) seen = true;
  }
  flush();
  return out;
}
const nTakes = (n) => n + ' take' + (n === 1 ? '' : 's');
function takeWhen(t) {
  const r = sgRel(t);
  return r.startsWith('on ') ? r.slice(3) : r.charAt(0).toUpperCase() + r.slice(1);
}
// practised means a take was recorded: in song practice now, and from a song's sections later
function lastPractised(s, map) {
  const t = map ? map[s.id] || 0 : TAKES.reduce((a, k) => (k.songId === s.id && k.created > a ? k.created : a), 0);
  return Math.max(t, +s.practised || 0) || null;
}
function practisedMap() {
  const m = {};
  TAKES.forEach((t) => {
    if (t.songId && t.created > (m[t.songId] || 0)) m[t.songId] = t.created;
  });
  return m;
}
function sgRel(t) {
  const d0 = startOfDay(new Date()),
    diff = Math.round((d0 - startOfDay(new Date(t))) / 864e5);
  if (diff <= 0) return 'today';
  if (diff === 1) return 'yesterday';
  if (diff < 7) return diff + ' days ago';
  return 'on ' + shortDate(t);
}
const practisedText = (t) => 'Practised ' + sgRel(t);
// capitalise each all-lowercase word; words that already have a capital (OPM, iPhone) are left alone
const titleCase = (t) =>
  String(t || '')
    .trim()
    .replace(/\s+/g, ' ')
    .split(' ')
    .map((w) => (w && w === w.toLowerCase() ? w.replace(/^(\P{L}*)(\p{L})/u, (m, a, b) => a + b.toUpperCase()) : w))
    .join(' ');
const songTitle = (s) => (s && s.name && s.name.trim()) || 'Untitled song';
const isEmptyMark = (a) => !a.br && !a.run && !a.up && !a.dn && !a.v && !a.nt;
function markText(a) {
  return (
    [
      a.up ? '↑' : '',
      a.dn ? '↓' : '',
      a.br ? 'Breath' : '',
      a.run ? 'Run' : '',
      a.v ? '“' + a.v + '”' : '',
      a.nt ? 'Note' : '',
    ]
      .filter(Boolean)
      .join(', ') || 'Mark'
  );
}

/* ===== Songs: checking saved songs =====
   Each song is checked on its own, so one damaged song can't affect the others. Fields this version doesn't know
   about are kept, so a backup from a newer version loses nothing. If a song's lyrics are damaged but its original
   paste is there, the lyrics are rebuilt from the paste. */
function cleanSong(x) {
  if (
    !x ||
    typeof x !== 'object' ||
    Array.isArray(x) ||
    !x.id ||
    typeof x.id !== 'string' ||
    typeof x.name !== 'string'
  )
    return null;
  const s = Object.assign({}, x);
  if ('artist' in s && typeof s.artist !== 'string') delete s.artist;
  if ('pinned' in s && typeof s.pinned !== 'boolean') delete s.pinned;
  if ('added' in s && !(+s.added > 0 && isFinite(+s.added))) delete s.added;
  if ('practised' in s && !(+s.practised > 0 && isFinite(+s.practised))) delete s.practised;
  if ('original' in s && typeof s.original !== 'string') delete s.original;
  if ('sections' in s || 'order' in s) {
    const lyr = cleanLyrics(s.sections, s.order);
    delete s.sections;
    delete s.order;
    if (lyr) Object.assign(s, lyr);
    else if (s.original) {
      const b = splitBlocks(s.original);
      if (b.length) Object.assign(s, buildLyrics(b));
    }
  }
  return s;
}
function cleanLyrics(secs, order) {
  if (!secs || typeof secs !== 'object' || Array.isArray(secs) || !Array.isArray(order)) return null;
  const sections = {},
    out = [],
    seen = new Set();
  for (const x of order) {
    if (!x || typeof x.o !== 'string' || typeof x.sid !== 'string' || seen.has(x.o)) continue;
    if (!sections[x.sid]) {
      const c = cleanSection(secs[x.sid]);
      if (!c) continue;
      sections[x.sid] = c;
    }
    seen.add(x.o);
    out.push(Object.assign({}, x));
  }
  return out.length ? { sections, order: out } : null;
}
function cleanSection(c) {
  if (!c || typeof c !== 'object' || Array.isArray(c)) return null;
  const lines = (Array.isArray(c.lines) ? c.lines : [])
    .filter(Array.isArray)
    .map((l) => l.filter((w) => typeof w === 'string' && w.trim()).map((w) => w.trim()))
    .filter((l) => l.length);
  if (!lines.length) return null;
  const ann = {};
  if (c.ann && typeof c.ann === 'object')
    for (const k in c.ann) {
      const m = /^(\d+):(\d+)$/.exec(k);
      if (!m || !lines[+m[1]] || +m[2] >= lines[+m[1]].length) continue;
      const a = cleanMark(c.ann[k]);
      if (a) ann[k] = a;
    }
  const orphans = (Array.isArray(c.orphans) ? c.orphans : [])
    .filter((o) => o && typeof o.id === 'string')
    .map((o) => ({ id: o.id, was: typeof o.was === 'string' ? o.was : '', ann: cleanMark(o.ann) }))
    .filter((o) => o.ann);
  return Object.assign({}, c, {
    label: typeof c.label === 'string' && c.label.trim() ? c.label.trim().slice(0, 30) : 'Verse',
    cue: typeof c.cue === 'string' ? c.cue.slice(0, 200) : '',
    lines,
    ann,
    orphans,
  });
}
function cleanMark(a) {
  if (!a || typeof a !== 'object' || Array.isArray(a)) return null;
  const b = Object.assign({}, a);
  ['br', 'run', 'up', 'dn', 'check'].forEach((k) => {
    if (b[k]) b[k] = 1;
    else delete b[k];
  });
  if (typeof b.v === 'string' && b.v.trim()) b.v = b.v.trim().slice(0, 20);
  else delete b.v;
  if (typeof b.nt === 'string' && b.nt.trim()) b.nt = b.nt.trim().slice(0, 200);
  else delete b.nt;
  if (typeof b.was !== 'string' || !b.check) delete b.was;
  return isEmptyMark(b) ? null : b;
}

/* ===== Songs: reading pasted lyrics =====
   Cleans the paste (links, website clutter, curly quotes), finds section labels anywhere ([Chorus], Verse 2:, PRECHORUS),
   splits a chorus that repeats itself into two, links exact repeats so marks are added once, and flags guesses. */
const LABEL_KEYS = {
  intro: 'Intro',
  verse: 'Verse',
  prechorus: 'Pre-chorus',
  prehook: 'Pre-chorus',
  chorus: 'Chorus',
  refrain: 'Chorus',
  postchorus: 'Post-chorus',
  posthook: 'Post-chorus',
  bridge: 'Bridge',
  hook: 'Hook',
  interlude: 'Interlude',
  instrumental: 'Interlude',
  tag: 'Tag',
  outro: 'Outro',
};
function labelKey(t) {
  t = t.split(/:|\s[-–—]\s/)[0];
  t = t.replace(/\s*[x×]\s*\d+\s*$/i, '').replace(/\s*\d+\s*$/, '');
  return t.toLowerCase().replace(/[\s\-–—_.]/g, '');
}
function findLabel(key) {
  if (LABEL_KEYS[key]) return LABEL_KEYS[key];
  const k = Object.keys(LABEL_KEYS)
    .sort((a, b) => b.length - a.length)
    .find((k) => key.startsWith(k));
  return k ? LABEL_KEYS[k] : null;
}
function readLabel(line) {
  const br = line.match(/^\[(.+?)\]$|^\((.+?)\)$/);
  if (br) {
    const inner = br[1] || br[2];
    const l = findLabel(labelKey(inner));
    if (l) return { label: l, guessed: false };
    if (/^\s*[x×]\s*\d+\s*$/i.test(inner) || /^\s*repeat/i.test(inner)) return null;
    return br[1] ? { label: 'Verse', guessed: true } : null;
  }
  const words = line.replace(/:$/, '').trim().split(/\s+/);
  if (words.length <= 4 && (line.endsWith(':') || (line === line.toUpperCase() && /\p{L}/u.test(line)))) {
    const l = findLabel(labelKey(line.replace(/:$/, '')));
    if (l) return { label: l, guessed: false };
  }
  if (words.length <= 3) {
    const k = labelKey(line.replace(/:$/, ''));
    if (LABEL_KEYS[k]) return { label: LABEL_KEYS[k], guessed: false };
  }
  return null;
}
const CLUTTER = [
  /^\d+\s*contributors?$/i,
  /^\d*\s*embed$/i,
  /^you might also like$/i,
  /^translations?$/i,
  /^see .+ live$/i,
  /^get tickets/i,
];
function cleanPaste(text) {
  const t = String(text || '')
    .replace(/\r/g, '')
    .replace(/[​-‍﻿]/g, '')
    .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '$1')
    .replace(/https?:\/\/\S+/g, '')
    .replace(/[‘’ʼ′`]/g, "'")
    .replace(/[“”″]/g, '"');
  let lines = t.split('\n').map((l) =>
    l
      .replace(/[ \t ]+/g, ' ')
      .trim()
      .replace(/\s*\d*Embed$/, '')
  );
  lines = lines.filter((l) => !CLUTTER.some((r) => r.test(l)));
  const first = lines.findIndex((l) => l);
  if (first > -1 && /\blyrics$/i.test(lines[first]) && lines.slice(first + 1).some((l) => l)) lines.splice(first, 1);
  return lines;
}
const sameText = (a, b) => sgNorm(a.replace(/\s+/g, '')) === sgNorm(b.replace(/\s+/g, ''));
function splitBlocks(text) {
  const lines = cleanPaste(text),
    raw = [];
  let cur = null;
  const close = () => {
    if (cur && cur.lines.length) raw.push(cur);
    cur = null;
  };
  lines.forEach((l) => {
    if (!l) {
      if (cur && cur.lines.length) close();
      return;
    }
    const lab = readLabel(l);
    if (lab) {
      close();
      cur = { lines: [], label: lab.label, guessed: lab.guessed };
      return;
    }
    if (!cur) cur = { lines: [], label: null, guessed: true };
    cur.lines.push(l);
  });
  close();
  const blocks = [];
  raw.forEach((b) => {
    const n = b.lines.length,
      h = n / 2;
    if (n >= 2 && n % 2 === 0 && sameText(b.lines.slice(0, h).join('\n'), b.lines.slice(h).join('\n'))) {
      const half = b.lines.slice(0, h).join('\n');
      blocks.push({ text: half, label: b.label, guessed: b.guessed, match: null, linked: false });
      blocks.push({ text: half, label: b.label, guessed: b.guessed, match: null, linked: false, doubled: true });
    } else blocks.push({ text: b.lines.join('\n'), label: b.label, guessed: b.guessed, match: null, linked: false });
  });
  blocks.forEach((b, i) => {
    const j = blocks.findIndex((c, k) => k < i && sameText(c.text, b.text));
    if (j > -1) {
      b.match = blocks[j].match != null ? blocks[j].match : j;
      b.linked = true;
    }
  });
  blocks.forEach((b, i) => {
    if (b.label) return;
    if (b.match != null && blocks[b.match].label && !blocks[b.match].guessed) {
      b.label = blocks[b.match].label;
      b.guessed = false;
      return;
    }
    b.label = b.match != null || blocks.some((c) => c.match === i) ? 'Chorus' : 'Verse';
    b.guessed = true;
  });
  return blocks;
}
// blocks → stored lyrics: linked repeats share one section, listed in a running order
function buildLyrics(blocks) {
  const sections = {},
    order = [],
    sidFor = [];
  blocks.forEach((b, i) => {
    if (b.match != null && b.linked && sidFor[b.match]) sidFor[i] = sidFor[b.match];
    else {
      const sid = sgId('x');
      sidFor[i] = sid;
      sections[sid] = { label: b.label, cue: '', lines: toLines(b.text), ann: {}, orphans: [] };
    }
    order.push({ o: sgId('o'), sid: sidFor[i] });
  });
  return { sections, order };
}

/* ===== Songs: marks follow their words =====
   When lyrics change, a word-level comparison moves each mark to where its word went. A mark whose word changed is
   flagged to check; one whose word was removed waits at the top of its section to be moved or removed. */
function flat(lines) {
  const t = [];
  lines.forEach((l, li) => l.forEach((w, wi) => t.push({ li, wi, w, n: sgNorm(w) })));
  return t;
}
function align(a, b) {
  const n = a.length,
    m = b.length,
    dp = Array.from({ length: n + 1 }, () => new Uint32Array(m + 1));
  for (let i = n - 1; i >= 0; i--)
    for (let j = m - 1; j >= 0; j--)
      dp[i][j] = a[i].n === b[j].n ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const ops = [];
  let i = 0,
    j = 0;
  while (i < n && j < m) {
    if (a[i].n === b[j].n) {
      ops.push(['=', i, j]);
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) ops.push(['-', i++]);
    else ops.push(['+', j++]);
  }
  while (i < n) ops.push(['-', i++]);
  while (j < m) ops.push(['+', j++]);
  return ops;
}
function relink(sec, nl) {
  const A = flat(sec.lines),
    B = flat(nl),
    ops = align(A, B),
    ann = {};
  let flagged = 0,
    dels = [],
    ins = [];
  const flush = () => {
    dels.forEach((i, k) => {
      const a = sec.ann[A[i].li + ':' + A[i].wi];
      if (!a) return;
      if (ins[k] != null) {
        const t = B[ins[k]];
        ann[t.li + ':' + t.wi] = Object.assign({}, a, { check: 1, was: a.was || A[i].w });
      } else {
        const c = Object.assign({}, a);
        delete c.check;
        delete c.was;
        sec.orphans.push({ id: sgId('r'), was: a.was || A[i].w, ann: c });
      }
      flagged++;
    });
    dels = [];
    ins = [];
  };
  ops.forEach((op) => {
    if (op[0] === '=') {
      flush();
      const a = sec.ann[A[op[1]].li + ':' + A[op[1]].wi];
      if (a) {
        const t = B[op[2]];
        ann[t.li + ':' + t.wi] = a;
      }
    } else if (op[0] === '-') dels.push(op[1]);
    else ins.push(op[1]);
  });
  flush();
  sec.ann = ann;
  sec.lines = nl.length ? nl : [['…']];
  return flagged;
}
// read the lyrics editors on screen back into the song
function applyLyrics() {
  const sg = songById(U.songId);
  if (!sg || !hasLyrics(sg)) return 0;
  let changed = false,
    flagged = 0;
  document.querySelectorAll('.lyred[data-k]').forEach((ed) => {
    const sec = sg.sections[ed.dataset.k];
    if (!sec) return;
    const nl = toLines(ed.innerText);
    if (sec.lines.map((l) => l.join(' ')).join('\n') === nl.map((l) => l.join(' ')).join('\n')) return;
    if (!changed) {
      sgSnap();
      changed = true;
    }
    flagged += relink(sec, nl);
  });
  if (changed) save();
  return flagged;
}

/* ===== Songs: forgiving search =====
   Ignores case, punctuation, apostrophes and accents; words in any order; one-letter slips in longer words.
   Matches titles and artists first, then a lyric line, then words spread across lines. */
const fold = (t) =>
  (t || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[‘’'`]/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
function near(a, b) {
  if (Math.abs(a.length - b.length) > 1) return false;
  let i = 0,
    j = 0,
    e = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) {
      i++;
      j++;
      continue;
    }
    if (++e > 1) return false;
    if (a.length > b.length) i++;
    else if (b.length > a.length) j++;
    else {
      i++;
      j++;
    }
  }
  return e + (a.length - i) + (b.length - j) <= 1;
}
function tokHit(tok, w) {
  if (w.includes(tok)) return 2;
  if (tok.length < 5 || !w || w[0] !== tok[0]) return 0;
  return near(tok, w) || near(tok, w.slice(0, tok.length)) ? 1 : 0;
}
function scoreText(text, q, toks) {
  const f = fold(text);
  if (!f) return 0;
  if (f.includes(fold(q))) return 3;
  const ws = f.split(' ');
  let typo = false;
  for (const t of toks) {
    let best = 0;
    for (const w of ws) {
      best = Math.max(best, tokHit(t, w));
      if (best === 2) break;
    }
    if (!best) return 0;
    if (best === 1) typo = true;
  }
  return typo ? 1 : 2;
}
function hlWords(text, toks) {
  if (!toks || !toks.length) return esc(text);
  return String(text)
    .split(/(\s+)/)
    .map((p) => {
      const w = fold(p);
      return w && toks.some((t) => w.split(' ').some((x) => tokHit(t, x)))
        ? '<mark class="sgmk">' + esc(p) + '</mark>'
        : esc(p);
    })
    .join('');
}
function searchSongs(q) {
  const toks = fold(q).split(' ').filter(Boolean);
  if (!toks.length) return { list: [], toks };
  const out = [];
  sortedSongs(D.songs).forEach((s, rank) => {
    const ts = Math.max(scoreText(songTitle(s), q, toks), scoreText(s.artist || '', q, toks));
    if (ts) return out.push({ s, hit: null, score: 10 + ts, rank });
    if (!hasLyrics(s)) return;
    let best = null;
    const seen = new Set(),
      lines = [];
    s.order.forEach((x, oi) => {
      if (seen.has(x.sid)) return;
      seen.add(x.sid);
      s.sections[x.sid].lines.forEach((ln) => {
        const t = ln.join(' ');
        lines.push({ t, oi });
        const sc = scoreText(t, q, toks);
        if (sc && (!best || sc > best.score)) best = { score: sc, hit: { label: occLabel(s, oi), line: t } };
      });
    });
    if (!best) {
      const ws = lines.map((l) => fold(l.t).split(' '));
      if (toks.every((t) => ws.some((w) => w.some((x) => tokHit(t, x))))) {
        let bi = 0,
          bc = -1;
        ws.forEach((w, i) => {
          const c = toks.reduce((a, t) => a + Math.max(0, ...w.map((x) => tokHit(t, x))), 0);
          if (c > bc) {
            bc = c;
            bi = i;
          }
        });
        best = { score: 0.5, hit: { label: occLabel(s, lines[bi].oi), line: lines[bi].t } };
      }
    }
    if (best) out.push({ s, hit: best.hit, score: best.score, rank });
  });
  return { list: out.sort((a, b) => b.score - a.score || a.rank - b.rank), toks };
}

/* ===== Songs: this device's preferences (sort order, recent searches). Not part of backups. ===== */
const SGP_KEY = 'vocalSongPrefs';
let SGP = null;
function sgp() {
  if (SGP) return SGP;
  let o = {};
  try {
    o = JSON.parse(localStorage.getItem(SGP_KEY) || '{}') || {};
  } catch (e) {}
  SGP = {
    sort: SG_SORTS[o.sort] ? o.sort : 'recent',
    recent: Array.isArray(o.recent) ? o.recent.filter((x) => typeof x === 'string').slice(0, 5) : [],
  };
  return SGP;
}
function saveSGP() {
  try {
    localStorage.setItem(SGP_KEY, JSON.stringify(sgp()));
  } catch (e) {}
}
function addRecent(q) {
  q = (q || '').trim();
  if (!q) return;
  const p = sgp();
  p.recent = [q].concat(p.recent.filter((r) => r.toLowerCase() !== q.toLowerCase())).slice(0, 5);
  saveSGP();
}
function sortedSongs(list) {
  const k = sgp().sort,
    pm = practisedMap();
  return list
    .slice()
    .sort((a, b) =>
      k === 'az'
        ? songTitle(a).localeCompare(songTitle(b), 'en-GB', { sensitivity: 'base' })
        : k === 'added'
          ? (b.added || 0) - (a.added || 0)
          : (lastPractised(b, pm) || b.added || 0) - (lastPractised(a, pm) || a.added || 0)
    );
}
const pinnedSongs = () => sortedSongs(D.songs.filter((s) => s.pinned));

/* ===== Songs: where things are on screen ===== */
const songOpenInPane = () => U.tab === 'songs' && !U.view && split();
const songShown = () => (U.view === 'lyr' || songOpenInPane()) && songById(U.songId);
const searching = () => (split() ? !!(U.sq || '').trim() : U.sFocus);
function sgFixSel() {
  if (songById(U.songId) || !D.songs.length) return;
  const p = pinnedSongs(),
    r = sortedSongs(D.songs.filter((s) => !s.pinned));
  U.songId = (p[0] || r[0]).id;
}
function openSong(id, from) {
  if (!songById(id)) return;
  if (rec && rec.o && rec.songId !== id) return toast('Stop recording first');
  if (U.sEdit) sgEndEdit(true);
  if (U.songId !== id) U.sSec = null;
  U.sMode = 'practise';
  if (split()) {
    const was = U.tab === 'songs' && !U.view;
    U.songId = id;
    if (was) {
      rerender();
      const p = document.querySelector('.sgpane');
      if (p && p.getBoundingClientRect().top < 0) window.scrollTo(0, 0);
    } else
      go(() => {
        U.tab = 'songs';
        U.view = null;
      });
    return;
  }
  go(() => {
    U.sRet = from || null;
    U.songId = id;
    U.tab = 'songs';
    U.view = 'lyr';
  });
}

/* ===== Songs: the list ===== */
function scrSongs() {
  if (split()) {
    sgFixSel();
    const sg = songById(U.songId);
    return (
      '<div class="split sgsplit"><div class="sl sgcol">' +
      songListCol() +
      '</div><div class="sgpane">' +
      (sg
        ? songBody(sg, true)
        : '<div class="sgempty">' + SGI.wave + '<b>No song open</b>Add a song to see its lyrics here.</div>') +
      '</div></div>'
    );
  }
  return songListCol();
}
function songListCol() {
  const sp = split(),
    n = U.sSel.length,
    all = D.songs.length && n === D.songs.length;
  let h = '';
  if (sp) {
    h += U.sList
      ? '<div class="sgph"><button class="txtbtn glass" data-a="sgSelAll">' +
        (all ? 'Deselect all' : 'Select all') +
        '</button><b class="sgphc">' +
        (n ? n + ' selected' : 'Select songs') +
        '</b><button class="txtbtn glass tinted" data-a="sgListDone">Done</button></div>'
      : '<div class="sgph"><h1>Songs</h1>' +
        (D.songs.length ? '<button class="txtbtn glass" data-a="sgListEdit">Edit</button>' : '') +
        '<button class="circ glass" data-a="sgNew" aria-label="New song">' +
        ICON.plus +
        '</button></div>';
    if (D.songs.length && !U.sList)
      h +=
        '<label class="sfield inl">' +
        SGI.search +
        '<input id="sgqi" class="sgq" type="search" placeholder="Search songs" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="search" aria-label="Search songs" value="' +
        esc(U.sq || '') +
        '"><button class="sclear" data-a="sgQClear" aria-label="Clear search"' +
        ((U.sq || '').trim() ? '' : ' hidden') +
        '>' +
        SGI.xc +
        '</button></label>';
  } else if (!U.sFocus) h += '<h1>' + (U.sList ? (n ? n + ' selected' : 'Select songs') : 'Songs') + '</h1>';
  if (!D.songs.length)
    return (
      h +
      '<div class="sgempty">' +
      SGI.wave +
      '<b>Add your first song</b>Paste the lyrics and the sections are labelled for you.<div style="margin-top:18px"><button class="cta ink" data-a="sgNew" style="max-width:260px;margin:0 auto">New song</button></div></div>'
    );
  return h + '<div id="slist">' + songListHTML() + '</div>';
}
function songListHTML() {
  if (searching()) return searchHTML();
  const pinned = pinnedSongs(),
    rest = sortedSongs(D.songs.filter((s) => !s.pinned)),
    pm = practisedMap();
  let h = '';
  if (pinned.length)
    h +=
      '<div class="hdr">Pinned</div><div class="grp sgrp">' +
      pinned.map((s) => songRowHTML(s, null, null, pm)).join('') +
      '</div>';
  if (rest.length)
    h +=
      '<div class="hdr"><button class="hdrsort" id="hdrsort" data-a="sgSortMenu" aria-haspopup="menu">' +
      SG_SORTS[sgp().sort] +
      SGI.down +
      '</button></div><div class="grp sgrp">' +
      rest.map((s) => songRowHTML(s, null, null, pm)).join('') +
      '</div>';
  if (!U.sList)
    h +=
      '<p class="foot">' +
      (split()
        ? 'Swipe a song to pin or delete it, or right-click for more.'
        : 'Swipe a song to pin or delete it, or press and hold for more.') +
      '</p>';
  return h;
}
function songRowHTML(s, hit, toks, pm) {
  const n = takesOf(s.id),
    ed = U.sList,
    sel = ed && U.sSel.includes(s.id),
    lp = lastPractised(s, pm || practisedMap()),
    open = split() && !ed && U.songId === s.id;
  const meta = hit
    ? '<span class="hitline"><i>' + esc(hit.label) + ' ·</i> ' + hlWords(hit.line, toks) + '</span>'
    : '<span class="rmeta">' +
      (s.artist ? '<span>' + hlWords(s.artist, toks) + '</span><span>·</span>' : '') +
      (lp ? '<span>' + practisedText(lp) + '</span>' : '<span class="newtag">New</span>') +
      (hasLyrics(s) ? '' : '<span>·</span><span>No lyrics</span>') +
      '</span>';
  const acts =
    ed || searching()
      ? ''
      : '<div class="acts" aria-hidden="true"><button class="act pin" tabindex="-1" data-a="sgPinRow" data-k="' +
        s.id +
        '">' +
        (s.pinned ? SGI.unpin : SGI.pin) +
        (s.pinned ? 'Unpin' : 'Pin') +
        '</button><button class="act del" tabindex="-1" data-a="sgDelRow" data-k="' +
        s.id +
        '">' +
        SGI.trash +
        'Delete</button></div>';
  return (
    '<div class="srow">' +
    acts +
    '<div class="rowc' +
    (open ? ' sel' : '') +
    (SG.ctx === s.id ? ' lifted' : '') +
    '" data-a="' +
    (ed ? 'sgToggle' : 'sgOpen') +
    '" data-k="' +
    s.id +
    '" role="button" tabindex="0" aria-label="' +
    esc(songTitle(s)) +
    (s.pinned ? ', pinned' : '') +
    '">' +
    (ed ? '<span class="selc' + (sel ? ' on' : '') + '">' + (sel ? SGI.check : '') + '</span>' : '') +
    '<span class="rtxt"><b>' +
    hlWords(songTitle(s), toks) +
    '</b>' +
    meta +
    '</span>' +
    (n && !ed && !hit ? '<span class="rright" aria-label="' + n + ' takes">' + ICON.mic + n + '</span>' : '') +
    (ed ? '' : chev) +
    '</div></div>'
  );
}
function searchHTML() {
  const q = (U.sq || '').trim();
  if (!q) {
    const rc = sgp().recent;
    if (!rc.length) return '<p class="note" style="margin-top:8px">Search titles, artists and lyrics.</p>';
    return (
      '<div class="hdr sghdr"><span>Recent</span><button data-a="sgClearRecent">Clear</button></div><div class="grp">' +
      rc
        .map(
          (r) =>
            '<div class="recent"><button class="rtxt2" data-a="sgRecent" data-v="' +
            esc(r) +
            '">' +
            SGI.clock +
            '<span>' +
            esc(r) +
            '</span></button><button class="rx" data-a="sgRmRecent" data-v="' +
            esc(r) +
            '" aria-label="Remove ' +
            esc(r) +
            '">' +
            SGI.x +
            '</button></div>'
        )
        .join('') +
      '</div>'
    );
  }
  const res = searchSongs(q),
    list = res.list;
  if (!list.length)
    return (
      '<div class="sgempty">' +
      SGI.search +
      '<b>No results for “' +
      esc(q) +
      '”</b>Check the spelling or try a different line.</div>'
    );
  const pm = practisedMap();
  return (
    '<div class="hdr">' +
    list.length +
    ' song' +
    (list.length > 1 ? 's' : '') +
    '</div><div class="grp sgrp">' +
    list.map((r) => songRowHTML(r.s, r.hit, res.toks, pm)).join('') +
    '</div>'
  );
}
// redraw just the list, so typing in the search field keeps the keyboard up
function updateSongList() {
  const l = $('slist');
  if (l) l.innerHTML = songListHTML();
  document.querySelectorAll('.sgq').forEach((i) => {
    const c = i.parentNode.querySelector('.sclear');
    if (c) c.hidden = !(U.sq || '').trim();
  });
  const b = $('sgbar');
  if (b) b.classList.toggle('hasq', !!(U.sq || '').trim());
}

/* ===== Songs: Today's pinned songs ===== */
function pinnedCard() {
  const p = pinnedSongs();
  if (!p.length) return '';
  const pm = practisedMap();
  return (
    '<div class="hdr">Pinned songs</div><div class="grp">' +
    p
      .map((s) => {
        const lp = lastPractised(s, pm);
        return (
          '<button class="row" data-a="sgOpen" data-k="' +
          s.id +
          '" data-v="today"><span class="lbl">' +
          esc(songTitle(s)) +
          '<small>' +
          (s.artist ? esc(s.artist) + ' · ' : '') +
          (lp ? practisedText(lp) : 'Not practised yet') +
          '</small></span>' +
          chev +
          '</button>'
        );
      })
      .join('') +
    '<button class="row" data-a="sgAll"><span class="lbl acc">Show all songs</span>' +
    chev +
    '</button></div>'
  );
}

/* ===== Songs: one song ===== */
function marksHTML(a) {
  return (
    (a.up ? '<span class="m">↑</span>' : '') +
    (a.dn ? '<span class="m">↓</span>' : '') +
    (a.br ? '<span class="m br" aria-label="breath">' + SG_BR + '</span>' : '') +
    (a.nt ? '<span class="m nt" aria-label="note">' + SGI.note + '</span>' : '')
  );
}
function sgWord(o, sid, li, wi, w, sec, mask) {
  const a = sec.ann[li + ':' + wi] || {},
    s = SG.word,
    ed = U.sEdit === 'annotate';
  const hit = ed && s && s.sid === sid && s.li === li && s.wi === wi,
    on = hit && s.o === o,
    echo = hit && !on;
  const pl = SG.pulse && SG.pulse.sid === sid && SG.pulse.li === li && SG.pulse.wi === wi && SG.pulse.o !== o;
  return (
    '<span class="w' +
    (a.run ? ' run' : '') +
    (a.check && ed ? ' chk' : '') +
    (on ? ' on' : '') +
    (echo ? ' echo' : '') +
    (pl ? ' pulse' : '') +
    '"' +
    (on ? ' id="sgselw"' : '') +
    (ed
      ? ' role="button" tabindex="0" data-a="sgWord" data-o="' +
        o +
        '" data-k="' +
        sid +
        '" data-li="' +
        li +
        '" data-wi="' +
        wi +
        '"'
      : '') +
    '>' +
    (a.v ? '<span class="v">' + (mask === 'all' ? maskText(a.v, 'all') : esc(a.v)) + '</span>' : '') +
    (mask ? maskText(w, mask) : esc(w)) +
    '</span>' +
    marksHTML(a)
  );
}
function sgSection(sg, idx) {
  const { o, sid } = sg.order[idx],
    sec = sg.sections[sid],
    linked = uses(sg, sid) > 1,
    ed = U.sEdit === 'annotate';
  // Practise and Perform: tap a section to select it, then record it or hear its takes
  const recOn = recHere(sg),
    tap = !U.sEdit && !rec,
    sel = !U.sEdit && (recOn ? rec.o === o : U.sSec === o),
    n = U.sEdit ? 0 : takesAt(sg.id, o).length;
  let h =
    '<section class="sgsec' +
    (tap ? ' tap' : '') +
    (sel ? ' sel' : '') +
    (sel && recOn ? ' recording' : '') +
    '" data-o="' +
    o +
    '" aria-label="' +
    esc(occLabel(sg, idx)) +
    '"' +
    (tap ? ' data-a="sgSec" data-k="' + o + '" tabindex="0" aria-current="' + (sel ? 'true' : 'false') + '"' : '') +
    '><div class="sghead"><span class="sglab">' +
    esc(occLabel(sg, idx)) +
    (linked ? SGI.link : '') +
    '</span>';
  if (ed)
    h +=
      '<span class="sgbtns"><button class="sgpill sm" data-a="sgCue" data-k="' +
      sid +
      '">' +
      (sec.cue ? 'Edit cue' : '+ Cue') +
      '</button>' +
      (linked ? '<button class="sgpill sm" data-a="sgUnlink" data-k="' + o + '">Unlink</button>' : '') +
      '</span>';
  else if (n && !sel) h += '<span class="shared">' + nTakes(n) + '</span>';
  h += '</div>';
  if (ed)
    sec.orphans.forEach((op) => {
      h +=
        '<div class="sgwarn"><span>' +
        esc(markText(op.ann)) +
        ' was on “' +
        esc(op.was) +
        '”, which was removed</span><span class="sgbtns"><button class="sgpill sm" data-a="sgOMove" data-k="' +
        sid +
        '" data-v="' +
        op.id +
        '">Move</button><button class="sgpill sm" data-a="sgORemove" data-k="' +
        sid +
        '" data-v="' +
        op.id +
        '">Remove</button></span></div>';
    });
  // Recall: 1 word shapes, 2 first words, 3 cues only, 4 blank. Marks stay visible
  const lv = hintLv(),
    mk = (wi) => (!lv ? null : lv === 1 ? 'shape' : lv === 2 && wi === 0 ? null : 'all'),
    peek = lv ? ' role="button" tabindex="0" aria-label="Peek at this line"' : '';
  if (sec.cue) h += '<p class="sgcue">' + (lv >= 4 ? maskText(sec.cue, 'all') : esc(sec.cue)) + '</p>';
  h += '<div class="sglines">';
  sec.lines.forEach((ln, li) => {
    const hasv = ln.some((w, wi) => (sec.ann[li + ':' + wi] || {}).v);
    h +=
      '<p class="sgl' +
      (hasv ? ' hasv' : '') +
      (lv ? ' rl' : '') +
      '" data-o="' +
      o +
      '" data-li="' +
      li +
      '"' +
      peek +
      '>' +
      ln.map((w, wi) => sgWord(o, sid, li, wi, w, sec, mk(wi))).join(' ') +
      '</p>';
    ln.forEach((w, wi) => {
      const a = sec.ann[li + ':' + wi];
      if (a && a.nt)
        h +=
          '<p class="sgnote' +
          (lv ? ' rl' : '') +
          '"' +
          peek +
          '>' +
          SGI.note +
          '<span>' +
          (lv >= 2 ? maskText(a.nt, 'all') : esc(a.nt)) +
          '</span></p>';
    });
  });
  h += '</div>';
  if (sel && !rec)
    h +=
      '<div class="sgrecp">' +
      (n ? '<button class="sgpill" data-a="sgTakes" data-k="' + o + '">' + nTakes(n) + '</button>' : '') +
      '<button class="sgpill blue" data-a="sgRec" data-k="' +
      o +
      '">' +
      SGI.mic +
      'Record</button></div>';
  return h + '</section>';
}
function lyricsEditHTML(sg) {
  const seen = [];
  let h = '';
  sg.order.forEach((x) => {
    if (seen.includes(x.sid)) return;
    seen.push(x.sid);
    const sec = sg.sections[x.sid],
      n = uses(sg, x.sid);
    const body = sec.lines
      .map(
        (ln, li) =>
          '<div>' +
          ln.map((w, wi) => (sec.ann[li + ':' + wi] ? '<span class="mk">' + esc(w) + '</span>' : esc(w))).join(' ') +
          '</div>'
      )
      .join('');
    h +=
      '<section class="sgsec"><div class="sghead"><button class="sglbl" data-a="sgLabel" data-k="' +
      x.sid +
      '">' +
      esc(sec.label) +
      SGI.down +
      '</button>' +
      (n > 1 ? '<span class="shared">' + SGI.link + ' Used ' + n + ' times</span>' : '') +
      '</div><div class="lyred" contenteditable="true" spellcheck="false" autocapitalize="sentences" data-k="' +
      x.sid +
      '" role="textbox" aria-multiline="true" aria-label="' +
      esc(sec.label) +
      ' lyrics">' +
      body +
      '</div></section>';
  });
  return h + '<p class="foot">Linked sections are written once and shown wherever they repeat.</p>';
}
// the controls for a song: in the top bar on iPhone, at the top of the song on iPad and Mac
function songControls(sg) {
  if (U.sEdit)
    return {
      l:
        '<button class="circ glass" data-a="sgUndo" aria-label="Undo"' +
        (SG.undo.length ? '' : ' disabled') +
        '>' +
        SGI.undo +
        '</button>',
      t:
        '<div class="seg sgseg" role="tablist"><span class="knob" aria-hidden="true"></span>' +
        [
          ['annotate', 'Annotate'],
          ['lyrics', 'Lyrics'],
        ]
          .map(
            (x) =>
              '<button role="tab" data-a="sgEditMode" data-v="' +
              x[0] +
              '" class="' +
              (U.sEdit === x[0] ? 'on' : '') +
              '" aria-selected="' +
              (U.sEdit === x[0]) +
              '">' +
              x[1] +
              '</button>'
          )
          .join('') +
        '</div>',
      r: '<button class="circ glass tinted" data-a="sgDone" aria-label="Done">' + SGI.check + '</button>',
    };
  if (recHere(sg)) {
    const i = occIdx(sg, rec.o);
    return { l: '', t: '', r: '', rec: 'Recording' + (i < 0 ? '' : ' ' + occLabel(sg, i)) };
  }
  const cc = checkCount(sg);
  return {
    l: '',
    t: '',
    r: hasLyrics(sg)
      ? '<button class="circ glass" data-a="sgEdit" aria-label="Edit' +
        (cc ? ', ' + cc + ' mark' + (cc > 1 ? 's' : '') + ' to check' : '') +
        '">' +
        SGI.pen +
        (cc ? '<span class="sgbadge">' + cc + '</span>' : '') +
        '</button>'
      : '',
  };
}
function songViewBar() {
  const sg = songById(U.songId);
  if (!sg) return { l: '', t: '', r: '' };
  const c = songControls(sg);
  if (U.sEdit) return { l: c.l, t: c.t, r: c.r, tabs: true, always: true };
  if (c.rec) return { l: '', t: '<span class="rechead">' + esc(c.rec) + '</span>', r: '', always: true };
  return {
    l: '<button class="circ glass" data-a="sgBack" aria-label="Back">' + ICON.back + '</button>',
    t: esc(songTitle(sg)),
    r: c.r,
  };
}
function songListBar() {
  if (U.sFocus) return { l: '', t: 'Search songs', r: '', always: true };
  if (U.sList) {
    const n = U.sSel.length,
      all = D.songs.length && n === D.songs.length;
    return {
      l: '<button class="txtbtn glass" data-a="sgSelAll">' + (all ? 'Deselect all' : 'Select all') + '</button>',
      t: n ? n + ' selected' : 'Select songs',
      r: '<button class="txtbtn glass tinted" data-a="sgListDone">Done</button>',
      always: true,
    };
  }
  return {
    l: '',
    t: 'Songs',
    r:
      (D.songs.length ? '<button class="txtbtn glass" data-a="sgListEdit">Edit</button>' : '') +
      '<button class="circ glass" data-a="sgNew" aria-label="New song">' +
      ICON.plus +
      '</button>',
  };
}
function scrSongView() {
  const sg = songById(U.songId);
  if (!sg) return '<div class="sgempty"><b>This song was deleted.</b></div>';
  return songBody(sg, false);
}
function songBody(sg, inPane) {
  const ed = U.sEdit;
  let h = '';
  if (inPane) {
    const c = songControls(sg);
    h += ed
      ? '<div class="sgph sgedit">' + c.l + '<span class="sgphc">' + c.t + '</span>' + c.r + '</div>'
      : '<div class="sgph"><h1>' +
        esc(songTitle(sg)) +
        '</h1>' +
        (c.rec ? '<span class="rechead">' + esc(c.rec) + '</span>' : c.r) +
        '</div>';
  } else h += '<h1>' + esc(songTitle(sg)) + '</h1>';
  if (sg.artist && !ed) h += '<p class="sgart">' + esc(sg.artist) + '</p>';
  if (!hasLyrics(sg))
    return (
      h +
      '<div class="sgempty">' +
      SGI.note +
      '<b>No lyrics yet</b>Paste the lyrics to label the sections and add marks.<div style="margin-top:18px"><button class="cta ink" data-a="sgAddLyrics" data-k="' +
      sg.id +
      '" style="max-width:260px;margin:0 auto">Add lyrics</button></div></div>' +
      practiceRow(sg)
    );
  if (!ed)
    h +=
      '<div class="sgmodes' +
      (recHere(sg) ? ' locked" aria-disabled="true' : '') +
      '"><div class="seg sgseg" role="tablist"><span class="knob" aria-hidden="true"></span>' +
      [
        ['practise', 'Practise'],
        ['recall', 'Recall'],
        ['perform', 'Perform'],
      ]
        .map(
          (x) =>
            '<button role="tab" data-a="sgMode" data-v="' +
            x[0] +
            '" class="' +
            (U.sMode === x[0] ? 'on' : '') +
            '" aria-selected="' +
            (U.sMode === x[0]) +
            '">' +
            x[1] +
            '</button>'
        )
        .join('') +
      '</div>' +
      (U.sMode === 'practise' ? '<button class="sgpill" data-a="sgKey">Key</button>' : '') +
      (U.sMode === 'recall'
        ? '<button class="circ glass sgrbtn" id="sgrbtn" data-a="sgRMenu" aria-label="Recall options" aria-haspopup="menu">' +
          SGI.more +
          '</button>'
        : '') +
      '</div>' +
      (U.sMode === 'recall' && (U.sHint || U.sOrder === 'end')
        ? '<p class="sgsub">' +
          (U.sOrder === 'end' ? 'Working from the end. ' : '') +
          (U.sHint ? 'Tap a line to peek. Tap a heading to record.' : '') +
          '</p>'
        : '');
  else
    h +=
      '<p class="sgsub">' +
      (ed === 'annotate'
        ? SG.pend
          ? 'Tap the word to move the mark to.'
          : 'Tap a word to mark it. Hold a section to move it.'
        : 'Marked words are highlighted. If you change one, its mark is flagged to check.') +
      '</p>';
  if (ed === 'lyrics') return h + lyricsEditHTML(sg);
  if (SG.drag)
    return (
      h +
      '<div class="creo">' +
      sg.order
        .map((x, i) => {
          const sec = sg.sections[x.sid];
          return (
            '<div class="crow" data-o="' +
            x.o +
            '"><span class="lab">' +
            esc(occLabel(sg, i)) +
            (uses(sg, x.sid) > 1 ? SGI.link : '') +
            '</span><span class="pv">' +
            esc((sec.lines[0] || []).join(' ')) +
            '</span>' +
            SGI.grip +
            '</div>'
          );
        })
        .join('') +
      '</div>'
    );
  const perf = U.sMode === 'perform' && !ed;
  h += '<div class="sgsong' + (perf ? ' perform' : '') + (ed ? ' editing' : '') + '">';
  if (perf) h += '<p class="sgbanner">Technical marks hidden. Expressive cues only.</p>';
  const idx = sg.order.map((_, i) => i);
  if (recallOn() && U.sOrder === 'end') idx.reverse();
  idx.forEach((i) => (h += sgSection(sg, i)));
  h += '</div>';
  if (!ed && !rec && !hintLv() && !sg.order.some((x) => x.o === U.sSec))
    h += '<p class="sghint">Tap a section to record it</p>';
  if (!ed) h += practiceRow(sg);
  return h;
}
function practiceRow(sg) {
  const n = takesOf(sg.id);
  return (
    '<div class="hdr">Practice</div><div class="grp"><button class="row" data-a="sgPractise" data-k="' +
    sg.id +
    '">' +
    songTile +
    '<span class="lbl">Song practice<small>' +
    (n ? n + ' saved take' + (n > 1 ? 's' : '') + ' · record another' : 'Record a take and note how it went') +
    '</small></span>' +
    chev +
    '</button></div>'
  );
}

/* ===== Songs: sheets ===== */
const sgField = (id, lab, val, ph, extra) =>
  '<label class="sglab2" for="' +
  id +
  '">' +
  lab +
  '</label><input class="field" id="' +
  id +
  '" value="' +
  esc(val || '') +
  '" placeholder="' +
  esc(ph) +
  '" autocomplete="off" ' +
  (extra || '') +
  '>';
function songSheet(s) {
  const sd = U.sd || {},
    sg = songById(U.songId);
  if (s === 'sgNew') return newSongSheet();
  if (s === 'sgLabel') {
    const cur = sd.draft
      ? ((U.sDraft && U.sDraft.blocks && U.sDraft.blocks[sd.i]) || {}).label
      : sg && sg.sections && sg.sections[sd.k] && sg.sections[sd.k].label;
    if (!cur) return '';
    return sheetWrap(
      'Section label',
      '<div class="grp">' +
        SG_LABELS.map(
          (l) =>
            '<button class="row" data-a="sgPick" data-v="' +
            l +
            '"><span class="lbl' +
            (l === cur ? ' acc' : '') +
            '">' +
            l +
            '</span>' +
            (l === cur ? '<span class="acc">' + ICON.check + '</span>' : '') +
            '</button>'
        ).join('') +
        '</div>'
    );
  }
  if (s === 'sgKey') {
    const rows = [
      ['<span class="m br">' + SG_BR + '</span>', 'Breath', 'Take a breath after this word'],
      ['<span class="w run">ooh</span>', 'Run', 'A run or riff on this word'],
      ['<span class="m">↑</span>', 'Higher', 'Aim the pitch up here'],
      ['<span class="m">↓</span>', 'Lower', 'Aim the pitch down here'],
      ['<span class="sgvk">ah</span>', 'Sing as', 'The vowel shape to aim for'],
      ['<span class="m nt">' + SGI.note + '</span>', 'Note', 'Your own reminder, shown under the line'],
      ['<span class="mut">' + SGI.link + '</span>', 'Linked', 'A section shared with its repeats'],
    ];
    return sheetWrap(
      'Marks key',
      '<div class="grp">' +
        rows
          .map(
            (r) =>
              '<div class="row sgkey"><span class="g">' +
              r[0] +
              '</span><span class="lbl">' +
              r[1] +
              '<small>' +
              r[2] +
              '</small></span></div>'
          )
          .join('') +
        '</div><p class="foot">Add or change marks with the pencil.</p>'
    );
  }
  if (s === 'sgTakes') return takesSheet(sd);
  if (!sg && s !== 'sgDel' && s !== 'sgPinFull' && s !== 'sgRename') return '';
  if (s === 'sgCue') {
    const sec = hasLyrics(sg) && sg.sections[sd.k];
    if (!sec) return '';
    return sheetWrap(
      'Expressive cue',
      '<p class="note">The feeling or intention for this section. Shown in Perform.</p><input class="field" id="sgCueIn" maxlength="200" value="' +
        esc(sec.cue) +
        '" placeholder="Open, hopeful" autocomplete="off"><div style="margin-top:14px"><button class="cta" data-a="sgSaveCue">Save cue</button></div>'
    );
  }
  const a = sgCurMark() || {};
  if (s === 'sgVowel')
    return sheetWrap(
      'Sing it as',
      '<p class="note">The vowel shape to aim for, shown above the word.</p><input class="field" id="sgVIn" maxlength="20" value="' +
        esc(a.v || '') +
        '" placeholder="ah" autocomplete="off" autocapitalize="none"><div style="margin-top:14px"><button class="cta" data-a="sgSaveVowel">Save</button></div>' +
        (a.v ? '<button class="ghost" data-a="sgClearVowel" style="color:var(--danger)">Remove</button>' : '')
    );
  if (s === 'sgNote')
    return sheetWrap(
      'Note',
      '<p class="note">A reminder for this word, shown under the line.</p><textarea class="field" id="sgNIn" maxlength="200" placeholder="Breath runs out before the end">' +
        esc(a.nt || '') +
        '</textarea><div style="margin-top:14px"><button class="cta" data-a="sgSaveNote">Save note</button></div>' +
        (a.nt ? '<button class="ghost" data-a="sgUnnote" style="color:var(--danger)">Remove note</button>' : '')
    );
  if (s === 'sgUnlink') {
    const i = hasLyrics(sg) ? occIdx(sg, sd.k) : -1;
    if (i < 0) return '';
    return sheetWrap(
      'Unlink this section?',
      '<p class="note">' +
        esc(occLabel(sg, i)) +
        ' gets its own copy of the lyrics and marks. Changes to it will no longer affect the other ' +
        esc(sg.sections[sg.order[i].sid].label.toLowerCase()) +
        ' sections. This can’t be linked back.</p><button class="cta" data-a="sgDoUnlink">Unlink</button><button class="ghost" data-a="close">Cancel</button>'
    );
  }
  if (s === 'sgPinFull') {
    const w = songById(sd.k);
    if (!w) return '';
    return sheetWrap(
      'Pinned is full',
      '<p class="note">You can pin up to ' +
        MAXPIN +
        ' songs. Unpin one to make room for “' +
        esc(songTitle(w)) +
        '”.</p><div class="grp">' +
        pinnedSongs()
          .map(
            (x) =>
              '<div class="row"><span class="lbl">' +
              esc(songTitle(x)) +
              '</span><button class="sgpill sm" data-a="sgSwapPin" data-k="' +
              x.id +
              '">Unpin</button></div>'
          )
          .join('') +
        '</div>'
    );
  }
  if (s === 'sgRename') {
    const r = songById(sd.k);
    if (!r) return '';
    return sheetWrap(
      'Rename song',
      sgField('sgRenIn', 'Title', r.name, 'Song title', 'maxlength="80" autocapitalize="words"') +
        sgField(
          'sgRenArt',
          'Artist (optional)',
          r.artist || '',
          'Who sings it',
          'maxlength="80" autocapitalize="words"'
        ) +
        '<div style="margin-top:16px"><button class="cta" data-a="sgSaveRename">Save</button></div>'
    );
  }
  if (s === 'sgDel') {
    const list = D.songs.filter((x) => (sd.ids || []).includes(x.id));
    if (!list.length) return '';
    const r = list.reduce((n, x) => n + takesOf(x.id), 0),
      one = list.length === 1;
    return sheetWrap(
      one ? 'Delete “' + esc(songTitle(list[0])) + '”?' : 'Delete ' + list.length + ' songs?',
      '<p class="note">' +
        (one ? 'Its' : 'Their') +
        ' lyrics' +
        (r ? ', marks and ' + r + ' recording' + (r > 1 ? 's' : '') : ' and marks') +
        ' will be deleted. Song practice already logged stays in Progress. This can’t be undone.</p><button class="cta red" data-a="sgDoDel">Delete' +
        (one ? '' : ' ' + list.length + ' songs') +
        '</button><button class="ghost" data-a="close">Cancel</button>',
      one ? 'Delete song' : 'Delete songs'
    );
  }
  return '';
}
// the takes for one place in the song: straight after recording, or from its "N takes" pill
function takeRowHTML(t, tag) {
  const n = noteStr(t.note);
  return (
    '<div class="row sgtake"><button class="ibtn acc" data-a="playTake" data-k="' +
    t.id +
    '" aria-label="' +
    (playingId === t.id ? 'Pause' : 'Play') +
    ' take">' +
    (playingId === t.id ? ICON.pause : ICON.play) +
    '</button><button class="lbl tk" data-a="takeNote" data-k="' +
    t.id +
    '" aria-label="Notes for this take">' +
    (tag ? '<span class="sgtag">' + tag + '</span>' : '') +
    '<span class="tkw">' +
    takeWhen(t.created) +
    ' · ' +
    mmss(t.len) +
    '</span>' +
    '<small class="' +
    (n ? 'acc' : '') +
    '">' +
    (n ? esc(n) : 'Add a note') +
    '</small><span class="prog"><i id="pg-' +
    t.id +
    '"></i></span></button>' +
    starBtn(t) +
    '</div>'
  );
}
const starBtn = (t) =>
  '<button class="ibtn star' +
  (t.star ? ' on' : '') +
  '" data-a="star" data-k="' +
  t.id +
  '" aria-label="' +
  (t.star ? 'Unstar' : 'Star') +
  ' take" aria-pressed="' +
  !!t.star +
  '" style="' +
  (t.star ? '' : 'color:var(--fg3)') +
  '">' +
  ICON.star +
  '</button>';
function takesSheet(sd) {
  const sg = songById(sd.k),
    i = hasLyrics(sg) ? occIdx(sg, sd.o) : -1;
  if (i < 0) return '';
  const list = takesAt(sg.id, sd.o),
    fresh = sd.fresh && list.find((t) => t.id === sd.fresh),
    first = list[0],
    latest = list[list.length - 1];
  let h = '';
  if (fresh) {
    const n = noteStr(fresh.note);
    h +=
      '<div class="newtake"><button class="playbig" data-a="playTake" data-k="' +
      fresh.id +
      '" aria-label="' +
      (playingId === fresh.id ? 'Pause' : 'Play') +
      ' new take">' +
      (playingId === fresh.id ? ICON.pause : ICON.play) +
      '</button><button class="lbl tk" data-a="takeNote" data-k="' +
      fresh.id +
      '" aria-label="Notes for the new take"><span class="sgtag">New take</span><span class="tkw">Just now · ' +
      mmss(fresh.len) +
      '</span>' +
      '<small class="' +
      (n ? 'acc' : '') +
      '">' +
      (n ? esc(n) : 'Add a note') +
      '</small><span class="prog"><i id="pg-' +
      fresh.id +
      '"></i></span></button>' +
      starBtn(fresh) +
      '</div><p class="foot sgfresh">Fresh ears help. Try listening again tomorrow.</p>';
  }
  // every starred take, then the latest and the first while they're still kept
  const rows = [];
  const add = (t) => t && t !== fresh && !rows.includes(t) && rows.push(t);
  list
    .filter((t) => t.star)
    .reverse()
    .forEach(add);
  add(latest);
  add(first);
  const tagOf = (t) =>
    [t === latest ? 'Latest' : '', t === first && list.length > 1 ? 'First' : '', t.star ? 'Starred' : '']
      .filter(Boolean)
      .join(' · ');
  if (rows.length)
    h +=
      (fresh ? '<div class="hdr">Earlier takes</div>' : '') +
      '<div class="grp">' +
      rows.map((t) => takeRowHTML(t, tagOf(t))).join('') +
      '</div>';
  if (!list.length) h += '<p class="note">No takes for this section yet.</p>';
  const more = list.length - rows.length - (fresh ? 1 : 0);
  h +=
    '<p class="foot">' +
    (more ? (more === 1 ? '1 more take' : more + ' more takes') + ' in Song practice. ' : '') +
    'Keeps the last ' +
    KEEP_TAKES +
    ' takes of this song, from any section, plus every take you star.</p><div class="sgagain"><button class="sgpill" data-a="sgRec" data-k="' +
    sd.o +
    '">' +
    SGI.mic +
    (list.length ? 'Record again' : 'Record') +
    '</button></div>';
  return sheetWrap(esc(occLabel(sg, i)), h, 'Takes for ' + occLabel(sg, i));
}
function newSongSheet() {
  const d = U.sDraft;
  if (!d) return '';
  if (d.step === 1)
    return sheetWrap(
      d.forId ? 'Add lyrics' : 'New song',
      sgField('sgTitle', 'Title', d.title, 'Song title', 'maxlength="80" autocapitalize="words"') +
        sgField('sgArtist', 'Artist (optional)', d.artist, 'Who sings it', 'maxlength="80" autocapitalize="words"') +
        '<label class="sglab2" for="sgLyr">Lyrics</label><textarea class="field sglyr" id="sgLyr" placeholder="Paste lyrics here. Leave a blank line between sections.">' +
        esc(d.text) +
        '</textarea><p class="foot">Labels like [Chorus] or Verse 2: start a new section. Blank lines split sections too.</p>' +
        (d.err ? '<p class="err">' + esc(d.err) + '</p>' : '') +
        '<div style="margin-top:14px"><button class="cta" data-a="sgSplit">Next</button></div>'
    );
  const gc = d.blocks.filter((b) => b.guessed).length;
  let h =
    '<p class="note">Tap a label to change it. Exact repeats are linked so marks only need adding once.' +
    (gc ? ' Check the ' + gc + ' marked “Guessed”.' : '') +
    '</p>';
  d.blocks.forEach((b, i) => {
    h +=
      '<div class="blk"><div class="sghead"><span class="sgbtns"><button class="sglbl" data-a="sgBlockLabel" data-k="' +
      i +
      '">' +
      esc(b.label) +
      SGI.down +
      '</button>' +
      (b.guessed ? '<span class="guess">Guessed</span>' : '') +
      '</span><span class="shared">Block ' +
      (i + 1) +
      '</span></div><pre>' +
      esc(b.text) +
      '</pre>' +
      (b.doubled
        ? '<p class="foot" style="margin:6px 0 0">Split from a section that repeated itself, so it plays twice.</p>'
        : '') +
      (b.match != null
        ? '<div class="match"><span>Same words as block ' +
          (b.match + 1) +
          '</span><button class="sgpill sm' +
          (b.linked ? ' blue' : '') +
          '" data-a="sgLink" data-k="' +
          i +
          '" aria-pressed="' +
          b.linked +
          '">' +
          SGI.link +
          (b.linked ? 'Linked' : 'Link') +
          '</button></div>'
        : '') +
      '</div>';
  });
  h +=
    '<div style="margin-top:16px"><button class="cta" data-a="sgSave">Save song</button></div><button class="ghost" data-a="sgBackStep">Back</button>';
  return sheetWrap(
    'Label sections',
    h,
    'Label sections',
    '<button class="shbtn glass ok" data-a="sgSave" aria-label="Save song">' + ICON.check + '</button>'
  );
}

/* ===== Songs: editing ===== */
function sgSnap() {
  const sg = songById(U.songId);
  if (!sg) return;
  SG.undo.push(JSON.stringify(sg));
  if (SG.undo.length > 40) SG.undo.shift();
}
function sgCurMark() {
  const w = SG.word,
    sg = songById(U.songId);
  if (!w || !hasLyrics(sg) || !sg.sections[w.sid]) return null;
  return sg.sections[w.sid].ann[w.li + ':' + w.wi] || null;
}
function setMark(fn) {
  const w = SG.word,
    sg = songById(U.songId);
  if (!w || !hasLyrics(sg) || !sg.sections[w.sid]) return;
  sgSnap();
  const s = sg.sections[w.sid],
    k = w.li + ':' + w.wi,
    a = Object.assign({}, s.ann[k] || {});
  fn(a);
  if (isEmptyMark(a)) delete s.ann[k];
  else s.ann[k] = a;
  save();
  if (uses(sg, w.sid) > 1) {
    SG.pulse = Object.assign({}, w);
    setTimeout(() => (SG.pulse = null), 950);
    if (!SG.told) {
      SG.told = true;
      const n = uses(sg, w.sid) - 1;
      setTimeout(() => toast('Also updated in ' + n + ' linked section' + (n > 1 ? 's' : '')), 50);
    }
  }
}
function selectWord(w) {
  const sg = songById(U.songId);
  if (!hasLyrics(sg) || !sg.sections[w.sid]) return;
  if (SG.pend) {
    const pm = SG.pend,
      src = sg.sections[pm.sid],
      op = src && src.orphans.find((x) => x.id === pm.id);
    SG.pend = null;
    if (op) {
      sgSnap();
      const dst = sg.sections[w.sid],
        k = w.li + ':' + w.wi;
      dst.ann[k] = Object.assign({}, dst.ann[k] || {}, op.ann);
      delete dst.ann[k].check;
      delete dst.ann[k].was;
      src.orphans = src.orphans.filter((x) => x !== op);
      save();
      SG.word = w;
      rerender();
      toast('Mark moved');
      return;
    }
  }
  const s = SG.word;
  SG.word = s && s.o === w.o && s.li === w.li && s.wi === w.wi ? null : w;
  rerender();
}
function sgEndEdit(quiet) {
  let f = 0;
  if (U.sEdit === 'lyrics') f = applyLyrics();
  U.sEdit = null;
  SG.word = null;
  SG.pend = null;
  SG.drag = null;
  save();
  if (!quiet) {
    const c = checkCount(songById(U.songId));
    toast(c ? c + ' mark' + (c > 1 ? 's' : '') + ' to check' : 'Changes saved');
  }
  return f;
}
function sgSaveDraft() {
  const d = U.sDraft;
  if (!d || !d.blocks || !d.blocks.length) return;
  const lyr = buildLyrics(d.blocks),
    title = titleCase(d.title) || 'Untitled song',
    artist = titleCase(d.artist);
  let sg = d.forId && songById(d.forId);
  if (sg) Object.assign(sg, { name: title, artist, original: d.text }, lyr);
  else {
    sg = Object.assign(
      { id: 'g_' + Date.now().toString(36), name: title, artist, added: Date.now(), pinned: false, original: d.text },
      lyr
    );
    D.songs.push(sg);
  }
  save();
  U.sDraft = null;
  U.sheet = null;
  U.sd = {};
  U.sFocus = false;
  U.sq = '';
  openSong(sg.id);
  toast(d.forId ? 'Lyrics added' : 'Song saved');
}
function togglePin(id) {
  const s = songById(id);
  if (!s) return;
  if (!s.pinned && D.songs.filter((x) => x.pinned).length >= MAXPIN) {
    U.sheet = 'sgPinFull';
    U.sd = { k: id };
    rerender();
    return;
  }
  s.pinned = !s.pinned;
  save();
  rerender();
  toast(s.pinned ? 'Pinned' : 'Unpinned');
}
async function deleteSongs(ids) {
  stopPlayback();
  D.songs = D.songs.filter((x) => !ids.includes(x.id));
  save();
  for (const t of TAKES.filter((t) => ids.includes(t.songId))) await delTake(t.id);
  if (X && ids.includes(X.song) && !rec) {
    X.song = null;
    saveDraft();
  }
  await refreshTakes();
  U.sSel = [];
  if (!D.songs.length) U.sList = false;
  if (ids.includes(U.songId)) {
    U.songId = null;
    U.sEdit = null;
    if (U.view === 'lyr') U.view = null;
  }
  U.sheet = null;
  U.sd = {};
  rerender();
  toast(ids.length > 1 ? ids.length + ' songs deleted' : 'Song deleted');
}
function endSearch() {
  U.sFocus = false;
  U.sq = '';
  const i = $('sgqb');
  if (i) {
    i.value = '';
    i.blur();
  }
  rerender();
}
function startSearch() {
  if (split()) {
    const i = $('sgqi');
    if (i) i.focus();
    return;
  }
  U.sFocus = true;
  SG.ctx = null;
  SG.sortMenu = false;
  render();
  window.scrollTo(0, 0);
  const i = $('sgqb');
  if (i) i.focus();
}
// the Songs circle beside the search field brings the tab bar back
function sgTabTap(v) {
  if (U.sFocus && !split()) {
    U.sFocus = false;
    U.sq = '';
    const i = $('sgqb');
    if (i) {
      i.value = '';
      i.blur();
    }
    if (v === 'songs') {
      tabMin = false;
      rerender();
      return true;
    }
  }
  if (U.sEdit && (v !== 'songs' || U.view === 'lyr')) sgEndEdit(true);
  return false;
}

/* ===== Songs: actions (data-a="sg…") ===== */
const SG_ACT = {
  sgOpen(el, v, k) {
    if (searching()) addRecent(U.sq);
    openSong(k, v);
  },
  sgAll() {
    U.clock = false;
    go(() => {
      U.tab = 'songs';
      U.view = null;
    });
  },
  sgBack() {
    if (U.sEdit) sgEndEdit(true);
    const r = U.sRet;
    U.sRet = null;
    go(() => {
      U.view = null;
      U.tab = r || 'songs';
    });
  },
  sgToggle(el, v, k) {
    const i = U.sSel.indexOf(k);
    if (i < 0) U.sSel.push(k);
    else U.sSel.splice(i, 1);
    rerender();
  },
  sgListEdit() {
    U.sList = true;
    U.sSel = [];
    U.sFocus = false;
    U.sq = '';
    SG.ctx = null;
    rerender();
  },
  sgListDone() {
    U.sList = false;
    U.sSel = [];
    rerender();
  },
  sgSelAll() {
    U.sSel = U.sSel.length === D.songs.length ? [] : D.songs.map((x) => x.id);
    rerender();
  },
  sgLPin() {
    const ids = U.sSel.filter(songById);
    if (!ids.length) return;
    const ap = ids.every((id) => songById(id).pinned);
    if (!ap && D.songs.filter((x) => x.pinned || ids.includes(x.id)).length > MAXPIN)
      return toast('You can pin up to ' + MAXPIN + ' songs');
    ids.forEach((id) => (songById(id).pinned = !ap));
    save();
    U.sList = false;
    U.sSel = [];
    rerender();
    toast(ap ? 'Unpinned' : 'Pinned');
  },
  sgLDel() {
    if (!U.sSel.length) return;
    U.sheet = 'sgDel';
    U.sd = { ids: U.sSel.slice() };
    rerender();
  },
  sgPinRow(el, v, k) {
    sgCloseSwipes();
    togglePin(k);
  },
  sgDelRow(el, v, k) {
    sgCloseSwipes();
    U.sheet = 'sgDel';
    U.sd = { ids: [k] };
    rerender();
  },
  sgDoDel() {
    deleteSongs((U.sd && U.sd.ids) || []);
  },
  sgSwapPin(el, v, k) {
    const a = songById(k),
      b = songById(U.sd && U.sd.k);
    if (a) a.pinned = false;
    if (b) b.pinned = true;
    save();
    U.sheet = null;
    U.sd = {};
    rerender();
    toast('Pinned');
  },
  sgCtxClose() {
    SG.ctx = null;
    rerender();
  },
  sgCtxPin() {
    const id = SG.ctx;
    SG.ctx = null;
    togglePin(id);
  },
  sgCtxRename() {
    const id = SG.ctx;
    SG.ctx = null;
    U.sheet = 'sgRename';
    U.sd = { k: id, focus: 'sgRenIn' };
    rerender();
  },
  sgCtxDel() {
    const id = SG.ctx;
    SG.ctx = null;
    U.sheet = 'sgDel';
    U.sd = { ids: [id] };
    rerender();
  },
  sgSaveRename() {
    const r = songById(U.sd && U.sd.k),
      t = titleCase(($('sgRenIn') || {}).value),
      a = titleCase(($('sgRenArt') || {}).value);
    if (r && t) {
      r.name = t;
      r.artist = a;
      save();
    }
    U.sheet = null;
    U.sd = {};
    rerender();
    if (r && t) toast('Saved');
  },
  sgSortMenu() {
    SG.sortMenu = true;
    rerender();
  },
  sgSortClose() {
    SG.sortMenu = false;
    rerender();
  },
  sgSetSort(el, v) {
    if (SG_SORTS[v]) {
      sgp().sort = v;
      saveSGP();
    }
    SG.sortMenu = false;
    rerender();
  },
  sgSearch() {
    startSearch();
  },
  sgQClear() {
    U.sq = '';
    document.querySelectorAll('.sgq').forEach((i) => (i.value = ''));
    updateSongList();
    const i = split() ? $('sgqi') : $('sgqb');
    if (i) i.focus();
  },
  sgQCancel() {
    endSearch();
  },
  sgRecent(el, v) {
    U.sq = v;
    const i = $('sgqb');
    if (i) {
      i.value = v;
      i.blur();
    }
    updateSongList();
  },
  sgRmRecent(el, v) {
    sgp().recent = sgp().recent.filter((r) => r !== v);
    saveSGP();
    updateSongList();
  },
  sgClearRecent() {
    sgp().recent = [];
    saveSGP();
    updateSongList();
  },
  sgNew() {
    U.sDraft = { step: 1, title: '', artist: '', text: '' };
    U.sheet = 'sgNew';
    U.sd = { focus: 'sgTitle' };
    SG.ctx = null;
    rerender();
  },
  sgAddLyrics(el, v, k) {
    const s = songById(k);
    if (!s) return;
    U.sDraft = { step: 1, title: s.name, artist: s.artist || '', text: '', forId: k };
    U.sheet = 'sgNew';
    U.sd = { focus: 'sgLyr' };
    rerender();
  },
  sgSplit() {
    const d = U.sDraft;
    if (!d) return;
    d.title = ($('sgTitle') || {}).value || '';
    d.artist = ($('sgArtist') || {}).value || '';
    d.text = ($('sgLyr') || {}).value || '';
    const b = splitBlocks(d.text);
    if (!b.length) {
      d.err = 'Paste some lyrics first.';
      return rerender();
    }
    d.err = '';
    d.blocks = b;
    d.step = 2;
    rerender();
    const sh = document.querySelector('.sheet');
    if (sh) sh.scrollTop = 0;
  },
  sgBackStep() {
    if (U.sDraft) U.sDraft.step = 1;
    rerender();
  },
  sgBlockLabel(el, v, k) {
    U.sheet = 'sgLabel';
    U.sd = { i: +k, draft: true, ret: { sheet: 'sgNew', sd: {} } };
    rerender();
  },
  sgLink(el, v, k) {
    const b = U.sDraft && U.sDraft.blocks[+k];
    if (b) b.linked = !b.linked;
    rerender();
  },
  sgSave() {
    sgSaveDraft();
  },
  sgSec(el, v, k) {
    if (rec || U.sEdit) return;
    U.sSec = U.sSec === k ? null : k;
    rerender();
  },
  sgRec(el, v, k) {
    const sg = songShown();
    if (!hasLyrics(sg) || occIdx(sg, k) < 0) return;
    if (rec) return toast('Stop recording first');
    if (U.sEdit) return;
    stopPlayback();
    U.sheet = null;
    U.sd = {};
    U.sSec = k;
    startRec({ songId: sg.id, o: k });
  },
  sgStop() {
    stopRec();
  },
  sgTakes(el, v, k) {
    const sg = songShown();
    if (!sg || rec) return;
    U.sheet = 'sgTakes';
    U.sd = { k: sg.id, o: k };
    rerender();
  },
  sgMode(el, v) {
    if (rec) return;
    if (U.sMode === v) return;
    segPick(el);
    U.sMode = v;
    U.sSec = null;
    SG.rMenu = SG.hMenu = false;
    if (v === 'recall') {
      // Recall always starts with the full lyrics, from the start
      U.sHint = 0;
      U.sOrder = 'start';
    }
    setTimeout(rerender, 180);
  },
  sgHint(el, v) {
    const n = Math.max(0, Math.min(SG_HINTS.length - 1, (U.sHint || 0) + +v));
    if (n === U.sHint) return;
    U.sHint = n;
    rerender();
    hxFadeIn();
  },
  sgHMenu() {
    SG.hMenu = true;
    rerender();
  },
  sgSetHint(el, v) {
    U.sHint = Math.max(0, Math.min(SG_HINTS.length - 1, +v || 0));
    SG.hMenu = false;
    rerender();
    hxFadeIn();
  },
  sgRMenu() {
    SG.rMenu = true;
    rerender();
  },
  sgMClose() {
    SG.rMenu = SG.hMenu = false;
    rerender();
  },
  sgOrder(el, v) {
    U.sOrder = v === 'end' ? 'end' : 'start';
    SG.rMenu = false;
    rerender();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  },
  sgAnywhere() {
    const sg = songShown();
    SG.rMenu = false;
    if (!hasLyrics(sg)) return rerender();
    const o = sg.order[Math.floor(Math.random() * sg.order.length)].o;
    rerender();
    scrollToSec(o);
    const el = document.querySelector('.sgsec[data-o="' + o + '"]');
    if (el) {
      el.classList.add('flash');
      setTimeout(() => el.classList.remove('flash'), 1400);
    }
    toast('Start from ' + occLabel(sg, occIdx(sg, o)));
  },
  sgKey() {
    U.sheet = 'sgKey';
    U.sd = {};
    rerender();
  },
  sgEdit() {
    if (!hasLyrics(songById(U.songId))) return;
    if (rec) return toast('Stop recording first');
    U.sSec = null;
    U.sEdit = 'annotate';
    SG.word = null;
    SG.undo = [];
    SG.pend = null;
    SG.told = false;
    rerender();
  },
  sgEditMode(el, v) {
    if (U.sEdit === v) return;
    let f = 0;
    if (U.sEdit === 'lyrics') f = applyLyrics();
    segPick(el);
    U.sEdit = v;
    SG.word = null;
    SG.pend = null;
    setTimeout(rerender, 180);
    if (f) toast(f + ' mark' + (f > 1 ? 's' : '') + ' to check');
  },
  sgDone() {
    sgEndEdit(false);
    rerender();
  },
  sgUndo() {
    if (U.sEdit === 'lyrics') applyLyrics();
    if (!SG.undo.length) return;
    const prev = JSON.parse(SG.undo.pop()),
      i = D.songs.findIndex((s) => s.id === prev.id);
    if (i > -1) D.songs[i] = prev;
    save();
    SG.word = null;
    SG.noSync = true; // the editors on screen still show the text being undone
    rerender();
    toast('Undone');
  },
  sgWord(el) {
    selectWord({ o: el.dataset.o, sid: el.dataset.k, li: +el.dataset.li, wi: +el.dataset.wi });
  },
  sgMark(el, v) {
    if (v === 'v' || v === 'nt') {
      U.sheet = v === 'v' ? 'sgVowel' : 'sgNote';
      U.sd = { focus: v === 'v' ? 'sgVIn' : 'sgNIn' };
      return rerender();
    }
    setMark((a) => {
      if (a[v]) delete a[v];
      else {
        a[v] = 1;
        if (v === 'up') delete a.dn;
        if (v === 'dn') delete a.up;
      }
    });
    rerender();
  },
  sgSaveVowel() {
    const v = (($('sgVIn') || {}).value || '').trim();
    setMark((a) => {
      if (v) a.v = v.slice(0, 20);
      else delete a.v;
    });
    closeSheet();
  },
  sgClearVowel() {
    setMark((a) => delete a.v);
    closeSheet();
  },
  sgSaveNote() {
    const n = (($('sgNIn') || {}).value || '').trim();
    setMark((a) => {
      if (n) a.nt = n.slice(0, 200);
      else delete a.nt;
    });
    closeSheet();
  },
  sgUnnote() {
    setMark((a) => delete a.nt);
    closeSheet();
  },
  sgCKeep() {
    setMark((a) => {
      delete a.check;
      delete a.was;
    });
    rerender();
  },
  sgCRemove() {
    const w = SG.word,
      sg = songById(U.songId);
    if (!w || !hasLyrics(sg) || !sg.sections[w.sid]) return;
    sgSnap();
    delete sg.sections[w.sid].ann[w.li + ':' + w.wi];
    save();
    SG.word = null;
    rerender();
  },
  sgOMove(el, v, k) {
    SG.pend = { sid: k, id: v };
    SG.word = null;
    rerender();
    toast('Tap a word to move it to');
  },
  sgORemove(el, v, k) {
    const sg = songById(U.songId),
      s = hasLyrics(sg) && sg.sections[k];
    if (!s) return;
    sgSnap();
    s.orphans = s.orphans.filter((x) => x.id !== v);
    save();
    rerender();
  },
  sgCue(el, v, k) {
    SG.word = null;
    U.sheet = 'sgCue';
    U.sd = { k, focus: 'sgCueIn' };
    rerender();
  },
  sgSaveCue() {
    const sg = songById(U.songId),
      sec = hasLyrics(sg) && sg.sections[U.sd.k];
    if (sec) {
      sgSnap();
      sec.cue = (($('sgCueIn') || {}).value || '').trim().slice(0, 200);
      save();
    }
    closeSheet();
  },
  sgLabel(el, v, k) {
    const f = applyLyrics();
    U.sheet = 'sgLabel';
    U.sd = { k };
    rerender();
    if (f) toast(f + ' mark' + (f > 1 ? 's' : '') + ' to check');
  },
  sgPick(el, v) {
    const sd = U.sd || {};
    if (sd.draft) {
      const b = U.sDraft && U.sDraft.blocks[sd.i];
      if (b) {
        b.label = v;
        b.guessed = false;
      }
    } else {
      const sg = songById(U.songId),
        sec = hasLyrics(sg) && sg.sections[sd.k];
      if (sec) {
        sgSnap();
        sec.label = v;
        save();
      }
    }
    closeSheet();
  },
  sgUnlink(el, v, k) {
    SG.word = null;
    U.sheet = 'sgUnlink';
    U.sd = { k };
    rerender();
  },
  sgDoUnlink() {
    const sg = songById(U.songId),
      x = hasLyrics(sg) && sg.order.find((y) => y.o === U.sd.k);
    if (x) {
      sgSnap();
      const sid = sgId('x');
      sg.sections[sid] = JSON.parse(JSON.stringify(sg.sections[x.sid]));
      x.sid = sid;
      save();
    }
    U.sheet = null;
    U.sd = {};
    rerender();
    if (x) toast('Unlinked');
  },
  sgPractise(el, v, k) {
    if (X && !isSong()) return toast('Finish or discard your session first');
    if (rec) return toast('Stop recording first');
    if (U.sEdit) sgEndEdit(true);
    if (!X) newSong();
    stopPlayback();
    X.song = k;
    saveDraft();
    go(() => {
      U.view = 'song';
    });
  },
};

/* ===== Songs: after drawing ===== */
function sgEnsure() {
  if ($('slayer')) return;
  const l = document.createElement('div');
  l.id = 'slayer';
  document.body.appendChild(l);
  const b = document.createElement('div');
  b.id = 'sgbar';
  b.className = 'sgbar';
  b.hidden = true;
  b.innerHTML =
    '<nav class="tabbar glass min" aria-label="Tabs"><button class="on" data-a="tab" data-v="songs" aria-label="Show tabs">' +
    SGI.music +
    'Songs</button></nav><label class="sfield glass">' +
    SGI.search +
    '<input id="sgqb" class="sgq" type="search" placeholder="Search songs" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="search" aria-label="Search songs"><button class="sclear" data-a="sgQClear" aria-label="Clear search" hidden>' +
    SGI.xc +
    '</button></label><button class="scancel" data-a="sgQCancel">Cancel</button>';
  document.body.appendChild(b);
  const vv = () => {
    const v = window.visualViewport;
    if (!v) return;
    document.documentElement.style.setProperty('--kb', Math.max(0, window.innerHeight - v.height - v.offsetTop) + 'px');
  };
  if (window.visualViewport) {
    visualViewport.addEventListener('resize', vv);
    visualViewport.addEventListener('scroll', vv);
  }
}
function slayerHTML() {
  let h = '';
  const sg = songShown();
  if (sg && U.sEdit === 'annotate' && SG.word && !U.sheet && !SG.drag) {
    const a = sgCurMark() || {};
    const MENU = [
      ['br', '<span class="m br" style="margin:0">' + SG_BR + '</span>', 'Breath'],
      ['run', '~', 'Run'],
      ['up', '↑', 'Higher'],
      ['dn', '↓', 'Lower'],
      ['v', 'Aa', 'Sing as'],
      ['nt', SGI.note, 'Note'],
    ];
    h +=
      '<div class="emenu glass" id="emenu" role="toolbar" aria-label="Marks">' +
      (a.check
        ? '<div class="chkrow"><span>Was on “' +
          esc(a.was || '') +
          '”</span><span class="sgbtns"><button class="sgpill sm" data-a="sgCKeep">Keep</button><button class="sgpill sm" data-a="sgCRemove">Remove</button></span></div>'
        : '') +
      '<div class="items">' +
      MENU.map(
        (m) =>
          '<button data-a="sgMark" data-v="' +
          m[0] +
          '" aria-pressed="' +
          !!a[m[0]] +
          '"><b>' +
          m[1] +
          '</b><span>' +
          m[2] +
          '</span></button>'
      ).join('') +
      '</div><span class="tail"></span></div>';
  }
  if (sg && recallOn() && !U.sheet && !rec) {
    if (SG.rMenu)
      h +=
        '<div class="ctxback clear" data-a="sgMClose"></div><div class="ctxmenu glass" id="rmenu" role="menu"><button role="menuitem" data-a="sgAnywhere">Start anywhere' +
        SGI.shuffle +
        '</button>' +
        [
          ['start', 'From the start'],
          ['end', 'From the end'],
        ]
          .map(
            (x) =>
              '<button role="menuitemradio" aria-checked="' +
              ((U.sOrder || 'start') === x[0]) +
              '" data-a="sgOrder" data-v="' +
              x[0] +
              '">' +
              x[1] +
              ((U.sOrder || 'start') === x[0] ? ICON.check : '<span></span>') +
              '</button>'
          )
          .join('') +
        '</div>';
    if (SG.hMenu)
      h +=
        '<div class="ctxback clear" data-a="sgMClose"></div><div class="ctxmenu glass" id="hmenu" role="menu">' +
        SG_HINTS.map(
          (l, i) =>
            '<button role="menuitemradio" aria-checked="' +
            (U.sHint === i) +
            '" data-a="sgSetHint" data-v="' +
            i +
            '">' +
            l +
            (U.sHint === i ? ICON.check : '<span></span>') +
            '</button>'
        ).join('') +
        '</div>';
  }
  const list = U.tab === 'songs' && !U.view && !U.sheet;
  if (list && SG.sortMenu)
    h +=
      '<div class="ctxback clear" data-a="sgSortClose"></div><div class="ctxmenu glass" id="sortmenu" role="menu">' +
      Object.keys(SG_SORTS)
        .map(
          (k) =>
            '<button role="menuitemradio" aria-checked="' +
            (sgp().sort === k) +
            '" data-a="sgSetSort" data-v="' +
            k +
            '">' +
            SG_SORTS[k] +
            (sgp().sort === k ? ICON.check : '<span></span>') +
            '</button>'
        )
        .join('') +
      '</div>';
  if (list && SG.ctx && songById(SG.ctx)) {
    const cs = songById(SG.ctx);
    h +=
      '<div class="ctxback" data-a="sgCtxClose"></div><div class="ctxmenu glass" id="ctxmenu" role="menu"><button role="menuitem" data-a="sgCtxPin">' +
      (cs.pinned ? 'Unpin' + SGI.unpin : 'Pin' + SGI.pin) +
      '</button><button role="menuitem" data-a="sgCtxRename">Rename' +
      SGI.pen +
      '</button><button role="menuitem" class="dng" data-a="sgCtxDel">Delete' +
      SGI.trash +
      '</button></div>';
  }
  if (list && U.sList) {
    const n = U.sSel.length,
      ap = n && U.sSel.every((id) => (songById(id) || {}).pinned);
    h +=
      '<div class="etool glass" role="toolbar" aria-label="Selected songs"><button data-a="sgLPin"' +
      (n ? '' : ' disabled') +
      '>' +
      (ap ? SGI.unpin + 'Unpin' : SGI.pin + 'Pin') +
      '</button><button class="dng" data-a="sgLDel"' +
      (n ? '' : ' disabled') +
      '>' +
      SGI.trash +
      'Delete' +
      (n ? ' (' + n + ')' : '') +
      '</button></div>';
  }
  return h;
}
function songsAfter() {
  sgEnsure();
  if (rec && rec.o && !rec.stopping) {
    const sh = songShown();
    if (!sh || sh.id !== rec.songId) {
      stopRec();
      toast('Recording stopped and saved');
    }
  }
  if (SG.ctx && !(U.tab === 'songs' && !U.view)) SG.ctx = null;
  if ((SG.rMenu || SG.hMenu) && !recallOn()) SG.rMenu = SG.hMenu = false;
  const bar = $('sgbar'),
    show = U.tab === 'songs' && !U.view && !split() && U.sFocus && !U.sheet && D.songs.length > 0;
  bar.hidden = !show;
  bar.classList.toggle('hasq', !!(U.sq || '').trim());
  const qb = $('sgqb');
  if (qb && qb.value !== (U.sq || '')) qb.value = U.sq || '';
  if (!show && document.activeElement === qb) qb.blur();
  bar.querySelector('.sclear').hidden = !(U.sq || '').trim();
  document.body.classList.toggle('sgsearch', show);
  $('slayer').innerHTML = slayerHTML();
  if (songShown()) {
    sgFit();
    sgPlaceMenu();
  }
  sgPlace('ctxmenu', '.rowc.lifted', 'row');
  sgPlace('sortmenu', '#hdrsort', 'under');
  sgPlace('rmenu', '#sgrbtn', 'under');
  sgPlaceHintMenu();
  if (U.sheet && U.sd && U.sd.focus) {
    const f = U.sd.focus;
    U.sd.focus = null;
    setTimeout(() => {
      const i = $(f);
      if (i) {
        i.focus();
        if (i.setSelectionRange && i.value) i.setSelectionRange(i.value.length, i.value.length);
      }
    }, 250);
  }
}
// one phrase per line: one size for a whole section, shrunk to fit like iOS, wrapping with a hanging indent as a last resort
function sgFit() {
  document.querySelectorAll('.sglines').forEach((box) => {
    const ls = [...box.querySelectorAll('.sgl')];
    ls.forEach((l) => {
      l.classList.remove('wrap');
      l.style.fontSize = '';
    });
    let size = 19;
    ls.forEach((l) => {
      if (l.scrollWidth > l.clientWidth + 1)
        size = Math.min(size, Math.floor(((19 * l.clientWidth) / l.scrollWidth) * 2) / 2 - 0.5);
    });
    size = Math.max(15, size);
    if (size < 19)
      ls.forEach((l) => {
        l.style.fontSize = size + 'px';
        if (l.scrollWidth > l.clientWidth + 1) l.classList.add('wrap');
      });
  });
}
function sgPlaceMenu() {
  const m = $('emenu'),
    w = $('sgselw');
  if (!m || !w) return;
  const r = w.getBoundingClientRect(),
    mw = m.offsetWidth,
    mh = m.offsetHeight,
    vw = document.documentElement.clientWidth;
  let left = r.left + r.width / 2 - mw / 2;
  left = Math.max(10, Math.min(vw - mw - 10, left));
  let top = r.top - mh - 12,
    below = false;
  if (top < 70) {
    top = r.bottom + 12;
    below = true;
  }
  m.classList.toggle('below', below);
  m.style.left = left + 'px';
  m.style.top = top + window.scrollY + 'px';
  m.style.setProperty('--tx', r.left + r.width / 2 - left + 'px');
}
// the hint level menu opens above the hint capsule
function sgPlaceHintMenu() {
  const m = $('hmenu'),
    b = $('sghname');
  if (!m || !b) return;
  const r = b.getBoundingClientRect(),
    vw = document.documentElement.clientWidth;
  m.style.position = 'fixed';
  m.style.top = Math.max(12, r.top - m.offsetHeight - 12) + 'px';
  m.style.left = Math.max(12, Math.min(vw - m.offsetWidth - 12, r.left + r.width / 2 - m.offsetWidth / 2)) + 'px';
}
// the hint capsule at the bottom in Recall: show more, the level (tap for the menu), hide more
function hintCapHTML() {
  const lv = U.sHint || 0,
    last = SG_HINTS.length - 1;
  return (
    '<div class="hcap glass" role="group" aria-label="Hints"><button class="hb" data-a="sgHint" data-v="-1" aria-label="Show more"' +
    (lv === 0 ? ' disabled' : '') +
    '>' +
    SGI.eye +
    '</button><button class="hname" id="sghname" data-a="sgHMenu" aria-haspopup="menu" aria-label="Hint level: ' +
    SG_HINTS[lv] +
    ', ' +
    (lv + 1) +
    ' of ' +
    SG_HINTS.length +
    '"><span class="hrow">' +
    SG_HINTS[lv] +
    SGI.updown +
    '</span><span class="hdots" aria-hidden="true">' +
    SG_HINTS.map((_, i) => '<i class="' + (i === lv ? 'on' : '') + '"></i>').join('') +
    '</span></button><button class="hb" data-a="sgHint" data-v="1" aria-label="Hide more"' +
    (lv === last ? ' disabled' : '') +
    '>' +
    SGI.eyeOff +
    '</button></div>'
  );
}
function sgPlace(id, anchor, how) {
  const m = $(id),
    b = document.querySelector(anchor);
  if (!m || !b) return;
  const r = b.getBoundingClientRect(),
    mh = m.offsetHeight,
    mw = m.offsetWidth,
    vw = document.documentElement.clientWidth;
  let top = r.bottom + (how === 'row' ? 8 : 6);
  if (how === 'row' && top + mh > window.innerHeight - 90) top = r.top - mh - 8;
  m.style.top = top + window.scrollY + 'px';
  m.style.left = Math.max(12, Math.min(vw - mw - 12, how === 'row' ? r.left : r.left - 8)) + 'px';
}

/* ===== Songs: swipe a row (pin or delete), press and hold (menu) ===== */
let sgSuppress = 0,
  sgLP = null;
function sgCloseSwipes() {
  document.querySelectorAll('.rowc').forEach((r) => {
    if (+r.dataset.x) {
      r.style.transform = '';
      r.dataset.x = 0;
      setTimeout(() => r.parentElement && r.parentElement.classList.remove('swp'), 360);
    }
  });
  SG.swOpen = null;
}
function sgSetX(el, x) {
  el.style.transform = x ? 'translateX(' + x + 'px)' : '';
  el.dataset.x = x;
  SG.swOpen = x ? el : null;
  if (!x)
    setTimeout(() => {
      if (!+el.dataset.x && el.parentElement) el.parentElement.classList.remove('swp');
    }, 360);
}
function sgOpenCtx(id) {
  if (SG.ctx) return;
  sgCloseSwipes();
  SG.ctx = id;
  rerender();
}
document.addEventListener('pointerdown', (e) => {
  const rc = e.target.closest && e.target.closest('.rowc');
  if (!rc || U.sList || U.sheet || SG.ctx || searching() || e.button > 0) return;
  if (SG.swOpen && SG.swOpen !== rc) sgCloseSwipes();
  SG.sw = {
    el: rc,
    id: rc.dataset.k,
    x0: e.clientX,
    y0: e.clientY,
    base: +(rc.dataset.x || 0),
    x: +(rc.dataset.x || 0),
    mode: null,
    pid: e.pointerId,
  };
  clearTimeout(sgLP);
  sgLP = setTimeout(() => {
    if (SG.sw && !SG.sw.mode) {
      SG.sw.mode = 'lp';
      sgOpenCtx(SG.sw.id);
    }
  }, 480);
});
document.addEventListener('pointermove', (e) => {
  const s = SG.sw;
  if (!s) return;
  const dx = e.clientX - s.x0,
    dy = e.clientY - s.y0;
  if (!s.mode) {
    if (Math.abs(dx) > 8 && Math.abs(dx) > Math.abs(dy)) {
      s.mode = 'swipe';
      clearTimeout(sgLP);
      s.el.classList.add('drag');
      s.el.parentElement.classList.add('swp');
      try {
        s.el.setPointerCapture(s.pid);
      } catch (err) {}
    } else if (Math.abs(dy) > 8) {
      s.mode = 'scroll';
      clearTimeout(sgLP);
    }
  }
  if (s.mode === 'swipe') {
    s.x = Math.max(-130, Math.min(280, s.base + dx));
    s.el.style.transform = 'translateX(' + s.x + 'px)';
  }
});
function sgEndSwipe() {
  clearTimeout(sgLP);
  const s = SG.sw;
  SG.sw = null;
  if (!s) return;
  if (s.mode === 'lp') {
    sgSuppress = Date.now();
    return;
  }
  if (s.mode !== 'swipe') return;
  sgSuppress = Date.now();
  s.el.classList.remove('drag');
  if (s.x > 170) {
    s.el.style.transform = 'translateX(110%)';
    setTimeout(() => togglePin(s.id), 200);
  } else if (s.x > 50) sgSetX(s.el, 88);
  else if (s.x < -44) sgSetX(s.el, -88);
  else sgSetX(s.el, 0);
}
document.addEventListener('pointerup', sgEndSwipe);
document.addEventListener('pointercancel', sgEndSwipe);
document.addEventListener('contextmenu', (e) => {
  const rc = e.target.closest && e.target.closest('.rowc');
  if (rc && !U.sList && !searching() && !U.sheet) {
    e.preventDefault();
    sgOpenCtx(rc.dataset.k);
  }
});
window.addEventListener('scroll', () => SG.swOpen && sgCloseSwipes(), { passive: true });

/* ===== Songs: hold a section in Annotate to move it ===== */
let sgDL = null,
  sgDT = null;
document.addEventListener('pointerdown', (e) => {
  if (U.sEdit !== 'annotate' || U.sheet || SG.drag || !songShown() || e.button > 0) return;
  const sec = e.target.closest && e.target.closest('.sgsec[data-o]');
  if (!sec || e.target.closest('button')) return;
  sgDL = { x0: e.clientX, y0: e.clientY, y: e.clientY, o: sec.dataset.o };
  clearTimeout(sgDT);
  sgDT = setTimeout(sgStartDrag, 450);
});
function sgStartDrag() {
  if (!sgDL) return;
  const o = sgDL.o,
    y = sgDL.y;
  sgDL = null;
  SG.word = null;
  SG.drag = { o };
  rerender();
  const rows = [...document.querySelectorAll('.crow')],
    el = rows.find((r) => r.dataset.o === o);
  if (!el) {
    SG.drag = null;
    return rerender();
  }
  const b = el.getBoundingClientRect();
  if (y < b.top || y > b.bottom) window.scrollBy(0, b.top + b.height / 2 - y);
  const b2 = el.getBoundingClientRect();
  Object.assign(SG.drag, {
    rows,
    el,
    from: rows.indexOf(el),
    to: rows.indexOf(el),
    mids: rows.map((r) => {
      const q = r.getBoundingClientRect();
      return q.top + window.scrollY + q.height / 2;
    }),
    h: b2.height + 8,
    startY: b2.top + b2.height / 2 + window.scrollY,
  });
  el.classList.add('dragging');
  sgSuppress = Date.now();
}
document.addEventListener('pointermove', (e) => {
  if (sgDL) {
    sgDL.y = e.clientY;
    if (Math.hypot(e.clientX - sgDL.x0, e.clientY - sgDL.y0) > 8) {
      clearTimeout(sgDT);
      sgDL = null;
    }
  }
  const d = SG.drag;
  if (!d || !d.el) return;
  if (e.clientY < 90) window.scrollBy(0, -6);
  else if (e.clientY > window.innerHeight - 90) window.scrollBy(0, 6);
  const y = e.clientY + window.scrollY;
  d.el.style.transform = 'translateY(' + (y - d.startY) + 'px)';
  let to = 0;
  d.mids.forEach((m, i) => {
    if (i !== d.from && m < y) to++;
  });
  d.to = to;
  d.rows.forEach((r, i) => {
    if (i === d.from) return;
    const t = i > d.from && i <= to ? -d.h : i < d.from && i >= to ? d.h : 0;
    r.style.transform = t ? 'translateY(' + t + 'px)' : '';
  });
});
function sgEndDrag() {
  clearTimeout(sgDT);
  sgDL = null;
  const d = SG.drag;
  if (!d) return;
  const sg = songById(U.songId),
    moved = d.el && d.to !== d.from && hasLyrics(sg);
  if (moved) {
    sgSnap();
    const item = sg.order.splice(d.from, 1)[0];
    sg.order.splice(d.to, 0, item);
    save();
  }
  SG.drag = null;
  sgSuppress = Date.now();
  rerender();
  if (moved) toast('Section moved');
}
document.addEventListener('pointerup', sgEndDrag);
document.addEventListener('pointercancel', sgEndDrag);
document.addEventListener(
  'touchmove',
  (e) => {
    if (SG.drag && e.cancelable) e.preventDefault();
  },
  { passive: false }
);

/* ===== Songs: taps that aren't on a button ===== */
document.addEventListener(
  'click',
  (e) => {
    // the tap that ends a swipe, a press and hold or a drag isn't a tap
    if (
      Date.now() - sgSuppress < 400 &&
      e.target.closest &&
      (e.target.closest('.rowc') || e.target.closest('.sgsong,.creo'))
    ) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    if (SG.swOpen && !(e.target.closest && e.target.closest('.act'))) {
      sgCloseSwipes();
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    // Recall: tapping a hidden line shows it for a moment, without selecting its section
    const rl = hintLv() && !U.sheet && e.target.closest && e.target.closest('.rl');
    if (rl) {
      e.preventDefault();
      e.stopPropagation();
      if (Date.now() - holdEnded > 400) peekLine(rl); // letting go of a hold hides the line rather than peeking again
      return;
    }
    const el = e.target.closest && e.target.closest('[data-a]');
    // iPhone search: tapping empty space ends an empty search, or just puts the keyboard away
    if (!el && U.sFocus && !split() && U.tab === 'songs' && !U.view && !e.target.closest('#sgbar')) {
      if (!(U.sq || '').trim()) endSearch();
      else {
        const i = $('sgqb');
        if (i) i.blur();
      }
      return;
    }
    if (!el && U.sEdit === 'annotate' && songShown() && !U.sheet) {
      // a tap near a word picks the nearest word on that line
      const line = e.target.closest('.sgl');
      if (line) {
        let best = null,
          bd = 1e9;
        line.querySelectorAll('.w').forEach((w) => {
          const r = w.getBoundingClientRect(),
            d = Math.hypot(e.clientX - (r.left + r.width / 2), (e.clientY - (r.top + r.height / 2)) * 2);
          if (d < bd) {
            bd = d;
            best = w;
          }
        });
        if (best) selectWord({ o: best.dataset.o, sid: best.dataset.k, li: +best.dataset.li, wi: +best.dataset.wi });
        return;
      }
      if (SG.word && !e.target.closest('#emenu')) {
        SG.word = null;
        rerender();
      }
    }
  },
  true
);

// changing hint level fades the pills in; nothing moves, as the letters keep their place
function hxFadeIn() {
  document.body.classList.remove('hxin');
  void document.body.offsetWidth;
  document.body.classList.add('hxin');
  clearTimeout(hxFadeIn.t);
  hxFadeIn.t = setTimeout(() => document.body.classList.remove('hxin'), 400);
}
// only the tapped line shows; tapping it again while it shows starts its time again
function endPeeks(except) {
  document.querySelectorAll('.rl.peeking').forEach((x) => {
    if (x === except) return;
    clearTimeout(x._peek);
    x.classList.remove('peeking', 'held');
  });
}
function peekLine(ln) {
  endPeeks(ln);
  ln.classList.add('peeking');
  clearTimeout(ln._peek);
  ln._peek = setTimeout(() => ln.classList.remove('peeking'), peekSecs() * 1000);
}
// hold a line to keep it showing until you let go
let PH = null,
  holdEnded = 0;
document.addEventListener(
  'pointerdown',
  (e) => {
    if (PH) clearTimeout(PH.t);
    PH = null;
    if (e.button || !hintLv() || U.sheet) return;
    const ln = e.target.closest && e.target.closest('.rl');
    if (!ln) return;
    PH = { ln, x: e.clientX, y: e.clientY, on: false };
    PH.t = setTimeout(() => {
      if (!PH || PH.ln !== ln) return;
      PH.on = true;
      endPeeks(ln);
      clearTimeout(ln._peek);
      ln.classList.add('peeking', 'held');
    }, HOLD_MS);
  },
  true
);
document.addEventListener(
  'pointermove',
  (e) => {
    if (PH && !PH.on && Math.hypot(e.clientX - PH.x, e.clientY - PH.y) > 10) {
      clearTimeout(PH.t);
      PH = null;
    }
  },
  true
);
function holdEnd() {
  if (!PH) return;
  clearTimeout(PH.t);
  if (PH.on) {
    PH.ln.classList.remove('peeking', 'held');
    holdEnded = Date.now();
  }
  PH = null;
}
['pointerup', 'pointercancel'].forEach((t) => document.addEventListener(t, holdEnd, true));
// iOS's long-press menu would interrupt a hold
document.addEventListener('contextmenu', (e) => {
  if (hintLv() && e.target.closest && e.target.closest('.rl')) e.preventDefault();
});

/* ===== Songs: typing ===== */
document.addEventListener('input', (e) => {
  const t = e.target;
  if (t.classList && t.classList.contains('sgq')) {
    U.sq = t.value;
    if (split()) U.sFocus = false;
    updateSongList();
    return;
  }
  const d = U.sDraft;
  if (!d) return;
  if (t.id === 'sgTitle') d.title = t.value;
  else if (t.id === 'sgArtist') d.artist = t.value;
  else if (t.id === 'sgLyr') d.text = t.value;
});
document.addEventListener('keydown', (e) => {
  if (e.target.classList && e.target.classList.contains('sgq') && e.key === 'Enter') {
    e.preventDefault();
    addRecent(U.sq);
    e.target.blur();
  }
});
document.addEventListener('focusin', (e) => {
  if (e.target.id === 'sgqb' && !U.sFocus) {
    U.sFocus = true;
    rerender();
  }
});
// paste plain text into the lyrics editor
document.addEventListener('paste', (e) => {
  const ed = e.target.closest && e.target.closest('.lyred');
  if (!ed) return;
  e.preventDefault();
  const t = (e.clipboardData || window.clipboardData).getData('text/plain');
  document.execCommand('insertText', false, t);
});

/* ===== Songs: keyboard =====
   Escape closes menus, the selected word and search. Cmd/Ctrl+F searches songs, Cmd/Ctrl+N adds one,
   Cmd/Ctrl+E edits the open song (and again for Done), and ↑ ↓ move between songs on iPad and Mac. */
document.addEventListener(
  'keydown',
  (e) => {
    const typing = e.target.closest && e.target.closest('input,textarea,[contenteditable="true"]');
    const mod = e.metaKey || e.ctrlKey;
    if (
      (e.key === 'Enter' || e.key === ' ') &&
      !typing &&
      e.target.matches &&
      e.target.matches('[role=button][data-a],.sgsec[data-a],.rl[role=button]')
    ) {
      e.preventDefault();
      e.target.click();
      return;
    }
    if (e.key === 'Escape') {
      if (U.sheet) return;
      if (SG.ctx || SG.sortMenu || SG.rMenu || SG.hMenu) {
        SG.ctx = null;
        SG.sortMenu = SG.rMenu = SG.hMenu = false;
        rerender();
      } else if (SG.pend) {
        SG.pend = null;
        rerender();
      } else if (SG.word) {
        SG.word = null;
        rerender();
      } else if (U.tab === 'songs' && !U.view && (U.sFocus || (split() && U.sq))) endSearch();
      else if (U.sList) SG_ACT.sgListDone();
      return;
    }
    if (!mod || U.sheet || rec || (X && isFlow(U.view))) return;
    const k = e.key.toLowerCase();
    if (k === 'f') {
      e.preventDefault();
      if (U.sEdit) sgEndEdit(true);
      if (U.tab !== 'songs' || U.view) {
        U.clock = false;
        U.tab = 'songs';
        U.view = null;
        render();
      }
      startSearch();
    } else if (k === 'n' && U.tab === 'songs' && !U.sEdit) {
      e.preventDefault();
      SG_ACT.sgNew();
    } else if (k === 'e' && songShown() && hasLyrics(songShown())) {
      e.preventDefault();
      if (U.sEdit) SG_ACT.sgDone();
      else SG_ACT.sgEdit();
    } else if (k === ',') {
      e.preventDefault();
      if (U.sEdit) sgEndEdit(true);
      go(() => {
        U.tab = 'settings';
        U.view = null;
      });
    }
  },
  true
);
document.addEventListener('keydown', (e) => {
  if (!(e.key === 'ArrowDown' || e.key === 'ArrowUp') || !songOpenInPane() || U.sheet || U.sEdit || U.sList) return;
  if (e.target.closest && e.target.closest('input,textarea,[contenteditable="true"]')) return;
  const ids = [...document.querySelectorAll('#slist .rowc')].map((r) => r.dataset.k);
  if (!ids.length) return;
  e.preventDefault();
  const i = ids.indexOf(U.songId),
    n = Math.max(0, Math.min(ids.length - 1, i + (e.key === 'ArrowDown' ? 1 : -1)));
  if (ids[n] !== U.songId) openSong(ids[n]);
  const r = document.querySelector('#slist .rowc.sel');
  if (r && r.scrollIntoView) r.scrollIntoView({ block: 'nearest' });
});
window.addEventListener('resize', () => {
  if (songShown()) {
    sgFit();
    sgPlaceMenu();
  }
});
