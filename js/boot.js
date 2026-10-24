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
LAUNCH.start(); // before the first draw, so the floating window waits for the launch ripple
render();
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost'))
  navigator.serviceWorker.register('sw.js').catch(() => {});
/* launch screen: stays up until recordings are loaded (at least 0.6 s, at most about 2.5 s), then goes.
   With motion on, the launch ripple plays meanwhile and the screen goes once it has (js/launch.js). */
setTimeout(LAUNCH.finish, LAUNCH.capWait());
checkPersist(true).then(() => {
  if (SET.shown()) rerender();
});
Promise.all([refreshTakes(), refreshUndo(), COACH.load(), TRACK.load()])
  .then(() => TAKE.load()) // 3.20: takes' waveforms (and both-ears copies) on this device
  .then(rerender)
  .catch(() => {})
  .then(() => new Promise((r) => setTimeout(r, LAUNCH.minWait())))
  .then(LAUNCH.finish);
