/* Vocal Sessions · events.js
   Taps and typing: swipe to delete, no zooming, and every button action.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Swipe to delete ===== */
let swT = null,
  swOpen = null,
  swJustMoved = 0;
function closeSwipes(except) {
  document.querySelectorAll('.sw.open').forEach((s) => {
    if (s !== except) {
      s.classList.remove('open');
      s.querySelector('.fg').style.transform = '';
    }
  });
  if (!except) swOpen = null;
}
document.addEventListener(
  'touchstart',
  (e) => {
    const s = e.target.closest('.sw');
    if (swOpen && swOpen !== s) closeSwipes();
    if (!s) return;
    const t = e.touches[0];
    swT = { s, x: t.clientX, y: t.clientY, dx: 0, base: s.classList.contains('open') ? -88 : 0, lock: null };
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (!swT) return;
    const t = e.touches[0],
      dx = t.clientX - swT.x,
      dy = t.clientY - swT.y;
    if (swT.lock === null) {
      if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
      swT.lock = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
    }
    if (swT.lock !== 'x') return;
    swT.dx = dx;
    swT.s.classList.add('dragging');
    const x = Math.max(-120, Math.min(0, swT.base + dx));
    swT.s.querySelector('.fg').style.transform = 'translateX(' + x + 'px)';
  },
  { passive: true }
);
document.addEventListener('touchend', () => {
  if (!swT) return;
  const s = swT.s;
  s.classList.remove('dragging');
  if (swT.lock === 'x') {
    swJustMoved = Date.now();
    const x = swT.base + swT.dx;
    const open = x < -44;
    s.classList.toggle('open', open);
    s.querySelector('.fg').style.transform = open ? 'translateX(-88px)' : '';
    swOpen = open ? s : null;
  }
  swT = null;
});

/* ===== No zooming (iOS ignores user-scalable=no, so block pinch and double-tap here) ===== */
['gesturestart', 'gesturechange', 'gestureend'].forEach((t) =>
  document.addEventListener(t, (e) => e.preventDefault(), { passive: false })
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (e.touches.length > 1) e.preventDefault();
  },
  { passive: false }
);
// double-tap zoom is turned off by touch-action:manipulation in the CSS, which keeps quick taps working

/* ===== Events ===== */
$('importIn').addEventListener('change', (e) => {
  const f = e.target.files && e.target.files[0];
  e.target.value = '';
  if (f) readBackupFile(f);
});
document.addEventListener('click', (e) => {
  if (ZOOM.swallow(e)) {
    e.preventDefault();
    return;
  }
  const el = e.target.closest('[data-a]');
  if (Date.now() - swJustMoved < 350 && !(el && el.classList.contains('swdel'))) {
    e.preventDefault();
    return;
  }
  if (swOpen && !(el && el.classList.contains('swdel')) && !e.target.closest('.scrim')) {
    const inOpen = e.target.closest('.sw') === swOpen;
    closeSwipes();
    if (inOpen) {
      e.preventDefault();
      return;
    }
  }
  if (!el) return;
  if (el.classList.contains('scrim') && e.target !== el) return;
  ZOOM.tap(el); // a card (data-zk) zooms into the page it opens; a Back button shrinks the page back into its card
  const a = el.dataset.a,
    v = el.dataset.v,
    k = el.dataset.k;
  const here = () => (U.sheet ? { sheet: U.sheet, sd: U.sd } : null);
  switch (a) {
    case 'tab':
      U.clock = false;
      if (sgTabTap(v)) break;
      // the collapsed bar's pill (or any tab while it's collapsed) brings the bar back first (3.23, Q08)
      if (tabMin && !MQ.reg.matches && $('dock').querySelector('.dockrow')) {
        setTabMin(false);
        break;
      }
      go(() => {
        U.tab = v;
        U.view = null;
      });
      break;
    case 'openSettings':
      U.clock = false;
      go(() => {
        U.tab = 'settings';
        U.view = null;
      });
      break;
    case 'setBack':
      go(() => {
        U.tab = 'today';
        U.view = null;
      });
      break;
    case 'openCal':
      U.calMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
      U.calDay = null;
      U.sheet = 'calendar';
      U.sd = {};
      rerender();
      DET.calendarIn();
      break;
    case 'calMove': {
      const m = U.calMonth;
      U.calMonth = new Date(m.getFullYear(), m.getMonth() + +v, 1);
      U.calDay = null;
      rerender();
      DET.calendarIn();
      break;
    }
    case 'calDay': {
      const r = el.getBoundingClientRect();
      U.calDay = U.calDay === +v ? null : +v;
      rerender();
      if (U.calDay) ZOOM.dayIn(r); // the day's sessions grow out of the day
      break;
    }
    case 'calSession':
      U.sheet = D.songSessions.some((x) => x.id === k) ? 'songSession' : 'session';
      U.sd = { k, ret: 'calendar' };
      rerender();
      break;
    case 'start':
      if (X)
        return toast(isSong() ? 'Save or discard your song practice first' : 'Finish or discard your session first');
      newSession();
      go(() => {
        U.view = 'found';
      });
      break;
    case 'songStart':
      // 3.20 one song list: Today's Song practice card switches to the Songs tab itself (a tab switch, no zoom).
      // Song practice in progress carries on from its song's page
      if (isSong() && X.start && songById(X.song)) {
        openSong(X.song);
        break;
      }
      go(() => {
        U.tab = 'songs';
        U.view = null;
      });
      break;
    case 'resume':
      go(() => {
        U.view = isSong() ? 'song' : X.fEnd ? (X.rEnd ? 'app' : 'rot') : 'found';
      });
      break;
    case 'discardYes':
      if (rec) stopRec();
      stopPlayback();
      X = null;
      saveDraft();
      U.clock = false;
      U.sheet = null;
      if (U.view)
        go(() => {
          U.view = null;
          U.tab = 'today';
        });
      else rerender();
      break;
    case 'exit':
      U.clock = false;
      go(() => {
        U.view = null;
        U.tab = 'today';
      });
      break;
    case 'view':
      go(() => {
        U.view = v;
      });
      break;
    case 'openEx':
      if (split()) {
        const was = U.tab;
        U.exId = k;
        U.exTab = 'summary';
        if (was !== 'exercises')
          go(() => {
            U.tab = 'exercises';
            U.view = null;
          });
        else rerender();
        break;
      }
      go(() => {
        U.prevTab = U.tab;
        U.view = 'ex';
        U.exId = k;
        U.exTab = 'summary';
      });
      break;
    case 'openLog':
      LOGSEEN.clear();
      fetchChangelog();
      go(() => {
        U.prevTab = U.tab;
        U.view = 'log';
        U.logPick = null;
        U.logDrawn = false;
      });
      break;
    case 'logRetry':
      LOG_STATE = 'idle';
      fetchChangelog();
      rerender();
      break;
    case 'logBack':
      go(() => {
        U.view = null;
        U.tab = 'settings';
      });
      break;
    case 'logMode':
      segPick(el);
      U.logAll = v === 'all';
      setTimeout(rerender, 180);
      break;
    case 'logMore': {
      const i = U.logOpen.indexOf(k);
      if (i < 0) U.logOpen.push(k);
      else U.logOpen.splice(i, 1);
      const card = el.closest('.tl-item'),
        top = card ? card.getBoundingClientRect().top : 0;
      rerender();
      const nc = $(logId(k));
      if (nc) {
        if (i >= 0) window.scrollBy(0, nc.getBoundingClientRect().top - top);
      }
      break;
    }
    case 'lgpick':
      U.logPick = U.logPick === +k ? null : +k;
      updateLogCard();
      break;
    case 'lgjump': {
      const t = $(logId(k));
      if (t) {
        t.classList.add('seen');
        LOGSEEN.add(t.dataset.r);
        const y = t.getBoundingClientRect().top + window.scrollY - 110;
        window.scrollTo({
          top: y,
          behavior: MOTION.reduced() ? 'auto' : 'smooth',
        });
        const c = t.querySelector('.tl-card');
        setTimeout(() => {
          c.classList.add('flash');
          setTimeout(() => c.classList.remove('flash'), 1200);
        }, 350);
      }
      break;
    }
    case 'exBack':
      go(() => {
        U.view = null;
        U.tab = U.prevTab || 'exercises';
      });
      break;
    case 'exTab':
      segPick(el);
      U.exTab = v;
      setTimeout(() => {
        rerender();
        if (v === 'history') DET.exLine();
      }, 180);
      break;
    case 'histTab':
      segPick(el);
      U.histTab = v;
      setTimeout(() => {
        rerender();
        DET.listIn();
      }, 180);
      break;
    case 'flv':
      X.f[k] = +v;
      saveDraft();
      segPick(el);
      break;
    case 'rlv':
      X.rot[k] = +v;
      saveDraft();
      segPick(el);
      break;
    case 'rate':
      X.rate[k] = +v;
      saveDraft();
      segPick(el);
      break;
    case 'eflv':
      if (E) {
        E.f = E.f || {};
        E.f[k] = +v;
        segPick(el);
      }
      break;
    case 'erlv':
      if (E) {
        E.rot[k] = +v;
        segPick(el);
      }
      break;
    case 'erate':
      if (E) {
        E.rate = E.rate || {};
        E.rate[k] = +v;
        segPick(el);
      }
      break;
    case 'tog':
      if (k in X.rot) delete X.rot[k];
      else X.rot[k] = 0;
      saveDraft();
      rerender();
      break;
    case 'song':
      if (rec) return toast('Stop recording first');
      stopPlayback();
      X.song = k;
      saveDraft();
      rerender();
      break;
    case 'rec':
      rec ? stopRec() : startRec();
      break;
    case 'playTake':
      playTake(k);
      break;
    case 'shareTake':
      shareTake(k);
      break;
    case 'star':
      (async () => {
        const t = TAKES.find((x) => x.id === k);
        if (!t) return;
        t.star = !t.star;
        await putTake(t);
        await refreshTakes();
        rerender();
        if (t.star) DET.starPop(document.querySelector('#layer .ibtn.star.on[data-k="' + k + '"], .ibtn.star.on[data-k="' + k + '"]'));
      })();
      break;
    case 'cta':
      if (U.view === 'found') {
        if (FOUND.some((x) => !(x.id in X.f))) return toast('Set a level or Skip for each exercise');
        U.sheet = 'confirmF';
        rerender();
      } else if (U.view === 'rot') {
        const ks = Object.keys(X.rot);
        if (!ks.length) return toast('Pick at least one exercise');
        if (ks.some((i) => !X.rot[i])) return toast('Set a level for each exercise you picked');
        X.rEnd = Date.now();
        X.rE = elapsedSec();
        saveDraft();
        go(() => {
          U.view = 'app';
        });
      } else if (U.view === 'app') {
        if (rec) return toast('Stop recording first');
        stopPlayback();
        startFinish();
      } else if (U.view === 'song') {
        if (!X.start)
          return toast(X.song ? 'Your practice starts with your first take' : 'Pick a song, then record a take');
        if (!X.song) return toast('Pick a song first');
        if (rec) return toast('Stop recording first');
        stopPlayback();
        startFinish();
      }
      break;
    case 'confirmF':
      X.fEnd = Date.now();
      X.fE = elapsedSec();
      saveDraft();
      U.sheet = null;
      go(() => {
        U.view = 'rot';
      });
      break;
    case 'longOk': {
      const m = Math.round(+($('longMins') || {}).value || 0);
      const max = Math.round(elapsedSec() / 60);
      if (!(m >= 1)) return toast('Enter the minutes you practised');
      X.minsOverride = Math.min(m, max);
      saveDraft();
      U.sheet = 'how';
      rerender();
      break;
    }
    case 'longAll':
      X.minsOverride = null;
      saveDraft();
      U.sheet = 'how';
      rerender();
      break;
    case 'saveHow':
      finishSession();
      break;
    case 'skipHow':
      X.how = [];
      X.howNote = '';
      finishSession();
      break;
    case 'clock':
      if (!X || !X.start) break;
      U.clock = true;
      rerender();
      break;
    case 'clockClose': {
      const c = document.querySelector('.clock');
      if (c) {
        c.classList.remove('still');
        c.classList.add('out');
        const sc = document.querySelector('.clockscrim');
        if (sc) sc.style.opacity = 0;
      }
      setTimeout(() => {
        U.clock = false;
        rerender();
      }, 260);
      break;
    }
    case 'pauseToggle':
      if (!X || !X.start) break;
      togglePause();
      rerender();
      break;
    /* 3.16 the coach video (coach.js) */
    case 'openCoach':
      COACH.open(k);
      break;
    case 'coachBack':
      COACH.back();
      break;
    case 'coachSettings':
      COACH.toSettings();
      break;
    case 'coachAdd':
      $('coachIn').click();
      break;
    case 'coachDel':
      COACH.remove();
      break;
    case 'coachPlay':
      COACH.toggle();
      break;
    case 'coachFS':
      COACH.fullscreen();
      break;
    case 'coachSkip':
      COACH.skip(+v);
      break;
    case 'coachLv':
      segPick(el);
      COACH.setLevel(+v);
      break;
    case 'coachLoop':
      COACH.toggleLoop();
      break;
    case 'coachSpeed':
      COACH.cycleSpeed();
      break;
    case 'coachEx':
      COACH.cue(k, COACH.level(k), true);
      break;
    case 'coachShow':
      COACH.show();
      break;
    case 'coachStepEx':
      COACH.stepMove(+v);
      break;
    case 'coachX':
    case 'fwX':
      fwClose(); // 3.20: ✕ on the floating window, for every kind of sound
      break;
    case 'fwOpen': {
      const fk = fwKindNow();
      if (fk) fk.open();
      break;
    }
    case 'fwToggle': {
      const fk = fwKindNow();
      if (!fk) break;
      FW.winAt = Date.now(); // 3.20: paused from the window, so the window stays
      fk.toggle();
      fwUpdate();
      break;
    }
    case 'exNote':
      U.noteOpen = null;
      {
        const r = here();
        U.sheet = 'exNote';
        U.sd = { k, src: el.dataset.src || '', ret: r };
      }
      rerender();
      break;
    case 'takeNote':
      U.noteOpen = null;
      {
        const r = here();
        U.sheet = 'takeNote';
        U.sd = { k, ret: r };
      }
      rerender();
      break;
    case 'xnClear': {
      const T = noteTarget();
      if (T && T.xn) delete T.xn[U.sd.k];
      if (T === X) saveDraft();
      closeSheet();
      break;
    }
    case 'wTog': {
      const arr = selArr();
      if (!arr) break;
      const i = arr.indexOf(v);
      if (i < 0) arr.push(v);
      else arr.splice(i, 1);
      el.classList.toggle('on', i < 0);
      el.setAttribute('aria-pressed', i < 0);
      if (U.sheet === 'how' || (U.sheet === 'exNote' && noteTarget() === X)) saveDraft();
      break;
    }
    case 'addWord': {
      const r = here();
      U.sheet = 'addWord';
      U.sd = { key: k, ret: r };
      rerender();
      setTimeout(() => {
        const i = $('wordIn');
        if (i) i.focus();
      }, 250);
      break;
    }
    case 'saveWord': {
      const w = (($('wordIn') || {}).value || '').trim().replace(/\s+/g, ' ');
      const key = U.sd.key,
        r = U.sd.ret;
      if (w) {
        D.words[key] = D.words[key] || [];
        if (!D.words[key].includes(w)) D.words[key].push(w);
        save();
      }
      if (r) {
        U.sheet = r.sheet;
        U.sd = r.sd || {};
      } else U.sheet = null;
      if (w) {
        const arr = selArr();
        if (arr && !arr.includes(w)) arr.push(w);
        if (U.sheet === 'how' || (U.sheet === 'exNote' && noteTarget() === X)) saveDraft();
        toast('Saved for next time');
      }
      rerender();
      break;
    }
    case 'openNote':
      U.noteOpen = k;
      rerender();
      setTimeout(() => {
        const t = $(k);
        if (t) {
          t.focus();
          t.scrollIntoView({ block: 'center', behavior: 'smooth' });
        }
      }, 80);
      break;
    case 'editSess': {
      const ss = findSess(k);
      if (!ss) break;
      E = JSON.parse(JSON.stringify(ss));
      E.kind = ss.kind || 'focused';
      E.dateStr = isoDay(new Date(ss.date));
      E.how = E.how || [];
      E.howNote = E.howNote || '';
      E.xn = E.xn || {};
      if (E.kind !== 'song' && (!E.split || E.mixed)) {
        E.mixed = true;
      }
      const r = here();
      U.noteOpen = null;
      U.sheet = 'edit';
      U.sd = { k, ret: r };
      rerender();
      break;
    }
    case 'saveEdit':
      if (E) {
        const m = +E.mins;
        if (!(m >= 1 && m <= 600)) {
          toast('Enter minutes between 1 and 600');
          break;
        }
        if (E.kind !== 'song' && !E.mixed && E.split) {
          const f = +E.split.f,
            r = +E.split.r;
          if (!(f >= 0 && r >= 0) || f + r > m) {
            toast('Foundation and Rotation can’t add up to more than the total');
            break;
          }
        }
        applyEdit();
        toast('Changes saved');
      }
      closeSheet();
      break;
    case 'sheet':
      if ((v === 'session' || v === 'songSession') && split() && U.view === 'all' && !U.sheet) {
        U.sel = k;
        rerender();
        break;
      }
      U.sheet = v;
      U.sd = { k };
      rerender();
      break;
    case 'peekLen':
      segPick(el);
      D.prefs = D.prefs || {};
      D.prefs.peek = +v;
      save();
      break;
    case 'goalOpen':
      // the weekly goal opens Progress on this week's focused sessions (song practice never counts towards it)
      U.histTab = 'sessions';
      U.range = 'W';
      U.roff = 0;
      U.pick = null;
      U.sheet = null;
      U.clock = false;
      go(() => {
        U.tab = 'history';
        U.view = null;
      });
      break;
    case 'openAll':
      U.histTab = v === 'songs' ? 'songs' : 'sessions';
      U.sel = null;
      U.sheet = null;
      go(() => {
        U.prevTab = U.tab;
        U.tab = 'history';
        U.view = 'all';
      });
      break;
    case 'allBack':
      go(() => {
        U.view = null;
        U.tab = U.prevTab && U.prevTab !== 'history' ? U.prevTab : 'history';
      });
      break;
    case 'prange':
      segPick(el);
      U.range = v;
      U.roff = 0;
      U.pick = null;
      setTimeout(() => updatePcard({ dir: 0 }), 150);
      break;
    case 'pnav':
      U.roff = Math.min(0, (U.roff || 0) + +v);
      U.pick = null;
      updatePcard({ dir: +v < 0 ? -1 : 1 });
      break;
    case 'esplit':
      if (E) {
        segPick(el);
        if (v === 'timed') {
          const sp = E.split && !E.mixed ? E.split : vidSplit(E);
          E.split = { f: Math.round(sp.f), r: Math.round(sp.r), a: 0 };
          E.mixed = false;
        } else {
          E.mixed = true;
        }
        setTimeout(rerender, 160);
      }
      break;
    case 'close':
      closeSheet();
      break;
    case 'focus':
      document.querySelectorAll('#focusChips .chip').forEach((c) => c.classList.toggle('on', c === el));
      break;
    case 'saveEx': {
      const n = ($('exName').value || '').trim(),
        err = $('exErr');
      if (!n) {
        err.textContent = 'Enter a name';
        err.hidden = false;
        return;
      }
      const f = (document.querySelector('#focusChips .chip.on') || {}).dataset;
      const id = 'c_' + Date.now().toString(36);
      DET.arm();
      D.custom.push({ id, name: n, focus: f ? f.v : 'custom', what: ($('exWhat').value || '').trim() });
      save();
      if (X && U.view === 'rot') {
        X.rot[id] = 0;
        saveDraft();
      }
      U.sheet = null;
      rerender();
      toast('Exercise added');
      break;
    }
    case 'saveWhat': {
      const e = D.custom.find((x) => x.id === k);
      if (e) {
        e.what = ($('whatIn').value || '').trim();
        save();
      }
      U.sheet = null;
      rerender();
      break;
    }
    case 'saveSong': {
      const n = ($('songIn').value || '').trim(),
        err = $('songErr');
      if (!n) {
        err.textContent = 'Enter a song name';
        err.hidden = false;
        return;
      }
      const id = 'g_' + Date.now().toString(36);
      D.songs.push({ id, name: titleCase(n), artist: '', added: Date.now(), pinned: false });
      save();
      if (X && (U.view === 'app' || U.view === 'song')) {
        X.song = id;
        saveDraft();
      }
      U.sheet = null;
      rerender();
      toast('Song added');
      break;
    }
    case 'delEx':
      DET.arm();
      D.custom = D.custom.filter((x) => x.id !== k);
      save();
      if (X && k in X.rot) {
        delete X.rot[k];
        saveDraft();
      }
      if (U.view === 'ex' && U.exId === k) {
        U.view = null;
      }
      U.sheet = null;
      rerender();
      toast('Exercise deleted');
      break;
    case 'delSong':
      (async () => {
        D.songs = D.songs.filter((x) => x.id !== k);
        save();
        for (const t of TAKES.filter((t) => t.songId === k)) await delTake(t.id);
        if (X && X.song === k) {
          X.song = null;
          saveDraft();
        }
        await refreshTakes();
        U.sheet = null;
        rerender();
        toast('Song deleted');
      })();
      break;
    case 'delTake':
      (async () => {
        await TAKE.del(k); // 3.20: its name, comments and waveform go with it
        await refreshTakes();
        U.sheet = null;
        rerender();
        toast('Take deleted');
      })();
      break;
    case 'delSession':
      DET.arm();
      deleteSession(k);
      U.sheet = null;
      rerender();
      toast('Session deleted');
      break;
    case 'delSongSess':
      DET.arm();
      D.songSessions = D.songSessions.filter((x) => x.id !== k);
      save();
      U.sheet = null;
      rerender();
      toast('Song practice deleted');
      break;
    case 'clearRec':
      (async () => {
        stopPlayback();
        await clearTakes();
        await refreshTakes();
        U.sheet = null;
        rerender();
        toast('Recordings deleted');
      })();
      break;
    case 'resetMonth':
      D.months[monthKey()] = 0;
      save();
      U.sheet = null;
      rerender();
      toast('This month reset');
      break;
    case 'resetAll':
      (async () => {
        stopPlayback();
        await clearTakes();
        await clearUndo();
        UNDO = null;
        try {
          localStorage.removeItem(BLOG);
        } catch (e) {}
        D = { v2: true };
        migrate();
        save();
        X = null;
        saveDraft();
        await refreshTakes();
        U = freshU();
        render();
        toast('All data deleted');
      })();
      break;
    case 'copy': {
      const ss = findSess(k);
      if (ss) copyText(togglLines(ss));
      break;
    }
    case 'exportPrep':
      prepareExport();
      break;
    case 'exportSave':
      saveExport();
      break;
    case 'exportNoRec':
      if (pendingExport && !pendingExport.busy) prepareExport(!pendingExport.noRec, true);
      break;
    case 'importPick':
      pickMode = 'import';
      $('importIn').click();
      break;
    case 'checkPick':
      pickMode = 'check';
      $('importIn').click();
      break;
    case 'bkToImport':
      U.sd.mode = 'import';
      rerender();
      {
        const sh = document.querySelector('.sheet');
        if (sh) sh.scrollTop = 0;
      }
      break;
    case 'importYes':
      restoreImport();
      break;
    case 'undoYes':
      undoRestore();
      break;
    case 'persistAsk':
      checkPersist(true).then((r) => {
        rerender();
        toast(r === true ? 'Storage protection is on' : 'iOS didn’t turn it on this time');
      });
      break;
    case 'bkGuideFrom':
      U.sheet = 'bkGuide';
      U.sd = { ret: 'exportReady' };
      rerender();
      break;
    // Q11: the rescued copy of saved data that couldn't be read (Settings › Backup)
    case 'rescueSave': {
      const c = SAFE.rescued().find((x) => x.key === k);
      if (!c) break;
      const name = ('Vocal Sessions rescued data · ' + fileDate(new Date(c.at))).replace(/[\/\\:*?"<>|]/g, '-') + '.txt';
      shareFile(new File([c.text], name, { type: 'text/plain' })).then((r) => {
        if (r !== 'cancelled') toast(r === 'shared' ? 'Rescued copy saved' : 'Rescued copy downloaded');
      });
      break;
    }
    case 'rescueDel':
      SAFE.del(k).then(
        () => {
          U.sheet = null;
          rerender();
          toast('Rescued copy deleted');
        },
        () => toast('Couldn’t delete the copy')
      );
      break;
    case 'saveReadme':
      shareFile(new File([readmeText()], README_NAME, { type: 'text/plain' })).then((r) => {
        if (r !== 'cancelled') toast(r === 'shared' ? 'Read-me saved' : 'Read-me downloaded');
      });
      break;
    default:
      if (SG_ACT[a]) SG_ACT[a](el, v, k, e);
  }
});
// anim ({dir}) is passed only when the range or period changes, so the bars ripple; scrubbing never passes it
function updatePcard(anim) {
  const a = $('pcard'),
    b = $('pbrk');
  if (!a && !b) return;
  const was = anim ? DET.bars() : null;
  const c = pcardHTML();
  if (a) a.innerHTML = c.card;
  if (b) b.innerHTML = c.brk;
  if (anim) DET.pcardIn(was, anim.dir);
}
// tap a bar, or slide a finger across them like Health
function pickAt(x, y) {
  const el = document.elementFromPoint(x, y),
    b = el && el.closest && el.closest('[data-pick]');
  if (!b) return;
  const i = +b.dataset.pick;
  if (i !== U.pick) {
    U.pick = i;
    updatePcard();
  }
}
let pickT = 0;
document.addEventListener('pointerdown', (e) => {
  if (e.target.closest && e.target.closest('#pchart')) {
    const b = e.target.closest('[data-pick]');
    if (b) {
      const i = +b.dataset.pick;
      U.pick = U.pick === i && e.pointerType === 'mouse' ? null : i;
      pickT = Date.now();
      updatePcard();
    }
  }
});
document.addEventListener('pointermove', (e) => {
  if (U.pick == null || !(e.buttons || e.pointerType === 'touch')) return;
  if (e.target.closest && e.target.closest('#pchart')) pickAt(e.clientX, e.clientY);
});
document.addEventListener(
  'click',
  (e) => {
    if (
      U.pick != null &&
      Date.now() - pickT > 400 &&
      e.target.isConnected &&
      !(e.target.closest && e.target.closest('#pcard'))
    ) {
      U.pick = null;
      updatePcard();
    }
  },
  true
);
document.addEventListener('input', (e) => {
  const t = e.target,
    id = t.id,
    v = t.value;
  if ((id === 'edF' || id === 'edR') && E && E.split) {
    E.split[id === 'edF' ? 'f' : 'r'] = v;
    const a = $('edA');
    if (a)
      a.textContent =
        Math.max(0, Math.round(+E.mins || 0) - Math.round(+E.split.f || 0) - Math.round(+E.split.r || 0)) + ' min';
  }
  if (id === 'edMins' && E && E.split && $('edA'))
    $('edA').textContent =
      Math.max(0, Math.round(+v || 0) - Math.round(+E.split.f || 0) - Math.round(+E.split.r || 0)) + ' min';
  if (id === 'howNote' && X) {
    X.howNote = v;
    saveDraft();
  } else if (id === 'xnText') {
    const T = noteTarget();
    if (T && T.xn && T.xn[U.sd.k]) {
      T.xn[U.sd.k].t = v;
      if (T === X) saveDraft();
    }
  } else if (id === 'tnText') {
    const tk = TAKES.find((x) => x.id === U.sd.k);
    if (tk && tk.note) tk.note.t = v;
  } else if (id === 'edHowNote' && E) E.howNote = v;
  else if (id === 'edDate' && E) E.dateStr = v;
  else if (id === 'edMins' && E) E.mins = v;
});
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  if (U.sheet) closeSheet();
  else if (U.clock) {
    U.clock = false;
    rerender();
  }
});
