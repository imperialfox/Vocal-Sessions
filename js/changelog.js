/* Vocal Sessions · changelog.js
   Settings › Changelog, built from CHANGELOG.md.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Changelog (Settings › Changelog), built from CHANGELOG.md =====
   Each version: "## 3.7 · 15 Oct 2026", then "*Headline*" on the next line.
   "<!-- era: Name · description -->" under an x.0 version names that era.
   "<!-- area: backup -->" on its own line sets the area for the version (right after the headline) or for the next section;
   at the end of a bullet it sets that bullet's area. Areas: practice, progress, recordings, backup, look, fixes. */
const LOG_AREAS = {
  p: ['Practice', 'var(--accent)'],
  g: ['Progress', 'var(--cF)'],
  r: ['Recordings', 'var(--coral)'],
  d: ['Backup & data', 'var(--cR)'],
  l: ['Look & feel', 'var(--cA)'],
  f: ['Fixes', 'var(--done)'],
};
const AREA_CODE = { practice: 'p', progress: 'g', recordings: 'r', backup: 'd', look: 'l', fixes: 'f' };
const MONTHS = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12 };
let LOG = null,
  LOG_ERAS = {},
  LOG_STATE = 'idle',
  LOG_WARN = [];
function parseChangelog(md) {
  const out = [],
    eras = {},
    warn = [];
  let e = null,
    sec = null,
    item = null,
    area = null;
  const code = (n) => {
    if (AREA_CODE[n]) return AREA_CODE[n];
    warn.push('unknown area "' + n + '"');
    return null;
  };
  const newSec = (t, n) => {
    sec = { t, n: n || '', a: area || e.area, items: [] };
    e.notes.push(sec);
    area = null;
    item = null;
  };
  for (const raw of String(md).split(/\r?\n/)) {
    const line = raw.replace(/\s+$/, '');
    let m;
    if ((m = line.match(/^## (\d+(?:\.\d+)+) · (\d{1,2}) ([A-Za-z]{3})[A-Za-z]* (\d{4})$/))) {
      const mo = MONTHS[m[3].toLowerCase()];
      if (!mo) warn.push(m[1] + ': unknown month');
      e = {
        v: m[1],
        date: m[4] + '-' + String(mo || 1).padStart(2, '0') + '-' + m[2].padStart(2, '0'),
        title: '',
        intro: '',
        notes: [],
        area: null,
      };
      out.push(e);
      sec = null;
      item = null;
      area = null;
      continue;
    }
    if (/^#{1,2} /.test(line)) {
      if (e && /^## /.test(line)) warn.push('heading not understood: ' + line);
      e = null;
      continue;
    }
    if (!e) continue;
    if ((m = line.match(/^<!--\s*era:\s*(.+?)\s*-->$/))) {
      const p = m[1].split(' · ');
      eras[+e.v.split('.')[0]] = [p[0], p.slice(1).join(' · ')];
      continue;
    }
    if ((m = line.match(/^<!--\s*area:\s*([a-z]+)\s*-->$/))) {
      area = code(m[1]);
      if (!sec) e.area = area;
      continue;
    }
    if (!e.title && !sec && !e.intro && (m = line.match(/^\*([^*](?:.*[^*])?)\*$/))) {
      e.title = m[1];
      continue;
    }
    if (!line.trim() || line === '---') continue;
    if ((m = line.match(/^\*\*([^*]+[^*:])\*\*(?: (\(.+\)))?$/))) {
      newSec(m[1], m[2]);
      continue;
    }
    if ((m = line.match(/^\s{2,}[-*] (.+)$/)) && item) {
      item[2].push(m[1]);
      continue;
    }
    let text = null;
    if ((m = line.match(/^[-*] (.+)$/))) text = m[1];
    else if (/^\*\*[^*]+:\*\* /.test(line)) text = line;
    if (text != null) {
      if (!sec || (area && !/^[-*] /.test(line))) newSec('');
      let a = null;
      const t = text.match(/\s*<!--\s*area:\s*([a-z]+)\s*-->\s*$/);
      if (t) {
        a = code(t[1]);
        text = text.slice(0, t.index);
      }
      item = [a || sec.a || e.area || (e.v.split('.').length === 3 ? 'f' : 'p'), text, []];
      sec.items.push(item);
      continue;
    }
    if (!e.notes.length) e.intro += (e.intro ? ' ' : '') + line;
  }
  out.forEach((x) => {
    if (!x.title) warn.push(x.v + ': no headline');
    x.notes = x.notes.filter((s) => s.items.length).map((s) => [s.t, s.items, s.n]);
    if (x.intro.replace(/\.$/, '') === x.title) x.intro = '';
    x.hl = Math.min(
      4,
      x.notes.reduce((n, s) => n + s[1].length, 0)
    );
    if (!x.hl) warn.push(x.v + ': no changes listed');
  });
  return { out, eras, warn };
}
async function fetchChangelog() {
  if (LOG_STATE === 'loading') return;
  LOG_STATE = 'loading';
  try {
    const r = await fetch('CHANGELOG.md', { cache: 'no-cache' });
    if (!r.ok) throw new Error(r.status);
    const p = parseChangelog(await r.text());
    if (!p.out.length) throw new Error('empty');
    LOG = p.out;
    LOG_ERAS = p.eras;
    LOG_WARN = p.warn;
    LOG_STATE = 'ready';
  } catch (err) {
    LOG_STATE = LOG ? 'ready' : 'error';
  }
  if (U.view === 'log') rerender();
}

const LOGSEEN = new Set(),
  TI = (k) => (LOGSEEN.has(k) ? 'tl-in seen' : 'tl-in') + '" data-r="' + k;
const logKind = (v) => (/^\d+\.0$/.test(v) ? 'major' : v.split('.').length === 3 ? 'patch' : 'minor');
const LOG_KIND = { major: 'Redesign', minor: 'New features', patch: 'Fixes' };
const logItems = (e) => e.notes.reduce((a, s) => a.concat(s[1]), []);
const mdi = (s) =>
  esc(s)
    .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
const logDate = (d) => new Date(d + 'T12:00:00');
const logId = (v) => 'log-' + v.replace(/\./g, '-');
// highlights: the first change from each section, then fill up
function logHL(e) {
  const out = [];
  let i = 0;
  while (out.length < e.hl) {
    let added = false;
    for (const s of e.notes) {
      if (s[1][i] && out.length < e.hl) {
        out.push(s[1][i]);
        added = true;
      }
    }
    if (!added) break;
    i++;
  }
  return out;
}
function logGrowth() {
  const acc = {};
  Object.keys(LOG_AREAS).forEach((k) => (acc[k] = 0));
  return LOG.slice()
    .reverse()
    .map((e) => {
      const it = logItems(e);
      it.forEach((x) => acc[x[0]]++);
      return {
        v: e.v,
        date: e.date,
        c: Object.assign({}, acc),
        add: it.length,
        by: it.reduce((m, x) => ((m[x[0]] = (m[x[0]] || 0) + 1), m), {}),
      };
    });
}
function logChart(G) {
  const W = 340,
    H = 140,
    top = 8,
    bot = 22,
    n = G.length,
    max = Math.max(...G.map((g) => Object.values(g.c).reduce((a, b) => a + b, 0)));
  const X = (i) => 6 + (i * (W - 12)) / (n - 1),
    Y = (v) => top + (H - top - bot) * (1 - v / max);
  const keys = Object.keys(LOG_AREAS);
  let base = G.map(() => 0),
    paths = '';
  keys.forEach((k) => {
    const lo = base.slice(),
      hi = base.map((b, i) => b + G[i].c[k]);
    paths +=
      '<path class="ar" fill="' +
      LOG_AREAS[k][1] +
      '" d="M' +
      hi.map((v, i) => X(i).toFixed(1) + ' ' + Y(v).toFixed(1)).join(' L') +
      ' L' +
      lo
        .map((v, i) => [X(i), Y(v)])
        .reverse()
        .map((p) => p[0].toFixed(1) + ' ' + p[1].toFixed(1))
        .join(' L') +
      'Z"/>';
    base = hi;
  });
  const tot = base;
  let grid = '';
  [0, 0.5, 1].forEach((f) => {
    const y = Y(max * f);
    grid += '<line x1="0" x2="' + W + '" y1="' + y + '" y2="' + y + '" stroke="var(--grid)" stroke-width="1"/>';
  });
  let dots = '',
    labels = '',
    hits = '',
    lastL = -99;
  G.forEach((g, i) => {
    const k = logKind(g.v),
      r = k === 'major' ? 4.5 : k === 'minor' ? 3.2 : 2.2,
      on = U.logPick === i;
    dots +=
      '<circle cx="' +
      X(i) +
      '" cy="' +
      Y(tot[i]) +
      '" r="' +
      (on ? r + 2 : r) +
      '" fill="' +
      (on ? 'var(--accent)' : 'var(--surface)') +
      '" stroke="var(--accent)" stroke-width="2"/>';
    if (
      (k === 'major' || i === n - 1) &&
      (X(i) - lastL > 34 || i === n - 1) &&
      (i === n - 1 || X(n - 1) - X(i) > 34) &&
      (lastL = X(i))
    )
      labels +=
        '<text x="' +
        X(i) +
        '" y="' +
        (H - 5) +
        '" text-anchor="' +
        (i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle') +
        '" font-size="11" fill="var(--fg2)" font-weight="' +
        (i === n - 1 ? 600 : 400) +
        '">' +
        g.v +
        '</text>';
    hits +=
      '<rect data-a="lgpick" data-k="' +
      i +
      '" x="' +
      (X(i) - (W - 12) / (n - 1) / 2) +
      '" y="0" width="' +
      (W - 12) / (n - 1) +
      '" height="' +
      H +
      '" fill="transparent"/>';
  });
  const rule =
    U.logPick != null
      ? '<line x1="' +
        X(U.logPick) +
        '" x2="' +
        X(U.logPick) +
        '" y1="' +
        top +
        '" y2="' +
        (H - bot) +
        '" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="3 3"/>'
      : '';
  return (
    '<svg id="lgchart" class="' +
    (U.logPick != null ? 'picking' : '') +
    '" viewBox="0 0 ' +
    W +
    ' ' +
    H +
    '" role="img" aria-label="Improvements added over time, by area"><g' +
    (U.logDrawn ? '' : ' class="lgdraw"') +
    '>' +
    grid +
    paths +
    '<path d="M' +
    tot.map((v, i) => X(i).toFixed(1) + ' ' + Y(v).toFixed(1)).join(' L') +
    '" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"/></g>' +
    rule +
    dots +
    labels +
    hits +
    '</svg>'
  );
}
function logCardTop(G) {
  const all = G[G.length - 1],
    T = Object.values(all.c).reduce((a, b) => a + b, 0);
  if (U.logPick == null)
    return (
      '<div class="kick">Improvements</div><div class="bignum"><b>' +
      T +
      '</b></div><div class="sub2">across ' +
      LOG.length +
      ' versions since ' +
      fileDate(logDate(LOG[LOG.length - 1].date)) +
      '</div>'
    );
  const g = G[U.logPick],
    t = Object.values(g.c).reduce((a, b) => a + b, 0),
    e = LOG.find((x) => x.v === g.v);
  return (
    '<div class="kick">Version ' +
    g.v +
    ' · ' +
    shortDate(logDate(g.date)) +
    '</div><div class="bignum"><b>+' +
    g.add +
    '</b><span>' +
    esc(e.title) +
    '</span></div><div class="sub2">' +
    t +
    ' of ' +
    T +
    ' improvements by this version</div><button class="lgjump" data-a="lgjump" data-k="' +
    g.v +
    '">Show in timeline ' +
    ICON.fwd.replace('class="i"', 'class="i" style="width:16px;height:16px"') +
    '</button>'
  );
}
function logEntry(e, prev) {
  const k = logKind(e.v),
    it = logItems(e),
    open = U.logAll || U.logOpen.includes(e.v),
    now = e.v === APP_VERSION;
  const by = it.reduce((m, x) => ((m[x[0]] = (m[x[0]] || 0) + 1), m), {});
  const li = (x) =>
    '<li style="--c:' +
    LOG_AREAS[x[0]][1] +
    '">' +
    mdi(x[1]) +
    (open && x[2].length ? '<ul class="tl-sub">' + x[2].map((c) => '<li>' + mdi(c) + '</li>').join('') + '</ul>' : '') +
    '</li>';
  let h = '';
  if (!prev || prev.date !== e.date)
    h += '<div class="tl-date ' + TI('d' + e.date) + '">' + fileDate(logDate(e.date)) + '</div>';
  h +=
    '<article class="tl-item ' +
    k +
    (now ? ' now' : '') +
    ' ' +
    TI(logId(e.v)) +
    '" id="' +
    logId(e.v) +
    '"><span class="tl-node" aria-hidden="true"></span><div class="tl-card">' +
    '<div class="tl-head"><span class="tl-v">' +
    e.v +
    '</span><span class="tl-kind">' +
    LOG_KIND[k] +
    '</span>' +
    (now ? '<span class="tl-nowc">● This version</span>' : '') +
    '<span class="tl-n">+' +
    it.length +
    '</span></div>' +
    '<div class="tl-title">' +
    esc(e.title) +
    '</div>' +
    '<div class="tl-bar" aria-hidden="true">' +
    Object.keys(LOG_AREAS)
      .filter((a) => by[a])
      .map((a) => '<i style="flex:' + by[a] + ';background:' + LOG_AREAS[a][1] + '"></i>')
      .join('') +
    '</div>';
  if (open)
    h +=
      (e.intro ? '<p class="tl-intro">' + mdi(e.intro) + '</p>' : '') +
      e.notes
        .map(
          (s) =>
            (s[0] ? '<div class="tl-sec">' + esc(s[0]) + '</div>' : '') +
            (s[2]
              ? '<p class="tl-intro" style="margin-top:2px">' + mdi(s[2].replace(/^\((.*)\)$/, '$1')) + '</p>'
              : '') +
            '<ul class="tl-list">' +
            s[1].map(li).join('') +
            '</ul>'
        )
        .join('');
  else h += '<ul class="tl-list">' + logHL(e).map(li).join('') + '</ul>';
  if (it.length > e.hl && !U.logAll)
    h +=
      '<button class="tl-more' +
      (open ? ' open' : '') +
      '" data-a="logMore" data-k="' +
      e.v +
      '">' +
      (open ? 'Show less' : 'Show all ' + it.length + ' changes') +
      ICON.down +
      '</button>';
  else h += '<div style="height:10px"></div>';
  return h + '</div></article>';
}
function scrLog() {
  if (!LOG || !LOG.length)
    return (
      '<h1>Changelog</h1><div class="lgcard">' +
      (LOG_STATE === 'error'
        ? '<p class="note" style="margin:0 0 12px">The changelog couldn’t be loaded. Connect to the internet once and it’s kept for offline use.</p><button class="cta" data-a="logRetry">Try again</button>'
        : '<p class="note" style="margin:0">Loading…</p>') +
      '</div>'
    );
  const G = logGrowth();
  let h =
    '<h1>Changelog</h1>' +
    '<div class="lgcard" id="lgcard"><div id="lgtop">' +
    logCardTop(G) +
    '</div><div id="lgsvg">' +
    logChart(G) +
    '</div>' +
    '<div class="lglegend">' +
    Object.keys(LOG_AREAS)
      .map(
        (a) =>
          '<span><i style="background:' +
          LOG_AREAS[a][1] +
          '"></i>' +
          LOG_AREAS[a][0] +
          ' ' +
          G[G.length - 1].c[a] +
          '</span>'
      )
      .join('') +
    '</div></div>' +
    '<div class="seg wide" role="tablist" style="margin-top:18px"><span class="knob" aria-hidden="true"></span><button role="tab" data-a="logMode" data-v="hl" class="' +
    (U.logAll ? '' : 'on') +
    '" aria-selected="' +
    !U.logAll +
    '">Highlights</button><button role="tab" data-a="logMode" data-v="all" class="' +
    (U.logAll ? 'on' : '') +
    '" aria-selected="' +
    !!U.logAll +
    '">Every change</button></div>' +
    '<div class="tl">';
  let era = null,
    prev = null;
  LOG.forEach((e) => {
    const m = +e.v.split('.')[0];
    if (m !== era) {
      if (prev) {
        const gap = Math.round((logDate(prev.date) - logDate(e.date)) / 864e5);
        if (gap > 14)
          h +=
            '<div class="tl-gap ' +
            TI('gap' + m) +
            '">' +
            (gap > 60 ? Math.round(gap / 30.4) + ' months' : gap + ' days') +
            ' between versions</div>';
      }
      era = m;
      const E = LOG_ERAS[m] || ['', ''];
      const vs = LOG.filter((x) => +x.v.split('.')[0] === m);
      h +=
        '<div class="tl-era ' +
        TI('era' + m) +
        '"><span class="tl-badge">' +
        m +
        '</span><div><b>Version ' +
        m +
        (E[0] ? ' · ' + esc(E[0]) : '') +
        '</b><small>' +
        esc(E[1]) +
        ' · ' +
        plural(vs.length, 'release') +
        '</small></div></div>';
      prev = null;
    }
    h += logEntry(e, prev);
    prev = e;
  });
  return (
    h +
    '<div class="tl-end ' +
    TI('end') +
    '"><span class="tl-badge" aria-hidden="true">' +
    ICON.star.replace('class="i"', 'class="i" style="width:16px;height:16px;color:#fff"') +
    '</span><span>Started ' +
    fileDate(logDate(LOG[LOG.length - 1].date)) +
    '</span></div></div>'
  );
}
function updateLogCard() {
  const a = $('lgtop'),
    b = $('lgsvg');
  if (!a || !b) return;
  const G = logGrowth();
  a.innerHTML = logCardTop(G);
  b.innerHTML = logChart(G);
}
let logIO = null;
function logReveal() {
  if (logIO) {
    logIO.disconnect();
    logIO = null;
  }
  if (U.view !== 'log') return;
  U.logDrawn = true;
  const els = document.querySelectorAll('.tl-in:not(.seen)');
  if (!('IntersectionObserver' in window)) {
    els.forEach((el) => {
      el.classList.add('seen');
      LOGSEEN.add(el.dataset.r);
    });
    return;
  }
  logIO = new IntersectionObserver(
    (es) =>
      es.forEach((x) => {
        if (x.isIntersecting) {
          x.target.classList.add('seen');
          LOGSEEN.add(x.target.dataset.r);
          logIO.unobserve(x.target);
        }
      }),
    { rootMargin: '0px 0px -6% 0px' }
  );
  els.forEach((el) => logIO.observe(el));
}
