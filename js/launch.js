/* Vocal Sessions · launch.js
   The launch ripple (3.13), the app's signature moment.
   On a cold launch (opening the app fresh, or the reload after an update) the icon's six sound-wave bars pulse in
   turn, the launch screen fades with a slight zoom, then Today's blocks rise in, top to bottom. Switching tabs and
   coming back to the app don't replay it; importing a backup does, on Today.
   - The bars are the <i> elements in #splash (index.html), drawn over the icon's plain background so they can move.
   - Today's blocks are the elements marked data-rise in scrToday() (screens.js), risen in the order they sit on screen.
   - Reduce Motion: no pulses or rises, the launch screen just fades. Motion off (the tests): exactly as before 3.13.
   - While it runs, LAUNCH.busy() is true and the floating window waits, so it appears after Today's rise. */
const LAUNCH = (() => {
  const BAR = { start: 120, gap: 70, ms: 520, peak: 1.5 }; // each bar pulses for 520 ms, 70 ms after the one before
  const FADE = { at: 860, ms: 300, zoom: 1.08 }; // the launch screen fades with a slight zoom
  const RISE = { after: 100, from: 16 }; // Today starts rising 100 ms into the fade, from 16 px down
  const SOFT_FADE = 200; // Reduce Motion: just a fade
  const MIN = 600; // the launch screen stays up at least this long (from the page opening), as before 3.13
  const CAP = 2500; // and at most about this long while recordings load

  let tpl = null, // a copy of the launch screen, for replaying after an import
    t0 = 0, // when this ripple started
    state = 'idle', // idle → showing (launch screen up) → rising (Today rising in) → idle
    endT = null,
    after = null; // what to do once the launch screen has gone (the import's toast)

  const moving = () => MOTION.on();
  const soft = () => MOTION.reduced() && MOTION.speed() > 0;
  const splash = () => document.getElementById('splash');
  const busy = () => state !== 'idle';

  function pulse(sp) {
    sp.querySelectorAll('i').forEach((b, k) =>
      MOTION.animate(
        b,
        [
          { transform: 'scaleY(1)' },
          { transform: 'scaleY(' + BAR.peak + ')', offset: 0.35 },
          { transform: 'scaleY(1)' },
        ],
        { ms: BAR.ms, delay: BAR.start + k * BAR.gap, easing: 'ease-in-out' }
      )
    );
  }

  // the cold launch: called from boot.js once the first screen is drawn
  function start() {
    const sp = splash();
    if (!sp) return;
    tpl = sp.cloneNode(true);
    t0 = performance.now();
    if (!moving() && !soft()) return; // motion off: the launch screen behaves as it always has
    state = 'showing';
    if (moving()) pulse(sp);
  }

  // how long to wait before hiding (never shorter than before 3.13), and the most to wait for recordings
  function minWait() {
    const fromStart = moving() ? FADE.at * MOTION.speed() - (performance.now() - t0) : 0;
    return Math.max(0, MIN - performance.now(), fromStart);
  }
  const capWait = () => Math.max(CAP, moving() ? t0 + FADE.at * MOTION.speed() - performance.now() + 200 : 0);

  // Today's blocks, in the order they sit on screen (top to bottom, then left to right on wide screens)
  function blocks() {
    if (U.view || U.tab !== 'today') return [];
    return [...document.querySelectorAll('#app [data-rise]')]
      .map((el) => ({ el, r: el.getBoundingClientRect() }))
      .filter((b) => b.r.height > 0 && b.r.bottom > 0 && b.r.top < innerHeight)
      .sort((a, b) => Math.round(a.r.top / 4) - Math.round(b.r.top / 4) || a.r.left - b.r.left)
      .map((b) => b.el);
  }

  function done() {
    state = 'idle';
    clearTimeout(endT);
    endT = null;
    if (typeof fwUpdate === 'function') fwUpdate(); // the floating window can appear now
    if (typeof DET !== 'undefined') DET.todayIn(); // the arch fills and the week row ripples
  }

  // the launch screen goes and Today rises in
  function finish() {
    const sp = splash();
    if (!sp || sp.dataset.going) return;
    sp.dataset.going = '1';
    const then = after;
    after = null;
    if (state === 'idle') {
      // motion off: as before 3.13
      sp.classList.add('out');
      setTimeout(() => sp.remove(), 500);
      if (then) then();
      return;
    }
    sp.style.pointerEvents = 'none'; // never block taps while it fades
    if (!moving()) {
      // Reduce Motion: just a short fade
      const a = sp.animate([{ opacity: 1 }, { opacity: 0 }], {
        duration: SOFT_FADE * MOTION.speed(),
        easing: 'ease-out',
        fill: 'forwards',
      });
      a.onfinish = () => {
        sp.remove();
        done();
      };
      endT = setTimeout(() => (sp.remove(), done()), SOFT_FADE * MOTION.speed() + 400);
      if (then) then();
      return;
    }
    state = 'rising';
    const fade = MOTION.animate(sp, [{ opacity: 1 }, { opacity: 0 }], {
      ms: FADE.ms,
      easing: 'cubic-bezier(.3,.7,.4,1)',
      fill: 'forwards',
    });
    MOTION.animate(
      sp.querySelector('.sp-icon'),
      [{ transform: 'scale(1)' }, { transform: 'scale(' + FADE.zoom + ')' }],
      { ms: FADE.ms, easing: 'cubic-bezier(.3,.7,.4,1)', fill: 'forwards' }
    );
    if (fade) fade.onfinish = () => sp.remove();
    const els = blocks();
    els.forEach((el, i) =>
      MOTION.animate(
        el,
        [
          { opacity: 0, transform: 'translateY(' + RISE.from + 'px)' },
          { opacity: 1, transform: 'none' },
        ],
        { spring: 'gentle', delay: RISE.after + MOTION.stagger(i, 'row'), fill: 'backwards' }
      )
    );
    const total = Math.max(
      FADE.ms,
      RISE.after + MOTION.stagger(Math.max(0, els.length - 1), 'row') + MOTION.dur('gentle') / MOTION.speed()
    );
    endT = setTimeout(
      () => {
        if (splash() === sp) sp.remove();
        done();
      },
      total * MOTION.speed() + 50
    );
    if (then) then();
  }

  // after an import lands on Today: the launch screen comes back for a moment and the ripple replays
  function replay(then) {
    if (!tpl || splash() || !moving() || U.view || U.tab !== 'today') {
      if (then) then();
      return;
    }
    const sp = tpl.cloneNode(true);
    document.body.insertBefore(sp, document.body.firstChild);
    after = then || null;
    state = 'showing';
    if (typeof fwUpdate === 'function') fwUpdate();
    MOTION.animate(sp, [{ opacity: 0 }, { opacity: 1 }], { ms: 180, easing: 'ease-out' });
    t0 = performance.now() + 180 * MOTION.speed();
    setTimeout(() => pulse(sp), 180 * MOTION.speed());
    setTimeout(finish, 180 * MOTION.speed() + FADE.at * MOTION.speed());
  }

  return { start, finish, replay, minWait, capWait, busy, BAR, FADE, RISE };
})();
