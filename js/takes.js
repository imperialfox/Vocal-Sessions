/* Vocal Sessions · takes.js
   3.20: a song's takes in one sheet. A switch between the section's takes and All takes; each take expands to a
   waveform scrubber, ±5 s, its name (renamed in place) and timestamped comments that pop up as the playhead passes.
   Swipe a row right to star it, left to delete it, or hold it for both. Every take is kept: nothing is removed
   automatically, and Settings › Storage › Review old takes lists the ones that are safe to clear.
   Names and comments live with the song (sg.takeNotes), so they're in every backup, even with Exclude recordings.
   On this device only (vocalTakeExtras): each take's waveform peaks, read once, and for an older take whose voice is
   on one side only, a copy made for both ears. The original recording is never changed.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Checking saved names and comments (used by cleanSong in songs.js) =====
   sg.takeNotes = {<take id>: {name?, comments?: [{t, text}]}}: a name up to 60 characters, comments up to 200
   characters at a time 0 or more, sorted by time. Anything malformed is dropped. */
const TK_NAME = 60,
  TK_TEXT = 200,
  TK_MAXC = 300;
function cleanTakeNotes(n) {
  if (!n || typeof n !== 'object' || Array.isArray(n)) return null;
  const out = {};
  Object.keys(n)
    .slice(0, 2000)
    .forEach((id) => {
      const v = n[id];
      if (!id || id.length > 40 || !v || typeof v !== 'object' || Array.isArray(v)) return;
      const o = {};
      if (typeof v.name === 'string' && v.name.trim()) o.name = v.name.trim().slice(0, TK_NAME);
      if (Array.isArray(v.comments)) {
        const c = v.comments
          .filter(
            (x) =>
              x &&
              typeof x === 'object' &&
              typeof x.t === 'number' &&
              isFinite(x.t) &&
              x.t >= 0 &&
              typeof x.text === 'string' &&
              x.text.trim()
          )
          .map((x) => ({ t: Math.round(x.t * 10) / 10, text: x.text.trim().slice(0, TK_TEXT) }))
          .sort((a, b) => a.t - b.t)
          .slice(0, TK_MAXC);
        if (c.length) o.comments = c;
      }
      if (o.name || o.comments) out[id] = o;
    });
  return Object.keys(out).length ? out : null;
}

const TAKE = (() => {
  const RATE = 50; // waveform peaks a second
  const ext = new Map(); // take id → {p: Uint8Array, rate, dur, side: 0|1|null, bad}
  const mono = new Map(); // take id → a both-ears copy (Blob), for a take whose voice is on one side
  const reading = new Set();
  let openId = null; // the expanded take
  let tab = null; // the sheet's switch: 'sec' or 'all'
  const pos = {}; // where each take's playhead was left (not playing)
  let prevT = 0; // the last frame's time, so a comment pops up only when playback passes it
  let pop = null; // {text, until}
  let draft = null; // the comment being typed: {id, text, t, edit: index|null, nudge}
  let renaming = null; // the take being renamed in place
  let scrub = null;
  let sw = null; // a row being swiped or held
  let C = null;

  /* ----- stored on the device: waveform peaks and both-ears copies (never in backups) ----- */
  let dbp = null;
  function xdb() {
    if (dbp) return dbp;
    dbp = new Promise((res, rej) => {
      if (!window.indexedDB) return rej(new Error('no idb'));
      const r = indexedDB.open('vocalTakeExtras', 1);
      r.onupgradeneeded = () => {
        const d = r.result;
        if (!d.objectStoreNames.contains('peaks')) d.createObjectStore('peaks');
        if (!d.objectStoreNames.contains('mono')) d.createObjectStore('mono');
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
  async function xtx(stores, mode, fn) {
    const d = await xdb();
    return new Promise((res, rej) => {
      const t = d.transaction(stores, mode);
      const out = fn(...stores.map((s) => t.objectStore(s)));
      t.oncomplete = () => res(out && out.result !== undefined ? out.result : undefined);
      t.onerror = () => rej(t.error);
      t.onabort = () => rej(t.error);
    });
  }
  const okExt = (r) => r && r.p instanceof Uint8Array && +r.rate > 0;
  // at launch (boot.js): what's already been worked out; then any take not yet read is read, one at a time
  async function load() {
    try {
      const d = await xdb();
      for (const st of ['peaks', 'mono'])
        await new Promise((res) => {
          const t = d.transaction(st, 'readonly'),
            c = t.objectStore(st).openCursor();
          c.onsuccess = () => {
            const k = c.result;
            if (!k) return;
            if (typeof k.key === 'string') {
              if (st === 'peaks' && okExt(k.value)) ext.set(k.key, k.value);
              if (st === 'mono' && k.value instanceof Blob && k.value.size > 0) mono.set(k.key, k.value);
            }
            k.continue();
          };
          t.oncomplete = res;
          t.onerror = res;
          t.onabort = res;
        });
    } catch (e) {}
    setTimeout(backlog, 1500);
  }
  // older takes, read in the background (at most one at a time), so every one plays in both ears soon
  async function backlog() {
    const ids = new Set(TAKES.map((t) => t.id));
    const gone = [...ext.keys(), ...mono.keys()].filter((id) => !ids.has(id));
    if (gone.length) forgetExtras(gone);
    for (const t of TAKES.slice().reverse()) {
      if (ext.has(t.id) || reading.has(t.id)) continue;
      await analyse(t.id);
      await new Promise((r) => setTimeout(r, 120));
    }
  }
  function decode(buf) {
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!OAC) return Promise.reject(new Error('no audio'));
    let ctx = null;
    for (const r of [22050, 44100])
      try {
        ctx = new OAC(2, 1, r);
        break;
      } catch (e) {}
    if (!ctx) return Promise.reject(new Error('no audio'));
    return new Promise((res, rej) => {
      try {
        const p = ctx.decodeAudioData(buf, res, rej);
        if (p && p.then) p.then(res, rej);
      } catch (e) {
        rej(e);
      }
    });
  }
  // a 16-bit mono WAV of one channel: the voice, for both ears
  function wav(ch, rate) {
    const n = ch.length,
      b = new ArrayBuffer(44 + n * 2),
      v = new DataView(b),
      w = (o, s) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
    w(0, 'RIFF');
    v.setUint32(4, 36 + n * 2, true);
    w(8, 'WAVE');
    w(12, 'fmt ');
    v.setUint32(16, 16, true);
    v.setUint16(20, 1, true);
    v.setUint16(22, 1, true);
    v.setUint32(24, rate, true);
    v.setUint32(28, rate * 2, true);
    v.setUint16(32, 2, true);
    v.setUint16(34, 16, true);
    w(36, 'data');
    v.setUint32(40, n * 2, true);
    for (let i = 0; i < n; i++) {
      const s = Math.max(-1, Math.min(1, ch[i]));
      v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }
    return new Blob([b], { type: 'audio/wav' });
  }
  // a take's waveform and channels, read once. A take with its voice on one side only gets a both-ears copy
  async function analyse(id) {
    if (ext.has(id) || reading.has(id)) return;
    const t = TAKES.find((x) => x.id === id);
    if (!t || !(t.blob instanceof Blob)) return;
    reading.add(id);
    let r = null,
      m = null;
    try {
      const ab = await decode(await t.blob.arrayBuffer());
      if (!ab || !ab.length) throw new Error('empty');
      const per = ab.sampleRate / RATE,
        n = Math.max(1, Math.ceil(ab.length / per)),
        raw = new Float32Array(n),
        rms = [];
      for (let c = 0; c < ab.numberOfChannels; c++) {
        const d = ab.getChannelData(c);
        let sq = 0;
        for (let i = 0; i < n; i++) {
          const a = Math.floor(i * per),
            b = Math.min(d.length, Math.floor((i + 1) * per));
          let mx = raw[i];
          for (let j = a; j < b; j++) {
            const v = d[j] < 0 ? -d[j] : d[j];
            if (v > mx) mx = v;
            sq += d[j] * d[j];
          }
          raw[i] = mx;
        }
        rms.push(Math.sqrt(sq / Math.max(1, d.length)));
      }
      let top = 0;
      for (let i = 0; i < n; i++) if (raw[i] > top) top = raw[i];
      const p = new Uint8Array(n);
      if (top > 0) for (let i = 0; i < n; i++) p[i] = Math.round((255 * raw[i]) / top);
      // one side near silent and the other not: play the live side to both ears
      let side = null;
      if (rms.length >= 2) {
        const hi = Math.max(rms[0], rms[1]),
          lo = Math.min(rms[0], rms[1]);
        if (hi > 0.0015 && lo < hi * 0.03) side = rms[0] >= rms[1] ? 0 : 1;
      }
      r = { p, rate: RATE, dur: ab.duration, side };
      if (side != null) m = wav(ab.getChannelData(side), ab.sampleRate);
    } catch (e) {
      r = { p: new Uint8Array(0), rate: RATE, dur: +t.len || 0, side: null, bad: true };
    }
    ext.set(id, r);
    if (m) mono.set(id, m);
    reading.delete(id);
    try {
      await xtx(['peaks', 'mono'], 'readwrite', (a, b) => {
        a.put(r, id);
        if (m) b.put(m, id);
      });
    } catch (e) {}
    if (openId === id) draw();
  }
  async function forgetExtras(ids) {
    ids.forEach((id) => {
      ext.delete(id);
      mono.delete(id);
    });
    try {
      await xtx(['peaks', 'mono'], 'readwrite', (a, b) =>
        ids.forEach((id) => {
          a.delete(id);
          b.delete(id);
        })
      );
    } catch (e) {}
  }
  // what a take plays from: its both-ears copy if it has one, else the recording itself
  const blobFor = (t) => mono.get(t.id) || t.blob;

  /* ----- names and comments (with the song) ----- */
  const noteOf = (sg, id) => (sg && sg.takeNotes && sg.takeNotes[id]) || null;
  function noteFor(sg, id) {
    if (!sg.takeNotes || typeof sg.takeNotes !== 'object') sg.takeNotes = {};
    if (!sg.takeNotes[id]) sg.takeNotes[id] = {};
    return sg.takeNotes[id];
  }
  function tidyNote(sg, id) {
    const n = sg && sg.takeNotes && sg.takeNotes[id];
    if (!n) return;
    if (!n.name) delete n.name;
    if (n.comments && !n.comments.length) delete n.comments;
    if (!n.name && !n.comments) delete sg.takeNotes[id];
    if (!Object.keys(sg.takeNotes).length) delete sg.takeNotes;
  }
  const comments = (sg, id) => ((noteOf(sg, id) || {}).comments || []).slice();
  const songTakes = (sid) => TAKES.filter((t) => t.songId === sid); // oldest first
  // "Take 3 · Chorus": the take's number in the song, and where it was sung from
  function where(sg, t) {
    const i = t.o && hasLyrics(sg) ? occIdx(sg, t.o) : -1;
    return i < 0 ? '' : occLabel(sg, i);
  }
  function defName(sg, t) {
    const n = songTakes(t.songId).indexOf(t) + 1,
      w = where(sg, t);
    return 'Take ' + (n || 1) + (w ? ' · ' + w : '');
  }
  const nameOf = (sg, t) => (noteOf(sg, t.id) || {}).name || defName(sg, t);
  const fmt = (s) => {
    s = Math.max(0, Math.floor(s || 0));
    return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  };
  const lenOf = (t) => {
    const x = ext.get(t.id);
    return (x && x.dur > 0 ? x.dur : 0) || +t.len || 1;
  };

  /* ----- playing: the takes player (session.js) plays them; this follows it ----- */
  const loaded = (id) => !!(player && playingId === id);
  const isOn = (id) => takePlaying(id);
  const now = (id) => (loaded(id) ? player.currentTime || 0 : pos[id] || 0);
  function seekTo(id, t) {
    const t0 = TAKES.find((x) => x.id === id);
    if (!t0) return;
    t = Math.max(0, Math.min(lenOf(t0) - 0.05, t));
    pos[id] = t;
    prevT = t; // a jump or a scrub never pops comments up on the way
    if (loaded(id)) {
      try {
        player.currentTime = t;
      } catch (e) {}
    }
    paint();
  }
  function play(id) {
    const at = pos[id] || 0,
      t = TAKES.find((x) => x.id === id);
    if (loaded(id)) {
      if (player.paused) FW_KINDS[0].toggle();
      else player.pause();
      return;
    }
    // 3.20: a take that had finished starts again from 0:00
    playTake(id, t && at >= lenOf(t) - 0.15 ? 0 : at);
    prevT = at;
  }

  /* ----- the sheet ----- */
  const STAR = ICON.star,
    CMT = '<svg class="i" viewBox="0 0 24 24"><path d="M5 5h14v10h-7l-4 4v-4H5z"/></svg>',
    UP = '<svg class="i" viewBox="0 0 24 24"><path d="M6 15l6-6 6 6"/></svg>',
    BACK5 =
      '<svg class="i" viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.3-5.6"/><path d="M4 4v4h4"/><text x="12" y="15.5" text-anchor="middle" font-size="8" font-weight="700" fill="currentColor" stroke="none">5</text></svg>',
    FWD5 =
      '<svg class="i" viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v4h-4"/><text x="12" y="15.5" text-anchor="middle" font-size="8" font-weight="700" fill="currentColor" stroke="none">5</text></svg>';
  function listFor(sd) {
    const all = songTakes(sd.k),
      sec = sd.o ? all.filter((t) => t.o === sd.o) : null,
      on = tab || (sd.all || !sd.o ? 'all' : 'sec');
    return { all, sec, on: sec ? on : 'all', list: (sec && on === 'sec' ? sec : all).slice().reverse() };
  }
  function rowHTML(sg, t, showWhere) {
    const open = openId === t.id,
      cm = comments(sg, t.id),
      on = isOn(t.id),
      w = where(sg, t),
      sub = takeWhen(t.created) + ' · ' + mmss(Math.round(lenOf(t))) + (showWhere && w ? ' · ' + esc(w) : '');
    let h =
      '<div class="tkr' +
      (open ? ' open' : '') +
      '" data-tk="' +
      t.id +
      '" data-own-gesture><div class="tkacts" aria-hidden="true"><button class="tkas" tabindex="-1" data-a="tkStar" data-k="' +
      t.id +
      '">' +
      STAR +
      (t.star ? 'Unstar' : 'Star') +
      '</button><button class="tkad" tabindex="-1" data-a="tkDel" data-k="' +
      t.id +
      '">' +
      ICON.trash +
      'Delete</button></div><div class="tkfg">';
    if (!open)
      h +=
        '<div class="tkhead" data-a="tkTap" data-k="' +
        t.id +
        '" role="button" tabindex="0" aria-expanded="false" aria-label="' +
        esc(nameOf(sg, t)) +
        ', ' +
        sub.replace(/<[^>]+>/g, '') +
        '. Tap to play"><span class="tktx"><b>' +
        esc(nameOf(sg, t)) +
        '</b><small>' +
        sub +
        '</small></span><span class="tkic">' +
        (cm.length
          ? '<span class="tkcmn" aria-label="' + cm.length + ' comments">' + CMT + cm.length + '</span>'
          : '') +
        (t.star ? '<span class="tkstar" aria-label="Starred">' + STAR + '</span>' : '') +
        '</span><button class="tkpp" data-a="tkPlay" data-k="' +
        t.id +
        '" aria-label="' +
        (on ? 'Pause' : 'Play') +
        '">' +
        (on ? ICON.pause : ICON.play) +
        '</button></div>';
    else h += openHTML(sg, t, sub);
    return h + '</div></div>';
  }
  function openHTML(sg, t, sub) {
    const nm = noteOf(sg, t.id) || {},
      cm = comments(sg, t.id),
      L = lenOf(t),
      cur = now(t.id),
      on = isOn(t.id),
      dr = draft && draft.id === t.id ? draft : null;
    return (
      '<div class="tkopen"><div class="tktop">' +
      (renaming === t.id
        ? '<span class="tkrn"><input id="tkNameIn" class="tkni" maxlength="' +
          TK_NAME +
          '" value="' +
          esc(nm.name || '') +
          '" placeholder="' +
          esc(defName(sg, t)) +
          '" enterkeyhint="done" autocomplete="off" aria-label="Take name"><button class="tknx" data-a="tkNameClear" aria-label="Clear">' +
          SGI.xc +
          '</button><button class="lnkbtn tknd" data-a="tkNameDone">Done</button></span>'
        : '<button class="tkname" data-a="tkRename" data-k="' +
          t.id +
          '" aria-label="' +
          esc(nameOf(sg, t)) +
          '. Tap to rename"><b>' +
          esc(nameOf(sg, t)) +
          '</b><small>' +
          (nm.name ? esc(defName(sg, t)) + ' · ' : '') +
          sub +
          '</small></button>') +
      '<button class="tkbtn tkstb' +
      (t.star ? ' on' : '') +
      '" data-a="tkStar" data-k="' +
      t.id +
      '" aria-pressed="' +
      !!t.star +
      '" aria-label="' +
      (t.star ? 'Unstar' : 'Star') +
      ' take">' +
      STAR +
      '</button><button class="tkbtn" data-a="tkCollapse" aria-label="Collapse">' +
      UP +
      '</button></div>' +
      '<div class="tkpop" id="tkPop" aria-live="polite"></div>' +
      '<div class="tkwave" id="tkWave" data-own-gesture role="slider" tabindex="0" aria-label="Take position" aria-valuemin="0" aria-valuemax="' +
      Math.round(L) +
      '" aria-valuenow="' +
      Math.round(cur) +
      '" aria-valuetext="' +
      fmt(cur) +
      ' of ' +
      fmt(L) +
      '"><canvas id="tkC" aria-hidden="true"></canvas></div><div class="tkdots">' +
      cm
        .map(
          (c, i) =>
            '<button class="tkdot" data-a="tkCJump" data-v="' +
            i +
            '" style="left:' +
            Math.min(100, (c.t / L) * 100).toFixed(2) +
            '%" aria-label="Comment at ' +
            fmt(c.t) +
            '"></button>'
        )
        .join('') +
      '</div><div class="tktimes"><span id="tkEl">' +
      fmt(cur) +
      '</span><span id="tkRm">−' +
      fmt(Math.max(0, L - cur)) +
      '</span></div><div class="tktr"><button class="tkb" data-a="tkSkip" data-v="-5" aria-label="Back 5 seconds">' +
      BACK5 +
      '</button><button class="tkbig" id="tkPP" data-a="tkPlay" data-k="' +
      t.id +
      '" data-on="' +
      on +
      '" aria-label="' +
      (on ? 'Pause' : 'Play') +
      '">' +
      (on ? ICON.pause : ICON.play) +
      '</button><button class="tkb" data-a="tkSkip" data-v="5" aria-label="Forward 5 seconds">' +
      FWD5 +
      '</button></div>' +
      // the comment field: the time is locked the moment typing starts
      '<div class="tkcf"><span class="tkstamp" id="tkStamp" role="button" tabindex="0" data-a="tkStamp"' +
      (dr && dr.t != null ? '' : ' hidden') +
      '>at ' +
      fmt(dr && dr.t != null ? dr.t : 0) +
      '</span><input id="tkCIn" class="tkci" maxlength="' +
      TK_TEXT +
      '" placeholder="Add a comment" enterkeyhint="send" autocomplete="off" value="' +
      esc(dr ? dr.text : '') +
      '" aria-label="Add a comment at the playhead"><button class="lnkbtn tkpost" data-a="tkPost"' +
      (dr && dr.text.trim() ? '' : ' disabled') +
      '>' +
      (dr && dr.edit != null ? 'Save' : 'Post') +
      '</button></div><p class="tkhint" id="tkHint"' +
      (dr && dr.t != null ? '' : ' hidden') +
      '>Time locked when you started typing. Tap it to change.</p><div class="tknudge" id="tkNudge"' +
      (dr && dr.nudge ? '' : ' hidden') +
      '><button class="sgpill sm" data-a="tkNudge" data-v="-1">−1 s</button><button class="sgpill sm" data-a="tkNudge" data-v="1">+1 s</button><button class="sgpill sm" data-a="tkNudge" data-v="now">Use current time</button></div>' +
      (cm.length
        ? '<div class="tkcl">' +
          cm
            .map(
              (c, i) =>
                '<button class="tkcm" data-a="tkCJump" data-v="' +
                i +
                '" data-ci="' +
                i +
                '"><span class="tkct">' +
                fmt(c.t) +
                '</span><span class="tkcx">' +
                esc(c.text) +
                '</span></button>'
            )
            .join('') +
          '</div>'
        : '') +
      '</div>'
    );
  }
  function sheet(sd, which) {
    which = which || 'sgTakes';
    if (which === 'sgReview') return reviewSheet();
    const sg = songById(sd.k);
    if (!sg) return '';
    if (which === 'sgTakeMenu' || which === 'sgTakeDel' || which === 'sgCmtMenu') {
      const t = TAKES.find((x) => x.id === sd.t);
      if (!t) return '';
      if (which === 'sgTakeMenu')
        return sheetWrap(
          esc(nameOf(sg, t)),
          '<div class="grp"><button class="row" data-a="tkStar" data-k="' +
            t.id +
            '"><span class="lbl acc">' +
            (t.star ? 'Unstar' : 'Star') +
            '</span></button><button class="row" data-a="tkMenuRename" data-k="' +
            t.id +
            '"><span class="lbl acc">Rename</span></button><button class="row" data-a="tkDel" data-k="' +
            t.id +
            '"><span class="lbl dng">Delete</span></button></div>',
          'Take options'
        );
      if (which === 'sgTakeDel') {
        const n = comments(sg, t.id).length;
        return confirmSheet(
          'Delete this take?',
          esc(nameOf(sg, t)) +
            ' (' +
            mmss(Math.round(lenOf(t))) +
            ')' +
            (n ? ' and its ' + (n === 1 ? 'comment' : n + ' comments') : '') +
            ' will be deleted from this ' +
            deviceName() +
            '. Copies you saved to Files stay. This can’t be undone.',
          'Delete take',
          'tkDelYes',
          t.id
        );
      }
      const c = comments(sg, t.id)[sd.c];
      if (!c) return '';
      return sheetWrap(
        'Comment at ' + fmt(c.t),
        '<p class="note">' +
          esc(c.text) +
          '</p><div class="grp"><button class="row" data-a="tkCEdit"><span class="lbl acc">Edit</span></button><button class="row" data-a="tkCDel"><span class="lbl dng">Delete</span></button></div>',
        'Comment options'
      );
    }
    // a take just recorded opens expanded, ready to play
    if (sd.fresh && !sd.seen) {
      sd.seen = true;
      openId = sd.fresh;
      tab = 'sec';
    }
    const L = listFor(sd),
      secName = sd.o && hasLyrics(sg) && occIdx(sg, sd.o) >= 0 ? occLabel(sg, occIdx(sg, sd.o)) : null,
      fresh = sd.fresh && L.all.find((t) => t.id === sd.fresh);
    let h = '';
    if (L.sec && secName)
      h +=
        '<div class="seg wide tkseg" role="tablist"><span class="knob" aria-hidden="true"></span><button role="tab" data-a="tkTab" data-v="sec" class="' +
        (L.on === 'sec' ? 'on' : '') +
        '" aria-selected="' +
        (L.on === 'sec') +
        '">' +
        esc(secName) +
        ' · ' +
        L.sec.length +
        '</button><button role="tab" data-a="tkTab" data-v="all" class="' +
        (L.on === 'all' ? 'on' : '') +
        '" aria-selected="' +
        (L.on === 'all') +
        '">All takes · ' +
        L.all.length +
        '</button></div>';
    if (L.list.length)
      h +=
        '<div class="grp tkgrp">' +
        L.list.map((t) => rowHTML(sg, t, L.on === 'all')).join('') +
        '</div>' +
        '<p class="foot">' +
        (fresh ? 'Fresh ears help. Try listening again tomorrow. ' : '') +
        'Every take is kept. Swipe right to star, left to delete, or hold a take for both.</p>';
    else
      h +=
        '<p class="note">' +
        (L.on === 'sec'
          ? 'No takes for this section yet.'
          : 'No takes yet. Tap a section of the lyrics to record it.') +
        '</p>';
    if (sd.o && secName)
      h +=
        '<div class="sgagain"><button class="sgpill" data-a="sgRec" data-k="' +
        sd.o +
        '">' +
        SGI.mic +
        (L.sec.length ? 'Record again' : 'Record') +
        '</button></div>';
    const title = L.on === 'sec' && secName ? esc(secName) : 'Takes';
    return sheetWrap(title, h, 'Takes for ' + songTitle(sg));
  }
  function reviewSheet() {
    const list = TAKES.filter((t) => !t.star && !comments(songById(t.songId), t.id).length).sort(
      (a, b) => a.created - b.created
    );
    if (!list.length)
      return sheetWrap(
        'Review old takes',
        '<p class="note">Nothing to review. Starred takes and takes with comments never appear here.</p>'
      );
    return sheetWrap(
      'Review old takes',
      '<p class="note">Takes that aren’t starred and have no comments, oldest first. Nothing is ever removed for you.</p><div class="grp">' +
        list
          .map((t) => {
            const sg = songById(t.songId);
            return (
              '<div class="row tkrv"><button class="ibtn acc" data-a="playTake" data-k="' +
              t.id +
              '" aria-label="' +
              (isOn(t.id) ? 'Pause' : 'Play') +
              ' take">' +
              (isOn(t.id) ? ICON.pause : ICON.play) +
              '</button><span class="lbl">' +
              esc(sg ? songTitle(sg) : 'Deleted song') +
              '<small>' +
              esc(sg ? nameOf(sg, t) : 'Take') +
              ' · ' +
              takeWhen(t.created) +
              ' · ' +
              mmss(Math.round(lenOf(t))) +
              '</small></span><button class="ibtn dng" data-a="tkRvDel" data-k="' +
              t.id +
              '" aria-label="Delete take">' +
              ICON.trash +
              '</button></div>'
            );
          })
          .join('') +
        '</div>'
    );
  }
  // the Takes button beside a song's title (shown by default; opens All takes)
  function headBtn(sg) {
    const n = songTakes(sg.id).length;
    return (
      '<button class="sgtkb" data-a="tkOpenAll" data-k="' +
      sg.id +
      '" aria-label="Takes, ' +
      n +
      '">' +
      SGI.mic +
      'Takes · ' +
      n +
      '</button>'
    );
  }
  // Settings › Storage
  function storageRows() {
    const size = TAKES.reduce((a, t) => a + (+t.size || 0), 0);
    return (
      '<button class="row" data-a="sheet" data-v="storage"><span class="lbl">Recordings</span><span class="mut">' +
      TAKES.length +
      (TAKES.length === 1 ? ' take' : ' takes') +
      ' · ' +
      (size / 1048576).toFixed(1) +
      ' MB</span>' +
      chev +
      '</button><button class="row" data-a="tkReview"><span class="lbl acc">Review old takes</span>' +
      chev +
      '</button>'
    );
  }

  /* ----- drawing in place (nothing is redrawn while it plays) ----- */
  const shown = () => U.sheet === 'sgTakes' && !!openId && !!$('tkC');
  const inPlace = () => U.sheet === 'sgTakes' && !!document.querySelector('#layer .tkr');
  function colours() {
    const cs = getComputedStyle(document.documentElement),
      g = (k, d) => cs.getPropertyValue(k).trim() || d;
    C = {
      fg: g('--fg', '#000'),
      dim: g('--trk-dim', '#bbb'),
      head: g('--accent', '#007aff'),
      dot: g('--star', '#ff9f0a'),
    };
  }
  function draw() {
    const c = $('tkC');
    if (!c || !openId) return;
    if (!C) colours();
    const t = TAKES.find((x) => x.id === openId);
    if (!t) return;
    const r = c.getBoundingClientRect(),
      dpr = window.devicePixelRatio || 1,
      W = Math.max(1, Math.round(r.width * dpr)),
      H = Math.max(1, Math.round(r.height * dpr));
    if (c.width !== W || c.height !== H) {
      c.width = W;
      c.height = H;
    }
    const g = c.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, r.width, r.height);
    const x = ext.get(t.id),
      P = x && x.p,
      L = lenOf(t),
      cur = now(t.id),
      w = r.width,
      h = r.height,
      mid = h / 2,
      step = 3,
      n = Math.floor(w / step);
    if (!x && !reading.has(t.id)) analyse(t.id);
    for (let i = 0; i < n; i++) {
      const a = (i / n) * L,
        b = ((i + 1) / n) * L;
      let v = 0;
      if (P && P.length) {
        const i0 = Math.floor(a * x.rate),
          i1 = Math.min(P.length, Math.max(i0 + 1, Math.ceil(b * x.rate)));
        for (let j = i0; j < i1; j++) if (P[j] > v) v = P[j];
        v /= 255;
      }
      const bh = Math.max(2, v * (h - 6));
      g.fillStyle = (a + b) / 2 <= cur ? C.head : C.dim;
      g.fillRect(i * step, mid - bh / 2, 2, bh);
    }
    const hx = Math.min(w - 1, (cur / L) * w);
    g.fillStyle = C.fg;
    g.fillRect(hx - 1, 0, 2, h);
  }
  function paint() {
    if (!openId) return;
    const t = TAKES.find((x) => x.id === openId);
    if (!t) return;
    const L = lenOf(t),
      cur = Math.min(L, now(t.id)),
      el = $('tkEl'),
      rm = $('tkRm'),
      pp = $('tkPP'),
      wv = $('tkWave');
    if (el) el.textContent = fmt(cur);
    if (rm) rm.textContent = '−' + fmt(Math.max(0, L - cur));
    if (wv) {
      wv.setAttribute('aria-valuenow', Math.round(cur));
      wv.setAttribute('aria-valuetext', fmt(cur) + ' of ' + fmt(L));
    }
    if (pp) {
      const on = isOn(t.id);
      if (pp.dataset.on !== String(on)) {
        pp.dataset.on = String(on);
        pp.innerHTML = on ? ICON.pause : ICON.play;
        pp.setAttribute('aria-label', on ? 'Pause' : 'Play');
      }
    }
    document.querySelectorAll('#layer .tkhead .tkpp').forEach((b) => {
      const on = isOn(b.dataset.k);
      if (b.classList.contains('on') === on) return;
      b.classList.toggle('on', on);
      b.innerHTML = on ? ICON.pause : ICON.play;
      b.setAttribute('aria-label', on ? 'Pause' : 'Play');
    });
    const pe = $('tkPop');
    if (pe) {
      const v = pop && Date.now() < pop.until ? pop.text : '';
      if (pe.textContent !== v) {
        pe.textContent = v;
        pe.classList.toggle('on', !!v);
      }
    }
    draw();
  }
  // every frame while a take plays: comments pop up as the playhead passes them (not when it jumps past)
  function frame(p) {
    if (!openId || !loaded(openId)) return;
    const cur = p.currentTime || 0,
      sg = songById((TAKES.find((x) => x.id === openId) || {}).songId);
    if (cur > prevT && cur - prevT < 0.6) {
      const hit = comments(sg, openId)
        .filter((c) => c.t > prevT && c.t <= cur)
        .pop();
      if (hit) pop = { text: fmt(hit.t) + '  ' + hit.text, until: Date.now() + 2000 };
    }
    prevT = cur;
    pos[openId] = cur;
    paint();
  }
  function show(text) {
    pop = { text, until: Date.now() + 2000 };
    paint();
    setTimeout(paint, 2050);
  }
  // after every redraw: the expanded take's waveform, and the field being typed in
  function after() {
    if (U.sheet !== 'sgTakes') {
      if (U.sheet !== 'sgTakeMenu' && U.sheet !== 'sgTakeDel' && U.sheet !== 'sgCmtMenu') {
        openId = null;
        tab = null;
        renaming = null;
        draft = null;
      }
      return;
    }
    colours();
    paint();
    if (renaming) {
      const i = $('tkNameIn');
      if (i && document.activeElement !== i) {
        i.focus();
        i.setSelectionRange(i.value.length, i.value.length);
      }
    }
    if (draft && draft.focus) {
      const i = $('tkCIn');
      if (i) {
        i.focus();
        i.setSelectionRange(i.value.length, i.value.length);
      }
      draft.focus = false;
    }
  }
  function stopped() {
    if (openId && playingId == null) paint();
  }

  /* ----- comments: the time locks on the first character ----- */
  document.addEventListener('input', (e) => {
    const i = e.target;
    if (i.id === 'sgLyr') {
      // the + sheet's button: Save song with no lyrics (Add media), Next to label them
      const b = document.querySelector('#layer [data-a=sgSplit]'),
        d = U.sDraft;
      if (b && d && !d.forId && d.mode !== 'manual' && d.media) b.textContent = i.value.trim() ? 'Next' : 'Save song';
      return;
    }
    if (i.id !== 'tkCIn' || !openId) return;
    const v = i.value;
    if (!draft || draft.id !== openId) draft = { id: openId, text: '', t: null, edit: null, nudge: false };
    draft.text = v;
    if (v && draft.t == null) draft.t = Math.round(now(openId) * 10) / 10;
    if (!v && draft.edit == null) {
      draft.t = null; // clearing the field lets go of the time
      draft.nudge = false;
    }
    stampPaint();
  });
  function stampPaint() {
    const st = $('tkStamp'),
      hi = $('tkHint'),
      nu = $('tkNudge'),
      po = document.querySelector('#layer [data-a=tkPost]'),
      on = !!(draft && draft.t != null);
    if (st) {
      st.hidden = !on;
      if (on) st.textContent = 'at ' + fmt(draft.t);
    }
    if (hi) hi.hidden = !on;
    if (nu) nu.hidden = !(on && draft.nudge);
    if (po) po.disabled = !(draft && draft.text.trim());
  }
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' || e.isComposing) return;
    if (e.target.id === 'tkCIn') {
      e.preventDefault();
      post();
    } else if (e.target.id === 'tkNameIn') {
      e.preventDefault();
      nameDone();
    }
  });
  document.addEventListener('focusout', (e) => {
    if (e.target.id === 'tkNameIn')
      setTimeout(() => renaming && !document.activeElement.closest('.tkrn') && nameDone(), 0);
  });
  function post() {
    if (!draft || draft.id !== openId) return;
    const text = draft.text.trim().slice(0, TK_TEXT),
      t = TAKES.find((x) => x.id === openId),
      sg = t && songById(t.songId);
    if (!text || !sg) return;
    const n = noteFor(sg, t.id);
    n.comments = n.comments || [];
    const c = { t: Math.max(0, Math.min(lenOf(t), draft.t == null ? now(t.id) : draft.t)), text };
    c.t = Math.round(c.t * 10) / 10;
    if (draft.edit != null && n.comments[draft.edit]) n.comments[draft.edit] = c;
    else n.comments.push(c);
    n.comments.sort((a, b) => a.t - b.t);
    if (n.comments.length > TK_MAXC) n.comments.length = TK_MAXC;
    save();
    draft = null;
    rerender();
  }
  function nameDone() {
    if (!renaming) return;
    const id = renaming,
      i = $('tkNameIn'),
      t = TAKES.find((x) => x.id === id),
      sg = t && songById(t.songId);
    renaming = null;
    if (sg && i) {
      const v = i.value.trim().slice(0, TK_NAME),
        n = noteFor(sg, id);
      if (v && v !== defName(sg, t)) n.name = v;
      else delete n.name; // empty: back to "Take 3 · Chorus"
      tidyNote(sg, id);
      save();
    }
    rerender();
  }

  /* ----- deleting and starring ----- */
  async function del(id) {
    const t = TAKES.find((x) => x.id === id),
      sg = t && songById(t.songId);
    if (playingId === id) stopPlayback();
    await delTake(id);
    if (sg && sg.takeNotes) {
      delete sg.takeNotes[id];
      if (!Object.keys(sg.takeNotes).length) delete sg.takeNotes;
      save();
    }
    forgetExtras([id]);
    if (openId === id) openId = null;
    await refreshTakes();
  }
  // a song's takes are going (the song was deleted)
  function forgetSong(sg) {
    if (sg) delete sg.takeNotes;
  }
  async function star(id) {
    const t = TAKES.find((x) => x.id === id);
    if (!t) return;
    t.star = !t.star;
    await putTake(t);
    await refreshTakes();
    toast(t.star ? 'Starred' : 'Unstarred');
  }

  /* ----- fingers: scrub the waveform; swipe or hold a row ----- */
  function scrubAt(x) {
    const wv = $('tkWave'),
      t = TAKES.find((y) => y.id === openId);
    if (!wv || !t) return;
    const r = wv.getBoundingClientRect();
    seekTo(openId, (Math.max(0, Math.min(r.width, x - r.left)) / Math.max(1, r.width)) * lenOf(t));
  }
  document.addEventListener('pointerdown', (e) => {
    if (U.sheet !== 'sgTakes' || e.button > 0) return;
    const wv = e.target.closest && e.target.closest('#tkWave');
    if (wv) {
      e.preventDefault();
      scrub = { id: e.pointerId };
      try {
        wv.setPointerCapture(e.pointerId);
      } catch (x) {}
      wv.classList.add('drag');
      scrubAt(e.clientX); // follows the finger at once
      return;
    }
    const row = e.target.closest && e.target.closest('.tkr');
    if (!row || row.classList.contains('open') || e.target.closest('.tkacts') || e.target.closest('input')) return;
    closeRows(row);
    sw = {
      row,
      id: row.dataset.tk,
      pid: e.pointerId,
      x: e.clientX,
      y: e.clientY,
      dx: 0,
      base: +(row.dataset.x || 0),
      on: false,
      held: false,
      open: row.classList.contains('open'),
      t: setTimeout(() => {
        if (!sw || sw.on || sw.row !== row) return;
        sw.held = true;
        U.sheet = 'sgTakeMenu';
        U.sd = { k: (TAKES.find((x) => x.id === row.dataset.tk) || {}).songId, t: row.dataset.tk, ret: retHere() };
        rerender();
      }, 500),
    };
  });
  document.addEventListener('pointermove', (e) => {
    if (scrub && e.pointerId === scrub.id) return scrubAt(e.clientX);
    if (!sw || e.pointerId !== sw.pid) return;
    const dx = e.clientX - sw.x,
      dy = e.clientY - sw.y;
    if (!sw.on) {
      if (Math.hypot(dx, dy) > 10) clearTimeout(sw.t);
      // the row claims a sideways move; an up-and-down one scrolls the sheet. An expanded take doesn't swipe
      if (sw.open || Math.abs(dx) < 10 || Math.abs(dx) < Math.abs(dy) * 1.2) {
        if (Math.abs(dy) > 10) sw = null;
        return;
      }
      sw.on = true;
      sw.row.classList.add('swiping');
      try {
        sw.row.setPointerCapture(e.pointerId);
      } catch (x) {}
    }
    sw.dx = dx;
    setX(sw.row, sw.base + dx, true);
  });
  const endPtr = (e) => {
    if (scrub && e.pointerId === scrub.id) {
      scrub = null;
      document.querySelectorAll('#tkWave.drag').forEach((w) => w.classList.remove('drag'));
      return;
    }
    if (!sw || e.pointerId !== sw.pid) return;
    const s = sw;
    sw = null;
    clearTimeout(s.t);
    if (s.held) heldAt = Date.now(); // the release after a hold isn't a tap on the menu that opened
    if (!s.on) return;
    s.row.classList.remove('swiping');
    rowMoved = Date.now();
    const x = s.base + s.dx,
      w = s.row.getBoundingClientRect().width;
    if (e.type === 'pointercancel') return setX(s.row, 0);
    if (x > w / 2) {
      setX(s.row, 0);
      star(s.id).then(rerender);
    } else if (x < -w / 2) {
      setX(s.row, 0);
      askDel(s.id);
    } else if (x > 40) setX(s.row, 84);
    else if (x < -40) setX(s.row, -84);
    else setX(s.row, 0);
  };
  document.addEventListener('pointerup', endPtr);
  document.addEventListener('pointercancel', endPtr);
  let rowMoved = 0,
    heldAt = 0;
  // a swipe or a hold isn't also a tap
  document.addEventListener(
    'click',
    (e) => {
      if (Date.now() - heldAt < 400) {
        e.stopPropagation();
        e.preventDefault();
        return;
      }
      if (!(e.target.closest && e.target.closest('#layer .tkr'))) return;
      if (Date.now() - rowMoved < 350 && !e.target.closest('.tkacts')) {
        e.stopPropagation();
        e.preventDefault();
      }
    },
    true
  );
  // only the side being swiped shows its colour: right is Star (orange), left is Delete (red)
  function setX(row, x, live) {
    const w = row.getBoundingClientRect().width;
    x = Math.max(-w, Math.min(w, x));
    row.dataset.x = x;
    const fg = row.querySelector('.tkfg');
    if (fg) {
      fg.style.transition = live ? 'none' : '';
      fg.style.transform = x ? 'translateX(' + x + 'px)' : '';
    }
    row.classList.toggle('sr', x > 0);
    row.classList.toggle('sl', x < 0);
  }
  function closeRows(except) {
    document.querySelectorAll('#layer .tkr[data-x]').forEach((r) => {
      if (r !== except && +r.dataset.x) setX(r, 0);
    });
  }
  const retHere = () => ({ sheet: 'sgTakes', sd: Object.assign({}, U.sd || {}) });
  function askDel(id) {
    const t = TAKES.find((x) => x.id === id);
    if (!t) return;
    const r =
      U.sheet === 'sgTakes' || U.sheet === 'sgReview'
        ? { sheet: U.sheet, sd: Object.assign({}, U.sd || {}) }
        : (U.sd || {}).ret;
    U.sheet = 'sgTakeDel';
    U.sd = { k: t.songId, t: id, ret: r };
    rerender();
  }
  // the sheet a menu or confirmation came from
  function back() {
    const r = (U.sd || {}).ret;
    if (r && r.sheet) {
      U.sheet = r.sheet;
      U.sd = r.sd || {};
    } else {
      U.sheet = null;
      U.sd = {};
    }
    rerender();
  }

  /* ----- actions (data-a="tk…") ----- */
  Object.assign(SG_ACT, {
    tkOpenAll(el, v, k) {
      if (rec) return toast('Stop recording first');
      U.sheet = 'sgTakes';
      U.sd = { k: k || U.songId, all: true };
      tab = 'all';
      openId = null;
      rerender();
    },
    tkTab(el, v) {
      tab = v === 'sec' ? 'sec' : 'all';
      segPick(el);
      openId = null;
      rerender();
    },
    tkTap(el, v, k) {
      // a row expands (one at a time) and plays
      renaming = null;
      if (draft && draft.id !== k) draft = null;
      openId = k;
      if (!isOn(k)) play(k);
      rerender();
      requestAnimationFrame(() => {
        const r = document.querySelector('#layer .tkr.open');
        if (r && r.scrollIntoView) r.scrollIntoView({ block: 'nearest' });
      });
    },
    tkPlay(el, v, k) {
      if (openId !== k) {
        openId = k;
        renaming = null;
        if (!isOn(k)) play(k);
        else player.pause();
        return rerender();
      }
      play(k);
    },
    tkCollapse() {
      // collapsing doesn't stop it; the window's rules apply once the sheet closes
      openId = null;
      renaming = null;
      draft = null;
      rerender();
    },
    tkSkip(el, v) {
      if (!openId) return;
      seekTo(openId, now(openId) + +v);
    },
    tkStar(el, v, k) {
      const wasMenu = U.sheet === 'sgTakeMenu';
      star(k).then(() => {
        if (wasMenu) back();
        else rerender();
        const b = document.querySelector('#layer .tkr[data-tk="' + k + '"] .tkstb.on');
        if (b) DET.starPop(b);
      });
    },
    tkDel(el, v, k) {
      askDel(k);
    },
    tkDelYes(el, v, k) {
      del(k).then(() => {
        back();
        toast('Take deleted');
      });
    },
    tkRvDel(el, v, k) {
      askDel(k);
    },
    tkMenuRename(el, v, k) {
      openId = k;
      renaming = k;
      back();
    },
    tkRename(el, v, k) {
      renaming = k;
      rerender();
    },
    tkNameClear() {
      const i = $('tkNameIn');
      if (i) {
        i.value = '';
        i.focus();
      }
    },
    tkNameDone() {
      nameDone();
    },
    tkStamp() {
      if (!draft || draft.t == null) return;
      draft.nudge = !draft.nudge;
      stampPaint();
    },
    tkNudge(el, v) {
      if (!draft || draft.t == null) return;
      const t = TAKES.find((x) => x.id === draft.id);
      draft.t =
        v === 'now'
          ? Math.round(now(draft.id) * 10) / 10
          : Math.max(0, Math.min(t ? lenOf(t) : 1e9, Math.round((draft.t + +v) * 10) / 10));
      stampPaint();
      const i = $('tkCIn');
      if (i) i.focus();
    },
    tkPost() {
      post();
    },
    tkCJump(el, v) {
      const t = TAKES.find((x) => x.id === openId),
        c = t && comments(songById(t.songId), t.id)[+v];
      if (!c) return;
      seekTo(openId, c.t);
      show(fmt(c.t) + '  ' + c.text);
    },
    tkCEdit() {
      const sd = U.sd || {},
        t = TAKES.find((x) => x.id === sd.t),
        c = t && comments(songById(t.songId), t.id)[sd.c];
      if (c) {
        openId = t.id;
        draft = { id: t.id, text: c.text, t: c.t, edit: sd.c, nudge: false, focus: true };
      }
      back();
    },
    tkCDel() {
      const sd = U.sd || {},
        t = TAKES.find((x) => x.id === sd.t),
        sg = t && songById(t.songId),
        n = sg && noteOf(sg, t.id);
      if (n && n.comments && n.comments[sd.c]) {
        n.comments.splice(sd.c, 1);
        tidyNote(sg, t.id);
        save();
        toast('Comment deleted');
      }
      back();
    },
    tkReview() {
      U.sheet = 'sgReview';
      U.sd = {};
      rerender();
    },
  });
  // hold a comment: Edit · Delete
  let ch = null;
  document.addEventListener('pointerdown', (e) => {
    const b = e.target.closest && e.target.closest('#layer .tkcm');
    if (!b) return;
    const t = TAKES.find((x) => x.id === openId);
    if (!t) return;
    ch = {
      x: e.clientX,
      y: e.clientY,
      done: false,
      t: setTimeout(() => {
        ch.done = true;
        U.sheet = 'sgCmtMenu';
        U.sd = { k: t.songId, t: t.id, c: +b.dataset.ci, ret: retHere() };
        rerender();
      }, 500),
    };
  });
  document.addEventListener('pointermove', (e) => {
    if (ch && !ch.done && Math.hypot(e.clientX - ch.x, e.clientY - ch.y) > 10) {
      clearTimeout(ch.t);
      ch = null;
    }
  });
  ['pointerup', 'pointercancel'].forEach((ty) =>
    document.addEventListener(ty, () => {
      if (!ch) return;
      if (ch.done)
        heldAt = Date.now(); // the click after the hold (if any) is swallowed above
      else clearTimeout(ch.t);
      ch = null;
    })
  );
  window.addEventListener('resize', () => draw());

  return {
    load,
    analyse,
    blobFor,
    sheet,
    headBtn,
    storageRows,
    after,
    paint,
    frame,
    stopped,
    inPlace,
    forgetExtras,
    forgetSong,
    del,
    // tests
    state: () => ({
      open: openId,
      tab,
      renaming,
      draft: draft ? Object.assign({}, draft) : null,
      pop: pop && Date.now() < pop.until ? pop.text : '',
    }),
    ext: (id) => (ext.get(id) ? Object.assign({}, ext.get(id), { p: null, n: ext.get(id).p.length }) : null),
    hasMono: (id) => mono.has(id),
    nameOf: (id) => {
      const t = TAKES.find((x) => x.id === id);
      return t ? nameOf(songById(t.songId), t) : '';
    },
    now,
    seekTo,
    shown,
  };
})();
