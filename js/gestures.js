/* Vocal Sessions · gestures.js
   Pull to refresh, update checks, rotating and resizing, keyboard shortcuts, scrolling.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Pull to refresh (Today and History) =====
   Pull down at the top: the page follows your finger with resistance and the spinner's spokes appear.
   Past the threshold, let go: it holds, re-reads your data and checks GitHub for a newer version
   (loading it if there is one), then eases back. */
const PTR = { y: null, x: 0, on: false, d: 0, busy: false, lock: null },
  PT_TRIG = 56,
  PT_HOLD = 56;
(() => {
  const sp = $('spin');
  for (let i = 0; i < 8; i++) {
    const e = document.createElement('i');
    e.style.transform = 'rotate(' + i * 45 + 'deg)';
    sp.appendChild(e);
  }
})();
function ptrOK() {
  return (
    !U.view && !U.sheet && !U.clock && (U.tab === 'today' || U.tab === 'history') && window.scrollY <= 0 && !PTR.busy
  );
}
function ptrPaint(d, armed) {
  const a = $('app');
  a.style.transform = d ? 'translateY(' + d + 'px)' : '';
  const sp = $('spin');
  sp.style.opacity = d > 8 ? 1 : 0;
  const p = Math.min(1, d / PT_TRIG);
  [...sp.children].forEach((s, i) => {
    s.style.opacity = PTR.busy ? 1 - i * 0.11 : p * 8 > i ? (armed ? 1 - i * 0.09 : 0.75) : 0;
  });
}
document.addEventListener(
  'touchstart',
  (e) => {
    PTR.y = null;
    if (e.touches.length !== 1 || !ptrOK()) return;
    for (let n = e.target; n && n !== document.body; n = n.parentElement) if (n.scrollTop > 0) return;
    PTR.y = e.touches[0].clientY;
    PTR.x = e.touches[0].clientX;
    PTR.on = false;
    PTR.lock = null;
    PTR.d = 0;
    $('app').classList.remove('ptr-snap');
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (PTR.y === null || e.touches.length !== 1) return;
    const t = e.touches[0],
      dy = t.clientY - PTR.y,
      dx = t.clientX - PTR.x;
    if (PTR.lock === null) {
      if (dy <= 0 || Math.abs(dx) > Math.abs(dy)) {
        if (Math.abs(dx) > 6 || dy < -6) PTR.lock = 'no';
        return;
      }
      if (dy > 6) PTR.lock = 'pull';
    }
    if (PTR.lock === 'no') return;
    if (window.scrollY > 0) {
      PTR.y = null;
      return;
    }
    if (e.cancelable) e.preventDefault();
    if (PTR.lock !== 'pull') return;
    PTR.on = true;
    PTR.d = Math.max(0, 170 * (1 - 1 / (Math.max(0, dy) / 360 + 1)));
    ptrPaint(PTR.d, PTR.d >= PT_TRIG);
  },
  { passive: false }
);
function ptrEnd() {
  if (PTR.y === null) return;
  PTR.y = null;
  if (!PTR.on) return;
  PTR.on = false;
  const a = $('app');
  a.classList.add('ptr-snap');
  if (PTR.d < PT_TRIG) {
    ptrPaint(0);
    return;
  }
  PTR.busy = true;
  $('ptr').classList.add('go');
  ptrPaint(PT_HOLD, true);
  refreshApp().then((r) => {
    if (r === 'reload') return;
    $('ptr').classList.remove('go');
    PTR.busy = false;
    ptrPaint(0);
    setTimeout(() => a.classList.remove('ptr-snap'), 450);
  });
}
document.addEventListener('touchend', ptrEnd);
document.addEventListener('touchcancel', ptrEnd);
const cmpVer = (a, b) => {
  const x = a.split('.').map(Number),
    y = b.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    const d = (x[i] || 0) - (y[i] || 0);
    if (d) return d;
  }
  return 0;
};
async function refreshApp() {
  const t0 = Date.now();
  let newer = null;
  D = load();
  migrate();
  X = loadDraft();
  normX();
  await refreshTakes();
  try {
    const r = await fetch(location.href.split('#')[0], { cache: 'reload' });
    const m = (await r.text()).match(/APP_VERSION='([\d.]+)'/);
    if (m && cmpVer(m[1], APP_VERSION) > 0) newer = m[1];
  } catch (e) {}
  await new Promise((r) => setTimeout(r, Math.max(0, 700 - (Date.now() - t0))));
  if (newer) {
    toast('Updating to ' + newer + '…');
    setTimeout(() => location.reload(), 800);
    return 'reload';
  }
  render(true);
  return 'ok';
}
/* layout changes (rotating, resizing a window) */
Object.values(MQ).forEach((m) => {
  const f = () => {
    layout();
    if (split() && U.view === 'ex') {
      U.tab = 'exercises';
      U.view = null;
    }
    if (split() && U.view === 'lyr') {
      U.tab = 'songs';
      U.view = null;
    }
    if (split()) U.sFocus = false;
    else if ((U.sq || '').trim()) U.sFocus = true;
    render(true);
  };
  if (m.addEventListener) m.addEventListener('change', f);
  else if (m.addListener) m.addListener(f);
});
/* keyboard: Cmd + 1–4 (Ctrl off Apple devices) switch sections, by the tab bar's rules (Q13): not on a session's
   step or while recording (the tab bar isn't there then), not while typing or with a sheet or picker open, once per
   press, and with the same side effects as tapping the tab (sgTabTap) */
KEYS.add({
  when: (e) => KEYS.mod(e) && !e.altKey && /^[1-4]$/.test(e.key) && !(X && isFlow(U.view)),
  run(e) {
    const t = TABS()[+e.key - 1][0];
    U.clock = false;
    if (sgTabTap(t)) return;
    go(() => {
      U.tab = t;
      U.view = null;
    });
  },
});
// every shortcut goes through here (KEYS in helpers.js), after the other keydown listeners, so a key a control
// already handled (defaultPrevented) or stopped is left alone
document.addEventListener('keydown', KEYS.route);
/* a sheet or the clock keeps scrolling to itself: when it can't scroll any further that way (or the swipe is on
   the dimmed page around it), the page behind stays put. iOS ignores overscroll-behavior once nothing inside can
   scroll, so touches and the mouse wheel are checked here */
// Q41 the kit's overlays (Parts.open) or the session clock
const overlayOpen = () => Parts.open > 0 || !!$('lyc').firstElementChild;
// can something between el and the sheet (or clock) still scroll in direction dy (positive = further down)?
function canScrollIn(el, dy) {
  for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
    if (n.classList.contains('pk-dim') || n.classList.contains('clockscrim') || n.id === 'layer') return false;
    const oy = getComputedStyle(n).overflowY;
    if ((oy === 'auto' || oy === 'scroll') && n.scrollHeight > n.clientHeight + 1) {
      if (dy > 0 ? n.scrollTop + n.clientHeight < n.scrollHeight - 1 : n.scrollTop > 0) return true;
    }
    if (n.classList.contains('sheet') || n.classList.contains('pk-sheet') || n.classList.contains('clock')) return false;
  }
  return false;
}
let OT = null;
document.addEventListener(
  'touchstart',
  (e) => {
    OT = overlayOpen() && e.touches.length === 1 ? { x: e.touches[0].clientX, y: e.touches[0].clientY } : null;
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (!OT || e.touches.length !== 1 || !overlayOpen()) return;
    const t = e.touches[0],
      dx = t.clientX - OT.x,
      dy = OT.y - t.clientY;
    OT.x = t.clientX;
    OT.y = t.clientY;
    if (Math.abs(dy) <= Math.abs(dx) || e.target.closest('input[type=range]')) return; // sideways: swipes and sliders
    if (!canScrollIn(e.target, dy) && e.cancelable) e.preventDefault();
  },
  { passive: false }
);
document.addEventListener(
  'wheel',
  (e) => {
    if (!overlayOpen() || !e.deltaY || Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
    if (!canScrollIn(e.target, e.deltaY)) e.preventDefault();
  },
  { passive: false }
);
/* Q41 dragging a sheet down to close it is the parts kit's own (Parts.sheet: from its head, or from its content when
   that's at the top; a flick closes it) */
// live session clock
setInterval(() => {
  if (!X || !isFlow(U.view)) return;
  const t = $('timer');
  if (t) t.textContent = pillText();
  SCLOCK.tick(); // Q22: the session clock's ring and numbers, in place
}, 1000);
/* Q41 (D01) the tab bar never folds away (the parts kit's tabBar.fold is off): scrolling only brings the soft edge.
   Q45 the app scrolls the page, not a .pk-scroll box, so the kit's .pk-scrolled (its soft edge and small title, after
   36 pt) is set here */
// Q44 Today rests: its background shapes (.tgrad) hold still while the page scrolls (body.scrolling, until no scroll
// has come for SCROLL_REST ms, or scrollend) and while they're scrolled out of view (body.tg-away). app.css pauses them
const SCROLL_REST = 150;
let scrollRest = 0;
const scrolled = () => {
  clearTimeout(scrollRest);
  document.body.classList.remove('scrolling');
};
window.addEventListener(
  'scroll',
  () => {
    closeSwipes();
    const sc = window.scrollY > 36;
    $('bar').classList.toggle('scrolled', sc);
    $('bar').classList.toggle('pk-scrolled', sc);
    document.body.classList.toggle('scrolled', sc);
    document.body.classList.add('scrolling');
    clearTimeout(scrollRest);
    scrollRest = setTimeout(scrolled, SCROLL_REST);
    const g = document.querySelector('#app .tgrad');
    document.body.classList.toggle('tg-away', !!g && g.getBoundingClientRect().bottom <= 0);
  },
  { passive: true }
);
window.addEventListener('scrollend', scrolled, { passive: true });
// iOS pauses the mic when you leave the app, so stop and save the take, then say so on return
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    if (rec) {
      bgSaved = true;
      stopRec();
    }
  } else {
    if (!U.sheet && !rec) render(true);
    if (bgSaved) {
      bgSaved = false;
      setTimeout(() => toast('Your take was saved when you left the app'), 500);
    }
  }
});

/* ===== Q10 Hover hints on a Mac =====
   With a mouse or trackpad (never on touch), resting the pointer on an icon-only button shows a short label after a
   pause, as on the Mac. The label is the button's own spoken label (aria-label), so the two always agree. Used on
   both track player transports and the top bar's glass circles. */
const HINT_SEL = '#bar .circ[aria-label], .scirc[aria-label], .trktr button[aria-label], .trkpads button[aria-label]';
const HINT_WAIT = 600;
const HINT = { el: null, on: null, t: 0 };
const hintPointer = () => window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;
function hintShow(btn) {
  const text = btn.getAttribute('aria-label');
  if (!text || !btn.isConnected) return;
  let h = HINT.el;
  if (!h) {
    h = HINT.el = document.createElement('div');
    h.className = 'hint';
    h.id = 'hint';
    h.setAttribute('aria-hidden', 'true');
    document.body.appendChild(h);
  }
  h.textContent = text;
  h.classList.remove('show');
  const r = btn.getBoundingClientRect(),
    w = h.offsetWidth,
    hh = h.offsetHeight,
    below = r.top < 140, // the top bar's circles: below them; the transports at the bottom: above
    x = Math.max(8, Math.min(innerWidth - w - 8, r.left + r.width / 2 - w / 2)),
    y = below ? r.bottom + 8 : r.top - hh - 8;
  h.style.left = Math.round(x) + 'px';
  h.style.top = Math.round(y) + 'px';
  void h.offsetWidth;
  h.classList.add('show');
  HINT.on = btn;
}
function hintHide() {
  clearTimeout(HINT.t);
  HINT.t = 0;
  HINT.on = null;
  if (HINT.el) HINT.el.classList.remove('show');
}
document.addEventListener('pointerover', (e) => {
  if (e.pointerType !== 'mouse' || !hintPointer()) return;
  const b = e.target.closest && e.target.closest(HINT_SEL);
  if (!b || b === HINT.on) return;
  hintHide();
  HINT.t = setTimeout(() => hintShow(b), HINT_WAIT);
});
document.addEventListener('pointerout', (e) => {
  const b = e.target.closest && e.target.closest(HINT_SEL);
  if (b && !(e.relatedTarget && b.contains(e.relatedTarget))) hintHide();
});
['pointerdown', 'keydown', 'wheel'].forEach((k) => document.addEventListener(k, hintHide, { passive: true, capture: true }));
document.addEventListener('scroll', hintHide, { passive: true, capture: true });

/* ===== Q33 Glass press, as on iOS 27 =====
   One shared rule for every glass button, measured when it's pressed, so new glass buttons follow it automatically.
   - Glass buttons (GROW) grow by GROW_PT (17 pt) along their longest side: scale = 1 + 17 ÷ longest side (a 44 pt
     circle ×1.39, the 64 pt search circle ×1.27), from the centre, on MOTION's `press` spring, and are lifted above
     their neighbours until they've settled back on `release` (one small dip, no wobble). It uses the `scale`
     property, so it adds to any transform the button already has (the collapsed tab pill's).
   - Buttons that sit on a glass bar (ON_BAR: the tabs, the track transport, the floating window's play/pause, the
     pattern player's steps) don't change size: the bar is the glass. They only light up.
   - Both light up: a white layer under the icon (--lift-max: 30% light, 14% dark), in over LIFT_IN, out over LIFT_OUT.
   - Reduce Motion: no growth, the light-up still fades. Motion off (the tests): everything is instant.
   Solid and other non-glass buttons keep their own :active shrink in app.css. */
const PRESS = (() => {
  const GROW =
    '.glass:is(.circ, .shbtn, .txtbtn, .cta, .trkpad, .trkpill, .ppill, .prep, .mktp), #timer[data-a="clock"]';
  const ON_BAR = '.tabbar button, .toptabs button, .trkb, .trkpp, .fwbtn, .pstep button';
  const SEL = GROW + ', ' + ON_BAR;
  const GROW_PT = 17,
    LIFT_IN = 150,
    LIFT_OUT = 60;
  let cur = null; // {el, grow, s, keep: {position, zIndex}, sa, la}
  const live = new WeakMap(); // el → its press, still pressed or settling
  const ok = !!(document.documentElement.animate && 'scale' in document.documentElement.style);
  try {
    if (window.CSS && CSS.registerProperty)
      CSS.registerProperty({ name: '--lift', syntax: '<color>', inherits: false, initialValue: 'transparent' });
  } catch (e) {}

  const scaleFor = (el) => 1 + GROW_PT / Math.max(el.offsetWidth, el.offsetHeight, 1);
  const nowScale = (el) => {
    const v = getComputedStyle(el).scale;
    return v && v !== 'none' ? parseFloat(v) || 1 : 1;
  };
  const nowLift = (el) => getComputedStyle(el).getPropertyValue('--lift').trim() || 'transparent';
  const liftMax = () => getComputedStyle(document.documentElement).getPropertyValue('--lift-max').trim() || 'rgba(255,255,255,.3)';
  const ms = (n) => n * MOTION.speed();

  function target(e) {
    const t = e.target && e.target.closest ? e.target : null;
    const el = t && t.closest(SEL);
    if (!el || el.disabled || el.getAttribute('aria-disabled') === 'true') return null;
    return el;
  }
  function down(e) {
    if (!ok || (e.pointerType === 'mouse' && e.button !== 0)) return;
    const el = target(e);
    if (!el) return;
    if (cur && cur.el !== el) settle(cur, true);
    // pressed again while settling: carry on from where it is, keeping what it had before the first press
    const prev = live.get(el);
    let keep = { position: el.style.position, zIndex: el.style.zIndex };
    if (prev && !prev.done) {
      prev.done = true;
      keep = prev.keep;
      el.style.position = keep.position;
      el.style.zIndex = keep.zIndex;
    }
    const grow = el.matches(GROW) && !MOTION.reduced();
    const cs = getComputedStyle(el);
    const from = nowScale(el),
      lift = nowLift(el);
    if (prev) [prev.sa, prev.la].forEach((a) => a && a.cancel());
    const c = { el, grow, s: grow ? scaleFor(el) : 1, keep };
    cur = c;
    live.set(el, c);
    // lift it above its neighbours while it's bigger
    if (cs.position === 'static') el.style.position = 'relative';
    el.style.zIndex = cs.zIndex === 'auto' ? '10' : String(Math.max(10, (parseInt(cs.zIndex, 10) || 0) + 1));
    el.classList.add('pressing');
    if (grow)
      c.sa = el.animate([{ scale: String(from) }, { scale: String(c.s) }], {
        duration: MOTION.dur('press'),
        easing: MOTION.ease('press'),
        fill: 'forwards',
      });
    c.la = el.animate([{ '--lift': lift }, { '--lift': liftMax() }], {
      duration: ms(LIFT_IN),
      easing: 'ease-out',
      fill: 'forwards',
    });
  }
  function up() {
    if (cur) settle(cur, false);
  }
  // let go: back to rest on `release`, then put everything back. now: straight away (a new press, the app hidden)
  function settle(c, now) {
    if (cur === c) cur = null;
    const el = c.el;
    const done = () => {
      if (c.done) return;
      c.done = true;
      if (live.get(el) === c) live.delete(el);
      if (c.sa) c.sa.cancel();
      if (c.la) c.la.cancel();
      el.classList.remove('pressing');
      el.style.position = c.keep.position;
      el.style.zIndex = c.keep.zIndex;
      if (!el.getAttribute('style')) el.removeAttribute('style');
    };
    if (c.done) return;
    if (now || !el.isConnected) return done();
    const from = c.grow ? nowScale(el) : 1,
      lift = nowLift(el);
    if (c.sa) c.sa.cancel();
    if (c.la) c.la.cancel();
    const rd = c.grow ? MOTION.dur('release') : 0,
      ld = ms(LIFT_OUT);
    c.sa = c.grow
      ? el.animate([{ scale: String(from) }, { scale: '1' }], { duration: rd, easing: MOTION.ease('release'), fill: 'forwards' })
      : null;
    c.la = el.animate([{ '--lift': lift }, { '--lift': 'transparent' }], { duration: ld, easing: 'ease-in', fill: 'forwards' });
    const last = rd >= ld && c.sa ? c.sa : c.la;
    last.onfinish = done;
    last.oncancel = done;
  }

  document.addEventListener('pointerdown', down, { passive: true, capture: true });
  ['pointerup', 'pointercancel'].forEach((k) => window.addEventListener(k, up, { passive: true, capture: true }));
  window.addEventListener('blur', () => cur && settle(cur, true));
  document.addEventListener('visibilitychange', () => document.hidden && cur && settle(cur, true));

  return { GROW, ON_BAR, SEL, GROW_PT, LIFT_IN, LIFT_OUT, scaleFor, pressed: () => (cur ? cur.el : null) };
})();
