/* Vocal Sessions · boot.js
   Starts the app. Loaded last, so everything above exists before anything runs.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

// Start the app: read saved data, upgrade it if needed, then draw the first screen.
D = load();
migrate();
save();
tidyPreUpgrade();
X = loadDraft();
normX();
layout();
render();
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost'))
  navigator.serviceWorker.register('sw.js').catch(() => {});
/* launch screen: stay up until recordings are loaded (at least 0.6 s, at most 2.5 s), then fade */
function hideSplash() {
  const sp = $('splash');
  if (!sp || sp.classList.contains('out')) return;
  sp.classList.add('out');
  setTimeout(() => sp.remove(), 500);
}
const splashMin = new Promise((r) => setTimeout(r, Math.max(0, 600 - performance.now())));
setTimeout(hideSplash, 2500);
checkPersist(true).then(() => {
  if (U.tab === 'settings' && !U.view) rerender();
});
Promise.all([refreshTakes(), refreshUndo()])
  .then(rerender)
  .catch(() => {})
  .then(() => splashMin)
  .then(hideSplash);
