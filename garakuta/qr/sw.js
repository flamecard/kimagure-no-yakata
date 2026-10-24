'use strict';
const VERSION = '1.0.0';
const CACHE_PREFIX = 'kimagure-qr-pwa-';
const CACHE = CACHE_PREFIX + VERSION;
const BASE = new URL('./', self.location.href);
const ASSETS = ['index.html','app.css','app.js','qrcodegen.js','manifest.webmanifest','icon.svg','icon-180.png','icon-192.png','icon-512.png','LICENSE.txt'];
const URLS = ASSETS.map(path => new URL(path, BASE).href);

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // Complete installation only when every required file is stored.
    await cache.addAll(URLS.map(url => new Request(url, {cache:'reload'})));
    // An existing app keeps its active version until its user accepts the update.
    if (!self.registration.active) await self.skipWaiting();
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith(CACHE_PREFIX) && name !== CACHE) await caches.delete(name);
    }
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== BASE.origin || !url.pathname.startsWith(BASE.pathname)) return;
  let key = url.href;
  if (event.request.mode === 'navigate' && [BASE.pathname, BASE.pathname+'index.html'].includes(url.pathname)) {
    key = new URL('index.html', BASE).href;
  } else {
    url.search = ''; url.hash = ''; key = url.href;
    if (!URLS.includes(key)) return;
  }
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const stored = await cache.match(key);
    if (stored) return stored;
    const response = await fetch(key);
    if (response.ok && response.type === 'basic') await cache.put(key, response.clone());
    return response;
  })());
});
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') { self.skipWaiting(); return; }
  if (event.data?.type !== 'CHECK_OFFLINE' || !event.ports[0]) return;
  event.waitUntil((async () => {
    try {
      const cache = await caches.open(CACHE);
      const present = await Promise.all(URLS.map(url => cache.match(url)));
      event.ports[0].postMessage({ready:present.every(Boolean),version:VERSION});
    } catch (_) { event.ports[0].postMessage({ready:false,version:VERSION}); }
  })());
});
