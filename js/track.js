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
// Q02 (Track: Waveform Sections): Phrase and Line are the strip, Song is the whole song in 24 s rows, and Markers is
// a grid of rehearsal tiles. (3.19–3.22 had Section 20 s and Song 30 s rows; the saved level is reset once, below.)
const TRK_LEVELS = [
  { id: 'phrase', name: 'Phrase', win: 6 }, // a scrolling strip, 6 s on screen
  { id: 'line', name: 'Line', win: 16 }, // a scrolling strip, 16 s on screen
  { id: 'song', name: 'Song', row: 24 }, // rows of 24 s, the whole song (the last one ends at the track's end)
  { id: 'markers', name: 'Markers', grid: true }, // the markers as large tiles, two columns
];
const TRK_LV_DEFAULT = 1; // Line: section starts are set with the lyric card above the strip
const TRK_LV_V = 2; // the levels' layout version: a level saved by 3.19–3.22 is reset to the default once
const TRK_JOGS = ['left', 'right', 'bottom'];
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
  const o = { start: Math.round(s * 100) / 100, end: Math.round(e * 100) / 100, on: l.on === true };
  if (typeof l.mk === 'string' && l.mk) o.mk = l.mk; // 3.20: the chip this loop belongs to (checked in cleanSong)
  return o;
}

/* ===== 3.20 markers ("chips"): sg.markers = [{id, t, end?, name?}], saved with the song and in backups =====
   Numbers 0 or more, an end at least TRK_MIN after its start, clamped to the track's length when it's known, sorted by
   time, unique ids. A marker is unnamed for now; Track 2 can promote one into a section start. */
function cleanMarkers(list, dur) {
  if (!Array.isArray(list)) return null;
  const num = (x) => typeof x === 'number' && isFinite(x) && x >= 0,
    seen = new Set(),
    out = [];
  list.forEach((m) => {
    if (!m || typeof m !== 'object' || Array.isArray(m) || typeof m.id !== 'string' || !m.id || seen.has(m.id)) return;
    if (!num(m.t)) return;
    let t = m.t;
    if (dur > 0 && t > dur) return;
    const o = { id: m.id.slice(0, 40), t: Math.round(t * 100) / 100 };
    if (num(m.end)) {
      let e = m.end;
      if (dur > 0 && e > dur) e = dur;
      if (e > t + TRK_MIN - 1e-6) o.end = Math.round(e * 100) / 100;
    }
    if (typeof m.name === 'string' && m.name.trim()) o.name = m.name.trim().slice(0, 60);
    seen.add(o.id);
    out.push(o);
  });
  out.sort((a, b) => a.t - b.t);
  return out.length ? out : null;
}

const TRACK = (() => {
  const have = new Map(); // song id → {name, size, type, dur, added}: tracks on this device
  let cur = null; // the track in the <audio>: {id, peaks, rate, dur, url}
  let el = null; // the one <audio>
  let loading = null;
  let busy = null; // importing: {id}
  let want = null; // where the file picked next goes: {id} or {fresh: true}
  let big = null; // a large file waiting for its OK: {file, want}
  let past = null; // Q12: a shorter track replaced a longer one, with markers or lines past its end: {id, dur, mk, ln}
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
  let mkCur = null; // 3.20: the chip last tapped, outlined: {id: song id, mk: marker id}
  let mkHold = null; // holding a chip for its menu
  let along = null; // Q02: Song Clock's play-along is driving this audio ({id}); play-along owns the sound
  let alongEnd = false; // a play-along reached the track's end (its pause came before the ended event)
  let mdl = null; // Q02: the song's timing (ckModel), kept until the next redraw or change
  let ctxAt = null; // the line the lyric card last showed
  let mute = false; // Q09 Backing Sound off: the track plays silently in Markers (on again whenever you leave the player)
  let wrapT = 0; // Q09 the timer that wraps the loop right at its end (a frame can be up to 16 ms late; a locked screen more)
  const wraps = []; // Q09 the last few wraps, for the tests: {t, start, end, rate, by}
  let lane = null; // Q05 the line block selected on the line lane: {id: song id, i: index into ckLines}
  let ret = null; // Q05 where Back goes when Retime came from Check timing ('ckCheck'); otherwise the song's page

  /* ----- this device's settings: zoom level, speed, jog wheel and Song lyrics (vocalSongPrefs, never backed up) ----- */
  function prefs() {
    const p = sgp();
    // Q02: the levels changed, so a level saved before is reset to the default, once
    if (p.trkLvV !== TRK_LV_V) {
      p.trkLevel = TRK_LV_DEFAULT;
      p.trkLvV = TRK_LV_V;
      saveSGP();
    }
    if (!(Number.isInteger(p.trkLevel) && p.trkLevel >= 0 && p.trkLevel < TRK_LEVELS.length)) p.trkLevel = TRK_LV_DEFAULT;
    if (!TRK_SPEEDS.includes(p.trkSpeed)) p.trkSpeed = 1;
    if (!TRK_JOGS.includes(p.trkJogPos)) p.trkJogPos = 'right';
    if (typeof p.trkSongLyrics !== 'boolean') p.trkSongLyrics = true;
    return p;
  }
  const lv = () => prefs().trkLevel;
  const speed = () => prefs().trkSpeed;
  const jogPos = () => prefs().trkJogPos;
  const strip = () => !!TRK_LEVELS[lv()].win;
  const grid = () => !!TRK_LEVELS[lv()].grid;

  /* ----- stored on the device: its own database, apart from recordings, the coach video and backups ----- */
  // through the shared helper (Q11, storage.js): the audio as imported, and its waveform peaks, as separate entries
  // keyed by song id. Name, version and stores as before
  const TDB = IDB.define('vocalTracks', 1, { audio: null, peaks: null });
  const tx = (stores, mode, fn) => TDB.tx(stores, mode, fn);
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
    await TDB.each('audio', (k, v) => {
      if (typeof k === 'string' && okAudio(v)) have.set(k, metaOf(v));
    });
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
      // Q02: playing along, the sound is Song Clock's: its window and its lock screen buttons
      if (!along) {
        woke = true;
        media();
      }
      frames();
      armWrap();
      paintRows();
      changed();
    });
    el.addEventListener('pause', () => {
      clearTimeout(wrapT);
      wrapT = 0;
      if (cur) pos[cur.id] = el.currentTime;
      // Q02: stopped from outside play-along (the lock screen, another sound): play-along pauses with it. (A pause
      // event that arrives after play-along has started the audio again is an older one, from what played before.)
      if (along && el.paused) {
        along = null;
        el.muted = false;
        if (el.ended) alongEnd = true;
        if (typeof ckAlongStopped === 'function') ckAlongStopped();
      }
      // paused on its own screen: you meant to stop, so no window follows you out
      if (here()) woke = false;
      if (!el.ended) fwPaused('track'); // 3.20: paused anywhere but the window: no window either
      paintRows();
      changed();
    });
    // Q02 sleep: with the screen locked there are no animation frames, so the loop is also kept on timeupdate
    el.addEventListener('timeupdate', () => {
      if (!raf || document.hidden) keepLoop(false, 'tick');
      armWrap();
    });
    el.addEventListener('ended', () => {
      // the end of a play-along (its pause came first): the player's own loop doesn't take over
      if (alongEnd || along) {
        alongEnd = false;
        if (along) {
          along = null;
          el.muted = false;
          if (typeof ckAlongStopped === 'function') ckAlongStopped();
        }
        paintRows();
        return changed();
      }
      const L = loopNow();
      if (L && L.on && L.end >= len() - 0.1) {
        seek(L.start);
        el.play().catch(() => {});
        return;
      }
      NOW.ended('track');
      paintRows();
      changed();
    });
    el.addEventListener('seeked', () => {
      paint();
      if (!playing()) draw();
      else armWrap();
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
  /* ----- Q02 the song's timing, from Song Clock (one timing model: ckModel reads it, ckStore writes it) ----- */
  function model() {
    const sg = song();
    if (!sg || !hasLyrics(sg)) return null;
    if (!mdl || mdl.sg !== sg) mdl = ckModel(sg);
    return mdl;
  }
  const timed = () => {
    const sg = song();
    return !!(sg && ckSynced(sg));
  };
  // the section starts that are set (Song Clock's anch): [{k, t, label}] in running order
  function secStarts() {
    const M = model();
    if (!M || !timed()) return [];
    const out = [];
    M.anch.forEach((a, k) => {
      if (!a) return;
      const i = ckFirst(M.L, k);
      if (i >= 0 && M.T[i][0] != null) out.push({ k, t: M.T[i][0], label: occLabel(M.sg, k) });
    });
    return out;
  }

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
  // load a song's track once, however many callers are waiting for it
  let loadP = null;
  function ensure(id) {
    if (cur && cur.id === id) return Promise.resolve();
    if (loading === id && loadP) return loadP;
    loadP = open1(id);
    return loadP;
  }

  /* ----- Q02 play-along from the track: Song Clock owns the sound (NOW kind 'clock') and the lyrics follow the
     track's time. getT() is where Song Clock wants it to be when the audio is ready. ----- */
  async function alongPlay(id, getT, mute) {
    if (!have.has(id)) return false;
    along = { id };
    alongEnd = false;
    await ensure(id);
    if (!along || along.id !== id || !cur || cur.id !== id) return false;
    const v = audio();
    v.muted = !!mute;
    v.playbackRate = speed();
    pitch();
    seek(getT());
    try {
      await v.play();
    } catch (e) {
      if (along && along.id === id) {
        along = null;
        v.muted = false;
        if (typeof ckAlongStopped === 'function') ckAlongStopped();
      }
      return false;
    }
    return true;
  }
  // play-along paused or stopped: the track stops quietly (Song Clock already knows)
  function alongPause() {
    if (!along) return;
    along = null;
    if (el) {
      el.pause();
      el.muted = false;
    }
  }
  // the track's time while it drives play-along, else null (Song Clock uses its own clock until the audio plays)
  const alongNow = (id) =>
    along && along.id === id && cur && cur.id === id && el && el.readyState >= 1 && pend == null && !el.paused
      ? el.currentTime
      : null;
  function alongMute(on) {
    if (along && el) el.muted = !!on;
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
  function play() {
    if (!cur) return;
    const v = audio();
    // one sound at a time (3.20): whatever else plays stops
    NOW.start('track', cur.id, () => pause());
    // with the loop on, play starts in the loop; a track that had finished starts again from 0:00 (3.20)
    const L = loopNow(),
      t = now();
    if (L && L.on && (t < L.start - 0.01 || t >= L.end - 0.01)) seek(L.start);
    else if (v.ended || (len() > 0 && t >= len() - 0.05)) seek(0);
    v.playbackRate = speed();
    pitch();
    syncMute();
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
    clearTimeout(wrapT);
    wrapT = 0;
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
    keepLoop(false, 'frame');
    armWrap();
    draw();
    paint();
    if (FW.shown === 'track') fwTick();
  }
  // the loop's boundary: wrap when playback crosses its end. Q02: also on timeupdate (no frames while the screen is
  // locked) and, waking, a playhead found outside the loop goes back to its start (best effort: iOS decides how
  // often a locked page hears anything)
  function keepLoop(wake, by) {
    if (!cur || !el) return;
    const L = loopNow();
    let t = el.currentTime;
    if (L && L.on && !along && !(drag && drag.kind !== 'handle')) {
      if (prevT < L.end && t >= L.end - 0.005) {
        wrapTo(L, t, by || 'frame');
        t = L.start;
      } else if (wake && !el.paused && (t < L.start - 0.05 || t > L.end + 0.05)) {
        el.currentTime = L.start;
        t = L.start;
      }
    }
    prevT = t;
    pos[cur.id] = t;
  }
  // Q09 the loop's boundary, as close to its end as a timer allows: when the end is under 0.3 s away (in real time, at
  // this speed) a timer is set for that moment, so the jump back isn't held up waiting for the next frame (or, locked, for
  // the next timeupdate). The frame and timeupdate checks above stay as the safety net, so no boundary is missed. Still
  // one <audio> with its pitch kept (the gapless Web Audio loop would change the pitch when slowed, and a second element
  // would fight the lock screen and one sound at a time)
  function wrapTo(L, t, by) {
    wraps.push({ t: r3(t), start: L.start, end: L.end, rate: el.playbackRate, by });
    if (wraps.length > 30) wraps.shift();
    el.currentTime = L.start;
    prevT = L.start;
    if (cur) pos[cur.id] = L.start;
  }
  const r3 = (x) => Math.round(x * 1000) / 1000;
  const WRAP_SOON = 0.3; // seconds of real time before the end that the timer is set
  const WRAP_NEAR = 0.012; // seconds of real time: close enough to the end to jump now
  function armWrap() {
    clearTimeout(wrapT);
    wrapT = 0;
    if (!cur || !el || el.paused || along || (drag && drag.kind !== 'handle') || el.readyState < 1 || pend != null)
      return;
    const L = loopNow();
    if (!L || !L.on) return;
    const t = el.currentTime,
      rate = el.playbackRate || 1,
      left = (L.end - t) / rate;
    if (t < L.start - 0.05 || left <= 0 || left > WRAP_SOON) return;
    wrapT = setTimeout(
      () => {
        wrapT = 0;
        const L2 = loopNow();
        if (!cur || !el || el.paused || along || !L2 || !L2.on || (drag && drag.kind !== 'handle')) return;
        const t2 = el.currentTime;
        if (t2 < L2.start - 0.05 || t2 > L2.end + 0.25) return; // moved away meanwhile: the frame check decides
        if ((L2.end - t2) / (el.playbackRate || 1) > WRAP_NEAR) return armWrap(); // the timer came early: once more
        wrapTo(L2, t2, 'timer');
      },
      Math.max(0, left * 1000 - 4)
    );
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden || !cur || !el) return;
    keepLoop(true, 'wake');
    draw();
    paint();
    if (playing()) frames();
  });
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
  function setLoop(s, e, on, mk) {
    const sg = song();
    if (!sg) return;
    const d = len();
    s = Math.max(0, Math.min(d, s));
    e = Math.max(0, Math.min(d, e));
    if (e - s < TRK_MIN) return false;
    sg.loop = { start: r2(s), end: r2(e), on: on !== false };
    if (mk) sg.loop.mk = mk;
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
      save(); // 3.20: Set start / Set end make a loop of their own; a chip keeps its range
      prevT = now();
      draw();
      paint();
      chips();
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
    chips();
  }
  function clearLoop() {
    const sg = song();
    if (!sg || !sg.loop) return;
    delete sg.loop;
    save();
    paint();
    draw();
    chips();
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
    if (!$('trkWave')) return;
    const b = document.querySelector('#app .trklv button[data-v="' + i + '"]');
    if (b) segPick(b);
    body();
    // Q02: Markers has its own transport (Q09: Replay, Play/Pause and Next pads, under Backing Sound and Loop)
    if (!!TRK_LEVELS[was].grid !== grid()) renderDock();
    syncMute(); // Q09: Backing Sound off only silences Markers
    const box = $('trkWave');
    showHead();
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
    C = {
      fg: g('--fg', '#000'),
      dim: g('--trk-dim', '#bbb'),
      loop: g('--trk-loop', '#ff9500'),
      head: g('--trk-playhead', '#ff3b30'), // Q02: the playhead is red in both themes
      mk: g('--trk-mk', '#af52de'),
      // Q10: a marker's numbered tab is filled with the higher-contrast purple, so its number stays readable
      mkink: g('--trk-mk-ink', '#8944ab'),
      mkinkfg: g('--trk-mk-inkfg', '#fff'),
      sec: g('--trk-sec', '#007aff'),
      secfg: g('--trk-secfg', '#fff'),
      // Q05 the line lane: placed lines solid, estimated ones dashed, the selected one stronger
      ln: g('--accent', '#007aff'),
      lnfg: g('--fg', '#000'),
      lnfg2: g('--fg2', '#6c6c72'),
      lnfg3: g('--fg3', '#a3a3a8'),
      font: getComputedStyle(document.body).fontFamily || 'sans-serif',
    };
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
  // 3.20 markers: purple lines (never orange, which is the loop) with a small numbered tab; a range's end is a thin line
  function marks(g, X, w, h, tab) {
    const M = mks();
    if (!M.length) return;
    g.save();
    g.font = '600 ' + (tab <= 11 ? 8 : 10) + 'px ' + (getComputedStyle(document.body).fontFamily || 'sans-serif');
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    M.forEach((m, i) => {
      const x = X(m.t);
      if (m.end != null) {
        const xe = X(m.end);
        if (xe > -20 && xe < w + 20) {
          g.fillStyle = C.mk;
          g.globalAlpha = 0.7;
          g.fillRect(xe - 0.75, tab, 1.5, h - tab);
          g.globalAlpha = 1;
        }
      }
      if (x < -20 || x > w + 20) return;
      g.fillStyle = C.mk;
      g.fillRect(x - 1, 0, 2, h);
      const tw = tab + (i >= 9 ? 4 : 0);
      g.fillStyle = C.mkink;
      rr(g, x - 1, 0, tw, tab, 3);
      g.fillStyle = C.mkinkfg;
      g.fillText(String(i + 1), x - 1 + tw / 2, tab / 2 + 0.5);
    });
    g.restore();
  }
  // Q02 section starts: blue lines, with the section's name on a tab (strip) or just the line (rows)
  function secs(g, X, w, h, tab) {
    const S = secStarts();
    if (!S.length) return;
    g.save();
    g.font = '600 11px ' + C.font;
    g.textBaseline = 'middle';
    S.forEach((s) => {
      const x = X(s.t);
      if (x < -160 || x > w + 20) return;
      g.fillStyle = C.sec;
      g.globalAlpha = 0.9;
      g.fillRect(x - 0.75, 0, 1.5, h);
      g.globalAlpha = 1;
      if (!tab) return;
      const tw = Math.min(140, g.measureText(s.label).width + 12);
      g.fillStyle = C.sec;
      rr(g, x - 0.75, tab, tw, 18, 4);
      g.fillStyle = C.secfg;
      g.save();
      g.beginPath();
      g.rect(x, tab, tw - 6, 18);
      g.clip();
      g.fillText(s.label, x + 5, tab + 9.5);
      g.restore();
    });
    g.restore();
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
      bars(g, t - hx / pps, t + (w - hx) / pps + 0.1, 4, 3, pps, x0, h / 2 + 6, h / 2 - 24, L);
      secs(g, (v) => x0 + v * pps, w, h, 18);
      if (L)
        [L.start, L.end].forEach((v) => {
          const x = x0 + v * pps;
          if (x < -20 || x > w + 20) return;
          g.fillStyle = C.loop;
          g.fillRect(x - 1.5, 0, 3, h);
          rr(g, x - 6.5, h - 17, 13, 17, 4);
        });
      marks(g, (v) => x0 + v * pps, w, h, 14);
      // the playhead: red (Q02), with a small dot above
      g.fillStyle = C.head;
      g.fillRect(hx - 1, 8, 2, h - 8);
      g.beginPath();
      g.arc(hx, 5, 4, 0, Math.PI * 2);
      g.fill();
      const s = $('trkStrip');
      if (s) s.setAttribute('aria-valuetext', fmt(t) + ' of ' + fmt(len()));
      laneDraw(c, x0, pps, hx);
      return;
    }
    const rs = TRK_LEVELS[lv()].row;
    if (!rs) return;
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
      secs(g, (v) => (v < a || v > b ? -999 : x0 + v * pps), w, h, 0);
      marks(g, (v) => (v < a || v > b ? -999 : x0 + v * pps), w, h, 11);
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
    const eh = $('trkEndH');
    if (eh) {
      const m = curMk(),
        ok = !!m && now() >= m.t + TRK_MIN - 1e-6;
      if (eh.classList.contains('wait') === ok) {
        eh.classList.toggle('wait', !ok);
        eh.setAttribute('aria-disabled', !ok);
      }
    }
    document.querySelectorAll('#trkMk .trkchl').forEach((b) => {
      const m = mkById(b.dataset.k),
        on = !!(m && chipLoopOn(m));
      if (b.classList.contains('on') !== on) {
        b.classList.toggle('on', on);
        b.setAttribute('aria-pressed', on);
      }
    });
    const lb = $('trkLoopB');
    if (lb) {
      const L = loopNow(),
        on = !!(L && L.on);
      lb.classList.toggle('on', on);
      lb.setAttribute('aria-pressed', on);
      lb.setAttribute('aria-label', L ? 'Loop ' + fmt1(L.start) + ' to ' + fmt1(L.end) : 'Loop (set a start and end first)');
    }
    paintCtx();
    paintTiles();
  }

  /* ----- Q05 the line lane: a block for each lyric line under the Phrase and Line strips, in running order -----
     Estimated lines (filled in, or spread from section starts and not placed yet) are dashed; placed ones solid. Drag a
     block's edge to move it (where two lines touch, one handle moves both); tap a block to select it, then Start here /
     End here at the playhead. Edges snap to the playhead, section starts and other lines' edges (about 10 px, so gentler
     zoomed in) while Snapping is on. Every change has Undo, and is written into Song Clock's timing (ckSetLines). */
  const LANE_EDGE = 14; // px either side of a block's edge that grabs it
  const LANE_SNAP = 10; // px
  const laneOn = () => {
    const sg = song();
    return !!(sg && hasLyrics(sg) && strip());
  };
  const laneSel = () => {
    const M = model();
    return lane && cur && lane.id === cur.id && M && lane.i < M.L.length ? lane.i : -1;
  };
  // the times the lane shows: the line being dragged (its working copy), else the song's timing
  function laneT() {
    if (drag && drag.kind === 'edge' && drag.W) return drag.W;
    const M = model();
    return M ? M.T.map((r, i) => [r[0], M.end(i)]) : [];
  }
  function laneDraw(sc, x0, pps, hx) {
    const c = $('trkLC'),
      box = $('trkLane');
    if (!c || !box) return;
    // the lane lines up with the strip's waveform (which starts 48 px in with the jog wheel on the left)
    const sr = sc.getBoundingClientRect(),
      br = box.getBoundingClientRect();
    c.style.left = Math.round(sr.left - br.left) + 'px';
    c.style.width = Math.round(sr.width) + 'px';
    const { g, w, h } = fit(c),
      M = model();
    if (!M) return;
    const T = laneT(),
      sel = laneSel(),
      y = 5,
      bh = h - 10;
    g.save();
    g.font = '500 12px ' + C.font;
    g.textBaseline = 'middle';
    T.forEach((r, i) => {
      if (r[0] == null) return;
      const xs = x0 + r[0] * pps,
        xe = x0 + r[1] * pps;
      if (xe < -4 || xs > w + 4) return;
      const est = M.est[i] && !(drag && drag.kind === 'edge' && (drag.a === i || drag.b === i)),
        on = i === sel,
        bx = xs + 1,
        bw = Math.max(3, xe - xs - 2);
      g.beginPath();
      if (g.roundRect) g.roundRect(bx, y, bw, bh, 7);
      else g.rect(bx, y, bw, bh);
      g.fillStyle = C.ln;
      g.globalAlpha = on ? 0.3 : est ? 0.06 : 0.16;
      g.fill();
      g.globalAlpha = on ? 1 : est ? 0.7 : 0.75;
      g.strokeStyle = est && !on ? C.lnfg3 : C.ln;
      g.lineWidth = on ? 2 : 1.25;
      g.setLineDash(est && !on ? [4, 3] : []);
      g.stroke();
      g.setLineDash([]);
      g.globalAlpha = 1;
      // the line's words, as far as they fit
      if (bw > 26) {
        g.save();
        g.beginPath();
        g.rect(bx + 6, y, bw - 12, bh);
        g.clip();
        g.fillStyle = on ? C.lnfg : est ? C.lnfg3 : C.lnfg2;
        g.fillText(M.L[i].words.join(' '), bx + 7, y + bh / 2 + 0.5);
        g.restore();
      }
      // the selected block's handles
      if (on)
        [bx, bx + bw].forEach((x) => {
          g.fillStyle = C.ln;
          rr(g, x - 2.5, y + bh / 2 - 9, 5, 18, 2.5);
        });
    });
    // the playhead runs through the lane too
    g.fillStyle = C.head;
    g.fillRect(hx - 1, 0, 2, h);
    g.restore();
  }
  // the time at an x on the lane (it shares the strip's scale)
  function laneX(e) {
    const c = $('trkLC');
    if (!c) return null;
    const r = c.getBoundingClientRect();
    return { x: e.clientX - r.left, w: r.width };
  }
  // what a finger lands on: an edge (with the line whose end and the line whose start it moves), a block, or nothing
  function laneHit(px, pw) {
    const M = model();
    if (!M) return null;
    const T = laneT(),
      k = pps(pw),
      hx = pw * TRK_HEAD,
      t0 = now(),
      X = (v) => hx + (v - t0) * k;
    let best = null;
    T.forEach((r, i) => {
      if (r[0] == null) return;
      const xs = X(r[0]),
        xe = X(r[1]),
        reach = Math.min(LANE_EDGE, Math.max(6, (xe - xs) / 3));
      [
        [xs, 'start'],
        [xe, 'end'],
      ].forEach(([x, which]) => {
        const d = Math.abs(px - x);
        if (d <= reach && (!best || d < best.d)) best = { d, i, which };
      });
    });
    if (best) {
      // where two lines touch, one handle moves the end of one and the start of the next together
      const i = best.i,
        touch = (a, b) => a >= 0 && b < T.length && Math.abs(X(T[b][0]) - X(T[a][1])) <= 3;
      if (best.which === 'end') return { kind: 'edge', a: i, b: touch(i, i + 1) ? i + 1 : null };
      return { kind: 'edge', a: touch(i - 1, i) ? i - 1 : null, b: i };
    }
    const v = t0 + (px - hx) / k,
      i = T.findIndex((r) => r[0] != null && v >= r[0] && v <= r[1]);
    return { kind: 'lane', i };
  }
  // dragging an edge: the working copy follows the finger, snapping and kept in order with its neighbours
  function laneMove(v) {
    const W = drag.W,
      a = drag.a,
      b = drag.b;
    if (ckPrefs().snapping) {
      const near = LANE_SNAP / pps(drag.w),
        cand = [now()].concat(secStarts().map((x) => x.t));
      W.forEach((r, i) => {
        if (i !== a && i !== b) cand.push(r[0], r[1]);
        else if (i === a && a != null) cand.push(r[0]);
        else if (i === b && b != null) cand.push(r[1]);
      });
      let sn = null;
      cand.forEach((c) => {
        if (c != null && Math.abs(c - v) <= near && (sn == null || Math.abs(c - v) < Math.abs(sn - v))) sn = c;
      });
      if (sn != null) v = sn;
    }
    // Q12: kept between the line's other edge and the placed lines either side (estimates are never limits)
    const M = model(),
      pb = a == null && b != null ? ckBounds(M, b)[0] : null,
      nb = b == null && a != null ? ckBounds(M, a)[1] : null,
      lb = a != null ? drag.O[a][0] + CK_MIN : pb != null ? pb + CK_MIN : 0,
      ub = b != null ? drag.O[b][1] - CK_MIN : nb != null ? nb : len();
    v = Math.max(lb, Math.min(ub, v));
    if (a != null) W[a][1] = v;
    if (b != null) {
      W[b][0] = v;
      // a start moved back over the line before trims that line's end
      if (a == null && b > 0 && W[b - 1][1] > v) W[b - 1][1] = Math.max(W[b - 1][0] + CK_MIN, v);
      else if (a == null && b > 0) W[b - 1][1] = drag.O[b - 1][1];
    }
    drag.moved2 = true;
    draw();
  }
  function laneCommit() {
    const d = drag,
      sg = song();
    if (!sg || !d.moved2) return draw();
    const ch = {};
    if (d.a != null) ch[d.a] = d.W[d.a].slice();
    if (d.b != null) ch[d.b] = d.W[d.b].slice();
    ckSetLines(sg, ch); // the placed line before a start dragged back over it is trimmed there (ckSetLines)
  }
  // Start here / End here: the selected line at the playhead (its length kept for a new start, where there's room)
  function laneAt(which) {
    const sg = song(),
      M = model(),
      i = laneSel();
    if (!sg || !M || i < 0) return toast('Tap a line on the lane first');
    // Q12: the limits are the placed lines either side, never estimates
    const t = r2(now()),
      [prevS, nextS] = ckBounds(M, i);
    let s = M.T[i][0],
      e = M.end(i);
    if (which === 'start') {
      if (prevS != null && t < prevS + CK_MIN) return toast('That’s before the line above starts');
      if (nextS != null && t > nextS - CK_MIN) return toast('That’s after the next line starts');
      const d = e - s;
      s = t;
      if (e < s + CK_MIN) e = Math.min(nextS != null ? nextS : len(), s + Math.max(d, CK_MIN));
    } else {
      if (t < s + CK_MIN) return toast('Move the playhead past the line’s start');
      e = nextS != null ? Math.min(t, nextS) : t;
    }
    ckSetLines(sg, { [i]: [s, e] });
  }
  // the time row under the waveform (no extra height on small phones): with a line selected on the lane, the line with
  // Start here / End here and ✕ beside the time; otherwise the time and a hint
  function infoInner() {
    const g = grid(),
      M = laneOn() ? model() : null,
      i = M ? laneSel() : -1,
      t = '<span class="trkt" id="trkT">' + fmt1(now()) + '</span>';
    if (i >= 0)
      return (
        t +
        '<span class="trklbt' +
        (M.est[i] ? ' est' : '') +
        '">' +
        esc(M.L[i].words.join(' ')) +
        '</span><button class="cvpill" data-a="trkLnStart">Start here</button><button class="cvpill" data-a="trkLnEnd">End here</button><button class="trklbx" data-a="trkLnX" aria-label="Deselect the line">' +
        ICON.x +
        '</button>'
      );
    // Markers: the speed sits here, since the grid has its own add tile and no Set start / Set end
    return t + '<span class="trkhint" id="trkHint">' + hint() + '</span>' + (g ? spdHTML() : '');
  }
  function laneBar() {
    const b = $('trkInfo');
    if (!b) return;
    b.innerHTML = infoInner();
    b.classList.toggle('lsel', laneSel() >= 0);
  }
  function laneSelect(i) {
    lane = i >= 0 && cur ? { id: cur.id, i } : null;
    laneBar();
    draw();
  }

  /* ----- Q02 the lyric card above the strip: the line before, the line at the playhead, the line after ----- */
  function ctxLines() {
    const M = model();
    if (!M || !timed()) return null;
    const a = ckAt(M.T, now()),
      line = (i) => (i >= 0 && i < M.L.length ? M.L[i].words.join(' ') : '');
    return {
      a,
      p: line(a - 1),
      c: a >= 0 ? line(a) : '',
      n: line(a + 1),
      lab: a >= 0 ? occLabel(M.sg, M.L[a].k) : M.L.length ? 'Before ' + occLabel(M.sg, M.L[0].k) : '',
    };
  }
  function ctxInner() {
    const sg = song();
    if (!sg || !hasLyrics(sg)) return '';
    const x = ctxLines();
    if (!x)
      return '<p class="trkcl trkcx">Add markers, then hold one to make it a section start. The lyrics follow here.</p>';
    return (
      '<p class="trkcl trkcp">' +
      esc(x.p) +
      '</p><p class="trkcl trkcc"><span class="trkct">' +
      (x.c ? esc(x.c) : '<span class="mut">…</span>') +
      '</span><span class="trkcs">' +
      esc(x.lab) +
      '</span></p><p class="trkcl trkcn">' +
      esc(x.n) +
      '</p>'
    );
  }
  function ctxHTML() {
    const h = ctxInner();
    return h ? '<div class="trkctx" id="trkCtx">' + h + '</div>' : '';
  }
  function paintCtx() {
    const box = $('trkCtx');
    if (!box) return;
    const x = ctxLines(),
      key = x ? x.a : 'none';
    if (key === ctxAt) return;
    const was = ctxAt;
    ctxAt = key;
    box.innerHTML = ctxInner();
    // Q09 the teleprompter: the new line rises (or, going back, drops) into place on the gentle spring, its neighbours
    // follow, and the line itself gives one soft pulse. Not on the first paint after a redraw (nothing changed then).
    // Reduce Motion: a short fade, no pulse. Motion off: nothing
    if (was === null || !x || typeof key !== 'number') return;
    const dir = typeof was === 'number' && key < was ? -1 : 1,
      c = box.querySelector('.trkcc'),
      t = box.querySelector('.trkct');
    MOTION.animate(
      c,
      [
        { transform: 'translateY(' + 12 * dir + 'px)', opacity: 0.35 },
        { transform: 'none', opacity: 1 },
      ],
      {
        spring: 'gentle',
        fade: true,
      }
    );
    box.querySelectorAll('.trkcp, .trkcn').forEach((p) =>
      MOTION.animate(
        p,
        [
          { transform: 'translateY(' + 6 * dir + 'px)', opacity: 0 },
          { transform: 'none', opacity: 1 },
        ],
        {
          spring: 'gentle',
          fade: true,
        }
      )
    );
    if (t && !MOTION.reduced())
      MOTION.animate(
        t,
        [{ transform: 'scale(1)' }, { transform: 'scale(1.035)', offset: 0.35 }, { transform: 'scale(1)' }],
        { ms: 460, easing: 'ease-out' }
      );
  }

  /* ----- Q02 the Markers grid: where each marker's rehearsal loop runs, and which one the playhead is in ----- */
  // to its own end, else the next marker, else the track's end; too short (under 0.5 s) to loop
  function rangeOf(m) {
    const M = mks(),
      i = M.indexOf(m),
      nx = M.slice(i + 1).find((x) => x.t > m.t + 1e-6),
      e = m.end != null ? m.end : nx ? nx.t : len();
    return { s: m.t, e, ok: e - m.t >= TRK_MIN - 1e-6 };
  }
  function playingMk() {
    const t = now();
    let at = null;
    mks().forEach((m) => {
      const r = rangeOf(m);
      if (t >= m.t - 0.01 && t < r.e) at = m;
    });
    return at;
  }
  function paintTiles() {
    const box = $('trkGrid');
    if (!box) return;
    const p = playing() ? playingMk() : null,
      c = curMk(),
      id = p ? p.id : '';
    box.querySelectorAll('.trktl[data-mk]').forEach((tl) => {
      const k = tl.dataset.mk,
        m = mkById(k),
        on = !!(m && chipLoopOn(m));
      tl.classList.toggle('play', k === id);
      tl.classList.toggle('sel', !!(c && c.id === k));
      const lb = tl.querySelector('.trktlo');
      if (lb && lb.classList.contains('on') !== on) {
        lb.classList.toggle('on', on);
        lb.setAttribute('aria-pressed', on);
      }
    });
    const q = $('trkQaT');
    if (q) {
      const v = fmt1(now());
      if (q.textContent !== v) q.textContent = v;
    }
  }

  /* ----- 3.20 a song row's play button ----- */
  // a tiny silent sound played first, in the tap, so iPhone lets the track start once it has loaded
  const HUSH = 'data:audio/wav;base64,UklGRiwAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQgAAAAAAAAAAAAAAA==';
  async function playSong(id) {
    if (!songById(id)) return;
    if (!have.has(id)) return toast('Upload a track to play', 1100);
    if (rec) return toast('Stop recording first');
    if (cur && cur.id === id) return toggle();
    const v = audio();
    unload();
    try {
      v.src = HUSH;
      const p = v.play();
      if (p && p.catch) p.catch(() => {});
    } catch (e) {}
    paintRows(id);
    await open1(id);
    if (!cur || cur.id !== id) return paintRows();
    play();
  }
  const rowIsOn = (id) => !!(cur && cur.id === id && playing());
  function rowPlay(sg) {
    const on = have.has(sg.id),
      p = rowIsOn(sg.id);
    return (
      '<button class="sgplay' +
      (on ? '' : ' off') +
      (p ? ' on' : '') +
      '" data-a="sgRowPlay" data-k="' +
      sg.id +
      '" aria-label="' +
      (p ? 'Pause ' : 'Play ') +
      esc(songTitle(sg)) +
      '"' +
      (on ? '' : ' aria-disabled="true"') +
      '>' +
      (p ? ICON.pause : ICON.play) +
      '</button>'
    );
  }
  // the rows' buttons, in place: pause on the playing song's row, play on the others
  function paintRows(loadingId) {
    document.querySelectorAll('[data-a=sgRowPlay]').forEach((b) => {
      const id = b.dataset.k,
        p = rowIsOn(id) || loadingId === id;
      if (b.classList.contains('on') === p) return;
      const sg = songById(id);
      b.classList.toggle('on', p);
      b.innerHTML = p ? ICON.pause : ICON.play;
      b.setAttribute('aria-label', (p ? 'Pause ' : 'Play ') + (sg ? songTitle(sg) : 'song'));
    });
  }

  /* ----- 3.20 markers and chips ----- */
  const MKI =
    '<svg class="i" viewBox="0 0 24 24"><path d="M7 3.5v17"/><path d="M7 4h9.5l-2.5 3.5 2.5 3.5H7" fill="currentColor" fill-opacity=".18"/></svg>';
  const mks = () => {
    const sg = song();
    return sg && Array.isArray(sg.markers) ? sg.markers : [];
  };
  const mkById = (id) => mks().find((m) => m.id === id) || null;
  function sortMks() {
    const sg = song();
    if (sg && sg.markers) sg.markers.sort((a, b) => a.t - b.t);
  }
  const curMk = () => (mkCur && cur && mkCur.id === cur.id ? mkById(mkCur.mk) : null);
  const chipLoopOn = (m) => {
    const L = loopNow();
    return !!(L && L.on && L.mk === m.id);
  };
  function chipsHTML() {
    const M = mks(),
      c = curMk();
    if (!M.length) return '';
    return M.map((m, i) => {
      const n = i + 1,
        lab = m.end != null ? fmt1(m.t) + '–' + fmt1(m.end) : fmt1(m.t),
        on = chipLoopOn(m);
      return (
        '<span class="trkchip' +
        (c && c.id === m.id ? ' cur' : '') +
        '" data-mk="' +
        m.id +
        '"><button class="trkchb" data-a="trkChip" data-k="' +
        m.id +
        '" aria-label="Marker ' +
        n +
        ', ' +
        lab +
        (m.name ? ', ' + esc(m.name) : '') +
        '. Tap to jump there, hold for more"><b>' +
        n +
        '</b>' +
        (m.name ? '<span class="trkchn">' + esc(m.name) + '</span>' : '') +
        '<span>' +
        lab +
        '</span></button>' +
        (m.end != null
          ? '<button class="trkchl' +
            (on ? ' on' : '') +
            '" data-a="trkChipLoop" data-k="' +
            m.id +
            '" aria-pressed="' +
            on +
            '" aria-label="Loop marker ' +
            n +
            '">' +
            LOOP +
            '</button>'
          : '') +
        '</span>'
      );
    }).join('');
  }
  // "End n here": sets the current chip's end at the playhead (greyed while the playhead is before its start)
  function endHereHTML() {
    const m = curMk();
    if (!m) return '';
    const n = mks().indexOf(m) + 1,
      ok = now() >= m.t + TRK_MIN - 1e-6;
    return (
      '<button class="cvpill trkendh' +
      (ok ? '' : ' wait') +
      '" id="trkEndH" data-a="trkEndHere" aria-disabled="' +
      !ok +
      '">End ' +
      n +
      ' here</button>'
    );
  }
  // the chip row and the buttons row, in place (the page itself isn't redrawn)
  function chips(added) {
    // Q02: the Markers grid shows the markers as tiles instead
    const gw = grid() && $('trkGrid');
    if (gw) {
      $('trkWave').innerHTML = gridHTML();
      paintTiles();
      if (added && !playing()) {
        const c = document.querySelector('#trkGrid .trktl[data-mk="' + added + '"]');
        if (c)
          MOTION.animate(c, [{ opacity: 0, transform: 'scale(.9)' }, { opacity: 1, transform: 'none' }], {
            spring: 'gentle',
            fade: true,
          });
      }
      return;
    }
    const box = $('trkMk');
    if (!box) return;
    const sl = box.scrollLeft;
    box.innerHTML = chipsHTML();
    box.scrollLeft = sl;
    edgeFade(box);
    endHere();
    if (added && !playing()) {
      const c = box.querySelector('.trkchip[data-mk="' + added + '"]');
      if (c) {
        const r = c.getBoundingClientRect(),
          br = box.getBoundingClientRect();
        if (r.left < br.left || r.right > br.right) box.scrollLeft += r.left - br.left - 16;
        MOTION.animate(c, [{ opacity: 0, transform: 'scale(.8)' }, { opacity: 1, transform: 'none' }], {
          spring: 'gentle',
          fade: true,
        });
      }
    }
  }
  function endHere() {
    const b = $('trkBtns');
    if (!b || !b.querySelector('.trkaddmk')) return;
    const old = $('trkEndH'),
      h = endHereHTML();
    if (!h) {
      if (old) old.remove();
      return;
    }
    const m = curMk(),
      ok = now() >= m.t + TRK_MIN - 1e-6,
      want = 'End ' + (mks().indexOf(m) + 1) + ' here';
    if (old && old.textContent === want) {
      old.classList.toggle('wait', !ok);
      old.setAttribute('aria-disabled', !ok);
      return;
    }
    if (old) old.remove();
    b.querySelector('.trkaddmk').insertAdjacentHTML('afterend', h);
  }
  function addMarker() {
    const sg = song();
    if (!sg || !cur) return;
    const t = r2(Math.min(now(), Math.max(0, len() - 0.01)));
    if (mks().some((m) => Math.abs(m.t - t) < 0.05)) return toast('There’s a marker here already');
    const m = { id: 'm' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5), t };
    sg.markers = mks().concat([m]);
    sortMks();
    mkCur = { id: sg.id, mk: m.id };
    save();
    draw();
    chips(m.id);
  }
  function jump(id) {
    const m = mkById(id);
    if (!m) return;
    mkCur = { id: cur.id, mk: id };
    seek(m.t); // playing carries on from there; paused stays paused
    prevT = m.t;
    document.querySelectorAll('#trkMk .trkchip').forEach((c) => c.classList.toggle('cur', c.dataset.mk === id));
    endHere();
  }
  function endAt(id) {
    const m = mkById(id || (curMk() || {}).id);
    if (!m) return;
    const t = r2(Math.min(now(), len()));
    if (t < m.t + TRK_MIN - 1e-6) return toast('Move the playhead past marker ' + (mks().indexOf(m) + 1) + ' first');
    m.end = t;
    const L = loopNow();
    if (L && L.mk === m.id) {
      L.start = m.t;
      L.end = m.end;
    }
    save();
    draw();
    chips();
  }
  function chipLoop(id) {
    const m = mkById(id),
      sg = song();
    if (!m || m.end == null || !sg) return;
    if (chipLoopOn(m)) sg.loop.on = false;
    else setLoop(m.t, m.end, true, m.id); // only one loop: this one takes over
    mkCur = { id: sg.id, mk: m.id };
    save();
    prevT = now();
    paint();
    draw();
    chips();
  }
  function moveMk(id) {
    const m = mkById(id);
    if (!m) return;
    const t = r2(now()),
      d = m.end != null ? m.end - m.t : 0;
    m.t = t;
    if (m.end != null) {
      m.end = r2(Math.min(len(), t + d));
      if (m.end < t + TRK_MIN) delete m.end;
    }
    const L = loopNow();
    if (L && L.mk === m.id) {
      if (m.end != null) {
        L.start = m.t;
        L.end = m.end;
      } else delete L.mk;
    }
    sortMks();
    save();
  }
  function delMk(id) {
    const sg = song();
    if (!sg) return;
    sg.markers = mks().filter((m) => m.id !== id);
    if (!sg.markers.length) delete sg.markers;
    if (sg.loop && sg.loop.mk === id) delete sg.loop.mk;
    if (mkCur && mkCur.mk === id) mkCur = null;
    save();
  }
  function clearMks() {
    const sg = song();
    if (!sg) return;
    delete sg.markers;
    if (sg.loop) delete sg.loop.mk;
    mkCur = null;
    save();
  }

  /* ----- Q02 the Markers grid's taps ----- */
  // a tile: select it, loop its range (if it's long enough) and play from its start
  function tileTap(id) {
    const m = mkById(id),
      sg = song();
    if (!m || !sg) return;
    const r = rangeOf(m);
    mkCur = { id: sg.id, mk: m.id };
    if (r.ok) setLoop(r.s, r.e, true, m.id);
    else if (sg.loop) sg.loop.on = false; // too short to loop: it just plays from there
    save();
    seek(m.t);
    prevT = m.t;
    play();
    paint();
    draw();
  }
  // a tile's loop button: its loop on or off, without starting anything
  function tileLoop(id) {
    const m = mkById(id),
      sg = song();
    if (!m || !sg) return;
    const r = rangeOf(m);
    if (!r.ok) return toast('Too short to loop: under half a second to the next marker');
    if (chipLoopOn(m)) sg.loop.on = false;
    else setLoop(r.s, r.e, true, m.id);
    mkCur = { id: sg.id, mk: m.id };
    save();
    prevT = now();
    paint();
    draw();
  }
  // the active marker: the one the playhead is in, else the one last tapped
  const activeMk = () => playingMk() || curMk();
  // Replay: back to the start of the active marker, playing
  function replay() {
    const m = activeMk();
    if (!m) return toStart();
    seek(m.t);
    prevT = m.t;
    if (!playing()) play();
    showTile(m.id);
  }
  // Next (Q09): the marker after the active one, in time order (with none active, the first after the playhead); a
  // marker loop moves on to it, otherwise it just goes there. Its tile scrolls into view
  function nextMk() {
    const M = mks(),
      a = activeMk(),
      n = a ? M[M.indexOf(a) + 1] : M.find((m) => m.t > now() + 0.05);
    if (!n) return toast(M.length ? 'That’s the last marker' : 'Add a marker first');
    const L = loopNow();
    if (L && L.on && L.mk) tileTap(n.id);
    else {
      mkCur = { id: cur.id, mk: n.id };
      seek(n.t);
      prevT = n.t;
      if (!playing()) play();
      paint();
    }
    showTile(n.id);
  }
  // a tile into view between the top bar and the dock, smoothly (Reduce Motion or motion off: straight there)
  function showTile(id) {
    const tl = document.querySelector('#trkGrid .trktl[data-mk="' + id + '"]');
    if (!tl) return;
    const r = tl.getBoundingClientRect(),
      top = Math.max(0, $('bar').getBoundingClientRect().bottom) + 8,
      dk = $('dock').firstElementChild,
      bot = (dk ? dk.getBoundingClientRect().top : window.innerHeight) - 8;
    const dy = r.top < top ? r.top - top : r.bottom > bot ? Math.min(r.bottom - bot, r.top - top) : 0;
    if (Math.abs(dy) < 1) return;
    window.scrollTo({ top: Math.max(0, window.scrollY + dy), behavior: MOTION.on() ? 'smooth' : 'auto' });
  }
  // Q09 Backing Sound: in Markers the track can play silently while the playhead, the loop and Next carry on, so you
  // sing the marker on your own. Only on the player, in Markers: any other view, the floating window or a song row is
  // heard, and leaving the player turns it back on (so it's on by default)
  function syncMute() {
    if (!el || along) return;
    const m = mute && here() && grid();
    if (el.muted !== m) el.muted = m;
  }
  function setBacking(on) {
    mute = !on;
    syncMute();
    const b = $('trkSnd');
    if (b) {
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on);
      b.innerHTML = (on ? CKI.sound : CKI.muted) + '<span>Backing Sound</span>';
    }
  }
  // Q09 the Loop pill in Markers: the loop on or off; with no loop yet, the active marker's
  function mdLoop() {
    if (loopNow()) return toggleLoop();
    const m = activeMk();
    if (m) return tileLoop(m.id);
    toast('Tap a marker to loop it');
  }

  /* ----- Q02 a marker becomes a section start (one timing model: written through ckStore) ----- */
  // which places in the running order this marker could start: in time order with the starts already set
  function secChoices(m) {
    const sg = song(),
      S = secStarts(),
      out = [];
    if (!sg || !hasLyrics(sg)) return out;
    sg.order.forEach((x, k) => {
      const before = S.filter((s) => s.k < k && s.t >= m.t - CK_MIN + 1e-6).pop(),
        after = S.find((s) => s.k > k && s.t <= m.t + CK_MIN - 1e-6),
        mine = S.find((s) => s.k === k);
      out.push({
        k,
        label: occLabel(sg, k),
        set: mine ? mine.t : null,
        why: before
          ? 'Must come after ' + before.label + ' (' + fmt1(before.t) + ')'
          : after
            ? 'Must come before ' + after.label + ' (' + fmt1(after.t) + ')'
            : '',
      });
    });
    return out;
  }
  function promote(id, k) {
    const sg = song(),
      m = mkById(id);
    if (!sg || !m || !hasLyrics(sg) || !sg.order[k]) return;
    const ch = secChoices(m)[k];
    if (!ch || ch.why) return toast(ch ? ch.why : 'That section isn’t in the song');
    const t = m.t,
      M = ckModel(sg),
      anch = M.anch.slice();
    // one Undo restores the timing and the marker together
    ckSnap(sg, true);
    // the marker goes: its time is the section's start now
    sg.markers = mks().filter((x) => x.id !== id);
    if (!sg.markers.length) delete sg.markers;
    if (sg.loop && sg.loop.mk === id) delete sg.loop.mk;
    if (mkCur && mkCur.mk === id) mkCur = null;
    anch[k] = true;
    if (ckSynced(sg)) {
      // already timed: this section moves to the marker, the other set starts stay, and the lines between stretch
      const f = (j) => M.T[ckFirst(M.L, j)][0],
        fk = ckFirst(M.L, k),
        pts = [];
      M.anch.forEach((a, j) => a && j !== k && pts.push([f(j), f(j)]));
      pts.push([f(k), t]);
      // Q12: with no set start before it, moving earlier squeezes the lines before it in from 0:00 (never below)
      const lo = Math.min(...M.raw.filter((r) => r[0] != null).map((r) => r[0]));
      if (!pts.some((p) => p[0] < f(k) - 1e-6) && lo - (f(k) - t) < 0) pts.push([0, 0]);
      // Q12: the saved times are warped, never the filled-in estimates, and the section's start lands on the marker
      const w = ckWarp(pts),
        T = M.raw.map((r) => [r[0] == null ? null : w(r[0]), r[1] == null ? null : w(r[1])]),
        pl = M.placed.slice();
      T[fk] = [t, T[fk][1] != null && T[fk][1] > t + CK_MIN ? T[fk][1] : null];
      pl[fk] = true;
      ckStore(sg, M.L, ckOrder(T, pl), anch, M.marks);
    } else {
      // not timed yet: the lines are spread from this start, as Sync by sections does
      const starts = sg.order.map(() => null);
      starts[k] = t;
      ckStore(sg, M.L, ckSpread(sg, M.L, starts), anch, M.marks, { est: true });
    }
    mdl = null;
    ctxAt = null;
    U.sheet = null;
    U.sd = {};
    rerender();
    ckToast(occLabel(sg, k) + ' starts at ' + fmt1(t), ckUndo);
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
  const REPLAY =
    '<svg class="i" viewBox="0 0 24 24"><path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"/><path d="M4.5 4v4.5H9"/></svg>';
  const NEXT = '<svg class="i" viewBox="0 0 24 24"><path d="M5 5l10 7-10 7z" fill="currentColor" stroke="none"/><path d="M18.5 5v14"/></svg>';
  const hint = () =>
    grid()
      ? 'Tap a marker to loop it · hold for more'
      : strip()
        ? (jogPos() === 'bottom' ? 'Drag the roller' : 'Drag the jog wheel') +
          (laneOn() ? ' · tap a line below to select it' : ' · double-tap outside the loop to clear')
        : 'Tap to move the playhead there';
  const mb = (b) => (b / 1048576).toFixed(b >= 10 * 1048576 ? 0 : 1) + ' MB';
  const ROLL = '<svg class="trkjogi" viewBox="0 0 20 12" aria-hidden="true"><path d="M7 2L3 6l4 4M13 2l4 4-4 4"/></svg>';

  function waveHTML() {
    if (grid()) return gridHTML();
    if (strip()) {
      const jp = jogPos();
      return (
        '<div class="trkstrip jog-' +
        jp +
        '" id="trkStrip" data-own-gesture role="slider" tabindex="0" aria-label="Track position" aria-valuetext="' +
        fmt(now()) +
        '"><canvas id="trkC" aria-hidden="true"></canvas>' +
        (jp === 'bottom'
          ? ''
          : '<div class="trkjog" id="trkJog" data-own-gesture aria-hidden="true"><span class="trkjogr"></span>' + JOG + '</div>') +
        '</div>' +
        // Q05 the line lane, lined up under the waveform
        (laneOn()
          ? '<div class="trklane" id="trkLane" data-own-gesture aria-hidden="true"><canvas id="trkLC"></canvas></div>'
          : '') +
        (jp === 'bottom'
          ? '<div class="trkroll" id="trkJog" data-own-gesture aria-hidden="true"><span class="trkrollr"></span>' + ROLL + '</div>'
          : '')
      );
    }
    const rs = TRK_LEVELS[lv()].row,
      d = len(),
      n = Math.max(1, Math.ceil(d / rs - 1e-6)),
      sg = song(),
      lyT = !!(sg && hasLyrics(sg) && timed()),
      lyOn = prefs().trkSongLyrics,
      M = lyOn && timed() ? model() : null;
    // Q09 the Song overview card: its heading, and the Lyrics pill at the top right
    let h =
      '<div class="trksong" id="trkSong"><div class="trksh"><span class="trksht">Whole song<small>' +
      fmt(d) +
      '</small></span>' +
      (lyT
        ? '<button class="cvpill trklyt' +
          (lyOn ? ' on' : '') +
          '" data-a="trkSongLyrics" aria-pressed="' +
          lyOn +
          '">Lyrics</button>'
        : '') +
      '</div><div class="trkrows' +
      (M ? ' ly' : '') +
      '" id="trkRows" data-own-gesture>';
    for (let r = 0; r < n; r++) {
      const a = r * rs,
        b = Math.min(d, (r + 1) * rs);
      h +=
        '<button class="trkrow" data-a="trkRow" data-r="' +
        r +
        '" aria-label="' +
        fmt(a) +
        ' to ' +
        fmt(b) +
        '. Move the playhead here"><span class="trkg">' +
        fmt(a) +
        '</span><canvas aria-hidden="true"></canvas></button>';
      if (M) h += rowLyrics(M, a, r === n - 1 ? Infinity : (r + 1) * rs);
    }
    return h + '</div></div>';
  }
  // Q02 Song: the lines that start in a row, under it; a section's name where it starts. Tap a line to go to it
  function rowLyrics(M, a, b) {
    let h = '';
    M.L.forEach((l, i) => {
      const s = M.T[i][0];
      if (s == null || s < a || s >= b) return;
      if (i === ckFirst(M.L, l.k)) h += '<span class="trkls">' + esc(occLabel(M.sg, l.k)) + '</span>';
      h +=
        '<button class="trkll" data-a="trkLyr" data-v="' +
        s +
        '" aria-label="' +
        esc(l.words.join(' ')) +
        ', at ' +
        fmt(s) +
        '">' +
        esc(l.words.join(' ')) +
        '</button>';
    });
    return h ? '<div class="trkly">' + h + '</div>' : '';
  }
  // Q02 Markers: a tile per marker (tap: play and loop it; its loop button: loop on or off; hold: its menu), then a
  // tile that adds one at the playhead
  function gridHTML() {
    const M = mks();
    // Q10: the tiles sit in a box that measures its own width, so they go three across with room and one without
    let h = '<div class="trkgw"><div class="trkgrid" id="trkGrid">';
    M.forEach((m, i) => {
      const n = i + 1,
        r = rangeOf(m),
        on = chipLoopOn(m),
        lab = fmt1(m.t) + '–' + fmt1(r.e);
      h +=
        '<div class="trktl" data-mk="' +
        m.id +
        '"><button class="trktlb" data-a="trkTile" data-k="' +
        m.id +
        '" aria-label="Marker ' +
        n +
        (m.name ? ', ' + esc(m.name) : '') +
        ', ' +
        lab +
        '. Tap to play' +
        (r.ok ? ' and loop it' : '') +
        ', hold for more"><b>' +
        n +
        '</b><span class="trktn">' +
        esc(m.name || 'Marker ' + n) +
        '</span><span class="trktm">' +
        lab +
        '</span></button><button class="trktlo' +
        (on ? ' on' : '') +
        (r.ok ? '' : ' off') +
        '" data-a="trkTileLoop" data-k="' +
        m.id +
        '" aria-pressed="' +
        on +
        '" aria-label="Loop marker ' +
        n +
        '"' +
        (r.ok ? '' : ' aria-disabled="true"') +
        '>' +
        LOOP +
        '</button></div>';
    });
    h +=
      '<button class="trktl trkqa" data-a="trkMkAdd" aria-label="Add a marker at the playhead">' +
      ICON.plus +
      '<span>Marker at <span id="trkQaT">' +
      fmt1(now()) +
      '</span></span></button></div></div>';
    if (!M.length) h += '<p class="foot trkgf">Add markers while it plays, then tap one to loop it.</p>';
    return h;
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
      '</div><div class="trkbody" id="trkBody">' +
      bodyHTML() +
      '</div><p class="foot trkfoot">' +
      esc(m.name) +
      ' · ' +
      fmt(m.dur) +
      ' · kept on this ' +
      deviceName() +
      ', not in backups</p></div>'
    );
  }
  // everything that changes with the level: the lyric card, the waveform (or the grid), chips and buttons
  function bodyHTML() {
    const g = grid();
    ctxAt = null;
    return (
      (strip() ? ctxHTML() : '') +
      '<div class="trkwave" id="trkWave">' +
      waveHTML() +
      '</div><div class="trkinfo' +
      (laneOn() && laneSel() >= 0 ? ' lsel' : '') +
      '" id="trkInfo" aria-live="polite">' +
      infoInner() +
      '</div>' +
      (g ? '' : '<div class="trkmk" id="trkMk" data-own-gesture data-edge-fade>' + chipsHTML() + '</div>') +
      (g
        ? ''
        : '<div class="trkchips" id="trkBtns"><button class="cvpill" data-a="trkSet" data-v="start">Set start</button><button class="cvpill" data-a="trkSet" data-v="end">Set end</button><button class="cvpill trkaddmk" data-a="trkMkAdd" aria-label="Add marker at the playhead">' +
          MKI +
          'Marker</button>' +
          endHereHTML() +
          '<span class="sp"></span>' +
          spdHTML() +
          '</div>')
    );
  }
  const spdHTML = () =>
    '<button class="cvpill trkspd" id="trkSpd" data-a="trkSpeed" aria-label="Speed ' +
    spTxt(speed()) +
    '. Tap to change">' +
    spTxt(speed()) +
    '</button>';
  // redraw the level's parts in place (the page itself and its scroll stay)
  function body() {
    const b = $('trkBody');
    if (!b) return;
    b.innerHTML = bodyHTML();
    draw();
    paint();
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
    // Q09 Markers: three wide pads (Replay the marker, Play/Pause, Next marker) under a floating row of pills
    // (Backing Sound and Loop). Phrase, Line and Song keep the round transport below
    if (grid()) {
      const lo = !!(L && L.on);
      return (
        '<div class="trkmd" role="group" aria-label="Markers"><div class="trkmp"><button class="trkpill glass' +
        (mute ? '' : ' on') +
        '" id="trkSnd" data-a="trkSnd" aria-pressed="' +
        !mute +
        '">' +
        (mute ? CKI.muted : CKI.sound) +
        '<span>Backing Sound</span></button><button class="trkpill trkpl glass' +
        (lo ? ' on' : '') +
        '" id="trkLoopB" data-a="trkMdLoop" aria-pressed="' +
        lo +
        '" aria-label="Loop">' +
        LOOP +
        '<span>Loop</span></button></div><div class="trkpads"><button class="trkpad glass" data-a="trkReplay" aria-label="Replay this marker">' +
        REPLAY +
        '</button><button class="trkpad trkpadpp" id="trkPP" data-a="trkPP" data-on="' +
        on +
        '" aria-label="' +
        (on ? 'Pause' : 'Play') +
        '">' +
        (on ? ICON.pause : ICON.play) +
        '</button><button class="trkpad glass" data-a="trkNext" aria-label="Next marker">' +
        NEXT +
        '</button></div></div>'
      );
    }
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
          '"><span class="lbl dng">Remove track</span></button></div>' +
          (sg.markers && sg.markers.length
            ? '<div class="grp"><button class="row" data-a="sheet" data-v="trkMkClear"><span class="lbl dng">Clear all markers…</span></button></div>'
            : '') +
          // Q02: which side the jog wheel sits on (this device only)
          '<div class="hdr">Jog wheel</div><div class="grp" role="radiogroup" aria-label="Jog wheel">' +
          [
            ['left', 'Left'],
            ['right', 'Right'],
            ['bottom', 'Bottom roller'],
          ]
            .map(
              (j) =>
                '<button class="row" data-a="trkJogPos" data-v="' +
                j[0] +
                '" role="radio" aria-checked="' +
                (jogPos() === j[0]) +
                '"><span class="lbl">' +
                j[1] +
                '</span><span class="acc setchk" aria-hidden="true">' +
                (jogPos() === j[0] ? ICON.check : '') +
                '</span></button>'
            )
            .join('') +
          '</div>' +
          '<p class="foot">Stays on this ' +
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
    const sd = U.sd || {};
    if (s === 'trkMkMenu' && sg) {
      const m = (sg.markers || []).find((x) => x.id === sd.k);
      if (!m) return '';
      const n = sg.markers.indexOf(m) + 1;
      const row = (a, l, cls) =>
        '<button class="row" data-a="' + a + '" data-k="' + m.id + '"><span class="lbl' + (cls ? ' ' + cls : '') + '">' + l + '</span></button>';
      return sheetWrap(
        'Marker ' + n,
        // Q02: the first door from a marker into the song's timing
        (hasLyrics(sg)
          ? '<div class="grp"><button class="row" data-a="trkMkSec" data-k="' +
            m.id +
            '"><span class="lbl acc">Make this a section start…<small>' +
            fmt1(m.t) +
            ' becomes where a section starts in Song Clock</small></span>' +
            chev +
            '</button></div>'
          : '') +
          '<div class="grp">' +
          row('trkMkRename', 'Rename', 'acc') +
          row('trkMkMove', 'Move to playhead', 'acc') +
          (m.end != null ? row('trkMkNoEnd', 'Remove end', 'acc') : row('trkMkEnd', 'Set end here', 'acc')) +
          row('trkMkDel', 'Delete marker', 'dng') +
          '</div><div class="grp"><button class="row" data-a="sheet" data-v="trkMkClear"><span class="lbl dng">Clear all markers…</span></button></div>',
        'Marker ' + n
      );
    }
    // Q02 the section picker: places in the running order, those that would break the time order greyed with why
    if (s === 'trkMkSec' && sg) {
      const m = (sg.markers || []).find((x) => x.id === sd.k);
      if (!m || !hasLyrics(sg)) return '';
      const C2 = secChoices(m);
      return sheetWrap(
        'Section start',
        '<p class="note trksecn">Marker ' +
          (sg.markers.indexOf(m) + 1) +
          ' at ' +
          fmt1(m.t) +
          '. Pick the section that starts here. The marker becomes its start, and Undo puts it back.</p><div class="grp">' +
          C2.map(
            (c) =>
              '<button class="row' +
              (c.why ? ' off' : '') +
              '" data-a="trkMkSecPick" data-k="' +
              m.id +
              '" data-v="' +
              c.k +
              '"' +
              (c.why ? ' aria-disabled="true"' : '') +
              '><span class="lbl">' +
              esc(c.label) +
              '<small>' +
              esc(c.why || (c.set != null ? 'Starts at ' + fmt1(c.set) + ' now' : 'Not set yet')) +
              '</small></span>' +
              (c.set != null && !c.why ? '<span class="trkadot" aria-label="Start set"></span>' : '') +
              '</button>'
          ).join('') +
          '</div>',
        'Section start'
      );
    }
    if (s === 'trkMkName' && sg) {
      const m = (sg.markers || []).find((x) => x.id === sd.k);
      if (!m) return '';
      return sheetWrap(
        'Rename marker',
        '<input class="field" id="trkMkIn" maxlength="60" placeholder="Run into the chorus" autocomplete="off" value="' +
          esc(m.name || '') +
          '"><div style="margin-top:14px"><button class="cta" data-a="trkMkSaveName" data-k="' +
          m.id +
          '">Save</button></div>'
      );
    }
    if (s === 'trkMkClear' && sg)
      return confirmSheet(
        'Clear all markers?',
        'All ' + ((sg.markers || []).length || '') + ' markers on this song are removed. The loop stays.',
        'Clear all markers',
        'trkMkClearYes',
        sg.id
      );
    if (s === 'trkPast' && past) {
      const n = (c, w) => c + ' ' + w + (c === 1 ? '' : 's');
      return sheetWrap(
        'Past the new end',
        '<p class="note">The new track is ' +
          fmt(past.dur) +
          '. ' +
          [past.mk ? n(past.mk, 'marker') : '', past.ln ? n(past.ln, 'line') : ''].filter(Boolean).join(' and ') +
          (past.mk + past.ln === 1 ? ' is' : ' are') +
          ' past its end. Keep them for when you swap back, or trim them to the new track.</p>' +
          '<button class="cta red" data-a="trkPastTrim">Trim to the new track</button><button class="ghost" data-a="trkPastKeep">Keep them</button>'
      );
    }
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
    want = id === 'draft' ? { draft: true } : { id };
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
  // read a picked file: its length and waveform (the Add sheet keeps this until Save, so nothing is left behind)
  async function read(file) {
    try {
      return await analyse(await file.arrayBuffer());
    } catch (e) {
      return null;
    }
  }
  // 3.20: Song Clock's length follows the track. A song with no length (or the same one) links to it; a different
  // length stays the song's own (shown with a broken link). Replacing: a linked length follows the new file
  function linkLen(sg, dur, replacing) {
    const L = Math.round(dur);
    if (!(L > 0) || L > CK_MAXLEN) return;
    const t = sg.timing;
    if (replacing && t && t.lenLink) t.len = L;
    else if (!t || !t.len) {
      if (!sg.timing) sg.timing = { len: null, real: false, est: false, slots: {} };
      sg.timing.len = L;
      sg.timing.lenLink = true;
    } else if (t.len === L) t.lenLink = true;
    else delete t.lenLink;
  }
  // store a read file as a song's track (the audio and its peaks, in vocalTracks)
  async function attach(sg, file, r) {
    const rec = {
      name: String(file.name || 'Track').slice(0, 200),
      size: file.size,
      type: file.type || '',
      dur: r.dur,
      added: Date.now(),
      blob: file,
    };
    await tx(['audio', 'peaks'], 'readwrite', (a, p) => {
      a.put(rec, sg.id);
      p.put({ p: r.peaks, rate: TRK_RATE, dur: r.dur }, sg.id);
    });
    const old = sg.track && sg.track.dur;
    // Q12: a shorter track: one Undo puts the timing, markers and loop back as they were
    const shorter = !!old && r.dur < old - 0.05;
    if (shorter) ckSnap(sg, true);
    if (cur && cur.id === sg.id) unload(); // replaced: the new audio and peaks load fresh
    delete pos[sg.id];
    sg.track = { name: rec.name, dur: r2(r.dur) };
    linkLen(sg, r.dur, !!old);
    // the loop is trimmed to the new end (or dropped if nothing's left)
    if (sg.loop) {
      const l = cleanLoop(sg.loop, r.dur);
      if (l) sg.loop = l;
      else delete sg.loop;
    }
    // Q12: markers and lines past the new end are checked the same way, and kept until Ivan picks Keep or Trim
    const mk = (sg.markers || []).filter((m) => m.t > r.dur || (m.end != null && m.end > r.dur)).length,
      ln = ckPast(sg, r.dur);
    past = shorter && (mk || ln) ? { id: sg.id, dur: r.dur, mk, ln } : null;
    if (sg.markers && !past) {
      const m = cleanMarkers(sg.markers, r.dur);
      if (m) sg.markers = m;
      else delete sg.markers;
    }
    have.set(sg.id, metaOf(rec));
    return { old, shorter };
  }
  // Q12: Keep (everything past the end stays, for swapping back to the longer mix) or Trim (markers past it go, lines
  // past it lose their time with a to-do marker, and nothing ends after it). Both have the replace's Undo
  function pastDo(trim) {
    const p = past,
      sg = p && songById(p.id);
    past = null;
    U.sheet = null;
    U.sd = {};
    if (!sg) return rerender();
    if (trim) {
      if (sg.markers) {
        const m = cleanMarkers(sg.markers, p.dur);
        if (m) sg.markers = m;
        else delete sg.markers;
      }
      ckTrim(sg, p.dur);
    }
    save();
    mdl = null;
    rerender();
    ckToast(trim ? 'Trimmed to the new track' : 'Kept everything past the end', ckUndo);
  }
  async function add(file, target, ok) {
    if (!file || busy || !target) return;
    if (!ok && file.size > TRK_BIG) {
      big = { file, want: target };
      U.sheet = 'trkBig';
      U.sd = target.draft ? { ret: { sheet: 'sgNew', sd: {} } } : {};
      return rerender();
    }
    busy = { id: target.id || null, draft: !!target.draft };
    showBusy(!target.draft);
    if (target.draft) {
      // 3.20 the Add sheet: read the file, keep it with the draft, and show the form
      const d = U.sDraft;
      if (d) d.reading = file.name || 'track';
      U.sheet = 'sgNew';
      rerender();
      const r = await read(file);
      busy = null;
      const d2 = U.sDraft;
      if (d2) delete d2.reading;
      if (!r) {
        rerender();
        return toast(TRK_BAD);
      }
      if (d2) SG_ACT.sgMedia(file, r);
      else rerender();
      return;
    }
    rerender();
    const r = await read(file);
    const fail = (msg) => {
      busy = null;
      showBusy(false);
      rerender();
      toast(msg);
    };
    if (!r) return fail(TRK_BAD);
    const sg = songById(target.id);
    if (!sg) return fail('That song was deleted');
    let old, shorter;
    try {
      ({ old, shorter } = await attach(sg, file, r));
    } catch (e) {
      return fail('Couldn’t save the track. Storage may be full.');
    }
    save();
    busy = null;
    showBusy(false);
    if (U.view === 'trk' && U.songId === sg.id) {
      U.sheet = null;
      rerender();
    } else open(sg.id);
    if (past && past.id === sg.id) {
      // Q12: ask what to do with what's past the new end (nothing is deleted while it asks)
      U.sheet = 'trkPast';
      U.sd = { k: sg.id };
      return rerender();
    }
    ckToast(old && Math.abs(old - r.dur) > 1 ? TRK_LENGTH : 'Track added', shorter ? ckUndo : null);
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
      delete sg.track; // the loop, markers and timings stay with the song
      if (sg.timing) delete sg.timing.lenLink; // 3.20: the length is kept, no longer linked
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
  // Q05 Retime: the player in Line view, the playhead on line i and its block selected. Pushed in from the song page or
  // Check timing (iPhone), and Back returns there
  function retime(id, i, t) {
    if (!songById(id)) return;
    if (rec) return toast('Stop recording first');
    const from = U.view;
    prefs().trkLevel = 1;
    saveSGP();
    lane = { id, i };
    pos[id] = Math.max(0, +t || 0);
    if (cur && cur.id === id) seek(pos[id]);
    if (from === 'lyr' || from === 'ckCheck') ZOOM.armPush('trk:retime');
    go(() => {
      U.tab = 'songs';
      U.view = 'trk';
      U.songId = id;
      U.sheet = null;
      U.sd = {};
    });
    ret = from === 'ckCheck' ? 'ckCheck' : null;
  }
  // Back goes to the song's page (Q05: or to Check timing, when Retime came from there)
  function back() {
    const id = U.songId,
      ok = !!songById(id),
      r = ret;
    ret = null;
    go(() => {
      U.tab = 'songs';
      U.view = ok && r === 'ckCheck' ? 'ckCheck' : ok && !split() ? 'lyr' : null;
      U.sheet = null;
      U.sd = {};
    });
  }
  // Q05: the song's timing changed under the player (a line placed): redraw what shows it, in place
  function refresh() {
    mdl = null;
    ctxAt = null;
    if (!here()) return;
    draw();
    paint();
    laneBar();
  }

  /* ----- after every redraw ----- */
  function after() {
    // the song went (deleted, Reset all data, a restore without it): stop and let go of its audio
    if (cur && !songById(cur.id)) unload();
    mdl = null; // Q02: the song's timing is read again after any change
    ctxAt = null;
    if (!here()) mute = false; // Q09: Backing Sound is on again whenever you come back
    if (U.view !== 'trk') ret = null;
    if (lane && (U.view !== 'trk' || lane.id !== U.songId)) lane = null;
    syncMute();
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

  /* ----- 3.20 holding a chip opens its menu ----- */
  document.addEventListener('pointerdown', (e) => {
    const c = e.target.closest && e.target.closest('#trkMk .trkchb, #trkGrid .trktlb');
    if (!c || e.button > 0) return;
    const id = c.dataset.k,
      x = e.clientX,
      y = e.clientY;
    clearTimeout(mkHold && mkHold.t);
    mkHold = {
      id,
      x,
      y,
      done: false,
      t: setTimeout(() => {
        if (!mkHold || mkHold.id !== id) return;
        mkHold.done = true;
        U.sheet = 'trkMkMenu';
        U.sd = { k: id };
        rerender();
      }, 500),
    };
  });
  document.addEventListener('pointermove', (e) => {
    if (mkHold && !mkHold.done && Math.hypot(e.clientX - mkHold.x, e.clientY - mkHold.y) > 10) {
      clearTimeout(mkHold.t);
      mkHold = null;
    }
  });
  let mkHeldAt = 0;
  ['pointerup', 'pointercancel'].forEach((t) =>
    document.addEventListener(t, () => {
      if (!mkHold) return;
      if (mkHold.done) mkHeldAt = Date.now();
      else clearTimeout(mkHold.t);
      mkHold = null;
    })
  );
  // a hold that opened the menu isn't also a tap (on the chip, or on the menu that rose under the finger)
  document.addEventListener(
    'click',
    (e) => {
      if (Date.now() - mkHeldAt < 400) {
        e.stopPropagation();
        e.preventDefault();
      }
    },
    true
  );
  document.addEventListener('contextmenu', (e) => {
    if (e.target.closest && e.target.closest('#trkMk, #trkGrid')) e.preventDefault();
  });

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
    // Q05 the line lane: an edge drags (and moves its neighbour's matching edge); anywhere else scrubs, or a tap selects
    const ln = e.target.closest && e.target.closest('#trkLane');
    if (ln) {
      const p = laneX(e);
      if (!p) return;
      e.preventDefault();
      const hit = laneHit(p.x, p.w) || { kind: 'lane', i: -1 };
      drag = { kind: hit.kind, id: e.pointerId, x: e.clientX, y: e.clientY, t: now(), at: Date.now(), moved: 0, w: p.w };
      if (hit.kind === 'edge') {
        const T = laneT();
        Object.assign(drag, { a: hit.a, b: hit.b, W: T.map((r) => r.slice()), O: T.map((r) => r.slice()) });
      } else drag.i = hit.i;
      try {
        ln.setPointerCapture(e.pointerId);
      } catch (x) {}
      ln.classList.add('drag');
      return;
    }
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
      // down moves later, up earlier; slow drags are precise, quick ones skim. Q02 the bottom roller: right is later
      const bot = jogPos() === 'bottom',
        d = bot ? dx : dy;
      seek(drag.t + (d * (TRK_LEVELS[lv()].win || 16)) / TRK_JOG);
      const j = $('trkJog');
      if (j) {
        j.dataset.rot = drag.rot + d;
        const r = j.querySelector(bot ? '.trkrollr' : '.trkjogr');
        if (r) r.style[bot ? 'backgroundPositionX' : 'transform'] = bot ? drag.rot + d + 'px' : 'rotate(' + (drag.rot + d) + 'deg)';
      }
    } else if (drag.kind === 'scrub' || drag.kind === 'lane') {
      if (drag.moved > 2) seek(drag.t - dx / pps(drag.w));
    } else if (drag.kind === 'edge') {
      const p = laneX(e);
      if (p && drag.moved > 2) laneMove(now() + (p.x - p.w * TRK_HEAD) / pps(p.w));
    } else if (drag.kind === 'handle') {
      const p = stripX(e);
      if (p) dragHandle(now() + (p.x - p.w * TRK_HEAD) / pps(p.w));
    }
  });
  const endDrag = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag;
    drag = null;
    document.querySelectorAll('#trkStrip.drag, #trkJog.drag, #trkLane.drag').forEach((x) => x.classList.remove('drag'));
    // Q05 the lane: a drag of an edge is saved (with Undo) on release; a tap selects a block, or clears the selection
    if (d.kind === 'edge') {
      if (e.type === 'pointerup' && d.moved2) {
        drag = d; // laneCommit reads the working copy
        laneCommit();
        drag = null;
        draw(); // the lane from the saved timing, not the working copy
      } else if (d.moved < 8) laneSelect(d.b != null ? d.b : d.a);
      else draw();
      return;
    }
    if (d.kind === 'lane') {
      if (e.type === 'pointerup' && d.moved < 8 && Date.now() - d.at < 500) laneSelect(d.i);
      return;
    }
    if (d.kind === 'handle') {
      // 3.20: a chip's loop being fine-tuned: the chip follows the handles
      const L = loopNow(),
        m = L && L.mk ? mkById(L.mk) : null;
      if (m) {
        m.t = L.start;
        m.end = L.end;
        sortMks();
        chips();
      }
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
  // a row: the playhead goes there, and the view stays as it is (3.20: zoom changes with the level pills, or a pinch)
  function rowTap(btn, e) {
    const cv = btn.querySelector('canvas');
    if (!cv) return;
    const r = cv.getBoundingClientRect(),
      rs = TRK_LEVELS[lv()].row,
      x = e && e.clientX ? Math.max(0, Math.min(r.width, e.clientX - r.left)) : 0;
    seek(+btn.dataset.r * rs + (x / Math.max(1, r.width)) * rs);
  }
  // after a change of level, the playhead's time is in view (the strips put it at the 40% playhead anyway)
  function showHead() {
    if (strip()) return;
    const rs = TRK_LEVELS[lv()].row,
      row = document.querySelector('#app .trkrow[data-r="' + Math.floor(now() / rs) + '"]');
    if (!row) return;
    const r = row.getBoundingClientRect(),
      top = Math.max(0, $('bar').getBoundingClientRect().bottom),
      dk = $('dock').firstElementChild,
      bot = dk ? dk.getBoundingClientRect().top : window.innerHeight;
    if (r.top < top || r.bottom > bot) window.scrollTo(0, Math.max(0, window.scrollY + r.top - (top + bot) / 2 + r.height / 2));
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
  // the keyboard on a Mac or iPad: Space plays, arrows move, I and O set the start and end (as in Final Cut Pro).
  // Through KEYS (Q13): never while typing or with a sheet or picker open; a held Space, I or O counts once (holding
  // Space used to flutter play/pause), a held arrow keeps moving
  const trkKey = (e, keys) => U.view === 'trk' && !!cur && !e.metaKey && !e.ctrlKey && !e.altKey && keys.includes(e.key.toLowerCase());
  KEYS.add({ when: (e) => trkKey(e, [' ']), run: () => toggle() });
  KEYS.add({
    repeat: true,
    when: (e) => trkKey(e, ['arrowleft', 'arrowright']),
    run: (e) => seek(now() + (e.key === 'ArrowLeft' ? -1 : 1) * (e.shiftKey ? 5 : 1)),
  });
  KEYS.add({ when: (e) => trkKey(e, ['i', 'o']), run: (e) => setAt(e.key.toLowerCase() === 'i' ? 'start' : 'end') });
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
    close() {
      pause();
      woke = false;
      paintRows();
    },
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
    trkPastKeep() {
      pastDo(false);
    },
    trkPastTrim() {
      pastDo(true);
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
    trkMkAdd() {
      addMarker();
    },
    trkChip(el, v, k) {
      jump(k);
    },
    trkChipLoop(el, v, k) {
      chipLoop(k);
    },
    trkEndHere() {
      endAt();
    },
    trkMkRename(el, v, k) {
      U.sheet = 'trkMkName';
      U.sd = { k };
      rerender();
      setTimeout(() => {
        const i = $('trkMkIn');
        if (i) i.focus();
      }, 60);
    },
    trkMkSaveName(el, v, k) {
      const m = mkById(k),
        i = $('trkMkIn');
      if (m && i) {
        const n = i.value.trim().slice(0, 60);
        if (n) m.name = n;
        else delete m.name;
        save();
      }
      U.sheet = null;
      U.sd = {};
      rerender();
    },
    trkMkMove(el, v, k) {
      moveMk(k);
      U.sheet = null;
      U.sd = {};
      rerender();
    },
    trkMkEnd(el, v, k) {
      U.sheet = null;
      U.sd = {};
      rerender();
      endAt(k);
    },
    trkMkNoEnd(el, v, k) {
      const m = mkById(k),
        sg = song();
      if (m) delete m.end;
      if (sg && sg.loop && sg.loop.mk === k) delete sg.loop.mk;
      save();
      U.sheet = null;
      U.sd = {};
      rerender();
    },
    trkMkDel(el, v, k) {
      delMk(k);
      U.sheet = null;
      U.sd = {};
      rerender();
      toast('Marker deleted');
    },
    trkMkClearYes() {
      clearMks();
      U.sheet = null;
      U.sd = {};
      rerender();
      toast('Markers cleared');
    },
    // 3.20 a song row's play button: the song's track through the player's audio
    sgRowPlay(el, v, k) {
      playSong(k);
    },
    // Q02 the Markers grid and its transport
    trkTile(el, v, k) {
      tileTap(k);
    },
    trkTileLoop(el, v, k) {
      tileLoop(k);
    },
    trkReplay() {
      replay();
    },
    trkNext() {
      nextMk();
    },
    // Q09 the Markers dock's pills
    trkSnd() {
      setBacking(mute);
      toast(mute ? 'Backing sound off' : 'Backing sound on');
    },
    trkMdLoop() {
      mdLoop();
    },
    // Q02 a marker into a section start
    trkMkSec(el, v, k) {
      U.sheet = 'trkMkSec';
      U.sd = { k };
      rerender();
    },
    trkMkSecPick(el, v, k) {
      promote(k, +v);
    },
    // Q02 the jog wheel's side, and lyrics under the Song rows
    trkJogPos(el, v) {
      if (!TRK_JOGS.includes(v)) return;
      prefs().trkJogPos = v;
      saveSGP();
      rerender();
    },
    trkSongLyrics() {
      const p = prefs();
      p.trkSongLyrics = !p.trkSongLyrics;
      saveSGP();
      body();
      showHead();
    },
    trkLyr(el, v) {
      seek(+v);
      prevT = now();
    },
    // Q05 the line lane's row
    trkLnStart() {
      laneAt('start');
    },
    trkLnEnd() {
      laneAt('end');
    },
    trkLnX() {
      laneSelect(-1);
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
    bytes: () => {
      let s = 0;
      have.forEach((m) => (s += +m.size || 0));
      return s;
    },
    open,
    back,
    retime,
    refresh,
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
      want = id === 'draft' ? { draft: true } : { id };
    },
    has: (id) => have.has(id),
    meta: (id) => (have.get(id) ? Object.assign({}, have.get(id)) : null),
    busy: () => !!busy,
    el: () => el,
    now,
    len,
    level: lv,
    speed,
    markers: () => mks().map((m) => Object.assign({}, m)),
    addMarker,
    jump,
    endAt,
    chipLoop,
    playSong,
    rowPlay,
    paintRows,
    read,
    attach,
    linkLen,
    peaks: () => (cur ? cur.peaks : null),
    // Q02
    along: alongPlay,
    alongPause,
    alongNow,
    alongMute,
    following: () => (along ? along.id : null),
    promote,
    secChoices: (id) => {
      const m = mkById(id);
      return m ? secChoices(m) : [];
    },
    secStarts: () => secStarts().map((s) => ({ k: s.k, t: s.t, label: s.label })),
    rangeOf: (id) => {
      const m = mkById(id);
      return m ? rangeOf(m) : null;
    },
    tileTap,
    tileLoop,
    replay,
    nextMk,
    // Q09
    backing: () => !mute,
    setBacking,
    mdLoop,
    wraps: () => wraps.map((w) => Object.assign({}, w)),
    jogPos,
    ctx: () => ctxLines(),
    // Q05 the line lane
    laneSel: () => laneSel(),
    laneSelect,
    laneAt,
    laneTimes: () => laneT().map((r) => r.slice()),
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
      along: along ? along.id : null,
      muted: !!(el && el.muted),
    }),
  };
})();
