/* Vocal Sessions · screens.js
   The main screens: Today, Progress, Exercises, Settings and the session steps.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Screens ===== */
function backupNudge() {
  if (!D.sessions.length && !D.songSessions.length) return '';
  const lb = D.lastBackup,
    age = lb ? Math.floor((Date.now() - new Date(lb)) / 864e5) : null;
  if (lb && age <= 14) return '';
  return (
    '<button class="nudge" data-rise data-a="exportPrep">' +
    ICON.save +
    '<span style="flex:1"><b>' +
    (lb ? 'Last backup ' + age + ' days ago.' : 'Not backed up yet.') +
    '</b> Back up now</span>' +
    ICON.fwd +
    '</button>'
  );
}
function scrToday() {
  const w = weekInfo(),
    p = Math.min(100, Math.round((w.mins / WEEK_TARGET) * 100)),
    mm = monthMins(),
    mp = Math.min(100, Math.round((mm / TARGET) * 100)),
    s = suggested();
  const today = startOfDay(new Date()).getTime();
  const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    .map((l, i) => {
      const d = new Date(w.ws);
      d.setDate(d.getDate() + i);
      const t = d.getTime();
      const cls = (w.days.has(t) ? 'done ' : '') + (t === today ? 'today' : '');
      return (
        '<span class="' +
        cls +
        '" aria-label="' +
        d.toLocaleDateString('en-GB', { weekday: 'long' }) +
        (w.days.has(t) ? ', practised' : '') +
        '">' +
        l +
        '</span>'
      );
    })
    .join('');
  const left = Math.max(0, WEEK_TARGET - Math.round(w.mins));
  let st, sub;
  if (w.mins >= WEEK_TARGET) {
    st = w.streak + '-week streak';
    sub = 'This week done';
  } else if (w.streak > 0) {
    st = w.streak + '-week streak';
    sub = left + ' min to go this week';
  } else {
    st = 'Start a new streak';
    sub = left + ' min this week starts one';
  }
  const dl = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
  const sw2 = songWeek(),
    songLive = isSong() && !!X.start;
  return (
    '<button class="dateline" data-rise data-a="openCal">' +
    dl +
    '</button><div class="titlerow" data-rise><h1><button class="tbtn" data-a="openCal">Today</button></h1><button class="calbtn" data-a="openCal" aria-label="Open practice calendar">' +
    ICON.down +
    '</button></div>' +
    backupNudge() +
    '<div class="dash"><div class="d-hero"><button class="arch" data-rise data-zk="goal" data-a="goalOpen" aria-label="This week, ' +
    Math.round(w.mins) +
    ' of your ' +
    WEEK_TARGET +
    '-minute goal. Open Progress"><svg viewBox="0 0 300 165" aria-hidden="true"><path d="M24 150 A126 126 0 0 1 276 150" fill="none" stroke="var(--fill)" stroke-width="16" stroke-linecap="round"/>' +
    (p > 0
      ? '<path d="M24 150 A126 126 0 0 1 276 150" pathLength="100" stroke-dasharray="' +
        p +
        ' 100" fill="none" stroke="' +
        (p >= 100 ? 'var(--good)' : 'var(--accent)') +
        '" stroke-width="16" stroke-linecap="round"/>'
      : '') +
    '</svg><div class="c" aria-hidden="true"><small>This week</small><b>' +
    Math.round(w.mins) +
    '</b><small>of your ' +
    WEEK_TARGET +
    '-minute goal</small></div></button>' +
    '<div data-rise style="margin-top:20px">' +
    (X && !songLive
      ? '<button class="cta ink" data-zk="start" data-a="resume">Resume session</button><button class="ghost" data-a="sheet" data-v="discard">Discard session</button>'
      : '<button class="cta ink" data-zk="start" data-a="start">Start session</button>') +
    '</div></div><div class="d-side"><div class="d-week">' +
    '<div class="week" data-rise role="list" aria-label="This week">' +
    days +
    '</div>' +
    '<div class="streak" data-rise>' +
    st +
    '<small>' +
    sub +
    '</small></div></div>' +
    '<div class="grp" data-rise style="margin-top:22px"><div class="row" style="display:block;padding:14px 16px"><div style="display:flex;justify-content:space-between;gap:8px"><span>This month</span><span class="mut">' +
    Math.round(mm) +
    ' of ' +
    TARGET +
    ' min</span></div><div class="track"><i class="' +
    (mp >= 100 ? 'full' : '') +
    '" style="width:' +
    mp +
    '%"></i></div></div>' +
    '<button class="row" data-zk="ex:' +
    s.id +
    '" data-a="openEx" data-k="' +
    s.id +
    '">' +
    tile(s) +
    '<span class="lbl">Suggested rotation<small>' +
    esc(s.name) +
    ' · ' +
    lastDone(s.id) +
    '</small></span>' +
    chev +
    '</button></div>' +
    '<div class="hdr" data-rise>Just singing</div><div class="grp tiled" data-rise><button class="row" data-zk="songStart" data-a="songStart">' +
    songTile +
    '<span class="lbl">Song practice<small>' +
    (songLive ? 'In progress · tap to carry on' : 'Record a take and note how it went') +
    '</small>' +
    (sw2.n && !songLive
      ? '<small class="co">This week · ' + sw2.n + ' session' + (sw2.n > 1 ? 's' : '') + ' · ' + hm(sw2.m) + '</small>'
      : '') +
    '</span>' +
    chev +
    '</button></div>' +
    '<p class="foot" data-rise>Song practice has its own stats. It never counts towards your weekly goal, streak or monthly minutes.</p>' +
    pinnedCard() +
    '</div></div>'
  );
}
function histSel(songs) {
  const arr = songs ? D.songSessions : D.sessions;
  let x = U.sel && arr.find((s) => s.id === U.sel);
  if (!x && arr.length) x = arr.slice().sort((a, b) => new Date(b.date) - new Date(a.date))[0];
  return x || null;
}
/* ===== Progress ===== */
const BLK = [
  ['f', 'Foundation', '--cF'],
  ['r', 'Rotation', '--cR'],
  ['a', 'Application', '--cA'],
];
const RANGES = ['D', 'W', 'M', '6M', 'Y', 'All'];
const pday = (d) => {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
};
const padd = (d, n, u) => {
  const x = new Date(d);
  if (u === 'd') x.setDate(x.getDate() + n);
  else if (u === 'm') x.setMonth(x.getMonth() + n);
  else x.setFullYear(x.getFullYear() + n);
  return x;
};
const pfmt = (d, o) => d.toLocaleDateString('en-GB', o);
function hmBig(m) {
  m = Math.round(m);
  const h = Math.floor(m / 60),
    x = m % 60;
  return h
    ? '<b>' + h + '</b><span>hr</span>' + (x ? '<b>' + x + '</b><span>min</span>' : '')
    : '<b>' + x + '</b><span>min</span>';
}
// the period a range covers and its bars; each step's minutes land in the bar for when it happened
function period() {
  const t = pday(new Date()),
    R = U.range || 'W',
    off = U.roff || 0;
  let a,
    b,
    bk = [],
    label;
  if (R === 'D') {
    a = padd(t, off, 'd');
    b = padd(a, 1, 'd');
    for (let h = 0; h < 24; h++) {
      const st = new Date(a);
      st.setHours(h);
      const e = new Date(st);
      e.setHours(h + 1);
      bk.push({
        s: st,
        e,
        x: h % 6 === 0 ? (h === 0 ? '12am' : h === 12 ? '12pm' : (h % 12) + (h < 12 ? 'am' : 'pm')) : '',
      });
    }
    label =
      off === 0 ? 'Today' : off === -1 ? 'Yesterday' : pfmt(a, { weekday: 'long', day: 'numeric', month: 'long' });
  } else if (R === 'W') {
    a = padd(weekStart(t), off * 7, 'd');
    b = padd(a, 7, 'd');
    for (let i = 0; i < 7; i++) {
      const st = padd(a, i, 'd');
      bk.push({ s: st, e: padd(st, 1, 'd'), x: 'MTWTFSS'[i] });
    }
    const e = padd(b, -1, 'd');
    label =
      pfmt(a, { day: 'numeric' }) +
      (a.getMonth() !== e.getMonth() ? ' ' + pfmt(a, { month: 'short' }) : '') +
      '–' +
      pfmt(e, { day: 'numeric', month: 'short', year: 'numeric' });
  } else if (R === 'M') {
    a = new Date(t.getFullYear(), t.getMonth() + off, 1);
    b = padd(a, 1, 'm');
    for (let st = new Date(a); st < b; st = padd(st, 1, 'd')) {
      const d = st.getDate();
      bk.push({ s: new Date(st), e: padd(st, 1, 'd'), x: [1, 8, 15, 22, 29].includes(d) ? String(d) : '' });
    }
    label = pfmt(a, { month: 'long', year: 'numeric' });
  } else if (R === '6M') {
    const end = padd(weekStart(t), 7 + off * 182, 'd');
    a = padd(end, -182, 'd');
    b = end;
    for (let i = 0; i < 26; i++) {
      const st = padd(a, i * 7, 'd'),
        pv = i ? padd(st, -7, 'd') : null;
      bk.push({
        s: st,
        e: padd(st, 7, 'd'),
        x: !pv || pv.getMonth() !== st.getMonth() ? pfmt(st, { month: 'narrow' }) : '',
      });
    }
    const e = padd(b, -1, 'd');
    label =
      pfmt(a, { month: 'short' }) +
      (a.getFullYear() !== e.getFullYear() ? ' ' + a.getFullYear() : '') +
      ' – ' +
      pfmt(e, { month: 'short', year: 'numeric' });
  } else if (R === 'Y') {
    a = new Date(t.getFullYear() + off, 0, 1);
    b = padd(a, 1, 'y');
    for (let m = 0; m < 12; m++) {
      const st = new Date(a.getFullYear(), m, 1);
      bk.push({ s: st, e: padd(st, 1, 'm'), x: pfmt(st, { month: 'narrow' }) });
    }
    label = String(a.getFullYear());
  } else {
    const ds = D.sessions.map((x) => new Date(x.date)).filter((d) => !isNaN(d));
    const first = ds.length ? new Date(Math.min(...ds)) : t;
    a = new Date(first.getFullYear(), first.getMonth(), 1);
    b = new Date(t.getFullYear(), t.getMonth() + 1, 1);
    for (let st = new Date(a); st < b; st = padd(st, 1, 'm'))
      bk.push({
        s: new Date(st),
        e: padd(st, 1, 'm'),
        x:
          +st === +a || st.getMonth() === 0
            ? pfmt(st, { month: 'short' }) + (st.getMonth() === 0 ? " '" + String(st.getFullYear()).slice(2) : '')
            : '',
      });
    label = 'Since ' + pfmt(a, { month: 'long', year: 'numeric' });
  }
  bk.forEach((k) => {
    k.f = k.r = k.a = k.mf = k.mr = k.ma = 0;
  });
  const sess = D.sessions.filter((x) => {
    const d = new Date(x.date);
    return d >= a && d < b;
  });
  sess.forEach((x) => {
    const sp = splitOf(x),
      st = +new Date(x.date);
    [
      ['f', sp.f, 0],
      ['r', sp.r, sp.f],
      ['a', sp.a, sp.f + sp.r],
    ].forEach(([key, m, o]) => {
      if (!(m > 0)) return;
      const at = new Date(st + o * 60000);
      const k = bk.find((k) => at >= k.s && at < k.e) || bk[bk.length - 1];
      k[(sp.mixed ? 'm' : '') + key] += m;
    });
  });
  bk.forEach((k) => {
    k.mx = k.mf + k.mr + k.ma;
    k.t = k.f + k.r + k.a + k.mx;
  });
  return { a, b, bk, label, sess };
}
function bucketName(k) {
  const R = U.range;
  if (R === 'D')
    return (
      pfmt(k.s, { hour: 'numeric', hour12: true }).replace(' ', '') +
      '–' +
      pfmt(k.e, { hour: 'numeric', hour12: true }).replace(' ', '')
    );
  if (R === 'W' || R === 'M') return pfmt(k.s, { weekday: 'short', day: 'numeric', month: 'short' });
  if (R === '6M') return 'Week of ' + pfmt(k.s, { day: 'numeric', month: 'short' });
  return pfmt(k.s, { month: 'long', year: 'numeric' });
}
const unitOf = () => ({ D: 'hour', W: 'day', M: 'day', '6M': 'week', Y: 'month', All: 'month' })[U.range];
// stacked bars: 2px gaps between steps, rounded tops, axis on the right like Health; blended bar = filled in at the end
function chartSVG(P) {
  const W = 340,
    H = 170,
    RA = 30,
    B = 22,
    T = 6,
    n = P.bk.length,
    max = Math.max(10, ...P.bk.map((k) => k.t));
  const step =
    max <= 30
      ? 10
      : max <= 60
        ? 20
        : max <= 120
          ? 30
          : max <= 300
            ? 60
            : max <= 600
              ? 120
              : max <= 1500
                ? 300
                : max <= 3000
                  ? 600
                  : 1200;
  const top = Math.ceil(max / step) * step;
  const cw = (W - RA) / n,
    bw = Math.max(2, Math.min(cw * 0.62, 22)),
    y = (v) => T + (H - T - B) * (1 - v / top);
  let g =
    '<defs><linearGradient id="mxg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="var(--cF)"/><stop offset=".5" stop-color="var(--cR)"/><stop offset="1" stop-color="var(--cA)"/></linearGradient></defs>';
  for (let v = 0; v <= top; v += step)
    g +=
      '<line class="gl' +
      (v ? ' d' : '') +
      '" x1="0" x2="' +
      (W - RA) +
      '" y1="' +
      y(v) +
      '" y2="' +
      y(v) +
      '"/><text x="' +
      (W - RA + 6) +
      '" y="' +
      (y(v) + 4) +
      '">' +
      (v >= 60 && v % 60 === 0 ? v / 60 + 'h' : v) +
      '</text>';
  P.bk.forEach((k, i) => {
    const x = i * cw + (cw - bw) / 2;
    let base = H - B;
    const segs = BLK.filter(([key]) => k[key] > 0).map(([key, , c]) => 'var(' + c + ')');
    if (k.mx > 0) segs.push('url(#mxg)');
    const vals = BLK.filter(([key]) => k[key] > 0)
      .map(([key]) => k[key])
      .concat(k.mx > 0 ? [k.mx] : []);
    let g2 = '';
    segs.forEach((col, j) => {
      const h = ((H - T - B) * vals[j]) / top,
        gap = j ? 2 : 0,
        yy = base - h,
        hh = Math.max(1, h - gap),
        r = Math.min(4, bw / 2, hh);
      g2 +=
        j === segs.length - 1
          ? '<path d="M' +
            x +
            ',' +
            (yy + hh) +
            ' V' +
            (yy + r) +
            ' Q' +
            x +
            ',' +
            yy +
            ' ' +
            (x + r) +
            ',' +
            yy +
            ' H' +
            (x + bw - r) +
            ' Q' +
            (x + bw) +
            ',' +
            yy +
            ' ' +
            (x + bw) +
            ',' +
            (yy + r) +
            ' V' +
            (yy + hh) +
            ' Z" fill="' +
            col +
            '"/>'
          : '<rect x="' + x + '" y="' + yy + '" width="' + bw + '" height="' + hh + '" fill="' + col + '"/>';
      base -= h;
    });
    g +=
      '<g class="bar' +
      (U.pick === i ? ' on' : '') +
      '" role="listitem" aria-label="' +
      (k.t ? hm(k.t) : 'Nothing') +
      ', ' +
      bucketName(k) +
      '">' +
      g2 +
      '<rect data-pick="' +
      i +
      '" x="' +
      i * cw +
      '" y="0" width="' +
      cw +
      '" height="' +
      H +
      '" fill="transparent" style="cursor:pointer"/></g>';
    if (k.x) g += '<text x="' + (i * cw + cw / 2) + '" y="' + (H - 6) + '" text-anchor="middle">' + k.x + '</text>';
  });
  return (
    '<svg viewBox="0 0 ' + W + ' ' + H + '" role="list" aria-label="Practice time by ' + unitOf() + '">' + g + '</svg>'
  );
}
function pcardHTML() {
  const P = period(),
    k = U.pick != null ? P.bk[U.pick] : null,
    sum = (key) => P.bk.reduce((a, x) => a + x[key], 0);
  const src = k
      ? { f: k.f + k.mf, r: k.r + k.mr, a: k.a + k.ma, mx: k.mx }
      : { f: sum('f') + sum('mf'), r: sum('r') + sum('mr'), a: sum('a') + sum('ma'), mx: sum('mx') },
    tot = src.f + src.r + src.a;
  const days = new Set(P.sess.map((x) => +pday(x.date))).size;
  const card =
    '<div class="kick">' +
    (k ? 'Practised' : 'Total practice') +
    '</div><div class="bignum" aria-live="polite">' +
    hmBig(tot) +
    '</div>' +
    '<div class="prange">' +
    (U.range === 'All'
      ? ''
      : '<button class="pnav" data-a="pnav" data-v="-1" aria-label="Earlier">' + ICON.back + '</button>') +
    '<span class="t">' +
    (k ? bucketName(k) : P.label) +
    '</span>' +
    (U.range === 'All'
      ? ''
      : '<button class="pnav" data-a="pnav" data-v="1" aria-label="Later"' +
        ((U.roff || 0) >= 0 ? ' disabled' : '') +
        '>' +
        ICON.fwd +
        '</button>') +
    '</div>' +
    '<div class="pchart' +
    (k ? ' picked' : '') +
    '" id="pchart">' +
    chartSVG(P) +
    '</div>' +
    '<div class="legend">' +
    BLK.map(([, nm, c]) => '<span><i class="dot" style="background:var(' + c + ')"></i>' + nm + '</span>').join('') +
    '<span><i class="dot mx"></i>Filled in at the end</span></div>';
  const brk =
    '<div class="hdr">Breakdown<span class="r">' +
    (k
      ? ''
      : P.sess.length +
        ' session' +
        (P.sess.length === 1 ? '' : 's') +
        (U.range !== 'D' ? ' · ' + days + ' day' + (days === 1 ? '' : 's') : '')) +
    '</span></div><div class="grp">' +
    BLK.map(([key, nm, c]) => {
      const v = src[key],
        p = tot ? Math.round((v / tot) * 100) : 0;
      return (
        '<div class="row"><i class="dot" style="background:var(' +
        c +
        ')"></i><span class="lbl">' +
        nm +
        '</span><span class="share" aria-hidden="true"><i style="width:' +
        p +
        '%;background:var(' +
        c +
        ')"></i></span><span class="pct">' +
        p +
        '%</span><span class="val">' +
        hm(v) +
        '</span></div>'
      );
    }).join('') +
    '</div>' +
    '<p class="foot">Tap or slide across the bars to see each ' +
    unitOf() +
    '.' +
    (src.mx >= 1
      ? ' ' + hm(src.mx) + ' was filled in at the end, so it’s split using the coach video’s length for each exercise.'
      : '') +
    '</p>';
  return { card, brk };
}
function sessRow(s) {
  const sp = splitOf(s),
    rots = Object.keys(s.rot || {}).map((id) => (exById(id) || { name: (s.rotNames || {})[id] || 'Exercise' }).name);
  return (
    '<button class="row" data-fk="rs:' +
    s.id +
    '" data-a="sheet" data-v="session" data-k="' +
    s.id +
    '"><span class="lbl">' +
    dayLabel(s.date) +
    '<small>' +
    esc(rots.length ? rots.join(', ') : 'Foundation only') +
    '</small><span class="mini" aria-hidden="true">' +
    (sp.mixed
      ? '<i class="mx" style="flex:1"></i>'
      : BLK.map(([key, , c]) =>
          sp[key] > 0 ? '<i style="flex:' + sp[key] + ';background:var(' + c + ')"></i>' : ''
        ).join('')) +
    '</span></span><span class="mut">' +
    hm(s.mins) +
    '</span>' +
    chev +
    '</button>'
  );
}
function songRow(s, a) {
  const n = (s.takes || []).length,
    how = howStr(s);
  return (
    '<button class="row" data-fk="rp:' +
    s.id +
    '" data-a="' +
    (a || 'sheet') +
    '" data-v="songSession" data-k="' +
    s.id +
    '">' +
    songTile +
    '<span class="lbl">' +
    esc(s.songName || 'Song practice') +
    '<small>' +
    dayLabel(s.date) +
    (n ? ' · ' + n + ' take' + (n > 1 ? 's' : '') : '') +
    (how ? ' · ' + esc(how) : '') +
    '</small></span><span class="mut">' +
    hm(s.mins) +
    '</span>' +
    chev +
    '</button>'
  );
}
function scrHistory() {
  const recent = D.sessions
    .slice()
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5);
  const songs = D.songSessions.slice().sort((a, b) => new Date(b.date) - new Date(a.date));
  const sw2 = songWeek(),
    now = new Date(),
    sm = songs.filter((x) => {
      const d = new Date(x.date);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    }).length;
  const { card, brk } = pcardHTML();
  const recentB =
    '<div class="hdr">Recent</div><div class="grp" data-gk="recent">' +
    (recent.length
      ? recent.map(sessRow).join('')
      : '<div class="empty">Your finished sessions will appear here.</div>') +
    '<button class="row acc" data-zk="all:sessions" data-a="openAll" data-v="sessions"><span class="lbl">Show all sessions</span>' +
    chev +
    '</button></div>';
  const timeB =
    '<div class="hdr">Practice time</div><div class="seg wide r6" role="tablist" aria-label="Range"><span class="knob" aria-hidden="true"></span>' +
    RANGES.map(
      (r) =>
        '<button role="tab" data-a="prange" data-v="' +
        r +
        '" class="' +
        (U.range === r ? 'on' : '') +
        '" aria-selected="' +
        (U.range === r) +
        '">' +
        r +
        '</button>'
    ).join('') +
    '</div>' +
    '<div class="pcard" id="pcard">' +
    card +
    '</div><div id="pbrk">' +
    brk +
    '</div>';
  const songB =
    '<div class="hdr">Song practice</div><div class="grp" data-gk="songrecent"><div class="stat3"><div><b>' +
    sw2.n +
    '</b>This week</div><div><b>' +
    hm(sw2.m) +
    '</b>Time</div><div><b>' +
    sm +
    '</b>This month</div></div>' +
    songs
      .slice(0, 3)
      .map((x) => songRow(x))
      .join('') +
    '<button class="row acc" data-zk="all:songs" data-a="openAll" data-v="songs"><span class="lbl">Show all song practice</span>' +
    chev +
    '</button></div>' +
    '<p class="foot">Kept apart from your focused practice time. You can also get here from Today, the calendar and each song in Exercises.</p>';
  return (
    '<h1>Progress</h1><div class="pgrid"><div class="p-rec">' +
    recentB +
    '</div><div class="p-time">' +
    timeB +
    '</div><div class="p-song">' +
    songB +
    '</div></div>'
  );
}
function histSel(songs) {
  const arr = songs ? D.songSessions : D.sessions;
  let x = U.sel && arr.find((s) => s.id === U.sel);
  if (!x && arr.length) x = arr.slice().sort((a, b) => new Date(b.date) - new Date(a.date))[0];
  return x || null;
}
// every "Show all" lands here: one list for sessions and song practice
function scrAll() {
  const songs = U.histTab === 'songs',
    sp = split(),
    sel = sp ? histSel(songs) : null,
    sid = sel ? sel.id : null;
  const segH =
    '<div class="seg wide" role="tablist" style="margin:2px 0 4px"><span class="knob" aria-hidden="true"></span><button role="tab" data-a="histTab" data-v="sessions" class="' +
    (songs ? '' : 'on') +
    '" aria-selected="' +
    !songs +
    '">Sessions</button><button role="tab" data-a="histTab" data-v="songs" class="' +
    (songs ? 'on' : '') +
    '" aria-selected="' +
    songs +
    '">Song practice</button></div>';
  const list = songs ? songHistory(sid) : sessionHistory(sid);
  if (!sp) return '<h1>All sessions</h1>' + segH + list;
  return (
    '<h1>All sessions</h1><div class="split"><div class="sl">' +
    segH +
    list +
    '</div><div class="pane">' +
    (sel
      ? songs
        ? songSessionBody(sel, 'pane')
        : sessionBody(sel, 'pane')
      : '<div class="grp" style="margin-top:6px"><div class="empty">Nothing here yet.</div></div>') +
    '</div></div>'
  );
}
function sessionHistory(selId) {
  const ss = D.sessions.slice().sort((a, b) => new Date(b.date) - new Date(a.date));
  if (!ss.length)
    return '<div class="grp" style="margin-top:12px"><div class="empty">Your finished sessions will appear here, with levels, notes and how they went.</div></div>';
  let h = '',
    cur = '';
  ss.forEach((s) => {
    const k = monthKey(new Date(s.date));
    if (k !== cur) {
      if (cur) h += '</div>';
      cur = k;
      const lab = new Date(s.date).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
      h +=
        '<div class="hdr">' +
        lab +
        ' · <span style="text-transform:none">' +
        hm(D.months[k] || 0) +
        '</span></div><div class="grp" data-gk="sm:' +
        k +
        '">';
    }
    const rots = Object.keys(s.rot || {}).map(
      (id) => (exById(id) || { name: (s.rotNames || {})[id] || 'Exercise' }).name
    );
    const how = howStr(s);
    h += sw(
      '<button class="row' +
        (s.id === selId ? ' sel' : '') +
        '" data-a="sheet" data-v="session" data-k="' +
        s.id +
        '"><span class="lbl">' +
        dayLabel(s.date) +
        (splitOf(s).mixed ? '<span class="ptag">Filled in at the end</span>' : '') +
        '<small>' +
        esc(rots.length ? rots.join(', ') : 'Foundation only') +
        '</small>' +
        (how ? '<small class="acc">' + esc(how) + '</small>' : '') +
        '</span><span class="mut">' +
        hm(s.mins) +
        '</span>' +
        chev +
        '</button>',
      'delSession',
      s.id
    );
  });
  return h + '</div><p class="foot">Swipe left on a session to delete it. Open one to edit it.</p>';
}
function songHistory(selId) {
  const ss = D.songSessions.slice().sort((a, b) => new Date(b.date) - new Date(a.date));
  if (!ss.length)
    return '<div class="grp" style="margin-top:12px"><div class="empty">Song practice you save appears here. It’s kept apart from your focused sessions.</div></div>';
  const sums = {};
  ss.forEach((s) => {
    const k = monthKey(new Date(s.date));
    sums[k] = (sums[k] || 0) + s.mins;
  });
  let h = '',
    cur = '';
  ss.forEach((s) => {
    const k = monthKey(new Date(s.date));
    if (k !== cur) {
      if (cur) h += '</div>';
      cur = k;
      const lab = new Date(s.date).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
      h +=
        '<div class="hdr">' +
        lab +
        ' · <span style="text-transform:none">' +
        hm(sums[k]) +
        '</span></div><div class="grp" data-gk="pm:' +
        k +
        '">';
    }
    const n = (s.takes || []).length,
      how = howStr(s);
    h += sw(
      '<button class="row' +
        (s.id === selId ? ' sel' : '') +
        '" data-a="sheet" data-v="songSession" data-k="' +
        s.id +
        '"><span class="lbl">' +
        dayLabel(s.date) +
        '<small>' +
        esc(s.songName || 'Song practice') +
        (n ? ' · ' + n + ' take' + (n > 1 ? 's' : '') : '') +
        '</small>' +
        (how ? '<small class="acc">' + esc(how) + '</small>' : '') +
        '</span><span class="mut">' +
        hm(s.mins) +
        '</span>' +
        chev +
        '</button>',
      'delSongSess',
      s.id
    );
  });
  return h + '</div><p class="foot">Swipe left to delete. Song practice never counts towards your goal or streak.</p>';
}
function scrExercises() {
  const sp = split();
  if (sp && !exById(U.exId)) U.exId = FOUND[0].id;
  const row = (e) =>
    '<button class="row' +
    (sp && e.id === U.exId ? ' sel' : '') +
    '" data-zk="ex:' +
    e.id +
    '" data-a="openEx" data-k="' +
    e.id +
    '">' +
    tile(e) +
    '<span class="lbl">' +
    esc(e.name) +
    '<small>' +
    esc(e.focus) +
    ' · ' +
    lastDone(e.id) +
    '</small></span>' +
    chev +
    '</button>';
  const list =
    '<div class="grp" style="margin-top:8px"><a class="row acc" href="' +
    VIDEO +
    '" target="_blank" rel="noopener"><span class="lbl">Coach video<small>Opens in YouTube</small></span>' +
    ICON.video +
    '</a></div>' +
    '<div class="hdr">Foundation</div><div class="grp tiled">' +
    FOUND.map(row).join('') +
    '</div>' +
    '<div class="hdr">Rotation</div><div class="grp tiled">' +
    ROT.map(row).join('') +
    '</div>' +
    '<div class="hdr">Your exercises</div><div class="grp tiled" data-gk="custom">' +
    D.custom.map((e) => sw(row(e), 'delEx', e.id)).join('') +
    '<button class="row acc" data-a="sheet" data-v="addEx"><span class="lbl">Add exercise</span>' +
    ICON.plus +
    '</button></div>' +
    (D.custom.length ? '<p class="foot">Swipe left on your own exercises to delete them.</p>' : '');
  return (
    '<h1>Exercises</h1>' +
    (sp ? '<div class="split"><div class="sl">' + list + '</div><div class="pane">' + scrEx() + '</div></div>' : list)
  );
}
function exHistory(id) {
  return D.sessions
    .filter((s) => (s.f && s.f[id]) || (s.rot && s.rot[id]))
    .map((s) => ({ s, lv: (s.f && s.f[id]) || s.rot[id] }));
}
function scrEx() {
  const e = exById(U.exId);
  if (!e) return '<div class="grp"><div class="empty">This exercise was removed.</div></div>';
  const d = DESC[e.id];
  const isF = FOUND.some((x) => x.id === e.id);
  let h =
    tile(e, true) +
    '<h1>' +
    esc(e.name) +
    '</h1><div class="ex-h"><span class="badge">' +
    (isF ? 'Foundation' : 'Rotation') +
    '</span><span class="badge">' +
    esc(e.focus) +
    '</span>' +
    (d ? '<span class="badge">Exercise ' + d.n + '</span>' : '') +
    '</div>' +
    '<div class="seg wide" role="tablist" style="margin-bottom:6px"><span class="knob" aria-hidden="true"></span><button role="tab" data-a="exTab" data-v="summary" class="' +
    (U.exTab === 'summary' ? 'on' : '') +
    '" aria-selected="' +
    (U.exTab === 'summary') +
    '">Summary</button><button role="tab" data-a="exTab" data-v="history" class="' +
    (U.exTab === 'history' ? 'on' : '') +
    '" aria-selected="' +
    (U.exTab === 'history') +
    '">History</button></div>';
  if (U.exTab === 'summary') {
    h +=
      '<div class="hdr">Last done</div><div class="grp"><div class="row"><span class="lbl">' +
      lastDone(e.id)
        .replace(/^last done /, '')
        .replace(/^Not done yet$/, 'Not done yet') +
      '</span></div></div>';
    if (d) {
      h +=
        '<div class="hdr">What it is</div><div class="grp"><div class="prose">' +
        d.what +
        '</div></div>' +
        '<div class="hdr">Why it helps</div><div class="grp"><div class="prose">' +
        d.why +
        '</div></div>' +
        '<div class="hdr">In a song</div><div class="grp"><div class="prose"><ul>' +
        d.song.map((x) => '<li><b>' + x[0] + '.</b> ' + x[1] + '</li>').join('') +
        '</ul></div></div>';
    } else {
      h +=
        '<div class="hdr">What it is</div><div class="grp"><div class="prose' +
        (e.what ? '' : ' mut') +
        '">' +
        (e.what ? esc(e.what) : 'No description yet.') +
        '</div><button class="row acc" data-a="sheet" data-v="editWhat" data-k="' +
        e.id +
        '"><span class="lbl">' +
        (e.what ? 'Edit description' : 'Add a description') +
        '</span></button></div>';
    }
  } else {
    const hist = exHistory(e.id);
    if (!hist.length) {
      h +=
        '<div class="grp" style="margin-top:14px"><div class="empty">No sessions with this exercise yet.' +
        ((D.ex[e.id] || {}).n
          ? ' Practice from before ' + UPDATE_DAY + ' wasn’t saved session by session, so it can’t be shown here.'
          : '') +
        '</div></div>';
    } else {
      const pts = hist.slice(-20);
      const W = 320,
        H = 150,
        L = 34,
        R = 12,
        T = 14,
        B = 26;
      const n = pts.length;
      const xs = (i) => (n === 1 ? L + (W - L - R) / 2 : L + (i * (W - L - R)) / (n - 1));
      const ys = (v) => T + ((3 - v) * (H - T - B)) / 2;
      let svg =
        '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Level over the last ' + n + ' sessions">';
      [1, 2, 3].forEach((v) => {
        svg +=
          '<line x1="' +
          L +
          '" x2="' +
          (W - R) +
          '" y1="' +
          ys(v) +
          '" y2="' +
          ys(v) +
          '" stroke="var(--sep)"/><text x="' +
          (L - 10) +
          '" y="' +
          (ys(v) + 4) +
          '" text-anchor="end" font-size="12" fill="var(--fg2)">L' +
          v +
          '</text>';
      });
      if (n > 1)
        svg +=
          '<polyline points="' +
          pts.map((p, i) => xs(i) + ',' + ys(p.lv)).join(' ') +
          '" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round"/>';
      pts.forEach((p, i) => {
        svg +=
          '<circle cx="' + xs(i) + '" cy="' + ys(p.lv) + '" r="' + (i === n - 1 ? 5.5 : 4) + '" fill="var(--accent)"/>';
      });
      svg +=
        '<text x="' +
        xs(0) +
        '" y="' +
        (H - 6) +
        '" text-anchor="' +
        (n === 1 ? 'middle' : 'start') +
        '" font-size="12" fill="var(--fg2)">' +
        shortDate(pts[0].s.date) +
        '</text>';
      if (n > 1)
        svg +=
          '<text x="' +
          xs(n - 1) +
          '" y="' +
          (H - 6) +
          '" text-anchor="end" font-size="12" fill="var(--fg2)">' +
          shortDate(pts[n - 1].s.date) +
          '</text>';
      svg += '</svg>';
      const lastLv = pts[n - 1].lv;
      h +=
        '<div class="hdr">Level · <span style="text-transform:none">latest L' +
        lastLv +
        '</span></div><div class="grp"><div class="chart">' +
        svg +
        '</div></div>' +
        '<div class="hdr">Sessions</div><div class="grp">' +
        hist
          .slice()
          .reverse()
          .map(
            (p) =>
              '<button class="row" data-a="sheet" data-v="session" data-k="' +
              p.s.id +
              '"><span class="lbl">' +
              dayLabel(p.s.date) +
              (noteStr((p.s.xn || {})[e.id]) ? '<small class="acc">' + esc(noteStr(p.s.xn[e.id])) + '</small>' : '') +
              '</span><span class="mut">Level ' +
              p.lv +
              '</span>' +
              chev +
              '</button>'
          )
          .join('') +
        '</div>';
    }
  }
  return h;
}
function scrSettings() {
  const lb = D.lastBackup;
  const age = lb ? (Date.now() - new Date(lb)) / 864e5 : Infinity;
  const lbText = lb ? 'Last backed up ' + shortDate(lb) + ' at ' + timeOf(lb) : 'Never backed up';
  const size = TAKES.reduce((a, t) => a + t.size, 0);
  return (
    '<h1>Settings</h1>' +
    '<div class="hdr">Backup</div><div class="grp">' +
    '<button class="row" data-a="exportPrep"><span class="lbl acc">Export backup</span>' +
    ICON.share +
    '</button>' +
    '<button class="row" data-a="importPick"><span class="lbl acc">Import backup</span>' +
    chev +
    '</button>' +
    '<button class="row" data-a="checkPick"><span class="lbl acc">Check a backup</span>' +
    chev +
    '</button>' +
    (UNDO
      ? '<button class="row" data-a="sheet" data-v="undoRestore"><span class="lbl acc">Undo last restore<small>Restored ' +
        shortDate(UNDO.at) +
        ' at ' +
        timeOf(UNDO.at) +
        '</small></span>' +
        chev +
        '</button>'
      : '') +
    '</div>' +
    '<p class="foot' +
    (age > 14 ? ' warn' : '') +
    '">' +
    lbText +
    (age > 14 && lb ? '. It’s been over two weeks.' : '') +
    '</p>' +
    '<p class="foot">A backup holds everything: sessions, minutes, exercises, songs with their lyrics and marks, and recordings (you can exclude those when you export). Keep them in iCloud Drive › Vocal Sessions › Backups, and import one after re-adding the app or switching phones.</p>' +
    '<div class="hdr">Backup files</div><div class="grp">' +
    '<button class="row" data-a="sheet" data-v="bkLog"><span class="lbl">Backup history</span><span class="mut">' +
    loadLog().length +
    '</span>' +
    chev +
    '</button>' +
    '<button class="row" data-a="sheet" data-v="bkGuide"><span class="lbl">Where backups go</span>' +
    chev +
    '</button>' +
    '<button class="row" data-a="saveReadme"><span class="lbl acc">Save a read-me file</span>' +
    ICON.share +
    '</button></div>' +
    '<div class="hdr">Recall</div><div class="grp"><div class="row"><span class="lbl">Peek length</span>' +
    '<div class="seg pkseg" role="group" aria-label="Peek length"><span class="knob" aria-hidden="true"></span>' +
    PEEKS.map(
      (n) =>
        '<button data-a="peekLen" data-v="' +
        n +
        '" class="' +
        (peekSecs() === n ? 'on' : '') +
        '" aria-pressed="' +
        (peekSecs() === n) +
        '" aria-label="' +
        n +
        (n === 1 ? ' second' : ' seconds') +
        '">' +
        n +
        ' s</button>'
    ).join('') +
    '</div></div></div>' +
    '<p class="foot">How long a hidden line shows when you tap it in Recall. Hold a line to keep it showing until you let go.</p>' +
    '<div class="hdr">Storage</div><div class="grp"><button class="row" data-a="sheet" data-v="storage"><span class="lbl">Recordings</span><span class="mut">' +
    TAKES.length +
    ' · ' +
    (size / 1048576).toFixed(1) +
    ' MB</span>' +
    chev +
    '</button>' +
    '<button class="row" data-a="sheet" data-v="persist"><span class="lbl">Storage protection<small>' +
    (PERSIST === true
      ? 'iOS won’t clear the app’s data to free up space'
      : PERSIST === false
        ? 'iOS could clear it if your ' + deviceName() + ' runs very low on space'
        : PERSIST === 'na'
          ? 'This browser doesn’t offer it. Keep backing up.'
          : 'Checking…') +
    '</small></span><span class="mut">' +
    persistVal() +
    '</span>' +
    chev +
    '</button></div>' +
    '<div class="hdr">Reset</div><div class="grp">' +
    '<button class="row" data-a="sheet" data-v="resetMonth"><span class="lbl dng">Reset this month’s minutes</span></button>' +
    '<button class="row" data-a="sheet" data-v="resetAll"><span class="lbl dng">Reset all data</span></button></div>' +
    '<div class="hdr">About</div><div class="grp"><button class="row" data-zk="log" data-a="openLog"><span class="lbl">Changelog<small>What’s new in ' +
    APP_VERSION +
    ', and every version before it</small></span>' +
    chev +
    '</button><a class="row" href="' +
    REPO +
    '" target="_blank" rel="noopener"><span class="lbl acc">View on GitHub<small>imperialfox/Vocal-Sessions</small></span>' +
    ICON.gh +
    '</a></div>' +
    '<button class="foot" data-a="openLog" style="display:block;width:calc(100% - 32px);text-align:center;margin-top:18px">Vocal Sessions ' +
    APP_VERSION +
    ' · ' +
    RELEASE_DATE +
    '</button>'
  );
}
// one exercise with its level picker and notes pencil (used in Foundation, Rotation and Edit)
function exBlock(e, a, v, skip, T, src) {
  const n = noteStr((T.xn || {})[e.id]);
  return (
    '<div><div class="row">' +
    tile(e) +
    '<span class="lbl">' +
    esc(e.name) +
    '</span><button class="nbtn' +
    (n ? ' has' : '') +
    '" data-a="exNote" data-k="' +
    e.id +
    '" data-src="' +
    (src || '') +
    '" aria-label="Notes for ' +
    esc(e.name) +
    '">' +
    ICON.pen +
    '</button></div>' +
    '<div class="sub" style="justify-content:flex-end">' +
    (skip ? segF(a, e.id, v) : seg(a, e.id, v)) +
    '</div>' +
    (n ? '<div class="notetxt">' + esc(n) + '</div>' : '') +
    '</div>'
  );
}
function scrFound() {
  return (
    '<h1>Foundation</h1><p class="note">Set how many levels you got through, or Skip. Tap the pencil for quick notes.</p><div class="grp tiled">' +
    FOUND.map((e) => exBlock(e, 'flv', X.f[e.id], true, X)).join('') +
    '</div>' +
    '<p class="foot">Tap the time at the top to see the full clock or pause it. With YouTube Premium, the coach video keeps playing in picture-in-picture while you use this app.</p>'
  );
}
function rotRow(e, sug) {
  const on = e.id in X.rot,
    n = noteStr(X.xn[e.id]);
  return (
    '<button class="row" data-a="tog" data-k="' +
    e.id +
    '" aria-pressed="' +
    on +
    '">' +
    tile(e) +
    '<span class="lbl">' +
    esc(e.name) +
    '<small>' +
    (sug ? 'Longest since last done · ' : '') +
    lastDone(e.id) +
    '</small></span><span class="' +
    (on ? 'acc' : 'mut') +
    '" aria-hidden="true">' +
    (on ? ICON.circleOn : ICON.circle) +
    '</span></button>' +
    (on
      ? '<div class="sub" style="padding-left:62px"><span class="tag" style="flex:1">' +
        esc(e.focus) +
        '</span><button class="nbtn' +
        (n ? ' has' : '') +
        '" data-a="exNote" data-k="' +
        e.id +
        '" aria-label="Notes for ' +
        esc(e.name) +
        '">' +
        ICON.pen +
        '</button>' +
        seg('rlv', e.id, X.rot[e.id]) +
        '</div>' +
        (n ? '<div class="notetxt">' + esc(n) + '</div>' : '')
      : '')
  );
}
function scrRot() {
  const s = suggested();
  const rest = allRot().filter((e) => e.id !== s.id);
  return (
    '<h1>Rotation</h1><p class="note">Pick as many as you like. Each one gets its own level.</p><div class="hdr">Suggested</div><div class="grp tiled">' +
    rotRow(s, true) +
    '</div>' +
    '<div class="hdr">More exercises</div><div class="grp tiled">' +
    rest.map((e) => rotRow(e)).join('') +
    '<button class="row acc" data-a="sheet" data-v="addEx"><span class="lbl">Add exercise</span>' +
    ICON.plus +
    '</button></div>'
  );
}
function songPicker() {
  const sid = X.song;
  return (
    '<div class="hdr">Song</div><div class="grp">' +
    D.songs
      .map(
        (s) =>
          '<button class="row" data-a="song" data-k="' +
          s.id +
          '"><span class="lbl">' +
          esc(s.name) +
          '</span>' +
          (sid === s.id ? '<span class="acc">' + ICON.check + '</span>' : '') +
          '</button>'
      )
      .join('') +
    '<button class="row acc" data-a="sheet" data-v="addSong"><span class="lbl">Add song</span>' +
    ICON.plus +
    '</button></div>'
  );
}
function takeRows(sid) {
  const tk = TAKES.filter((t) => t.songId === sid),
    sg = songById(sid);
  // takes recorded from a section say which one
  const where = (t) => {
    const i = t.o && hasLyrics(sg) ? occIdx(sg, t.o) : -1;
    return i < 0 ? '' : esc(occLabel(sg, i)) + ' · ';
  };
  return (
    '<div class="hdr">Takes</div><div class="grp"><button class="row recbtn' +
    (rec ? ' on' : '') +
    '" data-a="rec"><span class="dot" aria-hidden="true"></span><span id="recLbl">' +
    (rec ? 'Stop · ' + mmss(rec.t) + ' of ' + mmss(MAX_TAKE) : 'Record a take') +
    '</span></button>' +
    tk
      .map((t) => {
        const n = noteStr(t.note);
        return sw(
          '<div class="row"><button class="ibtn acc" data-a="playTake" data-k="' +
            t.id +
            '" aria-label="Play take">' +
            (takePlaying(t.id) ? ICON.pause : ICON.play) +
            '</button><button class="lbl tk" data-a="takeNote" data-k="' +
            t.id +
            '" aria-label="Notes for this take">' +
            where(t) +
            shortDate(t.created) +
            ' · ' +
            mmss(t.len) +
            '<small class="' +
            (n ? 'acc' : '') +
            '">' +
            (n ? esc(n) : 'Add a note') +
            '</small></button><button class="ibtn star' +
            (t.star ? ' on' : '') +
            '" data-a="star" data-k="' +
            t.id +
            '" aria-label="' +
            (t.star ? 'Unstar' : 'Star') +
            ' take" style="' +
            (t.star ? '' : 'color:var(--fg3)') +
            '">' +
            ICON.star +
            '</button><button class="ibtn acc" data-a="shareTake" data-k="' +
            t.id +
            '" aria-label="Save or share take">' +
            ICON.share +
            '</button><button class="ibtn dng" data-a="sheet" data-v="delTake" data-k="' +
            t.id +
            '" aria-label="Delete take">' +
            ICON.trash +
            '</button></div>',
          'delTake',
          t.id
        );
      })
      .join('') +
    '</div><p class="foot">Tap a take to add notes. Keeps the last ' +
    KEEP_TAKES +
    ' takes per song, plus any you star. If you leave the app while recording, the take stops and is saved.</p>'
  );
}
function scrApp() {
  let h =
    '<h1>Application</h1><p class="note">Sing a real song or section and record a take to listen back.</p>' +
    songPicker();
  if (X.song) h += takeRows(X.song);
  h +=
    '<div class="hdr">Rate the song</div><div class="grp">' +
    ['Pitch', 'Tone', 'Ease']
      .map((k) => '<div class="row"><span class="lbl">' + k + '</span>' + seg('rate', k, X.rate[k]) + '</div>')
      .join('') +
    '</div>';
  return h;
}
function scrSong() {
  let h =
    '<h1>Song practice</h1><p class="note">Just singing. Record takes and note how they went. This never counts towards your focused goal or streak.</p>' +
    songPicker();
  if (X.song) h += takeRows(X.song);
  return (
    h +
    (X.start
      ? '<button class="ghost" data-a="sheet" data-v="discard" style="color:var(--danger);margin-top:14px">Discard song practice</button>'
      : '<p class="foot">The clock starts when you record your first take. Choosing a song isn’t counted.</p>')
  );
}
