/* Vocal Sessions · config.js
   App settings and fixed design: limits, focus areas and their colours, and the exercise icons.
   The practice content you might want to change (exercises, write-ups, words, goals, video timings) is in content.js.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Config ===== */
const REPO = 'https://github.com/imperialfox/Vocal-Sessions',
  APP_URL = 'https://imperialfox.github.io/Vocal-Sessions/';
const UPDATE_DAY = '14 Oct'; // counts saved before this date have no dates
const OLD_ROT_IDS = ['falsetto', 'upperlower', 'rung', 'hinge', 'half', 'vertical', 'nasal', 'flex'];
const FOCI = ['cord-closure', 'register', 'resonance', 'agility', 'blend'];
const LONG_MINS = 90; // ask "how long did you actually practise?" past this
const MAX_TAKE = 120; // 3.20: every take is kept (the keep-last-3 rule is gone)
const VID_DEFAULT = 420,
  QUICK_STEP = 120; // own exercises ≈ 7 min; a step under 2 min means the form was filled in at the end
const FLOW = { found: 1, rot: 1, app: 1, song: 1 };
const isFlow = (v) => !!FLOW[v];
/* Q37 the song ladder: a section sung four ways, in this order (application.js). A ladder take keeps its rung's id in
   ext.rung, so never rename an id. lyr is the lyric view: faint words, the vowel letters picked out, or the words */
const RUNGS = [
  {
    id: 'trill',
    name: 'Lip trill',
    short: 'Trill',
    col: 'var(--sys-indigo)',
    lyr: 'faint',
    how: 'Sing the section on a lip trill. Keep it easy and let your lips do the work.',
  },
  {
    id: 'hum',
    name: 'Hum',
    short: 'Hum',
    col: 'var(--sys-teal)',
    lyr: 'faint',
    how: 'Now hum it on “ng”, lips lightly closed. Feel the buzz at the front of your face.',
  },
  {
    id: 'vowels',
    name: 'Vowels only',
    short: 'Vowels',
    col: 'var(--sys-orange)',
    lyr: 'vowels',
    how: 'Sing just the vowels of the words, joined up. Keep the trill’s easy feeling.',
  },
  {
    id: 'words',
    name: 'Words',
    short: 'Words',
    col: 'var(--sys-pink)',
    lyr: 'words',
    how: 'Now the real words. Hold on to what the trill felt like.',
  },
];
const rungOf = (id) => RUNGS.find((r) => r.id === id) || null;
// a take's rung, if it's a ladder take (an id this version doesn't know is an ordinary take)
const takeRung = (t) => (t && t.ext && typeof t.ext.rung === 'string' ? rungOf(t.ext.rung) : null);

/* One glyph per exercise; tile colour = focus area */
const FOCUS_COL = {
  'cord-closure': 'var(--sys-blue)',
  register: '#8e5cf7',
  resonance: '#16a8a0',
  agility: '#f2a20c',
  blend: 'var(--coral)',
};
const GL = (p) => '<svg viewBox="0 0 24 24" aria-hidden="true">' + p + '</svg>';
const GLYPH = {
  slides: GL('<path d="M3 18c3 0 4.5-12 9-12s6 12 9 12"/><path d="M3 21h18" opacity=".45"/>'),
  humming: GL(
    '<path d="M4.5 14c2.5-1.6 4.8-1.2 7.5 0 2.7-1.2 5-1.6 7.5 0"/><path d="M4.5 14c3 2.6 12 2.6 15 0"/><path d="M9 9V6.5M12 9V5M15 9V6.5"/>'
  ),
  lip: GL(
    '<path d="M2.5 13c2.3-3.2 6.2-3.2 8.5 0-2.3 3.2-6.2 3.2-8.5 0z"/><path d="M2.5 13H11"/><circle cx="15" cy="10" r="2"/><circle cx="19.5" cy="6" r="1.5"/><circle cx="19" cy="14.5" r="2.5"/>'
  ),
  falsetto: GL('<path d="M20 4c-8 0-13 5-13 12v4"/><path d="M20 4c0 8-5 12-13 12"/><path d="M7 16l7-7"/>'),
  upperlower: GL('<path d="M3 5h4v4h4v4h4v4h5"/><path d="M17 14l3 3-3 3"/>'),
  straw: GL('<path d="M5.5 9.5h13L17 21H7z"/><path d="M12 9.5 15 3h4"/><path d="M8 14h8" opacity=".45"/>'),
  rung: GL('<path d="M7 3v18M17 3v18M7 7.5h10M7 12h10M7 16.5h10"/>'),
  hinge: GL(
    '<path d="M5 21V4l8 2.5V21"/><path d="M10.5 13.5v1"/><path d="M16 9.5c1.3 1.4 1.3 3.6 0 5M19 7.5c2.6 2.6 2.6 6.4 0 9"/>'
  ),
  half: GL(
    '<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor" stroke="none"/>'
  ),
  vertical: GL('<ellipse cx="12" cy="12" rx="5" ry="8.5"/><path d="M9.2 16.2c1.8-1.4 3.8-1.4 5.6 0"/>'),
  nasal: GL(
    '<path d="M9.5 3c0 5-.5 7.5-3.5 11 0 2.2 2 3.5 4.5 3.5"/><path d="M14 10c1.6 1.2 1.6 3.8 0 5M17.5 8c3 2.4 3 6.6 0 9"/>'
  ),
  flex: GL('<path d="M2.5 16l3.5-5 3 3.5 3.5-8 3 5.5 3-3.5 3 4"/><circle cx="12" cy="6.5" r="1" fill="currentColor"/>'),
  custom: GL(
    '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M18.5 15.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>'
  ),
};
const tile = (e, big) =>
  '<span class="tile' +
  (big ? ' big' : '') +
  '" style="background:' +
  (FOCUS_COL[e.focus] || 'var(--sys-gray)') +
  '">' +
  (GLYPH[e.id] || GLYPH.custom) +
  '</span>';

/* The icons on the exercise page's facts (Q32), from the coach video's slides (tools/coach-video/slide.html). Drawn at
   24 × 24 with a 2 px stroke in the exercise's colour (darkened in light mode until it reads on white) */
const FACT_ICON = {
  target: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>',
  arrow: '<path d="M5 12h12M13 7l5 5-5 5"/>',
  wave: '<path d="M3 12c2.5-3 4.5-3 6 0s3.5 3 6 0 4.5-3 6 0"/>',
  up: '<path d="M12 19V6M6 11l6-6 6 6"/>',
  stop: '<circle cx="12" cy="12" r="8"/><path d="M8 8l8 8"/>',
  hand: '<path d="M6 12V7a1.5 1.5 0 0 1 3 0v4M9 11V5.5a1.5 1.5 0 0 1 3 0V11M12 11V6.5a1.5 1.5 0 0 1 3 0V12M15 12V9a1.5 1.5 0 0 1 3 0v4a7 7 0 0 1-7 7h-1a5 5 0 0 1-4-2l-3-4a1.5 1.5 0 0 1 2.3-1.9L6 15"/>',
  jaw: '<path d="M6.5 9.5c1.6-2.6 9.4-2.6 11 0"/><path d="M6 13c0 4.5 2.8 7.5 6 7.5s6-3 6-7.5"/><path d="M6 13h12"/>',
  mouth: '<path d="M3.5 12c3.2-4 13.8-4 17 0-3.2 4-13.8 4-17 0z"/><path d="M3.5 12h17"/>',
  head: '<circle cx="12" cy="8.5" r="4.5"/><path d="M4.5 20.5c1-4 4-6 7.5-6s6.5 2 7.5 6"/>',
  volume: '<path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z"/><path d="M15.5 9.5a3.5 3.5 0 0 1 0 5M18 7a7 7 0 0 1 0 10"/>',
  speed: '<path d="M4 17a8 8 0 1 1 16 0"/><path d="M12 17l4-5"/>',
  breath: '<path d="M3 9h11a3 3 0 1 0-3-3"/><path d="M3 14h15a3 3 0 1 1-3 3"/>',
  straw: '<path d="M7 9.5h10L15.5 21h-7z"/><path d="M12 9.5 15 3h4"/>',
  spark: '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7L12 6.3"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  next: '<circle cx="12" cy="12" r="8.5"/><path d="M10.5 8.5 14 12l-3.5 3.5"/>',
  ear: '<path d="M7 9a5 5 0 0 1 10 0c0 3-3 4-3 7a3 3 0 0 1-6 0"/><path d="M10 9a2 2 0 0 1 4 0"/>',
  repeat:
    '<path d="M4 11a8 8 0 0 1 14-4l2 2"/><path d="M20 4v5h-5"/><path d="M20 13a8 8 0 0 1-14 4l-2-2"/><path d="M4 20v-5h5"/>',
  note: '<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
};
