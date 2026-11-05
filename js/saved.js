/* Vocal Sessions · saved.js
   The Session saved screen (Q21, 3.41): finishing a focused session lands here (U.view 'saved', with U.tab 'today'),
   then Done turns it into Today. Song practice keeps its own finish (the summary sheet and the zoom into its card).
   - The screen: "Session saved"; the week arch, where only today's minutes draw in on top of the week so far; the line
     "N min · Day · weekly goal reached" (the last part only once the goal is reached); the week row, where the day
     just practised turns green; "N-week streak continues" (left out with no streak); Done, centred below.
   - Done: the arch, the week row and the streak line move onto their places on Today (FLIP, on the nav spring), Done
     moves to Start session's place and becomes it, "Today" fades up and the rest of Today rises in. Only on iPhone
     upright, with a streak line, and with every piece's place on Today on screen; otherwise (iPad, landscape, a page
     that would need scrolling, no streak, no goal) it's a plain fade.
   - No number counts up and nothing celebrates: the numbers are drawn at their final values.
   - Reduce Motion: fades both ways. Motion off (the tests): nothing animates.
   Like DET, everything animates elements already in their final place, so taps are never blocked.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */
const SAVED = (() => {
  const q = (s) => document.querySelector(s);
  // the prototype's timings (ms at normal speed): the arch's new minutes, then the week row, its dot, the streak, Done
  const T = { arc: 80, draw: 350, drawMs: 1100, line: 500, week: 1250 };

  // what the screen shows, from the session just saved and this week's data (null if that session has gone)
  function info() {
    const ss = U.saved && D.sessions.find((s) => s.id === U.saved.k);
    if (!ss) return null;
    const w = weekInfo(),
      goal = WEEK_TARGET > 0,
      day = startOfDay(ss.date).getTime(),
      inWeek = day >= w.ws.getTime(),
      before = Math.max(0, inWeek ? w.mins - ss.mins : w.mins),
      pa = goal ? Math.min(100, Math.round((w.mins / WEEK_TARGET) * 100)) : 0,
      pb = goal ? Math.min(pa, Math.round((before / WEEK_TARGET) * 100)) : 0;
    return {
      ss,
      w,
      goal,
      day: inWeek ? day : null,
      pa,
      pb,
      reached: goal && w.mins >= WEEK_TARGET,
      weekday: fmtDate(new Date(ss.date), { weekday: 'long' }),
    };
  }
  const ok = () => !!info();
  // "41 min · Sunday · weekly goal reached" (the last part only once the goal is reached). Q22: the session clock's
  // finish settles into this same line
  const lineOf = (n) => Math.round(n.ss.mins) + ' min · ' + n.weekday + (n.reached ? ' · weekly goal reached' : '');
  const line = () => {
    const n = info();
    return n ? lineOf(n) : '';
  };

  // the arch, drawn as Today draws it: the week so far a little lighter, today's minutes on top (the part that draws in)
  function arch(n) {
    const col = n.pa >= 100 ? 'var(--good)' : 'var(--accent)',
      path = (cls, len, off) =>
        '<path class="' +
        cls +
        '" d="' +
        ARC_D +
        '" pathLength="100" stroke-dasharray="' +
        len +
        ' 100"' +
        (off ? ' stroke-dashoffset="' + -off + '"' : '') +
        ' fill="none" stroke="' +
        col +
        '" stroke-width="16" stroke-linecap="round"/>';
    return (
      '<div class="arch svd-arch" data-sv="arc" role="img" aria-label="This week, ' +
      Math.round(n.w.mins) +
      ' of your ' +
      WEEK_TARGET +
      '-minute goal"><svg viewBox="0 0 300 165" aria-hidden="true"><path d="' +
      ARC_D +
      '" fill="none" stroke="var(--fill)" stroke-width="16" stroke-linecap="round"/>' +
      (n.pb > 0 ? path('svd-was', n.pb) : '') +
      (n.pa > n.pb ? path('svd-new', n.pa - n.pb, n.pb) : '') +
      '</svg><div class="c" aria-hidden="true"><small>This week</small><b>' +
      Math.round(n.w.mins) +
      '</b><small>of your ' +
      WEEK_TARGET +
      '-minute goal</small></div></div>'
    );
  }

  function page() {
    const n = info();
    if (!n) {
      // the session has gone (deleted from another screen): plain Today
      U.view = null;
      U.saved = null;
      return scrToday();
    }
    return (
      SET.wash() + // Today's soft gradient stays put while the screen becomes Today
      '<div class="svd">' +
      '<h1 class="svd-t" data-sv="title">Session saved</h1>' +
      (n.goal ? arch(n) : '') +
      '<p class="svd-line" data-sv="line">' +
      lineOf(n) +
      '</p>' +
      '<div class="week" data-sv="week" role="list" aria-label="This week">' +
      weekSpans(n.w, n.day) +
      '</div>' +
      (n.w.streak > 0 ? '<div class="streak" data-sv="streak">' + n.w.streak + '-week streak continues</div>' : '') +
      '<button class="cta ink svd-done" data-sv="btn" data-a="savedDone">Done</button>' +
      '</div>'
    );
  }

  // finishSession() has drawn the screen: its parts rise in, top to bottom, and today's minutes draw into the arch
  function enter() {
    const parts = [...document.querySelectorAll('#app [data-sv]')];
    if (!MOTION.on()) {
      if (MOTION.reduced() && MOTION.speed() > 0) parts.forEach((el) => MOTION.animate(el, null, { fade: true }));
      return;
    }
    const G = MOTION.dur('gentle') / MOTION.speed(),
      rise = (el, d) =>
        el &&
        MOTION.animate(
          el,
          [
            { opacity: 0, transform: 'translateY(14px)' },
            { opacity: 1, transform: 'none' },
          ],
          { spring: 'gentle', delay: d, fill: 'backwards' }
        );
    rise(q('#app [data-sv=title]'), 0);
    rise(q('#app [data-sv=arc]'), T.arc);
    const nw = q('#app .svd-new');
    if (nw) {
      const len = nw.getAttribute('stroke-dasharray');
      MOTION.animate(nw, [{ strokeDasharray: '0 100' }, { strokeDasharray: len }], {
        ms: T.drawMs,
        easing: MOTION.ease('gentle'),
        delay: T.draw,
        fill: 'backwards',
      });
    }
    rise(q('#app [data-sv=line]'), T.line);
    rise(q('#app [data-sv=week]'), T.week);
    // the day just practised turns from today's outline to green, with a small pop
    const dot = q('#app .week .svd-now');
    if (dot) {
      const cs = getComputedStyle(dot),
        fg = getComputedStyle(q('#app [data-sv=title]')).color,
        at = T.week + G * 0.7;
      MOTION.animate(
        dot,
        [
          { backgroundColor: 'rgba(0, 0, 0, 0)', borderColor: fg, color: fg },
          { backgroundColor: cs.backgroundColor, borderColor: cs.borderTopColor, color: cs.color },
        ],
        { spring: 'gentle', delay: at, fill: 'backwards' }
      );
      MOTION.animate(dot, [{ transform: 'scale(0.6)' }, { transform: 'none' }], { spring: 'ripple', delay: at, fill: 'backwards' });
    }
    rise(q('#app [data-sv=streak]'), T.week + G * 0.9);
    rise(q('#app [data-sv=btn]'), T.week + G * 1.1);
  }

  // where each moving part is on the saved screen, just before Done redraws Today
  function snap() {
    const r = {},
      n = info();
    document.querySelectorAll('#app [data-sv]').forEach((el) => (r[el.dataset.sv] = el.getBoundingClientRect()));
    const dot = q('#app .week .svd-now'),
      cs = dot && getComputedStyle(dot);
    return {
      r,
      n,
      dot: cs ? { bg: cs.backgroundColor, bd: cs.borderTopColor, fg: cs.color } : null,
      // the morph only where Today's pieces sit in one column, as on the saved screen (iPhone upright), and only when
      // every piece is there to move (a goal for the arch, a streak for the streak line)
      can: document.body.classList.contains('phone') && !!(n && n.goal && n.w.streak > 0 && r.arc && r.week && r.streak),
    };
  }
  const inView = (b) => b && b.height > 0 && b.top >= 0 && b.bottom <= window.innerHeight;

  // Done: the screen becomes Today
  function done() {
    const was = snap();
    go(() => {
      U.view = null;
      U.tab = 'today';
      U.saved = null;
    });
    if (!MOTION.on()) {
      if (MOTION.reduced() && MOTION.speed() > 0) fade();
      return;
    }
    if (!was.can || !morph(was)) fade();
  }
  // Reduce Motion, and anything the morph can't land exactly: Today simply fades in
  function fade() {
    [q('#app'), q('#dock .dockrow'), q('#barR')].forEach((el) => el && MOTION.animate(el, [{ opacity: 0 }, { opacity: 1 }], { spring: 'gentle', fade: true }));
  }
  function morph(was) {
    const el = {
      arc: q('#app .arch'),
      week: q('#app .week'),
      streak: q('#app .streak'),
      btn: q('#app [data-zk=start]'),
    };
    const now = {};
    for (const k of Object.keys(el)) {
      if (!el[k] || !inView(was.r[k])) return false;
      now[k] = el[k].getBoundingClientRect();
      if (!inView(now[k])) return false;
    }
    const flips = [];
    const flip = (k, scale) => {
      const b = was.r[k],
        a = now[k],
        s = scale ? b.width / a.width : 1;
      el[k].style.transformOrigin = '0 0';
      const an = MOTION.animate(
        el[k],
        [{ transform: 'translate(' + (b.left - a.left).toFixed(1) + 'px,' + (b.top - a.top).toFixed(1) + 'px) scale(' + s.toFixed(4) + ')' }, { transform: 'none' }],
        { spring: 'nav' }
      );
      const tidy = () => (el[k].style.transformOrigin = '');
      if (an) {
        an.finished.then(tidy, tidy);
        flips.push(an);
      }
      // the first frame must sit exactly where the piece was on the saved screen
      const f = el[k].getBoundingClientRect();
      return an && Math.abs(f.left - b.left) < 2 && Math.abs(f.top - b.top) < 2;
    };
    const fits = [flip('arc', true), flip('week', true), flip('streak')];
    if (!fits.every(Boolean)) {
      // something about this layout (a zoomed page, say) means it wouldn't line up: fade instead
      flips.forEach((an) => an.cancel());
      Object.values(el).forEach((x) => (x.style.transformOrigin = ''));
      return false;
    }
    // the arch: the week so far was drawn lighter; it darkens into Today's one solid arc as it moves
    const main = el.arc.querySelector('svg path[pathLength]');
    if (main && was.n.pb > 0) {
      const svg = main.ownerSVGElement,
        mk = (len, off, op) => {
          const p = main.cloneNode();
          p.setAttribute('stroke-dasharray', len + ' 100');
          if (off) p.setAttribute('stroke-dashoffset', -off);
          p.setAttribute('opacity', op);
          p.classList.add('svd-tmp');
          svg.appendChild(p);
          return p;
        };
      const lite = mk(was.n.pb, 0, 0.4),
        top = was.n.pa > was.n.pb ? mk(was.n.pa - was.n.pb, was.n.pb, 1) : null;
      main.style.visibility = 'hidden';
      const an = MOTION.animate(lite, [{ opacity: 0.4 }, { opacity: 1 }], { spring: 'nav', fill: 'forwards' }),
        put = () => {
          lite.remove();
          if (top) top.remove();
          main.style.visibility = '';
        };
      if (an) an.finished.then(put, put);
      else put();
    }
    // the day just practised hands its green over to Today's own colour for a practised day
    const dot = el.week.querySelector('span.today.done');
    if (dot && was.dot) {
      const cs = getComputedStyle(dot);
      MOTION.animate(
        dot,
        [
          { backgroundColor: was.dot.bg, borderColor: was.dot.bd, color: was.dot.fg },
          { backgroundColor: cs.backgroundColor, borderColor: cs.borderTopColor, color: cs.color },
        ],
        { spring: 'gentle', delay: 220, fill: 'backwards' }
      );
    }
    // Done moves to Start session's place (centre to centre) and becomes it: its words fade in as it lands
    const b = was.r.btn,
      a = now.btn;
    if (b) {
      MOTION.animate(
        el.btn,
        [{ transform: 'translate(' + (b.left + b.width / 2 - a.left - a.width / 2).toFixed(1) + 'px,' + (b.top - a.top).toFixed(1) + 'px)' }, { transform: 'none' }],
        { spring: 'nav' }
      );
      const c = getComputedStyle(el.btn).color;
      MOTION.animate(el.btn, [{ color: 'transparent' }, { color: 'transparent', offset: 0.35 }, { color: c }], { spring: 'nav' });
    }
    const rise = (x, d, dy) =>
      x &&
      MOTION.animate(
        x,
        [
          { opacity: 0, transform: 'translateY(' + (dy || 18) + 'px)' },
          { opacity: 1, transform: 'none' },
        ],
        { spring: 'gentle', delay: d, fill: 'backwards' }
      );
    // the title becomes "Today"; the date and everything else on Today rises in around the pieces that moved
    rise(q('#app .titlerow h1'), 80, 8);
    rise(q('#app .titlerow .dateline'), 60);
    const small = el.streak.querySelector('small');
    rise(small, 260, 8);
    const moved = Object.values(el);
    let i = 0;
    document.querySelectorAll('#app [data-rise]').forEach((x) => {
      if (x.closest('.titlerow') || moved.some((m) => m === x || x.contains(m) || m.contains(x))) return;
      rise(x, 260 + i++ * 70);
    });
    rise(q('#dock .dockrow'), 260);
    const gear = q('#barR');
    if (gear) MOTION.animate(gear, [{ opacity: 0 }, { opacity: 1 }], { spring: 'gentle', delay: 200, fill: 'backwards' });
    return true;
  }

  Object.assign(SG_ACT, { savedDone: () => done() });

  return { page, enter, ok, info, done, line };
})();
