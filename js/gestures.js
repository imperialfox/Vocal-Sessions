/* Vocal Sessions · gestures.js
   Pull to refresh, update checks, rotating and resizing, keyboard shortcuts, dragging sheets, scrolling.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Pull to refresh (Today and History) =====
   Pull down at the top: the page follows your finger with resistance and the spinner's spokes appear.
   Past the threshold, let go: it holds, re-reads your data and checks GitHub for a newer version
   (loading it if there is one), then eases back. */
const PTR = { y: null, x: 0, on: false, d: 0, busy: false, lock: null },
  PT_TRIG = 56,
  PT_HOLD = 56;
(() => {
  const sp = $('spin');
  for (let i = 0; i < 8; i++) {
    const e = document.createElement('i');
    e.style.transform = 'rotate(' + i * 45 + 'deg)';
    sp.appendChild(e);
  }
})();
function ptrOK() {
  return (
    !U.view && !U.sheet && !U.clock && (U.tab === 'today' || U.tab === 'history') && window.scrollY <= 0 && !PTR.busy
  );
}
function ptrPaint(d, armed) {
  const a = $('app');
  a.style.transform = d ? 'translateY(' + d + 'px)' : '';
  const sp = $('spin');
  sp.style.opacity = d > 8 ? 1 : 0;
  const p = Math.min(1, d / PT_TRIG);
  [...sp.children].forEach((s, i) => {
    s.style.opacity = PTR.busy ? 1 - i * 0.11 : p * 8 > i ? (armed ? 1 - i * 0.09 : 0.75) : 0;
  });
}
document.addEventListener(
  'touchstart',
  (e) => {
    PTR.y = null;
    if (e.touches.length !== 1 || !ptrOK()) return;
    for (let n = e.target; n && n !== document.body; n = n.parentElement) if (n.scrollTop > 0) return;
    PTR.y = e.touches[0].clientY;
    PTR.x = e.touches[0].clientX;
    PTR.on = false;
    PTR.lock = null;
    PTR.d = 0;
    $('app').classList.remove('ptr-snap');
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (PTR.y === null || e.touches.length !== 1) return;
    const t = e.touches[0],
      dy = t.clientY - PTR.y,
      dx = t.clientX - PTR.x;
    if (PTR.lock === null) {
      if (dy <= 0 || Math.abs(dx) > Math.abs(dy)) {
        if (Math.abs(dx) > 6 || dy < -6) PTR.lock = 'no';
        return;
      }
      if (dy > 6) PTR.lock = 'pull';
    }
    if (PTR.lock === 'no') return;
    if (window.scrollY > 0) {
      PTR.y = null;
      return;
    }
    if (e.cancelable) e.preventDefault();
    if (PTR.lock !== 'pull') return;
    PTR.on = true;
    PTR.d = Math.max(0, 170 * (1 - 1 / (Math.max(0, dy) / 360 + 1)));
    ptrPaint(PTR.d, PTR.d >= PT_TRIG);
  },
  { passive: false }
);
function ptrEnd() {
  if (PTR.y === null) return;
  PTR.y = null;
  if (!PTR.on) return;
  PTR.on = false;
  const a = $('app');
  a.classList.add('ptr-snap');
  if (PTR.d < PT_TRIG) {
    ptrPaint(0);
    return;
  }
  PTR.busy = true;
  $('ptr').classList.add('go');
  ptrPaint(PT_HOLD, true);
  refreshApp().then((r) => {
    if (r === 'reload') return;
    $('ptr').classList.remove('go');
    PTR.busy = false;
    ptrPaint(0);
    setTimeout(() => a.classList.remove('ptr-snap'), 450);
  });
}
document.addEventListener('touchend', ptrEnd);
document.addEventListener('touchcancel', ptrEnd);
const cmpVer = (a, b) => {
  const x = a.split('.').map(Number),
    y = b.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    const d = (x[i] || 0) - (y[i] || 0);
    if (d) return d;
  }
  return 0;
};
async function refreshApp() {
  const t0 = Date.now();
  let newer = null;
  D = load();
  migrate();
  X = loadDraft();
  normX();
  await refreshTakes();
  try {
    const r = await fetch(location.href.split('#')[0], { cache: 'reload' });
    const m = (await r.text()).match(/APP_VERSION='([\d.]+)'/);
    if (m && cmpVer(m[1], APP_VERSION) > 0) newer = m[1];
  } catch (e) {}
  await new Promise((r) => setTimeout(r, Math.max(0, 700 - (Date.now() - t0))));
  if (newer) {
    toast('Updating to ' + newer + '…');
    setTimeout(() => location.reload(), 800);
    return 'reload';
  }
  render(true);
  return 'ok';
}
/* layout changes (rotating, resizing a window) */
Object.values(MQ).forEach((m) => {
  const f = () => {
    layout();
    if (split() && U.view === 'ex') {
      U.tab = 'exercises';
      U.view = null;
    }
    tabMin = false;
    render(true);
  };
  if (m.addEventListener) m.addEventListener('change', f);
  else if (m.addListener) m.addListener(f);
});
/* keyboard: Cmd/Ctrl + 1–4 switch sections */
document.addEventListener('keydown', (e) => {
  if (!(e.metaKey || e.ctrlKey) || U.sheet || !/^[1-4]$/.test(e.key)) return;
  e.preventDefault();
  const t = TABS()[+e.key - 1][0];
  U.clock = false;
  go(() => {
    U.tab = t;
    U.view = null;
  });
});
/* drag a sheet down by its header to dismiss it, like iOS */
let SD = null;
document.addEventListener(
  'touchstart',
  (e) => {
    const h = e.target.closest('.shead');
    SD = null;
    if (!h || e.touches.length !== 1) return;
    SD = { sh: h.closest('.sheet'), y: e.touches[0].clientY, dy: 0 };
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (!SD || e.touches.length !== 1) return;
    const dy = e.touches[0].clientY - SD.y;
    SD.dy = Math.max(0, dy);
    if (e.cancelable) e.preventDefault();
    SD.sh.classList.add('drag');
    SD.sh.style.transform = SD.dy ? 'translateY(' + SD.dy + 'px)' : '';
  },
  { passive: false }
);
function sheetDragEnd() {
  if (!SD) return;
  const { sh, dy } = SD;
  SD = null;
  sh.classList.remove('drag');
  if (!dy) return;
  sh.classList.add('back');
  if (dy > 90) {
    sh.style.transform = 'translateY(110%)';
    setTimeout(() => {
      if (U.sheet) closeSheet();
    }, 200);
  } else {
    sh.style.transform = '';
    setTimeout(() => sh.classList.remove('back'), 340);
  }
}
document.addEventListener('touchend', sheetDragEnd);
document.addEventListener('touchcancel', sheetDragEnd);
// live session clock
setInterval(() => {
  if (!X || !isFlow(U.view)) return;
  const t = $('timer');
  if (t) t.textContent = pillText();
  const bc = $('bigClock');
  if (bc) bc.textContent = clk(elapsedSec());
  const cs = $('curSplit');
  if (cs) cs.textContent = clk(elapsedSec() - (+cs.dataset.base || 0));
}, 1000);
let lastY = 0,
  tabMin = false;
window.addEventListener(
  'scroll',
  () => {
    closeSwipes();
    const y = window.scrollY;
    const sc = y > 36;
    $('bar').classList.toggle('scrolled', sc);
    document.body.classList.toggle('scrolled', sc);
    const tb = $('dock').querySelector('.tabbar');
    if (tb && !U.sheet && !document.body.classList.contains('land')) {
      if (y > lastY + 6 && y > 120) tabMin = true;
      else if (y < lastY - 6 || y < 60) tabMin = false;
      tb.classList.toggle('min', tabMin);
    }
    lastY = y;
  },
  { passive: true }
);
// iOS pauses the mic when you leave the app, so stop and save the take, then say so on return
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    if (rec) {
      bgSaved = true;
      stopRec();
    }
  } else {
    if (!U.sheet && !rec) render(true);
    if (bgSaved) {
      bgSaved = false;
      setTimeout(() => toast('Your take was saved when you left the app'), 500);
    }
  }
});
