/* ===== Motion: the app's shared springs (3.11) =====
   Everything that moves uses these, so the whole app feels made by the same hand.
   - Springs: gentle (rows, capsules, sheets, fades), nav (card zoom, swiping back), ripple (peeks, small pops).
     Each is a damping ratio and a frequency in Hz, turned into a CSS linear() easing and a duration.
     CSS reads them as --ease-gentle / --dur-gentle and so on; JS uses MOTION.animate().
   - Stagger: words 30 ms apart, rows 45 ms, chart bars 30 ms.
   - Reduce Motion (the iOS setting, or forced on or off in Settings › Accessibility): no movement or blur, just short
     fades or nothing. <html> gets .motion-reduced, which is what the stylesheet follows (3.21; it used a media query).
   - Speed: 1 normally, 4 for slow motion while tuning, 0 for motion off (the tests use 0).
     Set on this device with MOTION.setSpeed(n); kept in localStorage 'vocalMotion', never in backups.
   - Distance blur: the dim-and-blur used around a focused part of a song (and later Song Clock's Blur ahead). */
const MOTION = (() => {
  const SPRINGS = {
    gentle: { z: 0.82, f: 1.9 },
    nav: { z: 0.86, f: 2.2 },
    ripple: { z: 0.6, f: 2.4 },
  };
  const STAGGER = { word: 30, row: 45, bar: 30 };
  const BLUR_MAX = 1.5; // px. Ivan chose 1.5 over 2 so far lyrics stay recognisable
  const KEY = 'vocalMotion';
  const mq = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : null;
  const linearOK = !!(window.CSS && CSS.supports && CSS.supports('transition-timing-function', 'linear(0, 1)'));

  // a spring's position over time, sampled into a linear() easing; ms is when it has settled
  function curve(z, f) {
    const w = 2 * Math.PI * f,
      wd = w * Math.sqrt(1 - z * z),
      T = Math.log(500) / (z * w),
      n = 40,
      p = [];
    for (let i = 0; i <= n; i++) {
      const t = (T * i) / n;
      p.push(+(1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t))).toFixed(4));
    }
    p[n] = 1;
    return { ease: linearOK ? 'linear(' + p.join(', ') + ')' : 'cubic-bezier(.25,.9,.3,1)', ms: Math.round(T * 1000) };
  }
  const C = {};
  Object.keys(SPRINGS).forEach((k) => (C[k] = curve(SPRINGS[k].z, SPRINGS[k].f)));

  let speed = 1;
  try {
    const s = localStorage.getItem(KEY);
    if (s !== null && !isNaN(+s)) speed = Math.max(0, Math.min(8, +s));
  } catch (e) {}

  // Settings › Accessibility › Reduce motion (3.21): 'on' or 'off' in localStorage 'vocalReduce', otherwise the system's
  const forced = () => {
    try {
      return localStorage.getItem('vocalReduce');
    } catch (e) {
      return null;
    }
  };
  const reduced = () => {
    const f = forced();
    return f === 'on' ? true : f === 'off' ? false : !!(mq && mq.matches);
  };
  const on = () => speed > 0 && !reduced();
  const dur = (name) => (C[name] ? C[name].ms : C.gentle.ms) * speed;
  const ease = (name) => (C[name] || C.gentle).ease;
  // the delay for item i, for MOTION.animate's delay (which applies the speed itself, so this doesn't)
  const stagger = (i, kind) => i * (STAGGER[kind] || STAGGER.row);

  // CSS variables, so stylesheets use the same springs: transition: opacity var(--dur-gentle) var(--ease-gentle)
  function publish() {
    const r = document.documentElement.style;
    Object.keys(C).forEach((k) => {
      r.setProperty('--ease-' + k, C[k].ease);
      r.setProperty('--dur-' + k, (on() ? dur(k) : 0) + 'ms');
    });
    document.documentElement.classList.toggle('motion-off', !on());
    document.documentElement.classList.toggle('motion-reduced', reduced());
  }
  function setSpeed(n) {
    speed = Math.max(0, Math.min(8, +n || 0));
    try {
      if (speed === 1) localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, String(speed));
    } catch (e) {}
    publish();
  }

  // el.animate on a spring. With motion off or Reduce Motion it jumps to the end (or fades, if asked)
  function animate(el, frames, o) {
    o = o || {};
    if (!el || !el.animate) return null;
    if (!on()) {
      if (reduced() && o.fade && speed > 0)
        return el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 180, easing: 'ease-out' });
      return null;
    }
    const name = o.spring || 'gentle';
    return el.animate(frames, {
      duration: o.ms ? o.ms * speed : dur(name),
      delay: (o.delay || 0) * speed,
      easing: o.ms ? o.easing || 'cubic-bezier(.2,.8,.2,1)' : ease(name),
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
      const t = (now - t0) / 1000 / speed,
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

  if (mq) {
    if (mq.addEventListener) mq.addEventListener('change', publish);
    else if (mq.addListener) mq.addListener(publish);
  }
  publish();

  return {
    SPRINGS,
    STAGGER,
    BLUR_MAX,
    curve,
    on,
    reduced,
    dur,
    ease,
    stagger,
    animate,
    spring,
    setSpeed,
    speed: () => speed,
    publish,
    blur,
    dim,
    dimLabel,
  };
})();
