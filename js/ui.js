/* Vocal Sessions · ui.js
   Top bar, tab bar, sidebar and sheets; render(); the sliding picker knobs.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Chrome ===== */
const VIEWS = {
  found: ['Foundation', '1 of 3', null],
  rot: ['Rotation', '2 of 3', 'found'],
  app: ['Application', '3 of 3', 'rot'],
  song: ['Song practice', '', null],
};
function pillText() {
  const st = VIEWS[U.view] && VIEWS[U.view][1];
  return (X && X.paused ? '❚❚ ' : '') + (st ? st + ' · ' : '') + clk(elapsedSec());
}
function renderBar() {
  const bar = $('bar');
  bar.classList.remove('tabsmode', 'always');
  $('barT').classList.remove('tabs');
  const tabsMode = MQ.reg.matches && !MQ.wide.matches;
  if (U.view === 'all') {
    $('barL').innerHTML = '<button class="circ glass" data-a="allBack" aria-label="Back">' + ICON.back + '</button>';
    $('barR').innerHTML = '';
    if (tabsMode) {
      bar.classList.add('tabsmode');
      $('barT').classList.add('tabs');
      $('barT').innerHTML = topTabs();
    } else $('barT').textContent = 'All sessions';
  } else if (U.view === 'log') {
    if (tabsMode) {
      bar.classList.add('tabsmode');
      $('barT').classList.add('tabs');
      $('barT').innerHTML = topTabs();
    } else $('barT').textContent = 'Changelog';
    $('barL').innerHTML = '<button class="circ glass" data-a="logBack" aria-label="Back">' + ICON.back + '</button>';
    $('barR').innerHTML = '';
  } else if (U.view === 'ex') {
    const e = exById(U.exId);
    $('barT').textContent = e ? e.name : '';
    $('barL').innerHTML = '<button class="circ glass" data-a="exBack" aria-label="Back">' + ICON.back + '</button>';
    $('barR').innerHTML = '';
  } else if (U.view === 'lyr') {
    const b = songViewBar();
    if (b.tabs) {
      $('barT').classList.add('tabs');
      $('barT').innerHTML = b.t;
    } else $('barT').innerHTML = b.t;
    if (b.always) bar.classList.add('always');
    $('barL').innerHTML = b.l;
    $('barR').innerHTML = b.r;
  } else if (U.view) {
    const v = VIEWS[U.view];
    $('barT').textContent = v[0];
    $('barL').innerHTML =
      '<button class="circ glass" data-a="' +
      (v[2] ? 'view' : 'exit') +
      '" data-v="' +
      (v[2] || '') +
      '" aria-label="Back">' +
      ICON.back +
      '</button>';
    $('barR').innerHTML =
      (U.view === 'song'
        ? ''
        : '<a class="circ glass" href="' +
          VIDEO +
          '" target="_blank" rel="noopener" aria-label="Open coach video">' +
          ICON.video +
          '</a>') +
      '<button class="pill glass' +
      (X && X.paused ? ' paused' : '') +
      '" id="timer" data-a="clock" aria-label="Session time. Tap for the clock">' +
      pillText() +
      '</button>';
  } else {
    // Today has Settings at the top right; Settings has a way back; Songs has its buttons on iPhone
    const x =
      U.tab === 'today'
        ? {
            l: '',
            r: '<button class="circ glass" data-a="openSettings" aria-label="Settings">' + ICON.gear + '</button>',
          }
        : U.tab === 'settings'
          ? {
              l: '<button class="circ glass" data-a="setBack" aria-label="Back to Today">' + ICON.back + '</button>',
              r: '',
            }
          : U.tab === 'songs' && !split()
            ? songListBar()
            : { l: '', r: '' };
    $('barL').innerHTML = x.l;
    $('barR').innerHTML = x.r;
    if (tabsMode) {
      bar.classList.add('tabsmode');
      $('barT').classList.add('tabs');
      $('barT').innerHTML = topTabs();
      return;
    }
    $('barT').textContent =
      x.t ||
      { today: 'Today', history: 'Progress', exercises: 'Exercises', songs: 'Songs', settings: 'Settings' }[U.tab];
    if (x.always) bar.classList.add('always');
  }
}
const topTabs = () =>
  '<nav class="toptabs glass" aria-label="Tabs">' +
  TABS()
    .map(
      (t) =>
        '<button class="' +
        (tabOf(U.tab) === t[0] ? 'on' : '') +
        '" data-a="tab" data-v="' +
        t[0] +
        '" aria-current="' +
        (tabOf(U.tab) === t[0] ? 'page' : 'false') +
        '">' +
        t[1] +
        '</button>'
    )
    .join('') +
  '</nav>';
function renderSide() {
  const el = $('side');
  if (!MQ.wide.matches) {
    el.innerHTML = '';
    return;
  }
  el.innerHTML =
    '<div class="sbt">Vocal Sessions</div>' +
    TABS()
      .map(
        (t) =>
          '<button class="sbi' +
          (tabOf(U.tab) === t[0] ? ' on' : '') +
          '" data-a="tab" data-v="' +
          t[0] +
          '" aria-current="' +
          (tabOf(U.tab) === t[0] ? 'page' : 'false') +
          '">' +
          t[2] +
          '<span>' +
          t[1] +
          '</span></button>'
      )
      .join('');
}
function renderDock() {
  if (U.sheet) {
    $('dock').innerHTML = '';
    return;
  }
  // recording a section: the recording bar takes the place of the tab bar
  if (rec && rec.o) {
    $('dock').innerHTML =
      '<div class="recbar glass" role="group" aria-label="Recording"><span class="rectime"><span class="recdot" aria-hidden="true"></span><span id="recT">' +
      mmss(rec.t) +
      '</span></span><span class="meter" id="recMeter" aria-hidden="true">' +
      '<i></i>'.repeat(14) +
      '</span><button class="stopb" data-a="sgStop" aria-label="Stop recording"><i></i></button></div>';
    return;
  }
  if (isFlow(U.view)) {
    const n = Object.keys(X.rot).length;
    const lab = {
      found: 'Log foundation',
      rot: n ? 'Log ' + n + ' exercise' + (n > 1 ? 's' : '') : 'Pick an exercise',
      app: 'Finish session',
      song: 'Save song practice',
    }[U.view];
    $('dock').innerHTML = '<button class="cta glass tinted" data-a="cta">' + lab + '</button>';
    return;
  }
  if (MQ.reg.matches) {
    $('dock').innerHTML = '';
    return;
  }
  const songList = U.tab === 'songs' && !U.view;
  // iPhone: searching songs, selecting them or editing one takes the place of the tab bar
  if ((songList && (U.sFocus || U.sList)) || (U.view === 'lyr' && U.sEdit)) {
    $('dock').innerHTML = '';
    return;
  }
  if (window.scrollY < 60) tabMin = false; // never leave it shrunk at the top of a page
  const cur = tabOf(U.tab);
  const nav =
    '<nav class="tabbar glass' +
    (tabMin ? ' min' : '') +
    '" aria-label="Tabs">' +
    TABS()
      .map(
        (t) =>
          '<button class="' +
          (cur === t[0] ? 'on' : '') +
          '" data-a="tab" data-v="' +
          t[0] +
          '" aria-current="' +
          (cur === t[0] ? 'page' : 'false') +
          '">' +
          t[2] +
          t[1] +
          '</button>'
      )
      .join('') +
    '</nav>';
  $('dock').innerHTML =
    songList && D.songs.length
      ? '<div class="dockrow">' +
        nav +
        '<button class="circ glass scirc" data-a="sgSearch" aria-label="Search songs">' +
        SGI.search +
        '</button></div>'
      : nav;
}
function sheetWrap(title, body, label, tools) {
  return (
    '<div class="scrim" data-a="close"><div class="sheet glass" role="dialog" aria-modal="true" aria-label="' +
    esc(label || title) +
    '"><div class="shead"><div class="grab"></div><div class="shrow"><h2>' +
    title +
    '</h2>' +
    (tools || '') +
    '<button class="shbtn glass xbtn" data-a="close" aria-label="Close">' +
    ICON.x +
    '</button></div></div>' +
    body +
    '</div></div>'
  );
}
const confirmSheet = (title, text, btn, action, k, cancel) =>
  sheetWrap(
    title,
    '<p class="note">' +
      text +
      '</p><button class="cta red" data-a="' +
      action +
      '" data-k="' +
      esc(k || '') +
      '">' +
      btn +
      '</button><button class="ghost" data-a="close">' +
      (cancel || 'Cancel') +
      '</button>'
  );
const noteTarget = () => (U.sd && U.sd.src === 'edit' ? E : X);
function selArr() {
  const s = U.sheet;
  if (s === 'how') return X && X.how;
  if (s === 'edit') return E && E.how;
  if (s === 'exNote') {
    const T = noteTarget();
    return T && T.xn && T.xn[U.sd.k] && T.xn[U.sd.k].w;
  }
  if (s === 'takeNote') {
    const t = TAKES.find((x) => x.id === U.sd.k);
    return t && t.note && t.note.w;
  }
  return null;
}
function howRow(ss) {
  const w = (ss.how || []).join(', ');
  if (!w && !ss.howNote) return '';
  return (
    '<div class="row"><span class="lbl">How it went' +
    (w ? '<small class="acc">' + esc(w) + '</small>' : '') +
    (ss.howNote ? '<small>' + esc(ss.howNote) + '</small>' : '') +
    '</span></div>'
  );
}
function renderSheet() {
  const s = U.sheet,
    k = U.sd.k;
  let h = '';
  if (s && /^sg[A-Z]/.test(s)) h = songSheet(s);
  else if (s === 'confirmF')
    h = sheetWrap(
      'Confirm foundation',
      '<div class="grp">' +
        FOUND.map(
          (e) =>
            '<div class="row"><span class="lbl">' +
            esc(e.name) +
            '</span><span class="mut">' +
            (X.f[e.id] ? 'Level ' + X.f[e.id] : 'Skipped') +
            '</span></div>'
        ).join('') +
        '</div><div style="margin-top:14px"><button class="cta" data-a="confirmF">Log foundation</button></div><button class="ghost" data-a="close">Edit</button>'
    );
  else if (s === 'how' && X) {
    h =
      '<div class="scrim" data-a="close"><div class="sheet glass" role="dialog" aria-modal="true" aria-label="How did it go?"><div class="shead"><div class="grab"></div><div class="shtop"><button class="shbtn glass" data-a="skipHow" aria-label="Skip and save">' +
      ICON.x +
      '</button><span class="mut" style="font-size:13px">' +
      (isSong() ? 'Song practice' : 'Session') +
      ' · ' +
      hm(finalMins()) +
      '</span><button class="shbtn ok" data-a="saveHow" aria-label="Save">' +
      ICON.check +
      '</button></div></div>' +
      '<h2 class="c">How did it go?</h2><p class="note" style="text-align:center">Tap any that fit. It’s all optional.</p>' +
      chipsHTML(wordList('how', HOW_WORDS), X.how, 'how') +
      noteBlock('howNote', X.howNote, 'Anything else about today') +
      '</div></div>';
  } else if (s === 'long' && X) {
    const m = Math.round(elapsedSec() / 60);
    h = sheetWrap(
      'How long did you practise?',
      '<p class="note">This ' +
        (isSong() ? 'song practice' : 'session') +
        ' has been running for ' +
        hm(m) +
        '. If you stopped and forgot to finish, enter the minutes you actually practised.</p><input class="field" id="longMins" type="number" inputmode="numeric" min="1" max="' +
        m +
        '" value="' +
        m +
        '" aria-label="Minutes practised"><div style="margin-top:14px"><button class="cta" data-a="longOk">Continue</button></div><button class="ghost" data-a="longAll">I practised the whole time</button>'
    );
  } else if (s === 'exNote') {
    const T = noteTarget();
    if (T) {
      const e = exById(k) || { name: (T.rotNames || {})[k] || 'Exercise' };
      T.xn = T.xn || {};
      if (!T.xn[k] || typeof T.xn[k] !== 'object') T.xn[k] = { w: [], t: T.xn[k] || '' };
      const n = T.xn[k];
      h = sheetWrap(
        esc(e.name),
        '<p class="note">Tap words that describe how it went. These are just for this exercise.</p>' +
          chipsHTML(wordList('x_' + k, EX_WORDS[k] || EX_WORDS_DEFAULT), n.w, 'x_' + k) +
          noteBlock('xnText', n.t, 'More detail on ' + e.name.toLowerCase()) +
          '<div style="margin-top:14px"><button class="cta" data-a="close">Done</button></div>' +
          (n.w.length || n.t
            ? '<button class="ghost" data-a="xnClear" style="color:var(--danger)">Clear notes</button>'
            : ''),
        'Notes for ' + e.name
      );
    }
  } else if (s === 'takeNote') {
    const t = TAKES.find((x) => x.id === k);
    if (t) {
      if (!t.note || typeof t.note !== 'object') t.note = { w: [], t: '' };
      h = sheetWrap(
        'Take · ' + shortDate(t.created) + ' · ' + mmss(t.len),
        '<p class="note">Tap words that describe this take.</p>' +
          chipsHTML(wordList('take', TAKE_WORDS), t.note.w, 'take') +
          noteBlock('tnText', t.note.t, 'More detail on this take') +
          '<div style="margin-top:14px"><button class="cta" data-a="close">Done</button></div>',
        'Notes for this take'
      );
    }
  } else if (s === 'addWord')
    h = sheetWrap(
      'Your own words',
      '<p class="note">It’s saved as a chip for next time.</p><input class="field" id="wordIn" maxlength="30" placeholder="Felt it in my chest" autocomplete="off"><div style="margin-top:14px"><button class="cta" data-a="saveWord">Add</button></div><button class="ghost" data-a="close">Cancel</button>'
    );
  else if (s === 'edit' && E) h = editSheet();
  else if (s === 'addEx')
    h = sheetWrap(
      'Add exercise',
      '<input class="field" id="exName" maxlength="40" placeholder="Siren on ng" autocomplete="off"><div class="err" id="exErr" hidden></div><div class="hdr">Focus</div><div class="chips" id="focusChips">' +
        FOCI.map(
          (f, i) =>
            '<button class="chip' + (i === 0 ? ' on' : '') + '" data-a="focus" data-v="' + f + '">' + f + '</button>'
        ).join('') +
        '</div><div class="hdr">What it is (optional)</div><textarea class="field" id="exWhat" maxlength="400" placeholder="Slide up and down on ng, keeping it light"></textarea><div style="margin-top:14px"><button class="cta" data-a="saveEx">Add exercise</button></div><button class="ghost" data-a="close">Cancel</button>'
    );
  else if (s === 'editWhat') {
    const e = exById(k) || {};
    h = sheetWrap(
      'Description',
      '<textarea class="field" id="whatIn" maxlength="400" placeholder="What the exercise is and how to do it">' +
        esc(e.what || '') +
        '</textarea><div style="margin-top:14px"><button class="cta" data-a="saveWhat" data-k="' +
        esc(k) +
        '">Save</button></div><button class="ghost" data-a="close">Cancel</button>'
    );
  } else if (s === 'addSong')
    h = sheetWrap(
      'Add song',
      '<input class="field" id="songIn" maxlength="60" placeholder="Versace on the Floor · bridge" autocomplete="off"><div class="err" id="songErr" hidden></div><p class="note" style="margin-top:8px">Include the section you’re working on, so takes stay grouped.</p><div style="margin-top:8px"><button class="cta" data-a="saveSong">Add song</button></div><button class="ghost" data-a="close">Cancel</button>'
    );
  else if (s === 'delEx') {
    const e = exById(k);
    h = confirmSheet(
      'Delete exercise?',
      esc(e ? e.name : '') + ' will be removed from your rotation. Past sessions keep it.',
      'Delete exercise',
      'delEx',
      k
    );
  } else if (s === 'delSong') {
    const so = D.songs.find((x) => x.id === k);
    h = confirmSheet(
      'Delete song?',
      esc(so ? so.name : '') + ' and its saved takes will be deleted from this phone.',
      'Delete song',
      'delSong',
      k
    );
  } else if (s === 'delTake') {
    const t = TAKES.find((x) => x.id === k);
    h = confirmSheet(
      'Delete take?',
      'This ' +
        (t ? mmss(t.len) + ' ' : '') +
        'recording will be deleted from this phone. Copies you saved to Files stay.',
      'Delete take',
      'delTake',
      k
    );
  } else if (s === 'delSession') {
    const ss = D.sessions.find((x) => x.id === k);
    h = confirmSheet(
      'Delete session?',
      (ss ? dayLabel(ss.date) + ' (' + hm(ss.mins) + ')' : 'This session') +
        ' will be removed. Its minutes come off that month and its exercises’ last-done dates are updated.',
      'Delete session',
      'delSession',
      k
    );
  } else if (s === 'delSongSess') {
    const ss = D.songSessions.find((x) => x.id === k);
    h = confirmSheet(
      'Delete song practice?',
      (ss ? dayLabel(ss.date) + ' (' + hm(ss.mins) + ')' : 'This song practice') +
        ' will be removed from your history. Its recordings stay.',
      'Delete',
      'delSongSess',
      k
    );
  } else if (s === 'storage') {
    const size = TAKES.reduce((a, t) => a + t.size, 0);
    h = sheetWrap(
      'Recordings',
      '<div class="grp"><div class="row"><span class="lbl">Saved takes</span><span class="mut">' +
        TAKES.length +
        '</span></div><div class="row"><span class="lbl">Space used</span><span class="mut">' +
        (size / 1048576).toFixed(1) +
        ' MB</span></div><div class="row"><span class="lbl">Starred</span><span class="mut">' +
        TAKES.filter((t) => t.star).length +
        '</span></div></div><p class="note" style="margin-top:10px">Recordings live on this phone and in your backups. Use Share on a take to save it to iCloud Drive on its own.</p><button class="cta red" data-a="sheet" data-v="clearRec">Delete all recordings</button><button class="ghost" data-a="close">Done</button>'
    );
  } else if (s === 'clearRec')
    h = confirmSheet(
      'Delete all recordings?',
      'Every saved take on this phone will be deleted. This can’t be undone.',
      'Delete all recordings',
      'clearRec'
    );
  else if (s === 'resetMonth')
    h = confirmSheet(
      'Reset this month?',
      'This month’s minutes go back to zero. Sessions and recordings stay.',
      'Reset minutes',
      'resetMonth'
    );
  else if (s === 'resetAll')
    h = sheetWrap(
      'Reset all data?',
      '<p class="note">Deletes your history, minutes, streak, custom exercises, songs, song practice and recordings on this phone. This can’t be undone.</p><button class="cta" data-a="exportPrep" style="margin-bottom:10px">Export a backup first</button><button class="cta red" data-a="resetAll">Delete everything</button><button class="ghost" data-a="close">Cancel</button>'
    );
  else if (s === 'discard')
    h = isSong()
      ? confirmSheet(
          'Discard song practice?',
          'This practice won’t be saved. Recordings stay.',
          'Discard',
          'discardYes',
          '',
          'Keep going'
        )
      : confirmSheet(
          'Discard session?',
          'Levels and notes from this session won’t be saved. Recordings stay.',
          'Discard',
          'discardYes',
          '',
          'Keep session'
        );
  else if (s === 'exportReady' && pendingExport) {
    const P = pendingExport,
      first = !loadLog().length;
    h = sheetWrap(
      'Backup ready',
      '<div class="bkstat ok">' +
        ICON.okc +
        '<div><b>' +
        (P.verified ? 'Checked' : 'Ready') +
        '</b>' +
        (P.verified ? 'The file reads back correctly and its check code matches.' : 'The file reads back correctly.') +
        '</div></div>' +
        '<div class="grp" style="margin-top:10px"><div class="row"><span class="lbl">File<small class="fname">' +
        esc(P.file.name) +
        '</small></span><span class="mut">' +
        mb(P.file.size) +
        '</span></div><div class="row"><span class="lbl">Sessions</span><span class="mut">' +
        P.s.sessions +
        '</span></div><div class="row"><span class="lbl">Song practice</span><span class="mut">' +
        P.s.songPractice +
        '</span></div><div class="row"><span class="lbl">Recordings</span><span class="mut">' +
        (P.busy ? '…' : P.noRec ? 'Not included' : P.s.recordings) +
        '</span></div></div>' +
        '<div class="grp" style="margin-top:10px"><button class="row" data-a="exportNoRec" role="switch" aria-checked="' +
        P.noRec +
        '"><span class="lbl">Exclude recordings<small>A smaller file. Restoring it keeps the recordings already on the device.</small></span><span class="tgl" aria-checked="' +
        P.noRec +
        '" aria-hidden="true"></span></button></div>' +
        '<p class="note" style="margin-top:10px">Choose <b>Save to Files</b>, then <b>iCloud Drive › Vocal Sessions › Backups</b>.' +
        (first ? '' : ' If Files asks, tap Replace to update this month’s backup.') +
        '</p>' +
        (first
          ? '<button class="row grp" data-a="bkGuideFrom" style="margin-bottom:14px;border-radius:16px"><span class="lbl acc">First time? Set up the folder</span>' +
            chev +
            '</button>'
          : '') +
        '<button class="cta" data-a="exportSave"' +
        (P.busy ? ' disabled' : '') +
        '>Save backup</button><button class="ghost" data-a="close">Cancel</button>'
    );
  } else if (s === 'persist') {
    const on = PERSIST === true;
    h = sheetWrap(
      'Storage protection',
      '<div class="bkstat ' +
        (on ? 'ok' : 'warn') +
        '">' +
        (on ? ICON.okc : ICON.warn) +
        '<div><b>' +
        (on ? 'On' : PERSIST === 'na' ? 'Not available here' : 'Off for now') +
        '</b>' +
        (on
          ? 'iOS has agreed to keep Vocal Sessions’ data, even when space runs low.'
          : PERSIST === 'na'
            ? 'This browser doesn’t let apps ask for protected storage.'
            : 'iOS hasn’t agreed yet. It decides this itself, and usually agrees for apps on the Home Screen.') +
        '</div></div>' +
        '<p class="note" style="margin-top:12px">When ' +
        (deviceName() === 'computer' ? 'a device' : 'an ' + deviceName()) +
        ' is very low on space, iOS can clear data saved by websites and web apps. Vocal Sessions asks iOS to protect its sessions and recordings from that.</p>' +
        '<p class="note">Either way, your backups in iCloud Drive are what keep everything safe.</p>' +
        (PERSIST === false ? '<button class="cta" data-a="persistAsk">Ask again</button>' : '') +
        '<button class="ghost" data-a="exportPrep">Back up now</button><button class="ghost" data-a="close">Done</button>'
    );
  } else if (s === 'bkReport' && pendingImport) h = bkReportHTML(pendingImport, U.sd.mode);
  else if (s === 'bkGuide') h = bkGuideHTML();
  else if (s === 'bkLog') h = bkLogHTML();
  else if (s === 'undoRestore' && UNDO) h = undoHTML();
  else if (s === 'undoing')
    h = sheetWrap('Undoing restore', '<p class="note">Putting back your sessions and recordings…</p>');
  else if (s === 'exporting')
    h = sheetWrap('Preparing backup', '<p class="note">Gathering your sessions and recordings…</p>');
  else if (s === 'importing')
    h = sheetWrap('Restoring backup', '<p class="note">Restoring your sessions and recordings…</p>');
  else if (s === 'calendar') h = calendarSheet();
  else if (s === 'session' || s === 'done') {
    const ss = D.sessions.find((x) => x.id === k);
    if (ss) h = sessionSheet(ss, s === 'done');
  } else if (s === 'songSession' || s === 'songDone') {
    const ss = D.songSessions.find((x) => x.id === k);
    if (ss) h = songSessionSheet(ss, s === 'songDone');
  }
  if (s && !h) {
    U.sheet = null;
    U.sd = {};
  }
  if (!h && U.clock && X && isFlow(U.view)) h = clockHTML();
  const key = h ? (U.sheet ? U.sheet + '|' + (k || '') : 'clock') : '';
  const prev = $('layer').querySelector('.sheet'),
    st = prev ? prev.scrollTop : 0,
    same = !!key && key === lastLayerKey;
  lastLayerKey = key;
  $('layer').innerHTML = h;
  if (same) {
    $('layer')
      .querySelectorAll('.scrim,.sheet,.clock,.clockscrim')
      .forEach((x) => x.classList.add('still'));
    const ns = $('layer').querySelector('.sheet');
    if (ns) ns.scrollTop = st;
  }
  const open = !!h && !!U.sheet;
  if (open && !document.body.classList.contains('sheet-open'))
    $('app').parentNode.style.transformOrigin = '50% ' + (window.scrollY + 120) + 'px';
  document.body.classList.toggle('sheet-open', open);
  if (h) placeKnobs($('layer'));
  if (s === 'addEx')
    setTimeout(() => {
      const i = $('exName');
      if (i) i.focus();
    }, 250);
  if (s === 'addSong')
    setTimeout(() => {
      const i = $('songIn');
      if (i) i.focus();
    }, 250);
}
function clockHTML() {
  const e = elapsedSec(),
    song = isSong(),
    v = U.view,
    fE = X.fE || 0,
    rE = X.rE || 0;
  const steps = song
    ? [['Song practice', e, 'cur', 0]]
    : [
        ['Foundation', v === 'found' ? e : fE, v === 'found' ? 'cur' : '', 0],
        [
          'Rotation',
          v === 'rot' ? e - fE : v === 'app' ? rE - fE : null,
          v === 'rot' ? 'cur' : v === 'app' ? '' : 'todo',
          fE,
        ],
        ['Application', v === 'app' ? e - rE : null, v === 'app' ? 'cur' : 'todo', rE],
      ];
  return (
    '<div class="clockscrim" data-a="clockClose"></div><div class="clock glass" role="dialog" aria-label="Session clock"><div class="ctop"><span>' +
    (song ? 'Song practice' : 'Session') +
    '</span><span>' +
    (VIEWS[v][1] ? 'Step ' + VIEWS[v][1] : '') +
    '</span></div>' +
    '<div class="big' +
    (X.paused ? ' paused' : '') +
    '" id="bigClock">' +
    clk(e) +
    '</div><div class="csub">' +
    (X.paused ? 'Paused. Paused time isn’t counted.' : 'Started at ' + timeOf(X.start)) +
    '</div>' +
    '<div class="cbtns"><button class="cbtn hide" data-a="clockClose">Hide</button><button class="cbtn ' +
    (X.paused ? 'resume' : 'pause') +
    '" data-a="pauseToggle">' +
    (X.paused ? 'Resume' : 'Pause') +
    '</button></div>' +
    '<div class="splits">' +
    steps
      .map(
        (x) =>
          '<div class="' +
          x[2] +
          '"><span>' +
          x[0] +
          '</span><span' +
          (x[2] === 'cur' ? ' id="curSplit" data-base="' + x[3] + '"' : '') +
          '>' +
          (x[1] === null ? '–' : clk(x[1])) +
          '</span></div>'
      )
      .join('') +
    '</div></div>'
  );
}
function calendarSheet() {
  const m = U.calMonth || new Date(new Date().getFullYear(), new Date().getMonth(), 1);
  const y = m.getFullYear(),
    mo = m.getMonth();
  const first = new Date(y, mo, 1),
    days = new Date(y, mo + 1, 0).getDate(),
    lead = (first.getDay() + 6) % 7;
  const byDay = {},
    songDay = {};
  D.sessions.forEach((s) => {
    const d = new Date(s.date);
    if (d.getFullYear() === y && d.getMonth() === mo) (byDay[d.getDate()] = byDay[d.getDate()] || []).push(s);
  });
  D.songSessions.forEach((s) => {
    const d = new Date(s.date);
    if (d.getFullYear() === y && d.getMonth() === mo) (songDay[d.getDate()] = songDay[d.getDate()] || []).push(s);
  });
  const now = new Date(),
    isThisMonth = now.getFullYear() === y && now.getMonth() === mo;
  let g = ['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((l) => '<span class="h">' + l + '</span>').join('');
  for (let i = 0; i < lead; i++) g += '<span></span>';
  for (let d = 1; d <= days; d++) {
    const has = !!byDay[d],
      hs = !!songDay[d];
    const cls =
      (has ? 'p ' : '') +
      (hs ? 's ' : '') +
      (isThisMonth && d === now.getDate() ? 't ' : '') +
      (U.calDay === d ? 'sel' : '');
    const parts = [];
    if (has) parts.push(byDay[d].length + ' session' + (byDay[d].length > 1 ? 's' : ''));
    if (hs) parts.push('song practice');
    g +=
      has || hs
        ? '<button class="' +
          cls +
          '" data-a="calDay" data-v="' +
          d +
          '" aria-label="' +
          d +
          ' ' +
          m.toLocaleDateString('en-GB', { month: 'long' }) +
          ', ' +
          parts.join(' and ') +
          '">' +
          d +
          '</button>'
        : '<button class="' + cls + '" disabled aria-label="' + d + '">' + d + '</button>';
  }
  const mk = y + '-' + String(mo + 1).padStart(2, '0');
  const n = Object.values(byDay).reduce((a, x) => a + x.length, 0),
    sn = Object.values(songDay).reduce((a, x) => a + x.length, 0),
    sm = Object.values(songDay).reduce((a, x) => a + x.reduce((b, s) => b + s.mins, 0), 0);
  let b =
    '<div class="calhead"><button class="circ" data-a="calMove" data-v="-1" aria-label="Previous month">' +
    ICON.back +
    '</button><b>' +
    m.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' }) +
    '</b><button class="circ" data-a="calMove" data-v="1" aria-label="Next month">' +
    ICON.fwd +
    '</button></div><div class="cal">' +
    g +
    '</div>';
  const sel = U.calDay && ((byDay[U.calDay] || []).length || (songDay[U.calDay] || []).length);
  if (sel) {
    b +=
      '<div class="hdr">' +
      new Date(y, mo, U.calDay).toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' }) +
      '</div><div class="grp">' +
      (byDay[U.calDay] || [])
        .map((s) => {
          const r = Object.keys(s.rot || {}).map(
            (id) => (exById(id) || { name: (s.rotNames || {})[id] || 'Exercise' }).name
          );
          return (
            '<button class="row" data-a="calSession" data-k="' +
            s.id +
            '"><span class="lbl">' +
            timeOf(s.date) +
            '<small>' +
            esc(r.length ? r.join(', ') : 'Foundation only') +
            '</small></span><span class="mut">' +
            hm(s.mins) +
            '</span>' +
            chev +
            '</button>'
          );
        })
        .join('') +
      (songDay[U.calDay] || [])
        .map(
          (s) =>
            '<button class="row" data-a="calSession" data-k="' +
            s.id +
            '"><span class="lbl">' +
            timeOf(s.date) +
            ' · Song practice<small class="co">' +
            esc(s.songName || '') +
            '</small></span><span class="mut">' +
            hm(s.mins) +
            '</span>' +
            chev +
            '</button>'
        )
        .join('') +
      '</div>';
  } else
    b +=
      '<p class="foot">' +
      (n || sn
        ? 'Blue days are focused sessions; a coral dot is song practice. Tap a day to see it.'
        : 'Nothing logged this month.') +
      '</p>';
  b +=
    '<div class="grp" style="margin-top:12px"><div class="row"><span class="lbl">This month</span><span class="mut">' +
    n +
    ' session' +
    (n === 1 ? '' : 's') +
    ' · ' +
    hm(D.months[mk] || 0) +
    '</span></div>' +
    (sn
      ? '<div class="row"><span class="lbl">Song practice</span><span class="mut">' +
        sn +
        ' · ' +
        hm(sm) +
        '</span></div>'
      : '') +
    '</div><button class="ghost" data-a="close">Done</button>';
  return sheetWrap('Practice calendar', b);
}
const editBtn = (id, lab) =>
  '<button class="shbtn glass xbtn" data-a="editSess" data-k="' +
  id +
  '" aria-label="' +
  lab +
  '">' +
  ICON.pen +
  '</button>';
function sessionSheet(ss, done) {
  return sheetWrap(
    done ? 'Session complete' : dayLabel(ss.date),
    sessionBody(ss, done ? 'done' : 'sheet'),
    '',
    editBtn(ss.id, 'Edit session')
  );
}
function sessionBody(ss, mode) {
  const done = mode === 'done',
    pane = mode === 'pane';
  const rots = Object.keys(ss.rot || {}),
    xn = ss.xn || {};
  const exRow = (name, id, val) => {
    const n = noteStr(xn[id]);
    return (
      '<div class="row"><span class="lbl">' +
      esc(name) +
      (n ? '<small class="acc">' + esc(n) + '</small>' : '') +
      '</span><span class="mut">' +
      val +
      '</span></div>'
    );
  };
  const spl = splitOf(ss);
  let b =
    '<div class="grp"><div class="row"><span class="lbl">Total time</span><span class="mut">' +
    hm(ss.mins) +
    '</span></div>' +
    '<div class="row" style="display:block;padding:12px 16px"><div style="display:flex;justify-content:space-between;font-size:15px"><span>Time per step</span><span class="mut" style="font-size:13px">' +
    (spl.mixed ? 'Filled in at the end' : 'Timed') +
    '</span></div>' +
    '<div class="mini" style="max-width:none;height:6px;margin-top:8px" aria-hidden="true">' +
    (spl.mixed
      ? '<i class="mx" style="flex:1"></i>'
      : BLK.map(([key, , c]) =>
          spl[key] > 0 ? '<i style="flex:' + spl[key] + ';background:var(' + c + ')"></i>' : ''
        ).join('')) +
    '</div>' +
    '<div class="legend" style="margin-top:8px">' +
    BLK.map(
      ([key, nm, c]) =>
        '<span><i class="dot" style="background:var(' + c + ')"></i>' + nm + ' ' + hm(spl[key]) + '</span>'
    ).join('') +
    '</div></div>' +
    howRow(ss) +
    '</div>' +
    (done
      ? '<div style="margin-top:12px"><button class="cta" data-a="copy" data-k="' +
        ss.id +
        '">Copy for Toggl</button></div>'
      : '') +
    '<div class="hdr">Foundation</div><div class="grp">' +
    FOUND.map((e) => {
      const f = ss.f || {};
      return exRow(e.name, e.id, f[e.id] ? 'Level ' + f[e.id] : e.id in f ? 'Skipped' : '–');
    }).join('') +
    (ss.fNote ? '<div class="row"><span class="lbl mut">' + esc(ss.fNote) + '</span></div>' : '') +
    '</div>';
  if (rots.length)
    b +=
      '<div class="hdr">Rotation</div><div class="grp">' +
      rots
        .map((id) =>
          exRow((exById(id) || { name: (ss.rotNames || {})[id] || 'Exercise' }).name, id, 'Level ' + ss.rot[id])
        )
        .join('') +
      (ss.rNote ? '<div class="row"><span class="lbl mut">' + esc(ss.rNote) + '</span></div>' : '') +
      '</div>';
  if (ss.songName || Object.keys(ss.rate || {}).length)
    b +=
      '<div class="hdr">Application</div><div class="grp">' +
      (ss.songName
        ? '<div class="row"><span class="lbl">' +
          esc(ss.songName) +
          '</span>' +
          ((ss.takes || []).length
            ? '<span class="mut">' + ss.takes.length + ' take' + (ss.takes.length > 1 ? 's' : '') + '</span>'
            : '') +
          '</div>'
        : '') +
      ['Pitch', 'Tone', 'Ease']
        .filter((x) => (ss.rate || {})[x])
        .map(
          (x) =>
            '<div class="row"><span class="lbl">' + x + '</span><span class="mut">' + ss.rate[x] + ' of 3</span></div>'
        )
        .join('') +
      '</div>';
  b +=
    (done
      ? ''
      : '<div style="margin-top:16px"><button class="cta" data-a="copy" data-k="' +
        ss.id +
        '">Copy for Toggl</button></div>') + (done ? '<button class="ghost" data-a="close">Done</button>' : '');
  if (!done)
    b +=
      '<button class="ghost" data-a="sheet" data-v="delSession" data-k="' +
      ss.id +
      '" style="color:var(--danger)">Delete session</button>';
  return pane
    ? '<div class="phrow"><h2 class="ph">' + dayLabel(ss.date) + '</h2>' + editBtn(ss.id, 'Edit session') + '</div>' + b
    : b;
}
function songSessionSheet(ss, done) {
  return sheetWrap(
    done ? 'Song practice saved' : dayLabel(ss.date) + ' · Song practice',
    songSessionBody(ss, done ? 'done' : 'sheet'),
    '',
    editBtn(ss.id, 'Edit song practice')
  );
}
function songSessionBody(ss, mode) {
  const done = mode === 'done',
    pane = mode === 'pane';
  const tk = TAKES.filter((t) => (ss.takes || []).includes(t.id));
  let b =
    '<div class="grp"><div class="row"><span class="lbl">Time</span><span class="mut">' +
    hm(ss.mins) +
    '</span></div><div class="row"><span class="lbl">Song</span><span class="mut">' +
    esc(ss.songName || '–') +
    '</span></div>' +
    howRow(ss) +
    '</div>';
  if (tk.length)
    b +=
      '<div class="hdr">Takes</div><div class="grp">' +
      tk
        .map((t) => {
          const n = noteStr(t.note);
          return (
            '<div class="row"><button class="ibtn acc" data-a="playTake" data-k="' +
            t.id +
            '" aria-label="Play take">' +
            (playingId === t.id ? ICON.pause : ICON.play) +
            '</button><span class="lbl">' +
            timeOf(t.created) +
            ' · ' +
            mmss(t.len) +
            (n ? '<small class="acc">' + esc(n) + '</small>' : '') +
            '</span></div>'
          );
        })
        .join('') +
      '</div>';
  else if ((ss.takes || []).length) b += '<p class="foot">This practice’s takes are no longer on this phone.</p>';
  b +=
    '<p class="foot">Toggl tag ' +
    esc(TOGGL.song) +
    '. Kept out of your focused goal and streak.</p><div style="margin-top:12px"><button class="cta" data-a="copy" data-k="' +
    ss.id +
    '">Copy for Toggl</button></div>' +
    (done ? '<button class="ghost" data-a="close">Done</button>' : '') +
    (done
      ? ''
      : '<button class="ghost" data-a="sheet" data-v="delSongSess" data-k="' +
        ss.id +
        '" style="color:var(--danger)">Delete</button>');
  return pane
    ? '<div class="phrow"><h2 class="ph">' +
        dayLabel(ss.date) +
        ' · Song practice</h2>' +
        editBtn(ss.id, 'Edit song practice') +
        '</div>' +
        b
    : b;
}
function editSheet() {
  const song = E.kind === 'song';
  let b =
    '<div class="grp"><div class="row"><span class="lbl">Date</span><input class="field dt" type="date" id="edDate" value="' +
    esc(E.dateStr) +
    '" max="' +
    isoDay(new Date()) +
    '" aria-label="Date"></div>' +
    '<div class="row"><span class="lbl">Minutes</span><input class="field dt num" type="number" inputmode="numeric" id="edMins" min="1" max="600" value="' +
    esc(E.mins) +
    '" aria-label="Minutes"></div></div>';
  if (!song) {
    b +=
      '<div class="hdr">Foundation</div><div class="grp tiled">' +
      FOUND.map((e) => exBlock(e, 'eflv', (E.f || {})[e.id], true, E, 'edit')).join('') +
      '</div>';
    const rk = Object.keys(E.rot || {});
    if (rk.length)
      b +=
        '<div class="hdr">Rotation</div><div class="grp tiled">' +
        rk
          .map((id) =>
            exBlock(
              exById(id) || { id, name: (E.rotNames || {})[id] || 'Exercise', focus: 'custom' },
              'erlv',
              E.rot[id],
              false,
              E,
              'edit'
            )
          )
          .join('') +
        '</div>';
    const tot = +E.mins || 0,
      ef = E.split && !E.mixed ? E.split : null;
    b +=
      '<div class="hdr">Time per step</div><div class="grp"><div class="row" style="display:block;padding:10px 16px 12px"><div class="seg wide" role="group" aria-label="How it was tracked"><span class="knob" aria-hidden="true"></span><button data-a="esplit" data-v="timed" class="' +
      (ef ? 'on' : '') +
      '">Timed</button><button data-a="esplit" data-v="mixed" class="' +
      (ef ? '' : 'on') +
      '">Filled in at the end</button></div></div>' +
      (ef
        ? '<div class="row"><span class="lbl">Foundation</span><input class="field dt num" type="number" inputmode="numeric" id="edF" min="0" max="600" value="' +
          Math.round(ef.f) +
          '" aria-label="Foundation minutes"></div>' +
          '<div class="row"><span class="lbl">Rotation</span><input class="field dt num" type="number" inputmode="numeric" id="edR" min="0" max="600" value="' +
          Math.round(ef.r) +
          '" aria-label="Rotation minutes"></div>' +
          '<div class="row"><span class="lbl">Application</span><span class="mut" id="edA">' +
          Math.max(0, tot - Math.round(ef.f) - Math.round(ef.r)) +
          ' min</span></div>'
        : '') +
      '</div>' +
      '<p class="foot">' +
      (ef
        ? 'Application is whatever’s left of the total.'
        : 'Split using the coach video’s length for each exercise and the levels you did. Application is whatever’s left.') +
      '</p>';
    if (E.songName)
      b +=
        '<div class="hdr">Application · ' +
        esc(E.songName) +
        '</div><div class="grp">' +
        ['Pitch', 'Tone', 'Ease']
          .map(
            (x) => '<div class="row"><span class="lbl">' + x + '</span>' + seg('erate', x, (E.rate || {})[x]) + '</div>'
          )
          .join('') +
        '</div>';
  }
  b +=
    '<div class="hdr">How it went</div>' +
    chipsHTML(wordList('how', HOW_WORDS), E.how, 'how') +
    noteBlock('edHowNote', E.howNote, 'Anything else about this ' + (song ? 'practice' : 'session'));
  b +=
    '<p class="foot">Changing the minutes or date updates your monthly totals, streak and last-done dates.</p><div style="margin-top:14px"><button class="cta" data-a="saveEdit">Save changes</button></div><button class="ghost" data-a="close">Cancel</button>';
  return sheetWrap('Edit ' + (song ? 'song practice' : 'session'), b);
}

/* ===== Render ===== */
function render(keepScroll) {
  const y = window.scrollY;
  closeSwipes();
  // keep what's typed in the lyrics editor, and leave editing when the song is no longer on screen
  if (U.sEdit === 'lyrics' && !SG.noSync && document.querySelector('.lyred')) applyLyrics();
  SG.noSync = false;
  if (U.sEdit && !(U.view === 'lyr' || songOpenInPane())) {
    U.sEdit = null;
    SG.word = null;
    SG.drag = null;
  }
  const v = U.view;
  $('app').innerHTML =
    v === 'log'
      ? scrLog()
      : v === 'ex'
        ? scrEx()
        : v === 'all'
          ? scrAll()
          : v === 'lyr'
            ? scrSongView()
            : v
              ? { found: scrFound, rot: scrRot, app: scrApp, song: scrSong }[v]()
              : {
                  today: scrToday,
                  history: scrHistory,
                  exercises: scrExercises,
                  songs: scrSongs,
                  settings: scrSettings,
                }[U.tab]();
  $('app').className =
    (isFlow(v) ? 'flow' : 'tabv') +
    (isFlow(v) || (!v && U.tab === 'settings') || v === 'log' || (v === 'ex' && !split()) ? ' narrow' : '');
  renderBar();
  renderSheet();
  renderDock();
  renderSide();
  if (keepScroll) window.scrollTo(0, y);
  placeKnobs();
  logReveal();
  songsAfter();
}
const rerender = () => render(true);
function go(fn) {
  const was = U.view;
  fn();
  if (rec && U.view !== was) {
    stopRec();
    toast('Recording stopped and saved');
  }
  window.scrollTo(0, 0);
  render();
}
var toastT = null;
function toast(t) {
  clearTimeout(toastT);
  const o = document.querySelector('.toast');
  if (o) o.remove();
  const el = document.createElement('div');
  el.className = 'toast glass';
  el.setAttribute('role', 'status');
  el.textContent = t;
  document.body.appendChild(el);
  toastT = setTimeout(() => el.remove(), 1900);
}

/* ===== Sliding knobs ===== */
function placeKnob(sg, animate) {
  const on = sg.querySelector('button.on'),
    k = sg.querySelector('.knob');
  if (!k) return;
  if (!on) {
    k.classList.remove('set');
    return;
  }
  const firstTime = !k.classList.contains('set');
  if (firstTime) {
    k.style.transition = 'none';
  }
  k.style.width = on.offsetWidth + 'px';
  k.style.transform = 'translateX(' + on.offsetLeft + 'px)';
  k.classList.add('set');
  if (firstTime) {
    void k.offsetWidth;
    k.style.transition = '';
  }
  if (animate) {
    k.classList.remove('squish');
    void k.offsetWidth;
    k.classList.add('squish');
  }
}
function placeKnobs(root) {
  (root || document).querySelectorAll('.seg').forEach((sg) => placeKnob(sg, false));
}
function segPick(el) {
  const sg = el.closest('.seg');
  sg.querySelectorAll('button').forEach((b) => {
    const on = b === el;
    b.classList.toggle('on', on);
    b.setAttribute('aria-pressed', on);
  });
  placeKnob(sg, true);
}
window.addEventListener('resize', () => placeKnobs());
