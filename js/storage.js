/* Vocal Sessions · storage.js
   Saved data: loading, checking and saving it, data-version upgrades, and recordings in IndexedDB.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Storage ===== */
const KEY = 'vocalTracker',
  DRAFT = 'vocalDraft';
/* Q11: saved data that can't be read is never saved over. Its text is copied to the device's safety copies
   (SAFE, below) first, and saving waits until that's done. A song that can't be checked is dropped on its own, and
   the data as it was is copied the same way. */
let CLEAN_DROPPED = 0; // songs cleanData() had to drop because checking them failed (counted, not thrown)
function load() {
  let raw = null;
  try {
    raw = localStorage.getItem(KEY);
  } catch (e) {
    // storage itself can't be read: leave it alone rather than save an empty app over it
    if (!SAVE_LOCK)
      afterLaunch(() =>
        toast('Your saved data couldn’t be opened. It’s been left as it was, and changes won’t be saved this time.', 9000, 'long')
      );
    lockSaves('unreadable');
    return {};
  }
  if (raw == null || raw === '' || raw === 'null') return {};
  let d, out = null;
  try {
    d = JSON.parse(raw);
  } catch (e) {}
  CLEAN_DROPPED = 0;
  try {
    out = d === undefined ? null : cleanData(d);
  } catch (e) {
    out = null;
  }
  if (!out) {
    rescueRaw(raw, 'unreadable');
    return {};
  }
  if (CLEAN_DROPPED) rescueRaw(raw, 'song');
  return out;
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
    // each song checked on its own (songs.js); one that makes the checks fail is dropped alone, not everything (Q11)
    songs: arr(d.songs)
      .map((sg) => {
        try {
          return cleanSong(sg);
        } catch (e) {
          CLEAN_DROPPED++;
          return null;
        }
      })
      .filter(Boolean),
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
/* Saving waits while a safety copy is being made (holdSaves), so the copy is always taken before anything is saved
   over what it copies. A lock (lockSaves) stops saving altogether for this launch: the stored data is left exactly as
   it was when it couldn't be read and couldn't be copied, or when opening it went wrong. */
let saveHolds = 0,
  saveLater = false,
  SAVE_LOCK = null; // null, or why saving is off for this launch
function holdSaves(p) {
  saveHolds++;
  return Promise.resolve(p)
    .catch(() => {})
    .then(() => {
      saveHolds = Math.max(0, saveHolds - 1);
      if (!saveHolds && saveLater) {
        saveLater = false;
        save();
      }
    });
}
function lockSaves(why) {
  SAVE_LOCK = SAVE_LOCK || why || 'locked';
}
function save() {
  if (SAVE_LOCK) return;
  if (saveHolds) {
    saveLater = true;
    return;
  }
  try {
    localStorage.setItem(KEY, JSON.stringify(D));
  } catch (e) {
    toast('Couldn’t save. Storage may be full.');
  }
}
// a message for when the launch screen has gone (it would be hidden behind it before then)
function afterLaunch(fn) {
  const ready = () =>
    !document.getElementById('splash') && !(typeof LAUNCH !== 'undefined' && LAUNCH.busy && LAUNCH.busy());
  if (ready()) return fn();
  let n = 0;
  const t = setInterval(() => {
    if (ready() || ++n > 50) {
      clearInterval(t);
      fn();
    }
  }, 150);
}
// copy saved data that couldn't be read (or lost a song) to the safety copies, then tell Ivan once
let rescuing = null;
function rescueRaw(raw, why) {
  if (rescuing === raw) return; // already copied this launch (pull to refresh reads the data again)
  rescuing = raw;
  holdSaves(
    SAFE.rescue(raw, why).then(
      () =>
        afterLaunch(() =>
          toast(
            why === 'song'
              ? 'A song couldn’t be read. A copy of your data as it was is in Settings › Backup.'
              : 'Your saved data couldn’t be read. A copy is safe in Settings › Backup.',
            8000,
            'long'
          )
        ),
      () => {
        // nowhere to copy it: leave it exactly where it is and save nothing over it this time
        lockSaves('uncopied');
        afterLaunch(() =>
          toast(
            'Your saved data couldn’t be read, so it’s been left as it was. Changes won’t be saved this time.',
            9000,
            'long'
          )
        );
      }
    )
  );
}
function loadDraft() {
  try {
    const o = JSON.parse(localStorage.getItem(DRAFT) || 'null');
    return o && typeof o === 'object' && +o.start > 0 ? o : null;
  } catch (e) {
    return null;
  }
}
let draftWarned = 0;
function saveDraft() {
  try {
    X && X.start ? localStorage.setItem(DRAFT, JSON.stringify(X)) : localStorage.removeItem(DRAFT);
  } catch (e) {
    // Q11: say so, as save() does (at most every 10 seconds, since drafts save often)
    if (Date.now() - draftWarned > 10000) {
      draftWarned = Date.now();
      toast('Couldn’t save your practice so far. Storage may be full.', 4000, 'long');
    }
  }
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
  // keep the data as it was, for 30 days, in case an upgrade ever goes wrong. Since Q11 it's kept in the safety
  // copies (IndexedDB), not beside the data in localStorage, and saving waits until it's there
  if ((D.sessions || []).length || (D.songSessions || []).length) {
    let copy = null;
    try {
      copy = JSON.parse(JSON.stringify(D));
    } catch (e) {}
    if (copy) holdSaves(SAFE.put(PRE_UPGRADE, { from, to: SCHEMA, at: Date.now(), data: copy }));
  }
  for (let n = from + 1; n <= SCHEMA; n++) {
    UPGRADES[n](D);
    D.schema = n;
  }
}
// at launch: the copy goes after 30 days, and one left in localStorage by 3.28 or earlier moves to IndexedDB (SAFE)
const tidyPreUpgrade = () => SAFE.load();
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

/* ===== IndexedDB: one shared helper (Q11) =====
   Every database goes through IDB: recordings (vocalTakes), the coach video (vocalCoach), song tracks (vocalTracks),
   takes' waveforms (vocalTakeExtras) and the safety copies (vocalSafety). A transaction settles on complete, error or
   abort, so a save can't hang without a word when storage is full. Opening waits out a blocked upgrade for a few
   seconds, then gives up. After a failure the connection is dropped and the next call opens a fresh one; a
   connection the browser has closed (iOS can) is reopened once. Names, versions and stores never change here:
   IDB.define() only creates a store when it's missing. */
const IDB = (() => {
  const BLOCKED_MS = 4000;
  function define(name, version, stores) {
    let conn = null, // a promise of the open database
      db = null;
    function drop(d) {
      if (d && db !== d) return;
      conn = null;
      db = null;
      if (d)
        try {
          d.close();
        } catch (e) {}
    }
    function open() {
      if (conn) return conn;
      const p = new Promise((res, rej) => {
        if (!window.indexedDB) return rej(new Error('IndexedDB isn’t available'));
        let done = false,
          bt = null,
          r;
        const fail = (e) => {
          if (done) return;
          done = true;
          clearTimeout(bt);
          if (conn === p) conn = null;
          rej(e);
        };
        try {
          r = indexedDB.open(name, version);
        } catch (e) {
          return fail(e);
        }
        r.onupgradeneeded = () => {
          const d = r.result;
          for (const s in stores) if (!d.objectStoreNames.contains(s)) d.createObjectStore(s, stores[s] || undefined);
        };
        r.onsuccess = () => {
          const d = r.result;
          if (done) return d.close(); // gave up waiting while it was blocked
          done = true;
          clearTimeout(bt);
          db = d;
          d.onversionchange = () => drop(d);
          d.onclose = () => drop(d);
          res(d);
        };
        r.onerror = () => fail(r.error || new Error('Couldn’t open ' + name));
        // another copy of the app holds an older version open: wait a little, then give up
        r.onblocked = () => {
          if (!bt) bt = setTimeout(() => fail(new Error(name + ' is blocked')), BLOCKED_MS);
        };
      });
      conn = p;
      return p;
    }
    // a transaction on a working connection; a connection that has gone is reopened once
    async function begin(list, mode) {
      for (let i = 0; ; i++) {
        const d = await open();
        try {
          return { d, t: d.transaction(list, mode) };
        } catch (e) {
          drop(d);
          if (i) throw e;
        }
      }
    }
    // fn gets the stores in the order named and may return a request; its result is what the promise gives
    async function tx(stores, mode, fn) {
      const list = [].concat(stores);
      const { d, t } = await begin(list, mode);
      return new Promise((res, rej) => {
        let out,
          settled = false;
        const fail = (e) => {
          if (settled) return;
          settled = true;
          drop(d);
          rej(e || new Error('The save didn’t finish'));
        };
        t.oncomplete = () => {
          if (settled) return;
          settled = true;
          res(out && out.result !== undefined ? out.result : undefined);
        };
        t.onerror = () => fail(t.error);
        t.onabort = () => fail(t.error || new Error('The save was stopped'));
        try {
          out = fn(...list.map((s) => t.objectStore(s)));
        } catch (e) {
          try {
            t.abort();
          } catch (x) {}
          fail(e);
        }
      });
    }
    // every entry in a store, as (key, value); resolves true when read, false if it couldn't be (never rejects)
    async function each(store, fn) {
      let b;
      try {
        b = await begin([store], 'readonly');
      } catch (e) {
        return false;
      }
      return new Promise((res) => {
        const { d, t } = b;
        const c = t.objectStore(store).openCursor();
        c.onsuccess = () => {
          const k = c.result;
          if (!k) return;
          try {
            fn(k.key, k.value);
          } catch (e) {}
          k.continue();
        };
        t.oncomplete = () => res(true);
        t.onerror = t.onabort = () => {
          drop(d);
          res(false);
        };
      });
    }
    // close it (tests, and deleting a database)
    async function close() {
      const p = conn;
      conn = null;
      db = null;
      if (p)
        try {
          (await p).close();
        } catch (e) {}
    }
    return { name, open, tx, each, close };
  }
  return { define };
})();

/* ===== Safety copies (Q11, IndexedDB vocalSafety) =====
   Kept on this device only, never in backups. Store `copies`, keyed by name:
   - `vocalBeforeUpgrade`: {from, to, at, data}, the data as it was before the last data upgrade, kept for 30 days
   - `rescued:<ms>`: {at, why, text, bytes, appVersion}, saved data that couldn't be read ('unreadable'), or that had a
     song that couldn't be ('song'), exactly as it was stored. Kept until deleted in Settings › Backup. */
const SAFE_DB = IDB.define('vocalSafety', 1, { copies: null });
const SAFE = (() => {
  const meta = new Map(); // key -> {at, bytes, why?}; rescued copies keep their text too, so Save can share it at once
  const sizeOf = (key, rec) => (rec && rec.text ? rec.text.length : +rec.bytes || 0);
  const note = (key, rec) => meta.set(key, Object.assign({ key, at: +rec.at || 0, bytes: sizeOf(key, rec) }, rec));
  async function put(key, rec) {
    if (key === PRE_UPGRADE && !rec.bytes)
      try {
        rec.bytes = JSON.stringify(rec.data).length;
      } catch (e) {}
    await SAFE_DB.tx('copies', 'readwrite', (s) => s.put(rec, key));
    note(key, rec);
  }
  const get = (key) => SAFE_DB.tx('copies', 'readonly', (s) => s.get(key)).catch(() => null);
  async function del(key) {
    await SAFE_DB.tx('copies', 'readwrite', (s) => s.delete(key));
    meta.delete(key);
  }
  function rescue(text, why) {
    const at = Date.now();
    return put('rescued:' + at, {
      at,
      why,
      text,
      bytes: text.length,
      appVersion: typeof APP_VERSION !== 'undefined' ? APP_VERSION : '',
    });
  }
  // at launch: what's kept, the 30-day limit, and moving 3.28's localStorage copy across (once, then it's cleared)
  async function load() {
    await SAFE_DB.each('copies', (k, v) => {
      if (typeof k === 'string' && v && typeof v === 'object') note(k, v);
    });
    const pre = meta.get(PRE_UPGRADE);
    if (pre && !(Date.now() - pre.at < 30 * 864e5)) await del(PRE_UPGRADE).catch(() => {});
    let old = null;
    try {
      old = JSON.parse(localStorage.getItem(PRE_UPGRADE) || 'null');
    } catch (e) {}
    if (old === null) return;
    const clear = () => {
      try {
        localStorage.removeItem(PRE_UPGRADE);
      } catch (e) {}
    };
    if (!old || typeof old !== 'object' || !(Date.now() - old.at < 30 * 864e5)) return clear();
    const now = meta.get(PRE_UPGRADE);
    if (now && now.at >= old.at) return clear(); // a newer copy is already kept
    try {
      await put(PRE_UPGRADE, old);
      clear(); // only once it's safely in IndexedDB
    } catch (e) {}
  }
  const rescued = () => [...meta.values()].filter((m) => m.key.startsWith('rescued:')).sort((a, b) => b.at - a.at);
  const bytes = () => [...meta.values()].reduce((a, m) => a + (m.bytes || 0), 0);
  return { put, get, del, rescue, load, rescued, bytes };
})();

/* ===== Recordings (IndexedDB vocalTakes) ===== */
const TAKES_DB = IDB.define('vocalTakes', 2, { takes: { keyPath: 'id' }, undo: { keyPath: 'id' } });
const db = () => TAKES_DB.open();
const tx = (mode, fn, store) => TAKES_DB.tx(store || 'takes', mode, fn);
// null when the recordings couldn't be read (not the same as having none)
const allTakes = () =>
  tx('readonly', (s) => s.getAll())
    .then((r) => r || [])
    .catch(() => null);
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
let TAKES_READ = false; // the recordings were read at least once (so a take missing from TAKES really has gone)
async function refreshTakes() {
  const all = await allTakes();
  if (!all) return; // couldn't read them this time: keep the list as it was rather than show none
  TAKES = all.sort((a, b) => a.created - b.created);
  TAKES_READ = true;
}
