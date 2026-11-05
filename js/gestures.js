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

/* ===== Q53 Kit buttons: every button presses through the parts kit =====
   The press itself is the kit's (parts-kit.js › PRESS, css/parts-kit.css › the press). This gives each button its kit
   press class by what the button is, so a new button gets the press for free by having one of these classes:
   - GLASS (part 12, .pk-press): glass buttons grow 17 pt along their longest side (a 44 pt circle ×1.39) and light up.
   - BAR (part 15, .pk-press-bar): buttons on a glass bar (the iPad's top tabs, the track transport, the floating
     window's buttons, the pattern player's steps, the steppers' halves) only light up: the bar is the glass.
   - SOLID (part 14, .pk-press-solid): solid buttons shrink to --press (0.93) and come back on the release spring.
   - A chip that picks (part 18, .pk-chip) has no press, as in the kit; a chip that only acts (+ Your own) is SOLID.
   - Rows highlight (D06, row.press 'highlight') and aren't here.
   kind(el) says which one a button takes. A button gets its class as a finger first lands on it (capture, before the
   kit's own pointerdown) and keeps it; a redrawn button gets it again, and a button whose class was rewritten (the
   one-page session's main button) is put right. Not as it's drawn: a class added after a button's first style would
   start a scale transition from none to 1 on every button of every redraw. When the class changes, the style is read
   first, so the kit's press still eases in from rest.
   It replaces Q33's PRESS (retired in 3.67): tools/parts-kit/REPLACED.md. */
const KITPRESS = (() => {
  const GLASS =
    '.glass:is(.circ, .shbtn, .txtbtn, .cta, .trkpad, .trkpill, .ppill, .prep, .mktp), #timer[data-a="clock"]';
  const BAR = '.toptabs button, .trkb, .trkpp, .fwbtn, .pstep button, .pvstep .pk-stepper > button';
  const SOLID =
    '.cta, .circ, .shbtn, .txtbtn, .trkpad, .trkpill, .ppill, .prep, .pplay, .chip.add, .calbtn, .cal button, ' +
    '.nudge, .ckpi, .cktile, .sgplay, .sgtkb, .tkb, .tkbig, .cvpp, .cvpill, .ladnote, .ladrpt';
  const ALL = GLASS + ', ' + BAR + ', ' + SOLID;
  const KINDS = ['pk-press', 'pk-press-bar', 'pk-press-solid'];
  const ours = new WeakSet(); // the buttons this gave a class to (the kit's own markup keeps its own)

  const kind = (el) =>
    el.matches(GLASS) ? 'pk-press' : el.matches(BAR) ? 'pk-press-bar' : el.matches(SOLID) ? 'pk-press-solid' : null;
  // give el its kit press (or take ours away if it's no longer a button of these kinds); true when the class changed
  function tag(el) {
    const k = el.matches(ALL) ? kind(el) : null;
    if (!k && !ours.has(el)) return false;
    let changed = false;
    KINDS.forEach((c) => {
      if (c !== k && el.classList.contains(c)) {
        el.classList.remove(c);
        changed = true;
      }
    });
    if (k && !el.classList.contains(k)) {
      el.classList.add(k);
      changed = true;
    }
    if (k) ours.add(el);
    else ours.delete(el);
    return changed;
  }
  function tagIn(root) {
    if (root.nodeType !== 1) return;
    if (root.matches(ALL)) tag(root);
    root.querySelectorAll(ALL).forEach(tag);
  }
  // as a finger lands, before the kit's own press (capture, on the way down): the right class, read from rest
  document.addEventListener(
    'pointerdown',
    (e) => {
      const t = e.target && e.target.closest ? e.target : null;
      if (!t) return;
      const el = t.closest(ALL + ', .pk-press, .pk-press-bar, .pk-press-solid');
      if (el && tag(el)) {
        getComputedStyle(el).scale;
        getComputedStyle(el, '::after').opacity;
      }
    },
    { passive: true, capture: true }
  );

  return { GLASS, BAR, SOLID, ALL, kind, tag, tagIn };
})();
