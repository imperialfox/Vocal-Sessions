/* ===== The shared pitch listener (Q37) =====
   PITCH reads the notes in a voice: after recording, from a take (its pitch line, sudden jumps and held notes), and
   live, from the microphone while recording. It's one shared piece, like the pattern player, so the song ladder (Q37),
   bridge-aware patterns (Q38) and key and scale lanes (Q39) all read the voice the same way.
   - The detector is pitchy 4.1.0 (McLeod method, MIT), pinned as js/pitchy.js (the global Pitchy).
   - A take's line (ofTake): the take decoded once, then a pitch every 10 ms over a 2048-sample window. Quiet frames are
     skipped, a pitch needs clarity 0.90, islands under 40 ms are dropped, octave slips are fixed against the median of
     the 150 ms either side, and a 25 ms median smooths it. Lines are worked out when needed and kept in memory only:
     never saved and never backed up. forget(id) lets one go.
   - Jumps: 2 semitones or more within 200 ms, with the pitch steady (within 1.2) for 50 ms either side.
   - Held notes: 250 ms or more within 1 semitone.
   - Live (live): reads the recording's own analyser (rec.mic.analyser(), Q16's shared audio service) on the one frame
     clock (AUDIO.frame), never a second microphone or context, and looks nothing up on the page per frame.
   - Lines are MIDI note numbers (60 is C4, fractions are cents); NaN where no pitch was read.
   - svg() and spark() draw lines for any screen: note rows, overlaid lines aligned at their first note, a marker. */
const PITCH = (() => {
  const SET = Object.freeze({
    hop: 0.01, // seconds between readings
    win: 2048, // samples in each reading
    rate: 44100, // what takes are decoded at
    clarity: 0.9, // how clear a reading must be
    fLo: 60, // Hz: lower than any singing voice reads as noise
    fHi: 1500,
    quiet: 0.04, // a frame quieter than this share of the loudest is skipped
    floor: 0.003, // and anything under this, however quiet the take
    island: 0.04, // s: readings shorter than this are dropped
    octave: 0.15, // s either side for the octave check
    smooth: 0.025, // s: the median that smooths the line
    jump: { semi: 2, within: 0.2, steady: 1.2, side: 0.05 },
    held: { min: 0.25, within: 1 },
    part: { min: 0.1, semi: 0.6 },
  });
  const NAMES = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'];
  const name = (m) => NAMES[((Math.round(m) % 12) + 12) % 12] + (Math.floor(Math.round(m) / 12) - 1);
  const midi = (f) => 69 + 12 * Math.log2(f / 440);
  const hz = (m) => 440 * Math.pow(2, (m - 69) / 12);
  const has = () => typeof Pitchy !== 'undefined' && !!Pitchy.PitchDetector;
  const dets = {};
  function det(n) {
    if (!has()) return null;
    if (!dets[n]) {
      dets[n] = Pitchy.PitchDetector.forFloat32Array(n);
      dets[n].clarityThreshold = SET.clarity;
    }
    return dets[n];
  }
  const median = (a) => {
    const b = a.slice().sort((x, y) => x - y);
    return b[b.length >> 1];
  };

  /* ----- a whole recording: its line ----- */
  // data: one channel of samples (Float32Array), sr: its rate. Returns the line and what's known about it
  function line(data, sr) {
    const W = SET.win,
      hop = Math.max(1, Math.round(sr * SET.hop)),
      n = data && data.length >= W ? Math.floor((data.length - W) / hop) + 1 : 0,
      raw = new Float32Array(n).fill(NaN),
      rms = new Float32Array(n),
      d = det(W);
    let loud = 0;
    for (let i = 0; i < n; i++) {
      let s = 0;
      for (let k = i * hop, e = k + W; k < e; k += 4) s += data[k] * data[k];
      rms[i] = Math.sqrt(s / (W / 4));
      if (rms[i] > loud) loud = rms[i];
    }
    const gate = Math.max(SET.floor, loud * SET.quiet);
    if (d)
      for (let i = 0; i < n; i++) {
        if (rms[i] < gate) continue;
        const [f, c] = d.findPitch(data.subarray(i * hop, i * hop + W), sr);
        if (c >= SET.clarity && f > SET.fLo && f < SET.fHi) raw[i] = midi(f);
      }
    return shape(raw, data ? data.length / sr : 0);
  }
  // readings (one per hop) into a clean line: islands dropped, octave slips fixed, smoothed
  function shape(m, dur) {
    const n = m.length,
      isl = Math.round(SET.island / SET.hop),
      oct = Math.round(SET.octave / SET.hop),
      sm = Math.floor(SET.smooth / SET.hop / 2);
    for (let i = 0; i < n; ) {
      if (isNaN(m[i])) {
        i++;
        continue;
      }
      let j = i;
      while (j < n && !isNaN(m[j])) j++;
      if (j - i < isl) for (let k = i; k < j; k++) m[k] = NaN;
      i = j;
    }
    const s = m.slice();
    for (let i = 0; i < n; i++) {
      if (isNaN(m[i])) continue;
      const near = [];
      for (let k = Math.max(0, i - oct); k <= Math.min(n - 1, i + oct); k++) if (!isNaN(m[k])) near.push(m[k]);
      const r = median(near);
      if (Math.abs(m[i] - r - 12) < 0.8) s[i] = m[i] - 12;
      else if (Math.abs(m[i] - r + 12) < 0.8) s[i] = m[i] + 12;
    }
    const out = s.slice();
    for (let i = 0; i < n; i++) {
      if (isNaN(s[i])) continue;
      const near = [];
      for (let k = Math.max(0, i - sm); k <= Math.min(n - 1, i + sm); k++) if (!isNaN(s[k])) near.push(s[k]);
      out[i] = median(near);
    }
    let first = 0;
    while (first < n && isNaN(out[first])) first++;
    const all = [];
    for (let i = 0; i < n; i++) if (!isNaN(out[i])) all.push(out[i]);
    all.sort((a, b) => a - b);
    return {
      s: out,
      n,
      hop: SET.hop,
      first: first < n ? first : -1,
      firstT: first < n ? first * SET.hop : 0,
      dur: dur || n * SET.hop,
      lo: all.length ? all[Math.floor(all.length * 0.01)] : null,
      hi: all.length ? all[Math.min(all.length - 1, Math.floor(all.length * 0.99))] : null,
      read: n ? all.length / n : 0, // how much of it read as a note
    };
  }
  // the pitch's spread over frames a..b; any gap counts as unsteady
  function spread(s, a, b) {
    let mn = Infinity,
      mx = -Infinity;
    for (let k = Math.max(0, a); k <= Math.min(s.length - 1, b); k++) {
      const v = s[k];
      if (isNaN(v)) return Infinity;
      if (v < mn) mn = v;
      if (v > mx) mx = v;
    }
    return mx - mn;
  }
  // sudden jumps (cracks and flips): {t, from, to}, t from the first note
  function jumps(a) {
    const s = a.s,
      J = SET.jump,
      within = Math.round(J.within / a.hop),
      side = Math.round(J.side / a.hop),
      out = [];
    let prev = -1;
    for (let i = 0; i < a.n; i++) {
      if (isNaN(s[i])) continue;
      if (
        prev >= 0 &&
        i - prev <= within &&
        Math.abs(s[i] - s[prev]) >= J.semi &&
        spread(s, prev - side, prev) <= J.steady &&
        spread(s, i, i + side) <= J.steady
      ) {
        out.push({ t: i * a.hop - a.firstT, from: s[prev], to: s[i] });
        prev = i;
        i += side;
        continue;
      }
      prev = i;
    }
    return out;
  }
  // held notes: {t, d, m}, t from the first note, m the median (not rounded)
  function held(a) {
    const s = a.s,
      H = SET.held,
      min = Math.round(H.min / a.hop),
      out = [];
    for (let i = 0; i < a.n; ) {
      if (isNaN(s[i])) {
        i++;
        continue;
      }
      let lo = s[i],
        hi = s[i],
        j = i + 1;
      while (j < a.n && !isNaN(s[j]) && Math.max(hi, s[j]) - Math.min(lo, s[j]) <= H.within) {
        lo = Math.min(lo, s[j]);
        hi = Math.max(hi, s[j]);
        j++;
      }
      if (j - i >= min) {
        out.push({ t: i * a.hop - a.firstT, d: (j - i) * a.hop, m: median(Array.from(s.subarray(i, j))) });
        i = j;
      } else i++;
    }
    return out;
  }
  // where line b parts from line a, both aligned at their first note: the longest run (100 ms or more) where b is more
  // than 0.6 semitone from a. {at, len, t} (seconds from the first note; t is its middle), or null when they don't
  function part(a, b) {
    if (!a || !b || a.first < 0 || b.first < 0) return null;
    const P = SET.part,
      min = Math.round(P.min / SET.hop),
      n = Math.min(a.n - a.first, b.n - b.first);
    let best = null,
      run = 0,
      start = 0;
    const close = () => {
      if (run >= min && (!best || run > best.run)) best = { k: start, run };
      run = 0;
    };
    for (let k = 0; k < n; k++) {
      const va = a.s[a.first + k],
        vb = b.s[b.first + k],
        far = !isNaN(va) && !isNaN(vb) && Math.abs(va - vb) > P.semi;
      if (far) {
        if (!run) start = k;
        run++;
      } else close();
    }
    close();
    if (!best) return null;
    return { at: best.k * SET.hop, len: best.run * SET.hop, t: (best.k + best.run / 2) * SET.hop };
  }

  /* ----- takes: decoded once, read when needed, kept in memory only ----- */
  const lines = new Map(); // take id → Promise of its line (or null)
  const done = new Map(); // take id → its line, once read
  function decode(blob) {
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!OAC || !blob) return Promise.reject(new Error('no audio'));
    return blob.arrayBuffer().then((buf) => {
      let ctx = null;
      for (const r of [SET.rate, 48000, 22050])
        try {
          ctx = new OAC(1, 1, r);
          break;
        } catch (e) {}
      if (!ctx) throw new Error('no audio');
      return new Promise((res, rej) => {
        try {
          const p = ctx.decodeAudioData(buf, res, rej); // callbacks for older Safari, a promise elsewhere
          if (p && p.then) p.then(res, rej);
        } catch (e) {
          rej(e);
        }
      });
    });
  }
  // one channel: the louder one (a headset can give the voice on one side only)
  function channel(ab) {
    let best = ab.getChannelData(0),
      top = -1;
    for (let c = 0; c < ab.numberOfChannels; c++) {
      const d = ab.getChannelData(c);
      let s = 0;
      for (let i = 0; i < d.length; i += 64) s += d[i] * d[i];
      if (s > top) {
        top = s;
        best = d;
      }
    }
    return best;
  }
  function ofBlob(blob) {
    return decode(blob).then((ab) => line(channel(ab), ab.sampleRate));
  }
  function ofTake(id) {
    if (lines.has(id)) return lines.get(id);
    const t = typeof TAKES !== 'undefined' ? TAKES.find((x) => x.id === id) : null;
    const p = t
      ? ofBlob(t.blob)
          .then((a) => (done.set(id, a), a))
          .catch(() => null)
      : Promise.resolve(null);
    lines.set(id, p);
    p.then((a) => {
      if (!a) lines.delete(id); // couldn't read it this time: try again next time it's needed
    });
    return p;
  }
  const got = (id) => done.get(id) || null;
  function forget(id) {
    lines.delete(id);
    done.delete(id);
  }

  /* ----- live, from the microphone ----- */
  // an: an AnalyserNode on the recording's microphone (rec.mic.analyser(2048)). fn(points, last) after each new
  // reading, at most every 10 ms on the frame clock. Points are {t, m}, t in seconds from the start. Returns stop()
  function live(an, fn) {
    if (!an || !has()) return () => {};
    const n = an.fftSize,
      d = det(n),
      buf = new Float32Array(n),
      sr = (an.context && an.context.sampleRate) || 48000,
      pts = [],
      recent = [];
    let t0 = 0,
      next = 0,
      off = null;
    off = AUDIO.frame((ts) => {
      if (!t0) t0 = ts;
      if (ts < next) return;
      next = ts + SET.hop * 1000;
      an.getFloatTimeDomainData(buf);
      let s = 0;
      for (let i = 0; i < n; i += 4) s += buf[i] * buf[i];
      const loud = Math.sqrt(s / (n / 4)),
        t = (ts - t0) / 1000;
      let m = NaN;
      if (loud >= 0.01) {
        const [f, c] = d.findPitch(buf, sr);
        if (c >= SET.clarity && f > SET.fLo && f < SET.fHi) m = midi(f);
      }
      if (isNaN(m)) {
        recent.length = 0;
        return fn(pts, null);
      }
      // the octave check, against the last 150 ms of readings
      if (recent.length >= 3) {
        const r = median(recent);
        if (Math.abs(m - r - 12) < 0.8) m -= 12;
        else if (Math.abs(m - r + 12) < 0.8) m += 12;
      }
      recent.push(m);
      if (recent.length > Math.round(SET.octave / SET.hop)) recent.shift();
      const p = { t, m: recent.length >= 3 ? median(recent.slice(-3)) : m };
      pts.push(p);
      fn(pts, p);
    });
    return () => {
      if (off) off();
      off = null;
    };
  }

  /* ----- drawing ----- */
  // the note range for some lines: whole notes either side, at least an octave
  function range(list) {
    let lo = Infinity,
      hi = -Infinity;
    list.forEach((a) => {
      if (!a) return;
      if (a.lo != null) lo = Math.min(lo, a.lo);
      if (a.hi != null) hi = Math.max(hi, a.hi);
    });
    if (!isFinite(lo)) return { lo: 55, hi: 67 };
    lo = Math.floor(lo) - 1;
    hi = Math.ceil(hi) + 1;
    if (hi - lo < 12) {
      const c = (hi + lo) / 2;
      lo = Math.floor(c - 6);
      hi = lo + 12;
    }
    return { lo, hi };
  }
  // a path through a line from its first note: x(t), y(m); gaps of more than 30 ms lift the pen. Live points
  // ([{t, m}], from live()) are drawn as they are, lifting the pen over gaps of more than 60 ms
  function path(a, x, y, upTo) {
    let d = '',
      last = -9;
    if (Array.isArray(a)) {
      a.forEach((p) => {
        d += (p.t - last > 0.06 ? 'M' : 'L') + x(p.t).toFixed(1) + ' ' + y(p.m).toFixed(1);
        last = p.t;
      });
      return d;
    }
    if (!a || a.first < 0) return d;
    for (let i = a.first; i < a.n; i++) {
      const t = i * a.hop - a.firstT;
      if (upTo != null && t > upTo) break;
      const v = a.s[i];
      if (isNaN(v)) continue;
      d += (i - last > 3 ? 'M' : 'L') + x(t).toFixed(1) + ' ' + y(v).toFixed(1);
      last = i;
    }
    return d;
  }
  // lines overlaid on note rows: [{a, col, on}], o: {w, h, lo, hi, dur, marker: {t, label}, dots: [{t, m}], label}
  function svg(list, o) {
    o = o || {};
    const W = o.w || 340,
      H = o.h || 160,
      L = 34,
      R = 6,
      T = 8,
      B = 16,
      shown = list.filter((l) => l.a && l.on !== false),
      rg = o.lo != null ? { lo: o.lo, hi: o.hi } : range(shown.map((l) => l.a)),
      dur = o.dur || Math.max(1, ...shown.map((l) => (Array.isArray(l.a) ? 1 : l.a.dur - l.a.firstT))),
      x = (t) => L + (t / dur) * (W - L - R),
      y = (m) => T + ((rg.hi - m) / (rg.hi - rg.lo)) * (H - T - B);
    let g = '',
      lastY = -99;
    for (let m = Math.ceil(rg.lo); m <= rg.hi; m++) {
      const yy = y(m).toFixed(1),
        pc = ((m % 12) + 12) % 12;
      g += '<line class="pg" x1="' + L + '" x2="' + (W - R) + '" y1="' + yy + '" y2="' + yy + '"/>';
      if ([0, 4, 7, 9].includes(pc) && Math.abs(yy - lastY) >= 12) {
        g += '<text class="pn" x="' + (L - 5) + '" y="' + (+yy + 4).toFixed(1) + '" text-anchor="end">' + name(m) + '</text>';
        lastY = +yy;
      }
    }
    const step = dur > 30 ? 10 : dur > 12 ? 5 : dur > 6 ? 2 : 1;
    for (let t = 0; t <= dur + 0.001 && x(t) <= W - R - 10; t += step)
      g += '<text class="pt" x="' + x(t).toFixed(1) + '" y="' + (H - 3) + '" text-anchor="middle">' + t + 's</text>';
    shown.forEach((l) => {
      g +=
        '<path d="' +
        path(l.a, x, y, l.upTo) +
        '" fill="none" style="stroke:' +
        l.col +
        '" stroke-width="' +
        (l.w || 2.5) +
        '" stroke-linecap="round" stroke-linejoin="round"' +
        (l.key ? ' data-ln="' + l.key + '"' : '') +
        '/>';
    });
    // Q38 points to mark on the lines (Find your bridge's jumps): [{t, m}]
    (o.dots || []).forEach((d) => {
      g += '<circle class="pj" cx="' + x(d.t).toFixed(1) + '" cy="' + y(d.m).toFixed(1) + '" r="4.5"/>';
    });
    if (o.marker) {
      const xx = x(o.marker.t).toFixed(1);
      g +=
        '<line class="pm" x1="' + xx + '" x2="' + xx + '" y1="' + T + '" y2="' + (H - B) + '"/>' +
        '<circle class="pmd" cx="' + xx + '" cy="' + (T + 4) + '" r="4"/>';
    }
    return (
      '<svg class="pchart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' +
      esc(o.label || 'Pitch lines') + '">' + g + '</svg>'
    );
  }
  // a small line for a row: 64 × 24
  function spark(a, col) {
    if (!a || a.first < 0 || a.lo == null)
      return '<svg class="pspark wait" width="64" height="24" viewBox="0 0 64 24" aria-hidden="true"></svg>';
    const lo = a.lo,
      hi = a.hi,
      dur = Math.max(0.5, a.dur - a.firstT),
      x = (t) => 2 + (t / dur) * 60,
      y = (m) => 3 + ((hi + 0.5 - m) / (hi - lo + 1)) * 18;
    return (
      '<svg class="pspark" width="64" height="24" viewBox="0 0 64 24" aria-hidden="true"><path d="' +
      path(a, x, y) +
      '" fill="none" style="stroke:' +
      col +
      '" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    );
  }

  return { SET, name, midi, hz, has, line, shape, jumps, held, part, ofBlob, ofTake, got, forget, live, range, path, svg, spark };
})();
