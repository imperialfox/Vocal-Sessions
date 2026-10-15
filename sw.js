/* Vocal Sessions offline support.
   Everything except images is fetched fresh when you're online (so updates and the changelog arrive),
   and the saved copy is used when there's no signal or the network is too slow.
   Images rarely change, so they're served from the saved copy. */
const CACHE = 'vocal-sessions-v2';
const SHELL = ['./', './index.html', './CHANGELOG.md', './icon.png?v=3', './splash/logo.png'];
const NET_TIMEOUT = 4000; // ms to wait for the network before using the saved copy
const IMAGE = /\.(png|jpe?g|webp|gif|svg|ico)$/i;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => {})))));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  e.respondWith(IMAGE.test(url.pathname) ? cacheFirst(req) : networkFirst(req, url));
});

// The app page is saved under './' whatever address opened it; other files under their own path.
const isPage = (req, url) => req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('.html');

async function networkFirst(req, url) {
  const cache = await caches.open(CACHE);
  const key = isPage(req, url) ? './' : url.pathname;
  try {
    const res = await Promise.race([
      fetch(req),
      new Promise((_, reject) => setTimeout(() => reject(new Error('slow network')), NET_TIMEOUT))
    ]);
    if (res && res.ok) { cache.put(key, res.clone()); }
    return res;
  } catch (err) {
    const saved = isPage(req, url)
      ? (await cache.match('./')) || (await cache.match('./index.html'))
      : (await cache.match(key)) || (await cache.match(req, { ignoreSearch: true }));
    return saved || Response.error();
  }
}

async function cacheFirst(req) {
  const hit = await caches.match(req);
  if (hit) return hit;
  try {
    const res = await fetch(req);
    if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  } catch (err) {
    return Response.error();
  }
}
