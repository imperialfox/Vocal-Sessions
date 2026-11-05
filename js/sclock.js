/* Vocal Sessions · sclock.js
   The session clock (Q22, 3.42): the timer pill opens a ring you can read at a glance, in the one-page session's family.
   - One ring, three slices (Foundation, Rotation, Application in the step colours --cF, --cR, --cA), each as long as
     Ivan's usual time for that step (usual(): the median of the last 10 sessions with that step, or set times until
     there are 3). The step on now fills its slice as time passes; a tick marks where its slice ends ("Usual move-on").
     A logged step fills its whole slice, however short it was, and going past the usual length changes nothing.
     Song practice is one slice round the whole ring, with no tick.
   - Paused: the ring breathes (not with Reduce Motion), the numbers go grey, the main button is Resume.
   - Finish from the clock: the ring closes and settles into Session saved's own line (SAVED.line()), with Done.
   - It zooms out of the timer pill and closes back into it: ✕, the dimmed page, Escape, or a swipe sideways anywhere
     on it (it follows the finger and shrinks towards the pill; past a fifth of its width or a flick closes it).
     Anything marked data-own-gesture (the step-time slider) keeps its own gesture.
   - The floating window shows the same ring, small (mini()).
   - A running session keeps the screen on (AWAKE, helpers.js), with a "Screen stays on" chip at the start and on
     Resume; it lets go when paused or finished, and says nothing if the phone refuses.
   - "Were you away?": after more than AWAY_MIN minutes away (the draft's `seen`, stamped while the app is on screen),
     a sheet asks whether to take the time out. Nothing changes unless Ivan says so.
   - Undo after a Log tap (logged()), fixing a finished step's time (hold and slide), "Session picked up" on reopening,
     and tapping the big number to swap the total and the step's time (kept on this device in vocalClock).
   Step ends stay exact: an Undo puts back the stamps as they were; a time fix or Take it out moves the uncounted time
   (X.pausedTotal) and every later stamp by the same amount, so each step keeps its own length and Progress's split is
   worked out from them as before.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */
const SCLOCK = (() => {
  const q = (s) => document.querySelector(s);
  // [view, name, colour, the split's key]
  const STEPS = [
    ['found', 'Foundation', '--cF', 'f'],
    ['rot', 'Rotation', '--cR', 'r'],
    ['app', 'Application', '--cA', 'a'],
  ];
  const FALL = { f: 22, r: 19, a: 14, s: 20 }, // usual minutes until there are 3 sessions with that step
    NEED = 3,
    RECENT = 10,
    AWAY_MIN = 10, // minutes away before the clock asks
    UNDO_MS = 5000,
    SWIPE_CLOSE = 0.2, // of the clock's width
    FLICK = 0.45, // px per ms
    SEEN_EVERY = 15000, // how often the draft notes the app is still on screen
    KEY = 'vocalClock'; // this device: {swap: true} when the big number shows the step's time
  const R = 70,
    C = 2 * Math.PI * R,
    GAP = 7;
  let prefs = {};
  try {
    prefs = JSON.parse(localStorage.getItem(KEY) || '{}') || {};
  } catch (e) {}
  let fix = null, // the step time being fixed: {i, v (minutes), was (seconds), min, max}
    fin = null, // finished from the clock: {k, m, mins}
    undo = null, // the last Log, for its Undo toast
    away = null, // {gap, at, st, shown}: time away, waiting to be asked about
    pill = null, // where the timer pill was when the clock opened
    chip = false, // say "Screen stays on" once the screen is kept on
    sw = null, // a sideways swipe on the clock
    swipedAt = 0,
    slide = null, // the step-time slider being held
    seenAt = 0,
    lastRing = '';

  /* ----- usual lengths ----- */
  function median(a) {
    a = a.slice().sort((x, y) => x - y);
    const n = a.length;
    return n % 2 ? a[(n - 1) / 2] : (a[n / 2 - 1] + a[n / 2]) / 2;
  }
  // minutes: each step's median over the last 10 sessions that had it (split worked out at the time), or FALL
  let usualKey = '',
    usualVal = null;
  function usual() {
    const key = (D.sessions || []).length + '|' + (D.songSessions || []).length;
    if (key === usualKey && usualVal) return usualVal;
    usualKey = key;
    return (usualVal = usualNow());
  }
  function usualNow() {
    const byDate = (a, b) => new Date(a.date) - new Date(b.date),
      out = {};
    const ss = (D.sessions || []).filter((s) => s.split && !s.mixed).sort(byDate);
    ['f', 'r', 'a'].forEach((k) => {
      const v = ss
        .filter((s) => +s.split[k] > 0)
        .slice(-RECENT)
        .map((s) => +s.split[k]);
      out[k] = v.length >= NEED ? median(v) : FALL[k];
    });
    const sp = (D.songSessions || [])
      .filter((s) => +s.mins > 0)
      .sort(byDate)
      .slice(-RECENT)
      .map((s) => +s.mins);
    out.s = sp.length >= NEED ? median(sp) : FALL.s;
    return out;
  }

  /* ----- where the session is ----- */
  // the steps with their times (seconds), from the stamps: the clock never guesses
  function model() {
    const e = elapsedSec(),
      u = usual();
    if (isSong())
      return { song: true, e, cur: 0, steps: [{ name: 'Song practice', col: '--cA', secs: e, usual: u.s * 60, cur: true }] };
    const fE = Math.min(e, X.fE || 0),
      rE = Math.min(e, Math.max(fE, X.rE || fE)),
      cur = X.fEnd ? (X.rEnd ? 2 : 1) : 0,
      secs = [cur === 0 ? e : fE, cur === 1 ? e - fE : cur > 1 ? rE - fE : 0, cur === 2 ? e - rE : 0];
    return {
      song: false,
      e,
      cur,
      steps: STEPS.map((s, i) => ({
        name: s[1],
        col: s[2],
        secs: Math.max(0, secs[i]),
        usual: u[s[3]] * 60,
        done: i < cur,
        cur: i === cur,
      })),
    };
  }
  const fillOf = (s) => (s.done ? 1 : s.cur ? Math.min(1, s.secs / Math.max(1, s.usual)) : 0);
  const mins = (s) => Math.max(1, Math.round(s / 60));

  /* ----- the ring ----- */
  // one slice (its track, or its fill): f is how full it is, whole the slice's full length
  function arc(cls, i, len, at, col, sw, f, whole) {
    return (
      '<circle class="' +
      cls +
      '" data-i="' +
      i +
      '"' +
      (f != null ? ' data-f="' + f.toFixed(3) + '" data-len="' + whole.toFixed(2) + '"' : '') +
      ' cx="90" cy="90" r="' +
      R +
      '" fill="none" stroke="' +
      col +
      '" stroke-width="' +
      sw +
      '" stroke-dasharray="' +
      len.toFixed(2) +
      ' ' +
      (C - len).toFixed(2) +
      '" stroke-dashoffset="' +
      (-at).toFixed(2) +
      '"/>'
    );
  }
  // o: {mini, fills (override), all (draw every fill, for the closing ring)}
  function ringSVG(m, o) {
    o = o || {};
    const n = m.steps.length,
      gap = n > 1 ? GAP : 0,
      tot = m.steps.reduce((a, s) => a + s.usual, 0),
      avail = C - n * gap,
      sw = o.mini ? 22 : 14;
    let at = gap / 2,
      g = '',
      tk = '';
    m.steps.forEach((s, i) => {
      const len = n > 1 ? (s.usual / tot) * avail : C,
        f = o.fills ? o.fills[i] : fillOf(s);
      g += arc('sl', i, len, at, 'var(--sck-track)', sw);
      if (o.all || f * len > 0.5) g += arc('sf', i, f * len, at, 'var(' + s.col + ')', sw, f, len);
      // the tick where the step on now usually moves on
      if (s.cur && !m.song && !o.mini && !o.noTick) {
        const a = ((at + len) / C) * 2 * Math.PI - Math.PI / 2,
          x = (r) => (90 + r * Math.cos(a)).toFixed(1),
          y = (r) => (90 + r * Math.sin(a)).toFixed(1);
        tk = '<line class="scktk" x1="' + x(58) + '" y1="' + y(58) + '" x2="' + x(82) + '" y2="' + y(82) + '"/>';
      }
      at += len + gap;
    });
    return '<svg viewBox="0 0 180 180" aria-hidden="true"><g transform="rotate(-90 90 90)"><g class="scksl">' + g + '</g></g>' + tk + '</svg>';
  }
  // the floating window's ring: the same shape, small
  const mini = () => (X && X.start ? ringSVG(model(), { mini: true }) : '');

  /* ----- the clock ----- */
  const can = () => (!!fin && U.view === 'saved') || !!(X && X.start && isFlow(U.view));
  function centre(m) {
    if (fin) return '<b class="sckbig">' + fin.mins + ' min</b><small>Session saved</small>';
    const s = m.steps[m.cur],
      big = (t, col) => '<b class="sckbig' + (t.length > 5 ? ' long' : '') + '"' + (col ? ' style="color:var(' + col + ')"' : '') + '>' + t + '</b>';
    if (X.paused)
      return big(clk(m.e)) + '<small class="sckp">Paused · for ' + mins((Date.now() - (X.pausedAt || Date.now())) / 1000) + ' min</small>';
    if (m.song) return big(clk(m.e)) + '<small>Song practice</small>';
    if (prefs.swap) return big(clk(s.secs), s.col) + '<small>Total ' + clk(m.e) + '</small>';
    return big(clk(m.e)) + '<small style="color:var(' + s.col + ')">' + s.name + ' · ' + clk(s.secs) + '</small>';
  }
  function centreLabel(m) {
    if (fin) return 'Session saved, ' + fin.mins + ' minutes';
    const s = m.steps[m.cur];
    if (X.paused) return 'Paused at ' + clk(m.e);
    if (m.song) return 'Song practice, ' + clk(m.e);
    return (
      'Total ' + clk(m.e) + ', ' + s.name + ' ' + clk(s.secs) + '. Tap to show the ' + (prefs.swap ? 'total' : 'step’s time') + ' first'
    );
  }
  function sub(m) {
    if (fin) return SAVED.line();
    if (X.paused) return 'Paused time isn’t counted';
    if (m.song) return 'Started at ' + timeOf(X.start);
    return 'Usual move-on ~' + Math.round(m.steps[m.cur].usual / 60) + ' min';
  }
  function editor(i, s) {
    const f = fix,
      p = (f.v - f.min) / Math.max(1, f.max - f.min);
    return (
      '<div class="sckfix" style="--sc:var(' +
      s.col +
      ')"><div class="sckfh"><span>Hold and slide</span><b id="sckFixV">' +
      f.v +
      ' min</b></div><div class="sckslider" id="sckSlider" data-own-gesture role="slider" tabindex="0" aria-label="' +
      s.name +
      '’s time in minutes" aria-valuemin="' +
      f.min +
      '" aria-valuemax="' +
      f.max +
      '" aria-valuenow="' +
      f.v +
      '" style="--p:' +
      p.toFixed(4) +
      '"><i class="sckrail"></i><i class="sckfill"></i><i class="sckknob"></i></div><div class="sckff"><span>Logged ' +
      mins(f.was) +
      ' min</span><button class="sckfs" data-a="sckFixSave">Save time</button></div></div>'
    );
  }
  function rows(m) {
    return m.steps
      .map((s, i) => {
        const on = s.done || s.cur || !!fin,
          t = fin ? clk(fin.m.steps[i].secs) : on ? clk(s.secs) : '~' + Math.round(s.usual / 60) + ' min',
          canFix = s.done && !fin && !m.song;
        return (
          '<div class="sckrow' +
          (s.cur && !fin ? ' cur' : '') +
          (on ? '' : ' todo') +
          '" style="--sc:var(' +
          s.col +
          ')"><span class="sckn">' +
          s.name +
          '</span>' +
          (canFix
            ? '<button class="sckt fixable' +
              (fix && fix.i === i ? ' on' : '') +
              '" data-a="sckFix" data-k="' +
              i +
              '" aria-label="' +
              s.name +
              ' took ' +
              t +
              '. Tap to fix its time">' +
              t +
              '</button>'
            : '<span class="sckt">' + t + '</span>') +
          '</div>' +
          (fix && fix.i === i && canFix ? editor(i, s) : '')
        );
      })
      .join('');
  }
  function mainBtn(m) {
    if (fin) return '<button class="cta ink sckmain" data-a="sckDone">Done</button>';
    if (X.paused) return '<button class="cta glass tinted sckmain" data-a="sckMain">Resume</button>';
    return (
      '<button class="cta glass ' +
      (m.song ? 'tinted' : OP.look()) +
      ' sckmain" data-a="sckMain">' +
      esc(m.song ? 'Save song practice' : OP.label()) +
      '</button>'
    );
  }
  function html() {
    const m = fin ? fin.m : model(),
      paused = !fin && X.paused;
    lastRing = fin ? '' : ringSVG(m);
    return (
      '<div class="clockscrim" data-a="clockClose"></div><div class="clock sck glass' +
      (paused ? ' paused' : '') +
      (fin ? ' fin' : '') +
      (m.song ? ' song' : '') +
      '" role="dialog" aria-label="Session clock"><div class="sckin"><div class="sckhd">' +
      (fin
        ? '<span class="sckph"></span>'
        : '<button class="circ glass" data-a="pauseToggle" aria-label="' +
          (paused ? 'Resume' : 'Pause') +
          '">' +
          (paused ? ICON.play : ICON.pause) +
          '</button>') +
      '<span class="scktl">' +
      (m.song ? 'Song practice' : 'Session clock') +
      '</span><button class="circ glass" data-a="clockClose" aria-label="Close">' +
      ICON.x +
      '</button></div><div class="sckring"><div id="sckRing">' +
      (fin ? ringSVG(m, { all: true, fills: MOTION.on() ? fin.from : m.steps.map(() => 1), noTick: true }) : lastRing) +
      '</div><button class="sckc" id="sckC" data-a="sckSwap" aria-label="' +
      esc(centreLabel(m)) +
      '">' +
      centre(m) +
      '</button></div><p class="scksub" id="sckSub">' +
      esc(sub(m)) +
      '</p><div class="sckrows">' +
      rows(m) +
      '</div>' +
      mainBtn(m) +
      '</div></div>'
    );
  }
  // every second: the ring, the numbers and the step's time change in place (digits never animate)
  function tick() {
    const el = q('#layer .sck');
    if (!el || fin || !X || !X.start) return;
    const m = model(),
      r = ringSVG(m);
    if (r !== lastRing) {
      lastRing = r;
      $('sckRing').innerHTML = r;
    }
    const c = $('sckC'),
      h = centre(m);
    if (c && c.innerHTML !== h) c.innerHTML = h;
    if (c) c.setAttribute('aria-label', centreLabel(m));
    const s = $('sckSub');
    if (s) s.textContent = sub(m);
    const t = el.querySelector('.sckrow.cur .sckt');
    if (t) t.textContent = clk(m.steps[m.cur].secs);
  }

  /* ----- opening and closing: out of the timer pill and back into it ----- */
  const box = (el) => ({ l: el.offsetLeft, t: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight }); // untransformed
  function pillBox() {
    const p = $('timer');
    if (p && p.offsetParent !== null) {
      const r = p.getBoundingClientRect();
      return { l: r.left, t: r.top, w: r.width, h: r.height };
    }
    return pill || { l: window.innerWidth - 120, t: 50, w: 100, h: 36 };
  }
  // the transform that puts the clock over the pill
  function atPill(el, k) {
    const b = box(el),
      p = pillBox();
    k = k == null ? 1 : k;
    const dx = (p.l + p.w / 2 - (b.l + b.w / 2)) * k,
      dy = (p.t + p.h / 2 - (b.t + b.h / 2)) * k,
      sx = 1 + (p.w / b.w - 1) * k,
      sy = 1 + (p.h / b.h - 1) * k;
    return 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px) scale(' + sx.toFixed(4) + ',' + sy.toFixed(4) + ')';
  }
  function open() {
    if (!X || !X.start) return;
    const p = $('timer');
    if (p) {
      const r = p.getBoundingClientRect();
      pill = { l: r.left, t: r.top, w: r.width, h: r.height };
    }
    fix = null;
    fin = null;
    U.clock = true;
    rerender();
    const el = q('#layer .sck'),
      sc = q('#layer .clockscrim');
    if (!el) return;
    if (!MOTION.on()) {
      MOTION.animate(el, null, { fade: true });
      if (sc) MOTION.animate(sc, null, { fade: true });
      return;
    }
    MOTION.animate(el, [{ transform: atPill(el), borderRadius: '999px' }, { transform: 'none', borderRadius: '34px' }], { spring: 'nav' });
    // Q54 its fades are the kit's glass appearing (250 ms) and leaving (350 ms), part 50
    MOTION.animate(el.firstElementChild, [{ opacity: 0 }, { opacity: 1 }], { ms: MOTION.ms('appear'), delay: 70, fill: 'backwards' });
    if (sc) MOTION.animate(sc, [{ opacity: 0 }, { opacity: 1 }], { ms: MOTION.ms('appear') });
  }
  // a still copy of the clock (or its dimmed page) on <body>, for it to leave by: nothing on it can be tapped
  function ghost(x) {
    const c = x.cloneNode(true);
    c.removeAttribute('role');
    c.removeAttribute('data-a');
    c.querySelectorAll('[id],[data-a]').forEach((n) => {
      n.removeAttribute('id');
      n.removeAttribute('data-a');
    });
    c.classList.add('sckghost');
    c.setAttribute('aria-hidden', 'true');
    c.style.pointerEvents = 'none';
    document.body.appendChild(c);
    return c;
  }
  const gone = (els, ms) => {
    const t = setTimeout(() => els.forEach((e) => e && e.remove()), ms + 250);
    return () => {
      clearTimeout(t);
      els.forEach((e) => e && e.remove());
    };
  };
  // back into the pill (quicker than it came out). The clock is closed at once (the page underneath can be tapped
  // straight away); a still copy of it shrinks into the pill
  function close() {
    if (!U.clock) return;
    const el = q('#layer .sck'),
      sc = q('#layer .clockscrim'),
      anim = !!el && MOTION.speed() > 0 && (MOTION.on() || MOTION.reduced()),
      g = anim ? ghost(el) : null,
      gs = anim && sc ? ghost(sc) : null;
    U.clock = false;
    fix = null;
    fin = null;
    sw = null;
    rerender();
    if (!g) return;
    const S = MOTION.speed(),
      leave = MOTION.ms('leave'),
      rm = gone([g, gs], leave * S);
    if (gs) gs.animate([{ opacity: 1 }, { opacity: 0 }], { duration: (MOTION.on() ? leave : MOTION.reducedMs()) * S, fill: 'forwards' });
    let a;
    if (!MOTION.on())
      a = g.animate([{ opacity: getComputedStyle(g).opacity }, { opacity: 0 }], { duration: MOTION.reducedMs() * S, fill: 'forwards' });
    else {
      // from wherever a swipe left it
      const from = g.style.transform || 'none';
      MOTION.animate(g.firstElementChild, [{ opacity: getComputedStyle(g.firstElementChild).opacity }, { opacity: 0 }], { ms: MOTION.ms('quick'), fill: 'forwards' });
      a = MOTION.animate(
        g,
        [
          { transform: from, opacity: 1 },
          { transform: atPill(g), opacity: 0.3, borderRadius: '999px' },
        ],
        { ms: leave, fill: 'forwards' }
      );
    }
    if (a) a.onfinish = rm;
  }

  /* ----- swiping it away, sideways, from anywhere on it ----- */
  function follow(el, w, dx) {
    const p = Math.min(1, Math.abs(dx) / w);
    el.style.transform = MOTION.reduced()
      ? 'translateX(' + dx.toFixed(1) + 'px)'
      : 'translateX(' + dx.toFixed(1) + 'px) ' + atPill(el, 0.3 * p).replace(/scale\(([^,]+),([^)]+)\)/, 'scale($1,$1)');
    el.firstElementChild.style.opacity = (1 - 0.35 * p).toFixed(3);
  }
  function settle(el) {
    el.style.transform = '';
    el.firstElementChild.style.opacity = '';
  }
  document.addEventListener(
    'touchstart',
    (e) => {
      sw = null;
      if (!U.clock || e.touches.length !== 1) return;
      const el = e.target.closest && e.target.closest('#layer .sck');
      if (!el || e.target.closest('[data-own-gesture], input, textarea')) return;
      const t = e.touches[0];
      if (el.__stop) el.__stop(); // a spring back still going: caught where it is
      const m = /translateX\((-?[\d.]+)px\)/.exec(el.style.transform || ''),
        off = m ? +m[1] : 0;
      sw = { el, x: t.clientX - off, y: t.clientY, lx: t.clientX, lt: e.timeStamp, v: 0, lock: false, w: el.offsetWidth };
    },
    { passive: true }
  );
  document.addEventListener(
    'touchmove',
    (e) => {
      if (!sw) return;
      if (e.touches.length !== 1) {
        sw = null;
        return;
      }
      const t = e.touches[0],
        dx = t.clientX - sw.x,
        dy = t.clientY - sw.y;
      if (!sw.lock) {
        if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return;
        if (Math.abs(dx) <= Math.abs(dy) * 1.3) {
          sw = null; // scrolling the clock: not ours
          return;
        }
        sw.lock = true;
      }
      if (e.cancelable) e.preventDefault();
      const dt = e.timeStamp - sw.lt;
      if (dt > 0) sw.v = 0.6 * ((t.clientX - sw.lx) / dt) + 0.4 * sw.v;
      sw.lx = t.clientX;
      sw.lt = e.timeStamp;
      follow(sw.el, sw.w, dx);
    },
    { passive: false }
  );
  function release() {
    const s = sw;
    sw = null;
    if (!s || !s.lock) return;
    swipedAt = Date.now();
    const dx = s.lx - s.x,
      el = s.el;
    if (Math.abs(dx) / s.w > SWIPE_CLOSE || (Math.abs(s.v) > FLICK && Math.abs(dx) > 24 && Math.sign(s.v) === Math.sign(dx))) {
      return close();
    }
    // not far enough: back to where it was, at the finger's speed
    const stop = MOTION.spring({ x: dx }, { x: 0 }, { x: s.v * 1000 }, {
      spring: 'nav',
      frame: (p) => el.isConnected && follow(el, s.w, p.x),
      done: () => {
        el.__stop = null;
        if (el.isConnected) settle(el);
      },
    });
    el.__stop = () => {
      stop();
      el.__stop = null;
    };
  }
  document.addEventListener('touchend', release);
  document.addEventListener('touchcancel', () => {
    const s = sw;
    sw = null;
    if (s && s.lock) settle(s.el);
  });
  const swallow = (e) => e.isTrusted && Date.now() - swipedAt < 350;

  /* ----- the main button: the same as the pinned button (Log, Finish), or Resume ----- */
  function main() {
    if (!X || !X.start) return;
    if (X.paused) {
      togglePause();
      rerender();
      return;
    }
    const b = q('#dock [data-a=cta]');
    if (!b) return;
    const was = U.view,
      last = !isSong() && was === 'app',
      m = last ? model() : null;
    b.click(); // exactly what the pinned button does
    if (last) {
      const ss = U.view === 'saved' && U.saved && !U.sheet && D.sessions.find((s) => s.id === U.saved.k);
      if (ss) finished(ss, m);
      return;
    }
    // logged a step: the clock stays open on the next one
    if (X && X.start && !isSong() && U.view !== was && isFlow(U.view) && !U.sheet) {
      U.clock = true;
      renderSheet();
      fwUpdate();
    }
  }
  // Q22 item 4: finished from the clock, the ring closes and settles into Session saved's line, with Done
  function finished(ss, m) {
    fin = { k: ss.id, m, mins: Math.round(ss.mins), from: m.steps.map(fillOf) };
    m.steps.forEach((s) => (s.cur = s.done = false));
    U.clock = true;
    renderSheet();
    if (!MOTION.on()) return;
    const el = q('#layer .sck');
    if (!el) return;
    // the ring closes: every slice fills to its end (a CSS transition on the gentle spring)...
    requestAnimationFrame(() =>
      el.querySelectorAll('.sf').forEach((c) => {
        const len = +c.dataset.len;
        c.style.strokeDasharray = len.toFixed(2) + ' ' + (C - len).toFixed(2);
        c.dataset.f = '1.000';
      })
    );
    // ...and the centre and the saved line settle in under it, then Done
    [q('#sckC'), q('#sckSub'), el.querySelector('.sckrows'), el.querySelector('.sckmain')].forEach((x, i) =>
      MOTION.animate(x, [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }], {
        spring: 'gentle',
        delay: 350 + i * 90,
        fill: 'backwards',
      })
    );
  }
  function done() {
    const el = q('#layer .sck');
    if (el && MOTION.speed() > 0) {
      // the clock fades away as the saved screen becomes Today
      const t = (MOTION.on() ? MOTION.ms('leave') : MOTION.reducedMs()) * MOTION.speed(),
        g = ghost(el),
        a = g.animate([{ opacity: 1 }, { opacity: 0 }], { duration: t, fill: 'forwards' });
      a.onfinish = gone([g], t);
    }
    fin = null;
    U.clock = false;
    if (U.view === 'saved') SAVED.done();
    else rerender();
  }

  /* ----- Undo on Log (item 9) ----- */
  const stamps = () => (X ? { view: U.view, fEnd: X.fEnd, fE: X.fE, rEnd: X.rEnd, rE: X.rE } : null);
  function logged(was, what) {
    if (!was || !X) return;
    const u = { was, st: X.start, now: stamps() };
    undo = u;
    u.el = toastBtn(what, 'Undo', () => undoLog(u), UNDO_MS, () => {
      if (undo === u) undo = null;
    });
  }
  function undoLog(u) {
    if (undo !== u) return;
    undo = null;
    const n = stamps();
    // only if nothing has moved on since (another Log, a finish, a time fix)
    if (!X || X.start !== u.st || ['fEnd', 'fE', 'rEnd', 'rE'].some((k) => n[k] !== u.now[k])) return;
    ['fEnd', 'fE', 'rEnd', 'rE'].forEach((k) => (X[k] = u.was[k] == null ? null : u.was[k]));
    saveDraft();
    const back = u.was.view,
      open = U.clock;
    if (OP.onPage() && U.view !== back) {
      OP.stepTo(back);
      if (open) {
        U.clock = true;
        renderSheet();
      }
    } else rerender();
  }

  /* ----- fixing a finished step's time (item 10) ----- */
  function fixOpen(i) {
    if (!X || !X.start || isSong()) return;
    const m = model(),
      s = m.steps[i];
    if (!s || !s.done) return;
    if (fix && fix.i === i) fix = null;
    else {
      const v = Math.round(s.secs / 60);
      fix = { i, v: Math.max(1, v), was: s.secs, min: 1, max: Math.max(Math.round((2 * s.usual) / 60), v + 10, 10) };
    }
    renderSheet();
  }
  function fixPaint() {
    const f = fix,
      sl = $('sckSlider');
    if (!f || !sl) return;
    sl.style.setProperty('--p', ((f.v - f.min) / Math.max(1, f.max - f.min)).toFixed(4));
    sl.setAttribute('aria-valuenow', f.v);
    $('sckFixV').textContent = f.v + ' min';
    const t = q('#layer .sckt[data-k="' + f.i + '"]');
    if (t) t.textContent = clk(f.v * 60);
  }
  function fixTo(x) {
    const sl = $('sckSlider');
    if (!fix || !sl) return;
    const r = sl.getBoundingClientRect(),
      p = Math.max(0, Math.min(1, (x - r.left - 14) / Math.max(1, r.width - 28)));
    fix.v = Math.round(fix.min + p * (fix.max - fix.min));
    fixPaint();
  }
  // the step keeps its new length; the time it gained or lost moves the uncounted time, and the later stamps with it
  function fixSave() {
    const f = fix;
    if (!f || !X || !X.start) return;
    fix = null;
    const m = model(),
      s = m.steps[f.i];
    if (s && s.done && Math.round(s.secs / 60) !== f.v) {
      const d = s.secs - f.v * 60; // seconds taken out (negative: added)
      shift(d, f.i === 0 ? ['fE', 'rE'] : ['rE']);
      saveDraft();
    }
    renderSheet();
    fwUpdate();
  }
  // take d seconds out of the count (negative: add them), and out of each stamp in ks that's set
  function shift(d, ks) {
    X.pausedTotal = (X.pausedTotal || 0) + d * 1000;
    ks.forEach((k) => {
      if (X[k] != null) X[k] = Math.max(0, X[k] - d);
    });
  }
  document.addEventListener('pointerdown', (e) => {
    const s = e.target.closest && e.target.closest('#sckSlider');
    if (!s || !fix) return;
    e.preventDefault();
    slide = e.pointerId;
    try {
      s.setPointerCapture(e.pointerId);
    } catch (err) {}
    fixTo(e.clientX);
  });
  document.addEventListener('pointermove', (e) => {
    if (slide === e.pointerId) fixTo(e.clientX);
  });
  ['pointerup', 'pointercancel'].forEach((t) => document.addEventListener(t, (e) => slide === e.pointerId && (slide = null)));
  document.addEventListener('keydown', (e) => {
    if (!fix || !e.target || e.target.id !== 'sckSlider') return;
    const d = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1 }[e.key];
    if (!d) return;
    e.preventDefault();
    e.stopPropagation();
    fix.v = Math.max(fix.min, Math.min(fix.max, fix.v + d));
    fixPaint();
  });

  /* ----- pause and the screen staying on (item 7) ----- */
  function wake() {
    const want = !!(X && X.start && !X.paused && !document.hidden);
    if (!want && !(X && X.start)) chip = false;
    AWAKE.set('sess', want, (ok) => {
      if (ok && chip && X && X.start && !X.paused) toast('Screen stays on', 1600);
      chip = false;
    });
  }
  // a session (or song practice's first take) has started, or carries on after a pause
  function started(quiet) {
    chip = !quiet;
    seen(true);
    wake();
  }
  function paused() {
    if (X && X.start && !X.paused) chip = true; // resumed
    wake();
  }

  /* ----- away, and coming back (items 8 and 11) ----- */
  function seen(force) {
    if (!X || !X.start || document.hidden) return;
    X.seen = Date.now();
    if (force || X.seen - seenAt > SEEN_EVERY) {
      seenAt = X.seen;
      saveDraft();
    }
  }
  // the app is on screen again (or has just opened): ask about a long time away, if the clock was running
  function back(gap, at) {
    if (!X || !X.start) return;
    if (at == null) {
      at = Date.now();
      gap = X.seen ? at - X.seen : 0;
    }
    if (!X.paused && gap > AWAY_MIN * 60000) {
      away = { gap, at, st: X.start, shown: false };
      ask();
    }
    seen(true);
  }
  function ask() {
    if (!away || away.shown) return;
    if (!X || X.start !== away.st) return (away = null);
    if (U.sheet || rec || (typeof LAUNCH !== 'undefined' && LAUNCH.busy())) return; // asked once that's done
    away.shown = true;
    U.clock = false;
    U.sheet = 'away';
    U.sd = {};
    rerender();
  }
  function awaySheet() {
    if (!away || !X || X.start !== away.st) return '';
    const m = Math.max(1, Math.round(away.gap / 60000)),
      left = Math.max(0, elapsedSec() - (Date.now() - away.at + away.gap) / 1000),
      st = model(),
      s = st.steps[st.cur];
    return sheetWrap(
      'You were away ' + m + ' min',
      '<p class="note">Left during ' +
        esc(s.name) +
        ' at ' +
        clk(left) +
        '. The clock kept counting while you were away.</p><div style="margin-top:14px"><button class="cta" data-a="awayOut">Take it out</button></div><button class="ghost" data-a="awayKeep">Keep it, I was singing</button>',
      'You were away ' + m + ' minutes'
    );
  }
  function awayOut() {
    const a = away;
    away = null;
    if (a && X && X.start === a.st) {
      // the time comes out of the step that was running while away, never more than that step has had
      const ends = [
          ['fEnd', 'fE'],
          ['rEnd', 'rE'],
        ],
        before = ends.filter(([w]) => X[w] && X[w] < a.at).pop(),
        after = ends.find(([w, k]) => X[w] && X[w] >= a.at && X[k] != null),
        from = before ? X[before[1]] || 0 : 0,
        to = after ? X[after[1]] : elapsedSec(),
        d = Math.max(0, Math.min(a.gap / 1000, to - from));
      X.pausedTotal = (X.pausedTotal || 0) + d * 1000;
      // stamps made since coming back include the time away too, so they move with it
      ends.forEach(([w, k]) => {
        if (X[w] && X[w] >= a.at && X[k] != null) X[k] = Math.max(0, X[k] - d);
      });
      saveDraft();
    }
    closeSheet();
  }
  function awayKeep() {
    away = null;
    closeSheet();
  }
  // leaving the app: note when, in the saved draft only if it's still this session's (never writing over anything else)
  function left() {
    if (!X || !X.start) return;
    X.seen = Date.now();
    try {
      const o = JSON.parse(localStorage.getItem(DRAFT) || 'null');
      if (o && o.start === X.start) {
        o.seen = X.seen;
        localStorage.setItem(DRAFT, JSON.stringify(o));
      }
    } catch (e) {}
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) left();
    else back();
    wake();
  });
  window.addEventListener('pagehide', left);
  // launch: a session still running carries on, and says so
  function boot() {
    if (!X || !X.start) return;
    // the time away is measured now, before anything notes the app is on screen again
    const at = Date.now(),
      gap = X.seen ? at - X.seen : 0,
      st = X.start;
    X.seen = at;
    afterLaunch(() => {
      if (!X || X.start !== st) return;
      toast('Session picked up', 1800);
      back(gap, at);
      wake();
    });
  }
  // the end of every render(): ask about time away once nothing's in the way; keep the screen on or let it go
  function after() {
    if (away && !away.shown) setTimeout(ask);
    // a Log's Undo goes once the session it belongs to has finished (or another has started)
    if (undo && (!X || X.start !== undo.st)) {
      if (undo.el) undo.el.remove();
      undo = null;
    }
    if (fin && U.view !== 'saved') {
      fin = null;
      U.clock = false;
    }
    wake();
  }
  setInterval(() => seen(), 1000); // the draft notes the app is on screen (saved every SEEN_EVERY)

  Object.assign(SG_ACT, {
    sckSwap: () => {
      if (fin || !X || X.paused || isSong()) return;
      prefs.swap = !prefs.swap;
      try {
        localStorage.setItem(KEY, JSON.stringify(prefs));
      } catch (e) {}
      lastRing = '';
      tick();
    },
    sckFix: (el, v, k) => fixOpen(+k),
    sckFixSave: () => fixSave(),
    sckMain: () => main(),
    sckDone: () => done(),
    awayOut: () => awayOut(),
    awayKeep: () => awayKeep(),
  });

  return {
    html,
    can,
    open,
    close,
    tick,
    mini,
    model,
    usual,
    swallow,
    stamps,
    logged,
    started,
    paused,
    awaySheet,
    boot,
    after,
    back,
    // for the tests
    state: () => ({
      swap: !!prefs.swap,
      fix: fix ? Object.assign({}, fix) : null,
      fin: !!fin,
      away: away ? Object.assign({}, away) : null,
      undo: !!undo,
      closing: !!q('.sckghost'),
      swiping: !!(sw && sw.lock),
      wake: AWAKE.wants('sess'),
    }),
  };
})();
