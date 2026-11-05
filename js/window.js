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
  vsize: 's', // Q26: the coach video's size (s, m or l), remembered on this device
  ctl: false, // Q26: the coach video's controls are showing
  tuck: null, // Q26: 'l' or 'r' while the window is tucked at that edge
};
try {
  const s = JSON.parse(localStorage.getItem(FW_KEY) || '{}');
  if (/^[tb][lr]$/.test(s.corner)) FW.corner = s.corner;
  if (/^[sml]$/.test(s.size)) FW.vsize = s.size;
} catch (e) {}
function fwSaveCorner() {
  try {
    localStorage.setItem(FW_KEY, JSON.stringify({ corner: FW.corner, size: FW.vsize }));
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
  // Q26: the name first (the section, or the song), the time below; the play/pause button shows the state
  return {
    k: where,
    t: clk(player.currentTime || 0),
    p: Math.min(1, (player.currentTime || 0) / d),
    on: !player.paused,
    open: 'Back to the take',
    label: 'Take, ' + where,
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
    // Q22: the session clock's ring, small, beside the step and its time. Q26: the step's name first, in the text
    // colour after a dot in the step's colour (the ring keeps its colours), and its time below; no "Paused ·"
    info() {
      const v = fwSessView(),
        m = SCLOCK.model(),
        s = m.steps[m.cur],
        name = isSong() ? 'Song practice' : s.name;
      return {
        k: name,
        t: clk(m.song ? m.e : s.secs),
        col: s.col,
        ring: SCLOCK.mini(),
        p: null,
        on: !X.paused,
        open: 'Back to ' + (isSong() ? 'song practice' : VIEWS[v][0]),
        label: isSong() ? 'Song practice' : 'Focused session, ' + name,
      };
    },
    draw(el, i) {
      if (FW.build !== 'session') {
        FW.build = 'session';
        el.innerHTML =
          '<button class="fwopen fwsess" data-a="fwOpen"><span class="fwring" aria-hidden="true"></span><span class="fwtx">' +
          '<span class="fwk"><i class="fwdot" aria-hidden="true"></i><span class="fwkn"></span></span><span class="fwt"></span></span></button>' +
          '<button class="fwbtn" data-a="fwToggle"></button>';
        FW.ring = '';
      }
      el.classList.toggle('paused', !i.on);
      fwOpenLabel(el, i);
      el.querySelector('.fwk').style.setProperty('--sc', 'var(' + i.col + ')');
      el.querySelector('.fwkn').textContent = i.k;
      el.querySelector('.fwt').textContent = i.t;
      if (FW.ring !== i.ring) el.querySelector('.fwring').innerHTML = FW.ring = i.ring;
      const b = el.querySelector('.fwbtn'),
        lab = i.on ? 'Pause' : 'Play';
      if (b.getAttribute('aria-label') !== lab) {
        b.setAttribute('aria-label', lab);
        b.innerHTML = i.on ? ICON.pause : ICON.play;
      }
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
// Q20: while Application records over the song's track, the window is the track, in red: what's playing under
// the take and where it's got to. It's only to see (nothing to tap but the drag), and it's never in FW_KINDS: it's
// the one window shown during a recording. Q26: a deeper red that white text reads on, "Track under your take" in
// normal case with a drawn note, and the same capsule and progress line as every other window
const FW_REC = {
  id: 'rectrack',
  active: () =>
    !!(rec && rec.app && rec.over && NOW.under() === 'track' && U.view === 'app' && typeof TRACK !== 'undefined' && TRACK.state().playing),
  own: () => false,
  info() {
    const sg = songById(rec.songId),
      st = TRACK.state();
    return {
      k: 'Track under your take',
      t: mmss(st.t),
      p: Math.min(1, st.t / Math.max(1, st.dur)),
      on: true,
      open: '',
      label: 'Track under your take, ' + (sg ? songTitle(sg) + ' · ' + APPL.secName(sg, rec.o) : 'track'),
      sub: sg ? songTitle(sg) + ' · ' + APPL.secName(sg, rec.o) : '',
    };
  },
  toggle() {},
  open() {},
  draw(el, i) {
    if (FW.build !== 'rectrack') {
      FW.build = 'rectrack';
      el.innerHTML =
        '<div class="fwrec"><span class="fwk">' +
        ICON.music +
        '<span>' +
        i.k +
        '</span></span><span class="fwtm"></span><span class="fwt"></span></div><span class="fwp" aria-hidden="true"><i></i></span>';
    }
    el.querySelector('.fwtm').textContent = i.t;
    el.querySelector('.fwt').textContent = i.sub;
    el.querySelector('.fwp i').style.width = (i.p * 100).toFixed(1) + '%';
  },
};
function fwGo(fn, y) {
  U.clock = false;
  fn();
  window.scrollTo(0, 0);
  render();
  window.scrollTo(0, y || 0);
}
const fwKindNow = () => (FW.shown === FW_REC.id ? FW_REC : FW_KINDS.find((k) => k.id === FW.shown));
// the window that should be on screen now, if any
function fwPick() {
  if (!D || U.sheet || U.clock || overlayOpen() || U.sFocus) return null;
  if (rec) return FW_REC.active() ? FW_REC : null; // Q20: during a recording, only the red track window
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
  if (k.tuck && k.tuck()) return; // Q19: the coach video over the session's page goes into its Coach pill
  FW.dis[k.id] = true;
  FW.shut = true;
  NOW.ended(k.id);
  k.close();
  fwUpdate();
}

/* ===== One sound at a time (3.20) =====
   Every sound starts through NOW: a take, a recording, the coach video, the song's track (its player or a song row's
   play button) and Song Clock's play-along. Starting one stops whatever was playing, and the stopped one's window
   stays closed until it's played again. The lock screen's play and pause follow whichever sound started last.
   Q16, the one exception: a recording started with over 'track' keeps the song's track playing under it (`under`).
   Stopping the recording leaves the track as the sound playing; anything else starting stops both. */
const NOW = (() => {
  let cur = null; // {kind, id, stop, over?}
  let under = null; // Q16: the track carrying on under a recording made over it
  let last = null; // the kind the lock screen controls
  const same = (a, b) => a.kind === b.kind && a.id === b.id;
  function halt(c, kind) {
    if (c.kind !== kind) FW.dis[c.kind] = true; // stopped by another sound: it doesn't wait in a window
    try {
      c.stop();
    } catch (e) {}
  }
  // over: the one kind that may carry on under this sound (Q16: a recording over the track)
  function start(kind, id, stop, over) {
    const me = { kind, id: id == null ? null : id, stop: stop || (() => {}) };
    // the track playing again during a recording made over it (the lock screen's play): it stays under the recording
    if (cur && cur.over && cur.over === kind) {
      if (under && !same(under, me)) {
        const u = under;
        under = null;
        halt(u, kind);
      }
      under = me;
      FW.dis[kind] = false;
      return;
    }
    const c = cur,
      u = under,
      keep = over && c && c.kind === over ? c : null;
    cur = null;
    under = null;
    if (c && c !== keep && !same(c, me)) halt(c, kind);
    if (u) halt(u, kind);
    under = keep;
    if (keep) me.over = over;
    cur = me;
    FW.dis[kind] = false; // an explicit play brings its window back
    FW.shut = false;
    last = kind;
    media();
  }
  // stop whatever plays (or only this kind), and the track under a recording with it
  function stop(kind) {
    if (!cur || (kind && cur.kind !== kind)) return;
    const c = cur,
      u = under;
    cur = null;
    under = null;
    try {
      c.stop();
    } catch (e) {}
    if (u)
      try {
        u.stop();
      } catch (e) {}
  }
  // a sound finished or was stopped from its own controls
  function ended(kind, id) {
    const is = (x) => x && x.kind === kind && (id == null || x.id === id);
    if (is(under)) under = null;
    else if (is(cur)) {
      // Q16: a recording made over the track ends, and the track it was made over is the sound playing again
      cur = under;
      under = null;
      if (cur) {
        last = cur.kind;
        media();
      }
    }
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
    under: () => (under ? under.kind : null), // Q16: the track under a recording made over it
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
  SCR.mark(el, 'overlay:window'); // Q36 its screen ID
  document.body.appendChild(el);
  FW.el = el;
  fwGestures(el);
  return el;
}
// Q26: a kind taking the window over starts from a clean window, so nothing one kind drew (a class such as hasx, an
// inline size, its markup) carries over to the next. Only what belongs to the window itself is kept
const FW_KEEP = ['fw', 'glass', 'dragging', 'pressed', 'tucked'];
function fwClean(el, id) {
  if (el.querySelector('video') && typeof COACH !== 'undefined') COACH.park(); // the coach video never goes with the old markup
  [...el.classList].forEach((c) => FW_KEEP.includes(c) || el.classList.remove(c));
  const tf = el.style.transform;
  el.removeAttribute('style');
  if (tf) el.style.transform = tf;
  Object.keys(el.dataset).forEach((d) => delete el.dataset[d]);
  el.dataset.kind = id;
  SCR.mark(el, 'overlay:window'); // Q36
  el.innerHTML = '';
  FW.build = '';
  fwCtl(false);
}
// Q26 (fix 16): only change an attribute that's really changed, so VoiceOver isn't told about it every second
function fwAttr(e, a, v) {
  if (e && e.getAttribute(a) !== v) e.setAttribute(a, v);
}
// Q26: the open button's steady label (where it goes and what it is); its time (#fwT) is its description, read when
// VoiceOver lands on it rather than every time it ticks
function fwOpenLabel(el, i) {
  const o = el.querySelector('.fwopen');
  if (!o) return;
  fwAttr(o, 'aria-label', i.open ? i.open + '. ' + i.label : i.label);
  const t = el.querySelector('.fwt');
  if (t) {
    t.id = 'fwT';
    fwAttr(o, 'aria-describedby', 'fwT');
  }
}
function fwDraw(k, i) {
  const el = fwEl(),
    b = k.id + '|' + i.on + '|' + (i.p != null) + '|' + !!k.close;
  if (el.dataset.kind !== k.id) fwClean(el, k.id);
  fwAttr(el, 'aria-label', i.label);
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
  fwOpenLabel(el, i);
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
  if (!k) {
    // Q26: nothing going at all (not just hidden by a sheet or a recording): the next window starts untucked
    if (FW.tuck && !rec && !FW_KINDS.some((x) => x.active())) fwTuckOff();
    return fwHide();
  }
  const was = FW.shown;
  // Q26: another kind takes over. A sound replacing another usually hides the window for a moment first (the old
  // sound stops before the new one plays), so a kind showing within FW_SWAP_GAP of another hiding counts too
  let snap = was && was !== k.id && FW.el && !FW.el.hidden ? fwSnap() : null;
  const gone = FW.gone;
  FW.gone = null;
  if (!was && gone && gone.kind !== k.id && Date.now() - gone.at < FW_SWAP_GAP) snap = gone.snap;
  fwDraw(k, k.info());
  FW.shown = k.id;
  if (!was && FW.tuck) {
    fwUnhide(); // Q26: tucked, it comes back as its tab
    fwPlace();
    fwTabShow(true);
  } else if (!was && !snap) fwShow();
  else if (was === k.id && !snap) fwPlaceSoon();
  else {
    if (!was) fwUnhide();
    fwPlace();
    if (snap) fwSwap(snap);
  }
}
// Q49 a draw that keeps the same window places it once on the next frame, not inside the draw: fwBounds reads the
// page's layout, which inside a draw made the browser lay out the new page early
let fwPlaceRaf = 0;
function fwPlaceSoon() {
  if (fwPlaceRaf) return;
  fwPlaceRaf = requestAnimationFrame(() => {
    fwPlaceRaf = 0;
    fwPlace();
  });
}
const FW_SWAP_GAP = 400; // ms
// the clock and the take's progress, without rebuilding anything
function fwTick() {
  const k = fwKindNow();
  if (!k) return;
  if (!k.active()) return fwUpdate();
  const i = k.info();
  fwDraw(k, i);
  if (FW.tuck) fwTabPaint(i);
}
// back on screen at once, any fade out stopped
function fwUnhide() {
  const el = FW.el;
  if (FW.hideAnim) {
    FW.hideAnim.cancel();
    FW.hideAnim = null;
  }
  clearTimeout(FW.hideTimer);
  el.hidden = false;
}
function fwShow() {
  const el = FW.el;
  fwUnhide();
  fwPlace(true);
  if (fwFades()) return el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: FW_FADE, easing: 'ease-out' }); // Q26
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
// Q26 (fix 12): with Reduce Motion the window fades in and out (0.2 s) instead of just appearing; with motion off
// (the tests' speed 0) it still just appears
const FW_FADE = 200;
const fwFades = () => MOTION.reduced() && MOTION.speed() > 0;
function fwHide() {
  const el = FW.el;
  if (!FW.shown) {
    // 3.17: a window left on screen with nothing in it (a fade that never finished) goes now
    if (el && !el.hidden && !FW.hideAnim) el.hidden = true;
    return;
  }
  // Q26: remembered for a moment, in case another kind takes the window straight back (fwPickAndDraw)
  FW.gone = el && !el.hidden ? { kind: FW.shown, at: Date.now(), snap: fwSnap() } : null;
  FW.shown = null;
  FW.drag = null;
  if (FW.stopSpring) FW.stopSpring();
  FW.stopSpring = null;
  el.classList.remove('dragging', 'pressed');
  fwSwapEnd();
  fwCtl(false);
  FW.pinch = null;
  fwTabShow(false);
  fwRoom();
  if (!MOTION.on() && !fwFades()) {
    el.hidden = true;
    return;
  }
  // shrinks and fades out, quicker than it came in (Q26: with Reduce Motion, a short fade)
  const base = el.style.transform;
  const a = fwFades()
    ? el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: FW_FADE, easing: 'ease-out', fill: 'forwards' })
    : MOTION.animate(
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
  if (FW.swap) return void (FW.swap.again = true); // Q26: placed once the change of kind has settled
  if (FW.shown === 'video' && !FW.pinch) fwVideoSize();
  fwSet(FW.tuck ? fwTuckXY() : fwCornerXY(FW.corner));
  if (FW.tuck) fwTabPlace();
  fwRoom();
}
// Q26 (fix 10): while the window sits in a bottom corner, every page gets room at its end for the window and its gap,
// so the last line can scroll clear of it (main::after in app.css)
function fwRoom() {
  const h = FW.shown && FW.el && !FW.el.hidden && FW.corner[0] === 'b' && !FW.tuck ? FW.el.offsetHeight + 12 : 0,
    v = h + 'px';
  if (FW.room !== v) document.documentElement.style.setProperty('--fwroom', (FW.room = v));
}

/* ===== Q26 (fix 13): one kind giving way to another =====
   A still copy of the old window (no ids or actions, the video as a dark box) fades out over the new one, while the
   window springs from the old size to the new in the same corner. With Reduce Motion, only the cross-fade */
function fwSnap() {
  const el = FW.el;
  if (!MOTION.on() && !fwFades()) return null;
  const g = el.cloneNode(true);
  g.removeAttribute('id');
  g.classList.add('fwghost');
  g.classList.remove('pressed', 'dragging');
  g.setAttribute('aria-hidden', 'true');
  g.inert = true;
  g.querySelectorAll('[id]').forEach((e) => e.removeAttribute('id'));
  g.querySelectorAll('[data-a]').forEach((e) => e.removeAttribute('data-a'));
  g.querySelectorAll('video').forEach((v) => v.replaceWith(Object.assign(document.createElement('div'), { className: 'fwvblack' })));
  return { g, w: el.offsetWidth, h: el.offsetHeight, pos: FW.pos ? { x: FW.pos.x, y: FW.pos.y } : null };
}
function fwSwap(s) {
  const el = FW.el;
  fwSwapEnd();
  if (!s.pos || FW.drag || FW.stopSpring || FW.tuck) return;
  const to = FW.pos,
    w = el.offsetWidth,
    h = el.offsetHeight,
    T = (p) => 'translate3d(' + p.x.toFixed(1) + 'px,' + p.y.toFixed(1) + 'px,0)',
    fadeOnly = !MOTION.on();
  s.g.style.transform = T(s.pos);
  document.body.appendChild(s.g);
  const ms = Math.round(MOTION.dur('gentle') / Math.max(0.01, MOTION.speed())),
    fade = fadeOnly ? FW_FADE : Math.min(220, ms);
  const anims = [
    s.g.animate([{ opacity: 1 }, { opacity: 0 }], { duration: fade, easing: 'ease-out', fill: 'forwards' }),
    el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: fade, easing: 'ease-in' }),
  ];
  if (!fadeOnly && (s.w !== w || s.h !== h || s.pos.x !== to.x || s.pos.y !== to.y)) {
    const sp = { duration: ms, easing: MOTION.ease('gentle') };
    anims.push(
      el.animate(
        [
          { width: s.w + 'px', height: s.h + 'px', transform: T(s.pos) },
          { width: w + 'px', height: h + 'px', transform: T(to) },
        ],
        sp
      ),
      s.g.animate(
        [
          { transform: T(s.pos), width: s.w + 'px', height: s.h + 'px' },
          { transform: T(to), width: w + 'px', height: h + 'px' },
        ],
        sp
      )
    );
  }
  FW.swap = { g: s.g, anims, again: false };
  Promise.all(anims.map((a) => a.finished.catch(() => {}))).then(() => {
    if (FW.swap && FW.swap.g === s.g) fwSwapEnd();
  });
}
// the change of kind has settled (or was cut short): the copy goes, and the window takes its place
function fwSwapEnd() {
  const s = FW.swap;
  if (!s) return;
  FW.swap = null;
  s.anims.forEach((a) => {
    try {
      a.cancel();
    } catch (e) {}
  });
  s.g.remove();
  if (s.again && FW.shown) fwPlace();
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
        return;
      }
      fwVTapGuard(e); // Q26
    },
    true
  );
  // Q26 (fix 14): the whole window presses down slightly when tapped, like a list row (its buttons have their own).
  // Not the coach video: a tap there shows its controls, and a scaled <video> loses a mouse's click in Chromium
  const unpress = () => el.classList.remove('pressed');
  el.addEventListener('pointerdown', (e) => {
    if (e.button > 0 || !FW.pos) return;
    fwSwapEnd(); // Q26: picked up mid-change: the change finishes at once
    // Q26: a second finger on the coach video pinches it between its three sizes
    if (e.isPrimary) FW.pts.clear(); // a first finger: anything left from before (a lift seen elsewhere) is gone
    FW.pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (FW.pts.size === 2 && FW.shown === 'video' && !FW.tuck) {
      FW.drag = null;
      el.classList.remove('dragging', 'pressed');
      const [a, b] = [...FW.pts.values()];
      FW.pinch = { d0: Math.max(20, Math.hypot(a.x - b.x, a.y - b.y)), w0: el.offsetWidth, w: el.offsetWidth };
      return;
    }
    if (FW.pinch) return;
    const b = e.target.closest && e.target.closest('button, [role=button]');
    if ((!b || b.classList.contains('fwopen')) && FW.shown !== 'video') el.classList.add('pressed');
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
    if (FW.pts.has(e.pointerId)) FW.pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (FW.pinch) return fwPinchMove();
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
      el.classList.remove('pressed');
      el.classList.add('dragging'); // Q26 (fix 15): lifted while held
    }
    d.pts.push({ x: e.clientX, y: e.clientY, t: e.timeStamp });
    while (d.pts.length > 2 && e.timeStamp - d.pts[0].t > 100) d.pts.shift();
    // follows the finger, kept on screen (Q26: up to three quarters off either side, to tuck it there)
    const vw = document.documentElement.clientWidth;
    fwSet({
      x: Math.max(-el.offsetWidth * 0.75, Math.min(vw - el.offsetWidth * 0.25, d.x0 + dx)),
      y: Math.max(0, Math.min(window.innerHeight - el.offsetHeight / 2, d.y0 + dy)),
    });
  });
  const end = (e) => {
    unpress();
    FW.pts.delete(e.pointerId);
    if (FW.pinch) {
      if (!FW.pts.size) fwPinchEnd();
      return;
    }
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
  el.addEventListener('pointerleave', unpress);
  // the coach video's picture is a button: Enter or Space shows its controls, as a tap does
  el.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('[role=button]')) {
      e.preventDefault();
      e.target.click();
    }
  });
}
// pick the corner it's thrown towards (where it is, plus where its speed would carry it), then spring there.
// Q26: dragged well off the left or right edge, or thrown off it once partly over, it tucks there instead
function fwThrow(v) {
  const B = fwBounds(),
    w = FW.el.offsetWidth,
    h = FW.el.offsetHeight,
    vw = document.documentElement.clientWidth,
    cx = FW.pos.x + w / 2 + v.x * 0.2,
    cy = FW.pos.y + h / 2 + v.y * 0.2,
    offL = Math.max(0, -FW.pos.x) / w,
    offR = Math.max(0, FW.pos.x + w - vw) / w,
    flat = Math.abs(v.x) > 2 * Math.abs(v.y), // a throw off the side is mostly sideways; a diagonal flick goes to a corner
    side =
      offL > FW_TUCK_OFF || (offL > 0.1 && flat && v.x < -FW_TUCK_V)
        ? 'l'
        : offR > FW_TUCK_OFF || (offR > 0.1 && flat && v.x > FW_TUCK_V)
          ? 'r'
          : null;
  FW.corner = (cy < (B.t + B.b) / 2 ? 't' : 'b') + (side || (cx < (B.l + B.r) / 2 ? 'l' : 'r'));
  fwSaveCorner();
  if (side) return fwTuckOn(side, v);
  FW.stopSpring = MOTION.spring(FW.pos, fwCornerXY(FW.corner), v, {
    spring: 'nav',
    frame: fwSet,
    done: () => {
      FW.stopSpring = null;
      fwPlace();
    },
  });
}

/* ===== Q26: tucked at the edge =====
   Dragged or thrown off the left or right edge, the window slides off and leaves a tab with an arrow at that edge.
   Its sound and timers carry on (a blue dot on the tab while something plays). Tapping the tab or pulling it out
   brings the window back to its corner on that side. Every kind can be tucked. */
const FW_TUCK_OFF = 0.35, // dragged this much of its width off the edge, it tucks when let go
  FW_TUCK_V = 600; // or thrown sideways off the edge this fast (px/s) once partly over
function fwTuckXY() {
  const p = fwCornerXY(FW.corner),
    vw = document.documentElement.clientWidth;
  return { x: FW.tuck === 'l' ? -FW.el.offsetWidth - 16 : vw + 16, y: p.y };
}
function fwTuckOn(side, v) {
  const el = FW.el;
  FW.tuck = side;
  fwCtl(false);
  el.classList.add('tucked');
  el.inert = true;
  el.setAttribute('aria-hidden', 'true');
  fwRoom();
  fwTabShow(true);
  FW.stopSpring = MOTION.spring(FW.pos, fwTuckXY(), v || { x: 0, y: 0 }, {
    spring: 'nav',
    frame: fwSet,
    done: () => {
      FW.stopSpring = null;
      fwPlace();
    },
  });
}
// back out to its corner on the side it was tucked, at the finger's speed if it was pulled out
function fwTuckOut(v) {
  if (!FW.tuck || !FW.shown) return;
  const el = FW.el;
  fwTuckOff();
  if (FW.stopSpring) FW.stopSpring();
  FW.stopSpring = MOTION.spring(FW.pos, fwCornerXY(FW.corner), v || { x: 0, y: 0 }, {
    spring: 'nav',
    frame: fwSet,
    done: () => {
      FW.stopSpring = null;
      fwPlace();
    },
  });
  // the tab has gone, so the keyboard (and VoiceOver) moves into the window it brought back
  const f = el.querySelector('button, [role=button]');
  if (f && FW.tab && FW.tab.contains(document.activeElement)) f.focus({ preventScroll: true });
}
function fwTuckOff() {
  const el = FW.el;
  FW.tuck = null;
  if (el) {
    el.classList.remove('tucked');
    el.inert = false;
    el.removeAttribute('aria-hidden');
  }
  fwTabShow(false);
  fwRoom();
}
// the tab: made once, on <body> beside the window
function fwTab() {
  if (FW.tab) return FW.tab;
  const t = document.createElement('button');
  t.id = 'fwtab';
  t.className = 'fwtab';
  t.dataset.a = 'fwTab';
  SCR.named(t); // Q48 tucked-window-tab
  t.hidden = true;
  t.innerHTML = '<span class="fwtabin" aria-hidden="true">' + ICON.fwd + '<i class="fwtabdot"></i></span>';
  document.body.appendChild(t);
  FW.tab = t;
  // pulled out: once the finger has moved inwards a little, the window comes out at its speed
  let p = null;
  t.addEventListener('pointerdown', (e) => {
    if (e.button > 0) return;
    p = { id: e.pointerId, x: e.clientX, t: e.timeStamp, done: false };
  });
  t.addEventListener('pointermove', (e) => {
    if (!p || p.done || e.pointerId !== p.id) return;
    const dx = (e.clientX - p.x) * (FW.tuck === 'r' ? -1 : 1);
    if (dx < 12) return;
    p.done = true;
    FW.moved = Date.now();
    const vx = ((e.clientX - p.x) / Math.max(16, e.timeStamp - p.t)) * 1000;
    fwTuckOut({ x: vx, y: 0 });
  });
  const up = () => (p = null);
  t.addEventListener('pointerup', up);
  t.addEventListener('pointercancel', up);
  t.addEventListener(
    'click',
    (e) => {
      if (Date.now() - FW.moved < 400) {
        e.stopPropagation();
        e.preventDefault();
      }
    },
    true
  );
  ['touchstart', 'touchmove'].forEach((n) => t.addEventListener(n, (e) => e.stopPropagation(), { passive: true }));
  return t;
}
function fwTabShow(on) {
  const t = on ? fwTab() : FW.tab;
  if (!t) return;
  if (!on) return void (t.hidden = true);
  const was = t.hidden;
  t.hidden = false;
  fwTabPlace();
  const k = fwKindNow();
  if (k) fwTabPaint(k.info());
  if (was) MOTION.animate(t, [{ opacity: 0 }, { opacity: 1 }], { spring: 'gentle', fade: true });
}
// at the window's edge, level with where the window would be
function fwTabPlace() {
  const t = FW.tab;
  if (!t || t.hidden || !FW.el) return;
  const dk = document.querySelector('.dock').getBoundingClientRect(),
    p = fwCornerXY(FW.corner),
    y = p.y + FW.el.offsetHeight / 2 - t.offsetHeight / 2;
  t.classList.toggle('r', FW.tuck === 'r');
  t.style.transform =
    'translate3d(' + (FW.tuck === 'r' ? dk.right - t.offsetWidth : dk.left).toFixed(1) + 'px,' + y.toFixed(1) + 'px,0)';
}
// its label says what it brings back; the blue dot shows while something plays
function fwTabPaint(i) {
  const t = FW.tab;
  if (!t) return;
  fwAttr(t, 'aria-label', 'Bring back the floating window: ' + i.label + (i.on ? ', playing' : ''));
  t.classList.toggle('on', !!i.on);
}

/* ===== Q26: the coach video, as picture in picture =====
   Just the picture. A tap shows its controls over the dimmed video (✕, open the player, −10 · play · +10 and
   L1 L2 L3), which fade after FW_CTL_MS; tapping again hides them. Three sizes: pinch between them, or double-tap
   for the next. The size is kept on this device. */
const FW_CTL_MS = 3000,
  FW_DTAP = 300, // ms between two taps that make a double-tap
  FW_VSIZES = ['s', 'm', 'l'];
// the width and height of a size: 176 pt, 264 pt, or the full width inside the margins (all 16:9, and never taller
// than the room it has)
function fwVideoDims(s) {
  const B = fwBounds(),
    room = Math.max(176, B.r - B.l),
    tall = Math.max(99, B.b - B.t);
  let w = s === 'l' ? room : s === 'm' ? 264 : 176;
  w = Math.min(w, room, (tall * 16) / 9);
  return { w: Math.round(w), h: Math.round((w * 9) / 16) };
}
function fwVideoSize() {
  const el = FW.el,
    d = fwVideoDims(FW.vsize);
  el.dataset.size = FW.vsize;
  if (el.style.width !== d.w + 'px') el.style.width = d.w + 'px';
  if (el.style.height !== d.h + 'px') el.style.height = d.h + 'px';
}
// to another size, springing from the size it is now in its corner
function fwVideoTo(s) {
  const el = FW.el;
  if (!el || FW.shown !== 'video') return;
  const from = { w: el.offsetWidth, h: el.offsetHeight, x: FW.pos.x, y: FW.pos.y };
  FW.vsize = s;
  fwSaveCorner();
  fwPlace();
  const to = { w: el.offsetWidth, h: el.offsetHeight, x: FW.pos.x, y: FW.pos.y },
    T = (p) => 'translate3d(' + p.x.toFixed(1) + 'px,' + p.y.toFixed(1) + 'px,0)';
  MOTION.animate(
    el,
    [
      { width: from.w + 'px', height: from.h + 'px', transform: T(from) },
      { width: to.w + 'px', height: to.h + 'px', transform: T(to) },
    ],
    { spring: 'gentle' }
  );
}
function fwPinchMove() {
  const [a, b] = [...FW.pts.values()];
  if (!a || !b) return;
  const P = FW.pinch,
    r = Math.hypot(a.x - b.x, a.y - b.y) / P.d0,
    lo = fwVideoDims('s').w,
    hi = fwVideoDims('l').w;
  P.w = Math.max(lo * 0.85, Math.min(hi * 1.05, P.w0 * r));
  const el = FW.el;
  el.style.width = P.w.toFixed(1) + 'px';
  el.style.height = ((P.w * 9) / 16).toFixed(1) + 'px';
  fwSet(fwCornerXY(FW.corner)); // grows from its corner
}
// let go: the nearest of the three sizes
function fwPinchEnd() {
  const P = FW.pinch;
  FW.pinch = null;
  FW.moved = Date.now();
  let best = FW.vsize,
    gap = Infinity;
  FW_VSIZES.forEach((s) => {
    const g = Math.abs(fwVideoDims(s).w - P.w);
    if (g < gap) (gap = g), (best = s);
  });
  fwVideoTo(best);
}
// the picture's tap: shows or hides the controls; a second tap straight after goes to the next size instead
function fwVTap() {
  const now = Date.now();
  if (now - (FW.vtap || 0) < FW_DTAP) {
    FW.vtap = 0;
    fwCtl(FW.vtapCtl);
    return fwVideoTo(FW_VSIZES[(FW_VSIZES.indexOf(FW.vsize) + 1) % 3]);
  }
  FW.vtap = now;
  FW.vtapCtl = FW.ctl;
  fwCtl(!FW.ctl);
}
// a second tap straight after the first shows the controls lands on whatever control is under the finger (play, in
// the middle of the bigger sizes): it's the double-tap, not that control
function fwVTapGuard(e) {
  if (FW.shown !== 'video' || !FW.vtap || Date.now() - FW.vtap >= FW_DTAP) return;
  const b = e.target.closest && e.target.closest('.fwvc button');
  if (!b) return;
  e.stopPropagation();
  e.preventDefault();
  fwVTap();
}
// the controls: shown (and the fade timer started again) or hidden. They stay while the keyboard or VoiceOver is in them
function fwCtl(on) {
  clearTimeout(FW.ctlTimer);
  FW.ctl = !!on && FW.shown === 'video';
  if (FW.el) FW.el.classList.toggle('ctl', FW.ctl);
  if (FW.ctl) FW.ctlTimer = setTimeout(fwCtlFade, FW_CTL_MS);
}
function fwCtlFade() {
  const a = document.activeElement;
  if (FW.el && a && FW.el.contains(a) && a.closest('.fwvc')) return void (FW.ctlTimer = setTimeout(fwCtlFade, FW_CTL_MS));
  fwCtl(false);
}

/* ===== Keeping it current ===== */
setInterval(() => {
  if (FW.shown === 'session') fwTick();
}, 1000);
window.addEventListener('resize', () => fwPlace());
FW.pts = new Map(); // Q26: the fingers on the window, for the pinch
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
// sheets, the clock and menus come and go in #layer (Q41: the parts kit's inside its .pk-layer)
new MutationObserver(() => fwUpdate()).observe($('layer'), { childList: true, subtree: true });
document.addEventListener('focusin', () => FW.shown && fwUpdate());
document.addEventListener('focusout', () => setTimeout(fwUpdate, 0));
