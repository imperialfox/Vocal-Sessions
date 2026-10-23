/* Vocal Sessions · session.js
   Running a session: steps, the clock, finishing and editing; recording takes.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Session logic ===== */
function newSession() {
  X = {
    kind: 'focused',
    start: Date.now(),
    f: {},
    xn: {},
    fEnd: null,
    rot: {},
    rEnd: null,
    song: null,
    rate: {},
    takes: [],
    how: [],
    howNote: '',
    pausedTotal: 0,
  };
  saveDraft();
}
function newSong() {
  const last = D.songSessions.length ? D.songSessions[D.songSessions.length - 1].songId : null;
  X = {
    kind: 'song',
    start: null, // set when the first take starts recording
    f: {},
    xn: {},
    rot: {},
    song: D.songs.some((s) => s.id === last) ? last : null,
    rate: {},
    takes: [],
    how: [],
    howNote: '',
    pausedTotal: 0,
  };
  saveDraft();
}
// leaving song practice before its first take drops it quietly: nothing was timed, so there's nothing to keep
function dropUnstarted() {
  if (unstarted() && U.view !== 'song' && !rec) {
    X = null;
    saveDraft();
    U.clock = false;
  }
}
// a first take that came to nothing leaves song practice untimed again
function unstartIfNoTakes(r) {
  if (!r.o && isSong() && X.start === r.started && !(X.takes || []).length) {
    X.start = null;
    X.paused = false;
    X.pausedTotal = 0;
    U.clock = false;
    saveDraft();
  }
}
function togglLines(ss) {
  const how = howStr(ss);
  if (ss.kind === 'song') {
    const n = (ss.takes || []).length;
    return (
      'Song practice' +
      (ss.songName ? ': ' + ss.songName : '') +
      (n ? ', ' + n + ' take' + (n > 1 ? 's' : '') : '') +
      (how ? ' — ' + how : '') +
      ' ' +
      TOGGL.song
    );
  }
  const L = [],
    xn = ss.xn || {};
  L.push(
    'Foundation: ' +
      FOUND.map((e) => {
        const lv = (ss.f || {})[e.id],
          n = noteStr(xn[e.id]);
        return e.name + (lv ? ' L' + lv : ' skipped') + (n ? ' (' + n + ')' : '');
      }).join(', ') +
      (ss.fNote ? ' — ' + ss.fNote : '') +
      ' ' +
      TOGGL.foundation
  );
  Object.keys(ss.rot || {}).forEach((id) => {
    const e = exById(id) || { name: (ss.rotNames || {})[id] || 'Exercise', focus: 'custom' };
    const n = noteStr(xn[id]);
    L.push(
      e.name +
        ' L' +
        ss.rot[id] +
        '/3' +
        (n ? ' — ' + n : '') +
        (ss.rNote ? ' — ' + ss.rNote : '') +
        ' ' +
        TOGGL.rotation +
        ' #' +
        e.focus
    );
  });
  const r = ss.rate || {};
  const rt = ['Pitch', 'Tone', 'Ease']
    .filter((x) => r[x])
    .map((x) => x.toLowerCase() + ' ' + r[x])
    .join(', ');
  L.push('Application' + (ss.songName ? ': ' + ss.songName : '') + (rt ? ' — ' + rt : '') + ' ' + TOGGL.application);
  if (how) L.push('How it went: ' + how);
  return L.join('\n');
}
// Finish: long-session check (over 90 min), then "How did it go?", then save
function startFinish() {
  U.clock = false;
  U.noteOpen = null;
  X.minsOverride = null;
  U.sheet = elapsedSec() > LONG_MINS * 60 ? 'long' : 'how';
  U.sd = {};
  saveDraft();
  rerender();
}
function finishSession() {
  const zc = ZOOM.finishing(); // a still of the session, to shrink back into Start session once Today is drawn
  const end = Date.now(),
    mins = finalMins();
  const song = D.songs.find((s) => s.id === X.song);
  const base = {
    id: 's' + end.toString(36),
    date: new Date(X.start).toISOString(),
    end: new Date(end).toISOString(),
    mins,
    how: (X.how || []).slice(),
    howNote: (X.howNote || '').trim(),
    songName: song ? song.name : '',
    takes: X.takes || [],
  };
  if (X.kind === 'song') {
    const ss = Object.assign(base, { kind: 'song', songId: X.song });
    D.songSessions.push(ss);
    save();
    X = null;
    saveDraft();
    U.view = null;
    U.tab = 'today';
    U.clock = false;
    U.noteOpen = null;
    U.sheet = 'songDone';
    U.sd = { k: ss.id };
    window.scrollTo(0, 0);
    render();
    ZOOM.finished(zc, 'songStart');
    return;
  }
  const rotNames = {};
  Object.keys(X.rot).forEach((id) => {
    const e = exById(id);
    if (e) rotNames[id] = e.name;
  });
  const e = Math.max(1, elapsedSec()),
    fE = Math.min(e, X.fE || 0),
    rE = Math.min(e, Math.max(fE, X.rE || fE)),
    sc = (mins * 60) / e;
  const mixed = fE < QUICK_STEP || rE - fE < QUICK_STEP; // a step under 2 minutes means the levels were filled in afterwards
  const ss = Object.assign(
    base,
    { f: X.f, fNote: X.fNote || '', rot: X.rot, rNote: X.rNote || '', rotNames, xn: X.xn || {}, rate: X.rate, mixed },
    mixed
      ? {}
      : {
          split: {
            f: Math.round((fE * sc) / 6) / 10,
            r: Math.round(((rE - fE) * sc) / 6) / 10,
            a: Math.round(((e - rE) * sc) / 6) / 10,
          },
        }
  );
  D.sessions.push(ss);
  DET.finished();
  const k = monthKey(new Date(X.start));
  D.months[k] = (D.months[k] || 0) + mins;
  exIds(ss).forEach((id) => {
    D.ex[id] = D.ex[id] || { n: 0, last: null };
    D.ex[id].n++;
    D.ex[id].last = ss.end;
  });
  save();
  X = null;
  saveDraft();
  U.view = null;
  U.tab = 'today';
  U.clock = false;
  U.noteOpen = null;
  U.sheet = 'done';
  U.sd = { k: ss.id };
  window.scrollTo(0, 0);
  render();
  ZOOM.finished(zc, 'start');
}
function deleteSession(id) {
  const ss = D.sessions.find((x) => x.id === id);
  if (!ss) return;
  D.sessions = D.sessions.filter((x) => x !== ss);
  const mk = monthKey(new Date(ss.date));
  D.months[mk] = Math.max(0, (D.months[mk] || 0) - ss.mins);
  exIds(ss).forEach((ex) => {
    const e = D.ex[ex];
    if (!e) return;
    e.n = Math.max(0, e.n - 1);
    e.last = lastFor(ex);
  });
  save();
}
// Save an edited session: recompute monthly minutes, exercise counts and last-done dates
function applyEdit() {
  const song = E.kind === 'song',
    arr = song ? D.songSessions : D.sessions,
    ss = arr.find((x) => x.id === E.id);
  if (!ss) return;
  const oldIds = song ? [] : exIds(ss),
    oldMonth = monthKey(new Date(ss.date)),
    oldMins = ss.mins;
  const od = new Date(ss.date),
    nd = new Date(od);
  if (/^\d{4}-\d{2}-\d{2}$/.test(E.dateStr || '')) {
    const p = E.dateStr.split('-').map(Number);
    nd.setFullYear(p[0], p[1] - 1, p[2]);
  }
  const shift = nd - od,
    mins = Math.max(1, Math.min(600, Math.round(+E.mins) || ss.mins));
  ss.date = nd.toISOString();
  if (ss.end) ss.end = new Date(new Date(ss.end).getTime() + shift).toISOString();
  ss.mins = mins;
  ss.how = (E.how || []).slice();
  ss.howNote = (E.howNote || '').trim();
  if (!song) {
    ss.f = E.f;
    ss.rot = E.rot;
    ss.xn = E.xn || {};
    ss.rate = E.rate || {};
    if (E.mixed || !E.split) {
      ss.mixed = true;
      delete ss.split;
    } else {
      const f = Math.max(0, Math.round(+E.split.f) || 0),
        r = Math.max(0, Math.round(+E.split.r) || 0);
      ss.mixed = false;
      ss.split = { f, r, a: Math.max(0, mins - f - r) };
    }
  }
  arr.sort((a, b) => new Date(a.date) - new Date(b.date));
  if (!song) {
    D.months[oldMonth] = Math.max(0, (D.months[oldMonth] || 0) - oldMins);
    const nk = monthKey(nd);
    D.months[nk] = (D.months[nk] || 0) + mins;
    const newIds = exIds(ss);
    new Set(oldIds.concat(newIds)).forEach((id) => {
      const e = (D.ex[id] = D.ex[id] || { n: 0, last: null });
      e.n = Math.max(0, (e.n || 0) + (newIds.includes(id) ? 1 : 0) - (oldIds.includes(id) ? 1 : 0));
      e.last = lastFor(id);
    });
  }
  save();
}
function closeSheet() {
  const s = U.sheet;
  if (s === 'exNote') {
    const T = noteTarget(),
      n = T && T.xn && T.xn[U.sd.k];
    if (n && typeof n === 'object') {
      n.t = (n.t || '').trim();
      if (!n.w.length && !n.t) delete T.xn[U.sd.k];
    }
    if (T && T === X) saveDraft();
  }
  if (s === 'takeNote') {
    const t = TAKES.find((x) => x.id === U.sd.k);
    if (t && t.note) {
      t.note.t = (t.note.t || '').trim();
      putTake(t).catch(() => toast('Couldn’t save the note'));
    }
  }
  if (s === 'edit') E = null;
  if (s === 'sgTakes' && !takePlaying(playingId)) stopPlayback(); // a playing take carries on, in the floating window
  const r = U.sd && U.sd.ret;
  if (typeof r === 'string') {
    U.sheet = r;
    U.sd = {};
  } else if (r && r.sheet) {
    U.sheet = r.sheet;
    U.sd = r.sd || {};
  } else U.sheet = null;
  U.noteOpen = null;
  pendingImport = null;
  rerender();
}

// pause or carry on with the session's clock (the clock overlay and the floating window)
function togglePause() {
  if (!X || !X.start) return;
  if (X.paused) {
    X.pausedTotal = (X.pausedTotal || 0) + (Date.now() - X.pausedAt);
    X.paused = false;
  } else {
    X.paused = true;
    X.pausedAt = Date.now();
  }
  saveDraft();
}

/* ===== Recording ===== */
function pickMime() {
  if (!window.MediaRecorder) return '';
  const c = ['audio/mp4;codecs=mp4a.40.2', 'audio/mp4', 'audio/aac', 'audio/webm;codecs=opus', 'audio/webm'];
  return (
    c.find((m) => {
      try {
        return MediaRecorder.isTypeSupported(m);
      } catch (e) {
        return false;
      }
    }) || ''
  );
}
// target: {songId, o} for a section of a song; nothing for song practice (the song picked in the session)
let recBusy = false;
async function startRec(target) {
  const tg = target || { songId: X && X.song };
  if (rec || recBusy) return;
  COACH.pause(); // the coach video stops before a recording starts
  if (typeof TRACK !== 'undefined') TRACK.pause(); // and the song's track (3.19)
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    toast('Recording isn’t supported in this browser');
    return;
  }
  recBusy = true;
  let stream;
  try {
    // voice processing off, so the take sounds like the voice in the room
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: false, noiseSuppression: false, autoGainControl: false },
    });
  } catch (e) {
    recBusy = false;
    toast('Microphone access was blocked. Allow it in Settings, then try again.');
    return;
  }
  recBusy = false;
  const mime = pickMime();
  let mr;
  try {
    // AAC mono at about 96 kbps where the browser offers it
    mr = new MediaRecorder(stream, Object.assign({ audioBitsPerSecond: 96000 }, mime ? { mimeType: mime } : {}));
  } catch (e) {
    mr = new MediaRecorder(stream);
  }
  rec = { mr, stream, chunks: [], t: 0, songId: tg.songId, o: tg.o || null, started: Date.now() };
  // song practice's clock starts with its first take
  if (!rec.o && unstarted()) {
    X.start = rec.started;
    X.paused = false;
    X.pausedTotal = 0;
    saveDraft();
  }
  mr.ondataavailable = (e) => {
    if (e.data && e.data.size) rec && rec.chunks.push(e.data);
  };
  mr.onstop = saveRec;
  mr.start(1000);
  rec.timer = setInterval(() => {
    if (!rec) return;
    rec.t = Math.round((Date.now() - rec.started) / 1000);
    const l = $('recLbl');
    if (l) l.textContent = 'Stop · ' + mmss(rec.t) + ' of ' + mmss(MAX_TAKE);
    const c = $('recT');
    if (c) c.textContent = mmss(rec.t);
    if (rec.t >= MAX_TAKE) stopRec();
  }, 250);
  if (rec.o) {
    recMeter(rec);
    U.sSec = rec.o;
  }
  rerender();
  if (rec.o) scrollToSec(rec.o);
}
// the level meter in the recording bar: the last few moments of loudness, newest on the right
function recMeter(r) {
  r.lv = [];
  try {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    r.ac = new AC();
    const an = r.ac.createAnalyser();
    an.fftSize = 512;
    r.ac.createMediaStreamSource(r.stream).connect(an);
    if (r.ac.state === 'suspended') r.ac.resume().catch(() => {});
    const buf = new Uint8Array(an.fftSize);
    r.mt = setInterval(() => {
      if (rec !== r) return;
      an.getByteTimeDomainData(buf);
      let sum = 0;
      for (let i = 0; i < buf.length; i++) sum += (buf[i] - 128) * (buf[i] - 128);
      r.lv.push(Math.min(1, (Math.sqrt(sum / buf.length) / 128) * 4));
      if (r.lv.length > 14) r.lv.shift();
      const bars = document.querySelectorAll('#recMeter i'),
        off = bars.length - r.lv.length;
      bars.forEach((b, i) => (b.style.height = Math.round(16 + (i < off ? 0 : r.lv[i - off]) * 84) + '%'));
    }, 90);
  } catch (e) {}
}
function scrollToSec(o) {
  const s = document.querySelector('.sgsec[data-o="' + o + '"]');
  if (!s) return;
  const bar = $('bar'),
    top = bar ? bar.getBoundingClientRect().bottom : 70;
  window.scrollTo({ top: Math.max(0, s.getBoundingClientRect().top + window.scrollY - top - 12), behavior: 'smooth' });
}
function stopRec() {
  if (!rec || rec.stopping) return;
  rec.stopping = true;
  clearInterval(rec.timer);
  clearInterval(rec.mt);
  if (rec.ac) rec.ac.close().catch(() => {});
  try {
    rec.mr.stop();
  } catch (e) {
    saveRec();
  }
  rec.stream.getTracks().forEach((t) => t.stop());
}
async function saveRec() {
  const r = rec;
  rec = null;
  if (!r) return;
  const type = (r.mr && r.mr.mimeType) || (r.chunks[0] && r.chunks[0].type) || 'audio/mp4';
  const blob = new Blob(r.chunks, { type });
  const len = Math.max(1, Math.round((Date.now() - r.started) / 1000));
  if (blob.size < 1000) {
    unstartIfNoTakes(r);
    toast('That take was empty. Try again.');
    rerender();
    return;
  }
  const t = Object.assign(
    {
      id: 't' + Date.now().toString(36),
      songId: r.songId,
      created: Date.now(),
      len,
      size: blob.size,
      type,
      star: false,
      blob,
    },
    r.o ? { o: r.o } : {} // the place in the song it was sung from (an entry in the song's order)
  );
  let saved = false;
  try {
    await putTake(t);
    saved = true;
    if (X && !r.o) {
      X.takes.push(t.id);
      saveDraft();
    }
  } catch (e) {
    unstartIfNoTakes(r);
    toast('Couldn’t save the take. Storage may be full.');
  }
  await prune(r.songId);
  await refreshTakes();
  const song = saved && D.songs.find((s) => s.id === r.songId);
  if (song) {
    song.practised = t.created; // practised means a take was recorded
    save();
  }
  // straight to the review sheet, layered over the song, if it's still on screen
  const sh = saved && r.o && songShown();
  if (sh && sh.id === r.songId && !U.sheet) {
    U.sheet = 'sgTakes';
    U.sd = { k: r.songId, o: r.o, fresh: t.id };
  }
  rerender();
  if (U.sd && U.sd.fresh === t.id) DET.takeIn();
}
async function prune(songId) {
  const loose = (await allTakes()).filter((t) => t.songId === songId && !t.star).sort((a, b) => b.created - a.created);
  for (const t of loose.slice(KEEP_TAKES)) await delTake(t.id);
}
function stopPlayback() {
  if (player) {
    const p = player;
    player = null; // first, so its pause doesn't redraw the window
    p.pause();
    URL.revokeObjectURL(p.src);
  }
  playingId = null;
  FW.take = null;
}
// a take that's playing now (not paused from the floating window)
const takePlaying = (id) => !!(id && playingId === id && player && !player.paused);
function playTake(id) {
  COACH.pause(); // one sound at a time
  if (typeof TRACK !== 'undefined') TRACK.pause();
  if (playingId === id && player) {
    // paused from the floating window: carry on from there; playing: stop, as before
    if (player.paused) FW_KINDS[0].toggle();
    else {
      stopPlayback();
      rerender();
    }
    return;
  }
  stopPlayback();
  const t = TAKES.find((x) => x.id === id);
  if (!t) return;
  player = new Audio(URL.createObjectURL(t.blob));
  playingId = id;
  FW.take = { id, place: fwHere() }; // where to come back to from the floating window
  player.onplay = player.onpause = () => {
    if (player !== p) return;
    // its own play button shows the change; elsewhere only the floating window does
    if (document.querySelector('[data-a=playTake][data-k="' + id + '"]')) rerender();
    else fwUpdate();
  };
  player.onended = () => {
    stopPlayback();
    rerender();
  };
  player.play().catch(() => {
    stopPlayback();
    toast('Couldn’t play this take');
    rerender();
  });
  rerender();
  const p = player;
  const tick = () => {
    if (player !== p) return;
    const el = $('pg-' + id),
      d = isFinite(p.duration) && p.duration > 0 ? p.duration : t.len || 1;
    if (el) el.style.width = Math.min(100, (p.currentTime / d) * 100) + '%';
    if (FW.shown === 'take') fwTick();
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
function downloadFile(file) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(file);
  a.download = file.name;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    URL.revokeObjectURL(a.href);
    a.remove();
  }, 4000);
}
async function shareFile(file) {
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title: file.name });
      return 'shared';
    } catch (e) {
      if (e && e.name === 'AbortError') return 'cancelled';
    }
  }
  downloadFile(file);
  return 'downloaded';
}
function shareTake(id) {
  const t = TAKES.find((x) => x.id === id);
  if (!t) return;
  const song = D.songs.find((s) => s.id === t.songId);
  const ext = /mp4|aac|m4a/.test(t.type) ? 'm4a' : /webm/.test(t.type) ? 'webm' : 'audio';
  const name =
    ((song ? song.name : 'Vocal take') + ' – ' + fileDate(new Date(t.created))).replace(/[\/\\:*?"<>|]/g, '-') +
    '.' +
    ext;
  shareFile(new File([t.blob], name, { type: t.type }));
}
