/* Vocal Sessions · details.js
   Motion details (3.14): the small movements that make changes feel looked after, all on the shared springs in motion.js.
   - Lists: DET.arm() before a change and DET.play() after the redraw (render() calls it) make a deleted row shrink away
     and the gap close, new rows slide in, rows slide to their new places (sort) and a pinned song travel up (pin).
     Rows and blocks opt in with data-fk (rows) and data-gk (the group they sit in, which closes or opens smoothly).
   - Progress: the bars ripple to their new heights, the headline total slides with the direction of time, the
     breakdown bars grow from the left, row by row. Scrubbing across bars stays instant (it never calls these).
   - Today: the arch fills and the week row ripples once the launch ripple has gone; today's circle pops after a session.
   - Recall: stepping the hint level masks (or unmasks) word by word, in reading order or back to front.
   - Calendar days ripple in; the session steps slide in the direction you're going; the song's bottom capsules swap.
   - Reduce Motion: none of this moves (MOTION.on() is false); fades are handled by motion.js and app.css. Motion off
     (the tests): every function here returns straight away, so the app behaves exactly as before 3.14.
   Never block taps for any of this: it only ever animates elements that are already in their final place. */
const DET = (() => {
  const EXIT_MS = 220; // a removed row leaves quicker than it arrived
  let armed = null; // what the page looked like before the change
  let popToday = false; // a session just finished: pop today's circle when Today shows without a sheet
  let todayPins = null; // the pinned songs Today last showed, so pins made elsewhere slide in on return
  const on = () => MOTION.on();

  /* ----- lists: rows leaving, arriving and moving ----- */
  const keyOf = (el) =>
    el.dataset.fk || (el.hasAttribute('data-rise') ? 'rise:' + el.className + ':' + el.textContent.trim().slice(0, 14) : '');
  const SEL = '#app [data-fk], #app [data-rise]';
  function snapshot() {
    const items = new Map(),
      groups = new Map();
    document.querySelectorAll(SEL).forEach((el) => {
      const r = el.getBoundingClientRect(),
        k = keyOf(el);
      if (!k || !r.height || items.has(k)) return;
      const g = el.closest('[data-gk]');
      items.set(k, { r, gk: g ? g.dataset.gk : '', node: el, cls: el.parentElement ? el.parentElement.className : '' });
    });
    document.querySelectorAll('#app [data-gk]').forEach((g) => groups.set(g.dataset.gk, g.getBoundingClientRect().height));
    return { items, groups };
  }
  // call just before the change that redraws (the stagger option ripples moved rows, as for a new sort order)
  function arm(o) {
    armed = on() ? Object.assign(snapshot(), { stagger: !!(o && o.stagger) }) : null;
  }
  function ghost(p, r) {
    const w = document.createElement('div');
    w.className = p.cls + ' det-ghost';
    w.setAttribute('aria-hidden', 'true');
    w.style.cssText =
      'position:fixed;margin:0;padding:0;z-index:30;pointer-events:none;left:' +
      r.left +
      'px;top:' +
      r.top +
      'px;width:' +
      r.width +
      'px;';
    w.appendChild(p.node.cloneNode(true));
    document.body.appendChild(w);
    return w;
  }
  function gone(w, ms) {
    setTimeout(() => w.remove(), (ms || EXIT_MS) * MOTION.speed() + 600);
  }
  function play() {
    const prev = armed;
    armed = null;
    if (!prev || !on()) return;
    const cur = new Map();
    document.querySelectorAll(SEL).forEach((el) => {
      const k = keyOf(el);
      if (k && !cur.has(k)) cur.set(k, el);
    });
    // groups: a shorter one eases down to its new height, a taller one eases up to it
    document.querySelectorAll('#app [data-gk]').forEach((g) => {
      const was = prev.groups.get(g.dataset.gk),
        h = g.getBoundingClientRect().height;
      if (was == null || Math.abs(was - h) < 2) return;
      if (was > h) MOTION.animate(g, [{ minHeight: was + 'px' }, { minHeight: '0px' }], { spring: 'gentle' });
      else MOTION.animate(g, [{ height: was + 'px' }, { height: h + 'px' }], { spring: 'gentle' });
    });
    let i = 0;
    cur.forEach((el, k) => {
      const p = prev.items.get(k),
        r = el.getBoundingClientRect();
      if (!p) {
        MOTION.animate(
          el,
          [
            { opacity: 0, transform: 'translateY(-8px) scale(0.97)' },
            { opacity: 1, transform: 'none' },
          ],
          { spring: 'gentle' }
        );
        return;
      }
      const dx = p.r.left - r.left,
        dy = p.r.top - r.top;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
      const g = el.closest('[data-gk]');
      if ((g ? g.dataset.gk : '') !== p.gk) {
        // into another group (a pin): a copy travels, so no group clips it on the way
        const w = ghost(p, r);
        el.style.visibility = 'hidden';
        w.style.zIndex = '31';
        const a = MOTION.animate(
          w,
          [{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }],
          { spring: 'gentle' }
        );
        const end = () => {
          el.style.visibility = '';
          w.remove();
        };
        if (a) a.onfinish = end;
        else end();
        gone(w, MOTION.dur('gentle') / MOTION.speed());
        setTimeout(() => (el.style.visibility = ''), MOTION.dur('gentle') + 400);
        return;
      }
      MOTION.animate(el, [{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }], {
        spring: 'gentle',
        delay: prev.stagger ? MOTION.stagger(Math.min(i++, 10), 'row') : 0,
      });
    });
    // rows that left: a copy stays where they were and shrinks away
    prev.items.forEach((p, k) => {
      if (cur.has(k) || !(p.node.className + '').length) return;
      const w = ghost(p, p.r);
      const a = MOTION.animate(
        w,
        [
          { opacity: 1, transform: 'none' },
          { opacity: 0, transform: 'scale(0.9)' },
        ],
        { ms: EXIT_MS, easing: 'cubic-bezier(.4,0,.6,1)', fill: 'forwards' }
      );
      if (a) a.onfinish = () => w.remove();
      else w.remove();
      gone(w);
    });
  }
  const armed_ = () => !!armed;

  /* ----- one-off helpers ----- */
  // elements rising in one after another
  function ripple(els, o) {
    if (!on()) return;
    o = o || {};
    [...els].slice(0, o.max || 24).forEach((el, i) =>
      MOTION.animate(
        el,
        [
          { opacity: 0, transform: 'translateY(' + (o.y == null ? 8 : o.y) + 'px)' },
          { opacity: 1, transform: 'none' },
        ],
        { spring: o.spring || 'gentle', delay: (o.delay || 0) + MOTION.stagger(i, o.kind || 'row'), fill: 'backwards' }
      )
    );
  }
  // sliding in from one side (a step of the session, the headline total)
  function slide(el, dir, px, spring) {
    if (!on() || !el) return;
    MOTION.animate(
      el,
      [
        { opacity: 0, transform: 'translateX(' + dir * (px || 28) + 'px)' },
        { opacity: 1, transform: 'none' },
      ],
      { spring: spring || 'nav', fill: 'backwards' }
    );
  }

  /* ----- Progress ----- */
  const BASE = 148; // the chart's baseline in its own units (H - B in chartSVG)
  const barTop = (g) => {
    let t = BASE;
    g.querySelectorAll('path, rect:not([data-pick])').forEach((s) => {
      const y = s.tagName === 'path' ? +/V([\d.]+)/.exec(s.getAttribute('d') || '')[1] : +s.getAttribute('y');
      if (!isNaN(y)) t = Math.min(t, y);
    });
    return t;
  };
  const barH = () => [...document.querySelectorAll('#pchart g.bar')].map((g) => BASE - barTop(g));
  // read the bars' heights before the chart is redrawn
  const bars = () => (on() ? barH() : null);
  // after the redraw: bars ripple from where they were (same count) or from the baseline (a new range), in the
  // direction of time: stepping back runs right to left, forward and a new range left to right
  function pcardIn(was, dir) {
    if (!on()) return;
    const gs = [...document.querySelectorAll('#pchart g.bar')],
      now = barH(),
      same = was && was.length === gs.length;
    gs.forEach((g, i) => {
      const rank = dir < 0 ? gs.length - 1 - i : i;
      const from = same ? (now[i] > 0 ? Math.min(2, was[i] / now[i]) : 1) : 0;
      if (same && Math.abs(was[i] - now[i]) < 0.5) return;
      g.querySelectorAll('path, rect:not([data-pick])').forEach((s) => {
        s.style.transformBox = 'view-box';
        s.style.transformOrigin = '0 ' + BASE + 'px';
        MOTION.animate(
          s,
          [{ transform: 'scaleY(' + from + ')' }, { transform: 'scaleY(1)' }],
          { spring: 'gentle', delay: MOTION.stagger(Math.min(rank, 30), 'bar'), fill: 'backwards' }
        );
      });
    });
    // the headline total slides the way time goes
    slide(document.querySelector('#pcard .bignum'), dir ? (dir < 0 ? -1 : 1) : 0.0001, 14, 'gentle');
    slide(document.querySelector('#pcard .prange .t'), dir ? (dir < 0 ? -1 : 1) : 0.0001, 10, 'gentle');
    // the breakdown bars grow from the left, row by row
    document.querySelectorAll('#pbrk .share i').forEach((b, i) => {
      b.style.transformOrigin = 'left center';
      MOTION.animate(b, [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], {
        spring: 'gentle',
        delay: MOTION.stagger(i, 'row'),
        fill: 'backwards',
      });
    });
  }

  /* ----- Today ----- */
  // the arch fills to this week's minutes and the week row ripples, after the launch ripple
  function todayIn() {
    if (!on() || U.view || U.tab !== 'today') return;
    const arc = document.querySelector('.arch svg path[pathLength]');
    if (arc) {
      const p = +/^([\d.]+)/.exec(arc.getAttribute('stroke-dasharray') || '0')[1];
      MOTION.animate(arc, [{ strokeDashoffset: p }, { strokeDashoffset: 0 }], { spring: 'gentle', fill: 'backwards' });
    }
    weekWave();
  }
  function weekWave() {
    const days = document.querySelectorAll('.week span');
    days.forEach((d, i) =>
      MOTION.animate(d, [{ transform: 'scale(0.6)', opacity: 0.4 }, { transform: 'none', opacity: 1 }], {
        spring: 'ripple',
        delay: MOTION.stagger(i, 'bar') * 1.5,
        fill: 'backwards',
      })
    );
  }
  // today's circle pops in once a finished session's sheet has gone
  function after() {
    if (U.view || U.tab !== 'today') return;
    if (popToday && !U.sheet && !(typeof LAUNCH !== 'undefined' && LAUNCH.busy())) {
      popToday = false;
      const t = document.querySelector('.week span.today');
      if (t && on())
        MOTION.animate(t, [{ transform: 'scale(0.6)' }, { transform: 'none' }], { spring: 'ripple', fill: 'backwards' });
    }
    // songs pinned somewhere else slide into Today's pinned list
    const now = [...document.querySelectorAll('[data-fk^="tp:"]')].map((el) => el.dataset.fk);
    if (todayPins && on() && !(typeof LAUNCH !== 'undefined' && LAUNCH.busy()))
      document.querySelectorAll('[data-fk^="tp:"]').forEach((el) => {
        if (!todayPins.includes(el.dataset.fk))
          MOTION.animate(
            el,
            [
              { opacity: 0, transform: 'translateX(-16px)' },
              { opacity: 1, transform: 'none' },
            ],
            { spring: 'gentle', fill: 'backwards' }
          );
      });
    todayPins = now;
  }
  const finished = () => (popToday = true);

  /* ----- calendar, session steps, All sessions ----- */
  // the days of a month ripple in, along the diagonal
  function calendarIn() {
    if (!on()) return;
    const ds = [...document.querySelectorAll('.cal button')];
    ds.forEach((d, i) =>
      MOTION.animate(d, [{ opacity: 0, transform: 'scale(0.7)' }, { opacity: 1, transform: 'none' }], {
        spring: 'ripple',
        delay: ((i % 7) + Math.floor(i / 7)) * 28,
        fill: 'backwards',
      })
    );
  }
  // moving between Foundation, Rotation and Application: the new step comes in from the side you're heading
  const STEP = { found: 0, rot: 1, app: 2 };
  const stepDir = (from, to) => (from in STEP && to in STEP ? Math.sign(STEP[to] - STEP[from]) : 0);
  function stepIn(dir) {
    if (!dir) return;
    slide(document.getElementById('app'), dir, 36, 'nav');
  }
  // All sessions: the new list's rows ripple in
  function listIn() {
    ripple(document.querySelectorAll('#app .grp > .sw, #app .grp > .row, #app .grp > .srow'), { y: 10, max: 14 });
  }

  /* ----- Recall: stepping the hint level ----- */
  // which words are hidden right now, keyed by line and place in the line
  function hxSnap() {
    if (!on()) return null;
    const m = new Map();
    document.querySelectorAll('#app .sgl').forEach((p) => {
      const k = p.dataset.o + '|' + p.dataset.li;
      [...p.querySelectorAll('.w')].forEach((w, i) => m.set(k + '|' + i, !!w.querySelector('.hx')));
    });
    return m;
  }
  // after the redraw: newly hidden words mask in reading order, newly shown ones reveal from the end backwards
  function hxWave(was) {
    if (!was || !on()) return;
    const mask = [],
      show = [];
    document.querySelectorAll('#app .sgl').forEach((p) => {
      const k = p.dataset.o + '|' + p.dataset.li;
      [...p.querySelectorAll('.w')].forEach((w, i) => {
        const before = was.get(k + '|' + i),
          now = !!w.querySelector('.hx');
        if (before === false && now) mask.push(w);
        else if (before === true && !now) show.push(w);
      });
    });
    const vis = (w) => {
      const r = w.getBoundingClientRect();
      return r.bottom > -40 && r.top < innerHeight + 40;
    };
    mask.filter(vis).forEach((w, i) => {
      w.querySelectorAll('.hx').forEach((x) => x.style.setProperty('--hxd', Math.min(i, 60) * MOTION.STAGGER.word * MOTION.speed() + 'ms'));
    });
    const sv = show.filter(vis);
    sv.forEach((w, i) =>
      MOTION.animate(w, [{ opacity: 0.2 }, { opacity: 1 }], {
        spring: 'gentle',
        delay: (sv.length - 1 - Math.min(i, 60)) * MOTION.STAGGER.word,
        fill: 'backwards',
      })
    );
  }
  // a peeked line gets a small ripple spring as it shows
  function peek(ln) {
    if (!on() || !ln) return;
    MOTION.animate(ln, [{ transform: 'scale(0.985)' }, { transform: 'none' }], { spring: 'ripple' });
  }

  /* ----- exercise history: the line draws left to right and ends on a dot ----- */
  function exLine() {
    if (!on()) return;
    const line = document.querySelector('.chart polyline'),
      dots = [...document.querySelectorAll('.chart circle')];
    if (line) {
      line.setAttribute('pathLength', '1');
      line.style.strokeDasharray = '1';
      MOTION.animate(line, [{ strokeDashoffset: 1 }, { strokeDashoffset: 0 }], {
        spring: 'gentle',
        ms: 620,
        easing: 'cubic-bezier(.3,.7,.3,1)',
        fill: 'backwards',
      });
    }
    dots.forEach((d, i) => {
      const last = i === dots.length - 1;
      d.style.transformBox = 'fill-box';
      d.style.transformOrigin = 'center';
      MOTION.animate(d, [{ opacity: 0, transform: 'scale(0.3)' }, { opacity: 1, transform: 'none' }], {
        spring: last ? 'ripple' : 'gentle',
        delay: dots.length > 1 ? (i / (dots.length - 1)) * 520 : 0,
        fill: 'backwards',
      });
    });
  }

  /* ----- sheets and bars that change in place ----- */
  // a sheet whose content changes (Preparing backup becomes Backup ready): the old height eases to the new one and
  // the content fades, so the sheet doesn't jump or rise again
  const IN_PLACE = /^(exporting|exportReady)\|/;
  const inPlace = (a, b) => IN_PLACE.test(a || '') && IN_PLACE.test(b || '') && a !== b;
  function sheetSwap(oldH) {
    if (!on() || !oldH) return;
    const sh = document.querySelector('#layer .sheet');
    if (!sh) return;
    const h = sh.getBoundingClientRect().height;
    if (Math.abs(h - oldH) > 2) MOTION.animate(sh, [{ height: oldH + 'px' }, { height: h + 'px' }], { spring: 'gentle' });
    [...sh.children]
      .filter((c) => !c.classList.contains('shead'))
      .forEach((c) => MOTION.animate(c, [{ opacity: 0 }, { opacity: 1 }], { ms: 220, easing: 'ease-out', fill: 'backwards' }));
  }
  // "Last backed up" changes colour softly when it updates
  function colourEase(oldColor, el) {
    if (!on() || !el || !oldColor) return;
    MOTION.animate(el, [{ color: oldColor }, { color: getComputedStyle(el).color }], { ms: 500, easing: 'ease-out' });
  }
  // the song's bottom capsules: when the mode changes (Practise, Recall, Perform, editing) the new ones come in with a
  // spring. Only a mode change: a hint step or a redraw never moves them (stillness while singing)
  let dockMode = null;
  function dockSwap(prevKids) {
    const shown = U.view === 'lyr' || (typeof songShown === 'function' && !!songShown());
    const mode = shown ? (U.sMode || 'practise') + '|' + (U.sEdit || '') : null;
    const was = dockMode;
    dockMode = mode;
    if (!on() || !mode || !was || was === mode || !prevKids || !prevKids.length) return;
    const d = document.getElementById('dock');
    if (!d) return;
    [...d.children].forEach((c) =>
      MOTION.animate(c, [{ opacity: 0, transform: 'translateY(14px) scale(0.96)' }, { opacity: 1, transform: 'none' }], {
        spring: 'gentle',
        fill: 'backwards',
      })
    );
  }
  const dockKids = () => (on() ? [...document.querySelectorAll('#dock > *')].map((c) => c.outerHTML) : null);
  // a new take slides in at the top of the takes sheet, and a starred one pops
  function takeIn() {
    if (!on()) return;
    const row = document.querySelector('#layer .newtake');
    if (row)
      MOTION.animate(row, [{ opacity: 0, transform: 'translateY(-14px)' }, { opacity: 1, transform: 'none' }], {
        spring: 'gentle',
        delay: MOTION.dur('gentle') * 0.5,
        fill: 'backwards',
      });
  }
  function starPop(el) {
    if (!on() || !el) return;
    MOTION.animate(el, [{ transform: 'scale(0.6)' }, { transform: 'none' }], { spring: 'ripple' });
  }

  return {
    arm,
    play,
    armed: armed_,
    ripple,
    slide,
    bars,
    pcardIn,
    todayIn,
    weekWave,
    after,
    finished,
    calendarIn,
    stepDir,
    stepIn,
    listIn,
    hxSnap,
    hxWave,
    peek,
    exLine,
    inPlace,
    sheetSwap,
    colourEase,
    dockKids,
    dockSwap,
    takeIn,
    starPop,
  };
})();
