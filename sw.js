const CACHE_NAME    = 'lightship-v1';
const ARCHIVE_HOST  = 'creationlightship-archive.com';
const PROXY_HOST    = 'corsproxy.io';
const STATIC_ASSETS = [
  './index.html',
  './app.js',
  './manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network-first for archive/proxy requests (identified by hostname); cache-first for static assets
function isRemoteRequest(request) {
  try {
    const { hostname } = new URL(request.url);
    return hostname === ARCHIVE_HOST || hostname === PROXY_HOST;
  } catch {
    return false;
  }
}

self.addEventListener('fetch', event => {
  const { request } = event;
  if (isRemoteRequest(request)) {
    event.respondWith(fetch(request).catch(() => caches.match(request)));
  } else {
    event.respondWith(
      caches.match(request).then(cached => cached || fetch(request))
    );
  }
});
