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
  // 3.19 New song from track: a short waveform with a plus
  trackNew:
    '<svg class="i" viewBox="0 0 24 24"><path d="M3 12h1M6.5 9v6M10 6v12M13.5 10v4"/><path d="M19 8v8M15 12h8"/></svg>',
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
  for (const k in sg.sections) n += MARKS.checks(sg.sections[k]); // Q03: marks.js
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
  // 3.18 Song Clock: timing is its own layer, checked against the running order; anything malformed is dropped
  if ('timing' in s) {
    const t = cleanTiming(s.timing, s);
    if (t) s.timing = t;
    else delete s.timing;
  }
  // 3.19 the track player: the track's name and length (the audio itself stays on the device, never in backups) and
  // the song's last loop, kept even without the track so a restore loses nothing (cleanLoop in track.js)
  if ('track' in s) {
    const k = s.track;
    if (k && typeof k === 'object' && !Array.isArray(k) && typeof k.dur === 'number' && isFinite(k.dur) && k.dur > 0)
      s.track = { name: typeof k.name === 'string' ? k.name.slice(0, 200) : '', dur: Math.round(k.dur * 100) / 100 };
    else delete s.track;
  }
  // 3.20 markers (chips on the track player), kept with the song like its loop (cleanMarkers in track.js)
  if ('markers' in s) {
    // Q12: not trimmed to the track's length here, so markers kept past a shorter track's end (Keep) aren't lost
    const m = cleanMarkers(s.markers);
    if (m) s.markers = m;
    else delete s.markers;
  }
  if ('loop' in s) {
    const l = cleanLoop(s.loop, s.track && s.track.dur);
    if (l) s.loop = l;
    else delete s.loop;
  }
  // the marker a loop belongs to must still be a marker (Q02: one without an end loops to the next marker, from the
  // Markers grid; 3.20–3.22 needed an end)
  if (s.loop && s.loop.mk && !(s.markers || []).some((m) => m.id === s.loop.mk)) delete s.loop.mk;
  // 3.20 takes' names and timestamped comments live with the song, so they're in every backup (cleanTakeNotes, takes.js)
  if ('takeNotes' in s) {
    const n = cleanTakeNotes(s.takeNotes);
    if (n) s.takeNotes = n;
    else delete s.takeNotes;
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
  // Q03: the layered marks (marks.js), moved across from the older `ann` the first time; `ann` and `orphans` are
  // kept in the older shape beside them, so a backup made now still opens in 3.26
  const mk = MARKS.clean(c, lines);
  return Object.assign({}, c, {
    label: typeof c.label === 'string' && c.label.trim() ? c.label.trim().slice(0, 30) : 'Verse',
    cue: typeof c.cue === 'string' ? c.cue.slice(0, 200) : '',
    lines,
    marks: mk.marks,
    held: mk.held,
    ann: mk.ann,
    orphans: mk.orphans,
  });
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
      sections[sid] = { label: b.label, cue: '', lines: toLines(b.text), marks: [], held: [], ann: {}, orphans: [] };
    }
    order.push({ o: sgId('o'), sid: sidFor[i] });
  });
  return { sections, order };
}

/* ===== Songs: marks follow their words =====
   When lyrics change, a word-level comparison moves each mark to where its word went (MARKS.relink in marks.js). A
   mark whose word changed is flagged to check; one whose word was removed waits at the top of its section to be moved
   or removed. */
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
    B = flat(nl);
  const flagged = MARKS.relink(sec, A, B, align(A, B)); // Q03: every layer's marks follow their words (marks.js)
  sec.lines = nl.length ? nl : [['…']];
  MARKS.mirror(sec);
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
    CLOCK.lyricsChanged(sg, ed.dataset.k, sec.lines, nl);
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
  // 3.18 Song Clock's settings live here too (checked in clock.js): Marks while playing, Blur ahead, Snapping,
  // Stay awake and the pinned icons
  // (3.19: and the track player's zoom level and speed, checked in track.js)
  // (3.22: and Search's recent searches, findRecent, checked in search.js)
  // (Q02: and the track player's jog wheel side, Song lyrics and the levels' layout version, checked in track.js)
  // (Q03: and the marks layer shown, mkLayer, checked in marks.js)
  [
    'marksPlaying',
    'blurAhead',
    'snapping',
    'stayAwake',
    'pins',
    'trkLevel',
    'trkSpeed',
    'findRecent',
    'trkJogPos',
    'trkSongLyrics',
    'trkLvV',
    'mkLayer',
  ].forEach((k) => {
    if (k in o) SGP[k] = o[k];
  });
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
  } else if (!U.sFocus) {
    h += '<h1>' + (U.sList ? (n ? n + ' selected' : 'Select songs') : 'Songs') + '</h1>';
    // 3.22: the Songs list keeps its own filter; on iPhone its field sits under the title (Search has the circle)
    if (D.songs.length && !U.sList)
      h +=
        '<button class="sfield inl sgqbtn" data-a="sgSearch" aria-label="Search songs">' +
        SGI.search +
        '<span>Search songs</span></button>';
  }
  if (!D.songs.length)
    return (
      h +
      '<div class="sgempty">' +
      SGI.wave +
      '<b>Add your first song</b>Add its audio from Files, or paste the lyrics and the sections are labelled for you.<div style="margin-top:18px"><button class="cta ink" data-a="sgNew" style="max-width:260px;margin:0 auto">New song</button></div></div>'
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
      '<div class="hdr">Pinned</div><div class="grp sgrp" data-gk="pinned">' +
      pinned.map((s) => songRowHTML(s, null, null, pm)).join('') +
      '</div>';
  if (rest.length)
    h +=
      '<div class="hdr"><button class="hdrsort" id="hdrsort" data-a="sgSortMenu" aria-haspopup="menu">' +
      SG_SORTS[sgp().sort] +
      SGI.down +
      '</button></div><div class="grp sgrp" data-gk="songs">' +
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
      // 3.20: practice shown automatically, never graded
      (lp ? '<span>' + practisedText(lp) + '</span>' : '<span>Not practised yet</span>') +
      (n ? '<span>·</span><span>' + nTakes(n) + '</span>' : '') +
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
    '<div class="srow" data-fk="sg:' +
    s.id +
    '">' +
    acts +
    '<div class="rowc' +
    (open ? ' sel' : '') +
    (SG.ctx === s.id ? ' lifted' : '') +
    '"' +
    (ed ? '' : ' data-zk="sg:' + s.id + '" data-push') + // 3.23 (Q08): a song pushes in from the right
    ' data-a="' +
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
    (ed ? '' : TRACK.rowPlay(s)) + // 3.20: play the song's track from the list
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
    '<div class="hdr" data-rise>Pinned songs</div><div class="grp" data-rise data-gk="todaypins">' +
    p
      .map((s) => {
        const lp = lastPractised(s, pm);
        return (
          '<div class="row sgtprow" data-fk="tp:' +
          s.id +
          '" data-zk="sg:' +
          s.id +
          '" data-push data-a="sgOpen" data-k="' +
          s.id +
          '" data-v="today" role="button" tabindex="0"><span class="lbl">' +
          esc(songTitle(s)) +
          '<small>' +
          (s.artist ? esc(s.artist) + ' · ' : '') +
          (lp ? practisedText(lp) : 'Not practised yet') +
          (takesOf(s.id) ? ' · ' + nTakes(takesOf(s.id)) : '') +
          '</small></span>' +
          TRACK.rowPlay(s) +
          '</div>'
        );
      })
      .join('') +
    '<button class="row" data-zk="songs" data-push data-a="sgAll"><span class="lbl acc">Show all songs</span>' +
    chev +
    '</button></div>'
  );
}

/* ===== Songs: one song ===== */
// Q03: which marks the song page draws: the chosen layer (plus Notes) in Practise and while marking, brackets, chains,
// breaths and Notes in Recall, and in Perform what Marks while playing allows (marks.js)
function sgShow() {
  if (U.sEdit === 'annotate') return MARKS.show('layer', MARKS.layer());
  if (recallOn()) return MARKS.show('recall');
  if (U.sMode === 'perform' && !U.sEdit) {
    const mp = ckPrefs().marksPlaying;
    return MARKS.show(mp === 'off' ? 'none' : mp === 'breaths' ? 'breaths' : 'active', MARKS.layer());
  }
  return MARKS.show('layer', MARKS.layer());
}
// one word on the song page: d is what it wears (marks.js), mask hides its letters in Recall
function sgWord(o, sid, li, wi, w, mask, d, chk) {
  const s = SG.sel,
    ed = U.sEdit === 'annotate';
  const hit = ed && s && s.sid === sid && s.li === li && wi >= s.w0 && wi <= s.w1,
    on = hit && s.o === o,
    echo = hit && !on;
  const p = SG.pulse,
    pl = p && p.sid === sid && p.li === li && wi >= p.w0 && wi <= p.w1 && p.o !== o;
  const lab = MARKS.labRow(d),
    txt = mask ? maskText(w, mask) : esc(w);
  return (
    '<span class="w' +
    (lab ? ' hv' : '') +
    (d.cls.length ? ' ' + d.cls.join(' ') : '') +
    (chk && ed ? ' chk' : '') +
    (on ? ' on' : '') +
    (echo ? ' echo' : '') +
    (pl ? ' pulse' : '') +
    '"' +
    (on && wi === s.w0 ? ' id="sgselw"' : '') +
    (ed
      ? ' role="button" tabindex="0" data-a="sgWord" data-o="' +
        o +
        '" data-k="' +
        sid +
        '" data-li="' +
        li +
        '" data-wi="' +
        wi +
        '"' +
        (on ? ' aria-pressed="true"' : '')
      : '') +
    '>' +
    // 3.17: a word with a label is a little column, the label above the word (like a chord sheet); Q03: every
    // layer's labels sit there, joined with " · ", with the peak tick first
    (lab ? lab + '<span class="wt">' + txt + '</span>' : txt) +
    '</span>'
  );
}
// the words of a line that have a mark to check, on any layer (shown while editing)
function sgChecks(sec, li) {
  const b = new Set();
  (sec.marks || []).forEach((m) => {
    if (m.check && m.line === li) for (let w = m.w0; w <= m.w1; w++) b.add(w);
  });
  return b;
}
// the layer chips, 1–4, above the lyrics in Practise and while marking
function sgLayerChips() {
  const L = MARKS.layer();
  return (
    '<div class="mkchips" role="tablist" aria-label="Marks layer">' +
    MK_LAYERS.map(
      (x, i) =>
        '<button class="mkchip' +
        (x[0] === L ? ' on' : '') +
        '" role="tab" aria-selected="' +
        (x[0] === L) +
        '" data-a="mkLayer" data-v="' +
        x[0] +
        '"><i>' +
        (i + 1) +
        '</i>' +
        x[1] +
        '</button>'
    ).join('') +
    '</div>'
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
    (sec.held || []).forEach((op) => {
      h +=
        '<div class="sgwarn"><span>' +
        esc(MARKS.name(op)) +
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
  // Q03: Delivery's Intention, one italic line under the section label
  const show = sgShow(),
    it = MARKS.intention(sec);
  if (it && show(it)) h += '<p class="mint">' + (hintLv() >= 2 ? maskText(it.text, 'all') : esc(it.text)) + '</p>';
  // Recall: 1 word shapes, 2 first words, 3 cues only, 4 blank. Marks stay visible
  const lv = hintLv(),
    mk = (wi) => (!lv ? null : lv === 1 ? 'shape' : lv === 2 && wi === 0 ? null : 'all'),
    peek = lv ? ' role="button" tabindex="0" aria-label="Peek at this line"' : '';
  if (sec.cue) h += '<p class="sgcue">' + (lv >= 4 ? maskText(sec.cue, 'all') : esc(sec.cue)) + '</p>';
  h += '<div class="sglines">';
  // Q05 suggested breaths (from the timing: a gap after a placed line), only in Phrasing on the Marks side, at the line's
  // end; a tap makes one a real Breath mark
  const sb = ed && MARKS.layer() === 'phrasing' ? CLOCK.sbAt(sg, o) : [];
  sec.lines.forEach((ln, li) => {
    const chk = ed ? sgChecks(sec, li) : null,
      r = MARKS.line(sec, li, show, (wi, w, d) => sgWord(o, sid, li, wi, w, mk(wi), d, chk && chk.has(wi))),
      sug =
        sb.includes(li) && !MARKS.breaths(sec, li).some(Boolean)
          ? '<button class="sgsb" data-a="sgSugBr" data-o="' +
            o +
            '" data-k="' +
            sid +
            '" data-li="' +
            li +
            '" aria-label="Suggested breath. Tap to add a breath mark">’<b>+</b></button>'
          : '';
    h +=
      '<p class="sgl' +
      (r.labelled ? ' hasv' : '') +
      (lv ? ' rl' : '') +
      '" data-o="' +
      o +
      '" data-li="' +
      li +
      '"' +
      peek +
      '>' +
      r.html +
      sug +
      '</p>';
    r.notes
      .slice()
      .sort((p, q) => p.w1 - q.w1)
      .forEach((m) => {
        h +=
          '<p class="sgnote' +
          (lv ? ' rl' : '') +
          '"' +
          peek +
          '>' +
          MKI.bookmark +
          '<span>' +
          (m.opt ? '<b>' + esc(m.opt) + '</b> ' : '') +
          (lv >= 2 ? maskText(m.text, 'all') : esc(m.text)) +
          '</span></p>';
      });
  });
  h += '</div>';
  // the focused section's controls sit on its soft patch (3.11): Record, its takes, and Marks
  if (sel && !rec)
    h +=
      '<div class="sgrecp"><button class="sgpill blue" data-a="sgRec" data-k="' +
      o +
      '">' +
      SGI.mic +
      'Record</button>' +
      (n ? '<button class="sgpill" data-a="sgTakes" data-k="' + o + '">' + nTakes(n) + '</button>' : '') +
      '<button class="sgpill" data-a="sgMarks" data-k="' +
      o +
      '">' +
      SGI.pen +
      'Marks</button></div>';
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
          ((mk) => ln.map((w, wi) => (mk[wi] ? '<span class="mk">' + esc(w) + '</span>' : esc(w))).join(' '))(
            MARKS.marked(sec, li)
          ) +
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
        '</button>' +
        CLOCK.timerPill(), // Q03 marking while listening: the play-along clock carries on, as a pill
      t:
        '<div class="seg sgseg" role="tablist"><span class="knob" aria-hidden="true"></span>' +
        [
          ['annotate', 'Marks'], // Q03: Marks · Lyrics (U.sEdit stays 'annotate' inside the code)
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
    r:
      hasLyrics(sg) && !CLOCK.editingHead()
        ? '<button class="circ glass" data-a="ckPencil" aria-label="Edit' +
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
  const ed = U.sEdit,
    head = !ed && hasLyrics(sg) && CLOCK.editingHead();
  let h = '';
  if (inPane) {
    const c = songControls(sg);
    h += ed
      ? '<div class="sgph sgedit">' + c.l + '<span class="sgphc">' + c.t + '</span>' + c.r + '</div>'
      : '<div class="sgph">' +
        (head ? CLOCK.titleInput(sg) : '<h1>' + esc(songTitle(sg)) + '</h1>') +
        (c.rec ? '<span class="rechead">' + esc(c.rec) + '</span>' : (head || ed ? '' : TAKE.headBtn(sg)) + c.r) +
        '</div>';
  } else
    h += head
      ? CLOCK.titleInput(sg)
      : // 3.20: the Takes button sits beside the title, so takes are one tap away without scrolling
        '<div class="sgtrow"><h1>' +
        esc(songTitle(sg)) +
        '</h1>' +
        (ed || recHere(sg) ? '' : TAKE.headBtn(sg)) +
        '</div>';
  // 3.18: "Artist · 3:58", the pinned icons and ⋯ (Song Clock, clock.js); songs without lyrics keep the plain line
  if (!ed && hasLyrics(sg)) h += CLOCK.headHTML(sg);
  else if (!ed && (sg.artist || (sg.timing && sg.timing.len))) {
    const lb = CLOCK.lenHTML(sg);
    h +=
      '<p class="sgart">' +
      esc(sg.artist || '') +
      (sg.artist && lb ? '<span aria-hidden="true"> · </span>' : '') +
      lb +
      '</p>' +
      CLOCK.lenFoot(sg);
  }
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
      (U.sMode === 'recall'
        ? '<button class="circ glass sgrbtn" id="sgrbtn" data-a="sgRMenu" aria-label="Recall options" aria-haspopup="menu">' +
          SGI.more +
          '</button>'
        : '') +
      '</div>' +
      // no tip line when the level changes, so the lyrics never move down (3.10.2)
      (U.sMode === 'recall' && U.sOrder === 'end' ? '<p class="sgsub">Working from the end.</p>' : '') +
      // Q03: the layer chips in Practise (one layer shows at a time)
      (U.sMode === 'practise' && !recHere(sg) ? sgLayerChips() : '');
  else
    h +=
      (ed === 'annotate' ? sgLayerChips() : '') +
      '<p class="sgsub">' +
      (ed === 'annotate'
        ? SG.pend
          ? 'Tap the word to move the mark to.'
          : 'Tap words to mark them. Hold a section to move it.'
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
  if (perf) {
    // Q03: Perform shows what Marks while playing allows
    const mp = ckPrefs().marksPlaying;
    h +=
      '<p class="sgbanner">' +
      (mp === 'off'
        ? 'Marks hidden. Cues only.'
        : mp === 'breaths'
          ? 'Breaths and cues only.'
          : mkLayerName(MARKS.layer()) + ' marks, breaths and cues.') +
      '</p>';
  }
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
    '<div class="hdr">Practice</div><div class="grp"><button class="row" data-zk="sgp:' +
    sg.id +
    '" data-a="sgPractise" data-k="' +
    sg.id +
    '">' +
    songTile +
    '<span class="lbl">Song practice<small>' +
    (n ? n + ' saved take' + (n > 1 ? 's' : '') + ' · record another' : 'Record a take and note how it went') +
    '</small></span>' +
    chev +
    '</button>' +
    TRACK.row(sg) + // 3.19 the track player (track.js)
    '</div>'
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
    // Q03: the four layers and what each mark looks like (the full guide is Q04)
    const ex = {
      phrase: '<span class="mph">so</span>',
      stress: '<span class="mst">so</span>',
      hold: '<span class="w mhold">so</span>',
    };
    return sheetWrap(
      'Marks key',
      MK_LAYERS.concat([['note', 'Every layer']])
        .map(
          (x, i) =>
            '<div class="hdr">' +
            (x[0] === 'note' ? '' : i + 1 + ' · ') +
            x[1] +
            '</div><div class="grp">' +
            (x[0] === 'note' ? ['note'] : MK_BY[x[0]])
              .map(
                (t) =>
                  '<div class="row sgkey"><span class="g">' +
                  (ex[t] || mkGlyph(t)) +
                  '</span><span class="lbl">' +
                  MK_DEF[t].n +
                  '<small>' +
                  esc(MK_DEF[t].opts.join(' · ') || (mkTakesText(t, '') ? 'Your own words' : 'One tap')) +
                  '</small></span></div>'
              )
              .join('') +
            '</div>'
        )
        .join('') +
        '<div class="grp" style="margin-top:14px"><div class="row sgkey"><span class="g"><span class="mut">' +
        SGI.link +
        '</span></span><span class="lbl">Linked<small>A section shared with its repeats, and their marks</small></span></div></div>' +
        '<p class="foot">Only one layer shows at a time. Add or change marks with the pencil.</p>'
    );
  }
  if (s === 'sgTakes') return TAKE.sheet(sd);
  if (s === 'sgTakeMenu' || s === 'sgTakeDel' || s === 'sgReview' || s === 'sgCmtMenu') return TAKE.sheet(sd, s);
  // 3.20 the length linked to the song's track
  if (s === 'sgLenUnlink')
    return confirmSheet(
      'Unlink from track?',
      'The length will stop matching the uploaded audio. You can relink it later.',
      'Unlink',
      'sgLenUnlinkYes',
      sd.k || ''
    );
  if (s === 'sgLenRelink') {
    const d = U.sDraft,
      w = sd.draft ? d && d.media && d.len : sg && sg.timing && sg.timing.len,
      L = sd.draft ? d && d.media && Math.round(d.media.r.dur) : sg && sg.track && Math.round(sg.track.dur);
    if (!w || !L) return '';
    return sheetWrap(
      'Relink to track?',
      '<p class="note">Your custom length ' +
        fmtLen(w) +
        ' will be replaced with ' +
        fmtLen(L) +
        '.</p><button class="cta" data-a="sgLenRelinkYes" data-k="' +
        esc(sd.k || '') +
        '">Relink</button><button class="ghost" data-a="close">Cancel</button>'
    );
  }
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
// 3.20 the + sheet: Add media (a song's audio from Files, then the form) or Manually (the form as before). The
// picked file stays with the draft until Save, so cancelling leaves nothing behind
const sgBase = (n) =>
  String(n || '')
    .replace(/\.[^./]{1,5}$/, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 80);
const SG_LNK =
  '<svg class="i" viewBox="0 0 24 24"><path d="M10 14a4 4 0 005.66 0l3-3a4 4 0 00-5.66-5.66l-1 1"/><path d="M14 10a4 4 0 00-5.66 0l-3 3a4 4 0 005.66 5.66l1-1"/></svg>';
const SG_UNLNK =
  '<svg class="i" viewBox="0 0 24 24"><path d="M15.5 13.5l3-3a4 4 0 00-5.66-5.66l-1 1"/><path d="M8.5 10.5l-3 3a4 4 0 005.66 5.66l1-1"/><path d="M4 4l3 3M20 20l-3-3M9 3.5V5M3.5 9H5M15 20.5V19M20.5 15H19"/></svg>';
function sgLenRow(d) {
  const m = d.media,
    len = d.len,
    t = len ? fmtLen(len) : 'Add';
  let h = '<label class="sglab2">Length</label><div class="sglenrow">';
  if (m && d.lenLink && len)
    h +=
      '<button class="sglenv" data-a="sgAddLen" aria-label="Length ' +
      t +
      ', linked to the track. Tap to unlink">' +
      t +
      '<span class="lnk on">' +
      SG_LNK +
      '</span></button>';
  else {
    h += '<button class="sglenv" data-a="sgAddLen" aria-label="Length ' + t + '">' + t + '</button>';
    if (m && len)
      h +=
        '<button class="lnk off" data-a="sgAddRelink" aria-label="Relink to the track">' +
        SG_UNLNK +
        '</button><span class="sglenc">Custom · track is ' +
        fmtLen(Math.round(m.r.dur)) +
        '</span>';
  }
  h += '</div>';
  if (!m) h += '<p class="foot sglenf">Add a track later and its length can link to it.</p>';
  return h;
}
const fmtLen = (s) => Math.floor(s / 60) + ':' + String(Math.round(s) % 60).padStart(2, '0');
function newSongSheet() {
  const d = U.sDraft;
  if (!d) return '';
  if (d.step === 1 && d.forId)
    return sheetWrap(
      'Add lyrics',
      sgField('sgTitle', 'Title', d.title, 'Song title', 'maxlength="80" autocapitalize="words"') +
        sgField('sgArtist', 'Artist (optional)', d.artist, 'Who sings it', 'maxlength="80" autocapitalize="words"') +
        '<label class="sglab2" for="sgLyr">Lyrics</label><textarea class="field sglyr" id="sgLyr" placeholder="Paste lyrics here. Leave a blank line between sections.">' +
        esc(d.text) +
        '</textarea><p class="foot">Labels like [Chorus] or Verse 2: start a new section. Blank lines split sections too.</p>' +
        (d.err ? '<p class="err">' + esc(d.err) + '</p>' : '') +
        '<div style="margin-top:14px"><button class="cta" data-a="sgSplit">Next</button></div>'
    );
  if (d.step === 1) {
    const media = d.mode !== 'manual';
    let h =
      '<div class="seg wide sgaddseg" role="tablist" aria-label="How to add the song"><span class="knob" aria-hidden="true"></span>' +
      [
        ['media', 'Add media'],
        ['manual', 'Manually'],
      ]
        .map(
          (x) =>
            '<button role="tab" data-a="sgAddMode" data-v="' +
            x[0] +
            '" class="' +
            ((x[0] === 'media') === media ? 'on' : '') +
            '" aria-selected="' +
            ((x[0] === 'media') === media) +
            '">' +
            x[1] +
            '</button>'
        )
        .join('') +
      '</div>';
    if (media && d.reading)
      return sheetWrap(
        'New song',
        h +
          '<div class="sgdrop busy" role="status" aria-busy="true">' +
          SGI.wave +
          '<b>Reading the track…</b><span>' +
          esc(d.reading) +
          '</span></div>'
      );
    if (media && !d.media)
      return sheetWrap(
        'New song',
        h +
          '<button class="sgdrop" data-a="sgAddPick">' +
          SGI.wave +
          '<b>Choose audio file</b><span>MP3, M4A or WAV from Files</span></button>' +
          '<p class="foot">The track stays on this ' +
          deviceName() +
          ' and isn’t included in backups. You can paste the lyrics next, or later.</p>'
      );
    if (media)
      h +=
        '<p class="sgadded">' +
        ICON.check +
        '<span>' +
        esc(d.media.name) +
        ' added</span></p><button class="lnkbtn sgswap" data-a="sgAddPick">Choose a different file</button>';
    h +=
      sgField(
        'sgTitle',
        'Title',
        d.title,
        media ? sgBase(d.media.name) || 'Song title' : 'Song title',
        'maxlength="80" autocapitalize="words"'
      ) +
      sgField('sgArtist', 'Artist (optional)', d.artist, 'Who sings it', 'maxlength="80" autocapitalize="words"') +
      sgLenRow(media ? d : Object.assign({}, d, { media: null })) +
      '<label class="sglab2" for="sgLyr">Lyrics' +
      (media ? ' (optional)' : '') +
      '</label><textarea class="field sglyr" id="sgLyr" placeholder="Paste lyrics here. Leave a blank line between sections.">' +
      esc(d.text) +
      '</textarea><p class="foot">Labels like [Chorus] or Verse 2: start a new section. Blank lines split sections too.</p>' +
      (d.err ? '<p class="err">' + esc(d.err) + '</p>' : '') +
      '<div style="margin-top:14px"><button class="cta" data-a="sgSplit">' +
      (media && !(d.text || '').trim() ? 'Save song' : 'Next') +
      '</button></div>';
    return sheetWrap('New song', h);
  }
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
/* ===== Songs: marking words (Q03) =====
   SG.sel = {o, sid, li, w0, w1, a}: the selected words, one line of one place in the song (a is the word the selection
   grew from). Repeats of a linked section show the same marks, so the same words light up in every copy. */
function sgSecOf(sel) {
  const sg = songById(U.songId);
  return sel && hasLyrics(sg) && sg.sections[sel.sid] ? sg.sections[sel.sid] : null;
}
// after a change on a linked section: its repeats pulse once, and the first time a toast says so
function sgLinked(sel) {
  const sg = songById(U.songId);
  if (!sg || uses(sg, sel.sid) < 2) return;
  SG.pulse = Object.assign({}, sel);
  setTimeout(() => (SG.pulse = null), 950);
  if (!SG.told) {
    SG.told = true;
    const n = uses(sg, sel.sid) - 1;
    setTimeout(() => toast('Also updated in ' + n + ' linked section' + (n > 1 ? 's' : '')), 2000);
  }
}
// tap a word: select it; another word on the same line extends the selection to it; a word inside a selection of
// several starts again from it; the only selected word clears it; a word on another line starts a new selection
function selectWord(w) {
  const sg = songById(U.songId);
  if (!hasLyrics(sg) || !sg.sections[w.sid]) return;
  if (SG.pend) {
    const pm = SG.pend,
      src = sg.sections[pm.sid],
      op = src && (src.held || []).find((x) => x.id === pm.id);
    SG.pend = null;
    if (op) {
      sgSnap();
      const dst = sg.sections[w.sid];
      src.held = src.held.filter((x) => x !== op);
      MARKS.mirror(src);
      const r = MARKS.add(dst, { li: w.li, w0: w.wi, w1: w.wi }, op.type, op.opt, op.text);
      if (r) r.m.id = op.id;
      const m = op;
      save();
      SG.sel = { o: w.o, sid: w.sid, li: w.li, w0: w.wi, w1: w.wi, a: w.wi };
      if (m.L !== 'note' && m.L !== MARKS.layer()) MARKS.setLayer(m.L);
      rerender();
      toast('Mark moved');
      return;
    }
  }
  const s = SG.sel,
    wi = w.wi;
  if (s && s.o === w.o && s.li === w.li) {
    if (s.w0 === s.w1 && s.w0 === wi) SG.sel = null;
    else if (wi >= s.w0 && wi <= s.w1) SG.sel = Object.assign({}, s, { w0: wi, w1: wi, a: wi });
    else SG.sel = Object.assign({}, s, { w0: Math.min(s.w0, wi), w1: Math.max(s.w1, wi) });
  } else SG.sel = { o: w.o, sid: w.sid, li: w.li, w0: wi, w1: wi, a: wi };
  MK.open = null;
  MK.err = '';
  rerender();
}
// the marks sheet's own state: the mark whose options are open, a message under the text field
const MK = { open: null, err: '' };
// "Added Peak" with Undo (the same toast as Song Clock's nudges)
function mkUndoToast(text, undo) {
  ckToast(text, () => {
    undo();
    save();
    rerender();
    toast('Undone');
  });
}
// add a mark to the selection (from the sheet)
function mkPut(type, opt, text) {
  const sel = SG.sel,
    sec = sgSecOf(sel);
  if (!sec) return;
  if (mkNeedsText(type, opt) && !(text || '').trim()) {
    MK.err = 'Type something first';
    return rerender();
  }
  sgSnap();
  const r = MARKS.add(sec, sel, type, opt, text);
  save();
  MK.open = null;
  MK.err = '';
  sgLinked(sel);
  MARKS.fresh = r.m.id;
  rerender();
  setTimeout(() => (MARKS.fresh = null), 50);
  const sid = sel.sid;
  mkUndoToast('Added ' + MK_DEF[type].n, () => {
    const s2 = songById(U.songId),
      c = s2 && s2.sections[sid];
    if (!c) return;
    c.marks = c.marks.filter((x) => x.id !== r.m.id).concat(r.gone);
    MARKS.mirror(c);
  });
}
function sgEndEdit(quiet) {
  let f = 0;
  if (U.sEdit === 'lyrics') f = applyLyrics();
  U.sEdit = null;
  SG.sel = null;
  SG.pend = null;
  SG.drag = null;
  save();
  if (!quiet) {
    const c = checkCount(songById(U.songId));
    toast(c ? c + ' mark' + (c > 1 ? 's' : '') + ' to check' : 'Changes saved');
  }
  return f;
}
// the + sheet's typed fields, kept in the draft before it's drawn again
function sgReadDraft() {
  const d = U.sDraft;
  if (!d) return;
  const v = (id) => ($(id) ? $(id).value : null);
  if (v('sgTitle') != null) d.title = v('sgTitle');
  if (v('sgArtist') != null) d.artist = v('sgArtist');
  if (v('sgLyr') != null) d.text = v('sgLyr');
}
// 3.20: relink a song's length to its track (asking first if they differ)
function sgRelink(sg, ok) {
  if (!sg || !sg.track) return;
  const L = Math.round(sg.track.dur);
  if (!(L > 0) || L > CK_MAXLEN) return;
  const len = sg.timing && sg.timing.len;
  if (!ok && len && len !== L) {
    U.sheet = 'sgLenRelink';
    U.sd = { k: sg.id };
    return rerender();
  }
  if (!sg.timing) sg.timing = { len: null, real: false, est: false, slots: {} };
  sg.timing.len = L;
  sg.timing.lenLink = true;
  save();
  rerender();
  toast('Relinked to track');
}
async function sgSaveDraft() {
  const d = U.sDraft;
  if (!d || !d.blocks || (!d.blocks.length && !(d.media && d.mode !== 'manual'))) return;
  if (d.saving) return;
  const lyr = d.blocks.length ? buildLyrics(d.blocks) : {},
    media = !d.forId && d.mode !== 'manual' ? d.media : null,
    // 3.20: a blank title uses the file's name, so a song is never nameless
    title = titleCase(d.title) || (media && sgBase(media.name)) || 'Untitled song',
    artist = titleCase(d.artist);
  let sg = d.forId && songById(d.forId);
  const fresh = !sg;
  if (sg) Object.assign(sg, { name: title, artist, original: d.text }, lyr);
  else {
    sg = Object.assign(
      { id: 'g_' + Date.now().toString(36), name: title, artist, added: Date.now(), pinned: false },
      d.text && d.blocks.length ? { original: d.text } : {},
      lyr
    );
    // the picked audio goes into vocalTracks only now, on Save
    if (media) {
      d.saving = true;
      try {
        await TRACK.attach(sg, media.file, media.r);
      } catch (e) {
        d.saving = false;
        return toast('Couldn’t save the track. Storage may be full.');
      }
      d.saving = false;
      if (U.sDraft !== d) return; // closed meanwhile: nothing is kept
    }
    // the length as set on the sheet: linked to the track, or the song's own
    if (d.len) {
      if (!sg.timing) sg.timing = { len: null, real: false, est: false, slots: {} };
      sg.timing.len = d.len;
      if (media && d.lenLink && d.len === Math.round(media.r.dur)) sg.timing.lenLink = true;
      else delete sg.timing.lenLink;
    } else if (sg.timing) delete sg.timing.lenLink;
    D.songs.push(sg);
  }
  save();
  // 3.15: a new song's sheet shrinks into its row in Songs, then the row opens the song (iPhone, motion on)
  const sh = fresh && !split() ? ZOOM.sheetShot() : null;
  U.sDraft = null;
  U.sheet = null;
  U.sd = {};
  U.sFocus = false;
  U.sq = '';
  if (sh) {
    go(() => {
      U.tab = 'songs';
      U.view = null;
    });
    toast('Song saved');
    const id = sg.id;
    ZOOM.sheetInto(sh, 'sg:' + id, () => {
      if (U.sheet || U.view || U.tab !== 'songs') return; // something else happened meanwhile
      ZOOM.arm(document.querySelector('#app [data-zk="sg:' + id + '"]'));
      openSong(id);
    });
    return;
  }
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
  DET.arm();
  s.pinned = !s.pinned;
  save();
  rerender();
  toast(s.pinned ? 'Pinned' : 'Unpinned');
}
async function deleteSongs(ids) {
  stopPlayback();
  DET.arm();
  D.songs = D.songs.filter((x) => !ids.includes(x.id));
  save();
  for (const t of TAKES.filter((t) => ids.includes(t.songId))) await delTake(t.id);
  await TRACK.forget(ids); // 3.19: a deleted song's track goes from this device too
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
    DET.arm();
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
    DET.arm({ stagger: true });
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
    // 3.20: one door, two ways in: Add media (the default) or Manually
    U.sDraft = { step: 1, mode: 'media', title: '', artist: '', text: '', len: null, lenLink: false, media: null };
    U.sheet = 'sgNew';
    U.sd = {};
    SG.ctx = null;
    rerender();
  },
  sgAddMode(el, v) {
    const d = U.sDraft;
    if (!d || d.mode === v) return;
    sgReadDraft();
    d.mode = v === 'manual' ? 'manual' : 'media';
    if (d.mode === 'manual' && d.lenLink) d.lenLink = false; // Manually has no track to follow
    if (d.mode === 'media' && d.media && d.len === Math.round(d.media.r.dur)) d.lenLink = true;
    segPick(el);
    rerender();
  },
  sgAddPick() {
    sgReadDraft();
    if (rec) return toast('Stop recording first');
    TRACK.pick('draft');
  },
  // a file read for the draft: the form opens with the length linked to it. Metadata isn't trusted, so the title
  // and artist stay as they were (empty to start); a blank title becomes the file's name on Save
  sgMedia(file, r) {
    const d = U.sDraft;
    if (!d) return;
    const L = Math.round(r.dur);
    d.media = { file, r, name: String(file.name || 'Track') };
    d.mode = 'media';
    if (L > 0 && L <= CK_MAXLEN) {
      d.len = L;
      d.lenLink = true;
    }
    d.err = '';
    U.sheet = 'sgNew';
    rerender();
  },
  sgAddLen(el) {
    const d = U.sDraft;
    if (!d) return;
    sgReadDraft();
    if (d.mode !== 'manual' && d.media && d.lenLink) {
      U.sheet = 'sgLenUnlink';
      U.sd = { draft: true, ret: { sheet: 'sgNew', sd: {} } };
      return rerender();
    }
    ckPick(el, d.len || (d.media ? Math.round(d.media.r.dur) : 210), (v) => {
      d.len = v > 0 ? v : null;
      d.lenLink = !!(d.media && d.mode !== 'manual' && d.len === Math.round(d.media.r.dur));
      rerender();
    });
  },
  sgAddRelink() {
    const d = U.sDraft;
    if (!d || !d.media) return;
    sgReadDraft();
    const L = Math.round(d.media.r.dur);
    if (d.len && d.len !== L) {
      U.sheet = 'sgLenRelink';
      U.sd = { draft: true, ret: { sheet: 'sgNew', sd: {} } };
      return rerender();
    }
    d.len = L;
    d.lenLink = true;
    rerender();
    toast('Relinked to track');
  },
  // 3.20 the length linked to the track: unlink (then the picker), or relink
  sgLenUnlinkYes() {
    const sd = U.sd || {};
    if (sd.draft) {
      const d = U.sDraft;
      if (!d) return;
      d.lenLink = false;
      U.sheet = 'sgNew';
      U.sd = {};
      rerender();
      const b = document.querySelector('#layer [data-a=sgAddLen]');
      ckPick(b, d.len || 210, (v) => {
        d.len = v > 0 ? v : null;
        rerender();
      });
      return;
    }
    const sg = songById(sd.k);
    U.sheet = null;
    U.sd = {};
    if (!sg || !sg.timing) return rerender();
    delete sg.timing.lenLink;
    save();
    rerender();
    const b = document.querySelector('#app .cklen, #app [data-a=ckLen]');
    ckPick(b, sg.timing.len || 210, (v) => ckSetLen(sg, v));
  },
  sgLenRelinkYes() {
    const sd = U.sd || {};
    if (sd.draft) {
      const d = U.sDraft;
      if (d && d.media) {
        d.len = Math.round(d.media.r.dur);
        d.lenLink = true;
      }
      U.sheet = 'sgNew';
      U.sd = {};
      rerender();
      return toast('Relinked to track');
    }
    U.sheet = null;
    U.sd = {};
    sgRelink(songById(sd.k), true);
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
    sgReadDraft();
    const b = splitBlocks(d.text);
    // 3.20: a song added from its audio can be saved without lyrics, to paste later
    if (!b.length && !d.forId && d.mode !== 'manual' && d.media) {
      d.blocks = [];
      return sgSaveDraft();
    }
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
  // Q05 a suggested breath becomes a real Breath mark on the line's last word, with Undo
  sgSugBr(el) {
    const sg = songShown(),
      sid = el.dataset.k,
      li = +el.dataset.li,
      sec = sg && sg.sections[sid];
    if (!sec || !sec.lines[li] || U.sEdit !== 'annotate') return;
    const n = sec.lines[li].length,
      was = JSON.stringify(sg.timing || null);
    sgSnap();
    const r = MARKS.add(sec, { sid, li, w0: n - 1, w1: n - 1 }, 'breath', '', '');
    CLOCK.clearSb(sg, sid, li);
    save();
    MARKS.fresh = r.m.id;
    rerender();
    setTimeout(() => (MARKS.fresh = null), 50);
    mkUndoToast('Added Breath', () => {
      const s2 = songById(sg.id),
        c = s2 && s2.sections[sid];
      if (!c) return;
      c.marks = c.marks.filter((x) => x.id !== r.m.id).concat(r.gone);
      MARKS.mirror(c);
      const t = JSON.parse(was);
      if (t) s2.timing = t;
    });
  },
  sgSec(el, v, k) {
    if (rec || U.sEdit) return;
    U.sSec = U.sSec === k ? null : k;
    sgRefocus();
  },
  // Marks on a focused section: Annotate, scrolled to that section
  sgMarks(el, v, k) {
    if (rec) return toast('Stop recording first');
    SG_ACT.sgEdit();
    if (U.sEdit) scrollToSec(k);
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
    const was = DET.hxSnap();
    U.sHint = n;
    rerender();
    hxFadeIn();
    DET.hxWave(was);
  },
  sgHMenu() {
    SG.hMenu = true;
    rerender();
  },
  sgSetHint(el, v) {
    const was = DET.hxSnap();
    U.sHint = Math.max(0, Math.min(SG_HINTS.length - 1, +v || 0));
    SG.hMenu = false;
    rerender();
    hxFadeIn();
    DET.hxWave(was);
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
    SG.sel = null;
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
    SG.sel = null;
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
    SG.sel = null;
    SG.noSync = true; // the editors on screen still show the text being undone
    rerender();
    toast('Undone');
  },
  sgWord(el) {
    selectWord({ o: el.dataset.o, sid: el.dataset.k, li: +el.dataset.li, wi: +el.dataset.wi });
  },
  // Q03 the layer chips: switch layer in place, keeping the line you're looking at where it is
  mkLayer(el, v) {
    if (!MK_BY[v] || v === MARKS.layer()) return;
    const anchor =
      document.querySelector('.w.on') ||
      [...document.querySelectorAll('#app .sgl')].find((l) => l.getBoundingClientRect().top >= 90);
    const line = anchor && (anchor.closest('.sgl') || anchor),
      key = line && line.dataset.o + '|' + line.dataset.li,
      y0 = line ? line.getBoundingClientRect().top : 0;
    MARKS.setLayer(v);
    MK.open = null;
    MK.err = '';
    CK.sig = '';
    rerender();
    if (key) {
      const [o, li] = key.split('|'),
        l2 = document.querySelector('.sgl[data-o="' + o + '"][data-li="' + li + '"]');
      if (l2) window.scrollBy(0, l2.getBoundingClientRect().top - y0);
    }
  },
  // a mark button in the sheet: added at once, or its options shown underneath (tap again to close them)
  mkPick(el, v) {
    const d = MK_DEF[v];
    if (!d || !SG.sel) return;
    if (!d.opts.length && !mkTakesText(v, '')) return mkPut(v, '', '');
    MK.open = MK.open && MK.open.type === v ? null : { type: v, opt: d.opts.length ? null : '' };
    MK.err = '';
    rerender();
    sgFocusMk();
  },
  // an option chip: added at once, or its text field shown
  mkOpt(el, v) {
    const o = MK.open;
    if (!o) return;
    if (!mkTakesText(o.type, v)) return mkPut(o.type, v, '');
    o.opt = v;
    MK.err = '';
    rerender();
    sgFocusMk();
  },
  mkText() {
    const o = MK.open;
    if (!o || o.opt == null) return;
    mkPut(o.type, o.opt, (($('mkIn') || {}).value || '').trim());
  },
  // remove a mark from "On these words"
  mkRm(el, v) {
    const sec = sgSecOf(SG.sel);
    if (!sec) return;
    sgSnap();
    const m = MARKS.remove(sec, v);
    if (!m) return;
    save();
    sgLinked(SG.sel);
    rerender();
    const sid = SG.sel.sid;
    mkUndoToast('Removed ' + MK_DEF[m.type].n, () => {
      const s2 = songById(U.songId),
        c = s2 && s2.sections[sid];
      if (!c) return;
      c.marks = c.marks.concat(m);
      MARKS.mirror(c);
    });
  },
  // a mark flagged after a lyric edit: it's right where it is
  mkKeep(el, v) {
    const sec = sgSecOf(SG.sel),
      m = sec && sec.marks.find((x) => x.id === v);
    if (!m) return;
    sgSnap();
    delete m.check;
    delete m.was;
    MARKS.mirror(sec);
    save();
    rerender();
  },
  mkClear() {
    SG.sel = null;
    MK.open = null;
    MK.err = '';
    rerender();
  },
  sgOMove(el, v, k) {
    SG.pend = { sid: k, id: v };
    SG.sel = null;
    rerender();
    toast('Tap a word to move it to');
  },
  sgORemove(el, v, k) {
    const sg = songById(U.songId),
      s = hasLyrics(sg) && sg.sections[k];
    if (!s) return;
    sgSnap();
    s.held = (s.held || []).filter((x) => x.id !== v);
    MARKS.mirror(s);
    save();
    rerender();
  },
  sgCue(el, v, k) {
    SG.sel = null;
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
    SG.sel = null;
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
function mkCapHTML() {
  return (
    '<div class="mkcap glass" id="mkcap" role="status">' +
    (SG.pend ? 'Tap the word to move the mark to' : 'Select words to mark') +
    '</div>'
  );
}
function mkSheetHTML(sg) {
  const sel = SG.sel,
    sec = sg.sections[sel.sid];
  if (!sec || !sec.lines[sel.li]) return '';
  const L = MARKS.layer(),
    words = sec.lines[sel.li].slice(sel.w0, sel.w1 + 1).join(' '),
    on = MARKS.onSel(sec, sel, L),
    o = MK.open;
  let h =
    '<div class="mksheet glass" id="mksheet" role="dialog" aria-label="Marks for ' +
    esc(words) +
    '"><div class="mkhd"><span class="mkwd">“' +
    esc(words) +
    '”<small>' +
    mkLayerNum(L) +
    ' · ' +
    mkLayerName(L) +
    '</small></span><button class="circ glass sm" data-a="mkClear" aria-label="Clear the selection">' +
    ICON.x +
    '</button></div>';
  if (on.length)
    h +=
      '<div class="mkon"><span class="mkonl">On these words</span>' +
      on
        .map(
          (m) =>
            '<span class="mkchipx' +
            (m.check ? ' chk' : '') +
            '"><span>' +
            (m.L !== L && m.L !== 'note' ? mkLayerNum(m.L) + ' · ' : '') +
            esc(MARKS.name(m)) +
            (m.check ? ' · was “' + esc(m.was || '') + '”' : '') +
            '</span>' +
            (m.check ? '<button class="mkkeep" data-a="mkKeep" data-v="' + m.id + '">Keep</button>' : '') +
            '<button class="mkx" data-a="mkRm" data-v="' +
            m.id +
            '" aria-label="Remove ' +
            esc(MARKS.name(m)) +
            '">' +
            ICON.x +
            '</button></span>'
        )
        .join('') +
      '</div>';
  h +=
    '<div class="mkbtns">' +
    MK_BY[L].concat('note')
      .map(
        (t) =>
          '<button class="mkb' +
          (o && o.type === t ? ' open' : '') +
          '" data-a="mkPick" data-v="' +
          t +
          '" aria-expanded="' +
          !!(o && o.type === t) +
          '"><span class="mkt" aria-hidden="true">' +
          mkGlyph(t) +
          '</span><span>' +
          MK_DEF[t].n +
          '</span></button>'
      )
      .join('') +
    '</div>';
  if (o) {
    const d = MK_DEF[o.type];
    if (d.opts.length)
      h +=
        '<div class="mkopts" role="group" aria-label="' +
        d.n +
        '">' +
        d.opts
          .map(
            (x) =>
              '<button class="mkopt' +
              (o.opt === x ? ' on' : '') +
              '" data-a="mkOpt" data-v="' +
              esc(x) +
              '">' +
              esc(x) +
              '</button>'
          )
          .join('') +
        '</div>';
    if (o.opt != null && mkTakesText(o.type, o.opt)) {
      const ph =
        { say: 'mor-nin', intention: 'Who you’re singing to', vowel: o.opt === 'Sing as…' ? 'wah' : 'ah→ee' }[o.type] ||
        'A reminder (optional)';
      h +=
        '<div class="mktxt"><input class="field" id="mkIn" maxlength="' +
        mkMax(o.type) +
        '" placeholder="' +
        esc(ph) +
        '" autocomplete="off" enterkeyhint="done" aria-label="' +
        esc(d.n + (o.opt ? ' · ' + o.opt : '')) +
        '"><button class="sgpill blue" data-a="mkText">Add</button></div>' +
        (MK.err ? '<p class="mkerr" role="alert">' + esc(MK.err) + '</p>' : '');
    }
  }
  return h + '</div>';
}
// the text field in the sheet takes the focus when it appears (and keeps what was typed after a message)
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target && e.target.id === 'mkIn') {
    e.preventDefault();
    SG_ACT.mkText();
  }
});
function sgFocusMk() {
  const i = $('mkIn');
  if (i) i.focus({ preventScroll: true });
}
function slayerHTML() {
  let h = '';
  const sg = songShown();
  // Q03 the marks sheet: rises when words are selected, in place of the dock; with nothing selected, a capsule
  if (sg && U.sEdit === 'annotate' && !U.sheet && !SG.drag) h += SG.sel ? mkSheetHTML(sg) : mkCapHTML();
  // Q05 the hold menu on a lyric line (clock.js)
  h += CLOCK.lineMenuHTML();
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
    sgFocusPaint(false);
  }
  ckLmPaint();
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
/* ===== Songs: focusing a section (3.11) =====
   The lyrics are one continuous page. Tapping a section gives it a soft patch with its controls,
   and everything else dims and blurs more the further it is (MOTION.blur, at most 1.5 px).
   Labels only dim, so every section stays easy to aim at. Focusing updates the page in place
   rather than redrawing it, so the fade can ease instead of snapping. */
function sgRefocus() {
  const sg = songShown(),
    box = document.querySelector('.sgsong');
  if (!sg || !box || U.sEdit || SG.drag || !hasLyrics(sg)) return rerender();
  const t = document.createElement('div');
  sg.order.forEach((x, i) => {
    const live = box.querySelector('.sgsec[data-o="' + x.o + '"]');
    if (!live) return;
    t.innerHTML = sgSection(sg, i);
    const nw = t.firstElementChild;
    [...live.attributes].forEach((a) => !nw.hasAttribute(a.name) && live.removeAttribute(a.name));
    [...nw.attributes].forEach((a) => live.getAttribute(a.name) !== a.value && live.setAttribute(a.name, a.value));
    const lh = live.querySelector('.sghead'),
      nh = nw.querySelector('.sghead');
    if (lh && nh && lh.innerHTML !== nh.innerHTML) lh.innerHTML = nh.innerHTML;
    const lc = live.querySelector('.sgrecp'),
      nc = nw.querySelector('.sgrecp');
    if (lc) lc.remove();
    if (nc) {
      live.appendChild(nc);
      MOTION.animate(
        nc,
        [
          { opacity: 0, transform: 'translateY(-4px)' },
          { opacity: 1, transform: 'none' },
        ],
        { fade: true }
      );
    }
  });
  const want = !rec && !hintLv() && !sg.order.some((x) => x.o === U.sSec),
    nx = box.nextElementSibling,
    hint = nx && nx.classList.contains('sghint') ? nx : null;
  if (want && !hint) box.insertAdjacentHTML('afterend', '<p class="sghint">Tap a section to record it</p>');
  if (!want && hint) hint.remove();
  sgFocusPaint(true);
}
function sgFocusPaint(animate) {
  const box = document.querySelector('.sgsong');
  if (!box) return;
  const sel = box.querySelector('.sgsec.sel'),
    rows = [];
  box
    .querySelectorAll('.sgsec')
    .forEach((sec) =>
      sec
        .querySelectorAll('.sghead,.sgcue,.sgl,.sgnote')
        .forEach((el) => rows.push({ el, own: sec === sel, label: el.classList.contains('sghead') }))
    );
  let first = -1,
    last = -1;
  rows.forEach((r, i) => {
    if (r.own) {
      if (first < 0) first = i;
      last = i;
    }
  });
  if (!animate) box.classList.add('nofx');
  box.classList.toggle('focused', !!sel);
  rows.forEach((r, i) => {
    const st = r.el.style;
    if (!sel || r.own) {
      st.removeProperty('--fo');
      st.removeProperty('--ff');
      return;
    }
    const d = i < first ? first - i : i - last,
      b = r.label ? 0 : MOTION.blur(d);
    st.setProperty('--fo', r.label ? MOTION.dimLabel(d) : MOTION.dim(d));
    if (b) st.setProperty('--ff', 'blur(' + b + 'px)');
    else st.removeProperty('--ff');
  });
  if (!animate) {
    void box.offsetWidth;
    box.classList.remove('nofx');
  }
}
const SG_FS = 17;
function sgFit() {
  document.querySelectorAll('.sglines').forEach((box) => {
    const ls = [...box.querySelectorAll('.sgl')];
    ls.forEach((l) => {
      l.classList.remove('wrap');
      l.style.fontSize = '';
    });
    // lyrics are body size (17px) since 3.11; long lines shrink a little, then wrap
    let size = SG_FS;
    ls.forEach((l) => {
      if (l.scrollWidth > l.clientWidth + 1)
        size = Math.min(size, Math.floor(((SG_FS * l.clientWidth) / l.scrollWidth) * 2) / 2 - 0.5);
    });
    size = Math.max(14, size);
    if (size < SG_FS)
      ls.forEach((l) => {
        l.style.fontSize = size + 'px';
        if (l.scrollWidth > l.clientWidth + 1) l.classList.add('wrap');
      });
  });
}
// Q03 the marks sheet and its capsule sit over the song's column, and the page leaves room under its last line
function sgPlaceMenu() {
  const m = $('mksheet') || $('mkcap'),
    col = document.querySelector('#app .sgsong') || document.querySelector('.sgsong');
  document.body.classList.toggle('mkopen', !!$('mksheet'));
  document.body.classList.toggle('mkcapon', !!$('mkcap'));
  if (!m) return;
  if (col && split()) {
    // centred on the song's column (iPad and Mac), never past the screen's edges
    const r = col.getBoundingClientRect(),
      vw = document.documentElement.clientWidth,
      w = Math.min(430, r.width + 16, vw - 16);
    if (m.id === 'mksheet') m.style.width = w + 'px';
    const half = (m.id === 'mksheet' ? w : m.offsetWidth) / 2;
    m.style.left = Math.round(Math.max(8 + half, Math.min(vw - 8 - half, r.left + r.width / 2))) + 'px';
  } else {
    m.style.left = '';
    m.style.width = '';
  }
  if ($('mksheet')) document.documentElement.style.setProperty('--mkh', $('mksheet').offsetHeight + 'px');
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
  SG.sel = null;
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
  let est = false;
  if (moved) {
    sgSnap();
    const item = sg.order.splice(d.from, 1)[0];
    sg.order.splice(d.to, 0, item);
    // Q12: a timed section's line times become estimates (its start kept); no other section's times change
    est = ckMoved(sg, item.o);
    save();
  }
  SG.drag = null;
  sgSuppress = Date.now();
  rerender();
  if (moved) toast(est ? 'Section moved · times estimated' : 'Section moved');
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
    // tapping away from a focused section lets it melt back into the page (3.11)
    if (
      !el &&
      U.sSec &&
      !U.sEdit &&
      !rec &&
      !U.sheet &&
      songShown() &&
      e.target.closest &&
      e.target.closest('#app') &&
      !e.target.closest('.sgsec')
    ) {
      U.sSec = null;
      sgRefocus();
      return;
    }
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
      if (SG.sel && !e.target.closest('#mksheet, .toast, #barL, #barR, #barT')) {
        SG.sel = null;
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
  hxFadeIn.t = setTimeout(
    () => document.body.classList.remove('hxin'),
    400 + 60 * MOTION.STAGGER.word * MOTION.speed()
  );
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
  if (!ln.classList.contains('peeking')) DET.peek(ln);
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
      if (!ln.classList.contains('peeking')) DET.peek(ln);
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
   Escape closes menus, the selected word and search. Cmd/Ctrl+F opens Search (3.22), Cmd/Ctrl+N adds one,
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
      } else if (SG.sel) {
        SG.sel = null;
        rerender();
      } else if (U.tab === 'songs' && !U.view && (U.sFocus || (split() && U.sq))) endSearch();
      else if (U.sList) SG_ACT.sgListDone();
      return;
    }
    if (!mod || U.sheet || rec || (X && isFlow(U.view))) return;
    const k = e.key.toLowerCase();
    if (k === 'f') {
      // 3.22: Cmd/Ctrl+F opens Search (search.js)
      e.preventDefault();
      if (U.sEdit) sgEndEdit(true);
      FIND.open();
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
