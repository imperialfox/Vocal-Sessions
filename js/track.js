/* Vocal Sessions · track.js
   The track player (3.19, Track 1): a practice player for a song's real track. Import the song's audio from Files,
   see its waveform, scrub it, zoom it, and loop a phrase slowly with the pitch kept. Built for drilling runs.
   The audio stays on the device in its own IndexedDB database (vocalTracks), never in backups. The song record only
   keeps the track's name and length (sg.track) and the last loop (sg.loop), so both survive a restore without it.
   The waveform is decoded once, at import, into peaks (50 a second) stored beside the audio; opening the player never
   decodes again. One <audio> plays the open track: playbackRate for speed with preservesPitch, and the loop is
   checked every animation frame while playing.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Track player: the numbers ===== */
const TRK_LEVELS = [
  { id: 'phrase', name: 'Phrase', win: 6 }, // a scrolling strip, 6 s on screen
  { id: 'line', name: 'Line', win: 16 }, // a scrolling strip, 16 s on screen
  { id: 'section', name: 'Section', row: 20 }, // rows of 20 s, the whole song
  { id: 'song', name: 'Song', row: 30 }, // rows of 30 s, the whole song
];
const TRK_SPEEDS = [1, 0.75, 0.5];
const TRK_RATE = 50; // waveform peaks a second
const TRK_SR = 8000; // the sample rate the waveform is read at (mono-ish, small: a 4-minute song isn't ~85 MB of floats)
const TRK_MIN = 0.5; // the shortest loop, in seconds
const TRK_HEAD = 0.4; // the strip's playhead sits 40% from the left
const TRK_JOG = 300; // the jog wheel: a drag of 300 px moves one window's worth
const TRK_BIG = 60 * 1048576; // over this, ask once before importing
const TRK_PINCH = 40; // px of pinch for each zoom level
const TRK_BAD = 'That file can’t be opened. Try an MP3 or M4A from Files.';
const TRK_LENGTH = 'This track is a different length, so timings may be off';

/* ===== Track player: checking a saved loop (used by cleanSong in songs.js) =====
   sg.loop = {start, end, on}: seconds, end after start by at least TRK_MIN, end clamped to the track's length. */
function cleanLoop(l, dur) {
  if (!l || typeof l !== 'object' || Array.isArray(l)) return null;
  const num = (x) => typeof x === 'number' && isFinite(x) && x >= 0;
  if (!num(l.start) || !num(l.end)) return null;
  let s = l.start,
    e = l.end;
  if (dur > 0 && e > dur) e = dur;
  if (e - s < TRK_MIN - 1e-6) return null;
  return { start: Math.round(s * 100) / 100, end: Math.round(e * 100) / 100, on: l.on === true };
}

const TRACK = (() => {
  const have = new Map(); // song id → {name, size, type, dur, added}: tracks on this device
  let cur = null; // the track in the <audio>: {id, peaks, rate, dur, url}
  let el = null; // the one <audio>
  let loading = null;
  let busy = null; // importing: {id}
  let want = null; // where the file picked next goes: {id} or {fresh: true}
  let big = null; // a large file waiting for its OK: {file, want}
  let woke = false; // played since opening it, and not paused on its own screen (the floating window)
  let prevT = 0; // where the last frame was, so the loop wraps only when playback crosses its end
  let pend = null; // a time to go to once the audio knows its length
  let raf = 0;
  let drag = null; // a finger on the strip: {kind: 'scrub'|'handle'|'jog', …}
  let lastTap = null;
  let pinch = null;
  let wheelAcc = 0;
  let C = null; // colours, read from the CSS tokens
  const pos = {}; // where each track was left, this time the app is open

  /* ----- this device's settings: zoom level and speed (vocalSongPrefs, never backed up) ----- */
  function prefs() {
    const p = sgp();
    if (!(Number.isInteger(p.trkLevel) && p.trkLevel >= 0 && p.trkLevel < TRK_LEVELS.length)) p.trkLevel = 1;
    if (!TRK_SPEEDS.includes(p.trkSpeed)) p.trkSpeed = 1;
    return p;
  }
  const lv = () => prefs().trkLevel;
  const speed = () => prefs().trkSpeed;
  const strip = () => !!TRK_LEVELS[lv()].win;

  /* ----- stored on the device: its own database, apart from recordings, the coach video and backups ----- */
  let dbp = null;
  function tdb() {
    if (dbp) return dbp;
    dbp = new Promise((res, rej) => {
      if (!window.indexedDB) return rej(new Error('no idb'));
      const r = indexedDB.open('vocalTracks', 1);
      r.onupgradeneeded = () => {
        const d = r.result;
        // the audio as imported, and its waveform peaks, as separate entries keyed by song id
        if (!d.objectStoreNames.contains('audio')) d.createObjectStore('audio');
        if (!d.objectStoreNames.contains('peaks')) d.createObjectStore('peaks');
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
  async function tx(stores, mode, fn) {
    const d = await tdb();
    return new Promise((res, rej) => {
      const t = d.transaction(stores, mode);
      const out = fn(...stores.map((s) => t.objectStore(s)));
      t.oncomplete = () => res(out && out.result !== undefined ? out.result : undefined);
      t.onerror = () => rej(t.error);
      t.onabort = () => rej(t.error);
    });
  }
  const okAudio = (r) => r && r.blob instanceof Blob && r.blob.size > 0 && +r.dur > 0;
  const okPeaks = (r) => r && r.p instanceof Uint8Array && r.p.length > 0 && +r.rate > 0;
  const metaOf = (r) => ({
    name: String(r.name || 'Track'),
    size: +r.size || r.blob.size,
    type: r.type || '',
    dur: +r.dur,
    added: +r.added || 0,
  });

  // at launch (boot.js): which songs have a track on this device. Blobs come back as handles, not their bytes
  async function load() {
    try {
      const d = await tdb();
      await new Promise((res) => {
        const t = d.transaction('audio', 'readonly'),
          c = t.objectStore('audio').openCursor();
        c.onsuccess = () => {
          const k = c.result;
          if (!k) return;
          if (typeof k.key === 'string' && okAudio(k.value)) have.set(k.key, metaOf(k.value));
          k.continue();
        };
        t.oncomplete = res;
        t.onerror = res;
        t.onabort = res;
      });
    } catch (e) {}
  }

  /* ----- reading a file: decoded once, at import, into peaks ----- */
  function decode(buf) {
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!OAC) return Promise.reject(new Error('no audio'));
    let ctx = null;
    // decodeAudioData resamples to the context's rate; older Safari may refuse a low one
    for (const r of [TRK_SR, 22050, 44100])
      try {
        ctx = new OAC(1, 1, r);
        break;
      } catch (e) {}
    if (!ctx) return Promise.reject(new Error('no audio'));
    return new Promise((res, rej) => {
      try {
        const p = ctx.decodeAudioData(buf, res, rej); // callbacks for older Safari, a promise elsewhere
        if (p && p.then) p.then(res, rej);
      } catch (e) {
        rej(e);
      }
    });
  }
  async function analyse(buf) {
    const ab = await decode(buf);
    if (!ab || !(ab.duration > 0) || !ab.length) throw new Error('empty');
    const per = ab.sampleRate / TRK_RATE,
      n = Math.max(1, Math.ceil(ab.length / per)),
      raw = new Float32Array(n);
    for (let c = 0; c < ab.numberOfChannels; c++) {
      const d = ab.getChannelData(c);
      for (let i = 0; i < n; i++) {
        const a = Math.floor(i * per),
          b = Math.min(d.length, Math.floor((i + 1) * per));
        let m = raw[i];
        for (let j = a; j < b; j++) {
          const v = d[j] < 0 ? -d[j] : d[j];
          if (v > m) m = v;
        }
        raw[i] = m;
      }
    }
    let top = 0;
    for (let i = 0; i < n; i++) if (raw[i] > top) top = raw[i];
    const p = new Uint8Array(n);
    if (top > 0) for (let i = 0; i < n; i++) p[i] = Math.round((255 * raw[i]) / top);
    return { dur: ab.duration, peaks: p };
  }

  /* ----- the audio element ----- */
  function pitch() {
    if (!el) return;
    el.preservesPitch = true;
    el.webkitPreservesPitch = true;
    el.mozPreservesPitch = true;
  }
  function audio() {
    if (el) return el;
    el = new Audio();
    el.preload = 'auto';
    el.setAttribute('playsinline', '');
    pitch();
    el.addEventListener('loadedmetadata', () => {
      if (pend != null) {
        const t = pend;
        pend = null;
        try {
          el.currentTime = Math.min(t, Math.max(0, len() - 0.05));
        } catch (e) {}
        prevT = el.currentTime;
      }
      el.playbackRate = speed();
      pitch();
      paint();
      draw();
    });
    el.addEventListener('play', () => {
      woke = true;
      media();
      frames();
      changed();
    });
    el.addEventListener('pause', () => {
      if (cur) pos[cur.id] = el.currentTime;
      // paused on its own screen: you meant to stop, so no window follows you out
      if (here()) woke = false;
      changed();
    });
    el.addEventListener('ended', () => {
      const L = loopNow();
      if (L && L.on && L.end >= len() - 0.1) {
        seek(L.start);
        el.play().catch(() => {});
        return;
      }
      changed();
    });
    el.addEventListener('seeked', () => {
      paint();
      if (!playing()) draw();
    });
    return el;
  }
  // the lock screen's buttons control the track while it plays (the coach video takes them back when it plays)
  function media() {
    if (!('mediaSession' in navigator)) return;
    const ms = navigator.mediaSession,
      on = (a, f) => {
        try {
          ms.setActionHandler(a, f);
        } catch (e) {}
      };
    on('play', () => play());
    on('pause', () => pause());
    on('seekbackward', (d) => seek(now() - ((d && d.seekOffset) || 5)));
    on('seekforward', (d) => seek(now() + ((d && d.seekOffset) || 5)));
    on('seekto', (d) => d && isFinite(d.seekTime) && seek(d.seekTime));
    const sg = cur && songById(cur.id);
    try {
      if (window.MediaMetadata)
        ms.metadata = new MediaMetadata({ title: sg ? songTitle(sg) : 'Track', artist: 'Track', album: 'Vocal Sessions' });
    } catch (e) {}
  }
  const playing = () => !!(el && cur && !el.paused);
  const len = () => (cur ? cur.dur : 0) || (el && isFinite(el.duration) ? el.duration : 0);
  const now = () =>
    cur ? (el && el.readyState >= 1 && pend == null ? el.currentTime : pend != null ? pend : pos[cur.id] || 0) : 0;
  // the player page for the open track is on screen
  const here = () => U.view === 'trk' && !!cur && U.songId === cur.id;
  const song = () => (cur ? songById(cur.id) : null);
  const loopNow = () => {
    const sg = song();
    return sg && sg.loop && sg.loop.end > sg.loop.start ? sg.loop : null;
  };

  // load a song's track into the player (from IndexedDB; the peaks were saved at import)
  async function open1(id) {
    if (loading === id || (cur && cur.id === id)) return;
    loading = id;
    let a = null,
      p = null;
    try {
      a = await tx(['audio'], 'readonly', (s) => s.get(id));
      p = await tx(['peaks'], 'readonly', (s) => s.get(id));
    } catch (e) {}
    if (loading !== id) return;
    loading = null;
    if (!okAudio(a)) {
      have.delete(id);
      return rerender();
    }
    if (!okPeaks(p)) {
      // the peaks went missing: read the audio once more and keep them this time
      try {
        const r = await analyse(await a.blob.arrayBuffer());
        p = { p: r.peaks, rate: TRK_RATE, dur: r.dur };
        await tx(['peaks'], 'readwrite', (s) => s.put(p, id));
      } catch (e) {
        p = { p: new Uint8Array(0), rate: TRK_RATE, dur: +a.dur };
      }
    }
    unload();
    cur = { id, peaks: p.p, rate: +p.rate, dur: +a.dur, url: URL.createObjectURL(a.blob) };
    const v = audio();
    pend = pos[id] || 0;
    prevT = pend;
    v.src = cur.url;
    v.playbackRate = speed();
    pitch();
    if (U.view === 'trk' && U.songId === id) rerender();
  }
  function unload() {
    if (!cur) return;
    if (el) {
      pos[cur.id] = now();
      el.pause();
      el.removeAttribute('src');
      try {
        el.load();
      } catch (e) {}
    }
    URL.revokeObjectURL(cur.url);
    cur = null;
    pend = null;
    woke = false;
    cancelAnimationFrame(raf);
    raf = 0;
  }

  /* ----- playing ----- */
  // one sound at a time: the coach video, a take and Song Clock's play-along stop when the track plays
  function quiet() {
    if (typeof COACH !== 'undefined') COACH.pause();
    if (typeof player !== 'undefined' && player) {
      stopPlayback();
      if (U.view !== 'trk') rerender();
    }
    if (typeof CK !== 'undefined' && CK.pc.run) ckPause();
  }
  function play() {
    if (!cur) return;
    const v = audio();
    quiet();
    // with the loop on, play starts in the loop
    const L = loopNow(),
      t = now();
    if (L && L.on && (t < L.start - 0.01 || t >= L.end - 0.01)) seek(L.start);
    v.playbackRate = speed();
    pitch();
    v.play().catch(() => {
      toast('Couldn’t play the track');
      changed();
    });
  }
  function pause() {
    if (el && !el.paused) el.pause();
  }
  const toggle = () => (playing() ? pause() : play());
  function seek(t) {
    if (!cur) return;
    t = Math.max(0, Math.min(Math.max(0, len() - 0.02), +t || 0));
    pos[cur.id] = t;
    prevT = t;
    if (el && el.readyState >= 1 && pend == null) {
      try {
        el.currentTime = t;
      } catch (e) {}
    } else pend = t;
    draw();
    paint();
  }
  // every frame while playing: the loop, the waveform and the time
  function frame() {
    if (!cur || !el) return;
    const L = loopNow();
    let t = el.currentTime;
    if (L && L.on && !(drag && drag.kind !== 'handle') && prevT < L.end && t >= L.end - 0.005) {
      el.currentTime = L.start;
      t = L.start;
    }
    prevT = t;
    pos[cur.id] = t;
    draw();
    paint();
    if (FW.shown === 'track') fwTick();
  }
  function frames() {
    cancelAnimationFrame(raf);
    const f = () => {
      raf = 0;
      if (!playing()) return;
      frame();
      raf = requestAnimationFrame(f);
    };
    raf = requestAnimationFrame(f);
  }
  function changed() {
    paint();
    draw();
    fwUpdate();
  }

  /* ----- the loop ----- */
  const r2 = (x) => Math.round(x * 100) / 100;
  function setLoop(s, e, on) {
    const sg = song();
    if (!sg) return;
    const d = len();
    s = Math.max(0, Math.min(d, s));
    e = Math.max(0, Math.min(d, e));
    if (e - s < TRK_MIN) return false;
    sg.loop = { start: r2(s), end: r2(e), on: on !== false };
    return true;
  }
  // Set start / Set end at the playhead (FCP's In and Out): a start with no end runs to the song's end; an end with no
  // start runs from its beginning; a start after the end (or an end before the start) starts a fresh range
  function setAt(which) {
    const sg = song();
    if (!sg) return;
    const t = now(),
      d = len(),
      L = loopNow();
    let s = L ? L.start : 0,
      e = L ? L.end : d;
    if (which === 'start') {
      s = t;
      if (!L || e - s < TRK_MIN) e = d;
      if (e - s < TRK_MIN) s = Math.max(0, e - TRK_MIN);
    } else {
      e = t;
      if (!L || e - s < TRK_MIN) s = 0;
      if (e - s < TRK_MIN) e = Math.min(d, s + TRK_MIN);
    }
    if (setLoop(s, e, true)) {
      save();
      prevT = now();
      draw();
      paint();
    }
  }
  function toggleLoop() {
    const sg = song(),
      L = loopNow();
    if (!sg) return;
    if (!L) return toast('Set a start and end to loop a phrase');
    L.on = !L.on;
    save();
    prevT = now();
    paint();
    draw();
  }
  function clearLoop() {
    const sg = song();
    if (!sg || !sg.loop) return;
    delete sg.loop;
    save();
    paint();
    draw();
    toast('Loop cleared');
  }
  function toStart() {
    const L = loopNow();
    seek(L ? L.start : 0);
  }
  // dragging a handle: past the other one, they swap; never closer than TRK_MIN
  function dragHandle(v) {
    const L = loopNow(),
      d = len();
    if (!L || !drag) return;
    v = Math.max(0, Math.min(d, v));
    const o = drag.which === 'start' ? L.end : L.start;
    if (drag.which === 'start' ? v > o : v < o) drag.which = drag.which === 'start' ? 'end' : 'start';
    let a = drag.which === 'start' ? Math.min(v, o - TRK_MIN) : Math.max(v, o + TRK_MIN),
      b = o;
    if (a < 0) {
      a = 0;
      b = Math.max(b, TRK_MIN);
    }
    if (a > d) {
      a = d;
      b = Math.min(b, d - TRK_MIN);
    }
    L.start = r2(drag.which === 'start' ? a : b);
    L.end = r2(drag.which === 'start' ? b : a);
    draw();
  }

  /* ----- speed and zoom ----- */
  const spTxt = (s) => String(s) + '×';
  function cycleSpeed() {
    const p = prefs();
    p.trkSpeed = TRK_SPEEDS[(TRK_SPEEDS.indexOf(p.trkSpeed) + 1) % TRK_SPEEDS.length];
    saveSGP();
    if (el) {
      el.playbackRate = p.trkSpeed;
      pitch();
    }
    const b = $('trkSpd');
    if (b) {
      b.textContent = spTxt(p.trkSpeed);
      b.setAttribute('aria-label', 'Speed ' + spTxt(p.trkSpeed) + '. Tap to change');
    }
  }
  function setLevel(i, anim) {
    i = Math.max(0, Math.min(TRK_LEVELS.length - 1, i));
    const was = lv();
    if (i === was) return;
    prefs().trkLevel = i;
    saveSGP();
    const box = $('trkWave');
    if (!box) return;
    const b = document.querySelector('#app .trklv button[data-v="' + i + '"]');
    if (b) segPick(b);
    box.innerHTML = waveHTML();
    const h = $('trkHint');
    if (h) h.textContent = hint();
    draw();
    paint();
    // eases on gentle (Reduce Motion: a short fade; motion off: a jump). Never while playing: stillness while singing
    if (anim === false || playing()) return;
    const A = TRK_LEVELS[was],
      B = TRK_LEVELS[i];
    if (A.win && B.win) {
      const c = $('trkC');
      if (c)
        MOTION.animate(c, [{ transform: 'scaleX(' + (B.win / A.win).toFixed(3) + ')' }, { transform: 'none' }], {
          spring: 'gentle',
          fade: true,
        });
    } else
      MOTION.animate(box, [{ opacity: 0, transform: 'scale(0.98)' }, { opacity: 1, transform: 'none' }], {
        spring: 'gentle',
        fade: true,
      });
  }

  /* ----- drawing ----- */
  const fmt = (s) => {
    s = Math.max(0, Math.floor(s || 0));
    return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  };
  const fmt1 = (s) => {
    s = Math.max(0, s || 0);
    const t = Math.floor(s * 10) / 10,
      m = Math.floor(t / 60),
      x = t - m * 60;
    return m + ':' + (x < 10 ? '0' : '') + x.toFixed(1);
  };
  function colours() {
    const cs = getComputedStyle(document.documentElement),
      g = (k, d) => cs.getPropertyValue(k).trim() || d;
    C = { fg: g('--fg', '#000'), dim: g('--trk-dim', '#bbb'), loop: g('--trk-loop', '#ff9500'), head: g('--trk-head', '#d65a00') };
  }
  function fit(c) {
    const r = c.getBoundingClientRect(),
      dpr = window.devicePixelRatio || 1,
      w = Math.max(1, Math.round(r.width * dpr)),
      h = Math.max(1, Math.round(r.height * dpr));
    if (c.width !== w || c.height !== h) {
      c.width = w;
      c.height = h;
    }
    const g = c.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, r.width, r.height);
    return { g, w: r.width, h: r.height };
  }
  // the loudest peak between two times, 0–1
  function peak(a, b) {
    const P = cur && cur.peaks;
    if (!P || !P.length) return 0;
    const i0 = Math.max(0, Math.floor(a * cur.rate)),
      i1 = Math.min(P.length, Math.max(i0 + 1, Math.ceil(b * cur.rate)));
    let m = 0;
    for (let i = i0; i < i1; i++) if (P[i] > m) m = P[i];
    return m / 255;
  }
  function rr(g, x, y, w, h, r) {
    g.beginPath();
    if (g.roundRect) g.roundRect(x, y, w, h, r);
    else g.rect(x, y, w, h);
    g.fill();
  }
  // bars from t0 to t1, with step px between bar starts; x(t) places a time
  function bars(g, t0, t1, step, bw, pps, x0, mid, amp, L) {
    const bt = step / pps,
      d = len();
    for (let k = Math.max(0, Math.floor(t0 / bt) - 1); ; k++) {
      const s = k * bt;
      if (s >= Math.min(t1, d)) break;
      const x = x0 + s * pps;
      const v = peak(s, s + bt),
        h = Math.max(1.5, v * amp * 2),
        m = s + bt / 2;
      g.fillStyle = !L || (m >= L.start && m < L.end) ? C.fg : C.dim;
      g.fillRect(x, mid - h / 2, bw, h);
    }
  }
  function draw() {
    if (U.view !== 'trk' || !cur || U.songId !== cur.id) return;
    if (!C) colours();
    const L = loopNow(),
      t = now();
    const c = $('trkC');
    if (c) {
      const { g, w, h } = fit(c),
        win = TRK_LEVELS[lv()].win || 16,
        pps = w / win,
        hx = w * TRK_HEAD,
        x0 = hx - t * pps; // where 0:00 is
      bars(g, t - hx / pps, t + (w - hx) / pps + 0.1, 4, 3, pps, x0, h / 2 - 3, h / 2 - 15, L);
      if (L)
        [L.start, L.end].forEach((v) => {
          const x = x0 + v * pps;
          if (x < -20 || x > w + 20) return;
          g.fillStyle = C.loop;
          g.fillRect(x - 1.5, 0, 3, h);
          rr(g, x - 6.5, h - 17, 13, 17, 4);
        });
      // the playhead: the darker orange, with a small dot above
      g.fillStyle = C.head;
      g.fillRect(hx - 1, 8, 2, h - 8);
      g.beginPath();
      g.arc(hx, 5, 4, 0, Math.PI * 2);
      g.fill();
      const s = $('trkStrip');
      if (s) s.setAttribute('aria-valuetext', fmt(t) + ' of ' + fmt(len()));
      return;
    }
    const rs = TRK_LEVELS[lv()].row;
    document.querySelectorAll('#app .trkrow canvas').forEach((cv) => {
      const r = +cv.parentNode.dataset.r,
        a = r * rs,
        b = a + rs,
        { g, w, h } = fit(cv),
        pps = w / rs,
        x0 = -a * pps;
      bars(g, a, b, 3, 2, pps, x0, h / 2, h / 2 - 3, L);
      if (L)
        [L.start, L.end].forEach((v) => {
          if (v < a || v > b) return;
          const x = x0 + v * pps;
          g.fillStyle = C.loop;
          g.fillRect(x - 1, 0, 2, h);
          rr(g, x - 4.5, h - 9, 9, 9, 3);
        });
      if (t >= a && (t < b || (b >= len() && t <= b))) {
        g.fillStyle = C.head;
        g.fillRect(x0 + t * pps - 1, 0, 2, h);
      }
    });
  }
  // text and buttons, in place (no redraw while playing)
  function paint() {
    const tt = $('trkT');
    if (tt && cur) {
      const v = fmt1(now());
      if (tt.textContent !== v) tt.textContent = v;
    }
    const pp = $('trkPP');
    if (pp) {
      const on = playing();
      if (pp.dataset.on !== String(on)) {
        pp.dataset.on = String(on);
        pp.innerHTML = on ? ICON.pause : ICON.play;
        pp.setAttribute('aria-label', on ? 'Pause' : 'Play');
      }
    }
    const lb = $('trkLoopB');
    if (lb) {
      const L = loopNow(),
        on = !!(L && L.on);
      lb.classList.toggle('on', on);
      lb.setAttribute('aria-pressed', on);
      lb.setAttribute('aria-label', L ? 'Loop ' + fmt1(L.start) + ' to ' + fmt1(L.end) : 'Loop (set a start and end first)');
    }
  }

  /* ----- screens ----- */
  const WAVE =
    '<svg class="i" viewBox="0 0 24 24"><path d="M3 12h1.5M6.5 8v8M10 5v14M13.5 9v6M17 6.5v11M20.5 10.5v3"/></svg>';
  const TILE =
    '<span class="tile trktile">' + GL('<path d="M3.5 12h1M7 8.5v7M10.5 5v14M14 9v6M17.5 6.5v11M21 10.5v3"/>') + '</span>';
  const TOSTART = '<svg class="i" viewBox="0 0 24 24"><path d="M6 5v14"/><path d="M19 5v14L9 12z" fill="currentColor" stroke="none"/></svg>';
  const LOOP =
    '<svg class="i" viewBox="0 0 24 24"><path d="M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4"/></svg>';
  const JOG = '<svg class="trkjogi" viewBox="0 0 12 20" aria-hidden="true"><path d="M2 7l4-4 4 4M2 13l4 4 4-4"/></svg>';
  const hint = () => (strip() ? 'Drag the jog wheel · double-tap outside the loop to clear' : 'Tap a row to zoom in there');
  const mb = (b) => (b / 1048576).toFixed(b >= 10 * 1048576 ? 0 : 1) + ' MB';

  function waveHTML() {
    if (strip())
      return (
        '<div class="trkstrip" id="trkStrip" data-own-gesture role="slider" tabindex="0" aria-label="Track position" aria-valuetext="' +
        fmt(now()) +
        '"><canvas id="trkC" aria-hidden="true"></canvas><div class="trkjog" id="trkJog" data-own-gesture aria-hidden="true"><span class="trkjogr"></span>' +
        JOG +
        '</div></div>'
      );
    const rs = TRK_LEVELS[lv()].row,
      n = Math.max(1, Math.ceil(len() / rs - 1e-6));
    let h = '<div class="trkrows" id="trkRows" data-own-gesture>';
    for (let r = 0; r < n; r++)
      h +=
        '<button class="trkrow" data-a="trkRow" data-r="' +
        r +
        '" aria-label="' +
        fmt(r * rs) +
        ' to ' +
        fmt(Math.min(len(), (r + 1) * rs)) +
        '. Zoom in here"><span class="trkg">' +
        fmt(r * rs) +
        '</span><canvas aria-hidden="true"></canvas></button>';
    return h + '</div>';
  }
  function emptyHTML(sg) {
    const miss = !!sg.track;
    return (
      '<div class="sgempty trkempty">' +
      WAVE +
      '<b>' +
      (miss ? 'Track not on this device' : 'No track yet') +
      '</b>' +
      (miss
        ? 'The loop and timings are kept with the song. Add the same file again from Files to line them up.'
        : 'Add the song’s audio from Files to loop a phrase and slow it down, with the pitch kept.') +
      '<div style="margin-top:18px"><button class="cta ink" data-a="trkAdd" data-k="' +
      sg.id +
      '" style="max-width:260px;margin:0 auto">Add track</button></div></div>'
    );
  }
  function page() {
    const sg = songById(U.songId);
    if (!sg) return '<div class="sgempty"><b>This song was deleted.</b></div>';
    if (busy && busy.id === sg.id)
      return '<div class="sgempty trkempty">' + WAVE + '<b>Reading the track…</b>This takes a moment.</div>';
    if (!have.has(sg.id)) return emptyHTML(sg);
    if (!cur || cur.id !== sg.id) return '<div class="trk trkload" aria-busy="true"></div>';
    const m = have.get(sg.id);
    return (
      '<div class="trk">' +
      '<div class="seg wide trklv" role="group" aria-label="Zoom"><span class="knob" aria-hidden="true"></span>' +
      TRK_LEVELS.map(
        (l, i) =>
          '<button data-a="trkLevel" data-v="' +
          i +
          '" class="' +
          (lv() === i ? 'on' : '') +
          '" aria-pressed="' +
          (lv() === i) +
          '">' +
          l.name +
          '</button>'
      ).join('') +
      '</div><div class="trkwave" id="trkWave">' +
      waveHTML() +
      '</div><div class="trkinfo"><span class="trkt" id="trkT">' +
      fmt1(now()) +
      '</span><span class="trkhint" id="trkHint">' +
      hint() +
      '</span></div><div class="trkchips"><button class="cvpill" data-a="trkSet" data-v="start">Set start</button><button class="cvpill" data-a="trkSet" data-v="end">Set end</button><span class="sp"></span><button class="cvpill" id="trkSpd" data-a="trkSpeed" aria-label="Speed ' +
      spTxt(speed()) +
      '. Tap to change">' +
      spTxt(speed()) +
      '</button></div><p class="foot trkfoot">' +
      esc(m.name) +
      ' · ' +
      fmt(m.dur) +
      ' · kept on this ' +
      deviceName() +
      ', not in backups</p></div>'
    );
  }
  function bar() {
    const sg = songById(U.songId);
    return {
      l: '<button class="circ glass" data-a="trkBack" aria-label="Back">' + ICON.back + '</button>',
      t: sg ? esc(songTitle(sg)) : 'Track',
      r:
        sg && have.has(sg.id) && !(busy && busy.id === sg.id)
          ? '<button class="circ glass" data-a="trkMenu" aria-label="Track settings">' + SGI.more + '</button>'
          : '',
    };
  }
  // the transport, in the dock: back to the loop start, play, loop
  function dock() {
    if (U.view !== 'trk' || !cur || U.songId !== cur.id || U.sheet) return '';
    const on = playing(),
      L = loopNow();
    return (
      '<div class="trktr glass" role="group" aria-label="Track player"><button class="trkb" data-a="trkToStart" aria-label="Back to the loop start">' +
      TOSTART +
      '</button><button class="trkpp" id="trkPP" data-a="trkPP" data-on="' +
      on +
      '" aria-label="' +
      (on ? 'Pause' : 'Play') +
      '">' +
      (on ? ICON.pause : ICON.play) +
      '</button><button class="trkb trkloopb' +
      (L && L.on ? ' on' : '') +
      '" id="trkLoopB" data-a="trkLoop" aria-pressed="' +
      !!(L && L.on) +
      '" aria-label="Loop">' +
      LOOP +
      '</button></div>'
    );
  }
  // the song page's Practice group: a door into the player, or a way to add the track
  function row(sg) {
    const on = have.has(sg.id),
      miss = !on && !!sg.track,
      wait = busy && busy.id === sg.id;
    if (on && !wait) {
      const m = have.get(sg.id),
        L = sg.loop;
      return (
        '<button class="row" data-zk="trk:' +
        sg.id +
        '" data-a="trkOpen" data-k="' +
        sg.id +
        '">' +
        TILE +
        '<span class="lbl">Track<small>' +
        fmt(m.dur) +
        (L ? ' · loop ' + fmt(L.start) + '–' + fmt(L.end) : ' · loop a phrase, slow it down') +
        '</small></span>' +
        chev +
        '</button>'
      );
    }
    return (
      '<button class="row" data-a="trkAdd" data-k="' +
      sg.id +
      '"' +
      (wait ? ' aria-busy="true"' : '') +
      '>' +
      TILE +
      '<span class="lbl">' +
      (wait ? 'Reading the track…' : miss ? 'Track not on this device' : 'Add track') +
      '<small>' +
      (miss ? 'The loop and timings are kept with the song' : 'From Files: loop a phrase and slow it down') +
      '</small></span>' +
      (miss && !wait ? '<span class="acc trkadd">Add track</span>' : chev) +
      '</button>'
    );
  }
  function sheet(s) {
    const sg = songById(U.songId),
      m = sg && have.get(sg.id);
    if (s === 'trkMenu' && sg && m)
      return sheetWrap(
        'Track',
        '<div class="grp tiled"><div class="row">' +
          TILE +
          '<span class="lbl">' +
          esc(m.name) +
          '<small>' +
          fmt(m.dur) +
          ' · ' +
          mb(m.size) +
          '</small></span></div><button class="row" data-a="trkReplace"><span class="lbl acc">Replace track…</span>' +
          chev +
          '</button><button class="row" data-a="sheet" data-v="trkDel" data-k="' +
          sg.id +
          '"><span class="lbl dng">Remove track</span></button></div><p class="foot">Stays on this ' +
          deviceName() +
          ' and isn’t included in backups. The loop and the song’s timings stay with the song.</p>'
      );
    if (s === 'trkDel')
      return confirmSheet(
        'Remove the track?',
        'The audio is removed from this ' +
          deviceName() +
          '. The loop and timings stay with the song, so adding the same file again lines everything up.',
        'Remove track',
        'trkRemove',
        (U.sd && U.sd.k) || U.songId
      );
    if (s === 'trkBig' && big)
      return sheetWrap(
        'A large file',
        '<p class="note">This file is ' +
          mb(big.file.size) +
          '. Reading it may take a while and uses space on your ' +
          deviceName() +
          '.</p><button class="cta" data-a="trkBigYes">Import it</button><button class="ghost" data-a="close">Cancel</button>'
      );
    return '';
  }
  const storageRow = () => {
    if (!have.size) return '';
    let s = 0;
    have.forEach((m) => (s += m.size));
    return '<div class="row"><span class="lbl">Song tracks</span><span class="mut">' + have.size + ' · ' + mb(s) + '</span></div>';
  };

  /* ----- adding, replacing and removing ----- */
  function pick(id) {
    if (busy) return toast('Still reading the last track');
    want = id ? { id } : { fresh: true };
    big = null;
    $('trackIn').click();
  }
  const nameOf = (f) =>
    (
      String((f && f.name) || '')
        .replace(/\.[^./]{1,5}$/, '')
        .replace(/\s+/g, ' ')
        .trim() || 'Untitled song'
    ).slice(0, 120);
  let busyEl = null;
  function showBusy(on) {
    if (on && !busyEl) {
      busyEl = document.createElement('div');
      busyEl.className = 'trkbusy glass';
      busyEl.setAttribute('role', 'status');
      busyEl.textContent = 'Reading the track…';
      document.body.appendChild(busyEl);
    } else if (!on && busyEl) {
      busyEl.remove();
      busyEl = null;
    }
  }
  async function add(file, target, ok) {
    if (!file || busy || !target) return;
    if (!ok && file.size > TRK_BIG) {
      big = { file, want: target };
      U.sheet = 'trkBig';
      U.sd = {};
      return rerender();
    }
    busy = { id: target.id || null };
    showBusy(true);
    rerender();
    let r = null;
    try {
      r = await analyse(await file.arrayBuffer());
    } catch (e) {}
    const fail = (msg) => {
      busy = null;
      showBusy(false);
      rerender();
      toast(msg);
    };
    if (!r) return fail(TRK_BAD);
    let sg = target.id ? songById(target.id) : null;
    if (target.id && !sg) return fail('That song was deleted');
    const fresh = !sg;
    if (fresh)
      sg = { id: 'g_' + Date.now().toString(36), name: nameOf(file), artist: '', added: Date.now(), pinned: false };
    const rec = {
      name: String(file.name || 'Track').slice(0, 200),
      size: file.size,
      type: file.type || '',
      dur: r.dur,
      added: Date.now(),
      blob: file,
    };
    try {
      await tx(['audio', 'peaks'], 'readwrite', (a, p) => {
        a.put(rec, sg.id);
        p.put({ p: r.peaks, rate: TRK_RATE, dur: r.dur }, sg.id);
      });
    } catch (e) {
      return fail('Couldn’t save the track. Storage may be full.');
    }
    if (fresh) D.songs.push(sg);
    const old = sg.track && sg.track.dur;
    if (cur && cur.id === sg.id) unload(); // replaced: the new audio and peaks load fresh
    delete pos[sg.id];
    sg.track = { name: rec.name, dur: r2(r.dur) };
    // the loop and timings stay; a loop past the new end is trimmed (or dropped if nothing's left)
    if (sg.loop) {
      const l = cleanLoop(sg.loop, r.dur);
      if (l) sg.loop = l;
      else delete sg.loop;
    }
    save();
    have.set(sg.id, metaOf(rec));
    busy = null;
    showBusy(false);
    if (U.view === 'trk' && U.songId === sg.id) {
      U.sheet = null;
      rerender();
    } else open(sg.id);
    toast(old && Math.abs(old - r.dur) > 1 ? TRK_LENGTH : fresh ? 'New song from the track' : old ? 'Track added' : 'Track added');
  }
  // forget a song's track on this device (deleting the song, or Remove track)
  async function forget(ids) {
    ids = (ids || []).filter((id) => typeof id === 'string');
    if (!ids.length) return;
    if (cur && ids.includes(cur.id)) unload();
    ids.forEach((id) => {
      have.delete(id);
      delete pos[id];
    });
    try {
      await tx(['audio', 'peaks'], 'readwrite', (a, p) =>
        ids.forEach((id) => {
          a.delete(id);
          p.delete(id);
        })
      );
    } catch (e) {}
    fwUpdate();
  }
  async function remove(id) {
    const sg = songById(id);
    await forget([id]);
    if (sg) {
      delete sg.track; // the loop and timings stay with the song
      save();
    }
    U.sheet = null;
    U.sd = {};
    toast('Track removed');
    if (U.view === 'trk') back();
    else rerender();
  }

  /* ----- doors ----- */
  function open(id) {
    if (!songById(id)) return;
    if (rec) return toast('Stop recording first');
    go(() => {
      U.tab = 'songs';
      U.view = 'trk';
      U.songId = id;
      U.sheet = null;
      U.sd = {};
    });
  }
  // Back goes to the song's page
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

  /* ----- after every redraw ----- */
  function after() {
    // the song went (deleted, Reset all data, a restore without it): stop and let go of its audio
    if (cur && !songById(cur.id)) unload();
    if (U.view === 'trk') {
      const sg = songById(U.songId);
      if (sg && have.has(sg.id) && (!cur || cur.id !== sg.id)) open1(sg.id);
      // back on its own screen and paused: leaving again shows no window (you've seen it's stopped)
      if (here() && el && el.paused) woke = false;
      colours();
      draw();
      paint();
    }
    showBusy(!!busy);
  }
  window.addEventListener('resize', () => draw());

  /* ----- fingers: the strip (scrub, handles, double-tap), the jog wheel, rows, pinch ----- */
  const stripX = (e) => {
    const c = $('trkC');
    if (!c) return null;
    const r = c.getBoundingClientRect();
    return { x: e.clientX - r.left, w: r.width };
  };
  const pps = (w) => w / (TRK_LEVELS[lv()].win || 16);
  document.addEventListener('pointerdown', (e) => {
    if (U.view !== 'trk' || !cur || e.button > 0 || pinch) return;
    const jog = e.target.closest && e.target.closest('#trkJog');
    const st = !jog && e.target.closest && e.target.closest('#trkStrip');
    if (!jog && !st) return;
    const p = stripX(e);
    if (!p) return;
    e.preventDefault();
    let kind = jog ? 'jog' : 'scrub',
      which = null;
    const L = loopNow();
    if (st && L) {
      const k = pps(p.w),
        hx = p.w * TRK_HEAD,
        t = now(),
        ds = Math.abs(hx + (L.start - t) * k - p.x),
        de = Math.abs(hx + (L.end - t) * k - p.x);
      if (Math.min(ds, de) <= 22) {
        kind = 'handle';
        which = ds <= de ? 'start' : 'end';
      }
    }
    drag = { kind, which, id: e.pointerId, x: e.clientX, y: e.clientY, t: now(), at: Date.now(), moved: 0, w: p.w };
    if (jog) drag.rot = +(jog.dataset.rot || 0);
    try {
      (jog || st).setPointerCapture(e.pointerId);
    } catch (x) {}
    (jog || st).classList.add('drag');
  });
  document.addEventListener('pointermove', (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const dx = e.clientX - drag.x,
      dy = e.clientY - drag.y;
    drag.moved = Math.max(drag.moved, Math.hypot(dx, dy));
    if (drag.kind === 'jog') {
      // down moves later, up earlier; slow drags are precise, quick ones skim
      seek(drag.t + (dy * (TRK_LEVELS[lv()].win || 16)) / TRK_JOG);
      const j = $('trkJog');
      if (j) {
        j.dataset.rot = drag.rot + dy;
        const r = j.querySelector('.trkjogr');
        if (r) r.style.transform = 'rotate(' + (drag.rot + dy) + 'deg)';
      }
    } else if (drag.kind === 'scrub') {
      if (drag.moved > 2) seek(drag.t - dx / pps(drag.w));
    } else if (drag.kind === 'handle') {
      const p = stripX(e);
      if (p) dragHandle(now() + (p.x - p.w * TRK_HEAD) / pps(p.w));
    }
  });
  const endDrag = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag;
    drag = null;
    document.querySelectorAll('#trkStrip.drag, #trkJog.drag').forEach((x) => x.classList.remove('drag'));
    if (d.kind === 'handle') {
      save(); // a handle saves once, on release
      prevT = now();
      paint();
      draw();
    }
    if (e.type === 'pointerup' && d.kind !== 'jog' && d.moved < 8 && Date.now() - d.at < 300) {
      const p = stripX(e);
      if (!p) return;
      const n = Date.now();
      if (lastTap && n - lastTap.at < 350 && Math.abs(p.x - lastTap.x) < 30) {
        lastTap = null;
        // double-tap outside the loop clears it
        const L = loopNow(),
          v = now() + (p.x - p.w * TRK_HEAD) / pps(p.w);
        if (L && (v < L.start || v > L.end)) clearLoop();
      } else lastTap = { at: n, x: p.x };
    }
  };
  document.addEventListener('pointerup', endDrag);
  document.addEventListener('pointercancel', endDrag);
  // a row: zoom into Line view at that spot
  function rowTap(btn, e) {
    const cv = btn.querySelector('canvas');
    if (!cv) return;
    const r = cv.getBoundingClientRect(),
      rs = TRK_LEVELS[lv()].row,
      x = e && e.clientX ? Math.max(0, Math.min(r.width, e.clientX - r.left)) : 0;
    seek(+btn.dataset.r * rs + (x / Math.max(1, r.width)) * rs);
    setLevel(1);
    window.scrollTo(0, 0);
  }
  // pinch on the waveform: a step per TRK_PINCH px. Spread to zoom in (towards Phrase), pinch to zoom out.
  // Changing level replaces the waveform under the fingers, and a removed element's touches no longer reach the
  // document, so the pinch also listens on the elements the fingers started on
  const span = (t) => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
  const seen = new WeakSet();
  function pinchMove(e) {
    if (!pinch || e.touches.length !== 2 || seen.has(e)) return;
    seen.add(e);
    if (e.cancelable) e.preventDefault();
    const k = Math.trunc((span(e.touches) - pinch.d) / TRK_PINCH);
    if (k !== pinch.k) {
      pinch.k = k;
      setLevel(pinch.lv - k);
    }
  }
  function pinchEnd(e) {
    if (!pinch || e.touches.length >= 2) return;
    pinch.nodes.forEach((n) => {
      n.removeEventListener('touchmove', pinchMove);
      n.removeEventListener('touchend', pinchEnd);
      n.removeEventListener('touchcancel', pinchEnd);
    });
    pinch = null;
  }
  document.addEventListener(
    'touchstart',
    (e) => {
      if (U.view !== 'trk' || e.touches.length !== 2 || !$('trkWave')) return;
      if (![...e.touches].every((t) => t.target.closest && t.target.closest('#trkWave'))) return;
      drag = null;
      const nodes = [...new Set([...e.touches].map((t) => t.target))];
      nodes.forEach((n) => {
        n.addEventListener('touchmove', pinchMove, { passive: false });
        n.addEventListener('touchend', pinchEnd);
        n.addEventListener('touchcancel', pinchEnd);
      });
      pinch = { d: span(e.touches), lv: lv(), k: 0, nodes };
    },
    { passive: true }
  );
  document.addEventListener('touchmove', pinchMove, { passive: false });
  document.addEventListener('touchend', pinchEnd);
  document.addEventListener('touchcancel', pinchEnd);
  // a trackpad pinch on a Mac arrives as a wheel with Ctrl held
  document.addEventListener(
    'wheel',
    (e) => {
      if (U.view !== 'trk' || !e.ctrlKey || !(e.target.closest && e.target.closest('#trkWave'))) return;
      e.preventDefault();
      wheelAcc += e.deltaY;
      if (Math.abs(wheelAcc) >= TRK_PINCH) {
        setLevel(lv() + Math.sign(wheelAcc));
        wheelAcc = 0;
      }
    },
    { passive: false }
  );
  // the keyboard on a Mac or iPad: Space plays, arrows move, I and O set the start and end (as in Final Cut Pro)
  document.addEventListener('keydown', (e) => {
    if (U.view !== 'trk' || !cur || U.sheet || e.metaKey || e.ctrlKey || e.altKey) return;
    const a = document.activeElement;
    if (a && a.matches && a.matches('input, textarea, [contenteditable="true"]')) return;
    const k = e.key.toLowerCase();
    if (k === ' ') toggle();
    else if (k === 'arrowleft' || k === 'arrowright') seek(now() + (k === 'arrowleft' ? -1 : 1) * (e.shiftKey ? 5 : 1));
    else if (k === 'i') setAt('start');
    else if (k === 'o') setAt('end');
    else return;
    e.preventDefault();
  });
  $('trackIn').addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0],
      w = want;
    e.target.value = '';
    want = null;
    if (f && w) add(f, w);
  });

  /* ----- the floating window (window.js): take → video → track → playing along → session ----- */
  const fwKind = {
    id: 'track',
    active: () => !!(cur && el && woke && songById(cur.id) && !el.ended && (!el.paused || el.currentTime > 0.5)),
    own: () => here(),
    info() {
      const sg = song(),
        on = playing();
      return {
        k: (on ? 'Playing' : 'Paused') + ' · ' + (sg ? songTitle(sg) : 'Track'),
        t: fmt(now()),
        p: Math.min(1, now() / Math.max(1, len())),
        on,
        open: 'Back to the track',
        label: 'Track ' + (on ? 'playing' : 'paused'),
      };
    },
    toggle: () => toggle(),
    open() {
      if (!cur) return;
      const id = cur.id;
      fwGo(() => {
        U.tab = 'songs';
        U.view = 'trk';
        U.songId = id;
        U.sheet = null;
        U.sd = {};
      }, 0);
    },
  };
  {
    const i = FW_KINDS.findIndex((k) => k.id === 'clock' || k.id === 'session');
    FW_KINDS.splice(i < 0 ? FW_KINDS.length : i, 0, fwKind);
  }

  /* ----- actions (data-a="trk…") ----- */
  Object.assign(SG_ACT, {
    trkOpen(el, v, k) {
      open(k);
    },
    trkAdd(el, v, k) {
      pick(k || U.songId);
    },
    trkNew() {
      if (rec) return toast('Stop recording first');
      pick(null);
    },
    trkBack() {
      back();
    },
    trkMenu() {
      U.sheet = 'trkMenu';
      U.sd = {};
      rerender();
    },
    trkReplace() {
      U.sheet = null;
      U.sd = {};
      rerender();
      pick(U.songId);
    },
    trkRemove(el, v, k) {
      remove(k || U.songId);
    },
    trkBigYes() {
      const b = big;
      big = null;
      U.sheet = null;
      U.sd = {};
      if (b) add(b.file, b.want, true);
      else rerender();
    },
    trkPP() {
      toggle();
    },
    trkToStart() {
      toStart();
    },
    trkLoop() {
      toggleLoop();
    },
    trkSet(el, v) {
      setAt(v === 'end' ? 'end' : 'start');
    },
    trkSpeed() {
      cycleSpeed();
    },
    trkLevel(el, v) {
      setLevel(+v);
    },
    trkRow(el, v, k, e) {
      rowTap(el, e);
    },
  });

  return {
    load,
    page,
    bar,
    dock,
    row,
    sheet,
    after,
    storageRow,
    open,
    back,
    pick,
    forget,
    play,
    pause,
    toggle,
    seek,
    setAt,
    setLevel,
    frame,
    // tests: where the next file given to #trackIn goes, without opening the picker
    expect(id) {
      want = id ? { id } : { fresh: true };
    },
    has: (id) => have.has(id),
    meta: (id) => (have.get(id) ? Object.assign({}, have.get(id)) : null),
    busy: () => !!busy,
    el: () => el,
    now,
    len,
    level: lv,
    speed,
    peaks: () => (cur ? cur.peaks : null),
    state: () => ({
      id: cur ? cur.id : null,
      loaded: !!cur,
      playing: playing(),
      t: now(),
      dur: len(),
      level: lv(),
      speed: speed(),
      woke,
      busy: !!busy,
    }),
  };
})();
