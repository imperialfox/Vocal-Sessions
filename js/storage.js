/* Vocal Sessions · storage.js
   Saved data: loading, checking and saving it, data-version upgrades, and recordings in IndexedDB.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Storage ===== */
const KEY = 'vocalTracker',
  DRAFT = 'vocalDraft';
function load() {
  try {
    return cleanData(JSON.parse(localStorage.getItem(KEY) || '{}')) || {};
  } catch (e) {
    return {};
  }
}
// keep only well-formed data, so a damaged file or storage can't break the app
function cleanData(d) {
  if (!d || typeof d !== 'object' || Array.isArray(d)) return null;
  const arr = (x) => (Array.isArray(x) ? x : []),
    obj = (x) => (x && typeof x === 'object' && !Array.isArray(x) ? x : {});
  const okS = (x) =>
    x &&
    typeof x === 'object' &&
    typeof x.id === 'string' &&
    !isNaN(new Date(x.date)) &&
    +x.mins > 0 &&
    isFinite(+x.mins);
  const fixS = (x) =>
    Object.assign(x, {
      mins: Math.round(+x.mins),
      f: obj(x.f),
      rot: obj(x.rot),
      xn: obj(x.xn),
      rate: obj(x.rate),
      takes: arr(x.takes),
      how: arr(x.how).filter((w) => typeof w === 'string'),
      howNote: typeof x.howNote === 'string' ? x.howNote : '',
    });
  const out = Object.assign({}, d, {
    sessions: arr(d.sessions).filter(okS).map(fixS),
    songSessions: arr(d.songSessions).filter(okS).map(fixS),
    songs: arr(d.songs).map(cleanSong).filter(Boolean), // each song checked on its own (songs.js)
    custom: arr(d.custom).filter((x) => x && x.id && typeof x.name === 'string'),
    months: obj(d.months),
    ex: obj(d.ex),
    words: obj(d.words),
    prefs: obj(d.prefs), // settings that travel with backups (3.10.1: Recall's peek length)
  });
  if (out.prefs.peek != null && ![1, 2, 3, 5].includes(+out.prefs.peek)) delete out.prefs.peek;
  for (const k in out.months)
    if (!(+out.months[k] >= 0) || !isFinite(+out.months[k])) delete out.months[k];
    else out.months[k] = +out.months[k];
  for (const k in out.ex) {
    const e = out.ex[k];
    if (!e || typeof e !== 'object') {
      delete out.ex[k];
      continue;
    }
    e.n = Math.max(0, Math.round(+e.n) || 0);
    if (e.last && isNaN(new Date(e.last))) e.last = null;
  }
  for (const k in out.words) if (!Array.isArray(out.words[k])) delete out.words[k];
  return out;
}
function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(D));
  } catch (e) {
    toast('Couldn’t save. Storage may be full.');
  }
}
function loadDraft() {
  try {
    const o = JSON.parse(localStorage.getItem(DRAFT) || 'null');
    return o && typeof o === 'object' && +o.start > 0 ? o : null;
  } catch (e) {
    return null;
  }
}
function saveDraft() {
  try {
    X && X.start ? localStorage.setItem(DRAFT, JSON.stringify(X)) : localStorage.removeItem(DRAFT);
  } catch (e) {}
}
/* Data version. When the shape of saved data has to change, add a numbered step to UPGRADES and raise SCHEMA.
   Steps may only add things, so older backups and the previous version of the app keep working. */
const SCHEMA = 4,
  PRE_UPGRADE = 'vocalBeforeUpgrade';
const UPGRADES = {
  1: (d) => {}, // 3.7: saved data gets a version number. Nothing else changes.
  // 3.8: songs can have lyrics, an artist and a pin. Songs already here keep their name and recordings, and get
  // an artist (none), a pin (off) and the date they were added (their first song practice, or now).
  2: (d) => {
    (d.songs || []).forEach((s) => {
      if (typeof s.artist !== 'string') s.artist = '';
      if (typeof s.pinned !== 'boolean') s.pinned = false;
      if (!(s.added > 0)) {
        const t = (d.songSessions || [])
          .filter((x) => x.songId === s.id)
          .map((x) => +new Date(x.date))
          .filter(isFinite);
        s.added = t.length ? Math.min.apply(null, t) : Date.now();
      }
    });
  },
  // 3.18: songs can carry timing (Song Clock), checked by cleanSong(). Songs from before have none, which means
  // not synced, so nothing changes in them.
  3: (d) => {},
  // 3.27 (Q03): marks come in layers. Each section's older Annotate marks (`ann`, `orphans`) are moved across into
  // `marks` and `held` by cleanSection() as the data loads (marks.js); this step makes sure every song has been, and
  // the older shape is kept beside them, so nothing is lost and a backup still opens in 3.26.
  4: (d) => {
    (d.songs || []).forEach((s) => {
      for (const k in s.sections || {}) {
        const c = s.sections[k];
        if (c && Array.isArray(c.lines) && !Array.isArray(c.marks)) MARKS.fromAnn(c);
      }
    });
  },
};
function upgradeData() {
  const from = +D.schema || 0;
  if (from >= SCHEMA) return;
  // keep the data as it was, for 30 days, in case an upgrade ever goes wrong
  if ((D.sessions || []).length || (D.songSessions || []).length) {
    try {
      localStorage.setItem(PRE_UPGRADE, JSON.stringify({ from, to: SCHEMA, at: Date.now(), data: D }));
    } catch (e) {}
  }
  for (let n = from + 1; n <= SCHEMA; n++) {
    UPGRADES[n](D);
    D.schema = n;
  }
}
function tidyPreUpgrade() {
  try {
    const o = JSON.parse(localStorage.getItem(PRE_UPGRADE) || 'null');
    if (o && !(Date.now() - o.at < 30 * 864e5)) localStorage.removeItem(PRE_UPGRADE);
  } catch (e) {}
}
let D = {}; // filled in by boot.js
function migrate() {
  if (!D.v2) {
    D.ex = D.ex || {};
    const custom = (D.customRotations || []).map((c, i) => ({
      id: 'c' + i + '_' + Date.now().toString(36),
      name: c.name,
      focus: c.focus || 'custom',
    }));
    const hist = D.rotationHistory || {};
    Object.keys(hist).forEach((k) => {
      const i = +k;
      const id = i < 8 ? OLD_ROT_IDS[i] : (custom[i - 8] || {}).id;
      if (id) D.ex[id] = { n: hist[k] || 0, last: null };
    });
    D.custom = custom;
    D.v2 = true;
  }
  D.ex = D.ex || {};
  D.custom = D.custom || [];
  D.songs = D.songs || [];
  D.sessions = D.sessions || [];
  D.months = D.months || {};
  D.songSessions = D.songSessions || [];
  D.words = D.words || {};
  D.prefs = D.prefs && typeof D.prefs === 'object' && !Array.isArray(D.prefs) ? D.prefs : {};
  upgradeData();
}
let X = null; // filled in by boot.js
// bring older drafts up to date (3.2 adds Skip, per-exercise notes, how it went, pause and song practice)
function normX() {
  if (!X) return;
  X.kind = X.kind || 'focused';
  X.f = X.f || {};
  X.rot = X.rot || {};
  X.xn = X.xn || {};
  X.rate = X.rate || {};
  X.takes = X.takes || [];
  X.how = X.how || [];
  X.howNote = X.howNote || '';
  X.pausedTotal = X.pausedTotal || 0;
  if (X.fEnd && X.fE == null) X.fE = (X.fEnd - X.start) / 1000;
  if (X.rEnd && X.rE == null) X.rE = (X.rEnd - X.start) / 1000;
}

/* ===== Recordings (IndexedDB) ===== */
let dbp = null;
function db() {
  if (dbp) return dbp;
  dbp = new Promise((res, rej) => {
    if (!window.indexedDB) return rej(new Error('no idb'));
    const r = indexedDB.open('vocalTakes', 2);
    r.onupgradeneeded = () => {
      const d = r.result;
      if (!d.objectStoreNames.contains('takes')) d.createObjectStore('takes', { keyPath: 'id' });
      if (!d.objectStoreNames.contains('undo')) d.createObjectStore('undo', { keyPath: 'id' });
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
async function tx(mode, fn, store) {
  store = store || 'takes';
  const d = await db();
  return new Promise((res, rej) => {
    const t = d.transaction(store, mode);
    const out = fn(t.objectStore(store));
    t.oncomplete = () => res(out && out.result !== undefined ? out.result : undefined);
    t.onerror = () => rej(t.error);
  });
}
const allTakes = () =>
  tx('readonly', (s) => s.getAll())
    .then((r) => r || [])
    .catch(() => []);
const putTake = (t) => tx('readwrite', (s) => s.put(t));
const delTake = (id) => tx('readwrite', (s) => s.delete(id));
const clearTakes = () => tx('readwrite', (s) => s.clear()).catch(() => {});
// the copy of your data kept for 30 days after a restore, so it can be undone
const getUndo = () =>
  tx('readonly', (s) => s.get('last'), 'undo')
    .then((r) => r || null)
    .catch(() => null);
const putUndo = (o) => tx('readwrite', (s) => s.put(o), 'undo');
const clearUndo = () => tx('readwrite', (s) => s.clear(), 'undo').catch(() => {});
const UNDO_DAYS = 30;
let UNDO = null;
async function refreshUndo() {
  const u = await getUndo();
  if (u && !(Date.now() - u.at < UNDO_DAYS * 864e5)) {
    await clearUndo();
    UNDO = null;
    return;
  }
  UNDO = u;
}
// ask the browser not to clear the app's data when the device is low on space
let PERSIST = null; // true, false, or 'na' when the browser doesn't offer it
async function checkPersist(ask) {
  const st = navigator.storage;
  if (!st || !st.persisted) {
    PERSIST = 'na';
    return PERSIST;
  }
  try {
    let p = await st.persisted();
    if (!p && ask && st.persist) p = await st.persist();
    PERSIST = !!p;
  } catch (e) {
    PERSIST = 'na';
  }
  return PERSIST;
}
const persistVal = () =>
  PERSIST === true ? 'On' : PERSIST === false ? 'Off' : PERSIST === 'na' ? 'Not available' : '…';
let TAKES = [];
async function refreshTakes() {
  TAKES = (await allTakes()).sort((a, b) => a.created - b.created);
}
