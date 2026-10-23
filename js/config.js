/* Vocal Sessions · config.js
   App settings and fixed design: limits, focus areas and their colours, and the exercise icons.
   The practice content you might want to change (exercises, write-ups, words, goals, video timings, Toggl tags) is in content.js.
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

/* One glyph per exercise; tile colour = focus area */
const FOCUS_COL = {
  'cord-closure': '#007aff',
  register: '#8e5cf7',
  resonance: '#16a8a0',
  agility: '#f2a20c',
  blend: '#f0524a',
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
  (FOCUS_COL[e.focus] || '#8e8e93') +
  '">' +
  (GLYPH[e.id] || GLYPH.custom) +
  '</span>';
