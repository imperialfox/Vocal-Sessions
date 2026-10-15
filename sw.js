/* Vocal Sessions offline support.

   The app is index.html plus its files in css/ and js/, each with ?v=<version> in its address.
   - The page is fetched fresh when you're online, so updates arrive. A new version is only saved for offline
     use once the page AND every file it lists have downloaded, so the saved copy is never half old, half new.
   - Versioned files never change, so they're served from the saved copy when there is one.
   - Other files (CHANGELOG.md) are fetched fresh, falling back to the saved copy.
   - Images rarely change, so they come from the saved copy.
   With no signal, or a network too slow to answer within 4 seconds, the saved copy is used. */
const CACHE = 'vocal-sessions-v3';
const EXTRA = ['./CHANGELOG.md', './icon.png?v=3', './splash/logo.png'];
const NET_TIMEOUT = 4000;
const IMAGE = /\.(png|jpe?g|webp|gif|svg|ico)$/i;
const APP_FILE = /\/(js|css)\/[^/]+$/;

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    try { const res = await fetch('./', { cache: 'reload' }); if (res.ok) await savePage(res); } catch (err) {}
    await Promise.all(EXTRA.map(u => cache.add(u).catch(() => {})));
  })());
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
  if (isPage(req, url)) e.respondWith(page(e));
  else if ((APP_FILE.test(url.pathname) && url.search) || IMAGE.test(url.pathname)) e.respondWith(cacheFirst(req));
  else e.respondWith(networkFirst(req, url));
});

const isPage = (req, url) => req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('.html');
const withTimeout = p => Promise.race([p, new Promise((_, reject) => setTimeout(() => reject(new Error('slow network')), NET_TIMEOUT))]);

async function page(e) {
  try {
    const res = await withTimeout(fetch(e.request));
    if (res && res.ok) e.waitUntil(savePage(res.clone()).catch(() => {}));
    return res;
  } catch (err) {
    const cache = await caches.open(CACHE);
    return (await cache.match('./')) || (await cache.match('./index.html')) || Response.error();
  }
}

// Save a version of the app for offline use, but only once every file it needs has downloaded.
async function savePage(res) {
  const html = await res.text();
  const files = [...html.matchAll(/(?:src|href)="((?:js|css)\/[^"?]+\?v=[^"]+)"/g)].map(m => m[1]);
  const cache = await caches.open(CACHE);
  const fresh = await Promise.all(files.map(async f => {
    if (await cache.match(f)) return null;
    const r = await fetch(f, { cache: 'reload' });
    if (!r.ok) throw new Error('missing ' + f);
    // read it now: an unread response keeps its connection busy, and browsers only allow 6 per site
    return [f, new Response(await r.blob(), { headers: r.headers })];
  }));
  await Promise.all(fresh.filter(Boolean).map(([f, r]) => cache.put(f, r)));
  await cache.put('./', new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } }));
  // remove files that no saved version uses any more
  const keep = new Set(files.map(f => new URL(f, self.registration.scope).href));
  for (const k of await cache.keys()) {
    const u = new URL(k.url);
    if (APP_FILE.test(u.pathname) && u.search && !keep.has(u.href)) await cache.delete(k);
  }
}

async function networkFirst(req, url) {
  const cache = await caches.open(CACHE);
  try {
    const res = await withTimeout(fetch(req));
    if (res && res.ok) cache.put(url.pathname, res.clone());
    return res;
  } catch (err) {
    return (await cache.match(url.pathname)) || (await cache.match(req, { ignoreSearch: true })) || Response.error();
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
