/* Vocal Sessions · settings.js (3.21)
   Settings as a main list of icon rows, each opening its own page, like the iPhone's Settings app.
   - Main list: Backup and Storage; Recall, Coach video, Marks guide (Q04, guide.js), Appearance and Accessibility; Changelog and View on GitHub; the two resets;
     then the app's icon, name and version at the bottom.
   - Pages are U.view = 'set' with U.setPg = 'backup' | 'storage' | 'recall' | 'coach' | 'appear' | 'access'. Backup
     and Storage open with a hero card (big icon, title and a short explanation); the others are plain pages.
   - Every row pushes its page in from the right (data-zk="set:<page>" with data-push, 3.23) and Back slides it away.
   - Appearance (3.23, Q08) holds this device's look: Gradient background, the soft moving wash behind Today's header
     (on unless switched off; localStorage 'vocalLook', never in a backup), and (Q36) Show screen IDs. Later look options join that page.
   - Accessibility holds this device's motion settings: Reduce motion (Match iPhone, On or Off, kept in localStorage
     'vocalReduce') and Slow motion (MOTION speed 4), and (Q33) Reduce transparency ('vocalTransp'). None is ever in a
     backup.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const SET = (() => {
  // the icon tiles: iOS-style colours, a white glyph of our own on each
  const G = {
    backup:
      '<svg viewBox="0 0 24 24"><path d="M19.6 13.4A7.8 7.8 0 1 1 17.3 6.3"/><path d="M19.4 3.6v4.3h-4.3"/><path d="M9.4 10.6v2.8M12 9.2v5.6M14.6 10.6v2.8"/></svg>',
    storage:
      '<svg viewBox="0 0 24 24"><path d="M12 3.8l8.2 4.1L12 12 3.8 7.9z"/><path d="M3.8 12.1L12 16.2l8.2-4.1"/><path d="M3.8 16.2L12 20.3l8.2-4.1"/></svg>',
    recall:
      '<svg viewBox="0 0 24 24"><path d="M2.6 12s3.5-6.4 9.4-6.4 9.4 6.4 9.4 6.4-3.5 6.4-9.4 6.4S2.6 12 2.6 12z"/><circle cx="12" cy="12" r="2.8"/></svg>',
    coach:
      '<svg viewBox="0 0 24 24"><rect x="3" y="5.5" width="18" height="13" rx="3.2"/><path d="M10.4 9.4v5.2l4.3-2.6z"/></svg>',
    // 3.23 Appearance: a soft wash with a sparkle, for the gradient behind Today's header
    appear:
      '<svg viewBox="0 0 24 24"><path d="M3.6 15.4c2.6-1.9 5.2-1.9 7.8 0s5.2 1.9 7.8 0"/><path d="M3.6 19.6c2.6-1.9 5.2-1.9 7.8 0s5.2 1.9 7.8 0"/><path d="M15.8 3.4l.9 2.1 2.1.9-2.1.9-.9 2.1-.9-2.1-2.1-.9 2.1-.9z"/><path d="M7 6.2v3.2M5.4 7.8h3.2"/></svg>',
    access:
      '<svg viewBox="0 0 24 24"><circle cx="14" cy="4.9" r="1.9"/><path d="M9.3 9.4h9.4M14 9.4v4.4l-2.6 5.6M14 13.8l2.6 5.6"/><path d="M3.4 11.2h3.2M2.6 14.8h3"/></svg>',
    log: '<svg viewBox="0 0 24 24"><path d="M10 7h10M10 12h10M10 17h7"/><path d="M5 4.6l.7 1.5 1.5.7-1.5.7L5 9l-.7-1.5-1.5-.7 1.5-.7z"/><path d="M5 15.6v2.8M3.6 17h2.8"/></svg>',
    // Q04 the Marks guide: an open book
    guide:
      '<svg viewBox="0 0 24 24"><path d="M12 6.6c-2.1-1.6-4.9-2.2-8.2-1.8v12.9c3.3-.4 6.1.2 8.2 1.8 2.1-1.6 4.9-2.2 8.2-1.8V4.8c-3.3-.4-6.1.2-8.2 1.8z"/><path d="M12 6.6v12.9"/></svg>',
    // Q32 Your voice: a microphone with its range; Pattern player: piano keys
    voice:
      '<svg viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.6 11.4a6.4 6.4 0 0 0 12.8 0M12 17.8V21M8.6 21h6.8"/></svg>',
    player:
      '<svg viewBox="0 0 24 24"><rect x="3.4" y="4.6" width="17.2" height="14.8" rx="2.6"/><path d="M8.2 4.6v14.8M12 4.6v14.8M15.8 4.6v14.8"/><path d="M8.2 4.6v8.6M15.8 4.6v8.6" stroke-width="3.2"/></svg>',
    code: '<svg viewBox="0 0 24 24"><circle cx="7" cy="5.6" r="2"/><circle cx="7" cy="18.4" r="2"/><circle cx="17" cy="8.6" r="2"/><path d="M7 7.6v8.8M17 10.6c0 3.8-10 1.6-10 5.8"/></svg>',
  };
  const COL = {
    backup: '#2ea596',
    storage: 'var(--sys-gray)',
    recall: 'var(--sys-indigo)',
    coach: 'var(--sys-orange)',
    appear: '#ff6b57',
    access: 'var(--sys-blue)',
    log: 'var(--sys-purple)',
    guide: 'var(--sys-pink)',
    voice: 'var(--sys-teal)',
    player: 'var(--sys-indigo)',
    code: 'var(--tile-ink)',
  };
  const TITLE = {
    backup: 'Backup',
    storage: 'Storage',
    recall: 'Recall',
    coach: 'Coach video',
    voice: 'Your voice',
    player: 'Pattern player',
    appear: 'Appearance',
    access: 'Accessibility',
  };
  const PAGES = Object.keys(TITLE);
  const ico = (k, big) =>
    '<span class="tile' +
    (big ? ' big' : '') +
    '" style="background:' +
    COL[k] +
    '" aria-hidden="true">' +
    G[k] +
    '</span>';
  const out = '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 16L16 8M9.5 8H16v6.5"/></svg>';

  /* ----- this device's motion settings ----- */
  const RKEY = 'vocalReduce';
  function reduceMode() {
    try {
      const m = localStorage.getItem(RKEY);
      return m === 'on' || m === 'off' ? m : 'system';
    } catch (e) {
      return 'system';
    }
  }
  function setReduce(m) {
    try {
      if (m === 'on' || m === 'off') localStorage.setItem(RKEY, m);
      else localStorage.removeItem(RKEY);
    } catch (e) {}
    Parts.motion.setReduced(m === 'on' ? true : m === 'off' ? false : null); // Q41 the kit runs the motion (D18)
  }
  const slow = () => MOTION.speed() === 4;

  /* ----- Q33 Reduce transparency: the glass tint more solid (alpha × 0.5 + 0.4, between 0.4 and 0.8), the blur kept.
     localStorage 'vocalTransp' ('on'), this device only, never in backups. Safari can't report the iPhone's own setting,
     so this switch is how it's turned on there; a browser that does report it is followed too. <html> gets
     .glass-solid, which app.css follows ----- */
  const TKEY = 'vocalTransp';
  const tmq = window.matchMedia ? matchMedia('(prefers-reduced-transparency: reduce)') : null;
  function transpSet() {
    try {
      return localStorage.getItem(TKEY) === 'on';
    } catch (e) {
      return false;
    }
  }
  const transpOn = () => transpSet() || !!(tmq && tmq.matches);
  const transpPublish = () => document.documentElement.classList.toggle('glass-solid', transpOn());
  function setTransp(on) {
    try {
      if (on) localStorage.setItem(TKEY, 'on');
      else localStorage.removeItem(TKEY);
    } catch (e) {}
    transpPublish();
  }
  transpPublish();
  if (tmq && tmq.addEventListener) tmq.addEventListener('change', transpPublish);

  /* ----- this device's look (3.23, Q08): localStorage 'vocalLook', an object so later options can join it ----- */
  const LKEY = 'vocalLook';
  function look() {
    try {
      const o = JSON.parse(localStorage.getItem(LKEY) || '{}');
      return o && typeof o === 'object' && !Array.isArray(o) ? o : {};
    } catch (e) {
      return {};
    }
  }
  const gradOn = () => look().grad !== false; // on unless switched off
  function setGrad(on) {
    const o = look();
    if (on) delete o.grad;
    else o.grad = false;
    try {
      if (Object.keys(o).length) localStorage.setItem(LKEY, JSON.stringify(o));
      else localStorage.removeItem(LKEY);
    } catch (e) {}
  }
  // Q36 Show screen IDs: {ids: true} when on (off unless switched on)
  const idsOn = () => look().ids === true;
  function setIds(on) {
    const o = look();
    if (on) o.ids = true;
    else delete o.ids;
    try {
      if (Object.keys(o).length) localStorage.setItem(LKEY, JSON.stringify(o));
      else localStorage.removeItem(LKEY);
    } catch (e) {}
  }
  // the wash behind Today's header: three soft blobs drifting very slowly, and a faint grain. It scrolls with the
  // page; Reduce motion (and motion off) holds the blobs still
  const wash = () =>
    gradOn()
      ? '<div class="tgrad" aria-hidden="true"><i class="tg1"></i><i class="tg2"></i><i class="tg3"></i></div>'
      : '';
  const REDUCE = [
    ['system', () => 'Match ' + deviceName()],
    ['on', () => 'On'],
    ['off', () => 'Off'],
  ];

  /* ----- what the main list shows on the right ----- */
  function backupVal() {
    const lb = D.lastBackup;
    if (!lb) return { t: 'Never', warn: true };
    const r = relDay(lb);
    return { t: r.charAt(0).toUpperCase() + r.slice(1), warn: (Date.now() - new Date(lb)) / 864e5 > 14 };
  }
  // bytes on this device, by kind (app data is the saved JSON, which is what a restore brings back)
  function sizes() {
    let app = 0;
    try {
      app = (localStorage.getItem('vocalTracker') || '').length + (localStorage.getItem('vocalDraft') || '').length;
    } catch (e) {}
    app += SAFE.bytes(); // Q11: the safety copies (before an upgrade, and any rescued data) are your data too
    const cm = COACH.meta();
    return [
      { k: 'rec', l: 'Recordings', b: TAKES.reduce((a, t) => a + (+t.size || 0), 0), c: 'var(--cF)' },
      { k: 'trk', l: 'Song tracks', b: TRACK.bytes(), c: 'var(--cR)' },
      { k: 'cv', l: 'Coach video', b: cm ? +cm.size || 0 : 0, c: 'var(--cA)' },
      { k: 'app', l: 'Sessions and songs', b: app, c: 'var(--done)' },
    ];
  }
  const total = () => sizes().reduce((a, s) => a + s.b, 0);
  const mb = (b) => {
    const m = b / 1048576;
    return (m >= 100 ? Math.round(m) : m >= 10 ? m.toFixed(0) : m >= 0.1 ? m.toFixed(1) : m > 0 ? '0.1' : '0') + ' MB';
  };
  function vals() {
    const b = backupVal();
    return {
      backup: b,
      storage: { t: mb(total()) },
      recall: { t: peekSecs() + ' s' },
      coach: { t: COACH.busy() ? 'Adding…' : COACH.has() ? 'Added' : 'Not added' },
      voice: { t: PAT.vals().voice },
      player: { t: PAT.vals().player },
      appear: { t: '' },
      access: { t: { system: 'System', on: 'On', off: 'Off' }[reduceMode()] },
    };
  }

  /* ----- the main list ----- */
  function row(k, v) {
    return (
      '<button class="row" data-a="setPg" data-v="' +
      k +
      '" data-zk="set:' +
      k +
      '" data-push>' +
      ico(k) +
      '<span class="lbl">' +
      TITLE[k] +
      '</span><span class="mut' +
      (v.warn ? ' setwarn' : '') +
      '">' +
      esc(v.t) +
      '</span>' +
      chev +
      '</button>'
    );
  }
  function main() {
    const v = vals();
    return (
      '<h1>Settings</h1>' +
      '<div class="grp tiled">' +
      row('backup', v.backup) +
      row('storage', v.storage) +
      '</div>' +
      '<div class="grp tiled setgap">' +
      row('recall', v.recall) +
      row('coach', v.coach) +
      // Q04: the Marks guide's door (no value; its pages are the guide's own, so Back returns here)
      '<button class="row" data-a="gdOpen" data-v="home" data-zk="mk:guide" data-push>' +
      ico('guide') +
      '<span class="lbl">Marks guide</span>' +
      chev +
      '</button>' +
      row('voice', v.voice) + // Q32: your voice range and the pattern player's sound (patterns.js)
      row('player', v.player) +
      row('appear', v.appear) +
      row('access', v.access) +
      '</div>' +
      '<div class="grp tiled setgap">' +
      '<button class="row" data-zk="log" data-push data-a="openLog">' +
      ico('log') +
      '<span class="lbl">Changelog</span><span class="mut">' +
      APP_VERSION +
      '</span>' +
      chev +
      '</button>' +
      '<a class="row" href="' +
      REPO +
      '" target="_blank" rel="noopener">' +
      ico('code') +
      '<span class="lbl">View on GitHub</span><span class="mut">' +
      out +
      '</span></a></div>' +
      '<div class="grp setgap">' +
      '<button class="row" data-a="sheet" data-v="resetMonth"><span class="lbl dng">Reset this month’s minutes</span></button>' +
      '<button class="row" data-a="sheet" data-v="resetAll"><span class="lbl dng">Reset all data</span></button></div>' +
      '<button class="setfoot" data-zk="log" data-push data-a="openLog" aria-label="Vocal Sessions ' +
      APP_VERSION +
      ', ' +
      RELEASE_DATE +
      '. Open the changelog"><img src="icon.png?v=3" alt="" width="60" height="60"><b>Vocal Sessions</b><span>' +
      APP_VERSION +
      ' · ' +
      RELEASE_DATE +
      '</span></button>'
    );
  }

  /* ----- the pages ----- */
  const hero = (k, text) =>
    '<div class="sethero">' + ico(k, true) + '<h1>' + TITLE[k] + '</h1><p>' + text + '</p></div>';

  function backup() {
    const b = backupVal(),
      lb = D.lastBackup;
    return (
      hero(
        'backup',
        'Saves everything in one file: sessions, minutes, exercises, songs with their lyrics and marks, and recordings. Keep it in iCloud Drive, and import it after re-adding the app or switching phones.'
      ) +
      '<div class="grp setgap">' +
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
      (b.warn ? ' warn' : '') +
      '">' +
      (lb ? 'Last backed up ' + shortDate(lb) + ' at ' + timeOf(lb) : 'Never backed up') +
      (b.warn && lb ? '. It’s been over two weeks.' : '') +
      '</p>' +
      '<p class="foot">You can leave recordings out when you export. Song tracks and the coach video stay on this ' +
      deviceName() +
      ' and are never backed up.</p>' +
      rescuedRows() +
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
      '</button></div>'
    );
  }

  // Q11: saved data that couldn't be read, kept exactly as it was, to save as a file or delete
  function rescuedRows() {
    const r = SAFE.rescued();
    if (!r.length) return '';
    return (
      '<div class="hdr">Rescued data</div><div class="grp">' +
      r
        .map(
          (c) =>
            '<button class="row" data-a="rescueSave" data-k="' +
            esc(c.key) +
            '"><span class="lbl acc">Save the rescued copy<small>' +
            (c.why === 'song' ? 'A song couldn’t be read' : 'Couldn’t be read') +
            ' on ' +
            shortDate(c.at) +
            ' at ' +
            timeOf(c.at) +
            ' · ' +
            mb(c.bytes) +
            '</small></span>' +
            ICON.share +
            '</button>' +
            '<button class="row" data-a="sheet" data-v="rescueDel" data-k="' +
            esc(c.key) +
            '"><span class="lbl dng">Delete the rescued copy</span></button>'
        )
        .join('') +
      '</div><p class="foot">Your saved data as it was when the app couldn’t read it, kept on this ' +
      deviceName() +
      ' so nothing is lost. Save it to Files, and it can usually be mended.</p>'
    );
  }

  function storage() {
    const s = sizes(),
      all = s.reduce((a, x) => a + x.b, 0),
      shown = s.filter((x) => x.b > 0);
    return (
      hero('storage', 'What’s using space on this ' + deviceName() + '. Everything stays on your device.') +
      '<div class="grp setgap setuse" role="img" aria-label="' +
      mb(all) +
      ' used: ' +
      shown.map((x) => x.l + ' ' + mb(x.b)).join(', ') +
      '"><div class="setuse-t">' +
      mb(all) +
      ' used</div><div class="setbar" aria-hidden="true">' +
      (all
        ? shown
            .map((x) => '<i style="flex:' + Math.max(x.b / all, 0.012).toFixed(4) + ';background:' + x.c + '"></i>')
            .join('')
        : '<i style="flex:1;background:var(--fill)"></i>') +
      '</div><div class="setkey" aria-hidden="true">' +
      s.map((x) => '<span><i style="background:' + x.c + '"></i>' + x.l + '</span>').join('') +
      '</div></div>' +
      '<div class="grp setgap">' +
      TAKE.storageRows() + // Recordings · n takes · x MB, and Review old takes (3.20)
      TRACK.storageRow() +
      COACH.storageRow() +
      '<div class="row"><span class="lbl">Sessions and songs</span><span class="mut">' +
      mb(s[3].b) +
      '</span></div></div>' +
      '<div class="grp setgap">' +
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
      '</button></div>'
    );
  }

  function recall() {
    return (
      '<h1>Recall</h1>' +
      '<div class="grp setgap"><div class="row"><span class="lbl">Peek length</span>' +
      '<div class="seg pk-seg pkseg" role="group" aria-label="Peek length"><span class="pk-seg-ind" aria-hidden="true"></span>' +
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
      '<p class="foot">How long a hidden line shows when you tap it in Recall. Hold a line to keep it showing until you let go.</p>'
    );
  }

  function coach() {
    return '<h1>Coach video</h1>' + COACH.settings(true);
  }

  function appear() {
    const g = gradOn();
    return (
      '<h1>Appearance</h1>' +
      '<div class="grp setgap">' +
      '<button class="row" data-a="setGrad" role="switch" aria-checked="' +
      g +
      '"><span class="lbl">Gradient background</span>' +
      switchHTML(g) +
      '</button></div>' +
      '<p class="foot">A soft moving wash behind Today’s header.</p>' +
      '<div class="grp setgap">' +
      '<button class="row" data-a="setIds" role="switch" aria-checked="' +
      idsOn() +
      '"><span class="lbl">Show screen IDs</span>' +
      switchHTML(idsOn()) +
      '</button></div>' +
      '<p class="foot">A small label in the corner with each screen’s ID, such as VS-001, for pointing at a screen in a note. This ' +
      deviceName() +
      ' only, never in backups.</p>'
    );
  }

  function access() {
    const m = reduceMode();
    return (
      '<h1>Accessibility</h1>' +
      '<div class="hdr">Reduce motion</div><div class="grp" role="radiogroup" aria-label="Reduce motion">' +
      REDUCE.map(
        (r) =>
          '<button class="row" data-a="setReduce" data-v="' +
          r[0] +
          '" role="radio" aria-checked="' +
          (m === r[0]) +
          '"><span class="lbl">' +
          r[1]() +
          '</span><span class="acc setchk" aria-hidden="true">' +
          (m === r[0] ? ICON.check : '') +
          '</span></button>'
      ).join('') +
      '</div>' +
      '<p class="foot">Swaps zooms and slides for short fades. Match ' +
      deviceName() +
      ' follows Reduce Motion in your ' +
      deviceName() +
      '’s Accessibility settings' +
      (m === 'system' ? ', which is ' + (MOTION.reduced() ? 'on' : 'off') + ' at the moment' : '') +
      '.</p>' +
      '<div class="hdr">Transparency</div><div class="grp">' +
      '<button class="row" data-a="setTransp" role="switch" aria-checked="' +
      transpSet() +
      '"><span class="lbl">Reduce transparency</span>' +
      switchHTML(transpSet()) +
      '</button></div>' +
      '<p class="foot">Makes the glass more solid, so what’s on it is easier to read. ' +
      (transpSet() || !(tmq && tmq.matches)
        ? 'This ' + deviceName() + ' only, never in backups.'
        : 'On at the moment, because this browser’s own Reduce Transparency setting is on.') +
      '</p>' +
      '<div class="hdr">Tuning</div><div class="grp">' +
      '<button class="row" data-a="setSlow" role="switch" aria-checked="' +
      slow() +
      '"><span class="lbl">Slow motion</span>' +
      switchHTML(slow()) +
      '</button></div>' +
      '<p class="foot">Plays every animation four times slower, to check how it feels. This ' +
      deviceName() +
      ' only, never in backups.</p>'
    );
  }

  function page() {
    const f = { backup, storage, recall, coach, appear, access, voice: PAT.voicePage, player: PAT.playerPage }[U.setPg];
    return f ? f() : main();
  }
  const title = () => TITLE[U.setPg] || 'Settings';

  /* ----- getting around ----- */
  function open(k) {
    if (!PAGES.includes(k)) return;
    U.setFrom = null;
    go(() => {
      U.tab = 'settings';
      U.view = 'set';
      U.setPg = k;
    });
  }
  // Back to the main list, or (Q32) to the exercise page Your voice was opened from
  function back() {
    const f = U.setFrom;
    U.setFrom = null;
    go(() => {
      U.setPg = null;
      if (f) {
        U.tab = f.tab;
        U.view = f.view;
        return;
      }
      U.tab = 'settings';
      U.view = null;
    });
  }
  // Settings is on screen (the main list or one of its pages), so it can be redrawn when something changes
  const shown = () => U.tab === 'settings' && (!U.view || U.view === 'set');

  Object.assign(SG_ACT, {
    setPg: (el, v) => open(v),
    setPgBack: () => back(),
    setReduce: (el, v) => {
      setReduce(v);
      rerender();
    },
    setSlow: () => {
      MOTION.setSpeed(slow() ? 1 : 4);
      rerender();
    },
    setTransp: () => {
      setTransp(!transpSet());
      rerender();
    },
    setGrad: () => {
      setGrad(!gradOn());
      rerender();
    },
    setIds: () => {
      setIds(!idsOn());
      rerender();
    },
  });

  return {
    main,
    page,
    title,
    open,
    back,
    shown,
    reduceMode,
    setReduce,
    sizes,
    PAGES,
    gradOn,
    setGrad,
    idsOn,
    setIds,
    wash,
    transpOn,
    setTransp,
  };
})();

function scrSettings() {
  return SET.main();
}
