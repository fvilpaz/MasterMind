// Service worker de MasterMind: solo guarda la interfaz (HTML, CSS, JS, iconos).
// Todo lo demás (/chat, /profile, /save-session...) va siempre directo al servidor.
const CACHE = 'mastermind-v3';
const SHELL = [
  '/styles.css',
  '/app.js',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  // Borra cachés de versiones anteriores al cambiar CACHE
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== location.origin) return;
  if (!SHELL.includes(url.pathname) && !url.pathname.startsWith('/icons/')) return;

  // Red primero (siempre lo último); la caché solo si no hay conexión
  event.respondWith(
    fetch(event.request)
      .then(resp => {
        const copy = resp.clone();
        caches.open(CACHE).then(cache => cache.put(event.request, copy));
        return resp;
      })
      .catch(() => caches.match(event.request))
  );
});
