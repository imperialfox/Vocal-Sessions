/* ===== Motion: the app's shared helpers on the parts kit's springs (3.11; the kit runs the motion since Q41, D18) =====
   Everything that moves uses these, so the whole app feels made by the same hand.
   - Springs come from the parts kit (Parts.motion, js/parts-kit.js): gentle (rows, capsules, sheets, fades), nav (card
     zoom, swiping back), ripple (peeks, small pops), press and release (the glass press, gestures.js PRESS) and the
     kit's own (snap, sheet, menu-open …). The kit publishes them on <html> as --ease-<name> / --dur-<name>, and only
     the kit writes those, .motion-off and .motion-reduced. An app spring that differs from the kit's is a line in
     js/parts.settings.js (springs: {…}) with its decision ID; there are none today.
   - Stagger: words 30 ms apart, rows 45 ms, chart bars 30 ms.
   - Reduce Motion (the iOS setting, or forced on or off in Settings › Accessibility): the kit's Parts.motion.setReduced.
     This device's choice is kept in localStorage 'vocalReduce' ('on' / 'off', absent = Match iPhone) and handed to
     the kit at start-up, because the kit doesn't save it.
   - Speed: 1 normally, 4 for slow motion while tuning, 0 for motion off (the tests use 0): Parts.motion.setSpeed,
     kept in localStorage 'vocalMotion', never in backups.
   - Distance blur: the dim-and-blur used around a focused part of a song (and later Song Clock's Blur ahead). */
const MOTION = (() => {
  const PM = Parts.motion;
  // the springs in use (the kit's, with any of the app's springs: {…} lines on top)
  const SPRINGS = PM.springs();
  // Q40 the named easings, the same three as app.css's --ease-pop, --ease-knob and --ease-out (test_values checks
  // they match): for code that needs a fixed-length move rather than a spring
  const EASE = { pop: 'cubic-bezier(.3,1.7,.45,1)', knob: 'cubic-bezier(.3,1.35,.5,1)', out: 'cubic-bezier(.2,.8,.2,1)' };
  const STAGGER = { word: 30, row: 45, bar: 30 };
  // Q52 (D20) cues: a flash that tells you something happened (the session's green flash when a step is done), not a
  // transition, so under Reduce Motion it keeps a visible length rather than the kit's 100 ms fade. Times the speed.
  const CUE = { flash: 650 };
  const BLUR_MAX = 1.5; // px. Ivan chose 1.5 over 2 so far lyrics stay recognisable
  const KEY = 'vocalMotion',
    RKEY = 'vocalReduce';
  const curve = PM.curve;
  const C = {};
  Object.keys(SPRINGS).forEach((k) => (C[k] = curve(SPRINGS[k].z, SPRINGS[k].f)));

  // this device's choices, handed to the kit at start-up (the kit doesn't save them)
  const read = (k) => {
    try {
      return localStorage.getItem(k);
    } catch (e) {
      return null;
    }
  };
  function load() {
    const s = read(KEY);
    PM.setSpeed(s !== null && !isNaN(+s) ? Math.max(0, Math.min(8, +s)) : 1);
    const f = read(RKEY);
    PM.setReduced(f === 'on' ? true : f === 'off' ? false : null);
  }
  load();

  const speed = () => PM.speed();
  const reduced = () => PM.reduced();
  const on = () => PM.on();
  const dur = (name) => (C[name] ? C[name].ms : C.gentle.ms) * speed();
  const ease = (name) => (C[name] || C.gentle).ease;
  // the delay for item i, for MOTION.animate's delay (which applies the speed itself, so this doesn't)
  const stagger = (i, kind) => i * (STAGGER[kind] || STAGGER.row);
  // Q52 (D20) the kit's Reduce Motion fade (--dur-reduced, 100 ms) in ms, before the speed: every fade that replaces
  // movement under Reduce Motion uses it
  const reducedMs = () => {
    const m = /^([\d.]+)(ms|s)$/.exec(getComputedStyle(document.documentElement).getPropertyValue('--dur-reduced').trim());
    return m ? +m[1] * (m[2] === 's' ? 1000 : 1) : 100;
  };

  // the kit writes the CSS variables and classes; this re-reads this device's choices and asks it to
  function publish() {
    load();
  }
  function setSpeed(n) {
    const v = Math.max(0, Math.min(8, +n || 0));
    try {
      if (v === 1) localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, String(v));
    } catch (e) {}
    PM.setSpeed(v);
  }

  // el.animate on a spring. With motion off or Reduce Motion it jumps to the end (or fades, if asked)
  function animate(el, frames, o) {
    o = o || {};
    if (!el || !el.animate) return null;
    if (!on()) {
      if (reduced() && o.fade && speed() > 0)
        return el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: reducedMs() * speed(), easing: 'ease-out' });
      return null;
    }
    const name = o.spring || 'gentle';
    return el.animate(frames, {
      duration: o.ms ? o.ms * speed() : dur(name),
      delay: (o.delay || 0) * speed(),
      easing: o.ms ? o.easing || EASE.out : ease(name),
      fill: o.fill || 'none',
    });
  }

  // a spring that starts moving: from and to are {x, y, …} in px, v is the finger's speed in px/s (3.12, the floating
  // window's corner snap). o: {spring, frame(p), done()}. Returns a function that stops it. With motion off it jumps.
  function spring(from, to, v, o) {
    o = o || {};
    let stop = false;
    if (!on()) {
      if (o.frame) o.frame(to);
      if (o.done) o.done();
      return () => {};
    }
    const s = SPRINGS[o.spring] || SPRINGS.gentle,
      w = 2 * Math.PI * s.f,
      wd = w * Math.sqrt(1 - s.z * s.z),
      T = Math.log(500) / (s.z * w);
    const ax = Object.keys(to).map((k) => {
      const A = from[k] - to[k];
      return { k, A, B: (((v && v[k]) || 0) + s.z * w * A) / wd };
    });
    const t0 = performance.now();
    const step = (now) => {
      if (stop) return;
      const t = (now - t0) / 1000 / speed(),
        e = Math.exp(-s.z * w * t),
        p = {};
      let left = 0;
      ax.forEach((a) => {
        p[a.k] = to[a.k] + e * (a.A * Math.cos(wd * t) + a.B * Math.sin(wd * t));
        left = Math.max(left, e * (Math.abs(a.A) + Math.abs(a.B)));
      });
      if (t >= T || left < 0.3) {
        if (o.frame) o.frame(to);
        if (o.done) o.done();
        return;
      }
      if (o.frame) o.frame(p);
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
    return () => (stop = true);
  }

  // distance blur: d is how many lines away from the focus (0 = in focus)
  const blur = (d) => (d <= 0 || reduced() ? 0 : +((BLUR_MAX * Math.min(d, 5)) / 5).toFixed(2));
  const dim = (d) => (d <= 0 ? 1 : +Math.max(0.3, 0.55 - 0.05 * d).toFixed(2));
  const dimLabel = (d) => (d <= 0 ? 1 : +Math.max(0.45, 0.7 - 0.05 * d).toFixed(2)); // labels only dim, never blur

  return {
    SPRINGS,
    EASE,
    STAGGER,
    CUE,
    BLUR_MAX,
    curve,
    on,
    reduced,
    dur,
    ease,
    stagger,
    reducedMs,
    animate,
    spring,
    setSpeed,
    speed,
    publish,
    blur,
    dim,
    dimLabel,
  };
})();
