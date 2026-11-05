/* Vocal Sessions · onepage.js
   Q19 the one-page session: Foundation, Rotation and Application follow each other on one page (drawn by scrFlow()
   in screens.js). This file has what happens on it:
   - tapping an exercise's row steps its level (Foundation 1 → 2 → 3 → Skip, Rotation 1 → 2 → 3 → off): the press
     shows first, then the ring fills. Level 3 sweeps the card blue then green and opens "How did it feel?"; levels 1
     and 2 open "What kept it at level N?" after a short settle. A picked word folds the row to one faded line and
     nudges the next exercise; tapping a folded row opens its box again
   - the pinned button (the dock): today's labels, a hint above, and "Just Foundation today? Finish here" on an empty
     Rotation. It records each step's end exactly as before (X.fEnd/X.fE, X.rEnd/X.rE), so Progress's split is unchanged
   - a finished step folds to a line; tapping it reopens it (U.fEdit) and Done folds it again. No jumping ahead: the
     next step only shows, faded and inert, underneath
   - pulling past the bottom springs back like pull to refresh, saying what's still needed
   - More exercises' sort menu (Longest ago, Most recent, A–Z)
   Everything that moves uses the shared springs (MOTION); with Reduce Motion it fades, with motion off it jumps.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */
const OP = (() => {
  const SETTLE = 700; // ms after the last tap before a level 1 or 2 box opens
  const RECEDE = 900; // ms after the last word picked before the row folds to one line
  const timers = {};
  // waits stretch with slow motion, like everything else (motion off keeps them as they are)
  const slow = () => (MOTION.on() ? MOTION.speed() : 1);
  const later = (key, fn, ms) => (timers[key] = timers[key] || []).push(setTimeout(fn, ms * slow()));
  const clear = (key) => {
    (timers[key] || []).forEach(clearTimeout);
    timers[key] = [];
  };
  const q = (sel) => document.querySelector(sel);
  const cssKey = (k) => (window.CSS && CSS.escape ? CSS.escape(k) : k);
  const itemOf = (key) => q('#app .osec:not(.preview) .rgi[data-rk="' + cssKey(key) + '"]');
  const parts = (key) => ({ s: key.slice(0, 1), id: key.slice(2) });
  const onPage = () => !!(X && !isSong() && isFlow(U.view) && U.view !== 'song');
  const gentleMs = () => MOTION.dur('gentle') / Math.max(1, MOTION.speed());

  /* ----- a row's ring, words and box, changed in place ----- */
  function paint(key) {
    const item = itemOf(key);
    if (!item) return;
    const { s, id } = parts(key),
      v = ringLv(s, id),
      e = exById(id) || { name: (X.rotNames || {})[id] || 'Exercise' },
      btn = item.querySelector('.rgrow'),
      arc = item.querySelector('.arc'),
      tx = item.querySelector('.ring text');
    arc.style.strokeDashoffset = (RING_C * (1 - (v > 0 ? v / 3 : 0))).toFixed(2);
    tx.textContent = v > 0 ? v : v === 0 ? (s === 'f' ? 'Skip' : '–') : s === 'f' ? '–' : '+';
    tx.setAttribute('class', v === 0 && s === 'f' ? 'sk' : v > 0 ? 'on' : '');
    btn.querySelector('small').textContent = ringSub(s, id);
    btn.classList.toggle('skipped', v === 0 && s === 'f');
    btn.setAttribute('aria-label', ringLabel(e, s));
  }
  function setBox(key, st) {
    U.rings = U.rings || {};
    U.rings[key] = st;
  }
  // fill the box for the level it settled on, then unfold it (or fade the words in if it's already open)
  function openBox(key) {
    const item = itemOf(key),
      { s, id } = parts(key);
    if (!item || !(ringLv(s, id) > 0)) return;
    const box = item.querySelector('.unfold'),
      cb = box.querySelector('.cuebox'),
      was = box.classList.contains('open');
    setBox(key, 'open');
    item.classList.remove('folded');
    cb.innerHTML = cueHTML(s, id);
    cb.classList.remove('waiting');
    box.classList.add('open');
    if (was) MOTION.animate(cb, [{ opacity: 0.3 }, { opacity: 1 }], { spring: 'gentle', fade: true });
    paint(key);
  }
  function shutBox(key) {
    const item = itemOf(key);
    if (!item) return;
    item.querySelector('.unfold').classList.remove('open');
    item.querySelector('.cuebox').classList.remove('waiting');
  }
  // a row you've picked words for steps back to one faded line, and the next exercise gets a nudge
  function fold(key) {
    const { s, id } = parts(key),
      item = itemOf(key);
    if (!item || !(ringLv(s, id) > 0) || !noteStr(X.xn[id])) return;
    setBox(key, 'fold');
    item.classList.add('folded');
    shutBox(key);
    paint(key);
    if (s === 'f') later('nudge', () => nudge(), 420);
  }
  // point at a row: the next Foundation exercise without a level, or the one named
  function nudge(key) {
    if (!onPage()) return;
    if (!key) {
      const next = FOUND.find((e) => !(e.id in X.f));
      if (!next) return;
      key = 'f:' + next.id;
    }
    const item = itemOf(key);
    if (!item) return;
    const row = item.querySelector('.rgrow'),
      r = row.getBoundingClientRect();
    if (r.top < 70 || r.bottom > window.innerHeight - 150)
      window.scrollTo({ top: window.scrollY + r.top - window.innerHeight * 0.35, behavior: MOTION.on() ? 'smooth' : 'auto' });
    item.classList.remove('rnudge');
    void item.offsetWidth;
    item.classList.add('rnudge');
  }

  /* ----- tapping a row ----- */
  const nextLv = (s, was) =>
    s === 'f'
      ? was === undefined || was === 0
        ? 1
        : was === 3
          ? 0
          : was + 1
      : was === undefined || !was
        ? 1
        : was === 3
          ? undefined
          : was + 1;
  function ring(btn) {
    if (!X) return;
    const id = btn.dataset.k,
      s = btn.dataset.s,
      key = s + ':' + id,
      item = btn.closest('.rgi');
    if (!item) return;
    // a folded row opens its box again first
    if (item.classList.contains('folded')) {
      clear(key);
      openBox(key);
      return;
    }
    clear(key);
    clear(key + '|r');
    const L = s === 'f' ? X.f : X.rot,
      v = nextLv(s, L[id]);
    if (v === undefined) delete L[id];
    else L[id] = v;
    saveDraft();
    setBox(key, 'shut');
    const box = item.querySelector('.unfold'),
      sw = item.querySelector('.rsweep');
    sw.getAnimations().forEach((a) => a.cancel());
    item.classList.remove('peak', 'folded');
    item.querySelector('.ring').classList.remove('peak');
    // the press shows first (the row's springy press), then the ring fills to its new third
    const fill = () => {
      paint(key);
      if (!(v > 0)) shutBox(key);
      else if (box.classList.contains('open')) box.querySelector('.cuebox').classList.add('waiting');
      dockUpd();
    };
    if (MOTION.on()) later(key, fill, 70);
    else fill();
    if (v === 3) peak(key, item);
    else if (v > 0) later(key, () => openBox(key), SETTLE);
  }
  // level 3: the card fills blue from the left, flashes green as the ring turns green, then the box unfolds inside it
  function peak(key, item) {
    const sw = item.querySelector('.rsweep'),
      ringEl = item.querySelector('.ring');
    const green = () => {
      item.classList.add('peak');
      ringEl.classList.add('peak');
    };
    if (!MOTION.on()) {
      green();
      if (MOTION.reduced() && MOTION.speed() > 0)
        sw.animate(
          [
            { opacity: 0, background: 'var(--rg-green)' },
            { opacity: 1, background: 'var(--rg-green)', offset: 0.3 },
            { opacity: 0, background: 'var(--rg-green)' },
          ],
          { duration: MOTION.CUE.flash * MOTION.speed(), easing: 'ease-out' } // Q52: a cue, one shared length
        );
      later(key, () => openBox(key), MOTION.speed() > 0 ? 300 : 0);
      return;
    }
    const G = gentleMs(),
      start = 230, // as the ring closes, not after it
      flashAt = start + G * 0.62;
    const B = 'var(--rg-blue)';
    later(
      key,
      () =>
        MOTION.animate(sw, [{ opacity: 1, transform: 'scaleX(0)', background: B }, { opacity: 1, transform: 'scaleX(1)', background: B }], {
          spring: 'gentle',
          fill: 'forwards',
        }),
      start
    );
    later(
      key,
      () => {
        sw.getAnimations().forEach((a) => a.cancel());
        MOTION.animate(
          sw,
          [
            { opacity: 1, background: B },
            { opacity: 1, background: 'var(--rg-green-s)', offset: 0.22 },
            { opacity: 1, background: 'var(--rg-green)', offset: 0.6 },
            { opacity: 0, background: 'var(--rg-green)' },
          ],
          { ms: 1350, easing: 'ease-out', fill: 'forwards' }
        );
        green();
        MOTION.animate(ringEl, [{ transform: 'scale(1)' }, { transform: 'scale(1.14)' }, { transform: 'scale(1)' }], {
          spring: 'ripple',
        });
      },
      flashAt
    );
    later(key, () => openBox(key), flashAt + 40); // inside the green, so the box is covered too
  }

  /* ----- the words ----- */
  function cue(b) {
    if (!X) return;
    const id = b.dataset.k,
      s = b.dataset.s,
      key = s + ':' + id,
      w = b.dataset.v,
      n = xnObj(id),
      i = n.w.indexOf(w);
    if (i < 0) n.w.push(w);
    else n.w.splice(i, 1);
    if (!n.w.length && !n.t) delete X.xn[id];
    saveDraft();
    b.classList.toggle('on', i < 0);
    b.setAttribute('aria-pressed', i < 0);
    if (i < 0) MOTION.animate(b, [{ transform: 'scale(1)' }, { transform: 'scale(1.08)' }, { transform: 'scale(1)' }], { spring: 'ripple' });
    clear(key + '|r');
    later(key + '|r', () => fold(key), RECEDE);
  }
  // + Your own: a field in its place; Enter or leaving it keeps the word (for next time too, as the notes sheet does)
  function own(b) {
    if (!X) return;
    const id = b.dataset.k,
      s = b.dataset.s,
      key = s + ':' + id;
    clear(key + '|r');
    const inp = document.createElement('input');
    inp.className = 'field ownin';
    inp.maxLength = 30;
    inp.placeholder = 'Your own words';
    inp.enterKeyHint = 'done';
    inp.autocomplete = 'off';
    inp.setAttribute('aria-label', 'Your own words');
    b.replaceWith(inp);
    inp.focus();
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      const w = inp.value.trim().replace(/\s+/g, ' ');
      if (w && X && ringLv(s, id) > 0) {
        const k = 'x_' + id;
        D.words[k] = D.words[k] || [];
        if (!D.words[k].includes(w)) D.words[k].push(w);
        save();
        const n = xnObj(id);
        if (!n.w.includes(w)) n.w.push(w);
        saveDraft();
      }
      const item = itemOf(key);
      if (!item || !inp.isConnected) return;
      item.querySelector('.cuebox').innerHTML = cueHTML(s, id);
      fwUpdate();
      if (!w) return;
      const nb = [...item.querySelectorAll('.cuebox .chip')].find((c) => c.dataset.v === w);
      if (nb) MOTION.animate(nb, [{ transform: 'scale(.6)', opacity: 0 }, { transform: 'none', opacity: 1 }], { spring: 'ripple', fade: true });
      later(key + '|r', () => fold(key), RECEDE);
    };
    inp.addEventListener('keydown', (e) => {
      if (KEYS.enter(e)) {
        e.preventDefault();
        inp.blur();
      } else if (e.key === 'Escape') {
        inp.value = '';
        inp.blur();
      }
    });
    inp.addEventListener('blur', finish, { once: true });
  }

  /* ----- the pinned button ----- */
  function state() {
    if (U.view === 'found') {
      const set = FOUND.filter((e) => e.id in X.f).length,
        all = FOUND.length;
      return {
        lab: 'Log foundation',
        wait: set < all,
        hint: set < all ? 'Level or Skip for each · ' + set + ' of ' + all + ' set' : 'Next: Rotation',
      };
    }
    if (U.view === 'rot') {
      const n = Object.keys(X.rot).length;
      return n
        ? { lab: 'Log ' + n + ' exercise' + (n > 1 ? 's' : ''), hint: 'Next: Application' }
        : { lab: 'Skip rotation', skip: true, hint: 'Pick some, or skip for today', fin: true };
    }
    // Q20: nothing sung yet, it can still finish
    return APPL.empty()
      ? { lab: 'Skip and finish', skip: true, hint: 'Pick a song, or finish without one' }
      : { lab: 'Finish session', hint: 'Last step' };
  }
  const FIN = '<button class="opfin" data-a="finHere">Just Foundation today? Finish here</button>';
  function dock() {
    const st = state();
    return (
      '<div class="ophint" id="opHint">' +
      esc(st.hint) +
      '</div><button class="cta glass ' +
      (st.wait ? 'opwait' : st.skip ? 'opskip' : 'tinted') +
      '" data-a="cta"><span id="opCta">' +
      esc(st.lab) +
      '</span></button>' +
      (st.fin ? FIN : '')
    );
  }
  // in place, so the label can ease to its new words
  function dockUpd() {
    if (!onPage() || U.sheet) return;
    const d = $('dock'),
      b = d.querySelector('[data-a=cta]'),
      t = $('opCta');
    if (!b || !t) return renderDock();
    const st = state();
    b.className = 'cta glass ' + (st.wait ? 'opwait' : st.skip ? 'opskip' : 'tinted');
    $('opHint').textContent = st.hint;
    if (t.textContent !== st.lab) {
      t.textContent = st.lab;
      MOTION.animate(t, [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], { spring: 'gentle', fade: true });
    }
    const f = d.querySelector('.opfin');
    if (st.fin && !f) b.insertAdjacentHTML('afterend', FIN);
    else if (!st.fin && f) f.remove();
  }
  // what's still needed, for the toast and the pull-past message
  function needText() {
    if (U.view === 'found') {
      const n = FOUND.filter((e) => !(e.id in X.f)).length;
      if (n) return n === 1 ? 'Set the last exercise first' : 'Set a level or Skip for each exercise';
    }
    if (U.view === 'rot' && !Object.keys(X.rot).length) return 'Pick some, or tap Skip rotation';
    if (U.view === 'app') return 'This is the last step';
    return 'Tap ' + state().lab + ' to carry on';
  }
  // scroll to what's missing in Foundation and flash it
  function showMissing() {
    if (!onPage() || U.view !== 'found') return;
    const els = FOUND.filter((e) => !(e.id in X.f))
      .map((e) => itemOf('f:' + e.id))
      .filter(Boolean);
    if (!els.length) return;
    const r = els[0].getBoundingClientRect();
    if (r.top < 70 || r.bottom > window.innerHeight - 150)
      window.scrollTo({ top: window.scrollY + r.top - 120, behavior: MOTION.on() ? 'smooth' : 'auto' });
    els.forEach((el) => {
      el.classList.remove('rneed');
      void el.offsetWidth;
      el.classList.add('rneed');
    });
  }
  function advance() {
    if (!onPage()) return;
    if (U.view === 'found') {
      if (FOUND.some((e) => !(e.id in X.f))) {
        toast(needText());
        MOTION.animate(
          q('#dock [data-a=cta]'),
          [{ transform: 'translateX(0)' }, { transform: 'translateX(-6px)' }, { transform: 'translateX(6px)' }, { transform: 'translateX(0)' }],
          { spring: 'ripple' }
        );
        showMissing();
        return;
      }
      // the end of Foundation, stamped exactly as the old confirm sheet's Log foundation did
      const was = SCLOCK.stamps();
      X.fEnd = Date.now();
      X.fE = elapsedSec();
      saveDraft();
      step('rot');
      SCLOCK.logged(was, 'Foundation logged'); // Q22: an Undo toast for about 5 s
    } else if (U.view === 'rot') {
      const ks = Object.keys(X.rot);
      if (ks.some((i) => !X.rot[i])) return toast('Set a level for each exercise you picked');
      // picked or not (Skip rotation), the end of Rotation is stamped as before
      const was = SCLOCK.stamps();
      X.rEnd = Date.now();
      X.rE = elapsedSec();
      saveDraft();
      step('app');
      SCLOCK.logged(was, ks.length ? 'Rotation logged' : 'Rotation skipped');
    } else if (U.view === 'app') {
      if (rec) return toast('Stop recording first');
      stopPlayback();
      startFinish();
    }
  }
  // Just Foundation today? Finish here: the session ends from an empty Rotation (session.js stamps Rotation's end)
  function finishHere() {
    if (!onPage() || U.view !== 'rot' || Object.keys(X.rot).length) return;
    U.finHere = true;
    stopPlayback();
    startFinish();
  }
  function step(to) {
    const was = U.view;
    U.fEdit = null;
    U.cvWin = null;
    U.clock = false;
    FW.shut = false;
    closeMenu();
    flip(() => (U.view = to), true);
    COACH.stepped(was); // the coach video cued to the new step's exercise, paused (Application pauses it)
  }

  /* ----- folding and reopening steps ----- */
  const stOf = (s) => ['reopened', 'folded', 'active', 'preview'].find((c) => s.classList.contains(c)) || '';
  // FLIP: change the state, redraw, then move every step from where it was
  function flip(change, toTop) {
    const before = {};
    document.querySelectorAll('#app .osec').forEach((s) => {
      before[s.dataset.sec] = { top: s.getBoundingClientRect().top, st: stOf(s) };
    });
    change();
    if (toTop) {
      window.scrollTo(0, 0);
      render();
    } else rerender();
    const secs = [...document.querySelectorAll('#app .osec')];
    if (!MOTION.on()) {
      if (MOTION.reduced() && MOTION.speed() > 0)
        secs.forEach((s) => {
          const b = before[s.dataset.sec];
          if (!b || b.st !== stOf(s))
            s.animate([{ opacity: 0 }, { opacity: getComputedStyle(s).opacity }], { duration: MOTION.reducedMs() * MOTION.speed(), easing: MOTION.EASE.out });
        });
      return;
    }
    secs.forEach((s) => {
      const b = before[s.dataset.sec],
        st = stOf(s),
        to = +getComputedStyle(s).opacity;
      if (!b) {
        // the new preview arrives from below
        MOTION.animate(s, [{ transform: 'translateY(60px)', opacity: 0 }, { transform: 'none', opacity: to }], {
          spring: 'gentle',
          delay: 90,
          fill: 'backwards',
        });
        return;
      }
      const dy = b.top - s.getBoundingClientRect().top;
      if (st === 'folded' && b.st !== 'folded') {
        // it collapses into its one-line summary
        MOTION.animate(
          s,
          [{ transform: 'translateY(' + (Math.min(dy, 0) * 0.15).toFixed(1) + 'px) scale(.96)', opacity: 0 }, { transform: 'none', opacity: to }],
          { spring: 'gentle' }
        );
        return;
      }
      if (Math.abs(dy) > 1 || b.st !== st)
        MOTION.animate(s, [{ transform: 'translateY(' + dy.toFixed(1) + 'px)', opacity: b.st === 'preview' ? 0.36 : to }, { transform: 'none', opacity: to }], {
          spring: 'nav',
        });
    });
  }
  function reopen(i) {
    if (!onPage() || !(i < flowCur()) || U.fEdit === i) return; // no jumping ahead
    if (rec) return toast('Stop recording first');
    closeMenu();
    flip(() => (U.fEdit = i));
  }
  function reclose() {
    if (U.fEdit == null) return;
    closeMenu();
    flip(() => (U.fEdit = null));
  }

  /* ----- More exercises' order (Q41: the parts kit's pull-down menu, KMENU in ui.js) ----- */
  let menu = null;
  function closeMenu() {
    if (menu) menu.shut();
    menu = null;
  }
  // list, now and act (Q20): Application's Other songs uses the same menu with its own orders
  function sortMenu(btn, list, now, act) {
    if (menu) return closeMenu();
    list = list || ROT_SORTS;
    now = now || U.rSort || 'old';
    act = act || 'rSortPick';
    const o = (menu = KMENU.open({
      id: 'opmenu',
      anchor: btn,
      kind: 'pull',
      name: 'Order',
      onClose: () => menu === o && (menu = null),
      html: list
        .map(
          (x) =>
            '<button role="menuitemradio" aria-checked="' +
            (now === x[0]) +
            '" data-a="' +
            act +
            '" data-v="' +
            x[0] +
            '">' +
            x[1] +
            (now === x[0] ? ICON.check : '') +
            '</button>'
        )
        .join(''),
    }));
  }
  // the rows slide to their new places
  function sortPick(v) {
    closeMenu();
    if (!ROT_SORTS.some((o) => o[0] === v) || v === (U.rSort || 'old')) return;
    const before = {};
    document.querySelectorAll('#app .sortlist .rgi').forEach((el) => (before[el.dataset.rk] = el.getBoundingClientRect().top));
    U.rSort = v;
    rerender();
    document.querySelectorAll('#app .sortlist .rgi').forEach((el) => {
      const b = before[el.dataset.rk];
      if (b === undefined) return;
      const dy = b - el.getBoundingClientRect().top;
      if (Math.abs(dy) > 1) MOTION.animate(el, [{ transform: 'translateY(' + dy.toFixed(1) + 'px)' }, { transform: 'none' }], { spring: 'nav' });
    });
    MOTION.animate(q('#app .sortname'), [{ opacity: 0, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }], {
      spring: 'gentle',
      fade: true,
    });
  }
  window.addEventListener('scroll', () => menu && closeMenu(), { passive: true });

  /* ----- pulling past the bottom: a rubber band, then it springs back ----- */
  const PULL = { y: null, x: 0, on: false, base: 0, last: 0, off: 0, w: 0, wt: 0 };
  let msg = null;
  const canPull = () =>
    onPage() && U.fEdit == null && !U.sheet && !U.clock && !rec && !Parts.open && !$('lyc').firstElementChild && !KEYS.typing();
  const atBottom = () => window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2;
  const rubber = (x) => {
    const d = window.innerHeight;
    return (1 - 1 / ((x * 0.55) / d + 1)) * d;
  };
  function msgEl() {
    if (msg) return msg;
    msg = document.createElement('div');
    msg.className = 'oppull glass';
    msg.id = 'opPull';
    msg.setAttribute('role', 'status');
    msg.innerHTML =
      '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg><span></span>';
    document.body.appendChild(msg);
    return msg;
  }
  function setPull(off) {
    PULL.off = off;
    $('app').style.transform = off ? 'translateY(' + (-off).toFixed(1) + 'px)' : '';
    const m = msgEl(),
      top = ($('dock').firstElementChild || $('dock')).getBoundingClientRect().top;
    m.querySelector('span').textContent = needText();
    m.style.bottom = Math.round(window.innerHeight - top + 12) + 'px';
    m.style.opacity = Math.min(1, off / 55);
    m.style.transform = 'translateX(-50%) translateY(' + Math.max(0, 14 - off / 4).toFixed(1) + 'px)';
    m.classList.add('on');
  }
  function hideMsg() {
    if (!msg) return;
    msg.style.opacity = 0;
    msg.classList.remove('on');
  }
  function release() {
    if (!PULL.on) return;
    const from = PULL.off,
      far = from > 48;
    PULL.on = false;
    PULL.off = 0;
    const a = $('app');
    a.style.transform = '';
    MOTION.animate(a, [{ transform: 'translateY(' + (-from).toFixed(1) + 'px)' }, { transform: 'none' }], { spring: 'ripple' });
    if (msg) {
      const o = +msg.style.opacity || 0;
      msg.style.transform = 'translateX(-50%)';
      hideMsg();
      if (MOTION.speed() > 0)
        msg.animate([{ opacity: o }, { opacity: far ? 1 : 0, offset: 0.5 }, { opacity: 0 }], {
          duration: (far ? 1400 : 300) * Math.max(1, MOTION.speed()),
          easing: 'ease-out',
        });
    }
    if (far) later('pull', showMissing, MOTION.on() ? MOTION.dur('ripple') / MOTION.speed() * 0.6 : 0);
  }
  document.addEventListener(
    'touchstart',
    (e) => {
      PULL.y = null;
      if (e.touches.length !== 1 || !canPull() || KEYS.typing(e) || (e.target.closest && e.target.closest('.fw'))) return;
      PULL.y = e.touches[0].clientY;
      PULL.x = e.touches[0].clientX;
      PULL.last = 0;
    },
    { passive: true }
  );
  document.addEventListener(
    'touchmove',
    (e) => {
      if (PULL.y === null || e.touches.length !== 1) return;
      if (!canPull()) return release();
      const t = e.touches[0],
        dy = PULL.y - t.clientY; // positive: the finger moving up, the page heading down
      if (!PULL.on) {
        if (Math.abs(t.clientX - PULL.x) > Math.abs(dy)) return;
        if (atBottom() && dy > PULL.last && dy > 0) {
          PULL.on = true;
          PULL.base = dy;
        }
      }
      PULL.last = dy;
      if (!PULL.on) return;
      if (e.cancelable) e.preventDefault();
      const x = dy - PULL.base;
      if (x < 0) {
        PULL.on = false;
        setPull(0);
        hideMsg();
        return;
      }
      setPull(rubber(x));
    },
    { passive: false }
  );
  const touchEnd = () => {
    PULL.y = null;
    release();
  };
  document.addEventListener('touchend', touchEnd);
  document.addEventListener('touchcancel', touchEnd);
  // a trackpad or mouse wheel does the same
  window.addEventListener(
    'wheel',
    (e) => {
      if (!canPull() || e.deltaY <= 0 || !(PULL.on || atBottom())) return;
      e.preventDefault();
      if (!PULL.on) {
        PULL.on = true;
        PULL.w = 0;
      }
      PULL.w += e.deltaY;
      setPull(rubber(PULL.w));
      clearTimeout(PULL.wt);
      PULL.wt = setTimeout(release, 140);
    },
    { passive: false }
  );

  // after every redraw (render() in ui.js)
  function after() {
    if (!onPage()) {
      closeMenu();
      if (PULL.on) {
        PULL.on = false;
        PULL.off = 0;
        $('app').style.transform = '';
      }
      hideMsg();
      return;
    }
    if (menu && !q('#app [data-a=rSort],#app [data-a=apSort]')) closeMenu();
    COACH.sessCue(); // the first time the coach window shows in a session, it's cued to the step's exercise
  }

  return {
    ring,
    cue,
    own,
    nudge,
    dock,
    dockUpd,
    advance,
    finishHere,
    reopen,
    reclose,
    sortMenu,
    sortPick,
    closeMenu,
    after,
    needText,
    label: () => state().lab, // Q22: the session clock's main button says the same, and looks the same
    look: () => {
      const st = state();
      return st.wait ? 'opwait' : st.skip ? 'opskip' : 'tinted';
    },
    onPage,
    stepTo: (to) => step(to), // Q22: Undo on Log goes back a step
    state: () => ({ pull: PULL.on, off: PULL.off, menu: !!menu }), // for the tests
  };
})();
