// สลากแล็บ service worker — ทำให้ติดตั้งเป็นแอปได้ และเปิดได้ตอนเน็ตหลุด
const CACHE = 'slk-v1';
const SHELL = ['./', 'offline.html', 'manifest.webmanifest', 'icon-192.png', 'icon.svg', 'data.json'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => null)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('slk-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // ตัวแอป (script.google.com) ให้เบราว์เซอร์จัดการเอง
  const fresh = fetch(req).then(res => {
    if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  });
  if (req.mode === 'navigate' || url.pathname.endsWith('data.json')) {
    // หน้าเว็บ/ผลล่าสุด: เอาของใหม่ก่อน ถ้าเน็ตหลุดใช้ของที่เก็บไว้
    e.respondWith(fresh.catch(() => caches.match(req).then(r => r || (req.mode === 'navigate' ? caches.match('offline.html') : Response.error()))));
  } else {
    e.respondWith(caches.match(req).then(r => r || fresh));
  }
});
