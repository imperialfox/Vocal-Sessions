/* Vocal Sessions · zoom.js
   Card zoom (3.15, Render 4c): a card that opens a page zooms into it, and Back shrinks the page back into the card.
   - Wide cards (rows, the arch, the Start session capsule) grow into the page with its title starting where the card's
     title sits. Small cards (under half the screen wide) grow the whole page from a miniature, the card scaling up and
     fading into it. The growing window starts in the card's own colour and blends to the page background, so dark mode
     never shows an empty dark window. If the card has scrolled off screen, the page fades and shrinks a little instead.
   - Swipe back from anywhere on a page with a Back button: the page follows your finger and shrinks, and closes past
     about a fifth of the width (or on a flick), otherwise springs back. Whatever your finger lands on gets first claim:
     rows with their own swipe, sliders, charts you scrub, anything that scrolls sideways and anything marked
     data-own-gesture never start a swipe back.
   - Every zoom can be interrupted: Back (or a swipe) in the middle of one reverses it from wherever it is.
   - Built on transforms and opacity only (Safari animates those smoothly). The growing window is four nested boxes
     that each clip one corner, moved with translate, instead of an animated clip-path.
   - It never blocks a tap: the zoom is a still copy of the screens drawn over the real, already-updated app, with
     pointer-events off. The real app underneath is what your taps reach.
   - Reduce Motion: the zoom becomes a short cross-fade; a swipe back still follows your finger, sideways only.
     Motion off (the tests): nothing is drawn, but the bookkeeping still happens (Back returns to where the list was).
   How a card opts in: give it data-zk="<key>" (a key that's the same on the screen you come back to). go() in ui.js
   does the rest: ZOOM.before() just before a change of screen, ZOOM.after() just after it's drawn. */
const ZOOM = (() => {
  const SWIPE_CLOSE = 0.22, // of the width
    FLICK = 0.45, // px per ms, to the right
    // things with their own sideways gesture: a swipe back never starts on them
    OWN =
      '.sw, .srow, input, textarea, select, [contenteditable], .fw, #pchart, #lgchart, .chart, .seg, .dock, .crow, ' +
      '.lifted, .scrim, .clockscrim, [data-own-gesture]';
  let armed = null; // the card just tapped: {key, el}
  let backing = false; // this change of screen is a Back
  let stack = []; // [{key, from, to, y}]: cards opened into pages, so Back can shrink each page into its card
  const prev = new Map(); // place -> {box, from}: a still of the screen you came from, shown under a swipe back
  let Z = null; // the zoom (or swipe) on screen now
  let SB = null; // a swipe back in progress
  let swipedAt = 0;

  const vw = () => document.documentElement.clientWidth,
    vh = () => document.documentElement.clientHeight;
  const busy = () => typeof LAUNCH !== 'undefined' && LAUNCH.busy();
  const moving = () => MOTION.speed() > 0 && !busy(); // zooms draw (as fades with Reduce Motion)
  const reduced = () => MOTION.reduced();
  const navMs = () => MOTION.dur('nav') / Math.max(MOTION.speed(), 0.01); // the nav spring's length at normal speed
  const T2 = (x, y) => 'translate(' + x + 'px,' + y + 'px)';

  // where you are: the place a Back returns to (session steps count as one place for the stack)
  const pid = () => (U.view === 'ex' ? U.exId : U.view === 'lyr' ? U.songId : '') || '';
  const here = () => U.tab + '|' + (U.view || '') + '|' + pid();
  const STEPS = { found: 1, rot: 1, app: 1 };
  const stackHere = () => U.tab + '|' + (STEPS[U.view] ? 'steps' : U.view || '') + '|' + pid();
  const backBtn = () => document.querySelector('#barL [aria-label^="Back"]');

  /* ----- measuring ----- */
  const box = (r) => ({ l: r.left, t: r.top, r: r.right, b: r.bottom, w: r.width, h: r.height });
  const rect = (el) => box(el.getBoundingClientRect());
  const cardEl = (key) =>
    key ? document.querySelector('#app [data-zk="' + (window.CSS && CSS.escape ? CSS.escape(key) : key) + '"]') : null;
  // the first line of the card's label (a row's name, not its small print), so the page title starts there
  function labelRect(c) {
    const l = c.querySelector('.lbl, .rtxt b');
    if (!l) return null;
    const tn = [...l.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim());
    if (tn) {
      const rg = document.createRange();
      rg.selectNodeContents(tn);
      const b = rg.getBoundingClientRect();
      if (b.width) return box(b);
    }
    return rect(l);
  }
  // the colour the card shows: its own background, or the group it sits in
  function colourOf(el) {
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      const c = getComputedStyle(n).backgroundColor;
      if (c && c !== 'transparent' && !/^rgba\(.*,\s*0\)$/.test(c)) return c; // (not rgba with no alpha)
    }
    return getComputedStyle(document.body).backgroundColor;
  }
  // a card whose colour is far from the page's (the black or white Start session capsule) hands it over quickly, so
  // the growing window never fills the screen with it
  function strong(c) {
    const lum = (x) => {
      const m = /(\d+(?:\.\d+)?)\D+(\d+(?:\.\d+)?)\D+(\d+(?:\.\d+)?)/.exec(x || '');
      return m ? (0.2126 * m[1] + 0.7152 * m[2] + 0.0722 * m[3]) / 255 : 0;
    };
    return Math.abs(lum(c) - lum(getComputedStyle(document.body).backgroundColor)) > 0.35;
  }
  function radiusOf(el, R) {
    const r = parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0;
    return Math.min(r || 14, R.h / 2);
  }
  const mini = (R) => R.w < vw() / 2;

  /* ----- still copies ----- */
  // a copy that nothing can find or tap: no ids (except inside SVG defs, and the changelog chart's for its styles),
  // no actions, nothing the motion code looks for
  function scrub(n) {
    const strip = (e) => {
      if (e.id && e.id !== 'lgchart' && !(e.closest && e.closest('defs'))) e.removeAttribute('id');
      ['data-a', 'data-fk', 'data-gk', 'data-rise', 'data-zk', 'data-pick', 'autofocus', 'tabindex'].forEach((a) =>
        e.removeAttribute(a)
      );
    };
    strip(n);
    n.querySelectorAll('*').forEach(strip);
    n.setAttribute('aria-hidden', 'true');
    n.inert = true;
    return n;
  }
  // a still of the screen as it is now (top bar and page), placed exactly where it is. hide: the card being zoomed,
  // left empty in the copy
  function shot(hide) {
    const wrap = document.querySelector('.wrap');
    if (!wrap) return null;
    if (hide) hide.setAttribute('data-zsrc', '');
    const c = wrap.cloneNode(true);
    if (hide) hide.removeAttribute('data-zsrc');
    const hid = c.querySelector('[data-zsrc]');
    if (hid) {
      hid.removeAttribute('data-zsrc');
      hid.classList.add('zm-hid');
    }
    scrub(c);
    const T = wrap.offsetTop - window.scrollY;
    c.style.position = 'absolute';
    c.style.left = wrap.offsetLeft + 'px';
    c.style.top = T + 'px';
    c.style.width = wrap.offsetWidth + 'px';
    c.style.margin = '0';
    // the top bar sticks to the top of the screen: in the copy it's put where it is now
    const bar = wrap.querySelector('.bar'),
      cb = c.querySelector('.bar');
    if (bar && cb) {
      const top = parseFloat(getComputedStyle(bar).top) || 0;
      cb.style.position = 'relative';
      cb.style.top = Math.max(0, top - (T + bar.offsetTop)) + 'px';
    }
    const b = document.createElement('div');
    b.className = 'zm-shot';
    b.appendChild(c);
    const edge = document.querySelector('.edge');
    if (edge && document.body.classList.contains('scrolled')) b.appendChild(scrub(edge.cloneNode(true))).classList.add('zm-edge');
    return { box: b, place: here() };
  }
  // the page title, copied with its own look, so it can stay visible while the rest of the page fades
  function titleOf() {
    const h = document.querySelector('#app h1');
    if (!h) return null;
    const r = rect(h);
    if (!r.w) return null;
    const cs = getComputedStyle(h),
      c = scrub(h.cloneNode(true));
    c.className = 'zm-title';
    ['fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'color', 'fontFamily'].forEach((p) => (c.style[p] = cs[p]));
    c.style.left = r.l + 'px';
    c.style.top = r.t + 'px';
    c.style.width = r.w + 'px';
    return { el: c, r };
  }
  // a copy of a card, in the group it sits in so it keeps its look
  function ghostOf(card, R, rad, tint) {
    const w = document.createElement('div');
    w.className = (card.parentElement ? card.parentElement.className : '') + ' zm-ghost';
    w.style.cssText =
      'left:' + R.l + 'px;top:' + R.t + 'px;width:' + R.w + 'px;height:' + R.h + 'px;border-radius:' + rad + 'px;background:' + tint;
    const c = scrub(card.cloneNode(true));
    c.classList.remove('zm-src');
    c.style.visibility = '';
    w.appendChild(c);
    return w;
  }

  /* ----- the layer: a still copy drawn over the app while a zoom plays ----- */
  function div(cls, parent) {
    const d = document.createElement('div');
    d.className = cls;
    if (parent) parent.appendChild(d);
    return d;
  }
  // o: {under (a shot, or null for plain background), page (a shot), title, rad, tint, top}
  function build(o) {
    const z = { anims: [], cs: [], layer: div('zm' + (o.top ? ' top' : '')), rad: o.rad, tint: o.tint, y: window.scrollY };
    z.layer.setAttribute('aria-hidden', 'true');
    if ('under' in o) {
      z.under = div('zm-under', z.layer);
      if (o.under) z.under.appendChild(o.under.box);
    }
    z.win = div('zm-win', z.layer);
    // the window: four boxes, each clipping one rounded corner, nested so only where they all overlap shows
    let host = z.win;
    for (let i = 0; i < 4; i++) {
      const a = div('zm-c', host),
        b = div('zm-ci', a);
      a.style.borderRadius = o.rad + 'px';
      z.cs.push([a, b]);
      host = b;
    }
    div('zm-bg', host);
    z.tintEl = div('zm-tint', host);
    z.tintEl.style.background = o.tint || 'transparent';
    z.content = div('zm-content', host);
    z.body = div('zm-body', z.content);
    if (o.page) z.body.appendChild(o.page.box);
    if (o.title) {
      const h = z.body.querySelector('main h1');
      if (h) h.style.visibility = 'hidden';
      z.title = o.title.el;
      z.titleR = o.title.r;
      z.content.appendChild(z.title);
    }
    document.body.appendChild(z.layer);
    return z;
  }
  // move one property of one element to a value: straight away (t null), or animated from wherever it is now
  function to(z, el, prop, val, t) {
    if (!el) return null;
    const from = getComputedStyle(el)[prop];
    el.getAnimations().forEach((a) => a.zp === prop && a.cancel());
    el.style[prop] = val;
    if (!t || from === val) return null;
    const sp = MOTION.speed(),
      a = el.animate(
        [{ [prop]: from }, { [prop]: val }],
        t.ms != null
          ? { duration: t.ms * sp, delay: (t.delay || 0) * sp, easing: t.easing || 'cubic-bezier(.2,.8,.2,1)', fill: 'backwards' }
          : { duration: MOTION.dur(t.spring || 'nav'), delay: (t.delay || 0) * sp, easing: MOTION.ease(t.spring || 'nav'), fill: 'backwards' }
      );
    a.zp = prop;
    z.anims.push(a);
    return a;
  }
  // the window's rectangle {l,t,r,b}: each corner box moves, and its inside moves back, so only the box edges move
  function win(z, R, t) {
    const w = vw(),
      h = vh();
    [
      [R.l, R.t],
      [R.r - w, R.b - h],
      [R.r - w, R.t],
      [R.l, R.b - h],
    ].forEach(([x, y], i) => {
      to(z, z.cs[i][0], 'transform', T2(x, y), t);
      to(z, z.cs[i][1], 'transform', T2(-x, -y), t);
    });
  }
  const FULL = () => ({ l: 0, t: 0, r: vw(), b: vh(), w: vw(), h: vh() });
  // where the page sits when it's the size of the card: its title where the card's label is (wide cards), or the
  // whole page as a miniature inside the card (small ones)
  function anchor(R, tr, lb) {
    const w = vw();
    if (mini(R)) return T2(R.l, R.t) + ' scale(' + R.w / w + ')';
    const s = Math.min(1, R.w / w);
    if (tr) {
      const tx = lb ? lb.l : R.l + 16 * s,
        cy = lb ? lb.t + lb.h / 2 : R.t + R.h / 2;
      return T2(tx - s * tr.l, cy - (s * tr.h) / 2 - s * tr.t) + ' scale(' + s + ')';
    }
    return T2(R.l - 16 * s, R.t) + ' scale(' + s + ')';
  }
  // the card copy grown to cover the screen (small-card zoom)
  const big = (R) => T2(-R.l, -R.t) + ' scale(' + vw() / R.w + ')';
  // when every animation of this zoom has finished, unless something else took over first
  function whenDone(z, fn) {
    const list = z.anims.slice(),
      gen = (z.gen = (z.gen || 0) + 1);
    Promise.all(list.map((a) => a.finished.catch(() => null))).then(() => {
      if (Z === z && z.gen === gen && !z.ended) fn();
    });
    clearTimeout(z.safety);
    z.safety = setTimeout(() => {
      if (Z === z && z.gen === gen && !z.ended) fn();
    }, navMs() * MOTION.speed() * 3 + 1200);
  }
  // take the layer away and put the real cards back
  function end(z) {
    if (!z || z.ended) return;
    z.ended = true;
    clearTimeout(z.safety);
    if (z.stop) z.stop();
    z.anims.forEach((a) => a.cancel());
    z.layer.remove();
    document.querySelectorAll('.zm-src').forEach((e) => e.classList.remove('zm-src'));
    if (Z === z) Z = null;
    const f = z.then;
    z.then = null;
    if (f) f();
  }
  // the bottom capsules come in with a spring when the zoom changed them (the tab bar for a session's button)
  function riseDock(was) {
    const d = $('dock');
    if (!d || d.innerHTML === was) return;
    [...d.children].forEach((c) =>
      MOTION.animate(c, [{ opacity: 0, transform: 'translateY(14px) scale(0.96)' }, { opacity: 1, transform: 'none' }], {
        spring: 'gentle',
        fade: true,
        fill: 'backwards',
      })
    );
  }
  function remember(place, s, from) {
    if (!s) return;
    s.box.querySelectorAll('.zm-hid').forEach((e) => e.classList.remove('zm-hid'));
    prev.delete(place);
    prev.set(place, { box: s.box, from });
    while (prev.size > 4) prev.delete(prev.keys().next().value);
  }

  /* ----- open: the card grows into its page ----- */
  function open(ctx) {
    const a = ctx.armed,
      R = a.R,
      title = titleOf(),
      page = shot();
    if (!page || !ctx.shot) return false;
    const z = build({ under: ctx.shot, page, title, rad: a.rad, tint: a.tint });
    z.kind = 'open';
    Z = z;
    // however it ends (finished, caught by a swipe, reversed), keep the screen you came from for swiping back
    const pl = here();
    z.then = () => pl === here() && remember(pl, ctx.shot, ctx.place);
    const done = () => end(z);
    if (reduced()) {
      z.win.style.opacity = '0';
      requestAnimationFrame(() => {
        to(z, z.win, 'opacity', '1', { ms: 200, easing: 'ease-out' });
        whenDone(z, done);
      });
      return true;
    }
    const sm = mini(R),
      d = navMs();
    // the first frame: the window is the card, the page inside it is card-sized, the card's colour on top
    win(z, R);
    to(z, z.content, 'transform', anchor(R, title && title.r, a.lb));
    z.tintEl.style.opacity = '1';
    z.body.style.opacity = '0';
    if (z.title) z.title.style.opacity = '0';
    z.ghost = ghostOf(a.el, R, a.rad, a.tint);
    z.layer.appendChild(z.ghost);
    // a frame later (the copies are built and painted), it grows
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        if (Z !== z || z.ended || z.drag || z.closing) return;
        win(z, FULL(), { spring: 'nav' });
        to(z, z.content, 'transform', 'none', { spring: 'nav' });
        to(z, z.tintEl, 'opacity', '0', strong(a.tint) ? { ms: 180 } : { ms: 320, delay: 60 });
        if (sm) {
          to(z, z.body, 'opacity', '1', { ms: d * 0.3 });
          to(z, z.title, 'opacity', '1', { ms: d * 0.3 });
          to(z, z.ghost, 'transform', big(R), { spring: 'nav' });
          to(z, z.ghost, 'opacity', '0', { ms: d * 0.4 });
        } else if (strong(a.tint)) {
          // a black or white capsule: the page comes straight in as its colour goes
          to(z, z.title, 'opacity', '1', { ms: 120 });
          to(z, z.body, 'opacity', '1', { ms: 160 });
          to(z, z.ghost, 'opacity', '0', { ms: 120 });
        } else {
          // the card's label hands over to the page title as the window grows, then the rest of the page arrives
          to(z, z.title, 'opacity', '1', { ms: 150, delay: 30 });
          to(z, z.body, 'opacity', '1', { ms: 240, delay: 90 });
          to(z, z.ghost, 'opacity', '0', { ms: 150 });
        }
        whenDone(z, done);
      })
    );
    return true;
  }

  /* ----- close: the page shrinks back into its card ----- */
  // ctx.z: a zoom or a swipe already on screen, carried on from where it is; otherwise the still of the page you left
  function close(ctx, key, opts) {
    let z = ctx.z;
    const card = cardEl(key),
      R = card && rect(card),
      onScreen = R && R.w && R.b > 0 && R.t < vh();
    if (!z) {
      if (!ctx.shot) return false;
      z = build({ page: ctx.shot, title: ctx.title, rad: onScreen ? radiusOf(card, R) : 22, tint: onScreen ? colourOf(card) : null, top: opts && opts.top });
      win(z, FULL());
      z.tintEl.style.opacity = '0';
    } else if (z.under) {
      z.under.remove(); // the screen you're going back to is the real app now
      z.under = null;
    }
    z.closing = true;
    z.drag = false;
    Z = z;
    if (!onScreen || reduced()) return away(z);
    // into the card: hide the real one until the page lands on it
    const lb = labelRect(card),
      sm = mini(R),
      d = navMs(),
      tint = colourOf(card);
    card.classList.add('zm-src');
    z.tintEl.style.background = tint;
    if (z.ghost) z.ghost.remove();
    z.ghost = ghostOf(card, R, radiusOf(card, R), tint);
    z.ghost.style.opacity = '0';
    if (sm) z.ghost.style.transform = big(R);
    z.layer.appendChild(z.ghost);
    win(z, R, { spring: 'nav' });
    to(z, z.win, 'transform', 'none', { spring: 'nav' }); // after a swipe, the page's own shrink eases away too
    to(z, z.win, 'opacity', '1', { ms: 120 });
    to(z, z.content, 'transform', anchor(R, z.titleR, lb), { spring: 'nav' });
    // the card's colour takes over from the page as the window nears the card's size, so the window is never an
    // empty dark box, and a black or white capsule doesn't fill the screen with its colour on the way
    const st = strong(tint);
    to(z, z.tintEl, 'opacity', '1', st ? { ms: d * 0.2, delay: d * 0.35 } : { ms: d * 0.3, delay: d * 0.18 });
    if (sm) {
      to(z, z.ghost, 'transform', 'none', { spring: 'nav' });
      to(z, z.ghost, 'opacity', '1', { ms: d * 0.45, delay: d * 0.3 });
      to(z, z.body, 'opacity', '0', { ms: d * 0.3, delay: d * 0.4 });
      to(z, z.title, 'opacity', '0', { ms: d * 0.3, delay: d * 0.4 });
    } else {
      // the page goes first, the title hands back to the card's label as it lands
      to(z, z.body, 'opacity', '0', { ms: 150, delay: d * (st ? 0.38 : 0.24) });
      to(z, z.title, 'opacity', '0', { ms: 140, delay: d * 0.45 });
      to(z, z.ghost, 'opacity', '1', { ms: 150, delay: d * 0.5 });
    }
    whenDone(z, () => end(z));
    return true;
  }
  // no card to go back into (scrolled away, or none): the page fades and shrinks a little
  function away(z) {
    z.closing = true;
    z.drag = false;
    Z = z;
    if (z.under) {
      z.under.remove();
      z.under = null;
    }
    const cur = getComputedStyle(z.win).transform;
    to(z, z.win, 'opacity', '0', { ms: reduced() ? 180 : 240, easing: 'ease-out' });
    if (!reduced()) to(z, z.win, 'transform', (cur === 'none' ? '' : cur + ' ') + 'scale(0.94)', { ms: 240, easing: 'ease-out' });
    whenDone(z, () => end(z));
    return true;
  }

  /* ----- going from screen to screen (go() in ui.js) ----- */
  // just before the change: what's on screen now
  function before() {
    const ctx = { place: here(), sp: stackHere(), y: window.scrollY, back: backing, armed, dock: ($('dock') || {}).innerHTML };
    armed = null;
    backing = false;
    // a Back while a zoom or a swipe is on screen carries on from there; anything else clears it away
    if (Z && !(ctx.back && (Z.drag || Z.kind === 'open'))) end(Z);
    ctx.z = Z;
    if (!moving()) return ctx;
    const a = ctx.armed;
    if (a && a.el && a.el.isConnected) {
      a.R = rect(a.el);
      a.lb = labelRect(a.el);
      a.rad = radiusOf(a.el, a.R);
      a.tint = colourOf(a.el);
    }
    if (!ctx.z) {
      ctx.title = titleOf();
      ctx.shot = shot(a && a.R ? a.el : null);
    }
    return ctx;
  }
  // just after the new screen is drawn. Returns true when a zoom is playing
  function after(ctx) {
    armed = null;
    backing = false;
    const np = here(),
      nsp = stackHere();
    if (np === ctx.place) return false; // nothing changed screen (a toast, a refusal)
    let zoomed = false,
      kept = false;
    const top = stack[stack.length - 1];
    if (ctx.back && top && top.to === ctx.sp && top.from === nsp) {
      // Back to the card it came from: back to where that list was, and the page shrinks into the card
      stack.pop();
      window.scrollTo(0, top.y);
      lastY = window.scrollY; // a scroll put back, not one you made: the tab bar stays as it is
      if (moving()) zoomed = close(ctx, top.key);
    } else if (ctx.armed && ctx.armed.key) {
      stack.push({ key: ctx.armed.key, from: ctx.sp, to: nsp, y: ctx.y });
      if (stack.length > 8) stack.shift();
      if (moving() && ctx.armed.R && ctx.shot) zoomed = kept = open(ctx);
    } else {
      // anything else: keep only the cards still on the way back to here
      const i = stack.findIndex((e) => e.to === nsp);
      stack = i < 0 ? [] : stack.slice(0, i + 1);
      if (ctx.z) away(ctx.z); // a swipe back to a page with no card: it fades away
    }
    // the still of the screen you came from, for swiping back (only kept when the new page has a Back button)
    if (ctx.back) prev.delete(ctx.place);
    else if (!kept && ctx.shot && backBtn()) remember(np, ctx.shot, ctx.place);
    if (zoomed) riseDock(ctx.dock);
    return zoomed;
  }
  // a tap: remember the card (data-zk) and whether it's a Back button, for the change of screen it causes
  function tap(el) {
    const c = el && el.closest && el.closest('[data-zk]');
    armed = c ? { key: c.dataset.zk, el: c } : null;
    backing = !!(el && el.closest && el.closest('#barL') && /^Back/.test(el.getAttribute('aria-label') || ''));
    setTimeout(() => {
      armed = null;
      backing = false;
    }, 0);
  }
  // for code that opens a page itself (the new song's row): this card is the one to zoom from
  function arm(el) {
    if (el && el.dataset && el.dataset.zk) armed = { key: el.dataset.zk, el };
  }

  /* ----- Finish: the session shrinks back into Start session (song practice into its row) ----- */
  function finishing() {
    armed = null;
    backing = false;
    if (Z) end(Z);
    const ctx = { place: here() };
    if (moving()) {
      ctx.title = titleOf();
      ctx.shot = shot();
    }
    return ctx;
  }
  function finished(ctx, key) {
    stack = [];
    prev.clear();
    if (moving() && ctx.shot) close(ctx, key);
  }

  /* ----- the new song's paste sheet shrinks into its row ----- */
  function sheetShot() {
    if (!moving()) return null;
    const s = document.querySelector('#layer .sheet');
    if (!s) return null;
    const R = rect(s),
      c = scrub(s.cloneNode(true));
    c.style.cssText += ';position:absolute;margin:0;animation:none;transform:none;max-height:none;overflow:hidden;left:' +
      R.l + 'px;top:' + R.t + 'px;width:' + R.w + 'px;height:' + R.h + 'px';
    c.scrollTop = s.scrollTop;
    const b = document.createElement('div');
    b.className = 'zm-shot';
    b.appendChild(c);
    return { box: b, R };
  }
  function sheetInto(sh, key, then) {
    let card = cardEl(key);
    if (!sh || !card || !moving()) return then && then();
    if (Z) end(Z);
    // the new row may be further down the list: bring it into view first
    let R = rect(card);
    if (R.t < 90 || R.b > vh() - 120) {
      window.scrollTo(0, Math.max(0, window.scrollY + R.t - vh() / 2 + R.h / 2));
      R = rect(card);
    }
    const tint = colourOf(card),
      rad = radiusOf(card, R),
      z = build({ page: sh, rad: 34, tint, top: true });
    z.kind = 'sheet';
    z.then = then;
    Z = z;
    win(z, sh.R);
    z.tintEl.style.opacity = '0';
    card.classList.add('zm-src');
    z.ghost = ghostOf(card, R, rad, tint);
    z.ghost.style.opacity = '0';
    z.layer.appendChild(z.ghost);
    if (reduced()) {
      to(z, z.win, 'opacity', '0', { ms: 180, easing: 'ease-out' });
      whenDone(z, () => end(z));
      return;
    }
    const s = R.w / sh.R.w,
      d = navMs();
    win(z, R, { spring: 'nav' });
    z.cs.forEach(([a]) => to(z, a, 'borderRadius', rad + 'px', { spring: 'nav' }));
    to(z, z.content, 'transform', T2(R.l - s * sh.R.l, R.t - s * sh.R.t) + ' scale(' + s + ')', { spring: 'nav' });
    to(z, z.body, 'opacity', '0', { ms: 150 });
    to(z, z.tintEl, 'opacity', '1', { ms: 200 });
    to(z, z.ghost, 'opacity', '1', { ms: 150, delay: d * 0.5 });
    whenDone(z, () => end(z));
  }

  /* ----- a calendar day: its sessions grow out of the day (small-card zoom, inside the calendar sheet) ----- */
  function dayIn(r) {
    const R = r && r.left != null ? box(r) : r;
    if (!moving() || !R || !R.w) return;
    const blk = document.querySelector('#layer [data-zday]'),
      day = document.querySelector('#layer .cal button.sel');
    if (!blk) return;
    if (reduced()) {
      MOTION.animate(blk, [{ opacity: 0 }, { opacity: 1 }], { fade: true });
      return;
    }
    const B = rect(blk),
      m = R.w / B.w,
      d = navMs();
    blk.style.transformOrigin = '0 0';
    MOTION.animate(blk, [{ transform: T2(R.l - B.l, R.t - B.t) + ' scale(' + m + ')' }, { transform: 'none' }], { spring: 'nav' });
    MOTION.animate(blk, [{ opacity: 0 }, { opacity: 1 }], { ms: d * 0.3, easing: 'ease-out' });
    const sh = day && day.closest('.sheet');
    if (!sh) return;
    // the day's tile grows towards the list and fades into it
    const S = sh.getBoundingClientRect(),
      g = scrub(day.cloneNode(true));
    g.classList.add('zm-day');
    g.style.cssText +=
      ';left:' + (R.l - S.left + sh.scrollLeft) + 'px;top:' + (R.t - S.top + sh.scrollTop) + 'px;width:' + R.w + 'px;height:' + R.h + 'px';
    sh.appendChild(g);
    const k = B.w / R.w;
    MOTION.animate(g, [{ transform: 'none' }, { transform: T2(B.l - R.l, B.t - R.t) + ' scale(' + k + ')' }], { spring: 'nav' });
    const a = MOTION.animate(g, [{ opacity: 1 }, { opacity: 0 }], { ms: d * 0.22, easing: 'ease-out', fill: 'forwards' });
    if (a) a.onfinish = () => g.remove();
    setTimeout(() => g.remove(), d * MOTION.speed() + 600);
  }

  /* ----- swipe back from anywhere ----- */
  function canSwipe(t) {
    if (!backBtn() || U.sheet || U.clock || rec || overlayOpen() || (Z && Z.kind === 'sheet')) return false;
    for (let n = t; n && n !== document.body && n.nodeType === 1; n = n.parentElement) {
      if (n.matches(OWN)) return false;
      if (n.scrollWidth > n.clientWidth + 1) {
        const ox = getComputedStyle(n).overflowX;
        if (ox === 'auto' || ox === 'scroll') return false;
      }
    }
    return true;
  }
  // the finger has gone sideways: lift the page (a zoom still opening is caught where it is)
  function grab() {
    if (!moving()) return;
    let z = Z;
    if (z && z.kind === 'open' && !z.closing) {
      z.anims.forEach((a) => {
        try {
          a.commitStyles();
        } catch (e) {}
        a.cancel();
      });
      z.anims = [];
      z.gen = (z.gen || 0) + 1;
    } else {
      if (z) end(z);
      const p = prev.get(here());
      z = build({
        under: p ? { box: p.box.cloneNode(true) } : null,
        page: shot(),
        title: titleOf(),
        rad: 22,
        tint: null,
      });
      win(z, FULL());
      z.tintEl.style.opacity = '0';
    }
    z.kind = 'swipe';
    z.drag = true;
    z.layer.classList.add('lift');
    z.d = { x: 0, y: 0, s: 1 };
    Z = z;
  }
  function follow(dx, dy) {
    const z = Z;
    if (!z || !z.drag) return;
    const p = Math.max(0, Math.min(1, dx / vw()));
    z.d = reduced() ? { x: Math.max(0, dx), y: 0, s: 1 } : { x: Math.max(0, dx) * 0.55, y: dy * 0.2, s: 1 - 0.28 * p };
    z.win.style.transform = T2(z.d.x, z.d.y) + ' scale(' + z.d.s + ')';
  }
  // not far enough: the page springs back to fill the screen, carrying on at the finger's speed
  function springBack(z, v) {
    if (!z || z.ended) return;
    z.drag = false;
    const d = z.d || { x: 0, y: 0, s: 1 };
    // a zoom caught while it opened finishes opening
    win(z, FULL(), { spring: 'nav' });
    to(z, z.content, 'transform', 'none', { spring: 'nav' });
    to(z, z.tintEl, 'opacity', '0', { ms: 200 });
    to(z, z.body, 'opacity', '1', { ms: 150 });
    if (z.title) to(z, z.title, 'opacity', '1', { ms: 150 });
    if (z.ghost) to(z, z.ghost, 'opacity', '0', { ms: 120 });
    let left = 2;
    const fin = () => {
      if (--left === 0 && Z === z && !z.closing) end(z);
    };
    z.stop = MOTION.spring(d, { x: 0, y: 0, s: 1 }, { x: (v || 0) * 1000 * (reduced() ? 1 : 0.55) }, {
      spring: 'nav',
      frame: (p) => (z.win.style.transform = T2(p.x, p.y) + ' scale(' + p.s + ')'),
      done: fin,
    });
    z.gen = (z.gen || 0) + 1;
    const gen = z.gen;
    Promise.all(z.anims.map((a) => a.finished.catch(() => null))).then(() => z.gen === gen && fin());
  }
  document.addEventListener(
    'touchstart',
    (e) => {
      SB = null;
      if (e.touches.length !== 1 || !canSwipe(e.target)) return;
      const t = e.touches[0];
      SB = { x: t.clientX, y: t.clientY, lx: t.clientX, lt: e.timeStamp, v: 0, lock: null };
    },
    { passive: true }
  );
  document.addEventListener(
    'touchmove',
    (e) => {
      if (!SB) return;
      if (e.touches.length !== 1) {
        cancelSwipe();
        return;
      }
      const t = e.touches[0],
        dx = t.clientX - SB.x,
        dy = t.clientY - SB.y;
      if (!SB.lock) {
        if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return;
        if (!(dx > 0 && Math.abs(dx) > Math.abs(dy) * 1.3)) {
          SB = null; // a scroll, or a swipe the other way: not ours
          return;
        }
        SB.lock = true;
        closeSwipes();
        grab();
      }
      if (e.cancelable) e.preventDefault();
      const dt = e.timeStamp - SB.lt;
      if (dt > 0) SB.v = 0.6 * ((t.clientX - SB.lx) / dt) + 0.4 * SB.v;
      SB.lx = t.clientX;
      SB.lt = e.timeStamp;
      follow(dx, dy);
    },
    { passive: false }
  );
  function release() {
    const s = SB;
    SB = null;
    if (!s || !s.lock) return;
    swipedAt = Date.now();
    const dx = s.lx - s.x;
    if (dx / vw() > SWIPE_CLOSE || (s.v > FLICK && dx > 24)) {
      const b = backBtn();
      if (b) b.click();
      if (Z && Z.drag) springBack(Z, 0); // Back didn't go anywhere
    } else if (Z && Z.drag) springBack(Z, s.v);
  }
  function cancelSwipe() {
    const s = SB;
    SB = null;
    if (s && s.lock && Z && Z.drag) springBack(Z, 0);
  }
  document.addEventListener('touchend', release);
  document.addEventListener('touchcancel', cancelSwipe);
  // a tap straight after a swipe is the end of the swipe, not a tap
  const swallow = (e) => e.isTrusted && Date.now() - swipedAt < 350;

  // scrolling, resizing or leaving the app while a zoom plays: it just finishes
  window.addEventListener(
    'scroll',
    () => {
      if (Z && !Z.drag && Z.kind !== 'sheet' && Math.abs(window.scrollY - Z.y) > 8) end(Z);
    },
    { passive: true }
  );
  window.addEventListener('resize', () => Z && end(Z));
  document.addEventListener('visibilitychange', () => document.hidden && Z && end(Z));

  return {
    before,
    after,
    tap,
    arm,
    swallow,
    finishing,
    finished,
    sheetShot,
    sheetInto,
    dayIn,
    busy: () => !!Z,
    end: () => Z && end(Z),
    stack: () => stack.map((e) => Object.assign({}, e)),
    swiping: () => !!(SB && SB.lock),
  };
})();
