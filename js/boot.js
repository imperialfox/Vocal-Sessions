/* Vocal Sessions · boot.js
   Starts the app. Loaded last, so everything above exists before anything runs.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* Q11: every step is guarded, so the launch screen always goes and a problem is shown rather than a frozen icon.
   If reading or upgrading the data goes wrong, saving is switched off for this launch (lockSaves), so what's stored is
   left exactly as it was. */
const BOOT_ERRORS = []; // which steps went wrong this launch (the tests read it)
function bootStep(what, fn) {
  try {
    fn();
    return true;
  } catch (e) {
    BOOT_ERRORS.push(what + ': ' + ((e && e.message) || e));
    try {
      console.warn('Vocal Sessions: ' + what + ' went wrong', e);
    } catch (x) {}
    return false;
  }
}
// the launch screen goes, whatever happened (its fade is skipped if finishing it goes wrong)
function bootFinish() {
  if (!bootStep('launch screen', LAUNCH.finish)) {
    const sp = document.getElementById('splash');
    if (sp) sp.remove();
  }
}
// what's shown when the first screen couldn't be drawn
function bootFailed() {
  const app = document.getElementById('app');
  if (app && !app.children.length)
    app.innerHTML =
      '<div style="padding:24px 0"><h1>Vocal Sessions</h1><p class="note">Something went wrong opening the app. Nothing you’ve saved has been deleted.</p>' +
      '<p class="note">Close the app and open it again. If this keeps happening, tap below to try again.</p>' +
      '<button class="cta" id="bootRetry" style="margin-top:14px">Try again</button></div>';
  const b = document.getElementById('bootRetry');
  if (b) b.addEventListener('click', () => location.reload());
}

// Start the app: read saved data, upgrade it if needed, then draw the first screen.
if (
  !bootStep('saved data', () => {
    D = load();
    migrate();
  })
) {
  lockSaves('boot'); // leave the stored data alone; this launch starts empty
  bootStep('empty data', () => {
    D = { v2: true };
    migrate();
  });
}
bootStep('saving', save);
let bootSafe = Promise.resolve();
bootStep('safety copies', () => (bootSafe = tidyPreUpgrade().catch(() => {}))); // Q11: kept in IndexedDB
bootStep('draft', () => {
  X = loadDraft();
  normX();
});
bootStep('layout', layout);
bootStep('launch', LAUNCH.start); // before the first draw, so the floating window waits for the launch ripple
const BOOT_DREW = bootStep('first draw', render);
if (!BOOT_DREW) bootFailed();
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost'))
  navigator.serviceWorker.register('sw.js').catch(() => {});
/* launch screen: stays up until recordings are loaded (at least 0.6 s, at most about 2.5 s), then goes.
   With motion on, the launch ripple plays meanwhile and the screen goes once it has (js/launch.js). */
let bootCap = 2500;
bootStep('launch timing', () => (bootCap = LAUNCH.capWait()));
setTimeout(bootFinish, bootCap);
// and if even that is stuck, the launch screen is simply taken away
setTimeout(() => {
  const sp = document.getElementById('splash');
  if (sp && !sp.dataset.going) sp.remove();
}, bootCap + 4000);
checkPersist(true)
  .then(() => {
    if (SET.shown()) rerender();
  })
  .catch(() => {});
Promise.all([refreshTakes(), refreshUndo(), COACH.load(), TRACK.load(), bootSafe])
  .then(() => TAKE.load()) // 3.20: takes' waveforms (and both-ears copies) on this device
  .then(() => BOOT_DREW && rerender())
  .catch(() => {})
  .then(() => new Promise((r) => setTimeout(r, LAUNCH.minWait())))
  .catch(() => {})
  .then(bootFinish);
if (BOOT_ERRORS.length)
  afterLaunch(() =>
    toast(
      SAVE_LOCK === 'boot'
        ? 'Something went wrong opening your data. It’s been left as it was, and changes won’t be saved this time.'
        : 'Something went wrong starting the app.',
      SAVE_LOCK === 'boot' ? 9000 : 6000,
      'long'
    )
  );
