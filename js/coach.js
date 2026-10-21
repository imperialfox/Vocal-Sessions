/* Vocal Sessions · coach.js
   The coach video (3.16): Ivan adds his coach's video on the phone (Settings › Coach video). It stays on the device in
   IndexedDB, never in backups and never on the public site. One <video id="cv"> plays it everywhere: the player page,
   inside a session step, and the floating window. render() replaces #app with innerHTML, so the video never lives
   in #app for good: it's parked in a hidden holder on <body> before each redraw and moved into the new screen's
   .cv-slot afterwards (or into the floating window). Moving it within the same task doesn't pause it.
   Chapters: the video is exercises 1–12 of the course. Where each starts comes from COACH_TIMES in content.js (the
   YouTube timestamps); an exercise given three times there also has levels. A video whose length isn't within 10 s
   of COACH_END is treated as a plain video with no chapters.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Chapters ===== */
// '1:04:30' or '7:15' in seconds (NaN if it isn't a time)
const coachSecs = (x) => {
  const p = String(x).trim().split(':');
  if (p.length < 2 || p.length > 3 || p.some((v) => !/^\d+$/.test(v))) return NaN;
  return p.reduce((a, v) => a * 60 + +v, 0);
};
// the chapters, numbered in the order they start: COACH_CH[n] is [start] or [Level 1, Level 2, Level 3] in seconds;
// COACH_MAP[id] is the exercise's number. Built from COACH_TIMES (content.js), skipping anything that doesn't parse.
const COACH_CH = {},
  COACH_MAP = {};
(() => {
  const rows = Object.keys(typeof COACH_TIMES === 'object' ? COACH_TIMES : {})
    .filter((id) => FOUND.concat(ROT).some((e) => e.id === id))
    .map((id) => {
      let t = (Array.isArray(COACH_TIMES[id]) ? COACH_TIMES[id] : [COACH_TIMES[id]]).map(coachSecs);
      // levels only when there are three times, all valid and in order
      if (!(t.length === 3 && t.every((v, i) => isFinite(v) && (!i || v > t[i - 1])))) t = [t[0]];
      return { id, t };
    })
    .filter((r) => isFinite(r.t[0]))
    .sort((a, b) => a.t[0] - b.t[0]);
  rows.forEach((r, i) => {
    COACH_CH[i + 1] = r.t;
    COACH_MAP[r.id] = i + 1;
  });
})();
const COACH_N = Object.keys(COACH_CH).length; // 12
const COACH_IDS = Object.keys(COACH_MAP).sort((a, b) => COACH_MAP[a] - COACH_MAP[b]);
const COACH_END = 4773, // 79:33, the length of the coach video Ivan keeps in Files
  COACH_SLACK = 10;
// short names for the floating window's slim bar
const COACH_SHORT = {
  slides: 'Slides',
  lip: 'Lip bubbling',
  upperlower: 'Upper to lower',
  straw: 'Straw',
  rung: 'On the rung',
  hinge: 'Squeaky hinge',
  half: 'Half squeaky',
  vertical: 'Vertical mouth',
  nasal: 'Nasal',
  flex: 'Flexibility',
  falsetto: 'Falsetto',
};
const COACH_SPEEDS = [0.75, 1, 1.25];
const COACH_PREF = 'vocalCoach'; // this device only, never backed up: {t, speed, loop}

const COACH = (() => {
  let meta = null; // {name, size, type, dur, chapters} once a video is added
  let url = null;
  let el = null; // the one <video id="cv">
  let hold = null; // where it waits when no screen shows it
  let busy = false; // adding a video
  let woke = false; // played since the app opened (so a paused video from last time doesn't pop up a window)
  let dismissed = false; // ✕ on the floating window, until the next play
  let cur = null; // the level being played, for Loop
  let lastEx = null; // the exercise the player page was drawn for
  let seekBy = 0; // a seek you made (not Loop), so Loop follows you to the new level
  let drag = null; // scrubbing
  let raf = 0;
  let savedAt = 0;
  // where the video was last on screen, for the floating window's tap: {view, y, back}
  let where = null;
  let prefs = { t: 0, speed: 1, loop: false };
  try {
    const p = JSON.parse(localStorage.getItem(COACH_PREF) || '{}');
    if (+p.t >= 0 && isFinite(+p.t)) prefs.t = +p.t;
    if (COACH_SPEEDS.includes(+p.speed)) prefs.speed = +p.speed;
    prefs.loop = p.loop === true;
  } catch (e) {}
  const savePrefs = () => {
    try {
      localStorage.setItem(COACH_PREF, JSON.stringify(prefs));
    } catch (e) {}
  };

  /* ----- stored on the device (its own database, apart from recordings and backups) ----- */
  let dbp = null;
  function cdb() {
    if (dbp) return dbp;
    dbp = new Promise((res, rej) => {
      if (!window.indexedDB) return rej(new Error('no idb'));
      const r = indexedDB.open('vocalCoach', 1);
      r.onupgradeneeded = () => {
        if (!r.result.objectStoreNames.contains('video')) r.result.createObjectStore('video');
      };
      r.onsuccess = () => {
        const d = r.result;
        d.onversionchange = () => {
          d.close();
          dbp = null;
        };
        res(d);
      };
      r.onerror = () => {
        dbp = null;
        rej(r.error);
      };
    });
    return dbp;
  }
  async function ctx(mode, fn) {
    const d = await cdb();
    return new Promise((res, rej) => {
      const t = d.transaction('video', mode);
      const out = fn(t.objectStore('video'));
      t.oncomplete = () => res(out && out.result !== undefined ? out.result : undefined);
      t.onerror = () => rej(t.error);
      t.onabort = () => rej(t.error);
    });
  }
  const okRec = (r) => r && r.blob instanceof Blob && r.blob.size > 0 && +r.dur > 0;
  const chaptersFor = (dur) => Math.abs(dur - COACH_END) <= COACH_SLACK;

  /* ----- the video element ----- */
  function video() {
    if (el) return el;
    hold = document.createElement('div');
    hold.id = 'cvHold';
    hold.setAttribute('aria-hidden', 'true');
    document.body.appendChild(hold);
    el = document.createElement('video');
    el.id = 'cv';
    el.setAttribute('playsinline', '');
    el.setAttribute('webkit-playsinline', '');
    el.preload = 'metadata';
    el.disablePictureInPicture = true;
    el.setAttribute('aria-label', 'Coach video');
    pitch();
    el.addEventListener('play', () => {
      woke = true;
      dismissed = false;
      // one sound at a time: a take stops when the coach starts
      if (typeof player !== 'undefined' && player) {
        stopPlayback();
        rerender();
      }
      loop();
      changed();
    });
    el.addEventListener('pause', () => {
      keep(true);
      changed();
    });
    el.addEventListener('ended', () => {
      if (prefs.loop && meta && meta.chapters && cur) {
        el.currentTime = cur.s;
        el.play().catch(() => {});
        return;
      }
      keep(true);
      changed();
    });
    el.addEventListener('timeupdate', () => {
      tick();
      keep();
    });
    el.addEventListener('seeked', () => paint());
    el.addEventListener('loadedmetadata', () => {
      if (prefs.t > 0 && prefs.t < el.duration - 1 && el.currentTime < 0.5) el.currentTime = prefs.t;
      el.playbackRate = prefs.speed;
      pitch();
      cur = chapters() ? at(el.currentTime) : null;
      // the Exercises row says where you paused, once the video knows
      if (!U.view && U.tab === 'exercises') rerender();
      else paint();
    });
    if ('mediaSession' in navigator) {
      const ms = navigator.mediaSession,
        on = (a, f) => {
          try {
            ms.setActionHandler(a, f);
          } catch (e) {}
        };
      on('play', () => play());
      on('pause', () => pause());
      on('seekbackward', (d) => skip(-((d && d.seekOffset) || 10)));
      on('seekforward', (d) => skip((d && d.seekOffset) || 10));
      on('seekto', (d) => d && isFinite(d.seekTime) && seek(d.seekTime));
    }
    return el;
  }
  function pitch() {
    if (!el) return;
    el.preservesPitch = true;
    el.webkitPreservesPitch = true;
    el.mozPreservesPitch = true;
  }
  function setSrc(blob) {
    const v = video();
    if (url) URL.revokeObjectURL(url);
    url = URL.createObjectURL(blob);
    v.src = url;
    v.playbackRate = prefs.speed;
  }
  // remember where you got to (every few seconds while playing, and on pause)
  function keep(now) {
    if (!el || !meta) return;
    if (!now && Date.now() - savedAt < 4000) return;
    savedAt = Date.now();
    prefs.t = el.ended ? 0 : Math.round(el.currentTime * 10) / 10;
    savePrefs();
  }
  window.addEventListener('pagehide', () => keep(true));

  /* ----- where it is on screen ----- */
  // back to the holder, just before #app is redrawn (render() in ui.js)
  function park() {
    if (!el || el.parentNode === hold) return;
    if (el.closest && el.closest('#app')) where = Object.assign({}, where || {}, { y: window.scrollY });
    hold.appendChild(el);
  }
  // after a redraw or a change to the floating window: into this screen's slot, the window, or the holder
  function place() {
    if (!el) return;
    const slot = document.querySelector('#app .cv-slot'),
      fwv = FW.shown === 'video' && FW.el ? FW.el.querySelector('.cv-fw') : null,
      to = slot || fwv || hold;
    if (slot) where = { view: U.view, y: (where && where.view === U.view && where.y) || 0, back: U.coachBack };
    if (el.parentNode !== to) to.insertBefore(el, to.firstChild);
    paint();
  }
  window.addEventListener(
    'scroll',
    () => {
      if (el && where && el.closest && el.closest('#app') && !U.sheet) where.y = window.scrollY;
    },
    { passive: true }
  );

  /* ----- chapters ----- */
  const has = () => !!(meta && url);
  const chapters = () => !!(meta && meta.chapters);
  const end = () => (el && isFinite(el.duration) && el.duration > 0 ? el.duration : (meta && meta.dur) || COACH_END);
  const idOf = (n) => COACH_IDS.find((id) => COACH_MAP[id] === n);
  const exEnd = (n) => {
    if (n < COACH_N) return COACH_CH[n + 1][0];
    const c = COACH_CH[n];
    return Math.max(c[c.length - 1] + 1, Math.min(end(), COACH_END));
  };
  // the exercise (and level, when it has levels) at a time: {n, id, l, lv, s, e}. lv is how many levels it has
  // (3, or 1 when only its start is known); s and e are where that level, or the whole exercise, starts and ends
  function at(t) {
    let n = 1;
    for (let i = 1; i <= COACH_N; i++) if (t >= COACH_CH[i][0] - 0.25) n = i;
    const c = COACH_CH[n],
      lv = c.length;
    let l = 1;
    for (let i = 1; i <= lv; i++) if (t >= c[i - 1] - 0.25) l = i;
    return { n, id: idOf(n), l, lv, s: c[l - 1], e: l < lv ? c[l] : exEnd(n) };
  }
  const hasLevels = (id) => !!(COACH_MAP[id] && COACH_CH[COACH_MAP[id]].length === 3);
  // what the chapters hold, e.g. "12 exercises" or "12 exercises · 3 levels each"
  const sumTxt = () => {
    const nl = Object.values(COACH_CH).filter((c) => c.length === 3).length;
    return COACH_N + ' exercises' + (nl === COACH_N ? ' · 3 levels each' : nl ? ' · ' + nl + ' with levels' : '');
  };
  const lvTxt = (a, short) => (a && a.lv === 3 ? (short ? ' · L' : ' · Level ') + a.l : '');
  const now = () => (drag ? drag.t : el && el.readyState >= 1 ? el.currentTime : prefs.t) || 0;
  const here = () => (chapters() ? at(now()) : null);
  // the level Ivan is on for an exercise: what this session has set, else his latest logged level, else 1
  function level(id) {
    const s = X && X.kind !== 'song' && ((X.f && +X.f[id]) || (X.rot && +X.rot[id]));
    if (s >= 1 && s <= 3) return s;
    const h = typeof exHistory === 'function' ? exHistory(id) : [];
    const lv = h.length ? +h[h.length - 1].lv : 0;
    return lv >= 1 && lv <= 3 ? lv : 1;
  }
  const exName = (id) => (exById(id) || { name: 'Exercise' }).name;

  /* ----- playing ----- */
  function play() {
    if (!has()) return;
    const v = video();
    if (typeof player !== 'undefined' && player) stopPlayback();
    dismissed = false;
    v.play().catch(() => {
      toast('Couldn’t play the coach video');
      changed();
    });
  }
  function pause() {
    if (el && !el.paused) el.pause();
  }
  const toggle = () => (el && !el.paused ? pause() : play());
  function seek(t) {
    if (!has()) return;
    const v = video();
    seekBy = Date.now();
    v.currentTime = Math.max(0, Math.min(end() - 0.2, t));
    if (v.readyState < 1) prefs.t = v.currentTime; // not loaded yet: it starts from here once it has
    cur = chapters() ? at(v.currentTime) : null;
    session();
    // a different exercise on the player page: draw its list and scrubber again
    if (cur && U.view === 'coach' && cur.n !== lastEx && document.querySelector('#app .cvpage')) rerender();
    else paint();
  }
  const skip = (d) => seek(now() + d);
  // an exercise at a level, playing or not
  function cue(id, lv, andPlay) {
    const n = COACH_MAP[id];
    if (!n || !chapters()) return false;
    const c = COACH_CH[n];
    seek(c.length === 3 ? c[Math.max(1, Math.min(3, lv || level(id))) - 1] : c[0]);
    if (andPlay) play();
    else pause();
    changed();
    return true;
  }
  // Loop: at the end of the level you're on, back to its start
  function tick() {
    const t = el ? el.currentTime : 0;
    if (chapters()) {
      const a = at(t);
      if (
        prefs.loop &&
        cur &&
        !drag &&
        Date.now() - seekBy > 400 &&
        a.s !== cur.s &&
        t >= cur.e - 0.35 &&
        t < cur.e + 3
      ) {
        el.currentTime = cur.s;
        seekBy = Date.now();
        return;
      }
      if (!cur || a.s !== cur.s) {
        const was = cur;
        cur = a;
        if (!was || was.n !== a.n || was.l !== a.l) chapterChanged();
      }
    }
    paint();
  }
  function loop() {
    cancelAnimationFrame(raf);
    const f = () => {
      if (!el || el.paused) return;
      paint();
      if (FW.shown === 'video') fwTick();
      raf = requestAnimationFrame(f);
    };
    raf = requestAnimationFrame(f);
  }
  function chapterChanged() {
    meta && meta.chapters && session();
    // the player page's exercise list and level picker follow along
    if (U.view === 'coach' && document.querySelector('#app .cvpage')) {
      const a = here();
      if (a && a.n !== lastEx) rerender();
      else paintLevel();
    }
    if (FW.shown === 'video') fwUpdate();
  }
  // the lock screen and Control Centre show what's playing
  function session() {
    if (!('mediaSession' in navigator) || !window.MediaMetadata) return;
    const a = here();
    try {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: a ? exName(a.id) + lvTxt(a) : (meta && meta.name) || 'Coach video',
        artist: 'Coach video',
        album: 'Vocal Sessions',
      });
    } catch (e) {}
  }
  function changed() {
    session();
    if (U.view === 'coach' || document.querySelector('#app .cv-slot')) paint();
    fwUpdate();
  }

  /* ----- drawing in place (no redraw while playing: stillness) ----- */
  const fmt = (s) => {
    s = Math.max(0, Math.round(s));
    const h = Math.floor(s / 3600),
      m = Math.floor((s % 3600) / 60),
      x = String(s % 60).padStart(2, '0');
    return h ? h + ':' + String(m).padStart(2, '0') + ':' + x : m + ':' + x;
  };
  // the stretch the scrubber covers: the current exercise, or the whole video without chapters
  function span() {
    if (!chapters()) return { s: 0, e: end(), segs: [end()] };
    const a = here(),
      c = COACH_CH[a.n],
      e = exEnd(a.n),
      b = c.concat([e]);
    return { s: c[0], e, segs: c.map((v, i) => b[i + 1] - v), a };
  }
  function paint() {
    const v = el,
      t = now(),
      pg = document.querySelector('#app .cvpage');
    document.querySelectorAll('#app .cv-slot').forEach((s) => s.classList.toggle('paused', !v || v.paused));
    if (pg) {
      const sp = span(),
        len = Math.max(0.01, sp.e - sp.s);
      // each level's segment fills on its own; the thumb sits where the time is, gaps between segments allowed for
      const segs = pg.querySelectorAll('.cvsegs i'),
        th = $('cvThumb');
      let a = sp.s,
        x = 0;
      segs.forEach((g, j) => {
        const w = sp.segs[j] || 0,
          f = Math.max(0, Math.min(1, (t - a) / Math.max(0.01, w)));
        g.firstChild.style.width = (f * 100).toFixed(2) + '%';
        if (t >= a - 0.01 && (t < a + w || j === segs.length - 1)) x = g.offsetLeft + f * g.offsetWidth;
        a += w;
      });
      if (th) th.style.left = x.toFixed(1) + 'px';
      const sc = $('cvScrub');
      if (sc) {
        sc.setAttribute('aria-valuenow', Math.round(t - sp.s));
        sc.setAttribute('aria-valuetext', fmt(t - sp.s) + ' of ' + fmt(len));
      }
      const elT = $('cvEl'),
        rem = $('cvRem');
      if (elT) elT.textContent = fmt(t - sp.s);
      if (rem) rem.textContent = '−' + fmt(sp.e - t);
      const pp = $('cvPP');
      if (pp) {
        const on = !!(v && !v.paused);
        if (pp.dataset.on !== String(on)) {
          pp.dataset.on = String(on);
          pp.innerHTML = on ? ICON.pause : ICON.play;
          pp.setAttribute('aria-label', on ? 'Pause' : 'Play');
        }
      }
      paintLevel();
    }
    const cap = $('cvCap');
    if (cap) {
      const a = here();
      cap.textContent = a ? 'Exercise ' + a.n + ' · ' + exName(a.id) + lvTxt(a) : '';
    }
  }
  function paintLevel() {
    const a = here();
    if (!a) return;
    const tt = $('cvTitle'),
      lt = $('cvLevel');
    if (tt) tt.textContent = 'Exercise ' + a.n + ' · ' + exName(a.id);
    if (lt) lt.textContent = a.lv === 3 ? 'Level ' + a.l + ' of 3' : '';
    const sg = document.querySelector('#app .cvlv');
    if (sg) {
      const on = sg.querySelector('button.on');
      if (!on || +on.dataset.v !== a.l) {
        const b = sg.querySelector('button[data-v="' + a.l + '"]');
        if (b) segPick(b);
      }
    }
  }

  /* ----- screens ----- */
  const thumb = (big) =>
    '<span class="cvthumb' + (big ? ' big' : '') + '" aria-hidden="true">' + ICON.play + '</span>';
  const WAVE =
    '<svg class="cvwave" viewBox="0 0 18 14" aria-hidden="true"><rect x="0" y="5" width="3" height="9" rx="1.5"/><rect x="5" y="1" width="3" height="13" rx="1.5"/><rect x="10" y="3" width="3" height="11" rx="1.5"/><rect x="15" y="7" width="3" height="7" rx="1.5"/></svg>';
  const FS =
    '<svg class="i" viewBox="0 0 24 24"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>';
  const B10 =
    '<svg class="i" viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4"/><text x="12" y="15.5" text-anchor="middle" font-size="7" font-weight="700" fill="currentColor" stroke="none">10</text></svg>';
  const F10 =
    '<svg class="i" viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.3-5.6M20 4v4h-4"/><text x="12" y="15.5" text-anchor="middle" font-size="7" font-weight="700" fill="currentColor" stroke="none">10</text></svg>';
  const LOOP =
    '<svg class="i" viewBox="0 0 24 24"><path d="M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4"/></svg>';
  const speedTxt = () => String(prefs.speed).replace(/^0\./, '0.') + '×';

  // Exercises tab: the row at the top (a door into the player, or into Settings › Coach video)
  function exercisesRow() {
    if (!has())
      return (
        '<div class="grp" style="margin-top:8px"><button class="row cvrow" data-a="coachSettings">' +
        thumb() +
        '<span class="lbl"><span class="acc">Add coach video</span><small>Watch it here, kept on this ' +
        deviceName() +
        '</small></span>' +
        chev +
        '</button></div>'
      );
    const a = here(),
      playing = el && !el.paused;
    const sub = !chapters()
      ? (playing ? 'Playing' : now() > 0.5 ? 'Paused at ' + fmt(now()) : 'No chapters')
      : now() > 0.5 || playing
        ? (playing ? 'Playing ' : 'Paused at ') + exName(a.id) + lvTxt(a)
        : COACH_N + ' exercises';
    return (
      '<div class="grp" style="margin-top:8px"><button class="row cvrow" data-zk="coach" data-a="openCoach">' +
      thumb() +
      '<span class="lbl">Coach video<small>' +
      esc(sub) +
      '</small></span>' +
      chev +
      '</button></div>'
    );
  }
  // an exercise's page: Play with coach (exercises 1–12, once a video with chapters is added)
  function exerciseRow(id) {
    if (!chapters() || !COACH_MAP[id]) return '';
    return (
      '<div class="grp" style="margin-top:14px"><button class="row cvrow tall" data-zk="coach:' +
      id +
      '" data-a="openCoach" data-k="' +
      id +
      '">' +
      thumb(true) +
      '<span class="lbl">Play with coach<small>' +
      (hasLevels(id) ? 'Level ' + level(id) : 'From the start of the exercise') +
      '</small></span>' +
      chev +
      '</button></div>'
    );
  }
  // the exercises a session step goes through, in order, that have a chapter
  function stepList(view) {
    if (!X || X.kind === 'song') return [];
    if (view === 'found') return FOUND.map((e) => e.id).filter((id) => COACH_MAP[id]);
    if (view === 'rot') {
      const picked = Object.keys(X.rot || {}).filter((id) => COACH_MAP[id]);
      if (picked.length) return picked.sort((a, b) => COACH_MAP[a] - COACH_MAP[b]);
      const s = suggested();
      return ROT.map((e) => e.id)
        .filter((id) => COACH_MAP[id])
        .sort((a, b) => (a === s.id ? -1 : b === s.id ? 1 : COACH_MAP[a] - COACH_MAP[b]));
    }
    return [];
  }
  // the one to start a step on: the first without a level yet (Foundation), or the first picked (Rotation)
  function stepEx(view) {
    const l = stepList(view);
    if (!l.length) return null;
    if (view === 'found') return l.find((id) => !(id in (X.f || {}))) || l[0];
    return l[0];
  }
  // a focused session step: hidden until tapped, then the video sits under the title for the rest of the session
  function stepHTML(view) {
    if (!chapters() || !X || X.kind === 'song') return '';
    const id = stepEx(view);
    if (!id) return '';
    if (!X.cv)
      return (
        '<div class="grp cvstep"><button class="row cvrow" data-a="coachShow">' +
        thumb() +
        '<span class="lbl">Coach video' +
        (hasLevels(id) ? ' · Level ' + level(id) : '') +
        '<small>' +
        esc(exName(id)) +
        ' · tap to show</small></span></button></div>'
      );
    return (
      '<div class="cvstep shown"><div class="cv-slot inline" data-a="coachPlay">' +
      '<button class="cvbig" data-a="coachPlay" aria-label="Play">' +
      ICON.play +
      '</button></div>' +
      '<div class="cvcapr"><button class="circ cvnav" data-a="coachStepEx" data-v="-1" aria-label="Previous exercise in the video">' +
      ICON.back +
      '</button><span class="cvcap" id="cvCap" role="status"></span><button class="circ cvnav" data-a="coachStepEx" data-v="1" aria-label="Next exercise in the video">' +
      ICON.fwd +
      '</button></div></div>'
    );
  }
  // the player page
  function page() {
    let h = '<h1>Coach video</h1>';
    if (!has())
      return (
        h +
        '<p class="note">' +
        sumTxt() +
        '</p><div class="grp"><div class="empty">Add the coach video from Files to watch it here. It stays on this ' +
        deviceName() +
        ' and isn’t put online.</div><button class="row acc" data-a="coachSettings"><span class="lbl">Add coach video…</span>' +
        chev +
        '</button></div>'
      );
    const ch = chapters(),
      sp = span(),
      a = sp.a,
      len = Math.max(0.01, sp.e - sp.s);
    lastEx = a ? a.n : null;
    const on = !!(el && !el.paused);
    h +=
      '<p class="note">' +
      (ch ? sumTxt() : esc(meta.name) + ' · No chapters') +
      '</p><div class="cvpage">' +
      '<div class="cv-slot" data-a="coachPlay"><button class="cvfs" data-a="coachFS" aria-label="Full screen">' +
      FS +
      '</button></div>' +
      (ch
        ? '<div class="cvnow"><b id="cvTitle">Exercise ' +
          a.n +
          ' · ' +
          esc(exName(a.id)) +
          '</b><small id="cvLevel">' +
          (a.lv === 3 ? 'Level ' + a.l + ' of 3' : '') +
          '</small></div>'
        : '') +
      '<div class="cvscrub" id="cvScrub" data-own-gesture role="slider" tabindex="0" aria-label="' +
      (ch ? 'Position in this exercise' : 'Position in the video') +
      '" aria-valuemin="0" aria-valuemax="' +
      Math.round(len) +
      '"><div class="cvsegs">' +
      sp.segs.map((w) => '<i style="flex:' + Math.max(1, w) + '"><b></b></i>').join('') +
      '</div><div class="cvthumb2" id="cvThumb"></div></div>' +
      '<div class="cvtimes"><span id="cvEl">0:00</span><span id="cvRem">−0:00</span></div>' +
      '<div class="cvtrans"><button class="circ cvskip" data-a="coachSkip" data-v="-10" aria-label="Back 10 seconds">' +
      B10 +
      '</button><button class="cvpp" id="cvPP" data-a="coachPlay" data-on="' +
      on +
      '" aria-label="' +
      (on ? 'Pause' : 'Play') +
      '">' +
      (on ? ICON.pause : ICON.play) +
      '</button><button class="circ cvskip" data-a="coachSkip" data-v="10" aria-label="Forward 10 seconds">' +
      F10 +
      '</button></div>' +
      '<div class="cvctl">' +
      (ch && a.lv === 3
        ? '<div class="seg cvlv" role="group" aria-label="Level"><span class="knob" aria-hidden="true"></span>' +
          [1, 2, 3]
            .map(
              (l) =>
                '<button data-a="coachLv" data-v="' +
                l +
                '" class="' +
                (a.l === l ? 'on' : '') +
                '" aria-pressed="' +
                (a.l === l) +
                '">L' +
                l +
                '</button>'
            )
            .join('') +
          '</div>'
        : '<span style="flex:1"></span>') +
      // Loop repeats the level you're on, or the whole exercise when its levels aren't known
      (ch
        ? '<button class="cvpill' +
          (prefs.loop ? ' on' : '') +
          '" data-a="coachLoop" aria-pressed="' +
          prefs.loop +
          '" aria-label="Loop this ' +
          (a.lv === 3 ? 'level' : 'exercise') +
          '">' +
          LOOP +
          '<span class="cvlt">Loop</span></button>'
        : '') +
      '<button class="cvpill" data-a="coachSpeed" aria-label="Speed ' +
      speedTxt() +
      '. Tap to change">' +
      speedTxt() +
      '</button></div></div>';
    if (ch)
      h +=
        '<div class="hdr">Exercises</div><div class="grp tiled">' +
        COACH_IDS.map((id) => {
          const e = exById(id),
            me = a && a.id === id;
          return (
            '<button class="row' +
            (me ? ' cvon' : '') +
            '" data-a="coachEx" data-k="' +
            id +
            '"' +
            (me ? ' aria-current="true"' : '') +
            '>' +
            tile(e) +
            '<span class="lbl">' +
            esc(e.name) +
            '</span>' +
            (me ? WAVE : '') +
            '</button>'
          );
        }).join('') +
        '</div>';
    return h;
  }
  // Settings › Coach video
  function settings() {
    let h = '<div class="hdr" id="cvset">Coach video</div><div class="grp">';
    if (busy) h += '<div class="row"><span class="lbl mut">Adding the coach video…</span></div>';
    else if (!has())
      h += '<button class="row" data-a="coachAdd"><span class="lbl acc">Add coach video…</span>' + chev + '</button>';
    else
      h +=
        '<div class="row cvrow">' +
        thumb() +
        '<span class="lbl">' +
        esc(meta.name) +
        '<small>' +
        (meta.chapters ? sumTxt() + ' · ' : 'No chapters · ') +
        mb(meta.size) +
        '</small></span></div>' +
        '<button class="row" data-a="coachAdd"><span class="lbl acc">Replace video…</span>' +
        chev +
        '</button>' +
        '<button class="row" data-a="sheet" data-v="coachDel"><span class="lbl dng">Remove video</span></button>';
    return (
      h +
      '</div><p class="foot">Stays on this ' +
      deviceName() +
      ' and isn’t included in backups. Keep the file in Files to add it again.</p>'
    );
  }
  const mb = (b) => (b / 1048576).toFixed(b >= 10 * 1048576 ? 0 : 1) + ' MB';
  // Settings › Storage
  const storageRow = () =>
    has()
      ? '<div class="row"><span class="lbl">Coach video</span><span class="mut">' + mb(meta.size) + '</span></div>'
      : '';

  /* ----- adding and removing ----- */
  function duration(blob) {
    return new Promise((res) => {
      const v = document.createElement('video'),
        u = URL.createObjectURL(blob);
      let done = false;
      const fin = (d) => {
        if (done) return;
        done = true;
        URL.revokeObjectURL(u);
        v.removeAttribute('src');
        try {
          v.load();
        } catch (e) {}
        res(d);
      };
      v.preload = 'metadata';
      v.muted = true;
      v.onloadedmetadata = () => {
        // some files only know their length after a seek to the end
        if (isFinite(v.duration) && v.duration > 0) fin(v.duration);
        else {
          v.ondurationchange = () => isFinite(v.duration) && v.duration > 0 && fin(v.duration);
          v.currentTime = 1e7;
        }
      };
      v.onerror = () => fin(0);
      setTimeout(() => fin(isFinite(v.duration) ? v.duration : 0), 15000);
      v.src = u;
    });
  }
  async function add(file) {
    if (!file || busy) return;
    if (file.type && !/^video\//.test(file.type)) return toast('That isn’t a video file');
    busy = true;
    if (U.tab === 'settings' && !U.view) rerender();
    const dur = await duration(file);
    if (!(dur > 0)) {
      busy = false;
      rerender();
      return toast('Couldn’t read that video');
    }
    const rec = {
      name: file.name || 'Coach video',
      size: file.size,
      type: file.type || 'video/mp4',
      dur,
      added: Date.now(),
      blob: file,
    };
    try {
      await ctx('readwrite', (s) => s.put(rec, 'v'));
    } catch (e) {
      busy = false;
      rerender();
      return toast('Couldn’t save the video. Storage may be full.');
    }
    const replaced = has();
    pause();
    meta = { name: rec.name, size: rec.size, type: rec.type, dur, chapters: chaptersFor(dur) };
    prefs.t = 0;
    savePrefs();
    cur = null;
    dismissed = true;
    setSrc(file);
    busy = false;
    rerender();
    toast(replaced ? 'Coach video replaced' : 'Coach video added');
  }
  async function remove() {
    try {
      await ctx('readwrite', (s) => s.delete('v'));
    } catch (e) {}
    pause();
    meta = null;
    cur = null;
    if (el) {
      park();
      el.removeAttribute('src');
      try {
        el.load();
      } catch (e) {}
    }
    if (url) URL.revokeObjectURL(url);
    url = null;
    prefs.t = 0;
    savePrefs();
    if (X && X.cv) {
      delete X.cv;
      saveDraft();
    }
    U.sheet = null;
    rerender();
    toast('Coach video removed');
  }
  // at launch (boot.js): the stored video, if there is one
  async function load() {
    try {
      const r = await ctx('readonly', (s) => s.get('v'));
      if (!okRec(r)) return;
      meta = { name: String(r.name || 'Coach video'), size: +r.size || r.blob.size, type: r.type, dur: +r.dur, chapters: chaptersFor(+r.dur) };
      setSrc(r.blob);
    } catch (e) {}
  }

  /* ----- doors ----- */
  // where the player's Back goes: the exercise page or the tab you came from
  const backHere = () =>
    U.view === 'ex' ? { view: 'ex', exId: U.exId, prevTab: U.prevTab, tab: U.tab } : { view: null, tab: U.tab };
  function open(id) {
    const b = U.view === 'coach' ? U.coachBack : backHere();
    go(() => {
      U.coachBack = b;
      U.view = 'coach';
      if (id) cue(id, level(id), true); // before the page is drawn, so it's drawn for this exercise
    });
  }
  function back() {
    const b = U.coachBack || { view: null, tab: 'exercises' };
    go(() => {
      U.coachBack = null;
      if (b.view === 'ex' && exById(b.exId)) {
        U.view = 'ex';
        U.exId = b.exId;
        U.prevTab = b.prevTab;
      } else U.view = null;
      U.tab = b.tab || 'exercises';
    });
  }
  function toSettings() {
    go(() => {
      U.coachBack = null;
      U.view = null;
      U.tab = 'settings';
    });
    const h = $('cvset');
    if (h) window.scrollTo(0, Math.max(0, h.getBoundingClientRect().top + window.scrollY - 110));
  }
  // a session step: tap to show, then cue this step's exercise at its level and play
  function show() {
    if (!X) return;
    X.cv = true;
    saveDraft();
    const id = stepEx(U.view);
    rerender();
    if (id) cue(id, level(id), true);
  }
  // ‹ › under the video in a step: the step's previous or next exercise, keeping play or pause as it was
  function stepMove(d) {
    const l = stepList(U.view);
    if (!l.length) return;
    const a = here(),
      i = a ? l.indexOf(a.id) : -1;
    const j = i < 0 ? (d > 0 ? 0 : l.length - 1) : (i + d + l.length) % l.length;
    cue(l[j], level(l[j]), !!(el && !el.paused));
  }
  // Next / Back between steps: cue the new step's exercise, paused; a step with nothing to show pauses the video
  function stepped(was) {
    if (!X || !X.cv || !chapters() || !isFlow(was) || !isFlow(U.view) || was === U.view) return;
    const id = stepEx(U.view);
    if (id) cue(id, level(id), false);
    else pause();
  }
  function fullscreen() {
    const v = video();
    try {
      if (v.webkitEnterFullscreen && !document.fullscreenEnabled) v.webkitEnterFullscreen();
      else if (v.requestFullscreen) v.requestFullscreen().catch(() => {});
      else if (v.webkitEnterFullscreen) v.webkitEnterFullscreen();
    } catch (e) {}
  }
  function setLevel(l) {
    const a = here();
    if (!a) return;
    if (a.lv === 3) seek(COACH_CH[a.n][l - 1]);
  }
  function toggleLoop() {
    prefs.loop = !prefs.loop;
    savePrefs();
    cur = here();
    const b = document.querySelector('#app [data-a=coachLoop]');
    if (b) {
      b.classList.toggle('on', prefs.loop);
      b.setAttribute('aria-pressed', prefs.loop);
    }
  }
  function cycleSpeed() {
    prefs.speed = COACH_SPEEDS[(COACH_SPEEDS.indexOf(prefs.speed) + 1) % COACH_SPEEDS.length];
    savePrefs();
    if (el) {
      el.playbackRate = prefs.speed;
      pitch();
    }
    const b = document.querySelector('#app [data-a=coachSpeed]');
    if (b) {
      b.textContent = speedTxt();
      b.setAttribute('aria-label', 'Speed ' + speedTxt() + '. Tap to change');
    }
  }

  /* ----- scrubbing: follows the finger at once, within the exercise ----- */
  function scrubAt(x) {
    const sc = $('cvScrub');
    if (!sc || !drag) return;
    // the same mapping the drawing uses: segment by segment, with the gaps between them
    const sp = span(),
      segs = [...sc.querySelectorAll('.cvsegs i')];
    let a = sp.s,
      t = sp.s;
    segs.forEach((g, j) => {
      const r = g.getBoundingClientRect(),
        w = sp.segs[j] || 0;
      if (x >= r.left) t = a + Math.max(0, Math.min(1, (x - r.left) / Math.max(1, r.width))) * w;
      a += w;
    });
    drag.t = Math.max(drag.s, Math.min(drag.e, t));
    paint();
    if (el) {
      seekBy = Date.now();
      if (el.fastSeek && !el.paused) el.fastSeek(drag.t);
      else el.currentTime = drag.t;
    }
  }
  document.addEventListener('pointerdown', (e) => {
    const sc = e.target.closest && e.target.closest('#cvScrub');
    if (!sc || !has() || e.button > 0) return;
    const sp = span();
    drag = { id: e.pointerId, s: sp.s, e: sp.e - 0.2, t: now() };
    try {
      sc.setPointerCapture(e.pointerId);
    } catch (x) {}
    sc.classList.add('drag');
    scrubAt(e.clientX);
  });
  document.addEventListener('pointermove', (e) => {
    if (drag && e.pointerId === drag.id) scrubAt(e.clientX);
  });
  const endDrag = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const t = drag.t;
    drag = null;
    const sc = $('cvScrub');
    if (sc) sc.classList.remove('drag');
    if (el) el.currentTime = t;
    cur = chapters() ? at(t) : null;
    keep(true);
    paint();
  };
  document.addEventListener('pointerup', endDrag);
  document.addEventListener('pointercancel', endDrag);
  document.addEventListener('keydown', (e) => {
    if (!(e.target && e.target.id === 'cvScrub')) return;
    if (e.key === 'ArrowLeft') skip(-5);
    else if (e.key === 'ArrowRight') skip(5);
    else return;
    e.preventDefault();
  });
  $('coachIn').addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0];
    e.target.value = '';
    if (f) add(f);
  });

  /* ----- the floating window (window.js): coach video, between a playing take and a session ----- */
  const fwKind = {
    id: 'video',
    active: () => !!(has() && el && woke && !dismissed && !el.ended && (!el.paused || el.currentTime > 0.5)),
    own: () => U.view === 'coach' || !!document.querySelector('#app .cv-slot'),
    info() {
      const a = here(),
        on = !el.paused;
      return {
        k: a ? (COACH_SHORT[a.id] || exName(a.id)) + lvTxt(a, true) : 'Coach video',
        t: fmt(now()),
        p: Math.min(1, now() / Math.max(1, end())),
        on,
        open: where && isFlow(where.view) && X ? 'Back to ' + VIEWS[where.view][0] : 'Back to the coach video',
        label: 'Coach video ' + (on ? 'playing' : 'paused'),
      };
    },
    toggle: () => toggle(),
    open() {
      if (where && isFlow(where.view) && X && X.cv) {
        const v = where.view,
          y = where.y || 0;
        fwGo(() => {
          U.view = v;
          U.sheet = null;
          U.sd = {};
        }, y);
        return;
      }
      const b = where && where.back ? where.back : backHere();
      fwGo(() => {
        U.coachBack = b;
        U.view = 'coach';
        U.sheet = null;
        U.sd = {};
      }, where && where.view === 'coach' ? where.y : 0);
    },
    draw(fw, i) {
      const b = 'video|' + i.on;
      if (FW.build !== b) {
        FW.build = b;
        fw.innerHTML =
          '<div class="fwopen fwvopen" data-a="fwOpen" role="button" tabindex="0"><span class="cv-fw"></span></div>' +
          '<div class="fwvb"><span class="fwk"></span><button class="fwbtn" data-a="fwToggle" aria-label="' +
          (i.on ? 'Pause' : 'Play') +
          '">' +
          (i.on ? ICON.pause : ICON.play) +
          '</button></div>' +
          '<button class="fwx" data-a="coachX" aria-label="Close the coach video">' +
          ICON.x +
          '</button><span class="fwvp" aria-hidden="true"><i></i></span>';
      }
      fw.classList.toggle('paused', !i.on);
      fw.querySelector('.fwopen').setAttribute('aria-label', i.open + '. ' + i.k + ', ' + i.t);
      fw.querySelector('.fwk').textContent = i.k;
      const p = fw.querySelector('.fwvp i');
      if (p) p.style.width = (i.p * 100).toFixed(1) + '%';
    },
  };
  FW_KINDS.splice(1, 0, fwKind); // take → video → session
  function dismiss() {
    dismissed = true;
    pause();
    keep(true);
    fwUpdate();
  }

  return {
    load,
    add,
    remove,
    has,
    chapters,
    at,
    level,
    cue,
    play,
    pause,
    toggle,
    seek,
    skip,
    park,
    place,
    open,
    back,
    toSettings,
    show,
    stepMove,
    stepped,
    stepList,
    stepEx,
    fullscreen,
    setLevel,
    toggleLoop,
    cycleSpeed,
    dismiss,
    page,
    exercisesRow,
    exerciseRow,
    stepHTML,
    settings,
    storageRow,
    busy: () => busy,
    el: () => el,
    prefs: () => Object.assign({}, prefs),
    meta: () => (meta ? Object.assign({}, meta) : null),
    where: () => (where ? Object.assign({}, where) : null),
    here,
  };
})();
