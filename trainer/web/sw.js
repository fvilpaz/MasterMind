// Service worker de MasterMind: solo guarda la interfaz (HTML, CSS, JS, iconos).
// Todo lo demás (/chat, /profile, /save-session...) va siempre directo al servidor.
// __VERSION__ lo rellena app.py con una huella del contenido de la interfaz: cualquier cambio en HTML, CSS o JS
// cambia este archivo, el navegador instala el service worker nuevo y la página se entera (SW_UPDATED).
const CACHE = 'mastermind-__VERSION__';
const SHELL = [
  '/styles.css',
  '/app.js',
  '/code-editor.js',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  // Borra cachés de versiones anteriores. Si había alguna, esto es una ACTUALIZACIÓN (no la primera instalación)
  // y se avisa a las páginas abiertas para que se recarguen con lo nuevo, como en nplayer.
  event.waitUntil(
    caches.keys()
      .then(keys => {
        const viejas = keys.filter(k => k !== CACHE);
        return Promise.all(viejas.map(k => caches.delete(k))).then(() => viejas.length > 0);
      })
      .then(actualizado => self.clients.claim().then(() => actualizado))
      .then(actualizado => {
        if (!actualizado) return;
        return self.clients.matchAll({ type: 'window' })
          .then(clients => clients.forEach(c => c.postMessage({ type: 'SW_UPDATED' })));
      })
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== location.origin) return;
  if (!SHELL.includes(url.pathname) && !url.pathname.startsWith('/icons/')) return;

  // Red primero (siempre lo último); la caché solo si no hay conexión. cache:'no-cache' obliga a preguntar al
  // servidor aunque el navegador tenga una copia guardada (lo mismo que resolvió el problema en ME·VENTS).
  event.respondWith(
    fetch(event.request, { cache: 'no-cache' })
      .then(resp => {
        const copy = resp.clone();
        caches.open(CACHE).then(cache => cache.put(event.request, copy));
        return resp;
      })
      .catch(() => caches.match(event.request))
  );
});
