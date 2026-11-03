/* Vocal Sessions · ui.js
   Top bar, tab bar, sidebar and sheets; render(); the sliding picker knobs.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Chrome ===== */
const VIEWS = {
  found: ['Foundation', '1 of 3', null],
  rot: ['Rotation', '2 of 3', null], // Q19: one page, so Back always leaves the session (it keeps running)
  app: ['Application', '3 of 3', null],
  song: ['Song practice', '', null],
};
function pillText() {
  if (unstarted()) return 'Not started';
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
  } else if (U.view === 'set') {
    // 3.21 a Settings page: Back to the main list
    if (tabsMode) {
      bar.classList.add('tabsmode');
      $('barT').classList.add('tabs');
      $('barT').innerHTML = topTabs();
    } else $('barT').textContent = SET.title();
    $('barL').innerHTML =
      '<button class="circ glass" data-a="setPgBack" aria-label="' +
      (U.setFrom ? 'Back' : 'Back to Settings') +
      '">' +
      ICON.back +
      '</button>';
    $('barR').innerHTML = '';
  } else if (U.view === 'guide') {
    // Q04 the Marks guide's pages: Back to where the guide was opened (or the guide page before)
    if (tabsMode) {
      bar.classList.add('tabsmode');
      $('barT').classList.add('tabs');
      $('barT').innerHTML = topTabs();
    } else $('barT').textContent = MKG.title();
    $('barL').innerHTML = '<button class="circ glass" data-a="gdBack" aria-label="Back">' + ICON.back + '</button>';
    $('barR').innerHTML = '';
  } else if (U.view === 'coach') {
    if (tabsMode) {
      bar.classList.add('tabsmode');
      $('barT').classList.add('tabs');
      $('barT').innerHTML = topTabs();
    } else $('barT').textContent = 'Coach video';
    $('barL').innerHTML = '<button class="circ glass" data-a="coachBack" aria-label="Back">' + ICON.back + '</button>';
    $('barR').innerHTML = '';
  } else if (U.view === 'trk') {
    // 3.19 the track player: Back, the song's title, and the track's settings
    const b = TRACK.bar();
    $('barL').innerHTML = b.l;
    $('barT').innerHTML = b.t;
    $('barR').innerHTML = b.r;
    bar.classList.add('always');
  } else if (U.view === 'saved') {
    // Q21 the Session saved screen: no buttons, only Done on the page
    $('barT').textContent = 'Session saved';
    $('barL').innerHTML = '';
    $('barR').innerHTML = '';
  } else if (U.view === 'pat') {
    // Q32 the Patterns page: Back shrinks it into the pattern pill
    $('barT').textContent = 'Patterns';
    $('barL').innerHTML = '<button class="circ glass" data-a="patBack" aria-label="Back">' + ICON.back + '</button>';
    $('barR').innerHTML = '';
  } else if (U.view === 'ex') {
    const e = exById(U.exId);
    $('barT').textContent = e ? e.name : '';
    $('barL').innerHTML = '<button class="circ glass" data-a="exBack" aria-label="Back">' + ICON.back + '</button>';
    $('barR').innerHTML = '';
  } else if (U.view === 'ckCheck') {
    // 3.18 Song Clock: Check timing (Back, so swipe back works)
    const b = CLOCK.bar();
    $('barL').innerHTML = b.l;
    $('barT').innerHTML = b.t;
    $('barR').innerHTML = b.r;
    bar.classList.add('always');
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
      (unstarted()
        ? '<span class="pill glass wait" id="timer" role="status" aria-label="Not started. The clock starts with your first take">' +
          pillText() +
          '</span>'
        : '<button class="pill glass' +
          (X && X.paused ? ' paused' : '') +
          '" id="timer" data-a="clock" aria-label="Session time. Tap for the clock">' +
          pillText() +
          '</button>');
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
      { today: 'Today', history: 'Progress', exercises: 'Exercises', songs: 'Songs', settings: 'Settings', find: 'Search' }[U.tab];
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
  FIND.capsuleBtn() + // 3.22 Search: a circle at the end of the capsule
  '</nav>';
function renderSide() {
  const el = $('side');
  if (!MQ.wide.matches) {
    el.innerHTML = '';
    return;
  }
  el.innerHTML =
    '<div class="sbt">Vocal Sessions</div>' +
    FIND.sideRow() + // 3.22 Search: a row at the top
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
// 3.23 (Q08) the tab bar's collapse: the class lives on the row holding the bar, its pill and the search circle, so
// the bar fades and scales away towards the left while the pill grows in where the active tab was (transforms and
// opacity only). renderDock() keeps the row when nothing in it changed, so a collapse that's still moving carries on
let dockKey = null;
function setTabMin(b) {
  tabMin = !!b;
  const r = $('dock').querySelector('.dockrow');
  if (r) r.classList.toggle('min', tabMin);
}
// how far the pill sits from the active tab: it grows in from there (layout positions, so a collapsed bar's own
// scale doesn't count)
function tabPillPlace(row) {
  const nav = row.querySelector('.tabbar'),
    on = nav && nav.querySelector('button.on'),
    pill = row.querySelector('.tabpill');
  if (!pill) return;
  const x = on ? nav.offsetLeft + on.offsetLeft + on.offsetWidth / 2 - (pill.offsetLeft + pill.offsetWidth / 2) : 0;
  row.style.setProperty('--pill-x', Math.round(x) + 'px');
}
// a page has real room to scroll when it can move at least a third of the screen's height (Ivan, 26 Oct 2026); a
// shorter page keeps the full bar
const tabRoom = () => document.documentElement.scrollHeight - window.innerHeight >= window.innerHeight / 3;
function renderDock() {
  const html = renderDock1();
  if (html === null) {
    dockKey = null; // something else took the bar's place
    return;
  }
  const d = $('dock'),
    row = d.querySelector('.dockrow');
  if (html === dockKey && row) {
    row.classList.toggle('min', tabMin); // the same bar: only its state, easing if it changed
    tabPillPlace(row);
    return;
  }
  dockKey = html;
  d.innerHTML = tabMin ? html.replace('class="dockrow"', 'class="dockrow min"') : html; // drawn in its state, no replay
  tabPillPlace(d.querySelector('.dockrow'));
}
function renderDock1() {
  if (U.sheet) {
    $('dock').innerHTML = '';
    return null;
  }
  // recording a section: the recording bar takes the place of the tab bar (Q20: Application's card is its own)
  if (rec && rec.o && !rec.app) {
    $('dock').innerHTML =
      '<div class="recbar glass" role="group" aria-label="Recording"><span class="rectime"><span class="recdot" aria-hidden="true"></span><span id="recT">' +
      mmss(rec.t) +
      '</span></span><span class="meter" id="recMeter" aria-hidden="true">' +
      '<i></i>'.repeat(14) +
      '</span><button class="stopb" data-a="sgStop" aria-label="Stop recording"><i></i></button></div>';
    return null;
  }
  // 3.18 Song Clock: the play-along transport takes the place of the tab bar
  const ck = CLOCK.dock();
  if (ck) {
    $('dock').innerHTML = ck;
    return null;
  }
  // 3.19 the track player's transport
  const tk = TRACK.dock();
  if (tk) {
    $('dock').innerHTML = tk;
    return null;
  }
  // Recall: the hint capsule takes the place of the tab bar
  if (recallOn()) {
    $('dock').innerHTML = hintCapHTML();
    return null;
  }
  // Q32 the pattern player's dock on an exercise page; the Patterns page has none (only its tiles scroll)
  if (U.view === 'pat') {
    $('dock').innerHTML = '';
    return null;
  }
  if (PAT.onPage()) {
    const pd = PAT.dock();
    if (pd) {
      $('dock').innerHTML = pd;
      return null;
    }
  }
  // Q21 the Session saved screen: Done is on the page, and the tab bar comes back with Today
  if (U.view === 'saved') {
    $('dock').innerHTML = '';
    return null;
  }
  if (isFlow(U.view)) {
    // Q19: Foundation, Rotation and Application share one pinned button, with a hint above it (onepage.js)
    if (U.view !== 'song') {
      $('dock').innerHTML = OP.dock();
      return null;
    }
    $('dock').innerHTML =
      '<button class="cta glass tinted' +
      (unstarted() ? ' wait" aria-disabled="true' : '') +
      '" data-a="cta">' +
      (unstarted() ? 'Record a take first' : 'Save song practice') +
      '</button>';
    return null;
  }
  if (MQ.reg.matches) {
    $('dock').innerHTML = '';
    return null;
  }
  const songList = U.tab === 'songs' && !U.view;
  // iPhone: searching songs, selecting them or editing one takes the place of the tab bar
  if ((songList && (U.sFocus || U.sList)) || (U.view === 'lyr' && U.sEdit)) {
    $('dock').innerHTML = '';
    return null;
  }
  // never left collapsed at the top of a page, on Search, on a page too short to scroll, or in landscape (3.23)
  if (window.scrollY < 60 || U.tab === 'find' || !tabRoom() || !document.body.classList.contains('phone')) tabMin = false;
  const cur = tabOf(U.tab),
    curTab = TABS().find((t) => t[0] === cur);
  const nav =
    '<nav class="tabbar glass" aria-label="Tabs">' +
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
  // 3.23 (Q08) iPhone upright: the collapsed tab bar, a pill at the left edge holding the active tab's icon. Tapping it
  // brings the bar back
  const pill =
    document.body.classList.contains('phone') && curTab
      ? '<button class="tabpill glass" data-a="tab" data-v="' + cur + '" aria-label="Show tabs"><span>' + curTab[2] + '</span></button>'
      : '';
  // 3.22 Search: its own circle beside the tab bar, on every screen that has the tab bar
  return '<div class="dockrow">' + nav + pill + FIND.circle() + '</div>';
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
// 3.20: the backup's expected size with and without recordings (base64 adds about a third to each)
function exportSizes(P) {
  const rec = Math.round(TAKES.reduce((a, t) => a + (+t.size || 0), 0) * 1.34),
    base = P.noRec ? P.file.size : Math.max(0, P.file.size - rec),
    tx = (b) => (b < 1048576 ? 'under 1 MB' : 'about ' + Math.round(b / 1048576) + ' MB');
  return 'Without recordings: ' + tx(base) + '. With them: ' + tx(base + rec) + '.';
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
  else if (s === 'ckGrid') h = CLOCK.gridSheet();
  else if (s === 'recOver') h = recOverSheet(); // Q16: recording while the track plays
  else if (s === 'away') h = SCLOCK.awaySheet(); // Q22: "You were away N min"
  else if (s && /^trk/.test(s)) h = TRACK.sheet(s);
  else if (s === 'how' && X) {
    h =
      '<div class="scrim" data-a="close"><div class="sheet glass" role="dialog" aria-modal="true" aria-label="How did it go?"><div class="shead"><div class="grab"></div><div class="shtop"><button class="shbtn glass" data-a="skipHow" aria-label="Skip and save">' +
      ICON.x +
      '</button><span class="mut" style="font-size:var(--t-footnote)">' +
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
          '<div style="margin-top:14px"><button class="cta" data-a="close">Done</button></div>' +
          // Q20: the take's row is play, name, waveform and star; saving it and deleting it are here
          '<button class="ghost" data-a="shareTake" data-k="' +
          esc(t.id) +
          '">Save or share</button><button class="ghost" data-a="sheet" data-v="delTake" data-k="' +
          esc(t.id) +
          '" style="color:var(--danger)">Delete take</button>',
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
  else if (s === 'coachDel')
    h = confirmSheet(
      'Remove the coach video?',
      'It’s removed from this ' + deviceName() + '. Your file in Files stays, so you can add it again any time.',
      'Remove video',
      'coachDel'
    );
  else if (s === 'rescueDel')
    h = confirmSheet(
      'Delete the rescued copy?',
      'The copy of your data that couldn’t be read is deleted from this ' +
        deviceName() +
        '. Save it to Files first if you might want it. This can’t be undone.',
      'Delete copy',
      'rescueDel',
      U.sd && U.sd.k
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
        '"><span class="lbl">Exclude recordings<small>' +
        exportSizes(P) +
        ' Restoring it keeps the recordings already on the device.</small></span><span class="tgl" aria-checked="' +
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
  // Q22 the session clock (sclock.js): over a running session's step, or the Session saved screen it finished onto
  if (!h && U.clock && SCLOCK.can()) h = SCLOCK.html();
  const key = h ? (U.sheet ? U.sheet + '|' + (k || '') : 'clock') : '';
  const prev = $('layer').querySelector('.sheet, .clock'),
    st = prev ? prev.scrollTop : 0,
    swap = DET.inPlace(lastLayerKey, key), // Preparing backup becomes Backup ready in the same sheet
    oldH = swap && prev ? prev.getBoundingClientRect().height : 0,
    same = !!key && (key === lastLayerKey || swap);
  lastLayerKey = key;
  $('layer').innerHTML = h;
  if (same) {
    $('layer')
      .querySelectorAll('.scrim,.sheet,.clock,.clockscrim')
      .forEach((x) => x.classList.add('still'));
    const ns = $('layer').querySelector('.sheet, .clock');
    if (ns) ns.scrollTop = st;
    if (swap) DET.sheetSwap(oldH);
  }
  const open = !!h && !!U.sheet;
  if (open && !document.body.classList.contains('sheet-open'))
    $('app').parentNode.style.transformOrigin = '50% ' + (window.scrollY + 120) + 'px';
  document.body.classList.toggle('sheet-open', open);
  SCR.sheet(); // Q36 the sheet's screen ID and part names
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
      '<div class="calday" data-zday><div class="hdr">' +
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
      '</div></div>';
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
    '<div class="row" style="display:block;padding:12px 16px"><div style="display:flex;justify-content:space-between;font-size:var(--t-subhead)"><span>Time per step</span><span class="mut" style="font-size:var(--t-footnote)">' +
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
  // Q29: no ratings shown; an old session's rate stays in its saved data
  if (ss.songName)
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
      '</div>';
  if (done) b += '<button class="ghost" data-a="close">Done</button>';
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
            (takePlaying(t.id) ? ICON.pause : ICON.play) +
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
    '<p class="foot">Kept out of your focused goal and streak.</p>' +
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
  CLOCK.before(); // keeps what's typed in the song's title and artist fields (3.18)
  dropUnstarted();
  closeSwipes();
  // keep what's typed in the lyrics editor, and leave editing when the song is no longer on screen
  if (U.sEdit === 'lyrics' && !SG.noSync && document.querySelector('.lyred')) applyLyrics();
  SG.noSync = false;
  if (U.sEdit && !(U.view === 'lyr' || songOpenInPane())) {
    U.sEdit = null;
    SG.sel = null;
    SG.drag = null;
  }
  const v = U.view;
  COACH.park(); // the coach video waits outside #app while it's redrawn, so it keeps playing (coach.js)
  $('app').innerHTML =
    v === 'log'
      ? scrLog()
      : v === 'set'
        ? SET.page()
      : v === 'guide'
        ? MKG.page()
      : v === 'coach'
        ? COACH.page()
      : v === 'ex'
        ? scrEx()
      : v === 'pat'
        ? PAT.page() // Q32 the Patterns page (patterns.js)
        : v === 'all'
          ? scrAll()
          : v === 'lyr'
            ? scrSongView()
            : v === 'ckCheck'
              ? CLOCK.page()
            : v === 'saved'
              ? SAVED.page() // Q21 the Session saved screen (saved.js)
            : v === 'trk'
              ? TRACK.page()
            : v
              ? v === 'song'
                ? scrSong()
                : scrFlow()
              : {
                  today: scrToday,
                  history: scrHistory,
                  exercises: scrExercises,
                  songs: scrSongs,
                  settings: scrSettings,
                  find: FIND.page,
                }[U.tab]();
  $('app').className =
    (isFlow(v) ? 'flow' : 'tabv') +
    (isFlow(v) ||
    (!v && U.tab === 'settings') ||
    (!v && U.tab === 'find') ||
    v === 'set' ||
    v === 'guide' ||
    v === 'log' ||
    v === 'coach' ||
    v === 'ckCheck' ||
    v === 'trk' ||
    v === 'saved' ||
    v === 'pat' ||
    (v === 'ex' && !split())
      ? ' narrow'
      : '');
  renderBar();
  renderSheet();
  const dk = DET.dockKids();
  renderDock();
  renderSide();
  if (keepScroll) window.scrollTo(0, y);
  placeKnobs();
  edgeFades();
  if (HINT.on && !HINT.on.isConnected) hintHide(); // Q10 a hover hint never outlives its button
  logReveal();
  songsAfter();
  CLOCK.after(); // 3.18 Song Clock: the play-along view, the current line when paused, the wake lock
  TRACK.after(); // 3.19 the track player: its waveform, and letting go of a deleted song's track
  TAKE.after(); // 3.20 the takes sheet: the expanded take's waveform and the field being typed in
  FIND.after(); // 3.22 Search: the field focused when the page is opened from its circle
  MKG.after(); // Q04 the peek card goes with its marks sheet
  OP.after(); // Q19 the one-page session: the coach video cued, the pull put back
  APPL.after(); // Q20 Application: the page dims around its card while it records
  SCLOCK.after(); // Q22: asks about time away once nothing's in the way; the screen kept on while a session runs
  PAT.after(); // Q32 the pattern player: stops when its page goes, the playhead carries on after a redraw
  fwUpdate();
  DET.dockSwap(dk);
  DET.play();
  DET.after();
  SCR.screen(); // Q36 the screen's ID and part names, from the register (register.js)
}
const rerender = () => render(true);

/* ===== Screen IDs (Q36) =====
   Each screen's permanent ID comes from the register (SCREENS, register.js), looked up by its code key. render() and
   renderSheet() stamp it on the page as data-screen (#app for the screen, the sheet or clock for what's over it), and
   the parts the register names get data-name. Drawn outside render(): the floating window (window.js), the peek card
   (guide.js) and the launch screen (index.html, set at boot). A screen missing from the register shows VS-??? and
   warns once in the console; the tests fail on it. Settings › Appearance › Show screen IDs (vocalLook.ids) puts the
   IDs in a small grey label in the top corner, below the bar. See MAINTAINING › Screen IDs. */
const SCR = (() => {
  const BY = {};
  SCREENS.screens.forEach((s) => (BY[s.key] = s));
  const warned = {};
  // the code key of the screen render() draws: see register.js
  function viewKey() {
    const v = U.view;
    if (!v) return 'tab:' + U.tab;
    if (v === 'set') return SET.PAGES.includes(U.setPg) ? 'view:set/' + U.setPg : 'tab:settings'; // SET.page() falls back to the main list
    if (v === 'guide') return 'view:guide/' + (U.gPg === 'how' ? 'how' : MK_DEF[U.gPg] ? 'mark' : 'home');
    return 'view:' + v;
  }
  function entry(key) {
    const s = BY[key];
    if (s && s.status === 'Live') return s;
    if (!warned[key]) {
      warned[key] = 1;
      console.warn('No screen ID in js/register.js for ' + key);
    }
    return null;
  }
  const id = (key) => (entry(key) || { id: 'VS-???' }).id;
  // data-name on the register's parts for this screen (and the shared ones) inside these elements
  function name(s, roots) {
    const parts = SCREENS.shared.concat(s ? s.parts : []);
    roots.forEach((r) => {
      if (!r) return;
      parts.forEach((p) => r.querySelectorAll(p.sel).forEach((el) => (el.dataset.name = p.name)));
    });
  }
  function screen() {
    const key = viewKey(),
      s = entry(key);
    $('app').dataset.screen = s ? s.id : 'VS-???';
    name(s, [$('app'), $('bar'), $('dock'), $('side')]);
    label();
  }
  // the sheet (or the session clock) over the screen: renderSheet()
  function sheet() {
    const el = $('layer').querySelector('.sheet, .clock');
    if (el) {
      const s = entry(U.sheet ? 'sheet:' + U.sheet : 'overlay:clock');
      el.dataset.screen = s ? s.id : 'VS-???';
      name(s, [el]);
    }
    label();
  }
  // something drawn outside render(): the floating window, the peek card, the launch screen
  function mark(el, key) {
    if (!el) return;
    const s = entry(key);
    el.dataset.screen = s ? s.id : 'VS-???';
    name(s, [el]);
  }
  // Settings › Appearance › Show screen IDs: the screen's ID, then the open sheet's
  function label() {
    let el = $('scrid');
    if (!SET.idsOn()) {
      if (el) el.remove();
      return;
    }
    if (!el) {
      el = document.createElement('div');
      el.id = 'scrid';
      el.setAttribute('aria-hidden', 'true');
      document.body.appendChild(el);
    }
    const over = $('layer').querySelector('.sheet[data-screen], .clock[data-screen]');
    el.textContent = $('app').dataset.screen + (over ? ' · ' + over.dataset.screen : '');
  }
  return { viewKey, id, screen, sheet, mark, label, BY };
})();

function go(fn) {
  const was = U.view,
    z = ZOOM.before(); // 3.15: a card tapped (or Back) zooms between the screens
  fn();
  if (typeof FW !== 'undefined') FW.shut = false; // 3.20: after ✕, other windows may show again on the next screen
  if (rec && U.view !== was) {
    stopRec();
    toast('Recording stopped and saved');
  }
  window.scrollTo(0, 0);
  render();
  COACH.stepped(was); // a session's step changing cues the coach video to the new step, paused
  ZOOM.after(z); // a card zoom or Back into a card (zoom.js)
}
var toastT = null;
// cls 'long' (Q11) lets a longer message wrap onto a second line instead of being cut off
function toast(t, ms, cls) {
  clearTimeout(toastT);
  const o = document.querySelector('.toast');
  if (o) o.remove();
  const el = document.createElement('div');
  el.className = 'toast glass' + (cls ? ' ' + cls : '');
  el.setAttribute('role', 'status');
  el.textContent = t;
  document.body.appendChild(el);
  toastT = setTimeout(() => el.remove(), ms || 1900);
  return el;
}
// a toast with one button (Q11: Retry), in the same style as Song Clock's Undo toasts; gone() runs if it times out
function toastBtn(t, label, fn, ms, gone) {
  const el = toast(t, ms || 4500, 'ckundo long');
  const b = document.createElement('button');
  b.className = 'ckub';
  b.textContent = label;
  b.addEventListener('click', (e) => {
    e.stopPropagation();
    clearTimeout(toastT);
    el.remove();
    fn();
  });
  el.appendChild(b);
  if (gone) {
    clearTimeout(toastT);
    toastT = setTimeout(() => {
      el.remove();
      gone();
    }, ms || 4500);
  }
  return el;
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

/* ===== Q10 Sideways scroll hints =====
   A row that scrolls sideways (marked data-edge-fade) gets a soft fade on whichever edge has more behind it:
   the right at the start, both in the middle, the left at the end, and none when everything fits. */
function edgeFade(el) {
  const max = el.scrollWidth - el.clientWidth,
    x = Math.abs(el.scrollLeft);
  el.classList.toggle('fadel', max > 1 && x > 1);
  el.classList.toggle('fader', max > 1 && x < max - 1);
}
function edgeFades(root) {
  (root || document).querySelectorAll('[data-edge-fade]').forEach(edgeFade);
}
document.addEventListener(
  'scroll',
  (e) => {
    const el = e.target;
    if (el && el.nodeType === 1 && el.hasAttribute('data-edge-fade')) edgeFade(el);
  },
  { passive: true, capture: true }
);
window.addEventListener('resize', () => edgeFades());
