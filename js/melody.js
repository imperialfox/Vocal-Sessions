/* Vocal Sessions · melody.js (Q42)
   MELODY: a song's sheet music, read from Ivan's own Ultimate Guitar print into a score (the vocal line's notes, bars
   and rests, in ticks, 480 a beat), kept on the device and in backups. "Sheet music" is its name on screen; in code it's
   the melody, because "sheet" means the bottom sheets everywhere.
   - Stored in IndexedDB vocalMelodies: `melodies` (the score, keyed by song id, in backups as the `melodies` field with
     its own check code), `prints` (the PDF as imported, never in backups, like tracks) and `undo` (the device's scores
     kept by a restore, cleared with the takes' undo). The song carries only a note, sg.ext.melody = {ug, at}.
   - Write order: score, then the song's note, then the print. A print that won't save leaves the score usable.
   - Every write names the rev it started from; a write from an older one (another window) is refused and reloaded.
   - The reader runs in a Worker (js/melodyread.js), with pdf.js loaded inside it from js/vendor/.
   - Guards: see MAINTAINING › Sheet music, where each one names its test.
   Screens: the Sheet music row on the Song page (VS-009), Sheet music (VS-099), Sheet music read (VS-100) and its
   questions (VS-101 to VS-105), the reading pill (VS-106), the PDF door on New song (VS-051) and Settings › Storage. */
const MELODY = (() => {
  let V = 1; // the score's shape; numbered upgrade steps are never removed
  const UPGRADES = {}; // v → fn(score) that brings a score from v - 1 to v
  const TPB = 480,
    LO = 33,
    HI = 96,
    MB = 1048576,
    MAX_MB = 30,
    DAYS = 30;
  const MDB = IDB.define('vocalMelodies', 1, { melodies: null, prints: null, undo: null });
  const scores = new Map(); // song id → its score (cleaned), once loaded
  const prints = new Map(); // song id → {name, size, pages, ug, at}: prints on this device (their bytes stay in IndexedDB)
  let loaded = false,
    loading = null;
  let want = null, // where the next picked PDF goes: {id} or {draft}
    job = null, // the read running: {target, file, w, f, line, lines}
    held = null, // a read waiting for its questions or its sheet: {target, r, file, step}
    big = null, // a big PDF waiting for "Read it anyway"
    testOpt = null;
  const q = (sel) => document.querySelector(sel);

  /* ----- Q47 the sheet view's lines: cut again from the kept print each time it opens (decision 22, H42) -----
     In the reader's Worker; if pdf.js won't load there, on the page. Resolves [{i, w, h, g, both}] at half size, or null
     when there's no print on this device or it can't be read. Nothing is stored. */
  let cutOpt = null; // tests: {nopdf: true}
  async function cut(id) {
    const rec = await MDB.tx('prints', 'readonly', (st) => st.get(id)).catch(() => null);
    if (!rec || !rec.blob) return null;
    let data;
    try {
      data = await rec.blob.arrayBuffer();
    } catch (e) {
      return null;
    }
    const src = (q('link[href^="js/melodyread.js"]') || { getAttribute: () => 'js/melodyread.js' }).getAttribute('href');
    const got = await new Promise((res) => {
      let w;
      try {
        w = new Worker(src);
      } catch (e) {
        return res('nopdf');
      }
      const done = (v) => {
        try {
          w.terminate();
        } catch (e) {}
        res(v);
      };
      w.onmessage = (e) => {
        const m = e.data;
        if (!m || !m.mine) return;
        if (m.type === 'cut') done(m.lines);
        else if (m.type === 'nopdf') done('nopdf');
        else if (m.type === 'cutfail') done(null);
      };
      w.onerror = () => done('nopdf');
      const d = data.slice(0);
      w.postMessage(Object.assign({ vs: 1, type: 'cut', data: d }, cutOpt || {}), [d]);
    });
    if (got !== 'nopdf') return got;
    try {
      const lib = await libHere();
      return await MELREAD.cutLines(lib, new Uint8Array(data));
    } catch (e) {
      return null;
    }
  }

  /* ----- checking a saved score (load, restore, import) ----- */
  const int = (v) => typeof v === 'number' && isFinite(v) && Math.round(v) === v;
  const clamp = (v, a, b, d) => (typeof v === 'number' && isFinite(v) ? Math.min(b, Math.max(a, Math.round(v))) : d);
  // record by record: a bad note, bar or rest is dropped on its own; unknown fields are kept; never throws (null when
  // the whole thing can't be used)
  function cleanMelody(x) {
    try {
      if (!x || typeof x !== 'object' || Array.isArray(x) || !Array.isArray(x.notes) || !Array.isArray(x.bars)) return null;
      const o = Object.assign({}, x);
      o.v = int(x.v) && x.v > 0 ? x.v : 1;
      o.reader = int(x.reader) ? x.reader : 0;
      o.rev = int(x.rev) && x.rev >= 0 ? x.rev : 0;
      o.at = typeof x.at === 'number' && isFinite(x.at) ? x.at : 0;
      o.src = x.src === 'track' ? 'track' : 'sheet';
      o.tempo = clamp(x.tempo, 20, 300, 100);
      o.shift = clamp(x.shift, -12, 12, 0);
      o.octave = clamp(x.octave, -2, 2, 0);
      o.key = clamp(x.key, -7, 7, 0);
      o.time =
        Array.isArray(x.time) && int(x.time[0]) && x.time[0] >= 1 && x.time[0] <= 16 && [1, 2, 4, 8, 16].includes(x.time[1])
          ? [x.time[0], x.time[1]]
          : [4, 4];
      const span = (r) => r && typeof r === 'object' && int(r.tick) && r.tick >= 0 && int(r.len) && r.len > 0;
      o.bars = x.bars.filter((b) => span(b) && int(b.n)).map((b) => Object.assign({}, b)).sort((a, b) => a.tick - b.tick);
      const notes = x.notes
        .filter((n) => span(n) && int(n.midi) && n.midi >= LO && n.midi <= HI)
        .map((n) => Object.assign({}, n))
        .sort((a, b) => a.tick - b.tick);
      o.notes = [];
      for (const n of notes) {
        const p = o.notes[o.notes.length - 1];
        if (p && n.tick < p.tick + p.len) continue; // overlapping: the later one goes
        if (n.flag != null && typeof n.flag !== 'string') delete n.flag;
        if (n.syl != null && typeof n.syl !== 'string') delete n.syl;
        o.notes.push(n);
      }
      o.rests = Array.isArray(x.rests) ? x.rests.filter(span).map((r) => Object.assign({}, r)).sort((a, b) => a.tick - b.tick) : [];
      o.anchors = Array.isArray(x.anchors) ? x.anchors.filter((a) => a && typeof a === 'object') : [];
      o.loop = x.loop && typeof x.loop === 'object' && !Array.isArray(x.loop) ? x.loop : null;
      if (x.ug != null && (typeof x.ug !== 'object' || Array.isArray(x.ug))) delete o.ug;
      return o;
    } catch (e) {
      return null;
    }
  }
  // the song's note: {ug, at} (cleanSong keeps it as checked here; anything else is dropped)
  function cleanNote(ext) {
    if (!ext || !('melody' in ext)) return;
    const m = ext.melody;
    if (!m || typeof m !== 'object' || Array.isArray(m) || !(typeof m.at === 'number' && isFinite(m.at))) delete ext.melody;
    else {
      ext.melody = Object.assign({}, m);
      if (m.ug != null && typeof m.ug !== 'string') ext.melody.ug = null;
    }
  }
  const noteOf = (sg) => (sg && sg.ext && sg.ext.melody) || null;
  function setNote(sg, ug, at) {
    sg.ext = Object.assign({}, sg.ext || {}, { melody: { ug: ug == null ? null : String(ug), at } });
  }
  // a score in an older shape: its old copy goes to the safety copies for 30 days, then each step runs in order
  async function upgrade(id, s) {
    if (s.v >= V) return s;
    try {
      await SAFE.put('melodyBeforeUpgrade:' + id, { at: Date.now(), from: s.v, to: V, data: JSON.parse(JSON.stringify(s)) });
    } catch (e) {
      return s; // no copy, no upgrade: it's used as it is
    }
    let o = s;
    for (let v = s.v + 1; v <= V; v++) {
      if (UPGRADES[v]) o = UPGRADES[v](o) || o;
      o.v = v;
    }
    await MDB.tx('melodies', 'readwrite', (st) => st.put(o, id)).catch(() => {});
    return o;
  }

  /* ----- loading (after the first draw, like takes) ----- */
  function load() {
    if (loading) return loading;
    loading = (async () => {
      const raw = [];
      await MDB.each('melodies', (k, v) => raw.push([k, v]));
      for (const [k, v] of raw) {
        if (typeof k !== 'string') continue;
        let s = cleanMelody(v);
        if (!s) {
          let text = '';
          try {
            text = JSON.stringify(v);
          } catch (e) {
            text = String(v);
          }
          await SAFE.rescue(text, 'melody').catch(() => {});
          await MDB.tx('melodies', 'readwrite', (st) => st.delete(k)).catch(() => {});
          continue;
        }
        s = await upgrade(k, s);
        scores.set(k, s);
      }
      await MDB.each('prints', (k, v) => {
        if (typeof k === 'string' && v && typeof v === 'object') prints.set(k, metaOf(v));
      });
      loaded = true;
      reconcile();
      // safety copies of sheet music older than 30 days go
      for (const m of SAFE.list ? SAFE.list() : [])
        if (/^melody/.test(m.key) && !(Date.now() - m.at < DAYS * 864e5)) await SAFE.del(m.key).catch(() => {});
    })();
    return loading;
  }
  const metaOf = (v) => ({ name: String(v.name || ''), size: +v.size || 0, pages: +v.pages || 0, ug: v.ug || null, at: +v.at || 0 });
  // a score with no note on its song gets its note back (a crash between the two writes)
  function reconcile() {
    let changed = false;
    scores.forEach((s, id) => {
      const sg = songById(id);
      if (sg && !noteOf(sg)) {
        setNote(sg, s.ug && s.ug.id, s.at);
        changed = true;
      }
    });
    if (changed) save();
  }

  /* ----- writing ----- */
  class Stale extends Error {}
  // the score, whole, if the stored one is still at rev `base` (0: none yet); else it's refused and reloaded
  async function put(id, s, base) {
    let stale = false;
    try {
      await MDB.tx('melodies', 'readwrite', (st) => {
        const g = st.get(id);
        g.onsuccess = () => {
          const cur = g.result;
          if ((cur ? +cur.rev || 0 : 0) !== base) {
            stale = true;
            st.transaction.abort();
          } else st.put(s, id);
        };
      });
    } catch (e) {
      if (!stale) throw e;
    }
    if (stale) {
      await reload(id);
      throw new Stale('stale');
    }
    scores.set(id, s);
  }
  async function reload(id) {
    const v = await MDB.tx('melodies', 'readonly', (st) => st.get(id)).catch(() => null);
    const s = cleanMelody(v);
    if (s) scores.set(id, s);
    else scores.delete(id);
  }
  // change one of the score's own settings (tempo, octave): one write with its rev
  async function edit(id, patch) {
    const s = scores.get(id);
    if (!s) return;
    const n = Object.assign({}, s, patch, { rev: (s.rev || 0) + 1, at: Date.now() });
    try {
      await put(id, n, s.rev || 0);
    } catch (e) {
      if (e instanceof Stale) toast('Sheet music changed in another window. Showing the latest.', 4000, 'long');
      else toast('Couldn’t save that. Storage may be full.');
    }
    rerender();
  }
  // a finished read becomes the song's score: score, then the note, then the print
  async function keep(sg, r, file, o) {
    await load();
    const id = sg.id,
      old = scores.get(id),
      at = Date.now();
    const s = {
      v: V,
      reader: r.reader,
      rev: old ? (old.rev || 0) + 1 : 1,
      at,
      src: 'sheet',
      tempo: clamp(o.tempo, 20, 300, 100),
      time: r.time,
      key: r.key,
      octave: clamp(o.octave, -2, 2, 0),
      shift: old ? old.shift || 0 : 0,
      bars: r.bars,
      notes: r.notes,
      rests: r.rests,
      anchors: old && old.anchors ? old.anchors : [],
      loop: null,
      ug: r.ug || null,
      repeats: !!r.repeats,
    };
    if (old) {
      // the score it replaces is kept for 30 days in the safety copies
      try {
        await SAFE.put('melody:' + id + ':' + at, { at, why: 'replaced', data: JSON.parse(JSON.stringify(old)) });
      } catch (e) {}
    }
    await put(id, s, old ? old.rev || 0 : 0);
    setNote(sg, r.ug && r.ug.id, at);
    save();
    try {
      await MDB.tx('prints', 'readwrite', (p) =>
        p.put({ name: String(file.name || 'Sheet music.pdf').slice(0, 200), size: file.size, type: 'application/pdf', pages: r.pages || 0, ug: r.ug || null, at, blob: file }, id)
      );
      prints.set(id, { name: String(file.name || ''), size: file.size, pages: r.pages || 0, ug: r.ug || null, at });
      return true;
    } catch (e) {
      prints.delete(id);
      MDB.tx('prints', 'readwrite', (p) => p.delete(id)).catch(() => {});
      toast('Print not saved; storage is full', 4000, 'long');
      return false;
    }
  }
  // deleting songs: their scores and prints go too, as their tracks do
  async function forget(ids) {
    ids = (ids || []).filter((id) => typeof id === 'string');
    if (!ids.length) return;
    ids.forEach((id) => {
      scores.delete(id);
      prints.delete(id);
    });
    try {
      await MDB.tx(['melodies', 'prints'], 'readwrite', (m, p) =>
        ids.forEach((id) => {
          m.delete(id);
          p.delete(id);
        })
      );
    } catch (e) {}
  }
  async function removePrints() {
    await MDB.tx('prints', 'readwrite', (p) => p.clear());
    prints.clear();
  }
  const orphans = () => [...scores.keys()].filter((id) => !songById(id));

  /* ----- backups ----- */
  // every score on this device, for a backup's `melodies` field
  const all = () => [...scores.entries()].map(([id, s]) => Object.assign({ id }, s));
  async function code(list) {
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return null;
    try {
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(list)));
      return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, '0')).join('');
    } catch (e) {
      return null;
    }
  }
  // a backup's melodies: 'none' (made before Q42), 'good', or 'damaged' (the rest of the backup still restores; the
  // field's text goes to Rescued data when it's restored). list: the scores that can be used
  async function inspect(p) {
    if (!('melodies' in p)) return { state: 'none', list: [] };
    let text = '';
    try {
      text = JSON.stringify(p.melodies);
    } catch (e) {}
    if (!Array.isArray(p.melodies)) return { state: 'damaged', list: [], text, bad: 1 };
    const c = p.melodiesCode ? await code(p.melodies) : null;
    if (p.melodiesCode && c != null && c !== p.melodiesCode) return { state: 'damaged', list: [], text, bad: p.melodies.length };
    const list = [];
    let bad = 0;
    for (const m of p.melodies) {
      const s = m && typeof m.id === 'string' ? cleanMelody(m) : null;
      if (!s) {
        bad++;
        continue;
      }
      delete s.id;
      list.push([m.id, s]);
    }
    return { state: bad ? 'damaged' : 'good', list, text: bad ? text : '', bad };
  }
  // a restore: the device's scores go to the undo copy first, then the backup's are written (others stay, like tracks)
  async function putUndo() {
    await MDB.tx('undo', 'readwrite', (u) => u.put({ at: Date.now(), list: all() }, 'last'));
  }
  const clearUndo = () => MDB.tx('undo', 'readwrite', (u) => u.clear()).catch(() => {});
  async function restore(mel) {
    if (!mel) return;
    if (mel.state === 'damaged' && mel.text) await SAFE.rescue(mel.text, 'melody').catch(() => {});
    if (mel.list && mel.list.length) {
      await MDB.tx('melodies', 'readwrite', (st) => mel.list.forEach(([id, s]) => st.put(s, id)));
      mel.list.forEach(([id, s]) => scores.set(id, s));
    }
    reconcile();
  }
  async function undo() {
    const u = await MDB.tx('undo', 'readonly', (st) => st.get('last')).catch(() => null);
    if (!u || !Array.isArray(u.list)) return;
    await MDB.tx('melodies', 'readwrite', (st) => {
      st.clear();
      u.list.forEach((m) => {
        const s = m && typeof m.id === 'string' && cleanMelody(m);
        if (s) {
          delete s.id;
          st.put(s, m.id);
        }
      });
    });
    scores.clear();
    loading = null;
    loaded = false;
    await load();
  }

  /* ----- what a score says ----- */
  const NM = ['C', 'C♯', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B'];
  const nameOf = (m) => NM[((m % 12) + 12) % 12] + (Math.floor(m / 12) - 1);
  const sounding = (s) => s.notes.filter((n) => !MUTED.includes(n.flag)).map((n) => Object.assign({}, n, { midi: n.midi + 12 * (s.octave || 0) + (s.shift || 0) }));
  const MUTED = ['fret', 'range', 'jump'];
  // the score as sung, between two ticks: [{tick, len, midi}], muted notes left out (the guide and the dots, M1b)
  function line(s, from, to) {
    if (!s) return [];
    const a = from == null ? 0 : from,
      b = to == null ? Infinity : to;
    return sounding(s).filter((n) => n.tick + n.len > a && n.tick < b).map((n) => ({ tick: n.tick, len: n.len, midi: n.midi }));
  }
  // Q47 every note to draw between two ticks, muted ones too (drawn hollow), as sung: [{tick, len, midi, flag, i}]
  function drawn(s, from, to) {
    if (!s) return [];
    const a = from == null ? 0 : from,
      b = to == null ? Infinity : to,
      up = 12 * (s.octave || 0) + (s.shift || 0);
    const out = [];
    s.notes.forEach((n, i) => {
      if (n.tick + n.len > a && n.tick < b) out.push({ tick: n.tick, len: n.len, midi: n.midi + up, flag: n.flag || null, i });
    });
    return out;
  }
  // H35 the written line as points, one every 10 ms inside each note (seconds at the score's tempo and speed sp), so a
  // pitch line drawn or compared from it reads no gaps inside a note. Worked out when needed, never saved
  function points(s, from, to, sp) {
    if (!s) return [];
    const tps = (TPB * (s.tempo || 100)) / 60 * (sp || 1),
      out = [];
    line(s, from, to).forEach((n) => {
      const a = n.tick / tps,
        b = (n.tick + n.len) / tps;
      for (let t = a; t < b - 0.0001; t += 0.01) out.push({ t, m: n.midi });
    });
    return out;
  }
  function range(s) {
    const ns = sounding(s);
    if (!ns.length) return null;
    let lo = Infinity,
      hi = -Infinity;
    ns.forEach((n) => {
      lo = Math.min(lo, n.midi);
      hi = Math.max(hi, n.midi);
    });
    return { lo, hi };
  }
  // where a song sits (idea 2): the band holding the middle 60% of the sung time, weighted by note length, and how much
  // of the sung time is in your bridge, above your top and below your bottom
  function sits(s, voice) {
    const ns = sounding(s);
    if (!ns.length) return null;
    const byPitch = ns.slice().sort((a, b) => a.midi - b.midi),
      total = ns.reduce((a, n) => a + n.len, 0);
    const at = (f) => {
      let acc = 0;
      for (const n of byPitch) {
        acc += n.len;
        if (acc >= f * total) return n.midi;
      }
      return byPitch[byPitch.length - 1].midi;
    };
    const out = { lo: at(0.2), hi: at(0.8), bridge: 0, above: 0, below: 0 };
    const v = voice || (D.prefs && D.prefs.pat && D.prefs.pat.voice),
      b = v && v.bridge;
    ns.forEach((n) => {
      if (b && n.midi >= b.lo && n.midi <= b.hi) out.bridge += n.len;
      if (v && isFinite(v.hi) && n.midi > v.hi) out.above += n.len;
      if (v && isFinite(v.lo) && n.midi < v.lo) out.below += n.len;
    });
    out.bridge /= total;
    out.above /= total;
    out.below /= total;
    return out;
  }
  const share = (f) => (f < 0.05 ? '' : f < 0.15 ? 'a little' : f < 0.3 ? 'a quarter' : f < 0.42 ? 'a third' : f < 0.6 ? 'half' : 'most');
  function sitsText(s) {
    const t = sits(s);
    if (!t) return '';
    let w = 'sits ' + nameOf(t.lo) + (t.hi !== t.lo ? '–' + nameOf(t.hi) : '');
    const sb = share(t.bridge),
      sa = share(t.above);
    if (sb) w += ', ' + sb + ' in your bridge';
    if (sa) w += ', ' + sa + ' above your top';
    return w;
  }
  // the octave that fits Your voice: as written unless where it sits is more than 2 semitones outside your range
  // (decision 4: as written when Your voice isn't set)
  function suggest(r) {
    const v = D.prefs && D.prefs.pat && D.prefs.pat.voice;
    if (!v || !isFinite(v.lo) || !isFinite(v.hi)) return 0;
    const t = sits({ notes: r.notes, octave: 0, shift: 0 }, v);
    if (!t) return 0;
    const out = (k) => Math.max(0, v.lo - (t.lo + 12 * k)) + Math.max(0, t.hi + 12 * k - v.hi);
    if (out(0) <= 2) return 0;
    return [0, -1, 1].reduce((a, k) => (out(k) < out(a) ? k : a), 0);
  }
  // the key signature as keys: {major, minor}, spelled as the key sheet spells them
  const MAJ = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'],
    MIN = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B'];
  function keysOf(n) {
    const pc = n >= 0 ? (7 * n) % 12 : (5 * -n) % 12;
    return { major: { tonic: MAJ[pc], mode: 'major' }, minor: { tonic: MIN[(pc + 9) % 12], mode: 'minor' } };
  }
  const glyph = (t) => String(t).replace(/#/g, '♯').replace(/b/g, '♭');
  const keyText = (n) => {
    const k = keysOf(n);
    return glyph(k.major.tonic) + ' major or ' + glyph(k.minor.tonic) + ' minor';
  };
  const sigText = (n) => (n === 0 ? 'no sharps or flats' : Math.abs(n) + (n > 0 ? ' sharp' : ' flat') + (Math.abs(n) > 1 ? 's' : ''));
  const lastBar = (s) => s.bars.reduce((a, b) => Math.max(a, b.n + (b.bars || 1) - 1), 0);
  // the "to check" list: [{n, why}] from the bars' and notes' flags
  function checks(s) {
    const out = [],
      beats = (t) => {
        const b = t / TPB;
        return Number.isInteger(b) ? String(b) : Number.isInteger(b * 2) ? Math.floor(b) + (Math.floor(b) ? ' and a half' : 'half a') : b.toFixed(2);
      };
    if (s.repeats) out.push({ n: null, why: 'This print uses repeats; the order may be wrong.' });
    s.bars.forEach((b) => {
      const f = b.f || [];
      if (f.includes('sum')) out.push({ n: b.n, why: 'Adds up to ' + beats(b.len) + ' of ' + beats(b.exp || b.len) + ' beats. It plays as read.' });
      if (f.includes('empty')) out.push({ n: b.n, why: 'Nothing could be read in this bar.' });
      if (f.includes('multi')) out.push({ n: b.n, why: 'A rest’s bar count couldn’t be read, so it counts as one bar.' });
      if (f.includes('part')) out.push({ n: b.n, why: 'A note’s length couldn’t be read, so it’s left out.' });
      if (f.includes('silent')) out.push({ n: b.n, why: 'A note was read outside any voice, so it’s left silent.' });
      if (f.includes('repeat')) out.push({ n: b.n, why: 'A repeat sign. The bars are kept in printed order.' });
      if (f.includes('numbers')) out.push({ n: b.n, why: 'The print says bar ' + b.pn + ' here; the reader counted ' + b.n + '.' });
    });
    const barAt = (t) => {
      let n = null;
      for (const b of s.bars) if (b.tick <= t) n = b.n;
      return n;
    };
    const WHY = {
      fret: 'A tab number couldn’t be read, so the note is muted.',
      range: 'A note far outside the song’s range, so it’s muted.',
      jump: 'A one-note jump of 10 semitones or more, so it’s muted.',
      unsure: 'The tab and the notation disagree on a note. It plays as the tab says.',
    };
    s.notes.forEach((n) => {
      if (WHY[n.flag]) out.push({ n: barAt(n.tick), why: nameOf(n.midi) + ': ' + WHY[n.flag], note: true });
    });
    return out.sort((a, b) => (a.n == null ? -1 : b.n == null ? 1 : a.n - b.n));
  }
  const bytes = () => {
    let b = 0;
    prints.forEach((p) => (b += p.size));
    scores.forEach((s) => {
      try {
        b += JSON.stringify(s).length;
      } catch (e) {}
    });
    return b;
  };

  /* ----- reading a print ----- */
  const ERR = {
    notpdf: 'This isn’t a PDF.',
    damaged: 'This PDF can’t be opened.',
    notug: 'This doesn’t look like an Ultimate Guitar print. Print it from UG as notation plus tab.',
    guitar: 'This looks like a guitar part. Print the Vocals part.',
    toomuch: 'This print has more than a song’s worth of music, so it wasn’t read.',
    broken: 'Couldn’t read this print. Try printing it again from UG.',
  };
  function errText(code, info) {
    if (code === 'view')
      return info && info.want === 'notation'
        ? 'This print has the tab but no notation. In UG choose notation plus tab, then print again.'
        : 'This print has the notation but no tab. In UG choose notation plus tab, then print again.';
    if (code === 'few')
      return (
        'Only ' + (info.ok || 0) + ' of ' + (info.bars || 0) + ' bars could be read, too few to keep. Check it’s the notation plus tab view.'
      );
    return ERR[code] || ERR.broken;
  }
  function pick(target) {
    if (rec) return toast('Finish the take first');
    if (job) return toast('Still reading the last print');
    want = target;
    const el = $('melodyIn');
    if (el) el.click();
  }
  // where the picked PDF went: the tests hand a file straight in
  // opt (tests only): {nopdf: the Worker acts as if pdf.js won't load there, limits: smaller limits}
  async function start(file, target, ok, opt) {
    if (!file || !target) return;
    if (rec) return toast('Finish the take first');
    if (job) return toast('Still reading the last print');
    if (!ok && file.size > MAX_MB * MB) {
      big = { file, target };
      U.sheet = 'melBig';
      U.sd = { what: 'size', mb: Math.round(file.size / MB), ret: target.draft ? { sheet: 'sgNew', sd: {} } : null };
      return rerender();
    }
    let head = '';
    try {
      head = String.fromCharCode(...new Uint8Array(await file.slice(0, 5).arrayBuffer()));
    } catch (e) {}
    if (head !== '%PDF-') return toast(ERR.notpdf);
    const data = await file.arrayBuffer();
    const src = (q('link[href^="js/melodyread.js"]') || {}).getAttribute ? q('link[href^="js/melodyread.js"]').getAttribute('href') : 'js/melodyread.js';
    let w;
    try {
      w = new Worker(src);
    } catch (e) {
      return toast(ERR.broken);
    }
    job = { target, file, w, f: 0, line: 0, lines: 0, draft: target.draft ? U.sDraft : null };
    w.onmessage = (e) => onMsg(job && job.w === w ? job : null, e.data);
    w.onerror = () => end(job && job.w === w ? job : null, { type: 'fail', code: 'broken' });
    testOpt = opt || null;
    w.postMessage(Object.assign({ vs: 1, type: 'read', data, long: !!ok }, opt || {}), [data]);
    busy();
    rerender();
  }
  function onMsg(j, m) {
    if (!j || !m || !m.mine) return;
    if (m.type === 'progress') {
      j.f = m.f;
      if (m.lines) {
        j.line = m.line;
        j.lines = m.lines;
      }
      return busy();
    }
    if (m.type === 'ask') {
      // over 40 pages: ask first
      j.answered = false;
      U.sheet = 'melBig';
      U.sd = { what: 'pages', n: m.info && m.info.n, ret: j.target.draft ? { sheet: 'sgNew', sd: {} } : null };
      return rerender();
    }
    if (m.type === 'nopdf') return pagesHere(j);
    if (m.type === 'done' || m.type === 'fail') end(j, m);
  }
  // the fallback when pdf.js won't load inside the Worker: read the pictures here, a page at a time, and hand them over
  let pdfHere = null;
  function libHere() {
    if (!pdfHere)
      pdfHere = (async () => {
        if (!window.MELREAD)
          await new Promise((res, rej) => {
            const s = document.createElement('script');
            s.src = (q('link[href^="js/melodyread.js"]') || {}).getAttribute('href');
            s.onload = res;
            s.onerror = rej;
            document.head.appendChild(s);
          });
        const base = new URL('js/vendor/pdfjs-4.10.38/', location.href).href;
        const lib = await import(base + 'pdf.min.js');
        window.pdfjsWorker = await import(base + 'pdf.worker.min.js');
        return lib;
      })().catch((e) => {
        pdfHere = null;
        throw e;
      });
    return pdfHere;
  }
  async function pagesHere(j) {
    try {
      const lib = await libHere(),
        data = new Uint8Array(await j.file.arrayBuffer());
      await MELREAD.picturesFromPdf(lib, data, async (p, n, pics, text) => {
        if (job !== j) throw new Error('stopped');
        if (p === 0 && n > 40 && !(await askHere(n))) throw new Error('stopped');
        j.f = 0.04 + (0.16 * p) / Math.max(1, n);
        busy();
        if (pics && pics.length) j.w.postMessage({ vs: 1, type: 'page', pics, text }, pics.map((x) => x.g.buffer));
        else if (text) j.w.postMessage({ vs: 1, type: 'page', pics: [], text });
      });
      j.w.postMessage({ vs: 1, type: 'pages' });
    } catch (e) {
      if (job !== j) return;
      if (e && e.message === 'stopped') return cancel();
      j.w.postMessage({ vs: 1, type: 'pages', fail: 'damaged' });
    }
  }
  let askRes = null;
  const askHere = (n) =>
    new Promise((res) => {
      askRes = res;
      U.sheet = 'melBig';
      U.sd = { what: 'pages', n, here: true };
      rerender();
    });
  function answer(yes) {
    const sd = U.sd || {};
    asking = false;
    if (job) job.answered = true;
    U.sheet = null;
    U.sd = {};
    if (sd.what === 'size') {
      const b = big;
      big = null;
      if (sd.ret) {
        U.sheet = sd.ret.sheet;
        U.sd = sd.ret.sd || {};
      }
      rerender();
      if (yes && b) start(b.file, b.target, true, testOpt);
      return;
    }
    if (sd.here && askRes) {
      const r = askRes;
      askRes = null;
      r(yes);
    } else if (job) {
      if (yes) job.w.postMessage({ vs: 1, type: 'answer', yes: true });
      else return cancel();
    }
    if (sd.ret) {
      U.sheet = sd.ret.sheet;
      U.sd = sd.ret.sd || {};
    }
    rerender();
  }
  // after every draw: the big or long PDF question closed some other way (Cancel, ✕, a swipe) means no
  let asking = false;
  function after() {
    if (U.sheet === 'melBig') asking = true;
    else if (asking) {
      asking = false;
      if (big) big = null;
      if (askRes) {
        const r = askRes;
        askRes = null;
        r(false);
      } else if (job && !job.answered) cancel();
    }
  }
  function cancel() {
    const j = job;
    if (!j) return;
    try {
      j.w.terminate();
    } catch (e) {}
    job = null;
    busy();
    if (U.sheet === 'melBig') {
      U.sheet = j.target.draft && U.sDraft ? 'sgNew' : null;
      U.sd = {};
    }
    rerender();
    toast('Stopped reading');
  }
  function end(j, m) {
    if (!j || job !== j) return;
    try {
      j.w.terminate();
    } catch (e) {}
    job = null;
    busy();
    if (U.sheet === 'melBig') {
      U.sheet = j.target.draft && U.sDraft ? 'sgNew' : null;
      U.sd = {};
    }
    if (m.type === 'fail') {
      if (m.code === 'stopped') return rerender();
      rerender();
      return toast(errText(m.code, m.info || {}), 5000, 'long');
    }
    const r = m.r;
    r.pages = r.pages || 0;
    // the read belongs to its song: dropped if the song (or the New song sheet it was for) has gone
    if (j.target.draft) {
      if (!U.sDraft || U.sDraft !== j.draft) return rerender();
      return toDraft(r, j.file);
    }
    const sg = songById(j.target.id);
    if (!sg) return rerender();
    held = { target: j.target, r, file: j.file, step: 0 };
    const here = U.view === 'lyr' && U.songId === sg.id && !U.sheet;
    if (!here) {
      rerender();
      return toastBtn('Sheet ready', 'Open', () => {
        if (!held || !songById(held.target.id)) return;
        openSong(held.target.id);
        next();
      }, 8000);
    }
    next();
  }
  // the questions after a read, in order: same print on another song, title differs, a second print; then the sheet
  function next() {
    const h = held;
    if (!h) return rerender();
    const sg = songById(h.target.id);
    if (!sg) {
      held = null;
      return rerender();
    }
    const ugId = h.r.ug && h.r.ug.id;
    if (h.step < 1) {
      h.step = 1;
      const other = ugId && D.songs.find((s) => s.id !== sg.id && noteOf(s) && noteOf(s).ug === ugId);
      if (other) {
        U.sheet = 'melSame';
        U.sd = { k: other.id };
        return rerender();
      }
    }
    if (h.step < 2) {
      h.step = 2;
      if (h.r.ug && h.r.ug.title && !sameTitle(h.r.ug.title, sg.name)) {
        U.sheet = 'melTitle';
        U.sd = {};
        return rerender();
      }
    }
    if (h.step < 3) {
      h.step = 3;
      if (scores.has(sg.id)) {
        U.sheet = 'melReplace';
        U.sd = {};
        return rerender();
      }
    }
    h.octave = h.octave != null ? h.octave : scores.has(sg.id) ? scores.get(sg.id).octave || 0 : suggest(h.r);
    h.tempo = h.tempo || (scores.has(sg.id) ? scores.get(sg.id).tempo : 100);
    U.sheet = 'melRead';
    U.sd = { k: sg.id };
    rerender();
  }
  const words = (t) =>
    String(t || '')
      .toLowerCase()
      .replace(/\(.*?\)|\[.*?\]/g, ' ')
      .replace(/[^a-z0-9]+/g, ' ')
      .trim();
  const sameTitle = (a, b) => {
    const x = words(a),
      y = words(b);
    return !!x && !!y && (x === y || x.includes(y) || y.includes(x));
  };
  // a read for the New song sheet: its title and artist fill empty fields, and the score is saved with the song
  function toDraft(r, file) {
    const d = U.sDraft;
    const ugId = r.ug && r.ug.id,
      other = ugId && D.songs.find((s) => noteOf(s) && noteOf(s).ug === ugId);
    d.melody = { r, file, name: (r.ug && r.ug.title) || String(file.name || 'Sheet music').replace(/\.pdf$/i, '') };
    if (!d.title && r.ug && r.ug.title) d.title = r.ug.title;
    if (!d.artist && r.ug && r.ug.artist) d.artist = r.ug.artist;
    d.mode = 'media';
    d.err = '';
    if (other) {
      U.sheet = 'melSame';
      U.sd = { k: other.id, draft: true };
    } else U.sheet = 'sgNew';
    rerender();
  }
  // New song's Save: the score goes in once the song exists (the score, then the note)
  async function attachDraft(sg, m) {
    if (!m || !m.r) return true;
    try {
      await keep(sg, m.r, m.file, { octave: suggest(m.r), tempo: 100 });
      return true;
    } catch (e) {
      toast('Couldn’t save the sheet music. Storage may be full.', 4000, 'long');
      return false;
    }
  }
  async function saveRead() {
    const h = held,
      sg = h && songById(h.target.id);
    if (!sg) {
      held = null;
      U.sheet = null;
      return rerender();
    }
    readFields(h);
    try {
      await keep(sg, h.r, h.file, h);
    } catch (e) {
      held = null;
      U.sheet = null;
      rerender();
      return toast(e instanceof Stale ? 'Sheet music changed in another window. Showing the latest.' : 'Couldn’t save the sheet music. Storage may be full.', 4000, 'long');
    }
    held = null;
    U.sheet = null;
    U.sd = {};
    rerender();
    toast('Sheet music saved');
    offerKey(sg);
  }
  // the key from the print, offered through the key sheet (VS-098): never set without asking
  function offerKey(sg) {
    const s = scores.get(sg.id);
    if (!s || typeof SONGKEY === 'undefined') return;
    const k = keysOf(s.key),
      cur = SONGKEY.of(sg);
    if (cur && ((cur.tonic === k.major.tonic && cur.mode === 'major') || (cur.tonic === k.minor.tonic && cur.mode === 'minor'))) return;
    SONGKEY.open(sg.id);
    // a song with a key keeps it chosen; one without starts on the print's major (major or minor is asked there)
    U.sd = Object.assign(U.sd || {}, cur ? {} : { tonic: k.major.tonic, mode: 'major' }, { from: keyText(s.key) });
    rerender();
  }

  /* ----- the reading pill (VS-106) ----- */
  let pill = null;
  function busy() {
    if (job && !pill) {
      pill = document.createElement('div');
      pill.className = 'melbusy glass';
      pill.setAttribute('role', 'status');
      pill.innerHTML = '<span class="melbusy-t"></span><button class="melbusy-x" data-a="melCancel">Cancel</button>';
      document.body.appendChild(pill);
      if (typeof SCR !== 'undefined' && SCR.mark) SCR.mark(pill, 'overlay:melread');
    } else if (!job && pill) {
      pill.remove();
      pill = null;
    }
    if (pill) pill.querySelector('.melbusy-t').textContent = busyText();
    const r = q('#app [data-a="melAdd"][aria-busy] small, #layer .sgdrop.melbusyd span');
    if (r) r.textContent = busyText();
  }
  const busyText = () => (!job ? '' : job.lines ? 'Reading line ' + job.line + ' of ' + job.lines : 'Opening the print');

  /* ----- screens ----- */
  const TILE =
    '<span class="tile" style="background:var(--sys-pink)">' +
    GL('<path d="M3 7.5h18M3 11.5h18M3 15.5h18"/><circle cx="9.5" cy="15.5" r="2.3" fill="currentColor"/><path d="M11.8 15.5V5.5l4.5 1.2"/>') +
    '</span>';
  // the Song page's Practice group (VS-009 › sheet-music-row)
  function row(sg) {
    const s = scores.get(sg.id),
      note = noteOf(sg),
      reading = job && job.target.id === sg.id;
    if (reading)
      return (
        '<button class="row" data-a="melAdd" data-k="' + sg.id + '" aria-busy="true">' + TILE +
        '<span class="lbl">Reading the print…<small>' + esc(busyText()) + '</small></span></button>'
      );
    if (s) {
      const rg = range(s),
        n = checks(s).length,
        k = SONGKEY && SONGKEY.of(sg),
        bits = [k ? SONGKEY.label(k) : sigText(s.key), lastBar(s) + ' bars'];
      if (rg) bits.push(nameOf(rg.lo) + '–' + nameOf(rg.hi));
      const st = sitsText(s);
      if (st) bits.push(st);
      if (n) bits.push(n + ' to check');
      return (
        '<button class="row" data-zk="mel:' + sg.id + '" data-a="melOpen" data-k="' + sg.id + '">' + TILE +
        '<span class="lbl">Sheet music<small>' + esc(bits.join(' · ')) + '</small></span>' + chev + '</button>'
      );
    }
    if (note && !loaded)
      return '<div class="row">' + TILE + '<span class="lbl">Sheet music<small>Loading…</small></span></div>';
    const miss = !!note;
    return (
      '<button class="row" data-a="melAdd" data-k="' + sg.id + '"' + (rec ? ' aria-disabled="true"' : '') + '>' + TILE +
      '<span class="lbl">' + (miss ? 'Sheet not on this device' : 'Add sheet music') + '<small>' +
      (rec ? 'Finish the take first' : miss ? 'Add the print again to read it' : 'A UG print as PDF: its notes, bars and key') +
      '</small></span>' + (miss ? '<span class="acc trkadd">Add</span>' : chev) + '</button>'
    );
  }
  // the settings a read or a score has: the octave (Lower · As written · Higher) and the tempo (± by 1, or typed)
  function controls(oct, tempo, note) {
    return (
      '<div class="hdr">Octave</div><div class="seg pk-seg wide meloct" role="group" aria-label="Octave"><span class="pk-seg-ind" aria-hidden="true"></span>' +
      [[-1, 'Lower'], [0, 'As written'], [1, 'Higher']]
        .map((x) => '<button data-a="melOct" data-v="' + x[0] + '" class="' + (x[0] === oct ? 'on' : '') + '" aria-pressed="' + (x[0] === oct) + '">' + x[1] + '</button>')
        .join('') +
      '</div>' + (note ? '<p class="foot">' + note + '</p>' : '') +
      '<div class="hdr">Tempo</div><div class="grp"><div class="row meltempo"><span class="lbl">Beats a minute</span>' +
      '<button class="shbtn glass" data-a="melTempo" data-v="-1" aria-label="Slower">−</button>' +
      '<input class="field" id="melTempoIn" type="number" inputmode="numeric" min="20" max="300" value="' + tempo + '" aria-label="Tempo">' +
      '<button class="shbtn glass" data-a="melTempo" data-v="1" aria-label="Faster">+</button></div></div>' +
      '<p class="foot">Type the tempo printed at the top of the print, the number after ♩=.</p>'
    );
  }
  function checkList(list, all) {
    if (!list.length) return '<div class="grp"><div class="row"><span class="lbl">Every bar adds up</span></div></div>';
    const shown = all ? list : list.slice(0, 4);
    return (
      '<div class="grp melchecks">' +
      shown.map((c) => '<div class="row"><span class="lbl">' + (c.n != null ? 'Bar ' + c.n : 'The whole print') + '<small>' + esc(c.why) + '</small></span></div>').join('') +
      (!all && list.length > 4 ? '<button class="row" data-a="melAll"><span class="lbl acc">Show all ' + list.length + '</span></button>' : '') +
      '</div>'
    );
  }
  function summary(s, title) {
    const rg = range(s),
      st = sitsText(s);
    return (
      '<div class="grp">' +
      (title ? '<div class="row"><span class="lbl">' + esc(title) + '</span></div>' : '') +
      '<div class="row"><span class="lbl">Key signature<small>' + esc(sigText(s.key) + ': ' + keyText(s.key)) + '</small></span></div>' +
      '<div class="row"><span class="lbl">Bars<small>' + lastBar(s) + ' · ' + s.time[0] + '/' + s.time[1] + '</small></span></div>' +
      (rg ? '<div class="row"><span class="lbl">Range<small>' + nameOf(rg.lo) + '–' + nameOf(rg.hi) + (st ? ' · ' + esc(st) : '') + '</small></span></div>' : '') +
      '</div>'
    );
  }
  const octNote = (k, set) =>
    !set ? 'Your voice isn’t set, so it’s as written in the tab.' : k === 0 ? 'As written suits Your voice.' : 'Moved ' + (k < 0 ? 'down' : 'up') + ' an octave to suit Your voice.';
  const voiceSet = () => !!(D.prefs && D.prefs.pat && D.prefs.pat.voice);
  function sheet(s) {
    const sd = U.sd || {};
    if (s === 'melRead' && held) {
      // VS-100 Sheet music read: what was read, the octave and tempo, the to-check list, Save
      const r = held.r,
        sg = songById(held.target.id);
      if (!sg) return '';
      const pv = { notes: r.notes, bars: r.bars, octave: held.octave || 0, shift: 0, key: r.key, time: r.time, repeats: r.repeats };
      const sug = suggest(r);
      return sheetWrap(
        'Sheet music read',
        '<p class="note">' + esc(r.ug && r.ug.title ? r.ug.title + (r.ug.artist ? ' by ' + r.ug.artist : '') : sg.name) + '</p>' +
          summary(pv) +
          controls(held.octave || 0, held.tempo || 100, octNote(sug, voiceSet())) +
          '<div class="hdr">To check</div>' + checkList(checks(pv), sd.all) +
          '<div style="margin-top:14px"><button class="cta" data-a="melSave">Save sheet music</button></div><button class="ghost" data-a="melDrop">Cancel</button>',
        'Sheet music read'
      );
    }
    if (s === 'melSheet') {
      // VS-099 Sheet music: the score's summary, octave and tempo, the song's key, the to-check list, Replace
      const sg = songById(sd.k),
        sc = sg && scores.get(sg.id);
      if (!sc) return '';
      const p = prints.get(sg.id),
        k = SONGKEY && SONGKEY.of(sg);
      return sheetWrap(
        'Sheet music',
        summary(sc, sc.ug && sc.ug.title ? sc.ug.title + (sc.ug.artist ? ' by ' + sc.ug.artist : '') : '') +
          controls(sc.octave || 0, sc.tempo || 100, '') +
          '<div class="hdr">Song key</div><div class="grp"><button class="row" data-a="melKey" data-k="' + sg.id + '"><span class="lbl">' +
          (k ? esc(SONGKEY.label(k)) : 'Not set') + '<small>From the print: ' + esc(keyText(sc.key)) + '</small></span>' + chev + '</button></div>' +
          '<div class="hdr">To check</div>' + checkList(checks(sc), sd.all) +
          '<div class="hdr">Print</div><div class="grp"><div class="row"><span class="lbl">' +
          (p ? esc(p.name || 'Print') + '<small>' + mb(p.size) + (p.pages ? ' · ' + p.pages + ' page' + (p.pages > 1 ? 's' : '') : '') + ' · on this ' + deviceName() + ' only</small>' : 'Print not on this device<small>The score is kept; the print isn’t</small>') +
          '</span></div><button class="row" data-a="melReplaceAsk" data-k="' + sg.id + '"><span class="lbl acc">Replace with a new print…</span></button></div>',
        'Sheet music'
      );
    }
    if (s === 'melSame') {
      // VS-101 the same UG print is on another song
      const o = songById(sd.k);
      if (!o) return '';
      return choiceSheet(
        'Already on another song',
        '<p class="note">This print is already on ' + esc(o.name) + '.</p>' +
          '<button class="row" data-a="melSameOpen" data-k="' + o.id + '"><span class="lbl">Open ' + esc(o.name) + '</span></button>' +
          '<button class="row" data-a="melSameGo"><span class="lbl">Add it here too</span></button>' +
          '<button class="row" data-a="melDrop"><span class="lbl">Cancel</span></button>'
      );
    }
    if (s === 'melTitle' && held) {
      // VS-102 the print's title isn't the song's
      const sg = songById(held.target.id),
        u = held.r.ug || {};
      if (!sg) return '';
      return choiceSheet(
        'A different song?',
        '<p class="note">This print is ' + esc(u.title || 'another song') + (u.artist ? ' by ' + esc(u.artist) : '') + '.</p>' +
          '<button class="row" data-a="melTitleHere"><span class="lbl">Add it to ' + esc(sg.name) + '</span></button>' +
          '<button class="row" data-a="melTitleNew"><span class="lbl">Make a new song</span></button>' +
          '<button class="row" data-a="melDrop"><span class="lbl">Cancel</span></button>'
      );
    }
    if (s === 'melReplace')
      // VS-103 a second print for a song that has sheet music
      return confirmSheet(
        'Replace the sheet music?',
        'The old score is kept in the safety copies for 30 days. Its octave and settings carry over.',
        'Replace',
        'melReplaceYes'
      );
    if (s === 'melBig')
      // VS-104 a big or long PDF: ask first
      return confirmSheet(
        sd.what === 'pages' ? 'This PDF is long' : 'This PDF is big',
        sd.what === 'pages'
          ? 'It has ' + (sd.n || 'over 40') + ' pages. A UG print of one song is usually under 10. Read it anyway?'
          : 'It is ' + (sd.mb || 'over 30') + ' MB. UG prints are usually under 5 MB. Read it anyway?',
        'Read it anyway',
        'melBigYes',
        '',
        'Cancel'
      );
    if (s === 'melPrintsDel')
      // VS-105 Settings › Storage › Remove prints, keep scores
      return confirmSheet(
        'Remove the prints?',
        'The PDFs go from this ' + deviceName() + '. Every song keeps its sheet music score, so nothing else changes.',
        'Remove prints',
        'melPrintsYes'
      );
    if (s === 'melOrphanDel')
      return confirmSheet('Delete this sheet music?', 'Its song isn’t on this ' + deviceName() + ' any more. The score and its print go.', 'Delete', 'melOrphanYes', sd.k);
    return '';
  }
  function readFields(h) {
    const el = q('#melTempoIn');
    if (el && h) h.tempo = clamp(+el.value, 20, 300, h.tempo || 100);
  }
  // Settings › Storage: the Sheet music rows
  function storageRows() {
    if (!scores.size && !prints.size) return '';
    let pb = 0;
    prints.forEach((p) => (pb += p.size));
    let h =
      '<div class="row"><span class="lbl">Sheet music<small>' + scores.size + ' score' + (scores.size === 1 ? '' : 's') + ' · ' + prints.size + ' print' + (prints.size === 1 ? '' : 's') + '</small></span><span class="mut">' + mb(bytes()) + '</span></div>';
    if (prints.size) h += '<button class="row" data-a="sheet" data-v="melPrintsDel"><span class="lbl dng">Remove prints, keep scores<small>Frees ' + mb(pb) + '</small></span></button>';
    return h;
  }
  function orphanRows() {
    const o = orphans();
    if (!o.length) return '';
    return (
      '<div class="hdr">Sheets with no song</div><div class="grp">' +
      o.map((id) => {
        const s = scores.get(id);
        return '<button class="row" data-a="sheet" data-v="melOrphanDel" data-k="' + id + '"><span class="lbl">' + esc((s.ug && s.ug.title) || 'Sheet music') + '<small>' + lastBar(s) + ' bars</small></span><span class="dng">Delete</span></button>';
      }).join('') +
      '</div>'
    );
  }

  /* ----- actions ----- */
  Object.assign(SG_ACT, {
    melAdd: (el, v, k) => {
      if (rec) return toast('Finish the take first');
      if (job && job.target.id === k) return;
      pick({ id: k });
    },
    melOpen: (el, v, k) => MELPLAY.open(k), // Q47 the Sheet music page (melodyplay.js)
    melInfo: (el, v, k) => {
      // Q47 VS-099, from the page's top bar
      U.sheet = 'melSheet';
      U.sd = { k: k || U.songId };
      rerender();
    },
    melAll: () => {
      readFields(held);
      U.sd = Object.assign({}, U.sd, { all: true });
      rerender();
    },
    melCancel: () => cancel(),
    melBigYes: () => answer(true),
    melOct: (el, v) => {
      const k = clamp(+v, -1, 1, 0);
      segPick(el);
      if (U.sheet === 'melRead' && held) {
        readFields(held);
        held.octave = k;
        return rerender();
      }
      const id = (U.sd || {}).k;
      if (scores.has(id)) edit(id, { octave: k });
    },
    melTempo: (el, v) => {
      if (U.sheet === 'melRead' && held) {
        readFields(held);
        held.tempo = clamp((held.tempo || 100) + +v, 20, 300, 100);
        return rerender();
      }
      const id = (U.sd || {}).k,
        s = scores.get(id);
      if (s) edit(id, { tempo: clamp((s.tempo || 100) + +v, 20, 300, 100) });
    },
    melSave: () => saveRead(),
    melDrop: () => {
      const d = (U.sd || {}).draft;
      held = null;
      if (d && U.sDraft) {
        delete U.sDraft.melody;
        U.sheet = 'sgNew';
      } else U.sheet = null;
      U.sd = {};
      rerender();
    },
    melSameOpen: (el, v, k) => {
      held = null;
      if (U.sDraft && (U.sd || {}).draft) delete U.sDraft.melody;
      U.sDraft = null;
      U.sheet = null;
      U.sd = {};
      openSong(k);
    },
    melSameGo: () => {
      if ((U.sd || {}).draft) {
        U.sheet = 'sgNew';
        U.sd = {};
        return rerender();
      }
      next();
    },
    melTitleHere: () => next(),
    // the print is a different song: a New song sheet opens with it, the title and artist from the print
    melTitleNew: () => {
      const h = held;
      held = null;
      if (!h) return;
      U.sDraft = { step: 1, title: '', artist: '', text: '', mode: 'media' };
      U.sheet = 'sgNew';
      U.sd = {};
      toDraft(h.r, h.file);
    },
    melReplaceAsk: (el, v, k) => {
      U.sheet = null;
      U.sd = {};
      rerender();
      pick({ id: k });
    },
    melReplaceYes: () => next(),
    melKey: (el, v, k) => {
      const s = scores.get(k),
        sg = songById(k);
      if (!sg || typeof SONGKEY === 'undefined') return;
      SONGKEY.open(k);
      if (s && !SONGKEY.of(sg)) {
        const ks = keysOf(s.key);
        U.sd = Object.assign(U.sd || {}, { tonic: ks.major.tonic, mode: 'major' });
      }
      if (s) U.sd.from = keyText(s.key);
      rerender();
    },
    melPrintsYes: async () => {
      try {
        await removePrints();
        U.sheet = null;
        rerender();
        toast('Prints removed. Scores kept.');
      } catch (e) {
        toast('Couldn’t remove the prints');
      }
    },
    melOrphanYes: async (el, v, k) => {
      await forget([k]);
      U.sheet = null;
      rerender();
      toast('Sheet music deleted');
    },
    sgAddPdf: () => {
      if (typeof sgReadDraft === 'function') sgReadDraft();
      pick({ draft: true });
    },
  });
  document.addEventListener('change', (e) => {
    const t = e.target;
    if (t && t.id === 'melodyIn') {
      const f = t.files && t.files[0],
        w = want;
      t.value = '';
      want = null;
      if (f && w) start(f, w);
    } else if (t && t.id === 'melTempoIn') {
      const v = clamp(+t.value, 20, 300, null);
      if (v == null) return rerender();
      if (U.sheet === 'melRead' && held) {
        held.tempo = v;
        return;
      }
      const id = (U.sd || {}).k;
      if (scores.has(id)) edit(id, { tempo: v });
    }
  });

  return {
    TPB,
    cleanMelody,
    cleanNote,
    load,
    loaded: () => loaded,
    get: (id) => (scores.has(id) ? JSON.parse(JSON.stringify(scores.get(id))) : null),
    has: (id) => scores.has(id),
    hasPrint: (id) => prints.has(id),
    print: (id) => (prints.has(id) ? Object.assign({}, prints.get(id)) : null),
    line,
    drawn,
    points,
    cut,
    _cutOpt: (o) => (cutOpt = o || null),
    range,
    sits,
    suggest,
    keysOf,
    checks,
    bytes,
    row,
    sheet,
    storageRows,
    orphanRows,
    orphans,
    forget,
    removePrints,
    all,
    code,
    inspect,
    putUndo,
    clearUndo,
    restore,
    undo,
    reconcile,
    after,
    attachDraft,
    pick,
    start,
    cancel,
    edit,
    busyText,
    reading: () => (job ? { id: job.target.id || null, draft: !!job.target.draft, f: job.f, line: job.line, lines: job.lines } : null),
    held: () => (held ? { id: held.target.id, step: held.step, octave: held.octave, tempo: held.tempo } : null),
    // tests: put a score in as if read (no PDF), and add an upgrade step
    _put: put,
    async _reloadAll() {
      scores.clear();
      prints.clear();
      loading = null;
      loaded = false;
      await load();
    },
    _testUpgrade(fn) {
      V += 1;
      UPGRADES[V] = fn;
      return V;
    },
  };
})();
