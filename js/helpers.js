/* Vocal Sessions · helpers.js
   Small helpers (dates, text, icons, layout), and the on-screen state (U).
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Helpers ===== */
const $ = (id) => document.getElementById(id);
const esc = (s) =>
  String(s == null ? '' : s).replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
  );
const mmss = (s) => {
  s = Math.max(0, Math.round(s));
  const m = Math.floor(s / 60),
    x = String(s % 60).padStart(2, '0');
  return m + ':' + x;
};
const hm = (m) => {
  m = Math.round(m);
  return m >= 60 ? Math.floor(m / 60) + 'h ' + (m % 60) + 'm' : m + 'm';
};
const monthKey = (d = new Date()) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
const monthMins = () => D.months[monthKey()] || 0;
const dayLabel = (iso) =>
  new Date(iso).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' });
const shortDate = (d) => new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
const fileDate = (d) => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
const timeOf = (d) => new Date(d).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
const allRot = () => ROT.concat(D.custom.map((c) => Object.assign({ custom: true }, c)));
const exById = (id) => FOUND.concat(allRot()).find((e) => e.id === id);
const sessEnd = (s) => s.end || s.date;
function startOfDay(d) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}
function weekStart(d) {
  const x = startOfDay(d);
  x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
  return x;
}
function relDay(iso) {
  const days = Math.round((startOfDay(new Date()) - startOfDay(iso)) / 864e5);
  if (days <= 0) return 'today';
  if (days === 1) return 'yesterday';
  if (days < 7) return days + ' days ago';
  return shortDate(iso);
}
function lastDone(id) {
  const e = D.ex[id];
  if (e && e.last) return 'last done ' + relDay(e.last);
  if (e && e.n) return 'last done before ' + UPDATE_DAY;
  return 'Not done yet';
}
// longest since last done: never done first, then practice from before dates were saved (fewest first), then the oldest date
function suggested() {
  const r = allRot();
  const score = (e) => {
    const x = D.ex[e.id];
    if (!x || (!x.n && !x.last)) return -2e13;
    if (!x.last) return -1e13 + (x.n || 0);
    return new Date(x.last).getTime();
  };
  return r.map((e, i) => ({ e, i, s: score(e) })).sort((a, b) => a.s - b.s || a.i - b.i)[0].e;
}
const isSong = () => !!X && X.kind === 'song';
// song practice is timed from its first take; until then it's only a choice of song and isn't kept
const unstarted = () => isSong() && !X.start;
function elapsedSec() {
  if (!X || !X.start) return 0;
  const now = X.paused ? X.pausedAt : Date.now();
  return Math.max(0, (now - X.start - (X.pausedTotal || 0)) / 1000);
}
const finalMins = () => (X && X.minsOverride ? X.minsOverride : Math.max(1, Math.round(elapsedSec() / 60)));
const clk = (s) => {
  s = Math.max(0, Math.floor(s));
  const h = Math.floor(s / 3600),
    m = Math.floor((s % 3600) / 60),
    x = String(s % 60).padStart(2, '0');
  return h ? h + ':' + String(m).padStart(2, '0') + ':' + x : m + ':' + x;
};
const noteStr = (n) =>
  !n ? '' : typeof n === 'string' ? n : (n.w || []).join(', ') + (n.t ? ((n.w || []).length ? ' — ' : '') + n.t : '');
const howStr = (ss) =>
  (ss.how || []).join(', ') + (ss.howNote ? ((ss.how || []).length ? ' — ' : '') + ss.howNote : '');
const exIds = (ss) =>
  FOUND.filter((e) => (ss.f || {})[e.id])
    .map((e) => e.id)
    .concat(Object.keys(ss.rot || {}).filter((id) => ss.rot[id]));
const wordList = (key, base) => base.concat((D.words[key] || []).filter((w) => !base.includes(w)));
const findSess = (id) => D.sessions.find((x) => x.id === id) || D.songSessions.find((x) => x.id === id);
const isoDay = (d) =>
  d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
function lastFor(id) {
  let m = null;
  D.sessions.forEach((s) => {
    if ((s.f && s.f[id]) || (s.rot && s.rot[id])) {
      const t = sessEnd(s);
      if (!m || new Date(t) > new Date(m)) m = t;
    }
  });
  return m;
}
// minutes per step: real timings when you tapped through, otherwise the coach video's lengths (scaled by levels done)
function vidSplit(ss) {
  const tot = +ss.mins || 0;
  let f = 0,
    r = 0;
  FOUND.forEach((e) => {
    const lv = +(ss.f || {})[e.id] || 0;
    f += (VID[e.id] * lv) / 3;
  });
  Object.keys(ss.rot || {}).forEach((id) => {
    const lv = +ss.rot[id] || 0;
    r += ((VID[id] || VID_DEFAULT) * lv) / 3;
  });
  f /= 60;
  r /= 60;
  if (f + r > tot && f + r > 0) {
    const k = tot / (f + r);
    f *= k;
    r *= k;
  }
  return { f, r, a: Math.max(0, tot - f - r), mixed: true };
}
function splitOf(ss) {
  const sp = ss.split,
    tot = +ss.mins || 0;
  if (!ss.mixed && sp && [sp.f, sp.r, sp.a].every((v) => isFinite(+v) && +v >= 0)) {
    const sum = +sp.f + +sp.r + +sp.a;
    if (sum > 0) {
      const k = tot / sum;
      return { f: sp.f * k, r: sp.r * k, a: sp.a * k, mixed: false };
    }
  }
  return vidSplit(ss);
}
function songWeek() {
  const ws = weekStart(new Date());
  const l = D.songSessions.filter((s) => new Date(s.date) >= ws);
  return { n: l.length, m: l.reduce((a, s) => a + s.mins, 0) };
}
function minsIn(from, to) {
  return D.sessions
    .filter((s) => {
      const t = new Date(s.date);
      return t >= from && t < to;
    })
    .reduce((a, s) => a + s.mins, 0);
}
function weekInfo() {
  const ws = weekStart(new Date()),
    we = new Date(ws);
  we.setDate(we.getDate() + 7);
  const mins = minsIn(ws, we);
  let streak = 0;
  const w = new Date(ws);
  for (let i = 0; i < 520; i++) {
    const a = new Date(w);
    a.setDate(a.getDate() - 7);
    if (minsIn(a, w) >= WEEK_TARGET) {
      streak++;
      w.setDate(w.getDate() - 7);
    } else break;
  }
  if (mins >= WEEK_TARGET) streak++;
  const days = new Set(D.sessions.map((s) => startOfDay(s.date).getTime()));
  return { ws, mins, streak, days };
}
const ICON = {
  mic: '<svg class="i" viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>',
  clock: '<svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  chart: '<svg class="i" viewBox="0 0 24 24"><path d="M5 20V11M10.5 20V5M16 20v-6M21.5 20H2.5"/></svg>',
  list: '<svg class="i" viewBox="0 0 24 24"><path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01"/></svg>',
  gear: '<svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
  back: '<svg class="i" viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>',
  down: '<svg class="i" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>',
  fwd: '<svg class="i" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>',
  gh: '<svg class="i" viewBox="0 0 24 24"><path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/></svg>',
  play: '<svg class="i" viewBox="0 0 24 24"><path d="M7 5v14l12-7z" fill="currentColor" stroke="none"/></svg>',
  pause: '<svg class="i" viewBox="0 0 24 24"><path d="M8 5v14M16 5v14"/></svg>',
  video:
    '<svg class="i" viewBox="0 0 24 24"><rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10 9.5v5l4.5-2.5z" fill="currentColor" stroke="none"/></svg>',
  star: '<svg class="i" viewBox="0 0 24 24"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/></svg>',
  share: '<svg class="i" viewBox="0 0 24 24"><path d="M12 15V3M8 7l4-4 4 4M6 11H5v10h14V11h-1"/></svg>',
  trash: '<svg class="i" viewBox="0 0 24 24"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></svg>',
  x: '<svg class="i" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  pen: '<svg class="i" viewBox="0 0 24 24"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>',
  save: '<svg class="i" viewBox="0 0 24 24"><path d="M12 3v12M8 11l4 4 4-4M5 21h14"/></svg>',
  okc: '<svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.5"/><path d="M7.5 12.5l3 3 6-6.5"/></svg>',
  warn: '<svg class="i" viewBox="0 0 24 24"><path d="M12 3.8L21.3 20H2.7z"/><path d="M12 10v4.5M12 17.4h.01"/></svg>',
  bad: '<svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.5"/><path d="M9 9l6 6M15 9l-6 6"/></svg>',
  check: '<svg class="i" viewBox="0 0 24 24" style="width:20px;height:20px"><path d="M5 12l5 5 9-10"/></svg>',
  plus: '<svg class="i" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
  circle: '<svg class="i" viewBox="0 0 24 24" style="width:24px;height:24px"><circle cx="12" cy="12" r="9.5"/></svg>',
  circleOn:
    '<svg class="i" viewBox="0 0 24 24" style="width:24px;height:24px"><circle cx="12" cy="12" r="10" fill="currentColor" stroke="none"/><path d="M7.5 12.2l3 3 6-6.4" stroke="#fff"/></svg>',
};
const chev = '<span class="mut" aria-hidden="true" style="font-size:20px">›</span>';
/* Layout: phone (compact), phone on its side (land), iPad or Mac window (reg), wide enough for a sidebar (wide) */
const MQ = {
  reg: matchMedia('(min-width:700px) and (min-height:501px)'),
  wide: matchMedia('(min-width:1100px) and (min-height:501px)'),
  land: matchMedia('(orientation:landscape) and (max-height:500px)'),
};
const split = () => MQ.reg.matches;
function layout() {
  const b = document.body.classList;
  b.toggle('reg', MQ.reg.matches);
  b.toggle('wide', MQ.wide.matches);
  b.toggle('land', MQ.land.matches && !MQ.reg.matches);
}
const TABS = () => [
  ['today', 'Today', ICON.mic],
  ['history', 'Progress', ICON.chart],
  ['exercises', 'Exercises', ICON.list],
  ['songs', 'Songs', SGI.music],
];
// Settings opens from the gear on Today, so it belongs to Today
const tabOf = (t) => (t === 'settings' ? 'today' : t);
const seg = (a, key, v) =>
  '<div class="seg" role="group"><span class="knob" aria-hidden="true"></span>' +
  [1, 2, 3]
    .map(
      (n) =>
        '<button data-a="' +
        a +
        '" data-k="' +
        esc(key) +
        '" data-v="' +
        n +
        '" class="' +
        (v === n ? 'on' : '') +
        '" aria-pressed="' +
        (v === n) +
        '" aria-label="Level ' +
        n +
        '">' +
        n +
        '</button>'
    )
    .join('') +
  '</div>';
const segF = (a, key, v) =>
  '<div class="seg" role="group"><span class="knob" aria-hidden="true"></span>' +
  [0, 1, 2, 3]
    .map(
      (n) =>
        '<button data-a="' +
        a +
        '" data-k="' +
        esc(key) +
        '" data-v="' +
        n +
        '" class="' +
        (n ? '' : 'sk ') +
        (v === n ? 'on' : '') +
        '" aria-pressed="' +
        (v === n) +
        '" aria-label="' +
        (n ? 'Level ' + n : 'Skip') +
        '">' +
        (n || 'Skip') +
        '</button>'
    )
    .join('') +
  '</div>';
const songTile =
  '<span class="tile" style="background:var(--coral)">' +
  GL('<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>') +
  '</span>';
const chipsHTML = (list, sel, key) =>
  '<div class="chips">' +
  list
    .map(
      (w) =>
        '<button class="chip' +
        (sel.includes(w) ? ' on' : '') +
        '" data-a="wTog" data-v="' +
        esc(w) +
        '" aria-pressed="' +
        sel.includes(w) +
        '">' +
        esc(w) +
        '</button>'
    )
    .join('') +
  '<button class="chip add" data-a="addWord" data-k="' +
  esc(key) +
  '">+ Your own</button></div>';
function noteBlock(id, val, ph) {
  if (U.noteOpen !== id && !val)
    return (
      '<button class="addnote" data-a="openNote" data-k="' + id + '">' + ICON.pen + '<span>Add a note</span></button>'
    );
  return (
    '<div class="notebox"><textarea class="field" id="' +
    id +
    '" maxlength="200" placeholder="' +
    esc(ph) +
    '" aria-label="Note">' +
    esc(val || '') +
    '</textarea></div>'
  );
}
// swipe-to-delete row wrapper
const sw = (inner, sheet, k) =>
  '<div class="sw" data-sw="1"><button class="swdel" data-a="sheet" data-v="' +
  sheet +
  '" data-k="' +
  esc(k) +
  '" tabindex="-1">Delete</button><div class="fg">' +
  inner +
  '</div></div>';

/* ===== UI state ===== */
const freshU = () => ({
  logOpen: [],
  logAll: false,
  logPick: null,
  logDrawn: false,
  range: 'W',
  roff: 0,
  pick: null,
  tab: 'today',
  view: null,
  exId: null,
  exTab: 'summary',
  sheet: null,
  sd: {},
  histTab: 'sessions',
  clock: false,
  noteOpen: null,
  calMonth: null,
  calDay: null,
  songId: null,
  sMode: 'practise',
  sEdit: null,
  sq: '',
  sFocus: false,
  sList: false,
  sSel: [],
  sDraft: null,
  sRet: null,
  sSec: null,
  sHint: 0,
  sOrder: 'start',
});
let U = freshU();
let E = null,
  bgSaved = false,
  lastLayerKey = '';
let rec = null,
  player = null,
  playingId = null,
  pendingImport = null,
  pendingExport = null;
