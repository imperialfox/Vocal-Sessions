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
// Today's week arch (also drawn by the Session saved screen, Q21, so the two line up exactly)
const ARC_D = 'M24 150 A126 126 0 0 1 276 150';
// the week's seven circles: practised days filled, today outlined. now (Q21, the Session saved screen) is the day just
// practised, whose circle turns green
function weekSpans(w, now) {
  const today = startOfDay(new Date()).getTime();
  return ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    .map((l, i) => {
      const d = new Date(w.ws);
      d.setDate(d.getDate() + i);
      const t = d.getTime();
      const cls = (w.days.has(t) ? 'done ' : '') + (t === today ? 'today' : '') + (t === now ? ' svd-now' : '');
      return (
        '<span class="' +
        cls +
        '" aria-label="' +
        fmtDate(d, { weekday: 'long' }) +
        (w.days.has(t) ? ', practised' : '') +
        '">' +
        l +
        '</span>'
      );
    })
    .join('');
}
function scrToday() {
  const w = weekInfo(),
    p = Math.min(100, Math.round((w.mins / WEEK_TARGET) * 100)),
    mm = monthMins(),
    mp = Math.min(100, Math.round((mm / TARGET) * 100)),
    s = suggested();
  const days = weekSpans(w);
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
  const dl = fmtDate(new Date(), { weekday: 'long', day: 'numeric', month: 'long' });
  const sw2 = songWeek(),
    songLive = isSong() && !!X.start;
  return (
    // Q45 the parts kit's large title (part 3): the date on its own line above "Today", which sits 17 pt lower than
    // the other tabs' titles (replaces 3.17's shared row); the chevron grey, 6 pt from the word, opening the calendar
    SET.wash() + // 3.23 (Q08): the soft gradient behind the date and title (Settings › Appearance)
    '<div class="titlerow"><button class="dateline pk-date-line" data-rise data-a="openCal">' +
    dl +
    '</button><h1 class="pk-large-title" data-rise><button class="tbtn" data-a="openCal">Today</button><button class="calbtn" data-a="openCal" aria-label="Open practice calendar">' +
    ICON.down +
    '</button></h1></div>' +
    backupNudge() +
    '<div class="dash"><div class="d-hero"><button class="arch" data-rise data-zk="goal" data-a="goalOpen" aria-label="This week, ' +
    Math.round(w.mins) +
    ' of your ' +
    WEEK_TARGET +
    '-minute goal. Open Progress"><svg viewBox="0 0 300 165" aria-hidden="true"><path d="' +
    ARC_D +
    '" fill="none" stroke="var(--fill)" stroke-width="16" stroke-linecap="round"/>' +
    (p > 0
      ? '<path d="' +
        ARC_D +
        '" pathLength="100" stroke-dasharray="' +
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
    '<div class="hdr" data-rise>Just singing</div><div class="grp tiled" data-rise><button class="row" data-a="songStart">' +
    songTile +
    '<span class="lbl">Song practice<small>' +
    (songLive ? 'In progress · tap to carry on' : 'Pick a song and record a take') +
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
const pfmt = (d, o) => fmtDate(d, o);
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
    '<div class="hdr">Practice time</div><div class="seg pk-seg wide r6" role="tablist" aria-label="Range"><span class="pk-seg-ind" aria-hidden="true"></span>' +
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
    '<div class="seg pk-seg wide" role="tablist" style="margin:2px 0 4px"><span class="pk-seg-ind" aria-hidden="true"></span><button role="tab" data-a="histTab" data-v="sessions" class="' +
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
      const lab = fmtDate(new Date(s.date), { month: 'long', year: 'numeric' });
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
      const lab = fmtDate(new Date(s.date), { month: 'long', year: 'numeric' });
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
    '" data-push data-a="openEx" data-k="' +
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
    COACH.exercisesRow() + // 3.16: the coach video on this device (coach.js)
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
  const redesigned = !!(d && EX_PAGE[e.id]);
  let h =
    (redesigned
      ? '<div class="exti">' +
        tile(e, true) +
        '<div><h1>' +
        esc(e.name) +
        '</h1><div class="exsub">' +
        esc(cap1(lastDone(e.id))) +
        '</div></div></div>'
      : tile(e, true) + '<h1>' + esc(e.name) + '</h1>') +
    '<div class="ex-h"><span class="badge">' +
    (isF ? 'Foundation' : 'Rotation') +
    '</span><span class="badge">' +
    esc(e.focus) +
    '</span>' +
    (d ? '<span class="badge">Exercise ' + d.n + '</span>' : '') +
    '</div>' +
    '<div class="seg pk-seg wide" role="tablist" style="margin-bottom:6px"><span class="pk-seg-ind" aria-hidden="true"></span><button role="tab" data-a="exTab" data-v="summary" class="' +
    (U.exTab === 'summary' ? 'on' : '') +
    '" aria-selected="' +
    (U.exTab === 'summary') +
    '">Summary</button><button role="tab" data-a="exTab" data-v="history" class="' +
    (U.exTab === 'history' ? 'on' : '') +
    '" aria-selected="' +
    (U.exTab === 'history') +
    '">History</button></div>';
  const P = d && EX_PAGE[e.id];
  if (U.exTab === 'summary' && P) {
    h += exSummary(e, d, P); // Q32: the redesigned page, with the pattern player
  } else if (U.exTab === 'summary') {
    PAT.use(null);
    h +=
      '<div class="hdr exh">Last done</div><div class="grp"><div class="row"><span class="lbl">' +
      lastDone(e.id)
        .replace(/^last done /, '')
        .replace(/^Not done yet$/, 'Not done yet') +
      '</span></div></div>';
    if (d) {
      h +=
        '<div class="hdr exh">About ' +
        esc(e.name.charAt(0).toLowerCase() + e.name.slice(1)) +
        '</div><div class="grp"><div class="prose">' +
        d.what +
        '</div></div>' +
        '<div class="hdr exh">Why it helps</div><div class="grp"><div class="prose">' +
        d.why +
        '</div></div>' +
        COACH.exerciseRow(e.id) +
        '<div class="hdr exh">In a song</div><div class="grp"><div class="prose"><ul>' +
        d.song.map((x) => '<li><b>' + x[0] + '.</b> ' + x[1] + '</li>').join('') +
        '</ul></div></div>';
    } else {
      h +=
        '<div class="hdr exh">About ' +
        esc(e.name) +
        '</div><div class="grp"><div class="prose' +
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
/* ===== The exercise page (Q32) =====
   The page explains the exercise and plays it: the drawing card and the dock come from the shared pattern player
   (patterns.js), which this page only tells its route (the coach's starting notes for the level shown), the default
   pattern and what you sing. Everything else is the page's own: the facts, the fix tip, How to do it, Where you feel
   it, the level dots, Why it helps, the coach video row and In a song. */
const cap1 = (s) => String(s).charAt(0).toUpperCase() + String(s).slice(1);
// the level the page shows: the last one logged, until a level dot is tapped
function exLevel(id) {
  if (U.exLv && U.exLv.id === id) return U.exLv.lv;
  return exLogged(id) || 1;
}
function exLogged(id) {
  const h = exHistory(id);
  return h.length ? Math.min(3, Math.max(1, +h[h.length - 1].lv || 1)) : 0;
}
// a colour dark enough to read on white (4.5:1), for the facts' icons in light mode; dark mode uses the colour as it is
function exInk(col) {
  const hex =
    { 'var(--sys-blue)': '007aff', 'var(--coral)': 'ff3b30' }[col] ||
    (/^#([0-9a-f]{6})$/i.exec(col) || [])[1] ||
    '8e8e93';
  const rgb = (h) => h.match(/\w\w/g).map((x) => parseInt(x, 16));
  const lum = (h) => {
    const v = rgb(h).map((x) => ((x /= 255), x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)));
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  };
  const mix = (a, p) =>
    rgb(a)
      .map((v) =>
        Math.round(v * (1 - p))
          .toString(16)
          .padStart(2, '0')
      )
      .join('');
  let p = 0.3,
    k = mix(hex, p);
  while (1.05 / (lum(k) + 0.05) < 4.5 && p < 0.8) k = mix(hex, (p += 0.02));
  return '#' + k;
}
// Q44 the glow on the spot pulses three times when the page opens, then rests. The page is redrawn on every tap, so
// each new glow carries on from where the last one was (a negative delay), and the pattern player starting stops it
// where it is (exGlowStop(), from PAT's play)
const EXGLOW = { key: '', at: 0, stop: 0 };
function exGlowStyle(key) {
  // a fresh visit: no glow on the page being replaced, or a different exercise's
  if (key !== EXGLOW.key || !document.querySelector('#app .exglow')) {
    EXGLOW.key = key;
    EXGLOW.at = performance.now();
    EXGLOW.stop = 0;
  }
  const t = ((EXGLOW.stop || performance.now()) - EXGLOW.at) / 1000;
  return 'animation-delay:-' + t.toFixed(3) + 's' + (EXGLOW.stop ? ';animation-play-state:paused' : '');
}
function exGlowStop() {
  if (EXGLOW.stop || !EXGLOW.at) return;
  EXGLOW.stop = performance.now();
  document.querySelectorAll('#app .exglow').forEach((g) => (g.style.animationPlayState = 'paused'));
}
// Where you feel it: a head in profile with a glow on the spot
function exHead(spot, col) {
  const P = { mask: [96, 66], palate: [90, 86], nose: [108, 70], lips: [106, 98], head: [66, 52], centre: [70, 64] }[
    spot
  ] || [90, 86];
  return (
    '<svg class="exhead" viewBox="0 0 150 150" aria-hidden="true"><path d="M66 16 C38 16 22 38 22 66 C22 88 30 102 42 110 L42 140 L88 140 L90 120 C100 120 108 117 110 108 L112 98 L119 94 L112 88 L114 82 L124 74 L112 64 C112 36 94 16 66 16 Z" class="exhd"/>' +
    '<circle class="exglow" style="' +
    exGlowStyle([U.view, U.exId, spot, col].join('|')) +
    '" cx="' +
    P[0] +
    '" cy="' +
    P[1] +
    '" r="18" fill="' +
    col +
    '"/><circle cx="' +
    P[0] +
    '" cy="' +
    P[1] +
    '" r="5" fill="' +
    col +
    '"/></svg>'
  );
}
// Vocal slides has no "Hear it": a still picture of short, medium and full-range slides instead of the player
function exSlides(col) {
  const arc = (d) => '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="4" stroke-linecap="round"/>';
  return (
    '<div class="pcard"><svg class="pdraw" viewBox="0 0 300 118" role="img" aria-label="Short, medium and full-range slides"><line x1="0" y1="96" x2="300" y2="96" class="pbase"/>' +
    arc('M12 96 C30 96 38 66 52 66 C66 66 74 96 92 96') +
    arc('M104 96 C124 96 132 42 147 42 C162 42 170 96 190 96') +
    arc('M202 96 C222 96 230 14 246 14 C262 14 270 96 290 96') +
    [
      ['Short', 52],
      ['Medium', 147],
      ['Full range', 246],
    ]
      .map(([l, x]) => '<text x="' + x + '" y="114" text-anchor="middle" class="plab">' + l + '</text>')
      .join('') +
    '</svg><div class="pstat"><b>Follow the coach</b><span>No “Hear it” for slides</span></div></div>'
  );
}
function exSummary(e, d, P) {
  const lv = exLevel(e.id),
    L = P.L[lv - 1],
    col = FOCUS_COL[e.focus] || 'var(--sys-gray)';
  const route = L[1] ? PAT.notes(L[1], L[2] || 0) : [];
  PAT.use(
    route.length
      ? { key: e.id, name: e.name, col, route, def: P.def, syl: P.syl, vowels: !!P.vowels, fal: !!P.fal }
      : null
  );
  const why = (d.why.match(/[^.!?]+[.!?]+(\s|$)/g) || [d.why]).map((s) => s.trim()),
    tip = why[why.length - 1],
    facts = P.facts[lv - 1] || [],
    logged = exLogged(e.id),
    more = U.exMore === e.id,
    ink = exInk(col);
  return (
    (route.length ? PAT.card() : exSlides(col)) +
    '<div class="exfacts" style="--fi:' +
    ink +
    ';--fid:' +
    col +
    ';grid-template-columns:repeat(' +
    facts.length +
    ',minmax(0,1fr))">' +
    facts
      .map(
        (f) =>
          '<div class="exfact">' +
          (FACT_ICON[f[0]] ? '<svg viewBox="0 0 24 24" aria-hidden="true">' + FACT_ICON[f[0]] + '</svg>' : '') +
          '<span class="l">' +
          esc(f[1]) +
          '</span><span class="v">' +
          esc(f[2]) +
          '</span></div>'
      )
      .join('') +
    '</div>' +
    '<div class="extip"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.6 1 2.5h6c0-.9.2-1.7 1-2.5A6 6 0 0 0 12 3z"/></svg><span>' +
    tip +
    '</span></div>' +
    '<div class="hdr exs">How to do it</div><ol class="exsteps">' +
    P.how.map((s) => '<li><span>' + s + '</span></li>').join('') +
    '</ol>' +
    '<div class="hdr exs">Where you feel it</div><div class="exwhere">' +
    exHead(P.where[0], col) +
    '<span>' +
    P.where[1] +
    '</span></div>' +
    '<div class="hdr exs">Levels</div><div class="exlvls" role="radiogroup" aria-label="Level" style="--c:' +
    col +
    '">' +
    [1, 2, 3]
      .map(
        (n) =>
          '<button class="exlvl' +
          (n === lv ? ' on' : '') +
          '" role="radio" aria-checked="' +
          (n === lv) +
          '" aria-label="Level ' +
          n +
          '" data-a="exLevel" data-v="' +
          n +
          '">' +
          n +
          '</button>'
      )
      .join('') +
    '</div><p class="exlvt">' +
    esc(L[0]) +
    '</p>' +
    (logged ? '<p class="foot exlog">Last logged at level ' + logged + '</p>' : '') +
    '<div class="hdr exs">Why it helps</div><div class="grp"><div class="prose">' +
    (more || why.length < 3
      ? why.slice(0, -1).join(' ') || why[0]
      : why[0] + ' <button class="exmore" data-a="exMore">More</button>') +
    '</div></div>' +
    COACH.exerciseRow(e.id) +
    '<div class="hdr exs">In a song</div><div class="grp"><div class="prose"><ul>' +
    d.song.map((x) => '<li><b>' + x[0] + '.</b> ' + x[1] + '</li>').join('') +
    '</ul></div></div>'
  );
}
// one exercise with its level picker and notes pencil (the Edit session sheet)
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
// Q20 one take: play, its name and waveform (the playhead drawn over it while it plays), its length and its star.
// Shared by Application's card and Song practice. Tap the name for its notes (and Save or share, Delete); swipe left
// to delete. o: {fresh: marked new, name: what it's called, date: show the day it was sung}
function takeRow(t, o) {
  o = o || {};
  const n = noteStr(t.note),
    on = takePlaying(t.id),
    nm = o.name || 'Take';
  return sw(
    '<div class="row tkrow' +
      (on ? ' playing' : '') +
      '" data-tk="' +
      t.id +
      '"><button class="tkplay" data-a="playTake" data-k="' +
      t.id +
      '" aria-label="' +
      (on ? 'Pause ' : 'Play ') +
      esc(nm) +
      '">' +
      (on ? ICON.pause : ICON.play) +
      '</button><button class="lbl tk" data-a="takeNote" data-k="' +
      t.id +
      '" aria-label="Notes for ' +
      esc(nm) +
      '"><span class="tkn">' +
      esc(nm) +
      (o.fresh ? ' <em>new</em>' : '') +
      (o.date ? ' <small class="tkd">' + shortDate(t.created) + '</small>' : '') +
      '</span>' +
      APPL.wave(t.id) +
      (n ? '<small class="acc">' + esc(n) + '</small>' : '') +
      '</button><span class="tklen">' +
      mmss(t.len) +
      '</span><button class="ibtn star' +
      (t.star ? ' on' : '') +
      '" data-a="star" data-k="' +
      t.id +
      '" aria-label="' +
      (t.star ? 'Unstar ' : 'Star ') +
      esc(nm) +
      '" aria-pressed="' +
      !!t.star +
      '">' +
      ICON.star +
      '</button></div>',
    'delTake',
    t.id
  );
}
// Q20 the takes, newest first: the newest, then Compare ("This take | Take N", from the second take on), then the
// rest. list: newest first; o: {fresh: the newest was just sung, prev: the take to compare it with, name(t), date}
function takesBlock(list, o) {
  if (!list.length) return '';
  const nm = (t) => (o.name ? o.name(t) : 'Take');
  let h =
    '<div class="grp tkgrp">' +
    takeRow(list[0], { fresh: o.fresh, name: nm(list[0]), date: o.date && !sameDay(list[0].created) }) +
    '</div>';
  if (o.prev) h += APPL.cmpHTML(list[0], o.prev, nm(o.prev));
  if (list.length > 1)
    h +=
      '<div class="grp tkgrp tkolder">' +
      list
        .slice(1)
        .map((t) => takeRow(t, { name: nm(t), date: o.date && !sameDay(t.created) }))
        .join('') +
      '</div>';
  return h;
}
// Song practice: the record button (↻ Again once this practice has a take), then the song's takes, newest first
function takeRows(sid) {
  const sg = songById(sid),
    tk = TAKES.filter((t) => t.songId === sid).reverse(),
    mine = (X && X.takes) || [],
    fresh = !!(tk.length && mine.includes(tk[0].id)),
    again = tk.some((t) => mine.includes(t.id));
  return (
    '<div class="hdr">Takes</div><div class="grp"><button class="row recbtn' +
    (rec ? ' on' : '') +
    '" data-a="rec"><span class="dot" aria-hidden="true"></span><span id="recLbl">' +
    (rec ? 'Stop · ' + mmss(rec.t) + ' of ' + mmss(MAX_TAKE) : again ? '↻ Again' : 'Record a take') +
    '</span></button></div>' +
    (tk.length
      ? '<div class="apcard tkcard">' +
        takesBlock(tk, {
          fresh,
          prev: fresh && tk[1] ? tk[1] : null,
          name: (t) => TAKE.nameOf(t.id) || 'Take',
          date: true,
        }) +
        '</div>'
      : '') +
    '<p class="foot">Tap a take’s name for its notes. Swipe left to delete. Every take is kept. If you leave the app while recording, the take stops and is saved.</p>'
  );
}
/* ===== The one-page session (Q19) =====
   Foundation, Rotation and Application on one page. The step you're on (U.view: found, rot or app) is open; finished
   steps fold to a line you can tap to reopen (U.fEdit); the next one shows faded underneath. The taps, the folding and
   the pinned button live in onepage.js (OP) */
const FLOW_STEPS = [
  { v: 'found', name: 'Foundation', desc: 'Four core exercises. Tap a row for the level you reached, or Skip.' },
  { v: 'rot', name: 'Rotation', desc: 'Pick as many as you like. Each one gets its own level.' },
  { v: 'app', name: 'Application', desc: 'Sing a song or a section, then keep your best take.' },
];
const flowCur = () => ({ found: 0, rot: 1, app: 2 })[U.view] || 0;
// how long since an exercise was last done, for Rotation's rows
function agoTxt(id) {
  const e = D.ex[id];
  if (e && e.last) {
    const r = relDay(e.last);
    return r === 'today' ? 'Done today' : r.charAt(0).toUpperCase() + r.slice(1);
  }
  if (e && e.n) return 'Done before ' + UPDATE_DAY;
  return 'Not done yet';
}
// an exercise's note in the session, as the exercise notes sheet saves it: {w: [words], t: text}
function xnObj(id) {
  X.xn = X.xn || {};
  const n = X.xn[id];
  if (!n || typeof n !== 'object') X.xn[id] = { w: [], t: n || '' };
  if (!Array.isArray(X.xn[id].w)) X.xn[id].w = [];
  return X.xn[id];
}
const ringLv = (s, id) => (s === 'f' ? X.f : X.rot)[id];
// a row's box: open (the words showing), fold (picked, so it stepped back to one line) or shut
function ringState(s, id) {
  const st = (U.rings || {})[s + ':' + id],
    v = ringLv(s, id);
  if (st) return st;
  return v > 0 && noteStr(X.xn[id]) ? 'fold' : 'shut';
}
function ringSub(s, id) {
  const v = ringLv(s, id);
  if (v > 0) {
    const n = ringState(s, id) === 'fold' ? noteStr(X.xn[id]) : '';
    return 'Level ' + v + (n ? ' · ' + n : '');
  }
  if (s === 'f') return v === 0 ? 'Skipped' : 'Tap to set';
  return v === 0 ? 'Tap to set a level' : agoTxt(id);
}
const RING_C = 100.53; // the ring's length (2π × 16)
function ringSVG(s, v) {
  const t = v > 0 ? v : v === 0 ? (s === 'f' ? 'Skip' : '–') : s === 'f' ? '–' : '+';
  return (
    '<svg class="ring' +
    (v === 3 ? ' peak' : '') +
    '" viewBox="0 0 40 40" aria-hidden="true"><circle class="rtrack" cx="20" cy="20" r="16"/><circle class="arc" cx="20" cy="20" r="16" stroke-dasharray="' +
    RING_C +
    '" style="stroke-dashoffset:' +
    (RING_C * (1 - (v > 0 ? v / 3 : 0))).toFixed(2) +
    '" transform="rotate(-90 20 20)"/><text x="20" y="25" class="' +
    (v === 0 && s === 'f' ? 'sk' : v > 0 ? 'on' : '') +
    '">' +
    t +
    '</text></svg>'
  );
}
const ringLabel = (e, s) => {
  const v = ringLv(s, e.id);
  return (
    e.name +
    ', ' +
    (v > 0 ? 'level ' + v : v === 0 && s === 'f' ? 'skipped' : 'not set') +
    '. Tap for ' +
    (s === 'f' ? 'the next level or Skip' : v === 3 ? 'none' : 'the next level')
  );
};
// the words for a row's box: how it felt at level 3, what kept it lower at 1 and 2; your own words and any picked
// words not in the list come last, so nothing picked is ever hidden
function cueWords(id, v) {
  const custom = !EX_WORDS[id];
  const base =
    v === 3 ? EX_WORDS[id] || EX_WORDS_DEFAULT : (EX_WHY[id] || (custom ? EX_WHY_DEFAULT : [])).concat(EX_WHY_ALL);
  const l = wordList('x_' + id, base);
  ((X.xn[id] && X.xn[id].w) || []).forEach((w) => {
    if (!l.includes(w)) l.push(w);
  });
  return l;
}
function cueHTML(s, id) {
  const v = ringLv(s, id);
  if (!(v > 0)) return '';
  const n = X.xn[id] && typeof X.xn[id] === 'object' ? X.xn[id] : { w: [], t: X.xn[id] || '' };
  return (
    '<p class="cueq">' +
    (v === 3 ? 'How did it feel?' : 'What kept it at level ' + v + '?') +
    '</p><div class="chips cues">' +
    cueWords(id, v)
      .map(
        (w) =>
          '<button class="chip' +
          (n.w.includes(w) ? ' on' : '') +
          '" data-a="rcue" data-k="' +
          esc(id) +
          '" data-s="' +
          s +
          '" data-v="' +
          esc(w) +
          '" aria-pressed="' +
          n.w.includes(w) +
          '">' +
          esc(w) +
          '</button>'
      )
      .join('') +
    '<button class="chip add" data-a="rown" data-k="' +
    esc(id) +
    '" data-s="' +
    s +
    '">+ Your own</button></div>' +
    (n.t ? '<p class="cuet">' + esc(n.t) + '</p>' : '')
  );
}
// one exercise: tap the row to go up a level (Foundation: 1, 2, 3, Skip; Rotation: 1, 2, 3, off)
function ringRow(e, s, big) {
  const v = ringLv(s, e.id),
    st = ringState(s, e.id);
  return (
    '<div class="rgi' +
    (big ? ' big' : '') +
    (v === 3 ? ' peak' : '') +
    (v > 0 && st === 'fold' ? ' folded' : '') +
    '" data-rk="' +
    s +
    ':' +
    esc(e.id) +
    '"><span class="rsweep" aria-hidden="true"></span><button class="row rgrow' +
    (v === 0 && s === 'f' ? ' skipped' : '') +
    '" data-a="ring" data-k="' +
    esc(e.id) +
    '" data-s="' +
    s +
    '" aria-label="' +
    esc(ringLabel(e, s)) +
    '">' +
    tile(e) +
    '<span class="lbl">' +
    (big ? '<span class="eyebrow">Suggested</span>' : '') +
    esc(e.name) +
    '<small>' +
    esc(ringSub(s, e.id)) +
    '</small></span>' +
    ringSVG(s, v) +
    '</button><div class="unfold' +
    (v > 0 && st === 'open' ? ' open' : '') +
    '"><div><div class="cuebox">' +
    (v > 0 && st === 'open' ? cueHTML(s, e.id) : '') +
    '</div></div></div></div>'
  );
}
const ROT_SORTS = [
  ['old', 'Longest ago'],
  ['recent', 'Most recent'],
  ['az', 'A–Z'],
];
// More exercises, in the order picked: longest ago (never done first, as the suggestion), most recent, or A to Z
function rotSorted(list) {
  const score = (e) => {
    const x = D.ex[e.id];
    if (!x || (!x.n && !x.last)) return -2e13;
    if (!x.last) return -1e13 + (x.n || 0);
    return new Date(x.last).getTime();
  };
  const l = list.map((e, i) => ({ e, i, s: score(e) }));
  const by = U.rSort || 'old';
  if (by === 'az') l.sort((a, b) => a.e.name.localeCompare(b.e.name, 'en-GB') || a.i - b.i);
  else if (by === 'recent') l.sort((a, b) => b.s - a.s || a.i - b.i);
  else l.sort((a, b) => a.s - b.s || a.i - b.i);
  return l.map((x) => x.e);
}
function flowBody(i) {
  if (i === 0)
    return (
      '<div class="grp rings">' +
      FOUND.map((e) => ringRow(e, 'f')).join('') +
      '</div><p class="foot">Tap a row to go up a level: 1, 2, 3, then Skip.</p>'
    );
  if (i === 1) {
    const sg = suggested(),
      rest = rotSorted(allRot().filter((e) => e.id !== sg.id));
    return (
      '<div class="grp rings">' +
      ringRow(sg, 'r', true) +
      '</div><button class="sorthdr" data-a="rSort" aria-haspopup="menu"><span>More exercises&nbsp;·&nbsp;</span><span class="sortname">' +
      ROT_SORTS.find((x) => x[0] === (U.rSort || 'old'))[1] +
      '</span>' +
      ICON.down +
      '</button><div class="grp rings sortlist">' +
      rest.map((e) => ringRow(e, 'r')).join('') +
      '<button class="row acc" data-a="sheet" data-v="addEx"><span class="lbl">Add exercise</span>' +
      ICON.plus +
      '</button></div>'
    );
  }
  // Q20: carry on where you left off, sing, compare, keep the best take (application.js)
  return APPL.body();
}
// a finished step folded to one line: what was done and how long it took. Tap to reopen it
function flowLine(i) {
  const e = elapsedSec(),
    fE = Math.min(e, X.fE || 0),
    secs = i === 0 ? fE : Math.max(0, Math.min(e, X.rE || 0) - fE);
  let sum = '',
    skipped = false;
  if (i === 0) {
    const d = FOUND.filter((x) => X.f[x.id] > 0).length,
      sk = FOUND.length - d;
    sum = d + ' done' + (sk ? ' · ' + sk + ' skipped' : '');
    skipped = !d;
  } else {
    const n = Object.keys(X.rot).filter((k) => X.rot[k] > 0).length;
    sum = n + ' exercise' + (n === 1 ? '' : 's');
    skipped = !n;
  }
  return (
    '<button class="osum' +
    (skipped ? ' skipped' : '') +
    '" data-a="flowOpen" data-v="' +
    i +
    '" aria-label="' +
    FLOW_STEPS[i].name +
    (skipped ? ', not today' : ', ' + sum) +
    '. Tap to change"><span class="otick" aria-hidden="true">' +
    (skipped ? '–' : ICON.check) +
    '</span><span class="lbl">' +
    FLOW_STEPS[i].name +
    '<small>' +
    (skipped ? 'Not today' : sum + ' · ' + clk(secs)) +
    '</small></span><span class="oedit" aria-hidden="true">Edit</span></button>'
  );
}
function flowSec(i, cur) {
  const st =
    U.fEdit === i && i < cur ? 'reopened' : i < cur ? 'folded' : i === cur ? 'active' : i === cur + 1 ? 'preview' : '';
  if (!st) return '';
  const s = FLOW_STEPS[i];
  let h =
    '<section class="osec ' +
    st +
    '" data-sec="' +
    i +
    '"' +
    (st === 'preview' ? ' inert aria-hidden="true"' : '') +
    '>';
  if (st === 'folded') h += flowLine(i);
  else if (st === 'reopened')
    h +=
      '<div class="osedit"><h1>' +
      s.name +
      '</h1><button class="osdone" data-a="flowDone">Done</button></div><p class="note">Change anything, then tap Done.</p>' +
      flowBody(i);
  else if (st === 'preview')
    h +=
      '<p class="osnext">Coming up · ' +
      (i + 1) +
      ' of 3</p><h1>' +
      s.name +
      '</h1><p class="note">' +
      s.desc +
      '</p>' +
      flowBody(i);
  else h += '<h1>' + s.name + '</h1><p class="note">' + s.desc + '</p>' + flowBody(i);
  return h + '</section>';
}
function scrFlow() {
  const cur = flowCur();
  return '<div class="onep">' + [0, 1, 2].map((i) => flowSec(i, cur)).join('') + '</div>';
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
