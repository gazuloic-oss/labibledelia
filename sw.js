// Service Worker — La Bible de l'IA v2
const CACHE_NAME = 'bible-ia-v2';
const STATIC_ASSETS = [
  '/styles.css',
  '/favicon.svg',
  '/manifest.json',
  '/tools-fr.js',
  '/tools-en.js',
  '/app-fr.js',
  '/app-en.js',
  '/fr/',
  '/en/',
  '/og-image-fr.png',
  '/og-image-en.png'
];

// Offline fallback page (simple)
const OFFLINE_HTML = `<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hors ligne — La Bible de l'IA</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,sans-serif;background:#0e0e1a;color:#e8e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;padding:2rem}.container{max-width:400px}h1{font-family:Georgia,serif;color:#c9a84c;font-size:2rem;margin-bottom:1rem}p{color:#9898b0;line-height:1.6;margin-bottom:1.5rem}a{color:#c9a84c;text-decoration:none;padding:.6rem 1.5rem;border:1px solid #c9a84c;border-radius:8px;display:inline-block}a:hover{background:rgba(201,168,76,.1)}</style></head><body><div class="container"><div style="font-size:3rem;margin-bottom:1rem">📖</div><h1>Vous etes hors ligne</h1><p>La Bible de l'IA necessite une connexion internet pour fonctionner. Verifiez votre connexion et reessayez.</p><a href="/" onclick="location.reload();return false">Reessayer</a></div></body></html>`;

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      cache.addAll(STATIC_ASSETS).catch(() => {
        // If some assets fail (e.g. og-images), continue anyway
        return cache.addAll(STATIC_ASSETS.filter(a => !a.includes('og-image')));
      })
    )
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

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Only handle same-origin requests
  if (url.origin !== self.location.origin) return;

  if (event.request.destination === 'document') {
    // HTML: Network-first with offline fallback
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Cache successful HTML responses for next offline visit
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() =>
          caches.match(event.request).then(cached =>
            cached || new Response(OFFLINE_HTML, {
              headers: { 'Content-Type': 'text/html; charset=utf-8' }
            })
          )
        )
    );
  } else if (url.pathname.endsWith('.js') || url.pathname.endsWith('.css') || url.pathname === '/favicon.svg' || url.pathname === '/manifest.json') {
    // JS/CSS/Static: Stale-while-revalidate
    event.respondWith(
      caches.match(event.request).then(cached => {
        const fetchPromise = fetch(event.request).then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    );
  } else if (url.pathname.endsWith('.png') || url.pathname.endsWith('.svg') || url.pathname.endsWith('.ico')) {
    // Images: Cache-first
    event.respondWith(
      caches.match(event.request).then(cached =>
        cached || fetch(event.request).then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        })
      )
    );
  } else {
    // Everything else: Network-only
    event.respondWith(fetch(event.request));
  }
});
