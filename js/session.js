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
  // Q19: a fresh page: no boxes open, nothing reopened, the coach window at each step's default
  U.rings = {};
  U.fEdit = null;
  U.cvWin = null;
  saveDraft();
  SCLOCK.started(); // Q22: the screen stays on, and the clock notes the app is on screen
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
// Finish: long-session check (over 90 min), then save. Q20: a focused session no longer asks "How did it go?" (its
// words can still be added on the session's edit sheet); song practice still does
function startFinish() {
  U.clock = false;
  U.noteOpen = null;
  X.minsOverride = null;
  U.sheet = elapsedSec() > LONG_MINS * 60 ? 'long' : isSong() ? 'how' : null;
  U.sd = {};
  saveDraft();
  if (!U.sheet) return finishSession();
  rerender();
}
// after the long-session check: song practice asks how it went, a focused session is saved
function afterLong() {
  if (!isSong()) return finishSession();
  U.sheet = 'how';
  rerender();
}
function finishSession() {
  // song practice shrinks back into its card (a still of it, taken now); a focused session lands on Session saved (Q21)
  const zc = ZOOM.finishing(X.kind !== 'song');
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
  // Q19 "Just Foundation today? Finish here" from an empty Rotation: Rotation ends now, as its button would have
  // ended it, so Application gets no time (the split is worked out exactly as before)
  if (U.finHere && X.fEnd && !X.rEnd) {
    X.rEnd = Date.now();
    X.rE = elapsedSec();
  }
  U.finHere = false;
  const e = Math.max(1, elapsedSec()),
    fE = Math.min(e, X.fE || 0),
    rE = Math.min(e, Math.max(fE, X.rE || fE)),
    sc = (mins * 60) / e;
  const mixed = fE < QUICK_STEP || rE - fE < QUICK_STEP; // a step under 2 minutes means the levels were filled in afterwards
  // Q20: the song Application practised, its section, and whether it was practised without a take (Carry on reads it)
  if (song) {
    const sp = X.sing && X.sing.id === song.id ? X.sing : null,
      app = { song: song.id };
    if (sp && sp.o) app.o = sp.o;
    if (!(X.takes || []).some((k) => (TAKES.find((t) => t.id === k) || {}).songId === song.id)) app.noRec = true;
    base.ext = { app };
  }
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
  // Q21: the Session saved screen, which Done turns into Today (saved.js). The session's own sheet is still a tap
  // away on Today's calendar and in All sessions
  U.view = 'saved';
  U.saved = { k: ss.id };
  U.tab = 'today';
  U.clock = false;
  U.noteOpen = null;
  U.sheet = null;
  U.sd = {};
  window.scrollTo(0, 0);
  render();
  ZOOM.finished(zc);
  SAVED.enter();
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
  if (s === 'how' || s === 'long') U.finHere = false; // Q19: Finish here only counts if the session is saved
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
  SCLOCK.paused(); // Q22: the screen may sleep while paused, and stays on again (with its chip) on Resume
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
// target: {songId, o} for a section of a song; nothing for song practice (the song picked in the session).
// over: how Ivan said he's listening when the track is playing ('hp' headphones, 'spk' the speaker), from recOverSheet
let recBusy = false;
async function startRec(target, over) {
  const tg = target || { songId: X && X.song };
  if (rec || recBusy) return;
  // Q16: the song's track may keep playing under a recording, the one exception to one sound at a time. It's for
  // headphones: the app can't tell whether they're in, so it asks first (recOverSheet), unless he said headphones while
  // this play of the track has kept going. Through the speaker it asks every time
  const onTrack = trackUnder(),
    keep = onTrack && (over === 'hp' || over === 'spk' || REC_OVER.hp);
  if (onTrack && !keep) return askOver(tg);
  if (!keep) NOW.stop(); // one sound at a time (3.20): whatever plays stops before a recording starts
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    toast('Recording isn’t supported in this browser');
    return;
  }
  recBusy = true;
  AUDIO.wake(); // in the tap: iOS only starts the shared audio context from one
  let stream;
  try {
    // voice processing off, so the take sounds like the voice in the room
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: false, noiseSuppression: false, autoGainControl: false },
    });
  } catch (e) {
    recBusy = false;
    AUDIO.rest(); // nothing to listen to: the context rests again
    toast('Microphone access was blocked. Allow it in Settings, then try again.');
    return;
  }
  const mic = AUDIO.listen(stream), // Q16: the microphone, heard once through the shared audio service
    mono = await monoStream(stream, mic); // 3.20: one channel, so takes play in both ears
  recBusy = false;
  const mime = pickMime();
  let mr;
  try {
    // AAC mono at about 96 kbps where the browser offers it
    mr = new MediaRecorder(mono.stream, Object.assign({ audioBitsPerSecond: 96000 }, mime ? { mimeType: mime } : {}));
  } catch (e) {
    mr = new MediaRecorder(mono.stream);
  }
  rec = {
    mr,
    stream,
    mono,
    mic,
    chunks: [],
    t: 0,
    songId: tg.songId,
    o: tg.o || null,
    started: Date.now(),
    over: keep ? over || 'hp' : null, // Q16: recorded over the track ('hp' or 'spk')
    app: !!tg.app, // Q20: sung in Application: its card is the recording, and the take joins the session
    from: keep && tg.from != null ? tg.from : null, // Q20: where the track started
  };
  NOW.start('rec', null, () => stopRec(), keep ? 'track' : null);
  // 3.20: a take on any song page starts (or carries on) song practice for that song, timed from its first take
  if (rec.o && !rec.app && songById(rec.songId)) {
    if (!X) {
      newSong();
      X.song = rec.songId;
    }
    if (isSong() && X.song === rec.songId) rec.sp = true;
  }
  // song practice's clock starts with its first take
  if ((!rec.o || rec.sp) && unstarted()) {
    X.start = rec.started;
    X.paused = false;
    X.pausedTotal = 0;
    saveDraft();
    SCLOCK.started(true); // Q22: the screen stays on (no chip over the take that's starting)
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
    if (FW.shown === 'rectrack') fwTick(); // Q20: the red track window's time
    if (rec.t >= MAX_TAKE) stopRec();
  }, 250);
  if (rec.app) recMeter(rec);
  else if (rec.o) {
    recMeter(rec);
    U.sSec = rec.o;
  }
  rerender();
  if (rec.o && !rec.app) scrollToSec(rec.o);
  if (rec.app) {
    // the card is the recording: it comes into view if it's out of it, then nothing moves
    const c = $('apcard'),
      r = c && c.getBoundingClientRect();
    if (r && (r.top < 70 || r.bottom > window.innerHeight - 150))
      window.scrollTo({ top: Math.max(0, window.scrollY + r.top - 90), behavior: MOTION.on() ? 'smooth' : 'auto' });
  }
}

/* ===== Recording over the track (Q16) =====
   The song's track (the track player's sound, NOW kind 'track') may carry on while a take is recorded: NOW keeps it
   playing under the recording, and stopping the take leaves it playing. Everything else still stops. With voice
   processing off, the track through the speaker would be heard in the take, so it's for headphones by default and
   asks first. Saying headphones is remembered only while the track keeps playing: it's forgotten when the track
   pauses (iOS pauses it when headphones come out), when audio devices change and when the app goes to the background. */
const REC_OVER = { hp: false, mine: 0 }; // mine (Q20): when the app itself last paused the track
const trackUnder = () =>
  NOW.kind() === 'track' && typeof TRACK !== 'undefined' && TRACK.state().playing && !TRACK.state().along;
function askOver(tg) {
  U.sheet = 'recOver';
  U.sd = { tg: Object.assign({}, tg) };
  rerender();
}
function recOverSheet() {
  return sheetWrap(
    'Record over the track?',
    '<p class="note">The track keeps playing while you record. Use headphones, so only your voice is in the take. Through the speaker, the track may be heard in the take.</p>' +
      '<button class="cta" data-a="recOver" data-v="hp">Record with headphones</button>' +
      '<button class="ghost" data-a="recOver" data-v="spk">Record through the speaker</button>'
  );
}
// the sheet's buttons: record now, the track carrying on
function recOver(v) {
  const tg = (U.sd || {}).tg;
  U.sheet = null;
  U.sd = {};
  // Q20 Sing over the track: Application starts the track itself, then records (application.js)
  if (tg && tg.sing) {
    rerender();
    return APPL.over(tg, v === 'hp' ? 'hp' : 'spk');
  }
  if (v === 'hp') hpSaid();
  rerender();
  if (tg) startRec(tg, v === 'hp' ? 'hp' : 'spk');
}
// Q20: a pause the app makes itself (Application's take ending, or a take about to play) isn't headphones coming
// out, so the answer is kept for ↻ Again; any other pause, a change of audio devices or leaving the app forgets it
function hpSaid() {
  REC_OVER.hp = true;
  const v = typeof TRACK !== 'undefined' && TRACK.el(),
    onPause = () => {
      if (Date.now() - REC_OVER.mine < 500) {
        if (REC_OVER.hp && v) v.addEventListener('pause', onPause, { once: true });
        return;
      }
      REC_OVER.hp = false;
    };
  if (v) v.addEventListener('pause', onPause, { once: true });
  try {
    navigator.mediaDevices.addEventListener('devicechange', () => (REC_OVER.hp = false), { once: true });
  } catch (e) {}
}
document.addEventListener('visibilitychange', () => {
  if (document.hidden) REC_OVER.hp = false;
});

// the level meter in the recording bar: the last few moments of loudness, newest on the right. Q16: it listens through
// the shared audio service and draws on its one frame clock, a new level about every 90 ms; its bars are found again
// only when the bar has been drawn again, never looked up each time
function recMeter(r) {
  r.lv = [];
  const an = r.mic && r.mic.analyser(512);
  if (!an) return;
  const buf = new Uint8Array(an.fftSize);
  let next = 0,
    bars = null;
  r.meterOff = AUDIO.frame((ts) => {
    if (rec !== r || r.stopping) return r.meterOff && r.meterOff();
    if (ts < next) return;
    next = ts + 90;
    r.lvAt = ts; // when it last listened
    an.getByteTimeDomainData(buf);
    let sum = 0;
    for (let i = 0; i < buf.length; i++) sum += (buf[i] - 128) * (buf[i] - 128);
    r.lv.push(Math.min(1, (Math.sqrt(sum / buf.length) / 128) * 4));
    if (r.lv.length > 14) r.lv.shift();
    if (!bars || !bars.length || !bars[0].isConnected) bars = document.querySelectorAll('#recMeter i');
    const off = bars.length - r.lv.length;
    bars.forEach((b, i) => (b.style.height = Math.round(16 + (i < off ? 0 : r.lv[i - off]) * 84) + '%'));
  });
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
  NOW.ended('rec');
  if (rec.app && rec.over) APPL.quietPause(); // Q20: the track was for this take; it stops with it
  clearInterval(rec.timer);
  if (rec.meterOff) rec.meterOff();
  try {
    rec.mr.stop();
  } catch (e) {
    saveRec();
  }
  rec.stream.getTracks().forEach((t) => t.stop());
  if (rec.mono && rec.mono.close) rec.mono.close();
  if (rec.mic) rec.mic.close(); // Q16: lets go of the shared context, which rests once nothing listens
}
// 3.20: the microphone mixed down to one channel before it's encoded (a headset can give the voice on one side only).
// Anything that doesn't work falls back to the microphone as it is, so a take is never lost to this. Q16: through the
// shared audio service (mic: the recording's AUDIO.listen(), else one made and let go of here)
async function monoStream(stream, mic) {
  const plain = { stream };
  let own = null;
  try {
    const tr = stream.getAudioTracks()[0],
      st = tr && tr.getSettings ? tr.getSettings() : {};
    if (st.channelCount === 1) return plain; // already one channel
    const m = mic || (own = AUDIO.listen(stream));
    if (!m) return plain;
    if (!(await AUDIO.wake())) {
      if (own) own.close();
      return plain;
    }
    const out = m.mono();
    return { stream: out, close: () => own && own.close() };
  } catch (e) {
    if (own) own.close();
    return plain;
  }
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
  // which practice it belongs to, so a take saved later (Retry) only joins the practice it was recorded in
  const xs = X && X.start;
  let saved = false;
  try {
    await putTake(t);
    saved = true;
  } catch (e) {
    // Q11: the take isn't lost. It stays here, with its audio, and the toast offers Retry
    keepUnsaved(t, r, xs);
  }
  if (saved) tookTake(t, r, xs);
  if (saved && UNSAVED.length) retryUnsaved(); // there's room again: save any take still waiting
  await refreshTakes(); // 3.20: every take is kept; nothing is removed automatically
  if (saved) analyseTake(t);
  // straight to the review sheet, layered over the song, if it's still on screen
  const sh = saved && r.o && !r.app && songShown();
  if (sh && sh.id === r.songId && !U.sheet) {
    U.sheet = 'sgTakes';
    U.sd = { k: r.songId, o: r.o, fresh: t.id };
  }
  rerender();
  if (U.sd && U.sd.fresh === t.id) DET.takeIn();
  if (saved && r.app) APPL.arrived(t.id);
}
// a saved take joins its practice (if that's still the one running) and marks its song as practised
function tookTake(t, r, xs) {
  if (X && X.start === xs && (!r.o || r.app || (r.sp && isSong() && X.song === r.songId))) {
    if (!X.takes.includes(t.id)) X.takes.push(t.id);
    if (r.app && !isSong()) X.song = r.songId; // Q20: the song Application practised
    saveDraft();
  }
  const song = D.songs.find((s) => s.id === r.songId);
  if (song) {
    song.practised = Math.max(+song.practised || 0, t.created); // practised means a take was recorded
    save();
  }
}
const analyseTake = (t) => typeof TAKE !== 'undefined' && TAKE.analyse(t.id); // its waveform, once, on this device

/* ===== Takes that couldn't be saved (Q11) =====
   A take whose save fails (storage full, or the database stopped it) stays here in memory, audio and all, and a toast
   offers Retry. If the toast goes before it's tapped, the take is tried again when the app comes back to the screen
   and after the next take saves, and the toast comes back if it still can't be saved. */
const UNSAVED = []; // [{t, r, xs}]
function keepUnsaved(t, r, xs) {
  if (!UNSAVED.some((u) => u.t.id === t.id)) UNSAVED.push({ t, r, xs });
  askRetry();
}
function askRetry(again) {
  if (!UNSAVED.length) return;
  const n = UNSAVED.length;
  toastBtn(
    (again ? 'Still couldn’t save ' : 'Couldn’t save ') +
      (n > 1 ? n + ' takes' : 'the take') +
      '. Storage may be full.',
    'Retry',
    () => retryUnsaved(true),
    12000
  );
}
let retrying = false;
async function retryUnsaved(asked) {
  if (retrying || !UNSAVED.length) return;
  retrying = true;
  let done = 0;
  const ok = [];
  for (const u of UNSAVED.slice()) {
    try {
      await putTake(u.t);
    } catch (e) {
      continue;
    }
    UNSAVED.splice(UNSAVED.indexOf(u), 1);
    tookTake(u.t, u.r, u.xs);
    ok.push(u.t);
    done++;
  }
  retrying = false;
  if (done) {
    await refreshTakes();
    ok.forEach(analyseTake);
    rerender();
  }
  if (UNSAVED.length) {
    if (asked || done) askRetry(true);
  } else if (done) toast(done > 1 ? done + ' takes saved' : 'Take saved');
}
document.addEventListener('visibilitychange', () => {
  if (!document.hidden && UNSAVED.length) retryUnsaved(true);
});
function stopPlayback() {
  if (player) {
    const p = player;
    player = null; // first, so its pause doesn't redraw the window
    p.pause();
    URL.revokeObjectURL(p.src);
  }
  if (playingId) NOW.ended('take', playingId);
  playingId = null;
  FW.take = null;
  if (typeof TAKE !== 'undefined') TAKE.stopped();
}
// a take that's playing now (not paused from the floating window)
const takePlaying = (id) => !!(id && playingId === id && player && !player.paused);
function playTake(id, at) {
  if (playingId === id && player) {
    // paused from the floating window: carry on from there (from 0:00 if it had finished); playing: stop, as before
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
  nowTake(id); // one sound at a time (3.20)
  // 3.20: an older take with its voice on one side plays a copy made for both ears (the original is never changed)
  const src = typeof TAKE !== 'undefined' ? TAKE.blobFor(t) : t.blob;
  player = new Audio(URL.createObjectURL(src));
  playingId = id;
  if (at > 0) {
    const p0 = player;
    p0.addEventListener('loadedmetadata', () => {
      try {
        if (player === p0) p0.currentTime = Math.min(at, Math.max(0, (isFinite(p0.duration) ? p0.duration : t.len) - 0.1));
      } catch (e) {}
    }, { once: true });
  }
  FW.take = { id, place: fwHere() }; // where to come back to from the floating window
  player.onplay = player.onpause = (e) => {
    if (player !== p) return;
    if (e && e.type === 'pause' && !p.ended) fwPaused('take');
    if (typeof TAKE !== 'undefined') TAKE.paint();
    // its own play button shows the change; elsewhere only the floating window does
    if (APPL.inPlace()) APPL.paint(); // Q20: the take rows change in place, so Compare's knob can slide
    else if (document.querySelector('[data-a=playTake][data-k="' + id + '"]') && !(typeof TAKE !== 'undefined' && TAKE.inPlace()))
      rerender();
    else fwUpdate();
  };
  player.onended = () => {
    if (player !== p) return;
    stopPlayback();
    rerender();
  };
  player.play().catch(() => {
    if (player !== p) return;
    stopPlayback();
    toast('Couldn’t play this take');
    rerender();
  });
  const p = player;
  if (typeof TAKE !== 'undefined' && TAKE.inPlace()) TAKE.paint();
  else if (APPL.inPlace()) APPL.paint();
  else rerender();
  const tick = () => {
    if (player !== p) return;
    const el = $('pg-' + id),
      d = isFinite(p.duration) && p.duration > 0 ? p.duration : t.len || 1;
    if (el) el.style.width = Math.min(100, (p.currentTime / d) * 100) + '%';
    // some recordings never say they've ended (iOS can report no length): past the take's length, it has
    if (!p.paused && !isFinite(p.duration) && t.len && p.currentTime > t.len + 0.5) {
      stopPlayback();
      rerender();
      return;
    }
    if (typeof TAKE !== 'undefined') TAKE.frame(p);
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
