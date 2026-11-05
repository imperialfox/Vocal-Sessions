/* ===== The Sheet music page and its guide (Q47) =====
   MELPLAY (also MELODY.play) is milestone M1b of Ivan's Sheet Music Reader Blueprint: a song's score shown as dots or as
   the print's own lines, the vocal line played as a guide, a loop in bars, the speed, and the starting note in one tap.
   - The page is U.view 'mel' (VS-108), opened from the Song page's Sheet music row (VS-009 › sheet-music-row). Its top
     bar's circle opens VS-099 (the score's settings).
   - The guide borrows the pattern player's sounds and output (PAT.guide, H2) and keeps its own state here, under NOW kind
     'melody' (H58). Notes are scheduled a third of a second ahead on the audio clock. Muted notes (the catcher's fret,
     range and jump) are silent; unsure notes play. It stops when its page goes (H28), when the app is hidden, or when
     anything else starts.
   - The loop is bars on the score (score.loop = {from, to, on} in ticks, H14); the track player's sg.loop is never
     touched. The speed uses the pattern player's stops (PAT.SPEEDS, H12).
   - Tap a bar to play from there. Tap a dot: its note when stopped; a jump while playing (H15). Give me my note plays the
     next note from the playhead (PAT.tone when stopped; on the guide's own bus while playing, so nothing stops).
   - The sheet view cuts the print's lines again each time it opens (decision 22, MELODY.cut), keeps only the last song's
     lines as small PNGs, and decodes only the lines near the screen (H42, H47).
   - This device's choices (vocalSongPrefs, never backed up): melView ('dots' or 'sheet'), melBars (bars a line in the
     dots view, 1 to 8; unset is 2 on an iPhone and 4 wider) and melSpeed (an index into PAT.SPEEDS).
   See MAINTAINING › Sheet music. */
const MELPLAY = (() => {
  const TPB = MELODY.TPB;
  const AHEAD = 0.35, // s of notes scheduled ahead
    EVERY = 50, // ms between scheduling passes
    CHUNK = 0.1; // s scheduled in one step
  const P = {
    id: null, // the song playing (or last played)
    on: false,
    bus: null,
    seg: [], // [{tick, time}]: where the playhead was at a time on the audio clock (a loop wrap or a jump adds one)
    cur: null, // {tick, time}: the next tick to schedule and when it sounds
    endAt: null, // the audio time the song ends (no loop)
    timer: 0,
    raf: 0,
    tps: 0, // ticks a second, at the speed
  };
  const pos = {}; // song id → the tick the playhead rests at
  let pick = null, // choosing a loop: {step: 1 | 2, a}
    sheet = { id: null, state: 'none', lines: [], urls: [] }, // the sheet view's lines, last song only
    seen = null, // the IntersectionObserver for the sheet view's pictures
    lastLn = -1;
  const q = (sel) => document.querySelector(sel);

  /* ----- this device's choices ----- */
  const SPEEDS = () => PAT.SPEEDS;
  const ONE = () => SPEEDS().indexOf(1);
  function prefs() {
    const p = sgp();
    if (p.melView !== 'dots' && p.melView !== 'sheet') p.melView = 'dots';
    if (p.melBars != null && !(Number.isInteger(p.melBars) && p.melBars >= 1 && p.melBars <= 8)) delete p.melBars;
    if (!(Number.isInteger(p.melSpeed) && p.melSpeed >= 0 && p.melSpeed < SPEEDS().length)) p.melSpeed = ONE();
    return p;
  }
  const speed = () => SPEEDS()[prefs().melSpeed];
  const wide = () => window.innerWidth >= 700;
  const perLine = () => prefs().melBars || (wide() ? 4 : 2);

  /* ----- the score ----- */
  // the score, read once per redraw (MELODY.get copies it) and once per start of the guide
  let shown = null; // {id, s}
  function score(id) {
    const k = id || U.songId;
    if (shown && shown.id === k) return shown.s;
    const s = MELODY.get(k);
    shown = s ? { id: k, s } : null;
    return s;
  }
  const fresh = () => (shown = null);
  const here = () => U.view === 'mel' && !!U.songId;
  const lastTick = (s) => {
    const b = s.bars[s.bars.length - 1];
    return b ? b.tick + b.len : 0;
  };
  const tpsOf = (s) => ((TPB * (s.tempo || 100)) / 60) * speed();
  function barAt(s, t) {
    let i = 0;
    for (let k = 0; k < s.bars.length; k++) if (s.bars[k].tick <= t) i = k;
    return i;
  }
  const barNum = (b, i) => (b.n != null ? b.n : i + 1);
  // the loop in ticks, when on
  function loopOf(s) {
    const L = s && s.loop;
    if (!L || !L.on || !(L.to > L.from)) return null;
    return { a: L.from, b: Math.min(L.to, lastTick(s)) };
  }
  // flagged bars: the reader's own flags and the "to check" list's bars
  function flagged(s) {
    const set = new Set();
    s.bars.forEach((b, i) => {
      if (b.f && b.f.length) set.add(i);
    });
    const byN = new Map(s.bars.map((b, i) => [b.n, i]));
    MELODY.checks(s).forEach((c) => {
      if (c.n != null && byN.has(c.n)) set.add(byN.get(c.n));
    });
    return set;
  }

  /* ----- the guide ----- */
  function nowTick() {
    const ac = PAT.guide.ctx();
    if (!P.on || !ac || !P.seg.length) return pos[P.id] || 0;
    const t = ac.currentTime;
    let sg = P.seg[0];
    for (const x of P.seg) if (x.time <= t) sg = x;
    if (t < sg.time) return sg.tick;
    return sg.tick + (t - sg.time) * P.tps;
  }
  function sched() {
    const ac = PAT.guide.ctx(),
      s = P.s;
    if (!P.on || !ac || !s) return stop();
    if (P.endAt != null) {
      if (ac.currentTime >= P.endAt + 0.15) {
        P.done = true; // the song's end: the playhead goes back to the start
        stop();
      }
      return;
    }
    const L = loopOf(s),
      end = lastTick(s),
      notes = P.notes;
    let guard = 0;
    while (P.cur.time < ac.currentTime + AHEAD && guard++ < 200) {
      const stopAt = L ? L.b : end,
        to = Math.min(stopAt, P.cur.tick + P.tps * CHUNK);
      notes.forEach((n) => {
        if (n.tick < P.cur.tick || n.tick >= to) return;
        const at = P.cur.time + (n.tick - P.cur.tick) / P.tps,
          d = (Math.min(n.len, stopAt - n.tick) / P.tps) * 0.96;
        if (at >= ac.currentTime - 0.01) PAT.guide.note(n.midi, at, Math.max(0.06, d), P.bus, 1);
      });
      P.cur.time += (to - P.cur.tick) / P.tps;
      P.cur.tick = to;
      if (to >= stopAt) {
        if (L) {
          P.cur.tick = L.a;
          P.seg.push({ tick: L.a, time: P.cur.time });
          if (P.seg.length > 6) P.seg.splice(0, P.seg.length - 6);
        } else {
          P.endAt = P.cur.time;
          break;
        }
      }
    }
  }
  // start the guide from tick t (in a tap)
  function play(t) {
    const s = score();
    if (!s) return;
    if (rec) return toast('Finish the take first');
    const ac = PAT.guide.audio();
    if (!ac) return toast('Sound isn’t available on this device');
    stop(false, true);
    const id = U.songId;
    NOW.start('melody', id, () => stop(true));
    const L = loopOf(s),
      end = lastTick(s);
    let from = t != null ? t : pos[id] || 0;
    if (L && (from < L.a || from >= L.b)) from = L.a;
    if (from >= end) from = 0;
    P.id = id;
    P.on = true;
    P.s = s;
    P.notes = MELODY.line(s);
    P.tps = tpsOf(s);
    P.bus = PAT.guide.bus();
    P.endAt = null;
    const at = ac.currentTime + 0.06;
    P.cur = { tick: from, time: at };
    P.seg = [{ tick: from, time: at }];
    sched();
    P.timer = setInterval(sched, EVERY);
    frame();
    paintDock();
  }
  // from somewhere else while playing (a jump, a new speed, a loop change): what was scheduled fades and it carries on
  function resync(t) {
    const ac = PAT.guide.ctx(),
      s = score(P.id);
    if (!P.on || !ac || !s) return;
    const from = t != null ? t : nowTick();
    P.s = s;
    P.notes = MELODY.line(s);
    PAT.guide.fade(P.bus, 0.02);
    P.bus = PAT.guide.bus();
    P.tps = tpsOf(s);
    P.endAt = null;
    const at = ac.currentTime + 0.04,
      L = loopOf(s);
    let f = from;
    if (L && (f < L.a || f >= L.b)) f = L.a;
    P.cur = { tick: f, time: at };
    P.seg = [{ tick: f, time: at }];
    sched();
  }
  // byNow: another sound started (NOW already moved on); quiet: about to start again
  function stop(byNow, quiet) {
    if (!P.on) return;
    const t = nowTick(),
      s = score(P.id);
    clearInterval(P.timer);
    cancelAnimationFrame(P.raf);
    P.timer = 0;
    P.raf = 0;
    P.on = false;
    if (s) {
      const L = loopOf(s);
      pos[P.id] = P.done ? 0 : L && t >= L.b ? L.a : Math.min(t, lastTick(s));
    }
    P.done = false;
    PAT.guide.fade(P.bus, 0.06);
    P.bus = null;
    if (!byNow) NOW.ended('melody', P.id);
    if (!quiet) {
      paintDock();
      paintHead();
    }
  }
  document.addEventListener('visibilitychange', () => document.hidden && stop());

  /* ----- the playhead ----- */
  function frame() {
    cancelAnimationFrame(P.raf);
    if (!P.on) return;
    paintHead();
    P.raf = requestAnimationFrame(frame);
  }
  // the dots view's lines: [{a, b, el}] read once per redraw
  let lines = null;
  function readLines() {
    lines = [...document.querySelectorAll('#mpBody .mpln')].map((el) => ({ a: +el.dataset.a, b: +el.dataset.b, el }));
  }
  function paintHead() {
    const head = q('#mpHead'),
      s = here() && score();
    if (!head || !s) return;
    const t = P.on && P.id === U.songId ? nowTick() : pos[U.songId] || 0;
    const body = q('#mpBody');
    if (prefs().melView === 'sheet') {
      // the bar being sung, outlined on its line picture
      const bi = barAt(s, t),
        bar = s.bars[bi],
        box = bar && q('#mpBody .mpbar[data-v="' + bi + '"]');
      if (!box) return (head.style.opacity = '0');
      const img = box.parentNode,
        f = Math.max(0, Math.min(1, (t - bar.tick) / bar.len));
      head.style.opacity = '1';
      head.style.height = img.offsetHeight + 'px';
      head.style.transform = 'translate(' + (img.offsetLeft + box.offsetLeft + f * box.offsetWidth).toFixed(1) + 'px,' + img.offsetTop + 'px)';
      follow(img, bi);
      return;
    }
    if (!lines || !lines.length || !lines[0].el.isConnected) readLines();
    const i = lines.findIndex((l) => t >= l.a && t < l.b),
      L = lines[i < 0 ? (t >= (lines[lines.length - 1] || {}).b ? lines.length - 1 : 0) : i];
    if (!L || !body) return (head.style.opacity = '0');
    const svg = L.el.querySelector('svg'),
      vb = svg && svg.viewBox && svg.viewBox.baseVal;
    if (!vb || !vb.width) return;
    const k = svg.clientWidth / vb.width,
      f = Math.max(0, Math.min(1, (t - L.a) / (L.b - L.a))),
      x = (34 + f * (vb.width - 40)) * k; // PITCH.svg's left and right edges (L 34, R 6)
    head.style.opacity = '1';
    head.style.height = Math.round(svg.clientHeight - 24 * k) + 'px';
    head.style.transform = 'translate(' + (L.el.offsetLeft + x).toFixed(1) + 'px,' + (L.el.offsetTop + 8 * k).toFixed(1) + 'px)';
    follow(L.el, lines.indexOf(L));
  }
  // while playing, a line about to leave the screen is brought into view (once per line)
  function follow(el, n) {
    if (!P.on || n === lastLn) return;
    lastLn = n;
    const r = el.getBoundingClientRect(),
      top = 110,
      bottom = window.innerHeight - 130;
    if (r.top >= top && r.bottom <= bottom) return;
    const smooth = !document.documentElement.classList.contains('motion-reduced') && !document.documentElement.classList.contains('motion-off');
    window.scrollTo({ top: window.scrollY + r.top - top, behavior: smooth ? 'smooth' : 'auto' });
  }

  /* ----- drawing ----- */
  // one line of the dots view: bars a to b (indexes), as a PITCH.svg with the notes as dots
  function lineSVG(s, a, b, rg, flags, lanesFn) {
    const A = s.bars[a].tick,
      Bt = s.bars[b].tick + s.bars[b].len,
      beats = (Bt - A) / TPB,
      L = loopOf(s),
      notes = MELODY.drawn(s, A, Bt);
    const under = (x, y, box) => {
      let g = '';
      for (let i = a; i <= b; i++) {
        const bar = s.bars[i],
          x0 = x((bar.tick - A) / TPB),
          x1 = x((bar.tick + bar.len - A) / TPB);
        const inLoop = L && bar.tick >= L.a && bar.tick < L.b,
          picked = pick && pick.step === 2 && i === pick.a;
        g +=
          '<rect class="mpbarbg' + (flags.has(i) ? ' flag' : '') + (inLoop ? ' loop' : '') + (picked ? ' picked' : '') + '" data-a="mpBar" data-v="' + i +
          '" x="' + x0.toFixed(1) + '" y="' + box.T + '" width="' + Math.max(1, x1 - x0).toFixed(1) + '" height="' + (box.H - box.T - box.B) +
          '"><title>Bar ' + barNum(bar, i) + (flags.has(i) ? ', to check' : '') + '</title></rect>';
        g += '<line class="mpbl" x1="' + x0.toFixed(1) + '" x2="' + x0.toFixed(1) + '" y1="' + box.T + '" y2="' + (box.H - box.B) + '"/>';
      }
      const xe = x(beats).toFixed(1);
      g += '<line class="mpbl" x1="' + xe + '" x2="' + xe + '" y1="' + box.T + '" y2="' + (box.H - box.B) + '"/>';
      return g;
    };
    const over = (x, y, box) => {
      const h = Math.max(5, Math.min(10, (box.H - box.T - box.B) / (box.hi - box.lo) - 1));
      return notes
        .map((n) => {
          const x0 = x((Math.max(n.tick, A) - A) / TPB) + 0.8,
            x1 = x((Math.min(n.tick + n.len, Bt) - A) / TPB) - 0.8,
            yy = y(n.midi) - h / 2,
            muted = n.flag === 'fret' || n.flag === 'range' || n.flag === 'jump',
            w = Math.max(h, x1 - x0);
          return (
            '<g data-a="mpDot" data-v="' + n.i + '"><rect class="mphit" x="' + (x0 - 3).toFixed(1) + '" y="' + (yy - 7).toFixed(1) + '" width="' + (w + 6).toFixed(1) +
            '" height="' + (h + 14).toFixed(1) + '"/><rect class="mpn' + (muted ? ' muted' : '') + (n.flag === 'unsure' ? ' unsure' : '') + '" x="' + x0.toFixed(1) +
            '" y="' + yy.toFixed(1) + '" width="' + w.toFixed(1) + '" height="' + h.toFixed(1) + '" rx="' + (h / 2).toFixed(1) + '"><title>' +
            PITCH.name(n.midi) + (muted ? ', silent: caught as a misread' : n.flag === 'unsure' ? ', unsure' : '') + '</title></rect></g>'
          );
        })
        .join('');
    };
    const axis = [];
    for (let i = a; i <= b; i++) axis.push({ t: (s.bars[i].tick - A) / TPB + 0.08, label: barNum(s.bars[i], i) });
    return PITCH.svg([], {
      w: wide() ? 640 : 340,
      h: wide() ? 200 : 150,
      lo: rg.lo,
      hi: rg.hi,
      dur: beats,
      axis,
      under,
      over,
      lanes: lanesFn,
      cls: 'mpsvg',
      label: 'Bars ' + barNum(s.bars[a], a) + ' to ' + barNum(s.bars[b], b),
    });
  }
  function dotsView(s) {
    const rg0 = MELODY.range(s) || { lo: 57, hi: 69 },
      rg = { lo: Math.floor(rg0.lo) - 1, hi: Math.ceil(rg0.hi) + 1 };
    if (rg.hi - rg.lo < 12) {
      const c = Math.round((rg.hi + rg.lo) / 2);
      rg.lo = c - 6;
      rg.hi = c + 6;
    }
    const sg = songById(U.songId),
      k = sg && SONGKEY && SONGKEY.of(sg),
      lanesFn = k ? (lo, hi) => SONGKEY.lanes(k, lo, hi) : null,
      flags = flagged(s),
      n = perLine();
    let out = '';
    for (let a = 0; a < s.bars.length; a += n) {
      const b = Math.min(s.bars.length - 1, a + n - 1),
        A = s.bars[a].tick,
        Bt = s.bars[b].tick + s.bars[b].len;
      out += '<div class="mpln" data-a="' + A + '" data-b="' + Bt + '">' + lineSVG(s, a, b, rg, flags, lanesFn) + '</div>';
    }
    return '<div class="mpdots">' + out + '</div>';
  }
  // bar → the picture it's on: its own picture index (pi, since 3.60), or the nth picture holding notation and tab
  function pictureOf(bar) {
    if (bar.pi != null) return bar.pi;
    const both = sheet.lines.filter((l) => l.both);
    return both[bar.ln] ? both[bar.ln].i : -1;
  }
  function sheetView(s) {
    const id = U.songId;
    if (!MELODY.hasPrint(id))
      return '<div class="mpmsg"><p class="note">Print not on this device</p><p class="foot">The dots still play. Add the print again from Sheet music (the circle at the top) to see its lines.</p></div>';
    if (sheet.id !== id || sheet.state === 'none') cutFor(id);
    if (sheet.state === 'cutting') return '<div class="mpmsg"><p class="note">Getting the print ready…</p></div>';
    if (sheet.state === 'fail') return '<div class="mpmsg"><p class="note">The print couldn’t be opened</p><p class="foot">The dots still play.</p></div>';
    const flags = flagged(s),
      L = loopOf(s),
      byPic = new Map();
    s.bars.forEach((b, i) => {
      const pi = pictureOf(b);
      if (pi < 0) return;
      if (!byPic.has(pi)) byPic.set(pi, []);
      byPic.get(pi).push(i);
    });
    let out = '';
    [...byPic.keys()]
      .sort((u, v) => u - v)
      .forEach((pi) => {
        const ln = sheet.lines.find((l) => l.i === pi);
        if (!ln) return;
        const W = ln.w * 2;
        out +=
          '<div class="mpimg" data-pi="' + pi + '" style="aspect-ratio:' + ln.w + ' / ' + ln.h + '"><img alt="" data-src="' + ln.url + '" draggable="false">' +
          byPic
            .get(pi)
            .map((i) => {
              const b = s.bars[i],
                inLoop = L && b.tick >= L.a && b.tick < L.b,
                picked = pick && pick.step === 2 && i === pick.a;
              return (
                '<button class="mpbar' + (flags.has(i) ? ' flag' : '') + (inLoop ? ' loop' : '') + (picked ? ' picked' : '') + '" data-a="mpBar" data-v="' + i +
                '" style="left:' + ((b.x0 / W) * 100).toFixed(2) + '%;width:' + (((b.x1 - b.x0) / W) * 100).toFixed(2) + '%" aria-label="Bar ' + barNum(b, i) +
                (flags.has(i) ? ', to check' : '') + '"></button>'
              );
            })
            .join('') +
          '</div>';
      });
    return '<div class="mpsheet">' + (out || '<div class="mpmsg"><p class="note">No lines of music found in the print</p></div>') + '</div>';
  }
  // the print's lines, cut again (decision 22): only the last song's are kept, as PNGs
  async function cutFor(id) {
    if (sheet.id === id && sheet.state !== 'none') return;
    sheet.urls.forEach((u) => URL.revokeObjectURL(u));
    sheet = { id, state: 'cutting', lines: [], urls: [] };
    const got = await MELODY.cut(id);
    if (sheet.id !== id) return;
    if (!got) {
      sheet.state = 'fail';
      return here() && U.songId === id && rerender();
    }
    const out = [];
    for (const l of got) {
      const url = await pngOf(l);
      out.push({ i: l.i, w: l.w, h: l.h, both: l.both, url });
      if (url) sheet.urls.push(url);
      l.g = null; // let the grey pixels go (H47)
      await new Promise((r) => setTimeout(r, 0));
      if (sheet.id !== id) return;
    }
    sheet.lines = out;
    sheet.state = 'ready';
    if (here() && U.songId === id && prefs().melView === 'sheet') rerender();
  }
  function pngOf(l) {
    return new Promise((res) => {
      try {
        const c = document.createElement('canvas');
        c.width = l.w;
        c.height = l.h;
        const cx = c.getContext('2d'),
          im = cx.createImageData(l.w, l.h),
          d = im.data;
        for (let i = 0, j = 0; i < l.g.length; i++, j += 4) {
          d[j] = d[j + 1] = d[j + 2] = l.g[i];
          d[j + 3] = 255;
        }
        cx.putImageData(im, 0, 0);
        c.toBlob((b) => {
          c.width = c.height = 0;
          res(b ? URL.createObjectURL(b) : '');
        }, 'image/png');
      } catch (e) {
        res('');
      }
    });
  }
  // H47: only the pictures near the screen are decoded; the rest let go of theirs
  function watchPictures() {
    if (seen) seen.disconnect();
    seen = null;
    const imgs = [...document.querySelectorAll('#mpBody .mpimg img[data-src]')];
    if (!imgs.length) return;
    if (!('IntersectionObserver' in window)) return imgs.forEach((im) => (im.src = im.dataset.src));
    seen = new IntersectionObserver(
      (es) =>
        es.forEach((e) => {
          const im = e.target;
          if (e.isIntersecting) {
            if (im.getAttribute('src') !== im.dataset.src) im.src = im.dataset.src;
          } else if (im.getAttribute('src')) im.removeAttribute('src');
        }),
      { rootMargin: '100% 0px' }
    );
    imgs.forEach((im) => seen.observe(im));
  }

  /* ----- the page ----- */
  const SPD = (i) => String(SPEEDS()[i]) + '×';
  function page() {
    fresh();
    const s = score();
    if (!s)
      return '<div class="mp"><div class="mpmsg"><p class="note">' + (MELODY.loaded() ? 'Sheet not on this device' : 'Loading…') + '</p></div></div>';
    const p = prefs(),
      sg = songById(U.songId),
      L = s.loop,
      sp = p.melSpeed,
      bars = s.bars.length ? barNum(s.bars[s.bars.length - 1], s.bars.length - 1) : 0;
    let strip = '';
    if (pick)
      strip =
        '<div class="mploop picking" role="status"><span>' + (pick.step === 1 ? 'Tap the first bar of the loop' : 'Now tap its last bar') +
        '</span><button class="mpchip" data-a="mpPickX">Cancel</button></div>';
    else if (L && L.to > L.from) {
      const a = barAt(s, L.from),
        b = barAt(s, L.to - 1);
      strip =
        '<div class="mploop' + (L.on ? ' on' : '') + '"><span>' + (L.on ? 'Looping' : 'Loop off') + ' · bars ' + barNum(s.bars[a], a) + (b !== a ? '–' + barNum(s.bars[b], b) : '') +
        '</span><button class="mpchip" data-a="mpPick">Change</button></div>';
    }
    return (
      '<div class="mp">' +
      '<h1 class="mptitle">' + esc((sg && songTitle(sg)) || 'Sheet music') + '</h1>' +
      '<p class="foot mpsub">' + esc(['Sheet music', bars + ' bars', 'tempo ' + (s.tempo || 100)].join(' · ')) + '</p>' +
      '<div class="seg pk-seg wide mpview" role="group" aria-label="View"><span class="pk-seg-ind" aria-hidden="true"></span>' +
      [['dots', 'Dots'], ['sheet', 'Sheet']]
        .map((x) => '<button data-a="mpView" data-v="' + x[0] + '" class="' + (p.melView === x[0] ? 'on' : '') + '" aria-pressed="' + (p.melView === x[0]) + '">' + x[1] + '</button>')
        .join('') +
      '</div>' +
      '<div class="mpctl"><div class="mpstep mpspd" role="group" aria-label="Speed"><span class="lbl">Speed</span>' +
      '<button class="shbtn glass" data-a="mpSpd" data-v="-1" aria-label="Slower"' + (sp <= 0 ? ' disabled' : '') + '>−</button>' +
      '<span class="mpval" id="mpSpdV">' + SPD(sp) + '</span>' +
      '<button class="shbtn glass" data-a="mpSpd" data-v="1" aria-label="Faster"' + (sp >= SPEEDS().length - 1 ? ' disabled' : '') + '>+</button></div>' +
      (p.melView === 'dots'
        ? '<div class="mpstep mpzoom" role="group" aria-label="Bars a line"><span class="lbl">Bars</span>' +
          '<button class="shbtn glass" data-a="mpZoom" data-v="-1" aria-label="Fewer bars a line"' + (perLine() <= 1 ? ' disabled' : '') + '>−</button>' +
          '<span class="mpval">' + perLine() + '</span>' +
          '<button class="shbtn glass" data-a="mpZoom" data-v="1" aria-label="More bars a line"' + (perLine() >= 8 ? ' disabled' : '') + '>+</button></div>'
        : '') +
      '</div>' +
      strip +
      '<div id="mpBody" class="mpbody ' + p.melView + '">' + (p.melView === 'sheet' ? sheetView(s) : dotsView(s)) + '<div id="mpHead" class="mphead" aria-hidden="true"></div></div>' +
      '</div>'
    );
  }
  function bar() {
    const sg = songById(U.songId);
    return {
      l: '<button class="circ glass" data-a="mpBack" aria-label="Back">' + ICON.back + '</button>',
      t: sg ? esc(songTitle(sg)) : 'Sheet music',
      r: sg && MELODY.has(sg.id) ? '<button class="circ glass" data-a="melInfo" data-k="' + sg.id + '" aria-label="Sheet music settings">' + SGI.more + '</button>' : '',
    };
  }
  const NOTE =
    '<svg class="i" viewBox="0 0 24 24"><path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5" fill="currentColor" stroke="none"/><circle cx="16.5" cy="16" r="2.5" fill="currentColor" stroke="none"/></svg>';
  const LOOPI =
    '<svg class="i" viewBox="0 0 24 24"><path d="M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4"/></svg>';
  // the transport, in the dock: the track player's (give me my note, play, loop)
  function dock() {
    if (!here() || U.sheet || !score()) return '';
    const on = P.on && P.id === U.songId,
      s = score(),
      lo = !!(s.loop && s.loop.on);
    return (
      '<div class="trktr glass mptr" role="group" aria-label="Sheet music guide"><button class="trkb" data-a="mpMy" aria-label="Give me my note">' + NOTE +
      '</button><button class="trkpp" id="mpPP" data-a="mpPP" data-on="' + on + '" aria-label="' + (on ? 'Pause' : 'Play') + '">' + (on ? ICON.pause : ICON.play) +
      '</button><button class="trkb trkloopb' + (lo ? ' on' : '') + '" id="mpLoopB" data-a="mpLoop" aria-pressed="' + lo + '" aria-label="Loop">' + LOOPI + '</button></div>'
    );
  }
  // the dock's buttons in place (no redraw, so the page doesn't jump)
  function paintDock() {
    const pp = q('#mpPP'),
      on = P.on && P.id === U.songId;
    if (pp) {
      pp.dataset.on = on;
      pp.setAttribute('aria-label', on ? 'Pause' : 'Play');
      pp.innerHTML = on ? ICON.pause : ICON.play;
    }
  }

  /* ----- doors ----- */
  function open(id) {
    if (!songById(id) || !MELODY.has(id)) return;
    go(() => {
      U.tab = 'songs';
      U.view = 'mel';
      U.songId = id;
      U.sheet = null;
      U.sd = {};
    });
  }
  function back() {
    const id = U.songId,
      ok = !!songById(id);
    go(() => {
      U.tab = 'songs';
      U.view = ok && !split() ? 'lyr' : null;
      U.sheet = null;
      U.sd = {};
    });
  }
  // after every redraw: the guide stops when its page goes (H28); the playhead and the pictures are put back
  function after() {
    if (P.on && (U.view !== 'mel' || U.songId !== P.id || !MELODY.has(P.id))) stop();
    if (U.view !== 'mel') {
      pick = null;
      if (seen) seen.disconnect();
      seen = null;
      return;
    }
    lines = null;
    lastLn = -1;
    if (prefs().melView === 'sheet') watchPictures();
    paintHead();
  }

  /* ----- actions (data-a="mp…") ----- */
  function setLoop(from, to, on) {
    MELODY.edit(U.songId, { loop: { from, to, on } }).then(() => {
      fresh();
      if (P.on) resync();
    });
  }
  function myNote() {
    const s = score();
    if (!s) return;
    const L = loopOf(s);
    let t = P.on && P.id === U.songId ? nowTick() : pos[U.songId] || 0;
    if (L && (t < L.a || t >= L.b)) t = L.a;
    const n = MELODY.line(s, t).find((x) => x.tick + x.len > t);
    if (!n) return toast('No notes after here');
    if (P.on && P.id === U.songId) {
      // H15: while the guide plays, its own bus sounds the note; nothing else stops
      const ac = PAT.guide.ctx();
      if (ac && P.bus) PAT.guide.note(n.midi, ac.currentTime + 0.02, 1.1, P.bus, 1);
      return;
    }
    PAT.tone(n.midi);
  }
  Object.assign(SG_ACT, {
    mpBack: () => back(),
    mpPP: () => {
      if (P.on && P.id === U.songId) stop();
      else play();
    },
    mpMy: () => myNote(),
    mpLoop: () => {
      const s = score();
      if (!s) return;
      const L = s.loop;
      if (L && L.to > L.from) return setLoop(L.from, L.to, !L.on);
      // no loop yet: the bars of the line the playhead is on
      const t = P.on && P.id === U.songId ? nowTick() : pos[U.songId] || 0,
        n = perLine(),
        bi = barAt(s, t),
        a = Math.floor(bi / n) * n,
        b = Math.min(s.bars.length - 1, a + n - 1);
      setLoop(s.bars[a].tick, s.bars[b].tick + s.bars[b].len, true);
    },
    mpPick: () => {
      pick = { step: 1 };
      rerender();
    },
    mpPickX: () => {
      pick = null;
      rerender();
    },
    mpBar: (el, v) => {
      const s = score(),
        i = +v;
      if (!s || !s.bars[i]) return;
      if (pick) {
        if (pick.step === 1) {
          pick = { step: 2, a: i };
          return rerender();
        }
        const a = Math.min(pick.a, i),
          b = Math.max(pick.a, i);
        pick = null;
        return setLoop(s.bars[a].tick, s.bars[b].tick + s.bars[b].len, true);
      }
      const t = s.bars[i].tick;
      if (P.on && P.id === U.songId) return resync(t);
      pos[U.songId] = t;
      play(t);
    },
    mpDot: (el, v) => {
      const s = score(),
        n = s && s.notes[+v];
      if (!n) return;
      if (n.flag === 'fret' || n.flag === 'range' || n.flag === 'jump') return toast('This note was caught as a misread, so it stays silent');
      if (P.on && P.id === U.songId) return resync(n.tick);
      pos[U.songId] = n.tick;
      PAT.tone(n.midi + 12 * (s.octave || 0) + (s.shift || 0));
      paintHead();
    },
    mpView: (el, v) => {
      if (v !== 'dots' && v !== 'sheet') return;
      segPick(el);
      prefs().melView = v;
      saveSGP();
      rerender();
    },
    mpSpd: (el, v) => {
      const p = prefs();
      p.melSpeed = Math.max(0, Math.min(SPEEDS().length - 1, p.melSpeed + (+v || 0)));
      saveSGP();
      if (P.on) resync();
      rerender();
    },
    mpZoom: (el, v) => {
      const p = prefs();
      p.melBars = Math.max(1, Math.min(8, perLine() + (+v || 0)));
      saveSGP();
      rerender();
    },
  });

  return {
    page,
    bar,
    dock,
    open,
    back,
    after,
    play,
    stop,
    // for the tests
    state: () => ({
      on: P.on,
      id: P.id,
      tick: Math.round(nowTick()),
      pos: Object.assign({}, pos),
      speed: speed(),
      tps: P.tps,
      view: prefs().melView,
      bars: perLine(),
      pick: pick ? Object.assign({}, pick) : null,
      sheet: { id: sheet.id, state: sheet.state, lines: sheet.lines.length },
      kind: NOW.kind ? NOW.kind() : null,
    }),
  };
})();
MELODY.play = MELPLAY;
