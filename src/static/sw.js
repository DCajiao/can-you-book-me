const CACHE_VERSION = 'canyoubookme-v2';
const CDN_CACHE = 'canyoubookme-cdn-v1';

// CDN assets are versioned URLs — safe to cache forever
const CDN_ASSETS = [
  'https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css',
  'https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js',
];

self.addEventListener('install', e => {
  self.skipWaiting();
  // Pre-cache only CDN assets on install
  e.waitUntil(
    caches.open(CDN_CACHE).then(c => c.addAll(CDN_ASSETS).catch(() => {}))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(k => k !== CACHE_VERSION && k !== CDN_CACHE)
          .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // API / admin: always network, never cache
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/admin/')) {
    e.respondWith(fetch(e.request));
    return;
  }

  // CDN assets: cache-first (URLs are version-pinned, safe forever)
  if (url.origin === 'https://cdn.jsdelivr.net') {
    e.respondWith(
      caches.match(e.request).then(cached => cached || fetch(e.request))
    );
    return;
  }

  // Everything else (HTML, CSS, JS, icons): network-first
  // → always serves fresh content; falls back to cache only if offline
  e.respondWith(
    fetch(e.request)
      .then(res => {
        if (res && res.status === 200 && e.request.method === 'GET') {
          const clone = res.clone();
          caches.open(CACHE_VERSION).then(c => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
