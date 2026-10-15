/* Vocal Sessions · backup.js
   Backups: export, check, restore and undo; Copy for Toggl.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Backup ===== */
// Files are named by month and device, e.g. "Vocal Sessions backup · 2026-10 · iPhone.json".
// Backing up again in the same month replaces that month's file, so the folder keeps one file per month per device.
const blobToDataURL = (b) =>
  new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => res(r.result);
    r.onerror = () => rej(r.error);
    r.readAsDataURL(b);
  });
function dataURLToBlob(u) {
  const [head, b64] = u.split(',');
  const type = (head.match(/data:([^;]+)/) || [])[1] || 'application/octet-stream';
  const bin = atob(b64);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return new Blob([arr], { type });
}
const BLOG = 'vocalBackupLog',
  README_NAME = 'READ ME – Vocal Sessions backups.txt';
function deviceName() {
  const u = navigator.userAgent || '';
  if (/iPad/.test(u) || (/Macintosh/.test(u) && navigator.maxTouchPoints > 1)) return 'iPad';
  if (/iPhone|iPod/.test(u)) return 'iPhone';
  if (/Macintosh/.test(u)) return 'Mac';
  if (/Android/.test(u)) return 'Android';
  return 'computer';
}
const thisDev = () => 'this ' + deviceName();
const ym = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
const backupName = (d) => 'Vocal Sessions backup · ' + ym(d) + ' · ' + deviceName() + '.json';
const mb = (n) => (n < 1048576 ? Math.max(1, Math.round(n / 1024)) + ' KB' : (n / 1048576).toFixed(1) + ' MB');
function loadLog() {
  try {
    const a = JSON.parse(localStorage.getItem(BLOG) || '[]');
    return Array.isArray(a) ? a.filter((x) => x && x.at && !isNaN(new Date(x.at))) : [];
  } catch (e) {
    return [];
  }
}
function addLog(e) {
  const a = loadLog();
  a.unshift(e);
  try {
    localStorage.setItem(BLOG, JSON.stringify(a.slice(0, 24)));
  } catch (x) {}
}
// check code: a SHA-256 fingerprint of everything in the backup, so a cut-off or edited file is spotted
async function checkCode(p) {
  if (!(window.crypto && crypto.subtle && window.TextEncoder)) return null;
  try {
    const buf = await crypto.subtle.digest(
      'SHA-256',
      new TextEncoder().encode(
        JSON.stringify({ data: p.data, draft: p.draft == null ? null : p.draft, takes: p.takes || [] })
      )
    );
    return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, '0')).join('');
  } catch (e) {
    return null;
  }
}
function sumOf(d, takes) {
  const all = (d.sessions || []).concat(d.songSessions || []);
  const t = all
    .map((x) => +new Date(x.date))
    .filter(isFinite)
    .sort((a, b) => a - b);
  return {
    sessions: (d.sessions || []).length,
    songPractice: (d.songSessions || []).length,
    songs: (d.songs || []).length,
    recordings: (takes || []).length,
    minutes: all.reduce((a, x) => a + (+x.mins || 0), 0),
    first: t.length ? new Date(t[0]).toISOString() : null,
    last: t.length ? new Date(t[t.length - 1]).toISOString() : null,
  };
}
const plural = (n, w, ws) => n + ' ' + (n === 1 ? w : ws || w + 's');
// plain-English note at the top of every backup file, for anyone who finds it later
function readmeLines(now, s) {
  return [
    'This is a backup from Vocal Sessions, a singing practice app for iPhone, iPad and Mac.',
    'It holds ' +
      plural(s.sessions, 'practice session') +
      ', ' +
      plural(s.songPractice, 'song practice', 'song practices') +
      ', ' +
      plural(s.recordings, 'voice recording') +
      ', plus exercises, songs and their lyrics, notes and monthly minutes.',
    'Made on ' +
      deviceName() +
      ' on ' +
      fileDate(now) +
      ' at ' +
      timeOf(now) +
      ' with Vocal Sessions ' +
      APP_VERSION +
      '.',
    'To restore it: open ' +
      APP_URL +
      ' and add it to your Home Screen. Then open Settings (the gear at the top of Today), tap Import backup and choose this file.',
    'To check it without restoring: Settings, then Check a backup.',
    'There is one backup file per month for each device. A newer one from the same month replaces the older one.',
    'Please don’t edit this file. The check code at the end confirms nothing is missing or changed.',
  ];
}
function backupText(p) {
  return (
    '{\n' +
    Object.keys(p)
      .map(
        (k) =>
          '  ' +
          JSON.stringify(k) +
          ': ' +
          (k === 'README' || k === 'summary'
            ? JSON.stringify(p[k], null, 2).replace(/\n/g, '\n  ')
            : JSON.stringify(p[k]))
      )
      .join(',\n') +
    '\n}\n'
  );
}
function readmeText() {
  const now = new Date();
  return [
    'Vocal Sessions backups',
    '======================',
    '',
    'This folder holds backups from Vocal Sessions, a singing practice app. It runs in Safari and is added to the Home Screen like an app.',
    '',
    'App: ' + APP_URL,
    'Code and instructions: ' + REPO,
    '',
    'WHAT’S IN EACH BACKUP',
    'Every practice session and its minutes, exercise levels, songs with their lyrics and marks, notes, how each session went, and voice recordings.',
    '',
    'FILE NAMES',
    'Vocal Sessions backup · YEAR-MONTH · DEVICE.json',
    'For example: Vocal Sessions backup · ' + ym(now) + ' · ' + deviceName() + '.json',
    'There is one file per month for each device (iPhone, iPad or Mac). Backing up again in the same month replaces that month’s file.',
    '',
    'HOW TO RESTORE',
    '1. Open ' + APP_URL + ' in Safari and add it to the Home Screen (Share, then Add to Home Screen).',
    '2. Open the app, tap the gear at the top of Today for Settings, and tap Import backup.',
    '3. Choose the newest file. The app shows what’s inside and compares it with what’s on the device before anything is replaced.',
    '4. Changed your mind? Settings, then Undo last restore, for 30 days.',
    '',
    'HOW TO CHECK A BACKUP',
    'Settings, then Check a backup. Each file has a check code that confirms it’s complete and unchanged.',
    '',
    'CAN I DELETE OLD ONES?',
    'Yes, once you have newer ones. Keep at least the last few months.',
    '',
    'Written by Vocal Sessions ' + APP_VERSION + ' on ' + fileDate(now) + '.',
    '',
  ].join('\n');
}

// read a backup file and work out whether it can be trusted, without changing anything
async function inspectBackup(text, name, size) {
  const r = { name: name || '', size: size == null ? text.length : size };
  let p = null;
  try {
    p = JSON.parse(text);
  } catch (e) {}
  if (!p || typeof p !== 'object' || Array.isArray(p)) {
    r.status = 'broken';
    r.why = /vocal-sessions/.test(String(text).slice(0, 6000))
      ? 'It’s a Vocal Sessions backup, but the file is cut short or damaged, so it can’t be read. Try an older backup.'
      : 'This file isn’t a Vocal Sessions backup.';
    return r;
  }
  if (p.app !== 'vocal-sessions' || !p.data) {
    r.status = 'broken';
    r.why = 'This file isn’t a Vocal Sessions backup.';
    return r;
  }
  const code = p.checkCode ? await checkCode(p) : null;
  const d = cleanData(p.data);
  if (!d || (p.takes != null && !Array.isArray(p.takes))) {
    r.status = 'broken';
    r.why = 'The backup is damaged inside, so it can’t be restored. Try an older backup.';
    return r;
  }
  const ok = [];
  let bad = 0;
  for (const t of p.takes || []) {
    try {
      if (!t || !t.id || typeof t.data !== 'string' || !/^data:[^,]*;base64,/.test(t.data)) throw 0;
      atob(t.data.slice(t.data.indexOf(',') + 1));
      ok.push(t);
    } catch (e) {
      bad++;
    }
  }
  r.bad = bad;
  r.exportedAt = isNaN(new Date(p.exportedAt)) ? null : p.exportedAt;
  r.device = typeof p.device === 'string' ? p.device : '';
  r.version = typeof p.appVersion === 'string' ? p.appVersion : '';
  r.p = Object.assign({}, p, {
    data: d,
    takes: ok,
    draft: p.draft && typeof p.draft === 'object' && +p.draft.start > 0 ? p.draft : null,
  });
  r.sum = sumOf(d, ok);
  r.newer = (+d.schema || 0) > SCHEMA;
  r.code = !p.checkCode ? 'none' : code == null ? 'unchecked' : code === p.checkCode ? 'match' : 'mismatch';
  r.status =
    r.code === 'mismatch'
      ? 'changed'
      : bad
        ? 'partial'
        : r.code === 'match'
          ? 'good'
          : r.code === 'none'
            ? 'old'
            : 'unchecked';
  return r;
}
async function prepareExport() {
  U.sheet = 'exporting';
  U.sd = {};
  rerender();
  try {
    const takes = await allTakes();
    const out = [];
    for (const t of takes) {
      const c = Object.assign({}, t);
      delete c.blob;
      c.data = await blobToDataURL(t.blob);
      out.push(c);
    }
    const now = new Date(),
      sm = sumOf(D, out);
    const p = {
      README: readmeLines(now, sm),
      app: 'vocal-sessions',
      format: 2,
      appVersion: APP_VERSION,
      exportedAt: now.toISOString(),
      device: deviceName(),
      summary: sm,
      data: D,
      draft: X || null,
      takes: out,
    };
    p.checkCode = await checkCode(p);
    const file = new File([backupText(p)], backupName(now), { type: 'application/json' });
    // read the finished file back and check it before offering to save it
    const back = await inspectBackup(await file.text(), file.name, file.size);
    const okBack =
      (back.status === 'good' || (back.status === 'old' && !p.checkCode)) &&
      back.sum.sessions === sm.sessions &&
      back.sum.songPractice === sm.songPractice &&
      back.sum.recordings === sm.recordings;
    if (!okBack) throw new Error('read-back failed');
    pendingExport = { file, at: p.exportedAt, s: sm, code: p.checkCode, verified: back.status === 'good' };
    U.sheet = 'exportReady';
  } catch (e) {
    U.sheet = null;
    toast('Couldn’t create the backup. Try again.');
  }
  rerender();
}
async function saveExport() {
  const p = pendingExport;
  if (!p) return;
  const r = await shareFile(p.file);
  if (r === 'cancelled') {
    toast('Backup not saved');
    return;
  }
  D.lastBackup = p.at;
  save();
  addLog({
    at: p.at,
    name: p.file.name,
    size: p.file.size,
    sessions: p.s.sessions,
    songPractice: p.s.songPractice,
    recordings: p.s.recordings,
    code: (p.code || '').slice(0, 8),
    verified: p.verified,
    how: r,
  });
  pendingExport = null;
  U.sheet = null;
  rerender();
  toast(r === 'shared' ? 'Backup saved' : 'Backup downloaded');
}
let pickMode = 'import';
function readBackupFile(file) {
  const fr = new FileReader();
  fr.onload = async () => {
    const rep = await inspectBackup(String(fr.result), file.name, file.size);
    pendingImport = rep;
    U.sheet = 'bkReport';
    U.sd = { mode: pickMode };
    rerender();
  };
  fr.onerror = () => toast('Couldn’t read that file');
  fr.readAsText(file);
}
async function restoreImport() {
  const r = pendingImport;
  if (!r || !r.p) return;
  const p = r.p;
  U.sheet = 'importing';
  U.sd = {};
  rerender();
  try {
    stopPlayback();
    if (rec) stopRec();
    // decode every recording first, so a bad file can't leave you with half your data
    const ready = p.takes.map((t) => {
      const c = Object.assign({}, t);
      c.blob = dataURLToBlob(t.data);
      delete c.data;
      return c;
    });
    // keep a copy of what's here now, so the restore can be undone
    let undoOK = true;
    try {
      await putUndo({
        id: 'last',
        at: Date.now(),
        data: JSON.parse(JSON.stringify(D)),
        draft: X ? JSON.parse(JSON.stringify(X)) : null,
        takes: await allTakes(),
        restored: p.data.sessions.concat(p.data.songSessions).map((x) => x.id),
        from: r.name || '',
      });
    } catch (e) {
      undoOK = false;
      await clearUndo();
    }
    await clearTakes();
    for (const c of ready) await putTake(c);
    D = cleanData(p.data) || {};
    migrate();
    D.lastBackup = p.exportedAt || new Date().toISOString();
    save();
    X = p.draft || null;
    normX();
    saveDraft();
    await refreshTakes();
    await refreshUndo();
    pendingImport = null;
    U = freshU();
    window.scrollTo(0, 0);
    render();
    toast(undoOK ? 'Backup restored' : 'Backup restored. Undo isn’t available: not enough space.');
  } catch (e) {
    U.sheet = null;
    rerender();
    toast('Couldn’t restore that backup');
  }
}
async function undoRestore() {
  const u = await getUndo();
  if (!u) {
    UNDO = null;
    U.sheet = null;
    rerender();
    toast('Nothing to undo');
    return;
  }
  U.sheet = 'undoing';
  U.sd = {};
  rerender();
  try {
    stopPlayback();
    if (rec) stopRec();
    await clearTakes();
    for (const t of u.takes || []) await putTake(t);
    D = cleanData(u.data) || {};
    migrate();
    save();
    X = u.draft && +u.draft.start > 0 ? u.draft : null;
    normX();
    saveDraft();
    await clearUndo();
    UNDO = null;
    await refreshTakes();
    U = freshU();
    U.tab = 'settings';
    window.scrollTo(0, 0);
    render();
    toast('Restore undone');
  } catch (e) {
    U.sheet = null;
    rerender();
    toast('Couldn’t undo the restore');
  }
}
// sessions logged after a restore, which undoing it would remove
function sinceRestore(u) {
  if (!u) return 0;
  const keep = new Set(
    (u.restored || []).concat(
      ((u.data || {}).sessions || []).concat((u.data || {}).songSessions || []).map((x) => x.id)
    )
  );
  return D.sessions.concat(D.songSessions).filter((x) => !keep.has(x.id)).length;
}

const BK_STAT = (r) =>
  ({
    good: ['ok', ICON.okc, 'This backup is complete', 'The check code matches, so nothing is missing or changed.'],
    unchecked: [
      'ok',
      ICON.okc,
      'This backup reads correctly',
      'This browser can’t verify the check code, but everything inside reads correctly.',
    ],
    old: [
      'ok',
      ICON.okc,
      'This backup reads correctly',
      'It was made before backups had check codes, so it can’t be fully verified. Everything inside reads correctly.',
    ],
    partial: [
      'warn',
      ICON.warn,
      'Some recordings are damaged',
      plural(r.bad, 'recording') + ' can’t be read and will be left out. Everything else is fine.',
    ],
    changed: [
      'warn',
      ICON.warn,
      'This backup has been changed',
      'The check code doesn’t match, so the file may have been edited or not fully copied. It still reads, but check what’s inside before restoring.' +
        (r.bad ? ' ' + plural(r.bad, 'recording') + ' can’t be read.' : ''),
    ],
    broken: ['bad', ICON.bad, 'This file can’t be used', r.why],
  })[r.status];
const bkStat = (r) => {
  const b = BK_STAT(r);
  return '<div class="bkstat ' + b[0] + '">' + b[1] + '<div><b>' + b[2] + '</b>' + esc(b[3]) + '</div></div>';
};
const when = (d) => (d ? fileDate(new Date(d)) + ' at ' + timeOf(d) : 'Unknown');
function bkReportHTML(r, mode) {
  const imp = mode === 'import';
  let b = bkStat(r);
  if (r.newer && r.status !== 'broken')
    b +=
      '<div class="bkstat warn" style="margin-top:8px">' +
      ICON.warn +
      '<div><b>Made by a newer version</b>This backup is from Vocal Sessions ' +
      esc(r.version || '') +
      ', which is newer than this app (' +
      APP_VERSION +
      '). Pull down on Today to update first, then restore it.</div></div>';
  if (r.status === 'broken')
    return sheetWrap(
      imp ? 'Can’t restore' : 'Backup check',
      b +
        '<div class="grp" style="margin-top:10px"><div class="row"><span class="lbl">File<small class="fname">' +
        esc(r.name) +
        '</small></span><span class="mut">' +
        mb(r.size) +
        '</span></div></div><button class="ghost" data-a="close">Done</button>'
    );
  const S = r.sum;
  b +=
    '<div class="grp" style="margin-top:10px"><div class="row"><span class="lbl">Backed up</span><span class="mut">' +
    when(r.exportedAt) +
    '</span></div>' +
    (r.device
      ? '<div class="row"><span class="lbl">Made on</span><span class="mut">' + esc(r.device) + '</span></div>'
      : '') +
    (r.version
      ? '<div class="row"><span class="lbl">App version</span><span class="mut">' + esc(r.version) + '</span></div>'
      : '') +
    '<div class="row"><span class="lbl">File<small class="fname">' +
    esc(r.name) +
    '</small></span><span class="mut">' +
    mb(r.size) +
    '</span></div></div>';
  if (imp) {
    const H = sumOf(D, TAKES);
    const cell = (a, h, f) =>
      '<span class="cmpv' +
      (a !== h ? ' diff' : '') +
      '">' +
      (f ? f(a) : a) +
      '</span><span class="cmpv">' +
      (f ? f(h) : h) +
      '</span>';
    const sd = (x) => (x ? shortDate(x) : '–');
    b +=
      '<div class="hdr">Compared with ' +
      thisDev() +
      '</div><div class="grp"><div class="row cmph"><span class="lbl"></span><span class="cmpv">Backup</span><span class="cmpv">' +
      esc(deviceName() === 'computer' ? 'Here' : 'This ' + deviceName()) +
      '</span></div>' +
      [
        ['Sessions', S.sessions, H.sessions],
        ['Song practice', S.songPractice, H.songPractice],
        ['Songs', S.songs, H.songs],
        ['Recordings', S.recordings, H.recordings],
        ['Practice time', S.minutes, H.minutes, hm],
        ['Latest practice', S.last, H.last, sd],
      ]
        .map((x) => '<div class="row"><span class="lbl">' + x[0] + '</span>' + cell(x[1], x[2], x[3]) + '</div>')
        .join('') +
      '</div>';
    const ids = new Set(r.p.data.sessions.map((x) => x.id)),
      gids = new Set(r.p.data.songSessions.map((x) => x.id)),
      tids = new Set(r.p.takes.map((x) => x.id));
    const lS = D.sessions.filter((x) => !ids.has(x.id)).length,
      lG = D.songSessions.filter((x) => !gids.has(x.id)).length,
      lT = TAKES.filter((x) => !tids.has(x.id)).length;
    const lost = [
      lS ? plural(lS, 'session') : '',
      lG ? plural(lG, 'song practice', 'song practices') : '',
      lT ? plural(lT, 'recording') : '',
    ].filter(Boolean);
    const older = H.last && (!S.last || new Date(S.last) < new Date(H.last));
    if (lost.length) {
      const list = lost.length > 1 ? lost.slice(0, -1).join(', ') + ' and ' + lost[lost.length - 1] : lost[0];
      b +=
        '<div class="bkstat warn" style="margin-top:12px">' +
        ICON.warn +
        '<div><b>' +
        (older ? 'This backup is older than ' + thisDev() : 'Not everything here is in this backup') +
        '</b>' +
        esc(list) +
        ' on ' +
        thisDev() +
        (lS + lG + lT === 1 ? ' isn’t' : ' aren’t') +
        ' in this backup. Restoring removes ' +
        (lS + lG + lT === 1 ? 'it' : 'them') +
        '.</div></div>' +
        '<button class="ghost" data-a="exportPrep">Back up ' +
        thisDev() +
        ' first</button>';
    } else if (D.sessions.length || D.songSessions.length || TAKES.length)
      b += '<p class="note" style="margin-top:12px">Everything on ' + thisDev() + ' is also in this backup.</p>';
    else
      b +=
        '<p class="note" style="margin-top:12px">' +
        (deviceName() === 'computer' ? 'This device' : 'This ' + deviceName()) +
        ' has no practice saved yet.</p>';
    b +=
      '<p class="note">You can undo a restore from Settings for ' +
      UNDO_DAYS +
      ' days.</p><button class="cta red" data-a="importYes">' +
      (r.status === 'changed' ? 'Restore anyway' : 'Replace and restore') +
      '</button><button class="ghost" data-a="close">Cancel</button>';
    return sheetWrap('Restore this backup?', b);
  }
  b +=
    '<div class="hdr">Inside</div><div class="grp">' +
    [
      ['Sessions', S.sessions],
      ['Song practice', S.songPractice],
      ['Songs', S.songs],
      ['Recordings', S.recordings],
      ['Practice time', hm(S.minutes)],
      ['Practice from', S.first ? shortDate(S.first) + ' – ' + shortDate(S.last) : '–'],
    ]
      .map((x) => '<div class="row"><span class="lbl">' + x[0] + '</span><span class="mut">' + x[1] + '</span></div>')
      .join('') +
    '</div>' +
    '<p class="note" style="margin-top:10px">Nothing has been changed on ' +
    thisDev() +
    '.</p><button class="cta" data-a="bkToImport">Restore from this backup</button><button class="ghost" data-a="close">Done</button>';
  return sheetWrap('Backup check', b);
}
function bkGuideHTML() {
  return sheetWrap(
    'Where backups go',
    '<p class="note">Keep every backup in one folder in iCloud Drive, so it’s safe if you lose your phone or remove the app.</p>' +
      '<div class="grp"><ol class="steps"><li>Tap <b>Export backup</b>, then <b>Save backup</b>.</li><li>In the share sheet, choose <b>Save to Files</b>.</li>' +
      '<li>Go to <b>iCloud Drive</b>. The first time, tap the new-folder button to make a folder called <b>Vocal Sessions</b>, and inside it one called <b>Backups</b>.</li>' +
      '<li>Open Backups and tap <b>Save</b>. Files remembers this folder for next time.</li></ol></div>' +
      '<div class="hdr">File names</div><div class="grp"><div class="row"><span class="lbl fname" style="color:var(--fg)">Vocal Sessions backup · ' +
      ym(new Date()) +
      ' · ' +
      esc(deviceName()) +
      '.json</span></div></div>' +
      '<p class="foot">One file per month for each device. If you back up again in the same month, Files asks whether to replace it. Tap <b>Replace</b> to keep one per month, or <b>Keep Both</b> for an extra copy.</p>' +
      '<div class="hdr">If you find them later</div><p class="note">Each backup starts with a short note in plain English saying what it is and how to restore it. You can also save a read-me file into the Backups folder.</p>' +
      '<button class="cta" data-a="saveReadme">Save a read-me file</button><button class="ghost" data-a="close">Done</button>'
  );
}
function bkLogHTML() {
  const a = loadLog();
  const rows = a
    .map(
      (e) =>
        '<div class="row"><span class="lbl">' +
        when(e.at) +
        '<small class="fname">' +
        esc(e.name || '') +
        '</small><small>' +
        [plural(+e.sessions || 0, 'session'), plural(+e.recordings || 0, 'recording')].join(' · ') +
        (e.verified ? ' · Checked' : '') +
        (e.how === 'downloaded' ? ' · Downloaded' : '') +
        '</small></span><span class="mut">' +
        mb(+e.size || 0) +
        '</span></div>'
    )
    .join('');
  return sheetWrap(
    'Backup history',
    (a.length
      ? '<div class="grp">' + rows + '</div>'
      : '<p class="note">No backups made on ' + thisDev() + ' yet.</p>') +
      '<p class="foot">This list is kept on ' +
      thisDev() +
      '. The files are wherever you saved them, ideally iCloud Drive › Vocal Sessions › Backups.</p><button class="ghost" data-a="close">Done</button>'
  );
}
function undoHTML() {
  const u = UNDO;
  if (!u) return '';
  const n = sinceRestore(u),
    until = new Date(u.at + UNDO_DAYS * 864e5);
  return sheetWrap(
    'Undo last restore?',
    '<p class="note">This puts back everything as it was before you restored a backup on ' +
      when(u.at) +
      '.</p>' +
      (n
        ? '<div class="bkstat warn">' +
          ICON.warn +
          '<div><b>' +
          plural(n, 'session') +
          ' since then</b>Anything you’ve logged since the restore will be removed. Back up first if you want to keep it.</div></div><button class="ghost" data-a="exportPrep">Back up first</button>'
        : '') +
      '<p class="note">The backup file stays in Files, so you can restore it again. Undo is available until ' +
      fileDate(until) +
      '.</p><button class="cta red" data-a="undoYes">Undo restore</button><button class="ghost" data-a="close">Cancel</button>'
  );
}

/* ===== Copy ===== */
function copyText(txt) {
  const ok = () => toast('Copied for Toggl');
  const fallback = () => {
    const ta = document.createElement('textarea');
    ta.value = txt;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, txt.length);
    let s = false;
    try {
      s = document.execCommand('copy');
    } catch (e) {}
    ta.remove();
    s ? ok() : toast('Copy failed. Try again.');
  };
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(ok, fallback);
  else fallback();
}
