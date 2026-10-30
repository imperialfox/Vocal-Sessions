/* Vocal Sessions · window.js
   The floating window (3.12): a running session or a playing take stays in sight on every other screen,
   with a button to pause or play and a tap to go back to exactly where you were. Drag it to any corner.
   It lives in its own element (#fw), not in #layer, so the sheet scroll guards never mistake it for a sheet.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Floating window ===== */
const FW_KEY = 'vocalWindow'; // this device's corner, never backed up
const FW = {
  el: null,
  shown: null, // the kind on screen ('take', 'session') or null
  build: '', // what the markup was drawn for, so ticks only change text
  corner: 'br', // tl, tr, bl or br
  pos: null, // {x, y}, the window's top left on screen
  sess: null, // {view, y}: the session step you were on, and how far down
  take: null, // {id, place}: the take playing, and where it was started from
  drag: null,
  stopSpring: null,
  hideAnim: null,
  hideTimer: 0, // 3.17: the fallback that hides the window if its fade never finishes
  moved: 0,
  // 3.20: ✕ (or another sound starting, or pausing a sound on its own screen) leaves a kind closed until its next
  // explicit play (NOW.start). Nothing else clears it: not a tab switch, a redraw, a sheet, a reload or the app coming back
  dis: {},
  // 3.20: after ✕ nothing takes the closed window's place on this screen; cleared by the next change of screen (go())
  shut: false,
};
try {
  const c = JSON.parse(localStorage.getItem(FW_KEY) || '{}').corner;
  if (/^[tb][lr]$/.test(c)) FW.corner = c;
} catch (e) {}
function fwSaveCorner() {
  try {
    localStorage.setItem(FW_KEY, JSON.stringify({ corner: FW.corner }));
  } catch (e) {}
}

// where you are now, to come back to later
function fwHere() {
  let sd = {};
  try {
    sd = U.sheet ? JSON.parse(JSON.stringify(U.sd || {})) : {};
  } catch (e) {}
  return {
    tab: U.tab,
    view: U.view,
    songId: U.songId,
    sheet: U.sheet,
    sd,
    sMode: U.sMode,
    sSec: U.sSec,
    y: window.scrollY,
  };
}
const fwResumeView = () => (isSong() ? 'song' : X.fEnd ? (X.rEnd ? 'app' : 'rot') : 'found');
function fwSessView() {
  const v = FW.sess && FW.sess.view;
  if (isSong()) return 'song';
  return v === 'found' || v === 'rot' || v === 'app' ? v : fwResumeView();
}
function fwTakeInfo() {
  const t = TAKES.find((x) => x.id === playingId),
    sg = t && songById(t.songId),
    i = t && t.o && hasLyrics(sg) ? occIdx(sg, t.o) : -1;
  const where = i >= 0 ? occLabel(sg, i) : sg ? songTitle(sg) : 'Take';
  const d = isFinite(player.duration) && player.duration > 0 ? player.duration : (t && t.len) || 1;
  return {
    k: (player.paused ? 'Paused' : 'Playing') + ' · ' + where,
    t: clk(player.currentTime || 0),
    p: Math.min(1, (player.currentTime || 0) / d),
    on: !player.paused,
    open: 'Back to the take',
    label: 'Take ' + (player.paused ? 'paused' : 'playing'),
  };
}

// Each kind of window, in the order they win when more than one is going. active(): it's going; own(): you're on
// its own screen, so it isn't needed; info(): what it shows; toggle(): its button; open(): back to where you were.
// Song Clock's "Playing along" can be added as another kind. 3.16's coach video (coach.js) is put in between take
// and session; it has its own draw(), since its window holds the real video.
const FW_KINDS = [
  {
    id: 'take',
    active: () => !!(playingId && player && TAKES.some((t) => t.id === playingId)),
    own() {
      const p = FW.take && FW.take.id === playingId ? FW.take.place : null;
      if (!p || p.sheet) return false; // a take started in a sheet: the sheet is its screen, and sheets hide the window
      if (isFlow(p.view)) return U.view === p.view;
      return U.view === p.view && U.tab === p.tab && U.songId === p.songId;
    },
    info: fwTakeInfo,
    close() {
      stopPlayback();
      rerender();
    },
    toggle() {
      if (!player) return;
      if (player.paused) {
        const p = player;
        nowTake(playingId);
        if (p.ended || (isFinite(p.duration) && p.currentTime >= p.duration - 0.05)) p.currentTime = 0; // 3.20: again from 0:00
        p.play().catch(() => {
          if (player !== p) return;
          stopPlayback();
          toast('Couldn’t play this take');
          rerender();
        });
      } else player.pause();
    },
    open() {
      const t = TAKES.find((x) => x.id === playingId);
      let p = FW.take && FW.take.id === playingId ? FW.take.place : null;
      if (!p || (isFlow(p.view) && !X))
        p = { tab: 'songs', view: t && hasLyrics(songById(t.songId)) ? 'lyr' : null, songId: t && t.songId, y: 0 };
      fwGo(() => {
        U.tab = p.tab;
        U.view = p.view;
        U.songId = p.songId;
        if (p.sMode) U.sMode = p.sMode;
        if (p.sSec !== undefined) U.sSec = p.sSec;
        U.sheet = p.sheet || null;
        U.sd = p.sd || {};
      }, p.y);
    },
  },
  {
    id: 'session',
    active: () => !!(X && X.start),
    // 3.20: song practice's own screen includes the song's page, where its takes are recorded
    own: () => isFlow(U.view) || !!(isSong() && songShown() && songShown().id === X.song),
    info() {
      const v = fwSessView();
      return {
        k: isSong() ? 'Song practice' : 'Focused session · ' + VIEWS[v][0],
        t: (X.paused ? 'Paused · ' : '') + clk(elapsedSec()),
        p: null,
        on: !X.paused,
        open: 'Back to ' + (isSong() ? 'song practice' : VIEWS[v][0]),
        label: (isSong() ? 'Song practice' : 'Session') + (X.paused ? ' paused' : ' running'),
      };
    },
    toggle: () => togglePause(),
    open() {
      const v = fwSessView(),
        y = FW.sess && FW.sess.view === v ? FW.sess.y : 0;
      fwGo(() => {
        U.view = v;
        U.sheet = null;
        U.sd = {};
      }, y);
    },
  },
];
function fwGo(fn, y) {
  U.clock = false;
  fn();
  window.scrollTo(0, 0);
  render();
  window.scrollTo(0, y || 0);
}
const fwKindNow = () => FW_KINDS.find((k) => k.id === FW.shown);
// the window that should be on screen now, if any
function fwPick() {
  if (!D || U.sheet || U.clock || rec || overlayOpen() || U.sFocus) return null;
  if (typeof LAUNCH !== 'undefined' && LAUNCH.busy()) return null; // appears after the launch ripple (3.13)
  if (KEYS.typing()) return null; // keep the keyboard clear
  if (FW.shut) return null; // ✕ always visibly closes something: nothing pops up in its place (3.20)
  for (const k of FW_KINDS) if (!FW.dis[k.id] && k.active() && !k.own()) return k;
  return null;
}
// 3.20: the window shows a sound while it plays, and when it was paused from the window itself (or the lock screen).
// Paused anywhere else (its own screen, a song row, the takes sheet), you've seen it stop, so no window follows
function fwPaused(id) {
  if (Date.now() - (FW.winAt || 0) > 800) FW.dis[id] = true;
}
// 3.20: ✕ on the window, for every kind of sound: stops it, and nothing brings the window back but an explicit play
function fwClose() {
  const k = fwKindNow();
  if (!k || !k.close) return;
  FW.dis[k.id] = true;
  FW.shut = true;
  NOW.ended(k.id);
  k.close();
  fwUpdate();
}

/* ===== One sound at a time (3.20) =====
   Every sound starts through NOW: a take, a recording, the coach video, the song's track (its player or a song row's
   play button) and Song Clock's play-along. Starting one stops whatever was playing, and the stopped one's window
   stays closed until it's played again. The lock screen's play and pause follow whichever sound started last. */
const NOW = (() => {
  let cur = null; // {kind, id, stop}
  let last = null; // the kind the lock screen controls
  function start(kind, id, stop) {
    if (cur && !(cur.kind === kind && cur.id === id)) {
      const c = cur;
      cur = null;
      if (c.kind !== kind) FW.dis[c.kind] = true; // stopped by another sound: it doesn't wait in a window
      try {
        c.stop();
      } catch (e) {}
    }
    cur = { kind, id: id == null ? null : id, stop: stop || (() => {}) };
    FW.dis[kind] = false; // an explicit play brings its window back
    FW.shut = false;
    last = kind;
    media();
  }
  // stop whatever plays (or only this kind)
  function stop(kind) {
    if (!cur || (kind && cur.kind !== kind)) return;
    const c = cur;
    cur = null;
    try {
      c.stop();
    } catch (e) {}
  }
  // a sound finished or was stopped from its own controls
  function ended(kind, id) {
    if (cur && cur.kind === kind && (id == null || cur.id === id)) cur = null;
  }
  const kindOf = (id) => FW_KINDS.find((k) => k.id === id);
  function media() {
    if (!('mediaSession' in navigator) || last === 'rec') return;
    const ms = navigator.mediaSession,
      on = (a, f) => {
        try {
          ms.setActionHandler(a, f);
        } catch (e) {}
      };
    const k = () => kindOf(last),
      playing = () => {
        try {
          return !!(k() && k().active() && k().info().on);
        } catch (e) {
          return false;
        }
      };
    on('play', () => {
      FW.winAt = Date.now();
      if (k() && !playing()) k().toggle();
    });
    on('pause', () => {
      FW.winAt = Date.now();
      if (k() && playing()) k().toggle();
    });
  }
  return {
    start,
    stop,
    ended,
    kind: () => (cur ? cur.kind : null),
    id: () => (cur ? cur.id : null),
    last: () => last,
  };
})();
// a take starting (or carrying on) through the owner
function nowTake(id) {
  NOW.start('take', id, () => {
    if (playingId === id) {
      stopPlayback();
      rerender();
    }
  });
}

/* ===== Drawing it ===== */
function fwEl() {
  if (FW.el) return FW.el;
  const el = document.createElement('div');
  el.id = 'fw';
  el.className = 'fw glass';
  el.setAttribute('role', 'group');
  el.hidden = true;
  document.body.appendChild(el);
  FW.el = el;
  fwGestures(el);
  return el;
}
function fwDraw(k, i) {
  const el = fwEl(),
    b = k.id + '|' + i.on + '|' + (i.p != null) + '|' + !!k.close;
  el.setAttribute('aria-label', i.label);
  el.dataset.kind = k.id;
  if (k.draw) return k.draw(el, i); // a kind with its own look (3.16: the coach video holds the real video)
  if (FW.build !== b) {
    FW.build = b;
    el.innerHTML =
      '<button class="fwopen" data-a="fwOpen"><span class="fwk"></span><span class="fwt"></span></button>' +
      '<button class="fwbtn" data-a="fwToggle" aria-label="' +
      (i.on ? 'Pause' : 'Play') +
      '">' +
      (i.on ? ICON.pause : ICON.play) +
      '</button>' +
      (k.close ? '<button class="fwx" data-a="fwX" aria-label="Close">' + ICON.x + '</button>' : '') +
      (i.p != null ? '<span class="fwp" aria-hidden="true"><i></i></span>' : '');
  }
  el.classList.toggle('paused', !i.on);
  el.classList.toggle('hasx', !!k.close);
  el.querySelector('.fwopen').setAttribute('aria-label', i.open + '. ' + i.k + ', ' + i.t);
  el.querySelector('.fwk').textContent = i.k;
  el.querySelector('.fwt').textContent = i.t;
  const p = el.querySelector('.fwp i');
  if (p) p.style.width = (i.p * 100).toFixed(1) + '%';
}
// redraw after every render, sheet change or playback change
function fwUpdate() {
  fwPickAndDraw();
  if (typeof COACH !== 'undefined') COACH.place(); // the coach video goes where it's shown now (coach.js)
}
function fwPickAndDraw() {
  // remember the session step you're on (and its scroll, from the scroll listener)
  if (!X) FW.sess = null;
  else if (isFlow(U.view) && (!FW.sess || FW.sess.view !== U.view)) FW.sess = { view: U.view, y: window.scrollY };
  const k = fwPick();
  if (!k) return fwHide();
  fwDraw(k, k.info());
  const was = FW.shown;
  FW.shown = k.id;
  if (!was) fwShow();
  else fwPlace();
}
// the clock and the take's progress, without rebuilding anything
function fwTick() {
  const k = fwKindNow();
  if (!k) return;
  if (!k.active()) return fwUpdate();
  fwDraw(k, k.info());
}
function fwShow() {
  const el = FW.el;
  if (FW.hideAnim) {
    FW.hideAnim.cancel();
    FW.hideAnim = null;
  }
  clearTimeout(FW.hideTimer);
  el.hidden = false;
  fwPlace(true);
  const base = el.style.transform;
  MOTION.animate(
    el,
    [
      { opacity: 0, transform: base + ' translateY(14px) scale(.86)' },
      { opacity: 1, transform: base },
    ],
    { spring: 'gentle' }
  );
}
function fwHide() {
  const el = FW.el;
  if (!FW.shown) {
    // 3.17: a window left on screen with nothing in it (a fade that never finished) goes now
    if (el && !el.hidden && !FW.hideAnim) el.hidden = true;
    return;
  }
  FW.shown = null;
  FW.drag = null;
  if (FW.stopSpring) FW.stopSpring();
  FW.stopSpring = null;
  el.classList.remove('dragging');
  if (!MOTION.on()) {
    el.hidden = true;
    return;
  }
  // shrinks and fades out, quicker than it came in
  const base = el.style.transform;
  const a = MOTION.animate(
    el,
    [
      { opacity: 1, transform: base },
      { opacity: 0, transform: base + ' scale(.86)' },
    ],
    { ms: Math.round((MOTION.dur('gentle') / MOTION.speed()) * 0.45), easing: MOTION.ease('gentle'), fill: 'forwards' }
  );
  FW.hideAnim = a;
  if (!a) {
    el.hidden = true;
    return;
  }
  const done = () => {
    if (FW.hideAnim !== a) return; // shown again since, or already done
    FW.hideAnim = null;
    clearTimeout(FW.hideTimer);
    if (!FW.shown) el.hidden = true;
    try {
      a.cancel();
    } catch (e) {}
  };
  a.onfinish = done;
  // 3.17: hidden once the fade's time is up even if it never finishes (iOS could leave the window on screen)
  let d = 0;
  try {
    d = +a.effect.getTiming().duration || 0;
  } catch (e) {}
  clearTimeout(FW.hideTimer);
  FW.hideTimer = setTimeout(done, (d || 400) + 120);
}

/* ===== Where it sits ===== */
// the room it has: right of the sidebar, below the top bar, above the tab bar, Recall's hint capsule or the dock button
function fwBounds() {
  const dk = document.querySelector('.dock'),
    cs = getComputedStyle(dk),
    dr = dk.getBoundingClientRect(),
    inn = $('dock');
  const l = dr.left + parseFloat(cs.paddingLeft),
    r = dr.right - parseFloat(cs.paddingRight);
  const t = Math.max(0, $('bar').getBoundingClientRect().bottom) + 10;
  let b = dr.bottom - parseFloat(cs.paddingBottom);
  if (inn.firstElementChild) {
    b = Math.min(b, inn.getBoundingClientRect().top) - 12; // 3.23: the collapsed bar keeps the row's height
  }
  return { l, r, t, b };
}
function fwCornerXY(c) {
  const B = fwBounds(),
    w = FW.el.offsetWidth,
    h = FW.el.offsetHeight;
  return {
    x: Math.round(c[1] === 'l' ? B.l : Math.max(B.l, B.r - w)),
    y: Math.round(c[0] === 't' ? B.t : Math.max(B.t, B.b - h)),
  };
}
function fwSet(p) {
  FW.pos = { x: p.x, y: p.y };
  FW.el.style.transform = 'translate3d(' + p.x.toFixed(1) + 'px,' + p.y.toFixed(1) + 'px,0)';
}
function fwPlace(force) {
  if (!FW.shown && !force) return;
  if (FW.drag || FW.stopSpring) return;
  fwSet(fwCornerXY(FW.corner));
}

/* ===== Dragging to a corner ===== */
function fwGestures(el) {
  // the page's own touch handlers (pull to refresh, swiping rows) leave the window alone
  ['touchstart', 'touchmove'].forEach((t) => el.addEventListener(t, (e) => e.stopPropagation(), { passive: true }));
  // a drag isn't a tap
  el.addEventListener(
    'click',
    (e) => {
      if (Date.now() - FW.moved < 400) {
        e.stopPropagation();
        e.preventDefault();
      }
    },
    true
  );
  el.addEventListener('pointerdown', (e) => {
    if (e.button > 0 || !FW.pos) return;
    if (FW.stopSpring) {
      FW.stopSpring();
      FW.stopSpring = null;
    }
    FW.drag = {
      id: e.pointerId,
      sx: e.clientX,
      sy: e.clientY,
      x0: FW.pos.x,
      y0: FW.pos.y,
      on: false,
      pts: [{ x: e.clientX, y: e.clientY, t: e.timeStamp }],
    };
  });
  el.addEventListener('pointermove', (e) => {
    const d = FW.drag;
    if (!d || e.pointerId !== d.id) return;
    const dx = e.clientX - d.sx,
      dy = e.clientY - d.sy;
    if (!d.on) {
      if (Math.hypot(dx, dy) < 8) return;
      d.on = true;
      try {
        el.setPointerCapture(e.pointerId);
      } catch (x) {}
      el.classList.add('dragging');
    }
    d.pts.push({ x: e.clientX, y: e.clientY, t: e.timeStamp });
    while (d.pts.length > 2 && e.timeStamp - d.pts[0].t > 100) d.pts.shift();
    // follows the finger, kept on screen
    const vw = document.documentElement.clientWidth;
    fwSet({
      x: Math.max(4 - el.offsetWidth / 2, Math.min(vw - el.offsetWidth / 2 - 4, d.x0 + dx)),
      y: Math.max(0, Math.min(window.innerHeight - el.offsetHeight / 2, d.y0 + dy)),
    });
  });
  const end = (e) => {
    const d = FW.drag;
    if (!d || e.pointerId !== d.id) return;
    FW.drag = null;
    if (!d.on) return;
    FW.moved = Date.now();
    el.classList.remove('dragging');
    // the finger's speed over its last moments (px/s)
    const a = d.pts[0],
      z = d.pts[d.pts.length - 1],
      dt = Math.max(16, z.t - a.t);
    const v =
      e.type === 'pointercancel' ? { x: 0, y: 0 } : { x: ((z.x - a.x) / dt) * 1000, y: ((z.y - a.y) / dt) * 1000 };
    fwThrow(v);
  };
  el.addEventListener('pointerup', end);
  el.addEventListener('pointercancel', end);
}
// pick the corner it's thrown towards (where it is, plus where its speed would carry it), then spring there
function fwThrow(v) {
  const B = fwBounds(),
    w = FW.el.offsetWidth,
    h = FW.el.offsetHeight,
    cx = FW.pos.x + w / 2 + v.x * 0.2,
    cy = FW.pos.y + h / 2 + v.y * 0.2;
  FW.corner = (cy < (B.t + B.b) / 2 ? 't' : 'b') + (cx < (B.l + B.r) / 2 ? 'l' : 'r');
  fwSaveCorner();
  FW.stopSpring = MOTION.spring(FW.pos, fwCornerXY(FW.corner), v, {
    spring: 'nav',
    frame: fwSet,
    done: () => {
      FW.stopSpring = null;
      fwPlace();
    },
  });
}

/* ===== Keeping it current ===== */
setInterval(() => {
  if (FW.shown === 'session') fwTick();
}, 1000);
window.addEventListener('resize', () => fwPlace());
window.addEventListener(
  'scroll',
  () => {
    // how far down the session step (or the take's own screen) you are, to come back to
    if (U.sheet) return;
    if (X && FW.sess && isFlow(U.view) && FW.sess.view === U.view) FW.sess.y = window.scrollY;
    const tk = FW_KINDS[0];
    if (FW.take && tk.active() && tk.own()) FW.take.place.y = window.scrollY;
  },
  { passive: true }
);
// sheets, the clock and menus come and go in #layer
new MutationObserver(() => fwUpdate()).observe($('layer'), { childList: true });
document.addEventListener('focusin', () => FW.shown && fwUpdate());
document.addEventListener('focusout', () => setTimeout(fwUpdate, 0));
